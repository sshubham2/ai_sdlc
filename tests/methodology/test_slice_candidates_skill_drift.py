"""OSDG-1: content-equality between in-repo `skills/slice-candidates/SKILL.md`
and installed `~/.claude/skills/slice-candidates/SKILL.md`.

Per slice-096 (R-13): `/slice-candidates` was the lone methodology skill in the
OSDG-1 / mini-CAD guarded family with no per-skill drift guard (R-13, open since
slice-052). Drift between the in-repo canonical and the installed copy silently
breaks every `/slice-candidates` invocation on this developer's machine (Claude
reads the installed copy at runtime, not the in-repo canonical) -- including a
silently-weakened "never read source files" read-only invariant (the ADR-054
bounded `--obo-peek` carve-out, the load-bearing safety property of this skill).

Scope-narrow per-file equality assertion mirroring the slice-032 QD-1 /
slice-010 MCT-1 / slice-007 CAD-1 per-file pattern. Does NOT generalize a
multi-file drift audit; reuses the shared `assert_md_forward_synced` comparator
unchanged.

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal modulo
line endings -- CRLF/LF artifacts are NOT drift; only genuine (non-EOL)
divergence FAILs.

MEPD-1 = EXCLUDE (slice-096 design): adding this member to the already
open-ended OSDG-1 guarded set is a test-only extension -- no new RULE-ID, no
methodology-changelog entry, no VERSION bump.

Rule reference: OSDG-1 (slice-049; ADR-051; extends slice-010 MCT-1 / slice-007
CAD-1 per-file pattern); slice-033 EOL-DRIFT-1; closes R-13 (slice-096).
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_slice_candidates_skill_md_are_content_equal():
    """In-repo `skills/slice-candidates/SKILL.md` MUST be content-equal
    (EOL-agnostic per slice-033 EOL-DRIFT-1) to installed
    `~/.claude/skills/slice-candidates/SKILL.md` (post-forward-sync).

    Defect class (per slice-006 B1 + slice-007 CAD-1 generalized): if the
    in-repo and installed copies diverge, Claude reads stale prose at
    /slice-candidates invocation -- including a possibly weakened read-only /
    "never read source files" invariant (the ADR-054 bounded `--obo-peek`
    carve-out), the entire safety value of this skill. CRLF/LF artifacts are
    NOT drift (slice-033 EOL-DRIFT-1).

    Rule reference: OSDG-1 (slice-049; ADR-051); slice-007 CAD-1 per-file
    pattern; slice-033 EOL-DRIFT-1; R-13 (slice-096).
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "slice-candidates" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "slice-candidates" / "SKILL.md",
        label="skills/slice-candidates/SKILL.md",
    )
