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


# --- Slice-026 / CRP-1 critique-review-prerequisite-check pins ---


def test_build_slice_prereq_crp_1_refuses_on_absent_mandatory_critique_review():
    """skills/build-slice/SKILL.md must carry the CRP-1 prerequisite sub-block
    with the verbatim STOP routing message + the audit invocation, located
    INSIDE `## Prerequisite check`, AFTER the `critique.md`-exists gate, and
    BEFORE `### Branch state` (deterministic placement — stable mini-CAD
    drift target per /critique M2 ACCEPTED-FIXED).

    Defect class (the slice-025 gap CRP-1 closes): a mandatory
    `/critique-review` (DR-1, Standard-mode + mandatory-Critic) skipped
    silently because nothing structurally detects the skip before
    `/build-slice`. Without this prose, every future /build-slice can
    proceed past a skipped mandatory dual-review unnoticed.

    Rule reference: CRP-1 (methodology-changelog.md v0.40.0); slice-026 AC #1.
    """
    prereq_pos = BUILD.find("## Prerequisite check")
    your_task_pos = BUILD.find("## Your task")
    branch_state_pos = BUILD.find("### Branch state")
    assert prereq_pos != -1 and your_task_pos != -1 and branch_state_pos != -1

    scoped = BUILD[prereq_pos:your_task_pos]

    # CRP-1 bullet present, inside the Prerequisite check section.
    assert "Run CRP-1 critique-review-prerequisite check" in scoped, (
        "CRP-1 prerequisite bullet missing from '## Prerequisite check' "
        "section — slice-025 silent-skip gap reopened"
    )

    # Audit invocation present.
    assert (
        "tools.critique_review_prerequisite_audit" in scoped
    ), "CRP-1 sub-block missing the critique_review_prerequisite_audit invocation"

    # Verbatim STOP routing message (load-bearing — pinned literally).
    assert (
        'STOP: this slice has a mandatory `/critique-review` (DR-1) that '
        "has not been run. Run `/critique-review` for this slice before "
        "`/build-slice`." in BUILD
    ), "CRP-1 verbatim STOP routing message drifted or missing"

    # Deterministic placement: CRP-1 bullet AFTER the critique.md-exists
    # gate and BEFORE `### Branch state` (dependency: no critique-review
    # without a critique).
    crp_pos = BUILD.find("Run CRP-1 critique-review-prerequisite check")
    critique_exists_pos = BUILD.find(
        "If `critique.md` doesn't exist (Standard or Heavy mode)"
    )
    assert critique_exists_pos != -1
    assert critique_exists_pos < crp_pos < branch_state_pos, (
        "CRP-1 bullet must fall AFTER the `critique.md`-exists gate and "
        "BEFORE `### Branch state` — placement drifted (per /critique M2: "
        "deterministic post-L22/L23 placement for stable mini-CAD target)"
    )

    # NON-`-D` naming-class conformance (per ADR-019 / B1) — the SKILL.md
    # prose must describe CRP-1 as an audit-enforced gate (the phrase lives
    # in the Step 6 block, outside the Prerequisite-check scope), not a
    # `-D` heuristic.
    assert "CRP-1" in scoped
    assert (
        "audit-enforced gate" in BUILD
        and "NON-`-D` per ADR-019" in BUILD
    ), "CRP-1 NON-`-D` naming-class conformance prose missing or drifted"


def test_build_slice_crp_1_step_7b_preserves_skip_key():
    """Step 7b must instruct preserving the `critique-review-skip:` key.

    Defect class (per /critique B2): build-slice Step 7b rewrites
    milestone.md continuously; if the escape-hatch key is dropped, the
    Step 6 CRP-1 defense-in-depth re-run false-refuses a legitimately
    escape-hatched build.

    Rule reference: CRP-1; slice-026 /critique B2; ADR-024.
    """
    assert "Preserve the CRP-1 escape-hatch key" in BUILD
    assert "critique-review-skip:" in BUILD

