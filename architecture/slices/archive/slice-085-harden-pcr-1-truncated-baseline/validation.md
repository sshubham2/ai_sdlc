# Validation: Slice 085 harden-pcr-1-truncated-baseline

**Date**: 2026-05-30
**Result**: PASS

**Environment note**: this is a methodology/tooling slice. The "real environment" for a git-rebase-conflict resolver is the **real `parallel_conflict_resolver` driven against real tmp-repo git rebase conflicts** (`_stage_rebase` builds an actual two-branch git repo, runs `git rebase`, and the conflict stages are read via real `git show :2:`/`:3:`). No mocks — the battery exercises the live resolver end-to-end, plus an APED-1 executed probe battery against the real `_baseline_is_truncation_shaped` helper. Walking-skeleton=false, Exploratory-charter=false → WS-1/ETC-1 skip (clean).

## Per-criterion results

### AC1: SOFT guard STOPs (no writes) on claimed-candidate drop from a tail-truncation-shaped baseline; audit row names the claim-loss-by-corruption
- **Status**: PASS
- **Evidence**: `test_soft_stops_on_orphan_claim_drop_from_tail_truncated_baseline` PASSED (real tmp-repo rebase: master/stage-2 claims `add-foo`; baseline/stage-3 dropped `add-foo` + last block `add-bar` missing Risk-retired → `resolve_soft_conflict` returns `action=="STOP"`, `reason` contains "truncat", audit log contains "truncat"). `test_baseline_truncation_helper_is_tail_specific_not_whole_file_scan` PASSED (tail-block-only signature; an earlier malformed block does NOT trip the gate).
- **Notes**: orphan-branch-gated (Option 4) per TRI-1.

### AC2: orphan claim from a WELL-FORMED baseline → WARN + auto-merge (no false-STOP)
- **Status**: PASS
- **Evidence**: `test_orphan_claim_drop_from_wellformed_baseline_warns_and_automerges` PASSED (`action=="APPLIED"`; `cross-stage-claim-drop` WARN on stderr). The pre-existing `test_cross_stage_claim_drop_warns_not_stops` (slice-082) also still PASSES — regression-confirms the happy path.

### AC3: legitimately-short well-formed baseline auto-merges (no false-STOP on a healthy short queue)
- **Status**: PASS
- **Evidence**: `test_wellformed_short_baseline_automerges_no_false_stop` PASSED (`action=="APPLIED"`; claim preserved in resolved file).

### AC4: no regression
- **Status**: PASS
- **Evidence**:
  - (a) `test_overlay_silent_drop_still_stops_1775_1783` PASSED — the pre-existing overlay-silent-drop STOP is unchanged.
  - (b) `test_stop_is_atomic_via_resolve_soft_conflict_both_soft_files_pending` PASSED — with slice-queue.md (truncation-shaped) + shippability.md (distinct-number rows, SOFT-benign) both pending, the truncation STOP fires before any write; `regenerated_files==()`, both U-files retain conflict markers, rebase still in progress.
  - (c) full PCR/queue/writer suite **134 passed**; full repo suite **1228 passed** — PCR-1 SOFT set-equal + PCR-2a clock-skew paths unchanged.
  - (d) `test_empty_and_placeholder_baseline_not_truncation_shaped` + `test_truncation_helper_normalizes_crlf_and_trailing_space_heading` PASSED — empty/`_(no candidates)_`/CRLF/trailing-space do NOT false-STOP. APED-1 executed battery (9 inputs) confirms: empty/placeholder/header-only/complete-LF/complete-CRLF/earlier-malformed/trailing-space → suspect=False; tail-missing-Risk-retired + tail-cut-midline → suspect=True.

### AC5: R-24 narrowed (not retired) in risk-register.md; 5 field labels sourced from a single `_RENDERED_FIELD_LABELS` constant
- **Status**: PASS
- **Evidence**: `test_baseline_truncation_helper_uses_writer_field_label_constant` PASSED (monkeypatch proves the helper reads `slice_queue_writer._RENDERED_FIELD_LABELS` at call time). `test_format_entry_renders_from_rendered_field_labels_constant` PASSED (writer renders FROM the constant — genuine SSoT). RR-1 audit: **R-24 status == open** (narrowed-downgraded, NOT retired); `**Narrowed:** slice-085` annotation present with residuals (i)–(iv).

## VAL-1 layered safety checks
- **Layer A (credentials)**: 0 secrets. PASS.
- **Layer B (dependency hallucination)**: 0 import findings (changed `.py` import only stdlib `re`/`subprocess` + internal `tools.*`/`tests` namespace). PASS.

## Shippability catalog (regression check)
- **Pre-gates**: SCMD-1 exit 0; PTFCD-1(b) exit 0.
- **Catalog run** (`tools.shippability_runner`): **89 rows, 89 PASS, 0 FAIL**. No past slice regressed.

## Multi-instance validation
- **Required?**: no — single-process git-conflict-resolution tool, no multi-user/device/account surface (ADR-067 cooperative threat model). The two-branch rebase fixtures already exercise the multi-stage (stage-2 vs stage-3) conflict scenario that is the closest analog.
- **Result**: not-applicable.

## Reality surprises
- None at validation. (The code-Critic's M1 false-negative — a value line beginning with the exact missing label literal masks the truncation — was surfaced at /code-review and recorded as R-24 residual (iv); not a validation-time surprise.)

## Notes for /reflect
- Add a `shippability.md` row pinning `tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py` (the claim-loss-by-truncation STOP is a must-never-regress critical path) — conventional /reflect catalog-update responsibility.
- code-review minors m1–m4 + the M1(a) durable field-shape-tightening fix are logged candidates (see code-review.md).
- R-24 stays open-downgraded; M1 invisible-claim case is the TRI-1-ratified documented residual.
