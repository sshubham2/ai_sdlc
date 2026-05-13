"""Pin load-bearing prose in skills/critique/SKILL.md.

Per TPHD-1 (slice-017, methodology-changelog v0.32.0) sub-mode (a):
when applying ACCEPTED-FIXED Builder draft edits at /critique Step 4 that
change test function names or AC #N row references, harmonize the
mission-brief TF-1 plan section in the SAME fix block. Otherwise the plan
ships stale to /build-slice and surfaces at Phase 6 audit as DEVIATION
(via pytest collection failure on stale function names, since
`tools/test_first_audit.py --strict-pre-finish` only checks status not
function-existence — per slice-017 /critique B1 ACCEPTED-FIXED).
"""
from tests.methodology.conftest import read_file

CRITIQUE = read_file("skills/critique/SKILL.md")


def test_critique_skill_md_tphd_1_post_fix_prose_step_present():
    """skills/critique/SKILL.md must carry TPHD-1 sub-mode (a) prose at end
    of Step 4 (Builder draft response per finding), before Step 4.5
    (User-owned triage TRI-1).

    Defect class: without the prose, every future /critique invocation that
    applies ACCEPTED-FIXED edits changing test function names risks shipping
    a stale TF-1 plan to /build-slice (slice-016 first-Critic-MISS class
    N=1; canonical reference instance at slice-017 itself via M2 rename
    `_phase_0_step_*` → `_prerequisite_check_bullet_*` triggering same-fix-
    block TF-1 plan harmonization).

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (a) skill prose pin).
    """
    assert "Per **TPHD-1**" in CRITIQUE, (
        "skills/critique/SKILL.md missing 'Per **TPHD-1**' canonical reference "
        "— TPHD-1 prose insertion at end of Step 4 missing or rule-ID drifted"
    )


def test_critique_skill_md_tphd_1_post_fix_prose_step_location_pinned():
    """skills/critique/SKILL.md TPHD-1 prose must appear specifically
    between Step 4 close (`Update \\`critique.md\\` with Builder draft
    dispositions inline`) and Step 4.5 header (`### Step 4.5: User-owned
    triage (TRI-1)`).

    Defect class: substring-pin alone doesn't catch placement drift.
    Without location-pin, a future edit could move TPHD-1 prose into the
    wrong step (e.g., Step 5 Gate decision) and the substring-pin would
    still pass. Per slice-009 M1 scoped-find precedent + slice-016 N=4
    stable `_sub_clause_present` + `_location_pinned` duality.

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (a) location pin).
    """
    # Scoped find: TPHD-1 must appear between Step 4 close and Step 4.5 header
    step_4_close_anchor = 'Update `critique.md` with Builder draft dispositions inline'
    step_4_5_header = "### Step 4.5: User-owned triage (TRI-1)"

    step_4_close_pos = CRITIQUE.find(step_4_close_anchor)
    step_4_5_pos = CRITIQUE.find(step_4_5_header)

    assert step_4_close_pos != -1, (
        f"skills/critique/SKILL.md missing Step 4 close anchor "
        f"'{step_4_close_anchor[:40]}...' — file structure changed"
    )
    assert step_4_5_pos != -1, (
        f"skills/critique/SKILL.md missing Step 4.5 header "
        f"'{step_4_5_header}' — file structure changed"
    )
    assert step_4_close_pos < step_4_5_pos, (
        "skills/critique/SKILL.md Step 4 close anchor must appear before "
        "Step 4.5 header — anchor ordering broken"
    )

    # TPHD-1 prose must fall in this scoped range
    scoped_segment = CRITIQUE[step_4_close_pos:step_4_5_pos]
    assert "Per **TPHD-1**" in scoped_segment, (
        "skills/critique/SKILL.md TPHD-1 prose not located between Step 4 "
        "close and Step 4.5 header — placement drifted from sub-mode (a) "
        "anchor (end of Step 4, before TRI-1 triage)"
    )
