# Design: Slice 008 refine-bc-1-anchors-with-negative-context

**Date**: 2026-05-10
**Mode**: Standard (per slice-007 archive — most recent active mode)
**Risk tier**: low; **critic-required**: true (voluntary, per slice-007 lesson on cross-cutting tooling slices)

## What's new

- **BC-1 v1.2 — `Negative anchors:` per-rule schema field** (additive). When specified, the field's tokens (case-insensitive, word-boundary regex against `mission-brief.md` + `design.md`) act as a **final filter**: an otherwise-applicable rule is suppressed when ≥1 negative anchor matches the slice's text. Applies to all three positive-applicability paths (`always: true` short-circuit, `--changed-files` glob match, keyword/anchor match) — i.e., post-applicability filter, not path-specific.
- **New parse-violation kind `negative-anchor-overlaps-positive`** — when a rule's negative anchors overlap with its `Trigger keywords` OR `Trigger anchors`, the audit emits a violation (Important). Mirrors slice-005's `anchor-not-in-keywords`. Closes input-validation must-not-defer loop.
- **`tools/build_checks_audit.py`**:
  - Add `negative_anchors: tuple[str, ...]` field to `BuildCheckRule` dataclass + `to_dict`.
  - Parse `**Negative anchors**:` field in `_parse_rules` (case-insensitive normalization on tokens).
  - Validate non-overlap with positive trigger_keywords/trigger_anchors -> `negative-anchor-overlaps-positive` violation kind.
  - Refactor `_rule_applies`: extract a `_negative_anchor_match(rule, slice_text)` helper that returns True iff ≥1 negative anchor matches; gate the final return of every positive-applicability path through `not _negative_anchor_match(...)`.
  - Update module docstring to describe the v1.2 semantic.
- **`architecture/build-checks.md`**:
  - Schema-description prelude updated: TWO sentences — (1) `Negative anchors:` field semantics; (2) explicit `final filter` algorithm-semantics phrase (per Critic M2 — TWO-surface schema-pin discipline requires distinguishable substrings for field-name AND semantics surfaces).
  - BC-PROJ-1 only gets `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` appended (per Critic M1 — BC-PROJ-2 has N=1 false-positive recurrence, below BC-1 promotion threshold of N=3; defer migration to a future slice at N=2).
- **`~/.claude/build-checks.md`**: same TWO-sentence schema-prelude addition; same negative-anchor list applied to BC-GLOBAL-1. ADDITIONAL one-sentence note (per Critic m1) that the negative-anchor curation in this global file is AI-SDLC-methodology-vocabulary-specific and may need re-curation by adopters in non-methodology domains.
- **`tests/methodology/test_build_checks_audit.py`**: add 5 new tests (one per AC) + 1 parse-violation test for `negative-anchor-overlaps-positive` (must-not-defer; not a numbered AC) + 1 anchor-tuple migration test (per slice-005 Critic M1 pattern; must-not-defer).
- **`methodology-changelog.md`** (in-repo + `~/.claude/`): new H2 entry `## v0.23.0 — 2026-05-10` documenting BC-1 v1.2 and ADR-007.
- **`VERSION` (in-repo) + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version`**: 0.22.0 -> 0.23.0 (atomic per slice-007 PMI-1 closure pattern).
- New ADR: [[ADR-007-bc-1-negative-context-anchors-via-final-filter]] — reversibility: **cheap**.

## What's reused

- BC-1 v0.10.0 ground (`tools/build_checks_audit.py` parse + applicability resolver) — slice-008 extends, doesn't replace.
- BC-1 v1.1 (slice-005 / [[ADR-004]]) — word-boundary regex + optional `Trigger anchors:` per-rule field. Slice-008's `Negative anchors:` is the **suppressive variant** of slice-005's inclusionary `Trigger anchors:`. Same parsing pattern (comma-split + lower + dedupe), same word-boundary semantic. The two fields are independent (negative anchors are NOT a subset of trigger keywords; they're an exclusionary vocabulary).
- The 22+ existing `tests/methodology/test_build_checks_audit.py` tests act as the regression-guard for backward-compat (per ADR-004 covenant: "rules without the new field continue to behave with current applicability semantics"). Slice-005's tests on slice-003/004 archives still pass post-slice-008 (those slices either have negative-anchor hits — desirable noise extension — or no hits, leaving applicability decisions unchanged).
- PMI-1 + INST-1 invariant patterns (slice-006/007 lesson) — version bumps + canonical-tools count remain consistent.
- TWO-surface schema-pin discipline (slice-005 Critic M3) generalized to N-surface (slice-007 lesson). Slice-008 has ONE new surface (the `Negative anchors:` field name); ONE TF-1 row is sufficient under AC #5.
- "Validate using your own ship" pattern (N=5 stable across slice-003..007). Slice-008 self-applies the negative-anchor mechanism: the slice's own mission-brief + design contain methodology-vocabulary anchors (`vocabulary`, `Dim 9`, `back-sync`, `forward-sync`); post-slice-008, the slice's own /build-slice BC-1 audit will silence BC-PROJ-1 + BC-GLOBAL-1 false-positively without manual defer-with-rationale (closes the noise loop on its own ship).

## Components touched

### `tools/build_checks_audit.py` (modified)

- **Responsibility**: parse build-checks files + resolve applicability per slice; emit human/JSON output. Slice-008 extends with negative-anchor final-filter semantics.
- **Lives at**: `tools/build_checks_audit.py`
- **Key interactions**: called by `/build-slice` SKILL.md Step 6 (pre-finish gate); called by `/reflect` SKILL.md Step 5b (promotion); imported by `tests/methodology/test_build_checks_audit.py` for unit tests.
- **What changes**:
  - `BuildCheckRule.negative_anchors: tuple[str, ...]` (new field; defaults to empty tuple via dataclass).
  - `_parse_rules()`: read `**Negative anchors**:` field (same comma-split + lower + dedupe as `Trigger anchors:`); validate non-overlap; emit `negative-anchor-overlaps-positive` violations.
  - `_rule_applies()`: introduce `_negative_anchor_match(rule, slice_text) -> bool` helper; gate every positive return through `not _negative_anchor_match(...)`.
  - `to_dict()`: include `negative_anchors: list`.
  - Module docstring: append paragraph on v1.2 negative-context semantics.

### `architecture/build-checks.md` (modified)

- **Responsibility**: project-level build-checks rules + schema description prose.
- **Lives at**: `architecture/build-checks.md`
- **Key interactions**: read by `tools.build_checks_audit.audit_slice()`; pinned by `tests/methodology/test_build_checks_audit.py`.
- **What changes**:
  - Schema-prelude (top-of-file): TWO sentences — (1) describing `Negative anchors:` field; (2) describing the universal `final filter` algorithm-semantics. Two distinguishable substrings get pinned per Critic M2.
  - BC-PROJ-1 only: append `**Negative anchors**: defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync` to its field block. **BC-PROJ-2 is NOT migrated** (per Critic M1; N=1 below BC-1 promotion threshold).

### `~/.claude/build-checks.md` (modified — out-of-repo)

- **Responsibility**: global-level build-checks rules + schema description prose; same shape as project-level.
- **Lives at**: `~/.claude/build-checks.md` (out-of-repo per slice-005..007 pattern).
- **Key interactions**: read by `tools.build_checks_audit.audit_slice()`; pinned by the same TWO-surface tests.
- **What changes**:
  - Schema-prelude addition: TWO sentences (same as project file) + ONE additional sentence (per Critic m1) noting "the negative-anchor curation below is calibrated for AI-SDLC-methodology-vocabulary slices; adopting projects in other domains may need to re-curate per their own discriminating tokens."
  - BC-GLOBAL-1: append `**Negative anchors**:` field with the same 9-token list.

### `tests/methodology/test_build_checks_audit.py` (modified)

- **Responsibility**: BC-1 regression suite; pin schema prose; cover applicability-resolution edge cases.
- **Lives at**: `tests/methodology/test_build_checks_audit.py`
- **Key interactions**: imports `tools.build_checks_audit`; reads from `architecture/build-checks.md` + `~/.claude/build-checks.md` (the latter via `_GLOBAL_BUILD_CHECKS = Path.home() / ".claude" / "build-checks.md"`); fixtures at `tests/methodology/fixtures/build_checks/`.
- **What changes**: add 5 new test functions (mapped to ACs 1-5) + 1 parse-violation test (`test_negative_anchor_overlaps_positive_yields_violation`) + 1 migration-tuple test (`test_migrated_rules_have_expected_negative_anchors`).

### `methodology-changelog.md` (in-repo + `~/.claude/`) — append-only entry

- **What changes**: new H2 `## v0.23.0 — 2026-05-10` entry following the v0.22.0 pattern; describes BC-1 v1.2 + cites slice-008 + ADR-007.

### `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml` (atomic version bumps)

- **What changes**: 0.22.0 -> 0.23.0 in all three locations (PMI-1 invariant; slice-007 escape-closure pattern).

## Algorithm-path conformance (per slice-005 lesson)

Per the slice-005 lesson "empirical verification at design-time should exercise algorithm paths, not just isolated metric counts," the table below traces every positive-applicability path's pre/post slice-008 behavior. The `_rule_applies` body has three branches that can return True; each must compose correctly with the new negative-anchor final filter.

| Path | Pre-slice-008 (current) | Post-slice-008 (with `negative_anchors`) |
|------|--------------------------|--------------------------------------------|
| `applies_to == ("always",)` short-circuit | Returns `True` immediately | Returns `not _negative_anchor_match(rule, slice_text)` — i.e., `True` unless ≥1 negative anchor matches. |
| Glob match in `--changed-files` | Returns `True` on first match | Returns `not _negative_anchor_match(rule, slice_text)` on first match. |
| Keyword path (with `Trigger anchors`) | Returns `any(a in matched for a in trigger_anchors)` | Same logic, but final return is wrapped with `and not _negative_anchor_match(...)`. |
| Keyword path (without `Trigger anchors`) | Returns `True` if any keyword matched | Same, wrapped with `and not _negative_anchor_match(...)`. |
| Nothing matches | Returns `False` | Returns `False` (negative anchors irrelevant when no positive match) — backward-compat preserved. |
| Rule with empty `negative_anchors` (e.g., un-migrated rules) | N/A | `_negative_anchor_match` returns False on empty `negative_anchors`; rule fires identically to pre-slice-008. Backward-compat preserved per ADR-004 covenant. |

The negative-anchor filter is EXPRESSED as a final check on positive-applicability decisions, so it composes with `always: true` / glob / keyword paths uniformly. No path-specific exception logic needed. This is the simpler design vs. having separate negative-anchor checks at each path's exit point.

## Empirical verification at design-time (per slice-005 N=6 discipline)

Pre-slice-008 BC-1 audit results across all 7 archived slices, two run modes (keyword-path-only WITHOUT --changed-files; multi-path WITH representative --changed-files matching the slice's actual git-diff patterns):

| Slice | --changed-files (representative) | BC-PROJ-1 | BC-PROJ-2 | BC-GLOBAL-1 | Negative-anchor hits | Post-slice-008 (predicted) |
|-------|-----------------------------------|-----------|-----------|-------------|----------------------|-----------------------------|
| 001 (legitimate fence-parsing) | `skills/diagnose/SKILL.md, skills/diagnose/write_pass.py, skills/diagnose/passes/01-intent.md` | applicable | applicable | applicable | **0** | applicable / applicable / applicable (preserved ✓ AC #4) |
| 002 (diagnose contract fix) | (typical /diagnose changes) | skipped | skipped | applicable (`**` glob) | 0 | unchanged (BC-GLOBAL-1 still fires; out-of-scope) |
| 003 (VAL-1 audit) | `tools/install_audit.py, pyproject.toml` | skipped | skipped | applicable (`**` glob) | 2 (`defer-with-rationale, aggregated lessons`) | BC-GLOBAL-1 silenced (desirable noise extension; doesn't break slice-005 tests since BC-PROJ-2 still skipped via anchor filter) |
| 004 (RR-1 audit) | `tools/risk_register_audit.py, ...` | skipped | skipped | applicable (`**`) | 0 | unchanged (out-of-scope) |
| 005 (BC-1 anchors v1.1) | `tools/build_checks_audit.py, architecture/build-checks.md` | **applicable** (kw `subagent`) | **applicable** (kw `llm, code-block`) | **applicable** (`**` + kw) | **5+** (`defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary`) | BC-PROJ-1 + BC-GLOBAL-1 silenced ✓ AC #1; BC-PROJ-2 STILL FIRES (not migrated per Critic M1; N=1 below promotion threshold). Acceptable per AC #1's explicit gating only on BC-PROJ-1 + BC-GLOBAL-1. |
| 006 (CCC-1 9th dimension) | `agents/critique.md` | **applicable** (`agents/**/*.md` glob) | skipped | **applicable** (`**`) | **4+** (`vocabulary, back-sync, Dim 9, Critic-MISSED`) | Both silenced ✓ AC #2 |
| 007 (CAD-1 audit) | `agents/critique.md, skills/critic-calibrate/SKILL.md` | **applicable** (`agents/**/*.md` glob) | skipped (no `tools/**/*.py` subfolder match per glob limitation) | **applicable** (`**`) | **3+** (`back-sync, forward-sync, Dim 9, Critic-MISSED`) | Both silenced ✓ AC #3 |

Cross-pattern check: each false-positive recurrence (slice-005, 006, 007) has ≥3 distinct negative anchors hitting; slice-001 has zero. The discriminating signal is robust — even if one anchor proves brittle (e.g., a future slice unexpectedly uses `Dim 9` in a non-meta context), the union semantic means another anchor in the set still suppresses the false positive.

## Negative-anchor curation rationale

The negative-anchor set `{defer-with-rationale, aggregated lessons, false positive, meta-discussion, vocabulary, Critic-MISSED, back-sync, Dim 9, forward-sync}` was empirically derived (not pre-curated) by:

1. Tokenizing slice-005, slice-006, slice-007 mission-brief + design text (lowered).
2. Removing tokens present in slice-001's mission-brief + design (the canonical legitimate fence-parsing slice).
3. Filtering for semantic specificity to "discussing methodology mechanics" (not generic English like `methodology`, `audit`, `Critic` which a fence-parsing slice could legitimately use).
4. Verifying union-coverage — at least one anchor matches each of slice-005..007.
5. Verifying non-overlap with positive trigger_keywords + trigger_anchors of BC-PROJ-1 + BC-GLOBAL-1 (BC-PROJ-2 not migrated per Critic M1).

Same set used for both migrated rules (BC-PROJ-1, BC-GLOBAL-1) — the domain inversion ("topic is methodology-vocabulary, not implementation") is rule-agnostic. Per-rule customization is supported by the schema (each rule's `Negative anchors:` field is independent) but not exercised in this slice. Future BC-N rules in different domains can curate their own.

The set is **conservative** — it does NOT include high-frequency-but-generic words like `methodology`, `Critic`, `audit`, `lessons-learned`, `recurrence`, `lesson` (each of which would over-suppress). It DOES include some specific multi-word phrases (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`) that are unlikely to appear in legitimate fence-parsing or subagent-fan-out implementation contexts.

**Cross-project applicability** (per Critic m1): the AI-SDLC-methodology-internal tokens (`Critic-MISSED`, `Dim 9`, `back-sync`, `forward-sync`, `meta-discussion`) are vocabulary specific to this project's `reflection.md` schema and the CCC-1 9th-dimension pattern (slice-006). Adopting projects (e.g., a frontend app using the AI-SDLC pipeline scaffolding without a Critic agent) may need to re-curate the global-file negative-anchor set for their own meta-vocabulary. The N=0 cross-project misuse evidence is reassuring but not load-bearing — the schema-prelude in `~/.claude/build-checks.md` documents this so adopters can re-curate without surprise.

## Contracts added or changed

### BC-1 schema (build-checks.md prose)

- **Defined in**: `architecture/build-checks.md` (project-level prose) + `~/.claude/build-checks.md` (global-level prose); enforced parsing in `tools/build_checks_audit.py`.
- **What's new**: optional per-rule `**Negative anchors**:` field. Comma-separated tokens; case-insensitive; lowered + deduped at parse. Acts as final filter on positive applicability decisions: a rule that would otherwise fire is suppressed when ≥1 negative anchor matches the slice's mission-brief + design text via case-insensitive word-boundary regex.
- **Validation**: each negative anchor MUST NOT also appear in the same rule's `Trigger keywords` or `Trigger anchors` (overlap is contradictory). Overlap emits `negative-anchor-overlaps-positive` parse violation (Important). Unrecognized field name (e.g., typo `Negative anchor`) is silently ignored — same posture as `Trigger anchors:` per ADR-004 (only the exact field name parses; v1 doesn't fuzzy-match).
- **Backward-compat**: rules without `Negative anchors:` field have empty `negative_anchors` tuple; `_negative_anchor_match` returns False; behavior identical to pre-slice-008.

### Parse-violation kind `negative-anchor-overlaps-positive`

- **Defined in**: `tools/build_checks_audit.py` `_parse_rules`.
- **What's new**: parallel to slice-005's `anchor-not-in-keywords`. Emitted when a rule's negative anchors overlap with `Trigger keywords` OR `Trigger anchors`.
- **Severity**: Important (matches `anchor-not-in-keywords` precedent).
- **Message format**: `f"rule {rule_id}: Negative anchor '{anchor}' overlaps with positive Trigger keywords/anchors. Negative anchors must be exclusionary (no overlap with positive vocabulary)."`

## Data model deltas

`BuildCheckRule` dataclass adds field `negative_anchors: tuple[str, ...]` (defaults to empty tuple; lowered tokens). `to_dict()` includes `negative_anchors: list`. No DB migrations — the audit is markdown-parser + pure-Python.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no new modules — all changes are extensions of existing files (`tools/build_checks_audit.py`, `architecture/build-checks.md`, `~/.claude/build-checks.md`, `tests/methodology/test_build_checks_audit.py`, `methodology-changelog.md`, `VERSION`, `~/.claude/ai-sdlc-VERSION`, `plugin.yaml`). Empty-matrix posture (header + separator only — accepted by audit per slice-005 fixture pattern).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-007-bc-1-negative-context-anchors-via-final-filter]] — adopt option (b) from slice-007 deferred description: extend BC-1 schema with `Negative anchors:` per-rule field acting as final filter on positive applicability decisions; curate the field on BC-PROJ-1 + BC-PROJ-2 + BC-GLOBAL-1 with a 9-token methodology-vocabulary set. Reversibility: **cheap** (additive; ~15-line revert in audit module + clear field strings from rules).

## Authorization model for this slice

N/A — slice modifies a methodology audit that runs locally on the developer's machine; no auth/authz surface.

## Error model for this slice

The audit's exit-code semantics are unchanged:
- **0**: clean (rules surfaced or none apply).
- **1**: parse violation in build-checks.md (any kind: `missing-field`, `invalid-severity`, `anchor-not-in-keywords`, **NEW** `negative-anchor-overlaps-positive`).
- **2**: usage error (slice folder not found, etc.).

The new `negative-anchor-overlaps-positive` kind reuses the existing `BuildCheckViolation` dataclass + `_format_human` rendering — no new error path.

## Test-first plan refinement (post-Critic; 9 rows)

Mission-brief AC #1-3 verifications in design.md narrow to **build-time scenario** with `--changed-files` matching each slice's representative changed pattern. This makes TF-1 PENDING -> WRITTEN-FAILING transitions genuine pre-slice-008:

- **AC #1 test** (`test_slice_005_archive_no_longer_fires_proj1_or_global1`): invokes audit on slice-005 archive WITH `--changed-files=["tools/build_checks_audit.py", "architecture/build-checks.md"]` -> pre-fix: BC-PROJ-1 + BC-GLOBAL-1 in applicable (2-way fail per Critic M1: BC-PROJ-2 also fires pre-fix, but the AC asserts only BC-PROJ-1 + BC-GLOBAL-1 NOT in applicable — BC-PROJ-2's status irrelevant); post-fix: BC-PROJ-1 + BC-GLOBAL-1 in skipped, BC-PROJ-2 STILL FIRES (acceptable per AC #1 explicit gating).
- **AC #2 test** (`test_slice_006_archive_no_longer_fires_proj1_or_global1`): slice-006 archive WITH `--changed-files=["agents/critique.md"]` -> pre-fix: BC-PROJ-1 + BC-GLOBAL-1 in applicable (2-way fail); post-fix: in skipped.
- **AC #3 test** (`test_slice_007_archive_no_longer_fires_proj1_or_global1`): slice-007 archive WITH `--changed-files=["agents/critique.md", "skills/critic-calibrate/SKILL.md"]` -> pre-fix: BC-PROJ-1 + BC-GLOBAL-1 in applicable (2-way fail); post-fix: in skipped.
- **AC #4 test** (`test_slice_001_archive_still_fires_legitimate_rules`): slice-001 archive WITH `--changed-files=["skills/diagnose/SKILL.md", "skills/diagnose/write_pass.py", "skills/diagnose/passes/01-intent.md"]` -> pre-fix and post-fix: BC-PROJ-1 + (BC-PROJ-2 OR BC-GLOBAL-1) in applicable. The TF-1 PENDING -> WRITTEN-FAILING genuineness comes from `AttributeError: 'BuildCheckRule' object has no attribute 'negative_anchors'` — the test reads `negative_anchors` as part of validation. Same pattern as slice-005's `test_migrated_rules_have_expected_anchors` per Critic M1.
- **AC #5a test** (`test_negative_anchors_schema_documents_field_name_in_both_files`, per Critic M2): prose-pin TWO-surface — `Negative anchors` substring (case-sensitive) in BOTH `architecture/build-checks.md` AND `~/.claude/build-checks.md`. Pre-fix: substring absent in both -> fail; post-fix: present in both -> pass. Pin pattern matches slice-005 `test_build_checks_schema_documents_trigger_anchors_field_name`.
- **AC #5b test** (`test_negative_anchors_schema_documents_final_filter_semantics`, per Critic M2): prose-pin TWO-surface — `final filter` substring (case-insensitive) in BOTH files. Pre-fix: substring absent -> fail; post-fix: present -> pass. Mirror of slice-005's separate `word-boundary` semantics-phrase pin. Per Critic M2: pinning ONLY the field name leaves the semantic phrase unprotected against doc-refactor drift; the `final filter` phrase encodes the universal post-applicability framing.
- **Must-not-defer test 1** (`test_negative_anchor_overlaps_positive_yields_violation`): mirror of `test_anchor_not_in_keywords_yields_violation`. Constructs inline tmp_path fixture with a rule whose negative anchors overlap with positive ones; asserts violation kind + rule_id + offending anchor name in message. Pre-fix: `_parse_rules` doesn't recognize Negative anchors field; no violation emitted; test fails on len assertion. Post-fix: passes.
- **Must-not-defer test 2** (`test_migrated_rules_have_expected_negative_anchors`): mirror of `test_migrated_rules_have_expected_anchors`. Reads `architecture/build-checks.md` + (when present) `~/.claude/build-checks.md` via `_parse_rules` and asserts BC-PROJ-1.negative_anchors == BC-GLOBAL-1.negative_anchors == the canonical 9-token tuple `("defer-with-rationale", "aggregated lessons", "false positive", "meta-discussion", "vocabulary", "critic-missed", "back-sync", "dim 9", "forward-sync")` (lowered). BC-PROJ-2 NOT asserted (per Critic M1 — not migrated). Pre-fix: rules don't have negative_anchors field set (empty tuple); test fails on tuple equality. Post-fix: passes.
- **Must-not-defer test 3** (`test_always_true_rule_with_negative_anchor_match_is_skipped`, per Critic M3): inline tmp_path fixture with a rule `Applies to: always: true` + `Negative anchors: foo` + slice text containing `foo`. Asserts rule appears in `result.skipped`, NOT in `result.applicable`. Counter-tests the `always: true` short-circuit + negative-anchor interaction explicitly. Pre-fix: `_rule_applies` returns True immediately on `always: true` regardless of negative anchors -> rule in applicable -> test fails. Post-fix: `_rule_applies` returns `not _negative_anchor_match(...)` on always-true; with foo matching, returns False -> rule in skipped -> test passes. Closes the algorithm-path-conformance gap per slice-005 lesson (which slice-008 explicitly inherits): missing path coverage was the exact failure mode caught at /build-slice T5 last time.

**Final TF-1 plan: 9 rows total** (4 numbered-AC + 2 split-AC #5 + 3 must-not-defer). Mission-brief had 5 PENDING rows; design.md grew to 7 (2 must-not-defer-driven); Critic grew to 9 (AC #5 split per M2 + always-true row per M3). Per slice-007 lesson "TF-1 plan grew 4 -> 5 -> 7 rows," slice-008 ratchets the generalization further to 5 -> 7 -> 9 rows. Schema-pin TWO-surface discipline now confirmed at N-surface = 2 rules (BC-PROJ-1 + BC-GLOBAL-1) × 2 substrings (`Negative anchors` + `final filter`) × 2 files = 8 prose-pin assertion sites.

## Mid-slice smoke gate (refinement)

At ~50% (after schema + audit logic + 1 of 5 ACs implemented):

```
PY=<HOME>\.claude\.venv\Scripts\python.exe
$PY -m tools.build_checks_audit --slice architecture/slices/archive/slice-007-add-critique-agent-content-equality-audit --project-checks architecture/build-checks.md --changed-files agents/critique.md skills/critic-calibrate/SKILL.md --no-carry-over --json
```

Expected: `applicable` array does NOT contain BC-PROJ-1 or BC-GLOBAL-1.

If still firing: STOP, diagnose. Likely root causes:
- Negative-anchor check applied at wrong point in algorithm (e.g., only on keyword path, not glob path; per algorithm-path-conformance lesson).
- Negative-anchor token typo in build-checks.md (`fwd-sync` instead of `forward-sync`); `_parse_rules` lowercases but doesn't fuzzy-match.
- Missing `--changed-files` in invocation (slice-007 archive WITHOUT --changed-files trivially passes pre-fix — defeats the smoke).

## Pre-finish gate

(per mission-brief, plus design refinements)

- All 5 ACs PASS (with AC #5 split into 5a + 5b per Critic M2) with evidence in `validation.md`.
- **9 TF-1 rows** all PASSING (5 + 2 from design + 2 added at /critique per M2 + M3).
- All must-not-defer items addressed (input validation via `negative-anchor-overlaps-positive`; TF-1 genuineness; TWO-surface × TWO-substring schema pin; always-true + negative-anchor interaction tested; methodology-changelog v0.23.0; PMI-1 clean; bidirectional sha256 forensic capture for `~/.claude/build-checks.md`; backward-compat covenant).
- `/drift-check` passes.
- Mid-slice smoke still passes.
- No new TODOs / FIXMEs / debug prints.
- PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0.
- Existing 22+ BC-1 tests still PASSING (regression-guard via TF-1 + pytest run).
- Self-application: `python -m tools.build_checks_audit --slice architecture/slices/slice-008-refine-bc-1-anchors-with-negative-context --project-checks architecture/build-checks.md --changed-files tools/build_checks_audit.py architecture/build-checks.md --no-carry-over` returns BC-PROJ-1 + BC-GLOBAL-1 in skipped (the slice's own text contains `vocabulary`, `Dim 9`, `back-sync`, `forward-sync`). Captured in `build-log.md` Phase 4. Closes the noise loop on its own ship.
