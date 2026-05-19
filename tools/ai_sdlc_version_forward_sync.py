"""ai-sdlc-VERSION forward-sync gate (AVFS-1).

Per **AVFS-1** (`methodology-changelog.md` v0.58.0; slice-050; [[ADR-052]];
extends the slice-041/MCFS-1 forward-sync-via-deterministic-downstream-gate
lineage; mints a new rule; supersedes nothing).

The PMI-1 atomic version bump has four legs: in-repo `VERSION`, installed
`~/.claude/ai-sdlc-VERSION`, `plugin.yaml.version`, and the forward-synced
`~/.claude/methodology-changelog.md`. Three are gated (PMI-1 audits
`VERSION`==`plugin.yaml`; MCFS-1 guards the installed changelog leg). The
installed `~/.claude/ai-sdlc-VERSION` leg had **no deterministic gate** — it
drifted silently N=2 (slice-035 DEVIATION-2; slice-048 latent → surfaced at
slice-049 with installed `0.55.0` vs in-repo `0.56.0`). The PMI-1 4-part
forward-sync that produces the installed copy is LLM-executed prose with no
deterministic source; the only sound control for a non-deterministic step is
a deterministic downstream gate (the slice-030A/ADR-029 / slice-041/MCFS-1
rationale).

AVFS-1 is that gate. It is a verbatim structural clone of MCFS-1
(`tools/methodology_changelog_forward_sync.py`) with two path constants
swapped: in-repo `VERSION` MUST be content-equal **modulo line endings**
(EOL-DRIFT-1 / [[ADR-033]]) to installed `~/.claude/ai-sdlc-VERSION`. The
comparison is CRLF→LF only — NOT trailing-whitespace/newline tolerant (a
`cp` of a no-trailing-newline `VERSION` is byte-identical; tolerance would
only mask corruption). The 1-line CRLF→LF normalization is implemented
locally (avoids a `tools/`→`tests/` import inversion; ADR-033's comparator
home stays untouched) and is CSP-1 behaviour-parity-pinned to
`tests/skill_drift_equality.py::_normalized_sha256`.

Semantics (BCI-1 / slice-030A meta-M3 parity, MCFS-1-identical):
  - in-repo `VERSION` absent/unreadable, or repo root unresolvable ⇒ exit 2
    (usage error: the repo is malformed).
  - installed `~/.claude/ai-sdlc-VERSION` **absent** (file does not exist) ⇒
    WARN, exit 0. The installed copy is untracked and environment-dependent;
    a machine that simply hasn't installed the plugin must not HALT
    `/build-slice`.
  - installed file **present but content-divergent after CRLF→LF**
    (including empty-present AND whitespace-only-present — empty ≠ absent, so
    R-4-class is not silently reopened) ⇒ HALT, exit 1, with an attributed
    message: "AI-SDLC-VERSION FORWARD-SYNC DRIFT — re-run the PMI-1 4-part
    forward-sync (in-repo VERSION → ~/.claude/ai-sdlc-VERSION); this is NOT
    a slice regression".

Wiring (slice-050, 2 points — both ungated; MCFS-1 2-point shape):
  - `/build-slice` Step 6 pre-finish — non-opt-out, runs every slice, NOT
    gated on rule promotion (the verified-ungated checklist gate).
  - `/reflect` a NEW dedicated post-write step (Step 5b-avfs) — explicitly
    NOT folded into the rule-promotion-gated Step 5b (else the gate silently
    never runs on a version-bumping-but-no-rule-promoted slice — R-7/
    slice-022 class).

This module is **non-catalog by construction**: it reads the untracked,
environment-mutable installed `~/.claude/ai-sdlc-VERSION`, and a shippability
`Machine-cmd` must not depend on environment-mutable/untracked state
(slice-029/030A discipline). It is NOT cited in any `architecture/
shippability.md` `Machine-cmd` cell and is not a callee of any catalog-cited
test fn. NB: `essential-unregistered` does NOT apply to this path —
`tools.shippability_decoupling_audit._ESSENTIAL_SHAPES` keys on
`~/.claude/methodology-changelog.md` only (the m-add-2 mechanism is
changelog-specific; this module's non-catalog ground is the environment-
state discipline, not essential-unregistered). Its regression suite
`tests/methodology/test_ai_sdlc_version_forward_sync.py` reads the installed
copy and is therefore intentionally NOT shippability-cited: only the
in-repo-only-body entry-pin
`test_v_0_58_0_avfs_1_entry_present_in_repo` + the consumer-propagation pin
carry catalog row #50.

Usage:
    python -m tools.ai_sdlc_version_forward_sync            # --check (default)
    python -m tools.ai_sdlc_version_forward_sync --check
    python -m tools.ai_sdlc_version_forward_sync --json
    python -m tools.ai_sdlc_version_forward_sync --root <repo-root>

Exit codes:
    0  synced (content-equal modulo EOL) OR installed-absent WARN
       (distinct stdout)
    1  HALT — installed present but content-divergent after CRLF→LF
    2  usage error — in-repo VERSION missing/unreadable, repo root
       unresolvable
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

_VERSION_REL = "VERSION"
_INSTALLED = Path.home() / ".claude" / "ai-sdlc-VERSION"

_ATTRIB = (
    "AI-SDLC-VERSION FORWARD-SYNC DRIFT — re-run the PMI-1 4-part forward-sync "
    "(in-repo {in_repo} → installed {installed}); this is NOT a slice "
    "regression. The installed copy is the forward-synced 4th leg of the "
    "PMI-1 atomic version bump (see tools/install_audit.py canonical lists)."
)


def _normalized_bytes(path: Path) -> bytes:
    """File content with CRLF normalized to LF.

    The 1-line normalization that makes the comparison EOL-agnostic
    (EOL-DRIFT-1). Behaviour-parity-pinned to
    `tests/skill_drift_equality.py::_normalized_sha256` (CSP-1) — both
    normalize via `bytes.replace(b"\\r\\n", b"\\n")` before content
    comparison; this module owns a local copy only to avoid a `tools/`→
    `tests/` import inversion (ADR-033's comparator home is untouched).
    CRLF→LF ONLY — NOT trailing-whitespace/newline tolerant (B3).
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
    """Assert in-repo VERSION is forward-synced to the installed
    `~/.claude/ai-sdlc-VERSION`, comparing content modulo line endings
    (EOL-DRIFT-1)."""
    result = CheckResult()
    in_repo = root / _VERSION_REL
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
            f"installed ai-sdlc-VERSION absent at {installed_path} — "
            f"install the plugin (INSTALL.md) / re-run the PMI-1 4-part "
            f"forward-sync for full AVFS-1 coverage. This is a WARN, not a "
            f"slice regression."
        )
        return result

    # Present (incl. empty-present / whitespace-only-present): compare modulo
    # EOL. empty ≠ absent — an empty or whitespace-only present installed
    # file is divergent ⇒ HALT (R-4-class not silently reopened).
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
        return "AVFS-1 ai-sdlc-VERSION forward-sync: USAGE ERROR\n\n" + \
            "".join(f"  {d}\n" for d in result.divergences)
    if result.status == "drift":
        return "AVFS-1 ai-sdlc-VERSION forward-sync: DRIFT (HALT)\n\n" + \
            "".join(f"  {d}\n" for d in result.divergences)
    if result.status == "warn":
        return "AVFS-1 ai-sdlc-VERSION forward-sync: PASS (with WARN)\n\n" + \
            "".join(f"  WARN: {w}\n" for w in result.warnings)
    return (
        "AVFS-1 ai-sdlc-VERSION forward-sync: PASS — in-repo VERSION is "
        "content-equal modulo line endings to the installed "
        "~/.claude/ai-sdlc-VERSION.\n"
    )


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="ai_sdlc_version_forward_sync",
        description=(
            "AVFS-1 — assert in-repo VERSION is forward-synced (content-equal "
            "modulo line endings) to the installed ~/.claude/ai-sdlc-VERSION"
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
