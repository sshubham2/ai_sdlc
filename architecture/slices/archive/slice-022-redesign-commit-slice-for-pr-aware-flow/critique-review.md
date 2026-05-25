# Critique Review: Slice 022 redesign-commit-slice-for-pr-aware-flow

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-14
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

## Summary

First Critic's 13 findings are substantively sound — the B2 squash-merge attack, B1 ff-only correction, B4 mutual-exclusion contract gap, and M3 EPGD-1 counter alignment all land. However, the dual-review pass surfaces FIVE missed findings, three of which are load-bearing: (1) a structurally impossible Pre-finish gate requirement that the Builder cannot satisfy without violating append-only; (2) the m2 fix-block was incomplete — the off-by-one counter exists at TWO sites and only one was corrected; (3) two count-drifts the first Critic missed (must-not-defer "12 items" vs actual 14; "22+ changed files" vs "19 enumerated"); (4) a `/drift-check` phantom-reference to a flag (`--do-commit`) that never existed; (5) edge cases in B2's Pass 2 fallback that warrant tightening (empty file-set vacuous-match; "covers FILES" ambiguity superset-vs-equal). One severity adjustment: m2 should be promoted to Minor-with-propagation (sub-Minor stays accurate but the un-propagated sibling is itself a separate finding). No suspicious findings — all 13 of the first Critic's findings are VALID.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- B1: `git pull` "fast-forward-only by default" is wrong — VALID; Blocker severity appropriate. design.md L105 fix (`git pull --ff-only`) + L178 error model row + mission-brief L67 must-not-defer + TF-1 row 12 all propagate correctly. Per Newman, *Building Microservices*: irreversible side-effects on shared mutable state must be explicit, never default-relied; first Critic applied this correctly.
- B2: `git cherry` patch-equivalence per-commit, not aggregate — VALID; Blocker severity appropriate. The mechanism table entry C+D fix at design.md L113-118 honestly documents the N>1-squash-merge limitation. Per Hendrickson, *Explore It!*: this is exactly the "happy-path-on-dominant-platform-failure-mode" exploratory catch class — first Critic's framing (squash-merge is the dominant GitHub PR-merge style) is calibrated correctly. See also missed-findings M-add-5 for residual Pass 2 edge cases.
- B3: GitHub URL pattern `github.com`-literal-only — VALID; Blocker filed correctly; DEFERRED disposition acceptable. ADR-020 L64 "Scope limitations (v1)" paragraph explicitly preserves Enterprise users' `gh pr create --web` fallback. Reviewing user item #10: the deferral does not undersell Enterprise UX as long as `gh` is configured for the Enterprise host. ADR-020's Reversibility section L76 marks this as a cheap follow-on widening. No second-pass concern.
- B4: Mutual exclusion + no-flag default unspecified — VALID; Blocker severity appropriate. AC #1 expansion + error model row at design.md L162 + TF-1 rows 3+4 + must-not-defer item 9 all in place. Per Wiegers, *Software Requirements*: argument-contract completeness is a Requirements-elicitation discipline — first Critic correctly elevated this from spec-gap (Major) to Blocker because three independent surfaces (AC, error model, test plan) all had the same gap.
- M1: Explicit fetch refspec — VALID; Major severity appropriate. design.md L94 `git fetch --prune origin <default> slice/NNN-<name>` is correct.
- M2: TF-1 row 14 transition spec — VALID; Major severity appropriate. mission-brief.md L46 expanded prose pins WRITTEN-FAILING → PASSING ordering against TF-1 audit `--strict-pre-finish`.
- M3: EPGD-1 counter alignment — VALID; Major severity appropriate. design.md L15 reads "EPGD-1 self-application N=8 → N=9 stable target" — matches v0.35.0 "N=7 → N=8 stable" anchor. Verified against methodology-changelog L54.
- M4: Re-push semantics — VALID; Major severity appropriate. design.md L170-171 adds 2 error model rows (non-ff diverged + ff re-push with prompt).
- M5: Signal A=YES + Signal B=NO diagnostic — VALID; Major severity appropriate. design.md L103 enumerates both causes.
- m1: Origin URL identity — VALID OVERRIDDEN. Per second-pass scrutiny of user item #9: the "user-reduced-vigilance" counter-argument has surface merit (skill scripts the push step), but is rebutted by the slice's explicit confirmation gates at L70 + must-not-defer item 11 (Explicit confirmation prompts) which arguably INCREASE vigilance vs raw `git push`. OVERRIDDEN holds with no second-pass adjustment.
- m2: BRANCH-1 self-application counter off-by-one — VALID at design.md L197; but see missed-findings M-add-2 for the un-propagated sibling site.
- m3: Files-changed enumeration — VALID at design.md L202+L226; but see missed-findings M-add-3 for inconsistent "22+ changed files" claim at L198 (different count-drift, same fix-block).
- m4: Worktree-conflict guard — VALID at design.md L180. Diagnostic propagation to `git worktree remove` resolution path is appropriate.

## Suspicious findings

No suspicious findings — all 13 of the first Critic's findings are independently validated by second-pass review. None warrant downgrading or dropping.

## Missed findings

Five concerns the first Critic did not flag that the meta-Critic surfaces from independent dimension re-application:

### M-add-1: Pre-finish gate L139 demands a structurally impossible "bidirectional supersession link per SUP-1" that mis-applies SUP-1 and would require violating append-only on ADR-019

- **Issue**: mission-brief.md L139 reads `[ ] ADR-020 cross-referenced from ADR-019 (supersession bidirectional link per SUP-1).` This is wrong on three independent counts:
  1. **SUP-1 applies to SLICE supersession, not ADR supersession**. Per methodology-changelog L629-647 (v0.19.0), SUP-1 is `/supersede-slice` for retiring archived slices via `**Supersedes**:` / `**Superseded by**:` reflection.md fields. ADR supersession uses frontmatter `supersedes:` (one-directional), and the entire ADR family (verified across ADR-001 through ADR-020) uses `supersedes: null` or `supersedes: <id>` — NEVER a `superseded-by:` field. The convention is structurally one-directional.
  2. **ADR-019 is explicitly NOT modified** per design.md L226: "ADR-019 is NOT modified (append-only respected; SUP-1's supersession link is encoded via ADR-020's `supersedes: ADR-019` frontmatter slot alone, which the new test `test_adr_020_file_exists_and_supersedes_adr_019` discovers)." So a Pre-finish gate that demands a "cross-reference from ADR-019" cannot be satisfied without violating append-only.
  3. **The mission-brief itself contradicts the design**. design.md L226 says one-directional encoding is correct; mission-brief.md L139 says bidirectional is required. These are contradictory load-bearing artifacts.
- **Framework**: Sommerville, *Software Engineering* — requirements consistency: contradictory acceptance criteria across artifacts at the same level (mission-brief vs design.md) is a Class-A specification defect. Wiegers, *Software Requirements* — verifiability: a gate that cannot be satisfied without violating a separately codified discipline (vault append-only) is unverifiable in principle.
- **Severity**: **Blocker**. The Builder will hit this at Step 6 pre-finish: either (a) modifies ADR-019 to satisfy the gate → violates append-only → /drift-check or SUP-1-by-confusion or audit failure; (b) leaves ADR-019 unmodified → Pre-finish gate L139 fails the check → cannot ship. There is no consistent build path.
- **Proposed fix**: rewrite mission-brief.md L139 to: `[ ] ADR-020's `supersedes: ADR-019` frontmatter slot is verified by test_adr_020_file_exists_and_supersedes_adr_019 (one-directional per ADR family convention; ADR-019 stays unmodified per append-only — SUP-1 does NOT apply because that rule scopes to /supersede-slice for archived-slice reflection.md links, NOT ADRs).` Also strike the parenthetical "(supersession bidirectional link per SUP-1)" entirely. Note: the Dependencies section mission-brief L95 says "supersession chain documented per SUP-1" — same mis-application; should also drop the SUP-1 reference there.

### M-add-2: m2 fix-block-completeness gap — "second non-bootstrap canonical-reference-instance" still exists at mission-brief.md L134 (one-site m2 fix; second sibling site un-propagated)

- **Issue**: m2 ACCEPTED-FIXED corrected design.md L197 from "second" → "first". But the EXACT SAME phrase still exists at mission-brief.md L134: `[ ] tools/branch_workflow_audit.py (slice-021) returns 0 violations against this slice's own /build-slice run (BRANCH-1 self-application — slice-022 IS the second non-bootstrap canonical-reference-instance after slice-021's bootstrap).` This is the **fix-block-completeness on count-drift** catch class (slice-020 M-add-1, slice-021 rerun-Critic catches × 4) — exactly what the user flagged as expected recurrence in slice-022.
- **Framework**: Wiegers regression-guard coverage-symmetry — a corrected counter must be propagated to every sibling site referencing the same claim. The first Critic's m2 framing was site-specific ("design.md L187") and did not search for sibling instances.
- **Severity**: **Minor** (matches m2's severity, but as a separate sibling finding so the fix gets logged).
- **Proposed fix**: change mission-brief.md L134 "second" → "first" to match design.md L197's corrected text.

### M-add-3: Count-drift between "22+ changed files" (design.md L198) and "19 enumerated touches" (design.md L202 + L226) — fix-block-completeness on m3

- **Issue**: design.md L198 reads: `**VAL-1**: 22+ changed files; standard Layer A + B sweep at /validate-slice Step 5b...`. But L202 says "Files changed (summary — total 19 enumerated touches + standard slice-lifecycle file updates)" and L226 says "Magnitude 19 enumerated touches matches reversibility=cheap tag." The "22+" claim is unanchored — it's not 19, not 19+standard-lifecycle (which would arguably be the same set), not the 19+3-new-extensions count, and the +3 SKILL.md mini-CAD edits are inside the 19 enumeration already. This is the same fix-block-completeness pattern as M-add-2 — m3 corrected the 15-28 placeholder to 19 enumerated but the L198 sibling claim retained the older "22+" estimate.
- **Framework**: Wiegers coverage-symmetry (count alignment across artifacts at the same slice level — N=9 watch-list at slice-021 ELEVATED to /critic-calibrate slice-022 per `_index.md` line 31+).
- **Severity**: **Minor**.
- **Proposed fix**: change design.md L198 from "22+ changed files" to "19 enumerated changed files" (consistent with L202 + L226). Alternatively, if "22" is the post-build-log + post-validation expanded count, explain the delta inline — but the simpler fix is alignment with L202/L226.

### M-add-4: mission-brief.md L131 `/drift-check` gate references a phantom `--do-commit` flag that never existed in the codebase

- **Issue**: mission-brief.md L131 reads: `[ ] /drift-check passes (no stale references to "--merge is the only post-/reflect cleanup mode" anywhere; no references to dropped --do-commit).` But `skills/commit-slice/SKILL.md` line 5 frontmatter shows `argument-hint: [--merge]` — there is no `--do-commit` flag in the current skill, nor in slice-021's flag set (slice-021 added `--merge`, not `--do-commit`). This is a phantom-flag reference inside a load-bearing pre-finish gate that the Builder is required to verify. `/drift-check` would either (a) report no stale `--do-commit` references because none ever existed (gate passes trivially — meaningless check), or (b) the Builder may misinterpret the gate and search for residual `--do-commit` references that never were.
- **Framework**: McGraw, *Software Security* — unverifiable / phantom security claims in audit gates train auditors to ignore the gate entirely (the boy-who-cried-wolf failure mode). Per Hendrickson, *Explore It!*: claims about prior-state behavior must be sourced.
- **Severity**: **Minor**. The gate is harmless (would pass vacuously) but is a Wiegers requirements-traceability defect — references something that has no upstream source.
- **Proposed fix**: change mission-brief.md L131 to drop the `--do-commit` parenthetical clause: `[ ] /drift-check passes (no stale references to "--merge is the only post-/reflect cleanup mode" anywhere).` Or replace `--do-commit` with an actual prior flag if the author meant something specific.

### M-add-5: B2 Pass 2 mechanism — three under-specified edge cases (empty-file-set vacuous match; "covers FILES" superset-vs-equal ambiguity; Pass 2 perf bound)

- **Issue**: design.md L99 specifies Pass 2 as: *"build the slice's full file-set `FILES=$(git diff --name-only BASE..slice/NNN-<name>)`; for each commit on `BASE..origin/<default>` check whether ANY single commit's full file-set diff matches the slice's aggregate tree-diff at `FILES` (i.e., search `origin/<default>` for a squash commit whose touched-file set covers `FILES` and whose end-state tree at those paths equals `slice/NNN-<name>^{tree}` at those paths)."* Three under-specifications surface:
  - **Edge case (a) — Empty `FILES` (vacuous-match false-YES)**: if slice net-changes nothing at FILES (e.g., file added then removed, or only intermediate-commit churn), `FILES=""` (empty set). The predicate "single commit's full file-set covers FILES" is vacuously true for ANY commit on default. → false-YES on Signal B Pass 2 → destructive `git branch -d` executes against a slice whose commits are NOT on default. The two-signal AND (with Signal A) saves us IF remote was deleted; but a user who manually deleted `origin/slice/...` without a real PR merge would hit destructive cleanup.
  - **Edge case (b) — "Covers FILES" superset-vs-equal ambiguity**: design.md says "touched-file set covers FILES". In set-theory "covers" typically means superset (touched ⊇ FILES). But GitHub squash-merges that include conflict-resolution may touch ADDITIONAL files (touched ⊃ FILES) — superset semantics correctly catches this. However, design.md doesn't pin which interpretation; a Builder implementing strict-equal (touched == FILES) would false-NO on conflict-resolved squash-merges. This is a contract-ambiguity inside a load-bearing predicate.
  - **Edge case (c) — Pass 2 perf bound undocumented**: design.md L118 mechanism table says "Pass 2 is O(commits on default since slice base) — bounded acceptably for typical repos" but doesn't specify what "typical" means, doesn't document a fallback / timeout if the scan exceeds N commits. For long-lived slice branches on busy default branches (e.g., a 6-week slice on a daily-merged default), N could be 100s-1000s of commits. No explicit perf-fallback in design.
- **Framework**: Hendrickson, *Explore It!* — boundary-condition exploration; per-commit aggregate-tree comparison is a fertile ground for boundary anomalies (empty set, superset vs equal, unbounded scan). Newman, *Building Microservices* — irreversible side-effects (`git branch -d` is data-loss-equivalent on uncommitted work) require defense-in-depth on the predicate that gates them.
- **Severity**: **Major** (edge case (a) is a data-loss failure mode that the two-signal AND only partially mitigates; (b) is a contract ambiguity; (c) is a perf-with-no-fallback gap).
- **Proposed fix**: add to design.md L99 explicit handling for three cases:
  - **Empty FILES guard**: `if FILES is empty → Signal B Pass 2 = NO (cannot determine merge state without files to compare; STOP with diagnostic "Slice has empty net file-set — `--sync-after-pr` cannot verify merge via Pass 2. Manually verify and use `git branch -D` only if confirmed.")`
  - **Pin "covers" to superset**: explicitly: "a squash commit whose touched-file set is a **superset** of `FILES` (allows conflict-resolution to touch additional files) and whose tree-state at the paths in `FILES` (intersection only) equals `slice/NNN-<name>^{tree}` at those paths."
  - **Perf bound**: "Pass 2 scan bounded to N=500 most recent commits on `BASE..origin/<default>`; if BASE is older than 500 commits back, STOP with diagnostic: 'Slice base too old for Pass 2 scan. Manually verify PR merge and cleanup.'" Or document the perf-fallback as the existing two-signal-must-agree-YES guard (the Signal A=YES + Signal B-Pass-2-not-conclusive case STOPs anyway).

## Severity adjustments

No severity adjustments to the first Critic's 13 findings — all severities are appropriately calibrated. The five missed findings (M-add-1 through M-add-5) carry their own severities as proposed above (1 Blocker + 1 Major + 3 Minor).

## Notes

Confidence in this review: **high**. Five independent missed findings surface from second-pass review, three of which directly match the recurrence classes the user explicitly queued for slice-022 elevated attention (fix-block-completeness on count-drift × 2; SUP-1 mis-application revealed by the partial-supersession encoding watchpoint). The other two (phantom `--do-commit` reference; Pass 2 edge cases) emerge from independent dimension re-application — `/drift-check`-gate verifiability and Hendrickson boundary-condition exploration respectively.

Calibration observation on the first Critic's pattern in slice-022: the Critic was tight on **mechanism correctness** (B1, B2, M4, M5 all caught real git-semantic errors) but loose on **propagation completeness** (m2 fix didn't propagate to mission-brief.md L134; m3 fix didn't sweep "22+ changed files" at design.md L198). This matches the slice-021 aggregated lesson "Fix-block-completeness on count-drift (DR-1 catch class candidate)" — the pattern is now N=2 at slice-021 and slice-022 if M-add-2 + M-add-3 are validated at user TRI-1 reconciliation, suggesting /critic-calibrate slice-022 elevation from "candidate" to "promote at N≥3" tracking (one more occurrence at slice-023 would meet the promotion threshold).

The M-add-1 SUP-1-misapplication finding is the highest-impact second-pass catch: a Pre-finish gate that contradicts the design's own append-only encoding would have surfaced as a Builder-vs-audit deadlock at Step 6, requiring an in-build redirect. Catching it at /critique-review saves one round-trip and validates the per-slice second-opinion role distinct from the cross-slice /critic-calibrate aggregation role.

Reservation: I did not verify the M-add-5 edge cases against an actual sandbox `git` execution; the empty-FILES vacuous-match argument is a set-theory inference and may not reproduce if git's `--name-only` returns a sentinel under net-zero-change. Builder should sandbox-verify before accepting M-add-5 as Major; if empirically the empty-FILES case STOPs git-naturally (e.g., diff returns nothing → predicate vacuously something), the severity may drop to Minor.
