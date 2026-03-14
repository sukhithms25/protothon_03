import sys
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Now run the main script
os.chdir(r'e:\protothon\git_ai')
sys.path.insert(0, r'e:\protothon\git_ai')

from main import run

issue = "Fix login crash when password is empty or None"
repo = "./sample_project"

run(issue, repo)
