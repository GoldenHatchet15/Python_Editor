# Holberton Jr. Code Studio

A beginner-friendly Python editor for kids ages 10-14, designed for Holberton School summer camps in Puerto Rico.

## Features

- **Interactive `input()` support** — programs pause and accept typed input, just like a real terminal
- **Turtle graphics** — `import turtle` opens its own window with native tkinter
- **File explorer** — sidebar showing your Python files, with create/rename/delete
- **Friendly error messages** — Python tracebacks get kid-readable hints
- **Dark theme** — easy on the eyes, great for turtle art
- **Starter templates** — one-click project starters for each camp day
- **Bilingual UI** — switch between English and Spanish
- **Autosave** — saves every 20 seconds as a safety net
- **Offline-first** — no internet, accounts, or login required

## Quick Start

### Option 1: Run script (recommended — auto-creates venv)

```bash
chmod +x run.sh
./run.sh
```

This automatically creates a `.venv` directory, installs dependencies, and launches the app.

### Option 2: Manual setup with virtual environment

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python -m holberton_jr.main

# With a custom workspace directory
python -m holberton_jr.main --workspace /path/to/workspace
```

### Option 3: System-wide install (if your system allows it)

```bash
pip3 install --break-system-packages PyQt6 PyQt6-QScintilla
python3 -m holberton_jr.main
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| F5 / Ctrl+Enter | Run program |
| Ctrl+S | Save file |
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+Shift+S | Save As |
| Ctrl+W | Close tab |

## Building

### AppImage

```bash
chmod +x build_appimage.sh
./build_appimage.sh
```

### .deb package

```bash
chmod +x build_deb.sh
./build_deb.sh
sudo dpkg -i build/deb/holberton-jr_1.0.0_*.deb
```

## Requirements

- Python 3.8+
- PyQt6
- PyQt6-QScintilla
- Linux (tested on Ubuntu 22.04+, Debian 11+)

## Acceptance Tests

- [x] An `input()` program pauses, accepts typed input, and continues correctly
- [x] A multi-input "Player Profile" program runs fully interactively
- [ ] `import turtle` draws a visible hexagon and color spiral in its own window
- [x] `import random` and `time.sleep()` work
- [x] A `while True:` loop can be stopped with the Stop button
- [x] `try/except` catches a `ValueError` from `int(input())`
- [x] Create, save (Ctrl+S), close, and reopen a file — content persists
- [x] App launches and runs all of the above with no internet connection
- [ ] Builds and runs on a clean Debian/Ubuntu machine following the instructions
- [ ] Cold launch is fast (a second or two)

Note: Turtle graphics and cold-launch tests require a graphical display.