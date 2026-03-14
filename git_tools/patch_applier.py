"""
patch_applier.py

Applies an AI-generated fix to a target source file.

Strategy (SWE-agent-style safe patching):
  Instead of naive string replacement, we:
  1. Parse the LLM output to extract the actual code block
  2. Identify the region of code to replace using the keywords from the issue
  3. Write a backup of the original file before touching it
  4. Write the updated file atomically (to a temp path, then rename)

This means a bad patch cannot corrupt the original — rollback is always possible.
"""

import re
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass, field


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class PatchResult:
    success: bool
    target_file: str
    backup_file: str = ""
    lines_changed: int = 0
    error: str = ""
    patch_code: str = ""          # the extracted/applied code snippet


# ── LLM output → code block ───────────────────────────────────────────────────

_CODE_BLOCK_RE = re.compile(
    r"```(?:python|py|javascript|js|typescript|ts|java|go|ruby|rb|c|cpp)?\s*\n"
    r"(.*?)"
    r"```",
    re.DOTALL | re.IGNORECASE,
)


def extract_code_from_llm_output(llm_response: str) -> str:
    """
    Pull the first fenced code block out of the LLM's response.
    Falls back to lines that look like code if no fence is found.
    """
    matches = _CODE_BLOCK_RE.findall(llm_response)
    if matches:
        return matches[0].strip()

    # Heuristic fallback: lines that start with keywords typical of a fix
    fix_lines = [
        line for line in llm_response.splitlines()
        if line.strip() and not line.startswith(("#", "*", "-", ">", "**"))
    ]
    return "\n".join(fix_lines).strip()


# ── Line-range detection ──────────────────────────────────────────────────────

def find_problem_region(content: str, keywords: list[str]) -> tuple[int, int]:
    """
    Locate the contiguous block of lines most likely containing the bug.

    Returns (start_line, end_line) — 0-indexed, inclusive.
    Falls back to (0, 0) if nothing is found.
    """
    lines = content.splitlines()
    kw_lower = [kw.lower() for kw in keywords]

    hit_indices = [
        i for i, line in enumerate(lines)
        if any(kw in line.lower() for kw in kw_lower)
    ]

    if not hit_indices:
        return 0, 0

    # Expand the region slightly so we capture surrounding context
    start = max(0, min(hit_indices) - 1)
    end   = min(len(lines) - 1, max(hit_indices) + 2)
    return start, end


# ── Safe file writer ──────────────────────────────────────────────────────────

def _backup_file(path: Path) -> Path:
    """Create a .bak copy of the file and return the backup path."""
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    return backup


def _atomic_write(path: Path, content: str) -> None:
    """Write to a temp file first, then rename — avoids partial writes."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(tmp_fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        shutil.move(tmp_path, path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


# ── Main entry point ──────────────────────────────────────────────────────────

def apply_patch(
    file_path: str,
    llm_response: str,
    keywords: list[str],
    repo_root: str = "",
    dry_run: bool = False,
) -> PatchResult:
    """
    Apply the fix extracted from *llm_response* to *file_path*.

    Args:
        file_path:    Relative or absolute path to the file to patch.
        llm_response: Raw text output from the LLM (may include prose + code block).
        keywords:     Issue keywords used to locate the problematic region.
        repo_root:    If provided, resolve file_path relative to this root.
        dry_run:      If True, compute the patch but don't write anything.

    Returns:
        PatchResult dataclass.
    """
    path = Path(file_path)
    if repo_root:
        path = Path(repo_root) / path
    path = path.resolve()

    if not path.exists():
        return PatchResult(success=False, target_file=str(path),
                           error="File not found")

    # Step 1 — Extract code from LLM output
    patch_code = extract_code_from_llm_output(llm_response)
    if not patch_code:
        return PatchResult(success=False, target_file=str(path),
                           error="Could not extract a code block from LLM response")

    # Step 2 — Read original
    original = path.read_text(encoding="utf-8")
    lines    = original.splitlines(keepends=True)

    # Step 3 — Find problem region
    start, end = find_problem_region(original, keywords)

    # Step 4 — Build replacement
    # Preserve indentation of the first hit line
    indent = ""
    if lines:
        first_hit = lines[start]
        indent = " " * (len(first_hit) - len(first_hit.lstrip()))

    # Indent patch lines to match the context
    patch_lines = [
        (indent + pl if pl.strip() else pl) + "\n"
        for pl in patch_code.splitlines()
    ]

    new_lines = lines[:start] + patch_lines + lines[end + 1:]
    new_content = "".join(new_lines)

    lines_changed = abs(len(patch_lines) - (end - start + 1)) + len(patch_lines)

    if dry_run:
        return PatchResult(
            success=True,
            target_file=str(path),
            lines_changed=lines_changed,
            patch_code=patch_code,
        )

    # Step 5 — Backup + atomic write
    backup = _backup_file(path)
    try:
        _atomic_write(path, new_content)
    except Exception as exc:
        # Restore from backup
        shutil.copy2(backup, path)
        return PatchResult(
            success=False,
            target_file=str(path),
            backup_file=str(backup),
            error=f"Write failed (original restored): {exc}",
        )

    return PatchResult(
        success=True,
        target_file=str(path),
        backup_file=str(backup),
        lines_changed=lines_changed,
        patch_code=patch_code,
    )


def rollback(result: PatchResult) -> bool:
    """
    Restore the original file from its backup.
    Returns True on success.
    """
    if not result.backup_file:
        return False
    try:
        shutil.copy2(result.backup_file, result.target_file)
        Path(result.backup_file).unlink(missing_ok=True)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    import sys
    mock_llm = (
        "The fix:\n"
        "```python\n"
        "if not password or not password.strip():\n"
        '    return {"error": "Password is required"}, 400\n'
        "```\n"
    )
    file  = sys.argv[1] if len(sys.argv) > 1 else "sample_project/login.py"
    kws   = ["password", "login", "empty"]
    result = apply_patch(file, mock_llm, kws, dry_run=True)
    print(result)
