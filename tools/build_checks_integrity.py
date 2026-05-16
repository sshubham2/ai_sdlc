"""Build-checks integrity gate (BCI-1).

Per **BCI-1** (`methodology-changelog.md` v0.44.0; slice-030A; ADR-028 + ADR-029).

`/reflect` Step 5b ("promote a recurring lesson to a build-checks rule") is
LLM-executed prose with NO deterministic promotion function (slice-030A B2 /
ADR-029). R-4 witnessed both `architecture/build-checks.md` and
`~/.claude/build-checks.md` silently truncated to only the last-promoted rule.
There is no deterministic *source* to fix; the only sound control for a
non-deterministic step is a deterministic gate that detects the invariant
violation downstream.

BCI-1 is that gate. It derives the expected canonical rule set by parsing the
**git-tracked** canonical fixtures
(`tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md`)
via `tools.build_checks_audit._parse_rules` (read-only — NO BC-1 anchor /
applicability semantics change), then asserts the **live** build-checks files
match on **full per-rule structural identity**:

    (rule_id, severity, applies_to, trigger_keywords,
     trigger_anchors, negative_anchors)  +  non-empty `check`

NOT rule-ID-set-only (slice-030A meta-M-add-2: an ID-only or 2-tuple check
passes a coverage-degraded file — correct headings but wrong/empty anchors or
a downgraded severity — re-opening R-4's substance).

Semantics (slice-030A meta-M3, refined):
  - The tracked canonical fixtures MUST exist (they are the oracle) — absent
    fixture ⇒ exit 2 (usage error: the repo is malformed, not vault drift).
  - `~/.claude/build-checks.md` **absent** (file does not exist) ⇒ WARN,
    exit 0. The global file is untracked and environment-dependent; a machine
    that simply hasn't installed it must not HALT `/build-slice`. The message
    names it so the user can install it for full global BC-1 coverage.
  - Any live file **present but non-conformant — including empty / missing
    rules / any structural-field mismatch** ⇒ HALT, exit 1, with an
    attributed message: "LOCAL VAULT DRIFT — reconstruct from <fixture>;
    this is NOT a slice regression". (An *empty* present global file is
    non-conformant, NOT "absent" — it routes to HALT, so R-4-global is not
    silently reopened.)
  - The project `architecture/build-checks.md` absent ⇒ HALT (exit 1): it is
    the core BC-1 gate surface; its absence is a coverage degradation, not an
    optional-install condition.

Wiring (slice-030A, 2 points — the shippability-catalog-row wiring is 030B):
  - `/build-slice` Step 6 pre-finish (non-opt-out audit-enforced gate).
  - `/reflect` Step 5b fail-loud post-write instruction (run after promotion).

Usage:
    python -m tools.build_checks_integrity                 # --check-live (default)
    python -m tools.build_checks_integrity --check-live
    python -m tools.build_checks_integrity --json
    python -m tools.build_checks_integrity --root <repo-root>

Exit codes:
    0  conformant  (OR global-file-absent WARN — distinct stdout message)
    1  LOCAL VAULT DRIFT — a present live file diverges (incl. empty /
       missing rules / structural-field mismatch) OR project file absent
    2  usage error (canonical fixture missing/unreadable, parse failure,
       root unresolvable)
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout
from tools.build_checks_audit import BuildCheckRule, _parse_rules

_PROJECT_FIXTURE_REL = (
    "tests/methodology/fixtures/build_checks/canonical_project_checks.md"
)
_GLOBAL_FIXTURE_REL = (
    "tests/methodology/fixtures/build_checks/canonical_global_checks.md"
)
_PROJECT_LIVE_REL = "architecture/build-checks.md"

_ATTRIB = (
    "LOCAL VAULT DRIFT — reconstruct from {fixture}; "
    "this is NOT a slice regression"
)


def _identity(rule: BuildCheckRule) -> tuple:
    """Full per-rule structural identity (meta-M-add-2 — NOT rule-ID-only)."""
    return (
        rule.rule_id,
        rule.severity,
        rule.applies_to,
        rule.trigger_keywords,
        rule.trigger_anchors,
        rule.negative_anchors,
    )


@dataclass
class CheckResult:
    status: str = "conformant"          # conformant | drift | warn | usage
    exit_code: int = 0
    warnings: list[str] = field(default_factory=list)
    divergences: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "warnings": self.warnings,
            "divergences": self.divergences,
        }


def _compare_surface(
    surface: str,
    fixture_path: Path,
    live_path: Path,
    result: CheckResult,
) -> None:
    """Compare one (fixture, live) surface; mutate result in place."""
    if not fixture_path.exists():
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            f"{surface}: canonical fixture missing at {fixture_path} — the "
            f"tracked oracle is absent; repo is malformed (not vault drift)."
        )
        return

    fixture_rules, fixture_viols = _parse_rules(
        fixture_path.read_text(encoding="utf-8"),
        source=surface,
        path=str(fixture_path),
    )
    if fixture_viols:
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            f"{surface}: canonical fixture {fixture_path} itself emits parse "
            f"violations {[(v.rule_id, v.kind) for v in fixture_viols]} — "
            f"fixture is the oracle and must be clean."
        )
        return
    fixture_by_id = {r.rule_id: _identity(r) for r in fixture_rules}
    fixture_checks = {r.rule_id: r.check.strip() for r in fixture_rules}

    attributed = _ATTRIB.format(fixture=fixture_path)

    if not live_path.exists():
        if surface == "global":
            # meta-M3: absent global file is an optional-install condition,
            # NOT vault drift. WARN, do not HALT.
            result.warnings.append(
                f"global build-checks file absent at {live_path} — install "
                f"it (reconstruct from {fixture_path}) for full global BC-1 "
                f"coverage. This is a WARN, not a slice regression."
            )
            return
        # project surface absent = core-gate coverage degradation = HALT
        result.status = "drift"
        result.exit_code = 1
        result.divergences.append(
            f"project build-checks file absent at {live_path} — {attributed}"
        )
        return

    live_rules, live_viols = _parse_rules(
        live_path.read_text(encoding="utf-8"),
        source=surface,
        path=str(live_path),
    )
    live_by_id = {r.rule_id: _identity(r) for r in live_rules}
    live_checks = {r.rule_id: r.check.strip() for r in live_rules}

    surface_drift: list[str] = []

    if live_viols:
        surface_drift.append(
            f"{surface}: live file emits parse violations "
            f"{[(v.rule_id, v.kind) for v in live_viols]}"
        )

    missing = sorted(set(fixture_by_id) - set(live_by_id))
    extra = sorted(set(live_by_id) - set(fixture_by_id))
    if missing:
        surface_drift.append(
            f"{surface}: live file MISSING canonical rule(s) {missing} "
            f"(present-but-truncated/empty ⇒ HALT, meta-M3)"
        )
    if extra:
        surface_drift.append(
            f"{surface}: live file has NON-canonical rule(s) {extra}"
        )

    for rid in sorted(set(fixture_by_id) & set(live_by_id)):
        if live_by_id[rid] != fixture_by_id[rid]:
            surface_drift.append(
                f"{surface}: rule {rid} structural-identity mismatch\n"
                f"      fixture={fixture_by_id[rid]}\n"
                f"      live   ={live_by_id[rid]}"
            )
        if not live_checks.get(rid):
            surface_drift.append(
                f"{surface}: rule {rid} has an empty `Check` body "
                f"(non-empty check is part of the canonical invariant)"
            )

    if surface_drift:
        result.status = "drift"
        result.exit_code = 1
        for d in surface_drift:
            result.divergences.append(d)
        result.divergences.append(f"  → {attributed}")


def check_live(root: Path) -> CheckResult:
    """Assert live build-checks files match the tracked canonical fixtures."""
    result = CheckResult()

    _compare_surface(
        "project",
        root / _PROJECT_FIXTURE_REL,
        root / _PROJECT_LIVE_REL,
        result,
    )
    # Usage error on the project fixture short-circuits — repo malformed.
    if result.status == "usage":
        return result

    _compare_surface(
        "global",
        root / _GLOBAL_FIXTURE_REL,
        Path.home() / ".claude" / "build-checks.md",
        result,
    )

    if result.status == "usage":
        return result
    if result.status == "drift":
        result.exit_code = 1
    elif result.warnings:
        result.status = "warn"
        result.exit_code = 0
    return result


def _format_human(result: CheckResult) -> str:
    out: list[str] = []
    if result.status == "usage":
        out.append("BCI-1 build-checks integrity: USAGE ERROR\n\n")
        for d in result.divergences:
            out.append(f"  {d}\n")
        return "".join(out)
    if result.status == "drift":
        out.append("BCI-1 build-checks integrity: DRIFT (HALT)\n\n")
        for d in result.divergences:
            out.append(f"  {d}\n")
        if result.warnings:
            out.append("\n  Warnings:\n")
            for w in result.warnings:
                out.append(f"    {w}\n")
        return "".join(out)
    if result.status == "warn":
        out.append("BCI-1 build-checks integrity: PASS (with WARN)\n\n")
        for w in result.warnings:
            out.append(f"  WARN: {w}\n")
        return "".join(out)
    out.append(
        "BCI-1 build-checks integrity: PASS — live build-checks files match "
        "the git-tracked canonical fixtures on full per-rule structural "
        "identity.\n"
    )
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="build_checks_integrity",
        description=(
            "BCI-1 — assert the live build-checks files match the git-"
            "tracked canonical fixtures on full per-rule structural identity"
        ),
    )
    parser.add_argument(
        "--check-live",
        action="store_true",
        help="Check live build-checks files vs fixtures (default action)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repo root (default: two parents up from this file)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    args = parser.parse_args(argv)

    if args.root is None:
        root = Path(__file__).resolve().parent.parent
    else:
        root = args.root.resolve()

    if not root.exists():
        sys.stderr.write(f"repo root not found: {root}\n")
        return 2

    result = check_live(root)

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
