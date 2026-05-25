# Slice 008: refine-bc-1-anchors-with-negative-context

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: MEDIUM — silences confirmed N=3 BC-1 false-positive class on methodology-vocabulary slices (BC-PROJ-1 + BC-GLOBAL-1 firing on slices that merely *cite* anchor keywords as historical lesson context, not as actual subagent-fan-out / LLM-fence-parsing implementation). Restores BC-1's signal-to-noise so future slices touching methodology vocabulary don't train the builder to ignore BC-1 surfacing. Also: refines the BC-1 keyword-applicability mechanism per BC-1 v0.10.0 + ADR-004 schema, which is the third precision iteration on BC-1 in slice-005..008.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Eliminate the N=3 BC-1 false-positive class on methodology-vocabulary slices (confirmed at slice-005 + slice-006 + slice-007) without breaking legitimate matches (slice-001 is the canonical legitimate fence-parsing + subagent-fan-out slice; it MUST continue to fire BC-PROJ-1 AND at least one of BC-PROJ-2 / BC-GLOBAL-1). The slice introduces some form of **negative-context anchor** to the BC-1 keyword-applicability mechanism so a rule whose anchors fire on a methodology-vocabulary slice can be silenced when the slice's text also matches a designated negative-context anchor (e.g., `vocabulary`, `meta-discussion`, `defer-with-rationale`, `aggregated lessons`). The exact implementation choice — (a) refine existing BC-PROJ-1 + BC-GLOBAL-1 anchors with negative-context exclusions, (b) extend the BC-1 schema with an explicit `Negative anchors:` field per rule, or (c) hybrid — is locked at `/design-slice`, not here. This brief is option-agnostic about the HOW; ACs are option-agnostic.

## Acceptance criteria

1. After this slice ships, running the BC-1 audit against slice-005's archived `mission-brief.md` + `design.md` (with the project + global build-checks files this slice touched) yields an `applicable` set that does NOT include `BC-PROJ-1` and does NOT include `BC-GLOBAL-1` (negative case 1/3 — the slice that introduced anchors itself; the false-positive recurred there).
2. After this slice ships, running the BC-1 audit against slice-006's archived `mission-brief.md` + `design.md` yields an `applicable` set that does NOT include `BC-PROJ-1` and does NOT include `BC-GLOBAL-1` (negative case 2/3).
3. After this slice ships, running the BC-1 audit against slice-007's archived `mission-brief.md` + `design.md` yields an `applicable` set that does NOT include `BC-PROJ-1` and does NOT include `BC-GLOBAL-1` (negative case 3/3 — meets BC-1 promotion threshold per slice-006 reflection lesson).
4. After this slice ships, running the BC-1 audit against slice-001's archived `mission-brief.md` + `design.md` yields an `applicable` set that DOES include `BC-PROJ-1` AND DOES include at least one of `BC-PROJ-2` / `BC-GLOBAL-1` (positive case — the canonical legitimate fence-parsing + subagent-fan-out slice continues to fire; backward-compat covenant per ADR-004).
5. The schema-prose changes introduced by this slice are pinned in BOTH `architecture/build-checks.md` AND `~/.claude/build-checks.md` (TWO-surface schema-pin discipline per slice-005 + Critic M2 generalization to N-surface). Both files contain the canonical literal substring `Negative anchors` (field-name surface) AND the canonical literal substring `final filter` (algorithm-semantics surface).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_build_checks_audit.py | test_slice_005_archive_no_longer_fires_proj1_or_global1 | PASSING |
| 2 | unit | tests/methodology/test_build_checks_audit.py | test_slice_006_archive_no_longer_fires_proj1_or_global1 | PASSING |
| 3 | unit | tests/methodology/test_build_checks_audit.py | test_slice_007_archive_no_longer_fires_proj1_or_global1 | PASSING |
| 4 | unit | tests/methodology/test_build_checks_audit.py | test_slice_001_archive_still_fires_legitimate_rules | PASSING |
| 5 | unit | tests/methodology/test_build_checks_audit.py | test_negative_anchors_schema_documents_field_name_in_both_files | PASSING |
| 5 | unit | tests/methodology/test_build_checks_audit.py | test_negative_anchors_schema_documents_final_filter_semantics | PASSING |
| 5 | unit | tests/methodology/test_build_checks_audit.py | test_always_true_rule_with_negative_anchor_match_is_skipped | PASSING |
| 5 | unit | tests/methodology/test_build_checks_audit.py | test_negative_anchor_overlaps_positive_yields_violation | PASSING |
| 5 | unit | tests/methodology/test_build_checks_audit.py | test_migrated_rules_have_expected_negative_anchors | PASSING |

**Notes**:
- TF-1 PENDING -> WRITTEN-FAILING transitions MUST be genuine per slice-005+006+007 lesson. Pin specific signals: e.g., AC #1-3 fail pre-fix because `BC-PROJ-1 in applicable` and `BC-GLOBAL-1 in applicable` (with build-time `--changed-files` matching each slice's representative pattern per design.md narrowing); AC #4 fails pre-fix because the audit doesn't yet know about `negative_anchors` field (AttributeError); AC #5a/5b fail pre-fix because the new substrings aren't in either file yet.
- TF-1 plan grew 5 (mission-brief at /slice) -> 7 (design.md: 2 must-not-defer rows added) -> 9 (post-Critic: AC #5 split into 5a + 5b per Critic M2; new must-not-defer always-true row per Critic M3). Per slice-007 lesson: schema-pin TWO-surface discipline generalizes to N-surface for any AC with multi-surface coverage. Slice-008 confirms the generalization at N=9.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | slice-005 archive no longer fires BC-PROJ-1 or BC-GLOBAL-1 | `python -m tools.build_checks_audit --slice architecture/slices/archive/slice-005-add-bc-1-keyword-precision --project-checks architecture/build-checks.md --no-carry-over --json` -> assert `applicable` array has no element with `rule_id == "BC-PROJ-1"` and no element with `rule_id == "BC-GLOBAL-1"` |
| 2 | slice-006 archive no longer fires BC-PROJ-1 or BC-GLOBAL-1 | same pattern, `--slice architecture/slices/archive/slice-006-update-critic-with-cross-cutting-conformance-dimension` |
| 3 | slice-007 archive no longer fires BC-PROJ-1 or BC-GLOBAL-1 | same pattern, `--slice architecture/slices/archive/slice-007-add-critique-agent-content-equality-audit` |
| 4 | slice-001 archive still fires legitimate rules | `python -m tools.build_checks_audit --slice architecture/slices/archive/slice-001-diagnose-orchestration-fix --project-checks architecture/build-checks.md --no-carry-over --json` -> assert `applicable` includes `BC-PROJ-1` AND (`BC-PROJ-2` OR `BC-GLOBAL-1`) |
| 5 | schema substring pinned in both surfaces | pytest reads `architecture/build-checks.md` AND `~/.claude/build-checks.md`; both files contain the canonical schema substring chosen at `/design-slice` (e.g., `Negative anchors` if option-(b)/(c); else the prose-clarification substring chosen) |

## Must-not-defer

- [ ] Input validation on any new BC-1 schema field (per slice-005's `anchor-not-in-keywords` precedent: anchors that aren't subsets of keywords -> parse violation. Any new `Negative anchors:` field MUST validate similarly — e.g., negative anchors that overlap with positive anchors, OR negative anchors not in `Trigger keywords`, are explicit parse violations, not silent no-ops). Lock the violation kind name + message at `/design-slice`.
- [ ] TF-1 PENDING -> WRITTEN-FAILING genuine transitions per slice-005+006+007 lesson. Pin specific failure signals (e.g., `AssertionError` with `BC-PROJ-1 in applicable`; `AttributeError` on missing schema field; absent substring in pinned file). No coincidental passes.
- [ ] Schema-pin TWO-surface discipline atomically: changes to `architecture/build-checks.md` AND `~/.claude/build-checks.md` ship in the same slice. The two files are bidirectionally synced.
- [ ] BC-1 v0.x.0 entry appended to `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md`. The `## Vault updates made` section in `reflection.md` MUST be verifiable by running PMI-1 audit (`tools.plugin_manifest_audit --root .`) per slice-007 escape closure (B2 calibration class).
- [ ] PMI-1 audit clean post-build (`python -m tools.plugin_manifest_audit --root .` exits 0). Per slice-006 PMI-1 escape lesson, claim made in `## Vault updates made` MUST be verifiable by audit.
- [ ] Bidirectional sha256 forensic capture in `build-log.md` if `~/.claude/build-checks.md` is touched (Phase 0 + Phase 4 pattern, N=2 stable per slice-006 + slice-007). Capture in-repo + installed sha256 BEFORE and AFTER the edits.
- [ ] Backward-compat covenant: rules without the new schema field continue to behave with current applicability semantics (per ADR-004 backward-compat: "rules without `Trigger anchors:` keep firing on any keyword match"). The new mechanism is additive, not breaking. Verify via the existing 22+ BC-1 test suite continuing to pass.
- [ ] No regression on the existing BC-1 + audit test suite. TF-1 strict-pre-finish refuses on any new test row in non-PASSING status; the regression-guard for "all existing tests pass" lives in verification-plan + must-not-defer (per slice-002+004+005 "no meta-AC" lesson).
- [ ] BC-PROJ-2 behavior unchanged: BC-PROJ-2 has `Applies to: skills/**/*.py, tools/**/*.py` (not `**` like BC-GLOBAL-1) — its keyword-path firing is conditional on glob fall-through, so BC-PROJ-2's interaction with the new mechanism MUST be empirically verified (does this slice's text trigger BC-PROJ-2? what about slice-005..007 archives?). Capture algorithm-path-conformance evidence at `/design-slice` per slice-005 lesson.
- [ ] Out-of-repo edits (`~/.claude/build-checks.md`) explicitly captured in `build-log.md` as forensic evidence (slice's git diff alone insufficient — N=3 stable lesson per slice-005+006+007).

## Out of scope

- BC-1 morphological-variant expansion (e.g., adding `parses, parsed, parsing` to BC-PROJ-2's `Trigger keywords`) — deferred N=1 from slice-005, still no recurrence; out of scope for this slice.
- `fix-bc-1-archived-slice-heuristic` (`audit_slice` `parent.parent` heuristic broken for archived paths) — slice-005 carry-over, separate ~30-min slice, workaround `--project-checks` acceptable. This slice's verification plan uses `--project-checks` explicitly, so the heuristic bug doesn't block.
- Refining Dim 9 of `agents/critique.md` with the design.md-mechanical-tables sub-clause — separate slice; N=2 promotion threshold met per slice-007 reflection but distinct scope (agent prompt refinement, not BC-1 audit refinement).
- BC-PROJ-2 modifications — empirical verification at design-time + Critic M1 confirmed BC-PROJ-2 fires false-positively only on slice-005 (N=1; the original BC-1 anchors-precision slice). Slice-006 + slice-007 do NOT trigger BC-PROJ-2 (their changed-files don't match `skills/**/*.py, tools/**/*.py` per the glob's required subfolder structure — BC-PROJ-2 skipped on both backtests). N=1 does NOT meet the BC-1 promotion threshold (N=3 per slice-007 reflection's promotion convention). **Defer BC-PROJ-2 migration until N=2 surfaces** (i.e., a future slice modifying a file under `skills/**/*.py` or `tools/**/*.py` AND citing methodology-vocabulary anchors). The slice's own AC framework (#1-4) does NOT gate BC-PROJ-2: AC #4 explicitly accepts `BC-PROJ-1 AND (BC-PROJ-2 OR BC-GLOBAL-1)` for slice-001's positive case.
- Auto-detection of recurring-pattern build-checks at `/critic-calibrate` — BC-1 v2 deferred from v0.10.0 release notes; out of scope.
- Promoting the BC-1 false-positive class lesson to a new BC-N rule — meta; not the right level of intervention for this recurrence.
- INST-2 generalization (general content-equality audit across all installed files) — deferred N=1 from slice-007.

## Dependencies

- Prior slices: [[slice-005-add-bc-1-keyword-precision]] — schema ground (word-boundary regex + optional `Trigger anchors:` field; any negative-context mechanism extends this); [[slice-006-update-critic-with-cross-cutting-conformance-dimension]] + [[slice-007-add-critique-agent-content-equality-audit]] — surface the N=2 + N=3 false-positive recurrences in their reflections.
- Vault refs: [[architecture/build-checks.md]] (project-level rules + schema prose), [[decisions/ADR-004-bc-1-keyword-precision-via-word-boundary-and-anchors]] (chooses anchors over alternatives; this slice extends, not supersedes), `~/.claude/build-checks.md` (global-level rules + schema prose), [[methodology-changelog.md]] BC-1 entry at v0.10.0 + the upcoming v0.x.0 entry this slice authors.
- Risk register: none (this slice doesn't retire R-1 or R-2; both are /diagnose-related).
- Tooling: `tools.build_checks_audit` (modify `_rule_applies` + `_parse_rules` + `BuildCheckRule` dataclass, depending on chosen option); `tools.plugin_manifest_audit` (PMI-1 gate, post-build). Existing 22+ BC-1 tests in `tests/methodology/test_build_checks_audit.py` continue to pass (regression-guard).

## Mid-slice smoke gate

At ~50% of build (after schema/audit logic is implemented but before all TF-1 tests are wired):

```
python -m tools.build_checks_audit --slice architecture/slices/archive/slice-007-add-critique-agent-content-equality-audit --project-checks architecture/build-checks.md --no-carry-over
```

Expected: BC-PROJ-1 and BC-GLOBAL-1 absent from `applicable`. Existing rule firings on legitimate slices (slice-001 backtest) unchanged.

If still firing (or if slice-001 stops firing): STOP, diagnose. Likely root causes:
- Negative-context substring not present in slice-007 mission-brief / design (re-read; pick a different anchor candidate)
- Algorithm-path-conformance gap: the new mechanism short-circuited or interacts badly with `always: true` short-circuit / glob path / existing anchor filter — trace through `_rule_applies` like slice-005 should have
- BC-PROJ-2 inadvertently affected — verify its applicability table

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (input validation, TF-1 genuineness, TWO-surface pin, methodology-changelog v0.x.0, PMI-1 clean, sha256 capture if `~/.claude/build-checks.md` touched, backward-compat, BC-PROJ-2 unchanged behavior captured, out-of-repo edit forensics)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0
- [ ] Existing 22+ BC-1 tests still pass (TF-1 strict-pre-finish picks up regression-guard via existing rows)
- [ ] Self-application check: this slice's own mission-brief.md + design.md, after the audit refinement ships, no longer triggers BC-PROJ-1 / BC-GLOBAL-1 false-positively (the slice's own text mentions methodology-vocabulary anchors `subagent`, `fence`, `code-block`, `llm` — meta-test of "validate using your own ship" pattern N=5 stable per slice-003..007). Deferred-with-rationale acceptable IF the slice's text genuinely IS about implementing a methodology rule (which it is); the negative-context mechanism should silence it cleanly. Self-application result captured in `build-log.md` Phase 4.
