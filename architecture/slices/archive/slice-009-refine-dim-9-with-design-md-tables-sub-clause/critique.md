# Critique: Slice 009 refine-dim-9-with-design-md-tables-sub-clause

**Critic reviewed**: mission-brief.md, design.md, ADR-008
**Date**: 2026-05-11
**Result**: NEEDS-FIXES

## Summary

Design is structurally sound — the refinement-not-new-sub-clause framing preserves the 5-sub-clause invariant, the N=2 promotion threshold is met, and self-application BC-1 confirms negative anchors silence cleanly. However, two factual errors (existing-test count claimed as 11 when actual is 13; mission-brief AC #3 names a non-existent test function) plus one substring-pin location ambiguity (AC #2 substring-only test doesn't anchor paragraph location) plus one meta-conformance error in the design.md prose itself (INST-1 do-not-copy list framing mislocates the canonical inventory surface — slice-009's own design.md commits the very class of design-doc-vs-canonical-inventory drift it's encoding into the Critic prompt) need correction before /build-slice. Plus 3 calibration-discipline findings (M3 missing substantive content anchor for CCC-1 v1.1 changelog pin; M4 reversibility-tag inconsistency; M5 N=2 supersession claim circular) + 4 minor cleanups.

## Findings

### Blockers (must address before /build-slice)

#### B1: Design.md asserts 11 existing tests in `test_critique_agent.py`; actual count is 13

- **Claim under review**: design.md lines 34, 44, 76, 97, 115, 154, 243, 287, 295, 301: "11 existing tests" / "Test count: 11 → 13". Mission-brief.md lines 66, 92, 102, 104, 112, 118 say the same.
- **Issue**: `grep -n '^def test_' tests/methodology/test_critique_agent.py` returns 13 functions (lines 11, 21, 31, 41, 59, 74, 86, 100, 115, 131, 147, 167, 191). The slice-006 methodology-changelog v0.21.0 entry says "extended from 6 → 11 tests" — that was end-of-slice-006 count. The file gained 2 more tests post-slice-006 to reach 13. Design.md's own algorithm-path-conformance table at lines 100-113 correctly enumerates 13 entries, contradicting the body prose claim of 11. Adding 2 new tests at slice-009 brings the total to **15**, not 13. The Phase 1b mid-slice smoke assertion "13 tests collected" (design.md line 287) will FAIL — pytest will collect 15.
- **Evidence**: `tests/methodology/test_critique_agent.py` grep -c returns 13. Design.md algorithm-path-conformance table itself lists 13 rows.
- **Proposed fix**: Replace every "11" with "13" and every "13 tests collected" with "15 tests collected" across design.md (lines 34, 44, 76, 97, 115, 154, 243, 287, 295, 301) and mission-brief.md (lines 66, 92, 102, 104, 112, 118). Algorithm-path-conformance table already lists 13 correctly; no edit needed there.
- **Builder draft**: ACCEPTED-FIXED — applied in this round to mission-brief.md + design.md.

#### B2: Mission-brief AC #3 names a non-existent test function

- **Claim under review**: mission-brief.md TF-1 plan line 33 + verification line 54: `test_in_repo_critique_md_byte_equal_to_installed`.
- **Issue**: This test function does not exist. The actual CAD-1 byte-equality test (slice-007) is named `test_in_repo_and_installed_critique_agent_are_content_equal` at `tests/methodology/test_critique_agent_drift.py:62`. Design.md correctly uses the actual name at lines 53, 64, 92, 199, 208 — but mission-brief.md retains the wrong name. Per slice-002/004/005 lesson "/build-slice strict refusal on non-existent tests", TF-1 audit will refuse with `test-function-missing` if /build-slice reads the mission-brief literally.
- **Evidence**: `tests/methodology/test_critique_agent_drift.py:62` defines `test_in_repo_and_installed_critique_agent_are_content_equal`. No occurrence of `test_in_repo_critique_md_byte_equal_to_installed` in the codebase.
- **Proposed fix**: Update mission-brief.md AC #3 TF-1 row + verification plan to reference `test_in_repo_and_installed_critique_agent_are_content_equal`. Aligns mission-brief with design.md's corrected name.
- **Builder draft**: ACCEPTED-FIXED — applied in this round to mission-brief.md.

### Majors (address this slice)

#### M1: AC #2 substring-only test doesn't pin paragraph location within sub-clause 2

- **Claim under review**: AC #2's test `test_critique_dim_9_design_md_tables_paragraph_cites_slice_006_and_007` asserts 5 example-anchor literals (`slice-006`, `DEVIATION-1`, `DEVIATION-2`, `slice-007`, `ai-sdlc-VERSION`) present anywhere in CRITIQUE.
- **Issue**: Substring-only tests don't enforce location. If Phase 1's edit accidentally interleaves the new sentences anywhere other than strictly after the existing closing example sentence in Dim 9 sub-clause 2 (design.md line 46 specifies "New sentences appended after the existing closing"), the substring tests still pass — masking subtle structural issues (e.g., the new paragraph could end up under a different sub-clause body or in a different dimension entirely). Slice-008 N-surface schema-pin discipline suggests adding a location anchor.
- **Evidence**: design.md lines 9-13 + 46 specify the new sentences and their placement; AC #1 + AC #2 substring tests don't enforce location. Algorithm-path-conformance risk: refinement drift could move the paragraph silently.
- **Proposed fix**: Add a third test `test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph` that asserts the canonical literal `design.md mechanical tables` falls AFTER the substring `Tooling-doc-vs-implementation parity` (sub-clause 2 title) AND BEFORE the substring `Algorithm-path-conformance` (sub-clause 3 title). This anchors the new paragraph's location to sub-clause 2's body. TF-1 plan grows 6 → 7 rows.
- **Builder draft**: ACCEPTED-PENDING — add the third test at /build-slice; TF-1 plan grows to 7 rows.

#### M2: Design's "INST-1 do-not-copy list" framing is technically inaccurate — slice-009 commits the very class of error it's mitigating

- **Claim under review**: design.md line 12 + ADR-008 Context section: "`plugin.yaml` is on INST-1's do-not-copy list".
- **Issue**: INST-1's `_CANONICAL_*` lists in `tools/install_audit.py` (lines 44-67) enumerate POSITIVE inclusion lists (`_CANONICAL_SKILLS`, `_CANONICAL_AGENTS`, `_CANONICAL_TEMPLATES`, `_CANONICAL_METADATA`, `_CANONICAL_TOOLS`) — what IS installed. The NEGATIVE exclusion ("do not copy") list lives in `INSTALL.md` Step 3f, mentioned in `methodology-changelog.md` v0.20.0 line 157: "Step 3f's 'do not copy' list updated to add `plugin.yaml` and `pyproject.toml`". The conflation of "INSTALL.md Step 3f do-not-copy list" with "INST-1 canonical inventory in `tools/install_audit.py`" is EXACTLY the design-doc-vs-canonical-source drift this slice is meant to mitigate — slice-009's own design.md commits the same class of error in its own example prose. Recursive meta-conformance failure: the slice that's encoding "verify against canonical inventories" into the Critic prompt mislocates the canonical inventory in its own justifying example. Future Critics applying CCC-1 v1.1 with this misleading example will mislocate too.
- **Evidence**: `tools/install_audit.py` lines 44-67 (canonical inventories — positive-inclusion); `methodology-changelog.md` line 157 (the "do not copy" list — INSTALL.md Step 3f, negative-exclusion).
- **Proposed fix**: In the Dim 9 sub-clause 2 body refinement prose AND in ADR-008, distinguish TWO canonical inventory surfaces: (a) `tools/install_audit.py` `_CANONICAL_*` tuples = positive-inclusion (what IS installed); (b) `INSTALL.md` Step 3f "do not copy" list = negative-exclusion (what is intentionally NOT installed). The slice-006 DEVIATION-1 example actually exercises (b), not (a). The slice-006 DEVIATION-2 example exercises (a) — `ai-sdlc-VERSION` IS in `_CANONICAL_METADATA`. Both surfaces named in the body to keep the example honest. Update design.md line 12 + ADR-008 Context.
- **Builder draft**: ACCEPTED-FIXED — applied to design.md (line 12 + Dim 9 prose draft) + ADR-008 Context section. Also updates the actual Dim 9 sub-clause 2 body refinement plan to name BOTH surfaces.

#### M3: AC #4 changelog-entry pin lacks substantive content anchor per slice-008 M2 N-surface discipline

- **Claim under review**: design.md line 62: "Rule reference: CCC-1 v1.1"; mission-brief AC #4 verification line 56: "asserts ... `CCC-1 v1.1` ... all present".
- **Issue**: Slice-008's `test_v_0_23_0_bc_1_v_1_2_entry_present_in_repo_and_installed` (test_methodology_changelog.py:109) asserts THREE substrings in BOTH in-repo + installed copies: `## v0.23.0`, `BC-1 v1.2`, AND `Negative anchors` (substantive content anchor). For CCC-1 v1.1, design.md doesn't specify the analogous substantive content anchor. A vacuous file containing only `## v0.24.0` and `CCC-1 v1.1` would pass — defeats the slice-008 M2 N-substring schema-pin discipline.
- **Evidence**: `tests/methodology/test_methodology_changelog.py:127` (`assert "Negative anchors" in in_repo`) as precedent template; design.md missing the analogous CCC-1 v1.1 substantive pin.
- **Proposed fix**: Commit to `design.md mechanical tables` as the substantive canonical phrase for the v0.24.0 entry. Reuses the same surface across critique.md AC #1 AND methodology-changelog AC #4 per slice-008 N-surface lesson (one canonical phrase pinned in N surfaces = strong contract). Update design.md "Components touched > methodology-changelog.md > Rule reference" to explicitly name `design.md mechanical tables` as the canonical phrase the v0.24.0 entry MUST contain.
- **Builder draft**: ACCEPTED-FIXED — pinned `design.md mechanical tables` as the substantive canonical phrase. Applied to design.md.

#### M4: ADR-008 "Reversibility: cheap" inconsistent with cited "same shape as ADR-005" precedent (ADR-005 was tagged expensive)

- **Claim under review**: ADR-008 frontmatter `reversibility: cheap` + body "same shape as ADR-005 but smaller magnitude".
- **Issue**: ADR-005 (per methodology-changelog v0.21.0 entry line 129) was tagged "expensive — with explicit 'Items that cannot be reverted' sub-section". ADR-008 tagged `cheap` while admitting "same shape as ADR-005" creates a precedent contradiction. "Smaller magnitude" is intuitively reasonable but lacks a quantitative criterion. Future Critics asking "is this slice's reversibility tagged consistently with prior ADRs at the same shape?" will see contradiction; damages the calibration trail.
- **Evidence**: methodology-changelog.md line 129 (ADR-005 expensive); ADR-008 frontmatter cheap + body "same shape but smaller magnitude".
- **Proposed fix**: Keep `cheap` (justified by smaller surface area) but ADD a brief justification in ADR-008 body explicitly stating WHY magnitude matters: "v1.1 refines body text of an existing sub-clause (~5 sentences) vs. v1 added an entire new dimension (9th dimension + 5 sub-clauses + Kiczales citation + 7 prose-parity sites + critique-output-format extension). Revert cost scales with surface area introduced; smaller surface = cheaper revert." Add this paragraph to ADR-008 Reversibility section.
- **Builder draft**: ACCEPTED-FIXED — added magnitude justification paragraph to ADR-008 Reversibility section.

#### M5: PMI-1 versioned-gate "N=2 supersession-stable" claim is circular at slice-009

- **Claim under review**: mission-brief.md line 47 + design.md line 31 + line 85 + line 212: "Per slice-007/008 N=2-stable supersession pattern".
- **Issue**: Slice-007 INTRODUCED the PMI-1 versioned-gate test pattern (`_at_0_22_0` — first instance). Slice-008 SUPERSEDED that with `_at_0_23_0` — the FIRST supersession event (N=1 supersession-events). Slice-009 would be the SECOND supersession event (N=2 post-completion). Citing N=2 stability as JUSTIFICATION for performing the second supersession is internally circular — slice-009 IS the second supersession; you can't cite N=2 stability as evidence supporting itself. The slice-008 aggregated lessons phrasing "PMI-1 versioned-gate test supersession pattern N=2 stable (slice-007 + slice-008)" may itself be off-by-one (slice-007 INTRODUCED; slice-008 first-superseded = 1 supersession event, not 2).
- **Evidence**: Slice-007 introduced `_at_0_22_0`; slice-008 first-superseded with `_at_0_23_0` = 1 supersession event. Slice-009 ratchets to 2 supersession events post-completion. The aggregated-lessons N=2 phrasing conflates "instance count of the test pattern" (which IS N=2 stable at slice-007 + slice-008) with "supersession-event count" (which is N=1 pre-slice-009).
- **Proposed fix**: Drift the phrasing across mission-brief.md (line 47) + design.md (lines 31, 85, 212) + ADR-008 to: "Per slice-007 + slice-008 PMI-1 versioned-gate pattern (slice-007 introduced; slice-008 first-superseded = N=1 supersession event); slice-009 ratchets to N=2 supersession events on completion. The supersession ACT itself is justified by the slice-008 reflection's explicit choice + the in-repo VERSION file's monotonicity invariant — NOT by N=2 stability of supersession-events (slice-009 itself is creating that N=2)."
- **Builder draft**: ACCEPTED-FIXED — drifted phrasing across mission-brief.md, design.md, and ADR-008.

### Minors (log; address if cheap)

#### m1: Mid-slice smoke gate command excludes CAD-1 drift signal — AC #3 row 3 won't WRITTEN-FAILING at Phase 1b

- **Claim under review**: design.md line 239 + 284: `pytest tests/methodology/test_critique_agent.py -q`.
- **Issue**: Phase 1b smoke gate's expected "CAD-1 audit reports content-drift exit 1" needs the CAD-1 test in the command to observe the WRITTEN-FAILING signal at mid-slice. Current command only runs `test_critique_agent.py`. AC #3's row-3 genuine PENDING → WRITTEN-FAILING transition won't be visible at Phase 1b — only at Phase 2 verification.
- **Proposed fix**: Extend Phase 1b command: `pytest tests/methodology/test_critique_agent.py tests/methodology/test_critique_agent_drift.py::test_in_repo_and_installed_critique_agent_are_content_equal -q`. Expect: 15 tests collected from test_critique_agent.py PASS; 1 test from test_critique_agent_drift.py FAIL (the genuine WRITTEN-FAILING for AC #3 row 3). The drift FAIL at mid-slice is intentional — Phase 2 forward-sync resolves it.
- **Builder draft**: ACCEPTED-FIXED — extended Phase 1b command.

#### m2: Sub-aspect of B1 — same count mismatch

- Already covered by B1's fix.
- **Builder draft**: ACCEPTED-FIXED — folded into B1.

#### m3: ADR-008 file path not pinned explicitly in design.md "Decisions made"

- **Claim under review**: design.md line 181: `[[ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class]]` (wiki-link only, no path).
- **Issue**: Cosmetic; recoverable at /build-slice. Prior ADRs (005/006/007) use `architecture/decisions/ADR-NNN-<kebab>.md`; should pin explicitly.
- **Proposed fix**: Add explicit file path `architecture/decisions/ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class.md` in design.md "Decisions made (ADRs)" section.
- **Builder draft**: ACCEPTED-FIXED — added file path.

#### m4: Empirical-verification table claim "3 in methodology-changelog.md historical entries" for `slice-006` is approximate

- **Claim under review**: design.md line 140 + 144.
- **Issue**: Cosmetic; the count is irrelevant to TF-1 genuineness (only counts in `agents/critique.md` matter).
- **Proposed fix**: Remove the parenthetical counts entirely (the in-methodology-changelog count is irrelevant for AC verification).
- **Builder draft**: ACCEPTED-FIXED — removed parentheticals from empirical-verification table.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (11 vs actual 13 existing tests); M2 (INST-1 do-not-copy list framing inaccurate); M5 (N=2 supersession-stability claim circular); m4 (empirical count approximate). Per Wiegers: claims about counts and inventories must trace to evidence; 5+ specific numeric/inventory claims drifted.
- [x] **Missing edge cases** — none. Per Hendrickson: prompt-prose refinement has no runtime input / concurrency / network / platform-specific surface. Design.md line 247 covers the single edge case (5-sub-clause invariant break at mid-slice → STOP, diagnose).
- [x] **Over-engineering** — none. Per Fowler speculative-generality: design.md is appropriately thin for Standard mode; Wiring matrix correctly empty per WIRE-1 fixture; no premature abstraction.
- [x] **Under-engineering** — M3 (AC #4 changelog-entry pin lacks substantive content anchor per slice-008 M2 N-surface lesson; Wiegers AC-trace candidate — design.md was supposed to make the canonical-phrase choice but deferred it).
- [x] **Contract gaps** — none. Per Newman: slice adds no endpoints/events/integrations; Critic prompt IS a contract but slice doesn't alter its shape.
- [x] **Security** — none. Per OWASP: no auth/authz/injection/IDOR/data-flow surface introduced.
- [x] **Drift from vault** — B2 (mission-brief AC #3 names non-existent test function while design.md uses correct name — slice-internal contradiction); M4 (ADR-008 reversibility tag inconsistent with cited precedent shape). Per Sommerville: requirements-design traceability requires consistent references.
- [x] **Web-known issues** — skipped intentionally: no external technology / API / library / platform-version dependency. The slice modifies in-house prompt-prose + tests + version files. Per dimension body: web-known is for post-cutoff platform changes / quotas / deprecations — none apply.
- [x] **Cross-cutting conformance** — M1 (AC #2 substring-only test doesn't pin paragraph location within sub-clause 2; algorithm-path-conformance risk); M2 (INST-1 do-not-copy list framing is itself a design-doc-vs-canonical-inventory drift — slice-009's own design.md commits the very class of error it's encoding into the Critic prompt; recursive self-application demonstrates the failure class). The latter is the most epistemically interesting finding — confirms slice-009 is intervening on a real, currently-active miss class.

## Triage

**Triaged by**: user
**Date**: 2026-05-11
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Empirically verified via `grep -c '^def test_' tests/methodology/test_critique_agent.py` = 13. Applied `s/11 existing/13 existing/` and `s/11 → 13/13 → 15/` across mission-brief.md + design.md in this round. |
| B2 | Blocker | ACCEPTED-FIXED | Empirically verified test name `test_in_repo_and_installed_critique_agent_are_content_equal` exists at test_critique_agent_drift.py:62; old name `test_in_repo_critique_md_byte_equal_to_installed` does not exist anywhere in codebase. Applied to mission-brief.md AC #3 TF-1 row + verification plan in this round. |
| M1 | Major | ACCEPTED-PENDING | Add `test_critique_dim_9_sub_clause_2_body_contains_design_md_table_paragraph` at /build-slice asserting `design.md mechanical tables` falls between sub-clause 2 title and sub-clause 3 title. TF-1 plan grows 6 → 7 rows. Location-pin guard prevents silent paragraph-relocation drift. |
| M2 | Major | ACCEPTED-FIXED | Empirically verified the "do not copy" list lives at INSTALL.md Step 3f per methodology-changelog.md v0.20.0 line 157, NOT in tools/install_audit.py `_CANONICAL_*`. Applied: design.md (line 12) + ADR-008 Context now distinguish positive-inclusion (`_CANONICAL_*`) from negative-exclusion (`INSTALL.md` Step 3f) surfaces. The Dim 9 sub-clause 2 body refinement plan updated to name BOTH surfaces, so the Critic prompt itself becomes self-correcting on this exact class. Recursive meta-conformance: slice-009's example now correctly demonstrates the discipline. |
| M3 | Major | ACCEPTED-FIXED | Committed `design.md mechanical tables` as the substantive canonical phrase for the v0.24.0 changelog entry (reuses surface across critique.md AC #1 + methodology-changelog AC #4 per slice-008 N-surface lesson). Applied to design.md Components-touched section + AC #4 verification plan. |
| M4 | Major | ACCEPTED-FIXED | Kept `reversibility: cheap` (smaller surface area = lower cost). Added magnitude-justification paragraph to ADR-008 Reversibility section explicitly stating: v1.1 refines ~5 sentences vs. v1 added 9th dimension + 5 sub-clauses + Kiczales citation + 7 prose-parity sites + output-format extension. Revert cost scales with surface area. |
| M5 | Major | ACCEPTED-FIXED | Drifted phrasing across mission-brief.md (line 47) + design.md (lines 31, 85, 212) + ADR-008. New framing: "slice-007 introduced + slice-008 first-superseded = N=1 supersession event; slice-009 ratchets to N=2 supersession events on completion. The supersession act is justified by slice-008 reflection's explicit choice + VERSION file monotonicity, NOT by N=2 stability (which slice-009 itself is creating)." |
| m1 | Minor | ACCEPTED-FIXED | Extended Phase 1b mid-slice smoke command to include CAD-1 byte-equality test; expected: 15 PASS + 1 FAIL (genuine WRITTEN-FAILING for AC #3 row 3). |
| m2 | Minor | ACCEPTED-FIXED | Folded into B1's fix (same 11 → 13 count mismatch). |
| m3 | Minor | ACCEPTED-FIXED | Added explicit ADR-008 file path `architecture/decisions/ADR-008-refine-ccc-1-dim-9-with-design-md-tables-sub-class.md` to design.md "Decisions made" section. |
| m4 | Minor | ACCEPTED-FIXED | Removed approximate parenthetical counts ("3 in methodology-changelog.md historical entries") from design.md empirical-verification table; the in-changelog count is irrelevant for AC verification. |

**Final-verdict derivation**:
- 0 ESCALATED → not BLOCKED
- 1 ACCEPTED-PENDING (M1) → **NEEDS-FIXES**
- 10 ACCEPTED-FIXED (B1, B2, M2, M3, M4, M5, m1, m2, m3, m4) — applied in this round

## Notes for /reflect (Critic calibration)

Slice-009's Critic found 11 findings; 10 ACCEPTED-FIXED in-round + 1 ACCEPTED-PENDING for /build-slice. The Critic's epistemically-strongest finding was **M2** — it caught that slice-009's own design.md commits the exact design-doc-vs-canonical-inventory drift class slice-009 is encoding into the Critic prompt. This is **recursive self-application** of the methodology — slice-009 demonstrating the failure class it's mitigating, in its own draft. Cross-cutting conformance Dim 9 catch rate at slice-009 = predicted 100% at /critique time (3 of 3 cross-cutting hits caught: M1 substring-only-pin algorithm-path, M2 design-doc-vs-canonical-inventory drift, M3 N-surface schema-pin discipline). Building on slice-006/007/008 trajectory: 0% → 25% → 60% → 100% → 100% (preserved at N=4).

Slice-008's "Wiegers AC-trace sub-class candidate at N=1" advances to N=2 if M3 is correctly framed as AC-trace (every AC needs design specificity; AC #4 deferred canonical-phrase choice = under-specified AC). Watch for further AC-trace accumulation at slice-010+.
