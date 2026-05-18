"""Methodology-changelog forward-sync gate (MCFS-1).

Per **MCFS-1** (`methodology-changelog.md` v0.53.0; slice-041, split-lineage
label "030C"; [[ADR-042]] + [[ADR-043]]).

The in-repo↔installed forward-sync of `methodology-changelog.md` is the
property that guarantees `/critic-calibrate` (and any installed-copy reader)
sees current, not stale, methodology. Before slice-041 that invariant was
half-asserted by ~33 per-version `test_v_0_NN_0_*` pins each reading the
**untracked** `~/.claude/methodology-changelog.md` — an "essential" coupling
with no BCI-1 analogue (R-4's residual; the false-PCA-1-HALT window). The
PMI-1 4-part forward-sync that produces the installed copy is LLM-executed
prose with no deterministic source; the only sound control for a
non-deterministic step is a deterministic downstream gate (the
slice-030A/ADR-029 precedent, BCI-1's exact rationale).

MCFS-1 is that gate. It re-homes the per-version reads onto ONE whole-file
content-equality check: in-repo `methodology-changelog.md` MUST be
content-equal **modulo line endings** to installed
`~/.claude/methodology-changelog.md`. Whole-file equality is strictly
stronger than the per-version substring reads (if the whole files are equal,
every entry's substring is equal). The comparison is EOL-agnostic
(EOL-DRIFT-1 / [[ADR-033]]): a CRLF working tree vs an LF installed copy with
identical content is CLEAN, while genuine (non-line-ending) divergence still
HALTs. The 1-line CRLF→LF normalization is implemented locally (avoids a
`tools/`→`tests/` import inversion; ADR-033's comparator home stays
untouched) and is CSP-1 behaviour-parity-pinned to
`tests/skill_drift_equality.py::_normalized_sha256`.

Semantics (BCI-1 / slice-030A meta-M3 parity):
  - in-repo `methodology-changelog.md` absent/unreadable, or repo root
    unresolvable ⇒ exit 2 (usage error: the repo is malformed).
  - installed `~/.claude/methodology-changelog.md` **absent** (file does not
    exist) ⇒ WARN, exit 0. The installed copy is untracked and
    environment-dependent; a machine that simply hasn't installed the plugin
    must not HALT `/build-slice`.
  - installed file **present but content-divergent after CRLF→LF**
    (including empty-present — empty != absent, so R-4-class is not silently
    reopened) ⇒ HALT, exit 1, with an attributed message:
    "METHODOLOGY-CHANGELOG FORWARD-SYNC DRIFT — re-run the PMI-1 forward-sync
    (in-repo → ~/.claude/); this is NOT a slice regression".

Wiring (slice-041, 2 points — both ungated; m1 / DR-1):
  - `/build-slice` Step 6 pre-finish — non-opt-out, runs every slice, NOT
    gated on rule promotion (the verified-ungated checklist gate).
  - `/reflect` a NEW dedicated post-write step — explicitly NOT folded into
    the rule-promotion-gated Step 5b (else the gate silently never runs on a
    version-bumping-but-no-rule-promoted slice — R-7/slice-022 class).

This module is **non-catalog by construction** (M-add-1 relocation guard):
it is never cited in any `architecture/shippability.md` `Machine-cmd` cell
and is not a callee of any catalog-cited test fn, so
`tools.shippability_decoupling_audit._cited()` cannot resolve it — the
compensating guard cannot itself become the relocated essential coupling.
Its regression suite `tests/methodology/test_methodology_changelog_forward_sync.py`
reads the installed copy and is therefore intentionally NOT shippability-
cited (m-add-2): only the in-repo-only-body entry-pin
`test_v_0_53_0_mcfs_1_entry_present_in_repo` carries the
catalog row.

Usage:
    python -m tools.methodology_changelog_forward_sync            # --check (default)
    python -m tools.methodology_changelog_forward_sync --check
    python -m tools.methodology_changelog_forward_sync --json
    python -m tools.methodology_changelog_forward_sync --root <repo-root>

Exit codes:
    0  synced (content-equal modulo EOL) OR installed-absent WARN
       (distinct stdout)
    1  HALT — installed present but content-divergent after CRLF→LF
    2  usage error — in-repo changelog missing/unreadable, repo root
       unresolvable
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

_CHANGELOG_REL = "methodology-changelog.md"
_INSTALLED = Path.home() / ".claude" / "methodology-changelog.md"

_ATTRIB = (
    "METHODOLOGY-CHANGELOG FORWARD-SYNC DRIFT — re-run the PMI-1 forward-sync "
    "(in-repo {in_repo} → installed {installed}); this is NOT a slice "
    "regression. The installed copy is a forward-synced copy of the in-repo "
    "source (see tools/install_audit.py canonical lists)."
)


def _normalized_bytes(path: Path) -> bytes:
    """File content with CRLF normalized to LF.

    The 1-line normalization that makes the comparison EOL-agnostic
    (EOL-DRIFT-1). Behaviour-parity-pinned to
    `tests/skill_drift_equality.py::_normalized_sha256` (CSP-1) — both
    normalize via `bytes.replace(b"\\r\\n", b"\\n")` before content
    comparison; this module owns a local copy only to avoid a `tools/`→
    `tests/` import inversion (ADR-033's comparator home is untouched).
    """
    return path.read_bytes().replace(b"\r\n", b"\n")


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


def check(root: Path, installed: Path | None = None) -> CheckResult:
    """Assert in-repo methodology-changelog.md is forward-synced to the
    installed copy, comparing content modulo line endings (EOL-DRIFT-1)."""
    result = CheckResult()
    in_repo = root / _CHANGELOG_REL
    installed_path = installed if installed is not None else _INSTALLED

    if not in_repo.is_file():
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            f"in-repo {in_repo} missing/unreadable — the repo is malformed "
            f"(not vault drift)."
        )
        return result

    if not installed_path.exists():
        # slice-030A meta-M3 parity: absent installed file is an optional-
        # install condition, NOT vault drift. WARN, exit 0.
        result.status = "warn"
        result.exit_code = 0
        result.warnings.append(
            f"installed methodology-changelog absent at {installed_path} — "
            f"install the plugin (INSTALL.md) / re-run the PMI-1 forward-sync "
            f"for full MCFS-1 coverage. This is a WARN, not a slice regression."
        )
        return result

    # Present (incl. empty-present): compare modulo EOL. empty != absent —
    # an empty present installed file is divergent ⇒ HALT (R-4-class not
    # silently reopened).
    if _normalized_bytes(in_repo) != _normalized_bytes(installed_path):
        result.status = "drift"
        result.exit_code = 1
        result.divergences.append(
            _ATTRIB.format(in_repo=in_repo, installed=installed_path)
        )
        return result

    result.status = "synced"
    result.exit_code = 0
    return result


def _format_human(result: CheckResult) -> str:
    if result.status == "usage":
        return "MCFS-1 methodology-changelog forward-sync: USAGE ERROR\n\n" + \
            "".join(f"  {d}\n" for d in result.divergences)
    if result.status == "drift":
        return "MCFS-1 methodology-changelog forward-sync: DRIFT (HALT)\n\n" + \
            "".join(f"  {d}\n" for d in result.divergences)
    if result.status == "warn":
        return "MCFS-1 methodology-changelog forward-sync: PASS (with WARN)\n\n" + \
            "".join(f"  WARN: {w}\n" for w in result.warnings)
    return (
        "MCFS-1 methodology-changelog forward-sync: PASS — in-repo "
        "methodology-changelog.md is content-equal modulo line endings to "
        "the installed copy.\n"
    )


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="methodology_changelog_forward_sync",
        description=(
            "MCFS-1 — assert in-repo methodology-changelog.md is forward-"
            "synced (content-equal modulo line endings) to the installed "
            "~/.claude/methodology-changelog.md"
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

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
