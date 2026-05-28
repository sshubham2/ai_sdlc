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

---

# /critique-review pass 2 — EXPANSION DELTA META-REVIEW

**Reviewed by**: critique-review agent (DR-1) — pass 2 of 2
**Date**: 2026-05-28
**First-Critic verdict (pass 2)**: NEEDS-FIXES
**Dual-review verdict (pass 2)**: ACCEPT

## Summary (pass 2)

The pass-2 /critique on the expansion delta (AC#5+AC#6) is exemplary. All five findings (B1, M1, M2, m1, m2) are APED-1-grounded against synthetic prose with empirical falsification evidence, the severity calibration is correct, and the Builder draft dispositions resolve each concern with composed mechanisms that minimize cross-impact (M1 + M2 share `_point_4_codefence_body`; B1 lookahead correctly scoped before `#` comment). Independent APED-1 re-execution against the Builder draft regexes confirms all canonical and Builder-mistake forms classify correctly. No suspicious findings, no missed findings, no severity adjustments.

## Confirmed findings (pass 2)

First-Critic pass-2 findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (AC#6 no-`-b` regex falsified by canonical `# no -b; branch exists` comment): **CONFIRMED VALID + Blocker correct**. APED-1 re-execution against the original `(?!.*-b)` regex on the canonical line returns no match — the test would FAIL at Phase A red-test verification with no path to PASSING absent the fix. Blocker is correct calibration: this would have stalled the Builder at Phase A regardless of how trivial the fix is, because the contradiction is between the prose AND the test, not a discoverable bug in either alone (the prose is canonical-correct; the regex is canonical-correct against an idealized line; only their composition fails). Filing as Major would have under-flagged because Major implies "Builder discovers + fixes at red-test"; here, the red-test would FAIL with no obvious-to-Builder cause until comment-aware lookahead is reasoned about. Hendrickson APED-1 / Wiegers severity-discrimination both support Blocker. Builder draft `(?!(?:[^#\n]*?)-b\s)[^#\n]*` is verified empirically.

- **M1** (AC#5 token-search PASSES on prose-only narrative without codefence): **CONFIRMED VALID + Major correct**. APED-1 re-execution confirms: prose-only narrative mentioning all 4 tokens in order satisfies `.find()` chain on the original `_point_4_block` extraction. Same failure-mode-class as pass-1 M3 (comment-substring leak). Major is correct — a future Builder who reverts point 4 to STOP-prose while keeping a narrative paragraph that describes the sequence would silently PASS AC#5 and ship a non-codification. Adding the 5th anchor `git commit -m "scaffold(slice-NNN):` is a sound defense-in-depth tightening on top of the codefence-scoping fix.

- **M2** (`_point_4_block` no upper boundary, swallows trailing paragraphs): **CONFIRMED VALID + Major correct**. APED-1 evidence is correct. Composing the fix with M1 (both share `_point_4_codefence_body`) is the right shape — one mechanism, two findings closed, no fix-block fragmentation. Major is correct — same "false-pass" severity class as M1.

- **m1** (no cross-reference to slice-070 reflection L127): **CONFIRMED VALID + Minor correct**. The R-20 codification's comment cites the risk-register; symmetry says the switch-commit-switch codification should cite its empirical-provenance reflection. No structural failure-mode; just future-maintainer findability. Minor is correct.

- **m2** (NO-auto-stash discipline not structurally pinned): **CONFIRMED VALID + Minor correct**. The pass-2 first-Critic correctly cites slice-022 codify-empirical-discipline + AC#1 M3 ACCEPTED-FIXED guard-prefix anchor as precedent. Filing as Minor (not Major) is correct: the failure mode is a future Builder VOLUNTARILY inserting `git stash`, which has zero empirical precedent (N=5 cumulative shows zero stash insertions). The Minor classification correctly captures "load-bearing-enough-to-pin, not load-bearing-enough-to-block." The 3rd-test addition is cheap and forecloses the regression-class structurally, which is the right cost/benefit at Minor severity.

## Suspicious findings (pass 2)

No suspicious findings. The pass-2 first-Critic ran APED-1 execution against synthetic prose for B1, M1, M2 (three of five findings have direct regex-execution evidence). The remaining two (m1, m2) are structural-discipline observations with clear out-of-scope-vs-pin contrast. No over-reach detected on any finding.

## Missed findings (pass 2)

No missed findings. Independent re-application of the 8 dimensions against the POST-fix mission-brief + design.md surfaced no additional concerns. Specific re-checks performed:

- **TPHD-1 sub-mode (a) cross-surface sweep (test count +6→+7)**: mission-brief.md says `~1002/1002 PASS — 4 cp-r-scope tests + 3 switch-commit-switch-scope tests including no-stash discipline pin`; design.md says `+7 NEW tests` and `expected post-slice pytest count: 995 → 1002`; mid-slice smoke gate says `Expected: 6 PASS`. TF-1 plan has 8 rows. No stale "5 tests" / "+6" / "1001" anchors leaked. Sweep is clean.

- **`_point_4_codefence_body`-as-shared-mechanism (3-test consistency)**: All three tests use `_point_4_codefence_body` consistently. Composition risk (a bug in `_point_4_codefence_body` cascading through 3 tests) is mitigated by the helper's assertion fail-loud — if the codefence is missing, ALL three tests fail with a clear diagnostic at the helper, not three separate cryptic per-test failures. This is the right ergonomics for a shared mechanism.

- **B1 fix regex APED-1 verification** (independent execution against 10 synthetic cases): canonical no-`-b` line MATCHES; Builder-mistake `-b<space>` form does NOT match; `-b<tab>` form does NOT match (`\s` lookahead is permissive enough); no-comment valid form MATCHES; path containing `-b` literal (e.g., `/foo-bar/`) MATCHES (no false-negative on incidental `-b` in path names); `-branch` substring MATCHES. The only edge case where the regex over-matches is `-b=master` no-space, but per [git-worktree(1) — kernel.org](https://www.kernel.org/pub/software/scm/git/docs/git-worktree.html), git's `-b` short option does NOT accept `=` syntax — only `-b <branchname>` with space-separated argument is valid. `-b=master` is not a real Builder mistake form because git itself would reject it; the regex over-match on this synthetic form is therefore not a real-world false-negative. The B1 fix is empirically sound.

## Severity adjustments (pass 2)

No severity adjustments. The B1 Blocker classification is correct (would FAIL Phase A with no path to PASSING absent comment-aware lookahead reasoning); M1 + M2 Major classifications are correct (silent test-pass on non-codified prose is the canonical Major failure mode); m1 + m2 Minor classifications are correct (cheap-fix, no active failure path, discipline-hardening at slice-022 increment-axis).

## Notes (pass 2)

Confidence in this meta-review: high. The pass-2 first-Critic applied APED-1 execution to 3 of 5 findings (B1, M1, M2) with concrete falsification proof — gold-standard rigor for prose-as-contract review on regex-shape contracts. Independent APED-1 re-execution of the Builder draft B1 fix against 10 synthetic edge cases (including tab + no-space variants) confirms the comment-aware lookahead is empirically sound for real-world Builder-mistake forms. The composition of M1 + M2 fixes into a shared `_point_4_codefence_body` mechanism is correctly executed across all 3 consuming tests with consistent diagnostic ergonomics. TPHD-1 sub-mode (a) cross-surface sweep is clean. The pass-2 Critic correctly distinguished pass-1 m2 (PMI-1 contingency anachronism) from pass-2 m2 (no-auto-stash discipline pin) — no conflation. The original AC#1-AC#4 clearance from pass-1 is preserved untouched per scope discipline. ACCEPT verdict is intentional and warranted; manufacturing meta-findings on a genuinely strong pass-2 critique would be worse than the small set of confirmed-valids offered here.
