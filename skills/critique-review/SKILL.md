---
name: critique-review
description: "AI SDLC pipeline. Dual review for /critique — spawns the critique-review meta-Critic agent to review the first Critic's output (critique.md) for false positives, false negatives, and severity miscalibrations. Use after /critique, before TRI-1 user triage. Trigger phrases: '/critique-review', 'meta-review the critique', 'second-pass critique', 'review the Critic', 'dual review'. Per-slice second opinion that complements /critic-calibrate's cross-slice pattern mining."
user_invokable: true
---

# /critique-review — Dual Review (DR-1)

You are running the meta-Critic review of the first Critic's output for the current slice. The meta-Critic is a SEPARATE Agent (spawned via the Agent tool with `subagent_type: "critique-review"`) — its job is to challenge the first Critic's review for accuracy, specificity, and severity calibration.

Per **DR-1** (`methodology-changelog.md` v0.17.0).

## Where this fits

Runs after `/critique` (critique.md exists). Output feeds the user's TRI-1 triage step (Step 4.5 of /critique) — the user reconciles findings from both passes when ratifying dispositions.

The two-Critic-pass model: first Critic reviews the design adversarially; meta-Critic reviews the first Critic's review for over-reach, under-reach, and severity miscalibration. Same underlying model, different roles. Cost: ~15-20% more tokens than a single Critic pass. Catches per-slice errors that `/critic-calibrate` (cross-slice pattern mining) won't see soon enough.

## When to run

Manual invocation in v1. Recommended scenarios:

- **High-tier slices** (`risk-tier: high` in milestone.md): always run; the cost of a missed concern is highest here.
- **Slices touching auth / data model / contracts**: Critic blind spots in these dimensions are expensive in production.
- **Slices where the first Critic returned "no findings"** on a non-trivial design: 3+ slices in a row of clean reviews is a calibration smell — run dual-review to verify.
- **Slices where the first Critic returned 5+ findings**: severity inflation is possible; meta-review can recalibrate.

In Minimal mode or for low-tier slices: optional. The cost-benefit of dual review for trivial slices is low.

A v2 may add automatic invocation via a `**Dual-review**: true` mission-brief field; for now it's manual.

## Prerequisite check

- Find active slice folder
- Read `mission-brief.md`, `design.md`, and **`critique.md`** (must exist; this skill does not run `/critique` itself)
- If `critique.md` doesn't exist: stop, tell user to run `/critique` first
- If `critique.md` shows "no blockers, no majors" AND the slice is low-tier with no mandatory triggers: consider whether dual-review is worth the cost; ask the user before proceeding

## Your task

### Step 1: Gather meta-Critic context

Collect the inputs the meta-Critic needs:

- The slice's mission brief (intent, ACs, must-not-defer, out-of-scope)
- The slice's design.md
- The slice's critique.md (the first Critic's findings + verdict)
- Any new ADRs from this slice
- The 8 review dimensions (the meta-Critic re-applies these independently)

### Step 2: Spawn the critique-review agent

Use the Agent tool with **`subagent_type: "critique-review"`**. This is a named subagent at `~/.claude/agents/critique-review.md` carrying the full meta-Critic prompt — adversarial-meta stance, scoring rules (VALID / SUSPICIOUS / SEVERITY-WRONG), missed-findings discipline, output format. You don't repeat that here.

Hand the agent the inputs in this shape:

```
Slice: slice-NNN-<name>
Mode: <Minimal | Standard | Heavy from triage.md>
Risk tier: <low | medium | high from milestone.md>

# mission-brief.md
<paste full contents>

# design.md
<paste full contents>

# critique.md (first Critic's output)
<paste full contents>

# New ADRs (if any)
<paste contents of each ADR-NNN-*.md created by this slice>
```

Return the agent's complete `critique-review.md` content. Do not re-prompt for dimensions or scoring rules — the agent already knows them.

**If the agent returns "ACCEPT, no suspicious / missed / severity adjustments"**: that's a valid result. The first Critic's review is sound. Do not push back. Trust the calibration loop in `/reflect` (and a future `/critic-calibrate` extension) to surface false negatives over time.

**If the meta-Critic's findings look generic** ("the first Critic could be sharper"): the meta-Critic prompt may have degraded. Request a re-run with: "Findings must reference specific finding IDs (B1, M2, m3) AND specific design.md sections — re-review with specificity."

### Step 3: Receive meta-Critic findings

Take the agent's output and write it to `architecture/slices/slice-NNN-<name>/critique-review.md` using the format the agent emits.

Per **TPHD-1** (`methodology-changelog.md` v0.32.0) sub-mode (b), when the meta-Critic's ACCEPTED-FIXED findings (during /critique Step 4.5 TRI-1) will change test function names or AC #N row references in `mission-brief.md` or `design.md`, harmonize the mission-brief TF-1 plan section in the same fix block. Sub-mode (a) lives in `/critique` Step 4 (post-fix-prose harmonization); (c) lives in `/build-slice` Prerequisite check (pre-flight harmonization bullet).

### Step 4: Run the audit

Validate the resulting file's structure:

```bash
$PY -m tools.critique_review_audit architecture/slices/slice-NNN-<name>
```

The audit checks: 4 required sections present, dual-review verdict in `{ACCEPT, ADJUST, EXTEND}`, Reviewed-by + Date fields. If violations: surface them; if the agent's output was malformed, ask for a re-run.

### Step 5: Hand off to TRI-1 triage

Tell the user:

- "Dual review complete for slice NNN. Files: critique.md (first Critic) + critique-review.md (meta-Critic)."
- "Dual-review verdict: <ACCEPT | ADJUST | EXTEND>."
- "<N> suspicious findings, <M> missed findings, <K> severity adjustments."
- "Run `/critique` Step 4.5 (TRI-1 user triage) to reconcile both passes when setting dispositions."

The user's triage incorporates BOTH passes:
- For each first-Critic finding marked SUSPICIOUS by the meta-Critic: the user can OVERRIDE with reduced friction (the meta-Critic agrees the original finding was over-reach).
- For each meta-Critic missed finding: the user adds it to the triage table as a new disposition row.
- For each SEVERITY-WRONG entry: the user adjusts the severity in the triage table or treats it informationally.

The audit at Step 4.5's `triage_audit` already validates that each finding (including new meta-Critic missed findings) has a disposition.

## Critical rules

- USE THE Agent TOOL with `subagent_type: "critique-review"` for the meta-Critic. Don't fake it by self-reviewing in the main thread — that defeats the two-persona separation that DR-1 is meant to provide (and would couple the meta-Critic's reasoning to the same context that produced the first review).
- DON'T re-state the meta-Critic stance, scoring rules, or output format in the prompt body — those live in the agent file (`~/.claude/agents/critique-review.md`). Skill prompt is just inputs.
- DO NOT soften meta-Critic findings. If the first Critic was wrong, the meta-Critic should say so with specifics; don't water down severity disagreements.
- DO NOT skip the audit step. Malformed critique-review.md (missing sections, invalid verdict) will trip TRI-1's reconciliation; catch it here.
- TRACK meta-Critic accuracy in `/reflect`'s calibration section — outcomes per meta-finding (validated-on-reconsideration / overridden-at-triage / overridden-misjudged) feed long-term DR-1 calibration.

## Failure mode to watch

The meta-Critic becomes a rubber stamp if its prompt is too mild or the inputs are sparse. Warning signs:
- "ACCEPT" on 5+ slices in a row when the first Critic flagged substantive findings on each
- Missed findings always tagged generic ("could be more thorough")
- No severity disagreements ever, even when the first Critic's distribution is suspicious (all Minors, or all Blockers)

If you spot this: rerun with a more pointed prompt, or escalate to user about meta-Critic effectiveness. The future calibration extension (planned for `/critic-calibrate` v2) will mine these patterns automatically.

## The agent vs the skill — separation of concerns

- **Agent** (`~/.claude/agents/critique-review.md`): carries the meta-Critic prompt — stance, scoring vocab, missed-findings discipline, output format. Read-only tools (Read/Glob/Grep/Bash/WebSearch). The prompt is load-bearing.
- **Skill** (this file): orchestrates — gathers inputs, invokes the agent, writes the result, runs the audit, hands off to TRI-1. The skill is glue; the agent is the work.

If the agent prompt needs tuning, edit the agent file, not this skill. The skill should rarely need changes once stable (same META-3 discipline as `/critique` + `/critic-calibrate` + `/diagnose`'s narrator + field-recon).

## Heavy mode adjustment

In Heavy mode (compliance / regulated): dual review is **mandatory** for any slice with risk-tier ≥ medium. The reviewer-signature field in `critique-review.md` (TODO in v2) gives audit reviewers a record that two independent passes ran.

For now (v1), Heavy mode users should ALWAYS invoke `/critique-review` after `/critique` for medium / high tier slices. The audit doesn't yet enforce this — it's a procedural rule documented here.

## Next step

`/critique` Step 4.5 (TRI-1 user-owned triage). Reconcile findings from both passes when setting dispositions per finding.

## Pipeline position

- **predecessor**: `/critique`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: once critique-review.md is written and the structural audit is clean, hand back to `/critique` Step 4.5 (TRI-1) so the user reconciles BOTH passes. The successor edge points to `/critique`; auto-advance carries control back to that skill, where the TRI-1 user-input gate then HALTs.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - (none on this skill's own clean path) — its non-clean / Builder-Critic-disagreement output is NOT auto-advanced past anything; it is reconciled AT `/critique` Step 4.5 TRI-1, the already-enumerated HALT.

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
