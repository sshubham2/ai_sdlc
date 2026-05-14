"""Mini-CAD-1: byte-equality between in-repo `skills/build-slice/SKILL.md` and
installed `~/.claude/skills/build-slice/SKILL.md`.

Per slice-021 AC #5 + slice-007 CAD-1 hybrid (option d): the in-repo file is
canonical; the installed copy MUST be forward-synced. Drift between them silently
breaks every /build-slice invocation on this developer's machine (Claude reads the
installed copy at runtime, not the in-repo canonical).

Mirrors slice-010's `test_slice_skill_drift.py` pattern. Slice-021 introduces the
`## Prerequisite check ### Branch state` sub-section + Step 7c canonical BRANCH=skip
shape sentence + Step 6 pre-finish gate BRANCH-1 audit bullet — all 3 edits in
`skills/build-slice/SKILL.md` must be forward-synced.

Status transitions: PENDING -> WRITTEN-FAILING (after in-repo SKILL.md edits but
before Phase 3 forward-sync) -> PASSING (post-forward-sync).
"""
import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


def _sha256(path: Path) -> str:
    """Compute sha256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_build_slice_skill_md_in_repo_byte_equal_installed() -> None:
    """In-repo `skills/build-slice/SKILL.md` MUST be byte-equal to installed copy."""
    in_repo = REPO_ROOT / "skills" / "build-slice" / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / "build-slice" / "SKILL.md"

    assert in_repo.exists(), f"in-repo file missing: {in_repo}"
    assert installed.exists(), (
        f"installed file missing: {installed} -- has the AI SDLC plugin been "
        f"installed via INSTALL.md Step 3? `build-slice` is enumerated in "
        f"tools/install_audit.py:_CANONICAL_SKILLS"
    )

    in_repo_sha = _sha256(in_repo)
    installed_sha = _sha256(installed)

    assert in_repo_sha == installed_sha, (
        f"skills/build-slice/SKILL.md byte-equality FAILED:\n"
        f"  in-repo   ({in_repo}): sha256={in_repo_sha}\n"
        f"  installed ({installed}): sha256={installed_sha}\n"
        f"Forward-sync after in-repo edit was forgotten. Run Phase 3 "
        f"Copy-Item per slice-021 design.md."
    )
