---
name: pulse
description: "Scan the AI SDLC vault and produce a compact 'macro state' summary — mode, active slice stage + next action, risk exposure, regression health, Critic calibration status, top aggregated lessons, recommended next skill. Use at session start to orient quickly, when returning to a project after time away, when handing off, or any time you want a single-command project pulse. Replaces 5-6 individual file reads with one structured summary. Renamed from /status (slice-035, SRCD-1) to avoid colliding with the Claude Code built-in /status command. Trigger phrases: '/pulse', 'where are we?', 'pulse', 'macro state', 'vault scan'."
user_invokable: true
argument-hint: [--brief | --full]
---

# /pulse — Project Pulse / Macro State

You scan the AI SDLC vault and produce a compact structured summary. Designed to replace the "reading 5-6 vault files to orient" problem with one call.

## Where this fits

- **Session start**: run first thing to get oriented — especially useful after context resets
- **After time away**: "what was I doing?" in one command
- **Handoff**: share the status output with a collaborator for instant context
- **Before major decisions**: see the full picture before deciding next slice

Independent of modes. Read-only — never modifies vault files.

## Argument modes

- `/pulse` — default balanced summary (~60 lines)
- `/pulse --brief` — one-screen summary (~20 lines) for quick glance
- `/pulse --full` — comprehensive view (~150 lines) including deferred items, recent reflections digest

## Prerequisite check

- `architecture/` must exist. If not: project hasn't been opened via `/triage` or `/adopt`; suggest one of those.
- Graphify is nice-to-have but not required.

## Your task

### Step 1: Read the vault state

Read these files (non-recursive, small total):

- `architecture/triage.md` → mode, classification, pipeline path, deferred steps
- `architecture/concept.md` (if exists) → 1-line "what it does"
- `architecture/risk-register.md` → risks with status (open / mitigating / retired / accepted) — use the **RR-1** audit (`$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open --sort score`) for scored, sorted output. Surface top-3 open by score in the "Risk exposure" section; older legacy table-format files emit zero risks and fall back to a grep-based summary with a one-line "register not migrated to RR-1 format" hint.
- `architecture/slices/_index.md` → active slice list, recent-10, aggregated lessons
- Active slice folder (if any): `milestone.md` FIRST (primary source — explicit stage, next-action, progress, on-resume data in one file). Only read `mission-brief.md` for extra detail on intent or ACs if the milestone summary isn't enough.
- If `milestone.md` shows stage `build` (or later but `build-log.md` exists): also read the **tail (~last 15 lines) of `build-log.md`'s `## Events` section**. This is the append-only flight recorder written by `/build-slice` Step 7c. Tool failures and session deaths can leave `milestone.md` stale; the events trace is the durable record. Compare the latest event timestamp to milestone.md's last update — if events are newer, milestone.md is behind and the events tell the real story.
- `architecture/shippability.md` (if exists) → count of critical paths
- `architecture/critic-calibration-log.md` (if exists) → last calibration run date, slices since last run
- `architecture/lessons-learned.md` → last 3-5 entries (most recent patterns)
- `architecture/drift-log.md` (if exists) → unresolved drift count
- `architecture/changelog.md` (if exists) → pipeline-bypass count
- `~/.claude/methodology-changelog.md` (if exists) → most recent dated entry; surfaces AI SDLC methodology version and last rule added
- `~/.claude/ai-sdlc-VERSION` (if exists) → AI SDLC semver string

Don't read individual slice files (active slice excepted). Don't read ADRs (too many). Don't descend into `slices/archive/`.

### Step 2: Compute derived metrics

**Active slice stage + next action** — read directly from `milestone.md` frontmatter:
- `stage:` field — explicit, not derived (low failure rate)
- `next-action:` field — explicit specific command (e.g., "run /critique" or "address B1 blocker then re-run /critique")
- Progress checkboxes — mid-phase state (e.g., "build — 3/5 tasks complete")
- "On resume" section — if session resumes, this tells you where to pick up

Fallback (if `milestone.md` missing — shouldn't happen but handle it): derive stage from file existence as a safety net:
- No mission-brief.md → "none"
- Only mission-brief → "slice"
- +design.md → "design"
- +critique.md → "critique"
- +build-log.md → "build"
- +validation.md → "validate"
- +reflection.md → "reflect" (should be auto-archived)

If fallback triggers: flag to user "milestone.md missing — consider running `/archive --index-only` or manually recreating milestone.md per `~/.claude/templates/milestone.md`."

**Regression health**:
- Shippability count
- Last full catalog run = most recent validation.md that mentions "Shippability catalog run"
- Slices since last run
- If >3 slices since last full run AND catalog exists: ⚠️ flag

**Critic calibration status (cadence enforcement per CAL-1)**:
- Slices since last `/critic-calibrate` run (from `architecture/critic-calibration-log.md`)
- Threshold: every 10-20 archived slices
- Categorize cadence into one of four states:
  - **within window** (0-9 slices): no flag
  - **approaching** (10-14 slices): info only
  - ⚠️ **recommended** (15-20 slices): "calibration recommended — N slices since last run"
  - ⚠️⚠️ **overdue** (>20 slices): "calibration overdue — N slices; run /critic-calibrate next"
- **Cadence-overdue override**: if state is ⚠️⚠️ overdue, the cadence flag supersedes other "Recommended next action" entries in Step 3 output (calibration runs first, then resume normal next-slice work)
- **First-run handling**: if calibration log is empty AND <10 archived slices, do not flag — output "first calibration deferred until 10 archived slices accumulate" (this is not a warning)

**Risk exposure**:
- Active HIGH risks count
- Pending spikes (HIGH risks marked "Spike? YES" that haven't been retired)

### Step 3: Produce the summary via Haiku dispatch

Per **COST-1** (cost-optimized model selection — `methodology-changelog.md` v0.4.0), the rendering work in this step is dispatched to a Haiku subagent. Steps 1+2 (vault reads + metric computation) stay main-thread; the summary text generation goes to Haiku.

**Dispatch:**
- Use the Agent tool with `subagent_type: "general-purpose"` and `model: haiku`.
- Hand the agent the structured state from Steps 1+2 as a dict: `{mode_arg ("brief" | "default" | "full"), project, sdlc_mode, opened, methodology_version, methodology_last_rule, methodology_updated, active_slice, recent_slices, risks, shippability, calibration, drift, lessons, next_action}`.
- Hand the agent the template for the requested mode (see below) and ask it to fill.
- The agent returns the summary text. Main thread prints it.

**Why Haiku**: `/pulse` is read-only summarization of structured state. No reasoning, no synthesis — just rendering. Haiku does this in a fraction of Opus's time and cost.

Output format (default, balanced) — **the dispatched agent fills this**:

```markdown
# Project Pulse — <YYYY-MM-DD>

## Identity
**Project**: <name from concept.md, or dir name>
**Mode**: <Minimal | Standard | Heavy>
**Opened**: <triage date> (<days>d ago, <last re-triage date if any>)

## Methodology
**SDLC version**: <semver from `~/.claude/ai-sdlc-VERSION`, or "not installed — re-run install to surface methodology metadata">
**Last rule added**: <RULE-ID from most recent changelog entry, e.g., "META-1 (Methodology versioning + changelog)">
**Updated**: <date of most recent changelog entry>

## Slices
**Total**: 23 shipped (22 archived, 1 active)

### Active
**slice-023-add-receipt-ocr** (stage: **critique**)
- Intent: OCR fallback for receipts when user skips photo upload
- ACs: 4 / 4 testable
- Critic: pending
- **Next action: run `/critique`**

(If active slice is in `build` stage and `build-log.md` events tail shows activity newer than milestone.md OR an unresolved FINDING/ERROR, append:)

- Recent activity (build-log.md events, last ~5):
  - 2026-05-03 14:25 BUILD: :app:assembleDebug PASS
  - 2026-05-03 14:30 SMOKE: mid-slice run on Pixel 7
  - 2026-05-03 14:32 FINDING: version footer half-hidden by nav bar
  - 2026-05-03 14:33 ERROR: screenshot read failed
- ⚠️ Recent FINDING/ERROR not reflected in milestone.md — verify next-action with user before continuing

### Recently shipped
- slice-022-settings-page (2 slices ago) — user prefs + password change
- slice-021-onboarding-flow (3 slices ago) — first-run UX + empty states
- slice-020-add-csv-export (4 slices ago) — CSV export from expenses page

## Risk exposure
- **Active HIGH**: 2 — R7 (image latency), R11 (OAuth token scope edge case)
- Pending spikes: 0
- Recent retirements: 5 (R3, R4, R5, R8, R10)

## Regression health
- Shippability catalog: **22 critical paths**
- Last full run: slice-022 (2 slices ago) — PASS
- ⚠️ if >3 slices since full run: "Consider running shippability during current /validate-slice"

## Critic calibration
- Recent miss categories: 2 platform-specific (iOS HEIC), 1 concurrency (from last 10 reflections)
- Last `/critic-calibrate` run: 8 slices ago (2 proposals accepted)
- Threshold: every 10-20 archived slices
- Status: **within window** (8 of 20-slice budget — calibration not yet recommended)

(For an overdue project, this section reads: `Status: ⚠️⚠️ overdue (24 slices since last; threshold 20)`. When overdue, the **Recommended next action** section below shows `/critic-calibrate` first, overriding other suggestions until run.)

## Drift & bypass
- Unresolved drift entries: 0
- Pipeline bypasses (changelog.md): 1 (typo fix on 2026-04-18)

## Top lessons (last 5 recent)
- Image features: enumerate formats + EXIF upfront
- Multi-device: validate on 2+ instances always
- Auth changes: always generate fix-slice for password reset compat
- Async queue slices: smoke-test the queue before declaring done
- HEIC handling: always rotate via EXIF orientation

## Recommended next action

**Cadence-overdue override (CAL-1)**: if Critic calibration is ⚠️⚠️ overdue (>20 slices since last run), the top line of this section is `Run /critic-calibrate (cadence-overdue: N slices since last; threshold 20)` — supersedes the active-slice next action until calibration runs. Other suggestions queue beneath. This is the only recommendation that overrides active-slice state.

**Otherwise** (the common case — calibration within window or approaching threshold):

**Run `/critique` on slice-023** (design complete; Critic hasn't reviewed).

Queued-after candidates (from recent Discovered + Deferred):
1. Fix iPhone HEIC EXIF orientation regression (from slice-022 reflection)
2. OCR confidence threshold tuning (deferred from slice-023)
```

### Step 4: Brief mode (`/pulse --brief`)

Compress to one-screen summary (~20 lines):

```markdown
# <project> — slice-023 (critique stage) | Mode: Standard | SDLC v0.1.0

**Next**: /critique (design done, Critic pending)

Active HIGH risks: 2 (R7, R11)
Shippability: 22 paths, last run OK (2 slices ago)
Critic calibrate: 8 slices since last run (threshold: 10-20)
Drift: clean

Recent lessons: image EXIF, multi-device validation, auth fix-slices
```

### Step 5: Full mode (`/pulse --full`)

Balanced view, plus:
- All active HIGH risks detailed
- All deferred items from last 5 reflections (candidates for next /slice)
- All aggregated lessons (not just top 5)
- Shippability catalog full listing
- Critic calibration history (all past runs)
- Changelog bypass events in detail

Length: ~150 lines. Use when doing a deep orientation.

## Critical rules

- READ-ONLY. Never edit vault files.
- Derive, don't fabricate. If a file doesn't exist, state that explicitly ("No shippability catalog yet — first slice hasn't populated it").
- Be specific about next action. Don't just say "continue"; say "run /critique" or "run /validate-slice" based on active slice stage.
- Flag warnings (⚠️) for: overdue critic-calibrate, shippability not run in >3 slices, drift entries unresolved, bypass log growing.
- In `--brief` mode, no tables — terse one-liners.
- Token budget target: `--brief` <500 tokens; default <2k; `--full` <5k.

## What /pulse is NOT

- Not a status-tracking system. Nothing is persisted by this skill — it just reads and summarizes.
- Not a report generator for stakeholders.
- Not a replacement for `/drift-check` or `/reduce` — those do work; this one observes.

## Anti-patterns

- **Running /pulse during a slice to "check progress"**: you already have the context in plan mode. Use /pulse for ORIENTATION, not constant-checking.
- **Ignoring /pulse flags**: if /pulse shows ⚠️ for overdue critic-calibrate and you run 5 more slices without addressing it, the Critic keeps missing the same categories. The flags exist for a reason.

## Principle alignment

- Helps enforce **Iterate per slice** (Principle 1): clear active slice + next action every session
- Surfaces **Risk-first** (Principle 2) status: active HIGH risks always in view
- Grounds **Vault as AI memory** (Principle 5): the summary IS the AI's macro memory of the project

## Next step

Whatever the "Recommended next action" line says. `/pulse` is an orientation tool; it hands off to real work skills.
