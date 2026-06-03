"""Pin slice-079 Fix E (slice-074 m4): shared `_branch_state_section` helper extracted from duplicated test corpus.

Slice-074 m4: `tests/methodology/test_build_slice_skill_cp_r_step.py` (deleted at slice-105 / ADR-094 with the
worktree cp-r seed it pinned) + `test_build_slice_skill_dirty_tree_resolution.py` both defined byte-equivalent
`_branch_state_section` helpers. Fix E promotes to shared module — still consumed by the surviving
`test_build_slice_skill_dirty_tree_resolution.py` + `test_build_slice_skill_branch_state_preamble.py`.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.methodology._skill_parse_helpers import _branch_state_section

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_METHODOLOGY = REPO_ROOT / "tests" / "methodology"


def test_branch_state_section_returns_section_body() -> None:
    """Fix E: the shared helper returns the Branch state section body of build-slice SKILL.md."""
    skill_md = REPO_ROOT / "skills" / "build-slice" / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    body = _branch_state_section(text)
    assert body, "Fix E regression: _branch_state_section returned empty body"
    # BRANCH-3 (slice-099) reordered ### Branch state: point 1 is now the
    # detect-existing-worktree case (pick-time create per ADR-090), so the
    # canonical point-1 marker moved from "If on default branch" to this.
    assert "If the worktree already exists" in body, (
        "Fix E regression: returned body does not contain the canonical point-1 marker"
    )


def test_helper_defined_only_once_in_test_corpus() -> None:
    """Fix E: no test module under tests/methodology defines its own `_branch_state_section`.

    Corpus-grep global structural invariant (WIRE-1 exemption-by-categorization per /critique m1 ACCEPTED-FIXED).
    Pre-fix: 2 modules define the helper locally. Post-fix: only the shared module + this test file mention it
    (the shared module via `def _branch_state_section`; this test via the `from` import).
    """
    definition_re = re.compile(r"^def _branch_state_section\b", re.MULTILINE)
    offenders: list[str] = []
    for py in TESTS_METHODOLOGY.glob("test_*.py"):
        text = py.read_text(encoding="utf-8")
        if definition_re.search(text):
            offenders.append(py.name)
    assert offenders == [], (
        f"Fix E regression: _branch_state_section duplicated in test corpus: {offenders}. "
        f"Use `from tests.methodology._skill_parse_helpers import _branch_state_section` instead."
    )
