# Design: Slice 102 vault-flip-readiness-tests

**Date**: 2026-06-02
**Mode**: Standard
**Revision note**: corrected post-`/critique` (M1: split the tests collection class out of the update-checklist; M2: AC4 `--strict` wording harmonized — see mission-brief.md).

## What's new

- Extend `tools/vault_flip_readiness_audit.py` (slice-100 / [[ADR-091]]) to scan and classify the **`tests/**/*.py` surface** in addition to the existing production surface (`tools/*.py` + `skills/**/*.py`).
- **Two** new occurrence classes for the tests surface, preserving ADR-091's loud-vs-silent fidelity by *not* conflating two structurally-different literal shapes (the M1 correction):
  - **`test-update-at-flip`** — a literal in a **path-construction** context (the test code *resolves* a vault path: `Path(...)`, `open(...)`, `/`-BinOp, `os.path.join`, a path-method receiver/glob). It breaks **loudly** at flip and **WILL** need updating. This is *the checklist*.
  - **`test-collection-pathspec`** — a vault literal that is a **member of a set/list/tuple** (a git-pathspec / `applies_to` tuple / `_SOFT_FILE_SET` mirror). It is **ambiguous** at flip: most mirror a production constant that is **Class-B git-identity-routed** (stays `architecture/…`, e.g. `tools/parallel_conflict_resolver.py:59-62`), so it does **not** update; a minority may. It is **reviewed separately** by the flip-execute slice, NOT auto-listed as "update me," and NOT fail-closed-blocking.
- A `surface` field (`production` | `tests`) on every `Occurrence` + the JSON output, derived from the **normalized** repo-relative path (`rel.replace("\\","/").startswith("tests/")` → tests, else production — m2).
- A correctness fix forced by the tests surface: **the positional argument to `write_text` / `write_bytes` is content, not a path** (only the receiver is the path).
- Scan-scope exclusion of `tests/**/fixtures/**` (test-input artifacts, not vault-resolving logic) + a pinned residual-documenting test (m3).
- Tests-surface regression guard = **fail-closed completeness invariant + per-class non-vacuity floors** (user-ratified Option B, refined per m1), NOT a frozen membership pin.
- [[ADR-092]] records the model + sub-decisions.

## What's reused

- `tools/vault_flip_readiness_audit.py` — the entire slice-100 ordered ruleset, match rule (`_value_matches`), AST parent-pointer + ≤1-hop flow analysis, `_norm_value`, stable sort, cp1252-safe stdout (`tools/_stdout.reconfigure_stdout_utf8`), and `--json` / `--strict` CLI. This slice **extends**, does not rewrite.
- The production baseline `_BASELINE` (4 `project_frame_synth.py` `/`-BinOp sites) + `test_must_rewrite_baseline_pinned` — preserved **unchanged** (AC1; the `write_text` fix verified by the Critic not to perturb it).
- `tests/methodology/test_vault_flip_readiness_audit.py` — extended with tests-surface cases.
- [[ADR-091]] (the readiness-audit decision this realises the deferred `tests/**/*.py` surface of), [[ADR-089]] (Class-B markers — the production-side `_SOFT_FILE_SET` markers the M1 split respects), [[ADR-065]] (`_vault_paths` seam). `tools/_vault_paths.py` default `Path("architecture")` — untouched (AC5).

## Evidence base (design-time probe + Critic execution, read-only)

Ran the existing `audit_file` as a library over the worktree's `tests/**/*.py` files (production ruleset, before any change), confirmed by the Critic's independent execution:

| Class (production ruleset on tests) | Count | Disposition under this design |
|---|---|---|
| `doc-example-safe` (prose/docstring/comment) | 287 | stays `doc-example-safe` |
| `must-rewrite-before-flip` (path-construction) | 160 | → **`test-update-at-flip`** (the genuine path-resolves; minus the `write_text`/`write_bytes`-content false-positives, which become `doc-example-safe`) |
| `needs-human` `unmarked-collection-pathspec` | 49 | → **`test-collection-pathspec`** (git-pathspec / `applies_to` / `_SOFT_FILE_SET` mirrors — review-at-flip; **not** the update checklist). *Current-corpus observation (not a structural invariant): all 49 are Class-B/git-pathspec mirrors that STAY `architecture/…` — see the M-add-1 heterogeneity residual below.* |
| `needs-human` `parse-error` | 1 | `tests/methodology/fixtures/syntax_error.py` — removed by the `fixtures/**` exclusion |
| `needs-human` `dynamic-fragment` | 1 | `test_drift_check_audit.py:35` is `write_text(f"…architecture/triage.md…")` content → fixed by the `write_text`-content rule → `doc-example-safe` |
| `already-seam-routed` | 2 | unchanged |

Production surface (preserve byte-identical, AC1): **49 files, 4 must-rewrite, 0 needs-human**, `baseline_tuple() == _BASELINE`. Re-verified by the Critic with the `write_text` rule applied.

The three `needs-human` sources all resolve to a definite class under this design ⇒ **tests-surface `needs-human` drives to ∅** (Critic-confirmed: 0 residual) ⇒ the existing exit-0-on-clean-tree gate is preserved and the smoke gate's "zero un-triaged needs-human" holds. The checklist (`test-update-at-flip`) is the **160 genuine path-resolves**, not polluted by the 49 collection mirrors.

## Components touched

### `tools/vault_flip_readiness_audit.py` (modified)
- **Responsibility**: read-only, deterministic, fail-closed inventory + classification of in-tree vault-location literals so the flip lands atomically. This slice widens its surface to tests with loud-vs-silent fidelity.
- **Lives at**: `tools/vault_flip_readiness_audit.py`
- **Key changes**:
  1. **Scan**: `_iter_scan_files` also yields `tests/**/*.py`, **excluding any path with a `fixtures/` segment**. `tests/` lives outside the existing `tools/`+`skills/` roots, so production scanning is unperturbed.
  2. **Surface tag**: `audit_file(path, rel)` derives `surface = "tests" if rel.replace("\\","/").startswith("tests/") else "production"` (normalized — robust to a backslash rel from a direct unit-test caller, m2; no signature change → existing `audit_file("tools/…")` callers stay production; the `test_`-named production tool `tools/test_first_audit.py` correctly stays production). `Occurrence` gains `surface`; `to_dict()` emits it.
  3. **New classes**: `TEST_UPDATE_AT_FLIP = "test-update-at-flip"` and `TEST_COLLECTION_PATHSPEC = "test-collection-pathspec"`, both added to `_ALL_CLASSES`. **Neither** is in the production baseline classes.
  4. **Surface-aware classification**: `_classify_constant` takes `surface`. On `surface == "tests"`:
     - the path-construction / path-construction-1hop rules (which yield `MUST_REWRITE` on production) yield **`TEST_UPDATE_AT_FLIP`**;
     - the `unmarked-collection-pathspec` rule (which yields `NEEDS_HUMAN` on production) yields **`TEST_COLLECTION_PATHSPEC`**;
     - rule 1 (docstring/help/seam), the `dynamic-fragment` rule (fail-closed `NEEDS_HUMAN`), and prose-mention (`DOC_EXAMPLE_SAFE`) are identical across surfaces.
     The production classification path is byte-identical to slice-100 (no surface branch taken when `surface == "production"`).
  5. **`write_text`/`write_bytes` content-arg fix**: a new `_CONTENT_ARG_METHODS = {"write_text", "write_bytes"}`; in `_is_path_call_arg_or_recv`, a positional **arg** to one of these is NOT a path (the receiver still is). Applies to both surfaces (correctness) — Critic-verified not to change the production `_BASELINE` (its 4 sites are `/`-BinOps; re-asserted by `test_must_rewrite_baseline_pinned`).
  6. **Baseline scoping**: `baseline_tuple()` is scoped to `surface == "production"` (defense-in-depth — a tests-surface regression can never silently pollute the production pin's diff). Production `--strict` pin semantics unchanged.
  7. **Output**: `_format_human` adds `test-update-at-flip` + `test-collection-pathspec` counts (and lists the `test-update-at-flip` checklist entries); JSON `counts` gains both classes.
- **Key interactions**: consumed by `tests/methodology/test_vault_flip_readiness_audit.py` and (future) the flip-execute pre-flight. No new external deps.

### `tests/methodology/test_vault_flip_readiness_audit.py` (modified)
- Adds the tests-surface cases (see AC mapping). Existing tests unchanged.

## Contracts added or changed

No HTTP/event contracts. The tool's **CLI contract** is extended additively:
- JSON gains a per-occurrence `surface` field + `test-update-at-flip` / `test-collection-pathspec` counts in `counts`. Production occurrences keep identical `(path, value, klass)` (AC1; `key()`/baseline keyed on `(path,value,klass)`, unaffected by the additive `surface` field).
- **Exit codes unchanged**: `0` clean (no `needs-human` on either surface; under `--strict` also the **production** baseline unchanged), `2` gate, `1` usage error. Both surfaces are gate-covered: the tests surface via the `needs-human`-empty rule (any tests-surface `needs-human` → exit 2); the production surface additionally via `--strict` baseline drift. No separate surface flag — both surfaces always scanned (simplest; both always covered; AC4).

## Data model deltas

None (no persistent store). The in-memory `Occurrence` dataclass gains `surface: str`; `_BASELINE` is unchanged.

## Wiring matrix

This slice introduces **no new module** (it modifies the existing audit + its existing test). Zero-row matrix → clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Tests-surface regression strategy (Option B — user-ratified; refined per m1)

The tests checklist is large and grows whenever any future slice adds a vault-referencing test. A frozen exact-membership pin (slice-100's production pattern) would churn on most future slices and replicate the SC-023 mega-pin anti-pattern. Instead the **always-on** in-suite guards are:

1. **`test_tests_surface_needs_human_empty`** — the audit's tests-surface `needs-human` set is **∅** (fail-closed *completeness*: every tests-surface vault literal lands in a definite class; nothing unclassifiable silently slips). Keyed on `(relpath, value, klass)`.
2. **Non-vacuity** (`test_tests_surface_needs_human_pin_non_vacuous`) — inject a genuinely-unclassifiable literal (a real `dynamic-fragment`-in-path in a tmp `tests/…` file) → tests-surface `needs-human` becomes non-empty → guard (1) would fail. Proves (1) is not vacuous.
3. **Per-class non-vacuity floors** (`test_tests_surface_class_floors`, refined per m1) — `test-update-at-flip` count ≥ FLOOR_A **and** `test-collection-pathspec` count ≥ FLOOR_B (each set at build comfortably below its measured live count — ~160 and ~49). A single aggregate floor would miss a silent collapse of one classification branch (160-checklist drained while the collection branch stays full, or vice-versa); per-class floors catch either. Floors guard *emptiness per sub-population*, not exact membership.

The **exact live checklist** is the audit's JSON output (`test-update-at-flip` entries with `path:line`), which the flip-execute slice consumes directly; `test-collection-pathspec` is its separate review list. `--strict` continues to drift-guard the small, stable **production** 4-set. This satisfies AC3's intent — *a new unclassifiable literal fails the gate* — while a new *classified* checklist item surfaces in the live inventory rather than tripping the suite.

## Documented residuals (slice-095 honest-contract pattern)

Three residual classes are intentionally out of the fail-closed net and pinned by tests so they stay visible, not silently assumed-closed:

1. **Fully-dynamic path** (slice-100, inherited) — a path with no `architecture`/`diagnose-out` string-literal segment is invisible to a static scan (`test_documented_residual_fully_dynamic_path_invisible`).
2. **`fixtures/**` scan exclusion** (m3) — a vault literal inside a `tests/**/fixtures/` `.py` file is out of scan scope; fixture dirs hold test-INPUT artifacts, not vault-resolving logic (`test_fixtures_dir_vault_literal_out_of_scope`).
3. **`test-collection-pathspec` heterogeneity** (M-add-1, meta-Critic) — a *genuine* path-resolve that is a **bare collection-display member** (a list/tuple a test loops over and opens) is classified `test-collection-pathspec` (review, off-checklist, exit-0), NOT the `test-update-at-flip` checklist and NOT fail-closed `needs-human` (`test_collection_member_genuine_resolve_is_review_residual`). **Why this is acceptable** (the loud-vs-silent rationale, ADR-091): on the *tests* surface a mis-bucketed resolve breaks **LOUDLY** at flip — it surfaces as a *failing test* at flip-execute, not a silent path mis-resolve — so a non-fail-closed *review* bucket is sound **provided flip-execute consumes BOTH lists** (`test-update-at-flip` checklist AND `test-collection-pathspec` review). For the current corpus the residual is **zero-instance** (all 49 collection members are real git-pathspec/Class-B mirrors); the stronger fix (loop/comprehension-variable flow tracking, or a non-zero review-required gate) was declined at TRI-1 as gold-plating over a zero-instance case (over-engineering watch). The per-class floor counts the bucket but does not catch a genuine-resolve being *absorbed* into it (the count rises) — hence this pinned residual, not a floor, carries the contract.

## Decisions made (ADRs)
- [[ADR-092]] — Extend the vault-flip readiness audit to the `tests/**/*.py` surface with **two** distinct tests classes (`test-update-at-flip` path-resolves vs `test-collection-pathspec` git-pathspec/Class-B mirrors), a `write_text`/`write_bytes` content-arg correctness fix, a `fixtures/**` scan exclusion, and a fail-closed-completeness + per-class-floor regression strategy — reversibility: **cheap**.

## Authorization model for this slice
N/A — read-only static-analysis CLI; no auth surface, no network, no persistent writes.

## Error model for this slice
Unchanged from slice-100: exit `1` on usage error, exit `2` on gate (`needs-human` present on either surface, or `--strict` production baseline drift), exit `0` clean. A `tests/` file that fails to parse and is NOT under `fixtures/` still yields a fail-closed `needs-human(parse-error)` (never a silent skip).

## AC → mechanism map

| AC | Mechanism | Test(s) |
|----|-----------|---------|
| 1 | tests surface scanned + classified; production `(path,value,klass)` unchanged | `test_tests_surface_scanned_and_classified`, `test_production_baseline_unchanged_vs_slice100`, `test_must_rewrite_baseline_pinned` (preserved) |
| 2 | path-resolve → `test-update-at-flip` distinct from git-pathspec → `test-collection-pathspec` distinct from production silent `must-rewrite`; collection NOT auto-"update"; fail-closed | `test_tests_path_resolve_is_test_update_at_flip`, `test_tests_collection_pathspec_is_review_not_checklist`, `test_write_text_content_is_not_path` |
| 3 | needs-human-empty + non-vacuity + per-class floors | `test_tests_surface_needs_human_empty`, `test_tests_surface_needs_human_pin_non_vacuous`, `test_tests_surface_class_floors` |
| 4 | CLI gate covers both surfaces (tests via needs-human-empty; production via `--strict`) | `test_cli_exit_zero_when_no_needs_human` (preserved), `test_cli_strict_nonzero_on_baseline_drift` (preserved, production) |
| 5 | capability-without-flip | `test_vault_paths_default_unchanged` (preserved); full suite + shippability green |

## Out of scope (recap)
Contract-prose surface; the actual flip; fixing any `must-rewrite`/`test-update-at-flip` literal; per-worktree-install isolation; C5 history decision. Also out of scope: **cross-referencing** a tests collection-member against the production Class-B set to *prove* it's a mirror (this slice classifies `test-collection-pathspec` by the structural collection-membership signal — honest and over-engineering-free; a precise cross-surface mirror-match is a possible flip-execute refinement). (Per mission-brief + M1 disposition.)

## MEPD-1 disposition
**EXCLUDE candidate** — extends an existing `tools/*.py` (no new module → no BC-PROJ-9 inventory fan-out / no PMI-1 count bump), no new RULE-ID, no VERSION / methodology-changelog bump (ADR-092 alone does not make it INCLUDE — consistent with slice-100/ADR-091). Confirm at `/reflect`. Keeps the slice off every coordination file → parallel-safe.

## Shippability
Update the audit's existing catalog row (slice-100 #108) to record the tests-surface coverage + the two tests classes + the Option-B guards (RPCD-1/SCPD-1 — consumer-reference propagation for the extended surface). No new rule ⇒ no new RULE-ID row needed; confirm exact row mechanics at build.
