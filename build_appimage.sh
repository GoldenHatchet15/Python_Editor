#!/bin/bash
# Build Holberton Jr. Code Studio as an AppImage
# Requires: python3, pip, wget
# Usage: ./build_appimage.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build/appimage"
APP_NAME="HolbertonJr"
APP_DIR="$BUILD_DIR/${APP_NAME}.AppDir"

echo "=== Building Holberton Jr. Code Studio AppImage ==="

# Install dependencies
echo "[1/5] Installing Python dependencies..."
pip3 install --user -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Install PyInstaller
pip3 install --user pyinstaller 2>/dev/null || pip3 install pyinstaller

# Create build directory
echo "[2/5] Creating build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Build with PyInstaller
echo "[3/5] Building with PyInstaller..."
cd "$SCRIPT_DIR"

pyinstaller --noconfirm \
    --name "holberton-jr" \
    --onefile \
    --windowed \
    --add-data "holberton_jr:holberton_jr" \
    --hidden-import PyQt6.Qsci \
    --hidden-import PyQt6.QtWidgets \
    --hidden-import PyQt6.QtCore \
    --hidden-import PyQt6.QtGui \
    --distpath "$BUILD_DIR/dist" \
    --workpath "$BUILD_DIR/build" \
    --specpath "$BUILD_DIR" \
    holberton_jr/main.py

echo "[4/5] Building AppImage..."

# Download AppImageTool if not present
APPIMAGETOOL="$BUILD_DIR/appimagetool"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    ARCH=$(uname -m)
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage" -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

# Create AppDir structure
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# Copy the binary
cp "$BUILD_DIR/dist/holberton-jr" "$APP_DIR/usr/bin/"

# Create desktop entry
cat > "$APP_DIR/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Name=Holberton Jr. Code Studio
Comment=A beginner-friendly Python editor for kids
Exec=holberton-jr
Icon=holberton-jr
Type=Application
Categories=Development;IDE;Education;
Terminal=false
EOF

# Create a simple icon (placeholder)
python3 -c "
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRect
pixmap = QPixmap(256, 256)
pixmap.fill(QColor(0, 0, 0, 0))
p = QPainter(pixmap)
p.setRenderHint(QPainter.RenderHint.Antialiasing)
p.setBrush(QColor('#C7254E'))
p.setPen(Qt.PenStyle.NoPen)
p.drawRoundedRect(10, 10, 236, 236, 30, 30)
p.setPen(QColor('white'))
p.setFont(QFont('Sans', 80, QFont.Weight.Bold))
p.drawText(QRect(10, 10, 236, 236), Qt.AlignmentFlag.AlignCenter, 'HJ')
p.end()
pixmap.save('$APP_DIR/holberton-jr.png')
" 2>/dev/null || {
    # Fallback: create icon with Python Imaging if PyQt fails
    python3 -c "
from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([10, 10, 246, 246], radius=30, fill=(199, 37, 78))
draw.text((80, 80), 'HJ', fill='white', font=ImageFont.load_default())
img.save('$APP_DIR/holberton-jr.png')
" 2>/dev/null || echo "Warning: Could not generate icon"
}

# Copy icon
cp "$APP_DIR/holberton-jr.png" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/holberton-jr.png" 2>/dev/null || true

# Create AppRun
cat > "$APP_DIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")
export PATH="${HERE}/usr/bin:${PATH}"
export PYTHONPATH="${HERE}/usr/share:${PYTHONPATH}"
exec "${HERE}/usr/bin/holberton-jr" "$@"
APPRUN
chmod +x "$APP_DIR/AppRun"

# Build AppImage
echo "[5/5] Packaging AppImage..."
ARCH=$(uname -m)
"$APPIMAGETOOL" "$APP_DIR" "$BUILD_DIR/HolbertonJr-${ARCH}.AppImage" || {
    echo ""
    echo "AppImage build failed. You can still run the app directly:"
    echo "  $BUILD_DIR/dist/holberton-jr"
    echo ""
    echo "Alternatively, build a .deb package with:"
    echo "  ./build_deb.sh"
    exit 0
}

echo ""
echo "=== Build complete! ==="
echo "AppImage: $BUILD_DIR/HolbertonJr-${ARCH}.AppImage"
echo ""
echo "To install:"
echo "  chmod +x $BUILD_DIR/HolbertonJr-${ARCH}.AppImage"
echo "  ./$BUILD_DIR/HolbertonJr-${ARCH}.AppImage"