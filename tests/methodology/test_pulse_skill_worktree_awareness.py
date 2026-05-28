"""Prose-pin tests on skills/pulse/SKILL.md Step 1 / Step 2 / Step 3
worktree-awareness augmentations per slice-077 / ADR-070.

Per slice-077 design.md § Prose-pin test discipline (M9 ACCEPTED-FIXED — RSAD-1
N=3 cumulative pre-empt): each pinned literal MUST use the specified anchoring
strategy (line-start / wrapping-context / scope-to-new-paragraph), NOT bare
substring-presence (which would either pollute against existing prose or fail
to distinguish new content from informative narration).

Specifically: `cadence-overdue` already exists in skills/pulse/SKILL.md L88
(existing CAL-1 override mention). Naïve substring-presence test would PASS
pre-edit, violating TF-1 WRITTEN-FAILING semantics. The Step 2 prose-pin test
scopes its anchor by first locating the new override-precedence paragraph
THEN asserting cadence-overdue appears within it.
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


_SKILL_MD = REPO_ROOT / "skills" / "pulse" / "SKILL.md"


def _read_skill() -> str:
    return _SKILL_MD.read_text(encoding="utf-8")


def test_step_1_documents_git_worktree_list_pre_read():
    """Step 1 prose MUST contain the literal `git worktree list --porcelain`
    in an invocation-form context (not bare prose mention) AND it must
    precede the existing "Active slice folder (if any): milestone.md" read
    instruction so the worktree milestone is consulted first per AC#1.

    Per design.md § Prose-pin discipline anchoring strategy: invocation-form
    + line-start (the actual CLI invocation, not a discussion reference).
    """
    text = _read_skill()
    wt_idx = text.find("git worktree list --porcelain")
    main_milestone_idx = text.find("milestone.md FIRST")
    assert wt_idx != -1, (
        "Step 1 must mention `git worktree list --porcelain` as the worktree-detection pre-read step"
    )
    assert main_milestone_idx != -1, (
        "existing 'milestone.md FIRST' anchor missing — Step 1 read instruction may have drifted"
    )
    assert wt_idx < main_milestone_idx, (
        "worktree-detection bullet must PRECEDE the existing main-tree milestone.md read instruction "
        f"(found git worktree list at offset {wt_idx}; milestone.md FIRST at offset {main_milestone_idx})"
    )


def test_worktree_milestone_read_precedes_main_tree_milestone_read():
    """Step 1 prose MUST document that the worktree's milestone.md is read
    (active OR archive) when a slice/NNN worktree exists. Both `archive` AND
    `active` slice folder path patterns must appear in the new Step 1 prose,
    so the test asserts BOTH literals + that they come BEFORE the existing
    main-tree milestone.md read."""
    text = _read_skill()
    main_milestone_idx = text.find("milestone.md FIRST")
    archive_idx = text.find("slices/archive/slice-NNN")
    assert main_milestone_idx != -1
    assert archive_idx != -1, (
        "Step 1 must document the archive path `slices/archive/slice-NNN-<name>/milestone.md` "
        "for the auto-archived-in-worktree case"
    )
    assert archive_idx < main_milestone_idx, (
        "worktree milestone read clause (mentioning slices/archive/) must precede the main-tree "
        f"milestone.md read instruction (archive at {archive_idx}; main-tree at {main_milestone_idx})"
    )


def test_built_but_not_merged_overrides_recommended_next_action_with_commit_slice_merge():
    """Step 2 prose MUST contain a precedence-ordering block that elevates
    BUILT_BUT_NOT_MERGED above CAL-1 cadence-overdue + stage-derived. The
    block must cite the canonical override command `/commit-slice --merge`
    and the worktree path placeholder.

    Per design.md § Prose-pin discipline: literal `BUILT_BUT_NOT_MERGED`
    pinned by wrapping-context (backtick-wrapped); literal `/commit-slice
    --merge` pinned by code-fence/wrapping context.
    """
    text = _read_skill()
    # State-name in backticks (or surrounded by non-ALL-CAPS) — wrapping-context anchoring
    state_pattern = re.compile(r"`BUILT_BUT_NOT_MERGED`")
    assert state_pattern.search(text), (
        "Step 2 must reference `BUILT_BUT_NOT_MERGED` (backtick-wrapped) in the override-precedence block"
    )
    # Override command literal — post-fix-unique by construction
    assert "/commit-slice --merge" in text, (
        "Step 2 must cite `/commit-slice --merge` as the BUILT_BUT_NOT_MERGED-state next-action"
    )
    # Both must appear together (within 500 chars of each other) — same paragraph anchor
    state_idx = state_pattern.search(text).start()
    cmd_idx = text.find("/commit-slice --merge")
    assert abs(state_idx - cmd_idx) < 1500, (
        f"`BUILT_BUT_NOT_MERGED` (offset {state_idx}) and `/commit-slice --merge` (offset {cmd_idx}) "
        f"must appear within the same prose block; they are {abs(state_idx - cmd_idx)} chars apart"
    )


def test_worktree_override_takes_precedence_over_calibration_cadence_override():
    """Step 2 prose MUST document that BUILT_BUT_NOT_MERGED supersedes CAL-1
    cadence-overdue per ADR-070 § Override-precedence ordering. The literal
    `cadence-overdue` already exists at L88 (existing CAL-1 mention); this
    test scopes its anchor to a NEW Step 2 paragraph that explicitly mentions
    precedence ordering.

    Per design.md § Prose-pin discipline: `cadence-overdue` pinned via
    scope-to-new-paragraph (substring-after-anchor), NOT bare substring.
    """
    text = _read_skill()
    # Anchor the search by the new precedence-discussion paragraph (post-fix-unique)
    precedence_anchor = text.find("worktree-state override")
    assert precedence_anchor != -1, (
        "Step 2 must contain a paragraph anchored by literal `worktree-state override` "
        "introducing the new precedence ordering"
    )
    # Within the next ~3000 chars after the anchor, cadence-overdue must appear
    # (alongside the override-ordering discussion)
    window = text[precedence_anchor:precedence_anchor + 3000]
    assert "cadence-overdue" in window, (
        "the new override-precedence paragraph must reference `cadence-overdue` "
        "(the rule #2 that BUILT_BUT_NOT_MERGED supersedes); existing L88 mention is NOT the target"
    )


def test_step_2_state_dict_includes_worktrees_field_with_worktreeinfo_list():
    """Step 2 prose MUST document the augmented structured-state dict shape
    passed to Step 3 Haiku dispatch — specifically the `worktrees` key and
    `WorktreeInfo` field type. This pins the contract between the Step 2
    deterministic resolver and the Step 3 Haiku-rendered output per design.md.

    Per AC#3 + m6 ACCEPTED-FIXED.
    """
    text = _read_skill()
    assert "worktrees" in text, "Step 2 prose must document the `worktrees` key in the augmented state-dict"
    # Either `WorktreeInfo` or `WorktreeState` should appear in the type description
    has_worktreeinfo = "WorktreeInfo" in text
    has_worktreestate = "WorktreeState" in text
    assert has_worktreeinfo or has_worktreestate, (
        "Step 2 prose must reference the WorktreeInfo / WorktreeState types in the state-dict shape"
    )
