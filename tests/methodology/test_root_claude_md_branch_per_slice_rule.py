"""Prose-pin test for the root CLAUDE.md Branch-per-slice bullet.

Per slice-021 AC #5: root project CLAUDE.md "Brownfield rules" section
gains a new bullet pointing at /build-slice Prerequisite check + /commit-slice --merge.
"""
from __future__ import annotations

from tests.methodology.conftest import read_file


def test_root_claude_md_has_branch_per_slice_bullet() -> None:
    """Root CLAUDE.md must contain a Branch-per-slice bullet in Brownfield rules."""
    content = read_file("CLAUDE.md")
    assert "Branch-per-slice" in content, (
        "Root CLAUDE.md must contain a `Branch-per-slice` bullet per slice-021 AC #5"
    )
    # Verify it's in the Brownfield rules section.
    assert "## Brownfield rules" in content, "Root CLAUDE.md must retain ## Brownfield rules"
    brownfield_section_start = content.find("## Brownfield rules")
    next_section = content.find("\n## ", brownfield_section_start + 1)
    brownfield_block = (
        content[brownfield_section_start:next_section]
        if next_section > 0
        else content[brownfield_section_start:]
    )
    assert "Branch-per-slice" in brownfield_block, (
        "Branch-per-slice bullet must appear within the ## Brownfield rules section "
        "(not elsewhere in CLAUDE.md)"
    )


# --- Slice-066 / BRANCH-2 worktree-rewrite pin (AC4) ---

def test_branch_per_slice_paragraph_rewritten_to_worktree_per_slice() -> None:
    """Root CLAUDE.md must have the active bullet rewritten to `Worktree-per-slice + branch` citing BRANCH-2 + ADR-063.

    Defect class: pre-slice-066 the bullet read `**Branch-per-slice.** Per BRANCH-1 ...`. Post-slice-066,
    the active bullet is `**Worktree-per-slice + branch.** Per BRANCH-2 ([[ADR-063]]; methodology v0.68.0) ...`
    while preserving the BRANCH-1 lineage citation as historical anchor (per ADR-063 §Scope of supersession
    "Carried forward unchanged" — `branch-per-slice workflow` phrase preserved as historical anchor for
    archive Glob).
    Rule reference: BRANCH-2 (slice-066; ADR-063); historical anchor BRANCH-1 (slice-021; ADR-019).
    """
    content = read_file("CLAUDE.md")
    # Active bullet title MUST be "Worktree-per-slice"
    assert "Worktree-per-slice" in content, (
        "Root CLAUDE.md must contain a `Worktree-per-slice` bullet (per BRANCH-2 / [[ADR-063]] / "
        "methodology v0.68.0); supersedes BRANCH-1's `Branch-per-slice` bullet"
    )
    # Must cite BRANCH-2 + ADR-063
    assert "BRANCH-2" in content, (
        "Root CLAUDE.md Worktree-per-slice bullet must cite BRANCH-2 rule reference"
    )
    assert "ADR-063" in content, (
        "Root CLAUDE.md Worktree-per-slice bullet must cite [[ADR-063]] decision reference"
    )
    # Must reference v0.68.0 methodology-changelog version
    assert "v0.68.0" in content, (
        "Root CLAUDE.md Worktree-per-slice bullet must cite methodology v0.68.0"
    )
