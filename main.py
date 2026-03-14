"""
main.py — git_ai Orchestrator

Full 10-step pipeline:
  1  Interpret issue
  2  Scan repository
  3  Detect relevant files
  4  Load code
  5  Generate fix (LLM)
  6  Apply patch to file
  7  Create git branch + commit
  8  Push branch to GitHub
  9  Create Pull Request
  10 AI Code Review
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT))

from agent.repo_analyzer        import scan_repository
from agent.issue_interpreter_v2 import interpret_issue, print_parsed_issue
from agent.code_generator       import generate_fix
from utils.file_loader          import load_files, format_file_block
from utils.code_parser          import extract_lines_with_keywords
from git_tools.patch_applier_v2 import apply_patch, extract_code_from_llm_output, PatchResult
from git_tools.repo_manager     import branch_and_commit, print_commit_result
from github_tools.pr_creator    import create_pull_request, print_pr_result
from review_engine.pr_reviewer  import review_pull_request, print_review_result

MAX_RELEVANT_FILES = 5


def find_relevant_files(all_files: list[str], keywords: list[str]) -> list[str]:
    kw_lower = [kw.lower() for kw in keywords]

    def score(fp: str) -> int:
        return sum(1 for kw in kw_lower if kw in fp.lower())

    scored = sorted([(f, score(f)) for f in all_files], key=lambda x: x[1], reverse=True)
    matched = [f for f, s in scored if s > 0]
    if not matched:
        matched = [f for f, _ in scored[:MAX_RELEVANT_FILES]]
    return matched[:MAX_RELEVANT_FILES]


def build_code_blocks(relevant_files: list[str], repo_path: str, keywords: list[str]) -> list[str]:
    loaded = load_files(relevant_files, repo_root=repo_path)
    blocks: list[str] = []
    for result in loaded:
        if result["error"]:
            blocks.append(format_file_block(result))
            continue
        highlighted = extract_lines_with_keywords(result["content"], keywords)
        if highlighted:
            snippet = f"[File: {result['path']}]\n" + "\n".join(highlighted) + "\n"
        else:
            snippet = format_file_block(result)
        blocks.append(snippet)
    return blocks


def _ok(label: str) -> None:
    print(f"  [OK] {label}")


def _fail(label: str, reason: str) -> None:
    print(f"  [FAIL] {label}: {reason}")


def run(issue: str, repo_path: str) -> None:
    print("\n" + "=" * 60)
    print("  git_ai - AI Developer Brain  |  Full Pipeline")
    print("=" * 60)

    # Step 1
    print("\n[1/10] Analysing issue ...")
    parsed = interpret_issue(issue)
    print_parsed_issue(parsed)

    # Step 2
    print("[2/10] Scanning repository ...")
    all_files = scan_repository(repo_path)
    if not all_files:
        print("  No source files found. Check the repo path.")
        return
    _ok(f"{len(all_files)} source file(s) detected")
    print()

    # Step 3
    print("[3/10] Detecting relevant files ...")
    relevant = find_relevant_files(all_files, parsed.keywords)
    if not relevant:
        print("  No relevant files found.")
        return
    for f in relevant:
        print(f"    * {f}")
    print()

    # Step 4
    print("[4/10] Loading code content ...")
    code_blocks = build_code_blocks(relevant, repo_path, parsed.keywords)
    _ok(f"{len(code_blocks)} file(s) loaded")
    print()

    # Step 5
    print("[5/10] Generating fix (LLM) ...")
    llm_response = generate_fix(parsed.raw_text, code_blocks)
    _ok("Fix generated")
    print()
    print("-" * 60)
    print("  AI Suggestion:")
    print("-" * 60)
    print(llm_response)
    print("-" * 60 + "\n")

    # Step 6
    print("[6/10] Applying patch ...")
    patched_files: list[str] = []
    patch_results: list[PatchResult] = []

    for rel_file in relevant:
        result = apply_patch(
            file_path=rel_file,
            llm_response=llm_response,
            keywords=parsed.keywords,
            repo_root=repo_path,
        )
        patch_results.append(result)
        if result.success:
            _ok(f"Patched -> {rel_file}  ({result.lines_changed} lines changed)")
            patched_files.append(rel_file)
        else:
            _fail(f"Patch failed for {rel_file}", result.error)

    if not patched_files:
        print("\n  No files were patched. Stopping.")
        return
    print()

    # Step 7
    print("[7/10] Creating git branch and committing ...")
    repo_root = Path(repo_path).resolve()
    abs_patched = [str((repo_root / f).resolve()) for f in patched_files]
    commit_result = branch_and_commit(
        repo_path=repo_path,
        modified_files=abs_patched,
        issue_text=parsed.raw_text,
        component=parsed.component,
    )
    print_commit_result(commit_result)
    print()

    if not commit_result.success:
        print("=" * 60)
        print("  Pipeline halted at git commit - fix is on disk but not committed.")
        print("=" * 60 + "\n")
        return

    # Step 8 + 9
    print("[8/10] Pushing branch to GitHub ...")
    patch_code = extract_code_from_llm_output(llm_response)
    print()

    print("[9/10] Creating Pull Request ...")
    pr_result = create_pull_request(
        repo_path=repo_path,
        branch=commit_result.branch,
        issue_text=parsed.raw_text,
        component=parsed.component,
        issue_type=parsed.issue_type,
        patch_code=patch_code,
    )
    print_pr_result(pr_result)
    print()

    # Step 10
    if pr_result.success:
        print("[10/10] Running AI code review ...")
        review_result = review_pull_request(
            repo_path=repo_path,
            pr_number=pr_result.pr_number,
            issue_text=parsed.raw_text,
        )
        print_review_result(review_result)
        print()
    else:
        review_result = None

    # Final summary
    print()
    print("=" * 60)
    if pr_result.success:
        print("  [OK] Pipeline Complete - AI fix shipped to GitHub!")
        print(f"  Branch  : {commit_result.branch}")
        print(f"  Commit  : {commit_result.commit_sha}")
        print(f"  PR #    : {pr_result.pr_number}")
        print(f"  PR URL  : {pr_result.pr_url}")
        if review_result and review_result.success:
            print(f"  Verdict : {review_result.verdict}")
            print(f"  Review  : {review_result.comment_url}")
    elif commit_result.success:
        print("  [OK] Phase 1+2 done - commit created (push/PR failed)")
        print(f"  Branch : {commit_result.branch}")
        print(f"  Commit : {commit_result.commit_sha}")
        print(f"  Reason : {pr_result.error}")
        print()
        print("  To push manually:")
        print(f"    git push origin {commit_result.branch}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    repo = sys.argv[1] if len(sys.argv) > 1 else "."

    if not sys.stdin.isatty():
        issue_text = sys.stdin.read().strip()
    else:
        print("\nEnter the issue description (press Enter twice to submit):")
        lines: list[str] = []
        try:
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
        except EOFError:
            pass
        issue_text = "\n".join(lines).strip()

    if not issue_text:
        print("No issue description provided. Exiting.")
        sys.exit(1)

    run(issue_text, repo)
