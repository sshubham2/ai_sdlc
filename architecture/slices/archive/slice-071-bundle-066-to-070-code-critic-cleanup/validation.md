# Validation: Slice 071 bundle-066-to-070-code-critic-cleanup

**Date**: 2026-05-26
**Result**: PASS

## Per-criterion results

### AC#1: All 6 slice-066 code-Critic findings discharged (M1 + M2 + m1 + m2 + m3 + m4)

- **Status**: PASS
- **Evidence**: `grep -cE "^\| slice-066 (M1|M2|m1|m2|m3|m4) " architecture/slices/slice-071-bundle-066-to-070-code-critic-cleanup/build-log.md` → **6** (matches expected). Per-finding dispositions in build-log.md §Phase-by-phase disposition log:
  - slice-066 M1 (gitdir guards): FIXED — `tools/branch_workflow_audit.py:266-285` `if len(gitdir.parts) < 4` + `if not (main_repo / ".git").exists()` guards added.
  - slice-066 M2 (wt_base via git rev-parse): FIXED — `skills/build-slice/SKILL.md:55-60` `repo_root="$(git rev-parse --show-toplevel)"` derivation; OSDG-1 mirror clean.
  - slice-066 m1 (AuditResult worktree_skip_used surface): FIXED — `tools/branch_workflow_audit.py:100-130` fields added; `test_audit_result_surfaces_worktree_skip_fields` PASS.
  - slice-066 m2 (fixture rewrite APED-1 load-bearing): FIXED — `tests/methodology/test_branch_workflow_audit.py:350-422` rewritten with negative assertion that worktree-cwd-mismatch fires without WORKTREE=skip line.
  - slice-066 m3 (import os hoist): FIXED — `tools/branch_workflow_audit.py:43` module-level import.
  - slice-066 m4 (PowerShell parenthetical): FIXED — `skills/build-slice/SKILL.md:62` parenthetical appended.
- **Notes**: 17 tests pass in tests/methodology/test_branch_workflow_audit.py.

### AC#2: All 6 slice-067 m1 + slice-068 (M1 + m1 + m2 + m3 + m4) findings discharged

- **Status**: PASS
- **Evidence**: `grep -cE "^\| slice-067 m1 |^\| slice-068 (M1|m1|m2|m3|m4) " build-log.md` → **6**. Per-finding:
  - slice-067 m1 (write_slice_queue out_path kwarg + main() collapse): FIXED — `tools/slice_queue_writer.py:525-545` kwarg added; `main()` L803-821 collapsed; `test_main_cli_custom_output_uses_canonical_write_path` PASS.
  - slice-068 M1 (test_vault_paths_module_is_leaf): FIXED — `tests/methodology/test_vault_root_constant.py:293-327` new AST-walk test PASS.
  - slice-068 m1 (idempotency regex 4-shape coverage): FIXED — `tests/methodology/test_vault_root_constant.py:178-238` regex expanded; test PASS.
  - slice-068 m2 (freeze-pin 3-step assertion): FIXED — `tests/methodology/test_vault_root_constant.py:256-320` 3-step assertion added; test PASS.
  - slice-068 m3 (two-marker asymmetry DOCUMENT-AS-DESIGNED): FIXED — sentinel test `test_two_marker_convention_asymmetry_documented` with VERBATIM-aligned substring assertions PASS; module docstring carries the m3 prose.
  - slice-068 m4 (PEP-8 blank line): FIXED — `tools/supersede_audit.py:54` blank line inserted.
- **Notes**: 12 tests pass in tests/methodology/test_vault_root_constant.py.

### AC#3: All 8 slice-069 code-Critic findings discharged (M1 + M2 + m1 + m2 + m3 + m4 + m5 + m6)

- **Status**: PASS
- **Evidence**: `grep -cE "^\| slice-069 (M1|M2|m1|m2|m3|m4|m5|m6) " build-log.md` → **8**. Per-finding:
  - slice-069 M1 (count "9 → 10" `_SECRET_PATTERNS`): FIXED — `methodology-changelog.md:45 + L59` + `architecture/decisions/ADR-066-track-vault-in-git.md:49 + L59 + L80`.
  - slice-069 M2 (BC-PROJ-10 paired-pin completion): FIXED — `tests/methodology/test_methodology_changelog.py` adds `test_v_0_70_0_adr_066_entry_present_in_repo` + `test_v_0_70_0_adr_066_shippability_consumer_propagation` (both PASS); `architecture/shippability.md` row #69 cites both test function names.
  - slice-069 m1 (file count drift 633→644/65504): FIXED — `methodology-changelog.md:45 + L61 + L67`.
  - slice-069 m2 (PII narrative 113/9/1 → 36/141): FIXED — `methodology-changelog.md:66`.
  - slice-069 m3 (600-word paragraph split): FIXED — `methodology-changelog.md:39` restructured into 1-sentence headline + 4 cross-references to existing **Primary deliverables** sub-bullets.
  - slice-069 m4 (.gitignore comment consolidation): FIXED — `.gitignore:10-15` consolidated.
  - slice-069 m5 (--detach HEAD codification): FIXED — `tools/branch_workflow_audit.py:29-37` operational note added to module-level docstring.
  - slice-069 m6 (BC-1 false-positive class): **DEFER-AGAIN** (honest deferral per /critique M2 ACCEPTED-FIXED) — /critic-calibrate proposal target; lands at slice-072+ if N=3 cumulative recurs.
- **Notes**: 2 new paired-pin tests pass; MCFS-1 forward-sync clean.

### AC#4: All 11 slice-070 code-Critic findings on `tools/slice_queue_writer.py` discharged (M1-M6 + m1-m5)

- **Status**: PASS
- **Evidence**: `grep -cE "^\| slice-070 (M1|M2|M3|M4|M5|M6|m1|m2|m3|m4|m5) " build-log.md` → **11**. Per-finding:
  - slice-070 M1 (4-step canonical path-normalization): FIXED — `tools/slice_queue_writer.py:248-326` `_discover_known_repo_roots` + `_normalize_abs_to_repo_relative` helpers added.
  - slice-070 M2 (_PATH_SHAPED_RE module constant): FIXED — `tools/slice_queue_writer.py:90-99` extracted; verbatim alignment to existing test-side regex.
  - slice-070 M3 (PRIMARY filter): FIXED — `tools/slice_queue_writer.py:404-411` PRIMARY return wrapped with `_is_path_shaped`.
  - slice-070 M4 (MappingProxyType wrap): FIXED — `tools/slice_queue_writer.py:346-350` `types.MappingProxyType(out)` wrap.
  - slice-070 M5 (`unknown` sentinel-skip): FIXED — `tests/bugs/test_psq_1_blast_radius_dict_leak.py` AC#3 loop skips `unknown`; new `test_unknown_cell_is_documented_sentinel_not_an_offender` PASS.
  - slice-070 M6 (subprocess patch SUT-bound): FIXED — 5 `patch.object(subprocess, "run", ...)` → `patch("tools.slice_queue_writer.subprocess.run", ...)`.
  - slice-070 m1 (autouse cache_clear): FIXED — `tests/bugs/test_psq_1_blast_radius_dict_leak.py` module-level autouse fixture added.
  - slice-070 m2 (--from fallback retry test): FIXED — new `test_call_graphify_blast_radius_falls_back_to_from_flag_on_node_not_found` PASS.
  - slice-070 m3 (build-log honesty): **ALREADY-FIXED-AT-/reflect** at slice-070 (build-log row confirms; no work this slice).
  - slice-070 m4 (id_to_path eager build): FIXED — `tools/slice_queue_writer.py:455-458` moved post-JSON-parse.
  - slice-070 m5 (_FORWARD_COMPAT_PATH_KEYS extraction): FIXED — `tools/slice_queue_writer.py:101-108` module-level constant; new `test_forward_compat_path_keys_docstring_in_sync_with_constant` PASS.
- **Notes**: 27 tests pass in tests/bugs/test_psq_1_blast_radius_dict_leak.py.

### AC#5: Full pytest ≥ 950 PASS + shippability ≥ 70/70 PASS + 14 Step-6 audits clean + slice's own /code-review surfaces 0 new structural Majors

- **Status**: PASS
- **Evidence**:
  - **Full pytest**: `$PY -m pytest tests/ -q` → **966 passed in 36.13s** (slice-070 baseline was 950; +16 net new = 8 new test functions per design.md + 1 m-add-1 drift-prevention test + 4+3 parametrized cases). Exit 0.
  - **Shippability runner**: `$PY -m tools.shippability_runner architecture/shippability.md` → **70 row(s), 70 PASS, 0 FAIL**. Exit 0.
  - **14 Step-6 audits clean** (per build-log.md L19): BRANCH-2, UTF8-STDOUT-1, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, WIRE-1 (zero-row), TF-1 (vacuous — test-first=false), WS-1 (vacuous), ETC-1 (vacuous), CSP-1 (skipped — not Heavy), SUP-1, PMI-1 (26/6/29), INST-1, RR-1, DR-1, TRI-1, CAD-1, OSDG-1 (11/11 drift tests). PLUS 2 Important defer-with-rationale (BC-1 BC-GLOBAL-2 prose-vs-automation N=3 cumulative; LINT-MOCK-1 13 Important findings inherited from slice-070 pattern; both deferrals fully rationalized in build-log Events §).
  - **Slice's own /code-review**: `code-review.md` → **FINDINGS 0 Blockers + 0 Majors + 5 Minors** (all advisory per CRSI-1 v1 walking-skeleton; deferred to slice-072+ bundled-cleanup nomination). **AC#5 must-not-defer "0 new structural Majors" SATISFIED.**

## VAL-1 layered safety checks (Step 5b)

- **Layer A (credential scan)**: 0 secrets detected. Clean.
- **Layer B (dep hallucination)**: 0 import findings. Clean. (Slice introduces no new imports beyond stdlib + already-declared tools.* imports.)
- **Suppressed (allowlisted)**: 0.

## Walking-skeleton (Step 5c) + Exploratory-charter (Step 5d) audits

- **WS-1**: not enabled (`**Walking-skeleton**: false` per mission-brief L7) — vacuous clean per opt-in default-off discipline.
- **ETC-1**: not enabled (`**Exploratory-charter**: false` per mission-brief L8) — vacuous clean.

## Multi-instance validation

- **Required?**: no
- **Result**: N/A — this slice is a methodology-internal cleanup with no user/device/account multi-instance surface. All ACs are single-instance disposition discharges against the slice's own diff.

## Pre-catalog gates (Step 5.5 prerequisites)

- **SCMD-1** (`tools.shippability_decoupling_audit`): clean. 70 row(s); 695 cited fn(s); 0 incidental couplings.
- **PTFCD-1 sub-mode (b)** (`tools.shippability_path_audit`): clean. 70 row(s); 365 test-path tokens; all files and cited functions exist.

## Shippability catalog (Step 5.5)

- **Runner**: `$PY -m tools.shippability_runner architecture/shippability.md`
- **Result**: **70 row(s), 70 PASS, 0 FAIL**. Exit 0.
- **Regression check**: clean. No past slice's critical-path test was broken by this slice's edits.

## Reality surprises

None substantive. One operational discovery captured in build-log.md §Discovered:
- **graphify-out/ + diagnose-out/ cp-r tax pattern persists post-vault-in-git** (N=6 cumulative; was N=5 at slice-070). User-flagged "we need a better solution" at Phase E mid-slice smoke. Structural fix nominees for slice-072+: (a) un-gitignore these dirs (parallel to slice-069 approach); (b) post-/build-slice symlink discipline; (c) explicit cp-r step in BRANCH-2 worktree-create SKILL.md prose. NOT a slice defect — known pre-existing operational pattern; flagged for /reflect §Discovered + slice-072+ nomination.

## Aggregate verdict

**Result: PASS** — all 5 ACs satisfied with evidence; VAL-1 + pre-catalog gates + shippability all clean; 0 reality surprises requiring immediate remediation; 5 code-Critic minors all deferrable per CRSI-1 v1 walking-skeleton voluntary-restraint precedent.
