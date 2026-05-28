# Code Review: Slice 077 enhance-pulse-with-worktree-awareness

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths; 18 files in scope)
**Date**: 2026-05-28
**Result**: FINDINGS (0 Blockers / 2 Majors / 11 Minors) — advisory only per CRSI-1 v1

## Summary

Implementation matches design.md intent for the witnessed-gap closure (BRANCH-2 worktree-state classification + override + drift-flag suppression). The code is internally consistent, the APED-1 battery is honest (13 real synthetic-git fixtures, not mocks), the OSDG-1 / BC-PROJ-9 5-inventory fan-out is correct, and the in-band Phase C / Phase D fixes resolved real defects. **2 Majors**: M1 cross-spec parity drift on JSON `"action"` value case (PCR-1 uppercase vs new helper lowercase); M2 `pytest.skip` in CLI classify test silently swallows real-defect signal. **11 Minors**: dead imports, phantom-test-function in WIRE-1 row, under-tested edge cases (bare repo, BOM, prunable-with-reason), under-implemented design contract (UNKNOWN WARN text never generated despite design.md L181-191 enumerating 8 specific strings). No Blockers. Per CRSI-1 v1 walking-skeleton + voluntary-restraint precedent (N=16 cumulative through slice-075), findings default to next bundled-cleanup slice (slice-079+ candidate); user may opt to fix in-band per Phase H slice-076 precedent.

## Changed files (in-scope)

- `tools/pulse_worktree_resolver.py` (NEW)
- `skills/pulse/SKILL.md`
- `tools/install_audit.py`
- `plugin.yaml`
- `INSTALL.md`
- `tests/methodology/test_pulse_skill_drift.py` (NEW)
- `tests/methodology/test_pulse_skill_worktree_awareness.py` (NEW)
- `tests/methodology/test_pulse_worktree_resolver_tool_inventory.py` (NEW)
- `tests/methodology/test_parallel_conflict_resolver_tool_inventory.py`
- `tests/methodology/test_utf8_stdout_regression.py`
- `tests/skills/pulse/__init__.py` (NEW)
- `tests/skills/pulse/test_classify_worktree_state.py` (NEW)
- `tests/skills/pulse/test_cli.py` (NEW)
- `tests/skills/pulse/test_detect_active_worktrees.py` (NEW)
- `tests/skills/pulse/test_drift_flag_suppression.py` (NEW)
- `tests/skills/pulse/test_state_dict_shape.py` (NEW)
- `architecture/slices/slice-077-.../aped_1_battery.py` (NEW)
- `architecture/slices/slice-077-.../build-log.md`

## Findings

### Blockers (advisory in v1)

None.

### Majors

#### M1: Cross-spec parity drift — `"action"` value case differs from PCR-1 (lowercase vs UPPERCASE)

- **Claim under review**: docstring at `tools/pulse_worktree_resolver.py:24-25` says output is `{"action": "<detect|classify>", ...}` to match PCR-1; design.md § Cross-spec parity row 4 says JSON shape matches PCR-1's `{"action": "<diagnose|classify|resolve-soft>", ...}`.
- **Issue**: PCR-1 emits **UPPERCASE** `"action": "DIAGNOSE"` / `"CLASSIFY"` / `result.action` (`tools/parallel_conflict_resolver.py:960, 980, 990`). New helper emits **lowercase** `"action": "detect"` / `"classify"` (`tools/pulse_worktree_resolver.py:512, 541, 504`). Build-log Phase E "Evidence" line outputs lowercase. The test `test_cross_spec_parity_with_parallel_conflict_resolver` does NOT catch this — only structural conventions are asserted, never JSON output-key case. Machine consumers iterating cross-helper output (queued `parallel-slice-family-parity-audit` slice) get inconsistent action-verb casing. The "matches PCR-1" docstring claim is empirically false.
- **Evidence**: `tools/parallel_conflict_resolver.py:960, 980` (UPPERCASE); `tools/pulse_worktree_resolver.py:512, 541, 504` (lowercase).
- **Proposed fix**: Option (a) PCR-1 retroactively lowercases at slice-078 (small drift; uppercase verbs unusual in JSON); option (b) pulse_worktree_resolver uppercases to match existing convention. Option (b) is smaller surface change for slice-077; rewrite 3 emitting sites + docstring + test assertions + APED-1 (unchanged). Extend `test_cross_spec_parity_with_parallel_conflict_resolver` to grep-pin `"action": "DETECT"`/`"CLASSIFY"` literals in BOTH helpers so future drift is structurally caught — closes Dim 9 RSAD-1 axis. (Wiegers — every cross-spec parity claim should have a test that empirically verifies it; current test only verifies *structural* parity, not *contract* parity.)
- **Builder draft disposition**: **DEFERRED** to next bundled-cleanup slice (slice-079+ candidate `bundle-077-code-critic-cleanup`). Rationale: cross-spec parity audit slice (`parallel-slice-family-parity-audit`) is the natural extraction-trigger slice for this AND for m1 (INSTALLED_SURFACES module-level extraction) — both findings belong in the parity-audit slice's scope where uppercase/lowercase decision is made canonically across all parallel-family helpers in one fix. Per voluntary-restraint discipline N=16 cumulative.

#### M2: `test_cli_classify_json_returns_state_for_given_slice` swallows real-defect signal via `pytest.skip` on the most-likely failure path

- **Claim under review**: `tests/skills/pulse/test_cli.py:90-105` — when CLI emits no stdout, the test enters the `else` branch and calls `pytest.skip(f"classify returned error (likely no default branch in synthetic repo): {err_data.get('error')}")`.
- **Issue**: A synthetic `git init` repo has NO `origin/HEAD` symbolic-ref AND typically no `init.defaultBranch` set. In CI / Windows / fresh shells, `_resolve_default_branch` returns `None`, `--classify` exits with `default-branch-unresolvable`, and the test **silently skips**. Two consequences: (1) the test never actually exercises the load-bearing `--classify` happy-path on a synthetic repo — only by accident on machines where the default is configured; (2) An ACTUAL classification UNKNOWN-returning defect (the very class this test was added to catch) would also produce `no stdout` and would also be silent-skipped. Textbook test-anti-pattern: `pytest.skip` masking load-bearing assertion.
- **Evidence**: `tools/pulse_worktree_resolver.py:524-530` (default-branch-unresolvable → stderr + exit 1, no stdout); `tests/skills/pulse/test_cli.py:90-105` (`pytest.skip` unconditional on "no stdout" outcome).
- **Proposed fix**: configure synthetic repo's default branch explicitly: `_git("config", "init.defaultBranch", "master", cwd=repo_root)` + `_git("symbolic-ref", "HEAD", "refs/heads/master", cwd=repo_root)` + `_git("update-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/master", cwd=repo_root)` if needed. Drop `pytest.skip` branch; assert `proc.returncode in {0, 1}` + `json.loads(proc.stdout)` + state-value-in-set. Add separate explicit test `test_cli_classify_returns_error_on_unresolvable_default_branch` exercising the stderr/exit-1 path. Per Hendrickson: "skipped tests are not passing tests; they are absent tests."
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup. Rationale: same bundle as M1 (CLI test surface). The test currently PASSES (via skip) so doesn't block /validate-slice. Voluntary-restraint default.

### Minors

#### m1: `should_suppress_vault_forward_population_flag` `INSTALLED_SURFACES` hardcoded inline; PCR-1 precedent puts equivalent constants at module level

- **Location**: `tools/pulse_worktree_resolver.py:398-402`.
- **Issue**: Future cross-skill propagation (ADR-070 L143-148 "promote to PWA-1 if N=2") wants this file-set discoverable + test-pinnable. PCR-1's `_SOFT_FILE_SET` is module-level `frozenset[str]` with paired regression test.
- **Proposed fix**: extract `_INSTALLED_SURFACE_RELPATHS` to module scope; add paired-pin test mirroring PCR-1 pattern.
- **Builder draft disposition**: **DEFERRED** to `parallel-slice-family-parity-audit` slice (extraction-trigger slice; same N=3 trigger).

#### m2: WIRE-1 row in design.md L73 + build-log.md L64 names phantom test `test_step_1_documents_pulse_worktree_resolver_dispatch`

- **Issue**: Test doesn't exist; actual prose-pin tests are named `test_step_1_documents_git_worktree_list_pre_read` etc.
- **Proposed fix**: rename build-log L64 (and design.md L73 if follow-up touches it) to existing function names.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup. PTFFD-1 phantom-test class; identical-shape to slice-073 m-add-1 promise-not-landed lesson.

#### m3: `pytest` imported but never used in 2 test modules

- **Location**: `tests/skills/pulse/test_classify_worktree_state.py:15` + `tests/skills/pulse/test_detect_active_worktrees.py:14`.
- **Proposed fix**: drop unused imports.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup.

#### m4: `WorktreeStateClassification` imported but unused in `test_classify_worktree_state.py:17-22`

- **Proposed fix**: drop from import tuple.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup.

#### m5: UNKNOWN WARN-text design contract under-implemented (design.md L181-191 enumerates 8 strings; impl emits none)

- **Issue**: design.md + ADR-070 contractually promise WARN-emission per UNKNOWN sub-reason; `_UNKNOWN_REASONS` tuple is enumerated but has no paired template table. CLI text-mode `_run_classify` prints `f"{slice_arg}: {cls.state.value} — {cls.reason}\n"` — a one-line state + raw reason ID, NOT the canonical Drift & flags WARN strings. `augment_pulse_state_dict` adds no `drift_warns` / `warnings` key.
- **Proposed fix**: (a) Defer WARN-text generation to Haiku-side prose interpretation (add mapping table to SKILL.md); OR (b) generate canonical WARN in `pulse_worktree_resolver` via module-level `_UNKNOWN_REASON_WARN_TEMPLATES` + `format_unknown_warn(info, cls) -> str` helper.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup. This IS the most substantive minor — points to a design→code translation gap (a class of TPHD-1 sub-mode (a) / 3-Critic stack value-validation N=12+ pattern). Worth bundling with M1/M2 to keep slice-077 ships at SMALL effort.

#### m6: `_parse_worktree_porcelain` bare-repo edge case unaddressed

- **Issue**: `detect_active_worktrees` assumes `blocks[0]` is always the main worktree; bare-repo case (no `worktree <path>` first-line) unhandled. Tests do not exercise bare-repo.
- **Proposed fix**: detect bare via `"bare" in block[0]`; log WARN if first block lacks `worktree` key.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup. Low impact (this repo is non-bare; defensive only).

#### m7: APED-1 case `detect_stale_prunable` evidence misattribution (path-missing filter vs prunable-flag filter)

- **Issue**: `aped_1_battery.py::detect_stale_prunable` rmtree's the worktree dir; observed equals expected, but reason chain is "path-missing filter" not "prunable-flag filter". Per Bach: "test what you claim to test, not just what produces the same outcome."
- **Proposed fix**: split into `detect_stale_path_missing_filtered` AND `detect_stale_prunable_filtered` (latter uses `git worktree prune --verbose --expire=now` OR synthetic porcelain text injection).
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup.

#### m8: `_parse_milestone_stage` doesn't tolerate UTF-8 BOM

- **Issue**: `text.startswith("---")` fails on PowerShell-saved files with BOM; classify silently returns UNKNOWN(malformed) instead of correctly parsing.
- **Proposed fix**: `if text.startswith("﻿"): text = text[1:]` before startswith check.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup.

#### m9: `_parse_milestone_stage` prefix-match fragility on `stage:`

- **Issue**: `stripped.startswith("stage:")` would also match `stage_owner:` / `stage-history:` if introduced. Hypothetical today.
- **Proposed fix**: tighten to `stripped.split(":", 1)[0].strip() == "stage"` OR regex.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup.

#### m10: build-log.md "Result" claims WIRE-1 clean but cites phantom test name (covariant with m2)

- See m2.
- **Builder draft disposition**: **DEFERRED** to slice-079+ bundled-cleanup (resolved together with m2).

#### m11: positive observation — `_CANONICAL_TOOLS` alphabetical insertion correct

(Not a finding — verified `tools.pulse_worktree_resolver` inserted after `tools.plugin_manifest_audit` per alphabetical convention. Build-log Phase E claim confirmed.)

## Dimensions checked

- [x] **Unfounded assumptions** — m6 (bare-repo blocks[0] assumption); m8 (no-BOM assumption); m9 (prefix-match fragility).
- [x] **Missing edge cases** — m6 (bare repo); m7 (prunable-with-reason vs path-missing test conflation); m8 (BOM on Windows); m5 (UNKNOWN WARN-text never generated despite contractual promise of 8 specific strings).
- [x] **Over-engineering** — none. Helper bounded to 2 main functions + dataclasses + CLI per design.md L9 target; ~430 LOC matches.
- [x] **Under-engineering** — m5 substantial: design.md + ADR-070 promise UNKNOWN WARN-emission per sub-reason but no code generates those strings.
- [x] **Contract gaps** — M1 (cross-spec JSON action-key case); m5 (no WARN-text contract).
- [x] **Security** — no findings. No new auth/network/secrets; subprocess uses list-form; helper is read-only by design.
- [x] **Drift from vault** — m2 (build-log WIRE-1 row cites phantom test name); design.md L73 same issue but design-meta out-of-scope.
- [x] **Web-known issues** — Skipped. Helper uses stdlib + one local import; no third-party SDK / deprecated calls.
- [x] **Cross-cutting conformance** — M1 (cross-spec parity drift); m1 (RSAD-1-axis INSTALLED_SURFACES inline vs module-level + paired-pin); APED-1 battery present + executed (13 cases) but m7 reveals case whose observed-equals-expected is true for wrong filter path; EOL-DRIFT-1 inherited correctly in `_content_equal_modulo_eol`; OSDG-1 / CAD-1 byte-equality test mirrors `test_reflect_skill_drift.py` pattern correctly.

## Disposition summary (CRSI-1 v1 advisory-only)

All 13 findings (0B/2M/11m) **DEFERRED** to slice-079+ bundled-cleanup slice (working title: `bundle-077-code-critic-cleanup`). Rationale: per CRSI-1 v1 walking-skeleton + voluntary-restraint precedent N=16 cumulative through slice-075. The natural extraction-trigger slice for M1 + m1 is `parallel-slice-family-parity-audit` (queued slice-queue head); m5 is the most substantive minor and a /critic-calibrate signal candidate for design→code translation gap N=13+ cumulative. Voluntary-restraint discipline extends to N=17 cumulative (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/075/077).

Per CRSI-1 v1: findings are ADVISORY, do NOT block /validate-slice (TRI-1 + verdict-driven block deferred to slice-062).
