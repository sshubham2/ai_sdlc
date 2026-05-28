# Reflection: Slice 074 codify-cp-r-in-branch-2-skill (expanded)

**Date**: 2026-05-28
**Shipped**: YES-WITH-DEFERRALS (6 code-Critic advisory findings DEFERRED to slice-075+ `bundle-074-code-critic-cleanup` per voluntary-restraint N=15 cumulative)

## Validated

- **R-20 cp-r tax codified at point 1 + retired structurally** — `skills/build-slice/SKILL.md` `### Branch state` point 1 bash codefence now contains the `if [ -d "$repo_root/<dir>" ]; then cp -r "$repo_root/<dir>" ./; fi` set-e-safe guard for both `diagnose-out/` + `graphify-out/`. R-20 flipped `mitigating` → `retired`. 3 structural-pin tests at `tests/methodology/test_build_slice_skill_cp_r_step.py` + 1 audit-runtime test at `tests/methodology/test_r_20_retired.py` all PASS. Validated by per-AC verification at /validate-slice + 73/73 shippability runner.
- **Switch-commit-switch codification at point 4 ships the canonical 4-step recipe inside a bash codefence** — replaces the pre-slice "STOP, ask user to commit or stash" prose with the empirically-stable N=5 cumulative pattern (slice-070/071/072/073/074). 3 structural-pin tests at `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` (order-tokens-in-codefence + both-worktree-create-forms-documented + no-`git stash` discipline pin) all PASS.
- **OSDG-1 forward-sync verified** — installed `~/.claude/skills/build-slice/SKILL.md` content-equal modulo line endings to in-repo copy post-cp; `test_build_slice_skill_drift.py` GREEN.
- **MEPD-1 EXCLUDE stance held** — no methodology-changelog v.73.0 entry, no PMI-1 atomic bump (ships at v0.72.0 unchanged), no shippability row #74 per design.md L96 carve-out. Both /critique passes ratified this decision at CLEAN.
- **Three-Critic stack value-validation extends to N=10 cumulative** (slice-063 → slice-074 inclusive) — pass-1 design-Critic surfaced 4M/4m + pass-1 meta-Critic ADJUST (1 sev-adj + 2 missed Minor) + pass-2 design-Critic 1B/2M/2m + pass-2 meta-Critic ACCEPT (0 sus/0 missed/0 sev-adj) + code-Critic 1M/5m. Each Critic surfaced distinct, complementary defect classes the others could not reach. Pass-2 meta-Critic ACCEPT is the cleanest possible outcome — pass-2 first-Critic calibration on the expansion delta was exemplary (APED-1-grounded across 3 of 5 findings with empirical falsification evidence).
- **Bootstrap exception per CRP-1/ADR-024 slice-026 mirror** held — slice-074's own /build-slice Phase A prereq executed the cp -r MANUALLY (R-20 N=9 cumulative), not the codified prose; the installed SKILL.md was still pre-slice during prereq check. Per /critique pass-1 M1 ACCEPTED-FIXED: the canonical N+1 first-governed-slice demonstration is slice-075's Phase A, not slice-074's.

## Corrected

- **None for code/vault.** All design-time corrections (10 first-Critic pass-1 + 2 missed meta-Critic pass-1 + 5 first-Critic pass-2 = 17 total dispositions) landed in-band during /critique + /critique-review BEFORE /build-slice execution. Post-build reality confirmed design verbatim — 6/6 ACs PASS, 73/73 shippability runner, no surprises.
- **Slice-074 design.md L96 claim about MEPD-1 EXCLUDE precluding shippability row was self-justifying and may be empirically wrong** — slice-068's reflection (the cited precedent) actually says "shippability row #67 added in /reflect Step 5.3 (M2 partial-discharge — paired-pin tests deferred to slice-070+ bundle)". So slice-068 EXCLUDE did NOT preclude a shippability row; it precluded the BC-PROJ-10 paired-pin obligation. Slice-074 inherits this "no row" stance from its CLEAN-ratified design, but a future /critic-calibrate proposal target is "MEPD-1 EXCLUDE vs shippability row obligation should be disentangled — they're separate axes." Logged as a /critic-calibrate signal for slice-075+. Not a vault correction this slice; flagging for future calibration only.

## Discovered

- **First scope-expansion at /build-slice plan-mode in slice history** (N=1 cumulative). User-approved at PCA-1 plan-mode gate (option 2: "Approve, but ALSO codify switch-commit-switch-worktree"). Methodology-strict path chosen — re-run /critique + /critique-review on the AC#5+AC#6 expansion delta only; original AC#1-AC#4 clearance preserved. Pass-2 dispositions ratified at TRI-1-EXT (5 ACCEPTED-FIXED in-band) before /build-slice execution resumed. New methodology pattern: **"scope-expansion-at-plan-mode + re-Critic-the-delta + TRI-1-EXT"** — slice-022 codify-empirical-pattern axis would say wait for N≥3 before promoting to methodology rule. Watch-list candidate.

- **Code-Critic M1 (point 4 variable-scope)**: REAL semantic defect. Point 4's codefence references `$wt_base`/`$repo_root`/`$default` defined only in point 1's codefence (mutually-exclusive branches). A Builder hitting the dirty-tree branch on a fresh shell hits unbound variables: `git worktree add  slice/NNN-<slice-name>` → `fatal: missing path`, OR cp -r `/diagnose-out` (root-anchored). DEFERRED to slice-075+ bundle per voluntary-restraint (N=15 cumulative). **Slice-075 is the empirical N+1 first-governed-slice for BOTH R-20 candidate (a) AND the switch-commit-switch codification** — if slice-075 ships dirty-on-default and exercises the codified point-4 recipe, M1's defect will surface loud-and-clear (the canonical slice-040 N+1 first-governed-slice catch surface).

- **TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions pattern HELD at N=7 cumulative** (no new instance this slice). Pass-1 meta-Critic m-add-1 (single-line if/then/fi constraint not recorded) and m-add-2 (Phase A/B/C glossary missing) were both pure missed-coverage findings, NOT regressions introduced by Builder fix-block sweeps. Pass-2 meta-Critic ACCEPT found 0 missed findings. **The pattern's recurrence rate slows when the Builder fix-block discipline is tight** (slice-074 evidence: ~10 design-time fixes applied with 0 regressions caught at meta-Critic layer). /critic-calibrate slice-075+ proposal target stays at N=7 from slice-073 — still genuinely overdue, just not extended this slice.

- **Voluntary-restraint discipline extends to N=15 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074) — code-Critic v1 advisory findings consistently route to next-slice bundled cleanup; structurally stable across 9 consecutive cycles. Next bundled-cleanup-at-N+1 opportunity is slice-075+ `slice-NNN-bundle-074-code-critic-cleanup` (6 findings: M1 variable-scope + m1 placeholder + m2 duplication + m3 regex docstring + m4 helper extraction + m5 subprocess error surface; bounded ~1-2 hours estimate).

- **BC-1 BC-GLOBAL-2 prose-vs-automation false-positive class extends to N=6 cumulative** (slice-069/070/071/072/073/074). The BC-GLOBAL-2 keyword-trigger fires on slice-074's prose mentioning `git stash` (NO-auto-stash discipline declaration; documentation context), NOT on git-mutate-then-revert automation. **`/critic-calibrate` slice-075+ proposal target SEVERELY OVERDUE at N=6** — pattern is well past the N=3 promotion threshold; BC-1 negative-anchor refinement candidate: negative anchors for `NO-auto-stash discipline`, `prose discussion`, `recovery hint`, `documented recovery path`.

- **AC count > 5 N=3 promotion of slice-067/072 pattern** — slice-074 has 6 ACs (slice-072 reflection L97 carve-out applied: AC#6 is exclusively an additional structural-pin meta-AC for the two worktree-create forms distinction). Three consecutive slices now demonstrate the carve-out genuinely needs 6 ACs for new-mechanism mints + paired-pin meta-ACs. **/critic-calibrate slice-075+ proposal target ready for action**: formalize "≤5 (or ≤6 when AC6+ are exclusively additional structural-pin meta-ACs)" in `/slice` SKILL.md.

- **Switch-commit-switch codification's pass-2 m2 N=1 (no-stash discipline structurally pinned)** — first instance of a discipline declared in out-of-scope being promoted to a structural test in the SAME slice. Slice-022 codify-empirical-discipline axis: declare-in-prose-then-pin-structurally is the canonical pattern; AC#1's M3 ACCEPTED-FIXED guard-prefix anchor is the sibling precedent. Watch-list candidate at N=1.

- **MEPD-1 EXCLUDE precedent for "codification of empirical pattern"** strengthens — slice-074 is the cleanest example yet (operationalizes R-20 candidate (a) + codifies N=5 switch-commit-switch empirical pattern; no methodology rule minted, no PMI-1 bump). Precedent shape: **codification-of-empirical-pattern → MEPD-1 EXCLUDE; rule-mint → MEPD-1 INCLUDE**.

- **R-20 cp-r tax cumulative count frozen at N=9** (slice-067 N=3 → slice-074 N=9). R-20 is RETIRED; the count stops accumulating at slice-074. Slice-075+ first slice that reads the codified prose at Phase A is the structural reset point.

- **3-Critic stack value-validation extends to N=10 cumulative** (slice-063 → slice-074). Each Critic surfaced distinct + complementary defect classes structurally unreachable by the others. Code-Critic M1 (variable-scope at point 4) is canonically a structural-prose-contract defect the design-Critic stack cannot reach (only post-code-completion empirical execution surfaces the variable-binding gap). Do NOT collapse the 3-Critic stack.

- **Switch-commit-switch pattern frozen at N=5 cumulative** (slice-070/071/072/073/074). The pattern's recurrence count stops accumulating at slice-074 because the codification at point 4 retires the pattern's pre-codification visibility. Slice-075+ that uses the codified recipe is the structural reset point.

## Deferred

- **All 6 code-Critic findings** (M1 variable-scope + m1 `<scaffolding files>` placeholder + m2 cp-r duplication + m3 regex docstring + m4 helper extraction + m5 subprocess error surface) → slice-075+ `slice-NNN-bundle-074-code-critic-cleanup` per voluntary-restraint discipline N=15 cumulative + CRSI-1 v1 walking-skeleton advisory-only.
- **`/critic-calibrate` proposal target** → slice-075+ run with FIVE accumulated signals now overdue:
  1. TPHD-1 sub-mode (a) N=7 cumulative (slice-073 nominee; held at N=7 this slice)
  2. BC-1 BC-GLOBAL-2 prose-vs-automation N=6 cumulative (slice-073 N=5 + slice-074 +1)
  3. AC-count > 5 N=3 promotion (slice-067 + slice-072 + slice-074 confirm carve-out)
  4. MEPD-1 EXCLUDE vs shippability row obligation disentanglement (new this slice — design.md L96 self-justifying claim contradicted by slice-068 actual practice)
  5. Scope-expansion-at-/build-slice-plan-mode + re-Critic discipline (new this slice; N=1 cumulative — watch-list)
- **R-20 candidate fixes (b)/(c)/(d) remain explicitly deferred** — (b) Windows symlink fragility; (c) un-gitignore violates ADR-066 derived-artifacts principle; (d) auto-cp audit gate reserved for empirical refutation of (a). The R-20 retirement is on (a) alone per slice-022 codify-only-what-reality-demands.
- **Close-merge-substep-3-worktree-collision-stop-asymmetry** (queue candidate #7 in `architecture/slice-queue.md`) — slice-073 design.md tracks this as a separate concern touching `skills/commit-slice/SKILL.md` Step 5b sub-step 3. Different surface from slice-074; deferred to slice-075+.
- **Slice-066 reflection's TFFL-1 extension to WS-1 + ETC-1 audits** — `/critic-calibrate` candidate at N=2 cumulative; still pending; slice-075+ target.
- **Critical-path shippability row for slice-074** — design.md L96 declared "no row" per (now-known-questionable) MEPD-1 EXCLUDE reading. The 3+1+3 = 7 new structural-pin tests are protected via full pytest CI (`tests/methodology/test_build_slice_skill_cp_r_step.py` + `test_r_20_retired.py` + `test_build_slice_skill_dirty_tree_resolution.py`) but NOT via shippability runner gate. If `/critic-calibrate` proposal (4) above lands and disentangles MEPD-1 EXCLUDE from shippability obligation, slice-075+ bundle would add row #74 retroactively. Watch-list.

## Critic calibration

Per TRI-1, score each finding via the disposition in `critique.md` + `critique-review.md` + `code-review.md` + reality observed during build/validate:

**Pass-1 first-Critic (design-Critic) findings — 8 total**:
- M1 (recursive-self-application bootstrap contradiction): **VALIDATED** — disposition ACCEPTED-FIXED; without the fix, slice-074 would have invented false evidence for an unfulfillable AC at Phase A.
- M2 (section-extraction regex over-terminates on `## ` codefence comments): **VALIDATED** — disposition ACCEPTED-FIXED; APED-1-executed evidence proved 34-char truncation; tightening to `(?=^## [A-Z])` is sound.
- M3 (cp -r regex over-matches on comment-only mentions): **VALIDATED** — disposition ACCEPTED-FIXED; APED-1 evidence proved leak; guard-prefix anchor forecloses.
- M4 (MEPD-1 EXCLUDE rationale precedent-axis confusion): **VALIDATED + SEVERITY-WRONG accepted at TRI-1** — disposition ACCEPTED-FIXED at Major; meta-Critic recommended Minor at TRI-1, user accepted demotion. Calibration-only; disposition unchanged.
- m1 (TF-1 plan +4 vs 5-row arithmetic): **VALIDATED** — disposition ACCEPTED-FIXED.
- m2 (mission-brief PMI-1 contingency anachronism post-EXCLUDE-decision): **VALIDATED** — disposition ACCEPTED-FIXED.
- m3 (chained-form vs if/then/fi exit-status under future set -e hardening): **VALIDATED** — disposition ACCEPTED-FIXED; cross-impact with M3 handled in single fix block.
- m4 (TF-1 row 4 prose vs function name): **VALIDATED** — disposition ACCEPTED-FIXED.

**Pass-1 meta-Critic (/critique-review) missed findings — 2 total**:
- m-add-1 (single-line if/then/fi constraint not recorded as intentional pin): **VALIDATED** — disposition ACCEPTED-FIXED in-band; RSAD-1 byte-exact-match discipline cited in test docstring.
- m-add-2 (Phase A/B/C terminology lacks glossary mapping to /build-slice Steps): **VALIDATED** — disposition ACCEPTED-FIXED in-band; design.md §"Bootstrap framing" gained glossary + slice-075 sequencing-confirmation paragraph.

**Pass-2 first-Critic (expansion delta) findings — 5 total**:
- B1 (AC#6 no-`-b` regex falsified by canonical `# no -b` trailing comment): **VALIDATED** — disposition ACCEPTED-FIXED; APED-1 evidence proved regex failure; comment-aware lookahead `(?!(?:[^#\n]*?)-b\s)` corrects. Pass-2 meta-Critic ACCEPT confirmed Blocker severity correct (would FAIL Phase A with no path to PASSING absent reasoning).
- M1 (AC#5 token-search PASSES on prose-only narrative without codefence): **VALIDATED** — disposition ACCEPTED-FIXED; codefence-scoped `_point_4_codefence_body` extraction + 5th anchor token `git commit -m "scaffold(slice-NNN):` close the gap.
- M2 (`_point_4_block` no upper boundary): **VALIDATED** — disposition ACCEPTED-FIXED; shared mechanism with M1 (one regex change, two findings closed).
- m1 (no slice-070 reflection L127 citation in codified comment): **VALIDATED** — disposition ACCEPTED-FIXED.
- m2 (NO-auto-stash discipline not structurally pinned): **VALIDATED** — disposition ACCEPTED-FIXED; 3rd structural-pin test `test_point_4_codefence_does_not_contain_git_stash` added; TF-1 plan +1 row tied to AC#5.

**Pass-2 meta-Critic (/critique-review)**: **0 missed findings / 0 suspicious / 0 severity adjustments — exemplary calibration**. The pass-2 first-Critic applied APED-1 execution to 3 of 5 findings (B1, M1, M2) with concrete falsification proof. Independent meta-Critic APED-1 re-execution of B1 fix against 10 synthetic edge cases (including tab + path-with-`-b` variants) confirmed empirical soundness. ACCEPT verdict is intentional and warranted; manufacturing meta-findings would have been worse than the small ACCEPT-with-confidence-high outcome.

**Code-Critic findings — 6 total (advisory; all DEFERRED)**:
- M1 (`$wt_base`/`$repo_root`/`$default` variable-scope at point 4): **NOT-YET — DEFERRED to slice-075+ bundle**; real semantic defect; will re-score in slice-075's empirical first-governed-slice run. If slice-075 ships dirty-on-default + executes point 4's codefence recipe, M1 materializes loud-and-clear; if not, remains theoretical.
- m1 (`<scaffolding files>` placeholder underspecification): **NOT-YET — DEFERRED**.
- m2 (cp-r seed duplicated at point 4): **NOT-YET — DEFERRED**.
- m3 (AC#6 test regex comment-position-fragile, false-alarm on re-read): **NOT-YET — DEFERRED**; code-Critic itself noted "Severity dropped to Minor because the regex is correct under the canonical prose; just brittle to refactoring."
- m4 (`_branch_state_section` helper duplicated verbatim): **NOT-YET — DEFERRED**.
- m5 (subprocess `check=True` masks audit-internal errors): **NOT-YET — DEFERRED**.

**Missed by Critic**: None this slice. The 3-Critic stack caught every defect surfacing at build/validate; no defects post-validate surfaced unflagged. The N=10 cumulative complementarity of the 3-Critic stack continues to be the highest-signal review surface for in-house methodology slices.

**Pattern**: pass-2 first-Critic + meta-Critic interaction on the expansion delta is the calibration-grade signal this slice surfaces. APED-1 execution on regex-shape contracts is the gold-standard rigor; the pass-2 first-Critic ran APED-1 on 3 of 5 findings BEFORE filing, and the meta-Critic ran independent APED-1 against the Builder draft fix on 10 synthetic edge cases. This is the canonical shape for /critique pass on prose-as-executable-contract surfaces — should be encoded into the Critic agent prompt at slice-075+ /critic-calibrate (when it lands).

## Lessons for next slice

- **PSQ-3 + R-20 retire two distinct axes of post-vault-in-git tax** — PSQ-3 retired the rebase-discipline class (slice-073), R-20 retired the cp-r tax class (slice-074). Together they close two of the three "post-vault-in-git operational friction" classes; the third (switch-commit-switch) is also codified by THIS slice as expansion scope. **Slice-075's BRANCH-2 prereq check is the first cleanroom run** — all three classes are now structurally addressed via codified SKILL.md prose. If slice-075's Phase A surfaces ANY new operational friction at the prereq step, that's a fresh N=1 axis.

- **Scope-expansion-at-/build-slice-plan-mode + re-Critic-the-delta + TRI-1-EXT** is the methodology-strict path for any future plan-mode user-approved expansions. Don't try to make it less rigorous; the cost (~30 min for dual-Critic pass on the delta) is acceptable for the defect-prevention value (pass-2 found 5 ACCEPTED-FIXED defects including 1 Blocker that would have stalled Phase A red-test verification).

- **For methodology-revision slices that codify shell recipes inside SKILL.md prose**, the structural-pin tests MUST anchor to the bash codefence body (not the prose narrative) AND to the executable shape (not the comment). Pass-2 M1 + M3 are both instances of "Critic / Builder reasoning that overlooks the prose-vs-codefence distinction in test contracts." APED-1 execution against synthetic input + canonical-line should be MANDATORY for any structural-pin regex on codified shell recipes. **The pass-2 first-Critic's gold-standard rigor (APED-1 on 3 of 5 findings) is the model for slice-075+ design-Critic runs on codification slices.**

- **`/critic-calibrate` is now SEVERELY overdue at FIVE simultaneous signals** (TPHD-1 N=7 + BC-GLOBAL-2 N=6 + AC-count > 5 N=3 + MEPD-1-EXCLUDE-vs-shippability N=1 + scope-expansion-discipline N=1). Slice-075+ should run `/critic-calibrate` as the highest-priority slice candidate alongside the slice-075+ bundle. The accumulated signal-strength is now well past the empirical threshold for a high-value calibration run.

- **R-20 retirement is the structural reset point** — slices 067-074 paid the cp-r tax manually (N=9 cumulative); slice-075+ inherits the codified prose at Phase A prereq. The N+1 first-governed-slice doctrine (slice-040) predicts slice-075's Phase A will surface structurally-novel edges of the codified step IF dirty-tree-on-default fires (the code-Critic M1 variable-scope defect would materialize there). Watch slice-075's build-log Events line for the first empirical execution.

- **Switch-commit-switch codification's no-stash discipline pin (pass-2 m2)** is the canonical example of "promote prose-declared discipline to structural pin in the SAME slice" — for future codifications, any out-of-scope discipline declaration SHOULD be paired with a regex-anchor or structural-pin test. The cost is one extra test function; the benefit is forestalling silent discipline regression. Promote to /critic-calibrate proposal at slice-075+ as a Critic-prompt addition: "for any out-of-scope discipline that's load-bearing enough to declare, structurally pin it in the same slice."

## Vault updates made

- [[architecture/risk-register#R-20]] — status `mitigating` → `retired`; new `**Retired**: slice-074 ...` paragraph cites bootstrap-exception per CRP-1/ADR-024.
- [[skills/build-slice/SKILL.md]] — `### Branch state` point 1 + point 4 prose extended (cp -r codification + switch-commit-switch codefence).
- [[architecture/slices/_index.md]] — auto-regenerated at Step 6.
- [[architecture/slices/archive/_index.md]] — auto-regenerated at Step 6.
- [[architecture/lessons-learned.md]] — chronological entry appended at Step 5.

**MEPD-1 EXCLUDE — no methodology-changelog v.73.0 entry, no PMI-1 atomic bump, no shippability row #74 added** per design.md L96 carve-out. Forward-sync gates skipped per MEPD-1 EXCLUDE (no in-repo `methodology-changelog.md` edit + no `VERSION` bump + no `ai-sdlc-tools` package re-install — all three would be no-op CLEAN if invoked).
