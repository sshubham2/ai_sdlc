"""slice-091 / ADR-083 — fail-closed behavior on a non-UTF-8 conflict stage.

These tests pin the R-30 residual #1 fix: a conflict stage that is PRESENT but
holds genuinely non-UTF-8 bytes must drive a LOUD fail-closed UNKNOWN STOP, never
a silent falsy claim-drop (which re-opens the VAULT_CLAIM bypass) and never an
uncaught ``UnicodeDecodeError``.

Cross-platform (host-locale-independent): the bytes are invalid UTF-8, so the
strict decode fails on every platform — no skip guard. Staging uses a REAL rebase
conflict (the ``git update-index --index-info`` single-stage approach is dead on
the dev's Windows ``git.exe`` — see tests/bugs/test_pcr_git_show_stage_non_utf8_
fail_closed.py for the /critique B1 finding).
"""
from __future__ import annotations

import subprocess

import pytest

from tools.parallel_conflict_resolver import (
    ConflictClass,
    ConflictDiagnostic,
    _AUDIT_LOG_PATH,
    _git_show_stage,
    _StageDecodeError,
    classify_conflict,
    diagnose_conflict,
    resolve_soft_conflict,
)

_QUEUE_REL = "architecture/slice-queue.md"

# Invalid UTF-8: 0xFF / lone 0x80 / 0xC3 0x28 — undecodable under strict UTF-8.
_NON_UTF8 = (
    b"### cand-evil \xff\xfe\x80 \xc3\x28 broken\n"
    b"- **Claimed-by:** Bob bob@example.com\n"
    b"- **Claimed-at:** 2026-05-31T10:00:00+00:00\n"
)
_UTF8 = (
    "### cand-other\n"
    "- **Claimed-by:** Alice alice@example.com\n"
    "- **Claimed-at:** 2026-05-31T09:00:00+00:00\n"
)


def _git(tmp_path, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=tmp_path, check=check,
        capture_output=True, text=True, encoding="utf-8",
    )


def _stage_rebase_non_utf8(tmp_path, rel_path, *, bad_stage):
    """Build a real rebase conflict on ``rel_path``; the non-UTF-8 bytes land in
    ``bad_stage`` (2 = master/ours, 3 = branchA/theirs); the other stage is
    decodable UTF-8 (a control)."""
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    target.write_text("# stub\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    if bad_stage == 3:
        target.write_bytes(_NON_UTF8)
    else:
        target.write_text(_UTF8, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    if bad_stage == 2:
        target.write_bytes(_NON_UTF8)
    else:
        target.write_text(_UTF8, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)
    # Fixture guard: the bad stage must really hold the invalid bytes (exit 0).
    raw = subprocess.run(
        ["git", "show", f":{bad_stage}:{rel_path}"], cwd=tmp_path,
        capture_output=True,
    )
    assert raw.returncode == 0 and b"\xff" in raw.stdout, (
        f"fixture failed to populate stage {bad_stage} with non-UTF-8 bytes "
        f"(rc={raw.returncode!r}) — the rebase did not conflict as expected."
    )


# --- AC2 -------------------------------------------------------------------

def test_present_stage_distinguished_from_absent_stage(tmp_path):
    """AC2: a present-but-non-UTF-8 stage raises ``_StageDecodeError`` (NOT a
    falsy value, NOT a raw ``UnicodeDecodeError``); an ABSENT stage still
    returns ``""`` — the two outcomes are distinguishable by the caller."""
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL, bad_stage=2)

    # Present-but-undecodable → typed fail-closed signal.
    with pytest.raises(_StageDecodeError) as ei:
        _git_show_stage(tmp_path, 2, _QUEUE_REL)
    assert ei.value.conflict_class is ConflictClass.UNKNOWN
    assert ei.value.stage == 2 and ei.value.path == _QUEUE_REL
    assert not isinstance(ei.value, UnicodeDecodeError)

    # Absent stage (no such stage for a never-conflicted path) → "" sentinel,
    # NOT a _StageDecodeError — the asymmetric-stage case stays distinguishable.
    assert _git_show_stage(tmp_path, 2, "architecture/does-not-exist.md") == ""


# --- AC3 -------------------------------------------------------------------

def test_undecodable_stage_records_audit_breadcrumb(tmp_path):
    """AC3: diagnose_conflict on an undecodable slice-queue stage marks the
    diagnostic degraded AND appends an audit breadcrumb naming stage + path —
    the failure is visible, not silent."""
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL, bad_stage=2)

    diag = diagnose_conflict(tmp_path)
    assert diag.claim_extraction_degraded is True
    assert diag.claim_history == ()  # no claims trusted from a degraded read

    log = (tmp_path / _AUDIT_LOG_PATH).read_text(encoding="utf-8")
    assert "## Decode-failure STOP (non-UTF-8 stage)" in log
    assert "**Undecodable stage**: 2" in log
    assert f"**Path**: {_QUEUE_REL}" in log
    assert "STOP (fail-closed, no writes)" in log


def test_stage_3_undecodable_also_degrades(tmp_path):
    """m-add-2: the catch is symmetric — a non-UTF-8 STAGE 3 (stage 2 decodable)
    degrades the diagnostic too, not only stage 2."""
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL, bad_stage=3)

    diag = diagnose_conflict(tmp_path)
    assert diag.claim_extraction_degraded is True
    log = (tmp_path / _AUDIT_LOG_PATH).read_text(encoding="utf-8")
    assert "## Decode-failure STOP (non-UTF-8 stage)" in log
    assert "**Undecodable stage**: 3" in log


# --- classify / resolve fail-closed channel --------------------------------

def test_classify_degraded_diagnostic_returns_unknown():
    """A degraded diagnostic classifies as UNKNOWN — the fail-closed channel,
    never silent-default to SOFT (no git needed; pure classifier)."""
    degraded = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={"architecture/slice-queue.md": ()},
        claim_history=(),
        claim_extraction_degraded=True,
    )
    assert classify_conflict(degraded) is ConflictClass.UNKNOWN


def test_resolve_soft_on_undecodable_stage_stops_no_writes(tmp_path):
    """End-to-end: a slice-queue.md conflict with a non-UTF-8 stage resolves to
    a STOP (UNKNOWN), never an auto-resolve/rebase --continue."""
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL, bad_stage=2)

    diag = diagnose_conflict(tmp_path)  # degraded=True
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.UNKNOWN
    assert result.regenerated_files == ()
    # rebase still in progress (not --continue'd): the conflict is unresolved.
    status = _git(tmp_path, "status", "--porcelain", check=False).stdout
    assert "slice-queue.md" in status


def test_defense_in_depth_regen_slice_queue_fail_closed(tmp_path):
    """Defense-in-depth: even a NON-degraded diagnostic (e.g. a stale diag piped
    without re-diagnose) fails closed — resolve_soft_conflict's SOFT path calls
    _regen_slice_queue → _git_show_stage → _StageDecodeError, caught by the
    existing ``except _SoftResolutionError`` handler → STOP(UNKNOWN)."""
    _stage_rebase_non_utf8(tmp_path, _QUEUE_REL, bad_stage=2)

    # Hand-built diagnostic that does NOT carry the degraded flag, forcing the
    # SOFT classification + the live re-read in _regen_slice_queue.
    stale = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={"architecture/slice-queue.md": ()},
        claim_history=(),
        claim_extraction_degraded=False,
    )
    assert classify_conflict(stale) is ConflictClass.SOFT  # not yet degraded

    result = resolve_soft_conflict(stale, repo_root=tmp_path)
    assert result.action == "STOP"
    assert result.conflict_class is ConflictClass.UNKNOWN
    assert result.regenerated_files == ()
