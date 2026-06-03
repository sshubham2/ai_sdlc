# Critique Review: Slice 108 add-fbcd-1-cardinality-fanout-sub-mode

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-03
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary
The first Critic's review is strong and empirically grounded — M1, M2, m1, m2 are all VALID with correct severities, and every fix-delta the Builder applied verifies clean against the worktree (M2's "12" count is the true literal count, M1's substantive phrase is unique/discriminating, m1 is consistently applied across both design sections). One genuine miss surfaces from independent re-application of the cross-cutting-conformance dimension: a SECOND factually-stale "not three like RPCD-1" count claim in the FBCD-1 test docstring that the design's own RSAD-1 self-application sweep does not enumerate — the exact class this slice's rule exists to catch.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1** (entry-pin substantive-content phrase unspecified) — confirmed; severity **Major** is appropriate. Re-verified against the CCC-1 v1.1 template at `test_methodology_changelog.py:196-224` (asserts `## v0.24.0` + `CCC-1 v1.1` + the substantive phrase `design.md mechanical tables`). A presence-only pin is a tautological green (Wiegers — a verification that cannot fail verifies nothing). The Builder's ACCEPTED-FIXED is sound: design.md§"What's new" L14 + §"Components touched" L40 + §"Tests touched" L112 now all require `## v0.83.0` + `FBCD-1 (v1.1)` + `Rule reference` + `Counted-set cardinality fan-out`. I independently confirmed the phrase `Counted-set cardinality fan-out` does NOT yet exist anywhere in the repo's changelog (grep returns zero hits outside slice-108) so the pin is discriminating, not duplicative.

- **M2** ("4 leg literals" under-frames the rolling-test rename) — confirmed; severity **Major** is appropriate. Re-verified the ground truth: `test_methodology_changelog.py:5496-5536` body contains **exactly 12** `0.82.0` literals and **2** `0.81.0` literals (`sed -n '5496,5536p' | grep -o` count = 12 / 2). The Builder's propagated "12" is CORRECT — no ironic wrong-count fan-out (the maximally-bad outcome this slice would have demonstrated against itself). Major (not Blocker) is right: the original "+ docstring" catch-all meant the sweep would still complete; the issue is enumeration precision, addressable in-slice. Major (not minor) is right: the slice teaching the Critic to grep ALL count literals must not under-frame its own literal sweep — direct dogfood-credibility defect.

- **m1** (intro "Two distinct sub-modes" above three bullets) — confirmed; severity **Minor** is appropriate. The target string `Two distinct sub-modes covering the temporal axis:` exists at `agents/critique.md:194`, so the planned edit will find its target. No test breaks.

- **m2** (PTFFD-1 backstop citation) — confirmed VALID as a logged no-change verification; correctly a Minor. The PTFFD-1 function-level layer at `agents/critique.md:202-205` would indeed emit `missing-test-function` if row #75 retained the stale `_at_v_0_82_0` selector after the rename — a correct belt-and-suspenders observation with SCPD-1 same-block propagation as the primary mechanism.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives second-pass scrutiny against the worktree. I specifically attempted to falsify M2 (is "12" wrong?), M1 (does the phrase collide with an existing assertion, making the pin non-discriminating?), and the dimension claim "row #75 only" (re-ran the AP-10 by-name grep myself) — all three held.

## Missed findings

- **m-add-1: Second stale "not three like RPCD-1" count claim in the `_names_both_sub_modes` test docstring is NOT enumerated by the slice's own RSAD-1 self-application sweep** — Minor.
  - **Issue**: There are TWO factually-stale "not three like RPCD-1" sites in `tests/methodology/test_critique_agent.py`: (1) the section comment at **L840** (`# … Two sub-modes (not three like RPCD-1) …`), which the design's Self-application sweep item 2 (design.md L79) explicitly enumerates and plans to update; and (2) the `test_critique_dim_9_fix_block_completeness_names_both_sub_modes` **docstring at L901-902** (`two sub-modes given FBCD-1's N=10-cumulative-cross-instance evidence base, **not three like RPCD-1**`). Once sub-mode (c) ships, FBCD-1 HAS three sub-modes, so "not three like RPCD-1" at L902 becomes a false count-claim. The design's sweep item 2 addresses the function name + the "two-sub-mode pin" assert-behavior rationale correctly (the asserts only check (a)+(b) presence via `in body`, so leaving them is right — confirmed L916-923), but it does NOT enumerate the docstring's embedded "not three" PROSE claim as a stale-count site. The design's own grep recipe at L76 (`grep "not three" scoped to the edit surface`) would surface L902 if executed — the design wrote the recipe but acted on only one of its two hits.
  - **Framework**: McGraw / Sommerville recursive-self-application (RSAD-1) + the slice's own FBCD-1 sub-mode (c) — a counted-set cardinality change (sub-mode count 2→3) leaving an un-swept sibling count-claim in the same file is precisely the AP-10 fan-out class this slice ships to catch. Maximally on-point dogfood: the slice authoring the count-fan-out rule should survive that very rule (mission-brief AC#5 / RSAD-1 self-application).
  - **design.md ref**: §"Self-application sweep" item 2 (L79) — enumerates only L840; misses L902.
  - **Proposed fix (for Builder via TRI-1)**: extend self-application sweep item 2 to also update the L902 docstring clause — change "two sub-modes given FBCD-1's … evidence base, not three like RPCD-1" to a three-sub-mode-accurate phrasing (e.g., "names the temporal pair (a)/(b); sub-mode (c) on the scope axis is pinned by the sibling `_names_cardinality_fanout_sub_mode` test"). No test asserts this docstring text as a pinned string (grep-confirmed — only L840's comment text appears, and no test reads it), so the edit is safe and breaks nothing. This keeps the slice's own diff clean under the rule it adds.

## Severity adjustments

No severity adjustments. M1/M2 are correctly Majors (real defect path, addressable in-slice, no spike), m1/m2 are correctly Minors. My one added finding (m-add-1) is filed as a Minor by parity with m1 (same internal-prose-count-tension class, no test break, prose-cleanliness with dogfood-credibility weight).

## Notes

High confidence in this review. The first Critic's empirical discipline was exemplary — it hand-verified the AP-10 fan-out scope, the sub-clause-vs-sub-mode count distinction, and the `_names_both_sub_modes` assert behavior against the worktree rather than reasoning about them, and every one of those claims reproduced when I independently re-ran the greps. The Builder's four fix-deltas all land clean (no stale "4 leg" residual; "12" is the true count; the M1 phrase is unique and discriminating; m1 is consistently applied across both design sections). The single calibration signal is a near-miss of the slice's OWN rule: both the first Critic (m1) and the Builder's sweep saw the L840 "not three" comment but neither extended the same logic to the structurally-identical L902 docstring clause — a one-site under-reach of an FBCD-1 sub-mode (c) self-application grep whose own recipe (grep "not three") would have surfaced it. Reservation: m-add-1 is genuinely Minor; it does not gate build and the slice's correctness/test-green outcome is unaffected — but on a slice whose entire thesis is "un-swept sibling count-claims are the recurring miss," leaving one in its own diff is worth the Builder's 30-second fix. EXTEND (not ADJUST) is the verdict because a new finding is the more substantive change.
