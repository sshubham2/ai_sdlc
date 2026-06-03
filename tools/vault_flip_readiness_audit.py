"""Vault-flip readiness audit (slice-100 / [[ADR-091]]; tests surface slice-102 / [[ADR-092]]).

Read-only inventory of in-tree-vault-location path literals so the external-vault
flip (the next cut) has a complete, regression-pinned checklist of what breaks when
`architecture/` + `diagnose-out/` relocate. The flip is NOT performed here
(capability-without-flip, mirroring slice-093); this audit only classifies + guards.

TWO SURFACES (slice-102 / [[ADR-092]]):
  * PRODUCTION (`tools/*.py` + skill-helper `skills/**/*.py`) — a missed literal is a
    SILENT path mis-resolve; the ordered ruleset below classifies it.
  * TESTS (`tests/**/*.py`, excluding any `fixtures/` segment) — a missed literal
    breaks LOUDLY (a failing test). The SAME ruleset runs, then `_remap_for_tests`
    relabels: path-construction (`must-rewrite`) → `test-update-at-flip` (the update
    checklist); unmarked-collection-pathspec (`needs-human` on production) →
    `test-collection-pathspec` (a git-pathspec/Class-B mirror — REVIEW at flip, NOT
    the checklist, NOT fail-closed). A genuinely-unclassifiable tests literal
    (dynamic-fragment / parse-error) still routes to `needs-human` (fail-closed).
    `baseline_tuple()` / `--strict` are PRODUCTION-scoped; the tests surface is
    gate-covered by the always-on needs-human-empty invariant + per-class floors.

CLASSIFICATION — context-aware, NOT node-type-only (the B1/M1 correction: a vault
literal inside a diagnostic *message* string is an ``ast.Constant`` str but is not
a path the code resolves; node-type alone over-flags it). Each matched occurrence
is classified by an ORDERED ruleset (first applicable wins):

  1. doc-example-safe   — a `tokenize` COMMENT, a docstring, an argparse
                          help=/description=/epilog=/usage= kwarg value, OR a line
                          carrying the slice-068 ``— error-message prose`` marker.
  2. already-seam-routed — the line carries the [[ADR-089]] Class-B marker
                          ``Class-B git identity (ADR-089)``; OR the file is the
                          seam itself (``_vault_paths.py`` / ``_vault_git.py``); OR
                          ``VAULT_ROOT`` appears on the literal's line.
  3. must-rewrite-before-flip — the literal (bare ``"architecture"``/``"diagnose-out"``
                          OR slashed prefix) sits in a PATH-CONSTRUCTION context
                          (≤1-hop usage analysis): operand of a ``/`` BinOp; arg to
                          ``Path(...)``/``PurePath(...)``; arg/receiver of a path
                          method (``.open``/``.read_text``/``.write_text``/
                          ``.read_bytes``/``.glob``/``.iterdir``/``.exists``/
                          ``.joinpath``); or assigned to a local name that flows
                          (≤1 hop) into one of those. The silent-breakage set.
  4. needs-human-classification (FAIL-CLOSED) — a slashed path-string that is a
                          member of a collection literal (frozenset/set/tuple/list)
                          and is NOT marked (an unmarked git-pathspec, e.g. PCR's
                          ``_SOFT_FILE_SET`` before its B2 Class-B marker); OR a
                          file that fails to parse (one entry per file,
                          reason ``parse-error``). The human decides rewrite-vs-Class-B.
  5. doc-example-safe (reason ``prose-mention``) — a matched literal in no
                          path/git context (a bare diagnostic/message string). At
                          worst cosmetically stale post-flip, never a silent
                          path mis-resolve.

MATCH RULE (M1 + B-add-1): an ``ast.Constant`` str value ``v`` matches iff
``v == "architecture"`` / ``v == "diagnose-out"`` (bare whole-segment, B-add-1) OR
the slashed-prefix regex finds ``(?:^|[\\s'"(/=])(?:architecture|diagnose-out)/``
in ``v``. The trailing-slash form alone is NOT the gate — a bare ``"architecture"``
operand of ``repo_root / "architecture" / "x"`` is the most classic silent
mis-resolve and MUST be caught; CONTEXT (the ruleset) decides the class, not the
slash. The audit's own module is self-excluded by path.

DOCUMENTED RESIDUAL (slice-095 honest-contract): a vault path assembled fully
dynamically with NO ``architecture``/``diagnose-out`` string-literal segment
anywhere is invisible to a static scan (pinned by a residual-documenting test).

Usage:
    python -m tools.vault_flip_readiness_audit
    python -m tools.vault_flip_readiness_audit --json
    python -m tools.vault_flip_readiness_audit --strict
    python -m tools.vault_flip_readiness_audit --repo-root <repo-root>

Exit codes:
    0  clean — no needs-human-classification (and, under --strict, the
       must-rewrite + needs-human baseline is unchanged)
    2  gate — >=1 needs-human-classification, OR (--strict) baseline drift
    1  usage error (tools/ missing, a scanned file unreadable, repo-root bad)
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

# ── classes ──────────────────────────────────────────────────────────────────
ALREADY_SEAM_ROUTED = "already-seam-routed"
MUST_REWRITE = "must-rewrite-before-flip"
DOC_EXAMPLE_SAFE = "doc-example-safe"
NEEDS_HUMAN = "needs-human-classification"
# slice-102 / [[ADR-092]] — the two TESTS-surface classes (loud-breakage, not the
# production silent-breakage `must-rewrite`). On the `tests/**/*.py` surface the
# path-construction rules route to TEST_UPDATE_AT_FLIP (the update checklist — the
# test resolves a vault path, WILL break loudly at flip) and the
# unmarked-collection-pathspec rule routes to TEST_COLLECTION_PATHSPEC (a
# git-pathspec / `applies_to` / `_SOFT_FILE_SET` mirror — review-at-flip; for the
# current corpus all such members mirror Class-B production constants that STAY
# `architecture/…`, but the bucket is HETEROGENEOUS: a genuine path-resolve that is
# a bare collection-display member is demoted here too — review, NOT the checklist,
# NOT fail-closed. This is acceptable because the tests surface breaks LOUDLY at
# flip, so a mis-bucketed resolve surfaces as a failing test at flip-execute, NOT a
# silent mis-resolve; flip-execute MUST consume BOTH lists. Pinned residual:
# test_collection_member_genuine_resolve_is_review_residual.)
TEST_UPDATE_AT_FLIP = "test-update-at-flip"
TEST_COLLECTION_PATHSPEC = "test-collection-pathspec"
_ALL_CLASSES = (ALREADY_SEAM_ROUTED, MUST_REWRITE, DOC_EXAMPLE_SAFE, NEEDS_HUMAN,
                TEST_UPDATE_AT_FLIP, TEST_COLLECTION_PATHSPEC)
# The two classes whose (relpath, value) set is the regression baseline (AC3).
# PRODUCTION-surface only (slice-102: `baseline_tuple()` filters surface=="production"
# so a tests-surface occurrence can never pollute the production --strict pin).
_BASELINE_CLASSES = (MUST_REWRITE, NEEDS_HUMAN)

# ── match rule (M1 + B-add-1: bare-or-slashed) ────────────────────────────────
_BARE_SEGMENTS: frozenset[str] = frozenset({"architecture", "diagnose-out"})
_SLASHED_RE = re.compile(r"""(?:^|[\s'"(/=])(?:architecture|diagnose-out)/""")


def _value_matches(v: str) -> bool:
    return v in _BARE_SEGMENTS or _SLASHED_RE.search(v) is not None


# ── markers + seam (ADR-089 / slice-068 / ADR-065) ────────────────────────────
_CLASS_B_MARKER = "Class-B git identity (ADR-089)"
_ERROR_MSG_MARKER = "error-message prose"
_SEAM_MODULE_STEMS: frozenset[str] = frozenset({"_vault_paths", "_vault_git"})
_VAULT_ROOT_TOKEN = "VAULT_ROOT"

# ── argparse-help kwargs (prose, not a runtime path) ──────────────────────────
_HELP_KWARGS: frozenset[str] = frozenset({"help", "description", "epilog", "usage", "prog", "metavar"})

# ── path-construction sinks (rule 3) ──────────────────────────────────────────
_PATH_CTOR_NAMES: frozenset[str] = frozenset({"Path", "PurePath", "PurePosixPath", "PureWindowsPath"})
_PATH_METHODS: frozenset[str] = frozenset({
    "open", "read_text", "write_text", "read_bytes", "write_bytes",
    "glob", "rglob", "iterdir", "exists", "is_file", "is_dir", "joinpath",
    "with_name", "with_suffix", "mkdir", "unlink", "stat",
})
# slice-102 / [[ADR-092]] — for these path-METHODS the RECEIVER is the path but the
# positional ARGUMENT is CONTENT, not a path (`p.write_text("…architecture/…")` writes
# vault-shaped content INTO p; the literal in the arg is not a resolved path). The
# tests surface is full of `(tmp/x).write_text("<vault content>")`; treating that arg
# as path-construction over-flagged it (and produced a spurious dynamic-fragment on an
# f-string content). Correctness fix on BOTH surfaces — verified to leave the production
# _BASELINE (4 `/`-BinOp sites) unchanged.
_CONTENT_ARG_METHODS: frozenset[str] = frozenset({"write_text", "write_bytes"})

# slice-102 / [[ADR-092]] m1 — single source of truth for the unmarked-collection
# reason string, shared by `_classify_constant` (rule 4) and `_remap_for_tests` so the
# tests-surface collection remap cannot silently de-couple from the classifier (a rename
# is now a single-edit / fail-loud change, not a silent fall-through).
_REASON_UNMARKED_COLLECTION = "unmarked-collection-pathspec"

# ── the regression baseline (AC3) — EMPTIED at slice-106. This was the 4 bare-
# "architecture" `/`-BinOp path-construction sites in project_frame_synth.py (the
# genuine production-.py must-rewrite set frozen at slice-100); slice-106 routed all
# 4 through VAULT_ROOT, so the production must-rewrite surface is now ∅. (relpath,
# value, klass) tuples for the must-rewrite + needs-human classes, DUPLICATES INCLUDED
# (count-sensitive yet line-number-independent per M2). Re-derived by running the audit;
# pinned by test_vault_flip_readiness_audit.py::test_must_rewrite_baseline_pinned.
# A NEW unrouted production literal (here or elsewhere) re-populates this tuple →
# --strict + the AC3 pin trip. The classifier's must-rewrite non-vacuity does NOT
# depend on a real-repo site — it is proven synthetically by test_new_unrouted_literal_fails_gate.
_BASELINE: tuple[tuple[str, str, str], ...] = ()


# ── occurrence model ──────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Occurrence:
    path: str       # repo-relative, forward-slash
    line: int
    col: int
    value: str      # the matched constant value (or comment text), normalized
    klass: str
    reason: str
    surface: str = "production"   # slice-102 / ADR-092: "production" | "tests"

    def key(self) -> tuple[str, str, str]:
        # NOTE: surface is intentionally NOT in the key — the production baseline
        # key (path, value, klass) is unchanged (AC1); path already determines surface.
        return (self.path, self.value, self.klass)

    def to_dict(self) -> dict:
        return {"path": self.path, "line": self.line, "col": self.col,
                "value": self.value, "klass": self.klass, "reason": self.reason,
                "surface": self.surface}


@dataclass
class AuditResult:
    files_scanned: int = 0
    occurrences: list[Occurrence] = field(default_factory=list)

    def by_class(self, klass: str) -> list[Occurrence]:
        return [o for o in self.occurrences if o.klass == klass]

    def baseline_tuple(self) -> tuple[tuple[str, str, str], ...]:
        # PRODUCTION-surface only (slice-102 / ADR-092 — defense-in-depth: a
        # tests-surface regression can never silently pollute the production --strict pin).
        keys = [o.key() for o in self.occurrences
                if o.klass in _BASELINE_CLASSES and o.surface == "production"]
        return tuple(sorted(keys))

    @property
    def needs_human(self) -> list[Occurrence]:
        return self.by_class(NEEDS_HUMAN)

    def to_dict(self) -> dict:
        counts = {k: len(self.by_class(k)) for k in _ALL_CLASSES}
        return {
            "files_scanned": self.files_scanned,
            "counts": counts,
            "occurrences": [o.to_dict() for o in self.occurrences],
        }


# ── AST helpers (parent pointers + docstrings + ≤1-hop flow) ──────────────────
_PARENT_ATTR = "_vfr_parent"


def _annotate_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, _PARENT_ATTR, parent)


def _parent(node: ast.AST) -> ast.AST | None:
    return getattr(node, _PARENT_ATTR, None)


def _docstring_const_ids(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                ids.add(id(body[0].value))
    return ids


def _enclosing_func(node: ast.AST) -> ast.AST | None:
    p = _parent(node)
    while p is not None and not isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
        p = _parent(p)
    return p


def _is_path_ctor(func: ast.expr) -> bool:
    if isinstance(func, ast.Name):
        return func.id in _PATH_CTOR_NAMES
    if isinstance(func, ast.Attribute):
        return func.attr in _PATH_CTOR_NAMES
    return False


def _in_help_kwarg(node: ast.AST) -> bool:
    p = _parent(node)
    return isinstance(p, ast.keyword) and p.arg in _HELP_KWARGS


def _is_div_operand(node: ast.AST) -> bool:
    p = _parent(node)
    return isinstance(p, ast.BinOp) and isinstance(p.op, ast.Div)


def _is_path_call_arg_or_recv(node: ast.AST) -> bool:
    """The node is an arg to Path(...)/PurePath(...) OR an arg/receiver of a path
    method call (``X.read_text(...)`` / ``X.joinpath("architecture", ...)``)."""
    p = _parent(node)
    if isinstance(p, ast.Call):
        if _is_path_ctor(p.func) and node in p.args:
            return True
        if isinstance(p.func, ast.Attribute) and p.func.attr in _PATH_METHODS:
            # the receiver (X in X.read_text()) is always the path
            if node is p.func.value:
                return True
            # an ARG is a path UNLESS the method takes CONTENT as its arg
            # (write_text/write_bytes — slice-102 / ADR-092 correctness fix)
            if node in p.args and p.func.attr not in _CONTENT_ARG_METHODS:
                return True
        # m1: builtin open(target, ...) — the first positional arg is the path
        if isinstance(p.func, ast.Name) and p.func.id == "open" and p.args and node is p.args[0]:
            return True
        # m1: os.path.join("architecture", ...) — any positional arg
        if isinstance(p.func, ast.Attribute) and p.func.attr == "join" \
                and isinstance(p.func.value, ast.Attribute) and p.func.value.attr == "path" \
                and node in p.args:
            return True
    # receiver of a path-method: node is the .value of an Attribute that is a call func
    if isinstance(p, ast.Attribute) and p.attr in _PATH_METHODS and node is p.value:
        gp = _parent(p)
        if isinstance(gp, ast.Call) and gp.func is p:
            return True
    return False


def _direct_path_construction(node: ast.AST) -> bool:
    return _is_div_operand(node) or _is_path_call_arg_or_recv(node)


def _assigned_name(node: ast.AST) -> str | None:
    """If ``node`` is the full RHS value of an ``x = <node>`` / ``x: T = <node>``
    assignment to a single Name, return ``x``; else None (≤1-hop flow seed)."""
    p = _parent(node)
    if isinstance(p, ast.Assign) and node is p.value and len(p.targets) == 1 \
            and isinstance(p.targets[0], ast.Name):
        return p.targets[0].id
    if isinstance(p, ast.AnnAssign) and node is p.value and isinstance(p.target, ast.Name):
        return p.target.id
    return None


def _name_flows_to_path(name: str, func: ast.AST | None) -> bool:
    """≤1-hop forward flow: ``name`` is used as a path-construction operand
    somewhere in ``func`` (Div operand / Path-ctor arg / path-method receiver)."""
    if func is None:
        return False
    for n in ast.walk(func):
        if isinstance(n, ast.Name) and n.id == name:
            if _is_div_operand(n) or _is_path_call_arg_or_recv(n):
                return True
    return False


def _is_collection_member(node: ast.AST) -> bool:
    """The literal is an element of a Set/List/Tuple display (e.g. a frozenset({...})
    git-pathspec set such as PCR's _SOFT_FILE_SET)."""
    p = _parent(node)
    return isinstance(p, (ast.Set, ast.List, ast.Tuple))


def _module_root(node: ast.AST) -> ast.AST | None:
    """Walk parents to the enclosing ast.Module — the ≤1-hop flow-scope fallback
    when a literal is assigned at MODULE level (M1: `_enclosing_func` returns None
    there, which silently killed the documented assigned-name-flow capability)."""
    p = _parent(node)
    while p is not None and not isinstance(p, ast.Module):
        p = _parent(p)
    return p


def _dynamic_fragment_in_path(node: ast.AST) -> bool:
    """The matched constant is a FRAGMENT of a composed string (f-string or
    ``+``-concat) whose composite flows into a path-construction context — only a
    fragment is constant, so the full path is ambiguous (M3 → fail-closed
    needs-human, NOT a silent prose-mention)."""
    p = _parent(node)
    if isinstance(p, ast.JoinedStr):
        composite: ast.AST = p
    elif isinstance(p, ast.BinOp) and isinstance(p.op, ast.Add):
        composite = p
    else:
        return False
    return _direct_path_construction(composite)


# ── classification ────────────────────────────────────────────────────────────
def _line_text(lines: list[str], lineno: int) -> str:
    return lines[lineno - 1] if 1 <= lineno <= len(lines) else ""


def _classify_constant(
    node: ast.Constant,
    *,
    module_stem: str,
    docstring_ids: set[int],
    lines: list[str],
) -> tuple[str, str]:
    """Return (klass, reason) for a matched str-Constant via the ordered ruleset."""
    line_txt = _line_text(lines, node.lineno)

    # rule 1 — node-based prose that CANNOT coexist with a path-construction node
    if id(node) in docstring_ids:
        return (DOC_EXAMPLE_SAFE, "docstring")
    if _in_help_kwarg(node):
        return (DOC_EXAMPLE_SAFE, "argparse-help")
    # the seam modules' OWN architecture literals are seam machinery (the `_DEFAULT`
    # definition / git-string derivations) — routed by definition, even when they flow
    # into a `Path(...)` (e.g. `_vault_paths._DEFAULT`). A MODULE fact, so checked
    # BEFORE path-construction (unlike the line-text markers below, which come after —
    # M2; this restores the seam default to already-routed after the M2 reorder).
    if module_stem in _SEAM_MODULE_STEMS:
        return (ALREADY_SEAM_ROUTED, "seam-internal")

    # rule 2 — path-construction context, the silent-breakage set. Checked BEFORE the
    # line-text markers (M2 / slice-099 whole-line-substring lesson): a prose comment
    # mentioning a marker on a real RESOLVING line must NOT false-route it to routed.
    # Class-B git-pathspecs are collection members (not path-construction), so they
    # still fall through to the marker rule below — the legitimate case is preserved.
    if _dynamic_fragment_in_path(node):                       # M3 — fail-closed
        return (NEEDS_HUMAN, "dynamic-fragment")
    if _direct_path_construction(node):
        return (MUST_REWRITE, "path-construction")
    name = _assigned_name(node)
    if name is not None and _name_flows_to_path(name, _enclosing_func(node) or _module_root(node)):  # M1
        return (MUST_REWRITE, "path-construction-1hop")

    # rule 3 — line-text markers / seam (reached only when NOT a path-construction)
    if _ERROR_MSG_MARKER in line_txt:
        return (DOC_EXAMPLE_SAFE, "error-message-prose-marked")
    if _CLASS_B_MARKER in line_txt:
        return (ALREADY_SEAM_ROUTED, "class-b-marked")
    if _VAULT_ROOT_TOKEN in line_txt:
        return (ALREADY_SEAM_ROUTED, "vault-root-derived")

    # rule 4 — fail-closed ambiguous (unmarked git-pathspec collection member)
    if _is_collection_member(node) and "/" in node.value:
        return (NEEDS_HUMAN, _REASON_UNMARKED_COLLECTION)

    # rule 5 — default: prose-mention (a message/diagnostic string, no path/git ctx)
    return (DOC_EXAMPLE_SAFE, "prose-mention")


# ── scan ──────────────────────────────────────────────────────────────────────
def _norm_value(v: str) -> str:
    """Normalize a matched value for stable identity (collapse internal newlines /
    runs of whitespace from implicit string concatenation — M2)."""
    return re.sub(r"\s+", " ", v).strip()


def _surface_of(rel: str) -> str:
    """slice-102 / [[ADR-092]]: the scan surface, derived from the NORMALIZED
    repo-relative path (m2 — robust to a backslash rel from a direct caller;
    `tools/test_first_audit.py` correctly stays production, not tests)."""
    return "tests" if rel.replace("\\", "/").startswith("tests/") else "production"


def _remap_for_tests(klass: str, reason: str) -> str:
    """slice-102 / [[ADR-092]] — tests-surface loud-vs-silent remap. Path-construction
    (the production SILENT `must-rewrite`) becomes the loud update checklist; an
    unmarked-collection-pathspec (a git-pathspec/Class-B mirror — fail-closed
    needs-human on production) becomes the REVIEW list (TEST_COLLECTION_PATHSPEC —
    NOT the checklist, NOT fail-closed). All other classes (docstring / seam /
    dynamic-fragment→needs-human / prose-mention / parse-error) are surface-independent —
    a genuinely-unclassifiable tests literal still routes to needs-human (fail-closed)."""
    if klass == MUST_REWRITE:
        return TEST_UPDATE_AT_FLIP
    if klass == NEEDS_HUMAN and reason == _REASON_UNMARKED_COLLECTION:
        return TEST_COLLECTION_PATHSPEC
    return klass


def audit_file(path: Path, rel: str) -> list[Occurrence]:
    """Classify every matched literal + comment in one file. A SyntaxError yields a
    single needs-human(parse-error) occurrence (fail-closed, never a silent skip).
    The surface (production | tests) is derived from `rel` and tags every Occurrence;
    on the tests surface the classes are remapped per `_remap_for_tests` (ADR-092)."""
    surface = _surface_of(rel)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    occ: list[Occurrence] = []

    # AST string-literal occurrences
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return [Occurrence(rel, exc.lineno or 1, (exc.offset or 1) - 1,
                           f"<parse-error: {exc.msg}>", NEEDS_HUMAN, "parse-error", surface)]
    _annotate_parents(tree)
    docstring_ids = _docstring_const_ids(tree)
    module_stem = path.stem
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and _value_matches(node.value):
            klass, reason = _classify_constant(
                node, module_stem=module_stem, docstring_ids=docstring_ids, lines=lines)
            if surface == "tests":
                klass = _remap_for_tests(klass, reason)
            occ.append(Occurrence(rel, node.lineno, node.col_offset,
                                  _norm_value(node.value), klass, reason, surface))

    # COMMENT-token occurrences (always doc-example-safe; not in the baseline)
    try:
        toks = tokenize.generate_tokens(io.StringIO(text).readline)
        for tok in toks:
            if tok.type == tokenize.COMMENT and _SLASHED_RE.search(tok.string):
                occ.append(Occurrence(rel, tok.start[0], tok.start[1],
                                      _norm_value(tok.string), DOC_EXAMPLE_SAFE, "comment", surface))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass  # comment harvest is best-effort (3.12+ tokenizer may raise SyntaxError — m2); AST pass is load-bearing

    return occ


def _iter_scan_files(root: Path) -> list[Path]:
    """PRODUCTION surface: tools/*.py (flat) + skills/**/*.py (recursive), excluding
    the audit's own module. TESTS surface (slice-102 / [[ADR-092]]): tests/**/*.py
    (recursive), EXCLUDING any path with a `fixtures/` segment — fixture dirs hold
    test-INPUT artifacts (synthetic / deliberately-malformed data), not vault-resolving
    test logic (documented residual: a vault literal inside a `fixtures/` dir is out
    of scan scope — pinned by test_fixtures_dir_vault_literal_out_of_scope)."""
    self_name = "vault_flip_readiness_audit.py"
    files: list[Path] = []
    tools_dir = root / "tools"
    if tools_dir.exists():
        files += [p for p in tools_dir.glob("*.py") if p.name != self_name]
    skills_dir = root / "skills"
    if skills_dir.exists():
        files += list(skills_dir.glob("**/*.py"))
    tests_dir = root / "tests"
    if tests_dir.exists():
        files += [p for p in tests_dir.glob("**/*.py")
                  if "fixtures" not in p.relative_to(root).parts]
    return sorted(files)


def audit_root(root: Path) -> AuditResult:
    result = AuditResult()
    for path in _iter_scan_files(root):
        result.files_scanned += 1
        rel = str(path.relative_to(root)).replace("\\", "/")
        result.occurrences.extend(audit_file(path, rel))
    result.occurrences.sort(key=lambda o: (o.path, o.line, o.col))
    return result


# ── output / gate ─────────────────────────────────────────────────────────────
def _format_human(result: AuditResult, baseline_drift: tuple | None) -> str:
    counts = {k: len(result.by_class(k)) for k in _ALL_CLASSES}
    # m3: only bracket the SURFACE-EXCLUSIVE classes by surface (must-rewrite is
    # production-only; update-at-flip + collection-pathspec are tests-only). The
    # remaining classes span both surfaces, so report them as cross-surface totals.
    out = [
        "Vault-flip readiness audit (ADR-091/092): "
        f"{result.files_scanned} file(s); "
        f"[production] {counts[MUST_REWRITE]} must-rewrite; "
        f"[tests] {counts[TEST_UPDATE_AT_FLIP]} update-at-flip, "
        f"{counts[TEST_COLLECTION_PATHSPEC]} collection-pathspec(review); "
        f"[both] {counts[ALREADY_SEAM_ROUTED]} already-routed, "
        f"{counts[DOC_EXAMPLE_SAFE]} doc/example, {counts[NEEDS_HUMAN]} needs-human.\n",
    ]
    for o in result.by_class(MUST_REWRITE):
        out.append(f"  [must-rewrite]     {o.path}:{o.line} ({o.reason}) {o.value!r}\n")
    for o in result.by_class(TEST_UPDATE_AT_FLIP):
        out.append(f"  [test-update]      {o.path}:{o.line} ({o.reason}) {o.value!r}\n")
    for o in result.needs_human:
        out.append(f"  [needs-human]      {o.path}:{o.line} ({o.reason}) {o.value!r}\n")
    if baseline_drift is not None:
        added, removed = baseline_drift
        out.append("\n--strict BASELINE DRIFT:\n")
        for k in added:
            out.append(f"  + {k}\n")
        for k in removed:
            out.append(f"  - {k}\n")
    return "".join(out)


def _baseline_drift(result: AuditResult) -> tuple[list, list] | None:
    """(added, removed) vs the frozen _BASELINE, or None if unchanged."""
    live = result.baseline_tuple()
    base = tuple(sorted(_BASELINE))
    if live == base:
        return None
    from collections import Counter
    lc, bc = Counter(live), Counter(base)
    added = sorted((lc - bc).elements())
    removed = sorted((bc - lc).elements())
    return (added, removed)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="vault_flip_readiness_audit",
        description=(
            "ADR-091 vault-flip readiness: classify every architecture/ + "
            "diagnose-out/ path literal on the production-.py surface so the flip "
            "has a complete, regression-pinned checklist. Read-only; no flip."
        ),
    )
    parser.add_argument("--repo-root", "--root", dest="repo_root", type=Path, default=None,
                        help="Repo root (defaults to the parent of this tools/ dir)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true",
                        help="Also gate (exit 2) on must-rewrite+needs-human baseline drift")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve() if args.repo_root is not None else Path(__file__).resolve().parent.parent
    if not (root / "tools").exists():
        sys.stderr.write(f"tools/ directory not found at {root}\n")
        return 1
    try:
        result = audit_root(root)
    except OSError as exc:
        sys.stderr.write(f"vault_flip_readiness_audit: unreadable source — {exc}\n")
        return 1

    drift = _baseline_drift(result) if args.strict else None

    if args.json:
        payload = result.to_dict()
        payload["baseline_drift"] = (
            {"added": drift[0], "removed": drift[1]} if drift is not None else None)
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result, drift))

    if result.needs_human:
        return 2
    if args.strict and drift is not None:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
