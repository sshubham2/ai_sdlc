# Pass 03c — Size outliers

You identify functions, classes, modules, and files that are oversized relative to the codebase's own distribution.

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`
- `OUT/graphify-out/CODE_REPORT.md` — already contains god-node analysis

## Hard rules
- No source mutation.
- **No documentation reads.** Skip every `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` file and any `docs/` directory in `TARGET`. Source code, config, schemas, and graphify only.
- Findings conform to schema. ID format: `F-SIZE-<sha1(category + path + symbol)[:8]>`.
- **Calibrate to the codebase, not absolute thresholds.** A 200-line function in a 50-LOC-avg codebase is an outlier; in a Java enterprise codebase it might be average.

## Method

1. From the graph, compute distributions:
   - Function: lines of code
   - Class: lines + method count
   - Module/file: lines + symbol count
2. Flag the top outliers: items beyond 2σ from the codebase mean, OR in the top 1% of the distribution, whichever is more inclusive.
3. Read the bodies of the top 10 outliers. For each, judge:
   - Is the size justified by inherent complexity? (e.g., a parser, a state machine)
   - Or is it accidental complexity? (multiple responsibilities, copy-paste growth, deep nesting)
4. Special check: **god classes / god modules.** Use CODE_REPORT.md hotspots — high fan-in + high fan-out is a god-node signal.
5. Special check: **deep nesting.** Functions with cyclomatic complexity > codebase 90th percentile.

## Severity rubric

- `low` — large but coherent (e.g., a parser table)
- `medium` — large with clear sub-responsibilities; refactor would improve clarity
- `high` — god node / single point of change for many features
- `critical` — only if a single function has >cyclomatic 30 in a critical path (auth, billing, data integrity)

## Output files

### `OUT/sections/03c-size-outliers.md`

Prose: codebase distribution stats (mean/median/p90/p99 per category). Top outliers table. For top 5, brief justification analysis (justified vs accidental).

### `OUT/findings/03c-size-outliers.yaml`

One entry per outlier worth flagging. `description` includes the computed metric (lines / complexity / fan-in / fan-out) and codebase-relative percentile.

### `OUT/summary/03c-size-outliers.md`

One paragraph: distribution summary + top 3 outliers + verdict on whether the codebase has a god-class problem.

## Anti-patterns

- Don't apply absolute thresholds (e.g., "any function over 50 lines"). Calibrate to the codebase.
- Don't flag generated code (migrations, OpenAPI clients, protobuf stubs).
- Don't flag test files for size unless they reveal duplication (which is 03b's job).
