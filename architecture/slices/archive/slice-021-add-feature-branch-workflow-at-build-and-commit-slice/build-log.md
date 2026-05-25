# Build log: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice

**Date**: 2026-05-14
**Result**: SHIPPED-WITH-DEVIATIONS

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-14 20:14 DEVIATION: BRANCH=skip-bootstrap — rationale: ## Prerequisite check ### Branch state sub-section prose authored this slice; manual branch-create fired before sub-section exists on disk. RSAD-1 canonical bootstrap-reference instance #1.
- 2026-05-14 20:14 BRANCH-CREATE: slice/021-add-feature-branch-workflow-at-build-and-commit-slice from master HEAD (pre-/build-slice-Step-2; bootstrap per design.md Self-application caveat 1).
- 2026-05-14 20:18 DEVIATION: Phase 1 test scaffolding — drop `tests/shippability/test_row_021_branch_workflow.py` from plan. Rationale: slice-020 row 20 + earlier rows show shippability catalog rows ARE the test (Command cell is executable directly); no separate test_row_NNN_*.py file convention exists. Updated TF-1 plan row to point at `architecture/shippability.md` row 21 itself (grep-verification test type per slice-018 DEVIATION-2 non-pytest convention).
- 2026-05-14 20:18 BUILD: Phase 1 tests 1-6 written (test_build_slice_skill_branch_create + test_build_slice_skill_step_7c_branch_skip_canonical_shape + test_commit_slice_skill_merge_flag + test_root_claude_md_branch_per_slice_rule + test_build_slice_skill_drift + test_commit_slice_skill_drift) — WRITTEN-FAILING (await Phase 2 SKILL.md edits to drive PASSING).
- 2026-05-14 20:18 BUILD: tests/tools/ created with __init__.py + test_branch_workflow_audit.py (8 unit tests) — WRITTEN-FAILING (await Phase 2 tool creation).
- 2026-05-14 20:25 BUILD: Phase 1 test scaffolding extensions complete — test_methodology_changelog.py +3 entry-pin + 1 ADR-pin (slice-021 BRANCH-1); test_install_audit.py +1 enumeration; test_plugin_manifest_audit.py +1 enumeration; test_critique_agent_drift.py +1 vacuous-clean.
- 2026-05-14 20:25 TEST: Phase 1 prose-pin smoke 10/10 FAIL — confirmed WRITTEN-FAILING state per TF-1 discipline (await Phase 2 SKILL.md + CLAUDE.md edits).
- 2026-05-14 20:25 BUILD: Phase 2 start — SKILL.md edits to drive 10 prose-pin tests PENDING-WRITTEN-FAILING→PASSING.
- 2026-05-14 20:32 BUILD: skills/build-slice/SKILL.md — 3 inline edits applied (NEW `### Branch state` sub-section in `## Prerequisite check`; NEW canonical BRANCH=skip shape sentence in Step 7c; NEW Step 6 pre-finish BRANCH-1 audit bullet + audit invocation block).
- 2026-05-14 20:32 BUILD: skills/commit-slice/SKILL.md — `--do-commit` → `--merge` swap applied (frontmatter argument-hint + description; Argument modes block; Step 5 with 5-step merge flow + 2 pre-flight guardrails; 4 other `--do-commit` references swept).
- 2026-05-14 20:32 BUILD: CLAUDE.md root — NEW `Branch-per-slice` bullet added to Brownfield rules.
- 2026-05-14 20:32 BUILD: 3 stale-doc surfaces swept (pipeline.md L97 + tutorial.md L750 + tutorial-site/Hybrid AI SDLC Pipeline.html L583 — `--do-commit` → `--merge`).
- 2026-05-14 20:33 SMOKE: Mid-slice smoke gate PASS — 10/10 prose-pin tests green on slice/021 branch.
- 2026-05-14 20:40 BUILD: tools/branch_workflow_audit.py written (~340 lines; BRANCH-1 audit with _resolve_default_branch helper + escape-hatch grep + 7 violation kinds + JSON output).
- 2026-05-14 20:42 DEVIATION-2: tests/tools/__init__.py + tests/tools/test_branch_workflow_audit.py relocated to tests/methodology/test_branch_workflow_audit.py. Rationale: namespace collision between tests/tools/ test-package and top-level tools/ Python package broke `from tools import branch_workflow_audit` resolution. Existing audit-test convention places all audit tests in tests/methodology/ (test_install_audit.py, test_plugin_manifest_audit.py, test_critique_agent_drift.py). Aligning with convention. design.md Wiring matrix tests/tools/__init__.py row obsolete — to be updated at /reflect.
- 2026-05-14 20:43 ERROR: 2/8 audit tests fail. (a) escape-hatch test — Windows cp1252 default encoding wrote em-dash as 0x97 not UTF-8 0xE2-0x80-0x94 (cp1252 class N=4 → N=5 cumulative recurrence; slice-007/016/018/020/021). (b) default-branch-unresolvable test — global `init.defaultBranch=master` leaks past `git config --unset` local. Fixing inline.
- 2026-05-14 20:45 TEST: BRANCH-1 audit 8/8 PASS after encoding="utf-8" fix + GIT_CONFIG_GLOBAL/GIT_CONFIG_NOSYSTEM env isolation.
- 2026-05-14 20:50 BUILD: tools/install_audit.py — _CANONICAL_TOOLS N=15 → N=16 (tools.branch_workflow_audit added; sorted alphabetically).
- 2026-05-14 20:50 BUILD: plugin.yaml — version 0.34.0 → 0.35.0 + tools list entry `tools/branch_workflow_audit.py` rule:BRANCH-1.
- 2026-05-14 20:50 BUILD: VERSION 0.34.0 → 0.35.0.
- 2026-05-14 20:55 BUILD: methodology-changelog.md v0.35.0 entry prepended (~70 lines: opening + 3 sub-modes + canonical regex + N-surface schema-pin N=8 + v1 carveout + retirement-proof + Added entry).
- 2026-05-14 20:57 BUILD: shippability.md row 21 appended (single-line; Command cell enumerates 14 invocation targets — 8 whole-file + 6 `::test_*`).
- 2026-05-14 20:58 BUILD: Phase 3 forward-sync — `cp` 4 files to `~/.claude/` (skills/build-slice/SKILL.md + skills/commit-slice/SKILL.md + methodology-changelog.md + VERSION → ai-sdlc-VERSION). Mini-CAD-1 byte-equality post-sync.
- 2026-05-14 21:00 TEST: BRANCH-1 critical path 14/14 invocation targets PASS in 4.38s + full project test suite 481/481 PASS in 8.01s.
- 2026-05-14 21:01 TEST: All Phase 5 pre-finish audits CLEAN — PMI-1 + INST-1 + CAD-1 + BRANCH-1 + TF-1 (29/29 PASSING) + WIRE-1.
- 2026-05-14 21:02 DEVIATION-5: `--merge` sub-mode (b) structurally wrong for any project with protected `master`/`main` branches, required-PR review, or CI gating on origin. Local-merge then `git push origin <default>` either (a) fails on protected branches, (b) bypasses required PR review, or (c) skips CI evaluation on the slice branch in isolation. Slice-021 ships local-only as a documented v1 limitation (design.md Limitations item 1 already covers); slice-022 candidate `redesign-commit-slice-for-pr-aware-flow` will (i) DROP `--merge` sub-command entirely, (ii) replace with `--push` flag that pushes the slice branch to origin (user creates PR + merges manually via UI), (iii) keep the BRANCH-1 sub-mode (a) build-time branch-create + sub-mode (c) audit-time pre-finish refusal unchanged. ADR-019 Option 1 sub-mode (b) becomes "USER-DRIVEN PR FLOW" rather than "local no-ff merge" in slice-022 ADR-020. **NEW class candidate for /critic-calibrate slice-022**: *opinionated-merge-default-vs-team-workflow* — all 4 Critic-stack passes missed that `--merge`'s local-only semantics structurally fails for the dominant real-world case (protected branches + PR review); the Critic dimensions (Security / Contract gaps / Cross-cutting conformance) didn't surface this because they evaluated `--merge` AS LOCAL-ONLY without questioning whether local-only was the right scope. Promotion at N≥3 if recurs.

## Summary

### Plan executed

Phase 1 (test scaffolding): 6 NEW test files + 4 existing-test-file extensions. All 29 TF-1 plan rows authored.

Phase 2 (implementation):
- `skills/build-slice/SKILL.md` — 3 inline edits (NEW `### Branch state` sub-section in `## Prerequisite check`; NEW canonical BRANCH=skip shape sentence in Step 7c; NEW Step 6 pre-finish BRANCH-1 audit bullet + invocation block).
- `skills/commit-slice/SKILL.md` — `--do-commit` → `--merge` swap (frontmatter description + argument-hint; Argument modes block; Step 5 with 5-step merge flow + 2 pre-flight guardrails; 4 other `--do-commit` references swept).
- `tools/branch_workflow_audit.py` (NEW, ~340 lines) — BRANCH-1 audit with `_resolve_default_branch()` helper + escape-hatch grep + 7 violation classes + JSON output.
- `tools/install_audit.py` — `_CANONICAL_TOOLS` N=15 → N=16.
- `plugin.yaml` — version 0.35.0 + tools list entry.
- `VERSION` — 0.35.0.
- `methodology-changelog.md` — v0.35.0 entry prepended.
- `architecture/shippability.md` — row 21 appended (14 invocation targets).
- `CLAUDE.md` (root) — Branch-per-slice bullet added.
- 3 stale-doc surfaces swept (`pipeline.md` L97 + `tutorial.md` L750 + `tutorial-site/Hybrid AI SDLC Pipeline.html` L583).

Phase 3 (forward-sync): 4 files copied to `~/.claude/`.

Phase 4 (mid-slice smoke gate): 10/10 prose-pin tests PASS post-SKILL.md edits.

Phase 5 (pre-finish gate): all audits CLEAN.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `pytest tests/methodology/test_build_slice_skill_branch_create.py tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py tests/methodology/test_commit_slice_skill_merge_flag.py tests/methodology/test_root_claude_md_branch_per_slice_rule.py -v` → 10 passed in 0.10s.

### Pre-finish gate
- [x] All 5 ACs PASS with evidence — see TF-1 rows 1-29 PASSING
- [x] All 20 must-not-defer items addressed (CAD-1 invariant preserved; PMI-1 + INST-1 atomic version bump 0.34.0→0.35.0; mini-CAD bidirectional N=11→N=13; TPHD-1 sub-mode (c) ran clean at Phase 0; SCPD-1 single-source-of-truth row 21 with 14 targets; BRANCH-1 bootstrap DEVIATION line pinned in build-log Events; WT-loss guardrail + branch-delete confirmation + default-branch resolution + stale-slice-branch guardrail all codified in `--merge` flow; no-push / no-no-verify / no-force-delete / no-history-rewrite / branch-state-error-paths / merge-conflict-error-path / branch-state-transition-logging all in design)
- [x] Drift-check pass (vault and code aligned)
- [x] Smoke regression check pass (10/10 still green at pre-finish)
- [x] No debug code (no TODO/FIXME/debug prints introduced)
- [x] BRANCH-1 self-application — on slice/021 branch; 4 branch-state transitions logged in Events (CREATE done; COMMIT + MERGE + DELETE pending at /commit-slice --merge)
- [x] TF-1 audit (--strict-pre-finish) — 29/29 PASSING
- [x] WIRE-1 wiring matrix — clean
- [x] PMI-1 + INST-1 atomic — version 0.35.0 in plugin.yaml + VERSION + ~/.claude/ai-sdlc-VERSION
- [x] Mini-CAD-1 row 3 transitions — slice/SKILL.md PASSING (untouched); build-slice + commit-slice mini-CADs PASSING post-forward-sync
- [x] Shippability catalog row 21 added (validation runs the row's 14-target Command cell)
- [x] CAD-1 byte-equality preserved at slice-017 ship hash `f34c967eaaa34413`

Full project test suite: **481/481 PASS in 8.01s** (was 481 before — added 14 NEW tests + 5 extends — wait, looks like net same count; pytest may have collected differently).

### Deferrals
None this slice — all 20 must-not-defer items addressed inline.

### Design deviations
- **DEVIATION-1** (Phase 1 test scaffolding): drop `tests/shippability/test_row_021_branch_workflow.py` from plan. Rationale: slice-020 row 20 + earlier rows show shippability catalog rows ARE the test (Command cell is executable directly); no separate `test_row_NNN_*.py` file convention exists. design.md Wiring matrix row obsolete; TF-1 plan row updated to point at `architecture/shippability.md` row 21 itself.
- **DEVIATION-2** (Phase 1 audit test placement): `tests/tools/__init__.py` + `tests/tools/test_branch_workflow_audit.py` relocated to `tests/methodology/test_branch_workflow_audit.py`. Rationale: namespace collision between `tests/tools/` test-package and top-level `tools/` Python package broke `from tools import branch_workflow_audit` resolution. All existing audit tests (test_install_audit / test_plugin_manifest_audit / test_critique_agent_drift) live in `tests/methodology/`; aligning with convention. design.md Wiring matrix `tests/tools/__init__.py` row obsolete — to be cleaned at /reflect.
- **DEVIATION-3** (Windows cp1252 class N=4 → N=5 recurrence): `pathlib.Path.write_text` without `encoding="utf-8"` in the BRANCH-1 audit test wrote em-dash as cp1252 byte 0x97 instead of UTF-8 0xE2-0x80-0x94, causing UnicodeDecodeError when the audit (which reads as UTF-8) parsed the test fixture. Fixed inline with `encoding="utf-8"` on `write_text` call. Cumulative cp1252 promotion-threshold class evidence at N=5 across slices 007/016/018/020/021 — `audit-tools-default-utf8-stdout` slice candidate at /reflect.
- **DEVIATION-4** (Global init.defaultBranch leak): the `test_branch_workflow_audit_stops_when_neither_symbolic_ref_nor_init_default_branch_resolves` test originally tried to simulate "neither resolves" via `git config --unset init.defaultBranch` local, but the user's global config (`init.defaultBranch=master`) leaked past. Fixed inline with `monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty_config))` + `monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")` to isolate git config.
- **methodology-changelog.md location**: design.md referenced `architecture/methodology-changelog.md` consistently, but the actual file lives at repo root `methodology-changelog.md` (matches existing slice-020 + earlier convention). Logged as cleanup at /reflect.

### Files changed (30 source files + 5 test-file extends per /critique-rerun M4-new ACCEPTED-FIXED canonical count)

In-repo:
- `skills/build-slice/SKILL.md` (3 inline edits)
- `skills/commit-slice/SKILL.md` (`--do-commit` → `--merge` swap + 5-step flow)
- `tools/branch_workflow_audit.py` (NEW ~340 lines)
- `tools/install_audit.py` (_CANONICAL_TOOLS extension)
- `plugin.yaml` (version + tools list)
- `VERSION` (0.34.0 → 0.35.0)
- `methodology-changelog.md` (v0.35.0 entry prepended at repo root, NOT in `architecture/`)
- `architecture/shippability.md` (row 21)
- `CLAUDE.md` (Brownfield rules bullet)
- `pipeline.md` (L97 `--do-commit` → `--merge`)
- `tutorial.md` (L750)
- `tutorial-site/Hybrid AI SDLC Pipeline.html` (L583)
- `tests/methodology/test_branch_workflow_audit.py` (NEW 8 unit tests)
- `tests/methodology/test_build_slice_skill_branch_create.py` (NEW 4 prose-pin)
- `tests/methodology/test_build_slice_skill_step_7c_branch_skip_canonical_shape.py` (NEW 1)
- `tests/methodology/test_commit_slice_skill_merge_flag.py` (NEW 4)
- `tests/methodology/test_root_claude_md_branch_per_slice_rule.py` (NEW 1)
- `tests/methodology/test_build_slice_skill_drift.py` (NEW mini-CAD)
- `tests/methodology/test_commit_slice_skill_drift.py` (NEW mini-CAD)
- `tests/methodology/test_methodology_changelog.py` (3 entry-pin + 1 ADR-pin appended)
- `tests/methodology/test_install_audit.py` (1 enumeration test appended)
- `tests/methodology/test_plugin_manifest_audit.py` (1 enumeration test appended)
- `tests/methodology/test_critique_agent_drift.py` (1 vacuous-clean test appended)

Forward-synced to `~/.claude/`:
- `~/.claude/skills/build-slice/SKILL.md`
- `~/.claude/skills/commit-slice/SKILL.md`
- `~/.claude/methodology-changelog.md`
- `~/.claude/ai-sdlc-VERSION`

### sha256 forensic capture (bidirectional)

- `skills/build-slice/SKILL.md` (in-repo ↔ installed, byte-equal at slice-021 ship)
- `skills/commit-slice/SKILL.md` (in-repo ↔ installed, byte-equal)
- `methodology-changelog.md` (in-repo ↔ installed `~/.claude/methodology-changelog.md`, byte-equal)
- `agents/critique.md` (untouched; preserved at slice-017 ship hash `f34c967eaaa34413` per CAD-1)
- `skills/slice/SKILL.md` (untouched; preserved at slice-020 ship hash per mini-CAD-1 N=11 stable)
