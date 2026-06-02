"""File explorer sidebar — lists Python files in the student workspace using QListWidget."""

import os
from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMenu, QInputDialog, QMessageBox,
    QAbstractItemView,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor

from . import theme


def _make_file_icon():
    """Create a simple Python file icon."""
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(0, 0, 0, 0))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#CBA6F7"))  # Purple like our keyword color
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(1, 1, 14, 14, 2, 2)
    p.setPen(QColor("white"))
    p.setFont(QFont("Sans", 8, QFont.Weight.Bold))
    p.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Py")
    p.end()
    return QIcon(pixmap)


class FileExplorer(QWidget):
    """File explorer sidebar showing Python files in the workspace."""

    file_selected = pyqtSignal(str)   # file path
    file_created = pyqtSignal(str)    # file path
    file_renamed = pyqtSignal(str, str)  # old path, new path
    file_deleted = pyqtSignal(str)    # file path

    def __init__(self, workspace_dir: str, parent=None):
        super().__init__(parent)
        self._workspace = os.path.expanduser(workspace_dir)
        self._lang = "en"
        self._file_icon = _make_file_icon()

        # Ensure workspace exists
        os.makedirs(self._workspace, exist_ok=True)

        self._setup_ui()
        self._refresh_file_list()

    def _setup_ui(self):
        """Build the file explorer UI."""
        self.setObjectName("fileExplorerFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with title and + button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 6, 8, 6)

        self._title_label = QLabel(self._lang_title())
        self._title_label.setStyleSheet(f"""
            color: {theme.HOLBERTON_RED};
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        # New file button
        self._new_btn = QPushButton("+")
        self._new_btn.setFixedSize(28, 28)
        self._new_btn.setToolTip("New file" if self._lang == "en" else "Nuevo archivo")
        self._new_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.HOLBERTON_RED};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.HOLBERTON_ACCENT};
            }}
        """)
        self._new_btn.clicked.connect(self._create_new_file)
        header_layout.addWidget(self._new_btn)

        layout.addLayout(header_layout)

        # File list
        self._list = QListWidget(self)
        self._list.setViewMode(QListWidget.ViewMode.ListMode)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setSpacing(2)
        self._list.setIconSize(QSize(16, 16))
        self._list.setUniformItemSizes(True)

        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme.CONSOLE_BG};
                color: {theme.EDITOR_FG};
                border: none;
                outline: none;
                font-family: 'Fira Code', 'Consolas', monospace;
                font-size: 12px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 4px 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {theme.HOLBERTON_RED};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: #2A2A4A;
            }}
        """)

        # Double-click to open
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        # Single click also opens
        self._list.itemClicked.connect(self._on_item_clicked)

        # Context menu
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self._list)

        # Set minimum/maximum width
        self.setMinimumWidth(160)
        self.setMaximumWidth(280)

    def _lang_title(self):
        return "My Files" if self._lang == "en" else "Mis Archivos"

    def workspace_dir(self):
        """Return the workspace directory path."""
        return self._workspace

    def set_language(self, lang: str):
        """Switch UI labels between English and Spanish."""
        self._lang = lang
        self._title_label.setText(self._lang_title())
        self._new_btn.setToolTip("New file" if lang == "en" else "Nuevo archivo")

    def _refresh_file_list(self):
        """Rebuild the file list from the workspace directory."""
        self._list.clear()
        try:
            entries = sorted(os.listdir(self._workspace))
        except OSError:
            return

        for name in entries:
            filepath = os.path.join(self._workspace, name)
            if os.path.isfile(filepath) and (name.endswith(".py") or name.endswith(".txt")):
                item = QListWidgetItem(self._file_icon, name)
                item.setData(Qt.ItemDataRole.UserRole, filepath)
                self._list.addItem(item)

    def refresh(self):
        """Refresh the file list."""
        self._refresh_file_list()

    def select_file(self, filepath: str):
        """Select a file in the list by its path."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == filepath:
                self._list.setCurrentItem(item)
                return

    def _on_item_clicked(self, item):
        """Handle single click on a file item."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath and os.path.isfile(filepath):
            self.file_selected.emit(filepath)

    def _on_item_double_clicked(self, item):
        """Handle double-click (same as single click — open file)."""
        filepath = item.data(Qt.ItemDataRole.UserRole)
        if filepath and os.path.isfile(filepath):
            self.file_selected.emit(filepath)

    def _create_new_file(self):
        """Create a new Python file in the workspace."""
        label = "New Python file name:" if self._lang == "en" else "Nombre del nuevo archivo Python:"
        name, ok = QInputDialog.getText(self, label, label)
        if ok and name.strip():
            # Ensure .py extension
            if not name.endswith(".py"):
                name += ".py"
            filepath = os.path.join(self._workspace, name)
            if os.path.exists(filepath):
                msg = "File already exists" if self._lang == "en" else "El archivo ya existe"
                QMessageBox.warning(self, msg, msg)
                return
            # Create with a simple starter comment
            with open(filepath, "w") as f:
                f.write(f"# {name.replace('.py', '')}\n\n")
            self._refresh_file_list()
            self.file_created.emit(filepath)

    def _show_context_menu(self, pos):
        """Show right-click context menu on a file item."""
        item = self._list.itemAt(pos)
        if item is None:
            return

        filepath = item.data(Qt.ItemDataRole.UserRole)
        if not filepath or not os.path.isfile(filepath):
            return

        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #16213E;
                color: #EAEAEA;
                border: 1px solid #2A2A4A;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {theme.HOLBERTON_RED};
            }}
        """)

        open_action = menu.addAction("Open" if self._lang == "en" else "Abrir")
        rename_action = menu.addAction("Rename" if self._lang == "en" else "Renombrar")
        delete_action = menu.addAction("Delete" if self._lang == "en" else "Eliminar")

        action = menu.exec(self._list.mapToGlobal(pos))

        if action == open_action:
            self.file_selected.emit(filepath)
        elif action == rename_action:
            self._rename_file(filepath, item)
        elif action == delete_action:
            self._delete_file(filepath)

    def _rename_file(self, filepath, item):
        """Rename a file."""
        old_name = os.path.basename(filepath)
        label = f"New name for {old_name}:" if self._lang == "en" else f"Nuevo nombre para {old_name}:"
        new_name, ok = QInputDialog.getText(self, label, label, text=old_name)
        if ok and new_name.strip() and new_name != old_name:
            if not new_name.endswith(".py"):
                new_name += ".py"
            new_path = os.path.join(self._workspace, new_name)
            try:
                os.rename(filepath, new_path)
                self._refresh_file_list()
                self.file_renamed.emit(filepath, new_path)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _delete_file(self, filepath):
        """Delete a file after confirmation."""
        name = os.path.basename(filepath)
        title = f"Delete {name}?" if self._lang == "en" else f"Eliminar {name}?"
        msg = f"Are you sure you want to delete '{name}'?" if self._lang == "en" else f"Estas seguro de que quieres eliminar '{name}'?"
        result = QMessageBox.question(
            self, title, msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                self._refresh_file_list()
                self.file_deleted.emit(filepath)
            except OSError as e:
                QMessageBox.warning(self, "Error", str(e))