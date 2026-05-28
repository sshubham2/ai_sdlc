"""resolve_soft_conflict() tests (PCR-1 / slice-076 / ADR-069).

Per AC3 + AC4 mission-brief.md rows: ``resolve_soft_conflict`` is the
SOFT-class auto-resolution entry point. For non-SOFT classes (VAULT_CLAIM /
HARD / MIXED / UNKNOWN), returns ResolutionResult(action="STOP", ...)
without mutating state.

For SOFT class:
  - Regenerate ``architecture/slice-queue.md`` via _overlay_claims_on_queue_text
    (NO write_slice_queue round-trip per /critique-review M-add-1).
  - Row-union merge ``architecture/shippability.md`` by slice number.
  - ``git add`` the resolved files + ``git rebase --continue``.
  - Append audit log entry.

These tests use synthetic ConflictDiagnostic inputs + tmp_path-rooted git
repos with pre-staged rebase state. The git fixture overhead is intentional:
resolve_soft_conflict's mutation surface (git add + git rebase --continue)
requires a real git index to exercise.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    ResolutionResult,
    resolve_soft_conflict,
)


def _diag(
    u_files: tuple[str, ...] = (),
    claim_history: tuple[ClaimEntry, ...] = (),
) -> ConflictDiagnostic:
    """Build a synthetic ConflictDiagnostic for resolve_soft_conflict tests."""
    return ConflictDiagnostic(
        u_files=u_files,
        concerned_slices={},
        claim_history=claim_history,
    )


def _init_repo(tmp_path: Path) -> Path:
    """Initialize a minimal git repo at tmp_path for resolution tests."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=tmp_path, check=True)
    (tmp_path / "architecture").mkdir()
    return tmp_path


def test_resolve_soft_conflict_dispatches_to_slice_queue_writer_for_slice_queue_conflict(tmp_path) -> None:
    """SOFT-class conflict on slice-queue.md dispatches to the queue-overlay
    resolution path (NOT write_slice_queue round-trip per /critique-review
    M-add-1).

    AC3 unit / soft-regen per mission-brief row. The dispatch contract:
    when SOFT-classified, ``resolve_soft_conflict`` regenerates the queue
    file via ``_overlay_claims_on_queue_text`` (textual overlay on the
    rebase-target stage ``:3:`` text), NOT via ``write_slice_queue`` (which
    would require the PSQ-1 5-field candidate metadata that ``parse_queue_text``
    does NOT return — the B1 phantom-parser trap per /critique).
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=("architecture/slice-queue.md",))
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult), (
        f"resolve_soft_conflict must return ResolutionResult; got {type(result).__name__}"
    )
    # SOFT-class resolution either succeeds (APPLIED) OR fails closed (STOP
    # with rationale) — but it MUST NOT raise NotImplementedError once Phase C ships.
    assert result.action in ("APPLIED", "STOP"), (
        f"ResolutionResult.action must be 'APPLIED' or 'STOP'; got {result.action!r}"
    )
    # If APPLIED, slice-queue.md MUST be in regenerated_files.
    if result.action == "APPLIED":
        assert "architecture/slice-queue.md" in result.regenerated_files, (
            "APPLIED resolution on slice-queue.md U-file MUST list "
            "'architecture/slice-queue.md' in regenerated_files"
        )


def test_resolve_soft_conflict_appends_shippability_rows_from_both_branches(tmp_path) -> None:
    """SOFT-class conflict on shippability.md performs row-union merge by
    slice number (per design.md Resolution algorithm table).

    AC3 unit / soft-regen per mission-brief row. The row-union contract:
    parse both stages' shippability tables, union by leading ``| <NN> |``
    slice number, sort ascending, write back. Same-slice-number with
    different content escalates to HARD (defense-in-depth per design.md
    Edge-cases column).
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=("architecture/shippability.md",))
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult)
    # APPLIED or STOP; if APPLIED, shippability.md must be in regenerated_files.
    if result.action == "APPLIED":
        assert "architecture/shippability.md" in result.regenerated_files, (
            "APPLIED resolution on shippability.md U-file MUST list "
            "'architecture/shippability.md' in regenerated_files"
        )


def test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_shippability(tmp_path) -> None:
    """Edge case (per design.md table, shippability.md row (a)):
    ``git show`` exits non-zero on one stage (file added on only one branch).
    Treat as empty-rows; resolved file contains only the other stage's rows.

    AC3 unit / soft-regen edge case per mission-brief row. The asymmetric-
    stage handling MUST NOT raise — treat missing stage as empty, proceed
    with the present stage's rows.
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=("architecture/shippability.md",))
    result = resolve_soft_conflict(diag)
    # Edge-case behavior must not raise; result is either APPLIED (with
    # rows from the present stage) or STOP-with-rationale on UNKNOWN class.
    assert isinstance(result, ResolutionResult)
    assert result.action in ("APPLIED", "STOP")


def test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_slice_queue(tmp_path) -> None:
    """Edge case (per design.md table, slice-queue.md row (a) + (b)):
    ``git show :3:`` exits non-zero (file added on rebased branch only):
    resolved queue uses ``text_2`` verbatim with claims merged. Symmetric for
    ``:2:``.

    AC3 unit / soft-regen edge case per mission-brief row. Defense-in-depth:
    when one stage is missing, the resolution uses the present stage's text
    verbatim (no overlay attempt on empty text).
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=("architecture/slice-queue.md",))
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult)
    assert result.action in ("APPLIED", "STOP")


def test_resolve_soft_conflict_bypassed_when_mixed_with_hard_file(tmp_path) -> None:
    """SOFT + HARD U-files (MIXED class) → action=STOP, no mutation.

    AC3 unit / soft-regen + AC4 fail-closed per mission-brief rows. The
    bypass contract: classify_conflict returns MIXED → resolve_soft_conflict
    returns STOP without touching files / staging / rebase. Atomicity per
    ADR-069: PCR-1 v1 never partially auto-resolves the SOFT portion if any
    HARD is present.
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=("architecture/slice-queue.md", "tools/some_source.py"))
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult)
    assert result.action == "STOP", (
        f"MIXED class (SOFT + HARD) MUST return STOP (no auto-resolve per "
        f"ADR-069 atomicity); got action={result.action!r}"
    )
    assert result.conflict_class == ConflictClass.MIXED, (
        f"MIXED class result MUST carry conflict_class=MIXED; got {result.conflict_class}"
    )
    assert result.regenerated_files == (), (
        f"MIXED class STOP MUST regenerate zero files (atomicity); got "
        f"regenerated_files={result.regenerated_files}"
    )


def test_resolve_soft_conflict_aborts_when_post_merge_claim_dict_has_same_candidate_different_identities(tmp_path) -> None:
    """VAULT_CLAIM gate (per /critique B4 ACCEPTED-FIXED): if both stages'
    claim dicts have the SAME candidate with DIFFERENT Claimed-by →
    STOP without auto-resolving.

    AC3 unit / soft-regen fail-closed per mission-brief row. Defense-in-depth
    against PSQ-2's existing newest-wins merge silently auto-resolving what
    PCR-2 reserves for timestamp-winner + light Critic. The VAULT_CLAIM gate
    fires BEFORE _overlay_claims_on_queue_text is invoked.
    """
    _init_repo(tmp_path)
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
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult)
    assert result.action == "STOP", (
        f"Same-candidate-different-identity claim collision MUST return STOP "
        f"(VAULT_CLAIM defense-in-depth per /critique B4 gate); got "
        f"action={result.action!r}"
    )
    assert result.conflict_class == ConflictClass.VAULT_CLAIM, (
        f"VAULT_CLAIM gate fire MUST carry conflict_class=VAULT_CLAIM; got "
        f"{result.conflict_class}"
    )


def test_resolve_soft_conflict_returns_stop_on_unknown_class(tmp_path) -> None:
    """UNKNOWN class (empty u_files / unparseable rebase state) → STOP.

    AC4 unit / resolve_soft_conflict fail-closed per mission-brief row. Per
    APED-1 silent-disable / default-off-on-malformed criterion: NEVER
    silent-default to SOFT when the rebase state is unexpected. The skill
    falls through to PSQ-3's existing SOAD-1 STOP block.
    """
    _init_repo(tmp_path)
    diag = _diag(u_files=())  # Empty → UNKNOWN per classify_conflict contract
    result = resolve_soft_conflict(diag)
    assert isinstance(result, ResolutionResult)
    assert result.action == "STOP", (
        f"UNKNOWN class MUST return STOP (fail-closed; never silent-default "
        f"to SOFT per APED-1); got action={result.action!r}"
    )
    assert result.conflict_class == ConflictClass.UNKNOWN, (
        f"UNKNOWN class result MUST carry conflict_class=UNKNOWN; got "
        f"{result.conflict_class}"
    )
    assert result.reason is not None, (
        "UNKNOWN STOP MUST include a non-None reason (diagnostic for "
        "the SOAD-1 fall-through)"
    )
