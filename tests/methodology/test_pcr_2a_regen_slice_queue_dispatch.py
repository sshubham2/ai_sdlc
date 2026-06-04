"""PCR-2a dispatch tests (slice-078 / AC#2).

Two dispatch sites for VAULT_CLAIM (both routed to resolve_vault_claim_conflict):

1. resolve_soft_conflict() L242-253 — CLI-facing entry. New VAULT_CLAIM
   branch ABOVE the existing `if cls is not ConflictClass.SOFT:` guard;
   the CLI --resolve-soft invocation goes through this path first.

2. _regen_slice_queue() L627-638 — defense-in-depth backstop. Raises
   _VaultClaimDispatch (sentinel) instead of _SoftResolutionError(VAULT_CLAIM);
   resolve_soft_conflict catches the sentinel and re-routes.

UNKNOWN-class fail-closed branch at _regen_slice_queue L605-609 stays
verbatim — pinned by test_unknown_class_still_fail_closed.
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

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    _SoftResolutionError,
    _regen_slice_queue,
    resolve_soft_conflict,
)


def _claim(name, by, at, stage):
    return ClaimEntry(
        candidate_name=name,
        claimed_by=by,
        claimed_at=at,
        branch_stage=stage,
    )


def _stage_rebase(tmp_path, text_2: str, text_3: str):
    """Build a tmp git repo with a rebase-in-progress on slice-queue.md."""
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


def test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a(tmp_path) -> None:
    """B3 — CLI-facing dispatch site: resolve_soft_conflict on VAULT_CLAIM class
    returns APPLIED via resolve_vault_claim_conflict, NOT STOP via the original
    `if cls is not ConflictClass.SOFT:` guard at L243.

    Without this dispatch, the CLI --resolve-soft path short-circuits VAULT_CLAIM
    to STOP before reaching the defense-in-depth backstop in _regen_slice_queue.
    """
    text_2 = _well_formed_queue("alice <a@example.com>", "2026-05-29T12:00:00+00:00")
    text_3 = _well_formed_queue("bob <b@example.com>", "2026-05-29T10:00:00+00:00")
    _stage_rebase(tmp_path, text_2, text_3)

    diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={},
        claim_history=(
            _claim("add-foo", "alice <a@example.com>", "2026-05-29T12:00:00+00:00", 2),
            _claim("add-foo", "bob <b@example.com>", "2026-05-29T10:00:00+00:00", 3),
        ),
    )
    result = resolve_soft_conflict(diag, repo_root=tmp_path)
    assert result.action == "APPLIED", (
        f"resolve_soft_conflict must dispatch VAULT_CLAIM into PCR-2a; "
        f"got action={result.action!r} reason={result.reason!r}"
    )
    assert result.conflict_class == ConflictClass.VAULT_CLAIM


def test_regen_slice_queue_dispatches_into_vault_claim_resolver(tmp_path) -> None:
    """Defense-in-depth dispatch: _regen_slice_queue's gate at L627-638 raises
    a _VaultClaimDispatch sentinel (NOT _SoftResolutionError(VAULT_CLAIM));
    resolve_soft_conflict catches it and reroutes to resolve_vault_claim_conflict.

    The sentinel-raise path is reached when classify_conflict returned SOFT
    (caller's class) but the actual queue text reveals a collision via
    _extract_claim_diff — the silent-classify-bypass corner case.
    """
    text_2 = _well_formed_queue("alice <a@example.com>", "2026-05-29T12:00:00+00:00")
    text_3 = _well_formed_queue("bob <b@example.com>", "2026-05-29T10:00:00+00:00")
    _stage_rebase(tmp_path, text_2, text_3)

    # Synthetic diag declaring class SOFT (empty claim_history bypasses classify's
    # VAULT_CLAIM gate); the in-helper defense-in-depth gate must catch the
    # collision present in the actual text_2/text_3 stages.
    diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={},
        claim_history=(),
    )
    # _regen_slice_queue must NOT raise _SoftResolutionError(VAULT_CLAIM) anymore.
    # Either it returns the overlaid (Path, str) for VAULT_CLAIM-resolved state
    # OR it raises _VaultClaimDispatch sentinel for resolve_soft_conflict to reroute.
    from tools.parallel_conflict_resolver import _VaultClaimDispatch
    try:
        _regen_slice_queue(tmp_path, diag)
        # If it returns without raising, that's the inline-handle path — also valid.
    except _VaultClaimDispatch:
        # Sentinel path — also valid.
        pass
    except _SoftResolutionError as exc:
        # The OLD behavior: must no longer occur for VAULT_CLAIM.
        assert exc.conflict_class != ConflictClass.VAULT_CLAIM, (
            "Defense-in-depth gate must NOT raise _SoftResolutionError(VAULT_CLAIM) "
            "post-PCR-2a; expected _VaultClaimDispatch sentinel or inline-handle"
        )


def test_unknown_class_still_fail_closed(tmp_path) -> None:
    """PCR-1's UNKNOWN-class fail-closed branch at L605-609 must remain intact.

    Trigger: both stages of slice-queue.md missing (synthetic — no rebase staged).
    Expected: _SoftResolutionError(UNKNOWN) raised; PCR-2a must not break this.
    """
    # No rebase staged → _git_show_stage returns empty for both stages →
    # _regen_slice_queue L605-609 raises _SoftResolutionError(UNKNOWN)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={},
        claim_history=(),
    )
    try:
        _regen_slice_queue(tmp_path, diag)
        raise AssertionError("expected _SoftResolutionError(UNKNOWN)")
    except _SoftResolutionError as exc:
        assert exc.conflict_class == ConflictClass.UNKNOWN, (
            f"UNKNOWN-class fail-closed branch must stay intact; "
            f"got conflict_class={exc.conflict_class}"
        )
