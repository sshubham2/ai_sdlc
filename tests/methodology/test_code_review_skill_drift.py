"""OSDG-1 family member: skills/code-review/SKILL.md in-repo↔installed
content-equality, EOL-agnostic (per EOL-DRIFT-1 / ADR-033).

Per slice-049 / slice-051 OSDG-1 lineage (the slice-019 LAYER-EVID-1 +
slice-007 CAD-1 + slice-010 mini-CAD precedents): a forgotten forward-sync
to `~/.claude/skills/code-review/SKILL.md` leaves Claude reading stale
`/code-review` orchestration prose at runtime, with no other gate catching
it. CRSI-1 makes /code-review an in-loop runtime-behavioral skill — the
drift exposure class OSDG-1 exists to close.

Reuses `tests/skill_drift_equality.py::assert_md_forward_synced` verbatim
— do NOT introduce a new byte-equality comparator (R-5 retirement /
EOL-DRIFT-1 / ADR-033 preserved).

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060;
ADR-059); extends OSDG-1 (slice-049/051 / ADR-051) family lineage.
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_code_review_skill_md_are_content_equal():
    """skills/code-review/SKILL.md MUST be content-equal modulo line
    endings to its installed copy at ~/.claude/skills/code-review/SKILL.md.
    """
    in_repo = REPO_ROOT / "skills" / "code-review" / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / "code-review" / "SKILL.md"
    assert_md_forward_synced(
        in_repo, installed, label="skills/code-review/SKILL.md"
    )
