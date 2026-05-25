---
id: ADR-016
title: Codify TF-1 plan harmonization discipline as 3-surface skill-prose discipline spanning /critique + /critique-review + /build-slice skills (TPHD-1)
date: 2026-05-13
slice: slice-017-address-tf-1-plan-staleness-discipline
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-016: Codify TF-1 plan harmonization discipline (TPHD-1)

**Note on rule-ID naming** (per -D suffix calibration-trail convention N=4 → N=5 stable post-RSAD-1 v0.26.0 + EPGD-1 v0.28.0 + SCPD-1 v0.30.0 + RPCD-1 v0.31.0 + TPHD-1 v0.32.0): the rule is **TPHD-1 "TF-Plan-Harmonization-Discipline"** with **-D suffix** at end of abbreviation, signaling skill-prose-heuristic semantics applied at /critique-time + /critique-review-time + /build-slice-time, distinct from audit-enforced gate semantics of sibling rules (BC-1 / PMI-1 / CAD-1 / TF-1 / RR-1 / INST-1 / VAL-1 / WIRE-1 / NFR-1 / CSP-1, each with a corresponding `tools/*_audit.py` enforcing the rule programmatically). TPHD-1 lives in `skills/critique/SKILL.md` Step 4 + `skills/critique-review/SKILL.md` Step 3 + `skills/build-slice/SKILL.md` Step 0 body prose only. v2 candidate `tools/tphd_1_audit.py` (programmatic mission-brief TF-1-plan-vs-actual-tests harmonization check) deferred until N≥3 TPHD-1 violations recur post-codification at slice-018+.

## Context

The `/build-slice` skill's Phase 6 strict-pre-finish gate runs `tools/test_first_audit.py --strict-pre-finish` (per TF-1, `methodology-changelog.md` v0.13.0) which checks ONLY row-level status (`tools/test_first_audit.py:65` `_ALLOWED_STATUSES = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})` + `tools/test_first_audit.py:350-364` `--strict-pre-finish` clause emits `non-passing-pre-finish` when `row.status != "PASSING"`). The audit does NOT verify that the row's `test_function` name exists at the named `test_path` — there is no AST/grep introspection of test file bodies anywhere in `tools/test_first_audit.py`. Per slice-017 /critique B1 ACCEPTED-FIXED, this is a load-bearing factual correction: TPHD-1's value proposition is **prophylactic against an audit gap**, NOT a redundant defense to an existing audit check.

At slice-016 reflection, a NEW first-Critic-MISS class surfaced at N=1: **TF-1-plan-comprehensive-harmonization-vs-actually-built**. The pattern:

1. `/design-slice` writes the initial TF-1 plan with placeholder function names + all rows in PENDING status.
2. `/critique` fix-prose (Step 4 Builder draft ACCEPTED-FIXED) may change test function names or AC #N row references in `mission-brief.md` or `design.md`.
3. `/critique-review` fix-prose (during /critique Step 4.5 TRI-1 triage applying meta-Critic ACCEPTED-FIXED findings) may further change function names.
4. The mission-brief TF-1 plan does NOT always get harmonized in the same fix block.
5. The stale plan ships to `/build-slice` Phase 6 audit, where it surfaces as DEVIATION via two distinct failure modes:
   - **Status-staleness mode** (TF-1 audit DOES catch this): rows still in PENDING/WRITTEN-FAILING at Phase 6 → audit emits `non-passing-pre-finish` violation → exit 1.
   - **Function-name-staleness mode** (TF-1 audit does NOT catch this; surfaces only when `pytest` is run on the named function): rows transitioned to PASSING with stale function names → audit passes but `pytest test_path::stale_function` fails ImportError / no-such-test → surfaces in Phase 6 catalog run or /validate-slice Step 5.5.

Slice-016 concrete instances at /build-slice Phase 6:
- AC #3 row referenced placeholder `_adr_015_pinned_in_methodology_changelog_v_0_31_0` — actual built test function name was `_exists_and_names_rpcd_1_canonical_phrase`. **Function-name-staleness mode** (not caught by TF-1 audit; surfaced when row was flipped to PASSING and pytest collection failed).
- AC #5 shippability row referenced placeholder `_rpcd_1_body_pins_cross_slice_and_substantive_anchors` — pre-/critique-review M-add-1 placeholder; replaced post-M-add-1 ACCEPTED-FIXED with 5 actual body-bound test function names. **Function-name-staleness mode** (similar surface).
- All 10 TF-1 plan rows still in PENDING status at Phase 6 audit time. **Status-staleness mode** (caught by TF-1 audit `non-passing-pre-finish` violation kind; this is the violation that actually triggered Phase 6 audit exit 1 at slice-016).

The first Critic at slice-016 (finding B2 "TF-1 plan non-existent function names") caught the end_anchor-tighten rows' stale names BUT missed AC #3 row + AC #5 shippability row + the all-rows-PENDING-status issue. The meta-Critic (DR-1 dual review) ALSO missed these. Caught at `/build-slice` Phase 6 audit empirical failure as third-Critic-stack-layer defense — for the status-staleness mode by TF-1 audit programmatically + for the function-name-staleness mode by pytest collection failure at catalog run.

**TPHD-1's value proposition**: sub-modes (a)/(b) prevent function-name-staleness BEFORE it reaches /build-slice Phase 6 — closing an audit-gap (TF-1 audit does not detect stale function names). Sub-mode (c) prevents status-staleness AND function-name-staleness BEFORE Phase 1 plan-mode entry — defense-in-depth for both modes. The discipline is NOT redundant with the TF-1 audit; it's an upstream pre-empt covering the function-name-staleness mode entirely and the status-staleness mode redundantly (TF-1 catches status-staleness at Phase 6; TPHD-1 sub-mode (c) catches it at /build-slice Prerequisite check before Phase 1).

**3-layer Critic-stack accountability lineage**: this is the second instance (N=2 cumulative; slice-014 was N=1) of a NEW first-Critic-MISS class surfacing at /build-slice Phase 6 audit time after both first Critic + meta-Critic missed it at /critique-review.

Without explicit codification, every future codification slice (esp. Dim 9 sub-clause refinement slices similar to slice-009 / slice-011 / slice-013 / slice-015 / slice-016 N=5 cumulative) is at risk of repeating the slice-016 staleness pattern. The fix discipline is clear and structurally simple: harmonize mission-brief TF-1 plan vs actual built test function names in the SAME fix-prose block where the test function names changed. The cost of codification is small; the cost of waiting for N=2 recurrence is one more avoidable /build-slice Phase 6 DEVIATION.

Slice-016 reflection's lesson 1 explicitly recommends codification:

> **TF-1 plan harmonization at /build-slice Phase 0 (or end of /critique-review fix-prose)** — when /critique fix-prose OR /critique-review fix-prose changes test function names or AC #N row references, the mission-brief TF-1 plan needs synchronization in the same fix block. Otherwise the plan ships stale to /build-slice and surfaces at Phase 6 audit as DEVIATION. Generic methodology lesson at N=1; promote to /build-slice Phase 0 discipline at N=2 if recurs at slice-017+.

The user-invoked /slice at slice-017 with explicit `address-tf-1-plan-staleness-discipline` argument ratchets codification ahead of the typical N=2 promotion threshold. Justification: structurally clear lesson + small codification cost + N=2 3-layer-Critic-stack-accountability cumulative at slice-014 + slice-016 (independent secondary evidence supporting the discipline's class).

## Options considered

### Option 1 — 3-surface skill-prose discipline at /critique Step 4 + /critique-review Step 3 + /build-slice Prerequisite check (CHOSEN, refined per /critique M2)

Insert TPHD-1 prose at three named insertion points covering three sub-modes:
- (a) `/critique` Step 4 end: post-fix-prose harmonization — when applying ACCEPTED-FIXED Builder draft edits.
- (b) `/critique-review` Step 3 end: post-fix-prose harmonization — when meta-Critic ACCEPTED-FIXED findings will result in fix-prose during /critique Step 4.5.
- (c) `/build-slice` Prerequisite-check pre-flight: harmonization sweep added as a NEW bullet INTO the existing `## Prerequisite check` section (NOT a new `### Step 0` — per /critique M2 ACCEPTED-FIXED: build-slice/SKILL.md's step numbering is 1,2,3,4,5,6,7,7b,7c,8 with no Step 0; the discipline IS structurally a prerequisite verification; folding into existing Prerequisite check section is the cleaner architectural choice).

Codify in `methodology-changelog.md` v0.32.0 entry naming TPHD-1 + 3 sub-modes + cross-slice anchor `slice-016` (N=1) + N-surface schema-pin discipline N=5 → N=6 stable + Limitations note acknowledging prose-heuristic semantics (no audit-enforced gate; v2 candidate deferred).

Mirror MCT-1 (slice-010 ADR-009) structural shape: terse skill-prose paragraphs at named insertion points + N-surface schema-pin + prose-pin tests + Limitations note.

**Pros**:
- 3-surface coverage matches the 3 distinct Critic-stack layers where staleness can be introduced (first-Critic fix-prose / meta-Critic fix-prose) or detected proactively (/build-slice pre-flight).
- Skill-prose-only — no audit-enforced gate at codification time. Prose-heuristic discipline is reversible per slice-014 EPGD-1 retirement-proof precedent + slice-015 SCPD-1 retirement-proof precedent. v2 `tools/tphd_1_audit.py` candidate deferred per slice-016 RPCD-1 prose-first-audit-later convention N=4 → N=5 stable.
- Prose-pin test scaffolding mirrors slice-010 MCT-1 test_slice_skill.py precedent + slice-014/015/016 entry-pin + _location_pinned duality N=4 stable.
- Reversibility: cheap. Revert path is git diff + superseding changelog entry. ~10-15 min per slice-015 SCPD-1 + slice-016 RPCD-1 magnitude.

**Cons**:
- 3-surface insertion (vs 1-surface for MCT-1) adds more code-surface for prose drift. Mitigated by prose-pin tests with duality (substring-pin + location-pin per surface = 6 tests across 3 skill files).
- 3-layer Critic-stack defense has potential for redundancy — sub-modes (a) + (b) overlap somewhat at /critique Step 4.5 TRI-1 triage. Mitigated by distinct insertion points: (a) lives where Builder applies ACCEPTED-FIXED; (b) lives where meta-Critic findings get persisted before triage. Each layer covers a distinct lifecycle moment.

### Option 2 — Single-surface discipline at /build-slice Prerequisite check only

Insert TPHD-1 prose ONLY at `/build-slice` Prerequisite check as defensive pre-flight harmonization bullet. Skip insertion at /critique + /critique-review.

**Pros**: minimal codification — single surface; one prose bullet; one prose-pin test file extension. Easier revert.

**Cons**:
- 3-layer Critic-stack accountability principle violated — the discipline should be applied at the LEVEL where staleness is introduced (Critic-stack fix-prose) AND at the level where it's defended (Prerequisite check pre-flight). Single-layer codification means staleness is detected late (at /build-slice Prerequisite check) instead of pre-empted at /critique + /critique-review.
- Doesn't honor slice-016 reflection's "TF-1 plan harmonization at /build-slice Phase 0 (or end of /critique-review fix-prose)" — the "or" implies BOTH are valid insertion points; ideally both should carry the discipline.
- **Rejected**: single-surface coverage underspecifies the discipline.

### Option 3 — Promote to `agents/critique.md` Dim 9 10th sub-clause

Codify TPHD-1 as a NEW Dim 9 sub-clause in the adversarial Critic prompt, similar to RPCD-1 sub-mode (a/b/c).

**Pros**: first Critic catches staleness at /critique time before fix-prose ships stale plan.

**Cons**:
- TPHD-1 is a **timing/sequencing** discipline ("harmonize TF-1 plan in same fix block"), not an **adversarial-prompt content** discipline (which is what Dim 9 sub-clauses are — fixed dimensions the Critic attacks design along).
- The discipline applies at fix-prose application time, NOT at design-review time. The Critic at /critique time CAN catch stale function names (B2 partial catch at slice-016), but can't catch staleness that's introduced DURING /critique's own fix-prose round.
- /build-slice Phase 6 TF-1 audit is already a programmatic check (TF-1 audit refuses non-PASSING rows at strict-pre-finish). Adding Dim 9 sub-clause is redundant at that detection layer.
- **Rejected**: misclassifies the discipline. Promote to Dim 9 sub-clause at v2 only if N≥3 first-Critic-MISS instances of this specific class recur post-TPHD-1-codification.

## Decision

**Adopt Option 1** (refined per /critique M2 ACCEPTED-FIXED) — 3-surface skill-prose discipline at `/critique` Step 4 + `/critique-review` Step 3 + `/build-slice` Prerequisite-check (NEW bullet INTO existing section, NOT new Step 0). Codified as TPHD-1 in `methodology-changelog.md` v0.32.0 with -D suffix calibration-trail convention N=4 → N=5 stable. Canonical phrase `TF-1 plan harmonization discipline` pinned across N=3 surfaces per slice-013 EPGD-1 + slice-014 PMI-1 v1.1 + slice-015 SCPD-1 + slice-016 RPCD-1 N-surface schema-pin precedent N=5 → N=6 instances stable: (1) `skills/critique/SKILL.md` Step 4 prose + `skills/critique-review/SKILL.md` Step 3 prose + `skills/build-slice/SKILL.md` Step 0 prose, (2) in-repo `methodology-changelog.md` v0.32.0 entry, (3) installed `~/.claude/methodology-changelog.md` v0.32.0 entry.

Three sub-modes named distinctly with concrete miss citations:
- **Sub-mode (a) /critique post-fix-prose harmonization**: when applying ACCEPTED-FIXED Builder draft edits at /critique Step 4 that change test function names or AC #N row references in mission-brief.md or design.md, harmonize the mission-brief TF-1 plan section in the SAME fix block.
- **Sub-mode (b) /critique-review post-fix-prose harmonization**: when meta-Critic ACCEPTED-FIXED findings will result in fix-prose during /critique Step 4.5 TRI-1 triage that changes test function names or AC #N row references, harmonize the mission-brief TF-1 plan section in the same fix block.
- **Sub-mode (c) /build-slice Prerequisite-check pre-flight harmonization** (per /critique M2 ACCEPTED-FIXED: placement is a NEW bullet INTO existing `## Prerequisite check` section, NOT a new `### Step 0`): BEFORE Step 1 plan-mode entry, scan the mission-brief TF-1 plan table; for each row, verify Test path exists or will be created at the right path AND Test function name will match what gets built. Flag drift to user for fix BEFORE plan-mode approval. Closes the function-name-staleness audit gap that `tools/test_first_audit.py --strict-pre-finish` does not detect (status-only check per /critique B1 ACCEPTED-FIXED).

Concrete miss citations grounded in slice-016 evidence:
- AC #3 ADR-pin row test name (`_adr_015_pinned_in_methodology_changelog_v_0_31_0` placeholder; actual built `_exists_and_names_rpcd_1_canonical_phrase`).
- AC #5 shippability placeholder (`_rpcd_1_body_pins_cross_slice_and_substantive_anchors` pre-M-add-1 placeholder).
- All TF-1 rows still in PENDING status at /build-slice Phase 6 audit time.

PMI-1 atomic version bump 0.31.0 → 0.32.0 with versioned-gate retirement-proof (PMI-1 v1.1 version-agnostic gate N=3 → N=4 stable; zero test code modification on gate body per slice-014 + slice-015 + slice-016 precedent).

Recursive-self-application: slice-017 IS a cross-cutting tooling slice modifying `skills/critique/SKILL.md` + `skills/critique-review/SKILL.md` + `skills/build-slice/SKILL.md` + `methodology-changelog.md` — exactly the in-house methodology surfaces MCT-1 (slice-010 ADR-009) covers. `critic-required: true` set at /slice time per MCT-1 default trigger N=6 → N=7 stable. Under both the OLD heuristic (RSAD-1 codified at slice-011) AND the NEW TPHD-1 heuristic this slice encodes, slice-017's own design + mission-brief + ADR-016 are expected to exhibit recursive-self-application defects at /critique. Per slice-016 lesson "codification slices that codify a discipline almost always commit instances of that discipline on their own draft. Strong prior. Recursive-self-application N=7 → N=8 cumulative post-RSAD-1 codification at slice-016." Slice-017 expected ratchet: N=8 → N=9.

## Consequences

**Immediate** (slice-017 ship):

- `skills/critique/SKILL.md` Step 4 gains TPHD-1 prose paragraph between L122 (Step 4 close) and L124 (Step 4.5 header).
- `skills/critique-review/SKILL.md` Step 3 gains TPHD-1 prose paragraph between L83 (Step 3 close) and L85 (Step 4 header).
- `skills/build-slice/SKILL.md` gains NEW bullet INTO existing `## Prerequisite check` section (L17-L22), between L22 (last existing bullet) and `## Your task` L24 — per /critique M2 ACCEPTED-FIXED placement refinement.
- `methodology-changelog.md` v0.32.0 entry appended (in-repo + installed) with TPHD-1 rule reference + three-sub-mode naming + Limitations note + RPCD-1-self-application probe + EPGD-1-self-application N=4→N=5 confirmation.
- `tests/methodology/test_critique_skill.py` NEW with 2 prose-pin tests per Wiegers regression-guard coverage symmetry (substring-pin + location-pin).
- `tests/methodology/test_critique_review_skill.py` NEW with 2 prose-pin tests.
- `tests/methodology/test_build_slice_skill.py` gains 2 prose-pin tests appended.
- `tests/methodology/test_methodology_changelog.py` gains 1 NEW SECTION header + 3 entry-pin tests (`_v_0_32_0_tphd_1_entry_present_in_repo_and_installed` + `_v_0_32_0_tphd_1_entry_names_three_sub_modes_in_repo_and_installed` + `_v_0_32_0_tphd_1_entry_names_slice_016_cross_slice_anchor`) + 1 ADR-pin test (`_adr_016_exists_and_names_tphd_1_canonical_phrase`).
- `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.31.0 → 0.32.0 atomically.
- `architecture/shippability.md` row 17 added enumerating TPHD-1 critical-path tests; rows 1-16 NOT touched (no Dim 9 sub-clause supersession this slice; `_lists_nine_sub_clauses` stays valid).
- `agents/critique.md` NOT touched (CAD-1 byte-equality preserved at slice-016 ship hash `f34c967eaaa34413...`; bidirectional sha256 forensic capture N=12 → N=13 stable expected).

**Downstream** (slice-018 and beyond):

- Every /critique invocation that applies ACCEPTED-FIXED Builder draft edits changing test function names automatically harmonizes the mission-brief TF-1 plan in the same fix block per TPHD-1 sub-mode (a) prose at Step 4 (read by Claude main thread at /critique time).
- Every /critique-review invocation that surfaces meta-Critic ACCEPTED-FIXED findings affecting test function names triggers TPHD-1 sub-mode (b) harmonization during /critique Step 4.5 TRI-1.
- Every /build-slice invocation performs Prerequisite-check pre-flight TF-1 plan harmonization (new bullet in `## Prerequisite check`) BEFORE Step 1 plan-mode entry, surfacing drift to user for fix-block synchronization.
- The slice-016 staleness pattern (3 stale function names + all-rows-PENDING-status surfacing at Phase 6 audit) projected to NOT recur at slice-018+ if TPHD-1 prose is read + applied by Claude main thread at all three insertion points.
- Drift detection at v1: prose-pin tests (substring + location-pin per surface = 6 tests) catch SKILL.md drift; v2 candidate `tools/tphd_1_audit.py` walks mission-brief TF-1 plan + actual test files programmatically (deferred at codification time; promote at N≥3 violations post-codification).

**Cumulative-Critic-influence note**: TPHD-1 is applied prospectively — slice-018 onward (the FIRST slice to benefit from TPHD-1 from /design-slice through /build-slice). Slice-017 IS the canonical reference instance of TPHD-1 codification (slice-017 codifies the rule AND must self-apply it AT /critique fix-prose + /critique-review fix-prose + /build-slice Step 0 on its own draft — strict canonical-reference-instance N=1 standalone post-codification, expected to ratchet to N=2 stable at slice-018+).

**3-layer Critic-stack accountability lineage**: pre-TPHD-1, the lineage at N=2 cumulative (slice-014 N=1 + slice-016 N=2) was uncodified. Post-TPHD-1, the lineage is reduced to 2 layers (first-Critic + meta-Critic) with Phase 0 acting as defensive pre-flight rather than third-layer-Critic-stack-detection. The Critic-stack reverts to 2-layer accountability where staleness should not surface at /build-slice Phase 6 (because TPHD-1 sub-modes (a)/(b)/(c) preempt it at /critique + /critique-review + /build-slice Step 0).

## Reversibility

**Reversibility: cheap** with magnitude justification (per slice-009 ADR-008 + slice-010 ADR-009 + slice-013 ADR-012 + slice-014 ADR-013 + slice-015 ADR-014 + slice-016 ADR-015 cheap-with-magnitude-justification convention N=5 → N=6 stable).

**Magnitude estimate** (~13-16 sites total):
1. `skills/critique/SKILL.md` — Step 4 prose paragraph insert (1 site, ~5 lines)
2. `skills/critique-review/SKILL.md` — Step 3 prose paragraph insert (1 site, ~3 lines)
3. `skills/build-slice/SKILL.md` — NEW bullet INTO existing `## Prerequisite check` section (1 site, ~5-7 lines per /critique M2 ACCEPTED-FIXED placement refinement)
4. `methodology-changelog.md` — v0.32.0 entry insert at file top (1 site, ~80-100 lines)
5. `~/.claude/methodology-changelog.md` — forward-sync mirror (1 site)
6. `VERSION` — bump 0.31.0 → 0.32.0 (1 site)
7. `~/.claude/ai-sdlc-VERSION` — forward-sync mirror (1 site)
8. `plugin.yaml.version` — bump 0.31.0 → 0.32.0 (1 site)
9. `tests/methodology/test_critique_skill.py` — NEW file (2 functions, ~30-40 lines)
10. `tests/methodology/test_critique_review_skill.py` — NEW file (2 functions, ~30-40 lines)
11. `tests/methodology/test_build_slice_skill.py` — append 2 functions (1 site, ~15-20 lines)
12. `tests/methodology/test_methodology_changelog.py` — append NEW SECTION header + 3 entry-pin tests + 1 ADR-pin test (1 site, ~30-40 lines)
13. `architecture/shippability.md` — append row 17 (1 site, multi-line pytest command)
14. `architecture/decisions/ADR-016-*.md` — this file itself (1 site, ~250-350 lines)

**Comparison to prior ADRs**:
- ADR-009 (MCT-1, slice-010) — **cheap** with magnitude justification. ~11-13 sites. Skill-prose-discipline at 1 surface (skills/slice/SKILL.md Step 4a) + bullet + evidence-paragraph split + 2 new test files. TPHD-1 closest sibling in pattern.
- ADR-010 (RSAD-1, slice-011) — **cheap** with magnitude justification. ~12 sites. Skill-prose-discipline at 1 surface (agents/critique.md Dim 9 sub-clause).
- ADR-012 (EPGD-1, slice-013) — **cheap** with magnitude justification. ~12 sites.
- ADR-014 (SCPD-1, slice-015) — **cheap** with magnitude justification. ~13-15 sites.
- ADR-015 (RPCD-1, slice-016) — **cheap** with magnitude justification. ~13-15 sites.
- **ADR-016 (this) — cheap with magnitude justification**. ~13-16 sites; same class as ADR-014/015 (~13-15 sites) at slightly larger surface area due to 3-surface skill-prose insertion (vs 1-surface for MCT-1/RSAD-1/SCPD-1/RPCD-1). Still cheap on reversibility because each site is small + isolated + revert path is well-trodden (git diff + superseding changelog entry).

**Revert path**:
1. Git diff revert of slice-017's commits (single-slice revert clean).
2. Append a superseding methodology-changelog entry retracting TPHD-1 (e.g., `## v0.33.0 — <date>` with `### Retired` section naming TPHD-1 + retirement rationale).
3. Remove the 6 new prose-pin test functions + delete the 2 new test files (`test_critique_skill.py` + `test_critique_review_skill.py`) + remove 4 new entry-pin/ADR-pin tests from `test_methodology_changelog.py`.
4. Forward-sync the reverted `methodology-changelog.md` to `~/.claude/`. Confirm byte-equality.
5. Atomic version bump (post-retirement bump 0.32.0 → 0.33.0 or whatever VERSION ends up at).

**Irreversible portion** (minor, append-only):
- The `methodology-changelog.md` v0.32.0 entry itself becomes part of the append-only changelog history. Retraction is a SUPERSEDING entry per slice-007/008/009/010/011/012/013/014/015/016 PMI-1 + changelog inclusion heuristic precedent, NOT a deletion.
- Cumulative slice-018-N harmonization edits applied under TPHD-1 are part of the project's empirical record.

Both irreversible portions are documentation-record-class (not functional-behavior-class). Neither prevents revert.

**Conclusion**: Reversibility is **cheap**. Magnitude is ~13-16 sites (same class as ADR-014/015/016 RPCD-1/SCPD-1 codification slices). Revert path is well-trodden. Adopt Option 1 (3-surface skill-prose discipline at /critique + /critique-review + /build-slice).
