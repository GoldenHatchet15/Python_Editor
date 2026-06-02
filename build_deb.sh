#!/bin/bash
# Build a .deb package for Holberton Jr. Code Studio
# Requires: dpkg-deb
# Usage: ./build_deb.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION="1.0.0"
ARCH=$(dpkg --print-architecture)
PKG_NAME="holberton-jr"
BUILD_DIR="$SCRIPT_DIR/build/deb/${PKG_NAME}_${VERSION}_${ARCH}"

echo "=== Building Holberton Jr. Code Studio .deb package ==="

# Clean and create directory structure
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/${PKG_NAME}"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"

# Copy source files
echo "[1/4] Copying source files..."
cp -r "$SCRIPT_DIR/holberton_jr" "$BUILD_DIR/usr/share/${PKG_NAME}/"

# Create wrapper script
cat > "$BUILD_DIR/usr/bin/holberton-jr" << 'WRAPPER'
#!/bin/bash
exec python3 -m holberton_jr.main "$@"
WRAPPER
chmod +x "$BUILD_DIR/usr/bin/holberton-jr"

# Create desktop entry
cat > "$BUILD_DIR/usr/share/applications/holberton-jr.desktop" << DESKTOP
[Desktop Entry]
Name=Holberton Jr. Code Studio
Comment=A beginner-friendly Python editor for kids ages 10-14
Exec=holberton-jr %F
Icon=holberton-jr
Type=Application
Categories=Development;IDE;Education;
Terminal=false
MimeType=text/x-python;
DESKTOP

# Create control file
cat > "$BUILD_DIR/DEBIAN/control" << CONTROL
Package: holberton-jr
Version: ${VERSION}
Section: education
Priority: optional
Architecture: ${ARCH}
Depends: python3 (>= 3.8), python3-pyqt6, python3-pyqt6.qscintilla
Maintainer: Holberton School <info@holbertonschool.com>
Description: Holberton Jr. Code Studio
 A beginner-friendly Python editor for kids ages 10-14,
 designed for Holberton School summer camps in Puerto Rico.
 Features interactive input() support, turtle graphics,
 friendly error messages, and starter templates.
CONTROL

# Create postinst script
cat > "$BUILD_DIR/DEBIAN/postinst" << POSTINST
#!/bin/bash
# Ensure dependencies are available
pip3 install PyQt6 PyQt6-QScintilla 2>/dev/null || pip install PyQt6 PyQt6-QScintilla 2>/dev/null || true
POSTINST
chmod +x "$BUILD_DIR/DEBIAN/postinst"

# Generate icon
echo "[2/4] Generating icon..."
python3 << 'PYICON'
try:
    from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
    from PyQt6.QtCore import Qt, QRect
    import sys
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
    pixmap.save(sys.argv[1])
except Exception as e:
    print(f"Icon generation failed: {e}")
PYICON "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/holberton-jr.png" 2>/dev/null || true

echo "[3/4] Building package..."
dpkg-deb --build "$BUILD_DIR"

echo "[4/4] Done!"
echo ""
echo "=== Build complete! ==="
echo "Package: $BUILD_DIR.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i $BUILD_DIR.deb"
echo ""
echo "To run after installing:"
echo "  holberton-jr"
echo ""
echo "Or run directly without installing:"
echo "  python3 -m holberton_jr.main"