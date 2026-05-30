# Critique Review: Slice 086 harden-agent-spawn-skills-await-real-output

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-30
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

> Provenance: produced by the `critique-review` subagent (Agent tool, `subagent_type: "critique-review"`) — NOT main-thread self-review (per the R-25 guard this slice installs).

## Summary

The first Critic's review is strong on factual verification — B1, B2, M1, M2, M3 are all VALID with correct severities, and the Builder's fix-deltas landed correctly and accurately on disk. But the first Critic missed one real gap: the pin test as specified is **file-global presence + uniqueness only**, with no scoping to the Step 2→Step 3 seam where the guard is load-bearing — even though the design explicitly claims to reuse the SOAD-1 precedent's section-scoped pattern. That is both a coverage gap and an internal design inconsistency.

## Confirmed findings

- **B1** (phantom `test_critique_skill_drift.py`) — confirmed VALID; Blocker severity appropriate. Independently verified: `Glob tests/methodology/test_*skill_drift*.py` returns build_slice, commit_slice, query_design, slice, adopt, triage, reflect, code_review, pulse — **no critique drift test**. The Builder's fix landed: mission-brief AC-3 and design.md "What's reused"/"Components touched" now correctly state critique has no drift test and AC-2's pin is its sole guard. Fix correct and complete.
- **B2** (code-review absent from CLAUDE.md:42 OSDG-1 set) — confirmed VALID; Blocker severity appropriate. Independently verified: CLAUDE.md:42 names `{slice, build_slice, commit_slice, query_design, critique, diagnose, triage, adopt, reflect}` — `code-review` is absent despite `test_code_review_skill_drift.py` existing, and `critique` is named but has no drift-test file. Bidirectional inventory drift confirmed exactly as B2 states. Builder fix landed at design.md + ADR-078 §Context; the inventory drift correctly logged as out-of-scope follow-up `reconcile-osdg-1-inventory-claude-md-L42`. Fix correct and complete.
- **M1** (dash-codepoint drift) — confirmed VALID; Major appropriate. Builder fix landed: mission-brief AC-1 and design.md now pin U+2014 explicitly with the "NOT U+002D, NOT U+2013" annotation and a build-time APED-1 byte-exact check. Correct.
- **M2** (heading-only pin lets a gutted body pass) — confirmed VALID; Major appropriate. Builder fix landed: AC-2 now pins two literals — heading + `NEVER self-author a placeholder`. **Item (d) independently checked and CLEARED**: grep for `self-author`, `placeholder`, `acknowledgment`, `task-notification`, `deliverable` across all three target SKILL.md files returns zero hits today — the chosen body literal is genuinely unique-to-invocation, and the design's build-time uniqueness check correctly guards future collision. This does NOT reproduce the slice-085 false-negative class. The first Critic's M2 fix is sound.
- **M3** (canonical literal absent from AC-1) — confirmed VALID; Major appropriate. Builder fix landed at mission-brief AC-1 — the literal is now present verbatim with the codepoint annotation. Correct.

Insertion-point citations (L99/L75/L140) independently VALIDATED accurate: all three correspond exactly to the "Return the agent's complete ... content" lines immediately before each skill's "Step 3" write. The first Critic's validation here holds.

## Suspicious findings

No suspicious findings. Every first-Critic finding is confirmed against disk; none over-reached.

## Missed findings

- **M-add-1: The pin test is file-global, not seam-scoped — a guard relocated out of the Step 2→Step 3 boundary stays green while becoming inert.** AC-2 and design.md specify the test asserts the two literals are "present once in each of the three SKILL.md files" — file-global presence + a uniqueness count. But AC-1 makes the guard's *placement* load-bearing: "at the spawn→write boundary (the Step 2 → Step 3 seam)." A file-global+unique pin passes if a future edit MOVES the guard block (e.g. into the template/footer section, or above Step 2) — the literal still appears exactly once, the test stays green, but the main thread no longer reads it inline at the spawn→write decision point, silently re-opening R-25 by relocation rather than deletion. Per Hendrickson (*Explore It!*, test-the-invariant-not-the-incidental) and the slice's own cited precedent: design.md explicitly claims to reuse SOAD-1's "**section-scoped assertions**," and `test_soad1_structured_options_ask_rule.py:13-16,55-70` exists *specifically* because "a repo-global `.count()` would pass even if both hits landed in the [wrong block]" (its `_fenced_block_after` helper scopes every assert to the correct section). The new test as specified discards that exact lesson while citing it as the model — an internal design inconsistency (the "What's reused" claim of section-scoping is not honored by the test spec). **Proposed fix**: scope the pin to the Step 2→Step 3 region of each SKILL.md (locate the "Step 2"/"Step 3" headings, assert both literals fall between them), mirroring the SOAD-1 `_fenced_block_after` pattern; reconcile design.md and mission-brief AC-2 so the spec matches the "section-scoped" claim. Severity: **Major** — same defect class (silently-green guard re-opening R-25) the first Critic correctly rated Major for M1/M2; placement-drift is one more path to it.

## Severity adjustments

No severity adjustments. B1/B2 as Blockers, M1/M2/M3 as Majors, m1/m2 as Minors are all correctly calibrated.

## Notes

High confidence in this review. The first Critic's factual verification (B1/B2) was rigorous and independently reproduces against disk; its calibration pattern in this slice is sound — no over-reach, no severity miscalibration, and the two-literal M2 fix correctly internalizes the slice-075/085 narration-collision lesson, which item (d) confirms is genuinely cleared. The one blind spot is dimensional: the first Critic verified the literals' *identity* (dash, uniqueness, presence) thoroughly but did not test their *placement*, even though placement is what makes the guard work and the cited precedent (SOAD-1) is built entirely around section-scoping. One reservation on M-add-1: it is a pre-build design slice, so a build-time reading might argue the Builder could scope the test correctly without a spec change — but the spec as written (file-global + the internal contradiction) invites the inert-relocation footgun, so I file it as a real finding for TRI-1 rather than leaving it to Builder discretion. Builder should confirm whether seam-scoping is intended; if so, harmonize AC-2 and design.md to match the "section-scoped assertions" claim.
