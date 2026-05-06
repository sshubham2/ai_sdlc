"""Tests for tools.supersede_audit (SUP-1).

Validates that the audit correctly:
- Walks active + archived slices and detects Supersedes / Superseded-by links
- Flags missing-target (link to a slice that doesn't exist)
- Flags one-way-link (active claims supersedes but archived doesn't ack — or vice versa)
- Returns clean when both ends agree
- Returns clean when no supersession links exist
- Pin skill prose for /supersede-slice + SUP-1 reference

Rule reference: SUP-1.
"""
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.supersede_audit import run_audit


def _make_active(root: Path, slice_id: str, supersedes: str | None = None) -> None:
    """Create an active slice folder under architecture/slices/<slice_id>/."""
    folder = root / "architecture" / "slices" / slice_id
    folder.mkdir(parents=True, exist_ok=True)
    text = f"# Slice {slice_id}\n\n**Mode**: Standard\n"
    if supersedes:
        text += f"**Supersedes**: {supersedes}\n"
    (folder / "mission-brief.md").write_text(text, encoding="utf-8")


def _make_archived(root: Path, slice_id: str, superseded_by: str | None = None) -> None:
    """Create an archived slice folder under architecture/slices/archive/<slice_id>/."""
    folder = root / "architecture" / "slices" / "archive" / slice_id
    folder.mkdir(parents=True, exist_ok=True)
    text = f"# Reflection: {slice_id}\n\n## Validated\n\nthings.\n"
    if superseded_by:
        text += (
            f"\n## Supersession\n\n"
            f"**Superseded by**: {superseded_by}\n"
            f"**Date**: 2026-05-06\n"
            f"**Reason**: design contradicted by reality.\n"
        )
    (folder / "reflection.md").write_text(text, encoding="utf-8")


# --- Audit tests ---

def test_no_supersession_links_returns_clean(tmp_path: Path):
    """A project with active + archived slices but no supersession produces zero violations.

    Defect class: An audit that fires on every project regardless of
    whether supersession is in use trains users to ignore it.
    Rule reference: SUP-1.
    """
    _make_active(tmp_path, "slice-001-foo")
    _make_archived(tmp_path, "slice-002-bar")
    result = run_audit(project_root=tmp_path)
    assert result.violations == []
    assert result.links == []


def test_bidirectional_link_passes(tmp_path: Path):
    """Active supersedes archived AND archived ack'd: clean.

    Defect class: The most common case (proper supersession) must
    audit cleanly.
    Rule reference: SUP-1.
    """
    _make_active(tmp_path, "slice-014-async-uploads", supersedes="slice-008-add-receipt-upload")
    _make_archived(tmp_path, "slice-008-add-receipt-upload", superseded_by="slice-014-async-uploads")
    result = run_audit(project_root=tmp_path)
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.links) == 2  # forward + backward


def test_missing_target_flagged(tmp_path: Path):
    """Active claims supersedes a nonexistent slice — flagged.

    Defect class: Typos or stale ids leave dangling supersession claims.
    Rule reference: SUP-1.
    """
    _make_active(tmp_path, "slice-014-async", supersedes="slice-999-doesnt-exist")
    result = run_audit(project_root=tmp_path)
    missing = [v for v in result.violations if v.kind == "missing-target"]
    assert len(missing) == 1


def test_one_way_active_to_archived_flagged(tmp_path: Path):
    """Active claims supersedes archived, but archived hasn't acknowledged.

    Defect class: A claim without acknowledgment lets the archived slice's
    reflection.md continue reading as a live claim.
    Rule reference: SUP-1.
    """
    _make_active(tmp_path, "slice-014-async", supersedes="slice-008-add-receipt-upload")
    _make_archived(tmp_path, "slice-008-add-receipt-upload")  # no superseded_by
    result = run_audit(project_root=tmp_path)
    one_way = [v for v in result.violations if v.kind == "one-way-link"]
    assert len(one_way) == 1


def test_one_way_archived_to_active_flagged(tmp_path: Path):
    """Archived says superseded-by active, but active doesn't claim.

    Defect class: Reverse one-way link is equally bad — the live slice's
    mission-brief.md doesn't acknowledge what it's replacing.
    Rule reference: SUP-1.
    """
    _make_active(tmp_path, "slice-014-async")  # no supersedes
    _make_archived(tmp_path, "slice-008-add-receipt-upload", superseded_by="slice-014-async")
    result = run_audit(project_root=tmp_path)
    one_way = [v for v in result.violations if v.kind == "one-way-link"]
    assert len(one_way) == 1


def test_audit_handles_missing_slices_dir_gracefully(tmp_path: Path):
    """A project with no architecture/slices/ produces no violations.

    Defect class: Crashing on missing input is hostile.
    Rule reference: SUP-1.
    """
    result = run_audit(project_root=tmp_path)
    assert result.violations == []


# --- Skill prose pins ---

def test_supersede_slice_skill_references_sup_1():
    """skills/supersede-slice/SKILL.md must reference SUP-1 + the audit.

    Defect class: Without the skill referencing SUP-1, the rule is
    advisory; without the audit reference, bidirectional consistency
    isn't validated.
    Rule reference: SUP-1.
    """
    text = (REPO_ROOT / "skills" / "supersede-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "SUP-1" in text, "no SUP-1 reference in /supersede-slice SKILL.md"
    assert "supersede_audit" in text, "no supersede_audit module reference"
    assert "**Superseded by**" in text, "Superseded by field format not pinned"
    assert "**Supersedes**" in text, "Supersedes field format not pinned"
