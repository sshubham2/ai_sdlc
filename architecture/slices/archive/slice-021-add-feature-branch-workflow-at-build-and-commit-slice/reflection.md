# Reflection: Slice 021 add-feature-branch-workflow-at-build-and-commit-slice

**Date**: 2026-05-14
**Shipped**: YES-WITH-DEFERRALS (5 DEVIATIONs logged; DEVIATION-5 surfaces a slice-022 candidate that supersedes part of ADR-019 Option 1)

## Validated

- **BRANCH-1 audit-from-day-one approach is right** — design.md L51 Option 2 rejection ("audit cheaper than prose-pin test mass") empirically held; the audit caught zero false positives across 8 unit tests + real-environment positive case + escape-hatch acceptance.
- **3-sub-mode discipline structure** (build-time + commit-time + audit-time) works as canonical reference shape; mirrors slice-020 BFRD-1 and slice-017 TPHD-1 sub-mode N-sub-mode precedent N=7 → **N=8 stable** post-slice-021.
- **Default-branch resolution via `git symbolic-ref refs/remotes/origin/HEAD` + `init.defaultBranch` fallback** — empirically robust across 3 test scenarios (origin-HEAD path; init.defaultBranch fallback path; neither-resolves STOP path). Canonical phrase pinned across N=3 surfaces (audit + 2 SKILL.md).
- **Canonical `BRANCH=skip — rationale: <text>` line shape with regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`** — empirically matches the slice's own bootstrap DEVIATION line on first try (no fixture iteration needed).
- **Bootstrap-reference instance pattern** — slice-021 successfully exercised the discipline at /build-slice Step 1 plan-mode entry via manual branch-create + canonical DEVIATION line; precedent set for any future codification slice authoring runtime-discipline prose.
- **Mini-CAD-1 byte-equality pattern extends cleanly to 2 new skill surfaces** (build-slice + commit-slice); N=11 → **N=13 stable** post-slice-021. Pattern is structurally portable.
- **6 ACCEPTED-FIXED inline applied at /critique TRI-1 (vs all-PENDING)** — slice-020 precedent confirmed efficient; reduces /build-slice PENDING-queue work.
- **Empirical-verification-at-design-time discipline** N=19 → **N=20 stable** — 6 audits VALIDATED at /build-slice + /validate-slice (PMI-1 + INST-1 + CAD-1 + BRANCH-1 + TF-1 + WIRE-1 all clean).
- **VAL-1 Layer A (Credential scan)** — 0 secrets across 22 changed files (continuing N=19+ stable streak).

## Corrected

- **shippability self-test convention** (DEVIATION-1) — design.md L201-220 envisioned a separate `tests/shippability/test_row_021_branch_workflow.py` file; reality: slice-020 row 20 + all earlier rows demonstrate that shippability catalog rows ARE the test (the Command cell is executable directly). No separate per-row test file convention exists. **Updated**: TF-1 plan row pointed at `architecture/shippability.md` row 21 itself (grep-verification test type per slice-018 DEVIATION-2 non-pytest precedent).
- **tests/tools/ namespace collision** (DEVIATION-2) — design.md L116 + L131 placed audit unit tests at `tests/tools/`; reality: namespace collision with top-level `tools/` Python package breaks `from tools import branch_workflow_audit`. **Updated**: relocated to `tests/methodology/test_branch_workflow_audit.py` (where ALL existing audit tests live — test_install_audit, test_plugin_manifest_audit, test_critique_agent_drift). The design.md Wiring matrix's `tests/tools/__init__.py` row is now obsolete (see Vault updates below).
- **Windows cp1252 default encoding on `write_text`** (DEVIATION-3) — `pathlib.Path.write_text("... — ...")` without explicit `encoding="utf-8"` wrote em-dash as cp1252 byte 0x97, breaking the audit's UTF-8 read. **Updated**: `encoding="utf-8"` added inline at the test fixture write call. Class N=4 → **N=5 cumulative recurrence** (slices 007 + 016 + 018 + 020 + 021) — past N≥3 promotion threshold; `audit-tools-default-utf8-stdout` slice candidate ELEVATED to highest-priority for slice-022 (was first proposed at slice-018 reflection's "Strongest slice-019 candidates").
- **Global `init.defaultBranch=master` leaks past local `--unset`** (DEVIATION-4) — the `default-branch-unresolvable` test required isolating git config via `GIT_CONFIG_GLOBAL` + `GIT_CONFIG_NOSYSTEM` env overrides. **Updated**: `monkeypatch.setenv` applied inline; documented in test docstring.
- **`/commit-slice --merge` is structurally wrong for non-solo projects** (DEVIATION-5; user-surfaced post-/build-slice) — local-merge + `git push origin master` either (a) fails on protected branches, (b) bypasses required-PR review, or (c) skips CI evaluation on slice branch in isolation. ALL 4 Critic-stack passes missed this; the dimensions (Security / Contract gaps / Cross-cutting conformance) evaluated `--merge` AS LOCAL-ONLY without questioning whether local-only was the right scope. **Updated**: design.md Limitations item 1 elevated from "future-slice concern" to "STRUCTURALLY WRONG for non-solo projects"; build-log.md DEVIATION-5 logs the realization; **slice-022 candidate `redesign-commit-slice-for-pr-aware-flow` queued** (DROP `--merge` sub-mode (b) entirely; replace with `--push` flag — push slice branch to origin, user creates PR + merges manually via UI). ADR-020 (slice-022) will SUPERSEDE ADR-019 Option 1's sub-mode (b) decision; sub-modes (a) build-time branch-create + (c) audit-time pre-finish refusal stay unchanged.
- **`methodology-changelog.md` location** — design.md L17 + L41 + L80 + L116 referenced `architecture/methodology-changelog.md`; reality: the file lives at repo root `methodology-changelog.md` (matches slice-020 + all earlier convention). The test path (`tests/methodology/test_methodology_changelog.py` uses `read_file("methodology-changelog.md")`) already had the right path. **Updated**: cleanup-class only; design.md prose references to `architecture/methodology-changelog.md` should be corrected at slice-022+ cleanup (not blocking; the actual edits landed at the correct path).

## Discovered

- **NEW class candidate for /critic-calibrate slice-022: `opinionated-merge-default-vs-team-workflow`** (DEVIATION-5 root cause). All 4 Critic-stack passes (first /critique + /critique-review + /critique rerun + /critique-review rerun) missed that `--merge`'s local-only semantics was the wrong default scope, not just an implementation detail. The Critic dimensions evaluated `--merge` *internally* (does the flow work as designed?) without asking *externally* (is this design right for the dominant real-world case?). **N=1 watch-list; promote at N≥3 distinct-slice recurrence**. The fix at /critic-calibrate slice-022: add a Dim 9 sub-clause about *default-mode-vs-typical-team-workflow alignment* — every new flag/discipline should be evaluated against the project's expected adopter profile, not just the codification slice's own constraints.
- **Auto-mode classifier as fifth-Critic-stack-layer (N=2 → N=3 cumulative)** — at /validate-slice AC #4 negative-case attempt, the classifier blocked `git stash + checkout master` mid-slice (correctly — not user-authorized). Class precedent: slice-018 DEVIATION-1 (mini-CAD-1-ceremonial-transition-cleanup-slice-applicability — classifier blocked agents/critique.md modification at /build-slice) + slice-018 DEVIATION-2 (cleanup-slice TF-1 row enumeration — TF-1 audit `--strict-pre-finish` caught at /build-slice Phase 6). Slice-021 adds: classifier blocked stash+checkout at /validate-slice. **N=3 cumulative recurrence — well past N=3 promotion threshold**. The pattern: auto-mode classifier + TF-1 audit + WIRE-1 audit + PMI-1 audit + INST-1 audit + CAD-1 audit + BRANCH-1 audit collectively function as a 6+-layer execution-time Critic stack that catches what /critique + /critique-review + TRI-1 review-time stack misses. Worth surfacing at /critic-calibrate slice-022 as an explicit observation.
- **VAL-1 Layer B intra-repo `tests` namespace-package class N=18 → N=19 cumulative recurrence** (every slice 003-021). Handled cleanly via documented `--imports-allowlist tests` workaround at /validate-slice Step 5b. Promotion candidate: default-on behavior in `tools/validate_slice_layers.py` (auto-allowlist `tests` when it's an in-repo package). Defer to a focused slice — touches the audit tool's defaults.
- **Wiegers regression-guard coverage-symmetry watch-list ratchets to N=9 cumulative within slice-021 alone** — 4 NEW instances within the slice (first-Critic M4 + meta-Critic M-add-1 + /critique-rerun B3-new violations 1+2 + /critique-review-rerun M-add-1-rerun + M-add-3-rerun). The Wiegers count-symmetry class is empirically the dominant recurrence class for codification slices. **Promotion to Dim 9 sub-clause at /critic-calibrate ELEVATED to slice-022** (from slice-024+).
- **DR-1 catch-class diversification N=8 → N=10 cumulative** with 2 NEW class candidates at N=1 each from slice-021:
  - `Cross-slice-branch leakage at upstream skill pipeline` (/critique-review M-add-4 ESCALATED → slice-021 ADR-019 option (a) carveout; pipeline-wide enforcement queued for `add-pipeline-wide-branch-discipline-to-upstream-slice-skills` follow-on slice)
  - `Milestone-summary surface as load-bearing claims-propagation target` (/critique-review-rerun M-add-1-rerun + M-add-2-rerun — both fixes failed to propagate to milestone.md L43 + L46 in the rerun's own fix-block; pattern is the rerun-Critic scoped grep to mission-brief + design + ADR but not to milestone.md)
  - Both **promote at N≥3 distinct-slice recurrence** if observed in slice-022+ slices.
- **Recursive-self-application N=17 → N=28 cumulative HWM** (slice-021 lifecycle: 14 first-Critic + 4 /critique-review missed + 11 /critique-rerun + 4 /critique-review-rerun missed = 33 total findings on own draft — new project HWM exceeding slice-020 N=17). Codification slices empirically commit instances of the disciplines they codify at progressively higher density as slice complexity grows. **Slice-022 should budget for N=15+ Critic-stack findings on its own draft as the new baseline expectation** (was N=15+ at slice-020; now N=25+ at slice-021).
- **The "design-time fix-block-completeness self-check" Builder-self-check pattern is provably falsifiable** (per slice-021 /critique-rerun M1-residual + /critique-review-rerun's 4 missed findings within the rerun's own fix-block). The honest closure is **adversarial Critic check via Dim 9 sub-clause**, not Builder-self-check. This is a methodological insight: any aspirational pre-finish-gate item that lacks a mechanical tool to enforce it will be falsified by the same Builder authoring it. Future slices should not propose Builder-self-checks for any class that demonstrates recursive recurrence; the structural solution is /critic-calibrate codification.
- **Slice-skill prerequisite-class disciplines should be sub-sections of `## Prerequisite check`, NOT new Steps** (slice-017 TPHD-1 sub-mode (c) precedent + slice-021 BRANCH-1 sub-mode (a) ACCEPTED-FIXED at /critique B3 + /critique-rerun B1-residual sweep). The Step-numbering convention is fixed at 1,2,3,4,5,6,7,7b,7c,8 per methodology-changelog v0.32.0 L102; adding Step 0 / Step 0.5 / Phase N / Phase 0 is a recurring B3-class vocabulary violation. **Slice-022 candidate**: codify this as a Dim 9 sub-clause at /critic-calibrate slice-022 alongside the Wiegers coverage-symmetry promotion.

## Deferred

- **Slice-022 candidate (HIGHEST PRIORITY): `redesign-commit-slice-for-pr-aware-flow`** — DEVIATION-5 fix. DROP `--merge` sub-command entirely; replace with `--push` flag that pushes slice branch to origin (user creates PR + merges manually via UI). ADR-020 will SUPERSEDE ADR-019 Option 1's sub-mode (b). The slice will:
  - Remove `--merge` flag + 5-step merge flow + 2 pre-flight guardrails from `skills/commit-slice/SKILL.md`
  - Add `--push` flag with single guardrail (`git status --porcelain` empty before push) + `git push -u origin slice/NNN-<name>` + display PR-creation URL hint (`gh pr create` or browser link)
  - Keep BRANCH-1 sub-mode (a) build-time branch-create + sub-mode (c) audit-time pre-finish refusal UNCHANGED
  - Update methodology-changelog with v0.36.0 entry naming `--push` as the new sub-mode (b)
  - Document conflict-recovery flow gap deferral CONTINUES (no recovery flow until needed)
- **Slice-022 candidate (HIGH PRIORITY): `audit-tools-default-utf8-stdout`** — cp1252 N=5 cumulative promotion threshold MET. Patch `tools/critique_review_audit.py` + `tools/validate_slice_layers.py` + `tools/branch_workflow_audit.py` + any other audit tool with console output to default `sys.stdout.reconfigure(encoding="utf-8")` at module load. Saves the `$env:PYTHONIOENCODING = "utf-8"` workaround at every PowerShell invocation. SMALL ~30-45 min.
- **Slice-022 candidate (HIGH PRIORITY): `/critic-calibrate slice-022 codification`** — explicit codification of:
  - Wiegers regression-guard coverage-symmetry as Dim 9 sub-clause (N=9 cumulative, well past N=3 threshold)
  - `Cross-slice-branch leakage at upstream skill pipeline` watch-list (N=1, await N=3)
  - `Milestone-summary surface as load-bearing claims-propagation target` watch-list (N=1, await N=3)
  - `opinionated-merge-default-vs-team-workflow` watch-list (N=1, await N=3)
  - Auto-mode-classifier-as-Critic-stack-layer observation (N=3, promote)
  - Builder-self-check-aspirational-pattern observation (N=1, promote at slice-021 codification — this slice produced the empirical demonstration)
- **Future slice candidate: `add-pipeline-wide-branch-discipline-to-upstream-slice-skills`** — extends BRANCH-1 to `/slice` + `/design-slice` + `/critique` + `/critique-review` per M-add-4 ESCALATED carveout. Magnitude: ~35+ sites (8 SKILL.md surfaces × in-repo + installed = 16 + prose-pin tests + mini-CAD drift). LARGE; may split into 2 sub-slices.
- **Future slice candidate: `add-merge-conflict-recovery-to-commit-slice-merge`** — per /critique B5 ACCEPTED-PENDING option (c) deferral. Becomes MOOT if slice-022 drops `--merge` entirely (the new `--push` flow has no merge-conflict surface).
- **Backlog: `add-branch-name-validation-to-slice-skill`** — m1 from first /critique DEFERRED. 20-slice empirical record shows zero `git check-ref-format` violations; promote at N≥1 actual violation.
- **Cleanup: `architecture/methodology-changelog.md` path references** — design.md L17/L41/L80/L116 reference wrong path. Non-blocking; sweep at slice-022 alongside other cleanup.
- **Design-time guard against fix-block-completeness recursion** (per /critique-rerun M1-residual ACCEPTED-FIXED option (a)) — RETIRED as aspirational; structural closure is /critic-calibrate slice-022 codification of Wiegers coverage-symmetry as adversarial Dim 9 sub-clause. NO Builder-self-check candidate.
- **VAL-1 Layer B `tests` auto-allowlist** — N=19 cumulative pattern; promote `--imports-allowlist tests` to default-on behavior. SMALL ~15 min; consider bundling into the `audit-tools-default-utf8-stdout` slice.

## Critic calibration

This slice ran the Critic stack **4 times** (first /critique + /critique-review + /critique rerun + /critique-review rerun). Score per disposition + reality:

### First /critique (14 findings)

- **B1** (escape-hatch regex contradicts empirical DEVIATION format): VALIDATED — disposition ACCEPTED-PENDING; canonical shape codified at /build-slice Step 7c; audit's regex empirically matches the slice's own bootstrap DEVIATION line on first try.
- **B2** ("zero external consumers" false — 3 stale-doc surfaces): VALIDATED — disposition ACCEPTED-PENDING; 3 surfaces swept at /build-slice; grep returns 0 `--do-commit` hits post-fix.
- **B3** (Step 0.5/Phase 6 vocabulary contradicts heading scheme): VALIDATED — disposition ACCEPTED-PENDING; full 22-site vocabulary sweep at /critique rerun (which itself caught the residual instances missed in /design-slice rerun).
- **B4** (mid-slice smoke gate references non-existent branch — bootstrap caveat hand-waved): VALIDATED — disposition ACCEPTED-PENDING; literal bootstrap DEVIATION line text pinned + TF-1 row added + slice-021's own bootstrap empirically validated the canonical shape.
- **B5** (`--merge` post-/reflect-archive merge-conflict recovery state undefined): VALIDATED — disposition ACCEPTED-PENDING option (c); pre-flight stale-`slice/*`-branch guardrail codified + Limitations item 10 documents deferral. **Becomes MOOT at slice-022 if `--merge` is dropped.**
- **M1** (master/main hard-coded): VALIDATED — disposition ACCEPTED-PENDING; `_resolve_default_branch()` helper + symbolic-ref + init.defaultBranch fallback + 3 unit tests all PASS.
- **M2** (TF-1 row count inconsistent with AC #5 — CAD-1 + INST-1 missing rows): VALIDATED — disposition ACCEPTED-FIXED inline; rows added; both tests PASS.
- **M3** (shippability row-21 Command cell omits BRANCH-1 critical-path tests): VALIDATED — disposition ACCEPTED-FIXED inline; expanded to 14 invocation targets; full row 21 runs clean at /validate-slice Step 5.5.
- **M4** (ADR-019 magnitude estimate 4 inconsistent counts): VALIDATED — disposition ACCEPTED-FIXED inline; harmonized to single canonical count (~22 pre-B2 / ~25 post-B2 in initial fix, later harmonized to 30 total touches per /critique-rerun M4-new option (b)).
- **M5** (Authorization model claim "none" understates local WT-loss risk): VALIDATED — disposition ACCEPTED-PENDING; 2 must-not-defer guardrails (hard `git status --porcelain` empty-check + explicit `Confirm merge + delete? (yes/no)` prompt) codified in `--merge` flow.
- **m1** (`/slice` produces names with no `git check-ref-format` guard): NOT-YET — disposition DEFERRED; 20-slice empirical record shows zero violations; will re-score at the first problematic-name slice (currently N=0).
- **m2** ("slice-022" speculation): VALIDATED — disposition ACCEPTED-FIXED inline; softened to "next non-/repro slice" across 5 sites.
- **m3** (`grep -F` substring vs canonical-phrase test function): VALIDATED — disposition ACCEPTED-FIXED inline; verification plan #4 named test functions.
- **m4** (smoke gate circular dependency on slice branch existing): VALIDATED — disposition ACCEPTED-FIXED inline; smoke gate prose updated to express intent + STOP/bootstrap path.

### First /critique-review (4 missed findings)

- **M-add-1** (count-drift WITHIN M3 ACCEPTED-FIXED block — 14 vs ~11): VALIDATED — disposition ACCEPTED-PENDING; harmonized at /critique rerun to canonical 14 invocation targets (8 whole-file + 6 `::test_*`).
- **M-add-2** (TPHD-1 sub-mode (a) violation in M3 + m3 fix blocks): VALIDATED — disposition ACCEPTED-PENDING; harmonized test function names across TF-1 plan + verification plan + Command cell at /critique rerun.
- **M-add-3** ("Phase 0" survival at mission-brief L65): VALIDATED — disposition ACCEPTED-PENDING; swept in /critique rerun's B1-residual 22-site sweep.
- **M-add-4** (cross-slice-branch leakage upstream-pipeline scope): VALIDATED — disposition ESCALATED → /design-slice redesign → option (a) /build-slice-only carveout chosen; Limitations item 8 + Error-model surface 4 document the carveout; future slice `add-pipeline-wide-branch-discipline-to-upstream-slice-skills` queued.

### /critique rerun (11 findings)

- **B1-residual** (22-site vocabulary sweep INCOMPLETE incl. ADR title): VALIDATED — disposition ACCEPTED-FIXED inline at /critique rerun; grep verified zero residual non-meta-reference instances.
- **B2-residual** ("zero external consumers" retraction not propagated to 4 sites): VALIDATED — disposition ACCEPTED-FIXED inline; 4 sites swept; grep returns 0 matches.
- **B3-new** (2 NEW Wiegers count-drifts WITHIN /design-slice rerun fix-block — "7+7=14" vs 8+6; "28 TF-1 rows" vs 30): VALIDATED — disposition ACCEPTED-FIXED inline; canonical counts harmonized at 5 surfaces.
- **M1-residual** (aspirational Pre-finish item 11 falsified at the rerun authoring it): VALIDATED — disposition ACCEPTED-FIXED option (a); item 11 RETIRED + watch-list ELEVATED to /critic-calibrate slice-022 (Wiegers N=9 cumulative).
- **M2-new** (helper-extraction asymmetry — default-branch resolution at N=3 sites without explicit marking): VALIDATED — disposition ACCEPTED-FIXED inline; Must-not-defer canonical-phrase pin added across N=3 surfaces.
- **M3-new** (must-not-defer count drift — "18" vs 19 actual): VALIDATED — disposition ACCEPTED-FIXED inline; count harmonized to 20 (19 + 1 from M2-new addition).
- **M4-new** (ADR-019 magnitude enumeration items 1-22 vs design.md 30 items): VALIDATED — disposition ACCEPTED-FIXED option (b); ADR-019 magnitude replaced with cross-reference to design.md §Files changed (eliminates dual-enumeration drift class permanently).
- **m1** (typo `_devation` vs `_deviation`): VALIDATED — disposition ACCEPTED-FIXED inline; replace_all.
- **m2** (Wiring matrix consumer-entry-point cell carries retired vocabulary — covered by B1-residual): VALIDATED — covered.
- **m3** (BRANCH-1 audit "catches" stale branches; actually "warns on"): VALIDATED — disposition ACCEPTED-FIXED inline; caveat 3 softened.
- **m4** (ADR-019 frontmatter title carries retired vocabulary — covered by B1-residual): VALIDATED — covered.

### /critique-review rerun (4 missed findings)

- **M-add-1-rerun** (B3-new fix did NOT propagate to milestone.md L43): VALIDATED — disposition ACCEPTED-FIXED inline; milestone.md L43 swept.
- **M-add-2-rerun** (M1-residual fix did NOT propagate to milestone.md L46): VALIDATED — disposition ACCEPTED-FIXED inline; milestone.md L46 replaced with retirement note.
- **M-add-3-rerun** (N-ratchet drift between ADR-019 L158 and design.md L197/L209/L211): VALIDATED — disposition ACCEPTED-FIXED inline; 3-site Cumulative-Critic-influence section harmonized.
- **M-add-4-rerun** (TPHD-1 N=4→N=5 stable claim falsified by M-add-1/2/3-rerun): VALIDATED — disposition ACCEPTED-FIXED inline; softened to "N=5 partial" + honest accounting.

### Aggregate Critic-disposition accuracy

**33 findings across 4 review passes; 100% Critic-disposition accuracy** (extends slice-019/020 N=14 consecutive 100% slice streak to **N=15 consecutive 100%**). Running totals: **127/127 first-Critic + 144/144 cross-Critic-stack across slices 6-21**.

**Missed by Critic (post-/validate-slice user-surfaced)**:

- **`opinionated-merge-default-vs-team-workflow`** (DEVIATION-5) — ALL 4 Critic-stack passes missed that `--merge`'s local-only semantics was structurally wrong for the dominant real-world case (protected branches + required-PR review + CI gating). The Critic dimensions evaluated `--merge` *internally* without questioning *external* fit-for-typical-team-workflow. **NEW class candidate for /critic-calibrate slice-022 (N=1 watch-list; promote at N≥3 distinct-slice recurrence)**. This is the strongest miss-class catch of the project to date — the user-surfaced post-validate gap that 4 review passes couldn't catch indicates a structural Critic-stack blind spot, not just an individual-finding miss.

### Pattern observations for /critic-calibrate slice-022

1. **Codification slices commit instances of their own discipline on own draft at progressively higher density as slice complexity grows**: slice-013 N=7 → slice-019 N=12 → slice-020 N=17 → **slice-021 N=33 (project HWM)**. Slice-022 should budget for N=20+ Critic-stack findings as new baseline.
2. **Builder-self-checks are provably falsifiable**: slice-021's "design-time fix-block-completeness self-check" Pre-finish-gate item was empirically falsified at the rerun authoring it (5 fresh count-drifts committed in the same round). Future slices should NOT propose Builder-self-checks for any class showing recursive recurrence; the structural solution is /critic-calibrate codification as adversarial Dim 9 sub-clause.
3. **Critic-stack scopes its grep to mission-brief + design + ADR but consistently misses milestone.md**: /critique-review-rerun M-add-1-rerun + M-add-2-rerun both targeted milestone.md propagation gaps. NEW DR-1 class candidate `Milestone-summary surface as load-bearing claims-propagation target` (N=1 watch-list; promote at N≥3).
4. **The Critic stack evaluates new disciplines INTERNALLY but not EXTERNALLY against typical adopter profile**: DEVIATION-5 escaped because all 4 passes treated `--merge` as a contract problem (does the flow work as designed?) without asking the adopter-profile question (is local-merge the right default for the dominant team-workflow shape?). This is a NEW dimension worth codifying at /critic-calibrate slice-022.

## Lessons for next slice

- **Run `grep -nE` after EVERY claimed "swept" / "harmonized" / "retracted" / "propagated" before declaring closure** (codified into /critique-rerun discipline; demonstrated 4× across slice-021 review passes). The discipline alone doesn't prevent recursion — the Critic-stack does, via Dim 9 sub-clause adversarial check.
- **Codification slices that ship a new audit tool benefit from the audit-from-day-one approach** (BRANCH-1 + slice-014 PMI-1 v1.1 precedent); prose-only disciplines with deferred audit (BFRD-1, TPHD-1, etc.) require a v2 audit slice at N≥3 recurrence. For programmatic-checkable disciplines, audit-from-day-one is structurally cheaper.
- **Methodology-research codebases should ship ANY new flag/discipline with both internal (Critic-time) and external (adopter-profile) evaluation**. DEVIATION-5's discovery teaches: "is this discipline right for the typical adopter, not just for this codebase's solo workflow" is a meta-Critic question worth codifying.
- **The bootstrap-reference-instance pattern is portable**: any codification slice authoring runtime-discipline prose can use the canonical `<discipline>=skip-bootstrap` DEVIATION line shape to document its own pre-existence gap. Slice-021 establishes the precedent.
- **Slice-skill prerequisite-class disciplines belong in `## Prerequisite check` sub-sections, NOT new Steps** — strong rule. Worth codifying as Dim 9 sub-clause at /critic-calibrate slice-022 alongside Wiegers coverage-symmetry promotion.

## Vault updates made (thin vault — slice-021 final state)

- `methodology-changelog.md` (repo root) — v0.35.0 entry prepended (BRANCH-1 + 3 sub-modes + 8 surface schema-pin ratchet + v1 carveout + PMI-1 retirement-proof N=7).
- `architecture/decisions/ADR-019-branch-per-slice-workflow.md` — NEW ADR; Option 1 CHOSEN with M-add-4 option (a) carveout; reversibility: cheap; ~25 source files + 5 test-file extends.
- `architecture/shippability.md` — row 21 appended (14 invocation targets enumerated).
- `architecture/slices/_index.md` — auto-updated at archive step below.
- `architecture/slices/archive/_index.md` — auto-updated at archive step below.
- `CLAUDE.md` (root project) — NEW `Branch-per-slice` bullet in Brownfield rules.
- 3 stale-doc surfaces updated: `pipeline.md` L97, `tutorial.md` L750, `tutorial-site/Hybrid AI SDLC Pipeline.html` L583 (all `--do-commit` → `--merge` per slice-021 ship state; slice-022 will revise to `--push` post-DEVIATION-5 redesign).
- `architecture/lessons-learned.md` — appended at Step 5 below.
- `architecture/risk-register.md` — NO new entries (R-1, R-2, R-3 unchanged; DEVIATION-5 captured as slice-022 candidate, not a register entry, since the issue has a clear remediation path).

**NOT updated** (per thin-vault discipline):
- `architecture/components/` — doesn't exist; code is truth.
- `architecture/contracts/` — doesn't exist; code (Python type hints, CLI argparse) is the contract.
- `architecture/schemas/` — doesn't exist; data models in code.

## Recursive-self-application empirical record

Slice-021 lifecycle produced **33 findings on own draft across 4 review passes**:
- First /critique: 14 (5 Blockers + 5 Majors + 4 Minors)
- First /critique-review: 4 missed (1 Blocker + 3 Majors)
- /critique rerun: 11 (3 Blockers + 4 Majors + 4 Minors)
- /critique-review rerun: 4 missed (3 Majors + 1 Minor)

**Recursive-self-application cumulative ratchets to N=28 → N=33 HWM** (new project record; was N=17 at slice-020).

The empirical conclusion: **codification slices that codify a discipline almost always commit instances of that discipline on their own draft, at densities scaling with slice complexity**. The structural mitigation is /critic-calibrate codification as adversarial Dim 9 sub-clauses, NOT Builder-self-checks (which are provably falsifiable per slice-021's M1-residual demonstration).
