"""Pin slice-079 Fix R (slice-078 m5): `_VaultClaimDispatch` sentinel carries catch-order-clarity comment.

Slice-078 m5: `_VaultClaimDispatch` and `_SoftResolutionError` both inherit from `Exception` (sibling, no
inheritance between them). The catch-clause order in `resolve_soft_conflict` is therefore SEMANTICALLY
INDEPENDENT, not load-bearing-by-inheritance. A future maintainer might reorder under the wrong belief.
Fix R adds a comment naming this invariant.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PCR_SRC = REPO_ROOT / "tools" / "parallel_conflict_resolver.py"


def test_vault_claim_dispatch_comment_names_catch_order_invariant() -> None:
    """Fix R: source contains the canonical comment naming the catch-order independence."""
    src = PCR_SRC.read_text(encoding="utf-8")
    assert "_VaultClaimDispatch" in src, "sanity: _VaultClaimDispatch must exist in source"
    assert "catch-order" in src and "independent" in src.lower(), (
        "Fix R regression: _VaultClaimDispatch is missing the canonical catch-order-clarity comment "
        "naming the independence invariant (sibling-to-_SoftResolutionError; both inherit from Exception "
        "directly; catch-order semantically independent, NOT load-bearing by inheritance)"
    )
    assert "_SoftResolutionError" in src, (
        "Fix R regression: comment must reference _SoftResolutionError as the sibling class"
    )
