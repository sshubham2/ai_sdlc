---
name: slice
description: "AI SDLC pipeline. Define the next thinnest valuable cut to build. Each slice = one vertical end-to-end cut delivered with verification. Selected by risk-first ordering. Use after /reflect (or after /discover for slice 1). Trigger phrases: '/slice', 'define next slice', 'plan next cut', 'what should we build next', 'next slice'. Produces a 1-page mission brief at architecture/slices/slice-NNN-<name>/mission-brief.md. Different from generic 'sprint planning' — slice is one cut, not a sprint."
user_invokable: true
argument-hint: [optional slice description or hint]
---

# /slice — Define the Next Cut

You are defining the next slice for the AI SDLC pipeline. A slice is one thin vertical cut — small enough to design, build, and validate in ≤1 day of AI implementation work, but big enough to retire risk or ship user-visible value.

## Where this fits

Runs after `/discover` (for slice 1) or after `/reflect` (for slice N+1). Output feeds `/design-slice`.

## Prerequisite check

Read the vault state:
- `architecture/triage.md` — exists? If not, run `/triage` (or `/adopt` for brownfield) first.
- `architecture/risk-register.md` — exists? If not, run `/triage` then `/discover` (or `/adopt`).
- `architecture/slices/_index.md` — THE primary source for past slices. Always read this.

Convention: `slices/` holds only active slices (no completed ones). All completed slices are in `slices/archive/` — found via `_index.md`. Don't scan individual archived slice folders by default.

**What to read for context**:
- `_index.md` "Active" table — any slices still in progress
- `_index.md` "Most recent 10" table — quick catalog of recently shipped work + one-line summaries
- `_index.md` "Aggregated lessons" section — patterns from recent reflections (this is your pattern-recognition input)

**When to go deeper**: only if a specific past slice is clearly relevant to the new candidate (e.g., "we're building 'add-csv-export-v2' and slice-045 was 'add-csv-export'" → read `archive/slice-045/reflection.md` specifically).

**First slice**: if `_index.md` doesn't exist yet, read `architecture/concept.md` (or `triage.md`) for first-slice candidate.

**Note on slice numbering**: new slice number = max(existing slice numbers including archive) + 1. Read `slices/_index.md` totals to get current max, or check `slices/archive/_index.md` if that's clearer. Numbers are globally unique across active + archived.

## Your task

### Step 1: Determine slice candidates

**Gather candidates from ALL these sources** — do NOT rely on the user to name the next slice:

1. **Risk register** (`architecture/risk-register.md`) — per **RR-1** (`methodology-changelog.md` v0.12.0), use the audit tool to get scored, sorted candidates instead of grepping for "HIGH" or "active":

   ```bash
   $PY -m tools.risk_register_audit architecture/risk-register.md \
     --json --filter-status open --sort score --top 5
   ```

   Top open high-band risks are first-priority slice candidates — the slice would retire them. Open medium-band risks are second-priority. Retired / accepted risks are excluded automatically. If the audit emits zero risks (legacy table format or empty file), fall back to grepping the file directly and flag for migration.
2. **Recent deferrals** (`slices/_index.md` "Aggregated lessons" + last 3 archived `reflection.md` files' "Deferred" sections): items deferred from prior slices are candidates
3. **Recent discoveries** (last 3 reflections' "Discovered" sections): new risks or gaps that surfaced during recent slices
4. **Concept scope not yet built** (`architecture/concept.md` — compare stated scope to `_index.md` catalog of shipped work): MVP features still unbuilt
5. **Aggregated lessons patterns** (`_index.md` "Aggregated lessons"): if a pattern suggests a slice ("we keep hitting X; should we fix X properly?"), surface it
6. **User-stated intent**: if `/slice "<description>"` was invoked with a description, that's a candidate — validate it against risks/value, don't auto-accept

**Use graphify queries** for richer candidate signals:

```bash
# Unbuilt concept scope — concepts mentioned but not in code
$PY -m graphify query "concepts in concept.md not yet in code"

# Related past slices — find slices that touched a related area (semantic, works across ALL archived slices, not just recent-10)
$PY -m graphify query "past slices that touched <area>"
$PY -m graphify query "past lessons about <candidate topic>"

# Dependency-blocked candidates — is a prereq missing?
# (CLI lacks `path`; use graphify-as-library)
$PY -c "
import json, networkx as nx
G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
try: print(' -> '.join(nx.shortest_path(G, '<candidate-feature>', '<required-prerequisite>')))
except Exception as e: print(f'no path: {e}')
"
```

Semantic archive retrieval catches relevant past slices even when you're on slice-108 and the match is slice-008 — the `_index.md` only lists recent-10, but `$PY -m graphify query` spans the full archive.

Build a list of 3-5 candidates minimum. Don't stop at 1 or 2 unless sources are exhausted.

### Step 2: Score each candidate

For each, rate on 4 axes. Be concrete — not just "HIGH / MEDIUM / LOW" but WHY:

| Axis | Rating | Rationale |
|------|--------|-----------|
| **Risk retired** | HIGH / MEDIUM / LOW / NONE | Which risk IDs; how much uncertainty does this eliminate? |
| **User value** | HIGH / PARTIAL / NONE | What does the user see/experience after this ships? |
| **Unblocks future work** | YES / NO | Does this open the door for other slices? |
| **Effort** | SMALL / MEDIUM / LARGE | Estimated in AI-hours (SMALL ≤ 2hr, MEDIUM ≤ 6hr, LARGE = 1 day or split) |
| **Prerequisites met** | YES / NO / PARTIAL | Are dependencies shipped? If NO, candidate is blocked |

**Ranking rule**: prioritize HIGH-risk-retired candidates with prerequisites met and SMALL-to-MEDIUM effort. User value breaks ties. A LARGE candidate with no user value is rarely the right next slice; consider splitting.

### Step 3: Actively recommend — don't just list

Claude recommends confidently. The user may not know what's next best; that's why this step exists.

Present the candidates as a **ranked recommendation**, not a menu. Example output:

```
Based on what's accumulated, here's my ranked recommendation for the next slice:

🏆 **#1 (recommended): enable-receipt-ocr-fallback**
   - Risk retired: R7 (HIGH) — OCR confidence gaps surfaced in slice-043, blocking the OCR feature shipping
   - User value: PARTIAL — user sees confidence score + "enter manually" fallback on low confidence
   - Unblocks: slice-046 (bulk receipt import), slice-047 (OCR analytics)
   - Effort: MEDIUM (~4 hours)
   - Prereqs: ✅ tesseract integration exists from slice-038

**#2: add-csv-export-filters**
   - Risk retired: none (incremental feature)
   - User value: HIGH — users requested date-range filter for exports
   - Unblocks: nothing new
   - Effort: SMALL (~2 hours)
   - Prereqs: ✅ all met
   - Note: deferred from slice-045

**#3: fix-thumbnail-exif-regression**
   - Risk retired: LOW (known bug, stable workaround exists)
   - User value: PARTIAL — quality improvement for iPhone users
   - Effort: SMALL (~1 hour)
   - Prereqs: ✅

My recommendation: #1. It retires the highest active risk AND unblocks two follow-on slices.

Want to go with #1, pick from #2/#3, or describe something else?
```

- Always produce a **🏆 recommended** candidate with a clear "why this one" line.
- Present 3-5 ranked alternatives.
- If the user invoked `/slice "<description>"` with a specific intent: evaluate it against the ranking; say explicitly if it's not the strongest candidate, and why. Don't just accept silently.
- If the user says "you pick" or "whatever": proceed with #1 without another round.

### Step 3b: If user has their own idea

If the user picks an option outside the ranked list (e.g., "actually, let's build X"):

- Validate it: score on the 4 axes above
- If the score is weak (no risk retired + low user value + high effort): raise the concern briefly ("that slice has low risk retirement; are you sure over #1?") — but respect the user's decision after one round
- Never silently build a weak slice without flagging

### Step 4: Define the slice

Once user agrees, define:

- **Name**: verb-object (`add-receipt-upload`, `enable-sync`, `fix-thumbnail-orientation`). NOT `phase-2`, `slice-N`, or vague nouns.
- **Risk tier**: **low / medium / high** (see Step 4a below) — controls whether `/critique` runs
- **Acceptance criteria**: testable, observable, ≤5 items.
- **Verification plan**: per criterion, exactly how it'll be checked (curl command, browser steps, device install).
- **Must-not-defer**: security, validation, error paths, observability, authorization.
- **Out of scope**: explicit non-goals.
- **Mid-slice smoke gate**: what to check at ~50% of build.
- **Pre-finish gate**: criteria all PASS + must-not-defer addressed + drift-check clean.

### Step 4a: Pick the risk tier

Ask the user (or propose if obvious from the candidate):

**Risk tier**: `low` | `medium` | `high`

- **Low**: pure CSS / styling / copy, docs-only, test additions to existing test files, formatter / linter fixes, single-package dep version bump with no API surface change. Critic may be skipped.
- **Medium** (the default): everything else that doesn't touch the "always mandatory" areas below.
- **High**: slice involves novel domain, first-time integration, or user explicitly wants extra scrutiny. Critic runs + re-critique after any design change.

**Always mandatory Critic** (regardless of tier — this field is "critic-required: true" in milestone.md):
- Auth / authz / permissions / login / tokens
- New API contracts or endpoint shapes
- Data model changes / migrations / schema
- Multi-device / multi-user / sync / sharing
- External integrations (OAuth, payment gateways, third-party APIs)
- Security-sensitive paths
- In-house methodology surfaces (`skills/*/SKILL.md`, `agents/*.md`, `tools/**/*.py`, `methodology-changelog.md`)
- Heavy mode (always)

When producing the mission brief and milestone.md: scan the slice's scope for these triggers. If any match, set `critic-required: true` even if tier is `low`. Tell the user explicitly: "Tier is low, but slice touches auth — Critic will run anyway."

> **Evidence for the In-house methodology surfaces trigger**: voluntary Critic on cross-cutting tooling slices has paid off N=9/9 across slices 1-9 in this project's reflection record (e.g., slice-006 INST-1 inventory drift; slice-007 install-time rename; slice-008 negative-anchor uniformity; slice-009 recursive self-application). Every voluntary Critic invocation on a cross-cutting tooling slice produced VALIDATED findings post-build with zero FALSE-ALARMs; see `architecture/slices/_index.md` "Aggregated lessons" and `archive/slice-NNN/reflection.md` "Critic calibration" sections for per-slice disposition records.

### Step 5: Scope check

Hard limits:
- ≤5 acceptance criteria
- ≤1 day of AI implementation work
- System remains shippable after the slice

If the slice exceeds these: split. Splitting that produces a slice with no user-visible value means the original "feature" is actually multiple features.

### Step 6: Write the mission brief + create milestone.md

Find the next slice number (if last slice was 003, this is 004).

Create:
- `architecture/slices/slice-NNN-<name>/mission-brief.md` using the template below
- `architecture/slices/slice-NNN-<name>/milestone.md` — initial rolling state file (see `~/.claude/templates/milestone.md` for the canonical shape)

### Initial milestone.md

Create with frontmatter + initial state:

```markdown
---
slice: slice-NNN-<name>
stage: slice
updated: <YYYY-MM-DD>
next-action: run /design-slice
risk-tier: <low | medium | high>
critic-required: <true | false>
---

# Milestone: slice-NNN <name>

**Stage**: slice
**Next action**: run `/design-slice`
**Updated**: <YYYY-MM-DD>
**Risk tier**: <tier> — <Critic required: yes | no (tier=low, no mandatory triggers)>

## Progress

- [x] /slice — <date>
- [ ] /design-slice
- [ ] /critique<if critic-required=false: " — skipped (risk-tier=low)">
- [ ] /build-slice
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Slice defined. Mission brief written. Ready for design.

## On resume

- **Last completed action**: /slice (mission brief and milestone created)
- **Current work**: none
- **Next immediate step**: run `/design-slice`

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md) — pending
- [critique.md](critique.md) — <pending | skipped>
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
```

Subsequent skills (`/design-slice`, `/critique`, `/build-slice`, `/validate-slice`, `/reflect`) update this file as they complete their phase. `/status` reads it as the primary source of active-slice state.

## Mission brief template

```markdown
# Slice NNN: <verb-object name>

**Mode**: <Minimal | Standard | Heavy>
**Estimated work**: <0.5 day | 1 day | split needed>
**Risk retired**: <which risk(s) from register this slice validates>
**Test-first**: <true | false>  (optional; per TF-1 — opt-in test-first variant)
**Walking-skeleton**: <true | false>  (optional; per WS-1 — opt-in walking-skeleton variant)
**Exploratory-charter**: <true | false>  (optional; per ETC-1 — opt-in charter-based exploratory testing)

## Intent

<2–3 sentences: what user-visible behavior ships with this slice, and why now>

## Acceptance criteria

1. <criterion 1 — testable, observable, one sentence>
2. <criterion 2>
3. <criterion 3>
4. (max 5)

## Test-first plan

(only when `**Test-first**: true`; per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | integration | tests/api/test_X.py | test_endpoint_accepts_input | PENDING |
| 1 | integration | tests/api/test_X.py | test_endpoint_rejects_oversize | PENDING |
| 2 | unit | tests/services/test_Y.py | test_normalize_payload | PENDING |

## Architectural layers exercised

(only when `**Walking-skeleton**: true`; per **WS-1**, `methodology-changelog.md` v0.15.0)

A walking-skeleton slice ships the thinnest end-to-end vertical that exercises every architectural layer. Real features layer onto the proven foundation. Statuses progress PENDING -> EXERCISED. `/validate-slice` Step 5c runs `tools/walking_skeleton_audit.py --strict-pre-finish` and refuses if any row is non-EXERCISED.

| # | Layer | Component | Verification | Status |
|---|-------|-----------|--------------|--------|
| 1 | Frontend | src/web/HomePage.tsx | Page loads in real browser | PENDING |
| 2 | API gateway | src/api/server.py | curl GET /healthz returns 200 | PENDING |
| 3 | Business logic | src/services/health.py | health_check() returns OK | PENDING |
| 4 | Persistence | src/db/health_log table | row inserted on /healthz call | PENDING |
| 5 | External | api.anthropic.com | trivial completions call returns 200 | PENDING |

## Exploratory test charter

(only when `**Exploratory-charter**: true`; per **ETC-1**, `methodology-changelog.md` v0.16.0)

Charter-based exploratory testing (Bach / Kaner / Hendrickson): each charter is a timeboxed mission ("Explore X using Y to find Z"); the tester runs the session freely within the timebox and captures findings. Surfaces what's NOT in the AC, unstated assumptions, edge cases the design didn't predict.

Statuses progress PENDING -> IN-PROGRESS -> COMPLETED (or DEFERRED with rationale). `/validate-slice` Step 5d runs `tools/exploratory_charter_audit.py --strict-pre-finish` and refuses any PENDING / IN-PROGRESS row; COMPLETED + DEFERRED both accepted.

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore HEIC upload edge cases using corrupted files to find error-handling gaps | 60min | PENDING | — |
| 2 | Explore concurrent uploads using 5 simultaneous requests to find race conditions | 45min | PENDING | — |

COMPLETED rows MUST have non-empty Findings (even if "no issues observed"). DEFERRED rows MUST carry a rationale in Findings.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | ... | `curl <url>` returns 200 with <schema> |
| 2 | ... | Open <page> in real browser, click <button>, observe <outcome> |

## Must-not-defer

- [ ] Input validation on <endpoint>
- [ ] Error handling for <failure mode>
- [ ] Authorization check on <protected action>
- [ ] Logging at <critical path>

## Out of scope

- <thing this slice deliberately won't do>
- <thing that's a different slice>

## Dependencies

- Prior slices: [[slice-NNN-name]] — <what we depend on>
- Vault refs: [[components/X]], [[decisions/ADR-NNN]]
- Risk register: [[risk-register#R1]]

## Mid-slice smoke gate

At ~50% of build, run:
```
<specific command or manual steps>
```
Expected: <outcome>. If fails: STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
```

## Critical rules

- ASK before deciding the slice. Present candidates, wait for user pick.
- ENFORCE scope limits. If a slice would take >1 day: split.
- VERB-OBJECT names only. No `phase-N` or `slice-N`.
- INCLUDE must-not-defer EVERY slice — even trivial ones (auth, logging, validation).
- DO NOT design the slice here. That's `/design-slice`. Mission brief is the WHAT, not the HOW.

## Anti-patterns for slice 1

- "Set up the database" — no user value, no risk retired
- "Build the login page" — unless auth IS the risk
- "Implement basic CRUD" — too broad
- "Scaffold the project" — that's setup, not a slice

## Good slice 1 examples

- "Validate Drive cross-account sync end-to-end with 2 devices" — retires huge risk, demonstrable
- "Capture and upload one receipt with thumbnail" — exercises storage stack, demonstrable
- "Send one push notification to a real device" — exercises FCM/APNs path

## Next step

`/design-slice` — turn the mission brief into a just-enough spec.
