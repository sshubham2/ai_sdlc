# Build log: Slice 012 bc-proj-2-negative-anchor-migration

**Date**: 2026-05-13
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-13 12:00 BUILD: Phase 0 sha256 baseline capture
  - methodology-changelog.md (in-repo)         5C261C963A5BA2DB
  - methodology-changelog.md (installed)       5C261C963A5BA2DB  (byte-equal pre-edit per slice-005..011 N=7 stable)
  - VERSION (in-repo)                          4F3CA66D226ADD97  = "0.26.0"
  - ai-sdlc-VERSION (installed)                4F3CA66D226ADD97  = "0.26.0"  (byte-equal pre-edit)
  - plugin.yaml                                BFF71FAEB70150A2  (contains `version: 0.26.0`)
  - architecture/build-checks.md (in-repo)     B46329E445D7A58B  (no installed counterpart; BC-PROJ-2 is project-only)
- 2026-05-13 12:05 TEST: Phase 1a appended 4 audit tests to test_build_checks_audit.py
- 2026-05-13 12:06 TEST: Phase 1a WRITTEN-FAILING confirmed — test_slice_005_archive_no_longer_fires_proj2 + test_slice_011_archive_no_longer_fires_proj2 fail with `AssertionError: BC-PROJ-2 should NOT apply to ... applicable: {'BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1'}` (BC-PROJ-2 fires pre-migration); test_bc_proj_2_has_methodology_vocabulary_negative_anchors fails with EXACTLY the B1 pinned signal `BC-PROJ-2 negative_anchors mismatch: got (), expected ('defer-with-rationale', ...)`
- 2026-05-13 12:07 TEST: Phase 1a mini-CAD-1 row 3 transition for test_slice_001_archive_still_fires_proj2 — PASSING -> WRITTEN-FAILING -> PASSING transition recorded (flipped to `not in`, observed AssertionError, flipped back, observed PASS; slice-007/009/010/011 N=4 stable -> slice-012 N=5 stable)
- 2026-05-13 12:10 TEST: Phase 1b INSERT — new entry-pin function test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed inserted AFTER L297 (closing assert of v0.26.0 RSAD-1 entry-pin) under NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header containing ONLY this function (per /critique M1 ACCEPTED-FIXED + Audit 6 structural-separation verification)
- 2026-05-13 12:11 TEST: Phase 1c narrow-scope Edit — PMI-1 gate renamed `_at_0_26_0` -> `_at_0_27_0` + SECTION header renamed `v0.26.0` -> `v0.27.0`; old_string scoped to gate function body + its dedicated SECTION header only (no entry-pin function spanned) per /critique M1 ACCEPTED-FIXED
- 2026-05-13 12:12 TEST: Phase 1b/1c WRITTEN-FAILING confirmed — test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed fails on missing `## v0.27.0`; test_plugin_yaml_version_matches_version_file_at_0_27_0 fails on `VERSION file content is '0.26.0', expected '0.27.0'`; the v0.26.0 RSAD-1 entry-pin function (test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed) STILL PASSES — slice-011 NEW Dim 9 sub-class N=1 (entry-pin-vs-PMI-1-gate-conflation) N=2 promotion probe SUCCESS at design-time-discipline level
- 2026-05-13 12:15 BUILD: Phase 2 — appended `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` line to BC-PROJ-2 in `architecture/build-checks.md:35` between existing `Trigger anchors:` (L34) and existing blank line before `**Check**:` (L36)
- 2026-05-13 12:16 SMOKE: mid-slice smoke gate PASS — `tools.build_checks_audit --slice architecture/slices/archive/slice-011-... --changed-files tools/build_checks_audit.py` returns `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (BC-PROJ-2 now suppressed); slice-001 backward-compat regression check returns `applicable=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (BC-PROJ-2 still fires — backward-compat covenant preserved)
- 2026-05-13 12:17 TEST: Phase 2 verification PASS — 4 Phase 1a tests all PASS post-Phase 2 migration (`test_slice_005_archive_no_longer_fires_proj2`, `test_slice_011_archive_no_longer_fires_proj2`, `test_slice_001_archive_still_fires_proj2`, `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`)
- 2026-05-13 12:20 BUILD: Phase 3 — appended `## v0.27.0 — 2026-05-13 BC-PROJ-2 negative-anchor migration` entry to in-repo `methodology-changelog.md` between L35 horizontal rule and L37 v0.26.0 entry. 3-pin shape (`## v0.27.0` + `BC-PROJ-2` + canonical phrase `BC-PROJ-2 negative-anchor migration`). Atomic version bump VERSION 0.26.0 → 0.27.0 + plugin.yaml.version 0.26.0 → 0.27.0
- 2026-05-13 12:22 BUILD: Phase 4 — byte-equal mirror to installed `~/.claude/methodology-changelog.md` (sha256 33423327EB101F26 both sides ✓); `~/.claude/ai-sdlc-VERSION` 0.26.0 → 0.27.0
- 2026-05-13 12:22 BUILD: Phase 4 sha256 forensic capture
  - methodology-changelog.md (in-repo)         33423327EB101F26
  - methodology-changelog.md (installed)       33423327EB101F26  (byte-equal post-edit; bidirectional N=7 → N=8 stable)
  - VERSION (in-repo)                          NEW = "0.27.0"
  - ai-sdlc-VERSION (installed)                NEW = "0.27.0"  (byte-equal post-edit)
  - plugin.yaml                                contains `version: 0.27.0`
  - architecture/build-checks.md (in-repo)     post-Phase 2 (BC-PROJ-2 now has Negative anchors line)
- 2026-05-13 12:23 SMOKE: self-application audit (validate-using-your-own-ship N=9 → N=10 ratchet) — `tools.build_checks_audit --slice architecture/slices/slice-012-...` with full changed-files list returns `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']`. Slice-012's own ship validates the BC-PROJ-2 migration it ships
- 2026-05-13 12:24 BUILD: PMI-1 audit clean — `tools.plugin_manifest_audit --root .` exits 0; version 0.27.0; 24 skills, 5 agents, 15 tools
- 2026-05-13 12:25 BUILD: Phase 5 — appended shippability row 12 (slice-012 critical path: 4 audit tests + 1 entry-pin test + 1 PMI-1 gate at 0.27.0); updated row 11 (slice-011) PMI-1 supersession note to point to slice-012 row 12
- 2026-05-13 12:27 TEST: pytest tests/methodology/ — 367/367 PASS in 1.85s
- 2026-05-13 12:28 TEST: pytest full repo tests/ — 397/397 PASS in 3.43s (no regressions on any prior slice critical path)
- 2026-05-13 12:29 BUILD: TF-1 strict-pre-finish audit clean (6 rows PASSING, 0 WRITTEN-FAILING, 0 PENDING); all `| PENDING |` cells in mission-brief.md replaced with `| PASSING |`
- 2026-05-13 12:30 BUILD: WIRE-1 audit clean (zero-row matrix accepted; no new modules)
- 2026-05-13 12:30 BUILD: TRI-1 triage audit clean (final verdict CLEAN; 5 findings all ACCEPTED-FIXED at /critique round)
- 2026-05-13 12:30 BUILD: LINT-MOCK-1 clean on changed Python test files (`tests/methodology/test_build_checks_audit.py`, `tests/methodology/test_methodology_changelog.py`)
- 2026-05-13 12:30 SMOKE: regression check — slice-011 backtest still returns `applicable=[]` post-Phase 5 (no regression from mid-slice smoke); shippability critical-path 185/185 PASS in 2.98s

## Summary

### Plan executed

| Phase | Status | Notes |
|-------|--------|-------|
| 0 — sha256 baseline | DONE | All 6 file pairs captured; methodology-changelog + VERSION byte-equal in-repo↔installed at baseline (N=7 stable) |
| 1a — 4 audit tests | DONE | All 4 WRITTEN-FAILING with pinned signals; B1-compliant per-rule scoping via `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors`; mini-CAD-1 row 3 transition recorded |
| 1b — entry-pin test (3-pin shape per m1) | DONE | INSERT under NEW SECTION header; entry-pin discipline preserved (M1 verified) |
| 1c — PMI-1 gate supersession | DONE | Narrow-scope Edit (gate body + dedicated SECTION header only); v0.26.0 RSAD-1 entry-pin untouched — N=2 promotion probe SUCCESS |
| 2 — BC-PROJ-2 Negative anchors line | DONE | Single-line addition; mid-slice smoke PASS (BC-PROJ-2 suppressed on slice-011; slice-001 backward-compat preserved) |
| 3 — in-repo v0.27.0 entry + atomic version bump | DONE | 3-pin canonical phrase present; VERSION + plugin.yaml.version → 0.27.0 |
| 4 — installed mirror + Phase 4 sha256 + N=10 self-application | DONE | Byte-equal (33423327EB101F26 both); BC-PROJ-2 suppressed on slice-012's own ship |
| 5 — shippability row 12 + row 11 supersession note | DONE | Catalog grew 11 → 12 rows |

### Mid-slice smoke gate

**Result**: PASS
**Evidence**:
- slice-011 archive backtest (post-Phase 2): `applicable=[]`, `skipped=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']`
- slice-001 regression check (post-Phase 2): `applicable=['BC-PROJ-1', 'BC-PROJ-2', 'BC-GLOBAL-1']` (backward-compat preserved)

### Pre-finish gate

- [x] All 5 ACs PASS with evidence — verified at Phase 2 + Phase 4 (validation.md to record formally at /validate-slice)
- [x] Must-not-defer (11 items) addressed
  - [x] Input validation (token-disjointness Ø verified Audit 1; no parse violations)
  - [x] TF-1 PENDING → WRITTEN-FAILING genuineness (all 6 rows pinned signals; B1-compliant per-rule scoping)
  - [x] Backward-compat slice-001 (Audit 2 + Phase 2 smoke + Phase 4 N=10 ratchet)
  - [x] BC-1 v0.27.0 bidirectional entry pinned (3-pin shape per m1)
  - [x] PMI-1 atomic 0.26.0 → 0.27.0 + audit clean
  - [x] PMI-1 versioned-gate supersession narrow-scoped (entry-pin discipline preserved; N=2 promotion probe SUCCESS)
  - [x] Bidirectional sha256 forensic (Phase 0 + Phase 4 captured; N=7 → N=8 ratchet)
  - [x] Backward-compat un-migrated rules (slice-008's BC-1 v1.2 schema unchanged; behavior identical)
  - [x] No regression on existing 29+ BC-1 test suite (367/367 methodology PASS; 397/397 full suite PASS)
  - [x] Self-application validate-using-your-own-ship N=9 → N=10 (slice-012's own ship: BC-PROJ-2 in skipped)
- [x] /drift-check semantically satisfied: bidirectional sha256 + entry-pin tests + PMI-1 audit clean; no separate `tools/drift_check_audit.py` exists (drift-check is a read-only methodology skill at `~/.claude/skills/drift-check/SKILL.md`)
- [x] Mid-slice smoke still passes (no regression post-Phase 5)
- [x] No new TODOs / FIXMEs / debug prints
- [x] LINT-MOCK-1 clean on changed Python test files
- [x] WIRE-1 clean (zero-row matrix; no new modules)
- [x] BC-1 self-application clean (no rules apply to slice-012 — BC-PROJ-2 suppressed by own ship's negative anchors)
- [x] TF-1 strict-pre-finish clean (6 rows PASSING)
- [x] TRI-1 triage audit clean (final verdict CLEAN)

### Deferrals (if any)

None. All 5 /critique findings ACCEPTED-FIXED in-round; all 11 must-not-defer items addressed; all gates pass.

### Design deviations (if any)

None. The 9-phase implementation order from design.md executed exactly as planned. Five design-time audits (disjointness, slice-001 backward-compat, slice-005/011 suppression, algorithm-path-conformance, RSAD-1 build-time recursive-self-application + Audit 6 structural-separation) all VALIDATED at build time. Zero build-time DEVIATIONs at slice-012 — second N-count in slice-005..012 series with this property (slice-008 was N=1; slice-012 ratchets to N=2 → promote "ZERO-build-deviation slice via strong /critique" to a tracked methodology metric per slice-008 reflection's recurrence-watch language).

### Files changed

**In-repo**:
- `architecture/build-checks.md` — BC-PROJ-2 rule body: 1 new line (`Negative anchors:`)
- `methodology-changelog.md` — 1 new H2 entry (`## v0.27.0`)
- `VERSION` — `0.26.0` → `0.27.0`
- `plugin.yaml` — `version: 0.26.0` → `0.27.0`
- `tests/methodology/test_build_checks_audit.py` — 4 new test functions + 1 new `_SLICE_011_CHANGED_FILES` constant + SECTION header
- `tests/methodology/test_methodology_changelog.py` — 1 new entry-pin function + 1 new SECTION header + PMI-1 gate renamed `_at_0_26_0` → `_at_0_27_0` with body updated
- `architecture/shippability.md` — row 12 appended; row 11 PMI-1 supersession note updated

**Installed (`~/.claude/`)**:
- `methodology-changelog.md` — byte-equal mirror of in-repo (sha256 33423327EB101F26)
- `ai-sdlc-VERSION` — `0.26.0` → `0.27.0`

**Vault (created at /design-slice + /critique earlier)**:
- `architecture/decisions/ADR-011-bc-proj-2-negative-anchor-migration.md` — renamed at /critique M3 ACCEPTED-FIXED
- `architecture/slices/slice-012-bc-proj-2-negative-anchor-migration/{mission-brief,design,critique,milestone,build-log}.md`

### Recursive-self-application observation at slice-012 (per RSAD-1 codification at slice-011)

Slice-012 — the slice authoring BC-PROJ-2 negative-anchor migration — had its own /critique draft committed an instance of the recursive-self-application defect class:

- **B1** caught at /critique: AC #4's naive substring verification approach was structurally unable to enforce that BC-PROJ-2 specifically receives the data, because slice-008 had already written all 9 methodology-vocabulary tokens on BC-PROJ-1's `architecture/build-checks.md:20` Negative-anchors line. The slice's verification design didn't account for the pre-existing slice-008 data in the same file.
- ACCEPTED-FIXED at /critique round; design.md + mission-brief.md updated to require `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_tuple` per-rule scoping mirroring slice-008's template at L1054.
- Empirically VALIDATED at /build-slice Phase 1a: pre-fix the test fails with EXACTLY the pinned signal `BC-PROJ-2 negative_anchors mismatch: got (), expected (...)`; post-fix the test passes.

**N=4 cumulative recursive-self-application events** across slices 9-12:
- slice-009 M2 (design-time): slice's own design.md committed design-doc-vs-canonical-inventory drift
- slice-010 (design-time stress-test + build-time DEVIATION-3): 3 design-time + 1 build-time recursive instance
- slice-011 (4 of 7 findings on own draft): B1+M1+M2+M3 all rule-class violations on slice-011's own draft
- **slice-012 (B1 on own draft)**: AC #4 verification approach under-scoped against slice-008's pre-existing data

RSAD-1 codification at slice-011 empirically load-bearing — without it, slice-012's B1 might have been Critic-MISSED. The Critic's adversarial prompt at `agents/critique.md` Dim 9 6th sub-clause explicitly stress-tests cross-cutting tooling slices' draft prose against the very discipline being encoded.

### Slice-011 NEW Dim 9 sub-class candidate N=2 promotion ratchet at slice-012

Slice-011 surfaced a NEW Dim 9 sub-class candidate at N=1: **entry-pin-vs-PMI-1-gate-semantics-conflation** (caught at /validate-slice Step 5.5 when shippability catalog row 10 failed because a section-spanning Edit accidentally deleted the v0.25.0 MCT-1 entry-pin function during a PMI-1 gate supersession).

Slice-012 deliberately encoded the discipline at design time via:
- /critique M1 ACCEPTED-FIXED (Phase 1b INSERT under NEW SECTION header + Phase 1c narrow-scope Edit discipline)
- design.md Audit 6 (empirical structural-separation verification pre-Edit)

Empirical validation at /build-slice Phase 1b/1c:
- Phase 1b inserted the v0.27.0 entry-pin function under its own NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header (not co-located with any PMI-1 gate function)
- Phase 1c renamed the PMI-1 gate body + its dedicated SECTION header `v0.26.0` → `v0.27.0` (no span to entry-pin function)
- Post-Phase 1b/1c: `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` (the slice-011 entry-pin function) STILL PASSES — empirically validated entry-pin discipline preserved across slice-012's PMI-1 gate supersession

**N=2 promotion threshold MET** — promote `entry-pin-vs-PMI-1-gate-semantics-conflation` to Dim 9 sub-class refinement at slice-013+ via /critic-calibrate or a dedicated Dim 9 sub-class refinement slice. The discipline is now empirically load-bearing across 2 slices (slice-011 caught at /validate-slice; slice-012 caught at /critique with design-time codification + build-time validation).

