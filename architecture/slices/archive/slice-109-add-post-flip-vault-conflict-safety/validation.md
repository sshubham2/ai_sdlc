# Validation: Slice 109 add-post-flip-vault-conflict-safety

**Date**: 2026-06-04
**Result**: PASS

For this CLI / methodology-tooling slice the "real environment" is the actual tools + tests run against the REAL repo corpus — including a real `multiprocessing(spawn)` concurrency proof (genuine OS processes contending on a real on-disk file, not mocks/threads). Evidence below is executed commands + output.

## Per-criterion results

### AC1: Concurrent RMW to slice-queue.md is lost-update-safe at write-time without git/PCR (CAS routing + bounded retry)
- **Status**: PASS
- **Evidence**: `pytest test_post_flip_queue_cas_concurrency.py test_post_flip_queue_cas.py` — 6 + 8 PASS. `test_concurrent_queue_rmw_zero_lost` / `test_concurrent_record_pick_distinct_slices_both_survive` / `test_concurrent_mutation_triggers_retry_both_land`: N≥4 real spawn workers, ALL pick lines survive (0 lost). `test_record_pick_cas_retry_on_stale_base` confirms the retry fires; `test_record_pick_retry_exhaustion_raises` confirms exhaustion RAISES (fail-visible). Structural pin `test_queue_writers_route_through_cas_channel`: the 3 RMW writers call `safe_rewrite_text(..., expected_base=…)`, not `safe_write_text`.
- **Notes**: graphify hoisted out of the retry loop (code-Critic verified no correctness regression); fail-visibility scoped to the non-regenerable provenance writer (M-add-1).

### AC2: Barrier-synchronized N≥4 concurrency proof, non-vacuous by mutation (record_pick + claim + regen)
- **Status**: PASS
- **Evidence**: `test_concurrent_mixed_writers_all_land` (record_pick + claim + write_slice_queue regen contend under one `mp.Barrier(3)` → all three effects survive). `test_concurrent_first_pick_empty_base_both_create` (empty-base create-race, 0 lost, exactly one pick-log section). **Non-vacuity**: `test_mutation_plain_write_loses_update` — the no-CAS `safe_write_text` arm under the SAME barrier LOSES ≥1 (the assert `survivors < N` holds), proving the CAS proof is not vacuous (AP-5 + AP-6).

### AC3: VWS-1 recognizes safe_rewrite_text as routed (non-constant base) + flags the CAS-defeat
- **Status**: PASS
- **Evidence**: `$PY -m tools.vault_write_safety_audit` → "clean. 48 tool(s) scanned; 6 vault write op(s) (7 routed call(s))" — the real writers (local `base`) stay routed. `test_safe_rewrite_text_recognized_as_routed` (non-constant → routed), `test_safe_rewrite_text_degenerate_base_flagged` (literal `b""` → violation), `test_safe_rewrite_text_name_bound_constant_base_flagged` (module-const name `b""` → violation, code-review M1), `test_routed_funcs_pinned` (set pinned closed). All PASS.

### AC4: Capability-without-flip + byte-identity enforced (LF) with CRLF divergence pinned
- **Status**: PASS
- **Evidence**: `tools/_vault_paths.py` default unchanged (`Path("architecture")`); FULL SUITE **1564 passed, 2 skipped, 0 failed** (no behavior change). `test_no_flip_queue_output_byte_identical_lf` (CAS output == safe_write_text on LF). `test_crlf_on_disk_queue_behavior_pinned` (EXECUTED — CRLF on-disk preserved, the documented B1 divergence). `.gitattributes architecture/slice-queue.md eol=lf` enforces the LF precondition. `test_cas_rewrite_crlf_release_unclaimed_is_noop` (code-review m3).
- **Notes**: 102 pre-existing queue/psq/claim tests + PSQ-1/PSQ-2 byte-equal round-trips all still PASS — no regression to the writers' output.

### AC5: R-32 register + shippability catalog updated; physical move the sole remaining retirement precondition
- **Status**: PASS
- **Evidence**: `shippability.md` row #115 present + executed by the catalog runner (PASS). `risk-register.md` R-32 carries the slice-109 residual-closed paragraph, stays `mitigating` (STP-1 green). `test_shippability_catalog_pins_post_flip_cas` PASS (RPCD-1). Shippability catalog: **114 row(s), 114 PASS, 0 FAIL**.

## Multi-instance validation
- **Required?**: yes — the slice's whole purpose is cross-PROCESS concurrent-write safety (the multi-instance analog of multi-device).
- **Result**: PASS
- **Evidence**: the concurrency proofs use `multiprocessing.get_context("spawn")` — N≥4 GENUINE OS processes (not threads) released by a shared `mp.Barrier`, contending on one real on-disk queue file. Single-process passing alone would NOT prove this; the barrier-synced multi-process proof is the required multi-instance check, and it is non-vacuous (the no-CAS control loses).

## Layered safety checks (VAL-1)
- **Result**: PASS — Layer A (credential scan): 0 secrets; Layer B (dependency hallucination): 0 findings (imports resolve via stdlib + the `tools`/`tests` roots).

## Shippability regression
- **Result**: PASS — pre-gates SCMD-1 / PTFCD-1 / SVW-1 all exit 0; catalog runner: 114/114 PASS, 0 FAIL.

## Reality surprises
- None at validation time. The one code-level edge (the VWS-1 name-indirection CAS-defeat) was surfaced by `/code-review` and closed in-slice before validation.
