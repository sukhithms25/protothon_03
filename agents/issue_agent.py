from services.llm_service import ask_llm
from agents.repo_agent import find_files
from agents.code_agent import generate_fix
from agents.pr_agent import create_pr
from agents.review_agent import review_pr

def process_issue(db, repo_id, issue_title, issue_body, author_id, issue_number=None):
    """Main orchestrator for fixing issues against the local DB."""

    issue_text = f"{issue_title}\n\n{issue_body}"

    print(f"\n[Repo Agent] Searching for relevant files in repo {repo_id}...")
    files = find_files(db, repo_id, issue_text)
    
    if not files:
        return {"status": "error", "message": "No relevant files found in the repository."}

    target_file = files[0]
    print(f"[Code Agent] Generating fix for: {target_file}")

    fix_result = generate_fix(db, repo_id, issue_text, target_file)
    if not fix_result:
        return {"status": "error", "message": "Failed to read file from DB."}

    print(f"[Review Agent] Reviewing the generated fix...")
    review = review_pr(
        fix_result["original_code"],
        fix_result["new_code"],
        fix_result["file_path"]
    )

    print(f"[AI Agent] Summarizing changes...")
    summary_prompt = f"""You are an expert developer. Summarize the changes made to the following code.
FILE: {fix_result["file_path"]}
ORIGINAL:
```
{fix_result["original_code"]}
```
NEW:
```
{fix_result["new_code"]}
```
INSTRUCTIONS:
- Provide a concise list of what changed and where (line numbers or function names).
- Be extremely brief and professional.
"""
    change_summary = ask_llm(summary_prompt).strip()

    print(f"[PR Agent] Creating Pull Request...")
    pr_url = create_pr(
        db=db,
        repo_id=repo_id,
        issue_title=issue_title,
        original_code=fix_result["original_code"],
        new_code=fix_result["new_code"],
        file_path=fix_result["file_path"],
        author_id=author_id,
        review_text=review,
        issue_id=issue_number,
        description=change_summary
    )

    return {
        "status": "success",
        "files_found": files,
        "target_file": target_file,
        "pull_request_url": pr_url,
        "review": review
    }