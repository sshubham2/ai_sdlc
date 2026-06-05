"""Drift-check enforcement audit (DCE-1).

Refuses `/build-slice` Step 6 when no `/drift-check` was run for the active
slice — closing the silent-skip gap. `/drift-check` was the only pipeline
discipline preached (CLAUDE.md "Run /drift-check before commit") and listed
in `/build-slice` Step 6 yet enforced by nothing: there was no
`tools/drift_check_audit.py` and no installed pre-commit hook, only an
honor-system `- [ ] /drift-check passes` checkbox (the R-7 / slice-022
silent-disable failure class).

Per DCE-1 (methodology-changelog.md v0.76.0; ADR-073). DCE-1 is an
**audit-enforced gate** (its programmatic gate is this module), so per
ADR-019's test-pinned naming note it carries the bare `DCE-1` form
(NO `-D` suffix). Naming-class peers: BC-1, CRP-1, PCA-1, BCI-1, MCFS-1,
STP-1, AVFS-1, TVFS-1, NAW-1.

Scope honesty (ADR-073 § Scope honesty, per slice-081 /critique M2): this
is a *was-it-MARKED* gate, not a was-it-RUN gate. It enforces that a
slice-referencing `architecture/drift-log.md` entry exists — which a slice
could in principle satisfy by writing the entry without performing the
semantic check. What it structurally closes is the silent-skip hole (a
slice finishing with NO drift-check trace at all). The semantic
vault-vs-code drift reading remains Claude's irreducible judgement via the
`/drift-check` skill. (Residual gap disclosed in the manner of NAW-1's
known-false-positive disclosure.)

Marker match (line-anchored + slice-anchored, per /critique B1 +
/critique-review M-add-1): the audit scans `architecture/drift-log.md`
**only on lines beginning `**Trigger**:`** and, on such a line, matches the
current slice number via `\bslice[- ]?0*<N>\b` (both-side anchored — left `\b`
per slice-081 /code-review m1 rejects `xslice-081`/`subslice-081`). The `**Trigger**:`-line anchor
is load-bearing — drift-log.md is append-only and routinely cross-mentions
OTHER slice numbers in `**Scope**` / Notes / Resolutions / `## Audit
(slice-NNN …)` heading lines; a bare whole-file scan would false-ACCEPT a
slice merely *mentioned* by a prior entry, silently defeating the gate (the
opposite, worse failure direction from M2). Mirrors CRP-1's keyed-not-
substring discipline (ADR-024).

Refuse condition (exit 1, `drift-check-not-run`):
    mode in {STANDARD, HEAVY}
    AND no `**Trigger**:` line in drift-log.md references the slice number
    AND no canonical `drift-check-skip` frontmatter key in milestone.md

Accept (exit 0): a slice-referencing `**Trigger**:` line present, OR canonical
`drift-check-skip` value present, OR mode == MINIMAL.

Malformed-skip (exit 1, Important, `escape-hatch-malformed`):
`drift-check-skip` frontmatter key present but value does NOT match
`^skip — rationale: .+`. Detection is keyed on the *frontmatter key*
(not a body substring scan) — eliminates the BRANCH-1-style narrative-prose
false-positive risk (per ADR-024 / CRP-1 precedent).

Mode resolution (per CRP-1 / ADR-024):
1. Primary: `architecture/triage.md` frontmatter `mode:` value.
2. Fallback: `CLAUDE.md` `**Mode**:` line.
3. STOP (exit 2 usage-error) if neither resolves.

Usage:
    python -m tools.drift_check_audit <slice-folder>
    python -m tools.drift_check_audit --json <slice-folder>
    python -m tools.drift_check_audit --root <repo-root> <slice-folder>

Exit codes:
    0  clean (accept — drift-check marker present / documented-skip / mode==MINIMAL)
    1  violations (drift-check marker absent + unrationalised, or malformed skip)
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
from tools._vault_paths import VAULT_ROOT

# Canonical regex for the milestone.md `drift-check-skip:` frontmatter value.
# Byte-faithful clone of CRP-1's `_SKIP_VALUE_RE` (em-dash `—`, NOT a hyphen;
# tools/critique_review_prerequisite_audit.py:69) — same `rationale:` spirit as
# BRANCH-1 / ADR-024. Pinned in skills/build-slice/SKILL.md Step 7b preserved-keys
# and asserted by tests/methodology/test_drift_check_audit.py.
_SKIP_VALUE_RE = re.compile(r"^skip — rationale: .+")

# Modes for which a mandatory /drift-check is enforced. MINIMAL skips drift-check
# by default (skills/drift-check/SKILL.md "In Minimal mode: skipped by default").
_ENFORCED_MODES = {"STANDARD", "HEAVY"}

_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")

# A drift-log.md line is a Trigger line iff it begins (modulo leading whitespace)
# with the literal `**Trigger**:`. Only Trigger lines are scanned for the slice
# number (M-add-1 line-anchor).
_TRIGGER_LINE_RE = re.compile(r"^\s*\*\*Trigger\*\*\s*:")


@dataclass(frozen=True)
class DCEViolation:
    kind: str       # "drift-check-not-run" | "escape-hatch-malformed" |
                    # "usage-error" | "mode-unresolvable"
    severity: str   # "Important" (all DCE-1 violations refuse)
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    slice_folder: str = ""
    repo_root: str = ""
    slice_number: str = ""
    resolved_mode: str = ""
    drift_marker_present: bool = False
    skip_key_present: bool = False
    skip_rationale: str | None = None
    accepted_reason: str = ""
    violations: list[DCEViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "DCE-1",
            "slice_folder": self.slice_folder,
            "repo_root": self.repo_root,
            "slice_number": self.slice_number,
            "resolved_mode": self.resolved_mode,
            "drift_marker_present": self.drift_marker_present,
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

    Byte-faithful clone of CRP-1's helper (minimal-dependency scalar reads).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[1:idx])
    return None


def _frontmatter_value(block: str, key: str) -> str | None:
    """Return the raw string value for `key:` in a frontmatter block, or None.

    Byte-faithful clone of CRP-1's helper.
    """
    pat = re.compile(rf"^{re.escape(key)}\s*:\s*(.*?)\s*$", re.MULTILINE)
    m = pat.search(block)
    if not m:
        return None
    val = m.group(1).strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in {'"', "'"}:
        val = val[1:-1]
    return val


def _resolve_mode(repo_root: Path) -> str | None:
    """Resolve pipeline mode.

    Byte-faithful clone of CRP-1's `_resolve_mode` (VAULT_ROOT-routed triage.md,
    then CLAUDE.md `**Mode**:` fallback). Returns an uppercased mode or None.
    """
    triage = repo_root / VAULT_ROOT / "triage.md"  # VAULT_ROOT-routed (slice-068)
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


def _drift_marker_present(repo_root: Path, slice_number: str) -> bool:
    """True iff a `**Trigger**:` line in drift-log.md references the slice number.

    Line-anchored (only `**Trigger**:` lines) + slice-anchored
    (`slice[- ]?0*<N>\\b`) per /critique B1 + /critique-review M-add-1. A missing
    drift-log.md is treated as "no marker" (NOT a usage error) — a repo that never
    ran /drift-check is legitimately refused, not errored.
    """
    drift_log = repo_root / VAULT_ROOT / "drift-log.md"
    if not drift_log.exists():
        return False
    n = int(slice_number)  # strip zero-padding: "081" -> 81
    # Left `\b` (per slice-081 /code-review m1): without it `slice` matches as a
    # bare substring, so `xslice-081` / `subslice-081` would false-ACCEPT. The
    # left `\b` still admits line-start and post-`: `/post-space cases (boundary
    # between a non-word char and `s`).
    slice_re = re.compile(rf"\bslice[- ]?0*{n}\b")
    for line in drift_log.read_text(encoding="utf-8").splitlines():
        if _TRIGGER_LINE_RE.match(line) and slice_re.search(line):
            return True
    return False


def audit(slice_folder: Path, repo_root: Path | None = None) -> AuditResult:
    """Run the DCE-1 audit against a slice folder."""
    slice_folder = Path(slice_folder).resolve()
    if not slice_folder.exists():
        return AuditResult(
            slice_folder=str(slice_folder),
            violations=[
                DCEViolation(
                    kind="usage-error",
                    severity="Important",
                    message=f"slice folder not found: {slice_folder}",
                )
            ],
        )

    # Extract slice number from folder name.
    m = _SLICE_FOLDER_RE.match(slice_folder.name)
    if not m:
        return AuditResult(
            slice_folder=str(slice_folder),
            violations=[
                DCEViolation(
                    kind="usage-error",
                    severity="Important",
                    message=(
                        f"slice folder name {slice_folder.name!r} does not match "
                        f"the canonical `slice-NNN-<name>` shape."
                    ),
                )
            ],
        )
    slice_number = m.group(1)

    # Resolve repo_root if not provided (byte-faithful clone of CRP-1).
    if repo_root is None:
        from tools._vault_git import resolve_repo_root_for_slice
        repo_root = resolve_repo_root_for_slice(slice_folder)
        if repo_root is None:
            return AuditResult(
                slice_folder=str(slice_folder),
                slice_number=slice_number,
                violations=[
                    DCEViolation(
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
        slice_number=slice_number,
    )

    milestone = slice_folder / "milestone.md"
    if not milestone.exists():
        result.violations.append(
            DCEViolation(
                kind="usage-error",
                severity="Important",
                message=f"milestone.md not found in slice folder: {slice_folder}",
            )
        )
        return result

    block = _frontmatter_block(milestone.read_text(encoding="utf-8"))
    if block is None:
        result.violations.append(
            DCEViolation(
                kind="usage-error",
                severity="Important",
                message="milestone.md has no YAML frontmatter block (cannot read drift-check-skip)",
            )
        )
        return result

    # Resolve mode.
    mode = _resolve_mode(repo_root)
    if mode is None:
        result.violations.append(
            DCEViolation(
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

    # Escape-hatch: drift-check-skip frontmatter key (keyed, not body-scanned).
    skip_val = _frontmatter_value(block, "drift-check-skip")
    result.skip_key_present = skip_val is not None
    if skip_val is not None:
        if _SKIP_VALUE_RE.match(skip_val):
            result.skip_rationale = skip_val
        else:
            result.violations.append(
                DCEViolation(
                    kind="escape-hatch-malformed",
                    severity="Important",
                    message=(
                        f"milestone.md `drift-check-skip:` key present but value "
                        f"{skip_val!r} does not match canonical shape "
                        f"`skip — rationale: <text>` (per ADR-073 / "
                        f"skills/build-slice/SKILL.md Step 7b)."
                    ),
                )
            )
            return result

    # drift-log marker presence (line-anchored + slice-anchored).
    result.drift_marker_present = _drift_marker_present(repo_root, slice_number)

    # Acceptance paths.
    if result.drift_marker_present:
        result.accepted_reason = (
            f"drift-log.md has a `**Trigger**:` line referencing slice-{slice_number}"
        )
        return result
    if result.skip_rationale is not None:
        result.accepted_reason = f"documented skip — {result.skip_rationale}"
        return result
    if mode not in _ENFORCED_MODES:
        result.accepted_reason = f"mode {mode} does not enforce mandatory /drift-check"
        return result

    # Refuse: mandatory /drift-check absent + unrationalised.
    result.violations.append(
        DCEViolation(
            kind="drift-check-not-run",
            severity="Important",
            message=(
                f"no /drift-check marker for slice-{slice_number}. Conditions held: "
                f"mode={mode} (in {{STANDARD, HEAVY}}); no `**Trigger**:` line in "
                f"architecture/drift-log.md references slice-{slice_number}; "  # NOT VAULT_ROOT-routed (slice-068) — error-message prose
                f"no canonical `drift-check-skip` milestone.md frontmatter key. "
                f"Run `/drift-check` (full mode) for this slice — it appends a "
                f"`**Trigger**: slice-{slice_number} pre-finish gate` entry to "
                f"architecture/drift-log.md — OR document a deliberate skip by adding "  # NOT VAULT_ROOT-routed (slice-068) — error-message prose
                f"`drift-check-skip: \"skip — rationale: <text>\"` to milestone.md "
                f"frontmatter (per ADR-073)."
            ),
        )
    )
    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="drift_check_audit",
        description="DCE-1 audit: refuse /build-slice when no /drift-check was run for the slice.",
    )
    parser.add_argument("slice_folder", type=Path, help="Path to active slice folder.")
    parser.add_argument("--root", type=Path, default=None, help="Repo root (default: ancestor with .git).")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(slice_folder=args.slice_folder, repo_root=args.root)
    except Exception as e:  # noqa: BLE001 — top-level CLI guard
        print(f"drift_check_audit: error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.violations:
            for v in result.violations:
                print(f"[{v.severity}] {v.kind}: {v.message}")
        else:
            print(f"DCE-1 audit: clean. Accepted: {result.accepted_reason}.")

    usage_kinds = {"usage-error", "mode-unresolvable"}
    if any(v.kind in usage_kinds for v in result.violations):
        return 2
    if result.violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
