# Critique: Slice 094 harden-vault-write-safety (v3 — AC4 concurrency proof)

**Critic reviewed**: mission-brief.md (v3), design.md (v3 §Why v3 + §Concurrency proof), ADR-086 (unchanged), tools/_vault_write.py, tests/methodology/test_vault_safe_write.py. The Critic EXECUTED its own probes of `os.write`/`O_APPEND` atomicity + EPERM on the real runtime (Win11/CPython 3.13.13/spawn).
**Date**: 2026-06-01
**Critic result**: BLOCKED
> **v3 critique** — supersedes the v2 NEEDS-FIXES critique + EXTEND critique-review (preserved in git). Scoped to the AC4 concurrency-proof correction. The v1 BLOCKED + v2 NEEDS-FIXES records are in git history (v2 TRI-1 ratified).

## Summary

The v3 EPERM-resilience proof design is sound and non-vacuous — but the v3 redesign **dropped a REAL, reproducible R-32 append lost-update hazard on a false premise**. The Critic independently probed and found that unlocked concurrent `O_APPEND` on Windows loses WHOLE writes (the lock prevents it), falsifying the v3 "os.write is atomic ⇒ no corruption ⇒ the append lock protects nothing" claim. **The Builder reproduced and CONFIRMED the Critic** via a barrier-synchronized probe (the Builder's first probe used an un-barriered spawn pool whose ~100 ms/worker stagger masked the hazard): 16 workers → 5-10 survive unlocked, N/N locked; 32 → 7-15 unlocked, N/N locked; every size 64B-64KB. The append lock is **load-bearing**. Corrected: Proof 2 = append LOST-UPDATE prevention (barrier-synchronized).

## Findings

### Blockers (must address before /build-slice)

#### B1: v3's "os.write atomic ⇒ 0 corruption unlocked ⇒ drop the append proof" premise is false; unlocked concurrent O_APPEND loses WHOLE writes, and the lock prevents it
- **Claim under review**: design.md (v3) — "concurrent `O_APPEND` never splits/interleaves … 0 corruption, locked AND unlocked … the lock's append value is … NOT interleaving-prevention (`os.write` is already atomic)."
- **Issue**: The corruption mode is **lost whole-writes**, not interleaving. `os.write` IS byte-atomic (no splicing — survivors are contiguous), but concurrent `O_APPEND` EOF-positioning is NOT atomic across opens (two opens compute the same end offset; the second clobbers the first). The v3 conflated "no interleaving" with "no corruption."
- **Evidence**: Critic probe — 3-4/8 writers lost at ≥512B. **Builder reconciliation (barrier-synchronized, decisive)**: un-barriered spawn-stagger masked it (Builder's false negative); WITH `mp.Barrier`, unlocked loses 6-11/16 and 17-25/32 writes every size 64B-64KB, locked loses 0, every run. `_vault_write.py:14`/:128-129 docstring already promises the lock "closes the read-modify-write lost-update window."
- **Proposed fix**: Restore the append concurrency proof as a **lost-update** proof: N barrier-synchronized workers each `safe_append_text` a unique multi-KB payload → all N survive; mutation (strip lock → raw `os.open(O_APPEND)`+`os.write`) → survivors < N. Stronger + more faithful to R-32 than the EPERM-append framing.
- **Builder draft**: **ACCEPTED-PENDING** — Builder independently CONFIRMED the Critic by barrier-synchronized probe (the two-persona model caught a real Builder error). Design §Concurrency proof Proof 2 + §Why v3 corrected NOW (the spec); the lost-update test is the Task-4 build deliverable. `/code-review` is the required second APED-1 author on the restored proof.

#### B2: AC4 + design assert a falsifiable platform claim ("os.write atomic … never interleaves at ANY size") + a dead-weight implication that contradict the primitive's own docstring and slice-092's non-vacuity law
- **Claim under review**: AC4 (v3) + design §Why v3/§Concurrency proof + the §Sub-decision recording "the lock protects nothing observable on append" as settled.
- **Issue**: The prose itself is a load-bearing false claim baked into an AC + sub-decision; it contradicts `_vault_write.py:14` (lock "closes the lost-update window") and slice-092 ("prove non-vacuity by mutation" — the v3 removed a mutation that WOULD fail). Risks the next slice re-deriving from "os.write is atomic" at the cross-platform flip.
- **Evidence**: B1 probe; `_vault_write.py:14`; `_index.md` slice-092 lesson.
- **Proposed fix**: Rewrite AC4 + §Why v3 + §Concurrency proof + §Sub-decision: drop the universal "os.write atomic ⇒ no corruption unlocked" claim; state the correct distinction (byte-atomic `os.write` prevents interleaving, but non-atomic Windows `O_APPEND` EOF-positioning loses whole writes, which the lock prevents — verified). Record the corrected DISCOVERED finding.
- **Builder draft**: **ACCEPTED-FIXED** — corrected prose applied this round in design.md §Why v3 (two-turn story), §Concurrency proof, §Sub-decision, and mission-brief AC4 + verification row 4 + must-not-defer bullet. The false "os.write atomic / lock protects nothing on append" claim is deleted; the lost-UPDATE distinction + the spawn-stagger DISCOVERED finding are recorded.

### Majors (address this slice)

#### M1: Holder-release-within-retry-budget is a flake vector; specify a non-timing-coupled construction
- **Issue**: A fixed holder sleep racing the fixed ~3.15 s retry budget can flake both ways under CI load (safe path EPERMs if hold stretches; mutation non-deterministic if hold too short).
- **Proposed fix**: Event-gate the construction — holder signals "held" via `Event` before the raw op (deterministic raw EPERM), holds ≪ budget, and the safe path asserts SUCCEEDS (not within-N-retries).
- **Builder draft**: **ACCEPTED-PENDING** — design §Concurrency proof Proof 1 corrected NOW to the Event-gated construction (M1); implemented at Task-4 build.

#### M2: nt-guard skips ALL POSIX concurrency assertion — but the flip may target Linux/Mac, and append lost-update is the cross-platform-relevant hazard
- **Issue**: Blanket nt-guard ships zero concurrency assertion for the platform the flip heads toward; R-32 is the load-bearing flip blocker.
- **Proposed fix**: Keep the EPERM/lost-update **mutation** nt-guarded (vacuous on POSIX), but run the **safe-path positive assertion** ("safe_append_text under N concurrent workers loses zero writes") cross-platform — a POSIX failure would be a flip-blocking discovery surfaced now.
- **Builder draft**: **ACCEPTED-PENDING** — design §Concurrency proof Proof 2 + AC4 corrected NOW (M2 cross-platform safe assertion; nt-guard only the mutation); implemented at Task-4 build.

### Minors (log; address if cheap)

#### m1: Existing thread-based `test_concurrent_appenders_no_lost_update` (threads, ~10B lines) is in the GIL-masked/small-payload regime the design bans — cannot catch B1, risks reading as redundant coverage
- **Builder draft**: **ACCEPTED-PENDING** — at Task-4 build, add a note (test docstring + mission-brief) that the new spawn+barrier lost-update proof is the authoritative append concurrency proof; the slice-093 thread test remains a cheap basic-non-clobbering smoke only. No code change to the existing test.

#### m2: Assert `PermissionError` type, not `.winerror == 5`, on the append path (winerror was None there)
- **Builder draft**: **ACCEPTED-PENDING** — largely MOOTED by the B1 correction (Proof 2 append is now LOST-UPDATE, not EPERM, so there is no append-EPERM `.winerror` assertion). Proof 1 (whole-file `os.replace`) keeps `.winerror == 5` (Critic verified os.replace carries it reliably); any residual EPERM assertion matches `PermissionError` type. Settled at Task-4 build.

### Meta-Critic missed finding (from critique-review.md, DR-1 — reconciled into TRI-1)

#### M-add-1: the M2 cross-platform safe-path assertion is near-vacuous on POSIX — label it a non-regression canary, not lock-value coverage
- **Issue**: On POSIX, `O_APPEND` `write()` is kernel-atomic → unlocked N concurrent appends also all survive → the locked safe-path assertion passes WITHOUT a mutation arm that fails on POSIX (the design nt-guards the mutation). So POSIX-green is a smoke/canary, not non-vacuous lock-value proof; the flip slice must not misread it.
- **Proposed fix**: one sentence in design §Concurrency proof Proof 2 + mission-brief AC4 M2 clause labeling the POSIX leg a non-regression canary; genuine POSIX lock-value proof is flip-slice work.
- **Builder draft**: **ACCEPTED-FIXED** — labeling applied this round (design.md §Concurrency proof Proof 2 "M-add-1" clause + mission-brief AC4 M2 clause).

## Dimensions checked
- [x] Unfounded assumptions — **B1, B2** (the "os.write atomic ⇒ no corruption ⇒ lock protects nothing" assumption, disproven by execution).
- [x] Missing edge cases — **B1, M2** (concurrent large-append lost-update; POSIX/flip-target edge).
- [x] Over-engineering — none. The append lock is load-bearing (B1), NOT dead weight.
- [x] Under-engineering — **B1** (AC4 delivered LESS than the must-not-defer "non-vacuous concurrency test" requires for the real hazard).
- [x] Contract gaps — none new; audit/CLI exit-code contract unchanged from ratified v2.
- [x] Security — none (ADR-067 cooperative/data-integrity model, correctly scoped).
- [x] Drift from vault — internal only: v3 prose contradicted `_vault_write.py:14` docstring (→ B2, now fixed). No ADR-086 contradiction; named test file consistent across mission-brief + design.
- [x] Web-known issues — Critic executed the platform behavior directly: Windows `O_APPEND` non-atomic EOF-positioning under concurrency → lost whole-writes; `#15723` (the v2/v3 citation) mis-applied (it concerns `f.write()` buffering).
- [x] Cross-cutting conformance — APED-1: the v3 redesign rested on a behavior claim about a code path; the discipline mandates EXECUTING it (the Critic did, the Builder re-confirmed by barrier probe). slice-092 non-vacuity-by-mutation applied. `/code-review` is the required second APED-1 author on the restored proof at build.

## Triage

**Triaged by**: user
**Date**: 2026-06-01
**Final verdict**: NEEDS-FIXES
> Reconciled across BOTH passes (DR-1): first Critic BLOCKED + meta-Critic ADJUST. User ratified all dispositions 2026-06-01. Meta-Critic adjustments applied: **B2 severity Blocker→Major** (consequence-of-B1, not independent) and **+M-add-1** (POSIX-canary, ACCEPTED-FIXED). Verdict NEEDS-FIXES = B1/M1/M2/m1/m2 ACCEPTED-PENDING (built at Task 4), no ESCALATED. Both Critics agreed the corrected Proof 2 spec is build-ready; no third `/design-slice` round.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Builder AND meta-Critic both reproduced the lost-write hazard (barrier 16→5-10 survive; un-barriered 64→10-39 lost); restore append lost-update proof at Task-4 build; design spec corrected now |
| B2 | Major | ACCEPTED-FIXED | (severity Blocker→Major per meta-Critic — consequence-of-B1) False "os.write atomic / lock protects nothing on append" prose rewritten this round (design §Why v3/§Concurrency proof/§Sub-decision + mission-brief AC4/row4/must-not-defer) |
| M1 | Major | ACCEPTED-PENDING | Event-gated holder construction (no wall-clock coupling); design corrected now, test at build |
| M2 | Major | ACCEPTED-PENDING | Cross-platform safe-path assertion; nt-guard only the mutation; design corrected now, test at build |
| M-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic missed-finding) POSIX safe-path leg labeled a non-regression canary, not lock-value coverage — applied this round (design §Concurrency proof + mission-brief AC4) |
| m1 | Minor | ACCEPTED-PENDING | Note spawn+barrier proof is authoritative; thread test = basic smoke only |
| m2 | Minor | ACCEPTED-PENDING | Mooted by B1 (append proof now lost-update not EPERM); Proof 1 keeps `.winerror==5` on os.replace |
