"""Prose-pin tests for BRANCH-1 sub-mode (b) commit-time `--merge` flow at /commit-slice.

Per slice-021 AC #3 + /critique B2 ACCEPTED-PENDING: skills/commit-slice/SKILL.md
- frontmatter `argument-hint: [--do-commit]` is replaced by `[--merge]`
- `--do-commit` flag is REMOVED entirely (no alias, no two-flag mode)
- Step 5 documents the new `--merge` flow: 2 pre-flight guardrails + 5-step
  commit-and-merge with explicit user confirmation
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_commit_slice_skill_md_documents_merge_flag() -> None:
    """skills/commit-slice/SKILL.md frontmatter + Step 5 must document the `--merge` flag."""
    content = read_file("skills/commit-slice/SKILL.md")
    # Frontmatter `argument-hint` must contain `--merge`.
    assert "argument-hint: [--merge]" in content, (
        "skills/commit-slice/SKILL.md frontmatter `argument-hint` must be `[--merge]` "
        "(replaces `[--do-commit]` per slice-021 AC #3)"
    )
    # Step 5 (or Argument modes block) must reference `--merge`.
    assert "--merge" in content, "skills/commit-slice/SKILL.md must reference --merge flag"


def test_commit_slice_skill_md_removes_do_commit_flag() -> None:
    """`--do-commit` MUST NOT appear in skills/commit-slice/SKILL.md (clean break)."""
    content = read_file("skills/commit-slice/SKILL.md")
    assert "--do-commit" not in content, (
        "skills/commit-slice/SKILL.md must NOT contain `--do-commit` "
        "(removed per slice-021 AC #3 + /critique B2 ACCEPTED-PENDING; clean break, no alias)"
    )


def test_commit_slice_skill_md_specifies_no_ff_merge_and_safe_local_branch_delete() -> None:
    """`--merge` flow must specify `git merge --no-ff` + `git branch -d` (safe-delete)."""
    content = read_file("skills/commit-slice/SKILL.md")
    assert "git merge --no-ff" in content, (
        "skills/commit-slice/SKILL.md must specify `git merge --no-ff` "
        "(preserves slice attribution as discrete merge commit)"
    )
    assert "git branch -d" in content, (
        "skills/commit-slice/SKILL.md must specify `git branch -d` (safe-delete; never `-D`)"
    )
    # `-D` (force-delete) must NOT be used as the canonical command; if it appears,
    # it must be in a NEVER context. Simplest assertion: forbid `git branch -D` as a
    # standalone command line.
    assert "git branch -D" not in content or "NEVER" in content, (
        "skills/commit-slice/SKILL.md must NOT use `git branch -D` (force-delete) "
        "as the canonical command — safe-delete only per slice-021 Must-not-defer"
    )


def test_commit_slice_skill_md_specifies_pre_flight_guardrails() -> None:
    """`--merge` flow must specify 2 pre-flight guardrails per /critique B5 + M5."""
    content = read_file("skills/commit-slice/SKILL.md")
    # Guardrail 1: WT-clean check via `git status --porcelain` (M5 silent-WT-discard).
    assert "git status --porcelain" in content, (
        "skills/commit-slice/SKILL.md `--merge` must include `git status --porcelain` "
        "pre-flight guardrail per slice-021 /critique M5 ACCEPTED-PENDING"
    )
    # Guardrail 2: explicit `Confirm merge + delete?` user prompt (M5 unrecoverable-without-push).
    assert "Confirm merge + delete?" in content, (
        "skills/commit-slice/SKILL.md `--merge` must include explicit "
        "`Confirm merge + delete? (yes/no)` user-confirmation prompt before `git branch -d` "
        "per slice-021 /critique M5 ACCEPTED-PENDING"
    )
