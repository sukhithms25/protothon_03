"""
code_parser.py

Lightweight code-parsing utilities.
Extracts function/class names and key identifiers from source text
without requiring a full AST (works across languages).
"""

import re
from pathlib import Path


# Simple regex patterns for common constructs
_PYTHON_DEF = re.compile(r"^\s*(?:def|class)\s+(\w+)", re.MULTILINE)
_JS_FUNC = re.compile(
    r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\()",
    re.MULTILINE,
)
_GENERIC_WORD = re.compile(r"\b([a-zA-Z_]\w{2,})\b")


def extract_symbols(content: str, extension: str = ".py") -> list[str]:
    """
    Extract function / class / variable names from source text.

    Args:
        content:    Raw source code as a string.
        extension:  File extension (e.g. '.py', '.js') to pick the right pattern.

    Returns:
        Deduplicated list of symbol names found.
    """
    ext = extension.lower()
    symbols: list[str] = []

    if ext == ".py":
        symbols = _PYTHON_DEF.findall(content)
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        for m in _JS_FUNC.finditer(content):
            name = m.group(1) or m.group(2)
            if name:
                symbols.append(name)
    else:
        # Fall back to all significant words
        symbols = _GENERIC_WORD.findall(content)

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for s in symbols:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique


def extract_lines_with_keywords(content: str, keywords: list[str]) -> list[str]:
    """
    Return lines from *content* that contain at least one keyword (case-insensitive).

    Useful for pulling the most relevant code snippets for the LLM prompt.
    """
    kw_lower = [kw.lower() for kw in keywords]
    result: list[str] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        if any(kw in line.lower() for kw in kw_lower):
            result.append(f"{lineno:4d}: {line}")
    return result


def get_extension(file_path: str) -> str:
    return Path(file_path).suffix.lower()


if __name__ == "__main__":
    import sys
    src = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else ""
    ext = get_extension(sys.argv[1]) if len(sys.argv) > 1 else ".py"
    print("Symbols:", extract_symbols(src, ext))
