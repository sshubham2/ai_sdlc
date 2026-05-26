# Design: Slice 070 fix-psq-1-blast-radius-dict-leak

**Date**: 2026-05-26
**Mode**: Standard

## What's new

- New private helper `_build_id_to_path_map(graph_path: Path) -> dict[str, str]` in `tools/slice_queue_writer.py` — reads `graph.json` once and constructs `{node_id → repo-relative source_file}` for every node carrying both fields. Memoized via `functools.lru_cache` keyed on the resolved graph_path string (so the per-`/slice`-invocation amortization is automatic; the cache is cleared on graph_path change, which doesn't happen within one `/slice` run).
- New private helper `_node_to_path(node, id_to_path)` in `tools/slice_queue_writer.py` — extracts a path-shaped string from a graphify node element, handling four shapes safely:
  1. `str` input → returned verbatim ONLY if path-shaped (contains `/` or `\` or matches a known file extension); ID-only strings dropped (this preserves the existing `_parse_text_nodes` discipline at line 255).
  2. `dict` input → PRIMARY path: lookup `id` in `id_to_path` map → repo-relative `source_file`. Fallback (for forward-compat with future graphify schema changes): if dict carries `path`/`name`/`source_file` keys that ARE populated AND path-shaped, use that value. Otherwise → `None`.
  3. Any other shape (int, list, None, etc.) → returns `None`.
- Modified `_call_graphify_blast_radius` set-comprehensions inside `tools/slice_queue_writer.py` (currently at lines 246 + 250; line numbers shift post-helper-insertion) to use `_node_to_path` + skip-on-None instead of `str(x)`. The function now builds the id→path map once at entry (`id_to_path = _build_id_to_path_map(graph_path)`) and threads it into both comprehension call sites. Fix surface: one new id-map helper + one new path-extractor helper + two call-site comprehension rewrites + one id-map-construction line at function entry. Full source-level diff lands at `/build-slice`.
- New tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (5 new functions added; the `/repro` test is renamed in-fix-block to align with the redesigned shape):
  - `test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup` (AC1 — replaces the /repro placeholder; uses real graphify-in-this-repo shape `{"id": "<id>", "label": "<label>", "type": "", "path": ""}` with `_build_id_to_path_map` mocked to return a known id→path map; asserts the extractor resolves IDs to mapped paths)
  - `test_blast_radius_handles_legacy_list_of_strings_shape` (AC2 backward-compat — strings returned verbatim if path-shaped)
  - `test_blast_radius_drops_non_path_strings_from_legacy_shape` (AC2 backward-compat — ID-only strings dropped; matches `_parse_text_nodes`'s "/" filter discipline at line 255)
  - `test_blast_radius_handles_dict_with_nodes_key_of_node_dicts` (AC2 the second leaky comprehension at line 250 — same id-lookup path)
  - `test_blast_radius_forward_compat_extracts_populated_path_or_source_file` (AC2 forward-compat — dict with populated `path`/`name`/`source_file` field works without id-map lookup; precedence pinned: dict-own-keys checked AFTER id-map miss, NOT before)
  - `test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens` (AC3 live-artifact pin — positive-shape regex per /critique M1 fix: every backtick-quoted token matches `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$`)

## What's reused

- `tools/slice_queue_writer.py` (slice-067 / [[ADR-064]] / PSQ-1) — the helper module being fixed; signature + injection seam (`blast_resolver`) + 4-value `Parallel-safety` enum + atomic write semantics ALL unchanged
- `architecture/slice-queue.md` (slice-067 / PSQ-1) — the rendered artifact whose `Blast-radius:` cells contain the empirically-visible leak this slice retires
- `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (slice-070 `/repro`) — the test module `/repro` just created; this slice RENAMES the /repro placeholder + extends from 1 to 6 functions in the same file (the /repro placeholder used a fictional graphify shape per /critique B2; rewritten to use the real shape in fix-block)
- `architecture/shippability.md:79` — row #70 added by `/repro` Step 5; the row's `Critical path` description references the AC3 invariant the fix establishes
- `diagnose-out/backlog.md` SC-027 (slice-068 `/critique-review` m2 severity-adjusted from low → medium) — the backlog candidate `/reflect` will close via BCR-1 round-trip
- Existing `tools/slice_queue_writer.py::_parse_text_nodes` text-fallback at line 255 — unchanged; out of scope per mission-brief

## Components touched

### `tools/slice_queue_writer.py` (modified)

- **Responsibility**: PSQ-1 helper that writes `architecture/slice-queue.md` with the top-10 parallel-safe candidates from `/slice` Step 6.5, each enriched with a graphify-derived blast-radius file set.
- **Lives at**: `tools/slice_queue_writer.py` (existing, slice-067)
- **Key interactions**: invoked by `/slice` Step 6.5 (`skills/slice/SKILL.md` L378-379 try/except wrapper); shells out to `graphify blast-radius --format json`; written artifact is consumed by future `/slice` invocations + future PSQ-2 claim machinery (the multi-consumer rationale for SC-027's medium severity per [[ADR-064]] architectural premise).
- **Fix surface (this slice)**: small delta — one id-map helper (`_build_id_to_path_map`) + one path-extractor helper (`_node_to_path`) + two call-site comprehension rewrites + one id-map-construction line at `_call_graphify_blast_radius` entry. Full source-level diff lands at `/build-slice`. The diff's structural anchor is the two `{str(x) for x in ...}` comprehensions inside `_call_graphify_blast_radius` (currently lines 246 + 250) plus the new helper functions inserted above.
- **Out of scope (this slice)**: the `_parse_text_nodes` text-fallback path (line 255) which is reached only when `json.JSONDecodeError` fires — not the dict-leak path; the `derive_active_slice_blast_radius` higher-level API (line 264) which passes `blast_resolver` results through unchanged; the `format_queue_md` renderer (line 415) which receives the now-clean path set.

### `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (modified)

- **Responsibility**: regression test module pinning SC-027 closure across all four observed graphify JSON output shapes + a positive-shape live-artifact pin against `architecture/slice-queue.md`.
- **Lives at**: `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (created by /repro; this slice RENAMES the /repro placeholder + extends from 1 to 6 functions total).
- **Key interactions**: uses `unittest.mock.patch.object` to fake `subprocess.run` results AND `_build_id_to_path_map` results (the id→path map is mocked rather than requiring a real graph.json fixture for unit tests); uses `tools.slice_queue_writer._call_graphify_blast_radius` directly (unit-level — no graphify install required for the test to run); the AC3 integration test reads the live `architecture/slice-queue.md` and applies the positive-shape regex to every backtick-quoted token in every `Blast-radius:` cell.

## Contracts added or changed

None. `_call_graphify_blast_radius`'s public signature (`graph_path: Path, file_or_node: str → set[str]`) is unchanged. The contract is tightened internally: every element in the returned set is now guaranteed to be a non-empty path-shaped string (no dict-strings, no empty strings, no other garbage) — this was the *intended* contract from slice-067 but was not enforced. The behavior change is bug-fix-shape: previously-broken consumers get correct output; previously-correct consumers (the legacy list-of-strings shape) see no change.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces zero new modules — only modifies an existing module (`tools/slice_queue_writer.py`) and an existing test file (`tests/bugs/test_psq_1_blast_radius_dict_leak.py`). The `_node_to_path` helper is module-private (leading-underscore convention; consumed only by `_call_graphify_blast_radius` within the same file).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

Zero-row matrix per WIRE-1 audit's documented clean handling (mission-brief Pre-finish gate: "WIRE-1 (zero-row matrix OK)" — same shape used by slice-069's zero-row matrix at slice-069 design.md).

## Decisions made (ADRs)

None. Voluntary-restraint discipline N≥10 cumulative inclusive of slice-070 — slice-037/046/050/052/055/056/057/061/065 precedent. The fix locks no new architectural decision; the precedence — id-via-`graph.json`-`source_file`-map (PRIMARY) → dict-own-`path`/`source_file`/`name` if path-shaped (forward-compat fallback) → None (skip) — is documented in the `_node_to_path` docstring (code is the canonical source per CLAUDE.md "Code is truth, docs are hypothesis").

## Authorization model for this slice

N/A. The slice touches no auth/authz/permission surface. `tools/slice_queue_writer.py` is a local-only helper invoked from `/slice` Step 6.5 in the user's own working directory; it shells out to `graphify` (a read-only local tool) and writes a single Markdown file (`architecture/slice-queue.md`) in the project's vault.

## Error model for this slice

The fix changes error behavior in one observable way and preserves it in all others:

- **Pre-fix**: `_call_graphify_blast_radius` returned a set containing dict-string elements when graphify emitted node-object JSON. Behavior was a silent-corruption defect — no exception raised, no error logged; downstream consumers received the corrupted set with literal Python `repr(dict)` strings.
- **Post-fix**: `_call_graphify_blast_radius` resolves dict-node IDs via the `_build_id_to_path_map` reading `graph.json` once at function entry; skips nodes for which `_node_to_path` returns None (id absent from map AND no path-shaped own-keys). The skip is silent at the function boundary (consistent with the surrounding error-handling philosophy: subprocess failure → `return set()`; JSON decode failure → fall back to `_parse_text_nodes`; non-zero returncode → retry with `--from`; `graph.json` unreadable → empty map → all nodes resolved via forward-compat fallback only — all surface as best-effort empty-set degradation rather than raised exceptions). This preserves the existing "graphify is best-effort, never block" contract from slice-067.

Skip-on-None is the right disposition (not raise) because:
1. A graphify node whose `id` isn't in the graph.json-build's id→source_file map is a graph-staleness or graphify-side-build-defect, not a `_call_graphify_blast_radius`-side condition the caller could meaningfully recover from
2. The surrounding `try/except (FileNotFoundError, TimeoutExpired) → return set()` + `JSONDecodeError → fallback path` + `returncode != 0 → retry` patterns all treat graphify-side issues as silent degradation
3. Raising would re-introduce the "graphify failure blocks /slice Step 6.5" defect class that the slice-067 try/except wrapper at SKILL.md L378-379 was designed to prevent

The post-fix behavior produces an empty `Blast-radius:` cell (or one containing only declared `hint_files` per `tools/slice_queue_writer.py:297`'s `blast |= declared`) on stale-graph or no-resolution cases — degraded but correct (no false-positive overlap claims). The pre-fix behavior produced opaque dict-strings that BOTH leaked into the rendered cell AND broke `compute_parallel_safety` overlap detection silently — the latter the more serious defect class.

## Fix shape (reference for /critique)

Pseudocode form of the fix (full source-level diff lands at /build-slice). Redesigned per /critique B1 + B2 fix-block: the empirically-verified graphify schema in this repo is `{label, file_type, source_file, source_location, community, id}` (per `~/.claude/packages/graphify/graphify/extract.py:656-662`); the blast-radius CLI emits `{id, label, type:"", path:""}` (per `~/.claude/packages/graphify/graphify/__main__.py:1009-1014`) — `type` and `path` are structurally EMPTY in this repo's graph. The real path lives in graph.json's `source_file` under matching `id`. Solution: read the graph once to build the id→path map; resolve dict-node IDs against it.

```python
import functools
import json

@functools.lru_cache(maxsize=4)
def _build_id_to_path_map(graph_path_str: str) -> dict[str, str]:
    """Build {node_id → repo-relative source_file} from graph.json.

    The graphify blast-radius JSON CLI output emits {id, label, type:"",
    path:""} where type/path are structurally empty in this repo's graph
    (per `~/.claude/packages/graphify/graphify/__main__.py:1013` —
    `"path": data.get("path", "")` always returns ""). The underlying
    node dicts in graph.json carry the real source_file. This map lets
    us resolve a returned ID to the path our consumers actually need.

    Cached via lru_cache (string key — Path is unhashable in some shapes)
    so multi-call enrichment within one `/slice` Step 6.5 invocation
    reads + parses graph.json once.
    """
    try:
        data = json.loads(Path(graph_path_str).read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    repo_root = Path.cwd().resolve()
    out: dict[str, str] = {}
    for n in data.get("nodes", []):
        if not isinstance(n, dict):
            continue
        nid = n.get("id")
        src = n.get("source_file")
        if not (isinstance(nid, str) and isinstance(src, str) and nid and src):
            continue
        try:
            rel = Path(src).resolve().relative_to(repo_root).as_posix()
        except (ValueError, OSError):
            # Fallback: source_file is outside repo_root or unresolvable.
            # Use the path as-given with as_posix() to normalize separators.
            rel = Path(src).as_posix()
        out[nid] = rel
    return out


def _is_path_shaped(s: str) -> bool:
    """A string is path-shaped if it contains a separator or a known
    file extension (mirrors `_parse_text_nodes` line-255's '/' filter
    discipline, but accepts Windows backslash + known extensions too)."""
    if not s:
        return False
    if "/" in s or "\\" in s:
        return True
    return s.endswith((".py", ".md", ".json", ".toml", ".yaml", ".txt"))


def _node_to_path(node: object, id_to_path: dict[str, str]) -> str | None:
    """Extract a path-shaped identifier from a graphify node element.

    PRIMARY path: dict input whose `id` is in `id_to_path` map → return
    the mapped repo-relative source_file. This is the path graphify
    actually carries today; the blast-radius CLI just doesn't surface
    the field directly in JSON output.

    Forward-compat fallback (future graphify schemas where the CLI DOES
    surface a path-bearing key): dict input with `path`/`name`/`source_file`
    populated AND path-shaped → return that value.

    Legacy compat: str input that is itself path-shaped → returned verbatim.
    ID-only strings dropped (mirrors `_parse_text_nodes` discipline).

    Any other shape → returns None; caller skips such items rather than
    letting `str(node)` leak Markdown-invalid characters into the rendered
    `Blast-radius:` cell (SC-027 defect class).
    """
    if isinstance(node, str):
        return node if _is_path_shaped(node) else None
    if not isinstance(node, dict):
        return None
    # PRIMARY: id-lookup via graph.json map
    nid = node.get("id")
    if isinstance(nid, str) and nid in id_to_path:
        return id_to_path[nid]
    # Forward-compat: dict has its own populated path-shaped key
    for key in ("path", "source_file", "name"):
        val = node.get(key)
        if isinstance(val, str) and _is_path_shaped(val):
            return val
    return None


# MODIFIED in _call_graphify_blast_radius (currently lines 246 + 250).
# Build the id→path map once at function entry; thread into both
# comprehension call sites:
def _call_graphify_blast_radius(graph_path: Path, file_or_node: str) -> set[str]:
    # ... existing subprocess invocation ...
    id_to_path = _build_id_to_path_map(str(graph_path))  # NEW
    # ... existing JSON parsing ...
        if isinstance(data, list):
            return {p for x in data if (p := _node_to_path(x, id_to_path)) is not None}
        if isinstance(data, dict):
            for key in ("nodes", "blast_radius", "affected"):
                if key in data and isinstance(data[key], list):
                    return {p for x in data[key] if (p := _node_to_path(x, id_to_path)) is not None}
        return set()
```

`tools/slice_queue_writer.py` requires Python 3.10+ (per `pyproject.toml` `requires-python = ">=3.10"`); walrus operator (3.8+) is safe; `functools.lru_cache` has been stdlib since 3.2. The walrus form is idiomatic for "compute-once, conditional-include" set comprehensions and avoids a redundant `_node_to_path` call per item.

**Empirical verification** (Builder, /critique fix-block): ran the strategy against the live `graphify-out/graph.json`. For input `slice_queue_writer.py`, graphify blast-radius returns 1 node (`slice_queue_writer_rationale_1`); the id→path map resolves it to `tools/slice_queue_writer.py`. Strategy works against real data; no opaque IDs emerge. This is the APED-1 discipline applied to a redesigned mechanism, per slice-069 aggregated lesson "methodology-revision slices that mint a new mechanism have a structural N+1 first-governed-slice catch surface — perform empirical execution of any minted mechanism on a known input before declaring done".

## Test plan (TF-1 supplement for `/build-slice` Step 6)

`/repro` wrote a placeholder test fixture with the fictional shape `{"path": "tools/..."}` (per /critique B2 — fictional graphify shape that graphify never emits in this repo). At `/build-slice` time, that test is RENAMED + rewritten to use the real graphify shape and the id-lookup path, AND five more tests are added BEFORE the fix lands (TF-1 PENDING → WRITTEN-FAILING transition); the fix transitions all six from WRITTEN-FAILING to PASSING.

| AC | Test function | Fixture / mocking strategy |
|----|--------------|---------------------------|
| 1 | `test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup` | renames + rewrites the /repro placeholder. Mocks BOTH `subprocess.run` (returns real graphify shape: list of 2 dicts `{"id": "<id1>", "label": "...", "type": "", "path": ""}` + `{"id": "<id2>", ...}`) AND `_build_id_to_path_map` (returns `{"<id1>": "tools/slice_queue_writer.py", "<id2>": "tools/branch_workflow_audit.py"}`). Asserts the result set is exactly `{"tools/slice_queue_writer.py", "tools/branch_workflow_audit.py"}` AND no element contains `{`, `'`, `:`, AND every element is path-shaped via `_is_path_shaped()`. |
| 2 | `test_blast_radius_handles_legacy_list_of_strings_shape` | mock returns JSON list-of-2-strings (`["tools/foo.py", "tools/bar.py"]`); assert exact set match (path-shaped strings preserved verbatim) |
| 2 | `test_blast_radius_drops_non_path_strings_from_legacy_shape` | mock returns mixed list (`["tools/foo.py", "opaque_identifier", "another_id_no_separator"]`); assert only path-shaped string `tools/foo.py` survives; non-path strings dropped per `_is_path_shaped` discipline (mirrors `_parse_text_nodes` line-255 "/" filter) |
| 2 | `test_blast_radius_handles_dict_with_nodes_key_of_node_dicts` | mock returns JSON object `{"nodes": [<real-shape dict>, <real-shape dict>]}` (line-250 second comprehension path); mock `_build_id_to_path_map` returns matching id→path entries; assert id-lookup resolution works for the second comprehension too |
| 2 | `test_blast_radius_forward_compat_extracts_populated_path_or_source_file` | mock returns list of 3 dicts: (a) `{"id": "unknown_id", "path": "tools/foo.py"}` (id-map misses → dict's own `path` key wins forward-compat path), (b) `{"id": "another_unknown", "source_file": "tools/bar.py"}` (source_file key works), (c) `{"id": "third_unknown", "name": "opaque_no_separator"}` (name is NOT path-shaped → dropped, demonstrating positive-shape filter applies to dict-own-keys too); assert result is exactly `{"tools/foo.py", "tools/bar.py"}` |
| 3 | `test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens` | reads live `architecture/slice-queue.md` via `pathlib.Path.read_text`; extracts every `Blast-radius:` line via regex; for each backtick-quoted token in each cell's value, asserts the token matches the positive-shape regex `^(?:[^\s\`]*[/\\][^\s\`]+\|[^\s\`]*\.[A-Za-z0-9]{1,8}\|\.[A-Za-z][A-Za-z0-9_.-]*)$` — contains a path separator OR ends with a `.alphanum` extension (1-8 chars) OR is a leading-dot dotfile like `.gitignore`. This is the empirical-evidence AC3 pin: opaque identifiers (e.g., `slice_queue_writer_rationale_1`) FAIL the regex; bare strings without separator-or-extension FAIL the regex; legitimate paths (`tools/slice_queue_writer.py`, `.gitignore`) PASS. Per /critique M1 fix + /build-slice 2026-05-26 DEVIATION (regex widened to accept the dotfile class — the original /critique-time literal blind-spotted `.gitignore`). |

## Pre-finish artifact regeneration obligation

Per AC3 + mission-brief must-not-defer #5: `/build-slice` Phase H (or equivalent step in the executed plan) MUST run `$PY -m tools.slice_queue_writer --root .` AFTER the fix lands, regenerating `architecture/slice-queue.md` with the corrected `_call_graphify_blast_radius` behavior. The regenerated file must then be staged for the slice commit. Leaving the broken `slice-queue.md` committed would defeat the slice's user-visible value (AC3 would FAIL the live-artifact pin).

The regenerate step can run candidate-list-less (just call `write_slice_queue` with a minimal candidate list, OR the CLI form `$PY -m tools.slice_queue_writer --root .`) — the goal is purely to overwrite the file with the fix's effect. Alternative: re-invoke `/slice` Step 6.5 with the current top-10 ranked candidate list at /build-slice end. Builder picks the cleaner option in their plan.

## Risks specific to this slice (for /critique)

- **R-X1 — Walrus operator + set comprehension idiom**: the proposed fix uses Python 3.8+ walrus inside a set comprehension (`{p for x in data if (p := _node_to_path(x, id_to_path)) is not None}`). The repo's `requires-python = ">=3.10"` (per `pyproject.toml`) makes this safe, but the idiom is uncommon enough that future maintainers might misread the precedence. **Mitigation**: the `_node_to_path` docstring + this design.md call out the pattern.
- **R-X2 — Node `id` absent from the graph.json build's `source_file` map** (rewritten per /critique M2 — original R-X2 had the framing inverted; the actual risk is silent-PRODUCTION-of-wrong-output, not silent-drop-of-empty-output): per /critique B1 empirical execution, EVERY live graphify node carries non-empty `id` and EMPTY `path`; the `name` key is absent from the schema. The proposed fix resolves dict-node IDs via the graph.json-build id→source_file map; a graphify node whose ID is absent from that map (e.g., stale `graph.json` not covering a newly-added file the live graphify CLI saw) would fall through to the forward-compat dict-own-key fallback (returns None for current graphify shape) → silent-drop. **Mitigation**: the AC3 integration test's positive-shape regex catches any regression where opaque IDs leak; the silent-drop is the documented disposition consistent with the surrounding "graphify is best-effort, never block" contract from slice-067.
- **R-X3 — AC3 positive-shape regex collision classes** (collapsed into /critique M1 fix — see above): per /critique M3 fix, the original R-X3 framing only acknowledged class (a) IDs containing `:` (false-positive) but missed class (b) IDs without `:` (false-negative masking the B1 defect). The redesigned AC3 regex (`^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$`) is a positive-shape check that correctly rejects both classes: tokens without `/`/`\`/known-extension FAIL. A hypothetical legitimate path containing characters outside the regex's allowance set (e.g., a path with a colon in a non-Windows-drive-letter position — rare in this codebase) would trigger a false positive; defer mitigation to a future slice if observed.
- **R-X4 — `lru_cache` on `_build_id_to_path_map` may cache stale data if `graph.json` is rewritten mid-`/slice`-invocation**: highly unlikely in practice (graph.json regenerates only at user-explicit `$PY -m graphify code .` invocation, not as a `/slice` side-effect); but theoretically a long-running `/slice` Step 6.5 + concurrent graphify rebuild could read a stale cache. **Mitigation**: cache key is the resolved string path; this is process-local + bounded to N=4 entries; explicit cache-clear is available via `_build_id_to_path_map.cache_clear()` if a follow-on slice needs it. No action this slice.

## Voluntary-restraint disposition (MEPD-1)

Per **MEPD-1** (`methodology-changelog.md` v0.30.0 — Inclusion-heuristic): this slice mints no new rule, mints no new ADR, adds no audit surface, makes no SKILL.md / agent edit. EXCLUDE posture per N≥10 cumulative voluntary-restraint discipline precedent — slice-037/046/050/052/055/056/057/061/065 lineage. No `## v0.70.1` methodology-changelog entry; no PMI-1 atomic version bump; no consumer-propagation obligation; no installed-side forward-sync (MCFS-1 / AVFS-1 / TVFS-1 / OSDG-1 / CAD-1 all no-op at this slice since their primary files don't change). Ships at v0.70.0 unchanged.

The BCR-1 round-trip (SC-027 closure) is consumption of an existing rule (BCR-1 was minted at slice-055 via [[ADR-055]]), not a mint of a new one.
