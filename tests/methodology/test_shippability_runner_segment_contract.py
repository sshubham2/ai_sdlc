"""SRSC-1 — pinned shippability-runner per-`;`-segment contract.

Per SRSC-1 (methodology-changelog.md v0.51.0; slice-038; ADR-039). Retires
R-8: a hand-rolled Step-5.5 runner that strips only the OUTER markdown fence
of a whole `Machine-cmd` cell mangles segment 2 of the lone multi-segment row
(#28) into a leading-backtick `argv[0]` -> WinError 2 (recurred N=2:
slice-032, slice-033).

The load-bearing test is `test_naive_outer_strip_runner_is_rejected`: it
exercises BOTH the historical naive-outer-strip (proves it IS broken on real
row #28) AND the canonical reused `_segments()` (proves it is NOT) in one
test, so the green is a contract-boundary proof, not a tautology over the
already-correct helper (critique m2 / slice-037 load-bearing-test lesson).
"""
from __future__ import annotations

from pathlib import Path

import tools.shippability_decoupling_audit as scmd1
import tools.shippability_runner as runner

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_CATALOG = REPO_ROOT / "architecture" / "shippability.md"


def _naive_outer_strip(cell: str) -> list[str]:
    """The historical R-8 bug: strip the OUTER fence of the WHOLE cell ONCE,
    then split on `;`. Leaves the inner per-segment backticks intact, so
    segment 2 retains a leading backtick -> `argv[0] = `<interp>...` ->
    WinError 2. This is the WRONG implementation, reproduced verbatim so the
    contrast against `_segments()` is exercised, not asserted."""
    stripped = cell.strip().strip("`")
    return [s.strip() for s in stripped.split(";") if s.strip()]


def _real_row_28_cell() -> str:
    text = REAL_CATALOG.read_text(encoding="utf-8")
    for _line, cells in scmd1._catalog_rows(text):
        if cells[0].strip() == "28":
            cell = scmd1._machine_cmd_cell(cells)
            assert cell, "row #28 has no Machine-cmd cell"
            return cell
    raise AssertionError("row #28 not found in real architecture/shippability.md")


# --- AC1: per-`;`-segment split + strip, and REUSE (not re-derivation) -------

def test_multi_segment_row_splits_and_strips_per_segment():
    """A 2-segment cell `\\`A\\` ; \\`B\\`` yields exactly two segments, each
    with NO surrounding backtick or whitespace (the SCMD-1 canonical
    contract). Also pins that the runner REUSES the canonical `_segments`
    (object identity) rather than re-deriving it -- the CSP-1 single-source
    guarantee SRSC-1 exists to enforce."""
    cell = "`<interp> -m pytest tests/a/test_x.py -q` ; `<interp> -m pytest tests/b/test_y.py -q`"
    segs = runner._segments(cell)
    assert len(segs) == 2, segs
    for seg in segs:
        assert not seg.startswith("`"), f"leading backtick survived: {seg!r}"
        assert not seg.endswith("`"), f"trailing backtick survived: {seg!r}"
        assert seg == seg.strip(), f"surrounding ws survived: {seg!r}"
    assert segs[0] == "<interp> -m pytest tests/a/test_x.py -q"
    assert segs[1] == "<interp> -m pytest tests/b/test_y.py -q"
    # REUSE, not re-derivation (object identity across the two modules):
    assert runner._segments is scmd1._segments
    assert runner._catalog_rows is scmd1._catalog_rows
    assert runner._machine_cmd_cell is scmd1._machine_cmd_cell


# --- AC2 / AC5: the real lone multi-segment row #28 is correctly parsed ------

def test_real_row_28_both_segments_interpreter_anchored():
    """The real `architecture/shippability.md` row #28 (the lone multi-segment
    row this slice exists to fix) splits into exactly two segments, each an
    interpreter-anchored pytest invocation with NO leading backtick on
    segment 2 (the R-8 WinError-2 signature). Reading the real catalog is
    SCMD-1-`clean` (the catalog being run, not gitignored archive/build-checks
    -- not the incidental class)."""
    cell = _real_row_28_cell()
    segs = runner._segments(cell)
    assert len(segs) == 2, f"row #28 expected 2 segments, got {segs!r}"
    for seg in segs:
        assert not seg.startswith("`"), (
            f"R-8 signature: segment retains a leading backtick -> "
            f"argv[0] would be mangled: {seg!r}")
        toks = seg.split()
        assert toks[0] in {"<interp>"} or toks[0].endswith(("python", "python.exe")), (
            f"segment is not interpreter-anchored: {seg!r}")
        assert "-m" in toks and "pytest" in toks, (
            f"segment is not a pytest invocation: {seg!r}")


# --- AC2: load-bearing negative contrast (the R-8 failing-first proof) -------

def test_naive_outer_strip_runner_is_rejected():
    """LOAD-BEARING: on the REAL row #28, the historical naive-outer-strip
    leaves a leading backtick on segment 2 (the R-8 bug -> WinError 2) WHILE
    the canonical reused `_segments()` does not. Both branches are exercised
    in one test, so this green proves the contract boundary -- it is NOT a
    tautology over the already-correct `_segments()` (critique m2)."""
    cell = _real_row_28_cell()

    naive = _naive_outer_strip(cell)
    canonical = runner._segments(cell)

    # The naive strip IS broken: it does not yield 2 clean segments; its
    # segment 2 retains a leading backtick (the exact R-8 WinError-2 cause).
    assert len(naive) >= 2, naive
    assert naive[1].startswith("`"), (
        "expected the historical naive-outer-strip to leave a leading "
        f"backtick on segment 2 (R-8 bug); got {naive[1]!r} -- if this no "
        "longer reproduces, the test is no longer load-bearing")

    # The canonical reused `_segments()` is NOT broken: 2 clean segments,
    # no leading backtick anywhere.
    assert len(canonical) == 2, canonical
    assert not canonical[1].startswith("`"), (
        f"canonical _segments() must not leave a leading backtick: "
        f"{canonical[1]!r}")
    assert canonical != naive, (
        "the canonical split-strip must differ from the broken naive strip "
        "on the real multi-segment row -- otherwise the pin is vacuous")


# --- AC3: /validate-slice Step 5.5 prose pins the runner invocation ----------

def test_validate_slice_skill_pins_runner_invocation():
    """`skills/validate-slice/SKILL.md` Step 5.5 explicitly INVOKES the
    canonical runner and pins the no-hand-roll + reuse contract by the
    canonical-mechanism strings (a CONTENT pin per critique M1 -- asserting
    the mechanism is named, not merely that Step 5.5 changed). Asserted on
    BOTH in-repo and the installed copy (forward-sync guard -- Claude reads
    the installed SKILL.md at /validate-slice)."""
    in_repo = (REPO_ROOT / "skills" / "validate-slice" / "SKILL.md").read_text(
        encoding="utf-8")
    installed = (Path.home() / ".claude" / "skills" / "validate-slice"
                 / "SKILL.md").read_text(encoding="utf-8")
    for surface, content in [("in-repo", in_repo), ("installed", installed)]:
        assert "tools.shippability_runner" in content, (
            f"{surface} validate-slice/SKILL.md does not invoke "
            f"tools.shippability_runner -- the contract is unbound (R-8 "
            f"folklore failure)")
        assert "do NOT hand-roll the execution loop" in content, (
            f"{surface} validate-slice/SKILL.md missing the canonical "
            f"no-hand-roll pin -- a future edit could silently revert to a "
            f"prose-described loop")
        assert "reuses SCMD-1" in content and "_segments()" in content, (
            f"{surface} validate-slice/SKILL.md missing the canonical "
            f"reuse-of-SCMD-1-_segments() mechanism pin")
        assert "SRSC-1" in content, (
            f"{surface} validate-slice/SKILL.md Step 5.5 does not cite the "
            f"SRSC-1 rule id")
