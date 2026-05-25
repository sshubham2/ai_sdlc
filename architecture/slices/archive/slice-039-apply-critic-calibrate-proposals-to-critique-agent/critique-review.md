# Critique Review: Slice 039 apply-critic-calibrate-proposals-to-critique-agent

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-18
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is largely sound: M1 (APED-1 behavioral-verb anti-tautology) is a correct slice-037-M-add-1 application and the Builder's `_pins_behavioral_obligation` fix is sufficient; m1 (changelog:266 frozen-history) and m2 (multi-occurrence) are correct in direction. But m1+m2 together MISSED the mechanically-decisive instance: shippability.md line 34 (slice-025 row) carries a **third**, frozen historical-narrative occurrence of `_lists_eleven_sub_clauses` requiring preservation — making the count 15 not 14, AND making the Builder's already-applied `"_lists_eleven_sub_clauses" not in catalog` absence-of-old assertion a **guaranteed false-FAIL**. This is the exact FBCD-1 sub-mode (a) full-fileset-enumeration defect m1 caught for changelog:266, recurring un-enumerated on the closer, more dangerous shippability.md surface that SCPD-1 propagation actually edits.

## Confirmed findings

- **M1** — confirmed; **Major is appropriate**. The four original APED-1 pins (title/location/rule-ID/evidence-anchor) provably stay green under a `MUST Bash-execute`→`should reason about` weakening. The Builder's `_pins_behavioral_obligation` ACCEPTED-FIXED (design.md:13) is sufficient and symmetric with MEPD-1's `_names_both_clauses`. Not a Blocker: APED-1's own trigger does not fire on this slice (no audit parse-rule changed — verified design.md:52/86); build-time real-artifact gates are the structural backstop per slice-037 reflection.md:55.
- **m1** — confirmed; **Minor appropriate** for the changelog:266 instance specifically. Repo-wide grep independently verified: exactly two live `_lists_eleven_sub_clauses` sites (`methodology-changelog.md:266` + `test_critique_agent.py:115`) + the 7 shippability rows; changelog:266 correctly NOT a live consumer. Builder's design.md:20 scope-boundary sentence correct as far as it goes (see M-add-1 for the symmetric site).
- **m2** — confirmed in direction; the absence-of-old instinct is right. But the specific count (14) and the `not in catalog` formulation are wrong — see Severity adjustments + M-add-1.

## Suspicious findings

None. Independently checked the three highest rubber-stamp-risk first-Critic calls — all VALID:
- "Drift from vault — none. ADR-040 `-D`-behavioral-class sound extension": VALID. ADR-019:13 independently corroborates — it defines the `-D` class *behaviorally* ("/critique-time skill-prose heuristics with no programmatic audit"), never by Dim-9 membership; ADR-040's class-boundary pin is a faithful extension; ADR-038:31 reinforces the `-D` ⊥ `vN.N` partition. No contradiction.
- "4-part PMI-1 bump all confirmed 0.51.0": VALID including installed side — independently verified in-repo `VERSION`=0.51.0, installed `~/.claude/ai-sdlc-VERSION`=0.51.0, in-repo `plugin.yaml`=0.51.0. No slice-035-B-add-1 installed-side blind spot; design.md:19 enumerates all 4 parts.
- AC4 entry-pin is NOT a slice-037-M-add-1 tautology one layer up: the `_entry_present_in_repo_and_installed` harness (verified at test_methodology_changelog.py:2869, v0.50.0 PTFFD-1) is already content-bearing (rule-ID token + anti-silent-weakening canonical phrase + ADR lineage), not byte-equality.

## Missed findings

### M-add-1: shippability.md line 34 carries a third, frozen-history occurrence — count is 15 not 14, and the Builder's accepted m2 `not in catalog` pin is a guaranteed false-FAIL
- **Issue**: m2 asserted uniform "14 occurrences (2/row × 7)"; the Builder codified that + a blanket `"_lists_eleven_sub_clauses" not in catalog` pin (design.md:18) as ACCEPTED-FIXED. Mechanically false: per-line `grep -o` = 2/2/2/2/2/2/**3** = **15**. Line 34 (slice-025 row 25) first occurrence is `` `_lists_ten_sub_clauses` -> `_lists_eleven_sub_clauses` `` inside the "Why" prose — a frozen record of *slice-025's own* PMI-1 structural-invariant supersession (ten→eleven). It MUST NOT be renamed: rewriting to `_lists_twelve` would falsely assert slice-025 superseded to twelve — the identical frozen-history corruption class m1 caught for changelog:266, on the surface SCPD-1 actually edits. Because that occurrence is legitimately preserved, the design's blanket `not in catalog` assertion is **guaranteed to false-FAIL at /validate-slice**. The "2 per row = Why-prose + Command-cell" model is also structurally wrong: the 2 renamable tokens per row are the bare-`Command` + backticked-`Machine-cmd` selector duplicates; the prose narrative is the frozen extra.
- **Framework**: FBCD-1 sub-mode (a) full-fileset enumeration (agents/critique.md:189) — same discipline m1 invoked, applied symmetrically.
- **Proposed fix** (applied by Builder as ACCEPTED-FIXED, design.md:18/20): (1) restate as 15 occurrences = 14 LIVE selector tokens to rename + 1 FROZEN line-34 narrative PRESERVED; (2) reformulate the pin to assert zero `::test_critique_dim_9_lists_eleven_sub_clauses` *selector tokens* remain (selector-prefix discriminator) + `_lists_twelve` in all 14 live positions + line-34 frozen narrative asserted UNCHANGED — NOT blanket `not in catalog`; (3) add line-34 to the design.md:20 scope-boundary sentence alongside changelog:266.

## Severity adjustments

- **m2 — SEVERITY-WRONG (scope, not band)**: band Minor is acceptable, but its accepted remedy (`not in catalog` + count 14) is incorrect and the Builder has already baked the unsafe `not in catalog` assertion into design.md:18 as ACCEPTED-FIXED. That fixed text now itself carries the defect (guaranteed false-FAIL) and must be re-opened/superseded by M-add-1's reformulation. → m2 disposition must become **SUPERSEDED-BY-M-add-1**.

## Notes

Confidence high — every load-bearing claim mechanically verified (per-line `grep -o`, repo-wide enumeration, line-32-vs-34 disambiguation, ADR-019:13 `-D`-behavioral corroboration, 4-surface PMI-1 pre-state). First-Critic pattern this slice: excellent precision (M1/m1/m2 all correctly-directioned, zero false positives, ADR-040 + PMI-1 calls independently confirmed sound) but a **partial-enumeration recall failure on its own FBCD-1 sub-mode (a) finding** — m1 enumerated the changelog:266 twin but did not re-run the same discipline against the shippability.md surface where the symmetric twin lives; m2 then compounded it with a 14/`not in catalog` arithmetic-and-formulation error the Builder baked in. The FBCD-1 "enumerate ALL sites, not the first" lesson recurring against the Critic stack itself — fittingly on the slice codifying APED-1's "execute, do not reason". Reservation: M-add-1's exact pin reformulation is a design-direction proposal for TRI-1; the Builder confirmed the selector-prefix discriminator (`::test_critique_dim_9_` token vs bare backticked narrative) is consistent with slice-025's own "2 historical-narrative occurrences preserved" handling and mechanically verified it against shippability.md line 34.
