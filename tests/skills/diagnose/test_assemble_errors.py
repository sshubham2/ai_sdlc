"""Tests for assemble.load_findings YAML error handling (slice-001 / AC #4 / M2).

Validates that load_findings:
- Prints offending file + line/column from problem_mark when present
- Falls back gracefully when problem_mark is absent (M2)

Rule reference: slice-001 ACs #4, disposition M2.
"""
import re
from pathlib import Path

import pytest

from assemble import load_findings


def test_yaml_error_includes_file_line_context(tmp_path: Path, capsys):
    """A YAML with an unquoted colon produces an actionable error.

    Defect class: 2026-05-09 root-cause #3 — bare error 'YAML parse failure
    in <file>: <yaml's str>' didn't surface line/column to the operator.
    AC #4 says: file + line/column + ±2 lines context.
    Disposition ref: AC #4.
    """
    findings_dir = tmp_path / "findings"
    findings_dir.mkdir()
    bad_yaml = (
        "- id: F-DEAD-aabbccdd\n"
        "  pass: 03a-dead-code\n"
        "  category: dead-code\n"
        "  severity: low\n"
        "  title: Reminders cluster: stub UI broken\n"  # unquoted ':' in scalar
        "  description: |\n"
        "    Some text.\n"
        "  evidence: []\n"
    )
    (findings_dir / "03a-dead-code.yaml").write_text(bad_yaml, encoding="utf-8")
    with pytest.raises(SystemExit):
        load_findings(findings_dir)
    captured = capsys.readouterr()
    err = captured.err + captured.out  # SystemExit may go to either
    # File path appears
    assert "03a-dead-code.yaml" in err
    # Line indicator appears (the offending colon is around line 5)
    assert re.search(r"line\s*\d+", err, re.IGNORECASE), (
        f"expected line-number indicator in error; got: {err!r}"
    )


def test_yaml_error_without_problem_mark_falls_back_gracefully(
    tmp_path: Path, capsys, monkeypatch
):
    """A YAMLError without problem_mark doesn't crash with AttributeError.

    Defect class: per critique M2 — `problem_mark` is on MarkedYAMLError,
    not bare YAMLError. Naive `exc.problem_mark` access raises
    AttributeError, masking the real YAML problem. The handler must use
    `getattr(exc, 'problem_mark', None)` and fall back to a plain message.

    Test strategy: monkeypatch yaml.safe_load to raise a bare YAMLError
    (no problem_mark) and verify load_findings exits with a sensible
    message rather than crashing.
    Disposition ref: M2.
    """
    import yaml

    findings_dir = tmp_path / "findings"
    findings_dir.mkdir()
    (findings_dir / "01-intent.yaml").write_text("[]", encoding="utf-8")

    def raise_bare(*args, **kwargs):
        raise yaml.YAMLError("synthetic bare YAMLError without problem_mark")

    monkeypatch.setattr(yaml, "safe_load", raise_bare)

    with pytest.raises(SystemExit):
        load_findings(findings_dir)
    captured = capsys.readouterr()
    err = captured.err + captured.out
    # The synthetic exception's message should appear — proves we didn't
    # crash with AttributeError before printing.
    assert "synthetic bare YAMLError" in err or "01-intent.yaml" in err
