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

slice-071 m3 DOCUMENT-AS-DESIGNED disposition (per slice-068 code-Critic m3 +
slice-071 /critique M6 + /critique-review M-add-1 ACCEPTED-FIXED):
Two-marker convention applies only to lines matched by ``literal_re`` at L118
of this module; substring-in-prose sites at argparse help / error messages /
log strings are intentionally unmarked per slice-071 design.md §slice-068-m3
disposition. The asymmetry is structural — broadening the audit regex to
catch all `architecture/` substrings would require marking ~6 additional
user-facing-prose sites without semantic benefit; the test
``test_two_marker_convention_asymmetry_documented`` pins this prose.
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


# The 16-element _MIGRATION_SITE_ALLOWLIST — every tools/*.py module that routes
# vault filesystem reads through VAULT_ROOT (the original slice-068 migration set
# plus later VAULT_ROOT consumers, each tagged inline with its slice).
# Pinned per /critique B1 ACCEPTED-FIXED + M3 ACCEPTED-FIXED (scope-back of
# tests/methodology/conftest.py to DEFERRED for follow-on slice).
_MIGRATION_SITE_ALLOWLIST: frozenset[str] = frozenset({
    "tools/build_checks_integrity.py",
    "tools/critique_review_prerequisite_audit.py",
    "tools/cross_spec_parity_audit.py",
    "tools/drift_check_audit.py",  # slice-081 / DCE-1 — new VAULT_ROOT consumer (drift-log + triage routing)
    "tools/risk_register_audit.py",
    "tools/slice_queue_claim.py",  # slice-072 / PSQ-2 — new VAULT_ROOT consumer
    "tools/slice_queue_writer.py",
    "tools/state_transition_pin_audit.py",
    "tools/supersede_audit.py",
    "tools/validate_slice_layers.py",
    "tools/vault_edit.py",  # slice-095 / SVW-1 — new VAULT_ROOT consumer (resolves --file under the vault root for the skill-path safe-append channel)
    # slice-098 / ADR-089 — the 3 git-coupled tools slice-093 AC4 deferred ("migrate-NONE"),
    # now Class-A-routed through VAULT_ROOT + Class-B RETIRE-when-external via vault_is_external:
    "tools/parallel_conflict_resolver.py",
    "tools/pulse_worktree_resolver.py",
    "tools/stranded_slice_audit.py",
    "tools/index_router_thinness_audit.py",  # slice-103 / ADR-093 — resolves slices/_index.md + archive/_index.md + action-points.md under VAULT_ROOT (flip-safe; M5)
    "tools/project_frame_synth.py",  # slice-106 / ADR-091 — routes the 4 vault reads (concept/triage/slice-queue/risk-register) through VAULT_ROOT (production must-rewrite 4→0)
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


@pytest.fixture(autouse=True)
def _restore_vault_paths_resolution():
    """slice-110 / [[ADR-101]] location-agnostic isolation: several tests here
    ``importlib.reload(tools._vault_paths)`` under a mutated env (e.g.
    ``test_vault_root_default_equals_path_architecture`` delenvs then reloads).
    ``monkeypatch`` restores the env but NOT the module reload, leaving
    ``tools._vault_paths.VAULT_ROOT`` pinned to the in-test resolution. Under the
    default suite that's harmless (``architecture`` == ``architecture``); under an
    external ``AI_SDLC_VAULT_ROOT`` override (the flip simulation) it pollutes
    ``test_consumer_constants_are_frozen_at_first_import`` (ambient external root vs
    a left-over ``architecture``). Reload after each test so the AMBIENT resolution
    is restored — green in BOTH worlds, no cross-test leak.

    NOTE: this is a non-``test_`` def, so it does NOT affect the
    ``test_full_pytest_baseline_preserved`` ``== 15`` count-pin.
    """
    yield
    import tools._vault_paths
    importlib.reload(tools._vault_paths)


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
    """AC3: structural pin — test-function count.

    slice-068 originally shipped 10 functions. slice-071 SC-028 bundle adds
    2 more (`test_vault_paths_module_is_leaf` + `test_two_marker_convention_
    asymmetry_documented`) → 12. slice-093 AC1 adds 3 resolution-precedence
    tests (`test_resolution_precedence_env_over_pointer_over_default` +
    `test_git_common_dir_key_stable_across_main_and_worktree` +
    `test_default_unchanged_when_no_env_no_pointer`) → 15. This count-pin
    update is the ONE sanctioned existing-test change in slice-093 (Critic M1)
    — it is NOT a resolution-behaviour change (the resolved default stays
    `architecture/`).
    """
    test_module_text = Path(__file__).read_text(encoding="utf-8")
    test_count = len(re.findall(r"^def test_", test_module_text, re.MULTILINE))
    assert test_count == 15, (
        f"test_vault_root_constant.py must contain exactly 15 test functions "
        f"(slice-068 shipped 10; slice-071 SC-028 added 2; slice-093 AC1 added "
        f"3 resolution-precedence tests); found {test_count}"
    )


def test_migration_is_idempotent() -> None:
    """AC3: scripted re-application of the migration transform on an
    already-migrated file produces an empty diff.

    slice-071 m1 FIX (per slice-068 code-Critic m1): pre-fix the regex
    ``Path(["\\']architecture["\\']\\)`` caught only ONE of the 4 pre-migration
    literal shapes the slice-068 8-site migration covered. On
    post-migration code, the narrow regex finds 0 matches → 0 substitutions
    → trivially equal to input (test passed vacuously regardless of
    migration state). Post-fix: regex covers all 4 pre-migration shapes,
    AND the assertion is empirically load-bearing — re-applying any of the
    4 transforms to a post-migration file must produce no change.

    4 pre-migration shapes covered:
      (a) Path("architecture") — bare module-level path constant
      (b) Path("architecture/<sub>") — single-arg with subpath
      (c) bare "architecture/<sub>" — string literal interpolated elsewhere
      (d) repo_root / "architecture" / "<sub>" — composed via __truediv__
    """
    target = REPO_ROOT / "tools/slice_queue_writer.py"
    original = target.read_text(encoding="utf-8")
    # 4-shape transform: re-route each pre-migration shape to VAULT_ROOT.
    # slice-071 m1 FIX expanded coverage per slice-068 code-Critic m1.
    transformed = original
    # Shape (a) + (b): Path("architecture[/...]")
    transformed = re.sub(
        r'Path\(["\']architecture(/[^"\']+)?["\']\)',
        "VAULT_ROOT",
        transformed,
    )
    # Shape (c): bare "architecture/<sub>" string literal (not inside Path())
    # — match string literal "architecture/..." NOT immediately preceded by
    # `Path(`. Use a negative lookbehind to avoid double-matching (a)+(b).
    transformed = re.sub(
        r'(?<!Path\()["\']architecture/[^"\']+["\']',
        "VAULT_ROOT_REL",
        transformed,
    )
    # Shape (d): composed `<expr> / "architecture" / "<sub>"`. Match a
    # `/ "architecture" /` fragment as the canonical composition shape.
    transformed = re.sub(
        r'/\s*["\']architecture["\']\s*/',
        "/ VAULT_ROOT_COMPOSED /",
        transformed,
    )
    assert transformed == original, (
        "Migration must be idempotent: re-applying the 4-shape transform "
        "(Path('architecture'[/sub]) | bare 'architecture/<sub>' | composed "
        "/'architecture'/) to an already-migrated file must produce no change. "
        "slice-071 m1 FIX expanded coverage from 1 shape to 4 (per slice-068 "
        "code-Critic m1)."
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
    """AC4: the 16-element _MIGRATION_SITE_ALLOWLIST frozenset matches the
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

    # Capture the consumer's frozen constant + the pre-patch VAULT_ROOT.
    frozen_index_md_rel = tools.slice_queue_writer._INDEX_MD_REL
    pre_patch_vault_root = tools._vault_paths.VAULT_ROOT

    # In-process monkeypatch of VAULT_ROOT itself.
    patched_vault = Path("/tmp/freeze-pin-test")
    monkeypatch.setattr(
        tools._vault_paths, "VAULT_ROOT", patched_vault
    )

    # slice-071 m2 FIX (per slice-068 code-Critic m2): two-step assertion.
    # Step 1: PROVE the monkeypatch actually mutated the attribute. Pre-fix,
    # a no-op monkeypatch (or one against a renamed attribute) would have
    # passed the freeze test silently because both sides of the equality
    # were the same captured-then-re-read value of a non-recomputed
    # consumer constant.
    assert tools._vault_paths.VAULT_ROOT == patched_vault, (
        "Monkeypatch did NOT mutate tools._vault_paths.VAULT_ROOT — the "
        "freeze test below would pass trivially. Verify the monkeypatch "
        "target attribute name."
    )

    # Step 2: PROVE the consumer's frozen constant did NOT propagate the
    # patched value — that's the production-correctness semantic.
    expected_canonical = pre_patch_vault_root / "slices" / "_index.md"
    assert frozen_index_md_rel == expected_canonical, (
        f"Consumer's frozen constant captured WRONG pre-patch value: "
        f"frozen={frozen_index_md_rel!r}, expected canonical "
        f"VAULT_ROOT-derived form={expected_canonical!r}"
    )
    # Step 3: PROVE the consumer's frozen constant ALSO did NOT change to
    # the patched value (defense-in-depth — if step 2 passed but step 3
    # also returned True against the patched-derived form, the consumer
    # would be recomputed-on-read which would violate the freeze).
    patched_derived = patched_vault / "slices" / "_index.md"
    assert tools.slice_queue_writer._INDEX_MD_REL != patched_derived, (
        f"Freeze contract VIOLATED: consumer constant equals "
        f"patched-derived value {patched_derived!r} — the constant is "
        f"recomputed-on-read instead of frozen-at-first-import."
    )

    # The consumer's frozen constant MUST be unchanged — that's the
    # production-correctness semantic this test pins.
    assert tools.slice_queue_writer._INDEX_MD_REL == frozen_index_md_rel, (
        "Freeze contract VIOLATED: tools.slice_queue_writer._INDEX_MD_REL "
        "updated after monkeypatching tools._vault_paths.VAULT_ROOT. "
        "Expected the consumer constant to remain frozen at its first-import "
        "value (production-correctness semantic per ADR-065 §Decision)."
    )


# ─── slice-071 SC-028 bundle additions ─────────────────────────────────


def test_vault_paths_module_is_leaf() -> None:
    """slice-071 M1 FIX pin (per slice-068 code-Critic M1 / SC-028).

    slice-068 design.md L25 + mission-brief.md L54 promised a regression-
    pin test asserting `tools/_vault_paths.py` imports only stdlib modules
    (the leaf-invariant). The test was never added at slice-068 build
    time — code-Critic caught the gap by direct AST inspection at post-
    build /code-review.

    This test parses `tools/_vault_paths.py` via `ast.parse`, walks all
    `ast.Import` + `ast.ImportFrom` nodes, and asserts no module starts
    with `"tools."`. Allowed: `__future__`, `os`, `pathlib` (stdlib roots).
    """
    target = REPO_ROOT / "tools" / "_vault_paths.py"
    source = target.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(target))
    non_stdlib_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_root = alias.name.split(".")[0]
                if module_root == "tools":
                    non_stdlib_imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                module_root = node.module.split(".")[0]
                if module_root == "tools":
                    non_stdlib_imports.append(
                        f"from {node.module} import {','.join(a.name for a in node.names)}"
                    )
    assert non_stdlib_imports == [], (
        f"Leaf invariant VIOLATED: tools/_vault_paths.py must import only "
        f"stdlib modules (not from `tools.*`). Found non-stdlib imports: "
        f"{non_stdlib_imports}. Per ADR-065 + design.md §VAULT_ROOT seam — "
        f"the module is the dependency leaf for the VAULT_ROOT cascade; "
        f"importing from `tools.*` would create a cycle."
    )


def test_two_marker_convention_asymmetry_documented() -> None:
    """slice-071 m3 DOCUMENT-AS-DESIGNED pin (per slice-068 code-Critic m3
    + /critique M6 + /critique-review M-add-1 ACCEPTED-FIXED).

    The two-marker convention asymmetry — audit's `literal_re` at L118
    matches `"architecture[/"\\]` patterns only; substring-in-prose sites
    at argparse help / error messages / log strings are intentionally
    unmarked — is documented in this module's docstring. This sentinel
    test asserts the documentation prose exists, pinning the asymmetry
    as deliberate-by-design rather than oversight.

    Assertion shape: prose-substring (NOT regex literal) per /critique M6
    + /critique-review M-add-1. Substrings VERBATIM-aligned to docstring
    (capital `T` in `Two-marker`; full anchor `§slice-068-m3`).
    """
    doc = __doc__ or ""
    # Verbatim substring assertions — case-sensitive; full-anchor.
    assert "Two-marker convention" in doc, (
        "Module docstring must contain `Two-marker convention` prose (capital T)."
    )
    assert "argparse help" in doc, (
        "Module docstring must mention `argparse help` as an unmarked-prose site."
    )
    assert "intentionally unmarked" in doc, (
        "Module docstring must include `intentionally unmarked` to mark the "
        "asymmetry as deliberate."
    )
    assert "slice-071 design.md §slice-068-m3" in doc, (
        "Module docstring must cite the slice-071 design.md §slice-068-m3 "
        "disposition as the canonical anchor."
    )


# ─── slice-093 AC1: resolution precedence (env → git-common-dir config → default) ───


def test_resolution_precedence_env_over_pointer_over_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC1 (slice-093 / ADR-085): _resolve_vault_root honours env >
    git-common-dir config > default 'architecture' — in that order."""
    import tools._vault_paths as vp

    # env beats config
    monkeypatch.setenv("AI_SDLC_VAULT_ROOT", "/from/env")
    monkeypatch.setattr(vp, "_read_common_dir_config", lambda: "/from/config")
    assert vp._resolve_vault_root() == Path("/from/env")

    # config beats default (env unset)
    monkeypatch.delenv("AI_SDLC_VAULT_ROOT", raising=False)
    assert vp._resolve_vault_root() == Path("/from/config")

    # default when neither env nor config
    monkeypatch.setattr(vp, "_read_common_dir_config", lambda: None)
    assert vp._resolve_vault_root() == Path("architecture")


def test_default_unchanged_when_no_env_no_pointer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC1 / no-flip safety contract: with no env AND no config, the resolved
    vault root is UNCHANGED at Path('architecture') — this repo behaves exactly
    as before slice-093."""
    import tools._vault_paths as vp

    monkeypatch.delenv("AI_SDLC_VAULT_ROOT", raising=False)
    monkeypatch.setattr(vp, "_read_common_dir_config", lambda: None)
    assert vp._resolve_vault_root() == Path("architecture")


def test_git_common_dir_key_stable_across_main_and_worktree(tmp_path: Path) -> None:
    """AC1 / C1 keying (the spike's central claim): `git rev-parse
    --path-format=absolute --git-common-dir` returns a byte-identical absolute
    path from the main tree AND a linked worktree — so the per-project key is
    stable across all worktrees of one repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.email", "t@example.com"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(repo), "config", "user.name", "tester"],
        check=True,
        capture_output=True,
    )
    (repo / "seed.txt").write_text("seed", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "init"], check=True, capture_output=True
    )
    wt = tmp_path / "linked-wt"
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "add", str(wt), "-b", "feature"],
        check=True,
        capture_output=True,
    )

    def common_dir(cwd: Path) -> str:
        return subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=cwd,
            capture_output=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()

    main_cd = common_dir(repo)
    wt_cd = common_dir(wt)
    assert main_cd == wt_cd, (
        f"git-common-dir key NOT stable across worktrees: main={main_cd!r} "
        f"worktree={wt_cd!r} — the per-project keying assumption (C1) fails"
    )
