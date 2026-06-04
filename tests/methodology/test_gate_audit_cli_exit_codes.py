"""CLI exit-code regression tests for the 8 mandatory gate audits (slice-101).

The pipeline's value proposition is "deterministic gates catch spec rot." Each
gate audit exposes that guarantee through its CLI exit code — `sys.exit(main())`
returning non-zero on violations — yet that block path was exercised by ZERO
tests (every per-audit test module only tested the `audit()`/`run_audit()`/
`lint_files()` function, never the `main()` entrypoint the pre-finish gate +
pre-commit hooks actually consume). A regression flipping any `main()` to
`return 0` on violations would silently un-block that gate, uncaught.

This module pins, for each of the 8 gate audits:
  * the **block path** — `main(violating_argv)` returns the non-zero block code;
  * the **clean path** — `main(conforming_argv)` returns 0 (so the test
    discriminates block-vs-pass, not merely "non-zero on garbage");
  * the two distinct **exit-2 usage paths** (shippability_path missing-catalog,
    branch_workflow usage-error).

**Cause-pinning (slice-101 /critique M1):** several audits emit the SAME exit 1
for MULTIPLE violation kinds (e.g. TRI-1 `no-section` fires for both a missing
file AND a present sectionless file), so an int-only assertion pins "something
refused," not "the TARGET gate fired." Every block-path test therefore pairs the
`_run_main(...) == block_code` int-assert with a `target_kind in {v.kind ...}`
assert on the SAME fixture via the audit's already-tested function — EXCEPT row 2
(TRI-1) where, because missing-file also yields `no-section`, the load-bearing
cause-pin is the `assert fixture.is_file()` precondition, not the kind-assert
(slice-101 /critique-review note 2). exit-2 cases cause-pin on the code itself
(2 = usage, distinct from 1 = violation).

**In-process invocation (slice-101 design decision):** `_run_main` calls
`main(argv)` in-process and returns the int. The regression guarded lives in
`main()`'s `return 1 if violations else 0`; the module-level `sys.exit(main())`
is unbreakable glue. All 8 `main()` accept `argv` and return the code; none has
import-time side effects (verified by /critique-review).

Closes diagnose-out backlog SC-004 / SC-011 / SC-013 / SC-014 / SC-015 / SC-016
/ SC-020 / SC-021.

Rule references: PMI-1, TRI-1, LINT-MOCK-1, DR-1, WIRE-1, CSP-1, PTFCD-1/PTFFD-1,
BRANCH-1.
"""
import shutil
import subprocess
from pathlib import Path

import yaml

from tests.methodology.conftest import REPO_ROOT
from tools import (
    branch_workflow_audit,
    critique_review_audit,
    cross_spec_parity_audit,
    mock_budget_lint,
    plugin_manifest_audit,
    shippability_path_audit,
    triage_audit,
    wiring_matrix_audit,
)

import _vault_isolation as vi  # tests/ on sys.path via tests/conftest.py

# slice-110 / [[ADR-101]]: pin cross_spec_parity_audit's VAULT_ROOT (in-tree
# relative) so its CLI main() reads each fixture's own architecture/triage.md —
# green under default AND an external AI_SDLC_VAULT_ROOT override (the flip sim).
# (cross_spec is the only VAULT_ROOT consumer among the 8 gate audits here.)
_pin_vault = vi.autouse_pin(cross_spec_parity_audit)

_FIXTURES = REPO_ROOT / "tests" / "methodology" / "fixtures"


def _run_main(main_fn, argv: list[str]) -> int:
    """Invoke an audit CLI entrypoint in-process; return its int exit code.

    `main(argv)` RETURNS the code (the module-level `sys.exit(main())` is the
    only exit site), so this exercises the real violations->exit-code mapping —
    the exact regression these tests guard. See slice-101 design.md.
    """
    return main_fn(argv)


# ============================================================================
# PMI-1 — plugin_manifest_audit (SC-004)
# ============================================================================

def _build_clean_manifest_project(tmp_path: Path) -> Path:
    """A complete, valid, in-sync plugin project. With every required field
    present + version==VERSION, an added orphan skill makes `orphan-skill` the
    SOLE non-zero source (slice-101 /critique M1: no incidental `missing-field`
    co-firing)."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "VERSION").write_text("1.0.0\n", encoding="utf-8")
    (root / "skills" / "alpha").mkdir(parents=True)
    (root / "skills" / "alpha" / "SKILL.md").write_text("# alpha\n", encoding="utf-8")
    (root / "agents").mkdir()
    (root / "agents" / "beta.md").write_text(
        "---\nname: beta\n---\n# beta\n", encoding="utf-8"
    )
    (root / "tools").mkdir()
    (root / "tools" / "gamma.py").write_text("# tool\n", encoding="utf-8")
    (root / "plugin.yaml").write_text(
        yaml.dump(
            {
                "name": "test-plugin",
                "version": "1.0.0",
                "description": "test plugin",
                "skills": [{"id": "alpha", "description": "alpha skill"}],
                "agents": [{"id": "beta", "description": "beta agent"}],
                "tools": [{"path": "tools/gamma.py", "rule": "TEST-1"}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return root


def test_pmi1_cli_blocks_on_orphan_skill(tmp_path: Path) -> None:
    root = _build_clean_manifest_project(tmp_path)
    (root / "skills" / "orphan").mkdir()
    (root / "skills" / "orphan" / "SKILL.md").write_text("# orphan\n", encoding="utf-8")
    assert _run_main(plugin_manifest_audit.main, ["--root", str(root)]) == 1
    kinds = {v.kind for v in plugin_manifest_audit.run_audit(project_root=root).violations}
    assert "orphan-skill" in kinds, f"expected orphan-skill cause; got {kinds}"


def test_pmi1_cli_clean_on_synced_manifest(tmp_path: Path) -> None:
    root = _build_clean_manifest_project(tmp_path)
    assert _run_main(plugin_manifest_audit.main, ["--root", str(root)]) == 0


# ============================================================================
# TRI-1 — triage_audit (SC-011)
# ============================================================================

def test_tri1_cli_blocks_on_missing_triage_section() -> None:
    f = _FIXTURES / "triage" / "no_triage_section_critique.md"
    # Cause-pin (slice-101 /critique-review note 2): a MISSING file also yields
    # `no-section`, so the load-bearing discriminator is that the fixture EXISTS.
    assert f.is_file(), f"fixture must exist to pin the present-sectionless cause: {f}"
    assert _run_main(triage_audit.main, [str(f), "--no-carry-over"]) == 1
    kinds = {
        v.kind
        for v in triage_audit.audit_critique_file(f, skip_if_carry_over=False).violations
    }
    assert "no-section" in kinds, f"expected no-section cause; got {kinds}"


def test_tri1_cli_clean_on_well_formed_triage() -> None:
    f = _FIXTURES / "triage" / "clean_critique.md"
    assert _run_main(triage_audit.main, [str(f), "--no-carry-over"]) == 0


# ============================================================================
# LINT-MOCK-1 — mock_budget_lint (SC-013)
# ============================================================================

def test_lintmock_cli_blocks_on_too_many_mocks() -> None:
    f = _FIXTURES / "mock_budget_too_many.py"
    # plain over-budget returns 0; exit 1 needs --strict (slice-101 design M3).
    assert _run_main(mock_budget_lint.main, ["--strict", str(f)]) == 1
    kinds = {v.kind for v in mock_budget_lint.lint_files([f], frozenset())}
    assert "mock-budget" in kinds, f"expected mock-budget cause; got {kinds}"


def test_lintmock_cli_clean_on_budget_compliant_file() -> None:
    f = _FIXTURES / "mock_budget_clean.py"
    assert _run_main(mock_budget_lint.main, ["--strict", str(f)]) == 0


# ============================================================================
# DR-1 — critique_review_audit (SC-014)
# ============================================================================

def test_dr1_cli_blocks_on_missing_section() -> None:
    f = _FIXTURES / "critique_review" / "missing_section_review.md"
    assert f.is_file(), f"fixture must exist (missing file co-fires): {f}"
    assert _run_main(critique_review_audit.main, [str(f), "--no-carry-over"]) == 1
    kinds = {
        v.kind
        for v in critique_review_audit.audit_review_file(f, skip_if_carry_over=False).violations
    }
    assert "missing-section" in kinds, f"expected missing-section cause; got {kinds}"


def test_dr1_cli_clean_on_well_formed_review() -> None:
    f = _FIXTURES / "critique_review" / "clean_review.md"
    assert _run_main(critique_review_audit.main, [str(f), "--no-carry-over"]) == 0


# ============================================================================
# WIRE-1 — wiring_matrix_audit (SC-015)
# ============================================================================

def test_wire1_cli_blocks_on_missing_cells() -> None:
    f = _FIXTURES / "wiring" / "missing_cells_design.md"
    assert _run_main(wiring_matrix_audit.main, [str(f), "--no-carry-over"]) == 1
    # audit_design_file returns a list of violations (not a result object).
    kinds = {v.kind for v in wiring_matrix_audit.audit_design_file(f, skip_if_carry_over=False)}
    assert "missing-cells" in kinds, f"expected missing-cells cause; got {kinds}"


def test_wire1_cli_clean_on_well_formed_matrix() -> None:
    f = _FIXTURES / "wiring" / "clean_design.md"
    assert _run_main(wiring_matrix_audit.main, [str(f), "--no-carry-over"]) == 0


# ============================================================================
# CSP-1 — cross_spec_parity_audit (SC-016)
# ============================================================================

def test_csp1_cli_blocks_on_broken_ref(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "architecture").mkdir(parents=True)
    # Reuse the existing broken_impl_threat fixture — its `## TM-1 — ...` heading
    # uses an EM-DASH, which `_ITEM_HEADING_RE` ([—\-]) accepts; this sidesteps
    # the M-add-1 double-dash (`--`) trap that would parse 0 items -> exit 0.
    shutil.copy(
        _FIXTURES / "cross_spec_parity" / "broken_impl_threat.md",
        root / "architecture" / "threat-model.md",
    )
    assert _run_main(cross_spec_parity_audit.main, ["--root", str(root), "--skip-heavy-check"]) == 1
    kinds = {
        v.kind
        for v in cross_spec_parity_audit.run_audit(project_root=root, skip_heavy_check=True).violations
    }
    assert "broken-ref" in kinds, f"expected broken-ref cause; got {kinds}"


def test_csp1_cli_clean_on_no_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "project"
    (root / "architecture").mkdir(parents=True)
    # No threat-model/requirements/nfrs artifacts -> nothing to violate -> clean.
    assert _run_main(cross_spec_parity_audit.main, ["--root", str(root), "--skip-heavy-check"]) == 0


# ============================================================================
# PTFCD-1 / PTFFD-1 — shippability_path_audit (SC-020)
# ============================================================================

def _scmd1_catalog(tmp_path: Path, machine_cmd: str) -> Path:
    """A minimal SCMD-1 6-column catalog with one data row whose Machine-cmd
    (col 6) is `machine_cmd`. A 3-column table would scan 0 rows -> exit 0
    (slice-101 design M3).

    Seeds a `VERSION` sentinel at tmp_path so `audit_catalog_file`'s
    `_find_repo_root` (which walks up for `.git`/`VERSION`) DETERMINISTICALLY
    anchors to tmp_path — `tests/...` path tokens then resolve under tmp_path
    regardless of where tmp_path lives (e.g. under `pytest --basetemp=<in-repo>`
    or a TMPDIR nested in a checkout). Without this, the clean test could
    false-FAIL by resolving to an outer repo (slice-101 /code-review m1)."""
    (tmp_path / "VERSION").write_text("0.0.0\n", encoding="utf-8")
    text = (
        "# Shippability\n\n"
        "| # | Slice | Critical path | Command | Runtime | Machine-cmd |\n"
        "|---|-------|---------------|---------|---------|-------------|\n"
        f"| 1 | slice-x | crit | cmd | <1s | {machine_cmd} |\n"
    )
    p = tmp_path / "shippability.md"
    p.write_text(text, encoding="utf-8")
    return p


def _seed_known_testfile(tmp_path: Path) -> None:
    d = tmp_path / "tests" / "methodology"
    d.mkdir(parents=True, exist_ok=True)
    (d / "test_known.py").write_text("def test_real():\n    pass\n", encoding="utf-8")


def test_ptfcd1_cli_blocks_on_phantom_test_path(tmp_path: Path) -> None:
    cat = _scmd1_catalog(
        tmp_path,
        "interp -m pytest tests/methodology/test_DOESNOTEXIST.py --no-header -q",
    )
    assert _run_main(shippability_path_audit.main, [str(cat)]) == 1
    kinds = {v.kind for v in shippability_path_audit.audit_catalog_file(cat).violations}
    assert "missing-test-file" in kinds, f"expected missing-test-file cause; got {kinds}"


def test_ptfcd1_cli_clean_on_existing_test_path(tmp_path: Path) -> None:
    _seed_known_testfile(tmp_path)
    cat = _scmd1_catalog(
        tmp_path,
        "interp -m pytest tests/methodology/test_known.py::test_real --no-header -q",
    )
    assert _run_main(shippability_path_audit.main, [str(cat)]) == 0


def test_ptfcd1_cli_usage_error_on_missing_catalog(tmp_path: Path) -> None:
    # exit 2 (usage) is distinct from exit 1 (violation): a MISSING catalog file
    # must NOT be confused with a bad row (slice-101 design row 7).
    missing = tmp_path / "does_not_exist.md"
    assert _run_main(shippability_path_audit.main, [str(missing)]) == 2


# ============================================================================
# BRANCH-1 — branch_workflow_audit (SC-021)
# ============================================================================

def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    # encoding="utf-8" per BC-GLOBAL-5: a bare text=True is a cp1252 silent-data-
    # loss / decode-crash site on Windows.
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=check,
    )


def _init_repo_default_trunk(tmp_path: Path) -> Path:
    """A tmp git repo whose current branch == resolved default branch, DETERMIN-
    ISTICALLY and host-independently (slice-101 /critique M2): `git branch -M
    trunk` forces the branch name regardless of the host's ambient
    init.defaultBranch (main vs master), and a repo-LOCAL `init.defaultBranch
    trunk` makes the audit's `_resolve_default_branch` fallback resolve to
    'trunk' (no origin -> symbolic-ref fails -> init.defaultBranch). So
    current == default -> the SOLE violation is `on-default-branch` (exit 1)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(repo, "init")
    _run_git(repo, "config", "user.email", "test@test.test")
    _run_git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("test\n", encoding="utf-8")
    _run_git(repo, "add", "README.md")
    _run_git(repo, "commit", "-m", "init")
    _run_git(repo, "branch", "-M", "trunk")
    _run_git(repo, "config", "init.defaultBranch", "trunk")
    return repo


def _make_slice_folder(repo: Path, number: int, name: str) -> Path:
    folder = repo / "architecture" / "slices" / f"slice-{number:03d}-{name}"
    folder.mkdir(parents=True)
    (folder / "mission-brief.md").write_text("# Slice fixture\n", encoding="utf-8")
    return folder


def test_branch1_cli_blocks_on_default_branch(tmp_path: Path) -> None:
    repo = _init_repo_default_trunk(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    assert _run_main(branch_workflow_audit.main, [str(slice_folder), "--root", str(repo)]) == 1
    kinds = {
        v.kind
        for v in branch_workflow_audit.audit(slice_folder=slice_folder, repo_root=repo).violations
    }
    assert "on-default-branch" in kinds, f"expected on-default-branch cause; got {kinds}"


def test_branch1_cli_clean_on_matching_slice_branch(tmp_path: Path) -> None:
    repo = _init_repo_default_trunk(tmp_path)
    slice_folder = _make_slice_folder(repo, 21, "test-feature")
    _run_git(repo, "checkout", "-b", "slice/021-test-feature")
    assert _run_main(branch_workflow_audit.main, [str(slice_folder), "--root", str(repo)]) == 0


def test_branch1_cli_usage_error_on_nonconforming_folder(tmp_path: Path) -> None:
    # exit 2 (usage) via a folder whose name is NOT slice-NNN-<name> — a
    # DETERMINISTIC usage trigger, NOT the env-dependent default-branch-
    # unresolvable path (slice-101 design row 8).
    repo = _init_repo_default_trunk(tmp_path)
    bad = repo / "architecture" / "slices" / "not-a-slice-folder"
    bad.mkdir(parents=True)
    assert _run_main(branch_workflow_audit.main, [str(bad), "--root", str(repo)]) == 2
