"""classify_conflict() 5-way classification tests (PCR-1 / slice-076 / ADR-069).

Per AC4 mission-brief.md rows + design.md § Public functions: ``classify_conflict``
returns one of:

  - ``SOFT``        — all U-files in 2-member _SOFT_FILE_SET, AND no
                      same-candidate-different-identity claim collision.
  - ``VAULT_CLAIM`` — sole U-file is slice-queue.md AND same-candidate
                      appears in both branches with different Claimed-by.
  - ``HARD``        — any U-file is a source file / not in SOFT-set.
  - ``MIXED``       — SOFT + non-SOFT U-files coexist (atomicity → treat as
                      non-auto-resolvable).
  - ``UNKNOWN``     — fail-closed; empty u_files despite rebase claim, or
                      malformed inputs.

Synthetic ``ConflictDiagnostic`` fixtures bypass the git-fixture overhead
that ``diagnose_conflict`` requires — these unit tests target the
classification algorithm directly given a ConflictDiagnostic input.
"""
from __future__ import annotations

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    classify_conflict,
)


def _diag(
    u_files: tuple[str, ...] = (),
    claim_history: tuple[ClaimEntry, ...] = (),
) -> ConflictDiagnostic:
    """Build a minimal ConflictDiagnostic for classification tests.

    The concerned_slices map is irrelevant to classify_conflict (it consumes
    u_files + claim_history only); we pass an empty dict.
    """
    return ConflictDiagnostic(
        u_files=u_files,
        concerned_slices={},
        claim_history=claim_history,
    )


def test_classify_conflict_returns_soft_when_all_u_files_are_in_two_member_soft_set() -> None:
    """All U-files in 2-member SOFT-set + no claim collision → SOFT.

    Real-corpus input per mission-brief APED-1 battery: synthetic conflict
    touching ONLY slice-queue.md + shippability.md.
    """
    diag = _diag(u_files=("architecture/slice-queue.md", "architecture/shippability.md"))
    result = classify_conflict(diag)
    assert result == ConflictClass.SOFT, (
        f"All U-files in SOFT-set + no claim collision → SOFT; got {result}"
    )


def test_classify_conflict_returns_hard_when_any_source_file_present() -> None:
    """Any source file in U-files → HARD.

    Real-corpus input per mission-brief APED-1 battery: ONLY a source file
    (expected HARD). Also covers the dotfile/hidden-path default-deny: if
    a path is not in the 2-member SOFT-set and not VAULT_CLAIM, it's HARD.
    """
    diag = _diag(u_files=("tools/some_module.py",))
    result = classify_conflict(diag)
    assert result == ConflictClass.HARD, (
        f"Source-file U-entry → HARD (default-deny for non-SOFT-set paths); got {result}"
    )


def test_classify_conflict_returns_mixed_when_soft_and_hard_coexist() -> None:
    """SOFT + HARD U-files coexist → MIXED (atomicity — never partial auto-resolve).

    Real-corpus input per mission-brief APED-1 battery: SOFT+HARD mix.
    Per ADR-069 § Decision: MIXED is treated as HARD for resolution
    purposes; PCR-1 v1 never auto-resolves the SOFT portion if any HARD is
    present.
    """
    diag = _diag(u_files=("architecture/slice-queue.md", "tools/some_module.py"))
    result = classify_conflict(diag)
    assert result == ConflictClass.MIXED, (
        f"SOFT+HARD coexist → MIXED (per ADR-069 atomicity contract); got {result}"
    )


def test_classify_conflict_returns_mixed_when_soft_and_vault_claim_coexist() -> None:
    """SOFT (shippability.md) + VAULT_CLAIM (slice-queue.md same-candidate-
    different-identity) coexist → MIXED.

    Real-corpus input per mission-brief APED-1 battery: SOFT+VAULT_CLAIM mix.
    Per /critique M4 ACCEPTED-FIXED disambiguation: SOFT+VAULT_CLAIM and
    SOFT+HARD both classify as MIXED (atomicity).
    """
    diag = _diag(
        u_files=("architecture/slice-queue.md", "architecture/shippability.md"),
        claim_history=(
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="alice <alice@example.com>",
                claimed_at="2026-05-28T10:00:00Z",
                branch_stage=2,
            ),
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="bob <bob@example.com>",
                claimed_at="2026-05-28T11:00:00Z",
                branch_stage=3,
            ),
        ),
    )
    result = classify_conflict(diag)
    assert result == ConflictClass.MIXED, (
        f"SOFT+VAULT_CLAIM coexist → MIXED (per /critique M4 disambiguation); "
        f"got {result}"
    )


def test_classify_conflict_returns_vault_claim_when_same_candidate_claimed_by_different_identities_across_branches() -> None:
    """Sole U-file is slice-queue.md + same-candidate-different-identity claim
    → VAULT_CLAIM (per /critique B4 ACCEPTED-FIXED gate).

    Real-corpus input per mission-brief APED-1 battery: same-candidate-
    different-identity claim collision. Defense-in-depth: PSQ-2's existing
    newest-wins merge would silently auto-resolve what PCR-2 reserves for
    timestamp-winner + light Critic; the VAULT_CLAIM gate defeats this here.
    """
    diag = _diag(
        u_files=("architecture/slice-queue.md",),
        claim_history=(
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="alice <alice@example.com>",
                claimed_at="2026-05-28T10:00:00Z",
                branch_stage=2,
            ),
            ClaimEntry(
                candidate_name="add-foo",
                claimed_by="bob <bob@example.com>",
                claimed_at="2026-05-28T11:00:00Z",
                branch_stage=3,
            ),
        ),
    )
    result = classify_conflict(diag)
    assert result == ConflictClass.VAULT_CLAIM, (
        f"slice-queue.md sole U-file + same-candidate-different-identity → "
        f"VAULT_CLAIM (per /critique B4 gate); got {result}"
    )


def test_classify_conflict_returns_unknown_when_rebase_state_empty() -> None:
    """Empty u_files (rebase claim but no U-entries) → UNKNOWN (fail-closed).

    Real-corpus input per mission-brief APED-1 battery: empty rebase state
    (expected UNKNOWN — fail-closed). Per APED-1 silent-disable / default-
    off-on-malformed criterion: NEVER silent-default to SOFT.

    The contract: classify_conflict MUST return UNKNOWN (not SOFT-by-vacuous-
    truth) when there are zero U-files to classify. A silent SOFT classification
    on empty u_files would cause resolve_soft_conflict to no-op + git rebase
    --continue with no actual resolution, masking the underlying anomaly.
    """
    diag = _diag(u_files=())
    result = classify_conflict(diag)
    assert result == ConflictClass.UNKNOWN, (
        f"Empty u_files → UNKNOWN (fail-closed; never silent-default to SOFT "
        f"per APED-1); got {result}"
    )
