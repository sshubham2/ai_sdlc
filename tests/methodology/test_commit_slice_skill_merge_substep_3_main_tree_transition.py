"""Prose-pin tests for sub-step 3 main-tree-transition at /commit-slice --merge.

Per slice-075 (closes P1.2 from `architecture/slices/slice-075-.../source-pending-items.txt`;
[[ADR-063]] BRANCH-2 + [[ADR-068]] PSQ-3 + [[ADR-020]] commit-slice 3-mode parents;
in-band methodology-prose-fix per MEPD-1 EXCLUDE — ships at methodology v0.72.0 unchanged):
`skills/commit-slice/SKILL.md` Step 5b sub-step 3 gains an explicit main-tree-transition
prepend BEFORE the existing `git checkout $default` invocation, closing the BRANCH-2
worktree-vs-main-tree `git checkout` collision (`fatal: '<default>' is already checked
out at '<main-tree-path>'`).

The main-tree-transition uses the canonical worktree-aware extraction
`main_tree=$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')`
which extracts the first-listed worktree = main tree per the git porcelain ordering
invariant documented at [git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree).
This is a SIBLING-BUT-DISTINCT idiom from Step 5b sub-step 5's
`awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'`
which extracts a SPECIFIC-branch worktree path (per /critique m1 ACCEPTED-FIXED — shared
`/^worktree /` regex anchor with divergent AWK action because divergent semantics).

Test assertions are ALL Step-5b-section-scoped via the local `_step_5b_section()` helper
modeled after `tests/methodology/test_commit_slice_skill_rebase_flag.py::_step_5b_section()`.
Section-scoping is MANDATORY (per /critique M2 ACCEPTED-FIXED) because the literal
`Pre-flight guardrails (run BEFORE any state change):` header appears 3x in
skills/commit-slice/SKILL.md (Step 5b L166 + Step 5c L207 + Step 5d L242), and Steps 5c
+ 5d legitimately retain WT-clean `git status --porcelain` pre-flight checks (--push and
--sync-after-pr have no commit step), so any whole-file assertion would false-FAIL.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def _step_5b_section(content: str) -> str:
    """Extract the `#### Step 5b: With \\`--merge\\` ...` section.

    Section boundary: opening `#### Step 5b:` heading through (but not
    including) the next `#### Step 5c:` heading. Sub-step 3 lives in this
    section; the main-tree-transition invariants are scoped here so a stray
    `cd` / `git worktree list` / `git checkout` mention in Step 5c/5d
    cannot satisfy the assertions.

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
        "(BRANCH-1 sub-mode (b) `--merge` section); slice-075 main-tree-transition "
        "prepend must be inserted at sub-step 3 in this section"
    )
    end = content.find(end_marker, start)
    if end == -1:
        end = len(content)
    return content[start:end]


def test_substep_3_includes_main_tree_transition_before_checkout() -> None:
    """AC#1: Step 5b sub-step 3 must include `cd "$main_tree"` BEFORE `git checkout`.

    Per slice-075 mission-brief AC#1 + design.md §What's new + §Contracts: the
    main-tree-transition prepend (option (a) `cd "$main_tree"` per design.md
    §Decisions Question A — chosen over option (b) `git -C "$main_tree"` heavier
    rewrite and option (c) worktree-tear-down-first reshuffle) MUST appear in
    Step 5b section, AND the literal `cd "$main_tree"` MUST appear BEFORE the
    literal `git checkout` (offset comparison) so a Builder following the
    prose literally transitions to the main tree BEFORE attempting the
    BRANCH-2-incompatible `git checkout $default`.

    Pre-fix: Step 5b L189 has only `git checkout $default + git merge --no-ff`
    with no main-tree transition prepended; under BRANCH-2 the worktree holds
    `slice/NNN-<name>` while the main tree holds `<default>`, so
    `git checkout $default` fails with `fatal: '<default>' is already checked
    out at '<main-tree-path>'`. Slice-074's `--merge` worked ONLY because
    Claude pragmatically deviated from the literal prose (cd'd to main tree
    ad-hoc); this slice codifies the workaround into prose.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    cd_idx = section.find('cd "$main_tree"')
    # Pin the canonical invocation literal `git checkout $default` (NOT the bare
    # noun-phrase `git checkout`) — the noun-phrase appears in informative narration
    # ("worktree-vs-main-tree `git checkout` collision" + failure-message references)
    # BEFORE the actual invocation. Pinning the invocation form makes the ordering
    # assertion robust against narration. (Build-time RSAD-1 tightening, same logic
    # as /critique-review M-add-1/M-add-2 — narration containing the pinned literal
    # would pollute the offset check; the invocation form is unique to the actual command.)
    checkout_invocation_idx = section.find("git checkout $default")
    assert cd_idx != -1, (
        'skills/commit-slice/SKILL.md Step 5b must contain `cd "$main_tree"` '
        "main-tree-transition prepend at sub-step 3 (slice-075 AC#1; closes "
        "P1.2 BRANCH-2 worktree-vs-main-tree `git checkout $default` collision)"
    )
    assert checkout_invocation_idx != -1, (
        "skills/commit-slice/SKILL.md Step 5b missing `git checkout $default` "
        "invocation (existing BRANCH-1 sub-step 3 contract — pre-existing, should "
        "still be present after slice-075's main-tree-transition prepend)"
    )
    assert cd_idx < checkout_invocation_idx, (
        f"Step 5b ordering violation: `cd \"$main_tree\"` (offset {cd_idx}) must "
        f"appear BEFORE `git checkout $default` (offset {checkout_invocation_idx}); "
        f"checkout-invocation-before-cd would fire the BRANCH-2 collision the slice "
        f"exists to close (slice-075 AC#1 + P1.2 source-pending-items.txt)"
    )


def test_substep_3_main_tree_transition_uses_canonical_worktree_list_awk_extraction() -> None:
    """AC#3 (paired pin for AC#1): main_tree resolution uses canonical awk extraction shape.

    Per slice-075 mission-brief AC#3 + design.md §Decisions Question A (a):
    the `$main_tree` resolution MUST use the canonical extraction
    `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'`
    which extracts the first-listed worktree = main tree per the git porcelain
    ordering invariant (per git-scm.com/docs/git-worktree).

    This is a SIBLING-BUT-DISTINCT idiom from Step 5b sub-step 5's existing
    extraction `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2}
    $0=="branch "b {print p; exit}'` which extracts a SPECIFIC-branch worktree
    path. Both grounded in the same git porcelain output format; shared
    `/^worktree /` regex anchor with divergent AWK action because divergent
    semantics (sub-step 3 wants the main tree; sub-step 5 wants a specific
    branch's worktree path). Per /critique m1 ACCEPTED-FIXED, the framing
    "matches Step 5b sub-step 5 existing convention" was misleading (false
    substring-check); the canonical form is the AWK shape this test pins.

    Two literals MUST appear in Step 5b section:
    1. `git worktree list --porcelain` — the porcelain output that's piped
    2. `awk '/^worktree / {print $2; exit}'` — the canonical AWK action for
       first-worktree extraction

    Pre-fix: neither literal exists in Step 5b sub-step 3 (sub-step 5 has only
    its own SPECIFIC-branch awk shape).
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "git worktree list --porcelain" in section, (
        "skills/commit-slice/SKILL.md Step 5b must contain literal "
        "`git worktree list --porcelain` as the porcelain-output source for "
        "main_tree resolution (slice-075 AC#3; the porcelain literal IS the "
        "stable on-disk contract per git-worktree docs)"
    )
    # The canonical AWK action for first-worktree extraction. SIBLING-BUT-DISTINCT
    # from sub-step 5's `awk -v b="..." '/^worktree / {p=$2} $0=="branch "b {print p; exit}'`
    # — shared regex anchor `/^worktree /`, divergent action.
    canonical_awk = "awk '/^worktree / {print $2; exit}'"
    assert canonical_awk in section, (
        f"skills/commit-slice/SKILL.md Step 5b must contain canonical first-worktree "
        f"AWK extraction literal `{canonical_awk}` for main_tree resolution "
        f"(slice-075 AC#3; sibling-but-distinct from sub-step 5's specific-branch "
        f"awk shape per /critique m1 ACCEPTED-FIXED clarification)"
    )
