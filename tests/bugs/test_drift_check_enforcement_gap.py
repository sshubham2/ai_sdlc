"""Bug: the /drift-check pre-finish gate is honor-system only — no programmatic enforcement.

Source: user-reported defect (slice candidate ``fix-drift-check-enforcement-gap``),
distilled + confirmed at /slice Step 3c (BFRD-1 bug-fix repro prelude).

Every sibling pipeline discipline is an *audit-enforced* gate: it ships a
``tools/<thing>_audit.py`` whose ``main()`` returns non-zero on violation, and
``skills/build-slice/SKILL.md`` Step 6 invokes that tool so the build HALTs
(BC-1 ``tools/build_checks_audit``, PMI-1 ``tools/plugin_manifest_audit``,
CRP-1 ``tools/critique_review_prerequisite_audit``, PCA-1
``tools/pipeline_chain_audit``, NAW-1 ``tools/new_agent_warning_audit``, …).

``/drift-check`` is the conspicuous exception. CLAUDE.md's vault discipline says
"Run ``/drift-check`` before commit"; the mission-brief template and
``skills/build-slice/SKILL.md`` Step 6 both list it. But:

  * there is NO ``tools/drift_check_audit.py`` (the only drift tool is
    ``tools/critique_agent_drift_audit.py`` — CAD-1, an unrelated
    Critic-agent content-equality check);
  * the pre-commit hook the drift-check skill claims ``/triage`` installs is
    absent (``.git/hooks/`` holds only ``.sample`` files);
  * build-slice Step 6 carries only the honor-system checkbox
    ``- [ ] /drift-check passes (vault and code aligned)``.

So a slice can finish AND commit with the drift-check gate entirely unenforced —
the R-7 / slice-022 "silent-disable" failure class that every other gate was
hardened against.

Expected (the fix contract):
    1. A ``tools/drift_check_audit.py`` module exists and exposes a ``main()``
       entry point (mirroring its audit-tool siblings).
    2. ``skills/build-slice/SKILL.md`` Step 6 (pre-finish gate) invokes that
       audit tool programmatically (a ``tools.drift_check_audit`` invocation),
       so drift-check becomes an audit-enforced HALT gate rather than an
       honor-system checkbox.

Actual (current defect):
    No ``tools/drift_check_audit.py`` exists, and build-slice Step 6 references
    drift-check only as a manual checkbox — no ``tools.drift_check_audit``
    invocation anywhere in the skill.

Fix slice: slice-NNN-fix-drift-check-enforcement-gap (numbered when /slice runs).
Both tests below FAIL today and PASS once the enforcement gate is wired.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _build_slice_step6_text() -> str:
    """Return the build-slice SKILL.md text from the Step 6 heading onward.

    Scoping to Step 6 keeps the wiring assertion honest: the gap is specifically
    that the *pre-finish gate* does not run a drift-check audit, not merely that
    the string ``drift_check`` appears somewhere in the file.
    """
    skill = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^#{2,3}\s+Step 6\b.*$", skill, flags=re.MULTILINE)
    assert m, "Could not locate the Step 6 heading in skills/build-slice/SKILL.md"
    return skill[m.start():]


def test_drift_check_audit_tool_exists():
    """A programmatic drift-check audit tool must exist, like every sibling gate."""
    matches = list((REPO_ROOT / "tools").glob("drift_check*audit*.py"))
    assert matches, (
        "No tools/drift_check_audit.py — /drift-check has no programmatic "
        "enforcement, unlike BC-1/PMI-1/CRP-1/PCA-1/NAW-1. This is the gap."
    )
    mod = importlib.import_module("tools.drift_check_audit")
    assert hasattr(mod, "main"), (
        "tools/drift_check_audit.py must expose a main() entry point so it can "
        "be invoked as an audit-enforced gate (mirrors sibling *_audit tools)."
    )


def test_drift_check_audit_wired_into_build_slice_step6():
    """Build-slice Step 6 must invoke the drift-check audit, not just checkbox it."""
    step6 = _build_slice_step6_text()
    assert re.search(r"tools\.drift_check\w*", step6), (
        "skills/build-slice/SKILL.md Step 6 does not invoke a drift_check audit "
        "tool — the drift-check pre-finish gate is honor-system only (a manual "
        "`- [ ] /drift-check passes` checkbox), so a slice can finish/commit "
        "with drift-check unenforced."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
