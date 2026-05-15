"""Tests for tools.pipeline_chain_audit (PCA-1).

Validates that the audit correctly:
- Exits 0 when all 8 covered skills carry a well-formed `## Pipeline
  position` block whose successor edges match the canonical loop.
- Exits 1 (`malformed-block`) when a covered skill is missing the block.
- Exits 1 (`successor-mismatch`) on a wrong successor edge.
- Exits 1 (`auto-advance-mismatch`) when the terminal boundary
  (`reflect` / `commit-slice`) is not `auto-advance: false`.
- Exits 2 (`usage-error`) when skills/ is absent.

Synthetic-repo fixtures keep the test independent of the live repo's
prose; the canonical chain is imported from the audit module itself so
the fixtures stay in lockstep with the rule definition.

Rule reference: PCA-1 (methodology-changelog.md v0.41.0); slice-027.
"""
from __future__ import annotations

from pathlib import Path

from tools.pipeline_chain_audit import _CANONICAL_CHAIN, audit, main


def _block(successor: str, auto: bool) -> str:
    return (
        "## Pipeline position\n\n"
        "- **predecessor**: `/x`\n"
        f"- **successor**: `{successor}`\n"
        f"- **auto-advance**: {str(auto).lower()}\n"
        "- **on-clean-completion**: invoke the successor via the Skill tool.\n"
        "- **user-input gates** (halt auto-advance):\n"
        "  - (none on clean path)\n"
    )


def _make_repo(tmp_path: Path, *, omit: str | None = None,
               break_successor: str | None = None,
               break_auto: str | None = None) -> Path:
    """Build a synthetic repo with .git + skills/<8>/SKILL.md.

    omit:            skill name whose `## Pipeline position` block is omitted.
    break_successor: skill name whose successor edge is set wrong.
    break_auto:      skill name whose auto-advance is flipped from canonical.
    """
    (tmp_path / ".git").mkdir()
    skills = tmp_path / "skills"
    for skill, succ, auto in _CANONICAL_CHAIN:
        d = skills / skill
        d.mkdir(parents=True)
        header = f"# /{skill}\n\nbody\n\n## Next step\n\n`{succ}`\n\n"
        if skill == omit:
            (d / "SKILL.md").write_text(header, encoding="utf-8")
            continue
        s = "/wrong-skill" if skill == break_successor else succ
        a = (not auto) if skill == break_auto else auto
        (d / "SKILL.md").write_text(header + _block(s, a), encoding="utf-8")
    return tmp_path


def test_clean_chain_exits_zero(tmp_path: Path):
    """All 8 well-formed blocks matching the canonical loop → clean, exit 0."""
    repo = _make_repo(tmp_path)
    result = audit(repo_root=repo)
    assert not result.violations, [v.to_dict() for v in result.violations]
    assert len(result.skills_checked) == 8
    assert main(["--root", str(repo)]) == 0


def test_missing_block_exits_one(tmp_path: Path):
    """A covered skill missing its `## Pipeline position` block →
    `malformed-block`, exit 1."""
    repo = _make_repo(tmp_path, omit="reflect")
    result = audit(repo_root=repo)
    kinds = {v.kind for v in result.violations}
    assert "malformed-block" in kinds, [v.to_dict() for v in result.violations]
    assert any(v.skill == "reflect" for v in result.violations)
    assert main(["--root", str(repo)]) == 1


def test_successor_mismatch_exits_one(tmp_path: Path):
    """A wrong successor edge → `successor-mismatch`, exit 1."""
    repo = _make_repo(tmp_path, break_successor="design-slice")
    result = audit(repo_root=repo)
    assert any(
        v.kind == "successor-mismatch" and v.skill == "design-slice"
        for v in result.violations
    ), [v.to_dict() for v in result.violations]
    assert main(["--root", str(repo)]) == 1


def test_terminal_auto_advance_mismatch_exits_one(tmp_path: Path):
    """Flipping `commit-slice` to auto-advance:true → `auto-advance-mismatch`,
    exit 1 (the /commit-slice-never-auto-invoked terminal guarantee)."""
    repo = _make_repo(tmp_path, break_auto="commit-slice")
    result = audit(repo_root=repo)
    assert any(
        v.kind == "auto-advance-mismatch" and v.skill == "commit-slice"
        for v in result.violations
    ), [v.to_dict() for v in result.violations]
    assert main(["--root", str(repo)]) == 1


def test_missing_skills_dir_exits_two(tmp_path: Path):
    """No skills/ directory → usage-error, exit 2."""
    (tmp_path / ".git").mkdir()
    result = audit(repo_root=tmp_path)
    assert any(v.kind == "usage-error" for v in result.violations)
    assert main(["--root", str(tmp_path)]) == 2
