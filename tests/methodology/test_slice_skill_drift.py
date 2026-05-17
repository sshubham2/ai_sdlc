"""Mini-CAD-1: content-equality between in-repo `skills/slice/SKILL.md` and
installed `~/.claude/skills/slice/SKILL.md`.

Per slice-007 CAD-1 hybrid (option d): the in-repo file is canonical; the
installed copy MUST be forward-synced. Drift between them silently breaks
every /slice invocation on this developer's machine (Claude reads the
installed copy at runtime, not the in-repo canonical).

This is a scope-narrow per-file equality assertion mirroring slice-007's
`test_in_repo_and_installed_critique_agent_are_content_equal` shape for
`agents/critique.md`. It does NOT generalize INST-2 (which remains deferred
per slice-009 reflection at N=1 actual-drift evidence; slice-010 adds a
second per-file content-equality test mirroring CAD-1's pattern but does NOT
build a generalized audit tool).

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal modulo
line endings — a CRLF working tree vs an LF installed copy with identical
content is CLEAN; only genuine (non-EOL) divergence FAILs.

Rule reference: MCT-1 (slice-010); slice-007 CAD-1 pattern (per-file shape);
slice-033 EOL-DRIFT-1.
"""
from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced
from pathlib import Path


def test_in_repo_and_installed_slice_skill_md_are_content_equal():
    """In-repo `skills/slice/SKILL.md` MUST be content-equal (EOL-agnostic)
    to installed `~/.claude/skills/slice/SKILL.md` at slice end
    (post-forward-sync).

    Defect class (per slice-006 B1 prose-parity drift + slice-007 CAD-1
    generalized): if the in-repo and installed copies diverge, Claude reads
    stale prose at /slice invocation. For slice-010 specifically: the new
    MCT-1 bullet + evidence paragraph must be in the installed copy for
    Step 4a's mandatory-Critic trigger to fire on subsequent slices. CRLF/LF
    artifacts are NOT drift (slice-033 EOL-DRIFT-1).

    Rule reference: MCT-1 (slice-010); slice-007 CAD-1 per-file pattern;
    slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "slice" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "slice" / "SKILL.md",
        label="skills/slice/SKILL.md",
    )
