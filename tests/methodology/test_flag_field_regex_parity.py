r"""Cross-flag parity for the three opt-in mission-brief flag-detection regexes.

Slice-116 (R-36 fix-the-class). The mission-brief template carries three opt-in
boolean flags, each detected by its own audit's value-regex:

    `**Test-first**: <bool>`        -> tools.test_first_audit._TEST_FIRST_FIELD_RE
    `**Walking-skeleton**: <bool>`  -> tools.walking_skeleton_audit._WS_FIELD_RE
    `**Exploratory-charter**: <bool>` -> tools.exploratory_charter_audit._ETC_FIELD_RE

All three must behave IDENTICALLY on the idiomatic annotated form the template
emits (`true  (optional; per X — …)`) AND on malformed-suffix values
(`trueish` / `false-positive`). Pre-slice-116 only TF-1 was correct
(`(true|false)(?=[\s(]|$)` lookahead); WS-1 + ETC-1 used `(true|false)\s*$`,
silently rejecting the annotation -> vacuous gate pass (R-36 + its WS-1 sibling).

This parity test pins BOTH poles for ALL THREE audits (per /critique m2): the
positive (annotated-`true` accepted) AND the negative (malformed-suffix
rejected). The negative pole is the load-bearing guard — a future loosening of
any one audit to `(true|false).*$` would pass an annotated-true-only test while
re-opening the R-7 / TFFL-1 silent-bypass; here it trips
`test_flag_audit_rejects_malformed_suffix` for that audit.

The annotated-`true` cases FAIL pre-fix for WS-1 + ETC-1 (TF-1 already green);
all cases pass post-fix. Rule references: TF-1, WS-1, ETC-1; ADR-034 (TFFL-1).
"""
from __future__ import annotations

import pytest

from tools.exploratory_charter_audit import _ETC_FIELD_RE
from tools.test_first_audit import _TEST_FIRST_FIELD_RE
from tools.walking_skeleton_audit import _WS_FIELD_RE

# (label, value-regex, mission-brief field name)
_FLAG_AUDITS = [
    ("TF-1", _TEST_FIRST_FIELD_RE, "Test-first"),
    ("WS-1", _WS_FIELD_RE, "Walking-skeleton"),
    ("ETC-1", _ETC_FIELD_RE, "Exploratory-charter"),
]
_IDS = [a[0] for a in _FLAG_AUDITS]

# Malformed values that must NEVER parse as a valid boolean (R-7 / TFFL-1): a
# real boolean followed by a non-`[\s(]` suffix, plus a non-boolean word.
_MALFORMED_SUFFIX = ["trueish", "false-positive", "true.", "true; note", "maybe"]


@pytest.mark.parametrize("label,regex,field", _FLAG_AUDITS, ids=_IDS)
def test_flag_audit_accepts_annotated_true(label, regex, field):
    """Positive pole: every audit accepts the template's annotated-`true` form."""
    line = f"**{field}**: true  (optional; per {label} — annotation)"
    m = regex.match(line)
    assert m is not None, (
        f"{label} value-regex rejected an annotated `**{field}**: true  (…)` line — "
        "the gate would pass vacuously (R-36 class)."
    )
    assert m.group(1).lower() == "true"


@pytest.mark.parametrize("label,regex,field", _FLAG_AUDITS, ids=_IDS)
def test_flag_audit_accepts_bare_true(label, regex, field):
    """Control: the bare (un-annotated) `true` form stays accepted for all three."""
    m = regex.match(f"**{field}**: true")
    assert m is not None and m.group(1).lower() == "true"


@pytest.mark.parametrize("label,regex,field", _FLAG_AUDITS, ids=_IDS)
@pytest.mark.parametrize("bad", _MALFORMED_SUFFIX)
def test_flag_audit_rejects_malformed_suffix(label, regex, field, bad):
    """Negative pole (load-bearing guard): no audit accepts a malformed value.

    A future loosening of any one audit to `(true|false).*$` would trip this.
    """
    assert regex.match(f"**{field}**: {bad}") is None, (
        f"{label} value-regex accepted malformed `{bad}` as a boolean — "
        "R-7 / TFFL-1 silent-bypass re-opened."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
