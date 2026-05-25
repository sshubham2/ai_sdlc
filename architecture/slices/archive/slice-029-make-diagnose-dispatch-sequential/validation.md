# Validation: Slice 029 make-diagnose-dispatch-sequential

**Date**: 2026-05-16
**Result**: PARTIAL

slice-029's own acceptance criteria all **PASS** with real-environment evidence. Aggregate is **PARTIAL** solely because the shippability catalog regression check surfaced 3 **pre-existing, non-slice-029** FAILs (#5/#8/#12) that require a user disposition (defer-with-rationale vs fix-now). Per PCA-1 this HALTs auto-advance to `/reflect` pending user decision.

## Per-criterion results

### AC1: Step 5 dispatches the 10 passes one Agent call/message, sequentially by default
- **Status**: PASS
- **Evidence**: `pytest tests/skills/diagnose/test_skill_md_pins.py` → 18/18 incl. `test_skill_md_step5_dispatch_is_sequential_by_default` (asserts the heading, the "one `Agent` call per message, one at a time" loop, the `$PARALLEL = 0` default gate, and the R-1/#57037 rationale present in real SKILL.md). Full diagnose suite 41/41.
- **Notes**: prior parallel batch is now the opt-in branch, not the default path — verified in the rewritten Step 5 prose.

### AC2: `/diagnose --parallel` restores the batch; flag in argument-hint + Step 1; unknown/garbled args fail safe (no mid-run abort)
- **Status**: PASS
- **Evidence**: **Real-shell execution of the exact slice-029 Step-1 3-arm `case` flag-strip logic under the actual runtime (Git-Bash 5.2.37 MINGW64 — the shell `/diagnose` runs on)**, 7 invocations:
  - `/diagnose` → PARALLEL=0, TARGET=cwd
  - `/diagnose --parallel` (no path) → PARALLEL=1, TARGET=cwd, **NO abort** (the exact user-reported R-1 failure case — fixed)
  - `/diagnose --paralll` (typo, no path) → `WARNING: unknown flag '--paralll' ignored`, PARALLEL=0, TARGET=cwd, **never aborts** (TRI-1 option B)
  - `/diagnose /some/repo` → TARGET=/some/repo
  - `/diagnose --parallel /some/repo` → PARALLEL=1, TARGET=/some/repo
  - `/diagnose /some/repo --parallel` (flag after path) → PARALLEL=1, TARGET=/some/repo (position-independent)
  - bash 5.2.37(1) MINGW64 → arrays + `"$@"` fully supported (**/critique-review M-add-1 portability concern empirically discharged on the real shell**)
  - Plus `test_skill_md_documents_parallel_optin` + `test_skill_md_step1_flag_strip_fail_safe` PASS.

### AC3: post-subagent invariants preserved; dispatch-coupled rewrite auditable; Step-5.5 silent-gap holds (both sub-cases)
- **Status**: PASS
- **Evidence**: All 10 enumerated dispatch-coupled edits present in real SKILL.md (heading / `$PARALLEL` split / `:170` / `:187` / Step-5.5 opening + early-exit) — verified by targeted scan. `test_skill_md_step55_dispatch_aware_with_early_exit` PASS (asserts dispatch-mode-aware opening + "Sequential early-exit" + "never silently skip to Step 6"). Full `pytest tests/skills/diagnose/` 41/41 — write_pass.py flow, 3-attempt cap, `.failed.raw`, Step 6/6.5 untouched.
- **Notes**: contract subsection `:149-162` + LAYER-EVID-1 `:164-166` left byte-verbatim.

### AC4: prose-pins added; CSP-1 + LAYER-EVID-1 N=6 + mini-CAD unchanged and passing
- **Status**: PASS
- **Evidence**: `pytest tests/skills/diagnose/` 41/41 incl. `test_pass_templates_match_skill_md_step5_contract` (CSP-1 byte-equality), `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` (LAYER-EVID-1 N=6, in-repo + installed), `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` (mini-CAD — green post forward-sync). 4 new pins green; slice-001/002/019 pins unmodified.

### AC5: R-1 → mitigating + structured Mitigation field; shippability row; changelog v0.43.0; PMI-1 lockstep
- **Status**: PASS
- **Evidence**: `risk_register_audit --json` → `R-1 status=mitigating, violations=[]`, structured `Mitigation` field present. `pytest tests/methodology/test_methodology_changelog.py` 64/64 incl. `test_v_0_43_0_diagnose_sequential_dispatch_entry_present_in_repo_and_installed` + `test_version_matches_most_recent_changelog_entry` + `test_each_changelog_entry_carries_rule_reference` (rule-ID-less `### Changed` entry citing ADR-027 accepted). `plugin_manifest_audit` → clean, version 0.43.0 (PMI-1 lockstep VERSION==plugin.yaml==0.43.0; ai-sdlc-VERSION + installed changelog forward-synced). shippability row 29 present, path-audit clean.

## VAL-1 layered safety (Step 5b)
- **Result**: PASS — `validate_slice_layers` → 0 secrets, 0 import findings, 0 suppressed. Layer A (credential scan) + Layer B (dep-hallucination, `--imports-allowlist tests`) both clean.

## WS-1 / ETC-1
- Walking-skeleton: false → WS-1 audit default-off clean (N/A).
- Exploratory-charter: false → ETC-1 audit default-off clean (N/A).

## Multi-instance validation
- **Required?**: no — slice-029 is a single-process `/diagnose` dispatch-strategy prose change; no multi-user / multi-device / sync surface.
- **Result**: not-applicable

## Shippability catalog (Step 5.5)

Pre-catalog gate (`shippability_path_audit`, PTFCD-1 sub-mode b): **CLEAN** — 27 rows, 206 test-path tokens all exist (incl. the new slice-029 row 29 path).

Catalog run: **24 commands PASS, 5 reported FAIL**. Triage:

| # | Slice | Disposition |
|---|-------|-------------|
| 28 | slice-028 | **FALSE POSITIVE** (catalog-runner artifact). The inline runner mis-grabbed the `<5s` Runtime cell as a command. Row-28's real commands re-run clean: `test_utf8_stdout_regression.py` 24 passed; `test_methodology_changelog.py -k v_0_42_0` 2 passed. NOT a regression. |
| 29 | slice-029 | **FALSE POSITIVE** (same runner artifact — `<3s` Runtime cell). Row-29's real command `pytest tests/skills/diagnose/test_skill_md_pins.py --no-header -q` → 18 passed. NOT a regression. |
| 5 | slice-005-add-bc-1-keyword-precision | **PRE-EXISTING, NOT slice-029-caused.** |
| 8 | slice-008-refine-bc-1-anchors | **PRE-EXISTING, NOT slice-029-caused.** |
| 12 | slice-012-bc-proj-2-negative-anchor-migration | **PRE-EXISTING, NOT slice-029-caused.** |

### Shippability regressions — analysis (#5/#8/#12)

- **Cause**: spec gap / environment drift in the catalog rows themselves — **NOT a slice-029 regression**.
- **Proof slice-029 did not cause it**:
  1. `git diff master --stat` and `git status --porcelain` show slice-029 modified **only 6 files**: `VERSION`, `methodology-changelog.md`, `plugin.yaml`, `skills/diagnose/SKILL.md`, `tests/methodology/test_methodology_changelog.py`, `tests/skills/diagnose/test_skill_md_pins.py`. **No BC-1 surface touched** (`tools/build_checks_audit.py`, `architecture/build-checks.md`, `tests/methodology/test_build_checks_audit.py` all clean/identical to master).
  2. The failing tests (`test_build_checks_audit.py::test_migrated_rules_have_expected_anchors`, `::test_slice_001_archive_still_fires_proj2`, `::test_bc_proj_2_*`, `::test_negative_anchors_schema_*`, etc.) read `REPO_ROOT/architecture/build-checks.md` and assert `"BC-PROJ-1" in by_id` ("BC-PROJ-1 not parsed from project file").
  3. `architecture/` is **gitignored** (`.gitignore:10-11` — "Local-only AI SDLC vault (per-project; never tracked)"). `architecture/build-checks.md` is a local-only, never-version-controlled file (2120 bytes, mtime 2026-05-16 10:40) whose local content has drifted from what `test_build_checks_audit.py` expects (it carries slice-028's BC-PROJ-3/BC-GLOBAL-2 promotions but not the BC-PROJ-1/2 migrated-rule anchors the tests assert). Because the file + the test are both branch-independent, **these tests fail identically on master** — confirmed by running them directly against the (slice-029-untouched) working copy.
- **Latent catalog-design issue surfaced (reality surprise)**: shippability rows #5/#8/#12 cite tests whose pass/fail depends on the content of a **gitignored local-only vault file** (`architecture/build-checks.md`). Such rows are not environment-robust — a fresh clone / different machine / vault-not-regenerated state makes them red regardless of code correctness. This is a catalog-robustness defect independent of slice-029.
- **Disposition**: requires user decision (defer-with-rationale vs fix-now). slice-029 cannot and should not fix unrelated pre-existing BC-1-catalog/vault-sync rot — that is out of its scope (mission-brief "Out of scope" + the brownfield "refactors need a slice" rule). Recommended: **user-approved deferral** with a follow-up slice candidate to (a) regenerate/repair the local `architecture/build-checks.md` to satisfy `test_build_checks_audit.py`, and/or (b) make catalog rows #5/#8/#12 environment-robust or move them off gitignored-vault dependence.

## Shippability regressions — disposition

**#5 / #8 / #12 — USER-APPROVED DEFERRAL (2026-05-16).**

- **Decision**: defer-with-rationale (user-ratified after full investigation at the TRI/validate gate).
- **Rationale**: These are NOT slice-029 regressions. Investigation established a pre-existing **local vault-corruption incident**: `architecture/build-checks.md` (and global `~/.claude/build-checks.md`) were truncated to only the slice-028-promoted rule (`BC-PROJ-3` / `BC-GLOBAL-2`) at mtime 2026-05-16 10:40 — *before* slice-029 began (~11:55) — losing `BC-PROJ-1`, `BC-PROJ-2`, and `BC-GLOBAL-1`. `test_build_checks_audit.py` is git-clean (identical to master) and fails identically on master; slice-029's entire diff is 6 files with zero BC-1 surfaces. Both build-checks.md files are gitignored/local-only (`.gitignore:11`) so there is no in-repo history; the canonical anchor spec lives in the tracked `test_build_checks_audit.py` + archived slice-005/008/012 reflections. Fixing this mid-slice would (a) expand slice-029 far beyond its mission ("Out of scope"), (b) violate the brownfield "refactors/repairs need a slice" rule, and (c) conflate two unrelated changes in one reflection/commit.
- **User approval**: yes (explicit — "Defer w/ rationale + flag follow-up").
- **Follow-up (for `/reflect` to formalize)**:
  1. **risk-register entry** — local AI-SDLC-vault build-checks.md truncation/corruption (BC-1 audit silently degraded: only BC-PROJ-3 active locally; BC-PROJ-1/2 + BC-GLOBAL-1 lost). Likely an append-vs-overwrite defect in an earlier `/reflect` Step 5b promotion OR a manual edit. Impact: BC-1 evergreen-rule coverage degraded until restored; reversibility cheap.
  2. **high-priority follow-up slice candidate** — restore `architecture/build-checks.md` + `~/.claude/build-checks.md` (reconstruct BC-PROJ-1/2 + BC-GLOBAL-1 from `test_build_checks_audit.py` expected anchors + archived slice-005/008/012 reflections). A **failing repro already exists** (`test_build_checks_audit.py` — the BFRD-1 prelude is pre-satisfied), so this routes straight to a fix slice. Also consider hardening shippability rows #5/#8/#12 (and the `/reflect` Step 5b promotion logic) so catalog pass/fail no longer silently depends on gitignored, never-tracked vault content.

**Net validation outcome**: slice-029 ACs 1-5 all PASS with real evidence; the only non-PASS is a pre-existing, user-deferred, non-slice-029 incident. Gate satisfied by explicit user-approved deferral → `/reflect` unblocked.

## Reality surprises
- The shippability catalog contains rows whose tests depend on **gitignored, never-tracked vault content** (`architecture/build-checks.md`). These rows produce environment-dependent FAILs unrelated to the slice under validation — a latent fragility in the regression-check design. Captured above as a follow-up; `/reflect` to formalize (risk-register + slice candidate).
- The earlier (pre-slice-029) corruption of both build-checks.md files to a single rule suggests a possible append-vs-overwrite defect in `/reflect` Step 5b rule-promotion — worth a targeted look during the follow-up slice.
