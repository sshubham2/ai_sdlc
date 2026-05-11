"""Tests for tools.build_checks_audit (BC-1).

Validates that the build-checks audit correctly:
- Parses H2 rules with required fields (Severity, Applies to, Check)
- Flags missing required fields and invalid severities (parse violations)
- Resolves applicability via globs, trigger keywords, and `always: true`
- Reads project + global build-checks together
- Honors NFR-1 carry-over exemption (mtime check on mission-brief.md)
- Pins skill-prose references in /build-slice + /reflect

Rule reference: BC-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT
from tools.build_checks_audit import (
    _BC_1_RELEASE_DATE,
    _matches_glob,
    audit_slice,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "build_checks"


def _make_slice(tmp_path: Path, brief_text: str = "# slice", mtime_date=None) -> Path:
    """Create a temp slice folder with mission-brief.md + design.md."""
    slice_folder = tmp_path / "slice-001-test"
    slice_folder.mkdir(parents=True, exist_ok=True)
    brief = slice_folder / "mission-brief.md"
    brief.write_text(brief_text, encoding="utf-8")
    design = slice_folder / "design.md"
    design.write_text("# design\n", encoding="utf-8")
    if mtime_date is not None:
        target_dt = datetime.combine(mtime_date, datetime.min.time().replace(hour=12))
        ts = target_dt.timestamp()
        os.utime(brief, (ts, ts))
    return slice_folder


# --- Glob matcher unit tests ---

def test_glob_simple_segment_match():
    """`src/api/*.py` matches `src/api/foo.py` but not `src/api/v1/foo.py`.

    Defect class: A `*` glob that escapes path segments would match too
    broadly and surface rules unrelated to the changed file.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/api/foo.py", "src/api/*.py") is True
    assert _matches_glob("src/api/v1/foo.py", "src/api/*.py") is False


def test_glob_double_star_matches_multi_segment():
    """`src/api/**` matches one or more segments under `src/api/`.

    Defect class: Without `**` support, a rule scoped to a directory tree
    would have to enumerate depths; that's brittle.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/api/foo.py", "src/api/**") is True
    assert _matches_glob("src/api/v1/foo.py", "src/api/**") is True
    assert _matches_glob("src/api/v1/v2/foo.py", "src/api/**") is True
    assert _matches_glob("src/services/foo.py", "src/api/**") is False


def test_glob_substring_within_filename():
    """`src/services/*upload*.py` matches `src/services/file_upload.py`.

    Defect class: A glob that can't match substring patterns within filenames
    would force rule authors to use ** or list files exhaustively.
    Rule reference: BC-1.
    """
    assert _matches_glob("src/services/file_upload.py", "src/services/*upload*.py") is True
    assert _matches_glob("src/services/download.py", "src/services/*upload*.py") is False


def test_glob_handles_windows_separators():
    """Windows-style backslashes normalize to forward slashes for matching.

    Defect class: A glob matcher that breaks on Windows path separators
    would silently mis-classify rules in the Windows dev environment.
    Rule reference: BC-1.
    """
    assert _matches_glob(r"src\api\foo.py", "src/api/**") is True


# --- Parsing tests ---

def test_clean_file_with_no_rules_yields_no_applicable(tmp_path: Path):
    """Empty rules section produces zero applicable rules (no violations).

    Defect class: A bootstrap file with no rules yet must not trip the audit.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "clean_project_checks.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.applicable == []
    assert result.violations == []


def test_always_true_rule_always_applies(tmp_path: Path):
    """`Applies to: always: true` surfaces regardless of changed_files / text.

    Defect class: An always-on guard (e.g., 'every endpoint needs auth test')
    must surface even when no obvious file glob matches.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=[],
    )
    assert len(result.applicable) == 1
    rule = result.applicable[0]
    assert rule.rule_id == "BC-PROJ-1"
    assert rule.severity == "Critical"
    assert rule.applies_to == ("always",)


def test_glob_applies_to_matches_changed_files(tmp_path: Path):
    """A rule with `Applies to: src/api/uploads/**` fires when a matching file changed.

    Defect class: Glob-scoped rules must NOT fire on unrelated slices, only
    when the file pattern matches the slice's changed files.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "glob_match.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/api/uploads/receipts.py"],
    )
    assert len(result.applicable) == 1
    assert result.applicable[0].rule_id == "BC-PROJ-2"


def test_glob_applies_to_does_not_match_unrelated_files(tmp_path: Path):
    """A glob-scoped rule must NOT fire on unrelated slices.

    Defect class: A rule firing on every slice (regardless of relevance) is
    noise; the builder learns to ignore it.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "glob_match.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/database/migrations/001.sql"],
    )
    assert result.applicable == []
    assert len(result.skipped) == 1


def test_keyword_match_via_mission_brief(tmp_path: Path):
    """A keyword in mission-brief.md fires the rule even with no matching glob.

    Defect class: Some rules apply by topic, not by file path (e.g., 'auth
    rework slice should run pen-test'). Without keyword matching, the rule
    can't be triggered by mission-brief alone.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        brief_text="# Slice\n\nRework JWT token refresh handling for the auth flow.",
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "keyword_only.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=[],  # no glob hits
    )
    assert len(result.applicable) == 1
    assert result.applicable[0].rule_id == "BC-PROJ-3"


def test_missing_severity_field_yields_violation(tmp_path: Path):
    """A rule missing the Severity field is flagged as a parse violation.

    Defect class: A malformed rule that's silently parsed with default
    severity would let authors skip the field by accident; making it a
    violation forces explicit severity.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "missing_severity.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.kind == "missing-field"
    assert "severity" in v.message.lower()


def test_invalid_severity_yields_violation(tmp_path: Path):
    """Severity outside {Critical, Important} is flagged.

    Defect class: An open severity vocabulary lets rules drift to 'Suggested'
    / 'Nice-to-have' / 'Maybe' and the gate becomes meaningless.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "invalid_severity.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert any(v.kind == "invalid-severity" for v in result.violations)


def test_multi_rules_filtered_by_applicability(tmp_path: Path):
    """3 rules: always-true fires; glob-only fires only on payments; keyword-only fires only on migration text.

    Defect class: An audit that surfaces every rule defeats the targeting
    purpose. Applicability filtering is the value of the audit.
    Rule reference: BC-1.
    """
    # First scenario: changed payments file, no migration in brief
    slice_payments = _make_slice(tmp_path / "a", brief_text="# slice\nadd payment processor.")
    result = audit_slice(
        slice_folder=slice_payments,
        project_checks=FIXTURES / "multi_rules.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/payments/stripe_adapter.py"],
    )
    rule_ids = {r.rule_id for r in result.applicable}
    assert "BC-PROJ-6" in rule_ids  # always
    assert "BC-PROJ-7" in rule_ids  # glob match
    assert "BC-PROJ-8" not in rule_ids  # no keyword

    # Second scenario: brief mentions migration, no payments file
    slice_migration = _make_slice(
        tmp_path / "b",
        brief_text="# slice\nadd alembic migration for users table schema.",
    )
    result2 = audit_slice(
        slice_folder=slice_migration,
        project_checks=FIXTURES / "multi_rules.md",
        global_checks=Path("/nonexistent/global.md"),
        changed_files=["src/users/model.py"],
    )
    rule_ids2 = {r.rule_id for r in result2.applicable}
    assert "BC-PROJ-6" in rule_ids2
    assert "BC-PROJ-7" not in rule_ids2
    assert "BC-PROJ-8" in rule_ids2  # keyword hit


def test_global_and_project_checks_combine(tmp_path: Path):
    """Project + global build-checks are merged in the result.

    Defect class: If global and project checks aren't combined, cross-project
    rules (e.g., 'never commit secrets') would be invisible at /build-slice.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=FIXTURES / "global_checks.md",
    )
    sources = {r.source for r in result.applicable}
    assert "project" in sources
    assert "global" in sources


def test_carry_over_exempts_old_slices(tmp_path: Path):
    """Slice whose mission-brief.md mtime predates BC-1 is exempt.

    Defect class: Retroactively applying BC-1 to slices authored before
    the rule existed would refuse old archived slices. NFR-1 carry-over
    via mtime check exempts them.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        mtime_date=_BC_1_RELEASE_DATE - timedelta(days=30),
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.carry_over_exempt is True
    assert result.applicable == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """`skip_if_carry_over=False` audits even old slices.

    Defect class: Without an override, archive scans (CI / catalog audits)
    can't reach pre-rule slices.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(
        tmp_path,
        mtime_date=_BC_1_RELEASE_DATE - timedelta(days=30),
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=FIXTURES / "one_always_applies.md",
        global_checks=Path("/nonexistent/global.md"),
        skip_if_carry_over=False,
    )
    assert result.carry_over_exempt is False
    assert len(result.applicable) == 1


def test_missing_project_checks_file_handled_gracefully(tmp_path: Path):
    """Missing project checks file is fine — no rules to surface.

    Defect class: A linter that crashes on a missing input is hostile;
    most projects won't have build-checks.md until rules accumulate.
    Rule reference: BC-1.
    """
    slice_folder = _make_slice(tmp_path)
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=Path("/nonexistent/project.md"),
        global_checks=Path("/nonexistent/global.md"),
    )
    assert result.applicable == []
    assert result.violations == []


# --- Skill prose pins ---

def test_build_slice_skill_references_bc_1():
    """skills/build-slice/SKILL.md must reference BC-1 + the audit module.

    Defect class: Without the pre-finish gate referencing BC-1 + the tool
    name, the rule is advisory. The skill prose must name both.
    Rule reference: BC-1.
    """
    text = (REPO_ROOT / "skills" / "build-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "BC-1" in text, "no BC-1 reference in /build-slice SKILL.md"
    assert "build_checks_audit" in text, (
        "no build_checks_audit module reference in /build-slice"
    )


def test_reflect_skill_references_bc_1():
    """skills/reflect/SKILL.md must reference BC-1 in the promotion step.

    Defect class: Without /reflect documenting promotion, recurring
    patterns stay buried in lessons-learned and never become checks.
    Rule reference: BC-1.
    """
    text = (REPO_ROOT / "skills" / "reflect" / "SKILL.md").read_text(encoding="utf-8")
    assert "BC-1" in text, "no BC-1 reference in /reflect SKILL.md"
    assert "build-checks" in text, (
        "no build-checks reference in /reflect"
    )
    # Pin the promotion-prompt language so it can't be paraphrased away
    assert "recurring pattern" in text.lower(), (
        "promotion prompt should mention 'recurring pattern'"
    )


# --- Slice-005: BC-1 keyword precision (word-boundary + Trigger anchors) ---
#
# Per slice-005-add-bc-1-keyword-precision (mission-brief + ADR-004), the
# BC-1 keyword-applicability path now uses case-insensitive word-boundary
# matching (was bare substring) and supports an optional Trigger anchors:
# field per rule. Tests below cover ACs #1-#5 + the M1/M2 promoted rows.

_GLOBAL_BUILD_CHECKS = Path.home() / ".claude" / "build-checks.md"


def test_slice_003_archive_backtest_no_bc_proj_2_or_global_1_applications():
    """Slice-003 archive folder must NOT trigger BC-PROJ-2 or BC-GLOBAL-1.

    Defect class: BC-1 trigger keywords matched as bare substrings produced
    false positives across slices (slice-003 + slice-004 N=2 confirmed —
    `parse_declared_deps` substring-matched `parse`). Word-boundary +
    Trigger anchors silences the noise. The rule must appear in `skipped`
    (per slice-003 lesson on TF-1 PENDING -> WRITTEN-FAILING genuineness:
    a presence-only `not in applicable` assertion could mass-pass if no
    rules apply at all; the in-`skipped` assertion makes the failure mode
    unambiguous — distinguishes "fix not applied" from "fix doesn't exist").
    Rule reference: BC-1 (slice-005 AC #1).
    """
    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-003-add-val-1-imports-allowlist",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-2" not in applicable_ids, (
        f"BC-PROJ-2 should NOT apply to slice-003 archive (false-positive class). "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-2" in skipped_ids, (
        f"BC-PROJ-2 should appear in skipped (rule was parsed but didn't fire). "
        f"Got skipped: {skipped_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" not in applicable_ids, (
            f"BC-GLOBAL-1 should NOT apply to slice-003 archive. "
            f"Got applicable: {applicable_ids}"
        )
        assert "BC-GLOBAL-1" in skipped_ids, (
            f"BC-GLOBAL-1 should appear in skipped. Got skipped: {skipped_ids}"
        )


def test_slice_004_archive_backtest_no_bc_proj_2_or_global_1_applications():
    """Slice-004 archive folder must NOT trigger BC-PROJ-2 or BC-GLOBAL-1.

    Defect class: slice-004 mission-brief + design contain bare-word
    `parse`, `backtick`, `output` in regex/markdown/CLI contexts (not LLM-
    fence). Word-boundary alone is INSUFFICIENT here (those bare-word
    matches still fire); the Trigger anchors filter (anchors fence/code-
    block/llm) is what closes the gap. The skipped half-assertion pattern
    matches test #1 above.
    Rule reference: BC-1 (slice-005 AC #2).
    """
    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-004-fix-rr1-audit-docstring-or-regex",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-2" not in applicable_ids, (
        f"BC-PROJ-2 should NOT apply to slice-004 archive (false-positive class). "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-2" in skipped_ids, (
        f"BC-PROJ-2 should appear in skipped (rule was parsed but didn't fire). "
        f"Got skipped: {skipped_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" not in applicable_ids, (
            f"BC-GLOBAL-1 should NOT apply to slice-004 archive. "
            f"Got applicable: {applicable_ids}"
        )
        assert "BC-GLOBAL-1" in skipped_ids, (
            f"BC-GLOBAL-1 should appear in skipped. Got skipped: {skipped_ids}"
        )


def test_legitimate_llm_fence_brief_still_triggers_bc_proj_2_and_global_1(
    tmp_path: Path,
):
    """A synthetic brief discussing LLM-fence parsing DOES trigger BC-PROJ-2.

    Defect class: precision improvement must not over-suppress. A real slice
    that discusses LLM-fence parsing must still surface the BC-PROJ-2 /
    BC-GLOBAL-1 rules. The canonical synthetic uses the bare anchor words
    `LLM` and `code-block` (per Critic B2 — the AC #3 example uses `fenced`
    which the new word-boundary regex doesn't match against `\\bfence\\b`;
    `code-block` provides a domain-coherent anchor word that DOES match).
    Rule reference: BC-1 (slice-005 AC #3).
    """
    slice_folder = _make_slice(
        tmp_path,
        brief_text=(
            "Parse the LLM agent's fenced output for nested triple-backtick "
            "code-block sections."
        ),
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}

    assert "BC-PROJ-2" in applicable_ids, (
        f"BC-PROJ-2 must apply to a brief that legitimately discusses "
        f"LLM-fence parsing. Got applicable: {applicable_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" in applicable_ids, (
            f"BC-GLOBAL-1 must apply to a brief that legitimately discusses "
            f"LLM-fence parsing. Got applicable: {applicable_ids}"
        )


def test_build_checks_schema_documents_trigger_anchors_field_name():
    """Schema description prose in BOTH project + global build-checks files
    must mention the literal `Trigger anchors` field name.

    Defect class: a new schema field added without documentation is invisible
    to authors of future rules. Per slice-002 + slice-003 + slice-004 pattern
    (methodology-tooling slices add prose-pin tests for every contract
    surface they change), and per Critic M3 (slice-005 — two surfaces,
    two pins).
    Rule reference: BC-1 (slice-005 AC #5 surface a).
    """
    project_text = (
        REPO_ROOT / "architecture" / "build-checks.md"
    ).read_text(encoding="utf-8")
    assert "Trigger anchors" in project_text, (
        "architecture/build-checks.md schema description must mention the "
        "literal `Trigger anchors` field name (case-sensitive)."
    )
    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pin is the canonical CI surface (slice-005 design "
            f"acknowledged this CI gap per Critic m4)."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    assert "Trigger anchors" in global_text, (
        f"{_GLOBAL_BUILD_CHECKS} schema description must mention the "
        f"literal `Trigger anchors` field name (case-sensitive)."
    )


def test_build_checks_schema_documents_word_boundary_semantics():
    """Schema description prose in BOTH project + global build-checks files
    must mention the literal `word-boundary` semantics phrase.

    Defect class: word-boundary is the OTHER new contract surface (universal
    semantic change, not just a new field). Per Critic M3 — pinning only the
    field name leaves the semantics phrase unprotected against doc refactor
    drift.
    Rule reference: BC-1 (slice-005 AC #5 surface b).
    """
    project_text = (
        REPO_ROOT / "architecture" / "build-checks.md"
    ).read_text(encoding="utf-8")
    assert "word-boundary" in project_text, (
        "architecture/build-checks.md schema description must mention the "
        "literal `word-boundary` semantics phrase (kebab-case)."
    )
    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pin is the canonical CI surface."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    assert "word-boundary" in global_text, (
        f"{_GLOBAL_BUILD_CHECKS} schema description must mention the "
        f"literal `word-boundary` semantics phrase."
    )


def test_migrated_rules_have_expected_anchors():
    """The 3 migrated rules MUST parse to the expected anchor tuples.

    Defect class: a migration typo (e.g., `Trigger anchors: fenced` instead
    of `fence`) would silently ship — backtest tests pass either way for
    slice-003 / slice-004 (those briefs have neither variant). The
    anchor-not-in-keywords parse violation would surface, but only if
    a separate test exercises the violation channel. This test pins the
    anchor TUPLES on the production rules themselves so a typo fails loud.
    Per Critic M1 — closes the migration-typo gap.
    Rule reference: BC-1 (slice-005 migration row).
    """
    from tools.build_checks_audit import _parse_rules

    project_path = REPO_ROOT / "architecture" / "build-checks.md"
    project_text = project_path.read_text(encoding="utf-8")
    rules, violations = _parse_rules(
        project_text, source="project", path=str(project_path)
    )
    by_id = {r.rule_id: r for r in rules}

    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed from project file"
    assert by_id["BC-PROJ-1"].trigger_anchors == ("subagent", "fan-out"), (
        f"BC-PROJ-1 anchors mismatch: got "
        f"{by_id['BC-PROJ-1'].trigger_anchors!r}, "
        f"expected ('subagent', 'fan-out')"
    )

    assert "BC-PROJ-2" in by_id, "BC-PROJ-2 not parsed from project file"
    assert by_id["BC-PROJ-2"].trigger_anchors == ("fence", "code-block", "llm"), (
        f"BC-PROJ-2 anchors mismatch: got "
        f"{by_id['BC-PROJ-2'].trigger_anchors!r}, "
        f"expected ('fence', 'code-block', 'llm')"
    )

    # No anchor-not-in-keywords violations expected on the production file
    bad = [
        v for v in violations
        if v.kind == "anchor-not-in-keywords"
    ]
    assert not bad, (
        f"production project build-checks.md emits anchor-not-in-keywords "
        f"violations: {[(v.rule_id, v.message) for v in bad]}"
    )

    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pins are the canonical CI surface."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    global_rules, global_violations = _parse_rules(
        global_text, source="global", path=str(_GLOBAL_BUILD_CHECKS)
    )
    global_by_id = {r.rule_id: r for r in global_rules}
    assert "BC-GLOBAL-1" in global_by_id, "BC-GLOBAL-1 not parsed from global file"
    expected_global_anchors = ("fence", "code-block", "llm", "structured-output")
    assert global_by_id["BC-GLOBAL-1"].trigger_anchors == expected_global_anchors, (
        f"BC-GLOBAL-1 anchors mismatch: got "
        f"{global_by_id['BC-GLOBAL-1'].trigger_anchors!r}, "
        f"expected {expected_global_anchors}"
    )


def test_anchor_not_in_keywords_yields_violation(tmp_path: Path):
    """A rule with anchors that aren't in trigger_keywords emits a violation.

    Defect class: input validation on the new `Trigger anchors:` field is a
    must-not-defer item per mission-brief.md; per Critic M2 — promoted from
    OPTIONAL to mandatory TF-1 row. Mirrors the existing
    `test_invalid_severity_yields_violation` pattern.
    Rule reference: BC-1 (slice-005 validation row).
    """
    from tools.build_checks_audit import _parse_rules

    fixture_text = (
        "# Build checks (project-specific)\n"
        "\n"
        "## Rules\n"
        "\n"
        "## BC-PROJ-99 - Test rule with bad anchor\n"
        "\n"
        "**Severity**: Important\n"
        "**Applies to**: src/**\n"
        "**Trigger keywords**: alpha, beta, gamma\n"
        "**Trigger anchors**: foo\n"
        "\n"
        "**Check**: This rule's anchor `foo` is not in trigger_keywords; "
        "audit MUST emit anchor-not-in-keywords violation.\n"
    )
    fixture_path = tmp_path / "anchor_not_in_keywords.md"
    fixture_path.write_text(fixture_text, encoding="utf-8")

    rules, violations = _parse_rules(
        fixture_text, source="project", path=str(fixture_path)
    )
    bad = [v for v in violations if v.kind == "anchor-not-in-keywords"]
    assert len(bad) >= 1, (
        f"expected at least 1 anchor-not-in-keywords violation; "
        f"got violations: {[(v.kind, v.message) for v in violations]}"
    )
    assert bad[0].rule_id == "BC-PROJ-99", (
        f"violation rule_id mismatch: got {bad[0].rule_id!r}, "
        f"expected 'BC-PROJ-99'"
    )
    assert "foo" in bad[0].message, (
        f"violation message must reference the offending anchor 'foo'; "
        f"got {bad[0].message!r}"
    )


# --- Slice-008: BC-1 v1.2 negative-context anchors (final filter) ---
#
# Per slice-008-refine-bc-1-anchors-with-negative-context (mission-brief +
# design.md + ADR-007), the BC-1 audit gains an optional per-rule
# `Negative anchors:` field (case-insensitive, word-boundary semantics)
# acting as a FINAL FILTER on positive applicability decisions. The
# mechanism applies UNIFORMLY across all three positive-applicability
# paths (`always: true` short-circuit, `--changed-files` glob match,
# keyword/anchor match) — see design.md Algorithm-path conformance table.
#
# Tests below cover ACs #1-#5 (with #5 split into 5a + 5b per Critic M2)
# + 3 must-not-defer rows (per Critic M3 algorithm-path conformance gap +
# the input-validation parse-violation + the migration-tuple pin).
#
# Build-time scenario (per design.md Test-first plan refinement): the
# slice-005..007 archive backtests use `--changed-files` matching each
# slice's representative changed pattern to make TF-1 PENDING ->
# WRITTEN-FAILING transitions genuine pre-slice-008.

# Representative --changed-files per slice (build-time scenario)
_SLICE_005_CHANGED_FILES = [
    "tools/build_checks_audit.py",
    "architecture/build-checks.md",
]
_SLICE_006_CHANGED_FILES = ["agents/critique.md"]
_SLICE_007_CHANGED_FILES = [
    "agents/critique.md",
    "skills/critic-calibrate/SKILL.md",
]
_SLICE_001_CHANGED_FILES = [
    "skills/diagnose/SKILL.md",
    "skills/diagnose/write_pass.py",
    "skills/diagnose/passes/01-intent.md",
]


def test_slice_005_archive_no_longer_fires_proj1_or_global1():
    """Slice-005 archive must NOT trigger BC-PROJ-1 or BC-GLOBAL-1.

    Defect class: methodology-vocabulary slice-005 fires BC-PROJ-1 +
    BC-GLOBAL-1 (and BC-PROJ-2) at build-time via keyword path on bare-
    word `subagent`, `llm`, `code-block`. Slice-008's negative-anchor
    final filter suppresses BC-PROJ-1 + BC-GLOBAL-1 because slice-005's
    text matches `defer-with-rationale, aggregated lessons, false
    positive, meta-discussion, vocabulary` (5+ negative-anchor hits).
    BC-PROJ-2 NOT migrated per Critic M1 (N=1 below promotion threshold)
    — assertion only on BC-PROJ-1 + BC-GLOBAL-1.
    Rule reference: BC-1 v1.2 (slice-008 AC #1).
    """
    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-005-add-bc-1-keyword-precision",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        changed_files=_SLICE_005_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-1" not in applicable_ids, (
        f"BC-PROJ-1 should NOT apply to slice-005 archive (silenced via "
        f"negative-anchor `vocabulary` etc.). Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-1" in skipped_ids, (
        f"BC-PROJ-1 should appear in skipped (rule was applicable but "
        f"final-filter suppressed). Got skipped: {skipped_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" not in applicable_ids, (
            f"BC-GLOBAL-1 should NOT apply to slice-005 archive. "
            f"Got applicable: {applicable_ids}"
        )
        assert "BC-GLOBAL-1" in skipped_ids, (
            f"BC-GLOBAL-1 should appear in skipped. Got skipped: {skipped_ids}"
        )


def test_slice_006_archive_no_longer_fires_proj1_or_global1():
    """Slice-006 archive must NOT trigger BC-PROJ-1 or BC-GLOBAL-1.

    Defect class: slice-006 (CCC-1 9th-dimension) fires BC-PROJ-1 (glob
    `agents/**/*.md`) + BC-GLOBAL-1 (`**` glob) at build-time when
    --changed-files=`agents/critique.md`. Slice-008's negative-anchor
    final filter suppresses both because slice-006 text matches
    `vocabulary, back-sync, Dim 9, Critic-MISSED` (4+ negative-anchor hits).
    Rule reference: BC-1 v1.2 (slice-008 AC #2).
    """
    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-006-update-critic-with-cross-cutting-conformance-dimension",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        changed_files=_SLICE_006_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-1" not in applicable_ids, (
        f"BC-PROJ-1 should NOT apply to slice-006 archive. "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-1" in skipped_ids, (
        f"BC-PROJ-1 should appear in skipped. Got skipped: {skipped_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" not in applicable_ids, (
            f"BC-GLOBAL-1 should NOT apply to slice-006 archive. "
            f"Got applicable: {applicable_ids}"
        )
        assert "BC-GLOBAL-1" in skipped_ids, (
            f"BC-GLOBAL-1 should appear in skipped. Got skipped: {skipped_ids}"
        )


def test_slice_007_archive_no_longer_fires_proj1_or_global1():
    """Slice-007 archive must NOT trigger BC-PROJ-1 or BC-GLOBAL-1.

    Defect class: slice-007 (CAD-1 audit) fires BC-PROJ-1 + BC-GLOBAL-1
    via glob path at build-time. Slice-008's negative-anchor final filter
    suppresses both because slice-007 text matches `back-sync, forward-
    sync, Dim 9, Critic-MISSED` (3+ negative-anchor hits). Per slice-007
    reflection: this is the third confirmed false-positive recurrence —
    meets BC-1 promotion threshold of N=3.
    Rule reference: BC-1 v1.2 (slice-008 AC #3).
    """
    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-007-add-critique-agent-content-equality-audit",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        changed_files=_SLICE_007_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-1" not in applicable_ids, (
        f"BC-PROJ-1 should NOT apply to slice-007 archive. "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-1" in skipped_ids, (
        f"BC-PROJ-1 should appear in skipped. Got skipped: {skipped_ids}"
    )
    if _GLOBAL_BUILD_CHECKS.exists():
        assert "BC-GLOBAL-1" not in applicable_ids, (
            f"BC-GLOBAL-1 should NOT apply to slice-007 archive. "
            f"Got applicable: {applicable_ids}"
        )
        assert "BC-GLOBAL-1" in skipped_ids, (
            f"BC-GLOBAL-1 should appear in skipped. Got skipped: {skipped_ids}"
        )


def test_slice_001_archive_still_fires_legitimate_rules():
    """Slice-001 archive (canonical legitimate fence-parsing + subagent-
    fan-out slice) MUST continue to fire BC-PROJ-1 AND at least one of
    BC-PROJ-2 / BC-GLOBAL-1 — backward-compat covenant per ADR-004.

    Defect class: precision improvement must not over-suppress. Slice-001
    is the canonical legitimate slice for both BC-PROJ-1 (fan-out) AND
    LLM-fence-parsing rules. Empirical: slice-001's mission-brief +
    design contain ZERO of the negative-anchor tokens — preservation is
    robust. The TF-1 PENDING -> WRITTEN-FAILING transition for this AC
    comes from the `negative_anchors` AttributeError pre-fix (mirror of
    slice-005's `test_migrated_rules_have_expected_anchors` per Critic M1
    pattern); reading the field as part of validation fails pre-fix.
    Rule reference: BC-1 v1.2 (slice-008 AC #4).
    """
    from tools.build_checks_audit import _parse_rules

    # Pre-fix genuineness: read negative_anchors as part of validation;
    # AttributeError pre-fix on missing field demonstrates non-coincidental
    # PENDING -> WRITTEN-FAILING transition.
    project_path = REPO_ROOT / "architecture" / "build-checks.md"
    project_text = project_path.read_text(encoding="utf-8")
    rules, _ = _parse_rules(
        project_text, source="project", path=str(project_path)
    )
    by_id = {r.rule_id: r for r in rules}
    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed"
    # Force read of negative_anchors field — AttributeError pre-fix
    _ = by_id["BC-PROJ-1"].negative_anchors

    result = audit_slice(
        slice_folder=REPO_ROOT / "architecture" / "slices" / "archive"
        / "slice-001-diagnose-orchestration-fix",
        project_checks=REPO_ROOT / "architecture" / "build-checks.md",
        global_checks=_GLOBAL_BUILD_CHECKS,
        changed_files=_SLICE_001_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}

    assert "BC-PROJ-1" in applicable_ids, (
        f"BC-PROJ-1 MUST apply to slice-001 (legitimate subagent-fan-out). "
        f"Got applicable: {applicable_ids}"
    )
    fence_rules = applicable_ids & {"BC-PROJ-2", "BC-GLOBAL-1"}
    if _GLOBAL_BUILD_CHECKS.exists():
        assert fence_rules, (
            f"At least one of BC-PROJ-2 / BC-GLOBAL-1 MUST apply to slice-001 "
            f"(legitimate fence-parsing). Got applicable: {applicable_ids}"
        )
    else:
        assert "BC-PROJ-2" in applicable_ids, (
            f"BC-PROJ-2 MUST apply to slice-001. Got applicable: {applicable_ids}"
        )


def test_negative_anchors_schema_documents_field_name_in_both_files():
    """Schema description prose in BOTH project + global build-checks files
    must mention the literal `Negative anchors` field name (case-sensitive).

    Defect class: a new schema field added without documentation is invisible
    to authors of future rules. Per slice-005 Critic M3 TWO-surface schema-
    pin discipline (slice-008 Critic M2 split into TWO substrings —
    field-name AND semantics).
    Rule reference: BC-1 v1.2 (slice-008 AC #5a; surface a — field-name).
    """
    project_text = (
        REPO_ROOT / "architecture" / "build-checks.md"
    ).read_text(encoding="utf-8")
    assert "Negative anchors" in project_text, (
        "architecture/build-checks.md schema description must mention the "
        "literal `Negative anchors` field name (case-sensitive)."
    )
    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pin is the canonical CI surface."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    assert "Negative anchors" in global_text, (
        f"{_GLOBAL_BUILD_CHECKS} schema description must mention the "
        f"literal `Negative anchors` field name (case-sensitive)."
    )


def test_negative_anchors_schema_documents_final_filter_semantics():
    """Schema description prose in BOTH project + global build-checks files
    must mention the literal `final filter` semantics phrase (case-
    insensitive — search via lowered text).

    Defect class: pinning ONLY the field name leaves the SEMANTICS phrase
    unprotected against doc refactor drift (per Critic M2). The `final
    filter` phrase encodes the universal post-applicability framing —
    losing it would let downstream rule authors miss that negative
    anchors compose UNIFORMLY across all three positive-applicability
    paths (always-true / glob / keyword), not just the keyword path.
    Mirrors slice-005's `word-boundary` semantics-phrase pin (per
    slice-005 Critic M3).
    Rule reference: BC-1 v1.2 (slice-008 AC #5b; surface b — semantics).
    """
    project_text = (
        REPO_ROOT / "architecture" / "build-checks.md"
    ).read_text(encoding="utf-8")
    assert "final filter" in project_text.lower(), (
        "architecture/build-checks.md schema description must mention the "
        "literal `final filter` semantics phrase (case-insensitive)."
    )
    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pin is the canonical CI surface."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    assert "final filter" in global_text.lower(), (
        f"{_GLOBAL_BUILD_CHECKS} schema description must mention the "
        f"literal `final filter` semantics phrase (case-insensitive)."
    )


def test_always_true_rule_with_negative_anchor_match_is_skipped(tmp_path: Path):
    """A rule with `Applies to: always: true` AND `Negative anchors: foo`
    is SUPPRESSED when slice text contains `foo`.

    Defect class: per slice-005 algorithm-path-conformance lesson (which
    slice-008 explicitly inherits via design.md), missing path coverage
    was the exact failure mode caught at /build-slice T5 last time.
    Slice-008's design.md Algorithm-path-conformance table claims the
    new mechanism applies UNIFORMLY across all three positive-applicability
    paths INCLUDING the `always: true` short-circuit. Without this test,
    the always-true path's new "always-EXCEPT-when-negative-anchor-matches"
    semantic is unverified. Per Critic M3 (slice-008) and Hendrickson's
    edge-case heuristics — distinct execution branches need distinct
    test cases when their semantics change.
    Rule reference: BC-1 v1.2 (slice-008 must-not-defer per Critic M3).
    """
    fixture_text = (
        "# Build checks (project-specific)\n"
        "\n"
        "## Rules\n"
        "\n"
        "## BC-PROJ-99 - Always-true rule with negative anchor\n"
        "\n"
        "**Severity**: Important\n"
        "**Applies to**: always: true\n"
        "**Negative anchors**: foo\n"
        "\n"
        "**Check**: This rule should be suppressed by negative anchor on slice text.\n"
    )
    fixture_path = tmp_path / "always_with_negative.md"
    fixture_path.write_text(fixture_text, encoding="utf-8")

    slice_folder = _make_slice(
        tmp_path / "slice-test",
        brief_text="# slice\nThis brief contains foo as the negative-anchor trigger.",
    )
    result = audit_slice(
        slice_folder=slice_folder,
        project_checks=fixture_path,
        global_checks=Path("/nonexistent/global.md"),
        changed_files=[],
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-99" not in applicable_ids, (
        f"BC-PROJ-99 (always: true + negative anchor matching) MUST be "
        f"suppressed by negative-anchor final filter. Got applicable: "
        f"{applicable_ids}"
    )
    assert "BC-PROJ-99" in skipped_ids, (
        f"BC-PROJ-99 should appear in skipped (rule was applicable via "
        f"always-true but final-filter suppressed). Got skipped: "
        f"{skipped_ids}"
    )


def test_negative_anchor_overlaps_positive_yields_violation(tmp_path: Path):
    """A rule whose negative anchors overlap with Trigger keywords OR
    Trigger anchors emits a `negative-anchor-overlaps-positive` violation.

    Defect class: input validation on the new `Negative anchors:` field
    is a must-not-defer item per mission-brief.md. An overlap is
    contradictory (the rule would never fire when its keyword/anchor is
    present, defeating the rule's domain). Mirrors slice-005's
    `anchor-not-in-keywords` pattern.
    Rule reference: BC-1 v1.2 (slice-008 must-not-defer input-validation).
    """
    from tools.build_checks_audit import _parse_rules

    fixture_text = (
        "# Build checks (project-specific)\n"
        "\n"
        "## Rules\n"
        "\n"
        "## BC-PROJ-99 - Test rule with overlapping negative anchor\n"
        "\n"
        "**Severity**: Important\n"
        "**Applies to**: src/**\n"
        "**Trigger keywords**: alpha, beta, gamma\n"
        "**Trigger anchors**: alpha\n"
        "**Negative anchors**: alpha\n"
        "\n"
        "**Check**: alpha is BOTH a positive trigger AND a negative anchor — "
        "audit MUST emit negative-anchor-overlaps-positive violation.\n"
    )
    fixture_path = tmp_path / "negative_overlaps_positive.md"
    fixture_path.write_text(fixture_text, encoding="utf-8")

    rules, violations = _parse_rules(
        fixture_text, source="project", path=str(fixture_path)
    )
    bad = [v for v in violations if v.kind == "negative-anchor-overlaps-positive"]
    assert len(bad) >= 1, (
        f"expected at least 1 negative-anchor-overlaps-positive violation; "
        f"got violations: {[(v.kind, v.message) for v in violations]}"
    )
    assert bad[0].rule_id == "BC-PROJ-99", (
        f"violation rule_id mismatch: got {bad[0].rule_id!r}, "
        f"expected 'BC-PROJ-99'"
    )
    assert "alpha" in bad[0].message, (
        f"violation message must reference the offending anchor 'alpha'; "
        f"got {bad[0].message!r}"
    )


def test_migrated_rules_have_expected_negative_anchors():
    """The 2 migrated rules (BC-PROJ-1, BC-GLOBAL-1) MUST parse to the
    expected canonical 9-token negative-anchor tuple.

    Defect class: a migration typo (e.g., `false-positive` instead of
    `false positive`) would silently NOT match because the slice texts
    in slice-005..007 use the space-form (per Critic m3). Pinning the
    exact tuple equality on the production rules makes typos fail loud.
    Mirrors slice-005's `test_migrated_rules_have_expected_anchors` per
    Critic M1 pattern. BC-PROJ-2 NOT asserted (per Critic M1 — not
    migrated; N=1 below promotion threshold).
    Rule reference: BC-1 v1.2 (slice-008 must-not-defer migration-tuple).
    """
    from tools.build_checks_audit import _parse_rules

    expected_negative_anchors = (
        "defer-with-rationale",
        "aggregated lessons",
        "false positive",
        "meta-discussion",
        "vocabulary",
        "critic-missed",
        "back-sync",
        "dim 9",
        "forward-sync",
    )

    project_path = REPO_ROOT / "architecture" / "build-checks.md"
    project_text = project_path.read_text(encoding="utf-8")
    rules, violations = _parse_rules(
        project_text, source="project", path=str(project_path)
    )
    by_id = {r.rule_id: r for r in rules}

    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed from project file"
    assert by_id["BC-PROJ-1"].negative_anchors == expected_negative_anchors, (
        f"BC-PROJ-1 negative_anchors mismatch: got "
        f"{by_id['BC-PROJ-1'].negative_anchors!r}, "
        f"expected {expected_negative_anchors!r}"
    )

    # No negative-anchor-overlaps-positive violations expected on production
    bad = [
        v for v in violations
        if v.kind == "negative-anchor-overlaps-positive"
    ]
    assert not bad, (
        f"production project build-checks.md emits negative-anchor-overlaps-"
        f"positive violations: {[(v.rule_id, v.message) for v in bad]}"
    )

    if not _GLOBAL_BUILD_CHECKS.exists():
        pytest.skip(
            f"global build-checks file not present at {_GLOBAL_BUILD_CHECKS}; "
            f"project pin is the canonical CI surface."
        )
    global_text = _GLOBAL_BUILD_CHECKS.read_text(encoding="utf-8")
    global_rules, global_violations = _parse_rules(
        global_text, source="global", path=str(_GLOBAL_BUILD_CHECKS)
    )
    global_by_id = {r.rule_id: r for r in global_rules}
    assert "BC-GLOBAL-1" in global_by_id, "BC-GLOBAL-1 not parsed"
    assert global_by_id["BC-GLOBAL-1"].negative_anchors == expected_negative_anchors, (
        f"BC-GLOBAL-1 negative_anchors mismatch: got "
        f"{global_by_id['BC-GLOBAL-1'].negative_anchors!r}, "
        f"expected {expected_negative_anchors!r}"
    )
