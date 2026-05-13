"""Pin load-bearing prose in skills/build-slice/SKILL.md."""
from tests.methodology.conftest import read_file

BUILD = read_file("skills/build-slice/SKILL.md")


def test_build_requires_plan_mode_first():
    """Build-slice must enter plan mode before editing.

    Defect class: Skipping plan mode produces edits against assumptions rather
    than actual code. Plan mode is what gives the Builder groundedness.
    Rule reference: META-2.
    """
    assert "ENTER PLAN MODE FIRST" in BUILD


def test_build_forbids_silent_deferral():
    """Must-not-defer items cannot be silently deferred.

    Defect class: Silent deferral of auth/validation/error-handling items is
    how production-affecting gaps ship. The skill must require explicit user
    approval to defer, not allow silent skipping.
    Rule reference: META-2.
    """
    assert "DO NOT silently defer must-not-defer items" in BUILD


def test_build_smoke_gate_required():
    """Mid-slice smoke gate is non-skippable.

    Defect class: Skipping the smoke gate at ~50% of work means the slice
    builds on a broken base. The gate catches "builds but doesn't work" before
    more is built.
    Rule reference: META-2.
    """
    assert "DO NOT skip the mid-slice smoke gate" in BUILD


def test_build_log_events_before_risky_calls():
    """Append events to build-log.md before risky tool calls.

    Defect class: Tool failures (corrupted binaries, parser errors) can erase
    in-memory context. Events written before the risky call survive on disk.
    Rule reference: META-2.
    """
    assert "APPEND TO build-log.md events BEFORE risky tool calls" in BUILD


# --- Slice-017 / TPHD-1 sub-mode (c) prerequisite-check bullet pin ---

def test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_present():
    """skills/build-slice/SKILL.md must carry TPHD-1 sub-mode (c) prose as
    a NEW bullet INTO the existing `## Prerequisite check` section.

    Defect class: without the prose, every future /build-slice invocation
    risks proceeding to Step 1 plan-mode entry with a stale mission-brief
    TF-1 plan. TPHD-1 sub-mode (c) is the third Critic-stack defense layer
    (after /critique Step 4 + /critique-review Step 3) — closes the
    function-name-staleness audit gap that `tools/test_first_audit.py
    --strict-pre-finish` does not detect (status-only check per slice-017
    /critique B1 ACCEPTED-FIXED).

    Placement decision per slice-017 /critique M2 ACCEPTED-FIXED: the
    discipline is structurally a prerequisite verification, and the
    existing build-slice step numbering is 1,2,3,4,5,6,7,7b,7c,8 with no
    Step 0. Folding into existing `## Prerequisite check` section is the
    cleaner architectural choice over adding a NEW `### Step 0`.

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (c) skill prose pin).
    """
    # Bullet form (imperative, matches existing Prerequisite check bullet style),
    # NOT "Per **TPHD-1**" paragraph form used by /critique + /critique-review
    # SKILL.md insertions. Per slice-017 self-application: test harmonized
    # in same /build-slice fix block per TPHD-1 sub-mode (a).
    assert "Run TPHD-1 pre-flight harmonization" in BUILD, (
        "skills/build-slice/SKILL.md missing 'Run TPHD-1 pre-flight "
        "harmonization' canonical reference — TPHD-1 bullet insertion in "
        "## Prerequisite check section missing or rule-ID drifted"
    )


def test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_location_pinned():
    """skills/build-slice/SKILL.md TPHD-1 prose must appear specifically
    inside the `## Prerequisite check` section (between the H2 header and
    the next `## Your task` H2 header).

    Defect class: substring-pin alone doesn't catch placement drift.
    Without location-pin, a future edit could move TPHD-1 prose into the
    wrong section (e.g., Step 5 mid-slice smoke gate or Step 6 pre-finish
    gate) and the substring-pin would still pass. Per slice-009 M1
    scoped-find precedent + slice-016 N=4 stable `_sub_clause_present` +
    `_location_pinned` duality.

    Rule reference: TPHD-1 (slice-017 AC #2; sub-mode (c) location pin).
    """
    prerequisite_check_header = "## Prerequisite check"
    your_task_header = "## Your task"

    prereq_pos = BUILD.find(prerequisite_check_header)
    your_task_pos = BUILD.find(your_task_header)

    assert prereq_pos != -1, (
        f"skills/build-slice/SKILL.md missing '## Prerequisite check' "
        f"section header — file structure changed"
    )
    assert your_task_pos != -1, (
        f"skills/build-slice/SKILL.md missing '## Your task' section "
        f"header — file structure changed"
    )
    assert prereq_pos < your_task_pos, (
        "skills/build-slice/SKILL.md `## Prerequisite check` must appear "
        "before `## Your task` — section ordering broken"
    )

    # TPHD-1 prose must fall in this scoped range (the prerequisite check section)
    scoped_segment = BUILD[prereq_pos:your_task_pos]
    assert "Run TPHD-1 pre-flight harmonization" in scoped_segment, (
        "skills/build-slice/SKILL.md TPHD-1 bullet not located inside "
        "'## Prerequisite check' section — placement drifted from sub-mode "
        "(c) anchor (per /critique M2 ACCEPTED-FIXED: must live in "
        "Prerequisite check section, NOT a new Step 0)"
    )
