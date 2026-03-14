"""
file_loader.py

Allows the AI to read code content from detected files.
Handles encoding fallbacks and large-file guards.
"""

from pathlib import Path

MAX_FILE_SIZE_BYTES = 1_000_000  # 1 MB — skip files larger than this


def load_file(file_path: str, repo_root: str = "") -> dict:
    """
    Read the contents of a source file.

    Args:
        file_path:  Path to the file (absolute or relative to repo_root).
        repo_root:  Optional repository root to resolve relative paths.

    Returns:
        A dict with keys:
            path    – resolved file path (str)
            content – file text (str), or None on error
            error   – error message (str), or None on success
    """
    path = Path(file_path)
    if repo_root:
        path = Path(repo_root) / path

    path = path.resolve()

    if not path.exists():
        return {"path": str(path), "content": None, "error": "File not found"}

    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return {
            "path": str(path),
            "content": None,
            "error": f"File too large (>{MAX_FILE_SIZE_BYTES // 1024} KB), skipped",
        }

    # Try UTF-8 first, fall back to latin-1 to avoid crashes on binary-ish files
    for encoding in ("utf-8", "latin-1"):
        try:
            content = path.read_text(encoding=encoding)
            return {"path": str(path), "content": content, "error": None}
        except (UnicodeDecodeError, OSError):
            continue

    return {"path": str(path), "content": None, "error": "Could not decode file"}


def load_files(file_paths: list[str], repo_root: str = "") -> list[dict]:
    """
    Load multiple files at once.

    Returns:
        List of dicts (same shape as load_file).
    """
    return [load_file(fp, repo_root) for fp in file_paths]


def format_file_block(file_result: dict) -> str:
    """
    Format a loaded file result as a readable text block for LLM prompts.
    """
    if file_result["error"]:
        return f"[File: {file_result['path']}]\nERROR: {file_result['error']}\n"
    return f"[File: {file_result['path']}]\n{file_result['content']}\n"


if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else __file__
    result = load_file(p)
    print(format_file_block(result))
