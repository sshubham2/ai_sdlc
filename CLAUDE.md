# AI SDLC pipeline (adopted into existing codebase)

**Mode**: Standard — see `architecture/triage.md`
**Adopted**: 2026-05-13
**Vault**: `architecture/`
**Active slice**: check `architecture/slices/_index.md` (currently: none active; 18 slices archived)

This repository IS the AI SDLC pipeline source — it dogfoods its own methodology. Read this with that context: the rules below aren't aspirational, they're the contracts the codebase audits against.

## Hard rule before editing code

If the change is more than a typo / single-line tweak / comment / local-variable rename:

1. Check `architecture/slices/_index.md` for an active slice
2. If none → **ASK** the user via structured options (per the Ask discipline below): "Run `/slice` first, or is this small enough to skip?"
3. Wait for explicit answer.

## Ask discipline

**Ask discipline**: when a skill needs user input, present it as structured options (with a recommended choice) via the `AskUserQuestion` tool — never a bare free-text prompt. A bare prose ask is legitimate only where `AskUserQuestion` genuinely cannot model the input. Rationale: Claude Code notifies the user only on options prompts; a free-text question blocks silently.

Per **SOAD-1** (`methodology-changelog.md` v0.56.0; [[ADR-050]] generalizes [[ADR-048]]'s gate-specific structured-options-ask requirement into a pipeline-wide skill-ask discipline). Pinned by `tests/methodology/test_soad1_structured_options_ask_rule.py`.

## Brownfield rules

- **Code is truth, docs are hypothesis.** In this repo the gap is narrow because skill prose IS executable contract (Claude reads SKILL.md and acts), but still verify before acting on doc claims about behavior. Doc says X but code does Y → code wins, log the discrepancy.
- **Respect existing conventions.** Follow the pattern unless a slice explicitly revises it.
- **Deviations need an ADR.** Breaking convention = written reason, not a judgment call. ADRs are append-only (supersede via new ADR per SUP-1; never edit in place).
- **Refactors need a slice.** No "while I'm here" cleanups — slice-018 exists precisely because cleanup-without-slice would have left a latent flaw.
- **Tests-first for bug fixes.** Reproduce with a failing test before fixing (run `/repro`).
- **Graphify before wide changes.** `$PY -m graphify reachable --from=<file> --graph graphify-out/graph.json` to see blast radius. `$PY -m graphify blast-radius --from=<file>` for AST-derived impact.
- **Worktree-per-slice + branch.** Per **BRANCH-2** (`methodology-changelog.md` v0.68.0; [[ADR-063]]; partial-supersedes [[ADR-019]] / BRANCH-1 / `Branch-per-slice` workflow sub-mode (a) build-time branch-create + extends sub-mode (c) audit-time refusal — Branch-per-slice citation preserved as historical anchor for archive Glob discoverability per ADR-063 §Scope of supersession): every `/build-slice` runs in a **filesystem-isolated worktree** at the canonical sibling-dir path `<main-parent>/<main-name>-wt/slice-NNN-<slice-name>` on a dedicated `slice/NNN-<slice-name>` branch (created via `git worktree add ... -b slice/NNN-<name> <default>` + `cd`); `/commit-slice --merge` no-ff merges back to the resolved default branch + tears the worktree down (idempotent guard) + safe-deletes the slice branch — order load-bearing (worktree-remove MUST precede branch-delete). Escape-hatch via canonical `WORKTREE=skip — rationale: <text>` DEVIATION line in build-log.md Events; `BRANCH=skip` (BRANCH-1 historical anchor) preserved as legacy parallel escape-hatch per ADR-063 §Scope of supersession 4th-surface inheritance. `tools/branch_workflow_audit.py` enforces at Step 6 pre-finish with 11 violation kinds (7 BRANCH-1 carry-forward + 4 BRANCH-2 worktree-mode additions). Retires R-17 (uncommitted-slice-A-WIP-contaminates-slice-B class closed structurally). **Split-slice folder-naming convention** (per **ADR-046** / R-6): split-slice follow-up slices use a numeric `slice-NNN-` folder + `slice/NNN-<name>` branch at the next free slice number (`max(existing)+1`); the `NNNx` letter (e.g. `030C`) is a prose lineage label only — it never appears in the folder or branch name. A letter-suffixed folder (`slice-030B-…`) is rejected at the prerequisite gate with an actionable convention-naming message; rename to the numeric form and keep `NNNx` as the documented split-lineage label in prose (milestone identity-note + reflection lineage + risk-register sub-entry cross-refs).
- **Pipeline auto-advance.** Per **PCA-1** (`methodology-changelog.md` v0.41.0): each in-loop skill carries a machine-actionable `## Pipeline position` block and, on clean completion with no pending user-input gate, auto-invokes its declared successor — the loop runs `/slice`→`/reflect` autonomously and HARD-STOPS before `/commit-slice` (always user-invoked). Fail-closed: enumerated user-input gates (TRI-1 triage, BLOCKED critique, plan-mode approval, mid-slice smoke failure, validate FAIL/PARTIAL) HALT the chain. `tools/pipeline_chain_audit.py` enforces the chain wiring at Step 6 pre-finish.

## Self-hosting discipline (specific to this repo)

This pipeline develops itself, so any methodology rule must be exercisable on this codebase:

- **CAD-1 (Critic-agent content-equality)**: `agents/critique.md` in-repo MUST be content-equal modulo line endings to installed `~/.claude/agents/critique.md` (EOL-agnostic per ADR-033 / EOL-DRIFT-1 — CRLF↔LF is not drift; genuine content divergence still is). Run `$PY -m tools.critique_agent_drift_audit --repo-root .` before commits that touch the Critic agent.
- **PMI-1 (plugin manifest audit)**: `plugin.yaml` MUST enumerate every skill/agent/tool that exists on disk and vice-versa; `version` field MUST match `VERSION`. Run `$PY -m tools.plugin_manifest_audit` before commits.
- **INST-1 (install audit)**: the canonical skill/agent/template lists in `tools/install_audit.py` MUST match `plugin.yaml`. Drift in either is a hard violation.
- **Mini-CAD / OSDG-1 (skill-drift content-equality)**: in-repo `skills/<name>/SKILL.md` MUST be content-equal modulo line endings to its installed copy (EOL-agnostic per ADR-033 / EOL-DRIFT-1 — CRLF↔LF is not drift; genuine content divergence still is). Guarded skills: `slice` (`tests/methodology/test_slice_skill_drift.py`), `build_slice`/`commit_slice`/`query_design`/`critique`/`diagnose` (their respective `*_skill_drift.py`), the **review-stack skills `design-slice` + `critique` + `critique-review`** (`test_design_slice_skill_drift.py` + `test_critique_skill_drift.py` + `test_critique_review_skill_drift.py`, all added at slice-088 / PFS-1 / [[ADR-080]] — these three were previously unguarded; slice-088 edits all three SKILL.md to wire in the project-frame, so it brings them under OSDG-1), and the pipeline openers **`triage` + `adopt`** plus the in-loop **`reflect`** under **OSDG-1** (slice-049; ADR-051 extends the slice-007 CAD-1 / slice-010 mini-CAD lineage; the `reflect` member was added at slice-051 / ADR-053 — OSDG-1's "Opener-Skill" name is now a historical label, NOT a scope boundary: the guarded set spans openers AND the in-loop `reflect` skill that owns the AVFS-1 `Step 5b-avfs` block) via `tests/methodology/test_triage_skill_drift.py` + `tests/methodology/test_adopt_skill_drift.py` + `tests/methodology/test_reflect_skill_drift.py`. Extended at slice-096 (R-13) to **`slice-candidates`** (`tests/methodology/test_slice_candidates_skill_drift.py`) — the **last named-but-unguarded member of THIS OSDG-1 family**, NOT a total-skill-coverage claim (≈12 skills such as `discover` / `risk-spike` / `validate-slice` carry no drift test by design — see slice-096 mission-brief Out-of-scope). Its SKILL.md carries the load-bearing ADR-054 read-only `--obo-peek` carve-out; a **test-only** OSDG-1 guarded-set extension (MEPD-1 = EXCLUDE: no new RULE-ID / methodology-changelog entry / VERSION bump — adding a member to the already open-ended set is the rule operating within its documented scope). (`pulse` + `code-review` have drift tests but are not yet enumerated here — a separate courtesy-parity cleanup, out of slice-096's scope.)
- **BCR-1 (Backlog Consume-and-Round-trip discipline)**: when `diagnose-out/backlog.md` exists in the repo, `/slice` MUST consult it as a primary candidate source AND `/reflect` MUST round-trip closed `SC-\d{3}` findings (triggered by an explicit `**Closes:** SC-\d{3}` sentinel header in mission-brief.md OR reflection.md — NOT bare mentions) with an in-place additive `- **Addressed:** slice-NNN-<name> on YYYY-MM-DD` line at the END of each closed candidate block (AFTER `**Evidence:**` sub-list, BEFORE next `### SC-NNN` header). Per **BCR-1** (`methodology-changelog.md` v0.61.0; ADR-055 extends the BC-PROJ-10 / Inclusion-heuristic lineage; mints a new rule; supersedes nothing). Pinned by `tests/methodology/test_bcr_1_backlog_round_trip.py` (8 anchor-presence + position-pin tests on both SKILL.md surfaces — closes the `/diagnose → /slice → /reflect` loop's structural axis; the human-judgement axis remains open as a future `/critic-calibrate` candidate).
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
