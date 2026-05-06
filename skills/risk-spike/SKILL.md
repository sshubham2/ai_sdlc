---
name: risk-spike
description: "AI SDLC pipeline. Validate risky third-party API assumptions with throwaway code on real environments — BEFORE any design or architecture work. Use after /triage or /discover when HIGH-risk items exist in architecture/risk-register.md, or when /critique flags an unvalidated assumption. Trigger phrases: '/risk-spike', 'spike a risk early', 'validate assumption before design', 'run a feasibility spike'."
user_invokable: true
argument-hint: [risk-id-or-name] | all
---

# /risk-spike — Pre-Design Feasibility Spike

You are validating risky third-party API assumptions with throwaway code on a real environment. This runs EARLY in the AI SDLC pipeline — before any design — to catch scope limitations and behavioral gaps that would otherwise blow up sprints later.

## Where this fits

Runs after `/triage` or `/discover` when HIGH-risk items exist. Can also be triggered by `/critique` flagging an unvalidated assumption mid-pipeline.

A NO-GO result loops back to `/discover` (revise the assumption). GO unblocks `/slice` and `/design-slice`.

## Why this runs before design

If a critical assumption fails after design (or worse, after build), you re-do design and possibly the slices that depend on it. Spiking BEFORE design means a failed assumption revises concept/discovery instead — much cheaper to absorb.

## Prerequisite check

Read `architecture/risk-register.md`. If it doesn't exist, run `/triage` first.

## Your task

### Step 1: Identify spike targets

Without an argument: list HIGH-risk items from the risk register that haven't been spiked yet. Ask user which to spike.

With an argument: target that specific risk by ID (R1) or name match.

With `all`: queue all unspiked HIGH-risk items.

### Step 2: For each target, design a minimal test

Before writing the spike code, query the graph for prior art:

```bash
# Has this integration been spiked before in a related slice?
$PY -m graphify query "past spikes involving <library-or-api>"

# Is there existing code that already touches this area?
$PY -m graphify query "what code uses <external-dependency>?"

# Relevant external references (if /discover added any)?
$PY -m graphify query "docs or papers about <technology>"
```

This prevents re-spiking something already validated, and reveals patterns from past work.

Then run **Step 2.5: Field reconnaissance** to survey what THE WORLD knows about this technology — recent platform changes, quotas, deprecations, known failure modes. Local graph (above) covers what THIS project knows; field recon covers everything outside.

Then produce a 10-30 line throwaway test spec. The spec must specify:

- **Real runtime** — not local mock; actual platform / device / API
- **Exact scopes / permissions / credentials** — what the real flow uses
- **Expected outcome** — what success looks like, in observable terms
- **Failure signal** — what failure would look like (don't conflate "didn't run" with "failed")

For multi-device / multi-user features: REQUIRE 2+ instances. Single-instance tests don't validate sync, sharing, or collaboration.

### Step 2.5: Field reconnaissance (web survey)

**Spawn the `field-recon` subagent.** Use the Agent tool with `subagent_type: "field-recon"`. The agent runs in fresh context (web search noise stays out of the main thread) and uses `WebSearch` to survey what the WORLD currently knows about the technology — post-training-cutoff platform changes, quotas, deprecations, known failure modes. Full prompt and output contract live in `~/.claude/agents/field-recon.md`.

**Inputs to pass in your prompt to the agent**:

- **Target** — specific technology / API / platform choice + version. Be specific: `"Android 15 ForegroundService dataSync background-start"`, not just `"FGS"`.
- **Assumption under test** — one sentence of what we believe to be true.
- **Use case context** — what the project is doing. Same API can be fine for one use case and broken for another.
- **Optional priors** — pre-fetch via `$PY -m graphify query "past field-recon findings about <technology>"` and pass excerpts. Agent uses as priors, not gospel — re-queries fresh regardless. Skip this if no past slices touch this tech.

**The agent returns**:

1. **`field-recon.md` content** — write it to `architecture/spikes/spike-<name>/field-recon.md`.
2. **Recommendation block** — `suggested_action` is one of `drop` / `proceed-with-caveats` / `proceed` / `inconclusive`.

**WebSearch unavailable**: if the agent reports `Skipped — WebSearch unavailable`, write a stub `field-recon.md` containing that note and proceed to Step 3 with local prior art only. Tell the user the open-loop check didn't run.

**Asymmetric early-drop rule** (main thread decides; agent only recommends):

- **`drop`** (OFFICIAL source contradicts the assumption) → flag to user. Default action: skip Step 3, mark NO-GO with field-recon as the evidence, jump to Step 6 (update risk register). Ask the user only if there's specific reason to think the official doc is wrong/outdated.
- **`proceed-with-caveats`** → run Step 3 with field-recon as a strong prior toward NO-GO. Test design should target the specific concern the agent surfaced.
- **`proceed`** → run Step 3 as planned. **Even if findings confirm the assumption — docs lie.** Empirical test is the WHOLE POINT of the spike (this skill's origin story is the Google Drive `drive.file` scope: docs claimed it'd work, reality didn't).
- **`inconclusive`** → run Step 3 normally. Field-recon adds no definitive prior either way.

**Critical**: never `drop` on a confirmation — only on an authoritative contradiction. Asymmetry exists because docs misrepresent reality more often than they admit broken behavior.

**Gate**: if `field-recon.md` contains an authoritative contradiction (whether or not the spike was dropped), the file becomes **required reading for `/critique`** on any downstream slice touching the same technology. Note this in the spike doc's Decision section.

### Step 3: Run the spike

If the target environment is available (connected device, local server, cloud account with credentials):

- Write the throwaway code at `architecture/spikes/code/spike-<name>/`
- Execute it
- Capture output, logs, screenshots

If environment isn't available: stop and tell the user what's needed, exact setup steps. Don't fabricate results.

### Step 4: Decide GO / NO-GO / CONDITIONAL

- **GO** — assumption holds, proceed with design
- **NO-GO** — assumption fails, redesign needed before any further work
- **CONDITIONAL** — holds under specific constraints; design must respect those constraints (document them)

Be honest. Don't soft-pedal a NO-GO into a CONDITIONAL because it's inconvenient.

### Step 5: Write `architecture/spikes/spike-<name>.md`

```markdown
# Spike: <name>

**Risk**: [[risk-register#R1]]
**Date**: <YYYY-MM-DD>
**Assumption under test**: <one sentence — what we believe>

## Test environment
<what we ran on — devices, accounts, versions, scopes>

## Prior art
- **Local graph**: <relevant past spikes / existing code, or "none">
- **Field reconnaissance**: see `field-recon.md` in this folder (or "skipped — WebSearch unavailable"). Tag findings here as Verified / Refuted / Untested by this spike.

## Test
<what code or steps were executed; link to spikes/code/spike-<name>/>

## Expected outcome
<what success would look like — observable>

## Actual outcome
<what happened — observable, with evidence (logs, output, screenshots)>

## Decision
**GO** | **NO-GO** | **CONDITIONAL**

<one paragraph rationale>

## Impact
- Affects: <components, decisions, slices>
- Changes needed: <if NO-GO or CONDITIONAL>
```

### Step 6: Update risk register

Update `architecture/risk-register.md` for each spiked risk:

- GO → mark "RETIRED — spike <name> validated"
- NO-GO → mark "BLOCKING — spike <name> failed; redesign required" + flag what needs to change
- CONDITIONAL → mark "CONDITIONAL — see spike <name> for constraints"

### Step 7: Tell user what's next

- All GO → "Proceed to `/slice`" (or `/discover` if not done)
- Any NO-GO → "STOP. `/discover` needs to revise assumption X. After that, re-run `/risk-spike`."
- Any CONDITIONAL → "Proceed to `/slice` but design MUST respect constraint Y from spike <name>"

## Critical rules

- NEVER fabricate spike results. If you can't run it, say so.
- NEVER skip multi-device validation for sync/sharing/collab features.
- NEVER soften a NO-GO. Redesign is cheaper than 8 wasted sprints.
- NEVER reuse spike code in production. It's throwaway. Mark it clearly.
- For OAuth scopes especially: test with TWO different accounts on the actual scope claimed. Most scope failures show up only there.

## When to spike (default triggers)

- OAuth scopes or cross-account data access
- Payment gateways (real sandbox, not mocked)
- Push notifications (delivery, not mocked)
- Runtime permissions (iOS/Android)
- Multi-device or collaboration features
- Any API where docs claim X but you've never personally seen it work
- Any "we'll figure that out later" assumption that affects expensive decisions

## Origin

Born from a real failure: an Expense Tracker project built 8 sprints around Google Drive `drive.file` scope, only to discover on first two-device test that the scope doesn't allow reading files uploaded by another user's app instance. A 30-minute spike at design time would have caught this.

## Fork-friendly execution

Spikes are a strong fork candidate. They need full project context (libraries, credentials, conventions) but are isolated work that benefits from running in the background while the user keeps moving.

**Requires** `CLAUDE_CODE_FORK_SUBAGENT=1` (Claude Code v2.1.117+). Forks inherit the parent conversation in full, run in the background, and report back when done.

**When to fork**:
- **Parallel risk validation** — fire `/fork /risk-spike R1`, `/fork /risk-spike R2`, `/fork /risk-spike R3` in one turn; spike all HIGH risks concurrently instead of serially
- **Long-running spike** — multi-device tests, real-API round-trips, OAuth flows that wait for callbacks
- **Heavy mode `/risk-spike all`** — many risks in queue; background execution lets the user continue with `/discover` or other prep while spikes resolve

**When NOT to fork**:
- Spike needs interactive dialogue ("I need you to log in to the Stripe sandbox in this browser")
- Quick spike (<5 min) where waiting is fine
- Fork env var not enabled — falls back to main-thread execution; same skill, same outputs

**Invocation**:

```
/fork /risk-spike R3
```

The fork inherits the project's risk register, concept, ADRs, and any work-in-progress context. Default behavior (no fork) is unchanged — runs in main thread.

## Next step

- GO: back to `/discover` (if not done) or `/slice`
- NO-GO: back to `/discover` to revise
- CONDITIONAL: `/slice` with caveats noted in ADR
