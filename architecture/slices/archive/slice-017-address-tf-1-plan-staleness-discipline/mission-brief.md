# Slice 017: address-tf-1-plan-staleness-discipline

**Mode**: Standard
**Estimated work**: 0.5 day (~60-90 min; SMALL-to-MEDIUM mirroring slice-010 MCT-1 prose-codification scope at 3 surfaces instead of 1)
**Risk retired**: NEW first-Critic-MISS class at N=1 from slice-016 reflection — "TF-1-plan-comprehensive-harmonization-vs-actually-built" — preempts `/build-slice` Phase 6 strict-pre-finish TF-1 audit DEVIATIONs of the slice-016 class (3 stale function names + all-rows-PENDING-status surfacing at audit time because /critique + /critique-review fix-prose changed function names without harmonizing the mission-brief TF-1 plan in the same fix block)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Codify TPHD-1 (TF-Plan-Harmonization-Discipline-1, -D suffix per slice-011 RSAD-1 / slice-013 EPGD-1 / slice-015 SCPD-1 / slice-016 RPCD-1 convention N=4 stable) into `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` + `skills/build-slice/SKILL.md` as a 3-surface prose-heuristic methodology entry. Names all three sub-modes (a) `/critique` post-fix-prose harmonization + (b) `/critique-review` post-fix-prose harmonization + (c) `/build-slice` Prerequisite-check pre-flight harmonization at N=1 cumulative cross-slice evidence (slice-016 only; user-invoked proactive ratchet ahead of typical N=2 promotion threshold per slice-016 reflection language). Mirrors slice-010 MCT-1 scope (skill-prose discipline, not adversarial-prompt content) but spans 3 skill files instead of 1.

The lesson from slice-016: when `/critique` fix-prose OR `/critique-review` fix-prose changes test function names or AC #N row references, the mission-brief TF-1 plan needs synchronization in the same fix block. Otherwise the plan ships stale to `/build-slice` and surfaces at Phase 6 TF-1 strict-pre-finish audit as DEVIATION (exit 1). At slice-016, 3 stale function names + all-rows-PENDING-status persisted — caught by /build-slice Phase 6 audit as Critic-stack layer 3 (after first Critic + meta-Critic both missed).

## Acceptance criteria

1. `methodology-changelog.md` v0.32.0 entry exists in-repo AND in installed copy (`~/.claude/plugins/ai-sdlc/methodology-changelog.md`) with sha256 byte-equality; entry names TPHD-1 canonical phrase `TF-1 plan harmonization discipline` + all three sub-modes (a) `/critique post-fix-prose harmonization` + (b) `/critique-review post-fix-prose harmonization` + (c) `/build-slice Prerequisite-check pre-flight harmonization` + cross-slice anchor `slice-016` (N=1) + Limitations note acknowledging prose-heuristic semantics (no audit-enforced gate; v2 `tools/tphd_1_audit.py` candidate deferred until N≥3 recurrence post-codification).

2. `skills/critique/SKILL.md` carries TPHD-1 prose at the end-of-fix-prose phase naming the harmonization step explicitly (test function names + AC row references in mission-brief TF-1 plan must sync in same fix block); `skills/critique-review/SKILL.md` carries equivalent prose at its end-of-fix-prose phase; `skills/build-slice/SKILL.md` carries TPHD-1 pre-flight harmonization as a NEW bullet in the existing `## Prerequisite check` section (NOT as a NEW `### Step 0` — placement per /critique M2 ACCEPTED-FIXED: the discipline IS structurally a prerequisite verification, and the existing build-slice step numbering is 1,2,3,4,5,6,7,7b,7c,8 with no Step 0). Each prose insertion is location-pinned within its skill file's existing phase structure.

3. `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md` exists; reversibility=cheap with magnitude justification ~13-16 sites (3 skill files + methodology-changelog entry + 4 test files + shippability row + 3 version files + ADR file itself per ADR-016 Reversibility enumeration L141-L154); supersedes=null; extends ADR-009 (MCT-1) at the cross-cutting-tooling skill-prose-discipline layer per slice-010 calibration-trail convention; canonical phrase `TF-1 plan harmonization discipline` pinned in title or body.

4. Prose-pin tests written test-first per TF-1 plan covering: methodology-changelog v0.32.0 entry-pin (entry present + three-sub-modes named + ADR-016 pin) AND each skill file's TPHD-1 prose (substring-pin `_present` + scoped-find `_location_pinned` per slice-009 M1 + slice-016 N=4 stable `_sub_clause_present` + `_location_pinned` duality precedent adapted to skill-prose surface). PMI-1 v1.1 version-agnostic gate passes unchanged through atomic version bump 0.31.0 → 0.32.0 (retirement-proof N=3 → N=4 stable).

5. `architecture/shippability.md` row 17 added enumerating TPHD-1 critical-path tests (~9 pytest commands across `test_methodology_changelog.py` + 3 skill-prose test files); full shippability catalog (17/17 rows) PASSES at `/validate-slice` Step 5.5 in <2 min aggregate; no rows 1-16 regressed by slice-017 changes. SCPD-1 stays at N=2 stable (per /critique m3 ACCEPTED-FIXED: slice-017 has NO Dim 9 sub-clause supersession event, so SCPD-1 proactive-application is vacuously satisfied — no active propagation event occurs; row 17 is added as a NEW row with no prior-row touch needed; `_lists_nine_sub_clauses` stays valid; slice-016's RPCD-1 body-bound test end_anchors at `### Bonus: weak graph edges` remain structurally load-bearing).

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_32_0_tphd_1_entry_present_in_repo_and_installed | PASSING |
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed | PASSING |
| 1 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_32_0_tphd_1_entry_names_slice_016_cross_slice_anchor | PASSING |
| 2 | methodology | tests/methodology/test_critique_skill.py | test_critique_skill_md_tphd_1_post_fix_prose_step_present | PASSING |
| 2 | methodology | tests/methodology/test_critique_skill.py | test_critique_skill_md_tphd_1_post_fix_prose_step_location_pinned | PASSING |
| 2 | methodology | tests/methodology/test_critique_review_skill.py | test_critique_review_skill_md_tphd_1_post_fix_prose_step_present | PASSING |
| 2 | methodology | tests/methodology/test_critique_review_skill.py | test_critique_review_skill_md_tphd_1_post_fix_prose_step_location_pinned | PASSING |
| 2 | methodology | tests/methodology/test_build_slice_skill.py | test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_present | PASSING |
| 2 | methodology | tests/methodology/test_build_slice_skill.py | test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_location_pinned | PASSING |
| 3 | methodology | tests/methodology/test_methodology_changelog.py | test_adr_016_exists_and_names_tphd_1_canonical_phrase | PASSING |
| 4 | methodology | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |
| 5 | (verified at /validate-slice) | architecture/shippability.md | row 17 added; 17/17 catalog rows PASS | PASSING |

Total: 12 TF-1 rows (10 PENDING → WRITTEN-FAILING → PASSING + 1 mini-CAD-1 PASSING → WRITTEN-FAILING → PASSING transition per slice-007/009/010/011/012/013/015/016 row precedent N=8 stable + 1 catalog-level verification handled at /validate-slice not /build-slice Phase 6). Comparable density to slice-014 (8 rows) / slice-015 (13 rows) / slice-016 (15 rows).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | methodology-changelog v0.32.0 entry | `pytest tests/methodology/test_methodology_changelog.py::test_v_0_32_0_tphd_1_entry_present_in_repo_and_installed -q` returns 0; bidirectional sha256 forensic capture in /build-slice Phase 2 confirms byte-equality at single hash value (N=12 → N=13 stable) |
| 2 | 3 skill files carry TPHD-1 prose | `pytest tests/methodology/test_critique_skill.py tests/methodology/test_critique_review_skill.py tests/methodology/test_build_slice_skill.py -k tphd_1 -q` returns 0 (6 tests PASS) |
| 3 | ADR-016 exists | `pytest tests/methodology/test_methodology_changelog.py::test_adr_016_exists_and_names_tphd_1_canonical_phrase -q` returns 0; manual file existence check |
| 4 | Test-first audit clean | `python -m tools.test_first_audit architecture/slices/slice-017-address-tf-1-plan-staleness-discipline/mission-brief.md --strict-pre-finish` returns 0 (all rows PASSING/WRITTEN-FAILING per TF-1 strict-pre-finish semantics); PMI-1 v1.1 atomic version bump 0.31.0 → 0.32.0 with zero gate-body modification |
| 5 | Shippability row 17 + full catalog | `architecture/shippability.md` has row 17 with TPHD-1 critical-path tests; manual run `bash architecture/shippability.md` extraction at /validate-slice Step 5.5 → 17/17 PASS in <2 min |

## Must-not-defer

- [ ] Input validation: rule-ID format consistency — TPHD-1 canonical-form used uniformly across mission-brief + design.md + ADR-016 + methodology-changelog + 3 skill files + 3 test files. Verification: positive-form assertion `grep -c "TPHD-1" <file>` returns ≥1 hit per surface, NOT negative-form absence-check on anti-form strings (per /critique m1 ACCEPTED-FIXED RSAD-1 sub-mode (b) re-introduction class: enumerating anti-form strings would itself re-introduce them).
- [ ] Authorization check: N/A (no auth surface touched)
- [ ] Logging: N/A (no runtime code touched; pure prose codification)
- [ ] PMI-1 v1.1 atomicity: `plugin.yaml.version` 0.31.0 → 0.32.0 + `VERSION` 0.31.0 → 0.32.0 + `~/.claude/ai-sdlc-VERSION` 0.31.0 → 0.32.0 in single atomic commit per META-1 atomicity (slice-014 M1 ACCEPTED-FIXED precedent)
- [ ] CAD-1 byte-equality on `agents/critique.md` preserved through slice (slice does NOT touch agents/critique.md; bidirectional sha256 forensic capture confirms byte-equal in-repo↔installed at slice end at same hash as slice-016 ship `f34c967eaaa34413...`)
- [ ] EPGD-1 self-application: 0 of 12 prior entry-pin functions (v0.22.0..v0.31.0 spans 10 minor versions; v0.29.0 doubled per slice-014 (a)↔(b) duality; v0.31.0 doubled per slice-016 RPCD-1 (a)↔(b) duality = 8 singles + 2 doublets = 12 functions per /critique-review M-add-1 ACCEPTED-FIXED empirical count) touched through slice-017's Phase 1b NEW SECTION header insertion + Phase 1c narrow-scope Edit (per slice-013 + slice-014 + slice-015 + slice-016 EPGD-1 self-application N=4 stable). Post-slice-017: 12 + 3 NEW v0.32.0 functions = 15 entry-pin functions total.
- [ ] RPCD-1 self-application probe at /design-slice (3 sub-modes (a) NEW-symbol import-audit + (b) NEW-status/token allowlist-audit + (c) NEW-anchor sibling-grep audit per slice-016 lesson — recursive-self-application density at codification slices empirically high N=8 cumulative)
- [ ] SCPD-1 proactive-application: rows 6 + 11 + 13 + 15 + 16 of shippability.md NOT touched (no Dim 9 sub-clause supersession; `_lists_nine_sub_clauses` stays valid); row 17 added at /build-slice Phase 5 BEFORE /validate-slice catalog run (N=2 → N=3 stable post-codification at slice-016)
- [ ] BC-1 self-application: methodology-vocabulary slices recur with negative-anchor false-positive class (slice-005/006/007/010/011 N=5 cumulative); slice-017 should be silenced by BC-PROJ-2 negative-anchor migration from slice-012 (verify by running `python -m tools.build_checks_audit --changed-files <slice-017-files>` returns 0 BC-PROJ-2 + 0 BC-GLOBAL-1 fires)
- [ ] -D suffix convention: TPHD-1 ends in -1 with -D positioned before final integer per slice-011/013/015/016 RSAD-1/EPGD-1/SCPD-1/RPCD-1 N=4 stable convention; rule ID stored as `TPHD-1` (capitalized) throughout
- [ ] No new TODOs / FIXMEs / debug prints in any of the 3 skill files or 4 test files
- [ ] TPHD-1 prose at each skill file is location-pinned to a specific phase (not free-floating) per slice-009 M1 + slice-016 N=4 stable scoped-find precedent
- [ ] Test-first audit `--strict-pre-finish` passes at /build-slice Phase 6 with TPHD-1 self-application probe (the slice CODIFYING TPHD-1 must demonstrate TPHD-1 sub-mode (a) /critique + sub-mode (b) /critique-review + sub-mode (c) /build-slice Prerequisite-check pre-flight harmonization on its OWN TF-1 plan — recursive-self-application N=8 → N=9 cumulative post-RSAD-1 codification; 7 first-Critic findings on slice-017 draft empirically confirm prediction)

## Out of scope

- `tools/tphd_1_audit.py` standalone audit tooling — v2 candidate per ADR-016 Cost summary; deferred until N≥3 TPHD-1 violations recur post-codification (mirrors slice-016 ADR-015 `tools/rpcd_1_audit.py` deferral)
- `agents/critique.md` Dim 9 10th sub-clause for TPHD-1 — TPHD-1 is a /build-slice + /critique skill discipline, not an adversarial-prompt content discipline; first-Critic catching staleness at /critique time is a separate v2 candidate if N≥3 first-Critic-MISS instances of this class recur
- mini-CAD-1 byte-equality on `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` + `skills/build-slice/SKILL.md` — defer to v2 if drift surfaces (mirrors slice-010 `test_slice_skill_drift.py` precedent — INST-2 generalization deferred)
- Open R-1 (cwd-mismatch /diagnose) + R-2 (no programmatic /diagnose warning test) — stale risks since slice-001/002; require `/repro` first per slice-016 reflection; explicitly out of scope per slice-017 mission brief
- Windows cp1252 console encoding workaround (N=2 cumulative at slice-016 watch-list) — separate candidate `audit-tools-default-utf8-stdout`; promote at N=3 if recurs at slice-018+
- 3-layer-Critic-stack-accountability Dim 9 sub-class refinement — slice-014 N=1 + slice-016 N=2 watch-list; promote to Dim 9 10th sub-clause at N=3 if recurs at slice-018+ (separate slice scope)

## Dependencies

- Prior slices: [[slice-010-promote-voluntary-critic-on-cross-cutting-to-slice-default-heuristic]] — MCT-1 trigger glob list extends to slice-017 ensuring critic-required:true; [[slice-016-refine-dim-9-with-runtime-prerequisite-completeness-sub-class]] — N=1 cross-slice anchor + 3-layer-Critic-stack-accountability discovery
- Vault refs: [[methodology-changelog.md]] (entry v0.32.0 target), [[architecture/decisions/ADR-016]] (NEW), [[architecture/shippability.md]] (row 17 target), [[skills/critique/SKILL.md]], [[skills/critique-review/SKILL.md]], [[skills/build-slice/SKILL.md]]
- Risk register: no entries — TF-1-plan-staleness pattern is a methodology-internal lesson, not a registered risk; no risk-register changes expected this slice

## Mid-slice smoke gate

At ~50% of build (after Phase 1a-1e INSERT/Edit on the 3 skill files + methodology-changelog v0.32.0 entry, BEFORE writing prose-pin tests in Phase 2 per /critique m2 ACCEPTED-FIXED Phase-range correction):

```
<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_methodology_changelog.py::test_plugin_yaml_version_matches_version_file_invariant tests/methodology/test_critique_agent_drift.py -q
```

Expected: 2 PASS (PMI-1 v1.1 invariant + CAD-1 byte-equality on agents/critique.md). If fails: STOP, diagnose. PMI-1 fail would mean atomic version bump 0.31.0 → 0.32.0 not yet propagated across all 3 files (`plugin.yaml.version` + `VERSION` + `~/.claude/ai-sdlc-VERSION`). CAD-1 fail would mean agents/critique.md was accidentally edited (this slice should NOT touch agents/critique.md; if it did, EPGD-1 self-application has been violated).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list (12 items) fully addressed
- [ ] `tools/test_first_audit.py --strict-pre-finish` passes on mission-brief TF-1 plan (all 10 PENDING rows transitioned to PASSING via test-first protocol + 1 mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition N=8 → N=9 stable + 1 catalog-level row deferred to /validate-slice)
- [ ] /drift-check passes — vault claims match code reality (3 skill files + methodology-changelog + ADR-016 + shippability.md + 4 test files all consistent with mission-brief + design.md claims)
- [ ] Mid-slice smoke still passes (PMI-1 v1.1 invariant + CAD-1 byte-equality both green)
- [ ] No new TODOs / FIXMEs / debug prints in any modified file
- [ ] Shippability catalog 17/17 PASS at /validate-slice Step 5.5 in <2 min aggregate (row 17 added; rows 1-16 no regression)
- [ ] Bidirectional sha256 forensic capture: methodology-changelog.md byte-equal in-repo ↔ installed at slice end (N=12 → N=13 stable); agents/critique.md unchanged at slice-016 ship hash `f34c967eaaa34413...` (CAD-1 byte-equality preserved through slice; EPGD-1 self-application empirically confirmed at validate time)
- [ ] TPHD-1 self-application probe: this slice IS the canonical reference instance of TPHD-1 — at /critique + /critique-review fix-prose, if any test function names change, the TF-1 plan above MUST be synchronized in the same fix block (sub-modes (a) + (b)); at /build-slice Prerequisite check, the TF-1 plan MUST be re-verified against actual built test file names BEFORE Step 1 plan-mode entry (sub-mode (c)); validate-using-your-own-ship N=14 → N=15 stable. **EMPIRICALLY DEMONSTRATED at slice-017 /critique**: sub-mode (a) self-application N=1 standalone — when /critique M2 ACCEPTED-FIXED renamed `_phase_0_step_*` → `_prerequisite_check_bullet_*` in TF-1 plan rows 8-9, the mission-brief TF-1 plan was harmonized in the SAME fix block per TPHD-1 sub-mode (a).
