# Slice 049: add-triage-adopt-skill-drift-guards

**Mode**: Standard
**Estimated work**: 0.75 day (rev-1 post-Critic: +changelog v0.57.0 / 4-part PMI-1 bump / entry-pin / ADR-051 per B2 — still ≤1 day; all mechanical)
**Risk retired**: closes the slice-048-discovered latent exposure (N=1) — `triage`/`adopt` SKILL.md have repo+installed copies but no mini-CAD in-repo↔installed drift guard, unlike build_slice/commit_slice/critique/query_design/slice + agents/critique.md (CAD-1). Not promoted to a risk-register ID at N=1; this slice retires it as a coverage gap.
**Test-first**: true  (per TF-1 — the deliverable IS regression tests; genuine-contrast FAIL→PASS is the proof)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The two pipeline-opener skills — `/triage` (greenfield) and `/adopt` (brownfield) — each have an in-repo canonical `skills/<name>/SKILL.md` and an installed `~/.claude/skills/<name>/SKILL.md` that Claude actually reads at runtime. Every other pinned skill in the mini-CAD set (build_slice, commit_slice, critique, query_design, slice) plus `agents/critique.md` (CAD-1) has a content-equality drift guard; triage/adopt do not. A silent divergence on either opener would currently be caught by nothing but human forward-sync discipline (slice-048's must-not-defer #3 was the only control and it is human-dependent). This slice extends the established mini-CAD pattern to both openers, closing the last manual-only forward-sync surface.

## Acceptance criteria

1. `tests/methodology/test_triage_skill_drift.py` exists and asserts `skills/triage/SKILL.md` is content-equal modulo line endings (EOL-agnostic per ADR-033 / EOL-DRIFT-1) to installed `~/.claude/skills/triage/SKILL.md` via the shared `assert_md_forward_synced` helper; it PASSES on the synced tree and its non-tautology is proven by a genuine-contrast FAIL→PASS captured in build-log (former AC3 folded in per Critic M1 — the contrast IS this test's non-tautology proof, not a separate prose-only AC).
2. `tests/methodology/test_adopt_skill_drift.py` exists and asserts `skills/adopt/SKILL.md` is content-equal modulo line endings to installed `~/.claude/skills/adopt/SKILL.md` via the same shared helper; PASSES on the synced tree with its own genuine-contrast FAIL→PASS captured in build-log.
3. slice-049 is recorded as a **methodology-surface behavior change** (per Critic B2 + the `methodology-changelog.md` Inclusion heuristic: a forward-sync miss on triage/adopt acceptable-yesterday is HALTed-today): a `## v0.57.0` changelog entry minting RULE-ID **OSDG-1** (Opener-Skill Drift Guard; extends the mini-CAD / EOL-DRIFT-1 lineage) + a 4-part PMI-1 atomic bump 0.56.0→0.57.0 (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`) + a `test_v_0_57_0_osdg_1_entry_present_in_repo` pin + [[ADR-051]] all ship together.
4. `architecture/shippability.md` gains **exactly one** new catalog row `| 49 | slice-049-add-triage-adopt-skill-drift-guards | OSDG-1 …` whose Critical-path covers BOTH the triage and adopt guards (per meta-Critic B-add-1 — the catalog is strictly one-row-per-slice, keyed `| NN | slice-NNN-name`; the latest is `| 48 | slice-048-…`; "two rows" would break the convention every runner/audit assumes AND make the AC3 `test_v_0_57_0_osdg_1_shippability_consumer_propagation` pin unsatisfiable). The real SRSC-1 runner `tools/shippability_runner.py` executes the new row green (per Critic B1 — the phantom `tests/methodology/test_shippability_catalog.py` cited in rev-0 does not exist; real artifacts are `tools/shippability_runner.py` + `tests/methodology/test_shippability_runner_segment_contract.py` + `tests/methodology/test_shippability_path_existence.py`).
5. The CLAUDE.md `## Self-hosting discipline` Mini-CAD-bullet generalization (must-not-defer) keeps the section passing `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py::test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant` — i.e. the rewritten bullet still contains "content-equal modulo line endings" + "EOL-DRIFT-1" + "ADR-033" and introduces NO "MUST be byte-equal" phrasing (per meta-Critic M-add-1 / slice-039 realign-the-pin-you-touch law — the edit lands in the exact section that pin guards).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Every numbered AC maps to ≥1 row whose `Test path` is a file that **exists on disk** (Critic B1 / PTFCD-1 — `tools/test_first_audit.py --strict-pre-finish` emits `missing-test-path-file` and FAILs on a phantom path). The two new drift-test files are created by this slice (normal test-first); the v0.57.0 entry-pin functions are new functions in the **existing** `test_methodology_changelog.py`. Genuine-contrast (former AC3) is folded into AC1/AC2 per the slice-045 law (a prose-only "build-log captures…" row cannot reach PASSING under `--strict-pre-finish`); the FAIL→PASS transition is captured in build-log as evidence for AC1/AC2.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_triage_skill_drift.py | test_in_repo_and_installed_triage_skill_md_are_content_equal | PASSING |
| 2 | methodology | tests/methodology/test_adopt_skill_drift.py | test_in_repo_and_installed_adopt_skill_md_are_content_equal | PASSING |
| 3 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_57_0_osdg_1_entry_present_in_repo | PASSING |
| 3 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_57_0_osdg_1_shippability_consumer_propagation | PASSING |
| 3 | methodology | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_invariant | PASSING |
| 4 | methodology | tests/methodology/test_shippability_path_existence.py | (whole-module — the single new row #49's cited paths resolve on disk) | PASSING |
| 4 | methodology | tests/methodology/test_shippability_runner_segment_contract.py | (whole-module — SRSC-1 runner parses + executes the single new row #49) | PASSING |
| 5 | methodology | tests/methodology/test_root_claude_md_cad1_eol_agnostic.py | test_claude_md_cad1_mini_cad_states_eol_agnostic_invariant | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | triage drift guard | `<PY> -m pytest tests/methodology/test_triage_skill_drift.py -q` → 1 passed |
| 2 | adopt drift guard | `<PY> -m pytest tests/methodology/test_adopt_skill_drift.py -q` → 1 passed |
| 1+2 | genuine-contrast non-tautology (folded in) | build-log shows, per test: append a non-EOL byte to the installed copy → test FAILs with the drift assertion message; restore → test PASSes. Both transitions captured for triage AND adopt. |
| 3 | behavior-change recorded | `<PY> -m pytest tests/methodology/test_methodology_changelog.py::test_v_0_57_0_osdg_1_entry_present_in_repo tests/methodology/test_methodology_changelog.py::test_v_0_57_0_osdg_1_shippability_consumer_propagation -q` → passed; PMI-1/INST-1 audits green (VERSION 0.57.0 == most-recent `## v` header; `plugin.yaml.version` lockstep) |
| 4 | shippability propagation | exactly ONE new row `\| 49 \| slice-049-…` present in `architecture/shippability.md` (one-row-per-slice convention); `<PY> -m tools.shippability_runner` (the real SRSC-1 runner) executes the new row green; `<PY> -m pytest tests/methodology/test_shippability_path_existence.py tests/methodology/test_shippability_runner_segment_contract.py tests/methodology/test_methodology_changelog.py::test_v_0_57_0_osdg_1_shippability_consumer_propagation -q` → passed |
| 5 | CLAUDE.md prose-pin not regressed (M-add-1) | after the Mini-CAD-bullet generalization, `<PY> -m pytest tests/methodology/test_root_claude_md_cad1_eol_agnostic.py -q` → passed (section still has "content-equal modulo line endings" + "EOL-DRIFT-1" + "ADR-033"; no "MUST be byte-equal") |

## Must-not-defer

- [ ] **Pre-sync evidence preservation (Critic M2)**: BEFORE the forward-sync copy, run an EOL-normalized diff of in-repo vs installed for BOTH openers and record the result verbatim in build-log (expected: identical). If a pre-existing **non-EOL** divergence is found → STOP: the latent bug this slice exists to guard actually occurred; record it in the slice vault + open a risk-register entry BEFORE reconciling. Never silently overwrite a real drift with `cp` (the slice-030A "coincidental cp masks the failure" class).
- [ ] Forward-sync both openers' installed copies (only after the pre-sync diff is recorded) BEFORE asserting equality (slice-035 "reconcile installed copy before the gate that audits it" law); record the sync in build-log.
- [ ] EOL-agnostic comparison only (reuse `assert_md_forward_synced`; do NOT introduce a byte-equality assertion — ADR-033 / EOL-DRIFT-1: CRLF↔LF is not drift).
- [ ] Genuine-contrast proof captured for BOTH tests, not just one (folded into AC1/AC2 — non-tautology evidence per BC-PROJ-5 / slice-045 discipline).
- [ ] **4-part PMI-1 atomic bump (Critic B2)**: `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`, all 0.56.0→0.57.0 in lockstep; the `## v0.57.0` OSDG-1 entry carries a `Rule reference` line (META-1) and a `test_v_0_57_0_osdg_1_entry_present_in_repo` + `_shippability_consumer_propagation` pin; ADR-051 created. INST-1 unchanged (no new skill/agent/tool — only two test modules + an ADR).
- [ ] **Exactly ONE** new shippability row `| 49 | slice-049-add-triage-adopt-skill-drift-guards | OSDG-1 …` covering BOTH guards (meta-Critic B-add-1 — NOT two rows; one-row-per-slice convention, slice-048 row #48 precedent); pipe-free / `\|`-escaped Machine-cmd cells (BC-PROJ-7 / SCMD-1 6-column schema integrity); sequence the catalog row LAST and run the real `tools/shippability_runner.py` SRSC-1 runner + read its output (slice-044 law).
- [ ] CLAUDE.md `## Self-hosting discipline` Mini-CAD bullet generalized to name the opener skills (`triage`, `adopt`) now under OSDG-1; keep EOL-DRIFT-1-precise wording ("content-equal modulo line endings", "EOL-DRIFT-1", "ADR-033"; introduce NO "MUST be byte-equal" phrasing). Done in-slice, not deferred to `/reflect` (slice-022 self-violation-avoidance). **Re-run `tests/methodology/test_root_claude_md_cad1_eol_agnostic.py` immediately after this edit** (meta-Critic M-add-1 / slice-039 realign-the-pin-you-touch law — this edit lands in the exact section that prose-pin guards).

## Out of scope

- A generalized INST-2 mini-CAD audit tool — remains deferred (slice-009/010 law: per-file content-equality tests, NOT a generalized audit; N=1 actual-drift evidence threshold unchanged).
- Drift guards for any other unpinned skills (e.g. design-slice, reflect, pulse) — only triage/adopt are in scope (the slice-048-named gap); a broader sweep is a separate slice if recurrence justifies it.
- `add-soad1-lint-audit` and per-skill ask-prose retrofit (slice-048 Deferred — backlog, not this slice).
- Any prose/behavior change to triage or adopt SKILL.md content itself — this slice only adds guards, it does not edit the openers.

## Dependencies

- Prior slices: [[slice-048-codify-structured-options-ask-rule]] — its reflection "Discovered" section nominates this exact cut; [[slice-010-add-second-skill-drift-test]] / [[slice-007-add-critique-agent-content-equality-audit]] — the CAD-1 / mini-CAD per-file pattern this mirrors; [[slice-035-rename-status-skill]] — "reconcile installed copy before the gate that audits it" law.
- Code refs: `tests/skill_drift_equality.py` (`assert_md_forward_synced`); `tests/methodology/test_slice_skill_drift.py` (canonical shape to mirror); `tests/methodology/conftest.py` (`REPO_ROOT`).
- Vault refs: [[decisions/ADR-033]] (EOL-DRIFT-1); [[shippability.md]]; CLAUDE.md `## Self-hosting discipline`.
- Risk register: none (slice-048-discovered gap, N=1, not a standing risk ID).

## Mid-slice smoke gate

At ~50% of build (both test files written + installed copies synced), run:
```
<PY> -m pytest tests/methodology/test_triage_skill_drift.py tests/methodology/test_adopt_skill_drift.py -q
```
Expected: `2 passed`. Then perturb one installed copy (append a non-EOL char) and re-run — expected: that test FAILs with the drift message. If the perturbed run still PASSes → the comparison is tautological (wrong helper / wrong path); STOP and diagnose, do not continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression); genuine-contrast captured for BOTH tests
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] CAD-1/PMI-1/INST-1/TF-1/SCPD-1/SCMD-1 + full methodology suite green (BC-PROJ-4 real-artifact run, read its output)
