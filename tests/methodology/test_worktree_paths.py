"""Tests for tools/_worktree_paths.py (slice-099 / BRANCH-3 / ADR-090).

Pins the shared single-source-of-truth helper: canonical worktree path +
slice branch name, plus that branch_workflow_audit still delegates to it
(AC5 — no drift between the audit and the skill-prose CLI).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools._worktree_paths import (
    canonical_worktree_path,
    slice_branch_name,
)


# ------------------------------------------------------------------
# canonical_worktree_path + slice_branch_name
# ------------------------------------------------------------------


def test_canonical_path_and_branch():
    """Path + branch follow the BRANCH-2 convention, unchanged by BRANCH-3."""
    main = Path("/home/u/ai_sdlc")
    folder = "slice-099-create-worktree-at-slice-pick"
    assert canonical_worktree_path(folder, main) == (
        Path("/home/u/ai_sdlc-wt/slice-099-create-worktree-at-slice-pick")
    )
    assert slice_branch_name(folder) == "slice/099-create-worktree-at-slice-pick"


def test_slice_branch_name_rejects_non_slice_name():
    """A folder name failing the strict slice-NNN-<name> shape → empty string."""
    assert slice_branch_name("not-a-slice") == ""
    assert slice_branch_name("slice-99-too-few-digits") == ""
    assert slice_branch_name("slice-099B-letter-suffix") == ""  # split-slice letter form


def test_canonical_path_uses_main_name_wt_sibling():
    """The -wt suffix attaches to the main repo dir name, as a sibling."""
    main = Path("/x/y/myrepo")
    assert canonical_worktree_path("slice-001-foo", main) == (
        Path("/x/y/myrepo-wt/slice-001-foo")
    )


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def test_cli_emits_path_then_branch():
    res = subprocess.run(
        [sys.executable, "-m", "tools._worktree_paths",
         "--slice-folder", "slice-099-create-worktree-at-slice-pick",
         "--repo-root", str(Path("/home/u/ai_sdlc"))],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert res.returncode == 0
    lines = res.stdout.strip().splitlines()
    assert lines[-2].endswith("slice-099-create-worktree-at-slice-pick")
    assert lines[-1] == "slice/099-create-worktree-at-slice-pick"


def test_cli_exit_2_on_bad_folder_name():
    res = subprocess.run(
        [sys.executable, "-m", "tools._worktree_paths", "--slice-folder", "not-a-slice"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    assert res.returncode == 2
    assert "does not match" in res.stderr


# ------------------------------------------------------------------
# branch_workflow_audit still delegates to the shared helper (AC5)
# ------------------------------------------------------------------


def test_branch_workflow_audit_delegates_to_shared_helper():
    """The audit's internal wrappers now delegate to _worktree_paths — same output."""
    from tools import branch_workflow_audit as bwa

    sf = Path("/home/u/ai_sdlc/architecture/slices/slice-042-foo-bar")
    assert bwa._slice_branch_name(sf) == "slice/042-foo-bar"
    assert bwa._resolve_expected_worktree_path(sf, Path("/home/u/ai_sdlc")) == (
        Path("/home/u/ai_sdlc-wt/slice-042-foo-bar")
    )
    # The moved regex is re-exported (slice-099 m3 — importable for back-compat).
    assert bwa._SLICE_FOLDER_RE.match("slice-042-foo-bar")
