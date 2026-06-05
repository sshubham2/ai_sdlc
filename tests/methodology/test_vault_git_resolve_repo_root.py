"""Pins ``tools._vault_git.resolve_repo_root_for_slice`` (slice-115 / [[ADR-107]]).

The 3 slice-folder-path audits (branch_workflow / drift_check /
critique_review_prerequisite) resolve their repo root through this helper. Post-flip
the live slice folder lives in the EXTERNAL vault store (no ``.git`` above it), so
the resolver falls back to the cwd repo (the worktree). Pre-flip / tmp-fixture slice
folders with their own ``.git`` resolve via the walk; a NON-external path with no
``.git`` ancestor stays a usage-error (None) — the regression that re-broke the 3
audits at slice-115's Step-6 gate would surface here.
"""
from __future__ import annotations

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
from tools import _vault_git


def test_walk_resolves_tmp_slice_with_git(tmp_path):
    """In-repo / tmp-fixture slice folder with a ``.git`` ancestor resolves via the
    walk (unchanged pre-flip behaviour)."""
    repo = tmp_path / "r"
    (repo / ".git").mkdir(parents=True)
    sd = repo / "architecture" / "slices" / "slice-999-x"
    sd.mkdir(parents=True)
    assert _vault_git.resolve_repo_root_for_slice(sd) == repo


def test_non_external_no_git_returns_none(tmp_path):
    """A non-external path with no ``.git`` ancestor stays a usage-error (None) —
    NO cwd fallback, so the tmp-fixture 'no .git' usage-error tests are preserved."""
    other_ext = tmp_path / "other-ext-store"
    other_ext.mkdir()
    sd = tmp_path / "nowhere" / "slice-999-x"
    sd.mkdir(parents=True)
    # Pin VAULT_ROOT to an absolute store that `sd` is NOT under → not external.
    with vi.pin_vault_root(other_ext, "tools._vault_paths", "tools._vault_git"):
        assert _vault_git.resolve_repo_root_for_slice(sd) is None


def test_external_slice_falls_back_to_cwd_repo(tmp_path, monkeypatch):
    """Post-flip ([[ADR-107]]): a slice folder under the external VAULT_ROOT (no
    ``.git`` above it) resolves the repo from cwd (the worktree), NOT a usage-error.
    This is the branch the 3 Step-6 audits broke on before the slice-115 fix."""
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    ext = tmp_path / "ext-aisdlc-store"
    sd = ext / "slices" / "slice-999-x"
    sd.mkdir(parents=True)
    monkeypatch.chdir(repo)
    with vi.pin_vault_root(ext, "tools._vault_paths", "tools._vault_git"):
        assert _vault_git.resolve_repo_root_for_slice(sd) == repo.resolve()
