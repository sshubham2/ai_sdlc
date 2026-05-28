"""_overlay_claims_on_queue_text() surgical-overlay tests (PCR-1 / slice-076).

Per /critique-review M-add-1 ACCEPTED-FIXED option (2): instead of round-
tripping through ``write_slice_queue`` (which requires the PSQ-1 5-field
enumeration metadata that PSQ-2's ``parse_queue_text`` does NOT return),
PCR-1's slice-queue.md resolution surgically overlays merged claim metadata
onto the rebase-target stage ``:3:`` queue text.

Contract (per design.md Resolution algorithm table):
  - For each candidate in ``queue_text`` that's also in ``merged_claims``:
      - If existing ``Claimed-by:`` + ``Claimed-at:`` lines present →
        replace them.
      - If absent → insert under the candidate's ``Risk-retired:`` line
        (PSQ-1 5-field convention: claim lines come AFTER ``Risk-retired:``).
  - Candidates in ``merged_claims`` whose names are NOT present in
    ``queue_text`` → dropped (will re-surface at next ``/slice`` regen).
"""
from __future__ import annotations

from tools.parallel_conflict_resolver import _overlay_claims_on_queue_text


_QUEUE_NO_CLAIMS = """# Slice queue

## Candidates

### add-foo

**Source**: risk-register R-13
**Blast-radius**: tools/foo.py
**Parallel-safety**: GRAPH-DISJOINT
**Effort**: SMALL
**Risk-retired**: LOW

### add-bar

**Source**: risk-register R-14
**Blast-radius**: tools/bar.py
**Parallel-safety**: GRAPH-DISJOINT
**Effort**: SMALL
**Risk-retired**: LOW
"""


_QUEUE_WITH_CLAIM_ON_FOO = """# Slice queue

## Candidates

### add-foo

**Source**: risk-register R-13
**Blast-radius**: tools/foo.py
**Parallel-safety**: GRAPH-DISJOINT
**Effort**: SMALL
**Risk-retired**: LOW
**Claimed-by**: alice <alice@example.com>
**Claimed-at**: 2026-05-28T09:00:00Z

### add-bar

**Source**: risk-register R-14
**Blast-radius**: tools/bar.py
**Parallel-safety**: GRAPH-DISJOINT
**Effort**: SMALL
**Risk-retired**: LOW
"""


def test_overlay_claims_on_queue_text_inserts_claimed_by_under_risk_retired_for_new_claim() -> None:
    """When ``queue_text`` has no claim on a candidate but ``merged_claims``
    does → insert ``Claimed-by:`` + ``Claimed-at:`` under the ``Risk-retired:`` line.

    AC3 unit / claim overlay per mission-brief row.

    The insertion-position contract (PSQ-1 5-field convention): claim lines
    appear AFTER ``Risk-retired:`` (the last of the 5 enumerated PSQ-1
    fields), so that ``parse_queue_text``'s ``after_risk_retired`` flag
    correctly accumulates them. An overlay that inserts BEFORE ``Risk-retired:``
    would break parse-after-roundtrip.
    """
    merged_claims = {
        "add-foo": {
            "claimed_by": "alice <alice@example.com>",
            "claimed_at": "2026-05-28T10:00:00Z",
        },
    }
    result = _overlay_claims_on_queue_text(_QUEUE_NO_CLAIMS, merged_claims)
    assert "**Claimed-by**: alice <alice@example.com>" in result, (
        "Overlay must insert the Claimed-by literal for the new claim"
    )
    assert "**Claimed-at**: 2026-05-28T10:00:00Z" in result, (
        "Overlay must insert the Claimed-at literal for the new claim"
    )
    # Insertion position: must appear AFTER add-foo's Risk-retired line +
    # BEFORE the next ### candidate heading (or EOF).
    risk_retired_idx = result.find("**Risk-retired**: LOW")
    claimed_by_idx = result.find("**Claimed-by**: alice")
    next_candidate_idx = result.find("### add-bar")
    assert risk_retired_idx != -1 and claimed_by_idx != -1, (
        "Overlay must produce both Risk-retired (preserved) + Claimed-by (inserted)"
    )
    assert risk_retired_idx < claimed_by_idx, (
        "Claimed-by MUST appear AFTER Risk-retired (PSQ-1 5-field convention; "
        "parse_queue_text's after_risk_retired flag requires this ordering)"
    )
    assert claimed_by_idx < next_candidate_idx, (
        "Claimed-by for add-foo MUST appear BEFORE the next ### add-bar "
        "candidate heading (insertion must stay scoped to the right candidate)"
    )


def test_overlay_claims_on_queue_text_replaces_existing_claim_with_newer_claimed_at() -> None:
    """When ``queue_text`` already has a claim AND ``merged_claims`` has a
    newer ``claimed_at`` → replace the existing claim lines.

    AC3 unit / claim overlay per mission-brief row.

    The replacement contract: PSQ-2's newest-wins semantics applies — the
    ``merged_claims`` dict represents the result of the in-helper
    newest-Claimed-at-wins union, so the overlay can trust it as
    authoritative. Existing lines are surgically replaced (not appended;
    appending would produce a malformed entry with 2 Claimed-by lines).
    """
    merged_claims = {
        "add-foo": {
            "claimed_by": "bob <bob@example.com>",
            "claimed_at": "2026-05-28T11:00:00Z",
        },
    }
    result = _overlay_claims_on_queue_text(_QUEUE_WITH_CLAIM_ON_FOO, merged_claims)
    assert "**Claimed-by**: bob <bob@example.com>" in result, (
        "Overlay must contain the NEW (replaced) Claimed-by literal"
    )
    assert "**Claimed-at**: 2026-05-28T11:00:00Z" in result, (
        "Overlay must contain the NEW (replaced) Claimed-at literal"
    )
    assert "alice <alice@example.com>" not in result, (
        "Overlay must REPLACE (not append) the existing claim — the old "
        "claimer 'alice' MUST NOT remain after replacement"
    )
    # Exactly one Claimed-by line for add-foo (no append-instead-of-replace).
    assert result.count("**Claimed-by**:") == 1, (
        f"Exactly 1 Claimed-by line expected after replacement; got "
        f"{result.count('**Claimed-by**:')} — append-instead-of-replace bug"
    )


def test_overlay_claims_on_queue_text_drops_claims_for_candidates_absent_from_target_text() -> None:
    """Candidates in ``merged_claims`` whose names are NOT in ``queue_text``
    → dropped (NOT inserted as orphan entries).

    AC3 unit / claim overlay per mission-brief row.

    The drop contract (per design.md L137 + ADR-069 § Decision):
    candidates that exist only on the rebased branch (stage 2 / ours) are
    dropped at soft-resolve and will re-surface at the next ``/slice`` regen.
    Documented behavior, not a bug — the rebase-target stage ``:3:`` is the
    candidate-list authority; PSQ-2's claim metadata may carry over names
    that have since been pruned from the queue.
    """
    merged_claims = {
        "add-foo": {
            "claimed_by": "alice <alice@example.com>",
            "claimed_at": "2026-05-28T10:00:00Z",
        },
        "add-orphan-not-in-queue": {
            "claimed_by": "bob <bob@example.com>",
            "claimed_at": "2026-05-28T11:00:00Z",
        },
    }
    result = _overlay_claims_on_queue_text(_QUEUE_NO_CLAIMS, merged_claims)
    # The valid claim (add-foo) MUST be inserted.
    assert "**Claimed-by**: alice <alice@example.com>" in result, (
        "Valid claim for add-foo (present in queue_text) MUST be inserted"
    )
    # The orphan claim MUST be dropped (not inserted as a new candidate).
    assert "add-orphan-not-in-queue" not in result, (
        "Orphan claim (candidate absent from queue_text) MUST be dropped per "
        "design.md L137 — overlay never invents new ### candidate headings"
    )
    assert "bob <bob@example.com>" not in result, (
        "Orphan claimer 'bob' MUST NOT appear in result — drop semantics"
    )
