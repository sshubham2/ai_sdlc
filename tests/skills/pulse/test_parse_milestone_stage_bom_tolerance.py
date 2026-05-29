"""Pin slice-079 Fix M+N (slice-077 m8+m9): milestone.md parse tolerance + stage exact-key match.

Slice-077 m8: `_parse_milestone_stage` did not tolerate UTF-8 BOM (PowerShell-saved files start with `﻿`),
silently returning None/unknown instead of parsing the stage.
Slice-077 m9: `stripped.startswith("stage:")` would also match hypothetical `stage_owner:` / `stage-history:`.
Fix M tolerates BOM. Fix N uses exact-key match `stripped.split(":", 1)[0].strip() == "stage"`.

Note: `_parse_milestone_stage` takes a `Path` (reads via `.read_text(encoding="utf-8")`).
Tests use tmp_path to write synthetic milestone.md files.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.pulse_worktree_resolver import _parse_milestone_stage


def _write_milestone(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "milestone.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_milestone_with_utf8_bom_parses_stage_correctly(tmp_path: Path) -> None:
    """Fix M: BOM-prefixed milestone.md (PowerShell convention) still parses stage from frontmatter."""
    milestone_path = _write_milestone(
        tmp_path,
        "﻿---\n"
        "slice: slice-NNN-foo\n"
        "stage: build\n"
        "updated: 2026-05-29\n"
        "next-action: run /validate-slice\n"
        "---\n\n"
        "# Milestone\n",
    )
    stage = _parse_milestone_stage(milestone_path)
    assert stage == "build", (
        f"Fix M regression: BOM-prefixed milestone returned stage={stage!r}; expected 'build'. "
        f"PowerShell-saved milestone.md silently returns None/unknown."
    )


def test_milestone_without_bom_still_parses_stage_correctly(tmp_path: Path) -> None:
    """Fix M: non-BOM milestone (canonical case) unaffected — sanity backstop."""
    milestone_path = _write_milestone(
        tmp_path,
        "---\n"
        "slice: slice-NNN-foo\n"
        "stage: design\n"
        "---\n",
    )
    stage = _parse_milestone_stage(milestone_path)
    assert stage == "design", f"Sanity regression: non-BOM milestone returned {stage!r}"


def test_stage_exact_key_does_not_match_stage_owner_prefix(tmp_path: Path) -> None:
    """Fix N: `stage_owner:` MUST NOT match the `stage:` lookup (exact-key match, not prefix).

    Pre-fix: `stripped.startswith("stage:")` would match `stage_owner:` and return its value.
    Post-fix: exact split-and-compare returns no match for non-stage keys.
    """
    milestone_path = _write_milestone(
        tmp_path,
        "---\n"
        "slice: slice-NNN-foo\n"
        "stage_owner: alice\n"
        "---\n",
    )
    stage = _parse_milestone_stage(milestone_path)
    assert stage in (None, "", "unknown"), (
        f"Fix N regression: `stage_owner:` matched the stage lookup, returned {stage!r}. "
        f"Pre-fix `.startswith('stage:')` permits this collision."
    )


def test_stage_exact_key_does_not_match_stage_history_prefix(tmp_path: Path) -> None:
    """Fix N: hypothetical `stage-history:` key MUST NOT match the `stage:` lookup."""
    milestone_path = _write_milestone(
        tmp_path,
        "---\n"
        "slice: slice-NNN-foo\n"
        "stage-history: [build, validate]\n"
        "---\n",
    )
    stage = _parse_milestone_stage(milestone_path)
    assert stage in (None, "", "unknown"), (
        f"Fix N regression: `stage-history:` matched the stage lookup, returned {stage!r}"
    )
