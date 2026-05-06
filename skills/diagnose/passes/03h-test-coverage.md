# Pass 03h — Test coverage gaps on critical paths

You identify critical code paths that lack tests. Not "coverage percent low" — specifically, **which capabilities are untested**.

## Inputs
- `TARGET`, `OUT`
- `OUT/graphify-out/graph.json`

## Hard rules
- No source mutation.
- **No documentation reads.** Skip every `.md`, `.rst`, `.txt`, `.adoc`, `.markdown`, `.org` file and any `docs/` directory in `TARGET`. Test code is source code (`.py`, `.ts`, `.go`, etc.) and IS in scope.
- Findings conform to schema. ID format: `F-TEST-<sha1(category + capability + path)[:8]>`.
- **Critical path** = code reachable from a user-facing entry point AND involved in auth, payment, data persistence, external API calls, or anything user-facing.

## Method

1. Identify test files (conventional names: `test_*.py`, `*_test.go`, `*.spec.ts`, `tests/`, `__tests__/`).
2. Identify what each test covers — by name, by import, by file under test.
3. Compute the set of code reachable from entry points (graphify reachable union).
4. For each critical-path module, check whether ANY test imports it or references it.
5. Flag critical-path modules with zero test coverage — these are the gaps that matter.
6. Also flag:
   - Test files that exist but contain only `skip`-ed tests
   - Tests that assert nothing (e.g., just call the function and rely on no exception)
   - Critical async/queue handlers with no test
7. Use:
   ```bash
   $PY -m graphify reachable --from=<entry> --graph $OUT/graphify-out/graph.json
   ```

## Severity rubric

- `low` — utility module on critical path, no tests
- `medium` — service-layer module, no tests
- `high` — auth, payment, or data-integrity module, no tests
- `critical` — critical path explicitly has skipped tests (someone wrote them, they're not running)

## Output files

### `OUT/sections/03h-test-coverage.md`

Prose: total test files, total tests, ratio of test code to source code (not coverage percent — call out that this is structural, not runtime). List critical-path modules with no test coverage. List skipped tests on critical paths.

### `OUT/findings/03h-test-coverage.yaml`

One entry per significant gap.

### `OUT/summary/03h-test-coverage.md`

One paragraph: structural test ratio + count of untested critical modules + worst gap.

## Anti-patterns

- Don't claim runtime coverage percent — you have not run the tests, only read them.
- Don't flag tests for trivial getters/setters as missing.
- Don't conflate "no test file with matching name" with "no tests" — tests may exist in integration test files.
- Don't propose specific tests to write — that's not this skill's job. Just flag the gap.
