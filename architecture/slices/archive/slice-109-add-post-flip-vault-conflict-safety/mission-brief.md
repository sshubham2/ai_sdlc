# Slice 109: add-post-flip-vault-conflict-safety

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (ADVANCES — closes the last open residual on the path to retirement: "wire the post-flip PCR conflict-resolution replacement / the `_vault_write`-lock substitute"). R-32 itself retires only at the physical move (a later flip slice), so this slice narrows, it does not retire.
**Test-first**: true  (per TF-1 — the CAS routing + the lost-update concurrency proof are deterministic and naturally testable, mirroring the slice-094/095/097 write-safety proofs)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Pre-flip, concurrent parallel-slice read-modify-write to `architecture/slice-queue.md` (pick-log appends, PSQ-2 claim/release, top-10 regenerations) is reconciled at **git-merge time** by `parallel_conflict_resolver` (PCR) when two slices' `/commit-slice --merge` rebase onto the same queue file. After the external-vault flip the queue file is **untracked** → there is no git merge and PCR's git-rebase vault-conflict role retires (it already STOPs via the `vault_is_external` guard, [[decisions/ADR-089]]). This slice wires the **write-time replacement** so that reconciliation is not lost: route the contended read-modify-write queue/claim writers — which today use the non-CAS whole-file `safe_write_text` and carry an explicitly-documented "flip-residual (B2)" RMW window (`slice_queue_writer.py:937`) — through the already-shipped CAS channel (`_vault_write.safe_rewrite_text` / [[decisions/ADR-088]]) under a bounded, fail-visible retry, so concurrent regenerations are **lost-update-safe at write-time**. **Capability-without-flip**: the `_vault_paths` default stays `architecture/` (git-tracked), so R-32's load-bearing concurrent-write gate is closed and *proven* before the irreversible physical move — mirroring how slices 093/100/102 built capability before flipping.

## Acceptance criteria

1. Concurrent read-modify-write to `slice-queue.md` (pick-log append, PSQ-2 claim/release, top-10 regen) is **lost-update-safe at write-time without relying on git/PCR reconciliation** — a writer that read a now-stale base is detected and retried, never silently clobbered. (Route `slice_queue_writer.write_slice_queue` + `record_pick` and `slice_queue_claim`'s claim/release RMW through the shipped CAS channel `_vault_write.safe_rewrite_text` under a bounded retry, replacing non-CAS `safe_write_text`; exact retry-bound settled at `/design-slice`.)
2. A **barrier-synchronized (`mp.Barrier`) multiprocessing-spawn** concurrency proof shows N≥4 parallel processes each applying a distinct queue mutation — the set MUST include `record_pick` (concurrent picks of *distinct* slices), a PSQ-2 claim, and a top-10 regen — against one shared queue file all land with **zero lost updates**, and is **non-vacuous by mutation** (AP-5 + AP-6): bypassing CAS (revert to plain `safe_write_text`) makes the proof FAIL with a detected lost update.
3. VWS-1 (`tools/vault_write_safety_audit.py`) **recognizes `safe_rewrite_text` as a routed safe channel** (added to `_ROUTED_FUNCS`, the membership pin test updated), so the newly CAS-routed write sites pass VWS-1 and a future un-routed vault write stays un-mergeable.
4. **Capability-without-flip invariant holds**: `tools/_vault_paths.py` default stays `Path("architecture")`; the full methodology suite + shippability catalog pass unchanged; the queue writers' on-disk output is **byte-for-byte identical on the no-flip default with the LF precondition ENFORCED** (this slice adds `architecture/slice-queue.md eol=lf` to `.gitattributes` — `safe_rewrite_text` is EOL-preserving, so byte-identity to LF-faithful `safe_write_text` holds only while the queue is LF on disk, which `.gitattributes` now guarantees; a stray-CRLF on-disk edge preserves CRLF — a documented, test-pinned divergence, per Critic B1); PCR's pre-flip git-rebase SOFT/VAULT_CLAIM resolution (the tracked-vault path) is unchanged. Fully reversible (a code revert; no migration, no external state).
5. The R-32 register entry + `architecture/shippability.md` are updated to record this residual closed ("write-time CAS replacement for PCR's git-merge queue reconciliation wired via `_vault_write.safe_rewrite_text`"), leaving the **physical move** as the sole remaining R-32 retirement precondition; R-32 status stays `mitigating`.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0 — paths/function names are a starting sketch; `/design-slice` firms them up)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_post_flip_queue_cas.py | test_queue_writers_route_through_cas_channel | PASSING |
| 1 | unit | tests/methodology/test_post_flip_queue_cas.py | test_record_pick_cas_retry_on_stale_base | PASSING |
| 1 | unit | tests/methodology/test_post_flip_queue_cas.py | test_record_pick_retry_exhaustion_raises | PASSING |
| 1 | unit | tests/methodology/test_post_flip_queue_cas.py | test_cas_rewrite_crlf_release_unclaimed_is_noop | PASSING |
| 1 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_concurrent_mutation_triggers_retry_both_land | PASSING |
| 2 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_concurrent_queue_rmw_zero_lost | PASSING |
| 2 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_concurrent_record_pick_distinct_slices_both_survive | PASSING |
| 2 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_concurrent_first_pick_empty_base_both_create | PASSING |
| 2 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_concurrent_mixed_writers_all_land | PASSING |
| 2 | concurrency | tests/methodology/test_post_flip_queue_cas_concurrency.py | test_mutation_plain_write_loses_update | PASSING |
| 3 | unit | tests/methodology/test_vault_write_safety_audit.py | test_safe_rewrite_text_recognized_as_routed | PASSING |
| 3 | unit | tests/methodology/test_vault_write_safety_audit.py | test_safe_rewrite_text_degenerate_base_flagged | PASSING |
| 3 | unit | tests/methodology/test_vault_write_safety_audit.py | test_safe_rewrite_text_name_bound_constant_base_flagged | PASSING |
| 3 | unit | tests/methodology/test_vault_write_safety_audit.py | test_routed_funcs_pinned | PASSING |
| 4 | regression | tests/methodology/test_post_flip_queue_cas.py | test_no_flip_queue_output_byte_identical_lf | PASSING |
| 4 | regression | tests/methodology/test_post_flip_queue_cas.py | test_crlf_on_disk_queue_behavior_pinned | PASSING |
| 5 | unit | tests/methodology/test_post_flip_queue_cas.py | test_shippability_catalog_pins_post_flip_cas | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | CAS-routed RMW + retry | AST/code assertion: the queue/claim RMW writers call `safe_rewrite_text`; a stale base raises the retryable `StaleVaultBaseError` → bounded re-read+re-apply+retry, not clobber |
| 2 | Lost-update-free under contention | `python -m pytest tests/methodology/test_post_flip_queue_cas_concurrency.py` — N≥4 `mp.Barrier`-synced spawn workers all land (0 lost); the no-CAS mutation control loses ≥1 (proof non-vacuous) |
| 3 | VWS-1 recognizes the CAS channel | `$PY -m tools.vault_write_safety_audit` clean with the routed writers; pin test asserts `safe_rewrite_text ∈ _ROUTED_FUNCS` |
| 4 | No-flip byte-identity | Full methodology suite + shippability green on the `architecture/` default; queue regen output diffed byte-for-byte vs pre-slice baseline (unchanged) |
| 5 | Residual recorded | `risk-register.md` R-32 + `shippability.md` show the residual closed with the physical move named as the sole remaining precondition; RR-1 + shippability audits clean |

## Must-not-defer

- [ ] **CAS retry is bounded + fail-visible** — `StaleVaultBaseError` triggers a bounded re-read+re-apply+retry (≈5, per the ADR-088 `vault_edit rewrite` precedent); exhaustion **RAISES** (never a silent fall-back to last-writer-wins `safe_write_text`). **Fail-visibility is scoped to the provenance writer (Critic M-add-1)**: `record_pick`'s exhaustion-raise propagates loudly (it is un-wrapped at `skills/slice/SKILL.md` Step 6.5, and the pick-log is NON-regenerable provenance — loud is mandatory); `write_slice_queue`'s exhaustion-raise is intentionally caught by Step 6.5's pre-existing ADR-064 `try/except` non-fatal wrapper (the `## Candidates` list IS regenerable next pick, so a swallowed regen is acceptable — NOT the forbidden silent lost-update). The two writers' divergent fail-visibility is by design, not an oversight.
- [ ] **Byte-faithfulness ENFORCED, not assumed** (Critic B1) — `safe_rewrite_text` is EOL-preserving while `safe_write_text` is LF-faithful; byte-identity holds only while the queue is LF on disk, which `.gitattributes` does NOT currently guarantee for `architecture/**`. Add `architecture/slice-queue.md eol=lf` to `.gitattributes` to enforce the LF precondition; pin both the LF byte-identity AND the CRLF-on-disk behavior by an *executed* test (APED-1 — do not reason "tool-written LF").
- [ ] **Single-read base invariant** (Critic M1) — `expected_base` MUST come from the same `read_bytes()` whose decode feeds the composition (one read per retry attempt, not `read_bytes()` for base + a separate `read_text()` that can straddle a concurrent write); the full compose re-runs on the fresh base inside each retry; graphify `active_blasts` is hoisted OUT of the retry loop (independent of queue bytes).
- [ ] **Non-vacuity by mutation** (AP-5) — the concurrency proof must FAIL when CAS is bypassed; a passing-on-already-safe-inputs test proves nothing.
- [ ] **Barrier-synchronized contention** (AP-6) — workers start on an `mp.Barrier`; un-barriered spawn gives a false-negative "0 loss".
- [ ] **VWS-1 recognized-channel + pin test** — adding `safe_rewrite_text` to `_ROUTED_FUNCS` must be pinned so a future un-routed vault write still fails the audit (no widening the hole).
- [ ] **RPCD-1 / SCPD-1 propagation** — any new/changed gate or test propagates its consumer refs into `architecture/shippability.md`.

## Out of scope

- The post-flip `/commit-slice --merge` **RETIRE no-op** + the **distinct PCR RETIRE signal** (today `_retire_if_vault_external` returns an indistinguishable `action="STOP"`) — **deferred to the flip slice** per [[decisions/ADR-089]], which assigns the commit-slice RETIRE handling there and lets it be tested against the *real* external path (not a simulation). (Scope-narrowed from this slice at `/design-slice` per AP-17.)
- The **physical move** of `architecture/` + `diagnose-out/` to the external store, the `git rm --cached` untrack, and flipping the `_vault_paths` default — the next/later flip slice (R-32 retires there, not here).
- The **318-site prose rewrite** (slice-107 inventory) and the **154 test-update-at-flip** sites (slice-102 inventory).
- `stranded_slice_audit` / `pulse_worktree_resolver` external-store *recovery reads* — ADR-089 names these as separate flip-slice concerns.
- `architecture/shippability.md`'s own writers — already append-safe via the slice-095 `vault_edit append` channel (not an RMW); not re-litigated here.

## Dependencies

- Prior slices: [[slice-097-harden-skill-driven-vault-rewrites]] — ships the CAS channel (`_vault_write.safe_rewrite_text` + `StaleVaultBaseError`); [[slice-098-route-or-retire-git-coupled-vault-tools]] — ships PCR's `vault_is_external` RETIRE guard (ADR-089) + names this residual; [[slice-094-enforce-python-vault-write-safety]] — byte-faithful `_vault_write` writers + VWS-1 (`_ROUTED_FUNCS`).
- Vault refs: [[decisions/ADR-085]] (concurrent-write-safety contract), [[decisions/ADR-088]] (CAS), [[decisions/ADR-089]] (route/retire git-coupled tools + the explicit "wire the `_vault_write`-lock substitute" residual), [[decisions/ADR-098]] (this slice).
- Risk register: [[risk-register#R-32]] — this slice closes its last pre-move residual.
- Tools: `tools/_vault_write.py`, `tools/slice_queue_writer.py`, `tools/slice_queue_claim.py`, `tools/vault_write_safety_audit.py`.

## Mid-slice smoke gate

At ~50% of build (CAS routing in place, concurrency test written), run:
```
$PY -m pytest tests/methodology/test_post_flip_queue_cas_concurrency.py tests/methodology/test_vault_safe_write.py -q
```
Expected: all parallel workers land with 0 lost updates AND the existing `_vault_write` suite stays green. If the no-CAS mutation control does NOT lose an update, the proof is vacuous — STOP and fix the barrier/contention before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes (DCE-1 trace present)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
