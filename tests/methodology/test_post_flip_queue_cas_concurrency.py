"""R-32 post-flip concurrency proof for the queue read-modify-write writers
(slice-109 / [[ADR-098]]).

Proves, NON-VACUOUSLY (by mutation, AP-5) and under barrier-synchronized
contention (AP-6), that routing the queue/claim RMW writers through the CAS
channel (`_vault_write.safe_rewrite_text`) closes the lost-update class that a
naive whole-file `safe_write_text` leaves open — the exact hazard the external
vault flip would otherwise re-open once the queue is untracked and PCR's
git-merge reconciliation retires.

  CAS (safe) arm — the REAL writer path: N `mp.Barrier`-synchronized spawn
  workers each call the production `record_pick` (and, in the mixed test, a
  `_cas_rewrite` claim + a `write_slice_queue` regen) against ONE shared
  slice-queue.md. CAS makes them CONVERGE: every distinct pick line lands; ZERO
  lost.

  Naive (mutation) arm — NON-VACUITY: N barrier-synchronized workers each read the
  same base and append a line via `safe_write_text` (NO CAS) → the lock serializes
  the writes but each computed `new` off the stale base → N-1 lines LOST. If this
  ever stops losing, the CAS proof above has gone vacuous.

Workers are `multiprocessing(spawn)` processes (NOT threads — the GIL can mask
in-thread contention; Windows has no fork), released by a shared `mp.Barrier` (an
un-barriered spawn pool staggers and never overlaps — the slice-094 lesson). The
queue is seeded LF (the `.gitattributes eol=lf`-enforced no-flip default, Critic
B1). The RMW lost-update is APP-LEVEL (two processes read the same base, both
replace the whole file) → both arms run CROSS-PLATFORM.
"""
from __future__ import annotations

import multiprocessing as mp
from pathlib import Path

_JOIN_TIMEOUT = 120.0  # bounded — a lock/convergence hang fails loud
# code-review m2: a per-`wait` timeout so a sibling that dies AFTER entering the
# barrier (CPython #123899) aborts the survivors promptly (BrokenBarrierError →
# loud worker exit) instead of wedging until _JOIN_TIMEOUT. The happy path (all
# workers reach the barrier within ms) is unaffected.
_BARRIER_TIMEOUT = 30.0
_N_WORKERS = 6


_CAND_ENTRY = (
    "### add-foo\n\n"
    "- **Source:** seed\n"
    "- **Blast-radius:** `unknown`\n"
    "- **Parallel-safety:** UNKNOWN-NO-GRAPH\n"
    "- **Effort:** SMALL\n"
    "- **Risk-retired:** LOW\n"
)


def _seed(path: Path, *, with_pick_log: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"# Slice queue\n\n## Candidates\n\n{_CAND_ENTRY}"
    if with_pick_log:
        body += (
            "\n## Pick log\n\n"
            "- slice-001-seed — picked 2026-01-01T00:00:00+00:00 by Seed s@x\n"
        )
    path.write_bytes(body.encode("utf-8"))  # LF on disk


# ── workers (module-level for spawn picklability) ───────────────────────────


def _pick_worker(qpath: str, w: int, barrier) -> None:
    from tools.slice_queue_writer import record_pick

    barrier.wait(_BARRIER_TIMEOUT)  # maximal contention
    record_pick(
        repo_root=Path("."), slice_name=f"slice-{200 + w}-x",
        picker_identity=f"W{w} w{w}@x", out_path=Path(qpath),
    )


def _pick_naive_worker(qpath: str, w: int, barrier) -> None:
    """Mutation arm: read + append a pick line via safe_write_text (NO CAS)."""
    from tools._vault_write import safe_write_text

    barrier.wait(_BARRIER_TIMEOUT)
    p = Path(qpath)
    text = p.read_text(encoding="utf-8")
    new = text.rstrip("\n") + f"\n- slice-{200 + w}-x — picked T by W{w}\n"
    safe_write_text(p, new)  # no expected_base → clobbers concurrent writers


def _claim_worker(qpath: str, barrier) -> None:
    from tools.slice_queue_claim import _cas_rewrite, apply_claim

    barrier.wait(_BARRIER_TIMEOUT)
    _cas_rewrite(
        Path(qpath),
        lambda t: apply_claim(t, "add-foo", "Claimer c@x", "2026-02-02T00:00:00+00:00", force=False),
        always_write=False,
    )


def _regen_worker(qpath: str, barrier) -> None:
    from tools.slice_queue_writer import write_slice_queue

    barrier.wait(_BARRIER_TIMEOUT)
    cands = [{"name": "add-foo", "source": "seed", "hint_files": [],
              "effort": "SMALL", "risk_retired": "LOW"}]
    write_slice_queue(
        repo_root=Path("."), candidates=cands, active_slice_num=109,
        graph_path=None, out_path=Path(qpath),
    )


def _run(workerfn, qpath: str, n: int) -> None:
    ctx = mp.get_context("spawn")
    barrier = ctx.Barrier(n)
    procs = [ctx.Process(target=workerfn, args=(qpath, w, barrier)) for w in range(n)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(_JOIN_TIMEOUT)
        assert not p.is_alive(), "worker hung (lock deadlock / non-convergence?)"


def _pick_survivors(qpath: str, n: int) -> int:
    data = Path(qpath).read_text(encoding="utf-8")
    return sum(1 for w in range(n) if f"slice-{200 + w}-x" in data)


def test_concurrent_queue_rmw_zero_lost(tmp_path: Path) -> None:
    """N barrier-synced record_pick workers (distinct slices) on one shared queue
    lose ZERO — every pick line survives; the file stays LF (no B1 churn)."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=True)
    _run(_pick_worker, str(q), _N_WORKERS)
    survivors = _pick_survivors(str(q), _N_WORKERS)
    assert survivors == _N_WORKERS, (
        f"CAS LOST {_N_WORKERS - survivors} of {_N_WORKERS} picks:\n"
        f"{q.read_text(encoding='utf-8')}"
    )
    assert b"\r" not in q.read_bytes(), "EOL drift — CAS churned the LF queue"


def test_concurrent_record_pick_distinct_slices_both_survive(tmp_path: Path) -> None:
    """Critic M2: concurrent picks of DISTINCT slices (distinct prefixes) must all
    survive — the precise lost-update the slice fixes."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=True)
    _run(_pick_worker, str(q), 4)
    assert _pick_survivors(str(q), 4) == 4


def test_concurrent_first_pick_empty_base_both_create(tmp_path: Path) -> None:
    """Critic M-add-2: the empty / no-`## Pick log` base — concurrent FIRST picks
    all create-and-merge the section; ZERO lost, exactly ONE pick-log section."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=False)  # NO ## Pick log section — the create race
    _run(_pick_worker, str(q), _N_WORKERS)
    assert _pick_survivors(str(q), _N_WORKERS) == _N_WORKERS
    assert q.read_text(encoding="utf-8").count("## Pick log") == 1, (
        "create race produced a duplicate / missing pick-log section"
    )


def test_concurrent_mutation_triggers_retry_both_land(tmp_path: Path) -> None:
    """AC1 / Critic M1: a concurrent mutation between base-capture and write forces
    a CAS retry; both updates land (2-worker focused case)."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=True)
    _run(_pick_worker, str(q), 2)
    assert _pick_survivors(str(q), 2) == 2


def test_concurrent_mixed_writers_all_land(tmp_path: Path) -> None:
    """AC2: the THREE contended writers — record_pick + a claim (_cas_rewrite) + a
    write_slice_queue regen — contend on one queue under a barrier; all three
    effects survive (CAS reconciles cross-writer, no git/PCR)."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=True)
    ctx = mp.get_context("spawn")
    barrier = ctx.Barrier(3)
    procs = [
        ctx.Process(target=_pick_worker, args=(str(q), 50, barrier)),
        ctx.Process(target=_claim_worker, args=(str(q), barrier)),
        ctx.Process(target=_regen_worker, args=(str(q), barrier)),
    ]
    for p in procs:
        p.start()
    for p in procs:
        p.join(_JOIN_TIMEOUT)
        assert not p.is_alive(), "mixed worker hung"
    txt = q.read_text(encoding="utf-8")
    assert "slice-250-x" in txt, f"record_pick line lost:\n{txt}"          # A
    assert "Claimer c@x" in txt, f"claim lost:\n{txt}"                      # B
    assert "### add-foo" in txt, f"regen candidates lost:\n{txt}"           # C


def test_mutation_plain_write_loses_update(tmp_path: Path) -> None:
    """AP-5 NON-VACUITY (mutation): the naive whole-file RMW (no CAS) under the SAME
    barrier-synced contention LOSES writes — N-1 vanish. If this stops losing, the
    CAS proofs above are meaningless."""
    q = tmp_path / "architecture" / "slice-queue.md"
    _seed(q, with_pick_log=True)
    _run(_pick_naive_worker, str(q), _N_WORKERS)
    survivors = _pick_survivors(str(q), _N_WORKERS)
    assert survivors < _N_WORKERS, (
        f"mutation VACUOUS — naive RMW lost ZERO of {_N_WORKERS}; the CAS proof "
        f"would be meaningless:\n{q.read_text(encoding='utf-8')}"
    )
