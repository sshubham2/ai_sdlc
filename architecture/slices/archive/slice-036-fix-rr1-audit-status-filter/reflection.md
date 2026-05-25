# Reflection: Slice 036 fix-rr1-audit-status-filter

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- ADR-036 decision (single filtered `risks` list, drop `view`, `summary` register-wide) — validated on the **real** register: `--json --filter-status open`→only `status:open`; `--filter-band high`→only `high`; `--top 3 --sort score`→3 rows scores `[6,4,4]`; no `view` key. BC-PROJ-4 dogfood.
- "No skill-prose edit needed (code-conformance-to-doc)" — validated: `/slice` L46/L49 + `/pulse` L40 unchanged and still consume the now-filtered `risks` key correctly; durable prose-pin added.
- "Removing `view` is safe" (design author + first Critic + meta-Critic, 3× grep) — validated: 30/30 module + 36/36 shippability, zero consumer breakage.
- `summary` register-wide invariant — validated: `to_dict()` untouched; `test_summary_counts_by_band_and_status` still passes.

## Corrected
- Mission-brief Test-oracle line `--filter-band high == {R1,R3}` (copied from Critic M2/M-add-1 proposal) → reality: R3 is `low×high=3=medium` band; correct oracle is `{R1}`. Corrected in mission-brief at plan-mode (build-log Events 02:15). Source-of-truth = `_band_for_score` + `test_summary_counts_by_band_and_status` (by_band high==1).
- R-9 `architecture/risk-register.md` → `Status: open`→`retired` (this slice; [[ADR-036]]).

## Discovered
- **A methodology-surface tool *behavior* change (RR-1 JSON contract) has an open traceability question — methodology-changelog entry + RULE-ID/`### Changed` + PMI-1 bump?** Empirically NOT gate-required (PMI-1 clean at 0.49.0 — no skill/agent/tool added; `test_methodology_changelog.py` 70/70 with no slice-036 entry; this is a *conformance bug fix*, the RR-1 rule itself is unchanged; ADR-036 + R-9-retirement carry the decision trace — same shape as the slice-029 rule-ID-less precedent). BUT prior audit-tool fixes 033/034 each minted a changelog entry, and **neither Critic raised the obligation question at all** — recurring slice-032 DEVIATION-1 / slice-034 M-add-1 class (the 2026-05-17 calibration Proposal-2 class, ACCEPTED but not yet applied to `agents/critique.md`). Surfaced to user as a pre-`/commit-slice` decision (Step 8). Not auto-decided either way (auto-blessing "no entry" IS the slice-032 anti-pattern; auto-adding is /reflect scope creep + not mechanically required).
- Critic-stack reasons *about* fixtures without *computing* them: M2/M-add-1 asserted band-oracle `{R1,R3}` without applying `_band_for_score`. Inverse of slice-034 M1 (there the Critic was tasked to *execute*; here neither did). Caught only at plan-mode.

## Deferred
- None functional. The methodology-changelog-entry decision (above) is a user-owned pre-commit choice, not a deferred slice.

## Critic calibration

Per TRI-1, scored against `critique.md` + `critique-review.md` `## Triage` + reality:

- **B1** (Intent vs authoritative R-9): **VALIDATED** — ACCEPTED-FIXED; verified vs `risk-register.md` L170/L172; the contradiction was real and would have shipped a false "fixed live corruption" R-9-retirement claim.
- **B2** (CSP-1 mis-cited): **VALIDATED** — ACCEPTED-FIXED; verified vs `cross_spec_parity_audit.py` L1-17 (Heavy-only no-op).
- **M1** (no-flag ordering unpinned): **VALIDATED** — ACCEPTED-FIXED; pin test passes; real ordering delta.
- **M2** (band/top under-covered + real-register fragility): **VALIDATED-WITH-CORRECTION** — the *concern* was right (stable-oracle discipline, slice-004) and ACCEPTED-FIXED, but the Critic's *proposed oracle* `{R1,R3}` was factually wrong (band miscomputed). Concern valid; proposed expected-value wrong.
- **m1** (stale line numbers): **VALIDATED** — ACCEPTED-FIXED.
- **m2** (AC3 gate command unnamed): **VALIDATED** — ACCEPTED-FIXED. *But* the carve-out it blessed ("AC3 is a gate not a TF-1 row, survives strict TF-1") was itself wrong (see Missed #1).
- **M-add-1** (meta-Critic, DR-1 EXTEND — prose-pin over-claim): **VALIDATED** — ACCEPTED-FIXED; verified vs `test_risk_register_audit.py` L356-381; the durable prose-pin closed a real false-comfort in the slice's own thesis.

**Missed by Critic** (first + meta together):
1. **The "AC3 no-regression carve-out survives strict TF-1" claim was WRONG.** first-Critic m2 AND meta-Critic both blessed it as slice-004-precedent-valid; `tools/test_first_audit.py --strict-pre-finish` refused `ac-without-row` on AC3 at build pre-finish. Caught by the audit-on-the-real-artifact, NOT the dual-Critic stack — exact BC-PROJ-4 / slice-022-self-violation-law recurrence (N+1). The slice about fixing an RR-1 audit shipped a TF-1-audit self-violation in its own brief.
2. **Critic-stack proposed a factually wrong fixture oracle** (`--filter-band high == {R1,R3}`; R3 is medium band). Both Critics reasoned about the fixture without computing `_band_for_score`. Caught only at /build-slice plan-mode (read the fixture + the scoring fn).
3. **Neither Critic raised the methodology-changelog/RULE-ID/PMI-1 obligation question** for a methodology-surface tool behavior change — recurring slice-032 DEVIATION-1 / slice-034 M-add-1 class (N+1).

**Pattern**: All 7 filed findings VALIDATED (zero false-alarm) with correct severity — dual-Critic stack precision remains high on what it *files*. The three misses are the SAME two standing classes the 2026-05-17 `/critic-calibrate` already minted ACCEPTED proposals for (Proposal 1 audit-parse-rule empirical-execution → miss #1/#2; Proposal 2 RULE-ID/entry-pin checklist → miss #3) — but those proposals are still "user-to-apply-manually" to `agents/critique.md` and are NOT yet in the live prompt. **This slice is a strong pre-codification baseline data point: misses #1 and #3 would very likely have been caught had Proposals 1+2 been applied.** New sub-class: "Critic must COMPUTE fixture-derived expected values (scores/bands), not eyeball them" (miss #2) — N=1, watch.

## Lessons for next slice
- **The dual-Critic stack files with high precision but still misses its two standing blind-spot classes (audit-self-violation, RULE-ID/entry-pin obligation) — and the BC-PROJ-4 real-artifact pre-finish gate, not the Critic stack, is the structural backstop.** slice-036: TF-1 `--strict-pre-finish` refused the Critic-blessed AC3 carve-out; slice-022 self-violation law N+1. Budget the BC-PROJ-4 run as the PRIMARY catch for any audit/gate-touching slice; never trust a Critic-blessed "survives strict <AUDIT>" claim without running the audit on the real artifact. (slice-036)
- **A Critic-proposed test oracle is a claim about the artifact, not the artifact — recompute fixture-derived expected values before encoding them.** slice-036 M2/M-add-1 proposed `--filter-band high == {R1,R3}`; R3 is score-3 medium band. /build-slice plan-mode reading the fixture + `_band_for_score` caught it. Generalizes the slice-032 "Critic reasons about the claim not the artifact" lesson to Critic-proposed test expected-values. (slice-036)
- **Methodology-surface *behavior* changes (not just new rules) carry a changelog/RULE-ID/PMI-1 obligation question that the Critic stack does not raise — pre-decide it at /design-slice, verified against the enforcing audit, not adjudicated at /reflect.** slice-036 had to resolve it post-hoc (empirically not gate-required; ADR + risk-retirement sufficient for a conformance fix). The slice-032 DEVIATION-1 anti-pattern is auto-blessing "no entry"; the correct move is the slice-029 "pre-read the enforcing audit's assertion" discipline applied at design time. Strong `/critic-calibrate` input — confirms 2026-05-17 Proposal 2; the proposals must actually be applied to `agents/critique.md`. (slice-036)
- **`/repro` before the slice branch exists leaves the slice's own first artifact uncommitted on the default branch — `git checkout -b` correctly carries it; this is not a BRANCH-1 contamination case.** Confirm with the user (done) and proceed; do not stash slice-owned WIP. (slice-036)

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-9 `Status: open`→`retired` (slice-036; ADR-036; mitigation + regression-guard recorded)
- [[decisions/ADR-036-rr1-json-emits-single-filtered-risks-list.md]] — created this slice (cheap; accepted); Context/Consequences corrected per Critic B1/B2 + meta M-add-1
- This slice's [[mission-brief.md]] / [[design.md]] — Critic fixes applied pre-triage; Test-oracle `{R1,R3}`→`{R1}` corrected at plan-mode (build-log Events)
- [[shippability.md]] — #36 (added by `/repro`; verified present, not double-added)
- `tests/methodology/test_risk_register_audit.py` — repro (from /repro) + 5 new tests (code, not vault)
