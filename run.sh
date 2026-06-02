#!/bin/bash
# Run Holberton Jr. Code Studio
# Usage: ./run.sh [workspace_dir]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check dependencies
python3 -c "import PyQt6" 2>/dev/null || {
    echo "PyQt6 not found. Installing dependencies..."
    pip3 install -r requirements.txt
}
python3 -c "from PyQt6.Qsci import QsciScintilla" 2>/dev/null || {
    echo "PyQt6-QScintilla not found. Installing..."
    pip3 install PyQt6-QScintilla
}

# Run the app
exec python3 -m holberton_jr.main "$@"