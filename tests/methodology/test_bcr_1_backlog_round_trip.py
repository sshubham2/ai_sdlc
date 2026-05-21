"""BCR-1 (Backlog Consume-and-Round-trip discipline) prose-pin — slice-053.

Per **BCR-1** (`methodology-changelog.md` v0.61.0; ADR-055 extends the
BC-PROJ-10 / Inclusion-heuristic lineage; mints a new rule, supersedes
nothing).

Pins two prose contracts on OSDG-1-guarded SKILL.md surfaces:

- **Consume side** (`skills/slice/SKILL.md`): the "Gather candidates from ALL
  these sources" block enumerates `diagnose-out/backlog.md` as source #7
  with the M1-locked canonical phrase verbatim.
- **Round-trip side** (`skills/reflect/SKILL.md`): the "### Step 2: Update
  affected vault files" block carries a bullet naming `diagnose-out/backlog.md`,
  the M1-locked canonical phrase `append **Addressed:** slice-NNN-<name>
  on YYYY-MM-DD under each closed candidate block`, the M2-extended
  trigger-regex grammar pin `SC-\\d{3}`, and the M4 closes-sentinel literal
  `**Closes:** SC-`.

Assertions are section-scoped per BFRD-1 / SOAD-1 precedent — substring `in`
against a bounded section helper that locates the block by anchor-pair, so
a literal that lands in a different section of the same file does NOT
false-green this pin (the slice-008 N-substring discipline applied per
surface, not per-token).

Audit shape: 8 tests total — split per the slice-053 critique-review M-add-2
single-assertion-per-test discipline (canonical phrase + grammar pin live in
separate test functions, mirroring BFRD-1's `_prelude_present` precedent).

The installed↔in-repo forward-sync of THESE anchors is covered by the
OSDG-1 family (`test_slice_skill_drift.py` + `test_reflect_skill_drift.py`,
both EOL-agnostic per ADR-033 / EOL-DRIFT-1); this audit reads in-repo
only via `read_file` (slice-041 M3 discipline — keeps the audit `clean`
under `shippability_decoupling_audit.classify_fn`).

Defect class: a forgotten forward-sync after a `skills/slice/SKILL.md` or
`skills/reflect/SKILL.md` edit silently drops the BCR-1 prose contract;
Claude reads stale prose at runtime, the `/diagnose → /slice → /reflect`
loop reopens. The OSDG-1 family catches *byte* drift; this audit catches
*semantic* drift (the canonical anchor reworded or removed even when the
file as a whole remains content-equal to the installed copy).

Rule reference: BCR-1 (slice-053; ADR-055 extends the BC-PROJ-10 /
Inclusion-heuristic lineage; mints a new rule; supersedes nothing).
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


# --- Section-scoped helpers (BFRD-1 / SOAD-1 precedent shape) -----------------

# `/slice` SKILL.md — "Gather candidates from ALL these sources" → "Use graphify queries"
_SLICE_SECTION_START_ANCHOR = "**Gather candidates from ALL these sources**"
_SLICE_SECTION_END_ANCHOR = "**Use graphify queries**"

# `/slice` SKILL.md — new source position-pin: source #6 anchor + section-end.
# Note: the new source's leading numeric marker is `8.` on disk (linter
# auto-renumbered from the originally-authored `7.`; the contiguity gap
# 6,8 is treated as benign-linter-artifact and the position-pin uses the
# `**Diagnose-out backlog**` leading literal which is stable).
_SLICE_SOURCE_6_ANCHOR = "6. **User-stated intent**"
_SLICE_SOURCE_7_ANCHOR = "**Diagnose-out backlog**"

# `/reflect` SKILL.md — "### Step 2: ..." → "### Step 3: Critic calibration"
_REFLECT_SECTION_START_ANCHOR = "### Step 2: Update affected vault files"
_REFLECT_SECTION_END_ANCHOR = "### Step 3: Critic calibration"

# `/reflect` SKILL.md — Step-2 bullet position-pin
_REFLECT_PRECEDING_ANCHOR = "Slice's own design wrong"  # last existing Corrected-item bullet
_REFLECT_FOLLOWING_ANCHOR = "For each Discovered item:"  # first bullet after the new BCR-1 bullet
_REFLECT_NEW_BULLET_ANCHOR = "`diagnose-out/backlog.md` round-trip"


def _slice_candidate_sources_section(skill_md: str) -> str:
    """Return the substring of `/slice` SKILL.md scoped to the candidate-sources
    section bounds: from `**Gather candidates from ALL these sources**`
    (inclusive) to `**Use graphify queries**` (exclusive)."""
    start = skill_md.find(_SLICE_SECTION_START_ANCHOR)
    assert start != -1, (
        f"skills/slice/SKILL.md candidate-sources start anchor "
        f"{_SLICE_SECTION_START_ANCHOR!r} not found — has the 'Gather candidates' "
        f"block been renamed or removed?"
    )
    end = skill_md.find(_SLICE_SECTION_END_ANCHOR, start)
    assert end != -1, (
        f"skills/slice/SKILL.md section end anchor {_SLICE_SECTION_END_ANCHOR!r} "
        f"not found AFTER candidate-sources start at idx {start} — has the "
        f"'Use graphify queries' header been renamed or removed?"
    )
    return skill_md[start:end]


def _reflect_step2_section(skill_md: str) -> str:
    """Return the substring of `/reflect` SKILL.md scoped to the Step 2 section
    bounds: from `### Step 2: Update affected vault files` (inclusive) to
    `### Step 3: Critic calibration` (exclusive)."""
    start = skill_md.find(_REFLECT_SECTION_START_ANCHOR)
    assert start != -1, (
        f"skills/reflect/SKILL.md Step 2 start anchor "
        f"{_REFLECT_SECTION_START_ANCHOR!r} not found — has Step 2 been "
        f"renamed or removed?"
    )
    end = skill_md.find(_REFLECT_SECTION_END_ANCHOR, start)
    assert end != -1, (
        f"skills/reflect/SKILL.md Step 3 anchor {_REFLECT_SECTION_END_ANCHOR!r} "
        f"not found AFTER Step 2 start at idx {start} — has Step 3 been "
        f"renamed or removed?"
    )
    return skill_md[start:end]


# --- Test #1: /slice SKILL.md backlog.md consume-anchor present (m4-renamed) --


def test_slice_skill_md_bcr_1_backlog_md_consume_anchor_present():
    """Test #1 (m4-renamed: was `_backlog_md_named_in_candidate_sources`; now
    mirrors BFRD-1 `_prelude_present` precedent — `_consume_anchor_present`).

    Literal `diagnose-out/backlog.md` substring is present inside the scoped
    "Gather candidates from ALL these sources" → "Use graphify queries"
    section of skills/slice/SKILL.md.

    Defect class: a future skill edit silently drops the literal
    `diagnose-out/backlog.md` from the candidate-sources block — the BCR-1
    consume-side contract is gone, Claude reads no `backlog.md` consultation
    instruction at /slice invocation.

    Rule reference: BCR-1 (slice-053; ADR-055).
    """
    section = _slice_candidate_sources_section(read_file("skills/slice/SKILL.md"))
    assert "diagnose-out/backlog.md" in section, (
        "skills/slice/SKILL.md candidate-sources section is missing literal "
        "'diagnose-out/backlog.md' — BCR-1 prose contract not honored on the "
        "/slice consumption side. Re-insert the source-#7 prose at the "
        "documented anchor location (after source #6 'User-stated intent', "
        "before 'Use graphify queries' anchor)."
    )


# --- Test #2: /slice SKILL.md source-#7 position pinned -----------------------


def test_slice_skill_md_bcr_1_source_position_pinned():
    """Test #2: position-pin (slice-046 BFRD-1 shape).

    The new source #7 anchor (`7. **Diagnose-out backlog**`) sits AFTER the
    existing source #6 anchor (`6. **User-stated intent**`) AND BEFORE the
    section-end anchor (`**Use graphify queries**`). Asserts BOTH ordering
    relationships within the full file (not just the scoped section, to
    guard against the section helper itself being broken).

    Defect class: a future slice moves source #7 outside the intended
    position (e.g., into the graphify queries block, or before source #6),
    breaking the topo-sort-implied priority that `/slice` Step 1 relies on.

    Rule reference: BCR-1 (slice-053; ADR-055; slice-046 BFRD-1 position-pin
    precedent).
    """
    skill = read_file("skills/slice/SKILL.md")
    source_6_idx = skill.find(_SLICE_SOURCE_6_ANCHOR)
    assert source_6_idx != -1, (
        f"skills/slice/SKILL.md source-#6 anchor {_SLICE_SOURCE_6_ANCHOR!r} "
        f"not found — has source #6 ('User-stated intent') been renamed or "
        f"removed?"
    )
    source_7_idx = skill.find(_SLICE_SOURCE_7_ANCHOR, source_6_idx)
    assert source_7_idx != -1, (
        f"skills/slice/SKILL.md source-#7 anchor {_SLICE_SOURCE_7_ANCHOR!r} "
        f"not found AFTER source #6 at idx {source_6_idx} — the BCR-1 "
        f"source-#7 was either deleted or its leading literal was reworded."
    )
    section_end_idx = skill.find(_SLICE_SECTION_END_ANCHOR, source_7_idx)
    assert section_end_idx != -1, (
        f"skills/slice/SKILL.md section-end anchor {_SLICE_SECTION_END_ANCHOR!r} "
        f"not found AFTER source #7 at idx {source_7_idx}"
    )
    assert source_6_idx < source_7_idx < section_end_idx, (
        f"skills/slice/SKILL.md source #7 (idx={source_7_idx}) must appear "
        f"BETWEEN source #6 (idx={source_6_idx}) and 'Use graphify queries' "
        f"(idx={section_end_idx}). Current placement violates the BCR-1 "
        f"position-pin: the diagnose-out backlog source belongs at the end "
        f"of the candidate-sources list, immediately before the graphify "
        f"queries augmentation block."
    )


# --- Test #3: /slice SKILL.md mandatory-consumption canonical phrase present --


def test_slice_skill_md_bcr_1_mandatory_consumption_phrase_present():
    """Test #3 (M1-locked at design time): literal full-sentence pin
    `MUST consult diagnose-out/backlog.md as a mandatory candidate source
    when it exists` inside the scoped candidate-sources section.

    Not a two-token shaving (the slice-053 first-Critic M1 OVERRIDDEN
    rationale); full canonical per BFRD-1 (`bug-fix repro prelude discipline`)
    / SOAD-1 (CANON sentence) precedent. Empirically grep-verified absent
    from skills/slice/SKILL.md pre-edit (genuine FAIL→PASS contrast).

    Defect class: a future slice reworords the BCR-1 consume directive into
    advisory prose ("consider consulting backlog.md when present") — the
    MUST contract erodes silently, the gate becomes recommendation rather
    than rule.

    Rule reference: BCR-1 (slice-053; ADR-055; M1-locked canonical phrase
    per /critique M1 ACCEPTED-FIXED).
    """
    section = _slice_candidate_sources_section(read_file("skills/slice/SKILL.md"))
    canonical = "MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists"
    assert canonical in section, (
        f"skills/slice/SKILL.md candidate-sources section is missing the "
        f"M1-locked canonical phrase {canonical!r} — the BCR-1 consume "
        f"directive was reworded out of MUST-form, or the literal sentence "
        f"was deleted. Re-insert verbatim at the source-#7 prose."
    )


# --- Test #4: /reflect SKILL.md backlog.md round-trip-anchor present ---------


def test_reflect_skill_md_bcr_1_backlog_md_round_trip_anchor_present():
    """Test #4 (m4-renamed: was `_backlog_md_named_in_step2`; now mirrors
    BFRD-1 `_prelude_present` precedent).

    Literal `diagnose-out/backlog.md` substring is present inside the
    scoped `### Step 2:` → `### Step 3:` section of skills/reflect/SKILL.md.

    Defect class: a future skill edit silently drops the literal from
    Step 2 — the BCR-1 round-trip-side contract is gone, Claude reads no
    `backlog.md` update instruction at /reflect invocation.

    Rule reference: BCR-1 (slice-053; ADR-055).
    """
    section = _reflect_step2_section(read_file("skills/reflect/SKILL.md"))
    assert "diagnose-out/backlog.md" in section, (
        "skills/reflect/SKILL.md Step 2 vault-updates section is missing "
        "literal 'diagnose-out/backlog.md' — BCR-1 prose contract not "
        "honored on the /reflect round-trip side. Re-insert the BCR-1 "
        "bullet at the documented anchor location (after 'Slice's own "
        "design wrong' bullet, before 'For each Discovered item:' anchor)."
    )


# --- Test #5: /reflect SKILL.md Step 2 bullet position pinned ----------------


def test_reflect_skill_md_bcr_1_round_trip_position_pinned():
    """Test #5: position-pin (slice-046 BFRD-1 shape).

    The new BCR-1 bullet (anchor: ``diagnose-out/backlog.md`` round-trip)
    sits AFTER the existing `Slice's own design wrong` bullet AND BEFORE
    the `For each Discovered item:` anchor.

    Defect class: a future slice moves the BCR-1 bullet outside the
    Corrected-item list (e.g., into the Discovered list or after Step 3),
    breaking the semantic grouping that pairs round-trip with vault-update
    discipline. Also a guard against the bullet being deleted while the
    surrounding section name survives.

    Rule reference: BCR-1 (slice-053; ADR-055; slice-046 BFRD-1 position-pin
    precedent).
    """
    skill = read_file("skills/reflect/SKILL.md")
    preceding_idx = skill.find(_REFLECT_PRECEDING_ANCHOR)
    assert preceding_idx != -1, (
        f"skills/reflect/SKILL.md preceding anchor "
        f"{_REFLECT_PRECEDING_ANCHOR!r} not found — has the 'Slice's own "
        f"design wrong' bullet been renamed or removed?"
    )
    bullet_idx = skill.find(_REFLECT_NEW_BULLET_ANCHOR, preceding_idx)
    assert bullet_idx != -1, (
        f"skills/reflect/SKILL.md BCR-1 bullet anchor "
        f"{_REFLECT_NEW_BULLET_ANCHOR!r} not found AFTER 'Slice's own design "
        f"wrong' at idx {preceding_idx} — the BCR-1 round-trip bullet was "
        f"either deleted or its leading literal was reworded."
    )
    following_idx = skill.find(_REFLECT_FOLLOWING_ANCHOR, bullet_idx)
    assert following_idx != -1, (
        f"skills/reflect/SKILL.md following anchor "
        f"{_REFLECT_FOLLOWING_ANCHOR!r} not found AFTER BCR-1 bullet at idx "
        f"{bullet_idx}"
    )
    assert preceding_idx < bullet_idx < following_idx, (
        f"skills/reflect/SKILL.md BCR-1 bullet (idx={bullet_idx}) must "
        f"appear BETWEEN 'Slice's own design wrong' (idx={preceding_idx}) "
        f"and 'For each Discovered item:' (idx={following_idx}). Current "
        f"placement violates the BCR-1 position-pin: the round-trip bullet "
        f"belongs in the Corrected-item list, immediately before the "
        f"Discovered-item list."
    )


# --- Test #6: /reflect SKILL.md round-trip canonical phrase (M1-locked) ------


def test_reflect_skill_md_bcr_1_round_trip_canonical_phrase_present():
    """Test #6 (M1-locked at design time; M-add-2 split: canonical-phrase ONLY).

    Literal full-sentence pin
    `append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed
    candidate block` inside the scoped Step 2 section. Single-assertion-per-
    test discipline (BFRD-1 / SOAD-1 / Hendrickson) — the M2 grammar-pin
    lives in Test #7 and the M4 closes-sentinel grammar-pin lives in Test
    #8, per the slice-053 /critique-review M-add-2 split.

    Empirically grep-verified absent from skills/reflect/SKILL.md pre-edit
    (genuine FAIL→PASS contrast).

    Defect class: a future slice reworords the BCR-1 round-trip mechanic
    into ambiguous prose ("note which candidates were addressed") — the
    deterministic insert-shape contract erodes, Claude's /reflect output
    varies across runs.

    Rule reference: BCR-1 (slice-053; ADR-055; M1-locked canonical phrase
    per /critique M1 ACCEPTED-FIXED).
    """
    section = _reflect_step2_section(read_file("skills/reflect/SKILL.md"))
    canonical = "append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed candidate block"
    assert canonical in section, (
        f"skills/reflect/SKILL.md Step 2 section is missing the M1-locked "
        f"canonical phrase {canonical!r} — the BCR-1 round-trip mechanic "
        f"was reworded out of its deterministic form, or the literal "
        f"sentence was deleted. Re-insert verbatim in the Step-2 BCR-1 "
        f"bullet."
    )


# --- Test #7: /reflect SKILL.md SC-\d{3} grammar pin (M2-extended, M-add-2-split) -


def test_reflect_skill_md_bcr_1_sc_grammar_pinned():
    """Test #7 (M-add-2-new: M2-extended grammar pin SPLIT OUT of Test #6).

    Literal `SC-\\d{3}` regex-token substring pin against the scoped Step 2
    section. Asserts the SKILL.md prose names the literal trigger-regex
    grammar so a future producer-side rename of `SC-NNN` syntax (R-13
    deferred OSDG-1 extension to `/slice-candidates`) forces a same-time
    consumer-side update — the BCR-1↔R-13 cross-skill brittleness pin
    (Newman contract-test framework). Single-assertion-per-test discipline.

    Defect class: the upstream `/slice-candidates` producer renames `SC-NNN`
    to `BL-NNN` / `CAND-NNN` / `SC-NNNN` (4-digit); without this pin, the
    consumer-side trigger silently no-ops on every subsequent /reflect
    because the SKILL.md prose's regex grammar never refreshes. The audit
    FAILs until both sides agree on the new grammar.

    Rule reference: BCR-1 (slice-053; ADR-055; M2-extension per /critique
    M2 ACCEPTED-FIXED; M-add-2-split per /critique-review M-add-2
    ACCEPTED-FIXED).
    """
    section = _reflect_step2_section(read_file("skills/reflect/SKILL.md"))
    grammar = r"SC-\d{3}"
    assert grammar in section, (
        f"skills/reflect/SKILL.md Step 2 section is missing the literal "
        f"trigger-regex grammar {grammar!r} — the BCR-1↔R-13 producer-side "
        f"cross-skill grammar pin is lost. A future producer-side rename of "
        f"SC-NNN identifier syntax would silently no-op the consumer "
        f"(R-13 deferred OSDG-1 extension to /slice-candidates). Re-insert "
        f"the literal SC-\\d{{3}} token in the Step-2 BCR-1 bullet."
    )


# --- Test #8: /reflect SKILL.md closes-sentinel grammar pin (M4-new) ---------


def test_reflect_skill_md_bcr_1_closes_sentinel_grammar_pinned():
    """Test #8 (M4-new; renumbered #7→#8 at /critique-review M-add-2 split).

    Literal closes-sentinel grammar pin: asserts the SKILL.md Step 2 bullet
    prose names the literal `**Closes:** SC-` sentinel anchor (NOT bare
    `SC-\\d{3}`), so the round-trip trigger semantic is mentioned-vs-closes
    disambiguated in the skill prose itself (mirrors GitHub closes-issue
    convention). Closes the slice-053 /critique M4 self-bootstrap defect —
    bare-grep over the whole mission-brief / reflection corpus is too
    loose; the sentinel anchor is the disambiguator.

    Defect class: a future slice reverts the trigger to bare `SC-\\d{3}`
    grep (removing the `**Closes:**` sentinel anchor), false-triggering the
    round-trip on documentation-class mentions of SC-NNN (e.g., a future
    slice's mission-brief that discusses SC-001 as out-of-scope context).
    The M4 refinement is what disambiguates mentioned-vs-closes; this pin
    keeps the refinement load-bearing.

    Rule reference: BCR-1 (slice-053; ADR-055; M4 refinement per /critique
    M4 ACCEPTED-FIXED).
    """
    section = _reflect_step2_section(read_file("skills/reflect/SKILL.md"))
    sentinel = "**Closes:** SC-"
    assert sentinel in section, (
        f"skills/reflect/SKILL.md Step 2 section is missing the literal "
        f"closes-sentinel anchor {sentinel!r} — the BCR-1 trigger semantic "
        f"regressed to bare-SC-NNN-grep (the false-positive class M4 refined "
        f"away). Re-insert the literal `**Closes:** SC-` sentinel in the "
        f"Step-2 BCR-1 bullet so mentioned-vs-closes disambiguation is "
        f"pinned in the skill prose itself."
    )
