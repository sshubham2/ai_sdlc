"""State-transition stale-pin audit (STP-1).

Per **STP-1** (`methodology-changelog.md` v0.54.0; slice-044; [[ADR-047]]).
Audit-enforced pre-finish gate (NON-`-D` `vN.N`; naming-class peer of
BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1).

Detects the recurring N>=3 methodology-discipline class: a slice performs a
*state transition* but a pre-existing test still pins the OLD value and was
not realigned in the same fix block — caught historically only at the
pre-finish full-suite (BC-PROJ-4) run, sometimes latent for several slices
(R-10 slice-038->040 ~5-slice latency; slice-041 R-4 stale
`test_r_4_..._stays_mitigating`; slice-042 ADR-prose recurrence).

Two mechanically-detectable sub-forms (the fuzzy ADR accepted->superseded
sub-form is explicitly out of scope per ADR-047):

- **Sub-form A — SKILL.md-prose-repoint stale pin** (git-diff-independent
  standing invariant). For every ``tests/**/test_*skill*.py`` prose-pin
  asserting a constant string literal via positive ``in`` membership against
  a name traced (directly or through ``str.split(...)[i]`` / subscript /
  slice chains) from a ``read_file("skills/<x>/SKILL.md")`` call, the folded
  literal MUST be present in the *full* target ``SKILL.md``. A ``not in``
  pin, or any membership whose enclosing ``BoolOp`` has a ``NotIn`` /
  non-constant sibling, is excluded (it asserts a deliberately-absent
  literal). Presence is checked against the full SKILL.md text, never a
  sliced sub-segment (slicing narrows location, not presence).

- **Sub-form B — risk-status-stale pin** (git-diff-independent standing
  invariant; revised from a git-merge-base mechanism by the slice-044
  /build-slice plan-mode deviation — ``architecture/`` is gitignored so the
  merge-base form was inapplicable). A test ``FunctionDef`` name matching
  ``(?:^|_)r[_-]?(\\d+).*?_(stays|remains|is)_(open|mitigating|retired|accepted)(?:_|$)``
  claims ``R-<num>`` is at the named status; if the *live*
  ``architecture/risk-register.md`` ``**Status**:`` for that risk differs
  from the claimed status it is a stale pin. The live register is parsed via
  the object-identity-reused ``risk_register_audit._parse_risks`` (CSP-1).

Parse-failure discipline (ADR-037 / PTFFD-1, inherited verbatim from the
cited ``shippability_path_audit.py`` / ``_pyfn`` precedent): a per-scanned
file that does not parse is **skip-with-visible-note, NO violation, NOT
exit 2** — a false-FAIL on a parse failure would halt the pipeline gate, the
strictly-worse audit failure mode. Exit-2 fail-closed is reserved for
hard-input failure only: ``architecture/risk-register.md`` missing/unreadable,
the ``tests/`` or ``skills/`` directory missing, or repo-root unresolvable.

Usage:
    python -m tools.state_transition_pin_audit
    python -m tools.state_transition_pin_audit --root <repo-root>
    python -m tools.state_transition_pin_audit --json

Exit codes:
    0  clean (incl. when scanned files were skipped-with-note for parse failure)
    1  Important violation (`stale-skill-prose-pin` / `stale-risk-status-pin`)
    2  usage-error (hard-input failure only — see above)
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools import _stdout
# Object-identity reuse (CSP-1; slice-038 `consumer._fn is source._fn`
# lesson) — Sub-form B parses the live register via the SAME parser RR-1
# uses; NOT re-derived.
from tools.risk_register_audit import _parse_risks

# Sub-form A: recognise a `read_file("skills/<x>/SKILL.md")` call. Only the
# bare imported `read_file` shape occurs in the corpus (every file does
# `from tests.methodology.conftest import read_file`); the qualified
# `conftest.read_file(...)` shape has zero corpus instances (YAGNI per
# critique M3) and is intentionally unsupported.
_SKILL_MD_ARG_RE = re.compile(r"^skills/[^\"']+/SKILL\.md$")

# Sub-form B detector. `(?:^|_)`-anchored (NOT `\b` — `\b` is never a
# boundary adjacent to `_`, dead against snake_case; targeted-critique M1);
# explicit status alternation terminated by `(?:_|$)` (NOT a greedy `\w+` +
# validity-guard; targeted-critique M2 — a descriptive suffix after the
# status word is still caught). Non-greedy `.*?` binds the nearest status.
_RISK_STATUS_FN_RE = re.compile(
    r"(?:^|_)r[_-]?(\d+).*?_(stays|remains|is)_(open|mitigating|retired|accepted)(?:_|$)"
)

_LITERAL_TRUNC = 80


@dataclass(frozen=True)
class StateTransitionViolation:
    kind: str       # "stale-skill-prose-pin" | "stale-risk-status-pin" |
                    # "usage-error"
    severity: str   # "Important"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AuditResult:
    repo_root: str = ""
    violations: list[StateTransitionViolation] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    # B-add-1 / meta-Critic reservation: machine-classify the full BoolOp-pin
    # set rather than assume — recorded for the build-log.
    boolop_pin_stats: dict = field(
        default_factory=lambda: {"positive_only": 0, "mixed_excluded": 0}
    )

    def to_dict(self) -> dict:
        important = [v for v in self.violations if v.severity == "Important"]
        return {
            "rule": "STP-1",
            "repo_root": self.repo_root,
            "violations": [v.to_dict() for v in self.violations],
            "skipped": list(self.skipped),
            "boolop_pin_stats": dict(self.boolop_pin_stats),
            "summary": {
                "violation_count": len(important),
                "skipped_count": len(self.skipped),
                "clean": not important,
            },
        }


def _const_str(node: ast.AST) -> str | None:
    """Return the folded constant str value of `node`, else None.

    CPython folds implicit adjacent-string concatenation at parse time into a
    single `ast.Constant`, so a 3-line implicitly-concatenated pin literal is
    recovered as its true single value here — never source-text / first-token
    scraping (critique B3). f-strings (`ast.JoinedStr`), `%`/`+`/`.format()`-
    built, and name-only operands are NOT constants and return None (the
    caller skips them — cannot statically prove absence).
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _root_name(node: ast.AST) -> str | None:
    """Resolve the root identifier of a (possibly sliced/subscripted) expr.

    `content` -> "content"; `content.split("##")[1]` -> "content";
    `prereq_block[0:50]` -> "prereq_block". Returns None if the expression
    does not bottom out in a bare Name.
    """
    cur = node
    while True:
        if isinstance(cur, ast.Name):
            return cur.id
        if isinstance(cur, ast.Subscript):
            cur = cur.value
        elif isinstance(cur, ast.Call):
            # e.g. <expr>.split(...) — descend through the bound method.
            if isinstance(cur.func, ast.Attribute):
                cur = cur.func.value
            else:
                return None
        elif isinstance(cur, ast.Attribute):
            cur = cur.value
        else:
            return None


def _skill_md_from_call(node: ast.AST) -> str | None:
    """If `node` is `read_file("skills/<x>/SKILL.md")`, return that rel-path."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (isinstance(func, ast.Name) and func.id == "read_file"):
        return None
    if not node.args:
        return None
    arg0 = _const_str(node.args[0])
    if arg0 and _SKILL_MD_ARG_RE.match(arg0):
        return arg0
    return None


def _trace_bindings(scope_body: list[ast.stmt], inherited: dict[str, str]) -> dict[str, str]:
    """Map every name bound (transitively) from a SKILL.md `read_file(...)`
    call within this scope to its SKILL.md rel-path.

    `inherited` carries module-level (or enclosing) traced names; local
    assignments override. Handles `NAME = read_file(...)` and the dominant
    `prereq_block = content.split("## ...", 1)[1]...` slice/subscript chains.
    """
    traced = dict(inherited)
    for stmt in scope_body:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            continue
        target = stmt.targets[0]
        if not isinstance(target, ast.Name):
            continue
        rhs = stmt.value
        direct = _skill_md_from_call(rhs)
        if direct is not None:
            traced[target.id] = direct
            continue
        # Transitive: rhs rooted at an already-traced name (slice/subscript/
        # .split chain) — slicing narrows location, not presence, so the
        # traced SKILL.md path is preserved.
        root = _root_name(rhs)
        if root is not None and root in traced:
            traced[target.id] = traced[root]
    return traced


def _excluded_compare_ids(tree: ast.AST) -> set[int]:
    """ids() of Compare nodes that must NOT be treated as positive pins.

    A node is excluded iff (i) its own single op is `ast.NotIn`, OR (ii) it
    is an operand of an `ast.Or` BoolOp (a *disjunction* pins NO single
    operand individually-present — `assert "solo-dev" in c or "solo dev" in
    c` legitimately has one absent alternative; flagging it is a false
    positive — Task-1 self-verify finding), OR (iii) it is an operand of an
    `ast.And` BoolOp whose other operands include a `NotIn` or a
    non-constant-left comparison (the mixed `"x" not in c or "NEVER" in c`
    idiom). A positive-only `ast.And` chain IS evaluated per-operand (each
    conjunct is independently pinned-present — critique B1 + B-add-1).
    """
    excluded: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            if len(node.ops) == 1 and isinstance(node.ops[0], ast.NotIn):
                excluded.add(id(node))
        elif isinstance(node, ast.BoolOp):
            cmps = [v for v in node.values if isinstance(v, ast.Compare)]
            if isinstance(node.op, ast.Or):
                # Disjunction: no operand is individually asserted-present.
                for c in cmps:
                    excluded.add(id(c))
                continue
            # ast.And — conjunction. Each operand IS individually pinned,
            # UNLESS a sibling is NotIn / non-constant (mixed idiom).
            has_bad_sibling = False
            for c in node.values:
                if isinstance(c, ast.Compare) and len(c.ops) == 1:
                    if isinstance(c.ops[0], ast.NotIn):
                        has_bad_sibling = True
                        break
                    if isinstance(c.ops[0], ast.In) and _const_str(c.left) is None:
                        has_bad_sibling = True
                        break
                else:
                    # A BoolOp value that is not a single-op Compare
                    # (a call, a name, a nested bool, ...) — non-constant.
                    has_bad_sibling = True
                    break
            if has_bad_sibling:
                for c in cmps:
                    excluded.add(id(c))
    return excluded


def _scan_skill_prose_pins(root: Path, result: AuditResult) -> None:
    """Sub-form A."""
    tests_dir = root / "tests"
    for py in sorted(tests_dir.rglob("test_*skill*.py")):
        try:
            src = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError):
            result.skipped.append(f"{py} (unreadable; ADR-037 skip-with-note)")
            continue
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError):
            result.skipped.append(f"{py} (unparseable; ADR-037 skip-with-note)")
            continue

        module_traced = _trace_bindings(tree.body, {})
        excluded = _excluded_compare_ids(tree)
        rel = py.relative_to(root).as_posix()
        skill_cache: dict[str, str | None] = {}

        def _emit(cmp_node: ast.Compare, fn_name: str, traced: dict[str, str]) -> None:
            if id(cmp_node) in excluded:
                return
            if not (len(cmp_node.ops) == 1 and isinstance(cmp_node.ops[0], ast.In)):
                return
            literal = _const_str(cmp_node.left)
            if literal is None:
                return  # non-constant operand — cannot prove absence
            if not cmp_node.comparators:
                return
            rhs_root = _root_name(cmp_node.comparators[0])
            if rhs_root is None or rhs_root not in traced:
                return
            skill_rel = traced[rhs_root]
            if skill_rel not in skill_cache:
                try:
                    skill_cache[skill_rel] = (root / skill_rel).read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError, ValueError):
                    skill_cache[skill_rel] = None
                    result.skipped.append(
                        f"{skill_rel} (target unreadable; ADR-037 skip-with-note)"
                    )
            skill_text = skill_cache[skill_rel]
            if skill_text is None:
                return
            if literal not in skill_text:
                shown = literal if len(literal) <= _LITERAL_TRUNC else literal[:_LITERAL_TRUNC] + "..."
                result.violations.append(
                    StateTransitionViolation(
                        kind="stale-skill-prose-pin",
                        severity="Important",
                        message=(
                            f"{rel}::{fn_name} asserts a prose-pin literal "
                            f"absent from {skill_rel}: {shown!r}. The SKILL.md "
                            f"anchor was repointed but this pin was not "
                            f"realigned/superseded in the same fix block — "
                            f"realign or supersede this prose-pin (the R-10 "
                            f"class; STP-1 / ADR-047)."
                        ),
                    )
                )

        # Single recursive walk with scope-tracked traced-bindings; each
        # Compare attributed to its nearest enclosing function (no
        # double-count, correct nested-scope attribution).
        def _visit(node: ast.AST, traced: dict[str, str], fn_name: str) -> None:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                local = _trace_bindings(node.body, traced)
                for child in node.body:
                    _visit(child, local, node.name)
                return
            if isinstance(node, ast.Compare):
                _emit(node, fn_name, traced)
                # still descend (a Compare can contain nested Compares)
            for child in ast.iter_child_nodes(node):
                _visit(child, traced, fn_name)

        for stmt in tree.body:
            _visit(stmt, module_traced, "<module>")


def _count_boolop_stats(root: Path, result: AuditResult) -> None:
    """Machine-classify the full BoolOp-pin set (B-add-1 reservation)."""
    for py in sorted((root / "tests").rglob("test_*skill*.py")):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
            continue
        excluded = _excluded_compare_ids(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.BoolOp):
                continue
            cmps = [
                v for v in node.values
                if isinstance(v, ast.Compare) and len(v.ops) == 1
                and isinstance(v.ops[0], ast.In) and _const_str(v.left) is not None
            ]
            if not cmps:
                continue
            if any(id(c) in excluded for c in cmps):
                result.boolop_pin_stats["mixed_excluded"] += 1
            else:
                result.boolop_pin_stats["positive_only"] += 1


def _scan_risk_status_pins(root: Path, result: AuditResult) -> None:
    """Sub-form B — git-diff-independent standing invariant."""
    register = root / "architecture" / "risk-register.md"
    if not register.exists():
        result.violations.append(
            StateTransitionViolation(
                kind="usage-error",
                severity="Important",
                message=(
                    f"architecture/risk-register.md not found at {register} — "
                    f"Sub-form B cannot resolve live risk statuses (fail-closed; "
                    f"hard-input failure)."
                ),
            )
        )
        return
    try:
        reg_text = register.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError) as e:
        result.violations.append(
            StateTransitionViolation(
                kind="usage-error",
                severity="Important",
                message=f"architecture/risk-register.md unreadable: {e} (fail-closed).",
            )
        )
        return
    try:
        risks, _violations = _parse_risks(reg_text, str(register))
    except Exception as e:  # noqa: BLE001 — any parser failure is fail-closed
        result.violations.append(
            StateTransitionViolation(
                kind="usage-error",
                severity="Important",
                message=(
                    f"architecture/risk-register.md unparseable via "
                    f"risk_register_audit._parse_risks: {e} (fail-closed)."
                ),
            )
        )
        return
    # RR-1 *content* violations (missing field, etc.) do NOT make the file
    # unparseable — the parsed risks still carry authoritative .status; per
    # ADR-047 exit-2 is reserved for unparseable/missing only.
    status_by_id = {r.risk_id: r.status for r in risks}

    for py in sorted((root / "tests").rglob("*.py")):
        try:
            src = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError):
            result.skipped.append(f"{py} (unreadable; ADR-037 skip-with-note)")
            continue
        try:
            tree = ast.parse(src)
        except (SyntaxError, ValueError):
            result.skipped.append(f"{py} (unparseable; ADR-037 skip-with-note)")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            m = _RISK_STATUS_FN_RE.search(node.name)
            if not m:
                continue
            risk_id = f"R-{int(m.group(1))}"
            claimed = m.group(3)
            live = status_by_id.get(risk_id)
            if live is None:
                continue  # risk not in register — not a contradiction
            if live != claimed:
                rel = py.relative_to(root).as_posix()
                result.violations.append(
                    StateTransitionViolation(
                        kind="stale-risk-status-pin",
                        severity="Important",
                        message=(
                            f"{rel}::{node.name} pins {risk_id} = {claimed!r} but "
                            f"the live architecture/risk-register.md has {risk_id} "
                            f"**Status**: {live!r} ({claimed} -> {live}). The risk "
                            f"status transitioned but this test was not realigned in "
                            f"the same fix block — realign the test to the live "
                            f"status or rename off the `_<verb>_<status>` token "
                            f"(slice-041 class; STP-1 / ADR-047)."
                        ),
                    )
                )


def audit(root: Path | None = None) -> AuditResult:
    """Run the STP-1 audit. `root` defaults to the nearest ancestor with .git."""
    if root is None:
        here = Path(__file__).resolve()
        for parent in [here] + list(here.parents):
            if (parent / ".git").exists():
                root = parent
                break
        else:
            r = AuditResult()
            r.violations.append(
                StateTransitionViolation(
                    kind="usage-error",
                    severity="Important",
                    message="repo root unresolvable (no .git ancestor); fail-closed.",
                )
            )
            return r
    root = Path(root).resolve()
    result = AuditResult(repo_root=str(root))

    if not (root / "tests").is_dir():
        result.violations.append(
            StateTransitionViolation(
                kind="usage-error",
                severity="Important",
                message=f"tests/ directory missing at {root} (fail-closed).",
            )
        )
        return result
    if not (root / "skills").is_dir():
        result.violations.append(
            StateTransitionViolation(
                kind="usage-error",
                severity="Important",
                message=f"skills/ directory missing at {root} (fail-closed).",
            )
        )
        return result

    _scan_skill_prose_pins(root, result)
    _count_boolop_stats(root, result)
    _scan_risk_status_pins(root, result)
    return result


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="state_transition_pin_audit",
        description="STP-1: state-transition stale-pin audit (Sub-form A + B).",
    )
    parser.add_argument("--root", type=Path, default=None,
                        help="Repo root (default: nearest .git ancestor).")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    args = parser.parse_args(argv)

    try:
        result = audit(root=args.root)
    except Exception as e:  # noqa: BLE001 — never raise into the gate
        print(f"state_transition_pin_audit: error: {e}", file=sys.stderr)
        return 2

    important = [v for v in result.violations if v.severity == "Important"]
    usage = [v for v in important if v.kind == "usage-error"]

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        for v in important:
            print(f"[{v.severity}] {v.kind}: {v.message}")
        for note in result.skipped:
            print(f"[skip] {note}")
        if not important:
            print(
                f"State-transition stale-pin audit (STP-1): clean. "
                f"{len(result.skipped)} file(s) skipped-with-note; "
                f"BoolOp pins positive-only={result.boolop_pin_stats['positive_only']} "
                f"mixed-excluded={result.boolop_pin_stats['mixed_excluded']}."
            )

    if usage:
        return 2
    if important:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
