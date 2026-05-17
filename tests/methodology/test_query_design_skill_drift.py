"""QD-1: byte-equality between in-repo `skills/query-design/SKILL.md` and
installed `~/.claude/skills/query-design/SKILL.md`.

Per slice-032 / ADR-032: the in-repo file is canonical; the installed copy
MUST be forward-synced. Drift between them silently breaks every
/query-design invocation on this developer's machine (Claude reads the
installed copy at runtime, not the in-repo canonical) — and a stale
installed copy could silently lose the read-only / delegation-only
invariant, the load-bearing safety property of this skill.

Scope-narrow per-file equality assertion mirroring slice-010's
`test_in_repo_and_installed_slice_skill_md_are_content_equal` shape
(MCT-1 / slice-007 CAD-1 per-file pattern). Does NOT generalize a
multi-file drift audit (that remains the deferred add-skill-drift-audit
N>=2 follow-on per slice-027 ADR-025 future candidates).

Rule reference: QD-1 (slice-032; ADR-032); slice-010 MCT-1 / slice-007
CAD-1 per-file pattern.
"""
import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


def _sha256(path: Path) -> str:
    """Compute sha256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_in_repo_and_installed_query_design_skill_md_are_content_equal():
    """In-repo `skills/query-design/SKILL.md` MUST be byte-equal to installed
    `~/.claude/skills/query-design/SKILL.md` (post-forward-sync).

    Defect class (per slice-006 B1 prose-parity drift + slice-007 CAD-1
    generalized): if the in-repo and installed copies diverge, Claude reads
    stale prose at /query-design invocation — including a possibly weakened
    read-only invariant, the entire value proposition of this skill.

    Per slice-007 CAD-1 / ADR-006 reversibility: in-repo is canonical;
    forward-sync is the slice-author's responsibility. Mid-slice smoke gate
    is EXPECTED to see this test FAIL transiently (in-repo edited, installed
    not yet synced); post-forward-sync re-run sees it PASS.

    Rule reference: QD-1 (slice-032; ADR-032); slice-007 CAD-1 per-file
    pattern.
    """
    in_repo = REPO_ROOT / "skills" / "query-design" / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / "query-design" / "SKILL.md"

    assert in_repo.exists(), f"in-repo file missing: {in_repo}"
    assert installed.exists(), (
        f"installed file missing: {installed} -- has the AI SDLC plugin been "
        f"installed via INSTALL.md Step 3? `query-design` is enumerated in "
        f"tools/install_audit.py:_CANONICAL_SKILLS"
    )

    in_repo_sha = _sha256(in_repo)
    installed_sha = _sha256(installed)

    assert in_repo_sha == installed_sha, (
        f"skills/query-design/SKILL.md byte-equality FAILED:\n"
        f"  in-repo   ({in_repo}): sha256={in_repo_sha}\n"
        f"  installed ({installed}): sha256={installed_sha}\n"
        f"Forward-sync after in-repo edit was forgotten. Run "
        f"`Copy-Item skills/query-design/SKILL.md "
        f"~/.claude/skills/query-design/SKILL.md` per slice-032 design.md."
    )
