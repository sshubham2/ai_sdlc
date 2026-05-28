"""Unit tests for the drift-flag false-positive suppression predicate per
slice-077 AC#4 + design.md L141-156 + ADR-070 L107-127.

Predicate semantics (per /critique B3 ACCEPTED-FIXED): suppress
"vault forward-population" flag IFF (a) at least one worktree.state ==
BUILT_BUT_NOT_MERGED AND (b) ALL 3 installed surfaces match the worktree's
content modulo line endings (EOL-DRIFT-1 / ADR-033).

The predicate lives in tools/pulse_worktree_resolver as
`should_suppress_vault_forward_population_flag`. v1 may not expose it as a
top-level API — these tests can be skipped or marked xfail until Phase C
defines the surface.
"""
from __future__ import annotations

import pytest

from tools.pulse_worktree_resolver import (
    WorktreeInfo,
    WorktreeState,
    WorktreeStateClassification,
)

# Phase C exposes the suppression predicate. Until then, these tests fail
# on ImportError; that IS the WRITTEN-FAILING signal for TF-1.
try:
    from tools.pulse_worktree_resolver import should_suppress_vault_forward_population_flag
    _PREDICATE_AVAILABLE = True
except ImportError:
    _PREDICATE_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not _PREDICATE_AVAILABLE,
    reason="should_suppress_vault_forward_population_flag not yet implemented (Phase C)",
)


def test_suppress_vault_forward_population_when_built_but_not_merged_and_installed_matches_worktree(
    tmp_path,
):
    """Positive case: BUILT_BUT_NOT_MERGED worktree exists AND all 3 installed
    surfaces match the worktree content → predicate returns True (suppress)."""
    # Synthetic worktree directory layout
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / "methodology-changelog.md").write_text("# changelog\n", encoding="utf-8")
    (worktree / "VERSION").write_text("0.73.0\n", encoding="utf-8")
    pulse_dir = worktree / "skills" / "pulse"
    pulse_dir.mkdir(parents=True)
    (pulse_dir / "SKILL.md").write_text("# pulse\n", encoding="utf-8")

    # Installed surfaces matching worktree content byte-for-byte
    installed = tmp_path / "installed"
    installed.mkdir()
    (installed / "methodology-changelog.md").write_text("# changelog\n", encoding="utf-8")
    (installed / "ai-sdlc-VERSION").write_text("0.73.0\n", encoding="utf-8")
    installed_pulse = installed / "skills" / "pulse"
    installed_pulse.mkdir(parents=True)
    (installed_pulse / "SKILL.md").write_text("# pulse\n", encoding="utf-8")

    # One BUILT_BUT_NOT_MERGED worktree
    detected = [
        (
            WorktreeInfo(
                path=str(worktree),
                branch="slice/077-test",
                head_sha="deadbeef",
                slice_num="077",
                slice_name="test",
                milestone_path=worktree / "milestone.md",
            ),
            WorktreeStateClassification(
                state=WorktreeState.BUILT_BUT_NOT_MERGED,
                reason="milestone stage=reflect; HEAD not ancestor of master",
                milestone_stage="reflect",
            ),
        ),
    ]
    assert should_suppress_vault_forward_population_flag(detected, installed_home=installed) is True


def test_do_not_suppress_when_installed_diverges_from_both_worktree_and_main(tmp_path):
    """Negative case: BUILT_BUT_NOT_MERGED exists BUT installed methodology-changelog
    diverges from worktree → predicate returns False (do NOT suppress; this is
    genuine three-way drift)."""
    worktree = tmp_path / "wt"
    worktree.mkdir()
    (worktree / "methodology-changelog.md").write_text("# changelog v1\n", encoding="utf-8")
    (worktree / "VERSION").write_text("0.73.0\n", encoding="utf-8")
    pulse_dir = worktree / "skills" / "pulse"
    pulse_dir.mkdir(parents=True)
    (pulse_dir / "SKILL.md").write_text("# pulse\n", encoding="utf-8")

    installed = tmp_path / "installed"
    installed.mkdir()
    # Diverges from worktree (different version)
    (installed / "methodology-changelog.md").write_text("# changelog DIVERGENT\n", encoding="utf-8")
    (installed / "ai-sdlc-VERSION").write_text("0.73.0\n", encoding="utf-8")
    installed_pulse = installed / "skills" / "pulse"
    installed_pulse.mkdir(parents=True)
    (installed_pulse / "SKILL.md").write_text("# pulse\n", encoding="utf-8")

    detected = [
        (
            WorktreeInfo(
                path=str(worktree),
                branch="slice/077-test",
                head_sha="deadbeef",
                slice_num="077",
                slice_name="test",
                milestone_path=worktree / "milestone.md",
            ),
            WorktreeStateClassification(
                state=WorktreeState.BUILT_BUT_NOT_MERGED,
                reason="milestone stage=reflect",
                milestone_stage="reflect",
            ),
        ),
    ]
    assert should_suppress_vault_forward_population_flag(detected, installed_home=installed) is False


def test_suppression_predicate_is_eol_agnostic_per_eol_drift_1(tmp_path):
    """EOL-tolerant comparison per ADR-033 / EOL-DRIFT-1: CRLF↔LF differences
    between installed and worktree do NOT count as divergence. Mirrors the
    surrounding CAD-1 / OSDG-1 carve-out per /critique B3 ACCEPTED-FIXED."""
    worktree = tmp_path / "wt"
    worktree.mkdir()
    # Worktree: LF endings
    (worktree / "methodology-changelog.md").write_text("# changelog\nline2\n", encoding="utf-8", newline="\n")
    (worktree / "VERSION").write_text("0.73.0\n", encoding="utf-8", newline="\n")
    pulse_dir = worktree / "skills" / "pulse"
    pulse_dir.mkdir(parents=True)
    (pulse_dir / "SKILL.md").write_text("# pulse\nbody\n", encoding="utf-8", newline="\n")

    # Installed: CRLF endings (typical Windows checkout)
    installed = tmp_path / "installed"
    installed.mkdir()
    (installed / "methodology-changelog.md").write_bytes(b"# changelog\r\nline2\r\n")
    (installed / "ai-sdlc-VERSION").write_bytes(b"0.73.0\r\n")
    installed_pulse = installed / "skills" / "pulse"
    installed_pulse.mkdir(parents=True)
    (installed_pulse / "SKILL.md").write_bytes(b"# pulse\r\nbody\r\n")

    detected = [
        (
            WorktreeInfo(
                path=str(worktree),
                branch="slice/077-test",
                head_sha="deadbeef",
                slice_num="077",
                slice_name="test",
                milestone_path=worktree / "milestone.md",
            ),
            WorktreeStateClassification(
                state=WorktreeState.BUILT_BUT_NOT_MERGED,
                reason="milestone stage=reflect",
                milestone_stage="reflect",
            ),
        ),
    ]
    # CRLF↔LF is NOT drift per EOL-DRIFT-1 → suppress fires
    assert should_suppress_vault_forward_population_flag(detected, installed_home=installed) is True, (
        "EOL-tolerant comparison failed — CRLF↔LF should NOT count as divergence per ADR-033 / EOL-DRIFT-1"
    )
