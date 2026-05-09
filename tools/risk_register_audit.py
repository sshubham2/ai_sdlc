"""Risk register audit (RR-1).

Parses `architecture/risk-register.md` in the H2-structured format and:
  - Validates required fields per risk (Likelihood, Impact, Status)
  - Validates allowed values per field
  - Detects duplicate risk IDs
  - Computes Score = Likelihood * Impact (low=1, medium=2, high=3 -> 1..9)
  - Computes Band (1-2 low, 3-4 medium, 6-9 high)
  - Sorts and filters for downstream consumers (/slice, /status)

Per RR-1 (methodology-changelog.md v0.12.0). The rule's purpose: turn the
risk register from freeform prose into ranked, sortable data so /slice can
make risk-first slice ordering mechanical (top-N open high-band risks
become candidates) and /status can surface the top-N concerns without a
human re-classifying every entry each time.

Format (H2-structured, matching BC-1 / TRI-1 conventions):

    ## R-1 — <title>

    **Likelihood**: low | medium | high
    **Impact**: low | medium | high
    **Status**: open | mitigating | retired | accepted
    **Reversibility**: cheap | expensive | irreversible            (optional)
    **Mitigation**: <text or spike ref>                             (optional)
    **Discovered**: slice-NNN-<name> (<YYYY-MM-DD>)                 (optional)
    **Notes**: <free text>                                          (optional)

The separator between the risk ID and the title is em-dash `—` (canonical
per slice-002 lessons-learned) OR single hyphen `-` (accepted alternate
form). Double-hyphen `## R-1 -- <title>` is NOT accepted — the regex
character class is single-character (em-dash or single hyphen).

Old table-format files (`| R1 | ... |`) yield zero risks with no violation
emitted — opt-in migration. Use --warn-legacy to surface a deprecation
hint when the file looks like the legacy format.

Usage:
    python -m tools.risk_register_audit <register.md>
    python -m tools.risk_register_audit <register.md> --json
    python -m tools.risk_register_audit <register.md> --filter-status open
    python -m tools.risk_register_audit <register.md> --filter-band high
    python -m tools.risk_register_audit <register.md> --sort score
    python -m tools.risk_register_audit <register.md> --top 3

Exit codes:
    0  clean (or empty register)
    1  violations
    2  usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

# H2 risk heading: "## R-1 — title" (em-dash separator, canonical) or
# "## R-1 - title" (single hyphen, accepted alternate). Double-hyphen
# "--" is NOT accepted — the regex character class [—\-] is single-character.
_RISK_HEADING_RE = re.compile(r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$")

# Field-line pattern (same as BC-1 / TRI-1)
_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z\s]*)\*\*\s*:\s*(.*?)\s*$")

# Required fields per risk
_REQUIRED_FIELDS: frozenset[str] = frozenset({"likelihood", "impact", "status"})

_ALLOWED_LEVELS: frozenset[str] = frozenset({"low", "medium", "high"})
_ALLOWED_STATUSES: frozenset[str] = frozenset({"open", "mitigating", "retired", "accepted"})
_ALLOWED_REVERSIBILITY: frozenset[str] = frozenset({"cheap", "expensive", "irreversible"})

_LEVEL_NUMERIC = {"low": 1, "medium": 2, "high": 3}

# Legacy table-row detection: line like "| R1 | text | something | ... |"
_LEGACY_ROW_RE = re.compile(r"^\s*\|\s*R-?\d+\s*\|")


@dataclass(frozen=True)
class Risk:
    risk_id: str
    title: str
    likelihood: str
    impact: str
    status: str
    score: int
    band: str
    reversibility: str
    mitigation: str
    discovered: str
    notes: str
    line: int

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class RiskViolation:
    path: str
    line: int
    risk_id: str
    kind: str    # "missing-field" | "invalid-value" | "duplicate-id" | "format" | "legacy-format"
    severity: str  # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    risks: list[Risk] = field(default_factory=list)
    violations: list[RiskViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        by_band: dict[str, int] = {"low": 0, "medium": 0, "high": 0}
        by_status: dict[str, int] = {s: 0 for s in _ALLOWED_STATUSES}
        for r in self.risks:
            by_band[r.band] += 1
            by_status[r.status] += 1
        open_high = [r.to_dict() for r in self.risks if r.status == "open" and r.band == "high"]
        return {
            "risks": [r.to_dict() for r in self.risks],
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "total": len(self.risks),
                "by_band": by_band,
                "by_status": by_status,
                "open_high_count": len(open_high),
                "open_high": open_high,
                "violation_count": len(self.violations),
            },
        }


def _band_for_score(score: int) -> str:
    if score <= 2:
        return "low"
    if score <= 4:
        return "medium"
    return "high"


def _looks_like_legacy(text: str) -> bool:
    """Heuristic: H2 risks absent but `| R1 |`-style rows present."""
    if _RISK_HEADING_RE.search("\n".join(text.splitlines())):
        return False
    for line in text.splitlines():
        if _LEGACY_ROW_RE.match(line):
            return True
    return False


def _parse_risks(text: str, path: str) -> tuple[list[Risk], list[RiskViolation]]:
    """Parse risks from the file text."""
    risks: list[Risk] = []
    violations: list[RiskViolation] = []
    lines = text.splitlines()

    # Locate H2 risk headings
    heading_positions: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        m = _RISK_HEADING_RE.match(line)
        if m:
            heading_positions.append((i, m.group(1), m.group(2)))

    seen_ids: dict[str, int] = {}

    for idx, (heading_line, risk_id, title) in enumerate(heading_positions):
        body_end = (
            heading_positions[idx + 1][0]
            if idx + 1 < len(heading_positions)
            else len(lines)
        )
        body_lines = lines[heading_line + 1:body_end]

        # Duplicate ID check
        if risk_id in seen_ids:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="duplicate-id", severity="Important",
                message=(
                    f"risk {risk_id} declared again at line "
                    f"{heading_line + 1} (first declared at line "
                    f"{seen_ids[risk_id]}). IDs must be unique."
                ),
            ))
            continue
        seen_ids[risk_id] = heading_line + 1

        fields_collected: dict[str, str] = {}
        for body_line in body_lines:
            m = _FIELD_RE.match(body_line)
            if m:
                key = m.group(1).strip().lower()
                value = m.group(2).strip()
                fields_collected[key] = value

        # Required-field check
        missing = _REQUIRED_FIELDS - set(fields_collected.keys())
        if missing:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="missing-field", severity="Important",
                message=(
                    f"risk {risk_id}: missing required field(s): "
                    f"{', '.join(sorted(missing))}. Required: "
                    f"{', '.join(sorted(_REQUIRED_FIELDS))}."
                ),
            ))
            continue

        likelihood = fields_collected["likelihood"].strip().lower()
        impact = fields_collected["impact"].strip().lower()
        status = fields_collected["status"].strip().lower()

        had_invalid = False
        if likelihood not in _ALLOWED_LEVELS:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="invalid-value", severity="Important",
                message=(
                    f"risk {risk_id}: likelihood '{likelihood}' not in "
                    f"{sorted(_ALLOWED_LEVELS)}."
                ),
            ))
            had_invalid = True
        if impact not in _ALLOWED_LEVELS:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="invalid-value", severity="Important",
                message=(
                    f"risk {risk_id}: impact '{impact}' not in "
                    f"{sorted(_ALLOWED_LEVELS)}."
                ),
            ))
            had_invalid = True
        if status not in _ALLOWED_STATUSES:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="invalid-value", severity="Important",
                message=(
                    f"risk {risk_id}: status '{status}' not in "
                    f"{sorted(_ALLOWED_STATUSES)}."
                ),
            ))
            had_invalid = True
        if had_invalid:
            continue

        reversibility = fields_collected.get("reversibility", "").strip().lower()
        if reversibility and reversibility not in _ALLOWED_REVERSIBILITY:
            violations.append(RiskViolation(
                path=path, line=heading_line + 1, risk_id=risk_id,
                kind="invalid-value", severity="Important",
                message=(
                    f"risk {risk_id}: reversibility '{reversibility}' not in "
                    f"{sorted(_ALLOWED_REVERSIBILITY)}."
                ),
            ))
            continue

        score = _LEVEL_NUMERIC[likelihood] * _LEVEL_NUMERIC[impact]
        band = _band_for_score(score)

        risks.append(Risk(
            risk_id=risk_id,
            title=title,
            likelihood=likelihood,
            impact=impact,
            status=status,
            score=score,
            band=band,
            reversibility=reversibility,
            mitigation=fields_collected.get("mitigation", ""),
            discovered=fields_collected.get("discovered", ""),
            notes=fields_collected.get("notes", ""),
            line=heading_line + 1,
        ))

    return risks, violations


def audit_register(
    register_path: Path,
    warn_legacy: bool = False,
) -> AuditResult:
    """Audit a risk-register.md file."""
    result = AuditResult()

    if not register_path.exists():
        return result  # missing file is silent — register may not exist yet

    text = register_path.read_text(encoding="utf-8")

    if warn_legacy and _looks_like_legacy(text):
        result.violations.append(RiskViolation(
            path=str(register_path), line=0, risk_id="",
            kind="legacy-format", severity="Important",
            message=(
                "risk-register.md uses the legacy `| R1 | ... |` table "
                "format. RR-1 (v0.12.0) introduced an H2-structured format "
                "with Likelihood/Impact/Status fields. Migrate to enable "
                "scoring + sorted output for /slice + /status."
            ),
        ))
        return result

    risks, violations = _parse_risks(text, str(register_path))
    result.risks = risks
    result.violations = violations
    return result


def filter_and_sort(
    result: AuditResult,
    filter_status: str | None = None,
    filter_band: str | None = None,
    sort_by: str = "score",
    top: int | None = None,
) -> list[Risk]:
    """Apply filter + sort to the audit result; return list of risks."""
    risks = list(result.risks)
    if filter_status:
        risks = [r for r in risks if r.status == filter_status]
    if filter_band:
        risks = [r for r in risks if r.band == filter_band]

    if sort_by == "score":
        # Score desc, then id asc for stable ordering
        risks.sort(key=lambda r: (-r.score, r.risk_id))
    elif sort_by == "band":
        # high > medium > low, then score desc
        band_order = {"high": 0, "medium": 1, "low": 2}
        risks.sort(key=lambda r: (band_order.get(r.band, 99), -r.score, r.risk_id))
    elif sort_by == "id":
        risks.sort(key=lambda r: r.risk_id)

    if top is not None and top > 0:
        risks = risks[:top]
    return risks


def _format_human(result: AuditResult, view: list[Risk]) -> str:
    if result.violations:
        out: list[str] = [f"{len(result.violations)} risk-register violation(s):\n\n"]
        for v in result.violations:
            out.append(
                f"  [{v.severity}] {v.path}:{v.line} ({v.kind}) "
                f"{f'risk {v.risk_id}' if v.risk_id else ''}\n"
                f"    {v.message}\n\n"
            )
        return "".join(out)

    if not view:
        return "Risk register: 0 risks (or filter excluded all).\n"

    lines: list[str] = [f"Risk register: {len(view)} risk(s):\n\n"]
    for r in view:
        lines.append(
            f"  [{r.band:>6}] {r.risk_id} score={r.score} ({r.likelihood}x{r.impact}) "
            f"status={r.status} - {r.title}\n"
        )
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="risk_register_audit",
        description="RR-1 risk register audit + scoring",
    )
    parser.add_argument(
        "register", type=Path,
        help="Path to risk-register.md (default: architecture/risk-register.md)",
        nargs="?",
        default=Path("architecture/risk-register.md"),
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--warn-legacy", action="store_true",
        help="Emit a deprecation violation for legacy table format",
    )
    parser.add_argument(
        "--filter-status",
        choices=sorted(_ALLOWED_STATUSES),
        help="Show only risks with this status",
    )
    parser.add_argument(
        "--filter-band",
        choices=sorted({"low", "medium", "high"}),
        help="Show only risks in this band",
    )
    parser.add_argument(
        "--sort", choices=["score", "band", "id"], default="score",
        help="Sort order (default: score)",
    )
    parser.add_argument(
        "--top", type=int, default=None,
        help="Limit output to first N risks after sort",
    )
    args = parser.parse_args(argv)

    result = audit_register(args.register, warn_legacy=args.warn_legacy)

    view = filter_and_sort(
        result,
        filter_status=args.filter_status,
        filter_band=args.filter_band,
        sort_by=args.sort,
        top=args.top,
    )

    if args.json:
        out = result.to_dict()
        out["view"] = [r.to_dict() for r in view]
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result, view))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
