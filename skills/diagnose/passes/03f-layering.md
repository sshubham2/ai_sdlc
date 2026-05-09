# Pass 03f — Layering violations / selective bypass

You identify places where the codebase's dominant layering pattern is selectively bypassed.

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`

## Hard rules
- No source mutation.
- **No documentation reads.** Skip every `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` file and any `docs/` directory in `TARGET`. Source code, config, schemas, and graphify only.
- Findings conform to schema. ID format: `F-LAYER-<sha1(category + violator_path + bypassed_layer)[:8]>`.
- **Establish the dominant pattern first**, then flag deviations. Don't import external best practices.

## Method

1. **Infer the layering pattern.** Look at the majority behavior:
   - Do most controllers/handlers go through a service layer? Through a repository layer to reach DB?
   - Does the codebase use middleware for auth uniformly? For request parsing?
   - Is there an event bus / queue most async work goes through?
   - Is direct DB access concentrated in one module?
2. **Flag the minority that bypasses.** Examples:
   - 4/5 controllers call `UserService.get`, but one controller calls the DB directly.
   - 6/7 producers send via the queue, but one calls the consumer in-process.
   - All routes go through the auth middleware, but two have it disabled with no recorded reason.
3. **Distinguish intentional from accidental bypass:**
   - Intentional: explicit comment, matches a known requirement (e.g., "health check must not query DB"), part of a documented module exception.
   - Accidental: no comment, no obvious reason, looks like the implementer just didn't know.
4. Use `graphify topo-sort` to confirm the layer order:
   ```bash
   $PY -m graphify topo-sort --graph $OUT/graphify-out/graph.json
   ```

## Severity rubric

- `low` — cosmetic layering inconsistency
- `medium` — bypass of service or repository layer
- `high` — bypass of auth, validation, or transaction boundary
- `critical` — bypass of a security-critical layer (authn, authz, audit logging)

## Output format

Per ADR-001 (slice-001) + slice-002, return your output as three 4-backtick fenced blocks in your final message. **Do NOT call Write to produce output files (the orchestrator handles that). You MAY use Bash/python for graphify queries within $OUT/graphify-out/, and Read/Grep/Glob for source files within $TARGET.**

### Schema crib sheet (for the `findings` block)

- `id`: `F-LAYER-<8hex>` · `pass`: `03f-layering` · `category`: `layering-violation`
- `severity`: `low | medium | high | critical` · `blast_radius`: `small | medium | large` · `reversibility`: `cheap | expensive | irreversible`
- `title`: ≤100 chars · `description`: include dominant pattern + specific deviation
- `evidence`: list of `{path, lines, note}` · `suggested_action` · `effort_estimate`: `small | medium | large` · `slice_candidate`: `yes | no | maybe`

Empty findings: return `[]`.

### Block contents

**`section` block** — Prose: state the inferred dominant layering pattern (with evidence: "X out of Y controllers follow this"). Then list each deviation, what layer it bypasses, and the apparent reason or absence of one.

**`findings` block** — One entry per violation. `description` must include the dominant pattern reference and the specific deviation.

**`summary` block** — One paragraph: dominant pattern + violation count + worst violation.

### Block template

`````
````section
<your section content>
````

````findings
<YAML list, or `[]`>
````

````summary
<your one-paragraph summary>
````
`````

## Anti-patterns

- **Don't apply external "best practices."** If the codebase has no service layer at all, don't flag controllers calling the DB directly — that's the codebase's pattern.
- Don't flag the first/only place a pattern appears — there's no dominant pattern to violate.
- Don't flag adapter/bridge code that explicitly translates between two layered worlds.
