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
    """skills/commit-slice/SKILL.md frontmatter + Step 5 must document the `--merge` flag.

    Per slice-022 AC #1 + ADR-020: the frontmatter `argument-hint` shape evolved
    from slice-021's `[--merge]` to the 3-mode mutually-exclusive
    `[--merge | --push | --sync-after-pr]`. The contract preserved here is
    "frontmatter argument-hint contains --merge"; the exact shape lives in the
    push_flag / sync_after_pr / merge_flag mutual-exclusion tests.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Frontmatter `argument-hint` must contain `--merge` (slice-022 broadens
    # the slice-021 single-flag pin to the 3-mode mutually-exclusive set).
    assert "argument-hint:" in content and "--merge" in content, (
        "skills/commit-slice/SKILL.md frontmatter `argument-hint` must contain "
        "`--merge` (slice-022 shape: `[--merge | --push | --sync-after-pr]` "
        "per ADR-020 + /critique B4 ACCEPTED-FIXED)"
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


# --- Slice-022 / 3-mode taxonomy (--merge preserved + --push + --sync-after-pr) ---
# Per slice-022 AC #1 + /critique B4 ACCEPTED-FIXED + /critique-review M-add-1
# ACCEPTED-FIXED. AC #1 expanded to "argument contract": (a) no-flag default
# preserved; (b) --merge unchanged; (c) 3 modes mutually exclusive; (d) "When to
# use which mode" guidance section added.


def test_commit_slice_skill_md_documents_when_to_use_which_mode_section() -> None:
    """SKILL.md has a "When to use which mode" guidance section between Argument
    modes and Prerequisite check, naming each mode's use case.

    Defect class: 3-mode taxonomy is introduced but users have no compass for
    picking the right mode; --merge users may keep using --merge on a protected-
    branch repo (the exact failure mode slice-022 exists to prevent per slice-021
    DEVIATION-5).
    """
    content = read_file("skills/commit-slice/SKILL.md")
    assert "## When to use which mode" in content, (
        "skills/commit-slice/SKILL.md must contain a `## When to use which mode` "
        "guidance section (per slice-022 AC #1 + /critique B4 ACCEPTED-FIXED)"
    )
    # Section must name use case for each mode.
    assert "solo-dev" in content or "solo dev" in content, (
        "`When to use which mode` section must name `--merge` as the solo-dev / "
        "no-protected-branch path"
    )
    assert "PR-based" in content or "PR workflow" in content, (
        "`When to use which mode` section must name `--push` as the PR-based-"
        "workflow path"
    )
    assert "post-PR-merge" in content or "post-PR merge" in content, (
        "`When to use which mode` section must name `--sync-after-pr` as the "
        "post-PR-merge local-cleanup path"
    )


def test_commit_slice_skill_md_merge_flow_5_steps_unchanged() -> None:
    """SKILL.md `--merge` 5-step flow + 2 pre-flight guardrails preserved
    verbatim from slice-021 (per slice-022 AC #1 + ADR-020 — `--merge` flow's
    behavior is unchanged; what's superseded is the implicit claim that --merge
    is the only mode).

    Defect class: future slice accidentally modifies the --merge flow while
    adding --push or --sync-after-pr (e.g., changes confirmation prompt wording,
    drops a step). The slice-021 contract regresses silently.

    Regression-guard: anchor specific phrases unique to the slice-021 5-step
    merge flow.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # 5-step anchor phrases from slice-021's --merge flow.
    five_step_anchors = (
        "Stale-slice-branch check",  # Pre-flight guardrail 1 per slice-021 B5
        "git status --porcelain",  # Pre-flight guardrail 2 per slice-021 M5
        "git symbolic-ref refs/remotes/origin/HEAD",  # Step 3 default-branch resolution
        "git merge --no-ff",  # Step 3 merge invocation
        "Confirm merge + delete?",  # Step 4 explicit confirmation prompt
        "git branch -d",  # Step 5 safe-delete
    )
    for anchor in five_step_anchors:
        assert anchor in content, (
            f"skills/commit-slice/SKILL.md `--merge` 5-step flow missing "
            f"slice-021 anchor {anchor!r} — preservation guarantee broken "
            f"per slice-022 AC #1 + ADR-020 (--merge behavior is unchanged)"
        )


def test_commit_slice_skill_md_documents_no_flag_default_mode() -> None:
    """SKILL.md preserves the slice-021 no-flag generate-only default.

    Per /critique B4 ACCEPTED-FIXED: invoking `/commit-slice` with NO flag
    preserves slice-021 generate-only behavior (show message + HEREDOC
    instruction; no git operations). This is the default mode (Step 5a per
    slice-022 design.md).

    Defect class: 3-mode taxonomy is added but the no-flag default is
    accidentally dropped or replaced by an implicit `--merge`; users who run
    plain `/commit-slice` get unexpected git operations.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Step 5a explicit "Default (no flag)" reference.
    assert "Default (no flag)" in content or "no-flag default" in content, (
        "skills/commit-slice/SKILL.md must explicitly document the no-flag "
        "default mode (slice-021 generate-only behavior preserved per slice-022 "
        "AC #1 + /critique B4 ACCEPTED-FIXED)"
    )
    # HEREDOC convention from slice-021 preserved (no-flag default outputs the
    # message via HEREDOC for user to copy).
    assert "HEREDOC" in content or "heredoc" in content or "<<'EOF'" in content, (
        "skills/commit-slice/SKILL.md no-flag default mode must reference the "
        "HEREDOC instruction convention for copying the commit message"
    )


def test_commit_slice_skill_md_documents_mutual_exclusion_of_three_mode_flags() -> None:
    """SKILL.md documents that the 3 mode flags are mutually exclusive.

    Per /critique B4 ACCEPTED-FIXED: combining any 2 of `--merge`, `--push`,
    `--sync-after-pr` → STOP with diagnostic "Mode flags are mutually
    exclusive; pass exactly one (or none for the slice-021 generate-only
    default)."

    Defect class: user passes `--merge --push` accidentally; implementation
    silently chooses last-wins or first-wins; ambiguous behavior across runs.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Mutual-exclusion diagnostic phrase.
    has_mutual_exclusion_diag = (
        "mutually exclusive" in content
        or "Mutually exclusive" in content
    )
    assert has_mutual_exclusion_diag, (
        "skills/commit-slice/SKILL.md must document that the 3 mode flags "
        "(`--merge`, `--push`, `--sync-after-pr`) are mutually exclusive "
        "per slice-022 AC #1 + /critique B4 ACCEPTED-FIXED"
    )
    # Error-model row reference: combining any 2 → STOP.
    assert "pass exactly one" in content, (
        "skills/commit-slice/SKILL.md mutual-exclusion error model row must "
        "include the explicit 'pass exactly one' diagnostic"
    )
