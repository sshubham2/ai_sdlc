# Critique Review: Slice 053 wire-backlog-md-into-slice-and-reflect

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-20
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong — B1's structural diagnosis, M4's empirical self-bootstrap defect catch, and M3's slice-051-recipe injection are all well-grounded and correctly recomputed. The Builder's ACCEPTED-FIXED responses are complete on all 10 findings with no over-eager accepts (slice-029 over-accept lens tested clean). Independent re-review (slice-032 "a design correction is itself an unguarded adversarial surface" lens, N+1) surfaces one missed contract gap (the empty-`Evidence:` candidate-block edge case under the B1-revised insert position) and three minor structural concerns. No suspicious findings, no severity adjustments.

## Confirmed findings

All 10 first-Critic findings are VALID with correct severities and complete Builder fixes:

- **B1** (insert anchor structurally fragile): VALID; severity Blocker is appropriate; concern matches design.md§"in-place additive write contract" + backlog.md candidate-block structure (SC-001/SC-002 at diagnose-out/backlog.md lines 89-105 / 109-124 confirm the Source→Severity→Risk-profile→Dependencies→…→Evidence metadata sequence). Builder fix at design.md:108 + ADR-055§Decision + Open ambiguities item 3 correctly relocates the insert to after `**Evidence:**` block. Empirically verified the post-fix shape is structurally stable.
- **M1** (canonical phrases deferred to /build): VALID; severity Major is appropriate. Builder locked `MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists` (Test #3) and `append **Addressed:** slice-NNN-<name> on YYYY-MM-DD under each closed candidate block` (Test #6) at design time. **Empirically verified neither phrase pre-exists in skills/slice/SKILL.md or skills/reflect/SKILL.md** — no tautological-green collision risk. Fowler's "tests as design specifications" framework satisfied.
- **M2** (R-13 producer-side dependency unpinned): VALID; severity Major appropriate; matches risk-register.md:225 (R-13 OPEN, deferred per slice-051/052 own-slice precedent). Builder fix at ADR-055§Consequences (line 63) + design.md Test #6 grammar-pin extension correctly hedges via consumer-side `SC-\d{3}` literal pin. Newman's "contract-test on cross-service boundaries" framework satisfied (within R-13's deferred-structural-closure constraint).
- **M3** (perturbation recipe under-specified): VALID; severity Major appropriate; matches slice-051 aggregated lesson on git-tracked perturbation hazard. Builder fix at design.md:193-200 echoes the 6-step save-bytes-then-restore-via-hash-assertion recipe verbatim with the explicit `NEVER git checkout/restore/stash` clause.
- **M4** (self-bootstrap empirically wrong under bare `SC-\d{3}` trigger): VALID; severity Major appropriate. **Empirically re-verified**: `grep "\*\*Closes:\*\* SC-" architecture/slices/slice-053-wire-backlog-md-into-slice-and-reflect/mission-brief.md` returns NOT-FOUND under the post-fix `**Closes:**` sentinel-anchored regex. Builder's refinement is correctly self-consistent — slice-053 itself no-ops on its own /reflect round-trip side, as design.md "Open ambiguities" item 4 claims.
- **m1-m5**: All five minor findings VALID; line-number stripping, META-1 enforcing-assertion citation, gitignore framing clarification, BFRD-1-mirror test naming, and double-shipment append-never-replace all correctly applied to design.md + ADR-055 in the Builder fix block.

## Suspicious findings

No suspicious findings. The first Critic did NOT over-reach — every finding has both an empirical anchor and a precedent-grounded framework citation.

## Missed findings

### M-add-1: Empty-`Evidence:`-list candidate-block edge case under B1-revised insert position

- **Issue**: The B1 fix correctly relocates the `**Addressed:**` insert to AFTER the `**Evidence:**` sub-bullet list. But design.md§"in-place additive write contract" phrases the location as *"between the last `Evidence:` sub-bullet and the next `### SC-NNN` header, or end-of-file"*. This presumes `**Evidence:**` exists and has at least one sub-bullet. **It does not handle the case where an SC-NNN candidate block has NO `Evidence:` sub-list** — possible for a manually-authored backlog candidate OR for a future build_backlog.py emit-shape change. Under the current design contract, Claude reading the prose would be unable to locate the insert position deterministically (no `last Evidence sub-bullet` anchor exists in the block).
- **Framework**: Sommerville (graceful-degradation contract) + Wiegers (boundary-value requirements analysis). Per the Builder's own m5 disposition ("Error cases" must cover the prior-slice double-shipment edge case), an analogous edge case exists for the upstream producer-shape variation. The first Critic caught the post-fix double-shipment edge case (m5) but not the pre-condition shape gap.
- **Design.md ref**: design.md "in-place additive write contract" subsection + ADR-055§Decision round-trip side.
- **Severity**: Minor — the diagnose→slice-candidates→backlog.md pipeline currently always emits Evidence sub-lists (verified for all 26 of 26 candidates in diagnose-out/backlog.md), so practical impact today is zero. But the contract layer should handle the degenerate case explicitly.
- **Proposed fix**: add an Error-case clause: *"SC-NNN block has no `**Evidence:**` sub-bullet list → insert the `**Addressed:**` line after the last top-level metadata bullet of the candidate block (i.e., after `**Suggested approach:** …`), before the next `### SC-NNN` header or end-of-file."*
- **Builder draft**: ACCEPTED-FIXED — added the empty-Evidence-list Error-case clause to design.md "in-place additive write contract" subsection.

### M-add-2: Test #6 bundles three distinct assertions (canonical phrase + `SC-\d{3}` grammar pin + literal `SC-` substring)

- **Issue**: Per the post-fix design.md Test inventory row 6, Test #6 (`test_reflect_skill_md_bcr_1_round_trip_canonical_phrase_present`) makes multiple substring assertions inside one test function: (a) the full canonical M1 phrase, (b) the literal `SC-\d{3}` regex grammar token (M2 extension). Per the BFRD-1 / SOAD-1 precedent the first Critic invoked in m4, each test pins ONE thing — a multi-assert test makes failure messages ambiguous (which substring is missing?) and complicates the per-test mid-slice contrast plan. Test #7 already exists to pin the `**Closes:** SC-` sentinel grammar; bundling the `SC-\d{3}` grammar pin into Test #6 instead of splitting it into a new test is a deviation from the BFRD-1-mirror discipline the same /critique m4 invoked.
- **Framework**: Hendrickson (testing — single-assertion-per-test discipline) + Beck/Fowler (xUnit test isolation).
- **Design.md ref**: design.md Test inventory row 6 ("M1-locked at design time + M2-extended with grammar pin").
- **Severity**: Minor — semantically correct, structurally untidy.
- **Proposed fix**: split Test #6 into `test_reflect_skill_md_bcr_1_round_trip_canonical_phrase_present` (canonical-phrase only) + `test_reflect_skill_md_bcr_1_sc_grammar_pinned` (literal `SC-\d{3}` substring only). Renumber Test #7 (closes-sentinel) → Test #8. Audit module becomes 8 tests total (was 7 post-M4).
- **Builder draft**: ACCEPTED-FIXED — split Test #6 into 6a (canonical phrase) + 6b (SC-\d{3} grammar pin); renumbered Test #7 → Test #8; entry-pins are now #9 + #10. Audit module → 8 tests + 2 entry-pins = 10 total.

### M-add-3: MCFS-1 co-FAIL during methodology-changelog.md perturbation (Test #9/#10 contrast plan)

- **Issue**: design.md per-test contrast plan says *"Tests 8, 9 → perturb `methodology-changelog.md` v0.61.0 entry tokens. FAIL. Restore. PASS. (methodology-changelog.md is also git-tracked — apply the same 6-step recipe.)"* The M3 fix correctly notes the OSDG-1 family co-FAIL hazard on SKILL.md perturbation, but a parallel hazard applies to the entry-pin contrast: `tools/methodology_changelog_forward_sync.py` (MCFS-1, slice-041) will HALT on a divergent installed copy. If the perturbation is on the in-repo `methodology-changelog.md` only (not the installed `~/.claude/methodology-changelog.md`), MCFS-1 itself will FAIL — polluting the contrast signal exactly as the OSDG-1 co-FAIL would. The mid-slice gate must run MCFS-1 in isolation along with the entry-pin tests, NOT alongside other tools that would compound the noise.
- **Framework**: Hendrickson (isolation of testing-axis contrasts) + slice-051 aggregated-lesson row 6 (which the first Critic invoked, generalized one level higher).
- **Design.md ref**: design.md per-test contrast plan, Tests 8+9 (now 9+10) row.
- **Severity**: Minor — the recipe is correct in principle; only the surrounding-tool noise warning is missing.
- **Proposed fix**: add to design.md per-test contrast plan a parenthetical *"(do NOT run `$PY -m tools.methodology_changelog_forward_sync` during the v0.61.0-entry perturbation window — MCFS-1 will HALT on the divergent installed copy and pollute the contrast signal; isolated `pytest tests/methodology/test_methodology_changelog.py::test_v_0_61_0_bcr_1_backlog_round_trip_entry_present_in_repo -q` only)"*.
- **Builder draft**: ACCEPTED-FIXED — added the MCFS-1 co-FAIL parenthetical warning to design.md per-test contrast plan, Tests #9+#10 row.

## Severity adjustments

No severity adjustments. All first-Critic severities are appropriate against the slice's risk tier (medium) and the post-fix concrete impact.

## Notes

Confidence: high on the empirical-verification axis (10 grep checks executed; canonical phrases, sentinel literals, section-anchor uniqueness, mission-brief sentinel-absence, R-13 risk status, and candidate-block structure all directly verified against on-disk artifacts).

Calibration observation on this slice's first Critic: the review pattern is the slice-039/044/051 high-yield shape — every finding has an empirical anchor (grep / sed / risk-register line number) AND a framework citation. The ACCEPTED-FIXED-in-one-pass dynamic on all 10 findings tested clean under slice-029 over-accept lens — Builder did not soften proposed fixes nor relocate flaws.

The three meta-findings above are structural and were missed at the "what does the post-fix contract degenerate into?" lens rather than the "is the first Critic right about pre-fix defects?" lens — i.e., they're slice-032 "design correction is itself an unguarded surface" class observations, not first-Critic gaps per se.

Reservation: M-add-3 borders on hyper-vigilance; if the user judges it noise during TRI-1, the meta-Critic concedes the recipe is empirically correct as-is and the MCFS-1 hazard is a /build-slice-time runtime concern not a /design defect.
