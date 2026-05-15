# AI SDLC pipeline (adopted into existing codebase)

**Mode**: Standard — see `architecture/triage.md`
**Adopted**: 2026-05-13
**Vault**: `architecture/`
**Active slice**: check `architecture/slices/_index.md` (currently: none active; 18 slices archived)

This repository IS the AI SDLC pipeline source — it dogfoods its own methodology. Read this with that context: the rules below aren't aspirational, they're the contracts the codebase audits against.

## Hard rule before editing code

If the change is more than a typo / single-line tweak / comment / local-variable rename:

1. Check `architecture/slices/_index.md` for an active slice
2. If none → **ASK** the user: "Run `/slice` first, or is this small enough to skip?"
3. Wait for explicit answer.

## Brownfield rules

- **Code is truth, docs are hypothesis.** In this repo the gap is narrow because skill prose IS executable contract (Claude reads SKILL.md and acts), but still verify before acting on doc claims about behavior. Doc says X but code does Y → code wins, log the discrepancy.
- **Respect existing conventions.** Follow the pattern unless a slice explicitly revises it.
- **Deviations need an ADR.** Breaking convention = written reason, not a judgment call. ADRs are append-only (supersede via new ADR per SUP-1; never edit in place).
- **Refactors need a slice.** No "while I'm here" cleanups — slice-018 exists precisely because cleanup-without-slice would have left a latent flaw.
- **Tests-first for bug fixes.** Reproduce with a failing test before fixing (run `/repro`).
- **Graphify before wide changes.** `$PY -m graphify reachable --from=<file> --graph graphify-out/graph.json` to see blast radius. `$PY -m graphify blast-radius --from=<file>` for AST-derived impact.
- **Branch-per-slice.** Per **BRANCH-1** (`methodology-changelog.md` v0.35.0): every `/build-slice` runs on a `slice/NNN-<slice-name>` branch created at the `## Prerequisite check ### Branch state` sub-section; `/commit-slice --merge` no-ff merges back to the resolved default branch + safe-deletes the slice branch. Escape-hatch via canonical `BRANCH=skip — rationale: <text>` DEVIATION line in build-log.md Events. `tools/branch_workflow_audit.py` enforces at Step 6 pre-finish.
- **Pipeline auto-advance.** Per **PCA-1** (`methodology-changelog.md` v0.41.0): each in-loop skill carries a machine-actionable `## Pipeline position` block and, on clean completion with no pending user-input gate, auto-invokes its declared successor — the loop runs `/slice`→`/reflect` autonomously and HARD-STOPS before `/commit-slice` (always user-invoked). Fail-closed: enumerated user-input gates (TRI-1 triage, BLOCKED critique, plan-mode approval, mid-slice smoke failure, validate FAIL/PARTIAL) HALT the chain. `tools/pipeline_chain_audit.py` enforces the chain wiring at Step 6 pre-finish.

## Self-hosting discipline (specific to this repo)

This pipeline develops itself, so any methodology rule must be exercisable on this codebase:

- **CAD-1 (Critic-agent content-equality)**: `agents/critique.md` in-repo MUST be byte-equal to installed `~/.claude/agents/critique.md`. Run `$PY -m tools.critique_agent_drift_audit --repo-root .` before commits that touch the Critic agent.
- **PMI-1 (plugin manifest audit)**: `plugin.yaml` MUST enumerate every skill/agent/tool that exists on disk and vice-versa; `version` field MUST match `VERSION`. Run `$PY -m tools.plugin_manifest_audit` before commits.
- **INST-1 (install audit)**: the canonical skill/agent/template lists in `tools/install_audit.py` MUST match `plugin.yaml`. Drift in either is a hard violation.
- **Mini-CAD for `slice` skill**: `skills/slice/SKILL.md` in-repo MUST be byte-equal to installed copy (`tests/methodology/test_slice_skill_drift.py`).
- **Builder ↔ Critic separation**: `/critique` and `/critique-review` are mandatory in Standard mode (default heuristic — see slice-010). Skipping requires a documented rationale in `risk-tier`.

## Vault discipline

- ADRs are append-only — supersede via a new ADR with `supersedes: ADR-NNN`, never edit in place.
- Design deviations → update the active slice's `design.md` (don't carry forward stale design claims).
- Run `/drift-check` before commit.
- Shippability catalog (`architecture/shippability.md`) is the single source of truth for "must never silently regress" claims. Per RPCD-1 / SCPD-1, every new audit rule MUST propagate its consumer references into the shippability catalog.

## Testing discipline

Before declaring "tests pass" on code inside an active slice: run `/validate-slice`, not just the test suite. `/validate-slice` runs VAL-1 + WS-1 + ETC-1 and includes shippability catalog regression checks; raw `pytest` runs miss these.

Audits are not optional: BC-1 (build-checks), RR-1 (risk-register), CAD-1 (Critic drift), PMI-1 (plugin manifest), DR-1 (critique-review structural), TF-1 (test-first), WS-1 (walking-skeleton), WIRE-1 (wiring matrix), ETC-1 (exploratory charter), CSP-1 (cross-spec parity), SUP-1 (supersession), LINT-MOCK-1/2/3 (mock-budget) all gate slice finish.

## Shared Python interpreter

Per `~/.claude/CLAUDE.md`: use `$PY = "$HOME/.claude/.venv/Scripts/python.exe"` (Windows) — never activate, call by absolute path. `graphify` is editable-installed from `~/.claude/packages/graphify`.

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m tools.<audit_name>
& $PY -m graphify code .        # rebuild code graph
& $PY -m graphify vault architecture   # rebuild vault graph
```

Skills: `~/.claude/skills/<name>/SKILL.md`. Templates: `~/.claude/templates/`. Agents: `~/.claude/agents/<name>.md`.
