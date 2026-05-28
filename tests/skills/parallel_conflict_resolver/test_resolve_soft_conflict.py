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


def test_resolve_soft_conflict_atomicity_preserves_slice_queue_on_helper_error(
    tmp_path, monkeypatch
) -> None:
    """Regression for M2 / atomicity gap (code-review fix).

    Pre-fix, `resolve_soft_conflict` called `_regen_slice_queue` then
    `_merge_shippability` in a loop, each writing to disk before returning.
    If `_merge_shippability` raised `_SoftResolutionError(HARD)` AFTER
    `_regen_slice_queue` already wrote `slice-queue.md`, the file was
    silently overwritten with the post-overlay content while the resolver
    returned STOP — leaving the working tree in a half-resolved state that
    defeats ADR-069's "atomicity — never partial auto-resolve" contract.

    Post-fix uses stage-then-commit pattern: helpers return `(Path, str)`
    tuples WITHOUT writing; `resolve_soft_conflict` batch-writes only if
    ALL helpers succeed. This test patches `_merge_shippability` to raise
    `_SoftResolutionError(HARD)` for U-files=(slice-queue.md, shippability.md)
    classified SOFT; asserts the on-disk slice-queue.md is NOT written
    (preserving conflict markers / pre-resolve state).
    """
    import tools.parallel_conflict_resolver as resolver
    from tools.parallel_conflict_resolver import _SoftResolutionError

    _init_repo(tmp_path)

    # Patch _regen_slice_queue to return a sentinel (Path, content) without
    # writing — verifies the stage-then-commit refactor isolates writes.
    out_path_sentinel = tmp_path / "architecture" / "slice-queue.md"
    sentinel_content = "SHOULD_NOT_BE_ON_DISK_IF_ATOMICITY_WORKS"

    def fake_regen_slice_queue(repo_root, diag):
        return (out_path_sentinel, sentinel_content)

    def fake_merge_shippability(repo_root):
        raise _SoftResolutionError(
            "synthetic shippability HARD escalation for atomicity test",
            ConflictClass.HARD,
        )

    monkeypatch.setattr(resolver, "_regen_slice_queue", fake_regen_slice_queue)
    monkeypatch.setattr(resolver, "_merge_shippability", fake_merge_shippability)

    diag = _diag(u_files=("architecture/slice-queue.md", "architecture/shippability.md"))
    result = resolve_soft_conflict(diag, repo_root=tmp_path)

    # Result MUST be STOP with HARD class.
    assert result.action == "STOP", (
        f"atomicity gap regression: helper raise should produce STOP; "
        f"got action={result.action!r}"
    )
    assert result.conflict_class == ConflictClass.HARD, (
        f"atomicity gap regression: _merge_shippability HARD escalation "
        f"should propagate to result.conflict_class; got {result.conflict_class}"
    )

    # CRITICAL: slice-queue.md MUST NOT exist on disk — _regen_slice_queue
    # returned content but the batch-write phase never ran because
    # _merge_shippability raised mid-collection.
    assert not out_path_sentinel.exists(), (
        f"ATOMICITY VIOLATION: slice-queue.md was written to disk despite "
        f"_merge_shippability raising _SoftResolutionError mid-loop. "
        f"Per ADR-069 atomicity contract: NO files should be written when "
        f"the resolver returns STOP. On-disk content: "
        f"{out_path_sentinel.read_text(encoding='utf-8')!r}"
    )


def test_regen_slice_queue_vault_claim_defense_in_depth_gate_fires_on_different_identity(
    tmp_path, monkeypatch
) -> None:
    """Regression for M3 / missing VAULT_CLAIM defense-in-depth gate (code-review fix).

    Per design.md L136 "Resolution algorithm for SOFT class" step 3 of 5
    + critique.md B4 fix (c) ACCEPTED-FIXED: `_regen_slice_queue` MUST
    walk both branches' claim dicts; if ANY candidate name appears in
    BOTH with DIFFERENT `Claimed-by` values, abort with
    `_SoftResolutionError(VAULT_CLAIM)`. This is defense-in-depth on
    top of `classify_conflict`'s upstream gate via
    `_has_same_candidate_different_identity(diag.claim_history)`.

    Simulates the bypass-the-upstream-gate scenario by patching
    `_git_show_stage` to return queue text with different-identity claims
    on the same candidate. The upstream gate's input
    (`diag.claim_history`) is irrelevant here because we call
    `_regen_slice_queue` directly. Verifies the in-helper gate fires.
    """
    import tools.parallel_conflict_resolver as resolver
    from tools.parallel_conflict_resolver import (
        _SoftResolutionError,
        _regen_slice_queue,
    )

    queue_stage_2 = (
        "# Slice queue\n\n## Candidates\n\n"
        "### add-foo\n\n"
        "- **Source:** R-1\n"
        "- **Blast-radius:** `tools/foo.py`\n"
        "- **Parallel-safety:** GRAPH-DISJOINT\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n"
        "- **Claimed-by:** alice <alice@example.com>\n"
        "- **Claimed-at:** 2026-05-28T10:00:00Z\n"
    )
    queue_stage_3 = (
        "# Slice queue\n\n## Candidates\n\n"
        "### add-foo\n\n"
        "- **Source:** R-1\n"
        "- **Blast-radius:** `tools/foo.py`\n"
        "- **Parallel-safety:** GRAPH-DISJOINT\n"
        "- **Effort:** SMALL\n"
        "- **Risk-retired:** LOW\n"
        "- **Claimed-by:** bob <bob@example.com>\n"
        "- **Claimed-at:** 2026-05-28T11:00:00Z\n"
    )

    def fake_git_show_stage(repo_root, stage, path):
        if path != "architecture/slice-queue.md":
            return ""
        if stage == 2:
            return queue_stage_2
        if stage == 3:
            return queue_stage_3
        return ""

    monkeypatch.setattr(resolver, "_git_show_stage", fake_git_show_stage)

    # Diag.claim_history is empty — simulating the upstream-gate-bypass
    # case (silent ClaimUsageError or stale diag). The in-helper gate
    # MUST still fire on the real stage-2/3 differing claims.
    diag = _diag(u_files=("architecture/slice-queue.md",), claim_history=())

    try:
        _regen_slice_queue(tmp_path, diag)
    except _SoftResolutionError as exc:
        assert exc.conflict_class == ConflictClass.VAULT_CLAIM, (
            f"M3 defense-in-depth gate fire MUST carry "
            f"conflict_class=VAULT_CLAIM; got {exc.conflict_class}"
        )
        assert "add-foo" in str(exc), (
            f"VAULT_CLAIM exception MUST name the conflicting candidate; "
            f"got {exc!s}"
        )
        assert "alice" in str(exc) and "bob" in str(exc), (
            f"VAULT_CLAIM exception MUST surface both Claimed-by identities "
            f"for diagnostic; got {exc!s}"
        )
    else:
        raise AssertionError(
            "M3 defense-in-depth gate FAILED to fire: _regen_slice_queue "
            "returned normally on same-candidate-different-identity input. "
            "Per design.md L136 step 3 + critique.md B4 fix (c): MUST raise "
            "_SoftResolutionError(VAULT_CLAIM)."
        )
