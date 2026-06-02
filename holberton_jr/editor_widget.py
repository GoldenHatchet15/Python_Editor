"""QScintilla-based Python editor widget with dark theme, auto-indent, and unsaved tracking."""

from PyQt6.QtGui import QFont, QColor, QKeyEvent
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.Qsci import QsciScintilla, QsciLexerPython

from . import theme


def _c(hex_color: str) -> QColor:
    """Create a QColor from a hex string."""
    return QColor(hex_color)


class PythonEditor(QsciScintilla):
    """Code editor widget using QScintilla with Python lexer."""

    content_changed = pyqtSignal()
    file_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filepath = None
        self._is_modified = False
        self._encoding = "utf-8"

        self._setup_editor()
        self._setup_lexer()
        self._connect_signals()

    def _setup_editor(self):
        """Configure editor appearance and behavior."""
        # Font
        font = QFont("Fira Code", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        # Margins (line numbers)
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, "  50 ")
        self.setMarginsForegroundColor(_c(theme.EDITOR_LINENUMBER_FG))
        self.setMarginsBackgroundColor(_c(theme.EDITOR_LINENUMBER_BG))

        # Auto-indent
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)

        # Brace matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        self.setMatchedBraceForegroundColor(_c("#F9E2AF"))
        self.setUnmatchedBraceForegroundColor(_c("#F38BA8"))

        # Current line highlighting
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(_c(theme.EDITOR_BG))

        # Colors
        self.setColor(_c(theme.EDITOR_FG))
        self.setCaretForegroundColor(_c(theme.EDITOR_FG))

        # EOL mode
        self.setEolMode(QsciScintilla.EolMode.EolUnix)

        # Whitespace
        self.setWhitespaceVisibility(QsciScintilla.WhitespaceVisibility.WsInvisible)

        # Selection colors
        self.setSelectionForegroundColor(_c("#CDD6F4"))
        self.setSelectionBackgroundColor(_c("#45475A"))

        # Edge column (80 char guide)
        self.setEdgeColumn(80)
        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColor(_c("#313244"))

        # Auto-completion
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(2)

        # Scrollbar
        self.setScrollWidth(1)
        self.setScrollWidthTracking(True)

    def _setup_lexer(self):
        """Configure the Python lexer with dark theme colors."""
        self._lexer = QsciLexerPython(self)

        # Use a consistent font for all lexer styles
        font = QFont("Fira Code", 12)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._lexer.setFont(font)

        # Map QsciLexerPython style numbers to our theme colors
        color_map = {
            QsciLexerPython.Default: theme.SYN_DEFAULT,
            QsciLexerPython.Comment: theme.SYN_COMMENT,
            QsciLexerPython.Number: theme.SYN_NUMBER,
            QsciLexerPython.DoubleQuotedString: theme.SYN_STRING,
            QsciLexerPython.SingleQuotedString: theme.SYN_SINGLESTRING,
            QsciLexerPython.TripleDoubleQuotedString: theme.SYN_TRIPLESTRING,
            QsciLexerPython.TripleSingleQuotedString: theme.SYN_TRIPLESTRING,
            QsciLexerPython.Keyword: theme.SYN_KEYWORD,
            QsciLexerPython.ClassName: theme.SYN_CLASSNAME,
            QsciLexerPython.FunctionMethodName: theme.SYN_FUNCTIONNAME,
            QsciLexerPython.Operator: theme.SYN_OPERATOR,
            QsciLexerPython.Identifier: theme.SYN_IDENTIFIER,
            QsciLexerPython.Decorator: theme.SYN_DECORATOR,
            QsciLexerPython.CommentBlock: theme.SYN_COMMENT,
            QsciLexerPython.UnclosedString: "#F38BA8",
        }

        for style_id, color_hex in color_map.items():
            self._lexer.setColor(_c(color_hex), style_id)
            self._lexer.setFont(font, style_id)

        # Paper (background) for all styles
        for i in range(128):
            self._lexer.setPaper(_c(theme.EDITOR_BG), i)

        self.setLexer(self._lexer)

    def _connect_signals(self):
        """Connect internal signals."""
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self):
        """Handle text change — track modified state."""
        was_modified = self._is_modified
        self._is_modified = True
        if not was_modified:
            self.content_changed.emit()

    def filepath(self):
        """Return the current file path, or None if untitled."""
        return self._filepath

    def set_filepath(self, path):
        """Set the file path (without loading)."""
        self._filepath = path

    def is_modified(self):
        """Return whether the editor has unsaved changes."""
        return self._is_modified

    def load_file(self, path):
        """Load a file into the editor."""
        try:
            with open(path, "r", encoding=self._encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(path, "r", encoding="latin-1") as f:
                content = f.read()

        self._filepath = path
        self.setText(content)
        self._is_modified = False
        # Clear undo history after loading
        self.SendScintilla(self.SCI_EMPTYUNDOBUFFER)

    def save_file(self, path=None):
        """Save editor content to file. Returns True on success."""
        save_path = path or self._filepath
        if save_path is None:
            return False

        try:
            with open(save_path, "w", encoding=self._encoding) as f:
                f.write(self.text())
            self._filepath = save_path
            self._is_modified = False
            self.file_saved.emit()
            return True
        except OSError as e:
            print(f"Save error: {e}")
            return False

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press for custom shortcuts."""
        # Ctrl+S is handled by main window, don't let Scintilla eat it
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_S:
            event.ignore()
            return
        # Ctrl+Enter / F5 handled by main window
        if event.key() == Qt.Key.Key_F5:
            event.ignore()
            return
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Return:
            event.ignore()
            return
        super().keyPressEvent(event)

    def reset_modified(self):
        """Mark the editor as unmodified (after autosave, etc.)."""
        self._is_modified = False