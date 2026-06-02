#!/bin/bash
# Run Holberton Jr. Code Studio
# Usage: ./run.sh [workspace_dir]
#
# This script automatically creates a virtual environment if needed,
# installs dependencies, and launches the app.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install dependencies if needed
if ! python -c "from PyQt6.Qsci import QsciScintilla" 2>/dev/null; then
    echo "Installing dependencies (this only happens once)..."
    pip install -r requirements.txt
fi

# Run the app
python -m holberton_jr.main "$@"