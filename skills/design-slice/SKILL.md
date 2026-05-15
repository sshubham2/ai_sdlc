---
name: design-slice
description: "AI SDLC pipeline. Just-enough spec for the current slice — not full architecture. Defines components touched, contracts added, decisions made, dependencies. Lock expensive decisions only when this slice needs them. Use after /slice, before /critique. Trigger phrases: '/design-slice', 'design this slice', 'spec the current slice', 'design the slice'. Reads architecture/slices/slice-NNN/mission-brief.md. Per-slice design, not whole-system; for Heavy-mode upfront vault, use /heavy-architect."
user_invokable: true
---

# /design-slice — Just-Enough Spec for One Cut

You are designing the current slice. NOT full architecture. ONLY what THIS slice needs to ship.

## Where this fits

Runs after `/slice` (mission brief exists). Output feeds `/critique` (separate Critic agent reviews).

## Prerequisite check

- Find the active slice (latest `architecture/slices/slice-NNN-*/` folder)
- Read `mission-brief.md` — if missing, run `/slice` first
- Read existing vault context (components, decisions, prior slices)

If the project uses graphify, query the vault graph for relevant context. Otherwise read directly.

## Your task

### Step 0: Use graphify for context (before designing)

Before ANY design writing, query the graph to understand the affected area:

```bash
# Keyword search across the graph (substring match on labels — not semantic)
$PY -m graphify query "<module-name>"
$PY -m graphify query "what uses <module>?"

# Reachability — what does this module depend on (transitively)?
$PY -m graphify reachable --from="<module-name>"

# Blast radius — what depends on this module (reverse reachability)?
$PY -m graphify blast-radius --from="<module-name>"

# Shortest path between two nodes (uses graphify-as-library since CLI lacks `path`):
$PY -c "
import json, networkx as nx
G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
try: print(' -> '.join(nx.shortest_path(G, source='<file-or-module>', target='<adjacent>')))
except Exception as e: print(f'no path: {e}')
"

# Plain-language node summary (CLI lacks `explain` — render in/out edges directly):
$PY -c "
import json, networkx as nx
G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
hits = [n for n in G.nodes() if '<module-name>' in str(n)][:5]
for n in hits:
    print(n)
    print('  imports:', list(G.successors(n))[:8])
    print('  used by:', list(G.predecessors(n))[:8])
"
```

Read `graphify-out/GRAPH_REPORT.md` — the one-page digest has god nodes, communities, and surprising connections. Faster than grepping raw files.

**Keyword archive retrieval** — for projects with many slices. The archive at `slices/archive/` contains every past reflection; if the vault graph was built with `$PY -m graphify vault architecture`, those reflections are queryable. Note: `query` is keyword substring matching on node labels, not semantic similarity — use the topic word literally.

```bash
# Find past slices/reflections whose label contains a topic keyword
$PY -m graphify query "<topic>" --graph graphify-out/vault-graph.json
# Example: query "EXIF" finds slice-023's EXIF lesson if "EXIF" appears in its label or path.
# Won't find conceptual matches without the literal word — fall back to grep -ri "<concept>" architecture/slices/archive/ for those.

# Pull specific relevant reflection(s) for full detail
cat architecture/slices/archive/slice-NNN-<name>/reflection.md
```

Don't rely on `_index.md` alone past slice ~30 — keyword query catches files past the recent-10.

If the graph is missing or stale: `$PY -m graphify code .` (rebuild is fast).

### Step 1: Identify what's new for this slice

Compare mission brief to existing vault + existing code (via graph queries above). List:
- New components needed (or modifications to existing)
- New contracts (endpoints, events, schemas)
- New data model fields / entities
- New decisions that lock with this slice (ADRs)

Don't list things this slice doesn't touch. The vault grows with the system, not ahead of it.

### Step 2: Ask 2-4 clarifying questions max

Only ask about real ambiguity in the mission brief. Examples of legitimate questions:

- "Should receipts be stored as DB blobs or in object storage?"
- "Is this entity editable after creation, or append-only?"
- "Who can read this — owner only, or household members?"
- "Do we need an audit log for these reads?"

Examples of bad questions:
- "How should we handle errors?" — that's the Builder's job, not a design question
- "What testing framework?" — not a slice-level decision
- "Database name?" — bikeshedding

If the mission brief is clear, skip this step.

### Step 3: Tag every new ADR with reversibility

For each decision this slice locks:

```yaml
---
id: ADR-NNN
title: <one sentence>
date: <YYYY-MM-DD>
slice: slice-NNN-<name>
reversibility: cheap | expensive | irreversible
status: proposed | accepted | superseded
supersedes: null | ADR-NNN
---
```

- **cheap**: UI tokens, log format, library swap that's a 1-hour change → lock now
- **expensive**: framework, DB engine, contract shape with multiple consumers → only lock if THIS slice needs it
- **irreversible**: identity model, tenant model, primary entity shape → only after `/risk-spike` confirmation

If a decision could wait: defer it. Don't lock it preemptively.

### Step 4: Write `architecture/slices/slice-NNN-<name>/design.md`

The thin vault philosophy applies: **reference code locations, don't duplicate them**. Don't write out full request/response JSON schemas if they live in `models.py`; reference the file. Don't enumerate every method on a class if the interface is in code; reference the file + class.

```markdown
# Design: Slice NNN <name>

**Date**: <YYYY-MM-DD>
**Mode**: <from triage>

## What's new
<bulleted list of what this slice introduces — files to create, behavior to add>

## What's reused
<bulleted list of existing code/decisions this slice depends on, with [[wikilinks]] for vault items and `path/to/file.py` for code>

## Components touched

### <new or modified component>
- **Responsibility**: <one sentence — WHAT it does, WHY it exists>
- **Lives at**: `path/to/file.py` (created by this slice) or `path/to/existing.py` (modified)
- **Key interactions**: <other modules / services / external APIs it talks to>

(In Heavy mode only: also include public surface enumeration, internal data structures, full dependency list.)

## Contracts added or changed

### <new endpoint or event>
- **Endpoint/event**: `POST /receipts` or `event:receipt.uploaded`
- **Defined in code at**: `path/to/file.py` (or "to be created")
- **Auth model**: <how auth/authz is enforced — reference middleware / decorator>
- **Error cases**: <which conditions, which status codes — reference where they're raised>

(Don't duplicate request/response schemas here. They live in code as Pydantic models / TypeScript interfaces / OpenAPI annotations. Reference them: "see `ReceiptUploadRequest` in `src/api/receipts.py`".)

## Data model deltas

### <new entity or field addition>
- **Defined in**: `path/to/migration.sql` or `path/to/model.py`
- **What's new**: <one-line summary; the schema lives in code>
- **Validation / constraints**: <reference where these are enforced — DB constraint, Pydantic validator, etc.>

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale. Empty cells without exemption are refused at `/build-slice` pre-finish.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `src/services/<example>.py` | `src/api/<entry>.py` | `tests/test_<entry>.py::test_<scenario>` | — |
| `src/utils/_<helper>.py` | — | — | `internal helper, no consumer demanded — rationale: shared by other _utils modules` |

If this slice introduces no new modules (e.g., config-only or refactor of existing files): keep the header + separator only — the audit treats zero-row matrices as clean.

The `Exemption` cell, if used, MUST contain the substring `rationale:` followed by the actual reason. The audit checks for it.

## Decisions made (ADRs)
- [[ADR-NNN]] — <one-sentence summary> — reversibility: <tag>

## Authorization model for this slice
<how this slice's actions are authorized — explicit, not implied>

## Error model for this slice
<which error codes this slice introduces, what triggers each>
```

### Step 5: Write new ADRs (one file per decision)

`architecture/decisions/ADR-NNN-<short-name>.md`:

```markdown
---
id: ADR-NNN
title: <decision in one sentence>
date: <YYYY-MM-DD>
slice: slice-NNN-<name>
reversibility: cheap | expensive | irreversible
status: accepted
---

# ADR-NNN: <title>

## Context
<why this decision is needed now>

## Options considered
1. <option> — pros / cons
2. <option> — pros / cons

## Decision
<chosen option, in one paragraph>

## Consequences
<what changes downstream — components affected, contracts implied, future flexibility>

## Reversibility
<why this is tagged the way it is — what cost would be incurred to change>
```

### Step 6: Heavy mode only — update component / contract files

In Heavy mode (compliance / regulated): also create or update `architecture/components/<name>.md` and `architecture/contracts/<name>.md` for components/contracts this slice introduces or substantively changes. These serve as audit artifacts.

In Standard / Minimal mode: SKIP this step. Code is the source of truth; no separate component/contract files exist. The slice's `design.md` references code locations and that's enough.

### Step 6b: Update milestone.md

Update `architecture/slices/slice-NNN-<name>/milestone.md`:

- Frontmatter: `stage: design`, `updated: <today>`, `next-action: run /critique` (or `run /build-slice` if `critic-required: false`)
- Check progress box: `- [x] /design-slice — <date>`
- "Current focus" section: brief summary of the design (what's new, what components touched)
- "On resume": last action = /design-slice complete; next immediate step = /critique or /build-slice

If the slice's scope expanded during design and now touches a mandatory Critic trigger (auth, contracts, data model, etc.) that `/slice` missed: update `critic-required: true` in frontmatter and flag to the user: "Slice scope expanded to touch X; Critic is now mandatory even though tier is low."

### Step 7: Confirm and hand off

Tell the user:
- "Design complete for slice NNN. Files: design.md, ADR-NNN-* (count), component-X updated."
- "Run `/critique` next to have the Critic review before build."

## Critical rules

- DO NOT spec components this slice doesn't touch.
- DO NOT define contracts for endpoints this slice doesn't add.
- DO NOT write test specs (acceptance criteria in mission brief are enough).
- DO NOT lock decisions this slice doesn't need (defer them).
- DO NOT duplicate code in design.md — REFERENCE code locations (`see src/api/X.py`).
- DO NOT create `components/`, `contracts/`, `schemas/` files in Standard / Minimal mode (thin vault). Heavy mode only.
- ASK clarifying questions only about real ambiguity. ≤4 questions.
- TAG every ADR with reversibility. No untagged decisions.
- IN HEAVY MODE: comprehensive vault (components, contracts, schemas, threat model, cost estimation) is produced ONCE by `/heavy-architect` before slicing starts. This skill (per-slice design) updates those files inline as the slice introduces new components/contracts/schemas. It does NOT produce the upfront architecture — that's `/heavy-architect`'s job.

## Anti-patterns

- Speculative interfaces ("this might be reused later")
- Pre-defined contracts for "phase 2" features
- ADRs for trivial choices (kebab-case naming, etc.)
- Component files written but never used by any slice

## Heavy mode behavior (updated)

In Heavy mode, `/heavy-architect` produces only the human-authored files (threat-model, cost-estimation, requirements, NFRs, diagrams, actors). It does NOT pre-generate `components/`, `contracts/`, or `schemas/` — those are code-derived and generated on-demand by `/sync` when audits need them.

Per-slice `/design-slice` in Heavy mode:
- Writes the slice's own `design.md` referencing code locations (same as Standard mode)
- Updates `threat-model.md` if the slice changes attack surface (human-authored; needs maintenance)
- Updates `cost-estimation.md` if the slice changes infra footprint (human-authored)
- **Does NOT** update `components/<name>.md` / `contracts/<name>.md` / `schemas/<entity>.md` — those don't exist between `/sync` runs. They'll be regenerated fresh at the next `/sync` from current code.

In Standard / Minimal mode: thin vault applies. Per-slice design writes only `slices/slice-NNN/design.md`, referencing code locations.

**Why this change**: previously Heavy mode's `/design-slice` had to keep 30+ files synced with every code change — drift nightmare. Now code-derived views are transient (regenerated by `/sync`); human-authored files are rare and stable. Heavy mode is lean between audits.

## Next step

`/critique` — adversarial review by separate Critic AI persona.

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: once design.md + any ADRs are written, invoke `/critique` via the Skill tool without waiting for the user. (If the slice is low-tier with `critic-required: false`, the chain still routes through `/critique`, which self-skips per its own mode/tier gate and auto-advances onward.)
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Real design ambiguity → Step 2 clarifying questions (≤4) — HALT. No clean-path plan-mode here (plan mode belongs to `/build-slice`).

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Next step` section above is the human-readable companion; this block is the machine-actionable auto-advance directive. Manual invocation remains supported.
