"""Unit tests for the pulse_worktree_resolver CLI per slice-077 AC#5 +
design.md § Cross-spec parity.

Tests --detect + --classify modes with --json output. Use subprocess to
invoke `python -m tools.pulse_worktree_resolver` from a synthetic git repo.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    _git("init", "-b", "master", str(repo_root), cwd=repo_root.parent)
    _git("config", "user.name", "test", cwd=repo_root)
    _git("config", "user.email", "test@example.com", cwd=repo_root)
    (repo_root / "README.md").write_text("init\n", encoding="utf-8")
    _git("add", "README.md", cwd=repo_root)
    _git("commit", "-m", "initial", cwd=repo_root)


def _run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Invoke `python -m tools.pulse_worktree_resolver` with given args."""
    return subprocess.run(
        [sys.executable, "-m", "tools.pulse_worktree_resolver", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_detect_json_emits_parseable_worktree_list(tmp_path: Path):
    """`--detect --json --repo-root <root>` emits parseable JSON with action='detect'
    + 'worktrees' key (list)."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    proc = _run_cli("--detect", "--json", "--repo-root", str(repo_root), cwd=repo_root)
    assert proc.returncode == 0, f"exit {proc.returncode}; stderr={proc.stderr!r}"
    data = json.loads(proc.stdout)
    assert data["action"] == "detect"
    assert "worktrees" in data
    assert isinstance(data["worktrees"], list)


def test_cli_classify_json_returns_state_for_given_slice(tmp_path: Path):
    """`--classify slice-077-test --json --repo-root <root>` emits parseable
    JSON with action='classify' + 'classification' key."""
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    # Create the slice worktree first so --classify has a target
    wt_path = tmp_path / "repo-wt" / "slice-077-test"
    _git("worktree", "add", str(wt_path), "-b", "slice/077-test", "master", cwd=repo_root)
    proc = _run_cli(
        "--classify", "slice-077-test", "--json", "--repo-root", str(repo_root), cwd=repo_root
    )
    # exit may be 0 or 1 depending on the classification (UNKNOWN → 1 by contract);
    # the test asserts the JSON shape, not the exit code
    assert proc.stdout, f"empty stdout; stderr={proc.stderr!r}"
    # JSON may be on stdout (success) or stderr (error). Try stdout first.
    if proc.returncode == 0:
        data = json.loads(proc.stdout)
        assert data["action"] == "classify"
        assert "classification" in data
        assert data["classification"]["state"] in {
            "IN_PROGRESS", "BUILT_BUT_NOT_MERGED", "MERGED", "UNKNOWN",
        }
    else:
        # UNKNOWN exit-1 path — stderr JSON
        err_data = json.loads(proc.stderr.strip().splitlines()[0])
        assert err_data["action"] == "classify"
