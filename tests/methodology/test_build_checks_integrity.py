"""Regression tests for tools.build_checks_integrity (BCI-1).

Per BCI-1 (methodology-changelog.md v0.44.0; slice-030A; ADR-028/029).
Exercises the DETERMINISTIC tool (slice-030A B2-correct: there is no
`/reflect` promotion function to test — Step 5b is LLM prose; the testable
artifact is this downstream gate):

  - PASS (exit 0, conformant) on a faithful canonical reconstruction
  - HALT (exit 1, attributed message) on a 1-rule truncation
  - HALT (exit 1) on a SINGLE corrupted `Applies to:` field — proves the
    check is FULL structural identity, NOT rule-ID-set-only (meta-M-add-2:
    all rule IDs still present, only a field differs)
  - HALT (exit 1) on a SINGLE corrupted `Severity:` field
  - WARN (exit 0) on an ABSENT global file (meta-M3: optional-install, not
    vault drift)
  - HALT (exit 1) on an EMPTY but PRESENT global file (meta-M3: empty !=
    absent — R-4-global not silently reopened)

Rule reference: BCI-1 (slice-030A AC #3 + #4).
"""
from pathlib import Path

import pytest

from tests.methodology.conftest import REPO_ROOT
from tools.build_checks_integrity import check_live, main

_REAL_PROJECT_FIXTURE = (
    REPO_ROOT / "tests" / "methodology" / "fixtures"
    / "build_checks" / "canonical_project_checks.md"
)
_REAL_GLOBAL_FIXTURE = (
    REPO_ROOT / "tests" / "methodology" / "fixtures"
    / "build_checks" / "canonical_global_checks.md"
)


def _make_root(tmp_path: Path, project_live: str | None, *,
               project_fixture: str | None = None) -> Path:
    """Build a synthetic repo root with the fixture + (optional) live file."""
    root = tmp_path / "repo"
    fx_dir = root / "tests" / "methodology" / "fixtures" / "build_checks"
    fx_dir.mkdir(parents=True, exist_ok=True)
    (fx_dir / "canonical_project_checks.md").write_text(
        project_fixture
        if project_fixture is not None
        else _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (fx_dir / "canonical_global_checks.md").write_text(
        _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8"
    )
    if project_live is not None:
        (root / "architecture").mkdir(parents=True, exist_ok=True)
        (root / "architecture" / "build-checks.md").write_text(
            project_live, encoding="utf-8"
        )
    return root


@pytest.fixture
def fake_home(tmp_path, monkeypatch):
    """Point Path.home() at a tmp dir so the global-file branch is isolated."""
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        "tools.build_checks_integrity.Path.home", lambda: home
    )
    return home


def _write_global(home: Path, text: str | None) -> None:
    gp = home / ".claude" / "build-checks.md"
    if text is None:
        if gp.exists():
            gp.unlink()
        return
    gp.write_text(text, encoding="utf-8")


def test_bci1_pass_on_faithful_reconstruction(tmp_path, fake_home):
    """Live == fixture on both surfaces ⇒ conformant, exit 0."""
    root = _make_root(
        tmp_path, _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    )
    _write_global(fake_home, _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"))
    r = check_live(root)
    assert r.exit_code == 0, r.divergences
    assert r.status == "conformant", r.to_dict()


def test_bci1_halts_on_one_rule_truncation(tmp_path, fake_home):
    """The R-4 signature: project file truncated to a single rule ⇒ HALT."""
    truncated = "\n\n## BC-PROJ-3 — only rule left\n\n" \
        "**Severity**: Critical\n**Applies to**: always: true\n" \
        "**Trigger keywords**: x\n\n**Check**: c\n"
    root = _make_root(tmp_path, truncated)
    _write_global(fake_home, _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"))
    r = check_live(root)
    assert r.exit_code == 1, r.to_dict()
    assert r.status == "drift"
    blob = "\n".join(r.divergences)
    assert "MISSING canonical rule" in blob
    assert "NOT a slice regression" in blob


def test_bci1_halts_on_single_corrupted_applies_to_field(tmp_path, fake_home):
    """All rule IDs present but ONE `Applies to:` differs ⇒ HALT.

    Proves FULL structural identity, not rule-ID-set-only (meta-M-add-2).
    """
    good = _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    corrupted = good.replace(
        "**Applies to**: agents/**/*.md",
        "**Applies to**: always: true",
    )
    assert corrupted != good, "fixture text changed — update this test"
    root = _make_root(tmp_path, corrupted)
    _write_global(fake_home, _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"))
    r = check_live(root)
    assert r.exit_code == 1, r.to_dict()
    blob = "\n".join(r.divergences)
    assert "structural-identity mismatch" in blob
    assert "BC-PROJ-1" in blob


def test_bci1_halts_on_single_corrupted_severity_field(tmp_path, fake_home):
    """A downgraded `Severity:` (IDs all present) ⇒ HALT (full identity)."""
    good = _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    # BC-PROJ-3 is Critical; downgrade it.
    corrupted = good.replace(
        "**Severity**: Critical\n**Applies to**: always: true",
        "**Severity**: Important\n**Applies to**: always: true",
        1,
    )
    assert corrupted != good
    root = _make_root(tmp_path, corrupted)
    _write_global(fake_home, _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"))
    r = check_live(root)
    assert r.exit_code == 1, r.to_dict()
    assert "structural-identity mismatch" in "\n".join(r.divergences)


def test_bci1_warns_not_halts_on_absent_global(tmp_path, fake_home):
    """Absent global file = optional-install ⇒ WARN, exit 0 (meta-M3)."""
    root = _make_root(
        tmp_path, _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    )
    _write_global(fake_home, None)  # absent
    r = check_live(root)
    assert r.exit_code == 0, r.to_dict()
    assert r.status == "warn"
    assert any("global build-checks file absent" in w for w in r.warnings)


def test_bci1_halts_on_empty_present_global(tmp_path, fake_home):
    """Empty BUT PRESENT global ⇒ HALT (meta-M3: empty != absent)."""
    root = _make_root(
        tmp_path, _REAL_PROJECT_FIXTURE.read_text(encoding="utf-8")
    )
    _write_global(fake_home, "")  # present but empty
    r = check_live(root)
    assert r.exit_code == 1, r.to_dict()
    assert r.status == "drift"
    assert "MISSING canonical rule" in "\n".join(r.divergences)


def test_bci1_main_exit_code_and_attribution(tmp_path, fake_home, capsys):
    """main() returns the exit code and prints the attributed drift message."""
    truncated = "\n\n## BC-PROJ-3 — only\n\n**Severity**: Critical\n" \
        "**Applies to**: always: true\n**Trigger keywords**: x\n\n" \
        "**Check**: c\n"
    root = _make_root(tmp_path, truncated)
    _write_global(fake_home, _REAL_GLOBAL_FIXTURE.read_text(encoding="utf-8"))
    rc = main(["--root", str(root)])
    assert rc == 1
    out = capsys.readouterr().out
    assert "DRIFT (HALT)" in out
    assert "NOT a slice regression" in out
