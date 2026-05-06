"""Tests for tools.cross_spec_parity_audit (CSP-1).

Validates that the audit correctly:
- Detects Heavy mode via architecture/triage.md
- Returns clean (no-op) in Minimal / Standard modes
- Parses H2-structured items with prefix TM / REQ / NFR
- Validates Status field per artifact-type vocabulary
- Validates Implementation (TM/REQ) and Verification (NFR) refs point
  to real files when status requires it (mitigated/implemented/met)
- Allows empty Implementation when status is accepted/open/pending/etc.
- Honors --skip-heavy-check for archive scans / CI

Plus skill prose pins for /sync + /drift-check.

Rule reference: CSP-1.
"""
import shutil
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.cross_spec_parity_audit import (
    _detect_heavy_mode,
    _normalize_id,
    run_audit,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "cross_spec_parity"


def _make_project(tmp_path: Path, mode: str = "Heavy") -> Path:
    """Create a tmp project root with architecture/triage.md declaring mode."""
    root = tmp_path / "project"
    (root / "architecture").mkdir(parents=True)
    (root / "architecture" / "triage.md").write_text(
        f"# Triage\n\n**Mode**: {mode}\n", encoding="utf-8"
    )
    return root


def _seed_real_files(root: Path) -> None:
    """Create the source files referenced by the clean fixtures."""
    (root / "src" / "middleware").mkdir(parents=True, exist_ok=True)
    (root / "src" / "middleware" / "auth.py").write_text(
        "def require_auth():\n    pass\n", encoding="utf-8"
    )
    (root / "src" / "api").mkdir(parents=True, exist_ok=True)
    (root / "src" / "api" / "receipts.py").write_text(
        "def upload_receipt():\n    pass\n", encoding="utf-8"
    )
    (root / "tests" / "load").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "load" / "upload_p99.py").write_text(
        "# load test\n", encoding="utf-8"
    )
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "tests" / "test_receipt_upload.py").write_text(
        "def test_upload_persists():\n    pass\n", encoding="utf-8"
    )


# --- Unit tests for helpers ---

def test_detect_heavy_mode_recognizes_mode_field(tmp_path: Path):
    """`**Mode**: Heavy` in triage.md is detected.

    Defect class: A detector that misses the standard frontmatter shape
    would silently treat Heavy projects as Standard, skipping the audit.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    assert _detect_heavy_mode(root) is True


def test_detect_heavy_mode_returns_false_for_standard(tmp_path: Path):
    """Mode: Standard is not Heavy.

    Defect class: False positive on Standard would force every project
    to maintain Heavy artifacts when they don't have any.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Standard")
    assert _detect_heavy_mode(root) is False


def test_detect_heavy_mode_handles_missing_triage(tmp_path: Path):
    """Missing triage.md returns False (cannot be Heavy without explicit declaration).

    Defect class: Crashing on missing input is hostile.
    Rule reference: CSP-1.
    """
    root = tmp_path / "no-triage"
    root.mkdir()
    assert _detect_heavy_mode(root) is False


def test_normalize_id_handles_variants():
    """TM-01, TM01, tm-1 all normalize to TM-1.

    Defect class: Inconsistent ID forms in artifacts could mismatch
    cross-references downstream.
    Rule reference: CSP-1.
    """
    assert _normalize_id("TM-1") == "TM-1"
    assert _normalize_id("TM-01") == "TM-1"
    assert _normalize_id("tm-1") == "TM-1"
    assert _normalize_id("REQ7") == "REQ-7"


# --- Heavy-mode gating ---

def test_non_heavy_mode_returns_clean_no_op(tmp_path: Path):
    """A Standard-mode project produces no items and no violations.

    Defect class: Running the audit on Minimal / Standard projects would
    flag missing artifacts that don't apply.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Standard")
    result = run_audit(project_root=root)
    assert result.heavy_mode is False
    assert result.items == []
    assert result.violations == []


def test_skip_heavy_check_forces_run(tmp_path: Path):
    """--skip-heavy-check audits even without Heavy mode declaration.

    Defect class: Without override, archive scans / CI can't audit
    pre-Heavy or non-Heavy projects.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Standard")
    result = run_audit(project_root=root, skip_heavy_check=True)
    assert result.heavy_mode is True
    # Still clean because no artifacts exist
    assert result.violations == []


# --- Clean artifact parsing ---

def test_clean_artifacts_parse_with_no_violations(tmp_path: Path):
    """All three artifacts (TM/REQ/NFR) with valid refs parse clean.

    Defect class: A parser that flags well-formed artifacts trains
    users to ignore the audit.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "clean_threat_model.md", root / "architecture" / "threat-model.md")
    shutil.copy(FIXTURES / "clean_requirements.md", root / "architecture" / "requirements.md")
    shutil.copy(FIXTURES / "clean_nfrs.md", root / "architecture" / "nfrs.md")

    result = run_audit(project_root=root)
    assert result.heavy_mode is True
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    # Expected counts: 3 TM items + 2 REQ items + 2 NFR items
    by_prefix = {p: sum(1 for i in result.items if i.prefix == p) for p in ("TM", "REQ", "NFR")}
    assert by_prefix == {"TM": 3, "REQ": 2, "NFR": 2}


def test_accepted_threat_with_empty_implementation_passes(tmp_path: Path):
    """A threat with status=accepted is allowed to have empty Implementation.

    Defect class: Forcing every threat to have a code path would force
    fake mitigations or block accepted-risk patterns (deliberate
    non-mitigation with rationale).
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "clean_threat_model.md", root / "architecture" / "threat-model.md")
    result = run_audit(project_root=root)
    accepted = [i for i in result.items if i.status == "accepted"]
    assert len(accepted) == 1
    assert accepted[0].item_id == "TM-2"


# --- Violation detection ---

def test_broken_implementation_path_flagged(tmp_path: Path):
    """`Implementation: src/.../nonexistent.py` is flagged broken-ref.

    Defect class: A claimed mitigation pointing nowhere is the core
    failure mode CSP-1 catches.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "broken_impl_threat.md", root / "architecture" / "threat-model.md")
    result = run_audit(project_root=root)
    broken = [v for v in result.violations if v.kind == "broken-ref"]
    assert len(broken) == 1
    assert "TM-1" in broken[0].message or broken[0].item_id == "TM-1"


def test_missing_status_field_flagged(tmp_path: Path):
    """An item without a Status field is flagged.

    Defect class: Status drives the audit's required-path check;
    missing status defeats the discipline.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "missing_status_threat.md", root / "architecture" / "threat-model.md")
    result = run_audit(project_root=root)
    missing = [v for v in result.violations if v.kind == "missing-field"]
    assert len(missing) == 1


def test_invalid_status_for_artifact_flagged(tmp_path: Path):
    """Status outside the artifact's vocabulary is flagged.

    Defect class: An open status vocabulary lets the discipline rot.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "invalid_status_threat.md", root / "architecture" / "threat-model.md")
    result = run_audit(project_root=root)
    invalid = [v for v in result.violations if v.kind == "invalid-status"]
    assert len(invalid) == 1


def test_mitigated_with_empty_impl_flagged(tmp_path: Path):
    """status=mitigated with empty Implementation is flagged missing-ref.

    Defect class: The whole point of CSP-1 is that mitigated threats
    must reference real code. Empty Implementation under mitigated is
    decoration, not mitigation.
    Rule reference: CSP-1.
    """
    root = _make_project(tmp_path, mode="Heavy")
    _seed_real_files(root)
    shutil.copy(FIXTURES / "mitigated_no_impl_threat.md", root / "architecture" / "threat-model.md")
    result = run_audit(project_root=root)
    missing_ref = [v for v in result.violations if v.kind == "missing-ref"]
    assert len(missing_ref) == 1


# --- Skill prose pins ---

def test_sync_skill_references_csp_1():
    """skills/sync/SKILL.md must reference CSP-1 + the audit module.

    Defect class: Without /sync running the audit, Heavy artifacts
    decay between syncs.
    Rule reference: CSP-1.
    """
    text = (REPO_ROOT / "skills" / "sync" / "SKILL.md").read_text(encoding="utf-8")
    assert "CSP-1" in text, "no CSP-1 reference in /sync SKILL.md"
    assert "cross_spec_parity_audit" in text, (
        "no cross_spec_parity_audit module reference"
    )


def test_drift_check_mentions_csp_1():
    """skills/drift-check/SKILL.md mentions CSP-1 as the Heavy-mode complement.

    Defect class: Without cross-references between /drift-check and
    /sync's CSP-1, users in Heavy mode may run only one of the two.
    Rule reference: CSP-1.
    """
    text = (REPO_ROOT / "skills" / "drift-check" / "SKILL.md").read_text(encoding="utf-8")
    assert "CSP-1" in text, "no CSP-1 reference in /drift-check"
