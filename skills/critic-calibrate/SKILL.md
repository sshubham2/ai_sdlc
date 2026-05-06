---
name: critic-calibrate
description: "Meta-skill: analyzes 'Critic calibration' + 'Missed by Critic' entries across recent reflections, identifies patterns in Critic blind spots, PROPOSES targeted updates to the critique skill's adversarial prompt. Human reviews and accepts — never auto-applies. Run periodically (every 10-20 slices) to close the feedback loop and systematically reduce Critic misses. Trigger phrases: '/critic-calibrate', 'calibrate the Critic', 'improve Critic prompt based on misses', 'analyze Critic blind spots', 'meta-critique'."
user_invokable: true
argument-hint: [--window N]
---

# /critic-calibrate — Close the Critic Feedback Loop

You analyze patterns in the Critic's misses across recent reflections and PROPOSE (not auto-apply) targeted prompt updates for `~/.claude/agents/critique.md`. This closes the feedback loop that was previously manual.

## Why this exists

Every `/reflect` fills a "Critic calibration" section — which Critic findings reality validated, which were false alarms, and what reality surfaced that the Critic MISSED. Over many slices, the "Missed by Critic" entries form patterns: categories of issues the Critic's prompt doesn't explicitly attack. Left manual, this data piles up without improving the Critic. This skill mines it and turns it into prompt improvements.

## When to use

- Every 10-20 slices as a routine calibration pass
- When `/reflect`'s Critic calibration section shows repeated misses in the same category
- When a serious bug slipped past Critic — run right after to update the Critic for next time
- Before a major release (catch accumulated blind spots)

Independent of modes — runs in all three.

## Argument

- `/critic-calibrate` — default window of last 15 reflections
- `/critic-calibrate --window N` — analyze last N reflections instead

## Prerequisite check

- `architecture/slices/archive/` exists with at least 5 archived slices (can't find patterns in <5)
- `architecture/slices/_index.md` exists (optional; if present, use for quick navigation)

If fewer than 5 archived slices: tell user to return after more slices have accumulated.

## Your task

### Step 1: Gather inputs for the analysis agent

Collect the four inputs the Meta-Critic agent needs:

1. **Window of archived reflections**. List the last N (default 15) archived slice folders:
   ```bash
   ls -t architecture/slices/archive/ | head -N
   ```
   For each, read its `reflection.md` and extract the "Critic calibration" + "Missed by Critic" sections. Concatenate into one block tagged by slice.

2. **Current Critic prompt**. Read `~/.claude/agents/critique.md` in full. (Note: prior versions of this skill referenced `~/.claude/skills/critique/SKILL.md` — the prompt has since moved to the agent file; this is the current canonical location.)

3. **Past calibration log**. Read `architecture/critic-calibration-log.md` if it exists. Empty file or missing → "no prior runs".

4. **Effectiveness data**. For any prior accepted proposal in the log, count misses in that category in the current window vs the equivalent window before the proposal was applied. Hand this to the agent so it knows whether prior fixes worked.

### Step 2: Invoke the Meta-Critic agent

Use the Agent tool with **`subagent_type: "critic-calibrate"`**. The agent at `~/.claude/agents/critic-calibrate.md` carries the full meta-review prompt — classification rubric, ≥3-distinct-slice threshold, proposal cap of 3, the "honesty over volume" rule, the output structure.

Your prompt body is just the inputs:

```
Window: last <N> archived reflections
Slice range: slice-<first> through slice-<last>

# Reflections in window
<paste extracted "Critic calibration" + "Missed by Critic" sections, tagged by slice>

# Current Critic agent prompt
# (from ~/.claude/agents/critique.md)
<paste full file contents>

# Past calibration log
# (from architecture/critic-calibration-log.md, or "no prior runs")
<paste contents>

# Effectiveness check
# For each prior accepted proposal:
<for each: category, run date, miss count in N reflections before, miss count in N reflections after>
```

The agent returns a structured analysis: pattern summary table, effectiveness section, 0–3 proposals, "watching but not proposing" list. Don't re-prompt for dimensions or examples — the agent already has the rubric.

**If the agent returns "no proposals this run"**: that's a valid result. Skip directly to Step 5 (log the run with zero proposals) — don't push the agent to find something. The honest-zero outcome is part of the calibration loop.

### Step 3: Present proposals one-at-a-time

Do NOT bundle all proposals into a single accept/reject. The agent has produced 0–3 proposals; present each separately:

- Show the pattern (with evidence from slices)
- Show the relevant excerpt from `~/.claude/agents/critique.md` that the proposal targets
- Show the proposed change
- Explain why this addition would have caught the observed misses
- Wait for user: **accept / modify / reject**

User reviews each in turn. Capture their decision (and any modifications) for the calibration log.

### Step 4: NEVER auto-apply

This skill PRODUCES proposals. It does NOT edit `~/.claude/agents/critique.md` itself. Reasons:

- The Critic prompt is load-bearing — a bad auto-edit propagates to every subsequent slice
- Human review is the cheap safety
- Audit trail matters — accepted proposals should be explicit user actions

For accepted proposals, state:

```
Accepted. To apply, edit ~/.claude/agents/critique.md and add the following under the
"Review along these 8 dimensions" section (dimension <N>):

<exact text>
```

User edits manually. If they want help applying, they can explicitly ask Claude to make the edit — this skill itself never writes to the critique agent file.

### Step 5: Log the calibration run

Append to `architecture/critic-calibration-log.md`:

```markdown
## Calibration run — <YYYY-MM-DD>

**Window**: last <N> reflections (slice-<first> through slice-<last>)
**Total misses analyzed**: <count>

### Pattern summary

<paste the agent's pattern summary table>

### Effectiveness on past proposals

<paste the agent's effectiveness section, or "no prior proposals">

### Proposals

| # | Pattern | Proposed | User action |
|---|---------|----------|-------------|
| 1 | Platform-specific quirks | Added sub-category to dimension 2 | ACCEPTED |
| 2 | Concurrency naming | New dedicated dimension | REJECTED (too niche) |
| 3 | ... | ... | MODIFIED (user changed wording) |

### Effectiveness check

Next calibration run should verify the accepted proposals actually reduced misses in those categories. Compare miss counts in categories pre-proposal vs post-proposal.
```

This creates an audit trail + enables measuring whether the calibration actually works over time.

## The agent vs the skill — separation of concerns

- **Agent** (`~/.claude/agents/critic-calibrate.md`): does the analysis — extracts misses, classifies into categories, applies the ≥3-distinct-slices threshold, correlates with current Critic prompt, generates 0–3 evidence-backed proposals. Read-only tools.
- **Skill** (this file): orchestrates — gathers inputs, invokes the agent, presents proposals one-at-a-time to the user for accept/modify/reject, writes the calibration log. The skill is glue; the agent is the work.

If the analysis rubric needs tuning (different category set, different threshold, different proposal cap), edit the agent file. The skill rarely needs changes once stable.

## Critical rules

- USE THE Agent TOOL with `subagent_type: "critic-calibrate"`. Don't re-implement the classification rubric in the main thread.
- NEVER auto-apply prompt changes. Even after the user accepts a proposal, this skill does not write to `~/.claude/agents/critique.md`. The user (or Claude in a separate explicit turn) applies it.
- ONE proposal at a time during user review. Don't bundle.
- TRUST the agent's "no proposals this run" output. Don't push it to find something.
- EVIDENCE-BASED proposals only. Every proposal references actual miss counts + specific slice numbers. No hypothetical "might be useful" additions.
- TRACK effectiveness across calibration runs. The agent reads the log and adjusts; the skill ensures the log is updated after every run (even runs with zero proposals).

## Anti-patterns

- **Over-prompting the Critic**: too many specific cases make the prompt bloated and Critic starts skimming. Each calibration should add at most 2-3 items.
- **Generic additions**: "pay more attention to edge cases" is useless. Specific: "Check HEIC EXIF orientation when handling iPhone image uploads" is useful.
- **Removing existing dimensions**: this skill ADDS specificity. If a dimension is never used: that's not this skill's job; address in a different calibration review.

## Effectiveness signals

Good calibration runs produce:
- 1-3 accepted proposals (not 0, not 10)
- Specific, evidence-backed additions
- Measurable reduction in miss category counts at next calibration

Bad signals:
- 0 accepted proposals three calibrations in a row → either Critic is already excellent (unlikely) or this skill is being run too frequently; stretch window to last 25-30 slices
- Accepted proposals don't reduce misses in next calibration → proposals were too generic; refine specificity

## Principle alignment

- **Two AI personas** (Principle 3): this is the continuous-improvement loop for the Critic persona
- **Vault as commit metadata** (Principle 5): `critic-calibration-log.md` is vault-appropriate (why the Critic prompt evolved)

## Next step

- Accepted proposals → user edits `~/.claude/agents/critique.md` manually
- Run next calibration in 10-20 slices to measure effectiveness
- If nothing accepted 3x in a row → widen window or skip runs until more data
