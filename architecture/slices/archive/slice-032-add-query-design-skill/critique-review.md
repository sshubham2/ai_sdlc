# Critique Review: Slice 032 add-query-design-skill

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-17
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong — the three Blockers (SCMD-1 grammar, SCMD-1 decoupling, slice-022 self-violation) are real, correctly severed, and the fixes are sound (B2 verified empirically clean; B3 verified NOT theater). One missed finding extends M1: INSTALL.md hard-codes the skill count at **three** sites (L19, L185, L218), but M1 / design / mission-brief addressed only L185 — the same single-site blind spot the Critic correctly diagnosed as a defect class, replicated two more times in the same file.

## Confirmed findings

- **B1** (SCMD-1 6-col grammar) — confirmed; Blocker appropriate. Verified `_MACHINE_CMD_IDX = 5`, `_SEGMENT_RE`, `test_real_catalog_scmd1_clean` asserts zero violations every row → non-conformant cell blocks finish. Fix specifies correct interpreter-anchored Machine-cmd.
- **B2** (new drift test SCMD-1 classification) — confirmed; Blocker appropriate. Meta-Critic empirically ran `tools.shippability_decoupling_audit` against live catalog: existing `*_skill_drift.py` `Path.home()` tests classify clean (0 incidental, 0 violations, 31 rows / 343 fns); `classify_fn` only flags archive/`build-checks.md` `_INCIDENTAL_SHAPES`; `skills/query-design/SKILL.md` path contains none → new test inherits clean. Builder's verified-exemption reasoning empirically correct.
- **B3** (slice-022 self-violation) — confirmed; Blocker appropriate; fix is NOT theater. SKILL.md prose IS the executed artifact (Claude reads installed markdown at runtime); no separate behavioral implementation can drift from it. Drift test (byte-equality) + prose-pin (required clauses present) jointly the strongest deterministic guarantee available for an LLM-prose skill; an LLM-output behavioral harness would be the inverse slice-022 anti-pattern.
- **M1** (INSTALL.md hard-count drift) — confirmed real, right severity, but **incomplete scope** → see M-add-1. The L185 portion is correct.
- **M3** (PCA-1 out-of-loop by-analogy) — confirmed; Major appropriate. Verified iteration boundary; "MUST NOT add Pipeline position block" prevents defensive over-add.
- **m1** (QD-1 prose-only no bespoke pin) — confirmed; Minor appropriate; declining bespoke pin avoids over-build.

## Suspicious findings

None. Every first-Critic finding survives closer reading. M2's documented-decision OVERRIDE is sound (no skill in repo uses `allowed-tools`; introducing for one skill genuinely unprecedented; inline-execution efficacy unverified). m2's OVERRIDE empirically airtight (ADR-032 L8 byte-identically `supersedes: null`, matching ADR-031; `supersede_audit.py` parses the sentinel).

## Missed findings

- **M-add-1: INSTALL.md hard-codes the skill count at THREE sites; M1/design/mission-brief address only ONE** — Severity **Major** (same defect class & severity as M1; a distinct unaddressed surface → extends, not re-grades). INSTALL.md L19 (`**24 drop-in skills**`), L185 (`(24 skills, 5 agents, …)`), L218 (`markdown skill files (24)`) all hard-code 24; 24 skill dirs today → `query-design` makes truth 25 at all three. No test pins any. M1's fix + design "What's modified" + mission-brief must-not-defer were all single-site (L185) → Builder would ship L19+L218 stale, the exact silent-prose-drift defect M1 names, surviving at 2/3 instances. **Proposed fix**: broaden design "What's modified" + mission-brief must-not-defer to all three sites; add a pre-finish grep guard for a stale literal skill count. **Builder draft**: ACCEPTED-FIXED — design.md "What's modified" INSTALL.md item now enumerates L19/L185/L218 + count-agnostic rewrite of all three; mission-brief must-not-defer broadened; pre-finish gate adds `grep -nE '\b2[45]\b.*skill' INSTALL.md` shows no stale literal count.

(No other missed findings. Verified: `/status` SKILL.md enumerates no skill count; CSP-1 is Heavy-mode-only, correct no-op in this Standard repo; `_index.md`, README, `test_methodology_changelog.py` carry no skill-count assertion. INSTALL.md is the only stale-count surface, and it is triple.)

## Severity adjustments

None. B1/B2/B3 all genuinely gate `/build-slice` or pre-finish — correctly Blockers, none over-filed. M1/M2/M3 correctly Majors; none a latent Blocker. m1/m2 correctly Minors.

## Notes

Confidence high. B2 verified empirically (live SCMD-1 audit: 0 incidental, 0 violations, drift-tests clean); m2 verified empirically (ADR-032 L8 == ADR-031 sentinel). B3 is NOT a slice-022 trap — slice-022's law is "prose assertion standing in for verifying code behavior the prose describes"; here the prose IS the implementation, so prose-pin + byte-equality drift test is the strongest available deterministic guarantee. Calibration observation: the first Critic's only weakness this slice was an *intra-file scope-truncation* (correctly named the silent-prose-drift defect class at INSTALL.md but stopped at the first occurrence); the mission-brief inherited the identical truncation. A single contained extension, not a calibration-grade pattern.
