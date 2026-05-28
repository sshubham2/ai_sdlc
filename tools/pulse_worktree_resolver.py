"""Pulse Worktree Resolver — BRANCH-2 worktree detection + state classification.

Per slice-077 / ADR-070 (MEPD-1 EXCLUDE; /pulse-internal mechanism, not a
load-bearing cross-skill methodology rule). Library API + CLI for `/pulse`
Step 1 augmentation: detect non-main worktrees on `slice/NNN-<name>` branches
and classify each worktree's HEAD-vs-default state into one of four values.

Reuses ``tools.branch_workflow_audit._resolve_default_branch`` for default-branch
resolution (single-sourced; NAW-1 ADR-061 exit-2 contract preserved).

Reuses ``tools._stdout.reconfigure_stdout_utf8`` for Windows cp1252 console
safety per UTF8-STDOUT-1 / slice-023.

Read-only — does NOT modify worktree state, does NOT invoke git mutations.

Cross-spec parity with ``tools/parallel_conflict_resolver.py`` (PCR-1 sibling
helper) per slice-077 design.md § Cross-spec parity:

- argparse mutually-exclusive group ``required=True`` for ``--detect`` /
  ``--classify``.
- ``--repo-root`` argument: parse-time ``default=Path(".")``; post-parse
  ``args.repo_root.resolve()`` (matches PCR-1 ``parallel_conflict_resolver:950``
  + ``L953``).
- JSON output keys ``{"action": "<detect|classify>", ...}`` on stdout for
  success; ``{"action": "<verb>", "error": "<message>"}`` on stderr for errors.
- Exit codes: 0 success, 1 runtime error (UNKNOWN classification on ``--classify``
  / git failure / parse error), 2 malformed CLI args.

4-state taxonomy per ADR-070 § 4-state worktree taxonomy:

- ``IN_PROGRESS``: worktree milestone.md ``stage:`` != ``reflect``; slice still
  being built.
- ``BUILT_BUT_NOT_MERGED``: milestone.md ``stage:`` == ``reflect`` AND worktree
  HEAD is NOT an ancestor of <default>'s tip.
- ``MERGED``: worktree HEAD IS an ancestor of <default>'s tip (transient under
  --merge happy path; can persist after --push + /sync-after-pr or --merge
  worktree-remove failure).
- ``UNKNOWN``: fail-closed default on any parse failure (8 enumerated sub-reasons
  per ``_UNKNOWN_REASONS``).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from tools import _stdout
from tools.branch_workflow_audit import _resolve_default_branch

__all__ = [
    "WorktreeState",
    "WorktreeInfo",
    "WorktreeStateClassification",
    "detect_active_worktrees",
    "classify_worktree_state",
    "main",
]


# Canonical BRANCH-2 slice-branch shape (mirrors tools/branch_workflow_audit.py
# `_SLICE_BRANCH_RE` at L81). Branches NOT matching this shape (e.g.
# `slice/077` with no name suffix, or non-slice/* branches) are filtered out
# of `detect_active_worktrees` output.
_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")


# UNKNOWN-reason enumeration per design.md § Fail-closed paths (Classification-side).
# Each value is also the short-token used in `WorktreeStateClassification.reason`
# and in the Drift & flags WARN text per ADR-070.
_UNKNOWN_REASONS = (
    "fresh-worktree-no-milestone",      # branch exists, milestone.md absent (BRANCH-2 pre-scaffold)
    "milestone-missing-in-active-and-archive",  # neither active nor archive milestone present
    "milestone-frontmatter-malformed",  # YAML frontmatter unparseable / no stage: field
    "detached-head",                    # mid-rebase or manual checkout, HEAD detached
    "dirty-worktree",                   # `git status --porcelain` non-empty
    "merge-base-error",                 # `git merge-base --is-ancestor` returned unexpected exit
    "head-unresolvable",                # `git rev-parse HEAD` failed
    "slice-folder-name-drift",          # branch `slice/NNN-foo` but folder `slice-NNN-bar`
)


class WorktreeState(Enum):
    """4-state classification of a BRANCH-2 slice worktree per ADR-070."""

    IN_PROGRESS = "IN_PROGRESS"
    BUILT_BUT_NOT_MERGED = "BUILT_BUT_NOT_MERGED"
    MERGED = "MERGED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class WorktreeInfo:
    """A non-main BRANCH-2 slice worktree registered with the repo.

    `path`: absolute path of the worktree on disk (forward-slash normalized).
    `branch`: branch name (e.g. `slice/077-enhance-pulse-with-worktree-awareness`).
    `head_sha`: full 40-char SHA of the worktree's HEAD commit, or empty string
        if the SHA could not be resolved (rare — would yield UNKNOWN/head-unresolvable).
    `slice_num`: the 3-digit slice number extracted from the branch name (e.g.
        `"077"`); empty if branch doesn't match `_SLICE_BRANCH_RE`.
    `slice_name`: the name suffix extracted from the branch (e.g.
        `"enhance-pulse-with-worktree-awareness"`).
    `milestone_path`: absolute Path to the resolved milestone.md (active path
        `architecture/slices/slice-NNN-<name>/milestone.md` OR archived path
        `architecture/slices/archive/slice-NNN-<name>/milestone.md`); None if
        neither resolves.
    """

    path: str
    branch: str
    head_sha: str
    slice_num: str
    slice_name: str
    milestone_path: Path | None


@dataclass(frozen=True)
class WorktreeStateClassification:
    """Result of classifying one WorktreeInfo against the default branch.

    `state`: one of the 4 `WorktreeState` enum values.
    `reason`: short-token rationale; for UNKNOWN states this is one of
        `_UNKNOWN_REASONS`. For IN_PROGRESS / BUILT_BUT_NOT_MERGED / MERGED
        this is a human-readable summary (e.g.
        `"milestone stage=reflect; HEAD not ancestor of master"`).
    `milestone_stage`: the parsed `stage:` field from milestone.md (e.g.
        `"reflect"`); empty if milestone.md missing or unparseable.
    """

    state: WorktreeState
    reason: str
    milestone_stage: str = ""


def detect_active_worktrees(repo_root: Path) -> list[WorktreeInfo]:
    """Detect non-main BRANCH-2 slice worktrees registered with the repo.

    Runs ``git worktree list --porcelain`` from `repo_root` and parses the
    output (the main worktree is listed first per git-worktree docs ordering
    invariant; subsequent worktrees follow). Returns a list of WorktreeInfo
    for each non-main worktree whose branch matches `_SLICE_BRANCH_RE`.

    Filters applied (return empty list on filtering only; never raises):

    - Non-`slice/*` branches: silently filtered out.
    - `slice/<NNN>` without `-<name>` suffix: filtered out (caller can detect
      via WARN if they run the audit at higher granularity).
    - Prunable worktrees (`prunable` line in porcelain output): filtered out.
    - Worktrees whose on-disk path doesn't exist: filtered out.

    Phase C implementation. Returns [] until then.
    """
    raise NotImplementedError("Phase C — see design.md § What's reused (worktree-list parsing pattern)")


def classify_worktree_state(
    worktree: WorktreeInfo,
    default_branch: str,
    repo_root: Path,
) -> WorktreeStateClassification:
    """Classify a worktree's HEAD-vs-default state into one of 4 WorktreeState values.

    Reads ``worktree.milestone_path`` for the milestone.md `stage:` field,
    then invokes ``git merge-base --is-ancestor <head> <default>`` from
    `repo_root` to determine ancestry. Fail-closed: returns
    ``WorktreeStateClassification(state=WorktreeState.UNKNOWN, reason=<one of
    _UNKNOWN_REASONS>)`` on ANY parse failure — never silent-defaults to
    MERGED or BUILT_BUT_NOT_MERGED.

    Phase C implementation. Returns UNKNOWN(reason=head-unresolvable) until then.
    """
    raise NotImplementedError("Phase C — see design.md § Override-precedence ordering")


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the CLI argparser for `python -m tools.pulse_worktree_resolver`.

    Cross-spec parity with PCR-1 per design.md § Cross-spec parity:
    - mutually-exclusive group ``required=True`` containing ``--detect`` +
      ``--classify``.
    - ``--repo-root`` parse-time default ``Path(".")``; post-parse
      ``args.repo_root.resolve()`` happens at top of `main()` body.
    - ``--json`` boolean flag.
    """
    parser = argparse.ArgumentParser(
        prog="python -m tools.pulse_worktree_resolver",
        description=(
            "Pulse Worktree Resolver (ADR-070) — detect BRANCH-2 slice "
            "worktrees and classify worktree state. Read-only."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--detect",
        action="store_true",
        help="Detect non-main BRANCH-2 slice worktrees; emit list of WorktreeInfo.",
    )
    mode.add_argument(
        "--classify",
        metavar="slice-NNN",
        help=(
            "Classify the named slice's worktree state (e.g. "
            "--classify slice-077). Slice arg format is the slice folder name."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output (default: human-readable text).",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repo root (default: cwd). Resolved post-parse.",
    )
    return parser


def _worktree_info_to_dict(info: WorktreeInfo) -> dict[str, Any]:
    """Serialize WorktreeInfo for JSON output."""
    return {
        "path": info.path,
        "branch": info.branch,
        "head_sha": info.head_sha,
        "slice_num": info.slice_num,
        "slice_name": info.slice_name,
        "milestone_path": str(info.milestone_path) if info.milestone_path else None,
    }


def _classification_to_dict(cls: WorktreeStateClassification) -> dict[str, Any]:
    """Serialize WorktreeStateClassification for JSON output."""
    return {
        "state": cls.state.value,
        "reason": cls.reason,
        "milestone_stage": cls.milestone_stage,
    }


def _emit_error(action: str, message: str) -> None:
    """Emit error to stderr in canonical PCR-1 shape `{action, error}`."""
    sys.stderr.write(json.dumps({"action": action, "error": message}) + "\n")


def _run_detect(repo_root: Path, json_mode: bool) -> int:
    """Handle `--detect` subcommand."""
    try:
        worktrees = detect_active_worktrees(repo_root)
    except NotImplementedError as e:
        _emit_error("detect", str(e))
        return 1
    if json_mode:
        sys.stdout.write(
            json.dumps(
                {"action": "detect", "worktrees": [_worktree_info_to_dict(w) for w in worktrees]}
            )
            + "\n"
        )
    else:
        sys.stdout.write(f"Detected {len(worktrees)} slice worktree(s).\n")
        for w in worktrees:
            sys.stdout.write(f"  {w.branch} @ {w.path} (HEAD {w.head_sha[:8]})\n")
    return 0


def _run_classify(slice_arg: str, repo_root: Path, json_mode: bool) -> int:
    """Handle `--classify slice-NNN` subcommand."""
    default_branch = _resolve_default_branch(repo_root)
    if default_branch is None:
        _emit_error(
            "classify",
            "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved",
        )
        return 1
    try:
        worktrees = detect_active_worktrees(repo_root)
    except NotImplementedError as e:
        _emit_error("classify", str(e))
        return 1
    matching = [w for w in worktrees if f"slice-{w.slice_num}-{w.slice_name}" == slice_arg]
    if not matching:
        _emit_error("classify", f"no worktree found for {slice_arg!r}")
        return 1
    try:
        cls = classify_worktree_state(matching[0], default_branch, repo_root)
    except NotImplementedError as e:
        _emit_error("classify", str(e))
        return 1
    if json_mode:
        sys.stdout.write(
            json.dumps(
                {
                    "action": "classify",
                    "slice": slice_arg,
                    "classification": _classification_to_dict(cls),
                }
            )
            + "\n"
        )
    else:
        sys.stdout.write(f"{slice_arg}: {cls.state.value} — {cls.reason}\n")
    return cls.state == WorktreeState.UNKNOWN  # UNKNOWN on --classify → exit 1


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code per PCR-1 contract: 0 ok, 1 runtime
    error, 2 malformed CLI args (argparse default)."""
    _stdout.reconfigure_stdout_utf8()
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()
    if args.detect:
        return _run_detect(repo_root, args.json)
    return _run_classify(args.classify, repo_root, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
