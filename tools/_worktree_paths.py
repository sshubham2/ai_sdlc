"""Shared worktree-create logic (BRANCH-3 / slice-099 / [[ADR-090]]).

Single source of truth for the canonical worktree path + slice branch name
+ the R-20 derived-dir seed. Used by:

- ``skills/slice/SKILL.md`` Step 5.5 (worktree-at-pick — BRANCH-3) via the CLI,
- ``skills/build-slice/SKILL.md`` ``### Branch state`` (the legacy/create path) via the CLI,
- ``tools/branch_workflow_audit.py`` (end-state validation) via import,

so the three surfaces compute the canonical path + branch identically and
cannot drift (slice-099 AC5 — single source of truth on the primary path).

Per **BRANCH-3** (``methodology-changelog.md`` v0.81.0; slice-099; [[ADR-090]];
partial-supersedes ADR-063 BRANCH-2 build-time worktree timing): the worktree
is created at ``/slice`` pick-time, not ``/build-slice``. The canonical path
convention itself is UNCHANGED from BRANCH-2 — ``<main-parent>/<main-name>-wt/
slice-NNN-<name>`` on ``slice/NNN-<name>`` — this module only centralizes its
computation. ``_SLICE_FOLDER_RE`` + ``slice_branch_name`` + the canonical-path
logic were moved verbatim out of ``branch_workflow_audit.py`` (which now imports
them, internal-audit use); behavior is byte-identical.

Underscore-prefixed (``_worktree_paths``) like ``_vault_paths`` / ``_vault_write``
/ ``_stdout`` — a shared helper, NOT a catalogued tool, so it carries no
``plugin.yaml`` / ``install_audit.py`` / INSTALL.md inventory count and no PMI-1
module-count bump (the MEPD precedent).

Usage::

    # Library API (imported by branch_workflow_audit.py)
    from tools._worktree_paths import (
        canonical_worktree_path, slice_branch_name, seed_derived_dirs,
    )

    # CLI (invoked by /slice + /build-slice prose to compute path + branch)
    python -m tools._worktree_paths --slice-folder slice-NNN-<name> --repo-root .
    # → stdout line 1: <canonical worktree path>
    #   stdout line 2: slice/NNN-<name>

Exit codes (CLI)::

    0  path + branch printed
    2  usage error (slice-folder name fails ``slice-NNN-<name>`` shape)
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from tools import _stdout

# Slice-folder pattern: `slice-NNN-<slice-name>` (zero-padded 3-digit number).
# Moved verbatim from branch_workflow_audit.py (slice-099 / BRANCH-3); that
# module now imports it (internal-audit use). The strict numeric-only accept is
# unchanged — the letter-suffixed split-slice diagnostic regex stays in
# branch_workflow_audit (it is audit-message-only, not a path-compute concern).
_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")

# R-20 derived-dir seed set: gitignored outputs a fresh worktree needs copied
# from the main tree (slice-093 L47 / slice-088 L71 — the seed BRANCH-2 codified
# only in /build-slice; BRANCH-3 moves the create to /slice, so this MUST be
# callable from both surfaces or the seed silently drops).
_DERIVED_DIRS: tuple[str, ...] = ("diagnose-out", "graphify-out")


def slice_branch_name(slice_folder_name: str) -> str:
    """Compute ``slice/NNN-<slice-name>`` from a slice-folder NAME.

    Returns ``""`` when ``slice_folder_name`` does not match the strict
    ``slice-NNN-<name>`` shape (caller decides how to handle the miss — the
    audit emits its split-slice-aware diagnostic; the CLI exits 2).
    """
    match = _SLICE_FOLDER_RE.match(slice_folder_name)
    if not match:
        return ""
    number, name = match.group(1), match.group(2)
    return f"slice/{number}-{name}"


def canonical_worktree_path(slice_folder_name: str, main_repo_root: Path) -> Path:
    """Canonical sibling-dir worktree path for ``slice_folder_name``.

    ``<main-parent>/<main-name>-wt/<slice-folder-name>`` per the BRANCH-2
    convention ([[ADR-063]] §Decision), unchanged by BRANCH-3. For main repo
    ``C:\\Users\\sshub\\ai_sdlc`` + folder ``slice-099-create-worktree-at-slice-pick``
    → ``C:\\Users\\sshub\\ai_sdlc-wt\\slice-099-create-worktree-at-slice-pick``.
    """
    main_repo_root = Path(main_repo_root)
    return main_repo_root.parent / f"{main_repo_root.name}-wt" / slice_folder_name


def seed_derived_dirs(main_repo_root: Path, worktree_path: Path) -> None:
    """R-20 seed: copy gitignored derived dirs from main tree → worktree.

    For each dir in ``_DERIVED_DIRS`` (``diagnose-out`` / ``graphify-out``):
    copy it into ``worktree_path`` only if it EXISTS in ``main_repo_root`` AND
    the target does NOT already exist in the worktree.

    Idempotency rule (slice-099 m1): "already seeded" = the target dir exists
    at all → skip (never clobber). This accepts the low-likelihood partial-seed
    risk (a seed interrupted mid-copy leaves a non-empty-but-incomplete dir that
    the guard then skips) in exchange for never clobbering a complete seed; the
    realistic failure mode (re-running ``/build-slice`` on an already-seeded
    BRANCH-3 worktree) is handled correctly — no double-copy.
    """
    main_repo_root = Path(main_repo_root)
    worktree_path = Path(worktree_path)
    for name in _DERIVED_DIRS:
        src = main_repo_root / name
        dst = worktree_path / name
        if src.is_dir() and not dst.exists():
            shutil.copytree(src, dst)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools._worktree_paths",
        description=(
            "Compute the canonical worktree path + slice branch for a slice "
            "folder name (BRANCH-3 / slice-099). Single source of truth shared "
            "by /slice, /build-slice, and branch_workflow_audit."
        ),
    )
    p.add_argument(
        "--slice-folder", required=True,
        help="Slice folder NAME, e.g. slice-099-create-worktree-at-slice-pick.",
    )
    p.add_argument(
        "--repo-root", type=Path, default=Path("."),
        help="Main repo root (default: cwd). The worktree is its sibling -wt dir.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2

    branch = slice_branch_name(args.slice_folder)
    if not branch:
        print(
            f"_worktree_paths usage error: slice-folder name does not match "
            f"`slice-NNN-<name>`: {args.slice_folder}",
            file=sys.stderr,
        )
        return 2
    wt = canonical_worktree_path(args.slice_folder, args.repo_root.resolve())
    print(str(wt))
    print(branch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
