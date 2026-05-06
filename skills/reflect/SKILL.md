---
name: reflect
description: "AI SDLC pipeline. Capture what this slice taught you and update the vault with reality. Categories: validated / corrected / discovered / deferred. Tracks Critic accuracy. Use after /validate-slice, before next /slice. Trigger phrases: '/reflect', 'reflect on slice', 'capture learnings', 'update vault with reality', 'slice retrospective'. The cure for spec rot — automatic vault updates at slice boundaries."
user_invokable: true
---

# /reflect — Capture Reality, Update Vault

You are reflecting on the just-completed slice and updating the vault with what reality taught you. This is THE step that prevents spec rot.

## Where this fits

Runs after `/validate-slice`. Output feeds the next `/slice` (the discoveries and deferrals inform what to build next).

## Why this matters

Spec rot is the biggest failure mode of spec-driven SDLC: spec written, code evolves, spec goes stale, discipline collapses. The cure: make vault updates automatic at slice boundaries, not optional at project end. Every slice produces deltas to the vault — `/reflect` is where they land.

## Prerequisite check

- Find active slice folder
- Read all of: `mission-brief.md`, `design.md`, `critique.md`, `build-log.md`, `validation.md`
- If `validation.md` is missing: stop, run `/validate-slice` first

## Your task

### Step 1: Synthesize learnings into four categories

Read all slice files. Categorize observations:

#### Validated
Design claims that reality confirmed. Examples:
- "Endpoint accepts JPEG/PNG/HEIC up to 10MB — validated by curl tests on each format"
- "Authorization rejects non-owners — manual check with second account"

#### Corrected
Design claims that reality refuted. Vault must be updated.
- "Design said thumbnails generate async; reality is sync (async queue is a separate slice)"
- "ADR-008 chose sendgrid; reality is we used resend"

#### Discovered
Things you didn't know to spec. New risks, edge cases, constraints.
- "iPhone HEIC files have EXIF orientation; thumbnails appeared sideways without handling"
- "S3 PUT timeout default (30s) is too aggressive for >5MB files"

#### Deferred
Things not done this slice. Will be addressed in next slice or backlog.
- "Multiple receipts per transaction — out of scope per mission brief"
- "Receipt deletion — separate slice"

### Step 2: Update affected vault files (thin vault)

The thin vault has fewer files to update. For each Corrected item, update the relevant file:

- Decision wrong → supersede the ADR (procedure below)
- Risk claim wrong → update `architecture/risk-register.md`
- Concept assumption wrong → update `architecture/concept.md` (the relevant section)
- Slice's own design wrong → update the slice's `design.md` (note the change in build-log too)

For each Discovered item:
- Add to `architecture/risk-register.md` with reversibility tag
- If it affects current slice scope: note in this slice's `reflection.md`
- If it spawns a future slice: leave a candidate note for next `/slice`

For superseded decisions:
- Mark original ADR `status: superseded`
- Add `superseded-by: ADR-NNN` field to the original
- Create new ADR with updated decision + `supersedes: ADR-NNN` field
- DO NOT edit the original ADR's content. Decisions are append-only history.

**What you do NOT update** (because they don't exist in thin vault, Standard / Minimal mode):
- `components/<name>.md` — read the code instead
- `contracts/<name>.md` — code IS the contract (FastAPI / OpenAPI / Pydantic)
- `schemas/<name>.md` — data models are in code
- `test-plan/` — tests are the plan

If you find yourself wanting to update one of these: either you're in Heavy mode (where they exist) or you're trying to document what code already shows (don't).

### Step 3: Critic calibration

For each Critic finding from this slice's `critique.md`, score:

- **VALIDATED**: reality confirmed the Critic's concern
- **FALSE ALARM**: Critic flagged something that turned out fine
- **NOT YET**: deferred; can't score yet

ALSO note: **MISSED by Critic** — things that surfaced during build/validate that the Critic should have caught but didn't.

**Why this matters**: every 10-20 slices, `/critic-calibrate` reads these "Missed by Critic" entries across recent reflections, patterns them, and proposes targeted prompt updates to `critique/SKILL.md`. Be specific in the "Missed by Critic" entry — "Critic didn't flag EXIF orientation issue on iPhone HEIC uploads" beats "Critic missed something." Specific patterns produce specific prompt improvements.

This data accumulates over time and informs Critic prompt tuning across projects.

### Step 4: Write `architecture/slices/slice-NNN-<name>/reflection.md`

```markdown
# Reflection: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Shipped**: YES | YES-WITH-DEFERRALS | NO

## Validated
- <design claim> — validated by <test/observation>
- <design claim> — validated by <test/observation>

## Corrected
- <design claim> → reality is <actual> — updated in [[file]]
- <decision> → superseded by [[ADR-NNN]]

## Discovered
- <discovery> — impact: <what changes for next slices>
- <discovery> — added to risk register as [[R-NN]]

## Deferred
- <item> — reason: <why> — lands in: <next slice | backlog>

## Critic calibration
- B1 (<title>): VALIDATED — bug appeared exactly as flagged
- B2 (<title>): VALIDATED — caught during validation
- M1 (<title>): FALSE ALARM — turned out to be a non-issue because <reason>
- m1 (<title>): NOT YET — deferred

**Missed by Critic**: <things that surfaced during build/validate that Critic didn't flag>

**Pattern**: <observation about Critic accuracy for future tuning>

## Lessons for next slice
- <actionable insight>
- <actionable insight>

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — added R7 (...)
- [[decisions/ADR-NNN.md]] — finalized with library choice
- This slice's [[design.md]] — corrected async claim to sync (build-log notes the deviation)
```

(In Standard / Minimal mode, this list is short. No `components/X.md` updates because those files don't exist — code is the source of truth. If your reflection has lots of file updates, you might be in Heavy mode, OR you're documenting what code already shows.)

### Step 5: Append to `architecture/lessons-learned.md`

Append a chronological entry:

```markdown
## Slice NNN (<name>) — <YYYY-MM-DD>

### Worked
- <what about the design / process / approach worked>

### Didn't work
- <what didn't>

### Pattern
- <generalizable insight for future slices>
```

### Step 5.3: Add one entry to `architecture/shippability.md`

Every completed slice contributes ONE critical-path test to the shippability catalog. Future `/validate-slice` runs execute the full catalog to catch regressions.

Ask yourself: **"If this slice silently broke later, what's THE one test that would catch it first?"** That's the critical path for this slice.

Append to `architecture/shippability.md`:

```markdown
| <next-#> | slice-NNN-<name> | <one-line critical path> | `<runnable command>` | <expected runtime> |
```

Rules for the critical-path entry:

- **One line** describing the path (e.g., "POST /receipts accepts HEIC with EXIF orientation preserved")
- **Runnable command** (curl, pytest -k, bash script, cypress spec). Must work as-is from project root.
- **Expected runtime** — keep to <10 seconds per entry. Shippability runs add up; if a slice's critical path takes minutes, split it into a faster smoke + a thorough CI-only version.
- Must be TEST, not manual step. `/validate-slice` runs the catalog programmatically.

If `architecture/shippability.md` doesn't exist yet, create it with header:

```markdown
# Shippability Catalog

Critical-path tests from every slice. `/validate-slice` runs these at pre-finish to catch regressions introduced by the current slice breaking past slices' critical paths.

| # | Slice | Critical path | Command | Runtime |
|---|-------|--------------|---------|---------|
```

### Step 5.5: Refresh the knowledge graph

Code shipped this slice. Refresh graphify so the graph reflects current state:

```bash
# If /triage or /adopt installed the post-commit git hook: already done at commit time — skip.
# If --watch is running in another terminal: already done — skip.
# Otherwise:
$PY -m graphify code .   # rebuild is fast; CLI has no incremental --update flag
```

This keeps GRAPH_REPORT.md current. The next slice's `/design-slice` and `/critique` will query a fresh graph.

### Step 5.8: Update milestone.md to complete

Final update to `architecture/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: complete`, `updated: <today>`, `next-action: none (slice complete)`
- Check progress box: `- [x] /reflect — <date>`
- "Current focus": brief one-line ("Slice shipped. Lessons captured. Auto-archiving next.")
- All phase artifact statuses should now show complete/PASS/etc.

After this update, the immediate next step (Step 6) auto-moves the whole slice folder (including milestone.md) to `slices/archive/`. The archived milestone.md is a frozen snapshot — the "complete" state becomes permanent history.

### Step 6: Auto-archive this slice

The convention: `slices/` holds ACTIVE slices only; completed slices live in `slices/archive/` with lookup via `slices/_index.md`.

After writing `reflection.md`, this slice is complete. Archive it immediately:

1. `mv architecture/slices/slice-NNN-<name>/ architecture/slices/archive/`
2. Regenerate `architecture/slices/_index.md` — update the "Active" table (remove this slice), update the "Most recent 10" table (add this slice at the top), update "Aggregated lessons" (pull this slice's "Lessons for next slice" items)
3. Regenerate `architecture/slices/archive/_index.md` — append this slice to the chronological catalog

This is the same work as `/archive --index-only` but triggered automatically by slice completion. If you'd rather skip auto-archive and batch it later, explicitly tell the user: "Leaving slice in `slices/` — run `/archive` to sweep later." Only do this if the user requests it.

### Step 7: Preview next-slice candidates

Don't just say "run /slice next" — preview top candidates so the user sees what's on deck. This maintains continuity from reflection into next-slice planning.

Gather candidates from:
- This slice's **Discovered** items → candidates for addressing new risks
- This slice's **Deferred** items → candidates for completing deferred scope
- Recent `risk-register.md` active HIGH risks
- `concept.md` scope not yet built

Do a quick ranking (lightweight — `/slice` will do the full scoring):

```
Next-slice candidates (preview — run `/slice` for full scoring):

🏆 #1: <verb-object name>
   Reason: <one line — what risk it retires OR what deferred item it completes>

#2: <verb-object name>
   Reason: <one line>

#3: <verb-object name>
   Reason: <one line>
```

Keep it short — this is a preview, not the full ranked list. `/slice` does the deep work.

### Step 8: Close

State:
- "Reflection complete. Vault updates: <list files>."
- "Slice archived to `slices/archive/slice-NNN-<name>/`. Index refreshed."
- "Discoveries: <count> (added to risk register)."
- "Deferrals: <count> (surfaced above as slice candidates)."
- "Run `/slice` to formally select + define the next cut. I've previewed candidates above."

Archived slices are easy to find via `architecture/slices/_index.md`. Full catalog in `archive/_index.md`. Direct file access via `slices/archive/slice-NNN-<name>/` still works.

## Critical rules

- HONESTY DISCIPLINE: this is not a victory lap. Capture what didn't work, where you got lucky, where you're still guessing.
- UPDATE THE VAULT for every Corrected item. The vault must reflect reality, not the original design.
- DO NOT edit superseded ADRs. Decisions are append-only history.
- TRACK Critic accuracy every slice. This data compounds.
- IF discoveries section is empty across multiple slices: either you're not learning or not capturing. Push harder.

## Honesty discipline examples

GOOD reflection (honest):
> "Discovered: HEIC EXIF orientation issue. We got lucky that one user complained early; without that, sideways thumbnails would've been in production for weeks. Pattern: image-handling slices need EXIF awareness in mission brief."

BAD reflection (sales pitch):
> "All acceptance criteria passed. The team did a great job implementing the design as planned. No major issues."

The bad version teaches nothing for the next slice. The good version arms you for the future.

## Vault update examples

In Standard / Minimal mode (thin vault), most "behavior corrections" don't need vault edits — code IS the truth. But there are still cases:

**Decision wrong**: ADR-008 said "use SQS for async uploads"; you implemented sync. Don't edit ADR-008. Mark it `status: superseded`, create ADR-014 with `supersedes: ADR-008` documenting why sync now and when async planned.

**Risk claim wrong**: risk-register.md said "R3 retired by spike-002" but reality is R3 only retired for the simple case; complex case still risky. Update risk-register.md to reflect that nuance.

**Slice design wrong (vs what shipped)**: this slice's design.md said "async via SQS"; you shipped sync. Update this slice's design.md (the slice is the source of truth for what was decided/built). Also note in build-log.md: "Deviated from design — sync instead of async; rationale in reflection.md."

In Heavy mode (where `components/storage-service.md` exists): also update that file. But Heavy mode is the exception, not the default.

## Next step

`/slice` — define the next cut, informed by this slice's discoveries and deferrals.
