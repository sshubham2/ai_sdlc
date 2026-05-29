"""AC#5 — Catalogued post-fix regression repro for PCR-2a (slice-078).

Per B2 ACCEPTED-FIXED: single PASS-post-fix test. The pre-fix → post-fix
FAIL→PASS contrast is captured empirically in build-log.md Events at
pre-build / post-build SHAs (NOT a separate test function — slice-024 /
slice-014 precedent).

Post-fix invariant: _regen_slice_queue's defense-in-depth gate at L627-638
NO LONGER raises _SoftResolutionError(VAULT_CLAIM) on a 2-claim collision.
Instead it dispatches via the _VaultClaimDispatch sentinel into the public
resolve_vault_claim_conflict path (caught by resolve_soft_conflict's loop).
Catalogued as shippability.md row — pinned never-silently-regress.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from tools.parallel_conflict_resolver import (
    ClaimEntry,
    ConflictClass,
    ConflictDiagnostic,
    _SoftResolutionError,
    _regen_slice_queue,
    _VaultClaimDispatch,
)


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
    )


def _stage_rebase(tmp_path: Path, text_2: str, text_3: str) -> None:
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


def test_vault_claim_gate_closed_returns_resolution_result(tmp_path) -> None:
    """Post-fix regression: VAULT_CLAIM gate at _regen_slice_queue L627-638
    NO LONGER raises _SoftResolutionError(VAULT_CLAIM).

    Pre-fix behavior (PCR-1, slice-076):
        raise _SoftResolutionError(..., ConflictClass.VAULT_CLAIM)

    Post-fix behavior (PCR-2a, slice-078):
        raise _VaultClaimDispatch()  # caught + rerouted by resolve_soft_conflict
        OR returns the overlaid (Path, str) tuple inline.

    Either way, the OLD _SoftResolutionError(VAULT_CLAIM) raise is gone.
    """
    text_2 = _well_formed_queue("alice <a@example.com>", "2026-05-29T12:00:00+00:00")
    text_3 = _well_formed_queue("bob <b@example.com>", "2026-05-29T10:00:00+00:00")
    _stage_rebase(tmp_path, text_2, text_3)

    diag = ConflictDiagnostic(
        u_files=("architecture/slice-queue.md",),
        concerned_slices={},
        claim_history=(),
    )
    try:
        _regen_slice_queue(tmp_path, diag)
    except _VaultClaimDispatch:
        pass  # post-fix sentinel path — gate-closure success
    except _SoftResolutionError as exc:
        assert exc.conflict_class != ConflictClass.VAULT_CLAIM, (
            "PCR-2a gate-closure regression: _regen_slice_queue still raises "
            "_SoftResolutionError(VAULT_CLAIM) on same-candidate-different-identity "
            "collision. Expected _VaultClaimDispatch sentinel raise (or inline "
            "return) per ADR-071 § Decision."
        )
