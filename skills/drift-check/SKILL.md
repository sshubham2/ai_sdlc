---
name: drift-check
description: "AI SDLC maintenance. Compare vault claims against code reality, flag divergence. Designed to run as a pre-commit hook OR on-demand audit. Catches spec rot before it compounds. Use as pre-commit hook (auto), before starting a new slice, or when you suspect drift after external changes. Trigger phrases: '/drift-check', 'check for drift', 'vault sync check', 'is the vault still accurate', 'audit vault vs code'."
user_invokable: true
argument-hint: [--fast] [--resolve] [path]
---

# /drift-check — Vault vs Code Sync Audit

You compare vault claims against code reality and flag divergence. Designed to run quickly enough for pre-commit hooks (`--fast`) and thoroughly enough for on-demand audits (no flag).

## Where this fits

- Pre-commit hook (auto, fast mode) — installed by `/triage` in Standard/Heavy modes
- Pre-finish gate of `/build-slice` — invoked automatically
- On-demand: before starting a new slice, after external changes, when suspicious

## Why this matters

Vault rot is the biggest failure mode of spec-driven SDLC. A stale vault is worse than no vault — it actively misleads. This skill catches drift early when fixing is cheap.

## Argument modes

- `/drift-check` — full audit, writes report
- `/drift-check --fast` — pre-commit mode, only changed files, target <2s
- `/drift-check --resolve` — interactive walk-through of findings
- `/drift-check <path>` — scope to one component/contract folder

## Your task

### Step 1: Detect mode

- If `--fast`: only check files changed since last commit (use `git diff --name-only HEAD`)
- If `--resolve`: load existing drift findings, walk user through each
- If path: scope to that folder
- Default: full audit

### Step 2: Load vault state

The thin vault has a small drift surface. Read only:

- `architecture/decisions/*.md` — chosen tech, libraries, approaches (status: accepted)
- `architecture/risk-register.md` — risks claimed retired
- `architecture/slices/*/design.md` — these are ACTIVE slices only (convention: completed slices move to `slices/archive/` via `/reflect`)
- `architecture/slices/*/mission-brief.md` — active slice must-not-defer items

Skip files that don't exist in thin vault: `components/`, `contracts/`, `schemas/`, `actors/`, `test-plan/`, `frontend/` (these are derived from code, can't drift).

Skip `slices/archive/*` entirely — those slices shipped, their claims are historical artifacts, not live assertions about current code. `slices/_index.md` is the lookup layer; it's metadata, also skipped.

If graphify is available, query the code graph to compare ADR claims against actual dependencies and structure.

**Heavy mode**: if `components/`, `contracts/`, `schemas/`, etc. exist (Heavy mode keeps them), include them in the audit.

### Step 3: Check each vault claim against code (graphify-first)

Use `$PY -m graphify query` before file reads — faster and more precise.

For thin vault, the checks are:

| Claim | Verification (graphify-first) |
|-------|------------------------------|
| ADR chose library `pyheif` (status: accepted) | `$PY -m graphify query "is pyheif in dependencies?"` OR `grep pyheif pyproject.toml` |
| ADR chose framework `FastAPI` | `$PY -m graphify query "what framework is imported?"` OR check imports |
| Slice design references `src/api/receipts.py` | `$PY -m graphify reachable --from="src/api/receipts.py"` (file exists in graph? has neighbors?) |
| Risk R3 marked "RETIRED" | Read the spike file directly: `cat architecture/spikes/spike-003*.md` |
| Mission brief must-not-defer item "auth on POST /receipts" | `$PY -m graphify query "does POST /receipts have auth?"` OR inspect route handler |

For each mismatch: capture file, line, vault claim, code reality.

Graph-based checks are sub-second even on large codebases. Direct file reads are a fallback when graphify isn't available.

**What's NOT checked anymore** (because not in thin vault): per-component file existence, per-contract endpoint signatures, per-schema field matches. If you find yourself wanting these checks, you may be in a Heavy-mode project, OR the thin vault is missing something it shouldn't be.

### Step 4: Classify findings

Three categories:

- **DRIFT (blocker)** — vault says X, code does Y. Pick one to update.
- **UNSPECIFIED CODE (major)** — code does X, vault doesn't mention. Either scope creep or missing ADR.
- **STALE CLAIM (major)** — vault mentions removed feature. Delete or supersede.

### Step 5: Output

#### `--fast` mode (pre-commit)

stdout to terminal. Block commit if blockers exist. Format:

```
DRIFT BLOCKING COMMIT:

[BLOCKER] contracts/receipt-api.md says POST /receipts returns 201
          but src/api/receipts.py returns 200
          Resolve: run /drift-check --resolve OR fix code OR update contract

[WARN]    components/notification.md mentions sendgrid
          but pyproject.toml no longer depends on sendgrid (removed in slice-008)
          Resolve: update component doc or note rationale in ADR

To bypass (NOT RECOMMENDED): git commit --no-verify
```

Exit code: 0 if clean, 1 if blockers, 2 if warns only.

#### Full mode (audit)

Write `architecture/drift-log.md` (append, not overwrite):

```markdown
## Audit <YYYY-MM-DD HH:MM>

**Trigger**: <pre-commit | manual | sliceNN pre-finish gate>
**Scope**: <full | path>
**Findings**: <N blockers, M majors>

### Blockers
- <vault file>:<line> says <X>; code <file>:<line> does <Y>
- ...

### Majors
- ...

### Resolutions
- <finding ID>: <update vault | fix code | accept drift with rationale>
```

#### `--resolve` mode (interactive)

For each finding, prompt user:

```
Finding: contracts/receipt-api.md says response is 201, code returns 200.

Choose:
  [1] Update vault (code is correct) — edit contract to say 200
  [2] Fix code (vault is correct) — becomes a new mini-slice
  [3] Accept drift (intentional) — log rationale in drift-log.md
```

### Step 6: Resolution actions

For each option:

- **Update vault**: edit the relevant file inline; commit with code change
- **Fix code**: create a new slice via `/slice "fix drift in <area>"` (do not silently fix; track it)
- **Accept drift**: append to drift-log with rationale + next-action (e.g., "intentional during sliceNN refactor; will reconcile in slice NN+1")

## Critical rules

- DO NOT silently fix code drift. Even small fixes go through `/slice` for traceability.
- DO NOT bypass via `git commit --no-verify` casually. If you must bypass, that's a signal: the hook is wrong, OR discipline is breaking down. Don't accept silently.
- IN `--fast` MODE: target <2 seconds. Skip graphify rebuild, skip deep schema diff. Just file existence + endpoint signatures.
- IN FULL MODE: deep checks acceptable, may take 30s+.
- "ACCEPT DRIFT" entries should have follow-ups. Periodic audits of drift-log catch accumulation.

## Setup as pre-commit hook

`/triage` in Standard/Heavy modes installs this. Manually:

```bash
# .git/hooks/pre-commit (or husky/lint-staged equivalent)
#!/bin/sh
exec /path/to/drift-check --fast
```

In Minimal mode: skipped by default; user can enable manually.

## Failure modes to watch

- **Hook gets disabled**: it's too slow or too noisy. Fix the hook, don't accept drift.
- **False positives**: rename in code without rename in vault. Solution: add `implements-in:` frontmatter to component files (`implements-in: src/api/receipts.py`).
- **Drift accepted too freely**: every "accept drift" should have a planned reconciliation. Periodic audit catches accumulation.

## Performance targets

Thin vault makes this much faster than original drift checks:

- `--fast`: <1 second for typical commits (small vault surface)
- Full audit: <10 seconds for typical thin vault
- Heavy-mode (full vault): <30 seconds
- If exceeded: profile, optimize. Slow checks get bypassed.

## /sync vs /drift-check

`/drift-check` is **detect-only** and works in **all modes**. It's the pre-commit hook (fast, safe, no side effects).

`/sync` is **bidirectional** (also regenerates code-derived vault files) and **Heavy mode only**. It runs periodically (every 5-10 slices) to reconcile the comprehensive Heavy vault with code reality.

In Standard / Minimal mode (thin vault): `/drift-check` is sufficient. There's nothing to bidirectionally sync — the vault is thin.
In Heavy mode: use `/drift-check` for fast pre-commit checks; use `/sync` periodically for deeper reconciliation including regeneration of components/contracts/schemas from code.

## Next step

- Clean → continue (commit, or proceed with slice)
- Blockers → resolve via `--resolve` mode, or fix manually
- Heavy drift → `/slice` targeted at cleanup
