"""OSDG-1: content-equality between in-repo `skills/triage/SKILL.md` and
installed `~/.claude/skills/triage/SKILL.md`.

Per slice-049 OSDG-1 (Opener-Skill Drift Guard; ADR-051): the in-repo file
is canonical; the installed copy MUST be forward-synced. `/triage` is the
greenfield pipeline-opener skill — Claude reads the *installed* copy at
runtime, not the in-repo canonical. A silent divergence ships every
`/triage` invocation on this developer's machine against stale opener
prose; before slice-049 the only control was slice-048 must-not-defer #3
(human-dependent manual forward-sync). OSDG-1 closes that N=1 latent
exposure (slice-048 reflection "Discovered").

Scope-narrow per-file equality assertion mirroring slice-010's
`test_in_repo_and_installed_slice_skill_md_are_content_equal` shape
(MCT-1 / slice-007 CAD-1 per-file pattern). Extends — does NOT
supersede — the CAD-1 (slice-007) / mini-CAD (slice-010) / EOL-DRIFT-1
(slice-033) lineage; it does NOT generalize a multi-file drift audit
(INST-2 remains deferred per slice-009/010 law).

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal
modulo line endings — CRLF/LF artifacts are NOT drift; only genuine
(non-EOL) divergence FAILs.

Rule reference: OSDG-1 (slice-049; ADR-051; extends slice-010 MCT-1 /
slice-007 CAD-1 per-file pattern + slice-033 EOL-DRIFT-1).
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_triage_skill_md_are_content_equal():
    """In-repo `skills/triage/SKILL.md` MUST be content-equal (EOL-agnostic
    per slice-033 EOL-DRIFT-1) to installed `~/.claude/skills/triage/SKILL.md`
    at slice end (post-forward-sync).

    Defect class (per slice-006 B1 prose-parity drift + slice-007 CAD-1
    generalized): if the in-repo and installed copies diverge, Claude reads
    stale prose at `/triage` invocation — the greenfield project-opener that
    emits the project-root CLAUDE.md and picks pipeline mode. CRLF/LF
    artifacts are NOT drift (slice-033 EOL-DRIFT-1).

    Rule reference: OSDG-1 (slice-049; ADR-051); slice-007 CAD-1 per-file
    pattern; slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "triage" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "triage" / "SKILL.md",
        label="skills/triage/SKILL.md",
    )
