# Validation: Slice 075 close-merge-substep-3-worktree-collision

**Date**: 2026-05-28
**Result**: PASS

## Per-criterion results

### AC#1: skills/commit-slice/SKILL.md Step 5b sub-step 3 prose includes explicit main-tree-transition step BEFORE `git checkout <default>`, using canonical worktree-aware form

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_includes_main_tree_transition_before_checkout -v` → PASSED [50%]; APED-1 empirical verification: `cd "$main_tree"` literal present in Step 5b section AND appears BEFORE canonical invocation literal `git checkout $default` (offset comparison: cd at lower offset than checkout-invocation). Test pin uses tightened invocation-specific literal `git checkout $default` (not bare `git checkout`) per build-time RSAD-1 finding resolution (FINDING event at 05:54 in build-log.md) — narration mentions of `git checkout` no longer pollute the ordering check.
- **Notes**: 3 prose-surgery edits at SKILL.md Step 5b executed cleanly. The `cd "$main_tree"` transition uses the canonical `main_tree=$(git worktree list --porcelain | awk '/^worktree / {print $2; exit}')` extraction documented at git-scm.com/docs/git-worktree (main-worktree-listed-first porcelain ordering invariant). Empirically verified: APED-1 execution returns `C:/Users/sshub/ai_sdlc` (main tree) from this worktree's invocation.

### AC#2: skills/commit-slice/SKILL.md Step 5b pre-flight WT-clean check no longer contradicts sub-step 2's commit semantics

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_does_not_contradict_substep_2_commit -v` → PASSED [50%]; APED-1 empirical verification: (a) Pre-flight guardrails sub-block in Step 5b does NOT contain `git status --porcelain` literal (only Stale-slice-branch check remains as preflight); (b) `2.1.` sub-step marker present in Step 5b (anchor unique to post-fix prose); (c) `git status --porcelain` literal present within the contiguous block from `2.1.` to `2.5.` (the lifted WT-clean check lives inside the new sub-step 2.1. post-commit guardrail block).
- **Notes**: WT-clean check lifted from pre-flight (was L168) to NEW sub-step 2.1. between sub-step 2 (L173 commit) and sub-step 2.5 (L174 PSQ-3 rebase). Decimal `2.1.` marker mirrors slice-073 PSQ-3 sub-step `2.5.` precedent for inserting intermediate sub-steps between integer-numbered steps (CommonMark ordered-list compliant per /critique m2 ACCEPTED-FIXED). Sub-step 2.1. is vacuous on PSQ-3 re-entry by construction per ADR-068 §Re-entry semantics — preservation verified.

### AC#3: paired pin for AC#1 — canonical `git worktree list --porcelain | awk ...` extraction shape

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py::test_substep_3_main_tree_transition_uses_canonical_worktree_list_awk_extraction -v` → PASSED [100%]; APED-1 empirical verification: both `git worktree list --porcelain` AND `awk '/^worktree / {print $2; exit}'` literals present in Step 5b section as the `$main_tree` resolution mechanism. Sibling-but-distinct from Step 5b sub-step 5's specific-branch extraction `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'` — shared `/^worktree /` regex anchor + divergent AWK action (per /critique m1 ACCEPTED-FIXED clarification).
- **Notes**: Byte-level cross-spec parity check (per slice-073 code-Critic M1 `2>/dev/null` divergence class N=2 precedent) confirms NO drift: all 3 awk-with-worktree sites in SKILL.md (sub-step 3 + sub-step 5 + Step 5d sub-step 5) share identical `/^worktree /` regex anchors with divergent AWK actions as designed.

### AC#4: paired pin for AC#2 — silent-WT-discard local-state-loss protection intent preserved at new sub-step 2.1. position

- **Status**: PASS
- **Evidence**: `$PY -m pytest tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py::test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent -v` → PASSED [100%]; APED-1 empirical verification: within the `2.1.` sub-step block, all 3 intent literals present — `silent-WT-discard` (the intent-preservation phrase per /critique M5 ACCEPTED-PENDING) + `STOP` (stop-on-non-empty semantic) + `Print:` (diagnostic-print pattern).
- **Notes**: Assertion is `2.1.` block-anchored via `_extract_substep_2_1_block()` helper with prelude guard (per /critique-review M-add-1 ACCEPTED-FIXED — prior whole-section presence-check would PASS pre-fix because L168 already contained all 3 literals; the `2.1.` anchor guarantees TF-1 WRITTEN-FAILING). Build-time RSAD-1 verification: stashed pre-fix SKILL.md + ran test → fails at prelude guard "Step 5b section must contain a `2.1.` sub-step marker"; restored post-fix → PASSes. Code-Critic m1 logged latent narration-leakage risk (defer to slice-076+ bundle).

### AC#5: /validate-slice CLEAN (meta-AC)

- **Status**: PASS
- **Evidence**: This very validate-slice run. Captured sub-results:
  - **Full pytest**: `$PY -m pytest --no-header -q` → `1006 passed in 39.97s` (1002 baseline + 4 new structural-pin tests)
  - **Shippability runner**: `$PY -m tools.shippability_runner architecture/shippability.md` → `Shippability catalog run: 74 row(s), 74 PASS, 0 FAIL`
  - **SCMD-1 pre-catalog audit**: `clean. 74 row(s); 783 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=781`
  - **PTFCD-1 pre-catalog audit**: `clean. 74 row(s), 381 test-path token(s) — all files and cited functions exist`
  - **SCMD-1 (mini-CAD skill-drift)**: `test_commit_slice_skill_drift.py` PASS — in-repo skills/commit-slice/SKILL.md content-equal modulo line endings to installed ~/.claude/skills/commit-slice/SKILL.md
  - **CAD-1**: clean — agents/critique.md in-repo ↔ installed parity
  - **16+ Step 6 audits** (run at /build-slice Phase F): TF-1 (5/5 PASSING) + WIRE-1 + BRANCH-2 + UTF8-STDOUT-1 + CRP-1 + PCA-1 + BCI-1 + MCFS-1 + STP-1 + AVFS-1 + TVFS-1 + NAW-1 + CAD-1 + PMI-1 (v0.72.0 unchanged — MEPD-1 EXCLUDE confirmed) + SCMD-1 + shippability runner + LINT-MOCK ALL CLEAN
  - **VAL-1**: `0 secret(s), 0 import finding(s), 0 suppressed (allowlisted)` — both Layer A (credential scan) + Layer B (Python dependency hallucination check) clean
  - **WS-1 + ETC-1**: default-off (test-first=true / walking-skeleton=false / exploratory-charter=false per mission-brief frontmatter — correctly skipped per opt-in semantics)
- **Notes**: AC#5 is the meta-AC verified by running this very /validate-slice + the post-build audit suite. All sub-claims (≥1004 pytest, ≥74/74 shippability, SCMD-1+CAD-1 clean, 16+ Step 6 audits clean) empirically met. Exceeds predicted thresholds (1006 > 1004 pytest baseline; 74/74 == 74/74 shippability).

## Multi-instance validation

**Required?**: no
**Result**: not-applicable
**Evidence**: Slice is methodology-prose-fix (MEPD-1 EXCLUDE) modifying skill prose + adding structural-pin tests. No multi-user / multi-device / sync / sharing / cross-account flows.

## Reality surprises

None. The slice executed per design.md plan with 2 in-band RSAD-1 defects surfaced + resolved at mid-slice smoke (FINDING events at build-log L11-12; resolution within original AC scope via annotation-rephrase + AC#1 test-pin tightening). The dual-Critic stack's M-add-1 + M-add-2 (RSAD-1 class) caught the assertion-strength weaknesses at design time; the build-time 2 additional RSAD-1 surfacings confirm the recurrence pattern — calibration signal extends RSAD-1 annotation-literal-pollution class to N=3 cumulative on this slice alone (2 caught at build-time + 1 latent post-finish per code-Critic m1).

## Shippability regressions

**Result**: NONE — 74/74 PASS, 0 FAIL.

Pre-catalog gates (both clean):
- SCMD-1 decoupling audit (`$PY -m tools.shippability_decoupling_audit architecture/shippability.md`): `clean. 74 row(s); 783 cited fn(s) — incidental=0 essential_registered=2 essential_unregistered=0 clean=781`
- PTFCD-1 path audit (`$PY -m tools.shippability_path_audit architecture/shippability.md`): `clean. 74 row(s), 381 test-path token(s) — all files and cited functions exist`

Catalog run (`$PY -m tools.shippability_runner architecture/shippability.md`): `Shippability catalog run: 74 row(s), 74 PASS, 0 FAIL`. No past slice broken by slice-075.
