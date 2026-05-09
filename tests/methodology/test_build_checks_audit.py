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
