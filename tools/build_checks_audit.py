"""Build-checks audit (BC-1).

Reads ``architecture/build-checks.md`` (project) and ``~/.claude/build-checks.md``
(global) and surfaces rules applicable to the current slice based on:
  - ``Applies to: always: true`` (always applies), OR
  - ``Applies to: <comma-separated globs>`` matched against --changed-files, OR
  - ``Trigger keywords: <comma-separated words>`` matched against
    mission-brief.md + design.md text via case-insensitive **word-boundary**
    regex (slice-005, ADR-004 — was bare substring pre-slice-005).

Optional per-rule ``Trigger anchors:`` field (slice-005, ADR-004): comma-
separated subset of ``Trigger keywords``. When specified, the rule fires on
the keyword path only when at least one anchor matches (word-boundary).
When absent, behavior preserves the legacy "any keyword match fires"
semantic (modulo the substring -> word-boundary tightening). Anchors that
aren't in trigger_keywords yield an ``anchor-not-in-keywords`` parse
violation (Important severity).

Per BC-1 (methodology-changelog.md v0.10.0). The rule's purpose: close the
lessons-learned -> builder feedback loop by giving recurring patterns a
formal home that `/build-slice` reads at pre-finish.

Promotion in v1 is manual at `/reflect` Step 5b — when a recurring pattern
emerges across slices, the user appends a rule to build-checks.md. Auto-
detection is deferred to v2 (likely as a `/critic-calibrate` extension).

NFR-1 carry-over: slices whose mission-brief.md mtime predates the rule's
release date (_BC_1_RELEASE_DATE) are exempt automatically.

v1 scope:
  - Parses H2 rules whose heading starts with "BC-"
  - Validates required fields: Severity, Applies to, Check
  - Surfaces applicable rules with severity, title, check, rationale,
    validation_hint
  - Does NOT auto-verify the check (human/AI builder addresses)

Usage:
    python -m tools.build_checks_audit --slice <slice-folder> [options]
    python -m tools.build_checks_audit --slice <slice-folder> --changed-files <files...>
    python -m tools.build_checks_audit --slice <slice-folder> --json
    python -m tools.build_checks_audit --slice <slice-folder> --no-carry-over
    python -m tools.build_checks_audit --slice <slice-folder> \\
        --project-checks <path> --global-checks <path>

Exit codes:
    0  success — applicable rules surfaced (or none apply)
    1  format violations in build-checks.md (malformed rule)
    2  usage error / unrecoverable failure
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path

# Date this rule shipped. Slices with mission-brief.md mtime BEFORE this date
# are carry-over exempt automatically. NFR-1 pattern.
_BC_1_RELEASE_DATE: date = date(2026, 5, 6)

# Rule heading pattern: H2 starting with "BC-" prefix.
# Examples: "## BC-PROJ-1 — Title", "## BC-GLOBAL-2 - Title"
_RULE_HEADING_RE = re.compile(r"^##\s+(BC-[A-Z0-9]+(?:-\d+)?)\s+[—\-]\s+(.+?)\s*$")

# Field-line pattern: "**FieldName**: value"
_FIELD_RE = re.compile(r"^\*\*([A-Za-z][A-Za-z\s]*)\*\*\s*:\s*(.*?)\s*$")

# Required fields per rule
_REQUIRED_FIELDS: frozenset[str] = frozenset({"severity", "applies to", "check"})

# Allowed severity values (case-insensitive comparison)
_ALLOWED_SEVERITIES: frozenset[str] = frozenset({"critical", "important"})

# "Applies to" sentinel meaning "always applies regardless of files"
_ALWAYS_SENTINEL_RE = re.compile(r"^\s*always\s*:\s*true\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class BuildCheckRule:
    """A parsed rule from build-checks.md."""
    source: str          # "project" | "global"
    rule_id: str         # e.g., "BC-PROJ-1"
    title: str           # human-readable title
    severity: str        # "Critical" | "Important"
    applies_to: tuple[str, ...]  # globs OR ("always",) sentinel
    trigger_keywords: tuple[str, ...]  # lowercased keywords
    trigger_anchors: tuple[str, ...]  # lowercased anchor subset (slice-005)
    check: str           # what the builder must verify
    rationale: str       # why this is permanent (may be empty)
    validation_hint: str  # how to verify (may be empty)
    promoted_from: str   # provenance (may be empty)
    line: int            # 1-based line where rule heading appears

    def to_dict(self) -> dict:
        d = asdict(self)
        d["applies_to"] = list(self.applies_to)
        d["trigger_keywords"] = list(self.trigger_keywords)
        d["trigger_anchors"] = list(self.trigger_anchors)
        return d


@dataclass(frozen=True)
class BuildCheckViolation:
    """A finding emitted by the audit (parse error, not applicability)."""
    path: str
    line: int
    rule_id: str  # may be empty for file-level errors
    kind: str     # "missing-field" | "invalid-severity" | "parse-error"
    severity: str  # always "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    """Audit output: rules applicable to this slice + any parse violations."""
    applicable: list[BuildCheckRule] = field(default_factory=list)
    skipped: list[BuildCheckRule] = field(default_factory=list)
    violations: list[BuildCheckViolation] = field(default_factory=list)
    carry_over_exempt: bool = False

    def to_dict(self) -> dict:
        return {
            "applicable": [r.to_dict() for r in self.applicable],
            "skipped": [r.to_dict() for r in self.skipped],
            "violations": [v.to_dict() for v in self.violations],
            "carry_over_exempt": self.carry_over_exempt,
            "summary": {
                "applicable_count": len(self.applicable),
                "skipped_count": len(self.skipped),
                "violation_count": len(self.violations),
                "critical_applicable": sum(
                    1 for r in self.applicable if r.severity.lower() == "critical"
                ),
            },
        }


def _slice_is_carry_over(slice_folder: Path) -> bool:
    """True if the slice was authored before BC-1 (mtime carry-over)."""
    brief = slice_folder / "mission-brief.md"
    if not brief.exists():
        return False
    mtime_date = datetime.fromtimestamp(brief.stat().st_mtime).date()
    return mtime_date < _BC_1_RELEASE_DATE


def _matches_glob(path: str, pattern: str) -> bool:
    """Glob match with `**` support (multi-segment) and `*` (single-segment).

    Patterns:
      - `src/api/**`        matches `src/api/foo.py`, `src/api/v1/foo.py`
      - `src/api/*.py`      matches `src/api/foo.py` (single segment only)
      - `**/*upload*.py`    matches anywhere
      - `src/services/*upload*.py` matches `src/services/file_upload.py`
    """
    norm_path = path.replace("\\", "/")
    norm_pattern = pattern.replace("\\", "/")
    if norm_path == norm_pattern:
        return True
    # Tokenize on `**` first so we can map ** -> .* (segment-greedy).
    # Then within each token map * -> [^/]* (single-segment).
    parts = norm_pattern.split("**")
    regex_parts: list[str] = []
    for part in parts:
        escaped = re.escape(part).replace(r"\*", "[^/]*")
        regex_parts.append(escaped)
    regex = ".*".join(regex_parts)
    return re.fullmatch(regex, norm_path) is not None


def _parse_rules(
    text: str,
    source: str,
    path: str,
) -> tuple[list[BuildCheckRule], list[BuildCheckViolation]]:
    """Parse rules + violations from build-checks.md text.

    Splits on H2 headings starting with "BC-". Lines between an H2 and the
    next H2 (or EOF) form a rule's body.
    """
    rules: list[BuildCheckRule] = []
    violations: list[BuildCheckViolation] = []
    lines = text.splitlines()

    # Find all rule heading positions
    heading_positions: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        m = _RULE_HEADING_RE.match(line)
        if m:
            heading_positions.append((i, m.group(1), m.group(2)))

    for idx, (heading_line, rule_id, title) in enumerate(heading_positions):
        body_end = heading_positions[idx + 1][0] if idx + 1 < len(heading_positions) else len(lines)
        body_lines = lines[heading_line + 1:body_end]

        fields_collected: dict[str, str] = {}
        for body_line in body_lines:
            m = _FIELD_RE.match(body_line)
            if m:
                key = m.group(1).strip().lower()
                value = m.group(2).strip()
                fields_collected[key] = value

        # Validate required fields
        missing = _REQUIRED_FIELDS - set(fields_collected.keys())
        if missing:
            violations.append(BuildCheckViolation(
                path=path, line=heading_line + 1, rule_id=rule_id,
                kind="missing-field", severity="Important",
                message=(
                    f"rule {rule_id}: missing required field(s): "
                    f"{', '.join(sorted(missing))}. Required: "
                    f"{', '.join(sorted(_REQUIRED_FIELDS))}."
                ),
            ))
            continue

        severity_raw = fields_collected.get("severity", "")
        if severity_raw.lower() not in _ALLOWED_SEVERITIES:
            violations.append(BuildCheckViolation(
                path=path, line=heading_line + 1, rule_id=rule_id,
                kind="invalid-severity", severity="Important",
                message=(
                    f"rule {rule_id}: severity '{severity_raw}' not allowed. "
                    f"Use one of: {', '.join(sorted(_ALLOWED_SEVERITIES))} "
                    f"(case-insensitive)."
                ),
            ))
            continue

        # Normalize severity to title case
        severity = severity_raw.title()

        applies_to_raw = fields_collected.get("applies to", "")
        if _ALWAYS_SENTINEL_RE.match(applies_to_raw):
            applies_to: tuple[str, ...] = ("always",)
        else:
            applies_to = tuple(
                glob.strip() for glob in applies_to_raw.split(",")
                if glob.strip()
            )

        trigger_raw = fields_collected.get("trigger keywords", "")
        trigger_keywords = tuple(
            kw.strip().lower() for kw in trigger_raw.split(",") if kw.strip()
        )

        # slice-005: optional Trigger anchors field (subset of Trigger keywords).
        # Validation: each anchor must appear in trigger_keywords; an anchor
        # outside the keyword vocabulary emits anchor-not-in-keywords (per ADR-004).
        # Storage: all parsed anchors retained as-is (per Critic m1 — invalid
        # anchors silently never match because matched-set is a subset of
        # trigger_keywords; the violation surfaces via the parse-violation
        # channel, not by silently dropping the anchor).
        anchors_raw = fields_collected.get("trigger anchors", "")
        seen_anchors: set[str] = set()
        anchors_list: list[str] = []
        for raw in anchors_raw.split(","):
            normalized = raw.strip().lower()
            if not normalized or normalized in seen_anchors:
                continue
            seen_anchors.add(normalized)
            anchors_list.append(normalized)
        trigger_anchors = tuple(anchors_list)

        for anchor in trigger_anchors:
            if anchor not in trigger_keywords:
                violations.append(BuildCheckViolation(
                    path=path, line=heading_line + 1, rule_id=rule_id,
                    kind="anchor-not-in-keywords", severity="Important",
                    message=(
                        f"rule {rule_id}: Trigger anchor '{anchor}' is not in "
                        f"Trigger keywords {sorted(trigger_keywords)}. Anchors "
                        f"must be a subset of the keyword vocabulary."
                    ),
                ))

        rules.append(BuildCheckRule(
            source=source,
            rule_id=rule_id,
            title=title,
            severity=severity,
            applies_to=applies_to,
            trigger_keywords=trigger_keywords,
            trigger_anchors=trigger_anchors,
            check=fields_collected.get("check", ""),
            rationale=fields_collected.get("rationale", ""),
            validation_hint=fields_collected.get("validation hint", ""),
            promoted_from=fields_collected.get("promoted from", ""),
            line=heading_line + 1,
        ))

    return rules, violations


def _rule_applies(
    rule: BuildCheckRule,
    changed_files: list[str],
    slice_text: str,
) -> bool:
    """Decide whether a rule applies to the current slice.

    Applicability is OR over the three signals:
      1. ``Applies to: always: true`` -> always applies
      2. Any glob in ``Applies to`` matches any of ``changed_files``
      3. Keyword path (slice-005, ADR-004): keywords are matched against
         ``slice_text`` via case-insensitive **word-boundary** regex
         (``\\b{kw}\\b``), not substring. If the rule defines
         ``Trigger anchors``, the rule fires only when at least one anchor
         (subset of ``Trigger keywords``) matches; otherwise any keyword
         match fires (legacy behavior + word-boundary tightening). Compound
         keywords with hyphens (e.g., ``code-block``) match cleanly because
         word-boundaries land at the start and end of the literal pattern.
    """
    if rule.applies_to == ("always",):
        return True

    for pattern in rule.applies_to:
        for changed in changed_files:
            if _matches_glob(changed, pattern):
                return True

    if rule.trigger_keywords and slice_text:
        haystack = slice_text.lower()
        matched = {
            kw for kw in rule.trigger_keywords
            if re.search(rf"\b{re.escape(kw)}\b", haystack)
        }
        if not matched:
            return False
        if rule.trigger_anchors:
            return any(a in matched for a in rule.trigger_anchors)
        return True

    return False


def _read_slice_text(slice_folder: Path) -> str:
    """Concatenate mission-brief.md + design.md text for keyword matching."""
    parts: list[str] = []
    for fname in ("mission-brief.md", "design.md"):
        path = slice_folder / fname
        if path.exists():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def audit_slice(
    slice_folder: Path,
    project_checks: Path | None = None,
    global_checks: Path | None = None,
    changed_files: list[str] | None = None,
    skip_if_carry_over: bool = True,
) -> AuditResult:
    """Audit a slice against project + global build-checks.

    Args:
        slice_folder: path to the slice folder (must contain mission-brief.md
            for carry-over check; design.md for keyword match)
        project_checks: path to project build-checks.md (defaults to
            <repo>/architecture/build-checks.md, where <repo> is the slice
            folder's two-grandparents-up — typical layout)
        global_checks: path to global build-checks.md (defaults to
            ~/.claude/build-checks.md)
        changed_files: list of files this slice changed (for glob match);
            empty list means glob match never fires (keyword-only)
        skip_if_carry_over: if True, slices with pre-rule mission-brief.md
            mtime get an empty result (carry-over exempt)
    """
    result = AuditResult()
    changed_files = changed_files or []

    if skip_if_carry_over and _slice_is_carry_over(slice_folder):
        result.carry_over_exempt = True
        return result

    slice_text = _read_slice_text(slice_folder)

    # Project-level build-checks
    if project_checks is None:
        # Heuristic: <slice-folder> is typically architecture/slices/slice-NNN-x;
        # project-checks lives at architecture/build-checks.md (sibling of slices/).
        project_checks = slice_folder.parent.parent / "build-checks.md"

    if project_checks.exists():
        rules, violations = _parse_rules(
            project_checks.read_text(encoding="utf-8"),
            source="project",
            path=str(project_checks),
        )
        result.violations.extend(violations)
        for r in rules:
            if _rule_applies(r, changed_files, slice_text):
                result.applicable.append(r)
            else:
                result.skipped.append(r)

    # Global build-checks
    if global_checks is None:
        global_checks = Path.home() / ".claude" / "build-checks.md"

    if global_checks.exists():
        rules, violations = _parse_rules(
            global_checks.read_text(encoding="utf-8"),
            source="global",
            path=str(global_checks),
        )
        result.violations.extend(violations)
        for r in rules:
            if _rule_applies(r, changed_files, slice_text):
                result.applicable.append(r)
            else:
                result.skipped.append(r)

    return result


def _format_human(result: AuditResult) -> str:
    if result.carry_over_exempt:
        return (
            "Build-checks audit: slice is carry-over exempt "
            "(mission-brief.md predates BC-1 release).\n"
        )

    out: list[str] = []

    if result.violations:
        out.append(f"{len(result.violations)} build-checks parse violation(s):\n\n")
        for v in result.violations:
            out.append(
                f"  [{v.severity}] {v.path}:{v.line} ({v.kind})\n"
                f"    {v.message}\n\n"
            )

    if not result.applicable:
        out.append("No build-checks rules apply to this slice.\n")
        return "".join(out)

    critical_count = sum(
        1 for r in result.applicable if r.severity.lower() == "critical"
    )
    out.append(
        f"{len(result.applicable)} build-checks rule(s) apply to this slice "
        f"({critical_count} Critical):\n\n"
    )
    for r in result.applicable:
        out.append(
            f"  [{r.severity}] {r.rule_id} ({r.source}) — {r.title}\n"
            f"    Check: {r.check}\n"
        )
        if r.validation_hint:
            out.append(f"    Validation hint: {r.validation_hint}\n")
        out.append("\n")

    if critical_count > 0:
        out.append(
            "Per BC-1, Critical rules MUST be addressed before "
            "/build-slice declares the slice done. Important rules surface "
            "here for builder review; defer-with-rationale is allowed.\n"
        )

    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_checks_audit",
        description="BC-1 build-checks audit — surface applicable rules at /build-slice",
    )
    parser.add_argument(
        "--slice", type=Path, required=True,
        help="Path to the slice folder (containing mission-brief.md + design.md)",
    )
    parser.add_argument(
        "--changed-files", nargs="*", default=None,
        help="Files changed by this slice (for Applies-to glob matching)",
    )
    parser.add_argument(
        "--project-checks", type=Path, default=None,
        help=(
            "Path to project build-checks.md (default: "
            "<repo>/architecture/build-checks.md)"
        ),
    )
    parser.add_argument(
        "--global-checks", type=Path, default=None,
        help="Path to global build-checks.md (default: ~/.claude/build-checks.md)",
    )
    parser.add_argument(
        "--no-carry-over", action="store_true",
        help="Disable mtime-based carry-over exemption",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output result as JSON (machine-readable)",
    )
    args = parser.parse_args(argv)

    slice_folder: Path = args.slice
    if not slice_folder.exists():
        sys.stderr.write(f"slice folder not found: {slice_folder}\n")
        return 2

    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=args.project_checks,
        global_checks=args.global_checks,
        changed_files=args.changed_files,
        skip_if_carry_over=not args.no_carry_over,
    )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    # Exit 1 only on parse violations (malformed build-checks.md).
    # Applicable rules are informational, not failures — the human/AI builder
    # addresses them.
    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
