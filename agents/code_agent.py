import re
from services.llm_service import ask_llm
from services.db_service import get_file_content

def generate_fix(db, repo_id, issue_text, file_path):
    """Fetch the file content from DB, send to AI, and get the corrected code."""

    current_code = get_file_content(db, repo_id, file_path)
    if current_code is None:
        return None

    prompt = f"""You are an expert software engineer.

TASK: Fix the code in the file below based on the issue described.

ISSUE:
{issue_text}

FILE PATH: {file_path}

CURRENT FILE CONTENT:
```
{current_code}
```

INSTRUCTIONS:
- Return ONLY the complete corrected file content.
- Do NOT include any explanation, markdown fences, or extra text.
- The output must be valid code that can directly replace the file content.
- If the file does not need changes, return the original content unchanged.
- Make minimal, targeted changes to fix the issue.
"""

    response = ask_llm(prompt)
    new_code = strip_code_fences(response)

    return {
        "file_path": file_path,
        "new_code": new_code,
        "original_code": current_code
    }

def strip_code_fences(text):
    text = text.strip()
    pattern = r'^```[\w]*\n(.*?)```$'
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()

    if text.startswith("```") and text.endswith("```"):
        lines = text.split("\n")
        return "\n".join(lines[1:-1]).strip()

    return text