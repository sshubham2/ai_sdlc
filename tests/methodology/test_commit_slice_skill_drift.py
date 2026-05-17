"""Mini-CAD-1: content-equality between in-repo `skills/commit-slice/SKILL.md` and
installed `~/.claude/skills/commit-slice/SKILL.md`.

Per slice-021 AC #5 + slice-007 CAD-1 hybrid (option d). Slice-021 introduces the
`--do-commit` -> `--merge` swap with 2 pre-flight guardrails — must be forward-synced.

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal modulo
line endings — CRLF/LF artifacts are NOT drift; only genuine (non-EOL)
divergence FAILs.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_commit_slice_skill_md_in_repo_byte_equal_installed() -> None:
    """In-repo `skills/commit-slice/SKILL.md` MUST be content-equal
    (EOL-agnostic per slice-033 EOL-DRIFT-1) to its installed copy."""
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "commit-slice" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "commit-slice" / "SKILL.md",
        label="skills/commit-slice/SKILL.md",
    )
