"""Shared helpers for parsing structural sections of `skills/*/SKILL.md` files in test pins.

Extracted per slice-079 Fix E (slice-074 m4): the byte-equivalent `_branch_state_section`
helper was duplicated across multiple `tests/methodology/test_*.py` modules. Promoted here so
the test corpus defines it exactly once — pinned by
`test_skill_parse_helpers.py::test_helper_defined_only_once_in_test_corpus` (a global
corpus-grep invariant; WIRE-1 exemption-by-categorization per /critique m1 ACCEPTED-FIXED).
"""
from __future__ import annotations

import re


def _branch_state_section(skill_md_text: str) -> str:
    """Return the `## Prerequisite check ### Branch state` sub-section body of a SKILL.md.

    The sub-section runs from its `### Branch state` heading up to the next markdown H2
    heading (`## ` followed by a CAPITAL letter). The capital-letter anchor disambiguates
    the real section boundary from `## `-prefixed shell comments inside bash codefences
    (per slice-074 /critique pass-1 M2 ACCEPTED-FIXED). Do NOT relax to bare `(?=^## )` —
    that misfires on `## `-prefixed shell comments and silently truncates the section,
    masking real prose changes.
    """
    m = re.search(
        r"^### Branch state\b.*?(?=^## [A-Z])",
        skill_md_text,
        re.MULTILINE | re.DOTALL,
    )
    assert m is not None, "### Branch state sub-section not found"
    return m.group(0)
