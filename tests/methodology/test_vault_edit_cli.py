"""vault_edit CLI contract — path containment + m3 vault-root/empty rejection
(slice-095 / [[ADR-087]] code-review hardening).

m3 (code-review): ``--file .`` / ``--file ""`` (the vault-root directory itself)
is now an INTENTIONAL ``ValueError`` → exit 2 with an actionable message, not an
incidental ``IsADirectoryError`` surfacing downstream. The path-escape vectors
(``..``-escape, absolute) that the code-Critic verified by execution are pinned
here too — they previously had no committed regression test.
"""
from __future__ import annotations

import pytest

from tools import _stdout

_stdout.reconfigure_stdout_utf8()

from tools import vault_edit  # noqa: E402
from tools._vault_paths import VAULT_ROOT  # noqa: E402


# ─── m3: the vault-root directory itself / an empty --file is rejected ───


@pytest.mark.parametrize("bad", [".", "", "   "])
def test_resolve_rejects_vault_root_or_empty(bad: str) -> None:
    """`--file .` / `--file ""` / whitespace resolve to (or below) the vault root
    directory itself — rejected intentionally, not via a downstream error."""
    with pytest.raises(ValueError):
        vault_edit._resolve_in_vault(bad)


def test_main_exit_two_on_dot_file(capsys: pytest.CaptureFixture) -> None:
    """`--file .` → exit 2 with an actionable 'vault root' message before any
    content is read (no stack trace, no IsADirectoryError)."""
    rc = vault_edit.main(["append", "--file", ".", "--stdin"])
    assert rc == 2
    assert "vault root" in capsys.readouterr().err


# ─── containment: escapes rejected; a normal in-vault file resolves ──────


@pytest.mark.parametrize("escape", ["../outside.md", "../../etc/passwd"])
def test_resolve_rejects_parent_escape(escape: str) -> None:
    with pytest.raises(ValueError):
        vault_edit._resolve_in_vault(escape)


def test_resolve_accepts_in_vault_file() -> None:
    target = vault_edit._resolve_in_vault("risk-register.md")
    assert target.parent == VAULT_ROOT.resolve()
    assert target.name == "risk-register.md"


def test_resolve_accepts_nested_in_vault_file() -> None:
    target = vault_edit._resolve_in_vault("slices/_index.md")
    assert VAULT_ROOT.resolve() in target.parents
