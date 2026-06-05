"""Location-agnostic test vault-root isolation (slice-110; [[ADR-101]]).

Pin a test's vault root to its OWN fixture directory, independent of the
process-global ``VAULT_ROOT``, so the test is green under the in-tree default
AND under an absolute ``AI_SDLC_VAULT_ROOT`` override (the external-vault flip
simulation). This is the reversible flip-readiness prep: once every
vault-resolving test routes through this helper, a future config-only flip is a
suite-neutral no-op.

Why this is needed (the consumer-freeze cascade)
-------------------------------------------------
``tools/_vault_paths.py`` reads ``AI_SDLC_VAULT_ROOT`` (and the git-common-dir
config) **once at import**, and consumers FREEZE the resolved value two ways:

* ``from tools._vault_paths import VAULT_ROOT`` binds the name into the
  consumer's own module namespace at the consumer's import time; consumers that
  compose ``repo_root / VAULT_ROOT / x`` read that module global at call time; and
* module-level constants derive from it (e.g.
  ``parallel_conflict_resolver._AUDIT_LOG_PATH = VAULT_ROOT / "...-log.md"``,
  ``build_checks_integrity._PROJECT_LIVE_REL``,
  ``slice_queue_writer._INDEX_MD_REL``).

So an in-process test cannot re-point the vault by setting the env var alone —
the consumer already froze the old value.

Mechanism: setattr-pin, NOT importlib.reload (build-discovered — [[ADR-101]] refined)
-------------------------------------------------------------------------------------
[[ADR-101]] originally specified ``importlib.reload`` of the consumer. Executing
that against the real cascade at ``/build-slice`` (APED-1) surfaced a fatal flaw:
reloading a consumer module REBINDS its classes/enums to NEW objects, so a test
that imported a symbol by name (e.g. ``from tools.parallel_conflict_resolver
import ConflictClass``) and asserts ``x is ConflictClass.SOFT`` breaks — the
reloaded module's ``ConflictClass.SOFT`` is a different object than the test's.
The sound mechanism is to **setattr the frozen names in place** (no reload, so
class/enum identity is preserved):

* set ``<module>.VAULT_ROOT`` on ``tools._vault_paths`` and each consumer — cures
  every function-local ``repo_root / VAULT_ROOT / x`` reader and every
  ``from tools._vault_paths import VAULT_ROOT`` binding; and
* re-derive each frozen module-level constant via an explicit ``derived`` entry
  (only the few consumers with such constants supply one).

:func:`pin_vault_root` is a context manager that captures the prior values,
setattrs the pinned ones, yields, then restores in reverse — no cross-test
pollution, no reload, no identity break.

Two call-shapes
---------------
* **in-process** (``run_audit(repo_root=tmp)``): use :func:`pin_vault_root`. Pin
  to the in-tree-relative ``Path("architecture")`` so ``repo_root / VAULT_ROOT /
  x`` resolves under the test's own ``tmp`` repo_root (identical to the un-flipped
  default; a no-op under the default suite, the cure under the flip sim). List
  the call-graph closure of vault-freezing modules: a tool whose runtime path
  delegates to another vault-freezing tool (e.g. the resolver's
  ``vault_is_external`` gate reads ``tools._vault_git.VAULT_ROOT``) must list BOTH.
* **subprocess** (``$PY -m tools.X --repo-root tmp``): use :func:`subprocess_env`
  to build the child env. The child must NOT inherit the parent's flip-sim
  ``AI_SDLC_VAULT_ROOT`` (which would make it read the seeded external store
  instead of its own ``tmp/architecture`` fixture); :func:`subprocess_env`
  removes it (or sets it explicitly to the child's own tmp vault).

This is test-support code (mirrors ``tests/methodology/conftest.py``); it is not
a product module and is excluded from the PMI-1 / INST-1 inventory.
"""
from __future__ import annotations

import contextlib
import importlib
import os
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterable, Iterator, Tuple

# The single env-var seam (mirrors tools/_vault_paths._ENV_VAR). Kept as a local
# literal so this test helper does not import a private tools constant.
ENV_VAR = "AI_SDLC_VAULT_ROOT"

# A derived-constant recompute spec: (consumer module-or-name, attr name, fn(vault_dir)->value).
DerivedSpec = Tuple["ModuleType | str", str, Callable[[Path], object]]


def _as_module(m: ModuleType | str) -> ModuleType:
    """Resolve a module object or dotted-name string to an imported module."""
    if isinstance(m, ModuleType):
        return m
    return importlib.import_module(m)


@contextlib.contextmanager
def pin_vault_root(
    vault_dir: Path | str,
    *consumers: ModuleType | str,
    derived: Iterable[DerivedSpec] | None = None,
) -> Iterator[Path]:
    """Pin the process-global ``VAULT_ROOT`` to ``vault_dir`` for the block.

    in-process mechanism (setattr-pin; see module docstring):
      1. set ``AI_SDLC_VAULT_ROOT`` = ``vault_dir`` (so any subprocess this test
         spawns also resolves the pinned root) and setattr
         ``tools._vault_paths.VAULT_ROOT`` = ``vault_dir``;
      2. setattr ``<consumer>.VAULT_ROOT`` = ``vault_dir`` for each consumer that
         binds it (cures function-local ``repo_root / VAULT_ROOT / x`` readers);
      3. re-derive each frozen module-level constant in ``derived``;
      4. **assert** at least one consumer's ``VAULT_ROOT`` was set (non-vacuity —
         a pin that touched nothing is a test-author mistake; the binding
         empirical non-vacuity proof is the flip-sim suite run itself, AP-5);
      5. yield;
      6. restore every changed name in reverse (no cross-test pollution).

    NON-VACUITY SCOPE (m1, slice-110 /code-review): the step-4 assert covers ONLY
    the ``VAULT_ROOT``-binding axis — it proves ≥1 listed consumer bound
    ``VAULT_ROOT``, NOT that every frozen derived constant was re-derived. A
    consumer listed WITHOUT its needed ``derived`` entry leaves that frozen
    constant pointing at the ambient (external, under the flip sim) store and the
    helper raises NO error here. The sole guard for derived-completeness is the
    **seeded flip-sim full-suite run** (the AC1 binding gate) — a missing
    ``derived`` surfaces there as a red test, not in this helper. Keep the seeded
    flip-sim in the loop when adding tests/constants under this convention.

    Args:
        vault_dir: the vault root to pin. Pass ``Path("architecture")`` (the
            in-tree relative default) so ``repo_root / VAULT_ROOT / x`` resolves
            under the test's own ``repo_root`` fixture in BOTH worlds.
        consumers: the tool module(s) whose frozen ``VAULT_ROOT`` the test's
            runtime path reads — the call-graph closure, as module objects or
            dotted names. At least one is required.
        derived: optional frozen module-level constants to re-derive, each as a
            ``(module, attr, fn)`` triple where ``fn(vault_dir)`` returns the new
            value (e.g. ``(_pcr, "_AUDIT_LOG_PATH", lambda vr: vr / "...-log.md")``).

    Yields:
        ``Path(vault_dir)`` — the pinned vault root.
    """
    if not consumers:
        raise ValueError(
            "pin_vault_root requires at least one consumer module to pin — an "
            "empty pin cannot take effect (the consumer froze VAULT_ROOT at its "
            "own import). List the tool module(s) under test."
        )

    pinned = Path(vault_dir)
    # (kind, key..., old) restore records, applied in reverse on exit.
    _env_unset = object()
    saved_env = os.environ.get(ENV_VAR, _env_unset)
    saved_attrs: list[tuple[ModuleType, str, object]] = []

    def _set(mod: ModuleType, attr: str, value: object) -> None:
        saved_attrs.append((mod, attr, getattr(mod, attr)))
        setattr(mod, attr, value)

    import tools._vault_paths as _vp

    try:
        os.environ[ENV_VAR] = str(pinned)
        _set(_vp, "VAULT_ROOT", pinned)

        changed = False
        for c in consumers:
            mod = _as_module(c)
            if mod is _vp:
                # _vault_paths.VAULT_ROOT was already pinned above; count it as a
                # valid (non-vacuous) consumer but do NOT re-record it (m3,
                # slice-110 /code-review — avoid a duplicate saved_attrs entry).
                changed = True
                continue
            if hasattr(mod, "VAULT_ROOT"):
                _set(mod, "VAULT_ROOT", pinned)
                changed = True

        for mod_ref, attr, fn in derived or ():
            dmod = _as_module(mod_ref)
            _set(dmod, attr, fn(pinned))

        assert changed, (
            "pin_vault_root non-vacuity FAILED: none of the listed consumers "
            f"{[getattr(_as_module(c), '__name__', c) for c in consumers]} bind a "
            "VAULT_ROOT attribute, so the pin touched nothing. List the tool "
            "module(s) whose VAULT_ROOT the test's runtime path actually reads."
        )
        yield pinned
    finally:
        for mod, attr, old in reversed(saved_attrs):
            setattr(mod, attr, old)
        if saved_env is _env_unset:
            os.environ.pop(ENV_VAR, None)
        else:
            os.environ[ENV_VAR] = saved_env  # type: ignore[arg-type]


_ENV_UNSET = object()


@contextlib.contextmanager
def default_vault_root() -> Iterator[Path]:
    """Force + yield the genuine NO-ENV default ``VAULT_ROOT`` resolution.

    For tests that assert the un-flipped default (``VAULT_ROOT == Path("architecture")``
    / the no-flip byte-identity contract): under the ``AI_SDLC_VAULT_ROOT=<seeded>``
    flip simulation the ambient ``VAULT_ROOT`` is the external root, so reading it
    directly is no longer the default. It resolves through the real precedence (env →
    git-common-dir config → ``architecture``) with BOTH the env AND the config
    isolated, so the result is the genuine default — proving the resolution logic,
    not a tautology.

    slice-115 ([[ADR-107]] — THE flip): this repo is now genuinely FLIPPED — a live
    ``$GIT_COMMON_DIR/aisdlc/vault-root`` config exists — so the original mechanism
    (pop env + ``importlib.reload``) would RE-READ that live config and resolve
    EXTERNAL (the slice-115 post-flip suite-run surfaced exactly this). The fix
    isolates the config too: pop the env AND stub ``_read_common_dir_config`` → None,
    then call ``_resolve_vault_root()`` DIRECTLY (no reload — a reload re-defines the
    stubbed function, un-doing the stub; direct-resolve keeps it in effect and is
    also identity-safe). With env None + config None the precedence falls to the
    ``architecture`` default regardless of whether the live repo is flipped.
    """
    import tools._vault_paths as _vp

    saved_env = os.environ.pop(ENV_VAR, _ENV_UNSET)
    saved_reader = _vp._read_common_dir_config
    try:
        _vp._read_common_dir_config = lambda: None  # isolate the live (flipped) config
        yield _vp._resolve_vault_root()
    finally:
        _vp._read_common_dir_config = saved_reader
        if saved_env is not _ENV_UNSET:
            os.environ[ENV_VAR] = saved_env  # type: ignore[arg-type]


def autouse_pin(
    *consumers: ModuleType | str,
    derived: Iterable[DerivedSpec] | None = None,
    vault: Path | str = "architecture",
):
    """Return an autouse pytest fixture that pins :func:`pin_vault_root` for a
    whole test module — the DRY form for the many breaking files that share an
    identical consumer + ``derived`` set (notably the parallel-conflict-resolver
    family). Assign it to a module-level name; pytest collects it as an autouse
    fixture::

        _pin = vi.autouse_pin(_vgit, _pcr,
            derived=[(_pcr, "_AUDIT_LOG_PATH", lambda vr: vr / "...-log.md")])

    The consumer set stays explicit at each call site (auditability); only the
    fixture boilerplate is factored out.
    """
    import pytest

    @pytest.fixture(autouse=True)
    def _pin_vault_location_agnostic() -> Iterator[Path]:
        with pin_vault_root(vault, *consumers, derived=derived) as v:
            yield v

    return _pin_vault_location_agnostic


def subprocess_env(
    vault_dir: Path | str | None = None,
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    """Build a child-process env that resolves its OWN vault, not the sim's.

    A subprocess test (``$PY -m tools.X --repo-root tmp``) must not let the child
    inherit the parent's flip-sim ``AI_SDLC_VAULT_ROOT`` — under the override the
    child would read the seeded external store instead of its ``tmp/architecture``
    fixture. This returns a copy of the ambient environment with ``AI_SDLC_VAULT_
    ROOT`` either removed (``vault_dir is None`` → the child resolves the relative
    ``architecture`` default under its ``--repo-root``) or set explicitly to
    ``vault_dir`` (the child's own tmp vault, absolute).

    Args:
        vault_dir: if given, the absolute vault path the child should use; if
            ``None``, the var is removed so the child falls back to the default.
        base: the environment to copy (defaults to ``os.environ``).

    Returns:
        A new ``dict[str, str]`` suitable for ``subprocess.run(..., env=...)``.
    """
    env = dict(os.environ if base is None else base)
    if vault_dir is None:
        env.pop(ENV_VAR, None)
    else:
        env[ENV_VAR] = str(vault_dir)
    return env
