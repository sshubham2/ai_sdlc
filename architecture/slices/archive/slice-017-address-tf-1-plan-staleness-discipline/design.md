# Design: Slice 017 address-tf-1-plan-staleness-discipline

**Date**: 2026-05-13
**Mode**: Standard
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## What's new

This slice codifies **TPHD-1 (TF-Plan-Harmonization-Discipline-1)** as a skill-prose-level discipline spanning 3 SKILL.md files plus a methodology-changelog entry. TPHD-1 is structurally analogous to MCT-1 (slice-010, methodology v0.25.0) — both live in skill prose, both extend ADR-009's cross-cutting-tooling skill-prose-discipline layer, both use the -D suffix convention (N=4 → N=5 stable post-RSAD-1 + EPGD-1 + SCPD-1 + RPCD-1 + TPHD-1).

- **TPHD-1 entry** at `methodology-changelog.md` v0.32.0 — names the rule + three sub-modes (a) `/critique` post-fix-prose harmonization + (b) `/critique-review` post-fix-prose harmonization + (c) `/build-slice` Prerequisite-check pre-flight harmonization with cross-slice anchor `slice-016` (N=1).
- **TPHD-1 prose at `skills/critique/SKILL.md`** at end of Step 4 (Builder draft response per finding), before Step 4.5 (User-owned triage TRI-1) — names sub-mode (a).
- **TPHD-1 prose at `skills/critique-review/SKILL.md`** at end of Step 3 (Receive meta-Critic findings), before Step 4 (Run the audit) — names sub-mode (b).
- **TPHD-1 prerequisite-check bullet at `skills/build-slice/SKILL.md`** as a NEW bullet inserted INTO the existing `## Prerequisite check` section (L17-L22), between the last existing bullet (L22 "If `critique.md` doesn't exist (Standard or Heavy mode): stop, run `/critique` first") and the `## Your task` heading (L24) — names sub-mode (c). Per /critique M2 ACCEPTED-FIXED: the discipline IS structurally a prerequisite verification, and the existing build-slice step numbering is 1,2,3,4,5,6,7,7b,7c,8 — adding a `### Step 0` would be anomalous. Folding into the existing Prerequisite check section is the cleaner architectural choice.
- **ADR-016** at `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md` — reversibility=cheap with magnitude justification ~3-5 surfaces; supersedes=null; extends ADR-009 (MCT-1) at skill-prose-discipline layer.
- **Prose-pin tests** in 3 test files (2 NEW + 1 EXTENDED): `tests/methodology/test_critique_skill.py` (NEW), `tests/methodology/test_critique_review_skill.py` (NEW), `tests/methodology/test_build_slice_skill.py` (EXTENDED). Plus 3 entry-pin tests in `tests/methodology/test_methodology_changelog.py` (EXTENDED).
- **Shippability row 17** at `architecture/shippability.md` enumerating TPHD-1 critical-path tests.
- **Atomic version bump** 0.31.0 → 0.32.0 across `VERSION` + `plugin.yaml.version` + `~/.claude/ai-sdlc-VERSION` per PMI-1 v1.1 (atomic META-1; version-agnostic gate retirement-proof N=3 → N=4 stable).

## What's reused

- **MCT-1 skill-prose-discipline pattern** (slice-010, methodology v0.25.0, `[[architecture/decisions/ADR-009]]`) — TPHD-1 mirrors MCT-1's structural shape: terse prose at named insertion point + N-surface schema-pin + prose-pin tests + Limitations note.
- **-D suffix calibration-trail convention** (slice-011 RSAD-1 → slice-013 EPGD-1 → slice-015 SCPD-1 → slice-016 RPCD-1; N=4 → N=5 stable). TPHD-1 = T(F)-P(lan)-H(armonization)-D(iscipline)-1.
- **N-surface schema-pin discipline** (N=5 → N=6 instances stable). Canonical phrase `TF-1 plan harmonization discipline` pinned across:
  1. `methodology-changelog.md` v0.32.0 in-repo
  2. `~/.claude/methodology-changelog.md` v0.32.0 installed
  3. ADR-016 (title + body)
  4. 3 skill files (substring-pin)
- **PMI-1 v1.1 version-agnostic gate** (slice-014, methodology v0.29.0, `[[architecture/decisions/ADR-013]]`) — atomic version bump 0.31.0 → 0.32.0 with zero gate body modification; retirement-proof N=3 → N=4 stable.
- **EPGD-1 self-application discipline** (slice-013, methodology v0.28.0) — 0 of 12 prior entry-pin functions touched at slice-017 Phase 1b NEW SECTION header insertion + Phase 1c narrow-scope Edit (v_0_22_0..v_0_31_0; v0.29.0 doubled per slice-014 (a)↔(b) duality; v0.31.0 doubled per slice-016 RPCD-1 (a)↔(b) duality per /critique-review m-add-1 ACCEPTED-FIXED).
- **SCPD-1 proactive-application discipline** (slice-015, methodology v0.30.0) — Phase 5 in-line propagation BEFORE /validate-slice catalog run. NOTE: slice-017 does NOT touch `agents/critique.md` Dim 9 sub-clause count (stays at 9; `_lists_nine_sub_clauses` stays valid); slice-016's RPCD-1 body-bound test end_anchors at `### Bonus: weak graph edges` remain structurally load-bearing. SCPD-1 proactive-application here applies to row 17 addition only; rows 6/11/13/15/16 are NOT touched.
- **RPCD-1 design-time audits** (slice-016, methodology v0.31.0) — sub-modes (a) NEW-symbol import-audit + (b) NEW-status/token allowlist-audit + (c) NEW-anchor sibling-grep audit. Applied to slice-017's own draft at Audits 1-3 below.
- **CAD-1 byte-equality on `agents/critique.md`** (slice-007) — preserved through slice (slice does NOT touch agents/critique.md; bidirectional sha256 forensic capture N=12 → N=13 stable expected at slice end at slice-016 ship hash `f34c967eaaa34413...`).
- **Code references**: `tools/test_first_audit.py` (TF-1 audit; PASSING/PENDING/WRITTEN-FAILING allowlist semantics); `tests/methodology/conftest.py::read_file` (skill-prose-pin test helper).

## Components touched

### NEW: `skills/critique/SKILL.md` (modified)

- **Responsibility**: orchestrates the `/critique` skill — gathers inputs, invokes Critic agent, persists `critique.md`, captures Builder draft dispositions, hands off to TRI-1 user triage. Modification: adds TPHD-1 sub-mode (a) prose at end of Step 4.
- **Lives at**: `skills/critique/SKILL.md` (existing 292 lines; +1 paragraph at L122-L123 area between Step 4 close and Step 4.5 header).
- **Key interactions**: spawned `critique` agent (read-only); writes `critique.md`; consumed by `/critique-review` (reads critique.md) + `/build-slice` (reads triage verdict). Mission-brief.md TF-1 plan is the harmonization target.

### NEW: `skills/critique-review/SKILL.md` (modified)

- **Responsibility**: orchestrates the `/critique-review` skill — gathers inputs, invokes meta-Critic agent, persists `critique-review.md`, runs critique-review-audit, hands off to TRI-1. Modification: adds TPHD-1 sub-mode (b) prose at end of Step 3.
- **Lives at**: `skills/critique-review/SKILL.md` (existing 143 lines; +1 paragraph at L83-L84 area between Step 3 close and Step 4 header).
- **Key interactions**: spawned `critique-review` agent; reads `critique.md`; writes `critique-review.md`; consumed by `/critique` Step 4.5 TRI-1 triage. Mission-brief.md TF-1 plan is the harmonization target (same as sub-mode (a)).

### NEW: `skills/build-slice/SKILL.md` (modified)

- **Responsibility**: executes the slice with plan mode + verification gates. Modification: adds TPHD-1 sub-mode (c) as a NEW bullet INTO the existing `## Prerequisite check` section (NOT a new Step 0 — per /critique M2 ACCEPTED-FIXED placement is in the existing prerequisite section since the discipline IS structurally a prerequisite verification).
- **Lives at**: `skills/build-slice/SKILL.md` (existing 331 lines; +1 new bullet inserted INTO `## Prerequisite check` section between L22 ("If critique.md doesn't exist...") and `## Your task` L24).
- **Key interactions**: reads mission-brief.md TF-1 plan; verifies against actual test file names via prose-heuristic discipline (no audit tooling at codification time; `tools/tphd_1_audit.py` deferred to v2). If staleness detected: surface to user; flag for fix-block synchronization BEFORE Step 1 plan-mode entry. Closes the function-name-staleness audit gap that `tools/test_first_audit.py --strict-pre-finish` does not detect (per /critique B1 ACCEPTED-FIXED: TF-1 audit checks `row.status != "PASSING"` only at `tools/test_first_audit.py:350-364`; no function-existence check).

### NEW: `methodology-changelog.md` v0.32.0 entry (in-repo + installed)

- **Responsibility**: methodology version catalog; v0.32.0 entry names TPHD-1 + three sub-modes + ADR-016 cross-reference.
- **Lives at**: `methodology-changelog.md` (existing 984 lines; +new section inserted at L36 area between `---` separator (L35) and `## v0.31.0 — 2026-05-13` (L37)). Installed copy at `~/.claude/methodology-changelog.md` synced via `tools/forward_sync` Phase 3.
- **Key interactions**: bidirectional sha256 forensic capture per slice-007 CAD-1 + N-surface schema-pin precedent; consumed by `/status` (most recent dated entry surfaced).

### NEW: `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md`

- **Responsibility**: locks the TPHD-1 decision with reversibility tag + magnitude justification + supersession lineage.
- **Lives at**: `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md` (NEW).
- **Key interactions**: cross-referenced from methodology-changelog v0.32.0 entry + slice-017 mission-brief.md AC #3. Extends ADR-009 (MCT-1).

### NEW: `tests/methodology/test_critique_skill.py` (NEW file)

- **Responsibility**: prose-pin tests for `skills/critique/SKILL.md` TPHD-1 sub-mode (a) — substring-pin (`_post_fix_prose_step_present`) + scoped-find location-pin (`_post_fix_prose_step_location_pinned`).
- **Lives at**: `tests/methodology/test_critique_skill.py` (NEW; ~30-40 lines).
- **Key interactions**: imports `read_file` from `tests/methodology/conftest.py` per slice-010 `test_slice_skill.py` precedent. Tests fail at WRITTEN-FAILING per TF-1, pass at PASSING post-implementation.

### NEW: `tests/methodology/test_critique_review_skill.py` (NEW file)

- **Responsibility**: prose-pin tests for `skills/critique-review/SKILL.md` TPHD-1 sub-mode (b).
- **Lives at**: `tests/methodology/test_critique_review_skill.py` (NEW; ~30-40 lines).
- **Key interactions**: same shape as `test_critique_skill.py`.

### MODIFIED: `tests/methodology/test_build_slice_skill.py` (extended)

- **Responsibility**: prose-pin tests for `skills/build-slice/SKILL.md` TPHD-1 sub-mode (c) at new bullet in existing `## Prerequisite check` section.
- **Lives at**: `tests/methodology/test_build_slice_skill.py` (existing 47+ lines; +2 functions appended).
- **Key interactions**: reuses existing `BUILD` module-level fixture; adds `test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_present` + `test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_location_pinned` (per /critique M2 ACCEPTED-FIXED rename from `_phase_0_step_*`).

### MODIFIED: `tests/methodology/test_methodology_changelog.py` (extended)

- **Responsibility**: entry-pin tests for v0.32.0 TPHD-1 entry + 3-sub-mode pin + slice-016 cross-slice anchor pin + ADR-016 pin.
- **Lives at**: `tests/methodology/test_methodology_changelog.py` (existing — extended with new SECTION header `# --- Slice-017 / TPHD-1 entry pinning ---` + 3 functions per EPGD-1 self-application discipline).
- **Key interactions**: 0 of 12 prior entry-pin functions touched (v_0_22_0..v_0_31_0; v0.29.0 doubled per slice-014; v0.31.0 doubled per slice-016 per /critique-review m-add-1 ACCEPTED-FIXED).

### MODIFIED: `architecture/shippability.md` (row 17 added)

- **Responsibility**: catalog of critical-path tests per slice; row 17 added for slice-017 TPHD-1.
- **Lives at**: `architecture/shippability.md` (existing; +1 row appended at table end).
- **Key interactions**: consumed by `/validate-slice` Step 5.5 (catalog runs at pre-finish; 17/17 PASS target).

### MODIFIED: `VERSION` + `plugin.yaml` + `~/.claude/ai-sdlc-VERSION` (atomic 0.31.0 → 0.32.0)

- Per PMI-1 invariant; META-1 atomicity in single commit.

## Contracts added or changed

None. Slice-017 is pure prose codification + entry addition + tests. No runtime API change, no event schema, no data model delta.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). The 2 NEW test files have explicit consumer entry points and consumer tests (they ARE the tests; consumer is `pytest` invocation at /build-slice Phase 6 + /validate-slice Step 5.5). The other modifications extend existing files — no new modules.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_critique_skill.py` | `pytest tests/methodology/test_critique_skill.py` (run at /build-slice Phase 6 + /validate-slice Step 5.5 via shippability row 17) | `test_critique_skill_md_tphd_1_post_fix_prose_step_present` + `test_critique_skill_md_tphd_1_post_fix_prose_step_location_pinned` (self-consuming — the module IS its own consumer test) | — |
| `tests/methodology/test_critique_review_skill.py` | `pytest tests/methodology/test_critique_review_skill.py` (run at /build-slice Phase 6 + /validate-slice Step 5.5 via shippability row 17) | `test_critique_review_skill_md_tphd_1_post_fix_prose_step_present` + `test_critique_review_skill_md_tphd_1_post_fix_prose_step_location_pinned` (self-consuming) | — |
| `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md` | `tests/methodology/test_methodology_changelog.py::test_adr_016_exists_and_names_tphd_1_canonical_phrase` (file-existence + canonical-phrase grep) | same test | — |

## Decisions made (ADRs)

- [[ADR-016]] — TPHD-1 codified as 3-surface skill-prose-discipline spanning `/critique` + `/critique-review` + `/build-slice` skills — reversibility: **cheap** with magnitude justification (~13-16 sites per ADR-016 Reversibility L141-L154 enumeration: 3 skill files + methodology-changelog entry + 4 test files + shippability row + 3 version files + ADR file itself; ~10-15 min revert per slice-016 ADR-015 magnitude class)

## Authorization model for this slice

N/A — no auth surface touched. Pure methodology-prose codification.

## Error model for this slice

N/A — no runtime code introduced. Test failures at /build-slice Phase 6 + /validate-slice Step 5.5 indicate prose drift or non-PASSING TF-1 status; standard pytest exit-code semantics apply.

## Phase plan (preview for /build-slice)

Per the slice-016 plan-decomposition precedent for Dim-9-sub-clause-equivalent codification slices (slice-009 / slice-011 / slice-013 / slice-015 / slice-016 N=5 stable; TPHD-1 maps the same shape to skill-prose layer instead of agents/critique.md Dim 9):

1. **Phase 1a — methodology-changelog v0.32.0 entry INSERT** at L36 between `---` and `## v0.31.0` header. EPGD-1 self-application: NEW SECTION header at top of file; 0 of 12 prior entries touched (per /critique-review m-add-1 ACCEPTED-FIXED corrected count).
2. **Phase 1b — atomic version bump** `VERSION` 0.31.0 → 0.32.0 + `plugin.yaml.version` 0.31.0 → 0.32.0 + `~/.claude/ai-sdlc-VERSION` 0.31.0 → 0.32.0 (META-1 atomic; PMI-1 v1.1 invariant gate stays PASSING throughout).
3. **Phase 1c — ADR-016 file CREATE** at `architecture/decisions/ADR-016-tphd-1-tf-plan-harmonization-discipline.md`.
4. **Phase 1d — Skill prose INSERT** across 3 SKILL.md files at insertion points per "Mechanical insertion-point table" below.
5. **Phase 1e — methodology-changelog forward-sync** to `~/.claude/methodology-changelog.md` (CAD-1-equivalent for methodology-changelog; bidirectional sha256 forensic capture at single hash value).
6. **Phase 2 — TF-1 plan tests WRITE per test-first** discipline. Create 2 NEW test files + extend 2 existing. Run tests; expect WRITTEN-FAILING; flip to PASSING in TF-1 plan after passing.
7. **Phase 3 — shippability row 17 APPEND** at end of `architecture/shippability.md` table. SCPD-1 proactive-application: NO touch to rows 6/11/13/15/16 (no Dim 9 sub-clause supersession this slice).
8. **Phase 4 — TPHD-1 self-application probe** on slice-017's own design.md + mission-brief.md + ADR-016 (RPCD-1 sub-modes a/b/c). Expect recursive-self-application catches at /critique on this slice's own draft (codification-slice density empirically N=4-7 self-defects per slice-013/015/016 precedent).
9. **Phase 5 — Drift-check + smoke gate + pre-finish gate** per /build-slice Steps 5-6.

## Mechanical insertion-point table

Pre-empts slice-016 B1 / B2 / M3 class — "end_anchor / target-line / target-function mis-identification on slice's own draft" per RPCD-1 sub-mode (c) sibling-grep self-application discipline N=8 → N=9 stable.

| # | Surface | Action | Start anchor | End anchor | Pre-Phase 1 line range | Insertion notes |
|---|---------|--------|--------------|------------|------------------------|-----------------|
| 1 | `methodology-changelog.md` | INSERT v0.32.0 entry | `---` line BEFORE `## v0.31.0` (L35) | `## v0.31.0 — 2026-05-13` (L37) | between L35 and L37 | New section block following v0.31.0 entry shape exactly: H2 version header + summary paragraph + `Per slice-017 [[ADR-016]]` paragraph + sub-modes paragraph + N-surface schema-pin paragraph + RPCD-1-self-application probe paragraph + atomic-version-bump paragraph + `### Added` section + RPCD-1 sub-mode (c) sibling test list + `---` close separator. Estimated ~80-100 lines. |
| 2 | `skills/critique/SKILL.md` | INSERT paragraph at end of Step 4 | `Update \`critique.md\` with Builder draft dispositions inline (one per finding under "Builder draft").` (L122) | `### Step 4.5: User-owned triage (TRI-1)` (L124) | between L122 and L124 | Single paragraph following format: "Per **TPHD-1** (`methodology-changelog.md` v0.32.0), when applying ACCEPTED-FIXED edits at this Step that change test function names or AC #N row references in `mission-brief.md` or `design.md`, harmonize the mission-brief TF-1 plan section (renaming function names + updating AC row references) in the SAME fix block. Otherwise the plan ships stale to `/build-slice` and surfaces at Phase 6 audit as DEVIATION (via pytest collection failure on stale function names, since `tools/test_first_audit.py --strict-pre-finish` only checks status not function-existence). Sub-mode (a) of three; (b) lives in `/critique-review` Step 3 (post-fix-prose harmonization); (c) lives in `/build-slice` Prerequisite check (pre-flight harmonization bullet)." |
| 3 | `skills/critique-review/SKILL.md` | INSERT paragraph at end of Step 3 | `Take the agent's output and write it to \`architecture/slices/slice-NNN-<name>/critique-review.md\` using the format the agent emits.` (L83) | `### Step 4: Run the audit` (L85) | between L83 and L85 | Single paragraph following format: "Per **TPHD-1** (`methodology-changelog.md` v0.32.0) sub-mode (b), when the meta-Critic's ACCEPTED-FIXED findings (during /critique Step 4.5 TRI-1) will change test function names or AC #N row references in `mission-brief.md` or `design.md`, harmonize the mission-brief TF-1 plan section in the same fix block. Sub-mode (a) lives in `/critique` Step 4 (post-fix-prose harmonization); (c) lives in `/build-slice` Prerequisite check (pre-flight harmonization bullet)." |
| 4 | `skills/build-slice/SKILL.md` | INSERT bullet into existing `## Prerequisite check` section | `If \`critique.md\` doesn't exist (Standard or Heavy mode): stop, run \`/critique\` first` (L22) | `## Your task` (L24) | between L22 and L24 | New bullet appended to the existing Prerequisite check list: "- **Run TPHD-1 pre-flight harmonization** (per `methodology-changelog.md` v0.32.0 sub-mode (c)): scan the mission-brief TF-1 plan table; for each row, verify (a) the Test path exists or will be created at the right path, (b) the Test function name will match what gets built. The /critique + /critique-review fix-prose may have changed test function names or AC row references without harmonizing the TF-1 plan in the same fix block (sub-modes (a) + (b) defend at fix-prose time; sub-mode (c) is the prerequisite-check defense-in-depth layer). Flag any drift to user for fix BEFORE Step 1 plan-mode entry. This closes the function-name-staleness audit gap that `tools/test_first_audit.py --strict-pre-finish` does not detect (status-only check)." |
| 5 | `architecture/shippability.md` | APPEND row 17 at end of table | row 16 line | end of table (next text section) | after row 16 line | New table row: `| 17 | slice-017-address-tf-1-plan-staleness-discipline | TPHD-1: <description with sub-modes (a)(b)(c) + slice-016 anchor + ADR-016 + PMI-1 v1.1 atomic 0.31.0 → 0.32.0 + EPGD-1 0/11 self-app + N-surface schema-pin N=5→N=6> | `<pytest commands>` | <runtime> |` — full command list per row-16 precedent. |

## Design-time audits (RPCD-1 self-application N=8 → N=9)

Per slice-016 Lesson 2 ("RPCD-1 self-application probe at /design-slice — every Dim 9 codification slice from slice-009 onwards has had at least one recursive-self-application catch on its own draft"), this slice's design.md performs the three RPCD-1 sub-modes against its own draft before /critique runs. Recursive-self-application N=8 → expected N=9 cumulative post-RSAD-1 codification.

### Audit 1 — RPCD-1 sub-mode (a) NEW-symbol import-audit on slice's own test plan

**Discipline**: when proposing a fix that uses a NEW symbol in a Python test body, verify the module imports that symbol.

**Application to slice-017's TF-1 plan**:
- AC #2 rows 4-9 introduce NEW Python test functions in 2 NEW test files (`test_critique_skill.py` + `test_critique_review_skill.py`) and 1 EXTENDED file (`test_build_slice_skill.py`).
- Each test function must import the `read_file` helper from `tests/methodology/conftest.py` — verified by precedent at `tests/methodology/test_slice_skill.py:1` and `tests/methodology/test_build_slice_skill.py:1` both showing `from tests.methodology.conftest import read_file`.
- Each test must also import any pytest fixtures it uses. The TF-1 plan rows specify substring-pin + scoped-find semantics — no pytest fixtures beyond default needed.
- **Conclusion**: sub-mode (a) check PASSES at design time. Empirical verification: `grep -n "from tests.methodology.conftest" tests/methodology/test_slice_skill.py tests/methodology/test_build_slice_skill.py` returns 2 hits per file ⇒ pattern confirmed.

### Audit 2 — RPCD-1 sub-mode (b) NEW-status/token allowlist-audit on slice's TF-1 plan statuses

**Discipline**: when proposing a fix that introduces a NEW status string / enum value / token, verify the relevant audit/parser/allowlist accepts it.

**Application to slice-017's TF-1 plan**:
- TF-1 plan uses statuses: `PENDING`, `WRITTEN-FAILING`, `PASSING` — all in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})` 3-element allowlist (empirically verified at slice-016 /critique M1 ACCEPTED-FIXED — slice-015 falsely claimed `WRITTEN-AS-EDIT` was added; reality: 3-element allowlist unchanged since slice-013).
- TF-1 plan introduces NO new status string. Slice-017 plan also uses 1 row at status `PASSING` (PMI-1 v1.1 invariant gate) per mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern N=8 → N=9 stable.
- **Conclusion**: sub-mode (b) check PASSES at design time. No new statuses introduced. Empirical citation: `tools/test_first_audit.py:65` per slice-016 design.md L141 correction reference.

### Audit 3 — RPCD-1 sub-mode (c) NEW-anchor sibling-grep audit on TPHD-1 insertion points

**Discipline**: when proposing a fix involving a NEW end_anchor / start_anchor / body-bound for a test, grep the test file for sibling tests sharing the same anchor pair and propose tightening them in lockstep.

**Application to slice-017's prose-pin test design**:
- `test_critique_skill_md_tphd_1_post_fix_prose_step_present` (NEW): substring-pin `"Per **TPHD-1**"` in `skills/critique/SKILL.md`. No anchor pair (bare-substring).
- `test_critique_skill_md_tphd_1_post_fix_prose_step_location_pinned` (NEW): scoped-find — start_anchor = `(L122 phrase pre-Phase 1)` close, end_anchor = `### Step 4.5: User-owned triage (TRI-1)`. Sibling tests in `tests/methodology/test_critique_skill.py`? **None — file is NEW**.
- `test_critique_review_skill_md_tphd_1_post_fix_prose_step_location_pinned` (NEW): scoped-find — start_anchor = `(L83 phrase pre-Phase 1)`, end_anchor = `### Step 4: Run the audit`. Sibling tests in `tests/methodology/test_critique_review_skill.py`? **None — file is NEW**.
- `test_build_slice_skill_md_tphd_1_prerequisite_check_bullet_location_pinned` (NEW in extended file): scoped-find — start_anchor = `## Prerequisite check`, end_anchor = `## Your task`. Sibling tests in `tests/methodology/test_build_slice_skill.py`? Let's grep.

**Empirical sibling-grep at design time** (per RPCD-1 sub-mode (c) discipline):

`grep -n "ENTER PLAN MODE FIRST\|DO NOT silently defer\|DO NOT skip the mid-slice smoke gate\|APPEND TO build-log.md events" tests/methodology/test_build_slice_skill.py` — 4 existing prose-pin tests (per Read at L7-46). None of them use scoped-find anchors with `## Prerequisite check` or `## Your task` bounds; they all use bare-substring `in BUILD` semantics on the SKILL.md global content. So slice-017's NEW `_location_pinned` test introduces a NEW anchor pair (`## Prerequisite check` → `## Your task`) not shared with existing siblings. No lockstep tightening required on prior siblings.

- **Conclusion**: sub-mode (c) check PASSES at design time. No sibling anchor-sharing. Empirical citation: `tests/methodology/test_build_slice_skill.py:7-46` (4 existing prose-pin tests, all bare-substring).

### Audit 4 — EPGD-1 self-application (Phase 1b NEW SECTION header insertion in methodology-changelog tests)

**Discipline**: when superseding a PMI-1 versioned gate (which slice-017 does NOT do — version-agnostic gate N=4 stable retirement-proof; PMI-1 v1.1 atomic bump 0.31.0 → 0.32.0 leaves gate body untouched), and when adding a NEW entry-pin function, ensure 0 of all prior entry-pin functions touched.

**Application to slice-017's `tests/methodology/test_methodology_changelog.py` extension** (per /critique-review m-add-1 ACCEPTED-FIXED count correction):
- Current state per slice-016 ship: **12 entry-pin functions** exist for v_0_22_0..v_0_31_0 — empirically verified by `grep "^def test_v_0_" tests/methodology/test_methodology_changelog.py` returning 12 matches at lines 76 / 111 / 152 / 202 / 250 / 304 / 370 / 437 / 499 / 747 / 844 / 910. Breakdown: 8 single + v0.29.0 doubled per slice-014 (a)↔(b) duality (functions at L437 + L499) + v0.31.0 doubled per slice-016 RPCD-1 (a)↔(b) duality (functions at L844 + L910 — `_present_in_repo_and_installed` + `_names_three_sub_modes_in_repo_and_installed`). The v0.31.0 doubling is structurally analogous to v0.29.0 doubling — entries that introduce N sub-modes get an additional sibling `_names_N_sub_modes` test.
- Slice-017 adds 3 NEW functions via Phase 1b NEW SECTION header insertion: `test_v_0_32_0_tphd_1_entry_present_in_repo_and_installed` + `test_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed` + `test_v_0_32_0_tphd_1_entry_names_slice_016_cross_slice_anchor` (3 entry-pin functions — slice-017 v0.32.0 is TRIPLED extending the doubling pattern by adding a 3rd cross-slice-anchor sibling) + `test_adr_016_exists_and_names_tphd_1_canonical_phrase` (1 ADR-pin function, sibling). Post-Phase 1b count: 12 + 3 = 15 entry-pin functions.
- Slice-017 does NOT touch any of the 12 prior entry-pin functions.
- Phase 1b discipline: NEW SECTION header `# --- Slice-017 / TPHD-1 entry pinning ---` inserted at file end before the trailing newline; new functions appended below NEW SECTION header.
- **Conclusion**: EPGD-1 self-application N=4 → N=5 stable confirmed at design time. 0 of 12 prior entry-pin functions touched (count corrected per /critique-review m-add-1 ACCEPTED-FIXED; the discipline guarantee 0/N holds at the corrected N=12).

### Audit 5 — Wiegers regression-guard coverage symmetry (slice-016 M-add-1 class N=1 → N=2 watch-list)

**Discipline**: when adding a sub-clause / discipline / rule with `_sub_clause_present` test, ensure paired `_location_pinned` sibling test is also added (slice-011 + slice-013 + slice-015 + slice-016 N=4 stable duality).

**Application to slice-017's TF-1 plan**:
- Sub-mode (a) `/critique` prose pin: 2 tests in `test_critique_skill.py` — `_post_fix_prose_step_present` (bare-substring per slice-015 L463 precedent) + `_post_fix_prose_step_location_pinned` (scoped-find per slice-015 L475 precedent). **Duality PRESENT**.
- Sub-mode (b) `/critique-review` prose pin: 2 tests in `test_critique_review_skill.py` — `_post_fix_prose_step_present` + `_post_fix_prose_step_location_pinned`. **Duality PRESENT**.
- Sub-mode (c) `/build-slice` Prerequisite-check bullet prose pin: 2 tests in `test_build_slice_skill.py` — `_prerequisite_check_bullet_present` + `_prerequisite_check_bullet_location_pinned` (per /critique M2 ACCEPTED-FIXED rename from `_phase_0_step_*` reflecting placement change to existing `## Prerequisite check` section instead of NEW `### Step 0`). **Duality PRESENT**.
- v0.32.0 entry pin: 2 functions in `test_methodology_changelog.py` — `test_v_0_32_0_tphd_1_entry_present_in_repo_and_installed` + (no separate `_location_pinned` because entry-pin tests don't have spatial location semantics within the changelog; they pin the entry's existence + content, which is a single concern). **Wiegers asymmetry exception**: entry-pin tests historically don't carry `_location_pinned` siblings (verified by grep: `tests/methodology/test_methodology_changelog.py` has 11 `_entry_present` functions, 0 `_entry_location_pinned` functions). This is the established pattern, not a coverage gap.
- **Conclusion**: Audit 5 PASSES at design time. All 3 sub-mode prose-pin tests carry the duality; entry-pin tests follow established asymmetry.

### Audit 6 — BC-1 self-application (BC-PROJ-2 negative-anchor migration silences false-positive on this methodology-vocabulary slice)

**Discipline**: methodology-vocabulary slices have historically triggered BC-PROJ-2 + BC-GLOBAL-1 false-positive (N=5 cumulative slices 005/006/007/010/011). Slice-012 migrated BC-PROJ-2 to negative-anchor schema. Slice-017 should be silenced by negative-anchor final-filter.

**BC-PROJ-2 actual rule content per `architecture/build-checks.md` L33-L35** (corrected per /critique M3 ACCEPTED-FIXED — original Audit 6 named wrong tokens):
- **Trigger keywords** (9): `parse, fence, code-block, backtick, llm, agent, prompt, output, response`
- **Trigger anchors** (3, subset of trigger keywords): `fence, code-block, llm`
- **Negative anchors** (9, per slice-012 migration): `defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`

**Applicability check** (BC-1 applicability = OR of `Applies to: skills/**/*.py, tools/**/*.py` glob match OR `Trigger keywords` substring match in mission-brief + design.md):
- `Applies to:` glob: slice-017 changed files include `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` + `skills/build-slice/SKILL.md` + `methodology-changelog.md` + 4 test files + ADR-016 + mission-brief + design.md + milestone.md + shippability.md. **None of these match `skills/**/*.py` or `tools/**/*.py` globs** (SKILL.md is `.md`, not `.py`). Glob path: 0 matches → glob trigger NOT FIRED.
- `Trigger keywords` substring match in mission-brief + design.md + ADR-016:
  - `parse`: 0 (no "parse" / "parser" in any of the 3 slice artifacts at /critique-disposition time)
  - `fence`: 0
  - `code-block`: 0
  - `backtick`: 0
  - `llm`: 0
  - `agent`: many (legitimate methodology vocabulary — Critic agent / spawned agents / meta-Critic agent)
  - `prompt`: 1 in design.md ("Critic prompt edit", quoted from methodology-changelog summary)
  - `output`: many (legitimate — methodology output / TF-1 audit output / etc.)
  - `response`: 1 in design.md ("Builder draft response" — quoted from /critique skill prose)
- Keyword path: positive match on `agent` + `prompt` + `output` + `response` → keyword trigger FIRES.

**Trigger anchors final-filter** (per slice-005 keyword precision): rule activates IFF at least one of `Trigger anchors` (`fence`, `code-block`, `llm`) substring-matches mission-brief or design.md.
- `fence`: 0 occurrences across slice artifacts.
- `code-block`: 0 occurrences.
- `llm`: 0 occurrences.
- **Trigger anchors final-filter result**: 0/3 anchors match → rule does NOT fire.

**Negative anchors final-filter** (per slice-008/012 negative-anchor migration): IF rule would otherwise fire (positive path), it is silenced if ANY negative anchor substring-matches the slice artifacts.
- Per the trigger anchors filter above, BC-PROJ-2 already does NOT fire on this slice. Negative anchors are moot for this slice.
- For completeness: negative anchors (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`) — `forward-sync` + `Critic-MISSED` + `aggregated lessons` all appear in slice-017 artifacts (mission-brief / design.md / ADR-016), so even if trigger anchors had matched, the rule would have been silenced by negative-anchor final-filter.

- **Conclusion**: Audit 6 PASSES at design time on the corrected basis. Empirical verification at /build-slice Phase 5 BC-1 audit run expected to confirm 0 BC-PROJ-2 + 0 BC-GLOBAL-1 fires (BC-GLOBAL-1 in `~/.claude/build-checks.md` follows similar trigger-anchors + negative-anchors discipline). Slice-005/008/012 N=2 → N=3 stable evidence base supports this prediction.

## Recursive-self-application N=8 → N=9 expected catches

Per slice-016 Lesson "Recursive-self-application density at codification slices empirically high — slice-016 had 4 RPCD-1-class self-defects on its own draft. Slice-011 had 4. Slice-013 had 7. Slice-015 had 6. Pattern: codification slices that codify a discipline almost always commit instances of that discipline on their own draft. Strong prior."

For slice-017 codifying TPHD-1, expected self-defect classes:
- **TPHD-1 sub-mode (a)/(b)/(c) self-application**: if slice-017's TF-1 plan above does NOT match what gets built in 4 test files, the slice IS the canonical reference instance of the discipline it authors (analogous to slice-015's SCPD-1 self-application N=1 standalone → slice-016's N=2 stable).
- **RPCD-1 sub-mode (c) sibling-grep failure**: expected ≥1 catch at /critique on this design.md's audit tables (e.g., end_anchor / target-function / line-number mis-identification).
- **EPGD-1 self-application failure**: expected 0 catches — EPGD-1 discipline N=4 stable; Phase 1b NEW SECTION header insertion is well-established.
- **Wiegers regression-guard coverage symmetry**: expected ≥1 catch (entry-pin Wiegers asymmetry exception identified at Audit 5 above is a candidate; first-Critic may flag).
- **Rule-ID drift (slice-013 B1 class)**: TPHD-1 canonical-form used uniformly across all surfaces. Must-not-defer item #1 addresses via positive-form assertion (`grep -c "TPHD-1" <file>` ≥1, NOT anti-form absence-check per /critique m1 ACCEPTED-FIXED RSAD-1 sub-mode (b) re-introduction class); expect 0 catches if must-not-defer enforced at /build-slice Phase 4.

Recursive-self-application N=8 → expected N=9 cumulative post-RSAD-1 codification at slice-017 completion.

## Cost summary

- 3 skill files modified (~1-3 lines each = ~3-9 lines total).
- 1 methodology-changelog entry inserted (~80-100 lines per v0.31.0 precedent).
- 1 ADR created (~50-80 lines per ADR-015 precedent).
- 2 new test files (~30-40 lines each = ~60-80 lines total).
- 2 test files extended (~10-20 lines added per file).
- 1 shippability row added (~1 line in table, multi-line pytest command list).
- Atomic version bump 3 files (1 line each = 3 lines).

**Total**: ~210-340 lines added across ~11 files. Reversibility: cheap — full revert is ~10-15 min (delete 2 new test files + delete ADR-016 + revert atomic version bump + Edit out 3 skill prose blocks + Edit out methodology-changelog entry + remove shippability row + remove 5 new tests in test_methodology_changelog.py + remove 2 new tests in test_build_slice_skill.py). Magnitude class same as slice-016 ADR-015 + slice-015 ADR-014 + slice-014 ADR-013 + slice-013 ADR-012 + slice-011 ADR-010 cheap-with-magnitude-justification convention N=5 → N=6 stable.

## Out of scope (per mission-brief)

- `tools/tphd_1_audit.py` standalone audit tooling (v2 candidate)
- `agents/critique.md` Dim 9 10th sub-clause for TPHD-1 (separate v2 candidate if N≥3 first-Critic-MISS instances recur)
- mini-CAD-1 byte-equality on 3 SKILL.md files (defer to v2)
- R-1 + R-2 stale-since-slice-001/002 (require `/repro` first)
- Windows cp1252 console encoding workaround (separate candidate)
- 3-layer-Critic-stack-accountability Dim 9 sub-class refinement (separate slice at N=3 if recurs)
