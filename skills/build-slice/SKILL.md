---
name: build-slice
description: "AI SDLC pipeline. Execute the current slice with plan-mode + verification gates. Reads mission brief, enters plan mode to explore actual code, ships with mid-slice smoke gate, do-not-defer enforcement, and pre-finish gate. Use after /critique blockers are addressed. Trigger phrases: '/build-slice', 'build this slice', 'implement the slice', 'ship the slice'. Works from a 1-page mission brief plus plan mode, not a long sprint file."
user_invokable: true
---

# /build-slice — Execute With Plan Mode + Verification

You are executing the current slice. Approach: plan mode (Builder explores actual code) + mission-brief discipline (gates, do-not-defer, acceptance criteria).

The mission brief is the **intent**. The design is the **shape**. The Critic findings are the **constraints**. Plan mode is the **route through actual code**.

## Where this fits

Runs after `/critique` blockers + majors are addressed. Output: working code + tests + build-log. Hands off to `/validate-slice`.

## Prerequisite check

- Find active slice folder
- Read `mission-brief.md`, `design.md`, `critique.md`, new ADRs from this slice
- If `critique.md` shows BLOCKED: stop, tell user to address blockers first
- If `critique.md` doesn't exist (Standard or Heavy mode): stop, run `/critique` first
- **Run TPHD-1 pre-flight harmonization** (per `methodology-changelog.md` v0.32.0 sub-mode (c)): scan the mission-brief TF-1 plan table; for each row, verify (a) the Test path exists or will be created at the right path, (b) the Test function name will match what gets built. The /critique + /critique-review fix-prose may have changed test function names or AC row references without harmonizing the TF-1 plan in the same fix block (sub-modes (a) + (b) defend at fix-prose time; sub-mode (c) is the prerequisite-check defense-in-depth layer). Flag any drift to user for fix BEFORE Step 1 plan-mode entry. This closes the function-name-staleness audit gap that `tools/test_first_audit.py --strict-pre-finish` does not detect (status-only check per slice-017 /critique B1 ACCEPTED-FIXED).
- **Run CRP-1 critique-review-prerequisite check** (per `methodology-changelog.md` v0.40.0): runs AFTER the `critique.md`-exists check above (there can be no `/critique-review` without a `/critique`). Invoke:

  ```bash
  $PY -m tools.critique_review_prerequisite_audit architecture/slices/slice-NNN-<name>
  ```

  Refusal semantics (exit 1 → STOP):
  - `mandatory-critique-review-absent`: mode ∈ {STANDARD, HEAVY} AND `milestone.md` `critic-required: true` AND `critique-review.md` absent AND no canonical `critique-review-skip` frontmatter key.
  - `escape-hatch-malformed`: `critique-review-skip` key present but value off-canonical (not `^skip — rationale: .+`).
  - `usage-error` / `mode-unresolvable` (exit 2): slice folder / milestone.md missing, or mode unresolvable from `architecture/triage.md` frontmatter `mode:` → fallback `CLAUDE.md` `**Mode**:`.

  On `mandatory-critique-review-absent`, STOP and tell the user verbatim: **"STOP: this slice has a mandatory `/critique-review` (DR-1) that has not been run. Run `/critique-review` for this slice before `/build-slice`. If the skip is deliberate, document it by adding `critique-review-skip: \"skip — rationale: <text>\"` to milestone.md frontmatter (per ADR-024)."** Do not enter Step 1 plan mode until the audit exits 0.

  **Bootstrap exception (slice-026 only)**: per ADR-024, slice-026 is CRP-1 bootstrap-reference instance #1 — it authors this very sub-block, so this sub-block does not exist at slice-026's own prerequisite check and cannot self-gate that build. slice-026's self-application is discharged by `/critique-review` run on slice-026 + the audit run against slice-026's own folder at Step 6. Every slice after 026 inherits a self-gating CRP-1.

### Branch state

Per **BRANCH-1** (`methodology-changelog.md` v0.35.0): branch-per-slice workflow runs at /build-slice as a structural prerequisite (NOT a new Step — slice-021 follows slice-017 TPHD-1 sub-mode (c) precedent of placing prerequisite-class disciplines under `## Prerequisite check` rather than creating a numbered Step 0). The slice's own commits live on a dedicated `slice/NNN-<slice-name>` branch; `/commit-slice --merge` integrates them back at slice end.

Resolve the repo's default branch at runtime (per /critique M1 ACCEPTED-PENDING — replaces hard-coded `master`/`main` for cross-project portability):

```bash
# Primary resolution
default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
# Fallback if no origin remote
[ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
# STOP if neither resolves
```

Then apply the branch-create logic:

1. **If on default branch** (HEAD == resolved default): `git checkout -b slice/NNN-<slice-name>` from current HEAD. Switch is immediate; WT must be clean.
2. **If `slice/NNN-<slice-name>` already exists** (resume after session death): `git checkout slice/NNN-<slice-name>`.
3. **If on any other branch** (including stale `slice/<other-number>-*` from prior conflict): STOP, ask user to switch to default branch or document `BRANCH=skip` escape-hatch in `build-log.md` Events per Step 7c canonical shape.
4. **If working tree is dirty** (`git status --porcelain` non-empty): STOP, ask user to commit or stash. NO auto-stash.

The canonical `BRANCH=skip` escape-hatch line shape (Step 7c-pinned): `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>`. The `tools/branch_workflow_audit.py` (BRANCH-1) audit at Step 6 pre-finish refuses anything else.

## Your task

### Step 1: Load full slice context

State briefly to the user:
- "Slice NNN: <name>"
- "Acceptance criteria: <count>"
- "Must-not-defer items: <count>"
- "Critic blockers addressed: yes / pending"

### Step 2: Enter plan mode

Use ExitPlanMode tooling appropriately. In plan mode:

- **Graphify first** for structural understanding:
  - `$PY -m graphify reachable --from=<module>` — what this module touches transitively
  - `$PY -m graphify blast-radius --from=<module>` — what touches it (reverse reachability)
  - Inline shortest-path (CLI lacks `path`):
    ```bash
    $PY -c "
    import json, networkx as nx
    G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
    try: print(' -> '.join(nx.shortest_path(G, '<target>', '<adjacent>')))
    except Exception as e: print(f'no path: {e}')
    "
    ```
    If path is short, you're near a god node and must design carefully.
  - The PreToolUse hook (installed by `/triage` / `/adopt`) injects a static hint pointing Claude at `GRAPH_REPORT.md` before Glob/Grep — it doesn't redirect those tools, just nudges.
- Then Read specific code files for detail (much less scanning needed after graph queries)
- Build dependency understanding for this slice's surface area
- Identify integration points with existing code
- Draft a concrete task sequence: files to create, files to modify, in what order

The plan should be:
- Grounded in the code you've actually read (not what design.md assumes)
- Specific (file paths, function names)
- Ordered so the mid-slice smoke gate is reachable at ~50% of work
- Sized so each task is independently verifiable

### Step 3: User approval

Present the plan to the user. Wait for approval or revisions.

> **PCA-1 gate-halt (v0.41.0)**: plan-mode approval is an enumerated user-input gate. DO NOT auto-advance into Step 4 execution — present the plan and HALT for explicit user sign-off, even when the pipeline is otherwise auto-advancing.

If user requests changes: revise the plan, re-present.

If the plan reveals the design is wrong: STOP. Tell the user: "Design says X. Code reality requires Y. Stop and revise design, or proceed with a deviation?"

### Step 4: Execute task-by-task with per-task verification

For each task in the plan:

1. Implement the task
2. Run the relevant acceptance criterion check (or smoke test if AC isn't testable yet)
3. If passes: mark complete, move on
4. If fails: fix, then verify again
5. If still fails after reasonable attempts: stop, ask for help (don't accumulate broken state)

### Step 5: Mid-slice smoke gate (at ~50%)

When ~50% of plan is done, run the mid-slice smoke gate from mission brief on a real environment:

- Backend: hit the endpoint with curl or test client; check DB
- Frontend: open the page in a real browser
- Mobile: install on a real device
- ML: run inference on a real sample

If smoke fails: STOP. Diagnose. Don't continue building on a broken base. Often the right move is to revise the plan.

> **PCA-1 gate-halt (v0.41.0)**: a mid-slice smoke-gate failure is an enumerated user-input gate. DO NOT auto-advance — STOP, surface the failure + diagnosis to the user, and HALT. Auto-advance on a broken base is forbidden.

### Step 6: Pre-finish gate

Before declaring slice done, ALL of these must be true:

- [ ] All acceptance criteria PASS with evidence
- [ ] All must-not-defer items addressed (no TODO, no stub, no silent except)
- [ ] `/drift-check` passes (vault and code aligned)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints / console.logs
- [ ] **Mock-budget lint passes (LINT-MOCK-1)** — see "Mock-budget lint" below
- [ ] **Wiring matrix audit passes (WIRE-1)** — see "Wiring matrix audit" below
- [ ] **Build-checks audit passes (BC-1)** — see "Build-checks audit" below
- [ ] **Test-first audit passes (TF-1)** — see "Test-first audit" below (only when `**Test-first**: true`)
- [ ] **Branch workflow audit passes (BRANCH-1)** — see "Branch workflow audit" below
- [ ] **UTF-8 stdout audit passes (UTF8-STDOUT-1)** — see "UTF-8 stdout audit" below
- [ ] **Critique-review prerequisite audit passes (CRP-1)** — see "Critique-review prerequisite audit" below
- [ ] **Pipeline-chain audit passes (PCA-1)** — see "Pipeline-chain audit" below
- [ ] **Build-checks integrity audit passes (BCI-1)** — see "Build-checks integrity audit" below

If any gate fails: don't declare done. Fix or escalate.

#### Branch workflow audit (BRANCH-1)

Per **BRANCH-1** (`methodology-changelog.md` v0.35.0 sub-mode (c)): the slice's commits MUST live on a `slice/NNN-<slice-name>` branch matching the active slice (created at the `## Prerequisite check ### Branch state` sub-section above). Run:

```bash
$PY -m tools.branch_workflow_audit architecture/slices/slice-NNN-<name>
```

Refusal semantics:
- `on-default-branch`: current branch is the resolved default branch AND no canonical `BRANCH=skip` escape-hatch line in `build-log.md` Events.
- `slice-branch-mismatch`: current branch is `slice/<wrong-number>-<wrong-name>` (doesn't match active slice).
- `escape-hatch-malformed`: a `BRANCH=skip` line is present but doesn't conform to the canonical regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+` (HH:MM + `rationale:` token required per Step 7c canonical shape).
- `default-branch-unresolvable`: neither `git symbolic-ref refs/remotes/origin/HEAD` nor `git config init.defaultBranch` resolves (exit 2 usage error).
- `stale-slice-branch`: lingering `slice/*` branches detected from prior `--merge` conflict-recovery (warning class — surfaces but doesn't refuse).

Default-branch resolution mirrors the `## Prerequisite check ### Branch state` sub-section logic.

#### UTF-8 stdout audit (UTF8-STDOUT-1)

Per **UTF8-STDOUT-1** (`methodology-changelog.md` v0.37.0): every `tools/*.py` module exposing `def main(argv: list[str] | None = None) -> int:` MUST call `_stdout.reconfigure_stdout_utf8()` (from the canonical helper at `tools/_stdout.py`) as the first executable statement of `main()`. This retires the recurring Windows cp1252 console encoding class (N=6 cumulative recurrence across slices 007 / 016 / 018 / 020 / 021 / 022).

Run:

```bash
$PY -m tools.utf8_stdout_audit
```

Refusal semantics:
- Any audit tool's `main()` whose first executable statement is not `_stdout.reconfigure_stdout_utf8()` → exit 1 + violation.
- Any audit tool missing the canonical import `from tools import _stdout` → exit 1 + violation.
- `tools/` directory missing at resolved root → exit 2 + stderr.
- SyntaxError parsing any `tools/*.py` → exit 2 + stderr.

Exclusion list: `__init__.py` + leading-underscore helpers (e.g., `tools/_stdout.py`) — neither has `main()`; both are out of scope by structural convention. The PMI-1 audit's `_list_actual_tools` filter mirrors this exclusion to prevent `orphan-tool` false positives.

Self-application: `tools/utf8_stdout_audit.py` itself conforms; the audit run on the post-slice-027 codebase returns `tools_scanned: 20, tools_with_main: 20, tools_clean: 20` (slice-027 added `tools/pipeline_chain_audit.py`, which conforms — `_stdout.reconfigure_stdout_utf8()` is the first statement of its `main()`).

#### Critique-review prerequisite audit (CRP-1)

Per **CRP-1** (`methodology-changelog.md` v0.40.0): the same audit invoked at the `## Prerequisite check` (above) is re-run at Step 6 pre-finish as a defense-in-depth layer — it catches `critique-review.md` deleted mid-build, or `critic-required` flipped `true` during a `/design-slice` scope expansion that post-dated the prerequisite check. It is idempotent and reads the Step-7b-preserved `critique-review-skip:` milestone.md frontmatter key (per ADR-024 the escape-hatch is a frontmatter key precisely so it survives Step 7b's continuous milestone.md rewrite). Run:

```bash
$PY -m tools.critique_review_prerequisite_audit architecture/slices/slice-NNN-<name>
```

Refusal semantics: `mandatory-critique-review-absent` (Important, exit 1) — mode ∈ {STANDARD, HEAVY} AND `critic-required: true` AND `critique-review.md` absent AND no canonical `critique-review-skip` key; `escape-hatch-malformed` (Important, exit 1) — key present, value off-canonical; `usage-error` / `mode-unresolvable` (exit 2). CRP-1 is an **audit-enforced gate** (NON-`-D` per ADR-019; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1) — its programmatic gate is `tools/critique_review_prerequisite_audit.py`.

Bootstrap (slice-026 only, per ADR-024): slice-026 authors CRP-1; at slice-026's Step 6 the audit IS run against slice-026's own folder and MUST exit 0 (self-application discharge — `/critique-review` having been run on slice-026).

#### Pipeline-chain audit (PCA-1)

Per **PCA-1** (`methodology-changelog.md` v0.41.0): every covered pipeline skill MUST carry a well-formed `## Pipeline position` block whose declared successor edge matches the canonical per-slice loop, and the terminal boundary (`reflect` + `commit-slice`) MUST be `auto-advance: false` so `/commit-slice` is never auto-invoked. Run:

```bash
$PY -m tools.pipeline_chain_audit
```

Refusal semantics:
- `malformed-block` (Important, exit 1): a covered skill's `## Pipeline position` section is absent or a required field (`predecessor`/`successor`/`auto-advance`/`on-clean-completion`/`user-input gates`) is missing/unparseable.
- `successor-mismatch` (Important, exit 1): a declared `successor:` ≠ the canonical chain successor.
- `auto-advance-mismatch` (Important, exit 1): a declared `auto-advance:` ≠ canonical — including the terminal guarantee that `reflect` and `commit-slice` are `false`.
- `usage-error` (exit 2): repo root unresolvable, `skills/` dir or a covered SKILL.md missing.

PCA-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1) — its programmatic gate is `tools/pipeline_chain_audit.py`. The audit reads the flat `successor:` field for chain-shape only; the documented `/critique` post-TRI-1 → `/build-slice` hop and `/critique`→`/critique` BLOCKED self-loop live in `on-clean-completion` prose and are NOT flagged (per slice-027 /critique-review m-add-1).

Bootstrap (slice-027 only, per [[ADR-025]]): slice-027 authors PCA-1; the `## Pipeline position` directive does not exist on disk during slice-027's own loop (the chain ran manually per the user's at-invocation directive). At slice-027's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — `/critique-review` having been run on slice-027). Every slice after 027 inherits a self-gating PCA-1.

#### Build-checks integrity audit (BCI-1)

Per **BCI-1** (`methodology-changelog.md` v0.44.0; slice-030A; [[ADR-028]] + [[ADR-029]]): `/reflect` Step 5b promotion is LLM-executed prose with no deterministic source (R-4 witnessed both `architecture/build-checks.md` + `~/.claude/build-checks.md` silently truncated to the last-promoted rule). The only sound control for a non-deterministic step is a deterministic downstream gate. BCI-1 asserts the live build-checks files match the **git-tracked** canonical fixtures (`tests/methodology/fixtures/build_checks/canonical_{project,global}_checks.md`) on **full per-rule structural identity** — `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` — NOT rule-ID-set-only (slice-030A meta-M-add-2: an ID-only check passes a coverage-degraded file, re-opening R-4). Run:

```bash
$PY -m tools.build_checks_integrity
```

Refusal semantics:
- `drift` (exit 1, HALT): a present live file diverges from the canonical fixture — missing/extra rules, **empty present file**, or any structural-field mismatch — OR the project `architecture/build-checks.md` is absent. Message is attributed: *"LOCAL VAULT DRIFT — reconstruct from <fixture>; this is NOT a slice regression"* (retires the R-4 anti-pattern where a truncation read as a confusing slice regression).
- `warn` (exit 0): `~/.claude/build-checks.md` **absent** (file does not exist) — the global file is untracked/environment-dependent; a machine that hasn't installed it must not HALT (slice-030A meta-M3). An *empty present* global file is `drift`/HALT, not WARN (empty != absent — R-4-global not silently reopened).
- `usage` (exit 2): a canonical fixture (the tracked oracle) is missing/unreadable, emits its own parse violations, or repo root is unresolvable.

BCI-1 is an **audit-enforced gate** (NON-`-D` per [[ADR-019]]; naming-class peers BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1) — its programmatic gate is `tools/build_checks_integrity.py`, wired non-opt-out here AND as a `/reflect` Step 5b fail-loud post-write instruction. (The shippability-catalog-row wiring is deferred to slice-030B per the user-approved split; 030A's two wiring points fully retire R-4's substance.)

Bootstrap (slice-030A only): slice-030A authors BCI-1; at slice-030A's Step 6 the audit IS run against the repo and MUST exit 0 (self-application discharge — the live files were just reconstructed from the canonical fixtures). Every slice after 030A inherits a self-gating BCI-1.

#### Test-first audit (TF-1)

Per **TF-1** (`methodology-changelog.md` v0.13.0), when this slice's `mission-brief.md` declares `**Test-first**: true`, every Acceptance criterion must map to one or more tests with a status field whose value at pre-finish is `PASSING`. Run:

```bash
$PY -m tools.test_first_audit architecture/slices/slice-NNN-<name> --strict-pre-finish
```

Refusal semantics:
- `missing-section`: brief declares test-first true but has no `## Test-first plan` section
- `format` / `missing-cells`: table is malformed (need 5 columns: AC | Test type | Test path | Test function | Status)
- `invalid-status`: status outside `{PENDING, WRITTEN-FAILING, PASSING}`
- `ac-without-row`: an AC declared in the brief body has no test-first row
- `non-passing-pre-finish`: any row's status is `PENDING` or `WRITTEN-FAILING` (only emitted with `--strict-pre-finish`)

Default-off semantics: when the brief lacks the `**Test-first**:` field or sets it to `false`, the audit returns clean and the gate passes silently. TF-1 is opt-in per slice; old briefs without the field continue to work.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt automatically.

#### Build-checks audit (BC-1)

Per **BC-1** (`methodology-changelog.md` v0.10.0), every slice's pre-finish runs the build-checks audit to surface evergreen rules promoted from past lessons-learned. The audit reads `architecture/build-checks.md` (project-specific) and `~/.claude/build-checks.md` (global, cross-project), filters rules by applicability, and surfaces matches:

```bash
$PY -m tools.build_checks_audit \
  --slice architecture/slices/slice-NNN-<name> \
  --changed-files <list of files changed by this slice>
```

Applicability is the OR of three signals:
- `Applies to: always: true` — always fires
- `Applies to: <globs>` — fires when any glob matches a changed file (e.g., `src/api/uploads/**`)
- `Trigger keywords: <words>` — fires when any keyword appears in mission-brief.md or design.md

Refusal semantics:
- **Critical rule applies**: this slice MUST address the rule before declaring done. Either fix the issue, or escalate (rule is wrong / rule needs scope adjustment) and document in build-log.md. Critical rules are not deferrable.
- **Important rule applies**: surface to user; defer-with-rationale is allowed and logged in build-log.md (matching the LINT-MOCK Important pattern).
- **Parse violations** (malformed `build-checks.md` rule, missing required field, invalid severity): fail the audit with exit code 1; fix the rule's format before continuing.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates BC-1's release date (2026-05-06) are exempt automatically. The audit returns `carry_over_exempt: true` and zero applicable rules for those.

If neither `architecture/build-checks.md` nor `~/.claude/build-checks.md` exists, the audit returns zero applicable rules. Both files are populated manually at `/reflect` Step 5b when a recurring pattern emerges across slices.

v1 surfaces rules; the human/AI builder addresses them. Auto-verification (executable check command per rule) is deferred to a v2 — the format already includes `Validation hint` so v2 can parse and run it.

#### Wiring matrix audit (WIRE-1)

Per **WIRE-1** (`methodology-changelog.md` v0.9.0), this slice's `design.md` must include a wiring matrix declaring a consumer entry point + consumer test for every new module, or an exemption with explicit rationale. Run:

```bash
$PY -m tools.wiring_matrix_audit architecture/slices/slice-NNN-<name>
```

Refusal on Important findings:
- `no-matrix`: design.md is missing the `## Wiring matrix` heading entirely
- `missing-cells`: a row has neither (consumer entry point + consumer test) nor an exemption
- `missing-rationale`: exemption present but no `rationale:` substring
- `format`: malformed table (wrong column count, missing separator, etc.)

v1 enforces format validation only. A v2 will add existence/import audits — verify entry-point files exist and grep for module imports.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates WIRE-1's release date (2026-05-06) are exempt automatically. The audit returns zero findings for those.

If the slice introduces no new modules: keep the matrix header + separator only — the audit accepts zero-row matrices as clean.

#### Mock-budget lint (LINT-MOCK-1, LINT-MOCK-2, LINT-MOCK-3)

Per **LINT-MOCK-1** (Python; v0.6.0), **LINT-MOCK-2** (TypeScript / JavaScript; v0.7.0), and **LINT-MOCK-3** (Go; v0.8.0), Python, TS/JS, and Go test files changed in this slice must pass `tools/mock_budget_lint.py`. The linter dispatches by file extension automatically:

```bash
$PY -m tools.mock_budget_lint <changed-test-files>
# Add --seam-allowlist architecture/.cross-chunk-seams (if file exists)
# Add --strict in Heavy mode (Important also blocks)
```

Supported extensions: `.py` (LINT-MOCK-1), `.ts` `.tsx` `.js` `.jsx` `.mts` `.cts` (LINT-MOCK-2), `.go` (LINT-MOCK-3).

Severity rules:
- **Critical** (target is in `architecture/.cross-chunk-seams`): blocks pre-finish; cannot be deferred. *(Critical applies to LINT-MOCK-1 and LINT-MOCK-2 only; LINT-MOCK-3 v1 enforces mock-budget without internal-mock classification — no Critical findings emitted.)*
- **Important** in Standard / Minimal mode: surface to user; allow defer with rationale recorded in `build-log.md`
- **Important** in Heavy mode: blocks pre-finish (`--strict` is mandatory)

The `architecture/.cross-chunk-seams` allowlist (if present) names targets where mocking is escalated to Critical. One target per line; lines starting with `#` are comments. The same allowlist applies to Python and TS files; format matches each language's import-target string (e.g., `src.api.receipts.upload_receipt` for Python, `./api/receipts` for TS). Go v1 doesn't yet honor the allowlist; a later slice adds import-aware boundary classification for Go.

If the slice didn't touch any Python, TS/JS, or Go test files: skip this gate (not applicable).

### Step 7: Do-not-defer enforcement

The mission brief's must-not-defer list is checked at pre-finish. Items there CANNOT be:

- Marked "TODO" and shipped
- Stubbed with placeholder values (`return None`, `// implement later`)
- Wrapped in silent try/except that hides failures
- Skipped via "we'll add this in the next slice"
- Committed with debug prints / console.logs

If you want to defer anything on the list: STOP and ask the user explicitly. Approved deferrals get logged in `build-log.md` with rationale.

### Step 7b: Update milestone.md continuously

Unlike other skills which update milestone.md at completion, `/build-slice` updates it **during execution** because build is the longest phase and most likely to be interrupted by session death.

Updates during build:

- At plan approval: `stage: build`, `next-action: task 1 (<specific>)`, "Current focus" = first task
- After EACH task completes: update "Progress" counter (`- [ ] /build-slice — in progress: N/M tasks complete`), update "Current work" and "Files being edited", update "Next immediate step"
- At mid-slice smoke gate: record pass/fail in "Current focus"
- At pre-finish gate: check the build-slice box, set `next-action: run /validate-slice`

**Preserve the CRP-1 escape-hatch key (per ADR-024).** If `milestone.md` frontmatter carries a `critique-review-skip:` key, the continuous rewrite MUST preserve it verbatim. It is a deliberate per-slice skip record the Step 6 CRP-1 defense-in-depth re-run reads; dropping it would false-refuse a legitimately escape-hatched build. Treat `critique-review-skip:` like `critic-required:` / `risk-tier:` — a frontmatter field that survives every rewrite, never a regenerated-from-template field.

**Critical for session resume**: if session dies mid-build, `milestone.md` tells Claude (or the user) EXACTLY where to pick up: task number, files being edited, specific next step. Don't skimp on these fields.

### Step 7c: Append events to build-log.md (flight recorder)

`milestone.md` is the phase checkpoint ("where am I"). `build-log.md`'s `## Events` section is the append-only flight recorder ("what just happened"). They're complementary: milestone records phase transitions; events capture the finer-grained activity between transitions where tool failures and session deaths usually strike.

**Write a one-line event BEFORE any tool call that could fail and erase in-memory context.** Tool failures (corrupted binaries, parser errors, network drops) can wipe the conversation, but committed files persist.

**When to append**:
- **Before** any tool call that returns binary or large parseable output (screenshots, image reads, web fetches that may include images, large file reads). Record the *intent* and any *pending finding* first.
- **After** significant build/test commands complete (PASS / FAIL with brief evidence).
- **When you discover a finding** mid-build (UI bug, surprising behavior, edge case). Record the finding **before** doing anything else with it — including taking a screenshot.
- **On errors** you intend to investigate (preserves the cause if the investigation tool itself fails).

**Format**: `<YYYY-MM-DD HH:MM> <CATEGORY>: <one-line description>` where CATEGORY ∈ `BUILD`, `TEST`, `SMOKE`, `FINDING`, `ERROR`, `DEFERRAL`, `DEVIATION`.

**Examples**:

- `2026-05-03 14:25 BUILD: :app:assembleDebug PASS`
- `2026-05-03 14:30 SMOKE: mid-slice run on Pixel 7`
- `2026-05-03 14:32 FINDING: version footer half-hidden by nav bar — screenshot pending`
- `2026-05-03 14:33 ERROR: screenshot read failed (binary corruption); finding still valid via manual inspection`

**Canonical `BRANCH=skip` sub-shape** (per **BRANCH-1**, `methodology-changelog.md` v0.35.0 sub-mode (a) — narrows the empirically-permissive parent DEVIATION convention for audit-quality): when documenting a deliberate skip of BRANCH-1's branch-create discipline, the DEVIATION line MUST conform to this exact shape: `<YYYY-MM-DD HH:MM> DEVIATION: BRANCH=skip — rationale: <text>` (HH:MM required; `rationale:` token required; text is non-empty). `tools/branch_workflow_audit.py` escape-hatch grep accepts only this shape via the regex `^- \d{4}-\d{2}-\d{2} \d{2}:\d{2} DEVIATION: BRANCH=skip\b.+rationale: .+`. Example: `2026-05-14 20:14 DEVIATION: BRANCH=skip — rationale: trivial 1-line typo fix per CLAUDE.md hard-rule exception`.

Keep entries to one line each. Detailed evidence (full command output, stack traces, screenshot paths) goes in the Summary section at slice end. The events section is the trace; the summary is the report.

`/status` reads the tail of this section on resume to reconstruct recent activity — durable next-action signal that survives `milestone.md` staleness.

### Step 8: Write `architecture/slices/slice-NNN-<name>/build-log.md`

```markdown
# Build log: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Result**: SHIPPED | SHIPPED-WITH-DEFERRALS | NOT-SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-03 14:25 BUILD: :app:assembleDebug PASS
- 2026-05-03 14:30 SMOKE: mid-slice run on Pixel 7
- 2026-05-03 14:32 FINDING: version footer half-hidden by nav bar
- 2026-05-03 14:33 ERROR: screenshot read failed (binary corruption); finding still valid via manual inspection

## Summary (filled at slice end)

### Plan executed
<the approved plan, with status per task>

### Mid-slice smoke gate
**Result**: PASS | FAIL
**Evidence**: <command + output>
<if FAIL: what was diagnosed and how it was fixed>

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md
- [x] Must-not-defer addressed
- [x] Drift-check pass
- [x] Smoke regression check pass
- [x] No debug code

### Deferrals (if any)
- <item> — reason: <why> — user-approved: <yes/no> — followup: <next slice / backlog>

### Design deviations (if any)
- <where design.md said X, code does Y because Z>
- <updated in design.md? yes/no>

### Files changed
- <list of source files modified>
```

## Critical rules

- ENTER PLAN MODE FIRST. Don't start editing without a user-approved plan.
- USE the Read / Glob / Grep tools to understand actual code BEFORE planning.
- DO NOT skip the mid-slice smoke gate. Catches "builds but doesn't work" early.
- DO NOT bypass the pre-finish gate. If something can't pass, the slice isn't done.
- DO NOT silently defer must-not-defer items. Ask explicitly.
- APPEND TO build-log.md events BEFORE risky tool calls (screenshots, image reads, large/binary outputs). Tool failures erase in-memory context; committed files persist. See Step 7c.
- IF design is wrong: STOP and surface, don't silently "make it work."

## When the design is wrong mid-build

This happens. Procedure:

1. STOP execution immediately
2. Write what you discovered (in conversation, not as a file yet)
3. Ask: "Design says X. Code says Y. Revise design, or proceed with documented deviation?"
4. If revise: stop the slice, run `/design-slice` updates, re-run `/critique` for the changed parts, then resume
5. If deviate: log the deviation in build-log.md and continue

## Heavy mode adjustment

In Heavy mode:
- Test coverage report at pre-finish (compliance trail)
- Sign-off field in build-log.md (human reviewer)
- Audit-grade commit messages: reference slice + ADRs

## The brief vs plan mode split

Persistent (mission brief, lives across sessions):
- Acceptance criteria
- Must-not-defer list
- Verification commands
- Vault/contract refs

Session (plan mode, mutable):
- Exact files to touch
- Task sequence
- Code-aware specifics

Brief carries discipline. Plan mode carries groundedness. This avoids the "500-line sprint file written against stale assumptions" failure mode.

## Next step

`/validate-slice` — reality check against real device / user / data.

## Pipeline position

- **predecessor**: `/critique` (post-TRI-1, on CLEAN/NEEDS-FIXES)
- **successor**: `/validate-slice`
- **auto-advance**: true
- **on-clean-completion**: once the pre-finish gate fully passes (all ACs, must-not-defer, drift-check, all Step 6 audits incl. PCA-1) and build-log.md is written, invoke `/validate-slice` via the Skill tool without waiting for the user.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Plan-mode approval (Step 3 / ExitPlanMode) — HALT for explicit user plan sign-off before any code edits.
  - Mid-slice smoke-gate failure (Step 5) — HALT, STOP, diagnose; do NOT auto-advance on a broken base.
  - Design-is-wrong mid-build — HALT and surface ("design says X, code says Y; revise or deviate?").

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
