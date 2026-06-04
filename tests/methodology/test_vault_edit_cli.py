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


# ─── slice-097 / ADR-088: rewrite (CAS) + read CLI contract ──────────────
import pathlib  # noqa: E402


def _use_tmp_vault(monkeypatch, tmp_path):
    """Redirect vault_edit's VAULT_ROOT to a tmp dir so functional rewrite/read
    tests operate on controlled files under the (faked) vault root."""
    monkeypatch.setattr(vault_edit, "VAULT_ROOT", tmp_path)


def test_rewrite_happy_path_exit_0(tmp_path: pathlib.Path, monkeypatch) -> None:
    _use_tmp_vault(monkeypatch, tmp_path)
    target = tmp_path / "idx.md"
    target.write_bytes(b"a\nb\n")
    base = tmp_path / "base.bin"; base.write_bytes(b"a\nb\n")
    new = tmp_path / "new.md"; new.write_text("z\na\nb\n", encoding="utf-8")
    rc = vault_edit.main(["rewrite", "--file", "idx.md", "--base-file", str(base), "--content-file", str(new)])
    assert rc == 0
    assert target.read_bytes() == b"z\na\nb\n"


def test_rewrite_conflict_exit_3(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """The on-disk file differs from --base-file → CAS conflict → exit 3 (distinct
    from usage 2), and the target is untouched."""
    _use_tmp_vault(monkeypatch, tmp_path)
    target = tmp_path / "idx.md"
    target.write_bytes(b"CHANGED-BY-PARALLEL-WRITER\n")
    base = tmp_path / "base.bin"; base.write_bytes(b"what I read earlier\n")
    new = tmp_path / "new.md"; new.write_text("my edit\n", encoding="utf-8")
    rc = vault_edit.main(["rewrite", "--file", "idx.md", "--base-file", str(base), "--content-file", str(new)])
    assert rc == 3
    assert "CONFLICT" in capsys.readouterr().err
    assert target.read_bytes() == b"CHANGED-BY-PARALLEL-WRITER\n"


def test_rewrite_eol_preserving_crlf_via_cli(tmp_path: pathlib.Path, monkeypatch) -> None:
    """critique B1 end-to-end: a CRLF target + an LF base of the same content →
    exit 0 (EOL-normalized compare), and the rewrite keeps the file CRLF."""
    _use_tmp_vault(monkeypatch, tmp_path)
    target = tmp_path / "idx.md"
    target.write_bytes(b"a\r\nb\r\n")  # CRLF on disk
    base = tmp_path / "base.bin"; base.write_bytes(b"a\nb\n")  # LF base
    new = tmp_path / "new.md"; new.write_text("z\na\nb\n", encoding="utf-8")
    rc = vault_edit.main(["rewrite", "--file", "idx.md", "--base-file", str(base), "--content-file", str(new)])
    assert rc == 0
    assert target.read_bytes() == b"z\r\na\r\nb\r\n", "EOL not preserved (B1 churn)"


def test_rewrite_missing_base_file_exit_2(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "idx.md").write_bytes(b"x\n")
    new = tmp_path / "new.md"; new.write_text("y\n", encoding="utf-8")
    rc = vault_edit.main(["rewrite", "--file", "idx.md", "--base-file", str(tmp_path / "nope.bin"), "--content-file", str(new)])
    assert rc == 2
    assert "base-file" in capsys.readouterr().err


def test_read_emits_raw_bytes(tmp_path: pathlib.Path, monkeypatch, capsysbinary) -> None:
    """read emits the target's RAW bytes (CRLF preserved) — the byte-exact CAS base."""
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "idx.md").write_bytes(b"a\r\nb\r\n")
    rc = vault_edit.main(["read", "--file", "idx.md"])
    assert rc == 0
    assert capsysbinary.readouterr().out == b"a\r\nb\r\n"


def test_read_missing_file_emits_empty(tmp_path: pathlib.Path, monkeypatch, capsysbinary) -> None:
    """read of an absent target emits nothing + exit 0 (the create-case base)."""
    _use_tmp_vault(monkeypatch, tmp_path)
    rc = vault_edit.main(["read", "--file", "absent.md"])
    assert rc == 0
    assert capsysbinary.readouterr().out == b""


# ─── slice-097 /code-review B1: read --out-file (byte-safe, no shell `>`) ──


def test_read_out_file_writes_byte_exact(tmp_path: pathlib.Path, monkeypatch) -> None:
    """B1: `read --out-file` writes the raw bytes via Python — byte-exact to the
    on-disk file, immune to the PowerShell `>`/Out-File UTF-16LE+BOM corruption the
    documented protocol now avoids."""
    _use_tmp_vault(monkeypatch, tmp_path)
    # CRLF + a UTF-8 multibyte char (em-dash) — exactly what PowerShell `>` would mangle
    (tmp_path / "idx.md").write_bytes("a\r\nb — em\r\n".encode("utf-8"))
    src = (tmp_path / "idx.md").read_bytes()
    out = tmp_path / "base.bin"
    rc = vault_edit.main(["read", "--file", "idx.md", "--out-file", str(out)])
    assert rc == 0
    assert out.read_bytes() == src, "--out-file base not byte-exact to the source"


def test_read_out_file_roundtrips_into_rewrite(tmp_path: pathlib.Path, monkeypatch) -> None:
    """B1 end-to-end: the DOCUMENTED protocol (read --out-file → rewrite --base-file)
    succeeds byte-exactly with NO false-conflict — the failure the prior `> base.bin`
    prose guaranteed under PowerShell."""
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "idx.md").write_bytes(b"x\r\ny\r\n")
    base = tmp_path / "base.bin"
    assert vault_edit.main(["read", "--file", "idx.md", "--out-file", str(base)]) == 0
    new = tmp_path / "new.md"; new.write_text("z\nx\ny\n", encoding="utf-8")
    rc = vault_edit.main(["rewrite", "--file", "idx.md", "--base-file", str(base), "--content-file", str(new)])
    assert rc == 0, "documented read --out-file → rewrite protocol false-conflicted"
    assert (tmp_path / "idx.md").read_bytes() == b"z\r\nx\r\ny\r\n"


# ─── slice-111 / ADR-103: move (seam-routed archive mv) CLI contract ──────


def _seed_slice(tmp_path: pathlib.Path, name: str) -> pathlib.Path:
    d = tmp_path / "slices" / name
    d.mkdir(parents=True)
    (d / "reflection.md").write_text("done\n", encoding="utf-8")
    (tmp_path / "slices" / "archive").mkdir(parents=True, exist_ok=True)
    return d


def test_move_into_existing_archive_dir_exit_0(tmp_path: pathlib.Path, monkeypatch) -> None:
    """M2: the archive idiom `move --from slices/slice-X --to slices/archive/`
    SUCCEEDS even though `slices/archive/` already exists — the dest-exists guard
    checks the FINAL landing path `<--to>/<src-name>`, not the `--to` directory."""
    _use_tmp_vault(monkeypatch, tmp_path)
    src = _seed_slice(tmp_path, "slice-042-foo")
    rc = vault_edit.main(["move", "--from", "slices/slice-042-foo", "--to", "slices/archive/"])
    assert rc == 0
    landed = tmp_path / "slices" / "archive" / "slice-042-foo"
    assert landed.is_dir() and (landed / "reflection.md").exists()
    assert not src.exists(), "source not removed after move"


def test_move_refuses_pre_existing_landing_exit_2(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """A pre-existing landing path `slices/archive/<same-name>` → exit 2 (preserves
    the /archive Step-2 'stop if already archived' semantic); source untouched."""
    _use_tmp_vault(monkeypatch, tmp_path)
    src = _seed_slice(tmp_path, "slice-042-foo")
    (tmp_path / "slices" / "archive" / "slice-042-foo").mkdir(parents=True)
    rc = vault_edit.main(["move", "--from", "slices/slice-042-foo", "--to", "slices/archive/"])
    assert rc == 2
    assert "already exists" in capsys.readouterr().err
    assert src.exists(), "source must be untouched on a refused move"


def test_move_missing_source_exit_2(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """A missing --from source → fail-VISIBLE exit 2 (R-7; also the post-flip
    worktree-local-source-under-external-root R-32.b loud failure)."""
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "slices" / "archive").mkdir(parents=True)
    rc = vault_edit.main(["move", "--from", "slices/slice-999-absent", "--to", "slices/archive/"])
    assert rc == 2
    assert "does not exist" in capsys.readouterr().err


@pytest.mark.parametrize("escape", ["../outside", "../../etc"])
def test_move_rejects_outside_root_from(tmp_path: pathlib.Path, monkeypatch, capsys, escape: str) -> None:
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "slices" / "archive").mkdir(parents=True)
    rc = vault_edit.main(["move", "--from", escape, "--to", "slices/archive/"])
    assert rc == 2
    assert "outside the vault root" in capsys.readouterr().err


def test_move_rejects_outside_root_to(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    _use_tmp_vault(monkeypatch, tmp_path)
    _seed_slice(tmp_path, "slice-042-foo")
    rc = vault_edit.main(["move", "--from", "slices/slice-042-foo", "--to", "../outside/"])
    assert rc == 2
    assert "outside the vault root" in capsys.readouterr().err


def test_move_to_nonexistent_path_renames_exit_0(tmp_path: pathlib.Path, monkeypatch) -> None:
    """When --to does NOT exist, shutil.move renames the source TO it (the dst-not-dir
    branch); the guard then checks --to itself as the landing."""
    _use_tmp_vault(monkeypatch, tmp_path)
    src = _seed_slice(tmp_path, "slice-042-foo")
    rc = vault_edit.main(["move", "--from", "slices/slice-042-foo", "--to", "slices/renamed-bar"])
    assert rc == 0
    assert (tmp_path / "slices" / "renamed-bar" / "reflection.md").exists()
    assert not src.exists()


def test_move_same_path_exit_2(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """m3 (code-review): `move --from X --to X` (same resolved path) → exit 2, not a
    silent exit-0 no-op."""
    _use_tmp_vault(monkeypatch, tmp_path)
    _seed_slice(tmp_path, "slice-042-foo")
    rc = vault_edit.main(["move", "--from", "slices/slice-042-foo", "--to", "slices/slice-042-foo"])
    assert rc == 2
    assert "same path" in capsys.readouterr().err


def test_move_error_names_from_not_file_arg(tmp_path: pathlib.Path, monkeypatch, capsys) -> None:
    """m2 (code-review): a `move --from` failure names `--from`, NOT the hardcoded
    `--file` (which would mislead — the user passed --from)."""
    _use_tmp_vault(monkeypatch, tmp_path)
    (tmp_path / "slices" / "archive").mkdir(parents=True)
    rc = vault_edit.main(["move", "--from", "../escape", "--to", "slices/archive/"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "--from" in err and "--file" not in err
