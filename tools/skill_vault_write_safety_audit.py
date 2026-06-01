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

DETECTION MODEL (fail-closed for RECOGNIZED sites; Critic M1/M3, hardened at
slice-095 code-review):
  1. Shared-file set (``_SHARED_BASENAMES``) — the genuinely-concurrent vault
     files. Per-slice-folder files + distinct-filename ADR creates are NOT in
     the set (isolated by construction).
  2. Mutation-site detector — a non-fenced line where a directive verb
     (``_DIRECTIVE_VERBS``) governs (appears before) a backticked-or-
     ``architecture/``-path reference to a shared file. Bare mentions (no
     directive verb, or an un-backticked filename) are NOT sites; a verb used
     as a NOUN immediately after a code span is excluded. HONEST SCOPE (M2):
     recognition is verb-LEXICON-bounded — the guarantee is "fail-closed for
     recognized directive verbs", not a completeness oracle over every English
     phrasing; noun-prone verbs are deliberately excluded (see the
     ``_DIRECTIVE_VERBS`` residual note). Fenced regions are tracked
     CommonMark-style (char + length; m1) so real prose after a malformed
     nested fence is no longer silently dropped.
  3. Verdict per site (fail-closed): CLEAN iff the line carries a GENUINE
     safe-route reference (a route token inside a backtick code span or a
     ``<!-- route: ... -->`` marker, not locally negated — ``_is_routed``; M1)
     OR a valid exemption marker ``<!-- vault-write-safe: <reason> -->`` whose
     ``<reason>`` is in the closed ``_EXEMPT_REASONS`` enum. A BARE/negated
     route mention ("do NOT use tools.vault_edit append"), an unrouted site, or
     an unknown exemption reason → VIOLATION. The exempt-site *allowlist*
     ``_REGISTERED_SKILL_EXEMPTIONS`` is pinned at per-(file, reason) COUNT
     granularity by ``test_exemption_allowlist_pinned`` (M3): a NEW off-allowlist
     exemption OR an N+1-th marker on an already-listed file trips a regression —
     closes the per-line ``# noqa`` silent-bypass vector at site granularity.

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
    # original six
    "append", "add", "write", "update", "regenerate", "edit",
    # M2 (slice-095 code-review): common UNAMBIGUOUS mutation verbs the 6-verb
    # lexicon missed (insert/replace/... all passed CLEAN — the fail-OPEN hole
    # the design's "fail-closed" claim overstated).
    "insert", "replace", "prepend", "modify", "amend", "create",
)
# LEXICON-BOUND RESIDUAL (honest scope, M2): recognition is verb-lexicon-bounded,
# so the "fail-closed" guarantee is over RECOGNIZED directive verbs — NOT a
# completeness guarantee over every English phrasing of a mutation. Verbs that
# are commonly NOUNS adjacent to a file reference in this corpus —
# `note` ("**Note** on…"), `record` ("reflection record"), `set`, `log`,
# `mark`, `put` — are deliberately EXCLUDED: adding them false-positives on
# descriptive prose (e.g. slice:34, slice:221) without a fragile noun/verb
# disambiguator. A raw write phrased SOLELY with such a noun-prone verb is a
# documented residual, not a silent gap. (`register` is excluded for a harder
# reason: `\bregister\b` matches inside `risk-register.md` itself.)
_DIRECTIVE_RE = re.compile(
    r"\b(?:" + "|".join(_DIRECTIVE_VERBS) + r")\b", re.IGNORECASE
)

# Line-local CLEAN signals. A safe-route reference is a route token that
# appears INSIDE a backtick code span (the corpus convention `tools.vault_edit
# append` / `$PY -m tools.vault_edit ...`) OR inside an HTML route marker
# `<!-- route: ... -->`. A BARE prose mention of a route token does NOT clean a
# mutation site — it is description, not a routing instruction (M1, slice-095
# code-review): "...raw (do NOT use tools.vault_edit append)", "NOT via
# safe_append_text", "predates _vault_write" must all stay VIOLATION.
_SAFE_ROUTE_TOKENS: tuple[str, ...] = (
    "tools.vault_edit", "vault_edit append", "safe_append_text", "_vault_write",
)
_ROUTE_TOKEN_ALT = "|".join(re.escape(t) for t in _SAFE_ROUTE_TOKENS)
# A route token inside a backtick code span.
_ROUTE_IN_CODESPAN_RE = re.compile(r"`[^`\n]*(?:" + _ROUTE_TOKEN_ALT + r")[^`\n]*`")
# A route token inside an HTML `<!-- route: ... -->` marker (end-of-line form
# used by reflect/reduce — the route token is not backticked there).
_ROUTE_MARKER_RE = re.compile(
    r"<!--\s*route:[^>]*(?:" + _ROUTE_TOKEN_ALT + r")[^>]*-->"
)
# A negation GOVERNING a route reference (within the ~2 words immediately before
# it) demotes that reference: "do NOT use `tools.vault_edit append`" /
# "NOT via `safe_append_text`" are not routes. The look-back is deliberately
# SHORT so a trailing safety assertion that governs the RAW write — "never a
# raw `Write`/`Edit`", which sits AFTER the route token — never demotes a
# genuine route (the slice-095 corpus FP shape the build was tuned against).
_NEG_LOOKBACK_WORDS = 2
_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|none|without|bypass(?:es|ing)?|predates)\b"
    r"|n't|\binstead\s+of\b",
    re.IGNORECASE,
)
_EXEMPTION_RE = re.compile(r"<!--\s*vault-write-safe:\s*([a-z0-9-]+)\s*-->")
_EXEMPT_REASONS: frozenset[str] = frozenset({
    "deferred-rmw",            # read-modify-write residual deferred to the flip slice
    "project-open-single-shot",  # project-lifecycle writer, not a parallel hazard
})

# Pinned allowlist of exempt sites at per-(file, reason) COUNT granularity
# (M3, slice-095 code-review). Pinning the COUNT — not just the (file, reason)
# PAIR — means adding an N+1-th exemption marker to an ALREADY-listed file trips
# test_exemption_allowlist_pinned. The prior pair-set pin let a future editor add
# unlimited new `deferred-rmw` markers to reflect/archive (pair already listed) —
# including next to a genuinely-unsafe append — without tripping the regression.
# slice-041 _REGISTERED_* shape. Total across all pairs == the audit's exemption
# count (currently 12).
_REGISTERED_SKILL_EXEMPTIONS: dict[tuple[str, str], int] = {
    ("skills/reflect/SKILL.md", "deferred-rmw"): 3,          # :56 risk-status RMW + :321/:322 _index RMW
    ("skills/archive/SKILL.md", "deferred-rmw"): 5,          # :27/:58/:75/:131/:177 _index regenerate (RMW)
    ("skills/supersede-slice/SKILL.md", "deferred-rmw"): 1,  # :103 _index superseded-row edit (RMW)
    ("skills/discover/SKILL.md", "project-open-single-shot"): 1,    # :113 risk-register (project open)
    ("skills/risk-spike/SKILL.md", "project-open-single-shot"): 1,  # :148 risk-register (spike)
    ("skills/triage/SKILL.md", "project-open-single-shot"): 1,      # :179 risk-register (project open) — surfaced by the m1 CommonMark fence fix; this line renders OUTSIDE the triage.md template fence
    # NOTE: /triage's OTHER risk-register write (:163) stays fence-HIDDEN — it sits
    # INSIDE the triage.md template block (between the :142 ```markdown opener and
    # the :165 nested block), so the audit does not see it. That is the separate,
    # still-deferred triage-markdown bug (a DISCOVERED finding for its own fix
    # slice), NOT an SVW-1 gap. If that template fence is later repaired, :163
    # surfaces → the audit flags it → an off-allowlist exemption (or a bumped
    # count here) trips test_exemption_allowlist_pinned (fail-closed review).
}

# CommonMark fenced code block: 0+ leading spaces, then a run of >=3 backticks
# or >=3 tildes, then an optional info string. m1 (slice-095 code-review):
# match `~~~` too AND track the opener's fence char + length so a fence closes
# only on the SAME char at >= the opener length with no trailing content — a
# `~~~` line inside a ``` block (or a ```lang info-string line as content) no
# longer blindly inverts parity. (Blockquoted `> ``` ` fences stay out of scope
# — the corpus uses none; documented residual.)
_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")


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
      - a verb used as a NOUN right after a code span (the build-slice:394
        "SKILL.md edit + risk-register.md flip" descriptive-prose shape).
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


def _is_routed(line: str) -> bool:
    """True iff the line carries a GENUINE safe-route reference.

    A route token counts only when it appears inside a backtick code span or an
    HTML ``<!-- route: ... -->`` marker (the two corpus conventions), AND is not
    locally negated. M1 (slice-095 code-review): a bare prose mention
    ("do NOT use tools.vault_edit append", "NOT via safe_append_text",
    "predates _vault_write") is description, not routing, and must NOT
    false-CLEAN; a backticked-but-negated reference is likewise demoted. The
    ~2-word look-back keeps a downstream "never a raw ``Write``/``Edit``" safety
    assertion (which governs the RAW write, not the route token) CLEAN.
    """
    for m in list(_ROUTE_IN_CODESPAN_RE.finditer(line)) + list(
        _ROUTE_MARKER_RE.finditer(line)
    ):
        preceding = " ".join(line[: m.start()].split()[-_NEG_LOOKBACK_WORDS:])
        if _NEGATION_RE.search(preceding):
            continue  # negation governs this route reference — not a real route
        return True
    return False


def _verdict(line: str) -> tuple[str, str | None]:
    """Return (verdict, detail) for a mutation-site line.

    ("routed", None) | ("exempted", reason) | ("violation", kind).
    """
    if _is_routed(line):
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
        fence_marker = ""  # the open fence's char-run (e.g. "```"); "" when closed
        for i, line in enumerate(text.splitlines(), start=1):
            fm = _FENCE_RE.match(line)
            if fm:
                ticks, rest = fm.group(1), fm.group(2)
                if not in_fence:
                    # A backtick fence opener may not carry a backtick in its
                    # info string (CommonMark) — an inline ``` `x` ``` is content.
                    if ticks[0] == "`" and "`" in rest:
                        pass  # not a valid opener — fall through to site check
                    else:
                        in_fence = True
                        fence_marker = ticks
                        continue
                elif (
                    ticks[0] == fence_marker[0]
                    and len(ticks) >= len(fence_marker)
                    and rest.strip() == ""
                ):
                    in_fence = False  # closer: same char, >= length, no content
                    fence_marker = ""
                    continue
                else:
                    continue  # fence-shaped line that is content of the open fence
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


def registered_exemption_counts(root: Path) -> dict[tuple[str, str], int]:
    """The per-(skill, reason) COUNT of exemptions actually present in the tree —
    consumed by test_exemption_allowlist_pinned to pin against
    _REGISTERED_SKILL_EXEMPTIONS at site-count granularity (M3). Adding an
    N+1-th exemption marker to an already-listed (skill, reason) changes its
    count here and trips the pin (the pair-set pin could not)."""
    counts: dict[tuple[str, str], int] = {}
    for e in audit_root(root).exemptions:
        key = (e.file, e.reason)
        counts[key] = counts.get(key, 0) + 1
    return counts


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
