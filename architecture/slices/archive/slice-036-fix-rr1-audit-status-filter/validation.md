# Validation: Slice 036 fix-rr1-audit-status-filter

**Date**: 2026-05-17
**Result**: PASS

## Per-criterion results

### AC1: repro test passes at slice end (BFRD-1)
- **Status**: PASS
- **Evidence**: `pytest …::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks -q` → `1 passed in 0.04s`. Was WRITTEN-FAILING pre-fix (`leaked: ['R2','R3']`), now passes against `clean_register.md`.

### AC2: --json applies --filter-status / --filter-band / --top to the consumed risks list (real register)
- **Status**: PASS
- **Evidence** (real `architecture/risk-register.md`, not fixture):
  - `--json --filter-status open` → `status-open: ['open']`, `view-key: False` (pre-fix leaked mitigating/retired R-1/R-3/R-4/R-5)
  - `--json --filter-band high` → bands `['high']` only
  - `--json --top 3 --sort score` → exactly 3 rows, scores `[6, 4, 4]` (descending)
- **Notes**: `view` key absent in all three — ADR-036 single-list contract confirmed on the real artifact (BC-PROJ-4 dogfood).

### AC3: no regression — existing RR-1 suite + behavior unchanged
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_risk_register_audit.py -q` → `30 passed in 0.06s` (24 pre-existing incl. `test_filter_status_open_excludes_retired` library sentinel + 6 new). Exit-code / violation path untouched (`_format_human` unchanged; `to_dict` unchanged).

### AC4: contract pinned (leak + no-flag ordering + consumer flag/prose)
- **Status**: PASS
- **Evidence**: `test_json_consumed_risks_contract_pinned_against_unfiltered_regression`, `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id`, `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` (durable M-add-1 prose-pin), plus pre-existing `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` → `5 passed`. Manual re-read: `skills/slice/SKILL.md` L46/L49 + `skills/pulse/SKILL.md` L40 still consume `--json --filter-status open` and read the (now-filtered) `risks` key — correct, no skill-prose edit needed.

## Multi-instance validation
**Required?**: no (local CLI/library audit tool — no multi-user/device/account surface)
**Result**: not-applicable

## VAL-1 layered safety checks
- Layer A (credentials): 0 secrets. Layer B (dep hallucination): 0 import findings. Clean (`--imports-allowlist tests`).

## Shippability catalog (regression check)
- Pre-catalog gates: SCMD-1 clean (36 rows), PTFCD-1 clean (36 rows, 228 test-path tokens all exist).
- **Catalog: 36/36 PASS** — including #36 (this slice's new R-9 repro). Zero regressions; slice-036 broke no past slice's critical path.

## Reality surprises
- None at validation. (One was caught earlier at /build-slice pre-finish: the Critic-stack's "AC3 no-regression carve-out survives strict TF-1" claim was wrong — `test_first_audit --strict-pre-finish` refused `ac-without-row`; fixed by mapping AC3 to the existing `test_filter_status_open_excludes_retired` sentinel. Recorded in build-log.md; a /critic-calibrate signal for /reflect.)
