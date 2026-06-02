"""Main window — assembles editor, console, file explorer, toolbar, menus, and autosave."""

import os
import sys
import tempfile
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QToolBar, QToolButton, QPushButton, QLabel, QTabWidget,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QFileDialog,
    QApplication, QTabBar,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QAction, QKeySequence, QIcon, QPixmap, QPainter, QColor

from .editor_widget import PythonEditor
from .console_widget import ConsoleWidget
from .file_explorer import FileExplorer
from .templates import TEMPLATES, template_names
from .friendly_errors import extract_friendly_hint
from . import theme


# ── Placeholder icon generator ──────────────────────────────────────────────
def _make_icon(color: str, letter: str, size=24):
    """Create a simple colored icon with a letter for buttons."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # transparent
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(2, 2, size - 4, size - 4, 4, 4)
    p.setPen(QColor("white"))
    p.setFont(QFont("Sans", size // 2, QFont.Weight.Bold))
    p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, letter)
    p.end()
    return QIcon(pixmap)


class EditorTab(QWidget):
    """A single editor tab — holds the editor and its file path."""

    def __init__(self, filepath=None, content=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.editor = PythonEditor(self)
        layout.addWidget(self.editor)

        self._filepath = filepath
        self._is_new = filepath is None  # Untitled tab

        if filepath and content is None:
            self.editor.load_file(filepath)
        elif content is not None:
            self.editor.setText(content)
            if filepath:
                self.editor.set_filepath(filepath)

        self.editor.content_changed.connect(self._on_modified)
        self.editor.file_saved.connect(self._on_saved)

    def _on_modified(self):
        """Mark tab as modified."""
        self._is_new = False

    def _on_saved(self):
        """Mark tab as saved."""
        pass

    def filepath(self):
        return self.editor.filepath()

    def is_modified(self):
        return self.editor.is_modified()

    def save(self, path=None):
        return self.editor.save_file(path)

    def set_filepath(self, path):
        self.editor.set_filepath(path)
        self._filepath = path
        self._is_new = False

    def tab_title(self):
        if self._filepath:
            name = os.path.basename(self._filepath)
        else:
            name = "untitled.py"
        if self.is_modified():
            return name + " *"
        return name


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, workspace_dir=None):
        super().__init__()
        self._lang = "en"  # "en" or "es"
        self._autosave_timer = QTimer(self)
        self._autosave_timer.setInterval(20000)  # 20 seconds
        self._autosave_timer.timeout.connect(self._autosave)

        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.expanduser("~"), "HolbertonJr")

        self._workspace = workspace_dir
        os.makedirs(self._workspace, exist_ok=True)

        self._setup_window()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_central()
        self._setup_statusbar()
        self._setup_shortcuts()

        # Start autosave
        self._autosave_timer.start()

        # Open a welcome tab
        self._new_untitled_tab()

        # Show the window
        self.show()

    def _setup_window(self):
        """Configure the main window."""
        self.setWindowTitle("Holberton Jr. Code Studio")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self.setStyleSheet(theme.DARK_STYLESHEET)

    def _setup_menu(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu(theme.label("file", self._lang))
        self._new_action = file_menu.addAction(theme.label("new_file", self._lang))
        self._new_action.setShortcut(QKeySequence("Ctrl+N"))
        self._new_action.triggered.connect(self._new_untitled_tab)

        self._open_action = file_menu.addAction("&Open..." if self._lang == "en" else "&Abrir...")
        self._open_action.setShortcut(QKeySequence("Ctrl+O"))
        self._open_action.triggered.connect(self._open_file)

        file_menu.addSeparator()

        self._save_action = file_menu.addAction(theme.label("save", self._lang))
        self._save_action.setShortcut(QKeySequence("Ctrl+S"))
        self._save_action.triggered.connect(self._save_current)

        self._saveas_action = file_menu.addAction("Save As..." if self._lang == "en" else "Guardar Como...")
        self._saveas_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self._saveas_action.triggered.connect(self._save_current_as)

        file_menu.addSeparator()

        self._close_action = file_menu.addAction("Close Tab" if self._lang == "en" else "Cerrar Pestaña")
        self._close_action.setShortcut(QKeySequence("Ctrl+W"))
        self._close_action.triggered.connect(self._close_current_tab)

        # Edit menu
        edit_menu = menubar.addMenu(theme.label("edit", self._lang))
        undo_action = edit_menu.addAction("Undo" if self._lang == "en" else "Deshacer")
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        redo_action = edit_menu.addAction("Redo" if self._lang == "en" else "Rehacer")
        redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))

        # Templates menu
        self._templates_menu = menubar.addMenu(theme.label("templates", self._lang))
        self._rebuild_templates_menu()

        # Language toggle
        lang_menu = menubar.addMenu(theme.label("language", self._lang))
        en_action = lang_menu.addAction("English")
        es_action = lang_menu.addAction("Español")
        en_action.triggered.connect(lambda: self._set_language("en"))
        es_action.triggered.connect(lambda: self._set_language("es"))

        # Help
        help_menu = menubar.addMenu(theme.label("help", self._lang))
        about_action = help_menu.addAction(theme.label("about", self._lang))
        about_action.triggered.connect(self._show_about)

    def _rebuild_templates_menu(self):
        """Rebuild the templates menu with current language."""
        self._templates_menu.clear()
        for key, name in template_names(self._lang):
            action = self._templates_menu.addAction(name)
            action.triggered.connect(lambda checked, k=key: self._open_template(k))

    def _setup_toolbar(self):
        """Create the main toolbar with Run, Stop, Save, Clear buttons."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # Run button
        self._run_btn = QToolButton()
        self._run_btn.setText(" ▶ Run ")
        self._run_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: #2ECC71;
                color: white;
                border: 2px solid #27AE60;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            QToolButton:hover {{
                background-color: #27AE60;
            }}
            QToolButton:pressed {{
                background-color: #1E8449;
            }}
            QToolButton:disabled {{
                background-color: #555555;
                border-color: #444444;
                color: #888888;
            }}
        """)
        self._run_btn.clicked.connect(self._run_script)
        toolbar.addWidget(self._run_btn)

        # Stop button
        self._stop_btn = QToolButton()
        self._stop_btn.setText(" ■ Stop ")
        self._stop_btn.setEnabled(False)
        self._stop_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: #E74C3C;
                color: white;
                border: 2px solid #C0392B;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            QToolButton:hover {{
                background-color: #C0392B;
            }}
            QToolButton:pressed {{
                background-color: #922B21;
            }}
            QToolButton:disabled {{
                background-color: #555555;
                border-color: #444444;
                color: #888888;
            }}
        """)
        self._stop_btn.clicked.connect(self._stop_script)
        toolbar.addWidget(self._stop_btn)

        toolbar.addSeparator()

        # Save button
        self._save_btn = QToolButton()
        self._save_btn.setText(" 💾 Save ")
        self._save_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: #3498DB;
                color: white;
                border: 2px solid #2980B9;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-width: 90px;
            }}
            QToolButton:hover {{
                background-color: #2980B9;
            }}
            QToolButton:pressed {{
                background-color: #1F618D;
            }}
        """)
        self._save_btn.clicked.connect(self._save_current)
        toolbar.addWidget(self._save_btn)

        # Clear Output button
        self._clear_btn = QToolButton()
        self._clear_btn.setText(" 🗑 Clear ")
        self._clear_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: #2A2A4A;
                color: #EAEAEA;
                border: 1px solid #3A3A5A;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                min-width: 90px;
            }}
            QToolButton:hover {{
                background-color: #3A3A5A;
            }}
        """)
        self._clear_btn.clicked.connect(self._clear_output)
        toolbar.addWidget(self._clear_btn)

        toolbar.addSeparator()

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding,
                             spacer.sizePolicy().verticalPolicy().Preferred)
        toolbar.addWidget(spacer)

        # Status label in toolbar
        self._status_label = QLabel(theme.label("ready", self._lang))
        self._status_label.setStyleSheet("color: #A6ADC8; font-size: 12px; background: transparent;")
        toolbar.addWidget(self._status_label)

    def _setup_central(self):
        """Set up the central widget with file explorer, editor tabs, and console."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # File explorer
        self._file_explorer = FileExplorer(self._workspace)
        self._file_explorer.file_selected.connect(self._open_file_from_explorer)
        self._file_explorer.file_created.connect(self._open_file_from_explorer)
        self._file_explorer.file_renamed.connect(self._on_file_renamed)
        self._file_explorer.file_deleted.connect(self._on_file_deleted)
        main_layout.addWidget(self._file_explorer)

        # Right side: editor + console split
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Editor tab widget
        self._tab_widget = QTabWidget()
        self._tab_widget.setTabsClosable(True)
        self._tab_widget.tabCloseRequested.connect(self._close_tab)
        self._tab_widget.setMovable(True)
        self._tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #2A2A4A;
                background-color: {theme.EDITOR_BG};
            }}
            QTabBar::tab {{
                background-color: #16213E;
                color: #A6ADC8;
                padding: 6px 14px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-size: 12px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme.EDITOR_BG};
                color: #EAEAEA;
            }}
            QTabBar::tab:hover {{
                background-color: #2A2A4A;
            }}
        """)

        right_splitter.addWidget(self._tab_widget)

        # Console
        console_container = QWidget()
        console_layout = QVBoxLayout(console_container)
        console_layout.setContentsMargins(0, 0, 0, 0)
        console_layout.setSpacing(0)

        self._console_label = QLabel(f"  {theme.label('output', self._lang)}")
        self._console_label.setStyleSheet(f"""
            background-color: #16213E;
            color: {theme.HOLBERTON_RED};
            font-weight: bold;
            font-size: 12px;
            padding: 4px 8px;
            border-top: 1px solid #2A2A4A;
        """)
        console_layout.addWidget(self._console_label)

        self._console = ConsoleWidget()
        self._console.program_started.connect(self._on_program_started)
        self._console.program_finished.connect(self._on_program_finished)
        console_layout.addWidget(self._console)

        right_splitter.addWidget(console_container)

        # Set initial split sizes (editor: 60%, console: 40%)
        right_splitter.setSizes([450, 300])
        right_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2A2A4A;
                height: 3px;
            }
        """)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self._file_explorer)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([200, 1000])
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #2A2A4A;
                width: 3px;
            }
        """)

        main_layout.addWidget(main_splitter)

    def _setup_statusbar(self):
        """Create status bar."""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

    def _setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Run (F5)
        run_shortcut = QAction(self)
        run_shortcut.setShortcut(QKeySequence("F5"))
        run_shortcut.triggered.connect(self._run_script)
        self.addAction(run_shortcut)

        # Run (Ctrl+Enter)
        run_shortcut2 = QAction(self)
        run_shortcut2.setShortcut(QKeySequence("Ctrl+Return"))
        run_shortcut2.triggered.connect(self._run_script)
        self.addAction(run_shortcut2)

        # New file (Ctrl+N) — already in menu
        # Save (Ctrl+S) — already in menu
        # Close tab (Ctrl+W) — already in menu

    # ── Tab management ──────────────────────────────────────────────────

    def _current_tab(self) -> EditorTab:
        """Return the current editor tab."""
        widget = self._tab_widget.currentWidget()
        if isinstance(widget, EditorTab):
            return widget
        return None

    def _new_untitled_tab(self, content=None):
        """Open a new untitled tab."""
        tab = EditorTab(content=content or "# Write your code here! :)\n\n")
        idx = self._tab_widget.addTab(tab, "untitled.py")
        self._tab_widget.setCurrentIndex(idx)
        tab.editor.content_changed.connect(lambda: self._update_tab_title(idx))
        tab.editor.file_saved.connect(lambda: self._update_tab_title(idx))
        tab.editor.setFocus()

    def _update_tab_title(self, idx):
        """Update tab title to reflect modified state."""
        tab = self._tab_widget.widget(idx)
        if isinstance(tab, EditorTab):
            title = tab.tab_title()
            self._tab_widget.setTabText(idx, title)

    def _open_file_from_explorer(self, filepath):
        """Open a file from the file explorer."""
        self._open_file_by_path(filepath)

    def _open_file_by_path(self, filepath):
        """Open a file in a new tab, or switch to existing tab if already open."""
        # Check if already open
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.filepath() == filepath:
                self._tab_widget.setCurrentIndex(i)
                return

        # Open in new tab
        tab = EditorTab(filepath=filepath)
        idx = self._tab_widget.addTab(tab, tab.tab_title())
        self._tab_widget.setCurrentIndex(idx)
        tab.editor.content_changed.connect(lambda: self._update_tab_title(idx))
        tab.editor.file_saved.connect(lambda: self._update_tab_title(idx))
        tab.editor.setFocus()
        self._file_explorer.select_file(filepath)

    def _open_file(self):
        """Show Open File dialog."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open File" if self._lang == "en" else "Abrir Archivo",
            self._workspace,
            "Python Files (*.py);;All Files (*)",
        )
        if filepath:
            self._open_file_by_path(filepath)

    def _close_current_tab(self):
        """Close the current tab."""
        idx = self._tab_widget.currentIndex()
        if idx >= 0:
            self._close_tab(idx)

    def _close_tab(self, idx):
        """Close a tab, prompting to save if modified."""
        tab = self._tab_widget.widget(idx)
        if not isinstance(tab, EditorTab):
            return

        if tab.is_modified():
            result = QMessageBox.question(
                self,
                "Save?" if self._lang == "en" else "Guardar?",
                f"'{tab.tab_title()}' has unsaved changes. Save before closing?" if self._lang == "en"
                else f"'{tab.tab_title()}' tiene cambios sin guardar. ¿Guardar antes de cerrar?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if result == QMessageBox.StandardButton.Save:
                if not self._save_tab(tab):
                    return  # Save failed, don't close
            elif result == QMessageBox.StandardButton.Cancel:
                return

        self._tab_widget.removeTab(idx)
        tab.deleteLater()

        # If no tabs left, create a new untitled one
        if self._tab_widget.count() == 0:
            self._new_untitled_tab()

    def _save_current(self):
        """Save the current file."""
        tab = self._current_tab()
        if tab:
            self._save_tab(tab)

    def _save_tab(self, tab) -> bool:
        """Save a tab. Returns True on success."""
        if tab.filepath():
            result = tab.save()
            if result:
                self._statusbar.showMessage(theme.label("saved", self._lang), 3000)
            return result
        else:
            return self._save_tab_as(tab)

    def _save_current_as(self):
        """Save current file with a new name."""
        tab = self._current_tab()
        if tab:
            self._save_tab_as(tab)

    def _save_tab_as(self, tab) -> bool:
        """Save tab with a new file name. Returns True on success."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save As..." if self._lang == "en" else "Guardar Como...",
            os.path.join(self._workspace, "untitled.py"),
            "Python Files (*.py);;All Files (*)",
        )
        if filepath:
            if tab.save(filepath):
                tab.set_filepath(filepath)
                idx = self._tab_widget.indexOf(tab)
                self._update_tab_title(idx)
                self._file_explorer.refresh()
                self._file_explorer.select_file(filepath)
                self._statusbar.showMessage(theme.label("saved", self._lang), 3000)
                return True
        return False

    # ── Script execution ─────────────────────────────────────────────────

    def _run_script(self):
        """Run the current script."""
        tab = self._current_tab()
        if tab is None:
            return

        if self._console.is_running():
            return

        # Auto-save before running
        filepath = tab.filepath()
        if filepath is None:
            # Untitled file — save to temp
            filepath = os.path.join(self._workspace, "untitled_temp.py")

        # Always save before running so the child process reads the latest content
        if tab.is_modified():
            if tab.filepath():
                tab.save()
            else:
                tab.save(filepath)

        # Make sure the file exists on disk
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self,
                "Error",
                "Please save the file before running." if self._lang == "en"
                else "Guarda el archivo antes de ejecutar.",
            )
            return

        self._console.set_spanish(self._lang == "es")
        self._console.run_script(filepath)

    def _stop_script(self):
        """Stop the running script."""
        self._console.stop_script()

    def _clear_output(self):
        """Clear the console output."""
        self._console.clear()

    def _on_program_started(self):
        """Handle program start."""
        self._run_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._status_label.setText(theme.label("running", self._lang))
        self._status_label.setStyleSheet("color: #2ECC71; font-size: 12px; background: transparent;")

    def _on_program_finished(self, exit_code):
        """Handle program end."""
        self._run_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)

        if exit_code == 0:
            msg = theme.label("program_ended", self._lang)
        elif exit_code == -1:
            msg = theme.label("program_killed", self._lang)
        else:
            msg = theme.label("program_ended", self._lang) + f" (exit {exit_code})"

        self._status_label.setText(msg)
        self._status_label.setStyleSheet("color: #F9E2AF; font-size: 12px; background: transparent;")

    # ── Template handling ────────────────────────────────────────────────

    def _open_template(self, key):
        """Open a starter template."""
        from .templates import get_template
        tmpl = get_template(key)
        content = tmpl["content"]
        filename = tmpl["filename"]

        # Save to workspace
        filepath = os.path.join(self._workspace, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                f.write(content)
            self._file_explorer.refresh()

        # Open in new tab
        self._open_file_by_path(filepath)

    # ── File explorer callbacks ─────────────────────────────────────────

    def _on_file_renamed(self, old_path, new_path):
        """Handle file rename from explorer."""
        # Update any open tabs
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.filepath() == old_path:
                tab.set_filepath(new_path)
                self._update_tab_title(i)
                break

    def _on_file_deleted(self, filepath):
        """Handle file deletion from explorer."""
        # Close any open tab for this file
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.filepath() == filepath:
                self._tab_widget.removeTab(i)
                tab.deleteLater()
                break

        # If no tabs left, create new
        if self._tab_widget.count() == 0:
            self._new_untitled_tab()

    # ── Autosave ────────────────────────────────────────────────────────

    def _autosave(self):
        """Auto-save all modified files every 20 seconds."""
        saved_any = False
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.is_modified() and tab.filepath():
                if tab.save():
                    saved_any = True

        if saved_any:
            self._statusbar.showMessage(theme.label("autosaved", self._lang), 3000)

    # ── Language toggle ─────────────────────────────────────────────────

    def _set_language(self, lang):
        """Switch between English and Spanish UI."""
        self._lang = lang
        self._console.set_spanish(lang == "es")
        self._file_explorer.set_language(lang)

        # Rebuild menus
        menubar = self.menuBar()
        menubar.clear()
        self._setup_menu()

        # Update toolbar labels
        self._run_btn.setText(" ▶ " + theme.label("run", lang) + " ")
        self._stop_btn.setText(" ■ " + theme.label("stop", lang) + " ")
        self._save_btn.setText(" 💾 " + theme.label("save", lang) + " ")
        self._clear_btn.setText(" 🗑 " + theme.label("clear", lang) + " ")
        self._status_label.setText(theme.label("ready", lang))

    # ── About ────────────────────────────────────────────────────────────

    def _show_about(self):
        """Show the About dialog."""
        about_text = (
            "<h2 style='color: #C7254E;'>Holberton Jr. Code Studio</h2>"
            "<p>A beginner-friendly Python editor for kids ages 10-14.</p>"
            "<p>Built for Holberton School summer camps in Puerto Rico.</p>"
            "<p style='color: #A6ADC8;'>Version 1.0</p>"
        ) if self._lang == "en" else (
            "<h2 style='color: #C7254E;'>Holberton Jr. Code Studio</h2>"
            "<p>Un editor de Python para niños de 10-14 años.</p>"
            "<p>Hecho para los campamentos de verano de Holberton School en Puerto Rico.</p>"
            "<p style='color: #A6ADC8;'>Version 1.0</p>"
        )
        QMessageBox.about(self, theme.label("about", self._lang), about_text)

    # ── Window events ────────────────────────────────────────────────────

    def closeEvent(self, event):
        """Prompt to save modified files before closing."""
        modified_tabs = []
        for i in range(self._tab_widget.count()):
            tab = self._tab_widget.widget(i)
            if isinstance(tab, EditorTab) and tab.is_modified():
                modified_tabs.append((i, tab))

        if modified_tabs:
            result = QMessageBox.question(
                self,
                "Save?" if self._lang == "en" else "Guardar?",
                f"You have {len(modified_tabs)} unsaved file(s). Save before closing?" if self._lang == "en"
                else f"Tienes {len(modified_tabs)} archivo(s) sin guardar. ¿Guardar antes de cerrar?",
                QMessageBox.StandardButton.SaveAll |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel,
            )
            if result == QMessageBox.StandardButton.SaveAll:
                for _, tab in modified_tabs:
                    self._save_tab(tab)
            elif result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Stop any running program
        if self._console.is_running():
            self._console.stop_script()

        event.accept()