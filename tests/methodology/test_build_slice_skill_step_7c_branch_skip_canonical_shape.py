"""Prose-pin test for the BRANCH=skip canonical DEVIATION-line shape at /build-slice Step 7c.

Per slice-021 AC #2 + /critique B1 ACCEPTED-PENDING: skills/build-slice/SKILL.md Step 7c
flight-recorder discipline must canonicalize the `BRANCH=skip` line shape:

    <YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>

This narrows the empirically-permissive parent DEVIATION convention (which accepts
date-only / date+HH:MM / date+phase variants) by requiring HH:MM AND the `rationale:`
token for `BRANCH=skip` sub-shape — necessary for `tools/branch_workflow_audit.py`
escape-hatch regex matching.

The audit's escape-hatch regex is `^- \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2} DEVIATION: BRANCH=skip\\b.+rationale: .+`.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_build_slice_skill_md_step_7c_canonicalizes_branch_skip_deviation_line_shape() -> None:
    """Step 7c must contain a sentence pinning the canonical BRANCH=skip line shape."""
    content = read_file("skills/build-slice/SKILL.md")
    assert "Step 7c" in content, (
        "skills/build-slice/SKILL.md must retain Step 7c flight-recorder discipline section"
    )
    # Scope to Step 7c body (between `### Step 7c` and the next `### Step` heading).
    step7c_idx = content.find("### Step 7c")
    assert step7c_idx >= 0, "Step 7c section heading not found"
    # Find next `### Step` heading after Step 7c, OR Step 8 specifically.
    rest = content[step7c_idx:]
    next_step_idx = rest.find("### Step 8")
    step7c_body = rest[:next_step_idx] if next_step_idx > 0 else rest

    # Canonical BRANCH=skip line shape must be pinned: requires HH:MM + rationale: token.
    assert "BRANCH=skip" in step7c_body, (
        "Step 7c must reference the canonical `BRANCH=skip` token per slice-021 AC #2"
    )
    assert "rationale:" in step7c_body, (
        "Step 7c must pin the `rationale:` token in the canonical BRANCH=skip line shape"
    )
    # Canonical shape exemplar: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>`.
    # Either the literal YYYY-MM-DD HH:MM placeholder OR a concrete instance must appear.
    assert (
        "YYYY-MM-DD HH:MM" in step7c_body
        or "HH:MM" in step7c_body
    ), (
        "Step 7c canonical BRANCH=skip line shape must require HH:MM "
        "(narrows the empirically-permissive parent DEVIATION convention)"
    )
