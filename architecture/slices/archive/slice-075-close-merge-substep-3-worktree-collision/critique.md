# Critique: Slice 075 close-merge-substep-3-worktree-collision

**Critic reviewed**: mission-brief.md, design.md (no new ADRs introduced — MEPD-1 EXCLUDE per design.md §Decisions)
**Date**: 2026-05-28
**Critic agent**: `~/.claude/agents/critique.md` (subagent_type: critique; agent ID a1e1a6cf1faa0c689)
**Result**: CLEAN (post-TRI-1; user ratified all 6 ACCEPTED-FIXED in-band — 4 first-Critic dispositions + 2 meta-Critic missed findings)

## Summary

The intent (fixing two adjacent prose defects in Step 5b) is sound and minimally scoped. Two Major findings (one shippability-row-numbering arithmetic contradiction; one ambiguous test-scoping for AC#2) require resolution before /build-slice; two Minor findings on a misleading "canonical form matches sub-step 5" claim and a Markdown numbered-list rendering risk for the `2-bis` literal would improve robustness. All 4 findings VALIDATED — none FALSE-ALARM.

## Findings

### Blockers (must address before /build-slice)

None.

### Majors (address this slice)

#### M1: shippability-row count arithmetic contradicts itself — AC#5 says ≥75/75, design.md says +1 row but current catalog has 73

- **Claim under review**: mission-brief.md AC#5: `shippability runner ≥75/75 PASS`; design.md §Audit/shippability propagation: `architecture/shippability.md +1 row (row #75)`; design.md §What's new: `architecture/shippability.md +1 row (row #75): test_substep_3_includes_main_tree_transition_before_checkout as catalog representative`.
- **Issue**: APED-1 execution against the real catalog (`$PY -m tools.shippability_runner architecture/shippability.md`) reports `73 row(s), 73 PASS, 0 FAIL`. Slice-074 was MEPD-1 EXCLUDE+no-shippability-row per the source document; the highest existing row is 73. Adding "+1 row" produces 74 total → row #74, not #75. AC#5's "≥75/75" is internally inconsistent with the "+1 row" claim in design.md and would either (a) require adding 2 rows (contradicting design.md), or (b) fail the validate-slice gate when actual runner returns 74 not 75. Per slice-074 aggregated lesson "TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions stable at N=7" + "Scope-narrowing in design.md but mission-brief not back-propagated", this is a textbook stale-anchor sweep miss across the 4 sibling surfaces: AC#5 (mission-brief), design.md §What's new, design.md §Wiring matrix, design.md §Audit/shippability propagation.
- **Evidence**: `architecture/shippability.md` (highest row = 73); `$PY -m tools.shippability_runner architecture/shippability.md` empirical output `73 row(s), 73 PASS, 0 FAIL`; mission-brief.md AC#5 vs design.md §Audit/shippability propagation row-number divergence.
- **Proposed fix**: Decide arithmetically. Option (a) preferred: keep "+1 row" → rewrite AC#5 to `shippability runner ≥74/74 PASS` + rewrite design.md §What's new + §Wiring matrix + §Audit/shippability propagation to `row #74`. Option (b) rejected: adding a 2nd shippability row for AC#2 representative test contradicts §Wiring matrix exemption rationale "AC#2 is repositioning-not-introduction so AC#1's catalog row is sufficient". Stale-anchor sweep across mission-brief.md AC#5 + Pre-finish gate row + design.md (3 surfaces).
- **Builder draft**: ACCEPTED-FIXED in same fix-block (per TPHD-1 sub-mode (a)). Apply option (a) sweep across mission-brief.md AC#5 + mission-brief.md Pre-finish gate row + design.md §What's new + §Wiring matrix consumer entry-point cell + §Audit/shippability propagation.

#### M2: AC#2 test scoping is ambiguous — "Pre-flight guardrails block" matches 3 sections in SKILL.md (5b/5c/5d), risking either false-PASS or false-FAIL

- **Claim under review**: design.md §Components touched §test functions (AC#2 test): `test_wt_clean_preflight_does_not_contradict_substep_2_commit (AC#2): asserts Pre-flight guardrails block does NOT contain git status --porcelain (only Stale-slice-branch check); the literal git status --porcelain MUST still appear in Step 5b but at a position AFTER sub-step 2's git commit invocation (offset-comparison)`.
- **Issue**: The literal anchor `Pre-flight guardrails (run BEFORE any state change):` appears THREE times in `skills/commit-slice/SKILL.md` — at L166 (Step 5b `--merge`), L207 (Step 5c `--push`), and L242 (Step 5d `--sync-after-pr`). Steps 5c and 5d **legitimately still contain WT-clean pre-flight `git status --porcelain` checks** (L209 and L244 respectively) — and they SHOULD, because --push and --sync-after-pr have no commit step in their flows. The proposed test as drafted has no section-scoping specification; depending on the implementation, it will either (a) check the wrong "Pre-flight guardrails" block via `content.find()`-first-occurrence and produce false-PASS/FAIL, or (b) check whole-file and fail because 5c/5d still contain `git status --porcelain` in their pre-flight blocks. Per the slice-073 `_step_5b_section()` precedent (`test_commit_slice_skill_rebase_flag.py`), section-scoping MUST be explicit. APED-1 execution: `content.count("Pre-flight guardrails (run BEFORE any state change):") == 3` — confirmed.
- **Evidence**: `skills/commit-slice/SKILL.md` L166/L207/L242 (3 occurrences of identical pre-flight header); existing precedent `tests/methodology/test_commit_slice_skill_rebase_flag.py::_step_5b_section`.
- **Proposed fix**: design.md §Components touched §test functions for both AC#2 and AC#4 MUST specify: "section-scoped via `_step_5b_section()` helper modeled after `test_commit_slice_skill_rebase_flag.py`". Additionally, AC#2 assertion specification: rather than "Pre-flight guardrails block does NOT contain `git status --porcelain`", scope further to "the contiguous block from the literal `Pre-flight guardrails (run BEFORE any state change):` header through the blank line preceding `Then the 5-step merge flow:` MUST NOT contain `git status --porcelain`". AC#1 test specification correctly says "in Step 5b section" — sibling-site fix.
- **Builder draft**: ACCEPTED-FIXED in same fix-block. Update design.md §Components touched §AC#2 test + §AC#4 test specifications to explicitly cite `_step_5b_section()` helper (mirrors slice-073 precedent) + tighten AC#2 assertion to "Pre-flight guardrails block through blank line preceding 'Then the 5-step merge flow:'".

### Minors (log; address if cheap)

#### m1: Must-not-defer claim "canonical form matches Step 5b sub-step 5 + Step 5d sub-step 5 existing convention" is misleading — the proposed shape differs literally

- **Claim under review**: mission-brief.md Must-not-defer: `Main-tree resolution canonical form: git worktree list --porcelain | awk '/^worktree / {print $2; exit}' (matches Step 5b sub-step 5 + Step 5d sub-step 5 existing convention)`.
- **Issue**: APED-1 verification: the proposed extraction `awk '/^worktree / {print $2; exit}'` is NOT a substring of the existing sub-step 5 awk extraction `awk -v b="refs/heads/slice/NNN-<name>" '/^worktree / {p=$2} $0=="branch "b {print p; exit}'`. The two solve DIFFERENT problems: the proposed extraction returns the FIRST worktree (main tree, by git porcelain ordering — verified via web research: "The main worktree is listed first, followed by each of the linked worktrees" per git-scm.com/docs/git-worktree); the existing sub-step 5 extraction returns the path for a SPECIFIC branch. They share the `/^worktree /` regex anchor but the AWK action differs. The Must-not-defer claim presents them as identical-form, when they are sibling-but-distinct idioms.
- **Evidence**: APED-1 Python execution substring-check: `"awk '/^worktree / {print $2; exit}'" in "awk -v b=...{print p; exit}'"` → `False`. WebSearch confirmation: git-scm.com/docs/git-worktree — main worktree always listed first in porcelain output.
- **Proposed fix**: rephrase Must-not-defer line to: `Main-tree resolution canonical form: git worktree list --porcelain | awk '/^worktree / {print $2; exit}' (extracts first-listed worktree = main tree per git porcelain ordering invariant; SIBLING-BUT-DISTINCT idiom from Step 5b sub-step 5 + Step 5d sub-step 5 which extract a SPECIFIC-branch worktree path; shared regex anchor /^worktree / with divergent AWK action because divergent semantics)`. Same correction at design.md §Decisions Question A (a) which references "reuses sub-step 5's awk extraction" — that phrasing also misleads.
- **Builder draft**: ACCEPTED-FIXED in same fix-block. Apply at mission-brief.md Must-not-defer + design.md §Decisions Question A (a) + design.md §What's reused (the bullet "reuses sub-step 5's existing `git worktree list --porcelain | awk ...` extraction shape" also misleads).

#### m2: Sub-step "2-bis" non-standard numeral may break Markdown numbered-list rendering

- **Claim under review**: design.md §Components touched §skills/commit-slice/SKILL.md: `Insert new sub-step 2-bis (post-commit WT-clean guardrail) between sub-step 2 (L172-173) and sub-step 2.5 (L174)`.
- **Issue**: The existing PSQ-3 sub-step uses the decimal `2.5.` literal as its Markdown list marker (L174 starts `2.5. **Rebase slice branch onto default**...`). A literal `2-bis` is not a recognized Markdown numbered-list marker — it will render as bold/italic prose, NOT as a list item, breaking the visual ordered-list flow between sub-step 2 (L173) and sub-step 2.5 (L174). The PSQ-3 precedent for inserting an intermediate sub-step between integer steps was decimal `N.M`. A `2-bis` literal also creates sibling-convention asymmetry vs slice-073 `2.5.` shape.
- **Evidence**: `skills/commit-slice/SKILL.md` L174 (`2.5.` decimal marker); CommonMark spec on ordered-list markers (digits-then-`.` or digits-then-`)`).
- **Proposed fix**: rename "sub-step 2-bis" to "sub-step 2.1." throughout mission-brief.md (Must-not-defer references) + design.md (§What's new, §Components touched, §Contracts added/changed, §Decisions Question B, §Error model row 1). Single rename, sweep across 4-6 sibling sites — preserves Markdown list rendering + sibling convention symmetry with `2.5.`. Per slice-073 aggregated lesson on stale-anchor sweep, the rename must be propagated atomically across all surfaces.
- **Builder draft**: ACCEPTED-FIXED in same fix-block. Apply rename "2-bis" → "2.1." across all 5-6 sibling sites in design.md (mission-brief.md doesn't currently mention "2-bis" — verified). Stale-anchor sweep: §What's new + §Components touched (skills/commit-slice/SKILL.md edit surface) + §Contracts added/changed (OLD/NEW pre-flight ordering bullets, PSQ-3 re-entry semantics bullet) + §Decisions Question B option (a) + §Error model row 1.

## Dimensions checked

- [x] Unfounded assumptions — m1 (Must-not-defer's "matches existing convention" claim is misleading per APED-1 substring check); design.md §Decisions Question A (a) inherits same misleading framing.
- [x] Missing edge cases — none. Design correctly identifies (i) PSQ-3 re-entry vacuous-on-clean-WT, (ii) main_tree resolution failure STOP, (iii) cd failure STOP, (iv) sub-step 5 awk still works post-cwd-change. Minor terminology slip on §Error model row 3 ("cd is shell builtin not git command; stderr would be shell-level") not worth a finding.
- [x] Over-engineering — none. Slice scope appropriately minimal; design.md §Decisions explicitly declines (b) `git -C "$main_tree"` heavier rewrite + (c) worktree-tear-down-first reshuffle + AC#6 meta-AC (good carve-out reversion).
- [x] Under-engineering — none on AC coverage. M1 above is technically under-engineering on shippability-row coverage symmetry, but tagged Major because arithmetic contradiction not missing element. Methodology-audit conformance: all 4 TF-1 rows have credible WRITTEN-FAILING signal.
- [x] Contract gaps — none. New behavior contract well-specified at design.md §Contracts (old vs new ordering + 3 STOP paths). Error model enumerated. PSQ-3 re-entry semantics explicitly confirmed preserved.
- [x] Security — N/A — skill-prose surgery only, no new authn/authz/data-exposure paths.
- [x] Drift from vault — none on ADR contradiction; design.md correctly cites ADR-063 sub-step 5 order-load-bearing (preserved), ADR-068 §Re-entry semantics (preserved), ADR-020 §3-mode taxonomy (preserved). MEPD-1 EXCLUDE sub-mode (b) "documented-why-none path" — verified no PMI-1 bump needed. M2 above is technically drift-from-existing-test-convention finding (slice-073 `_step_5b_section` precedent not named) but tagged Major because risks structurally-ambiguous tests.
- [x] Web-known issues — WebSearch verified: `git worktree list --porcelain` main-worktree-first ordering is documented invariant per git-scm.com/docs/git-worktree; proposed `awk '/^worktree / {print $2; exit}'` extraction structurally sound. No platform-version restrictions / deprecations relevant.
- [x] Cross-cutting conformance — TPHD-1 sub-mode (a) catches M1 stale-anchor cross-file (AC#5 vs design.md row-count). M2 catches phantom-citation-equivalent class. APED-1 execution discipline applied at m1 (substring-check Python execution) + M2 (count of header occurrences in real SKILL.md). RSAD-1 recursive-self-application: M2 is exactly this class (slice authoring section-pinning tests proposes them WITHOUT section scoping, the very discipline they encode). PTFCD-1: new test files don't exist on disk yet but slice creates them in Phase B per TF-1 — verified slice's own plan creates them, not phantom. SCPD-1: 1 shippability row propagated (modulo M1 arithmetic).

Sources cited by Critic:
- [Git - git-worktree Documentation](https://git-scm.com/docs/git-worktree) — confirms main worktree always listed first in porcelain output; documents `branch -d` refuses on checked-out branch (already cited in ADR-063).

## Triage

**Triaged by**: user
**Date**: 2026-05-28
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | Fix applied in same fix-block; 5-surface sweep across mission-brief.md AC#5 + Pre-finish gate row + Verification plan row 5 + design.md §What's new + §Wiring matrix + §Audit/shippability propagation; row #75 → row #74; ≥75/75 → ≥74/74 (empirical baseline 73 confirmed via `$PY -m tools.shippability_runner architecture/shippability.md`) |
| M2 | Major | ACCEPTED-FIXED | Fix applied in same fix-block; `_step_5b_section()` helper mandate added at design.md L42 + L50 + §What's reused L23 with explicit cross-module duplication trade-off documented (N=4 follow-on consolidation trigger) |
| m1 | Minor | ACCEPTED-FIXED | Fix applied in same fix-block; rephrased Must-not-defer at mission-brief.md L47 + design.md §Decisions Question A (a) L93 + §What's reused — sibling-but-distinct idiom framing (shared `/^worktree /` anchor + divergent AWK action) |
| m2 | Minor | ACCEPTED-FIXED | Fix applied in same fix-block; "2-bis" → "2.1." rename swept across design.md §What's new + §Components touched + §Contracts added/changed + §Decisions Question B (a) + §Error model row 1 + milestone.md (mirrors PSQ-3 sub-step 2.5 sibling-convention symmetry; CommonMark ordered-list compliant) |
| M-add-1 | Major | ACCEPTED-FIXED | Per /critique-review meta-Critic MISSED finding; fix applied in same fix-block per TPHD-1 sub-mode (b); AC#4 paired-pin tightened to `2.1.` block-anchored extraction with prelude guard `assert two_one_pos != -1` at design.md L53 — previously whole-section presence-check would PASS pre-fix (L168 already has all 3 intent literals) violating TF-1 WRITTEN-FAILING |
| M-add-2 | Major | ACCEPTED-FIXED | Per /critique-review meta-Critic MISSED finding; fix applied in same fix-block per TPHD-1 sub-mode (b); AC#2 sub-assertion (b) tightened to `2.1.` literal + block-scoped `git status --porcelain` presence at design.md L52 — previously offset-comparison would PASS pre-fix via L181 PSQ-3 conflict-STOP block's pre-existing `git status --porcelain` |
