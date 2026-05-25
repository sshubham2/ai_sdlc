# Critique: Slice 002 fix-diagnose-contract-and-cwd-mismatch

**Critic reviewed**: mission-brief.md, design.md (no new ADRs — slice introduces none)
**Date**: 2026-05-09
**Result**: NEEDS-FIXES (pending user triage)
**Mode**: voluntary critique on a low-tier slice (Critic-required: false per methodology, but user opted in — same pattern as slice-001 where it paid off)

## Summary

Narrow cleanup slice with 0 blockers but 4 majors + 4 minors that warrant fixes before /build-slice. Most-significant finding (M1): the slice's premise — "subagents lose tools because TARGET ≠ cwd" — is one *hypothesis*, not the confirmed root cause; public Claude Code issue #57037 describes the same symptom under a different proximate cause (parallel-spawn permission cascade-failure when multiple Agent tool calls dispatch in one message — exactly what /diagnose Step 5 does). The slice's documented-constraint fix path is still the cheapest mitigation, but the warning prose should acknowledge causal uncertainty rather than asserting cwd-mismatch as confirmed.

## Findings

### Blockers (must address before /build-slice)

(none)

### Majors (address this slice)

#### M1: cwd-mismatch is one hypothesis, not the confirmed root cause — warning prose risks misleading users

- **Claim under review**: design.md ("explains the cwd-mismatch, names the slice-001 / R1 finding, recommends re-invocation after `cd $TARGET`"); mission-brief AC #1 ("subagents lose tool access otherwise").
- **Issue**: Public Claude Code GitHub issues describe the same symptom (subagents denied Read/Grep/Bash, Glob remaining) under a *different* proximate cause: **parallel-spawn permission cascade-failure** (issue #57037), and **subagents not inheriting user-level permissions** (issues #18950, #37730). Slice-001's reflection asserts cwd-mismatch as the cause based only on correlation ("we saw it after invoking with an out-of-PWD path"). Cascade-failure happens specifically when "multiple Agent tool calls in one message" are dispatched — exactly what /diagnose Step 5 does. If the actual root cause is parallel-spawn cascade-failure, then `cd $TARGET` won't fix it.
- **Evidence**: SKILL.md Step 5 ("Parallel batch (run in a single message with multiple Agent tool calls)"); GitHub anthropics/claude-code #57037, #18950, #37730; slice-001 reflection.md attributes root cause to cwd without controlled experiment.
- **Proposed fix**: In SKILL.md Step 1's new cwd-warning prose AND in the user-facing warning text, soften from "subagents lose tool access otherwise" to "subagents *may* lose tool access otherwise — slice-001 surfaced this when TARGET was outside $PWD; the upstream root cause may be cwd-mismatch and/or a known parallel-spawn cascade-failure (claude-code #57037), so `cd $TARGET` is the cheapest mitigation but not guaranteed to fix every instance." Cross-reference #57037 in risk-register.md R-1's Notes/prose so future risk-spike work has a starting point.
- **Builder draft**: ACCEPTED-PENDING — apply during /build-slice. Soften the causal claim in SKILL.md Step 1 + mission-brief AC #1. Add #57037 cross-reference to R-1's prose. Costs ~3 lines of prose; doesn't expand scope.

#### M2: AC #2 / design.md offers two wording variants without selecting one

- **Claim under review**: design.md "Components touched > skills/diagnose/passes/*.md > Key change" lists both "the same four-line format as SKILL.md Step 5" AND "Optional shorter form: 'Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.' Pick one wording style and apply uniformly across all 11 files."
- **Issue**: The design says "Pick one" but doesn't *itself* pick. If Builder picks four-line for SKILL.md and shorter form for templates, they diverge — exactly the slice-001 lesson the new uniformity is meant to preserve. Worse, the inconsistency is exactly what made slice-001's bug hard to spot (contract authoritative in SKILL.md, copied verbatim into templates).
- **Evidence**: design.md "Pick one wording style and apply uniformly across all 11 files" — but doesn't specify which one.
- **Proposed fix**: Pre-select the **shorter form** uniformly: in SKILL.md Step 5's "Explicit subagent contract" bullet, in all 11 pass-template "Output format" sections, and in 01-intent.md's Hard rules line. Reserve the four-line breakdown as **once-only** human-readable preamble in SKILL.md Step 5 (above the contract bullet). Per-bullet contract that gets embedded into subagent prompts stays a single sentence so prompts stay terse. Add a new prose-pin test `test_pass_templates_match_skill_md_step5_contract` asserting byte-equality of the contract string across all 11 templates + SKILL.md.
- **Builder draft**: ACCEPTED-PENDING — pre-select shorter form; add the byte-equality prose-pin test (now 7 new tests instead of 6).

#### M3: AC #5's manual smoke gate is not mechanically checkable

- **Claim under review**: mission-brief AC #5 ("invoke `/diagnose <path-outside-PWD>` and observe the orchestrator's cwd-mismatch warning"); verification plan #5 ("observe warning in initial output").
- **Issue**: "Observe warning" is human-eyeball validation. The orchestrator (Claude main thread) emits the warning by following SKILL.md prose — non-deterministic. The prose-pin (AC #4) protects against the *prose disappearing*; nothing protects against the *orchestrator silently ignoring the prose at runtime*. The slice's whole point is to catch cwd-mismatch at runtime, but there's no programmatic check.
- **Evidence**: AC #5 + verification plan rely on human observation; SKILL.md Step 1 currently has no warning code path, so adding new prose alone may not move runtime behavior reliably.
- **Proposed fix**: Two options:
  (a) Accept AC #5 is exploratory-only; demote to "deferred-explicitly"; add **R-2** to risk-register: "no programmatic test ensures orchestrator emits cwd-mismatch warning at runtime; relies on prose-pin + manual smoke."
  (b) Tighten /validate-slice to capture warning text via prompt instrumentation (sandbox /diagnose invocation, grep for pinned phrase like "WARNING: TARGET resolves to a path outside $PWD").
  Option (a) is cheapest; option (b) is more robust.
- **Builder draft**: ACCEPTED-PENDING — apply option (a). Cheaper. Add R-2 to risk-register. Note in mission-brief AC #5 that runtime emission is acknowledged-fragile; programmatic verification is deferred to a future slice if R-2 surfaces real regressions.

#### M4: AC #2 negative pin scope + existing positive pin compatibility

- **Claim under review**: mission-brief AC #2 ("the literal string 'Do NOT call Write, Bash, or python' must not appear anywhere in skills/diagnose/"); existing test `tests/skills/diagnose/test_skill_md_pins.py:91` (`assert "do not call write" in lower or "do not use write" in lower or ...`).
- **Issue**: The new wording must preserve the substring "do not call write" (case-insensitive) so the existing positive pin continues to pass. Both wordings recommended in design.md happen to preserve it, but the design doesn't *verify* this. If Builder rephrases to "Subagents must not invoke Write..." (preserving meaning but breaking the substring), the existing test will silently break — a planning gap.
- **Evidence**: tests/skills/diagnose/test_skill_md_pins.py:91 accepts: "do not call write" / "do not use write" / "no write tool" / "must not call write" / "do not write".
- **Proposed fix**: Add a pre-flight to mission-brief Verification plan or build-slice notes: "the chosen wording must preserve the substring 'Do NOT call Write' (case-insensitive) so existing `test_skill_md_subagents_instructed_no_write` continues to pass." Also add to mid-slice smoke gate: run all existing prose-pin tests after wording change to confirm no regression.
- **Builder draft**: ACCEPTED-PENDING — apply during /build-slice. With M2's pre-selected shorter form ("Do NOT call Write to produce output files..."), the substring is preserved; the design will note this explicitly.

### Minors (log; address if cheap)

#### m1: "01-intent through 04-ai-bloat" reads as a 4-file numeric range

- **Claim under review**: design.md "Lives at: `01-intent.md` through `04-ai-bloat.md`" — heading says 11 files but description implies range.
- **Proposed fix**: rephrase as "01-intent.md, 02-architecture.md, 03a-dead-code.md, 03b-duplicates.md, 03c-size-outliers.md, 03d-half-wired.md, 03e-contradictions.md, 03f-layering.md, 03g-dead-config.md, 03h-test-coverage.md, and 04-ai-bloat.md (11 files total)" — same convention slice-001 used after correction.
- **Builder draft**: ACCEPTED-PENDING — cosmetic prose fix in design.md.

#### m2: risk-register format conversion — multi-line content silently lost in Notes field

- **Claim under review**: design.md "Convert prose ... into a single `**Notes**:` block ... OR keep them as sub-bullets after the field block".
- **Issue**: tools/risk_register_audit.py's `_FIELD_RE` regex is single-line. Folding multi-line prose into a Notes line silently truncates to first line. Design recommends sub-bullets but doesn't explain *why*.
- **Evidence**: tools/risk_register_audit.py:59 (`_FIELD_RE` single-line); :188-193 (line-by-line parse).
- **Proposed fix**: replace "OR keep them as sub-bullets" with "Keep them as sub-bullets (NOT folded into Notes — the audit's `_FIELD_RE` regex is single-line and would truncate multi-line content)."
- **Builder draft**: ACCEPTED-PENDING — clarify in design.md.

#### m3: Format conversion needs explicit before/after diff table

- **Claim under review**: design.md "Format conversion (R1 only)" lists 5 changes mixing "replace value", "add new field", "rename heading" without explicit ordering.
- **Issue**: Builder may misread; e.g., "Replace `**Severity**: Important` with `**Likelihood**: medium` and `**Impact**: high`" is actually *delete one field, add two new fields*, while "Add `**Status**: open` (was `**Status**: ACTIVE`)" is *change a value*. Different edits; misread risks malformed file.
- **Proposed fix**: rewrite as explicit before/after sketch in design.md:
  ```
  REMOVE:  **Severity**: Important
  ADD:     **Likelihood**: medium
  ADD:     **Impact**: high
  REPLACE: **Status**: ACTIVE → **Status**: open
  KEEP:    **Reversibility**: cheap (already valid)
  ADD:     **Discovered**: slice-001-diagnose-orchestration-fix (2026-05-09)
  RENAME:  ### R1 — Cwd-mismatch...  →  ## R-1 -- Cwd-mismatch...  (H3 → H2; em-dash → double-dash)
  ```
- **Builder draft**: ACCEPTED-PENDING — add explicit diff to design.md.

#### m4: AC #3 "high-band" assertion over-specifies

- **Claim under review**: design.md "Validation check" mentions `score: 6, band: high`.
- **Issue**: The integration test is band-agnostic ("≥1 risk + zero violations"). Asserting band=high in design risks mismatch if a future slice re-rates R-1 (e.g., reduces likelihood after the fix); test should remain band-agnostic.
- **Proposed fix**: drop specific score/band from the validation check; just say "returns R-1 in `risks` array with zero parse violations". Matches what the integration test actually checks.
- **Builder draft**: ACCEPTED-PENDING — drop score/band over-specification.

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (cwd-mismatch as confirmed cause is a leap; per Wiegers, claims trace to evidence; slice-001's evidence is correlation, not controlled experiment)
- [x] **Missing edge cases** — caught one minor: relative-path TARGET that resolves under $PWD would not be a true mismatch but might trigger the warning (false positive); folded into M1's broader concern about specifying the warning's trigger
- [x] **Over-engineering** — none. Slice is correctly scoped; no new modules; empty wiring matrix is honest
- [x] **Under-engineering** — none. Every AC has design delivery; M3 is a testability concern, not under-engineering
- [x] **Contract gaps** — none new (slice introduces no contracts)
- [x] **Security** — none (pure documentation + format-conversion edits; no secrets / input handling / authz / PII paths)
- [x] **Drift from vault** — none. ADR-001 is correctly preserved as accepted; risk-register conversion is required by RR-1 (compliance, not drift)
- [x] **Web-known issues** — M1 surfaced GitHub anthropics/claude-code issues #57037 (parallel-spawn permission cascade), #18950 (subagents don't inherit permissions), #37730 (subagents prompt for permission on already-allowed tools), #12748 (cwd parameter for Task tool — feature request), #31940 (cwd in subagent frontmatter — feature request). These collectively show cwd handling and parallel-spawn permissions are both known weak points; the slice's interpretation is plausible but not unique.

Sources cited by Critic:
- https://github.com/anthropics/claude-code/issues/57037 (parallel-spawn cascade-failure — symptom matches slice-001)
- https://github.com/anthropics/claude-code/issues/18950 (subagents don't inherit user-level permissions)
- https://github.com/anthropics/claude-code/issues/37730 (subagents prompt for already-allowed tools)
- https://github.com/anthropics/claude-code/issues/12748 (Task tool cwd parameter — feature request)
- https://github.com/anthropics/claude-code/issues/31940 (subagent frontmatter cwd/additionalDirectories — feature request)
- https://code.claude.com/docs/en/sub-agents

## Triage

**Triaged by**: user
**Date**: 2026-05-09
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-PENDING | Soften causal claim in SKILL.md Step 1 + mission-brief AC #1 from "subagents lose tool access otherwise" to "subagents *may* lose tool access — slice-001 surfaced this when TARGET was outside $PWD; upstream root cause may be cwd-mismatch and/or parallel-spawn cascade-failure (claude-code #57037), so `cd $TARGET` is the cheapest mitigation but not guaranteed to fix every instance." Add #57037 cross-reference to R-1's prose in risk-register.md. |
| M2 | Major | ACCEPTED-PENDING | Pre-select shorter form uniformly: SKILL.md Step 5's contract bullet + all 11 pass-template "Output format" sections + 01-intent.md Hard rules. Reserve four-line breakdown as once-only human-readable preamble in SKILL.md Step 5 above the contract bullet. Add prose-pin test `test_pass_templates_match_skill_md_step5_contract` for byte-equality (test count 6 → 7). |
| M3 | Major | ACCEPTED-PENDING | Apply option (a): add R-2 to risk-register ("no programmatic test ensures orchestrator emits cwd-mismatch warning at runtime; relies on prose-pin + manual smoke"); update mission-brief AC #5 to explicitly note runtime-emission is acknowledged-fragile and programmatic verification is deferred to a future slice if R-2 surfaces real regressions. |
| M4 | Major | ACCEPTED-PENDING | Add pre-flight to design.md: chosen wording must preserve "do not call write" substring (case-insensitive) so existing `test_skill_md_subagents_instructed_no_write` continues to pass. M2's pre-selected shorter form satisfies this; document explicitly. Mid-slice smoke gate runs full `test_skill_md_pins.py` to confirm no regression. |
| m1 | Minor | ACCEPTED-PENDING | Replace "01-intent.md through 04-ai-bloat.md" with explicit 11-file enumeration in design.md. Cosmetic. |
| m2 | Minor | ACCEPTED-PENDING | In design.md "Format conversion" subsection, explain the `_FIELD_RE` single-line behavior and commit to sub-bullets after the field block (NOT folded into Notes). |
| m3 | Minor | ACCEPTED-PENDING | Add explicit before/after diff to design.md (REMOVE/ADD/REPLACE/KEEP/RENAME table). |
| m4 | Minor | ACCEPTED-PENDING | Drop `score: 6, band: high` over-specification from design.md "Validation check"; assert only "≥1 risk + zero violations" matching the integration test's actual check. |
