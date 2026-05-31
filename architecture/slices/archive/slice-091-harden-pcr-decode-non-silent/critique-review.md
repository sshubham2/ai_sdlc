# Critique Review: Slice 091 harden-pcr-decode-non-silent

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-31
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: ADJUST

## Summary

The first Critic's review is strong and the M2 OVERRIDDEN disposition is correct — independently confirmed the round-trip is structurally unreachable. One disposition needs a calibration note (m1 is under-filed given it touches a load-bearing contract), and the independent re-review surfaces no new Blocker/Major, but two design-coherence points deserve a breadcrumb for the Builder. No verdict-changing miss.

## Confirmed findings

- **B1** (AC1 repro stages no blob) — confirmed; severity Blocker appropriate. Verified `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` L33-45 + L89-117: the rewrite to a real rebase conflict (`_stage_rebase_non_utf8`, non-UTF-8 on master → stage 2) with the fixture-guard (`raw.returncode == 0 and b"\xff" in raw.stdout`) is a genuine fix and structurally prevents the absent-stage vacuous-pass. ACCEPTED-FIXED is right.
- **M2** (degraded flag lost through `--diagnose → --classify` round-trip) — **OVERRIDDEN is CORRECT**. Independently verified: no `_from_jsonable`, no `json.loads`, no `from_dict` (only `argparse` at L38/L2099/L2122 as input). `main()` L2125 unconditionally rebuilds `diag = diagnose_conflict(repo_root)` live for every mode; `--classify` (L2148) and `--resolve-soft` (L2157) consume that live diag; `_to_jsonable` (L2082) is output-only via `dataclasses.asdict`. No CLI path ingests a serialized `ConflictDiagnostic`. The vulnerability is genuinely unreachable. The override stands.
- **M3** (both-manifestations convergence) — confirmed; Major appropriate. The bytes-mode rewrite collapses the Windows-falsy and POSIX-raise manifestations into one main-thread `.decode("utf-8")` path; the repro test already accepts any non-`UnicodeDecodeError` exception as PASS. ACCEPTED-FIXED is right.
- **m2** (MEPD-1 posture) — confirmed; Minor appropriate. EXCLUDE line present in design.md§Decisions with precedent slices cited.

## Suspicious findings

No suspicious findings. Every first-Critic finding maps to a real concern in design.md or the test surface. No over-reach.

## Missed findings

No missed Blocker or Major. Two minor coherence points the first Critic did not surface — both genuinely Minor, neither verdict-changing:

- **m-add-1** (Maintainability — frozen-dataclass mutation contract): `ConflictDiagnostic` is `@dataclasses.dataclass(frozen=True, slots=True)` (resolver L162-168). The design phrasing "diagnose_conflict ... marks the diagnostic degraded" reads as a post-construction set, which is impossible on a frozen+slots dataclass — `diagnose_conflict` MUST thread `claim_extraction_degraded=True` through the constructor call at the L221-225 return site (field added with a default so existing/synthetic construction sites stay valid). The design likely intends this (the "bool = False default" wording implies it), but the prose doesn't name the frozen constraint; a Builder skimming "set degraded=True" could reach for an `object.__setattr__` workaround. Fix: design.md states the flag is set at the L221 constructor call, not mutated. **Builder disposition: ACCEPTED-FIXED** (design.md§What's-new clarified).
- **m-add-2** (Error-model completeness — diagnose-path catch scope): the diagnose path calls `_git_show_stage` for BOTH stage 2 (L204) and stage 3 (L205). The design did not specify whether a stage-3 decode failure is equally caught and sets `degraded=True`. The catch must wrap both reads; the AC2/AC3 test should assert degraded=True for a stage-3-undecodable case too. Fix: design.md§Fail-closed-flow states the catch wraps both stage reads; add a stage-3 variant to the AC2 test matrix. **Builder disposition: ACCEPTED-FIXED** (design.md§What's-new + Test plan clarified).

## Severity adjustments

- **m1** (`_git_show_stage` docstring L709-716 goes stale) — **SEVERITY-WRONG: filed as cosmetic Minor; recommend elevating to a must-not-defer doc-discipline item (borderline Major-doc).** The docstring (L711-716) does not describe cosmetics — it documents the *falsy/None-tolerant contract* and instructs callers: *"Callers that parse the result must tolerate a falsy value (see `parse_queue_text(text) if text else {}` guard)."* That is the exact contract the fix INVERTS. A stale docstring here actively documents the removed dangerous contract and would mislead a future maintainer into reintroducing a falsy-tolerant caller (re-opening R-30 residual #1). Recommend: keep the ID, treat the docstring rewrite as a must-not-defer build item, and have the Builder rewrite the caller-tolerance sentence to document the raise-on-undecodable contract — not just trim the `None` mention. **Builder disposition: ACCEPTED-PENDING (elevated)** — added as an explicit must-not-defer item in mission-brief.

## Notes

High confidence. The load-bearing M2 override was traced end-to-end through actual source (no deserialization path; live re-diagnose at L2125; output-only `_to_jsonable`) — unambiguously correct. The count-pin reconciliation (9→8/4→5) checks out against the AST classifier's `text=True`-vs-`elif capture_output` logic. Skill integration verified: `classify_conflict → UNKNOWN → exit 1` is caught by commit-slice/SKILL.md L196-198 ("NEVER silent-default to SOFT on UNKNOWN"), so the fail-closed STOP propagates without any skill change — the "no external/CLI change" contract holds. Verdict ADJUST (not EXTEND): the substantive change is the m1 severity reframe; the two m-add findings are foot-gun-removal breadcrumbs, not coverage gaps. No new Major/Blocker.
