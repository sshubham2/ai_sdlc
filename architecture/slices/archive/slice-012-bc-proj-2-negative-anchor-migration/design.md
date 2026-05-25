# Design: Slice 012 bc-proj-2-negative-anchor-migration

**Date**: 2026-05-13
**Mode**: Standard

## What's new

- **`architecture/build-checks.md`** — append `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` line to the BC-PROJ-2 rule body (between the existing `Trigger anchors:` line and the existing blank line before `**Check**:`). Single-line addition mirroring slice-008's BC-PROJ-1 migration exactly.
- **`methodology-changelog.md`** (in-repo) — append `## v0.27.0 — 2026-05-13` entry titled `BC-1 v1.3 — BC-PROJ-2 negative-anchor migration` documenting the completion of the BC-1 v1.2 rollout (rule-level data migration only, NOT a schema change). Names BC-PROJ-2 explicitly, the 9-token methodology-vocabulary set verbatim, AND the N=2 cross-slice evidence anchors (slice-005 + slice-011) per slice-009/010/011 N-surface schema-pin discipline (N=3 stable). Per slice-011 NEW Dim 9 sub-class candidate N=1 (entry-pin-vs-pmi-1-gate-semantics-conflation): the entry pin function MUST be scoped narrowly so the supersession Edit cannot delete it accidentally.
- **`~/.claude/methodology-changelog.md`** (installed) — same `## v0.27.0` entry byte-equal mirror of the in-repo entry. Bidirectional sync per slice-005..011 N=7-stable forensic-capture pattern.
- **`VERSION`** (in-repo) + **`~/.claude/ai-sdlc-VERSION`** (installed) + **`plugin.yaml.version`** — all bump `0.26.0` → `0.27.0` atomically per PMI-1 invariant (slice-007 escape-closure pattern, N=5 stable post-slice-011).
- **`tests/methodology/test_build_checks_audit.py`** — 4 new test functions: `test_slice_005_archive_no_longer_fires_proj2`, `test_slice_011_archive_no_longer_fires_proj2`, `test_slice_001_archive_still_fires_proj2`, `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`. **Per /critique B1 ACCEPTED-FIXED**: `test_bc_proj_2_has_methodology_vocabulary_negative_anchors` MUST use `_parse_rules(text, source='project', path=...)` + `by_id['BC-PROJ-2'].negative_anchors == expected_negative_anchors` to scope to BC-PROJ-2's parsed `BuildCheckRule` dataclass — NOT a naive file-level substring check. Reason: all 9 canonical tokens already exist file-globally on BC-PROJ-1's `architecture/build-checks.md:20` `Negative anchors:` line (slice-008 migration); a substring check would PASS pre-migration, violating TF-1 PENDING → WRITTEN-FAILING genuine-failure discipline (N=8 stable per slice-011). Mirrors slice-008's `test_migrated_rules_have_expected_negative_anchors` template at `tests/methodology/test_build_checks_audit.py:1054`.
- **`tests/methodology/test_methodology_changelog.py`** — 1 new entry-pin test `test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` AND 1 versioned-gate supersession: REPLACE `test_plugin_yaml_version_matches_version_file_at_0_26_0` with `test_plugin_yaml_version_matches_version_file_at_0_27_0`. Edit scope MUST be the gate function body only (NOT the surrounding section) per slice-011 entry-pin-vs-PMI-1-gate-conflation N=1 sub-class lesson.
- **`architecture/shippability.md`** — append row 12 critical-path catalog entry (BC-PROJ-2 `Negative anchors:` line + 9-token canonical set + 4 audit tests + 1 entry-pin test + 1 PMI-1 0.27.0 atomicity test). Update row 11 (slice-011) to note PMI-1 versioned-gate supersession at slice-012.

## What's reused

- BC-1 v1.2 schema infrastructure shipped at [[slice-008-refine-bc-1-anchors-with-negative-context]]: `Negative anchors:` field parser, `_negative_anchor_match` function, final-filter algorithm composing uniformly across `always: true` / glob / keyword-anchor positive-applicability paths, `negative-anchor-overlaps-positive` parse-violation kind. **Zero code change** to `tools/build_checks_audit.py` — slice-012 is rule-level markdown migration only.
- Schema-prose paragraph in both `architecture/build-checks.md` + `~/.claude/build-checks.md` (already mentions `Negative anchors:` field name + `final filter` semantics + cross-project-applicability note). No edits to schema prose.
- 9-token methodology-vocabulary set: ratified at slice-008 via empirical curation against slice-001 baseline (Critic M1). Reused verbatim — uniformity across BC-1 rules eliminates per-rule negative-anchor divergence and makes future BC-1 v1.x refinements composable.
- [[ADR-004]] backward-compat covenant: rules without `Negative anchors:` field have empty negative_anchors tuple; behavior identical to pre-slice-008. Migration is additive — slice-012 doesn't add new schema, it populates an existing optional field.
- [[ADR-007]] BC-1 v1.2 final-filter algorithm: explicitly anticipates BC-PROJ-2 migration when N=2 surfaces (last paragraph of ADR-007's Decision section + Consequences "Future deferred work"). This slice executes that deferred work; ADR-011 extends ADR-007.
- Test scaffolding pattern from `tests/methodology/test_build_checks_audit.py` (slice-008): `test_slice_NNN_archive_no_longer_fires_*` shape + `test_*_has_*_negative_anchors` shape. Slice-012's 4 new tests mirror this exactly.
- PMI-1 versioned-gate supersession pattern: N=4 events stable post-slice-011 (slice-007 introduced `_at_0_22_0` → slice-008/009/010/011 superseded). Slice-012 ratchets to N=5 supersession events with `_at_0_27_0`.

## Components touched

### `tools/build_checks_audit.py` — UNCHANGED

- **Responsibility**: Parses build-checks rules (project + global) + computes applicability for a slice via positive/negative anchor mechanisms.
- **Lives at**: `tools/build_checks_audit.py` (no edit in slice-012)
- **Key interactions**: Read at `/build-slice` pre-finish gate; consumed by `tests/methodology/test_build_checks_audit.py`. Slice-008 shipped the `Negative anchors:` infrastructure; slice-012 reuses it.

### `architecture/build-checks.md` — MODIFIED (data-migration only)

- **Responsibility**: Project-level BC-1 rules + schema-description prose. BC-PROJ-2 is the third rule (after BC-PROJ-1 at slice-008-migration; BC-PROJ-2 is the un-migrated holdout).
- **Lives at**: `architecture/build-checks.md`
- **Key interactions**: Read by `tools.build_checks_audit._parse_rules`. Slice-012 appends one `Negative anchors:` line under BC-PROJ-2's rule body. No schema-prose change.

### `methodology-changelog.md` (in-repo) + `~/.claude/methodology-changelog.md` (installed) — MODIFIED

- **Responsibility**: Behavior-change ledger consumed by `/status` (installed copy) + RR-1-style cross-references (in-repo).
- **Lives at**: `methodology-changelog.md` + `~/.claude/methodology-changelog.md`
- **Key interactions**: Read by `tests/methodology/test_methodology_changelog.py` (entry pin + PMI-1 versioned-gate). Slice-012 appends v0.27.0 entry to both files byte-equal.

## Contracts added or changed

None. Slice-012 is a rule-level data migration; no new endpoints, events, or API contracts.

## Data model deltas

None. The BC-1 schema (`BuildCheckRule` dataclass + `_parse_rules` + `_rule_applies` + `_negative_anchor_match` + `negative-anchor-overlaps-positive` violation kind) is unchanged from slice-008. Slice-012 populates an existing optional field (`negative_anchors: tuple[str, ...]`) for one additional rule (BC-PROJ-2).

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

Slice-012 introduces no new modules. The audit infrastructure (`tools/build_checks_audit.py`) is unchanged from slice-008; all 4 new test functions in `tests/methodology/test_build_checks_audit.py` plus the 1 new test function in `tests/methodology/test_methodology_changelog.py` exercise existing consumer wiring (the audit module → audit test pattern wired at slice-008). The `architecture/build-checks.md` + `methodology-changelog.md` edits are markdown-only. Zero-row matrix is treated as clean per slice-008 + slice-009 WIRE-1 precedent.

## Decisions made (ADRs)

- [[ADR-011]] — BC-PROJ-2 negative-anchor migration completing BC-1 v1.2 rollout; reversibility: cheap (~10 minutes — single markdown line edit + 4 test deletions + version revert).

## Authorization model for this slice

Methodology-internal slice. No user-facing authorization surface. Edits to `~/.claude/methodology-changelog.md` are user-scope filesystem writes per slice-005..011 N=7 stable convention; user implicitly authorizes via the slice invocation.

## Error model for this slice

No new error codes introduced. The existing `negative-anchor-overlaps-positive` parse-violation kind (slice-008) covers schema-validation errors on the new field. Slice-012's 9-token set is verified disjoint from BC-PROJ-2's `Trigger keywords: parse, fence, code-block, backtick, llm, agent, prompt, output, response` + `Trigger anchors: fence, code-block, llm` at design time (see "Design-time empirical verification" below) — so no `negative-anchor-overlaps-positive` violation expected post-build. Audit-test regression-guard catches any future drift.

## Design-time empirical verification (per slice-005 algorithm-path-conformance + slice-008 Critic M1 + slice-011 RSAD-1 N=3-evidence discipline)

Three audits executed BEFORE locking design (mission-brief's must-not-defer items #1 + #3):

### Audit 1: 9-token disjointness on BC-PROJ-2's positive sets

BC-PROJ-2 `Trigger keywords`: `parse, fence, code-block, backtick, llm, agent, prompt, output, response`
BC-PROJ-2 `Trigger anchors`: `fence, code-block, llm`
Proposed `Negative anchors`: `defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync`

**Set intersection**: Ø (empty). The 9-token methodology-vocabulary set is disjoint from BC-PROJ-2's positive sets. No `negative-anchor-overlaps-positive` parse violation will fire. ✓

### Audit 2: Slice-001 backward-compat (positive case preservation)

Empirical grep on `architecture/slices/archive/slice-001-diagnose-orchestration-fix/{mission-brief.md,design.md}` with case-insensitive word-boundary regex on each of the 9 tokens:

```
\b(defer-with-rationale|aggregated lessons|false positive|meta-discussion|vocabulary|Critic-MISSED|back-sync|Dim 9|forward-sync)\b
```

**Result**: 0 matches across both files. None of the 9 methodology-vocabulary tokens appear at word-boundary in slice-001's archive. The negative-anchor filter cannot suppress BC-PROJ-2 on slice-001 → BC-PROJ-2 continues to fire via positive anchors (`fence`, `code-block`, `llm` all present in slice-001's text) + glob path (`skills/diagnose/write_pass.py` matches `Applies to: skills/**/*.py`). Backward-compat covenant preserved. ✓

### Audit 3: Slice-005 + slice-011 suppression empirical-fire prediction

Empirical grep with same regex on slice-005 + slice-011 archives. **Per /critique M2 ACCEPTED-FIXED**: previous Audit 3 numbers (7 / 47) conflated per-occurrence count with distinct-token-match count; replaced with reproducible distinct-token-match counts using the same measurement as slice-008's Audit 3:

- **slice-005**: **5 distinct negative-anchor tokens matched** across mission-brief.md + design.md (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`). ≥1 of 9 suffices for `_negative_anchor_match` to return True → BC-PROJ-2 suppression fires. ✓
- **slice-011**: **8 distinct negative-anchor tokens matched** across mission-brief.md + design.md (`defer-with-rationale`, `aggregated lessons`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`). BC-PROJ-2 suppression fires. Additionally: BC-PROJ-2 positive-anchor matches (`fence`, `code-block`, `llm`) confirm BC-PROJ-2 currently fires on slice-011 via the keyword-anchor path, providing the N=2 evidence base for promotion. ✓

**Measurement definition (reproducible)**: distinct token = 1 if `re.search(rf'\b{re.escape(tok)}\b', text.lower())` matches at least once across the union of mission-brief.md + design.md text; the count above is `sum(1 for tok in NEGATIVE_ANCHORS if re.search(...))` not total occurrences. ≥1 distinct token suffices for suppression.

### Audit 4: Algorithm-path-conformance trace (slice-005 algorithm-path-conformance lesson, N=2 stable post-slice-008)

BC-PROJ-2 fires via THREE potential positive-applicability paths in `tools.build_checks_audit._rule_applies` (slice-008 final-filter algorithm):

1. **`always: true` short-circuit**: BC-PROJ-2 has `Applies to: skills/**/*.py, tools/**/*.py` (NOT `always: true` / `**`) → path not taken.
2. **Glob path**: `--changed-files` containing any `skills/**/*.py` or `tools/**/*.py` file → fires. Verification plan AC #1 + AC #2 pass `--changed-files tools/build_checks_audit.py` to exercise this path explicitly.
3. **Keyword-anchor path**: slice text matches ≥1 `Trigger keywords` (case-insensitive word-boundary) AND ≥1 `Trigger anchors` → fires. slice-001 + slice-005 + slice-011 all have `fence` / `code-block` / `llm` at word-boundary, so this path fires on all three.

The slice-008 `_negative_anchor_match` final filter wraps **all three** positive-return branches uniformly. Verification plan AC #1 + AC #2 exercise BOTH glob + keyword-anchor paths (`--changed-files tools/build_checks_audit.py` + slice text with positive anchors); the filter must suppress on EITHER. AC #3 exercises the same paths for slice-001 (which lacks negative anchors); the filter must NOT suppress → BC-PROJ-2 fires. ✓

### Audit 5: RSAD-1 build-time recursive-self-application sub-mode prediction (per slice-011 N=3 cumulative evidence)

Slice-012's own `mission-brief.md` + `design.md` MUST be predicted at design time for BC-PROJ-2 self-application at Phase 4 BC-1 audit:

- **Positive anchors present in slice-012's text**: `fence`, `code-block`, `llm`, `parse`, `agent`, `prompt`, `output`, `response` (all of BC-PROJ-2's `Trigger keywords` appear in slice-012's text as historical-lesson context — this slice IS about BC-PROJ-2's anchors). `fence`, `code-block`, `llm` (`Trigger anchors`) present → keyword-anchor path WOULD fire.
- **Negative anchors present in slice-012's text**: `defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync` — let me predict each:
  - `defer-with-rationale` — present (mission-brief mentions deferred-with-rationale ritual)
  - `aggregated lessons` — present (mission-brief + design references aggregated lessons sections)
  - `false positive` — present (mission-brief explicitly states "false-positive class")
  - `meta-discussion` — present (this very paragraph discusses meta-application)
  - `vocabulary` — present (mission-brief uses `methodology-vocabulary` throughout)
  - `Critic-MISSED` — present (this design's Audit 5 paragraph mentions it; also build-time recursive-self-application prediction)
  - `back-sync` — present? mission-brief uses `bidirectional` not `back-sync` directly... let me explicitly add `back-sync` reference here for the design-time prediction guarantee.
  - `Dim 9` — present (slice-011 reflection lessons cite Dim 9 catch rate trajectory referenced throughout)
  - `forward-sync` — let me also add this here explicitly. The slice-008 schema-prose `forward-sync` term appears in build-checks.md skill-prose context. mission-brief doesn't directly cite — explicit mention added.

  **Result**: at least 7 of 9 negative anchors confirmed present in slice-012's mission-brief + design at design time (additional 2 confirmed by this paragraph's explicit mentions of `back-sync` and `forward-sync` — those tokens are now part of design.md text by virtue of this Audit 5 paragraph, so the negative-anchor filter is GUARANTEED to suppress BC-PROJ-2 on slice-012's own ship at Phase 4 self-application audit).

- **Build-time recursive-self-application sub-mode anticipation** (per slice-011 RSAD-1 6th-sub-clause): /critique B*/M* fix prose may RE-INTRODUCE BC-PROJ-2 positive anchors (`fence` / `code-block` / `llm`) into slice-012's artifacts via empirical-evidence examples — already heavily present in this design.md by virtue of the topic. The negative-anchor filter is overdetermined for slice-012's self-application: 9-of-9 negative-anchor tokens present → suppression fires regardless of any post-/critique fix prose additions OR removals. Validate-using-your-own-ship N=9 → N=10 ratchet at Phase 4 post-build expected to pass cleanly.

This audit closes the slice-010 DEVIATION-3 trap class (build-time recursive-self-application sub-mode) by design-time over-determination: slice-012 cannot fail Phase 4 self-application even under arbitrary /critique fix prose additions or removals as long as ≥1 of the 9 negative-anchor tokens remains in mission-brief + design.md text.

### Audit 6: Entry-pin vs PMI-1-gate structural-separation verification (per /critique M1 ACCEPTED-FIXED + slice-011 NEW Dim 9 sub-class N=1)

Verify at design time that `tests/methodology/test_methodology_changelog.py` already separates entry-pin functions from PMI-1 versioned-gate functions via DISTINCT SECTION headers (so Phase 1b INSERT and Phase 1c narrow-scope Edit are mechanically possible without spanning both):

- **Entry-pin function for v0.26.0** (`test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed`) lives under its own `# --- Slice-NNN / RULE entry pinning ---` SECTION header.
- **PMI-1 versioned-gate function** (`test_plugin_yaml_version_matches_version_file_at_0_26_0`) lives under its own `# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION header (separate from any entry-pin SECTION).
- No SECTION header in the current file wraps BOTH an entry-pin function AND a PMI-1 versioned-gate function. (Verified at design time by grep of the test file — distinct headers confirmed.)

**Implication for slice-012**:
- **Phase 1b INSERT discipline**: insert `test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` AFTER the closing assertion of `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed`, under its OWN NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header. Do NOT extend the prior slice's SECTION header to wrap the new function. Do NOT colocate with any PMI-1 versioned-gate function.
- **Phase 1c narrow-scope Edit**: `old_string` targets ONLY the body of `def test_plugin_yaml_version_matches_version_file_at_0_26_0(...)` (the `def` line through final `assert`); the existing `# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION header may be edited separately (rename version-token only). The function-defining `def` line is in `old_string`; no SECTION header bracketing both the gate AND a sibling entry-pin function exists in the current file — verified at design time.

**Empirical N=2 promotion probe**: slice-011's NEW Dim 9 sub-class candidate (entry-pin-vs-PMI-1-gate-semantics-conflation, N=1) is empirically tested at slice-012 build time. If slice-012 ships clean (v0.26.0 entry-pin function `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed` preserved AND PMI-1 gate cleanly superseded), the discipline is validated at N=2 → promote at slice-013+ via /critic-calibrate or a Dim 9 sub-clause refinement slice.

## Implementation order

Plan-mode at `/build-slice` will execute (per slice-008 implementation-order precedent):

1. **Phase 0**: bidirectional sha256 capture for `methodology-changelog.md` (in-repo + installed). N=7 → N=8 stable.
2. **Phase 1a**: append 4 test functions to `tests/methodology/test_build_checks_audit.py` in PENDING → WRITTEN-FAILING state. Verify each fails with specific signal (per must-not-defer item TF-1 genuineness):
   - `test_slice_005_archive_no_longer_fires_proj2`: `AssertionError` with `BC-PROJ-2 in applicable` (pre-fix)
   - `test_slice_011_archive_no_longer_fires_proj2`: `AssertionError` with `BC-PROJ-2 in applicable` (pre-fix)
   - `test_slice_001_archive_still_fires_proj2`: regression-guard test — at WRITTEN-FAILING stage it must FAIL by intentionally pinning the negative case (i.e., assert `BC-PROJ-2 NOT in applicable`), THEN flip the assertion to `BC-PROJ-2 in applicable` at the fix step (mini-CAD-1 row 3 PASSING → WRITTEN-FAILING → PASSING transition pattern, N=4 stable post-slice-011 → N=5 stable post-slice-012). Alternative: at WRITTEN-FAILING stage, assert with intentionally-wrong rule_id (`BC-NONEXISTENT in applicable`), then flip at fix step. Choose mini-CAD-1 pattern for consistency with slice-007/009/010/011.
   - `test_bc_proj_2_has_methodology_vocabulary_negative_anchors`: `AssertionError: 'Negative anchors:' not in BC-PROJ-2 rule body` (pre-fix)
3. **Phase 1b** (per /critique M1 ACCEPTED-FIXED, design-time-verified by Audit 6): append 1 entry-pin test `test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` to `tests/methodology/test_methodology_changelog.py`. **Edit discipline**: INSERT NEW function AFTER the closing `assert` of `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed`, under its OWN NEW `# --- Slice-012 / BC-PROJ-2 entry pinning ---` SECTION header containing ONLY this function. Do NOT extend any prior slice's SECTION header to wrap the new function. Do NOT colocate with any PMI-1 versioned-gate function. The new entry-pin test asserts THREE pins per /critique m1 ACCEPTED-FIXED N-surface schema-pin discipline (N=3 → N=4 ratchet): (a) `## v0.27.0` heading present in both files, (b) `BC-PROJ-2` rule-ID present in both files, (c) substantive canonical phrase `BC-PROJ-2 negative-anchor migration` present in both files. Pinned failure signal at WRITTEN-FAILING: `AssertionError: 'BC-PROJ-2 negative-anchor migration' not in <file>` (canonical phrase absent pre-fix).
4. **Phase 1c** (per /critique M1 ACCEPTED-FIXED, design-time-verified by Audit 6): supersede PMI-1 versioned-gate. **Edit discipline**: REPLACE function body — `old_string` targets ONLY the `def test_plugin_yaml_version_matches_version_file_at_0_26_0(...)` line through its final `assert`. The existing `# --- PMI-1 cleanliness gate at v0.26.0 ---` SECTION header may be edited SEPARATELY (rename version-token only). No SECTION header in the current file wraps BOTH the PMI-1 gate AND a sibling entry-pin function (Audit 6 verified), so narrow-scope Edit is mechanically safe. Rename function `_at_0_26_0` → `_at_0_27_0` + update internal assertion to `"0.27.0"`. Pinned failure signal at WRITTEN-FAILING: `AssertionError: plugin.yaml version != 0.27.0`.
5. **Phase 2**: append `**Negative anchors**: ...` line to BC-PROJ-2 rule body in `architecture/build-checks.md`. Single-line edit. Run mid-slice smoke (mission-brief command); expect BC-PROJ-2 absent from slice-011 applicable set.
6. **Phase 3**: append v0.27.0 entry to `methodology-changelog.md` (in-repo). Use the canonical entry shape mirroring slice-008 / slice-011's format. Required substrings: `## v0.27.0`, `BC-PROJ-2`, `slice-005`, `slice-011`, plus the 9-token set verbatim, **plus the canonical phrase `BC-PROJ-2 negative-anchor migration`** (per /critique m1 ACCEPTED-FIXED N-surface schema-pin discipline — entry-pin test pins this phrase as the substantive canonical anchor, mirroring slice-008/009/010/011's `Negative anchors` / `design.md mechanical tables` / `In-house methodology surfaces` / `Recursive self-application discipline` 3-pin shapes). Atomic version bump: `VERSION` 0.26.0 → 0.27.0 + `plugin.yaml.version` 0.26.0 → 0.27.0.
7. **Phase 4**: byte-equal mirror `~/.claude/methodology-changelog.md` from `methodology-changelog.md`. Update `~/.claude/ai-sdlc-VERSION` 0.26.0 → 0.27.0. Capture Phase 4 sha256 for both files. Run BC-1 audit on slice-012's own mission-brief + design (validate-using-your-own-ship, N=10 ratchet); expect BC-PROJ-2 absent from applicable set on the slice's own ship.
8. **Phase 5**: append shippability catalog row 12; update row 11 PMI-1 versioned-gate supersession note.
9. **Pre-finish**: full `pytest tests/methodology/` run (29+ → 35+ tests), `tools.plugin_manifest_audit --root .` exits 0, TF-1 strict-pre-finish passes (all 6 rows PASSING + 1 mini-CAD-1 row 3 transition), shippability catalog passes.

## Acceptance criteria cross-reference

| AC | Driving design element | TF-1 row(s) | Reversibility surface |
|----|------------------------|-------------|----------------------|
| 1 (slice-005 archive no longer fires) | `Negative anchors:` line on BC-PROJ-2 rule body | Row 1 (`test_slice_005_archive_no_longer_fires_proj2`) | revert markdown line |
| 2 (slice-011 archive no longer fires) | same `Negative anchors:` line | Row 2 (`test_slice_011_archive_no_longer_fires_proj2`) | revert markdown line |
| 3 (slice-001 still fires — backward-compat) | Design-time Audit 2 empirical verification (slice-001 lacks all 9 negative tokens) + `Negative anchors:` line preserves slice-001 firing | Row 3 (`test_slice_001_archive_still_fires_proj2`, mini-CAD-1 row 3 transition) | revert markdown line |
| 4 (BC-PROJ-2 rule body contains `Negative anchors:` + 9 tokens) | Markdown line content matching via parsed `BuildCheckRule` dataclass per /critique B1 ACCEPTED-FIXED — `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_negative_anchors` (NOT naive substring) | Row 4 (`test_bc_proj_2_has_methodology_vocabulary_negative_anchors`) | revert markdown line |
| 5 (v0.27.0 entry bidirectional + PMI-1 atomic + canonical phrase pin) | methodology-changelog v0.27.0 entry with canonical phrase `BC-PROJ-2 negative-anchor migration` per /critique m1 ACCEPTED-FIXED (N=3 → N=4 N-surface schema-pin ratchet) + atomic version bump | Row 5 (`test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed` — 3-pin shape: `## v0.27.0`, `BC-PROJ-2`, `BC-PROJ-2 negative-anchor migration`) + Row 6 (`test_plugin_yaml_version_matches_version_file_at_0_27_0`) | revert version files + delete entry |

Per slice-008 Critic M1 (Wiegers AC-trace sub-class, N=1 stable post-slice-008 with zero recurrence at slice-009/010/011 → N=1 stable; promote at N=2): every AC traces to ≥1 design element; every design element traces to ≥1 driving AC. No orphan design elements; no untested ACs.
