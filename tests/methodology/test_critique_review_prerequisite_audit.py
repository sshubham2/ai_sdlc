"""Tests for tools.critique_review_prerequisite_audit (CRP-1).

Validates that the audit correctly:
- Refuses when mode in {STANDARD, HEAVY} + critic-required:true +
  critique-review.md absent + no canonical skip key (the slice-025 gap).
- Accepts when critique-review.md present.
- Accepts a canonical `critique-review-skip:` frontmatter escape-hatch.
- Flags a malformed `critique-review-skip:` value as Important (exit 1).
- Does NOT false-positive on narrative prose mentioning the token (per
  /critique m2 + /critique-review M-add-1 — frontmatter-keyed detection).
- Accepts Minimal mode / not-critic-required (no false-refuse).
- Emits usage-error (exit 2) on missing milestone.md / unresolvable mode.

Rule reference: CRP-1 (methodology-changelog.md v0.40.0); slice-026.
"""
from __future__ import annotations

from pathlib import Path

from tools.critique_review_prerequisite_audit import audit, main


def _make_repo(tmp_path: Path, mode: str = "STANDARD") -> Path:
    """Create a minimal repo root with .git + architecture/triage.md."""
    (tmp_path / ".git").mkdir()
    arch = tmp_path / "architecture"
    arch.mkdir()
    (arch / "triage.md").write_text(
        f"---\ntype: adoption-record\nmode: {mode}\n---\n\n# Triage\n",
        encoding="utf-8",
    )
    return tmp_path


def _make_slice(
    repo: Path,
    *,
    critic_required: bool = True,
    skip_value: str | None = None,
    with_review: bool = False,
    name: str = "slice-026-enforce-critique-review-prerequisite",
) -> Path:
    folder = repo / "architecture" / "slices" / name
    folder.mkdir(parents=True)
    fm = ["---", f"slice: {name}", "stage: critique", f"critic-required: {str(critic_required).lower()}"]
    if skip_value is not None:
        fm.append(f'critique-review-skip: "{skip_value}"')
    fm.append("---")
    body = "\n".join(fm) + "\n\n# Milestone\n\nCurrent focus narrative.\n"
    (folder / "milestone.md").write_text(body, encoding="utf-8")
    (folder / "mission-brief.md").write_text("# brief\n", encoding="utf-8")
    if with_review:
        (folder / "critique-review.md").write_text("# Critique Review\n", encoding="utf-8")
    return folder


def test_refuses_when_standard_mandatory_and_absent(tmp_path: Path):
    """STANDARD + critic-required:true + no critique-review.md + no skip → refuse.

    This is the exact slice-025 gap CRP-1 closes.
    Rule reference: CRP-1; mission-brief AC #1.
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(repo, critic_required=True)
    result = audit(folder, repo_root=repo)
    kinds = [v.kind for v in result.violations]
    assert kinds == ["mandatory-critique-review-absent"], (
        f"expected single mandatory-critique-review-absent violation, got {kinds}"
    )
    assert result.violations[0].severity == "Important"
    # Refuse-path observability: message names which conditions held.
    msg = result.violations[0].message
    assert "mode=STANDARD" in msg and "critic-required=true" in msg
    assert main([str(folder), "--root", str(repo)]) == 1


def test_accepts_documented_skip_frontmatter_canonical_shape(tmp_path: Path):
    """A canonical `critique-review-skip:` frontmatter value → accept (exit 0).

    Rule reference: CRP-1; mission-brief AC #2; ADR-024.
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(
        repo,
        critic_required=True,
        skip_value="skip — rationale: low-tier copy-only follow-up, dual-review not value-add",
    )
    result = audit(folder, repo_root=repo)
    assert result.violations == [], (
        f"unexpected violations: {[(v.kind, v.message) for v in result.violations]}"
    )
    assert result.skip_rationale is not None
    assert "documented skip" in result.accepted_reason
    assert main([str(folder), "--root", str(repo)]) == 0


def test_accepts_when_critique_review_md_present(tmp_path: Path):
    """critique-review.md present → accept (exit 0).

    Rule reference: CRP-1; mission-brief AC #2.
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(repo, critic_required=True, with_review=True)
    result = audit(folder, repo_root=repo)
    assert result.violations == []
    assert result.critique_review_present is True
    assert result.accepted_reason == "critique-review.md present"
    assert main([str(folder), "--root", str(repo)]) == 0


def test_malformed_skip_value_is_important_violation(tmp_path: Path):
    """`critique-review-skip:` key present, value off-canonical → Important, exit 1.

    Mirrors BRANCH-1 malformed-escape-hatch handling — prevents a sloppy
    half-written skip from silently passing.
    Rule reference: CRP-1; mission-brief AC #2; ADR-024.
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(repo, critic_required=True, skip_value="yeah skip it")
    result = audit(folder, repo_root=repo)
    kinds = [v.kind for v in result.violations]
    assert kinds == ["escape-hatch-malformed"], f"got {kinds}"
    assert result.violations[0].severity == "Important"
    assert main([str(folder), "--root", str(repo)]) == 1


def test_narrative_prose_mention_does_not_false_positive(tmp_path: Path):
    """milestone.md BODY prose mentioning the token does NOT trip detection.

    Per /critique m2 + /critique-review M-add-1: detection is keyed on the
    frontmatter KEY, not a body substring scan, so a methodology slice's
    narrative discussing `critique-review-skip` cannot false-positive.
    Rule reference: CRP-1; /critique m2.
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(repo, critic_required=True, with_review=True)
    milestone = folder / "milestone.md"
    milestone.write_text(
        milestone.read_text(encoding="utf-8")
        + "\nThis slice discusses the `critique-review-skip` key and the "
        "value `skip — rationale: ...` extensively in prose.\n",
        encoding="utf-8",
    )
    result = audit(folder, repo_root=repo)
    assert result.violations == [], (
        f"narrative-prose mention false-positived: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )


def test_accepts_minimal_mode_no_false_refuse(tmp_path: Path):
    """Minimal mode → no mandatory /critique-review → accept.

    Rule reference: CRP-1; mission-brief Must-not-defer "no false-refuse".
    """
    repo = _make_repo(tmp_path, mode="MINIMAL")
    folder = _make_slice(repo, critic_required=True)
    result = audit(folder, repo_root=repo)
    assert result.violations == []
    assert "MINIMAL" in result.accepted_reason


def test_accepts_when_not_critic_required(tmp_path: Path):
    """critic-required:false → accept even in STANDARD.

    Rule reference: CRP-1; mission-brief Must-not-defer "no false-refuse".
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = _make_slice(repo, critic_required=False)
    result = audit(folder, repo_root=repo)
    assert result.violations == []
    assert "critic-required is not true" in result.accepted_reason


def test_heavy_mode_enforces(tmp_path: Path):
    """HEAVY mode also enforces (mode in {STANDARD, HEAVY}).

    Rule reference: CRP-1; mission-brief AC #1.
    """
    repo = _make_repo(tmp_path, mode="HEAVY")
    folder = _make_slice(repo, critic_required=True)
    result = audit(folder, repo_root=repo)
    assert [v.kind for v in result.violations] == ["mandatory-critique-review-absent"]


def test_missing_milestone_is_usage_error(tmp_path: Path):
    """No milestone.md → usage-error, exit 2.

    Rule reference: CRP-1 contract (design.md "Usage error").
    """
    repo = _make_repo(tmp_path, mode="STANDARD")
    folder = repo / "architecture" / "slices" / "slice-099-x"
    folder.mkdir(parents=True)
    result = audit(folder, repo_root=repo)
    assert [v.kind for v in result.violations] == ["usage-error"]
    assert main([str(folder), "--root", str(repo)]) == 2


def test_mode_unresolvable_is_usage_error(tmp_path: Path):
    """No triage.md mode + no CLAUDE.md → mode-unresolvable, exit 2.

    Rule reference: CRP-1 contract (design.md "Usage error").
    """
    (tmp_path / ".git").mkdir()
    (tmp_path / "architecture").mkdir()
    folder = tmp_path / "architecture" / "slices" / "slice-026-x"
    folder.mkdir(parents=True)
    (folder / "milestone.md").write_text(
        "---\ncritic-required: true\n---\n# m\n", encoding="utf-8"
    )
    result = audit(folder, repo_root=tmp_path)
    assert [v.kind for v in result.violations] == ["mode-unresolvable"]
    assert main([str(folder), "--root", str(tmp_path)]) == 2


def test_claude_md_mode_fallback(tmp_path: Path):
    """When triage.md lacks mode, CLAUDE.md `**Mode**:` is the fallback.

    Rule reference: CRP-1; design.md mode-resolution.
    """
    (tmp_path / ".git").mkdir()
    arch = tmp_path / "architecture"
    arch.mkdir()
    (arch / "triage.md").write_text("---\ntype: x\n---\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text(
        "# Project\n\n**Mode**: Standard — see triage.md\n", encoding="utf-8"
    )
    folder = arch / "slices" / "slice-026-x"
    folder.mkdir(parents=True)
    (folder / "milestone.md").write_text(
        "---\ncritic-required: true\n---\n# m\n", encoding="utf-8"
    )
    result = audit(folder, repo_root=tmp_path)
    assert result.resolved_mode == "STANDARD"
    assert [v.kind for v in result.violations] == ["mandatory-critique-review-absent"]
