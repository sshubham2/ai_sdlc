# Validation: Slice 028 refactor-utf8-rollup-sentinel-version-agnostic

**Date**: 2026-05-16
**Result**: PASS

"Real environment" for a test-infra refactor = the actual tests/audits executed on the real repo (not synthetic). Evidence below is real command output.

## Per-criterion results

### AC1: rollup sentinel has no hardcoded count literal / no `post-slice-NNN` anchor; assertion derived from current repo state
- **Status**: PASS
- **Evidence**: AST of `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` — `no int-Compare: True | no post-slice anchor: True | ast+re imported: True`. Sentinel body calls `_discovered_audit_tools()` + `_covered_tool_tokens()` (derived from repo state). `test_rollup_sentinel_is_version_agnostic_shape` (passing) structurally pins this.
- **Notes**: int-Compare check scoped to the sentinel body (helpers legitimately use arity ints) — slice-014-faithful defect-class precision.

### AC2: protective invariant preserved both directions (new tool w/ coverage → green, zero sentinel edit; w/o coverage → red)
- **Status**: PASS
- **Evidence**:
  - dir-A (no coverage → RED): real `tools/aaa_ac2_fake_audit.py` (non-`_`, has `main()`) → sentinel `1 failed`, message names `tools.aaa_ac2_fake_audit`; `rm` (no test-file edit needed for an uncovered tool) → `1 passed`. Re-confirmed clean post-reconstruction.
  - dir-B (coverage added at a real call site, NOT the sentinel body → GREEN): adding `"tools.aaa_ac2_fake_audit"` to `_ROOT_ONLY_TOOLS` → sentinel `1 passed` with the sentinel body byte-untouched. Observed against the correct refactored code (pre-revert run).
  - `test_rollup_sentinel_fails_with_tool_naming_message_on_parity_break` (passing, both directions) is the standing executable proof; structurally, covered-set is AST-read from call sites so coverage can only be satisfied by editing a real call site.
- **Notes**: invariant genuinely protected — the option-3 declaration-weakening (B2) is closed; a green sentinel requires a real coverage call site.

### AC3: removing/renaming an audit tool leaves no stale count; no manual ledger edit
- **Status**: PASS
- **Evidence**: removing `tools/triage_audit.py` + its `_POSITIONAL_SLICE_TOOLS` token (the same localized change) → sentinel `1 passed` (no `== N` to break, no separate ledger edit). Observed against correct refactored code (pre-revert). Structurally guaranteed: covered-set token vanishes with the call site automatically; there is no parallel hand-maintained list.

### AC4: full `tests/methodology/` passes; `utf8_stdout_audit` clean; no per-tool cp1252 regression
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/ -q` → **561 passed**; `tools.utf8_stdout_audit` → `clean. 20 tool(s) scanned; 20 with main(); 20 clean`; the 22 pre-existing per-tool parametrized/bespoke cp1252 tests still pass (unchanged).

### AC5: changelog records UTF8-STDOUT-1 v1.1 (rule-ID lineage preserved); shippability UTF-8 rollup row updated
- **Status**: PASS
- **Evidence**: v0.42.0 entry — `UTF8-STDOUT-1 v1.1 + 'NOT a new rule ID': True`; in-repo == installed methodology-changelog.md `byte-equal: True`; `architecture/shippability.md` row 28 present with `UTF8-STDOUT-1 v1.1` + `test_utf8_stdout_regression` consumer ref. EPGD-1 entry-pins (`test_v_0_42_0_utf8_stdout_1_*`) + ADR-026 pin pass; 0 prior entry-pin functions touched.

## VAL-1 layered safety checks
- **Result**: clean — `0 secret(s), 0 import finding(s), 0 suppressed`. (`--imports-allowlist tests` for the pytest namespace root.)

## WS-1 / ETC-1 / TF-1
- not-applicable — mission-brief sets Walking-skeleton / Exploratory-charter / Test-first all `false` (audits return clean silently).

## Shippability catalog (regression check)
- **PTFCD-1 pre-catalog gate**: clean — 27 rows, 206 test-path tokens, all exist (re-run post-reconstruction).
- **Catalog run**: 34 distinct catalog-cited test files, 0 missing, **394 passed**. No past slice broken by slice-028.

## Multi-instance validation
- **Required?**: no (test-infra refactor; no multi-user/device/account surface).
- **Result**: not-applicable.

## Reality surprises
- **Destructive-`git checkout`-on-uncommitted-slice-work hazard (process, not code).** During AC2/AC3 behavioral demo, the validation harness used `git checkout -- tests/methodology/test_utf8_stdout_regression.py` to revert demo edits. Under **branch-per-slice (BRANCH-1)** the slice's work is *uncommitted* until `/commit-slice`, so `git checkout --` silently reverted the entire Task-2 refactor to pre-slice HEAD (the post-revert "1 passed" was the OLD `== 20` sentinel passing — a false-green that nearly masked the loss). Caught immediately via a sentinel-file hash mismatch + the harness's own system-reminder showing reverted content. Refactor reconstructed verbatim from in-context final state; all checks re-run clean. **Lesson for /reflect**: validation/demo harnesses that mutate-then-revert source MUST use in-place reverse edits or temp copies — NEVER `git checkout -- <path>` / `git restore` / `git stash` on files carrying uncommitted slice work. Candidate methodology note (build-checks / CLAUDE.md): "no destructive git on uncommitted slice work; revert demo mutations in-place." Not a risk-register R-ID (process discipline, not a product/tech risk).
- No code-level or spec-level surprises. The observed-covered-set design behaved exactly as ADR-026 predicted in all three behavioral directions.
