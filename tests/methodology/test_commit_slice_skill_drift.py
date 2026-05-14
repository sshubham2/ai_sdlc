"""Mini-CAD-1: byte-equality between in-repo `skills/commit-slice/SKILL.md` and
installed `~/.claude/skills/commit-slice/SKILL.md`.

Per slice-021 AC #5 + slice-007 CAD-1 hybrid (option d). Slice-021 introduces the
`--do-commit` → `--merge` swap with 2 pre-flight guardrails — must be forward-synced.

Status transitions: PENDING -> WRITTEN-FAILING (after in-repo SKILL.md edits but
before Phase 3 forward-sync) -> PASSING (post-forward-sync).
"""
import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


def _sha256(path: Path) -> str:
    """Compute sha256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_commit_slice_skill_md_in_repo_byte_equal_installed() -> None:
    """In-repo `skills/commit-slice/SKILL.md` MUST be byte-equal to installed copy."""
    in_repo = REPO_ROOT / "skills" / "commit-slice" / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / "commit-slice" / "SKILL.md"

    assert in_repo.exists(), f"in-repo file missing: {in_repo}"
    assert installed.exists(), (
        f"installed file missing: {installed} -- has the AI SDLC plugin been "
        f"installed via INSTALL.md Step 3? `commit-slice` is enumerated in "
        f"tools/install_audit.py:_CANONICAL_SKILLS"
    )

    in_repo_sha = _sha256(in_repo)
    installed_sha = _sha256(installed)

    assert in_repo_sha == installed_sha, (
        f"skills/commit-slice/SKILL.md byte-equality FAILED:\n"
        f"  in-repo   ({in_repo}): sha256={in_repo_sha}\n"
        f"  installed ({installed}): sha256={installed_sha}\n"
        f"Forward-sync after in-repo edit was forgotten. Run Phase 3 "
        f"Copy-Item per slice-021 design.md."
    )
