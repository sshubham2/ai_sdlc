# Reflection: Slice 108 add-fbcd-1-cardinality-fanout-sub-mode

**Date**: 2026-06-03
**Shipped**: YES

## Validated
- **Sub-mode (c) closes the AP-10 blind spot at design-Critic time** — `agents/critique.md` FBCD-1 now mandates a WHOLE-repo count-pin grep on a counted-set cardinality change; validated by `test_critique_dim_9_fix_block_completeness_names_cardinality_fanout_sub_mode` (mutation-confirmed non-vacuous on both anchors) + CAD-1 byte-equality.
- **FBCD-1 v1.1 versioned-refinement path was the right MEPD-1 discharge** — the full PMI-1 cascade (5 surfaces + pip + rolling-test rename + shippability #75 repoint + #114) landed clean: PMI-1/MCFS-1/AVFS-1/TVFS-1 all exit 0 at 0.83.0; `test_version_files_synchronized_at_v_0_83_0` green; full suite 1549/0; shippability 113/113. The CCC-1 v1.1 precedent held.
- **The dogfood works** — a slice authoring the count-fan-out rule had its OWN un-swept sibling count-claim (L902 docstring) caught by the very review stack it strengthens (meta-Critic m-add-1). The strongest possible validation of sub-mode (c)'s value.

## Corrected
- None. The build matched design.md on every point (the meta-Critic's "12" literal ground-truth, the AP-10 enumeration, the sub-clause-count-untripped boundary all held). No ADR superseded, no risk-status flip, no design.md correction.

## Discovered
- **A versioned Critic-prompt refinement (vN.N, no new `-D` rule-ID) is NOT a "light" prose edit** — FBCD-1 v1.1 / CCC-1 v1.1 carry the entire BC-PROJ-16 version-bump cascade (rolling-test rename + 12-literal sweep + predecessor docstring line + precedent-chain append + shippability repoint + #114=max+1). Impact: budget any future "just add a sub-mode/sub-bullet to the Critic" slice as a full version-bumping slice, not a 1-paragraph edit.
- **TF-1 audit does not parse a combined `| 1, 4 |` AC cell** as covering both ACs — each AC needs its own row (surfaced at pre-finish, fixed by splitting). WIRE-1 reads a `| — | — | — | — |` placeholder as a row with an empty New-module cell — a zero-module slice needs header+separator ONLY. Impact: minor TF-1/WIRE-1 authoring conventions; not Critic-reachable (the Critic stack doesn't run those audits on table format).

## Deferred
- A **deterministic repo-wide count-pin build-check tool** (out-of-scope per mission-brief) — sub-mode (c) is Critic-prompt-only; a `tools/*.py` audit that mechanically greps every `== N` pin on a changed counted set would be the build-time backstop to the design-time Critic check. Candidate for a future `build-check-candidate` slice if the fan-out recurs post-sub-mode-(c).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions (all ACCEPTED-FIXED, verdict CLEAN) + reality at build/code-review/validate. Three-Critic stack: design-Critic (`/critique`) + meta-Critic (`/critique-review`) + code-Critic (`/code-review`).

- **M1** (entry-pin substantive-content phrase unspecified → tautological-green risk): **VALIDATED** — ACCEPTED-FIXED. The content-bearing pin shipped (`Counted-set cardinality fan-out` asserted in the v0.83.0 entry-pin); the code-Critic confirmed the phrase is unique repo-wide → discriminating, not tautological. A real defect path (a presence-only pin would have greened regardless of semantics).
- **M2** ("4 leg literals" undercounts the 12 `0.82.0` literals): **VALIDATED** — ACCEPTED-FIXED. The meta-Critic re-verified "12" is the true count; the renamed rolling test swept all 12 + the `0.81.0→0.82.0` predecessor line + the precedent chain `/108`; code-Critic git-grep found zero stale `0.82.0` leg. Real enumeration-precision gap — and ironically the exact count-literal fan-out class this slice encodes.
- **m1** (intro "Two sub-modes" above three bullets): **VALIDATED** — ACCEPTED-FIXED; intro now reads "Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):" (code-Critic confirmed well-formed above exactly three bullets).
- **m2** (PTFFD-1 backstop citation): **VALIDATED** — no-change verification; the row #75 repoint + PTFCD-1 clean (471 tokens resolve) confirmed the backstop reasoning.
- **M-add-1** (meta-Critic, EXTEND; second stale "not three" at `test_critique_agent.py:L902`): **VALIDATED** — ACCEPTED-FIXED. **The headline calibration signal.** The first design-Critic (m1) AND the Builder's first RSAD-1 sweep both saw the L840 comment but missed the structurally-identical L902 docstring "not three" clause — the meta-Critic caught it by extending the design's own `grep "not three"` recipe. This is the slice's OWN sub-mode (c) fan-out class (a counted-set cardinality change 2→3 leaving an un-swept sibling count-claim) manifesting in the slice's OWN diff.

**Missed by Critic**: (1) the L902 docstring stale count-claim — missed by the first design-Critic + the Builder's first sweep, caught by the meta-Critic (m-add-1, above). This is a count-literal fan-out miss — feeds the NEXT `/critic-calibrate` as a self-referential datapoint: the slice applying Proposal 1 had a Proposal-1-class miss, caught by DR-1. (2) The TF-1 combined-cell + WIRE-1 placeholder gate failures surfaced at pre-finish, not Critic-flagged — but those are mechanical audit-format issues outside the Critic stack's static-artifact scope, not design defects.

**Pattern**: the 3-Critic stack performed excellently on this versioned-refinement methodology slice — design-Critic (M1 content-pin + M2 literal-undercount, both real defect paths), meta-Critic (m-add-1, the count-fan-out miss in the slice's own diff — DR-1 earning its keep on the EXACT class the slice ships), code-Critic (executed the version-cascade grep + mutation-confirmed test non-vacuity — zero false-alarm; its 2 minors were honest no-change observations). **Do NOT collapse the stack.** The recursive validation is the lesson: a slice teaching the Critic to grep all count-claim sites had its own un-swept count-claim caught by the very stack it strengthens.

## Lessons for next slice
- **Budget a versioned Critic-prompt refinement as a full version-bumping slice** (BC-PROJ-16), not a 1-paragraph edit — the rolling-test rename + literal sweep + shippability repoint + #114 are the bulk of the work.
- **On a counted-set-cardinality-changing slice, run the design's own RSAD-1 grep recipe EXHAUSTIVELY and act on EVERY hit** — the first sweep missed L902; the rule the slice ships (sub-mode c) is precisely "don't enumerate only the obvious site." Apply it to your own diff first.
- **TF-1 authoring**: one row per AC (no combined `| 1, 4 |`); **WIRE-1**: zero-module slice = header+separator only (no `| — |` placeholder row).

## Vault updates made (thin vault)
- This slice's [[design.md]] + [[mission-brief.md]] — reconciled for cross-file consistency (FBCD-1 sub-mode (a)) at /critique fix-time (M1/M2/m1) + /critique-review fix-time (m-add-1).
- [[architecture/shippability.md]] — row #114 added (the slice's critical-path entry; added at build as part of AC4 + the BC-PROJ-16 cascade) + row #75 version-sync citation repointed.
- [[architecture/lessons-learned.md]] — appended (Step 5).
- [[architecture/drift-log.md]] — slice-108 pre-finish drift-check entry (CLEAN).
- No ADR (versioned refinement of [[decisions/ADR-022]]); no risk-register change; no build-check promotion (the lesson is the slice's own deliverable — FBCD-1 v1.1 — and BC-PROJ-16 already covers the cascade).
