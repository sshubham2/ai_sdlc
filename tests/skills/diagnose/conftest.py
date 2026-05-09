"""Shared fixtures for /diagnose skill tests.

Skills are not Python packages (no __init__.py inside skills/) — they're
script directories invoked via `python skills/<name>/<script>.py`. To
import them in tests, we insert skills/diagnose/ into sys.path so
`from assemble import ...` and `import write_pass` resolve.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = REPO_ROOT / "skills" / "diagnose"

if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))
