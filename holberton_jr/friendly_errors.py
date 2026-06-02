"""Friendly error messages for kids — maps Python exceptions to plain-English hints."""

import re
from typing import Optional

# Error type -> (English hint, Spanish hint)
ERROR_HINTS = {
    "SyntaxError": (
        "Check for a missing colon (:), quote, or parenthesis.",
        "Revisa si falta un punto y coma (:), una comilla o un parentesis.",
    ),
    "NameError": (
        "You used a name Python doesn't recognize — typo, or defined later?",
        "Usaste un nombre que Python no reconoce — error de escritura o definido despues?",
    ),
    "TypeError": (
        "You may be mixing text and numbers — try str() or an f-string.",
        "Puede que estes mezclando texto y numeros — prueba str() o un f-string.",
    ),
    "IndentationError": (
        "Check your spaces — lines inside an if/for/while must be indented.",
        "Revisa los espacios — las lineas dentro de un if/for/while deben tener sangria.",
    ),
    "IndexError": (
        "You're reaching past the end of a list.",
        "Estas tratando de acceder mas alla del final de una lista.",
    ),
    "ValueError": (
        "int() got something that isn't a number — like letters.",
        "int() recibio algo que no es un numero — como letras.",
    ),
    "ZeroDivisionError": (
        "You tried to divide by zero — that's math-impossible!",
        "Intentaste dividir por cero — eso no se puede en matematicas!",
    ),
    "AttributeError": (
        "That thing doesn't have the method or attribute you typed — check spelling?",
        "Ese objeto no tiene el metodo o atributo que escribiste — revisa la ortografia?",
    ),
    "FileNotFoundError": (
        "Python can't find that file — check the name and path.",
        "Python no puede encontrar ese archivo — revisa el nombre y la ruta.",
    ),
    "RecursionError": (
        "Your function called itself too many times — add a base case!",
        "Tu funcion se llamo a si misma demasiadas veces — agrega un caso base!",
    ),
    "KeyboardInterrupt": (
        "You pressed Ctrl+C to stop the program.",
        "Presionaste Ctrl+C para detener el programa.",
    ),
}

# Regex to detect the last line of a Python traceback: "ErrorType: message"
# This matches both full tracebacks and standalone SyntaxError output
_ERROR_LINE_RE = re.compile(r"^(\w+Error|\w+Exception): .+$", re.MULTILINE)
_TRACEBACK_START_RE = re.compile(r"^Traceback \(most recent call last\):", re.MULTILINE)
_LINE_NUM_RE = re.compile(r'^\s+File "([^"]+)", line (\d+)', re.MULTILINE)


def extract_friendly_hint(output: str, spanish: bool = False) -> Optional[str]:
    """Scan program output for a Python error and return a friendly hint.

    Works with both full tracebacks (starting with "Traceback...") and
    standalone error lines (like SyntaxError which often omits the header).

    Returns None if no recognized error is found.
    """
    # Find all error-type lines in the output
    matches = list(_ERROR_LINE_RE.finditer(output))
    if not matches:
        return None

    # Use the last error line found
    last_match = matches[-1]
    error_line = last_match.group(0)

    # Extract error type (e.g. "SyntaxError" from "SyntaxError: invalid syntax")
    error_type = error_line.split(":")[0].strip()

    # Extract file and line number
    file_matches = _LINE_NUM_RE.findall(output)
    line_info = ""
    if file_matches:
        _, lineno = file_matches[-1]
        line_info = f" (line {lineno})"

    if error_type in ERROR_HINTS:
        idx = 1 if spanish else 0
        hint = ERROR_HINTS[error_type][idx]
        return f"{hint}{line_info}"

    # Generic fallback for unknown error types
    msg = error_line.split(":", 1)[1].strip() if ":" in error_line else error_line
    if spanish:
        return f"Algo salio mal: {error_type}: {msg}{line_info}"
    return f"Something went wrong: {error_type}: {msg}{line_info}"


def format_friendly_block(output: str, spanish: bool = False) -> str:
    """Return the full output with a friendly hint block inserted before the error."""
    hint = extract_friendly_hint(output, spanish)
    if hint is None:
        return output

    separator = "=" * 50
    block = (
        f"\n{separator}\n"
        f"  {hint}\n"
        f"{separator}\n\n"
    )

    # Insert the hint block just before the traceback header if present
    tb_match = _TRACEBACK_START_RE.search(output)
    if tb_match:
        pos = tb_match.start()
        return output[:pos] + block + output[pos:]

    # Otherwise, insert before the error line
    matches = list(_ERROR_LINE_RE.finditer(output))
    if matches:
        pos = matches[-1].start()
        return output[:pos] + block + output[pos:]

    return block + output