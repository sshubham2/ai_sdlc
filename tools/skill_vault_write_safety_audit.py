"""SVW-1 — skill-driven vault-write-safety audit (slice-095 / [[ADR-087]]).

The skill-driven counterpart of slice-094's VWS-1 (which AST-audits
``tools/*.py`` Python writers). SVW-1 statically scans ``skills/*/SKILL.md``
prose for any *directive* that mutates a **shared-aggregate** vault file
without routing through the ``vault_edit append`` safe channel (or carrying a
sanctioned exemption marker).

HONEST SCOPE (Critic B1 / [[ADR-029]]): SVW-1's guarantee is over the
**prose-detection surface** — no SKILL.md *prescribes* an unsafe raw mutation
of a shared file — NOT a completeness guarantee over runtime writes. Unlike
VWS-1 (an AST scan where the write op IS the ground truth), this audits a
*description of intent*; it cannot observe Claude invoking the raw
``Write``/``Edit`` tool at runtime in violation of correct prose (the R-2
class — structurally unreachable by a static audit, the LLM-prose-inspection
shape ADR-029 rejected for BC-1). There is no content-oracle for LLM-authored
vault appends, so a BCI-1-style downstream gate is unconstructible; prose
honesty + the wrapper + the cooperative model ([[ADR-067]]) are the controls.

DETECTION MODEL (fail-closed; Critic M1/M3):
  1. Shared-file set (``_SHARED_BASENAMES``) — the genuinely-concurrent vault
     files. Per-slice-folder files + distinct-filename ADR creates are NOT in
     the set (isolated by construction).
  2. Mutation-site detector — a non-fenced line where a directive verb
     (``_DIRECTIVE_VERBS``) governs (appears before) a backticked-or-
     ``architecture/``-path reference to a shared file. Bare mentions (no
     directive verb, or an un-backticked filename) are NOT sites; a verb used
     as a NOUN immediately after a code span (e.g. ``\`X.md\` edit``) is
     excluded.
  3. Verdict per site (line-local, fail-closed): CLEAN iff the line carries a
     safe-route token (``_SAFE_ROUTE_TOKENS``) OR a valid exemption marker
     ``<!-- vault-write-safe: <reason> -->`` whose ``<reason>`` is in the
     closed ``_EXEMPT_REASONS`` enum. Unrouted-and-unexempted → VIOLATION;
     an unknown exemption reason → VIOLATION. The exempt-site *allowlist*
     ``_REGISTERED_SKILL_EXEMPTIONS`` is pinned by
     ``test_exemption_allowlist_pinned`` (a NEW off-allowlist exemption trips
     a regression — closes the per-line ``# noqa`` silent-bypass vector M3).

Usage:
    python -m tools.skill_vault_write_safety_audit
    python -m tools.skill_vault_write_safety_audit --json
    python -m tools.skill_vault_write_safety_audit --root <repo-root>

Exit codes:
    0  clean (every shared-vault mutation site is routed or validly exempted)
    1  violation (>=1 unrouted/unexempted/unknown-reason site)
    2  usage error (skills/ missing, unreadable)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

# --- the shared-aggregate vault file set (genuinely concurrent mutation
# targets). ADR-*.md is EXCLUDED: each ADR is a distinct-filename NEW create
# (isolated by construction, like per-slice files), not a shared-file append.
_SHARED_BASENAMES: tuple[str, ...] = (
    "risk-register.md",
    "lessons-learned.md",
    "_index.md",
    "methodology-changelog.md",
    "shippability.md",
    "build-checks.md",
)
_SHARED_ALT = "|".join(re.escape(b) for b in _SHARED_BASENAMES)
# A shared-file reference: a backticked path ending in a shared basename, OR an
# architecture/-prefixed path ending in one. A BARE filename (no backtick, no
# architecture/ prefix) is NOT a reference (excludes reflect:386 example prose).
_SHARED_REF_RE = re.compile(
    r"`[^`\n]*(?:" + _SHARED_ALT + r")`"
    r"|architecture/[\w./-]*(?:" + _SHARED_ALT + r")"
)

# Directive verbs that, when they GOVERN a shared-file reference (appear before
# it on the line), denote a mutation. "edit" is included but a noun-usage right
# after a code span is filtered in _is_mutation_site (the build-slice:394 FP).
_DIRECTIVE_VERBS: tuple[str, ...] = (
    "append", "add", "write", "update", "regenerate", "edit",
)
_DIRECTIVE_RE = re.compile(
    r"\b(?:" + "|".join(_DIRECTIVE_VERBS) + r")\b", re.IGNORECASE
)

# Line-local CLEAN signals.
_SAFE_ROUTE_TOKENS: tuple[str, ...] = (
    "tools.vault_edit", "vault_edit append", "safe_append_text", "_vault_write",
)
_EXEMPTION_RE = re.compile(r"<!--\s*vault-write-safe:\s*([a-z0-9-]+)\s*-->")
_EXEMPT_REASONS: frozenset[str] = frozenset({
    "deferred-rmw",            # read-modify-write residual deferred to the flip slice
    "project-open-single-shot",  # project-lifecycle writer, not a parallel hazard
})

# Pinned allowlist of exempt sites (skill-relpath, reason). A NEW exemption not
# on this list trips test_exemption_allowlist_pinned (M3 — keeps "visible
# residual" enforced, not self-asserted). slice-041 _REGISTERED_* shape.
_REGISTERED_SKILL_EXEMPTIONS: frozenset[tuple[str, str]] = frozenset({
    ("skills/reflect/SKILL.md", "deferred-rmw"),          # :56 risk-status RMW, :319/:320 _index RMW
    ("skills/archive/SKILL.md", "deferred-rmw"),          # :27/:58/:75/:131/:177 _index regenerate (RMW)
    ("skills/supersede-slice/SKILL.md", "deferred-rmw"),  # :103 _index superseded-row edit (RMW)
    ("skills/discover/SKILL.md", "project-open-single-shot"),   # :113 risk-register (project open)
    ("skills/risk-spike/SKILL.md", "project-open-single-shot"),  # :148 risk-register (spike)
    # NOTE: /triage's risk-register writes (:163/:179) are NOT listed — they sit
    # inside an unclosed ```markdown fence (a pre-existing triage markdown bug:
    # the Triage-template fence at ~:142 is never closed, inverting parity for
    # the rest of the file), so the audit does not flag them. Recorded as a
    # DISCOVERED finding (build-log/reflection) for a separate fix slice. If that
    # fence is later closed, :163 surfaces → audit flags it → an off-allowlist
    # exemption would trip test_exemption_allowlist_pinned (fail-closed review).
})

_FENCE_RE = re.compile(r"^\s*```")


@dataclass(frozen=True)
class Violation:
    file: str       # repo-relative SKILL.md path
    line: int
    kind: str       # "unrouted" | "unknown-exemption-reason"
    message: str

    def to_dict(self) -> dict:
        return {"file": self.file, "line": self.line, "kind": self.kind,
                "message": self.message}


@dataclass(frozen=True)
class Exemption:
    file: str
    line: int
    reason: str

    def to_dict(self) -> dict:
        return {"file": self.file, "line": self.line, "reason": self.reason}


@dataclass
class AuditResult:
    skills_scanned: int = 0
    sites_found: int = 0
    sites_routed: int = 0
    violations: list[Violation] = field(default_factory=list)
    exemptions: list[Exemption] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "clean" if not self.violations else "violation"

    def to_dict(self) -> dict:
        return {
            "skills_scanned": self.skills_scanned,
            "sites_found": self.sites_found,
            "sites_routed": self.sites_routed,
            "violations": [v.to_dict() for v in self.violations],
            "exemptions": [e.to_dict() for e in self.exemptions],
            "status": self.status,
        }


def _is_mutation_site(line: str) -> bool:
    """A non-fenced line where a directive verb GOVERNS (precedes) a vault-scoped
    shared-file reference.

    Excludes (APED-1-tuned at slice-095 build against the real 26-skill corpus):
      - a ``~/.claude/`` GLOBAL file ref (e.g. ``~/.claude/build-checks.md``) —
        the cross-project global, NOT the ``architecture/`` vault (reflect:207).
      - a verb that is part of a hyphen-compound (``post-write`` / ``read-modify-
        write``) — the verb is a noun there, not a directive (reflect:209).
      - a verb used as a NOUN right after a code span (``\`X.md\` edit``) —
        build-slice:394.
    """
    for ref in _SHARED_REF_RE.finditer(line):
        if ".claude" in ref.group():
            continue  # global ~/.claude/ file, not the architecture/ vault
        for m in _DIRECTIVE_RE.finditer(line):
            if m.start() >= ref.start():
                continue  # verb must GOVERN (precede) the file reference
            if m.start() > 0 and line[m.start() - 1] == "-":
                continue  # hyphen-compound (post-write / read-modify-write)
            if "`" in line[max(0, m.start() - 2):m.start()]:
                continue  # noun-usage right after a code span (`X.md` edit)
            return True
    return False


def _verdict(line: str) -> tuple[str, str | None]:
    """Return (verdict, detail) for a mutation-site line.

    ("routed", None) | ("exempted", reason) | ("violation", kind).
    """
    if any(tok in line for tok in _SAFE_ROUTE_TOKENS):
        return ("routed", None)
    m = _EXEMPTION_RE.search(line)
    if m:
        reason = m.group(1)
        if reason in _EXEMPT_REASONS:
            return ("exempted", reason)
        return ("violation", "unknown-exemption-reason")
    return ("violation", "unrouted")


def _iter_skill_files(root: Path) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    return sorted(skills_dir.glob("*/SKILL.md"))


def audit_root(root: Path) -> AuditResult:
    """Scan every skills/*/SKILL.md; classify each shared-vault mutation site."""
    result = AuditResult()
    for path in _iter_skill_files(root):
        result.skills_scanned += 1
        rel = str(path.relative_to(root)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        in_fence = False
        for i, line in enumerate(text.splitlines(), start=1):
            if _FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if not _is_mutation_site(line):
                continue
            result.sites_found += 1
            verdict, detail = _verdict(line)
            if verdict == "routed":
                result.sites_routed += 1
            elif verdict == "exempted":
                result.exemptions.append(Exemption(file=rel, line=i, reason=detail))  # type: ignore[arg-type]
            else:  # violation
                if detail == "unknown-exemption-reason":
                    msg = (
                        f"exemption marker with reason not in {sorted(_EXEMPT_REASONS)} "
                        f"— a vault mutation must route through `vault_edit append` "
                        f"or carry a sanctioned exemption"
                    )
                else:
                    msg = (
                        "unrouted skill-driven mutation of a shared-aggregate vault "
                        "file — route through `vault_edit append` (append class) or "
                        "add `<!-- vault-write-safe: <reason> -->` (rewrite/project-open)"
                    )
                result.violations.append(
                    Violation(file=rel, line=i, kind=detail or "unrouted", message=msg)  # type: ignore[arg-type]
                )
    return result


def registered_exemption_pairs(root: Path) -> set[tuple[str, str]]:
    """The (skill, reason) set of exemptions actually present in the tree —
    consumed by test_exemption_allowlist_pinned to pin against
    _REGISTERED_SKILL_EXEMPTIONS."""
    return {(e.file, e.reason) for e in audit_root(root).exemptions}


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"SVW-1 skill-vault-write audit: clean. "
            f"{result.skills_scanned} skill(s) scanned; "
            f"{result.sites_found} mutation site(s) "
            f"({result.sites_routed} routed, {len(result.exemptions)} exempted).\n"
        )
    out = [
        f"SVW-1 skill-vault-write audit: {len(result.violations)} violation(s):\n\n"
    ]
    for v in result.violations:
        out.append(f"  {v.file}:{v.line} [{v.kind}] {v.message}\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="skill_vault_write_safety_audit",
        description=(
            "SVW-1 audit: every skills/*/SKILL.md directive mutating a "
            "shared-aggregate vault file must route through `vault_edit append` "
            "or carry a sanctioned exemption marker."
        ),
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="Repo root (defaults to parent of the tools/ dir containing this script)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    root = args.root.resolve() if args.root is not None else Path(__file__).resolve().parent.parent
    if not (root / "skills").exists():
        sys.stderr.write(f"skills/ directory not found at {root}\n")
        return 2

    result = audit_root(root)
    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))
    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
