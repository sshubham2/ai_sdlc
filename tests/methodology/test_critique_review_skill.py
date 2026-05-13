"""Pin load-bearing prose in skills/critique-review/SKILL.md.

Per TPHD-1 (slice-017, methodology-changelog v0.32.0) sub-mode (b):
when the meta-Critic's ACCEPTED-FIXED findings (during /critique Step 4.5
TRI-1) will change test function names or AC #N row references, harmonize
the mission-brief TF-1 plan section in the same fix block. Sub-mode (a)
lives in /critique Step 4 (post-fix-prose harmonization); (c) lives in
/build-slice Prerequisite check (pre-flight harmonization bullet).
"""
from tests.methodology.conftest import read_file

CRITIQUE_REVIEW = read_file("skills/critique-review/SKILL.md")


def test_critique_review_skill_md_tphd_1_post_fix_prose_step_present():
    """skills/critique-review/SKILL.md must carry TPHD-1 sub-mode (b) prose
    at end of Step 3 (Receive meta-Critic findings), before Step 4 (Run the
    audit).

    Defect class: without the prose, every future /critique-review
    invocation that surfaces meta-Critic ACCEPTED-FIXED findings affecting
    test function names risks shipping a stale TF-1 plan to /build-slice.
    Canonical reference instance at slice-017 itself via meta-Critic
    m-add-1 count correction (11 → 12 entry-pin functions across 6 sites).

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (b) skill prose pin).
    """
    assert "Per **TPHD-1**" in CRITIQUE_REVIEW, (
        "skills/critique-review/SKILL.md missing 'Per **TPHD-1**' canonical "
        "reference — TPHD-1 prose insertion at end of Step 3 missing or "
        "rule-ID drifted"
    )


def test_critique_review_skill_md_tphd_1_post_fix_prose_step_location_pinned():
    """skills/critique-review/SKILL.md TPHD-1 prose must appear specifically
    between Step 3 close (`Take the agent's output and write it to`) and
    Step 4 header (`### Step 4: Run the audit`).

    Defect class: substring-pin alone doesn't catch placement drift.
    Without location-pin, a future edit could move TPHD-1 prose into the
    wrong step (e.g., Step 5 Hand off) and the substring-pin would still
    pass. Per slice-009 M1 scoped-find precedent + slice-016 N=4 stable
    `_sub_clause_present` + `_location_pinned` duality.

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (b) location pin).
    """
    step_3_close_anchor = "Take the agent's output and write it to"
    step_4_header = "### Step 4: Run the audit"

    step_3_close_pos = CRITIQUE_REVIEW.find(step_3_close_anchor)
    step_4_pos = CRITIQUE_REVIEW.find(step_4_header)

    assert step_3_close_pos != -1, (
        f"skills/critique-review/SKILL.md missing Step 3 close anchor "
        f"'{step_3_close_anchor}' — file structure changed"
    )
    assert step_4_pos != -1, (
        f"skills/critique-review/SKILL.md missing Step 4 header "
        f"'{step_4_header}' — file structure changed"
    )
    assert step_3_close_pos < step_4_pos, (
        "skills/critique-review/SKILL.md Step 3 close anchor must appear "
        "before Step 4 header — anchor ordering broken"
    )

    # TPHD-1 prose must fall in this scoped range
    scoped_segment = CRITIQUE_REVIEW[step_3_close_pos:step_4_pos]
    assert "Per **TPHD-1**" in scoped_segment, (
        "skills/critique-review/SKILL.md TPHD-1 prose not located between "
        "Step 3 close and Step 4 header — placement drifted from sub-mode "
        "(b) anchor (end of Step 3, before audit step)"
    )
