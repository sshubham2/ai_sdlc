# Reflection: Slice 034 fix-tf1-audit-field-line-regex

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- ADR-034 Option 3 (relax-AND-loud-malformed) — validated: annotated `**Test-first**: true  (per TF-1 — …)` now ENABLES the gate (repro 3/3, BC-PROJ-4 dogfood on the slice's own bare-field brief reports "clean. 9 row(s)" not "not enabled"); `false-positive`/`true.` hit the loud `malformed-test-first-field` branch (real-artifact: exit 1 + attributed message).
- M2 both-booleans invariant — validated: `test_present_false_field_is_not_malformed` (bare + annotated `false` → zero violations, not enabled). `**Test-first**: false` stays a legitimate default-off, not malformed.
- `_format_human` L443 guard (`and not result.violations`) — validated: the malformed violation renders loudly; the silent "not enabled" message only fires on genuine absence (real-artifact AC3 output had no "not enabled").
- 4-part atomic PMI-1 bump 0.47.0→0.48.0 + TFFL-1 entry-pin — validated: `test_v_0_48_0_tffl_1_entry_present_in_repo_and_installed` green; PMI-1 audit clean at version 0.48.0; INST-1 lockstep (no tool added).
- R-7 retirement — validated: risk-register `**Status**: retired`, audit parses `status: retired`, `test_r7_retired_in_risk_register` green; durable repro catalogued as shippability #34.
- Zero regression — full methodology suite 656 passed (was 648 @ slice-033; +8 net); shippability 34/34.

## Corrected
- None at build time. design.md §1/§2 + ADR-034 + the M1/M2/M-add-1 fix-block landed exactly as specified through /build-slice with zero deviation. One implementation refinement (the `_format_human` L443 `and not result.violations` guard) was *consistent with* design intent ("'not enabled' only on genuine absence"), surfaced in plan-mode — captured in build-log, not a correction.

## Discovered
- **`tools.risk_register_audit --filter-status open` lists RETIRED risks** (R-5 [retired slice-033] AND R-7 [retired here] both appear in `--filter-status open` output; JSON `status` field is correctly `retired`). The flag does not filter by status; /status + /slice read the `status`/`band` fields so current consumers are unaffected, but a naive `--filter-status open` consumer could treat retired risks as open during risk-first prioritization. Pre-existing (R-5 proves it predates slice-034), out of slice-034 scope. Added to risk-register as [[risk-register#R-9]] (low; reversibility: cheap).

## Deferred
- R-9 (RR-1 `--filter-status open` filter semantics) — reason: out of slice-034 scope (R-7/TFFL-1 fix only; RR-1 filter is a separate tool); low impact (consumers read the `status` field). Lands in: backlog / a future risk-register-tooling slice.

## Critic calibration

Scored from `critique.md` `## Triage` + `critique-review.md` DR-1 + reality during build/validate:

- **M1** (regex `(true|false)\b.*$` over-matches `false-positive`→`false`): **VALIDATED** — ACCEPTED-FIXED; reality (AC3 real-artifact: `false-positive` brief → loud `malformed-test-first-field`) confirmed the over-match was real and the standalone-token fix closes it. **Highest-value catch** — the first Critic caught it by *empirically running the proposed pattern*, reaching the audit-regex defect class that slice-031/033 reflections said "the dual-Critic stack structurally cannot reach." Tasking the Critic to test the regex empirically worked.
- **M2** (both-booleans invariant unstated): **VALIDATED** — ACCEPTED-FIXED; `test_present_false_field_is_not_malformed` confirms a `true`-only narrowing would have spuriously flagged every disabled brief. Real load-bearing invariant.
- **M-add-1** (RULE-ID + `test_v_0_48_0_*` entry-pin obligation absent): **VALIDATED** — ACCEPTED-FIXED; PMI-1 genuinely required v0.48.0 and the entry-pin test would not exist otherwise. **Missed by the FIRST Critic, caught by the DR-1 meta-Critic.** First Critic's Dim 7 checked PMI-1 version *mechanics* but not the rule-ID/entry-pin *content* obligation — the "deep-dive crowded out the checklist item" pattern the meta-Critic named.
- **m1** (PENDING functions not phantom): **VALIDATED** — ACCEPTED-PENDING; all cited functions created under exact names, green. No phantom citation (citation discipline checked clean by both Critics).
- **m2** (AC5 vault-state ordering hazard): **VALIDATED** — ACCEPTED-PENDING; register escalation sequenced before AC5 PASSING; AC5 green. Correct call.

**Missed by Critic**: M-add-1 was missed by the first Critic (caught by DR-1 meta-Critic — the dual-stack worked as designed). Neither Critic flagged the RR-1 `--filter-status open`-lists-retired issue, but that is a pre-existing latent tool defect orthogonal to slice-034's design, surfaced only by running the audit on the mutated register at /validate — a Discovered, not a design miss.

**Pattern**: the slice-022 self-violation law held (~N≈11) — the R-7-fixing slice committed a *narrower* R-7 (the `\b` over-match) in its own proposed regex. **But this time the first Critic CAUGHT it at design-time by empirically testing the proposed pattern** — a departure from slice-031/033 where the identical audit-vs-artifact class was MISSED by both Critics and caught only by the BC-PROJ-4 real-artifact backstop. Strong `/critic-calibrate` signal: explicitly tasking the first Critic to *run the proposed regex against adversarial strings* (not reason about it) closes the design-stage audit-regex blind spot the project had concluded was structurally Critic-unreachable. The complementary signal: the first Critic's deep regex-correctness focus crowded out a mechanically-derivable checklist obligation (M-add-1 RULE-ID/entry-pin) that DR-1 caught — argues for a Critic checklist pass on "does a methodology-surface slice mint a RULE-ID + entry-pin" alongside the deep dive.

## Lessons for next slice
- **Tasking the first Critic to empirically execute a proposed regex/parser against adversarial inputs reaches the audit-vs-artifact defect class the dual-Critic stack was thought structurally unable to reach** (slice-031/033 said only BC-PROJ-4 could). slice-034 M1 is the counter-example: the Critic ran `(true|false)\b.*$` against `false-positive` and caught the self-violation at /critique, not at pre-finish. For any slice that changes an audit's own parse rule, the /critique prompt should explicitly demand empirical pattern-testing — promote-eligible `/critic-calibrate` input.
- **Methodology-surface slices need a Critic checklist pass for RULE-ID + entry-pin obligation, separate from the deep-dive.** First Critic verified PMI-1 version mechanics but missed that a behavior-changing entry needs a minted RULE-ID + `test_v_0_NN_0_*` pin (slice-032 DEVIATION-1 class). DR-1 caught it; the "deep-dive crowds out the checklist item" pattern recurs — candidate for a Dim-7/Dim-9 surgical sub-bullet at the next `/critic-calibrate`.
- **BC-PROJ-4 dogfood remains the decisive proof for audit-parse-rule slices** — running the changed audit on the slice's OWN brief ("ENABLED 9 row(s)" not "not enabled") is the single most convincing validation artifact; cheaper and more conclusive than any unit fixture. Keep it the mid-slice + pre-finish gate for this slice class.
- **R-9 candidate**: a naive `--filter-status open` consumer is a latent risk-first-prioritization footgun; if a future slice consumes that flag directly (not the `status` field), promote R-9 to a fix slice.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-7 → `Status: retired` + `Retired:` field + retirement note (AC5); added [[risk-register#R-9]] (RR-1 `--filter-status open` lists retired risks; low / cheap)
- [[decisions/ADR-034]] — accepted (relax-AND-loud-malformed; M1/M2/M-add-1 fix-block applied)
- [[methodology-changelog.md]] — v0.48.0 TFFL-1 entry (+ forward-synced installed copy)
- This slice's [[design.md]] — M1/M2/M-add-1 fixes + zero-row wiring matrix; no post-build correction
- [[shippability.md]] — row #34 (added at /repro; slice name confirmed correct; durable R-7 regression guard)
