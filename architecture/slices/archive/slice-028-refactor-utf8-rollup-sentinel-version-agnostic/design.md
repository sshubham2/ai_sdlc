# Design: Slice 028 refactor-utf8-rollup-sentinel-version-agnostic

**Date**: 2026-05-16
**Mode**: Standard

## What's new

- Refactor the rollup sentinel `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` in `tests/methodology/test_utf8_stdout_regression.py` (currently `assert len(actual_audits) == 20` + a hand-maintained "17 post-slice-023 + 1 + 1 + 1" / `post-slice-027` ledger comment). Replace the absolute-count proxy with a **repo-state-derived bidirectional coverage-parity** assertion: `discovered_set == covered_set`.
- **Discovered-set — ONE precise rule** (resolves /critique B1): a `tools/*.py` file is discovered iff its name is not `__init__.py`, does not start with `_`, **AND** its module AST contains a top-level `FunctionDef`/`AsyncFunctionDef` named `main` (semantics mirroring `tools/utf8_stdout_audit.py::_find_main_function`, L104-110). This makes the sentinel's population byte-for-byte the set UTF8-STDOUT-1 actually governs (`audit_root`'s `tools_with_main` denominator, L185-188) — NOT the looser glob in `_candidate_tools` (L93-101) and NOT the current sentinel's pure glob (L221-224). Computing "has top-level `main`" without importing requires the sentinel to **AST-parse each `tools/*.py`** — this is a *second AST read* (the meta-test reads the sentinel's own AST; the discovered-set reads each tool's AST), stated explicitly here, not implied. No subprocess, no `import tools.*` — `ast.parse` on file text only.
- **Covered-set — derived from the REAL test surface by observation, NOT a hand-maintained declaration** (resolves /critique B2 + M1; this is the Critic-recommended option (a), and supersedes the earlier "single in-module registry the parity reads" design). The sentinel AST-introspects *this module* for the tool tokens actually wired into executed cp1252 invocations: (i) the string elements of `_POSITIONAL_SLICE_TOOLS` / `_ROOT_ONLY_TOOLS` (the parametrize sources), and (ii) the second positional argument of every `_assert_no_encoding_error(proc, "<tool>")` call inside the ~7 bespoke `test_*` functions (the tool name each bespoke test declares it exercises). Covered-set = union of (i) and (ii). This is materially stronger than option-3's free-floating declaration list — you must edit a real test call site, and the parametrize-list direction (i) IS execution-bound (pytest parametrizes over those exact strings and runs the subprocess). **Honest residual (resolves /critique-review B2 over-claim adjustment)**: the bespoke direction (ii) is a *source-presence* proxy, NOT a verified execution observation — AST-reading `_assert_no_encoding_error(proc, "tools.foo")`'s second arg proves the literal textually appears as that arg in a `test_*`-named function; it does NOT entail the subprocess in that function was invoked with `tools.foo`'s argv (a copy-paste bug where `proc` ran a different tool but the assertion still names `tools.foo` would satisfy covered-set), nor that the test is not `@pytest.mark.skip`/`xfail`. The argv↔assertion-name binding is unverified by design (verifying it would require executing/parsing every bespoke test's subprocess construction — out of scope, and the per-tool tests themselves are the execution guarantee for that direction). So: parity is *observed-by-source* for (ii) and *execution-bound* for (i) — stronger than declaration, weaker than full execution-observation. The "cannot pass without an executed test" claim is NOT made. The bespoke function bodies and the two list constants are **untouched** (consistent with mission-brief "out of scope: per-tool cp1252 invocation tests' behavior" and "What's reused: kept as-is").
- **Code placement — slice-014-faithful, no parity-logic extraction** (resolves /critique-review B-add-1): the **parity assertion itself** (`assert discovered_set == covered_set`, the only count-literal-smuggle-risk site) stays INSIDE the sentinel FunctionDef body — it is NOT extracted into a helper. Set *construction* lives in two small named module-level helpers `_discovered_audit_tools()` and `_covered_tool_tokens()` (pure functions returning `frozenset[str]`); the sentinel body calls them and asserts parity in-body. The failure-path regression test injects synthetic sets via `monkeypatch` of those two module-level helpers (slice-014-faithful — slice-014 used `monkeypatch` of `REPO_ROOT`, leaving protected logic in-body; we mirror that, NOT helper-extraction of the assertion).
- Add an **AST structural meta-test** pinning the version-agnostic shape: the sentinel FunctionDef body contains no integer-count `Compare`/`Constant` literal and no `post-slice-NNN` string anchor (modeled on slice-014 `test_pmi_1_gate_function_is_version_agnostic_shape`). **Scan scope widened (B-add-1)**: the meta-test scans the sentinel FunctionDef body AND the bodies of `_discovered_audit_tools` / `_covered_tool_tokens` by name (so a count literal cannot hide in a set-construction helper). Plus a **counter-anchor meta-test** (modeled on slice-014 `test_no_per_version_pmi_1_gate_functions_remain`) asserting both helpers exist and are exactly the ones scanned — defeats the "move the logic somewhere unscanned" regression class.
- Add a **failure-path regression test**: a tool present in discovered-set but absent from covered-set (and the reverse — a covered token with no matching discovered tool) makes the sentinel FAIL with a message that **names the offending tool(s)**. Injection is `monkeypatch.setattr` on the two module-level helpers to return synthetic frozensets — the parity assertion under test stays in-body and is genuinely exercised (modeled on slice-014 `test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge`, which monkeypatched the module's `REPO_ROOT` rather than extracting the gate logic).
- **Covered-set AST walk MUST fail closed** (resolves /critique-review M-add-1): `_covered_tool_tokens()` AST-reads `_POSITIONAL_SLICE_TOOLS`/`_ROOT_ONLY_TOOLS` list elements and `_assert_no_encoding_error(proc, "<tool>")` second args. Every such element/arg MUST be a `Constant(str)`; on ANY other node shape (`BinOp` list-concat, `JoinedStr` f-string, `Name`, `Starred`, etc.) the helper raises a **loud named diagnostic** (`AssertionError` naming the offending node + line) — it MUST NOT silently skip. Silent-skip would drop coverage tokens → an uncovered tool falsely GREEN, defeating AC#2. This is the fail-closed analogue of the discovered-set precision rule.
- `methodology-changelog.md` v0.42.0 entry — **UTF8-STDOUT-1 v1.1** (version-agnostic rollup sentinel); rule-ID lineage preserved (NOT a new rule ID — exactly the PMI-1 v1.0→v1.1 precedent).
- `architecture/shippability.md` — append slice-028 row (SCPD-1 / RPCD-1 propagation).
- `architecture/decisions/ADR-026-*.md` (created).
- `tests/methodology/test_methodology_changelog.py` — add the v0.42.0 entry-pin test per EPGD-1, named per the established convention (resolves /critique M3a): `test_v_0_42_0_utf8_stdout_1_entry_present_in_repo_and_installed` + sibling `test_v_0_42_0_utf8_stdout_1_shippability_consumer_propagation` (mirroring the v0.40.0/v0.41.0 pair at `test_methodology_changelog.py` L2238-2344). Build plan MUST assert EPGD-1 self-application: 0 of the N prior `test_v_0_NN_0_*` entry-pin functions touched at function-name level (the slice-011 N=1 Critic-MISSED adjacent-section-pull class, ADR-013 L34/L131).
- Atomic version bump `0.41.0 → 0.42.0` across `VERSION` + `plugin.yaml` `version` + installed `~/.claude/ai-sdlc-VERSION` (PMI-1 v1.1 atomicity).

## What's reused

- [[ADR-013]] / slice-014 — "version-agnostic PMI-1 cleanliness gate" refactor: the canonical 3-part template (derive-the-real-invariant + AST structural meta-test + failure-path regression). This slice applies the *same* template to the UTF-8 rollup sentinel.
- `tools/_stdout.py` `reconfigure_stdout_utf8()` — unchanged; the behaviour the sentinel guards.
- `tools/utf8_stdout_audit.py` — unchanged. Its *effective* governed population is `audit_root`'s `tools_with_main` (L185-188, main()-filtered) — NOT the looser `_candidate_tools` glob (L93-101). The sentinel does **not** import the audit tool; it re-derives the discovered-set independently via `ast.parse` on each `tools/*.py` file's text, applying the same `_find_main_function`-equivalent rule (see "What's new" discovered-set rule). This is deliberate (keeps the regression module import-free of `tools.*` for discovery) and the B1 internal-inconsistency is now resolved by stating the rule once, precisely.
- Existing per-tool parametrized + custom-argv tests in the same module — **bodies untouched**. They remain the actual subprocess cp1252 coverage AND are now the *observed source* the covered-set is AST-read from (call sites, not a parallel list). Only the rollup sentinel body + the two named set-construction helpers + the AST meta-test + counter-anchor + the failure-path regression test change. This is what moves covered-set from option-3 declaration toward source-observation (B2) — execution-bound for the parametrize direction, source-presence proxy for the bespoke direction (see honest residual above) — while honoring mission-brief out-of-scope.
- PMI-1 v1.1 atomic-bump discipline; EPGD-1 entry-pin convention (every changelog version gets a pin test); RPCD-1 / SCPD-1 shippability-catalog propagation; the per-version changelog entry-pin pattern in `test_methodology_changelog.py`.

## Components touched

### `tests/methodology/test_utf8_stdout_regression.py` (modified)
- **Responsibility**: behavioural cp1252 regression coverage for every audit tool + the rollup invariant that no audit tool escapes cp1252 coverage. WHY: closes the recurring Windows cp1252 stdout class (UTF8-STDOUT-1, retired slice-023) and prevents silent coverage gaps as tools are added.
- **Lives at**: `tests/methodology/test_utf8_stdout_regression.py` (modified — sentinel body replaced with bidirectional `discovered_set == covered_set` parity; AST meta-test + failure-path regression test added; bespoke function bodies + the two list constants untouched).
- **Key interactions**: invoked by pytest; `ast.parse`s each `tools/*.py` for the discovered set (main()-filtered) and `ast.parse`s its own module source for the covered set (parametrize list elements + bespoke `_assert_no_encoding_error` second args) and for the meta-test. No new runtime imports of `tools.*`. Not mirrored/installed anywhere (confirmed — repo-only `tests/` file, not a skill/agent/template/changelog install surface; no mini-CAD byte-equality obligation).

### `methodology-changelog.md` (modified, in-repo) + installed mirror
- **Responsibility**: append the v0.42.0 UTF8-STDOUT-1 v1.1 entry. WHY: every codified discipline change is changelog-recorded with rule-ID lineage.
- **Lives at**: `methodology-changelog.md` + forward-synced byte-equal `~/.claude/methodology-changelog.md` (CAD-class; bidirectional sha256 byte-equality, same as slice-023 row 23 / slice-027 row 27).

### `architecture/shippability.md` (modified)
- **Responsibility**: append slice-028 critical-path row. WHY: SCPD-1 — every audit-rule change propagates its consumer refs into the catalog.
- **Lives at**: `architecture/shippability.md` (append-only catalog; prior rows 23/27 left intact — they are historical per-slice entries, not edited).

### `architecture/decisions/ADR-026-*.md` (created)
- **Responsibility**: record the decision "rollup cp1252 sentinel asserts repo-state-derived bidirectional coverage-parity (covered-set observed from the real test surface, not declared), not a version-pinned tool count". WHY: methodology-discipline decision with a structural meta-test contract — same ADR class as ADR-013.
- **ADR numbering** (resolves /critique m1): highest existing decision is **ADR-025** (slice-027; verified via `architecture/decisions/` listing — ADR-001…ADR-025 present, no gaps at the tail). ADR-026 is the correct next number.

## Contracts added or changed

No runtime API / endpoint / event / data-model contract. The contract introduced is a **test-shape invariant** (the rollup sentinel is version-agnostic and asserts bidirectional, *observed* coverage-parity), recorded in [[ADR-026]] and the v0.42.0 changelog entry, and pinned structurally by the new AST meta-test. Canonical phrase `version-agnostic UTF-8 rollup sentinel` pinned across **N=3 surfaces** (sentinel docstring + changelog v0.42.0 entry + ADR-026), mirroring slice-014's `version-agnostic PMI-1 cleanliness gate` N=3 pin. **Pre-build verification (ACCEPTED-PENDING, /critique m2)**: Builder greps the proposed canonical phrase repo-wide before the 3-surface pin to confirm zero pre-existing occurrences (per ADR-013 L69 convention); record the grep result in build-log.md.

## Data model deltas

None.

## Wiring matrix

Per WIRE-1. This slice introduces **no new source/`tools/` modules** — it modifies an existing test file (adding test functions consumed by pytest, an existing consumer) and adds a vault ADR. Zero-row matrix = clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-026]] — rollup cp1252 sentinel asserts repo-state-derived **bidirectional, observed** coverage-parity (discovered-set via per-tool AST main()-filter ⇔ covered-set AST-read from the real test call sites), not a version-pinned tool count and not a hand-maintained declaration registry — reversibility: **cheap**

## Authorization model for this slice

N/A — test-infrastructure refactor, no runtime authorization surface.

## Error model for this slice

No new runtime error codes. The sentinel's `AssertionError` message MUST enumerate the specific offending tool name(s) on failure — both directions:
- **Uncovered tool** (in discovered-set, absent from covered-set): "audit tool(s) `<names>` have no cp1252 regression coverage — add a parametrize-list entry or a bespoke `test_*` for them".
- **Phantom coverage token** (in covered-set, no matching main()-bearing `tools/*.py`): "cp1252 coverage references non-existent tool(s) `<names>` — stale after rename/removal" (PTFCD-1-adjacent phantom-citation guard).

A bare count-delta message is explicitly disallowed (mission-brief must-not-defer).

**AC#3 (removal/rename) — now literally true** (resolves /critique M2): because covered-set is AST-read from the actual test call sites, removing a tool and its `tools/*.py` file plus its parametrize-list entry / bespoke test (the same localized change that removes the tool) keeps parity green with **zero sentinel edit and zero separate ledger/registry edit** — the removed coverage token disappears from covered-set automatically because the call site is gone. There is no parallel hand-maintained list to fall out of sync. The earlier declaration-registry design would have required a relocated ledger edit on removal; that residual is eliminated, not merely reduced.
