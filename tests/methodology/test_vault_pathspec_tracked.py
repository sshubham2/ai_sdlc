"""slice-098 / [[ADR-089]]: tests for ``tools._vault_git.vault_pathspec_is_tracked``
— the binding RETIRE-when-untracked signal that replaces the VAULT_ROOT_IS_DEFAULT
proxy. The WIRE-1 consumer test for ``tools/_vault_git.py``.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools._vault_git import VaultGitUnavailable, vault_pathspec_is_tracked


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "slice-queue.md").write_text("queue\n", encoding="utf-8")
    _git(tmp_path, "add", "architecture/slice-queue.md")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    return tmp_path


def test_tracked_pathspec_returns_true(tmp_git_repo: Path) -> None:
    # The no-flip default: vault file is git-tracked -> True -> git-tree reads run.
    assert vault_pathspec_is_tracked(tmp_git_repo, "architecture/slice-queue.md") is True


def test_untracked_pathspec_refuses(tmp_git_repo: Path) -> None:
    # An untracked vault file (the post-flip external-store state) -> False ->
    # callers RETIRE visibly. This is the AC5 / R-7 silent-disable guard.
    (tmp_git_repo / "architecture" / "shippability.md").write_text("s\n", encoding="utf-8")
    assert vault_pathspec_is_tracked(tmp_git_repo, "architecture/shippability.md") is False
    # A path absent from the tree entirely is likewise untracked.
    assert vault_pathspec_is_tracked(tmp_git_repo, "architecture/nope.md") is False


def test_git_unavailable_raises_not_silent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Fail-VISIBLE, never a silent untracked verdict, when git can't be spawned.
    import tools._vault_git as vg

    def _boom(*_a: object, **_k: object) -> None:
        raise FileNotFoundError("git")

    monkeypatch.setattr(vg.subprocess, "run", _boom)
    with pytest.raises(VaultGitUnavailable):
        vault_pathspec_is_tracked(tmp_path, "architecture/slice-queue.md")
