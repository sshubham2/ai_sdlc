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

If any gate fails: don't declare done. Fix or escalate.

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
