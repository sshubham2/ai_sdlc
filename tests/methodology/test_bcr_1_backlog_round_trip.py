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

# (slice-105 / ADR-095: the `/reflect` Step-2 round-trip anchors + the
# _reflect_step2_section helper + reflect-side Tests #4–#8 were removed here —
# BCR-1's /reflect round-trip-write is retired, so there is no Step-2 backlog
# prose left to pin. The /slice consume-side anchors + Tests #1–#3 below stay.)


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
