"""Tests for tools/_vault_flip.py — the slice-115 vault flip + rollback engine.

Non-vacuous by construction (AP-5): the round-trip seeds the exact shapes the
dual-Critic flagged — a non-slice-folder ``decisions/ADR`` (Critic B1), a CRLF
text file (Critic M-add-2), nested archive folders, and a ``.lock`` sidecar —
and the verify-mutation tests prove ``verify`` reds on a partial / tampered copy
(Critic B3).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tools import _vault_flip


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    arch = repo / "architecture"
    (arch / "decisions").mkdir(parents=True)
    (arch / "slices" / "archive" / "slice-001-foo").mkdir(parents=True)
    # non-slice-folder vault files (Critic B1 — must survive the migrate)
    (arch / "decisions" / "ADR-001-x.md").write_bytes(b"# ADR-001\nbody\n")
    (arch / "risk-register.md").write_bytes(b"# risks\nR-1\n")
    # nested archive content
    (arch / "slices" / "archive" / "slice-001-foo" / "reflection.md").write_bytes(b"# refl\n")
    # CRLF text → must be canonicalized to LF in the external store (Critic M-add-2)
    (arch / "crlf.md").write_bytes(b"line1\r\nline2\r\n")
    # sidecar lock → must NOT migrate
    (arch / "slice-queue.md.lock").write_bytes(b"lock")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")
    return repo


def test_flip_then_rollback_roundtrip(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext-base"

    res = _vault_flip.flip(repo, base=base)
    dest = Path(res["dest"])

    # external store populated + the flip config points at it
    assert dest.is_dir()
    assert _vault_flip.read_config_value(repo) == str(dest)

    # B1: non-slice-folder files survive
    assert (dest / "decisions" / "ADR-001-x.md").read_bytes() == b"# ADR-001\nbody\n"
    assert (dest / "risk-register.md").exists()
    # nested archive survives
    assert (dest / "slices" / "archive" / "slice-001-foo" / "reflection.md").exists()
    # M-add-2: CRLF canonicalized to LF
    assert (dest / "crlf.md").read_bytes() == b"line1\nline2\n"
    # .lock NOT migrated
    assert not (dest / "slice-queue.md.lock").exists()

    # B3: full file-set count equality (excluding the skipped .lock)
    intree = {
        p.relative_to(repo / "architecture").as_posix()
        for p in (repo / "architecture").rglob("*")
        if p.is_file() and p.suffix.lower() != ".lock"
    }
    deste = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    assert intree == deste

    # the skill's git-untrack step (verified here so the test exercises it)
    _git(repo, "rm", "-r", "--cached", "-q", "architecture")
    tracked = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "architecture"],
        capture_output=True, text=True,
    ).stdout.strip()
    assert tracked == ""  # untracked after the flip

    # the skill removes the in-tree orphan after a successful flip
    shutil.rmtree(repo / "architecture")
    assert not (repo / "architecture").exists()

    # rollback restores the in-tree vault + unsets the config
    _vault_flip.rollback(repo)
    assert _vault_flip.read_config_value(repo) is None
    assert (repo / "architecture" / "decisions" / "ADR-001-x.md").exists()
    assert (repo / "architecture" / "crlf.md").read_bytes() == b"line1\nline2\n"


def test_absent_base_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Critic M1: an absent base file ⇒ default ~/.aisdlc (NOT a STOP).
    monkeypatch.setattr(_vault_flip, "_BASE_CONFIG_FILE", str(tmp_path / "nonexistent"))
    assert _vault_flip.resolve_base() == Path(os.path.expanduser("~/.aisdlc"))


def test_present_base_file_is_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bf = tmp_path / "base"
    bf.write_text("/custom/vault/base\n", encoding="utf-8")
    monkeypatch.setattr(_vault_flip, "_BASE_CONFIG_FILE", str(bf))
    assert _vault_flip.resolve_base() == Path("/custom/vault/base")


def test_verify_catches_missing_file(tmp_path: Path) -> None:
    # B3 non-vacuity: a partial copy must red.
    repo = _make_repo(tmp_path)
    res = _vault_flip.flip(repo, base=tmp_path / "ext")
    dest = Path(res["dest"])
    (dest / "risk-register.md").unlink()
    problems = _vault_flip.verify(dest, res["manifest"])
    assert any("risk-register.md" in p for p in problems)


def test_verify_catches_hash_mismatch(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    res = _vault_flip.flip(repo, base=tmp_path / "ext")
    dest = Path(res["dest"])
    (dest / "risk-register.md").write_bytes(b"TAMPERED\n")
    problems = _vault_flip.verify(dest, res["manifest"])
    assert any("HASH MISMATCH" in p for p in problems)


def test_flip_refuses_nonempty_external_store(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    _vault_flip.flip(repo, base=base)
    with pytest.raises(_vault_flip.VaultFlipError):
        _vault_flip.flip(repo, base=base)


def test_external_store_path_is_stable_and_bounded(tmp_path: Path) -> None:
    repo = _make_repo(tmp_path)
    p1 = _vault_flip.external_store_path(repo, base=Path("/b"))
    p2 = _vault_flip.external_store_path(repo, base=Path("/b"))
    assert p1 == p2                       # stable per repo
    assert len(p1.name) == 16             # bounded hash (MAX_PATH-safe)
