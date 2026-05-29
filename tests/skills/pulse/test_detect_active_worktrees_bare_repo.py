"""Pin slice-079 Fix L (slice-077 m6): bare-repo edge case for detect_active_worktrees.

Slice-077 m6: `_parse_worktree_porcelain` assumed `blocks[0]` is always the main worktree.
Bare-repo case (no `worktree <path>` first-line; `bare` field present) was unhandled.
Fix L detects bare via `"bare" in block[0]` AND-only per slice-077 m6 original prescription
+ /critique m2 ACCEPTED-FIXED (tightened from OR-logic in pre-fix draft).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.pulse_worktree_resolver import detect_active_worktrees


def _run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@pytest.fixture()
def bare_repo(tmp_path: Path) -> Path:
    """Create a bare git repo at tmp_path/bare and return the path."""
    bare = tmp_path / "bare.git"
    bare.mkdir()
    _run_git(["init", "--bare"], cwd=bare)
    return bare


def test_bare_repo_returns_empty_tuple_without_crashing(
    bare_repo: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    """Fix L: detect_active_worktrees on a bare-repo returns empty + emits stderr WARN.

    Pre-fix: blocks[0] missing `worktree <path>` key causes KeyError or mis-classification.
    Post-fix: bare-repo first-block detected via `"bare" in block[0]`; returns tuple() + WARN.
    """
    result = detect_active_worktrees(bare_repo)
    # Container-agnostic empty check (code-review m2): the function is annotated
    # `-> list[WorktreeInfo]` and returns `[]` for the bare-repo case; assert on
    # emptiness, not on the concrete container type.
    assert list(result) == [], (
        f"Fix L regression: detect_active_worktrees on bare-repo returned non-empty result {result!r}; "
        f"bare-repo has no checked-out tree so no active-worktree should be classified"
    )
    _, stderr = capfd.readouterr()
    assert "bare" in stderr.lower(), (
        "Fix L regression: bare-repo detection silent — no WARN emitted to stderr naming the bare-repo "
        "edge case"
    )
