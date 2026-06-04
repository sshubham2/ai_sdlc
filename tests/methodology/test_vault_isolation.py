"""Self-tests for the location-agnostic vault-root isolation helper
(``tests/_vault_isolation.py``; slice-110 / [[ADR-101]]).

These prove the helper's mechanism end-to-end against REAL consumers (not a
mock): it setattr-pins a function-local VAULT_ROOT reader, re-derives a frozen
module-level constant via ``derived``, preserves class/enum identity (no reload),
fails LOUD on a pin that touches nothing (non-vacuity, AP-5), and restores
ambient state on exit with no cross-test pollution.

Deliberately a NEW module (NOT ``test_vault_root_constant.py``) so its
``test_full_pytest_baseline_preserved`` ``== 15`` count-pin at L201 stays
untouched (slice-110 /critique B2 / FBCD-1 sub-mode (c)).

The self-tests are themselves location-agnostic: they capture the AMBIENT
``VAULT_ROOT`` at test start and assert restoration to THAT (not a hardcoded
``Path("architecture")``), so they are green under the default suite AND under
the ``AI_SDLC_VAULT_ROOT=<seeded-ext>`` flip simulation.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

import _vault_isolation as vi  # tests/ is on sys.path via tests/conftest.py
from tools import _stdout

_stdout.reconfigure_stdout_utf8()


def _ambient_vault_root() -> Path:
    """The process-global VAULT_ROOT under the ambient (un-pinned) resolution."""
    import tools._vault_paths
    return tools._vault_paths.VAULT_ROOT


# ─── in-process: function-local reader ──────────────────────────────────


def test_pin_repoints_function_local_reader(tmp_path: Path) -> None:
    """A consumer that reads VAULT_ROOT at call time (drift_check_audit) sees the
    pinned value inside the block and the ambient value after (setattr-restored,
    no reload)."""
    import tools.drift_check_audit as dca

    ambient = _ambient_vault_root()
    vault = tmp_path / "architecture"
    vault.mkdir()

    with vi.pin_vault_root(vault, dca):
        assert dca.VAULT_ROOT == vault

    assert dca.VAULT_ROOT == ambient  # restored without a reload


# ─── in-process: frozen module-level constant via `derived` ─────────────


def test_pin_redrives_frozen_constant_via_derived(tmp_path: Path) -> None:
    """A frozen derived constant (slice_queue_writer._INDEX_MD_REL = VAULT_ROOT /
    'slices' / '_index.md') is re-derived only when supplied in ``derived`` — and
    restored on exit."""
    import tools.slice_queue_writer as sqw

    ambient = _ambient_vault_root()
    vault = tmp_path / "architecture"
    vault.mkdir()

    with vi.pin_vault_root(
        vault, sqw,
        derived=[(sqw, "_INDEX_MD_REL", lambda vr: vr / "slices" / "_index.md")],
    ):
        assert sqw.VAULT_ROOT == vault
        assert sqw._INDEX_MD_REL == vault / "slices" / "_index.md"

    assert sqw._INDEX_MD_REL == ambient / "slices" / "_index.md"


# ─── identity preservation: no reload ───────────────────────────────────


def test_pin_preserves_class_identity(tmp_path: Path) -> None:
    """The setattr mechanism does NOT reload the consumer, so a symbol imported by
    name stays identical to the module's attribute (the reload trap that broke
    `is ConflictClass.SOFT` comparisons)."""
    import tools.parallel_conflict_resolver as pcr
    from tools.parallel_conflict_resolver import ConflictClass

    vault = tmp_path / "architecture"
    vault.mkdir()

    with vi.pin_vault_root(vault, pcr):
        assert ConflictClass is pcr.ConflictClass  # same object — not reloaded


# ─── non-vacuity: a pin that touches nothing must fail loud ──────────────


def test_non_vacuity_assert_fires_on_non_consumer(tmp_path: Path) -> None:
    """Listing a module that does NOT bind VAULT_ROOT (tools._stdout) must raise
    AssertionError — the AP-5 guard against a pin that silently touches nothing."""
    vault = tmp_path / "architecture"
    vault.mkdir()

    with pytest.raises(AssertionError, match="non-vacuity"):
        with vi.pin_vault_root(vault, _stdout):
            pass  # pragma: no cover — entry raises before the body


def test_empty_consumers_raises(tmp_path: Path) -> None:
    """A pin with no consumer cannot take effect → ValueError."""
    with pytest.raises(ValueError, match="at least one consumer"):
        with vi.pin_vault_root(tmp_path / "architecture"):
            pass  # pragma: no cover


# ─── restore: no cross-test pollution + env restoration ──────────────────


def test_restore_to_ambient_and_env(tmp_path: Path) -> None:
    """After the block, the env var is restored to its prior state and the
    consumer's VAULT_ROOT is restored to the ambient value (setattr-restored)."""
    import tools.supersede_audit as sup

    prior_env = os.environ.get(vi.ENV_VAR)
    ambient = _ambient_vault_root()
    vault = tmp_path / "architecture"
    vault.mkdir()

    with vi.pin_vault_root(vault, sup):
        assert sup.VAULT_ROOT == vault
        assert os.environ[vi.ENV_VAR] == str(vault)

    assert os.environ.get(vi.ENV_VAR) == prior_env
    assert sup.VAULT_ROOT == ambient


# ─── subprocess env helper ───────────────────────────────────────────────


def test_subprocess_env_removes_var() -> None:
    """subprocess_env(None) strips AI_SDLC_VAULT_ROOT so the child resolves its
    own --repo-root default, regardless of a sim var in the parent."""
    base = {"AI_SDLC_VAULT_ROOT": "/seeded/ext", "PATH": "x"}
    env = vi.subprocess_env(base=base)
    assert vi.ENV_VAR not in env
    assert env["PATH"] == "x"


def test_subprocess_env_sets_explicit_vault() -> None:
    """subprocess_env(vault) points the child at an explicit vault dir."""
    base = {"AI_SDLC_VAULT_ROOT": "/seeded/ext", "PATH": "x"}
    env = vi.subprocess_env(vault_dir="/child/own/architecture", base=base)
    assert env[vi.ENV_VAR] == "/child/own/architecture"


def test_subprocess_env_defaults_to_os_environ() -> None:
    """With no base, subprocess_env copies os.environ (and never mutates it)."""
    env = vi.subprocess_env()
    assert vi.ENV_VAR not in env
    assert isinstance(env, dict)
