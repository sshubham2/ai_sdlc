# Critique Review: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-31
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong on the high-severity axis — B1, B2, B3, M1, M2, M3 are all VALID with correct severities, and the B3 raw-porcelain switch was the right call. But the B3 fix itself introduced a NEW latent defect the post-fix design does not close: `_parse_worktree_porcelain` returns the `branch` value as `refs/heads/slice/...` (unstripped), while step 3's `for-each-ref --format='%(refname:short)'` returns `slice/...` — the step-4 set intersection silently never matches, classifying every worktree-backed branch as an orphan (false-refuse). This is the "a Critic's own fix is a fresh claim" pattern (slice-078/082/083) and it is a Blocker. Two additional missed concerns (path-normalization symmetry, empty-set/default-branch edge cases) surface.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (own-worktree self-exclusion): confirmed; Blocker appropriate. `detect_active_worktrees` (pulse_worktree_resolver.py:275-345) does emit the current slice's own worktree as a block; branch-name self-exclusion against a path-keyed source was genuinely mismatched. The path-equality fix is the correct shape.
- **B2** (APED-1 — reasoned-not-executed): confirmed; Blocker appropriate. `detect_active_worktrees(Path('.'))` returns `[]` in this repo's main checkout, so the classification was never executed against a real two-worktree porcelain. ACCEPTED-PENDING real-fixture-at-build is the correct disposition.
- **B3** (filter-cascade reclassification): confirmed; Blocker appropriate. `detect_active_worktrees` lines 313-329 drop prunable/non-`refs/heads/`/regex-non-match/path-gone blocks — a worktree-backed `slice/077` (no name suffix, line 320 `_SLICE_BRANCH_RE` non-match) would be silently dropped → misclassified orphan → false-refuse. Switching to the raw `_parse_worktree_porcelain` is correct. Per R-7 (fail-visible, never silently swallow).
- **M1** (CSP-1 exit-code parity): confirmed; Major appropriate. pulse_worktree_resolver.py:26-27 + L611 use exit 0/1/2; the design's original 0/2 broke sibling parity. Fix to 0/1/2 + widen bootstrap trigger to exit∈{1,2} is correct.
- **M2** (--merge/--push symmetry): confirmed; Major appropriate. The two surfaces (SKILL.md:167 merge pre-flight, SKILL.md:242 push pre-flight #2) are at structurally different positions; the byte-identical-block + FBCD-1 prose-parity-test disposition is sound.
- **M3** (bootstrap-fallback self-exclusion): confirmed; Major appropriate. The shipped SKILL.md:167 says "any non-current `slice/*` branches" but never writes the `git symbolic-ref --short HEAD` mechanism; the fix makes the legacy fallback's self-exclusion explicit.
- **m1** (ADR-081 reversibility wording), **m2** (for-each-ref format pin): both confirmed VALID at Minor.
- **MEPD-1** (changelog obligation): see Severity adjustments — the EXCLUDE *disposition* is defensible but I flag a reservation.

## Suspicious findings

No suspicious findings. Every first-Critic finding maps to a real, verifiable concern in the source. The first Critic did not over-reach on this slice.

## Missed findings

- **B-add-1** (Blocker — the B3 fix introduced a set-key mismatch): SKILL.md prose / design.md §Core design decision steps 2-4. `_parse_worktree_porcelain` (pulse_worktree_resolver.py:172-199) returns the `branch` field as the **raw refname** `refs/heads/slice/NNN-name` — the `refs/heads/` strip lives in `detect_active_worktrees` line 319 (`branch = branch_ref[len("refs/heads/"):]`), NOT in the parser. Design step 3 builds `all_slice_refs` from `for-each-ref --format='%(refname:short)'` = `slice/NNN-name` (short form). Step 4 computes `parallel_slices = all_slice_refs ∩ backed` and `orphan_branches = all_slice_refs − backed`. If `backed` holds raw `refs/heads/slice/...` strings while `all_slice_refs` holds short `slice/...` strings, **the intersection is always empty and the difference is always all-refs** → every worktree-backed peer is classified orphan → universal false-refuse, defeating the entire slice. This is precisely the B3 fix becoming a fresh defect (slice-078/082/083 pattern). **Proposed fix**: design must state explicitly that `classify_stale_branches` strips `refs/heads/` from each porcelain `branch` value (or normalizes both sets to short form) before the step-4 set operations, and the test `test_worktree_backed_slice_branch_is_allowed` must assert the *short-form* membership — otherwise the test will pass against a stub but fail against real porcelain (an APED-1 of its own). MUST be closed at /build-slice, not deferred.

- **M-add-1** (Major — path-equality self-exclusion normalization asymmetry on Windows): design.md §Core design decision steps 1-2 + §Authorization. Step 1 normalizes `current_path` via `git rev-parse --show-toplevel` + `\→/`. Step 2 compares against the porcelain `worktree` line value. On Windows these two git surfaces can differ in drive-letter case, 8.3 short-name vs long-name, and trailing separators. The current worktree is double-protected (branch-exclusion belt + path suspenders), so *self*-exclusion stays safe even if path-equality slips; the genuine gap is that the design relies on the branch-belt to cover a path miss without stating it as the load-bearing invariant. **Proposed fix**: design should pin that self-exclusion is correct IFF *either* path-equality OR current-branch-exclusion fires, and add a `test_current_slice_own_worktree_excluded_by_path` variant exercising a case/separator-mismatched current_path to prove the branch-belt covers it.

- **m-add-1** (Minor — empty-repo / zero-slice-branch / worktree-on-default edge cases unspecified): design.md §Error model + §Core design decision. The design covers orphan/parallel/stranded-complete/noncanonical-backed but does not state the verdict for: (a) zero `slice/*` refs (→ verdict allow, silent — correct but unstated); (b) a worktree on the **default branch** (doesn't match `refs/heads/slice/`, correctly ignored, unstated); (c) the main worktree block itself (must not count as backing any slice). All resolve correctly under the algorithm as written; the design should name them so the test suite covers the empty + default-branch cases. Specification-completeness gap, not a behavior defect.

## Severity adjustments

- **MEPD-1** (changelog EXCLUDE disposition): SEVERITY-OK on the finding, but a **reservation, not a reclassification**. EXCLUDE is defensible (no new RULE-ID; ADR-081 carries the decision). However, this slice *changes guardrail behaviour* (narrows the refusal set from all-non-current to worktree-less-only) — the EXCLUDE precedents (077/079/082/084/085/086/087) are mechanism/tool-shipping slices; this one alters a shipped guardrail's decision boundary. Do NOT escalate to INCLUDE — ADR-081 + the SKILL.md prose edit are the durable record and no RULE-ID changes — but the design should add one sentence to §MEPD-1 acknowledging the behaviour-boundary change is captured by ADR-081 (supersedes null) + the SKILL.md prose delta, so the EXCLUDE is "no-new-rule" rather than "no-behaviour-change." Documentation-precision adjustment, not a blocker.

## Notes

Confidence: high on B-add-1 — verified directly against pulse_worktree_resolver.py:172-199 (parser returns raw `refs/heads/` refname) and line 319 (strip lives in the caller). The first Critic's pattern in this slice is the inverse of over-reach: tight, accurate, correctly-severed findings, but it stopped at "switch to the raw parser" (B3) without tracing the raw parser's *output contract* into the downstream set operations — the slice-078/082/083 "fix-is-a-fresh-claim" blind spot. B-add-1 pairs naturally with B2's two-worktree fixture (the same fixture that proves backing also proves the strip). Verdict EXTEND (one Blocker + one Major + one Minor added; one severity-reservation noted).

Verified non-collisions:
- `tests/methodology/test_commit_slice_skill_merge_flag.py:131` anchors the LABEL "Stale-slice-branch check", NOT the message body — the byte-identical-prose change does NOT collide.
- `test_commit_slice_skill_merge_wt_clean_preflight_ordering.py:142-159` (pre-flight block must not contain `git status --porcelain`) — the new prose does not reintroduce it.
- `test_stranded_slice_audit.py:67-92` (`_make_bare_branch`/`_add_live_worktree`) — confirms R-26 worktree-less==stranded alignment.
