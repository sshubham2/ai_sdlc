"""Tests for tools.test_first_audit (TF-1).

Validates that the audit correctly:
- Detects the opt-in `**Test-first**: true | false` field
- Treats absent / false flag as "default-off, no violation"
- When true, requires a `## Test-first plan` section with a 5-column table
- Validates Status vocabulary {PENDING, WRITTEN-FAILING, PASSING}
- Flags ACs in the brief without at least one test-first row
- Refuses non-PASSING rows when --strict-pre-finish (used at /build-slice)
- Honors NFR-1 carry-over exemption

Pins skill prose in /slice + /build-slice.

Rule reference: TF-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.test_first_audit import (
    _TF_1_RELEASE_DATE,
    _format_human,
    _normalize_ac_label,
    audit_brief_file,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "test_first"


# --- Unit tests ---

def test_normalize_ac_label_handles_common_forms():
    """'AC#1', 'ac 1', '1' all normalize to '1'.

    Defect class: An AC reference that's spelled 'AC#1' in the body but
    '1' in the table would be treated as different ACs and the orphan
    detection would fire spuriously.
    Rule reference: TF-1.
    """
    assert _normalize_ac_label("AC#1") == "1"
    assert _normalize_ac_label("ac 1") == "1"
    assert _normalize_ac_label("1") == "1"
    assert _normalize_ac_label("AC#10") == "10"


# --- File-level audit tests ---

def test_clean_brief_passes():
    """A test-first brief with all ACs covered + statuses valid passes.

    Defect class: The most common case (test-first opt-in, all rows
    PASSING) must audit cleanly.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "clean_brief.md")
    assert result.test_first_enabled is True
    assert result.violations == [], (
        f"unexpected violations: "
        f"{[(v.kind, v.message) for v in result.violations]}"
    )
    assert len(result.rows) == 4
    statuses = {r.status for r in result.rows}
    assert statuses == {"PASSING"}


def test_test_first_off_is_silent():
    """A brief without `**Test-first**: true` produces no violations.

    Defect class: An audit that fires on every brief regardless of opt-in
    would force every project to adopt test-first immediately.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "test_first_off.md")
    assert result.test_first_enabled is False
    assert result.violations == []


def test_missing_section_when_test_first_true_flagged():
    """`**Test-first**: true` without a `## Test-first plan` section fails.

    Defect class: Opting into test-first but skipping the plan defeats
    the rule's purpose; the audit must catch the inconsistency.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "missing_section_brief.md")
    assert any(v.kind == "missing-section" for v in result.violations)


def test_invalid_status_flagged():
    """Status outside {PENDING, WRITTEN-FAILING, PASSING} is flagged.

    Defect class: An open status vocabulary lets the lifecycle decay
    into ad-hoc strings; the gate becomes meaningless.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "invalid_status_brief.md")
    assert any(v.kind == "invalid-status" for v in result.violations)


def test_ac_without_row_flagged():
    """An AC declared in the brief body without any test-first row fails.

    Defect class: Orphan ACs slip through to /build-slice without
    any test coverage planned — TF-1's coverage guarantee is silently
    violated.
    Rule reference: TF-1.
    """
    result = audit_brief_file(FIXTURES / "ac_without_row_brief.md")
    orphans = [v for v in result.violations if v.kind == "ac-without-row"]
    assert len(orphans) == 1
    assert orphans[0].ac == "2"


def test_strict_pre_finish_refuses_non_passing():
    """--strict-pre-finish flags PENDING + WRITTEN-FAILING rows as violations.

    Defect class: /build-slice declaring "done" while tests are still
    failing is exactly what test-first is supposed to prevent. Strict
    mode is the gate that catches it.
    Rule reference: TF-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=True,
    )
    non_passing = [v for v in result.violations if v.kind == "non-passing-pre-finish"]
    # 2 rows are non-PASSING (one WRITTEN-FAILING, one PENDING)
    assert len(non_passing) == 2


def test_strict_pre_finish_default_does_not_refuse():
    """Without --strict-pre-finish, non-PASSING rows are allowed.

    Defect class: Refusing PENDING / WRITTEN-FAILING during /design-slice
    or /critique would block legitimate workflows where rows haven't yet
    been brought to PASSING.
    Rule reference: TF-1.
    """
    result = audit_brief_file(
        FIXTURES / "pre_finish_pending_brief.md",
        strict_pre_finish=False,
    )
    non_passing = [v for v in result.violations if v.kind == "non-passing-pre-finish"]
    assert non_passing == []


def test_missing_brief_is_silent():
    """A missing mission-brief.md produces no violations (default-off).

    Defect class: A linter that crashes on missing input is hostile.
    Rule reference: TF-1.
    """
    result = audit_brief_file(REPO_ROOT / "does-not-exist-tf.md")
    assert result.test_first_enabled is False
    assert result.violations == []


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_briefs(tmp_path: Path):
    """Briefs whose mtime predates TF-1 are exempt automatically.

    Defect class: Retroactively applying TF-1 to old slices would refuse
    every archived brief that has `Test-first: true` set ad-hoc.
    Rule reference: TF-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Test-first**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _TF_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief)
    assert result.carry_over_exempt is True
    assert result.violations == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Without an override, archive scans can't reach pre-rule
    slices.
    Rule reference: TF-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text(
        "# old slice\n\n**Test-first**: true\n\n## Acceptance criteria\n\n1. thing\n",
        encoding="utf-8",
    )
    _set_brief_mtime(brief, _TF_1_RELEASE_DATE - timedelta(days=30))

    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.carry_over_exempt is False
    assert any(v.kind == "missing-section" for v in result.violations)


# --- Skill prose pins ---

def test_slice_skill_references_tf_1():
    """skills/slice/SKILL.md must reference TF-1 + the Test-first option.

    Defect class: Without /slice documenting the option, projects don't
    know they can opt in; TF-1 sits unused.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "skills" / "slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "TF-1" in text, "no TF-1 reference in /slice SKILL.md"
    assert "Test-first" in text, "no Test-first option in /slice"


def test_build_slice_references_tf_1():
    """skills/build-slice/SKILL.md must reference TF-1 + the audit.

    Defect class: Without /build-slice running the strict-pre-finish
    audit, slices declaring test-first ship with PENDING/WRITTEN-FAILING
    rows.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "TF-1" in text, "no TF-1 reference in /build-slice SKILL.md"
    assert "test_first_audit" in text, (
        "no test_first_audit module reference in /build-slice"
    )


def test_mission_brief_template_documents_test_first():
    """templates/mission-brief.md must document the Test-first field + section.

    Defect class: Without the template referencing TF-1, project owners
    creating briefs by hand miss the option.
    Rule reference: TF-1.
    """
    text = (REPO_ROOT / "templates" / "mission-brief.md").read_text(encoding="utf-8")
    assert "Test-first" in text
    assert "TF-1" in text


# --- PTFCD-1: test-path-existence check (slice-025 AC #1) ---

def _write_brief(tmp_path, rows: list[tuple[str, str, str, str, str]]) -> Path:
    """Write a minimal test-first brief into tmp_path; `rows` are
    (ac, test_type, test_path, test_function, status) tuples.
    """
    table = "\n".join(
        f"| {ac} | {tt} | {tp} | {tf} | {st} |" for (ac, tt, tp, tf, st) in rows
    )
    brief = (
        "# Slice 999: ptfcd fixture\n\n"
        "**Test-first**: true\n\n"
        "## Acceptance criteria\n\n"
        "1. the thing\n\n"
        "## Test-first plan\n\n"
        "| AC | Test type | Test path | Test function | Status |\n"
        "|----|-----------|-----------|---------------|--------|\n"
        f"{table}\n\n"
        "## Out of scope\n\n- nothing\n"
    )
    p = tmp_path / "mission-brief.md"
    p.write_text(brief, encoding="utf-8")
    return p


def test_strict_pre_finish_flags_missing_test_path_file(tmp_path):
    """A PASSING row citing a non-existent Test path is a
    `missing-test-path-file` violation under --strict-pre-finish.

    Defect class: the phantom-test-file-citation class (slice-023 B4 /
    slice-024) — a PASSING row may not cite a file that does not exist.
    Rule reference: PTFCD-1 (slice-025 AC #1).
    """
    brief = _write_brief(
        tmp_path,
        [("1", "unit", "tests/methodology/test_DOES_NOT_EXIST_xyz.py",
          "test_x", "PASSING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-path-file" in kinds, (
        f"expected missing-test-path-file under strict; got {kinds}"
    )


def test_non_strict_does_not_flag_pending_missing_file(tmp_path):
    """Non-strict runs never emit `missing-test-path-file` — a PENDING
    test-first row legitimately references a not-yet-created file.

    Defect class: false-positive on mid-slice PENDING rows would make the
    audit unusable during normal test-first development.
    Rule reference: PTFCD-1 (slice-025 AC #1; must-not-defer false-positive
    avoidance).
    """
    brief = _write_brief(
        tmp_path,
        [("1", "unit", "tests/methodology/test_not_yet_created.py",
          "test_x", "PENDING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=False,
                              skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "missing-test-path-file" not in kinds, (
        f"non-strict run must not emit missing-test-path-file; got {kinds}"
    )


def test_existence_check_covers_non_pytest_rows(tmp_path):
    """The existence check covers non-pytest rows (catalog-verification),
    not just unit/integration pytest rows.

    Defect class: slice-024's phantom citation was a non-pytest
    (catalog-verification) row; a pytest-only check would have missed it.
    Rule reference: PTFCD-1 (slice-025 AC #1).
    """
    brief = _write_brief(
        tmp_path,
        [("1", "catalog-verification",
          "tests/methodology/test_phantom_catalog_xyz.py",
          "covered by catalog command", "PASSING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    assert any(
        v.kind == "missing-test-path-file" and v.ac == "1"
        for v in result.violations
    ), (
        "non-pytest (catalog-verification) PASSING row with missing file "
        f"must be flagged; got {[(v.kind, v.ac) for v in result.violations]}"
    )


def test_pending_row_missing_file_emits_exactly_one_violation(tmp_path):
    """A still-PENDING row with a missing file under --strict-pre-finish
    emits exactly ONE violation (non-passing-pre-finish), NOT a doubled
    non-passing + missing-test-path-file pair.

    Defect class (Critic M1): the existence loop iterates the same
    `result.rows` as the non-passing loop; without the `row.status ==
    "PASSING"` gate a PENDING missing-file row would be flagged twice.
    Rule reference: PTFCD-1 (slice-025 AC #1; Critic M1 ACCEPTED-FIXED).
    """
    brief = _write_brief(
        tmp_path,
        [("1", "unit", "tests/methodology/test_pending_missing_xyz.py",
          "test_x", "PENDING")],
    )
    result = audit_brief_file(brief, strict_pre_finish=True,
                              skip_if_carry_over=False)
    row_violations = [v for v in result.violations if v.ac == "1"]
    assert len(row_violations) == 1, (
        f"expected exactly one violation for the PENDING row, got "
        f"{[(v.kind) for v in row_violations]}"
    )
    assert row_violations[0].kind == "non-passing-pre-finish", (
        f"the single violation must be non-passing-pre-finish, not "
        f"{row_violations[0].kind} — PASSING-gate broken (double-flag)"
    )


# --- R-7 / TFFL-1 (slice-034): field-line robustness ---

def _brief_with_field_line(tmp_path: Path, field_line: str | None) -> Path:
    """Write a minimal brief with a custom (or absent) `**Test-first**`
    field line. `field_line=None` → the field is genuinely absent.
    """
    head = "# Slice 999: tffl-1 fixture\n\n"
    fld = "" if field_line is None else f"{field_line}\n\n"
    body = (
        "## Acceptance criteria\n\n"
        "1. the thing\n\n"
        "## Out of scope\n\n- nothing\n"
    )
    p = tmp_path / "mission-brief.md"
    p.write_text(head + fld + body, encoding="utf-8")
    return p


def test_absent_field_stays_default_off_clean(tmp_path: Path):
    """AC2: a brief with NO `**Test-first**:` field stays legitimate
    default-off — clean, not enabled, zero violations.

    Defect class: the TFFL-1 malformed branch must NOT fire on genuine
    absence (that is the legitimate opt-out — old briefs keep working).
    Rule reference: TF-1 / TFFL-1 / R-7.
    """
    brief = _brief_with_field_line(tmp_path, None)
    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.test_first_enabled is False
    assert result.violations == []
    assert "not enabled" in _format_human(result)


def test_present_false_field_is_not_malformed(tmp_path: Path):
    """AC2 / M2 invariant: `**Test-first**: false` SATISFIES the value
    matcher → legitimate default-off, NOT a malformed violation.

    Defect class: an implementation that narrowed the malformed branch's
    value check to `true`-only would spuriously flag every disabled brief.
    Rule reference: TF-1 / TFFL-1 / R-7 (critique M2).
    """
    brief = _brief_with_field_line(tmp_path, "**Test-first**: false")
    result = audit_brief_file(brief, skip_if_carry_over=False)
    assert result.test_first_enabled is False
    assert result.violations == [], (
        "`**Test-first**: false` is well-formed + disabled — must take "
        "legitimate default-off, NOT the malformed branch (M2 invariant)"
    )

    # Annotated false must also stay clean (not malformed, not enabled).
    brief2 = _brief_with_field_line(
        tmp_path, "**Test-first**: false  (intentionally disabled here)"
    )
    result2 = audit_brief_file(brief2, skip_if_carry_over=False)
    assert result2.test_first_enabled is False
    assert result2.violations == []


def test_present_but_malformed_field_is_loud_not_silent(tmp_path: Path):
    """AC3: `**Test-first**: maybe` (present but unparseable) emits a loud
    `malformed-test-first-field` violation — NEVER silent default-off.

    Defect class: R-7 — a present-but-broken field silently default-offs
    and bypasses the entire TF-1 gate on a genuinely test-first slice.
    Rule reference: TF-1 / TFFL-1 / R-7.
    """
    brief = _brief_with_field_line(tmp_path, "**Test-first**: maybe")
    result = audit_brief_file(brief, skip_if_carry_over=False)
    kinds = [v.kind for v in result.violations]
    assert "malformed-test-first-field" in kinds, (
        f"present-but-unparseable field must be loud; got violations={kinds}"
    )
    human = _format_human(result)
    assert "not enabled" not in human, (
        "the silent 'not enabled' message must NOT mask a malformed field"
    )
    assert "malformed-test-first-field" in human

    # Empty value is also malformed (present prefix, no value token).
    brief_empty = _brief_with_field_line(tmp_path, "**Test-first**:")
    res_empty = audit_brief_file(brief_empty, skip_if_carry_over=False)
    assert "malformed-test-first-field" in [
        v.kind for v in res_empty.violations
    ]


def test_malformed_suffix_value_is_loud_not_silent(tmp_path: Path):
    """AC3 / M1: `**Test-first**: false-positive` / `true.` must NOT be
    silently accepted as a valid boolean (the `\\b` over-match defect) —
    they hit the loud malformed branch instead.

    Defect class: the rejected `(true|false)\\b.*$` accepted `false-positive`
    as `false` → silent default-off — a narrower R-7 self-violation.
    Rule reference: TF-1 / TFFL-1 / R-7 (critique M1).
    """
    for bad in (
        "**Test-first**: false-positive",
        "**Test-first**: true.",
        "**Test-first**: trueish",
        "**Test-first**: false; see note",
    ):
        brief = _brief_with_field_line(tmp_path, bad)
        result = audit_brief_file(brief, skip_if_carry_over=False)
        assert result.test_first_enabled is False, (
            f"{bad!r} must NOT be parsed as an enabling boolean"
        )
        assert "malformed-test-first-field" in [
            v.kind for v in result.violations
        ], f"{bad!r} must hit the loud malformed branch, not silent default-off"
        assert "not enabled" not in _format_human(result)
