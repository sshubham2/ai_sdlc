"""ai-sdlc-tools pip-package version forward-sync gate (TVFS-1).

Per **TVFS-1** (`methodology-changelog.md` v0.63.0; slice-059; [[ADR-058]];
extends the slice-050/AVFS-1 + slice-041/MCFS-1
forward-sync-via-deterministic-downstream-gate lineage; mints a new rule;
supersedes nothing).

The PMI-1 atomic version bump has, after slice-054/PVFS-1, five *source-side*
or *installed-file* legs — `VERSION`, `plugin.yaml.version` (PMI-1),
`pyproject.toml [project].version` (PVFS-1), installed `~/.claude/
ai-sdlc-VERSION` (AVFS-1), installed `~/.claude/methodology-changelog.md`
(MCFS-1). The **installed `ai-sdlc-tools` pip distribution** is a sixth,
ungated leg: PVFS-1 keeps `pyproject.toml` correct so the *next* `pip
install` builds a correctly-versioned wheel, but nothing forces the
*re-install* — the venv package drifted silently to `0.20.0` while the
source advanced to `0.62.0`. TVFS-1 is the deterministic downstream gate
for that leg (the slice-030A/ADR-029 / slice-041/MCFS-1 rationale: the
only sound control for a non-deterministic LLM-executed step — "re-run
`pip install --upgrade`" — is a deterministic downstream gate).

Read-mechanism hazard (B1 — first-Critic finding, slice-059). The naive
`importlib.metadata.version("ai-sdlc-tools")` does NOT read the venv
artifact when run from the source repo: `setuptools` writes an
`ai_sdlc_tools.egg-info/` directory into the source tree on `pip install`,
`importlib.metadata` discovers metadata from every `sys.path` entry
(including the CWD), and the in-repo egg-info — whose `Version` is
regenerated from `pyproject.toml`, which PVFS-1 keeps equal to `VERSION` —
shadows the venv `.dist-info`, making the naive read tautologically green.
`_resolve_installed_version()` therefore scopes the enumeration to
`sysconfig.get_path("purelib")` (the running interpreter's site-packages),
excluding the in-repo egg-info by construction. The audit always runs
under `$PY` (the venv interpreter) per the pipeline `$PY` convention, so
`purelib` IS the pipeline's venv site-packages.

Divergences from the AVFS-1 clone: (1) no CRLF→LF / `_normalized_bytes`
machinery — the installed side is an `importlib.metadata` version string,
not a file; equality is plain trimmed-string `==`. (2) the installed side
is resolved by `_resolve_installed_version()` (purelib-scoped), not a file
path; `check()` exposes an `installed_version_resolver` injection seam
(B2) so the regression suite can drive a genuine non-tautological drift
case. `--root` is RETAINED — TVFS-1 still reads the in-repo `VERSION` file.

Semantics:
  - in-repo `VERSION` absent/unreadable, or repo root unresolvable ⇒ exit
    2 (usage error: the repo is malformed).
  - `ai-sdlc-tools` not installed in the running interpreter's venv
    site-packages ⇒ WARN, exit 0. The pip package is environment-
    dependent/untracked; a machine that simply hasn't installed the
    plugin must not HALT `/build-slice` (AVFS-1 installed-absent parity).
    The WARN message names `sys.executable` + `purelib` (M3 — TVFS-1's
    WARN is weaker than AVFS-1's: "not in this interpreter's
    site-packages" can co-exist with a stale install reachable another
    way).
  - installed version present but ≠ trimmed in-repo `VERSION` ⇒ HALT,
    exit 1, attributed: "AI-SDLC-TOOLS VERSION DRIFT — … re-run
    INSTALL.md Step 3g … this is NOT a slice regression".
  - >1 `ai-sdlc-tools` distribution in `purelib` (a real pip failure
    mode — a stale `.dist-info` left by an interrupted upgrade) ⇒ exit 2
    (usage), with its OWN distinct message naming the `pip uninstall`
    remediation (M-add-2 — meta-Critic finding). Exit code stays 2; no
    4th exit code, the AVFS-1 tri-state contract is preserved.

Wiring (slice-059, 2 points — both ungated; AVFS-1 / MCFS-1 2-point shape):
  - `/build-slice` Step 6 pre-finish — non-opt-out, runs every slice.
  - `/reflect` a dedicated post-write step (Step 5b-tvfs) — explicitly
    NOT folded into the rule-promotion-gated Step 5b (R-7/slice-022
    silent-disable class).

This module reads the environment-mutable installed distribution metadata
and is **non-catalog by construction** (slice-029/030A discipline): it is
NOT cited in any `architecture/shippability.md` `Machine-cmd` cell. Only
the two in-repo-only entry-pins
`test_methodology_changelog.py::test_v_0_63_0_tvfs_1_entry_present_in_repo`
+ `::test_v_0_63_0_tvfs_1_shippability_consumer_propagation` carry row #59.

Usage:
    python -m tools.ai_sdlc_tools_version_forward_sync            # --check
    python -m tools.ai_sdlc_tools_version_forward_sync --check
    python -m tools.ai_sdlc_tools_version_forward_sync --json
    python -m tools.ai_sdlc_tools_version_forward_sync --root <repo-root>

Exit codes:
    0  synced (installed == in-repo VERSION) OR not-installed WARN
       (distinct stdout)
    1  HALT — installed present but ≠ in-repo VERSION
    2  usage error — in-repo VERSION missing/unreadable, repo root
       unresolvable, OR >1 ai-sdlc-tools distribution in site-packages
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import sys
import sysconfig
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout
from tools._forward_sync_base import installed_is_sibling_ahead

_VERSION_REL = "VERSION"
_DIST_NAME = "ai-sdlc-tools"

_ATTRIB_DRIFT = (
    "AI-SDLC-TOOLS VERSION DRIFT — the installed ai-sdlc-tools pip package "
    "(v{installed}) does not match in-repo VERSION (v{in_repo}); re-run "
    "INSTALL.md Step 3g (`$PY -m pip install --upgrade <ai-sdlc-source>`) to "
    "refresh the venv. This is NOT a slice regression — the installed pip "
    "distribution is the forward-synced leg TVFS-1 gates."
)

_ATTRIB_DUP = (
    "AI-SDLC-TOOLS DUPLICATE DISTRIBUTION — {count} ai-sdlc-tools "
    "distributions ({versions}) found in {purelib}. This is a real (if "
    "uncommon) pip failure mode — a stale .dist-info left beside the current "
    "one by an interrupted upgrade or a version-renamed reinstall. It is an "
    "ENVIRONMENT fault, not a malformed repo: run `$PY -m pip uninstall "
    "ai-sdlc-tools` (repeat until none remain) then re-run INSTALL.md Step 3g."
)

_WARN_NOT_INSTALLED = (
    "ai-sdlc-tools distribution not found in this interpreter's site-packages "
    "({purelib}); interpreter checked: {executable}. If you have installed "
    "ai-sdlc-tools, it is not visible to THIS interpreter — verify $PY points "
    "at ~/.claude/.venv per ~/.claude/CLAUDE.md. This is a WARN (a machine "
    "that has not installed the plugin must not HALT /build-slice), not a "
    "slice regression."
)


class DuplicateDistributionError(Exception):
    """Raised by `_resolve_installed_version` when >1 `ai-sdlc-tools`
    distribution is present in the scoped site-packages (M-add-2).

    Carries the discovered versions + the site-packages path so `check()`
    can render the distinct duplicate-distribution remediation message.
    """

    def __init__(self, versions: list[str], purelib: str) -> None:
        self.versions = versions
        self.purelib = purelib
        super().__init__(
            f"{len(versions)} ai-sdlc-tools distributions in {purelib}: "
            f"{versions}"
        )


def _norm(name: str | None) -> str:
    """Normalize a distribution name for comparison (PEP 503-ish:
    lowercase, `_`→`-`, stripped)."""
    return (name or "").strip().lower().replace("_", "-")


def _resolve_installed_version(purelib: str | None = None) -> str | None:
    """Resolve the installed `ai-sdlc-tools` distribution version, scoped to
    the running interpreter's site-packages.

    Enumerates `importlib.metadata.distributions(path=[purelib])` — NOT the
    naive `importlib.metadata.version()`, which discovers metadata from every
    `sys.path` entry and is shadowed by an in-repo `ai_sdlc_tools.egg-info/`
    build artifact (B1). Scoping to `sysconfig.get_path("purelib")` excludes
    the egg-info by construction.

    Returns the version string when exactly one distribution is found,
    `None` when none is found (not installed in this venv — the WARN case).
    Raises `DuplicateDistributionError` when >1 is found (M-add-2). The
    enumerate-and-filter approach never raises `PackageNotFoundError`.

    `purelib` is overridable so the regression suite can point the real
    resolver at a controlled fixture directory.
    """
    site = purelib if purelib is not None else sysconfig.get_path("purelib")
    dists = [
        d
        for d in importlib.metadata.distributions(path=[site])
        if _norm(d.metadata["Name"]) == _DIST_NAME
    ]
    if not dists:
        return None
    if len(dists) > 1:
        raise DuplicateDistributionError(
            sorted(d.version for d in dists), str(site)
        )
    return dists[0].version


@dataclass
class CheckResult:
    status: str = "synced"              # synced | drift | warn | usage
    exit_code: int = 0
    warnings: list[str] = field(default_factory=list)
    divergences: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "warnings": self.warnings,
            "divergences": self.divergences,
        }


def check(
    root: Path,
    *,
    installed_version_resolver: Callable[[], str | None] = (
        _resolve_installed_version
    ),
) -> CheckResult:
    """Assert the installed `ai-sdlc-tools` pip-package version is
    forward-synced to in-repo `VERSION`.

    `installed_version_resolver` is the B2 injection seam — a zero-arg
    callable returning the installed version `str`, or `None` when not
    installed; it MAY raise `DuplicateDistributionError`. The default is the
    real `_resolve_installed_version` (purelib-scoped).
    """
    result = CheckResult()
    in_repo = root / _VERSION_REL

    if not in_repo.is_file():
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            f"in-repo {in_repo} missing/unreadable — the repo is malformed "
            f"(not vault drift)."
        )
        return result

    try:
        in_repo_version = in_repo.read_text(encoding="utf-8").strip()
    except OSError as e:
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            f"in-repo {in_repo} unreadable ({e}) — the repo is malformed."
        )
        return result

    try:
        installed_version = installed_version_resolver()
    except DuplicateDistributionError as e:
        # M-add-2: an environment fault with its own remediation — NOT a
        # malformed repo. Exit 2 (usage), distinct message.
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            _ATTRIB_DUP.format(
                count=len(e.versions),
                versions=", ".join(e.versions),
                purelib=e.purelib,
            )
        )
        return result

    if installed_version is None:
        # AVFS-1 installed-absent parity: WARN, exit 0.
        result.status = "warn"
        result.exit_code = 0
        result.warnings.append(
            _WARN_NOT_INSTALLED.format(
                purelib=sysconfig.get_path("purelib"),
                executable=sys.executable,
            )
        )
        return result

    if installed_version.strip() != in_repo_version:
        # slice-117 / ADR-108 (version gate → version-ordering): installed
        # strictly-newer than in-repo ⟹ a sibling re-installed the shared venv
        # ahead (external-drift WARN). Installed OLDER ⟹ a genuinely stale venv
        # never `pip install --upgrade`d (M-add-2 must-not-mask) → HALT.
        # Unparseable (None) ⟹ strict HALT (never mask).
        if installed_is_sibling_ahead(in_repo_version, installed_version.strip()) is True:
            result.status = "external-drift"
            result.exit_code = 0
            result.warnings.append(
                f"EXTERNAL-DRIFT (not a slice regression): the installed "
                f"ai-sdlc-tools venv package (v{installed_version.strip()}) is a "
                f"strictly-newer version than in-repo VERSION (v{in_repo_version}) "
                f"— a sibling slice re-installed the shared venv ahead. Rebase onto "
                f"the default branch to catch up."
            )
        else:
            result.status = "drift"
            result.exit_code = 1
            result.divergences.append(
                _ATTRIB_DRIFT.format(
                    installed=installed_version.strip(), in_repo=in_repo_version
                )
            )
        return result

    result.status = "synced"
    result.exit_code = 0
    return result


def _format_human(result: CheckResult) -> str:
    if result.status == "usage":
        return (
            "TVFS-1 ai-sdlc-tools version forward-sync: USAGE ERROR\n\n"
            + "".join(f"  {d}\n" for d in result.divergences)
        )
    if result.status == "drift":
        return (
            "TVFS-1 ai-sdlc-tools version forward-sync: DRIFT (HALT)\n\n"
            + "".join(f"  {d}\n" for d in result.divergences)
        )
    if result.status == "external-drift":
        return (
            "TVFS-1 ai-sdlc-tools version forward-sync: PASS (external-drift WARN — not a slice regression)\n\n"
            + "".join(f"  {w}\n" for w in result.warnings)
        )
    if result.status == "warn":
        return (
            "TVFS-1 ai-sdlc-tools version forward-sync: PASS (with WARN)\n\n"
            + "".join(f"  WARN: {w}\n" for w in result.warnings)
        )
    return (
        "TVFS-1 ai-sdlc-tools version forward-sync: PASS — the installed "
        "ai-sdlc-tools pip package matches in-repo VERSION.\n"
    )


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="ai_sdlc_tools_version_forward_sync",
        description=(
            "TVFS-1 — assert the installed ai-sdlc-tools pip-package version "
            "equals in-repo VERSION (the installed-distribution leg of the "
            "PMI-1 version bump)"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check forward-sync (default action)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repo root (default: two parents up from this file)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    args = parser.parse_args(argv)

    if args.root is None:
        root = Path(__file__).resolve().parent.parent
    else:
        root = args.root.resolve()

    if not root.exists():
        sys.stderr.write(f"repo root not found: {root}\n")
        return 2

    result = check(root)

    if result.status == "external-drift":
        # ADR-108 round-2 M1: persist a recoverable breadcrumb (advisory — never
        # changes the gate verdict/exit code).
        try:
            from tools._forward_sync_breadcrumb import emit_external_drift
            emit_external_drift(
                "TVFS-1", _VERSION_REL,
                "; ".join(result.warnings) or "installed venv strictly-newer (sibling-ahead)",
            )
        except (OSError, TimeoutError, ImportError) as exc:
            sys.stderr.write(
                f"TVFS-1: external-drift breadcrumb write failed (advisory, "
                f"gate verdict unchanged): {exc}\n"
            )

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
