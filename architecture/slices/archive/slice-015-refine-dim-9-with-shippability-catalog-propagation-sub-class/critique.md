# Critique: Slice 015 refine-dim-9-with-shippability-catalog-propagation-sub-class

**Critic reviewed**: mission-brief.md, design.md, ADR-014, milestone.md
**Date**: 2026-05-13
**Result**: NEEDS-FIXES

## Summary

Design is structurally sound (SCPD-1 codification follows slice-013 EPGD-1 precedent cleanly; rule-ID locked SCPD-1 consistently across mission-brief / design.md / ADR-014 / milestone.md — no slice-013 B1-class rule-ID drift recurrence; 7 pre-AC-lock empirical audits documented). However, the slice's design.md has TWO concrete defects that mirror slice-013 + slice-014 critique catches and would block /build-slice if unaddressed: (B1) the design.md `Substantive-discipline anchors (≥2 of 4)` list contains 3 of 4 phrases that do NOT actually appear as literal substrings in the canonical 8th sub-clause body (`shippability catalog`, `consumer reference`, `rename propagation` — body uses hyphenated forms `shippability-catalog`, `consumer-reference`, and never uses `rename propagation` literal); the `_cites_at_least_two_cross_slice_anchors` AC #2 test will FAIL at /build-slice with only 1 of 4 anchors matching, regardless of how the test is implemented from the design spec. (M1) Slice-015's design.md plans no end_anchor tightening on slice-013's three existing body-bound tests (`_names_both_sub_modes` + `_paragraph_cites_slice_011_and_012` + `_cites_at_least_two_cross_slice_anchors` at test_critique_agent.py:312/347/387 all using `end_anchor = "### Bonus: weak graph edges"`) — exactly the M1 + M-add-1 precision-degradation pattern slice-013 caught and tightened.

Two Majors: (M2) Mission-brief AC #2 doesn't formalize the strict-both / ≥k-of-n anchor list semantics — slice-013 M2 class recurrence at mission-brief layer (design.md has the formalization but it didn't propagate up to AC). (M3) Canonical 8th sub-clause body says "SAME Phase as the supersession Edit" (design.md L122-126 final paragraph + body L124) but slice-015's own Phase plan supersedes at Phase 1f and propagates at Phase 5 — not the same numbered Phase. Slice-014 also did Phase 1c supersession + Phase 4 propagation. The discipline prose is empirically falsified by both N=1 + N=2 reference instances — tooling-doc-vs-impl-parity (Dim 1) issue with the rule being codified at the moment of codification.

Two Minors: cosmetic.

Recursive-self-application (Dim 9 sub-clause 6, RSAD-1) N=7 cumulative confirmed: the slice authoring SCPD-1 has its own draft showing the EXACT class of defects SCPD-1's sibling disciplines (M1/M-add-1 body-bound widening; M2 anchor-list under-specification; CCC-1 v1.1 doc-vs-impl parity) were codified to catch. Strongest single instance is B1 because it would silently fail at build time.

## Findings

### Blockers (must address before /build-slice)

#### B1: Substantive-discipline anchor list (≥2 of 4) under-tested against canonical body — 3 of 4 literal substrings absent

- **Claim under review** (design.md L10): "**Substantive-discipline anchors (≥2 of 4)**: `[\"Phase 5\", \"shippability catalog\", \"consumer reference\", \"rename propagation\"]` — at least 2 of these 4 MUST be present in the 8th sub-clause body (or scoped equivalents — design-slice locks; final list may be tightened at /critique per slice-013 Critic M2 precedent)"
- **Claim under review** (mission-brief.md TF-1 row 6, line 39): "test_critique_dim_9_shippability_catalog_propagation_cites_at_least_two_cross_slice_anchors | PENDING"
- **Issue**: Empirical substring verification against the canonical 8th sub-clause body (design.md L122-126) shows only 1 of 4 anchors will match as literal substrings:
  - `"Phase 5"` — YES (body L123: `Phase 5 (shippability.md updates) does NOT scan`)
  - `"shippability catalog"` (space) — NO. Body uses hyphenated `"shippability-catalog"` in title (L122) and `"shippability.md"` elsewhere. No literal `"shippability catalog"` (with space) substring exists.
  - `"consumer reference"` (space) — NO. Body uses hyphenated `"consumer-reference"` in title (L122). No literal `"consumer reference"` (with space) substring exists.
  - `"rename propagation"` — NO. Body uses `"the rename across all consumer rows"` (L124) and `"shippability.md propagation Phase"` (L125), but no literal `"rename propagation"` substring.

  At /build-slice Phase 1f, when the `_cites_at_least_two_cross_slice_anchors` test is implemented per the design.md spec, it will assert `sub_count >= 2` against this 4-element list and FAIL with `sub_count == 1`. This is the slice-013 M2-class anchor-list-under-specification defect ratcheted to Blocker because the design.md anchor list is locked but doesn't match the canonical body it's supposed to anchor.
- **Evidence**: design.md L8-10 (anchor lists); design.md L122-126 (canonical body); slice-013 critique M2 + slice-013 reflection.md L36 (M2 ratified VALIDATED, anchor list formalization saves /build-slice author from drift). Empirical: count of `"shippability catalog"` (with space) in design.md L122-126 = 0; count of `"consumer reference"` (with space) = 0; count of `"rename propagation"` = 0.
- **Proposed fix**: At /critique disposition, revise design.md L10 substantive-discipline anchor tuple to use literal substrings that DO appear in the canonical body:
  ```
  Substantive-discipline anchors (≥2 of 4): ["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]
  ```
  Each of these 4 literals empirically appears in the canonical 8th sub-clause body (design.md L122-126):
  - `"Phase 5"` — L123, L125
  - `"shippability.md"` — L122, L124, L125, L126
  - `"/validate-slice Step 5.5"` — L124, L126 (slice-013 reactive anchor)
  - `"supersession"` — L122 ("PMI-1 structural-invariant supersession", "rename-driven supersession discipline")

  Propagate revised list to (a) mission-brief AC #2 + verification plan row 2, (b) the test function body for `_cites_at_least_two_cross_slice_anchors` per the slice-013 `_cites_at_least_two_cross_slice_anchors` precedent (TF-1 PENDING → WRITTEN-FAILING genuineness depends on the assertion matching the canonical body it pins). Alternatively, EDIT the canonical body to use the literal phrases (`"shippability catalog"`, `"consumer reference"`, `"rename propagation"`) — but this churns the body prose; cheaper to revise the anchor tuple.
- **Builder draft**: ACCEPTED-FIXED — revise design.md L10 substantive-discipline anchor tuple to `["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]` (empirically verified against canonical body — all 4 appear; ≥2-of-4 will robustly PASS). Propagate to mission-brief.md AC #2 (folded with M2). RSAD-1 (Dim 9 sub-clause 6) design-time mode catch — exactly the class the discipline was codified for. **N=7 recursive-self-application instance confirmed empirically.**

### Majors (address this slice)

#### M1: Slice-013's 3 body-bound tests precision-degrades when 8th sub-clause inserted between 7th sub-clause and `### Bonus: weak graph edges` — exact slice-013 M1 + M-add-1 recurrence

- **Claim under review** (design.md L35): "tests/methodology/test_critique_agent.py — existing 25+ tests from slice-006..013 (the structural-invariant `_lists_seven_sub_clauses` + location-pin + canonical-substring + cross-slice anchors). Slice-015 supersedes `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`; adds 5 new tests; deletes 0; existing tests preserved per backward-compat covenant per slice-011 + slice-012 + slice-013 Critic findings B1 class"
- **Issue**: Three slice-013 tests in test_critique_agent.py use body-bound start_anchor/end_anchor pairs anchored on `### Bonus: weak graph edges`:
  - `test_critique_dim_9_entry_pin_vs_pmi_1_gate_names_both_sub_modes` (L312-344, `end_anchor = "### Bonus: weak graph edges"`)
  - `test_critique_dim_9_entry_pin_pmi_1_paragraph_cites_slice_011_and_012` (L347-384, same end_anchor)
  - `test_critique_dim_9_entry_pin_vs_pmi_1_gate_cites_at_least_two_cross_slice_anchors` (L387-433, same end_anchor)

  Slice-015 design.md L8 explicitly plans to insert the new 8th sub-clause body BETWEEN the 7th sub-clause close and `### Bonus: weak graph edges` H3. After insertion, each of these 3 tests' `body = CRITIQUE[start_idx:end_idx]` widens to include the new 8th sub-clause body — exactly the slice-013 M1 + M-add-1 defect class. Slice-013's caught-symmetry: when slice-013 appended the 7th sub-clause, slice-011's `_names_both_sub_modes` + `_cites_at_least_two_cross_slice_anchors` body bounds widened similarly; slice-013 M1 + M-add-1 explicitly tightened the end_anchor on those slice-011 tests to `"Entry-pin-vs-PMI-1-gate semantics conflation"` (the new 7th sub-clause title). Slice-015 is the structural-analog operation on slice-013's 3 tests.

  The widening is **latent precision-degradation** (not immediate correctness regression): the new 8th sub-clause body in design.md L122-126 happens not to contain `"Build-time slip mode"`, `"Design-time-pre-empted success mode"`, `"slice-011"`, `"slice-012"`, `"Phase 1b INSERT"`, `"Phase 1c narrow-scope Edit"`, `"Audit 6 structural-separation"`, or `"SECTION header"` — so slice-013 tests' assertions don't accidentally pass on 8th sub-clause content. BUT any future drift that moves these substrings out of 7th sub-clause and into 8th sub-clause body would silently leave slice-013 tests passing. Slice-013 M1 + M-add-1 reflection explicitly flagged this regression-guard-precision class as a Major finding.
- **Evidence**: tests/methodology/test_critique_agent.py:312-344 (slice-013 `_names_both_sub_modes`), L347-384 (`_paragraph_cites_slice_011_and_012`), L387-433 (`_cites_at_least_two_cross_slice_anchors`); slice-013 critique.md L33-39 + slice-013 reflection.md L38; design.md L122-126.
- **Proposed fix**: At /build-slice Phase 1f, tighten end_anchor on all 3 slice-013 tests from `### Bonus: weak graph edges` to `Shippability-catalog consumer-reference propagation` (the new 8th sub-clause title). Add to TF-1 plan as 3 new WRITTEN-AS-EDIT rows (one per test); mid-slice smoke verifies all 3 transitions. The 3 slice-015 NEW body-bound tests use `end_anchor = "### Bonus: weak graph edges"` (correct shape) since slice-015 is the LAST sub-clause at this slice's ship — until slice-NNN+1 appends a 9th sub-clause. This is canonical methodology recurrence: EVERY future Dim 9 sub-clause append will need to tighten its predecessor's end_anchors. Generic methodology lesson candidate ratcheted from slice-013 reflection.md "having-found-a-body-bound-widening-defect-grep-for-siblings" N=1 → **N=2 stable at slice-015** if applied.
- **Builder draft**: ACCEPTED-PENDING — apply at /build-slice Phase 1f. TF-1 plan grows 10 → 13 rows (3 new WRITTEN-AS-EDIT rows for tightening slice-013 tests' end_anchors). Mid-slice smoke gate verifies all 3 transitions. Also add to mission-brief.md must-not-defer list as a structural invariant: "Slice-013 body-bound tests' end_anchors tightened from `### Bonus: weak graph edges` to `Shippability-catalog consumer-reference propagation`".

#### M2: Mission-brief AC #2 doesn't formalize the strict-both / ≥k-of-n anchor list semantics — slice-013 M2 class recurrence at mission-brief layer

- **Claim under review** (mission-brief.md L18, AC #2): "Both sub-modes pinned via dedicated prose-pin tests with slice-013 + slice-014 anchors (mirrors slice-011 RSAD-1 `_names_both_sub_modes` + `_cites_at_least_two_cross_slice_anchors` test shape and slice-013 EPGD-1 sub-mode + slice-anchor pin shape)."
- **Issue**: Mission-brief AC #2 names "slice-013 + slice-014 anchors" but doesn't formalize:
  - The strict-both cross-slice anchor tuple `["slice-013", "slice-014"]`
  - The ≥2-of-4 substantive-discipline anchor tuple (which itself is broken per B1)

  Slice-013 critique M2 explicitly caught this class on slice-013's own mission-brief: AC #2 said "asserts canonical substrings `slice-011`, `slice-012`, AND substantive discipline anchors (per /design-slice choice) all present" with the "per /design-slice choice" phrase being the under-specification trigger. Slice-013 design.md formalized; slice-013 critique M2 propagated the formalization back up to slice-013 mission-brief AC. Slice-015 design.md L8-10 DID formalize; slice-015 mission-brief AC #2 did NOT. The propagation step slice-013 M2 ratified is missing.

  This is recursive-self-application (Dim 9 sub-clause 6, RSAD-1) N=7 — the slice authoring SCPD-1 has its own mission-brief committing the exact specification-defect class slice-013 M2 was codified to mitigate.
- **Evidence**: mission-brief.md L18 (AC #2 lacks strict-both / ≥2-of-4 semantics); design.md L8-10 (formalized but not back-propagated); slice-013 critique.md L40-51 + M2 ACCEPTED-FIXED; slice-013 reflection.md L36.
- **Proposed fix**: Update mission-brief.md AC #2 (line 18) — add the formalized anchor lists from design.md L8-10 directly (with B1 revision applied):
  ```
  2. The new 8th sub-clause body names BOTH sub-modes ... Both sub-modes pinned via dedicated prose-pin tests with formalized anchor lists:
     - Cross-slice anchors (strict-both): ["slice-013", "slice-014"]
     - Substantive-discipline anchors (≥2 of 4): ["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]
  ```
- **Builder draft**: ACCEPTED-FIXED — folded into B1's revision; apply both as single mission-brief.md edit.

#### M3: 8th sub-clause canonical body L122-126 says "SAME Phase as the supersession Edit" — but slice-014 reference instance + slice-015 own Phase plan both do supersession + propagation in DIFFERENT numbered Phases — discipline-prose-vs-empirical-practice drift

- **Claim under review** (design.md L122-124, canonical 8th sub-clause body): "downstream consumers of that test function name in `architecture/shippability.md` (the catalog of critical-path commands run at /validate-slice pre-finish) carry stale references unless the SAME Phase explicitly propagates the rename across all consumer rows." + L124 "...updates each row's pytest command in the SAME Phase as the supersession Edit, BEFORE running the shippability catalog at /validate-slice."
- **Issue**: "SAME Phase as the supersession Edit" is empirically falsified by the N=2 evidence base the rule cites:
  - **Slice-014 N=2 proactive reference instance**: per slice-014 reflection.md L16 + the design.md L122-126 body itself: slice-014 did this at Phase 4 (full methodology suite phase, before /validate-slice), but the supersession Edit happened at Phase 1c. Phase 1c ≠ Phase 4.
  - **Slice-015 own Phase plan**: Phase 1f supersedes `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses` (design.md L139); Phase 5 propagates rows 6 + 11 + 13 (design.md L143). Phase 1f ≠ Phase 5.

  The rule prose says "SAME Phase" but the canonical reference instances do it in different numbered Phases. The operational meaning that holds across both reference instances is "BEFORE running the shippability catalog at /validate-slice" (in the same /build-slice block, BEFORE the catalog run). This is the slice-013/014 generic methodology lesson actually being encoded. The wording "SAME Phase" is misleading — it would lead future Critic readers + Builders to expect Phase 1f propagation, which doesn't match the empirical reference instances.

  This is a Dim 1 / Dim 9 sub-clause 2 tooling-doc-vs-impl-parity defect (the rule's documentation drifts from its actual implementation/empirical practice) — at the moment of codifying the rule. The slice authoring SCPD-1 has its own canonical body committing the exact class of doc-vs-impl drift CCC-1 v1.1 was codified to catch.
- **Evidence**: design.md L122-126 (rule prose "SAME Phase"); slice-014 reflection.md L16 + design.md Phase plan L143 (slice-015 own Phase plan — supersession at Phase 1f, propagation at Phase 5).
- **Proposed fix**: Revise the 8th sub-clause canonical body (design.md L122-126) to use empirically-accurate phrasing. Replace "the SAME Phase explicitly propagates the rename across all consumer rows" + "updates each row's pytest command in the SAME Phase as the supersession Edit, BEFORE running the shippability catalog at /validate-slice" with:

  > "...the same /build-slice block (before /validate-slice catalog run) explicitly propagates the rename across all consumer rows" + "updates each row's pytest command in the same /build-slice block as the supersession Edit and BEFORE running the shippability catalog at /validate-slice".

  The phrase "the same /build-slice block" preserves the discipline (no deferral to /validate-slice reactive time) without falsely implying same-numbered-Phase requirement.
- **Builder draft**: ACCEPTED-FIXED — revise canonical body wording in design.md "Sub-clause canonical body" section (L122-126). Propagate the revised phrasing to methodology-changelog v0.30.0 entry body at /build-slice Phase 1e (entry text reproduces canonical body literally per slice-013 v0.28.0 precedent).

### Minors (log; address if cheap)

#### m1: Mission-brief AC #3 N-surface count says "N=3 surfaces" — pre-finish gate should verify with explicit grep

- **Claim under review** (mission-brief.md L20): "substantive canonical phrase `Shippability-catalog consumer-reference propagation` pinned across N=3 surfaces per slice-013 EPGD-1 3-surface precedent (agents/critique.md 8th sub-clause title + in-repo entry + installed entry)"
- **Issue**: Structurally correct (3-surface shape mirrors slice-013 EPGD-1 precedent N=2 → N=3 instances stable). Cheap to add explicit post-Phase-5 verification.
- **Evidence**: mission-brief.md L20; design.md L21, L168-170.
- **Proposed fix**: Add to pre-finish gate a post-Phase-5 grep `grep -rn "Shippability-catalog consumer-reference propagation"` across `agents/critique.md` + `methodology-changelog.md` + `~/.claude/agents/critique.md` + `~/.claude/methodology-changelog.md` — expected: ≥4 hits (in-repo critique sub-clause title + installed critique sub-clause title + in-repo changelog v0.30.0 entry + installed changelog v0.30.0 entry).
- **Builder draft**: ACCEPTED-PENDING — add explicit grep verification to pre-finish gate in mission-brief.md.

#### M-add-1: `WRITTEN-AS-EDIT` status (introduced by M1 disposition) is not in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist — added by /critique-review meta-Critic per DR-1 N=3 stable

- **Source**: critique-review.md "Missed findings" section — meta-Critic empirically verified by running `tools.test_first_audit --strict-pre-finish` against post-disposition mission-brief; got 11 Important violations (3 × `invalid-status` for rows 41/42/43 + 8 × expected-PENDING for rows 38-49).
- **Issue**: `tools/test_first_audit.py` L65 `_ALLOWED_STATUSES: frozenset[str] = frozenset({"PENDING", "WRITTEN-FAILING", "PASSING"})`. M1 disposition introduced a new `WRITTEN-AS-EDIT` status string not in the allowlist. /build-slice Phase 6 strict-pre-finish would halt; slice unshipable as-was.
- **Severity**: Major (would block /build-slice completion; cheap fix).
- **Proposed fix**: Per meta-Critic Option (b) recommendation: flip 3 `WRITTEN-AS-EDIT` rows to `PASSING` (matching slice-013 precedent — existing tests stay PASSING; end_anchor tightening tracked in must-not-defer at mission-brief.md L70-71, already present per M1). Also update stale pre-finish gate count "10/10" → "13/13".
- **Builder draft**: ACCEPTED-FIXED — empirically applied + re-verified `tools.test_first_audit` clean (13 rows, 5 PASSING + 8 PENDING expected pre-build).

**Calibration observation (per /critique-review notes)**: DR-1 N=3 stable runtime-prerequisite-completeness pattern across slices 013/014/015 — first Critic catches design-semantic defect AND structurally sound fix; fix introduces a new runtime-prerequisite gap because surrounding tooling/context not symmetrically audited. Strong candidate for /critic-calibrate at slice-016+ if recurs (would justify explicit "audit-tooling-completeness" sub-discipline in Critic prompt).

#### m2: Phase 5 step-ordering text (design.md L143) — minor traceability gap on row 13 carrying both `_invariant` (slice-014) AND `_lists_seven_sub_clauses` (slice-013)

- **Claim under review** (design.md L143): "Phase 5 explicit step ordering: (a) scan with `grep -n "_lists_seven_sub_clauses" architecture/shippability.md` — expected: 3 hits at rows 6 + 11 + 13 pytest commands; (b) edit each row's pytest command in-line; (c) re-scan with same grep — expected: 0 hits; (d) THEN append row 15."
- **Issue**: Row 13 pytest command carries TWO test references — `_invariant` (slice-014's update) AND `_lists_seven_sub_clauses` (from slice-013). Cheap to note explicitly in Phase 5 step (b) ordering so the Builder doesn't accidentally replace `_invariant` too.
- **Evidence**: shippability.md row 13 (line 21) pytest command shows both references; slice-014 reflection.md L90.
- **Proposed fix**: Add a one-sentence note to design.md L143 step (b): "Row 13 already carries `_invariant` from slice-014 Phase 4 propagation; slice-015 Phase 5 step (b) updates ONLY the structural-invariant test ref on row 13 from `_lists_seven_sub_clauses` → `_lists_eight_sub_clauses`, preserving `_invariant`."
- **Builder draft**: ACCEPTED-FIXED — cosmetic clarification.

## Dimensions checked

- [x] **Unfounded assumptions** — finding B1 (substantive-discipline anchor list claims body presence but empirical substring count is 1 of 4). Audit 4's grep-3-hits claim verified empirically; Audit 6's EPGD-1 N/A claim verified by reading test_methodology_changelog.py.
- [x] **Missing edge cases** — finding M1 (precision-degradation of slice-013 body-bound tests — Hendrickson body-bound discipline class slice-013 codified at M1 + M-add-1; canonical recurrence). No other edge cases.
- [x] **Over-engineering** — none. Slice is minimal append-new; reversibility cheap.
- [x] **Under-engineering** — findings B1 (≥2-of-4 substantive anchor list under-fits canonical body) + M1 (TF-1 plan should add 3 end_anchor tightening rows) + M2 (mission-brief AC #2 anchor-list under-specification).
- [x] **Contract gaps** — none. No new endpoints, events, or external integrations.
- [x] **Security** — none. Slice modifies prose content in canonical methodology files; no runtime authorization paths.
- [x] **Drift from vault** — none. ADR-014 supersedes: null; rule-ID `SCPD-1` locked consistently; canonical inventories surfaces verified.
- [x] **Web-known issues** — skipped (methodology prose slice; no external technology/API/platform dependency).
- [x] **Cross-cutting conformance** — findings M1 (body-bound widening — Dim 9 sub-clause 7+ structural recurrence per slice-013 M1+M-add-1), M3 (doc-vs-impl parity — Dim 9 sub-clause 2 / Dim 1 recurrence at codification moment), B1 + M2 (RSAD-1 recursive-self-application N=7 — 4 distinct sub-class hits on slice's own draft, strongest recursive-self-application finding count post-slice-013).

## Triage

**Triaged by**: user
**Date**: 2026-05-13
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md L10 substantive-discipline tuple revised to `["Phase 5", "shippability.md", "/validate-slice Step 5.5", "supersession"]` — all 4 empirically appear in canonical body L122-126; propagated to mission-brief AC #2 (folded with M2) |
| M1 | Major | ACCEPTED-PENDING | At /build-slice Phase 1f, tighten end_anchor from `"### Bonus: weak graph edges"` to `"Shippability-catalog consumer-reference propagation"` on slice-013's 3 body-bound tests (`_names_both_sub_modes` + `_paragraph_cites_slice_011_and_012` + `_cites_at_least_two_cross_slice_anchors`). TF-1 plan grew 10 → 13 rows; mission-brief.md must-not-defer list adds this as canonical methodology recurrence (every future Dim 9 sub-clause append must apply the same end_anchor-tightening discipline to its predecessor's body-bound tests) |
| M2 | Major | ACCEPTED-FIXED | mission-brief.md AC #2 updated with formalized anchor lists (strict-both `["slice-013", "slice-014"]` + ≥2-of-4 substantive-discipline anchors from B1 revision); slice-013 M2 mitigation precedent applied — N=1 → N=2 stable at slice-015 |
| M3 | Major | ACCEPTED-FIXED | design.md "Sub-clause canonical body" L122-126 revised: "the SAME Phase" → "the same /build-slice block (before /validate-slice catalog run)"; "the SAME Phase as the supersession Edit" → "the same /build-slice block as the supersession Edit and BEFORE the /validate-slice catalog run"; revised body to be propagated literally to methodology-changelog v0.30.0 entry at /build-slice Phase 1e per slice-013 v0.28.0 precedent |
| m1 | Minor | ACCEPTED-PENDING | mission-brief.md must-not-defer list adds explicit post-Phase-5 grep verification: `grep -rn "Shippability-catalog consumer-reference propagation"` across in-repo + installed `agents/critique.md` + `methodology-changelog.md` returns ≥4 hits |
| m2 | Minor | ACCEPTED-FIXED | design.md Phase 5 step (b) clarified — row 13 carries TWO test references (`_invariant` from slice-014 + `_lists_seven_sub_clauses` from slice-013); slice-015 Phase 5 step (b) updates ONLY the structural-invariant ref on row 13 while preserving `_invariant` |
| M-add-1 | Major | ACCEPTED-FIXED | **/critique-review meta-Critic catch (DR-1 N=3 stable runtime-prerequisite-completeness pattern)** — `WRITTEN-AS-EDIT` status string introduced by M1 disposition is not in `tools/test_first_audit.py`'s `_ALLOWED_STATUSES` allowlist; would cause /build-slice Phase 6 pre-finish gate to FAIL with 11 violations (3 invalid-status + 8 expected-PENDING). Meta-Critic empirically verified by running `tools.test_first_audit --strict-pre-finish`. Fix per meta-Critic option (b): flip the 3 end_anchor-tightening rows in TF-1 plan from `WRITTEN-AS-EDIT` to `PASSING` (matching slice-013 precedent of keeping pre-existing tests at PASSING and tracking end_anchor tightening in must-not-defer prose, which mission-brief already does at L70-71 per M1 disposition). ALSO: pre-finish gate L130 updated from stale "10/10" to "13/13" (post-disposition row count). Empirically re-verified post-fix: `tools.test_first_audit` returns "clean. 13 row(s) → PASSING=5, WRITTEN-FAILING=0, PENDING=8." Pattern N=3 stable post-slice-013/014 DR-1 codification — strong candidate for /critic-calibrate aggregation at slice-016+ proposing explicit "audit-tooling-completeness" sub-discipline addition to Critic prompt |
