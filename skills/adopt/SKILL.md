---
name: adopt
description: "AI SDLC pipeline opener for BROWNFIELD projects — existing codebases you want to adopt the pipeline into. Use INSTEAD of /triage when code already exists. Code is the source of truth — runs forensic analysis via /diagnose (optional but recommended) before trusting any docs. Asks brownfield-specific questions, produces initial vault reflecting current code reality (not aspirational README claims), generates CLAUDE.md with brownfield-aware rules (respect existing conventions, document deviations as ADRs, code-truth-over-docs). Mode can be pre-declared: '/adopt MINIMAL', '/adopt STANDARD', '/adopt HEAVY'. Plain '/adopt' picks mode interactively. Trigger phrases: '/adopt', 'adopt AI SDLC for this project', 'brownfield', 'onboard existing codebase', 'add AI SDLC to this repo', 'retrofit the pipeline'. Different from /triage (greenfield) — /adopt reverse-engineers current state from code first, not docs."
user_invokable: true
argument-hint: [MINIMAL|STANDARD|HEAVY]
---

# /adopt — AI SDLC Pipeline Opener for Brownfield Projects

You onboard the AI SDLC pipeline into an EXISTING codebase. Unlike `/triage` (greenfield, start from idea), `/adopt` starts from code that already exists and produces a vault reflecting **what the code actually does**, not what docs claim it does.

**Trust hierarchy** (load-bearing for this skill):

1. **Code observations** (via graphify AST + reachability) — primary
2. **User pain points + firsthand history** — secondary
3. **Doc claims** (README, design docs) — tertiary; treated as hypothesis only, validated against code via `/diagnose` before believed

The reason: in brownfield (especially legacy or AI-assisted codebases), README is aspirational at best, fictional at worst. /adopt's job is to bind the vault to reality, not perpetuate stale docs.

## Where this fits

First step for brownfield adoption. REPLACES `/triage` in that role — don't run both. After `/adopt`, the normal AI SDLC loop takes over (`/slice` → `/design-slice` → ... for new features; `/risk-spike` / `/user-test` as needed).

If you've already run `/triage` and now realize you should've used `/adopt`: run `/adopt` anyway; it will merge with existing vault rather than overwrite.

## Mode argument

Same as `/triage`:

- `/adopt MINIMAL` — solo brownfield, minimal ceremony
- `/adopt STANDARD` — team brownfield, full pipeline (the default)
- `/adopt HEAVY` — compliance / regulated brownfield (produces comprehensive retrospective vault; may need substantial reverse-engineering)
- `/adopt` (no mode) — interactive mode selection

## Prerequisite check

### Machine-level (preflight)

Before doing any project work, verify the AI SDLC pipeline is installed correctly on this machine. Run:

```bash
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) PY="$HOME/.claude/.venv/Scripts/python.exe" ;;
  *)                    PY="$HOME/.claude/.venv/bin/python" ;;
esac

test -f "$PY"                                            && echo "venv: OK"     || echo "venv: MISSING"
"$PY" -m graphify --help >/dev/null 2>&1                  && echo "graphify: OK" || echo "graphify: MISSING"
test -f "$HOME/.claude/agents/critique.md"                && echo "agents: OK"   || echo "agents: MISSING"
test -f "$HOME/.claude/skills/slice/SKILL.md"             && echo "skills: OK"   || echo "skills: MISSING"
```

If ANY prints "MISSING": **STOP**. Tell the user:

> "AI SDLC pipeline prerequisites are missing on this machine. To install: `cd` into the AI SDLC source directory and tell me 'Install this. Read INSTALL.md and follow it.' Then re-run /adopt. The install is idempotent — safe even if already partially configured."

### Project-level

- Working directory has code (not an empty repo)
- If `architecture/triage.md` already exists: ask if this is a merge (continue) or if we should start fresh (abort and let user clean up first)

## Your task

### Step 1: Scan the codebase (graphify is your primary tool here)

Brownfield is where graphify shines — an existing codebase has real structure to extract. Do this before asking the user anything:

```bash
# Build the graph FIRST — subsequent steps read graphify-out/ for structure
$PY -m graphify code .                    # AST + INFERRED edges across source files
# (Optional vault graph if architecture/ already exists from a prior run:)
# $PY -m graphify vault architecture
# (Optional file-watcher in a separate terminal — rebuilds on code changes:)
# $PY -m graphify.watch .
```

This produces:
- `graphify-out/graph.json` — full AST + semantic graph
- `graphify-out/GRAPH_REPORT.md` — one-page digest: god nodes, communities, surprising connections, suggested questions

Now read (in order of trust):

1. `GRAPH_REPORT.md` — fastest way to see codebase shape (~2k tokens, code-derived)
2. `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` — dependency truth (concrete, not aspirational)
3. Top-level dir tree (~10 entries) — file structure as evidence
4. `README.md` if it exists — **as hypothesis only**. Do not let README claims shape the vault directly. If README says "this service handles X" but graphify shows the X module is dead code, the README is wrong; record the discrepancy as a finding for /diagnose.

Also install always-on integration (offer to user; recommended yes for brownfield):

```bash
$PY -m graphify claude install         # PreToolUse hook for every future session
$PY -m graphify hook install           # post-commit auto-rebuild
```

Summarize to user:

```
Scanned codebase (code-derived, not doc-derived):
- Primary: Python 3.11 + FastAPI + Postgres
- ~12 endpoints, ~8 data models
- ~2,400 LOC across 34 files
- Main entry: src/main.py
- Tests: tests/ (pytest, ~60 tests, ~70% coverage from conftest)
- README.md: present (will be treated as hypothesis, not fact)
- No existing architecture/ docs

Proceeding to forensic analysis offer.
```

### Step 2: Detect explicit mode argument (same logic as /triage)

Parse: `/adopt MINIMAL|STANDARD|HEAVY <optional-description>` → skip mode-selection questions.
`/adopt` with no mode → full interactive.

### Step 3: Offer forensic analysis via /diagnose (RECOMMENDED for non-trivial brownfields)

Docs lie. Code doesn't. Before trusting any narrative about this codebase, offer `/diagnose` — a forensic skill that reads **only the code** (never docs) and produces a structured findings document covering: dead code, duplicates, half-wired features, contradictory assumptions, layering violations, AI-bloat signatures (multiple impls of the same capability, modules added without integration, stale scaffolding, inconsistent patterns suggestive of session breaks), oversized functions, dead config, test gaps.

#### When to recommend strongly (offer with "yes" as the suggested default)

- Codebase >500 LOC OR >10 source files
- Maturity: "production" or "legacy maintenance" or "handed off" (Q2 will surface this; you can preview from the scan)
- AI-assisted history (any indication the codebase was built with AI help — common patterns: many similar implementations, inconsistent style across modules, half-finished features)
- Compliance / regulated (Heavy mode candidate)

#### When to skip (offer with "skip" as the suggested default)

- Tiny project (<500 LOC) — diagnose overhead exceeds payoff
- Pure prototype / throwaway code
- User explicitly says "I know this codebase deeply, skip"

#### How to offer

Tell the user:

> "Before I trust any narrative about this codebase, I recommend running `/diagnose` — it analyzes code only (ignores docs/READMEs) and produces a `diagnosis.html` with forensic findings. You annotate each finding `Confirmed: yes/no` in your browser, save the HTML back, and I use the confirmed ones to seed the risk register + first-slice candidates via `/slice-candidates`.
>
> Cost: ~10–20 min for the analysis + your annotation pass.
> Recommended for: <state reason based on heuristics above>.
>
> Run `/diagnose` now? (yes recommended | skip | tell me more)"

#### If user chooses YES

1. Tell the user: "I'll invoke `/diagnose` next. It'll produce `diagnose-out/diagnosis.html`. Open it in a browser, mark each finding `Confirmed: yes` or `no`, click 'Save annotated HTML' to download the annotated copy, and put it back in `diagnose-out/`. Then come back here and tell me 'continue /adopt' — I'll resume from Step 4."
2. Stop here. Wait for the user to come back.
3. **On resume** (when user says continue): verify `diagnose-out/diagnosis.html` exists and contains annotations. Then invoke `/slice-candidates` to produce `backlog.md`. The confirmed findings + backlog feed Steps 6 (risk register) and 11 (handoff).

#### If user chooses SKIP

Note in `architecture/triage.md` (Step 9) that diagnose was skipped + reason. Risk register (Step 6) will be built from user pain points only, not confirmed findings. Concept.md (Step 7) derives from code observations + user input only.

#### If user chooses "tell me more"

Briefly explain what /diagnose does (one paragraph), then re-offer.

### Step 4: Brownfield interview

Ask questions tailored to brownfield context. ONE at a time, wait for engagement:

#### Always ask:

1. **What does this codebase do, in one sentence?** (Compare to what you observed in the scan — flag mismatches)
2. **What's the maturity?** (Prototype / MVP shipped / production / legacy maintenance)
3. **Who maintains it?** (Just you / small team / multiple teams / handed off)
4. **What's the next thing you want to build?** (This becomes the first slice candidate)
5. **Are there known pain points?** (Bugs you live with / tech debt / risky external integrations / deferred work)

#### If mode NOT pre-declared, also ask:

6. **Who uses this?** (Internal / B2B / B2C / mixed)
7. **Compliance constraints?** (None / light / heavy)

#### Optional (skip if user wants speed):

8. **Any historical decisions you can articulate firsthand worth capturing as ADRs?**

   STRICT rule: only capture decisions the user can describe themselves — context, options considered, why this won. Do NOT extract historical ADRs from existing docs (the doc may be wrong; if it's not in the user's head, it's not a real ADR).

   If user struggles to articulate: skip. Better 0 ADRs than 5 fictional ones.

#### What we no longer ask (deliberately removed)

- ~~"Are there docs / READMEs / Notion pages that capture design?"~~ — docs are not a trust source. If diagnose ran, code reality is captured; if user articulates firsthand history, that's captured. Doc archaeology is dropped.

### Step 5: Classify mode (if not pre-declared)

Use the same heuristics as `/triage`:

- Heavy: compliance OR team >5 OR public API
- Minimal: solo + (MVP or legacy maintenance)
- Standard: everything else

State mode + rationale, wait for confirmation.

### Step 6: Build initial risk register

Sources, in trust order:

1. **Confirmed findings from /diagnose** (if it ran) — risk-relevant findings (security gaps, half-wired features in production paths, contradictory assumptions affecting expected behavior, dead code in critical modules) become risk register entries.
2. **User pain points from Q5** — known bugs, tech debt, risky integrations, deferred work.
3. (NOT a source: README warnings or doc-based "known issues" — if real, they'll show up in 1 or 2.)

For each, tag:
- One-line description
- Reversibility (cheap / expensive / irreversible)
- Spike candidate? (YES / NO / MAYBE)
- Source: `diagnose-finding-<id>` | `user-pain-point` | `both`

Example:

```
R1: SMS provider (Twilio) has rate limits we hit in spike campaigns
    Reversibility: expensive (migration to Sinch would take 2 weeks)
    Spike? Already known behavior — no
    Source: user-pain-point

R2: PDF generation memory leak on docs >50 pages
    Reversibility: cheap (swap library)
    Spike? YES — try weasyprint replacement
    Source: both (user mentioned + diagnose F-007 confirmed: weasyprint inefficient buffer reuse)

R3: Auth token rotation deferred — code path exists but never called
    Reversibility: expensive (migration window required)
    Spike? No — design work needed, not validation
    Source: diagnose-finding-F-012 (half-wired feature)
```

### Step 7: Reverse-engineer `concept.md`

Write `architecture/concept.md` reflecting current state from CODE first, user input second:

```markdown
# Concept (brownfield)

**Date adopted**: <YYYY-MM-DD>
**Mode**: <mode>
**Codebase maturity**: <from Q2>
**Forensic analysis**: <ran on YYYY-MM-DD | skipped (reason)>

## What it does

<2-3 sentences. PRIMARY source: graphify scan of entry points + reachability. SECONDARY: user's Q1 answer. If user's answer contradicts code, note both: "User says: X. Code does: Y. Resolution: <which is right>". Do NOT reproduce README claims here.>

## Actors (inferred from code + user input)

- **<actor>**: <role>; acts via `<endpoint / UI flow>` (source: `<file>`)

Source priority:
1. Endpoints in code → external actors
2. Auth/role-check sites → role taxonomy
3. User confirmation in Q1/Q3 → labels

## Constraints (observed)

- Stack: <derived from package.json / pyproject.toml — concrete>
- Infra: <from user only — code can't always tell us this>
- Team: <from Q3>

## What docs say vs. what code does (if /diagnose ran)

<List any contradictions found between README/docs and code reality. Code wins; this section documents the discrepancies for future readers.>

## First slice candidate

<from Q4 if specific; else from backlog.md top entry if /diagnose ran>
```

### Step 8: Capture historical ADRs (firsthand only)

If the user answered Q8 with decisions they can articulate firsthand:

For each, write `architecture/decisions/ADR-historical-<NNN>.md`:

```markdown
---
id: ADR-historical-001
title: <decision>
date: <adopt date>
adopted-as-historical: true
reversibility: <tag>
status: accepted
source: firsthand-user-recall
---

# ADR-historical-<NNN>: <title>

## Context (as user remembers it)
<what the decision was made for, in user's own words>

## Decision
<what was decided>

## Consequences (observed in code)
<what's true now in the code because of this decision — verify via graphify before writing>

## Note
This is a historical ADR captured at adoption time from firsthand user recollection. Context may be partially reconstructed; treat as a snapshot, not a full record. Future decisions that change this should supersede via normal ADR process.
```

**Strict rules**:

- DO NOT manufacture ADRs from doc archaeology. If it's only in a doc and not in the user's head, skip it.
- DO NOT invent rationale. "User can't remember why" → skip the ADR or capture it as `reversibility: unknown` with explicit note.
- 3 real ADRs > 15 fictional ones.

### Step 9: Write thin vault skeleton (or comprehensive for Heavy)

Same files as `/triage`, plus diagnose artifacts if /diagnose ran:

```
architecture/
  CLAUDE.md              ← brownfield-aware version (Step 10)
  triage.md              ← records adoption (not greenfield triage); notes whether /diagnose ran
  concept.md             ← Step 7
  risk-register.md       ← Step 6 (sources tagged)
  decisions/
    ADR-historical-*.md  ← Step 8 (if any, firsthand only)
  spikes/                ← empty (to be filled by /risk-spike)
  slices/                ← empty (next feature will be slice-001)
  backlog.md             ← from /slice-candidates if /diagnose ran (else absent)

diagnose-out/            ← if /diagnose ran
  diagnosis.html         ← annotated HTML (kept as audit trail)
```

For Heavy mode: additionally run `/heavy-architect` mentally — but adapt it for brownfield:

- `components/<name>.md` — reverse-engineered from code (via graphify), one file per major module
- `contracts/<name>.md` — reverse-engineered from OpenAPI / route handlers
- `schemas/<entity>.md` — reverse-engineered from data models
- `threat-model.md` — flag known issues from user's pain points + obvious STRIDE gaps + relevant /diagnose findings
- `cost-estimation.md` — flagged as "to be populated" unless user has infra data
- `diagrams.md` — generated from $PY -m graphify code graph

In Heavy brownfield, explicitly mark each reverse-engineered file with frontmatter:

```yaml
---
source: brownfield-adoption
adoption-date: <YYYY-MM-DD>
fidelity: reverse-engineered | partial | confirmed
diagnose-cross-ref: <finding IDs that informed this, or "none">
---
```

Ask user to review and confirm fidelity before marking `fidelity: confirmed`.

### Step 10: Generate/update `./CLAUDE.md` — KEEP IT SMALL

Same discipline as `/triage`: short file (~25 lines) at project root, no `architecture/CLAUDE.md`. Skills carry detailed guidance.

Check first: does `./CLAUDE.md` exist?

- If NO → create with the **Fresh brownfield template** below
- If YES → append the **Append template** below. Do not overwrite existing content.

#### Fresh brownfield template (create `./CLAUDE.md`)

```markdown
# AI SDLC pipeline (adopted into existing codebase)

**Mode**: <Minimal | Standard | Heavy> — see `architecture/triage.md`
**Adopted**: <YYYY-MM-DD>
**Vault**: `architecture/`
**Active slice**: check `architecture/slices/_index.md`

## Hard rule before editing code

If the change is more than a typo / single-line tweak / comment / local-variable rename:

1. Check `architecture/slices/_index.md` for an active slice
2. If none → **ASK** the user: "Run `/slice` first, or is this small enough to skip?"
3. Wait for explicit answer.

## Brownfield rules

- **Code is truth, docs are hypothesis.** Before acting on any doc claim about behavior, verify against code (read it or `$PY -m graphify reachable --from=<file>`). Doc says X but code does Y → code wins, log discrepancy.
- **Respect existing conventions.** Follow the pattern unless a slice explicitly revises it.
- **Deviations need an ADR.** Breaking convention = written reason, not a judgment call.
- **Refactors need a slice.** No "while I'm here" cleanups.
- **Tests-first for bug fixes.** Reproduce with a failing test before fixing (run `/repro`).
- **Graphify before wide changes.** `$PY -m graphify reachable --from=<file>` to see blast radius.

## Vault discipline

ADRs are append-only (supersede, don't edit). Design deviations → update active slice's `design.md`. Run `/drift-check` before commit.

## Testing discipline

Before declaring "tests pass" on code inside an active slice: run `/validate-slice`, not just the test suite. `/validate-slice` includes shippability catalog regression checks; raw test runs miss this.

Skills: `~/.claude/skills/<name>/SKILL.md`. Templates: `~/.claude/templates/`.
```

#### Append template (existing `./CLAUDE.md`)

```markdown

## AI SDLC pipeline (brownfield-adopted)

**Mode**: <mode>. Vault: `architecture/`. Active slice: `architecture/slices/_index.md`.

**Hard rule**: before editing code (beyond typos/trivial), check for active slice. If none, **ASK** — "Run `/slice` first?" Wait for answer.

**Brownfield rules**: code is truth, docs are hypothesis (verify doc claims against code before acting); respect existing conventions; deviations require ADRs; refactors need slices; tests-first for bug fixes; `$PY -m graphify reachable --from=<file>` before wide changes.

ADRs are append-only. Run `/drift-check` before commit.
```

### Step 11: Tell user what's next

```
Adoption complete.

Vault produced at architecture/:
- concept.md (reverse-engineered from code first, user input second)
- risk-register.md (N risks: <N1> from /diagnose findings, <N2> from user pain points)
- decisions/ADR-historical-*.md (M historical ADRs, firsthand-only)
- backlog.md (K slice candidates from /slice-candidates) <if /diagnose ran>
- CLAUDE.md (brownfield-aware pipeline rules with code-truth-over-docs rule)

First slice candidate: <from Q4 if specific; else from backlog.md top entry>

Next step:
- Any HIGH risk needs validation? → /risk-spike
- backlog.md has dependencies sorted; consider top 1-3 entries → /slice "<top entry>"
- Otherwise → /slice "<next feature>"
```

## Critical rules

- USE INSTEAD of `/triage`, not in addition. If user runs both, the second one should merge, not overwrite.
- TRUST CODE over docs. README is hypothesis; graphify scan + /diagnose findings are facts. Where they conflict, code wins; log the discrepancy.
- DO NOT manufacture historical context. Reverse-engineered ADRs come from firsthand user recall ONLY, not doc archaeology.
- DO NOT rewrite existing code during adoption. `/adopt` is analysis + documentation, not implementation.
- RESPECT existing conventions in the brownfield CLAUDE.md. The default posture is "don't refactor without justification."
- OFFER /diagnose for non-trivial brownfields. It's the cure for the doc-trust problem. Don't make it mandatory but recommend strongly when warranted.
- HEAVY BROWNFIELD: produce the comprehensive vault via graphify + user review, but mark fidelity (`reverse-engineered` / `partial` / `confirmed`) and cross-reference /diagnose finding IDs. Auditors should see what's verified vs inferred vs confirmed-by-forensic-pass.

## Anti-patterns to avoid

- **Trusting README**: README says "this service does X" — don't write that into concept.md without verifying against code. /diagnose exists for this reason.
- **Doc archaeology for ADRs**: extracting historical ADRs from existing docs that the user can't articulate firsthand. Skip them. Better 0 than 5 fictional.
- **Skipping /diagnose to save time on a substantial brownfield**: 15 minutes of forensic pass saves hours of slicing on top of stale assumptions. Recommend strongly when codebase warrants.
- **Over-documenting**: don't reverse-engineer 30 component files and 50 contracts for a small project. Match vault scope to project scope.
- **Under-engaging with the user**: don't let `/adopt` become silent auto-generation. Q5 (pain points) is the most valuable subjective input; user memory + code reality together are richer than either alone.
- **Making up ADRs**: if user can't articulate a historical decision's rationale, don't invent one. Skip it.

## When to use `/triage` instead of `/adopt`

- Greenfield (no code yet)
- Existing code is so small it's effectively greenfield (<500 LOC, no users)
- You're starting over (discarding existing code)

## Next step

- backlog.md exists (from /slice-candidates) → `/slice` against the top backlog entry
- HIGH risks exist → `/risk-spike`
- B2C and next slice is UX-critical → `/user-test mockup`
- Otherwise → `/slice "<next feature>"` to start the build loop
