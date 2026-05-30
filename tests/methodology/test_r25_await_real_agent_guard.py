"""R-25 await-the-real-agent guard pin — slice-086.

Per [[ADR-078]]: the three agent-spawning skills (`critique`,
`critique-review`, `code-review`) MUST carry the canonical
await-the-real-agent guard at the spawn->write seam (between each skill's
"### Step 2" and "### Step 3" headings), so the main thread never
fabricates an async-spawned agent's output before it returns — the R-25
failure mode, observed live in slice-085 (the main thread wrote
`critique.md` from its own self-review before the real Critic returned).

The pin asserts BOTH literals and is SEAM-SCOPED (M-add-1, DR-1
critique-review EXTEND):

  * CANON_HEADING — the guard's identity ("the guard exists").
  * CANON_BODY    — one operative obligation ("the guard still
                    instructs"); guards against a heading-only slogan
                    with a gutted body (M2).

Both are asserted to fall WITHIN each skill's Step 2 -> Step 3 region,
NOT merely present file-globally — a file-global pin would stay green if
the guard were RELOCATED out of the spawn->write seam (into a
footer/template section or above Step 2), leaving the literal present
once but the guard inert at the decision point. Modeled on the SOAD-1
precedent's section-scoping (`test_soad1_structured_options_ask_rule.py`
`_fenced_block_after`), which exists precisely because a repo-global
`.count()` passes even when a hit lands in the wrong section.

Defect class: the guard silently dropped (deletion) OR relocated out of
the spawn->write seam from any of the three skills — R-25 re-opens.

Rule reference: R-25 fix (slice-086; ADR-078). MEPD-1 EXCLUDE — no new
RULE-ID, no methodology-changelog entry, no VERSION bump.
"""
from __future__ import annotations

import re

import pytest

from tests.methodology.conftest import read_file

# Heading anchors — line-start (`(?m)^`) + word-boundary (`\b`) matched, NOT
# bare substring (m1 / code-review): `.find("### Step 2")` would mis-anchor on
# an inline narration mention of the heading text OR collide with a future
# `### Step 20` heading, yielding the wrong region (the exact substring-vs-shape
# false-negative class this slice exists to close — slice-085 / slice-075 /
# M-add-1 lineage). `\b` after the digit rejects `### Step 20`; `(?m)^` rejects
# mid-line narration mentions.
_STEP2_HEADING_RE = re.compile(r"(?m)^### Step 2\b")
_STEP3_HEADING_RE = re.compile(r"(?m)^### Step 3\b")

# The canonical guard heading literal — the dash is U+2014 EM DASH (NOT
# hyphen-minus U+002D, NOT en-dash U+2013). Pinned VERBATIM across all
# three SKILL.md surfaces; this string is the single source of truth.
CANON_HEADING = "**Await the real agent — never fabricate its output.**"

# One operative body literal — unique-to-invocation (verified absent from
# informative narration across all three skills at build time, per the
# slice-075 lesson). Signals "the guard still instructs".
CANON_BODY = "NEVER self-author a placeholder"

# (surface_id, repo_relpath) — the three agent-spawning skills.
_SPAWN_SKILLS = [
    ("critique", "skills/critique/SKILL.md"),
    ("critique-review", "skills/critique-review/SKILL.md"),
    ("code-review", "skills/code-review/SKILL.md"),
]


def _step2_to_step3_region(content: str, *, src: str) -> str:
    """Return the text between the "### Step 2" and "### Step 3" headings.

    Seam-scoped extraction (M-add-1; SOAD-1 `_fenced_block_after`
    precedent shape): a file-global presence check would pass even if the
    guard were relocated out of the spawn->write seam. Scope every assert
    to the Step 2 -> Step 3 region so PLACEMENT is enforced, not just
    presence.

    Headings are matched line-anchored (`(?m)^### Step N\\b`), NOT by bare
    substring (m1 / code-review): `.find("### Step 2")` would mis-anchor on
    an inline narration mention before the real heading, or collide with a
    future `### Step 20` heading — the same substring-vs-shape false-negative
    class this slice exists to close.
    """
    m2 = _STEP2_HEADING_RE.search(content)
    assert m2 is not None, f"{src}: '### Step 2' heading not found"
    m3 = _STEP3_HEADING_RE.search(content, m2.end())
    assert m3 is not None, f"{src}: '### Step 3' heading not found after Step 2"
    return content[m2.start():m3.start()]


@pytest.mark.parametrize("surface_id,relpath", _SPAWN_SKILLS)
def test_await_real_agent_heading_in_spawn_write_seam(
    surface_id: str, relpath: str
) -> None:
    """AC-1/AC-2: the canonical guard heading literal is present in the
    Step 2 -> Step 3 seam of each agent-spawning skill (seam-scoped)."""
    region = _step2_to_step3_region(read_file(relpath), src=surface_id)
    assert CANON_HEADING in region, (
        f"{surface_id} ({relpath}): the canonical await-the-real-agent "
        f"guard heading ({CANON_HEADING!r}) is absent from the Step 2 -> "
        f"Step 3 seam — R-25 guard dropped or relocated out of the "
        f"spawn->write boundary (slice-086 AC-1/AC-2)"
    )


@pytest.mark.parametrize("surface_id,relpath", _SPAWN_SKILLS)
def test_await_real_agent_body_in_spawn_write_seam(
    surface_id: str, relpath: str
) -> None:
    """AC-2 (M2): one operative body literal is present in the seam too —
    a heading-only slogan with a gutted body must NOT pass."""
    region = _step2_to_step3_region(read_file(relpath), src=surface_id)
    assert CANON_BODY in region, (
        f"{surface_id} ({relpath}): the operative guard instruction "
        f"({CANON_BODY!r}) is absent from the Step 2 -> Step 3 seam — the "
        f"guard was reduced to a heading-only slogan (slice-086 AC-2/M2)"
    )


def test_seam_scoping_rejects_relocated_guard() -> None:
    """M-add-1 proof (the AC-2 relocate fixture): a guard RELOCATED out of
    the Step 2 -> Step 3 seam (e.g. into a footer) is NOT seen by the
    region extractor — proving the pin enforces PLACEMENT, not merely
    file-global presence. A file-global `.count()`-style pin would falsely
    pass on this input (both literals ARE present globally)."""
    relocated = (
        "### Step 2: Spawn the agent\n"
        "spawn instructions here\n\n"
        "### Step 3: Receive\n"
        "write the file\n\n"
        "## Footer\n"
        f"{CANON_HEADING}\n{CANON_BODY}\n"  # guard present, but OUTSIDE the seam
    )
    region = _step2_to_step3_region(relocated, src="synthetic-relocated")
    assert CANON_HEADING not in region, (
        "seam-scoping failed: a guard relocated into the footer was still "
        "seen inside the Step 2 -> Step 3 region"
    )
    assert CANON_BODY not in region, (
        "seam-scoping failed: a relocated body literal was still seen "
        "inside the Step 2 -> Step 3 region"
    )
    # Sanity: the literals ARE present file-globally — a file-global pin
    # would falsely pass on this relocated input, which is the bug
    # seam-scoping closes.
    assert CANON_HEADING in relocated and CANON_BODY in relocated


def test_seam_anchoring_is_line_start_not_substring() -> None:
    """m1 fix (code-review): headings are matched line-anchored, so INLINE
    narration mentions of '### Step 2'/'### Step 3' (mid-line) do not
    mis-anchor the region. The pre-fix bare-substring `.find()` anchored on
    the first inline mention and could exclude the real guard — the
    substring-vs-shape false-negative class this slice exists to close.

    Discriminating input: the intro line mentions BOTH '### Step 2' and
    '### Step 3' mid-line. The pre-fix `.find()` would set start/end to
    those two inline mentions, returning a region that EXCLUDES the real
    guard (false-negative). The line-anchored regex skips the mid-line
    mentions and anchors on the real headings.
    """
    content = (
        "Intro that mentions ### Step 2 and ### Step 3 inline on one line.\n\n"
        "### Step 2: real heading\n"
        f"{CANON_HEADING}\n{CANON_BODY}\n\n"
        "### Step 3: real heading\n"
        "write the file\n"
    )
    region = _step2_to_step3_region(content, src="synthetic-anchor")
    assert region.startswith("### Step 2: real heading"), (
        "region must anchor on the line-start heading, not the inline "
        "narration mention (m1: substring `.find` would mis-anchor here)"
    )
    assert CANON_HEADING in region and CANON_BODY in region


def test_step2_regex_rejects_step20_prefix_collision() -> None:
    """m1 fix: the `\\b` after the digit rejects a `### Step 20` heading —
    `### Step 2` must not prefix-match `### Step 20`."""
    assert _STEP2_HEADING_RE.search("### Step 20: far-future heading\n") is None
    assert _STEP2_HEADING_RE.search("### Step 2: real\n") is not None
