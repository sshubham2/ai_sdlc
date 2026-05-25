# Critique: Slice 028 refactor-utf8-rollup-sentinel-version-agnostic

**Critic reviewed**: mission-brief.md, design.md, ADR-026, aggregated lessons from `_index.md`, slice-014 precedent (`test_methodology_changelog.py` L612-779), ADR-013, `tests/methodology/test_utf8_stdout_regression.py`, `tools/utf8_stdout_audit.py`
**Date**: 2026-05-16
**Result**: NEEDS-FIXES

## Summary

The slice intent is sound and the slice-014/ADR-013 precedent is genuinely transferable at the *template* level (derive-real-invariant + AST meta-test + failure-path regression). However the design had a load-bearing internal inconsistency in the discovered-set definition (pure-glob vs. `main()`-filtered) and the chosen "single in-module registry" mechanism re-introduced a *declaration-not-observation* hole that silently weakens the protective invariant. Two blockers, three majors, two minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: Discovered-set definition internally inconsistent (pure-glob vs. `main()`-filtered) — wrong resolution silently weakens the invariant
- **Claim under review**: design.md "discovered under tools/*.py (non-`_`, non-`__init__`, exposing main())" vs. "computes the same discovered set independently ... subprocess-free".
- **Issue**: `tools/utf8_stdout_audit.py::_candidate_tools` (L93-101) is glob-only; the real UTF8-STDOUT-1 denominator is `tools_with_main` (L185-188, main()-filtered). Current sentinel (L221-224) is pure-glob. "Exposing main()" without import requires a second AST read the design did not state. A future non-`_` `tools/foo.py` with no `main()` would be falsely demanded in coverage (false RED) or, under pure-glob, the design text is simply wrong. All 20 tools have `main()` today — coincidence, not invariant.
- **Evidence**: `tools/utf8_stdout_audit.py` L93-101 vs L185-188; `test_utf8_stdout_regression.py` L221-224; design.md "What's new" para 1 vs "What's reused" para 3.
- **Proposed fix**: State discovered-set as ONE precise rule: `tools/*.py` minus `__init__.py`/leading-`_`, AST-confirm top-level `main` FunctionDef (mirror `_find_main_function`), so the sentinel's population == `tools_with_main`. Explicitly state this is a second AST read.

#### B2: "Single in-module registry" makes the parity assertion self-referential — passes while real per-tool cp1252 coverage is absent
- **Claim under review**: design.md "Introduce a single in-module covered-tools registry ... the parity assertion reads."
- **Issue**: A hand-maintained registry the assertion reads is covered-set *by declaration, not observation*. A future slice could add a tool name to the registry to make parity pass WITHOUT writing the `_run_under_cp1252` test — suite green, tool never exercised, the N=6 cp1252 regression class silently re-opens. Strictly weaker than today (the parametrized lists ARE the execution surface). slice-014's PMI-1 `_invariant` asserts a disk-fact equality — no analogue of "a list you can edit to make the assertion pass without changing protected behavior". Directly defeats AC#2 "adding one without coverage makes the suite red".
- **Evidence**: design.md "What's new" para 2; `test_utf8_stdout_regression.py` L79-97 (parametrize lists), L112-200 (7 bespoke fns ARE coverage); ADR-013 L52.
- **Proposed fix**: Covered-set MUST derive from the real test surface (AST-introspect this module for tool tokens in parametrize lists + `_assert_no_encoding_error(proc, "<name>")` second args), OR registry must be the single source that drives the parametrize ids (parity-by-construction). Bare list-literal vs. glob set-equality must be rejected in ADR-026 with reason.

### Majors (address this slice)

#### M1: Bespoke-test coverage not uniformly derivable — "unifies 7 one-off functions" hand-waved
- **Claim under review**: design.md "registry unifies these into one source the parity assertion reads".
- **Issue**: The 7 bespoke functions construct heterogeneous argv (tmp fixtures, `--claude-dir`, `--slice`, positional catalog) — that is *why* they are not parametrized. A names-only registry = pure declaration (B2); a registry carrying argv callables materially enlarges the slice (no longer SMALL/2hr) and touches per-tool tests the mission-brief puts OUT of scope. Unreconciled tension.
- **Evidence**: `test_utf8_stdout_regression.py` L65-68, L112-200; mission-brief "Out of scope" bullet 3; design.md "What's reused" ("kept as-is").
- **Proposed fix**: Adopt option (a): parity = discovered-names ⇔ AST-scanned coverage tokens (parametrize args + bespoke `_assert_no_encoding_error` second arg), bespoke bodies untouched (consistent with out-of-scope). Record in ADR-026 + design.md.

#### M2: Removal/rename direction (AC#3) circular for a declaration-registry
- **Claim under review**: mission-brief AC#3 "no manual ledger edit required"; design.md "phantom registry entry → RED".
- **Issue**: With a declaration-registry, tool removal still requires deleting a registry line (a relocated ledger edit) or the phantom-direction goes RED. Mission-brief frames the tax as *eliminated*; it is only *reduced*. Over-claims. AST-derived-from-real-surface (B2/M1 option a) makes removal genuinely zero-edit — strong argument for that resolution.
- **Evidence**: mission-brief AC#3; design.md "Authorization / Error model"; ADR-013 L75 (honest about removed secondary check).
- **Proposed fix**: Adopt AST-derived covered-set (AC#3 then literally true) OR soften AC#3 + Must-not-defer wording and state residual honestly in ADR-026 Consequences (mirror ADR-013 Cons honesty).

#### M3: Missing entry-pin enumeration + loss of "independent counters" vault knowledge — EPGD-1 + INST-1-confusion recurrence risk
- **Claim under review**: design.md "add v0.42.0 entry-pin test per EPGD-1".
- **Issue**: (1) Entry-pin function name(s) not enumerated per the `test_v_0_42_0_<rule>_entry_present_in_repo_and_installed` + `_shippability_consumer_propagation` convention (L2238-2344); EPGD-1's recurring failure (slice-011 N=1 Critic-MISSED, ADR-013 L34) is adjacent-section pull on under-specified pin Edits. (2) The current sentinel docstring L213-219 carries the "sentinel counter ≠ `install_audit._CANONICAL_TOOLS` counter; do not collapse" knowledge — it will be deleted with the count; design does not say where that knowledge survives.
- **Evidence**: `test_utf8_stdout_regression.py` L213-219; `test_methodology_changelog.py` L2238-2344; ADR-013 L34/L131; aggregated lessons bullet 5.
- **Proposed fix**: (a) Name the v0.42.0 entry-pin function(s) explicitly + assert EPGD-1 self-application (0 of N prior pins touched) in build plan; (b) preserve the "independent counters" note in the refactored sentinel docstring and/or ADR-026 Consequences.

### Minors (log; address if cheap)

#### m1: ADR number collision not verified in design
- **Issue**: ADR-026 is correct (slice-027 shipped ADR-025) but design does not state it verified highest existing ADR; gap from precedent ADR-013 is large/easy to mis-count.
- **Proposed fix**: Confirm `architecture/decisions/` highest is ADR-025 (one `ls`); no design change if confirmed.

#### m2: Canonical phrase uniqueness not pre-validated
- **Issue**: `version-agnostic UTF-8 rollup sentinel` not asserted unique repo-wide before a 3-surface pin (ADR-013 L69 sets the pre-check convention).
- **Proposed fix**: Builder greps the phrase repo-wide pre-build; record in design.md as ADR-013 L69 does.

## Builder draft dispositions

> Draft only — user ratifies in Step 4.5 (TRI-1). The Critic cannot be overridden by the Builder alone.

- **B1** — **ACCEPTED-FIXED** at design.md "What's new" (new "Discovered-set — ONE precise rule" bullet: AST `main`-filter mirroring `_find_main_function`, explicit second-AST-read) + "What's reused" (`_candidate_tools` glob vs `tools_with_main` disambiguated). The internal inconsistency is resolved by stating the rule once, precisely.
- **B2** — **ACCEPTED-FIXED** at design.md "What's new" (covered-set now AST-read from the real cp1252 call sites — observation, not declaration) + ADR-026 Options (option 3 declaration-registry explicitly rejected with the B2 reasoning; option 4 observed-parity chosen) + ADR-026 RSAD-1 stress-test section. A green sentinel now entails an executed cp1252 test for every discovered tool.
- **M1** — **ACCEPTED-FIXED** at design.md (Critic-recommended option (a): covered-set = AST-scanned parametrize elements ∪ bespoke `_assert_no_encoding_error` second args; bespoke bodies untouched — out-of-scope honored). Tension reconciled.
- **M2** — **ACCEPTED-FIXED** at design.md "Error model" (new "AC#3 now literally true" paragraph) + ADR-026 Consequences (residual *eliminated not reduced*, stated honestly per ADR-013 Cons convention). With observed covered-set, removal needs zero ledger edit.
- **M3** — **ACCEPTED-FIXED**: (a) entry-pin function names enumerated in design.md (`test_v_0_42_0_utf8_stdout_1_entry_present_in_repo_and_installed` + `_shippability_consumer_propagation` sibling) + EPGD-1 self-application assertion required in build plan; (b) "independent counters ≠ `install_audit._CANONICAL_TOOLS`" knowledge relocated into ADR-026 Consequences + (build-time) the refactored sentinel docstring.
- **m1** — **ACCEPTED-FIXED** at design.md "Components touched / ADR numbering" (verified highest existing decision is ADR-025; ADR-026 correct).
- **m2** — **ACCEPTED-PENDING**: build-time — Builder greps the canonical phrase `version-agnostic UTF-8 rollup sentinel` repo-wide before the 3-surface pin, records result in build-log.md (noted in design.md "Contracts").

Draft final verdict (pre-triage): **NEEDS-FIXES** — one ACCEPTED-PENDING (m2) present; all blockers/majors ACCEPTED-FIXED. User ratifies in Step 4.5.

## Triage

**Triaged by**: user
**Date**: 2026-05-16
**Final verdict**: NEEDS-FIXES

Reconciles both passes (first Critic critique.md + meta-Critic critique-review.md). User ratified all Builder draft dispositions ("accept all").

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md "Discovered-set — ONE precise rule" (AST `main`-filter == `tools_with_main`, explicit 2nd AST read) |
| B2 | Blocker | ACCEPTED-FIXED | option-4 observed covered-set (AST-read from real call sites); ADR-026 option-3 declaration-registry rejected |
| M1 | Major | ACCEPTED-FIXED | option (a): AST-scan parametrize elements + bespoke `_assert_no_encoding_error` args; bespoke bodies untouched |
| M2 | Major | ACCEPTED-FIXED | observed covered-set → AC#3 literally true; ADR-026 Consequences states residual eliminated honestly |
| M3 | Major | ACCEPTED-FIXED | (a) `test_v_0_42_0_utf8_stdout_1_*` enumerated + EPGD-1 self-app; (b) independent-counter note relocated to ADR-026 |
| m1 | Minor | ACCEPTED-FIXED | highest existing decision verified ADR-025; ADR-026 correct |
| m2 | Minor | ACCEPTED-PENDING | build-time: repo-wide grep of canonical phrase before 3-surface pin, recorded in build-log.md |
| B-add-1 | Blocker | ACCEPTED-FIXED | (meta) parity assertion stays in-body; AST meta-test scope widened to named helpers + counter-anchor; failure-path uses monkeypatch not extraction (slice-014-faithful) |
| M-add-1 | Major | ACCEPTED-FIXED | (meta) `_covered_tool_tokens` fails LOUDLY on any non-`Constant(str)` node — never silent-skip |
| B2-adj | Severity-adjust | ACCEPTED-FIXED | (meta) tempered over-claim: parametrize=execution-bound, bespoke=source-presence proxy; honest residual in ADR-026 RSAD-1 + design.md |

## Dimensions checked
- [x] Unfounded assumptions — B1, M1
- [x] Missing edge cases — M2; empty-set + no-`main()` tool case (B1); concurrency/network N/A (synchronous in-repo refactor)
- [x] Over-engineering — none (single-registry is under-robust per B2, not speculative)
- [x] Under-engineering — B2 (invariant weakened), M3 (pin surface under-specified)
- [x] Contract gaps — B2/M2 (parity "covered" semantics under-defined: declaration vs observation); failure-message contract adequately specified
- [x] Security — none (no auth/input/secret/data path; in-repo test-shape refactor, no runtime surface)
- [x] Drift from vault — none blocking; ADR-026 preserves UTF8-STDOUT-1 lineage correctly; m1 + M3(2) drift-adjacent; self-hosting "not mirrored" claim verified consistent; PMI-1 atomic-bump 0.41.0→0.42.0 correctly enumerated (all three at 0.41.0 verified)
- [x] Web-known issues — not applicable (stdlib `ast`/`pathlib`/`glob`/`subprocess` + pytest, all stable, no external tech); logged not silently-skipped
- [x] Cross-cutting conformance — RSAD-1 slice-022 self-violation law: this IS an audit-adjacent codification slice; B1/B2 are the predicted "did the refactor preserve the real invariant" self-defect; ADR-026 lacks the RSAD-1 stress-test section ADR-013 L166-176 has — recommend adding it. Algorithm-path-conformance + tooling-doc-vs-implementation parity: `_candidate_tools` glob vs `audit_root` main-filtered drift is the substance of B1.
