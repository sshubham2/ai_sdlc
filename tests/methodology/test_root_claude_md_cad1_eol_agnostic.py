"""Prose-pin: root CLAUDE.md "Self-hosting discipline" states the CAD-1 /
Mini-CAD invariant as EOL-agnostic, not raw byte-equality (B2 / slice-033).

Per slice-033 ADR-033 / EOL-DRIFT-1: shipping an EOL-agnostic comparator
while the governing self-hosting doc still asserts "MUST be byte-equal"
leaves a project-instruction-level falsehood future slices audit against
(CLAUDE.md is OVERRIDE-priority instruction). This pin has a positive
substring (the corrected invariant is present) AND a negative substring
(the OLD "MUST be byte-equal" CAD-1/Mini-CAD phrasing is gone) — the
negative catches a regression that reverts the wording.

Mirrors the test_root_claude_md_branch_per_slice_rule.py shape (slice-021):
section-scoped substring assertion, no line-range pin.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file

_SECTION = "## Self-hosting discipline"


def _self_hosting_block(content: str) -> str:
    start = content.find(_SECTION)
    assert start != -1, f"Root CLAUDE.md must retain `{_SECTION}` section"
    nxt = content.find("\n## ", start + 1)
    return content[start:nxt] if nxt > 0 else content[start:]


def test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant() -> None:
    """CLAUDE.md CAD-1 + Mini-CAD bullets state the EOL-agnostic invariant
    and no longer say "MUST be byte-equal" (B2 regression guard)."""
    block = _self_hosting_block(read_file("CLAUDE.md"))

    # Positive: the corrected invariant + decision lineage are present.
    assert "content-equal modulo line endings" in block, (
        "CLAUDE.md Self-hosting discipline must state the CAD-1/mini-CAD "
        "invariant as `content-equal modulo line endings` (EOL-DRIFT-1 / "
        "ADR-033) — slice-033 B2"
    )
    assert "EOL-DRIFT-1" in block and "ADR-033" in block, (
        "CLAUDE.md Self-hosting discipline must cite the EOL-DRIFT-1 / "
        "ADR-033 lineage for the EOL-agnostic invariant"
    )

    # Negative: the OLD actively-false phrasing must be gone. Pre-slice-033
    # CLAUDE.md said `MUST be byte-equal to installed` (CAD-1) and
    # `MUST be byte-equal to installed copy` (Mini-CAD). That exact
    # signature must not survive — it is the B2 falsehood.
    assert "MUST be byte-equal" not in block, (
        "CLAUDE.md Self-hosting discipline still contains the OLD "
        "`MUST be byte-equal` CAD-1/Mini-CAD phrasing — after slice-033 the "
        "guard is EOL-agnostic; a false MUST-statement in the governing "
        "contract is the slice-022 self-violation B2 caught. Regression."
    )
