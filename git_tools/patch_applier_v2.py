"""
patch_applier_v2.py

IMPROVED patch applier that intelligently inserts fixes instead of blindly replacing regions.

Strategy:
  1. Extract fix code from LLM output
  2. Analyze WHERE the fix should go (function start, before logic, etc.)
  3. INSERT validation code at the right location
  4. Preserve all existing code structure
  5. Validate syntax after patching
"""

import re
import ast
import shutil
import tempfile
from pathlib import Path
from dataclasses import dataclass


@dataclass
class PatchResult:
    success: bool
    target_file: str
    backup_file: str = ""
    lines_changed: int = 0
    error: str = ""
    patch_code: str = ""


_CODE_BLOCK_RE = re.compile(
    r"```(?:python|py|javascript|js|typescript|ts|java|go|ruby|rb|c|cpp)?\s*\n"
    r"(.*?)"
    r"```",
    re.DOTALL | re.IGNORECASE,
)


def extract_code_from_llm_output(llm_response: str) -> str:
    """Extract the first fenced code block from LLM response."""
    matches = _CODE_BLOCK_RE.findall(llm_response)
    if matches:
        return matches[0].strip()
    
    # Fallback: lines that look like code
    fix_lines = [
        line for line in llm_response.splitlines()
        if line.strip() and not line.startswith(("#", "*", "-", ">", "**"))
    ]
    return "\n".join(fix_lines).strip()


def validate_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if Python file has valid syntax."""
    try:
        code = file_path.read_text(encoding="utf-8")
        compile(code, str(file_path), 'exec')
        return True, ""
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def find_insertion_point(content: str, keywords: list[str]) -> int:
    """
    Find the best line to INSERT validation code.
    
    Strategy:
    - Look for function definitions containing keywords
    - Insert validation at the START of the function body
    - Returns line number (0-indexed) where to insert
    """
    lines = content.splitlines()
    kw_lower = [kw.lower() for kw in keywords]
    
    # Find function definitions that match keywords
    for i, line in enumerate(lines):
        # Check if this is a function definition
        if re.match(r'^\s*def\s+\w+\s*\(', line):
            # Check if function name or nearby lines contain keywords
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+10)]).lower()
            if any(kw in context for kw in kw_lower):
                # Found the function - insert after the def line
                # Skip docstrings if present
                insert_line = i + 1
                if insert_line < len(lines) and '"""' in lines[insert_line]:
                    # Skip to end of docstring
                    for j in range(insert_line + 1, len(lines)):
                        if '"""' in lines[j]:
                            insert_line = j + 1
                            break
                return insert_line
    
    # Fallback: insert at the first line with a keyword
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in kw_lower):
            return i
    
    return 0


def get_indentation(lines: list[str], line_num: int) -> str:
    """Get the indentation of a specific line."""
    if line_num >= len(lines):
        return "    "
    line = lines[line_num]
    return " " * (len(line) - len(line.lstrip()))


def _backup_file(path: Path) -> Path:
    """Create a .bak copy of the file."""
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    return backup


def _atomic_write(path: Path, content: str) -> None:
    """Write to a temp file first, then rename."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(tmp_fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        shutil.move(tmp_path, path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def apply_patch_smart(
    file_path: str,
    llm_response: str,
    keywords: list[str],
    repo_root: str = "",
    dry_run: bool = False,
) -> PatchResult:
    """
    Intelligently INSERT fix code at the right location.
    
    This version INSERTS validation code instead of REPLACING regions.
    """
    path = Path(file_path)
    if repo_root:
        path = Path(repo_root) / path
    path = path.resolve()

    if not path.exists():
        return PatchResult(success=False, target_file=str(path),
                           error="File not found")

    # Extract fix code
    patch_code = extract_code_from_llm_output(llm_response)
    if not patch_code:
        return PatchResult(success=False, target_file=str(path),
                           error="Could not extract code block from LLM response")

    # Read original
    original = path.read_text(encoding="utf-8")

    # Duplicate check - skip if fix already applied
    if patch_code.strip() in original:
        return PatchResult(success=True, target_file=str(path),
                           lines_changed=0, patch_code=patch_code)
    lines = original.splitlines(keepends=True)

    # Find where to insert
    insert_at = find_insertion_point(original, keywords)
    
    # Get proper indentation
    indent = get_indentation([l.rstrip('\n\r') for l in lines], insert_at)
    
    # Format patch lines with proper indentation
    patch_lines = [
        (indent + pl if pl.strip() else pl) + "\n"
        for pl in patch_code.splitlines()
    ]
    
    # INSERT the patch (don't replace)
    new_lines = lines[:insert_at] + patch_lines + lines[insert_at:]
    new_content = "".join(new_lines)

    if dry_run:
        return PatchResult(
            success=True,
            target_file=str(path),
            lines_changed=len(patch_lines),
            patch_code=patch_code,
        )

    # Backup original
    backup = _backup_file(path)
    
    try:
        # Write new content
        _atomic_write(path, new_content)
        
        # Validate syntax for Python files
        if path.suffix == ".py":
            valid, error = validate_python_syntax(path)
            if not valid:
                # Rollback on syntax error
                shutil.copy2(backup, path)
                return PatchResult(
                    success=False,
                    target_file=str(path),
                    backup_file=str(backup),
                    error=f"Syntax validation failed: {error}",
                )
        
        return PatchResult(
            success=True,
            target_file=str(path),
            backup_file=str(backup),
            lines_changed=len(patch_lines),
            patch_code=patch_code,
        )
        
    except Exception as exc:
        # Restore from backup
        shutil.copy2(backup, path)
        return PatchResult(
            success=False,
            target_file=str(path),
            backup_file=str(backup),
            error=f"Write failed (original restored): {exc}",
        )


# Alias for backward compatibility
apply_patch = apply_patch_smart


if __name__ == "__main__":
    import sys
    mock_llm = (
        "The fix:\n"
        "```python\n"
        "if not password or not password.strip():\n"
        '    return {"error": "Password is required"}, 400\n'
        "```\n"
    )
    file = sys.argv[1] if len(sys.argv) > 1 else "sample_project/login.py"
    kws = ["password", "login", "empty"]
    result = apply_patch(file, mock_llm, kws, dry_run=True)
    print(result)
