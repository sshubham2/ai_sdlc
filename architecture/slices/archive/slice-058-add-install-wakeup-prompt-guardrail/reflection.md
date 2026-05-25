# Reflection: Slice 058 add-install-wakeup-prompt-guardrail

**Date**: 2026-05-22
**Shipped**: YES

## Validated
- design.md's core claim — seed the wakeup-prompt guardrail via a Step-3d-modelled `INSTALL.md` → global `~/.claude/CLAUDE.md` append — validated: `### 3h` appended cleanly, idempotent (heading-check skip) + confirmation-gated; AC1 test PASS.
- The three load-bearing `ScheduleWakeup` facts + the `/loop` carve-out are stateable in a concise advisory block — validated: AC2 test PASS (4 discrete whitespace-collapsed anchors).
- The prose-existence-pin test approach (slice-045 `test_install_md_correctness.py` class) — validated: genuine FAIL→PASS contrast (3 FAIL pre-edit → 3 PASS post-edit at the mid-slice smoke gate).
- ADR-057's placement decision (global-only via `INSTALL.md`, citing ADR-049's decided global-only install posture) — validated: built exactly that way; `/triage` + `/adopt` untouched; zero friction.
- The Inclusion-heuristic "no methodology-changelog entry / no VERSION bump" classification — validated: both Critics independently upheld it; MEPD-1(b) discharged by name against the real META-1 assertion at `tests/methodology/test_methodology_changelog.py:136` (zero new `## v...` sections → vacuously satisfied).

## Corrected
- None. design.md was executed verbatim — zero design deviations. (The two meta-Critic EXTEND findings, M-add-1 + M-add-2, were corrected into design.md DURING `/critique-review`, before build — they are not post-build corrections.)

## Discovered
- **INSTALL.md hard-coded version literals re-drift (N=2).** slice-045 fixed a stale `v0.20.0` by replacing it with a hard `v0.54.0` literal; that literal then re-drifted across the v0.48–v0.54 bumps and was stale again (`v0.54.0` vs `VERSION` 0.62.0) by slice-058. The first Critic caught it (B2). slice-058's fix removes the literal entirely (references `VERSION` instead), so `INSTALL.md` now carries **zero** version-number literals — drift-proof by construction. Pattern: recipe / methodology docs must reference `VERSION` dynamically, never hard-code a version literal. (Build-check promotion candidate — see Step 5b below.)
- The slice-045 regression test (`test_install_md_has_no_stale_v0_20_0_literal`) pins only the *specific* `v0.20.0` literal — it would not have caught the `v0.54.0` re-drift. slice-058 deliberately did not generalize it (the drift-proof reword leaves nothing to drift); the residual latent gap is a *future* `INSTALL.md` edit re-introducing a literal — which the proposed build-check would address.

## Deferred
- None. The slice completed all in-scope work. (The per-project `/triage`+`/adopt` guardrail route — ADR-057 option 2 — was *rejected* on reach/granularity grounds, not deferred; ADR-057 notes it remains available as future work if a pipeline-specific variant is ever wanted.)

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all 8 findings ACCEPTED-FIXED, user-ratified CLEAN) + reality during build/validate:

- **B1** (test-fn name inconsistent across 3 sites — FBCD-1): VALIDATED — real cross-file divergence; the canonical-name fix held (build used it consistently; TF-1 + tests all aligned).
- **B2** (stale `v0.54.0` literal at INSTALL.md:18): VALIDATED — real stale literal; drift-proof reword applied + validated (0 version literals remain in INSTALL.md).
- **M1** (AC3 row-count ambiguity): VALIDATED — real ambiguity; the "AC3 = exactly one function" clarification held; build implemented one function.
- **M2** (genuine-contrast under-specified): VALIDATED — the four-discrete-asserts design paid off: each anchor FAILed individually pre-edit; the AC2 test is non-tautological.
- **m1** (ADR-057 numbering): VALIDATED (informational) — the Critic's "verified clean, no defect" check was accurate.
- **m2** (`## v0.63.0` next-version reference): VALIDATED (informational) — the Critic's correctness confirmation was accurate.
- **M-add-1** (AC2 pins a still-"Draft" block — test/text coupling): VALIDATED — meta-Critic missed-finding; freezing the block + naming 4 verbatim anchors held (build anchored on the frozen phrases; genuine contrast confirmed).
- **M-add-2** (new install step placement unspecified): VALIDATED — meta-Critic missed-finding; the `### 3h`, no-renumber specification was applied exactly; build appended 3h cleanly with no cross-ref churn.

**Missed by Critic**: none. Both Critic layers together caught every issue; the build executed verbatim with zero deviations and every Step-6 gate passed first-run. (BC-GLOBAL-2 surfaced at the BC-1 pre-finish gate, but that is an always:true evergreen gate-surfacing — a non-violation — not a Critic miss.)

**Pattern**: first Critic — 6/6 findings VALID, 0 false alarms, correct severities. Meta-Critic EXTEND added 2 genuine findings the first Critic missed, both in dimensions the first Critic structurally under-weighted: *recipe completeness* (M-add-2 — step placement within the numbered procedure) and *test/text freeze coupling* (M-add-1 — pinning a still-"Draft" artifact). Consistent with the slice-040 N+1 doctrine + the slice-037 "dual-Critic precision on codification-class work" law — N≥11 cumulative zero-false-alarm on codification slices; the meta-Critic earning its keep as the DR-1 structural backstop.

## Lessons for next slice
- Recipe / methodology docs (`INSTALL.md` especially) must reference `VERSION` dynamically — never hard-code a methodology version literal. Hard literals re-drift every bump (N=2: v0.20.0, v0.54.0). When fixing a stale literal, **remove** the literal, don't refresh it.
- For a content slice where a test pins prose, FREEZE the prose at design time and name the verbatim test anchors — a "Draft" artifact under a downstream pin is a latent test/text divergence (M-add-1). Same canonical-phrase discipline FBCD-1 applies to test-function names.
- A new step in a numbered procedure needs an explicit placement decision at design time, including whether to renumber — check for letter-referenced cross-refs first (INSTALL.md's "Source independence" section cross-references Step 3f/3g, which made append-as-`3h` cheaper than insert-as-`3e`).

## Vault updates made (thin vault — small list)
- This slice's [[design.md]] — the 8 Critic findings' ACCEPTED-FIXED edits were applied during `/critique` + `/critique-review` (recorded in critique.md).
- [[drift-log.md]] — 2026-05-22 slice-058 pre-finish audit entry (0 blockers, 0 majors).
- [[shippability.md]] — row #58 added (during `/build-slice` as AC3's deliverable; this IS the slice's Step-5.3 catalog entry — no duplicate added at `/reflect`).
- No ADR superseded; no `risk-register.md` entry added — the slice is preventive and retires no registered risk; the B2 re-drift pattern is captured as a lesson + a build-check candidate, not an open risk.
