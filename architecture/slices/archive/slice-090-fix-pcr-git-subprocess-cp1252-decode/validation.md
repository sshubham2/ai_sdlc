# Validation: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Date**: 2026-05-31
**Result**: PARTIAL — slice's own ACs all PASS; shippability catalog has 3 sibling-induced FAILs (R-28) pending user-approved deferral. Zero slice-090 regressions.

## Per-criterion results

### AC1: Both repro tests pass (cp1252 round-trip + claim extraction)
- **Status**: PASS
- **Evidence**: Real Windows/cp1252 host, real git repos with real emoji (🏆) content — `pytest tests/bugs/test_pcr_git_subprocess_cp1252_decode.py -v` → `test_git_show_stage_decodes_utf8_content_on_cp1252_host PASSED`, `test_diagnose_conflict_extracts_claims_from_utf8_slice_queue_on_cp1252_host PASSED` (2 passed). NOT skipped — `_host_decodes_utf8_natively()` is False here (cp1252), so the behavioral tests ran for real.
- **Notes**: Pre-fix these failed with `UnicodeDecodeError: byte 0x8f` in the reader thread (the user's exact crash signature). Post-fix they round-trip losslessly.

### AC2: All 9 text=True git subprocess sites carry encoding="utf-8"; 4 byte-mode excluded
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_parallel_conflict_resolver_git_encoding.py -v` → `test_all_git_decode_sites_specify_utf8_encoding PASSED`, `test_exactly_nine_git_decode_sites_byte_mode_sites_excluded PASSED`. AST scan of the real module confirms exactly 9 decode sites all carry `encoding="utf-8"`, 4 byte-mode staging sites carry none (APED-1).

### AC3: No PCR-suite regression
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_parallel_conflict_resolution_log_hard.py test_parallel_conflict_resolution_log_vault_claim.py test_parallel_conflict_resolver_truncated_baseline.py` → 13 passed. Full suite (separately): 1270 passed (the only 2 failures are the sibling-induced commit-slice drift — see below).

## Multi-instance validation
**Required?**: no — internal git-subprocess decode fix; no multi-user/device/account surface.
**Result**: not-applicable

## VAL-1 layered safety checks
- **Layer A (credentials)**: 0 secrets. **Layer B (dep hallucination)**: 0 findings. Clean.

## Shippability regressions

**Catalog run**: `tools.shippability_runner` → 95 rows, **92 PASS, 3 FAIL**.

All 3 FAIL rows fail ONLY because they bundle one of these 2 tests; every other test in each row PASSES:
- `tests/methodology/test_commit_slice_skill_drift.py::test_commit_slice_skill_md_in_repo_byte_equal_installed` (in 2 failing rows)
- `tests/methodology/test_commit_slice_skill_vault_claim_dispatch.py::test_in_repo_and_installed_forward_synced` (in 1 failing row)

**Classification: SIBLING-INDUCED (R-28), NOT a slice-090 regression.**
- Evidence: slice-090's changeset = {`tools/parallel_conflict_resolver.py`, 2 new test files}. `git diff HEAD -- skills/commit-slice/SKILL.md` is **EMPTY** — slice-090 never touched it.
- Root cause: the in-flight slice-089 (`make-commit-slice-stale-branch-check-parallel-slice-aware`) has its ADR-081 stale-branch-classifier edits in the **installed** `~/.claude/skills/commit-slice/SKILL.md` (404 lines) but NOT committed to the in-repo copy (390 lines). The 2 drift tests compare in-repo-committed vs installed and fail on that divergence.
- This is the documented R-28 shared-`~/.claude/` contention class (precedent: slice-087, where 13 shippability + 4 forward-sync rows were sibling-induced by parallel slice-088, user-approved deferral, zero regressions).

**Disposition**: per R-28 procedure — documented deferral, NEVER clobber the shared install; reconcile when slice-089 commits its in-repo `skills/commit-slice/SKILL.md` (so in-repo == installed again). **USER-APPROVED DEFERRAL 2026-05-31** (Step 5.5 + PCA-1 gate cleared): the 3 FAILs are sibling-induced by slice-089, zero slice-090 regressions; proceed to /reflect.

## Reality surprises
- The build/validation empirically surfaced that slice-089 has leaked its commit-slice SKILL.md edits into the installed plugin without committing them in-repo — a concrete instance of R-28 (and a hygiene item for slice-089 to close). It also corroborates why slice-090 built in-place (WORKTREE=skip): the parallel slices' shared-state entanglement is real.
