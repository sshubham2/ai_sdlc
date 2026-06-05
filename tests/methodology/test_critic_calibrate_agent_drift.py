"""CAD-1 family member: agents/critic-calibrate.md in-repo↔installed
content-equality, EOL-agnostic (per EOL-DRIFT-1 / ADR-033).

Per slice-007 CAD-1 (the original Critic-Agent Drift discipline) + the
slice-049/051 OSDG-1 family-add pattern: a forgotten forward-sync to
`~/.claude/agents/critic-calibrate.md` leaves Claude reading stale meta-Critic
prose at runtime — the agent's prompt body IS its load-bearing contract (per
the slice-007 "treat the prompt like compiled code, not a comment" principle).

slice-114 (ADR-105) converts `agents/critic-calibrate.md` to the `<vault>/`
prose seam + embeds a self-sufficient resolver note. That converted runtime
prompt MUST stay in sync with the installed copy or a Task-spawned subagent
(which does NOT inherit the project CLAUDE.md) resolves a stale / note-less
`<vault>/` path — the M1 / slice-113 M-add-1 stale-roster class. Before this
slice critic-calibrate.md was the second CAD-1-guarded agent with no drift
test (code-review.md being the first); this test closes that asymmetry.

Reuses `tests/skill_drift_equality.py::assert_md_forward_synced` verbatim
(the EOL-DRIFT-1 / ADR-033 comparator).

Rule reference: CRSI-1 (methodology-changelog.md v0.64.0; slice-060;
ADR-059); extends CAD-1 (slice-007) family lineage. Added slice-114 (ADR-105).
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_critic_calibrate_agent_md_are_content_equal():
    """agents/critic-calibrate.md MUST be content-equal modulo line endings to
    its installed copy at ~/.claude/agents/critic-calibrate.md.
    """
    in_repo = REPO_ROOT / "agents" / "critic-calibrate.md"
    installed = Path.home() / ".claude" / "agents" / "critic-calibrate.md"
    assert_md_forward_synced(
        in_repo, installed, label="agents/critic-calibrate.md"
    )
