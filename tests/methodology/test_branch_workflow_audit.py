"""Unit tests for tools/branch_workflow_audit.py (BRANCH-1).

Per slice-021 AC #4: BRANCH-1 audit refuses when:
- current branch is the resolved default branch (master/main/trunk/etc.)
- OR current branch is `slice/<wrong-number>-<slice-name>` (mismatch with active slice)

Unless build-log.md Events contains a canonical `BRANCH=skip` escape-hatch line
matching the regex `^- \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2} DEVIATION: BRANCH=skip\\b.+rationale: .+`.

Default-branch resolution per /critique M1 ACCEPTED-PENDING:
1. `git symbolic-ref refs/remotes/origin/HEAD` → strip `refs/remotes/origin/` prefix
2. Fallback: `git config init.defaultBranch`
3. STOP if neither resolves.

Tests use temp git repos (via subprocess) as fixtures to exercise real `git` plumbing.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tools import branch_workflow_audit as bwa


# --- Helpers ---


def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run git in a temp repo; raise on non-zero exit by default."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _init_repo_on_default_branch(tmp_path: Path, default: str = "master") -> Path:
    """Create a temp git repo on the named default branch with one commit + origin/HEAD."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "-b", default)
    _run_git(repo, "config", "user.email", "test@test.test")
    _run_git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("test\n")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "init")
    # Simulate a remote origin pointing at this repo's default branch for
    # `git symbolic-ref refs/remotes/origin/HEAD` resolution.
    _run_git(repo, "remote", "add", "origin", str(repo))
    _run_git(repo, "fetch", "origin", check=False)
    _run_git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", f"refs/remotes/origin/{default}", check=False)
    return repo


def _make_slice_folder(repo: Path, slice_number: int, slice_name: str) -> Path:
    """Create an active-slice folder at architecture/slices/slice-NNN-<name>/."""
    slice_folder = repo / "architecture" / "slices" / f"slice-{slice_number:03d}-{slice_name}"
    slice_folder.mkdir(parents=True)
    (slice_folder / "mission-brief.md").write_text("# Slice fixture\n")
    return slice_folder


# --- Tests ---


def test_branch_workflow_audit_refuses_on_default_branch(tmp_path: Path) -> None:
    """Audit exits non-zero when current branch is the resolved default branch
    and no `BRANCH=skip` escape-hatch is documented."""
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    # HEAD is on `master` (the default branch); slice folder is slice-021.
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert result.violations, "Expected violations when on default branch with no escape-hatch"
    assert any(v.kind == "on-default-branch" for v in result.violations), (
        f"Expected `on-default-branch` violation; got: {[v.kind for v in result.violations]}"
    )


def test_branch_workflow_audit_accepts_slice_branch_matching_active_slice(tmp_path: Path) -> None:
    """Audit exits clean when current branch is `slice/NNN-<name>` matching active slice."""
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    _run_git(repo, "checkout", "-b", "slice/021-test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert not result.violations, (
        f"Expected clean audit on matching slice branch; got: {result.violations}"
    )


def test_branch_workflow_audit_refuses_slice_branch_with_wrong_number(tmp_path: Path) -> None:
    """Audit refuses when current slice/NNN-... branch doesn't match active slice number."""
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    _run_git(repo, "checkout", "-b", "slice/099-some-other-slice")
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert result.violations, "Expected violations when on wrong slice branch"
    assert any(v.kind == "slice-branch-mismatch" for v in result.violations), (
        f"Expected `slice-branch-mismatch`; got: {[v.kind for v in result.violations]}"
    )


def test_branch_workflow_audit_accepts_escape_hatch_rationale_in_build_log_events(tmp_path: Path) -> None:
    """Audit accepts when on default branch IF build-log.md Events has canonical BRANCH=skip line."""
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    # Add canonical BRANCH=skip escape-hatch line per slice-021 AC #2 shape.
    # NOTE: encoding="utf-8" required on Windows (default cp1252 mangles em-dash
    # per Windows cp1252 class N=5 cumulative recurrence at slice-021).
    (slice_folder / "build-log.md").write_text(
        "# Build log\n\n## Events\n\n"
        "- 2026-05-14 20:14 DEVIATION: BRANCH=skip — rationale: trivial 1-line typo fix per CLAUDE.md hard-rule exception.\n",
        encoding="utf-8",
    )
    # HEAD stays on default branch.
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert not result.violations, (
        f"Expected clean audit with canonical BRANCH=skip escape-hatch; got: {result.violations}"
    )
    assert result.escape_hatch_used is True, "escape_hatch_used must be True when accepted via escape-hatch"


def test_branch_workflow_audit_resolves_default_branch_via_symbolic_ref(tmp_path: Path) -> None:
    """Audit resolves default branch via `git symbolic-ref refs/remotes/origin/HEAD`."""
    repo = _init_repo_on_default_branch(tmp_path, default="trunk")
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    # On `trunk` (the resolved default branch), audit should refuse without escape-hatch.
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert result.resolved_default_branch == "trunk", (
        f"Expected resolved_default_branch=='trunk'; got '{result.resolved_default_branch}'"
    )
    assert result.violations, "Expected violation when on default branch (trunk)"


def test_branch_workflow_audit_falls_back_to_init_default_branch(tmp_path: Path) -> None:
    """When `git symbolic-ref refs/remotes/origin/HEAD` fails, fallback to `init.defaultBranch`."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init", "-b", "dev")
    _run_git(repo, "config", "user.email", "test@test.test")
    _run_git(repo, "config", "user.name", "Test")
    _run_git(repo, "config", "init.defaultBranch", "dev")
    (repo / "README.md").write_text("test\n")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "init")
    # NO origin remote configured, so symbolic-ref will fail; fallback to init.defaultBranch.
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert result.resolved_default_branch == "dev", (
        f"Expected fallback to 'dev' via init.defaultBranch; got '{result.resolved_default_branch}'"
    )


def test_branch_workflow_audit_stops_when_neither_symbolic_ref_nor_init_default_branch_resolves(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Audit returns usage-error when neither symbolic-ref nor init.defaultBranch resolves.

    Isolates global git config (which typically sets `init.defaultBranch=master`) using
    GIT_CONFIG_GLOBAL + GIT_CONFIG_NOSYSTEM env overrides — otherwise global config leaks
    past the test's `git config --unset` local. The audit's _resolve_default_branch
    subprocess inherits the env and resolves to None as intended.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    empty_config = tmp_path / "empty-global-gitconfig"
    empty_config.write_text("", encoding="utf-8")
    # Isolate git config: empty global + no system config.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty_config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")

    _run_git(repo, "init", "-b", "foobar")
    _run_git(repo, "config", "user.email", "test@test.test")
    _run_git(repo, "config", "user.name", "Test")
    # NO origin remote, NO init.defaultBranch config (global is empty + system disabled).
    (repo / "README.md").write_text("test\n")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "init")
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert any(v.kind == "default-branch-unresolvable" for v in result.violations), (
        f"Expected `default-branch-unresolvable` violation; got: {[v.kind for v in result.violations]}"
    )


def test_branch_workflow_audit_warns_on_stale_slice_branch_from_prior_conflict(tmp_path: Path) -> None:
    """Audit warns when stale `slice/*` branches exist (artefact of prior conflict-recovery)."""
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    # Create slice-021 branch + a stale slice/019-... branch from "prior conflict".
    _run_git(repo, "checkout", "-b", "slice/019-stale-prior-slice")
    _run_git(repo, "checkout", "master")
    _run_git(repo, "checkout", "-b", "slice/021-test-feature")
    # The slice/019 branch still exists; audit should warn (not refuse) on current slice/021.
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    # Stale branches surfaced as warning-class findings (kind="stale-slice-branch") — not fatal.
    stale_warnings = [v for v in result.violations if v.kind == "stale-slice-branch"]
    assert stale_warnings, (
        "Expected `stale-slice-branch` warning when prior slice/* branches linger; "
        f"got: {[v.kind for v in result.violations]}"
    )
