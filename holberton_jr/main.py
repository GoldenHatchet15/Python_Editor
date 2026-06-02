#!/usr/bin/env python3
"""Holberton Jr. Code Studio — entry point."""

import sys
import os


def main():
    # Ensure PyQt6 platform plugin can be found
    # This helps with virtual environments and AppImage setups
    if "QT_QPA_PLATFORM_PLUGIN_PATH" not in os.environ:
        for path in [
            os.path.join(sys.prefix, "PyQt6", "Qt6", "plugins", "platforms"),
            # venv layout
            os.path.join(sys.prefix, "lib", "python3",
                         f"dist-packages/PyQt6/Qt6/plugins/platforms"),
            # site-packages layout (varies by distro)
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
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("--workspace", "-w") and i + 1 < len(args):
            workspace = args[i + 1]
            break
        elif not args[i].startswith("-"):
            workspace = args[i]
            break
        i += 1

    window = MainWindow(workspace_dir=workspace)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()