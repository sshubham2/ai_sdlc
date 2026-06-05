"""PCR-2a clock-skew guard tests (slice-084 / ADR-076).

Hardens PCR-2a's strict-newer VAULT_CLAIM winner against cross-machine
clock-skew (R-23, partial). A Step 2.5 guard in ``resolve_vault_claim_conflict``
flags a winner whose ``Claimed-at`` is future-dated relative to the resolver's
own (injectable) wall-clock beyond a tolerance, OR is unparseable / tz-naive
(fail-closed) — returning a STOP that escalates to the PCR-2b gate rather than
silently applying a possibly-skewed strict-newer win.

APED-1 battery (per BC-PROJ-13): the timestamp parse + future-dating comparison
is exercised against an adversarial corpus in BOTH directions (caught + resolves),
including the B1 (tz-naive) and B2 (Z-suffix on the >=3.10 floor) classes the
design Critic surfaced by execution.
"""
from __future__ import annotations

import datetime

import pytest

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.parallel_conflict_resolver as _pcr

# slice-110 / [[ADR-101]]: location-agnostic VAULT_ROOT pin (see autouse_pin).
_pin_vault = vi.autouse_pin(
    _vgit, _pcr,
    derived=[(_pcr, "_AUDIT_LOG_PATH",
              lambda vr: vr / "parallel-conflict-resolution-log.md")],
)

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    _AUDIT_LOG_PATH,
    _CLOCK_SKEW_TOLERANCE_SECONDS,
    _append_skew_stop_audit,
    _winner_clock_skew_suspect,
    resolve_soft_conflict,
    resolve_vault_claim_conflict,
)

UTC = datetime.timezone.utc


def _claim(name: str, by: str, at: str, stage: int) -> ClaimEntry:
    return ClaimEntry(candidate_name=name, claimed_by=by, claimed_at=at, branch_stage=stage)


def _diag(u_files=("architecture/slice-queue.md",), claim_history=()) -> ConflictDiagnostic:
    return ConflictDiagnostic(u_files=u_files, concerned_slices={}, claim_history=claim_history)


def _well_formed_queue(claimed_by: str, claimed_at: str) -> str:
    return (
        "# Slice queue\n\n## Candidates\n\n"
        "### add-foo\n\n"
        "- **Source:** synthetic\n"
        "- **Blast-radius:** `nothing`\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n"
        f"- **Claimed-by:** {claimed_by}\n"
        f"- **Claimed-at:** {claimed_at}\n"
        "\n### add-replacement\n\n"
        "- **Source:** synthetic\n"
        "- **Blast-radius:** `nothing`\n"
        "- **Parallel-safety:** NON-OVERLAPPING\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n"
    )


def _stage_rebase(tmp_path, text_2: str, text_3: str) -> None:
    """Build a tmp git repo with a rebase-in-progress on slice-queue.md.

    Mirrors the canonical fixture in test_pcr_2a_regen_slice_queue_dispatch.py:
    stage 2 = branchA (rebased), stage 3 = master tip (rebase-target).
    """
    import subprocess

    subprocess.run(["git", "init", "-q", "-b", "master"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir()
    qpath = tmp_path / "architecture" / "slice-queue.md"
    qpath.write_text("# Slice queue\n\n## Candidates\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp_path, check=True)
    subprocess.run(["git", "checkout", "-q", "-b", "branchA"], cwd=tmp_path, check=True)
    qpath.write_text(text_2, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "checkout", "-q", "master"], cwd=tmp_path, check=True)
    qpath.write_text(text_3, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "B"], cwd=tmp_path, check=True)
    subprocess.run(["git", "checkout", "-q", "branchA"], cwd=tmp_path, check=True)
    subprocess.run(["git", "rebase", "master"], cwd=tmp_path, capture_output=True)


# ---------------------------------------------------------------------------
# AC-1 — _winner_clock_skew_suspect unit behaviour (future-dating + fail-closed)
# ---------------------------------------------------------------------------

def test_suspicious_ordering_yields_no_auto_winner() -> None:
    """A winner future-dated beyond tolerance vs resolver-now → truthy skew reason."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    winner = _claim("add-foo", "alice <a@x>", "2026-05-29T12:00:00+00:00", 2)
    reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
    assert reason, "future-dated winner must be flagged suspicious (no auto-winner)"
    assert "future-dated" in reason and "clock-skew" in reason.lower()


def test_naive_offsetless_claimed_at_stops_not_crashes() -> None:
    """B1: an offset-less (tz-naive) claimed_at parses then would TypeError on compare.

    The guard must return a fail-closed reason, NOT raise.
    """
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    winner = _claim("add-foo", "alice <a@x>", "2026-05-29T12:00:00", 2)  # NO offset
    reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
    assert reason, "tz-naive claimed_at must fail-closed to a STOP reason, not crash"
    assert "PCR-2b" in reason


def test_unparseable_claimed_at_stops_fail_closed() -> None:
    """Garbage claimed_at → fail-closed reason (cannot verify)."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    for bad in ("not-a-timestamp", "", "2026-13-99T99:99:99+00:00"):
        winner = _claim("add-foo", "alice <a@x>", bad, 2)
        reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
        assert reason, f"unparseable claimed_at {bad!r} must fail-closed"
        assert "PCR-2b" in reason


def test_z_suffix_claimed_at_handled_version_independently() -> None:
    """B2: a Z-suffixed (RFC-3339 UTC) claimed_at must behave identically on any
    Python >=3.10 — future Z → suspicious; past Z → resolves (None)."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    future_z = _claim("add-foo", "alice <a@x>", "2026-05-29T12:00:00Z", 2)
    past_z = _claim("add-foo", "alice <a@x>", "2026-05-29T08:00:00Z", 2)
    assert _winner_clock_skew_suspect(future_z, now, _CLOCK_SKEW_TOLERANCE_SECONDS), (
        "future-dated Z-suffix winner must be flagged (version-independent)"
    )
    assert _winner_clock_skew_suspect(past_z, now, _CLOCK_SKEW_TOLERANCE_SECONDS) is None, (
        "past Z-suffix winner must resolve (None) on any >=3.10 interpreter"
    )


def test_gate_does_not_overtrigger_on_normal_skew_within_threshold() -> None:
    """AC-3: a winner within tolerance of resolver-now is NOT flagged."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    within = now + datetime.timedelta(seconds=200)  # < 300 tolerance
    winner = _claim("add-foo", "alice <a@x>", within.isoformat(), 2)
    assert _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS) is None


def test_tolerance_boundary_at_300s_not_suspicious() -> None:
    """Strict-greater boundary: exactly now + tolerance is NOT suspicious."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    at = now + datetime.timedelta(seconds=_CLOCK_SKEW_TOLERANCE_SECONDS)
    winner = _claim("add-foo", "alice <a@x>", at.isoformat(), 2)
    assert _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS) is None


def test_tolerance_boundary_at_301s_suspicious() -> None:
    """One second past tolerance → suspicious (pins strict `>`)."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    at = now + datetime.timedelta(seconds=_CLOCK_SKEW_TOLERANCE_SECONDS + 1)
    winner = _claim("add-foo", "alice <a@x>", at.isoformat(), 2)
    assert _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)


def test_skew_stop_reason_routes_to_pcr_2b_gate() -> None:
    """AC-2: the suspicious reason names the PCR-2b escalation path."""
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    winner = _claim("add-foo", "alice <a@x>", "2026-05-29T12:00:00+00:00", 2)
    reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
    assert "PCR-2b" in reason


# ---------------------------------------------------------------------------
# AC-2 — skew-STOP audit records both claims + the resolver-now signal
# ---------------------------------------------------------------------------

def test_skew_stop_audit_records_both_claims_and_signal(tmp_path) -> None:
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    winner = _claim("add-foo", "alice <a@example.com>", "2026-05-29T12:00:00+00:00", 2)
    loser = _claim("add-foo", "bob <b@example.com>", "2026-05-29T11:00:00+00:00", 3)
    reason = "clock-skew suspected: ... escalate to PCR-2b hand-resolve + TRI-RESOLVE-1"
    _append_skew_stop_audit(tmp_path, reason, winner, loser, now)

    # slice-115 ([[ADR-107]] — the flip): use the LIVE module attr `_pcr._AUDIT_LOG_PATH`
    # (re-derived to "architecture/…" relative by the autouse pin), NOT the module-level import
    # `_AUDIT_LOG_PATH` which froze to the live (post-flip ABSOLUTE external) value at test import —
    # `tmp_path / <absolute>` resolves to the live external log, not this fixture.
    log = (tmp_path / _pcr._AUDIT_LOG_PATH).read_text(encoding="utf-8")
    assert "clock-skew STOP" in log
    assert "alice <a@example.com>" in log and "2026-05-29T12:00:00+00:00" in log
    assert "bob <b@example.com>" in log and "2026-05-29T11:00:00+00:00" in log
    assert now.isoformat() in log, "resolver-now signal must be recorded for forensics"
    assert "PCR-2b" in log


# ---------------------------------------------------------------------------
# AC-1 / AC-2 — resolve_vault_claim_conflict integration (suspicious → STOP)
# ---------------------------------------------------------------------------

def test_suspicious_ordering_returns_stop_with_skew_reason(tmp_path) -> None:
    """Integration: a future-dated strict-newer winner → STOP(VAULT_CLAIM) with skew reason.

    The guard returns at Step 2.5 before any git-stage read, so no rebase staging
    is needed — only the injected early `now` makes the 2026-05-29 winner future-dated.
    """
    early_now = datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    diag = _diag(
        claim_history=(
            _claim("add-foo", "alice <a@example.com>", "2026-05-29T12:00:00+00:00", 2),
            _claim("add-foo", "bob <b@example.com>", "2026-05-29T10:00:00+00:00", 3),
        ),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path, now=early_now)
    assert result.action == "STOP"
    assert result.conflict_class == ConflictClass.VAULT_CLAIM
    assert "clock-skew" in result.reason.lower() and "PCR-2b" in result.reason
    # forensic audit entry written
    # slice-115 ([[ADR-107]] — the flip): use the LIVE module attr `_pcr._AUDIT_LOG_PATH`
    # (re-derived to "architecture/…" relative by the autouse pin), NOT the module-level import
    # `_AUDIT_LOG_PATH` which froze to the live (post-flip ABSOLUTE external) value at test import —
    # `tmp_path / <absolute>` resolves to the live external log, not this fixture.
    log = (tmp_path / _pcr._AUDIT_LOG_PATH).read_text(encoding="utf-8")
    assert "clock-skew STOP" in log


# ---------------------------------------------------------------------------
# AC-3 — happy path: a plausibly-ordered (past) winner still auto-resolves
# ---------------------------------------------------------------------------

def test_plausible_ordering_still_auto_resolves_strict_newer(tmp_path) -> None:
    """No regression: a past-dated winner (vs resolver-now) resolves to APPLIED exactly
    as PCR-2a does today. Injected far-future `now` makes both 2026 stamps plausibly-past."""
    far_future = datetime.datetime(2099, 1, 1, 0, 0, 0, tzinfo=UTC)
    text_2 = _well_formed_queue("alice <a@example.com>", "2026-05-29T12:00:00+00:00")
    text_3 = _well_formed_queue("bob <b@example.com>", "2026-05-29T10:00:00+00:00")
    _stage_rebase(tmp_path, text_2, text_3)
    diag = _diag(
        claim_history=(
            _claim("add-foo", "alice <a@example.com>", "2026-05-29T12:00:00+00:00", 2),
            _claim("add-foo", "bob <b@example.com>", "2026-05-29T10:00:00+00:00", 3),
        ),
    )
    result = resolve_vault_claim_conflict(diag, repo_root=tmp_path, now=far_future)
    assert result.action == "APPLIED", (
        f"plausible past-dated winner must still resolve; got {result.action!r} / {result.reason!r}"
    )
    assert result.conflict_class == ConflictClass.VAULT_CLAIM


# ---------------------------------------------------------------------------
# AC-4 — APED-1 adversarial corpus battery (both directions)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "claimed_at, expect_suspicious",
    [
        ("2026-05-29T08:00:00+00:00", False),   # canonical past → resolves
        ("2026-05-29T12:00:00+00:00", True),    # canonical future → caught
        ("2026-05-29T08:00:00Z", False),        # Z past → resolves (version-independent)
        ("2026-05-29T12:00:00Z", True),         # Z future → caught
        ("2026-05-29T08:00:00z", False),        # /code-review M1: lowercase-z past → resolves (case-insensitive)
        ("2026-05-29T12:00:00z", True),         # lowercase-z future → caught
        ("2026-05-29T08:00:00.123456+00:00", False),  # microsecond past → resolves
        ("2026-05-29T12:00:00.123456+00:00", True),   # microsecond future → caught
        ("2026-05-29T12:00:00+0000", True),     # /code-review M2: offset-no-colon future → caught (3.11+ parse future; 3.10 fail-closed) — stable True
        ("2026-05-29 12:00:00+00:00", True),    # /code-review M2: space-separated future → caught (3.11+ parse future; 3.10 fail-closed) — stable True
        ("2026-05-29T12:00:00", True),          # B1 tz-naive → fail-closed
        ("not-a-timestamp", True),              # garbage → fail-closed
        ("", True),                             # empty → fail-closed
    ],
)
def test_aped1_battery_future_dated_winner_caught_past_resolves(claimed_at, expect_suspicious) -> None:
    now = datetime.datetime(2026, 5, 29, 10, 0, 0, tzinfo=UTC)
    winner = _claim("add-foo", "alice <a@x>", claimed_at, 2)
    reason = _winner_clock_skew_suspect(winner, now, _CLOCK_SKEW_TOLERANCE_SECONDS)
    if expect_suspicious:
        assert reason, f"{claimed_at!r} should be flagged suspicious/fail-closed"
    else:
        assert reason is None, f"{claimed_at!r} should resolve (plausible past), got {reason!r}"
