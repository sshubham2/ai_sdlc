# Validation: Slice 084 harden-pcr-2a-clock-skew-winner

**Date**: 2026-05-30
**Result**: PASS

Real environment for this methodology-tool slice = the resolver executing against **real git
rebase-in-progress states** (integration tests build real `tmp_path` git repos via `subprocess` +
`git rebase`) and **real `datetime` wall-clock arithmetic** (timezone-aware comparison, no mocks of
the clock — `now` is injected as a real `datetime` value). The 24-item suite is the validation harness;
evidence is the verbose per-test pass record below.

## Per-criterion results

### AC1: skew-plausibility check → STOP with skew-specific reason; NEVER silently strict-newer on a suspicious ordering
- **Status**: PASS
- **Evidence**:
  - `test_suspicious_ordering_yields_no_auto_winner` PASSED — `_winner_clock_skew_suspect` returns a truthy reason for a future-dated winner.
  - `test_suspicious_ordering_returns_stop_with_skew_reason` PASSED — integration (real `tmp_path`, injected early `now`): `resolve_vault_claim_conflict` returns `action="STOP"`, `conflict_class=VAULT_CLAIM`, reason contains `clock-skew` + `PCR-2b`; the guard returns at Step 2.5 before any overlay/write (verified: no `git rebase --continue`).
  - `test_naive_offsetless_claimed_at_stops_not_crashes` + `test_unparseable_claimed_at_stops_fail_closed` PASSED — fail-closed STOP, never a `TypeError` crash (B1).
- **Notes**: Step 2.5 runs strictly before Step 3 → a skew-STOP mutates no rebase state (atomicity).

### AC2: skew-STOP records BOTH claims' Claimed-by/at + the cross-check signal in the audit entry, and routes the operator to the PCR-2b gate
- **Status**: PASS
- **Evidence**:
  - `test_skew_stop_audit_records_both_claims_and_signal` PASSED — the `## Vault-claim resolution (clock-skew STOP)` audit section contains both `Claimed-by`/`Claimed-at` values + `now.isoformat()` (resolver-now signal) + `PCR-2b`.
  - `test_skew_stop_reason_routes_to_pcr_2b_gate` PASSED — the reason string names `PCR-2b`. The integration STOP returns `conflict_class=VAULT_CLAIM`, which `skills/commit-slice/SKILL.md:190` already routes to the SOAD-1 user-disposition block (no skill edit required — verified by the code-Critic).
- **Notes**: R-23 corrigibility hook satisfied — both timestamps are forensically recoverable.

### AC3: no happy-path regression — a plausibly-ordered collision still auto-resolves by strict-newer; gate fires ONLY on the suspicious case (no over-trigger)
- **Status**: PASS
- **Evidence**:
  - `test_plausible_ordering_still_auto_resolves_strict_newer` PASSED — integration with the canonical APPLIED fixture + injected far-future `now`: `action="APPLIED"`, `conflict_class=VAULT_CLAIM` (strict-newer resolution unchanged).
  - `test_gate_does_not_overtrigger_on_normal_skew_within_threshold` + `test_tolerance_boundary_at_300s_not_suspicious` + `test_tolerance_boundary_at_301s_suspicious` PASSED — strict `>` boundary pinned at 300s.
  - **PCR regression: 95 passed** (`pytest -k "pcr_2a or pcr_2b or pcr_1 or parallel_conflict"`) — every existing dispatch-site caller (which omits `now` → real-now default) is unaffected; their 2026 fixture stamps are historically-past → guard returns `None`.

### AC4: R-23 NARROWED (not fully retired) — APED-1 battery shows the future-dated sub-case caught/escalated AND the plausible case resolves; staler-but-past residual stays open
- **Status**: PASS
- **Evidence**:
  - `test_aped1_battery_future_dated_winner_caught_past_resolves` — 13-row adversarial corpus, all PASSED: canonical past→resolve / future→caught; `Z` + lowercase `z` past→resolve / future→caught; microsecond past→resolve / future→caught; offset-no-colon + space-separated future→caught; tz-naive / garbage / empty → fail-closed.
  - The staler-but-past residual is explicitly documented OPEN (mission-brief AC-4, ADR-076 §Consequences); R-23 stays open/downgraded — to be recorded at /reflect, NOT flipped to retired.
- **Notes**: full suite **1217 PASS** (was 1193 @ slice-083; +24).

## Multi-instance validation
**Required?**: no — single-process resolver invoked during a (serialized) `git rebase --continue`; no multi-device/multi-user runtime concurrency surface (the cross-machine skew it addresses is a *property of the claim timestamps*, exercised via fixtures, not a live two-machine test). The cooperative-not-adversarial threat model (ADR-067/071/076) is preserved.
**Result**: not-applicable

## VAL-1 layered safety checks
- **Layer A (credential scan)**: PASS — 0 secrets.
- **Layer B (dependency hallucination)**: PASS — 0 findings (`--imports-allowlist tests`).

## Shippability catalog (Step 5.5)
- **SCMD-1**: clean — 89 rows; prose-free Machine-cmd on every row (incl. new row 90); 0 incidental couplings.
- **PTFCD-1**: clean — 429 test-path tokens, all files + cited functions exist.
- **SRSC-1 runner**: **89 rows, 89 PASS, 0 FAIL** (exit 0) — no past-slice regression introduced by slice-084 (row 90, the new clock-skew test file, PASS).

## Shippability regressions
None. Catalog 89/89 PASS.

## Reality surprises
- None at validation. (The code-Critic's M1 lowercase-`z` + M2 cross-version `fromisoformat` were surfaced at /code-review and fixed in-slice before validation — recorded in code-review.md, not reality surprises here.)
