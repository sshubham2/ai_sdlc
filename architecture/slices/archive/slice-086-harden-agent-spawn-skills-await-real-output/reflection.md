# Reflection: Slice 086 harden-agent-spawn-skills-await-real-output

**Date**: 2026-05-30
**Shipped**: YES

## Validated
- Guard authored at the spawn→write seam of all three spawn-skills — validated by `test_r25_await_real_agent_guard.py` (9/9; seam-scoped) + heading_count=1 per skill (worktree + installed).
- The seam-scoped pin genuinely enforces placement, not mere presence — validated by the code-Critic's mutation battery (delete / relocate-out-of-seam / gut-body / em-dash→hyphen all FAIL; unmutated PASSES) and the in-test relocate fixture.
- The body literal `NEVER self-author a placeholder` is unique-to-invocation — validated by an independent grep (0 narration hits for `self-author`/`placeholder` across all three skills); the slice-085 false-negative class does not recur.
- AC-4 ordering invariant held — the global CLAUDE.md stopgap was removed (count→0) only AFTER the skill guard was verified installed (build-log events 00:05→00:08).
- The whole slice dogfooded its own guard: /critique, /critique-review, /code-review were each Agent-spawned and their artifacts written ONLY from the real returned content — never main-thread self-review.

## Corrected
- design.md / mission-brief AC-3 originally claimed `tests/methodology/test_critique_skill_drift.py` exists and that critique + code-review are "ALREADY in the OSDG-1 guarded set" — both refuted by disk (B1/B2). Corrected in this slice's `design.md`, `mission-brief.md`, and `ADR-078` §Context/Options/Decision during /critique (ACCEPTED-FIXED). critique/critique-review have NO content-equality drift test; code-review is the only one of the three that does.
- The pin's spec was initially file-global; reality (meta-Critic M-add-1) showed a relocated guard would stay green — corrected to seam-scoped (`_step2_to_step3_region`), reconciling the design's own "reuses SOAD-1 section-scoping" claim.

## Discovered
- **Pre-existing CLAUDE.md:42 OSDG-1 inventory drift** (B2): the canonical guarded-set line names `critique` + `diagnose` with `*_skill_drift.py` files that do NOT exist on disk, and OMITS `code-review` + `pulse` which DO have drift tests. Bidirectional drift; out of scope here. Candidate: `reconcile-osdg-1-inventory-claude-md-L42` (left for next /slice).
- **The pin test's own region extractor shipped with the exact fragility class the slice guards against** (code-review m1): `.find("### Step 2")` is bare substring, vulnerable to inline-narration mis-anchor + `### Step 20` prefix collision — a slice-022-style self-violation. Fixed in-slice (line-anchored `(?m)^### Step N\b`) per user election, with 2 regression tests.

## Deferred
- `reconcile-osdg-1-inventory-claude-md-L42` — reason: B2 inventory drift is a separate methodology-inventory reconciliation, not an R-25 surface — lands in: next /slice candidate.
- Full OSDG-1 content-equality extension to `critique-review` — reason: R-13-class change (own drift-test module + install-audit wiring); the AC-2 pin already guards its guard-literal — lands in: queued `extend-osdg-1-to-critique-review`.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed during build/validate:

- B1 (phantom `test_critique_skill_drift.py`): **VALIDATED** — ACCEPTED-FIXED; Builder-verified against disk at /critique, meta-Critic re-verified independently; the verification plan would have collection-failed on the phantom path.
- B2 (OSDG-1 set membership vs CLAUDE.md:42): **VALIDATED** — ACCEPTED-FIXED; bidirectional inventory drift confirmed exactly as flagged.
- M1 (em-dash/hyphen drift): **VALIDATED** — ACCEPTED-FIXED; APED-1 + the code-Critic's dash→hyphen mutation confirmed a mismatch fails closed (real risk on a single verbatim-match pin).
- M2 (heading-only pin lets a gutted body pass): **VALIDATED** — ACCEPTED-FIXED; the gut-body mutation confirmed the gap; body literal added.
- M3 (canonical literal absent from AC-1): **VALIDATED** — ACCEPTED-FIXED; cheap cross-file anchor, confirmed useful.
- M-add-1 (file-global vs seam-scoped — meta-Critic EXTEND): **VALIDATED** — ACCEPTED-FIXED; the relocate fixture + code-Critic relocate mutation confirmed a file-global pin would false-pass. Strong meta-Critic catch on an internal design inconsistency the first Critic missed.
- m1 (shippability row precision): **VALIDATED** — ACCEPTED-PENDING → applied at build; single-path row, audit clean.
- m2 (ADR-078 Option-1 con overstated): **VALIDATED** — ACCEPTED-FIXED; harmonized with B1/B2 facts.
- code-review m1 (substring region extractor): **VALIDATED** — advisory; ACCEPTED-FIXED in-slice (user-elected). The discriminating regression test confirmed the pre-fix `.find` would have EXCLUDED the guard on inline-narration input — not hypothetical.

**Missed by Critic**: none by the stack as a whole. The 3-Critic stack reached everything: the design-Critic caught vault-truth (B1/B2) + design-level (M1/M2/M3); the meta-Critic caught the design's internal inconsistency + placement gap (M-add-1) the first Critic missed; the code-Critic caught the runtime-execution property (m1) by EXECUTING the parse rule — a class the design stack structurally cannot reach. No defect surfaced during build/validate that ALL three missed.

**Pattern**: 3-Critic stack complementarity held again, and on a slice whose subject IS review integrity. Each persona caught a distinct, non-overlapping class. The standout: the meta-Critic's M-add-1 was an internal-inconsistency catch (the design cited SOAD-1 section-scoping but specced a file-global pin) — exactly the "review the first Critic's blind spot" value DR-1 exists for.

## Lessons for next slice
- **A structural-pin test on prose-as-executable-contract must SEAM-SCOPE its assertion AND match headings/anchors line-anchored, never bare substring** (slice-086 M-add-1 + code-review m1) — extends the slice-075 "unique-to-invocation literal" + slice-085 "presence-regex ≠ shape-check" lineage to the placement axis. A file-global `in`/`.count()` passes a relocated-out-of-seam guard; a bare `.find("### Step N")` mis-anchors on narration or `### Step 20`. This is now N≥3 (075/085/086) on the "pin precision" family — a strong /critic-calibrate + build-check promotion candidate.
- **Verify vault claims about file/inventory existence against disk at /critique, don't take the design's word** (slice-086 B1/B2) — the design asserted a drift test that didn't exist and OSDG-1 membership the canonical CLAUDE.md:42 contradicted. The Builder verified against disk before drafting dispositions; the meta-Critic re-verified independently. Both blockers were real.
- **A slice that ships a guard should not ship that guard's own test with the exact defect class the guard defends against** (slice-086 code-review m1) — the slice-022 self-violation law, N+1. Fixing m1 in-slice (rather than deferring) closed the irony and hardened the test against the very class (substring-vs-anchored) the slice is about.
- **Dogfooding a review-integrity guard mid-slice is the strongest possible validation** — this slice's own /critique, /critique-review, /code-review each waited for the real Agent and wrote from its returned output; fabricating any of them would have re-committed the exact R-25 defect being closed.
- **MEPD-1 EXCLUDE for a risk-closing fix-slice with an ADR + no new RULE-ID is now N≥5** (077/079/082/084/085 → 086) — VERSION unchanged at 0.77.0; forward-sync gates (MCFS-1/AVFS-1/TVFS-1) no-op. Stable precedent.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-25 flipped **open → retired** with a retirement annotation (residual: prose-enforced, not runtime-blockable — inherent + acknowledged).
- This slice's [[design.md]] + [[mission-brief.md]] + [[decisions/ADR-078]] — corrected B1/B2 vault-truth claims + M1/M2/M3/M-add-1 (applied during /critique; build followed corrected design).
- [[shippability.md]] — row 92 pinning `test_r25_await_real_agent_guard.py` (added at build per AC-5; satisfies /reflect Step 5.3 — the slice's one critical-path entry).
- [[lessons-learned.md]] — slice-086 entry appended.
- [[build-checks.md]] — **BC-PROJ-14** promoted (user-approved /reflect Step 5b): "a structural-pin test on prose-as-executable-contract must pin a unique-to-invocation literal, assert shape, and section/seam-scope its assertion" (pin-precision family N=3, slice-075/085/086). BCI-1 fail-loud sync done: same rule added to `tests/methodology/fixtures/build_checks/canonical_project_checks.md` + literal-pin `test_bc_proj_14_has_expected_structural_identity` in `tests/methodology/test_build_checks_audit.py`; live reconstructed from fixture; `build_checks_integrity` PASS.
- `~/.claude/CLAUDE.md` — removed the `# Spawned-agent output` stopgap (AC-4 migration; recorded here for auditability).
