"""Prose-pin tests for PSQ-3 rebase-onto-default discipline at /commit-slice --merge.

Per slice-073 + ADR-068 (mints PSQ-3): `skills/commit-slice/SKILL.md` Step 5b
gains a NEW sub-step 2.5 between existing sub-step 2 (commit on slice branch)
and sub-step 3 (default-branch resolution + checkout + no-ff merge). The
sub-step 2.5 invokes `git rebase <default>` on the slice branch BEFORE the
no-ff merge; on conflict it STOPS with `git status --porcelain` U-prefixed
entries + `git rebase --abort` recovery hint + SOAD-1 3-option ask.

The 5 prose-pin assertions enforced here mirror the existing
`test_commit_slice_skill_merge_flag.py::test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete`
precedent — prose-pinning a git-command invocation rather than minting a
separate audit-tool module (per ADR-068 §Options-#3 — the `git rebase`
invocation IS the runtime gate).
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def _step_5b_section(content: str) -> str:
    """Extract the `#### Step 5b: With \\`--merge\\` ...` section.

    Section boundary: opening `#### Step 5b:` heading through (but not
    including) the next `#### Step 5c:` heading. Sub-step 2.5 lives in this
    section; the rebase invariants are scoped here so a stray `git rebase`
    mention in Step 5c/5d/elsewhere cannot satisfy the assertions.
    """
    start_marker = "#### Step 5b:"
    end_marker = "#### Step 5c:"
    start = content.find(start_marker)
    assert start != -1, (
        "skills/commit-slice/SKILL.md missing `#### Step 5b:` heading "
        "(BRANCH-1 sub-mode (b) `--merge` section); PSQ-3 sub-step 2.5 "
        "must be inserted in this section"
    )
    end = content.find(end_marker, start)
    if end == -1:
        end = len(content)
    return content[start:end]


def test_step_5b_contains_git_rebase_invocation() -> None:
    """Step 5b must contain a `git rebase <default>` invocation (PSQ-3 sub-step 2.5).

    AC1 per mission-brief.md + design.md §Contracts: the rebase step is the
    behavior PSQ-3 adds. The invocation literal `git rebase` MUST appear in
    the Step 5b section.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "git rebase" in section, (
        "skills/commit-slice/SKILL.md Step 5b must contain `git rebase` "
        "invocation literal per PSQ-3 (slice-073; ADR-068)"
    )


def test_step_5b_rebase_precedes_no_ff_merge() -> None:
    """Step 5b: `git rebase` must appear BEFORE `git merge --no-ff` (ordering).

    AC1 per design.md §Contracts behavior-contract: sub-step 2.5 (rebase)
    must be inserted BEFORE sub-step 3 (no-ff merge). This is the load-bearing
    ordering invariant — a rebase AFTER the merge would mis-rebase the wrong
    direction.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    rebase_idx = section.find("git rebase")
    merge_idx = section.find("git merge --no-ff")
    assert rebase_idx != -1, "Step 5b missing `git rebase` invocation (AC1 sibling test)"
    assert merge_idx != -1, "Step 5b missing `git merge --no-ff` invocation (existing BRANCH-1 contract)"
    assert rebase_idx < merge_idx, (
        f"Step 5b ordering violation: `git rebase` (offset {rebase_idx}) must "
        f"appear BEFORE `git merge --no-ff` (offset {merge_idx}); rebase-after-merge "
        f"would mis-rebase the wrong direction (PSQ-3 ADR-068 §Contracts)"
    )


def test_step_5b_rebase_target_resolved_via_canonical_2_step() -> None:
    """Step 5b sub-step 2.5: default-branch resolution must use the canonical 2-step pattern.

    AC1 per design.md §Contracts: the rebase target resolves via
    (primary) `git symbolic-ref refs/remotes/origin/HEAD` + (fallback)
    `git config init.defaultBranch` — the same 2-step pattern as existing
    sub-step 3 (NAW-1 ADR-061 §Decision exit-2 contract). Divergent resolution
    would create a footgun where rebase targets a different default than merge.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "git symbolic-ref refs/remotes/origin/HEAD" in section, (
        "Step 5b must contain `git symbolic-ref refs/remotes/origin/HEAD` "
        "primary default-branch resolution literal (PSQ-3 sub-step 2.5 + "
        "existing sub-step 3 use the same 2-step pattern per design.md §Contracts)"
    )
    assert "git config init.defaultBranch" in section, (
        "Step 5b must contain `git config init.defaultBranch` fallback "
        "default-branch resolution literal (NAW-1 ADR-061 §Decision exit-2 contract)"
    )


def test_step_5b_conflict_stops_with_porcelain_u_entries() -> None:
    """Step 5b: rebase conflict-STOP must enumerate `git status --porcelain` U-entries.

    AC2 per design.md §Error model: on rebase conflict, STOP and print
    conflicting file paths derived from `git status --porcelain` filtered to
    U-prefixed entries. The literal `git status --porcelain` AND a reference to
    U-prefixed entries MUST appear in the Step 5b section. Note: this string
    already appears at L168 (existing WT-clean guardrail) — the assertion here
    is co-occurrence with the U-prefixed-entries language, which is unique to
    PSQ-3's conflict-STOP block.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "git status --porcelain" in section, (
        "Step 5b must contain `git status --porcelain` literal "
        "(existing WT-clean guardrail + PSQ-3 conflict-STOP enumeration)"
    )
    # PSQ-3's specific contribution: U-prefixed-entries language in the conflict-STOP block.
    assert "U-prefixed" in section, (
        "Step 5b PSQ-3 conflict-STOP must reference `U-prefixed` entries from "
        "`git status --porcelain` (the canonical git encoding for unmerged paths; "
        "distinguishes PSQ-3 conflict-STOP from the pre-existing WT-clean guardrail "
        "use of `git status --porcelain`)"
    )


def test_step_5b_conflict_surfaces_git_rebase_abort_hint() -> None:
    """Step 5b: rebase conflict-STOP must surface `git rebase --abort` recovery hint.

    AC2 per design.md §Error model: on conflict, the recovery hint
    `git rebase --abort` MUST be printed. This is the canonical git recovery
    path for an in-progress rebase; without it the user is stranded in
    rebase-in-progress state. /commit-slice's Critical rules forbid auto-resolve;
    the user must `--abort` or `--continue` outside the skill.
    """
    section = _step_5b_section(read_file("skills/commit-slice/SKILL.md"))
    assert "git rebase --abort" in section, (
        "Step 5b conflict-STOP must contain `git rebase --abort` recovery hint "
        "literal per design.md §Error model + ADR-068 §Decision option (a). "
        "Without the recovery hint, the user is stranded in rebase-in-progress state."
    )
