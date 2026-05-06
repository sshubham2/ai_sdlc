# Pass 02 — Architecture mapping and judgment

You describe the **current architecture as observed in code**, then judge it for fitness against the inferred intent (which is also derivable from code — do not read pass 01's output).

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`
- `OUT/graphify-out/CODE_REPORT.md` — god nodes, communities, hotspots

## Hard rules
- **No documentation reads.** Do not read any `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` files or anything in a `docs/` directory in `TARGET`. Source code, config (`.yaml`, `.toml`, `.json`, `.env`), schemas, build manifests, and graphify only. Inline docstrings/comments may be read but not trusted as ground truth.
- Do not modify any file in `TARGET`.
- Recommendations must be specific, evidence-backed, and tagged keep/modify/drop.

## Method

1. **Components.** Use graphify communities + topo-sort to identify the structural components (modules / layers / services). Name each, describe its responsibility from its code, list its in-edges and out-edges.
2. **Data flow.** Trace one or two primary user-facing flows from entry point through layers to persistence and back. State the path concretely (file → file → file).
3. **Stack.** Languages, major frameworks, persistence, queues, deployment hints (Dockerfile, k8s manifests, serverless configs).
4. **Where the code agrees with itself.** Patterns that are consistently applied: e.g., "all controllers use the service layer; all services use the repository layer." This is the implicit contract.
5. **Where the code disagrees with itself.** Modules that bypass the otherwise-consistent pattern. (These also become findings in pass 03f, but mention them here at architectural level.)
6. **Architecture judgment.** Is the architecture appropriate for what the system does? Is it over-engineered for its scope? Under-engineered? What's load-bearing?
7. **Recommendations.**
   - **KEEP** — strengths to preserve through any refactor (3-7 items, with rationale).
   - **MODIFY** — structural changes worth making (3-7 items, with rationale + concrete what).
   - **DROP** — parts that aren't earning their keep (0-5 items, with rationale).

## Use graphify

```bash
$PY -m graphify topo-sort --graph $OUT/graphify-out/graph.json
$PY -m graphify query "<component-keyword>" --graph $OUT/graphify-out/graph.json
$PY -m graphify reachable --from=<entry-file> --graph $OUT/graphify-out/graph.json
```

Read `OUT/graphify-out/CODE_REPORT.md` for community structure.

## Output files

### `OUT/sections/02-architecture.md`

```markdown
## 2. Architecture

### 2.1 Current architecture (as observed)

**Components:**
| Component | Responsibility | Key files |
|-----------|----------------|-----------|
| ... | ... | ... |

**Data flow (primary path):**
<concrete trace>

**Stack:** <list>

**Where the code agrees with itself (implicit contract):**
- <observed consistent pattern>
- ...

**Where the code disagrees with itself:**
- <selective bypass>
- ...

### 2.2 Architecture judgment

<2-4 paragraphs assessing fitness, over/under-engineering, load-bearing parts>

### 2.3 Recommendations

**KEEP** (preserve through any refactor):
- <strength + rationale + evidence>
- ...

**MODIFY** (structural changes worth making):
- <change + rationale + concrete what>
- ...

**DROP** (parts not earning their keep):
- <part + rationale>
- ...
```

### `OUT/findings/02-architecture.yaml`

```yaml
[]
```

(Architectural recommendations live in the prose, not as findings. Code-level findings come in 03* passes.)

### `OUT/summary/02-architecture.md`

One paragraph, ~80 words: stack at a glance, dominant architectural pattern, main strength, main structural concern, overall fit-for-purpose verdict (well-fit / over-engineered / under-engineered / drifting).

## Anti-patterns

- Don't generate generic architecture advice ("consider microservices"). Recommendations must be tied to evidence in this codebase.
- Don't list every component as KEEP. Be opinionated; skipping a section is fine if there's nothing real to say.
- Don't recommend rewrites. Recommendations should be incremental.
