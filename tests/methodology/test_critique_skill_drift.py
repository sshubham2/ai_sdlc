"""OSDG-1: content-equality between in-repo `skills/critique/SKILL.md` and
installed `~/.claude/skills/critique/SKILL.md`.

Per **PFS-1** (`methodology-changelog.md` v0.78.0; slice-088; [[ADR-080]]):
slice-088 adds the project-frame to `critique/SKILL.md` Step 1 Inputs + the
Step 2 agent-prompt body (`# project-frame.md`). Claude reads the *installed*
copy at `/critique` runtime, so a silent divergence would let the handed-over
frame skip on a stale install. This extends the OSDG-1 guarded set to
`critique` (previously unguarded — only `agents/critique.md` was CAD-1-guarded).

EOL-agnostic per slice-033 EOL-DRIFT-1 / [[ADR-033]] — CRLF/LF is not drift.

Rule reference: OSDG-1 (slice-049; ADR-051; critique member-added at
slice-088 / PFS-1 / ADR-080); slice-007 CAD-1 per-file pattern; slice-033
EOL-DRIFT-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_critique_skill_md_are_content_equal():
    """In-repo `skills/critique/SKILL.md` MUST be content-equal (EOL-agnostic)
    to the installed copy at slice end (post-forward-sync).

    Rule reference: OSDG-1 (slice-049; ADR-051; critique member-added at
    slice-088 / PFS-1 / ADR-080); slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "critique" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "critique" / "SKILL.md",
        label="skills/critique/SKILL.md",
    )
