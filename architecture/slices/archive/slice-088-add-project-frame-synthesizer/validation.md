# Validation: Slice 088 add-project-frame-synthesizer

**Date**: 2026-05-31
**Result**: PASS

## Per-criterion results

### AC1: deterministic synthesizer emits a tight ephemeral 3-section frame (synthesis, not concat; ASCII-safe stdout)
- **Status**: PASS
- **Evidence**: Real-repo run `$PY -m tools.project_frame_synth --repo-root . --slice-dir architecture/slices/slice-088-...` → 14-line frame with `## Identity` / `## Trajectory` / `## Impact`, ATTACK-LENS preamble, Trajectory naming `PFS, PCR, DCE, BCSG, PSQ, BRANCH` (deduped families incl. the letter-suffixed PCR-2b post-M1-fix) + 6 pending candidates + 3 score-ranked open risks; exit 0; em-dash/arrow in extracted text emitted clean. `tests/methodology/test_project_frame_synth.py` 7 tests PASS (identity/trajectory/impact present, tight-budget, deterministic-regen, synthesis-not-concatenates [dedup + score-shown + retired-excluded + named-candidates + letter-suffix family], impact-degrades, budget-clamp, API-pin). Bespoke cp1252 test PASS (`assert "→" in proc.stdout` — em-dash survives under cp1252).
- **Notes**: ephemeral confirmed — no tracked file written; stdout-only.

### AC2: /design-slice consults the project-frame BEFORE designing (shift-left, Step 0.5)
- **Status**: PASS
- **Evidence**: `test_design_slice_skill_frame_consult.py::test_design_slice_consults_frame_before_design` PASS — pins the `$PY -m tools.project_frame_synth ... --slice-dir` invocation within the line-anchored `### Step 0.5` seam AND asserts Step 0.5 ordinally precedes Step 1. Manual: `skills/design-slice/SKILL.md` Step 0.5 ("Consult the project-frame BEFORE designing") present + forward-synced (OSDG-1 drift green).

### AC3: /critique and /critique-review receive the frame; Dim-7 consumes it
- **Status**: PASS
- **Evidence**: `test_critique_skill_frame_input.py` + `test_critique_review_skill_frame_input.py` PASS — pin the `# project-frame.md` block (line-anchored) within each skill's `### Step 2:` agent-prompt-body seam. `agents/critique.md` Dim-7 (b) updated to read the handed-over frame; CAD-1 (`test_critique_agent_drift.py` + `critique_agent_drift_audit`) green.

### AC4: tests — behavioral + structural-pins + OSDG-1 drift + CAD-1
- **Status**: PASS
- **Evidence**: 3 new OSDG-1 drift tests (design-slice/critique/critique-review) PASS; 3 structural-pins PASS; CAD-1 PASS; TF-1 strict 13/13 PASSING. OSDG-1 guarded set extended (CLAUDE.md prose + 3 drift tests are the load-bearing artifacts).

### AC5: anchoring guard explicit; full pytest + audits pass; BC-PROJ-9 propagated; shippability row added
- **Status**: PASS
- **Evidence**: ATTACK-LENS adversarial preamble is the frame's first line (anti-anchoring). Full suite **1255 passed / 0 failed**. All 16 Step-6 audits green (TF-1/WIRE-1/BC-1/PMI-1/INST-1/UTF8-STDOUT-1/CRP-1/PCA-1/BCI-1/MCFS-1/STP-1/AVFS-1/TVFS-1/NAW-1/BRANCH-2/DCE-1 + LINT-MOCK). BC-PROJ-9 5-surface fan-out complete (PMI-1/INST-1 = 34 tools); shippability row 93 added (PTFCD-1 + SCMD-1 clean). PFS-1 v0.78.0 + 5-part PMI-1 bump synced.

## VAL-1 layered safety checks (Step 5b)
**Result**: CLEAN — 0 secrets (Layer A), 0 hallucinated imports (Layer B), 0 suppressed. project_frame_synth imports resolve (stdlib + `tools._stdout` + `tools.risk_register_audit`).

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
Not applicable — `**Walking-skeleton**: false`, `**Exploratory-charter**: false`; audits no-op.

## Shippability catalog regression check (Step 5.5)
**Result**: PASS — `tools.shippability_runner` → **92 row(s), 92 PASS, 0 FAIL** (runner exit 0). SCMD-1 + PTFCD-1 pre-catalog gates clean (all cited test files + functions exist, incl. row 93). This slice introduced no regression in any past slice's critical path.

## Multi-instance validation
**Required?**: no — a read-only local synthesis tool + skill-prose edits; no multi-user / multi-device / sync surface.
**Result**: not-applicable

## Reality surprises
- **M1 (code-Critic, fixed in-slice)**: the `_RULE_TITLE_RE` regex silently dropped letter-suffixed rule-ids (`PCR-2b`/`PCR-2a`) — caught only by the code-Critic EXECUTING the regex against the real changelog, not predicted by design or the dual design-Critic. Fresh instance of the regex-APED-1 / BC-PROJ-13 miss class. Impact on next slice: reinforces "execute new parse rules against the real corpus, including `-Na` letter-suffix variants, at design time."
- **cp1252 deviation (build plan-mode)**: the dual-Critic ratified `_ascii_fold()`; reading the actual code in plan-mode revealed UTF8-STDOUT-1's `reconfigure_stdout_utf8()` is the codebase-standard, mandatory, and sufficient mechanism — the Critics correctly flagged the *risk* but prescribed a fix fighting the established mechanism. Calibration input: Critics reviewing a new tool should check the codebase's existing solution for a flagged risk-class before prescribing a novel fix.
- **R-26 registered** (open, downgraded-by-design): advisory-frame silent-all-degrade residual (R-7 analogue).
