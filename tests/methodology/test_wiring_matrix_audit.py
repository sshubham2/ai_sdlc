"""Tests for tools.wiring_matrix_audit (WIRE-1).

Validates that the wiring matrix audit correctly:
- Accepts clean designs (cells filled OR exemption-with-rationale)
- Flags rows with empty cells and no exemption (missing-cells)
- Flags exemptions without 'rationale:' (missing-rationale)
- Flags missing matrix heading (no-matrix)
- Accepts empty matrices (zero data rows = slice has no new modules)
- Honors NFR-1 carry-over exemption (mtime check on mission-brief.md)

Rule reference: WIRE-1.
"""
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.wiring_matrix_audit import (
    _WIRE_1_RELEASE_DATE,
    WireViolation,
    audit_design_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "wiring"


def test_clean_design_has_no_violations():
    """A wiring matrix with all cells filled (or exemption + rationale) passes.

    Defect class: A linter that flags valid patterns (single mock at boundary,
    or properly-rationalized exemption) trains users to ignore it.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(FIXTURES / "clean_design.md")
    assert violations == [], (
        f"clean design had unexpected violations: "
        f"{[(v.kind, v.message) for v in violations]}"
    )


def test_missing_consumer_cells_flags_missing_cells():
    """Row with empty entry_point/consumer_test and no exemption is flagged.

    Defect class: A row claiming a new module exists but with no consumer
    means the module is structurally dead. WIRE-1 catches this at design-time.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(FIXTURES / "missing_cells_design.md")
    missing = [v for v in violations if v.kind == "missing-cells"]
    assert len(missing) >= 1, (
        f"expected missing-cells violation; got "
        f"{[(v.kind, v.message) for v in violations]}"
    )
    # Verify the flagged row is the one with the orphan
    assert any("orphan" in v.message for v in missing), (
        "expected the violation to name the orphan module"
    )


def test_missing_rationale_flags_missing_rationale():
    """Exemption present but no 'rationale:' marker is flagged.

    Defect class: An exemption without rationale defeats WIRE-1's intent.
    A bare 'internal helper' note doesn't tell future readers WHY this
    module has no consumer; the rationale is what makes the exemption
    auditable.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(FIXTURES / "missing_rationale_design.md")
    rationale = [v for v in violations if v.kind == "missing-rationale"]
    assert len(rationale) == 1, (
        f"expected exactly 1 missing-rationale; got {len(rationale)}: "
        f"{[v.message for v in violations]}"
    )


def test_no_matrix_heading_emits_no_matrix_violation():
    """Design.md without `## Wiring matrix` heading fails.

    Defect class: A slice that ships without the matrix entirely is the
    worst case — no audit possible. The no-matrix finding forces the
    matrix to exist before /build-slice proceeds.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(FIXTURES / "no_matrix_design.md")
    assert any(v.kind == "no-matrix" for v in violations), (
        f"expected no-matrix finding; got {[v.kind for v in violations]}"
    )


def test_empty_matrix_is_acceptable():
    """Header + separator only (zero data rows) is clean.

    Defect class: A slice may introduce no new modules (e.g., config-only,
    refactor of existing files). Forcing a placeholder row would be
    bureaucratic noise. Empty matrices are accepted as a deliberate signal.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(FIXTURES / "empty_matrix_design.md")
    assert violations == [], (
        f"empty matrix should be clean; got {[v.message for v in violations]}"
    )


def test_audit_handles_missing_design_md_gracefully():
    """Missing design.md emits a no-matrix finding, not a crash.

    Defect class: A linter that crashes on a missing input is hostile;
    graceful 'file not found' surfaces the issue without halting other lint.
    Rule reference: WIRE-1.
    """
    violations = audit_design_file(REPO_ROOT / "does-not-exist-xyz-wire.md")
    assert any(v.kind == "no-matrix" for v in violations)


def _set_brief_mtime(brief: Path, target_date) -> None:
    """Set mission-brief.md mtime to noon on the given date."""
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    target_ts = target_dt.timestamp()
    os.utime(brief, (target_ts, target_ts))


def test_carry_over_exempts_old_slices(tmp_path: Path):
    """Slices with mission-brief.md mtime before WIRE-1 are exempt.

    Defect class: Retroactively applying WIRE-1 to slices authored before
    the rule existed would break every old design.md. NFR-1 carry-over via
    mtime check exempts pre-rule slices automatically.
    Rule reference: WIRE-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()

    brief = slice_folder / "mission-brief.md"
    brief.write_text("# Old slice", encoding="utf-8")
    # ~30 days before release
    _set_brief_mtime(brief, _WIRE_1_RELEASE_DATE - timedelta(days=30))

    # design.md that would normally fail (empty cells, no exemption)
    design = slice_folder / "design.md"
    design.write_text(
        "## Wiring matrix\n\n"
        "| New module | Consumer entry point | Consumer test | Exemption |\n"
        "|------------|---------------------|---------------|-----------|\n"
        "| `src/foo.py` | — | — | — |\n",
        encoding="utf-8",
    )

    violations = audit_design_file(design)
    assert violations == [], (
        f"carry-over should suppress violations on pre-WIRE-1 slices; "
        f"got {[(v.kind, v.message) for v in violations]}"
    )


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices (testing/CI mode).

    Defect class: Without an override, the carry-over exemption is too sticky;
    CI runs that want to audit the entire archive need a way to disable it.
    Rule reference: WIRE-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()

    brief = slice_folder / "mission-brief.md"
    brief.write_text("# Old slice", encoding="utf-8")
    _set_brief_mtime(brief, _WIRE_1_RELEASE_DATE - timedelta(days=30))

    design = slice_folder / "design.md"
    design.write_text(
        "## Wiring matrix\n\n"
        "| New module | Consumer entry point | Consumer test | Exemption |\n"
        "|------------|---------------------|---------------|-----------|\n"
        "| `src/foo.py` | — | — | — |\n",
        encoding="utf-8",
    )

    violations = audit_design_file(design, skip_if_carry_over=False)
    assert any(v.kind == "missing-cells" for v in violations), (
        "expected missing-cells violation when carry-over is disabled"
    )


def test_carry_over_does_not_apply_when_brief_missing(tmp_path: Path):
    """If mission-brief.md doesn't exist, no carry-over claim — audit applies.

    Defect class: Bypassing the audit by deleting mission-brief.md would be
    a trivial dodge. A missing brief means no carry-over claim.
    Rule reference: WIRE-1.
    """
    slice_folder = tmp_path / "slice-001-no-brief"
    slice_folder.mkdir()
    # No mission-brief.md created

    design = slice_folder / "design.md"
    design.write_text(
        "## Wiring matrix\n\n"
        "| New module | Consumer entry point | Consumer test | Exemption |\n"
        "|------------|---------------------|---------------|-----------|\n"
        "| `src/foo.py` | — | — | — |\n",
        encoding="utf-8",
    )

    violations = audit_design_file(design)
    assert any(v.kind == "missing-cells" for v in violations), (
        "audit should apply when mission-brief.md is absent (no carry-over claim)"
    )


def test_design_slice_skill_references_wire_1():
    """skills/design-slice/SKILL.md must reference WIRE-1.

    Defect class: A rule the skill prose doesn't reference is invisible to
    executors writing design.md — the wiring matrix becomes optional in
    practice.
    Rule reference: WIRE-1.
    """
    text = (REPO_ROOT / "skills" / "design-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "WIRE-1" in text, "no WIRE-1 reference in /design-slice SKILL.md"
    assert "Wiring matrix" in text


def test_build_slice_skill_references_wire_1():
    """skills/build-slice/SKILL.md must reference WIRE-1 in the pre-finish gate.

    Defect class: Without the pre-finish gate referencing WIRE-1 + the audit
    tool name, the rule is advisory. The skill prose must name both.
    Rule reference: WIRE-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "WIRE-1" in text, "no WIRE-1 reference in /build-slice SKILL.md"
    assert "wiring_matrix_audit" in text, (
        "no wiring_matrix_audit module reference in /build-slice"
    )
