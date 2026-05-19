"""OSDG-1: content-equality between in-repo `skills/reflect/SKILL.md` and
installed `~/.claude/skills/reflect/SKILL.md`.

Per slice-049 OSDG-1 (ADR-051) extended at slice-051 (ADR-053): the
in-repo file is canonical; the installed copy MUST be forward-synced.
`/reflect` is an in-loop pipeline skill (NOT a pipeline opener like
`/triage` or `/adopt` — OSDG-1's "Opener-Skill" name is a historical
label, not a scope boundary; ADR-053 records the decoupling). slice-050
added the AVFS-1 `Step 5b-avfs` post-write block to `reflect/SKILL.md`,
making it load-bearing: Claude reads the *installed* copy at `/reflect`
runtime, so a silent divergence lets the AVFS-1 gate's `/reflect` arm
skip on a stale install (the `/build-slice` arm lives in OSDG-1-guarded
`build-slice/SKILL.md`, so the gate is not fully defeated — bounded but
real). Before slice-051 the only control was slice-050 must-not-defer
(human-dependent manual forward-sync). slice-051 closes that N=1 latent
exposure (slice-050 reflection "Discovered" / meta-Critic M-add-1).

Scope-narrow per-file equality assertion mirroring slice-010's
`test_in_repo_and_installed_slice_skill_md_are_content_equal` shape
(MCT-1 / slice-007 CAD-1 per-file pattern), structural twin of
slice-049's `test_triage_skill_drift.py` / `test_adopt_skill_drift.py`.
Extends — does NOT supersede — the CAD-1 (slice-007) / mini-CAD
(slice-010) / EOL-DRIFT-1 (slice-033) / OSDG-1 (slice-049) lineage; it
does NOT generalize a multi-file drift audit (INST-2 remains deferred
per slice-009/010 law).

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal
modulo line endings — CRLF/LF artifacts are NOT drift; only genuine
(non-EOL) divergence FAILs.

Rule reference: OSDG-1 (slice-049; ADR-051; member-added at slice-051 /
ADR-053; extends slice-010 MCT-1 / slice-007 CAD-1 per-file pattern +
slice-033 EOL-DRIFT-1).
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_reflect_skill_md_are_content_equal():
    """In-repo `skills/reflect/SKILL.md` MUST be content-equal (EOL-agnostic
    per slice-033 EOL-DRIFT-1) to installed `~/.claude/skills/reflect/SKILL.md`
    at slice end (post-forward-sync).

    Defect class (per slice-006 B1 prose-parity drift + slice-007 CAD-1
    generalized): if the in-repo and installed copies diverge, Claude reads
    stale prose at `/reflect` invocation — the in-loop slice-retrospective
    skill that owns the AVFS-1 `Step 5b-avfs` post-write forward-sync block
    (added slice-050). A stale installed copy could silently skip the
    `/reflect` arm of the AVFS-1 `ai-sdlc-VERSION` gate. CRLF/LF artifacts
    are NOT drift (slice-033 EOL-DRIFT-1).

    Rule reference: OSDG-1 (slice-049; ADR-051; member-added at slice-051 /
    ADR-053); slice-007 CAD-1 per-file pattern; slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "reflect" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "reflect" / "SKILL.md",
        label="skills/reflect/SKILL.md",
    )
