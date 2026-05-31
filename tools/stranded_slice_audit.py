"""Stranded-slice detector (slice-087 / ADR-079).

Read-only git-vs-vault CLASSIFIER. Enumerates every unmerged local
``slice/NNN-<name>`` branch and classifies each into a 4-class divergence model
(+ INDETERMINATE), halting ``/slice`` only on genuine divergence
(STRANDED-COMPLETE / ORPHANED / INDETERMINATE). A healthy in-flight parallel
slice (own worktree, mid-stage) classifies as IN-PROGRESS -> informational,
never halts -- the parallel-safety property under PSQ-1/PSQ-2/BRANCH-2 (the
reframe motivated by the slice-087 flag-all flaw the USER caught).

Reuses (NO re-implementation of porcelain/ancestry/claim parsing -- ADR-079 B1):
- ``tools.pulse_worktree_resolver.detect_active_worktrees`` + ``classify_worktree_state``
  (slice-077) for any branch with a live worktree (WorktreeState maps directly:
  IN_PROGRESS->IN-PROGRESS, BUILT_BUT_NOT_MERGED->STRANDED-COMPLETE, MERGED->skip,
  UNKNOWN->INDETERMINATE).
- ``tools.branch_workflow_audit._resolve_default_branch`` for default resolution.
- ``tools.slice_queue_claim.parse_queue_text`` (slice-072 / PSQ-2) for claims.
- ``tools._stdout.reconfigure_stdout_utf8`` (UTF8-STDOUT-1).

Classification precedence (first match wins; ADR-079 Decision table):
  1. CLAIMED-BY-OTHER  -- PSQ-2 claim for the branch's queue key by a foreign git
     identity (cross-session courtesy; never halt my /slice). Inert in solo-dev.
  2. IN-PROGRESS       -- live worktree classify_worktree_state==IN_PROGRESS, or a
     non-terminal milestone on the branch's own tree (healthy parallel work).
  3. STRANDED-COMPLETE -- git-unmerged AND vault says DONE (BUILT_BUT_NOT_MERGED,
     or archive/slice-NNN-* present, or a terminal milestone). HALT.
  4. ORPHANED          -- git-unmerged AND no vault story anywhere. HALT.
  5. INDETERMINATE     -- could not classify (UNKNOWN / merge-base error). HALT (fail-closed).

Bare-branch (no-worktree) vault reads consult the BRANCH's OWN tree via
``git ls-tree``/``git show <branch>:`` (M1): the stranded archive/milestone of a
committed-but-unmerged slice lives on that branch, not the invoking tree. That
read is committed-tip state and may lag an uncommitted working milestone
(M-add-1) -- for a bare branch committed-tip is the only recoverable state and
the fail-closed posture still surfaces something.

Advisory, never blocking: exit 0 on any successful run (status clean or
divergent); exit 2 only on usage failure. There is NO exit 1.
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

from tools import _stdout
from tools.branch_workflow_audit import _resolve_default_branch
from tools.pulse_worktree_resolver import (
    WorktreeState,
    classify_worktree_state,
    detect_active_worktrees,
)
from tools.slice_queue_claim import parse_queue_text

__all__ = [
    "DivergenceClass",
    "StrandedEntry",
    "classify_branches",
    "compute_status",
    "main",
]

# Canonical BRANCH-2 slice-branch shape (mirrors pulse_worktree_resolver L73).
_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")
# Folder-form of the slice id (HYPHEN, not slash) — the on-disk
# `architecture/slices/slice-NNN-<name>/` directory name (slice-092 / ADR-084).
# The branch and folder forms coincide on the `NNN-name` capture ONLY; never
# prefix-strip across the two (the `slice/` vs `slice-` prefixes match at 6 chars
# only by accident — B2). The `\d{3}` digit-count MUST stay symmetric with
# _SLICE_BRANCH_RE or the folder/branch dedup keys diverge (a laxer folder regex
# would match a folder whose branch ref cannot be keyed — an asymmetric dedup hole;
# code-review m2).
_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")
# Terminal milestone stages for the BARE-branch path (B1, code-review): the vault's
# real terminal stage is `complete` (written by skills/reflect/SKILL.md:305 as
# `stage: complete` / `next-action: none (slice complete)` at /reflect Step 6 — 85/87
# milestones). `reflect` is the TRANSIENT mid-/reflect stage that pulse_worktree_resolver's
# classify_worktree_state keys BUILT_BUT_NOT_MERGED on WHILE a worktree is still live; a
# BARE branch (worktree gone, post-reflect) almost always carries `complete`. Both belong
# in the terminal set so a stranded completed slice on a bare branch is caught, not missed.
_TERMINAL_STAGES = {"reflect", "complete"}


class _UsageError(Exception):
    """Hard input failure -> exit 2 (git unavailable / default unresolvable / not a repo)."""


class DivergenceClass(Enum):
    STRANDED_COMPLETE = "stranded-complete"
    ORPHANED = "orphaned"
    IN_PROGRESS = "in-progress"
    CLAIMED_BY_OTHER = "claimed-by-other"
    INDETERMINATE = "indeterminate"
    # 5th class (ADR-084 / slice-092): a branchless in-flight slice — a
    # `slice-NNN-<name>/` folder in the invoking tree with a non-terminal
    # milestone and NO matching `slice/NNN-*` ref. INFORMATIONAL, never a halt
    # (deliberately absent from `_HALT_CLASSES` below): under PSQ/BRANCH-2 a
    # not-yet-branched scaffold is healthy parallel-safe state, NOT a strand.
    BRANCHLESS_IN_FLIGHT = "branchless-in-flight"


_HALT_CLASSES = {
    DivergenceClass.STRANDED_COMPLETE,
    DivergenceClass.ORPHANED,
    DivergenceClass.INDETERMINATE,
}


@dataclass(frozen=True)
class StrandedEntry:
    branch: str
    worktree_path: str | None
    klass: DivergenceClass
    halt: bool
    vault_state: str
    claimed_by: str | None
    ahead: int | None
    dirty: bool
    reason: str


# ----------------------------- private helpers -----------------------------


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _read_git_identity(repo_root: Path) -> str | None:
    """Return ``"<name> <email>"`` or None if unreadable.

    Non-fatal: when identity is unknown, CLAIMED-BY-OTHER simply does not fire
    (a foreign claim cannot be proven foreign), and the branch falls through to
    the worktree/vault signals.
    """
    try:
        name = _run_git(repo_root, "config", "user.name")
        email = _run_git(repo_root, "config", "user.email")
    except FileNotFoundError:
        return None
    if name.returncode != 0 or email.returncode != 0:
        return None
    n, e = name.stdout.strip(), email.stdout.strip()
    if not n or not e:
        return None
    return f"{n} {e}"


def _load_claims(repo_root: Path) -> dict[str, str | None]:
    """Map queue candidate key -> claimed_by string (None when unclaimed).

    Non-fatal: absent/unparseable ``slice-queue.md`` -> no claims -> the
    CLAIMED-BY-OTHER class simply never fires (B1 honesty: an in-flight branch
    is frequently absent from the top-10 queue, which is correct fall-through).
    """
    queue = repo_root / "architecture" / "slice-queue.md"
    if not queue.is_file():
        return {}
    try:
        parsed = parse_queue_text(queue.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {name: entry.get("claimed_by") for name, entry in parsed.items()}  # type: ignore[misc]


def _frontmatter_field(text: str, field: str) -> str | None:
    """Extract a YAML-frontmatter scalar field from milestone text."""
    in_fm = False
    for line in text.splitlines():
        s = line.strip()
        if s == "---":
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and s.lower().startswith(field.lower() + ":"):
            # Strip surrounding YAML quotes so `stage: 'complete'` / "complete" parse (m2).
            return s.split(":", 1)[1].strip().strip("'\"")
    return None


def _is_terminal(stage: str | None, next_action: str | None) -> bool:
    if stage and stage.strip().lower() in _TERMINAL_STAGES:
        return True
    # Word-boundary match so `precommit`/`commitment` don't false-positive (m1).
    if next_action and re.search(r"\bcommit\b", next_action.lower()):
        return True
    return False


def _branch_tree_has_path(repo_root: Path, branch: str, path: str) -> bool:
    res = _run_git(repo_root, "ls-tree", branch, "--", path)
    return res.returncode == 0 and bool(res.stdout.strip())


def _branch_tree_file(repo_root: Path, branch: str, path: str) -> str | None:
    res = _run_git(repo_root, "show", f"{branch}:{path}")
    return res.stdout if res.returncode == 0 else None


def _worktree_dirty(wt_path: str) -> bool:
    res = _run_git(Path(wt_path), "status", "--porcelain")
    return res.returncode == 0 and bool(res.stdout.strip())


def _entry(
    branch: str,
    wt: str | None,
    klass: DivergenceClass,
    vault_state: str,
    claimed_by: str | None,
    ahead: int | None,
    reason: str,
    dirty: bool = False,
) -> StrandedEntry:
    return StrandedEntry(
        branch=branch,
        worktree_path=wt,
        klass=klass,
        halt=klass in _HALT_CLASSES,
        vault_state=vault_state,
        claimed_by=claimed_by,
        ahead=ahead,
        dirty=dirty,
        reason=reason,
    )


def _bare_slice_branches(
    repo_root: Path, worktree_branches: set[str]
) -> list[tuple[str, str, str]]:
    """Enumerate local ``slice/NNN-<name>`` branches WITHOUT a live worktree.

    The ``refs/heads/slice/`` ref-glob is load-bearing (m-add-2): ``recovery/*``
    lives at ``refs/heads/recovery/...`` outside this glob and is structurally
    excluded -- widening to ``refs/heads/`` would silently reintroduce
    recovery/* false-positives.
    """
    res = _run_git(repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads/slice/")
    if res.returncode != 0:
        return []
    out: list[tuple[str, str, str]] = []
    for line in res.stdout.splitlines():
        branch = line.strip()
        if not branch or branch in worktree_branches:
            continue
        m = _SLICE_BRANCH_RE.match(branch)
        if not m:
            continue
        out.append((branch, m.group(1), m.group(2)))
    return out


def _classify_bare_branch(
    repo_root: Path,
    branch: str,
    num: str,
    name: str,
    default: str,
    claims: dict[str, str | None],
    my_identity: str | None,
) -> StrandedEntry | None:
    # Merged? (ancestor of default -> integrated -> not stranded).
    anc = _run_git(repo_root, "merge-base", "--is-ancestor", branch, default)
    if anc.returncode == 0:
        return None  # merged -> skip
    if anc.returncode != 1:
        # Genuine merge-base error (not the clean 0/1 contract) -> per-entry INDETERMINATE (m2).
        return _entry(
            branch, None, DivergenceClass.INDETERMINATE, "none", None, None,
            f"merge-base --is-ancestor errored (rc={anc.returncode})",
        )

    # ahead-count: defined-but-not-meaningful for a no-common-ancestor branch (m1) -> None.
    ahead: int | None = None
    if _run_git(repo_root, "merge-base", branch, default).returncode == 0:
        cnt = _run_git(repo_root, "rev-list", "--count", f"{default}..{branch}")
        if cnt.returncode == 0 and cnt.stdout.strip().isdigit():
            ahead = int(cnt.stdout.strip())

    claimed_by = claims.get(name)

    # Precedence #1: foreign claim.
    if claimed_by and my_identity and claimed_by.strip() != my_identity:
        return _entry(
            branch, None, DivergenceClass.CLAIMED_BY_OTHER, f"claimed-by:{claimed_by}",
            claimed_by, ahead, f"queue key {name!r} claimed by {claimed_by!r} (!= my identity)",
        )

    # Read the BRANCH's OWN tree (M1) -- committed-tip (M-add-1 staleness named in design).
    archive_path = f"architecture/slices/archive/slice-{num}-{name}"
    if _branch_tree_has_path(repo_root, branch, archive_path):
        return _entry(
            branch, None, DivergenceClass.STRANDED_COMPLETE, "archived", claimed_by, ahead,
            "archived on the branch's own tree, unmerged",
        )
    milestone_path = f"architecture/slices/slice-{num}-{name}/milestone.md"
    ms = _branch_tree_file(repo_root, branch, milestone_path)
    if ms is not None:
        stage = _frontmatter_field(ms, "stage")
        if _is_terminal(stage, _frontmatter_field(ms, "next-action")):
            return _entry(
                branch, None, DivergenceClass.STRANDED_COMPLETE, f"milestone:{stage}",
                claimed_by, ahead, f"branch milestone terminal (stage={stage})",
            )
        return _entry(
            branch, None, DivergenceClass.IN_PROGRESS, f"milestone:{stage}",
            claimed_by, ahead, f"branch milestone in-flight (stage={stage})",
        )

    # Secondary fallback: the invoking tree's vault (branch may share it if not yet diverged).
    if (repo_root / archive_path).exists():
        return _entry(
            branch, None, DivergenceClass.STRANDED_COMPLETE, "archived(invoking-tree)",
            claimed_by, ahead, "archived in the invoking tree, unmerged",
        )
    inv_ms = repo_root / milestone_path
    if inv_ms.is_file():
        txt = inv_ms.read_text(encoding="utf-8")
        stage = _frontmatter_field(txt, "stage")
        if _is_terminal(stage, _frontmatter_field(txt, "next-action")):
            return _entry(
                branch, None, DivergenceClass.STRANDED_COMPLETE, f"milestone:{stage}",
                claimed_by, ahead, f"invoking-tree milestone terminal (stage={stage})",
            )
        return _entry(
            branch, None, DivergenceClass.IN_PROGRESS, f"milestone:{stage}",
            claimed_by, ahead, f"invoking-tree milestone in-flight (stage={stage})",
        )

    # No vault story anywhere.
    return _entry(
        branch, None, DivergenceClass.ORPHANED, "none", claimed_by, ahead,
        "unmerged branch with no vault story (branch tree, invoking tree, or queue)",
    )


def _branchless_in_flight_slices(
    repo_root: Path, seen_keys: set[str]
) -> list[StrandedEntry]:
    """Enumerate branchless in-flight slice folders (slice-092 / ADR-084).

    A branchless in-flight slice is an ``architecture/slices/slice-NNN-<name>/``
    folder in the INVOKING tree whose ``milestone.md`` exists and is NON-terminal
    AND which has NO matching ``slice/NNN-*`` ref. That is the normal
    pre-``/build-slice`` scaffold state, invisible to the two branch-only passes
    (R-31). Each surviving folder yields ONE informational ``BRANCHLESS_IN_FLIGHT``
    entry (never a halt -- healthy parallel-safe state under PSQ/BRANCH-2).

    Strictly SUBORDINATE to the branch passes (ADR-084 Decision / M2): emits ONLY
    for keys ABSENT from ``seen_keys`` (the union of worktree'd + bare ``slice/*``
    ref keys assembled by ``classify_branches``), so it can never downgrade or mask
    a halt-worthy branch classification, and a slice with BOTH a folder and a branch
    is reported once (via the branch). Fail-open per-folder: absent / unparseable /
    stage-less milestones are skipped -- minting a halt for a missing milestone would
    re-introduce the cry-wolf the slice-087 reframe killed.
    """
    out: list[StrandedEntry] = []
    slices_dir = repo_root / "architecture" / "slices"
    if not slices_dir.is_dir():
        return out  # no vault slices dir -> nothing to surface (advisory-never-blocking)
    for child in sorted(slices_dir.iterdir()):
        if not child.is_dir() or child.name == "archive":
            continue  # files (e.g. _index.md) and the archive/ tree are not in-flight
        m = _SLICE_FOLDER_RE.match(child.name)
        if not m:
            continue  # non-conforming dir (e.g. `slice-bad`) -> skip
        num, name = m.group(1), m.group(2)
        key = f"{num}-{name}"
        if key in seen_keys:
            continue  # already reported via a slice/* ref -> dedup (B2 / precedence subordination)
        ms_path = child / "milestone.md"
        if not ms_path.is_file():
            continue  # fail-open: no milestone -> skip
        try:
            txt = ms_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # fail-open: unreadable -> skip
        stage = _frontmatter_field(txt, "stage")
        if stage is None:
            continue  # parseable-but-stage-less / unparseable -> skip (never `folder:None`, m-add-2)
        if _is_terminal(stage, _frontmatter_field(txt, "next-action")):
            continue  # terminal -> already merged or a strand the branch path owns (4l)
        out.append(_entry(
            f"slice-{num}-{name}",  # folder-form id (HYPHEN) -> signals "folder, not branch"
            None,
            DivergenceClass.BRANCHLESS_IN_FLIGHT,
            f"folder:{stage}",
            None,
            None,
            f"branchless in-flight slice (folder slice-{num}-{name}, stage={stage}, "
            f"no slice/{num}-* branch) -- informational, parallel-safe",
        ))
    return out


# ----------------------------- library API -----------------------------


def classify_branches(repo_root: Path | str) -> list[StrandedEntry]:
    """Classify every unmerged ``slice/*`` branch into a divergence class.

    Raises ``_UsageError`` (mapped to exit 2 by ``main``) on hard input failure:
    git binary unavailable, ``repo_root`` is not a git repository, or the default
    branch cannot be resolved. Never raises on a per-branch classification
    failure -- that becomes a per-entry INDETERMINATE (advisory-never-blocking).
    """
    repo_root = Path(repo_root)
    try:
        rp = _run_git(repo_root, "rev-parse", "--git-dir")
    except FileNotFoundError as exc:
        raise _UsageError(f"git binary not available on PATH: {exc}") from exc
    if rp.returncode != 0:
        raise _UsageError(f"not a git repository: {repo_root}")
    default = _resolve_default_branch(repo_root)
    if not default:
        raise _UsageError(
            "could not resolve default branch (no origin/HEAD, no init.defaultBranch)"
        )

    my_identity = _read_git_identity(repo_root)
    claims = _load_claims(repo_root)

    entries: list[StrandedEntry] = []
    worktree_branches: set[str] = set()

    # --- worktree'd branches (reuse slice-077 detect + classify) ---
    for wt in detect_active_worktrees(repo_root):
        worktree_branches.add(wt.branch)
        claimed_by = claims.get(wt.slice_name)
        dirty = _worktree_dirty(wt.path)
        # Precedence #1: foreign claim wins (cross-session courtesy).
        if claimed_by and my_identity and claimed_by.strip() != my_identity:
            entries.append(_entry(
                wt.branch, wt.path, DivergenceClass.CLAIMED_BY_OTHER, f"claimed-by:{claimed_by}",
                claimed_by, None, f"queue key {wt.slice_name!r} claimed by {claimed_by!r}", dirty,
            ))
            continue
        cls = classify_worktree_state(wt, default, repo_root)
        if cls.state is WorktreeState.MERGED:
            continue  # integrated -> not stranded
        if cls.state is WorktreeState.IN_PROGRESS:
            klass = DivergenceClass.IN_PROGRESS
        elif cls.state is WorktreeState.BUILT_BUT_NOT_MERGED:
            klass = DivergenceClass.STRANDED_COMPLETE
        else:  # UNKNOWN
            klass = DivergenceClass.INDETERMINATE
        entries.append(_entry(
            wt.branch, wt.path, klass,
            f"worktree:{cls.state.value}:{cls.milestone_stage}", claimed_by, None, cls.reason, dirty,
        ))

    # --- bare branches (no live worktree) ---
    bare_tuples = _bare_slice_branches(repo_root, worktree_branches)
    for branch, num, name in bare_tuples:
        entry = _classify_bare_branch(repo_root, branch, num, name, default, claims, my_identity)
        if entry is not None:
            entries.append(entry)

    # --- branchless in-flight slices (slice-092 / ADR-084): folders with no slice/* ref ---
    # seen_keys = the `NNN-name` key of EVERY slice/* ref (worktree'd AND bare), so a slice
    # with both a folder AND a branch is deduped (reported once, via the branch path). The
    # worktree key is sliced from the FULL `slice/NNN-name` ref in `worktree_branches`
    # (`wt.branch`), NOT derived from `wt.slice_name` (the bare name without the `NNN-`
    # prefix) -- that mis-key is the B2 double-report trap.
    seen_keys = (
        {b[len("slice/"):] for b in worktree_branches}
        | {f"{num}-{name}" for (_b, num, name) in bare_tuples}
    )
    entries.extend(_branchless_in_flight_slices(repo_root, seen_keys))

    return entries


def compute_status(entries: list[StrandedEntry]) -> str:
    """``divergent`` iff >=1 halt-worthy entry; else ``clean`` (IN-PROGRESS /
    CLAIMED-BY-OTHER entries are listed but do NOT make the run divergent)."""
    return "divergent" if any(e.halt for e in entries) else "clean"


def _entry_to_dict(e: StrandedEntry) -> dict[str, object]:
    return {
        "branch": e.branch,
        "worktree_path": e.worktree_path,
        "klass": e.klass.value,
        "halt": e.halt,
        "vault_state": e.vault_state,
        "claimed_by": e.claimed_by,
        "ahead": e.ahead,
        "dirty": e.dirty,
        "reason": e.reason,
    }


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="stranded-slice-audit",
        description="Classify unmerged slice/* branches into the 4-class divergence model (ADR-079).",
    )
    parser.add_argument(
        "--repo-root", "--root", dest="repo_root", default=Path("."), type=Path,
        help="repository root to inspect (default: cwd)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of human text")
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    try:
        entries = classify_branches(repo_root)
    except _UsageError as exc:
        sys.stderr.write(f"stranded-slice-audit: {exc}\n")
        return 2

    status = compute_status(entries)
    if args.json:
        print(json.dumps(
            {"action": "audit", "status": status, "entries": [_entry_to_dict(e) for e in entries]},
            indent=2,
        ))
    else:
        n_div = sum(1 for e in entries if e.halt)
        # The human-mode header ALWAYS emits a non-ASCII arrow so the cp1252
        # _ROOT_ONLY_TOOLS regression genuinely exercises stdout (M3, non-vacuous).
        print(f"stranded-slice-audit → status: {status} ({n_div} divergent)")
        for e in entries:
            tag = "HALT" if e.halt else "info"
            wt = f" wt={e.worktree_path}" if e.worktree_path else ""
            print(f"  {tag}  {e.branch}  [{e.klass.value}]{wt}  {e.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
