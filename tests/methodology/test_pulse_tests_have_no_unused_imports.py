"""Pin slice-079 Fix I+J (slice-077 m3+m4): unused-imports AST walker for pulse test corpus.

Slice-077 m3: unused `import pytest` in tests/skills/pulse/test_classify_worktree_state.py + test_detect_active_worktrees.py.
Slice-077 m4: unused `WorktreeStateClassification` in test_classify_worktree_state.py import tuple.

Fix I+J drops the unused imports. This structural-pin guards against silent re-introduction.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PULSE_TEST_DIR = REPO_ROOT / "tests" / "skills" / "pulse"


def _collect_imported_names(tree: ast.AST) -> dict[str, int]:
    """Return {imported_name: lineno} for top-level Import / ImportFrom nodes."""
    out: dict[str, int] = {}
    for node in tree.body if isinstance(tree, ast.Module) else []:
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                out[local] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                local = alias.asname or alias.name
                out[local] = node.lineno
    return out


def _collect_used_names(tree: ast.AST) -> set[str]:
    """All ast.Name and ast.Attribute root identifiers referenced in the module."""
    used: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            cur: ast.AST = node
            while isinstance(cur, ast.Attribute):
                cur = cur.value
            if isinstance(cur, ast.Name):
                used.add(cur.id)
    return used


def _unused_imports(source: str) -> list[tuple[str, int]]:
    tree = ast.parse(source)
    imported = _collect_imported_names(tree)
    used = _collect_used_names(tree)
    return [(name, lineno) for name, lineno in imported.items() if name not in used]


def test_pulse_test_corpus_has_no_unused_imports() -> None:
    """Fix I+J: every tests/skills/pulse/test_*.py module has all imports consumed."""
    offenders: dict[str, list[tuple[str, int]]] = {}
    for py in PULSE_TEST_DIR.glob("test_*.py"):
        source = py.read_text(encoding="utf-8")
        unused = _unused_imports(source)
        if unused:
            offenders[py.name] = unused
    assert offenders == {}, (
        f"Fix I+J regression: unused imports detected in pulse test corpus: {offenders}. "
        f"(Slice-077 m3 + m4 surfaced unused `pytest` + `WorktreeStateClassification`; "
        f"silent re-introduction defeats Fix I+J.)"
    )
