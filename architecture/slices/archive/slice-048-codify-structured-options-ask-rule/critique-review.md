# Critique Review: Slice 048 codify-structured-options-ask-rule

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-19
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's five findings (B1, M1, M2, m1, m2) are all VALID with correct severities, and the B1 false-precedent catch is well-grounded — the meta-Critic independently verified the unbroken `_entry_present_in_repo` convention through v0.55.0. An independent re-pass surfaces one Major the first Critic missed: the SOAD-1 rule's own host templates contain a literal bare free-text ask (`**ASK** the user: "Run /slice first..."`) that the new rule directly contradicts, creating a shipped self-violation.

## Confirmed findings

- **B1** (changelog false-precedent misread) — confirmed; severity Blocker appropriate. Verified vs `tests/methodology/test_methodology_changelog.py`: `_entry_present_in_repo` convention unbroken at v0.53.0 (L2921), v0.54.0 (L3024), v0.55.0 (L3097), all post-MCFS-1. Original design correction was a genuine false-precedent error (slice-032 m1 / MEPD-1 class). Builder ACCEPTED-FIXED reversal correct; the v0.54.0 STP-1 pair (L3024/L3068) is a precise model; lineage literal "generalizes ADR-048 / supersedes nothing" correctly mirrors the v0.54.0 "refines nothing, supersedes nothing" shape.
- **M1** (AC5 pin spec inconsistent; global `.count()` defeatable) — confirmed; Major appropriate. slice-021 precedent (`test_root_claude_md_branch_per_slice_rule.py`, verified `content.find(section)` → bounded slice → substring assert) is a sound section-scoped model; per-fenced-block resolution fixes the defeatable-oracle defect.
- **M2** (free-text fallback conflation) — confirmed; Major appropriate. Tool built-in free-text IS an options prompt that DOES notify; ADR-048 verbal-claim-with-path bare-prose does NOT. ADR-050 §Decision + must-not-defer 4 confirm the corrected reading.
- **m1** (brittle line-range citations) — confirmed; Minor appropriate. Anchor-on-heading+fence is the right remediation.
- **m2** (shippability row #48 forward-asserted) — confirmed; Minor appropriate. `max(existing)+1` + confirm-at-/reflect is the established pattern.

## Suspicious findings

None. All five first-Critic findings hold up against design.md and the verified source.

## Missed findings

- **M-add-1 (Major): SOAD-1 ships verbatim inside templates that themselves contain a bare free-text ask the rule forbids.** `skills/triage/SKILL.md` Fresh L224 + Append L248 and `skills/adopt/SKILL.md` Fresh L373 + Append L404 each contain a bare free-text directive (`2. If none → **ASK** the user: "Run \`/slice\` first, or is this small enough to skip?"`). The SOAD-1 sentence added to these same four fenced blocks says "never a bare free-text prompt." A generated `./CLAUDE.md` would carry SOAD-1 and, ~20 lines above it, a bare free-text ASK — a shipped self-violation of the discipline (the slice-022 self-violation law: "the codifying slice itself satisfies the rule it mints"). must-not-defer 1 + the genuine-contrast test do nothing about the co-located contradiction. **Proposed fix** (Builder, via TRI-1): (a) reword the four templates' hard-rule ASK line to structured options, making templates self-consistent with SOAD-1; OR (b) explicitly scope SOAD-1 to *skill* ask-points and state the CLAUDE.md hard-rule ASK is out of scope via an ADR-050 scoping clarification. Design-level scoping decision, not a Builder judgment call (deviations need an ADR).

## Severity adjustments

None. B1/M1/M2/m1/m2 severities all correctly calibrated.

## Notes

Confidence high. The first Critic's pattern is disciplined — the B1 catch (rejecting a Builder-asserted false precedent, verifying vs the actual enforcing test) is exactly the MEPD-1(b) discipline; the WebSearch premise verification (anthropics/claude-code#13830) is appropriately rigorous. Calibration observation: the first Critic checked the rule's *content* and the test oracle's *correctness* thoroughly but did not step back to *surface-consistency* (does the rule contradict its own host template). Single-slice blind spot, not yet a cross-slice `/critic-calibrate` pattern — the per-slice second-opinion gap DR-1 exists to fill. M-add-1 is a genuine missed finding (literal contradiction on the same shipped artifact), not manufactured. Reservation: triage could land on fix-option (b) (SOAD-1 scoped to skill ask-points; CLAUDE.md hard-rule ASK explicitly exempt) — then M-add-1 resolves as a one-sentence ADR-050 scoping clarification rather than a template rewrite. Either way the shipped artifact must not be internally self-contradicting on the discipline it codifies.
