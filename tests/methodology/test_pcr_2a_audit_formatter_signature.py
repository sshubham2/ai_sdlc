"""Pin slice-079 Fix O (slice-078 m1 + /critique-review M-add-1): `_format_vault_claim_audit_entry` 6-arg signature.

Slice-078 m1: formatter re-derives winner/loser from `diag.claim_history` while resolver already has them
in scope at Step 1+2 — DRY violation at signature boundary.
/critique-review M-add-1: design.md mis-cited pre-fix signature as 2-arg; reality is 4-arg
`(diag, result, timestamp, head_sha)`. Fix O extends to 6-arg + computes winner/loser inside
`_append_audit_log` (existing scope near L1270-1277) before dispatch.
"""
from __future__ import annotations

import inspect

import tools.parallel_conflict_resolver as pcr


def test_format_vault_claim_audit_entry_signature_is_6_arg() -> None:
    """Fix O: signature includes winner + loser params in addition to existing 4 args."""
    sig = inspect.signature(pcr._format_vault_claim_audit_entry)
    params = list(sig.parameters)
    assert "diag" in params, "Fix O regression: diag param missing"
    assert "result" in params, "Fix O regression: result param missing"
    assert "timestamp" in params, "Fix O regression: timestamp param missing (pre-fix shape preserved)"
    assert "head_sha" in params, "Fix O regression: head_sha param missing (pre-fix shape preserved)"
    assert "winner" in params, (
        "Fix O regression: winner param not added; formatter still re-derives from diag.claim_history "
        "(slice-078 m1 DRY violation returns)"
    )
    assert "loser" in params, "Fix O regression: loser param not added"
    assert len(params) == 6, f"Fix O regression: expected 6 params, got {len(params)} ({params})"


def test_append_audit_log_public_3_arg_surface_unchanged() -> None:
    """Fix O: _append_audit_log signature stays 3-arg public per M-add-1 ACCEPTED-FIXED.

    Winner/loser computation lives INSIDE _append_audit_log's existing scope (alongside the existing
    timestamp + head_sha computations), NOT passed in by resolver callers. Public surface preserved.
    """
    sig = inspect.signature(pcr._append_audit_log)
    params = list(sig.parameters)
    assert params == ["repo_root", "diag", "result"], (
        f"Fix O regression / M-add-1 regression: _append_audit_log public surface widened from 3-arg "
        f"to {params}; widening would require ADR per /critique-review M-add-1 ACCEPTED-FIXED rationale"
    )


def test_formatter_uses_passed_winner_loser_not_diag_claim_history() -> None:
    """Fix O behavioral discriminator (design.md test-plan row O / code-review M1).

    The formatter must render the PASSED-IN winner/loser, never re-derive from
    diag.claim_history. Constructed with an EMPTY claim_history: a regression that
    re-introduces `_collect_same_candidate_different_identity(diag.claim_history)` inside
    the formatter body (re-creating the slice-078 m1 DRY violation Fix O removes) would
    render candidate_name '(unknown)' + '(unavailable)' here and FAIL — the structural
    signature/source pins above cannot discriminate the DRY-satisfied state from the
    DRY-violated state, so this behavioral assertion is the real FAIL→PASS contrast.
    """
    diag = pcr.ConflictDiagnostic(u_files=(), concerned_slices={}, claim_history=())
    result = pcr.ResolutionResult(
        action="APPLIED",
        conflict_class=pcr.ConflictClass.VAULT_CLAIM,
        regenerated_files=("architecture/slice-queue.md",),
        reason="vault-claim-resolved; replacement=none-available",
    )
    winner = pcr.ClaimEntry(
        candidate_name="add-foo", claimed_by="alice <a@x>",
        claimed_at="2026-05-29T10:00:00Z", branch_stage=3,
    )
    loser = pcr.ClaimEntry(
        candidate_name="add-foo", claimed_by="bob <b@x>",
        claimed_at="2026-05-29T09:00:00Z", branch_stage=2,
    )
    entry = pcr._format_vault_claim_audit_entry(
        diag, result, "2026-05-29T10:00:00Z", "abc123de", winner, loser
    )
    assert "**Candidate name**: add-foo" in entry, (
        "Fix O regression: candidate_name must come from winner.candidate_name, NOT be "
        "re-derived from the (empty) diag.claim_history (which would yield '(unknown)')"
    )
    assert "**Winner Claimed-by**: alice <a@x>" in entry, "winner identity must be the passed-in value"
    assert "**Winner Claimed-at**: 2026-05-29T10:00:00Z" in entry
    assert "**Loser Claimed-by**: bob <b@x>" in entry
    assert "(unavailable)" not in entry, (
        "Fix O regression: passed winner/loser must render real values, not the "
        "defensive '(unavailable)' fallback (which fires only when winner/loser are None)"
    )


def test_unavailable_branch_kept_with_pragma_no_cover() -> None:
    """Fix O / /critique M2 ACCEPTED-FIXED: defensive `(unavailable)` branch kept with pragma:no-cover."""
    src = inspect.getsource(pcr._format_vault_claim_audit_entry)
    assert "(unavailable)" in src, (
        "Fix O regression / M2 regression: (unavailable) defensive fallback silently deleted "
        "instead of kept with pragma:no-cover marker"
    )
    assert "pragma: no cover" in src or "pragma:no cover" in src, (
        "Fix O regression / M2 regression: (unavailable) branch lacks `# pragma: no cover` marker"
    )
