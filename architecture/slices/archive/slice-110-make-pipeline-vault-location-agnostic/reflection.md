# Reflection: Slice 110 make-pipeline-vault-location-agnostic

**Date**: 2026-06-04
**Shipped**: YES-WITH-DEFERRALS (Phase-1 = location-agnostic test suite; AC2/AC3/AC4 deferred to a Phase-2 follow-on per the user-approved Phase 1→2 split)

## Validated
- **AC1 (binding): the test suite is vault-location-agnostic** — full suite byte-identical under the in-tree default AND a SEEDED external `AI_SDLC_VAULT_ROOT` (1575 passed / 0 failed in BOTH modes, exit 0 each). The pipeline's test layer is now flip-neutral.
- **AC5: reversible + green-throughout** — `git diff --stat master -- tools/ skills/ agents/ plugin.yaml VERSION methodology-changelog.md` = empty; no `_vault_paths` behavior change; revertible by plain `git revert`.
- **The freeze-cascade re-point mechanism works** — pinning a consumer's `VAULT_ROOT` (+ re-deriving its frozen module-level constants) re-points both function-local `repo_root / VAULT_ROOT / x` readers AND frozen constants (`_INDEX_MD_REL`, `_AUDIT_LOG_PATH`, `_PROJECT_LIVE_REL`). Validated against real consumers in `test_vault_isolation.py`.
- **The call-graph-closure consumer model** — the design-Critic's M1 cause-model held: the PCR family needs `_vault_git` (the `vault_is_external` gate, pcr:329) and the stranded family needs `pulse_worktree_resolver` (`classify_worktree_state`, stranded:482). Both confirmed empirically at build (tests stayed red until the right module was added to the pin set).

## Corrected
- **ADR-101 mechanism: `importlib.reload` → `setattr`-pin** (the slice's own ADR, refined IN-SLICE via a "Build-time refinement" § — append, not an edit-of-a-shipped-decision; ADR-101 was authored this slice and not yet archived). design.md updated to match. NO external ADR superseded; no risk-register status flip; no concept change.
- **AC1 breaker count**: design said "~74"; the live SEEDED flip-sim measured **86** (85 genuine location breakers + 1 pre-existing non-location `psq_1`). Treated the live-measured set as the inventory of record (APED-1), per B1.

## Discovered
- **`importlib.reload` is unsound for re-pointing module-level state when consumer tests compare that module's class/enum identity.** Reload re-executes the module body, rebinding its classes/enums to NEW objects; a test holding `from M import ConflictClass` and asserting `x is ConflictClass.SOFT` then compares a stale object against the reloaded one → false failure. This broke `test_pcr_1_*` under BOTH default and flip-sim when the first pin draft followed ADR-101's reload prescription. **Impact**: the location-agnostic test convention (ADR-101) is `setattr`-pin, not reload. Generalizable Python-testing gotcha; captured in ADR-101 + lessons-learned. (NOT added to risk-register as a code risk — it's a resolved test-authoring convention, not a standing product risk.)
- **The non-vacuity guarantee is split**: the helper's `assert changed` covers only the `VAULT_ROOT`-binding axis; **derived-completeness has no in-helper guard** — its sole proof is the seeded flip-sim full-suite run. A future test that lists a consumer but forgets its `derived` entry will silently read the external store unless the flip-sim is re-run. Documented in the `pin_vault_root` docstring + ADR-101 (code-review m1).
- **A worktree can carry a STALE copy of a shared main-tree coordination ledger** (`slice-queue.md`): the worktree branched before the slice-110 pick regenerated the queue on master, so the worktree's committed queue had a pre-regen malformed cell — a pre-existing red test (`psq_1`) unrelated to this slice's work. Resolved by `git checkout master -- architecture/slice-queue.md` (user-approved stale-ledger reconciliation). **Impact**: a slice whose suite reads committed shared-ledger state can inherit a stale-vs-master red; the queue is a main-tree ledger and the worktree's copy can lag.

## Deferred
- **AC2 (UNAMBIGUOUS in-loop skill vault-op routing)** — archive `mv` (`/reflect`, `/archive`), drift-log.md (`/drift-check`), commit-slice archived reads. → Phase-2 follow-on.
- **AC3 (SKILL.md-prose op-gate)** — extend `tools/vault_flip_prose_inventory.py` with an operational-op gate mode + the `DEFERRED_TO_FLIP` class + shippability propagation + AP-4 code-Critic; implements [[ADR-102]]. → Phase-2 follow-on.
- **AC4 (graphify flip-awareness)** — `/design-slice:62` `graphify vault architecture` target via the seam; 5 non-in-loop sites to the 318-prose-rewrite slice. → Phase-2 follow-on.
- **Optional helper hardening (code-review m1)** — make each `derived` entry loud on a no-op re-derive. Deferred (would false-fail on a default-suite no-op derive; needs a "changed-vs-ambient" check that tolerates the default identity).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed at build/validate:

- **B1** (count undercounted, re-measure live): **VALIDATED** — ACCEPTED-PENDING; the live SEEDED set was 86 (neither the design's 74 nor the empty-sim 99). The "re-measure live as inventory of record" concern was exactly right.
- **B2** (`== 15` count-pin obstacle): **VALIDATED** — ACCEPTED-FIXED; helper + self-tests went to a NEW file, and the autouse fixture added to `test_vault_root_constant.py` is a non-`test_` def, so the `== 15` pin held (verified). The obstacle was real and correctly sidestepped.
- **B3** (readiness audit tokenizer-only; reuse `vault_flip_prose_inventory`): **NOT-YET** — AC3 deferred to the Phase-2 follow-on; re-score there. The reuse direction stands as ratified design.
- **M1** (RETIRE failure cause wrong for worktree path): **VALIDATED** — ACCEPTED-FIXED; the stranded worktree tests failed via `classify_worktree_state`/`pulse_worktree_resolver` exactly as M1 corrected, and the fix required adding `_pwr` to the pin set. Load-bearing — without M1's cause-model the Builder would have chased the wrong symptom.
- **M2** (incomplete enumeration; narrow AC2): **VALIDATED** — ACCEPTED-FIXED; the narrowing + deferral became the Phase-1/2 split.
- **M3** (`/archive` not OSDG-1 guarded): **VALIDATED** — ACCEPTED-FIXED; factual correction was right (moot for Phase-1 since AC2 deferred → no skill edits).
- **m1** (AC5 shell mix): **VALIDATED** — cosmetic, fixed.
- **m2** (AP-4 code-Critic on new parser): **NOT-YET** — deferred with AC3.
- **m3** (helper home): **VALIDATED** — new file confirmed.
- **M-add-1 / M-add-2 / M-add-3** (meta-Critic: reuse-not-3rd-classifier / gate-visible `DEFERRED_TO_FLIP` / shippability propagation): **NOT-YET** — all AC3-scoped, deferred to the Phase-2 follow-on.

**Missed by Critic**: the design-Critic EXECUTED the freeze-cascade reload and declared it "SOUND — no unbounded transitive by-value imports" (dimension: Unfounded assumptions), but **missed that `importlib.reload` rebinds the consumer's CLASS/ENUM objects**, breaking consumer tests that compare reloaded-module identity (`x is ConflictClass.SOFT`). The Critic verified reload re-points the VALUE (`VAULT_ROOT`) correctly but not that it swaps the TYPE objects. This reddened `test_pcr_1_*` under both modes at build and forced the reload→setattr mechanism change (ADR-101 refinement). **Calibration heuristic for the design-Critic**: when a proposed mechanism reloads a module, check whether any consumer test compares that module's class/enum/exception identity (`is` / `isinstance` / `except SpecificError`) — reload breaks those even when it re-points values correctly.

**Pattern**: the design-Critic's empirical execution (APED-1) was strong on the dimension it tested (value re-pointing) but the test was incomplete — "executed and sound" covered the happy path (does VAULT_ROOT change?) not the identity-preservation path (do held class refs survive?). Execution depth, not just execution presence, is the calibration axis here.

## Lessons for next slice
- For the Phase-2 follow-on (`route-in-loop-skill-vault-ops-via-seam`): the location-agnostic test convention is **`setattr`-pin via `tests/_vault_isolation.pin_vault_root`** — never `importlib.reload` a consumer whose tests compare its class/enum identity. New vault-resolving tests follow this convention.
- When a slice's suite reads committed shared-ledger state (`slice-queue.md`), check the worktree's copy is current vs master before treating a red as a slice regression — a worktree can lag the main-tree ledger.
- Keep the seeded flip-sim in the loop when adding tests/constants under the ADR-101 convention — it is the ONLY guard for `derived`-completeness.

## Vault updates made (thin vault)
- [[lessons-learned.md]] — slice-110 entry (reload→setattr; worktree ledger staleness).
- [[shippability.md]] — new row (the helper self-tests as slice-110's critical path).
- This slice's [[design.md]] + [[decisions/ADR-101]] — reload→setattr build-time refinement (recorded during build; noted here).
- No ADR superseded; no risk-register status change (R-32 retires at the physical flip, not here); no concept change.
