"""UTF8-STDOUT-1 structural audit.

Validates every `tools/*.py` module exposing a `main()` function calls
`_stdout.reconfigure_stdout_utf8()` as the first executable statement.
Closes the recurring Windows cp1252 console encoding class (N=6 across
slices 007 / 016 / 018 / 020 / 021 / 022 → retired at slice-023).

Per UTF8-STDOUT-1 (methodology-changelog.md v0.37.0). The canonical
invocation pattern is:

    from tools import _stdout

    def main(argv: list[str] | None = None) -> int:
        _stdout.reconfigure_stdout_utf8()
        # ... rest of main() body ...

Exclusion list: `__init__.py` (no main), `_stdout.py` (helper, no main).

Detection mechanism: AST-based. Parse each candidate file; find
top-level FunctionDef named `main`; identify the first executable
statement after the docstring; verify it's a Call to the canonical
reconfigure helper.

Usage:
    python -m tools.utf8_stdout_audit
    python -m tools.utf8_stdout_audit --json
    python -m tools.utf8_stdout_audit --root <repo-root>

Exit codes:
    0 = clean (every audit tool conforms)
    1 = violation (>=1 tool non-conforming)
    2 = usage error (root missing, parse failure, etc.)
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from tools import _stdout

_EXCLUDED_FILENAMES: frozenset[str] = frozenset({"__init__.py"})
_CANONICAL_FUNCTION_NAME: str = "reconfigure_stdout_utf8"
_CANONICAL_HELPER_NAME: str = "_stdout"


@dataclass(frozen=True)
class Violation:
    file: str  # repo-relative path
    function: str
    line: int
    message: str

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "function": self.function,
            "line": self.line,
            "message": self.message,
        }


@dataclass
class AuditResult:
    tools_scanned: int = 0
    tools_with_main: int = 0
    tools_clean: int = 0
    violations: list[Violation] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "clean" if not self.violations else "violation"

    def to_dict(self) -> dict:
        return {
            "tools_scanned": self.tools_scanned,
            "tools_with_main": self.tools_with_main,
            "tools_clean": self.tools_clean,
            "violations": [v.to_dict() for v in self.violations],
            "status": self.status,
        }


def _is_helper_module(name: str) -> bool:
    """Helper modules (leading underscore, no main()) are excluded from scan."""
    return name.startswith("_")


def _candidate_tools(root: Path) -> list[Path]:
    """Return tools/*.py files eligible for audit (excludes __init__.py + _*.py)."""
    tools_dir = root / "tools"
    if not tools_dir.exists():
        return []
    return sorted(
        p for p in tools_dir.glob("*.py")
        if p.name not in _EXCLUDED_FILENAMES and not _is_helper_module(p.name)
    )


def _find_main_function(tree: ast.Module) -> ast.FunctionDef | None:
    """Find top-level `def main(...)` in the module's AST."""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == "main":
                return node  # type: ignore[return-value]
    return None


def _first_executable_statement(func: ast.FunctionDef) -> ast.stmt | None:
    """Return the first executable statement in func.body, skipping docstring."""
    body = func.body
    if not body:
        return None
    first = body[0]
    # Skip docstring: a bare Expr whose value is a Constant string.
    if (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        return body[1] if len(body) > 1 else None
    return first


def _is_canonical_reconfigure_call(stmt: ast.stmt) -> bool:
    """Check if stmt is `_stdout.reconfigure_stdout_utf8()` or equivalent.

    Accepts:
      - _stdout.reconfigure_stdout_utf8()        (canonical pinned form)
      - reconfigure_stdout_utf8()                (from-import form)
    """
    if not isinstance(stmt, ast.Expr):
        return False
    call = stmt.value
    if not isinstance(call, ast.Call):
        return False
    func = call.func
    if isinstance(func, ast.Attribute):
        if (
            isinstance(func.value, ast.Name)
            and func.value.id == _CANONICAL_HELPER_NAME
            and func.attr == _CANONICAL_FUNCTION_NAME
        ):
            return True
    if isinstance(func, ast.Name):
        if func.id == _CANONICAL_FUNCTION_NAME:
            return True
    return False


def _has_canonical_import(tree: ast.Module) -> bool:
    """Check the module imports `from tools import _stdout` (canonical M4 form)."""
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == "tools":
                for alias in node.names:
                    if alias.name == _CANONICAL_HELPER_NAME:
                        return True
    return False


def audit_root(root: Path) -> AuditResult:
    """Audit every tools/*.py under root; return AuditResult."""
    result = AuditResult()
    for path in _candidate_tools(root):
        result.tools_scanned += 1
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            result.violations.append(
                Violation(
                    file=str(path.relative_to(root)).replace("\\", "/"),
                    function="<module>",
                    line=e.lineno or 0,
                    message=f"SyntaxError parsing module: {e.msg}",
                )
            )
            continue

        main_func = _find_main_function(tree)
        if main_func is None:
            # Tool has no main() — not subject to UTF8-STDOUT-1
            continue

        result.tools_with_main += 1
        rel_path = str(path.relative_to(root)).replace("\\", "/")
        first_stmt = _first_executable_statement(main_func)

        if first_stmt is None:
            result.violations.append(
                Violation(
                    file=rel_path,
                    function="main",
                    line=main_func.lineno,
                    message="main() body is empty or docstring-only",
                )
            )
            continue

        if not _is_canonical_reconfigure_call(first_stmt):
            try:
                got = ast.unparse(first_stmt)
            except Exception:
                got = f"<line {first_stmt.lineno}>"
            result.violations.append(
                Violation(
                    file=rel_path,
                    function="main",
                    line=first_stmt.lineno,
                    message=(
                        f"first executable statement is not "
                        f"_stdout.reconfigure_stdout_utf8() "
                        f"(got: {got})"
                    ),
                )
            )
            continue

        if not _has_canonical_import(tree):
            result.violations.append(
                Violation(
                    file=rel_path,
                    function="<module>",
                    line=1,
                    message=(
                        "missing canonical import 'from tools import _stdout' "
                        "(per UTF8-STDOUT-1 + M4 ACCEPTED-FIXED at slice-023)"
                    ),
                )
            )
            continue

        result.tools_clean += 1

    return result


def _format_human(result: AuditResult) -> str:
    if not result.violations:
        return (
            f"UTF8-STDOUT-1 audit: clean. "
            f"{result.tools_scanned} tool(s) scanned; "
            f"{result.tools_with_main} with main(); "
            f"{result.tools_clean} clean.\n"
        )

    out: list[str] = [
        f"UTF8-STDOUT-1 audit: {len(result.violations)} violation(s) "
        f"({result.tools_with_main - result.tools_clean} of "
        f"{result.tools_with_main} tool(s) with main() non-conforming):\n\n"
    ]
    for v in result.violations:
        out.append(f"  {v.file}:{v.line} {v.function}: {v.message}\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(
        prog="utf8_stdout_audit",
        description=(
            "UTF8-STDOUT-1 structural audit: every tools/*.py with main() "
            "must call _stdout.reconfigure_stdout_utf8() as first executable "
            "statement."
        ),
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="Repo root (defaults to parent of tools/ directory containing this script)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON",
    )
    args = parser.parse_args(argv)

    if args.root is None:
        # Default: parent of tools/ where this script lives
        root = Path(__file__).resolve().parent.parent
    else:
        root = args.root.resolve()

    if not (root / "tools").exists():
        sys.stderr.write(f"tools/ directory not found at {root}\n")
        return 2

    result = audit_root(root)

    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2) + "\n")
    else:
        sys.stdout.write(_format_human(result))

    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
