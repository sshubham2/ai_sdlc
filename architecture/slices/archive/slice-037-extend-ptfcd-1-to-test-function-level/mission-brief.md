# Slice 037: extend-ptfcd-1-to-test-function-level

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: closes the function-level phantom-test-citation Critic-stack blind-spot class at N=3 cumulative (slice-025 AC3 + slice-026 AC5 + slice-027 B1) — the project's uncontested strongest standing deferred candidate (`_index.md:79/83`, slice-028)
**Test-first**: true  (per TF-1 — opt-in test-first variant; an audit-detection extension is the canonical test-first shape)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

PTFCD-1 (slice-025) closed phantom test-citation at the FILE level: a PASSING TF-1 plan row or shippability `Machine-cmd` row may not cite a test path whose *file* is absent on disk. But both enforcing audits discard the pytest selector — `tools/test_first_audit.py:294` and `tools/shippability_path_audit.py:126` both do `tok.split("::", 1)[0]`, so a row citing `tests/x/test_real.py::test_does_not_exist` (file exists, function phantom) passes silently. That exact gap was Critic-missed three times (slice-025/026/027) and caught only by downstream gates. This slice extends PTFCD-1 to the test-*function* level so the citation is validated end-to-end, mirroring the proven FILE-level template.

## Acceptance criteria

1. `tools/test_first_audit.py --strict-pre-finish` emits a NEW violation kind (`missing-test-function`) when a PASSING TF-1 plan row's test-path file exists on disk but the resolved test-function name is absent from that file. Function name is sourced function-column-first; when the function column is not a checkable identifier it falls back to the `test_path` `::`-tail (M3). The function-level check is entered ONLY when the resolved name matches the strict Python-identifier shape `^[A-Za-z_][A-Za-z0-9_]*(\[.*\])?$` after strip and is not in `_EMPTY_SENTINELS`; any prose / whitespace / `(` / `—` value degrades to FILE-level-only (B2).
2. `tools/shippability_path_audit.py` emits a NEW violation when a shippability `Machine-cmd` row's test file exists but the cited `::<test_function>` (terminal `::`-segment, `[param-id]` stripped) is absent from that file. Pre-existing file-level phantoms still carry `kind="missing-test-file"` and `to_dict()` retains all prior keys (m1, additive contract).
3. Both extended audits run clean (zero violations) against the *current real* `architecture/shippability.md` AND the full archived + active TF-1-plan corpus (explicitly including `slice-034`'s prose `(full existing module — non-regression)` row) — no false positives on valid existing citations or prose values; rows with NO checkable function name retain FILE-level-only behavior unchanged.
4. `agents/critique.md` Dim 9 "Phantom test-file citation discipline" sub-clause is refined N=2→N=3-distinct-slice with a function-level layer on both sub-modes — verified by **content-pinning** tests (the function-level prose literal + `PTFFD-1` are asserted present, mirroring the slice-025 `test_critique_dim_9_phantom_test_file_citation_*` precedent), NOT by byte-equality alone; `tools.critique_agent_drift_audit` (CAD-1) ALSO stays clean (in-repo ≡ installed, EOL-agnostic per ADR-033). The CAD-1 byte-equality test alone is a tautological green for this AC (M-add-1) — both checks are required.
5. `methodology-changelog.md` carries the new RULE-ID **PTFFD-1** + `test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed` entry-pin + a NEW shippability catalog row (PTFFD-1, SCPD-1 propagation) pinned by `test_v_0_50_0_ptffd_1_shippability_consumer_propagation` + the 4-part PMI-1 atomic v0.50.0 bump; PMI-1 and INST-1 audits clean.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_phantom_function_in_existing_file_is_violation | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_present_function_in_existing_file_is_clean | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_empty_test_function_sentinel_keeps_file_level_only | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_prose_test_function_value_degrades_to_file_level_only | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_path_column_selector_used_when_function_column_empty | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_unparseable_test_file_skips_function_check_no_violation | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_unparseable_file_emits_skip_note_in_human_output | PASSING |
| 1 | unit | tests/methodology/test_ptffd1_test_first_audit.py | test_async_def_and_nested_class_method_resolve_true | PASSING |
| 2 | unit | tests/methodology/test_ptffd1_shippability_path_audit.py | test_phantom_function_selector_is_violation | PASSING |
| 2 | unit | tests/methodology/test_ptffd1_shippability_path_audit.py | test_present_function_selector_is_clean | PASSING |
| 2 | unit | tests/methodology/test_ptffd1_shippability_path_audit.py | test_class_method_selector_resolves_terminal_name | PASSING |
| 2 | unit | tests/methodology/test_ptffd1_shippability_path_audit.py | test_legacy_file_level_phantom_keeps_missing_test_file_kind | PASSING |
| 3 | regression | tests/methodology/test_ptffd1_no_false_positive.py | test_real_shippability_and_full_tf1_corpus_clean_under_func_level | PASSING |
| 3 | regression | tests/methodology/test_ptffd1_no_false_positive.py | test_slice034_prose_test_function_is_not_false_positive | PASSING |
| 4 | methodology | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_citation_function_level_layer_present | PASSING |
| 4 | methodology | tests/methodology/test_critique_agent.py | test_critique_dim_9_phantom_citation_names_ptffd_1_rule_id | PASSING |
| 4 | methodology | tests/methodology/test_critique_agent_drift.py | test_in_repo_and_installed_critique_agent_are_content_equal | PASSING |
| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed | PASSING |
| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_v_0_50_0_ptffd_1_shippability_consumer_propagation | PASSING |

(Version + RULE-ID pre-decided at `/design-slice` per `_index.md:48` against the enforcing convention: methodology **v0.50.0**, RULE-ID **PTFFD-1** "Phantom-Test-Function-citation Discipline". PTFFD-1 is a NEW minted `-D`-suffix rule-ID that **refines PTFCD-1 in place** — rule-ID lineage preserved, **supersedes nothing** — mirroring the TFFL-1↔TF-1 (slice-034) / EOL-DRIFT-1↔CAD-1 in-place-mint precedent (`methodology-changelog.md:51`). NOT `PTFCD-1 v1.1`: the `vN.N` label is reserved for the NON-`-D` audit-gate naming class (CCC-1/PMI-1/BC-1/UTF8-STDOUT-1); `-D` rules mint new IDs (B3 fix, ADR-038). Entry-pin uses the `<rule>_<numeral>` underscore form (`ptffd_1`). Not auto-blessed "no entry"; not adjudicated late at `/reflect`.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | TF-1 func-level violation + skip-note | Fixture brief whose TF-1 row's function exists-as-file but phantom-as-fn; `python -m tools.test_first_audit <fixture> --strict-pre-finish` → exit≠0 + `missing-test-function` naming file AND function. Separate unparseable-file fixture → no violation BUT human output contains `function-check skipped (file unparseable)` (M2) |
| 2 | Shippability func-level violation + legacy kind | Fixture catalog row citing existing file `::test_absent`; `python -m tools.shippability_path_audit <fixture>` → violation `kind="missing-test-function"` naming file AND function; a file-level phantom fixture still emits `kind="missing-test-file"` (m1) |
| 3 | Zero false positives, full corpus | `python -m tools.test_first_audit` on the full archived+active brief corpus (incl. `slice-034`) + `python -m tools.shippability_path_audit architecture/shippability.md` → both clean; slice-034's `(full existing module — non-regression)` prose row degrades to FILE-level-only, NOT a violation (B2) |
| 4 | Critic Dim 9 + CAD-1 | `agents/critique.md` Dim 9 sub-clause refined N=2→N=3 with function-level layer; `python -m tools.critique_agent_drift_audit --repo-root .` → clean |
| 5 | Changelog + catalog + PMI-1/INST-1 | `pytest tests/methodology/test_methodology_changelog.py -k "ptffd_1"`; new shippability row 37 present; `python -m tools.plugin_manifest_audit`; INST-1 → all clean |
| 6 | Second-order self-application (M-add-2) | After the `tests/methodology/test_ptffd1_*.py` files AND `test_v_0_50_0_ptffd_1_*` entry-pins exist AND row 37 is added (in that order), `python -m tools.shippability_path_audit architecture/shippability.md` under the NEW function-level audit → clean: row 37's OWN `Machine-cmd` `tests/methodology/test_ptffd1_*.py::<fn>` selectors all resolve at the function level (the slice's new audit must not phantom-flag its own catalog row — B1's defect class one order higher) |

## Must-not-defer

- [ ] Back-compat: rows with NO `::` selector MUST retain FILE-level-only behavior — zero new false positives (the `_index.md:46/55` audit-self-violation backstop class).
- [ ] Selector-shape handling: both `path::fn` and `path::Class::method` resolve correctly to the function/method name being asserted.
- [ ] Error handling: an unparseable / syntax-error test file degrades gracefully (documented disposition — fail-closed vs skip-with-note decided at `/design-slice`), never an audit crash.
- [ ] Observability: violation message names BOTH the file AND the missing function (actionable, mirrors FILE-level message shape).
- [ ] RULE-ID + entry-pin + 4-part version-bump obligation pre-decided at `/design-slice` against the enforcing audit (`_index.md:48` discipline) — not auto-blessed "no entry" (slice-032 DEVIATION-1 anti-pattern), not adjudicated late at `/reflect`.

## Out of scope

- Detecting test functions that exist but are `skip`/`xfail` (present ≠ phantom — not this class).
- Parametrized-test id resolution (`test_foo[case1]`) — match on the selector base name only.
- Pytest collection-time semantics (conftest fixtures, dynamically generated tests, `pytest_generate_tests`).
- The shippability Step-5.5 catalog-runner per-`;`-segment-backtick contract (R-8) — separate slice candidate #2, not touched here.
- Any change to the `::`-split contract outside the two PTFCD-1 audits.

## Dependencies

- Prior slices: [[slice-025-add-test-file-existence-check-for-non-pytest-rows]] — FILE-level PTFCD-1 is the proven template this extends; [[slice-028-refactor-utf8-rollup-sentinel-version-agnostic]] — AST-introspection precedent.
- Vault refs: [[decisions/ADR-033]] (EOL-agnostic drift, CAD-1); `agents/critique.md` Dim 9; `architecture/shippability.md`.
- Risk register: none open in this class (this is a Critic-blind-spot codification, not a risk-register entry).

## Mid-slice smoke gate

At ~50% of build, run the BC-PROJ-4 dogfood (the decisive artifact for audit-parse-rule slices, `_index.md:54`):
```
python -m tools.test_first_audit <crafted-fixture-with-phantom-fn> --strict-pre-finish   # expect: missing-test-function violation
python -m tools.test_first_audit architecture/slices/slice-037-extend-ptfcd-1-to-test-function-level --strict-pre-finish   # expect: own TF-1 plan clean
python -m tools.shippability_path_audit architecture/shippability.md   # expect: zero false positives on real catalog
```
Expected: phantom-function fixture FAILs with the new kind; real repo artifacts stay clean. If a real-repo false positive appears: STOP, scope the matcher tighter, don't continue.

**Build-ordering constraint (M-add-2 — second-order self-application)**: shippability row 37 and the AC5 `test_v_0_50_0_ptffd_1_*` entry-pins MUST be added AFTER (a) the `tests/methodology/test_ptffd1_*.py` test files exist with their cited functions and (b) the entry-pin functions exist in `test_methodology_changelog.py`. Adding row 37 before its Machine-cmd targets exist would make the slice's own newly-live function-level `shippability_path_audit` phantom-flag its own catalog row at `/validate-slice` Step 5.5 (B1's defect class at the catalog layer). Sequence: write test files → write entry-pins → add row 37 → run the smoke gate's `shippability_path_audit` last.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
