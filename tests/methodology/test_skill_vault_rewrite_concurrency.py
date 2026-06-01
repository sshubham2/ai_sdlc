"""R-32 concurrency proof for the skill-driven READ-MODIFY-WRITE channel
(slice-097 / SVW-1-RMW / [[ADR-088]]).

Proves, NON-VACUOUSLY (by mutation), that compare-and-swap (`vault_edit rewrite`
over `safe_rewrite_text`) closes the lost-update class that a naive whole-file
read-modify-write leaves open — the exact scenario R-32 was opened for (two
concurrent slice completions both rewriting the `_index.md` recent-10 table, one
slice's row silently lost).

  CAS (safe) arm — the REAL skill path via the CLI SUBPROCESS (critique M1):
    N **barrier-synchronized** spawn workers each run the skill's read→rewrite→
    retry-on-exit-3 loop by SHELLING `$PY -m tools.vault_edit rewrite` (with
    AI_SDLC_VAULT_ROOT pointed at a tmp vault). Each reads the current file as its
    byte-exact base, appends its unique marker (the read-modify step), and rewrites
    with `--base-file`. A concurrent writer that landed first makes the base stale
    → exit 3 → the worker re-reads + re-applies + retries. CAS makes them CONVERGE:
    every worker's marker lands; ZERO lost.

  Naive (mutation) arm — NON-VACUITY (no CAS):
    N barrier-synchronized spawn workers each read the SAME initial base, append
    their marker, and `safe_write_text` (unconditional whole-file replace, NO CAS).
    All computed `new` from the stale initial base → the lock serializes the
    writes but the last writer's content (base + only ITS marker) wins → N-1
    markers are LOST. If this ever stops losing, the CAS proof above has gone
    vacuous.

Workers are `multiprocessing(spawn)` processes (NOT threads — the GIL can mask
in-thread contention; Windows has no fork), released by a shared `mp.Barrier` (an
un-barriered spawn pool staggers ~100 ms/worker and never overlaps — the slice-094
lesson). The fixture is a **CRLF** file (exercises critique B1: the CRLF
`_index.md` vs an LF/normalized base must not false-conflict, and the rewrite must
not churn CRLF→LF). Unlike the O_APPEND hazard (`test_vault_write_safety_concurrency.py`,
Windows-only), the RMW lost-update is APP-LEVEL (two processes read the same base,
both replace the whole file) → both arms run CROSS-PLATFORM.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import subprocess
import sys
from pathlib import Path

_JOIN_TIMEOUT = 120.0  # bounded — a cross-process lock/convergence hang fails loud
_RETRY_MAX = 80        # generous CAS-convergence bound (N workers ⇒ ~O(N) rounds)
_N_WORKERS = 6         # modest: each CAS worker shells ≥1 subprocess per round
_REPO_ROOT = str(Path(__file__).resolve().parents[2])


def _marker(w: int) -> str:
    return f"<<M{w:03d}>>\n"


def _subprocess_env(vault_root: str) -> dict:
    # Full env + AI_SDLC_VAULT_ROOT (the 1st-tier vault resolution, slice-093) so
    # the subprocess resolves --file under the TMP vault, never the real one.
    return {**os.environ, "AI_SDLC_VAULT_ROOT": vault_root, "PYTHONUTF8": "1"}


def _rewrite_worker_cas(
    vault_root: str, fname: str, scratch: str, w: int, barrier
) -> None:
    """The real skill path: read→rewrite→retry-on-3, shelling `vault_edit rewrite`."""
    barrier.wait()  # maximal contention
    env = _subprocess_env(vault_root)
    for attempt in range(_RETRY_MAX):
        # Capture the base via the DOCUMENTED protocol: `vault_edit read --out-file`
        # (NOT in-process read_bytes, NOT shell `>` — the slice-097 /code-review B1
        # gap: the prior in-process capture never exercised the real skill protocol,
        # and a shell `>` would corrupt the base under PowerShell). --out-file makes
        # Python write the raw bytes, byte-safe on every shell.
        bf = Path(scratch) / f"base_{w:03d}_{attempt}.bin"
        rc_read = subprocess.run(
            [sys.executable, "-m", "tools.vault_edit", "read",
             "--file", fname, "--out-file", str(bf)],
            cwd=_REPO_ROOT, env=env, capture_output=True,
        ).returncode
        if rc_read != 0:
            raise RuntimeError(f"worker {w}: vault_edit read --out-file rc={rc_read}")
        base = bf.read_bytes()  # byte-exact base, captured by the subcommand
        new = base.decode("utf-8") + _marker(w)  # read-modify: append my unique line
        cf = Path(scratch) / f"new_{w:03d}_{attempt}.md"
        cf.write_text(new, encoding="utf-8", newline="")  # exact; rewrite re-applies EOL
        rc = subprocess.run(
            [sys.executable, "-m", "tools.vault_edit", "rewrite",
             "--file", fname, "--base-file", str(bf), "--content-file", str(cf)],
            cwd=_REPO_ROOT, env=env, capture_output=True,
        ).returncode
        if rc == 0:
            return
        if rc == 3:
            continue  # CAS conflict — re-read + re-apply + retry
        raise RuntimeError(f"worker {w}: unexpected vault_edit rewrite rc={rc}")
    raise RuntimeError(f"worker {w}: CAS retry budget ({_RETRY_MAX}) exhausted")


def _rewrite_worker_naive(vault_root: str, fname: str, w: int, barrier) -> None:
    """Mutation arm: unconditional whole-file replace, NO CAS — clobbers."""
    from tools._vault_write import safe_write_text

    barrier.wait()
    target = Path(vault_root) / fname
    base = target.read_bytes()
    new = base.decode("utf-8") + _marker(w)
    safe_write_text(target, new)  # no expected_base → overwrites concurrent writers


def _seed_crlf(vault_root: Path, fname: str) -> None:
    vault_root.mkdir(parents=True, exist_ok=True)
    (vault_root / fname).write_bytes(b"# Index\r\nseed-row\r\n")  # CRLF (B1)


def _run(vault_root: str, scratch: str, fname: str, n: int, *, use_cas: bool) -> tuple[int, bytes]:
    ctx = mp.get_context("spawn")
    barrier = ctx.Barrier(n)
    procs = []
    for w in range(n):
        if use_cas:
            procs.append(ctx.Process(target=_rewrite_worker_cas, args=(vault_root, fname, scratch, w, barrier)))
        else:
            procs.append(ctx.Process(target=_rewrite_worker_naive, args=(vault_root, fname, w, barrier)))
    for p in procs:
        p.start()
    for p in procs:
        p.join(_JOIN_TIMEOUT)
        assert not p.is_alive(), "rewrite worker hung (lock deadlock / non-convergence?)"
    data = (Path(vault_root) / fname).read_bytes()
    survivors = sum(1 for w in range(n) if _marker(w).strip().encode("ascii") in data)
    return survivors, data


def test_cas_rewrite_loses_zero_updates(tmp_path: Path) -> None:
    """`vault_edit rewrite` CAS under N barrier-synchronized concurrent skill-path
    workers loses ZERO updates — every worker's marker survives, and the file stays
    CRLF (no B1 churn). This is the R-32 recent-10 hazard, closed."""
    vault = tmp_path / "vault"
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    fname = "idx.md"
    _seed_crlf(vault, fname)
    survivors, data = _run(str(vault), str(scratch), fname, _N_WORKERS, use_cas=True)
    assert survivors == _N_WORKERS, (
        f"CAS LOST {_N_WORKERS - survivors} of {_N_WORKERS} concurrent rewrites "
        f"(final file:\n{data.decode('utf-8', 'replace')})"
    )
    assert b"\r\n" in data, "EOL not preserved — CAS rewrite churned CRLF→LF (B1)"
    assert b"# Index" in data and b"seed-row" in data, "seed content lost"


def test_naive_rewrite_mutation_loses_writes(tmp_path: Path) -> None:
    """NON-VACUITY (mutation): unconditional whole-file replace (no CAS) under the
    same barrier-synchronized contention LOSES writes — N-1 markers vanish. If this
    ever stops losing, the CAS proof above is meaningless. Cross-platform (the RMW
    lost-update is app-level, not OS-atomicity-dependent)."""
    vault = tmp_path / "vault"
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    fname = "idx.md"
    _seed_crlf(vault, fname)
    survivors, data = _run(str(vault), str(scratch), fname, _N_WORKERS, use_cas=False)
    assert survivors < _N_WORKERS, (
        f"mutation VACUOUS — naive whole-file RMW lost ZERO of {_N_WORKERS} writes; "
        f"the CAS proof would be meaningless (final file:\n{data.decode('utf-8','replace')})"
    )
