# Critique Review: Slice 042 realign-entry-present-pin-names-to-decoupled-shape

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-18
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic correctly identified the *class* (slice-022 self-violation: inaccurate identifier inventory in an identifier-truth slice) and the LIVE-core (37=33+4 defs, 2 comments, 4 siblings, 1 tool source — all re-verified VALID). But the ACCEPTED-FIXED edits substituted a fresh set of wrong numbers for five inventory buckets — the recompute-don't-trust failure (slice-041 rev-1 DR-1 class; execute-don't-reason now N≥4). The Builder has since recomputed every figure via the authoritative ADR-044 anchor regex and applied rev-2 corrections (all B-add/m-add ACCEPTED-FIXED).

## Confirmed findings (first Critic was right)

- **B1** (def 40→37; AC "2 _entry_names"→4 incl no-`_sub_`): VALID, Blocker appropriate. Builder re-verified: 37 = 33 `_entry_present` + 4 `_entry_names` @ L802/1005/1512/1606; anchor leak-proof (CAD-1 family structurally excluded).
- **B3** (4 undocumented active refs incl `tools/...:58`): VALID, Blocker appropriate. `tools/methodology_changelog_forward_sync.py:58` is the only `tools/` source ref (the `.pyc` is stale bytecode); no conftest/parametrize string refs.
- **m1** (smoke-gate "4 files" wording): VALID, Minor appropriate.

## Suspicious findings

None. Every first-Critic finding is a real defect; no over-reach.

## Missed findings (first Critic dispositioned ACCEPTED-FIXED without re-running the grep)

- **B-add-1 (Blocker)**: rev-1 `shippability.md = 67 occ / 31 unique` wrong. Authoritative anchor: **69 occ / 32 unique** (28 `_entry_present` + 4 `_entry_names`), 28 rows. Internally falsifiable (28+4=32≠31). Builder-verified. **Disposition: ACCEPTED-FIXED** — design.md table + Components + ADR-045 + mission-brief AC2 → 69/32/28.
- **B-add-2 (Blocker)**: rev-1 FROZEN `changelog = 43` wrong (M2 over-corrected 39→43). Authoritative: **40 occ / 32 unique**. Builder-verified. **Disposition: ACCEPTED-FIXED** → 40 in design.md + ADR-045.
- **B-add-3 (Blocker)**: rev-1 FROZEN `16 prior ADRs incl ADR-016/018/031` wrong. Authoritative: **13** (ADR-009..014, 026, 033, 034, 035, 038, 039, 040); ADR-016/018/031 contain **0** fn-name-family matches (B2's named-ADR correction was itself unverified). Builder-verified. **Disposition: ACCEPTED-FIXED** → predicate retained (leak-proof regardless), illustrative count → 13, false ADR-016/018/031 claim removed.
- **m-add-1 (Minor)**: rev-1 `_index.md(4)`, `critic-calibration-log.md(1)` wrong. Authoritative: `_index.md` = **3**; `critic-calibration-log.md` = **0** (bucket non-existent); `lessons-learned.md` = 2 (correct). FROZEN ⇒ cannot break build, but a false inventory claim in an identifier-truth slice. Builder-verified. **Disposition: ACCEPTED-FIXED** → `_index.md(3)`, calibration-log bucket dropped.
- **m-add-2 (Minor)**: mid-slice smoke-gate scope vs live `::`-selector consumers. `tools/shippability_path_audit.py:199-213` (`missing-test-function`) + `tools/shippability_runner.py:144` (`subprocess.run`) resolve the 69 `::`-selectors; between defs-renamed (step 3) and shippability-realigned (step 4) they are expected-red. Builder-verified. **Disposition: ACCEPTED-FIXED** — design build-seq step 3 now explicitly scopes the smoke gate to the SOT file ONLY and excludes path-audit/runner from its green-bar claim (validated at step 4/6).

## Severity adjustments

- **M3** SEVERITY-WRONG in scope (not severity): only **ADR-044** contains the literal old name (1 occ, line 44); **ADR-045** has **0** (placeholders). Minor severity correct for ADR-044; rev-1 prose "ADR-044/045 cite old name" factually overstated for ADR-045. **Disposition: ACCEPTED-FIXED** — ADR-045 Consequences narrowed to "ADR-044 cites once; ADR-045 zero".

## Notes

Confidence: high — every figure instantiated with ripgrep against the real working tree (clean master at slice-041 merge, pre-rename old-name state) AND independently re-verified by the Builder with the authoritative ADR-044 anchor regex (canonical command now embedded in design.md so figures are reproducible, not hand-transcribed). Calibration signal: the recompute-don't-trust law fired on the Builder's OWN fix (N≥4 with slice-032/034/041) — strong `/critic-calibrate` + `/reflect` input. The slice's escape hatch ("build-step-1 grep = single source of truth, grep wins") bounds production impact, which is why B-add-1/2/3 are slice-022-class identifier-truth Blockers (wrong facts in an identifier-truth slice's own design), not behavior Blockers.
