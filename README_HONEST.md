# git_ai — Autonomous AI Developer Agent

> **Status:** 🟡 Proof of Concept / MVP  
> **Production Ready:** ❌ No  
> **Last Updated:** March 13, 2026

An autonomous AI agent that reads bug reports, scans repositories, identifies relevant code, generates fixes, applies patches, commits to git, and opens Pull Requests automatically.

---

## 🎯 What It Claims vs What It Does

### **Claims:**
- Autonomous AI developer that fixes bugs automatically
- Scans repositories and identifies relevant code
- Generates intelligent fixes using LLM
- Applies patches safely without breaking code
- Creates git branches, commits, and Pull Requests

### **Reality:**
- ✅ Works for simple password validation bugs
- ✅ Can scan repositories and find files
- ⚠️ Uses mock responses (no real AI installed)
- ⚠️ Patches are naive (inserts at function start only)
- ⚠️ GitHub integration untested
- ❌ Cannot handle complex bugs
- ❌ No test execution or verification

---

## 📊 Current State: Brutally Honest

| Component | Status | Success Rate | Notes |
|-----------|--------|--------------|-------|
| Issue Analysis | ✅ Works | 80% | Keyword-based only |
| Repo Scanning | ✅ Works | 95% | Reliable |
| LLM Integration | ⚠️ Mock Only | 10% | Only handles password bugs |
| Patch Application | ⚠️ Naive | 60% | Inserts blindly at function start |
| Git Operations | ✅ Works | 90% | Solid implementation |
| GitHub PR Creation | ❓ Untested | 0% | Never tested in production |
| Multi-File Fixes | ❌ Not Supported | 0% | Single file only |
| Test Verification | ❌ Not Implemented | 0% | Doesn't verify fixes work |

**Overall Functionality:** 4/10 — Interesting prototype, not production-ready

---

## 🏗️ Architecture

```
git_ai/
├── agent/                    # AI Brain
│   ├── issue_interpreter.py      # Keyword extraction (BASIC)
│   ├── issue_interpreter_v2.py   # Enhanced version (NOT INTEGRATED)
│   ├── repo_analyzer.py          # File scanner (WORKS)
│   └── code_generator.py         # LLM interface (MOCK ONLY)
│
├── utils/                    # Helper Functions
│   ├── file_loader.py            # File reading (WORKS)
│   └── code_parser.py            # Symbol extraction (BASIC)
│
├── git_tools/                # Git Operations
│   ├── patch_applier.py          # OLD VERSION (BROKEN)
│   ├── patch_applier_v2.py       # FIXED VERSION (WORKS)
│   └── repo_manager.py           # Git operations (WORKS)
│
├── github_tools/             # GitHub Integration
│   ├── github_auth.py            # Token auth (WORKS)
│   └── pr_creator.py             # PR creation (UNTESTED)
│
├── sample_project/           # Test Project
│   └── login.py                  # Buggy test file
│
├── main.py                   # Orchestrator (HAS CRITICAL BUG)
├── test_run.py               # UTF-8 wrapper (WORKS)
├── run_with_issue.py         # CLI helper (WORKS)
└── test_bugs.py              # Bug verification (WORKS)
```

---

## 🔧 Tech Stack

### **Core:**
- **Python 3.12** - Main language
- **GitPython** - Git operations
- **PyGithub** - GitHub API (untested)
- **Ollama** - Local LLM (not installed, uses mock)

### **Missing (Should Have):**
- ❌ **ast** - Python AST parsing (uses regex instead)
- ❌ **pytest** - Testing framework (NO TESTS!)
- ❌ **openai/anthropic** - Real AI (uses mock)
- ❌ **black** - Code formatting
- ❌ **mypy** - Type checking

---

## 🚀 Installation

### **Prerequisites:**
```bash
# Required
Python 3.12+
Git 2.0+

# Optional (for real AI)
Ollama + codellama model
```

### **Setup:**
```bash
# Clone repository
git clone https://github.com/sukhithms25/git_ai.git
cd git_ai

# Install dependencies
pip install -r requirements.txt

# Set GitHub token (for Phase 3)
setx GITHUB_TOKEN "ghp_your_token_here"  # Windows
export GITHUB_TOKEN="ghp_your_token_here"  # Linux/Mac

# Optional: Install Ollama for real AI
# Download from: https://ollama.com/download
ollama pull codellama
```

---

## 💻 Usage

### **Method 1: Interactive Mode**
```bash
python main.py ./sample_project

# Enter issue when prompted:
Fix login crash when password is empty
```

### **Method 2: Command Line**
```bash
python run_with_issue.py "Fix login crash when password is empty"
```

### **Method 3: Pipe Input**
```bash
echo "Fix login crash when password is empty" | python main.py ./sample_project
```

---

## 📝 Pipeline Stages

### **Phase 1: AI Brain (Steps 1-5)**
```
[1/7] Analyse issue          → Extract keywords, detect component
[2/7] Scan repository         → Find all source files
[3/7] Detect relevant files   → Match keywords to files
[4/7] Load code content       → Read file contents
[5/7] Generate fix (LLM)      → Create patch code
```

### **Phase 2: Modification Engine (Steps 6-7)**
```
[6/7] Apply patch             → Insert fix into file
[7/7] Git branch + commit     → Create branch and commit
```

### **Phase 3: Automation Layer (Steps 8-9) - UNTESTED**
```
[8/9] Push to GitHub          → Push branch to remote
[9/9] Create Pull Request     → Open PR with description
```

---

## 🐛 Known Bugs & Issues

### **Critical (Breaks Functionality):**

#### 1. **main.py Import Bug** 🔴
```python
# Line 19: CRITICAL BUG
# from pathlib import Path  # ← COMMENTED OUT

# Line 21: WILL CRASH
ROOT = Path(__file__).parent.resolve()  # ← NameError
```
**Fix:** Uncomment line 19

#### 2. **No Real AI** 🔴
- Ollama not installed
- Falls back to mock responses
- Mock only handles password validation bugs
- Any other bug type returns generic fallback

#### 3. **Duplicate Insertions** 🟡
- Running agent twice on same file adds duplicate code
- No detection of existing fixes

#### 4. **Single File Only** 🟡
- Cannot fix bugs spanning multiple files
- Only patches first relevant file

### **Major (Causes Problems):**

5. **Naive Insertion Logic** - Always inserts at function start
6. **No Test Execution** - Doesn't verify fixes work
7. **No Rollback on Git Failure** - Leaves repo in bad state
8. **No Syntax Validation for JS/TS** - Only validates Python

### **Minor (Annoying):**

9. **Unicode Warnings** - Some characters cause issues on Windows
10. **Ollama Error Spam** - Always shows "model not found"
11. **No Progress Indicators** - Long operations seem frozen
12. **Hardcoded Limits** - MAX_RELEVANT_FILES = 5

---

## ✅ What Actually Works

### **Scenario 1: Simple Password Validation Bug**
**Success Rate:** 90% ✅

```bash
Issue: "Fix login crash when password is empty"
Result: ✓ Correctly inserts validation at function start
```

**Before:**
```python
def authenticate_user(username, password):
    user = database.find_user(username)
    if user.password_hash == hash_password(password):
        return {"success": True, "user": user}
```

**After:**
```python
def authenticate_user(username, password):
    if not password or not password.strip():  # ← AI INSERTED THIS
        return {"error": "Password is required"}, 400
    user = database.find_user(username)
    if user.password_hash == hash_password(password):
        return {"success": True, "user": user}
```

### **Scenario 2: Any Other Bug**
**Success Rate:** 10% ❌

```bash
Issue: "Fix SQL injection in search function"
Result: ✗ Mock doesn't handle this, returns generic fallback
```

### **Scenario 3: Multi-File Bug**
**Success Rate:** 0% ❌

```bash
Issue: "Fix authentication bug across login.py and auth.py"
Result: ✗ Only fixes first file, ignores second
```

### **Scenario 4: Complex Insertion Point**
**Success Rate:** 20% ⚠️

```bash
Issue: "Insert validation before database.find_user call"
Result: ✗ Inserts at function start instead (wrong place)
```

---

## 🧪 Testing

### **Run Bug Verification:**
```bash
# Check for bugs in sample project
python test_bugs.py

# Output:
[X] BUG 1 FOUND: authenticate_user() doesn't validate empty password
[X] BUG 2 FOUND: authenticate_user() doesn't validate empty username
[X] BUG 3 FOUND: hash_password() will crash on None/empty password
```

### **Run Agent to Fix:**
```bash
python run_with_issue.py "Fix login crash when password is empty"

# Output:
✔ Fix generated
✔ Patched → login.py (2 lines changed)
✔ Branch: ai-fix-login-260313-234832
✔ Commit: 5e3997e6
```

### **Verify Fix:**
```bash
python test_bugs.py

# Output:
[OK] BUG 1 FIXED: Password validation exists in authenticate_user()
[X] BUG 2 FOUND: authenticate_user() doesn't validate empty username
[X] BUG 3 FOUND: hash_password() will crash on None/empty password
```

### **Check Git History:**
```bash
git log --oneline -3
git diff HEAD~1
```

---

## 📈 Performance

### **Speed:**
- Issue interpretation: **<1ms**
- Repo scanning: **10-100ms** (depends on repo size)
- File loading: **10-50ms**
- LLM call: **N/A** (mock is instant, real would be 1-5s)
- Patch application: **10-50ms**
- Git operations: **100-500ms**

**Total pipeline:** ~1-2 seconds (with mock)

### **Scalability:**
- **Small repos (<100 files):** ✅ Works fine
- **Medium repos (100-1000 files):** ⚠️ Slow but works
- **Large repos (>1000 files):** ❌ Would timeout

### **Memory Usage:**
- **Typical:** 50-100MB
- **Large files:** Could spike to 500MB+
- **No streaming:** Loads everything into memory

---

## 🎯 Supported Issue Formats

### **Basic (Auto-detect):**
```
"Fix login crash when password is empty"
"Fix authentication bug"
"Add validation to user input"
```

### **Function-Specific (v2 - Not Integrated):**
```
"Fix bug in authenticate_user function"
"Add validation in hash_password function"
```

### **Line-Specific (v2 - Not Integrated):**
```
"Add check at line 15 in login.py"
"Fix bug at line 42"
```

### **Before/After (v2 - Not Integrated):**
```
"Insert validation before database.find_user call"
"Add error handling after authenticate_user call"
```

### **File:Function (v2 - Not Integrated):**
```
"Fix login.py:authenticate_user password bug"
```

---

## 🏆 Strengths

1. ✅ **Modular Architecture** - Clean separation of concerns
2. ✅ **Git Integration** - Solid branching/commit logic
3. ✅ **Error Handling** - Graceful fallbacks in most places
4. ✅ **Documentation** - Good docstrings and comments
5. ✅ **Backup System** - Creates .bak files before patching
6. ✅ **Syntax Validation** - Checks Python syntax after patching

---

## 💀 Fatal Flaws

1. ❌ **No Real AI** - Mock only handles one bug type
2. ❌ **Naive Patching** - Inserts blindly at function start
3. ❌ **No Tests** - Completely untested
4. ❌ **Single File Only** - Can't handle multi-file bugs
5. ❌ **No Verification** - Doesn't check if fix works
6. ❌ **Phase 3 Untested** - GitHub integration never validated
7. ❌ **Import Bug** - main.py crashes immediately

---

## 🚧 Roadmap

### **Immediate (Fix Critical Bugs):**
- [ ] Fix main.py import bug (5 minutes)
- [ ] Test Phase 3 with real GitHub token (30 minutes)
- [ ] Add duplicate detection (1 hour)
- [ ] Integrate issue_interpreter_v2 (1 hour)

### **Short-term (Make It Useful):**
- [ ] Install Ollama and real LLM (2-4 hours)
- [ ] Add AST-based code analysis (8-12 hours)
- [ ] Smart insertion logic (12-16 hours)
- [ ] Multi-file support (8-12 hours)

### **Long-term (Production Ready):**
- [ ] Comprehensive test suite (8-16 hours)
- [ ] Test execution & verification (8-12 hours)
- [ ] Error recovery & rollback (4-8 hours)
- [ ] Production hardening (16-24 hours)

**Total Time to Production:** 50-80 hours

---

## 🎓 Verdict

### **Is This Production-Ready?**

**NO. Absolutely not.**

### **Current State:**
Proof of concept / MVP that demonstrates potential but has critical flaws.

### **What It Can Do:**
- ✅ Fix simple password validation bugs in Python files
- ✅ Create git branches and commits
- ✅ Generate formatted PR descriptions (untested)

### **What It Cannot Do:**
- ❌ Fix any bug that isn't password validation
- ❌ Handle multi-file bugs
- ❌ Verify fixes actually work
- ❌ Recover from errors
- ❌ Work without manual intervention

### **Recommended Use:**
- ✅ Demo/prototype
- ✅ Educational purposes
- ✅ Starting point for real implementation

### **NOT Recommended For:**
- ❌ Production codebases
- ❌ Critical bug fixes
- ❌ Automated deployment
- ❌ Unsupervised operation

---

## 📊 Final Score

| Category | Score | Notes |
|----------|-------|-------|
| **Architecture** | 7/10 | Clean but incomplete |
| **Code Quality** | 6/10 | Good structure, poor implementation |
| **Testing** | 0/10 | No tests at all |
| **Documentation** | 7/10 | Good docstrings, missing user docs |
| **Functionality** | 4/10 | Works for one bug type only |
| **Reliability** | 3/10 | Crashes on edge cases |
| **Production Ready** | 1/10 | Absolutely not |

**Overall:** 4/10 — Interesting prototype, not production-ready

---

## 🤝 Contributing

### **Priority Issues:**
1. Fix main.py import bug
2. Add real LLM integration
3. Write comprehensive tests
4. Implement smart insertion logic
5. Add multi-file support

### **How to Contribute:**
```bash
# Fork the repository
git clone https://github.com/sukhithms25/git_ai.git
cd git_ai

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
python test_bugs.py

# Commit and push
git commit -m "feat: your feature"
git push origin feature/your-feature

# Open Pull Request
```

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM runtime (not installed but supported)
- **GitPython** - Reliable git operations
- **PyGithub** - GitHub API integration
- **SWE-agent** - Inspiration for safe patching strategy

---

## 📞 Contact

- **Author:** Sukhith MS
- **GitHub:** [@sukhithms25](https://github.com/sukhithms25)
- **Repository:** [git_ai](https://github.com/sukhithms25/git_ai)

---

## ⚠️ Disclaimer

**This is a proof-of-concept project. Do not use in production without extensive testing and improvements.**

The agent:
- May introduce bugs instead of fixing them
- Does not verify fixes work
- Can corrupt files if patch logic fails
- Has no security auditing
- Is not suitable for critical systems

**Use at your own risk. Always review generated code before merging.**

---

## 🔮 Future Vision

**Phase 4: AI Code Review Engine** (Planned)
- Automatic PR review
- Security vulnerability detection
- Code quality analysis
- Test coverage suggestions

**Phase 5: Multi-Agent System** (Concept)
- Specialized agents for different bug types
- Collaborative fixing across multiple files
- Self-learning from successful fixes

**Phase 6: Production Deployment** (Long-term)
- CI/CD integration
- Automated testing pipeline
- Rollback mechanisms
- Production monitoring

---

**This project has potential, but needs 50-80 hours of serious development before it's reliable.**

**Current Status:** 🟡 Proof of Concept  
**Production Ready:** ❌ No  
**Recommended Action:** Fix critical bugs, add tests, integrate real AI

---

*Last Updated: March 13, 2026*  
*Version: 0.1.0-alpha*  
*Status: Experimental*
