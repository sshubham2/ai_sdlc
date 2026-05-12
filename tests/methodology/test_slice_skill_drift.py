"""Mini-CAD-1: byte-equality between in-repo `skills/slice/SKILL.md` and
installed `~/.claude/skills/slice/SKILL.md`.

Per slice-007 CAD-1 hybrid (option d): the in-repo file is canonical; the
installed copy MUST be forward-synced. Drift between them silently breaks
every /slice invocation on this developer's machine (Claude reads the
installed copy at runtime, not the in-repo canonical).

This is a scope-narrow per-file equality assertion mirroring slice-007's
`test_in_repo_and_installed_critique_agent_are_content_equal` shape for
`agents/critique.md`. It does NOT generalize INST-2 (which remains deferred
per slice-009 reflection at N=1 actual-drift evidence; slice-010 adds a
second per-file byte-equality test mirroring CAD-1's pattern but does NOT
build a generalized audit tool).

Per slice-010 Critic B2 + slice-009 mission-brief row 3 precedent: this test
starts at TF-1 status PASSING (file pair byte-equal at slice start per
Phase 0 sha256 capture); transitions PASSING -> WRITTEN-FAILING (Phase 2
in-repo edit; observed at Phase 2b mid-slice smoke gate) -> PASSING
(Phase 2c post-forward-sync).

Rule reference: MCT-1 (slice-010); slice-007 CAD-1 pattern (per-file shape).
"""
import hashlib
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT


def _sha256(path: Path) -> str:
    """Compute sha256 hex digest of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_in_repo_and_installed_slice_skill_md_are_content_equal():
    """In-repo `skills/slice/SKILL.md` MUST be byte-equal to installed
    `~/.claude/skills/slice/SKILL.md` at slice end (post-forward-sync).

    Defect class (per slice-006 B1 prose-parity drift + slice-007 CAD-1
    generalized): if the in-repo and installed copies diverge, Claude reads
    stale prose at /slice invocation. For slice-010 specifically: the new
    MCT-1 bullet + evidence paragraph must be in the installed copy for
    Step 4a's mandatory-Critic trigger to fire on subsequent slices.

    Per slice-007 CAD-1 / ADR-006 reversibility: in-repo is canonical;
    forward-sync is the slice-author's responsibility at Phase 2c. Mid-slice
    smoke gate (Phase 2b) is EXPECTED to see this test FAIL (in-repo edited,
    installed not yet synced); post-forward-sync (Phase 2c) re-run sees it
    PASS.

    Rule reference: MCT-1 (slice-010); slice-007 CAD-1 per-file pattern.
    """
    in_repo = REPO_ROOT / "skills" / "slice" / "SKILL.md"
    installed = Path.home() / ".claude" / "skills" / "slice" / "SKILL.md"

    assert in_repo.exists(), f"in-repo file missing: {in_repo}"
    assert installed.exists(), (
        f"installed file missing: {installed} -- has the AI SDLC plugin been "
        f"installed via INSTALL.md Step 3? `slice` is enumerated in "
        f"tools/install_audit.py:_CANONICAL_SKILLS"
    )

    in_repo_sha = _sha256(in_repo)
    installed_sha = _sha256(installed)

    assert in_repo_sha == installed_sha, (
        f"skills/slice/SKILL.md byte-equality FAILED:\n"
        f"  in-repo   ({in_repo}): sha256={in_repo_sha}\n"
        f"  installed ({installed}): sha256={installed_sha}\n"
        f"Forward-sync after in-repo edit was forgotten. Run Phase 2c "
        f"Copy-Item per slice-010 design.md."
    )
