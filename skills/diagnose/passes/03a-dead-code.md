# Pass 03a — Dead code detection

You identify code unreachable from any entry point.

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`

## Hard rules
- No source mutation in `TARGET`.
- **No documentation reads.** Skip every `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` file and any `docs/` directory in `TARGET`. Source code, config, schemas, build manifests, and graphify only.
- Findings must conform to `~/.claude/skills/diagnose/schema/finding.yaml`.
- ID format: `F-DEAD-<sha1(category + primary_evidence_path + signature)[:8]>` where `signature` = the function/class/module name being flagged.

## Method

1. Run `graphify orphans` to get modules / functions with no inbound edges:
   ```bash
   $PY -m graphify orphans --graph $OUT/graphify-out/graph.json
   ```
2. For each candidate, **verify before flagging:**
   - grep for the symbol name as a string literal (catches dynamic imports / reflection / config-driven loading).
   - Check if it's a public API exported from the package (might be intentionally part of the surface).
   - Check if it's a test fixture, a CLI subcommand, or a plugin entry point (these often have no static inbound edges but ARE entry points).
3. Identify entry-point candidates by scanning for: `if __name__ == "__main__"`, framework decorators (`@app.route`, `@cli.command`, `@click.command`, `@pytest.fixture`), exported package symbols (`__all__`, `index.ts` exports).
4. Use `graphify reachable` from each entry point to get the union of reachable code:
   ```bash
   $PY -m graphify reachable --from=<entry> --graph $OUT/graphify-out/graph.json
   ```
5. Anything not in that union AND not a verified entry point AND not referenced as a string literal is dead code.
6. Severity rubric:
   - `low` — entire module / file unreachable; cheap to remove
   - `medium` — function within a live module is dead; moderate clarity benefit
   - `high` — dead code path inside a function (e.g., unreachable branch after an early return); may indicate a logic bug
   - `critical` — only if the dead code is masking a security check or correctness invariant

## Output files

### `OUT/sections/03a-dead-code.md`

Prose: how many dead items, broken down by file/module/function/branch level. Top 5 most impactful (largest modules / clearest cuts). Note any verified-but-uncertain cases (e.g., "appears dead but referenced in YAML config — flagged for owner verification").

### `OUT/findings/03a-dead-code.yaml`

One YAML entry per dead item, conforming to schema. Include the verification step taken in the description.

### `OUT/summary/03a-dead-code.md`

One paragraph: "Detected N dead-code items: M unreachable modules, K dead functions, J dead branches. Largest cluster: <name> (<LOC> lines). Verification: dynamic-import grep, config-reference grep."

## Anti-patterns

- **Don't flag without verification.** Dynamic imports (`importlib`, `require()` with computed strings, `eval`) defeat static reachability. Always grep for the symbol string before flagging.
- **Don't flag public API.** A function exported from a package's `__init__.py` / `index.ts` may be deliberately part of the surface even if no internal caller exists.
- **Don't flag test fixtures.** Pytest fixtures, jest setup hooks, etc., have implicit inbound edges via the test runner.
- **Don't flag plugin entry points** registered via setuptools entry-points / package.json `bin`.
