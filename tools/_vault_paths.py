"""Vault-root path constant (slice-068; resolution extended slice-093 / ADR-085).

Exports VAULT_ROOT — the single seam routing tools/*.py filesystem
references to the vault directory. **Resolution precedence** (slice-093 /
[[ADR-085]], layered on ADR-065's env seam):

  1. env var ``AI_SDLC_VAULT_ROOT`` (if set) — unchanged from ADR-065.
  2. the per-project config at ``$GIT_COMMON_DIR/aisdlc/vault-root`` (a
     single line: the absolute vault path) — shared identically across all
     worktrees of a repo (the git common-dir is shared), and never
     git-tracked (it lives inside ``.git/``). Written by the slice-094
     flip; ABSENT by default.
  3. default ``Path("architecture")`` — UNCHANGED from slice-068.

For this repo (no env, no config) VAULT_ROOT resolves to
``Path("architecture")`` EXACTLY as before slice-093 — the no-flip
safety contract.

Per [[ADR-065]] + [[ADR-085]]. Leading-underscore-helper module per
UTF8-STDOUT-1 / ``tools/_stdout.py`` precedent — auto-excluded from PMI-1
inventory (``tools/plugin_manifest_audit.py:148`` filter).

**Leaf invariant** (pinned by
``test_vault_root_constant.py::test_vault_paths_module_is_leaf``): this
module imports ONLY stdlib (``os``, ``subprocess``, ``sys``, ``pathlib``)
— never ``tools.*`` — so it stays the dependency leaf of the VAULT_ROOT
cascade. The git-common-dir read uses stdlib ``subprocess`` (still a leaf),
and the stderr diagnostics use the encoding-safe ``_stderr`` helper below
(stdlib ``sys`` only — does NOT import ``tools._stdout``, which would break
leaf-purity).

**Read-at-import + consumer-freeze cascade** (production-correctness
semantic per ADR-065 §Decision + design.md §Consumer-freeze cascade —
PRESERVED by slice-093): the env var AND the git-common-dir config are
read EXACTLY ONCE at this module's import. Downstream consumers that
compose VAULT_ROOT into their own module-level constants (e.g.,
``tools.slice_queue_writer._INDEX_MD_REL = VAULT_ROOT / "slices" /
"_index.md"``) FREEZE the derived Path at THEIR import-time value.
In-process ``monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", ...)``
does NOT propagate to those frozen consumer constants. Cross-process env
override works via subprocess fixtures (env injection at process
boundary). Pinned by
``tests/methodology/test_vault_root_constant.py::test_consumer_constants_are_frozen_at_first_import``.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_ENV_VAR = "AI_SDLC_VAULT_ROOT"
_DEFAULT = "architecture"

# The per-project config path RELATIVE to the git common-dir. SINGLE SOURCE
# OF TRUTH for the config location (slice-093 m2): ``tools/_vault_write.py``
# imports this constant rather than re-deriving it, so the inline reader here
# and the writer there cannot diverge (pinned by
# test_vault_safe_write.py::test_inline_and_helper_config_readers_agree).
_CONFIG_REL = "aisdlc/vault-root"


def _stderr(msg: str) -> None:
    """Encoding-safe stderr write (leaf-safe — stdlib only). A bare
    ``print(..., file=sys.stderr)`` raises ``UnicodeEncodeError`` on a
    non-ASCII path under a cp1252 stderr (the repo's documented Windows
    footgun — CLAUDE.md "Windows Python stdout is cp1252"), which would crash
    EVERY consumer at import since these diagnostics fire during
    ``_resolve_vault_root`` at module-import. Write UTF-8 bytes with
    ``errors="replace"`` when a buffer is available, else an ascii-folded
    ``print`` fallback. (slice-093 /code-review M1.)
    """
    line = msg + "\n"
    buf = getattr(sys.stderr, "buffer", None)
    if buf is not None:
        try:
            buf.write(line.encode("utf-8", "replace"))
            buf.flush()
            return
        except (OSError, ValueError):
            pass
    try:
        print(msg, file=sys.stderr)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"), file=sys.stderr)


def _read_common_dir_config() -> str | None:
    """Return the vault path configured at ``$GIT_COMMON_DIR/aisdlc/vault-root``,
    or ``None`` when no config applies.

    Defensive (R-7 fail-visible): not-a-git-repo / git-unavailable /
    config-absent → ``None`` (the INTENDED default-to-``architecture`` path,
    NOT a disabled feature, so no warning). Config / git output PRESENT but
    non-UTF-8 / unreadable / empty → stderr WARN + ``None`` (never a silent
    mis-resolve, never an uncaught reader-thread traceback). stdlib only —
    leaf-purity preserved.

    Git output is captured as BYTES and decoded explicitly in the MAIN thread
    (slice-093 /code-review m1 / the R-30 / slice-091 pattern): a
    ``subprocess.run(..., encoding="utf-8")`` decodes in the reader thread and
    would raise an UNCAUGHT ``UnicodeDecodeError`` there on a non-UTF-8
    git-common-dir path (``UnicodeDecodeError`` is not an ``OSError``).
    """
    try:
        cp = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,  # BYTES — decoded explicitly below (main thread)
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None  # git binary unavailable / failed to spawn → default
    if cp.returncode != 0:
        return None  # not inside a git work tree → default
    try:
        common_dir = cp.stdout.decode("utf-8").strip()
    except UnicodeDecodeError:
        _stderr(
            "WARN: AI-SDLC git-common-dir path is not UTF-8; "
            f"falling back to '{_DEFAULT}'."
        )
        return None
    if not common_dir:
        return None
    cfg = Path(common_dir) / _CONFIG_REL
    try:
        if not cfg.exists():
            return None  # no config written (the normal case) → default
        text = cfg.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError) as exc:
        _stderr(
            f"WARN: AI-SDLC vault-root config at {cfg} is present but unreadable "
            f"({exc}); falling back to '{_DEFAULT}'."
        )
        return None
    if not text:
        _stderr(
            f"WARN: AI-SDLC vault-root config at {cfg} is empty; "
            f"falling back to '{_DEFAULT}'."
        )
        return None
    return text


def _resolve_vault_root() -> Path:
    """3-tier resolution: env ``AI_SDLC_VAULT_ROOT`` → git-common-dir config →
    default ``Path("architecture")``. Read ONCE at module import.

    Observability (must-not-defer): a NON-default resolution (env or config
    override) emits a one-line stderr INFO naming the chosen root + WHY (via
    the encoding-safe ``_stderr``); the default path stays silent (it fires on
    every tool import in an un-flipped repo, so logging it would be noise).
    """
    env = os.environ.get(_ENV_VAR)
    if env:
        _stderr(f"INFO: AI-SDLC vault root = {env!r} (via {_ENV_VAR} env var).")
        return Path(env)
    cfg = _read_common_dir_config()
    if cfg:
        _stderr(f"INFO: AI-SDLC vault root = {cfg!r} (via git-common-dir config).")
        return Path(cfg)
    return Path(_DEFAULT)


VAULT_ROOT: Path = _resolve_vault_root()

# slice-098 / [[ADR-089]]: an OPTIONAL cheap fast-path / observability flag — True
# iff resolution fell through to the relative ``Path("architecture")`` default
# (env unset AND no git-common-dir config). It is NOT the binding RETIRE gate:
# the precise per-pathspec ``git ls-files --error-unmatch`` tracked-check in
# ``tools/_vault_git.vault_pathspec_is_tracked`` is the binding signal (the proxy
# conflates "fell through to default" with "git-untracked"). Frozen-at-import per
# the consumer-freeze cascade. An env set to a relative ``"architecture"`` folds
# to True here, which is harmless — the in-tree vault IS tracked, so the
# downstream tracked-check runs git normally.
VAULT_ROOT_IS_DEFAULT: bool = VAULT_ROOT == Path(_DEFAULT)
