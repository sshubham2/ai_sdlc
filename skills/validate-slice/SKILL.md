---
name: validate-slice
description: "AI SDLC pipeline. Reality check the current slice — real device, real user, real data. NOT just 'tests pass'. Per-criterion PASS/FAIL with evidence. Classifies failures (implementation bug / spec gap / reality surprise). Use after /build-slice. Trigger phrases: '/validate-slice', 'validate this slice', 'reality check the slice', 'check slice on real device'. Per-slice continuous validation, not a terminal full-codebase audit."
user_invokable: true
---

# /validate-slice — Reality Check

You are validating the current slice on a real environment. Tests passing is not enough — real device, real user, real data.

## Where this fits

Runs after `/build-slice` completes its pre-finish gate. Output feeds `/reflect`.

## Two phases

1. **This slice's acceptance criteria** — real-device / real-user / real-data checks (this skill's traditional job)
2. **Shippability catalog regression check** — run every past slice's critical-path test from `architecture/shippability.md` to catch regressions introduced by THIS slice breaking past work

Both must pass before the slice is considered validated.

## Why this matters

Tests can pass while the feature doesn't work:
- Mocks return what tests expect, not what the real API does
- Simulated actors don't catch UX issues
- Single-device tests don't validate multi-device features
- Synthetic data doesn't surface real-data edge cases (HEIC files, EXIF orientation, weird unicode)

This step closes that gap, per slice.

## Prerequisite check

- Find active slice folder
- Read `mission-brief.md` (acceptance criteria + verification plan)
- Read `build-log.md` (what was actually built; helps interpret deviations)
- If `build-log.md` is missing or shows NOT-SHIPPED: stop, the slice isn't ready

## Your task

### Step 1: For each acceptance criterion, run the real-world check

Read the verification plan from mission-brief.md. For each AC, execute the check:

- **Backend endpoint**: hit it with a real client (curl, real test harness, Postman). Inspect response. Check DB state.
- **Frontend page**: open in a real browser (or local dev server). Perform the user action. Observe.
- **Mobile feature**: install on a real device. For multi-device features: install on TWO devices.
- **CLI / script**: run on real sample data (not synthetic test data). Inspect output.
- **ML inference**: evaluate on held-out data (not training data).

### Step 2: Capture evidence per criterion

Each AC's validation MUST record what was actually checked:

- Command run + actual output (paste it)
- Screenshot if UI (note where saved)
- Log excerpts if backend
- Manual steps + observation if observation-based

"It worked" without evidence doesn't count. If you cannot produce evidence, the AC isn't validated — even if you trust the test suite.

### Step 3: Classify results

For each criterion: **PASS** | **FAIL** | **PARTIAL**

For FAIL or PARTIAL, classify the cause:

- **Implementation bug**: code wrong, spec right → fix code, re-validate, then `/reflect`
- **Spec gap**: spec incomplete, can't actually deliver → don't fix yet; `/reflect` formally captures it
- **Reality surprise**: neither predicted (e.g., HEIC EXIF issue) → log immediately to risk-register, `/reflect`

### Step 4: Multi-instance validation (if applicable)

For features involving:
- >1 user (sharing, collaboration, permissions across users)
- >1 device (sync, push, real-time)
- >1 account (cross-account flows)

Validation REQUIRES testing on multiple instances simultaneously. Single-instance passing is NOT proof. The Google Drive `drive.file` incident is the canonical example of why.

### Step 5: Write `architecture/slices/slice-NNN-<name>/validation.md`

```markdown
# Validation: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Result**: PASS | PARTIAL | FAIL

## Per-criterion results

### AC1: <criterion text>
- **Status**: PASS | FAIL | PARTIAL
- **Evidence**: <command + output, screenshot ref, log excerpt>
- **Notes**: <observations, edge cases noticed>

### AC2: <criterion text>
- **Status**: FAIL
- **Cause**: implementation bug | spec gap | reality surprise
- **Evidence**: <what failed, with output>
- **Action**: <fix code now | flag for reflect | log to risk-register>

(repeat per AC)

## Multi-instance validation
**Required?**: yes / no
**Result**: PASS | FAIL | not-applicable
**Evidence**: <devices/users/accounts used; what was checked>

## Reality surprises
- <thing not predicted by design or critique>
- <impact on next slice>
```

### Step 5b: Layered safety checks (VAL-1)

Per **VAL-1** (`methodology-changelog.md` v0.14.0), `/validate-slice` runs two defensive layers against the slice's changed files BEFORE the shippability catalog. These layers catch defect classes that real-environment validation tends to miss: committed credentials and AI-hallucinated dependencies.

```bash
$PY -m tools.validate_slice_layers \
  --slice architecture/slices/slice-NNN-<name> \
  --changed-files <list of files this slice changed>
```

**Layer A — Credential scan (Critical, blocks)**
Static regex patterns for AWS access keys, GitHub PATs (classic + fine-grained + bot tokens), Slack tokens, JWTs, PEM private keys, Anthropic / OpenAI API keys, and generic `api_key = "..."` literals. Each detected secret is a Critical finding that **cannot be deferred** — committed credentials are immediately exploitable. False positives (test fixtures, public-docs examples) are silenced via `architecture/.secrets-allowlist` (one regex per line; `#` comments).

**Layer B — Dependency hallucination check (Important, surfaces)**
Python `ast`-parses every changed `.py` file and resolves each top-level import against the project's declared deps from `pyproject.toml` (`[project.dependencies]`, `[project.optional-dependencies]`, `[tool.poetry.dependencies]`) and `requirements.txt`. Stdlib imports (per `sys.stdlib_module_names`), relative imports (`from . import X`), and a small known-aliases table (`yaml`->`pyyaml`, `bs4`->`beautifulsoup4`, `PIL`->`pillow`, `cv2`->`opencv-python`, etc.) resolve cleanly. Anything else is an Important `hallucinated-import` finding — possible AI hallucination, or a real package that the project simply forgot to declare. Surface to user; defer-with-rationale allowed (consistent with the LINT-MOCK Important pattern).

Refusal semantics:
- Any Critical finding (Layer A) -> refuse `/reflect`. Either remove the secret + rotate it, or add a precise allowlist regex with a `#` comment explaining the suppression.
- Any Important finding (Layer B) -> surface to user; allowed to proceed with documented rationale in `validation.md` (typical resolution: add the package to `pyproject.toml` and re-run, OR remove the import).

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt automatically; archive scans use `--no-carry-over`.

Skip flags: `--skip-secrets` (when a project runs its own scanner), `--skip-deps` (when a project runs its own dep linter). Both default off.

v1 limitations: Layer B is Python-only; TS/JS dep hallucination is deferred to v2 (needs npm package.json parsing + scoped-package handling). Layer A's pattern set is a starting point, not exhaustive — projects with vendor-specific secret formats can extend it via project-local copies.

### Step 5c: Walking-skeleton layers audit (WS-1)

Per **WS-1** (`methodology-changelog.md` v0.15.0), when this slice's `mission-brief.md` declares `**Walking-skeleton**: true`, every architectural layer in the `## Architectural layers exercised` table must be EXERCISED at runtime by validation. Run:

```bash
$PY -m tools.walking_skeleton_audit architecture/slices/slice-NNN-<name> --strict-pre-finish
```

The walking-skeleton discipline (Cockburn): the smallest possible end-to-end implementation that exercises every architectural layer. Real features layer onto the proven foundation. The audit forces explicit enumeration of the layers and confirms each was actually reached during validation — not just unit-tested in isolation.

Refusal semantics:
- `missing-section`: brief declares walking-skeleton true but has no `## Architectural layers exercised` section
- `empty-table` / `format` / `missing-cells`: table is malformed, or has zero data rows (a walking-skeleton with no layers is meaningless — that's a standard slice)
- `missing-verification`: a row's Verification cell is empty
- `invalid-status`: status outside `{PENDING, EXERCISED}`
- `non-exercised-pre-finish`: a layer's status is PENDING (only emitted with `--strict-pre-finish`)

Default-off semantics: when the brief lacks the `**Walking-skeleton**:` field or sets it to `false`, the audit returns clean and the gate passes silently. WS-1 is opt-in per slice.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt automatically.

### Step 5d: Exploratory-charter audit (ETC-1)

Per **ETC-1** (`methodology-changelog.md` v0.16.0), when this slice's `mission-brief.md` declares `**Exploratory-charter**: true`, every charter in the `## Exploratory test charter` table must be COMPLETED (with findings recorded) or DEFERRED (with rationale). Run:

```bash
$PY -m tools.exploratory_charter_audit architecture/slices/slice-NNN-<name> --strict-pre-finish
```

Charter-based exploratory testing (Bach / Kaner / Hendrickson): each charter is a timeboxed mission ("Explore X using Y to find Z"); the tester runs the session freely and captures what surfaces. Distinct from scripted testing — surfaces what's NOT in the AC, unstated assumptions, edge cases the design didn't predict.

Refusal semantics:
- `missing-section`: brief declares Exploratory-charter true but has no `## Exploratory test charter` section
- `empty-table` / `format` / `missing-cells`: table is malformed or has zero rows
- `missing-mission`: a row has an empty Mission cell (a charter without a mission is undirected exploration)
- `invalid-status`: status outside `{PENDING, IN-PROGRESS, COMPLETED, DEFERRED}`
- `missing-findings`: a COMPLETED or DEFERRED row has empty Findings (the discipline IS capturing what surfaced; bare COMPLETED is performance theater, bare DEFERRED is hand-waving)
- `non-final-pre-finish`: a row's status is PENDING or IN-PROGRESS (only emitted with `--strict-pre-finish`); COMPLETED and DEFERRED are both accepted as "settled"

Default-off semantics: when the brief lacks the `**Exploratory-charter**:` field or sets it to `false`, the audit returns clean and the gate passes silently. ETC-1 is opt-in per slice.

NFR-1 carry-over: slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt automatically.

### Step 5.5: Run the shippability catalog (regression check)

Before deciding next action, verify no past slice was silently broken by this one:

1. Read `architecture/shippability.md` — the catalog of critical-path tests from every past slice
2. If the file doesn't exist (first slice, catalog empty): skip this step; `/reflect` will create the catalog
3. Run each entry's **Command** column — execute it from project root
4. Record PASS / FAIL per entry

If any entry FAILS:
- The current slice broke something a past slice established
- Append to `validation.md` under a new "Shippability regressions" section — list which tests failed, with their output
- **This blocks `/reflect`**. Either fix the regression or get explicit user approval to defer (with rationale)

Example output:

```
Shippability catalog run: 14 tests, 13 PASS, 1 FAIL

FAILED:
  #3 slice-008-enable-sync: "2-device sync converges within 10s"
    Command: `bash tests/multi-device/sync_converge.sh`
    Output: timeout after 30s (expected <10s)
    Likely cause: this slice's async refactor changed delivery guarantees

Cannot proceed to /reflect. Fix the regression, OR get user approval to defer the fix to a new slice.
```

Target runtime: full catalog < 2 min. If it bloats past that, `/reduce` can propose trimming redundant entries.

### Step 6: Decide next action

- All PASS (current ACs + shippability), no surprises → `/reflect`
- Implementation bug on current ACs: fix the code, re-validate, then `/reflect`
- Spec gap or reality surprise: don't fix during validate; let `/reflect` capture and decide whether next slice addresses
- Shippability regression: fix OR user-approved deferral (logged in validation.md); don't silently skip

### Step 7: Update milestone.md

Update `architecture/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: validate`, `updated: <today>`, `next-action: run /reflect` (or `fix regression then re-run /validate-slice` if shippability caught one)
- Check progress box: `- [x] /validate-slice — <date> — <PASS | PARTIAL | FAIL>`
- Update phase artifact status: `validation.md — <result>`
- "Current focus": validation summary (N/M ACs passed, shippability status)
- If shippability regression caught: capture in "Current focus" with the specific test that failed

## Critical rules

- USE REAL ENVIRONMENTS. No mocks, no simulators-only when real is possible.
- CAPTURE EVIDENCE per criterion. "It worked" doesn't count.
- MULTI-INSTANCE for multi-user/device features. ALWAYS.
- DO NOT auto-fix spec gaps during validation. Let `/reflect` formalize them.
- DO NOT pass a partial criterion as PASS. Partial is partial.
- DO NOT skip a criterion because "it's covered by the test suite." Tests pass != feature works.

## When real validation isn't possible (early projects)

Some slices have no deployment target yet. Acceptable substitutes:

- Run locally with real sample data (not synthetic)
- Demonstrate in user-facing form (terminal, screenshot, recording)
- Manual user observation if UX-critical

NOT acceptable: "we'll really test this later." If you can't validate now, the slice was either too early or missing a testable acceptance criterion.

## Heavy mode adjustment

In Heavy mode, validation produces a compliance-grade record:
- Reproducible test commands (anyone can re-run)
- Timestamped evidence
- Sign-off field for QA / compliance reviewer
- Cross-reference to test-plan IDs

## Failure handling

- **Implementation bug**: fix code → re-run validation for that AC → if pass, proceed to `/reflect`
- **Spec gap**: log in validation.md as cause; let `/reflect` capture; next slice incorporates
- **Reality surprise**: add to `architecture/risk-register.md` immediately (don't wait); `/reflect` may trigger a follow-up slice

## Next step

`/reflect` — capture what reality taught you.
