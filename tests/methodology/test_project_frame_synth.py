"""Behavioral tests for the PFS-1 project-frame synthesizer.

Per **PFS-1** (`methodology-changelog.md` v0.78.0; slice-088; [[ADR-080]]):
`tools/project_frame_synth.py` emits an ephemeral, deterministic, tight
project-frame (Identity / Trajectory / Impact) to stdout so `/design-slice`
and both Critic layers review a slice against the project's deliberate
forward direction.

These pin the AC #1 contract: 3 required sections, the `_MAX_FRAME_LINES`
budget, deterministic regeneration from fixtures, and the
synthesis-not-concatenation property (deduped rule-FAMILY extraction +
score-shown risks) that a naive concatenation provably fails.

Rule reference: PFS-1 (slice-088; ADR-080).
"""
from pathlib import Path

from tools import project_frame_synth as pfs


def _build_fixture(root: Path, *, with_design: bool = False) -> Path:
    """Write a minimal but realistic project fixture under `root`; return the
    slice-dir. Sources deliberately carry U+2014 em-dashes (the RR-1 canonical
    separator + changelog header separator) so the synth's extracted-text path
    is exercised by realistic input."""
    (root / "architecture").mkdir(parents=True, exist_ok=True)
    (root / "architecture" / "concept.md").write_text(
        "---\ntype: concept\n---\n\n# Concept\n\n## What it does\n\n"
        "Fixture project does a thing end-to-end for its users.\n",
        encoding="utf-8",
    )
    (root / "architecture" / "triage.md").write_text(
        "---\nmode: STANDARD\n---\n\n# Triage\n\n## Mode: Standard\n",
        encoding="utf-8",
    )
    # Newest-first changelog; PSQ appears twice (PSQ-1 + PSQ-2) and MUST
    # collapse to a single PSQ family in the frame (synthesis, not concat).
    (root / "methodology-changelog.md").write_text(
        "# Methodology changelog\n\n"
        "## v0.78.0 — 2026-05-31\n\n"
        "**PFS-1 — project-frame synthesis** (slice-088; ADR-080).\n\n"
        "## v0.77.0 — 2026-05-30\n\n"
        "**PCR-2b — letter-suffixed rule id** (slice-083; ADR-075).\n\n"
        "## v0.71.0 — 2026-05-28\n\n"
        "**PSQ-2 — claim machinery** (slice-072; ADR-067).\n\n"
        "## v0.69.0 — 2026-05-27\n\n"
        "**PSQ-1 — parallel-slice queue** (slice-067; ADR-064).\n\n"
        "## v0.68.0 — 2026-05-26\n\n"
        "**BRANCH-2 — worktree-per-slice** (slice-068; ADR-063).\n",
        encoding="utf-8",
    )
    (root / "architecture" / "slice-queue.md").write_text(
        "# Slice queue\n\n## Candidates\n\n"
        "### add-foo-detector\n\n- **Source:** risk-register R-9 — latent\n\n"
        "### add-bar-cache\n\n- **Source:** deferral from slice-080\n",
        encoding="utf-8",
    )
    (root / "architecture" / "risk-register.md").write_text(
        "# Risk Register\n\n"
        "## R-1 — High-band test risk\n"
        "**Likelihood**: high\n**Impact**: high\n**Status**: open\n\n"
        "## R-2 — Low-band test risk\n"
        "**Likelihood**: low\n**Impact**: low\n**Status**: open\n\n"
        "## R-3 — Retired test risk\n"
        "**Likelihood**: high\n**Impact**: high\n**Status**: retired\n",
        encoding="utf-8",
    )
    slice_dir = root / "architecture" / "slices" / "slice-088-add-project-frame-synthesizer"
    slice_dir.mkdir(parents=True, exist_ok=True)
    (slice_dir / "mission-brief.md").write_text(
        "# Slice 088: add-project-frame-synthesizer\n\n## Intent\n\n"
        "Ship an ephemeral project-frame so reviews are direction-aware. "
        "Second sentence that should not appear.\n",
        encoding="utf-8",
    )
    if with_design:
        (slice_dir / "design.md").write_text("# Design\n\nstuff\n", encoding="utf-8")
    return slice_dir


def test_frame_has_identity_trajectory_impact(tmp_path):
    """AC #1: the frame carries the 3 required section headings."""
    slice_dir = _build_fixture(tmp_path)
    frame = pfs.synthesize_frame(tmp_path, slice_dir)
    assert "## Identity" in frame
    assert "## Trajectory" in frame
    assert "## Impact" in frame
    # Anchoring guard: the adversarial ATTACK-LENS preamble is the first line.
    assert frame.splitlines()[0].startswith("ATTACK-LENS")


def test_frame_respects_tight_budget(tmp_path):
    """AC #1 must-not-defer: hard line budget; over-budget truncates with marker."""
    slice_dir = _build_fixture(tmp_path)
    # Default budget.
    frame = pfs.synthesize_frame(tmp_path, slice_dir)
    assert len(frame.splitlines()) <= pfs._MAX_FRAME_LINES
    # Forced tiny budget must truncate AND mark it.
    tiny = pfs.synthesize_frame(tmp_path, slice_dir, max_lines=5)
    assert len(tiny.splitlines()) <= 5
    assert "(frame truncated to budget)" in tiny


def test_frame_regenerates_deterministically(tmp_path):
    """AC #1: identical fixtures -> byte-identical frame (no wall-clock/randomness)."""
    slice_dir = _build_fixture(tmp_path)
    first = pfs.synthesize_frame(tmp_path, slice_dir)
    second = pfs.synthesize_frame(tmp_path, slice_dir)
    assert first == second


def test_frame_trajectory_synthesizes_not_concatenates(tmp_path):
    """AC #1 (M4): the Trajectory section is SYNTHESIS, not concatenation —
    properties a naive concat provably fails:
      (a) rule families are DEDUPED (PSQ-1 + PSQ-2 -> one 'PSQ'),
      (b) open risks are SCORE-RANKED with the score shown (high-band first),
      (c) retired risks are excluded,
      (d) slice-queue candidates appear by NAME.
    """
    slice_dir = _build_fixture(tmp_path)
    frame = pfs.synthesize_frame(tmp_path, slice_dir)
    traj = frame.split("## Trajectory", 1)[1].split("## Impact", 1)[0]

    # (a) dedup: PSQ appears exactly once despite two PSQ-N changelog entries;
    # PFS + BRANCH also present.
    assert traj.count("PSQ") == 1, f"PSQ not deduped:\n{traj}"
    assert "PFS" in traj and "BRANCH" in traj

    # (a') /code-review M1: a LETTER-SUFFIXED rule id (`PCR-2b`) must NOT be
    # silently dropped — its family `PCR` must surface (the pre-fix `\b` regex
    # collapsed `PCR-2b` to `PCR` then `_FAMILY_RE` rejected it).
    assert "PCR" in traj, f"letter-suffixed rule-id family (PCR-2b) dropped:\n{traj}"

    # (b) score shown + (c) retired excluded + ranking: R-1 (high) before R-2 (low),
    # R-3 (retired) absent.
    assert "(score " in traj, f"risk score not shown:\n{traj}"
    assert traj.index("R-1") < traj.index("R-2"), "risks not score-ranked"
    assert "R-3" not in traj, "retired risk leaked into trajectory"

    # (d) candidates by name.
    assert "add-foo-detector" in traj and "add-bar-cache" in traj


def test_impact_degrades_when_design_absent(tmp_path):
    """AC #2 (M5): at /design-slice Step 0.5 the slice's design.md does not yet
    exist; Impact degrades to mission-brief-only WITHOUT error."""
    slice_dir = _build_fixture(tmp_path, with_design=False)
    frame = pfs.synthesize_frame(tmp_path, slice_dir)
    impact = frame.split("## Impact", 1)[1]
    assert "add-project-frame-synthesizer" in impact
    # The degraded marker names the absent design explicitly.
    assert "mission-brief-only" in impact or "design.md not yet written" in impact


def test_budget_clamps_degenerate_max_lines(tmp_path):
    """/code-review M2: a 0/negative budget must NOT overflow (the pre-fix
    negative-slice index dropped only the tail, emitting a near-full frame)."""
    slice_dir = _build_fixture(tmp_path)
    for bad in (0, -1, -10):
        out = pfs.synthesize_frame(tmp_path, slice_dir, max_lines=bad)
        assert len(out.splitlines()) <= 1, (
            f"max_lines={bad} overflowed the budget: {len(out.splitlines())} lines"
        )
    # The CLI rejects a degenerate budget with a usage error (exit 2), never a breach.
    import pytest

    with pytest.raises(SystemExit) as exc:
        pfs.main(["--repo-root", str(tmp_path), "--slice-dir", str(slice_dir), "--max-lines", "0"])
    assert exc.value.code == 2


def test_open_risks_uses_parse_risks_api():
    """/code-review m2: pin the private-API coupling the synth depends on, so a
    `risk_register_audit` refactor trips a red test instead of silently emptying
    the frame's risk line."""
    from tools import risk_register_audit as rra

    assert hasattr(rra, "_parse_risks")
    for field in ("risk_id", "title", "score", "status"):
        assert field in rra.Risk.__dataclass_fields__, (
            f"risk_register_audit.Risk lost the '{field}' field project_frame_synth depends on"
        )
