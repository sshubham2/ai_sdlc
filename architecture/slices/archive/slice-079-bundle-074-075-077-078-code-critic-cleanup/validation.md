# Validation: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**Date**: 2026-05-29
**Result**: PASS (AC#5 resolved by user decision 2026-05-29 — archive-immutability carve-out; see AC5 below)

> **User decision (2026-05-29, validate-slice PCA-1 PARTIAL gate)**: AC#5's source-pending-items.txt text-removal sub-clause is accepted as a documented non-actionable deferral (**DEFER-6**, archive-immutability — same basis as DEFER-1/3/4/5). AC#5's substantive obligation (fix + regression test for P1.1 + P3.10) is fully met, so AC#5 is treated as PASS-with-carve-out and the aggregate result is PASS. The forward handoff (routing P3.10' `find-real-mojibake-source` + still-open slice-075 P-items into a fresh live tracker) is delegated to /reflect, where handoff-file authorship naturally belongs.

This is a self-hosting methodology slice — "real environment" = running the actual audits + regression tests against the real repo artifacts (not synthetic fixtures). Full pytest suite: **1125 passed / 0 failed**. Shippability catalog: **83 rows, 83 PASS, 0 FAIL** (no regression). VAL-1 layers: 0 secrets, 0 import findings.

## Per-criterion results

### AC1: slice-074 code-Critic findings m1–m5 each have a fix landed + regression test, catalogued in shippability.md
- **Status**: PASS
- **Evidence**: Fix A (m1/P1.1 var pre-amble) → `test_build_slice_skill_branch_state_preamble.py` (2 tests, FAIL→PASS confirmed at Phase C baseline); Fix B (m1 concrete pathspec) → `test_build_slice_skill_dirty_tree_resolution.py::test_branch_state_no_bare_git_add_placeholder`; Fix C (m2 cp-r count ==4), Fix D (m3 regex doc), Fix E (m4 shared helper) → `test_build_slice_skill_cp_r_step.py` + `_dirty_tree_resolution.py` + `test_skill_parse_helpers.py`; Fix F (m5 subprocess stderr) → `test_r_20_retired.py::test_audit_failure_surfaces_stderr`. Shippability rows 79 cover the cluster. All green in the 1125-test suite.

### AC2: slice-075 code-Critic findings m1–m2 each have a fix landed + regression test
- **Status**: PASS
- **Evidence**: Fix G (m1 line-start anchor + narration-leakage guard) → `test_commit_slice_skill_merge_wt_clean_preflight_ordering.py` (2 tests; empirically confirmed substring `.find("2.1.")` matched a narration forward-ref → `silent-WT-discard` count 2, line-start anchor → count 1). m2 (stale `enable-parallel-slice-pending-items.txt` anchors in archived slice-075 mission-brief/design) DEFERRED per design.md DEFER-1 (archive-immutability) — authorized by mission-brief §Out-of-scope DEFER-with-rationale carve-out. Shippability row 80.

### AC3: slice-077 12 actionable findings each fixed+tested OR documented-DEFER
- **Status**: PASS
- **Evidence**: Fix H (M2 pytest.skip drop + new unresolvable-default test), Fix I (m3 unused pytest), Fix J (m4 unused WorktreeStateClassification), Fix K (m5 `_UNKNOWN_REASON_WARN_TEMPLATES`), Fix L (m6 bare-repo), Fix M (m8 BOM), Fix N (m9 stage exact-key) → `tests/skills/pulse/*` (27 tests) + `test_pulse_tests_have_no_unused_imports.py`. DEFER-2 (M1+m1 → parallel-slice-family-parity-audit slice), DEFER-3 (m2+m10 archive-immutability), DEFER-4 (m7 archive-immutability) per design.md. AC#3 explicitly permits DEFER-with-rationale. Shippability rows 81-82.

### AC4: slice-078 code-Critic findings m1–m5 each have a fix landed + regression test
- **Status**: PASS
- **Evidence**: Fix O (m1 6-arg formatter DRY — incl. the in-loop-added behavioral discriminator `test_formatter_uses_passed_winner_loser_not_diag_claim_history` closing code-review M1), Fix P (m2 `_QueueCandidate` NamedTuple + MISSING-FIELD), Fix Q (m3 atomicity docstring), Fix R (m5 catch-order comment) → `tests/methodology/test_pcr_2a_*` (4 files; existing `test_pcr_2a_vault_claim_resolver.py` no-regression). m4 (archived design.md stale `4 tests` claim) DEFERRED per DEFER-5 (archive-immutability). Shippability row 83.

### AC5: P1.1 + P3.10 each have a fix/reframe + regression test; both entries' current text removed from source-pending-items.txt
- **Status**: **PASS** (substantive obligation met; text-removal sub-clause = DEFER-6 archive-immutability carve-out, user-approved 2026-05-29)
- **Cause (of the sub-clause carve-out)**: **spec gap** — the AC's text-removal sub-clause references a `source-pending-items.txt` that has since been **archived**.
- **Evidence (substantive part — MET)**: P1.1 (build-slice point-4 variable-scope footgun) shipped a full fix via Fix A (vars extracted to shared pre-amble above the numbered Branch-state list), pinned by `test_build_slice_skill_branch_state_preamble.py`. P3.10 (slice_queue_writer mojibake) reframed per /critique B2+M3 to a structural-pin regression-guard (Fix S), pinned by `test_slice_queue_writer_utf8_encoding.py` (2 tests; FAIL→PASS via fixture-mutation; real source already UTF-8-compliant at all 9 I/O sites).
- **Evidence (unmet sub-clause)**: "both entries' current text removed from source-pending-items.txt" + "route P3.10' to source-pending-items" cannot be performed. The ONLY `source-pending-items.txt` in the repo is `architecture/slices/archive/slice-075-.../source-pending-items.txt` (where P1.1 @L37 + P3.10 @L291 live). slice-075 is archived; editing its frozen handoff file violates archive-immutability (the same convention design.md DEFER-1/3/4/5 rely on). No live source-pending-items.txt exists for slice-079 (git confirms it never existed in the slice-079 folder). The AC was written at /slice time assuming a live handoff file (as slice-075 had); reality archived it before build.
- **Action**: RESOLVED — user selected the archive-immutability carve-out (2026-05-29). Recorded as DEFER-6; AC#5 PASS-with-carve-out; aggregate PASS; PCA-1 gate cleared → /reflect proceeds. /reflect authors the forward handoff (P3.10' + open P-items into a fresh tracker).

## Multi-instance validation
**Required?**: no (methodology/self-hosting slice — no multi-user/device/account surface)
**Result**: not-applicable

## Shippability regressions
None. 83/83 catalog rows PASS.

## Reality surprises
- **AC#5 source-pending-items.txt is archived, not live.** The mission-brief assumed a live handoff tracker; by build time slice-075 (which owns the file) was archived. The substantive cleanup (fix+test) landed cleanly; only the file-mutation bookkeeping is blocked. This is the same spec-vs-archive tension that produced design.md DEFER-1/3/4/5 — but AC#5's sub-clause was not pre-carved-out as a DEFER, so it surfaces here as PARTIAL for user adjudication. Forward handoff hygiene (carrying P3.10' + still-open P-items into a fresh tracker) is naturally /reflect's job, not /build-slice's.
