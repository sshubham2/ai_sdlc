"""Tests for the index-router thinness audit (ADR-093, slice-103).

Pins:
- the real-tree thinned routers + register are clean (regression guard);
- the audit is NON-VACUOUS by mutation (a bloated row / 26 entries / untagged
  entry / missing register / >10 recent rows each trip the right violation kind);
- the M3/APED-1 adversarial battery (CRLF, heading-less archive, a `|`-prose line
  OUTSIDE the table not counted, a fence inside the register file);
- the CLI exit-code contract (0 clean / 1 violations / 2 usage).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.index_router_thinness_audit import (
    _MAX_ACTION_POINTS,
    _MAX_ROW_CHARS,
    audit,
    check_archive_catalog,
    check_recent_10,
    check_register,
    main,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

# --- Minimal well-formed fixtures ------------------------------------------------

_THIN_INDEX = """# Slices Index

## Active

(none)

## Most recent 10

| # | Slice | Shipped | One-line summary |
|---|-------|---------|------------------|
| 103 | [slice-103-thin](archive/slice-103-thin/) | 2026-06-03 | Thin the hot index routers + enforce |
| 102 | [slice-102-foo](archive/slice-102-foo/) | 2026-06-02 | Vault-flip readiness on the tests surface |

Full register: [action-points.md](action-points.md).
"""

_THIN_ARCHIVE = """# Archived Slices Catalog

Chronological. Most recent at top.

| # | Slice | Shipped | One-line summary |
|---|-------|---------|------------------|
| 103 | [slice-103-thin](slice-103-thin/) | 2026-06-03 | Thin routers + enforce |
| 102 | [slice-102-foo](slice-102-foo/) | 2026-06-02 | Flip readiness, tests surface |
"""

_GOOD_REGISTER = """# Cross-slice action points

Synthesized from lessons-learned.md (full history lives there). Bounded ≤25.

- **AP-1** [build-check-candidate] A marker detector must be region-anchored, not `marker in line_text` (slices 099,100).
- **AP-2** [critic-calibrate-probe] A Critic's own fix is a fresh claim (slices 089,097,102).
- **AP-3** [already-a-gate] subprocess text capture must pass encoding="utf-8" (slice 090).
- **AP-4** [cultural] Barrier-synchronize concurrency proofs; prove non-vacuity by mutation (slices 092,094).
"""


def _write(tmp: Path, index=_THIN_INDEX, archive=_THIN_ARCHIVE, register=_GOOD_REGISTER):
    ip = tmp / "_index.md"
    ap = tmp / "archive_index.md"
    rp = tmp / "action-points.md"
    ip.write_text(index, encoding="utf-8")
    ap.write_text(archive, encoding="utf-8")
    if register is not None:
        rp.write_text(register, encoding="utf-8")
    return ip, ap, rp


# --- Clean fixtures -------------------------------------------------------------

def test_thin_fixtures_clean(tmp_path: Path):
    ip, ap, rp = _write(tmp_path)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert result.violations == [], [v.to_dict() for v in result.violations]
    assert result.recent_row_count == 2
    assert result.archive_row_count == 2
    assert result.register_entry_count == 4


def test_real_tree_clean():
    """The actual repo routers + register must be thin (regression guard)."""
    result = audit(repo_root=_REPO_ROOT)
    assert result.violations == [], [v.to_dict() for v in result.violations]


# --- Non-vacuity by mutation ----------------------------------------------------

def test_bloated_recent_row_trips_row_too_long(tmp_path: Path):
    bloated = _THIN_INDEX.replace(
        "Thin the hot index routers + enforce",
        "X" * (_MAX_ROW_CHARS + 50),
    )
    ip, ap, rp = _write(tmp_path, index=bloated)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    kinds = {v.kind for v in result.violations}
    assert "row-too-long" in kinds


def test_bloated_archive_row_trips_row_too_long(tmp_path: Path):
    bloated = _THIN_ARCHIVE.replace("Thin routers + enforce", "Y" * (_MAX_ROW_CHARS + 50))
    ip, ap, rp = _write(tmp_path, archive=bloated)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "row-too-long" for v in result.violations)


def test_too_many_recent_rows_trips_recent_10_too_many(tmp_path: Path):
    rows = "\n".join(
        f"| {n} | [slice-{n}-x](archive/slice-{n}-x/) | 2026-06-03 | one liner |"
        for n in range(120, 108, -1)  # 12 rows > 10
    )
    index = (
        "# Slices Index\n\n## Most recent 10\n\n"
        "| # | Slice | Shipped | One-line summary |\n|---|---|---|---|\n" + rows + "\n"
    )
    ip, ap, rp = _write(tmp_path, index=index)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "recent-10-too-many" for v in result.violations)


def test_over_25_register_entries_trips_register_too_many(tmp_path: Path):
    entries = "\n".join(
        f"- **AP-{n}** [cultural] point {n}" for n in range(1, _MAX_ACTION_POINTS + 5)
    )
    ip, ap, rp = _write(tmp_path, register="# Cross-slice action points\n\n" + entries + "\n")
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "register-too-many" for v in result.violations)


def test_untagged_register_entry_trips_register_untagged(tmp_path: Path):
    reg = "# Cross-slice action points\n\n- **AP-1** no verdict tag here\n"
    ip, ap, rp = _write(tmp_path, register=reg)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "register-untagged" for v in result.violations)


def test_invalid_verdict_tag_trips_register_untagged(tmp_path: Path):
    reg = "# Cross-slice action points\n\n- **AP-1** [not-a-verdict] something\n"
    ip, ap, rp = _write(tmp_path, register=reg)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "register-untagged" for v in result.violations)


def test_missing_register_trips_register_missing(tmp_path: Path):
    ip, ap, rp = _write(tmp_path, register=None)  # action-points.md absent
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "register-missing" for v in result.violations)


def test_register_bounds(tmp_path: Path):
    """Wiring-matrix-cited: the register count bound + verdict-tag invariant."""
    # Exactly 25 entries, all tagged → clean.
    entries = "\n".join(f"- **AP-{n}** [cultural] point {n}" for n in range(1, 26))
    ip, ap, rp = _write(tmp_path, register="# Cross-slice action points\n\n" + entries + "\n")
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert result.register_entry_count == 25
    assert not any(v.kind.startswith("register-") for v in result.violations)


# --- M3 / APED-1 adversarial battery --------------------------------------------

def test_crlf_index_rows_measured_without_eol(tmp_path: Path):
    """CRLF line endings must not inflate the row length past the cap falsely, and a
    genuinely-thin CRLF file stays clean (splitlines() strips \\r\\n)."""
    crlf_index = _THIN_INDEX.replace("\n", "\r\n")
    ip, ap, rp = _write(tmp_path, index=crlf_index)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert not any(v.kind == "row-too-long" for v in result.violations)


def test_heading_less_archive_anchored_on_header_row(tmp_path: Path):
    """archive/_index.md has NO `## ` heading; the region anchor is the catalog
    header row. A `|`-containing PROSE line BEFORE the header is NOT counted (M3)."""
    archive = (
        "# Archived Slices Catalog\n\n"
        "Note: pipes | can | appear | in prose before the table.\n\n"  # <-- not a data row
        "| # | Slice | Shipped | One-line summary |\n|---|---|---|---|\n"
        "| 1 | [slice-1-x](slice-1-x/) | 2026-01-01 | thin |\n"
    )
    ip, ap, rp = _write(tmp_path, archive=archive)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    # Only 1 real data row; the prose pipe-line is excluded (counted → would be 2).
    assert result.archive_row_count == 1
    assert not any(v.kind == "row-too-long" for v in result.violations)


def test_prose_pipe_line_outside_table_not_a_row(tmp_path: Path):
    """A long `|`-containing prose line OUTSIDE the table must NOT be flagged
    row-too-long (region-anchored, not a whole-file `^|` scan)."""
    long_prose = "Prose with a pipe | " + "z" * (_MAX_ROW_CHARS + 50)
    archive = (
        "# Archived Slices Catalog\n\n"
        + long_prose + "\n\n"
        + "| # | Slice | Shipped | One-line summary |\n|---|---|---|---|\n"
        + "| 1 | [slice-1-x](slice-1-x/) | 2026-01-01 | thin |\n"
    )
    ip, ap, rp = _write(tmp_path, archive=archive)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert not any(v.kind == "row-too-long" for v in result.violations)


def test_fence_in_register_file_is_harmless(tmp_path: Path):
    """A code fence inside action-points.md must not break the register parse
    (m2 — the audit keys on `- **AP-n**` entry lines, not fence balance)."""
    reg = (
        "# Cross-slice action points\n\n"
        "- **AP-1** [build-check-candidate] use a line-anchored ```^``` check, not a substring scan.\n"
        "- **AP-2** [cultural] another point.\n"
    )
    ip, ap, rp = _write(tmp_path, register=reg)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert result.register_entry_count == 2
    assert not any(v.kind.startswith("register-") for v in result.violations)


# --- Region-anchor fail-closed cases --------------------------------------------

def test_missing_recent_10_section_is_fail_closed(tmp_path: Path):
    index = "# Slices Index\n\n## Active\n\n(none)\n"  # no Most recent 10
    ip, ap, rp = _write(tmp_path, index=index)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "recent-10-section-missing" for v in result.violations)


def test_missing_archive_header_is_fail_closed(tmp_path: Path):
    archive = "# Archived Slices Catalog\n\nNo table here.\n"
    ip, ap, rp = _write(tmp_path, archive=archive)
    result = audit(index_path=ip, archive_path=ap, register_path=rp)
    assert any(v.kind == "archive-catalog-missing" for v in result.violations)


# --- CLI exit-code contract -----------------------------------------------------

def test_cli_exit_0_on_clean_real_tree():
    assert main(["--root", str(_REPO_ROOT)]) == 0


def test_cli_exit_2_on_unresolvable_root(tmp_path: Path, monkeypatch):
    # A directory with no .git ancestor and no --root → usage error exit 2.
    monkeypatch.chdir(tmp_path)
    assert main([]) == 2


def test_pure_check_functions_smoke():
    """The pure region checks are callable on text directly (no repo)."""
    n, viols = check_recent_10(_THIN_INDEX, "_index.md")
    assert n == 2 and viols == []
    n, viols = check_archive_catalog(_THIN_ARCHIVE, "archive/_index.md")
    assert n == 2 and viols == []
    n, viols = check_register(_GOOD_REGISTER, "action-points.md")
    assert n == 4 and viols == []


# --- code-review M1: empty-region fail-closed vs legitimately-empty -------------

def test_recent10_heading_without_table_is_fail_closed():
    """code-review M1: a `## Most recent 10` heading present but NO table beneath it
    (only a pointer / prose — a regen that lost the table) is fail-closed, not a
    silent pass."""
    index = "# I\n\n## Most recent 10\n\nFull register: [action-points.md](action-points.md).\n\n## Next\n"
    n, viols = check_recent_10(index, "_index.md")
    assert any(v.kind == "recent-10-section-missing" for v in viols), [v.to_dict() for v in viols]


def test_recent10_empty_table_with_header_is_clean():
    """code-review M1 boundary: a present-but-empty table (header + separator + 0
    rows) is a LEGITIMATE fresh-project state (0 archived slices) and must NOT
    false-fail — only a wholly-absent table is fail-closed."""
    index = "# I\n\n## Most recent 10\n\n| # | Slice | Shipped | s |\n|---|---|---|---|\n\n## Next\n"
    n, viols = check_recent_10(index, "_index.md")
    assert n == 0 and viols == [], [v.to_dict() for v in viols]


# --- code-review M2: verdict tag is leading-anchored, not whole-line -------------

def test_register_descriptive_bracketed_verdict_in_prose_is_clean(tmp_path: Path):
    """code-review M2: an entry with ONE leading verdict tag plus a DESCRIPTIVE
    bracketed verdict word later in its prose (or a markdown link) must stay clean —
    the check is anchored to the leading `**AP-n** [verdict]`, not a whole-line scan
    (which would count the prose mention and false-fail register-untagged)."""
    reg = (
        "# Cross-slice action points\n\n"
        "- **AP-1** [build-check-candidate] promote the recurring [cultural] discipline "
        "to a gate; see [the doc](already-a-gate) and `[critic-calibrate-probe]` inline.\n"
    )
    n, viols = check_register(reg, "action-points.md")
    assert n == 1 and not any(v.kind == "register-untagged" for v in viols), [v.to_dict() for v in viols]


def test_register_non_leading_tag_is_untagged():
    """code-review M2: a verdict word present ONLY later in the line (not the leading
    tag) does NOT satisfy the tag requirement → register-untagged."""
    reg = "# R\n\n- **AP-1** this entry mentions [cultural] but has no leading tag.\n"
    n, viols = check_register(reg, "action-points.md")
    assert any(v.kind == "register-untagged" for v in viols)


# --- code-review m1: exotic Unicode line boundary does not evade the cap ---------

def test_exotic_unicode_boundary_row_still_capped():
    """code-review m1: a bloated recent-10 row containing an embedded U+2028 (which
    str.splitlines() would split on, fragmenting the row under the cap) is still
    measured as ONE row and flagged row-too-long (_lines splits only on \\n)."""
    long_cell = "x" * 300 + " " + "y" * 300  # 601 chars, one logical row
    long_cell = "x" * 300 + chr(0x2028) + "y" * 300  # 601 chars w/ embedded U+2028
    index = (
        "# I\n\n## Most recent 10\n\n| # | Slice | Shipped | s |\n|---|---|---|---|\n"
        f"| 1 | [a](archive/a/) | 2026-01-01 | {long_cell} |\n"
    )
    n, viols = check_recent_10(index, "_index.md")
    assert any(v.kind == "row-too-long" for v in viols), [v.to_dict() for v in viols]
