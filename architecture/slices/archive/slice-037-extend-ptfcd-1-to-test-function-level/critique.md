# Critique: Slice 037 extend-ptfcd-1-to-test-function-level

**Critic reviewed**: mission-brief.md, design.md, ADR-037
**Date**: 2026-05-17
**Result**: BLOCKED (Critic recommendation; final verdict computed at Triage from dispositions)

## Summary

The slice intent is sound and the FILE-level template it extends is proven, but the slice commits the exact recursive self-violation class it codifies (a phantom test-function citation in its own AC4 TF-1 row), and the central "is it prose or an identifier" discrimination — the linchpin of AC3's zero-false-positive claim — is hand-waved in the design while a real archived TF-1 plan (slice-034) contains free-text prose in the `Test function` column that the proposed matcher will false-positive on. The rule-ID/version label also contradicts the project's `-D`-suffix vs `vN.N` conventions, with the most recent directly-analogous precedent (TFFL-1, slice-034) deciding the opposite way.

## Findings

### Blockers (must address before /build-slice)

#### B1: Slice-037's own AC4 TF-1 row cites a phantom test-function — recursive self-violation of the exact discipline being codified
- **Claim under review**: mission-brief.md TF-1 plan AC4 row cites `tests/methodology/test_critique_agent_drift.py` / `test_critique_agent_in_repo_equals_installed`.
- **Issue**: `test_critique_agent_drift.py` defines `test_in_repo_and_installed_critique_agent_are_content_equal` (L62) and does NOT define `test_critique_agent_in_repo_equals_installed`. Function-level phantom citation in the slice's own plan — the exact class this slice codifies (slice-022 law N≈10; identical to slice-025 AC3 + slice-026 AC5). At `/build-slice` Step 6 the slice's own function-level audit would emit `missing-test-function` on this row.
- **Evidence**: `tests/methodology/test_critique_agent_drift.py:62`; slice-025/026 reflections; `_index.md` Aggregated lessons.
- **Proposed fix**: Change AC4 `Test function` to `test_in_repo_and_installed_critique_agent_are_content_equal`; cross-check every slice-037 TF-1 row fn name via `grep -nE "^def "` against the cited file.
- **Builder draft**: ACCEPTED-FIXED — mission-brief AC4 row corrected; all other slice-037 TF-1 rows cross-checked against live source (B1 fix block, this round).

#### B2: AC3 "zero false positives on real repo" is unmet — a real archived TF-1 plan has prose in the `Test function` column and the discriminator is hand-waved
- **Claim under review**: design.md "consult `row.test_function`; when it is a real identifier (not `_EMPTY_SENTINELS`, not prose)"; mission-brief AC3 "zero false positives ... all active/recent TF-1 plans".
- **Issue**: (1) "not prose" predicate undefined; `_EMPTY_SENTINELS` (`test_first_audit.py:91`) does not filter prose. (2) `slice-034/mission-brief.md` has a real PASSING TF-1 row with `test_function = '(full existing module — non-regression)'` (verified live) — not a sentinel; under the design the helper is called with that prose, no `def` matches → false-positive `missing-test-function` on a real archived slice. AC3 demonstrably unmet.
- **Evidence**: `tools/test_first_audit.py:91`; live `test_first_audit` JSON for slice-034; wider archived corpus has many prose `test_function` values.
- **Proposed fix**: Specify the discriminator concretely: enter function-level check only when `row.test_function` matches `^[A-Za-z_][A-Za-z0-9_]*(\[.*\])?$` after strip AND not in `_EMPTY_SENTINELS`; anything with whitespace/`(`/`—`/multiple tokens degrades to FILE-level-only. Add slice-034's prose row as a named regression fixture; scope AC3 to include the archived corpus.
- **Builder draft**: ACCEPTED-FIXED — discriminator regex specified in design.md error model + ADR-038; slice-034 prose row added as named regression fixture in the AC3 TF-1 plan; AC3 wording scoped to archived corpus (B2 fix block, this round).

#### B3: Rule-ID label `PTFCD-1 v1.1` contradicts the `-D`-suffix convention; the most analogous precedent (TFFL-1) minted a new rule-ID instead
- **Claim under review**: mission-brief L41 + design.md L12 "RULE-ID PTFCD-1 v1.1 — version-suffix convention (CCC-1 v1.1 / PMI-1 v1.1 / BC-1 v1.2 / UTF8-STDOUT-1 v1.1)"; entry-pin `test_v_0_50_0_ptfcd1_v1_1_...`.
- **Issue**: All cited `vN.N` precedents are NON-`-D` audit-gate-class rules (`methodology-changelog.md:161,183`). PTFCD-1 is a `-D`-suffix rule (ADR-023; `methodology-changelog.md:219,239`). No `-D` rule has ever taken a `vN.N` label. The single most analogous case — TFFL-1 (slice-034 v0.48.0, an in-place function-granularity refinement of the SAME `test_first_audit.py` surface) — explicitly minted a NEW rule-ID refining TF-1 in place, lineage preserved, supersedes nothing (`methodology-changelog.md:51`). Entry-pin `ptfcd1` also breaks the `<rule>_<numeral>` underscore convention (must be `ptffd_1`).
- **Evidence**: `ADR-023`; `methodology-changelog.md:51,161,183,219,239`; entry-pin naming convention in `test_methodology_changelog.py`.
- **Proposed fix**: Mint a new `-D` rule-ID refining PTFCD-1 in place (supersedes nothing) — `PTFFD-1` "Phantom-Test-Function-citation Discipline"; new ADR documenting the decision per the ADR-023 / ADR-034 precedent; fix entry-pin to `test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed`; align mission-brief AC5 + design + changelog atomically.
- **Builder draft**: ACCEPTED-FIXED — RULE-ID changed to PTFFD-1 (refines PTFCD-1 in place, supersedes nothing) across mission-brief/design; ADR-038 authored documenting the in-place-mint decision per TFFL-1 precedent; entry-pin renamed `test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed` (B3 fix block, this round).

### Majors (address this slice)

#### M1: SCPD-1 / RPCD-1 shippability-catalog consumer-propagation obligation not addressed in design.md
- **Claim under review**: design.md "Contracts" / "What's new" — no `architecture/shippability.md` catalog row for the new audit behavior.
- **Issue**: CLAUDE.md Vault discipline (SCPD-1/RPCD-1) + every prior PTFCD-family slice (slice-025 added shippability row 25 with propagation entry-pin). slice-037 adds a new violation kind to two enforcing audits but neither adds a catalog row nor an explicit no-row justification (slice-032 DEVIATION-1 anti-pattern).
- **Evidence**: `CLAUDE.md` Vault discipline; `architecture/shippability.md:34` (row 25); `test_methodology_changelog.py` `*_shippability_consumer_propagation` entry-pins.
- **Proposed fix**: Add a new shippability row binding the new function-level tests (mirror row 25) + a `test_v_0_50_0_ptffd_1_shippability_consumer_propagation` entry-pin; reflect in mission-brief AC5 + design.md Contracts + verification plan. Decide here, not at `/reflect`.
- **Builder draft**: ACCEPTED-FIXED — design.md Contracts gains an explicit disposition: NEW shippability row 37 (PTFFD-1) binding the function-level tests + `test_v_0_50_0_ptffd_1_shippability_consumer_propagation` entry-pin; mission-brief AC5 + verification plan updated (M1 fix block, this round).

#### M2: ADR-037 observability requirement has no AC, no test-first row, no design element
- **Claim under review**: ADR-037 Decision mandates the human formatter note `function-check skipped (file unparseable)`; nothing delivers it.
- **Issue**: ADR-037 rejected Option 3 (silent skip) *because* of this requirement, but no AC/test/design element covers the formatter change → the rejected silent-skip ships by omission.
- **Evidence**: `ADR-037` Decision + Options #3; mission-brief TF-1 plan; `test_first_audit.py:499` / `shippability_path_audit.py:176` `_format_human`.
- **Proposed fix**: Add a design element (formatter delta in both audits' `_format_human`) + a test-first row asserting the skip-note renders for a `None`-result row that carried a concrete identifier.
- **Builder draft**: ACCEPTED-FIXED — design.md "Components touched" gains the `_format_human` skip-note delta for both audits; mission-brief TF-1 plan gains `test_unparseable_file_emits_skip_note_in_human_output`; ADR-037 requirement now delivered, not superseded (M2 fix block, this round).

#### M3: `_resolve_test_path` already strips `::` — function name can double-source-escape; needs an explicit fallback guard
- **Claim under review**: design.md "What's reused" — "`_resolve_test_path` ... TF-1's function name is the separate `test_function` column".
- **Issue**: `_resolve_test_path:294` strips `::`; if a brief writes `path::test_foo` in the Test path column and leaves the function column as a sentinel, the cited function is never validated — a function-level phantom escapes for exactly the `path::fn` shape the file-level docstring (`:286-288`) defensively handles.
- **Evidence**: `tools/test_first_audit.py:286-288,294`.
- **Proposed fix**: When `row.test_function` is not a checkable identifier but raw `row.test_path` contains a `::selector`, resolve the fn name from the `::`-tail (strip `[param-id]`) and check it. Add fixture; document precedence in design.md + ADR.
- **Builder draft**: ACCEPTED-FIXED — design.md error model gains the fallback precedence (function-column-first, then `test_path` `::`-tail); ADR-037 gains a precedence note; mission-brief TF-1 plan gains `test_path_column_selector_used_when_function_column_empty` (M3 fix block, this round).

### Minors (log; address if cheap)

#### m1: `PhantomCitation` legacy `kind` default not pinned by a test
- **Issue**: Adding `kind` to the frozen dataclass changes call site `:167` + JSON shape; nothing pins that pre-existing file-level phantoms still carry `kind="missing-test-file"` and `to_dict()` retains prior keys.
- **Proposed fix**: One-line assertion in a shippability test for the legacy-default direction + key-superset.
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF-1 plan gains `test_legacy_file_level_phantom_keeps_missing_test_file_kind`; design.md Contracts notes the additive-key superset assertion (m1 fix block, this round).

#### m2: async / nested-class resolution asserted "at any nesting depth" but thinly tested
- **Issue**: Only one shippability-side class-method test; no TF-1-side `async def` / nested-class coverage though the real corpus uses both.
- **Proposed fix**: Add a TF-1-side fixture asserting `async def test_x` and a nested-class method both resolve True.
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF-1 plan gains `test_async_def_and_nested_class_method_resolve_true` (m2 fix block, this round).

## Dimensions checked
- [x] Unfounded assumptions — B2, M3, m2 (see findings)
- [x] Missing edge cases — M3 (`path::fn`-in-path-column), m2 (async/nested), B2 (prose `test_function`)
- [x] Over-engineering — none (`_pyfn.py` is a genuine 2-consumer shared helper; stdlib `ast` only; thin-vault correct)
- [x] Under-engineering — B1 (own AC4 phantom), M1 (no SCPD-1 catalog row), M2 (ADR-037 observability undelivered)
- [x] Contract gaps — m1 (`PhantomCitation.kind` legacy-default not pinned); otherwise CLI/exit contract sound, skip-with-note correct
- [x] Security — none (local CLI audit, no actors/secrets/injection; `_pyfn` swallows OSError/SyntaxError so a malformed file cannot crash the gate)
- [x] Drift from vault — B3 (rule-ID/version label contradicts ADR-019/ADR-023 + TFFL-1 precedent), M1 (SCPD-1 obligation); `_pyfn.py` verified NOT to trip consumer-propagation sentinels (`_`-prefixed helpers excluded by `install_audit.py:71-72`, `test_utf8_stdout_regression:288`)
- [x] Web-known issues — none (pure-stdlib `ast`, no external API/platform surface)
- [x] Cross-cutting conformance — B1 (recursive self-application, design-time mode), B3 (RULE-ID/entry-pin conformance), M1 (SCPD-1 catalog propagation); design.md line-number citations all verified against live source

## Triage

**Triaged by**: user
**Date**: 2026-05-17
**Final verdict**: CLEAN

Reconciles BOTH passes (first Critic + DR-1 meta-Critic `critique-review.md`, verdict EXTEND). User ratified all 12 Builder draft dispositions as ACCEPTED-FIXED; all fixes applied in-round to mission-brief.md / design.md / ADR-037 (amended) / ADR-038 (new).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | AC4 fn renamed to real `test_in_repo_and_installed_critique_agent_are_content_equal` (verified `test_critique_agent_drift.py:62`) |
| B2 | Blocker | ACCEPTED-FIXED | Discriminator regex `^[A-Za-z_][A-Za-z0-9_]*(\[.*\])?$` specified in design+ADR; slice-034 prose row added as named regression fixture; empirically verified by meta-Critic |
| B3 | Blocker | ACCEPTED-FIXED | Rule-ID → PTFFD-1 (new `-D` ID refining PTFCD-1 in place, supersedes nothing); ADR-038 authored per TFFL-1↔TF-1 precedent |
| M1 | Major | ACCEPTED-FIXED | New shippability row 37 (PTFFD-1) + `test_v_0_50_0_ptffd_1_shippability_consumer_propagation` entry-pin specified at design stage |
| M2 | Major | ACCEPTED-FIXED | `_format_human` skip-note delta in both audits + `test_unparseable_file_emits_skip_note_in_human_output` row; ADR-037 observability now delivered |
| M3 | Major | ACCEPTED-FIXED | Function-column-first → `test_path` `::`-tail fallback precedence specified; fixture row added |
| m1 | Minor | ACCEPTED-FIXED | `test_legacy_file_level_phantom_keeps_missing_test_file_kind` + key-superset assertion |
| m2 | Minor | ACCEPTED-FIXED | `test_async_def_and_nested_class_method_resolve_true` row added |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) AC4 tautological-green closed: content-pinning rows `test_critique_dim_9_phantom_citation_function_level_layer_present` + `_names_ptffd_1_rule_id` added per slice-025 precedent |
| M-add-2 | Major | ACCEPTED-FIXED | (meta-Critic) row 37 Machine-cmd enumerated; build-ordering constraint + verification #6 guard the second-order catalog-self-application |
| m-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic) `AuditResult.to_dict()` additive `skip_notes` key noted in Contracts + key-superset assertion |
| m-add-2 | Minor | ACCEPTED-FIXED | (meta-Critic) both-columns-disagree → function-column-wins stated in design error model + ADR-037 |
