"""Vault flip + rollback engine (slice-115 / [[ADR-107]]).

The one-time migration that relocates this repo's in-tree ``architecture/``
vault to the external shared store ``~/.aisdlc/<project>/`` and writes the
per-project git-common-dir config that points ``VAULT_ROOT`` there. Provides a
scripted inverse (``rollback``) so the flip's reversibility is *tested*, not
asserted (the slice-115 must-not-defer).

Decisions it embodies (ADR-107, settled at /design-slice + the dual-Critic
pass):

- **Option A — whole vault external**: the entire ``architecture/`` tree moves;
  ``vault_edit move`` then resolves both archive endpoints under one external
  ``VAULT_ROOT`` (R-32.b dissolves).
- **Plain external directory** (no independent git history).
- **LF-normalize text on migrate** (Critic M-add-2): the external store is a
  plain dir with NO ``.gitattributes`` renormalization layer, and only
  ``architecture/slice-queue.md`` was in-tree EOL-pinned. Under
  ``core.autocrlf`` the in-tree working copy may carry CRLF; a raw byte copy
  would freeze CRLF into the store forever. Normalizing ``.md``/``.txt`` to
  canonical LF on write keeps the external store uniformly LF — matching the
  EOL-agnostic comparators (ADR-033), the ``_vault_write`` LF writers
  (slice-094), and re-homing ADR-098's ``slice-queue.md`` byte-identity
  precondition.
- **Full-manifest verify before any delete** (Critic B3): ``flip`` migrates
  (copy — source untouched) then verifies the COMPLETE file set (count
  equality + per-file SHA-256), and RAISES on any mismatch. The caller deletes
  the in-tree copy only after ``flip`` returns success. At no point is the
  vault's only copy in flight (the slice-115 Invariant).

Separation of concerns: this module owns the *filesystem* migration + the
config + the inverse. The *git* operations (``git rm -r --cached architecture/``
+ ``.gitignore`` + commit + orphan removal) are driven by the ``/build-slice``
prose so they stay visible in build-log.md. ``flip`` NEVER deletes the source
and NEVER touches git.

Underscore-prefixed (``_vault_flip``) like ``_vault_paths`` / ``_vault_write`` /
``_vault_git`` / ``_worktree_paths`` — a shared internal helper, auto-excluded
from PMI-1 inventory (no ``plugin.yaml`` / ``install_audit`` count). Stdlib leaf
beyond ``_stdout`` (+ ``_vault_paths._CONFIG_REL`` and ``_vault_write`` for the
config write, the established slice-093 pattern).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from tools import _stdout
from tools._vault_paths import _CONFIG_REL  # single source of truth for "aisdlc/vault-root"
from tools._vault_write import safe_write_text

_BASE_CONFIG_FILE = "~/.claude/ai-sdlc-vault-base"
_DEFAULT_BASE = "~/.aisdlc"
_TEXT_SUFFIXES = frozenset({".md", ".txt"})
# Untracked per-process sidecar locks (_vault_write) live IN architecture/ on
# disk but are NOT vault content — never migrate them.
_SKIP_SUFFIXES = frozenset({".lock"})
_VAULT_DIRNAME = "architecture"


class VaultFlipError(RuntimeError):
    """Raised on a fail-visible flip/rollback error (R-7 class — never silent)."""


# ── path resolution ───────────────────────────────────────────────────────────

def resolve_base() -> Path:
    """The external-store BASE directory.

    Reads ``~/.claude/ai-sdlc-vault-base`` (ADR-085 §Install enhancement). An
    ABSENT or empty file is the NORMAL path → default ``~/.aisdlc`` (Critic M1 —
    NOT a STOP; the default is the documented value). STOP-on-unwritable is the
    caller's C3 concern, not this resolver's.
    """
    cfg = Path(os.path.expanduser(_BASE_CONFIG_FILE))
    try:
        text = cfg.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        text = ""
    return Path(os.path.expanduser(text or _DEFAULT_BASE))


def _common_dir(repo_root: Path) -> str:
    """Canonicalized absolute git-common-dir string (the hash seed; ADR-085 C1).

    Always ``--path-format=absolute --git-common-dir`` (never bare). Captured as
    BYTES + decoded in the main thread (AP-7 — a reader-thread decode of a
    non-UTF-8 path would raise an uncaught ``UnicodeDecodeError``).
    """
    try:
        cp = subprocess.run(
            ["git", "-C", str(repo_root),
             "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VaultFlipError(f"git-common-dir unresolvable: {exc}") from exc
    if cp.returncode != 0:
        raise VaultFlipError(
            "git-common-dir unresolvable (not a git work tree?): "
            + cp.stderr.decode("utf-8", "replace").strip()
        )
    raw = cp.stdout.decode("utf-8").strip()
    if not raw:
        raise VaultFlipError("git-common-dir returned empty output")
    # Canonical form: resolve symlinks + normcase (Windows case-insensitive) so
    # the hash is stable across equivalent path spellings.
    return os.path.normcase(str(Path(raw).resolve()))


_MAX_SLUG_LEN = 48


def _project_slug(canonical_common_dir: str) -> str:
    """Human-readable, filesystem-safe slug = the repo-root dir basename (the
    parent of the git-common-dir), sanitized. Derived from the SAME canonical
    (resolved + ``normcase``-d) common-dir string the shorthash uses, so it is
    deterministic + identical across every worktree of a repo ([[ADR-109]]).

    On case-insensitive filesystems the input is already ``normcase``-lowered
    (by ``_common_dir``), so the slug folds to lowercase there — by design, so a
    case-variant path spelling maps to ONE store (worktree/idempotency
    stability). Non-``[A-Za-z0-9._-]`` runs fold to ``-``; bounded to
    ``_MAX_SLUG_LEN``; an empty result falls back to ``"vault"``.
    """
    raw = Path(canonical_common_dir).parent.name
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-.")[:_MAX_SLUG_LEN].strip("-.")
    return slug or "vault"


def external_store_path(repo_root: Path, base: Path | None = None) -> Path:
    """``<base>/<project-slug>-<shorthash>`` — the per-project external vault dir
    (ADR-085 §C1 keying, naming amended by [[ADR-109]]).

    ``<project-slug>`` = sanitized repo-root basename (`_project_slug`);
    ``<shorthash>`` = first 8 hex of ``sha256(canonical common-dir)``. Human-
    identifiable AND collision-resistant + per-repo-stable + shared across all
    worktrees of a repo (the common-dir seed is shared) + MAX_PATH-safe
    (≤``_MAX_SLUG_LEN``-char slug + 9). Both segments derive from the ONE
    canonical common-dir string, so the whole name is deterministic.
    """
    base = base or resolve_base()
    cc = _common_dir(repo_root)
    short = hashlib.sha256(cc.encode("utf-8")).hexdigest()[:8]
    return base / f"{_project_slug(cc)}-{short}"


# ── migration ─────────────────────────────────────────────────────────────────

def _lf(data: bytes) -> bytes:
    """CRLF → LF canonicalization (text only). Lone CR is left as-is (the vault
    is LF or CRLF, never classic-Mac CR)."""
    return data.replace(b"\r\n", b"\n")


def _iter_files(root: Path):
    """Yield every migratable file under ``root`` (skips ``.lock`` sidecars)."""
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() not in _SKIP_SUFFIXES:
            yield p


def _content_for(path: Path) -> bytes:
    """The bytes to write at the destination: LF-normalized for text, byte-exact
    otherwise."""
    raw = path.read_bytes()
    return _lf(raw) if path.suffix.lower() in _TEXT_SUFFIXES else raw


def migrate(src: Path, dest: Path) -> dict[str, str]:
    """Copy every file under ``src`` to ``dest`` (text LF-normalized), returning a
    manifest ``{posix-relpath: sha256(written-bytes)}``.

    NEVER deletes ``src`` (the copy-then-verify-then-delete invariant — the
    caller deletes the source only after ``verify`` passes).
    """
    src = Path(src)
    dest = Path(dest)
    manifest: dict[str, str] = {}
    for f in _iter_files(src):
        rel = f.relative_to(src).as_posix()
        content = _content_for(f)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        manifest[rel] = hashlib.sha256(content).hexdigest()
    return manifest


def _manifest_of(src: Path) -> dict[str, str]:
    """The manifest ``migrate`` WOULD produce for ``src`` — ``{posix-relpath:
    sha256(written-bytes)}`` — computed WITHOUT writing (text LF-normalized,
    ``.lock`` skipped, exactly as ``migrate``). Lets ``rename_store`` re-``verify``
    a pre-existing destination against the source to classify it
    (resume / our-partial / foreign)."""
    src = Path(src)
    return {
        f.relative_to(src).as_posix(): hashlib.sha256(_content_for(f)).hexdigest()
        for f in _iter_files(src)
    }


def verify(dest: Path, manifest: dict[str, str]) -> list[str]:
    """Full-manifest verify (Critic B3): the destination file SET must equal the
    manifest keys (count + names) AND each destination file's SHA-256 must match.

    Returns the list of mismatch descriptions (empty == clean). NOT a sample.
    """
    dest = Path(dest)
    actual = {p.relative_to(dest).as_posix() for p in _iter_files(dest)}
    expected = set(manifest)
    problems: list[str] = []
    for missing in sorted(expected - actual):
        problems.append(f"MISSING at dest: {missing}")
    for extra in sorted(actual - expected):
        problems.append(f"UNEXPECTED at dest: {extra}")
    for rel in sorted(expected & actual):
        got = hashlib.sha256((dest / rel).read_bytes()).hexdigest()
        if got != manifest[rel]:
            problems.append(f"HASH MISMATCH: {rel} ({got} != {manifest[rel]})")
    return problems


# ── config (the flip signal) ──────────────────────────────────────────────────

def _config_path(repo_root: Path) -> Path:
    return Path(_common_dir(repo_root)) / _CONFIG_REL


def read_config_value(repo_root: Path) -> str | None:
    cfg = _config_path(repo_root)
    try:
        text = cfg.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return None
    return text or None


def write_config(repo_root: Path, dest_abs: Path) -> Path:
    """Write ``<common-dir>/aisdlc/vault-root`` = the absolute external path. This
    is the flip SIGNAL — once written, ``VAULT_ROOT`` resolves external in BOTH
    the main tree and every worktree (the common-dir is shared)."""
    cfg = _config_path(repo_root)
    cfg.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(cfg, str(dest_abs) + "\n")
    return cfg


def remove_config(repo_root: Path) -> None:
    cfg = _config_path(repo_root)
    try:
        cfg.unlink()
    except FileNotFoundError:
        pass


# ── orchestration ─────────────────────────────────────────────────────────────

def flip(repo_root: Path, *, base: Path | None = None) -> dict:
    """Migrate the in-tree vault to the external store + write the flip config.

    Sequence (NEVER deletes the source, NEVER touches git): compute dest →
    refuse a non-empty dest → migrate (copy, LF-normalize text) → FULL-manifest
    verify (RAISE on any mismatch — config NOT written, caller MUST NOT delete) →
    write config. Returns a summary ``{dest, files, manifest}``.
    """
    repo_root = Path(repo_root)
    src = repo_root / _VAULT_DIRNAME
    if not src.is_dir():
        raise VaultFlipError(f"in-tree vault not found: {src}")
    dest = external_store_path(repo_root, base)
    if dest.exists() and any(dest.iterdir()):
        raise VaultFlipError(
            f"external store already exists and is non-empty: {dest} "
            "(refusing to clobber; remove it or pick a clean base)"
        )
    manifest = migrate(src, dest)
    problems = verify(dest, manifest)
    if problems:
        raise VaultFlipError(
            "MIGRATION VERIFY FAILED — in-tree vault is UNTOUCHED, config NOT "
            "written. Do NOT delete the source. Problems:\n  "
            + "\n  ".join(problems)
        )
    write_config(repo_root, dest)
    return {"dest": str(dest), "files": len(manifest), "manifest": manifest}


def rename_store(repo_root: Path, *, base: Path | None = None) -> dict:
    """Migrate an already-flipped store to the [[ADR-109]] human-identifiable name
    ``<project-slug>-<shorthash>`` + repoint the flip config. Composes the existing
    ``migrate`` / ``verify`` / ``write_config`` primitives; preserves the
    copy → verify → rewrite-config → delete-old ordering so the vault is NEVER
    unresolvable mid-migration (on any pre-config-rewrite failure the config still
    resolves to the intact source).

    - No flip config → raise (vault not external; nothing to rename).
    - **Missing ``current``** (config → non-existent dir) → raise — NEVER a silent
      empty-store repoint (mirrors ``rollback``'s ``is_dir`` guard; meta-Critic M-add-1:
      ``migrate`` of a missing dir yields an empty manifest that ``verify`` passes
      vacuously).
    - **Idempotent**: ``current`` already resolves to ``new`` → no-op.
    - **Pre-existing non-empty ``new``** (3-way, never destroys non-our data, M2):
      a COMPLETE verified copy → **RESUME** (skip migrate — an interrupted prior
      rename); an OUR-partial = **whole files missing, every present file's hash
      correct** (only ``MISSING`` problems — the migrate was interrupted at a
      file boundary) → delete + redo; ANYTHING else (``UNEXPECTED`` OR
      ``HASH MISMATCH`` — foreign content, OR a truncated final file from an
      interrupt mid-``write_bytes``) → **refuse** (conservative by design — never
      delete a dir we can't positively identify as our clean partial; the
      operator removes it + retries). I.e. auto-redo covers the whole-file-missing
      interrupt subset; a truncated-final-file interrupt is safely refused, not
      redone (code-review M2).
    """
    repo_root = Path(repo_root)
    cfg_val = read_config_value(repo_root)
    if not cfg_val:
        raise VaultFlipError(
            "no flip config found — nothing to rename (vault is not external)"
        )
    current = Path(cfg_val)
    if not current.is_dir():
        raise VaultFlipError(
            f"configured external store missing: {current} — config points at a "
            "non-existent dir; resolve manually before renaming"
        )
    new = external_store_path(repo_root, base)
    if current.resolve() == new.resolve():
        return {"renamed": False, "resumed": False, "dest": str(new)}

    resumed = False
    manifest: dict[str, str]
    if new.exists() and any(new.iterdir()):
        expected = _manifest_of(current)
        problems = verify(new, expected)
        if not problems:
            resumed, manifest = True, expected          # complete verified copy → resume
        elif all(p.startswith("MISSING at dest:") for p in problems):
            try:
                shutil.rmtree(new)                      # our interrupted partial → redo
            except OSError as exc:                      # Windows lock / read-only (code-review M1)
                raise VaultFlipError(
                    f"could not clear the partial copy at {new} ({exc}) — config "
                    f"UNCHANGED (still resolves to the intact source {current}); "
                    "remove it manually and retry"
                ) from exc
        else:
            raise VaultFlipError(
                f"refusing to rename into {new}: it contains unrecognized content "
                "(not a leftover from this rename) — remove it manually if intended, "
                "then retry"
            )

    if not resumed:
        manifest = migrate(current, new)
        problems = verify(new, manifest)
        if problems:
            try:
                shutil.rmtree(new)
            except OSError:
                pass
            raise VaultFlipError(
                "RENAME VERIFY FAILED — config UNCHANGED (still resolves to the intact "
                f"source {current}). Problems:\n  " + "\n  ".join(problems)
            )

    write_config(repo_root, new)                        # config now → verified new
    try:
        shutil.rmtree(current)
    except OSError as exc:
        print(
            f"WARN: rename succeeded (config → {new}) but old store not removed "
            f"({current}): {exc}",
            file=sys.stderr,
        )
    return {
        "renamed": True, "resumed": resumed,
        "from": str(current), "dest": str(new), "files": len(manifest),
    }


def rollback(repo_root: Path) -> dict:
    """Scripted inverse: copy the external store back to in-tree ``architecture/``
    + unset the config. (The caller re-tracks via ``git add`` + removes the
    ``.gitignore`` entry — git ops stay in the skill prose.) Cheap only within
    the same build, before post-flip external writes diverge (ADR-107 §Reversibility).
    """
    repo_root = Path(repo_root)
    ext = read_config_value(repo_root)
    if not ext:
        raise VaultFlipError(
            "no flip config found — nothing to roll back (vault is not external)"
        )
    ext_path = Path(ext)
    if not ext_path.is_dir():
        raise VaultFlipError(f"configured external store missing: {ext_path}")
    src = repo_root / _VAULT_DIRNAME
    manifest = migrate(ext_path, src)
    problems = verify(src, manifest)
    if problems:
        raise VaultFlipError(
            "ROLLBACK VERIFY FAILED — config left in place (external store is "
            "intact). Problems:\n  " + "\n  ".join(problems)
        )
    remove_config(repo_root)
    return {"restored_to": str(src), "files": len(manifest)}


# ── CLI ───────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools._vault_flip",
        description="Flip the vault to the external shared store, or roll it back "
                    "(slice-115 / ADR-107).",
    )
    p.add_argument("--repo-root", type=Path, default=Path("."),
                   help="Repo root (default: cwd).")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--flip", action="store_true", help="Migrate in-tree → external + write config.")
    g.add_argument("--rollback", action="store_true", help="Restore external → in-tree + unset config.")
    g.add_argument("--rename-store", action="store_true",
                   help="Rename an already-flipped store to <project-slug>-<shorthash> + repoint config (ADR-109).")
    g.add_argument("--print-path", action="store_true", help="Print the resolved external store path and exit.")
    return p


def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 2
    repo_root = args.repo_root.resolve()
    try:
        if args.print_path:
            print(str(external_store_path(repo_root)))
            return 0
        if args.flip:
            res = flip(repo_root)
            print(f"FLIPPED: {res['files']} files → {res['dest']}")
            return 0
        if args.rollback:
            res = rollback(repo_root)
            print(f"ROLLED BACK: {res['files']} files → {res['restored_to']}")
            return 0
        if args.rename_store:
            res = rename_store(repo_root)
            if res["renamed"]:
                verb = "RESUMED" if res.get("resumed") else "RENAMED"
                print(f"{verb}: {res['files']} files {res['from']} → {res['dest']}")
            else:
                print(f"ALREADY NAMED: {res['dest']}")
            return 0
    except VaultFlipError as exc:
        print(f"vault-flip error: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
