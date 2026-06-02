"""Dark theme stylesheet and QScintilla color definitions."""

# Holberton School brand colors
HOLBERTON_RED = "#C7254E"
HOLBERTON_DARK = "#1A1A2E"
HOLBERTON_DARKER = "#16213E"
HOLBERTON_LIGHT = "#EAEAEA"
HOLBERTON_ACCENT = "#E94560"

# Editor background
EDITOR_BG = "#1E1E2E"
EDITOR_FG = "#CDD6F4"
EDITOR_LINENUMBER_BG = "#181825"
EDITOR_LINENUMBER_FG = "#6C7086"

# Syntax highlighting colors (Catppuccin Mocha-inspired)
SYN_DEFAULT = "#CDD6F4"     # Default text
SYN_COMMENT = "#6C7086"     # Comments
SYN_KEYWORD = "#CBA6F7"     # Python keywords (purple)
SYN_STRING = "#A6E3A1"      # Strings (green)
SYN_SINGLESTRING = "#F9E2AF" # Single-quoted strings (yellow)
SYN_NUMBER = "#FAB387"      # Numbers (peach)
SYN_DECORATOR = "#F38BA8"   # Decorators (red/pink)
SYN_CLASSNAME = "#F9E2AF"   # Class names (yellow)
SYN_FUNCTIONNAME = "#89B4FA" # Function/method names (blue)
SYN_OPERATOR = "#89DCEB"    # Operators (teal)
SYN_TRIPLESTRING = "#A6E3A1" # Triple-quoted strings
SYN_IDENTIFIER = "#CDD6F4"  # Identifiers

# Console colors
CONSOLE_BG = "#11111B"
CONSOLE_FG = "#CDD6F4"
CONSOLE_ERROR_FG = "#F38BA8"
CONSOLE_HINT_FG = "#F9E2AF"

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1A1A2E;
}
QWidget {
    background-color: #1A1A2E;
    color: #EAEAEA;
    font-family: 'Segoe UI', 'Noto Sans', sans-serif;
    font-size: 13px;
}
QMenuBar {
    background-color: #16213E;
    color: #EAEAEA;
    border-bottom: 1px solid #2A2A4A;
    padding: 2px;
}
QMenuBar::item:selected {
    background-color: #C7254E;
    border-radius: 4px;
}
QMenu {
    background-color: #16213E;
    color: #EAEAEA;
    border: 1px solid #2A2A4A;
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #C7254E;
}
QMenu::separator {
    height: 1px;
    background: #2A2A4A;
    margin: 4px 8px;
}
QToolBar {
    background-color: #16213E;
    border-bottom: 1px solid #2A2A4A;
    padding: 4px;
    spacing: 6px;
}
QToolButton {
    background-color: #2A2A4A;
    color: #EAEAEA;
    border: 1px solid #3A3A5A;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: bold;
    min-width: 60px;
}
QToolButton:hover {
    background-color: #3A3A5A;
}
QToolButton:pressed {
    background-color: #4A4A6A;
}
QPushButton {
    background-color: #2A2A4A;
    color: #EAEAEA;
    border: 1px solid #3A3A5A;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #3A3A5A;
}
QSplitter::handle {
    background-color: #2A2A4A;
    width: 3px;
}
QTreeView {
    background-color: #11111B;
    color: #CDD6F4;
    border: none;
    font-size: 12px;
    outline: none;
}
QTreeView::item {
    padding: 3px 4px;
    border-radius: 3px;
}
QTreeView::item:selected {
    background-color: #C7254E;
    color: #FFFFFF;
}
QTreeView::item:hover {
    background-color: #2A2A4A;
}
QHeaderView::section {
    background-color: #16213E;
    color: #EAEAEA;
    border: none;
    padding: 4px;
    font-weight: bold;
}
QPlainTextEdit {
    background-color: #11111B;
    color: #CDD6F4;
    border: none;
    font-family: 'Fira Code', 'Cascadia Code', 'Consolas', monospace;
    font-size: 13px;
    selection-background-color: #45475A;
}
QLabel {
    color: #EAEAEA;
    background: transparent;
}
QStatusBar {
    background-color: #16213E;
    color: #A6ADC8;
    border-top: 1px solid #2A2A4A;
    font-size: 12px;
}
QTabWidget::pane {
    border: 1px solid #2A2A4A;
    background-color: #1A1A2E;
}
QTabBar::tab {
    background-color: #16213E;
    color: #A6ADC8;
    padding: 6px 12px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1A1A2E;
    color: #EAEAEA;
}
QMessageBox {
    background-color: #1A1A2E;
    color: #EAEAEA;
}
QMessageBox QLabel {
    color: #EAEAEA;
}
QInputDialog {
    background-color: #1A1A2E;
    color: #EAEAEA;
}
QScrollBar:vertical {
    background: #11111B;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #45475A;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #585B70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #11111B;
    height: 10px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #45475A;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #585B70;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QFrame#fileExplorerFrame {
    background-color: #11111B;
    border-right: 1px solid #2A2A4A;
}
"""


# English/Spanish label translations
LABELS = {
    "run": {"en": "Run", "es": "Ejecutar"},
    "stop": {"en": "Stop", "es": "Detener"},
    "save": {"en": "Save", "es": "Guardar"},
    "clear": {"en": "Clear Output", "es": "Limpiar"},
    "new_file": {"en": "New File", "es": "Nuevo Archivo"},
    "file": {"en": "File", "es": "Archivo"},
    "edit": {"en": "Edit", "es": "Editar"},
    "view": {"en": "View", "es": "Ver"},
    "templates": {"en": "Templates", "es": "Plantillas"},
    "language": {"en": "Language", "es": "Idioma"},
    "help": {"en": "Help", "es": "Ayuda"},
    "about": {"en": "About Holberton Jr.", "es": "Acerca de Holberton Jr."},
    "files": {"en": "My Files", "es": "Mis Archivos"},
    "output": {"en": "Output", "es": "Salida"},
    "unsaved": {"en": " (modified)", "es": " (modificado)"},
    "confirm_delete": {"en": "Delete {name}?", "es": "Eliminar {name}?"},
    "confirm_delete_msg": {
        "en": "Are you sure you want to delete '{name}'?",
        "es": "Estas seguro de que quieres eliminar '{name}'?",
    },
    "file_exists": {"en": "File already exists", "es": "El archivo ya existe"},
    "new_file_prompt": {"en": "New Python file name:", "es": "Nombre del nuevo archivo Python:"},
    "rename_prompt": {"en": "New name for {name}:", "es": "Nuevo nombre para {name}:"},
    "running": {"en": "Running...", "es": "Ejecutando..."},
    "ready": {"en": "Ready", "es": "Listo"},
    "saved": {"en": "Saved", "es": "Guardado"},
    "autosaved": {"en": "Auto-saved", "es": "Auto-guardado"},
    "program_ended": {"en": "Program finished", "es": "Programa terminado"},
    "program_killed": {"en": "Program stopped", "es": "Programa detenido"},
}


def label(key: str, lang: str = "en") -> str:
    """Get a translated label by key."""
    entry = LABELS.get(key, {})
    return entry.get(lang, entry.get("en", key))