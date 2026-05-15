"""Pipeline-chain auto-advance audit (PCA-1).

Verifies the per-slice pipeline loop is correctly wired for auto-advance:
every covered skill carries a well-formed `## Pipeline position` block, the
declared successor edges match the canonical chain, and the terminal
boundary (`reflect` -> `/commit-slice`, and `commit-slice` itself) is marked
`auto-advance: false` so `/commit-slice` is never auto-invoked.

Per PCA-1 (methodology-changelog.md v0.41.0). PCA-1 is an
**audit-enforced gate** (its programmatic gate is this module), so per
ADR-019's test-pinned naming note it carries the bare `PCA-1` form
(NO `-D` suffix). Naming-class peers: BC-1, CAD-1, PMI-1, INST-1, WIRE-1,
BRANCH-1, UTF8-STDOUT-1, CRP-1.

Canonical chain (the per-slice loop). `(successor, auto-advance)`:

    slice           -> /design-slice    (auto-advance: true)
    design-slice    -> /critique        (auto-advance: true)
    critique        -> /critique-review (auto-advance: true)   [1]
    critique-review -> /critique         (auto-advance: true)   [2]
    build-slice     -> /validate-slice  (auto-advance: true)
    validate-slice  -> /reflect         (auto-advance: true)
    reflect         -> /commit-slice    (auto-advance: false)  [3]
    commit-slice    -> /slice           (auto-advance: false)  [4]

[1] `/critique`'s primary successor is `/critique-review` (mandatory in
    Standard mode for methodology surfaces). The post-TRI-1 hop to
    `/build-slice` (on CLEAN/NEEDS-FIXES) and the `/critique` ->
    `/critique` self-loop on BLOCKED are verdict-dependent and expressed
    in `on-clean-completion` prose, not the flat `successor:` field. This
    audit reads `successor:` for chain-shape and DOES NOT flag the
    documented post-TRI-1 or BLOCKED edges (per /critique-review m-add-1).
[2] `/critique-review` hands back to `/critique` Step 4.5 (TRI-1) — its
    successor edge points to `/critique`; TRI-1 is the user-input HALT
    where both passes are reconciled before `/build-slice`.
[3] `reflect` is the terminal-before-commit: `auto-advance: false`. Its
    successor names `/commit-slice` but the chain HALTS — the user
    invokes `/commit-slice` manually.
[4] `commit-slice` is out of the auto-advance loop entirely
    (`auto-advance: false`); it is never an auto-advance target.

Refuse conditions (exit 1):
    malformed-block      : `## Pipeline position` section absent or a
                           required field missing/unparseable.
    successor-mismatch   : declared `successor:` != canonical successor.
    auto-advance-mismatch: declared `auto-advance:` != canonical value
                           (this is the `/commit-slice`-never-auto-invoked
                           terminal guarantee).

Usage:
    python -m tools.pipeline_chain_audit
    python -m tools.pipeline_chain_audit --json
    python -m tools.pipeline_chain_audit --root <repo-root>

Exit codes:
    0  clean (all 8 blocks well-formed + edges match canonical chain)
    1  violations (malformed block / successor mismatch / auto-advance mismatch)
    2  usage error (repo root unresolvable, skills/ dir or a SKILL.md missing)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import _stdout

# Canonical per-slice loop. Order is the chain order (used for output).
# value = (canonical successor command, canonical auto-advance bool)
_CANONICAL_CHAIN: tuple[tuple[str, str, bool], ...] = (
    ("slice", "/design-slice", True),
    ("design-slice", "/critique", True),
    ("critique", "/critique-review", True),
    ("critique-review", "/critique", True),
    ("build-slice", "/validate-slice", True),
    ("validate-slice", "/reflect", True),
    ("reflect", "/commit-slice", False),
    ("commit-slice", "/slice", False),
)

_SECTION_RE = re.compile(r"^##\s+Pipeline position\s*$", re.MULTILINE)
_NEXT_H2_RE = re.compile(r"^##\s+", re.MULTILINE)
# `- **key**: value`  (value may carry backticks / slashes / prose)
_FIELD_RE = re.compile(
    r"^-\s+\*\*(?P<key>[^*]+?)\*\*\s*:\s*(?P<val>.*?)\s*$", re.MULTILINE
)

_REQUIRED_FIELDS = ("predecessor", "successor", "auto-advance", "on-clean-completion")


@dataclass(frozen=True)
class PCAViolation:
    kind: str       # "malformed-block" | "successor-mismatch" |
                    # "auto-advance-mismatch" | "usage-error"
    severity: str   # "Important" (all PCA-1 violations refuse)
    skill: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    repo_root: str = ""
    skills_checked: list[str] = field(default_factory=list)
    violations: list[PCAViolation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rule": "PCA-1",
            "repo_root": self.repo_root,
            "skills_checked": self.skills_checked,
            "violations": [v.to_dict() for v in self.violations],
            "summary": {
                "violation_count": len(self.violations),
                "clean": not self.violations,
            },
        }


def _norm_cmd(raw: str) -> str:
    """Normalize a successor cell to a `/skill` command token.

    Strips markdown backticks/bold and surrounding prose, keeps the first
    `/skill`-shaped token. E.g. "invoke `/design-slice` via Skill" -> "/design-slice".
    """
    cleaned = raw.replace("`", "").replace("*", "")
    m = re.search(r"/([a-z][a-z0-9-]+)", cleaned)
    return f"/{m.group(1)}" if m else cleaned.strip()


def _norm_bool(raw: str) -> bool | None:
    """Parse an auto-advance cell to a bool, or None if unparseable."""
    cleaned = raw.replace("`", "").replace("*", "").strip().lower()
    m = re.match(r"(true|false)\b", cleaned)
    if not m:
        return None
    return m.group(1) == "true"


def _extract_section(text: str) -> str | None:
    """Return the `## Pipeline position` section body, or None if absent."""
    m = _SECTION_RE.search(text)
    if not m:
        return None
    start = m.end()
    nxt = _NEXT_H2_RE.search(text, start)
    return text[start : nxt.start()] if nxt else text[start:]


def _parse_fields(section: str) -> dict[str, str]:
    """Return the first occurrence of each `- **key**: value` field."""
    out: dict[str, str] = {}
    for fm in _FIELD_RE.finditer(section):
        key = fm.group("key").strip().lower()
        if key not in out:
            out[key] = fm.group("val").strip()
    return out


def audit(repo_root: Path | None = None) -> AuditResult:
    """Run the PCA-1 audit against the in-repo skills/ tree."""
    if repo_root is None:
        here = Path(__file__).resolve()
        for parent in [here] + list(here.parents):
            if (parent / ".git").exists():
                repo_root = parent
                break
        else:
            return AuditResult(
                violations=[
                    PCAViolation(
                        kind="usage-error",
                        severity="Important",
                        skill="",
                        message=f"no .git directory found above {here}",
                    )
                ]
            )

    repo_root = Path(repo_root).resolve()
    result = AuditResult(repo_root=str(repo_root))

    skills_dir = repo_root / "skills"
    if not skills_dir.is_dir():
        result.violations.append(
            PCAViolation(
                kind="usage-error",
                severity="Important",
                skill="",
                message=f"skills/ directory not found at {skills_dir}",
            )
        )
        return result

    for skill, exp_succ, exp_auto in _CANONICAL_CHAIN:
        result.skills_checked.append(skill)
        skill_md = skills_dir / skill / "SKILL.md"
        if not skill_md.is_file():
            result.violations.append(
                PCAViolation(
                    kind="usage-error",
                    severity="Important",
                    skill=skill,
                    message=f"SKILL.md not found: {skill_md}",
                )
            )
            continue

        text = skill_md.read_text(encoding="utf-8")
        section = _extract_section(text)
        if section is None:
            result.violations.append(
                PCAViolation(
                    kind="malformed-block",
                    severity="Important",
                    skill=skill,
                    message=(
                        f"`## Pipeline position` section absent in "
                        f"skills/{skill}/SKILL.md (PCA-1 requires it on all "
                        f"8 covered skills)"
                    ),
                )
            )
            continue

        fields = _parse_fields(section)
        missing = [k for k in _REQUIRED_FIELDS if k not in fields]
        # "user-input gates" is a parent label, not a `key: value` pair —
        # require the literal bold label is present in the section.
        if "**user-input gates**" not in section:
            missing.append("user-input gates")
        if missing:
            result.violations.append(
                PCAViolation(
                    kind="malformed-block",
                    severity="Important",
                    skill=skill,
                    message=(
                        f"`## Pipeline position` block in skills/{skill}/"
                        f"SKILL.md missing required field(s): "
                        f"{', '.join(missing)}"
                    ),
                )
            )
            continue

        got_succ = _norm_cmd(fields["successor"])
        if got_succ != exp_succ:
            result.violations.append(
                PCAViolation(
                    kind="successor-mismatch",
                    severity="Important",
                    skill=skill,
                    message=(
                        f"skills/{skill}/SKILL.md `## Pipeline position` "
                        f"successor is {got_succ!r}; canonical chain "
                        f"requires {exp_succ!r}"
                    ),
                )
            )

        got_auto = _norm_bool(fields["auto-advance"])
        if got_auto is None:
            result.violations.append(
                PCAViolation(
                    kind="malformed-block",
                    severity="Important",
                    skill=skill,
                    message=(
                        f"skills/{skill}/SKILL.md `## Pipeline position` "
                        f"auto-advance value {fields['auto-advance']!r} is "
                        f"not parseable as true|false"
                    ),
                )
            )
        elif got_auto != exp_auto:
            result.violations.append(
                PCAViolation(
                    kind="auto-advance-mismatch",
                    severity="Important",
                    skill=skill,
                    message=(
                        f"skills/{skill}/SKILL.md `## Pipeline position` "
                        f"auto-advance is {got_auto}; canonical requires "
                        f"{exp_auto} "
                        + (
                            "(terminal boundary — /commit-slice must never "
                            "be auto-invoked)"
                            if not exp_auto
                            else ""
                        )
                    ),
                )
            )

    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="pipeline_chain_audit",
        description=(
            "PCA-1 audit: verify the 8-skill pipeline-chain auto-advance "
            "directives match the canonical loop."
        ),
    )
    parser.add_argument(
        "--root", type=Path, default=None, help="Repo root (default: ancestor with .git)."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(repo_root=args.root)
    except Exception as e:  # noqa: BLE001 — top-level CLI guard
        print(f"pipeline_chain_audit: error: {e}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.violations:
            for v in result.violations:
                tag = f"{v.skill}: " if v.skill else ""
                print(f"[{v.severity}] {v.kind}: {tag}{v.message}")
        else:
            print(
                f"PCA-1 audit: clean. {len(result.skills_checked)} skills "
                f"checked; pipeline chain matches canonical loop."
            )

    if any(v.kind == "usage-error" for v in result.violations):
        return 2
    if result.violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
