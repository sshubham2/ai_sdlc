---
id: ADR-003
title: RR-1 audit fixes documentation to match the regex's actual behavior, rather than widening the regex to accept double-hyphen
date: 2026-05-09
slice: slice-004-fix-rr1-audit-docstring-or-regex
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-003: RR-1 audit fixes docs, not regex

## Context

`tools/risk_register_audit.py` (introduced in slice-002 as part of the RR-1 schema migration) parses risk-register.md entries via `_RISK_HEADING_RE = re.compile(r"^##\s+(R-?\d+)\s+[—\-]\s+(.+?)\s*$")`. The regex's character class `[—\-]` accepts a SINGLE em-dash `—` OR a SINGLE hyphen `-` between the risk ID and the title — it is single-character.

Two surfaces of documentation contradicted this:

1. **The module docstring's "Format" section** (around L17–L27) showed the canonical example as `## R-NN -- <title>` with a DOUBLE hyphen.
2. **The inline comment immediately above the regex** (L55) said `# H2 risk heading: "## R-NN -- title" or "## R-NN — title" (em dash)` — claiming both `--` and `—` are accepted.

Neither claim is true. A `##  R-1 -- title` heading produces a silent zero-risks-returned audit because the regex cannot match. Slice-002 hit this exact bug at format-conversion time: the user followed the docstring, ran the audit, got "0 risks" with no error, debugged for a while, eventually noticed the regex was character-class-not-string-class, and switched to em-dash. The reflection logged it as a tooling-cleanup candidate.

Slice-002's reflection said: *"either fix the regex to accept `--`, or update the docstring to drop the misleading example."* Slice-003 carried it forward as a deferred candidate. Slice-004 picks it up. The design must choose between (at least) three real alternatives.

## Options considered

1. **Widen the regex** (option A) to also accept `--`. Pattern becomes `^##\s+(R-?\d+)\s+(?:—|--?)\s+(.+?)\s*$` or similar. The docstring's existing `## R-NN -- <title>` example becomes correct retroactively.
   - Pros: forgiving for users who type `--` (more natural; em-dash typically requires IME/snippet); zero documentation churn (existing docstring becomes correct as-is); zero risk of breaking hypothetical projects that have `--`-shaped entries
   - Cons: encourages the format the methodology has explicitly canonicalized AGAINST (slice-002's lessons-learned + slice-003's `_index.md` aggregated lessons both say "use em-dash, not double-dash"); makes the audit's behavior more surface area to maintain; future tightening to em-dash-only is a behavior break
   - Reversibility: cheap (revert pattern change)

2. **Tighten the regex to em-dash only** (option B2) — character class becomes literally `—` (single character). Drops single-hyphen acceptance as well.
   - Pros: cleanest end-state (single canonical separator); aligns with the methodology's explicit em-dash preference
   - Cons: breaks any project that has `## R-N - title` (single-hyphen) entries; this case isn't observed in this repo but is a behavior change for hypothetical adopters; forces an undocumented existing capability to be explicitly removed
   - Reversibility: cheap (revert to `[—\-]`)

3. **Fix the documentation to match the regex** (option B1) — change docstring + inline comment to accurately describe `[—\-]`'s behavior: em-dash OR single hyphen accepted; double-hyphen NOT accepted (because the regex is single-character).
   - Pros: smallest possible change (zero behavior change); fixes the actual contradiction (the regex IS the source of truth; docs should describe it); preserves existing behavior for any caller; documentation accuracy improves immediately
   - Cons: doesn't fix the UX pain (a user who types `--` still gets silent 0-risks); the resolution path requires the user to read the corrected documentation (or hit the bug, then read)
   - Reversibility: cheap (revert documentation edits)

4. **Hybrid — widen regex + emit deprecation hint when `--` is detected** (option C). Pattern accepts `--` but emits a stderr warning like "heading uses `--`; em-dash `—` is canonical (RR-1 v1.x)".
   - Pros: best UX (no silent 0-risks bug; user gets immediate signal); nudges toward canonical form without breaking existing behavior; mirrors the existing `--warn-legacy` pattern for legacy table-format files
   - Cons: more code (separate detection regex + stderr emission + new test); risk of changing audit's default output stream behavior in ways that could affect existing CI / automation parsing the output; design-stage decision about whether the hint is opt-in (flag-gated) vs. always-on
   - Reversibility: cheap (revert all three change classes)

## Decision

Choose **option 3 (B1): fix the documentation to match the regex's actual behavior. Keep `_RISK_HEADING_RE` strictly unchanged**. The change is purely documentation; zero behavior change.

Specifically:
- The module docstring's "Format" section shows `## R-1 — <title>` (digit-bearing ID + em-dash separator) as canonical, with an inline note that single hyphen is also accepted as alternate, and double-hyphen is NOT accepted because the regex is single-character. *(Note: examples MUST use a digit-bearing ID like `R-1` because the regex requires `R-?\d+` — letter placeholders like `R-NN` don't match. Verified empirically.)*
- The inline comment immediately above `_RISK_HEADING_RE` accurately describes what `[—\-]` matches (em-dash OR single hyphen) and explicitly notes that double-hyphen is not.
- `architecture/risk-register.md`'s L3 opening prose is updated to use the canonical example shape, eliminating the third documentation surface that perpetuated the bug. *(Added per Critic M2 review.)*

The slice-004 mission brief's must-not-defer item explicitly considered the option-C deprecation-hint path as an in-scope hedge against silent failure for `--`-typing users. The design-stage decision against option C: it adds code surface (5–10 LoC + a test) that addresses a known-shape UX pain whose actual frequency in this repo is N=1 (slice-002 incident, since recovered). The cost-benefit of option C improves IF additional `--`-typing incidents accumulate in slice-005+; until then, option B1's minimum-change posture wins.

The decision against option A: option A makes `--` a CANONICAL accepted form, which the methodology's lessons-learned have explicitly canonicalized AGAINST. Slice-002's reflection says "use em-dash, not double-dash" and slice-003's aggregated lessons mirror this. Widening the regex would silently retract that lesson.

The decision against option B2: option B2 is a behavior change to drop single-hyphen acceptance. No test fixture and no production entry uses single-hyphen, but that's not a strong enough negative signal to remove undocumented existing capability. Tightening is a separate slice if it becomes warranted.

## Consequences

- **No behavior change.** The audit's regex, output, exit codes, and CLI surface are identical pre/post slice-004. Existing 38+ tests in `test_risk_register_audit.py` + `test_risk_register_audit_real_file.py` continue to pass without modification. Slice-002's shippability entry (real-file integration test) continues to pass.
- **Documentation now matches reality across all three surfaces** *(extended to 3 surfaces per Critic M2)*: (a) the audit module's docstring "Format" section, (b) the inline comment immediately above `_RISK_HEADING_RE`, AND (c) `architecture/risk-register.md` L3 opening prose. The user-facing risk-register.md prose was previously the third unchecked surface; the slice-002-style silent-zero-risks bug now requires the user to ignore documentation across ALL THREE surfaces to recur.
- **The `--`-typing UX pain persists.** A user who skips reading the docstring and types `## R-N -- title` still gets 0 risks silently. This is acknowledged; option C is the deferred hedge if recurrence happens. **Mitigation**: future `/risk-spike` or `/reflect` should re-evaluate this trade-off if a slice-005+ incident surfaces.
- **No methodology-changelog version bump.** Slice-004 is documentation-only within the audit module; RR-1 v0.12.0 is unchanged in its public schema definition. `/reflect` decides whether the cleanup gets a v0.20.x changelog bullet.
- **The new regression-guard tests are scoped to documentation-vs-regex consistency.** They do NOT pin the docstring's exact wording (which would create over-specification + churn for cosmetic edits). Instead they assert: every H2-shaped heading example in either documentation surface successfully parses through `_RISK_HEADING_RE`. This is the minimum invariant that prevents the slice-002 contradiction from recurring.

## Reversibility

**Cheap.** Reverting the chosen option-B1 path: undo three documentation edits (docstring "Format" section + inline comment + `architecture/risk-register.md` L3) and delete three new test functions plus the regression-guard test. Total revert: ~20–40 minutes.

Migrating from option B1 to option C in a future slice (the hedge) is **cheap for the code**, with a small documentation-precedent migration cost. Concretely:
- B1's documentation is a strict superset of what option C would document; only ADD the deprecation-hint code path (~5–10 LoC + a test), no SUBTRACT. The decision is layered, not exclusive.
- B1 explicitly canonicalizes em-dash in **three** documentation surfaces (audit docstring + inline comment + risk-register.md L3) — not just in lessons-learned. A future option-C slice that widens the canonical accepted forms would need to revise the "is NOT accepted" claim across all three surfaces. Estimated migration cost: **30–60 minutes of additional doc-revision work**, plus the new option-C tests. Not blocking; just a non-zero cost worth flagging *(per Critic m1: previously this was paraphrased as "somewhat costly" — concrete time estimate added for honesty).*

The slice's **regression-guard test** (R-1.score=6/band=high; R-2.score=2/band=low; outside TF-1 per Critic M1) keeps the path bidirectional: any future regex-altering slice that breaks scoring is caught loudly rather than silently shifting the risk rankings.
