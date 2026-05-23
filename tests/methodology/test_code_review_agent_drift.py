"""CAD-1 family member: agents/code-review.md in-repo↔installed
content-equality, EOL-agnostic (per EOL-DRIFT-1 / ADR-033).

Per slice-007 CAD-1 (the original Critic-Agent Drift discipline) + the
slice-049/051 OSDG-1 family-add pattern: a forgotten forward-sync to
`~/.claude/agents/code-review.md` leaves Claude reading stale code-Critic
adversarial-prompt prose at runtime — the new agent's prompt body IS its
load-bearing contract (per the slice-007 "treat the prompt like compiled
code, not a comment" principle).

Reuses `tests/skill_drift_equality.py::assert_md_forward_synced` verbatim
(the EOL-DRIFT-1 / ADR-033 comparator).

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060;
ADR-059); extends CAD-1 (slice-007) family lineage.
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_code_review_agent_md_are_content_equal():
    """agents/code-review.md MUST be content-equal modulo line endings to
    its installed copy at ~/.claude/agents/code-review.md.
    """
    in_repo = REPO_ROOT / "agents" / "code-review.md"
    installed = Path.home() / ".claude" / "agents" / "code-review.md"
    assert_md_forward_synced(
        in_repo, installed, label="agents/code-review.md"
    )
