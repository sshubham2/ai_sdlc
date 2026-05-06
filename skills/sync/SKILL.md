---
name: sync
description: "Heavy mode only. Bidirectional vault-code reconciliation — regenerates code-derived vault files (components from AST, contracts from OpenAPI/Pydantic/type defs, schemas from data models) AND detects vault claims that don't match code. More aggressive than /drift-check (which is detect-only). Use periodically in Heavy mode (every 5-10 slices), or after major code changes (refactors, dependency swaps). Trigger phrases: '/sync', 'sync vault and code', 'regenerate component docs', 'reconcile architecture'. Standard/Minimal mode users should use /drift-check instead — there's nothing to regenerate when vault is thin."
user_invokable: true
argument-hint: [--dry-run] [--regen-only] [--check-only] [path]
---

# /sync — On-Demand Code-Derived Vault Generator (Heavy Mode)

You generate code-derived vault artifacts (components, contracts, schemas) fresh from current code, and detect drift on human-authored files. Heavy mode only.

**Reframe from prior design**: previously `/sync` was "bidirectional reconciliation" assuming components/contracts/schemas already existed in the vault. In the current design, those files DO NOT EXIST between sync runs — `/heavy-architect` no longer pre-generates them. `/sync` is the **only source** of those files. You run it on-demand (before audit, before release, etc.) — it generates fresh. After the audit, you can delete them or leave them; they'll be regenerated next time.

This is the honest implementation of "code is the truth for WHAT." Code-derived views exist transiently, as projections, not as persistent artifacts prone to drift.

Two jobs:

1. **Generate code-derived artifacts on-demand**: produce `components/*.md`, `contracts/*.md`, `schemas/*.md` from code AST / OpenAPI / type definitions
2. **Drift check on human-authored files**: ADRs reference libraries that still exist, threat-model entries match real attack surface, cost-estimation matches deployed services, etc.

Standard / Minimal mode: `/sync` is not used. `/drift-check` handles drift detection there (much smaller surface).

## Where this fits

Maintenance skill in Heavy mode. Run:

- Every 5-10 slices to reconcile accumulated changes
- After major refactors or dependency swaps
- Before a release / audit cycle
- When `/drift-check` reports many findings (sign that comprehensive vault has drifted significantly)

## Argument modes

- `/sync` — full bidirectional sync (default)
- `/sync --dry-run` — show what would change without writing
- `/sync --regen-only` — only regenerate code-derived files; skip drift detection
- `/sync --check-only` — only detect drift; skip regeneration (equivalent to `/drift-check` deep mode)
- `/sync <path>` — scope to one component / contract folder

## Prerequisite check

- Read `architecture/triage.md` — confirm `mode: Heavy`
- If Standard or Minimal: STOP, suggest `/drift-check` instead
- Confirm comprehensive vault exists (`components/`, `contracts/`, `schemas/` directories)
- If `/heavy-architect` hasn't run: STOP, run that first

## Your task

### Step 1: Build code graph

Use graphify to build a fresh code graph:

```bash
$PY -m graphify code <src-root>                 # AST + INFERRED cross-file edges
```

This gives you AST-level structure: classes, functions, endpoints, imports, types. (Note: the upstream slash-command form supports a `--mode deep` flag that adds rationale-comment extraction; the CLI does not. For Heavy-mode rebuilds, run `/graphify <path> --mode deep` from inside Claude Code chat if you need the deeper extraction; otherwise the standard `code` build is sufficient for sync purposes.)

If `$PY -m graphify.watch <src-root>` is running in another terminal: graph rebuilds on file changes automatically; skip this step.

### Step 2: Code → Vault regeneration

For each code-derived vault file, check if regeneration is needed:

#### Components

For each `components/<name>.md`:

- Find the corresponding code module (look at `implements-in:` frontmatter, or match by name)
- Re-derive: public surface (exported functions/classes), dependencies (imports), data structures
- Compare with current vault content
- If different: regenerate the public surface section, dependencies section, data structures section
- PRESERVE: responsibility description, failure modes, threat model entries, cost notes (these are human-authored, not derived)

#### Contracts

For REST contracts:

- If the project uses FastAPI / OpenAPI: parse `openapi.json` (or generate from running app)
- If Express / Fastify with typed schemas: parse route definitions
- Regenerate endpoint specs (method, path, request schema, response schema, status codes)
- PRESERVE: auth model commentary, idempotency notes, rate limit decisions, versioning strategy

For event contracts:

- Find publisher / subscriber code (annotation-based or convention-based)
- Regenerate event name, payload schema, delivery guarantee
- PRESERVE: ordering decisions, retry strategy, dead-letter handling commentary

#### Schemas

- Find data model code (SQLAlchemy / Prisma / Pydantic / Drizzle etc.)
- Regenerate field list, types, constraints
- PRESERVE: state transition diagrams (Mermaid), entity lifecycle commentary

### Step 3: Vault → Code drift detection

For non-derived vault content, run drift checks:

- ADR-claimed library still in dependencies?
- ADR-chosen approach still reflected in code architecture?
- Risk register's "retired" claims still valid?
- Slice design references match real file paths?
- Threat model components still exist in code?
- Cost estimation tied to real services in deployment?

For each mismatch: capture file, claim, code reality.

### Step 4: Present diff

Show the user what would change. Group by file. Show:

- **Regenerated content** (auto-derived; safe to apply)
- **Detected drift** (vault claims that don't match; need decision)
- **Preserved content** (human-authored sections kept as-is)

Example output:

```
SYNC PLAN

Regenerate (auto, safe):
  components/notification.md — public surface changed (3 new functions added)
  contracts/notification-api.md — POST /notify response schema changed (added 'queued_at' field)
  schemas/user.md — added field 'last_login_at'

Drift detected (need decision):
  components/storage-service.md — claims sync upload, code is now async (slice-008 added queue)
  ADR-008 — chose sendgrid; pyproject.toml has resend (when did this change?)
  risk-register R3 — marked RETIRED in slice-002, but spike-002 only validated simple case

Preserved (human-authored):
  components/notification.md — responsibility, failure modes, threat entries
  contracts/notification-api.md — auth model, idempotency notes
```

### Step 5: Execute (unless --dry-run)

For regenerated content: apply automatically.

For drift findings: walk user through each (like `/drift-check --resolve`). Three options per finding:

1. **Update vault** (code is right)
2. **Fix code** (vault is right; spawns a fix slice)
3. **Accept drift** (intentional; log to drift-log.md with rationale + reconciliation plan)

### Step 6: Update vault graph

Rebuild $PY -m graphify vault graph after sync:

```bash
$PY -m graphify vault architecture
```

### Step 7: Write `architecture/sync-log.md`

Append a sync record:

```markdown
## Sync <YYYY-MM-DD HH:MM>

**Mode**: full | --dry-run | --regen-only | --check-only
**Files regenerated**: <count>
**Drift findings**: <count>
**User-resolved**: <count> (vault updated: N, code fixed: M, drift accepted: K)

### Regenerated
- components/<name>.md — <what section>
- contracts/<name>.md — <what section>

### Drift resolved
- <finding> — <action taken>
```

## What this skill regenerates vs preserves

| Section | Source | Action |
|---------|--------|--------|
| Component public surface | Code AST | Regenerate |
| Component dependencies | Code imports | Regenerate |
| Component responsibility | Human | Preserve |
| Component failure modes | Human | Preserve |
| Contract endpoints / events | OpenAPI / annotations | Regenerate |
| Contract auth model | Human | Preserve |
| Contract idempotency notes | Human | Preserve |
| Schema field list | Data model | Regenerate |
| Schema state transitions | Human | Preserve |
| ADR rationale | Human | Preserve (drift-check only) |
| Threat model | Human | Preserve (drift-check only) |
| Cost estimation | Human | Preserve (drift-check only) |

## Critical rules

- VERIFY Heavy mode first. In Standard / Minimal, this skill should not run.
- DRY-RUN by default if uncertain. Show diff, get approval.
- PRESERVE human-authored sections. Regeneration only touches derived content.
- DO NOT silently fix code drift. Drift findings need user decision.
- DO NOT auto-delete ADRs even if libraries removed — mark superseded, link new ADR.
- LOG every sync to `sync-log.md` for audit trail (Heavy mode = audit trail mandatory).
- REBUILD vault graph after — downstream skills depend on it.

## Why /sync exists separately from /drift-check

`/drift-check` is detection-only and works in all modes. It's the pre-commit hook (must be fast, must be safe).

`/sync` is bidirectional and Heavy-only. It's deeper, slower, and has write side-effects on derived content. Different tool for different job.

## Failure modes to watch

- **Over-regeneration**: if component description changes faster than code, regenerated content overwrites recent human edits. Fix: always show diff before apply (interactive mode default).
- **Under-detection**: if naming changes in code without `implements-in:` frontmatter update, sync may regenerate from wrong code. Fix: ensure component files have `implements-in:` paths.
- **Sync becomes a slice replacement**: tempting to sync after every code change. Don't — periodic (every 5-10 slices) keeps the vault aligned without becoming busy work.

## Performance targets

- Full sync (typical Heavy vault): 1-3 minutes (graphify rebuild dominates)
- `--dry-run`: same; just doesn't write
- `--regen-only`: faster (skips drift checks)
- `--check-only`: similar to `/drift-check` deep mode

## Heavy mode pipeline reminder

```
/triage (Heavy) → /discover → /risk-spike → /heavy-architect → /user-test (if B2C)
  → [per slice:] /slice → /design-slice → /critique → /build-slice → /validate-slice → /reflect
  → [every 5 slices:] /reduce
  → [periodic, here:] /sync
```

## Fork-friendly execution

Sync is the strongest fork candidate in the entire pipeline. It's Heavy-mode only, runs periodically (every 5–10 slices) or pre-audit, takes 1–3 minutes (graphify rebuild dominates), produces no user-blocking output until done, and benefits enormously from full project context (the vault, the code, all OpenAPI/Pydantic/migration files). Background execution is a clear win.

**Requires** `CLAUDE_CODE_FORK_SUBAGENT=1` (Claude Code v2.1.117+). Forks inherit the parent conversation in full, run in the background, and report when reconciliation completes.

**When to fork** (almost always, in practice):
- **Pre-audit regeneration** — fork at the start of audit prep; review components/contracts/schemas regen + drift findings when ready
- **Periodic 5–10-slice cadence** — kick off in background while user starts the next slice; reconcile when done
- **After major refactor** — fork the deep `--mode deep` graph rebuild + drift check while the user moves to other work
- **`/drift-check` reported many findings** — escalate to `/sync` in background; the user doesn't need to wait

**When NOT to fork**:
- `/sync --dry-run` for a quick "what would change?" preview that the user wants to see immediately
- `/sync --check-only` when treated as a heavier `/drift-check` and the user is at the keyboard
- `/sync <path>` scoped to one component for a tight inspection
- Fork env var not enabled — runs in main thread; sync still works, just blocks

**Invocation**:

```
/fork /sync
/fork /sync --dry-run
/fork /sync --regen-only
```

The fork inherits the project's mode (must be Heavy), the existing comprehensive vault, all ADRs, and recent slice history. The drift-resolution dialogue (Step 5 in this skill) is interactive — when the fork hits drift findings that need a user decision, it surfaces those for resolution. Auto-regenerated content applies without dialogue.

**Audit trail note**: `sync-log.md` is appended whether the run is forked or main-thread. Forked runs are flagged in the log as `**Run mode**: forked` so the audit trail captures the execution context — relevant in compliance environments where reproducibility matters.

## Next step

- Sync clean → continue with normal pipeline
- Heavy drift resolved manually → may spawn a `/slice` for code fixes
- Many drift findings → consider running `/reduce` to simplify before next sync
