# Design: Slice 037 extend-ptfcd-1-to-test-function-level

**Date**: 2026-05-17
**Mode**: Standard

## What's new

- `tools/_pyfn.py` — NEW shared `_`-prefixed helper (mirrors the `tools/_stdout.py` shared-helper precedent): `function_defined_in_file(py_file: Path, func_name: str) -> bool | None`. Returns `True`/`False` if the file parses and the terminal selector name does/doesn't exist as a `FunctionDef`/`AsyncFunctionDef` (at any nesting depth — module-level, class method, nested/async); returns `None` (= "cannot determine, skip") on `SyntaxError` / non-Python / unreadable file (internally swallows `SyntaxError`/`OSError`/`ValueError`/`UnicodeDecodeError` — never raises into the audit). Pure stdlib `ast`. Also exports `is_checkable_function_name(s: str) -> bool` (the B2 discriminator) and `selector_terminal_name(s: str) -> str | None` (strip `[param-id]`, take the last `::`-segment).
- **B2 discriminator (concrete, not hand-waved)**: the function-level check is entered ONLY when the resolved name satisfies `is_checkable_function_name` = `re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\[.*\])?", s.strip())` AND `s.strip().lower() not in _EMPTY_SENTINELS`. Any value with whitespace, `(`, `—`, or multiple tokens (e.g. the real `slice-034` row `(full existing module — non-regression)`) is NOT a checkable name → degrade to FILE-level-only exactly as the empty-sentinel path does. This is the linchpin of AC3 zero-false-positive.
- `tools/test_first_audit.py` — extended: after the existing `missing-test-path-file` FILE-level check (line 483), for a PASSING row whose file *does* exist, resolve the function name **function-column-first, then `test_path` `::`-tail fallback** (M3: when `row.test_function` is not checkable but raw `row.test_path` carries a `::selector`, source the name from that tail so a `path::fn`-in-path-column + empty-function-column row cannot escape). Run `is_checkable_function_name` gate; if checkable, call the helper and emit NEW violation `kind="missing-test-function"` (added to the `TestFirstViolation.kind` doc enum L112-114) when it returns `False`. Helper `None` (unparseable) → no violation, but `_format_human` (L499) emits `function-check skipped (file unparseable)` for that row (M2 — delivers ADR-037's observability requirement).
- `tools/shippability_path_audit.py` — extended: capture the `::`-selector that line 126 currently discards. For a token whose file exists with a selector present, resolve the terminal `::`-segment via `selector_terminal_name` (strip `[param-id]`), gate on `is_checkable_function_name`, call the helper, and append a `PhantomCitation` with NEW `kind="missing-test-function"` when it returns `False`; `None` → no violation + `_format_human` (L176) skip-note. `PhantomCitation` gains a `kind` field defaulting to `"missing-test-file"` for the pre-existing file-level path (m1: legacy direction pinned by test; `to_dict()` key-superset preserved).
- `agents/critique.md` — Dim 9 "Phantom test-file citation discipline" sub-clause refined N=2→N=3-distinct-slice (slice-025 AC3 + slice-026 AC5 + slice-027 B1) with a function-level layer on BOTH sub-modes; SHOULD-list item (1) extended to also assert the cited test *function* exists. Forward-synced to `~/.claude/agents/critique.md` (CAD-1, EOL-agnostic per ADR-033).
- `architecture/shippability.md` — NEW catalog row 37 (PTFFD-1) binding the new function-level tests, mirroring slice-025's row 25; SCPD-1 consumer-propagation obligation discharged here at `/design-slice` (M1 — NOT auto-blessed "no row", NOT deferred to `/reflect`). **Row 37 `Machine-cmd` selectors (enumerated per M-add-2 / SCPD-1 — not "add a row" hand-wave)**: `<interp> -m pytest tests/methodology/test_ptffd1_test_first_audit.py tests/methodology/test_ptffd1_shippability_path_audit.py tests/methodology/test_ptffd1_no_false_positive.py tests/methodology/test_critique_agent.py::test_critique_dim_9_phantom_citation_function_level_layer_present tests/methodology/test_critique_agent.py::test_critique_dim_9_phantom_citation_names_ptffd_1_rule_id tests/methodology/test_methodology_changelog.py::test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed tests/methodology/test_methodology_changelog.py::test_v_0_50_0_ptffd_1_shippability_consumer_propagation --no-header -q`. **Second-order self-application (M-add-2)**: this slice's own newly-live function-level `shippability_path_audit` runs against `shippability.md` at `/validate-slice` Step 5.5, so row 37's selectors must resolve at the *function* level — row 37 is added LAST, only after every cited test file + function and the entry-pins exist (build-ordering constraint, mission-brief smoke gate). This is B1's phantom-citation defect class recurring one layer up (TF-1-plan-self-application → catalog-self-application).
- `methodology-changelog.md` — NEW `## v0.50.0` entry, RULE-ID **PTFFD-1** ("Phantom-Test-Function-citation Discipline"; NEW minted `-D` rule-ID refining PTFCD-1 in place, supersedes nothing — per TFFL-1↔TF-1 precedent, ADR-038); 4-part PMI-1 atomic bump (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md`).
- New test files per the mission-brief TF-1 plan (`tests/methodology/test_ptffd1_*.py`).

## What's reused

- [[slice-025-add-test-file-existence-check-for-non-pytest-rows]] — FILE-level PTFCD-1 is the structural template; the new function-level layer sits immediately after each FILE-level check, gated identically (`row.status == "PASSING"` for TF-1; file-exists for shippability) so PENDING/phantom-FILE rows are never double-reported.
- [[slice-028-refactor-utf8-rollup-sentinel-version-agnostic]] — `ast`-introspection precedent (slice-028 used AST shape checks; same stdlib approach, no new dependency).
- `tools/_stdout.py` — precedent for a shared `tools/_<helper>.py` consumed by multiple audit tools.
- `tools/test_first_audit.py:281-300` `_resolve_test_path` (FILE resolution, unchanged). NOTE (M3): its `::`-split at L294 means a `path::fn`-in-Test-path-column shape — which the code's own docstring L286-288 documents as a real occurrence — is FILE-resolved correctly but the fn is dropped; the function-level layer therefore sources the fn name function-column-first THEN falls back to the raw `test_path` `::`-tail, so that shape cannot silently escape. The columns are NOT assumed always-separate.
- `tools/shippability_path_audit.py:112-129` `_extract_test_tokens` (the `::`-split at line 126 is the exact discard point the selector must be captured before).
- [[decisions/ADR-033]] — EOL-agnostic forward-sync drift (CAD-1) governs the `agents/critique.md` edit.

## Components touched

### `tools/_pyfn.py` (created)
- **Responsibility**: single source of truth for "does Python file F define a test callable named N", with a tri-state result so phantom-detection and parse-failure are not conflated.
- **Lives at**: `tools/_pyfn.py` (created by this slice)
- **Key interactions**: imported by `tools/test_first_audit.py` and `tools/shippability_path_audit.py`; stdlib `ast` only.

### `tools/test_first_audit.py` (modified)
- **Responsibility**: TF-1 strict-pre-finish gate — adds the function-level layer to PTFFD-1.
- **Lives at**: `tools/test_first_audit.py` (modify the `strict_pre_finish` PTFCD-1 block at L471-494; add `missing-test-function` to the `TestFirstViolation.kind` doc-comment enum at L112-114; **M2: extend `_format_human` at L499 to emit `function-check skipped (file unparseable)` for any PASSING row whose resolved fn name was checkable but `_pyfn` returned `None`** — tracked via a new `AuditResult` skip-note list so the formatter can render it).
- **Key interactions**: `tools/_pyfn.py`; consumed by `/build-slice` Step 6.

### `tools/shippability_path_audit.py` (modified)
- **Responsibility**: PTFFD-1 sub-mode (b) pre-catalog gate — adds the function-level layer to shippability `Machine-cmd` pytest selectors.
- **Lives at**: `tools/shippability_path_audit.py` (modify `_extract_test_tokens` L112-129 to return `(token, selector)`; add selector check in `audit_catalog_file` L161-172; add `kind` field to `PhantomCitation` L53-61 defaulting `"missing-test-file"`; **M2: extend `_format_human` at L176 to render the same `function-check skipped (file unparseable)` note** for `None`-result checkable-name tokens).
- **Key interactions**: `tools/_pyfn.py`; consumed by `/validate-slice` Step 5.5.

### `agents/critique.md` (modified)
- **Responsibility**: Critic Dim 9 prose codification of the function-level layer.
- **Lives at**: `agents/critique.md` L194-198 (refine in place — this is prose codification, not an append-only ADR surface); forward-sync to `~/.claude/agents/critique.md`.
- **Key interactions**: CAD-1 content-equality gate (`tools.critique_agent_drift_audit`).

## Contracts added or changed

No HTTP/event contracts. The changed contracts are CLI-tool exit/violation contracts:

- `tools/test_first_audit.py` — adds violation `kind="missing-test-function"` (severity `Important`, same exit-1 path as `missing-test-path-file`). No new flag; rides existing `--strict-pre-finish`. **`AuditResult` (non-frozen `@dataclass`, `test_first_audit.py:122`) gains an additive `skip_notes: list[str]` field for the M2 skip-note; `to_dict()` (asdict-based, L130) therefore extends the `--json` shape additively with a new `skip_notes` key — no removed key (m-add-1, symmetric to m1's `PhantomCitation` concern). A key-superset assertion rides the skip-note test row.**
- `tools/shippability_path_audit.py` — `PhantomCitation` gains a `kind` field (`"missing-test-file"` legacy default for existing behavior, `"missing-test-function"` for the new layer); JSON `to_dict()` shape extends additively (new key, no removed key). Exit code contract unchanged (1 on any violation). **m1: a regression test asserts a pre-existing file-level phantom still emits `kind == "missing-test-file"` AND that `to_dict()` retains every prior key (additive-superset, not shape-replacement)** — the legacy direction is pinned, not merely asserted.

## Data model deltas

None (no persistence). Dataclass shape deltas are covered under Contracts above.

## Wiring matrix

Per **WIRE-1**. The one new module:

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_pyfn.py` | `tools/test_first_audit.py` (PTFFD-1 strict-pre-finish block) + `tools/shippability_path_audit.py` (`audit_catalog_file`) | `tests/methodology/test_ptffd1_test_first_audit.py::test_phantom_function_in_existing_file_is_violation` + `tests/methodology/test_ptffd1_shippability_path_audit.py::test_phantom_function_selector_is_violation` | — |

## Decisions made (ADRs)
- [[ADR-037]] — unparseable / non-Python cited test file → `_pyfn` returns `None`, function-level check skipped with NO violation BUT the human formatter renders a visible `function-check skipped (file unparseable)` note (M2 — observability requirement now delivered, Option 3 silent-skip genuinely rejected). Also carries the M3 fn-name precedence note (function-column-first, then `test_path` `::`-tail). — reversibility: cheap
- [[ADR-038]] — RULE-ID for the function-level extension is a NEW minted `-D`-suffix ID **PTFFD-1** ("Phantom-Test-Function-citation Discipline") that refines PTFCD-1 in place, supersedes nothing — NOT `PTFCD-1 v1.1`; the `vN.N` label is reserved for the NON-`-D` audit-gate naming class, and the most analogous precedent TFFL-1↔TF-1 (slice-034) minted a new `-D` ID. — reversibility: cheap

## Authorization model for this slice

N/A — local CLI audit tools, no actors/permissions. (Not a mandatory-Critic auth trigger; Critic is mandatory here solely on the in-house-methodology-surface trigger: `tools/**`, `agents/critique.md`, `methodology-changelog.md`.)

## Error model for this slice

- **Function-name resolution precedence (M3)**: (1) `row.test_function` if `is_checkable_function_name` passes; else (2) the `::`-tail of raw `row.test_path` (`selector_terminal_name`) if checkable; else (3) no checkable name → FILE-level-only, function-layer not entered. Shippability side has no separate column → selector-tail only. **Both-columns-disagree case (m-add-2)**: when `row.test_function` AND the `test_path` `::`-tail BOTH carry checkable-but-different names, the function column wins and the path-column selector is NOT separately validated — the `Test function` column is the authoritative TF-1 field; checking it is the conservative choice (it never under-checks the authoritative source). This is a deliberate, stated decision, not an oversight.
- **B2 discriminator**: `is_checkable_function_name(s)` = `re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\[.*\])?", s.strip())` AND `s.strip().lower() not in _EMPTY_SENTINELS`. Real prose values like `slice-034`'s `(full existing module — non-regression)` fail this → degrade to FILE-level-only, NOT a false-positive violation. This predicate is the AC3 linchpin and has a named regression fixture (`test_slice034_prose_test_function_is_not_false_positive`).
- `missing-test-function` (TF-1, severity Important) — PASSING row, file exists, resolved fn name checkable, but no matching `def`/`async def` (any nesting depth) in the file. Message names BOTH file AND function (mirrors `missing-test-path-file` message shape).
- `missing-test-function` (shippability `PhantomCitation.kind="missing-test-function"`) — token file exists, `::`-selector present + checkable, terminal name absent. Message names file, row, AND missing function. File-level phantoms retain `kind="missing-test-file"` (m1).
- Parse failure / non-Python / unreadable cited file → `_pyfn` returns `None` → NO violation, BUT `_format_human` (both audits) emits `function-check skipped (file unparseable)` for that row/token so the skip is visible, not silent (M2). Never raises — `_pyfn` swallows `SyntaxError`/`OSError`/`ValueError`/`UnicodeDecodeError` internally.
- Empty `test_function` sentinel (`—`, `n/a`, ``, etc.) AND no checkable `::`-tail → function-level layer not entered; FILE-level-only behavior preserved bit-for-bit (back-compat must-not-defer).
- Parametrized id `test_x[case]` → `selector_terminal_name` strips the trailing `[...]` to the base identifier (out-of-scope: per-param resolution).
- Async tests (`async def test_x`) and methods inside (possibly nested) `class TestX` resolve True — the AST walk is depth-agnostic; `test_async_def_and_nested_class_method_resolve_true` pins this (m2).
