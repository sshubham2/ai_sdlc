---
name: heavy-architect
description: "Heavy mode only. Produces the comprehensive upfront architecture vault — components, contracts, schemas, threat model, cost estimation, test-plan index — required for compliance, regulated, or audit-grade projects. Runs once after /discover and /risk-spike, before slicing starts. Trigger phrases: '/heavy-architect', 'create the architecture upfront', 'compliance architecture', 'regulated project architecture'. Do NOT use in Standard or Minimal mode — those use per-slice design via /design-slice with no upfront comprehensive vault."
user_invokable: true
---

# /heavy-architect — Comprehensive Upfront Vault for Heavy Mode

You produce the comprehensive upfront architecture for Heavy mode projects — compliance, regulated, audit-grade. This is the one place in the AI SDLC pipeline where waterfall-style upfront design is correct, because compliance environments legitimately require comprehensive contracts, threat models, and audit artifacts before implementation begins.

## Where this fits

Runs after `/discover` and `/risk-spike` (all HIGH risks retired). Before `/user-test` (if B2C) and before `/slice` starts the build loop.

In Standard/Minimal mode: this skill DOES NOT RUN. Per-slice design via `/design-slice` is sufficient there. If a user invokes this in Standard mode, ask: "Are you sure this should be Heavy mode? `/triage --re-triage` if so."

## Prerequisite check

- Read `architecture/triage.md` — confirm `mode: Heavy`
- If mode is Standard or Minimal: STOP, suggest `/triage --re-triage` if Heavy is actually needed
- Read `architecture/concept.md`, `architecture/risk-register.md`, all `architecture/spikes/spike-*.md`, all `architecture/decisions/ADR-*.md`
- Read all `architecture/actors/<actor>.md` (Heavy mode has separate actor files)

## Your task

### Step 0: Seed from graphify if brownfield

If `/adopt` was run (brownfield) rather than `/triage` (greenfield): the codebase exists. Use graphify to auto-discover the component inventory BEFORE writing files:

```bash
$PY -m graphify code .                          # build code graph (CLI doesn't have a --mode deep flag)

# Plain-language description per top-level module (CLI lacks `explain`):
$PY -c "
import json, networkx as nx
G = nx.node_link_graph(json.load(open('graphify-out/graph.json')), edges='links')
hits = [n for n in G.nodes() if '<top-level-module>' in str(n)][:5]
for n in hits:
    print(n)
    print('  imports:', list(G.successors(n))[:8])
    print('  used by:', list(G.predecessors(n))[:8])
"

# God-node discovery — already pre-computed in the build:
cat graphify-out/CODE_REPORT.md | head -60

$PY -m graphify query "<keyword>"               # keyword match for finding modules
```

Read `graphify-out/GRAPH_REPORT.md` for god nodes + communities. Seed your component list from there — each god node typically maps to a component file. For each, a component file will describe WHAT (from graph) + WHY (from user).

For greenfield: skip this step; `/heavy-architect` generates from concept, not code.

### Step 1: Confirm scope with user

Before writing files, present a planned outline:

> "I'll produce the Heavy-mode comprehensive vault. This will include:
> - Components (one file per component, ~N components based on concept)
> - Contracts (one file per integration point, ~M contracts)
> - Schemas (shared entities, ~K)
> - Threat model (STRIDE per component)
> - Cost estimation (per-component infra + scaling curves)
> - Test plan index (will be populated per slice)
> - Requirements (functional + non-functional)
>
> Estimated work: 1-2 days. Confirm to proceed, or scope down."

Wait for confirmation. Heavy mode users sometimes want a subset — confirm before producing 30+ files.

### Step 2: Decompose into components

From the concept and actors, identify components. For each, define:

- **Single responsibility** (one sentence — if you can't, decompose further)
- **Public surface** (what other components / external clients see)
- **Internal state** (what it owns)
- **Dependencies** (other components, external services)
- **Failure modes** (what can go wrong, what blast radius)

Default to modular monolith or microservices. Recommend monolith only when scale + team + ops maturity clearly don't warrant distribution; document in an ADR if so.

### Step 3: Define contracts

For every integration point (component → component, component → external service):

- Method/path (REST) or event name (events)
- Request schema (with field types, required/optional, validation rules)
- Response schema (success + error responses with status codes)
- Auth model (how authn/authz is enforced)
- Versioning strategy
- Idempotency (where applicable)
- Rate limits / quotas (where applicable)

### Step 4: Define shared schemas

Entities referenced by multiple contracts go in `schemas/`:

- Field list with types
- Validation rules
- State machine (Mermaid diagram if entity has lifecycle)
- Indexes / constraints

### Step 5: Threat model (STRIDE)

For each component, walk the STRIDE checklist:

- **S**poofing — can an attacker impersonate this component or its users?
- **T**ampering — can data in transit / at rest be modified?
- **R**epudiation — can actions be denied without audit trail?
- **I**nformation disclosure — what data leaks if this component is compromised?
- **D**enial of service — what triggers DOS, what's the blast radius?
- **E**levation of privilege — can a low-privilege actor escalate?

For each finding, document mitigation.

### Step 6: Cost estimation

For each component, estimate infrastructure costs at three scales: 1K users, 10K users, 100K users.

- Compute (CPU/RAM/instances)
- Storage (DB, object storage, CDN)
- Network (egress, inter-AZ, CDN)
- Third-party services (auth, analytics, monitoring)

Total monthly cost per scale + per-user cost.

### Step 7: Test plan index

For each component and contract, list the test categories that must exist. Populate per slice during `/build-slice`. The index is the placeholder — actual test specs live in `architecture/test-plan/<area>.md` files populated as slices complete.

### Step 8: Requirements

Two files:

- `requirements.md` — functional requirements (what the system does, by actor)
- `non-functional.md` — latency, uptime, scalability, security posture, compliance constraints (specific regulations: HIPAA, PCI, SOC2, GDPR, etc.)

### Step 9: Write only the human-authored files

**Important change**: `/heavy-architect` no longer pre-generates `components/`, `contracts/`, `schemas/` files. Those are **derived from code** (via `/sync` on-demand) and trying to maintain them by hand between audits is fool's errand — they'll drift.

Write only the files that genuinely cannot be derived from code:

```
architecture/
  threat-model.md                # STRIDE per component (Step 5) — human rationale
  cost-estimation.md             # per-component infra costs (Step 6) — human estimate, not derivable
  requirements.md                # functional (Step 8) — human-authored intent
  non-functional.md              # NFRs + compliance — human-authored regulation mapping
  diagrams.md                    # Mermaid: system overview + sequence — human design intent
  actors/<actor>.md              # Heavy mode actor files with full role-play (Step 2 groundwork)
```

DO NOT create:
- `components/<name>.md` — derived from code via `/sync`
- `contracts/<name>.md` — derived from OpenAPI / route definitions / event annotations via `/sync`
- `schemas/<entity>.md` — derived from data models / migrations via `/sync`
- `test-plan/<area>.md` — tests are in code; plan is the shippability catalog

For components/contracts/schemas that need to exist as audit artifacts: tell the user to run `/sync` before audit to generate them from current code. Between audits, they don't exist — which is fine because the code IS the truth.

Every human-authored file uses frontmatter:

```yaml
---
type: threat-model | cost | requirement | non-functional | diagram | actor
date: <YYYY-MM-DD>
locked-at: heavy-architect
mode: Heavy
source: human-authored (vs code-derived which /sync produces)
---
```

**Why this design**: pre-generating 30+ markdown files for components/contracts/schemas violates the Thin Vault principle — they drift from code immediately. The honest approach: produce only irreducible human-authored content here; let `/sync` regenerate derived views on-demand when compliance needs them. Keeps Heavy mode honest without sacrificing audit artifacts.

Every file uses `[[wikilinks]]` to connect related items.

### Step 10: Build vault graph

After files are written, run graphify (if available) to build the vault graph:

```bash
$PY -m graphify vault architecture
```

This makes the comprehensive vault queryable for downstream skills.

### Step 11: Tell user what's next

Close with:

- "Heavy-mode comprehensive vault produced. <N> components, <M> contracts, <K> schemas. Threat model + cost estimation in place."
- "Run `/user-test mockup` next" (if B2C) — OR — "Run `/slice` to start building"
- "Reminder: in Heavy mode, every slice updates the comprehensive vault (components, contracts, schemas) inline. Use `/sync` periodically to reconcile vault and code."

## Component / contract / schema templates — handled by `/sync`, not this skill

The templates for code-derived artifacts (components, contracts, schemas) are owned by `/sync` — which generates them fresh from code when needed. This skill doesn't produce them, so the templates live with the tool that does.

For the human-authored artifacts this skill DOES produce, see each file's structure above (threat-model.md, cost-estimation.md, requirements.md, non-functional.md, diagrams.md, actors/).

## Critical rules

- VERIFY Heavy mode first. Don't run in Standard/Minimal.
- CONFIRM scope with user before writing 30+ files.
- DECOMPOSE: every component must have one-sentence responsibility. If you can't, split.
- DEFAULT modular: avoid monolith unless explicitly justified in an ADR.
- LINK heavily: `[[wikilinks]]` between components, contracts, schemas, threats, costs, requirements.
- TAG every file with frontmatter (type, date, mode, locked-at).
- BUILD graphify after writing — downstream skills depend on the graph.
- DO NOT skip threat model or cost estimation — these are compliance requirements in Heavy mode, not nice-to-haves.

## What this skill is NOT

- NOT a replacement for `/design-slice` — per-slice design still happens in Heavy mode, just inside the comprehensive vault scaffolding produced here
- NOT for Standard / Minimal mode — those use thin vault, no upfront comprehensive design
- NOT for greenfield experimentation — Heavy mode is for compliance / regulated / audit; if your project is exploratory, downgrade to Standard

## Heavy mode pipeline reminder

```
/triage (Heavy) → /discover (full) → /risk-spike (all HIGH) → /heavy-architect → /user-test (if B2C)
  → [per slice with audit trails:]
    /slice → /design-slice (updates components/contracts/schemas inline)
    → /critique (mandatory + human sign-off)
    → /build-slice (compliance trail)
    → /validate-slice (reproducible commands, timestamped, QA sign-off)
    → /reflect (full vault updates)
  → [every 5 slices:] /reduce (mandatory in Heavy)
  → /sync (periodic vault-code reconciliation)
```

## Next step

- B2C → `/user-test mockup`
- Otherwise → `/slice` to define slice 1
