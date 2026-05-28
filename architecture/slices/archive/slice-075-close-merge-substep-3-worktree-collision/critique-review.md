# Critique Review: Slice 075 close-merge-substep-3-worktree-collision

**Reviewed by**: critique-review agent (DR-1; subagent_type: critique-review; agent ID a64ef88ae368ec9aa)
**Date**: 2026-05-28
**First-Critic verdict**: NEEDS-FIXES

(Predicted CLEAN after TRI-1 ratifies all 6 ACCEPTED-FIXED in-band — 4 first-Critic dispositions M1+M2+m1+m2 + 2 meta-Critic missed-findings M-add-1+M-add-2 — but verdict-pattern is set by user-owned TRI-1 ratification at /critique Step 4.5 per TRI-1.)
**Dual-review verdict**: EXTEND

## Summary

The first Critic's four findings (M1, M2, m1, m2) are all VALID with correct severities and the Builder's fix-block dispositions are correctly propagated across all sibling sites in mission-brief.md + design.md (TPHD-1 sub-mode (a) sweep is clean — zero "≥75/75" / "row #75" / "2-bis" anchors remain outside critique.md's intended historical record; APED-1 verification of the canonical `awk` extraction returns the main-tree path correctly; shippability baseline empirically confirmed at 73 rows). However, the meta-Critic surfaces **two new RSAD-1 (recursive-self-application) findings** that the first Critic missed despite citing RSAD-1 in its own Dim 9 checklist: both the AC#2 (sub-assertion b) and AC#4 paired-pin assertions, as drafted, will PASS against the **current pre-fix SKILL.md** — violating the TF-1 WRITTEN-FAILING invariant the slice claims to honor.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **M1** (shippability-row arithmetic ≥75/75 → ≥74/74) — confirmed; severity Major appropriate; APED-1 verified via `$PY -m tools.shippability_runner architecture/shippability.md` → `73 row(s), 73 PASS, 0 FAIL`; Builder fix-block correctly swept AC#5 + Pre-finish gate row (mission-brief.md L121) + Verification plan row 5 (L43) + design.md §What's new (L15) + §Wiring matrix (L81) + §Audit/shippability propagation (L126) — N=5 surfaces, all consistent at `74` post-fix; zero residual "75" anchors.

- **M2** (AC#2 test scoping ambiguous; mandate `_step_5b_section()`) — confirmed; severity Major appropriate; APED-1 verified via `Grep "Pre-flight guardrails (run BEFORE any state change):"` → 3 occurrences at L166/L207/L242; Builder fix-block correctly added `_step_5b_section()` mandate at design.md L42, L50 + §What's reused L23 with explicit cross-module duplication trade-off (Fowler "Duplicated Code" with N=4 follow-on consolidation trigger documented).

- **m1** (sibling-but-distinct idiom not identical-form) — confirmed; severity Minor appropriate; APED-1 substring-check `"awk '/^worktree / {print $2; exit}'" in <sub-step-5-awk>` → False (verified); Builder fix-block correctly rephrased at mission-brief.md L47 + design.md §Decisions Question A (a) L93 + §What's reused (the "reuses sub-step 5's existing awk extraction" framing was removed and replaced with "SIBLING-BUT-DISTINCT idiom" language).

- **m2** (`2-bis` non-standard numeral → `2.1.`) — confirmed; severity Minor appropriate; rename swept across design.md §What's new + §Components touched + §Contracts added/changed (OLD/NEW ordering bullets, PSQ-3 re-entry semantics, sub-step 2.1. vacuous-on-re-entry) + §Decisions Question B (a) + §Error model row 1 + §Audit/shippability — zero `2-bis` residuals outside critique.md historical record; matches slice-073 `2.5.` PSQ-3 sibling-convention symmetry.

## Suspicious findings

No suspicious findings — all four first-Critic findings are legitimate and the Builder's in-band fix dispositions are correctly applied with zero false-positive over-reach.

## Missed findings

Two new RSAD-1 (recursive-self-application) findings surface from independent re-review. Both target the same defect class the first Critic invoked at its Dim 9 closure (`M2 catches phantom-citation-equivalent class … RSAD-1 recursive-self-application: M2 is exactly this class`) — but the first Critic stopped at M2's section-scoping concern and missed the deeper invariant: a structural-pin test must FAIL against the pre-fix SKILL.md per TF-1's WRITTEN-FAILING contract.

### M-add-1: AC#4 paired-pin assertion (`silent-WT-discard` + `STOP` + `Print:`) will PASS against pre-fix SKILL.md — violates TF-1 WRITTEN-FAILING

- **Severity**: Major
- **Issue**: design.md §Components touched L53 specifies AC#4's `test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent` asserts the Step-5b-section-scoped content contains `"silent-WT-discard"` (or `"local-state-loss"`) AND `"STOP"` AND `"Print:"` (or `'Print "'`). APED-1 verification on the CURRENT pre-fix `skills/commit-slice/SKILL.md` Step 5b section (L162-201): all four literals already present at L168 ("`closes silent-WT-discard local-state-loss path`" + "`If non-empty, STOP`" + "`Print:`"). The assertion as drafted will PASS at WRITTEN-FAILING stage → violates TF-1's contract that the test FAILS against pre-fix prose, then PASSES post-fix.
- **Framework**: RSAD-1 (recursive-self-application discipline; agents/critique.md Dim 9 sub-clause 6) + TF-1 (test-first WRITTEN-FAILING progression).
- **Why first Critic missed it**: the first Critic correctly invoked RSAD-1 at its dimensions-checked closure but applied it only to AC#2's section-scoping (the surface-level mistake); the deeper invariant — "the assertion must DISTINGUISH the post-fix-position WT-clean check from any pre-fix occurrence of the same literal" — was not checked. The mid-slice smoke gate in mission-brief.md L107-111 explicitly expects "BOTH FAIL with structural-pin assertion errors against current SKILL.md (per TF-1 WRITTEN-FAILING state)" — but the assertion as drafted will not satisfy that expectation, which would not surface until Phase B build (or worse, slip through if Builder doesn't notice the premature PASS).
- **Proposed fix**: anchor on the unique post-fix `2.1.` sub-step marker (pre-fix Step 5b has no `2.1.`). Tighten AC#4 to assert that within the contiguous block extracted via `two_one_pos = section.find("2.1."); two_five_pos = section.find("2.5.", two_one_pos); block = section[two_one_pos:two_five_pos]`, the literals `silent-WT-discard` (or `local-state-loss`) + `STOP` + `Print:` are present. Add explicit guard `assert two_one_pos != -1, "Step 5b section must contain a '2.1.' sub-step marker (post-fix prose required per /critique-review M-add-1)"` for clean WRITTEN-FAILING diagnostic. This makes the test FAIL pre-fix (no `2.1.` anchor exists) AND PASS post-fix (the lifted prose lives inside the new 2.1. block with all three intent literals preserved).
- **Builder draft**: ACCEPTED-FIXED in same fix-block (TPHD-1 sub-mode (b) — meta-Critic ACCEPTED-FIXED triggers same-block harmonization).

### M-add-2: AC#2 sub-assertion (b) `section.find('git status --porcelain', section.find('git commit')) != -1` will PASS against pre-fix SKILL.md via the PSQ-3 conflict-STOP block's pre-existing `git status --porcelain` — violates TF-1 WRITTEN-FAILING

- **Severity**: Major
- **Issue**: design.md §Components touched L52 specifies AC#2's sub-assertion (b) as `section.find('git status --porcelain', section.find('git commit')) != -1`. APED-1 verification: within current pre-fix Step 5b section, `git commit` appears at L173 (sub-step 2) AND `git status --porcelain` appears at L181 (PSQ-3 conflict-STOP enumeration block — the literal is pre-existing per slice-073 `test_step_5b_conflict_stops_with_porcelain_u_entries` rationale). So `section.find('git status --porcelain', section.find('git commit'))` resolves to L181's offset (>L173's offset for `git commit`), making the assertion PASS against pre-fix SKILL.md WITHOUT any new sub-step 2.1. having been inserted. The test passes whether or not the slice's prose surgery is applied.
- **Framework**: RSAD-1 + TF-1 + Wiegers (test independence — an assertion that doesn't FAIL pre-fix doesn't pin the fix).
- **Why first Critic missed it**: the first Critic correctly identified the 3-section pre-flight-header ambiguity (M2 sub-assertion a) and prescribed `_step_5b_section()` scoping — but did not run APED-1 on the (b) sub-assertion's `section.find('git status --porcelain', section.find('git commit'))` against the real pre-fix Step 5b section, missing that the PSQ-3 conflict-STOP block (slice-073 lineage) already satisfies the offset arithmetic.
- **Proposed fix**: same `2.1.` anchor strategy as M-add-1 fix. Replace AC#2 sub-assertion (b) with: (b) the `2.1.` sub-step marker MUST appear in Step 5b section (anchor unique to post-fix; pre-fix Step 5b has no `2.1.` — `assert two_one_pos != -1, "..."` for clean WRITTEN-FAILING); (c) the contiguous block from `2.1.` through `2.5.` MUST contain `git status --porcelain` (i.e., the lifted WT-clean check lives inside the new sub-step 2.1. block, not at any pre-existing site).
- **Builder draft**: ACCEPTED-FIXED in same fix-block.

## Severity adjustments

No severity adjustments — first Critic's M1/M2/m1/m2 severities are all appropriately filed.

## Notes

High-confidence review (verified empirically via APED-1 on the shippability runner, `git worktree list --porcelain` output, and Grep against the actual SKILL.md). The first Critic's coverage of the four surface defects (M1/M2/m1/m2) is sound and the Builder's fix-block sweep is clean — TPHD-1 sub-mode (a) regression hunting found zero new defects from the fix-block edits themselves (which preserves the N=7 cumulative baseline). The two missed findings are both in the same RSAD-1 family: the first Critic correctly invoked RSAD-1 at the dimensions-checked closure but applied it only to one surface (AC#2's section-scoping), missing that the test-assertion design must satisfy the deeper "FAIL against pre-fix prose" TF-1 invariant. This is a textbook RSAD-1 sub-mode (a) miss — the slice that authors test-first-pinning tests must itself satisfy test-first-pinning discipline against its OWN structural-pin assertions.

**Calibration signal**: this is the SECOND consecutive slice where the meta-Critic surfaces RSAD-1 assertion-strength misses missed by the first Critic (after slice-074); if it recurs at slice-076+, candidate for `/critic-calibrate` proposal to strengthen the agents/critique.md RSAD-1 sub-clause with explicit APED-1-against-pre-fix-prose enforcement language.

The proposed fixes are localized to design.md §Components touched §test functions (L52-53 specifically — tighten the two assertion shapes with `2.1.` anchor) with no cascade into mission-brief.md ACs or other design surfaces (test function names stay the same; assertion details change inside the function bodies). Safe to apply at TRI-1 triage.

Relevant file paths reviewed:
- `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/mission-brief.md`
- `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/design.md`
- `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/critique.md`
- `architecture/slices/slice-075-close-merge-substep-3-worktree-collision/milestone.md`
- `skills/commit-slice/SKILL.md` (L155-275; specifically Step 5b L162-201 + 3× pre-flight headers L166/L207/L242)
- `tests/methodology/test_commit_slice_skill_rebase_flag.py` (`_step_5b_section()` helper precedent)
- `tests/methodology/test_commit_slice_skill_merge_flag.py` (regression-baseline anchor `_step_5b_merge_section()`)
- `architecture/shippability.md` (73-row baseline empirically confirmed)
