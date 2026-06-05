"""Bug: the ETC-1 exploratory-charter gate passes *vacuously* on an annotated flag line.

Source: risk-register R-36 + slice-115 reflection "Discovered" note; distilled +
confirmed at /slice Step 3c (BFRD-1 bug-fix repro prelude).

The mission-brief template (and every real charter brief, e.g. slice-115's) writes
the opt-in flag with a trailing inline annotation::

    **Exploratory-charter**: true  (optional; per ETC-1 — opt-in charter-based exploratory testing)

ETC-1's flag-detection regex (``tools/exploratory_charter_audit.py``)::

    _ETC_FIELD_RE = re.compile(r"^\\*\\*Exploratory[-\\s]?charter\\*\\*\\s*:\\s*(true|false)\\s*$", re.IGNORECASE)

anchors the value with ``(true|false)\\s*$`` — the line MUST end right after the
boolean (modulo trailing whitespace). The idiomatic ``  (optional; …)`` annotation
makes ``.match`` fail, so ``_detect_etc_flag`` returns ``False``. The audit then
reports "not enabled" and the charter gate enforces NOTHING — a vacuous pass on
EVERY charter slice that keeps the template annotation (R-7 silent-disable class).

This is a divergence from its sibling: TF-1's ``_TEST_FIRST_FIELD_RE`` already
accepts an annotated value via a lookahead — ``(true|false)(?=[\\s(]|$)`` — whose
docstring (``tools/test_first_audit.py:53``) explicitly warns against the loose
``(true|false)\\b.*$`` form that would re-admit malformed suffixes. The fix should
bring ETC-1 to parity with that already-correct pattern (NOT a loose ``.*$``).

Expected (fix contract):
    1. ``_detect_etc_flag`` returns ``True`` for an annotated ``true`` line.
    2. ``audit_brief_file`` sets ``exploratory_charter_enabled is True`` for a
       mission-brief carrying the annotated ``true`` flag (the real slice-115 case).
    3. An annotated ``false`` line still resolves to disabled (no over-correction).
    4. A malformed-suffix value (``trueish``/``false-positive``) is NOT accepted as
       a valid boolean — the fix must not regress to a loose ``.*$`` (guards the
       TF-1 / R-7 / TFFL-1 concern).

Actual (current defect):
    The annotated ``true`` line fails the ``\\s*$`` anchor → ``_detect_etc_flag``
    returns ``False`` → ``exploratory_charter_enabled`` is ``False`` → vacuous pass.

Fix slice: slice-NNN-fix-etc-1-charter-flag-detection (numbered when /slice runs).
``test_annotated_true_flag_is_detected_enabled`` and
``test_audit_brief_with_annotated_true_reports_enabled`` FAIL today and PASS once
the regex is brought to TF-1 parity. The control/guard tests pass today and must
keep passing after the fix.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.exploratory_charter_audit import _detect_etc_flag, audit_brief_file

# The exact annotated form the mission-brief template emits and slice-115 carried.
_ANNOTATED_TRUE = (
    "**Exploratory-charter**: true  "
    "(optional; per ETC-1 — opt-in charter-based exploratory testing)"
)
_ANNOTATED_FALSE = (
    "**Exploratory-charter**: false  "
    "(optional; per ETC-1 — opt-in charter-based exploratory testing)"
)


# --- The reproduction: these FAIL today ---

def test_annotated_true_flag_is_detected_enabled():
    """The core repro: an annotated `true` line must read as enabled.

    Fails today — `(true|false)\\s*$` rejects the trailing `(optional; …)`
    annotation, so `_detect_etc_flag` returns False (vacuous-pass root cause).
    """
    assert _detect_etc_flag(_ANNOTATED_TRUE) is True, (
        "ETC-1 flag detection rejected an annotated `**Exploratory-charter**: "
        "true  (optional; …)` line — the charter gate passes vacuously on every "
        "brief that keeps the template annotation (R-36)."
    )


def test_audit_brief_with_annotated_true_reports_enabled(tmp_path: Path):
    """End-to-end repro of the real slice-115 scenario via the public file audit.

    A mission-brief carrying the annotated `true` flag must surface as
    `exploratory_charter_enabled is True`. Fails today (reports False → the gate
    silently enforces nothing despite authored charters).
    """
    brief = tmp_path / "mission-brief.md"
    brief.write_text(
        "# Slice 999: demo-charter-slice\n\n"
        f"{_ANNOTATED_TRUE}\n\n"
        "## Exploratory test charter\n\n"
        "| # | Mission | Timebox | Status | Findings |\n"
        "|---|---------|---------|--------|----------|\n"
        "| 1 | Explore X using Y to find Z | 60min | COMPLETED | no issues observed |\n",
        encoding="utf-8",
    )
    result = audit_brief_file(brief)
    assert result.exploratory_charter_enabled is True, (
        "audit_brief_file read an annotated `Exploratory-charter: true` brief as "
        "NOT enabled — the ETC-1 gate passes vacuously (R-36)."
    )


# --- Controls / guards: these PASS today and must keep passing after the fix ---

def test_unannotated_true_flag_still_enabled():
    """Control: the bare `true` form (no annotation) must remain enabled."""
    assert _detect_etc_flag("**Exploratory-charter**: true") is True


def test_annotated_false_flag_is_disabled():
    """Control: an annotated `false` must resolve to disabled (no over-correction)."""
    assert _detect_etc_flag(_ANNOTATED_FALSE) is False


def test_malformed_suffix_value_is_not_a_valid_boolean():
    """Guard: a malformed-suffix value must NOT be accepted as a boolean.

    Pins the fix toward TF-1's lookahead `(true|false)(?=[\\s(]|$)` rather than a
    loose `(true|false).*$` / `\\b.*$` — the latter would silently admit
    `trueish` / `false-positive` as valid booleans (R-7 / TFFL-1 silent-bypass).
    Passes today (current `\\s*$` anchor already rejects these) and must keep
    passing after the fix.
    """
    assert _detect_etc_flag("**Exploratory-charter**: trueish") is False
    assert _detect_etc_flag("**Exploratory-charter**: false-positive") is False


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
