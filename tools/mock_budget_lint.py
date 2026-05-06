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


# TypeScript / JavaScript boundary modules where mocking is allowed per TDD-2.
# Includes node:* prefixes (modern Node) and bare names (legacy compat).
# Scoped npm packages match at the scope level (e.g., @aws-sdk matches
# @aws-sdk/client-s3, @aws-sdk/client-dynamodb, etc.).
_TS_BOUNDARY_DEFAULTS: frozenset[str] = frozenset({
    # HTTP / networking
    "axios", "node-fetch", "got", "ky", "undici", "fetch", "superagent",
    "node:http", "http", "node:https", "https",
    "node:net", "net", "node:url", "url", "node:dns", "dns",
    # Filesystem
    "node:fs", "fs", "node:fs/promises", "fs/promises",
    "node:path", "path",
    # Process / OS
    "node:child_process", "child_process",
    "node:os", "os",
    "node:process", "process",
    # Crypto / streams
    "node:crypto", "crypto", "node:stream", "stream",
    # Databases / ORMs
    "pg", "mysql", "mysql2", "mongodb", "mongoose",
    "redis", "ioredis", "sqlite3", "better-sqlite3",
    "prisma", "@prisma/client", "knex", "typeorm",
    # Cloud / vendor SDKs (npm scopes match all subpackages)
    "@aws-sdk", "aws-sdk",
    "@google-cloud", "googleapis",
    "stripe", "@anthropic-ai/sdk", "openai", "@azure",
    # Email / messaging
    "nodemailer", "kafkajs",
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
    """True if target's root module is an allowed external boundary (Python)."""
    if not target:
        return False
    root = target.split(".", 1)[0]
    return root in _BOUNDARY_DEFAULTS


def _is_ts_boundary(target: str) -> bool:
    """True if target is an external TypeScript / JavaScript module boundary.

    Relative imports (./foo, ../foo, /abs) are never boundaries. Scoped npm
    packages match at the scope level (e.g., @aws-sdk/client-s3 matches @aws-sdk).
    """
    if not target:
        return False
    if target.startswith(("./", "../", "/")):
        return False
    if target in _TS_BOUNDARY_DEFAULTS:
        return True
    if "/" in target:
        first = target.split("/", 1)[0]
        if first in _TS_BOUNDARY_DEFAULTS:
            return True
    return False


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
    """Lint a single test file (any supported language). Dispatches by extension.

    Supported extensions:
        .py                              -> _lint_python
        .ts, .tsx, .js, .jsx, .mts, .cts -> _lint_typescript

    Unsupported extensions return a single parse-error finding rather than
    crashing — the runner can skip non-test files cleanly.
    """
    suffix = path.suffix.lower()
    if suffix == ".py":
        return _lint_python(path, seam_allowlist)
    if suffix in {".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"}:
        return _lint_typescript(path, seam_allowlist)
    if suffix == ".go":
        return _lint_go(path, seam_allowlist)
    return [LintViolation(
        path=str(path),
        line=0,
        test_function="<file>",
        kind="parse-error",
        severity="Important",
        message=(
            f"unsupported file extension: '{suffix}' "
            f"(supported: .py, .ts/.tsx/.js/.jsx/.mts/.cts, .go)"
        ),
    )]


def _lint_python(
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


def _lint_typescript(
    path: Path,
    seam_allowlist: frozenset[str] = frozenset(),
) -> list[LintViolation]:
    """Lint a single TypeScript / JavaScript test file via tree-sitter.

    Detects mocks from vitest (vi.mock, vi.spyOn, vi.doMock), jest (jest.mock,
    jest.spyOn, jest.doMock), testdouble (td.replace), and sinon (sinon.stub,
    sinon.replace, sinon.spy, sinon.mock). Test scopes are it()/test() calls
    (and their .only / .skip / .concurrent / .each / .todo / .fails variants);
    mocks are attributed to the innermost containing test scope.

    Limitations (v1):
    - Module-level vi.mock / jest.mock calls (hoisted; apply to all tests in
      the file) are not attributed to any specific test's count. Per-test
      mocks inside the it()/test() body are counted.
    - beforeEach / afterEach mocks are not attributed to individual tests.
    """
    try:
        import tree_sitter
        import tree_sitter_typescript as _ts_ts
    except ImportError:
        return [LintViolation(
            path=str(path),
            line=0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=(
                "tree_sitter and tree_sitter_typescript packages are required "
                "for TypeScript/JavaScript linting; install via "
                "`pip install tree_sitter tree_sitter_typescript`"
            ),
        )]

    try:
        source_bytes = path.read_bytes()
    except OSError as exc:
        return [LintViolation(
            path=str(path),
            line=0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=f"could not read file: {exc}",
        )]

    suffix = path.suffix.lower()
    lang_fn = (
        _ts_ts.language_tsx
        if suffix in {".tsx", ".jsx"}
        else _ts_ts.language_typescript
    )
    lang = tree_sitter.Language(lang_fn())
    parser = tree_sitter.Parser(lang)
    tree = parser.parse(source_bytes)

    if tree.root_node.has_error:
        return [LintViolation(
            path=str(path),
            line=tree.root_node.start_point[0] + 1,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message="syntax error in TypeScript/JavaScript source (tree-sitter)",
        )]

    # Test-function names and member-expression variants (vitest / jest / mocha)
    _TEST_FUNCS = frozenset({"it", "test"})
    _TEST_VARIANTS = frozenset({
        "only", "skip", "skipIf", "concurrent", "todo", "fails", "each", "runIf",
    })

    # (object_name, method_name) -> mock kind
    _MOCK_PATTERNS = {
        ("vi", "mock"): "vi-mock",
        ("vi", "doMock"): "vi-mock",
        ("vi", "spyOn"): "vi-spy",
        ("jest", "mock"): "jest-mock",
        ("jest", "doMock"): "jest-mock",
        ("jest", "spyOn"): "jest-spy",
        ("td", "replace"): "td-replace",
        ("sinon", "stub"): "sinon-stub",
        ("sinon", "replace"): "sinon-replace",
        ("sinon", "spy"): "sinon-spy",
        ("sinon", "mock"): "sinon-mock",
    }

    def _txt(node) -> str:
        return node.text.decode("utf-8", errors="replace")

    def _callee_obj_method(call_node):
        func = call_node.child_by_field_name("function")
        if func is None:
            return (None, None)
        if func.type == "identifier":
            return (None, _txt(func))
        if func.type == "member_expression":
            obj = func.child_by_field_name("object")
            prop = func.child_by_field_name("property")
            return (
                _txt(obj) if obj else None,
                _txt(prop) if prop else None,
            )
        return (None, None)

    def _is_test_call(call_node) -> bool:
        obj, method = _callee_obj_method(call_node)
        if obj is None and method in _TEST_FUNCS:
            return True
        if obj in _TEST_FUNCS and method in _TEST_VARIANTS:
            return True
        return False

    def _test_description(call_node) -> str:
        args = call_node.child_by_field_name("arguments")
        if args is None:
            return "<unknown>"
        for child in args.children:
            if child.type in {"(", ",", ")"}:
                continue
            if child.type == "string":
                return _txt(child).strip("'\"`")
            return "<unknown>"
        return "<unknown>"

    def _mock_kind(call_node):
        return _MOCK_PATTERNS.get(_callee_obj_method(call_node))

    def _extract_mock_target(call_node):
        args = call_node.child_by_field_name("arguments")
        if args is None:
            return None
        for child in args.children:
            if child.type in {"(", ",", ")"}:
                continue
            if child.type == "string":
                return _txt(child).strip("'\"`")
            if child.type in {"identifier", "member_expression"}:
                return _txt(child)
            return None
        return None

    test_scopes: list[dict] = []   # {start, end, name, line, mocks}
    mock_calls: list[tuple[int, MockCall]] = []  # (start_byte, MockCall)

    def _walk(node):
        if node.type == "call_expression":
            if _is_test_call(node):
                test_scopes.append({
                    "start": node.start_byte,
                    "end": node.end_byte,
                    "name": _test_description(node),
                    "line": node.start_point[0] + 1,
                    "mocks": [],
                })
            kind = _mock_kind(node)
            if kind:
                target = _extract_mock_target(node)
                if target:
                    mock_calls.append((node.start_byte, MockCall(
                        target=target,
                        line=node.start_point[0] + 1,
                        kind=kind,
                    )))
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)

    # Attribute each mock to the innermost containing test scope
    for byte_pos, mock in mock_calls:
        innermost = None
        for scope in test_scopes:
            if scope["start"] <= byte_pos <= scope["end"]:
                if (
                    innermost is None
                    or (scope["end"] - scope["start"])
                    < (innermost["end"] - innermost["start"])
                ):
                    innermost = scope
        if innermost is not None:
            innermost["mocks"].append(mock)

    # Apply rules per scope
    violations: list[LintViolation] = []
    for scope in test_scopes:
        mocks = scope["mocks"]
        if not mocks:
            continue
        test_label = f"it('{scope['name']}')"

        # Rule 1 — mock budget
        if len(mocks) > 1:
            violations.append(LintViolation(
                path=str(path),
                line=scope["line"],
                test_function=test_label,
                kind="mock-budget",
                severity="Important",
                message=(
                    f"test '{scope['name']}' has {len(mocks)} mocks; "
                    f"TDD-2 limits tests to <=1 mock at an external boundary"
                ),
            ))

        # Rule 2 — internal mocks
        for mock in mocks:
            if _is_ts_boundary(mock.target):
                continue
            in_seam = mock.target in seam_allowlist
            severity = "Critical" if in_seam else "Important"
            suffix_msg = (
                " — target is a documented cross-chunk seam (.cross-chunk-seams)"
                if in_seam else ""
            )
            violations.append(LintViolation(
                path=str(path),
                line=mock.line,
                test_function=test_label,
                kind="internal-mock",
                severity=severity,
                message=(
                    f"test '{scope['name']}' mocks internal target "
                    f"'{mock.target}'{suffix_msg}"
                ),
            ))

    return violations


def _lint_go(
    path: Path,
    seam_allowlist: frozenset[str] = frozenset(),  # reserved for v2 internal-mock support
) -> list[LintViolation]:
    """Lint a single Go test file via tree-sitter.

    v1 enforces mock-budget only (>1 mock per test = Important). Internal-mock
    classification is deferred to a v2 — Go mocks are type-based without
    string targets, so accurate boundary classification requires import-aware
    analysis not yet implemented.

    Detection (v1):
    - Test scopes: function_declaration whose name matches `^Test[A-Z]` (Go
      convention; uppercase second char filters out helpers like `Testing`)
    - Subtests: call_expression matching `<ident>.Run("name", func ...)`
    - Mock instances: call_expression whose function name matches
      `^New(Mock|Fake|Stub|Spy)` — covers gomock-generated mocks
      (NewMockXxx), manual mocks, fakes, stubs, spies

    Limitations (v1):
    - `var x MockUserService` declarations not yet counted (constructor pattern
      is the dominant idiom in Go test code)
    - testify `mock.Mock` embedding not yet detected (would require type-graph
      walk; v2 candidate)
    - `gomock.NewController` itself not counted (it's infra; the NewMockXxx
      calls that follow are the mocks)
    - `seam_allowlist` parameter ignored in v1; reserved for v2 when
      internal-mock support arrives

    Function declarations like `func NewMockUserService()` are correctly NOT
    counted — only call_expressions match, not function_declaration nodes.
    """
    try:
        import tree_sitter
        import tree_sitter_go as _ts_go
    except ImportError:
        return [LintViolation(
            path=str(path),
            line=0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=(
                "tree_sitter and tree_sitter_go packages are required for Go "
                "linting; install via `pip install tree_sitter tree_sitter_go`"
            ),
        )]

    try:
        source_bytes = path.read_bytes()
    except OSError as exc:
        return [LintViolation(
            path=str(path),
            line=0,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message=f"could not read file: {exc}",
        )]

    lang = tree_sitter.Language(_ts_go.language())
    parser = tree_sitter.Parser(lang)
    tree = parser.parse(source_bytes)

    if tree.root_node.has_error:
        return [LintViolation(
            path=str(path),
            line=tree.root_node.start_point[0] + 1,
            test_function="<file>",
            kind="parse-error",
            severity="Important",
            message="syntax error in Go source (tree-sitter)",
        )]

    import re as _re
    _GO_MOCK_FUNC_RE = _re.compile(r"^New(Mock|Fake|Stub|Spy)")

    def _txt(node) -> str:
        return node.text.decode("utf-8", errors="replace")

    def _is_test_func_decl(node) -> bool:
        if node.type != "function_declaration":
            return False
        name = node.child_by_field_name("name")
        if name is None:
            return False
        text = _txt(name)
        return len(text) >= 5 and text.startswith("Test") and text[4].isupper()

    def _is_subtest_run_call(node) -> bool:
        if node.type != "call_expression":
            return False
        func = node.child_by_field_name("function")
        if func is None or func.type != "selector_expression":
            return False
        field = func.child_by_field_name("field")
        if field is None or _txt(field) != "Run":
            return False
        args = node.child_by_field_name("arguments")
        if args is None:
            return False
        for child in args.children:
            if child.type in {"(", ",", ")"}:
                continue
            return child.type in {"interpreted_string_literal", "raw_string_literal"}
        return False

    def _subtest_name(node) -> str:
        args = node.child_by_field_name("arguments")
        if args is None:
            return "<unknown>"
        for child in args.children:
            if child.type in {"(", ",", ")"}:
                continue
            if child.type in {"interpreted_string_literal", "raw_string_literal"}:
                return _txt(child).strip("\"`")
            return "<unknown>"
        return "<unknown>"

    def _mock_constructor_name(node) -> str | None:
        if node.type != "call_expression":
            return None
        func = node.child_by_field_name("function")
        if func is None:
            return None
        if func.type == "identifier":
            return _txt(func)
        if func.type == "selector_expression":
            field = func.child_by_field_name("field")
            if field is not None:
                return _txt(field)
        return None

    test_scopes: list[dict] = []
    mock_calls: list[tuple[int, MockCall]] = []

    def _walk(node):
        if _is_test_func_decl(node):
            name_node = node.child_by_field_name("name")
            test_scopes.append({
                "start": node.start_byte,
                "end": node.end_byte,
                "name": _txt(name_node) if name_node else "<unknown>",
                "line": node.start_point[0] + 1,
                "mocks": [],
            })
        if _is_subtest_run_call(node):
            test_scopes.append({
                "start": node.start_byte,
                "end": node.end_byte,
                "name": _subtest_name(node),
                "line": node.start_point[0] + 1,
                "mocks": [],
            })
        if node.type == "call_expression":
            func_name = _mock_constructor_name(node)
            if func_name and _GO_MOCK_FUNC_RE.match(func_name):
                mock_calls.append((node.start_byte, MockCall(
                    target=func_name,
                    line=node.start_point[0] + 1,
                    kind="go-mock-constructor",
                )))
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)

    # Attribute each mock call to the innermost containing test scope
    for byte_pos, mock in mock_calls:
        innermost = None
        for scope in test_scopes:
            if scope["start"] <= byte_pos <= scope["end"]:
                if (
                    innermost is None
                    or (scope["end"] - scope["start"])
                    < (innermost["end"] - innermost["start"])
                ):
                    innermost = scope
        if innermost is not None:
            innermost["mocks"].append(mock)

    # Apply mock-budget rule (v1 — internal-mock and seam allowlist deferred to v2)
    violations: list[LintViolation] = []
    for scope in test_scopes:
        mocks = scope["mocks"]
        if len(mocks) > 1:
            violations.append(LintViolation(
                path=str(path),
                line=scope["line"],
                test_function=scope["name"],
                kind="mock-budget",
                severity="Important",
                message=(
                    f"test '{scope['name']}' has {len(mocks)} mock instances; "
                    f"TDD-2 limits tests to <=1 mock per test"
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
