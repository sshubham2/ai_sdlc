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
backtick), which catches only 69 of 318 on slice-107's corpus: the 216 backtick-wrapped
inline-code paths + the operational ``:(exclude)architecture/...`` git-pathspecs are
invisible to it, yet they break at the M4 flip. ``re.finditer`` (not one ``re.search``
per line) is load-bearing: 24 lines carry >1 match (32 extra occurrences;
``code-review.md:103`` carries 5), so a per-line single match would undercount
(318→286 on slice-107's corpus). (These sub-counts are slice-107's measurement; the
LIVE total is the pinned ``EXPECTED_TOTAL`` — 131 after slice-114 / [[ADR-105]], was 132 after slice-113 / [[ADR-106]].)

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

On the current corpus the ruleset yields **127 rewrite-at-flip / 0 historical-anchor /
4 doc-example / 0 needs-human** (131 total; was 318 at slice-107; slice-111 / [[ADR-103]] → 313;
slice-112 / [[ADR-105]] converted 12 operational refs to the ``<vault>/`` placeholder + added 2
plain-prose definitionals → 303; slice-113 / [[ADR-106]] converted 171 convertible skill-prose
``architecture/`` refs across the 25 skill SKILL.md to ``<vault>/`` → 132, leaving 116 carve-outs
[classes 1-pathspec / 4-worktree-composed / 5-active-folder / 6-slice-queue / 7-diagnose-out];
slice-114 / [[ADR-105]] converted 3 agent-prose refs (code-review :44/:119 + critic-calibrate :22)
to ``<vault>/`` + added 2 plain-prose definitional notes → 131, leaving 4 agent carve-outs
[code-review :29 pathspec-mirror + :237 active-folder, critique-review :78, diagnose-narrator :19] +
the 4 doc-example) — most operational prose references to the vault location go stale at the M4
flip (rewrite-at-flip); the 4 doc-example are the CLAUDE.md + 3 agent-note (critique / code-review /
critic-calibrate) resolution-rule defaults (the ``<vault>`` convention's plain-prose ``architecture/``
default — slice-112/114); historical-anchor
and needs-human remain empty on this corpus (the classes exist for future drift / other surfaces).
The ``_DISPOSITION`` table + needs-human bucket remain the fail-closed mechanism for future drift.
``--strict`` pins the ``rewrite-at-flip`` + ``needs-human`` multiset baseline + a per-class
total-count floor (m2 — catches a silent ``rewrite-at-flip → doc-example`` demotion).

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
_BASELINE_SHA256 = "44b2287682bae389779623c59beae1dcdb4e9b0abe19c472075b29b26d701966"

# per-class total-count floor (m2 — a silent shrink trips --strict).
# slice-111 (ADR-103): routing the archive `mv` (/reflect, /archive) + drift-log
# (/drift-check) through `vault_edit` removed K=5 `architecture/` literals → 318→313.
# slice-112 (ADR-105): converting CLAUDE.md (5) + agents/critique.md (7) operational
# refs to the `<vault>/` placeholder removed 12 rewrite-at-flip literals; the 2 new
# plain-prose definitionals are doc-example → 313→301 rewrite-at-flip (DOC_EXAMPLE 0→2).
# slice-113 (ADR-106): the BULK skill-prose conversion — 171 convertible shared-aggregate
# `architecture/` literals across the 25 skill SKILL.md converted to `<vault>/` (carve-out
# classes 1-pathspec/4/5/6/7 stay concrete: 116 carve-outs remain — incl. the 3 code-review
# git-pathspec PROSE mirrors kept concrete per the /code-review B1 fix) → 301→130 rewrite-at-flip.
# slice-114 (ADR-105): the AGENT-prose surface — converted agents/code-review.md (:44 calibration-log,
# :119 .secrets-allowlist) + agents/critic-calibrate.md (:22 calibration-log) = 3 refs to `<vault>/`;
# the 2 new self-sufficient resolver notes add 2 plain-prose definitionals → 130→127 rewrite-at-flip
# (DOC_EXAMPLE 2→4). code-review :29 (architecture/**, operational-reference) + :237 (active-folder)
# stay concrete (hash-keyed in _CONVERTED_CARVEOUTS); critique-review :78 + diagnose-narrator :19 are
# note-less carve-outs (classes 5/7 — left untouched per ADR-105, the flip slice drains them).
_CLASS_COUNT_FLOOR: dict[str, int] = {
    REWRITE_AT_FLIP: 127,
    HISTORICAL_ANCHOR: 0,
    DOC_EXAMPLE: 0,
    NEEDS_HUMAN: 0,
}

# bare-no-slash vault-dir args — the ONLY honest-contract residual (B1 + m-add-1).
_RESIDUAL: tuple[dict, ...] = (
    {'path': 'CLAUDE.md', 'line': 70, 'value': 'architecture', 'note': 'graphify vault architecture (rebuild vault graph); line shifted 67→70 at slice-112 (added the <vault> resolution-rule bullet)'},
    {'path': 'skills/adopt/SKILL.md', 'line': 72, 'value': 'architecture', 'note': 'graphify vault architecture'},
    {'path': 'skills/discover/SKILL.md', 'line': 102, 'value': 'architecture', 'note': 'graphify vault architecture (vault graph)'},
    {'path': 'skills/heavy-architect/SKILL.md', 'line': 184, 'value': 'architecture', 'note': 'graphify vault architecture'},
    {'path': 'skills/query-design/SKILL.md', 'line': 59, 'value': 'architecture', 'note': 'graphify vault architecture (Error-model rebuild hint; slice-111 / critique-review m-add-3 — out-of-loop residual slice-107 missed)'},
    {'path': 'skills/sync/SKILL.md', 'line': 176, 'value': 'architecture', 'note': 'graphify vault architecture'},
)

# Boundary-free corpus total (m2 provenance): == `grep -rohE "(architecture|diagnose-out)/"`
# over the 5 _PROSE_GLOBS, all-matches-per-line. Co-pinned with _BASELINE_SHA256 + the
# REWRITE_AT_FLIP count-floor (all three move together on any corpus change): a count
# change fails test_enumerates_full_corpus_all_matches_per_line; a class/value change trips --strict.
# Pinned by AC1 (test, the documented consumer) — re-derive all three when the corpus changes.
# slice-111 (ADR-103): 318 → 313 after K=5 archive-`mv`/drift-log literals routed via `vault_edit`.
# slice-112 (ADR-105): 313 → 303 — 12 operational refs converted to `<vault>/` (no longer match),
# 2 new plain-prose definitionals added (CLAUDE.md + agents/critique.md self-sufficient note).
# slice-113 (ADR-106): 303 → 132 — 171 convertible skill-prose `architecture/` refs converted to
# `<vault>/` (no longer match); 116 carve-outs (classes 1-pathspec/4/5/6/7) + the 2 doc-example stay.
# slice-114 (ADR-105): 132 → 131 — 3 agent-prose `architecture/` refs converted to `<vault>/` (no
# longer match), +2 plain-prose definitional notes (doc-example 2→4); 4 agent carve-outs stay
# (code-review :29 pathspec-mirror + :237 active-folder, critique-review :78, diagnose-narrator :19).
EXPECTED_TOTAL = 131


# ══════════════════════════════════════════════════════════════════════════════
# CONVERTED-FILE ONE-WAY RATCHET (slice-112 / [[ADR-105]]) — the `<vault>` prose-
# seam convention's enforcement. A file in _CONVERTED_FILES has had its operational
# vault literals rewritten to the `<vault>/` placeholder; it must NEVER silently
# regress to a hardcoded operational `architecture/`/`diagnose-out/` literal. The
# ratchet is INDEPENDENT of the re-pinnable _BASELINE_SHA256 (M3): it reds a
# converted-file regression EVEN when the baseline is re-pinned to "cover" it.
# ══════════════════════════════════════════════════════════════════════════════
# Forward-slash repo-relative paths (match Occurrence.path, which audit_root
# normalizes via .replace("\\","/")). A backslash member would silently never
# match → vacuous-green (R-7); pinned forward-slash-only by the test (M3).
# slice-113 (ADR-106): grown from the slice-112 pilot (CLAUDE.md + agents/critique.md) to the
# 22 converted skill SKILL.md whose residual carve-outs are sound under VALUE-keying.
# `skills/code-review/SKILL.md` is DELIBERATELY EXCLUDED (un-ratcheted, documented — M3 / slice-113
# build-log): 5 of its git-pathspec carve-out VALUES (`architecture/decisions/**`,
# `architecture/slices/_index.md`, …) equal converted shared-aggregate values in the same file, so a
# per-value carve-out entry would also whitelist a real same-value regression (the M3 collision is
# EXPLOITABLE there — real paths, not slice/SKILL.md's non-exploitable `…` ellipsis). code-review's 8
# conversions are unprotected by the ratchet (its pathspecs are git-consumed flip-residual anyway).
_CONVERTED_FILES: frozenset[str] = frozenset({
    "CLAUDE.md",
    "agents/critique.md",
    "agents/code-review.md",        # slice-114 (ADR-105 agent-prose surface)
    "agents/critic-calibrate.md",   # slice-114 (ADR-105 agent-prose surface)
    "skills/adopt/SKILL.md",
    "skills/archive/SKILL.md",
    "skills/build-slice/SKILL.md",
    "skills/commit-slice/SKILL.md",
    "skills/critic-calibrate/SKILL.md",
    "skills/critique/SKILL.md",
    "skills/design-slice/SKILL.md",
    "skills/diagnose/SKILL.md",
    "skills/discover/SKILL.md",
    "skills/drift-check/SKILL.md",
    "skills/heavy-architect/SKILL.md",
    "skills/pulse/SKILL.md",
    "skills/reduce/SKILL.md",
    "skills/reflect/SKILL.md",
    "skills/repro/SKILL.md",
    "skills/risk-spike/SKILL.md",
    "skills/slice/SKILL.md",
    "skills/supersede-slice/SKILL.md",
    "skills/sync/SKILL.md",
    "skills/triage/SKILL.md",
    "skills/user-test/SKILL.md",
    "skills/validate-slice/SKILL.md",
})

# Sanctioned carve-outs that legitimately STAY concrete inside a converted file:
# the OPERATIONAL (in-code) literals of carve-out classes 5/6/7 (ADR-105) — per-slice
# active-folder, the slice-queue ledger, diagnose-out (no seam yet, B5). Keyed
# (path, sha256(value)) so this tools/*.py source carries NO slashed `architecture/`
# literal that vault_flip_readiness_audit would flag (slice-107 AC5 disjointness;
# same SHA-256 precedent as _BASELINE_SHA256 + slice-111's _OP_ALLOWLIST). The
# definitional literal (class 2) is plain-prose doc-example — NOT rewrite-at-flip —
# so it never enters this ratchet. An un-sanctioned carve-out is a regression.
# slice-113 (ADR-106): grown to the carve-out literals of the 22 ratcheted converted skill files.
# Classes: 1-pathspec (git-consumed, M-add-2 — only in non-ratcheted code-review, so none appear here),
# 5-active-folder (R-32.a), 6-slice-queue (M1), 7-diagnose-out (B5), 4-worktree-composed. The lone
# `slices/…` ellipsis (skills/slice/SKILL.md) is a documented NON-exploitable same-value collision
# (an `…` ellipsis is not a real path — a real regression cannot match it; M3 / slice-113 build-log).
_CONVERTED_CARVEOUTS: frozenset[tuple[str, str]] = frozenset({
    # slice-112 pilot (CLAUDE.md + agents/critique.md):
    ("CLAUDE.md", "d38d844b56ab18a745e9d49a97975e4a37da983bb86d3b0c28b36ab8874044d1"),  # diagnose-out/backlog.md
    ("CLAUDE.md", "5c7c173c05aa115363f9af90583148092d9558b610c7d92b09841078f95701c8"),  # diagnose-out/
    ("agents/critique.md", "39e937eae93854994eff21f409b9d87207fda490c42063ce39945d06c44e2bfe"),  # architecture/slice-queue.md
    ("agents/critique.md", "9a4b7f08b84ba3a46ebd2e10938f6ef842719d477cfacbe9c3a8f71ba14c1f35"),  # architecture/slices/slice-NNN-<name>/critique.md
    # skills/adopt/SKILL.md:
    ("skills/adopt/SKILL.md", "5c7c173c05aa115363f9af90583148092d9558b610c7d92b09841078f95701c8"),  # [diagnose-out] diagnose-out/
    ("skills/adopt/SKILL.md", "b31caff21eb6dab4d6839fb6ee62bea1c65c6cf7bbca8af04719357196158270"),  # [diagnose-out] diagnose-out/diagnosis.html
    # skills/build-slice/SKILL.md:
    ("skills/build-slice/SKILL.md", "39e937eae93854994eff21f409b9d87207fda490c42063ce39945d06c44e2bfe"),  # [slice-queue] architecture/slice-queue.md
    ("skills/build-slice/SKILL.md", "cbd281686d3dae6380ffbb8d130c82a378f55cddb840bebce10787f4b0b34150"),  # [active-folder] architecture/slices/slice-NNN-<name>
    ("skills/build-slice/SKILL.md", "a91b20d271865574a5d8a0b2e015f0b0c0294ca7676c9fcc4dfb9794aea752b5"),  # [active-folder] architecture/slices/slice-NNN-<name>/build-log.md
    ("skills/build-slice/SKILL.md", "0048a558d7c8ded4e7d3037e97ac1768a849fd8f10ef2c7cab210de8e6a97730"),  # [active-folder] architecture/slices/slice-NNN-<slice-name>/
    ("skills/build-slice/SKILL.md", "5c7c173c05aa115363f9af90583148092d9558b610c7d92b09841078f95701c8"),  # [diagnose-out] diagnose-out/
    # skills/commit-slice/SKILL.md:
    ("skills/commit-slice/SKILL.md", "39e937eae93854994eff21f409b9d87207fda490c42063ce39945d06c44e2bfe"),  # [slice-queue] architecture/slice-queue.md
    ("skills/commit-slice/SKILL.md", "4b8447125928b34deddd2fa65efc2f91a8b1e5359d6707e4c2231b565c638219"),  # [active-folder] architecture/slices/<slice-id>/mission-brief.md
    # skills/critique/SKILL.md:
    ("skills/critique/SKILL.md", "cbd281686d3dae6380ffbb8d130c82a378f55cddb840bebce10787f4b0b34150"),  # [active-folder] architecture/slices/slice-NNN-<name>
    ("skills/critique/SKILL.md", "9a4b7f08b84ba3a46ebd2e10938f6ef842719d477cfacbe9c3a8f71ba14c1f35"),  # [active-folder] architecture/slices/slice-NNN-<name>/critique.md
    ("skills/critique/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    # skills/design-slice/SKILL.md:
    ("skills/design-slice/SKILL.md", "70421ea5582b58aa5c6428f716e93687f8a0ff40bc1057b8046e5bf7ece6a122"),  # [active-folder] architecture/slices/slice-NNN-*/
    ("skills/design-slice/SKILL.md", "cbd281686d3dae6380ffbb8d130c82a378f55cddb840bebce10787f4b0b34150"),  # [active-folder] architecture/slices/slice-NNN-<name>
    ("skills/design-slice/SKILL.md", "aa8442abe07c25ce43f8b6d82ee1ea369af46eda0e72a684045b5b43e6456283"),  # [active-folder] architecture/slices/slice-NNN-<name>/design.md
    ("skills/design-slice/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    ("skills/design-slice/SKILL.md", "612f1c6eb1253016a7556c3c82ecdfef0d1f5396fed5e13f9b5b428b82b1a222"),  # [active-folder] architecture/slices/slice-NNN/mission-brief.md.
    # skills/diagnose/SKILL.md:
    ("skills/diagnose/SKILL.md", "5c7c173c05aa115363f9af90583148092d9558b610c7d92b09841078f95701c8"),  # [diagnose-out] diagnose-out/
    ("skills/diagnose/SKILL.md", "b31caff21eb6dab4d6839fb6ee62bea1c65c6cf7bbca8af04719357196158270"),  # [diagnose-out] diagnose-out/diagnosis.html
    ("skills/diagnose/SKILL.md", "cb384b4b7598b959fd268d69e2d07b98b7a799331d8476ab12f295fbbd2f0557"),  # [diagnose-out] diagnose-out/graphify-out/
    # skills/drift-check/SKILL.md:
    ("skills/drift-check/SKILL.md", "dbabb63c90bf7d44f8025c20d81578f92fe06d853066118b88c8fa0aacd20779"),  # [active-folder] architecture/slices/*/design.md
    ("skills/drift-check/SKILL.md", "265891161a7012ded01d6324b341d096f1e8aa234eedac4bef6191a7b965fcca"),  # [active-folder] architecture/slices/*/mission-brief.md
    # skills/pulse/SKILL.md:
    ("skills/pulse/SKILL.md", "74dcc480bb7d4fb8cc195e7aa3a4213d5f623d678b7c93c24679f27373be47ec"),  # [active-folder] architecture/slices/<active>/milestone.md
    ("skills/pulse/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    # skills/reflect/SKILL.md:
    ("skills/reflect/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    ("skills/reflect/SKILL.md", "6af578d89b8dd85bfdfdb45b0d47e4b48c54fafdb39605a380c5ef47c70fff7a"),  # [active-folder] architecture/slices/slice-NNN-<name>/reflection.md
    ("skills/reflect/SKILL.md", "5c7c173c05aa115363f9af90583148092d9558b610c7d92b09841078f95701c8"),  # [diagnose-out] diagnose-out/
    ("skills/reflect/SKILL.md", "d38d844b56ab18a745e9d49a97975e4a37da983bb86d3b0c28b36ab8874044d1"),  # [diagnose-out] diagnose-out/backlog.md
    # skills/slice/SKILL.md:
    ("skills/slice/SKILL.md", "39e937eae93854994eff21f409b9d87207fda490c42063ce39945d06c44e2bfe"),  # [slice-queue] architecture/slice-queue.md
    ("skills/slice/SKILL.md", "f0bec21a0ababecb37a19f78f513b20f7d48093778b3338ac34ad44607eec2df"),  # [active-folder] architecture/slices/slice-NNN-<name>/
    ("skills/slice/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    ("skills/slice/SKILL.md", "8103879a08054561e84ac18bb54e0cd1613e587aaae1992627a191c19075be5c"),  # [active-folder] architecture/slices/slice-NNN-<name>/mission-brief.md
    ("skills/slice/SKILL.md", "21bfd206aad55f561435ef77ea1d32528ae258f4ce19042ed215689021cbeb83"),  # [active-folder] architecture/slices/slice-NNN-<name>/mission-brief.md.
    ("skills/slice/SKILL.md", "0f5deb5f2c9776e1659d0d6e08bda7938931f1f88c7904bb842f5e930a8953ae"),  # [active-folder] architecture/slices/… (non-exploitable ellipsis collision — M3)
    ("skills/slice/SKILL.md", "d38d844b56ab18a745e9d49a97975e4a37da983bb86d3b0c28b36ab8874044d1"),  # [diagnose-out] diagnose-out/backlog.md
    # skills/supersede-slice/SKILL.md:
    ("skills/supersede-slice/SKILL.md", "61fd8677b9ab75e69f2877f16d3c54bd4bd54596ee1e851908708c61f4c157da"),  # [active-folder] architecture/slices/<active-slice-id>/
    # skills/validate-slice/SKILL.md:
    ("skills/validate-slice/SKILL.md", "cbd281686d3dae6380ffbb8d130c82a378f55cddb840bebce10787f4b0b34150"),  # [active-folder] architecture/slices/slice-NNN-<name>
    ("skills/validate-slice/SKILL.md", "aa23f93ad8223e154a3d7e485a630eff0e8391b85438795787f80b5521d79be8"),  # [active-folder] architecture/slices/slice-NNN-<name>/milestone.md
    ("skills/validate-slice/SKILL.md", "61952ccd32863abd4b70deca452e237709b3844c60426cf99466e833a188ed30"),  # [active-folder] architecture/slices/slice-NNN-<name>/validation.md
    # agents/code-review.md (slice-114) — the 2 operational carve-outs surviving conversion:
    ("agents/code-review.md", "0a69ee77c51793aecd3e6f0e233f885844ad89cd877dd8c3c758fe42c6ac1666"),  # [pathspec-mirror] architecture/** (diff-scope prose mirror of skills/code-review/SKILL.md :(exclude) pathspecs; operational-reference class, M2)
    ("agents/code-review.md", "46e2f7eb6b4042736d63d4169f5df52746eb31f59f9f1c4fc336938c87c6892f"),  # [active-folder] architecture/slices/slice-NNN-<name>/code-review.md
    # (agents/critic-calibrate.md needs NO carve-out — its sole ref :22 was converted.)
})


def _carveout_key(path: str, value: str) -> tuple[str, str]:
    return (path, hashlib.sha256(value.encode("utf-8")).hexdigest())


def converted_file_regressions(result: AuditResult) -> list["Occurrence"]:
    """The converted-file one-way ratchet (ADR-105): every `rewrite-at-flip`
    occurrence inside a _CONVERTED_FILES member whose (path, value) is NOT a
    sanctioned carve-out. Non-empty → the convention regressed; `--strict` exits 2.
    INDEPENDENT of _BASELINE_SHA256 (M3 — keyed on the live occurrence set + the
    carve-out allowlist, never the re-pinnable baseline hash)."""
    return [
        o for o in result.occurrences
        if o.path in _CONVERTED_FILES
        and o.klass == REWRITE_AT_FLIP
        and _carveout_key(o.path, o.value) not in _CONVERTED_CARVEOUTS
    ]


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


# ══════════════════════════════════════════════════════════════════════════════
# OP-GATE (slice-111 / [[ADR-104]], implements [[ADR-102]]) — a DISTINCT concern
# from the inventory above: the inventory enumerates location-LITERALS for the flip
# rewrite-checklist; the op-gate flags un-routed in-loop-skill vault WRITE-OPS.
# Reuses this module's region-anchoring (_in_inline_code + fence-tracking) + file
# walk + --strict baseline machinery (CSP-1 / slice-110 M-add-1: NOT a third
# classifier). In-loop-scoped (slice-111 /critique-review M-add-1): OP_UNROUTED
# (exit 2) fires ONLY for the slice-loop skills; out-of-loop / undecided-disposition
# writes land in a gate-visible OP_OUT_OF_SCOPE bucket (AP-12: never a silent waiver).
# ══════════════════════════════════════════════════════════════════════════════
OP_ROUTED = "op-routed"
OP_DEFERRED_TO_FLIP = "op-deferred-to-flip"
OP_OUT_OF_SCOPE = "op-out-of-scope"
OP_UNROUTED = "op-unrouted"
_OP_ALL_CLASSES = (OP_ROUTED, OP_DEFERRED_TO_FLIP, OP_OUT_OF_SCOPE, OP_UNROUTED)

# Mutating verbs. Bare ``add`` is DELIBERATELY EXCLUDED — it false-matches slice
# names (``slice-NNN-add-receipt`` → ``\badd\b``) and prose (``Add --seam-allowlist``);
# ``git add`` is detected as a bigram (_GIT_ADD_RE). AP-16 (m1): the DETECTION set
# (these verbs + git-add) IS the CLASSIFICATION set — no verb classifies a site it
# can't detect.
_WRITE_OP_VERBS = ("mv", "move", "cp", "copy", "rm", "delete", "write", "edit",
                   "create", "append")
_WRITE_OP_VERB_RE = re.compile(r"\b(?:" + "|".join(_WRITE_OP_VERBS) + r")\b", re.IGNORECASE)
_GIT_ADD_RE = re.compile(r"\bgit\s+add\b", re.IGNORECASE)
# move/copy verbs: only the DEST (last in-code literal) is a write TARGET (the source
# is a read). Other write verbs target every in-code literal on the line.
_MOVE_VERB_RE = re.compile(r"\b(?:mv|move|cp|copy)\b", re.IGNORECASE)

# A routed op carries a seam token in its line.
_SEAM_TOKEN_RE = re.compile(r"vault_edit|VAULT_ROOT")

# Op-gate SINK matcher — SEAM-AWARE ([[ADR-106]] / slice-113): matches the `<vault>/`
# placeholder IN ADDITION to architecture|diagnose-out/, so a CONVERTED in-loop write-op
# stays VISIBLE to the gate. A gate blind to `<vault>/` would be permanently fail-OPEN for
# the very convention slice-113 rolls out (an un-routed `<vault>/risk-register.md` write
# would never red) — defeating the R-32 write-safety story. DELIBERATELY DISTINCT from the
# inventory `_MATCH_RE` (which must NOT match `<vault>/`, else a converted literal re-appears
# in the inventory baseline + the converted-file ratchet and EXPECTED_TOTAL never settles).
# A maintainer who "unifies" the two silently re-breaks one half — a /code-review trap; do NOT.
# B2 (slice-113 /critique): the value EXTRACTOR `_OP_SINK_TOKEN_RE` is CO-load-bearing with
# the matcher — `_classify_op` keys on the extracted sink VALUE (`_ACTIVE_FOLDER_RE.search(sink)`
# etc.), so a `<vault>/` match whose tail can't be extracted collapses to bare `<vault>/` and
# every sub-regex misses. Matcher + extractor MUST move in lockstep (proven by the
# `<vault>/`-sink op-gate tests — AP-5 non-vacuity).
_OP_SINK_RE = re.compile(r"(?:architecture|diagnose-out)/|<vault>/")
_OP_SINK_TOKEN_RE = re.compile(r"(?:(?:architecture|diagnose-out)|<vault>)/[^\s`'\"()\\|,]*")

# Destination taxonomy (keyed on the op's SINK literal, NOT any literal on the line
# — B2/AP-15). A per-slice ACTIVE folder (slices/slice-NNN…, NOT slices/archive/) is
# the bootstrap-entangled DEFERRED class.
_ACTIVE_FOLDER_RE = re.compile(r"slices/slice-(?:\d+|NNN)")  # real digits OR the skill-prose placeholder
_ARCHIVE_DEST_RE = re.compile(r"slices/archive/")
# Undecided-flip-disposition: the slice-queue.md main-tree coordination ledger (its
# tracked-vs-external fate is the flip slice's call — [[ADR-090]] keeps it on the
# default branch today). git-add of it is OUT_OF_SCOPE, not a routing violation.
_UNDECIDED_DISPOSITION_RE = re.compile(r"slice-queue\.md")

# The slice-loop skills the op-gate GATES (OP_UNROUTED → exit 2). Out-of-loop skills
# → OP_OUT_OF_SCOPE. Pinned FBCD-1 counted set — a membership change re-pins
# _IN_LOOP_SKILLS_COUNT + fans out.
_IN_LOOP_SKILLS = frozenset({
    "slice", "design-slice", "critique", "critique-review", "build-slice",
    "code-review", "validate-slice", "reflect", "commit-slice", "archive",
    "drift-check",
})
_IN_LOOP_SKILLS_COUNT = 11

# Hand-verified in-loop candidates that are NOT OP_UNROUTED violations — keyed on
# (skill, SHA-256(normalized-line)) → (class, reason). The lexical markdown detector
# is deliberately loose (catch everything); this allowlist absorbs the residual
# explicitly + gate-visibly (AP-12 — enumerated, count-floored, NOT a silent
# baseline). Finalized at build against the real corpus (APED-1, 2026-06-04).
#
# The key is a HASH of the normalized line, NOT the line text — so this `tools/*.py`
# source carries NO `architecture/` literal that `vault_flip_readiness_audit` would
# flag (AC5 disjointness; same reason slice-107 hashed `_BASELINE_SHA256` rather than
# inlining slashed tuples). A line edit changes its hash → the site re-surfaces as
# OP_UNROUTED (fail-safe; re-verify + re-pin), exactly like the inventory baseline.
# Site comments name skill:line + the verified reason (no path literals in comments).
_OP_ALLOWLIST: dict[tuple[str, str], tuple[str, str]] = {
    # build-slice:407 — NAW-1 bootstrap narrative; 'edit'/'flip' are nouns, not a write-op.
    # slice-113 (ADR-106): re-hashed — the line's `architecture/risk-register.md` converted to `<vault>/`.
    ("build-slice", "afedad5b84f6eeff8e1b97130a5df2374fac497ba4cf1bb9ffee1f8793aec408"):
        (OP_OUT_OF_SCOPE, "lexical-false-positive: NAW-1 bootstrap narrative; 'edit'/'flip' are nouns, not a write-op"),
    # commit-slice:216 — parallel_conflict_resolver PCR log (git-coupled; retires at flip).
    # slice-113 (ADR-106): re-hashed — the line's `architecture/parallel-conflict-resolution-log.md` converted.
    ("commit-slice", "74c0303a1bc93e9d5e702a685b1bbf834e36fc3428cda3d49d33269de829498a"):
        (OP_OUT_OF_SCOPE, "parallel_conflict_resolver PCR log; git-coupled, retires at flip (ADR-098); owner = the flip slice's retire work"),
    # design-slice:240 — Heavy-mode component/contract write; out of slice-111 AC1 scope.
    # slice-113 (ADR-106): re-hashed — the line's `architecture/components|contracts/<name>.md` converted.
    ("design-slice", "f6e634537607b8529ceb94ff6b7b868548900f4ed010c84266e759c7fa0ff332"):
        (OP_OUT_OF_SCOPE, "Heavy-mode component/contract write; out of slice-111 AC1 scope (archive-mv + drift-log only); owner = prose-rewrite/flip slice"),
    # slice:264 — per-slice active-folder scaffold reference (abbreviated form).
    ("slice", "c965f3d99437c5b83bea62b4b11ae62d408f4e0e16ada17f8e9b46e0ffa2eab0"):
        (OP_DEFERRED_TO_FLIP, "per-slice active-folder scaffold (abbreviated); same bootstrap-deferred class as the slice:249 scaffold write"),
}

# Per-op-class count floors (a silent shrink trips --strict; AP-12 — the deferred /
# out-of-scope buckets must not silently empty). Finalized at build against the real
# corpus (APED-1, 2026-06-04): 6 routed / 11 deferred / 23 out-of-scope / 0 unrouted.
# Re-pin these (deliberately) when a slice routes / removes an op (a legit shrink).
_OP_CLASS_FLOOR: dict[str, int] = {
    OP_UNROUTED: 0,           # the binding invariant: zero un-routed in-loop writes (the gate)
    OP_DEFERRED_TO_FLIP: 11,  # AP-12: the flip slice's R-32.a drain bucket must stay visible
    OP_OUT_OF_SCOPE: 23,      # AP-12: out-of-scope writes owned by the prose-rewrite/flip slice
}


@dataclass(frozen=True)
class OpOccurrence:
    path: str
    line: int
    col: int
    value: str        # the write-target (sink) literal
    klass: str
    reason: str
    skill: str

    def to_dict(self) -> dict:
        return {"path": self.path, "line": self.line, "col": self.col,
                "value": self.value, "klass": self.klass, "reason": self.reason,
                "skill": self.skill}


def _skill_of(rel: str) -> str | None:
    """``skills/<name>/SKILL.md`` → ``<name>``; anything else → None (the op-gate
    scans skill SKILL.md only — CLAUDE.md/README/INSTALL/agents carry no in-loop ops)."""
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "skills" and parts[-1] == "SKILL.md":
        return parts[1]
    return None


def _classify_op(line: str, sink: str, *, skill: str, routed: bool) -> tuple[str, str]:
    """Classify ONE write-op by its SINK literal (B2/AP-15 — the destination, not any
    literal on the line). First-applicable wins; an un-allowlisted in-loop
    shared-aggregate write is the only OP_UNROUTED (exit 2).

    ``routed`` is computed by the caller as "a seam token appears AFTER the governing
    verb" (M1 / code-review) — NOT a line-wide `vault_edit`/`VAULT_ROOT` match, which a
    decoy prose mention ("do NOT run raw, use `vault_edit`") could exploit to mask a
    real un-routed write (the AP-15 decoy-marker failure ADR-104 warns against)."""
    if routed:
        return (OP_ROUTED, "seam-token")
    if _ACTIVE_FOLDER_RE.search(sink) and not _ARCHIVE_DEST_RE.search(sink):
        return (OP_DEFERRED_TO_FLIP, "active-folder-dest")
    if skill not in _IN_LOOP_SKILLS:
        return (OP_OUT_OF_SCOPE, "out-of-loop-skill")
    if _UNDECIDED_DISPOSITION_RE.search(sink):
        return (OP_OUT_OF_SCOPE, "undecided-flip-disposition-ledger")
    key = (skill, hashlib.sha256(_normalize(line).encode("utf-8")).hexdigest())
    if key in _OP_ALLOWLIST:
        return _OP_ALLOWLIST[key]
    return (OP_UNROUTED, "in-loop-unrouted-aggregate-write")


def scan_op_file(path: Path, rel: str) -> list[OpOccurrence]:
    """Find vault WRITE-OP targets in one skill SKILL.md. A literal is a target iff
    (a) a write-op verb / ``git add`` appears BEFORE it on the line (a write targets a
    FOLLOWING path; drops 'completed slices move to `…`' / '…then `git add` it'), AND
    (b) the literal is IN-CODE (inline backtick or fenced — a real path reference, not
    a sentence mention). For a SINGLE clean move/copy line only the DEST (last in-code
    literal) is a target; any multi-verb line is fail-safe — every in-code literal is a
    target (M2 / code-review).

    Known coverage limit (m1 / code-review, intentional v1 trade-off): a write whose
    SINK literal is NOT inside backticks (e.g. a backticked flag then a BARE path:
    ``mv `--force` architecture/x``) is treated as prose and NOT gated — the in-code
    requirement that suppresses sentence-mentions also drops a bare-path sink."""
    skill = _skill_of(rel)
    if skill is None:
        return []
    text = path.read_text(encoding="utf-8")
    out: list[OpOccurrence] = []
    fenced = False
    for i, line in enumerate(text.splitlines(), start=1):
        if _FENCE_RE.match(line):
            fenced = not fenced
        has_git_add = _GIT_ADD_RE.search(line) is not None
        verb_cols = [m.start() for m in _WRITE_OP_VERB_RE.finditer(line)]
        verb_cols += [m.start() for m in _GIT_ADD_RE.finditer(line)]
        if not verb_cols:
            continue
        first_verb = min(verb_cols)
        lits: list[tuple[int, str]] = []
        for m in _OP_SINK_RE.finditer(line):   # SEAM-AWARE (ADR-106): also matches <vault>/
            col = m.start()
            if col <= first_verb:
                continue  # a write-op targets a path AFTER the verb; a literal before
                          # any verb is a subject/mention, not a write target (drops
                          # "`…/design.md` … completed slices move to …" / "…then `git add` it")
            if not (fenced or _in_inline_code(line, col)):
                continue  # a real write target is an in-code path ref, not a mention
            tok = _OP_SINK_TOKEN_RE.match(line, col)   # B2: extractor co-load-bearing with _OP_SINK_RE
            lits.append((col, tok.group(0) if tok else m.group(0)))
        if not lits:
            continue
        # M1: a write is ROUTED only if a seam token follows the governing verb (NOT
        # a line-wide match — a decoy `vault_edit` mention before the verb must not
        # mask a raw write). first_verb is the earliest write-verb/git-add column.
        routed = _SEAM_TOKEN_RE.search(line, first_verb) is not None
        # M2: collapse to the single DEST (last literal) ONLY for a clean single-move
        # line (exactly one write verb, a move/copy, no git-add). A multi-verb line
        # (e.g. `copy X then create Y`, or `mv … then git add …`) is fail-safe: EVERY
        # in-code literal is a target (over-flag, never silently drop an un-routed write).
        is_move = (not has_git_add and len(verb_cols) == 1
                   and _MOVE_VERB_RE.search(line) is not None)
        targets = [lits[-1]] if is_move else lits
        for col, value in targets:
            klass, reason = _classify_op(line, value, skill=skill, routed=routed)
            out.append(OpOccurrence(rel, i, col, value, klass, reason, skill))
    return out


def op_audit_root(root: Path) -> list[OpOccurrence]:
    out: list[OpOccurrence] = []
    for path in _iter_scan_files(root):
        rel = str(path.relative_to(root)).replace("\\", "/")
        out.extend(scan_op_file(path, rel))
    out.sort(key=lambda o: (o.path, o.line, o.col))
    return out


def _op_class_counts(ops: list[OpOccurrence]) -> dict[str, int]:
    return {k: sum(1 for o in ops if o.klass == k) for k in _OP_ALL_CLASSES}


def _op_floor_shrink(ops: list[OpOccurrence]) -> list[str]:
    counts = _op_class_counts(ops)
    return [f"{k}: {counts.get(k, 0)} < floor {floor}"
            for k, floor in _OP_CLASS_FLOOR.items()
            if k != OP_UNROUTED and counts.get(k, 0) < floor]


def _format_op_human(ops: list[OpOccurrence], strict: bool) -> str:
    c = _op_class_counts(ops)
    out = [
        f"Vault-flip OP-GATE (ADR-104): {len(ops)} in-code write-op(s) — "
        f"{c[OP_ROUTED]} routed, {c[OP_DEFERRED_TO_FLIP]} deferred-to-flip, "
        f"{c[OP_OUT_OF_SCOPE]} out-of-scope, {c[OP_UNROUTED]} UNROUTED.\n",
    ]
    for o in ops:
        if o.klass == OP_UNROUTED:
            out.append(f"  [OP_UNROUTED]  {o.path}:{o.line}:{o.col} "
                       f"({o.skill}; {o.reason}) {o.value!r}\n")
    if strict:
        for s in _op_floor_shrink(ops):
            out.append(f"  --strict OP COUNT-FLOOR SHRINK: {s}\n")
    return "".join(out)


def _run_op_gate(root: Path, *, as_json: bool, strict: bool) -> int:
    ops = op_audit_root(root)
    unrouted = [o for o in ops if o.klass == OP_UNROUTED]
    shrink = _op_floor_shrink(ops) if strict else []
    if as_json:
        sys.stdout.write(json.dumps({
            "mode": "op-gate",
            "counts": _op_class_counts(ops),
            "in_loop_skills_count": _IN_LOOP_SKILLS_COUNT,
            "op_class_floor": _OP_CLASS_FLOOR,
            "op_count_floor_shrink": shrink,
            "occurrences": [o.to_dict() for o in ops],
        }, indent=2) + "\n")
    else:
        sys.stdout.write(_format_op_human(ops, strict))
    if unrouted:
        return 2
    if strict and shrink:
        return 2
    return 0


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
    parser.add_argument("--op-gate", dest="op_gate", action="store_true",
                        help="OP-GATE mode (ADR-104): flag un-routed in-loop-skill vault "
                             "WRITE-ops (exit 2 on OP_UNROUTED) instead of the location-literal "
                             "inventory. In-loop-scoped; out-of-loop/undecided-disposition writes "
                             "→ gate-visible OP_OUT_OF_SCOPE.")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve() if args.repo_root is not None else Path(__file__).resolve().parent.parent
    if not root.exists():
        sys.stderr.write(f"repo root not found: {root}\n")
        return 1

    if args.op_gate:
        try:
            return _run_op_gate(root, as_json=args.json, strict=args.strict)
        except OSError as exc:
            sys.stderr.write(f"vault_flip_prose_inventory: unreadable source — {exc}\n")
            return 1

    try:
        result = audit_root(root)
    except OSError as exc:
        sys.stderr.write(f"vault_flip_prose_inventory: unreadable source — {exc}\n")
        return 1

    drift = _baseline_drift(result) if args.strict else None
    shrink = _count_floor_shrink(result) if args.strict else []
    regressions = converted_file_regressions(result) if args.strict else []

    if args.json:
        payload = result.to_dict()
        payload["baseline_drift"] = ({"live_hash": drift, "pinned_hash": _BASELINE_SHA256}
                                     if drift else None)
        payload["count_floor_shrink"] = shrink
        payload["converted_file_regressions"] = [o.to_dict() for o in regressions]
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result, drift, shrink))
        for o in regressions:
            sys.stdout.write(
                f"  --strict CONVERTED-FILE REGRESSED: {o.path}:{o.line}:{o.col} "
                f"{o.value!r} — a converted file (ADR-105) must not hardcode an "
                f"operational vault literal; use `<vault>/` or sanction a carve-out\n")

    if result.needs_human:
        return 2
    if args.strict and (drift is not None or shrink or regressions):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
