#!/usr/bin/env python3
"""Holberton Jr. Code Studio — entry point."""

import sys
import os


def main():
    # Ensure PyQt6 platform plugin can be found
    # This helps with AppImage and some Linux setups
    if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
        # Try to find the platform plugin in common locations
        for path in [
            os.path.join(sys.prefix, "PyQt6", "Qt6", "plugins", "platforms"),
            os.path.join(os.path.dirname(sys.executable), "..", "lib", "python3",
                         f"dist-packages/PyQt6/Qt6/plugins/platforms"),
        ]:
            if os.path.isdir(path):
                os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = path
                break

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from holberton_jr.main_window import MainWindow

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Holberton Jr. Code Studio")
    app.setOrganizationName("Holberton School")

    # Parse command-line args for workspace dir
    workspace = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg in ("--workspace", "-w") and i + 1 < len(sys.argv[1:]):
            workspace = sys.argv[i + 2]
        elif not arg.startswith("-"):
            workspace = arg

    window = MainWindow(workspace_dir=workspace)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()