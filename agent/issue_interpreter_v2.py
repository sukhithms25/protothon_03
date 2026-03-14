"""
issue_interpreter_v2.py

Enhanced version that understands location-specific fix requests.

Supports formats like:
- "Fix login crash in authenticate_user function"
- "Add validation at line 15 in login.py"
- "Fix password bug in login.py:authenticate_user"
- "Insert check before database.find_user call"
"""

import re
from dataclasses import dataclass, field

# ── Heuristic keyword maps ────────────────────────────────────────────────────

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
                   "allow", "enable", "insert"}
REFACTOR_SIGNALS = {"refactor", "clean", "improve", "optimise", "optimize",
                    "restructure", "rename"}

# Location indicators
LOCATION_PATTERNS = {
    "function": re.compile(r"in\s+(\w+)\s+function", re.IGNORECASE),
    "method": re.compile(r"in\s+(\w+)\s+method", re.IGNORECASE),
    "class": re.compile(r"in\s+(\w+)\s+class", re.IGNORECASE),
    "line": re.compile(r"at\s+line\s+(\d+)", re.IGNORECASE),
    "before": re.compile(r"before\s+(\w+(?:\.\w+)*)", re.IGNORECASE),
    "after": re.compile(r"after\s+(\w+(?:\.\w+)*)", re.IGNORECASE),
    "file_function": re.compile(r"(\w+\.py):(\w+)", re.IGNORECASE),
}


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class ParsedIssue:
    raw_text:  str
    component: str               = "unknown"
    issue_type: str              = "unknown"
    keywords:  list[str]        = field(default_factory=list)
    
    # New location-specific fields
    target_file: str            = ""           # e.g., "login.py"
    target_function: str        = ""           # e.g., "authenticate_user"
    target_line: int            = 0            # e.g., 15
    insertion_point: str        = ""           # "before", "after", "start", "end"
    insertion_reference: str    = ""           # e.g., "database.find_user"


# ── Core logic ────────────────────────────────────────────────────────────────

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


def _extract_location_info(text: str) -> dict:
    """
    Extract location-specific information from the issue text.
    
    Examples:
    - "Fix bug in authenticate_user function" → function: "authenticate_user"
    - "Add check at line 15" → line: 15
    - "Insert validation before database.find_user" → before: "database.find_user"
    - "Fix login.py:authenticate_user" → file: "login.py", function: "authenticate_user"
    """
    location = {
        "target_file": "",
        "target_function": "",
        "target_line": 0,
        "insertion_point": "",
        "insertion_reference": "",
    }
    
    # Check for file:function pattern
    match = LOCATION_PATTERNS["file_function"].search(text)
    if match:
        location["target_file"] = match.group(1)
        location["target_function"] = match.group(2)
    
    # Check for function/method/class mentions
    for pattern_type in ["function", "method", "class"]:
        match = LOCATION_PATTERNS[pattern_type].search(text)
        if match:
            location["target_function"] = match.group(1)
            break
    
    # Check for line number
    match = LOCATION_PATTERNS["line"].search(text)
    if match:
        location["target_line"] = int(match.group(1))
    
    # Check for before/after references
    match = LOCATION_PATTERNS["before"].search(text)
    if match:
        location["insertion_point"] = "before"
        location["insertion_reference"] = match.group(1)
    
    match = LOCATION_PATTERNS["after"].search(text)
    if match:
        location["insertion_point"] = "after"
        location["insertion_reference"] = match.group(1)
    
    return location


def interpret_issue(issue_text: str) -> ParsedIssue:
    """
    Main entry point. Parse a free-form issue string and return a ParsedIssue.
    Now with location-specific parsing!
    """
    tokens = _tokenize(issue_text)
    location_info = _extract_location_info(issue_text)
    
    parsed = ParsedIssue(
        raw_text=issue_text,
        component=_detect_component(tokens),
        issue_type=_detect_type(tokens),
        keywords=_extract_keywords(tokens),
        **location_info
    )
    return parsed


def print_parsed_issue(parsed: ParsedIssue) -> None:
    print("\n-- Issue Analysis --------------------------------------------")
    print(f"  Input     : {parsed.raw_text}")
    print(f"  Component : {parsed.component}")
    print(f"  Type      : {parsed.issue_type}")
    print(f"  Keywords  : {', '.join(parsed.keywords)}")
    
    # Print location info if specified
    if parsed.target_file:
        print(f"  Target File    : {parsed.target_file}")
    if parsed.target_function:
        print(f"  Target Function: {parsed.target_function}")
    if parsed.target_line:
        print(f"  Target Line    : {parsed.target_line}")
    if parsed.insertion_point:
        print(f"  Insert {parsed.insertion_point}: {parsed.insertion_reference}")
    
    print("--------------------------------------------------------------\n")


if __name__ == "__main__":
    import sys
    
    # Test cases
    test_cases = [
        "Fix login crash when password empty",
        "Fix bug in authenticate_user function",
        "Add validation at line 15 in login.py",
        "Insert password check before database.find_user call",
        "Fix login.py:authenticate_user password validation",
    ]
    
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else test_cases[0]
    
    if text == "test":
        for test in test_cases:
            print(f"\nTesting: {test}")
            print_parsed_issue(interpret_issue(test))
    else:
        print_parsed_issue(interpret_issue(text))
