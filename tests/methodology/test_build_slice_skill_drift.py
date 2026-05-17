"""Mini-CAD-1: content-equality between in-repo `skills/build-slice/SKILL.md` and
installed `~/.claude/skills/build-slice/SKILL.md`.

Per slice-021 AC #5 + slice-007 CAD-1 hybrid (option d): the in-repo file is
canonical; the installed copy MUST be forward-synced. Drift between them silently
breaks every /build-slice invocation on this developer's machine (Claude reads the
installed copy at runtime, not the in-repo canonical).

Mirrors slice-010's `test_slice_skill_drift.py` pattern. Slice-021 introduces the
`## Prerequisite check ### Branch state` sub-section + Step 7c canonical BRANCH=skip
shape sentence + Step 6 pre-finish gate BRANCH-1 audit bullet — all 3 edits in
`skills/build-slice/SKILL.md` must be forward-synced.

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal modulo
line endings — CRLF/LF artifacts are NOT drift; only genuine (non-EOL)
divergence FAILs.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_build_slice_skill_md_in_repo_byte_equal_installed() -> None:
    """In-repo `skills/build-slice/SKILL.md` MUST be content-equal
    (EOL-agnostic per slice-033 EOL-DRIFT-1) to its installed copy."""
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "build-slice" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "build-slice" / "SKILL.md",
        label="skills/build-slice/SKILL.md",
    )
