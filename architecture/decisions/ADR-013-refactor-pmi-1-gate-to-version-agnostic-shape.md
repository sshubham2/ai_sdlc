---
id: ADR-013
title: Refactor PMI-1 cleanliness gate to version-agnostic shape (PMI-1 v1.1) — retires N=6 supersession-event churn
date: 2026-05-13
slice: slice-014-refactor-pmi-1-gate-to-version-agnostic-shape
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-013: Refactor PMI-1 cleanliness gate to version-agnostic shape (PMI-1 v1.1)

**Note on rule-ID convention** (per slice-005/008/012 BC-1 v1.x evolution precedent): the rule ID stays **PMI-1**; the methodology-changelog entry at v0.29.0 records the shape refinement as **PMI-1 v1.1**. This mirrors BC-1's evolution lineage (BC-1 v1 at slice-005 keyword-precision → v1.1 at slice-008 negative-anchors → v1.2 at slice-008 same → v1.3 at slice-012 BC-PROJ-2 migration). Introducing PMI-2 would falsely signal a structurally new rule; the methodology rule IS still "Plugin Manifest Invariant — VERSION and plugin.yaml.version must bump atomically". Only the gate-test SHAPE changes. PMI-1 v1.1 captures the shape evolution faithfully while preserving rule-ID lineage. The canonical-phrase pin for slice-014's 3-surface schema-pin discipline is `version-agnostic PMI-1 cleanliness gate` — substantive, 5 words, unique to this refactor.

## Context

The PMI-1 cleanliness gate was introduced at slice-007 (ADR-006 / CAD-1 + PMI-1 closure pattern) as a single test function `test_plugin_yaml_version_matches_version_file_at_0_22_0` in `tests/methodology/test_methodology_changelog.py`. The gate enforces the PMI-1 invariant: `VERSION` (in-repo) and `plugin.yaml.version` MUST bump atomically — the slice-006 escape (one file bumped, the other not) MUST NOT recur.

The original gate function name encoded the current version (`_at_0_22_0`). Every subsequent slice that bumped the version superseded the gate by deleting the prior function and adding a new one with the new version in the name AND in three hardcoded `"0.NN.0"` assertion strings. The supersession discipline grew across slices:

- slice-007 introduced `_at_0_22_0` (N=0 supersession events at slice-end)
- slice-008 first-superseded with `_at_0_23_0` (N=1 events stable)
- slice-009 second-superseded with `_at_0_24_0` (N=2 events stable)
- slice-010 third-superseded with `_at_0_25_0` (N=3 events stable)
- slice-011 fourth-superseded with `_at_0_26_0` (N=4 events stable)
- slice-012 fifth-superseded with `_at_0_27_0` (N=5 events stable)
- slice-013 sixth-superseded with `_at_0_28_0` (N=6 events stable)

By slice-013, the supersession pattern was empirically mechanical: every slice that bumps `VERSION` runs the same ~1-minute Edit (delete prior, add new with literal-version-bumped). The per-bump cost is small individually but the cumulative friction signal is real:

- **N=6 supersession events stable** at slice-013 reflection.
- **Mechanical-feel finding** in slice-013 reflection: *"the version-gate function exists-in-name-only feels increasingly mechanical at N=6"*.
- The aggregate-lessons list in `architecture/slices/_index.md` named `refactor-pmi-1-gate-to-version-agnostic-shape` as the **strongest slice-013+ candidate (corrected post-errata)**.
- Slice-011 N=1 build-time slip (Critic-MISSED) involved the PMI-1 gate's Edit accidentally pulling adjacent entry-pin SECTION content — the gate function's per-version churn IS the operation EPGD-1 (codified at slice-013 Dim 9 7th sub-clause) governs going forward. Retiring the churn closes EPGD-1's primary recurring trigger.

The literal-pin assertions in the per-version gate (`assert version_file == "0.NN.0"`) do not actually enforce the PMI-1 invariant — they enforce a slice-specific version pin. The PMI-1 invariant IS `assert version_file == plugin_version` (cross-file equality). The literal pin's only utility was a secondary "did you bump from the previous version?" check. That secondary check is independently carried by:

- **META-1** (`test_version_matches_most_recent_changelog_entry` at `test_methodology_changelog.py:33`) — asserts `VERSION` matches the latest `## v0.NN.0` heading in methodology-changelog.md. A slice that fails to bump VERSION while creating a v0.29.0 changelog entry fails META-1, independently of PMI-1.
- The slice's mission-brief atomicity checklist (must-not-defer item) — operator-level enforcement that the bump happens.
- The entry-pin tests `test_v_0_NN_0_*_entry_present_in_repo_and_installed` — fails until the v0.NN.0 changelog entry exists.

The three invariants (PMI-1 v1.1 cross-file equality + META-1 VERSION-matches-changelog + INST-1 installed-vs-in-repo-sync) compose to cover the full "did you bump? did you bump atomically? did the installed copy receive the bump?" trio without any per-version-literal pin in the PMI-1 gate test itself.

Without the refactor, every future slice keeps paying the ~1-minute supersession churn, and EPGD-1's primary recurring trigger remains live. With the refactor, the churn terminates at N=6 forever, and EPGD-1 governs other entry-pin / structural-invariant-supersession Edits (e.g., `_lists_N_sub_clauses` structural invariant in `test_critique_agent.py`) without the PMI-1 gate as its highest-frequency surface.

## Options considered

### Option 1 — Refactor to version-agnostic invariant with AST meta-tests (CHOSEN)

Replace `test_plugin_yaml_version_matches_version_file_at_0_28_0` with `test_plugin_yaml_version_matches_version_file_invariant`. The new function:

- Asserts `version_file == plugin_version` (the SOLE assertion — the actual PMI-1 invariant).
- Carries a pinned error-message containing both `"PMI-1"` and `"slice-006 escape"` substrings — the defect-class trace per slice-007 closure pattern.
- Contains NO hardcoded version literal anywhere in body or docstring.

Two AST meta-tests defend the new shape against future regression:

- `test_pmi_1_gate_function_is_version_agnostic_shape` — AST-walks the test file's module, locates the `_invariant` `FunctionDef`, walks its body for any `Constant(value=str)` matching `r"^\d+\.\d+\.\d+$"`, asserts NONE found.
- `test_no_per_version_pmi_1_gate_functions_remain` — AST-walks the test file's module, locates any `FunctionDef.name` matching `r"^test_plugin_yaml_version_matches_version_file_at_0_\d+_0$"`, asserts the list is EMPTY.

A regression test (`test_pmi_1_gate_fails_with_pinned_message_when_version_files_diverge`) uses pytest's `monkeypatch` to swap `REPO_ROOT` with a tempdir containing mismatched VERSION + plugin.yaml files; asserts `AssertionError` raised with both pinned substrings present in `args[0]`.

**Pros**:

- Retires per-version-bump test churn permanently from slice-015 onward. N=6 supersession events stable terminates at N=6; the supersession-event counter does NOT continue to ratchet.
- Two AST meta-tests provide structural defense against any future regression that smuggles a version literal back in OR re-introduces an `_at_0_NN_0`-shaped function. The defense is structural (AST-level), not prose-level — robust against rephrasing.
- The pinned error-message substrings (`"PMI-1"` + `"slice-006 escape"`) preserve the defect-class trace established at slice-006/007 — future PMI-1 failures still surface with the historical context.
- EPGD-1 self-application: slice-014's own PMI-1 supersession Edit is the LAST one — slice-014 IS the canonical reference instance of EPGD-1's last application on the PMI-1 versioned-gate surface. (a) Slice-014 follows EPGD-1's narrow-scope discipline at /build-slice Phase 1c; (b) slice-014 retires the very pattern EPGD-1 governs going forward on this surface. The (a) ↔ (b) duality is recursive-self-application (RSAD-1) at the methodology-evolution level — distinct from RSAD-1's design-time-stress-test sub-mode, slice-014 demonstrates RSAD-1 at the discipline-retirement level. N=6 cumulative RSAD-1 evidence post-codification (slices 009 → 010 → 011 → 012 → 013 → 014).
- N-surface schema-pin discipline ratchets from N=2 instances stable (RSAD-1 v0.26.0 + EPGD-1 v0.28.0) to **N=3 instances stable** at slice-014 (PMI-1 v1.1 v0.29.0). Canonical phrase `version-agnostic PMI-1 cleanliness gate` pinned across (1) ADR-013 + (2) in-repo methodology-changelog v0.29.0 + (3) installed methodology-changelog v0.29.0.
- Reversibility: cheap with magnitude-of-revert justification. ~30 min one-time revert (re-introduce `_at_0_NN_0` test for the then-current version + delete the 4 new tests; revert version-bump if undoing the v0.29.0 ship at the same time). PLUS recurring 1-min × N future slices cost reintroduced. The cumulative-revert-cost is the real magnitude justification: cheap individually, recurring forever if not.
- Aligns with slice-013 reflection's explicit candidate framing.

**Cons**:

- The "did you bump at all?" secondary check that the literal-pin carried is REMOVED. Mitigated by the 3-way composition (PMI-1 v1.1 + META-1 + entry-pin tests + mission-brief checklist) — see Context for the analysis.
- One-time slice cost (~30-45 min) to ship the refactor including 4 new tests + ADR + methodology-changelog v0.29.0 entry + atomic version bump + shippability catalog row + bidirectional sha256 forensic capture. Amortized across all future slices that would have paid the per-bump churn (N → ∞).

### Option 2 — Keep current per-version shape; document the friction as acceptable (REJECTED)

Defer the refactor indefinitely. Each future slice continues to supersede the gate by deleting prior + adding new with literal-version-bumped.

**Pros**:
- Zero one-time slice cost (no refactor needed).
- Preserves the literal-pin's "did you bump from the previous version?" secondary check inside the gate test itself (no reliance on META-1 + entry-pin composition).

**Cons**:
- N=6 friction signal is real and growing. Every future slice pays ~1 minute on a mechanical operation. By slice-020 the cumulative supersession churn is 12 minutes; by slice-050 it's 42 minutes — all on the same boilerplate.
- The mechanical-feel framing in slice-013 reflection signals that this is at the threshold where the friction crosses into "should be retired" territory. The aggregate-lessons explicitly names the refactor as the strongest slice-013+ candidate.
- Slice-011 N=1 build-time slip (Critic-MISSED) shows that the per-version supersession Edit IS the primary recurring trigger for EPGD-1. Every supersession is a fresh opportunity for the Edit-discipline failure. Retiring the supersession retires the trigger.
- The literal-pin's secondary check is NOT actually load-bearing — META-1 + entry-pin tests + mission-brief atomicity checklist independently cover it (see Context analysis). The literal-pin's apparent value is a halo from looking similar to the actual PMI-1 invariant; removing it does not weaken any invariant.

Rejected: friction signal at N=6 + recurring EPGD-1 trigger + non-load-bearing literal-pin justify the one-time refactor cost.

### Option 3 — Migrate PMI-1 to methodology-changelog source-of-truth (PMI-1 v2) (DEFERRED)

Re-architect PMI-1 so that `methodology-changelog.md`'s latest `## v0.NN.0` heading IS the source of truth, and `VERSION` + `plugin.yaml.version` MUST derive from it. The gate test parses the changelog, extracts the latest version, asserts both files match.

**Pros**:
- Strongest "did you bump at all?" coverage — a slice that bumps `VERSION` to 0.29.0 but adds the v0.30.0 changelog entry would fail (version mismatch with the latest changelog heading).
- Source-of-truth becomes the human-authored methodology-changelog rather than a version-file-as-string.

**Cons**:
- Introduces a parse step on the methodology-changelog markdown structure inside a test — increases test code surface and tightly couples PMI-1 to the changelog's prose format (any future heading format change breaks PMI-1).
- Larger slice scope (~1-2 hours minimum) — exceeds the slice-014 sizing budget (~30-45 min per slice-013 reflection).
- Deferred to a future slice IF cross-cutting friction surfaces between v1.1 META-1 PMI-1 INST-1 interactions.

Rejected at slice-014 scope; recorded as v2 candidate.

### Option 4 — Build `tools/pmi_1_audit.py` standalone audit (REJECTED at slice-014; deferred)

Move PMI-1 from prose-pin-discipline (single test function) to an audit module with the same shape as `tools/build_checks_audit.py` / `tools/install_audit.py` etc. The audit module would expose a CLI + library API and could be invoked from CI hooks, /drift-check, /validate-slice.

**Pros**:
- Aligns PMI-1 with the audit-enforced-gate convention used by BC-1 / INST-1 / VAL-1 / WIRE-1 / CAD-1 / TF-1 / RR-1 (each has a `tools/*_audit.py` module).
- Standalone CLI + library invocation surface beyond pytest.

**Cons**:
- Adds module surface (~150-300 lines + tests) for what is currently a single 12-line assertion. Over-engineering for the actual PMI-1 invariant size.
- Deferral was explicit at slice-007 (PMI-1 stays prose-pin-discipline-only); slice-014 does not have a friction signal demanding the v2 audit module promotion.
- v2 candidate; defer until N≥2 PMI-1 escape recurrences post-refactor surface OR cross-cutting parity with other audit modules becomes a coherence issue.

Rejected: prose-pin discipline is the right size for PMI-1's invariant complexity.

## Decision

**Option 1**: refactor PMI-1 to version-agnostic shape via `_invariant` function + 2 AST meta-tests + 1 regression test, codify as **PMI-1 v1.1** in methodology-changelog v0.29.0 entry, terminate the per-version supersession-event counter at N=6 (slice-006-013 → slice-014 retires), and preserve the "did you bump?" secondary coverage via the existing META-1 + entry-pin tests + mission-brief atomicity checklist composition. Canonical phrase `version-agnostic PMI-1 cleanliness gate` pinned across N=3 surfaces. Atomic version bump 0.28.0 → 0.29.0 across VERSION + plugin.yaml + ai-sdlc-VERSION.

## Consequences

### Components affected
- `tests/methodology/test_methodology_changelog.py` — 1 narrow-scoped Edit removing the legacy gate function + its SECTION header; 4 new functions in 3 new SECTIONs (1 invariant + 2 AST meta-tests + 1 regression test + 1 ADR-pin = 5 functions actually — invariant, is_version_agnostic_shape, fails_with_pinned_message, no_per_version_remain, adr_013_exists); plus 1 new v0.29.0 entry-pin SECTION + 2 entry-pin functions (`test_v_0_29_0_pmi_1_v1_1_entry_present_in_repo_and_installed` + `test_v_0_29_0_entry_names_supersession_pattern_retired`). All previously-existing entry-pin functions for v0.22.0..v0.28.0 are NOT touched (EPGD-1 self-application empirical verification at Phase 4).
- `methodology-changelog.md` (in-repo + installed) — new v0.29.0 entry with explicit `Supersession pattern retired at slice-014` prose line replacing the running supersession-event-counter prose that v0.22.0..v0.28.0 entries carried.
- `VERSION` + `plugin.yaml` + `~/.claude/ai-sdlc-VERSION` — atomic bump 0.28.0 → 0.29.0.
- `architecture/shippability.md` — row 14 (8 pytest commands) added.
- `architecture/decisions/ADR-013-refactor-pmi-1-gate-to-version-agnostic-shape.md` — this file.

### Behaviors implied
- **From slice-015 onward**: PMI-1 gate is NOT superseded per-version. Slices bump VERSION + plugin.yaml + ai-sdlc-VERSION atomically and run the existing `_invariant` test unchanged. Pre-Phase-1c grep on `_at_0_NN_0` patterns returns ZERO matches in `test_methodology_changelog.py` post-slice-014.
- **EPGD-1 governance scope shifts** — slice-013 codified EPGD-1 with PMI-1 versioned-gate supersession as its primary recurring trigger. Post-slice-014 retirement, EPGD-1's primary triggers become other entry-pin / structural-invariant-supersession Edits (e.g., `_lists_N_sub_clauses` structural invariant in `test_critique_agent.py`). EPGD-1 itself does NOT need re-codification; only its observed-trigger profile shifts.
- **META-1 + entry-pin composition** becomes the load-bearing "did you bump?" check. META-1 + per-version entry-pin tests + mission-brief atomicity checklist must each remain in place; removing any one weakens the composition.
- **Per-slice version-bump TF-1 row** disappears from future mission briefs. Slices no longer need to plan PMI-1 supersession as a Phase 1 build step; only `VERSION` / `plugin.yaml.version` / `ai-sdlc-VERSION` file edits + entry-pin function addition.

### Future flexibility
- Adding a 3rd file to the PMI-1 atomic-bump invariant (e.g., a `claude_plugin_version_marker` future addition) requires extending the `_invariant` function with one new assertion + updating the regression test fixtures. No supersession needed.
- Migrating to PMI-1 v2 (changelog source-of-truth) is a separate slice; the v1.1 invariant + AST meta-tests preserve correctness during the transition.
- If PMI-1 escape recurs post-refactor (gate doesn't fire when it should), the regression test is the diagnostic — re-exercise it manually with a known-bad fixture; if it still PASSES with the bug, the gate's logic is broken and a fix slice is needed.

## Reversibility

**Class: cheap.** Frontmatter `reversibility: cheap` matches ADRs 003/004/006/007/008/009/010/011/012 single-token convention (per slice-014 /critique m1 ACCEPTED-FIXED). Magnitude-of-revert justification follows in body prose below — the class is `cheap` because no irreversible portion exists, but the recurring-revert-cost (1-min × N future slices) is large enough to merit explicit discussion.

Single-revert magnitude: ~30 min. Revert path:
1. Re-introduce `test_plugin_yaml_version_matches_version_file_at_0_29_0` (single function with literal pins) in `test_methodology_changelog.py`.
2. Delete `test_plugin_yaml_version_matches_version_file_invariant` + the 4 supporting tests (`_is_version_agnostic_shape`, `_fails_with_pinned_message_when_version_files_diverge`, `_no_per_version_pmi_1_gate_functions_remain`, `_adr_013_exists_and_names_pmi_1_refactor_canonical_phrase`).
3. Delete v0.29.0 changelog entry from in-repo + installed methodology-changelog.md.
4. Optionally retract the version bump (0.29.0 → 0.28.0) — IF reverting the entire slice; IF reverting just the refactor, keep the version bump and re-introduce `_at_0_29_0` at the current version.
5. Mark ADR-013 as `superseded` with the superseding ADR's number.
6. Restore the legacy SECTION headers; remove the new SECTION headers.

Recurring-revert-cost: 1-min × N future slices of supersession-event churn reintroduced. The cumulative-revert-cost grows monotonically with future slice count; at N=15 slices post-revert, the cumulative supersession cost matches the one-time slice-014 refactor cost (15 × 1 min ≈ 30 min × 0.5 = the slice-014 refactor's actual effective cost). At N>15 the revert becomes net-negative.

No structurally irreversible portion: the `## v0.29.0 — methodology entry` prose history is bounded (it doesn't get rewritten); the methodology-changelog's append-only nature means a future re-introduction of `_at_0_NN_0`-shape gates would write a NEW v0.NN.0 entry retracting PMI-1 v1.1 — clean evolution with full audit trail.

The magnitude justification is the recurring-revert cost (1-min × N), not the one-time revert cost. The decision IS cheap because the magnitude only compounds against the user, not against the system's structural integrity.

## Recursive-self-application audit (RSAD-1 stress-test)

Per slice-011 RSAD-1 codification at Dim 9 6th sub-clause: any slice authoring or refining a methodology rule MUST stress-test its own draft against the very discipline being encoded.

Stress-test for ADR-013 + slice-014:

- **Does this ADR commit version-literal pinning that slice-014's refactor would refuse?** No. `0.29.0` appears in this ADR (Context, Decision, Consequences, Reversibility sections). All occurrences are about the atomic-bump EVENT this slice executes. None are inside the proposed `_invariant` function's body. The version-agnostic-shape rule applies to the gate test, NOT to entry-pin / ADR text (which IS per-version by definition).
- **Does this ADR retire a discipline it depends on?** Slice-014 retires the PMI-1 versioned-gate supersession pattern. The PMI-1 invariant (atomic bump cross-file equality) is PRESERVED. The retirement is narrow; transitive dependencies (META-1, entry-pin tests, mission-brief atomicity, INST-1 install-audit) are intact.
- **Does this slice ship its own ADR-013 using the very ADR-pin convention it depends on for AC #4?** Yes. ADR-013 is created by this slice; row 7 of the TF-1 plan asserts ADR-013 exists + contains the canonical phrase. The ADR-pin test PASSES only after ADR-013 is committed. Slice-014 IS the canonical reference instance of "the slice authoring the refactor IS the canonical reference instance of the discipline's last application" — the (a) ↔ (b) duality of EPGD-1 self-application at the discipline-retirement level.

RSAD-1 stress-test PASSES at design time. RSAD-1 cumulative evidence post-codification: N=5 at slice-013 → **N=6 at slice-014** (slices 009 → 010 → 011 → 012 → 013 → 014).
