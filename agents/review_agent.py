from services.llm_service import ask_llm


def review_pr(original_code, new_code, file_path):
    """Use AI to review the generated code changes."""

    prompt = f"""You are a senior code reviewer.
Review the following code change and give a brief assessment.

FILE: {file_path}

ORIGINAL CODE:
```
{original_code}
```

MODIFIED CODE:
```
{new_code}
```

Provide:
1. A brief summary of what was changed
2. Whether the change looks correct
3. Any potential issues or improvements
Keep your review concise (max 5 lines).
"""

    return ask_llm(prompt)