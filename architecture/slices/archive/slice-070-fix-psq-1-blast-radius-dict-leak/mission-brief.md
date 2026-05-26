# Slice 070: fix-psq-1-blast-radius-dict-leak

**Mode**: Standard
**Estimated work**: 0.5 day (~1-2 hr fix + tests + multi-shape coverage)
**Risk retired**: SC-027 (backlog candidate; severity medium per multi-consumer-artifact rule — see `diagnose-out/backlog.md:558-576`; the multi-consumer premise traces to ADR-064 §Decision option 1 "durable across sessions" rationale + diagnose-out/backlog.md SC-027's `**Blocks:**` line citing PSQ-2 cross-machine coordination)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

**Closes:** SC-027

## Intent

`tools/slice_queue_writer.py::_call_graphify_blast_radius` (`tools/slice_queue_writer.py:246` + `:250`) stringifies each JSON list element via `{str(x) for x in data}` without checking whether `x` is a string or a graphify node-OBJECT. When graphify returns the current node-object shape (`[{"id": ..., "label": ..., "type": "", "path": ""}, ...]` — empirically verified: `path` and `type` fields are structurally EMPTY in this repo's `graphify-out/graph.json`; the `name` key is absent from the schema entirely; only `id` is universally populated), `str(x)` yields a literal dict-string (`"{'id': '...', 'label': '...', 'type': '', 'path': ''}"`) — containing the characters `{`, `'`, `:` that any downstream consumer parsing the rendered `Blast-radius:` cell as a comma-separated path list will trip on. The leak is empirically visible right now in committed `architecture/slice-queue.md` at lines 18, 34, 42 (post-slice-069 queue write). Build an `{id → repo-relative source_file}` map from `graph.json` (the underlying graph node carries the real path in its `source_file` field; the blast-radius CLI just doesn't surface it) and have `_node_to_path` resolve a node-dict's `id` against this map — falling back to dict's own `path`/`name`/`source_file` keys if present and path-shaped (forward-compat for future graphify schema changes), and to None otherwise (skip-on-None at the comprehension).

## Acceptance criteria

1. The /repro WRITTEN-FAILING test at `tests/bugs/test_psq_1_blast_radius_dict_leak.py::test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup` PASSES post-fix (verified by `pytest`).
2. `_call_graphify_blast_radius` correctly handles four graphify JSON output shapes without leaking non-path tokens — (a) list-of-strings (legacy/backward-compat — string returned verbatim only if path-shaped), (b) list-of-dicts-with-empty-`path`-and-no-`name`-and-non-path-`id`-but-id-mappable-via-`graph.json`-`source_file` (the actual current graphify-in-this-repo shape), (c) dict-with-`nodes`/`blast_radius`/`affected`-keyed-list-of-dicts (line-250 second comprehension), (d) forward-compat list-of-dicts where `path`/`name`/`source_file` IS populated path-shaped (future graphify schema) — pinned by four supplemental test functions in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` plus the AC#1 repro test.
3. The live committed `architecture/slice-queue.md` regenerated post-fix (via `$PY -m tools.slice_queue_writer --root .` against current graphify graph) contains only path-shaped tokens in `Blast-radius:` cells — every backtick-quoted token in any `Blast-radius:` cell value matches the positive-shape regex `^(?:[^\s\`]*[/\\][^\s\`]+|[^\s\`]*\.[A-Za-z0-9]{1,8}|\.[A-Za-z][A-Za-z0-9_.-]*)$` (contains a path separator OR ends with a `.alphanum` extension 1-8 chars OR is a leading-dot dotfile like `.gitignore`/`.env`). This is a positive-shape contract: bare opaque identifiers (e.g., `slice_queue_writer_rationale_1`) FAIL the test even though they contain no `{`, `'`, `:`. **Regex widening per /build-slice 2026-05-26 DEVIATION**: the original /critique-time regex `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$` had a blind spot for legitimate dotfiles (`.gitignore` in `rename-architecture-to-sdlc`'s `hint_files`). The contract (positive-shape check) is unchanged; the regex literal widened to accept the dotfile class. Pinned by `tests/bugs/test_psq_1_blast_radius_dict_leak.py::test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens` reading the live file.
4. The `**Closes:** SC-027` sentinel in this `mission-brief.md` triggers `/reflect` to append a BCR-1 round-trip line `- **Addressed:** slice-070-fix-psq-1-blast-radius-dict-leak on YYYY-MM-DD` to SC-027's block in `diagnose-out/backlog.md` (between SC-027's `**Evidence:**` sub-list end and the next `### SC-028` header).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). All test functions live in `tests/bugs/test_psq_1_blast_radius_dict_leak.py`.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup | PASSING |
| 2 | unit | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_blast_radius_handles_legacy_list_of_strings_shape | PASSING |
| 2 | unit | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_blast_radius_drops_non_path_strings_from_legacy_shape | PASSING |
| 2 | unit | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_blast_radius_handles_dict_with_nodes_key_of_node_dicts | PASSING |
| 2 | unit | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_blast_radius_forward_compat_extracts_populated_path_or_source_file | PASSING |
| 3 | integration | tests/bugs/test_psq_1_blast_radius_dict_leak.py | test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens | PASSING |
| 4 | integration | tests/methodology/test_bcr_1_backlog_round_trip.py | test_reflect_skill_md_bcr_1_closes_sentinel_grammar_pinned | PASSING |

AC4 (BCR-1 round-trip) is mechanically verified at /reflect time (the BCR-1 audit asserts the `**Addressed:** ...` line was appended) rather than via a fresh test function — the existing `tests/methodology/test_bcr_1_backlog_round_trip.py` anchor-presence + position-pin tests on both SKILL.md surfaces cover the structural axis.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro test passes | `$PY -m pytest tests/bugs/test_psq_1_blast_radius_dict_leak.py::test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup -v` exits 0 (the test mocks both subprocess.run AND the id→path map; the fix's id-lookup-then-fallback precedence resolves the real graphify node shape to its mapped path) |
| 2 | Multi-shape coverage clean | `$PY -m pytest tests/bugs/test_psq_1_blast_radius_dict_leak.py -v` runs all 5 unit tests + 1 integration test → 6/6 PASS |
| 3 | Live slice-queue.md path-shape-clean | After running `$PY -m tools.slice_queue_writer --root .`, the AC3 integration test PASSES — every backtick-quoted token in every `Blast-radius:` cell value matches `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$`. Manual spot-check: `grep -nE "Blast-radius:" architecture/slice-queue.md` shows ONLY paths like `` `tools/slice_queue_writer.py` ``, no opaque identifiers, no dict-strings |
| 4 | SC-027 closure | At /reflect time, `diagnose-out/backlog.md` contains the `- **Addressed:** slice-070-fix-psq-1-blast-radius-dict-leak on YYYY-MM-DD` line at the end of SC-027's block (verified by BCR-1 audit) |

## Must-not-defer

- [ ] Multi-shape coverage — fix must handle all four observed JSON shapes (list-of-strings, list-of-dicts-with-empty-`path`-AND-id-mappable, dict-with-`nodes`-keyed-list-of-dicts, forward-compat list-of-dicts-with-populated-`path`-or-`source_file`); a single-shape patch leaves the others vulnerable
- [ ] Backward-compatibility with legacy list-of-strings shape (graphify versions before the node-object output change); regression in this shape would break any cached or older-graphify-built `graphify-out/graph.json`
- [ ] Deterministic path-extraction precedence — id-via-`graph.json`-`source_file`-map (PRIMARY) → dict-own-`path`/`source_file`/`name` if path-shaped (forward-compat fallback) → None (skip); documented in the `_node_to_path` docstring + pinned by the 6 tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (closes the "silently swallow garbage" footgun AND the slice-070 /critique B1 wrong-precedence defect class)
- [ ] No regression on existing PSQ-1 tests at `tests/skills/slice/test_slice_queue_output.py` (must continue to pass with no edits — the fix touches `_call_graphify_blast_radius` only, not the higher-level `write_slice_queue` / `compute_parallel_safety` / `format_queue_md` API surface)
- [ ] The committed `architecture/slice-queue.md` is regenerated and re-committed at /build-slice end to capture the fix's effect on the live artifact (must-not-defer because AC3 requires the live file to be clean — leaving the broken file committed would defeat the slice's user-visible value)
- [ ] BCR-1 round-trip closure executes at /reflect time (the `**Closes:** SC-027` sentinel is the trigger; if /reflect doesn't append the `**Addressed:** ...` line, AC4 fails)

## Out of scope

- Refactoring `_call_graphify_blast_radius` beyond the dict-extraction surface (e.g., merging with `_parse_text_nodes` fallback, changing the retry-with-`--from`-fallback control flow)
- Slice-067 PSQ-2 claim machinery (the downstream parser of `Blast-radius:` cells) — its own slice candidate
- Removing the `_parse_text_nodes` text-fallback (still useful for non-JSON graphify output paths; separate cleanup defer)
- PMI-1 atomic bump (EXCLUDE posture per voluntary-restraint discipline — see "MEPD-1 disposition" below)
- Renaming `slice_queue_writer.py` or restructuring the queue file format

## Dependencies

- Prior slices:
  - [[slice-067-add-parallel-slice-queue-output]] — PSQ-1 minted; introduced `tools/slice_queue_writer.py` + `_call_graphify_blast_radius` (the defect site)
  - [[slice-068-add-vault-root-constant]] — `tools/slice_queue_writer.py` routes through `VAULT_ROOT` per `_MIGRATION_SITE_ALLOWLIST`; this slice does NOT alter that routing
  - [[slice-069-track-vault-in-git]] — `architecture/slice-queue.md` is now git-tracked, which is what makes the leaked dict-strings empirically visible at lines 18, 34, 42
- Vault refs:
  - [[architecture/decisions/ADR-064-add-parallel-slice-queue-output]] — PSQ-1 architectural premise (multi-session shared visibility — the consumer surface that motivates the fix's medium severity per slice-068 /critique-review m2 severity adjustment)
- Backlog refs:
  - `diagnose-out/backlog.md` SC-027 (severity medium; blast medium; reversibility cheap; effort small) — filed at slice-068 /reflect per /critique m2 ACCEPTED-PENDING + /critique-review m2 severity adjustment

## MEPD-1 disposition

**EXCLUDE** (no new `## v0.70.1` methodology-changelog entry + no PMI-1 bump + no consumer-propagation obligation). Voluntary-restraint discipline N≥10 cumulative inclusive of slice-070 — slice-037/046/050/052/055/056/057/061/065 precedent. This slice:
- mints no new rule
- mints no new ADR
- adds no audit surface
- makes no SKILL.md or agent edit
- introduces no user-facing behavior change beyond fixing a defect in a tool consumed only by `/slice` Step 6.5

The BCR-1 round-trip (SC-027 closure) is mechanics on existing rule (BCR-1 itself was minted at slice-055 via ADR-055; SC-027 closure here is BCR-1 consumption, not a new rule mint).

Ships at v0.70.0 unchanged — VERSION, plugin.yaml.version, pyproject.toml [project].version, methodology-changelog.md, and installed `~/.claude/ai-sdlc-VERSION` all remain at 0.70.0.

## Mid-slice smoke gate

At ~50% of build, run the FULL test module (all 6 tests, including the AC3 live-artifact integration pin — per /critique m1 fix, the smoke gate must catch B1-class silent-wrong-output classes that pass unit tests but fail the live-artifact contract):

```bash
$PY -m tools.slice_queue_writer --root .  # regenerate live slice-queue.md against current graph
$PY -m pytest tests/bugs/test_psq_1_blast_radius_dict_leak.py -v
```

Expected: all 6 tests PASS (transitions WRITTEN-FAILING → PASSING). If any fail, the fix is incomplete or wrong — STOP, diagnose, do not continue. The AC3 integration test failure on a unit-test-passing fix is the canonical B1-class signal.

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] `/drift-check` passes (vault and code aligned)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] All 14 Step-6 audits exit 0 (BRANCH-2 + TF-1 + BC-1 + WIRE-1 + UTF8-STDOUT-1 + CRP-1 + PCA-1 + BCI-1 + MCFS-1 + STP-1 + AVFS-1 + TVFS-1 + NAW-1 + PMI-1)
- [ ] Full pytest baseline preserved (slice-070 adds 6 new tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` — 5 unit + 1 integration; expected baseline shift +6)
- [ ] `architecture/slice-queue.md` regenerated and committed at /build-slice end (live-artifact AC3 verification)
- [ ] `**Closes:** SC-027` sentinel propagates to /reflect → BCR-1 round-trip line landed in `diagnose-out/backlog.md`
