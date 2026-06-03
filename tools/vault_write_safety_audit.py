"""VWS-1 — Python vault-write-safety audit (slice-094 / [[ADR-086]]).

The AST counterpart of slice-095's SVW-1 (which scans ``skills/*/SKILL.md``
prose). VWS-1 proves that no ``tools/*.py`` module writes a vault file by a
channel OTHER than the sanctioned ``_vault_write`` safe primitives (or an
explicit, COUNT-pinned scoped-out allowlist). The write op IS the ground truth
here — unlike SVW-1's prose-detection surface, this is a structural AST scan, so
the "fail-closed" guarantee is real (a write op the matcher cannot classify as
routed / exempt / scoped-out is a VIOLATION, never a silent pass).

DETECTION MODEL (per-write-target AST — B2/M1 redesign over the v1 import-tripwire):
  For every WRITE-OP node in every ``tools/*.py``:
    - ``X.write_text`` / ``X.write_bytes``            → target = ``X``
    - ``X.open(mode)`` where mode ∈ {w,a,x}           → target = ``X``
    - builtin ``open`` / ``io.open(target, mode)`` w/a/x → target = arg0
    - ``os.open(target, flags)`` flags imply write    → target = arg0
    - ``os.replace`` / ``os.rename(src, dst)``        → target = arg1 (dst)
    - ``shutil.move`` / ``copyfile`` / ``copy`` / ``copy2``(src, dst) → arg1 (dst)
  resolve the TARGET expression and decide:

  1. Is it a VAULT write? — TRUE iff the resolved target path
     (a) carries an ``architecture/`` path segment, OR
     (b) ends with / contains a known vault basename (``_VAULT_BASENAMES`` or an
         ``ADR-NNN-*.md``), OR
     (c) is derived from ``VAULT_ROOT`` / ``resolve_vault_root()`` (the seam —
         the post-flip signal).
     A ``read_text`` / ``git show`` / error-string mentioning a vault literal is
     NOT a write-op node → never matches (the M1 per-write-target fix: this is
     per-WRITE-TARGET, not per-module-mention).

     Target-resolution depth (M2 — bounded + decidable, NOT interprocedural
     dataflow): resolve the target through (i) ≤1 intra-function ``Name``
     assignment (``out_path = repo_root / "architecture" / "x.md";
     out_path.write_text(...)``) AND (ii) module-level ``Path(...)`` / string
     constants (``_AUDIT_LOG_PATH = Path("architecture/...")``). NO
     interprocedural, container-element, or fixpoint resolution. This catches
     the ``var = root/"architecture"/"x.md"; var.write_text()`` shape that all 4
     real writers + 6 of PCR's 7 ops use; PCR's ``:430`` ``pending_writes``
     loop-var (a container element) is the documented accepted RESIDUAL (a 2-hop
     alias is likewise a documented residual, pinned by a test).

  2. CLASSIFY a vault write:
     - module is ``tools/_vault_write.py``        → EXEMPT (the sanctioned
       primitive impl; its raw write_text/os.replace/os.open ARE the safe channel)
     - module is on the scoped-out allowlist (PCR) → CLEAN-SCOPED-OUT (git-coupled;
       concurrent mutation surfaces as a git conflict PCR resolves; routing
       deferred to the flip per slice-093's migration map)
     - otherwise                                   → VIOLATION (exit 1; names
       ``path/to/file.py:line`` + the un-routed channel)

  Routed calls (``safe_write_text`` / ``safe_append_text``) are detected
  separately and counted as ROUTED sites — they are the safe channel by
  construction (a Name-call, not a raw write op).

Honest scope: VWS-1 is a DATA-INTEGRITY control, not a security boundary
([[ADR-067]]). It defends cooperating writers (parallel slices / two Claude
sessions on one machine), not a malicious actor. The bounded resolution depth is
a deliberate decidability tradeoff — its residuals are visible (pinned by tests),
never silently assumed closed.

Usage:
    python -m tools.vault_write_safety_audit
    python -m tools.vault_write_safety_audit --json
    python -m tools.vault_write_safety_audit --repo-root <repo-root>

Exit codes:
    0  clean (every vault write is routed / exempt / scoped-out)
    1  violation (>=1 un-routed vault write)
    2  usage error (tools/ missing/unreadable, or a tools/*.py is unparseable)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

# --- Known vault file basenames (a SECONDARY signal; the PRIMARY signal is an
# "architecture/" path segment, the TERTIARY is VAULT_ROOT-derivation). A vault
# write whose literal target omits the "architecture" segment but names one of
# these basenames is still caught.
_VAULT_BASENAMES: frozenset[str] = frozenset({
    "slice-queue.md",
    "risk-register.md",
    "_index.md",
    "shippability.md",
    "methodology-changelog.md",
    "lessons-learned.md",
    "build-checks.md",
    "parallel-conflict-resolution-log.md",
    "drift-log.md",
})
# An ADR file basename (ADR-NNN-<slug>.md). Matched on the final path segment.
_ADR_BASENAME_RE = re.compile(r"^ADR-\d+.*\.md$")
# The vault directory segment — the strongest in-repo (pre-flip) signal.
_VAULT_SEGMENT = "architecture"
# VAULT_ROOT-derivation: a Name/attribute the writer obtained from the resolver
# seam (tools/_vault_paths). Post-flip the target won't carry a literal
# "architecture" segment, so this is the forward-looking signal.
_VAULT_ROOT_NAMES: frozenset[str] = frozenset({"VAULT_ROOT"})
_VAULT_ROOT_FUNCS: frozenset[str] = frozenset({"resolve_vault_root"})

# Module STEMS (filename without .py) whose raw vault writes are the sanctioned
# safe channel — exempt by construction.
_EXEMPT_MODULES: frozenset[str] = frozenset({"_vault_write"})

# The routed safe-channel functions. A Call to one of these (by bare name) is a
# routed site — the post-routing seam writers + vault_edit use these. slice-109 /
# ADR-098 adds the CAS channel `safe_rewrite_text`; UNLIKE the other two it is
# routed ONLY with a non-constant `expected_base=` (a literal base, e.g. b"", is
# CAS-defeating — Critic m1), enforced in `_is_routed_call`. The set is pinned
# closed by test_routed_funcs_pinned so a 4th channel needs an explicit review.
_ROUTED_FUNCS: frozenset[str] = frozenset(
    {"safe_write_text", "safe_append_text", "safe_rewrite_text"}
)

# Scoped-out allowlist: module STEM -> COUNT of CLEAN-SCOPED-OUT vault write ops.
# parallel_conflict_resolver is git-coupled (its concurrent mutation surfaces as
# a LOUD git conflict it resolves pre-flip); VWS-1 routing is the flip slice's
# work per slice-093's migration map (B3-ratified). The COUNT — not just
# membership — is pinned by test_scoped_out_allowlist_pinned so adding a
# scoped-out op (or a whole new scoped-out module) requires an explicit, reviewed
# change. Fail-closed against silent scope creep (slice-095 _REGISTERED_* shape).
_REGISTERED_SCOPED_OUT: dict[str, int] = {
    "parallel_conflict_resolver": 6,  # 5x log_path.open("a") + :1546 out_path.write_text; :430 loop-var is the residual
}
_SCOPED_OUT_RATIONALE = (
    "git-coupled; concurrent mutation surfaces as a git conflict PCR resolves "
    "pre-flip; VWS-1 routing deferred to the flip per slice-093's migration map"
)

# Write-op method names on a path-like object.
_WRITE_METHODS: frozenset[str] = frozenset({"write_text", "write_bytes"})
# os.open flag names that imply a write. `O_CREAT` ALONE does NOT (it pairs with
# `O_RDONLY`=0 for create-read); a write needs one of these (design.md
# "O_CREAT-with-write" — /code-review m1: dropping bare O_CREAT removes an FP).
_WRITE_OPEN_FLAGS: frozenset[str] = frozenset({"O_WRONLY", "O_RDWR", "O_APPEND"})
# os.<op>(src, dst) write ops whose vault TARGET is the 2nd arg (dst). `os.rename`
# is the direct twin of `os.replace` (/code-review M1 — closing the most likely
# R-32 re-opening channel: a future writer reaching the vault via os.rename).
_OS_DST_ARG2_OPS: frozenset[str] = frozenset({"replace", "rename"})
# shutil.<op>(src, dst) write ops whose vault TARGET is the 2nd arg (dst) (M1).
_SHUTIL_DST_OPS: frozenset[str] = frozenset({"move", "copyfile", "copy", "copy2"})


@dataclass(frozen=True)
class Violation:
    file: str       # repo-relative tools/*.py path
    line: int
    channel: str    # the un-routed write channel, e.g. ".write_text" / "os.replace"
    message: str

    def to_dict(self) -> dict:
        return {"file": self.file, "line": self.line, "channel": self.channel,
                "message": self.message}


@dataclass(frozen=True)
class ClassifiedWrite:
    file: str
    line: int
    channel: str
    verdict: str    # "exempt" | "scoped-out"
    module_stem: str

    def to_dict(self) -> dict:
        return {"file": self.file, "line": self.line, "channel": self.channel,
                "verdict": self.verdict, "module_stem": self.module_stem}


@dataclass
class AuditResult:
    tools_scanned: int = 0
    write_ops_found: int = 0   # raw write ops targeting a vault file (classified)
    sites_routed: int = 0      # safe_write_text/safe_append_text call sites
    exempt: list[ClassifiedWrite] = field(default_factory=list)
    scoped_out: list[ClassifiedWrite] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "clean" if not self.violations else "violation"

    def to_dict(self) -> dict:
        return {
            "tools_scanned": self.tools_scanned,
            "write_ops_found": self.write_ops_found,
            "sites_routed": self.sites_routed,
            "exempt": [c.to_dict() for c in self.exempt],
            "scoped_out": [c.to_dict() for c in self.scoped_out],
            "violations": [v.to_dict() for v in self.violations],
            "status": self.status,
        }


# ── target resolution (bounded: ≤1 intra-function hop + module consts) ──────


def _collect_consts(body: list[ast.stmt]) -> dict[str, ast.expr]:
    """Name -> RHS expr for module-level (or function-level) Assign/AnnAssign."""
    consts: dict[str, ast.expr] = {}
    for node in body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    consts[tgt.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            consts[node.target.id] = node.value
    return consts


def _func_scope(func: ast.AST | None) -> dict[str, ast.expr]:
    """Name -> RHS for every Assign/AnnAssign lexically within ``func`` (its own
    body; nested-function shadowing is not a concern in this corpus)."""
    scope: dict[str, ast.expr] = {}
    if func is None:
        return scope
    for node in ast.walk(func):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    scope[tgt.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            scope[node.target.id] = node.value
    return scope


def _is_path_ctor(func: ast.expr) -> bool:
    """`Path(...)` / `PurePath(...)` / `PurePosixPath(...)` constructor call."""
    if isinstance(func, ast.Name):
        return func.id in {"Path", "PurePath", "PurePosixPath", "PureWindowsPath"}
    if isinstance(func, ast.Attribute):
        return func.attr in {"Path", "PurePath", "PurePosixPath", "PureWindowsPath"}
    return False


def _is_resolve_vault_root(func: ast.expr) -> bool:
    if isinstance(func, ast.Name):
        return func.id in _VAULT_ROOT_FUNCS
    if isinstance(func, ast.Attribute):
        return func.attr in _VAULT_ROOT_FUNCS
    return False


def _resolve_target(
    node: ast.expr,
    func_scope: dict[str, ast.expr],
    module_consts: dict[str, ast.expr],
    hops_left: int,
) -> tuple[list[str], bool]:
    """Flatten a write-target expression to (path-string-parts, vault_root_derived).

    Bounded: ``hops_left`` caps intra-function ``Name`` resolution (≤1); module
    constants are always resolved (a separate mechanism). Anything else
    (parameter, attribute, container element, deeper alias) is left UNRESOLVED →
    contributes no parts (a documented residual, never a silent reclassification)."""
    if isinstance(node, ast.Constant):
        return ([node.value], False) if isinstance(node.value, str) else ([], False)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        lp, lv = _resolve_target(node.left, func_scope, module_consts, hops_left)
        rp, rv = _resolve_target(node.right, func_scope, module_consts, hops_left)
        return (lp + rp, lv or rv)
    if isinstance(node, ast.JoinedStr):  # f-string — pull literal segments
        parts: list[str] = []
        for v in node.values:
            if isinstance(v, ast.Constant) and isinstance(v.value, str):
                parts.append(v.value)
        return (parts, False)
    if isinstance(node, ast.Call):
        if _is_resolve_vault_root(node.func):
            return ([], True)
        if _is_path_ctor(node.func):
            parts, vrd = [], False
            for arg in node.args:
                p, v = _resolve_target(arg, func_scope, module_consts, hops_left)
                parts += p
                vrd = vrd or v
            return (parts, vrd)
        # A method call like `x.with_name(...)` / `x.joinpath(...)`: resolve the
        # receiver + any literal string args (bounded, no deeper Name hops).
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"joinpath", "with_name", "with_suffix", "resolve", "absolute"}:
            parts, vrd = _resolve_target(node.func.value, func_scope, module_consts, hops_left)
            for arg in node.args:
                p, v = _resolve_target(arg, func_scope, module_consts, 0)
                parts += p
                vrd = vrd or v
            return (parts, vrd)
        return ([], False)
    if isinstance(node, ast.Name):
        if node.id in _VAULT_ROOT_NAMES:
            return ([], True)
        if node.id in module_consts:               # module const — always resolved
            return _resolve_target(module_consts[node.id], func_scope, module_consts, 0)
        if hops_left > 0 and node.id in func_scope:  # ≤1 intra-function hop
            return _resolve_target(func_scope[node.id], func_scope, module_consts, hops_left - 1)
        return ([], False)
    if isinstance(node, ast.Attribute):
        if node.attr in _VAULT_ROOT_NAMES:
            return ([], True)
        return ([], False)
    return ([], False)


def _parts_are_vault(parts: list[str]) -> bool:
    """True iff any flattened path part carries the vault segment or basename."""
    for raw in parts:
        # A part may itself be a multi-segment path ("architecture/x.md").
        segs = re.split(r"[\\/]+", raw)
        if _VAULT_SEGMENT in segs:
            return True
        base = segs[-1] if segs else raw
        if base in _VAULT_BASENAMES or _ADR_BASENAME_RE.match(base):
            return True
    return False


# ── write-op extraction ─────────────────────────────────────────────────────


def _mode_has_write(mode: str | None) -> bool:
    return bool(mode) and any(c in mode for c in "wax")


def _str_arg(node: ast.expr | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _flags_imply_write(node: ast.expr) -> bool:
    """Walk an os.open flags expression for any write-implying os.O_* flag."""
    for n in ast.walk(node):
        if isinstance(n, ast.Attribute) and n.attr in _WRITE_OPEN_FLAGS:
            return True
        if isinstance(n, ast.Name) and n.id in _WRITE_OPEN_FLAGS:
            return True
    return False


def _builtin_open_target(call: ast.Call) -> ast.expr | None:
    """`open(target, mode)` / `io.open(target, mode)` shape: returns the target
    iff the mode (2nd positional or `mode=` kw) contains a write char (w/a/x)."""
    mode = None
    if len(call.args) >= 2:
        mode = _str_arg(call.args[1])
    if mode is None:
        for kw in call.keywords:
            if kw.arg == "mode":
                mode = _str_arg(kw.value)
    return call.args[0] if (_mode_has_write(mode) and call.args) else None


def _write_target(call: ast.Call) -> tuple[ast.expr, str] | None:
    """If ``call`` is a raw write op, return (target_expr, channel); else None.

    Covered channels (M1 — the set whose absence is the docstring 'fail-closed'
    guarantee): `.write_text`/`.write_bytes`; builtin `open`/`io.open`(w/a/x);
    `os.open`(write-flags); `Path.open`(w/a/x); `os.replace`/`os.rename`(→dst);
    `shutil.move`/`copyfile`/`copy`/`copy2`(→dst); `safe_rewrite_text`(→arg0,
    slice-109/ADR-098 — detected so a degenerate constant-base CAS call is flagged,
    not silently skipped). A channel outside this set is NOT a silent pass to ignore
    lightly — extend this set + the APED-1 battery before a new write API enters
    `tools/`."""
    func = call.func
    # Bare-name builtin open(target, mode)
    if isinstance(func, ast.Name) and func.id == "open":
        tgt = _builtin_open_target(call)
        return (tgt, "open") if tgt is not None else None
    # slice-109 / ADR-098 (Critic m1): bare-name safe_rewrite_text(target, ...).
    # Reached only when _is_routed_call rejected it (constant/absent expected_base)
    # → surface the degenerate CAS-defeat as an un-routed vault write.
    if isinstance(func, ast.Name) and func.id == "safe_rewrite_text":
        return (call.args[0], "safe_rewrite_text") if call.args else None
    if isinstance(func, ast.Attribute):
        attr = func.attr
        recv = func.value
        recv_is_os = isinstance(recv, ast.Name) and recv.id == "os"
        recv_is_io = isinstance(recv, ast.Name) and recv.id == "io"
        recv_is_shutil = isinstance(recv, ast.Name) and recv.id == "shutil"
        if attr in _WRITE_METHODS:                         # X.write_text / X.write_bytes
            return (recv, f".{attr}")
        if attr == "open" and recv_is_os:                  # os.open(target, flags)
            if len(call.args) >= 2 and _flags_imply_write(call.args[1]):
                return (call.args[0], "os.open")
            return None
        if attr == "open" and recv_is_io:                  # io.open(target, mode) — builtin-open shape
            tgt = _builtin_open_target(call)
            return (tgt, "io.open") if tgt is not None else None
        if attr == "open":                                 # X.open(mode) (Path.open)
            mode = _str_arg(call.args[0]) if call.args else None
            if mode is None:
                for kw in call.keywords:
                    if kw.arg == "mode":
                        mode = _str_arg(kw.value)
            if _mode_has_write(mode):
                return (recv, ".open")
            return None
        if attr in _OS_DST_ARG2_OPS and recv_is_os:        # os.replace / os.rename (src, dst) → dst
            if len(call.args) >= 2:
                return (call.args[1], f"os.{attr}")
            return None
        if attr in _SHUTIL_DST_OPS and recv_is_shutil:     # shutil.move/copyfile/copy/copy2 (src, dst) → dst
            if len(call.args) >= 2:
                return (call.args[1], f"shutil.{attr}")
            return None
        if attr == "safe_rewrite_text":                    # m.safe_rewrite_text(target, ...) — slice-109/ADR-098
            return (call.args[0], "safe_rewrite_text") if call.args else None
    return None


def _is_routed_call(
    call: ast.Call, module_consts: dict[str, ast.expr] | None = None
) -> bool:
    """A Call to a routed safe channel (safe_write_text / safe_append_text /
    safe_rewrite_text). slice-109 / ADR-098 (Critic m1 + code-review M1):
    `safe_rewrite_text` is routed ONLY when an `expected_base=` keyword is present
    AND its value does not RESOLVE to a constant — a literal base (`b""`) **OR a
    module-level name bound to a constant** (`expected_base=_EMPTY` where
    `_EMPTY = b""`) is a CAS-defeat, so it is NOT auto-cleaned here; `_write_target`
    then flags it as an un-routed vault write. A genuinely dynamic/local base (the
    real writers' `expected_base=base` read-bytes result — not a module constant)
    stays routed. The literal AND the name-indirection variants are both EXECUTED
    by the APED-1 battery (code-review M1 closed the name-indirection gap)."""
    func = call.func
    if isinstance(func, ast.Name):
        name: str | None = func.id
    elif isinstance(func, ast.Attribute):
        name = func.attr
    else:
        return False
    if name not in _ROUTED_FUNCS:
        return False
    if name == "safe_rewrite_text":
        kw = next((k for k in call.keywords if k.arg == "expected_base"), None)
        if kw is None:
            return False
        val = kw.value
        # Resolve a module-level name to its bound value (the name-indirection
        # CAS-defeat, code-review M1); a local/unresolvable name is dynamic → routed.
        if isinstance(val, ast.Name) and module_consts is not None:
            resolved = module_consts.get(val.id)
            if resolved is not None:
                val = resolved
        if isinstance(val, ast.Constant):
            return False
    return True


def _enclosing_func(node: ast.AST) -> ast.AST | None:
    p = getattr(node, "_vws_parent", None)
    while p is not None and not isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
        p = getattr(p, "_vws_parent", None)
    return p


# ── module + repo scan ──────────────────────────────────────────────────────


def audit_module(path: Path, rel: str, result: AuditResult) -> None:
    """Classify every write op in one tools/*.py; mutate ``result`` in place.

    Raises SyntaxError to the caller (a usage-error / fail-VISIBLE — an
    unparseable tool is never a silent skip)."""
    module_stem = path.stem
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._vws_parent = parent  # type: ignore[attr-defined]
    module_consts = _collect_consts(tree.body)
    scope_cache: dict[int, dict[str, ast.expr]] = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_routed_call(node, module_consts):
            result.sites_routed += 1
            continue
        wt = _write_target(node)
        if wt is None:
            continue
        target, channel = wt
        func = _enclosing_func(node)
        key = id(func)
        if key not in scope_cache:
            scope_cache[key] = _func_scope(func)
        parts, vault_root_derived = _resolve_target(target, scope_cache[key], module_consts, hops_left=1)
        is_vault = vault_root_derived or _parts_are_vault(parts)
        if not is_vault:
            continue  # non-vault write (tmp / graphify-out / a parameter) — out of scope by construction
        result.write_ops_found += 1
        line = node.lineno
        if module_stem in _EXEMPT_MODULES:
            result.exempt.append(ClassifiedWrite(rel, line, channel, "exempt", module_stem))
        elif module_stem in _REGISTERED_SCOPED_OUT:
            result.scoped_out.append(ClassifiedWrite(rel, line, channel, "scoped-out", module_stem))
        else:
            result.violations.append(Violation(
                file=rel, line=line, channel=channel,
                message=(
                    f"un-routed vault write via `{channel}` — route through "
                    f"`_vault_write.safe_write_text`/`safe_append_text`, or (if "
                    f"git-coupled) add the module to the COUNT-pinned scoped-out "
                    f"allowlist with rationale"
                ),
            ))


def _iter_tool_files(root: Path) -> list[Path]:
    tools_dir = root / "tools"
    if not tools_dir.exists():
        return []
    return sorted(tools_dir.glob("*.py"))


def audit_root(root: Path) -> AuditResult:
    """Scan every tools/*.py; classify each vault write op. Raises SyntaxError
    (caller maps to exit 2) on an unparseable module — fail-VISIBLE."""
    result = AuditResult()
    for path in _iter_tool_files(root):
        if path.name == "__init__.py":
            continue
        result.tools_scanned += 1
        rel = str(path.relative_to(root)).replace("\\", "/")
        audit_module(path, rel, result)
    return result


def registered_scoped_out_counts(root: Path) -> dict[str, int]:
    """The per-module COUNT of CLEAN-SCOPED-OUT vault write ops actually present —
    consumed by test_scoped_out_allowlist_pinned to pin against
    _REGISTERED_SCOPED_OUT. Adding a scoped-out op changes this count and trips
    the pin (fail-closed against silent scope creep)."""
    counts: dict[str, int] = {}
    for c in audit_root(root).scoped_out:
        counts[c.module_stem] = counts.get(c.module_stem, 0) + 1
    return counts


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"VWS-1 vault-write-safety audit: clean. "
            f"{result.tools_scanned} tool(s) scanned; "
            f"{result.write_ops_found} vault write op(s) "
            f"({result.sites_routed} routed call(s), {len(result.exempt)} exempt, "
            f"{len(result.scoped_out)} scoped-out).\n"
        )
    out = [f"VWS-1 vault-write-safety audit: {len(result.violations)} violation(s):\n\n"]
    for v in result.violations:
        out.append(f"  {v.file}:{v.line} [{v.channel}] {v.message}\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="vault_write_safety_audit",
        description=(
            "VWS-1 audit: every tools/*.py vault write must route through the "
            "_vault_write safe primitives, be the exempt primitive impl, or be on "
            "the COUNT-pinned scoped-out allowlist."
        ),
    )
    parser.add_argument(
        "--repo-root", type=Path, default=None,
        help="Repo root (defaults to the parent of the tools/ dir containing this script)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args(argv)

    root = args.repo_root.resolve() if args.repo_root is not None else Path(__file__).resolve().parent.parent
    if not (root / "tools").exists():
        sys.stderr.write(f"tools/ directory not found at {root}\n")
        return 2

    try:
        result = audit_root(root)
    except SyntaxError as exc:
        sys.stderr.write(f"VWS-1: unparseable tools/*.py — {exc}\n")
        return 2
    except OSError as exc:
        sys.stderr.write(f"VWS-1: tools/ unreadable — {exc}\n")
        return 2

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))
    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
