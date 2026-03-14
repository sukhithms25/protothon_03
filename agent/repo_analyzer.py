"""
repo_analyzer.py

The "eyes" of the AI Developer Brain.
Scans a repository directory, collects all source file paths,
and filters for known code file extensions.
"""

import os
from pathlib import Path

# Extensions we consider source code
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rb", ".rs", ".php", ".cs",
    ".swift", ".kt", ".r", ".sh", ".yaml",
    ".yml", ".json", ".toml", ".html", ".css",
}

# Directories to skip (noise / not actual source)
IGNORED_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv",
    "venv", "env", ".mypy_cache", ".pytest_cache",
    "dist", "build", ".idea", ".vscode",
}


def scan_repository(repo_path: str) -> list[str]:
    """
    Walk the repository root and return a list of relative code-file paths.

    Args:
        repo_path: Absolute or relative path to the repository root.

    Returns:
        Sorted list of relative file paths (strings) for all detected code files.
    """
    repo_root = Path(repo_path).resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_root}")

    collected: list[str] = []

    for dirpath, dirnames, filenames in os.walk(repo_root):
        # Prune ignored directories in-place so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        for filename in filenames:
            ext = Path(filename).suffix.lower()
            if ext in CODE_EXTENSIONS:
                full_path = Path(dirpath) / filename
                rel_path = full_path.relative_to(repo_root)
                collected.append(str(rel_path))

    return sorted(collected)


def print_scan_results(repo_path: str) -> list[str]:
    """
    Convenience wrapper: scan, pretty-print, and return results.
    """
    print(f"\nScanning repository: {repo_path}\n")
    files = scan_repository(repo_path)

    if not files:
        print("No source files detected.")
    else:
        print(f"Files detected ({len(files)} total):")
        for f in files:
            print(f"  {f}")

    return files


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    print_scan_results(path)
