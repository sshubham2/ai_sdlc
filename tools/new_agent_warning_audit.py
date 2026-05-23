"""New-agent session-restart warning audit (NAW-1).

Per **NAW-1** (`methodology-changelog.md` v0.66.0; slice-063; [[ADR-061]];
mints a new rule; supersedes nothing). NAW-1 is the first audit-enforced
gate on the **discovery-gate** axis, adjacent to (but NOT extending) the
forward-sync family (PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1).

R-18 (slice-061-discovered; N=2 cumulative recurrence at slice-061 +
slice-062): the Claude Code agent registry is loaded at session start;
mid-session writes to `~/.claude/agents/*.md` are invisible to
`Agent(subagent_type=…)` calls until the user restarts Claude Code. NAW-1
surfaces this failure mode methodology-discoverably at `/build-slice`
Step 6 BEFORE the next slice's chain runs.

**Read mechanism** (B1 critique fix). The naive `git diff <base>...HEAD`
is commit-vs-commit only (per https://git-scm.com/docs/git-diff
"`<commit>...<commit>` … starting at a common ancestor of both") and
would return EMPTY for an uncommitted new agent (slice work lives in the
uncommitted working tree at Step 6 — commits land only at
`/commit-slice`). The audit therefore reads a **union of three
git-derived sources** covering all states a new agent file can occupy at
Step 6:

  1. ``git diff --name-only --diff-filter=A {base} -- 'agents/*.md'``
     — **working-tree-vs-base**; modified + staged-but-uncommitted adds.
  2. ``git ls-files --others --exclude-standard -- 'agents/*.md'``
     — **untracked-new** agent files (the canonical untracked-file
     enumerator per https://git-scm.com/docs/git-ls-files).
  3. ``git diff --name-only --diff-filter=A {base}...HEAD -- 'agents/*.md'``
     — **commits-vs-base**; already-committed-in-branch agents (covers
     any `/build-slice` Step 4 intermediate commit or worktree-add path).

Results are unioned and deduplicated by path. ``base`` is resolved via
BRANCH-1's logic at ``tools/branch_workflow_audit.py:127-146``:
``git symbolic-ref refs/remotes/origin/HEAD`` →
``git config init.defaultBranch`` → **``None``** (M3 critique fix: NO
``main`` literal fallback in the implementation; ``None`` ⇒ NAW-1 exits
2 per BRANCH-1's ``default-branch-unresolvable`` semantics).

**Test seams** (m3 critique fix — seam-driven self-application replaces
the bootstrap-brittle branch-state-dependent original).
``check(root, *, default_branch_resolver=…, added_files_resolver=…)``
exposes two injectable callables. The regression suite drives controlled
fixture sets — empty / single-entry / synthetic-tmp-repo — without
depending on slice-063's specific live branch state. Both injection
seams default to the real resolvers; tests override per-case.

**Semantics** (BINARY exit contract by construction — there is NO
"drift" branch for a discovery gate):
  - no added ``agents/*.md`` ⇒ exit 0, status ``"clean"``, quiet stdout.
  - ≥1 added ``agents/*.md`` ⇒ exit 0, status ``"warn"``, WARN line(s)
    on stdout (each citing agent path + session-restart instruction +
    R-18 cross-reference).
  - usage error ⇒ exit 2 with stderr message. Causes: repo root
    unresolvable, ``git`` binary unavailable on PATH, default-branch
    resolution returned ``None``, any of the three ``git`` subprocess
    calls non-zero.

**NEVER exit 1** — by construction. A new-agent slice is NOT a slice
regression; the WARN is informational, never a HALT. The pytest
regression suite explicitly asserts ``exit_code == 0`` on BOTH clean AND
warn branches (the load-bearing contract).

**Overbroad-pathspec known false-positive class** (m2 critique fix). The
``agents/*.md`` pathspec matches ANY ``.md`` file added under ``agents/``
— not just files registered in ``tools/install_audit.py``
``_CANONICAL_AGENTS``. The current ``agents/`` directory carries
``agents/AUTHORING.md`` (a documentation file, not a registered
subagent); a future slice that adds a similar prose-doc under
``agents/`` (e.g., ``agents/CONVENTIONS.md``) will trigger a NAW-1 WARN
even though no registry cache-miss can result. Accepted as a
known-false-positive class with **minimal cost**: an extra WARN never
HALTs (the binary exit contract is preserved); the user can ignore the
WARN when the added file is verifiably a prose-doc. See ADR-061
§Consequences for the rejected ``_CANONICAL_AGENTS``-scoped pathspec
alternative.

**Wiring** (1 point; intentionally NOT mirrored at ``/reflect`` Step 5b
— NAW-1 has no installed-side mutation to verify, distinct from
AVFS-1/MCFS-1/TVFS-1 forward-sync gates):
  - ``/build-slice`` Step 6 pre-finish, appended after the TVFS-1 gate.

Usage::

    python -m tools.new_agent_warning_audit            # --check
    python -m tools.new_agent_warning_audit --check
    python -m tools.new_agent_warning_audit --json
    python -m tools.new_agent_warning_audit --root <repo-root>

Exit codes::

    0  no added `agents/*.md` (clean, quiet) OR ≥1 added (warn, stdout)
    2  usage error (repo root unresolvable, `git` unavailable,
       default-branch resolution failed, or any git subprocess call
       non-zero)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

_AGENT_PATHSPEC = "agents/*.md"

# Canonical NAW-1 WARN line template — pinned by `test_new_agent_warning_audit.py
# ::test_warn_line_cites_agent_path_session_restart_and_r_18`. MUST cite
# (a) the agent path, (b) the session-restart-before-next-slice
# recommendation, and (c) the explicit R-18 risk-register cross-reference.
_WARN_LINE_TEMPLATE = (
    "NAW-1 NEW-AGENT WARNING — this slice adds the subagent file "
    "`{agent_path}`. The Claude Code agent registry is loaded at session "
    "start; the new agent is NOT visible to `Agent(subagent_type=…)` "
    "calls in this session. Before invoking the next slice's chain, "
    "restart Claude Code so the new agent is loaded. See "
    "`architecture/risk-register.md` R-18. This is a WARN, not a slice "
    "regression."
)

_USAGE_REPO_ROOT_MISSING = (
    "NAW-1 usage error: repo root not found: {root}"
)
_USAGE_GIT_MISSING = (
    "NAW-1 usage error: `git` command not found on PATH; NAW-1 cannot "
    "resolve the slice diff."
)
_USAGE_DEFAULT_BRANCH_UNRESOLVABLE = (
    "NAW-1 usage error: default branch unresolvable (neither "
    "`git symbolic-ref refs/remotes/origin/HEAD` nor "
    "`git config init.defaultBranch` returned a value). Configure an "
    "`origin/HEAD` ref or set `init.defaultBranch`."
)
_USAGE_GIT_SUBCOMMAND_FAILED = (
    "NAW-1 usage error: `git {subcommand}` exited non-zero ({rc}): "
    "{stderr}"
)


def _resolve_default_branch(root: Path) -> str | None:
    """Resolve the repo's default branch via ``git symbolic-ref`` then
    ``git config init.defaultBranch``. Returns the branch name, or
    ``None`` if neither resolution path succeeds (M3 critique fix: there
    is NO ``main`` literal fallback in the implementation — mirrors
    BRANCH-1's `_resolve_default_branch` at
    ``tools/branch_workflow_audit.py:127-146`` byte-for-byte semantics).
    """
    try:
        r1 = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=root, capture_output=True, text=True, encoding="utf-8",
        )
        if r1.returncode == 0:
            # Output: "refs/remotes/origin/master\n"
            full = r1.stdout.strip()
            prefix = "refs/remotes/origin/"
            if full.startswith(prefix):
                return full[len(prefix):]
    except FileNotFoundError:
        # git binary missing — caller will hit this again at downstream
        # calls; return None so the upstream usage path fires.
        return None

    try:
        r2 = subprocess.run(
            ["git", "config", "init.defaultBranch"],
            cwd=root, capture_output=True, text=True, encoding="utf-8",
        )
        if r2.returncode == 0:
            val = r2.stdout.strip()
            if val:
                return val
    except FileNotFoundError:
        return None
    return None


def _resolve_added_agent_files(root: Path, base: str) -> list[str]:
    """Compute the union of three git-derived sets of added
    ``agents/*.md`` paths covering all states a new agent file can
    occupy at ``/build-slice`` Step 6.

    Sources (per ADR-061 §Decision L60-67):
      (i)   ``git diff --name-only --diff-filter=A {base} -- 'agents/*.md'``
            working-tree-vs-base; modified + staged-but-uncommitted adds.
      (ii)  ``git ls-files --others --exclude-standard -- 'agents/*.md'``
            untracked-new agents.
      (iii) ``git diff --name-only --diff-filter=A {base}...HEAD -- 'agents/*.md'``
            commits-vs-base; already-committed-in-branch agents.

    Returns the deduplicated union, sorted for stable output. Raises
    ``subprocess.CalledProcessError`` if any git call exits non-zero, or
    ``FileNotFoundError`` if the ``git`` binary is missing — caller
    converts both to exit-2 usage class.
    """
    found: set[str] = set()

    def _run(args: list[str]) -> list[str]:
        proc = subprocess.run(
            args, cwd=root, capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(
                proc.returncode, args, output=proc.stdout, stderr=proc.stderr,
            )
        return [ln for ln in proc.stdout.splitlines() if ln.strip()]

    # Source (i): working-tree-vs-base (modified + staged adds)
    found.update(_run([
        "git", "diff", "--name-only", "--diff-filter=A", base,
        "--", _AGENT_PATHSPEC,
    ]))
    # Source (ii): untracked-new
    found.update(_run([
        "git", "ls-files", "--others", "--exclude-standard",
        "--", _AGENT_PATHSPEC,
    ]))
    # Source (iii): commits-vs-base (already-committed-in-branch adds)
    found.update(_run([
        "git", "diff", "--name-only", "--diff-filter=A", f"{base}...HEAD",
        "--", _AGENT_PATHSPEC,
    ]))

    return sorted(found)


def _format_warn_line(agent_path: str) -> str:
    """Render the canonical NAW-1 WARN line for a single agent path.

    The template MUST cite (a) the agent path, (b) the session-restart-
    before-next-slice recommendation, and (c) the explicit R-18
    cross-reference per ADR-061 §Decision (Attributed WARN message).
    Pinned by ``test_warn_line_cites_agent_path_session_restart_and_r_18``.
    """
    return _WARN_LINE_TEMPLATE.format(agent_path=agent_path)


@dataclass
class CheckResult:
    status: str = "clean"            # clean | warn | usage
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
    default_branch_resolver: Callable[[Path], str | None] = (
        _resolve_default_branch
    ),
    added_files_resolver: Callable[[Path, str], list[str]] = (
        _resolve_added_agent_files
    ),
) -> CheckResult:
    """Assert no new ``agents/*.md`` files have been added in the slice's
    diff vs the resolved default branch.

    Returns a ``CheckResult`` with binary exit contract (0/2; never 1):
      - 0 status ``"clean"``: no added agents (quiet)
      - 0 status ``"warn"``: ≥1 added agents; WARN line(s) populated
      - 2 status ``"usage"``: environment/setup error

    Both resolvers are injectable for the regression suite per
    [[ADR-061]] §Consequences (m3 critique fix — seam-driven self-
    application avoids branch-state-dependent assertions).
    """
    result = CheckResult()

    if not root.exists():
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(
            _USAGE_REPO_ROOT_MISSING.format(root=root)
        )
        return result

    base = default_branch_resolver(root)
    if base is None:
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(_USAGE_DEFAULT_BRANCH_UNRESOLVABLE)
        return result

    try:
        added = added_files_resolver(root, base)
    except FileNotFoundError:
        result.status = "usage"
        result.exit_code = 2
        result.divergences.append(_USAGE_GIT_MISSING)
        return result
    except subprocess.CalledProcessError as e:
        result.status = "usage"
        result.exit_code = 2
        subcommand = (
            " ".join(e.cmd[1:]) if isinstance(e.cmd, list) and len(e.cmd) > 1
            else str(e.cmd)
        )
        result.divergences.append(
            _USAGE_GIT_SUBCOMMAND_FAILED.format(
                subcommand=subcommand, rc=e.returncode,
                stderr=(e.stderr or "").strip(),
            )
        )
        return result

    if added:
        result.status = "warn"
        result.exit_code = 0
        for agent_path in added:
            result.warnings.append(_format_warn_line(agent_path))
        return result

    result.status = "clean"
    result.exit_code = 0
    return result


def _format_human(result: CheckResult) -> str:
    if result.status == "usage":
        return (
            "NAW-1 new-agent warning audit: USAGE ERROR\n\n"
            + "".join(f"  {d}\n" for d in result.divergences)
        )
    if result.status == "warn":
        return (
            "NAW-1 new-agent warning audit: WARN (non-blocking; exit 0)\n\n"
            + "".join(f"  WARN: {w}\n" for w in result.warnings)
        )
    # clean → quiet stdout (per ADR-061 §Decision exit contract)
    return ""


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="new_agent_warning_audit",
        description=(
            "NAW-1 — emit a non-blocking WARN at /build-slice Step 6 "
            "when the slice diff adds any `agents/*.md` file (Claude "
            "Code agent registry session-restart-before-next-slice "
            "recommendation; retires R-18)."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check for newly-added `agents/*.md` files (default action)",
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
        out = _format_human(result)
        if out:
            sys.stdout.write(out)

    if result.status == "usage":
        # Mirror divergences to stderr (AVFS-1/TVFS-1 precedent)
        for d in result.divergences:
            sys.stderr.write(d + "\n")

    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
