# Code Review: Slice 109 add-post-flip-vault-conflict-safety

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths), worktree base `aef3e7ce`
**Date**: 2026-06-04
**Result**: FINDINGS (advisory in v1 — does not block /validate-slice)

## Summary
The implementation is solid; core correctness holds under empirical attack: single-read base invariant confirmed, graphify-hoist is NOT a correctness regression (only graphify moved out; queue-byte-dependent reads stayed inside the loop), same-slice concurrent picks collapse to one line (no double-append), regen-landing-last preserves a concurrent pick + claim, non-vacuity control reliably loses, CRLF EOL preserved. All 47 slice tests pass; VWS-1 clean, no double-count. **No blockers.** 1 Major (constant-base CAS-defeat check has a name-indirection bypass that overstates the design's guarantee), 3 Minors.

## Changed files (in-scope)
- tools/slice_queue_writer.py
- tools/slice_queue_claim.py
- tools/vault_write_safety_audit.py
- .gitattributes
- tests/methodology/test_vault_write_safety_audit.py
- tests/methodology/test_post_flip_queue_cas.py (NEW)
- tests/methodology/test_post_flip_queue_cas_concurrency.py (NEW)

## Findings

### Blockers
None. CAS retry loops bounded + fail-visible; single-read invariant holds; no infinite-loop or swallowed-StaleVaultBaseError path; no code contradicts an ACCEPTED ADR.

### Majors

#### M1: VWS-1 constant-base CAS-defeat check is bypassed by a name-bound `b""` — overstates the design's guarantee
- **Claim under review**: `tools/vault_write_safety_audit.py` `_is_routed_call` treats `safe_rewrite_text(..., expected_base=X)` as routed unless `isinstance(kw.value, ast.Constant)`. design.md + ADR-098 claim "a literal base (e.g. `b""`) is a CAS-defeat, so it is NOT auto-cleaned" — stated unconditionally.
- **Issue**: Only a *literal* `ast.Constant` is caught. `expected_base=_NAME` where `_NAME = b""` at module level is an `ast.Name` → passes as routed → auto-cleaned. The CAS-defeat survives one level of name indirection (verified: `expected_base=_EMPTY` → `_is_routed_call == True`). The audit already owns name→constant resolution (`_resolve_target` / `_collect_consts` / `scope_cache`), so the capability exists but isn't applied in `_is_routed_call`. Major not Blocker: strictly tighter than pre-slice state, requires a contrived named-empty-base, and the literal case the pin test exercises IS caught.
- **Proposed fix**: resolve a `ast.Name` `expected_base` against scope/module-consts before deciding (reuse `_collect_consts`/`_func_scope`), OR narrow the docstring + design claim to "a *literal*-constant base" + add a pin test executing the `expected_base=_NAME` variant as a documented residual (APED-1).

### Minors

#### m1: `_atomic_write_text` is now production-orphaned stale scaffolding
- `tools/slice_queue_claim.py` `_atomic_write_text` has zero production callers after the refactor (all 3 `main()` paths route through `_cas_rewrite`); only `test_psq_2_claim_machinery.py:251` references it. Its docstring "callers are unchanged" is now stale; `safe_write_text` import retained solely for it. Fowler dead-pass-through smell.
- **Proposed fix**: (b, cheapest) update the docstring to note it's retained for the direct-helper test + slice-094 byte-equality anchor, not a production path; OR (a) delete + retarget the test (widens scope). Log for the slice-061 AI-bloat pass if not done here.

#### m2: barrier-synced test relies on `barrier.wait()` with no per-call timeout — CPython #123899 (Web-known)
- `tests/methodology/test_post_flip_queue_cas_concurrency.py` workers call `barrier.wait()` (no timeout). Per CPython #123899 (open, Windows-repro), a party dying *after* entering the barrier wedges the survivors; the test's `p.join(120)` + `assert not p.is_alive()` converts that to a LOUD (but slow/opaque) failure. Robustness/diagnosability note, not a correctness hole; ran 8× zero-flake.
- **Proposed fix**: `barrier.wait(timeout=<short>)` + let `BrokenBarrierError` propagate (dead sibling aborts promptly instead of 120s wedge); split the assert message to name the suspected cause. Optional.

#### m3: `_cas_rewrite` no-op detection on CRLF — verified benign, worth a pin
- `tools/slice_queue_claim.py` `if not always_write and new_text == current` compares raw (CRLF-possible) `current` vs LF-normalized `compose` output. The one risky case (release-of-unclaimed) is saved by `apply_release` returning the raw original text early (line ~393) → `new_text == current` holds → correct no-op. Verified empirically (CRLF release-of-unclaimed → `wrote=False`, bytes unchanged). Relies on `apply_release`'s raw early-return; a future change there would silently flip a no-op into a spurious write. `.gitattributes eol=lf` makes this unreachable on the canonical path.
- **Proposed fix**: add a one-line pin test (CRLF queue, release-of-unclaimed → `wrote=False`, "already unclaimed").

## Dimensions checked
- [x] Unfounded assumptions — M1 (constant-base claim overstated; name-bound bypass, executed). No phantom imports (StaleVaultBaseError + safe_rewrite_text exist).
- [x] Missing edge cases — none beyond findings; empirically verified create-race, same-slice idempotency, CRLF preservation, regen-last reconciliation, exhaustion-raises.
- [x] Over-engineering — m1 (orphaned `_atomic_write_text`). `_CAS_RETRIES=5` justified by ADR-088.
- [x] Under-engineering — none; every AC has a delivering code element + test; fail-visibility asymmetry matches must-not-defer scoping.
- [x] Contract gaps — M1 (audit's advertised guarantee broader than implementation). `_cas_rewrite` contract docstring-complete; `compose` param untyped (private helper, minor).
- [x] Security — none. No new auth/input-boundary/injection; cross-process safety is OS lock + CAS, not authz. No secrets, no shell=True/eval/exec.
- [x] Drift from vault — none material. `_vault_write.py` unchanged (design permits inlining); `_cas_rewrite` in slice_queue_claim.py satisfies VWS-1 (scans all tools/*.py, ran clean). MEPD-1 EXCLUDE holds; R-32 stays mitigating.
- [x] Web-known issues — m2 (multiprocessing.Barrier no-timeout-on-death, CPython #123899), mitigated by join+is_alive.
- [x] Cross-cutting conformance — RSAD-1 (own writers pass own VWS-1 + concurrency proof); APED-1 (CRLF + degenerate-base executed; the name-indirection variant is the M1 APED-1 gap); EOL-DRIFT-1 (no new == byte-compare on .md).

## Builder dispositions (advisory v1 — addressed in-slice, 2026-06-04)

All four findings addressed this round (code-review is advisory in v1, but these were cheap and improve correctness/honesty):

| ID | Disposition | Action |
|----|-------------|--------|
| M1 | FIXED | `_is_routed_call(call, module_consts)` now RESOLVES a name-bound `expected_base` against module constants — a literal `b""` OR `expected_base=_NAME` (`_NAME = b""`) is flagged; a dynamic/local base stays routed. design.md + ADR-098 narrowed→corrected. New pin `test_safe_rewrite_text_name_bound_constant_base_flagged` (EXECUTED). VWS-1 real corpus stays clean (real writers use local `base`). |
| m1 | FIXED | `_atomic_write_text` docstring corrected — now states it is PRODUCTION-ORPHANED (retained only for its direct-helper test + slice-094 byte anchor); full removal deferred to the slice-061 AI-bloat pass. |
| m2 | FIXED | concurrency-test workers now `barrier.wait(_BARRIER_TIMEOUT=30)` so a sibling dying after entering the barrier (CPython #123899) aborts promptly instead of a 120s wedge. Happy path unaffected. |
| m3 | FIXED | new pin `test_cas_rewrite_crlf_release_unclaimed_is_noop` locks the CRLF release-of-unclaimed no-op (the dependency on `apply_release`'s raw early-return). |

Re-verified: VWS-1 audit clean (7 routed); affected suites 49/49 PASS; full suite re-run green.
