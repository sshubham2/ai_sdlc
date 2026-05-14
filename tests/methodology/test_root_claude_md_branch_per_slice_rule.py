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
