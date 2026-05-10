"""Critique-agent in-repo↔installed content-drift audit (CAD-1).

Validates that the in-repo `agents/critique.md` and the installed
`~/.claude/agents/critique.md` carry byte-equal content (sha256 match).

Per CAD-1 (methodology-changelog.md v0.22.0). The rule's purpose:
- Slice-006 (CCC-1) discovered that every `/critic-calibrate` ACCEPTED
  proposal that follows the prior skill prose at
  `skills/critic-calibrate/SKILL.md:107-114` instructs editing the
  installed `~/.claude/agents/critique.md` only — leaving the in-repo
  canonical source out of sync. Slice-006 had to back-sync the
  surgical Dim 1 + Dim 4 sub-bullets that existed only in the
  installed copy. The defect class is N=1 visible (slice-006), N=∞
  projected (every future calibration run).
- Slice-007 closes the loop with a hybrid prevention + detection: the
  skill prose at `skills/critic-calibrate/SKILL.md:107-114` is updated
  to name in-repo as canonical with manual forward-sync (prevention);
  this audit verifies sha256 byte-equality post-edit (detection).

The audit is intentionally narrow: it covers `agents/critique.md` only.
INST-2 (general content-equality across all installed files) was rejected
at slice-007 ADR-006 as over-scoped vs the N=1 evidence base — it would
violate INST-1's source-independence design contract.

Usage:
    python -m tools.critique_agent_drift_audit
    python -m tools.critique_agent_drift_audit --repo-root <path>
    python -m tools.critique_agent_drift_audit --claude-dir <path>
    python -m tools.critique_agent_drift_audit --json

Exit codes:
    0  clean — in-repo and installed agents/critique.md byte-equal
    1  content-drift — sha256 differs; output names both paths and hashes
    2  path-missing — either file doesn't exist
       OR usage-error — argparse error / sanity-check refusal
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class CritiqueDriftViolation:
    kind: str       # "content-drift" | "path-missing" | "usage-error"
    severity: str   # "Important"
    paths: list[str]
    hashes: list[str]
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    repo_root: str = ""
    claude_dir: str = ""
    in_repo_path: str = ""
    installed_path: str = ""
    in_repo_sha256: str = ""
    installed_sha256: str = ""
    violations: list[CritiqueDriftViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "CAD-1",
            "repo_root": self.repo_root,
            "claude_dir": self.claude_dir,
            "in_repo_path": self.in_repo_path,
            "installed_path": self.installed_path,
            "in_repo_sha256": self.in_repo_sha256,
            "installed_sha256": self.installed_sha256,
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "clean": len(self.violations) == 0,
            },
        }


def _sha256_of(path: Path) -> str:
    """Compute sha256 hex digest of a file's bytes."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _check_sanity(repo_root: Path) -> CritiqueDriftViolation | None:
    """Refuse if --repo-root doesn't look like an AI SDLC source root.

    Per Critic M3: prevents accidental comparison against `build/lib/`
    shadow or arbitrary directory. Sentinel files: plugin.yaml +
    INSTALL.md must both exist at --repo-root.
    """
    plugin_yaml = repo_root / "plugin.yaml"
    install_md = repo_root / "INSTALL.md"
    if not (plugin_yaml.exists() and install_md.exists()):
        missing = []
        if not plugin_yaml.exists():
            missing.append(str(plugin_yaml))
        if not install_md.exists():
            missing.append(str(install_md))
        return CritiqueDriftViolation(
            kind="usage-error",
            severity="Important",
            paths=[str(repo_root)],
            hashes=[],
            message=(
                f"--repo-root '{repo_root}' does not appear to be an AI SDLC "
                f"source root (missing: {', '.join(missing)}). Refusing to "
                f"compare against potentially stale `build/lib/` shadow or "
                f"arbitrary directory. Pass --repo-root <ai-sdlc-source> "
                f"explicitly."
            ),
        )
    return None


def run_audit(repo_root: Path, claude_dir: Path) -> AuditResult:
    """Run the CAD-1 audit.

    Steps:
      1. Sanity-check --repo-root (must contain plugin.yaml + INSTALL.md).
      2. Resolve in-repo and installed paths to agents/critique.md.
      3. Verify both files exist.
      4. Compute sha256 of each.
      5. Compare; emit content-drift violation if differ.
    """
    result = AuditResult(
        repo_root=str(repo_root),
        claude_dir=str(claude_dir),
    )

    sanity = _check_sanity(repo_root)
    if sanity is not None:
        result.violations.append(sanity)
        return result

    in_repo = repo_root / "agents" / "critique.md"
    installed = claude_dir / "agents" / "critique.md"
    result.in_repo_path = str(in_repo)
    result.installed_path = str(installed)

    if not in_repo.exists():
        result.violations.append(CritiqueDriftViolation(
            kind="path-missing",
            severity="Important",
            paths=[str(in_repo)],
            hashes=[],
            message=(
                f"in-repo agents/critique.md not found at {in_repo}. "
                f"Check --repo-root or run from an AI SDLC source root."
            ),
        ))
        return result

    if not installed.exists():
        result.violations.append(CritiqueDriftViolation(
            kind="path-missing",
            severity="Important",
            paths=[str(installed)],
            hashes=[],
            message=(
                f"installed agents/critique.md not found at {installed}. "
                f"Re-run INSTALL.md to populate ~/.claude/."
            ),
        ))
        return result

    result.in_repo_sha256 = _sha256_of(in_repo)
    result.installed_sha256 = _sha256_of(installed)

    if result.in_repo_sha256 != result.installed_sha256:
        result.violations.append(CritiqueDriftViolation(
            kind="content-drift",
            severity="Important",
            paths=[str(in_repo), str(installed)],
            hashes=[result.in_repo_sha256, result.installed_sha256],
            message=(
                f"content-drift between in-repo and installed agents/critique.md.\n"
                f"  in-repo:   {in_repo} (sha256: {result.in_repo_sha256})\n"
                f"  installed: {installed} (sha256: {result.installed_sha256})\n"
                f"Per /critic-calibrate skill prose, the in-repo copy is "
                f"canonical; forward-sync the in-repo content to ~/.claude/, "
                f"OR (if installed has content in-repo doesn't) back-sync "
                f"first per slice-005+006 bidirectional discipline."
            ),
        ))

    return result


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"CAD-1: clean - agents/critique.md byte-equal across in-repo "
            f"({result.in_repo_path}) and installed ({result.installed_path}); "
            f"sha256: {result.in_repo_sha256[:16]}...\n"
        )

    out: list[str] = [
        f"{len(result.violations)} CAD-1 violation(s):\n\n"
    ]
    for v in result.violations:
        out.append(f"  [{v.severity}] ({v.kind})\n    {v.message}\n\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="critique_agent_drift_audit",
        description=(
            "CAD-1 in-repo↔installed content-equality audit for "
            "agents/critique.md."
        ),
    )
    parser.add_argument(
        "--repo-root", type=Path, default=Path.cwd(),
        help=(
            "Path to the AI SDLC source root (must contain plugin.yaml "
            "and INSTALL.md as sanity check). Default: cwd."
        ),
    )
    parser.add_argument(
        "--claude-dir", type=Path, default=Path.home() / ".claude",
        help="Path to ~/.claude/ (default: $HOME/.claude)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    result = run_audit(repo_root=args.repo_root, claude_dir=args.claude_dir)

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    if not result.violations:
        return 0
    # Disambiguate exit codes by violation kind:
    # content-drift -> 1; path-missing or usage-error -> 2.
    kinds = {v.kind for v in result.violations}
    if "content-drift" in kinds and "path-missing" not in kinds and "usage-error" not in kinds:
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
