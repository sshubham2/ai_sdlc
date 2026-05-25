# Build log: Slice 031 complete-shippability-decoupling (split-label 030B)

**Date**: 2026-05-17
**Result**: SHIPPED-WITH-DEFERRALS (slice scope 100% delivered; one pre-existing out-of-scope R-5 CRLF artifact, user-pre-approved via mission-brief out-of-scope + slice-030A precedent)

## Events (append-only — written DURING build per Step 7c)

- 2026-05-17 00:00 BUILD: branch slice/031-complete-shippability-decoupling created from master (default resolved via init.defaultBranch=master)
- 2026-05-17 00:01 DEVIATION: slice folder renamed slice-030B→slice-031 — rationale: branch_workflow_audit BRANCH-1 `slice-NNN-` regex requires numeric NNN; "030B" retained as documented split-lineage prose label (mirrors slice-030A: folder slice-030, label "030A"). Canonical id slice-031; all prereq audits re-run clean on new path.
- 2026-05-17 00:02 BUILD: plan approved (8 tasks, incidental-only scope, smoke gate at T3); prereq audits clean (BRANCH-1/CRP-1/triage/critique-review)
- 2026-05-17 00:15 BUILD: T1 tools/shippability_decoupling_audit.py created (SCMD-1: shared token predicate import + net-new segment validator + AST closed-world classifier)
- 2026-05-17 00:16 TEST: T1 SCMD-1 self-run exit 1, 30 rows missing-machine-cmd (correct pre-column WRITTEN-FAILING state); --json valid
- 2026-05-17 00:35 BUILD: T2 test_shippability_command_column.py + test_shippability_decoupling_audit.py written (TF-1 failing-first)
- 2026-05-17 00:36 BUILD: T1 tool bugs fixed during T2 — per-segment backtick strip in _segments; audit() repo_root override; path-expression-scoped set-subset classifier (ast.walk is BFS not source-order; docstring/assert prose was polluting); docstring \` SyntaxWarning removed
- 2026-05-17 00:37 TEST: T2 6 failed / 9 passed — all 6 failures are genuine WRITTEN-FAILING (column/decouple/corpus pending T3/T5/T7); 9 behavior pins (M-add-A prose-discriminator, M1 indirection-catch, M2 allowlist, essential-recognition) PASS
- 2026-05-17 00:55 BUILD: T3 shippability.md → 6 cols (30 rows, /tmp/add_machine_cmd.py); #28 two ;-clean, #29 single, <interp> canonical; 0 grammar failures
- 2026-05-17 00:58 SMOKE: T3 mid-slice gate — check(a) CLEAN (0 missing/prose); derivation spans all 30 rows (325 fns); slice-001 IN derived corpus set ✓; 31 essential entry-pins recognized-not-flagged ✓; 11 incidental (expected pre-T5) ✓
- 2026-05-17 00:59 FINDING: smoke gate caught classifier over-reach — 39 false `unresolved-path` on skill-drift/diagnose/utf8 fns that read ~/.claude/<skill>.md (NOT 030B's incidental archive/build-checks class). Blanket Path.home→unresolved violates the design's principled scope boundary; would make SCMD-1 un-clean-able (breaks AC1). Fix: drop unresolved class + add same-module helper-call resolution (closed-world completeness for real indirection vector). Aligns code to ratified design; no design/plan change.
- 2026-05-17 01:10 FINDING: smoke gate caught 2nd classifier bug — 7 test_bci1_* false-incidental: they build SYNTHETIC tmp_path/architecture/build-checks.md + monkeypatch Path.home (env-independent already), not real-vault reads. Fix: root-anchor incidental detection to REPO_ROOT/Path.home() chain roots (synthetic test-local roots contribute nothing). _attr_paths_in + _PATH_READ_FUNCS removed (dead). No design change.
- 2026-05-17 01:12 SMOKE: T3 mid-slice gate PASS — check(a) clean; 325 fns/30 rows; 11 GENUINE incidental (10 test_build_checks_audit.py + 1 test_validate_slice_layers.py::test_slice_002_archive_replay); 31 essential recognized-not-flagged; 283 clean; corpus folders=8 incl slice-001 & slice-002. Scope clarification: T5 decouples ALL 11 (B1 mechanical-complete-set, not just test_build_checks_audit.py) + corpus covers all 8 folders.
- 2026-05-17 01:25 BUILD: T4 shippability_path_audit repointed cells[3]→cells[5] (Machine-cmd); len<5→len<4 + fallback to cells[3] (never silent-skip; B3). PTFCD-1 clean 30 rows/214 tokens; its 3 tests + missing-col test pass.
- 2026-05-17 01:45 BUILD: T5 corpus built (8 folders verbatim mission-brief+design); _ARCHIVE_BACKTEST_CORPUS const added; 11 incidental fns repointed (project_checks→_CANONICAL_PROJECT_FIXTURE, global_checks→_CANONICAL_GLOBAL_FIXTURE, slice_folder→corpus); 7 _GLOBAL_BUILD_CHECKS.exists() guards collapsed to hard-asserts (M4); dead _GLOBAL_BUILD_CHECKS const removed; test_slice_002_archive_replay vacuous skip→hard assert.
- 2026-05-17 01:46 BUILD: classifier hardened (transitive real-vault-root via module consts: _ARCHIVE_BACKTEST_CORPUS/_CANONICAL_*→REPO_ROOT) — preserves BCI-1 synthetic-tree false-positive fix (test-locals are not module consts).
- 2026-05-17 01:48 TEST: SCMD-1 CLEAN (incidental=0, essential=31, clean=294); 93 tests pass (TF-1 WRITTEN-FAILING→PASSING; decoupled backtests functionally green; BCI-1 no-regression; bidirectional corpus-completeness green)
- 2026-05-17 02:05 BUILD: T6 validate-slice SKILL.md Step5.5 repointed→Machine-cmd + SCMD-1 non-opt-out pre-catalog gate + PTFCD-1 reads Machine-cmd; prose-pin test added (test_validate_slice_skill.py 4 pass)
- 2026-05-17 02:20 BUILD: T7 propagation — methodology-changelog v0.45.0 SCMD-1 entry (in-repo+installed); VERSION/ai-sdlc-VERSION/plugin.yaml 0.44→0.45; plugin.yaml+install_audit SCMD-1 tool entry; v0_45_0 entry-pin + R-4-subentry tests added (pass); slice-031 catalog row appended (SCMD-1 still clean 31 rows); installed SKILL.md forward-synced
- 2026-05-17 02:22 FINDING+FIX: TF-1 audit reported "not enabled" — trailing parenthetical on `**Test-first**: true` broke the field regex (would silently bypass the TF-1 gate). Fixed to bare field-line + HTML-comment annotation. TF-1 audit now clean: 18 rows all PASSING.

## Summary

### Plan executed (8 tasks, all complete)
- **T1** `tools/shippability_decoupling_audit.py` (SCMD-1) — shared token predicate + net-new interpreter-anchored segment validator + closed-world AST classifier (transitive real-vault-root via module consts; module-const + same-module-helper indirection following).
- **T2** TF-1 tests written failing-first — `test_shippability_decoupling_audit.py` + `test_shippability_command_column.py`.
- **T3** shippability.md → 6-column (Machine-cmd); #28 two `;`-clean, #29 single, `<interp>` canonical. **Mid-slice smoke gate PASS** (after diagnosing+fixing 2 classifier bugs — see Deviations).
- **T4** `shippability_path_audit` repointed `cells[3]`→`cells[5]` with non-silent fallback (B3).
- **T5** 11 incidental fns decoupled (10 `test_build_checks_audit.py` + `test_validate_slice_layers.py::test_slice_002_archive_replay`) → slice-030A canonical fixtures + git-tracked verbatim 8-folder corpus; 7 `.exists()` guards collapsed to hard-asserts (M4); dead `_GLOBAL_BUILD_CHECKS` removed.
- **T6** `validate-slice/SKILL.md` Step 5.5 → Machine-cmd runner + SCMD-1 non-opt-out pre-catalog gate + PTFCD-1-reads-Machine-cmd; prose-pin test (B2).
- **T7** methodology-changelog v0.45.0 SCMD-1 (in-repo+installed); VERSION/ai-sdlc-VERSION/plugin.yaml 0.44→0.45; plugin.yaml+install_audit tool entry; v0_45_0 entry-pin + R-4-subentry tests; slice-031 catalog row (RPCD-1/SCPD-1); installed SKILL.md forward-synced; TF-1 plan harmonized to as-built fns + all PASSING.
- **T8** pre-finish gate (below).

### Mid-slice smoke gate
**Result**: PASS — check(a) clean; 325 fns derived from all 30 rows; 11 genuine incidental; 31 essential entry-pins recognized-not-flagged; slice-001+002 in 8-folder corpus set. Two classifier bugs diagnosed + fixed before continuing (smoke-gate discipline; see Deviations).

### Pre-finish gate
- [x] All ACs PASS — TF-1 18/18 PASSING; SCMD-1 self-run clean (incidental=0, essential=31)
- [x] Must-not-defer addressed — all-rows mechanical derivation; principled incidental/essential read-shape boundary; closed-world allowlist; non-vacuous AC2 (`.exists()` guards removed); R-4 stays `mitigating`; methodology propagation; drift-check clean
- [x] /drift-check passes — 0 blockers / 0 majors (drift-log 2026-05-17 02:40)
- [x] Mid-slice smoke still passes — SCMD-1 clean at 31 rows post-propagation
- [x] No new TODOs / FIXMEs / debug prints
- [x] LINT-MOCK ✓ · WIRE-1 ✓ · TF-1 ✓ · BRANCH-1 ✓ · UTF8-STDOUT-1 ✓ · CRP-1 ✓ · PCA-1 ✓ · BCI-1 ✓ · PMI-1 ✓ · INST-1 ✓ · CAD-1 ✓ · DR-1 ✓ · triage_audit ✓ · PTFCD-1 ✓ · slice-skill mini-CAD ✓
- [x] BC-1 — exit 0; BC-PROJ-3 + BC-GLOBAL-2 (Critical) APPLY: slice complies **by construction** — its build used only `git checkout -b` / `git branch -m` / `mv` / file-edits / `cp`; ZERO `git checkout -- <path>` / `git restore` / `git stash` reverts; the decoupled tests + SCMD-1 tool perform no git-path-reverts.
- [x] Full suite: **632 passed**, 1 failed (the pre-existing R-5 diagnose-drift only)

### Deferrals
- **R-5 / D-1 diagnose-skill-drift CRLF-LF fragility** — `tests/skills/diagnose/test_diagnose_skill_drift.py` FAILs (in-repo CRLF vs installed LF; content **byte-identical CRLF-normalized**; `skills/diagnose/SKILL.md` git-untouched this slice). NOT a slice-031 regression — pre-existing environment artifact. **User-pre-approved**: slice-031 mission-brief "Out of scope" explicitly excludes R-5/D-1 ("030B MUST NOT absorb it"); slice-030A established the precedent (user-approved-deferral against R-5 on shippability #1/#19). Tracked by risk-register R-5. Followup: standalone backlog slice `fix-skill-drift-test-crlf-normalization`.

### Design deviations (smoke-gate-driven classifier corrections — code aligned to ratified design, NO design/scope change)
1. **Dropped the `unresolved` classification** — initial blanket "`Path.home()` + no shape ⇒ unresolved" false-flagged 39 unrelated skill-drift/diagnose/utf8 fns (other slices' rows), violating the design's principled scope boundary + making SCMD-1 un-clean-able. Replaced with: incidental/essential/clean only + same-module helper-call resolution for genuine closed-world indirection completeness.
2. **Root-anchored incidental detection** — 7 `test_bci1_*` false-flagged because they build SYNTHETIC `tmp_path/architecture/build-checks.md` trees + monkeypatch `Path.home()`. Fixed: incidental shapes only counted when the `/`-chain roots at the REAL vault (`REPO_ROOT`/`Path.home()`), resolved transitively through module consts (so `_ARCHIVE_BACKTEST_CORPUS`/`_CANONICAL_*` qualify; test-locals don't).
3. **TF-1 field-line** — trailing parenthetical on `**Test-first**: true` broke the audit regex (silent gate bypass); fixed to bare field-line + HTML-comment annotation. TF-1 now engaged: 18/18 PASSING.
- All three are implementation corrections surfaced by the mid-slice smoke gate / pre-finish audits; design.md + ADR-031 already specified the *intended* semantics (principled scope boundary, closed-world) — the code now matches. No vault update needed (design was correct; code caught up).

### Files changed
- New: `tools/shippability_decoupling_audit.py`, `tests/methodology/test_shippability_decoupling_audit.py`, `tests/methodology/test_shippability_command_column.py`, `tests/methodology/fixtures/archive_backtest_corpus/{8 slice folders × mission-brief.md+design.md}`
- Modified: `architecture/shippability.md` (6th col + slice-031 row), `tools/shippability_path_audit.py`, `tests/methodology/test_build_checks_audit.py`, `tests/methodology/test_validate_slice_layers.py`, `tests/methodology/test_validate_slice_skill.py`, `tests/methodology/test_methodology_changelog.py`, `tests/methodology/test_risk_register_audit_real_file.py`, `tests/methodology/test_utf8_stdout_regression.py`, `skills/validate-slice/SKILL.md`, `methodology-changelog.md`, `VERSION`, `plugin.yaml`, `tools/install_audit.py`, `architecture/risk-register.md` (R-4 sub-entry), `architecture/decisions/ADR-030*.md`, `architecture/decisions/ADR-031*.md`, slice-031 vault (mission-brief/design/critique/critique-review/milestone)
- Installed forward-sync: `~/.claude/{ai-sdlc-VERSION, methodology-changelog.md, skills/validate-slice/SKILL.md}`
