"""Prose-pin tests for slice-022 AC #2: `/commit-slice --push` mode.

Per slice-022 design.md + ADR-020:
- `skills/commit-slice/SKILL.md` frontmatter `argument-hint` lists `--push` in the
  mutually-exclusive flag set `[--merge | --push | --sync-after-pr]`.
- Step 5 has a new sub-step (5c) documenting the `--push` flow: WT-clean + stale-
  slice-branch + origin-present + slice-branch-name pre-flight guardrails; commit
  on slice branch; `git push -u origin slice/NNN-<name>` (NEVER `--force`); display
  PR-creation URL hint (`gh pr create` + GitHub compare URL).
- `--push` does NOT merge locally, does NOT delete the slice branch, does NOT touch
  the default branch.

These prose-pin tests use substring assertions against `skills/commit-slice/SKILL.md`.
The full runtime exercise (sandbox push to a fixture remote) lives at /validate-slice
Step 5.5 row 22.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_skill_md_documents_push_flag_in_frontmatter_and_step_5() -> None:
    """SKILL.md frontmatter argument-hint includes --push AND Step 5 has a sub-
    section dedicated to --push.

    Defect class: --push flag is introduced in description prose but the
    frontmatter is not updated; Claude's argument parser sees the old surface.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # Frontmatter must list --push in the mutually-exclusive flag set.
    assert (
        "argument-hint: [--merge | --push | --sync-after-pr]" in content
    ), (
        "skills/commit-slice/SKILL.md frontmatter `argument-hint` must be "
        "`[--merge | --push | --sync-after-pr]` (3-mode mutually-exclusive set "
        "per slice-022 AC #1 + ADR-020 + /critique B4 ACCEPTED-FIXED)"
    )
    # Step 5 sub-section reference for --push.
    assert "--push" in content, (
        "skills/commit-slice/SKILL.md must reference `--push` flag in body"
    )
    assert "git push -u origin slice" in content, (
        "skills/commit-slice/SKILL.md `--push` sub-step must specify the canonical "
        "command `git push -u origin slice/...` (first-push OR fast-forward re-push "
        "semantics; NEVER --force per slice-022 must-not-defer)"
    )


def test_skill_md_push_flag_does_not_merge_or_delete() -> None:
    """SKILL.md --push sub-step explicitly states it does NOT merge locally and
    does NOT delete the slice branch.

    Defect class: --push prose lifted from --merge by accident, accidentally
    inheriting the local-merge or branch-delete steps; user runs --push and loses
    the slice branch unexpectedly.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # `--push` MUST NOT include `git merge` or `git branch -d` in its flow.
    # We check this prose-claim is documented (negative-pin): the phrase
    # "NOT merged locally" or equivalent appears alongside --push.
    has_does_not_merge = (
        "Never merges, never deletes" in content
        or "does NOT merge locally" in content
        or "NOT merged locally and NOT deleted" in content
        or "is NOT merged locally and NOT deleted" in content
    )
    assert has_does_not_merge, (
        "skills/commit-slice/SKILL.md `--push` sub-step must explicitly state "
        "that --push does NOT merge locally and does NOT delete the slice branch "
        "(prevents accidental --merge-style behavior in --push)"
    )
    # NEVER --force anchor for --push push command.
    assert (
        "NEVER `--force`" in content or "NEVER --force" in content
    ), (
        "skills/commit-slice/SKILL.md `--push` must include `NEVER --force` "
        "anchor — `--push` is first-push OR fast-forward re-push only per "
        "slice-022 must-not-defer + /critique M4 ACCEPTED-FIXED"
    )


def test_skill_md_push_flag_displays_pr_creation_hint() -> None:
    """SKILL.md --push sub-step documents PR-creation URL hint derivation:
    `gh pr create` command + GitHub compare URL pattern.

    Defect class: --push pushes the branch but provides no actionable next step
    for the user to open a PR; --push becomes a write-only flow with no
    workflow continuation.
    """
    content = read_file("skills/commit-slice/SKILL.md")
    # `gh pr create` invocation pattern.
    assert "gh pr create" in content, (
        "skills/commit-slice/SKILL.md `--push` must document the `gh pr create` "
        "command suggestion (works for GitHub.com + Enterprise via gh CLI)"
    )
    # GitHub compare URL pattern (github.com handled in v1; Enterprise deferred
    # per /critique B3 DEFERRED to `add-github-enterprise-url-derivation` slice).
    assert "/compare/" in content, (
        "skills/commit-slice/SKILL.md `--push` must document the GitHub compare "
        "URL pattern `/compare/<default>...slice/NNN` (raw browser-openable URL "
        "alongside the gh pr create command per slice-022 design.md L75-77)"
    )
