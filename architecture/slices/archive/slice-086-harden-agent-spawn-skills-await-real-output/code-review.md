# Code Review: Slice 086 harden-agent-spawn-skills-await-real-output

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-30
**Result**: FINDINGS (1 Minor — ACCEPTED-FIXED in-slice; user-elected)

> Provenance: produced by the `code-review` subagent (Agent tool, `subagent_type: "code-review"`) — NOT main-thread self-review (per the R-25 guard this slice installs). v1 advisory: does NOT block `/validate-slice`.

## Summary

A tight, well-scoped slice. The guard block is byte-identical across all three skills (U+2014 dash confirmed at 0x2014 in all four files including the test CANON), the operative literals (`self-author`/`placeholder`) have zero narration collisions, and the seam-scoped pin test genuinely has teeth — the code-Critic empirically mutated a real skill four ways (delete / relocate-out-of-seam / gut-body / em-dash→hyphen) and the test failed on all four while passing unmutated. All five ACs verified against disk. One Minor: the region extractor `_step2_to_step3_region` uses unanchored substring matching that is robust for the three current files but latently fragile for future skills.

## Changed files (in-scope)
skills/critique/SKILL.md
skills/critique-review/SKILL.md
skills/code-review/SKILL.md
tests/methodology/test_r25_await_real_agent_guard.py
architecture/slices/slice-086-harden-agent-spawn-skills-await-real-output/build-log.md

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

None. (The four highest-risk failure modes flagged in the review brief were all checked by execution, not inspection, and all held — see "Verification performed".)

### Minors

#### m1: `_step2_to_step3_region` uses unanchored substring `.find()` — false-negative risk for future skills with `### Step 2`-prefix narration or `### Step 20`
- **Claim under review**: `tests/methodology/test_r25_await_real_agent_guard.py:67-69`
  ```python
  start = content.find("### Step 2")
  ...
  end = content.find("### Step 3", start)
  ```
- **Issue**: `.find("### Step 2")` matches the FIRST occurrence of the substring, not the first Markdown heading. Per Hendrickson (*Explore It!*) substring-collision heuristics and the slice-085 false-negative lineage this slice exists to close: (a) an inline narration mention — e.g. prose `"when you reach ### Step 2 you spawn"` before the real `### Step 2:` heading — anchors `start` on the narration; (b) a future skill with a `### Step 20` heading collides on the `### Step 2` prefix. Executed scenario (a) against the live helper: the extractor returned a 27-char garbage region and reported the guard absent — the *exact wrong-region false-negative class* the slice's own docstring (lines 23-26) cites as the reason SOAD-1 needed section-scoping.
- **Evidence**: NOT a present defect — all three current skills have exactly one clean `### Step 2` / `### Step 3` heading pair in correct order (offsets: critique 4046/6223, critique-review 3123/5188, code-review 10726/13893; no prefix collisions, no pre-heading narration). The test is correct today. It is a robustness gap that bites a future skill author or a future skill whose narration references the step headings.
- **Proposed fix**: anchor on line-start to match headings rather than substrings — `re.search(r"(?m)^### Step 2\b", content)` / `^### Step 3\b`. The `\b` closes the `### Step 20` prefix collision; the `(?m)^` closes the inline-narration collision. Cheap, and future-proofs the helper against the same wrong-region class the slice was written to defend against.
- **Disposition**: **ACCEPTED-FIXED in-slice** (user-elected, 2026-05-30 — NOT deferred to bundle). `_step2_to_step3_region` now uses module-level compiled `_STEP2_HEADING_RE` / `_STEP3_HEADING_RE` (`(?m)^### Step N\b`). Two regression tests added: `test_seam_anchoring_is_line_start_not_substring` (inline mid-line mentions must not mis-anchor — the discriminating case where the pre-fix `.find` excluded the guard) and `test_step2_regex_rejects_step20_prefix_collision`. Pin test now 9/9; full suite 1237 passed. Rationale: the fix closes the exact substring-vs-shape class this slice exists to defend against — shipping the guard's own test with that fragility would be a slice-022-style self-violation.

## Verification performed (execution, not inspection)

Per APED-1, the code-Critic executed the slice's own parse rule against an adversarial battery rather than trusting the build summary:

- **Dash byte-consistency**: U+2014 (0x2014) confirmed in the heading of all four files (3 skills + test CANON). No U+002D or U+2013 contamination. LF-only.
- **Body-literal uniqueness**: `self-author`, `placeholder` each appear exactly once per skill — no narration collision; the slice-085 false-negative class does not recur.
- **Test teeth**: monkeypatched mutation battery — DELETE → fail; RELOCATE-after-Step-3 → fail; GUT-body-keep-heading → fail; em-dash→hyphen → fail; unmutated → pass. The test catches deletion AND relocation, not mere presence.
- **Region extractor edge cases**: missing-heading is handled (clear assert); narration-before-heading is the m1 latent gap.
- **Drift / parity (AC-3)**: all three installed copies content-equal modulo EOL; `test_code_review_skill_drift.py` (OSDG-1) green. code-review DOES have a whole-file drift test — the design's "critique/critique-review have NO drift test per B1/B2" claim refers to those two specifically and is accurate.
- **AC-4 / AC-5**: global `~/.claude/CLAUDE.md` `# Spawned-agent output` stopgap removed (no `Async agent launched` residue); shippability row pinning `test_r25_await_real_agent_guard` + R-25 present.
- **Suite**: 8/8 pass on the R-25 + drift tests.

## Dimensions checked
- [x] Unfounded assumptions — none. Docstring claims (U+2014, seam-scoping, written-failing→passing) all verified true against disk; no phantom imports (`read_file` exists in conftest.py:15).
- [x] Missing edge cases — m1 (substring-collision / narration-before-heading in `_step2_to_step3_region`). Missing-heading edge IS handled. No EOL-DRIFT-1 exposure (drift test reuses EOL-agnostic helper).
- [x] Over-engineering — none. Three-tuple parametrization + one helper; no speculative generality.
- [x] Under-engineering — none. Every AC has a delivering code element (AC-1..AC-5 verified). Relocate fixture delivers the M-add-1 placement-enforcement obligation. RSAD-1: the pin would catch its own guard's deletion.
- [x] Contract gaps — none. `_step2_to_step3_region` type-hinted, docstringed, keyword-only `src`.
- [x] Security — none. No new input boundary, authz path, secret, subprocess, or injection vector.
- [x] Drift from vault — none. Code matches design.md insertion points + ADR-078 ordering (stopgap removed LAST — confirmed gone); MEPD-1 EXCLUDE honored (no RULE-ID/VERSION bump). No out-of-scope files touched.
- [x] Web-known issues — Skipped: no external API/SDK/framework call (markdown prose + stdlib `re`/`pytest` only).
- [x] Cross-cutting conformance — none beyond m1. APED-1 executed (the slice's own claim holds). RSAD-1 clean. EOL-DRIFT-1: no new byte-compare. The new `.find()`-anchored extraction composes correctly with the three current skills' single-pair heading structure (m1 is the one branch that doesn't generalize).
