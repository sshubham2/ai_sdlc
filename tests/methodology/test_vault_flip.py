"""Tests for tools/_vault_flip.py — the slice-115 vault flip + rollback engine.

Non-vacuous by construction (AP-5): the round-trip seeds the exact shapes the
dual-Critic flagged — a non-slice-folder ``decisions/ADR`` (Critic B1), a CRLF
text file (Critic M-add-2), nested archive folders, and a ``.lock`` sidecar —
and the verify-mutation tests prove ``verify`` reds on a partial / tampered copy
(Critic B3).
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools import _vault_flip


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def _make_repo(tmp_path: Path, repo_dir: Path | None = None) -> Path:
    repo = repo_dir if repo_dir is not None else tmp_path / "repo"
    repo.mkdir(parents=True)
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
    assert p1 == p2                                       # stable per repo
    assert re.fullmatch(r"repo-[0-9a-f]{8}", p1.name)     # <slug>-<8hex> (ADR-109; was len==16)
    assert len(p1.name) <= _vault_flip._MAX_SLUG_LEN + 1 + 8   # bounded (MAX_PATH-safe)


# ── slice-118 naming scheme + rename_store (ADR-109) ──────────────────────────

def _seed_store(d: Path) -> None:
    """Populate a minimal vault store: a top-level file + a nested file."""
    (d / "slices").mkdir(parents=True, exist_ok=True)
    (d / "risk-register.md").write_bytes(b"# risks\nR-1\n")
    (d / "slices" / "x.md").write_bytes(b"# x\n")


def test_store_path_is_project_name_plus_shorthash(tmp_path: Path) -> None:
    # AC1: <base>/<project-slug>-<shorthash>
    repo = _make_repo(tmp_path)
    p = _vault_flip.external_store_path(repo, base=Path("/b"))
    assert p.parent == Path("/b")
    assert re.fullmatch(r"repo-[0-9a-f]{8}", p.name)


def test_store_path_collision_safe_same_basename(tmp_path: Path) -> None:
    # AC1: two repos with the SAME basename but distinct common-dirs → distinct stores
    r1 = _make_repo(tmp_path, repo_dir=tmp_path / "p1" / "repo")
    r2 = _make_repo(tmp_path, repo_dir=tmp_path / "p2" / "repo")
    n1 = _vault_flip.external_store_path(r1, base=Path("/b")).name
    n2 = _vault_flip.external_store_path(r2, base=Path("/b")).name
    assert n1.startswith("repo-") and n2.startswith("repo-")
    assert n1 != n2                                       # distinct shorthash → no clash


def test_store_path_stable_across_worktrees(tmp_path: Path) -> None:
    # AC1: every worktree of a repo resolves to the SAME store (shared common-dir)
    repo = _make_repo(tmp_path)
    wt = tmp_path / "wt"
    _git(repo, "worktree", "add", "-q", "-b", "br", str(wt))
    assert _vault_flip.external_store_path(repo, base=Path("/b")) == \
        _vault_flip.external_store_path(wt, base=Path("/b"))


def test_store_path_sanitizes_unsafe_project_name(tmp_path: Path) -> None:
    # AC1 / Critic m2: unit-test _project_slug DIRECTLY on adversarial input
    # (NOT via _make_repo, whose repo dir "repo" is already safe → vacuous, AP-5).
    slug = _vault_flip._project_slug(str(Path("/x/My Project!") / ".git"))
    assert slug == "My-Project"                           # space + '!' folded, case preserved
    assert re.fullmatch(r"[A-Za-z0-9._-]+", slug)
    assert slug != "My Project!"                          # folding actually happened
    assert re.fullmatch(r"[A-Za-z0-9._-]+",
                        _vault_flip._project_slug(str(Path("/x/café") / ".git")))  # non-ASCII folded
    assert _vault_flip._project_slug(str(Path("/") / ".git")) == "vault"  # empty → fallback


def test_rename_store_moves_and_rewrites_config(tmp_path: Path) -> None:
    # AC2: legacy hash-named store → new identifiable name + config repoint + old removed
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    _vault_flip.write_config(repo, old)
    new = _vault_flip.external_store_path(repo, base=base)
    res = _vault_flip.rename_store(repo, base=base)
    assert res["renamed"] is True and res["resumed"] is False
    assert Path(_vault_flip.read_config_value(repo)) == new
    assert (new / "risk-register.md").read_bytes() == b"# risks\nR-1\n"
    assert (new / "slices" / "x.md").exists()
    assert not old.exists()


def test_rename_store_verifies_and_rolls_back_on_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # AC2: a post-migrate verify failure → partial `new` cleaned up, config UNCHANGED
    # (still resolves to the intact source). Force verify to report a problem.
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    _vault_flip.write_config(repo, old)
    new = _vault_flip.external_store_path(repo, base=base)
    monkeypatch.setattr(_vault_flip, "verify", lambda dest, manifest: ["HASH MISMATCH: x"])
    with pytest.raises(_vault_flip.VaultFlipError):
        _vault_flip.rename_store(repo, base=base)
    assert not new.exists()                                   # partial new rolled back
    assert Path(_vault_flip.read_config_value(repo)) == old   # config untouched
    assert (old / "risk-register.md").exists()                # source intact


def test_rename_store_is_idempotent(tmp_path: Path) -> None:
    # AC2: a freshly-flipped repo already lands at the new name → rename is a no-op
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    dest = Path(_vault_flip.flip(repo, base=base)["dest"])
    res = _vault_flip.rename_store(repo, base=base)
    assert res["renamed"] is False
    assert Path(_vault_flip.read_config_value(repo)) == dest
    assert _vault_flip.rename_store(repo, base=base)["renamed"] is False   # re-run still no-op


def test_rename_store_refuses_missing_current(tmp_path: Path) -> None:
    # AC2 / meta M-add-1: config → non-existent dir must refuse, NOT silently repoint
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    missing = base / "doesnotexist"
    _vault_flip.write_config(repo, missing)
    with pytest.raises(_vault_flip.VaultFlipError):
        _vault_flip.rename_store(repo, base=base)
    assert Path(_vault_flip.read_config_value(repo)) == missing       # config UNCHANGED
    assert not _vault_flip.external_store_path(repo, base=base).exists()  # no empty store created


def test_rename_store_resumes_complete_new(tmp_path: Path) -> None:
    # AC2 / M2: a COMPLETE verified copy already at new (interrupted rename) → RESUME
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    new = _vault_flip.external_store_path(repo, base=base)
    _vault_flip.migrate(old, new)                         # complete copy already present
    _vault_flip.write_config(repo, old)
    res = _vault_flip.rename_store(repo, base=base)
    assert res["renamed"] is True and res["resumed"] is True
    assert Path(_vault_flip.read_config_value(repo)) == new
    assert not old.exists() and (new / "risk-register.md").exists()


def test_rename_store_redoes_partial_new(tmp_path: Path) -> None:
    # AC2 / M2: an OUR-partial new (MISSING-only) → delete + redo (not resume)
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    new = _vault_flip.external_store_path(repo, base=base)
    (new / "slices").mkdir(parents=True)
    (new / "slices" / "x.md").write_bytes(b"# x\n")       # subset of old, correct hash
    _vault_flip.write_config(repo, old)
    res = _vault_flip.rename_store(repo, base=base)
    assert res["renamed"] is True and res["resumed"] is False
    assert (new / "risk-register.md").exists() and not old.exists()


def test_rename_store_refuses_foreign_new(tmp_path: Path) -> None:
    # AC2 / M2: foreign content at new (UNEXPECTED) → refuse, do NOT delete, config untouched
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    new = _vault_flip.external_store_path(repo, base=base)
    new.mkdir(parents=True)
    (new / "foreign.md").write_bytes(b"# not ours\n")
    _vault_flip.write_config(repo, old)
    with pytest.raises(_vault_flip.VaultFlipError):
        _vault_flip.rename_store(repo, base=base)
    assert (new / "foreign.md").exists()                  # foreign dir NOT destroyed
    assert Path(_vault_flip.read_config_value(repo)) == old   # config UNCHANGED


def test_rename_store_refuses_truncated_partial(tmp_path: Path) -> None:
    # code-review M2: a truncated final-file (HASH MISMATCH, not MISSING) from an
    # interrupt mid-`write_bytes` is NOT a positively-identified clean partial →
    # REFUSED (conservative), not redone. Pins the honest 3-way contract.
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    new = _vault_flip.external_store_path(repo, base=base)
    (new / "slices").mkdir(parents=True)
    (new / "risk-register.md").write_bytes(b"# risks\nR-1\n")    # complete + correct
    (new / "slices" / "x.md").write_bytes(b"# truncat")          # truncated → HASH MISMATCH
    _vault_flip.write_config(repo, old)
    with pytest.raises(_vault_flip.VaultFlipError):
        _vault_flip.rename_store(repo, base=base)
    assert (new / "slices" / "x.md").exists()                    # refused, NOT deleted
    assert Path(_vault_flip.read_config_value(repo)) == old       # config unchanged


def test_resolution_unbroken_after_rename(tmp_path: Path) -> None:
    # AC3 / M1: resolve via a FRESH subprocess (in-process VAULT_ROOT is frozen-at-import)
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    _vault_flip.write_config(repo, old)
    pre = _vault_flip._manifest_of(old)
    new = _vault_flip.external_store_path(repo, base=base)
    _vault_flip.rename_store(repo, base=base)
    repo_root = Path(_vault_flip.__file__).resolve().parents[1]   # dir containing tools/
    env = {k: v for k, v in os.environ.items() if k != "AI_SDLC_VAULT_ROOT"}
    env["PYTHONPATH"] = str(repo_root) + os.pathsep + env.get("PYTHONPATH", "")
    cp = subprocess.run([sys.executable, "-m", "tools._vault_paths"],
                        cwd=repo, env=env, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    line = [l for l in cp.stdout.splitlines() if l.startswith("vault-root:")]
    assert line, cp.stdout
    assert Path(line[0].split("vault-root:")[1].strip()) == new
    assert _vault_flip._manifest_of(new) == pre           # zero data loss


def test_unmigrated_hash_store_still_resolves(tmp_path: Path) -> None:
    # AC3: an un-renamed legacy store keeps resolving via the config's absolute path
    repo = _make_repo(tmp_path)
    base = tmp_path / "ext"
    old = base / "legacy0123456789abcd"
    _seed_store(old)
    _vault_flip.write_config(repo, old)
    assert Path(_vault_flip.read_config_value(repo)) == old   # not renamed → config unchanged
    assert old.is_dir() and (old / "risk-register.md").exists()
