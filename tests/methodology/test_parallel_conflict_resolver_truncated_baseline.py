"""PCR-1 SOFT-regen claim-loss-by-truncation gate — slice-085 / R-24 / ADR-077.

slice-082 (ADR-074) added the SOFT equivalence guard `_verify_soft_equivalence`;
its Invariant #1 *exempts* orphan claims (a claimed candidate absent from the
baseline) from STOP, emitting a WARN instead — because at the name level that is
the legitimate top-10-churn-drop case. R-24 named the residual hole: a baseline
truncated/corrupt mid-write is INDISTINGUISHABLE, at the name level, from churn.

slice-085 adds the discriminating signal the name comparison lacked: the baseline
blob's STRUCTURAL INTEGRITY. When a claimed candidate is dropped from the baseline
AND the baseline is *tail-truncation-shaped* (its LAST `### ` block is missing >=1
of the 5 canonical PSQ-1 field labels), the orphan WARN is escalated to a
fail-closed STOP (claim-loss-by-corruption). Well-formed baselines keep the
WARN-only churn semantics (no false-STOP).

TRI-1 ratified (2026-05-30): Option 4 (orphan-gated) + (a) document M1 as residual.

These tests drive the REAL resolver against REAL tmp-repo rebase-conflict fixtures
(APED-1 execution, not reasoned-about), plus direct unit tests of the new
`_baseline_is_truncation_shaped` helper.
"""
from __future__ import annotations

import subprocess

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py
import tools._vault_git as _vgit
import tools.parallel_conflict_resolver as _pcr

# slice-110 / [[ADR-101]]: location-agnostic VAULT_ROOT pin (see autouse_pin).
_pin_vault = vi.autouse_pin(
    _vgit, _pcr,
    derived=[(_pcr, "_AUDIT_LOG_PATH",
              lambda vr: vr / "parallel-conflict-resolution-log.md")],
)

from tools import slice_queue_writer
from tools.parallel_conflict_resolver import (
    ConflictClass,
    _baseline_is_truncation_shaped,
    classify_conflict,
    diagnose_conflict,
    resolve_soft_conflict,
)

_AUDIT_LOG = "architecture/parallel-conflict-resolution-log.md"
_QUEUE_REL = "architecture/slice-queue.md"
_SHIP_REL = "architecture/shippability.md"


# ---------------------------------------------------------------------------
# Fixture helpers (mirrors test_pcr_1_soft_regen_equivalence_guard.py:
#   branchA == stage 3 == regen baseline; master == stage 2 == claim source)
# ---------------------------------------------------------------------------

def _git(tmp_path, *args, check=True):
    return subprocess.run(["git", *args], cwd=tmp_path, check=check, capture_output=True, text=True)


def _candidate(name: str, *, claimed_by: str | None = None, claimed_at: str | None = None,
               risk_retired: bool = True) -> str:
    """One PSQ-1 candidate block. risk_retired=False omits the Risk-retired line —
    which (as the LAST block) is the truncation-shaped signature this slice keys on."""
    lines = [
        f"### {name}\n",
        "- **Source:** synthetic\n",
        "- **Blast-radius:** `nothing`\n",
        "- **Parallel-safety:** NON-OVERLAPPING\n",
        "- **Effort:** SMALL\n",
    ]
    if risk_retired:
        lines.append("- **Risk-retired:** LOW\n")
    if claimed_by and claimed_at:
        lines.append(f"- **Claimed-by:** {claimed_by}\n")
        lines.append(f"- **Claimed-at:** {claimed_at}\n")
    return "".join(lines)


def _queue(*candidate_blocks: str) -> str:
    return "# Slice queue\n\n## Candidates\n\n" + "\n".join(candidate_blocks)


def _shippability(rows: tuple[str, ...] = ()) -> str:
    head = (
        "# Shippability catalog\n\n"
        "Single source of truth for must-never-regress claims.\n\n"
        "| # | Claim | Command |\n|---|-------|---------|\n"
    )
    body = "".join(r if r.endswith("\n") else r + "\n" for r in rows)
    return head + body


def _stage_rebase(tmp_path, rel_path: str, *, branchA: str, master: str):
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# stub\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    target.write_text(branchA, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    target.write_text(master, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)


def _stage_rebase_two(tmp_path, *, branchA: dict[str, str], master: dict[str, str]):
    """Like _stage_rebase but conflicts on TWO files (both in the SOFT allowlist),
    so an atomic-STOP assertion can verify NEITHER file is mutated."""
    rels = set(branchA) | set(master)
    _git(tmp_path, "init", "-q", "-b", "master")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "test")
    for rel in rels:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# stub\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "init")
    _git(tmp_path, "checkout", "-q", "-b", "branchA")
    for rel, content in branchA.items():
        (tmp_path / rel).write_text(content, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "A")
    _git(tmp_path, "checkout", "-q", "master")
    for rel, content in master.items():
        (tmp_path / rel).write_text(content, encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "B")
    _git(tmp_path, "checkout", "-q", "branchA")
    _git(tmp_path, "rebase", "master", check=False)


def _resolve(tmp_path):
    diag = diagnose_conflict(tmp_path)
    return diag, resolve_soft_conflict(diag, tmp_path)


# A baseline (stage 3) whose LAST block is missing Risk-retired = truncation-shaped,
# AND which has DROPPED the claimed `add-foo` heading entirely (orphan claim).
def _tail_truncated_dropping(name_present: str) -> str:
    return _queue(_candidate(name_present, risk_retired=False))


# ===========================================================================
# AC-1 — claim-loss from a tail-truncation-shaped baseline STOPs (Option 4)
# ===========================================================================

def test_soft_stops_on_orphan_claim_drop_from_tail_truncated_baseline(tmp_path) -> None:
    """master(stage2) claims `add-foo`; baseline(stage3/branchA) has DROPPED add-foo's
    heading AND its last surviving block (`add-bar`) is missing Risk-retired →
    tail-truncation-shaped. The orphan-claim drop on a truncation-shaped baseline is
    claim-loss-by-corruption → fail-closed STOP (escalates the pre-fix WARN-only).
    RED before the wiring lands (pre-fix this WARNs and APPLIES)."""
    branchA = _tail_truncated_dropping("add-bar")          # truncation-shaped, add-foo gone
    master = _queue(
        _candidate("add-foo", claimed_by="alice <a@example.com>",
                   claimed_at="2026-05-29T12:00:00+00:00"),
        _candidate("add-bar"),
    )
    _stage_rebase(tmp_path, _QUEUE_REL, branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "STOP", (
        "claim-loss from a tail-truncation-shaped baseline must STOP (R-24/Option 4)"
    )
    assert "truncat" in (result.reason or "").lower()
    # audit row names the integrity failure
    log = (tmp_path / _AUDIT_LOG).read_text(encoding="utf-8")
    assert "truncat" in log.lower()


def test_baseline_truncation_helper_is_tail_specific_not_whole_file_scan() -> None:
    """The helper keys ONLY on the LAST block (a truncation cuts the tail). A complete
    LAST block preceded by an incomplete EARLIER block (legacy / hand-edit) must NOT trip
    the gate (bounds the false-STOP per /critique M1)."""
    # last block complete, an earlier block missing Risk-retired → NOT truncation-shaped
    earlier_malformed = _queue(
        _candidate("add-foo", risk_retired=False),   # incomplete, but NOT the tail
        _candidate("add-bar"),                        # complete tail
    )
    suspect, _ = _baseline_is_truncation_shaped(earlier_malformed)
    assert suspect is False, "an incomplete EARLIER block must not be truncation-shaped"

    # last block missing Risk-retired → truncation-shaped
    tail_malformed = _queue(
        _candidate("add-foo"),                        # complete
        _candidate("add-bar", risk_retired=False),    # incomplete tail
    )
    suspect, reason = _baseline_is_truncation_shaped(tail_malformed)
    assert suspect is True and reason
    assert "Risk-retired" in reason


# ===========================================================================
# AC-2 — orphan claim dropped from a WELL-FORMED baseline → WARN + auto-merge
# ===========================================================================

def test_orphan_claim_drop_from_wellformed_baseline_warns_and_automerges(tmp_path, capfd) -> None:
    """A claimed candidate absent from a fully WELL-FORMED baseline is legitimate top-10
    churn → preserve the WARN-only behaviour and APPLY (no false-STOP, Option 4 happy path)."""
    branchA = _queue(_candidate("add-bar"))            # well-formed, complete; add-foo dropped
    master = _queue(
        _candidate("add-foo", claimed_by="alice <a@example.com>",
                   claimed_at="2026-05-29T12:00:00+00:00"),
        _candidate("add-bar"),
    )
    _stage_rebase(tmp_path, _QUEUE_REL, branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "APPLIED", (
        "orphan claim drop from a WELL-FORMED baseline must NOT STOP (legitimate churn)"
    )
    err = capfd.readouterr().err
    assert "cross-stage-claim-drop" in err


# ===========================================================================
# AC-3 — a legitimately-short WELL-FORMED baseline auto-merges (no false-STOP)
# ===========================================================================

def test_wellformed_short_baseline_automerges_no_false_stop(tmp_path) -> None:
    """A short but well-formed baseline (clean ending, all blocks complete) on a regen
    that preserves the claim must APPLY — no false-STOP on a healthy short queue."""
    claim = dict(claimed_by="alice <a@example.com>", claimed_at="2026-05-29T12:00:00+00:00")
    branchA = _queue(_candidate("add-foo", **claim))            # short, well-formed, claim kept
    master = _queue(_candidate("add-foo", **claim), _candidate("add-bar"))
    _stage_rebase(tmp_path, _QUEUE_REL, branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "APPLIED"
    resolved = (tmp_path / _QUEUE_REL).read_text(encoding="utf-8")
    assert "alice <a@example.com>" in resolved


# ===========================================================================
# AC-4a — the pre-existing overlay-silent-drop STOP (:1775-1783) is UNCHANGED
# ===========================================================================

def test_overlay_silent_drop_still_stops_1775_1783(tmp_path) -> None:
    """Regression pin: a claimed candidate whose heading SURVIVES in the baseline but whose
    block is malformed (no Risk-retired) so the overlay cannot re-emit the claim must still
    STOP at the pre-existing claimed-WITH-heading loop. This slice does NOT touch that loop;
    it must not regress (corrected per /critique M1 — this is overlay-silent-drop, NOT
    claim-line truncation)."""
    branchA = _queue(_candidate("add-foo", risk_retired=False))   # heading survives, malformed
    master = _queue(_candidate("add-foo", claimed_by="alice <a@example.com>",
                               claimed_at="2026-05-29T12:00:00+00:00"))
    _stage_rebase(tmp_path, _QUEUE_REL, branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "STOP"
    assert "equivalence-guard" in (result.reason or "")


# ===========================================================================
# AC-4b — the new STOP is end-to-end ATOMIC (both SOFT files pending, none mutated)
# ===========================================================================

def test_stop_is_atomic_via_resolve_soft_conflict_both_soft_files_pending(tmp_path) -> None:
    """With slice-queue.md (truncation-shaped, claim-dropping) AND shippability.md both
    pending, the truncation STOP must fire BEFORE any write — neither file mutated, rebase
    still in progress, no regenerated files."""
    # shippability conflicts on DISTINCT row numbers → SOFT row-union (benign); the ONLY
    # STOP cause must be the slice-queue truncation gate, so this test genuinely exercises
    # the new wiring (not a spurious _merge_shippability HARD same-number escalation).
    branchA = {
        _QUEUE_REL: _tail_truncated_dropping("add-bar"),
        _SHIP_REL: _shippability(rows=("| 80 | claim80 | cmd80 |",)),
    }
    master = {
        _QUEUE_REL: _queue(
            _candidate("add-foo", claimed_by="alice <a@example.com>",
                       claimed_at="2026-05-29T12:00:00+00:00"),
            _candidate("add-bar"),
        ),
        _SHIP_REL: _shippability(rows=("| 81 | claim81 | cmd81 |",)),
    }
    _stage_rebase_two(tmp_path, branchA=branchA, master=master)
    diag, result = _resolve(tmp_path)
    assert classify_conflict(diag) is ConflictClass.SOFT
    assert result.action == "STOP"
    assert result.regenerated_files == ()
    # rebase still in progress
    assert (tmp_path / ".git" / "rebase-merge").exists() or (tmp_path / ".git" / "rebase-apply").exists()
    # both U-files still carry conflict markers (not overwritten)
    for rel in (_QUEUE_REL, _SHIP_REL):
        content = (tmp_path / rel).read_text(encoding="utf-8")
        assert "<<<<<<<" in content and ">>>>>>>" in content, f"{rel} was mutated despite STOP"


# ===========================================================================
# AC-4d — empty / placeholder / CRLF / trailing-space (APED-1 battery, no false-STOP)
# ===========================================================================

def test_empty_and_placeholder_baseline_not_truncation_shaped() -> None:
    """An empty baseline or the `_(no candidates)_` placeholder is a legitimate queue, NOT
    truncation-shaped — must not false-STOP (per /critique m3)."""
    for text in ("", "# Slice queue\n\n## Candidates\n\n_(no candidates)_\n"):
        suspect, reason = _baseline_is_truncation_shaped(text)
        assert suspect is False, f"empty/placeholder must not be truncation-shaped: {text!r}"
        assert reason is None
    # the literal placeholder constant must be honoured
    assert slice_queue_writer._NO_CANDIDATES_PLACEHOLDER == "_(no candidates)_"


def test_truncation_helper_normalizes_crlf_and_trailing_space_heading() -> None:
    """The helper must normalize CRLF (mirroring parse_queue_text) and tolerate a
    trailing-space heading — a CRLF complete queue is NOT suspect; a CRLF tail-truncated
    queue IS suspect (per /critique m3 APED-1 battery)."""
    complete = _queue(_candidate("add-foo"), _candidate("add-bar"))
    suspect_lf, _ = _baseline_is_truncation_shaped(complete)
    suspect_crlf, _ = _baseline_is_truncation_shaped(complete.replace("\n", "\r\n"))
    assert suspect_lf is False and suspect_crlf is False, "CRLF must not change the verdict"

    truncated = _queue(_candidate("add-foo"), _candidate("add-bar", risk_retired=False))
    s_lf, _ = _baseline_is_truncation_shaped(truncated)
    s_crlf, _ = _baseline_is_truncation_shaped(truncated.replace("\n", "\r\n"))
    assert s_lf is True and s_crlf is True, "a CRLF tail-truncated baseline must still be suspect"

    # trailing-space heading on a complete tail block → not suspect (heading still parsed)
    trailing = "# Slice queue\n\n## Candidates\n\n### add-foo \n" + \
        "- **Source:** synthetic\n- **Blast-radius:** `nothing`\n" + \
        "- **Parallel-safety:** NON-OVERLAPPING\n- **Effort:** SMALL\n- **Risk-retired:** LOW\n"
    s_trail, _ = _baseline_is_truncation_shaped(trailing)
    assert s_trail is False, "a complete block with a trailing-space heading must not be suspect"


# ===========================================================================
# AC-5 — single source of truth: helper reads the writer's label constant
# ===========================================================================

def test_baseline_truncation_helper_uses_writer_field_label_constant(monkeypatch) -> None:
    """The helper must derive its required labels FROM `slice_queue_writer._RENDERED_FIELD_LABELS`
    (genuine SSoT) — not a hard-coded copy. Monkeypatch the constant to add a 6th required label
    absent from a real block; the helper must then classify that previously-complete block as
    truncation-shaped, proving it reads the constant at call time."""
    real = slice_queue_writer._RENDERED_FIELD_LABELS
    complete = _queue(_candidate("add-foo"))
    assert _baseline_is_truncation_shaped(complete)[0] is False

    monkeypatch.setattr(
        slice_queue_writer, "_RENDERED_FIELD_LABELS", real + ("- **Nonexistent:**",)
    )
    suspect, reason = _baseline_is_truncation_shaped(complete)
    assert suspect is True, "helper must read the writer constant (patched 6th label not in block)"
    assert "Nonexistent" in (reason or "")
