"""
pr_creator.py

Pushes the AI-generated branch to GitHub and opens a Pull Request.

Flow:
  1. Detect remote repo from git config (origin URL)
  2. Push branch via GitPython (uses existing SSH/HTTPS credentials)
  3. Create Pull Request via PyGitHub REST API

PR naming convention:
  Title:  AI Fix: <component> validation bug
  Branch: ai-fix-<component>-<timestamp>   →   base: main (or master)
"""

import re
import sys
from dataclasses import dataclass

try:
    import git as gitpython  # type: ignore
    GITPYTHON_AVAILABLE = True
except ImportError:
    gitpython = None  # type: ignore
    GITPYTHON_AVAILABLE = False

try:
    from github import GithubException  # type: ignore
    PYGITHUB_AVAILABLE = True
except ImportError:
    GithubException = Exception  # type: ignore
    PYGITHUB_AVAILABLE = False

from github_tools.github_auth import get_github_client


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class PRResult:
    success: bool
    pr_url: str = ""
    pr_number: int = 0
    branch: str = ""
    error: str = ""


# ── Remote repo detection ─────────────────────────────────────────────────────

_SSH_RE   = re.compile(r"git@github\.com[:/](.+?)(?:\.git)?$")
_HTTPS_RE = re.compile(r"https?://(?:.*@)?github\.com/(.+?)(?:\.git)?$")


def _parse_repo_slug(remote_url: str) -> str:
    """
    Extract 'owner/repo' from a GitHub remote URL (SSH or HTTPS).
    e.g.  git@github.com:sukhithms25/git_ai.git  →  sukhithms25/git_ai
    """
    for pattern in (_SSH_RE, _HTTPS_RE):
        m = pattern.search(remote_url)
        if m:
            return m.group(1).strip("/")
    raise ValueError(f"Cannot parse GitHub repo slug from URL: {remote_url!r}")


def get_repo_slug(repo_path: str) -> str:
    """Open the git repo and return the 'owner/repo' slug from origin."""
    if not GITPYTHON_AVAILABLE or gitpython is None:
        raise ImportError("GitPython not installed")
    repo = gitpython.Repo(repo_path, search_parent_directories=True)
    try:
        origin_url = repo.remotes["origin"].url
    except (IndexError, AttributeError):
        raise RuntimeError("No 'origin' remote configured in this repository.")
    return _parse_repo_slug(origin_url)


# ── Push branch ───────────────────────────────────────────────────────────────

def push_branch(repo_path: str, branch_name: str) -> None:
    """
    Push *branch_name* to origin using GitPython.
    Uses whatever credentials git already has (SSH key / credential helper).
    """
    if not GITPYTHON_AVAILABLE or gitpython is None:
        raise ImportError("GitPython not installed")
    repo = gitpython.Repo(repo_path, search_parent_directories=True)
    origin = repo.remotes["origin"]
    push_info = origin.push(refspec=f"{branch_name}:{branch_name}")

    # GitPython returns flags; check for errors
    for info in push_info:
        if info.flags & info.ERROR:
            raise RuntimeError(f"Push failed: {info.summary}")


# ── PR body builder ───────────────────────────────────────────────────────────

def _build_pr_body(
    issue_text: str,
    component: str,
    issue_type: str,
    patch_code: str,
    branch: str,
) -> str:
    patch_section = (
        f"```python\n{patch_code}\n```" if patch_code
        else "_Patch applied directly to file — see diff._"
    )
    return f"""\
## 🤖 AI-Generated Fix

**Issue reported:**
> {issue_text}

**Component:** `{component}`  
**Issue type:** `{issue_type}`  
**Branch:** `{branch}`

---

## Suggested Patch

{patch_section}

---

*This Pull Request was created automatically by [git_ai](https://github.com/sukhithms25/git_ai) assistant.*  
*Review the diff carefully before merging.*
"""


# ── Main entry point ──────────────────────────────────────────────────────────

def create_pull_request(
    repo_path: str,
    branch: str,
    issue_text: str,
    component: str = "unknown",
    issue_type: str = "bug",
    patch_code: str = "",
    base_branch: str = "main",
) -> PRResult:
    """
    Push *branch* to origin and open a PR against *base_branch*.

    Args:
        repo_path:   Local path to the repository root.
        branch:      Name of the AI-generated branch.
        issue_text:  Raw issue description (used in PR title / body).
        component:   Detected component (e.g. 'login').
        issue_type:  Detected type (e.g. 'bug').
        patch_code:  The extracted fix snippet (shown as code block in PR body).
        base_branch: Target branch for the PR (default: 'main').

    Returns:
        PRResult with the PR URL and number on success.
    """
    if not GITPYTHON_AVAILABLE:
        return PRResult(success=False, error="GitPython not installed")
    if not PYGITHUB_AVAILABLE:
        return PRResult(success=False, error="PyGithub not installed. Run: pip install PyGithub")

    # ── Step 1: Push branch ───────────────────────────────────────────────────
    try:
        push_branch(repo_path, branch)
    except Exception as exc:
        return PRResult(success=False, branch=branch,
                        error=f"Push failed: {exc}")

    # ── Step 2: Connect to GitHub ─────────────────────────────────────────────
    try:
        gh = get_github_client()
    except Exception as exc:
        return PRResult(success=False, branch=branch,
                        error=f"GitHub auth failed: {exc}")

    # ── Step 3: Get repo ──────────────────────────────────────────────────────
    slug = ""
    try:
        slug      = get_repo_slug(repo_path)
        gh_repo   = gh.get_repo(slug)
    except Exception as exc:
        return PRResult(success=False, branch=branch,
                        error=f"Cannot locate GitHub repo '{slug if slug else 'unknown'}': {exc}")

    # ── Step 4: Create PR ─────────────────────────────────────────────────────
    title = f"AI Fix: {component} validation bug"
    body  = _build_pr_body(issue_text, component, issue_type, patch_code, branch)

    try:
        pr = gh_repo.create_pull(
            title=title,
            body=body,
            head=branch,
            base=base_branch,
        )
        return PRResult(
            success=True,
            pr_url=pr.html_url,
            pr_number=pr.number,
            branch=branch,
        )
    except GithubException as exc:
        # Common case: PR already exists for this branch
        msg = str(exc)
        # Only access 'data' if exc is a GithubException and has 'data'
        errors = [{}]
        if isinstance(exc, GithubException) and hasattr(exc, "data") and isinstance(getattr(exc, "data", None), dict):
            errors = getattr(exc, "data", {}).get("errors", [{}])
            if errors and isinstance(errors, list) and isinstance(errors[0], dict):
                msg = errors[0].get("message", str(exc))
        return PRResult(success=False, branch=branch, error=f"PR creation failed: {msg}")
    except Exception as exc:
        return PRResult(success=False, branch=branch, error=str(exc))


def print_pr_result(result: PRResult) -> None:
    if result.success:
        print(f"  [OK] Pull Request #{result.pr_number} created")
        print(f"  [OK] URL: {result.pr_url}")
    else:
        print(f"  [FAIL] PR error: {result.error}", file=sys.stderr)


if __name__ == "__main__":
    # Quick test — requires GITHUB_TOKEN to be set
    result = create_pull_request(
        repo_path=".",
        branch="ai-fix-test",
        issue_text="Fix login crash when password empty",
        component="login",
    )
    print_pr_result(result)
