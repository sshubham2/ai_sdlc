"""Tests for tools.validate_slice_layers (VAL-1).

Layer A — credential scan:
  - Detects AWS keys, GitHub PATs, JWTs, private keys, Anthropic keys,
    generic api-key patterns
  - Allowlist suppresses matches
  - Critical severity (cannot defer)

Layer B — dependency hallucination check (Python only in v1):
  - Parses imports via ast
  - Skips stdlib (sys.stdlib_module_names)
  - Skips relative imports
  - Resolves declared deps from pyproject.toml + requirements.txt
  - Resolves common aliases (yaml -> pyyaml, bs4 -> beautifulsoup4)
  - Flags undeclared imports as Important hallucinated-import findings

Plus skill prose pins for /validate-slice.

Rule reference: VAL-1.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

from tests.methodology.conftest import REPO_ROOT
from tools.validate_slice_layers import (
    _VAL_1_RELEASE_DATE,
    _check_import_resolves,
    _extract_pkg_name,
    _normalize_pkg,
    _read_allowlist,
    parse_declared_deps,
    run_layers,
    scan_imports,
    scan_secrets,
)


FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures" / "validate_layers"


# --- Unit tests for parser helpers ---

def test_extract_pkg_name_handles_specifiers():
    """`anthropic>=0.34.0[extras]` -> `anthropic`.

    Defect class: Without spec stripping, declared deps stay version-tagged
    and never match the bare import name.
    Rule reference: VAL-1.
    """
    assert _extract_pkg_name("anthropic>=0.34.0") == "anthropic"
    assert _extract_pkg_name("anthropic[extras]>=0.34") == "anthropic"
    assert _extract_pkg_name("anthropic ==0.34.0") == "anthropic"
    assert _extract_pkg_name("anthropic # comment") == "anthropic"
    assert _extract_pkg_name("# pure comment") == ""


def test_normalize_pkg_pep503():
    """Normalization lowercases + collapses [-_.]+ to single underscore.

    Defect class: PEP 503 requires `Pillow` and `pillow` to match;
    failing this means a project declaring `Pillow` won't satisfy
    `import PIL`.
    Rule reference: VAL-1.
    """
    assert _normalize_pkg("PyYAML") == "pyyaml"
    assert _normalize_pkg("scikit-learn") == "scikit_learn"
    assert _normalize_pkg("python.dateutil") == "python_dateutil"


def test_parse_declared_deps_pyproject():
    """pyproject.toml [project.dependencies] + optional-dependencies parsed.

    Defect class: A parser missing optional-dependencies would silently
    skip dev deps, flagging legitimate dev imports as hallucinated.
    Rule reference: VAL-1.
    """
    deps = parse_declared_deps(
        FIXTURES / "pyproject_fixture.toml",
        None,
    )
    assert "anthropic" in deps
    assert "requests" in deps
    assert "pyyaml" in deps
    assert "beautifulsoup4" in deps
    assert "pytest" in deps  # from optional-dependencies


def test_parse_declared_deps_requirements():
    """Legacy requirements.txt parsing handles version specs + comments.

    Defect class: Old projects without pyproject.toml would have all
    imports flagged.
    Rule reference: VAL-1.
    """
    deps = parse_declared_deps(
        None,
        FIXTURES / "requirements_fixture.txt",
    )
    assert "anthropic" in deps
    assert "requests" in deps
    assert "pyyaml" in deps  # PyYAML normalizes to pyyaml
    assert "beautifulsoup4" in deps


def test_check_import_resolves_stdlib():
    """stdlib import resolves without needing declaration.

    Defect class: Flagging stdlib imports would drown the audit in noise.
    Rule reference: VAL-1.
    """
    assert _check_import_resolves("json", set()) is True
    assert _check_import_resolves("pathlib", set()) is True
    assert _check_import_resolves("re", set()) is True


def test_check_import_resolves_alias():
    """Alias resolution: yaml when pyyaml is declared.

    Defect class: Without alias resolution, `import yaml` would be flagged
    even though pyyaml is correctly declared.
    Rule reference: VAL-1.
    """
    assert _check_import_resolves("yaml", {"pyyaml"}) is True
    assert _check_import_resolves("PIL", {"pillow"}) is True
    assert _check_import_resolves("bs4", {"beautifulsoup4"}) is True


# --- Layer A: credential scan tests ---

def test_secrets_clean_file_yields_no_findings():
    """A file with no secret patterns produces zero findings.

    Defect class: A scanner with false positives on plain config trains
    users to ignore it.
    Rule reference: VAL-1.
    """
    findings, suppressed = scan_secrets([FIXTURES / "secrets_clean.txt"], [])
    assert findings == []
    assert suppressed == 0


def test_secrets_aws_access_key_detected():
    """`AKIA...` pattern detected with Critical severity.

    Defect class: AWS access keys committed to source are
    immediately exploitable; missing them is a security hole.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_aws.txt"], [])
    aws = [f for f in findings if f.pattern_name == "aws-access-key"]
    assert len(aws) == 1
    assert aws[0].severity == "Critical"


def test_secrets_github_pat_detected():
    """`ghp_...` and `github_pat_...` patterns both fire.

    Defect class: Multiple GitHub token formats — missing any is a gap.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_github.txt"], [])
    classics = [f for f in findings if f.pattern_name == "github-token-classic"]
    fine = [f for f in findings if f.pattern_name == "github-token-fine"]
    bots = [f for f in findings if f.pattern_name == "github-token-other"]
    assert len(classics) == 1
    assert len(fine) == 1
    assert len(bots) == 1


def test_secrets_jwt_detected():
    """JWT shape `eyJ.*\\..*\\..*` detected.

    Defect class: JWTs in source are usually session-bearer or signing
    secrets; committing them is a compromise.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_jwt.py"], [])
    jwts = [f for f in findings if f.pattern_name == "jwt"]
    assert len(jwts) == 1


def test_secrets_private_key_detected():
    """`-----BEGIN ... PRIVATE KEY-----` detected.

    Defect class: PEM private keys committed are catastrophic; the most
    important pattern to catch.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_private_key.txt"], [])
    keys = [f for f in findings if f.pattern_name == "private-key"]
    assert len(keys) == 1


def test_secrets_anthropic_key_detected():
    """Anthropic `sk-ant-...` keys detected.

    Defect class: AI-assisted projects often use Anthropic keys; without
    a specific pattern, generic-api-key may miss the prefix shape.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_anthropic.txt"], [])
    anthropic_keys = [f for f in findings if f.pattern_name == "anthropic-key"]
    assert len(anthropic_keys) == 1


def test_secrets_generic_api_key_detected():
    """Generic `api_key = "..."` patterns detected.

    Defect class: The catch-all for vendor-specific keys not yet in our
    pattern set.
    Rule reference: VAL-1.
    """
    findings, _ = scan_secrets([FIXTURES / "secrets_generic.py"], [])
    generic = [f for f in findings if f.pattern_name == "generic-api-key"]
    assert len(generic) >= 1


def test_secrets_allowlist_suppresses_match():
    """Allowlisted patterns are suppressed (not emitted as findings).

    Defect class: Without an allowlist, fixture-/example-shaped secrets
    create unfixable Critical findings on every test run.
    Rule reference: VAL-1.
    """
    allowlist = _read_allowlist(FIXTURES / "secrets_allowlist.txt")
    findings, suppressed = scan_secrets(
        [FIXTURES / "secrets_allowlisted.txt"],
        allowlist,
    )
    aws = [f for f in findings if f.pattern_name == "aws-access-key"]
    assert aws == []  # suppressed
    assert suppressed >= 1


def test_secrets_skipped_when_skip_secrets_true(tmp_path: Path):
    """run_layers(skip_secrets=True) returns no secret findings.

    Defect class: Without a skip flag, projects with their own secret
    scanner can't disable Layer A.
    Rule reference: VAL-1.
    """
    slice_folder = tmp_path / "slice-001-test"
    slice_folder.mkdir()
    (slice_folder / "mission-brief.md").write_text("# slice", encoding="utf-8")
    result = run_layers(
        slice_folder=slice_folder,
        changed_files=[FIXTURES / "secrets_aws.txt"],
        skip_secrets=True,
    )
    assert result.secret_findings == []


# --- Layer B: dependency hallucination tests ---

def test_imports_clean_file_has_no_findings():
    """Stdlib + declared imports produce zero findings.

    Defect class: False positives on legit imports train users to ignore.
    Rule reference: VAL-1.
    """
    declared = parse_declared_deps(FIXTURES / "pyproject_fixture.toml", None)
    findings = scan_imports([FIXTURES / "imports_clean.py"], declared)
    assert findings == []


def test_imports_hallucinated_pkg_flagged():
    """Undeclared package imports are flagged Important.

    Defect class: AI implementations commonly hallucinate package names;
    without a check, they silently break at runtime.
    Rule reference: VAL-1.
    """
    declared = parse_declared_deps(FIXTURES / "pyproject_fixture.toml", None)
    findings = scan_imports([FIXTURES / "imports_hallucinated.py"], declared)
    flagged_names = {f.import_name for f in findings}
    assert "nonexistent_pkg" in flagged_names
    assert "another_phantom" in flagged_names
    # anthropic is declared, must NOT be flagged
    assert "anthropic" not in flagged_names


def test_imports_aliased_resolves_to_declared():
    """`import yaml` resolves when pyyaml is declared (alias table).

    Defect class: Without the alias table, every project using yaml/PIL/bs4
    would see false positives.
    Rule reference: VAL-1.
    """
    declared = parse_declared_deps(FIXTURES / "pyproject_fixture.toml", None)
    findings = scan_imports([FIXTURES / "imports_aliased.py"], declared)
    assert findings == []


def test_imports_relative_skipped():
    """Relative imports (`from . import x`) are skipped — never flagged.

    Defect class: Relative imports refer to project-internal modules;
    flagging them would create noise on every project.
    Rule reference: VAL-1.
    """
    declared = parse_declared_deps(FIXTURES / "pyproject_fixture.toml", None)
    findings = scan_imports([FIXTURES / "imports_relative.py"], declared)
    assert findings == []


def test_imports_skipped_when_skip_deps_true(tmp_path: Path):
    """run_layers(skip_deps=True) returns no import findings.

    Defect class: Projects with their own dep linter need a way to disable
    Layer B without affecting Layer A.
    Rule reference: VAL-1.
    """
    slice_folder = tmp_path / "slice-001-test"
    slice_folder.mkdir()
    (slice_folder / "mission-brief.md").write_text("# slice", encoding="utf-8")
    result = run_layers(
        slice_folder=slice_folder,
        changed_files=[FIXTURES / "imports_hallucinated.py"],
        pyproject=FIXTURES / "pyproject_fixture.toml",
        skip_deps=True,
    )
    assert result.import_findings == []


# --- run_layers integration ---

def test_run_layers_combines_both_layers(tmp_path: Path):
    """Both layers run; result aggregates findings + summary counts.

    Defect class: Independent layers must be runnable together at /validate.
    Rule reference: VAL-1.
    """
    slice_folder = tmp_path / "slice-001-test"
    slice_folder.mkdir()
    (slice_folder / "mission-brief.md").write_text("# slice", encoding="utf-8")
    result = run_layers(
        slice_folder=slice_folder,
        changed_files=[
            FIXTURES / "secrets_aws.txt",
            FIXTURES / "imports_hallucinated.py",
        ],
        pyproject=FIXTURES / "pyproject_fixture.toml",
    )
    assert len(result.secret_findings) >= 1
    assert len(result.import_findings) >= 1
    summary = result.to_dict()["summary"]
    assert summary["critical_count"] >= 1
    assert summary["important_count"] >= 1


# --- Carry-over tests ---

def _set_brief_mtime(brief: Path, target_date) -> None:
    target_dt = datetime.combine(target_date, datetime.min.time().replace(hour=12))
    ts = target_dt.timestamp()
    os.utime(brief, (ts, ts))


def test_carry_over_exempts_old_slice(tmp_path: Path):
    """Slice with mtime predating VAL-1 release is exempt.

    Defect class: Retroactively applying VAL-1 would refuse archived
    slices that may legitimately have committed test fixtures.
    Rule reference: VAL-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _VAL_1_RELEASE_DATE - timedelta(days=30))

    result = run_layers(
        slice_folder=slice_folder,
        changed_files=[FIXTURES / "secrets_aws.txt"],
    )
    assert result.carry_over_exempt is True
    assert result.secret_findings == []


def test_no_carry_over_flag_disables_exemption(tmp_path: Path):
    """skip_if_carry_over=False audits even old slices.

    Defect class: Archive scans need a way to override carry-over.
    Rule reference: VAL-1.
    """
    slice_folder = tmp_path / "slice-001-old"
    slice_folder.mkdir()
    brief = slice_folder / "mission-brief.md"
    brief.write_text("# old slice", encoding="utf-8")
    _set_brief_mtime(brief, _VAL_1_RELEASE_DATE - timedelta(days=30))

    result = run_layers(
        slice_folder=slice_folder,
        changed_files=[FIXTURES / "secrets_aws.txt"],
        skip_if_carry_over=False,
    )
    assert result.carry_over_exempt is False
    assert any(f.pattern_name == "aws-access-key" for f in result.secret_findings)


# --- Skill prose pins ---

def test_validate_slice_skill_references_val_1():
    """skills/validate-slice/SKILL.md must reference VAL-1 + the audit.

    Defect class: Without the skill referencing VAL-1, the layered
    safety checks become opt-in / forgotten.
    Rule reference: VAL-1.
    """
    text = (REPO_ROOT / "skills" / "validate-slice" / "SKILL.md").read_text(encoding="utf-8")
    assert "VAL-1" in text, "no VAL-1 reference in /validate-slice SKILL.md"
    assert "validate_slice_layers" in text, (
        "no validate_slice_layers module reference"
    )
    assert "credential scan" in text.lower()
    assert "hallucinat" in text.lower(), "dep-hallucination layer prose missing"
