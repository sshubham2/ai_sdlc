# Slice 027: add-pipeline-chain-auto-advance

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: none from register directly — closes a pipeline-ergonomics gap (manual re-invocation between every loop step). Methodology-surface change → `critic-required: true` (in-house methodology surface trigger; tier `high`).
**Test-first**: false  (defer audit-vs-prose split to `/design-slice`; AC1 is audit-shaped — see Step 6 note)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Every in-loop pipeline skill currently ends in a human-readable `## Next step` prose section, so the operator must manually re-invoke each subsequent skill (`/design-slice`, `/critique`, …) one at a time. This slice codifies a **Pipeline Chain Auto-advance** discipline: each in-loop skill (a) declares its successor in a normalized, machine-actionable form, and (b) on successful completion with no pending user-input gate, auto-invokes that successor via the Skill tool. The chain runs autonomously from `/slice` through `/reflect` and HARD-STOPS before `/commit-slice`, which remains user-invoked. Any user-input/feedback gate (plan approval, TRI-1 triage, validation FAIL, BLOCKED critique) pauses the chain and surfaces to the user.

## Acceptance criteria

1. Every in-loop pipeline skill — `slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `validate-slice`, `reflect` — declares its successor skill in a normalized, machine-actionable directive (not human-only prose), with the successor of `reflect` declared as the terminal stop (`/commit-slice`, user-invoked, never auto-triggered).
2. Each in-loop skill, on successful completion with no pending user-input gate, auto-invokes its declared successor via the Skill tool without waiting for the user; the existing manual-invocation path still works unchanged.
3. The auto-advance chain terminates after `/reflect`. `/commit-slice` is never auto-invoked under any path; its user-invoked contract is explicitly restated.
4. An enumerated set of user-input/feedback gates HALTS auto-advance and surfaces to the user (resume only on explicit user action). The set covers at minimum: `/critique` Step 4.5 TRI-1 user-owned triage; `/critique` BLOCKED → design revision; `/build-slice` plan-mode approval (ExitPlanMode) and mid-slice smoke-gate failure; `/validate-slice` any per-criterion FAIL.
5. The discipline is codified in `methodology-changelog.md` (new version entry, atomic bump across in-repo `VERSION` + installed `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`) and propagated into `architecture/shippability.md` per RPCD-1/SCPD-1; the `## Pipeline position` section of every touched in-repo skill is byte-equal to its installed copy, verified by a parametrized `tests/methodology/test_pipeline_position_block_drift.py` over all 8 skill pairs (mini-CAD / CAD-1 class).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Successor declared, normalized, machine-actionable in all 7 in-loop skills | grep each `skills/<name>/SKILL.md` for the normalized successor directive block; `reflect` declares `/commit-slice` as terminal user-invoked stop |
| 2 | Auto-invoke on clean completion; manual path intact | Read each skill's completion section: confirms an explicit "auto-invoke successor via Skill tool unless a user-input gate is pending" instruction; manual invocation prose still present |
| 3 | Chain stops before `/commit-slice` | `reflect/SKILL.md` and `commit-slice/SKILL.md` both state `/commit-slice` is user-invoked and never auto-triggered; no in-loop skill names `/commit-slice` as an auto-advance target |
| 4 | User-input gates halt the chain | Each gate-bearing skill (`critique`, `build-slice`, `validate-slice`) carries an explicit "DO NOT auto-advance; surface to user and wait" directive at its enumerated gate(s); the gate list is centralized in the changelog discipline entry |
| 5 | Codified + propagated + drift-clean | `methodology-changelog.md` has the new v0.41.0 entry; in-repo `VERSION` / `plugin.yaml.version` / installed `~/.claude/ai-sdlc-VERSION` agree; new shippability row present; `$PY -m tools.critique_agent_drift_audit` + `$PY -m pytest tests/methodology/test_pipeline_position_block_drift.py` + `$PY -m tools.plugin_manifest_audit` + `$PY -m tools.install_audit` all PASS; `/drift-check` clean |

## Must-not-defer

- [ ] User-input gate enumeration is COMPLETE for the in-loop skills — auto-advancing past a gate that needs the user is the critical safety failure of this slice and must not happen
- [ ] `/commit-slice` stop boundary is hard and explicit in both `reflect` and `commit-slice` skills (no path auto-triggers it)
- [ ] Existing manual single-skill invocation remains fully functional (no regression for operators who run steps one at a time)
- [ ] Atomic version bump (in-repo `VERSION` + `plugin.yaml.version` + installed `~/.claude/ai-sdlc-VERSION`) — partial bump is a PMI-1 violation
- [ ] Shippability catalog row added per RPCD-1/SCPD-1; no catalog regression
- [ ] `## Pipeline position` section byte-equal in-repo↔installed for all 8 skills (parametrized drift test — CAD-1 / mini-CAD class)

## Out of scope

- Ancillary / maintenance skills NOT in the per-slice loop (`/status`, `/drift-check`, `/archive`, `/reduce`, `/sync`, `/supersede-slice`, `/critic-calibrate`, `/diagnose`, `/triage`, `/discover`, `/adopt`, `/risk-spike`, `/user-test`, `/repro`, `/slice-candidates`, `/heavy-architect`) — their `## Next step` prose stays as-is; normalizing them is a possible follow-on slice
- Auto-advancing `/reflect` → `/slice` (starting the NEXT slice is a deliberate user decision; reflect→slice handoff stays manual)
- Any change to `/commit-slice`'s own behavior beyond restating its user-invoked contract
- Building a generic skill-chaining engine / config file — this slice codifies directive prose in the skills, not a new runtime

## Dependencies

- Prior slices: [[slice-026-enforce-critique-review-prerequisite]] — CRP-1 prerequisite-gate + verbatim-STOP-routing pattern to mirror for gate-halt prose; [[slice-021]] — BRANCH-1 bootstrap-reference precedent (a chain skill cannot fully self-trigger the build that authors it)
- Vault refs: [[shippability]], [[methodology-changelog]], [[decisions/ADR-019]] (rule-ID `-D` / NON-`-D` naming convention — decide rule ID at `/design-slice`)
- Risk register: none

## Mid-slice smoke gate

At ~50% of build (after `slice` + `design-slice` + `critique` skills are edited, before the rest), run:
```
$PY -m tools.plugin_manifest_audit
$PY -m tools.critique_agent_drift_audit --repo-root .
```
Expected: both PASS, and the three edited skills show a normalized successor directive + (where applicable) gate-halt directive. If fails: STOP, diagnose, don't continue editing the remaining skills.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
