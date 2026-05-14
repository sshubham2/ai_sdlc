"""Mini-CAD bidirectional byte-equality tests for /diagnose skill files (slice-019).

Per slice-019 AC #1 + B3 TF-1 row split (Path A: single-file convention
per slice-007 CAD-1 + slice-010 mini-CAD precedent): each file under
bidirectional byte-equality discipline gets its own test function.

Files under mini-CAD-for-/diagnose:
- skills/diagnose/SKILL.md (top-level skill orchestration prose)
- skills/diagnose/passes/03f-layering.md (the LAYER-EVID-1 carrier)

Both must be byte-equal between the in-repo source and the installed
copy at ~/.claude/skills/diagnose/. Drift between them means a
forward-sync was forgotten after an in-repo edit, which silently
breaks the LAYER-EVID-1 rule at /diagnose runtime (subagent reads the
installed copy).

Rule reference: slice-019 AC #1 (mini-CAD for /diagnose); slice-007
CAD-1 introduction; slice-010 mini-CAD for slice/SKILL.md.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
INSTALLED_DIAGNOSE_DIR = Path.home() / ".claude" / "skills" / "diagnose"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_in_repo_and_installed_diagnose_skill_md_are_content_equal():
    """skills/diagnose/SKILL.md MUST be byte-equal between in-repo and
    installed copy.

    Defect class: in-repo edit (e.g., adding the LAYER-EVID-1 Step 5
    cross-reference paragraph) without forward-sync to ~/.claude/skills/
    diagnose/SKILL.md means /diagnose runtime reads stale prose; subagent
    never sees the rule.

    Rule reference: slice-019 AC #1 (mini-CAD); slice-007 CAD-1 pattern.
    """
    in_repo = REPO_ROOT / "skills" / "diagnose" / "SKILL.md"
    installed = INSTALLED_DIAGNOSE_DIR / "SKILL.md"

    assert in_repo.exists(), f"in-repo SKILL.md missing at {in_repo}"
    assert installed.exists(), (
        f"installed SKILL.md missing at {installed} — install_audit + mini-CAD "
        "expect this to be a forward-synced copy of the in-repo source"
    )

    in_repo_hash = _sha256(in_repo)
    installed_hash = _sha256(installed)
    assert in_repo_hash == installed_hash, (
        f"skills/diagnose/SKILL.md DRIFT: in-repo sha256={in_repo_hash[:16]}... "
        f"installed sha256={installed_hash[:16]}... — forward-sync after the "
        f"latest in-repo edit was forgotten. /diagnose runtime would read stale "
        f"prose. Fix: `cp skills/diagnose/SKILL.md ~/.claude/skills/diagnose/SKILL.md`."
    )


def test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal():
    """skills/diagnose/passes/03f-layering.md MUST be byte-equal between
    in-repo and installed copy.

    Defect class: in-repo edit to the LAYER-EVID-1 rule body (Method step 4
    + Severity rubric + Anti-patterns) without forward-sync means the
    03f-layering subagent at /diagnose runtime reads stale prose and
    doesn't apply the rule — F-LAYER-bca9c001-class false-positives
    return silently.

    Rule reference: slice-019 AC #1 (mini-CAD for /diagnose, second file).
    """
    in_repo = REPO_ROOT / "skills" / "diagnose" / "passes" / "03f-layering.md"
    installed = INSTALLED_DIAGNOSE_DIR / "passes" / "03f-layering.md"

    assert in_repo.exists(), f"in-repo 03f-layering.md missing at {in_repo}"
    assert installed.exists(), (
        f"installed 03f-layering.md missing at {installed} — install_audit + "
        "mini-CAD expect this to be a forward-synced copy of the in-repo source"
    )

    in_repo_hash = _sha256(in_repo)
    installed_hash = _sha256(installed)
    assert in_repo_hash == installed_hash, (
        f"skills/diagnose/passes/03f-layering.md DRIFT: in-repo "
        f"sha256={in_repo_hash[:16]}... installed sha256={installed_hash[:16]}... "
        f"— forward-sync after the latest in-repo edit was forgotten. "
        f"/diagnose 03f-layering subagent at runtime would read stale prose "
        f"(LAYER-EVID-1 rule body). Fix: "
        f"`cp skills/diagnose/passes/03f-layering.md ~/.claude/skills/diagnose/passes/03f-layering.md`."
    )
