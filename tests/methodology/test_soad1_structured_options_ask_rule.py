"""SOAD-1 (Structured-Options-Ask Discipline) prose-pin — slice-048.

Per **SOAD-1** (`methodology-changelog.md` v0.56.0; ADR-050 generalizes
ADR-048's gate-specific structured-options-ask requirement into a
pipeline-wide skill-ask discipline).

The canonical SOAD-1 sentence MUST appear verbatim inside each of the
four CLAUDE.md template fenced blocks the openers emit
(`/triage` Step 5b Fresh+Append; `/adopt` Step 10 Fresh+Append) AND in
this repo's own project-root `CLAUDE.md` (self-hosting dogfood).

Assertions are section-scoped per fenced block (critique M1 — a repo-
global `.count()` would pass even if both hits landed in the Fresh block
and Append was missed), modeled on the slice-021 precedent
`test_root_claude_md_branch_per_slice_rule.py` (`content.find(section)`
-> bounded slice -> substring assert).

The M-add-1 self-consistency guard (critique-review DR-1, user-ratified
fix option (a)) pins that the host templates no longer carry the bare
free-text hard-rule ASK literal SOAD-1 forbids, and that the reworded
hard-rule ASK directs a structured-options ask.

Defect class: SOAD-1 silently dropped/reworded out of any opener
template (every future /triage|/adopt project would ship a CLAUDE.md
without the discipline) or this repo's CLAUDE.md (self-hosting dogfood
lost) — or the slice's own self-violation (SOAD-1 shipped beside a bare
free-text ASK) silently regressing.

Rule reference: SOAD-1 (slice-048; ADR-050; generalizes ADR-048,
mints a new rule, supersedes nothing).
"""
from __future__ import annotations

import pytest

from tests.methodology.conftest import read_file

# The single canonical SOAD-1 sentence — reused VERBATIM in all 5 surfaces.
# The em-dash is U+2014 (matches the literal authored into the surfaces).
CANON = (
    "**Ask discipline**: when a skill needs user input, present it as "
    "structured options (with a recommended choice) via the "
    "`AskUserQuestion` tool — never a bare free-text prompt. A bare prose "
    "ask is legitimate only where `AskUserQuestion` genuinely cannot model "
    "the input. Rationale: Claude Code notifies the user only on options "
    "prompts; a free-text question blocks silently."
)

# The exact bare free-text hard-rule ASK literal SOAD-1 forbids. Present
# pre-slice-048 in triage Fresh / adopt Fresh / this repo's CLAUDE.md;
# the M-add-1 (option a) reword removes it from every SOAD-1 surface.
BARE_ASK = '**ASK** the user: "Run `/slice` first'


def _fenced_block_after(content: str, heading_marker: str, *, src: str) -> str:
    """Return the body of the first ```-fenced block after `heading_marker`.

    Section-scoped extraction (slice-021 precedent shape): locate the
    heading, then the next ```-fence open, then its matching ```-fence
    close, and return the text strictly between them.
    """
    h = content.find(heading_marker)
    assert h != -1, f"{src}: heading marker {heading_marker!r} not found"
    fence_open = content.find("```", h)
    assert fence_open != -1, f"{src}: no opening ``` after {heading_marker!r}"
    body_start = content.find("\n", fence_open)
    assert body_start != -1, f"{src}: malformed fence after {heading_marker!r}"
    fence_close = content.find("```", body_start)
    assert fence_close != -1, f"{src}: no closing ``` after {heading_marker!r}"
    return content[body_start:fence_close]


# (surface_id, repo_relpath, heading_marker) — heading_marker None ⇒ whole file
_SKILL_SURFACES = [
    ("triage-fresh", "skills/triage/SKILL.md", "#### Fresh template"),
    ("triage-append", "skills/triage/SKILL.md", "#### Append template"),
    ("adopt-fresh", "skills/adopt/SKILL.md", "#### Fresh brownfield template"),
    ("adopt-append", "skills/adopt/SKILL.md", "#### Append template"),
]


@pytest.mark.parametrize("surface_id,relpath,marker", _SKILL_SURFACES)
def test_soad1_canonical_sentence_in_each_opener_template_block(
    surface_id: str, relpath: str, marker: str
) -> None:
    """AC2/AC5: the canonical SOAD-1 sentence is verbatim inside EACH of
    the 4 opener template fenced blocks (section-scoped, not global count).
    """
    block = _fenced_block_after(read_file(relpath), marker, src=surface_id)
    assert CANON in block, (
        f"{surface_id} ({relpath}): the canonical SOAD-1 sentence is not "
        f"present verbatim inside the {marker!r} fenced template block — "
        f"SOAD-1 missing/reworded out of an opener template (slice-048 AC2)"
    )


def test_soad1_canonical_sentence_in_repo_root_claude_md() -> None:
    """AC3: this repo's own project-root CLAUDE.md carries SOAD-1 verbatim
    inside an `## Ask discipline` section (self-hosting dogfood)."""
    content = read_file("CLAUDE.md")
    assert "## Ask discipline" in content, (
        "root CLAUDE.md must carry an `## Ask discipline` section (SOAD-1 "
        "self-hosting dogfood, slice-048 AC3)"
    )
    sect = content.find("## Ask discipline")
    nxt = content.find("\n## ", sect + 1)
    block = content[sect:nxt] if nxt != -1 else content[sect:]
    assert CANON in block, (
        "root CLAUDE.md `## Ask discipline` section must contain the "
        "canonical SOAD-1 sentence verbatim (slice-048 AC3)"
    )


@pytest.mark.parametrize("surface_id,relpath,marker", _SKILL_SURFACES)
def test_madd1_no_bare_freetext_hardrule_ask_in_opener_templates(
    surface_id: str, relpath: str, marker: str
) -> None:
    """M-add-1 (DR-1, fix option a): no opener template fenced block may
    carry the bare free-text hard-rule ASK literal SOAD-1 forbids, and the
    reworded hard-rule must direct a structured-options ask."""
    block = _fenced_block_after(read_file(relpath), marker, src=surface_id)
    assert BARE_ASK not in block, (
        f"{surface_id}: the bare free-text hard-rule ASK ({BARE_ASK!r}) is "
        f"still present — SOAD-1 self-violation (slice-022 law); M-add-1 "
        f"fix (a) reword regressed"
    )
    assert "via structured options" in block, (
        f"{surface_id}: the reworded hard-rule ASK must direct a "
        f"structured-options ask ('via structured options' absent)"
    )


def test_madd1_repo_claude_md_hardrule_reworded() -> None:
    """M-add-1: this repo's CLAUDE.md hard-rule ASK is reworded to the
    structured-options form (the slice satisfies its own rule, RSAD-1)."""
    content = read_file("CLAUDE.md")
    assert BARE_ASK not in content, (
        "root CLAUDE.md still carries the bare free-text hard-rule ASK "
        f"({BARE_ASK!r}) — SOAD-1 self-violation; M-add-1 fix (a) regressed"
    )
    assert "**ASK** the user via structured options" in content, (
        "root CLAUDE.md hard-rule ASK must be reworded to "
        "'**ASK** the user via structured options …' (M-add-1 fix a)"
    )
