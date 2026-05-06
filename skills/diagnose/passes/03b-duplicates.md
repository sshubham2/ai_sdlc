# Pass 03b — Duplicate detection (literal + semantic)

You identify duplicated code: both literal/AST duplicates and **semantic** duplicates (different code shape, same purpose).

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`

## Hard rules
- No source mutation.
- **No documentation reads.** Skip every `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` file and any `docs/` directory in `TARGET`. Source code, config, schemas, and graphify only.
- Findings conform to schema. ID format: `F-DUPE-<sha1(category + canonical_path + signature)[:8]>` where `canonical_path` is the lexicographically smallest path among the duplicates.

## Method

### Literal/AST duplicates
1. Look for token sequences ≥30 tokens that appear in 2+ locations.
2. Use heuristics: identical function bodies (modulo identifiers), copy-pasted blocks within a function repeated across functions, near-identical files (e.g., `users_v1.py` and `users_v2.py`).
3. Skip: trivial getters/setters, generated code (look for "DO NOT EDIT" headers), test fixtures duplicated by design.

### Semantic duplicates (the AI-bloat signal)
1. Use `graphify query` with capability keywords to cluster functions touching similar data:
   ```bash
   $PY -m graphify query "fetch user by id" --graph $OUT/graphify-out/graph.json
   $PY -m graphify query "validate email format" --graph $OUT/graphify-out/graph.json
   $PY -m graphify query "send notification email" --graph $OUT/graphify-out/graph.json
   ```
2. For each cluster of >1 function, read the bodies and judge: are they doing the same thing differently? Concrete equivalence checks:
   - Same input shape, same output shape, same side effects?
   - Same SQL table touched / same external API called?
   - One calls the other? (Then it's not a dupe, it's a wrapper.)
3. If equivalent: flag the cluster, name a canonical implementation, list the others as duplicates of it.
4. Common semantic-dupe patterns to actively look for:
   - Two HTTP clients for the same external API
   - Two date-parsing helpers
   - Two implementations of "fetch user by ID" with diverging cache behavior
   - Two slug/identifier generators
   - Two retry / backoff utilities
   - Two pagination implementations

## Severity rubric

- `low` — cosmetic dupe (small helpers); cleanup-only
- `medium` — diverging behavior across dupes (one has a bug fix the other doesn't)
- `high` — security or correctness implication (e.g., one auth check, the other none)
- `critical` — duplicates with materially different behavior on the same code path

## Output files

### `OUT/sections/03b-duplicates.md`

Prose: total dupe clusters, breakdown by literal vs semantic. Top 5 most concerning (especially diverging-behavior ones). For each, explain what's duplicated, where canonical is, where the others are, what diverges.

### `OUT/findings/03b-duplicates.yaml`

One entry per cluster. `evidence` lists ALL paths in the cluster. `description` names the canonical and explains divergence (if any).

### `OUT/summary/03b-duplicates.md`

One paragraph: "Found N duplicate clusters: M literal, K semantic. Highest concern: <one-line example>. <Yes/no on whether AI-bloat pattern is present>."

## Anti-patterns

- Don't flag intentional patterns (e.g., per-tenant repository classes that are similar by design).
- Don't flag generated code.
- For semantic dupes, **always read the actual function bodies** before flagging. Graphify clustering is a candidate filter, not a verdict.
- Don't conflate "similar names" with "duplicate behavior". `delete_user` and `delete_user_account` may do entirely different things.
