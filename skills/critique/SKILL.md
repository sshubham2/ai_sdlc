---
name: critique
description: "AI SDLC pipeline. Adversarial review of the current slice's design by a separate Critic AI persona. Spawns a separate Agent with adversarial prompt, attacks design along fixed dimensions (assumptions, edge cases, security, contracts, drift), produces blockers/majors/minors. Use after /design-slice, before /build-slice. Trigger phrases: '/critique', 'critique this design', 'review the slice design', 'have the Critic review', 'adversarial review'. Mandatory in Standard and Heavy modes."
user_invokable: true
---

# /critique — Adversarial Review by Critic Persona

You are running the Critic-persona review of the current slice's design. The Critic is a SEPARATE Agent (spawned via the Agent tool) with an adversarial prompt — its job is to attack the design, not approve it.

## Where this fits

Runs after `/design-slice`. Output blocks `/build-slice` until blockers and majors are addressed.

The two-persona model: Builder (you, in the main thread) writes designs; Critic (separate Agent) reviews them. Same underlying model, different roles. Cost: ~20% more tokens. Catches errors single-AI gates miss.

## When to run — mode + risk tier gating

Read both the project mode AND the slice's risk tier (from `mission-brief.md` frontmatter + `milestone.md`'s `critic-required` field).

| Mode | Risk tier | critic-required | Action |
|------|-----------|-----------------|--------|
| Heavy | any | any | **ALWAYS RUN** + human sign-off required |
| Standard | medium or high | any | ALWAYS RUN |
| Standard | low | true | RUN (mandatory triggers detected — auth/contracts/data model/etc.) |
| Standard | low | false | **SKIP** with explicit message + update milestone.md |
| Minimal | medium or high | any | RUN (but no sign-off) |
| Minimal | low | true | RUN |
| Minimal | low | false | **SKIP** with explicit message |

**Skip message** (when skipping):

> "Slice tier is `low` and no mandatory triggers detected. Skipping /critique for this slice — Builder self-review applies. If you want Critic anyway, re-run with `/critique --force`."

Update `milestone.md` Progress section: `- [x] /critique — <date> — skipped (risk-tier=low)` and set `next-action: run /build-slice`.

If user runs `/critique --force`: run the full flow regardless of tier. Record why in the critique.md summary.

## Mandatory triggers (override tier)

Even on a `low` tier slice, Critic runs if mission-brief or design touches any of:
- auth / authz / permissions / login / tokens / sessions
- new API contracts or endpoint shapes
- data model changes / migrations / schema
- multi-device / multi-user / sync / sharing / collaboration
- external integrations (OAuth, payment gateways, third-party API)
- security-sensitive paths (input validation, authorization decisions, secrets handling)

`/slice` sets `critic-required: true` upfront when it detects these. `/critique` double-checks here — if it scans mission-brief + design and finds a trigger that `/slice` missed, run anyway and note the discrepancy.

## Prerequisite check

- Find active slice folder
- Read `mission-brief.md`, `design.md`, and any new ADRs created in this slice
- If `design.md` doesn't exist: stop, tell user to run `/design-slice` first

## Your task

### Step 1: Gather Critic context

Collect the inputs the Critic needs:

- The slice's mission brief (intent, acceptance criteria, must-not-defer, out of scope)
- The slice's design.md
- Any new ADRs from this slice
- Pattern recognition input: read `architecture/slices/_index.md` → "Aggregated lessons" section + "Most recent 10" table. AND run semantic $PY -m graphify query against the full archive: `$PY -m graphify query "past lessons related to <this-slice's-topic>"`. The _index.md covers recent; graphify catches long-archived relevant lessons (e.g., slice-008's issue surfaces for slice-108). Only open individual archived `reflection.md` files when semantic query or _index.md points to a specific match.
- The principles being applied (risk-first, reversibility, two-persona, thin-vault)

### Step 2: Spawn the Critic agent

Use the Agent tool with **`subagent_type: "critique"`**. This is a named subagent at `~/.claude/agents/critique.md` that carries the full adversarial Critic system prompt — stance, 9 dimensions, specificity/honesty rules, output format, calibration awareness. You don't repeat that here.

Your job in this step is just to **hand the agent the inputs**. The prompt body should contain:

```
Slice: slice-NNN-<name>
Mode: <Minimal | Standard | Heavy from triage.md>
Risk tier: <low | medium | high from milestone.md>

# mission-brief.md
<paste full contents>

# design.md
<paste full contents>

# New ADRs
<paste contents of each ADR-NNN-*.md created by this slice>

# Aggregated lessons (from slices/_index.md)
<paste the "Aggregated lessons" section>

# Specific archived reflections (only if directly relevant to this slice's topic)
<paste relevant archived reflection.md files, or "none">

# Graphify status
<one line: "graphify-out/graph.json exists" or "graph not available">
```

Return the agent's complete critique.md content. Do not re-prompt for dimensions — the agent already knows them.

**If the agent returns "no blockers, no majors"**: that's a valid result. Do not push back. Trust the calibration loop in `/reflect` to surface false negatives over time.

**If the agent's findings look generic** ("consider error handling" without a file ref): the Critic prompt has degraded. Note this for `/critic-calibrate` and request a re-run with: "Findings must reference specific files / ADRs / endpoints — re-attack with specificity."

### Step 3: Receive Critic findings

Take the Critic's output and write it to `architecture/slices/slice-NNN-<name>/critique.md` using the template below.

### Step 4: Builder draft response per finding

For each blocker, major, and minor, the Builder proposes a **draft disposition** — not a final one. The user ratifies in Step 4.5.

Draft disposition vocabulary:

- **ACCEPTED-FIXED**: Builder agrees with the Critic and has applied the fix in this round (edit design.md / ADR before triage). State the change reference.
- **ACCEPTED-PENDING**: Builder agrees with the Critic; fix to apply during `/build-slice`. State what will be done.
- **OVERRIDDEN**: Builder believes the Critic is wrong. State a specific rationale — not a hand-wave. The user adjudicates in Step 4.5.
- **DEFERRED**: Builder agrees in principle but proposes punting to a later slice. State the slice or backlog target.
- **ESCALATED**: Builder cannot resolve without further investigation (spike). State what's unknown.

Update `critique.md` with Builder draft dispositions inline (one per finding under "Builder draft").

### Step 4.5: User-owned triage (TRI-1)

Per **TRI-1** (`methodology-changelog.md` v0.11.0), the user is the final triage authority — the Builder cannot override the Critic alone. This step is the explicit ratification gate.

Present the user with a compact summary of every finding + the Builder's draft disposition + a one-line rationale (or fix reference). Format:

```
Critic findings for slice-NNN <name>:

  [Blocker] B1 <title>
    Critic: <issue summary>
    Builder draft: ACCEPTED-FIXED — fix at design.md§endpoints
    Ratify? (Enter to accept, or specify: ACCEPTED-FIXED | ACCEPTED-PENDING | OVERRIDDEN | DEFERRED | ESCALATED + rationale)

  [Major] M1 <title>
    Critic: <issue summary>
    Builder draft: OVERRIDDEN — inline auth check is sufficient for v1
    Ratify? (...)

  [Minor] m1 <title>
    ...
```

For each finding, the user either accepts the draft or replaces it. OVERRIDDEN, DEFERRED, ESCALATED MUST carry a non-empty rationale (the audit refuses empty rationale on these dispositions).

Once all findings have user-ratified dispositions, compute the **Final verdict** mechanically:

- Any disposition is `ESCALATED` -> **BLOCKED**
- Else any disposition is `ACCEPTED-PENDING` -> **NEEDS-FIXES**
- Else (only `ACCEPTED-FIXED` / `OVERRIDDEN` / `DEFERRED`) -> **CLEAN**
- Zero findings -> **CLEAN**

Append to `critique.md` after the Findings + Dimensions sections:

```markdown
## Triage

**Triaged by**: user
**Date**: <YYYY-MM-DD>
**Final verdict**: CLEAN | NEEDS-FIXES | BLOCKED

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | <fix ref> |
| M1 | Major    | OVERRIDDEN | <user's reasoning, not Builder's> |
| m1 | Minor    | DEFERRED | <slice / backlog target> |
```

Then run the triage audit:

```bash
$PY -m tools.triage_audit architecture/slices/slice-NNN-<name>
```

Refusal semantics:
- `no-section`: critique.md is missing the `## Triage` heading entirely (Step 4.5 not run)
- `missing-field`: Triaged by / Date / Final verdict missing
- `invalid-verdict`: Final verdict not in {CLEAN, NEEDS-FIXES, BLOCKED}
- `missing-row`: a finding declared in the body has no triage row
- `invalid-disposition`: disposition not in the allowed vocabulary
- `missing-rationale`: OVERRIDDEN / DEFERRED / ESCALATED row has empty rationale
- `verdict-mismatch`: declared final verdict doesn't match the disposition pattern

NFR-1 carry-over: critiques in slices whose `mission-brief.md` mtime predates 2026-05-06 are exempt; the audit returns zero violations and `carry_over_exempt: true`.

If the audit returns violations: surface them, ask the user to correct the table or the verdict, and re-run. Do NOT bypass.

### Step 5: Gate decision

After Step 4.5 (user-owned triage per TRI-1) sets the final verdict and dispositions, the gate is:

- Final verdict **CLEAN** → proceed to `/build-slice`
- Final verdict **NEEDS-FIXES** → Builder applies ACCEPTED-PENDING fixes during `/build-slice`; ACCEPTED-FIXED items already settled; OVERRIDDEN/DEFERRED items recorded but don't block
- Final verdict **BLOCKED** → at least one finding ESCALATED; do not run `/build-slice`. Re-run `/design-slice` (redesign) or `/risk-spike` (investigate the unknown that prompted the escalation)

The triage_audit (`tools/triage_audit.py`) validates verdict-pattern consistency before this gate runs. Mismatch (e.g., ACCEPTED-PENDING present but verdict declared CLEAN) is a refusal — the user re-runs Step 4.5 with corrected verdict or corrected dispositions.

In Heavy mode: BLOCKED requires human reviewer sign-off on the redesign before triage may set CLEAN/NEEDS-FIXES on a re-critique.

### Step 5b: Update milestone.md

Update `architecture/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: critique`, `updated: <today>`, `next-action: run /build-slice` (or `address blockers in design.md then re-run /critique` if BLOCKED)
- Check progress box: `- [x] /critique — <date> — <CLEAN | NEEDS-FIXES | BLOCKED>`
- Update phase artifact status: `critique.md — <result>`
- "Current focus" section: critique result summary (blocker count, major count)
- "On resume": next step = /build-slice (or address blockers first)

If skipped (risk tier = low, no mandatory triggers): still update milestone.md with `- [x] /critique — <date> — skipped (risk-tier=low)` and `next-action: run /build-slice`.

### Step 6: Write critique.md

```markdown
# Critique: Slice NNN <name>

**Critic reviewed**: mission-brief.md, design.md, new ADRs
**Date**: <YYYY-MM-DD>
**Result**: CLEAN | NEEDS-FIXES | BLOCKED

## Summary
<1-2 sentences>

## Findings

### Blockers (must address before /build-slice)

#### B1: <short title>
- **Claim under review**: <quote from design>
- **Issue**: <what's wrong>
- **Evidence**: <vault ref / spec ref>
- **Proposed fix**: <concrete change>
- **Builder draft**: ACCEPTED-FIXED at <ref> | ACCEPTED-PENDING <plan> | OVERRIDDEN: <rationale> | DEFERRED to <target> | ESCALATED: <unknown>

#### B2: ...

### Majors (address this slice)
(same structure)

### Minors (log; address if cheap)
(same structure)

## Dimensions checked
- [x] Unfounded assumptions — <findings or "none">
- [x] Missing edge cases — <findings or "none">
- [x] Over-engineering — <findings or "none">
- [x] Under-engineering — <findings or "none">
- [x] Contract gaps — <findings or "none">
- [x] Security — <findings or "none">
- [x] Drift from vault — <findings or "none">

## Triage

**Triaged by**: user
**Date**: <YYYY-MM-DD>
**Final verdict**: CLEAN | NEEDS-FIXES | BLOCKED

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | <fix ref> |
```

## Critical rules

- USE THE Agent TOOL with `subagent_type: "critique"` for the Critic. Don't fake it by self-reviewing in the main thread — that defeats the two-persona separation.
- DON'T re-state the adversarial stance or 9 dimensions in the prompt body — those live in the agent file (`~/.claude/agents/critique.md`). Skill prompt is just inputs.
- DO NOT soften Critic findings. If the Critic is wrong, dispute with rationale; don't water down severity.
- DO NOT bypass the gate. Blockers block.
- TRACK Critic accuracy in `/reflect` (the calibration section). Every 10-20 slices, run `/critic-calibrate` — it analyzes "Missed by Critic" patterns across recent reflections and proposes targeted prompt updates to close blind spots (human-reviewed, never auto-applied).

## Failure mode to watch

Critic becomes a rubber stamp if its prompt is too mild. Warning signs:
- "No issues found" on 3+ slices in a row (statistically unlikely)
- Findings always tagged "minor"
- Findings generic ("consider error handling") rather than specific

If you spot this: rerun with a more pointed prompt, or escalate to user about Critic effectiveness.

## The agent vs the skill — separation of concerns

- **Agent** (`~/.claude/agents/critique.md`): carries the adversarial Critic prompt — role, stance, 9 dimensions with examples, specificity/honesty rules, output format, calibration awareness. Read-only tools (Read/Glob/Grep/Bash). The prompt itself is load-bearing; treat it like compiled code, not a comment.
- **Skill** (this file): orchestrates — gathers inputs, invokes the agent, writes the result to `critique.md`, handles Builder responses, gates `/build-slice`, updates `milestone.md`. The skill is glue; the agent is the work.

If the agent prompt needs tuning (e.g., `/critic-calibrate` proposes additions), edit the agent file, not this skill. The skill should rarely need changes once stable.

## Next step

- CLEAN or NEEDS-FIXES (after triage ratifies dispositions) → `/build-slice`
- BLOCKED → revise design (or run `/risk-spike` for an unknown), re-run `/critique`
