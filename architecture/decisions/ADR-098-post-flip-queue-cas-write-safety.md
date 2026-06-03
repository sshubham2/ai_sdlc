---
id: ADR-098
title: Close the post-flip vault-queue read-modify-write lost-update class by routing the queue/claim RMW writers through the _vault_write CAS channel under a bounded fail-visible retry, and teach VWS-1 to recognize the CAS channel
date: 2026-06-03
slice: slice-109-add-post-flip-vault-conflict-safety
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-098: Post-flip vault-queue CAS write-safety (the `_vault_write`-lock substitute for PCR's git-merge queue reconciliation)

## Context

The external-shared-vault initiative ([[ADR-065]] → [[ADR-085]]) relocates the vault to a shared, **untracked** external store. Slices 094/095/097 closed all three R-32 write-safety sub-classes and slice-098 made the 3 git-coupled tools flip-ready. The R-32 register and [[ADR-089]] both name one explicit remaining pre-move residual: **"wire the post-flip PCR conflict-resolution replacement — the `_vault_write`-lock substitute."** This ADR **partially discharges** that [[ADR-089]] §Residual item — it wires the *write-time replacement* (the queue/claim RMW writers now reconcile concurrent writes via the `_vault_write` CAS lock instead of git-merge-time PCR). The remaining halves — the post-flip `/commit-slice --merge` RETIRE no-op and a distinct PCR RETIRE signal — stay ADR-089's flip-slice residual. `supersedes: null` is retained (this ADR *narrows*, it does not reverse, ADR-089).

Concretely: today, concurrent parallel-slice writes to `architecture/slice-queue.md` (pick-log appends via `record_pick`, PSQ-2 claim/release, top-10 regen via `write_slice_queue`) are read-modify-write cycles. They write via the non-CAS whole-file `safe_write_text`, whose own docstring flags the caller's RMW window as a **"documented flip-residual (B2), not closed here"** (`tools/slice_queue_writer.py:937`, `tools/slice_queue_claim.py:537`). Pre-flip this is safe *only* because the queue file is git-tracked: two parallel `/commit-slice --merge` rebases collide loudly and PCR reconciles them at git-merge time. **Post-flip the queue file is untracked → there is no git merge and no PCR** — so a stale-base whole-file write silently clobbers a concurrent writer's contribution (the R-32 lost-update class, live).

The CAS channel that closes exactly this — read-under-lock + EOL-normalized base-compare + EOL-preserving write, raising `StaleVaultBaseError` on a stale base — already exists (`_vault_write.safe_rewrite_text`, [[ADR-088]]/slice-097), but only the *skill-driven* RMW writers were routed through it; the *Python tool* queue writers still use `safe_write_text`.

A second, smaller gap: VWS-1's recognized routed-channel set `_ROUTED_FUNCS` (`tools/vault_write_safety_audit.py:114`) is `{safe_write_text, safe_append_text}` — it does **not** include `safe_rewrite_text`. Routing the queue writers through CAS without teaching VWS-1 would make the new write sites read as *un-routed* → a false VWS-1 violation.

This slice does NOT flip the default (vault stays `architecture/`, git-tracked). It builds + proves the write-time replacement before the irreversible move (capability-without-flip).

## Options considered

1. **Leave the queue writers on `safe_write_text`; rely on the flip slice to fix it** — Con: leaves R-32's last load-bearing residual (silent lost-update on the shared mutable queue) un-closed and un-proven going into the irreversible physical move; the flip slice would then carry both the move AND an unproven concurrency mechanism. **Rejected** — the whole value of a capability-without-flip cut is to prove the mechanism *before* the move.
2. **Hold a lock across the whole read-modify-write** (acquire the sidecar lock, read, compose, write, release) — Con: the compose step for `write_slice_queue` includes a graphify blast-radius subprocess + claim parse; holding an exclusive cross-process lock across that widens the critical section and risks lock-timeout under contention; and it does not match the shipped CAS protocol the rest of the vault uses. **Rejected** — CAS (short lock only at the compare+write) is the established, lower-contention pattern (ADR-088).
3. **Route the 3 queue/claim RMW writers through `safe_rewrite_text` under a bounded fail-visible retry; add `safe_rewrite_text` to VWS-1's `_ROUTED_FUNCS`** (chosen) — capture the raw base bytes at read; compose; CAS-write; on `StaleVaultBaseError` re-read + re-compose + retry (bounded ≈5); on exhaustion RAISE. Pro: reuses the shipped, dual-Critic-ratified CAS channel; lost-update-safe at write-time with no git dependency; byte-identical on the no-flip default (LF tool-written queue → EOL-preserving CAS matches `safe_write_text` LF); MEPD-1-clean (no new rule); the VWS-1 extension keeps the audit fail-closed against future un-routed writes.

## Decision

Adopt option 3.

- **Route the three queue/claim read-modify-write writers** — `slice_queue_writer.write_slice_queue`, `slice_queue_writer.record_pick`, and `slice_queue_claim`'s claim/release rewrite (the `main` path, via the new `_cas_rewrite` helper; the legacy `_atomic_write_text` wrapper is retained only for its direct-helper test) — through `_vault_write.safe_rewrite_text`. Capture the raw base bytes at read time and pass them as `expected_base`. The read→compose→CAS-write cycle (including `record_pick`'s idempotency scan and `write_slice_queue`'s claim-preservation parse) runs **inside a bounded retry loop** (≈5 attempts, ADR-088 precedent): `StaleVaultBaseError` → re-read + re-compose + retry; **exhaustion RAISES** a typed error. Never a silent fall-back to lost-update-prone `safe_write_text`.
- **Teach VWS-1**: add `"safe_rewrite_text"` to `_ROUTED_FUNCS`; the recognized set becomes a pinned, closed `{safe_write_text, safe_append_text, safe_rewrite_text}` (membership pin test extended) so the new sites pass and a future un-routed vault write still fails fail-closed. **(slice-109 m1 + code-review M1)** `safe_rewrite_text` is recognized as routed only with an `expected_base=` that does not RESOLVE to a constant — a literal `b""` OR a module-level name bound to one (`expected_base=_EMPTY`) is flagged as an un-routed CAS-defeat (`_is_routed_call` resolves the name via the audit's `module_consts`); a dynamic/local base stays routed.
- The retry loop MAY be a thin shared helper in `_vault_write` (so the `safe_rewrite_text` write site VWS-1 inspects stays inside the writer module) OR inlined at the 3 call sites calling `safe_rewrite_text` directly — Builder's choice at plan time; both reach the recognized channel.

## Consequences

- The R-32 lost-update residual on the shared mutable queue is closed at **write-time** — the reconciliation PCR did at git-merge time is now done by CAS, so the flip can remove git tracking of the queue without reopening silent corruption.
- The **no-flip safety contract holds** with the LF precondition **enforced, not assumed** (B1, executed by the Critic): `safe_rewrite_text` is EOL-PRESERVING while `safe_write_text` is LF-faithful, so byte-identity holds only while `slice-queue.md` is LF on disk — which is NOT invariant (`.gitattributes` does not normalize `architecture/**`; a `core.autocrlf` checkout could introduce CRLF). This slice therefore adds `architecture/slice-queue.md eol=lf` to `.gitattributes` (the queue is a tool-owned regenerable artifact, legitimately LF-canonical — unlike the hand-edited CRLF aggregates `safe_rewrite_text` preserves), making the LF precondition enforced. Byte-identity to `safe_write_text` then holds on the no-flip default; on a stray-CRLF on-disk edge the routed writer preserves CRLF (a documented, test-pinned divergence). Pinned by an LF byte-identity test **and** a CRLF-on-disk behavior test (AC4).
- The post-flip `/commit-slice --merge` **RETIRE no-op** + a distinct PCR RETIRE signal (today `_retire_if_vault_external` returns an indistinguishable `action="STOP"`) remain the **flip slice's** job, per ADR-089's own division of labor — out of scope here.
- VWS-1 now recognizes all three lock-safe channels; the closed pinned set prevents the recognition extension from silently widening into a hole.

## Reversibility

**cheap.** Pure call-site routing (`safe_write_text` → `safe_rewrite_text` + a base-capture + retry loop) + one frozenset membership addition + its pin test. No data model, schema, contract, or identity lock; no migration; no external state. Reverting is a code revert.
