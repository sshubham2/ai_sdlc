"""OSDG-1: content-equality between in-repo `skills/design-slice/SKILL.md` and
installed `~/.claude/skills/design-slice/SKILL.md`.

Per **PFS-1** (`methodology-changelog.md` v0.78.0; slice-088; [[ADR-080]]):
slice-088 adds a load-bearing `### Step 0.5` to `design-slice/SKILL.md` that
invokes `tools.project_frame_synth` before designing. Claude reads the
*installed* copy at `/design-slice` runtime, so a silent divergence would let
the shift-left project-frame consult skip on a stale install. This extends the
OSDG-1 guarded set (slice-049/051) to `design-slice` (previously unguarded).

EOL-agnostic per slice-033 EOL-DRIFT-1 / [[ADR-033]] — CRLF/LF is not drift.

Rule reference: OSDG-1 (slice-049; ADR-051; design-slice member-added at
slice-088 / PFS-1 / ADR-080); slice-007 CAD-1 per-file pattern; slice-033
EOL-DRIFT-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_design_slice_skill_md_are_content_equal():
    """In-repo `skills/design-slice/SKILL.md` MUST be content-equal (EOL-agnostic)
    to the installed copy at slice end (post-forward-sync).

    Rule reference: OSDG-1 (slice-049; ADR-051; design-slice member-added at
    slice-088 / PFS-1 / ADR-080); slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "design-slice" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "design-slice" / "SKILL.md",
        label="skills/design-slice/SKILL.md",
    )
