# Critique Review: Slice 076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-28
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively sound on the catches it surfaces (B1-B4 are all real; M1/M6/M7 are well-targeted; m1-m5 are correctly scoped). The 11 ACCEPTED-FIXED dispositions are mostly clean. However, the **B1 fix is structurally incomplete** — the Builder's redesigned algorithm at design.md L136 names a phantom function `parse_target_queue_for_candidate_metadata` that does not exist in the codebase and cannot be derived from `parse_queue_text` (whose docstring at `tools/slice_queue_claim.py:230-234` explicitly excludes PSQ-1 enumeration fields). The fix-block-completeness sweep also missed a stale `3 named files` count in ADR-069 L175. Two additional concerns surface from independent re-review: the v0.73.0 entry-pin substring list at design.md L21 includes a Builder-invented anchor `mints a new rule on a new family axis` that diverges from the established v0.68.0 / v0.69.0 / v0.72.0 precedent (`'mints a new rule'` literal only), and a missing TF-1 row for slice-queue stage-missing (symmetric to the shippability row M2 added).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1**: parse_queue_text wrong module — VALID; severity Blocker is appropriate. The citation correction (slice_queue_writer → slice_queue_claim) and the algorithm-redesign direction (rebase-target verbatim baseline) are both correct. **However the fix application is incomplete — see M-add-1 below.**
- **B2**: SOFT file-set drift (mission-brief vs design+ADR) — VALID; severity Blocker is appropriate. Cross-file FBCD-1 catch on the load-bearing axis of the slice. Fix applied at mission-brief AC3 + milestone L46.
- **B3**: `/archive` Haiku-LLM-dispatched not deterministic — VALID; severity Blocker is appropriate. `skills/archive/SKILL.md:58` confirmed Haiku dispatch via Agent tool with `model: haiku`. Option (b) drop is the correct fix.
- **B4**: VAULT_CLAIM detection predicate under-spec — VALID; severity Blocker is appropriate. The gate-before-dispatch ordering at ADR-069 + the defensive post-merge guard at design.md are correctly specified.
- **M1**: Windows backslash `_SOFT_FILE_SET` membership — VALID; severity Major is appropriate. APED-1-executed concrete evidence; fix shape (forward-slash + `.as_posix()` normalization + `list[str]` typing) is canonical.
- **M2**: Stage-missing edge case — VALID; severity Major is appropriate. ACCEPTED-PENDING disposition correct (the code-level catch lands at /build-slice). **Coverage incomplete — see M-add-2 below.**
- **M3**: `_index.md` AC coupled with B3 — VALID; severity Major appropriate; cleanly couples with B3 resolution.
- **M4**: UNKNOWN/MIXED fail-closed not in TF-1 — VALID; severity Major appropriate. The 3 new TF-1 rows close the must-not-defer gap.
- **M6**: INSTALL.md two-site tool-count — VALID; severity Major appropriate. INSTALL.md L22 + L166 both confirmed via grep; two-site TF-1 row name is correctly scoped.
- **M7**: Audit-log race documentation — VALID; severity Major appropriate. The ADR-069 § Audit log "Concurrency / race-acceptance" paragraph correctly grounds in ADR-067 cooperative-not-adversarial.
- **m1-m4**: ACCEPTED-FIXED disposition rationales are accurate.
- **m5**: R-21 ACCEPTED-PENDING — VALID; correctly defers to /build-slice Phase A scaffolding.

## Suspicious findings

No suspicious findings — every B/M/m the first Critic filed maps to a concrete defect or under-spec that I can independently verify in the post-fix artifacts.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### M-add-1: B1 fix structurally incomplete — design.md L136 + ADR-069 § Resolution algorithm reference phantom function `parse_target_queue_for_candidate_metadata` that doesn't exist

- **Severity**: **Blocker** (recurrence of B1's core defect under a renamed wrapper)
- **Claim under review**: design.md L136: `write_slice_queue(repo_root, candidates=parse_target_queue_for_candidate_metadata(target_text), ...)`. ADR-069 § Resolution algorithm has the same shape with `candidates=<...>` ellipsis.
- **Issue**: Per Fowler (refactoring rule: name a function only after it exists or you specify it) AND per Wiegers (requirements-precision discipline): `parse_target_queue_for_candidate_metadata` is not defined anywhere in the slice artifacts, not in `tools/slice_queue_claim.py`, not in `tools/slice_queue_writer.py`. The Critic established at B1 that `parse_queue_text` returns CLAIM metadata only (docstring at `tools/slice_queue_claim.py:230-234`: "Known PSQ-1 fields (Source / Blast-radius / Parallel-safety / Effort / Risk-retired) are NOT returned"). So either (a) PCR-1 must mint a NEW parser that extracts `name + source + blast_radius + parallel_safety + effort + risk_retired` from queue.md text (additional design surface that's not currently scoped), OR (b) PCR-1 must NOT call `write_slice_queue` for the slice-queue.md SOFT-regen and instead use a different mechanism (e.g., write the rebase-target's queue text verbatim with a textual claim-merge overlay — no `write_slice_queue` re-emit). The current design.md prose conflates both options into a phantom-function reference.
- **Evidence**: design.md L136 `parse_target_queue_for_candidate_metadata`; absent from codebase grep; `tools/slice_queue_claim.py:230-234` docstring explicit non-extraction of PSQ-1 fields.
- **Proposed fix**: Pick one of: **(1)** mint a `parse_full_queue_entries(text: str) -> list[dict]` parser in this slice (adds scope, adds AC, adds TF-1 rows); OR **(2)** redesign the slice-queue.md SOFT-regen to NOT round-trip through `write_slice_queue`'s candidate-list — instead, write rebase-target's queue text verbatim, then surgically overlay merged claim lines via a textual edit on `**Claimed-by:**` / `**Claimed-at:**` lines under each candidate's `**Risk-retired:**` line (no `write_slice_queue` call; no candidate parser mint). Document the chosen mechanism concretely in both design.md AND ADR-069. This must close before /build-slice — otherwise the Builder will hit B1's core defect again during code authoring.
- **Builder draft**: ACCEPTED-FIXED — option (2) chosen as cleaner scope. design.md + ADR-069 § Resolution algorithm rewritten to specify the textual claim-overlay mechanism: new private helper `_overlay_claims_on_queue_text(queue_text: str, merged_claims: dict) -> str` that inserts/updates `Claimed-by:` + `Claimed-at:` lines under each candidate's `Risk-retired:` line. No `write_slice_queue` dispatch for SOFT-resolve. TF-1 row added for the overlay helper.

### M-add-2: TF-1 plan missing slice-queue stage-missing test, asymmetric with M2 fix

- **Severity**: **Minor** (per Hendrickson — coverage symmetry across the load-bearing surface)
- **Claim under review**: M2's proposed fix said "Add TF-1 rows for the add-on-one-side case for **both SOFT files**" (plural). Builder only added one row (shippability).
- **Issue**: The SOFT-regen `slice-queue.md` resolution path documents both `:2:` and `:3:` non-zero handling at design.md Edge-cases column, but no corresponding `test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_slice_queue` row exists in TF-1.
- **Evidence**: mission-brief.md TF-1 plan (only shippability stage-missing row); M2 proposed fix text ("both SOFT files").
- **Proposed fix**: Add `test_resolve_soft_conflict_handles_file_added_only_on_one_branch_for_slice_queue`. Implementation lives in the same `_regen_slice_queue` helper but the test surface is independent.
- **Builder draft**: ACCEPTED-FIXED — TF-1 row added.

### M-add-3: design.md L21 BC-PROJ-10 entry-pin anchor `'mints a new rule on a new family axis'` diverges from v0.68.0 / v0.69.0 / v0.72.0 precedent (`'mints a new rule'` literal)

- **Severity**: **Minor** (per Sommerville — established conventions should be challenged only with explicit deviation rationale)
- **Claim under review**: design.md (m3 fix): "design.md 'What's new' BC-PROJ-10 paragraph extended with the 5-anchor enumeration … (e) `mints a new rule on a new family axis`".
- **Issue**: Inspected `tests/methodology/test_methodology_changelog.py`: v0.68.0 BRANCH-2 pins `'mints a new rule'` literal; v0.69.0 PSQ-1 pins `'mints a new rule'` literal; v0.72.0 PSQ-3 pins `'mints a new rule'` literal. The first three rule-on-parallel-family-axis precedents (BRANCH-2, PSQ-1, PSQ-3) ALL use `'mints a new rule'` (3 words, not 7). design.md anchor (e) prescribes the longer phrase which has no precedent. **Risk**: at /build-slice the Builder writes the changelog entry with the precedent phrase, but the paired-pin test asserts the longer phrase — entry-pin test fails on a string the Critic + design explicitly invented.
- **Evidence**: `tests/methodology/test_methodology_changelog.py` v0.68.0 / v0.69.0 / v0.72.0 entry-pin function bodies; design.md anchor (e) (post m3 fix).
- **Proposed fix**: Replace anchor (e) with the precedent `'mints a new rule'` literal; the family-axis canonical phrase is already covered by anchor (d) `'parallel-conflict-resolution'`.
- **Builder draft**: ACCEPTED-FIXED — anchor (e) corrected to `'mints a new rule'`.

### M-add-4: ADR-069 § Reversibility carries stale `SOFT file-set is 3 named files` count — FBCD-1 sub-mode (b) Builder-sweep miss

- **Severity**: **Major** (per the slice-020/021/022/023/038/042 meta-Critic signature class — N≥10 cumulative pattern; this is exactly the meta-Critic's job per FBCD-1 sub-mode (b))
- **Claim under review**: ADR-069 § Reversibility: "Reverting is unlikely in practice: PCR-1's design is well-bounded (SOFT file-set is **3 named files**; auto-regen dispatches to existing tooling; fail-closed semantics on UNKNOWN)."
- **Issue**: The Builder swept 3→2 across mission-brief AC3 + milestone L34 + milestone L46 + design.md `_SOFT_FILE_SET` + ADR-069 § Decision + ADR-069 Resolution-algorithm table + ADR-069 SOFT-class-file-set §, but **missed ADR-069 § Reversibility**. High-signal stale anchor — anyone reading the Reversibility section sees `3` and contradicts the `_SOFT_FILE_SET` pin.
- **Evidence**: ADR-069 § Reversibility `3 named files` literal (post-Builder-sweep state).
- **Proposed fix**: Change to `2 named files`. 1-line edit.
- **Builder draft**: ACCEPTED-FIXED — ADR-069 § Reversibility `3 named files` → `2 named files`.

### M-add-5: APED-1 enumeration in mission-brief Must-not-defer covers `_SOFT_FILE_SET` + `classify_conflict` but misses `_extract_claim_diff` + `_merge_shippability` predicates

- **Severity**: **Minor** (per APED-1 just-extended scope completeness)
- **Claim under review**: mission-brief Must-not-defer "APED-1 empirical execution on the soft-conflict file-set predicate AND the `classify_conflict` 5-way classification logic. [13-input adversarial battery]".
- **Issue**: The first Critic ran APED-1 against `_SOFT_FILE_SET` membership (M1 catch). But the slice mints OTHER predicate-like classifiers — `_extract_claim_diff` parser (materially affects VAULT_CLAIM detection per B4) and `_merge_shippability` row-union predicate. These are not in the APED-1 enumeration.
- **Evidence**: mission-brief.md Must-not-defer APED-1 entry (post m1 fix); design.md private-helpers list including `_extract_claim_diff` + `_merge_shippability`.
- **Proposed fix**: Extend mission-brief Must-not-defer APED-1 enumeration to include (a) `_extract_claim_diff` parser predicate empirical execution + (b) `_merge_shippability` row-union predicate empirical execution. Lands at /build-slice as additional executed-battery rows in the build-log.
- **Builder draft**: ACCEPTED-FIXED — mission-brief Must-not-defer APED-1 entry extended.

## Severity adjustments

### M5 (Pre-finish gate count claim — Critic self-withdrew)

- **First-Critic disposition**: OVERRIDDEN (rationale: "Critic explicitly self-withdrew this finding; substantive concern moved to m1")
- **Meta-Critic assessment**: SEVERITY-WRONG (semantically miscategorized).
- **Issue**: OVERRIDDEN's defined meaning per `tools/triage_audit.py:28` is "user disagrees with Critic — rationale required." Here the **Critic itself withdrew the finding** — there is no user-disagreement-with-Critic, just a Critic mid-review reversal. The triage_audit's verdict-pattern check accepts OVERRIDDEN-with-rationale (rationale is non-empty), so this isn't a hard failure — but the disposition vocabulary has a gap (no SELF-WITHDRAWN disposition).
- **Recommended**: leave OVERRIDDEN with current rationale (acceptable per triage_audit semantics); file a follow-up methodology slice to extend disposition vocabulary with `WITHDRAWN-BY-CRITIC`. The disposition vocabulary gap is a separate methodology refinement (queue at slice-079+).
- **Builder ratification**: noted; deferred methodology refinement candidate. No immediate fix to this slice's disposition.

## Notes

Meta-Critic confidence: **high** on M-add-1 (the phantom-function name is unambiguously absent from the codebase + its semantic role contradicts `parse_queue_text`'s explicit non-extraction docstring) and **high** on M-add-4 (`3 named files` stale literal is grep-verifiable at ADR-069 § Reversibility). Medium confidence on M-add-3 (the precedent is clear but the Builder may have a deliberate-deviation rationale that isn't surfaced). Lower confidence on M-add-2 and M-add-5 (coverage-symmetry arguments are inherently negotiable).

Overall calibration of the first Critic on this slice: **strong on dimension coverage** (Dim 1/2/4/7/9 all surfaced concrete defects); **weak on fix-block-completeness verification** — the first Critic accepted B1's ACCEPTED-FIXED disposition without verifying the redesigned algorithm names a real function. The slice-076 calibration pattern matches the slice-020/021/022/023/038/042 lineage where the meta-Critic's signature catch class is FBCD-1 sub-mode (b) (Builder-sweep miss) — N≥11 cumulative now reinforced.

The `OVERRIDDEN-on-self-withdrawn` vocabulary gap is worth surfacing as a methodology refinement candidate but doesn't block this slice.
