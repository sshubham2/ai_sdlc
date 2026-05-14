"""Prose-pin tests for BRANCH-1 sub-mode (a) build-time branch-create at /build-slice.

Per slice-021 AC #1: skills/build-slice/SKILL.md `## Prerequisite check` H2 section
gains a NEW `### Branch state` sub-section pinning:
- the BRANCH-1 rule ID
- the canonical `slice/NNN-<slice-name>` branch-name pattern
- the canonical `BRANCH=skip` escape-hatch token
- the runtime default-branch resolution mechanism
  (`git symbolic-ref refs/remotes/origin/HEAD` + `init.defaultBranch` fallback)

These are prose-heuristic invariants the Claude main thread executes at /build-slice time.
Drift in any pinned phrase silently breaks the discipline.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_build_slice_skill_md_prerequisite_check_has_branch_state_sub_section() -> None:
    """`## Prerequisite check` H2 must contain a `### Branch state` sub-section."""
    content = read_file("skills/build-slice/SKILL.md")
    # The sub-section heading must appear after `## Prerequisite check` and before
    # the next H2 (which is `## Your task`).
    assert "## Prerequisite check" in content, (
        "skills/build-slice/SKILL.md must retain the `## Prerequisite check` H2"
    )
    prereq_block = content.split("## Prerequisite check", 1)[1].split("## Your task", 1)[0]
    assert "### Branch state" in prereq_block, (
        "skills/build-slice/SKILL.md `## Prerequisite check` H2 must contain a "
        "`### Branch state` sub-section per slice-021 AC #1"
    )
    assert "BRANCH-1" in prereq_block, (
        "Branch state sub-section must name the BRANCH-1 rule ID"
    )


def test_build_slice_skill_md_specifies_slice_branch_name_pattern() -> None:
    """Branch state sub-section must pin the canonical `slice/NNN-<slice-name>` pattern."""
    content = read_file("skills/build-slice/SKILL.md")
    prereq_block = content.split("## Prerequisite check", 1)[1].split("## Your task", 1)[0]
    # Canonical pattern uses `slice/` namespace prefix; either NNN-<slice-name>
    # placeholder or a concrete `slice/021-...`-style example must appear.
    assert "slice/" in prereq_block and "NNN" in prereq_block, (
        "Branch state sub-section must reference canonical `slice/NNN-<slice-name>` pattern"
    )


def test_build_slice_skill_md_specifies_branch_escape_hatch_via_branch_skip_deviation() -> None:
    """Branch state sub-section must reference the `BRANCH=skip` escape-hatch token."""
    content = read_file("skills/build-slice/SKILL.md")
    prereq_block = content.split("## Prerequisite check", 1)[1].split("## Your task", 1)[0]
    assert "BRANCH=skip" in prereq_block, (
        "Branch state sub-section must name the `BRANCH=skip` escape-hatch token "
        "(canonical shape pinned at Step 7c per slice-021 AC #2)"
    )


def test_build_slice_skill_md_specifies_runtime_default_branch_resolution() -> None:
    """Branch state sub-section must specify runtime default-branch resolution
    (NOT hard-coded master/main per slice-021 /critique M1 ACCEPTED-PENDING)."""
    content = read_file("skills/build-slice/SKILL.md")
    prereq_block = content.split("## Prerequisite check", 1)[1].split("## Your task", 1)[0]
    assert "git symbolic-ref refs/remotes/origin/HEAD" in prereq_block, (
        "Branch state sub-section must specify default-branch resolution via "
        "`git symbolic-ref refs/remotes/origin/HEAD`"
    )
    assert "init.defaultBranch" in prereq_block, (
        "Branch state sub-section must specify `init.defaultBranch` fallback"
    )
