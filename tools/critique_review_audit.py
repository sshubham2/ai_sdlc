"""Critique-review structural audit (DR-1).

Validates that a slice's `critique-review.md` (produced by the
critique-review meta-Critic agent via the `/critique-review` skill)
has the required structure: 4 H2 sections + Reviewed-by / Date /
First-Critic verdict / Dual-review verdict header fields.

Per DR-1 (methodology-changelog.md v0.17.0). The rule's purpose: ensure
the meta-Critic's output is structurally well-formed so the user's
TRI-1 triage step can reconcile it with the first Critic's findings
without parsing surprises.

Required sections:
  - Confirmed findings
  - Suspicious findings
  - Missed findings
  - Severity adjustments

Required header fields:
  - Reviewed by
  - Date
  - First-Critic verdict (one of CLEAN | NEEDS-FIXES | BLOCKED)
  - Dual-review verdict (one of ACCEPT | ADJUST | EXTEND)

NFR-1 carry-over: slices whose mission-brief.md mtime predates
`_DR_1_RELEASE_DATE` are exempt automatically.

Usage:
    python -m tools.critique_review_audit <slice-folder>
    python -m tools.critique_review_audit <critique-review.md>
    python -m tools.critique_review_audit --json <slice-folder>
    python -m tools.critique_review_audit --no-carry-over <slice-folder>

Exit codes:
    0  clean (or carry-over exempt)
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
_DR_1_RELEASE_DATE: date = date(2026, 5, 6)

# Required H2 section headings (case-insensitive)
_REQUIRED_SECTIONS: tuple[str, ...] = (
    "confirmed findings",
    "suspicious findings",
    "missed findings",
    "severity adjustments",
)

# Required header fields
_REQUIRED_HEADER_FIELDS: tuple[str, ...] = (
    "reviewed by",
    "date",
    "first-critic verdict",
    "dual-review verdict",
)

# Allowed values for each verdict field
_ALLOWED_FIRST_VERDICTS: frozenset[str] = frozenset({"CLEAN", "NEEDS-FIXES", "BLOCKED"})
_ALLOWED_DUAL_VERDICTS: frozenset[str] = frozenset({"ACCEPT", "ADJUST", "EXTEND"})

# Field-line pattern (matches **Name**: value with optional inline parenthetical)
_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z\s\-]*)\*\*\s*:\s*(.*?)\s*$")

# H2 heading pattern
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")


@dataclass(frozen=True)
class CRViolation:
    path: str
    line: int
    kind: str       # "missing-section" | "missing-field" | "invalid-verdict" |
                    # "no-file"
    severity: str   # always "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    sections_found: list[str] = field(default_factory=list)
    fields_found: dict[str, str] = field(default_factory=dict)
    first_verdict: str = ""
    dual_verdict: str = ""
    violations: list[CRViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "sections_found": list(self.sections_found),
            "fields_found": dict(self.fields_found),
            "first_verdict": self.first_verdict,
            "dual_verdict": self.dual_verdict,
            "violations": [v.to_dict() for v in self.violations],
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "violation_count": len(self.violations),
                "consistent": len(self.violations) == 0,
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    """True if the slice was authored before DR-1 (mtime carry-over)."""
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _DR_1_RELEASE_DATE


def audit_review_file(
    review_path: Path,
    skip_if_carry_over: bool = True,
) -> AuditResult:
    """Audit a critique-review.md file against DR-1."""
    result = AuditResult()

    if not review_path.exists():
        result.violations.append(CRViolation(
            path=str(review_path), line=0,
            kind="no-file", severity="Important",
            message=f"critique-review.md not found: {review_path}",
        ))
        return result

    if skip_if_carry_over:
        slice_folder = review_path.parent
        if _slice_is_carry_over(slice_folder):
            result.carry_over_exempt = True
            return result

    text = review_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Collect H2 section headings (lowercased) and field lines (collect from
    # the prologue before the first H2)
    sections_lower: list[str] = []
    fields_lower: dict[str, str] = {}
    first_h2_line: int | None = None

    for i, raw in enumerate(lines):
        m_h2 = _H2_RE.match(raw)
        if m_h2:
            sections_lower.append(m_h2.group(1).strip().lower())
            if first_h2_line is None:
                first_h2_line = i
            continue
        # Only collect fields above the first H2 (the prologue)
        if first_h2_line is None:
            m_field = _FIELD_RE.match(raw)
            if m_field:
                key = m_field.group(1).strip().lower()
                value = m_field.group(2).strip()
                fields_lower[key] = value

    result.sections_found = sections_lower
    result.fields_found = fields_lower

    # Required sections
    for section in _REQUIRED_SECTIONS:
        if not any(section in s for s in sections_lower):
            result.violations.append(CRViolation(
                path=str(review_path), line=first_h2_line or 0,
                kind="missing-section", severity="Important",
                message=(
                    f"required section `## {section.title()}` is missing. "
                    f"Per DR-1, critique-review.md must include all 4 "
                    f"required sections: "
                    f"{', '.join(s.title() for s in _REQUIRED_SECTIONS)}."
                ),
            ))

    # Required header fields
    for field_name in _REQUIRED_HEADER_FIELDS:
        if field_name not in fields_lower:
            result.violations.append(CRViolation(
                path=str(review_path), line=0,
                kind="missing-field", severity="Important",
                message=(
                    f"required header field `**{field_name.title()}**:` is "
                    f"missing or appears below the first H2 (must be in "
                    f"prologue). Required fields: "
                    f"{', '.join(f.title() for f in _REQUIRED_HEADER_FIELDS)}."
                ),
            ))

    # Verdict values
    first = fields_lower.get("first-critic verdict", "").strip().upper()
    dual = fields_lower.get("dual-review verdict", "").strip().upper()
    result.first_verdict = first
    result.dual_verdict = dual

    if first and first not in _ALLOWED_FIRST_VERDICTS:
        result.violations.append(CRViolation(
            path=str(review_path), line=0,
            kind="invalid-verdict", severity="Important",
            message=(
                f"First-Critic verdict '{first}' not in "
                f"{sorted(_ALLOWED_FIRST_VERDICTS)}. The first-Critic "
                f"verdict mirrors `Result:` from critique.md (post-TRI-1 "
                f"rename per v0.11.0)."
            ),
        ))

    if dual and dual not in _ALLOWED_DUAL_VERDICTS:
        result.violations.append(CRViolation(
            path=str(review_path), line=0,
            kind="invalid-verdict", severity="Important",
            message=(
                f"Dual-review verdict '{dual}' not in "
                f"{sorted(_ALLOWED_DUAL_VERDICTS)}. ACCEPT (first Critic "
                f"sound), ADJUST (existing findings need modification), "
                f"or EXTEND (missed findings surface)."
            ),
        ))

    return result


def _format_human(result: AuditResult) -> str:
    if result.carry_over_exempt:
        return (
            "Critique-review audit: slice is carry-over exempt "
            "(mission-brief.md predates DR-1 release).\n"
        )

    if not result.violations:
        return (
            f"Critique-review audit: clean. "
            f"First-Critic verdict: {result.first_verdict}; "
            f"Dual-review verdict: {result.dual_verdict}.\n"
        )

    out: list[str] = [f"{len(result.violations)} critique-review violation(s):\n\n"]
    for v in result.violations:
        out.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind})\n"
            f"    {v.message}\n\n"
        )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="critique_review_audit",
        description="DR-1 critique-review structural audit",
    )
    parser.add_argument(
        "target", type=Path,
        help="Slice folder (auto-finds critique-review.md inside) OR a critique-review.md file",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    args = parser.parse_args(argv)

    target: Path = args.target
    review_path = target / "critique-review.md" if target.is_dir() else target

    result = audit_review_file(
        review_path,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
