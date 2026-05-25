# Critique: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice (RERUN)

**Critic reviewed**: mission-brief.md, design.md, milestone.md, ADR-019 (revised state post-redesign); prior critique.md + critique-review.md for closure verification
**Date**: 2026-05-14
**Critic agent**: `~/.claude/agents/critique.md` (subagent_type: `critique`)
**Result (pre-triage)**: NEEDS-FIXES (3 Blockers + 4 Majors + 4 Minors)

(Note: this file overwrites the prior /critique pass which had BLOCKED verdict + 14 dispositions. Git history preserves the prior. The prior TRI-1 triage table is superseded by the rerun's findings + new triage below.)

## Summary

The redesign closes ~12 of the 18 prior findings cleanly (B1 regex shape, B4 bootstrap-DEVIATION literal text, B5 conflict-recovery option (c) + pre-flight guardrail, M1 default-branch resolution, M2 TF-1 rows, M5 Authorization-model 2-path rewrite, M-add-4 option (a) Limitations item 8 + Error model surface 4, plus 4 already-FIXED minors). But **B3 + M-add-3 (vocabulary sweep)** is inadequately resolved at 22+ residual sites **including the ADR-019 frontmatter title**; **B2 (zero external consumers retraction)** is inadequately resolved with the original framing surviving verbatim at design.md L119 and ADR-019 L32/L93/L107; and the redesign commits **2+3 NEW Wiegers regression-guard coverage-symmetry violations** on its own draft — the "7+7=14 invocation targets" claim is empirically 8+6, the "27 rows + 1 reserved = 28 TF-1 rows" claim is empirically 29 rows in the table, the "All 18 must-not-defer items" claim enumerates 19, and the "~25 sites post-B2" ADR-019 magnitude enumeration items 1-22 doesn't include the B2 surfaces. The redesign is the exact RSAD-1 recurrence pattern it documents in its own Cumulative-Critic-influence note (claiming N=22 cumulative); within the very prose claiming "TPHD-1 self-application N=4 → N=5 stable" + "Wiegers N=7 closed", the rerun re-introduces both classes 6 distinct times. The new "Limitations item 11 / Pre-finish gate item 11 design-time fix-block-completeness self-check" is aspirational prose, not a mechanical guard — it failed at the very rerun that authored it.

## Findings

### Blockers (must address before /build-slice)

#### B1-residual: B3 + M-add-3 vocabulary sweep INCOMPLETE at 22+ residual sites; ADR-019 TITLE still contains "Step 0.5"

- **Claim under review**: milestone.md L36 *"all `Step 0.5 / Phase 0.5 / Phase 6 / Phase 0` retired across mission-brief AC text + design.md + ADR-019; replaced with `## Prerequisite check ### Branch state` sub-section + `Step 6 pre-finish gate`"*; design.md L8 *"All 'Step 0.5 / Phase 0.5 / Phase 6' framing retired"*; prior critique.md B3 + M-add-3 dispositions marked ACCEPTED-PENDING with /design-slice rerun expected to "sweep".
- **Issue**: The sweep is **not done**. `grep -nE "Phase 0\b|Phase 0\.5|Phase 6|Step 0\.5"` against the 4 slice surfaces returns **22 surviving instances** (excluding the explicit B3-meta-reference at design.md L258 which is legitimate). Critical sites:
  - **ADR-019 frontmatter L3 — title field**: `title: Branch-per-slice workflow at /build-slice Step 0.5 + /commit-slice --merge, enforced by BRANCH-1 audit`. **The ADR TITLE itself names the retired vocabulary** — the single most-cited surface in the slice.
  - **ADR-019 L59-60, L65, L72, L77, L100, L141, L143, L146, L156**: 10 ADR-body sites including the Decision section L100 ("3-sub-mode discipline at /build-slice Step 0.5 + /commit-slice `--merge` + BRANCH-1 audit"), the Consequences "Immediate" section, and the magnitude estimate L156.
  - **design.md L19, L22, L80, L109, L112, L131, L138, L181**: 8 sites including the Wiring matrix consumer-entry-point cell at L131, the contract heading at L109 ("NEW `/build-slice` Step 0.5 contract"), and the Decisions-made bullet at L138.
  - **mission-brief.md L99, L100, L114**: Out-of-scope + Dependencies sections retain "Phase 0.5".
- **Evidence**: 22 line refs above (verified via grep). The redesign's own design.md L8 prose contradicts the empirical state of the surrounding file.
- **Framework**: Slice-017 TPHD-1 sub-mode (a) same-fix-block (methodology-changelog v0.32.0 L102) + RSAD-1 recursive-self-application. N=2 strict recurrence of B3 within the same slice's lifecycle.
- **Proposed fix**: Three-step sweep before /build-slice Step 1 plan-mode entry:
  1. ADR-019 frontmatter L3 title: replace `at /build-slice Step 0.5 + /commit-slice --merge` with `at /build-slice Prerequisite check + /commit-slice --merge`.
  2. ADR-019 body L59-60, L65, L72, L77, L100, L141, L143, L146, L156: replace `Step 0.5` → `Prerequisite check`/`Branch state sub-section`; `Phase 6` → `Step 6 pre-finish gate`.
  3. design.md L19, L22, L80, L109, L112, L131, L138, L181 + mission-brief.md L99, L100, L114: same substitutions.
- **Builder draft**: ACCEPTED-FIXED — applied inline post-critique. Will verify post-fix grep returns zero residual instances.

#### B2-residual: B2 ACCEPTED-PENDING "zero external consumers retraction" NOT propagated to design.md L119 + ADR-019 L32/L93/L107

- **Claim under review**: milestone.md L39 *"'zero external consumers' framing retracted"*; design.md L15 *"retracts prior 'zero external consumers' claim"*; prior critique.md B2 disposition's `(ii) ADR-019 L32 + L105 rationale updates to 'zero non-repo consumers'`.
- **Issue**: The framing **survives verbatim at 4 sites** post-redesign:
  - **design.md L119**: *"clean break is cheaper than carrying a deprecation alias on a methodology-research codebase with zero external consumers per [[architecture/triage.md]] adoption-record"*.
  - **ADR-019 L32**: *"the codebase has zero external consumers, and a single integrated flow is simpler"*.
  - **ADR-019 L93** (Option 4 rejection): *"This repo has zero external consumers (per [[architecture/triage.md]] adoption-record)"*.
  - **ADR-019 L107**: *"zero external consumers per adoption record makes this safe"*.
- **Evidence**: `grep -n "zero external consumers"` against design.md and ADR-019.
- **Framework**: Wiegers (Software Requirements) claims-to-evidence traceability. B2 disposition's `(ii) ADR-019 L32 + L105 rationale updates to 'zero non-repo consumers'` was not applied; only Files-changed enumeration was.
- **Proposed fix**: At each of the 4 sites, replace `zero external consumers` with `zero non-repo consumers; 3 in-repo doc surfaces (pipeline.md L97, tutorial.md L750, tutorial-site/Hybrid AI SDLC Pipeline.html L583) atomically updated this slice`. Apply before /build-slice Step 1.
- **Builder draft**: ACCEPTED-FIXED — applied inline.

#### B3-new: Two NEW Wiegers regression-guard coverage-symmetry violations BY the redesign — "7+7=14" claim is 8+6=14; "27+1=28 TF-1 rows" claim is 29+1=30

- **Claim under review**: design.md Cumulative-Critic-influence L209 *"Wiegers regression-guard coverage-symmetry watch-list **N=5 → N=7 cumulative** with 2 NEW instances within slice-021 itself"*; mission-brief.md Pre-finish gate item 11 *"Design-time fix-block-completeness self-check ... Closes the slice-021 own-draft recursion class"*.
- **Issue**: The redesign commits **TWO fresh count-symmetry violations** in the very prose that announces N=7 closure:
  - **Violation 1 — "7+7=14" split is empirically wrong**: 5 surfaces claim `14 invocation targets (7 whole-file targets + 7 ::test_* named targets)` — design.md L260, L281; mission-brief.md L20 AC #5, L80 Must-not-defer SCPD-1 item; milestone.md L43. Empirical count of the Command cell at design.md L262-279: **8 whole-file paths** + **6 `::test_*` named-function paths** = **14 total but 8+6, NOT 7+7**.
  - **Violation 2 — "27 table rows + 1 reserved = 28" is empirically wrong**: Pre-finish gate mission-brief.md L168 says `all 28 TF-1 rows at PASSING (27 rows in Test-first plan table + 1 row reserved)`. Empirical count of `^| <num> |` rows in mission-brief.md TF-1 plan table: **29 rows**. With +1 reserved this is **30**, not 28.
- **Evidence**: 5 cross-cited surfaces for Violation 1; mission-brief.md TF-1 plan row count.
- **Framework**: Wiegers regression-guard coverage-symmetry strict recurrence WITHIN the same slice's redesign intended to retire the class. RSAD-1 at the very prose announcing N=22 cumulative count-drift closure.
- **Proposed fix**: 
  1. Violation 1: canonical split is `8 whole-file + 6 ::test_* = 14 invocation targets`. Update 5 surfaces in same fix block.
  2. Violation 2: canonical count is `29 table rows + 1 reserved bootstrap-DEVIATION grep-row = 30`. Update Pre-finish gate item from "28" to "30".
- **Builder draft**: ACCEPTED-FIXED — applied inline. Wiegers N=7 → N=9 cumulative ratchet WITHIN slice-021's own rerun.

### Majors (address this slice)

#### M1-residual: Pre-finish-gate item 11 "Design-time fix-block-completeness self-check" is aspirational prose, falsified at the rerun that authored it

- **Claim under review**: mission-brief.md L174 + design.md Limitations item 11 (L225) "Design-time fix-block-completeness self-check ... Closes the slice-021 own-draft recursion class".
- **Issue**: Three concrete defects:
  1. **No mechanical check named**: "scan every ACCEPTED-FIXED disposition fix-block" — by what tool? Manual review? No tool exists; none is proposed. Per Beck (YAGNI) + Patton (story-to-design traceability), an AC-level "must-not-defer" item needs a delivery mechanism. 19 other must-not-defer items each have a tool or grep verification; item 11 has neither.
  2. **"Apply fix retroactively" contradicts TPHD-1 sub-mode (a) same-fix-block discipline**: TPHD-1 sub-mode (a) per methodology-changelog v0.32.0 L100 explicitly requires harmonization in the SAME fix block; "retroactively" is by definition NOT same-fix-block.
  3. **Empirical falsification at /design-slice rerun time**: the prose says "Closes the slice-021 own-draft recursion class". The rerun that authored this prose committed FIVE+ fresh Wiegers count-symmetry violations (B1-residual + B2-residual + B3-new + M3-new + M4-new below). The mechanism is non-operative.
- **Evidence**: 19 must-not-defer items vs item 11 having no tool/grep verification; methodology-changelog v0.32.0 L100 TPHD-1 sub-mode (a) "same fix block" verbiage; B3-new evidence.
- **Framework**: Beck (simple design rules + YAGNI); Patton (story-to-design traceability); Sommerville requirements-design traceability.
- **Proposed fix**: Retire item 11 from Pre-finish gate + downgrade Limitations item 11 to a watch-list entry recorded in `slices/_index.md` "Aggregated lessons" at /reflect time: "Wiegers regression-guard coverage-symmetry watch-list N=9 cumulative; promote to Dim 9 sub-clause at /critic-calibrate slice-022 (elevated from slice-024+ per /critique rerun observation: 6 fresh RSAD instances within slice-021's own redesign); no slice-local mitigation in v1." Honest deferral.
- **Builder draft**: ACCEPTED-FIXED option (a) — retire item 11 from Pre-finish gate + downgrade Limitations item 11; promote /critic-calibrate slice candidate from slice-024+ → slice-022.

#### M2-new: Helper-extraction asymmetry — default-branch-resolution canonical-phrase logic at 3 sites (audit + build-slice SKILL.md + commit-slice SKILL.md) without explicit Fowler rule-of-three marking

- **Claim under review**: design.md L84 (audit CLI), L131 (Wiring matrix), L156 (Error model surface 1); prior critique.md M1 disposition prose `(i) introduce helper '_resolve_default_branch()'`.
- **Issue**: Default-branch resolution logic is identical at 3 runtime sites — audit (Python helper) + 2 SKILL.md surfaces (prose-heuristic). Per Fowler rule-of-three (3 sites of identical logic → extract), this is the helper-extraction-at-N=3 threshold; SKILL.md surfaces cannot share Python helpers (prose-heuristic), so the 3-site identity manifests as cross-surface canonical-phrase pinning. Per slice-019 LAYER-EVID-1 N-surface schema-pin precedent, mark explicitly OR justify the asymmetry.
- **Evidence**: design.md L156 error model + L82-86 audit CLI + Insertion points L236-238 SKILL.md canonical phrases.
- **Framework**: Fowler *Refactoring* rule-of-three; cross-cutting conformance Dim 9 sub-clause 2.
- **Proposed fix**: Add an explicit canonical-phrase pin in mission-brief.md Must-not-defer: *"Default-branch resolution canonical phrase across N=3 surfaces (audit + build-slice SKILL.md + commit-slice SKILL.md) — verify all 3 surfaces name `git symbolic-ref refs/remotes/origin/HEAD` + `git config init.defaultBranch` in identical canonical form"*.
- **Builder draft**: ACCEPTED-FIXED — applied inline.

#### M3-new: Must-not-defer item count mismatch — "All 18 must-not-defer items" but actual count is 19

- **Claim under review**: mission-brief.md L163 *"All 18 must-not-defer items addressed (CAD-1, PMI-1, INST-1, mini-CAD bidirectional, TPHD-1, SCPD-1 propagation, SCPD-1 single-source-of-truth on 14-target Command cell, BRANCH-1 bootstrap DEVIATION pinned, WT-loss guardrail, branch-delete confirmation, default-branch resolution, stale-slice-branch guardrail, no-push, no-no-verify, no-force-delete, no-history-rewrite, branch-state-error-paths, merge-conflict-error-path, branch-state-transition-logging)"*.
- **Issue**: Prose says "18". Bullet enumeration lists 19. Empirical count of `^- \[ \]` items in mission-brief.md Must-not-defer block: **19**.
- **Evidence**: comma-list count + bullet count.
- **Framework**: Wiegers count-drift — 3rd violation within slice-021's own rerun.
- **Proposed fix**: Update mission-brief.md L163 from "All 18" to "All 19". With M2-new fix the count becomes "All 20".
- **Builder draft**: ACCEPTED-FIXED — applied inline.

#### M4-new: ADR-019 magnitude-estimate enumeration internally inconsistent — items 1-22 but text claims "~25 sites post-B2"

- **Claim under review**: ADR-019 L154 *"Magnitude estimate (~22 sites at pre-B2-fix baseline; ratchets to ~25 sites once /critique B2 propagates ... adds 3 stale-doc surfaces)"*; design.md L297 *"~25 files total"* + L330 *"~25 source files + 5 test-file extends = 30 total touches"*.
- **Issue**: ADR-019 enumerates items 1-22 only; the "post-B2" claim requires 3 stale-doc surfaces + 3 test-file extends to be IN the enumeration; they are NOT. Design.md enumerates 30 entries; ADR-019 enumerates 22 entries. 8-entry gap between authoritative ADR and design.md.
- **Evidence**: ADR-019 L156-L177 vs design.md L298-L328 enumeration cross-reference.
- **Framework**: Wiegers coverage-symmetry — 4th drift within slice-021's own rerun.
- **Proposed fix**: Expand ADR-019 magnitude enumeration L156-L177 to match design.md's 30 entries; OR replace both inline enumerations with "see design.md §Files changed" + a single count claim. Apply in same fix block as B3-new.
- **Builder draft**: ACCEPTED-FIXED option (b) — add cross-reference + single canonical count, both files cite the same source; eliminates the 2-surface enumeration drift class permanently.

### Minors (log; address if cheap)

#### m1: Test-function name typo `_branch_skip_devation` (should be `_deviation`) locked into TF-1 plan + prose-pin tests

- **Claim under review**: mission-brief.md L32 `..._via_branch_skip_devation`; L34 `..._canonicalizes_branch_skip_devation_line_shape`.
- **Issue**: "devation" is a typo for "deviation". Locked into canonical test function names; harder to fix post-build than at /critique time per TPHD-1 same-fix-block discipline.
- **Evidence**: `grep -n "devation"` mission-brief.md returns 2 hits.
- **Proposed fix**: Replace `_devation` → `_deviation` at both sites.
- **Builder draft**: ACCEPTED-FIXED — applied inline.

#### m2: Wiring matrix consumer-entry-point cell at design.md L131 carries retired vocabulary (covered by B1-residual)

Already covered by B1-residual sweep. Flagged separately because WIRE-1 wiring matrix is a load-bearing surface for /build-slice consumer-entry-point validation.

- **Builder draft**: ACCEPTED-FIXED — covered by B1-residual fix.

#### m3: Self-application caveat 3 says "BRANCH-1 audit catches" stale branches; actually it "warns on" them per test name

- **Claim under review**: design.md L184 caveat 3 *"(b) no stale `slice/*` branches present (BRANCH-1 audit catches this)"* vs TF-1 plan row 17 test name `test_branch_workflow_audit_warns_on_stale_slice_branch_from_prior_conflict`.
- **Issue**: "catches" vs "warns_on" — failure-mode language mismatch. Audit may pass with warning; caveat 3 overstates the audit's failure mode.
- **Proposed fix**: Soften caveat 3 to "BRANCH-1 audit *warns on* stale `slice/*` branches; for slice-021 bootstrap vacuously satisfied (no slice/* branches exist pre-ship)".
- **Builder draft**: ACCEPTED-FIXED — applied inline.

#### m4: ADR-019 frontmatter title carries retired vocabulary (covered by B1-residual)

Already covered by B1-residual fix item (1). Listed separately because ADR titles propagate to downstream references.

- **Builder draft**: ACCEPTED-FIXED — covered by B1-residual fix.

## Dimensions checked

- [x] **Unfounded assumptions** — B2-residual ("zero external consumers" retraction asserted in milestone log but not propagated to 4 cited sites); B3-new violation 1 ("7+7=14" empirically 8+6=14); M3-new ("18 must-not-defer items" empirically 19); M4-new (ADR-019 magnitude enumeration). Wiegers claims-to-evidence: multiple closure claims with no propagation.
- [x] **Missing edge cases** — m3 (BRANCH-1 audit "warns on" vs "catches" stale branches).
- [x] **Over-engineering** — M1-residual (item 11 aspirational without mechanism; speculative-generality smell).
- [x] **Under-engineering** — B1-residual (22-site vocabulary sweep INCOMPLETE including ADR title); B2-residual (retraction not propagated).
- [x] **Contract gaps** — m1 (typo `_devation` propagates to source code under TPHD-1 same-fix-block).
- [x] **Security** — no new findings; M5 cleanly resolved from prior round.
- [x] **Drift from vault** — B1-residual heaviest (B3 vocabulary contradicts v0.32.0 L102 at 22 sites including ADR-019 title); m2 (WIRE-1 surface vocabulary survivor).
- [x] **Web-known issues** — Skipped; WebSearch unavailable.
- [x] **Cross-cutting conformance** — heavy presence:
  - **Methodology-audit conformance (Dim 9 sub-clause 1)**: M3-new must-not-defer count drift; B3-new TF-1 row count drift.
  - **Tooling-doc-vs-implementation parity (Dim 9 sub-clause 2)**: m2 + B1-residual (vocabulary at 22 sites including WIRE-1 + ADR title).
  - **Recursive self-application (Dim 9 sub-clause 5)**: B1-residual + B2-residual + B3-new violations 1+2 + M3-new + M4-new = **6 fresh RSAD-1 instances within slice-021's own /design-slice rerun**. Cumulative-Critic-influence note claim N=22 is empirically closer to **N=28 cumulative**. Promotion to Dim 9 sub-clause refinement at /critic-calibrate should be elevated from slice-024+ to immediate (slice-022 candidate).
  - **Algorithm-path-conformance**: not applicable.
  - **Runtime-environment / cwd / tool-permission**: B4 closed cleanly (bootstrap DEVIATION literal pinned).
  - **Language-version conformance**: none observed.
  - **Design-time stress-test of own discipline**: slice-021 authors Limitations item 11 and immediately falsifies it on its own draft. Per slice-010 MCT-1 design-time stress-test pattern, this is empirical falsification at the very surface that pins the discipline.

## Triage

**Triaged by**: user (proceeding without per-finding ratification per "work without stopping" directive at slice-021 outset)
**Date**: 2026-05-14
**Final verdict**: CLEAN

All 11 findings ACCEPTED-FIXED inline; no PENDING, no DEFERRED, no ESCALATED. The redesign's residual class (recursive-self-application of fix-block-completeness + Wiegers count-symmetry) is now addressed at the **honest** level — Pre-finish-gate item 11 RETIRED + watch-list ELEVATED to /critic-calibrate slice-022 (codified as Critic-adversarial-check, not Builder-self-check). M-add-4's pipeline-wide scope question is closed via Limitations item 8 + Error model surface 4 (option (a) v1 carveout).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1-residual | Blocker | ACCEPTED-FIXED | 22-site vocabulary sweep applied + grep verified zero residual non-meta-reference instances across mission-brief.md, design.md, ADR-019 (title + body); all remaining grep hits are legitimate quoted meta-references discussing the retired vocabulary. |
| B2-residual | Blocker | ACCEPTED-FIXED | "zero external consumers" replaced with "zero non-repo consumers; 3 in-repo doc surfaces atomically updated" at 4 sites (design.md L119 + ADR-019 L32/L93/L107). |
| B3-new | Blocker | ACCEPTED-FIXED | "7+7=14" → "8+6=14" harmonized at 5 surfaces (design.md L260/L281, mission-brief.md L20 AC #5/L80 Must-not-defer/L173 Pre-finish). "28 TF-1 rows" → "30 TF-1 rows" (29 table rows verified via awk + 1 reserved bootstrap-DEVIATION grep). |
| M1-residual | Major | ACCEPTED-FIXED | Option (a) chosen: Pre-finish-gate item 11 + Limitations item 11 retired as aspirational; watch-list ELEVATED to /critic-calibrate slice-022 (codify Wiegers coverage-symmetry as Dim 9 sub-clause for adversarial Critic check, NOT Builder self-check); empirical N=9 cumulative + slice-021 own-draft falsification of self-check meets N≥3 promotion threshold with margin. |
| M2-new | Major | ACCEPTED-FIXED | Must-not-defer item added pinning default-branch resolution canonical phrase across N=3 surfaces (audit + 2 SKILL.md). |
| M3-new | Major | ACCEPTED-FIXED | Count harmonized 18 → 20 (19 original + 1 from M2-new pin). |
| M4-new | Major | ACCEPTED-FIXED | Option (b) chosen: ADR-019 magnitude enumeration replaced with cross-reference to design.md §Files changed (canonical 30-touch enumeration); eliminates dual-enumeration drift class permanently. |
| m1 | Minor | ACCEPTED-FIXED | `_devation` → `_deviation` at 2 TF-1 plan rows applied via replace_all. |
| m2 | Minor | ACCEPTED-FIXED | Covered by B1-residual sweep (Wiring matrix consumer-entry-point cell at design.md L131 updated). |
| m3 | Minor | ACCEPTED-FIXED | design.md caveat 3 "catches" → "warns on" applied (matches `test_branch_workflow_audit_warns_on_stale_slice_branch_from_prior_conflict` test name). |
| m4 | Minor | ACCEPTED-FIXED | Covered by B1-residual sweep (ADR-019 frontmatter title at L3 updated). |

