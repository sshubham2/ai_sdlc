"""SCMD-1 — shippability-catalog machine-stable-command + incidental-decoupling audit.

Per SCMD-1 (methodology-changelog.md v0.45.0; slice-031, split-lineage label
"030B"; [[ADR-030]] + [[ADR-031]]). Two independent checks over
`architecture/shippability.md`:

(a) machine-stable command — every catalog data row carries a `Machine-cmd`
    cell (the 6th column) that is one OR MORE `;`-separated, prose-free,
    interpreter-anchored pytest invocations. The anchor (each segment must
    START with the interpreter token) is what rejects a narrative prose cell
    such as a `Commands:`-prefixed narrative cell. A row missing the column,
    or any segment failing the anchored full-match, is a violation — never a
    silent skip (a silent skip would also disable PTFCD-1 for that row, B3).

(b) incidental-decoupling invariant — the cited-fn set is mechanically
    re-derived from EVERY row's `Machine-cmd` cell (not a hand-coded subset).
    Each resolved test function is AST-classified by the read-shape it
    statically exhibits (incidental / essential / clean — SCMD-1's policing
    scope is the INCIDENTAL class ONLY):

      * incidental  → reaches gitignored `architecture/slices/archive/**`,
                       gitignored `architecture/build-checks.md`, or untracked
                       `~/.claude/build-checks.md`. MUST be decoupled to a
                       byte-faithful git-tracked input (slice-030A canonical
                       fixtures + the ADR-030 verbatim corpus). Presence ⇒
                       VIOLATION (the invariant this slice exists to enforce).
      * essential   → reaches `~/.claude/methodology-changelog.md`. That read
                       IS the in-repo↔installed forward-sync assertion (no
                       BCI-1 analogue). RECOGNIZED and explicitly NOT flagged
                       — chartered to slice-030C (label) per the R-4 sub-entry.
      * clean       → anything else. Per the design's principled scope
                       boundary (ADR-031), OTHER `~/.claude/...` reads
                       (skill-drift, diagnose pins, …) are OUT OF 030B's scope
                       — same rationale as essential-not-flagged. Closed-world
                       completeness for the REAL indirection vector is via
                       module-constant + same-module helper-call resolution
                       (`_reachable_path_segments`), NOT by flagging every
                       `Path.home()` use (that would be a category error — M1
                       scoped to the incidental class).

The shared artifact with `tools/shippability_path_audit.py` is ONLY the
token-extraction predicate (`_TEST_PATH_RE` + table-cell parsing). The
grammar/segment validator and the AST classifier are net-new here (m2):
`shippability_path_audit` cannot reject prose; SCMD-1 (a) is what does.

Usage:
    python -m tools.shippability_decoupling_audit architecture/shippability.md
    python -m tools.shippability_decoupling_audit architecture/shippability.md --json

Exit codes:
    0  clean (or empty / zero-row catalog)
    1  >=1 SCMD-1 violation (prose/missing Machine-cmd, OR an incidental
       cited fn)
    2  usage error (catalog missing/unreadable, or a cited module / its
       referenced conftest fails to ast.parse)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

from tools import _stdout
from tools.shippability_path_audit import (  # shared token-extraction predicate
    _TEST_PATH_RE,
    _find_repo_root,
    _is_separator_row,
    _parse_table_cells,
)

# --- (a) machine-stable command grammar -------------------------------------
# Each ;-separated segment, trimmed, must FULL-MATCH this anchored shape. The
# leading anchor (segment starts with the interpreter token) is the mechanism
# that rejects a prose cell like `Commands: \`python -m pytest ...\``.
_INTERP = r"(?:<interp>|python|[^\s;]*python(?:\.exe)?)"
_SEGMENT_RE = re.compile(
    rf"^{_INTERP}(?:\s+-W\s+\S+)?\s+-m\s+pytest\s+"
    r"(?:tests/\S+?\.py(?:::\S+)?|tests/\S+)"  # >=1 tests/-rooted target
    r"(?:\s+\S+)*$"
)

# --- (b) read-shape classification ------------------------------------------
# Ordered string-segment subsequences. A fn is classified by the segments its
# reachable Path-producing expressions compose.
_INCIDENTAL_SHAPES: tuple[tuple[str, ...], ...] = (
    ("architecture", "slices", "archive"),
    ("architecture", "build-checks.md"),
    (".claude", "build-checks.md"),
)
_ESSENTIAL_SHAPES: tuple[tuple[str, ...], ...] = (
    (".claude", "methodology-changelog.md"),
)

# Tracked-fixture-producing symbols an incidental-decoupled fn MAY reach
# (concrete membership — v2-M2; asserted by test_allowlist_membership_is_exactly).
_ALLOWLIST_SYMBOLS = frozenset({
    "_CANONICAL_PROJECT_FIXTURE",
    "_CANONICAL_GLOBAL_FIXTURE",
    "_ARCHIVE_BACKTEST_CORPUS",   # ADR-030 verbatim-corpus accessor (T5)
})
# Resolve-through (follow transitively; not themselves coupling).
_RESOLVE_THROUGH = frozenset({"REPO_ROOT", "read_file", "FIXTURES", "Path"})
# `_GLOBAL_BUILD_CHECKS` is deliberately NOT a member — any fn still reaching
# it is incidental coupling (it resolves to ~/.claude/build-checks.md).


@dataclass(frozen=True)
class Violation:
    kind: str          # "missing-machine-cmd" | "prose-segment" |
                        # "incidental-coupling"
    row: str           # catalog row number (or "-" for fn-level)
    detail: str
    line: int = 0

    def to_dict(self) -> dict:
        return {"kind": self.kind, "row": self.row,
                "detail": self.detail, "line": self.line}


@dataclass
class AuditResult:
    rows_scanned: int = 0
    cited_fns: int = 0
    incidental: list[str] = field(default_factory=list)
    essential: list[str] = field(default_factory=list)
    clean: list[str] = field(default_factory=list)
    derived_archive_folders: set[str] = field(default_factory=set)
    violations: list[Violation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rows_scanned": self.rows_scanned,
            "cited_fns": self.cited_fns,
            "incidental": sorted(self.incidental),
            "essential": sorted(self.essential),
            "clean": sorted(self.clean),
            "derived_archive_folders": sorted(self.derived_archive_folders),
            "violations": [v.to_dict() for v in self.violations],
            "summary": {"violation_count": len(self.violations)},
        }


# --------------------------------------------------------------------------- #
# Catalog parsing                                                             #
# --------------------------------------------------------------------------- #
def _catalog_rows(text: str) -> list[tuple[int, list[str]]]:
    """Return [(1-based-line, cells)] for catalog DATA rows only."""
    out: list[tuple[int, list[str]]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        if not s.startswith("|") or _is_separator_row(line):
            continue
        cells = _parse_table_cells(line)
        if not cells:
            continue
        row_num = cells[0]
        if row_num.lower() in {"#", ""} or not any(c.isdigit() for c in row_num):
            continue  # header / non-data row
        out.append((i, cells))
    return out


# Column index of the machine-stable command: catalog schema becomes
# | # | Slice | Critical path | Command | Runtime | Machine-cmd |  → index 5.
_MACHINE_CMD_IDX = 5


def _machine_cmd_cell(cells: list[str]) -> str | None:
    if len(cells) <= _MACHINE_CMD_IDX:
        return None
    return cells[_MACHINE_CMD_IDX].strip()


def _segments(machine_cmd: str) -> list[str]:
    """Split on `;`, then strip surrounding markdown backtick fence + ws from
    EACH segment. Catalog cells fence every command individually
    (`` `cmd1` ; `cmd2` ``), so a single outer-fence strip is insufficient."""
    out: list[str] = []
    for raw in machine_cmd.split(";"):
        seg = raw.strip().strip("`").strip()
        if seg:
            out.append(seg)
    return out


def _check_machine_cmd(result: AuditResult, line: int, row: str,
                       cells: list[str]) -> str | None:
    """Check (a). Returns the raw Machine-cmd cell if structurally OK, else
    records a violation and returns None."""
    cell = _machine_cmd_cell(cells)
    if cell is None or cell == "":
        result.violations.append(Violation(
            "missing-machine-cmd", row,
            "row has no Machine-cmd (6th) column cell — would silently "
            "disable PTFCD-1 for this row", line))
        return None
    segs = _segments(cell)
    if not segs:
        result.violations.append(Violation(
            "prose-segment", row,
            f"Machine-cmd cell has zero parseable segments: {cell!r}", line))
        return None
    for seg in segs:
        if not _SEGMENT_RE.fullmatch(seg):
            result.violations.append(Violation(
                "prose-segment", row,
                f"segment is not an interpreter-anchored pytest invocation "
                f"(prose/narrative rejected): {seg!r}", line))
            return None
    return cell


# --------------------------------------------------------------------------- #
# Cited-fn derivation                                                         #
# --------------------------------------------------------------------------- #
def _cited(machine_cmd: str) -> list[tuple[str, str | None, str | None]]:
    """From a Machine-cmd cell return [(test_path, selector|None, k_expr|None)].

    Reuses the shared `_TEST_PATH_RE` predicate (post-`pytest` scoping per
    segment). `selector` is the `::name` (may be a glob); `k_expr` is the
    `-k EXPR` value if present (pytest substring/keyword filter)."""
    out: list[tuple[str, str | None, str | None]] = []
    for seg in _segments(machine_cmd):
        idx = seg.find("pytest")
        if idx == -1:
            continue
        post = seg[idx + len("pytest"):]
        k_expr = None
        km = re.search(r"-k\s+(\S+)", post)
        if km:
            k_expr = km.group(1).strip("\"'")
        for m in _TEST_PATH_RE.finditer(post):
            raw = m.group(0)
            # capture an optional ::selector that the shared predicate strips
            tail = post[m.end():]
            sel = None
            sm = re.match(r"::(\S+)", tail)
            if sm:
                sel = sm.group(1).strip("`\"'")
            out.append((raw, sel, k_expr))
    return out


# --------------------------------------------------------------------------- #
# AST read-shape classifier (closed-world, fail-closed)                       #
# --------------------------------------------------------------------------- #
# Names that root a path-chain at the REAL gitignored vault / untracked home.
# A `/`-chain rooted at a test-local (`root`, `tmp_path`, a `fake_home` dir)
# is a SYNTHETIC fixture tree (environment-independent) and MUST NOT be read
# as incidental coupling — the BCI-1 tests build `tmp_path/"architecture"/
# "build-checks.md"` + monkeypatch `Path.home()`; they are not vault reads.
_REAL_VAULT_ROOT_NAMES = frozenset({"REPO_ROOT"})


def _div_chain_root(node: ast.AST) -> ast.AST:
    """Leftmost atom of a `a / b / c` chain (descend `.left` while Div)."""
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        node = node.left
    return node


def _is_real_vault_root(atom: ast.AST,
                        extra_root_names: frozenset[str] = frozenset()) -> bool:
    """True iff `atom` is `REPO_ROOT` / `Path.home()` / `Path.cwd()`, OR a
    module-constant name (in `extra_root_names`) that transitively resolves to
    one of those. The transitive set lets `_ARCHIVE_BACKTEST_CORPUS = REPO_ROOT
    / ...` (and `_CANONICAL_* = FIXTURES = REPO_ROOT / ...`) count as real-
    vault-rooted, so a `<const> / "slice-001"` chain is fully resolved — while
    a test-local (`root`, `tmp_path`) is NOT a module const and stays excluded
    (the BCI-1 synthetic-tree false-positive fix is preserved)."""
    if isinstance(atom, ast.Name) and (
            atom.id in _REAL_VAULT_ROOT_NAMES or atom.id in extra_root_names):
        return True
    if isinstance(atom, ast.Call):
        f = atom.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) \
                and f.value.id == "Path" and f.attr in {"home", "cwd"}:
            return True
    return False


def _real_vault_const_names(mod: "_ModuleIndex") -> frozenset[str]:
    """Module-const names whose value chain transitively roots at the real
    vault/home (fixpoint over `REPO_ROOT` / `Path.home()` / each other)."""
    resolved: set[str] = set()
    changed = True
    while changed:
        changed = False
        for name, value in mod.module_consts.items():
            if name in resolved:
                continue
            root = _div_chain_root(value)
            if _is_real_vault_root(root, frozenset(resolved)):
                resolved.add(name)
                changed = True
    return frozenset(resolved)


def _path_segments_in(node: ast.AST,
                      extra_root_names: frozenset[str] = frozenset()) -> set[str]:
    """Str constants that are REAL-VAULT PATH segments.

    Collected ONLY from a `/` BinOp chain whose leftmost atom is the real
    vault/home root (`REPO_ROOT` / `Path.home()`), or a literal arg to
    `read_file(...)` (conftest helper — always repo-rooted). A chain rooted at
    a test-local (`root`, `tmp_path`, fixture dir) is a synthetic tree and
    contributes NOTHING (the BCI-1-tests false-positive class). Module-const
    indirection (`_GLOBAL_BUILD_CHECKS = Path.home()/.claude/...`) is handled
    by the caller passing the const's *value* node here — that value IS a
    `Path.home()`-rooted chain, so root-anchoring still holds.

    Deliberately NOT all string constants: docstrings / assert-message prose
    contain words like "architecture" and must not pollute classification.
    Order-independent (set) — `ast.walk` is BFS, not source order."""
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            # Only the OUTERMOST Div of a chain (its parent is not a Div with
            # this as .left) needs handling, but walking every Div and
            # root-checking each is simplest and idempotent.
            if not _is_real_vault_root(_div_chain_root(n), extra_root_names):
                continue
            for sub in ast.walk(n):
                if isinstance(sub, ast.Constant) \
                        and isinstance(sub.value, str):
                    out.add(sub.value)
        elif isinstance(n, ast.Call):
            f = n.func
            name = (f.attr if isinstance(f, ast.Attribute)
                    else f.id if isinstance(f, ast.Name) else "")
            if name == "read_file":  # conftest helper — always repo-rooted
                for a in n.args:
                    if isinstance(a, ast.Constant) \
                            and isinstance(a.value, str):
                        out.add(a.value)
    return out


def _names_in(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


@dataclass
class _ModuleIndex:
    tree: ast.Module
    funcs: dict[str, ast.FunctionDef]
    module_consts: dict[str, ast.AST]   # module-level Name -> value expr


def _index_module(path: Path) -> _ModuleIndex:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    funcs: dict[str, ast.FunctionDef] = {}
    consts: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs[node.name] = node  # type: ignore[assignment]
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    consts[tgt.id] = node.value
    return _ModuleIndex(tree, funcs, consts)


def _reachable_path_segments(fn: ast.FunctionDef, mod: _ModuleIndex,
                             _seen: set[str] | None = None) -> set[str]:
    """Path segments reachable from `fn`: its own path-exprs, PLUS module-level
    constants it references (constant indirection — the real `_GLOBAL_BUILD_
    CHECKS = Path.home()/.claude/...` vector), PLUS same-module helper functions
    it calls (call indirection — closed-world completeness for M1: an incidental
    path built inside a local helper must not sneak past). Bounded by `_seen`."""
    if _seen is None:
        _seen = set()
    extra = _real_vault_const_names(mod)
    segs: set[str] = set(_path_segments_in(fn, extra))
    for nm in _names_in(fn):
        if nm in mod.module_consts:
            segs |= _path_segments_in(mod.module_consts[nm], extra)
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            callee = n.func.id
            if callee in mod.funcs and callee not in _seen:
                _seen.add(callee)
                segs |= _reachable_path_segments(
                    mod.funcs[callee], mod, _seen)
    return segs


def classify_fn(fn: ast.FunctionDef, mod: _ModuleIndex) -> str:
    """Return 'incidental' | 'essential' | 'clean'.

    SCMD-1's policing scope is the INCIDENTAL class ONLY (gitignored archive /
    gitignored `architecture/build-checks.md` / untracked
    `~/.claude/build-checks.md`). Per the design's principled scope boundary
    (ADR-031), the *essential* class (`~/.claude/methodology-changelog.md`) is
    recognized-and-NOT-flagged (030C domain) — and, by the SAME rationale, any
    OTHER `~/.claude/...` read (skill-drift, diagnose pins, etc.) is OUT OF
    SCOPE for 030B and classifies `clean`. Flagging every `Path.home()` use
    would be a category error (those are other slices' rows). Closed-world
    completeness for the *real* indirection vector is achieved by resolving
    module constants AND same-module helper calls (`_reachable_path_segments`)
    — that is what catches incidental coupling hidden behind indirection,
    without false-positives on benign unrelated home reads."""
    segs = _reachable_path_segments(fn, mod)
    for shape in _ESSENTIAL_SHAPES:          # essential first (030C; not flagged)
        if set(shape) <= segs:
            return "essential"
    for shape in _INCIDENTAL_SHAPES:         # the only flagged class
        if set(shape) <= segs:
            return "incidental"
    return "clean"                            # out of SCMD-1's policing scope


def _collect_archive_folders(fn: ast.FunctionDef, mod: _ModuleIndex) -> set[str]:
    """Slice-folder names a backtest reads — pre-decouple from the gitignored
    archive, post-decouple from the tracked corpus (for AC4 completeness)."""
    extra = _real_vault_const_names(mod)
    segs: set[str] = set(_path_segments_in(fn, extra))
    for nm in _names_in(fn):
        if nm in mod.module_consts:
            segs |= _path_segments_in(mod.module_consts[nm], extra)
    return {s for s in segs if s.startswith("slice-") and "archive" not in s}


# --------------------------------------------------------------------------- #
# Orchestration                                                               #
# --------------------------------------------------------------------------- #
def audit(catalog_path: Path, repo_root: Path | None = None) -> AuditResult:
    result = AuditResult()
    text = catalog_path.read_text(encoding="utf-8")
    # Cited `tests/...` paths are repo-relative. Production: the catalog is
    # in-repo so `_find_repo_root(catalog)` resolves correctly. Tests pass an
    # explicit repo_root so a synthetic catalog in tmp_path still resolves the
    # real cited modules.
    if repo_root is None:
        repo_root = _find_repo_root(catalog_path)
    module_cache: dict[Path, _ModuleIndex] = {}

    for line, cells in _catalog_rows(text):
        result.rows_scanned += 1
        row = cells[0]
        machine_cmd = _check_machine_cmd(result, line, row, cells)
        if machine_cmd is None:
            continue
        for test_path, selector, k_expr in _cited(machine_cmd):
            mod_path = repo_root / test_path
            if not mod_path.exists():
                continue  # PTFCD-1 owns phantom-path; SCMD-1 skips non-py here
            if mod_path not in module_cache:
                module_cache[mod_path] = _index_module(mod_path)
            mod = module_cache[mod_path]
            # resolve which fns this token cites
            if selector and "*" not in selector and "[" not in selector \
                    and selector in mod.funcs:
                targets = [selector]
            elif selector and ("*" in selector or "[" in selector):
                targets = [f for f in mod.funcs if fnmatch(f, selector)]
            elif k_expr:
                targets = [f for f in mod.funcs
                           if k_expr in f and f.startswith("test_")]
            else:
                targets = [f for f in mod.funcs if f.startswith("test_")]
            for fname in targets:
                result.cited_fns += 1
                cls = classify_fn(mod.funcs[fname], mod)
                qual = f"{test_path}::{fname}"
                if cls == "incidental":
                    result.incidental.append(qual)
                    result.derived_archive_folders |= _collect_archive_folders(
                        mod.funcs[fname], mod)
                    result.violations.append(Violation(
                        "incidental-coupling", row,
                        f"{qual} reaches gitignored/untracked incidental "
                        f"state (archive corpus / live build-checks / "
                        f"~/.claude/build-checks.md) — must be decoupled to "
                        f"a tracked byte-faithful input", line))
                elif cls == "essential":
                    result.essential.append(qual)  # recognized, NOT flagged
                else:
                    result.clean.append(qual)
    return result


def _format_human(r: AuditResult) -> str:
    if not r.violations:
        return (
            f"SCMD-1 audit: clean. {r.rows_scanned} row(s); "
            f"{r.cited_fns} cited fn(s) — incidental={len(r.incidental)} "
            f"essential={len(r.essential)} (recognized, 030C) "
            f"clean={len(r.clean)}.\n")
    out = [f"{len(r.violations)} SCMD-1 violation(s):\n\n"]
    for v in r.violations:
        loc = f"shippability.md:{v.line} " if v.line else ""
        out.append(f"  [Important] {loc}row {v.row} [{v.kind}]\n"
                   f"    {v.detail}\n\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="shippability_decoupling_audit",
        description="SCMD-1 machine-stable-command + incidental-decoupling audit",
    )
    parser.add_argument("catalog", type=Path,
                        help="Path to architecture/shippability.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    catalog_path: Path = args.catalog
    if not catalog_path.is_file():
        sys.stderr.write(f"usage error: catalog not found: {catalog_path}\n")
        return 2
    try:
        result = audit(catalog_path)
    except SyntaxError as e:
        sys.stderr.write(f"usage error: cited module failed to parse: {e}\n")
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(_format_human(result), end="")
    return 1 if result.violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
