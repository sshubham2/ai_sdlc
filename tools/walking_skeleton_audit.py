"""Walking-skeleton slice audit (WS-1).

Parses a slice's `mission-brief.md` and validates:
  - The opt-in field `**Walking-skeleton**: true | false` is recognized
  - When true, a `## Architectural layers exercised` section must exist
    with a 5-column table: # | Layer | Component | Verification | Status
  - The table has at least one data row (a walking skeleton with no
    layers is meaningless — that's a standard slice)
  - Each row's Verification cell is non-empty
  - Each row's Status is one of {PENDING, EXERCISED}
  - With --strict-pre-finish, any non-EXERCISED row is a violation
    (used at /validate-slice Step 5c)

Per WS-1 (methodology-changelog.md v0.15.0). The walking-skeleton
discipline (Cockburn): the smallest possible end-to-end implementation
that exercises every architectural layer. Real features layer onto
the proven foundation. Contrast with test-first (TF-1) — which is
about test discipline before implementation — and the standard slice,
which is feature-driven.

Default-off semantics: a brief without `**Walking-skeleton**:` (or with
false) is unaffected. WS-1 is opt-in per slice; old briefs continue to
work without modification.

NFR-1 carry-over: slices whose mission-brief.md mtime predates
`_WS_1_RELEASE_DATE` are exempt automatically.

Usage:
    python -m tools.walking_skeleton_audit <slice-folder>
    python -m tools.walking_skeleton_audit <mission-brief.md>
    python -m tools.walking_skeleton_audit <slice-folder> --strict-pre-finish
    python -m tools.walking_skeleton_audit <slice-folder> --json
    python -m tools.walking_skeleton_audit <slice-folder> --no-carry-over

Exit codes:
    0  clean (or default-off / carry-over exempt)
    1  violations
    2  usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path

# Date this rule shipped. NFR-1 carry-over.
_WS_1_RELEASE_DATE: date = date(2026, 5, 6)

# Field-line: `**Walking-skeleton**: true`
_WS_FIELD_RE = re.compile(
    r"^\*\*Walking[-\s]?skeleton\*\*\s*:\s*(true|false)\s*$",
    re.IGNORECASE,
)

# Section heading: `## Architectural layers exercised`
_LAYERS_HEADING_RE = re.compile(
    r"^##\s+Architectural\s+layers\s+exercised\s*$",
    re.IGNORECASE,
)

_OTHER_H2_RE = re.compile(r"^##\s+\S")

# Allowed statuses
_ALLOWED_STATUSES: frozenset[str] = frozenset({"PENDING", "EXERCISED"})

# Required columns
_REQUIRED_COLUMNS = 5

_EMPTY_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)"})


@dataclass(frozen=True)
class LayerRow:
    index: str       # the # column value (e.g. "1", "2"); free-form string
    layer: str       # name of the architectural layer
    component: str   # the component / file / module touched
    verification: str  # how this layer's exercise is verified
    status: str      # "PENDING" | "EXERCISED"
    line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WSViolation:
    path: str
    line: int
    layer_index: str  # "" for section-level errors
    kind: str         # "missing-section" | "empty-table" | "missing-verification" |
                      # "invalid-status" | "format" | "missing-cells" |
                      # "non-exercised-pre-finish"
    severity: str     # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    walking_skeleton_enabled: bool = False
    rows: list[LayerRow] = field(default_factory=list)
    violations: list[WSViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "walking_skeleton_enabled": self.walking_skeleton_enabled,
            "rows": [r.to_dict() for r in self.rows],
            "violations": [v.to_dict() for v in self.violations],
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "row_count": len(self.rows),
                "by_status": {
                    s: sum(1 for r in self.rows if r.status == s)
                    for s in _ALLOWED_STATUSES
                },
                "violation_count": len(self.violations),
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _WS_1_RELEASE_DATE


def _detect_ws_flag(text: str) -> bool:
    """Return True if `**Walking-skeleton**: true` is present."""
    for line in text.splitlines():
        m = _WS_FIELD_RE.match(line)
        if m:
            return m.group(1).strip().lower() == "true"
    return False


def _find_layers_table_lines(text: str) -> tuple[int, list[str]] | None:
    """Locate the layers table; return (start_line_idx, table_lines) or None."""
    lines = text.splitlines()
    heading_idx: int | None = None
    for i, line in enumerate(lines):
        if _LAYERS_HEADING_RE.match(line):
            heading_idx = i
            break
    if heading_idx is None:
        return None

    table_start: int | None = None
    for j in range(heading_idx + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("|"):
            table_start = j
            break
        if _OTHER_H2_RE.match(lines[j]):
            return None

    if table_start is None:
        return None

    table_lines: list[str] = []
    for j in range(table_start, len(lines)):
        if lines[j].strip().startswith("|"):
            table_lines.append(lines[j])
        else:
            break
    return (table_start, table_lines)


def _parse_table_cells(line: str) -> list[str]:
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _parse_table_cells(line)
    if not cells:
        return False
    for cell in cells:
        stripped = cell.replace(" ", "")
        if not stripped:
            return False
        if not set(stripped) <= set("-:"):
            return False
        if "-" not in stripped:
            return False
    return True


def _cell_is_empty(cell: str) -> bool:
    return cell.strip().lower() in _EMPTY_SENTINELS


def audit_brief_file(
    brief_path: Path,
    strict_pre_finish: bool = False,
    skip_if_carry_over: bool = True,
) -> AuditResult:
    """Audit a mission-brief.md against WS-1."""
    result = AuditResult()

    if not brief_path.exists():
        return result

    if skip_if_carry_over:
        slice_folder = brief_path.parent
        if _slice_is_carry_over(slice_folder):
            result.carry_over_exempt = True
            return result

    text = brief_path.read_text(encoding="utf-8")
    enabled = _detect_ws_flag(text)
    result.walking_skeleton_enabled = enabled

    if not enabled:
        return result  # default-off; nothing else to check

    found = _find_layers_table_lines(text)
    if found is None:
        result.violations.append(WSViolation(
            path=str(brief_path), line=0, layer_index="",
            kind="missing-section", severity="Important",
            message=(
                "`**Walking-skeleton**: true` is set but no "
                "`## Architectural layers exercised` section with a table "
                "was found. Per WS-1, when walking-skeleton is enabled, "
                "the brief must include a 5-column table listing every "
                "architectural layer the slice touches end-to-end."
            ),
        ))
        return result

    table_start, table_lines = found

    if len(table_lines) < 2:
        result.violations.append(WSViolation(
            path=str(brief_path), line=table_start + 1, layer_index="",
            kind="format", severity="Important",
            message=(
                "layers table is malformed: needs header + separator at "
                "minimum (# | Layer | Component | Verification | Status)."
            ),
        ))
        return result

    if not _is_separator_row(table_lines[1]):
        result.violations.append(WSViolation(
            path=str(brief_path), line=table_start + 2, layer_index="",
            kind="format", severity="Important",
            message=(
                "layers table second line must be the markdown separator "
                "(`|---|---|---|---|---|`)."
            ),
        ))
        return result

    header_cells = _parse_table_cells(table_lines[0])
    if len(header_cells) < _REQUIRED_COLUMNS:
        result.violations.append(WSViolation(
            path=str(brief_path), line=table_start + 1, layer_index="",
            kind="format", severity="Important",
            message=(
                f"layers table needs {_REQUIRED_COLUMNS} columns "
                f"(# | Layer | Component | Verification | Status); "
                f"found {len(header_cells)}: {header_cells}"
            ),
        ))
        return result

    data_rows = table_lines[2:]
    if not data_rows:
        result.violations.append(WSViolation(
            path=str(brief_path), line=table_start + 1, layer_index="",
            kind="empty-table", severity="Important",
            message=(
                "layers table has no data rows. A walking skeleton with "
                "zero layers is meaningless — that's a standard slice. "
                "Per WS-1, list every architectural layer the slice touches."
            ),
        ))
        return result

    for idx, raw in enumerate(data_rows, start=1):
        line_num = table_start + 2 + idx
        cells = _parse_table_cells(raw)
        if len(cells) < _REQUIRED_COLUMNS:
            result.violations.append(WSViolation(
                path=str(brief_path), line=line_num, layer_index="",
                kind="missing-cells", severity="Important",
                message=(
                    f"row {idx}: {len(cells)} cells; expected {_REQUIRED_COLUMNS}"
                ),
            ))
            continue

        index_cell, layer, component, verification, status_raw = (
            c.strip() for c in cells[:_REQUIRED_COLUMNS]
        )
        if _cell_is_empty(index_cell) and _cell_is_empty(layer):
            continue  # blank row — skip silently

        if _cell_is_empty(verification):
            result.violations.append(WSViolation(
                path=str(brief_path), line=line_num, layer_index=index_cell,
                kind="missing-verification", severity="Important",
                message=(
                    f"row {idx} (layer '{layer}'): Verification cell is "
                    f"empty. Per WS-1, every layer must declare HOW its "
                    f"exercise is verified at runtime."
                ),
            ))
            continue

        status = status_raw.upper().strip()
        if status not in _ALLOWED_STATUSES:
            result.violations.append(WSViolation(
                path=str(brief_path), line=line_num, layer_index=index_cell,
                kind="invalid-status", severity="Important",
                message=(
                    f"row {idx} (layer '{layer}'): status '{status_raw}' "
                    f"not in {sorted(_ALLOWED_STATUSES)}."
                ),
            ))
            continue

        result.rows.append(LayerRow(
            index=index_cell, layer=layer, component=component,
            verification=verification, status=status, line=line_num,
        ))

    if strict_pre_finish:
        for row in result.rows:
            if row.status != "EXERCISED":
                result.violations.append(WSViolation(
                    path=str(brief_path), line=row.line,
                    layer_index=row.index,
                    kind="non-exercised-pre-finish", severity="Important",
                    message=(
                        f"row for layer '{row.layer}' status is "
                        f"{row.status}; --strict-pre-finish requires "
                        f"EXERCISED. The walking-skeleton hasn't actually "
                        f"reached this layer yet — fix the implementation "
                        f"or remove --strict-pre-finish (only used at "
                        f"/validate-slice Step 5c)."
                    ),
                ))

    return result


def _format_human(result: AuditResult) -> str:
    if result.carry_over_exempt:
        return (
            "Walking-skeleton audit: slice is carry-over exempt "
            "(mission-brief.md predates WS-1 release).\n"
        )
    if not result.walking_skeleton_enabled:
        return (
            "Walking-skeleton audit: not enabled "
            "(`**Walking-skeleton**: true` absent).\n"
        )

    if not result.violations:
        by_status = {
            s: sum(1 for r in result.rows if r.status == s)
            for s in _ALLOWED_STATUSES
        }
        return (
            f"Walking-skeleton audit: clean. {len(result.rows)} layer(s) — "
            f"EXERCISED={by_status['EXERCISED']}, "
            f"PENDING={by_status['PENDING']}.\n"
        )

    out: list[str] = [
        f"{len(result.violations)} walking-skeleton violation(s):\n\n"
    ]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
            f"{f'layer #{v.layer_index}' if v.layer_index else ''}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="walking_skeleton_audit",
        description="WS-1 walking-skeleton slice variant audit",
    )
    parser.add_argument(
        "target", type=Path,
        help="Slice folder (auto-finds mission-brief.md inside) OR a mission-brief.md file",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--strict-pre-finish", action="store_true",
        help="Refuse non-EXERCISED rows (use at /validate-slice Step 5c)",
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    args = parser.parse_args(argv)

    target: Path = args.target
    brief_path = target / "mission-brief.md" if target.is_dir() else target

    result = audit_brief_file(
        brief_path,
        strict_pre_finish=args.strict_pre_finish,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
