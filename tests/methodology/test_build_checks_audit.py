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


# slice-030A / ADR-028: BC-1 logic/tuple/schema-pin tests assert against these
# GIT-TRACKED canonical fixtures, NOT the gitignored live build-checks files.
# The live files are byte-reconstructed FROM these fixtures; BCI-1
# (tools/build_checks_integrity.py) is the always-running live↔fixture
# divergence gate. The literal-constant tuples in the test bodies below are
# the tracked oracle the fixtures are asserted *against* (fixture = subject,
# literal = oracle) — closing the v2-B3 / meta-M-add-3 unguarded-oracle hole.
# slice-031 (split-label 030B; SCMD-1 / ADR-030 / ADR-031): the archive-
# backtests are now DECOUPLED — they read the git-tracked canonical fixtures
# (BCI-1 guarantees live ≡ fixture) and a git-tracked verbatim archived-slice
# mini-corpus (ADR-030; membership = the SCMD-1 runtime derivation, NOT a
# hand list — incl. slice-001/002). No `_GLOBAL_BUILD_CHECKS` / live-vault /
# gitignored-archive read remains in any catalog-cited backtest.
_CANONICAL_PROJECT_FIXTURE = FIXTURES / "canonical_project_checks.md"
_CANONICAL_GLOBAL_FIXTURE = FIXTURES / "canonical_global_checks.md"
# ADR-030 verbatim corpus accessor (allowlisted in shippability_decoupling_
# audit._ALLOWLIST_SYMBOLS; rooted at REPO_ROOT → SCMD-1 classifies `clean`).
_ARCHIVE_BACKTEST_CORPUS = (
    REPO_ROOT / "tests" / "methodology" / "fixtures" / "archive_backtest_corpus"
)


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
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-003-add-val-1-imports-allowlist",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
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
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-004-fix-rr1-audit-docstring-or-regex",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
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
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}

    assert "BC-PROJ-2" in applicable_ids, (
        f"BC-PROJ-2 must apply to a brief that legitimately discusses "
        f"LLM-fence parsing. Got applicable: {applicable_ids}"
    )
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

    slice-030A/ADR-028: asserts the GIT-TRACKED canonical fixtures (not the
    gitignored live files) — the fixtures are always present, so the legacy
    skip-if-global-absent guard is removed.
    """
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    assert "Trigger anchors" in project_text, (
        f"{_CANONICAL_PROJECT_FIXTURE} schema description must mention the "
        "literal `Trigger anchors` field name (case-sensitive)."
    )
    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    assert "Trigger anchors" in global_text, (
        f"{_CANONICAL_GLOBAL_FIXTURE} schema description must mention the "
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

    slice-030A/ADR-028: asserts the git-tracked canonical fixtures.
    """
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    assert "word-boundary" in project_text, (
        f"{_CANONICAL_PROJECT_FIXTURE} schema description must mention the "
        "literal `word-boundary` semantics phrase (kebab-case)."
    )
    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    assert "word-boundary" in global_text, (
        f"{_CANONICAL_GLOBAL_FIXTURE} schema description must mention the "
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

    slice-030A/ADR-028 + meta-M-add-2: asserts the GIT-TRACKED canonical
    fixtures, and pins FULL structural identity — `applies_to` +
    `trigger_keywords` in addition to `trigger_anchors` — so an
    `applies_to`/`severity`/`keywords` mis-reconstruction (which the
    archive-backtests can coincidentally pass, _rule_applies L413-431)
    fails loud against this literal-constant oracle. The literal tuples
    here ARE the tracked oracle; the fixture is the subject.
    """
    from tools.build_checks_audit import _parse_rules

    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    rules, violations = _parse_rules(
        project_text, source="project", path=str(_CANONICAL_PROJECT_FIXTURE)
    )
    by_id = {r.rule_id: r for r in rules}

    # --- BC-PROJ-1 full structural identity (literal-constant oracle) ---
    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed from project fixture"
    p1 = by_id["BC-PROJ-1"]
    assert p1.trigger_anchors == ("subagent", "fan-out"), (
        f"BC-PROJ-1 anchors mismatch: got {p1.trigger_anchors!r}"
    )
    assert p1.applies_to == ("agents/**/*.md",), (
        f"BC-PROJ-1 applies_to mismatch: got {p1.applies_to!r}, "
        f"expected ('agents/**/*.md',)"
    )
    assert p1.trigger_keywords == (
        "subagent", "fan-out", "agent", "parallel", "spawn", "orchestrate",
    ), f"BC-PROJ-1 trigger_keywords mismatch: got {p1.trigger_keywords!r}"
    assert p1.severity == "Important", (
        f"BC-PROJ-1 severity mismatch: got {p1.severity!r}"
    )

    # --- BC-PROJ-2 full structural identity ---
    assert "BC-PROJ-2" in by_id, "BC-PROJ-2 not parsed from project fixture"
    p2 = by_id["BC-PROJ-2"]
    assert p2.trigger_anchors == ("fence", "code-block", "llm"), (
        f"BC-PROJ-2 anchors mismatch: got {p2.trigger_anchors!r}"
    )
    assert p2.applies_to == ("skills/**/*.py", "tools/**/*.py"), (
        f"BC-PROJ-2 applies_to mismatch: got {p2.applies_to!r}"
    )
    assert p2.trigger_keywords == (
        "fence", "code-block", "llm", "parse", "structured-output",
        "fenced", "output",
    ), f"BC-PROJ-2 trigger_keywords mismatch: got {p2.trigger_keywords!r}"
    assert p2.severity == "Important", (
        f"BC-PROJ-2 severity mismatch: got {p2.severity!r}"
    )

    # No anchor-not-in-keywords violations expected on the canonical fixture
    bad = [v for v in violations if v.kind == "anchor-not-in-keywords"]
    assert not bad, (
        f"canonical project fixture emits anchor-not-in-keywords "
        f"violations: {[(v.rule_id, v.message) for v in bad]}"
    )

    # --- BC-GLOBAL-1 full structural identity (global fixture) ---
    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    global_rules, _ = _parse_rules(
        global_text, source="global", path=str(_CANONICAL_GLOBAL_FIXTURE)
    )
    global_by_id = {r.rule_id: r for r in global_rules}
    assert "BC-GLOBAL-1" in global_by_id, "BC-GLOBAL-1 not parsed from global fixture"
    g1 = global_by_id["BC-GLOBAL-1"]
    assert g1.trigger_anchors == ("fence", "code-block", "llm", "structured-output"), (
        f"BC-GLOBAL-1 anchors mismatch: got {g1.trigger_anchors!r}"
    )
    # meta-M2 anti-circularity pin: slice-005 DEVIATION-1 value `**`
    # (NOT always:true — always:true short-circuits before the anchor
    # final-filter; an always:true mis-reconstruction would coincidentally
    # pass the archive-backtests via _rule_applies L413-414).
    assert g1.applies_to == ("**",), (
        f"BC-GLOBAL-1 applies_to mismatch: got {g1.applies_to!r}, "
        f"expected ('**',) — the slice-005 DEVIATION-1 value"
    )
    assert g1.trigger_keywords == (
        "parse", "fence", "code-block", "llm", "structured-output",
        "fenced", "output",
    ), f"BC-GLOBAL-1 trigger_keywords mismatch: got {g1.trigger_keywords!r}"
    assert g1.severity == "Important", (
        f"BC-GLOBAL-1 severity mismatch: got {g1.severity!r}"
    )


def test_bc_proj_3_and_bc_global_2_have_expected_structural_identity():
    """BC-PROJ-3 (project fixture) + BC-GLOBAL-2 (global fixture) MUST parse
    to their expected full structural identity.

    Defect class (slice-030A v2-B3 / meta-M-add-3): BC-PROJ-3 + BC-GLOBAL-2
    are the slice-028-promoted rules R-4's truncation *left behind*. They
    were NEVER pinned by any literal-constant test (the migrated-rules tests
    only cover BC-PROJ-1/2/BC-GLOBAL-1), so before this test the canonical
    fixture's content for these two rules had NO tracked oracle — sourced
    only from the suspect live file (a circular oracle). This test is that
    missing tracked oracle: literal-constant structural-identity pins
    authored from the surviving uncorrupted live bodies (best-recoverable;
    see slice-030A design.md M3 + ADR-028). The fixture is the subject;
    these literals are the oracle.

    Rule reference: BC-1 (slice-030A AC #2 — all-5-rule literal oracle).
    """
    from tools.build_checks_audit import _parse_rules

    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    p_rules, _ = _parse_rules(
        project_text, source="project", path=str(_CANONICAL_PROJECT_FIXTURE)
    )
    p_by_id = {r.rule_id: r for r in p_rules}
    assert "BC-PROJ-3" in p_by_id, "BC-PROJ-3 not parsed from project fixture"
    p3 = p_by_id["BC-PROJ-3"]
    assert p3.severity == "Critical", f"BC-PROJ-3 severity: {p3.severity!r}"
    assert p3.applies_to == ("always",), (
        f"BC-PROJ-3 applies_to mismatch: got {p3.applies_to!r}, "
        f"expected ('always',) — the always:true sentinel"
    )
    assert p3.trigger_keywords == (
        "validate", "demo", "revert", "fixture", "mutate", "git checkout",
        "git restore", "git stash", "scratch",
    ), f"BC-PROJ-3 trigger_keywords mismatch: got {p3.trigger_keywords!r}"
    assert p3.trigger_anchors == (), (
        f"BC-PROJ-3 trigger_anchors: expected () got {p3.trigger_anchors!r}"
    )
    assert p3.negative_anchors == (), (
        f"BC-PROJ-3 negative_anchors: expected () got {p3.negative_anchors!r}"
    )

    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    g_rules, _ = _parse_rules(
        global_text, source="global", path=str(_CANONICAL_GLOBAL_FIXTURE)
    )
    g_by_id = {r.rule_id: r for r in g_rules}
    assert "BC-GLOBAL-2" in g_by_id, "BC-GLOBAL-2 not parsed from global fixture"
    g2 = g_by_id["BC-GLOBAL-2"]
    assert g2.severity == "Critical", f"BC-GLOBAL-2 severity: {g2.severity!r}"
    assert g2.applies_to == ("always",), (
        f"BC-GLOBAL-2 applies_to mismatch: got {g2.applies_to!r}"
    )
    assert g2.trigger_keywords == (
        "revert", "rollback", "scratch edit", "temporary change", "demo",
        "restore", "git checkout", "git stash", "cleanup",
    ), f"BC-GLOBAL-2 trigger_keywords mismatch: got {g2.trigger_keywords!r}"
    assert g2.trigger_anchors == (), (
        f"BC-GLOBAL-2 trigger_anchors: expected () got {g2.trigger_anchors!r}"
    )
    assert g2.negative_anchors == (), (
        f"BC-GLOBAL-2 negative_anchors: expected () got {g2.negative_anchors!r}"
    )


def test_bc_proj_4_has_expected_structural_identity():
    """BC-PROJ-4 (slice-031 /reflect Step-5b promotion) MUST parse to its
    expected full structural identity. The canonical fixture is the subject;
    these literal constants are the git-tracked oracle (ADR-028; fixture =
    subject, literal = oracle). BCI-1 separately asserts the gitignored live
    `architecture/build-checks.md` matches the fixture structurally.

    Defect class: a /reflect Step-5b promotion that silently truncated or
    mis-authored BC-PROJ-4's structural fields would degrade BC-1 coverage
    with no loud signal (R-4 class). This literal pin + BCI-1 close that.

    Rule reference: BC-1 (slice-031 /reflect Step 5b; user-approved promotion).
    """
    from tools.build_checks_audit import _parse_rules

    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    p_rules, _ = _parse_rules(
        project_text, source="project", path=str(_CANONICAL_PROJECT_FIXTURE)
    )
    p_by_id = {r.rule_id: r for r in p_rules}
    assert "BC-PROJ-4" in p_by_id, "BC-PROJ-4 not parsed from project fixture"
    p4 = p_by_id["BC-PROJ-4"]
    assert p4.severity == "Important", f"BC-PROJ-4 severity: {p4.severity!r}"
    assert p4.applies_to == ("tools/**/*.py", "skills/**/*.md"), (
        f"BC-PROJ-4 applies_to mismatch: got {p4.applies_to!r}"
    )
    assert p4.trigger_keywords == (
        "audit", "gate", "regex", "field-line", "branch", "methodology",
        "prerequisite", "pre-finish", "skill", "classifier", "ast",
    ), f"BC-PROJ-4 trigger_keywords mismatch: got {p4.trigger_keywords!r}"
    assert p4.trigger_anchors == (), (
        f"BC-PROJ-4 trigger_anchors: expected () got {p4.trigger_anchors!r}"
    )
    assert p4.negative_anchors == (), (
        f"BC-PROJ-4 negative_anchors: expected () got {p4.negative_anchors!r}"
    )
    assert p4.check and p4.check.strip(), "BC-PROJ-4 check must be non-empty"


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
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-005-add-bc-1-keyword-precision",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
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
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-006-update-critic-with-cross-cutting-conformance-dimension",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
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
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-007-add-critique-agent-content-equality-audit",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
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
    project_path = _CANONICAL_PROJECT_FIXTURE
    project_text = project_path.read_text(encoding="utf-8")
    rules, _ = _parse_rules(
        project_text, source="project", path=str(project_path)
    )
    by_id = {r.rule_id: r for r in rules}
    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed"
    # Force read of negative_anchors field — AttributeError pre-fix
    _ = by_id["BC-PROJ-1"].negative_anchors

    result = audit_slice(
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-001-diagnose-orchestration-fix",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
        changed_files=_SLICE_001_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}

    assert "BC-PROJ-1" in applicable_ids, (
        f"BC-PROJ-1 MUST apply to slice-001 (legitimate subagent-fan-out). "
        f"Got applicable: {applicable_ids}"
    )
    fence_rules = applicable_ids & {"BC-PROJ-2", "BC-GLOBAL-1"}
    assert fence_rules, (
        f"At least one of BC-PROJ-2 / BC-GLOBAL-1 MUST apply to slice-001 "
        f"(legitimate fence-parsing). Got applicable: {applicable_ids}"
    )
def test_negative_anchors_schema_documents_field_name_in_both_files():
    """Schema description prose in BOTH project + global build-checks files
    must mention the literal `Negative anchors` field name (case-sensitive).

    Defect class: a new schema field added without documentation is invisible
    to authors of future rules. Per slice-005 Critic M3 TWO-surface schema-
    pin discipline (slice-008 Critic M2 split into TWO substrings —
    field-name AND semantics).
    Rule reference: BC-1 v1.2 (slice-008 AC #5a; surface a — field-name).

    slice-030A/ADR-028: asserts the git-tracked canonical fixtures.
    """
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    assert "Negative anchors" in project_text, (
        f"{_CANONICAL_PROJECT_FIXTURE} schema description must mention the "
        "literal `Negative anchors` field name (case-sensitive)."
    )
    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    assert "Negative anchors" in global_text, (
        f"{_CANONICAL_GLOBAL_FIXTURE} schema description must mention the "
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

    slice-030A/ADR-028: asserts the git-tracked canonical fixtures.
    """
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    assert "final filter" in project_text.lower(), (
        f"{_CANONICAL_PROJECT_FIXTURE} schema description must mention the "
        "literal `final filter` semantics phrase (case-insensitive)."
    )
    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    assert "final filter" in global_text.lower(), (
        f"{_CANONICAL_GLOBAL_FIXTURE} schema description must mention the "
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

    # slice-030A/ADR-028: assert the git-tracked canonical fixtures.
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    rules, violations = _parse_rules(
        project_text, source="project", path=str(_CANONICAL_PROJECT_FIXTURE)
    )
    by_id = {r.rule_id: r for r in rules}

    assert "BC-PROJ-1" in by_id, "BC-PROJ-1 not parsed from project fixture"
    assert by_id["BC-PROJ-1"].negative_anchors == expected_negative_anchors, (
        f"BC-PROJ-1 negative_anchors mismatch: got "
        f"{by_id['BC-PROJ-1'].negative_anchors!r}, "
        f"expected {expected_negative_anchors!r}"
    )

    # No negative-anchor-overlaps-positive violations expected on the fixture
    bad = [
        v for v in violations
        if v.kind == "negative-anchor-overlaps-positive"
    ]
    assert not bad, (
        f"canonical project fixture emits negative-anchor-overlaps-"
        f"positive violations: {[(v.rule_id, v.message) for v in bad]}"
    )

    global_text = _CANONICAL_GLOBAL_FIXTURE.read_text(encoding="utf-8")
    global_rules, global_violations = _parse_rules(
        global_text, source="global", path=str(_CANONICAL_GLOBAL_FIXTURE)
    )
    global_by_id = {r.rule_id: r for r in global_rules}
    assert "BC-GLOBAL-1" in global_by_id, "BC-GLOBAL-1 not parsed"
    assert global_by_id["BC-GLOBAL-1"].negative_anchors == expected_negative_anchors, (
        f"BC-GLOBAL-1 negative_anchors mismatch: got "
        f"{global_by_id['BC-GLOBAL-1'].negative_anchors!r}, "
        f"expected {expected_negative_anchors!r}"
    )


# --- Slice-012 / BC-PROJ-2 negative-anchor migration (BC-1 v1.3) ---
#
# Per ADR-011 (slice-012, 2026-05-13), BC-PROJ-2 receives the same 9-token
# methodology-vocabulary `Negative anchors:` set used for BC-PROJ-1 +
# BC-GLOBAL-1 at slice-008. Migration is data-only; reuses BC-1 v1.2
# infrastructure (slice-008's `_parse_rules` + `_negative_anchor_match` +
# final-filter algorithm) verbatim.
#
# Per /critique B1 ACCEPTED-FIXED: AC #4 test MUST use `_parse_rules` +
# `by_id['BC-PROJ-2'].negative_anchors == expected_tuple` per-rule scoping
# — NOT naive file-level substring — because all 9 tokens already exist on
# BC-PROJ-1's L20 Negative-anchors line file-globally from slice-008.
# A naive substring check would PASS pre-migration, violating TF-1
# PENDING -> WRITTEN-FAILING genuine-failure discipline (N=8 stable per
# slice-011 reflection).

# Representative --changed-files for slice-011 archive backtest (BC-PROJ-2
# glob `skills/**/*.py, tools/**/*.py`). Mirrors `_SLICE_005_CHANGED_FILES`
# pattern at L693.
_SLICE_011_CHANGED_FILES = [
    "tools/build_checks_audit.py",
]


def test_slice_005_archive_no_longer_fires_proj2():
    """Slice-005 archive must NOT trigger BC-PROJ-2 post-migration.

    Defect class: methodology-vocabulary slice-005 fires BC-PROJ-2 at build-
    time via the glob path (`tools/build_checks_audit.py` matches
    `skills/**/*.py, tools/**/*.py`) AND via the keyword-anchor path (bare-
    word `fence`, `code-block`, `llm` match BC-PROJ-2's Trigger anchors).
    Slice-012's 9-token negative-anchor migration suppresses BC-PROJ-2
    because slice-005's text matches `defer-with-rationale, aggregated
    lessons, false positive, meta-discussion, vocabulary` (5 distinct
    negative-anchor hits per design.md Audit 3).

    This is the N=1 evidence base per slice-008 Critic M1's BC-PROJ-2-
    specific N=2 deferral language; ratified at slice-012 per N=2 met
    (slice-005 + slice-011).

    Rule reference: BC-1 v1.3 (slice-012 AC #1).
    """
    result = audit_slice(
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-005-add-bc-1-keyword-precision",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
        changed_files=_SLICE_005_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-2" not in applicable_ids, (
        f"BC-PROJ-2 should NOT apply to slice-005 archive post-migration "
        f"(silenced via 9-token methodology-vocabulary negative anchors). "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-2" in skipped_ids, (
        f"BC-PROJ-2 should appear in skipped (rule was applicable via glob "
        f"+ keyword paths, final-filter suppressed). Got skipped: {skipped_ids}"
    )


def test_slice_011_archive_no_longer_fires_proj2():
    """Slice-011 archive must NOT trigger BC-PROJ-2 post-migration.

    Defect class: methodology-vocabulary slice-011 (RSAD-1 codification)
    fires BC-PROJ-2 at /critique time via the keyword-anchor path on
    `fence`, `code-block`, `llm` (slice-011's mission-brief + design.md
    contain 26 BC-PROJ-2 positive-anchor matches as historical-lesson
    context, not as LLM-fence-parsing implementation). Slice-012's 9-token
    negative-anchor migration suppresses BC-PROJ-2 because slice-011's
    text matches 8 distinct negative-anchor tokens (per design.md Audit 3:
    `defer-with-rationale, aggregated lessons, meta-discussion, vocabulary,
    Critic-MISSED, back-sync, Dim 9, forward-sync`).

    This is the N=2 evidence base — slice-011's BC-PROJ-2 fire is the
    N=2 promotion-threshold-met recurrence per slice-008 Critic M1 deferral
    language ("defer BC-PROJ-2 migration until N=2 surfaces").

    Rule reference: BC-1 v1.3 (slice-012 AC #2).
    """
    result = audit_slice(
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
        changed_files=_SLICE_011_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}
    skipped_ids = {r.rule_id for r in result.skipped}

    assert "BC-PROJ-2" not in applicable_ids, (
        f"BC-PROJ-2 should NOT apply to slice-011 archive post-migration "
        f"(silenced via 9-token methodology-vocabulary negative anchors). "
        f"Got applicable: {applicable_ids}"
    )
    assert "BC-PROJ-2" in skipped_ids, (
        f"BC-PROJ-2 should appear in skipped (rule was applicable via glob "
        f"+ keyword paths, final-filter suppressed). Got skipped: {skipped_ids}"
    )


def test_slice_001_archive_still_fires_proj2():
    """Slice-001 archive (canonical legitimate LLM-fence-parsing slice)
    MUST continue to fire BC-PROJ-2 post-migration — backward-compat
    covenant per ADR-007 / ADR-011.

    Defect class: precision improvement must not over-suppress. Slice-001
    is the canonical legitimate slice for BC-PROJ-2 (4-backtick outer
    fence parser at `skills/diagnose/write_pass.py`). Empirical per
    design.md Audit 2: slice-001's mission-brief + design contain ZERO of
    the 9 methodology-vocabulary negative-anchor tokens at word-boundary
    — negative-anchor filter cannot suppress. BC-PROJ-2 continues to fire
    via positive anchors (`fence`, `code-block`, `llm`) AND glob path
    (`skills/diagnose/write_pass.py` matches `Applies to: skills/**/*.py`).

    Per /critique B1 ACCEPTED-FIXED: TF-1 PENDING -> WRITTEN-FAILING
    genuineness uses the `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors`
    read pattern (mirrors slice-008's `test_slice_001_archive_still_fires_
    legitimate_rules` at L843 + reuses the same `_parse_rules` API).

    Rule reference: BC-1 v1.3 (slice-012 AC #3).
    """
    from tools.build_checks_audit import _parse_rules

    # Pre-fix genuineness via slice-008 Critic M1 pattern: force read of
    # the field as part of validation. Post-migration, BC-PROJ-2 has the
    # 9-token tuple populated; pre-migration, it parses to () which then
    # fails the assertion `BC-PROJ-2 in applicable` below for slice-001.
    project_path = _CANONICAL_PROJECT_FIXTURE
    project_text = project_path.read_text(encoding="utf-8")
    rules, _ = _parse_rules(
        project_text, source="project", path=str(project_path)
    )
    by_id = {r.rule_id: r for r in rules}
    assert "BC-PROJ-2" in by_id, "BC-PROJ-2 not parsed"
    _ = by_id["BC-PROJ-2"].negative_anchors  # field-read assertion (slice-008 pattern)

    result = audit_slice(
        slice_folder=_ARCHIVE_BACKTEST_CORPUS
        / "slice-001-diagnose-orchestration-fix",
        project_checks=_CANONICAL_PROJECT_FIXTURE,
        global_checks=_CANONICAL_GLOBAL_FIXTURE,
        changed_files=_SLICE_001_CHANGED_FILES,
        skip_if_carry_over=False,
    )
    applicable_ids = {r.rule_id for r in result.applicable}

    # Mini-CAD-1 row 3 PASSING -> WRITTEN-FAILING -> PASSING transition
    # (per slice-007/009/010/011 N=4 stable -> N=5 stable post-slice-012):
    # this assertion was temporarily flipped to `not in` at Phase 1a to
    # establish a genuine WRITTEN-FAILING signal pre-migration; flipped
    # back to `in` at Phase 1a-verify, then verified to PASS post-Phase 2
    # migration. The final-form assertion below is what guards backward-
    # compat at every future audit run.
    assert "BC-PROJ-2" in applicable_ids, (
        f"BC-PROJ-2 MUST apply to slice-001 (legitimate LLM-fence-parsing). "
        f"Backward-compat covenant per ADR-007 / ADR-011: slice-001's text "
        f"contains zero methodology-vocabulary tokens, so the 9-token "
        f"negative-anchor filter cannot suppress. "
        f"Got applicable: {applicable_ids}"
    )


def test_bc_proj_2_has_methodology_vocabulary_negative_anchors():
    """BC-PROJ-2 MUST parse to the canonical 9-token negative-anchor tuple.

    Per /critique B1 ACCEPTED-FIXED: this test uses `_parse_rules` +
    `by_id['BC-PROJ-2'].negative_anchors == expected_tuple` per-rule
    scoping on the parsed `BuildCheckRule` dataclass — NOT a naive file-
    level substring check. Reason: all 9 canonical tokens already exist
    file-globally on BC-PROJ-1's `architecture/build-checks.md:20`
    Negative-anchors line from slice-008's migration. A naive substring
    check would PASS pre-slice-012-migration, violating TF-1 PENDING ->
    WRITTEN-FAILING genuine-failure discipline (N=8 stable per slice-011
    reflection).

    Pinned failure signal pre-fix:
        AssertionError: BC-PROJ-2 negative_anchors mismatch: got (),
        expected (...)

    Mirrors slice-008's `test_migrated_rules_have_expected_negative_anchors`
    at L1054.

    Rule reference: BC-1 v1.3 (slice-012 AC #4).
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

    # slice-030A/ADR-028: assert the git-tracked canonical project fixture.
    project_text = _CANONICAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    rules, violations = _parse_rules(
        project_text, source="project", path=str(_CANONICAL_PROJECT_FIXTURE)
    )
    by_id = {r.rule_id: r for r in rules}

    assert "BC-PROJ-2" in by_id, (
        "BC-PROJ-2 not parsed from canonical project fixture"
    )
    assert by_id["BC-PROJ-2"].negative_anchors == expected_negative_anchors, (
        f"BC-PROJ-2 negative_anchors mismatch: got "
        f"{by_id['BC-PROJ-2'].negative_anchors!r}, "
        f"expected {expected_negative_anchors!r}"
    )

    # No negative-anchor-overlaps-positive violations expected on BC-PROJ-2
    # (Audit 1 at design time: 9-token set disjoint from BC-PROJ-2's
    # `parse, fence, code-block, backtick, llm, agent, prompt, output,
    # response` keywords + `fence, code-block, llm` anchors).
    bc_proj_2_violations = [
        v for v in violations
        if v.rule_id == "BC-PROJ-2" and v.kind == "negative-anchor-overlaps-positive"
    ]
    assert not bc_proj_2_violations, (
        f"BC-PROJ-2 emits negative-anchor-overlaps-positive violations: "
        f"{[(v.rule_id, v.message) for v in bc_proj_2_violations]}"
    )
