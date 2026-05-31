# Validation: Slice 087 add-stranded-slice-detection-to-slice

**Date**: 2026-05-31
**Result**: PARTIAL — slice-087's own 5 ACs all PASS; the shippability catalog has 13 FAILs that are **100% sibling-induced** (a single CAD-1 content-equality test, drifted by parallel slice-088's PFS-1 install-sync), ZERO genuine slice-087 regressions. Requires a user-approved deferral (reconciles at merge).

## Per-criterion results

### AC1: New tool classifies every unmerged `slice/*` branch into the 4-class divergence model (+ INDETERMINATE), reusing slice-077 + slice-072 machinery; advisory exit contract
- **Status**: PASS
- **Evidence**: real run against the live repo —
  ```
  $ $PY -m tools.stranded_slice_audit --root <worktree>
  stranded-slice-audit → status: clean (0 divergent)
    info  slice/087-…  [in-progress] wt=…  milestone stage=build; pre-reflect
    info  slice/088-add-project-frame-synthesizer  [in-progress] wt=…  milestone stage=complete; pre-reflect
  (exit 0)
  ```
  9/9 behavioral cases PASS (`test_stranded_slice_audit.py`), exercising all 5 classes + the advisory `status ∈ {clean, divergent}` + per-entry `{branch, worktree_path, klass, halt, vault_state, claimed_by, ahead, dirty, reason}` JSON contract. Exit 0 advisory / exit 2 usage / no exit 1 verified. Reuse verified live (the executed run drives `detect_active_worktrees` + `classify_worktree_state` + `_resolve_default_branch`).
- **Notes**: B1 (code-review) fixed — `_TERMINAL_STAGES = {"reflect", "complete"}` so a bare-branch terminal `stage: complete` (the vault's real terminal vocabulary) classifies STRANDED-COMPLETE; pinned by case 4i.

### AC2: `/slice` Prerequisite consult halts ONLY on `status: divergent`; surfaces informational entries and proceeds (parallel-safe)
- **Status**: PASS
- **Evidence**: structural-pin `test_slice_skill_stranded_prereq.py` PASS (asserts the consult prose, halt-on-divergent + AskUserQuestion gate + proceed-anyway + the clean+informational proceed-without-gate path + exit-2 fail-visible). Live dry-run: the detector returns `status: clean` against the real two-worktree repo (087 + 088 both IN-PROGRESS) → the parallel-safe no-gate path is exercised (a healthy parallel slice does NOT halt `/slice`).
- **Notes**: this is the binding behavioral fix for the PARKED flaw — validated against real parallel state.

### AC3: `/pulse` surfaces the bare-unmerged-branch-without-worktree signal (rendering `klass`)
- **Status**: PASS
- **Evidence**: structural-pin `test_pulse_skill_stranded_signal.py` PASS; the bullet is present in `skills/pulse/SKILL.md` and OSDG-1-synced to the installed copy. Slice-077's offset pins still hold (`test_pulse_skill_worktree_awareness.py` PASS — M4 offset-safety).

### AC4: Behavioral battery (incl. the binding parallel-safety pin) + OSDG-1 content-equality
- **Status**: PASS
- **Evidence**: 9 behavioral cases PASS — STRANDED-COMPLETE (4a, incl. archive-only-on-branch M1), ORPHANED (4b), **IN-PROGRESS parallel-safety (4c — `status: clean`, no halt)**, CLAIMED-BY-OTHER (4d), clean (4e), recovery/*+merged not flagged (4f), INDETERMINATE on malformed milestone (4g), own-pushed STRANDED-COMPLETE (4h), **terminal `stage: complete` bare branch (4i — B1 fix)**. OSDG-1 drift tests PASS for both `skills/slice` + `skills/pulse`.
- **Notes**: 4c must fail against a flag-all impl and pass against the classifier — the binding regression guard for the flaw the user caught.

### AC5: R-27 registered + BC-PROJ-9 5-surface inventory + full suite + Step-6 audits
- **Status**: PASS
- **Evidence**: R-27 registered (Status: mitigating, with the Relationship-to-R-22 clause). 5-surface inventory consistent (plugin.yaml + `_CANONICAL_TOOLS` + INSTALL.md L22/L166 33→34 + slice-077 inventory test 33→34 + `_ROOT_ONLY_TOOLS`); `test_stranded_slice_audit_tool_inventory.py` + `test_install_md_correctness.py` PASS. PMI-1 (34 tools) / INST-1 (34/34) / UTF8-STDOUT-1 (34 clean) clean. All slice-owned Step-6 audits green: WIRE-1, BC-1 (Critical acked), TF-1 (15 rows), BRANCH-1, CRP-1, PCA-1, BCI-1, STP-1, NAW-1, DCE-1, mock-budget, shippability-path/decoupling.

## VAL-1 layered safety checks
- **Layer A (credentials)**: 0 secrets. PASS.
- **Layer B (dependency hallucination)**: 0 findings (all imports resolve: `tools.*` internal, stdlib, `--imports-allowlist tests`). PASS.

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
Not applicable — `Walking-skeleton: false`, `Exploratory-charter: false`.

## Shippability catalog regression check
**Run**: `tools.shippability_runner` (SCMD-1 + PTFCD-1 pre-gates both clean) — **92 rows, 79 PASS, 13 FAIL**.

**All 13 FAILs share ONE root cause** (the "distinct failing test files" set is a single file): `tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal` (+ the `..._audit_clean_at_slice_021_ship` companion). Failing rows: #7, #9, #11, #13, #15, #16, #18, #21, #22, #24, #25, #33, #39 — every catalog row whose critical-path bundle happens to include the CAD-1 drift test.

**Attribution — sibling-induced, NOT a slice-087 regression**: the shared installed `~/.claude/agents/critique.md` carries the **parallel sibling slice-088's** PFS-1 edit (v0.78.0 / ADR-080 / project-frame.md block), forward-synced from slice-088's worktree. slice-087 makes ZERO changes to `agents/` (`git diff HEAD -- agents/` empty). The CAD-1 content-equality test compares slice-087's in-repo agent (pre-PFS-1 base) against the slice-088-advanced install → drift. slice-087 cannot clear this without either clobbering slice-088's PFS-1 install-sync or pulling slice-088's unrelated agent edit into slice-087 — both wrong.

**Disposition**: **DEFERRED — user-approved 2026-05-31** (PCA-1 PARTIAL gate). Reconciles automatically at merge: slice-087 has no `agents/` conflict; once slice-088 merges (or slice-087 rebases onto a slice-088-merged master), in-repo == installed and all 13 rows pass. No fix is correct from within slice-087. The user accepted the deferral on the basis that 100% of the FAILs are slice-088-induced CAD-1 install-drift with zero genuine slice-087 regressions.

## Reality surprises
- **The PSQ shared-install hazard is real and broad** (not just CAD-1): a version-bumping parallel sibling forward-syncing the single shared `~/.claude/` causes the OTHER worktree's forward-sync/content-equality audits (CAD-1, MCFS-1, AVFS-1, TVFS-1) AND any shippability row bundling those tests to fail — 13 catalog rows here. None are defects in the slice under validation. Strong `/reflect` + `/critic-calibrate` candidate: forward-sync/content-equality gates compared against a single shared install are structurally fragile under parallel slices; consider per-worktree-scoped comparison or merge-time-only enforcement.
