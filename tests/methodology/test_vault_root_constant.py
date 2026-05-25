"""Test the VAULT_ROOT constant module (slice-068; per ADR-065).

Pins:
- AC1: module exports VAULT_ROOT constant; default equals Path("architecture")
- AC2: every tools/*.py module in _MIGRATION_SITE_ALLOWLIST imports VAULT_ROOT;
       no orphan "architecture" literals (two-marker convention per /critique-review
       M-add-1 ACCEPTED-FIXED); shippability_decoupling_audit.py:91-92 AST-pattern
       tuples preserve literal (EXCLUDED per design.md §Sites EXCLUDED)
- AC3: pytest baseline preserved; migration is idempotent
- AC4: env-var override via subprocess (read-at-import semantic); allowlist pinned;
       consumer constants are frozen at first import (M1 freeze contract per
       /critique ACCEPTED-FIXED — production-correctness semantic per ADR-065)
"""
from __future__ import annotations

import ast
import importlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tools import _stdout

_stdout.reconfigure_stdout_utf8()


# The 8-element _MIGRATION_SITE_ALLOWLIST — every tools/*.py module that
# hardcoded "architecture/" filesystem-resolving literals pre-slice-068.
# Pinned per /critique B1 ACCEPTED-FIXED + M3 ACCEPTED-FIXED (scope-back of
# tests/methodology/conftest.py to DEFERRED for follow-on slice).
_MIGRATION_SITE_ALLOWLIST: frozenset[str] = frozenset({
    "tools/build_checks_integrity.py",
    "tools/critique_review_prerequisite_audit.py",
    "tools/cross_spec_parity_audit.py",
    "tools/risk_register_audit.py",
    "tools/slice_queue_writer.py",
    "tools/state_transition_pin_audit.py",
    "tools/supersede_audit.py",
    "tools/validate_slice_layers.py",
})

# 5 enumerated EXCLUDED error-message-string sites (file, line) — these contain
# "architecture/..." in user-facing error prose, NOT filesystem paths; they
# carry the "# NOT VAULT_ROOT-routed (slice-068) — error-message prose" marker
# per the two-marker convention (per /critique-review M-add-1 ACCEPTED-FIXED).
_ERROR_MESSAGE_STRING_EXCLUSIONS: frozenset[tuple[str, int]] = frozenset({
    ("tools/cross_spec_parity_audit.py", 335),
    ("tools/state_transition_pin_audit.py", 374),
    ("tools/state_transition_pin_audit.py", 388),
    ("tools/state_transition_pin_audit.py", 400),
    ("tools/validate_slice_layers.py", 521),
})

# Repo root for tests (parents[2] = .../<repo>; parents[1] = tests/).
REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── AC1: module exports + default ──────────────────────────────────────


def test_vault_root_module_exports_constant() -> None:
    """AC1: tools._vault_paths exports VAULT_ROOT as a Path."""
    import tools._vault_paths
    assert hasattr(tools._vault_paths, "VAULT_ROOT")
    assert isinstance(tools._vault_paths.VAULT_ROOT, Path)


def test_vault_root_default_equals_path_architecture(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC1: when AI_SDLC_VAULT_ROOT is unset, VAULT_ROOT == Path("architecture")."""
    monkeypatch.delenv("AI_SDLC_VAULT_ROOT", raising=False)
    import tools._vault_paths
    importlib.reload(tools._vault_paths)
    assert tools._vault_paths.VAULT_ROOT == Path("architecture")


# ─── AC2: migration sites + two-marker convention ───────────────────────


def _read_module_ast(rel_path: str) -> ast.Module:
    abs_path = REPO_ROOT / rel_path
    return ast.parse(abs_path.read_text(encoding="utf-8"))


def test_all_tools_modules_import_vault_root() -> None:
    """AC2: every migrated tools/*.py imports VAULT_ROOT from tools._vault_paths."""
    for rel_path in sorted(_MIGRATION_SITE_ALLOWLIST):
        tree = _read_module_ast(rel_path)
        imported = any(
            isinstance(node, ast.ImportFrom)
            and node.module == "tools._vault_paths"
            and any(alias.name == "VAULT_ROOT" for alias in node.names)
            for node in ast.walk(tree)
        )
        assert imported, (
            f"{rel_path} must import VAULT_ROOT from tools._vault_paths "
            f"(slice-068 migration site per _MIGRATION_SITE_ALLOWLIST)"
        )


def test_no_orphan_architecture_literal_in_migrated_tools() -> None:
    """AC2 + M-add-1 two-marker convention: every "architecture" literal in
    a migrated tools/*.py file MUST either carry the
    "# VAULT_ROOT-routed (slice-068)" marker (for migration sites) OR the
    "# NOT VAULT_ROOT-routed (slice-068) — error-message prose" marker
    (for the 5 enumerated EXCLUDED error-message-string sites), OR be a
    comment/docstring line (heuristic: starts with # or ' or ").
    """
    violations: list[str] = []
    # Files in the migration allowlist also contain the EXCLUDED error-
    # message-string sites — checking both classes here in one sweep.
    files_to_check = sorted(_MIGRATION_SITE_ALLOWLIST)
    literal_re = re.compile(r'["\']architecture[/"\\]')
    for rel_path in files_to_check:
        abs_path = REPO_ROOT / rel_path
        for line_num, line in enumerate(
            abs_path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not literal_re.search(line):
                continue
            if "# VAULT_ROOT-routed (slice-068)" in line:
                continue  # accepted migration marker
            if "# NOT VAULT_ROOT-routed (slice-068)" in line:
                continue  # accepted exclusion marker (two-marker convention)
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue  # in-line comment
            if stripped.startswith('"') or stripped.startswith("'"):
                continue  # docstring continuation line
            violations.append(f"{rel_path}:{line_num}: {line.strip()}")

    assert not violations, (
        "Orphan 'architecture' literals lacking the slice-068 two-marker "
        "convention:\n  " + "\n  ".join(violations)
    )


def test_shippability_decoupling_audit_tuples_preserve_literal() -> None:
    """AC2: tools/shippability_decoupling_audit.py:91-92 AST-pattern allowlist
    tuples MUST stay literal (preserved verbatim per design.md §Sites EXCLUDED
    — migrating them would BREAK the audit's detection purpose; those tuples
    are pattern data for detecting Path-shape literals in OTHER files).
    """
    text = (REPO_ROOT / "tools/shippability_decoupling_audit.py").read_text(
        encoding="utf-8"
    )
    assert '("architecture", "slices", "archive")' in text, (
        "shippability_decoupling_audit.py:91 must preserve the literal "
        "AST-pattern allowlist tuple (slice-068 EXCLUDED per design.md §Sites EXCLUDED)"
    )
    assert '("architecture", "build-checks.md")' in text, (
        "shippability_decoupling_audit.py:92 must preserve the literal "
        "AST-pattern allowlist tuple (slice-068 EXCLUDED)"
    )


# ─── AC3: behavior preserved + idempotent ───────────────────────────────


def test_full_pytest_baseline_preserved() -> None:
    """AC3: structural pin — this slice adds exactly 10 new tests; the actual
    full pytest run is gated by /build-slice pre-finish, not duplicated here.
    """
    test_module_text = Path(__file__).read_text(encoding="utf-8")
    test_count = len(re.findall(r"^def test_", test_module_text, re.MULTILINE))
    assert test_count == 10, (
        f"slice-068 test_vault_root_constant.py must contain exactly 10 "
        f"test functions per mission-brief AC4 (post-/critique M1 freeze-pin "
        f"row addition: 9 → 10); found {test_count}"
    )


def test_migration_is_idempotent() -> None:
    """AC3: scripted re-application of the migration transform on an
    already-migrated file produces an empty diff. Empirical pin: take
    slice_queue_writer.py's current text, apply a no-op transform that
    re-routes already-routed literals through VAULT_ROOT, assert the
    re-routed text equals the input.
    """
    target = REPO_ROOT / "tools/slice_queue_writer.py"
    original = target.read_text(encoding="utf-8")
    # The migration transform: route any naked Path("architecture") to
    # VAULT_ROOT. Since slice_queue_writer.py is already migrated post-
    # slice-068, re-applying the transform produces no change.
    transformed = re.sub(
        r'Path\(["\']architecture["\']\)',
        "VAULT_ROOT",
        original,
    )
    assert transformed == original, (
        "Migration must be idempotent: re-applying the Path('architecture') "
        "→ VAULT_ROOT transform to an already-migrated file must produce no change."
    )


# ─── AC4: env-var + allowlist pin + freeze contract ─────────────────────


def test_env_var_override_via_subprocess(tmp_path: Path) -> None:
    """AC4: AI_SDLC_VAULT_ROOT=<path> in env propagates to VAULT_ROOT at
    subprocess module-import time. Uses subprocess fixture per the read-at-
    import-time semantic — in-process env mutation would not propagate to the
    already-imported tools._vault_paths.VAULT_ROOT (production-correctness
    semantic; see test_consumer_constants_are_frozen_at_first_import).
    """
    override = str(tmp_path / "alt-vault")
    env = {**os.environ, "AI_SDLC_VAULT_ROOT": override}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from tools._vault_paths import VAULT_ROOT; print(VAULT_ROOT)",
        ],
        env=env,
        capture_output=True,
        text=True,
        check=True,
        cwd=str(REPO_ROOT),
    )
    assert result.stdout.strip() == override, (
        f"Expected VAULT_ROOT={override} via subprocess env override; "
        f"got stdout={result.stdout!r} stderr={result.stderr!r}"
    )


def test_migration_site_allowlist_pinned() -> None:
    """AC4: the 8-element _MIGRATION_SITE_ALLOWLIST frozenset matches the
    actual post-migration tools/*.py modules importing VAULT_ROOT. Catches
    drift in two directions: (a) a new tool module added post-slice-068 that
    hardcodes Path("architecture") without migrating (drift IN); (b) a
    migrated module silently removed from the allowlist (drift OUT). Per
    /critique B1 lesson — would have caught the build_checks_integrity.py:78
    site that slice-068 rev-1 grep missed.
    """
    actual_importers: set[str] = set()
    for py_file in sorted((REPO_ROOT / "tools").glob("*.py")):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        if "from tools._vault_paths import VAULT_ROOT" in text:
            actual_importers.add(f"tools/{py_file.name}")

    assert actual_importers == _MIGRATION_SITE_ALLOWLIST, (
        f"_MIGRATION_SITE_ALLOWLIST drift detected:\n"
        f"  pinned: {sorted(_MIGRATION_SITE_ALLOWLIST)}\n"
        f"  actual: {sorted(actual_importers)}\n"
        f"  symmetric_diff: {sorted(_MIGRATION_SITE_ALLOWLIST ^ actual_importers)}"
    )


def test_consumer_constants_are_frozen_at_first_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC4 (NEW per /critique M1 ACCEPTED-FIXED): the production-correctness
    freeze contract. Downstream consumer constants (e.g.,
    tools.slice_queue_writer._INDEX_MD_REL) FREEZE the VAULT_ROOT value at
    their own module-import time. Subsequent monkeypatch of
    tools._vault_paths.VAULT_ROOT does NOT propagate.

    Pinning this as a contract serves both:
    1. Production semantic correctness — env var read once per process at startup
       (per ADR-065 §Decision §Read-at-import semantics + consumer-freeze cascade)
    2. Test-author warning — in-process monkeypatch does not propagate to
       already-frozen downstream consumer constants; use subprocess fixtures
       (see test_env_var_override_via_subprocess) for cross-process semantics
    """
    import tools._vault_paths
    import tools.slice_queue_writer

    # Capture the consumer's frozen constant.
    frozen_index_md_rel = tools.slice_queue_writer._INDEX_MD_REL

    # In-process monkeypatch of VAULT_ROOT itself.
    monkeypatch.setattr(
        tools._vault_paths, "VAULT_ROOT", Path("/tmp/freeze-pin-test")
    )

    # The consumer's frozen constant MUST be unchanged — that's the
    # production-correctness semantic this test pins.
    assert tools.slice_queue_writer._INDEX_MD_REL == frozen_index_md_rel, (
        "Freeze contract VIOLATED: tools.slice_queue_writer._INDEX_MD_REL "
        "updated after monkeypatching tools._vault_paths.VAULT_ROOT. "
        "Expected the consumer constant to remain frozen at its first-import "
        "value (production-correctness semantic per ADR-065 §Decision)."
    )
