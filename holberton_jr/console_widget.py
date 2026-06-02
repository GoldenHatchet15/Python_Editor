"""PTY-based console widget — runs Python scripts in a real terminal with full input() support."""

import os
import pty
import signal
import fcntl
import termios
import struct
import re
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QSocketNotifier, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QKeyEvent, QTextCharFormat, QColor

from . import friendly_errors
from . import theme


class ConsoleWidget(QPlainTextEdit):
    """Terminal emulator widget that communicates with a child process via PTY.

    - Spawns `python3 <script>` in a PTY so input() works interactively.
    - Reads output via QSocketNotifier on the PTY master fd.
    - Forwards keystrokes from the user to the PTY master fd.
    - Supports friendly error hints injected before tracebacks.
    """

    program_started = pyqtSignal()
    program_finished = pyqtSignal(int)  # exit code

    def __init__(self, parent=None):
        super().__init__(parent)
        self._master_fd = None
        self._child_pid = None
        self._notifier = None
        self._input_pos = 0  # position where user input starts
        self._running = False
        self._output_buffer = ""  # accumulate output for friendly error detection
        self._spanish = False
        self._cols = 80
        self._rows = 24

        self._setup_console()

    def _setup_console(self):
        """Configure console appearance."""
        font = QFont("Fira Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {theme.CONSOLE_BG};
                color: {theme.CONSOLE_FG};
                border: none;
                font-family: 'Fira Code', 'Consolas', monospace;
                font-size: 11pt;
                selection-background-color: #45475A;
            }}
        """)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.setCursorWidth(10)  # Block cursor feel
        self._update_cursor_style()

    def _update_cursor_style(self):
        """Update cursor to be wide when running, thin when idle."""
        if self._running:
            self.setCursorWidth(10)
            self.setStyleSheet(self.styleSheet())
        else:
            self.setCursorWidth(2)

    def is_running(self):
        """Return whether a program is currently running."""
        return self._running

    def run_script(self, script_path):
        """Spawn the script as a child process in a PTY."""
        if self._running:
            return

        self.clear()
        self._output_buffer = ""

        master_fd, slave_fd = pty.openpty()

        # Set terminal size
        winsize = struct.pack("HHHH", self._rows, self._cols, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)

        pid = os.fork()

        if pid == 0:
            # Child process
            os.close(master_fd)
            os.setsid()

            # Set slave as controlling terminal
            fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)

            os.dup2(slave_fd, 0)  # stdin
            os.dup2(slave_fd, 1)  # stdout
            os.dup2(slave_fd, 2)  # stderr

            if slave_fd > 2:
                os.close(slave_fd)

            # Set environment for turtle
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"

            try:
                os.execvpe("python3", ["python3", "-u", script_path], env)
            except Exception as e:
                # If exec fails, write error to stdout (which goes to master)
                os.write(1, f"Error starting Python: {e}\n".encode())
                os._exit(1)
        else:
            # Parent process
            os.close(slave_fd)

            # Set master_fd to non-blocking
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            self._master_fd = master_fd
            self._child_pid = pid
            self._running = True
            self._update_cursor_style()

            # Set up QSocketNotifier to read from the PTY
            self._notifier = QSocketNotifier(master_fd, QSocketNotifier.Type.Read, self)
            self._notifier.activated.connect(self._read_pty_output)

            self.program_started.emit()

    def stop_script(self):
        """Kill the running script. Send SIGTERM, then SIGKILL if needed."""
        if not self._running or self._child_pid is None:
            return

        try:
            # Kill the entire process group
            os.killpg(self._child_pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except OSError:
            pass

        # Give it a moment, then force kill
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self._force_kill)

    def _force_kill(self):
        """Force-kill the child process with SIGKILL."""
        if not self._running or self._child_pid is None:
            return
        try:
            os.killpg(self._child_pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except OSError:
            pass

    def _read_pty_output(self):
        """Read data from PTY master fd and display it."""
        if self._master_fd is None:
            return

        try:
            data = os.read(self._master_fd, 4096)
            if not data:
                # EOF — child process ended
                self._on_process_exit()
                return

            text = data.decode("utf-8", errors="replace")
            self._output_buffer += text

            # Display the output
            self._append_output(text)

        except BlockingIOError:
            # No data available right now
            pass
        except OSError:
            # PTY closed
            self._on_process_exit()

    def _append_output(self, text):
        """Append text to the console, processing ANSI escape sequences."""
        # Strip ANSI escape sequences for display
        # (We keep a few basic ones but strip colors/cursors)
        clean_text = self._strip_ansi(text)
        if clean_text:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(clean_text)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()
            self._input_pos = cursor.position()

    def _strip_ansi(self, text):
        """Remove ANSI escape sequences from text."""
        # Remove CSI sequences (colors, cursor movement, etc.)
        ansi_re = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[.*?[a-zA-Z]')
        text = ansi_re.sub('', text)
        # Remove other control characters except newline, tab, carriage return
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1a\x1c-\x1f]', '', text)
        # Handle carriage return (for progress bars, etc.)
        # Simple CR handling: text after CR on same line replaces text before
        return text

    def _on_process_exit(self):
        """Handle child process termination."""
        if self._notifier:
            self._notifier.setEnabled(False)
            self._notifier.deleteLater()
            self._notifier = None

        # Drain any remaining output
        self._drain_pty()

        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None

        # Check friendly errors
        hint = friendly_errors.extract_friendly_hint(self._output_buffer, self._spanish)
        if hint:
            self._insert_friendly_hint(hint)

        # Check if process was killed vs. normal exit
        exit_code = 0
        if self._child_pid is not None:
            try:
                _, status = os.waitpid(self._child_pid, os.WNOHANG)
                if os.WIFEXITED(status):
                    exit_code = os.WEXITSTATUS(status)
                elif os.WIFSIGNALED(status):
                    sig = os.WTERMSIG(status)
                    if sig == signal.SIGKILL or sig == signal.SIGTERM:
                        self._append_output("\n\n--- Program stopped ---\n")
                    exit_code = -1
            except ChildProcessError:
                pass

        self._child_pid = None
        self._running = False
        self._update_cursor_style()
        self.program_finished.emit(exit_code)

    def _drain_pty(self):
        """Read any remaining data from the PTY."""
        if self._master_fd is None:
            return
        while True:
            try:
                data = os.read(self._master_fd, 4096)
                if not data:
                    break
                text = data.decode("utf-8", errors="replace")
                self._output_buffer += text
                self._append_output(text)
            except (BlockingIOError, OSError):
                break

    def _insert_friendly_hint(self, hint):
        """Insert a friendly error hint into the console before the error output."""
        separator = "=" * 50
        block = (
            f"\n{separator}\n"
            f"  {hint}\n"
            f"{separator}\n"
        )

        cursor = self.textCursor()

        # Find where to insert the hint:
        # 1. Before "Traceback (most recent call last):" if present
        # 2. Before the error line (e.g., "SyntaxError: ...") if no traceback header
        # 3. At the end as fallback
        console_text = self.toPlainText()
        tb_match = re.search(r'Traceback \(most recent call last\):', console_text)

        if tb_match:
            # Insert before the traceback
            pos = tb_match.start()
            cursor.setPosition(pos)
            cursor.insertText(block)
        else:
            # Try to find the error line (e.g., "SyntaxError: ...")
            err_match = re.search(r'^\s*\w+Error: .+$', console_text, re.MULTILINE)
            if err_match:
                # Insert before the File line that precedes the error, or before the error itself
                file_match = re.search(r'^\s+File "[^"]+", line \d+', console_text, re.MULTILINE)
                if file_match:
                    pos = file_match.start()
                    cursor.setPosition(pos)
                    cursor.insertText(block)
                else:
                    pos = err_match.start()
                    cursor.setPosition(pos)
                    cursor.insertText(block)
            else:
                # Append at the end
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(block)

        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def set_spanish(self, spanish: bool):
        """Set the language for friendly error messages."""
        self._spanish = spanish

    def keyPressEvent(self, event: QKeyEvent):
        """Forward keystrokes to the PTY when a program is running."""
        if not self._running or self._master_fd is None:
            return

        key = event.key()
        text = event.text()
        modifiers = event.modifiers()

        # Handle special keys
        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            # Send just \r — the PTY's ICRNL translates it to \n for the child.
            # Sending \r\n would produce TWO newlines: \r->\n and the \n as-is.
            self._write_to_pty(b'\r')
        elif key == Qt.Key.Key_Backspace:
            self._write_to_pty(b'\x7f')  # DEL character
        elif key == Qt.Key.Key_Delete:
            self._write_to_pty(b'\x1b[3~')  # VT100 delete
        elif key == Qt.Key.Key_Up:
            self._write_to_pty(b'\x1b[A')
        elif key == Qt.Key.Key_Down:
            self._write_to_pty(b'\x1b[B')
        elif key == Qt.Key.Key_Left:
            self._write_to_pty(b'\x1b[D')
        elif key == Qt.Key.Key_Right:
            self._write_to_pty(b'\x1b[C')
        elif key == Qt.Key.Key_Home:
            self._write_to_pty(b'\x1b[H')
        elif key == Qt.Key.Key_End:
            self._write_to_pty(b'\x1b[F')
        elif key == Qt.Key.Key_Tab:
            self._write_to_pty(b'\t')
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+C
            if key == Qt.Key.Key_C:
                self._write_to_pty(b'\x03')
            # Ctrl+D
            elif key == Qt.Key.Key_D:
                self._write_to_pty(b'\x04')
            # Ctrl+A
            elif key == Qt.Key.Key_A:
                self._write_to_pty(b'\x01')
            # Ctrl+E
            elif key == Qt.Key.Key_E:
                self._write_to_pty(b'\x05')
            # Ctrl+L (clear screen)
            elif key == Qt.Key.Key_L:
                self._write_to_pty(b'\x0c')
            else:
                # Other Ctrl+key combos
                if key >= Qt.Key.Key_A and key <= Qt.Key.Key_Z:
                    self._write_to_pty(bytes([key - Qt.Key.Key_A + 1]))
        elif text:
            # Regular character
            self._write_to_pty(text.encode("utf-8"))

    def _write_to_pty(self, data: bytes):
        """Write data to the PTY master fd."""
        if self._master_fd is not None:
            try:
                os.write(self._master_fd, data)
            except OSError:
                pass

    def resize_pty(self, cols, rows):
        """Resize the PTY to match the console widget."""
        self._cols = cols
        self._rows = rows
        if self._master_fd is not None:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    def clear(self):
        """Clear the console."""
        super().clear()
        self._output_buffer = ""
        self._input_pos = 0