"""R-7 regression: TF-1 audit silently default-off on an annotated field-line.

Bug (risk-register R-7, open, medium/medium, score 4; recurred N+1 at slice-033):
`tools.test_first_audit._TEST_FIRST_FIELD_RE` (tools/test_first_audit.py:54) is
`$`-anchored: `^\\*\\*Test[-\\s]?first\\*\\*\\s*:\\s*(true|false)\\s*$`.
`_detect_test_first_flag` (L138-144) does `_TEST_FIRST_FIELD_RE.match(line)`,
so a mission-brief field-line carrying a trailing parenthetical annotation —
the idiomatic `/slice` template form `**Test-first**: true  (per TF-1 — ...)` —
fails the `\\s*$` anchor. `run_audit` then takes the L289
`return result  # default-off` path, and `main` prints
"Test-first audit: not enabled (`**Test-first**: true` absent)." with exit 0
on a slice that genuinely declared test-first. The entire TF-1 gate is
silently bypassed; a test-first slice can ship with PENDING/WRITTEN-FAILING
rows because the audit never engaged.

Expected: an annotated `**Test-first**: true` field-line is detected as
test-first ENABLED (so the gate engages). Distinguishing "field absent"
(legitimate default-off) from "field present but annotated" is the fix
slice's job — this test only pins the reproduction.

Actual (pre-fix): the annotated form is read as NOT enabled -> silent
default-off -> audit exits clean.

Fixed by: slice-034-fix-tf1-audit-field-line-regex (candidate name; /slice
will confirm).
Rule reference: TF-1 / R-7.
"""
from tests.methodology.conftest import REPO_ROOT
from tools.test_first_audit import _detect_test_first_flag, audit_brief_file


# The idiomatic /slice mission-brief annotated form that triggers R-7.
_ANNOTATED_FIELD_LINE = (
    "**Test-first**: true  (per TF-1 — failing repro pre-exists; "
    "tests/methodology/test_tf1_field_line_annotation_regression.py)"
)


def test_detect_test_first_flag_honors_trailing_annotation():
    """Root cause: the detector must read an annotated true field-line as enabled.

    `**Test-first**: true  (per TF-1 — ...)` is genuinely test-first.
    Pre-fix this returns False (the `\\s*$` anchor rejects the annotation).
    Rule reference: TF-1 / R-7.
    """
    assert _detect_test_first_flag(_ANNOTATED_FIELD_LINE) is True

    # The bare form must keep working (guards against an over-broad fix that
    # would break the common case).
    assert _detect_test_first_flag("**Test-first**: true") is True
    # A genuinely-absent field stays default-off (legitimate, not a violation).
    assert _detect_test_first_flag("**Mode**: Standard") is False


def test_annotated_brief_does_not_silently_default_off(tmp_path):
    """End-to-end: an annotated, genuinely test-first brief must engage the gate.

    The danger R-7 describes is observable at the audit-result level: a brief
    that declares test-first AND ships a `## Test-first plan` table currently
    yields `test_first_enabled=False` with ZERO violations (silent green) —
    the gate never ran. Expected: the gate engages (`test_first_enabled` True).
    Rule reference: TF-1 / R-7.
    """
    brief = tmp_path / "mission-brief.md"
    brief.write_text(
        "# Slice 999: repro-r7\n"
        "\n"
        f"{_ANNOTATED_FIELD_LINE}\n"
        "\n"
        "## Acceptance criteria\n"
        "\n"
        "1. the annotated field-line is detected as test-first\n"
        "\n"
        "## Test-first plan\n"
        "\n"
        "| AC | Test type | Test path | Test function | Status |\n"
        "|----|-----------|-----------|---------------|--------|\n"
        "| 1 | unit | tests/methodology/test_tf1_field_line_annotation_regression.py "
        "| test_detect_test_first_flag_honors_trailing_annotation | PASSING |\n",
        encoding="utf-8",
    )

    result = audit_brief_file(brief, skip_if_carry_over=False)

    # Pre-fix: enabled is False -> default-off -> the gate silently passes.
    assert result.test_first_enabled is True, (
        "annotated `**Test-first**: true` brief was read as NOT test-first — "
        "TF-1 gate silently bypassed (R-7)"
    )


def test_r7_retired_in_risk_register():
    """AC5: R-7 is escalated to `retired` in the risk register by this slice.

    Durable vault-state regression guard (state-check, per the project's
    "declaration-check vs state-check" lesson): if a future change reopens
    R-7 or drops the slice-034 retirement, this fails.
    Rule reference: TF-1 / TFFL-1 / R-7.
    """
    reg = (REPO_ROOT / "architecture" / "risk-register.md").read_text(
        encoding="utf-8"
    )
    # Isolate the R-7 section (## R-7 ... up to the next "## R-" heading).
    start = reg.index("## R-7 ")
    rest = reg[start + 1 :]
    nxt = rest.find("\n## R-")
    r7 = rest if nxt == -1 else rest[:nxt]
    assert "**Status**: retired" in r7, (
        "R-7 must be **Status**: retired in architecture/risk-register.md"
    )
    assert "slice-034" in r7, (
        "R-7 retirement must cite slice-034 (Retired field + retirement note)"
    )
