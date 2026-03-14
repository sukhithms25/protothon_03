# User Guide: How to Specify Where to Fix Code

## Overview
The git_ai agent can understand location-specific instructions. You can tell it exactly where to apply the fix!

---

## 📍 Supported Location Formats

### 1. **By Function Name**
Tell the agent which function to fix:

```bash
python main.py ./sample_project
# Then enter:
"Fix the password validation bug in authenticate_user function"
```

**What it does:** Inserts the fix at the start of the `authenticate_user` function.

---

### 2. **By Line Number**
Specify an exact line number:

```bash
"Add password check at line 15 in login.py"
```

**What it does:** Inserts the fix at line 15.

---

### 3. **Before/After a Specific Call**
Insert code before or after a specific statement:

```bash
"Insert password validation before database.find_user call"
```

**What it does:** Finds `database.find_user` and inserts the fix right before it.

```bash
"Add error handling after authenticate_user call"
```

**What it does:** Inserts code right after the `authenticate_user` call.

---

### 4. **File:Function Format**
Specify both file and function:

```bash
"Fix login.py:authenticate_user password bug"
```

**What it does:** Targets the `authenticate_user` function in `login.py`.

---

### 5. **General (Auto-detect)**
Let the AI figure it out:

```bash
"Fix login crash when password is empty"
```

**What it does:** Uses keywords to find the most relevant location automatically.

---

## 🎯 Examples

### Example 1: Function-Specific Fix
```
Issue: "Fix null pointer bug in hash_password function"

Result:
✓ Targets: hash_password function
✓ Inserts: Null check at function start
```

### Example 2: Line-Specific Fix
```
Issue: "Add validation at line 32 in login.py"

Result:
✓ Targets: login.py, line 32
✓ Inserts: Validation code at that exact line
```

### Example 3: Before/After Fix
```
Issue: "Insert authentication check before user.save call"

Result:
✓ Finds: user.save() in the code
✓ Inserts: Auth check right before it
```

### Example 4: Multi-Location Fix
```
Issue: "Fix password validation in authenticate_user and login_endpoint functions"

Result:
✓ Targets: Both functions
✓ Inserts: Validation in both places
```

---

## 💡 Tips for Best Results

### ✅ DO:
- Be specific: "Fix in authenticate_user function"
- Use actual function/variable names from your code
- Mention the file name if you have multiple files
- Use "before" or "after" for precise insertion

### ❌ DON'T:
- Be too vague: "Fix the bug somewhere"
- Use incorrect function names
- Forget to mention the component (login, payment, etc.)

---

## 🔧 Advanced Usage

### Combining Multiple Hints
```
"Fix password validation bug in login.py:authenticate_user before database.find_user call"
```

This gives the agent:
- File: login.py
- Function: authenticate_user
- Insertion point: before database.find_user
- Context: password validation

The agent will use ALL this information to place the fix perfectly!

---

## 📊 How the Agent Decides

1. **Explicit location** (line number, function name) → Uses that
2. **Before/After reference** → Finds the reference and inserts there
3. **Keywords only** → Scans code for keyword matches
4. **Fallback** → Inserts at the most logical place (function start)

---

## 🚀 Quick Reference

| What You Want | How to Say It |
|---------------|---------------|
| Fix a specific function | "Fix in `function_name` function" |
| Fix at a line | "Fix at line `N`" |
| Insert before something | "Insert before `code_reference`" |
| Insert after something | "Insert after `code_reference`" |
| Fix in a file | "Fix in `filename.py`" |
| Fix file + function | "Fix `file.py:function_name`" |

---

## 🎬 Try It Now!

```bash
cd e:\protothon\git_ai

# Test with specific location
python main.py ./sample_project
# Enter: "Add password validation in authenticate_user function before database.find_user"

# Or use the command line
echo "Fix login.py:authenticate_user password bug" | python main.py ./sample_project
```

---

## 🔮 Coming Soon

- [ ] Class-level fixes: "Fix in User class"
- [ ] Multi-file fixes: "Fix in login.py and auth.py"
- [ ] Conditional fixes: "Fix only if password is None"
- [ ] Interactive mode: Agent asks "Where should I apply this fix?"

---

**Your AI agent is smart enough to understand natural language location hints!** 🎯
