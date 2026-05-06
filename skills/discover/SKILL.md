---
name: discover
description: "AI SDLC discovery step. Interactive concept + user + tech-constraint exploration in one unified loop. Use after /triage. Trigger phrases: '/discover', 'discover the project', 'explore concept and users', 'AI SDLC discovery'. Do NOT confuse with general 'discovery' or research — this is specifically the AI SDLC pipeline step that runs after /triage."
user_invokable: true
---

# /discover — Concept + Users + Constraints

You are running the discovery step of the AI SDLC pipeline. Output: enough understanding of WHAT, WHO, and CONSTRAINTS to identify the first slice candidate.

## Where this fits

Runs after `/triage`. Outputs feed `/risk-spike` (if HIGH-risk items exist) or `/slice` (to start building).

## Prerequisite check

Read `architecture/triage.md`. If it doesn't exist, stop and tell the user: "Run `/triage` first to set the project mode and risk register."

Read the mode (Minimal / Standard / Heavy) — it controls what you produce.

## Your task

### Step 1: Acknowledge what you know

State briefly what triage already established (mode, risks, audience). Don't re-ask those.

### Step 2: Three-area conversation, ONE TOPIC AT A TIME

Cover these three areas in order. After each, STOP and engage with the user's answer before moving on.

#### Area 1: WHAT (concept)

Ask: "What's the core thing this app does for users? What's deliberately out of scope?"

Then engage:
- Push back on scope bloat
- Surface obvious edge cases
- Confirm explicit non-goals

#### Area 2: WHO (users + actors)

Ask: "Who are the primary users? Are there secondary roles (admin, support, integrator)?"

For each actor, briefly note:
- What they do (top 2-3 actions)
- What they need from the system (the data / signals they consume)
- Boundaries (what they CAN'T do)

In Heavy mode, do a deeper walkthrough per actor: first-time use, heavy load, error case, waiting, collaboration, audit/history.

#### Area 3: CONSTRAINTS (tech + infra + team)

Ask: "Tech stack constraints? Existing infra? Team experience? Deployment target?"

Engage honestly:
- If user picks something that doesn't fit: push back with reasoning
- If user is open: suggest options with trade-offs
- Tag each tech decision with reversibility (cheap / expensive / irreversible)

### Step 3: Address HIGH-risk items

For each HIGH-risk item from the risk register, ask: "Can we `/risk-spike` this before designing?"

If yes: note that the next step will be `/risk-spike`.
If no (e.g., risk needs design first to even formulate): note the risk stays open through design.

### Step 4: Identify the first slice candidate

Close with: "Based on this, the first slice should be **<verb-object name>**, which retires risks **<R1, R2>** and produces **<user-visible outcome>**."

Good first slices:
- Exercise the riskiest external dependency
- Produce something a real user can touch
- Cover <20% of final scope

Anti-patterns: "set up the database", "build the login page" (unless auth IS the risk), "implement basic CRUD".

### Step 4.5: Enrich the knowledge graph with external references

Graphify supports multi-modal ingestion — code, docs, papers, videos, images. During discovery, add any external references that inform the project's design. They become queryable graph nodes alongside the code.

Ask the user:

> "Any external references that shape this project's design? Examples: research papers, design docs in Notion/Confluence, stakeholder interview recordings, industry API reference docs, architecture videos. I can add these to the graph so queries span code + vault + references."

For each reference the user provides, fetch it into `./raw/` (graphify's convention) using the library — the CLI doesn't expose `add`, but the function is one import away:

```bash
mkdir -p raw
$PY -c "
from graphify.ingest import ingest
from pathlib import Path
ingest('https://arxiv.org/abs/2405.12345', Path('raw'))
ingest('https://docs.company.internal/arch', Path('raw'))
"
# Local files (audio/video) — drop them into ./raw/ directly:
cp ./interviews/stakeholder-1.mp4 raw/

# Then rebuild the graph so the new references are indexed:
$PY -m graphify code .   # for code-corpus
# or:
$PY -m graphify vault architecture   # for the vault graph
```

Audio/video files require the `[video]` extra (`pip install graphifyy[video]`) for local Whisper transcription. If unavailable, drop transcript text files into `./raw/` instead.

Skip this step if the user has nothing to add — don't push.

### Step 5: Write outputs per mode

**Minimal mode**:
- `architecture/concept.md` — 1-page brief covering What/Who/Constraints (actors as a section inline, not separate files)
- Update `architecture/risk-register.md` with discovery-phase risks
- First slice candidate stated in conversation

**Standard mode** — all of Minimal, plus:
- `architecture/concept.md` includes a richer "Actors" section with one paragraph per actor (NOT separate files in `actors/` — thin vault)
- Tech decisions captured as ADRs in `architecture/decisions/` (one ADR per non-trivial tech choice with reversibility tag) — NOT a separate `tech-brief.md` file
- For B2C: recommend `/user-test mockup` next

**Heavy mode** — all of Standard, plus:
- Full role-play walkthrough per actor (first-time / load / error / waiting / collaboration / audit)
- Separate `architecture/actors/<actor>.md` files allowed (compliance / audit artifacts)
- `architecture/requirements.md` — functional + non-functional
- Per-tech-decision tradeoff analysis as full ADRs
- Heavy mode is the only mode where the comprehensive vault structure is appropriate

## Critical rules

- ONE topic at a time. Stop after each area. Engage with answers, don't rush.
- Do NOT invent actors, scope, or constraints. Ask.
- Do NOT skip Area 1 even if "obvious from /triage" — concept depth matters.
- Do NOT propose a slice candidate until Step 4. The conversation must inform it.
- For Standard B2C: explicitly recommend `/user-test mockup` after `/discover` and before `/slice`.

## Output file templates

### concept.md

```markdown
# Concept

**Date**: <YYYY-MM-DD>
**Mode**: <from triage>

## What
<2-3 paragraphs: what users get, what's in scope, what's deliberately not>

## Who
- **<Actor 1>**: <role, top actions>
- **<Actor 2>**: <role, top actions>

## Constraints
- Stack: <tech, with reversibility tags>
- Infra: <hosting, deployment>
- Team: <size, capabilities, timeline>

## First slice candidate
**<verb-object name>** — retires <R1, R2>, ships <user outcome>.
```

### Actors (inline in concept.md, Standard mode)

In Standard mode, actors are a richer section in concept.md (NOT separate files):

```markdown
## Actors

### <name>
- **Role**: <one sentence>
- **Top actions**: ...
- **Needs from system**: ...
- **Boundaries (cannot)**: ...

### <other actor>
...
```

### actors/<actor>.md (Heavy mode only)

```markdown
# Actor: <name>

**Role**: <one sentence>

## Top actions
1. ...

## Needs from system
- ...

## Boundaries
- Cannot: ...

## Role-play walkthroughs (Heavy mode)
### First-time use
### Heavy load
### Error case
### Waiting on others
### Collaboration
### Audit / history
```

## Next step

- HIGH-risk items remain: `/risk-spike`
- B2C with UX uncertainty: `/user-test mockup`
- Otherwise: `/slice`
