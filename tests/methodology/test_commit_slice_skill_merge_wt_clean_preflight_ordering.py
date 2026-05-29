"""Prose-pin tests for WT-clean preflight repositioning at /commit-slice --merge Step 5b.

Per slice-075 (closes P2.4 from `architecture/slices/slice-075-.../source-pending-items.txt`;
[[ADR-063]] BRANCH-2 + [[ADR-068]] PSQ-3 + [[ADR-020]] commit-slice 3-mode parents;
in-band methodology-prose-fix per MEPD-1 EXCLUDE — ships at methodology v0.72.0 unchanged):
`skills/commit-slice/SKILL.md` Step 5b pre-flight WT-clean check (currently at L168)
is lifted out of "Pre-flight guardrails (run BEFORE any state change)" and repositioned
as a NEW sub-step `2.1.` (post-commit WT-clean guardrail) between sub-step 2 (commit
on slice branch) and sub-step 2.5 (PSQ-3 rebase). This closes the WT-clean-vs-sub-step-2
commit-ordering contradiction: pre-fix, the preflight required empty `git status
--porcelain` BEFORE sub-step 2's `git add` + `git commit` could execute (logical
contradiction — /build-slice produces uncommitted slice work for sub-step 2 to commit).

The decimal `2.1.` marker mirrors the slice-073 PSQ-3 sub-step `2.5.` precedent for
inserting intermediate sub-steps between integer-numbered steps (CommonMark ordered-list
compliant — per /critique m2 ACCEPTED-FIXED, rejecting earlier "2-bis" draft which
Markdown renders as bold prose, not list item).

The original /critique M5 ACCEPTED-PENDING silent-WT-discard local-state-loss protection
intent MUST be preserved at the new sub-step 2.1. position (per Must-not-defer item
"silent-WT-discard protection intent preserved").

Test assertions are ALL Step-5b-section-scoped via `_step_5b_section()` AND further
sub-step-scoped via the unique post-fix `2.1.` anchor (per /critique-review M-add-1
+ M-add-2 ACCEPTED-FIXED). Section-scoping is MANDATORY (per /critique M2 ACCEPTED-FIXED)
because the literal `Pre-flight guardrails (run BEFORE any state change):` header
appears 3x in skills/commit-slice/SKILL.md (Step 5b L166 + Step 5c L207 + Step 5d L242),
and Steps 5c + 5d legitimately retain WT-clean pre-flight `git status --porcelain`
checks (--push and --sync-after-pr have no commit step). The `2.1.` sub-step-scoping
is mandatory because pre-fix Step 5b ALREADY contains `silent-WT-discard` + `STOP` +
`Print:` literals at L168 (the original pre-flight) AND `git status --porcelain` at
L181 (the PSQ-3 conflict-STOP block); without `2.1.` anchoring the assertions would
PASS pre-fix, violating TF-1 WRITTEN-FAILING.
"""
from __future__ import annotations

import re

from tests.methodology.conftest import read_file


def _step_5b_section(content: str) -> str:
    """Extract the `#### Step 5b: With \\`--merge\\` ...` section.

    Section boundary: opening `#### Step 5b:` heading through (but not
    including) the next `#### Step 5c:` heading. The new sub-step 2.1.
    lives in this section; the WT-clean repositioning invariants are scoped
    here so the legitimate WT-clean pre-flight checks at Step 5c (--push
    L207-209) + Step 5d (--sync-after-pr L242-244) — which have no commit
    step in their flows — cannot satisfy/violate the assertions by accident.

    Mirrors the helper in `test_commit_slice_skill_rebase_flag.py` (slice-073
    PSQ-3 sub-step 2.5 precedent). Per design.md §What's reused: a cross-module
    shared helper in conftest.py would be a follow-on consolidation slice
    (N=4 cumulative recurrence trigger; current N=2 with rebase_flag +
    N=2 new slice-075 modules = N=4 total at slice-076+ candidate).
    """
    start_marker = "#### Step 5b:"
    end_marker = "#### Step 5c:"
    start = content.find(start_marker)
    assert start != -1, (
        "skills/commit-slice/SKILL.md missing `#### Step 5b:` heading "
        "(BRANCH-1 sub-mode (b) `--merge` section); slice-075 WT-clean "
        "preflight repositioning to sub-step 2.1. must occur in this section"
    )
    end = content.find(end_marker, start)
    if end == -1:
        end = len(content)
    return content[start:end]


def _extract_substep_2_1_block(section: str) -> str:
    """Extract the contiguous block from `2.1.` sub-step marker through `2.5.`.

    Per /critique-review M-add-1 + M-add-2 ACCEPTED-FIXED: anchor on the unique
    post-fix `2.1.` literal (pre-fix Step 5b has no `2.1.` sub-step) for clean
    TF-1 WRITTEN-FAILING semantics. The prelude guard raises AssertionError
    pre-fix (no `2.1.` anchor exists → `section.find("2.1.")` returns -1);
    post-fix the block-extraction returns the new sub-step 2.1. body.

    Returns the substring `section[two_one_pos:two_five_pos]`. Asserts both
    markers are present with clear diagnostics for the WRITTEN-FAILING state.
    """
    # Fix G (slice-075 m1): anchor on the LINE-START list markers `^2.1. ` / `^2.5. `
    # (re.MULTILINE), NOT bare `section.find("2.1.")`. The substring form matched the
    # narration forward-reference "...sub-step 2.1. post-commit guardrail below..." in
    # the preflight prose, widening the extracted block to include a SECOND
    # `silent-WT-discard` mention (narration leakage). The line-start anchor pins the
    # actual ordered-list item.
    two_one_match = re.search(r"^2\.1\.\s", section, re.MULTILINE)
    assert two_one_match is not None, (
        "Step 5b section must contain a line-start `2.1. ` sub-step marker "
        "(post-fix prose required per /critique-review M-add-1 + M-add-2 "
        "ACCEPTED-FIXED; pre-fix Step 5b has no `2.1.` sub-step — this is "
        "the canonical TF-1 WRITTEN-FAILING state for slice-075 pre-prose-change)"
    )
    two_one_pos = two_one_match.start()
    two_five_match = re.search(r"^2\.5\.\s", section[two_one_pos:], re.MULTILINE)
    assert two_five_match is not None, (
        "Step 5b section must contain a line-start `2.5. ` sub-step marker AFTER `2.1.` "
        "(PSQ-3 sub-step 2.5 per slice-073 precedent; expected to remain "
        "unchanged by slice-075 — if missing, sub-step 5 ordering may have "
        "regressed which violates ADR-063 §Decision)"
    )
    two_five_pos = two_one_pos + two_five_match.start()
    block = section[two_one_pos:two_five_pos]
    # Fix G narration-leakage guard: line-start extraction yields the sub-step 2.1. body
    # ONLY — exactly one `silent-WT-discard` mention. A count of 2 means the boundary
    # leaked the preflight narration paragraph (the pre-fix substring-extraction failure).
    assert block.count("silent-WT-discard") == 1, (
        f"narration leakage detected: expected exactly 1 `silent-WT-discard` in the "
        f"sub-step 2.1. block, found {block.count('silent-WT-discard')} "
        f"(line-start `^2\\.1\\.` anchor must exclude the preflight narration forward-reference)"
    )
    return block


def test_wt_clean_preflight_does_not_contradict_substep_2_commit() -> None:
    """AC#2: WT-clean check is no longer pre-flight (lifted to post-commit sub-step 2.1.).

    Per slice-075 mission-brief AC#2 + design.md §Components touched §test functions:
    three sub-assertions, all Step-5b-section-scoped via `_step_5b_section()`:

    (a) Pre-flight-guardrails sub-block (from literal `Pre-flight guardrails (run BEFORE
        any state change):` header through the blank line preceding `Then the 5-step merge
        flow:`) MUST NOT contain `git status --porcelain` — i.e., WT-clean check is no
        longer pre-flight (resolves the contradiction with sub-step 2's commit semantics).

    (b) The `2.1.` sub-step marker MUST appear in Step 5b section (anchor unique to
        post-fix prose; per /critique-review M-add-2 ACCEPTED-FIXED — the prior
        offset-comparison `section.find('git status --porcelain', section.find('git commit'))`
        was too weak because the PSQ-3 conflict-STOP block at L181 already contains
        `git status --porcelain` AFTER sub-step 2's L173 `git commit`, satisfying the
        offset check pre-fix; the `2.1.` anchor guarantees WRITTEN-FAILING).

    (c) Within the contiguous block extracted from `2.1.` through `2.5.`, the literal
        `git status --porcelain` MUST appear — i.e., the lifted WT-clean check lives
        inside the new sub-step 2.1. block, not at any pre-existing site.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))

    # Sub-assertion (a): Pre-flight guardrails block MUST NOT contain WT-clean check
    preflight_header = "Pre-flight guardrails (run BEFORE any state change):"
    preflight_start = section.find(preflight_header)
    assert preflight_start != -1, (
        f"Step 5b section must contain `{preflight_header}` header "
        "(existing BRANCH-1 contract — pre-existing, should still be present "
        "with the Stale-slice-branch check as the sole remaining preflight)"
    )
    # End of preflight block: the blank line preceding `Then the 5-step merge flow:`
    flow_marker = "Then the 5-step merge flow:"
    flow_idx = section.find(flow_marker, preflight_start)
    assert flow_idx != -1, (
        f"Step 5b section must contain `{flow_marker}` marker after preflight block "
        "(existing structural anchor — pre-existing)"
    )
    preflight_block = section[preflight_start:flow_idx]
    assert "git status --porcelain" not in preflight_block, (
        "Step 5b Pre-flight guardrails block MUST NOT contain `git status --porcelain` "
        "(slice-075 AC#2 sub-assertion (a); closes P2.4 WT-clean-vs-sub-step-2-commit "
        "ordering contradiction — the WT-clean check was lifted to new sub-step 2.1. "
        "post-commit guardrail per design.md §Contracts NEW pre-flight ordering)"
    )

    # Sub-assertion (b) + (c): `2.1.` anchor + WT-clean lives inside 2.1. block
    # The _extract_substep_2_1_block helper raises AssertionError if `2.1.` is absent
    # (pre-fix state) — clean TF-1 WRITTEN-FAILING diagnostic.
    two_one_block = _extract_substep_2_1_block(section)
    assert "git status --porcelain" in two_one_block, (
        "Step 5b sub-step 2.1. block MUST contain `git status --porcelain` "
        "(slice-075 AC#2 sub-assertion (c); the lifted WT-clean check lives inside "
        "the new sub-step 2.1. post-commit guardrail block per design.md §What's new — "
        "extracted via `section.find('2.1.')` through `section.find('2.5.', ...)` "
        "bounded slice)"
    )


def test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent() -> None:
    """AC#4 (paired pin for AC#2): silent-WT-discard local-state-loss protection intent preserved.

    Per slice-075 mission-brief AC#4 + design.md §Components touched §test functions:
    section-scoped via `_step_5b_section()` AND further sub-step-scoped via the `2.1.`
    anchor (same extraction shape as `test_wt_clean_preflight_does_not_contradict_substep_2_commit`
    sub-assertion (c)). Asserts the 2.1. sub-step block contains:

    1. The intent-preservation phrase `silent-WT-discard` (or equivalent `local-state-loss`)
       — preserves the original /critique M5 ACCEPTED-PENDING silent-WT-discard local-
       state-loss protection intent at the new post-commit position.
    2. The STOP semantic (literal `STOP`) — preserves the M5 stop-on-non-empty behavior.
    3. The diagnostic-print pattern (literal `Print:` or `Print "`) — preserves the
       diagnostic-message contract.

    Per /critique-review M-add-1 ACCEPTED-FIXED: the prior whole-Step-5b-section
    assertion was too weak because the pre-fix L168 WT-clean preflight block ALREADY
    contains all three literals (`silent-WT-discard local-state-loss` + `STOP` +
    `Print:`) — the assertion would PASS pre-fix, violating TF-1 WRITTEN-FAILING.
    The `2.1.` sub-step-scoping (via `_extract_substep_2_1_block`) makes the assertion
    FAIL pre-fix (no `2.1.` anchor exists → prelude guard raises) and PASS post-fix
    (the lifted prose lives inside the new 2.1. block with all three intent literals
    preserved per M5 ACCEPTED-PENDING shape).
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    # _extract_substep_2_1_block raises AssertionError if `2.1.` is absent (pre-fix state)
    two_one_block = _extract_substep_2_1_block(section)

    # Intent-preservation phrase: accept either `silent-WT-discard` OR `local-state-loss`
    # per design.md §Components touched §test functions item 2 spec ("or equivalent
    # intent-preserving phrase like 'local-state-loss'").
    intent_phrases = ("silent-WT-discard", "local-state-loss")
    has_intent = any(phrase in two_one_block for phrase in intent_phrases)
    assert has_intent, (
        f"Step 5b sub-step 2.1. block MUST contain intent-preservation phrase — "
        f"one of {intent_phrases} (slice-075 AC#4; preserves original /critique M5 "
        f"ACCEPTED-PENDING silent-WT-discard local-state-loss protection intent at "
        f"new post-commit position; per Must-not-defer item 'silent-WT-discard "
        f"protection intent preserved')"
    )

    # STOP semantic
    assert "STOP" in two_one_block, (
        "Step 5b sub-step 2.1. block MUST contain literal `STOP` "
        "(slice-075 AC#4; preserves M5 ACCEPTED-PENDING stop-on-non-empty behavior)"
    )

    # Diagnostic-print pattern: accept either `Print:` or `Print "`
    has_print = "Print:" in two_one_block or 'Print "' in two_one_block
    assert has_print, (
        "Step 5b sub-step 2.1. block MUST contain literal `Print:` or `Print \"` "
        "(slice-075 AC#4; preserves M5 ACCEPTED-PENDING diagnostic-message contract)"
    )
