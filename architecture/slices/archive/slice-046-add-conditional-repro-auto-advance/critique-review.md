# Critique Review: Slice 046 add-conditional-repro-auto-advance

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-19
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is technically sound — all three findings (M1, m1, m2) verified VALID against source, with correct severities and a correctly-accepted FALSE-POSITIVE override on m2. One missed concern surfaces from independent re-review: the design specified a post-auto-invoke "re-run Step 3c verification" loop without bounding its re-entrancy — a control-flow termination gap on the slice's core new path.

## Confirmed findings

- **M1** (genuine-contrast negative-anchor literal): confirmed VALID; severity Major appropriate. `` re-invoke `/slice` `` verified present verbatim at `skills/slice/SKILL.md:155` and absent from any other Step 3c location — a genuine, unique negative anchor. Positive literal `conditional confirm-then-auto-invoke` grep-confirmable absent pre-edit. Builder ACCEPTED-FIXED (design.md STP-1 + genuine-contrast sections pin both literals verbatim, agree with each other) resolves the tautology risk.
- **m1** (META-1 em-dash+ISO split regex): confirmed VALID; severity Minor appropriate. `test_methodology_changelog.py:136` splits on `^## v\S+ — \d{4}-\d{2}-\d{2}` (em-dash U+2014). ASCII-hyphen/dateless header silently skips block (META-1 vacuously passes). Builder ACCEPTED-FIXED (design.md header-shape paragraph) mitigates fully.
- **m2** (stale ADR-048 full-text excerpt): confirmed as correctly-overridden FALSE POSITIVE. Independently verified — design.md contains only thin `[[ADR-048]]` references (lines 11, 84) + a one-line "Decisions made (ADRs)" entry; no `## ADR-048 (full text)` block anywhere. The block the first Critic saw is the `/critique` skill's agent-input paste-in template, not design.md content. First Critic correctly accepted the OVERRIDDEN disposition rather than forcing a non-existent fix.

## Suspicious findings

None. M1, m1, m2 all VALID (m2 as a correctly-identified-and-overridden false positive). The first Critic did not over-reach.

## Missed findings

- **m-add-1: post-auto-invoke re-verification loop is unbounded** (Minor). design.md§"New Step 3c flow" step (4) stated that after auto-invoking `/repro <desc>`, `/slice` "re-runs Step 3c verification, continues Step 4." Step 3c verification is the shippability.md grep for a `tests/bugs/*` row. If `/repro` completes yet writes the failing test to a path NOT matching `tests/bugs/*` (legitimately possible — `skills/repro/SKILL.md` L87 explicitly allows "or project's convention for bug-fix tests", which is exactly why the verbal-claim-with-path fallback exists), re-run verification finds no row again. The design did not state whether re-verification (a) falls through to the preserved verbal-claim-with-path fallback, (b) re-enters the confirm gate / re-invokes `/repro` (potential loop), or (c) fail-closes. The first Critic checked the fail-closed "Not a bug — cancel" branch but did not trace the `/repro`-completed-but-grep-still-misses path. **Proposed fix**: design.md should add one sentence stating post-auto-invoke re-verification, on a still-missing `tests/bugs/*` row, routes into the preserved verbal-claim-with-path fallback (ask user to paste the just-created path) — NOT a re-invoke of `/repro` — bounding the edge to a single auto-invoke attempt. Minor severity (the verbal-claim fallback already exists in unmodified prose and is PRESERVED; the gap is the new flow not wiring its re-verification miss INTO that fallback explicitly, risking an ambiguous-prose loop rather than a guaranteed runtime loop).
- **Builder draft for m-add-1**: ACCEPTED-FIXED — design.md§"New Step 3c flow" step (4) now states `/repro` is invoked **exactly once**; a still-missing `tests/bugs/*` row routes into the preserved verbal-claim-with-path fallback (no `/repro` re-invoke, no loop). design.md§"Error model" now enumerates two bounded error paths (fail-closed + `/repro`-completed-but-grep-still-misses), explicitly bounding the auto-invoke edge to one attempt.

## Severity adjustments

None. M1 Major, m1 Minor, m2 Minor-class-false-positive, m-add-1 Minor all correctly filed.

## Notes

High confidence — all three first-Critic findings verified against primary source (`pipeline_chain_audit.py:235` literal-only gate check; `state_transition_pin_audit.py:229-230` NotIn exclusion; `test_methodology_changelog.py:136` em-dash split regex; `skills/slice/SKILL.md:155` verbatim negative anchor; ADR-018 + ADR-020 single-slot-plus-body-scope precedent; `supersede_audit.py` operates on briefs not ADR headers ⇒ partial-supersession unconstrained by SUP-1). The single missed finding is a control-flow termination edge on the NEW auto-invoke path — the highest-novelty surface of the slice; the first Critic's energy went (correctly) to the prose-pin and changelog-header mechanics. m-add-1 is genuinely Minor — but because the auto-invoke edge is the slice's entire reason for existing and the loop-vs-fallback ambiguity lives in prose Claude executes at runtime, it merited an explicit one-sentence resolution rather than reader inference. Now resolved (ACCEPTED-FIXED).
