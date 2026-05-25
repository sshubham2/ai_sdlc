---
id: ADR-026
title: Rollup cp1252 sentinel asserts repo-state-derived bidirectional coverage-parity, not a version-pinned tool count
date: 2026-05-16
slice: slice-028-refactor-utf8-rollup-sentinel-version-agnostic
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-026: Version-agnostic UTF-8 rollup sentinel

## Context

**Canonical phrase** (N=3 surface schema-pin, per slice-013 EPGD-1 / slice-015 SCPD-1 precedent): `version-agnostic UTF-8 rollup sentinel` — pinned across the sentinel docstring + methodology-changelog v0.42.0 entry (in-repo + installed, bidirectional byte-equality) + this ADR-026 body.

The UTF-8 rollup sentinel `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input`
(`tests/methodology/test_utf8_stdout_regression.py`) asserted an absolute
literal count of audit tools (`assert len(actual_audits) == 20`) plus a
hand-maintained `post-slice-027` ledger comment ("17 post-slice-023 + 1
post-slice-025 + 1 post-slice-026 + 1 post-slice-027"). Every slice that
adds a `tools/*.py` audit tool had to manually bump the literal and extend
the ledger or the methodology suite went red. This count was bumped at
slices 023 → 025 → 026 → 027 (N=5 with slice-028) — a recurring, purely
mechanical maintenance tax flagged in slice-027 aggregated lessons
(`architecture/slices/_index.md` lines 40-41) as the strongest standing
deferred candidate.

The count was never the property worth protecting. The sentinel exists so
that **no audit tool silently escapes cp1252 regression coverage**. `== 20`
is a brittle proxy for that invariant: it fails on a count mismatch without
naming what is actually wrong, and it passes even if the wrong 20 tools are
covered.

This is the same defect class slice-014 / [[ADR-013]] retired for the PMI-1
cleanliness gate (per-version `_at_0_NN_0` literal gate → version-agnostic
cross-file-equality invariant). PMI-1 v1.0 → v1.1 is the precedent template.

## Options considered

1. **Keep `== N`, add a process reminder** (slice-027 line-40 lesson:
   "count-agnostic greps"). Pros: zero code change. Cons: does not retire
   the tax — every tool-adding slice still edits the literal; a forgotten
   bump still reds the suite; the proxy weakness (right count, wrong tools)
   remains. Rejected — treats the symptom, not the class.
2. **Derive the expected count dynamically** (`assert len(actual) ==
   len(expected_registry)`). Pros: no version literal. Cons: still a count
   equality — a mismatch names a number, not a tool; tolerates two
   compensating errors (one tool dropped, one phantom added). Rejected —
   version-agnostic but still a proxy.
3. **Bidirectional coverage-parity, covered-set = a hand-maintained
   in-module registry the parity assertion reads.** No count literal, no
   version anchor. Pros: single source of truth. **Rejected (/critique B2 +
   M1 + M2)**: a registry the assertion *reads* is the covered-set *by
   declaration, not observation*. A future slice could add a tool name to
   the registry to make parity pass WITHOUT writing the corresponding
   `_run_under_cp1252` test — suite green, tool never exercised, the N=6
   cp1252 regression class (slices 007/016/018/020/021/022) silently
   re-opens. This is strictly weaker than the status quo and directly
   defeats mission-brief AC#2 ("adding one without coverage makes the suite
   red"). It also forces either a names-only list (the declaration hole) or
   a registry carrying per-tool argv callables (materially enlarges the
   slice and touches per-tool tests the mission-brief puts out of scope).
   There is no slice-014 analogue — PMI-1's invariant asserts a *disk-fact
   equality* (`VERSION == plugin.yaml.version`), an observed fact, never a
   declared list.
4. **Bidirectional coverage-parity, covered-set OBSERVED from the real test
   surface by AST introspection** (chosen). `discovered_set` = each
   `tools/*.py` (non-`_`, non-`__init__`) whose module AST has a top-level
   `main` FunctionDef (mirrors `tools/utf8_stdout_audit.py::_find_main_function`
   semantics — the `tools_with_main` denominator UTF8-STDOUT-1 actually
   governs, NOT the looser `_candidate_tools` glob). `covered_set` =
   AST-read from *this module's actual cp1252 call sites*: the string
   elements of `_POSITIONAL_SLICE_TOOLS`/`_ROOT_ONLY_TOOLS` (the parametrize
   sources) ∪ the second positional arg of every
   `_assert_no_encoding_error(proc, "<tool>")` call in the bespoke
   `test_*` functions. The parametrize direction is **execution-bound**
   (pytest parametrizes over those exact strings and runs the subprocess);
   the bespoke direction is a **source-presence proxy** — materially
   stronger than option-3's free-floating list (you must edit a real test
   call site) but NOT a verified execution observation (the
   argv↔assertion-name binding is unverified — a copy-paste bug naming the
   wrong tool, or a `skip`/`xfail`, would still satisfy that direction; the
   per-tool tests themselves are the execution guarantee there). The "cannot
   enter covered-set without an executed test" claim is therefore NOT made
   (resolves /critique-review B2 over-claim adjustment, held to the same
   ADR-013 honesty convention as M2). No count literal, no version anchor;
   bidirectional failure names the offending tool(s). Bespoke bodies + list
   constants are untouched (mission-brief out-of-scope honored). Pros:
   retires the tax, strengthens the invariant toward observation,
   removal/rename needs zero ledger edit. Cons: a second AST surface (each
   `tools/*.py` for discovered-set; this module for covered-set) + the
   bespoke-direction proxy residual — accepted as the cost of
   source-observation-over-declaration within mission-brief scope.

## Decision

Adopt option 4. Refactor the rollup sentinel to assert repo-state-derived
**bidirectional** coverage-parity: `discovered_set` (per-tool AST
`main`-filter over `tools/*.py`) `==` `covered_set` (AST-read from this
module's real cp1252 call sites — parametrize-list string elements
[execution-bound] ∪ bespoke `_assert_no_encoding_error` second args
[source-presence proxy]). Set *construction* lives in two named
module-level helpers (`_discovered_audit_tools`, `_covered_tool_tokens`);
the **parity assertion stays in the sentinel FunctionDef body** (NOT
extracted) so the AST meta-test still scans the count-literal-risk site —
the meta-test scan scope is widened to also cover both helper bodies, plus
a counter-anchor meta-test asserts the helpers exist and are the scanned
ones (resolves /critique-review B-add-1: helper-extraction would otherwise
move logic out of the scanned body, fail-OPEN). `_covered_tool_tokens`
fails LOUDLY on any non-`Constant(str)` list element / assertion arg —
never silently skips (resolves /critique-review M-add-1: silent-skip would
drop coverage tokens, fail-OPEN). The failure-path regression test injects
synthetic sets via `monkeypatch` of the two helpers (slice-014-faithful —
slice-014 monkeypatched `REPO_ROOT`, did not extract the gate logic).
Covered-set is source-observed from the test surface, never a
hand-maintained declaration (option 3 rejected for the declaration hole).
Rule-ID lineage is preserved: this is
**UTF8-STDOUT-1 v1.1**, not a new rule ID — mirroring PMI-1 v1.0 → v1.1
([[ADR-013]]). The 3-part template (derive-invariant + AST meta-test +
failure-path regression) is reused verbatim from slice-014.

## Consequences

- Future audit-tool-adding slices add the tool's real cp1252 coverage (a
  parametrize-list entry or a bespoke `test_*`) — the same action they
  already perform — and never touch a count literal or ledger comment. The
  N=5 maintenance-tax class is retired. Satisfying parity requires editing
  a real test call site (parametrize-list entry [execution-bound] or a
  bespoke `test_*` assertion [source-presence proxy]) — not a free-floating
  list as in option 3; the shortcut option 3 allowed is closed (the
  bespoke-direction proxy residual is documented honestly, not claimed away).
- Tool removal/rename needs **zero ledger/registry edit**: the coverage
  call site disappears with the tool in the same localized change, so the
  covered-set token vanishes automatically. The residual edit-on-removal
  that option 3's declaration-registry would have imposed is *eliminated,
  not merely reduced* (resolves /critique M2 honestly — there is no parallel
  list to keep in sync).
- The sentinel now catches an *uncovered* new tool by name and a *phantom*
  coverage token with no matching `main()`-bearing tool — strictly stronger
  than `== N` (which tolerates compensating errors), and stronger than a
  declaration-registry (which tolerates declared-but-unexercised tools).
- **Independent-counter knowledge preserved** (resolves /critique M3b): the
  current sentinel docstring (L213-219) carries the load-bearing note that
  this sentinel's counter is INDEPENDENT of
  `install_audit._CANONICAL_TOOLS` (the INST-1 canonical-tuple counter) —
  the two move for different reasons and must not be collapsed (slice-026
  row 26 / slice-027 row 27 distinguish "INST-1 19→20" vs "UTF8-STDOUT-1
  narrative 17→20"). That note is deleted with the old count body, so the
  knowledge is relocated here and into the refactored sentinel docstring:
  *the version-agnostic sentinel governs `tools_with_main` cp1252 coverage
  parity; it does NOT track and must not be conflated with the INST-1
  `_CANONICAL_TOOLS` canonical-tuple inventory — that is a separate
  propagation site, explicitly out of this slice's scope.*
- methodology-changelog v0.42.0 records UTF8-STDOUT-1 v1.1; shippability
  gains the slice-028 row (SCPD-1); `test_methodology_changelog.py` gains
  the v0.42.0 entry-pin per EPGD-1
  (`test_v_0_42_0_utf8_stdout_1_entry_present_in_repo_and_installed` +
  `_shippability_consumer_propagation` sibling); atomic version bump
  0.41.0 → 0.42.0 under PMI-1 v1.1.
- One new structural invariant to honour going forward: the AST meta-test
  refuses any future regression that smuggles a count literal /
  `post-slice-NNN` anchor back into the sentinel body (same regression
  class slice-014's `test_pmi_1_gate_function_is_version_agnostic_shape`
  guards).

## Recursive self-application (RSAD-1 stress-test)

Per the slice-022 self-violation law (N≈7, fires multi-layer on
audit-adjacent codification slices) and the ADR-013 L166-176 precedent of
an explicit self-stress section, this ADR must confront: *does this
refactor weaken the very invariant it protects?*

- **The predicted self-defect fired at design time.** The first design
  (option 3, declaration-registry) committed exactly the rule's own defect
  class — a "version-agnostic" refactor that silently *weakens* the
  protected invariant (covered-set declared, not observed). /critique B2
  caught it before /build-slice. This is the law behaving as expected:
  the codification slice committed its discipline's defect, caught one
  layer in.
- **Why option 4 does not recommit the option-3 defect.** Under option 3 a
  tool name could enter covered-set with no test edit at all (free-floating
  list). Under option 4 covered-set is read from real test call sites: the
  parametrize direction is execution-bound; the bespoke direction requires
  editing a real `test_*` function's assertion (a source-presence proxy,
  not full execution observation — stated honestly, NOT over-claimed as
  "entails an executed test"). Strictly stronger than option 3, within
  mission-brief scope.
- **The law fired a SECOND layer in — and was caught by /critique-review
  (B-add-1).** The Builder's own option-4 fix initially specified the
  failure-path test via *helper-extraction*, which would have moved the
  count-literal-risk logic OUT of the sentinel FunctionDef the AST
  meta-test scans — re-committing the discipline's defect class (a
  "version-agnostic guard" that is itself trivially defeated) at the
  meta-test layer, this time **fail-OPEN**. slice-014 did not have this
  hole (it monkeypatched `REPO_ROOT`, kept gate logic in-body). Resolution
  adopted: parity assertion stays in-body; set-construction helpers are
  named and the meta-test scan scope is widened to them + a counter-anchor
  meta-test pins that the helpers exist and are scanned; failure-path test
  uses `monkeypatch` of the helpers, not extraction. This is the
  slice-022 law behaving exactly as predicted for audit-adjacent
  codification slices (multi-layer: B2 at layer 1, B-add-1 at layer 2,
  both caught by the dual-Critic stack before /build-slice).
- **Residual watch (handed to /reflect calibration)**: (1) the covered-set
  AST walk now fails LOUDLY (not silently) on unrecognized list-element /
  assertion-arg node shapes (M-add-1) — fail-CLOSED, never fail-open. (2)
  The bespoke-direction source-presence proxy: argv↔assertion-name binding
  is unverified by design; the per-tool tests are the execution guarantee
  there. (3) If a future bespoke test invokes a tool via a
  differently-named assertion helper, the AST walk under-counts covered-set
  → false RED (fail-safe). All three handed to /reflect for the
  helper-shape-drift / proxy-tightening calibration class.

## Reversibility

**cheap.** The change is localized to one repo-only test file (not
mirrored/installed — no CAD byte-equality obligation) plus append-only
vault entries (changelog, shippability row, this ADR) and an atomic
version bump. Reverting is a localized edit restoring the count assertion;
no consumer code, no runtime contract, no data migration. Tagged cheap on
the same basis as ADR-013 (test-shape change, single-file blast radius).
