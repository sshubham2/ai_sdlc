"""Mock-budget linter for Python test files (LINT-MOCK-1).

Implements TDD-2: each test mocks at most one collaborator, only at network
or process boundaries. Internal-class mocking is flagged. Targets in the
project's .cross-chunk-seams allowlist escalate Important -> Critical.

Usage:
    python -m tools.mock_budget_lint <test-file>...
    python -m tools.mock_budget_lint --json <test-file>...
    python -m tools.mock_budget_lint --seam-allowlist <path> <test-file>...
    python -m tools.mock_budget_lint --strict <test-file>...

Exit codes:
    0  no Critical findings (or no findings at all)
    1  Critical findings present (or any findings if --strict)
    2  usage error / unrecoverable failure

Detection:
    - @patch / @mock.patch / @patch.object decorators on test functions
    - patch(...) / mocker.patch(...) / mocker.spy(...) calls inside test bodies
    - Counts mocks per test function (def test_*)
    - Boundary check: target's root module must be in _BOUNDARY_DEFAULTS

Limitations (v1):
    - Mocks inside pytest fixtures (used by tests via injection) are not
      attributed to the consuming test function. Whole-file mock budgets
      are out of scope; the linter is per-test-function.
    - Wrapper-as-SUT exemption (test file's name matching the target's
      basename) is not implemented; all internal mocks are flagged. Use the
      seam-allowlist to handle project-specific exceptions.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


# External boundary module stems where mocking is allowed per TDD-2.
# These are roots of dotted paths; e.g., "requests.get" matches "requests".
_BOUNDARY_DEFAULTS: frozenset[str] = frozenset({
    # HTTP / networking
    "requests", "httpx", "urllib", "urllib2", "urllib3", "aiohttp", "http",
    "socket", "asyncio",
    # Process / OS
    "subprocess", "shutil", "os", "sys", "signal",
    # Filesystem
    "pathlib", "tempfile", "io",
    # Databases
    "psycopg2", "sqlalchemy", "pymongo", "redis", "mysql", "sqlite3",
    "asyncpg", "aiosqlite",
    # Cloud / vendor SDKs
    "boto3", "botocore", "google", "googleapiclient", "stripe",
    "anthropic", "openai", "azure", "kubernetes",
    # Email / messaging
    "smtplib", "imaplib", "kafka", "pika", "amqp",
    # SSH / secrets
    "paramiko", "ssh", "fabric",
    # Time / clock (often mocked at boundary)
    "time", "datetime",
})


@dataclass(frozen=True)
class MockCall:
    """A single mock invocation found in a test function."""
    target: str  # e.g., "requests.get"
    line: int
    kind: str    # "decorator" | "call"


@dataclass(frozen=True)
class LintViolation:
    """A finding emitted by the linter."""
    path: str
    line: int
    test_function: str
    kind: str       # "mock-budget" | "internal-mock" | "parse-error"
    severity: str   # "Important" | "Critical"
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


def load_seam_allowlist(path: Path) -> frozenset[str]:
    """Load .cross-chunk-seams style file: one target per line; # for comments."""
    if not path.exists():
        return frozenset()
    targets: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        targets.add(line)
    return frozenset(targets)


def _is_boundary(target: str) -> bool:
    """True if target's root module is an allowed external boundary."""
    if not target:
        return False
    root = target.split(".", 1)[0]
    return root in _BOUNDARY_DEFAULTS


def _attr_to_dotted(node: ast.AST) -> str:
    """Render an ast.Attribute / ast.Name chain as a dotted string."""
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return ".".join(reversed(parts))


def _extract_target_arg(call: ast.Call) -> str | None:
    """Given a Call node like patch('x') or patch.object(x, 'method'), return target."""
    if not call.args:
        return None
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    if isinstance(first, (ast.Attribute, ast.Name)):
        return _attr_to_dotted(first)
    return None


def _is_patch_decorator(decorator: ast.expr) -> bool:
    """Is this decorator @patch(...) / @mock.patch(...) / @patch.object(...)?"""
    target = decorator
    if isinstance(target, ast.Call):
        target = target.func
    if isinstance(target, ast.Name):
        return target.id == "patch"
    if isinstance(target, ast.Attribute):
        if target.attr == "patch":
            return True
        if target.attr == "object":
            inner = target.value
            if isinstance(inner, ast.Name) and inner.id == "patch":
                return True
            if isinstance(inner, ast.Attribute) and inner.attr == "patch":
                return True
    return False


def _is_patch_call_func(func: ast.expr) -> bool:
    """Is this call's function patch / mocker.patch / mocker.spy / mock.patch?"""
    if isinstance(func, ast.Name):
        return func.id == "patch"
    if isinstance(func, ast.Attribute):
        if func.attr in {"patch", "spy"}:
            return True
        if func.attr == "object":
            inner = func.value
            if isinstance(inner, ast.Attribute) and inner.attr == "patch":
                return True
    return False


def _walk_function_for_mocks(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[MockCall]:
    """Collect all mock invocations attributed to this test function."""
    mocks: list[MockCall] = []

    # Decorators on the function itself
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call) and _is_patch_decorator(dec):
            target = _extract_target_arg(dec)
            if target:
                mocks.append(MockCall(target=target, line=dec.lineno, kind="decorator"))

    # Inline calls — walk each body statement separately (NOT the whole `func`,
    # which would also walk the decorator_list and double-count decorators).
    for stmt in func.body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call) and _is_patch_call_func(node.func):
                target = _extract_target_arg(node)
                if target:
                    mocks.append(MockCall(target=target, line=node.lineno, kind="call"))

    return mocks


def lint_file(
    path: Path,
    seam_allowlist: frozenset[str] = frozenset(),
) -> list[LintViolation]:
    """Lint a single Python test file. Returns violations (empty if clean)."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [LintViolation(
            path=str(path),
            line=0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=f"could not read file: {exc}",
        )]

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [LintViolation(
            path=str(path),
            line=exc.lineno or 0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=f"syntax error: {exc.msg}",
        )]

    violations: list[LintViolation] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue

        mocks = _walk_function_for_mocks(node)

        # Rule 1 — mock budget: <=1 mock per test
        if len(mocks) > 1:
            violations.append(LintViolation(
                path=str(path),
                line=node.lineno,
                test_function=node.name,
                kind="mock-budget",
                severity="Important",
                message=(
                    f"test '{node.name}' has {len(mocks)} mocks; "
                    f"TDD-2 limits tests to <=1 mock at an external boundary"
                ),
            ))

        # Rule 2 — internal-class mocking: target must be at boundary
        for mock in mocks:
            if _is_boundary(mock.target):
                continue
            in_seam = mock.target in seam_allowlist
            severity = "Critical" if in_seam else "Important"
            suffix = (
                " — target is a documented cross-chunk seam (.cross-chunk-seams)"
                if in_seam else ""
            )
            violations.append(LintViolation(
                path=str(path),
                line=mock.line,
                test_function=node.name,
                kind="internal-mock",
                severity=severity,
                message=(
                    f"test '{node.name}' mocks internal target "
                    f"'{mock.target}'{suffix}"
                ),
            ))

    return violations


def lint_files(
    paths: Iterable[Path],
    seam_allowlist: frozenset[str] = frozenset(),
) -> list[LintViolation]:
    """Lint multiple files; aggregate violations."""
    all_violations: list[LintViolation] = []
    for p in paths:
        all_violations.extend(lint_file(p, seam_allowlist))
    return all_violations


def format_human(violations: list[LintViolation]) -> str:
    """Render violations as human-readable text."""
    if not violations:
        return "No mock-budget violations.\n"
    lines: list[str] = []
    crits = sum(1 for v in violations if v.severity == "Critical")
    imps = sum(1 for v in violations if v.severity == "Important")
    lines.append(
        f"{len(violations)} mock-budget findings ({crits} Critical, {imps} Important):\n\n"
    )
    for v in violations:
        lines.append(
            f"  [{v.severity}] {v.path}:{v.line} ({v.kind})\n"
            f"    {v.message}\n\n"
        )
    return "".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mock_budget_lint",
        description=(
            "TDD-2 mock-budget linter (LINT-MOCK-1). Flags >1 mock per test "
            "and internal-class mocking."
        ),
    )
    parser.add_argument(
        "files", nargs="+", type=Path,
        help="Python test files to lint",
    )
    parser.add_argument(
        "--seam-allowlist", type=Path, default=None,
        help=(
            "Path to .cross-chunk-seams allowlist (one target per line; "
            "comments via #). Targets in this list escalate from Important "
            "to Critical."
        ),
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 1 on any findings (default: exit 1 only on Critical)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output findings as JSON (machine-readable)",
    )
    args = parser.parse_args(argv)

    seam_allowlist = (
        load_seam_allowlist(args.seam_allowlist) if args.seam_allowlist else frozenset()
    )

    violations = lint_files(args.files, seam_allowlist)

    if args.json:
        payload = {
            "violations": [v.to_dict() for v in violations],
            "summary": {
                "total": len(violations),
                "critical": sum(1 for v in violations if v.severity == "Critical"),
                "important": sum(1 for v in violations if v.severity == "Important"),
            },
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        sys.stdout.write(format_human(violations))

    has_critical = any(v.severity == "Critical" for v in violations)
    if args.strict and violations:
        return 1
    if has_critical:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
