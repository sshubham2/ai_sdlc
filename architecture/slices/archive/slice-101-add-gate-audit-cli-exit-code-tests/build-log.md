# Build log: Slice 101 add-gate-audit-cli-exit-code-tests

**Date**: 2026-06-02
**Result**: SHIPPED

## Events (append-only — written per Step 7c)

- 2026-06-02 BUILD: prereqs clean — branch slice/101-…, CRP-1 clean, worktree pre-seeded (BRANCH-3, no re-seed)
- 2026-06-02 BUILD: wrote tests/methodology/test_gate_audit_cli_exit_codes.py (18 tests: 8 block-path + paired kind-asserts, 6 clean-path, 2 exit-2)
- 2026-06-02 TEST: new module 18 passed (against current code — wiring exists, tests pin it)
- 2026-06-02 TEST: AC2 non-vacuity harness — all 8 block-path tests FAIL under `main()→return 0` mutation; all 8 tools reverted (git diff tools/ empty)
- 2026-06-02 FINDING: full suite showed test_lintmock returning 0 not 1 — diagnosed as STALE BYTECODE (harness's byte-length-identical `1`→`0` mutation defeated Python's .pyc mtime+size staleness check after git-checkout revert)
- 2026-06-02 BUILD: cleared __pycache__ → lint test passes alone + full module 18/18
- 2026-06-02 TEST: full methodology suite 1345 passed (0 failed) from clean bytecode
- 2026-06-02 TEST: Step-6 audits all green (BRANCH-1/WIRE-1/CRP-1/LINT-MOCK/UTF8/PCA-1/NAW-1/STP-1/SVW-1/BCI-1/MCFS-1/AVFS-1/TVFS-1 exit 0; BC-1 --strict ack BC-PROJ-3+BC-GLOBAL-2 exit 0)

## Summary

### Plan executed
One consolidated test module `tests/methodology/test_gate_audit_cli_exit_codes.py` pinning the CLI block-path (exit-1), clean-path (exit-0), and two exit-2 usage paths of the 8 mandatory gate audits via in-process `main(argv)` int-assertion paired with a violation-kind cause-assert (slice-101 /critique M1). Reused existing on-disk fixtures where available (`no_triage_section_critique.md`, `missing_section_review.md`, `missing_cells_design.md`, `broken_impl_threat.md`, `mock_budget_too_many.py`/`clean.py`); built tmp fixtures for PMI-1 (complete manifest + orphan skill), CSP-1 (broken_impl threat copied into tmp project), PTFCD-1 (6-col SCMD-1 catalog), BRANCH-1 (deterministic `branch -M trunk` + local `init.defaultBranch trunk` repo). No production code changed.

### Mid-slice smoke gate
**Result**: PASS (build is one module; the smoke gate = new module green + one mutation). New module 18/18 + the AC2 mutation pass below.

### AC2 non-vacuity by mutation (8-row evidence)
For each audit: force `main()`'s violations→block-code to `return 0`, run that audit's block-path test, confirm it FAILS, then `git checkout` revert. Mutation proves int-DEPENDENCE; the paired kind-assert proves CAUSE-pinning (slice-101 m1). Row 2 (TRI-1): the cause-pin is the `is_file()` precondition, not the kind-assert (a missing file also yields `no-section`).

| Audit (tool) | block-path test | mutation → test FAILED? | reverted? |
|--------------|-----------------|:-----------------------:|:---------:|
| plugin_manifest_audit (PMI-1) | test_pmi1_cli_blocks_on_orphan_skill | YES (non-vacuous) | yes |
| triage_audit (TRI-1) | test_tri1_cli_blocks_on_missing_triage_section | YES | yes |
| mock_budget_lint (LINT-MOCK) | test_lintmock_cli_blocks_on_too_many_mocks | YES | yes |
| critique_review_audit (DR-1) | test_dr1_cli_blocks_on_missing_section | YES | yes |
| wiring_matrix_audit (WIRE-1) | test_wire1_cli_blocks_on_missing_cells | YES | yes |
| cross_spec_parity_audit (CSP-1) | test_csp1_cli_blocks_on_broken_ref | YES | yes |
| shippability_path_audit (PTFCD-1) | test_ptfcd1_cli_blocks_on_phantom_test_path | YES | yes |
| branch_workflow_audit (BRANCH-1) | test_branch1_cli_blocks_on_default_branch | YES | yes |

Harness verdict: `ALL NON-VACUOUS + ALL REVERTED: True` (exit 0). Harness was a throwaway (`_mutation_harness.tmp.py`), deleted; NOT committed.

### Stale-bytecode incident (diagnosed + resolved — NOT a slice defect)
The full suite initially showed `test_lintmock` returning 0 (1 Important violation found, but `main()` returned 0). Root cause: the mutation harness's `return 1`→`return 0` edit is byte-length-identical, so after `git checkout` restored the source, Python's `.pyc` (mtime+size) staleness check matched and served the MUTATED bytecode (`return 0`). Resolution: `Remove-Item -Recurse __pycache__` → recompile from correct source → lint test passes alone + full module 18/18 + full suite 1345 passed. Production code + test are correct (`git diff tools/` empty throughout). Lesson for /reflect: a mutation harness must use a byte-length-CHANGING mutation or clear `__pycache__` after revert.

### Pre-finish gate
- [x] All ACs pass with evidence (AC1 block-path 8/8; AC2 mutation table above; AC3 clean-path 6/6 + cause-asserts; AC4 diff = only tests/methodology/test_gate_audit_cli_exit_codes.py, `git diff tools/`/skills/plugin.yaml/INSTALL/shippability/VERSION all empty) — full per-AC PASS recorded at /validate-slice
- [x] Must-not-defer addressed: non-vacuity (8/8 mutation), pin-the-cause (kind-asserts + is_file for row 2), cp1252-safe (deliverable is in-process — NO subprocess capture; the only subprocess is `_run_git` with `encoding="utf-8"`), no slice-100 files touched / no VERSION bump, no new public surface (test module only)
- [x] /drift-check full mode (drift-log.md `**Trigger**: slice-101 pre-finish gate` appended, 0 blockers/0 majors) + DCE-1 audit clean (exit 0)
- [x] Mid-slice smoke still passes
- [x] No new TODOs / FIXMEs / debug prints (throwaway harness deleted)
- [x] Step-6 tool audits: BRANCH-1, WIRE-1, CRP-1, LINT-MOCK, UTF8-STDOUT-1, PCA-1, NAW-1, STP-1, SVW-1, BCI-1, MCFS-1, AVFS-1, TVFS-1 all exit 0; BC-1 --strict (ack BC-PROJ-3 + BC-GLOBAL-2) exit 0
- [x] Full methodology suite: 1345 passed

### BC-1 Critical attestation
- **BC-PROJ-3 / BC-GLOBAL-2** (no destructive `git checkout`/`restore`/`stash` revert of uncommitted work): the only `git checkout` use was the throwaway mutation harness reverting its OWN injected mutations to tracked `tools/*.py` files (temporary, self-created). No uncommitted user work was destroyed; the untracked deliverable (test module + scaffold) was never a `git checkout` target. Acknowledged.
- BC-PROJ-4 (Important — exercise every affected gate on the real artifact): directly embodied — this slice runs every gate's real CLI on real fixtures + the harness ran each against the real audit. BC-PROJ-5 / BC-PROJ-11 (Important): N/A — no rename/carve-out/count change, no version-literal in any recipe doc.

### Deferrals
- Full `shippability_runner` (AC4 "stays green") deferred to /validate-slice, its canonical home (VAL-1 + shippability regression). The full methodology suite — which includes the new module — is green; no shippability.md row added (deliberate: AC4 parallel-safety with slice-100 forbids touching shippability.md; the new tests are covered by the existing "methodology suite green" catalog claim).

### Design deviations
- None. Built exactly to the post-/critique design (in-process invocation, consolidated module, paired kind-asserts, deterministic branch_workflow recipe, reused fixtures). The CSP-1 fixture reuse (`broken_impl_threat.md`, em-dash heading) inherently sidesteps the M-add-1 double-dash trap.

### Files changed
- `tests/methodology/test_gate_audit_cli_exit_codes.py` (new — the sole production-surface change)
- slice scaffold under `architecture/slices/slice-101-add-gate-audit-cli-exit-code-tests/` (mission-brief, design, critique, critique-review, milestone, build-log)
