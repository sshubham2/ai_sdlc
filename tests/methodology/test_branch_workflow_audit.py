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


# --- Slice-066 / BRANCH-2 worktree-mode audit tests (AC3) ---


def _add_worktree(repo: Path, wt_path: Path, branch: str, base: str = "master") -> None:
    """Create a worktree via real git plumbing.

    `wt_path.parent` must exist (created by caller). `git worktree add` creates the wt-path
    directory itself.
    """
    _run_git(repo, "worktree", "add", str(wt_path), "-b", branch, base)


def _make_slice_folder_in_worktree(wt_path: Path, slice_number: int, slice_name: str) -> Path:
    """Create the active-slice folder inside a worktree's checkout (mirrors repo content)."""
    slice_folder = wt_path / "architecture" / "slices" / f"slice-{slice_number:03d}-{slice_name}"
    slice_folder.mkdir(parents=True)
    (slice_folder / "mission-brief.md").write_text("# Slice fixture\n")
    return slice_folder


def test_accepts_cwd_in_worktree_sibling_path(tmp_path: Path) -> None:
    """Shape 1 canonical clean: cwd inside worktree at canonical sibling path; audit accepts.

    Defect class: pre-slice-066 the audit had no worktree-mode awareness — running it from
    inside a worktree at `<main-parent>/<main-name>-wt/slice-NNN-<name>` either spuriously
    refused (wrong-cwd false positive) or quietly accepted without verifying registration.
    Post-BRANCH-2, the audit detects worktree-mode via the `.git` file marker + verifies
    registration via `git worktree list --porcelain`.

    Rule reference: BRANCH-2 sub-mode (c) extended (slice-066; ADR-063).
    """
    repo = _init_repo_on_default_branch(tmp_path)
    # Sibling-dir canonical convention: <tmp_path>/repo-wt/slice-021-test-feature (repo is at <tmp_path>/repo).
    wt_path = tmp_path / "repo-wt" / "slice-021-test-feature"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/021-test-feature")
    slice_folder = _make_slice_folder_in_worktree(wt_path, 21, "test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=wt_path)
    important = [v for v in result.violations if v.severity == "Important"]
    assert not important, (
        f"Shape 1 (cwd in canonical sibling-path worktree, slice branch checked out) must be clean; "
        f"got Important violations: {[(v.kind, v.message) for v in important]}"
    )


def test_accepts_worktree_registered_via_git_worktree_list_porcelain(tmp_path: Path) -> None:
    """The audit must verify the worktree IS registered via `git worktree list --porcelain`.

    Defect class: silent acceptance based on filesystem path-shape alone (without checking
    `git worktree list`) admits a corrupted state where a directory looks like a worktree
    (correct path, has `.git` file) but isn't actually registered in `.git/worktrees/`.

    Rule reference: BRANCH-2 worktree-registered helper (slice-066; ADR-063 §Decision).
    """
    repo = _init_repo_on_default_branch(tmp_path)
    wt_path = tmp_path / "repo-wt" / "slice-021-test-feature"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/021-test-feature")
    # Verify `git worktree list --porcelain` shows the worktree (real git plumbing).
    list_result = _run_git(repo, "worktree", "list", "--porcelain")
    assert str(wt_path) in list_result.stdout or wt_path.name in list_result.stdout, (
        f"git worktree list --porcelain must show the new worktree at {wt_path}; got: {list_result.stdout}"
    )
    slice_folder = _make_slice_folder_in_worktree(wt_path, 21, "test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=wt_path)
    # No worktree-not-registered violation should fire (the worktree IS registered).
    assert not any(v.kind == "worktree-not-registered" for v in result.violations), (
        f"Worktree registered via `git worktree list --porcelain` must not emit "
        f"`worktree-not-registered`; got: {[v.kind for v in result.violations]}"
    )


def test_rejects_main_tree_cwd_when_worktree_registered_elsewhere(tmp_path: Path) -> None:
    """Shape 2 (forgot to cd): cwd is main tree, slice branch checked out in worktree; audit emits worktree-cwd-mismatch.

    Defect class: this is the canonical "Claude forgot to `cd` into the worktree" failure mode.
    Without `worktree-cwd-mismatch` detection, a Claude running /build-slice Step 6 in the main
    tree (HEAD on default) while the slice branch is checked out in a worktree elsewhere would
    either fire the wrong violation (on-default-branch) or silently accept.

    Rule reference: BRANCH-2 / ADR-063 §Decision Audit invocation call-shapes shape 2.
    """
    repo = _init_repo_on_default_branch(tmp_path)
    wt_path = tmp_path / "repo-wt" / "slice-021-test-feature"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/021-test-feature")
    # Slice folder also exists in the main tree (mirror of vault content).
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    # Audit called with main tree as repo_root → forgot-to-cd canonical case.
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert any(v.kind == "worktree-cwd-mismatch" for v in result.violations), (
        f"Shape 2 (cwd in main tree, slice branch checked out in worktree elsewhere) must emit "
        f"`worktree-cwd-mismatch`; got kinds: {[v.kind for v in result.violations]}. "
        f"Per ADR-063 §Decision Audit-invocation call-shapes shape 2."
    )


def test_accepts_invocation_from_inside_worktree_with_relative_slice_folder(tmp_path: Path) -> None:
    """Variant of shape 1: invocation with cwd-relative slice-folder path inside the worktree.

    Defect class: Path resolution semantics must tolerate cwd-relative slice-folder arguments
    when invoked from inside the worktree (the canonical /build-slice Step 6 invocation form).
    Per design.md "Path-comparison semantics" + Windows path edge cases (microsoft/vscode#101244).

    Rule reference: BRANCH-2 path-comparison semantics (slice-066; /critique B2 ACCEPTED-FIXED).
    """
    repo = _init_repo_on_default_branch(tmp_path)
    wt_path = tmp_path / "repo-wt" / "slice-021-test-feature"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/021-test-feature")
    slice_folder = _make_slice_folder_in_worktree(wt_path, 21, "test-feature")
    # Pass slice_folder as absolute path (canonical form); repo_root resolution should land on wt_path.
    result = bwa.audit(slice_folder=slice_folder, repo_root=None)
    important = [v for v in result.violations if v.severity == "Important"]
    assert not important, (
        f"Shape 1 variant (cwd-resolved repo_root from slice_folder ancestor walk; worktree's .git "
        f"file detected) must be clean; got Important violations: {[(v.kind, v.message) for v in important]}"
    )


def test_emits_worktree_path_shape_violation_on_non_canonical_wt_path(tmp_path: Path) -> None:
    """Worktree registered but at a non-canonical path (not `<main-parent>/<main-name>-wt/slice-NNN-<name>`) emits `worktree-path-shape-violation`.

    Defect class: a worktree at an arbitrary path (e.g., `/tmp/random-wt/`) bypasses the
    canonical convention; tools that derive the worktree path via the canonical resolver
    would miss it.

    Rule reference: BRANCH-2 / ADR-063 §Decision canonical worktree path convention.
    """
    repo = _init_repo_on_default_branch(tmp_path)
    # Non-canonical wt-path: NOT `<tmp_path>/repo-wt/...`, instead `<tmp_path>/elsewhere/...`.
    wt_path = tmp_path / "elsewhere" / "slice-021-test-feature"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/021-test-feature")
    slice_folder = _make_slice_folder_in_worktree(wt_path, 21, "test-feature")
    result = bwa.audit(slice_folder=slice_folder, repo_root=wt_path)
    assert any(v.kind == "worktree-path-shape-violation" for v in result.violations), (
        f"Non-canonical worktree path `{wt_path}` (expected `{tmp_path}/repo-wt/slice-021-test-feature`) "
        f"must emit `worktree-path-shape-violation`; got kinds: {[v.kind for v in result.violations]}"
    )


def test_honours_canonical_worktree_skip_rationale_line(tmp_path: Path) -> None:
    """A canonical `WORKTREE=skip — rationale: <text>` line in build-log.md Events accepts the audit clean.

    Defect class: without an escape-hatch, a legitimate single-tree edge-case slice (or the
    slice-066 bootstrap itself) would be falsely refused by the worktree-mode gate.

    Canonical line shape (mirrors BRANCH=skip): `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip\\b.+rationale: .+`

    slice-071 m2 FIX (per slice-066 code-Critic m2 + APED-1 conformance):
    fixture rewritten to actually exercise the WORKTREE=skip dependency.
    Pre-fix the test passed even WITHOUT the WORKTREE=skip line because
    the slice branch was checked out IN the main tree (no worktree
    registered elsewhere), so `_slice_branch_in_worktree(repo_root,
    expected)` found a match on the main-tree's own worktree-list entry,
    and `_paths_equivalent(wt_path, repo_root)` returned True (it IS the
    main tree), so no `worktree-cwd-mismatch` fired regardless. The
    rewritten fixture creates a worktree elsewhere with the slice branch
    (mirroring `test_rejects_main_tree_cwd_when_worktree_registered_
    elsewhere`) — the WORKTREE=skip line is now load-bearing for the
    audit's clean verdict.

    Rule reference: BRANCH-2 WORKTREE=skip escape-hatch (slice-066; ADR-063 §Decision).
    """
    repo = _init_repo_on_default_branch(tmp_path)
    # Create the worktree elsewhere with the slice branch — without the
    # WORKTREE=skip line the audit would now emit worktree-cwd-mismatch
    # (the slice branch lives in <wt_path> but the audit's repo_root is the
    # main tree). This is the canonical "Claude forgot to cd into the
    # worktree" failure mode that the WORKTREE=skip escape-hatch covers.
    wt_path = tmp_path / "repo-wt" / "slice-066-test-worktree-skip"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/066-test-worktree-skip")
    # Slice folder mirrored in the main tree for the audit invocation.
    slice_folder = _make_slice_folder(repo, 66, "test-worktree-skip")
    # WORKTREE=skip documented in build-log Events. Explicit utf-8 encoding
    # to match the audit module's read (UTF8-STDOUT-1 lineage discipline —
    # Windows default cp1252 corrupts U+2014 em-dash).
    (slice_folder / "build-log.md").write_text(
        "# Build log\n\n"
        "## Events\n\n"
        "- 2026-05-24 17:00 DEVIATION: WORKTREE=skip-bootstrap "
        "— rationale: slice-066 authors the worktree-create prose; bootstrap-reference instance #1\n",
        encoding="utf-8",
    )
    # Audit invoked with main tree as repo_root (the "forgot to cd" shape
    # — without WORKTREE=skip, worktree-cwd-mismatch would fire).
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    # No worktree-* Important violations should fire (the escape-hatch is honoured).
    worktree_violations = [
        v for v in result.violations
        if v.kind.startswith("worktree-") and v.severity == "Important"
    ]
    assert not worktree_violations, (
        f"Canonical WORKTREE=skip — rationale: line must accept worktree-mode discipline skip; "
        f"got worktree-* violations: {[(v.kind, v.message) for v in worktree_violations]}"
    )
    # APED-1 load-bearing check (slice-071 m2 FIX): remove the
    # WORKTREE=skip line → audit MUST now fail with worktree-cwd-mismatch.
    # Proves the WORKTREE=skip line was the load-bearing element of the
    # clean verdict above (pre-slice-071 fixture passed even without it).
    (slice_folder / "build-log.md").write_text(
        "# Build log\n\n## Events\n\n- 2026-05-26 09:00 BUILD: starting\n",
        encoding="utf-8",
    )
    result_without_skip = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert any(
        v.kind == "worktree-cwd-mismatch" and v.severity == "Important"
        for v in result_without_skip.violations
    ), (
        "APED-1 load-bearing check (slice-071 m2 FIX): removing the "
        "WORKTREE=skip line MUST cause `worktree-cwd-mismatch` to fire. "
        f"Got violations: {[(v.kind, v.severity) for v in result_without_skip.violations]}"
    )


def test_audit_result_surfaces_worktree_skip_fields(tmp_path: Path) -> None:
    """slice-071 m1 FIX pin (per slice-066 code-Critic m1).

    `AuditResult.worktree_skip_used` + `worktree_skip_rationale` MUST be
    populated AND reach `to_dict()` output. Symmetric with the existing
    BRANCH=skip surface (`escape_hatch_used` + `escape_hatch_rationale`).

    Pre-fix: `_check_worktree_skip_line` returned the rationale but the
    consumer at L513 discarded it (`_` prefix); a `--json` consumer could
    not distinguish "clean because BRANCH=skip" from "clean because
    WORKTREE=skip".
    """
    repo = _init_repo_on_default_branch(tmp_path)
    # Set up: worktree elsewhere + WORKTREE=skip line.
    wt_path = tmp_path / "repo-wt" / "slice-066-skip-fields-test"
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    _add_worktree(repo, wt_path, "slice/066-skip-fields-test")
    slice_folder = _make_slice_folder(repo, 66, "skip-fields-test")
    rationale_text = "test rationale for surfacing worktree_skip in AuditResult"
    (slice_folder / "build-log.md").write_text(
        "# Build log\n\n## Events\n\n"
        "- 2026-05-26 10:00 DEVIATION: WORKTREE=skip "
        f"— rationale: {rationale_text}\n",
        encoding="utf-8",
    )
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert result.worktree_skip_used is True, (
        f"AuditResult.worktree_skip_used must be True when WORKTREE=skip "
        f"line is present; got {result.worktree_skip_used}"
    )
    assert result.worktree_skip_rationale is not None, (
        "AuditResult.worktree_skip_rationale must be populated when "
        "WORKTREE=skip line is present"
    )
    assert rationale_text in result.worktree_skip_rationale, (
        f"AuditResult.worktree_skip_rationale must contain the rationale "
        f"text from the canonical line; got {result.worktree_skip_rationale!r}"
    )
    # Verify the fields reach to_dict() output (--json consumer-visible).
    d = result.to_dict()
    assert d["worktree_skip_used"] is True
    assert rationale_text in d["worktree_skip_rationale"]
    # Symmetry pin: the BRANCH=skip surface fields also exist (not populated
    # in this test, but the schema is symmetric).
    assert "escape_hatch_used" in d
    assert "escape_hatch_rationale" in d


def test_emits_worktree_skip_malformed_on_off_canonical_line(tmp_path: Path) -> None:
    """A `WORKTREE=skip` line that doesn't match canonical grammar emits `worktree-skip-malformed`.

    Defect class: a permissive WORKTREE=skip grammar (no HH:MM, no `rationale:` token) admits
    drive-by "I skipped" notes that bypass audit discipline. The narrow regex
    `^- \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2} DEVIATION: WORKTREE=skip\\b.+rationale: .+` mirrors
    BRANCH=skip's shape.

    Rule reference: BRANCH-2 WORKTREE=skip grammar pin (slice-066; ADR-063; mirrors BRANCH=skip).
    """
    repo = _init_repo_on_default_branch(tmp_path)
    slice_folder = _make_slice_folder(repo, 66, "test-worktree-skip-malformed")
    # Off-canonical WORKTREE=skip line: no HH:MM, no `rationale:` token.
    # Explicit utf-8 to mirror the audit module's read (UTF8-STDOUT-1 lineage discipline).
    (slice_folder / "build-log.md").write_text(
        "# Build log\n\n"
        "## Events\n\n"
        "- WORKTREE=skip because I felt like it\n",
        encoding="utf-8",
    )
    _run_git(repo, "checkout", "-b", "slice/066-test-worktree-skip-malformed")
    result = bwa.audit(slice_folder=slice_folder, repo_root=repo)
    assert any(v.kind == "worktree-skip-malformed" for v in result.violations), (
        f"Off-canonical WORKTREE=skip line must emit `worktree-skip-malformed`; got: "
        f"{[v.kind for v in result.violations]}"
    )


def test_worktree_skip_grammar_pinned_across_three_surfaces() -> None:
    """Cross-spec parity (RPCD-1): WORKTREE=skip canonical phrase appears across 3 surfaces.

    Defect class: a future edit to one surface (e.g., commit-slice SKILL.md) that drops the
    canonical phrase would silently break the audit's escape-hatch reading. Cross-spec parity
    asserts the same literal exists in build-slice SKILL.md, commit-slice SKILL.md, AND
    branch_workflow_audit.py.

    Rule reference: RPCD-1 / cross-spec parity discipline (slice-019 / slice-023 lineage);
    BRANCH-2 grammar pin (slice-066; ADR-063 + /critique B4 ACCEPTED-FIXED).
    """
    repo_root = Path(__file__).resolve().parents[2]
    surfaces = {
        "skills/build-slice/SKILL.md": (repo_root / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8"),
        "skills/commit-slice/SKILL.md": (repo_root / "skills" / "commit-slice" / "SKILL.md").read_text(encoding="utf-8"),
        "tools/branch_workflow_audit.py": (repo_root / "tools" / "branch_workflow_audit.py").read_text(encoding="utf-8"),
    }
    canonical_phrase = "WORKTREE=skip"
    for surface_name, surface_content in surfaces.items():
        assert canonical_phrase in surface_content, (
            f"Cross-spec parity (RPCD-1): canonical phrase `{canonical_phrase}` must appear in "
            f"{surface_name} — per slice-066 /critique B4 ACCEPTED-FIXED + ADR-063 §Scope of "
            f"supersession (BRANCH=skip 4th-surface inheritance preserves parallel grammar; "
            f"WORKTREE=skip is the new worktree-discipline escape-hatch). If this test fails on "
            f"one surface, a future edit to that surface dropped the canonical phrase — re-add "
            f"verbatim before /commit-slice."
        )
