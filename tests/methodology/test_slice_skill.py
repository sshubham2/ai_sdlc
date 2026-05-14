"""Pin load-bearing prose in skills/slice/SKILL.md."""
from tests.methodology.conftest import read_file

SLICE = read_file("skills/slice/SKILL.md")


def test_slice_scope_limits():
    """A slice is ≤5 acceptance criteria and ≤1 day of AI work.

    Defect class: Slice bloat — a 12-AC, 3-day slice defeats mid-slice smoke
    gates and reflection. Without enforced limits, slices grow into sprints.
    Rule reference: META-2.
    """
    assert "≤5 acceptance criteria" in SLICE
    assert "≤1 day of AI implementation work" in SLICE


def test_slice_lists_mandatory_critic_triggers():
    """Always-mandatory Critic triggers must include the load-bearing categories.

    Defect class: Trigger erosion — quietly dropping any of these triggers
    means a low-tier slice that touches auth/contracts/data/sync skips the
    Critic. That's exactly the case where the Critic earns its keep.
    Rule reference: META-2.
    """
    # Find the Always-mandatory section and verify all triggers present
    assert "Always mandatory Critic" in SLICE
    # Trigger list — these substrings appear in the bulleted triggers
    assert "Auth / authz" in SLICE
    assert "API contracts" in SLICE
    assert "Data model changes" in SLICE
    assert "Multi-device" in SLICE
    assert "External integrations" in SLICE


def test_slice_verb_object_naming_rule():
    """Slice names must be verb-object, not phase-N or vague nouns.

    Defect class: Vague slice names (`phase-2`, `slice-N`, `improvements`)
    defeat the discipline of mission-brief intent and verification planning.
    Rule reference: META-2.
    """
    assert "VERB-OBJECT names only" in SLICE


# --- Slice-010 / MCT-1: In-house methodology surfaces mandatory-Critic trigger ---
#
# Per MCT-1 (`methodology-changelog.md` v0.25.0): the `/slice` skill's Step 4a
# "Always mandatory Critic" section gains a new bullet for in-house methodology
# surfaces (skill prose, agent prompts, custom build / lint / audit tooling,
# methodology rules) PLUS an adjacent evidence prose paragraph appended after
# the existing "When producing the mission brief..." paragraph (per slice-010
# Critic M1 split — keeps the bullet stylistically uniform with the existing 7
# bullets while pinning the empirical-evidence-base anchors in adjacent prose).
#
# Per slice-008 M2 N-substring discipline + slice-009 M3 N-surface discipline:
# the substantive canonical phrase `In-house methodology surfaces` is pinned
# across N=3 surfaces (this file + `test_methodology_changelog.py` v0.25.0 pin
# in BOTH in-repo + installed methodology-changelog.md).
#
# Per slice-009 DEVIATION-1 lesson: canonical literal `voluntary Critic` is
# case-sensitive lowercase-v; the prose MUST place this phrase mid-sentence to
# honor literal case without bullet-start auto-capitalization.
#
# Per slice-009 DEVIATION-2 lesson + slice-005 algorithm-path-conformance: the
# location-pin test uses scoped `text.find()` chained off unique anchors;
# anchor uniqueness empirically verified pre-AC-lock.
#
# Per slice-010 Critic M3 ACCEPTED-PENDING: the 5th test pins ≥2 of 4 sub-class
# anchors so the descriptive sub-class text doesn't drift unpinned.

# ---- Section anchors (empirically verified unique at slice-010 design time) ----

_SECTION_START_ANCHOR = "Always mandatory Critic"  # unique L165 at slice-010 design time
_SECTION_END_ANCHOR = "### Step 5:"  # unique markdown H3 header
_BULLET_PRECEDING_ANCHOR = "- Security-sensitive paths"  # unique L171 at slice-010 design time
_BULLET_FOLLOWING_ANCHOR = "- Heavy mode (always)"  # unique L172 at slice-010 design time


def _step4a_section(skill_md: str) -> str:
    """Return the substring of skill_md scoped to the Step 4a "Always mandatory
    Critic" section. Bounds: from `Always mandatory Critic` (inclusive) to
    `### Step 5:` (exclusive). Scoped section captures both the bullet list
    AND the evidence prose paragraph appended below the "When producing..."
    paragraph (per slice-010 Critic M1 split — widened end anchor from
    `Heavy mode (always)` to `### Step 5:`).
    """
    start = skill_md.find(_SECTION_START_ANCHOR)
    assert start != -1, (
        f"Step 4a section start anchor {_SECTION_START_ANCHOR!r} not found in "
        f"skills/slice/SKILL.md — has the Step 4a section been renamed?"
    )
    end = skill_md.find(_SECTION_END_ANCHOR, start)
    assert end != -1, (
        f"Step 4a section end anchor {_SECTION_END_ANCHOR!r} not found AFTER "
        f"the start anchor at idx {start} — has Step 5 been renamed or removed?"
    )
    return skill_md[start:end]


def test_slice_step4a_mandatory_critic_section_contains_in_house_methodology_surfaces_bullet():
    """AC #1 row 1: the canonical literal `In-house methodology surfaces`
    appears within the Step 4a "Always mandatory Critic" section bounds.

    Pins the new bullet's title canonical literal (capitalized-I bullet-title
    form per slice-009 DEVIATION-1 mitigation — bullet start gets natural
    capitalization without forcing case manipulation).

    Defect class: if a future slice deletes the bullet or rewords its title,
    this test surfaces the drift at /validate-slice.

    Rule reference: MCT-1 (slice-010).
    """
    section = _step4a_section(SLICE)

    assert "In-house methodology surfaces" in section, (
        "skills/slice/SKILL.md Step 4a section is missing canonical literal "
        "'In-house methodology surfaces' — the MCT-1 bullet was removed or "
        "renamed. Re-add the bullet between the existing `Security-sensitive "
        "paths` bullet and the `Heavy mode (always)` bullet per "
        "slice-010 design.md."
    )

    # File-class anchor: bullet body must name at least one of the 4 in-house
    # surface families. Design selects all 4 for canonical-inventory
    # completeness; AC #1 row 1 asserts >=1.
    file_class_anchors = (
        "skills/*/SKILL.md",
        "agents/*.md",
        "tools/**/*.py",
        "methodology-changelog.md",
    )
    present = [a for a in file_class_anchors if a in section]
    assert len(present) >= 1, (
        f"skills/slice/SKILL.md Step 4a section is missing all 4 file-class "
        f"anchors {file_class_anchors!r} — the MCT-1 bullet's body lost its "
        f"in-house surface family references. Found 0 of 4."
    )


def test_slice_step4a_in_house_methodology_bullet_location_between_security_paths_and_heavy_mode():
    """AC #1 row 2: the new `In-house methodology surfaces` bullet appears
    BETWEEN the existing `Security-sensitive paths` bullet and the existing
    `Heavy mode (always)` bullet. Pins the bullet's position within the
    bullet list (content-trigger bullets grouped before the mode-meta closer).

    Per slice-009 Critic M1 location-pin discipline + slice-005 + slice-009
    DEVIATION-2 algorithm-path-conformance: anchor uniqueness empirically
    verified at design time (each of the 3 anchors appears exactly once in
    `skills/slice/SKILL.md`); scoped `text.find()` chained off prior anchor
    pre-empts `.find()`-collision class.

    Defect class: if the new bullet is inserted outside the bullet list (e.g.,
    in narrative prose), or placed before `Security-sensitive paths`, or after
    `Heavy mode (always)`, this test surfaces the misplacement.

    Rule reference: MCT-1 (slice-010); slice-009 Critic M1 location-pin.
    """
    # Section start anchor (unique)
    section_start = SLICE.find(_SECTION_START_ANCHOR)
    assert section_start != -1, (
        f"Section start anchor {_SECTION_START_ANCHOR!r} not found"
    )

    # Bullet anchors -- both scoped to start AFTER section_start to avoid
    # any cross-section collision (defensive -- anchor-uniqueness empirically
    # verified, but scoped find is the slice-009 DEVIATION-2 mitigation
    # discipline).
    security_paths_idx = SLICE.find(_BULLET_PRECEDING_ANCHOR, section_start)
    assert security_paths_idx != -1, (
        f"Preceding-bullet anchor {_BULLET_PRECEDING_ANCHOR!r} not found "
        f"after section start at idx {section_start}"
    )

    heavy_mode_idx = SLICE.find(_BULLET_FOLLOWING_ANCHOR, security_paths_idx)
    assert heavy_mode_idx != -1, (
        f"Following-bullet anchor {_BULLET_FOLLOWING_ANCHOR!r} not found "
        f"after preceding-bullet anchor at idx {security_paths_idx}"
    )

    # New bullet's canonical phrase must appear strictly between them
    new_bullet_idx = SLICE.find(
        "In-house methodology surfaces", security_paths_idx
    )
    assert new_bullet_idx != -1, (
        "New bullet's canonical phrase 'In-house methodology surfaces' not "
        "found after the preceding `Security-sensitive paths` bullet"
    )
    assert security_paths_idx < new_bullet_idx < heavy_mode_idx, (
        f"New bullet 'In-house methodology surfaces' (idx={new_bullet_idx}) "
        f"must appear BETWEEN `Security-sensitive paths` (idx="
        f"{security_paths_idx}) and `Heavy mode (always)` (idx={heavy_mode_idx})."
        f" Current placement violates the bullet position-pin: content-trigger "
        f"bullets must be grouped before the `Heavy mode (always)` mode-meta closer."
    )


def test_slice_step4a_evidence_paragraph_cites_n_9_and_voluntary_critic():
    """AC #1 row 3: the canonical literals `N=9/9` AND `voluntary Critic`
    (case-sensitive lowercase-v) both appear within the Step 4a section bounds.

    Per slice-010 Critic M1 split: these canonical literals live in the
    evidence prose paragraph appended below the existing "When producing the
    mission brief..." paragraph (NOT in the bullet itself -- the bullet stays
    stylistically uniform with the existing 7 bullets). The section bounds
    (`Always mandatory Critic` start -> `### Step 5:` end) capture both the
    bullet list and the evidence paragraph.

    Per slice-009 DEVIATION-1 mitigation: `voluntary Critic` is lowercase-v;
    the prose must place this phrase mid-sentence (not at sentence start)
    so markdown convention doesn't pull toward capitalization.

    Defect class: if a future slice deletes the evidence paragraph or rewrites
    it without the empirical-evidence anchors, this test surfaces the drift.

    Rule reference: MCT-1 (slice-010).
    """
    section = _step4a_section(SLICE)

    assert "N=9/9" in section, (
        "skills/slice/SKILL.md Step 4a section is missing empirical-evidence "
        "anchor 'N=9/9' -- the evidence prose paragraph below the bullet list "
        "was removed or its N-count framing changed. Re-add or restore."
    )

    # Case-sensitive: lowercase 'voluntary Critic' (slice-009 DEVIATION-1
    # mitigation -- assert exact case)
    assert "voluntary Critic" in section, (
        "skills/slice/SKILL.md Step 4a section is missing pattern-name "
        "canonical literal 'voluntary Critic' (case-sensitive lowercase-v) -- "
        "either the phrase is absent OR it was auto-capitalized to "
        "'Voluntary Critic' at sentence start (slice-009 DEVIATION-1 trap "
        "recurrence). Re-structure prose to keep the phrase mid-sentence."
    )


def test_slice_step4a_evidence_paragraph_cites_at_least_two_cross_cutting_tooling_slices():
    """AC #2: the Step 4a section's evidence prose paragraph cites at least
    TWO of the 4 cross-slice example anchors {slice-006, slice-007,
    slice-008, slice-009} -- grounding the N=9/9 evidence base claim in
    concrete reflection-record references.

    Per slice-010 design: all 4 anchors are included for completeness; AC #2
    asserts >=2 (allows minor prose refinement without test churn).

    Defect class: if a future slice rewrites the evidence paragraph to drop
    all concrete sub-class examples, the empirical-evidence base claim
    becomes unverifiable.

    Rule reference: MCT-1 (slice-010).
    """
    section = _step4a_section(SLICE)

    cross_slice_anchors = ("slice-006", "slice-007", "slice-008", "slice-009")
    present = [a for a in cross_slice_anchors if a in section]
    assert len(present) >= 2, (
        f"skills/slice/SKILL.md Step 4a section cites only {len(present)} of "
        f"4 cross-slice example anchors {cross_slice_anchors!r}; need >=2. "
        f"Found: {present}. The evidence prose paragraph lost its concrete "
        f"reflection-record references."
    )


def test_slice_step4a_evidence_paragraph_cites_at_least_two_sub_class_anchors():
    """AC #2 sub-row per slice-010 Critic M3 ACCEPTED-PENDING: the evidence
    prose paragraph cites at least TWO of the 4 sub-class Critic-catch anchors
    {INST-1 inventory drift, install-time rename, negative-anchor uniformity,
    recursive self-application} -- pinning the sub-class evidence so a future
    cleanup deleting them surfaces as a test failure.

    Per slice-009 N-substring schema-pin discipline (referenced in slice-010
    mission-brief): substantive prose anchors should be pinned. Without this
    test the 4 sub-class anchors are descriptive-only and a drift vector.

    Rule reference: MCT-1 (slice-010); slice-010 Critic M3 (ACCEPTED-PENDING
    at /critique, applied at /build-slice Phase 1a).
    """
    section = _step4a_section(SLICE)

    sub_class_anchors = (
        "INST-1 inventory drift",
        "install-time rename",
        "negative-anchor uniformity",
        "recursive self-application",
    )
    present = [a for a in sub_class_anchors if a in section]
    assert len(present) >= 2, (
        f"skills/slice/SKILL.md Step 4a section cites only {len(present)} of "
        f"4 sub-class Critic-catch anchors {sub_class_anchors!r}; need >=2. "
        f"Found: {present}. The evidence prose paragraph lost its concrete "
        f"sub-class references -- a future reader can no longer verify which "
        f"specific past Critic-catches the N=9/9 evidence base draws on."
    )


# --- Slice-020 / BFRD-1 bug-fix repro prelude pinning ---
#
# Per BFRD-1 (`methodology-changelog.md` v0.34.0): `skills/slice/SKILL.md`
# Step 3c codifies the bug-fix repro prelude discipline. Section sits
# between existing `### Step 3b: If user has their own idea` and
# `### Step 4: Define the slice` anchors. Three prose-pin tests:
# (1) `_prelude_present` asserts literal canonical phrase
# `bug-fix repro prelude discipline` per /critique-review M2 SUSPICIOUS
# clarification (rationale-strengthening locks N=3 surface schema-pin
# into concrete test enforcement, not aspirational "phrase appears
# naturally in section opener" rationale);
# (2) `_prelude_location_pinned` scoped-find between Step 3b end-anchor
# and Step 4 header-anchor per slice-009 DEVIATION-2 algorithm-path-
# conformance discipline N=11 stable;
# (3) `_verification_mechanism_present` asserts literal canonical phrase
# `shippability.md grep verification` per /critique B2 + /critique-
# review M-add-2 ACCEPTED-FIXED Option (a).

_STEP3C_START_ANCHOR = "### Step 3c: Bug-fix prelude (BFRD-1)"
_STEP3C_PRECEDING_ANCHOR = "### Step 3b: If user has their own idea"
_STEP3C_FOLLOWING_ANCHOR = "### Step 4: Define the slice"


def _step3c_section(skill_md: str) -> str:
    """Return the substring of skill_md scoped to the Step 3c section
    bounds. Bounds: from `### Step 3c: Bug-fix prelude (BFRD-1)`
    (inclusive) to `### Step 4: Define the slice` (exclusive).
    """
    start = skill_md.find(_STEP3C_START_ANCHOR)
    assert start != -1, (
        f"Step 3c section start anchor {_STEP3C_START_ANCHOR!r} not found "
        f"in skills/slice/SKILL.md — has Step 3c been renamed or removed?"
    )
    end = skill_md.find(_STEP3C_FOLLOWING_ANCHOR, start)
    assert end != -1, (
        f"Step 4 anchor {_STEP3C_FOLLOWING_ANCHOR!r} not found AFTER "
        f"Step 3c start at idx {start} — has Step 4 been renamed or "
        f"removed, or did Step 3c insertion break the file structure?"
    )
    return skill_md[start:end]


def test_slice_skill_md_bfrd_1_prelude_present():
    """AC #2 row 1: literal canonical phrase `bug-fix repro prelude
    discipline` appears within the Step 3c section bounds.

    Per slice-020 /critique-review M2 SUSPICIOUS ACCEPTED-FIXED
    clarification (design.md "Prose-pin test assertion locks"): the
    `_prelude_present` test asserts the literal canonical phrase, NOT
    merely `BFRD-1` rule ID. This transitively requires Step 3c body
    to contain the literal phrase, locking the design.md L93
    commitment via test enforcement (closes the first-Critic M2
    OVERRIDDEN rationale's "phrase appears naturally in section
    opener" claim into a concrete test-assertion contract that
    survives /build-slice Phase 1 prose drafting).

    Defect class: if a future slice deletes the canonical phrase from
    Step 3c (or rewords as "bug-fix repro prelude" without the
    "discipline" word), the N=3 surface schema-pin breaks at the
    skill-prose surface. Test surfaces drift at /validate-slice.
    Rule reference: BFRD-1 (slice-020 AC #2, /critique-review M2).
    """
    section = _step3c_section(SLICE)
    assert "bug-fix repro prelude discipline" in section, (
        "skills/slice/SKILL.md Step 3c section is missing literal "
        "canonical phrase 'bug-fix repro prelude discipline' — the "
        "N=3 surface schema-pin is broken at the skill-prose surface. "
        "Re-add the phrase to Step 3c's opening sentence per design.md "
        "Step 3c content structure item 2 + 'Prose-pin test assertion "
        "locks' clarification."
    )


def test_slice_skill_md_bfrd_1_prelude_location_pinned():
    """AC #2 row 2: Step 3c section sits BETWEEN existing Step 3b
    section and Step 4 section header. Pins the section's position
    within the skill file's overall step structure.

    Per slice-009 DEVIATION-2 algorithm-path-conformance discipline
    N=11 stable: anchor uniqueness empirically verified at design
    time (each of the 3 anchors appears exactly once in
    `skills/slice/SKILL.md`); scoped `text.find()` chained off prior
    anchor pre-empts `.find()`-collision class.

    Defect class: if a future slice moves Step 3c outside the
    intended position (e.g., into Step 2 or after Step 4), this
    test surfaces the misplacement. Step 3c MUST sit at the
    candidate-selection→slice-definition inflection point.
    Rule reference: BFRD-1 (slice-020 AC #2; slice-009 DEVIATION-2
    + slice-017 TPHD-1 location-pin discipline N=11 stable).
    """
    step3b_idx = SLICE.find(_STEP3C_PRECEDING_ANCHOR)
    assert step3b_idx != -1, (
        f"Step 3b preceding anchor {_STEP3C_PRECEDING_ANCHOR!r} not "
        f"found in skills/slice/SKILL.md"
    )
    step3c_idx = SLICE.find(_STEP3C_START_ANCHOR, step3b_idx)
    assert step3c_idx != -1, (
        f"Step 3c start anchor {_STEP3C_START_ANCHOR!r} not found "
        f"after Step 3b anchor at idx {step3b_idx}"
    )
    step4_idx = SLICE.find(_STEP3C_FOLLOWING_ANCHOR, step3c_idx)
    assert step4_idx != -1, (
        f"Step 4 following anchor {_STEP3C_FOLLOWING_ANCHOR!r} not "
        f"found after Step 3c at idx {step3c_idx}"
    )
    assert step3b_idx < step3c_idx < step4_idx, (
        f"Step 3c (idx={step3c_idx}) must appear BETWEEN Step 3b "
        f"(idx={step3b_idx}) and Step 4 (idx={step4_idx}). Current "
        f"placement violates the section position-pin: bug-fix "
        f"prelude must sit at the candidate-selection→slice-"
        f"definition inflection point."
    )


def test_slice_skill_md_bfrd_1_verification_mechanism_present():
    """AC #2 row 3: literal canonical phrase `shippability.md grep
    verification` appears within the Step 3c section bounds.

    Per slice-020 /critique B2 + /critique-review M-add-2 ACCEPTED-
    FIXED Option (a): verification mechanism is `shippability.md grep
    verification` for `tests/bugs/*` Command-cell match + verbal-
    claim-with-path fallback. Canonical phrase pinned in skill prose
    per design.md "Prose-pin test assertion locks" clarification.

    Defect class: future slice strips the verification mechanism from
    Step 3c; BFRD-1 becomes advisory-only without an enforcement
    primitive (RPCD-1 sub-mode (b) NEW-status/token allowlist-audit
    class regression at the BFRD-1 surface).
    Rule reference: BFRD-1 (slice-020 AC #2, /critique B2 +
    /critique-review M-add-2 ACCEPTED-FIXED Option (a)).
    """
    section = _step3c_section(SLICE)
    assert "shippability.md grep verification" in section, (
        "skills/slice/SKILL.md Step 3c section is missing literal "
        "canonical phrase 'shippability.md grep verification' — "
        "verification mechanism canonical-phrase pin broken per "
        "/critique B2 ACCEPTED-FIXED + /critique-review M-add-2 "
        "ACCEPTED-FIXED Option (a). Re-add the phrase to Step 3c's "
        "verification-mechanism bullet per design.md Step 3c content "
        "structure item 4."
    )
