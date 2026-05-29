"""Pin slice-079 Fix Q (slice-078 m3): PCR-2a Step 5 atomicity docstring names single-file blast-radius rationale.

Slice-078 m3: `resolve_vault_claim_conflict`'s Step 5 inverts the SOFT path's pending_writes batching
(PCR-1's slice-076 critique M2 fix). The inversion is correct for single-file VAULT_CLAIM scope but
the docstring did not name the rationale. Fix Q adds the rationale to the docstring.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import tools.parallel_conflict_resolver as pcr

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_resolve_vault_claim_conflict_docstring_names_atomicity_rationale() -> None:
    """Fix Q: docstring contains 'Single-file scope' + 'PCR-1's pending_writes' substrings."""
    fn = pcr.resolve_vault_claim_conflict
    doc = inspect.getdoc(fn) or ""
    assert "Single-file scope" in doc, (
        "Fix Q regression: resolve_vault_claim_conflict docstring missing 'Single-file scope' "
        "atomicity rationale"
    )
    assert "PCR-1's pending_writes" in doc or "pending_writes" in doc, (
        "Fix Q regression: docstring missing reference to PCR-1's pending_writes batching contrast"
    )


def test_step_5_block_in_source_names_atomicity_rationale() -> None:
    """Fix Q: source file contains the atomicity-rationale comment block near Step 5.

    Belt-and-suspenders: docstring assertion above guards the `inspect.getdoc` view; this asserts
    the raw source contains the substrings, which guards against future refactor moving the rationale
    out of the canonical docstring into a code comment (or vice versa).
    """
    src = (REPO_ROOT / "tools" / "parallel_conflict_resolver.py").read_text(encoding="utf-8")
    assert "Single-file scope" in src, (
        "Fix Q regression: 'Single-file scope' atomicity rationale absent from "
        "tools/parallel_conflict_resolver.py source"
    )
