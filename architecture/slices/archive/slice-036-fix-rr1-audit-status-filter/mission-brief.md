# Slice 036: fix-rr1-audit-status-filter

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-9 (medium, score 3) — `tools.risk_register_audit --json` does not apply `--filter-status` / `--filter-band` / `--top` to the risk list JSON consumers read (latent contract footgun; no current correctness impact)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

In JSON mode `main()` emits the full unfiltered `result.to_dict()` under `out["risks"]` and only applies the filter to `out["view"]`, so `retired`/`accepted`/non-matching risks appear in the `risks` list even under `--filter-status open` (e.g. retired R-5/R-7). Per the authoritative R-9 entry (`architecture/risk-register.md` L170, L172), this is a **latent footgun, not a live corruption**: `/pulse` and `/slice` are currently correct because they read the per-risk `status`/`band` fields, not the filter's membership. This slice retires R-9 **proactively** — before any consumer starts trusting `--filter-status` membership directly — by making the consumed `risks` key honour the flag. No current correctness impact is being claimed or fixed.

## Acceptance criteria

1. The failing repro test `tests/methodology/test_risk_register_audit.py::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks` PASSES at slice end (BFRD-1).
2. `tools.risk_register_audit --json` applies `--filter-status`, `--filter-band`, and `--top` to the risk list JSON consumers read; run against the real `architecture/risk-register.md` with `--filter-status open`, the consumed list contains zero `retired`/`accepted`/`mitigating` entries (only `open`).
3. No regression: the existing RR-1 suite (`tests/methodology/test_risk_register_audit.py`, incl. `test_filter_status_open_excludes_retired`) and human-format output (already correct via `view`) still pass; exit-code / violation-reporting behavior unchanged. Gate command: `python -m pytest tests/methodology/test_risk_register_audit.py -q` — full module green.
4. The JSON-output contract is pinned by regression tests so a future change cannot silently (a) re-introduce an unfiltered consumed list, (b) revert the documented no-flag score-desc ordering, or (c) drop the load-bearing `--filter-status open` flag / exclusion prose from the two consumer SKILL.md files (the new `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` is the durable guard for (c); the pre-existing `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` only pin the bare `RR-1`/`risk_register_audit` reference and are NOT credited with flag/prose parity — per meta-Critic M-add-1). A manual `/build-slice` + `/validate-slice` re-read of both SKILL.md invocation strings is a supplementary check, not the primary guard. (Parity is NOT enforced by CSP-1 — Heavy-mode-only, a structural no-op here.)

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | integration | tests/methodology/test_risk_register_audit.py | test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks | PASSING |
| 2 | integration | tests/methodology/test_risk_register_audit.py | test_json_filter_band_and_top_applied_to_consumed_risks_fixture | PASSING |
| 2 | integration | tests/methodology/test_risk_register_audit.py | test_json_filter_status_open_excludes_non_open_real_register_invariant | PASSING |
| 4 | integration | tests/methodology/test_risk_register_audit.py | test_json_consumed_risks_contract_pinned_against_unfiltered_regression | PASSING |
| 4 | integration | tests/methodology/test_risk_register_audit.py | test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id | PASSING |
| 4 | integration | tests/methodology/test_risk_register_audit.py | test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose | PASSING |
| 3 | unit | tests/methodology/test_risk_register_audit.py | test_filter_status_open_excludes_retired | PASSING |

(AC3 = "existing RR-1 behavior unchanged". The existing library-level `test_filter_status_open_excludes_retired` is the concrete no-regression sentinel — it proves `filter_and_sort` semantics are untouched by the JSON-branch fix, and it still passes. The full-module gate `python -m pytest tests/methodology/test_risk_register_audit.py -q` remains the broader pre-finish check. **Build-time correction**: the prior "AC3 is a gate, not a TF-1 row — survives strict TF-1" carve-out (blessed by first-Critic m2 + meta-Critic) was refuted by `test_first_audit --strict-pre-finish` (`ac-without-row` on AC3) — a BC-PROJ-4-class catch; every AC declared in the brief body MUST have a row.)

**Test oracle scoping (per Critic M2 — stable-oracle discipline, slice-004 real-file precedent):**
- `test_json_filter_band_and_top_applied_to_consumed_risks_fixture` runs against the **fixture** `tests/methodology/fixtures/risk_register/clean_register.md`. Verified scores via `_band_for_score` (1-2 low / 3-4 medium / 6-9 high): **R1** open, high×high=9 → **high** band; **R2** mitigating, med×med=4 → medium; **R3** retired, low×high=**3 → medium** band (NOT high — corrects the Critic-stack-proposed `{R1,R3}` oracle, plan-mode design-vs-reality catch); **R4** open, low×low=1 → low. Assert `out["risks"]` under `--filter-band high` == **{R1}**; under `--top 2 --sort score` == exactly **[R1, R2]** (scores 9, 4 — score-desc). Stable oracle, no vault coupling.
- `test_json_filter_status_open_excludes_non_open_real_register_invariant` runs against the real `architecture/risk-register.md` but asserts ONLY the **invariant** (zero non-`open` entries in `out["risks"]` under `--filter-status open`) — never a count/ordering that mutates as risks are added/retired (mirrors `test_risk_register_audit_real_file.py` slice-004 scoping discipline).
- `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` (AC #4, per Critic M1): `main([fixture, "--json"])` with NO filter flags → `out["risks"]` is `(-score, risk_id)` ordered, pinning the ADR-036-documented register-order→score-desc behavior change so it cannot silently revert.
- `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` (AC #4, **per meta-Critic M-add-1**): asserts `skills/slice/SKILL.md` AND `skills/pulse/SKILL.md` each contain the load-bearing `--filter-status open` invocation flag AND the behavioral prose this slice's "code-conformance-to-doc" thesis depends on ("Retired / accepted risks are excluded automatically" in `/slice`; "scored, sorted" in `/pulse`). This is the **durable** parity guard — the pre-existing `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` only assert `"RR-1"`/`"risk_register_audit"` substrings (verified L356–381) and do NOT pin the flag or exclusion prose; crediting them with that parity was an over-claim (M-add-1).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro passes | `python -m pytest tests/methodology/test_risk_register_audit.py::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks -q` → 1 passed |
| 2 | Real-register filter | `python -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` → no `"status"` value other than `open` in the consumed risk list; same for `--filter-band` / `--top` |
| 3 | No regression | `python -m pytest tests/methodology/test_risk_register_audit.py -q` → all pass; human-format spot-check unchanged |
| 4 | Contract pinned (leak + no-flag ordering + consumer flag/prose) | `test_json_consumed_risks_contract_pinned_against_unfiltered_regression` + `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` + `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` PASS; `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` still PASS (bare RR-1/module ref only — M-add-1); supplementary manual re-read of both SKILL.md invocation strings (no CSP-1) |

## Must-not-defer

- [ ] JSON-output contract decision is explicit and coherent: what `out["risks"]` vs `out["view"]` mean post-fix, and which key documented consumers (`/pulse`, `/slice` SKILL.md) read — resolved in `/design-slice`, not deferred
- [ ] Backward-compat check on every JSON consumer: `skills/pulse/SKILL.md`, `skills/slice/SKILL.md` (this skill's Step 1), and any `tools/*`/test reading the audit JSON `risks` key — enforced by the NEW `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` (durable flag+prose pin; the pre-existing `*_references_rr_1` tests only pin the bare RR-1/module substring, M-add-1) plus a supplementary manual `/build-slice` + `/validate-slice` re-read (NOT CSP-1 — Heavy-mode-only no-op here)
- [ ] Error path / no-filter case unchanged: unfiltered invocation still returns all risks (now score-desc ordered per ADR-036, pinned by `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id`); violation reporting + exit code (`1 if result.violations`) unchanged
- [ ] Regression test added to shippability #36 actually guards the unfiltered-leak class (not just the one fixture) — plus band/top coverage via the fixture stable-oracle test

## Out of scope

- Redesigning the RR-1 risk-register schema or `Risk`/`AuditResult` shapes
- Changing filter *semantics* (e.g., adding an "active" = open+mitigating filter, or altering the `--filter-status` choices set) — this slice makes the existing filter actually apply, nothing more
- Migrating the real `architecture/risk-register.md` content or re-triaging any risk

## Dependencies

- Failing repro: `tests/methodology/test_risk_register_audit.py::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks` (shippability #36, established by `/repro`)
- Code: `tools/risk_register_audit.py` — `main()` `if args.json:` branch (`out = result.to_dict(); out["view"] = ...`)
- Consumers (skill-prose only; verified no code/test reads `out["view"]`): `skills/pulse/SKILL.md`, `skills/slice/SKILL.md` (RR-1 `--json` usage reading the `risks` key) — flag+prose parity guarded by the new `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` (the `*_references_rr_1` tests pin only the bare RR-1/module reference, M-add-1); not CSP-1
- Risk register: [[risk-register#R-9]]

## Mid-slice smoke gate

At ~50% of build, run:
```
python -m pytest tests/methodology/test_risk_register_audit.py::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks -q
python -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open
```
Expected: repro test PASSES, and the real-register JSON `risks` list contains only `status: open` entries (no R-5/R-7 retired). If either fails: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] TF-1 audit `--strict-pre-finish`: all Test-first rows PASSING
- [ ] No-regression gate green: `python -m pytest tests/methodology/test_risk_register_audit.py -q`
- [ ] Consumer parity verified: `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` passes (durable flag+prose pin) AND `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` still pass (bare RR-1/module ref) AND a supplementary manual re-read of the `--json` invocation strings in both SKILL.md confirms correct `risks`-key consumption (NOT via CSP-1)
