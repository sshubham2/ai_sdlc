# Validation: Slice 034 fix-tf1-audit-field-line-regex

**Date**: 2026-05-17
**Result**: PASS

## Per-criterion results

### AC1: annotated `**Test-first**: true  (per TF-1 — …)` detected as ENABLED; `audit_brief_file` no silent default-off
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_tf1_field_line_annotation_regression.py -q` → **3 passed** (`test_detect_test_first_flag_honors_trailing_annotation`, `test_annotated_brief_does_not_silently_default_off`, `test_r7_retired_in_risk_register`). These were the FAILING repro (2 failed pre-fix with `AuditResult(test_first_enabled=False)`); now pass. Real-artifact: `python -m tools.test_first_audit <slice-034>` → `Test-first audit: clean. 9 row(s) — PASSING=9` (ENABLED on the slice's own bare-field brief; "not enabled" pre-fix).
- **Notes**: BC-PROJ-4 dogfood confirms the cure on the real artifact, not just unit fixtures.

### AC2: absent / bare `true`|`false` non-regressed; `**Test-first**: false` not malformed (M2 invariant)
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_test_first_audit.py -q` → **22 passed** (incl. `test_absent_field_stays_default_off_clean`, `test_present_false_field_is_not_malformed` [bare + annotated false → zero violations, not enabled], and all pre-existing TF-1 tests). Full methodology suite **656 passed** (was 648 @ slice-033; +8 net; zero regression).

### AC3: present-but-malformed field is loud, not silent default-off
- **Status**: PASS
- **Evidence**: real-artifact — wrote `/tmp/s34mal/mission-brief.md` with `**Test-first**: false-positive`; `python -m tools.test_first_audit /tmp/s34mal --no-carry-over` → exit 1, `1 test-first violation(s): [Important] …:3 (malformed-test-first-field) the **Test-first** field is present at line 3 but its value 'false-positive' is not a standalone true or false token …` (attributed: brief path + line + raw value + accepted forms; NOT the silent "not enabled"). Unit: `test_present_but_malformed_field_is_loud_not_silent` (incl. empty value) + `test_malformed_suffix_value_is_loud_not_silent` (`false-positive`/`true.`/`trueish`/`false; note`) green.

### AC4: full `test_test_first_audit.py` + entire shippability catalog stay green
- **Status**: PASS
- **Evidence**: full methodology suite **656 passed in 11.50s**. Shippability catalog (SCMD-1 + PTFCD-1 pre-gates clean; 34 rows) run with per-`;`-segment backtick-strip → **34 rows, 34 PASS, 0 FAIL**. Row #28 (R-8 multi-segment) passed under correct per-segment parsing. TF-1 `--strict-pre-finish` on the slice brief: 9/9 PASSING.

### AC5: R-7 escalated to `retired` in risk-register.md with slice-034 reference + regression-test citation
- **Status**: PASS
- **Evidence**: `architecture/risk-register.md` R-7 block: `**Status**: retired` + `**Retired**: slice-034-fix-tf1-audit-field-line-regex (2026-05-17; ADR-034 / TFFL-1 / methodology v0.48.0)` + a "R-7 RETIREMENT (slice-034 …)" note citing the catalogued repro (shippability #34) as the durable guard. `tools.risk_register_audit --json` parses R-7 `status: retired`. `test_r7_retired_in_risk_register` (AC5 unit, reads live register) → 1 passed. Sequenced per m2: register escalation done before the AC5 row was marked PASSING.

## Multi-instance validation
**Required?**: no
**Result**: not-applicable
**Evidence**: slice-034 is a local audit-tool parsing fix (`tools/test_first_audit.py`) — no multi-user / multi-device / sync / account surface.

## Layered safety checks (VAL-1)
- **Layer A (credential scan)**: clean — 0 secrets across changed files.
- **Layer B (dependency hallucination)**: clean — 0 import findings (`--imports-allowlist tests`; only stdlib `re` + intra-repo `tools`/`tests` imports added).
- WS-1: not applicable (`**Walking-skeleton**: false`). ETC-1: not applicable (`**Exploratory-charter**: false`).

## Shippability regressions
None. 34/34 PASS.

## Reality surprises
- **`tools.risk_register_audit --filter-status open` lists RETIRED risks** (both R-5 [retired by slice-033] and R-7 [retired here] appear in `--filter-status open` output; the JSON `status` field is correctly `retired`). The flag does NOT filter by status — consumers (/status, /slice) must read the `status`/`band` fields, which they do. **Pre-existing** (R-5 demonstrates it predates slice-034), **out of slice-034 scope**, does NOT fail any AC. Flagged for `/reflect` as a candidate latent RR-1 observation (could mislead a naive `--filter-status open` consumer into treating retired risks as open during risk-first /slice prioritization) — not a slice-034 defect; potential future risk-register-tooling slice.
