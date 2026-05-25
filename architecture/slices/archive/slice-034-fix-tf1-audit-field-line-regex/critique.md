# Critique: Slice 034 fix-tf1-audit-field-line-regex

**Critic reviewed**: mission-brief.md, design.md, ADR-034
**Date**: 2026-05-17
**Result**: NEEDS-FIXES (pending TRI-1 user ratification)

## Summary

Fix strategy is sound; all cited line numbers (L54, L138-144, L289, L443-444) and contract claims (`_detect_test_first_flag` → `bool`; `missing-section` `severity="Important"`) VERIFY against the real `tools/test_first_audit.py`. Self-violation-law check PASSES for the dogfood guard (this slice's own bare `**Test-first**: true` line is correctly detected; HTML-comment annotation lines do not false-fire). But two majors: the proposed `(true|false)\b.*$` over-matches `false-positive`→`false` (a narrower R-7 silent-bypass re-introduced through the fix's own regex), and the AC3 malformed-branch correctness rested on an unstated both-booleans invariant. 0 blockers, 2 majors, 2 minors.

## Findings

### Blockers (must address before /build-slice)

None. Line-number/contract claims all verified accurate against the actual file; the dogfood self-violation guard is structurally sound.

### Majors (address this slice)

#### M1: Proposed regex `(true|false)\b.*$` over-matches `**Test-first**: false-positive` / `true.` as a valid boolean
- **Claim under review**: design.md §1 / ADR-034: widen value match to `(true|false)\b.*$`; must-not-defer only contemplated mid-sentence prose, not malformed-suffix values.
- **Issue**: `\b` matches between `false` and `-` (non-word char). Empirically: `**Test-first**: false-positive` → `false`; `true.` → `true`; `false; note` → `false`. These are exactly the "field present but value unparseable" class AC3 promises to catch loudly, but the value matcher accepts them — silent default-off. `false-positive`→`false` is the precise R-7 silent-bypass class this slice exists to close, re-introduced through the relaxed regex. Self-violation-law instance (~N≈10/11).
- **Evidence**: empirical test of the exact pattern (Critic Bash run); risk-register.md R-7 names "field present but value/format unparseable" as the class to make loud.
- **Proposed fix**: boolean must be a standalone token — `(true|false)(?=[\s(]|$)`; malformed-suffix forms fall to the §2 branch. Add test rows for `false-positive` / `true.`. Verify the repro's annotated `true  (per TF-1 …)` still passes.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §1 rewritten to the standalone-token lookahead `^\*\*Test[-\s]?first\*\*\s*:\s*(true|false)(?=[\s(]|$)` with explicit rejection rationale; ADR-034 Decision updated (records `\b` rejection); mission-brief must-not-defer bullet (b) added; TF-1 plan gains AC3 row `test_malformed_suffix_value_is_loud_not_silent`. (TPHD-1 sub-mode (a) harmonization applied same fix block.)

#### M2: AC3 malformed-branch correctness rests on the unstated invariant that the value matcher captures BOTH booleans
- **Claim under review**: design.md §2: "if field prefix present AND no line satisfies the value matcher → malformed violation".
- **Issue**: A legitimately-disabled `**Test-first**: false`-only brief MUST take silent default-off (AC2), NOT the malformed branch. This works only because the value matcher's alternation is `(true|false)`. An implementer narrowing the branch's value check to `true`-only (plausible misreading — "no valid *enabling* value") would spuriously emit `malformed-test-first-field` on every `**Test-first**: false` brief, breaking AC2 + existing fixtures. The invariant was not stated load-bearing and had no pinning test.
- **Evidence**: design.md §2 prose; AC2 (mission-brief.md) requires `**Test-first**: false` non-regression; empirically `false` satisfies the proposed value matcher.
- **Proposed fix**: state the both-booleans invariant explicitly in design.md §2 + add `test_present_false_field_is_not_malformed` (false-only brief → zero violations, `test_first_enabled is False`).
- **Builder draft**: **ACCEPTED-FIXED** — design.md §2 now carries the "Load-bearing invariant (per /critique M2 — do NOT narrow)" paragraph; TF-1 plan gains AC2 row `test_present_false_field_is_not_malformed`.

### Minors (log; address if cheap)

#### m1: AC2/AC3/AC5 cite test functions that do not yet exist — confirmed PENDING, not phantom
- **Issue**: Critic Grep'd `tests/` for the three cited names → none exist. Correct/expected — all rows marked `PENDING`; the design did NOT phantom-cite. Recorded for the calibration loop (citation discipline checked; clean).
- **Builder draft**: **ACCEPTED-PENDING** — `/build-slice` creates the functions under the exact cited names (incl. the two new rows added by M1/M2). No design change.

#### m2: AC5 `test_r7_retired_in_risk_register` asserts vault state the same slice mutates — ordering hazard, not circular
- **Issue**: State-check (preferred form per "declaration-check vs state-check" lesson), not circular. Only hazard: sequence the R-7 register escalation before marking the AC5 row PASSING.
- **Builder draft**: **ACCEPTED-PENDING** — Builder performs the R-7 register escalation, then brings AC5 row to PASSING (sequencing note for `/build-slice`).

## Dimensions checked
- [x] Unfounded assumptions — M1, M2 (cited line numbers/contracts verified accurate; the regex sufficiency + implicit invariant were the unfounded "this is enough" assumptions)
- [x] Missing edge cases — M1 (`false-positive`/`true.`/`false; note`), M2 (`false`-only vs malformed branch); empty-value correctly → malformed (verified); multi-occurrence noted, not realistic
- [x] Over-engineering — none (pure in-file, zero new module, reuses `TestFirstViolation`/`_format_human`/`to_dict`; zero-row wiring matrix correct)
- [x] Under-engineering — none blocking (every AC has a TF-1 row; WRITTEN-FAILING genuineness confirmed — repro fails with `test_first_enabled=False`, not an import error)
- [x] Contract gaps — none (CLI surface unchanged; behavioural-delta table accurate)
- [x] Security — none (local audit tool, no auth/secret/injection surface)
- [x] Drift from vault — none (ADR-034 `supersedes: null`; R-7 entry confirms open/medium/cheap; PMI-1 4-part bump genuinely required — refusal boundary shifts; no new tool → INST-1 lockstep only — verified)
- [x] Web-known issues — none (stdlib `re`; `\b` semantics stable — M1 is a pattern-choice design error, not a platform issue)
- [x] Cross-cutting conformance — M1 is a recursive-self-application catch (Dim 9 design-time): the R-7-fixing slice re-introduced a narrower silent-bypass via its own regex (self-violation law ~N≈10). Algorithm-path: malformed branch correctly inserted BEFORE L289 and AFTER carry-over (L278) / missing-brief (L272) returns — no regression to `_slice_is_carry_over` / `--strict-pre-finish` interaction. Tooling-doc-vs-impl: module docstring L20-22 stays accurate only if M2's invariant holds (now pinned).

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: NEEDS-FIXES

(Reconciles BOTH passes: first Critic `critique.md` M1/M2/m1/m2 + meta-Critic `critique-review.md` EXTEND missed-finding M-add-1. User ratified all Builder drafts 2026-05-17.)

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-FIXED | design.md §1 + ADR-034 Decision retightened to standalone-token lookahead `(true|false)(?=[\s(]|$)`; mission-brief must-not-defer (b); TF-1 row `test_malformed_suffix_value_is_loud_not_silent` |
| M2 | Major | ACCEPTED-FIXED | design.md §2 "Load-bearing invariant (do NOT narrow)" para; TF-1 row `test_present_false_field_is_not_malformed` |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic missed finding) minted RULE-ID `TFFL-1` (refines TF-1 in place, supersedes nothing; EOL-DRIFT-1↔CAD-1 lineage); design.md "What's new" + ADR-034 Consequences + must-not-defer + TF-1 row `test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed` |
| m1 | Minor | ACCEPTED-PENDING | `/build-slice` creates cited test functions under exact names |
| m2 | Minor | ACCEPTED-PENDING | Builder sequences R-7 register escalation before AC5 row PASSING |
