"""Triage audit (TRI-1).

Parses the `## Triage` section of a slice's critique.md and validates:
  - Section heading present
  - Triaged by / Date / Final verdict fields present
  - Final verdict is one of {CLEAN, NEEDS-FIXES, BLOCKED}
  - Every finding in the body (#### B1, #### M1, #### m1) has a disposition row
  - Each disposition is in the allowed vocabulary
  - OVERRIDDEN / DEFERRED / ESCALATED rows have non-empty rationale
  - Final verdict is consistent with the disposition pattern:
      any ESCALATED                  -> BLOCKED
      any ACCEPTED-PENDING (no esc.) -> NEEDS-FIXES
      otherwise                      -> CLEAN

Per TRI-1 (methodology-changelog.md v0.11.0). The rule's purpose: make
Critic-Builder-User triage explicit and auditable so dispositions don't
disappear into Builder hand-waves and the user has formal authority over
the gate decision.

Three terminal verdicts:
  - CLEAN          ready to /build-slice (no pending fixes, no escalations)
  - NEEDS-FIXES    ready to /build-slice once Builder applies ACCEPTED-PENDING fixes
  - BLOCKED        cannot /build-slice — escalation or redesign required

Disposition vocabulary:
  - ACCEPTED-FIXED      agree with Critic; fix applied already
  - ACCEPTED-PENDING    agree with Critic; fix to apply during /build-slice
  - OVERRIDDEN          user disagrees with Critic — rationale required
  - DEFERRED            known issue; later slice — rationale required
  - ESCALATED           spike or redesign needed — rationale required

NFR-1 carry-over: slices whose mission-brief.md mtime predates the rule's
release date (_TRI_1_RELEASE_DATE) are exempt automatically.

Usage:
    python -m tools.triage_audit <slice-folder>
    python -m tools.triage_audit <critique.md>
    python -m tools.triage_audit --json <slice-folder>
    python -m tools.triage_audit --no-carry-over <slice-folder>

Exit codes:
    0  clean (or carry-over exempt)
    1  triage violations
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
_TRI_1_RELEASE_DATE: date = date(2026, 5, 6)

# Triage section heading
_TRIAGE_HEADING = "## Triage"

# Required fields in the triage section header block
_REQUIRED_HEADER_FIELDS: frozenset[str] = frozenset({
    "triaged by", "date", "final verdict",
})

# Allowed final verdict values (case-sensitive in critique.md, but we compare
# case-insensitively at parse time)
_ALLOWED_VERDICTS: frozenset[str] = frozenset({"CLEAN", "NEEDS-FIXES", "BLOCKED"})

# Allowed dispositions
_ALLOWED_DISPOSITIONS: frozenset[str] = frozenset({
    "ACCEPTED-FIXED", "ACCEPTED-PENDING", "OVERRIDDEN", "DEFERRED", "ESCALATED",
})

# Dispositions that REQUIRE a non-empty rationale cell
_RATIONALE_REQUIRED: frozenset[str] = frozenset({
    "OVERRIDDEN", "DEFERRED", "ESCALATED",
})

# Sentinel cell values treated as empty
_EMPTY_SENTINELS = frozenset({"", "—", "-", "n/a", "none", "(none)"})

# H4 finding heading regex, e.g. "#### B1: title", "#### M2: ...", "#### m1: ..."
_FINDING_HEADING_RE = re.compile(r"^####\s+([BMm]\d+)\s*:\s*(.+?)\s*$")

# Field-line pattern
_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z\s]*)\*\*\s*:\s*(.*?)\s*$")


@dataclass(frozen=True)
class TriageViolation:
    """A finding emitted by the audit."""
    path: str
    line: int
    finding_id: str  # may be "" for section-level errors
    kind: str        # "no-section" | "missing-field" | "invalid-verdict" |
                     # "missing-row" | "invalid-disposition" |
                     # "missing-rationale" | "verdict-mismatch" | "format"
    severity: str    # always "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TriageResult:
    declared_verdict: str = ""
    expected_verdict: str = ""
    triaged_by: str = ""
    date: str = ""
    findings: list[str] = field(default_factory=list)
    dispositions: dict[str, str] = field(default_factory=dict)  # finding_id -> disposition
    violations: list[TriageViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "declared_verdict": self.declared_verdict,
            "expected_verdict": self.expected_verdict,
            "triaged_by": self.triaged_by,
            "date": self.date,
            "findings": list(self.findings),
            "dispositions": dict(self.dispositions),
            "violations": [v.to_dict() for v in self.violations],
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "violation_count": len(self.violations),
                "consistent": (
                    self.declared_verdict == self.expected_verdict
                    if self.declared_verdict and self.expected_verdict
                    else False
                ),
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    """True if the slice was authored before TRI-1 (mtime carry-over)."""
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _TRI_1_RELEASE_DATE


def _cell_is_empty(cell: str) -> bool:
    return cell.strip().lower() in _EMPTY_SENTINELS


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


def _find_findings_in_body(text: str, triage_start_line: int | None) -> list[str]:
    """Extract finding IDs (B1, M1, m1, ...) from H4 headings BEFORE the Triage section.

    Findings declared after the Triage section are not part of the body the
    triage covers (they don't exist).
    """
    found: list[str] = []
    seen: set[str] = set()
    for i, line in enumerate(text.splitlines()):
        if triage_start_line is not None and i >= triage_start_line:
            break
        m = _FINDING_HEADING_RE.match(line)
        if m:
            fid = m.group(1)
            if fid not in seen:
                seen.add(fid)
                found.append(fid)
    return found


def _expected_verdict(dispositions: dict[str, str]) -> str:
    """Compute the expected verdict from the disposition pattern."""
    if not dispositions:
        return "CLEAN"
    values = set(dispositions.values())
    if "ESCALATED" in values:
        return "BLOCKED"
    if "ACCEPTED-PENDING" in values:
        return "NEEDS-FIXES"
    return "CLEAN"


def audit_critique_file(
    critique_path: Path,
    skip_if_carry_over: bool = True,
) -> TriageResult:
    """Audit a critique.md file against TRI-1 triage rules."""
    result = TriageResult()

    if not critique_path.exists():
        result.violations.append(TriageViolation(
            path=str(critique_path), line=0, finding_id="",
            kind="no-section", severity="Important",
            message=f"critique.md not found: {critique_path}",
        ))
        return result

    if skip_if_carry_over:
        slice_folder = critique_path.parent
        if _slice_is_carry_over(slice_folder):
            result.carry_over_exempt = True
            return result

    text = critique_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Locate the Triage section
    triage_start: int | None = None
    for i, line in enumerate(lines):
        if line.strip() == _TRIAGE_HEADING:
            triage_start = i
            break

    findings = _find_findings_in_body(text, triage_start)
    result.findings = findings

    if triage_start is None:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=0, finding_id="",
            kind="no-section", severity="Important",
            message=(
                f"no `{_TRIAGE_HEADING}` heading found in critique.md. "
                f"Per TRI-1, every critique must include a user-ratified "
                f"triage section (Triaged by / Date / Final verdict + "
                f"per-finding dispositions)."
            ),
        ))
        return result

    # Parse header fields between Triage heading and the table (or next H2)
    header_fields: dict[str, str] = {}
    table_start: int | None = None
    for j in range(triage_start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("|"):
            table_start = j
            break
        if stripped.startswith("## ") or stripped.startswith("# "):
            break  # next section without table
        m = _FIELD_RE.match(lines[j])
        if m:
            key = m.group(1).strip().lower()
            value = m.group(2).strip()
            header_fields[key] = value

    # Validate required header fields
    missing_header = _REQUIRED_HEADER_FIELDS - set(header_fields.keys())
    if missing_header:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=triage_start + 1, finding_id="",
            kind="missing-field", severity="Important",
            message=(
                f"triage section missing required field(s): "
                f"{', '.join(sorted(missing_header))}. Required: "
                f"{', '.join(sorted(_REQUIRED_HEADER_FIELDS))}."
            ),
        ))

    result.triaged_by = header_fields.get("triaged by", "")
    result.date = header_fields.get("date", "")
    declared = header_fields.get("final verdict", "").strip().upper()
    result.declared_verdict = declared

    if declared and declared not in _ALLOWED_VERDICTS:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=triage_start + 1, finding_id="",
            kind="invalid-verdict", severity="Important",
            message=(
                f"final verdict '{declared}' not allowed. Use one of: "
                f"{', '.join(sorted(_ALLOWED_VERDICTS))}."
            ),
        ))

    # If no findings in body, no table is required; verdict should be CLEAN.
    if not findings:
        result.expected_verdict = "CLEAN"
        if declared and declared != "CLEAN":
            result.violations.append(TriageViolation(
                path=str(critique_path), line=triage_start + 1, finding_id="",
                kind="verdict-mismatch", severity="Important",
                message=(
                    f"final verdict '{declared}' does not match disposition "
                    f"pattern: no findings in body imply CLEAN."
                ),
            ))
        return result

    # Findings exist — table is required
    if table_start is None:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=triage_start + 1, finding_id="",
            kind="format", severity="Important",
            message=(
                "triage section has findings in body but no disposition table. "
                "Add a 4-column table: ID | Severity | Disposition | Rationale."
            ),
        ))
        return result

    # Collect contiguous table lines
    table_lines: list[str] = []
    for j in range(table_start, len(lines)):
        if lines[j].strip().startswith("|"):
            table_lines.append(lines[j])
        else:
            break

    if len(table_lines) < 2:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=table_start + 1, finding_id="",
            kind="format", severity="Important",
            message=(
                "triage table is malformed: needs header + separator at "
                "minimum (ID | Severity | Disposition | Rationale)."
            ),
        ))
        return result

    if not _is_separator_row(table_lines[1]):
        result.violations.append(TriageViolation(
            path=str(critique_path), line=table_start + 2, finding_id="",
            kind="format", severity="Important",
            message=(
                "triage table second line must be the markdown separator "
                "(`|---|---|---|---|`)."
            ),
        ))
        return result

    # Validate header column count
    header_cells = _parse_table_cells(table_lines[0])
    if len(header_cells) < 4:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=table_start + 1, finding_id="",
            kind="format", severity="Important",
            message=(
                f"triage table needs 4 columns (ID | Severity | Disposition | "
                f"Rationale); found {len(header_cells)}: {header_cells}"
            ),
        ))
        return result

    # Parse data rows
    seen_ids: set[str] = set()
    for idx, raw in enumerate(table_lines[2:], start=1):
        line_num = table_start + 2 + idx
        cells = _parse_table_cells(raw)
        if len(cells) < 4:
            result.violations.append(TriageViolation(
                path=str(critique_path), line=line_num, finding_id="",
                kind="format", severity="Important",
                message=f"triage row {idx}: {len(cells)} cells; expected 4",
            ))
            continue

        fid, severity, disposition, rationale = (c.strip() for c in cells[:4])
        if not fid or _cell_is_empty(fid):
            continue
        seen_ids.add(fid)

        normalized_disp = disposition.upper()
        if normalized_disp not in _ALLOWED_DISPOSITIONS:
            result.violations.append(TriageViolation(
                path=str(critique_path), line=line_num, finding_id=fid,
                kind="invalid-disposition", severity="Important",
                message=(
                    f"finding {fid}: disposition '{disposition}' not allowed. "
                    f"Use one of: {', '.join(sorted(_ALLOWED_DISPOSITIONS))}."
                ),
            ))
            continue

        result.dispositions[fid] = normalized_disp

        if normalized_disp in _RATIONALE_REQUIRED and _cell_is_empty(rationale):
            result.violations.append(TriageViolation(
                path=str(critique_path), line=line_num, finding_id=fid,
                kind="missing-rationale", severity="Important",
                message=(
                    f"finding {fid}: disposition '{normalized_disp}' "
                    f"requires non-empty rationale."
                ),
            ))

    # Findings in body without disposition rows
    missing_rows = [f for f in findings if f not in seen_ids]
    for fid in missing_rows:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=triage_start + 1, finding_id=fid,
            kind="missing-row", severity="Important",
            message=(
                f"finding {fid} declared in body but has no triage row. "
                f"Per TRI-1, every finding must have a disposition."
            ),
        ))

    # Verdict consistency
    expected = _expected_verdict(result.dispositions)
    result.expected_verdict = expected
    if declared and declared in _ALLOWED_VERDICTS and declared != expected:
        result.violations.append(TriageViolation(
            path=str(critique_path), line=triage_start + 1, finding_id="",
            kind="verdict-mismatch", severity="Important",
            message=(
                f"declared final verdict '{declared}' does not match "
                f"disposition pattern. Expected: '{expected}'. Pattern: "
                f"any ESCALATED -> BLOCKED; else any ACCEPTED-PENDING -> "
                f"NEEDS-FIXES; else CLEAN."
            ),
        ))

    return result


def _format_human(result: TriageResult) -> str:
    if result.carry_over_exempt:
        return (
            "Triage audit: slice is carry-over exempt "
            "(mission-brief.md predates TRI-1 release).\n"
        )

    if not result.violations:
        if result.declared_verdict:
            return (
                f"Triage audit: clean. Final verdict: "
                f"{result.declared_verdict} "
                f"({len(result.findings)} finding(s); "
                f"triaged by {result.triaged_by or 'unknown'}).\n"
            )
        return "Triage audit: clean (no findings).\n"

    out: list[str] = [f"{len(result.violations)} triage violation(s):\n\n"]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
            f"{f'finding {v.finding_id}' if v.finding_id else ''}\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="triage_audit",
        description="TRI-1 triage audit — user-owned triage discipline",
    )
    parser.add_argument(
        "target", type=Path,
        help="Slice folder (auto-finds critique.md inside) OR a critique.md file",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON (machine-readable)",
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    args = parser.parse_args(argv)

    target: Path = args.target
    critique_path = target / "critique.md" if target.is_dir() else target

    result = audit_critique_file(
        critique_path,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
