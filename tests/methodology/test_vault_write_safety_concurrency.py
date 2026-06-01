"""R-32 concurrency proof for the _vault_write safe primitives (slice-094 / VWS-1
/ [[ADR-086]]).

Proves, NON-VACUOUSLY (by mutation), what the sidecar lock + bounded EPERM-retry
ACTUALLY protect — one proof per primitive, on the real runtime:

  Proof 1 — whole-file EPERM-resilience (`safe_write_text` / `os.replace`):
    under an EXCLUSIVE external handle (CreateFileW dwShareMode=0 — the
    OneDrive/AV/Search-indexer scenario `_vault_write`'s docstring cites), a raw
    `os.replace` raises PermissionError (WinError 5); `safe_write_text`'s lock+
    retry absorbs it. nt-guarded (POSIX `os.replace` is atomic and won't EPERM
    under a reader → the mutation would be vacuous off-Windows). M1: the holder
    signals "held" via an Event BEFORE the op (so the raw EPERM is deterministic,
    no wall-clock coupling) and auto-releases after a hold ≪ the ~3.15 s retry
    budget, so the safe path has wide margin; we assert the safe op SUCCEEDS.

  Proof 2 — append LOST-UPDATE prevention (`safe_append_text` / `os.open(O_APPEND)`):
    N **barrier-synchronized** spawn workers each append a unique multi-KB
    payload to ONE shared target. Unlocked, Windows `O_APPEND` EOF-positioning is
    NOT atomic across concurrent opens (two opens compute the same end offset; the
    second clobbers the first) → whole writes are LOST (verified at build: 16
    workers → 5-10 survive, 32 → 7-15; every size 64B-64KB). `safe_append_text`'s
    lock serializes the appends → all N survive. This is the real R-32 append
    hazard the primitive's docstring (`_vault_write.py:128-129`) promises to close.
    NOTE: `os.write` IS byte-atomic (a survivor's bytes are contiguous — no
    interleaving); the hazard is lost-UPDATE, not byte-splicing.

    M2 (cross-platform): the lost-update MUTATION is nt-guarded (POSIX `O_APPEND`
    `write()` is kernel-atomic → unlocked also survives → mutation vacuous off
    Windows). The SAFE-PATH positive assertion runs CROSS-PLATFORM — but on POSIX
    it is an explicit non-regression CANARY (no mutation arm fails there), NOT a
    lock-value proof; genuine POSIX lock-value proof is flip-slice work. A POSIX
    failure of the canary would be a flip-blocking discovery surfaced now.

Workers are `multiprocessing(spawn)` processes (NOT threads — the GIL can mask
in-thread contention; Windows has no fork). Real contention is forced with a
`mp.Barrier` (an un-barriered spawn pool staggers ~100 ms/worker and never
overlaps — that masked the hazard in the Builder's first probe; the v3 /critique
B1 caught it). Every `join` has a bounded timeout so a lock-acquire hang fails
loud.
"""
from __future__ import annotations

import multiprocessing as mp
import os
from pathlib import Path

import pytest

from tools._vault_write import safe_append_text, safe_write_text

_IS_WINDOWS = os.name == "nt"
_JOIN_TIMEOUT = 60.0  # bounded — a cross-process lock-acquire hang fails loud
_nt_only = pytest.mark.skipif(
    not _IS_WINDOWS,
    reason="Windows MoveFileEx / non-atomic-O_APPEND EPERM/lost-write hazard; on "
    "POSIX os.replace is atomic and O_APPEND write() is kernel-atomic → the "
    "mutation would be vacuous (M2)",
)

# ── Proof 2: append lost-update workers (module-level for spawn re-import) ──

_APPEND_SIZE = 4096  # multi-KB payload; loss reproduces from 64B up (build probe)
_APPEND_WORKERS = 20  # barriered, 16 already lost 6-11/trial at build; 20 = margin


def _payload(worker: int, size: int) -> str:
    """Unique, fixed-width (so every payload is byte-identical in length)."""
    return f"<<W{worker:03d}>>" + ("x" * size) + f"<<E{worker:03d}>>\n"


def _append_worker_safe(path_s: str, payload: str, barrier) -> None:
    barrier.wait()
    safe_append_text(path_s, payload)


def _append_worker_raw(path_s: str, payload_bytes: bytes, barrier) -> None:
    barrier.wait()  # all workers released simultaneously → maximal contention
    fd = os.open(path_s, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0), 0o644)
    os.write(fd, payload_bytes)
    os.close(fd)


def _run_append(path: Path, n_workers: int, size: int, *, use_lock: bool) -> tuple[int, int]:
    """Run n_workers barrier-synchronized appenders; return (survivors, file_len).

    A worker 'survives' iff its unique start marker is present in the file."""
    ctx = mp.get_context("spawn")
    barrier = ctx.Barrier(n_workers)
    procs = []
    for w in range(n_workers):
        pl = _payload(w, size)
        if use_lock:
            procs.append(ctx.Process(target=_append_worker_safe, args=(str(path), pl, barrier)))
        else:
            procs.append(ctx.Process(target=_append_worker_raw, args=(str(path), pl.encode("ascii"), barrier)))
    for p in procs:
        p.start()
    for p in procs:
        p.join(_JOIN_TIMEOUT)
        assert not p.is_alive(), "append worker hung (lock deadlock?) — bounded-timeout tripwire"
    data = Path(path).read_bytes()
    survivors = sum(1 for w in range(n_workers) if f"<<W{w:03d}>>".encode("ascii") in data)
    return survivors, len(data)


@_nt_only
def test_append_lost_update_mutation_loses_writes(tmp_path: Path) -> None:
    """NON-VACUITY (mutation): unlocked concurrent O_APPEND under a barrier loses
    WHOLE writes — the raw channel that `safe_append_text` minus its lock leaves.
    If this ever stops losing, the safe-path proof below has gone vacuous."""
    reps = 2
    losses = []
    for rep in range(reps):
        f = tmp_path / f"raw_{rep}.md"
        survivors, _ = _run_append(f, _APPEND_WORKERS, _APPEND_SIZE, use_lock=False)
        losses.append(_APPEND_WORKERS - survivors)
    assert any(loss > 0 for loss in losses), (
        f"mutation VACUOUS — unlocked O_APPEND lost zero writes across {reps} reps "
        f"({losses}); the safe-path proof would be meaningless. (Expected loss: "
        f"build probe saw 6-11/16 lost every trial.)"
    )


def test_append_safe_loses_zero_writes(tmp_path: Path) -> None:
    """`safe_append_text` under N barrier-synchronized concurrent workers loses
    ZERO writes — all N payloads survive intact (distinct markers + exact length).

    M2: runs CROSS-PLATFORM. On Windows this is the lock-value proof (paired with
    the nt-only mutation above). On POSIX it is a non-regression CANARY only
    (unlocked also survives there) — a POSIX failure would be a flip-blocking
    discovery; it is NOT a POSIX lock-value proof (that is flip-slice work)."""
    reps = 2
    payload_len = len(_payload(0, _APPEND_SIZE).encode("ascii"))
    for rep in range(reps):
        f = tmp_path / f"safe_{rep}.md"
        survivors, length = _run_append(f, _APPEND_WORKERS, _APPEND_SIZE, use_lock=True)
        assert survivors == _APPEND_WORKERS, (
            f"rep {rep}: safe_append_text LOST {_APPEND_WORKERS - survivors} of "
            f"{_APPEND_WORKERS} writes under concurrency"
        )
        assert length == _APPEND_WORKERS * payload_len, (
            f"rep {rep}: file length {length} != expected {_APPEND_WORKERS * payload_len} "
            f"(a write was partially clobbered)"
        )


# ── Proof 1: whole-file EPERM-resilience (Windows exclusive-holder, M1) ──

_GENERIC_READ = 0x80000000
_OPEN_EXISTING = 3
_FILE_ATTRIBUTE_NORMAL = 0x80


def _exclusive_holder(path_s: str, held_evt, release_evt, hold_seconds: float) -> None:
    """Open `path_s` with an EXCLUSIVE handle (CreateFileW dwShareMode=0 — the
    OneDrive/AV/indexer scenario), signal 'held', then release on `release_evt`
    OR after `hold_seconds` (whichever first), then CloseHandle."""
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    h = k32.CreateFileW(
        path_s, _GENERIC_READ, 0, None, _OPEN_EXISTING, _FILE_ATTRIBUTE_NORMAL, None
    )
    held_evt.set()
    release_evt.wait(hold_seconds)
    invalid = ctypes.c_void_p(-1).value
    if h and h != invalid:
        k32.CloseHandle(h)


@_nt_only
def test_whole_file_eperm_mutation_raises(tmp_path: Path) -> None:
    """NON-VACUITY (mutation): a raw `os.replace` onto a target held by an
    exclusive external handle raises PermissionError (WinError 5) — the channel
    that `safe_write_text` minus its lock+retry leaves. Event-gated so the EPERM
    is deterministic (no wall-clock coupling — M1)."""
    target = tmp_path / "wf.md"
    target.write_bytes(b"seed\n")
    ctx = mp.get_context("spawn")
    held, release = ctx.Event(), ctx.Event()
    holder = ctx.Process(target=_exclusive_holder, args=(str(target), held, release, 30.0))
    holder.start()
    try:
        assert held.wait(30), "holder never acquired the exclusive handle"
        tmp = target.with_name(target.name + ".repl.tmp")
        tmp.write_bytes(b"x" * 64)
        with pytest.raises(PermissionError) as ei:
            os.replace(tmp, target)  # raw, no lock/retry → EPERM while held
        assert ei.value.winerror == 5, f"expected WinError 5, got {ei.value.winerror}"
        tmp.unlink(missing_ok=True)
    finally:
        release.set()
        holder.join(_JOIN_TIMEOUT)
        assert not holder.is_alive(), "holder hung"


@_nt_only
def test_whole_file_safe_write_absorbs_eperm(tmp_path: Path) -> None:
    """`safe_write_text`'s sidecar-lock + bounded EPERM-retry ABSORBS the WinError
    5 a raw replace raises under an exclusive holder: the holder auto-releases
    after a hold ≪ the ~3.15 s retry budget (M1 — wide margin), and we assert the
    safe write SUCCEEDS (not 'within N retries')."""
    target = tmp_path / "wf2.md"
    target.write_bytes(b"seed\n")
    ctx = mp.get_context("spawn")
    held, release = ctx.Event(), ctx.Event()
    # hold 0.1 s ≪ 3.15 s retry budget (6 × 0.05·2ⁿ): safe_write_text EPERMs on
    # its first attempt(s) then succeeds after release — ~15× margin to the last attempt.
    holder = ctx.Process(target=_exclusive_holder, args=(str(target), held, release, 0.1))
    holder.start()
    try:
        assert held.wait(30), "holder never acquired the exclusive handle"
        safe_write_text(target, "after\n")  # retries through the held window → succeeds
        assert target.read_text(encoding="utf-8") == "after\n"
    finally:
        release.set()
        holder.join(_JOIN_TIMEOUT)
        assert not holder.is_alive(), "holder hung"
