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
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Mapping

from tools import _stdout
from tools.branch_workflow_audit import _resolve_default_branch

__all__ = [
    "WorktreeState",
    "WorktreeInfo",
    "WorktreeStateClassification",
    "detect_active_worktrees",
    "classify_worktree_state",
    "should_suppress_vault_forward_population_flag",
    "augment_pulse_state_dict",
    "main",
]


# Canonical BRANCH-2 slice-branch shape (mirrors tools/branch_workflow_audit.py
# `_SLICE_BRANCH_RE` at L81). Branches NOT matching this shape (e.g.
# `slice/077` with no name suffix, or non-slice/* branches) are filtered out
# of `detect_active_worktrees` output.
_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")


# UNKNOWN-reason enumeration per design.md § Fail-closed paths (Classification-side).
_UNKNOWN_REASONS = (
    "fresh-worktree-no-milestone",
    "milestone-missing-in-active-and-archive",
    "milestone-frontmatter-malformed",
    "detached-head",
    "dirty-worktree",
    "merge-base-error",
    "head-unresolvable",
    "slice-folder-name-drift",
)


# Per-UNKNOWN-reason WARN template strings (Fix K, slice-077 m5 — MAP-ONLY shape per
# /critique B1 + M1 ACCEPTED-FIXED). Closes the slice-077 design.md L181-191 / ADR-070
# contractual promise of a WARN string per UNKNOWN sub-reason. Pure data exposed at
# module scope: the `skills/pulse/SKILL.md` Drift & flags consumer reads this constant and
# performs `_UNKNOWN_REASON_WARN_TEMPLATES.get(reason, <fallback>)` at Haiku-side
# prose-interpretation time. NO new public helper, NO new JSON state-dict field, NO change
# to CLI text-mode emission (MEPD-1 EXCLUDE preserved). Keys are byte-equal to
# `_UNKNOWN_REASONS`; the `{slice}` placeholder is filled by the consumer.
_UNKNOWN_REASON_WARN_TEMPLATES: Mapping[str, str] = {
    "fresh-worktree-no-milestone": (
        "WARN: worktree {slice} has no milestone.md yet (fresh scaffold) — state UNKNOWN; "
        "run /slice in the worktree or verify the slice folder."
    ),
    "milestone-missing-in-active-and-archive": (
        "WARN: worktree {slice} milestone.md is absent from both the active and archive "
        "paths — state UNKNOWN; verify the slice folder name."
    ),
    "milestone-frontmatter-malformed": (
        "WARN: worktree {slice} milestone.md frontmatter is malformed (no parseable "
        "stage:) — state UNKNOWN; repair the YAML frontmatter."
    ),
    "detached-head": (
        "WARN: worktree {slice} is on a detached HEAD — state UNKNOWN; check out the "
        "slice/NNN-<name> branch."
    ),
    "dirty-worktree": (
        "WARN: worktree {slice} has a dirty working tree — state UNKNOWN; commit or "
        "inspect before relying on classification."
    ),
    "merge-base-error": (
        "WARN: worktree {slice} `git merge-base --is-ancestor` errored — state UNKNOWN; "
        "HEAD-vs-default ancestry is indeterminate."
    ),
    "head-unresolvable": (
        "WARN: worktree {slice} HEAD could not be resolved — state UNKNOWN; the worktree "
        "may be empty or corrupt."
    ),
    "slice-folder-name-drift": (
        "WARN: worktree {slice} branch name and slice folder name disagree — state "
        "UNKNOWN; reconcile the folder/branch naming."
    ),
}


class WorktreeState(Enum):
    """4-state classification of a BRANCH-2 slice worktree per ADR-070."""

    IN_PROGRESS = "IN_PROGRESS"
    BUILT_BUT_NOT_MERGED = "BUILT_BUT_NOT_MERGED"
    MERGED = "MERGED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class WorktreeInfo:
    path: str
    branch: str
    head_sha: str
    slice_num: str
    slice_name: str
    milestone_path: Path | None


@dataclass(frozen=True)
class WorktreeStateClassification:
    state: WorktreeState
    reason: str
    milestone_stage: str = ""


# ----------------------------- private helpers -----------------------------


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run git with -C <repo_root>, capturing both stdout/stderr as text."""
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _parse_worktree_porcelain(output: str) -> list[dict[str, str]]:
    """Parse `git worktree list --porcelain` output into block dicts.

    Each block represents one registered worktree. The main worktree is the
    first block per git-worktree docs ordering invariant. Block keys include
    `worktree` (path), `HEAD` (40-char sha), `branch` (refs/heads/...), or
    sentinel-flags like `bare`, `detached`, `prunable`.

    Returns a list of dicts, one per block.
    """
    blocks: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.rstrip("\r")
        if not line:
            if current:
                blocks.append(current)
                current = {}
            continue
        # Lines can be 'key value' or just 'key' (e.g. 'bare', 'detached', 'prunable').
        if " " in line:
            key, _, value = line.partition(" ")
            current[key] = value
        else:
            current[line] = ""
    if current:
        blocks.append(current)
    return blocks


def _resolve_milestone_path(scan_root: Path, slice_num: str, slice_name: str) -> Path | None:
    """Resolve milestone.md path for a slice — active OR archived. Returns
    None if neither exists.

    Active: <scan_root>/architecture/slices/slice-NNN-<name>/milestone.md
    Archive: <scan_root>/architecture/slices/archive/slice-NNN-<name>/milestone.md

    For BRANCH-2 worktrees, `scan_root` MUST be the WORKTREE's path (not the
    main repo's path) — the milestone.md is checked into the slice branch and
    physically lives in the worktree's filesystem, not the main tree's. This
    is precisely the witnessed-gap scenario slice-077 closes (R-22): a freshly
    scaffolded slice's milestone is invisible to /pulse if it reads only the
    main tree.
    """
    folder = f"slice-{slice_num}-{slice_name}"
    active = scan_root / "architecture" / "slices" / folder / "milestone.md"
    if active.is_file():
        return active
    archive = scan_root / "architecture" / "slices" / "archive" / folder / "milestone.md"
    if archive.is_file():
        return archive
    return None


def _parse_milestone_stage(milestone_path: Path) -> str | None:
    """Parse `stage:` value from milestone.md YAML frontmatter. Returns None
    on any parse failure (missing file, no frontmatter, no stage field)."""
    try:
        text = milestone_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    # Fix M (slice-077 m8): strip a leading UTF-8 BOM. PowerShell's default redirection /
    # Set-Content writes a BOM; `read_text(encoding="utf-8")` (not utf-8-sig) leaves a
    # leading U+FEFF that would defeat the `startswith("---")` frontmatter check.
    text = text.removeprefix("﻿")
    if not text.startswith("---"):
        return None
    # Find closing frontmatter delimiter
    rest = text[3:]
    end_idx = rest.find("\n---")
    if end_idx == -1:
        return None
    frontmatter = rest[:end_idx]
    for line in frontmatter.splitlines():
        stripped = line.strip()
        # Fix N (slice-077 m9): exact-key match (partition on the FIRST colon, compare the
        # key) instead of `startswith("stage:")` — the prefix form also matched
        # hypothetical `stage_owner:` / `stage-history:` keys.
        key, sep, value = stripped.partition(":")
        if sep and key.strip() == "stage":
            return value.strip()
    return None


def _content_equal_modulo_eol(a: Path, b: Path) -> bool:
    """Compare two files content-equal modulo CRLF↔LF per ADR-033 / EOL-DRIFT-1.

    Returns False if either file is missing or unreadable.
    """
    try:
        a_bytes = a.read_bytes()
        b_bytes = b.read_bytes()
    except OSError:
        return False
    # Normalize CRLF and CR to LF on both sides
    a_norm = a_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    b_norm = b_bytes.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return a_norm == b_norm


# ----------------------------- library API -----------------------------


def detect_active_worktrees(repo_root: Path) -> list[WorktreeInfo]:
    """Detect non-main BRANCH-2 slice worktrees registered with the repo.

    Runs ``git worktree list --porcelain`` from `repo_root` and parses the
    output. Returns a list of WorktreeInfo for each non-main worktree whose
    branch matches `_SLICE_BRANCH_RE`.

    Filters applied (return empty list on filtering only; never raises on
    expected failure modes — only on truly-unexpected exceptions like missing
    git binary):

    - Main worktree (first block): always filtered out.
    - Branch missing `branch refs/heads/slice/NNN-<name>` shape: filtered out.
    - Non-`slice/*` branches: filtered out.
    - `slice/<NNN>` without `-<name>` suffix (regex non-match): filtered out.
    - Prunable worktrees: filtered out.
    - Worktrees whose on-disk path doesn't exist: filtered out.

    Returns empty list if git command fails or no slice worktrees registered.
    """
    result = _run_git(repo_root, "worktree", "list", "--porcelain")
    if result.returncode != 0:
        return []
    blocks = _parse_worktree_porcelain(result.stdout)
    # Fix L (slice-077 m6): bare-repo edge case. `git worktree list --porcelain` on a bare
    # repo emits a first block carrying a `bare` sentinel field; a bare repo has no
    # checked-out tree, so there is no active slice worktree to classify. Detect via
    # `"bare" in blocks[0]` (AND-only per /critique m2 ACCEPTED-FIXED — git guarantees
    # `worktree <path>` as the first line for non-bare, so widening to OR would add an
    # impossible-state branch). Return an empty tuple + WARN to stderr.
    if blocks and "bare" in blocks[0]:
        sys.stderr.write("WARN: bare repo detected; no active worktrees applicable\n")
        return []
    # First block is the main worktree — skip it.
    candidates = blocks[1:] if blocks else []
    out: list[WorktreeInfo] = []
    for block in candidates:
        # Filter prunable
        if "prunable" in block:
            continue
        # Filter bare / detached / no branch
        branch_ref = block.get("branch", "")
        if not branch_ref.startswith("refs/heads/"):
            continue
        branch = branch_ref[len("refs/heads/"):]
        m = _SLICE_BRANCH_RE.match(branch)
        if not m:
            continue
        slice_num, slice_name = m.group(1), m.group(2)
        wt_path_str = block.get("worktree", "")
        if not wt_path_str:
            continue
        wt_path = Path(wt_path_str)
        if not wt_path.exists():
            continue
        head_sha = block.get("HEAD", "")
        # Resolve milestone.md from the WORKTREE's filesystem, not the main
        # tree's — BRANCH-2 worktrees check milestone into the slice branch
        # so the file physically lives in the worktree.
        milestone_path = _resolve_milestone_path(wt_path, slice_num, slice_name)
        out.append(
            WorktreeInfo(
                path=str(wt_path).replace("\\", "/"),
                branch=branch,
                head_sha=head_sha,
                slice_num=slice_num,
                slice_name=slice_name,
                milestone_path=milestone_path,
            )
        )
    return out


def classify_worktree_state(
    worktree: WorktreeInfo,
    default_branch: str,
    repo_root: Path,
) -> WorktreeStateClassification:
    """Classify a worktree's HEAD-vs-default state into one of 4 WorktreeState values.

    Fail-closed: returns UNKNOWN with a specific reason on any parse failure;
    never silent-defaults to MERGED or BUILT_BUT_NOT_MERGED.
    """
    # 1. Resolve milestone.md
    if worktree.milestone_path is None:
        return WorktreeStateClassification(
            state=WorktreeState.UNKNOWN,
            reason="fresh-worktree-no-milestone",
        )
    if not worktree.milestone_path.is_file():
        return WorktreeStateClassification(
            state=WorktreeState.UNKNOWN,
            reason="milestone-missing-in-active-and-archive",
        )

    # 2. Parse milestone stage
    stage = _parse_milestone_stage(worktree.milestone_path)
    if stage is None:
        return WorktreeStateClassification(
            state=WorktreeState.UNKNOWN,
            reason="milestone-frontmatter-malformed",
        )

    # 3. Resolve HEAD sha (use the cached one if non-empty; otherwise rev-parse)
    head_sha = worktree.head_sha
    if not head_sha:
        rev_result = _run_git(Path(worktree.path), "rev-parse", "HEAD")
        if rev_result.returncode != 0:
            return WorktreeStateClassification(
                state=WorktreeState.UNKNOWN,
                reason="head-unresolvable",
                milestone_stage=stage,
            )
        head_sha = rev_result.stdout.strip()
        if not head_sha:
            return WorktreeStateClassification(
                state=WorktreeState.UNKNOWN,
                reason="head-unresolvable",
                milestone_stage=stage,
            )

    # 4. Stage-driven dispatch per ADR-070 § 4-state worktree taxonomy:
    #    - stage != "reflect" → IN_PROGRESS (regardless of ancestry; slice is mid-build).
    #    - stage == "reflect" + head IS ancestor of default → MERGED (transient).
    #    - stage == "reflect" + head NOT ancestor → BUILT_BUT_NOT_MERGED.
    # The IN_PROGRESS case does NOT consult ancestry — a pre-reflect slice's
    # ancestry state is irrelevant (it's still being built; the next-action
    # override recommends `cd <wt> && <stage-derived>`, not /commit-slice --merge).
    if stage != "reflect":
        return WorktreeStateClassification(
            state=WorktreeState.IN_PROGRESS,
            reason=f"milestone stage={stage}; pre-reflect",
            milestone_stage=stage,
        )

    # stage == "reflect": consult ancestry to disambiguate BUILT_BUT_NOT_MERGED vs MERGED
    ancestor_result = _run_git(
        repo_root, "merge-base", "--is-ancestor", head_sha, default_branch
    )
    # exit 0 → IS ancestor (MERGED); exit 1 → NOT ancestor; other → error
    if ancestor_result.returncode == 0:
        return WorktreeStateClassification(
            state=WorktreeState.MERGED,
            reason=f"HEAD {head_sha[:8]} reachable from {default_branch}",
            milestone_stage=stage,
        )
    if ancestor_result.returncode != 1:
        return WorktreeStateClassification(
            state=WorktreeState.UNKNOWN,
            reason="merge-base-error",
            milestone_stage=stage,
        )
    return WorktreeStateClassification(
        state=WorktreeState.BUILT_BUT_NOT_MERGED,
        reason=f"milestone stage=reflect; HEAD not ancestor of {default_branch}",
        milestone_stage=stage,
    )


def should_suppress_vault_forward_population_flag(
    detected: Iterable[tuple[WorktreeInfo, WorktreeStateClassification]],
    installed_home: Path,
) -> bool:
    """Predicate per slice-077 design.md L141-156 + ADR-070 L107-127.

    Suppress "vault forward-population" drift flag IFF:
    (a) at least one worktree.state == BUILT_BUT_NOT_MERGED
    (b) ALL 3 installed surfaces (methodology-changelog.md, ai-sdlc-VERSION,
        skills/pulse/SKILL.md) are content-equal-modulo-EOL to the worktree's
        copy (CRLF↔LF is NOT drift per ADR-033 / EOL-DRIFT-1).

    `installed_home` is the directory representing `~/.claude`-equivalent;
    tests pass a synthetic tmp_path location. Worktree paths are taken from
    the WorktreeInfo.path field.
    """
    detected_list = list(detected)
    bbnm = [
        (info, cls) for info, cls in detected_list if cls.state == WorktreeState.BUILT_BUT_NOT_MERGED
    ]
    if not bbnm:
        return False
    # Use the first BUILT_BUT_NOT_MERGED worktree for comparison
    info, _ = bbnm[0]
    wt_root = Path(info.path)
    surfaces = [
        (installed_home / "methodology-changelog.md", wt_root / "methodology-changelog.md"),
        (installed_home / "ai-sdlc-VERSION", wt_root / "VERSION"),
        (installed_home / "skills" / "pulse" / "SKILL.md", wt_root / "skills" / "pulse" / "SKILL.md"),
    ]
    for installed_path, worktree_path in surfaces:
        if not _content_equal_modulo_eol(installed_path, worktree_path):
            return False
    return True


def augment_pulse_state_dict(
    base_state_dict: dict[str, Any],
    detected_worktrees: list[WorktreeInfo],
    classifications: list[WorktreeStateClassification],
) -> dict[str, Any]:
    """Augment /pulse Step 2 state-dict with worktree fields per design.md L37.

    Adds three keys:
    - `worktrees`: list[WorktreeInfo]
    - `worktree_classifications`: list[WorktreeStateClassification]
    - `recommended_next_action_override`: str | None (the resolved override
      per the 3-level precedence table; None when no BUILT_BUT_NOT_MERGED or
      IN_PROGRESS worktree fires rule #1).

    Per design.md § Override-precedence ordering: the override resolution
    happens here in Step 2 deterministic main-thread computation; the
    Step 3 Haiku dispatch consumes the resolved value.
    """
    augmented = dict(base_state_dict)
    augmented["worktrees"] = list(detected_worktrees)
    augmented["worktree_classifications"] = list(classifications)
    # Resolve the override per rule #1
    override: str | None = None
    for info, cls in zip(detected_worktrees, classifications):
        if cls.state == WorktreeState.BUILT_BUT_NOT_MERGED:
            override = f"cd {info.path} && /commit-slice --merge"
            break
        if cls.state == WorktreeState.IN_PROGRESS:
            # IN_PROGRESS variant: defer the stage-derived next-action from the
            # worktree's milestone.md (cd + continue)
            override = f"cd {info.path} && continue per worktree milestone.md next-action"
            # Don't break — a BUILT_BUT_NOT_MERGED later in the list takes priority
    augmented["recommended_next_action_override"] = override
    return augmented


# ----------------------------- CLI -----------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
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
    return {
        "path": info.path,
        "branch": info.branch,
        "head_sha": info.head_sha,
        "slice_num": info.slice_num,
        "slice_name": info.slice_name,
        "milestone_path": str(info.milestone_path) if info.milestone_path else None,
    }


def _classification_to_dict(cls: WorktreeStateClassification) -> dict[str, Any]:
    return {
        "state": cls.state.value,
        "reason": cls.reason,
        "milestone_stage": cls.milestone_stage,
    }


def _emit_error(action: str, message: str) -> None:
    sys.stderr.write(json.dumps({"action": action, "error": message}) + "\n")


def _run_detect(repo_root: Path, json_mode: bool) -> int:
    worktrees = detect_active_worktrees(repo_root)
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
    default_branch = _resolve_default_branch(repo_root)
    if default_branch is None:
        _emit_error(
            "classify",
            "default-branch-unresolvable: neither origin/HEAD nor init.defaultBranch resolved",
        )
        return 1
    worktrees = detect_active_worktrees(repo_root)
    matching = [w for w in worktrees if f"slice-{w.slice_num}-{w.slice_name}" == slice_arg]
    if not matching:
        _emit_error("classify", f"no worktree found for {slice_arg!r}")
        return 1
    cls = classify_worktree_state(matching[0], default_branch, repo_root)
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
    return 1 if cls.state == WorktreeState.UNKNOWN else 0


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
