# Graphify Integration

How the AI SDLC pipeline uses graphify. Read this once; skills reference it.

## TL;DR

Graphify turns the codebase + vault + external references into a **queryable multi-modal knowledge graph**. Benefit: structural queries (reachability, blast-radius, orphans) and keyword search hit a pre-built index instead of scanning files. Every skill in this pipeline can query the graph for context instead of re-reading source.

## What graphify provides

### 1. Multi-modal graph building

```bash
$PY -m graphify <path>                    # build graph from code + docs
$PY -m graphify <path> --mode deep        # aggressive INFERRED edge extraction
$PY -m graphify <path> --update           # re-extract only changed files
$PY -m graphify <path> --watch            # auto-rebuild as files change
```

Inputs:
- **Code**: 25 languages via tree-sitter AST (Python, JS/TS, Go, Rust, Java, C/C++, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Dart, Vue, Svelte, and more)
- **Docs**: Markdown, HTML, reStructuredText, plaintext
- **Office**: .docx, .xlsx (converted to markdown)
- **Papers**: PDF with citation mining
- **Images**: PNG/JPG/WebP/GIF via vision models
- **Video/audio**: MP4/MOV/MKV/MP3/WAV transcribed locally with faster-whisper

Rationale comments (`# WHY:`, `# NOTE:`, `# IMPORTANT:`, `# HACK:`) are captured as graph edges — aligns with this pipeline's "why lives in vault, what lives in code" philosophy. Even the "why" scattered in code is queryable.

### 2. Query modes

```bash
$PY -m graphify query "what connects attention to optimizer?"   # natural language BFS
$PY -m graphify query "..." --dfs                               # path tracing
$PY -m graphify query "..." --budget 1500                       # token limit
$PY -m graphify path "NodeA" "NodeB"                            # shortest path
$PY -m graphify explain "NodeName"                              # plain-language explanation
```

Natural-language queries beat keyword grep for conceptual questions.

### 3. Edge confidence

Edges are tagged:
- `EXTRACTED` — found directly in source (confidence 1.0)
- `INFERRED` — reasonable inference with confidence score (0.0–1.0)
- `AMBIGUOUS` — flagged for human review

Critic persona uses this: INFERRED edges with low confidence = design assumptions to challenge.

### 4. Content enrichment

```bash
$PY -m graphify add https://arxiv.org/abs/...       # paper into graph
$PY -m graphify add https://example.com/design-doc  # external doc
$PY -m graphify add <video-url>                     # transcribe + add
$PY -m graphify add <url> --author "Name"           # attribution
```

`/discover` uses this to pull research papers, architecture docs, stakeholder interviews into the knowledge graph alongside code.

### 5. Claude Code integration (the always-on part)

```bash
$PY -m graphify install                   # base skill
$PY -m graphify claude install            # CLAUDE.md + PreToolUse hook
$PY -m graphify hook install              # post-commit + post-checkout git hooks
```

**PreToolUse hook**: fires before every Glob/Grep. When a knowledge graph exists, injects: "Knowledge graph exists. Read GRAPH_REPORT.md for god nodes and community structure before searching raw files." Redirects search from keyword-grepping to structure-aware navigation automatically.

**`GRAPH_REPORT.md`**: one-page digest auto-generated alongside `graph.json`. Contains god nodes (highest-degree concepts), community structure, surprising connections, suggested questions. This is the navigation layer — don't dump full `graph.json` into context.

**Git hooks**: post-commit runs the AST pass (instant, no LLM cost); post-checkout ditto. Doc changes notify the user to `$PY -m graphify <path> --update` for semantic re-extraction.

### 6. MCP server mode

```bash
python -m graphify.serve graphify-out/graph.json
```

Exposes graph.json as an MCP stdio server. Claude Code can then call `query_graph`, `get_node`, `get_neighbors`, `shortest_path` as tools instead of shell commands. More precise than pasting JSON.

## How AI SDLC pipeline uses graphify

### Installed by `/triage` and `/adopt`

Both project openers run (with user consent):

```bash
$PY -m graphify install                   # base skill — should already exist in ~/.claude/skills/graphify/
$PY -m graphify claude install            # PreToolUse hook + CLAUDE.md injection
$PY -m graphify hook install              # git hooks for auto-sync
$PY -m graphify .                         # initial graph build
```

After setup, every subsequent session has graph-aware search automatically.

### Per-skill usage

| Skill | Graphify usage |
|-------|---------------|
| `/triage` | Installs hooks + builds initial graph after vault skeleton |
| `/adopt` | Builds initial graph from existing code (`$PY -m graphify .`); uses the graph to reverse-engineer `concept.md` and identify major modules |
| `/discover` | Adds external references via `$PY -m graphify add <url>` (papers, design docs, interviews); queries existing graph for affected areas |
| `/risk-spike` | `$PY -m graphify query "what uses <risky-module>"` before designing the spike test |
| `/slice` | `$PY -m graphify query` for "related past slices" in candidate discovery; `$PY -m graphify path <current-slice-area> <rest-of-system>` for blast radius |
| `/design-slice` | `$PY -m graphify explain <module>` to understand existing code before designing; `$PY -m graphify path A B` for dependency check |
| `/critique` | Flags INFERRED / AMBIGUOUS edges the design depends on; runs `$PY -m graphify query` to find similar past contracts/components |
| `/build-slice` | In plan mode, `$PY -m graphify path <file> <affected-areas>` to see blast radius before editing |
| `/validate-slice` | — (runs on real environments, not graph) |
| `/reflect` | After slice completes, if `--watch` isn't running: `$PY -m graphify . --update` to refresh |
| `/drift-check` | Graph queries instead of file reads: `$PY -m graphify query "is library X in dependencies?"` + `$PY -m graphify path <ADR-claim> <code-location>` |
| `/heavy-architect` | Queries graph to auto-discover components + their dependencies; seeds `components/`, `contracts/`, `schemas/` from graph nodes |
| `/sync` | Heavy-mode bidirectional sync — regenerates `components/*.md` from graph nodes, `contracts/*.md` from OpenAPI/annotations surfaced via graph |
| `/reduce` | Identifies god nodes + speculative generality from graph structure |
| `/archive` | `graphify` remains authoritative for archived slices — they stay queryable |

### The always-on pattern

With `$PY -m graphify claude install` done at `/triage`/`/adopt` time:

1. User asks: "How does payment work?"
2. Claude's Glob/Grep would normally scan files
3. PreToolUse hook intercepts: "Knowledge graph exists. Read GRAPH_REPORT.md first."
4. Claude reads GRAPH_REPORT.md (one file, ~2k tokens) instead of scanning raw files (~100k+ tokens)
5. Finds "payment" community in the graph, the god nodes, the surprising connections
6. Answers with structure-aware reasoning

This happens transparently in every session. Nothing for the user to remember.

### Query patterns by skill

#### `/slice` candidate discovery

```bash
# Find related past slices
$PY -m graphify query "slices that touched payment"

# Find unbuilt concept scope
$PY -m graphify query "concepts mentioned in concept.md not in code"

# Blast radius of a candidate
$PY -m graphify path "slice-047-target-area" "auth-module"
```

#### `/design-slice` understanding existing code

```bash
# Plain-language module explanation
$PY -m graphify explain "receipt-service"

# Dependency understanding before locking design
$PY -m graphify path "new-component" "existing-storage-service"
$PY -m graphify query "what does receipt-service depend on?"
```

#### `/critique` attacking the design

```bash
# Find similar past contracts (pattern recognition)
$PY -m graphify query "past contracts with auth + pagination"

# Weak-link detection
$PY -m graphify query "INFERRED edges confidence<0.5 affecting this design"
```

#### `/build-slice` blast radius before editing

```bash
$PY -m graphify path "src/api/receipts.py" "src/auth/*"
```

If the path is surprisingly short (auth is directly imported by receipts handler), your design must explicitly consider auth; if long (many hops via utilities), it's more isolated.

#### `/drift-check` graph-based checks

```bash
# Does ADR-008's library still exist in deps?
$PY -m graphify query "is pyheif in dependency graph?"

# Does slice-042's referenced file still exist?
$PY -m graphify path "slice-042-design.md-claim" "src/api/payments.py"
```

## Setup details

### First-time install

```bash
# Ensure graphify is available (should be in ~/.claude/.venv or globally)
$PY -m graphify --version   # where $PY is your shared Python interpreter

# Base skill (one-time, registers in ~/.claude/skills/graphify/)
$PY -m graphify install

# Claude Code integration (per project)
cd your-project/
$PY -m graphify claude install        # injects CLAUDE.md section + PreToolUse hook
$PY -m graphify hook install          # post-commit + post-checkout git hooks

# Initial graph
$PY -m graphify .                     # builds graphify-out/graph.json + GRAPH_REPORT.md
```

Commit `graphify-out/` to version control so teammates inherit current graph state.

### Per-session conventions

- `GRAPH_REPORT.md` is ~always in context if PreToolUse hook is installed — check it before raw file search
- `graph.json` is queryable via `$PY -m graphify query`, `$PY -m graphify explain`, `$PY -m graphify path`
- `$PY -m graphify . --update` keeps graph current if git hooks aren't installed
- `$PY -m graphify . --watch` for long sessions with many file changes

### Multi-modal enrichment

```bash
# Research papers informing architecture
$PY -m graphify add https://arxiv.org/abs/2405.12345

# Team design docs
$PY -m graphify add https://docs.company.internal/architecture/v2

# Stakeholder interview recording
$PY -m graphify add ./interviews/kickoff-2026-04-15.mp4

# External API reference docs
$PY -m graphify add https://stripe.com/docs/api
```

All of these become graph nodes. `$PY -m graphify query` can then connect "our payment service" to "Stripe pagination patterns from the docs we added."

## Semantic archive retrieval — the slice-108 problem

As projects cross ~30 slices, `_index.md`'s "Aggregated lessons" and "Recent 10" only capture nearby history. A lesson from slice-008 can be relevant when designing slice-108, but is no longer in the index.

Graphify solves this without new tooling — archived reflections are already in the graph (it traverses `slices/archive/` by default). Just query semantically:

```bash
# When designing slice-108 that touches image handling
$PY -m graphify query "past lessons about image handling"
# → surfaces slice-023's EXIF orientation lesson, slice-045's HEIC edge cases, etc.

# When critiquing a design touching auth
$PY -m graphify query "past misses in auth-related slices"
# → surfaces patterns across any archived reflection, not just recent

# Before spiking a new integration
$PY -m graphify query "past spikes with OAuth scopes"
```

This is a usage pattern, not a new command. `/design-slice` and `/critique` both query semantically as part of their Step 0 / input-gathering. See those skills' SKILL.md for concrete query examples.

Bottom line: **`_index.md` = recent context; `$PY -m graphify query` = deep archive retrieval**. Use both; the index is in-context (free), the query is on-demand (~1.7k tokens).

## Performance characteristics

Graph-backed structural queries (reachability, blast-radius, shortest path, orphan detection) are sub-second even on large codebases — they read a pre-computed networkx graph rather than re-parsing files. Keyword `query "..."` returns a scoped BFS subgraph capped at a token budget (default 2000), avoiding full-corpus dumps.

Actual token savings vs. raw file scanning depend heavily on corpus shape, language mix, and query pattern — measure on your own corpus rather than relying on a single headline number.

## Privacy note

Graphify performs no telemetry. The only outbound call is the semantic-extraction step (uses your configured AI model API key); only semantic descriptions are transmitted, never raw source code. Runs locally otherwise.

## Where to read more

- [Graphify home](https://graphify.net/)
- [Knowledge graphs for AI coding assistants](https://graphify.net/knowledge-graph-for-ai-coding-assistants.html)
- [Claude Code integration](https://graphify.net/graphify-claude-code-integration.html)
- [GitHub repo](https://github.com/safishamsi/graphify)

## How this changes pipeline discipline

Before: vault is the AI's memory; code is the source of truth; skills read files.

After: vault is the AI's memory (unchanged); code is the source of truth (unchanged); **graph is the structural index over both** — queried first, raw files read only when needed. Same thin-vault philosophy; graph replaces N file reads with one query.

When the PreToolUse hook fires on every file search and redirects to GRAPH_REPORT.md, structure-aware reasoning becomes the default, not an opt-in. This is the biggest lift graphify provides.
