"""Structural-pin: /slice SKILL.md carries the stranded-slice consult (R-26 / ADR-079).

Section-scoped per BC-PROJ-14 (anchor on the line-anchored `### Stranded-slice
consult` heading; assert the load-bearing literals within that section only, not
file-globally). Pins the prerequisite consult prose that makes `/slice` halt
ONLY on genuine divergence and proceed past healthy parallel slices.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT

_SKILL = REPO_ROOT / "skills" / "slice" / "SKILL.md"


def _section(text: str, heading: str) -> str:
    """Return the slice of `text` from a line-anchored `heading` to the next
    `## `/`### ` heading (section/seam-scope per BC-PROJ-14 (c))."""
    m = re.search(rf"(?m)^{re.escape(heading)}\b", text)
    assert m, f"heading {heading!r} not found in {_SKILL}"
    start = m.start()
    nxt = re.search(r"(?m)^#{2,3} ", text[start + len(heading):])
    end = start + len(heading) + nxt.start() if nxt else len(text)
    return text[start:end]


def test_slice_skill_has_stranded_detection_prereq():
    text = _SKILL.read_text(encoding="utf-8")
    section = _section(text, "### Stranded-slice consult")

    # The consult invokes the detector tool (unique-to-invocation literal).
    assert "tools.stranded_slice_audit" in section, (
        "the stranded-slice consult must invoke `$PY -m tools.stranded_slice_audit`"
    )
    # It must run BEFORE candidate-gathering (Step 1).
    assert "Step 1" in section, "the consult must state it runs BEFORE Step 1 candidate-gathering"
    # divergent → HALT with a structured-options gate.
    assert "status: divergent" in section
    assert "AskUserQuestion" in section, "a divergent result must halt with an AskUserQuestion gate"
    # The three resume options + always-available proceed-anyway (advisory, never blocking).
    assert "/commit-slice" in section
    assert re.search(r"[Pp]roceed defining a new slice anyway", section), (
        "the gate must always offer proceed-anyway (advisory, never blocking)"
    )
    # The parallel-safe path: clean + informational entries PROCEED without a gate.
    assert "status: clean" in section
    assert "in-progress" in section and "claimed-by-other" in section, (
        "informational classes must be named as the no-halt (parallel-safe) path"
    )
    assert re.search(r"PROCEED to Step 1 without a gate|PROCEED .* without a gate", section), (
        "clean+informational must proceed WITHOUT a gate (the parallel-safety path)"
    )
    # Exit 2 (usage) is fail-visible, never a silent skip (R-7 class).
    assert "Exit 2" in section or "exit 2" in section
