"""Pin slice-079 Fix K (slice-077 m5 — design→code translation gap closure; MAP-ONLY shape).

Slice-077 m5: design.md L181-191 + ADR-070 contractually promised WARN-emission per UNKNOWN sub-reason
but `tools/pulse_worktree_resolver.py` shipped no templates. Fix K adds module-level constant
`_UNKNOWN_REASON_WARN_TEMPLATES: Mapping[str, str]` keyed by the canonical 8 reasons from
`_UNKNOWN_REASONS` tuple. MAP-ONLY per /critique-review B1+M1: NO new public helper, NO new
JSON state-dict field, NO change to CLI text-mode emission. Haiku-side prose consumer reads constant.
"""
from __future__ import annotations

import pytest

from tools.pulse_worktree_resolver import _UNKNOWN_REASONS, _UNKNOWN_REASON_WARN_TEMPLATES


def test_constant_exists_as_mapping_str_to_str() -> None:
    """Fix K: the constant is a Mapping[str, str]."""
    assert isinstance(_UNKNOWN_REASON_WARN_TEMPLATES, dict), (
        "Fix K regression: _UNKNOWN_REASON_WARN_TEMPLATES is not a dict (Mapping)"
    )
    for k, v in _UNKNOWN_REASON_WARN_TEMPLATES.items():
        assert isinstance(k, str), f"Fix K regression: non-str key {k!r}"
        assert isinstance(v, str), f"Fix K regression: non-str value for {k!r}: {v!r}"
        assert v.strip(), f"Fix K regression: empty WARN template for {k!r}"


def test_constant_keys_are_byte_equal_to_unknown_reasons_tuple() -> None:
    """Fix K: keys of _UNKNOWN_REASON_WARN_TEMPLATES == set(_UNKNOWN_REASONS) exactly.

    Empirically verified at /critique time (APED-1 clause-5 grep) + /critique-review confirmation:
    canonical 8 reasons are at `tools/pulse_worktree_resolver.py:77-86`.
    """
    template_keys = set(_UNKNOWN_REASON_WARN_TEMPLATES.keys())
    canonical = set(_UNKNOWN_REASONS)
    assert template_keys == canonical, (
        f"Fix K regression: _UNKNOWN_REASON_WARN_TEMPLATES keys diverged from canonical _UNKNOWN_REASONS. "
        f"Missing from templates: {canonical - template_keys}. "
        f"Extra in templates: {template_keys - canonical}. "
        f"(Pre-fix design.md mis-cited 8 different keys; per /critique-review B1+M1 ACCEPTED-FIXED.)"
    )


@pytest.mark.parametrize("reason", list(_UNKNOWN_REASONS) if _UNKNOWN_REASON_WARN_TEMPLATES else [])
def test_template_covers_canonical_reason(reason: str) -> None:
    """Fix K: every canonical _UNKNOWN_REASONS member has a non-empty WARN template."""
    assert reason in _UNKNOWN_REASON_WARN_TEMPLATES, (
        f"Fix K regression: canonical reason {reason!r} missing from _UNKNOWN_REASON_WARN_TEMPLATES"
    )
    template = _UNKNOWN_REASON_WARN_TEMPLATES[reason]
    assert template, f"Fix K regression: empty WARN template for {reason!r}"
