from services.llm_service import ask_llm
from services.db_service import get_repo_files

def find_files(db, repo_id, issue_text):
    """Use the DB to list repo files, then ask AI to pick the most relevant ones."""
    db_files = get_repo_files(db, repo_id)
    all_files = [f.path for f in db_files]
    
    if not all_files:
        return []

    file_list = "\n".join(all_files)

    prompt = f"""You are an expert software engineer. 
Given the following issue and a list of files in the repository, identify which file(s) are most likely related to the issue and need to be modified to fix it.

ISSUE:
{issue_text}

FILES IN THE REPOSITORY:
{file_list}

INSTRUCTIONS:
- Return ONLY the file paths, one per line.
- Return the most relevant files first.
- Do NOT include any explanation, markdown formatting, or extra text.
- If no files seem relevant, return "NONE".
"""

    response = ask_llm(prompt).strip()

    if response.upper() == "NONE":
        return []

    relevant = []
    for line in response.split("\n"):
        line = line.strip().strip("`").strip("-").strip("*").strip()
        if line and line in all_files:
            relevant.append(line)

    if not relevant:
        return all_files[:5]

    return relevant