# Reflection: Slice 075 close-merge-substep-3-worktree-collision

**Date**: 2026-05-28
**Shipped**: YES

## Validated

- **BRANCH-2 worktree-vs-main-tree collision closure (P1.2)** — validated by `test_substep_3_includes_main_tree_transition_before_checkout` PASS + APED-1 empirical execution of `git worktree list --porcelain | awk '/^worktree / {print $2; exit}'` returning `C:/Users/sshub/ai_sdlc` (main tree) correctly. The `cd "$main_tree"` prepend BEFORE `git checkout $default` resolves the BRANCH-2 collision (`fatal: '<default>' is already checked out at '<main-tree-path>'`) — codifies slice-074's empirical pragmatic workaround (Builder cd'd to main tree ad-hoc) into prose.
- **WT-clean preflight repositioning to sub-step 2.1. (P2.4)** — validated by `test_wt_clean_preflight_does_not_contradict_substep_2_commit` PASS + `test_wt_clean_preflight_preserves_silent_wt_discard_protection_intent` PASS. The lift from preflight (was L168) to NEW sub-step 2.1. between sub-step 2 (commit) and sub-step 2.5 (PSQ-3 rebase) closes the WT-clean-vs-commit-ordering contradiction while preserving M5 silent-WT-discard local-state-loss protection intent at the new post-commit position.
- **Decimal `2.1.` marker CommonMark ordered-list compliance** — validated by post-fix SKILL.md rendering (Markdown parses `2.1.` as ordered-list continuation; preserves slice-073 PSQ-3 sub-step `2.5.` sibling-convention symmetry). Per /critique m2 ACCEPTED-FIXED — rejected earlier "2-bis" draft which Markdown would render as bold prose.
- **SIBLING-BUT-DISTINCT awk idiom** — validated by APED-1 empirical execution: shared `/^worktree /` regex anchor + divergent AWK action across all 3 awk-with-worktree sites in SKILL.md (sub-step 3 + sub-step 5 + Step 5d sub-step 5). No `2>/dev/null` divergence class from slice-073 recurring.
- **Section-scoping mandatory via `_step_5b_section()` helper** — validated by /code-review byte-level cross-spec parity check: the literal `Pre-flight guardrails (run BEFORE any state change):` header appears 3× in SKILL.md (L166/L207/L242), and Steps 5c (--push) + 5d (--sync-after-pr) legitimately retain WT-clean preflights — section-scoping prevents the test from false-FAIL/PASS via sibling-sub-mode prose. Per /critique M2 ACCEPTED-FIXED.
- **TF-1 WRITTEN-FAILING via `2.1.` anchor (per /critique-review M-add-1 + M-add-2)** — validated by stash-and-rerun: pre-fix SKILL.md has no `2.1.` literal → `_extract_substep_2_1_block()` prelude guard raises clean diagnostic; post-fix → block extraction returns 2.1. body containing the 3 intent literals. The `2.1.` anchor distinguishes post-fix lifted position from pre-fix L168 (which already had `silent-WT-discard` + `STOP` + `Print:`) AND pre-fix L181 PSQ-3 conflict-STOP (which already had `git status --porcelain` after L173 `git commit`).
- **PSQ-3 re-entry semantics preserved (per ADR-068)** — validated by /critique drift-from-vault check + design.md §Contracts re-entry trace: post-rebase-resolve re-invocation has sub-step 2 SKIP (nothing to commit) → sub-step 2.1. passes trivially (WT already clean before SKIP) → sub-step 2.5 fast-forward no-ops → sub-step 3 proceeds. Vacuous on re-entry by construction.
- **Sub-step 5 idempotent worktree-remove ordering preserved (per ADR-063)** — validated by /code-review empirical execution: sub-step 5's specific-branch awk extraction still works correctly from the post-`cd "$main_tree"` cwd context; returns slice-075 worktree path; sub-step 5 → sub-step 6 ordering preserved load-bearing per ADR-063 §Decision.
- **SCMD-1 mini-CAD parity** — validated by `test_commit_slice_skill_drift.py` PASS post-prose-surgery + post-SCMD-1-resync (user-authorized Self-Modification boundary copy from in-repo → installed). EOL-agnostic per ADR-033.
- **MEPD-1 EXCLUDE confirmed** — validated by PMI-1 audit: v0.72.0 unchanged; no methodology-changelog entry; no atomic bump; no `## v0.NN.0` header added. Cites parents ADR-063 / ADR-068 / ADR-020 contracts as in-band methodology-prose-fix.

## Corrected

(No design.md or ADR claim refuted by reality. The slice executed per design plan; 2 in-band RSAD-1 defects surfaced + resolved at mid-slice smoke within original AC scope.)

In-band test-pin tightening (not a design correction, but documented for traceability):
- **AC#1 test pin literal**: tightened from bare `git checkout` to canonical invocation `git checkout $default` per build-time RSAD-1 FINDING (build-log L12). Narration mentions of `git checkout` in sub-step 3 informative prose (intro + failure-message references) would pollute the ordering offset check otherwise.
- **SKILL.md annotation literals**: 2 annotations rephrased to avoid satisfying structural-pin negative-anchors — Edit 1 annotation `git status --porcelain` → "porcelain status check" (avoided AC#2 sub-assertion (a) negative-anchor); Edit 2 annotation `git checkout` → "default-branch switch" (avoided AC#1 pre-cd `git checkout` mention).
- **Sub-step 3 failure-message narration**: rephrased from "`git checkout $default` from the worktree fails with..." → "a default-branch checkout from the worktree fails with..." — preserves informativeness while keeping `git checkout $default` invocation-unique to the actual command line.

## Discovered

- **RSAD-1 annotation-literal-pollution sub-class N=3 cumulative on this slice alone** — 2 surfaced at build-time mid-slice smoke (Edit 1 + Edit 2 annotation literals) + 1 surfaced post-finish at /code-review (code-Critic m1: `_extract_substep_2_1_block` uses unanchored `find("2.1.")` substring; narration paragraph at L169 contains `2.1.` literal too). All 3 instances share the same structural class: prose that uses a literal which is ALSO a structural-pin test's positive- or negative-anchor pollutes the test's offset/presence semantics. The build's resolution (rephrase 2 specific literals + tighten 1 test pin) was instance-specific; the discipline didn't generalize. This is the **strongest /critic-calibrate proposal target** to extend critique-review.md L60's calibration-signal proposal text: agents/critique.md RSAD-1 sub-clause MUST enumerate explicit APED-1-against-pre-fix-prose enforcement language at /critique time + Builder MUST audit annotation drafts BEFORE writing them.

- **Code-Critic m1**: latent narration-leakage in `_extract_substep_2_1_block` (`find("2.1.")` returns offset 1131 narration vs offset 1812 real list marker; 681-char prefix gap). DEFERRED to slice-076+ bundle. Latent regression vector — IF future slice removes `silent-WT-discard` from sub-step 2.1. body but leaves L169 narration intact, AC#4 paired-pin would still PASS (test misses the regression).

- **Code-Critic m2**: source-document-move stale-anchor sweep miss — 5 in-vault references to old `enable-parallel-slice-pending-items.txt` path remain in mission-brief.md (L5/L66/L72/L81) + design.md (L6) after the file was moved to `architecture/slices/slice-075-.../source-pending-items.txt`. DEFERRED to slice-076+ bundle. TPHD-1 sub-mode (a) "file-move-but-anchor-not-swept" sub-class variant — adds to N=7 cumulative TPHD-1 baseline as sub-class N=8 with variant flag.

- **3-Critic stack value-validation extends to N=11 cumulative** (slice-063 → slice-075 inclusive) — code-Critic surfaced 2 structural-analysis-lane findings (test-pin latent weakness + file-move stale anchor) NEITHER reachable by the design-Critic stack (which reads design.md + mission-brief at /critique time, doesn't run APED-1 against post-fix prose at substring-vs-line-start anchor granularity). Pattern remains structurally stable across 11 cycles. Do NOT collapse the 3-Critic stack.

- **Voluntary-restraint discipline N=16 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072/073/074/**075**) — code-Critic v1 advisory findings consistently route to next-slice bundled cleanup. Pattern structurally stable across 16 cycles.

- **MEPD-1 EXCLUDE + DID add shippability row #74 = N=2 confirmation** that MEPD-1-EXCLUDE-vs-shippability-row axes are independent (per slice-074 Discovered signal N=1). Cumulative N=2 (slice-068 EXCLUDE DID add row #67 + slice-075 EXCLUDE DID add row #74) confirms the two axes are independent: methodology-changelog entry/PMI-1 bump is one obligation surface; shippability row is a separate obligation universal to every slice. `/critic-calibrate` proposal target P4.4: disentangle the two axes in /reflect Step 5.3 prose.

- **Scope-expansion-at-/build-slice-plan-mode N=1 (slice-074) HELD** — slice-075 plan-mode approval (Option 1 as-drafted, no expansion) preserved single-scope discipline; pattern at N=1 cumulative pending N=3 threshold.

- **/critic-calibrate is now SEVERELY OVERDUE at SIX simultaneous signals** — extends slice-074 reflection's "FIVE simultaneous signals":
  1. TPHD-1 sub-mode (a) Builder-fix-block-introduces-N+1-regressions N=8 cumulative (slice-062/064/067/070/071/072/073/075 — slice-075 m2 new sub-class variant)
  2. BC-1 BC-GLOBAL-2 prose-vs-automation N=7 cumulative (slice-069/070/071/072/073/074/075)
  3. AC-count > 5 N=3 promotion (slice-067/072/074 carve-out confirmed; slice-075 deliberately reverted to 5 ACs without meta-AC #6, but signal stable at N=3)
  4. MEPD-1-EXCLUDE-vs-shippability-row N=2 cumulative (slice-068 EXCLUDE+row, slice-075 EXCLUDE+row)
  5. Scope-expansion-at-/build-slice-plan-mode N=1 (slice-074)
  6. **NEW: RSAD-1 annotation-literal-pollution N=3 cumulative on slice-075 alone** (build-time #1 + build-time #2 + post-finish code-Critic m1) — strongest new signal; cross-Critic-stack class (design-Critic missed; meta-Critic missed; only code-Critic caught the post-finish instance; build-time instances caught only at empirical mid-slice smoke)

## Deferred

- **Code-Critic m1** (narration-leakage in `_extract_substep_2_1_block`) — lands in: slice-076+ `slice-NNN-bundle-075-code-critic-cleanup` per voluntary-restraint N=16. Fix: line-start anchor (`re.search(r'^2\.1\.\s', ...)` OR `section.find("\n2.1. ") + 1`) + add `assert block.count("silent-WT-discard") == 1` post-extraction guard.
- **Code-Critic m2** (source-document-move stale-anchor sweep) — lands in: slice-076+ bundle. Fix: sweep mission-brief.md L5/L66/L72/L81 + design.md L6 — replace bare `enable-parallel-slice-pending-items.txt` with new slice-scaffold path.
- **P1.1 (build-slice point 4 variable-scope)** — separate slice (`slice-NNN-bundle-074-code-critic-cleanup`) per slice-074 source-pending-items.txt accumulation; still pending; lands at slice-076+ (now lineage extends 074 + 075 deferrals).
- **P2.2 (SOAD-1 retrofit for 6 raw yes/no prompts in /commit-slice)** — separate slice; lands at slice-076+ via separate scope.
- **/critic-calibrate run** — separate user-invokable meta-skill; SEVERELY OVERDUE at 6 simultaneous signals (extends slice-074's 5-signal reading); strongest slice-076 candidate alongside the bundled cleanup. User invokes independently — not a /slice candidate per se.
- **PSQ-3 conflict-STOP re-entry semantics** (P2.3) — separate slice; lands when empirical rebase conflict surfaces in real parallel work.
- **R-2 programmatic test for /diagnose cwd-mismatch warning** — risk-register R-2; low-urgency since slice-002.
- **R-13 OSDG-1 drift guard for /slice-candidates** — risk-register R-13; low-urgency.
- **Empirical parallel-slice readiness validation (P6.3)** — solo cooperative parallel-slice empirical run with 2 concurrent Claude sessions; lands when user-driven.
- **PSQ-4 (--push time rebase)** — deferred per ADR-068 §Future flexibility; lands when PR-based workflow demanded.

## Critic calibration

Per TRI-1, scoring each finding via the disposition in `critique.md` § Triage + reality observed during build/validate:

**Design-Critic (first-Critic at /critique pass-1)**:
- **M1** (shippability-row arithmetic ≥75/75 → ≥74/74): **VALIDATED** — disposition ACCEPTED-FIXED; empirical baseline 73 confirmed via `$PY -m tools.shippability_runner`; row #74 added cleanly → 74/74 PASS at /validate-slice.
- **M2** (AC#2 test scoping ambiguous; 3× pre-flight header): **VALIDATED** — disposition ACCEPTED-FIXED; APED-1 confirmed 3 occurrences L166/L207/L242; `_step_5b_section()` helper mandate prevented false-FAIL/PASS across sibling sub-modes.
- **m1** (sibling-but-distinct claim misleading): **VALIDATED** — disposition ACCEPTED-FIXED; APED-1 substring check `awk_a in awk_b` → False; rephrased as "SIBLING-BUT-DISTINCT idiom"; clarity gained.
- **m2** (`2-bis` Markdown rendering): **VALIDATED** — disposition ACCEPTED-FIXED; CommonMark spec confirms `2-bis` renders as bold prose not list item; `2.1.` rename preserves slice-073 PSQ-3 sub-step `2.5.` precedent.

**Meta-Critic (critique-review pass-2)**:
- **M-add-1** (AC#4 pre-fix PASS — L168 has all 3 intent literals): **VALIDATED** — disposition ACCEPTED-FIXED; empirical pre-fix L168 verified to contain `silent-WT-discard` + `STOP` + `Print:`; `2.1.` block-anchored extraction + prelude guard fixes WRITTEN-FAILING semantics.
- **M-add-2** (AC#2 sub-assertion (b) pre-fix PASS — L181 PSQ-3 conflict-STOP has `git status --porcelain` after L173 `git commit`): **VALIDATED** — disposition ACCEPTED-FIXED; empirical confirmation via grep on pre-fix SKILL.md; `2.1.` anchor strategy fixes WRITTEN-FAILING.

**code-Critic (/code-review pass)**:
- **m1** (`_extract_substep_2_1_block` narration-leakage in `find("2.1.")`): **NOT-YET** — disposition DEFERRED to slice-076+ bundle per voluntary-restraint N=16; will re-score in bundle slice. The latent regression vector is real (verified by code-Critic APED-1 — `block.count("silent-WT-discard") == 2`); next slice's fix will validate by stash-test before/after.
- **m2** (source-document-move stale-anchor sweep): **NOT-YET** — disposition DEFERRED to slice-076+ bundle; will re-score in bundle slice. Stale anchors verified: `mission-brief.md:5/66/72/81` + `design.md:6` reference old path; will sweep at bundle.

**Missed by Critic**:
- **Build-time RSAD-1 defect #1** (Edit 1 SKILL.md annotation contained `git status --porcelain` literal that satisfied AC#2 sub-assertion (a) negative-anchor): NEITHER first-Critic NOR meta-Critic flagged at design-stage. Surfaced at build-time mid-slice smoke via test FAIL. Caught only by empirical test execution.
- **Build-time RSAD-1 defect #2** (Edit 2 SKILL.md annotation contained `git checkout` literal at sub-step 2.1. body that polluted AC#1 ordering check — appeared BEFORE `cd "$main_tree"` at sub-step 3): NEITHER first-Critic NOR meta-Critic flagged. Surfaced at build-time via test FAIL with offset 7038 < cd offset 8245.
- **Build-time RSAD-1 defect #3** (Sub-step 3 narration "`git checkout $default` from the worktree fails with..." appeared BEFORE the actual invocation in sub-step 3 body): NEITHER design-Critic nor meta-Critic flagged. Surfaced at build-time via test FAIL with offset 7166 < cd offset 8245. Resolved by tightening AC#1 test pin from bare `git checkout` to canonical invocation `git checkout $default` + rephrasing narration to "default-branch checkout".

All 3 missed instances share the same **RSAD-1 annotation-literal-pollution class**. The design-Critic stack reviewed mission-brief + design.md prose at /critique time; the meta-Critic re-applied dimensions at /critique-review; NEITHER ran APED-1 against my prospective annotation drafts in the in-repo SKILL.md — because the annotation drafts hadn't been written yet at /critique time (the prose surgery is a Phase C build artifact). So this class is structurally **post-design-Critic** — it can only surface at build-time empirical test execution OR at post-build code-Critic structural analysis. Code-Critic m1 caught the 3rd instance (latent narration-leakage in test helper) post-finish.

**Pattern**: For methodology-revision slices that codify shell recipes inside SKILL.md prose AND that pin them via structural tests on negative-/positive-anchor literals, the Builder MUST audit annotation drafts for negative-/positive-anchor literal collisions BEFORE writing them. Each test's pinned literal MUST be a unique enough literal that informative narration prose can't satisfy it accidentally. The /critic-calibrate proposal target: strengthen agents/critique.md RSAD-1 sub-clause with "literal-uniqueness against prospective annotation prose" enforcement language.

## Lessons for next slice

- **For ANY structural-pin test that asserts a literal in prose-as-executable-contract surfaces, the pinned literal MUST be UNIQUE-TO-THE-INVOCATION (not a noun-phrase that appears in informative narration)**. Slice-075 surfaced this 3× in one slice — bare `git checkout`, bare `git status --porcelain`, bare `2.1.` substring all polluted by adjacent narration. Tighten to invocation-form (`git checkout $default`), line-start anchor (`^2.1.\s`), or wrapping context (`\nLITERAL\n`). APED-1 against pre-fix AND post-fix prose at design time would catch.

- **For methodology-revision slices that lift/reposition prose, audit ALL test pins for literal-uniqueness against BOTH pre-fix AND post-fix prose**. Pre-fix collision = false-PASS pre-fix (TF-1 WRITTEN-FAILING violation per M-add-1/M-add-2). Post-fix collision = informative narration pollutes ordering offsets (build-time defects #1-#3 per build-log). Both classes are RSAD-1 sub-mode (a) — the slice authors structural-pin tests + the slice's own prose violates the pins.

- **For file-move operations (e.g., source-document scaffold-relocation), sweep ALL in-vault references to the old path** — TPHD-1 sub-mode (a) sub-class variant "file-move-but-anchor-not-swept" surfaced this slice (5 stale anchors in mission-brief + design pointing to old `enable-parallel-slice-pending-items.txt` path). Cheap defense: at file-move time, grep the slice's own vault for the old path before commit.

- **/critic-calibrate is SEVERELY OVERDUE at 6 simultaneous signals** — the strongest slice-076 candidate alongside the bundled cleanup. Run /critic-calibrate before bundle work to encode the 6 signals into Critic prompt updates BEFORE the bundle slice surfaces a 7th.

- **Voluntary-restraint discipline N=16 cumulative is structurally stable** — the bundled-cleanup-at-N+1 disposition shape continues to absorb code-Critic v1 advisory findings without scope inflation. Slice-076+ bundle inherits 2 findings from this slice (m1 + m2).

- **3-Critic stack N=11 cumulative complementarity** is now empirically stable across 11 cycles. Code-Critic m1 + m2 are structurally unreachable by design-Critic + meta-Critic stack (substring-vs-line-start anchor granularity + file-move-but-anchor-not-swept span the code-Critic's structural-analysis lane). Do NOT collapse the 3-Critic stack.

- **Slice-074's switch-commit-switch-worktree pattern + R-20 cp -r seed at point 1 + structural codification at point 4** functioned cleanly at slice-075's Phase A prereq — N+1 first-governed-slice empirical validation PASSED. Codification stable.

- **PSQ-3 sub-step 2.5 re-entry semantics preserved across sub-step 2.1. insertion** — confirmed by /critique drift check + design.md trace; vacuous on re-entry by construction.

- **The "scope-narrowing-at-design-stage" pattern (slice-073 lesson)** held this slice — design.md option (a) chosen at design time without later expansion at build time. Builder fix-block discipline in /critique tight (zero TPHD-1 sub-mode (a) regressions from the fix-block edits themselves).

## Vault updates made (thin vault — small list)

- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/mission-brief.md]] — 4 ACCEPTED-FIXED edits at /critique TRI-1 (M1 shippability arithmetic + m1 sibling-but-distinct rephrase + AC#5 TF-1 row addition + verification plan row 5 update) + TF-1 plan 4 rows PENDING → PASSING + AC#5 row added at /build-slice
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/design.md]] — 6 ACCEPTED-FIXED edits at /critique TRI-1 (M1 + M2 + m1 + m2 + M-add-1 + M-add-2 sweeps across 5+ surfaces)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/critique.md]] — written + Triage section ratified CLEAN at TRI-1
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/critique-review.md]] — written (dual-Critic pass-2 EXTEND verdict; 2 missed RSAD-1-class findings)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/build-log.md]] — written (Events flight-recorder + Summary; 12+ events documented)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/code-review.md]] — written (CRSI-1 v1 advisory; 0B/0M/2m all DEFERRED to slice-076+ bundle)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/validation.md]] — written (aggregate Result: PASS; 5/5 ACs validated; 74/74 shippability)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/milestone.md]] — continuous updates (slice → design → critique → build → code-review → validate → complete)
- [[architecture/slices/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt]] — moved from repo root for audit-trail integrity (per mission-brief Notes recommendation (a))
- [[architecture/slice-queue.md]] — regenerated at /slice Step 6.5 (PSQ-1 top-10 candidates)
- [[architecture/shippability.md]] — appended row #74 (test_substep_3_includes_main_tree_transition_before_checkout as catalog representative)
- [[skills/commit-slice/SKILL.md]] (in-repo) — Step 5b prose surgery (3 edits): WT-clean removed from preflight + sub-step 2.1. inserted + sub-step 3 main-tree-transition prepended
- [[~/.claude/skills/commit-slice/SKILL.md]] (installed) — SCMD-1 sync (user-authorized Self-Modification boundary)
- [[tests/methodology/test_commit_slice_skill_merge_substep_3_main_tree_transition.py]] (NEW)
- [[tests/methodology/test_commit_slice_skill_merge_wt_clean_preflight_ordering.py]] (NEW)

**NO** methodology-changelog entry / NO PMI-1 atomic bump / NO new ADR / NO risk-register flip (MEPD-1 EXCLUDE confirmed at /build-slice PMI-1 audit v0.72.0 unchanged).

**NO** BCR-1 round-trip needed (no `**Closes:** SC-` sentinel in mission-brief.md or this reflection.md — slice closes P1.2 + P2.4 from source-pending-items.txt, NOT a /diagnose backlog SC-NNN).
