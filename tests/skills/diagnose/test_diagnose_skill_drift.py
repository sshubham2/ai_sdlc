"""Mini-CAD bidirectional content-equality tests for /diagnose skill files (slice-019).

Per slice-019 AC #1 + B3 TF-1 row split (Path A: single-file convention
per slice-007 CAD-1 + slice-010 mini-CAD precedent): each file under
bidirectional content-equality discipline gets its own test function.

Files under mini-CAD-for-/diagnose:
- skills/diagnose/SKILL.md (top-level skill orchestration prose)
- skills/diagnose/passes/03f-layering.md (the LAYER-EVID-1 carrier)

Both must be content-equal (EOL-agnostic per ADR-033 / EOL-DRIFT-1,
slice-033) between the in-repo source and the installed copy at
~/.claude/skills/diagnose/. Drift between them means a forward-sync was
forgotten after an in-repo edit, which silently breaks the LAYER-EVID-1
rule at /diagnose runtime (subagent reads the installed copy).

Rule reference: slice-019 AC #1 (mini-CAD for /diagnose); slice-007
CAD-1 introduction; slice-010 mini-CAD for slice/SKILL.md; slice-033
EOL-DRIFT-1 (comparison is now content-equal modulo line endings).
"""
from __future__ import annotations

from pathlib import Path

from tests.skill_drift_equality import assert_md_forward_synced

REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALLED_DIAGNOSE_DIR = Path.home() / ".claude" / "skills" / "diagnose"


def test_in_repo_and_installed_diagnose_skill_md_are_content_equal():
    """skills/diagnose/SKILL.md MUST be content-equal (EOL-agnostic) between
    in-repo and installed copy.

    Defect class: in-repo edit (e.g., adding the LAYER-EVID-1 Step 5
    cross-reference paragraph) without forward-sync to ~/.claude/skills/
    diagnose/SKILL.md means /diagnose runtime reads stale prose; subagent
    never sees the rule. CRLF/LF artifacts are NOT drift (EOL-DRIFT-1).

    Rule reference: slice-019 AC #1 (mini-CAD); slice-007 CAD-1 pattern;
    slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "diagnose" / "SKILL.md",
        INSTALLED_DIAGNOSE_DIR / "SKILL.md",
        label="skills/diagnose/SKILL.md",
    )


def test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal():
    """skills/diagnose/passes/03f-layering.md MUST be content-equal
    (EOL-agnostic) between in-repo and installed copy.

    Defect class: in-repo edit to the LAYER-EVID-1 rule body (Method step 4
    + Severity rubric + Anti-patterns) without forward-sync means the
    03f-layering subagent at /diagnose runtime reads stale prose and
    doesn't apply the rule — F-LAYER-bca9c001-class false-positives
    return silently. CRLF/LF artifacts are NOT drift (EOL-DRIFT-1).

    Rule reference: slice-019 AC #1 (mini-CAD for /diagnose, second file);
    slice-033 EOL-DRIFT-1.
    """
    assert_md_forward_synced(
        REPO_ROOT / "skills" / "diagnose" / "passes" / "03f-layering.md",
        INSTALLED_DIAGNOSE_DIR / "passes" / "03f-layering.md",
        label="skills/diagnose/passes/03f-layering.md",
    )
