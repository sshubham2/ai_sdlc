"""Branch workflow audit (BRANCH-1).

Validates that the current git branch matches the active slice's
`slice/NNN-<slice-name>` pattern, with documented `BRANCH=skip`
escape-hatch via `build-log.md` Events conforming to a canonical regex.

Per BRANCH-1 (methodology-changelog.md v0.35.0). The rule's purpose:
- Slice work must live on a dedicated `slice/NNN-<slice-name>` branch
  (created at `/build-slice` `## Prerequisite check ### Branch state`
  sub-section); `/commit-slice --merge` integrates back via no-ff merge
  to the resolved default branch.
- This audit fires at `/build-slice` Step 6 pre-finish gate to catch any
  slice that bypassed the branch-create discipline OR ran on the wrong
  branch.

Default-branch resolution (per /critique M1 ACCEPTED-PENDING — replaces
hard-coded `master`/`main` for cross-project portability):
1. Primary: `git symbolic-ref refs/remotes/origin/HEAD` → strip
   `refs/remotes/origin/` prefix.
2. Fallback: `git config init.defaultBranch`.
3. STOP if neither resolves (exit 2 usage-error).

Escape-hatch: `build-log.md` Events line matching the canonical regex
`^- \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2} DEVIATION: BRANCH=skip\\b.+rationale: .+`
(HH:MM required + `rationale:` token required — narrows the empirically-
permissive parent DEVIATION convention; pinned in build-slice SKILL.md
Step 7c per slice-021 AC #2).

Usage:
    python -m tools.branch_workflow_audit <slice-folder>
    python -m tools.branch_workflow_audit --json <slice-folder>
    python -m tools.branch_workflow_audit --root <repo-root> <slice-folder>

Exit codes:
    0  clean (current branch matches active slice OR canonical escape-hatch present)
    1  violations (on default branch + no escape-hatch, or branch-mismatch, or stale-slice-branch)
    2  usage error (slice-folder missing, git unavailable, default-branch-unresolvable)

Operational notes (slice-071 / slice-069 m5 codification):

  ``--detach HEAD`` worktree-add sub-case: when verifying a state-transition
  in-place (slice-069 H4 N=4 verification pattern) and the slice branch
  is already checked out in another worktree, ``git worktree add <path>
  <branch>`` refuses with "branch already checked out". The canonical
  workaround per slice-069 build-log Phase H4 is ``git worktree add
  --detach <verify-path> HEAD`` (detached HEAD pointing at current
  commit), which sidesteps the branch-collision check. Codified here for
  future BRANCH-2 slices that need throwaway-worktree verification.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tools import _stdout
from tools._worktree_paths import (  # slice-099 / BRANCH-3: single source of truth (AC5)
    _SLICE_FOLDER_RE,
    canonical_worktree_path as _shared_canonical_worktree_path,
    slice_branch_name as _shared_slice_branch_name,
)


# Canonical regex for the `BRANCH=skip` escape-hatch line in build-log.md Events.
# Pinned in skills/build-slice/SKILL.md Step 7c per slice-021 AC #2.
_BRANCH_SKIP_LINE_RE = re.compile(
    r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+",
    re.MULTILINE,
)

# Canonical regex for the `WORKTREE=skip` escape-hatch line in build-log.md Events.
# Per BRANCH-2 (slice-066; ADR-063): mirrors `BRANCH=skip`'s shape with a new keyword.
# Pinned in skills/build-slice/SKILL.md Step 7c (same canonical-line-shape sub-section).
# Cross-spec parity (RPCD-1): the literal `WORKTREE=skip` appears across N=3 surfaces —
#   (1) skills/build-slice/SKILL.md, (2) skills/commit-slice/SKILL.md, (3) this regex.
_WORKTREE_SKIP_LINE_RE = re.compile(
    r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: WORKTREE=skip\b.+rationale: .+",
    re.MULTILINE,
)

# Slice-branch pattern: `slice/NNN-<slice-name>` (zero-padded 3-digit number).
_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")

# Slice-folder pattern `_SLICE_FOLDER_RE` is now imported from tools._worktree_paths
# (slice-099 / BRANCH-3 — moved verbatim; single source of truth, AC5). Re-exported
# above for this module's internal use + any external importer (slice-099 m3).

# Diagnostic-only split-slice folder shape (slice-043 / ADR-046 / R-6). NOT an
# accept regex — `_SLICE_FOLDER_RE` above stays the sole strict accept gate
# (numeric-only accept unchanged). This is consulted ONLY after a strict miss to
# emit a convention-naming, actionable `usage-error` for a letter-suffixed
# split-slice folder (e.g. `slice-030B-...`). Uppercase-only: the documented
# lineage label is uppercase `030A`/`030B`/`030C`, so a lowercase malformed name
# (`slice-030misc-x`) correctly falls through to the generic message rather than
# receiving the split-slice-specific guidance (per slice-043 /critique m1).
_SPLIT_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})([A-Z]+)-(.+)$")


@dataclass(frozen=True)
class BranchViolation:
    kind: str       # "on-default-branch" | "slice-branch-mismatch" |
                    # "escape-hatch-malformed" | "default-branch-unresolvable" |
                    # "stale-slice-branch" | "usage-error" |
                    # (slice-066 / BRANCH-2 worktree-mode additions:)
                    # "worktree-not-registered" | "worktree-cwd-mismatch" |
                    # "worktree-path-shape-violation" | "worktree-skip-malformed"
    severity: str   # "Important" (refuses) or "Warning" (for stale-slice-branch)
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    slice_folder: str = ""
    repo_root: str = ""
    expected_branch: str = ""
    actual_branch: str = ""
    resolved_default_branch: str = ""
    escape_hatch_used: bool = False
    escape_hatch_rationale: str | None = None
    # slice-071 m1 FIX (per slice-066 code-Critic m1): surface
    # WORKTREE=skip alongside the BRANCH=skip escape-hatch fields. Pre-
    # fix, `_check_worktree_skip_line` computed the rationale but
    # discarded it (`_` prefix); a `--json` consumer could not
    # distinguish "clean because BRANCH=skip" from "clean because
    # WORKTREE=skip". Now symmetric with the existing BRANCH=skip surface.
    worktree_skip_used: bool = False
    worktree_skip_rationale: str | None = None
    violations: list[BranchViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "BRANCH-1",
            "slice_folder": self.slice_folder,
            "repo_root": self.repo_root,
            "expected_branch": self.expected_branch,
            "actual_branch": self.actual_branch,
            "resolved_default_branch": self.resolved_default_branch,
            "escape_hatch_used": self.escape_hatch_used,
            "escape_hatch_rationale": self.escape_hatch_rationale,
            "worktree_skip_used": self.worktree_skip_used,
            "worktree_skip_rationale": self.worktree_skip_rationale,
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len([v for v in self.violations if v.severity == "Important"]),
                "warning_count": len([v for v in self.violations if v.severity == "Warning"]),
                "clean": all(v.severity != "Important" for v in self.violations),
            },
        }


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a git command in repo_root; return CompletedProcess (don't raise)."""
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _resolve_default_branch(repo_root: Path) -> str | None:
    """Resolve the repo's default branch.

    Primary: `git symbolic-ref refs/remotes/origin/HEAD` → strip prefix.
    Fallback: `git config init.defaultBranch`.
    Returns None if neither resolves.
    """
    # Primary: symbolic-ref of origin/HEAD.
    result = _run_git(repo_root, "symbolic-ref", "refs/remotes/origin/HEAD")
    if result.returncode == 0:
        ref = result.stdout.strip()
        if ref.startswith("refs/remotes/origin/"):
            return ref[len("refs/remotes/origin/"):]

    # Fallback: init.defaultBranch.
    result = _run_git(repo_root, "config", "init.defaultBranch")
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return None


def _current_branch(repo_root: Path) -> str | None:
    """Return current branch name or None if detached HEAD or error."""
    result = _run_git(repo_root, "branch", "--show-current")
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch if branch else None


def _slice_branch_name(slice_folder: Path) -> str:
    """Compute expected `slice/NNN-<slice-name>` branch from slice-folder name.

    Delegates to the shared single-source helper (slice-099 / BRANCH-3 /
    `tools._worktree_paths.slice_branch_name`); kept as a Path-taking wrapper
    for this module's internal call sites + any external importer. Behavior is
    byte-identical to the pre-slice-099 inline implementation.
    """
    return _shared_slice_branch_name(slice_folder.name)


def _check_escape_hatch(slice_folder: Path) -> tuple[bool, str | None, BranchViolation | None]:
    """Scan build-log.md Events for a canonical BRANCH=skip line.

    Returns (escape_hatch_used, rationale, malformed_violation).
    - escape_hatch_used=True if canonical regex matches.
    - rationale is the text after `rationale:` token, or None.
    - malformed_violation is a violation if a `BRANCH=skip` line is present
      but doesn't match the canonical shape (HH:MM + rationale: required).
    """
    build_log = slice_folder / "build-log.md"
    if not build_log.exists():
        return False, None, None

    content = build_log.read_text(encoding="utf-8")
    match = _BRANCH_SKIP_LINE_RE.search(content)
    if match:
        # Extract rationale text (everything after `rationale:`).
        line = match.group(0)
        rationale_idx = line.find("rationale:")
        rationale = line[rationale_idx + len("rationale:"):].strip() if rationale_idx >= 0 else None
        return True, rationale, None

    # No canonical match — but is there a malformed `BRANCH=skip` attempt?
    if "BRANCH=skip" in content:
        return False, None, BranchViolation(
            kind="escape-hatch-malformed",
            severity="Important",
            message=(
                "build-log.md Events contains `BRANCH=skip` but doesn't conform to "
                "canonical shape. Required: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` "
                "per skills/build-slice/SKILL.md Step 7c."
            ),
        )

    return False, None, None


def _check_stale_slice_branches(repo_root: Path, current_branch: str) -> list[BranchViolation]:
    """Detect stale `slice/*` branches (artefact of prior `--merge` conflict-recovery).

    Warning class (surfaces but doesn't refuse).
    """
    result = _run_git(repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads/slice/")
    if result.returncode != 0:
        return []
    branches = [b.strip() for b in result.stdout.splitlines() if b.strip()]
    stale = [b for b in branches if b != current_branch]
    if not stale:
        return []
    return [
        BranchViolation(
            kind="stale-slice-branch",
            severity="Warning",
            message=(
                f"Stale `slice/*` branches present (artefact of prior `--merge` "
                f"conflict-recovery): {stale}. Inspect with `git log <default>..<branch>` "
                f"and `git branch -d` each after verifying merged."
            ),
        )
    ]


def _is_repo_root_a_worktree(repo_root: Path) -> tuple[bool, Path | None]:
    """Detect worktree-mode by inspecting the `.git` marker.

    A linked worktree's `.git` is a FILE containing `gitdir: <main-repo>/.git/worktrees/<name>`;
    the main tree's `.git` is a DIRECTORY. Per BRANCH-2 (slice-066; ADR-063 §Decision).

    Returns:
        (in_worktree, main_repo_root):
        - (True, <main-repo>) when repo_root is a worktree pointing at <main-repo>.
        - (False, None) otherwise (main tree, no .git, malformed pointer, OR
          shallow-gitdir-walk-off — slice-071 M1 FIX per slice-066 code-Critic
          M1: gitdir < 4 parts triggers an unguarded `Path.parent.parent.parent`
          walk off the filesystem into unrelated ancestors; sanity-check via
          `.git`-existence on the resolved main repo closes this surface).
    """
    git_marker = repo_root / ".git"
    if not git_marker.exists():
        return (False, None)
    if git_marker.is_dir():
        return (False, None)  # Main tree — `.git` is a directory.
    try:
        content = git_marker.read_text(encoding="utf-8").strip()
    except OSError:
        return (False, None)
    if not content.startswith("gitdir:"):
        return (False, None)
    gitdir_str = content.split(":", 1)[1].strip()
    gitdir = Path(gitdir_str)
    if not gitdir.is_absolute():
        # Worktrees can have relative gitdir paths; resolve against repo_root.
        gitdir = (repo_root / gitdir).resolve()
    # gitdir points to <main-repo>/.git/worktrees/<name>. Walk up: name → worktrees → .git → main.
    if not gitdir.exists():
        return (False, None)
    # slice-071 M1 FIX (slice-066 code-Critic M1): guard against shallow
    # gitdir paths that would walk past the intended worktrees-record-root
    # into unrelated directories. `Path.parent` on a root path returns the
    # path itself (no exception); the try/except below is structurally
    # unreachable without this guard.
    if len(gitdir.parts) < 4:
        return (False, None)
    try:
        main_repo = gitdir.parent.parent.parent
    except (IndexError, AttributeError):
        return (False, None)
    # slice-071 M1 FIX (continued): even with depth ≥ 4, gitdir might
    # resolve to a path whose 3-parent walk lands somewhere that ISN'T a
    # git repo (corrupted .git pointer, attacker-crafted file, unusual
    # setup). Sanity-check via .git existence on the resolved main repo.
    if not (main_repo / ".git").exists():
        return (False, None)
    return (True, main_repo)


def _resolve_expected_worktree_path(slice_folder: Path, main_repo_root: Path) -> Path:
    """Canonical sibling-dir convention: `<main-parent>/<main-name>-wt/<slice-folder-name>`.

    Delegates to the shared single-source helper (slice-099 / BRANCH-3 /
    `tools._worktree_paths.canonical_worktree_path`). Per BRANCH-2 (ADR-063
    §Decision worktree path convention), unchanged by BRANCH-3.
    """
    return _shared_canonical_worktree_path(slice_folder.name, main_repo_root)


def _paths_equivalent(a: Path, b: Path) -> bool:
    """Compare two paths tolerating Windows case-insensitivity + symlink/junction targets.

    Per slice-066 /critique B2 ACCEPTED-FIXED + WebSearch evidence (microsoft/vscode#101244):
    `git worktree list --porcelain` records paths as-supplied; `Path.resolve()` normalizes case
    + resolves symlinks. Use `samefile()` when both paths exist; fall back to
    `os.path.normcase(os.path.realpath(...))` string equality when one side doesn't exist.

    slice-071 m3 FIX (per slice-066 code-Critic m3): `import os` hoisted to
    module-level imports block; pre-fix the import lived inline at function
    entry (per-call lookup overhead + PEP 8 violation).
    """
    try:
        a_resolved = a.resolve(strict=False)
        b_resolved = b.resolve(strict=False)
    except (OSError, RuntimeError):
        return False
    # Prefer samefile() when both paths exist on disk (handles junctions/symlinks).
    if a_resolved.exists() and b_resolved.exists():
        try:
            return a_resolved.samefile(b_resolved)
        except (OSError, FileNotFoundError):
            pass
    # Fallback: case-insensitive realpath comparison (Windows-tolerant).
    a_norm = os.path.normcase(os.path.realpath(str(a_resolved)))
    b_norm = os.path.normcase(os.path.realpath(str(b_resolved)))
    return a_norm == b_norm


def _worktree_registered(main_repo_root: Path, wt_path: Path) -> bool:
    """Check whether `git worktree list --porcelain` shows `wt_path` as a registered worktree.

    Per BRANCH-2 (slice-066; ADR-063 §Decision worktree-registered helper). The porcelain output
    format is one record per worktree, each starting with `worktree <path>` line followed by
    `HEAD <sha>`, `branch refs/heads/<name>` (or `detached`), and a blank line.
    """
    result = _run_git(main_repo_root, "worktree", "list", "--porcelain")
    if result.returncode != 0:
        return False
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            registered_path = Path(line[len("worktree "):])
            if _paths_equivalent(registered_path, wt_path):
                return True
    return False


def _slice_branch_in_worktree(main_repo_root: Path, slice_branch: str) -> Path | None:
    """Locate which worktree (if any) has `slice_branch` checked out.

    Returns the worktree path (resolved) if found, else None. Used to detect the
    "Claude forgot to `cd` into the worktree" canonical case — slice branch checked out
    in some worktree but `Path.cwd()` is the main tree.

    Per BRANCH-2 (slice-066; ADR-063 §Decision Audit invocation call-shapes shape 2).
    """
    result = _run_git(main_repo_root, "worktree", "list", "--porcelain")
    if result.returncode != 0:
        return None
    current_wt: Path | None = None
    target_ref = f"branch refs/heads/{slice_branch}"
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            current_wt = Path(line[len("worktree "):])
        elif line == target_ref and current_wt is not None:
            return current_wt
    return None


def _check_worktree_skip_line(slice_folder: Path) -> tuple[bool, str | None, BranchViolation | None]:
    """Scan build-log.md Events for a canonical `WORKTREE=skip` line (mirror of `_check_escape_hatch`).

    Returns (skip_used, rationale, malformed_violation). Per BRANCH-2 (slice-066; ADR-063 §Decision).
    """
    build_log = slice_folder / "build-log.md"
    if not build_log.exists():
        return False, None, None
    content = build_log.read_text(encoding="utf-8")
    match = _WORKTREE_SKIP_LINE_RE.search(content)
    if match:
        line = match.group(0)
        rationale_idx = line.find("rationale:")
        rationale = line[rationale_idx + len("rationale:"):].strip() if rationale_idx >= 0 else None
        return True, rationale, None
    # No canonical match — but is a malformed `WORKTREE=skip` attempt present?
    if "WORKTREE=skip" in content:
        return False, None, BranchViolation(
            kind="worktree-skip-malformed",
            severity="Important",
            message=(
                "build-log.md Events contains `WORKTREE=skip` but doesn't conform to "
                "canonical shape. Required: `<YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>` "
                "per skills/build-slice/SKILL.md Step 7c (BRANCH-2; ADR-063)."
            ),
        )
    return False, None, None


def audit(slice_folder: Path, repo_root: Path | None = None) -> AuditResult:
    """Run the BRANCH-1 audit against a slice folder.

    Args:
        slice_folder: Path to active slice folder
            (e.g., architecture/slices/slice-021-add-feature-branch-workflow-...).
        repo_root: Path to the git repository root. Defaults to slice_folder's
            ancestor with a `.git` directory.

    Returns:
        AuditResult with violations + diagnostic fields.
    """
    slice_folder = Path(slice_folder).resolve()
    if not slice_folder.exists():
        return AuditResult(
            slice_folder=str(slice_folder),
            violations=[
                BranchViolation(
                    kind="usage-error",
                    severity="Important",
                    message=f"slice folder not found: {slice_folder}",
                )
            ],
        )

    # Resolve repo_root if not provided.
    if repo_root is None:
        for parent in [slice_folder] + list(slice_folder.parents):
            if (parent / ".git").exists():
                repo_root = parent
                break
        else:
            return AuditResult(
                slice_folder=str(slice_folder),
                violations=[
                    BranchViolation(
                        kind="usage-error",
                        severity="Important",
                        message=f"no .git directory found above {slice_folder}",
                    )
                ],
            )

    repo_root = Path(repo_root).resolve()
    result = AuditResult(
        slice_folder=str(slice_folder),
        repo_root=str(repo_root),
    )

    # Compute expected slice branch from folder name.
    expected = _slice_branch_name(slice_folder)
    if not expected:
        # Strict `_SLICE_FOLDER_RE` miss. If the name matches the letter-suffixed
        # split-slice shape, emit a convention-naming, actionable message instead
        # of the generic one (slice-043 / ADR-046 / R-6); otherwise the generic
        # message is preserved verbatim (kind + exit-code 2 unchanged either way).
        split_match = _SPLIT_SLICE_FOLDER_RE.match(slice_folder.name)
        if split_match:
            digits, letters, rest = split_match.groups()
            message = (
                f"split-slice follow-up folder name not accepted: {slice_folder.name!r}. "
                f"Per ADR-046 / BRANCH-1, split-slice follow-up folders are numeric "
                f"`slice-NNN-`; the `NNNx` letter (here `{digits}{letters}`) is a "
                f"prose lineage label only, never the folder/branch name. Rename to "
                f"the next free numeric slice number (e.g. `slice-<NNN>-{rest}` with a "
                f"fresh number = max(existing)+1) and keep `{digits}{letters}` as the "
                f"split-lineage label in prose (milestone identity-note + reflection "
                f"lineage + risk-register sub-entry cross-refs)."
            )
        else:
            message = (
                f"slice folder name does not match `slice-NNN-<name>` pattern: "
                f"{slice_folder.name}"
            )
        result.violations.append(
            BranchViolation(
                kind="usage-error",
                severity="Important",
                message=message,
            )
        )
        return result
    result.expected_branch = expected

    # Get current branch.
    current = _current_branch(repo_root)
    if current is None:
        result.violations.append(
            BranchViolation(
                kind="usage-error",
                severity="Important",
                message="cannot resolve current branch (detached HEAD or git error)",
            )
        )
        return result
    result.actual_branch = current

    # Resolve default branch.
    default = _resolve_default_branch(repo_root)
    if default is None:
        result.violations.append(
            BranchViolation(
                kind="default-branch-unresolvable",
                severity="Important",
                message=(
                    "cannot resolve repo default branch via "
                    "`git symbolic-ref refs/remotes/origin/HEAD` or "
                    "`git config init.defaultBranch`. Set `git config init.defaultBranch <name>` "
                    "or add `origin` remote with HEAD reference, then retry."
                ),
            )
        )
        return result
    result.resolved_default_branch = default

    # Check for stale slice branches (warning class — doesn't refuse).
    result.violations.extend(_check_stale_slice_branches(repo_root, current))

    # Check escape-hatch (BRANCH=skip).
    escape_hatch, rationale, malformed = _check_escape_hatch(slice_folder)
    if malformed:
        result.violations.append(malformed)
        return result
    result.escape_hatch_used = escape_hatch
    result.escape_hatch_rationale = rationale

    # BRANCH-2 (slice-066; ADR-063): worktree-mode awareness.
    # Check parallel WORKTREE=skip escape-hatch (mirror of BRANCH=skip).
    # slice-071 m1 FIX (per slice-066 code-Critic m1): rationale is now
    # surfaced via AuditResult (consumer-visible) rather than discarded.
    worktree_skip_used, worktree_skip_rationale, worktree_skip_malformed = _check_worktree_skip_line(slice_folder)
    result.worktree_skip_used = worktree_skip_used
    result.worktree_skip_rationale = worktree_skip_rationale
    if worktree_skip_malformed is not None:
        result.violations.append(worktree_skip_malformed)
        return result

    # Detect worktree mode via .git marker shape.
    in_worktree, main_repo_for_wt = _is_repo_root_a_worktree(repo_root)
    if in_worktree and main_repo_for_wt is not None:
        # Worktree-mode validation: verify registration + canonical path shape.
        if not _worktree_registered(main_repo_for_wt, repo_root):
            result.violations.append(
                BranchViolation(
                    kind="worktree-not-registered",
                    severity="Important",
                    message=(
                        f"Worktree at `{repo_root}` is not registered via `git worktree list`. "
                        f"The worktree's `.git` file may be stale or the worktree may have been "
                        f"manually deleted. Recover with `git worktree repair` (if `{repo_root}` "
                        f"exists) or `git worktree add {repo_root} -b {expected} {default}` (if "
                        f"deleted). Per BRANCH-2 / ADR-063."
                    ),
                )
            )
            return result
        expected_wt = _resolve_expected_worktree_path(slice_folder, main_repo_for_wt)
        if not _paths_equivalent(repo_root, expected_wt):
            result.violations.append(
                BranchViolation(
                    kind="worktree-path-shape-violation",
                    severity="Important",
                    message=(
                        f"Worktree is registered at `{repo_root}` but the canonical convention "
                        f"is `{expected_wt}` (`<main-parent>/<main-name>-wt/slice-NNN-<name>` per "
                        f"ADR-063 §Decision). Move the worktree (`git worktree move {repo_root} "
                        f"{expected_wt}`) or document `WORKTREE=skip — rationale: <text>` in "
                        f"build-log.md Events."
                    ),
                )
            )
            # Continue to branch checks — path shape violation is severe but the branch must
            # still match the expected slice branch.
    elif not worktree_skip_used:
        # Main-tree mode: detect "Claude forgot to `cd` into the worktree".
        # If the slice branch is checked out in a worktree elsewhere AND cwd is main tree,
        # emit worktree-cwd-mismatch (the canonical Audit-invocation call-shape 2 per ADR-063).
        wt_path = _slice_branch_in_worktree(repo_root, expected)
        if wt_path is not None and not _paths_equivalent(wt_path, repo_root):
            result.violations.append(
                BranchViolation(
                    kind="worktree-cwd-mismatch",
                    severity="Important",
                    message=(
                        f"Slice branch `{expected}` is checked out in worktree `{wt_path}` but "
                        f"your cwd is the main tree `{repo_root}`. Did you forget to `cd "
                        f"{wt_path}`? Run `cd {wt_path}` and retry; or, if you intend to skip "
                        f"the worktree discipline for this slice, document `WORKTREE=skip — "
                        f"rationale: <text>` in build-log.md Events. Per BRANCH-2 / ADR-063 "
                        f"§Decision Audit-invocation call-shapes shape 2."
                    ),
                )
            )
            return result

    # Apply branch-state logic. BRANCH=skip OR WORKTREE=skip accepts the discipline-skip case.
    combined_skip = escape_hatch or worktree_skip_used
    if current == default:
        if not combined_skip:
            result.violations.append(
                BranchViolation(
                    kind="on-default-branch",
                    severity="Important",
                    message=(
                        f"active-slice work occurred on default branch '{default}' with no canonical "
                        f"`BRANCH=skip — rationale: <text>` or `WORKTREE=skip — rationale: <text>` "
                        f"escape-hatch in build-log.md Events. Expected branch: '{expected}'. "
                        f"Either switch to '{expected}' OR document escape-hatch per "
                        f"skills/build-slice/SKILL.md Step 7c canonical shape."
                    ),
                )
            )
        # If escape_hatch or worktree_skip present, acceptance via canonical escape-hatch.
    elif current.startswith("slice/"):
        if current != expected:
            result.violations.append(
                BranchViolation(
                    kind="slice-branch-mismatch",
                    severity="Important",
                    message=(
                        f"current branch '{current}' does not match active slice's expected branch "
                        f"'{expected}'. Did you forget to switch back after a prior slice's `--merge`?"
                    ),
                )
            )
        # else: clean (matching slice branch).
    else:
        # On some other branch entirely (not default, not slice/*).
        result.violations.append(
            BranchViolation(
                kind="slice-branch-mismatch",
                severity="Important",
                message=(
                    f"current branch '{current}' is neither the default branch '{default}' "
                    f"nor the active slice's expected branch '{expected}'. "
                    f"Switch to '{expected}' or document escape-hatch."
                ),
            )
        )

    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(description="BRANCH-1 audit: branch-per-slice workflow validation.")
    parser.add_argument("slice_folder", type=Path, help="Path to active slice folder.")
    parser.add_argument("--root", type=Path, default=None, help="Repo root (default: ancestor with .git).")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(slice_folder=args.slice_folder, repo_root=args.root)
    except Exception as e:
        print(f"branch_workflow_audit: error: {e}", file=sys.stderr)
        return 2

    important = [v for v in result.violations if v.severity == "Important"]
    warnings = [v for v in result.violations if v.severity == "Warning"]

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if important:
            for v in important:
                print(f"[{v.severity}] {v.kind}: {v.message}")
        if warnings:
            for v in warnings:
                print(f"[{v.severity}] {v.kind}: {v.message}")
        if not result.violations:
            print(f"Branch workflow audit: clean. On branch '{result.actual_branch}' (matches expected '{result.expected_branch}').")
        elif not important:
            print(f"Branch workflow audit: clean (with {len(warnings)} warning(s)). On branch '{result.actual_branch}'.")

    # Exit codes: 0 clean, 1 important violations, 2 usage error.
    usage_kinds = {"usage-error", "default-branch-unresolvable"}
    if any(v.kind in usage_kinds for v in important):
        return 2
    if important:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
