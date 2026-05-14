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
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


# Canonical regex for the `BRANCH=skip` escape-hatch line in build-log.md Events.
# Pinned in skills/build-slice/SKILL.md Step 7c per slice-021 AC #2.
_BRANCH_SKIP_LINE_RE = re.compile(
    r"^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+",
    re.MULTILINE,
)

# Slice-branch pattern: `slice/NNN-<slice-name>` (zero-padded 3-digit number).
_SLICE_BRANCH_RE = re.compile(r"^slice/(\d{3})-(.+)$")

# Slice-folder pattern: `slice-NNN-<slice-name>`.
_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")


@dataclass(frozen=True)
class BranchViolation:
    kind: str       # "on-default-branch" | "slice-branch-mismatch" |
                    # "escape-hatch-malformed" | "default-branch-unresolvable" |
                    # "stale-slice-branch" | "usage-error"
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
    """Compute expected `slice/NNN-<slice-name>` branch from slice-folder name."""
    folder_name = slice_folder.name
    match = _SLICE_FOLDER_RE.match(folder_name)
    if not match:
        return ""
    number, name = match.group(1), match.group(2)
    return f"slice/{number}-{name}"


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
        result.violations.append(
            BranchViolation(
                kind="usage-error",
                severity="Important",
                message=(
                    f"slice folder name does not match `slice-NNN-<name>` pattern: "
                    f"{slice_folder.name}"
                ),
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

    # Check escape-hatch.
    escape_hatch, rationale, malformed = _check_escape_hatch(slice_folder)
    if malformed:
        result.violations.append(malformed)
        return result
    result.escape_hatch_used = escape_hatch
    result.escape_hatch_rationale = rationale

    # Apply branch-state logic.
    if current == default:
        if not escape_hatch:
            result.violations.append(
                BranchViolation(
                    kind="on-default-branch",
                    severity="Important",
                    message=(
                        f"active-slice work occurred on default branch '{default}' with no canonical "
                        f"`BRANCH=skip — rationale: <text>` escape-hatch in build-log.md Events. "
                        f"Expected branch: '{expected}'. "
                        f"Either switch to '{expected}' OR document escape-hatch per "
                        f"skills/build-slice/SKILL.md Step 7c canonical shape."
                    ),
                )
            )
        # If escape_hatch present, acceptance via canonical escape-hatch.
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
