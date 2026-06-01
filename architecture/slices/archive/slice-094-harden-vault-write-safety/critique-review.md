# Critique Review: Slice 094 harden-vault-write-safety (v3 — AC4 concurrency proof)

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-01
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: ADJUST
> **v3 critique-review** — supersedes the v2 EXTEND review (preserved in git). Scoped to the AC4 concurrency-proof critique.

## Summary

The first Critic's central call (B1) is correct and the meta-Critic independently re-confirmed it by probe: unlocked concurrent `O_APPEND` on Windows loses whole writes, and the barrier is a legitimate *accelerator* of a real race, not its sole cause — loss fires un-barriered at higher worker counts too (10-39 of 64 lost, every rep). The review's substance is sound. The one adjustment is a severity mis-file (B2 is a consequence of B1, not an independent Blocker) and a missed-finding flag on the cross-platform M2 assertion being near-vacuous on POSIX — which matters precisely because the flip may target Linux/Mac.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (unlocked concurrent O_APPEND loses whole writes; lock is load-bearing) — **confirmed; Blocker is correct**. Independent probe (Win11/CPython 3.13.13/spawn, distinct-marker metric): barriered 16→lost 7-12, 32→lost 18-23; **un-barriered** 16→lost 2-7, 32→lost 5-18, **64→lost 10-39, every rep**. Real, reproducible, NOT a `mp.Barrier` artifact — the barrier only forces the worst case earlier. Maps to R-32's threat model (ADR-067: cooperating writers, two Claude sessions / parallel slices on a shared untracked vault). The lock is **load-bearing**; design.md§"Why v3" is correct; the v3-first-pass "drop the proof" was a genuine under-engineering defect. ACCEPTED-PENDING appropriate.
- **M1** (holder-release-within-retry-budget flake; Event-gate it) — confirmed; **Major correct**. Fixed holder sleep racing the ~3.15s budget (`_vault_write.py:37-38`) is a two-way flake under CI load. The Event-gated fix is the right construction; a correctness-of-test issue, not cosmetic.
- **m1** (existing thread-based `test_concurrent_appenders_no_lost_update` is GIL-masked/tiny-payload) — confirmed; **Minor correct**. `test_vault_safe_write.py:64-83`: threads + 9-byte payloads + safe-path-only (no mutation arm) → cannot catch B1. Doc-note disposition proportionate.
- **m2** (assert `PermissionError` type not `.winerror==5` on append) — confirmed, correctly noted **largely MOOTED** by B1 (Proof 2 now lost-update, not append-EPERM). Minor correct.

## Suspicious findings

None. The meta-Critic specifically stress-tested the most plausible over-reach — that B1 might be a barrier-only artifact unrepresentative of R-32's cooperative threat model. The probe falsified that: un-barriered loss is substantial at n≥32. B1 is not over-reach.

## Missed findings

- **M-add-1 (POSIX near-vacuity of the M2 cross-platform safe-path assertion)** — Minor. M2 (run the safe-path assertion cross-platform) is good, but on POSIX the assertion is **near-vacuous as a lock-value proof**: POSIX `O_APPEND` `write()` is kernel-atomic, so *unlocked* N concurrent appends also all survive — the locked assertion passes on POSIX without distinguishing the lock's contribution (no mutation arm fails on POSIX; the design nt-guards the mutation). Per Hendrickson (a test must be able to fail to be meaningful) + slice-092 non-vacuity-by-mutation: the POSIX leg is a **smoke/canary**, not lock-value coverage. Fix → Builder: add one sentence to design.md§Concurrency proof Proof 2 + mission-brief AC4 M2 clause stating the POSIX safe-path leg is a non-regression canary (NOT a mutation-backed proof); genuine POSIX lock-value proof is flip-slice work. Low cost; closes a flip-direction blind spot.

No other missed findings — the mutation faithfulness (strip lock → raw `os.open(O_WRONLY|O_CREAT|O_APPEND|O_BINARY)`+`os.write` is byte-exact to `safe_append_text` minus `_file_lock`, verified `_vault_write.py:145-163`) is correct; the Proof 2 spec is sufficiently pinned (16/32 workers, 64B-64KB, "every run," dual loss-metric distinct-marker-count AND `len == Σ payloads`) to build deterministically.

## Severity adjustments

- **B2** (false "os.write atomic ⇒ no corruption ⇒ lock protects nothing" prose) — **SEVERITY-WRONG: filed as Blocker, recommend Major.** Not an *independent* defect; it is the prose *symptom* of B1's root cause (the §"Why v3" conflation of "no interleaving" with "no corruption"). A derived documentation-of-a-wrong-premise finding rides the severity of the underlying defect — B1 is the Blocker; B2 is the Major prose-correction that flows from it. It gates `/design-slice` (already ACCEPTED-FIXED this round), not independently `/build-slice`. Verdict impact: none (B1 alone holds). Re-file B2 as M-prose (Major), consequence-of-B1.

## Notes

Confidence high on B1 — reproduced across three regimes; un-barriered loss at n≥32 settles the false-positive question. The first Critic's calibration on this slice is good — it caught a real under-engineering defect the Builder's own first probe missed (exactly the dual-review failure mode). The spawn-stagger DISCOVERED finding (design.md§Sub-decisions) is a genuine generalizable lesson. On **disposition soundness**: ACCEPTED-PENDING is sufficient — the corrected Proof 2 spec is not too thin to leave to build, so a third `/design-slice` round is not warranted; residual = implementation + the mandated `/code-review` second-APED-1-author pass. The two adjustments (B2 severity, M-add-1 POSIX-canary labeling) are reconciliation refinements for TRI-1, not a reason to re-design.
