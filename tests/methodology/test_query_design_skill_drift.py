"""QD-1: content-equality between in-repo `skills/query-design/SKILL.md` and
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
multi-file drift audit.

Per slice-033 EOL-DRIFT-1 (ADR-033): the comparison is content-equal modulo
line endings — CRLF/LF artifacts are NOT drift; only genuine (non-EOL)
divergence FAILs.

Rule reference: QD-1 (slice-032; ADR-032); slice-010 MCT-1 / slice-007
CAD-1 per-file pattern; slice-033 EOL-DRIFT-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tests.skill_drift_equality import assert_md_forward_synced


def test_in_repo_and_installed_query_design_skill_md_are_content_equal():
    """In-repo `skills/query-design/SKILL.md` MUST be content-equal
    (EOL-agnostic per slice-033 EOL-DRIFT-1) to installed
    `~/.claude/skills/query-design/SKILL.md` (post-forward-sync).

    Defect class (per slice-006 B1 + slice-007 CAD-1 generalized): if the
    in-repo and installed copies diverge, Claude reads stale prose at
    /query-design invocation — including a possibly weakened read-only
    invariant, the entire value proposition of this skill. CRLF/LF
    artifacts are NOT drift (slice-033 EOL-DRIFT-1).

    Rule reference: QD-1 (slice-032; ADR-032); slice-007 CAD-1 per-file
    pattern; slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "query-design" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "query-design" / "SKILL.md",
        label="skills/query-design/SKILL.md",
    )
