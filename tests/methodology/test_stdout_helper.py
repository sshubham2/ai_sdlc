"""Unit tests for tools._stdout.reconfigure_stdout_utf8 (UTF8-STDOUT-1).

Verifies the helper:
- Calls reconfigure on streams that expose it (real sys.stdout / sys.stderr).
- No-ops on streams without reconfigure (StringIO test-capture; pytest capsys).
- Is idempotent under repeat invocation.
- Sets errors="replace" (not "strict").
- Overrides a prior errors="strict" state (per M6 + M-add-3 ACCEPTED-FIXED).
"""

from __future__ import annotations

import io
import sys
from unittest.mock import MagicMock

from tools import _stdout


def test_reconfigure_called_on_real_streams_with_reconfigure(monkeypatch):
    """Real TextIOWrapper streams have `reconfigure`; the helper must call it."""
    fake_stdout = MagicMock(spec=io.TextIOWrapper)
    fake_stdout.encoding = "cp1252"
    fake_stderr = MagicMock(spec=io.TextIOWrapper)
    fake_stderr.encoding = "cp1252"

    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _stdout.reconfigure_stdout_utf8()

    fake_stdout.reconfigure.assert_called_once_with(
        encoding="utf-8", errors="replace"
    )
    fake_stderr.reconfigure.assert_called_once_with(
        encoding="utf-8", errors="replace"
    )


def test_reconfigure_noop_on_streams_without_reconfigure_attribute(monkeypatch):
    """StringIO (test capture) lacks `reconfigure`; helper must no-op cleanly."""
    capture_stdout = io.StringIO()
    capture_stderr = io.StringIO()
    assert not hasattr(capture_stdout, "reconfigure")
    assert not hasattr(capture_stderr, "reconfigure")

    monkeypatch.setattr(sys, "stdout", capture_stdout)
    monkeypatch.setattr(sys, "stderr", capture_stderr)

    _stdout.reconfigure_stdout_utf8()  # Must not raise.


def test_reconfigure_idempotent_under_repeat_invocation(monkeypatch):
    """Calling the helper twice must not raise; second call also reconfigures."""
    fake_stdout = MagicMock(spec=io.TextIOWrapper)
    fake_stdout.encoding = "cp1252"
    fake_stderr = MagicMock(spec=io.TextIOWrapper)
    fake_stderr.encoding = "cp1252"

    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _stdout.reconfigure_stdout_utf8()
    _stdout.reconfigure_stdout_utf8()

    # Per M6 + M-add-3: NO short-circuit — the helper unconditionally
    # reconfigures every call to guarantee errors="replace" post-state.
    assert fake_stdout.reconfigure.call_count == 2
    assert fake_stderr.reconfigure.call_count == 2


def test_reconfigure_sets_errors_replace_not_strict(monkeypatch):
    """The helper MUST pass errors="replace" (not "strict"); slice's value-prop."""
    fake_stdout = MagicMock(spec=io.TextIOWrapper)
    fake_stdout.encoding = "cp1252"
    fake_stderr = MagicMock(spec=io.TextIOWrapper)
    fake_stderr.encoding = "cp1252"

    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _stdout.reconfigure_stdout_utf8()

    for call_args in (
        fake_stdout.reconfigure.call_args,
        fake_stderr.reconfigure.call_args,
    ):
        assert call_args.kwargs.get("errors") == "replace", (
            f"Expected errors='replace', got {call_args.kwargs.get('errors')!r}"
        )
        assert call_args.kwargs.get("errors") != "strict"


def test_reconfigure_overrides_prior_errors_strict_to_errors_replace(monkeypatch):
    """If a prior caller set errors='strict', the helper must override to 'replace'.

    Per M6 + M-add-3 ACCEPTED-FIXED at slice-023: the encoding-only
    short-circuit was REMOVED for exactly this case — a downstream caller
    that reconfigured to UTF-8 with errors='strict' would otherwise leak
    through. The helper must guarantee post-call state.
    """
    fake_stdout = MagicMock(spec=io.TextIOWrapper)
    fake_stdout.encoding = "utf-8"  # Already UTF-8, but errors=strict
    fake_stderr = MagicMock(spec=io.TextIOWrapper)
    fake_stderr.encoding = "utf-8"

    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _stdout.reconfigure_stdout_utf8()

    # Must reconfigure even though encoding already says UTF-8 — to
    # override errors mode.
    fake_stdout.reconfigure.assert_called_once_with(
        encoding="utf-8", errors="replace"
    )
    fake_stderr.reconfigure.assert_called_once_with(
        encoding="utf-8", errors="replace"
    )
