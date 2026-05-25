# Critique Review: Slice 049 add-triage-adopt-skill-drift-guards

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-19
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong — B2 (the load-bearing false-precedent catch) is correct and its evidence chain (commit `8823c53`, `methodology-changelog.md:474`) reproduces exactly. No first-Critic finding is over-reach. But the rev-1 remediation and the rev-0 design share two unflagged defects that survive into rev-1: a shippability-catalog schema mismatch ("two rows" vs the enforced one-row-per-slice convention the slice's own AC3 consumer-propagation pin asserts), and an unguarded CLAUDE.md prose edit that an existing prose-pin test guards (slice-039 class). Both Builder-re-verified against the live tree and ACCEPTED-FIXED in rev-2.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (phantom `test_shippability_catalog.py`) — VALID, Blocker correct. Independently verified absent; real artifacts `tools/shippability_runner.py` + `test_shippability_runner_segment_contract.py` + `test_shippability_path_existence.py` all present. PTFCD-1 class.
- **B2** (false slice-035 precedent → slice IS a behavior change) — VALID, Blocker correct, load-bearing. Independently verified: `git log --diff-filter=A` → drift tests first added by commit `8823c53` (slice-021, BRANCH-1); `methodology-changelog.md:474` is the v0.35.0 BRANCH-1 entry; they rode an existing v0.35.0 4-part bump → no no-bump precedent. The rev-1 remediation (OSDG-1 as a new plain RULE-ID extending, not superseding, CAD-1/mini-CAD/EOL-DRIFT-1) is convention-correct: SOAD-1 (v0.56.0) is precedent for "mints a new rule, supersedes nothing" with a plain RULE-ID; `test_v_0_57_0_osdg_1_entry_present_in_repo` / `_shippability_consumer_propagation` exactly match the enforced v0.50–v0.56 naming convention; INST-1-unchanged is correct (two `tests/` modules + an ADR add nothing to `plugin.yaml`'s enumerated surface).
- **M1** (prose-only AC3/AC4 fail `--strict-pre-finish`) — VALID, Major correct. slice-045/PTFFD-1 law; fold + re-cite is the right fix.
- **M2** (forward-sync-first masks pre-existing real drift) — VALID, Major correct. slice-030A "coincidental cp masks the failure" class; the pre-sync EOL-diff evidence-preservation step is well-specified.
- **m1** (uncorroborated slice-019/021 claim) — VALID, Minor correct; deletion correct (same false-precedent class as B2, non-load-bearing).
- **m2** (WIRE-1 exemption format) — VALID no-op non-finding; correctly Minor/dropped.

## Suspicious findings

None. Every first-Critic finding is VALID at its filed severity; no over-reach on any of the six.

## Missed findings

- **B-add-1 (Blocker): shippability "two rows" violates the enforced one-row-per-slice convention the slice's own AC3 consumer-propagation pin asserts.** rev-1 AC4 + design.md §"What's new" specified "two new rows / a row for each new pin." Verified `architecture/shippability.md`: 6-column schema `| # | Slice | Critical path | Command | Runtime | Machine-cmd |`, one row per slice keyed `| NN | slice-NNN-name`, latest `| 48 | slice-048-…`. The precedent `test_v_0_56_0_soad_1_shippability_consumer_propagation` asserts a **single** `| 48 | slice-048-…` row + the rule ID. The slice's own AC3 names `test_v_0_57_0_osdg_1_shippability_consumer_propagation` → by convention asserts a single `| 49 | slice-049-… | OSDG-1`. "Two rows" either breaks the one-row-per-slice convention every runner/audit assumes or makes the AC3 pin unsatisfiable — a self-contradictory contract shipped green. **Proposed fix**: one slice-049 row whose Critical-path covers both triage+adopt guards (slice-048 row precedent).
- **M-add-1 (Major): the CLAUDE.md Mini-CAD generalization edit is guarded by an existing prose-pin test the slice's verification surface does not run (slice-039 / slice-032 class).** The must-not-defer item edits `## Self-hosting discipline` — the exact section `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py::test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant` pins (section-scoped; asserts "content-equal modulo line endings" + "EOL-DRIFT-1" + "ADR-033" present, "MUST be byte-equal" absent). The must-not-defer shows awareness ("keep EOL-DRIFT-1-precise wording") but neither the TF-1 plan, verification plan, nor pre-finish gate names that test — the edit's guard is not in the slice's own evidence surface (caught only by the broad "full methodology suite" line, not an AC-mapped row). **Proposed fix**: add a verification row + TF-1 row running `test_root_claude_md_cad1_eol_agnostic.py` immediately after the CLAUDE.md edit (slice-039 realign-the-pin-you-touch law).

## Severity adjustments

None. B1, B2, M1, M2, m1, m2 all at correct severity. B2-as-Blocker is correctly the spine of NEEDS-FIXES; M1/M2-as-Major (process-correctness) and m1/m2-as-Minor well-calibrated. B-add-1 filed Blocker (self-contradictory contract shipped green); M-add-1 filed Major (regression-scope coverage gap).

## Notes

Confidence high — both missed findings verified against the live tree (`architecture/shippability.md` schema/count; `test_root_claude_md_cad1_eol_agnostic.py` source). The byte-equality question in the review brief is a non-issue: changelog:474 "byte-equality tests" is stale v0.35.0 historical prose pre-dating ADR-033's slice-033 retrofit; the canonical `assert_md_forward_synced` is EOL-agnostic and reused verbatim. `.gitattributes` `skills/**/SKILL.md text eol=lf` (line 8) genuinely covers both new openers. The first Critic's blind spot is consistent: both missed items are contract/regression-scope concerns about how the rev-1 remediation lands against existing enforced conventions, not the design's internal logic — a dimension thinner than its strong logic/precedent analysis.

## Builder rev-2 disposition (drafts — TRI-1 ratifies)

- **B-add-1** → **ACCEPTED-FIXED**: AC4 + design.md §"What's new" + build-sequencing now specify exactly ONE row `| 49 | slice-049-… | OSDG-1 …` covering both guards (slice-048 #48 precedent); Builder independently verified the one-row-per-slice schema + the SOAD-1 single-row pin against the live tree.
- **M-add-1** → **ACCEPTED-FIXED**: new AC5 + verification row #5 + TF-1 row (`test_root_claude_md_cad1_eol_agnostic.py::test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant`) + must-not-defer "re-run immediately after the CLAUDE.md edit"; Builder verified the pin is section-scoped to `## Self-hosting discipline`.
