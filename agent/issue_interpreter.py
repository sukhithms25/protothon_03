"""
issue_interpreter.py

Understands a bug report / feature issue and extracts:
  - component  : the system area likely involved
  - type       : "bug", "feature", "refactor", etc.
  - keywords   : terms that will be used to search the repository

Works entirely offline — no LLM call needed for this step.
"""

import re
from dataclasses import dataclass, field

# ── Heuristic keyword maps ──────────────────────────────────────────────────

# Maps common issue tokens → guessed component names
COMPONENT_HINTS: dict[str, list[str]] = {
    "login":       ["login", "signin", "sign_in", "auth"],
    "register":    ["register", "signup", "sign_up"],
    "password":    ["password", "passwd", "pwd"],
    "database":    ["database", "db", "sql", "query", "model"],
    "api":         ["api", "route", "endpoint", "request", "response"],
    "user":        ["user", "profile", "account"],
    "payment":     ["payment", "stripe", "billing", "checkout"],
    "upload":      ["upload", "file", "storage", "s3", "blob"],
    "email":       ["email", "mail", "smtp", "notification"],
    "search":      ["search", "index", "query", "filter"],
    "cache":       ["cache", "redis", "memcache"],
    "test":        ["test", "spec", "assert"],
}

BUG_SIGNALS    = {"crash", "error", "bug", "fix", "broken", "fail", "exception",
                  "traceback", "null", "none", "undefined", "nan", "404", "500"}
FEATURE_SIGNALS = {"add", "implement", "create", "new", "feature", "support",
                   "allow", "enable"}
REFACTOR_SIGNALS = {"refactor", "clean", "improve", "optimise", "optimize",
                    "restructure", "rename"}


# ── Data model ─────────────────────────────────────────────────────────────

@dataclass
class ParsedIssue:
    raw_text:  str
    component: str               = "unknown"
    issue_type: str              = "unknown"
    keywords:  list[str]        = field(default_factory=list)


# ── Core logic ─────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    """Lower-case alphabetic tokens only."""
    return re.findall(r"[a-z]+", text.lower())


def _detect_component(tokens: list[str]) -> str:
    token_set = set(tokens)
    for component, hints in COMPONENT_HINTS.items():
        if token_set & set(hints):
            return component
    return "unknown"


def _detect_type(tokens: list[str]) -> str:
    token_set = set(tokens)
    if token_set & BUG_SIGNALS:
        return "bug"
    if token_set & FEATURE_SIGNALS:
        return "feature"
    if token_set & REFACTOR_SIGNALS:
        return "refactor"
    return "unknown"


def _extract_keywords(tokens: list[str]) -> list[str]:
    """
    Return meaningful tokens — skip very short stopwords and duplicates.
    These are what will be matched against file paths and code content.
    """
    stopwords = {
        "the", "a", "an", "is", "in", "on", "at", "to", "of",
        "and", "or", "but", "for", "with", "when", "that", "this",
        "it", "be", "was", "are", "has", "have", "not",
    }
    seen: set[str] = set()
    result: list[str] = []
    for t in tokens:
        if len(t) >= 3 and t not in stopwords and t not in seen:
            seen.add(t)
            result.append(t)
    return result


def interpret_issue(issue_text: str) -> ParsedIssue:
    """
    Main entry point.  Parse a free-form issue string and return a ParsedIssue.
    """
    tokens = _tokenize(issue_text)
    parsed = ParsedIssue(
        raw_text=issue_text,
        component=_detect_component(tokens),
        issue_type=_detect_type(tokens),
        keywords=_extract_keywords(tokens),
    )
    return parsed


def print_parsed_issue(parsed: ParsedIssue) -> None:
    print("\n── Issue Analysis ────────────────────────────────")
    print(f"  Input     : {parsed.raw_text}")
    print(f"  Component : {parsed.component}")
    print(f"  Type      : {parsed.issue_type}")
    print(f"  Keywords  : {', '.join(parsed.keywords)}")
    print("──────────────────────────────────────────────────\n")


if __name__ == "__main__":
    import sys
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Fix login crash when password empty"
    print_parsed_issue(interpret_issue(text))
