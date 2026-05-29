"""Bug: BC-1 build-checks audit exit code does not gate on applicable Critical rules.

Source: diagnose-out/backlog.md SC-008 (finding F-HALF-9b2e44d1).

Expected (the fix contract — ADR-072 / BCSG-1, the acknowledgment-flag design):
    `tools/build_checks_audit.main()` accepts a `--strict` flag (mirroring
    test_first_audit / walking_skeleton_audit's `--strict-pre-finish`) plus an
    `--ack-critical <RULE-ID...>` sign-off list. Under `--strict`, an applicable
    Critical-severity rule whose rule_id is NOT in the ack set becomes an
    `unacknowledged-critical` violation, so the existing
    `return 1 if result.violations else 0` yields gate-failure exit 1; the gate
    returns 0 when every applicable Critical rule is acknowledged OR none
    applies. `/build-slice` Step 6 invokes the audit with
    `--strict --ack-critical <addressed rule IDs>` so a non-deferrable Critical
    rule that has not been acknowledged actually blocks the slice.
    (NOTE: the blunt "exit 1 whenever critical_applicable > 0" framing was
    ADR-072 option 1 and was REJECTED — it has no green path for a slice that
    legitimately touches an always-on Critical rule.)

Actual (current defect):
    `main()` ends in `return 1 if result.violations else 0` (build_checks_audit.py:619).
    `result.violations` holds only parse errors (malformed build-checks.md), NOT
    applicable Critical rules. So an applicable Critical rule produces exit 0,
    while the tool prints "Per BC-1, Critical rules MUST be addressed ...". There
    is no `--strict` flag at all — argparse rejects it with exit code 2. A tooling
    consumer that treats the exit code as the gate signal passes a slice that
    violates a non-deferrable Critical rule.

Fix slice: slice-080-harden-bc1-critical-rules-exit-gate.
This test FAILS until the --strict gate is implemented and PASSES after.
"""
from datetime import datetime
from pathlib import Path

from tools import build_checks_audit

FIXTURES = Path(__file__).resolve().parents[1] / "methodology" / "fixtures" / "build_checks"

# 1 applicable Critical always-rule (BC-PROJ-1, Severity: Critical, Applies to: always).
CRITICAL_PROJECT_CHECKS = FIXTURES / "one_always_applies.md"
# 0 rules → 0 applicable Critical. Doubles as an empty global-checks source.
CLEAN_CHECKS = FIXTURES / "clean_project_checks.md"


def _make_slice(tmp_path: Path) -> Path:
    """A fresh slice folder (mission-brief mtime = now → not BC-1 carry-over)."""
    slice_folder = tmp_path / "slice-080-test"
    slice_folder.mkdir(parents=True, exist_ok=True)
    (slice_folder / "mission-brief.md").write_text(
        "# slice-080 test\n\nendpoint route api\n", encoding="utf-8"
    )
    (slice_folder / "design.md").write_text("# design\n", encoding="utf-8")
    return slice_folder


def _run_main(argv: list[str]) -> int:
    """Invoke main(); normalize an argparse SystemExit to its integer code.

    Today `--strict` is unrecognized → argparse raises SystemExit(2); after the
    fix the flag is accepted and main() returns its int gate code directly.
    """
    try:
        return build_checks_audit.main(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1


def test_strict_exits_nonzero_on_applicable_critical_rule(tmp_path: Path):
    """`--strict` returns exit code 1 when an applicable Critical rule is unacknowledged.

    No `--ack-critical` is passed, so the applicable Critical rule (BC-PROJ-1
    from the fixture) stays unacknowledged → becomes an `unacknowledged-critical`
    violation → exit 1, the same gate-failure code main() already uses for parse
    violations. Fails now: argparse rejects the unknown `--strict` flag with exit
    code 2 (2 != 1). Passes after the fix.
    """
    slice_folder = _make_slice(tmp_path)
    rc = _run_main([
        "--slice", str(slice_folder),
        "--project-checks", str(CRITICAL_PROJECT_CHECKS),
        "--global-checks", str(CLEAN_CHECKS),
        "--no-carry-over",
        "--strict",
    ])
    assert rc == 1, (
        "BC-1 --strict must return gate-failure exit 1 when an applicable "
        f"Critical rule is present; got {rc}"
    )


def test_strict_exits_zero_when_no_critical_applicable(tmp_path: Path):
    """`--strict` does NOT false-fire: exit 0 when no Critical rule applies.

    Fails now: argparse rejects the unknown `--strict` flag with exit code 2
    (2 != 0). Passes after the fix: the strict gate is silent when
    critical_applicable == 0 and there are no parse violations.
    """
    slice_folder = _make_slice(tmp_path)
    rc = _run_main([
        "--slice", str(slice_folder),
        "--project-checks", str(CLEAN_CHECKS),
        "--global-checks", str(CLEAN_CHECKS),
        "--no-carry-over",
        "--strict",
    ])
    assert rc == 0, (
        "BC-1 --strict must exit 0 when no Critical rule is applicable and "
        f"there are no parse violations; got {rc}"
    )
