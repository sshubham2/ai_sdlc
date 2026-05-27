# Critique Review: Slice 073 add-rebase-and-conflict-discipline

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-28
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

First Critic correctly identified the dominant FBCD-1 sub-mode (a) cross-doc harmonization cluster (14 of 16 findings on one root cause) and the 5 independent design-shape concerns (M1/M2/M3/M4/M6 + M5). All 16 findings confirmed VALID with correct severities. The meta-Critic surfaces **6 missed findings** the first Critic + Builder fix block both missed — 2 Major (M-add-1 + M-add-2) + 4 minor (m-add-1 through m-add-4). M-add-1 (M4 sweep regression — two ADR-068 surfaces still carry slice-064 appeals) and M-add-2 (M1 fix introduces SKILL.md-line citation error) are Builder-fix-block-introduced regressions — empirically extending the aggregated-lessons "N=6 cumulative Builder fix block introduces N+1 regressions" pattern to **N=7 cumulative** on this slice. All 6 missed findings ACCEPTED-FIXED in-band before TRI-1.

## Confirmed findings (first-Critic)

All 16 first-Critic findings VALID + correct severity:

- **B1** (Blocker): PTFCD-1 phantom test-file directory — VALID; filesystem-verified no `tests/skills/commit_slice/`.
- **B2** (Blocker): AC3 design-narrowing not back-propagated — VALID; design.md L156 + ADR-068 §Options-#3 explicitly eliminate audit-tool module.
- **B3** (Blocker): AC1 scope contradiction `--merge` vs `--sync-after-pr` — VALID; design.md §Scope-narrowing + ADR-068 §Options-#2 narrow to `--merge` only.
- **B4** (Blocker): Must-not-defer items presuppose audit module — VALID; same root cause as B2.
- **B5** (Blocker): Paired-pin name divergence `_in_changelog` vs `_in_repo` — VALID; existing convention is `_in_repo` (51 instances in `test_methodology_changelog.py`).
- **B6** (Blocker): ADR-068 filename divergence — VALID; slice-072 `mint-psq-2-…` pattern establishes convention.
- **M1** (Major): Worktree-vs-main-tree collision unaddressed at design time — VALID; but Builder fix introduces citation error (see M-add-2 below).
- **M2** (Major): Conflict-STOP re-entry semantics undefined — VALID; Builder fix exhaustive across 3 SOAD-1 options.
- **M3** (Major): Mid-skill SOAD-1 invocation precedent unjustified — VALID; Builder fix has off-by-one count claim (see m-add-1 below).
- **M4** (Major): Slice-064 precedent claim misleading — VALID; Builder fix INCOMPLETE (see M-add-1 below).
- **M5** (Major): Verification plan row 3 cites stale audit invocation — VALID; same root cause as B2.
- **M6** (Major): ADR-068 option (c) operational path undefined — VALID; Builder fix specifies the path.
- **m1** (minor): Risk-retired rhetorical overshoot — VALID.
- **m2** (minor): Mid-slice smoke gate stale audit invocation — VALID.
- **m3** (minor): Pre-finish gate "14+" loose count — VALID.
- **m4** (minor): 5-7 test-name enumeration absent — VALID; Builder fix enumerates 5 tests at design.md L11 + L38-43 + mission-brief test-first plan.

## Suspicious findings

None. Every first-Critic finding survives second-pass scrutiny.

## Missed findings (meta-Critic adds)

### M-add-1 (Major): M4 fix-block sweep INCOMPLETE — two ADR-068 surfaces still carry the slice-064 precedent appeal

- **Claim under review**: ADR-068 L29 Pros bullet ("structural-pin precedent (slice-064 NAW-1 union-of-three-sources extension to /code-review used this exact shape — no new tool, structural pins only)") + ADR-068 L53 Decision § ("This mirrors slice-064's in-family-extension precedent ... no new tool, structural pins only").
- **Issue**: M4's proposed fix explicitly called for "replacing the slice-064 precedent appeal with the actual rebase-specific argument." Builder substituted at design.md L156 (clean — fully rebase-specific) but left BOTH parallel ADR-068 sites stale. Per M4's own analysis: slice-064 "mints no new rule; supersedes nothing" (ADR-062) — a scope-extension applying NAW-1 to a new surface, NOT a new-rule mint with no new tool. PSQ-3 IS a new-rule mint; the apples-to-apples precedents (PSQ-1 / PSQ-2) BOTH minted tool modules. L29 + L53 reproduce the exact unfounded-precedent claim M4 retired. Textbook TPHD-1 sub-mode (a) sweep regression — the dominant first-Critic cluster (B1-B6 + M5 + m2 = 8 instances) co-occurred with a same-class N+1 regression in the Builder's M4 fix block. Cumulative pattern extends to N=7 (slice-062/064/067/070/071/072 + slice-073).
- **Evidence**: ADR-068 L29, L53; design.md L156 (correct rebase-specific argument); ADR-062 + slice-064 reflection (no rule mint, scope-extension).
- **Proposed fix**: Replace both ADR-068 surfaces with the rebase-specific argument that landed at design.md L156 — `git rebase` IS the runtime gate (no-op at-tip / clean exit 0 when behind without conflict / non-zero with U-prefixed conflicts); an audit-tool would duplicate `git rebase`'s own behavior; structural pins on SKILL.md prose mirror the existing `test_commit_slice_skill_merge_flag.py` no-ff precedent.
- **Builder draft**: ACCEPTED-FIXED at ADR-068 L29 + L53.

### M-add-2 (Major): design.md L100 (M1 fix) misattributes the worktree-collision STOP path to SKILL.md L259

- **Claim under review**: design.md L100 — "The existing worktree-vs-main-tree collision STOP at `skills/commit-slice/SKILL.md:259` (which fires when `<default>` is checked out in another worktree, typically the main tree) still applies post-rebase and is the correct error surface for that case."
- **Issue**: SKILL.md L259 is the `--sync-after-pr` STOP path, NOT the `--merge` STOP path. There is NO equivalent explicit `--merge` Step 5b STOP path for the `git checkout $default`-collides-with-main-tree case — only `--sync-after-pr` Step 5d has the explicit STOP-with-diagnostic. The M1 fix's claim that "the existing STOP path at SKILL.md L259 still applies" is doubly broken: (a) the line is on a different sub-mode (Step 5d vs Step 5b); (b) the `--merge` checkout failure case in Step 5b sub-step 3 currently surfaces only via git's own non-zero exit (no explicit Step 5b STOP-with-diagnostic on this case). This is a Builder-fix-block-introduced regression — the M1 fix cited a SKILL.md line without verifying the cited line referred to the correct sub-mode. The fix's substance (rebase preserves worktree-checkout, doesn't add new edge case) is correct; only the cited-line reference is wrong.
- **Evidence**: skills/commit-slice/SKILL.md L259 (`--sync-after-pr` STOP); skills/commit-slice/SKILL.md L170-184 (`--merge` flow has no equivalent explicit STOP); design.md L100 (the misattribution).
- **Proposed fix**: Restate the M1 paragraph to acknowledge the asymmetry: `--sync-after-pr` Step 5d sub-step 5 has an explicit worktree-collision STOP at SKILL.md L259; `--merge` Step 5b sub-step 3 currently does NOT have an equivalent explicit STOP — it surfaces via git's own non-zero exit. PSQ-3 preserves this asymmetry (doesn't introduce a STOP); the rebase invocation does NOT change the existing `--merge` flow's checkout-failure surface.
- **Builder draft**: ACCEPTED-FIXED at design.md L100.

### m-add-1 (minor): design.md L104 says "five confirmation sites" but SKILL.md has six raw `(yes/no)` sites

- **Claim under review**: design.md L104 — "the existing `--merge` / `--push` / `--sync-after-pr` flows use raw `(yes/no)` confirmation prompts at all five confirmation sites."
- **Issue**: Grep of `skills/commit-slice/SKILL.md` for `(yes/no)`: 6 matches at L173, L175, L202, L203, L205, L255. design.md L104 count is off-by-one. Does not change M3 substance; only the count claim.
- **Evidence**: Grep result on SKILL.md; design.md L104.
- **Proposed fix**: Change "five confirmation sites" to "six confirmation sites" (count-verifiable).
- **Builder draft**: ACCEPTED-FIXED at design.md L104.

### m-add-2 (minor): design.md L158 stale post-/critique prose

- **Claim under review**: design.md L158 — "Both narrowings are open to /critique review; the user-input gate is `/critique`'s adversarial pass, which can push back if either narrowing turns out to be wrong."
- **Issue**: /critique has run; both narrowings have been reviewed (B2 + B3 ACCEPTED-FIXED with the narrowings preserved). The "open to /critique review" tense is now stale. FBCD-1 sub-mode (a) state-anchor drift.
- **Evidence**: design.md L158; critique.md (B2 + B3 dispositions).
- **Proposed fix**: Rewrite to past tense — "Both narrowings were reviewed at /critique (B2 + B3 ACCEPTED-FIXED via mission-brief back-propagation; design narrowing preserved post-meta-Critic)."
- **Builder draft**: ACCEPTED-FIXED at design.md L158.

### m-add-3 (minor): ADR-068 L37 N=10 vs 11-item enumeration off-by-one

- **Claim under review**: ADR-068 L37 §Options-#5 — "Inclusion-heuristic firing on new-mechanism slices is N=10 cumulative — slice-049/050/051/057/058/059/060/063/064/067/072 precedent".
- **Issue**: Enumeration has 11 items (049, 050, 051, 057, 058, 059, 060, 063, 064, 067, 072); count says N=10. ADR-068 L91 §Inclusion-heuristic posture cites the same 11-item enumeration as N=11. L37 N=10 is the off-by-one.
- **Evidence**: ADR-068 L37 (N=10 claim); ADR-068 L91 (N=11 claim with same enumeration); 11-item count verifiable by direct enumeration.
- **Proposed fix**: Change L37 N=10 → N=11 to match L91 + actual enumeration.
- **Builder draft**: ACCEPTED-FIXED at ADR-068 L37.

### m-add-4 (minor): design.md "fast-forward no-op" framing inverted at L83-84

- **Claim under review**: design.md L83-84 — "**Fast-forward no-op**: default is already at slice's merge-base (the common case when the second-to-merge slice hasn't conflicted with a recently-merged peer); proceed to sub-step 3."
- **Issue**: The "second-to-merge slice hasn't conflicted with a recently-merged peer" case is precisely when default HAS advanced past slice's branch-point; in that case, a clean (non-conflicting) rebase replays slice's commits onto the new default tip — that's a clean rebase, NOT a fast-forward. The actual fast-forward no-op case is when default has NOT advanced (i.e., slice's branch-point IS default's tip). The framing conflates the two clean-exit paths. Documentary only — structural-pin tests don't verify this prose.
- **Evidence**: design.md L83-84; `git rebase` semantics (per git-scm.com docs).
- **Proposed fix**: Split into two outcome paths — `**Fast-forward no-op**: default has not advanced since slice's branch-point; git rebase exits 0 without replay. **Clean replay**: default has advanced but slice's commits replay cleanly atop the new default tip (the common second-to-merge case). Either path: proceed to sub-step 3.`
- **Builder draft**: ACCEPTED-FIXED at design.md L81-84.

## Severity adjustments

None. All 16 first-Critic findings filed at appropriate severities.

## Notes

**Calibration observation**: First Critic correctly anticipated TPHD-1 sub-mode (a) sweep risk and called it the dominant cluster (14/16 findings). Builder applied a single fix block per "TPHD-1 sub-mode (a) discipline" claim. Despite this discipline, the M4 sweep regressed at the predictable failure mode (two ADR-068 sites stale; design.md sole site clean) — empirically confirming the aggregated-lessons N=6 cumulative pattern "Builder fix blocks introduce N+1 regressions in the same class" on this slice, extending it to **N=7 cumulative**. M1's citation error (M-add-2) is a separate, simpler defect class: the Builder cited a SKILL.md line without verifying the cited line referred to the correct sub-mode — a Read-tool spot-check would have caught it. `/critic-calibrate` proposal target (post-slice-073 nomination): add an explicit "post-fix-block grep -n on the precedent name OR audit anchor across all 3 surfaces (mission-brief + design + ADR)" step to the Builder fix-block discipline. The grep would have caught M-add-1 in seconds; the Read-spot-check would have caught M-add-2 likewise.

**Reservation on M-add-2**: severity-borderline Major. If the Builder's intent was that the M1 paragraph SHOULD acknowledge an asymmetry (no Step 5b explicit STOP today, PSQ-3 doesn't introduce one), then the framing is acceptable but the prose needs to make the asymmetry explicit rather than asserting the L259 STOP "still applies post-rebase" to a sub-mode where it does not structurally apply. Builder's proposed fix above takes this interpretation.
