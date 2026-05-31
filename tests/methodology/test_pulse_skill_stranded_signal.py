"""Structural-pin: /pulse SKILL.md surfaces the bare-branch stranded signal (R-26 / ADR-079).

Window-scoped per BC-PROJ-14: anchor on the unique `Stranded-slice signal` bullet
literal and assert the load-bearing literals within the following window — the
case slice-077's worktree pre-read does NOT cover (a bare unmerged `slice/*`
branch without a live worktree).
"""
from __future__ import annotations

from pathlib import Path

from tests.methodology.conftest import REPO_ROOT

_SKILL = REPO_ROOT / "skills" / "pulse" / "SKILL.md"


def test_pulse_skill_surfaces_stranded_signal():
    text = _SKILL.read_text(encoding="utf-8")
    anchor = text.find("Stranded-slice signal")
    assert anchor != -1, "/pulse SKILL.md must carry a `Stranded-slice signal` bullet (R-26)"
    window = text[anchor:anchor + 1200]

    # Invokes the detector and names the genuinely-new bare-branch case.
    assert "tools.stranded_slice_audit" in window, (
        "the /pulse signal must invoke `$PY -m tools.stranded_slice_audit`"
    )
    assert "bare unmerged" in window, (
        "the signal must name the bare-unmerged-branch-without-a-worktree case (the case "
        "slice-077's worktree pre-read does NOT cover)"
    )
    # Surfaces only halt-worthy classes as a warning; informational classes are parallel-normal.
    assert "stranded-complete" in window
    assert "halt: true" in window, "only halt-worthy entries are surfaced as a ⚠ stranded note"
    assert "in-progress" in window and "claimed-by-other" in window, (
        "informational classes must be named as parallel-normal (NOT warnings)"
    )
    # 5th informational klass (slice-092 / ADR-084): a branchless in-flight scaffold.
    assert "branchless-in-flight" in window, (
        "the `branchless-in-flight` klass must be named as a parallel-normal "
        "situational-awareness class so /pulse can render branchless in-flight work, "
        "not silently drop it (M1)"
    )
