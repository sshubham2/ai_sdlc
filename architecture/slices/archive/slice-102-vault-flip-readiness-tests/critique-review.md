# Critique Review: Slice 102 vault-flip-readiness-tests

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-02
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is empirically grounded and correct on every finding it filed — the meta-Critic reproduced the load-bearing executions independently (production `_BASELINE` stays byte-identical at 4 sites under the `write_text` fix; tests-surface `needs-human` drives to ∅ after the M1 remap; 287/160/49 probe reproduced). M1 and M2 are VALID and the Builder's applied fixes are sound for the current corpus and do not perturb production. But the M1 fix — moving the *entire* `unmarked-collection-pathspec` bucket off the checklist into a non-fail-closed `test-collection-pathspec` class — trades M1's false-positive for a **latent false-negative** the first Critic did not surface: a genuine path-resolving literal that is a collection-display member (a list/tuple a test loops over and opens) is silently demoted off the flip-execute checklist AND escapes the fail-closed `needs-human` net. Filed as a missed Major (M-add-1).

## Confirmed findings

- **M1** (collection→checklist mislabel) — confirmed; **Major** appropriate. Executed: 209 = 160 path-construction + 49 collection-pathspec mirrors. Anchors verified real: `test_soft_file_set.py:47-50` (`frozenset` mirror of the Class-B `_SOFT_FILE_SET` that stays), `test_pcr_2a_vault_claim_resolver.py:274/280/286` (`git add` pathspecs), `test_build_checks_audit.py:828` (BC-1 `applies_to`). The Builder's split is the right correction (consumer-driven-contract: the checklist IS flip-execute's contract).
- **M2** (AC4 "combined baseline" vs production-scoped `baseline_tuple()`) — confirmed; **Major** appropriate. The AC4 rewrite to production-scoped `--strict` is consistent with the design. `baseline_tuple()` returns exactly the 4-set.
- **m1** (aggregate floor misses sub-class collapse) — confirmed; **Minor** appropriate. Per-class floors (FLOOR_A/FLOOR_B) are the correct refinement.
- **m2** (backslash-rel surface mis-derivation) — confirmed; **Minor** appropriate. `"tests\\…".startswith("tests/")` is `False`; the `rel.replace("\\","/")` normalization is the correct cheap fix; `tools/test_first_audit.py` stays production under it.
- **m3** (`fixtures/**` silent residual) — confirmed; **Minor** appropriate. The pinned residual-documenting test is the right disposition.

The "no Blocker" call is correct: both load-bearing correctness claims are verified-by-execution; the meta-Critic re-ran both and concurs.

## Suspicious findings

None. Every first-Critic finding is VALID and confirmed by independent execution. No over-reach.

## Missed findings

### M-add-1: `test-collection-pathspec` is a heterogeneous bucket — a genuine path-resolving literal that is a collection-display member is silently demoted off the checklist AND escapes the fail-closed net (proposed severity: **Major**)
- **Issue**: The M1 fix routes the *entire* `unmarked-collection-pathspec` rule output to `test-collection-pathspec`, defined as NOT-checklist and NOT-fail-closed (exit 0). But the class is a purely *structural* signal (`_is_collection_member` + rule 4, audit lines 279/361). Executed against an ordinary loop-over-list pattern:
  ```python
  for rel in ["architecture/slice-queue.md", "architecture/shippability.md"]:
      (tmp_path / rel).write_text("x", encoding="utf-8")
  ```
  Both literals classify `unmarked-collection-pathspec` → on tests become `test-collection-pathspec` (review-at-flip, off-checklist, exit 0) — even though they ARE genuine path-resolves that break **loudly** at flip. The ≤1-hop flow analysis does not track loop/comprehension variable binding, so the path-use one hop away is invisible and rule 4 wins. Same for a list of glob patterns.
- **Why M1's fix introduced it**: M1 was the inverse defect (collection wrongly ON the checklist). The fix moves the whole bucket OFF — achieving "tests `needs-human` → ∅" partly by reclassifying a fail-closed sub-population into a non-gating class. The identical signal is fail-closed `needs-human` (exit 2) on production but a silent non-blocking review-list on tests. **Latent, not live**: all 49 of today's collection members are git-pathspec / Class-B / git-status mirrors (inspected) — the slice ships correctly now.
- **Frameworks**: McGraw (fail-closed default — ambiguous classification must degrade safe; tests degrades to exit-0 where production degrades to exit-2 for the identical signal) + Wiegers (AC2 promises "genuinely-unclassifiable → `needs-human` (never dropped)"; a genuine-resolve-in-a-list is neither checklisted nor routed to `needs-human` — it is dropped into a non-gating bucket).
- **Design refs**: design.md§What's-new ("mostly mirror a production constant… Class-B-routed"); Evidence table ("mostly Class-B constants that STAY"); Tests-surface-regression-strategy (floors guard emptiness-per-sub-population, NOT membership — a genuine-resolve absorbed into the bucket makes the count go UP, FLOOR_B still passes); ADR-092 Consequences (no documented residual for this case, unlike `fixtures/**` and fully-dynamic).
- **Proposed fix** (for TRI-1 → Builder): (a) keep `test-collection-pathspec` fail-closed at a *lower* tier — a distinct "review-required" disposition flip-execute must explicitly acknowledge, rather than exit-0 invisibility — OR, minimally, (b) add an explicit honest-contract **documented-residual test** (mirroring m3 / slice-100's `test_documented_residual_fully_dynamic_path_invisible`) pinning the contract: "a genuine path-resolving literal that is a bare collection-display member is classified `test-collection-pathspec` (review, not checklist, not fail-closed) — flip-execute MUST review this list, not just the checklist." (b) is the cheap honest-contract floor; (a) is the stronger fix. At minimum the design's "mostly stays" prose should be downgraded from an implied invariant to a *current-corpus observation* with the heterogeneity named.

(One smaller missed item, foldable into M-add-1 fix (b): the design documents two residuals — `fixtures/**` and fully-dynamic paths — but omits this third, structurally-identical residual class, an inconsistency in the otherwise-rigorous honest-contract coverage.)

## Severity adjustments

None. M1/M2 correctly Major; m1/m2/m3 correctly Minor. The Builder's ACCEPTED-FIXED (M1, M2) and ACCEPTED-PENDING (m1, m2, m3) dispositions are appropriate.

## Notes

High confidence on the confirmations (re-ran production-baseline-invariance, tests-`needs-human`-∅, and the 287/160/49 probe — all reproduced exactly) and on M-add-1's *existence* (demonstrated by executing the real ruleset against an ordinary loop-over-list). Reservation on M-add-1's *severity*: it is genuinely **latent** (zero of today's 49 collection members is a hidden genuine-resolve), so the slice ships correctly now. Filed Major rather than Minor because (1) it corrupts the flip-execute checklist — the exact consumer this slice exists to serve — and the failure mode (a will-break literal demoted to "mostly stays") is the mirror image of M1 (correctly rated Major); and (2) it is a fail-closed-property regression relative to the production surface, which the must-not-defer list elevates. **Calibration observation**: the first Critic is strong on empirical verification of stated claims (executed everything it asserted) but had a blind spot on the *second-order consequence of its own accepted fix* — M1's remap was checked for "does it remove the 49 mirrors" (yes) but not for "what else does the now-non-fail-closed bucket silently absorb." Recommend TRI-1 treat M-add-1 fix (b) as the cheap must-do and (a) as a discussion item.
