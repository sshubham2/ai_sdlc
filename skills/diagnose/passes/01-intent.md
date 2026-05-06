# Pass 01 — Intent reconstruction

You reconstruct what this codebase is **trying to be** from raw code. No README, no docs.

## Inputs
- `TARGET` — path to the repo being diagnosed
- `OUT` — path to `diagnose-out/`
- `OUT/graphify-out/CODE_REPORT.md` — graph hotspots, communities

## Hard rules
- **No documentation reads.** Do not read any `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` files or anything in a `docs/` directory in `TARGET`. Source code, config (`.yaml`, `.toml`, `.json`, `.env`), schemas, build manifests, and graphify only. Inline docstrings/comments may be read but not trusted as ground truth.
- Do not modify any file in `TARGET`. Only write to `OUT/sections/`, `OUT/findings/`, `OUT/summary/`.
- Findings (none expected for this pass) must conform to `~/.claude/skills/diagnose/schema/finding.yaml`.

## Method

1. Identify entry points: `main`, `index`, route definitions, CLI entrypoints, server startup, queue workers, scheduled jobs.
2. Identify route handlers / public API surface. List endpoints, their methods, what data they accept/return.
3. Identify primary data models / entities. Names, fields, relationships.
4. Identify user-facing strings: error messages, UI labels, log messages — these reveal *who the user is* and *what they're being told*.
5. Identify external integrations: third-party APIs, queues, databases, payment providers — each integration is a clue to capability.
6. Synthesize: in 2-3 paragraphs, **what is this system trying to do, and for whom?**
7. List inferred actors with one line each (role + how they interact with the system).
8. List the capability map: 5-15 verb-phrase capabilities the system delivers (e.g., "schedule recurring payments", "export account statements as PDF").

## Use graphify

```bash
$PY -m graphify query "main entry routes handlers" --graph $OUT/graphify-out/graph.json
$PY -m graphify query "models entities domain" --graph $OUT/graphify-out/graph.json
$PY -m graphify query "external api integration client" --graph $OUT/graphify-out/graph.json
```

## Output files

### `OUT/sections/01-intent.md`

```markdown
## 1. What the codebase does

### Inferred intent
<2-3 paragraphs>

### Actors
- **<actor>** — <role>; interacts via `<surface>` (`<file:line>`)
- ...

### Domain model
<table or list of primary entities, fields, relationships>

### Capability map
- <verb phrase capability> — `<file:line>` evidence
- ...

### External integrations
- <service>: `<file:line>`, purpose
- ...
```

### `OUT/findings/01-intent.yaml`

```yaml
[]
```

(Pass 01 produces no findings — it's prose only.)

### `OUT/summary/01-intent.md`

One paragraph, ~80 words: "This codebase appears to be a <type> for <users>, primarily delivering <top 3 capabilities>. Built on <stack>. <One sentence on what's distinctive or surprising about the inferred intent>."

## Anti-patterns

- Don't quote the README. Don't quote design docs. Code only.
- Don't speculate about future intent — only what current code implements.
- If the codebase has no clear entry point (library or framework code), say so explicitly in the prose and degrade actors/capabilities to "consumers of API X".
