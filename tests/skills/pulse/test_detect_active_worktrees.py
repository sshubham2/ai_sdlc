"""Unit tests for detect_active_worktrees per slice-077 AC#5 + design.md
§ Fail-closed paths (Detection-side).

Tests use synthetic git repos via tmp_path + subprocess('git worktree add').
The function returns empty list (never raises) when no slice/* worktrees
exist; filters non-slice branches + no-suffix branches + prunable + missing-
on-disk silently per design.md.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.pulse_worktree_resolver import WorktreeInfo, detect_active_worktrees


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo_root: Path) -> None:
    """Initialize a git repo at `repo_root` on master with one commit."""
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)


def test_detect_returns_empty_list_when_only_main_worktree_present(tmp_path: Path):
    """A bare repo with only the main worktree → empty list (no slice/* registered)."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    worktrees = detect_active_worktrees(repo_root)
    assert worktrees == [], f"expected empty list; got {worktrees!r}"


def test_detect_returns_worktree_info_for_slice_branch_worktree(tmp_path: Path):
    """A repo with a slice/077-test worktree on the canonical BRANCH-2 sibling
    path → list with one WorktreeInfo entry for it."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    # Create slice worktree at canonical BRANCH-2 path: <parent>/<name>-wt/slice-077-test
    wt_path = tmp_path / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt_path), "-b", "slice/077-test", "master", cwd=repo_root)
    worktrees = detect_active_worktrees(repo_root)
    assert len(worktrees) == 1, f"expected 1 worktree; got {len(worktrees)}: {worktrees!r}"
    wt = worktrees[0]
    assert isinstance(wt, WorktreeInfo)
    assert wt.branch == "slice/077-test", f"branch={wt.branch!r}"
    assert wt.slice_num == "077", f"slice_num={wt.slice_num!r}"
    assert wt.slice_name == "test", f"slice_name={wt.slice_name!r}"
    assert wt.head_sha, "head_sha must be non-empty"
    # path normalized to forward-slash per design
    assert "/" in wt.path or "\\" in wt.path, f"path looks malformed: {wt.path!r}"
