---
name: triage
description: "Opens an AI SDLC project. Picks pipeline mode (Minimal / Standard / Heavy), builds the initial risk register with reversibility tags, and tells the user what to run next. Use this skill at the start of a new project that will use the AI SDLC hybrid pipeline, or when re-scoping mid-project. Mode can be pre-declared to skip the mode-selection questions: '/triage MINIMAL <description>', '/triage STANDARD <description>', '/triage HEAVY <description>'. Plain '/triage <description>' runs the full interactive flow and picks mode for you. Trigger phrases: '/triage', '/triage MINIMAL', '/triage STANDARD', '/triage HEAVY', 'start AI SDLC project', 'open project for hybrid pipeline', 'pick pipeline mode', 're-triage'. Do NOT auto-trigger for general project planning — only when user invokes the AI SDLC pipeline explicitly."
user_invokable: true
argument-hint: [MINIMAL|STANDARD|HEAVY] <one-sentence project description>
---

# /triage — AI SDLC Pipeline Opener (Greenfield)

You are opening (or re-opening) a **greenfield** project for the AI SDLC hybrid pipeline. Your job: ask enough questions to pick the right mode, build the initial risk register, and give the user a clear next step.

## Greenfield vs brownfield

- **Greenfield** (this skill): starting from an idea; no code exists yet (or code is trivial enough to discard).
- **Brownfield** (use `/adopt` instead): adopting the pipeline into an EXISTING codebase. `/adopt` reads the code, reverse-engineers initial vault, sets brownfield-aware CLAUDE.md rules.

If the user has substantial existing code (>500 LOC, real users, ongoing maintenance): STOP and suggest `/adopt` instead. Greenfield `/triage` doesn't fit brownfield adoption.

## Where this fits

This is the FIRST step of the AI SDLC hybrid pipeline for greenfield projects. The full pipeline is: `/triage → /discover → (/risk-spike) → (/user-test) → /slice → /design-slice → /critique → /build-slice → /validate-slice → /reflect → loop`.

After you complete, the user runs `/discover` next (or `/risk-spike` if HIGH-risk items are obvious now).

## Your task

### Step 0: Preflight check (machine prerequisites)

Before doing any project work, verify the AI SDLC pipeline is installed correctly on this machine. Run:

```bash
# Pick the right Python path for the platform
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe" ;;
  *)                    PY="$HOME/.claude/.venv/bin/python" ;;
esac

# Required prerequisites
test -f "$PY"                                            && echo "venv: OK"        || echo "venv: MISSING"
"$PY" -m graphify --help >/dev/null 2>&1                  && echo "graphify: OK"   || echo "graphify: MISSING"
test -f "$HOME/.claude/agents/critique.md"                && echo "agents: OK"     || echo "agents: MISSING"
test -f "$HOME/.claude/skills/slice/SKILL.md"             && echo "skills: OK"     || echo "skills: MISSING"
```

If ALL four print "OK": continue to Step 1.

If ANY print "MISSING": **STOP**. Tell the user:

> "AI SDLC pipeline prerequisites are missing on this machine. To install: `cd` into the AI SDLC source directory and tell me 'Install this. Read INSTALL.md and follow it.' Then re-run /triage. The install is idempotent — safe even if already partially configured."

Do NOT proceed to Step 1 with missing prerequisites — downstream skills will fail mysteriously when they invoke `$PY -m graphify`. Fail fast here with a clear pointer.

### Step 1: Detect re-triage

Check if `architecture/triage.md` exists:

- **If YES**: this is a re-triage. Read the file. Acknowledge the existing mode and risks. Ask only what's needed to update — typically: "What changed?" and "Does this require mode change?"
- **If NO**: fresh project. Proceed to Step 2.

### Step 2: Detect explicit mode argument

Parse the invocation:

- `/triage MINIMAL <description>` — mode is pre-declared as Minimal; skip mode-selection questions
- `/triage STANDARD <description>` — mode is pre-declared as Standard; skip mode-selection questions
- `/triage HEAVY <description>` — mode is pre-declared as Heavy; skip mode-selection questions
- `/triage <description>` — no mode pre-declared; full interactive mode selection (Step 3a)

Mode tokens are case-insensitive. If the first word of the argument matches one of the three modes, treat it as the mode declaration; the rest is the description.

If mode is pre-declared:
- Acknowledge: "Mode pre-declared: <Mode>. Skipping mode-selection questions."
- Skip Step 3a; go to Step 3b (skip questions Q2 and Q4 below — those exist to drive mode selection)

If mode is NOT pre-declared: proceed to Step 3a.

### Step 3a: Mode-selection questions (only if mode NOT pre-declared)

Ask 5 questions, ONE AT A TIME. Critical: do NOT batch. Ask one, wait, engage with the answer, then the next.

1. **What are you building, in one sentence?**
2. **Who uses this?** (Internal / B2B / B2C / mixed) — drives mode
3. **What's the biggest unknown?** (Domain / tech / users / scale / integration / something else)
4. **Compliance constraints?** (None / light — logging & access / heavy — HIPAA / PCI / SOC2) — drives mode
5. **Team size and timeline?** — drives mode

Then classify on three axes:
- Domain clarity: known | fuzzy
- Compliance: none | light | heavy
- Audience: internal | B2B | B2C | mixed

Pick the mode using these heuristics:

| Mode | Trigger conditions |
|------|-------------------|
| **Heavy** | compliance-heavy OR team >5 OR long-lived enterprise system OR public API with external consumers |
| **Minimal** | solo dev AND (MVP OR exploration OR one-off) |
| **Standard** | everything else (the default) |

Tell the user the mode + 2-3 sentence rationale BEFORE writing any files. Wait for confirmation or adjustment.

### Step 3b: Risk-only questions (only if mode pre-declared)

Mode is already known; ask only the questions that build the risk register:

1. **What are you building, in one sentence?** (if not already in the description argument)
2. **What's the biggest unknown?** (Domain / tech / users / scale / integration / something else)
3. **Team size and timeline?** (just to size scope, mode already locked)

Skip Q2 (audience) and Q4 (compliance) from Step 3a — those drove mode selection, which is already done.

If user pre-declared a mode that doesn't match what their answers suggest (e.g., declared MINIMAL but mentions HIPAA in a follow-up): flag the mismatch. Ask: "Your project sounds like it might need <other mode> because <reason>. Stick with <pre-declared> or switch?"

### Step 4: Build initial risk register

From the conversation, identify risks. For each, tag reversibility:

- **cheap**: change has low cost (hours)
- **expensive**: change has medium cost (days, with migration)
- **irreversible**: requires data migration, user re-onboarding, or is impossible

For each HIGH-risk item, decide if it can be retired with `/risk-spike` (validate empirically before any design).

### Step 5: Write the thin vault skeleton

Create `architecture/` if needed. Write the thin vault skeleton — these files only:

```
architecture/
  CLAUDE.md          ← project-level pipeline enforcement (Step 5b)
  triage.md          ← this step
  risk-register.md   ← this step
  decisions/         ← empty dir for ADRs
  spikes/            ← empty dir for /risk-spike output
  slices/            ← empty dir for slice folders
```

Do NOT pre-create `components/`, `contracts/`, `actors/`, `test-plan/`, `frontend/`, `schemas/` directories. Those are derived from code on demand. Heavy mode is the only exception — create them empty there for compliance.

Write `architecture/triage.md`:

```markdown
# Triage

**Mode**: <Minimal | Standard | Heavy>
**Date**: <YYYY-MM-DD>
**Classification**: <domain clarity> / <compliance> / <audience>

## Mode rationale
<2-3 sentences why this mode>

## Pipeline path
You'll run: <ordered list of skill invocations for this mode>

## Deferred steps
- <step skipped> — <why; revisit if X>

## Initial risk register
(mirrored in risk-register.md)

| ID | Risk | Reversibility | Spike? |
|----|------|---------------|--------|
| R1 | ... | irreversible-if-wrong | YES |
| R2 | ... | expensive | via /user-test |
```

Also write `architecture/risk-register.md` with the same risks (this becomes the running risk log).

### Step 5b-pre: Offer graphify integration

Before writing CLAUDE.md, offer to install graphify's always-on integration. This is the single biggest lift for the rest of the pipeline:

- `$PY -m graphify claude install` → adds a PreToolUse hook that nudges Claude to read `graphify-out/GRAPH_REPORT.md` before Glob/Grep. (The hook is a hint, not an interceptor — Claude still decides what to do next.)
- `$PY -m graphify hook install` → post-commit + post-checkout git hooks auto-rebuild the graph after code changes. Graph stays fresh without manual work.
- `$PY -m graphify code .` → builds the initial code graph (mostly no-op on greenfield; will grow as code ships).

Ask the user:

> "Install graphify integration (PreToolUse hook + git hooks + initial graph)? This makes every subsequent skill in the pipeline graph-aware automatically. [recommended: yes]"

If yes, run the three commands. If no, note in `triage.md` under "Deferred steps" — can be added later.

**Do NOT run `git init`.** If `$PY -m graphify hook install` fails because the directory isn't a git repo, STOP and ask the user: "This isn't a git repo yet. Want to run `git init` yourself, or skip the git-hook step for now (graphify auto-rebuild will be deferred)?" Initializing a repo is the user's decision — it touches identity (default branch, user.name/email), authorship, and CI assumptions. Do not make it silently. Same rule for `git config` of any kind.

For detail on graphify capabilities, run `$PY -m graphify --help`.

### Step 5b: Generate/update `./CLAUDE.md` — KEEP IT SMALL

This file keeps Claude on the pipeline across sessions. Must be short (~15-20 lines) so Claude actually reads it instead of skimming. Detailed skill guidance already lives in the SKILL.md files — don't duplicate it here.

**Do NOT create `architecture/CLAUDE.md`.** Single file at project root is enough. Skills themselves carry detail.

Check first: does `./CLAUDE.md` (project root) exist?

- If NO → create with the **Fresh template** below (~18 lines)
- If YES → append the **Append template** below (~8 lines). Do not overwrite existing content.

#### Fresh template (create `./CLAUDE.md`)

```markdown
# AI SDLC pipeline

**Mode**: <Minimal | Standard | Heavy> — details in `architecture/triage.md`
**Vault**: `architecture/`
**Active slice**: check `architecture/slices/_index.md`

## Hard rule before editing code

If the change is more than a typo / single-line tweak / comment / local-variable rename:

1. Check `architecture/slices/_index.md` for an active slice
2. If none → **ASK** the user: "Run `/slice` first, or is this small enough to skip?"
3. Wait for explicit answer. Don't proceed by default.

## Vault discipline

- ADRs (`architecture/decisions/ADR-*.md`) are append-only — supersede with a new ADR, never edit in place
- Mid-build design deviations → update active slice's `design.md` + note in `build-log.md`
- Run `/drift-check` before commit (or rely on the pre-commit hook)

## Testing discipline

Before declaring "tests pass" on code inside an active slice: run `/validate-slice`, not just the test suite. `/validate-slice` includes shippability catalog regression checks; raw test runs miss this.

Skills: `~/.claude/skills/<name>/SKILL.md`. Templates: `~/.claude/templates/`.
```

#### Append template (existing `./CLAUDE.md`)

```markdown

## AI SDLC pipeline

**Mode**: <mode>. Vault: `architecture/`. Active slice: `architecture/slices/_index.md`.

**Hard rule**: before editing code (anything more than a typo / 1-line tweak / comment / local rename), check for an active slice. If none, **ASK** the user — "Run `/slice` first, or is this small enough to skip?" Wait for the answer.

**Testing discipline**: inside an active slice, "tests pass" means `/validate-slice` passed — including the shippability catalog. Raw test-suite runs miss regressions.

ADRs are append-only (supersede, don't edit). Run `/drift-check` before commit. Skills at `~/.claude/skills/<name>/SKILL.md`.
```

That's it. No architecture/CLAUDE.md, no extensive lists, no re-declaration of skill catalog.

Why this works:
- Claude loads `./CLAUDE.md` automatically every session
- The hard rule (check active slice, ask if none) is the load-bearing bit
- Skill-specific detail is in SKILL.md files — loaded when the skill is invoked, not always
- Bypass tracking, vault scope nuances, mode-specific behaviors — all live in the relevant skill's SKILL.md

On re-triage: if mode changes or active slice section gets stale, just rewrite those lines. The file stays small.

### Step 6: Tell user what's next (mode-specific)

Close with the next step appropriate to the chosen mode.

**Minimal mode**:
- Run `/discover` next.

**Standard mode**:
- HIGH-risk items remain → "Run `/risk-spike` next to validate <risk-id> before any design"
- B2C with UX uncertainty → "Run `/user-test mockup` next to validate UX assumptions"
- Otherwise → "Run `/discover` next to map concept, users, and constraints"

**Heavy mode** (full pipeline path):
- Run `/discover` (full role-play per actor)
- Then `/risk-spike all` (mandatory for ALL HIGH risks in Heavy)
- Then `/heavy-architect` (produces comprehensive upfront vault — components, contracts, schemas, threat model, cost estimation)
- Then `/user-test` if B2C
- Then `/slice` to start the build loop
- Periodic: `/sync` every 5-10 slices for vault-code reconciliation; `/reduce` mandatory every 5 slices

Also remind: "I created/updated `./CLAUDE.md` (~20 lines) with the hard rule and vault discipline. This keeps me on the pipeline across sessions. If you ever want me to bypass, say so explicitly."

## Critical rules

- ASK ONE QUESTION AT A TIME. Wait for the answer. Never batch questions.
- Do NOT invent answers. If the user is vague, re-ask.
- Do NOT pick the mode silently. State the rationale, wait for confirmation.
- Do NOT write files until Step 5 (after mode is confirmed).
- Re-triage: append a new section to triage.md, don't overwrite history.
- **NEVER run `git init` or `git config`.** If a step needs a git repo and one doesn't exist, surface that to the user and let them decide. Repo creation is identity-touching and not yours to do silently.

## Mode quick reference

| Mode | For |
|------|-----|
| Minimal | Solo dev, MVP, exploration, one-off scripts |
| Standard | B2C, small teams, product work — the default |
| Heavy | Compliance, enterprise, regulated, public APIs |

## Principles you're applying

- **Risk-first ordering**: build the risk register upfront so downstream skills slice by risk
- **Reversibility tagging**: every risk gets a tag so design knows when to lock
- **Skip-by-default**: deferred steps are explicit; user knows what's NOT happening
