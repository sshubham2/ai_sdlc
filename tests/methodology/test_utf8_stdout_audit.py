"""Unit tests for tools.utf8_stdout_audit (UTF8-STDOUT-1).

Covers AC #2 (structural rule fires per-tool) and AC #3 (audit emits
violations + JSON shape + exit codes). The behavioural cp1252-subprocess
regression test (AC #4) lives in `test_utf8_stdout_regression.py`,
separated per M5 ACCEPTED-FIXED for runtime isolation.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import utf8_stdout_audit


REPO_ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


def _conforming_tool(body: str = "") -> str:
    """Synthetic conforming audit tool source."""
    return (
        '"""Conforming synthetic audit tool."""\n'
        "from tools import _stdout\n"
        "import sys\n"
        "\n"
        "def main(argv: list[str] | None = None) -> int:\n"
        "    _stdout.reconfigure_stdout_utf8()\n"
        f"    {body or 'return 0'}\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    sys.exit(main())\n"
    )


def _non_conforming_tool(body: str = "") -> str:
    """Synthetic non-conforming tool (no reconfigure call)."""
    return (
        '"""Non-conforming synthetic audit tool."""\n'
        "import argparse\n"
        "import sys\n"
        "\n"
        "def main(argv: list[str] | None = None) -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        f"    {body or 'return 0'}\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    sys.exit(main())\n"
    )


def _build_synthetic_root(tmp_path: Path, files: dict[str, str]) -> Path:
    """Build a synthetic repo root with tools/ subdir populated from files dict."""
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    (tools_dir / "__init__.py").write_text("", encoding="utf-8")
    (tools_dir / "_stdout.py").write_text(
        "def reconfigure_stdout_utf8(): pass\n", encoding="utf-8"
    )
    for name, content in files.items():
        (tools_dir / name).write_text(content, encoding="utf-8")
    return tmp_path


# ---------- AC #2: structural rule fires per-tool ----------


def test_every_tool_with_main_calls_reconfigure_first():
    """Run audit on real post-slice-023 repo; every audit tool MUST conform."""
    result = utf8_stdout_audit.audit_root(REPO_ROOT)
    assert result.status == "clean", (
        f"UTF8-STDOUT-1 self-audit failed: {result.to_dict()}"
    )
    assert result.tools_with_main >= 17, (
        f"Expected >=17 audit tools with main(); got {result.tools_with_main}"
    )


def test_stdout_helper_module_itself_exempt(tmp_path):
    """`tools/_stdout.py` is a helper (no main()); MUST NOT be scanned."""
    root = _build_synthetic_root(
        tmp_path,
        {"sample_audit.py": _conforming_tool()},
    )
    result = utf8_stdout_audit.audit_root(root)
    scanned_paths = [
        v.file for v in result.violations
    ]
    assert "tools/_stdout.py" not in scanned_paths
    # And the result should show only the synthetic tool, not _stdout.py
    assert result.tools_scanned == 1


def test_every_tool_uses_canonical_from_tools_import_stdout():
    """Per M4 ACCEPTED-FIXED: pinned import form 'from tools import _stdout'."""
    tools_dir = REPO_ROOT / "tools"
    # Inspect each conforming tool's AST for the canonical import
    for path in sorted(tools_dir.glob("*.py")):
        if path.name.startswith("_") or path.name == "__init__.py":
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        # Find main(); skip if no main
        has_main = any(
            isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == "main"
            for n in tree.body
        )
        if not has_main:
            continue
        # Find canonical import
        has_canonical = utf8_stdout_audit._has_canonical_import(tree)
        assert has_canonical, (
            f"{path.name}: missing canonical 'from tools import _stdout' import"
        )


# ---------- AC #3: audit emits violations + JSON + exit codes ----------


def test_audit_flags_tool_missing_reconfigure_call(tmp_path):
    """Synthetic tool without the reconfigure call MUST flag a violation."""
    root = _build_synthetic_root(
        tmp_path,
        {"broken_audit.py": _non_conforming_tool()},
    )
    result = utf8_stdout_audit.audit_root(root)
    assert result.status == "violation"
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.file == "tools/broken_audit.py"
    assert v.function == "main"
    assert "reconfigure_stdout_utf8" in v.message


def test_audit_flags_tool_with_reconfigure_after_argparse(tmp_path):
    """Reconfigure after argparse is still a violation (must be FIRST stmt)."""
    delayed_call = (
        '"""Delayed-reconfigure synthetic tool."""\n'
        "from tools import _stdout\n"
        "import argparse\n"
        "import sys\n"
        "\n"
        "def main(argv: list[str] | None = None) -> int:\n"
        "    parser = argparse.ArgumentParser()\n"
        "    _stdout.reconfigure_stdout_utf8()\n"  # WRONG: not first
        "    return 0\n"
    )
    root = _build_synthetic_root(tmp_path, {"delayed_audit.py": delayed_call})
    result = utf8_stdout_audit.audit_root(root)
    assert result.status == "violation"
    assert any(
        "first executable statement is not" in v.message
        for v in result.violations
    )


def test_audit_clean_on_canonical_pattern(tmp_path):
    """Conforming synthetic tool returns clean."""
    root = _build_synthetic_root(
        tmp_path,
        {"clean_audit.py": _conforming_tool()},
    )
    result = utf8_stdout_audit.audit_root(root)
    assert result.status == "clean"
    assert result.tools_clean == 1


def test_audit_json_output_shape(tmp_path):
    """`--json` emits the canonical JSON shape (tools_scanned / with_main / clean / violations / status)."""
    root = _build_synthetic_root(
        tmp_path,
        {"clean_audit.py": _conforming_tool()},
    )
    proc = subprocess.run(
        [PY, "-m", "tools.utf8_stdout_audit", "--json", "--root", str(root)],
        capture_output=True, text=True, encoding="utf-8",
        cwd=REPO_ROOT,
    )
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert set(payload.keys()) == {
        "tools_scanned", "tools_with_main", "tools_clean",
        "violations", "status",
    }
    assert payload["status"] == "clean"
    assert payload["tools_clean"] == payload["tools_with_main"]
    assert isinstance(payload["violations"], list)


def test_audit_exit_code_zero_on_clean_one_on_violation(tmp_path):
    """exit 0 clean / exit 1 violation."""
    clean_root = _build_synthetic_root(
        tmp_path / "clean",
        {"clean_audit.py": _conforming_tool()},
    )
    proc_clean = subprocess.run(
        [PY, "-m", "tools.utf8_stdout_audit", "--root", str(clean_root)],
        capture_output=True, text=True, encoding="utf-8",
        cwd=REPO_ROOT,
    )
    assert proc_clean.returncode == 0

    violation_root = _build_synthetic_root(
        tmp_path / "broken",
        {"broken_audit.py": _non_conforming_tool()},
    )
    proc_viol = subprocess.run(
        [PY, "-m", "tools.utf8_stdout_audit", "--root", str(violation_root)],
        capture_output=True, text=True, encoding="utf-8",
        cwd=REPO_ROOT,
    )
    assert proc_viol.returncode == 1


def test_output_contract_invariant(tmp_path):
    """Per B5 ACCEPTED-FIXED: tools_clean == tools_with_main - len(violations)."""
    # Mixed root: one clean, one broken
    root = _build_synthetic_root(
        tmp_path,
        {
            "clean_audit.py": _conforming_tool(),
            "broken_audit.py": _non_conforming_tool(),
        },
    )
    result = utf8_stdout_audit.audit_root(root)
    assert result.tools_clean == result.tools_with_main - len(result.violations)
    # tools_scanned >= tools_with_main (some scanned files may lack main())
    assert result.tools_scanned >= result.tools_with_main
    # status flag matches violations count
    assert (result.status == "clean") == (len(result.violations) == 0)
