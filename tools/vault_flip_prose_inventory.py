"""Vault-flip PROSE inventory (slice-107 / [[ADR-096]] + [[ADR-097]]).

The prose-surface analog of ``tools/vault_flip_readiness_audit.py`` (which covers
the Python production + tests surfaces). Markdown has NO AST, so classification is
line-context-driven. Read-only inventory; the flip is NOT performed here.

THE SURFACE — operational/installed prose that hardcodes the vault *location* for an
external reader: ``skills/**/SKILL.md`` + ``agents/*.md`` + root ``CLAUDE.md`` +
``INSTALL.md`` + ``README.md``. Vault-internal prose (``architecture/**/*.md``) is
OUT of scope (it relocates *with* the vault).

MATCH RULE (B1 / slice-107 dual review) — **boundary-free** ``(?:architecture|
diagnose-out)/`` scanned with ``re.finditer`` (ALL matches per line). Deliberately
NOT the anchored ``readiness_audit._SLASHED_RE`` (delimiter class ``[\\s'"(/=]`` — no
backtick), which catches only 69 of 318 on the real corpus: the 216 backtick-wrapped
inline-code paths + the operational ``:(exclude)architecture/...`` git-pathspecs are
invisible to it, yet they break at the M4 flip. ``re.finditer`` (not one ``re.search``
per line) is load-bearing: 24 lines carry >1 match (32 extra occurrences;
``code-review.md:103`` carries 5), so a per-line single match would undercount 318→286.

CLASSIFICATION — context-aware ordered ruleset. The in-code state is column-anchored
PER MATCH (`_in_inline_code(line, col)`); the marker detectors (pathspec / anchor /
verb) are LINE-anchored, never a whole-FILE substring scan (AP-1) — so on a multi-match
line a marker governs every match on that line (harmless on the current corpus where
same-line matches share a class; m1). RECALIBRATED at build-time against the real corpus
(user-ratified deviation, build-log 2026-06-03; see design.md §Build-time
recalibration): an in-code / fenced / operational vault path defaults to
``rewrite-at-flip`` — the dominant case (a LIVE reference the M4 flip must update).
B2's goal is preserved: an operational path lands ON the checklist, NEVER the
off-checklist ``doc-example``. ``doc-example`` is RESERVED for genuine plain prose.
Order (first applicable wins):

  0. disposition override (``_DISPOSITION``, [[ADR-097]]) — keyed on the 5-tuple
     ``(relpath, normalized-line, fence-state, ordinal-among-identical-lines,
     column-offset)``; resolves a curated literal WITHOUT editing prose.
  1. git-pathspec literal (``:(exclude)``/``:(glob)``/``:(top)`` …)        → rewrite-at-flip
  2. genuine historical-anchor preserve-marker on the line ("historical
     anchor" / "Glob discoverability" / "preserved as …") AND the literal
     is in-code → ``needs-human`` (a true rewrite-vs-preserve conflict; the
     ONLY auto-route to needs-human, resolved via ``_DISPOSITION``).
  3. genuine preserve-marker AND the literal is plain prose                → historical-anchor
  4. in-code (inline backticks OR fenced) OR an operational verb on the line → rewrite-at-flip
  5. plain prose mention (not in code, no signal)                          → doc-example

On the current corpus the ruleset yields **318 rewrite-at-flip / 0 historical-anchor /
0 doc-example / 0 needs-human** — every operational prose reference to the vault
location goes stale at the M4 flip, so all 318 are rewrite-at-flip; doc-example,
historical-anchor, and needs-human are all empty on this corpus (the classes exist for
future drift / other surfaces). The ``_DISPOSITION`` table + needs-human bucket remain
the fail-closed mechanism for future drift. ``--strict`` pins the ``rewrite-at-flip`` + ``needs-human`` multiset
baseline + a per-class total-count floor (m2 — catches a silent
``rewrite-at-flip → doc-example`` demotion).

DOCUMENTED RESIDUAL (B1 + m-add-1) — a bare ``architecture``/``diagnose-out`` dir
*argument* with NO slash (e.g. ``graphify vault architecture``) is invisible to any
slashed match; ``_RESIDUAL`` enumerates the bounded set (never a silent gap).

Usage:
    python -m tools.vault_flip_prose_inventory [--json] [--strict] [--repo-root <root>]

Exit codes (mirrors readiness_audit): 0 clean (no needs-human; under --strict no
baseline drift / no count-floor shrink) · 2 gate · 1 usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

# ── classes (m1: deliberately DISTINCT from readiness_audit's class strings) ──
REWRITE_AT_FLIP = "rewrite-at-flip"
HISTORICAL_ANCHOR = "historical-anchor"
DOC_EXAMPLE = "doc-example"
NEEDS_HUMAN = "needs-human"
_ALL_CLASSES = (REWRITE_AT_FLIP, HISTORICAL_ANCHOR, DOC_EXAMPLE, NEEDS_HUMAN)
# the classes whose (relpath, value) multiset is the regression baseline (AC3)
_BASELINE_CLASSES = (REWRITE_AT_FLIP, NEEDS_HUMAN)

# ── the prose surface ─────────────────────────────────────────────────────────
_PROSE_GLOBS = ("skills/**/SKILL.md", "agents/*.md", "CLAUDE.md", "INSTALL.md", "README.md")

# ── match rule (boundary-free PREFIX — guarantees the grep-equal count) ────────
_MATCH_RE = re.compile(r"(?:architecture|diagnose-out)/")
# full path token (for the stable `value`); does NOT affect the match count
_PATH_TOKEN_RE = re.compile(r"(?:architecture|diagnose-out)/[^\s`'\"()\\|,]*")

# ── operational verb / path-sink vocabulary (B2 — the corpus's real set; a
# generous set errs toward rewrite-at-flip, the SAFE direction — a vault path that
# is on the checklist when it didn't need to be costs a human a glance at flip; the
# dangerous direction (a real path silently OFF the checklist) is what B2 closes) ──
_OP_VERBS = (
    # design.md rule-4 vocabulary (incl. see/note — m3 reconciliation)
    "read", "run", "check", "consult", "see", "open", "write", "mv", "move",
    "update", "note", "verify", "ls", "cat", "create", "delete", "rm", "append",
    "regenerate", "scan", "edit", "commit", "add", "glob", "grep", "find", "copy", "cp",
    # frontmatter / prose inflections (M1 — `Reads`/`Produces`/`Writes` are operational
    # path references in skill `description:` fields; a \bword\b verb-list missed the
    # plural form, sweeping two LIVE paths to the off-checklist doc-example bucket):
    "reads", "produces", "produce", "writes", "defines", "define", "loads", "load",
    "emits", "emit", "stored", "stores", "store", "reading", "produced", "located",
)
_OP_VERB_RE = re.compile(r"\b(?:" + "|".join(_OP_VERBS) + r")\b", re.IGNORECASE)

# ── historical-anchor markers — NARROW genuine-preserve signals only (slice-107
# build-time recalibration / user-ratified deviation): broad markers ([[ADR-NNN]],
# changelog vN.N.N) co-occur with live operational references all over the corpus and
# mis-flag them; only the explicit preserve-vocabulary marks a literal as a do-NOT-
# rewrite anchor. ──
_ANCHOR_RE = re.compile(
    r"(?:historical[ -]anchor|Glob[ -]discoverability|discoverability anchor|"
    r"preserved as (?:a |an |the )?(?:historical|legacy|anchor)|legacy anchor)",
    re.IGNORECASE,
)

# ── git-pathspec syntax (breaks at flip — unambiguous rewrite) ────────────────
_PATHSPEC_RE = re.compile(r":\((?:exclude|glob|top|attr|icase|literal)")

# ── fence toggles (a line whose stripped form opens/closes a fence) ───────────
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")


def _normalize(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _in_inline_code(line: str, col: int) -> bool:
    """True if column ``col`` sits inside an odd run of backticks (inline code)."""
    return line[:col].count("`") % 2 == 1


# ── occurrence model ──────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Occurrence:
    path: str        # repo-relative, forward-slash
    line: int
    col: int         # 0-based start column of the match (M-add-1 disambiguator)
    value: str       # the full matched path token
    klass: str
    reason: str
    norm_line: str = ""
    fenced: bool = False
    ordinal: int = 0  # ordinal among identical normalized-lines in the file (M2)

    def disposition_key(self) -> tuple:
        # 5-tuple (M2 + M-add-1): path + normalized line + fence-state +
        # cross-line ordinal + intra-line column-offset.
        return (self.path, self.norm_line, self.fenced, self.ordinal, self.col)

    def baseline_key(self) -> tuple[str, str, str]:
        return (self.path, self.value, self.klass)

    def to_dict(self) -> dict:
        return {"path": self.path, "line": self.line, "col": self.col,
                "value": self.value, "klass": self.klass, "reason": self.reason}


@dataclass
class AuditResult:
    files_scanned: int = 0
    occurrences: list[Occurrence] = field(default_factory=list)

    def by_class(self, klass: str) -> list[Occurrence]:
        return [o for o in self.occurrences if o.klass == klass]

    @property
    def needs_human(self) -> list[Occurrence]:
        return self.by_class(NEEDS_HUMAN)

    def baseline_tuple(self) -> tuple[tuple[str, str, str], ...]:
        keys = [o.baseline_key() for o in self.occurrences if o.klass in _BASELINE_CLASSES]
        return tuple(sorted(keys))

    def class_counts(self) -> dict[str, int]:
        return {k: len(self.by_class(k)) for k in _ALL_CLASSES}

    def to_dict(self) -> dict:
        return {"files_scanned": self.files_scanned,
                "counts": self.class_counts(),
                "occurrences": [o.to_dict() for o in self.occurrences]}


# ── classification ────────────────────────────────────────────────────────────
def _classify_match(line: str, col: int, *, fenced: bool) -> tuple[str, str]:
    """Return (klass, reason) for one match at column ``col`` on ``line`` via the
    ordered ruleset (disposition override is applied by the caller).

    Recalibrated at slice-107 build-time (user-ratified deviation, build-log
    2026-06-03 — see design.md §Build-time recalibration): an in-code / fenced /
    operational vault path defaults to ``rewrite-at-flip`` (the dominant case on
    this corpus — a LIVE reference the flip must update; B2's goal preserved — it
    lands ON the M4 checklist, never the off-checklist ``doc-example``).
    ``doc-example`` is reserved for genuine plain prose. ``needs-human`` fires only
    for a true conflict: an in-code path on a line carrying a genuine
    historical-anchor *preserve* marker (rewrite-vs-preserve is then a human call,
    resolved via the ``_DISPOSITION`` table)."""
    in_code = fenced or _in_inline_code(line, col)
    if _PATHSPEC_RE.search(line):                      # 1. git-pathspec — breaks at flip
        return (REWRITE_AT_FLIP, "git-pathspec")
    has_anchor = _ANCHOR_RE.search(line) is not None
    if has_anchor:                                     # 2. genuine preserve marker
        if in_code:                                    #    in-code + anchor → true conflict
            return (NEEDS_HUMAN, "anchor-code-conflict")
        return (HISTORICAL_ANCHOR, "historical-anchor")
    if in_code or _OP_VERB_RE.search(line) is not None:  # 3. live operational reference
        return (REWRITE_AT_FLIP, "operational-reference")
    return (DOC_EXAMPLE, "plain-prose")                # 4. genuine plain-prose mention


def classify_line_occurrences(
    line: str, *, rel: str, lineno: int, fenced: bool,
    disposition: dict | None = None, ordinal: int = 0,
) -> list[Occurrence]:
    """Classify every vault-literal match on a single line (all matches per line)."""
    disposition = _DISPOSITION_MAP if disposition is None else disposition
    norm = _normalize(line)
    out: list[Occurrence] = []
    for m in _MATCH_RE.finditer(line):
        col = m.start()
        tok = _PATH_TOKEN_RE.match(line, col)
        value = tok.group(0) if tok else m.group(0)
        klass, reason = _classify_match(line, col, fenced=fenced)
        key = (rel, norm, fenced, ordinal, col)
        if key in disposition:
            klass, reason = disposition[key], "disposition"
        out.append(Occurrence(rel, lineno, col, value, klass, reason, norm, fenced, ordinal))
    return out


def audit_file(path: Path, rel: str, *, disposition: dict | None = None) -> list[Occurrence]:
    """Classify every matched literal in one file, tracking fence-state + the
    per-normalized-line ordinal (the M2 cross-line disambiguator)."""
    text = path.read_text(encoding="utf-8")
    occ: list[Occurrence] = []
    fenced = False
    seen: Counter[str] = Counter()
    for i, line in enumerate(text.splitlines(), start=1):
        if _FENCE_RE.match(line):
            fenced = not fenced
            # a fence-delimiter line itself never carries a vault path match worth
            # classifying, but fall through so an inline ```` ```architecture/x ````
            # edge is still scanned under the pre-toggle state below.
        norm = _normalize(line)
        ordinal = seen[norm]
        seen[norm] += 1
        occ.extend(classify_line_occurrences(
            line, rel=rel, lineno=i, fenced=fenced, disposition=disposition, ordinal=ordinal))
    return occ


def _iter_scan_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for g in _PROSE_GLOBS:
        files += [p for p in root.glob(g) if p.is_file()]
    # de-dup (a glob overlap) + stable order
    return sorted(set(files))


def audit_root(root: Path, *, disposition: dict | None = None) -> AuditResult:
    result = AuditResult()
    for path in _iter_scan_files(root):
        result.files_scanned += 1
        rel = str(path.relative_to(root)).replace("\\", "/")
        result.occurrences.extend(audit_file(path, rel, disposition=disposition))
    result.occurrences.sort(key=lambda o: (o.path, o.line, o.col))
    return result


# ── pinned baseline + disposition + residual (populated from the real corpus) ──
# (relpath, normalized-line, fenced, ordinal, column-offset) -> klass override.
_DISPOSITION: tuple[tuple, ...] = ()
_DISPOSITION_MAP: dict[tuple, str] = {(p, n, f, o, c): k for (p, n, f, o, c, k) in _DISPOSITION}

# sorted (relpath, value, klass) multiset for rewrite-at-flip + needs-human (AC3).
# Baseline pinned as an in-module SHA-256 of the sorted (relpath, value, klass)
# multiset for rewrite-at-flip + needs-human (AC3). A HASH, not the inlined
# slashed-path tuples, because readiness_audit scans tools/*.py and would classify
# 316 slashed collection-member literals as needs-human, tripping slice-106's
# baseline (AC5 / M1 disjointness — discovered at build, build-log 2026-06-03). The
# full enumerated inventory is the --json output; this hash is the drift identity
# (exit 2 on ANY multiset change — same gate behavior as an enumerated multiset).
_BASELINE_SHA256 = "1d150ca1764eedea5e52b5b3ecfcff3e4655d3a231e86bbbdfe03ea78f68f182"

# per-class total-count floor (m2 — a silent shrink trips --strict).
_CLASS_COUNT_FLOOR: dict[str, int] = {
    REWRITE_AT_FLIP: 318,
    HISTORICAL_ANCHOR: 0,
    DOC_EXAMPLE: 0,
    NEEDS_HUMAN: 0,
}

# bare-no-slash vault-dir args — the ONLY honest-contract residual (B1 + m-add-1).
_RESIDUAL: tuple[dict, ...] = (
    {'path': 'CLAUDE.md', 'line': 67, 'value': 'architecture', 'note': 'graphify vault architecture (rebuild vault graph)'},
    {'path': 'skills/adopt/SKILL.md', 'line': 72, 'value': 'architecture', 'note': 'graphify vault architecture'},
    {'path': 'skills/discover/SKILL.md', 'line': 102, 'value': 'architecture', 'note': 'graphify vault architecture (vault graph)'},
    {'path': 'skills/heavy-architect/SKILL.md', 'line': 184, 'value': 'architecture', 'note': 'graphify vault architecture'},
    {'path': 'skills/sync/SKILL.md', 'line': 176, 'value': 'architecture', 'note': 'graphify vault architecture'},
)

# Boundary-free corpus total (m2 provenance): == `grep -rohE "(architecture|diagnose-out)/"`
# over the 5 _PROSE_GLOBS, all-matches-per-line. Co-pinned with _BASELINE_SHA256 + the
# REWRITE_AT_FLIP count-floor (all three move together on any corpus change): a count
# change fails test_enumerates_full_corpus_318_…; a class/value change trips --strict.
# Pinned by AC1 (test, the documented consumer) — re-derive all three when the corpus changes.
EXPECTED_TOTAL = 318


# ── drift gate ────────────────────────────────────────────────────────────────
def baseline_sha(result: AuditResult) -> str:
    """SHA-256 of the sorted (relpath, value, klass) multiset for the baseline
    classes — the drift identity (AC3). Any add/remove/reclassify changes it."""
    return hashlib.sha256(repr(result.baseline_tuple()).encode("utf-8")).hexdigest()


def _baseline_drift(result: AuditResult) -> str | None:
    """The live baseline hash if it differs from the pinned ``_BASELINE_SHA256``,
    else None. (A hash, not enumerated tuples — see ``_BASELINE_SHA256`` for the
    AC5/M1 disjointness reason; re-run without ``--strict`` + ``--json`` to inspect
    WHAT changed.)"""
    live = baseline_sha(result)
    return None if live == _BASELINE_SHA256 else live


def _count_floor_shrink(result: AuditResult) -> list[str]:
    counts = result.class_counts()
    return [f"{k}: {counts.get(k,0)} < floor {floor}"
            for k, floor in _CLASS_COUNT_FLOOR.items() if counts.get(k, 0) < floor]


def _format_human(result: AuditResult, drift, shrink) -> str:
    c = result.class_counts()
    out = [
        f"Vault-flip PROSE inventory (ADR-096/097): {result.files_scanned} file(s), "
        f"{len(result.occurrences)} literal(s) — {c[REWRITE_AT_FLIP]} rewrite-at-flip, "
        f"{c[HISTORICAL_ANCHOR]} historical-anchor, {c[DOC_EXAMPLE]} doc-example, "
        f"{c[NEEDS_HUMAN]} needs-human.\n",
    ]
    for o in result.needs_human:
        out.append(f"  [needs-human]  {o.path}:{o.line}:{o.col} ({o.reason}) {o.value!r}\n")
    if drift is not None:
        out.append(f"\n--strict BASELINE DRIFT: live hash {drift} != pinned "
                   f"{_BASELINE_SHA256}\n  (the rewrite-at-flip+needs-human multiset "
                   f"changed; re-run with --json to inspect, then re-pin _BASELINE_SHA256)\n")
    for s in shrink:
        out.append(f"  --strict COUNT-FLOOR SHRINK: {s}\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="vault_flip_prose_inventory",
        description=("ADR-096 vault-flip PROSE inventory: enumerate + classify every "
                     "architecture/ + diagnose-out/ location-literal on the prose surface "
                     "(skills/agents/CLAUDE.md/INSTALL.md/README.md) so the flip has a "
                     "complete, regression-pinned prose checklist. Read-only; no flip."))
    parser.add_argument("--repo-root", "--root", dest="repo_root", type=Path, default=None,
                        help="Repo root (defaults to the parent of this tools/ dir)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Also gate (exit 2) on baseline drift / count-floor shrink")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve() if args.repo_root is not None else Path(__file__).resolve().parent.parent
    if not root.exists():
        sys.stderr.write(f"repo root not found: {root}\n")
        return 1
    try:
        result = audit_root(root)
    except OSError as exc:
        sys.stderr.write(f"vault_flip_prose_inventory: unreadable source — {exc}\n")
        return 1

    drift = _baseline_drift(result) if args.strict else None
    shrink = _count_floor_shrink(result) if args.strict else []

    if args.json:
        payload = result.to_dict()
        payload["baseline_drift"] = ({"live_hash": drift, "pinned_hash": _BASELINE_SHA256}
                                     if drift else None)
        payload["count_floor_shrink"] = shrink
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result, drift, shrink))

    if result.needs_human:
        return 2
    if args.strict and (drift is not None or shrink):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
