"""
github_auth.py

Handles authentication with the GitHub API.
Reads a Personal Access Token (PAT) from the GITHUB_TOKEN environment variable
and returns an authenticated PyGitHub client.

How to set the token:
  Windows:  setx GITHUB_TOKEN ghp_your_token_here
  Linux:    export GITHUB_TOKEN=ghp_your_token_here

Required token scopes:
  - repo          (read + write repository content, branches)
  - pull_request  (included under repo in classic tokens)
  - workflow      (for triggering CI, optional)
"""

import os
import sys

try:
    from github import Github, Auth, GithubException  # type: ignore  (PyGithub)
    PYGITHUB_AVAILABLE = True
except ImportError:
    PYGITHUB_AVAILABLE = False


# ── Constants ─────────────────────────────────────────────────────────────────

TOKEN_ENV_VAR = "GITHUB_TOKEN"


# ── Auth helpers ──────────────────────────────────────────────────────────────

def get_token() -> str:
    """
    Read the GitHub PAT from the environment.
    Raises EnvironmentError with a clear message if not set.
    """
    token = os.environ.get(TOKEN_ENV_VAR, "").strip()
    if not token:
        raise EnvironmentError(
            f"GitHub token not found.\n"
            f"Set it with:  setx {TOKEN_ENV_VAR} <your_token>  (Windows)\n"
            f"           or export {TOKEN_ENV_VAR}=<your_token>  (Linux/Mac)\n"
            f"Generate a token at: https://github.com/settings/tokens\n"
            f"Required scopes: repo, workflow"
        )
    return token


def get_github_client() -> "Github":
    """
    Return an authenticated PyGitHub client.

    Raises:
        ImportError       if PyGithub is not installed
        EnvironmentError  if GITHUB_TOKEN is not set
        GithubException   if the token is invalid
    """
    if not PYGITHUB_AVAILABLE:
        raise ImportError(
            "PyGithub is not installed. Run: pip install PyGithub"
        )

    token = get_token()
    auth   = Auth.Token(token)
    client = Github(auth=auth)

    # Eagerly validate the token by fetching the authenticated user
    try:
        user = client.get_user()
        _ = user.login          # triggers the API call
    except Exception as exc:
        raise RuntimeError(
            f"GitHub authentication failed. Check your token.\nError: {exc}"
        ) from exc

    return client


def get_authenticated_user(client: "Github") -> str:
    """Return the login name of the authenticated user."""
    return client.get_user().login


if __name__ == "__main__":
    try:
        gh   = get_github_client()
        name = get_authenticated_user(gh)
        print(f"✔ Authenticated as: {name}")
    except Exception as exc:
        print(f"✘ Auth error: {exc}", file=sys.stderr)
        sys.exit(1)
