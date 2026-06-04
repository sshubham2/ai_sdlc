"""Tests for the DCE-1 drift-check enforcement audit (tools/drift_check_audit.py).

APED-1 empirical-execution discipline: clean / refuse / escape-hatch / mode /
usage paths are each exercised against real on-disk fixtures, and the
line-anchored + slice-anchored marker matcher is parametrized against the
producer-template variants AND the /critique-review M-add-1 false-ACCEPT surface
(a cross-slice mention in a non-Trigger line must NOT satisfy the gate).

Per DCE-1 (methodology-changelog.md v0.76.0; ADR-073; slice-081).
"""
from __future__ import annotations

from pathlib import Path

import pytest

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
from tools import drift_check_audit as dca

SLICE_NAME = "slice-081-fix-drift-check-enforcement-gap"


@pytest.fixture(autouse=True)
def _pin_vault_location_agnostic():
    """slice-110 / [[ADR-101]]: pin drift_check_audit's VAULT_ROOT to the in-tree
    relative default so every test reads its own ``<repo_root>/architecture/...``
    fixture — green under the default suite AND under an external
    ``AI_SDLC_VAULT_ROOT`` override (the flip simulation). Without this, the
    absolute override makes ``repo_root / VAULT_ROOT / x`` discard the test's tmp
    ``repo_root`` and read the real external store."""
    with vi.pin_vault_root(Path("architecture"), dca):
        yield


def _make_repo(
    tmp_path: Path,
    *,
    mode: str | None = "Standard",
    drift_log: str | None = None,
    milestone_frontmatter_extra: str = "",
    with_milestone: bool = True,
) -> tuple[Path, Path]:
    """Build a throwaway repo; return (repo_root, slice_folder)."""
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "architecture").mkdir(parents=True)
    if mode is not None:
        (repo / "CLAUDE.md").write_text(f"**Mode**: {mode} — see architecture/triage.md\n", encoding="utf-8")
    # else: no CLAUDE.md and no triage.md → mode unresolvable.
    if drift_log is not None:
        (repo / "architecture" / "drift-log.md").write_text(drift_log, encoding="utf-8")
    slice_folder = repo / "architecture" / "slices" / SLICE_NAME
    slice_folder.mkdir(parents=True)
    if with_milestone:
        fm = "---\nslice: " + SLICE_NAME + "\nstage: build\n"
        fm += milestone_frontmatter_extra
        fm += "---\n\n# Milestone\n"
        (slice_folder / "milestone.md").write_text(fm, encoding="utf-8")
    return repo, slice_folder


_CANONICAL_TRIGGER = "## Audit 2026-05-29\n\n**Trigger**: slice-081 pre-finish gate (/build-slice Step 6)\n**Findings**: 0 blockers\n"


def test_accepts_when_trigger_line_present(tmp_path):
    repo, sf = _make_repo(tmp_path, drift_log=_CANONICAL_TRIGGER)
    r = dca.audit(sf, repo_root=repo)
    assert not r.violations
    assert r.drift_marker_present is True
    assert "slice-081" in r.accepted_reason


def test_refuses_when_drift_check_not_run(tmp_path):
    # drift-log exists but has no Trigger line for slice-081.
    other = "## Audit 2026-05-20\n\n**Trigger**: slice-079 pre-finish gate\n**Findings**: 0\n"
    repo, sf = _make_repo(tmp_path, drift_log=other)
    r = dca.audit(sf, repo_root=repo)
    assert [v.kind for v in r.violations] == ["drift-check-not-run"]


def test_refuses_when_drift_log_absent(tmp_path):
    # No drift-log.md at all → no marker → refuse (NOT usage-error).
    repo, sf = _make_repo(tmp_path, drift_log=None)
    r = dca.audit(sf, repo_root=repo)
    assert [v.kind for v in r.violations] == ["drift-check-not-run"]


def test_false_accept_guard_cross_slice_mention(tmp_path):
    """M-add-1: slice-081 mentioned only in a prior entry's Notes/Scope/heading
    (NOT a `**Trigger**:` line) must NOT false-ACCEPT."""
    drift_log = (
        "## Audit 2026-05-20 (slice-081 deferred work noted here)\n\n"
        "**Trigger**: slice-079 pre-finish gate\n"
        "**Scope**: full (cross-refs slice-081 follow-up)\n\n"
        "### Notes\n- deferred to slice-081; blocked on slice-081 review\n"
    )
    repo, sf = _make_repo(tmp_path, drift_log=drift_log)
    r = dca.audit(sf, repo_root=repo)
    assert r.drift_marker_present is False
    assert [v.kind for v in r.violations] == ["drift-check-not-run"]


def test_accepts_canonical_skip(tmp_path):
    repo, sf = _make_repo(
        tmp_path,
        drift_log=None,
        milestone_frontmatter_extra='drift-check-skip: "skip — rationale: docs-only slice"\n',
    )
    r = dca.audit(sf, repo_root=repo)
    assert not r.violations
    assert r.skip_rationale == "skip — rationale: docs-only slice"


def test_refuses_malformed_skip(tmp_path):
    repo, sf = _make_repo(
        tmp_path,
        drift_log=None,
        milestone_frontmatter_extra='drift-check-skip: "yeah whatever"\n',
    )
    r = dca.audit(sf, repo_root=repo)
    assert [v.kind for v in r.violations] == ["escape-hatch-malformed"]


def test_accepts_minimal_mode(tmp_path):
    repo, sf = _make_repo(tmp_path, mode="Minimal", drift_log=None)
    r = dca.audit(sf, repo_root=repo)
    assert not r.violations
    assert "MINIMAL" in r.accepted_reason


def test_usage_error_mode_unresolvable(tmp_path):
    repo, sf = _make_repo(tmp_path, mode=None, drift_log=_CANONICAL_TRIGGER)
    r = dca.audit(sf, repo_root=repo)
    assert [v.kind for v in r.violations] == ["mode-unresolvable"]


def test_usage_error_missing_milestone(tmp_path):
    repo, sf = _make_repo(tmp_path, with_milestone=False)
    r = dca.audit(sf, repo_root=repo)
    assert [v.kind for v in r.violations] == ["usage-error"]


def test_usage_error_missing_folder(tmp_path):
    repo, sf = _make_repo(tmp_path)
    missing = sf.parent / "slice-999-nonexistent"
    r = dca.audit(missing, repo_root=repo)
    assert [v.kind for v in r.violations] == ["usage-error"]


# --- main() exit-code contract -------------------------------------------------

def test_main_exit_codes(tmp_path):
    repo, sf = _make_repo(tmp_path, drift_log=_CANONICAL_TRIGGER)
    assert dca.main([str(sf), "--root", str(repo)]) == 0

    repo2, sf2 = _make_repo(tmp_path / "b", drift_log=None)
    assert dca.main([str(sf2), "--root", str(repo2)]) == 1

    repo3, sf3 = _make_repo(tmp_path / "c", mode=None, drift_log=_CANONICAL_TRIGGER)
    assert dca.main([str(sf3), "--root", str(repo3)]) == 2


# --- APED-1: line-anchored + slice-anchored marker matcher ---------------------

@pytest.mark.parametrize(
    "trigger_token, expect",
    [
        ("slice-081", True),    # canonical dash form
        ("slice81", True),      # sloppy no-dash no-pad
        ("slice 81", True),     # space separator
        ("slice-81", True),     # dash, no zero-pad
        ("slice-0810", False),  # collision: trailing digit
        ("slice-081x", False),  # collision: trailing word char
        ("slice-810", False),   # different slice
        ("slice-018", False),   # transposed digits
        ("slice-079", False),   # adjacent slice
        ("xslice-081", False),  # left-prefix collision (m1 — left `\b`)
        ("subslice-081", False),  # left-prefix word collision (m1 — left `\b`)
    ],
)
def test_marker_regex_anchoring(tmp_path, trigger_token, expect):
    drift_log = f"## Audit 2026-05-29\n\n**Trigger**: {trigger_token} pre-finish gate\n"
    repo, _sf = _make_repo(tmp_path, drift_log=drift_log)
    assert dca._drift_marker_present(repo, "081") is expect


def test_marker_only_matches_trigger_lines(tmp_path):
    """The slice token on a non-Trigger line must NOT count (M-add-1 anchor)."""
    drift_log = (
        "## Audit 2026-05-29\n\n"
        "**Trigger**: slice-079 pre-finish gate\n"
        "**Scope**: slice-081 follow-up referenced here\n"
        "- resolution touches slice-081 docs\n"
    )
    repo, _sf = _make_repo(tmp_path, drift_log=drift_log)
    assert dca._drift_marker_present(repo, "081") is False
