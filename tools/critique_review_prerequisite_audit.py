"""Critique-review prerequisite audit (CRP-1).

Refuses `/build-slice` when a mandatory `/critique-review` (DR-1) was
skipped without a documented rationale. First structural skip-detector
for DR-1 — `tools/critique_review_audit.py` only validates the *structure*
of a `critique-review.md` that exists and runs only inside
`/critique-review` itself, so it cannot detect a *skip*.

Per CRP-1 (methodology-changelog.md v0.40.0). CRP-1 is an
**audit-enforced gate** (its programmatic gate is this module), so per
ADR-019's test-pinned naming note it carries the bare `CRP-1` form
(NO `-D` suffix — `-D` is reserved for /critique-time prose-heuristics
with no audit). Naming-class peers: BC-1, CAD-1, PMI-1, INST-1, WIRE-1,
BRANCH-1, UTF8-STDOUT-1.

Refuse condition (exit 1, `mandatory-critique-review-absent`):
    mode in {STANDARD, HEAVY}
    AND milestone.md `critic-required: true`
    AND `critique-review.md` absent in the slice folder
    AND no canonical `critique-review-skip` frontmatter key in milestone.md

Accept (exit 0): `critique-review.md` present, OR canonical
`critique-review-skip` value present, OR mode == MINIMAL, OR
`critic-required: false`.

Malformed-skip (exit 1, Important, `escape-hatch-malformed`):
`critique-review-skip` frontmatter key present but value does NOT match
`^skip — rationale: .+`. Detection is keyed on the *frontmatter key*
(not a body substring scan) — this eliminates the BRANCH-1-style
narrative-prose false-positive risk (per /critique m2 + ADR-024).

Mode resolution (per design.md / ADR-024):
1. Primary: `architecture/triage.md` frontmatter `mode:` value.
2. Fallback: `CLAUDE.md` `**Mode**:` line.
3. STOP (exit 2 usage-error) if neither resolves.

Escape-hatch location is the milestone.md `critique-review-skip:`
frontmatter key (NOT build-log.md Events as BRANCH-1, NOT a free-form
body line) — per ADR-024: the CRP-1 primary gate fires at the
`## Prerequisite check` before build-log.md exists, AND the key must
survive build-slice Step 7b's continuous milestone.md rewrite.

Usage:
    python -m tools.critique_review_prerequisite_audit <slice-folder>
    python -m tools.critique_review_prerequisite_audit --json <slice-folder>
    python -m tools.critique_review_prerequisite_audit --root <repo-root> <slice-folder>

Exit codes:
    0  clean (accept — review present / documented-skip / mode==MINIMAL / not critic-required)
    1  violations (mandatory review absent + unrationalised, or malformed skip)
    2  usage error (slice-folder missing, milestone.md missing, mode unresolvable)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import _stdout

# Canonical regex for the milestone.md `critique-review-skip:` frontmatter
# value. Same `rationale:` spirit as BRANCH-1's `BRANCH=skip — rationale:`
# (ADR-024); pinned in skills/build-slice/SKILL.md CRP-1 prerequisite
# sub-block and asserted by tests/methodology/test_critique_review_prerequisite_audit.py.
_SKIP_VALUE_RE = re.compile(r"^skip — rationale: .+")

# Modes for which a mandatory /critique-review is enforced.
_ENFORCED_MODES = {"STANDARD", "HEAVY"}

_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")


@dataclass(frozen=True)
class CRPViolation:
    kind: str       # "mandatory-critique-review-absent" |
                    # "escape-hatch-malformed" | "usage-error" |
                    # "mode-unresolvable"
    severity: str   # "Important" (all CRP-1 violations refuse)
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    slice_folder: str = ""
    repo_root: str = ""
    resolved_mode: str = ""
    critic_required: bool | None = None
    critique_review_present: bool = False
    skip_key_present: bool = False
    skip_rationale: str | None = None
    accepted_reason: str = ""
    violations: list[CRPViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "CRP-1",
            "slice_folder": self.slice_folder,
            "repo_root": self.repo_root,
            "resolved_mode": self.resolved_mode,
            "critic_required": self.critic_required,
            "critique_review_present": self.critique_review_present,
            "skip_key_present": self.skip_key_present,
            "skip_rationale": self.skip_rationale,
            "accepted_reason": self.accepted_reason,
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "clean": not self.violations,
            },
        }


def _frontmatter_block(text: str) -> str | None:
    """Return the YAML frontmatter block (between leading `---` fences) or None.

    A lightweight scan (no yaml dependency) sufficient for scalar reads —
    mirrors the minimal-dependency style of the other tools/ audits.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[1:idx])
    return None


def _frontmatter_value(block: str, key: str) -> str | None:
    """Return the raw string value for `key:` in a frontmatter block, or None."""
    pat = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    m = pat.search(block)
    if not m:
        return None
    val = m.group(1).strip()
    # Strip surrounding quotes if present.
    if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
        val = val[1:-1]
    return val


def _resolve_mode(repo_root: Path) -> str | None:
    """Resolve pipeline mode.

    Primary: architecture/triage.md frontmatter `mode:`.
    Fallback: CLAUDE.md `**Mode**:` line.
    Returns an uppercased mode string, or None if unresolvable.
    """
    triage = repo_root / "architecture" / "triage.md"
    if triage.exists():
        block = _frontmatter_block(triage.read_text(encoding="utf-8"))
        if block:
            val = _frontmatter_value(block, "mode")
            if val:
                return val.strip().upper()

    claude_md = repo_root / "CLAUDE.md"
    if claude_md.exists():
        m = re.search(
            r"^\*\*Mode\*\*\s*:\s*([A-Za-z]+)",
            claude_md.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if m:
            return m.group(1).strip().upper()

    return None


def audit(slice_folder: Path, repo_root: Path | None = None) -> AuditResult:
    """Run the CRP-1 audit against a slice folder."""
    slice_folder = Path(slice_folder).resolve()
    if not slice_folder.exists():
        return AuditResult(
            slice_folder=str(slice_folder),
            violations=[
                CRPViolation(
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
                    CRPViolation(
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

    milestone = slice_folder / "milestone.md"
    if not milestone.exists():
        result.violations.append(
            CRPViolation(
                kind="usage-error",
                severity="Important",
                message=f"milestone.md not found in slice folder: {slice_folder}",
            )
        )
        return result

    block = _frontmatter_block(milestone.read_text(encoding="utf-8"))
    if block is None:
        result.violations.append(
            CRPViolation(
                kind="usage-error",
                severity="Important",
                message="milestone.md has no YAML frontmatter block (cannot read critic-required)",
            )
        )
        return result

    # Resolve mode.
    mode = _resolve_mode(repo_root)
    if mode is None:
        result.violations.append(
            CRPViolation(
                kind="mode-unresolvable",
                severity="Important",
                message=(
                    "cannot resolve pipeline mode from architecture/triage.md "
                    "frontmatter `mode:` or CLAUDE.md `**Mode**:` line"
                ),
            )
        )
        return result
    result.resolved_mode = mode

    # Read critic-required.
    cr_raw = _frontmatter_value(block, "critic-required")
    critic_required = (cr_raw or "").strip().lower() == "true"
    result.critic_required = critic_required

    # critique-review.md presence.
    result.critique_review_present = (slice_folder / "critique-review.md").exists()

    # Escape-hatch: critique-review-skip frontmatter key.
    skip_val = _frontmatter_value(block, "critique-review-skip")
    result.skip_key_present = skip_val is not None
    if skip_val is not None:
        if _SKIP_VALUE_RE.match(skip_val):
            result.skip_rationale = skip_val
        else:
            result.violations.append(
                CRPViolation(
                    kind="escape-hatch-malformed",
                    severity="Important",
                    message=(
                        f"milestone.md `critique-review-skip:` key present but value "
                        f"{skip_val!r} does not match canonical shape "
                        f"`skip — rationale: <text>` (per ADR-024 / "
                        f"skills/build-slice/SKILL.md CRP-1 sub-block)."
                    ),
                )
            )
            return result

    # Acceptance paths.
    if result.critique_review_present:
        result.accepted_reason = "critique-review.md present"
        return result
    if result.skip_rationale is not None:
        result.accepted_reason = f"documented skip — {result.skip_rationale}"
        return result
    if mode not in _ENFORCED_MODES:
        result.accepted_reason = f"mode {mode} does not enforce mandatory /critique-review"
        return result
    if not critic_required:
        result.accepted_reason = "critic-required is not true (no mandatory-Critic trigger)"
        return result

    # Refuse: mandatory /critique-review absent + unrationalised.
    result.violations.append(
        CRPViolation(
            kind="mandatory-critique-review-absent",
            severity="Important",
            message=(
                f"mandatory /critique-review is absent and unrationalised. "
                f"Conditions held: mode={mode} (in {{STANDARD, HEAVY}}); "
                f"critic-required=true; critique-review.md absent; "
                f"no canonical `critique-review-skip` milestone.md frontmatter key. "
                f"Run `/critique-review` for this slice, OR document a deliberate "
                f"skip by adding `critique-review-skip: \"skip — rationale: <text>\"` "
                f"to milestone.md frontmatter (per ADR-024)."
            ),
        )
    )
    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="critique_review_prerequisite_audit",
        description="CRP-1 audit: refuse /build-slice on skipped mandatory /critique-review.",
    )
    parser.add_argument("slice_folder", type=Path, help="Path to active slice folder.")
    parser.add_argument("--root", type=Path, default=None, help="Repo root (default: ancestor with .git).")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(slice_folder=args.slice_folder, repo_root=args.root)
    except Exception as e:  # noqa: BLE001 — top-level CLI guard
        print(f"critique_review_prerequisite_audit: error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.violations:
            for v in result.violations:
                print(f"[{v.severity}] {v.kind}: {v.message}")
        else:
            print(f"CRP-1 audit: clean. Accepted: {result.accepted_reason}.")

    usage_kinds = {"usage-error", "mode-unresolvable"}
    if any(v.kind in usage_kinds for v in result.violations):
        return 2
    if result.violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
