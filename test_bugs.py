"""
test_bugs.py

This script demonstrates the bugs in login.py and verifies if they're fixed.
"""

import sys
from pathlib import Path

print("=" * 70)
print("  BUG VERIFICATION TEST")
print("=" * 70)

# Read the current login.py
login_file = Path("sample_project/login.py")
content = login_file.read_text()

print("\n[1] Checking for known bugs in login.py...\n")

bugs_found = []

# Bug 1: No password validation in authenticate_user
if "def authenticate_user" in content:
    func_start = content.find("def authenticate_user")
    func_section = content[func_start:func_start+500]
    
    if "if not password" not in func_section and "password is None" not in func_section:
        bugs_found.append("BUG 1: No password validation in authenticate_user()")
        print("  [X] BUG 1 FOUND: authenticate_user() doesn't validate empty password")
    else:
        print("  [OK] BUG 1 FIXED: Password validation exists in authenticate_user()")

# Bug 2: No username validation
if "def authenticate_user" in content:
    func_start = content.find("def authenticate_user")
    func_section = content[func_start:func_start+500]
    
    if "if not username" not in func_section and "username is None" not in func_section:
        bugs_found.append("BUG 2: No username validation in authenticate_user()")
        print("  [X] BUG 2 FOUND: authenticate_user() doesn't validate empty username")
    else:
        print("  [OK] BUG 2 FIXED: Username validation exists")

# Bug 3: No null check in hash_password
if "def hash_password" in content:
    func_start = content.find("def hash_password")
    func_section = content[func_start:func_start+300]
    
    if "if not password" not in func_section and "password is None" not in func_section:
        bugs_found.append("BUG 3: No null check in hash_password()")
        print("  [X] BUG 3 FOUND: hash_password() will crash on None/empty password")
    else:
        print("  [OK] BUG 3 FIXED: Null check exists in hash_password()")

# Bug 4: No request validation in login_endpoint
if "def login_endpoint" in content:
    func_start = content.find("def login_endpoint")
    func_section = content[func_start:func_start+400]
    
    if "request.json is None" not in func_section and "if not request.json" not in func_section:
        bugs_found.append("BUG 4: No request.json validation in login_endpoint()")
        print("  [X] BUG 4 FOUND: login_endpoint() doesn't validate request.json")
    else:
        print("  [OK] BUG 4 FIXED: Request validation exists")

# Bug 5: No user null check in reset_password
if "def reset_password" in content:
    func_start = content.find("def reset_password")
    func_section = content[func_start:func_start+400]
    
    if "if not user" not in func_section and "user is None" not in func_section:
        bugs_found.append("BUG 5: No user null check in reset_password()")
        print("  [X] BUG 5 FOUND: reset_password() doesn't check if user exists")
    else:
        print("  [OK] BUG 5 FIXED: User null check exists")

print("\n" + "=" * 70)
print(f"  SUMMARY: {len(bugs_found)} bug(s) found")
print("=" * 70)

if bugs_found:
    print("\nBugs that need fixing:")
    for i, bug in enumerate(bugs_found, 1):
        print(f"  {i}. {bug}")
    print("\n[!] Run the AI agent to fix these bugs!")
    print("    Command: python run_with_issue.py \"Fix login crash when password is empty\"")
    sys.exit(1)
else:
    print("\n[SUCCESS] All bugs have been fixed! ✓")
    sys.exit(0)
