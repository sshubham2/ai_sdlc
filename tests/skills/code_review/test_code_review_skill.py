"""Pins the /code-review skill SKILL.md (CRSI-1; slice-060).

Asserts:
- `## Pipeline position` block is present with the canonical chain edge
  (predecessor /build-slice, successor /validate-slice, auto-advance true).
- The walking-skeleton self-dogfood produced `code-review.md` on slice-060.

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060; ADR-059).
"""
from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SKILL_MD = _REPO_ROOT / "skills" / "code-review" / "SKILL.md"
_SLICE_060_CODE_REVIEW = (
    _REPO_ROOT / "architecture" / "slices"
    / "slice-060-add-code-review-skill" / "code-review.md"
)


def _read(path: Path) -> str:
    assert path.exists(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def test_skill_md_pipeline_position_block_present():
    """skills/code-review/SKILL.md must carry a well-formed `## Pipeline
    position` block (PCA-1 obligation; the audit reads this for chain-shape).
    """
    body = _read(_SKILL_MD)
    assert "## Pipeline position" in body, (
        "skills/code-review/SKILL.md missing `## Pipeline position` block"
    )
    # All 5 required fields per tools/pipeline_chain_audit.py:_REQUIRED_FIELDS
    for field in ("predecessor", "successor", "auto-advance",
                  "on-clean-completion", "user-input gates"):
        assert f"**{field}**" in body, (
            f"skills/code-review/SKILL.md `## Pipeline position` missing "
            f"required field `{field}`"
        )


def test_skill_md_successor_is_validate_slice():
    """/code-review's canonical successor MUST be /validate-slice
    (walking-skeleton CRSI-1 chain edge per design.md).
    """
    body = _read(_SKILL_MD)
    # Read the `## Pipeline position` block specifically (not random body prose)
    idx = body.find("## Pipeline position")
    assert idx >= 0
    block = body[idx:]
    # Successor field on its own line
    assert "**successor**: `/validate-slice`" in block, (
        "skills/code-review/SKILL.md Pipeline-position `successor:` field "
        "must point to `/validate-slice` per the canonical CRSI-1 chain"
    )
    assert "**predecessor**: `/build-slice`" in block, (
        "skills/code-review/SKILL.md Pipeline-position `predecessor:` field "
        "must point to `/build-slice`"
    )
    assert "**auto-advance**: true" in block, (
        "skills/code-review/SKILL.md Pipeline-position `auto-advance:` must "
        "be `true` (in-loop step; no user-input HALT in v1)"
    )


def test_self_dogfood_produces_code_review_md_on_slice_060():
    """Walking-skeleton Layer 6 proof: invoking `/code-review` against
    slice-060 itself must produce `code-review.md` with non-empty findings
    (the artifact-existence-and-content check; NOT a pytest-driven LLM
    invocation — per critique M2 reclassification).

    Per design.md Build-phase sequence Phase C: this test PASSES only after
    the self-dogfood `/code-review` invocation against slice-060 has run
    (which itself requires Phase B forward-sync to have completed).
    """
    body = _read(_SLICE_060_CODE_REVIEW)
    # Result line present
    assert "**Result**" in body, (
        "slice-060 code-review.md missing **Result** header — agent output "
        "either malformed or self-dogfood did not run"
    )
    # Non-empty findings: at minimum, one of the canonical section markers
    # OR a NO-CODE-CHANGES result (which is itself valid output).
    has_findings = any(
        marker in body
        for marker in ("### B", "### M", "Blockers", "Majors", "Minors")
    )
    has_no_code_changes = "NO-CODE-CHANGES" in body
    assert has_findings or has_no_code_changes, (
        "slice-060 code-review.md missing non-empty findings AND lacks the "
        "NO-CODE-CHANGES marker — agent output is unusable"
    )
    # Dimensions footer present (the agent's specificity discipline)
    assert "## Dimensions checked" in body, (
        "slice-060 code-review.md missing `## Dimensions checked` footer — "
        "agent did not emit the 9-dimensions report"
    )
