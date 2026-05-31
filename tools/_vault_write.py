"""Concurrent-write/append-safe vault writer (slice-093 / [[ADR-085]]).

The C2 concurrent-write-safety primitive (R-32): a shared MUTABLE vault
store turns loud git merge-conflicts into SILENT Windows lost-update /
atomic-rename-EPERM corruption (the ``.claude.json``/OneDrive class). This
module is the structural replacement for PCR-on-vault-files once the
slice-094 flip removes git-conflict resolution.

- ``safe_write_text``  — whole-file: sidecar-``.lock`` + temp-write +
  atomic ``os.replace`` + bounded retry on ``PermissionError``/EPERM.
- ``safe_append_text`` — append-only (ADRs, ``risk-register.md``,
  ``_index.md``, the PCR audit log): ``O_APPEND``/``FILE_APPEND_DATA``
  under the sidecar lock — non-clobbering, closes the read-modify-write
  lost-update window that whole-file atomic-replace does NOT.
- ``write_vault_root_config`` / ``read_vault_root_config`` — the
  per-project config API (production-called at the slice-094 flip).

The lock is acquired on a per-file SIDECAR ``<path>.lock`` — NEVER the
replace target (Windows ``msvcrt.locking``→``LockFileEx`` is *mandatory*,
so locking the target would block its own ``os.replace``).

Leading-underscore helper → auto-excluded from PMI-1 inventory. Imports
``tools._vault_paths._CONFIG_REL`` (the shared config-location SSoT, m2);
that does NOT break ``_vault_paths``'s own leaf-purity.
"""
from __future__ import annotations

import contextlib
import os
import time
from collections.abc import Iterator
from pathlib import Path

from tools._vault_paths import _CONFIG_REL

_LOCK_SUFFIX = ".lock"
_EPERM_RETRIES = 6
_EPERM_BACKOFF_BASE = 0.05  # seconds; exponential 0.05, 0.10, 0.20, ...
_LOCK_TIMEOUT = 15.0  # seconds
_LOCK_POLL = 0.02  # seconds between non-blocking lock attempts


@contextlib.contextmanager
def _file_lock(target: Path) -> Iterator[None]:
    """Hold an exclusive lock on the SIDECAR ``<target>.lock`` (NEVER the target
    itself) for the duration of the block. Cross-platform: ``msvcrt.locking``
    (Windows; mandatory byte-range) / ``fcntl.flock`` (POSIX; advisory). Blocks
    up to ``_LOCK_TIMEOUT`` polling non-blocking attempts, then ``TimeoutError``.
    """
    lockpath = target.with_name(target.name + _LOCK_SUFFIX)
    lockpath.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lockpath, "a+")  # noqa: SIM115 — released in finally
    try:
        deadline = time.monotonic() + _LOCK_TIMEOUT
        if os.name == "nt":
            import msvcrt

            while True:
                try:
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"timeout acquiring lock {lockpath}")
                    time.sleep(_LOCK_POLL)
        else:
            import fcntl

            while True:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError(f"timeout acquiring lock {lockpath}")
                    time.sleep(_LOCK_POLL)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()


def safe_write_text(path: Path | str, text: str, *, encoding: str = "utf-8") -> None:
    """Whole-file write: lock the sidecar → write a temp file → atomic
    ``os.replace`` onto the target, with bounded exponential-backoff retry on
    ``PermissionError`` (Windows EPERM when a handle is held by OneDrive / AV /
    indexer). Never leaves a truncated target (the replace is atomic)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with _file_lock(path):
        tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        tmp.write_text(text, encoding=encoding)
        last_exc: BaseException | None = None
        for attempt in range(_EPERM_RETRIES):
            try:
                os.replace(tmp, path)
                return
            except PermissionError as exc:  # WinError 5 — a handle is held
                last_exc = exc
                time.sleep(_EPERM_BACKOFF_BASE * (2**attempt))
        with contextlib.suppress(OSError):
            tmp.unlink()
        raise PermissionError(
            f"safe_write_text: could not atomically replace {path} after "
            f"{_EPERM_RETRIES} attempts — a handle is held by another process "
            f"(OneDrive / antivirus / Search indexer?). Last error: {last_exc}"
        )


def safe_append_text(path: Path | str, text: str, *, encoding: str = "utf-8") -> None:
    """Append-only write: lock the sidecar → ``O_APPEND``/``FILE_APPEND_DATA``
    open → write. Non-clobbering; closes the read-modify-write lost-update
    window that a whole-file atomic-replace does NOT (the append-log class:
    ADRs, ``risk-register.md``, ``_index.md``, the PCR audit log)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.encode(encoding)
    with _file_lock(path):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
        try:
            os.write(fd, data)
        finally:
            os.close(fd)


def write_vault_root_config(common_dir: Path | str, vault_path: Path | str) -> Path:
    """Write the per-project vault-root config at
    ``<common_dir>/aisdlc/vault-root`` (a single line: the absolute vault path)
    via ``safe_write_text``. Returns the config path. (Production-called at the
    slice-094 flip; test-exercised in slice-093.)"""
    cfg = Path(common_dir) / _CONFIG_REL
    safe_write_text(cfg, str(vault_path).strip() + "\n")
    return cfg


def read_vault_root_config(common_dir: Path | str) -> str | None:
    """Read the per-project vault-root config — the writer-side mirror of the
    inline reader in ``_vault_paths._read_common_dir_config`` (m2 parity, pinned
    by ``test_inline_and_helper_config_readers_agree``). Returns the stripped
    path, or ``None`` if absent/empty."""
    cfg = Path(common_dir) / _CONFIG_REL
    try:
        if not cfg.exists():
            return None
        text = cfg.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return text or None
