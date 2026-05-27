# Critique Review: Slice 074 codify-cp-r-in-branch-2-skill

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-28
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: ADJUST

## Summary

First Critic returned a substantive review (4M/4m) with APED-1-executed evidence (M2 + M3 regex shapes were tested against synthetic input before filing). All 8 findings are content-valid and the Builder fix-block correctly resolves each. The single calibration adjustment: M4 (MEPD-1 precedent axis confusion) is a documentation-clarity issue, not a decision-correctness issue; filing it as Major rather than Minor inflates severity for what is effectively a "future reader will be confused but no action goes wrong" defect. Two minor missed-coverage angles surfaced from independent re-review, both Minor-tier — neither would block the Builder draft.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B**: 0 Blockers — confirmed; nothing in the slice rises to Blocker. Surface is a single bash codefence + risk-register status flip + 2 new test modules.
- **M1** (recursive-self-application bootstrap contradiction): **CONFIRMED VALID + correct severity**. Bootstrap order at `skills/build-slice/SKILL.md:37` (CRP-1 slice-026 exception) is canonical and the slice-074 mission-brief's original recursive-self-application claim was genuinely unfulfillable at Phase A. Major is correct — without the fix, the Builder would have either invented false evidence or stalled at the AC verification step. Builder draft (reframe as bootstrap exception + add §"Bootstrap framing" sub-section to design.md) is the canonical CRP-1/ADR-024 mirror.
- **M2** (section-extraction regex over-terminates on `## ` codefence comments): **CONFIRMED VALID + correct severity**. APED-1-executed evidence is real (synthetic input demonstrated truncation to 34 chars). The tightening to `(?=^## [A-Z])` (markdown-H2-capital-letter convention) is sound; matches existing markdown convention without false-negatives on real-world H2 headings (every standard H2 starts with a capital). Major is appropriate because the latent regex would silently mask real prose changes — a structural-pin test that lies about what it pins is worse than no test.
- **M3** (cp -r regex over-matches on comment-only mentions): **CONFIRMED VALID + correct severity**. APED-1 evidence is correct (a `# WARNING: do NOT use cp -r diagnose-out outside ...` comment satisfies the bare regex). The if/then guard-prefix anchor cross-pins AC#1 + AC#2 and forecloses the comment-substring leak. Major is appropriate — a structural-pin that silently accepts a code-deleted-replaced-by-comment refactor is functionally equivalent to no pin.
- **m1** (TF-1 plan +4 vs 5-row arithmetic): **CONFIRMED VALID + Minor appropriate**. Documentation clarity.
- **m2** (mission-brief PMI-1 contingency anachronism post-EXCLUDE-decision): **CONFIRMED VALID + Minor appropriate**. Tidy-up only.
- **m3** (chained-form vs if/then/fi exit-status under future set -e hardening): **CONFIRMED VALID + Minor appropriate**. Genuine latent fragility, cheap fix; cross-impacts M3 in single fix block (Builder draft caught this co-impact correctly).
- **m4** (TF-1 row 4 prose vs function name): **CONFIRMED VALID + Minor appropriate**. PTFFD-1 status FILE-level degradation is documented; cite-the-function-name is the canonical convention.

## Suspicious findings

No suspicious findings. Every first-Critic finding has supporting evidence (5 of 8 with APED-1 executed regex / synthetic-input proof; the remaining 3 with direct file-path citations). No over-reach detected.

## Missed findings

Two minor coverage gaps surface from independent re-review of design.md POST-fix. Neither rises to Major; both are Minor-tier suggestions for the Builder.

- **m-add-1**: **Multi-line if/then/fi form is rejected by the structural-pin test, but design.md does not record this as an intentional constraint** — the AC#2 test regex `r'^\s*if \[ -d[^\n]*\]\s*;\s*then\s+cp -r [^\n]*;\s*fi'` requires `; then` and `; fi` on the SAME line (semicolons + same-line constraint via `[^\n]*`). A POSIX-legitimate alternative the Builder might write as a "more readable" refactor:
  ```bash
  if [ -d "$repo_root/diagnose-out" ]
  then
      cp -r "$repo_root/diagnose-out" ./
  fi
  ```
  would FAIL the structural-pin (no `;` before `then`, multi-line). This is intentional — design.md L10 specifies the single-line form — but design.md should explicitly note the single-line constraint is pinned as a contract surface (per Hendrickson, *Explore It!* APED-1 — verification surface drift is the canonical test-vs-prose pitfall). Cheap fix: add one sentence to design.md §"Test contracts" docstring annotation: "Single-line `if [ -d ... ]; then ... ; fi` form is pinned; multi-line POSIX equivalents are out-of-scope (RSAD-1 byte-exact-match discipline)."
  - **Framework**: Hendrickson APED-1 / RSAD-1 byte-exact-match discipline (slice-071 M6 prevention pattern cited in mission-brief L46).
  - **Recommended severity**: Minor.
  - **Builder draft**: **ACCEPTED-FIXED** — design.md §"Test contracts" docstring of `test_cp_r_lines_use_if_then_guard_for_source_dir_absence` gains an explicit single-line-form-pinned note citing RSAD-1.

- **m-add-2**: **No "Phase A/B/C" glossary in design.md — the terminology is informal-mapping to /build-slice Steps 1-7 and could mislead a future Critic comparing against the canonical /build-slice numbering** — design.md L107-108 + L116 use "Phase A/B/C" terminology (Phase A = prereq check; Phase B/C = OSDG-1 forward-sync at Step 4 cp-to-installed + Step 6 drift test). The actual /build-slice SKILL.md uses Step 1-7 numbering; "Phase A/B/C" is an informal layer borrowed from the mission-brief vocabulary. A future reader (or `/critic-calibrate` slice) reading design.md without the cross-mapping might cross-reference against /build-slice Steps and find no "Phase B/C" anchor. Cheap fix: add one sentence to §"Bootstrap framing" — "Phase A = `## Prerequisite check`; Phase B/C = Step 4 task-execution cp-to-installed + Step 6 pre-finish drift test verification." Sequencing concern (will slice-075 Phase A actually find the codified prose installed?) is satisfied: the cp-to-installed at slice-074 Step 4 + Step 6 drift test PASS + /commit-slice merge all happen before slice-075 begins, so the installed copy IS codified by slice-075's invocation.
  - **Framework**: Fowler *Refactoring* terminology-vs-source-truth discipline (informal vocabulary that doesn't match the executed contract is a future-maintenance liability).
  - **Recommended severity**: Minor.
  - **Builder draft**: **ACCEPTED-FIXED** — design.md §"Bootstrap framing" gains a Phase-A/B/C-to-Step-1-7 glossary sentence + explicit sequencing-confirmation that slice-075's Phase A finds the codified prose installed.

## Severity adjustments

- **M4** (MEPD-1 EXCLUDE rationale precedent-axis confusion): **SEVERITY-WRONG: filed as Major, recommend Minor**. The concern is real (the slice-068/070/071 precedent comparison conflates rule-mint axis with surface-class axis; slice-066's same-surface INCLUDE is a missing distinguisher). But the CONCLUSION (EXCLUDE) is correct on independent grounds (R-20 candidate-(a) operationalization mints no new methodology rule; PMI-1 atomic bump not needed; no v0.73.0 entry; no shippability row #74). A future reader who reads the design.md rationale and concludes "this is EXCLUDE because slice-068/070/071 were EXCLUDE" reaches the right answer for an arguably-wrong reason — they would still ship the EXCLUDE-correct artifacts. Compare to M1 + M2 + M3 which would have produced functionally-wrong outcomes (unfulfillable AC; silently-truncated section; code-deleted-by-refactor passes test). M4's failure mode is "future Critic confusion in 6 months when comparing slice-074 to slice-066"; M1-M3's failure modes are "this slice ships broken." The severity gap is real. Builder draft fix (add one differentiating-axis sentence) is correct in substance; the fix would have been correct under Minor classification too — severity adjustment does not change disposition.
  - **Framework**: Wiegers *More About Software Requirements* — severity calibration discriminates "produces wrong output" (Major) from "produces correct output via opaque reasoning" (Minor).
  - **Recommended severity**: **Minor (was: Major)**.
  - **Builder draft (severity-only)**: **ACCEPT-ADJUSTMENT** — at TRI-1, record M4 in the triage table as severity Minor (informationally tagged "was-Major-per-first-Critic; SEVERITY-WRONG per /critique-review; meta-Critic recommends Minor"). Disposition stays ACCEPTED-FIXED (unchanged). The triage_audit verdict-pattern remains the same.

## Notes

Confidence in this review: high. The first Critic applied APED-1 execution to the two regex Majors (M2 + M3) — both empirically demonstrated against synthetic input before filing — which is the gold-standard rigor for prose-as-contract review. M1's bootstrap-order analysis correctly cited CRP-1 / ADR-024 slice-026 precedent at `skills/build-slice/SKILL.md:37` and would have been a real blocker for the Builder at /build-slice Phase A absent the fix. The single severity miscalibration (M4 → Minor) is calibration-grade, not disposition-grade; the Builder draft's ACCEPTED-FIXED is correct regardless of severity. Two missed minors surfaced (m-add-1 single-line if/then/fi constraint not recorded; m-add-2 Phase-A/B/C glossary missing), both documentation-clarity-tier and neither blocking. Overall the first Critic's coverage is genuinely solid on a slice that was always going to be small — single-surface prose addition + structural-pin tests + risk-register status flip. The TPHD-1 sub-mode (a) N=7 cumulative regression-introduction pattern (per slice-073 reflection L26) was checked against the Builder's 8-fix block: no stale `[ -d ... ] && cp -r` references leaked outside narrative-of-the-switch context; the regex tightenings in M2 + M3 are internally consistent with the prose contract in mission-brief AC#1 + AC#2; the cross-impact between m3 (form switch) and M3 (regex anchor) was correctly handled as a single coordinated fix. ADJUST verdict (M4 severity demotion + two Minor missed findings) is intentionally narrow — the Critic's review on this slice is genuinely strong and inflating findings to justify a second pass would be worse than the small adjustments offered here.
