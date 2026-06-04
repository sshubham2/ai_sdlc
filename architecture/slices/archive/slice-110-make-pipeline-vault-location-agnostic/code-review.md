# Code Review: Slice 110 make-pipeline-vault-location-agnostic

**code-Critic reviewed**: slice diff vs default branch (merge-base `803fd6f`), filtered to in-scope paths; Phase-1-only ship (AC1+AC5)
**Date**: 2026-06-04
**Result**: FINDINGS (minors only — no blockers, no majors)

> **Disposition (Builder, 2026-06-04):** all 3 minors ADDRESSED in-slice (advisory in v1, but cheap + on the newly-introduced shared helper, so fixed at introduction):
> - **m1** — `tests/_vault_isolation.py` `pin_vault_root` docstring gained a **NON-VACUITY SCOPE** note stating the step-4 assert covers only the `VAULT_ROOT`-binding axis and that derived-completeness has no in-helper guard (its sole proof is the seeded flip-sim full-suite). ADR-101 §Build-time refinement already states the same. (Optional per-derived loud-assert hardening left to a Phase-2/future slice, as the agent recommended — a no-op `derived` under the default suite would false-fail.)
> - **m2** — `tests/skills/pulse/test_cli.py` + `tests/methodology/test_utf8_stdout_regression.py` now strip the sim var via `vi.subprocess_env(base=env)` instead of an inline `env.pop(...)` (the new seam gets its 2 missed consumers).
> - **m3** — `pin_vault_root` now skips re-recording `tools._vault_paths` in the consumer loop (`if mod is _vp: changed = True; continue`) — no duplicate `saved_attrs` entry if a caller lists `_vault_paths` as a consumer; non-vacuity semantics preserved.
> Re-verified: 136 passed under both default AND flip-sim after the fixes.

## Summary
A genuinely clean Phase-1 cut. The setattr-pin mechanism is correct, leak-free, and identity-safe; the per-file consumer + `derived` pin sets match the real call-graph closure for every family traced (PCR, stranded, single-consumer audits, the 8-audit gate-CLI test); and the external/flip-behavior tests (`test_slice_098_vault_routing`) are correctly NOT neutralized. The code-Critic independently confirmed green under both the in-tree default AND a seeded external flip-sim, and empirically proved the `derived` re-derive is load-bearing (not vacuous). Findings were three minors about latent fragility in the non-vacuity guarantee and DRY consistency — none block; all addressed.

## Changed files (in-scope)
```
tests/_vault_isolation.py
tests/conftest.py
tests/methodology/test_vault_isolation.py
tests/methodology/test_drift_check_audit.py
tests/methodology/test_cross_spec_parity_audit.py
tests/methodology/test_supersede_audit.py
tests/methodology/test_build_checks_integrity.py
tests/methodology/test_state_transition_pin_audit.py
tests/methodology/test_critique_review_prerequisite_audit.py
tests/methodology/test_project_frame_synth.py
tests/methodology/test_psq_2_claim_machinery.py
tests/methodology/test_slice_098_vault_routing.py
tests/methodology/test_vault_flip_readiness_audit.py
tests/methodology/test_vault_root_constant.py
tests/methodology/test_gate_audit_cli_exit_codes.py
tests/methodology/test_utf8_stdout_regression.py
tests/methodology/test_stranded_slice_audit.py
tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py
tests/methodology/test_pcr_2a_vault_claim_resolver.py
tests/methodology/test_pcr_2a_clock_skew_winner.py
tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py
tests/methodology/test_pcr_2b_hard_conflict_dispatch.py
tests/methodology/test_pcr_2b_mixed_routes_to_hard.py
tests/methodology/test_parallel_conflict_resolution_log_hard.py
tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py
tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py
tests/bugs/test_stranded_audit_branchless_slice_blindspot.py
tests/skills/parallel_conflict_resolver/test_audit_log.py
tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py
tests/skills/pulse/test_cli.py
tests/skills/slice/test_slice_queue_output.py
architecture/slices/slice-110-.../build-log.md
architecture/slices/slice-110-.../superseded-flip-design/ (prose, low priority)
```

## Findings

### Blockers (advisory in v1)
None.

### Majors
None.

### Minors

#### m1: The non-vacuity assert cannot detect a missing `derived` entry — only the flip-sim full-suite can — **ADDRESSED (doc)**
- **Claim under review**: `tests/_vault_isolation.py` — `changed` is set True only when a consumer binds `VAULT_ROOT`; the `assert changed` is the entire structural non-vacuity guarantee; the `derived` loop is never checked for completeness.
- **Issue**: code-Critic empirically confirmed that pinning a consumer WITHOUT its `derived` entry leaves the frozen constant pointed at the external store with NO error from the helper — the seeded flip-sim full-suite is the actual backstop. Latent trap for FUTURE tests/constants once the flip-sim isn't being re-run on every change. Not a present defect (suite is green).
- **Fix applied**: docstring NON-VACUITY SCOPE note added (helper covers only the `VAULT_ROOT`-binding axis; derived-completeness proof is the seeded flip-sim suite). ADR-101 §Build-time refinement already states this. Optional loud-per-derived assert deferred (would false-fail on a default-suite no-op derive).

#### m2: Two subprocess tests hand-rolled the env-strip instead of `subprocess_env` (DRY) — **ADDRESSED**
- **Claim under review**: `tests/skills/pulse/test_cli.py` + `tests/methodology/test_utf8_stdout_regression.py` stripped `AI_SDLC_VAULT_ROOT` inline rather than via the new `vi.subprocess_env(...)`.
- **Fix applied**: both now call `env = vi.subprocess_env(base=env)`. (`test_slice_098_vault_routing` correctly still sets the external root explicitly — opposite intent — and is unchanged.)

#### m3: `pin_vault_root` double-records `_vault_paths` if listed as a consumer (harmless/latent) — **ADDRESSED**
- **Claim under review**: the helper unconditionally pins `_vault_paths` then would pin it again if a caller lists it in `*consumers` (correct-by-LIFO-luck restore).
- **Fix applied**: consumer loop now `if mod is _vp: changed = True; continue` — no duplicate `saved_attrs` record; non-vacuity preserved.

## Dimensions checked
- [x] Unfounded assumptions — none. `==15` count-pin verified unaffected (new fixture is non-`test_`); PCR-vs-stranded consumer asymmetry verified correct (pcr has no pwr dep; stranded reaches `_pwr.VAULT_ROOT` via `classify_worktree_state`); no phantom imports.
- [x] Missing edge cases — covered (empty consumers → ValueError; non-consumer → AssertionError; env-unset vs env-set restore; subprocess inherit-strip). The one un-loud edge (missing `derived`) filed as m1 (now documented).
- [x] Over-engineering — none. `autouse_pin` justified (9-file PCR family); each helper has ≥1 real consumer.
- [x] Under-engineering — none for DELIVERED scope. AC2/3/4 absence is the documented user-approved Phase-1→2 split (correctly not flagged). All 16 Step-6 audits attested clean.
- [x] Contract gaps — none. Full type hints + docstrings; explicit ValueError/AssertionError semantics; `DerivedSpec` named alias.
- [x] Security — none. No auth/input boundary/secrets/shell=True; `subprocess_env` never mutates ambient env; `pin_vault_root` restores `os.environ` in `finally`.
- [x] Drift from vault — none. Code matches design.md (setattr-pin per ADR-101 refinement); no production code touched (AC5 verified); ADR-102 op-gate correctly absent (deferred); slice-queue.md sync is the documented master reconciliation.
- [x] Web-known issues — none. stdlib-only on Py3.13; setattr-over-reload is the well-known mitigation for reload-rebinds-class-identity.
- [x] Cross-cutting conformance — strong. RSAD-1 (self-tests use REAL consumers); APED-1 (code-Critic executed both worlds + adversarial derived-probe); identity-preservation directly tested; EOL-DRIFT-1 N/A (no new .md byte-compare).

**Net**: 0 blockers, 0 majors, 3 minors — all addressed in-slice.

_(Full code-Critic transcript: agent a6a5feb3, 9 dimensions, 44 tool uses, independent dual-world execution.)_
