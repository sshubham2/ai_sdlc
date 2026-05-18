"""STP-1 R-10-reconstruction regression (slice-044; ADR-047).

Reconstructs the **exact R-10 scenario** (slice-038 SRSC-1 repointed
`/validate-slice` Step 5.5 prose, leaving `test_step4_5_5_consumes_machine
_stable_command` asserting a since-removed anchor — FAILing slice-innocently
on master for ~5 slices until slice-039's BC-PROJ-4 run surfaced it): a
`test_*skill*.py` prose-pin asserting a constant literal that the target
SKILL.md no longer contains.

Genuine-contrast discipline (slice-043): the SAME fixture is exercised in
two states — the *repointed* state (anchor removed → STP-1 MUST flag) and
the *aligned* state (anchor present → STP-1 MUST be clean). The FAIL→PASS
transition on identical assertions is the non-tautology proof; before
`tools/state_transition_pin_audit.py` existed this module could not import
and FAILed at collection (build-log 2026-05-18 — written before the tool,
captured FAIL, now PASSES).

m-add (DR-1 round-1): the repro asserts the exit-1 **signature** —
`kind == "stale-skill-prose-pin"` AND the named folded literal — NOT merely
`exit != 0`, so a coverage hole that exited 1 for the wrong reason could
not let this repro spuriously "pass".

Shippability-catalogued (row #42) so this critical path can never silently
regress (RPCD-1 / slice-040 lesson).
"""
from __future__ import annotations

import textwrap
from pathlib import Path

from tools.state_transition_pin_audit import audit, main

# The slice-038/R-10 anchor shape: a multi-segment prose anchor a SKILL.md
# repoint would delete. Asserted as an implicitly-concatenated literal (B3)
# to also exercise folded-constant extraction.
_R10_ANCHOR = "Run each entry's **Machine-cmd** column through the canonical pinned runner"

_SKILL_REPOINTED = "# Validate Slice\n\n## Step 5.5\n\nInvoke `$PY -m tools.shippability_runner architecture/shippability.md` (SRSC-1).\n"
_SKILL_ALIGNED = f"# Validate Slice\n\n## Step 5.5\n\n{_R10_ANCHOR} — legacy wording.\n"

_PIN_FILE = '''
    from tests.methodology.conftest import read_file

    VALIDATE = read_file("skills/validate-slice/SKILL.md")


    def test_step4_5_5_consumes_machine_stable_command():
        # slice-031 SCMD-1 B2-v1 mini-CAD prose-pin (the R-10 victim).
        assert (
            "Run each entry's **Machine-cmd** column "
            "through the canonical pinned runner"
        ) in VALIDATE
'''


def _build(tmp_path: Path, skill_md: str) -> Path:
    (tmp_path / "skills" / "validate-slice").mkdir(parents=True)
    (tmp_path / "skills" / "validate-slice" / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (tmp_path / "architecture").mkdir()
    (tmp_path / "architecture" / "risk-register.md").write_text(
        "# Risk Register\n\n## R-1 — x\n\n**Likelihood**: low\n**Impact**: low\n**Status**: open\n",
        encoding="utf-8",
    )
    tdir = tmp_path / "tests" / "methodology"
    tdir.mkdir(parents=True)
    (tdir / "test_validate_slice_skill.py").write_text(
        textwrap.dedent(_PIN_FILE), encoding="utf-8"
    )
    return tmp_path


def test_r10_repointed_state_is_flagged_with_signature(tmp_path: Path) -> None:
    """R-10 reproduced: SKILL.md repointed (anchor removed) while the
    slice-031 prose-pin still asserts it → STP-1 Sub-form A flags it with
    the exit-1 signature (kind + named folded literal), exit 1."""
    root = _build(tmp_path, _SKILL_REPOINTED)
    res = audit(root=root)
    important = [v for v in res.violations if v.severity == "Important"]
    assert [v.kind for v in important] == ["stale-skill-prose-pin"], (
        [f"{v.kind}: {v.message}" for v in important]
    )
    # m-add: assert the SIGNATURE, not merely exit != 0.
    msg = important[0].message
    assert "test_validate_slice_skill.py::test_step4_5_5_consumes_machine_stable_command" in msg
    assert _R10_ANCHOR in msg, "the FULL folded literal must be named (B3 / m-add)"
    assert "skills/validate-slice/SKILL.md" in msg
    assert main(["--root", str(root)]) == 1


def test_r10_aligned_state_is_clean(tmp_path: Path) -> None:
    """Genuine-contrast (slice-043): identical pin, SKILL.md ALIGNED (anchor
    present) → STP-1 clean, exit 0. The FAIL→PASS transition on the same
    assertion proves the row #42 pin is non-tautological."""
    root = _build(tmp_path, _SKILL_ALIGNED)
    res = audit(root=root)
    assert [v for v in res.violations if v.severity == "Important"] == []
    assert main(["--root", str(root)]) == 0
