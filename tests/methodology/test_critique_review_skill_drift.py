"""OSDG-1: content-equality between in-repo `skills/critique-review/SKILL.md`
and installed `~/.claude/skills/critique-review/SKILL.md`.

Per **PFS-1** (`methodology-changelog.md` v0.78.0; slice-088; [[ADR-080]]):
slice-088 adds the project-frame to `critique-review/SKILL.md` Step 1 Inputs +
the Step 2 agent-prompt body (`# project-frame.md`). Claude reads the
*installed* copy at `/critique-review` runtime, so a silent divergence would
let the handed-over frame skip on a stale install. This extends the OSDG-1
guarded set to `critique-review` (previously unguarded).

EOL-agnostic per slice-033 EOL-DRIFT-1 / [[ADR-033]] — CRLF/LF is not drift.

Rule reference: OSDG-1 (slice-049; ADR-051; critique-review member-added at
slice-088 / PFS-1 / ADR-080); slice-007 CAD-1 per-file pattern; slice-033
EOL-DRIFT-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_critique_review_skill_md_are_content_equal():
    """In-repo `skills/critique-review/SKILL.md` MUST be content-equal
    (EOL-agnostic) to the installed copy at slice end (post-forward-sync).

    Rule reference: OSDG-1 (slice-049; ADR-051; critique-review member-added at
    slice-088 / PFS-1 / ADR-080); slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "critique-review" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "critique-review" / "SKILL.md",
        label="skills/critique-review/SKILL.md",
    )
