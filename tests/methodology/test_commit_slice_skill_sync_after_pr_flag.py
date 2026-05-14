"""Prose-pin tests for slice-022 AC #3: `/commit-slice --sync-after-pr` mode.

Per slice-022 design.md + ADR-020:
- `--sync-after-pr` is the post-PR-merge local-cleanup mode for the PR-based
  workflow (`--push` + external PR + remote merge + remote auto-delete → local
  cleanup via `--sync-after-pr`).
- Skips Steps 1-4 (no commit message generation).
- Pre-flight guardrails: WT-clean + slice-branch + origin-present + upstream-
  tracking.
- Two-signal merged-state detection (per /critique B2 + /critique-review M-add-5
  ACCEPTED-FIXED): Signal A = `git ls-remote` returns non-zero (remote branch
  absent — pruned); Signal B = two-pass cherry-pick + aggregate-tree-diff fallback.
- On YES: `git checkout <default>` + `git pull --ff-only origin <default>` (per
  /critique B1 ACCEPTED-FIXED — explicit `--ff-only`) + `git branch -d` (safe-delete).
- Pass 2 has 3 guards: empty-FILES → STOP, "covers FILES" pinned to superset,
  perf bound N=500 commits.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_skill_md_documents_sync_after_pr_flag() -> None:
    """SKILL.md frontmatter + Step 5 document `--sync-after-pr` as a mode.

    Defect class: --sync-after-pr is documented in body prose but not in
    frontmatter argument-hint; Claude's argument parser sees the old surface.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Frontmatter mutually-exclusive flag set must include `--sync-after-pr`.
    assert (
        "argument-hint: [--merge | --push | --sync-after-pr]" in content
    ), (
        "skills/commit-slice/SKILL.md frontmatter `argument-hint` must be "
        "`[--merge | --push | --sync-after-pr]` per slice-022 AC #1 + ADR-020"
    )
    assert "--sync-after-pr" in content, (
        "skills/commit-slice/SKILL.md must reference `--sync-after-pr` in body"
    )


def test_skill_md_sync_after_pr_uses_two_signal_detection() -> None:
    """SKILL.md `--sync-after-pr` sub-step documents the two-signal merged-state
    detection (Signal A = `git ls-remote` + Signal B = `git cherry` two-pass +
    aggregate-tree-diff fallback per /critique B2 ACCEPTED-FIXED).

    Defect class: future slice swaps the detection mechanism to `git branch
    --merged` (rejected at design-time per /critique B2 because it fails for
    squash-merge of multi-commit branches); silent regression to the wrong
    primitive.

    Per /build-slice TPHD-1 sub-mode (c) 2026-05-15: function renamed from
    `test_skill_md_sync_after_pr_uses_branch_merged_detection` since design
    rejected `git branch --merged` for the squash-merge failure mode.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Signal A: `git ls-remote` for remote-branch absence.
    assert "git ls-remote" in content, (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must reference "
        "`git ls-remote` (Signal A — detects remote-branch absence post-PR-merge "
        "+ remote-auto-delete per design.md Flow Step 3)"
    )
    # Signal B Pass 1: `git cherry` for per-commit cherry-pick equivalence.
    assert "git cherry" in content, (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must reference "
        "`git cherry` (Signal B Pass 1 — per-commit cherry-pick equivalence; "
        "covers merge-commit + rebase-merge + cherry-pick + single-commit-squash)"
    )
    # Signal B Pass 2: aggregate-tree-diff fallback for multi-commit squash-merge.
    assert "aggregate-tree-diff" in content or "tree-diff" in content, (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must reference the "
        "aggregate-tree-diff Pass 2 fallback (covers GitHub squash-merge of "
        "N>1-commit slice branches per /critique B2 ACCEPTED-FIXED — `git cherry` "
        "alone fails for multi-commit squash because patch-id is per-commit)"
    )


def test_skill_md_sync_after_pr_stops_if_not_merged() -> None:
    """SKILL.md `--sync-after-pr` STOPs (does not delete the slice branch) if
    either signal reports NO.

    Defect class: --sync-after-pr proceeds to destructive cleanup even when
    PR was not actually merged; user loses slice branch + uncommitted local
    work.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # STOP semantics on signal failure.
    assert "STOP" in content, (
        "skills/commit-slice/SKILL.md must use STOP semantics for "
        "`--sync-after-pr` signal failure paths (do not proceed to destructive "
        "cleanup on signal=NO)"
    )
    # Specific diagnostic for remote-branch-still-exists path (Signal A = NO).
    assert "Remote slice branch still exists" in content or (
        "Remote slice branch" in content and "still exists" in content
    ), (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must include the "
        "specific 'Remote slice branch still exists' diagnostic for Signal A=NO"
    )
    # Specific diagnostic for commits-not-on-default path (Signal B = NO).
    assert "NOT yet on `origin/<default>`" in content or (
        "NOT yet" in content and "origin" in content
    ), (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must include the "
        "specific 'commits NOT yet on origin/<default>' diagnostic for Signal B=NO"
    )


def test_skill_md_sync_after_pr_uses_branch_d_not_force_delete() -> None:
    """SKILL.md `--sync-after-pr` uses `git branch -d` (safe-delete), NEVER
    `git branch -D` (force-delete).

    Defect class: future slice swaps `-d` for `-D` to avoid the "safe-delete
    refused" path; user silently loses unmerged commits.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Safe-delete reference.
    assert "git branch -d" in content, (
        "skills/commit-slice/SKILL.md `--sync-after-pr` must use `git branch -d` "
        "(safe-delete; refuses if branch has unmerged commits)"
    )
    # `-D` must NOT be the canonical form (only allowed in NEVER context).
    # Heuristic: if `-D` appears, it must be alongside NEVER or "do NOT use".
    lines_with_force_delete = [
        line for line in content.split("\n") if "git branch -D" in line
    ]
    for line in lines_with_force_delete:
        # Allowed contexts for `git branch -D` references:
        # (a) NEVER / do-NOT / Do-NOT — explicit prohibition (forbidden as
        #     canonical command).
        # (b) Manually / manually — manual-escape-hatch diagnostic context where
        #     the skill STOPped, told the user to verify externally, and is
        #     informing them that user-driven force-delete IS available as a
        #     last-resort manual action (e.g., Pass 2 guards trip → STOP with
        #     "Manually verify... then use `git branch -D` if confirmed").
        # Both contexts are non-canonical (the skill itself never executes -D).
        allowed_context = (
            "NEVER" in line
            or "do NOT" in line
            or "Do NOT" in line
            or "Manually" in line
            or "manually" in line
        )
        assert allowed_context, (
            f"skills/commit-slice/SKILL.md line containing `git branch -D` "
            f"must be in a NEVER/do-NOT context (canonical prohibition) OR a "
            f"Manually/manually context (manual-escape-hatch diagnostic after "
            f"a STOP) — force-delete is never the skill's canonical command "
            f"per slice-021 must-not-defer + slice-022 `--sync-after-pr` "
            f"safe-delete preservation: {line!r}"
        )


def test_skill_md_sync_after_pr_uses_ff_only_pull() -> None:
    """SKILL.md `--sync-after-pr` uses `git pull --ff-only` explicitly.

    Per /critique B1 ACCEPTED-FIXED: `git pull`'s default is MERGE not
    fast-forward-only (Git 2.34+ warns when ff fails but still merges).
    `--sync-after-pr` MUST use `--ff-only` explicitly to STOP on non-ff
    rather than silently create a merge commit on the local default branch.

    Defect class: future slice strips the `--ff-only` flag (e.g., "simplify
    to plain `git pull`"); silent merge-commit creation on default
    re-introduced.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    assert "git pull --ff-only" in content, (
        "skills/commit-slice/SKILL.md `--sync-after-pr` MUST use `git pull "
        "--ff-only` explicitly — `git pull`'s default is MERGE not ff-only "
        "(per /critique B1 ACCEPTED-FIXED; closes silent-merge-commit-on-default "
        "data-loss path)"
    )
