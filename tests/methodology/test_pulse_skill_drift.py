"""OSDG-1-class CAD-1 byte-equality between in-repo `skills/pulse/SKILL.md`
and installed `~/.claude/skills/pulse/SKILL.md`.

Per slice-077 / ADR-070: slice-077 edits skills/pulse/SKILL.md Step 1 + Step 2
+ Step 3 prose. `/pulse` is an in-loop methodology skill (NOT an opener); Claude
reads the *installed* copy at `/pulse` invocation, so any silent divergence
between in-repo and installed would defeat slice-077's worktree-awareness
enhancement (stale installed prose → /pulse silently ignores worktrees).

Mirrors test_reflect_skill_drift.py shape (slice-049/051 OSDG-1 pattern). Per
slice-033 EOL-DRIFT-1 / ADR-033: comparison is content-equal modulo line
endings; CRLF/LF artifacts are NOT drift.

slice-077 itself is the canonical N+1 governed-slice for this drift test — it
authors both the test AND the SKILL.md edits. The forward-sync (cp -p
skills/pulse/SKILL.md ~/.claude/skills/pulse/SKILL.md) happens at /build-slice
Phase D after the SKILL.md edits land.

Rule reference: slice-007 CAD-1 per-file pattern; slice-033 EOL-DRIFT-1;
slice-049 OSDG-1 (extended to in-loop skills at slice-051 / ADR-053).
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_pulse_skill_md_byte_equal():
    """In-repo `skills/pulse/SKILL.md` MUST be content-equal (EOL-agnostic per
    slice-033 EOL-DRIFT-1) to installed `~/.claude/skills/pulse/SKILL.md` at
    slice end (post-forward-sync).

    Defect class: stale installed prose would cause Claude to read the
    pre-slice-077 /pulse implementation (no worktree-awareness), defeating the
    slice's witnessed-gap closure. CRLF/LF artifacts are NOT drift.

    Rule reference: slice-007 CAD-1; slice-033 EOL-DRIFT-1; slice-049 OSDG-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "pulse" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "pulse" / "SKILL.md",
        label="skills/pulse/SKILL.md",
    )
