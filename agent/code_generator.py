"""
code_generator.py

The reasoning core of the AI Developer Brain.
Sends the issue + relevant code to a local Ollama LLM and returns
a suggested patch / fix.

Model default: codellama (change MODEL below to match what you have pulled).
Run `ollama list` to see available models.
"""

import sys
from pathlib import Path

try:
    import ollama  # type: ignore
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# ── Configuration ───────────────────────────────────────────────────────────

MODEL = "qwen2.5-coder:7b"          # swap for "llama3", "mistral", "deepseek-coder", etc.
MAX_CONTEXT_CHARS = 6_000    # trim code snippets to avoid exceeding context window

# ── Prompt template ─────────────────────────────────────────────────────────

PROMPT_TEMPLATE = """\
You are a senior software engineer fixing a bug.

Bug report:
{issue}

Relevant code:
{code}

Instructions:
1. Identify the root cause
2. Write ONLY the fix as a code block
3. Do NOT rewrite the entire file
4. Do NOT remove any existing logic
5. Keep the fix minimal and correct

Return the fix in this exact format:
```python
<your fix here>
```
"""

# ── Helpers ──────────────────────────────────────────────────────────────────

def _trim_code(code: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    """Trim code to fit within context limits."""
    if len(code) <= max_chars:
        return code
    half = max_chars // 2
    return (
        code[:half]
        + f"\n\n... [truncated {len(code) - max_chars} chars] ...\n\n"
        + code[-half:]
    )


def _build_prompt(issue: str, code_blocks: list[str]) -> str:
    combined_code = "\n\n".join(code_blocks)
    trimmed = _trim_code(combined_code)
    return PROMPT_TEMPLATE.format(issue=issue, code=trimmed)


# ── Main entry point ─────────────────────────────────────────────────────────

def generate_fix(issue: str, code_blocks: list[str]) -> str:
    """
    Ask the local LLM to suggest a fix.

    Args:
        issue:       The raw issue description string.
        code_blocks: List of strings — each is the content of one relevant file.

    Returns:
        The LLM's response as a plain string.
        Falls back to a mock response if Ollama is not available.
    """
    prompt = _build_prompt(issue, code_blocks)

    if not OLLAMA_AVAILABLE:
        return _mock_response(issue)

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        # Ollama is installed but the server might not be running
        print(f"[code_generator] Ollama error: {exc}", file=sys.stderr)
        print("[code_generator] Falling back to mock response.", file=sys.stderr)
        return _mock_response(issue)


def _mock_response(issue: str) -> str:
    """
    Offline fallback — useful for testing without Ollama running.
    Returns a plausible-looking fix for the most common issue keywords.
    """
    issue_lower = issue.lower()
    if "password" in issue_lower and ("empty" in issue_lower or "blank" in issue_lower):
        return (
            "**Root cause:** The code does not validate whether `password` is empty "
            "before proceeding with authentication, causing a crash or unintended login.\n\n"
            "**Suggested Fix:**\n"
            "```python\n"
            "if not password or not password.strip():\n"
            '    return {"error": "Password is required"}, 400\n'
            "```\n"
            "**Why it works:** Checking `not password` catches both `None` and empty strings. "
            "`.strip()` also handles whitespace-only inputs."
        )
    return (
        "**Suggested Fix:**\n"
        "```\n"
        "# Add input validation before processing\n"
        "if not input_value:\n"
        '    return {"error": "Input required"}, 400\n'
        "```\n"
        "(This is a generic fallback — start Ollama for AI-generated fixes.)"
    )


if __name__ == "__main__":
    issue = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Fix login crash when password empty"
    sample_code = "def login():\n    password = request.json['password']\n    authenticate(password)\n"
    print(generate_fix(issue, [sample_code]))
