"""Pin slice-079 Fix S (P3.10 reframed per /critique B2+M3): UTF-8 encoding kwarg structural-pin.

/critique B2 empirical APED-1 grep at /critique time demonstrated all 9 encoded-I/O sites in
`tools/slice_queue_writer.py` (L134, 183, 214, 266, 351, 450, 703, 790, 847) ALREADY carry
`encoding="utf-8"` — the helper was correct pre-slice-079. Fix S is REGRESSION-GUARD ONLY:
asserts no encoded-I/O call (`Path.read_text` / `Path.write_text` / `open()` /
`subprocess.run(text=True, ...)`) silently loses the encoding kwarg.

FAIL→PASS contrast: fixture-mutation test deletes `encoding="utf-8"` from one site → walker flags it.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / "tools" / "slice_queue_writer.py"


def _has_encoding_utf8_kwarg(call: ast.Call) -> bool:
    for kw in call.keywords:
        if kw.arg == "encoding":
            if isinstance(kw.value, ast.Constant) and kw.value.value == "utf-8":
                return True
    return False


def _is_path_text_io(call: ast.Call) -> bool:
    """True if this Call is a Path.read_text / Path.write_text invocation (attribute call)."""
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr in {"read_text", "write_text"}
    return False


def _is_bare_open(call: ast.Call) -> bool:
    """True if this Call is `open(...)` (a builtin call) — not Path.open."""
    func = call.func
    return isinstance(func, ast.Name) and func.id == "open"


def _is_subprocess_run_with_text_true(call: ast.Call) -> bool:
    """True if this Call is `subprocess.run(..., text=True, ...)`."""
    func = call.func
    is_subprocess_run = (
        isinstance(func, ast.Attribute)
        and func.attr == "run"
        and isinstance(func.value, ast.Name)
        and func.value.id == "subprocess"
    )
    if not is_subprocess_run:
        return False
    for kw in call.keywords:
        if kw.arg == "text":
            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                return True
    return False


def _scan_encoded_io_sites(source: str) -> list[tuple[int, str]]:
    """Return list of (lineno, kind) for each encoded-I/O call lacking encoding='utf-8'."""
    tree = ast.parse(source)
    offenders: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _is_path_text_io(node):
            kind = "Path.read_text|write_text"
        elif _is_bare_open(node):
            kind = "open()"
        elif _is_subprocess_run_with_text_true(node):
            kind = "subprocess.run(text=True)"
        else:
            continue
        if not _has_encoding_utf8_kwarg(node):
            offenders.append((node.lineno, kind))
    return offenders


def test_no_encoded_io_site_lacks_encoding_kwarg() -> None:
    """Fix S: every encoded-I/O call in tools/slice_queue_writer.py carries encoding='utf-8'."""
    source = TARGET.read_text(encoding="utf-8")
    offenders = _scan_encoded_io_sites(source)
    assert offenders == [], (
        f"Fix S regression: tools/slice_queue_writer.py has {len(offenders)} encoded-I/O call(s) "
        f"missing `encoding=\"utf-8\"` kwarg: {offenders}. The P3.10 mojibake class re-opens at this surface."
    )


def test_fixture_mutation_triggers_failure() -> None:
    """Fix S FAIL→PASS contrast proof: a synthetic mutation removing encoding='utf-8' is detected.

    This guards the structural-pin's discriminator power: if a future refactor weakens the AST walker
    (e.g., flatten to substring match), this contrast test still fires on the mutated input.
    """
    source = TARGET.read_text(encoding="utf-8")
    # Mutation: remove the first `encoding="utf-8"` occurrence — synthetic regression
    mutated = source.replace(', encoding="utf-8"', "", 1)
    if mutated == source:
        mutated = source.replace('encoding="utf-8"', "", 1)
    assert mutated != source, "Sanity: synthetic mutation produced no change"
    offenders = _scan_encoded_io_sites(mutated)
    assert offenders, (
        "Fix S walker discriminator regression: synthetic mutation removing encoding='utf-8' "
        "from a real call site was NOT flagged. AST walker has degraded to a non-empirical check."
    )
