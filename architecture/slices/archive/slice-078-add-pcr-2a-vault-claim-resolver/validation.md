# Validation: Slice 078 add-pcr-2a-vault-claim-resolver

**Date**: 2026-05-29
**Result**: PASS

## Per-criterion results

### AC#1: `resolve_vault_claim_conflict` correctness across stage-2/stage-3 winner + tie/multi/silent-drop STOP + in-memory disk-ignore

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_pcr_2a_vault_claim_resolver.py -v` → **20 passed in 0.75s**. Covers:
  - `test_collect_returns_empty/single/multiple_collision` (3 predicate tests)
  - `test_timestamp_winner_when_newer_in_stage_3` + `test_timestamp_winner_when_newer_in_stage_2` (M4 critical-invariant pair — stage-agnostic winner identification verified)
  - `test_claimed_at_tie_returns_none` (helper predicate) + `test_claimed_at_tie_returns_stop` (public-API integration)
  - `test_parse_queue_extracts_name_safety_claimed` + `test_parse_queue_returns_empty_on_empty_text` (B1 file-local parser)
  - `test_loser_auto_re_pick_returns_highest_priority_unclaimed_non_overlapping` + `test_loser_auto_re_pick_skips_claimed_candidates` + `test_loser_auto_re_pick_skips_non_parallel_safe_candidates` + `test_loser_auto_re_pick_skips_exclude_names` (filter combinations)
  - `test_no_available_when_queue_empty` + `test_no_available_when_all_overlapping` + `test_no_available_when_all_claimed` (m5 ACCEPTED-FIXED — 3 distinct branches)
  - `test_multi_candidate_collision_returns_stop` (m2 — multi-collision STOP)
  - `test_no_collision_diag_returns_unknown_stop` (caller misuse fail-closed)
  - `test_overlay_silently_dropped_returns_stop` (M-add-1 — defensive post-overlay regex catches silent-drop on malformed candidate block)
  - `test_pick_loser_replacement_reads_resolved_text_not_disk` (M-add-2 load-bearing — disk holds conflict-marker'd text; in-memory holds resolved overlay; helper returns disk-ignored result)
- **Notes**: 20 tests > 18 declared TF-1 rows (mid-build addition of 2 predicate tests recorded in build-log §Design deviations; conformance class per TPHD-1).

### AC#2: Both `resolve_soft_conflict` L242-253 AND `_regen_slice_queue` L627-638 dispatch VAULT_CLAIM; UNKNOWN-class still fail-closed

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_pcr_2a_regen_slice_queue_dispatch.py -v` → **3 passed in 1.65s**. Tests use real tmp_path-rooted git repos with staged rebase-in-progress state (not mocked).
  - `test_resolve_soft_conflict_dispatches_vault_claim_into_pcr_2a` — exercises CLI-facing path; without this dispatch the L243 guard short-circuits VAULT_CLAIM to STOP.
  - `test_regen_slice_queue_dispatches_into_vault_claim_resolver` — exercises defense-in-depth sentinel raise + reroute (post-fix `_VaultClaimDispatch` replaces `_SoftResolutionError(VAULT_CLAIM)`).
  - `test_unknown_class_still_fail_closed` — verifies PCR-1's UNKNOWN raise leg at L605-609 preserved verbatim (no scope-creep).
- **Notes**: Plus the Phase D-repaired sibling test `test_regen_slice_queue_vault_claim_defense_in_depth_gate_raises_sentinel` in `tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py` re-runs the assertion with monkeypatched `_git_show_stage` fixtures — PASS.

### AC#3: SKILL.md sub-step 2.5 APED-1 Pins #1 + #2 + OSDG-1 forward-sync

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py -v` → **3 passed in 0.05s**.
  - `test_substep_2_5_l185_pins_vault_claim_in_apply_block` — APED-1 Pin #1 regex `VAULT_CLAIM[^\n]*(?:auto-resolves|APPLIED|auto-resolved by PCR-2a|dispatched to PCR-2a)` matches the L185 dispatch paragraph.
  - `test_substep_2_5_l192_drops_vault_claim_from_fall_closed_enumeration` — APED-1 Pin #2 regex `VAULT_CLAIM\s*\([^)]+\)\s*\+\s*HARD\s*\(` (the pre-fix multi-class enumeration form) returns 0 matches — VAULT_CLAIM no longer in fall-closed list.
  - `test_in_repo_and_installed_forward_synced` — OSDG-1 byte-equality modulo CRLF/LF per ADR-033 passes (forward-sync done in Phase C build-log:11).
- **Notes**: Pin #2 regex refined mid-build after initial over-broad match — recorded in build-log §Design deviations + code-review:m3 sibling-aware framing.

### AC#4: Audit-log section heading `## Vault-claim resolution - <ISO>` (uniform hyphen-space per M2) + mixed-section append-only

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py -v` → **2 passed in 0.40s**.
  - `test_vault_claim_event_row_format` — verifies section heading regex `^## Vault-claim resolution - \d{4}-\d{2}-\d{2}T` (hyphen-space; M2 fix) + 8 required field-lines (`Repo HEAD SHA pre-resolution`, `Candidate name`, `Winner Claimed-by`, `Winner Claimed-at`, `Loser Claimed-by`, `Loser Claimed-at`, `Loser auto-re-pick`, `Resolution actions`) + winner identity preserved (alice <a@example.com>) + loser identity surfaced (bob <b@example.com>) + replacement field carries `add-replacement`.
  - `test_log_is_append_only_across_section_types` — seeds a SOFT-section row first; appends a VAULT_CLAIM section; asserts the post-append file STARTS with the pre-append bytes (byte-equal SOFT survives) AND the new VAULT_CLAIM section follows. Lazy-create-on-first-of-each-section behavior verified (file was absent on disk per m7 ACCEPTED-FIXED).

### AC#5: Catalogued post-fix regression repro + shippability row #78 added

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_pcr_2a_repro_vault_claim_gate_closed.py::test_vault_claim_gate_closed_returns_resolution_result -v` → **1 passed in 0.73s**. Test exercises a real tmp_path-rooted git repo with rebase-in-progress state; asserts `_regen_slice_queue` raises `_VaultClaimDispatch` sentinel (post-fix behavior) and NOT `_SoftResolutionError(VAULT_CLAIM)` (PCR-1 pre-fix behavior). Pre-fix → post-fix FAIL→PASS contrast: pre-fix git SHA was f329c7d (master, no PCR-2a); post-fix SHA carries the slice-078 PCR-2a mint. Single-direction repro per B2 ACCEPTED-FIXED.
- **Notes**: Shippability row #78 added to `architecture/shippability.md` pins the post-fix PASS as never-silently-regress assertion. Verified via full shippability catalog run (Step 5.5 below).

## Multi-instance validation

**Required?**: No
**Result**: not-applicable
**Evidence**: PCR-2a is methodology tooling; no multi-user / multi-device / cross-account flows. Cooperative-not-adversarial threat model per ADR-067 / ADR-069 inheritance carries forward.

## Reality surprises

None. All 5 ACs delivered as designed. The 2 mid-build TF-1 plan growths (18 → 20 rows) and the Pin #2 regex refinement after initial over-broad match are documented in build-log §Design deviations as Conformance-class.

## Step 5b — VAL-1 layered safety checks

```
VAL-1 layered safety checks: 0 secret(s), 0 import finding(s), 0 suppressed (allowlisted).
Clean — both layers passed.
```

- **Layer A (Critical, credential scan)**: 0 secrets detected across 13 changed files.
- **Layer B (Important, dependency hallucination)**: 0 hallucinated imports; new modules use only stdlib (`subprocess`, `re`, `pathlib`, `os`, `dataclasses`, `enum`, `datetime`, `sys`, `json`, `argparse`) + in-house `tools.parallel_conflict_resolver` + `tools.slice_queue_claim` references resolved.

## Step 5c — WS-1 walking-skeleton audit

Not applicable — mission-brief `**Walking-skeleton**: false`. Audit skipped silently per default-off semantics.

## Step 5d — ETC-1 exploratory-charter audit

Not applicable — mission-brief `**Exploratory-charter**: false`. Audit skipped silently per default-off semantics.

## Step 5.5 — Shippability catalog regression check

**Pre-catalog gates**:
- `SCMD-1 audit: clean. 77 row(s); 828 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=826.`
- `Shippability path audit (PTFCD-1/PTFFD-1): clean. 77 row(s), 396 test-path token(s) — all files and cited functions exist.`

**Canonical runner**:
```
$PY -m tools.shippability_runner architecture/shippability.md
Shippability catalog run: 77 row(s), 77 PASS, 0 FAIL
```

**77 of 77 PASS** — no past slice regression; the new PCR-2a row (slice-078) is included in the catalog runner sweep and passes. The PCR-2a mint did not break any prior slice's critical-path assertion.
