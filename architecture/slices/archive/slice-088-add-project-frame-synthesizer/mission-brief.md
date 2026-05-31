# Slice 088: add-project-frame-synthesizer

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: the structural blind spot behind the slice-087 miss — the review stack reviews each slice **in isolation** with no awareness of the project's strategic direction / trajectory (no risk-register ID yet; register during this slice if warranted)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

A slice can be locally correct yet strategically wrong — slice-087 designed a "flag-all-unmerged" detector that breaks the project's parallel-slice direction, and neither `/design-slice` nor either Critic layer caught it because none had the project's *trajectory* in front of it (the user caught it). This slice ships an **ephemeral, regenerated-per-slice project-frame** — a tight (≤~half-page) synthesis of *what this project is*, *where it's deliberately heading*, and *this slice's impact on the whole* — and feeds it to `/design-slice` (so designs come out direction-aware), `/critique`, and `/critique-review`. It is the durable, systematic version of the manual "tell me before build / why did critique miss it" safeguards, and the input that the already-shipped `agents/critique.md` Dim-7 "strategic-direction-fit + architectural-concurrency" probe (committed `64f6ea3`) is written to consume.

**Decoupling note (PSQ parallel)**: this slice is needed **regardless of slice-087's outcome** and shares **zero blast-radius** with it (087 touches `skills/slice` + `skills/pulse` + `tools/stranded_slice_audit.py`; this touches `skills/design-slice` + `skills/critique` + `skills/critique-review` + `tools/project_frame_synth.py`). The two run in parallel BRANCH-2 worktrees — itself a live exercise of the parallel-slice model.

## Acceptance criteria

1. A **deterministic** synthesizer (`tools/project_frame_synth.py` — a tool, not a skill, per [[ADR-080]]) emits an **ephemeral** project-frame **to stdout** — never hand-maintained, regenerated each invocation — from existing truth-sources: **identity** (`concept.md` / `triage.md`), **trajectory** (recent in-repo `methodology-changelog.md` rule families + pending `architecture/slice-queue.md` candidates + open `risk-register.md` entries + the slice's own ADR option-rejection notes), and **impact** (the slice's `mission-brief.md` / `design.md`). Output is **tight** (hard `_MAX_FRAME_LINES = 40` budget). It is **synthesis, not concatenation** — pinned by a behavioral property a naive concat fails: Trajectory names the **deduped active rule-FAMILY** (`PSQ` / `BRANCH-2`), open risks **sorted-by-score with score shown**, slice-queue candidates **by name**. All emitted output is **ASCII** (cp1252-safe stdout).
2. `/design-slice` consults the project-frame **BEFORE designing** (shift-left, Step 0.5), so the design is direction-aware from the start. (At Step 0.5 the slice's own `design.md` does not yet exist, so the Impact section is expected-degraded to mission-brief-only — that is normal, not an error.)
3. `/critique` and `/critique-review` receive the project-frame as a Step-1 context input (added to their Inputs lists), so both Critic layers review against where the project is *deliberately heading*, not only its static current artifacts. The `agents/critique.md` Dim-7 probe (already shipped) is updated to consume the handed-over frame rather than re-fetching trajectory artifacts itself.
4. Tests: synthesizer behavioral (identity/trajectory/impact sections present; tight-budget enforced; regenerates deterministically from fixtures) + structural-pin on the 3 skills' new frame-consult/input prose + OSDG-1 drift for `design-slice` / `critique` / `critique-review` + CAD-1 for the agent edit.
5. **Anchoring guard** is explicit (the frame is a lens to attack with, not a narrative to nod along to — the Dim-7 probe phrases direction-fit adversarially); full pytest + all Step-6 audits pass; the new tool propagated across the BC-PROJ-9 5-surface inventory; shippability row added.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | behavioral | tests/methodology/test_project_frame_synth.py | test_frame_has_identity_trajectory_impact | PASSING |
| 1 | behavioral | tests/methodology/test_project_frame_synth.py | test_frame_respects_tight_budget | PASSING |
| 1 | behavioral | tests/methodology/test_project_frame_synth.py | test_frame_regenerates_deterministically | PASSING |
| 1 | behavioral (M4) | tests/methodology/test_project_frame_synth.py | test_frame_trajectory_synthesizes_not_concatenates | PASSING |
| 1 | cp1252 (B1/B2) | tests/methodology/test_utf8_stdout_regression.py | test_project_frame_synth_survives_cp1252_with_u2192 | PASSING |
| 2 | structural-pin | tests/methodology/test_design_slice_skill_frame_consult.py | test_design_slice_consults_frame_before_design | PASSING |
| 3 | structural-pin | tests/methodology/test_critique_skill_frame_input.py | test_critique_inputs_include_project_frame | PASSING |
| 3 | structural-pin | tests/methodology/test_critique_review_skill_frame_input.py | test_critique_review_inputs_include_project_frame | PASSING |
| 4 | drift (OSDG-1, NEW) | tests/methodology/test_design_slice_skill_drift.py | test_in_repo_and_installed_design_slice_skill_md_are_content_equal | PASSING |
| 4 | drift (OSDG-1, NEW) | tests/methodology/test_critique_skill_drift.py | test_in_repo_and_installed_critique_skill_md_are_content_equal | PASSING |
| 4 | drift (OSDG-1, NEW) | tests/methodology/test_critique_review_skill_drift.py | test_in_repo_and_installed_critique_review_skill_md_are_content_equal | PASSING |
| 4 | entry-pin (PFS-1) | tests/methodology/test_methodology_changelog.py | test_v_0_78_0_pfs1_entry_present_in_repo | PASSING |
| 5 | inventory-pin | tests/methodology/test_project_frame_synth_tool_inventory.py | test_project_frame_synth_in_canonical_inventory | PASSING |

> **Corrected at design (2026-05-31):** `design-slice` / `critique` / `critique-review` are NOT currently OSDG-1-guarded — no `test_*_skill_drift.py` exists for them (verified on disk). This slice CREATES three new drift tests (reusing `tests/skill_drift_equality.py::assert_md_forward_synced`, modeled on `test_reflect_skill_drift.py`) and extends the OSDG-1 guarded set + root `CLAUDE.md` description. The `agents/critique.md` Dim-7 update is CAD-1-guarded by the existing `test_critique_agent_drift.py`.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Synthesizer produces a tight frame | `test_project_frame_synth.py` (3 cases) PASS; manual run on this repo emits ≤~40 lines with identity/trajectory/impact |
| 2 | `/design-slice` consults it first | structural-pin test + manual `/design-slice` dry-run shows the frame consulted before design writing |
| 3 | Both Critics receive it | structural-pin tests on the two skills' Inputs lists; manual `/critique` hands the frame to the agent |
| 4 | OSDG-1 + CAD-1 clean | drift tests green; `critique_agent_drift_audit` clean |
| 5 | No regression; anchoring-safe | full `pytest`; `/validate-slice`; Dim-7 probe phrased adversarially (reviewed) |

## Must-not-defer

- [ ] **Tight frame, not a dump** — enforce a hard line/size budget; a bloated frame makes the Critic skim and lose sharpness (net-negative).
- [ ] **Ephemeral / regenerated** — no standing hand-maintained `direction.md`; the frame is recomputed each invocation from truth-sources, so it cannot drift.
- [ ] **Anchoring guard** — the frame must be a lens to *attack* with; the Dim-7 probe and the skill prose must frame direction-fit adversarially, not as a narrative to absorb.
- [ ] **Shift-left at `/design-slice`** — the context layer is consulted BEFORE designing, not only at critique (that's the whole point — prevent the misfit, don't just catch it).
- [ ] **CAD-1 / OSDG-1** — the agent + 3 skill edits forward-synced; installed copies content-equal.

## Out of scope

- A standing/cached project-frame file (ephemeral-only by design).
- Auto-deciding direction-fit (the synthesizer *surfaces* the frame; the Critic/Builder judge fit).
- Re-litigating the Dim-7 probe text (shipped via `/critic-calibrate`; this slice only wires the frame into it).
- slice-087's stranded-detector (separate parallel slice).

## Dependencies

- Prior: the `/critic-calibrate` 2026-05-30 run (Part B Dim-7 probe, committed `64f6ea3`) — this slice is Part A of that proposal. Sources: `concept.md`, `triage.md`, `methodology-changelog.md`, `architecture/slice-queue.md` (PSQ-1), `risk-register.md`.
- Parallel sibling (zero overlap): [[slice-087-add-stranded-slice-detection-to-slice]].
- Skill surfaces: `skills/design-slice/SKILL.md`, `skills/critique/SKILL.md`, `skills/critique-review/SKILL.md`; agent `agents/critique.md` (Dim-7).

## Mid-slice smoke gate

After writing `tools/project_frame_synth.py` + its behavioral test (before skill wiring): run it against THIS repo and eyeball the output:
```
$PY -m pytest tests/methodology/test_project_frame_synth.py -q
$PY -m tools.project_frame_synth --repo-root . --slice-dir architecture/slices/slice-088-add-project-frame-synthesizer
```
Expected: a ≤~40-line frame naming the parallel-slice family (PSQ/BRANCH-2) as the active trajectory + pending slice-queue candidates + open risks. If it dumps the whole project or misses the trajectory: STOP, tighten the synthesis before wiring the skills.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer addressed (esp. tight-frame + anchoring-guard + shift-left)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes
- [ ] No new TODOs / FIXMEs / debug prints
