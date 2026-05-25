# Critique: Slice 039 apply-critic-calibrate-proposals-to-critique-agent

**Critic reviewed**: mission-brief.md, design.md, ADR-040, ADR-041 (+ calibration-log L445–497, agents/critique.md L110–204, test_critique_agent.py L100–160, shippability.md rows 6/11/13/15/16/24/25, methodology-changelog.md L255–268, test_methodology_changelog.py L2951–3025)
**Date**: 2026-05-18
**Result**: NEEDS-FIXES

## Summary

The slice is structurally sound and faithfully applies both ACCEPTED proposals to-intent (verified verbatim against calibration-log L457/L458 — no weakened paraphrase). The SCPD-1 row enumeration, single-structural-invariant supersession chain, 4-part PMI-1 bump, ADR-040 `-D`-class-boundary extension, and the PTFCD-1/PTFFD-1 self-check all check out. Two real gaps: (1) the APED-1 content-pin set pinned title + evidence-anchors but not the load-bearing behavioral verbs (partial slice-037 M-add-1 anti-tautology exposure); (2) a frozen v0.39.0 changelog occurrence of the superseded test name was not enumerated/reasoned, and the SCPD-1 replacement is 14 occurrences (2/row) not 7.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: APED-1 content-pin set does not pin the load-bearing behavioral verbs — partial slice-037 M-add-1 anti-tautology exposure
- **Claim under review**: design.md L11 "content-pin tests … mirrors the slice-037 M-add-1 anti-tautology pattern"; design.md L13 enumerates APED-1 pins as `_sub_clause_present` + `_location_pinned` + `_names_aped_1_rule_id` + `_cites_audit_parse_rule_evidence_anchors`.
- **Issue**: Per slice-037 M-add-1 (a content-deliverable AC needs a pin that FAILS if the load-bearing prose is absent), the four enumerated APED-1 pins assert title, location, rule-ID token, and evidence anchors — none asserts the *behavioral obligation verbs* that ARE Proposal 1's load-bearing content ("MUST Bash-execute", "file a Blocker", "executed, not reasoned", the adversarial-battery member list). A future edit could weaken "MUST Bash-execute" → "should reason about" and all four pins stay green. The MEPD-1 set is correctly behavioral (`_names_both_clauses`); APED-1 lacked the symmetric pin.
- **Evidence**: slice-037 reflection.md:54 (M-add-1 VALIDATED law); design.md L13 vs L14 asymmetry; calibration-log L457 (the verbs to pin).
- **Proposed fix**: Add `test_critique_dim_9_audit_parse_rule_empirical_execution_pins_behavioral_obligation` asserting `"Bash-execute"`, `"Blocker"`, the "executed, not reasoned" phrase, and ≥2 battery-member tokens; state in design.md that this pin FAILS on silent weakening.
- **Builder draft**: ACCEPTED-FIXED at design.md L13 — added `_pins_behavioral_obligation` to the APED-1 pin enumeration with the explicit anti-tautology property ("FAILS if `MUST Bash-execute` → `should reason about` even while title/location/rule-ID/evidence-anchor pins stay green") and annotated MEPD-1's `_names_both_clauses` as the symmetric pin M1 requires.

### Minors (log; address if cheap)

#### m1: v0.39.0 changelog historical occurrence of the superseded test name unaddressed; "all consumers" claim not shown reasoned
- **Claim under review**: design.md L20 SCPD-1 propagation rows 6/11/13/15/16/24/25; design.md L51 "any docstring/prose self-reference".
- **Issue**: Repo-wide grep also matches `methodology-changelog.md:266` inside the frozen v0.39.0 PTFCD-1 `Validation:` line. It is correctly NOT a live consumer (no audit runs changelog `Validation:` lines) and renaming would corrupt history — so scoping to shippability.md is *right* — but the design never enumerated this site nor stated the frozen-history exclusion reasoning, against the FBCD-1 sub-mode (a) full-fileset-grep enumeration discipline (agents/critique.md:189).
- **Evidence**: `methodology-changelog.md:266`; design.md L20/L51; agents/critique.md:189.
- **Proposed fix**: Add one sentence enumerating the changelog:266 occurrence as deliberately-NOT-renamed (frozen historical record; not an executed consumer).
- **Builder draft**: ACCEPTED-FIXED at design.md L20 — added the "Scope boundary (per Critic m1 — FBCD-1 sub-mode (a))" sentence explicitly enumerating `methodology-changelog.md:266` as an enumerated-and-excluded frozen-history site, not a missed one.

#### m2: SCPD-1 propagation is 14 occurrences (2 per row), enumerated by slice-label not occurrence-count
- **Claim under review**: design.md L20 "across rows 6, 11, 13, 15, 16, 24, 25 (lines 14/19/21/23/24/32/34)".
- **Issue**: Each line contains the superseded token **twice** (Why-prose + Command-cell pytest) — 14 replacements, not 7. A one-per-row replace leaves 7 stale prose occurrences; whether the propagation pin catches that depends on absence-of-old vs presence-of-new assertion.
- **Evidence**: `grep -c` = 2 occurrences/line on each of the 7 lines (14 total); design.md L18/L20 phrased per-row.
- **Proposed fix**: State 14 occurrences (2/row × 7); propagation pin asserts `"_lists_eleven_sub_clauses" not in catalog` (absence-of-old) in addition to presence-of-new.
- **Builder draft**: ~~ACCEPTED-FIXED~~ → **SUPERSEDED-BY-M-add-1** (DR-1 EXTEND). The first applied fix (`"_lists_eleven_sub_clauses" not in catalog` + count 14) was itself defective — a guaranteed false-FAIL on the legitimately-preserved line-34 frozen narrative. Re-opened and replaced by M-add-1's selector-token-discriminated reformulation (see below); design.md L18/L20 re-corrected.

### Meta-Critic missed finding (DR-1 /critique-review EXTEND)

#### M-add-1: shippability.md line 34 carries a third frozen-history occurrence — count is 15 not 14; the accepted m2 `not in catalog` pin is a guaranteed false-FAIL
- **Claim under review**: design.md L18 (Builder's now-superseded m2 fix) `"test_critique_dim_9_lists_eleven_sub_clauses" not in catalog` + "14 occurrences, 2 per row".
- **Issue**: Mechanically verified (independent `grep -o` per line: 2/2/2/2/2/2/**3** = **15**). shippability.md line 34 (slice-025 row 25) carries a frozen `` `_lists_ten_sub_clauses` -> `_lists_eleven_sub_clauses` `` PMI-1-supersession narrative recording slice-025's *own* ten→eleven supersession — renaming it corrupts history (false "ten→twelve"); the same frozen-history class m1 caught for changelog:266, but on the surface SCPD-1 edits. The blanket `not in catalog` pin therefore guaranteed-false-FAILs at /validate-slice on the legitimately-preserved string. The "2/row = Why-prose + Command-cell" model is structurally wrong (the 2 renamable tokens/row are bare-`Command` + backticked-`Machine-cmd` selector duplicates).
- **Evidence**: `architecture/shippability.md` line 34 (3 occurrences; the `_lists_ten -> _lists_eleven` PMI-1-supersession narrative + 2 live `::test_critique_dim_9_lists_eleven_sub_clauses` selector tokens); lines 14/19/21/23/24/32 = 2 live each; `agents/critique.md:189` (FBCD-1 sub-mode (a)); slice-025 row "2 historical-narrative occurrences preserved" precedent.
- **Proposed fix**: rename only the `::test_critique_dim_9_lists_eleven_sub_clauses` selector tokens (selector-prefix discriminator); pin asserts (i) zero such selector tokens remain + (ii) `_lists_twelve` in all 14 live positions + (iii) line-34 frozen narrative asserted UNCHANGED; enumerate line 34 alongside changelog:266 in the scope-boundary.
- **Builder draft**: ACCEPTED-FIXED at design.md L18 + L20 — propagation reformulated to the selector-token-discriminated pin; occurrence map restated as 15 = 14 live (rename) + 1 frozen line-34 narrative (preserved); both frozen-history twins (changelog:266 + shippability line 34) enumerated-and-excluded in the scope-boundary sentence.

## Dimensions checked

- [x] Unfounded assumptions — m1 (resolved); verified-sound: 4-part PMI-1 bump (VERSION/ai-sdlc-VERSION/plugin.yaml all confirmed 0.51.0), Dim 7 has no structural-count test, single structural-invariant test at test_critique_agent.py:115.
- [x] Missing edge cases — m1 (resolved — frozen-history site now enumerated); anti-tautology transient-remove-restore guard (design.md L80) sound.
- [x] Over-engineering — none. Two distinct disciplines → two rule-IDs; ADR-041 rejects gratuitous two-version split.
- [x] Under-engineering — M1 (resolved — APED-1 behavioral-verb pin added).
- [x] Contract gaps — none. Prompt-contract + test-name-contract only; `_lists_eleven`→`_lists_twelve` consumer surface correctly enumerated (m2 resolved); APED-1's own trigger correctly reasoned as not-firing on this slice.
- [x] Security — none — no actors/permissions/inputs/secrets/data-ownership surface.
- [x] Drift from vault — none. ADR-040 `-D`-behavioral-class is a sound extension of ADR-019/ADR-023 (no prior ADR stated `-D ⊆ Dim 9`); ADR-038 mint-not-version precedent followed; cited test functions verified extant.
- [x] Web-known issues — skipped — not applicable (zero external technology/API/platform surface; internal methodology-prose + pytest + markdown only).
- [x] Cross-cutting conformance — m1 (resolved — FBCD-1 sub-mode (a) enumeration now demonstrated); RSAD-1 self-application addressed (design.md L82–87 — APED-1 correctly not-triggered, MEPD-1 satisfied by construction via AC4); PTFCD-1/PTFFD-1 self-check clean (no phantom citation); SCPD-1 proactive-application (slice-014 mode) correctly planned; EPGD-1 dedicated-section-header followed-regardless; ADR-041 correctly identifies the bump as a standard single PMI-1-gate supersession, not a double.

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | APED-1 `_pins_behavioral_obligation` pin added (design.md L13); DR-1 confirmed sufficient + symmetric with MEPD-1 `_names_both_clauses` |
| m1 | Minor | ACCEPTED-FIXED | `methodology-changelog.md:266` frozen-history occurrence enumerated-and-excluded in scope-boundary (design.md L20); DR-1 confirmed correct |
| m2 | Minor | ACCEPTED-FIXED | Direction correct; original `not in catalog`/count-14 remedy was a guaranteed false-FAIL — re-opened and superseded by M-add-1's selector-token-discriminated reformulation (design.md L18); corrected fix applied |
| M-add-1 | Major | ACCEPTED-FIXED | DR-1 EXTEND missed finding; independently verified by Builder against shippability.md line 34 (3 occurrences: 1 frozen slice-025 narrative + 2 live selector tokens; 15 total = 14 live rename + 1 frozen preserve). Propagation reformulated to selector-prefix-discriminated pin + both frozen-history twins enumerated (design.md L18/L20) |
