# Slice 012: bc-proj-2-negative-anchor-migration

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: MEDIUM — silences the confirmed N=2 BC-PROJ-2 false-positive class on methodology-vocabulary slices (slice-005 + slice-011). Restores BC-PROJ-2's signal-to-noise so future methodology-vocabulary slices modifying `skills/**/*.py` or `tools/**/*.py` and citing `fence`/`code-block`/`llm` as historical-lesson context (not as actual LLM-fence-parsing implementation) don't train the builder to ignore BC-1 surfacing. Completes the BC-1 v1.2 negative-anchor rollout — BC-PROJ-1 + BC-GLOBAL-1 migrated at slice-008; BC-PROJ-2 deferred there to N=2 evidence threshold per slice-008 Critic M1; threshold MET at slice-011.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Migrate BC-PROJ-2 in `architecture/build-checks.md` to BC-1 v1.2 by adding the 9-token methodology-vocabulary `Negative anchors:` field mirroring slice-008's BC-PROJ-1 + BC-GLOBAL-1 v1.2 migration. The token set is the same 9-token methodology-vocabulary set ratified at slice-008 (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`) — uniformity across the three BC-1 rules eliminates per-rule negative-anchor divergence and makes future BC-1 v1.x refinements composable. Schema-prose changes (the `Negative-context anchors` paragraph in `architecture/build-checks.md` and `~/.claude/build-checks.md`) are already in place from slice-008; this slice is rule-level data migration only, not schema change. Backward-compat covenant: slice-001's archive (canonical legitimate LLM-fence-parsing slice) MUST continue to fire BC-PROJ-2 — slice-001's text does NOT cite methodology-meta vocabulary, so the negative anchors don't suppress it.

## Acceptance criteria

1. After this slice ships, running the BC-1 audit against slice-005's archived `mission-brief.md` + `design.md` (with build-time `--changed-files` representative of BC-PROJ-2's `skills/**/*.py, tools/**/*.py` glob path — e.g., `tools/build_checks_audit.py`) yields an `applicable` set that does NOT include `BC-PROJ-2` (negative case 1/2 — slice-005's own anchors-precision text triggers BC-PROJ-2 false-positively via prose-describing-the-rule; this was the N=1 evidence at slice-008 Critic M1).
2. After this slice ships, running the BC-1 audit against slice-011's archived `mission-brief.md` + `design.md` (with build-time `--changed-files` representative of BC-PROJ-2's `skills/**/*.py, tools/**/*.py` glob path) yields an `applicable` set that does NOT include `BC-PROJ-2` (negative case 2/2 — meets BC-1 promotion threshold per slice-008 Critic M1 N=2 deferral language; slice-011 RSAD-1 codification surfaced the N=2 evidence threshold by re-firing BC-PROJ-2 via methodology-vocabulary anchors).
3. After this slice ships, running the BC-1 audit against slice-001's archived `mission-brief.md` + `design.md` yields an `applicable` set that DOES include `BC-PROJ-2` (positive case — the canonical legitimate LLM-fence-parsing slice continues to fire; backward-compat covenant per ADR-007 BC-1 v1.2 backward-compat clause).
4. The BC-PROJ-2 rule definition in `architecture/build-checks.md` contains the canonical literal substring `Negative anchors:` (field-name surface) AND the 9-token methodology-vocabulary set verbatim (`defer-with-rationale`, `aggregated lessons`, `false positive`, `meta-discussion`, `vocabulary`, `Critic-MISSED`, `back-sync`, `Dim 9`, `forward-sync`).
5. A BC-1 v1.3 entry appended to BOTH in-repo `methodology-changelog.md` AND installed `~/.claude/methodology-changelog.md` (bidirectional, per slice-008 N-surface schema-pin discipline) naming BC-PROJ-2 explicitly + the 9-token methodology-vocabulary set + the N=2 cross-slice evidence anchors (`slice-005` + `slice-011`) + **the substantive canonical phrase `BC-PROJ-2 negative-anchor migration`** (per /critique m1 ACCEPTED-FIXED, mirroring slice-008/009/010/011 N-surface schema-pin 3-pin shape: `## vNN.NN.0` + rule-ID + canonical phrase); PMI-1 invariant maintained atomically (`VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` all 0.26.0 → 0.27.0).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0)

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING -> PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_build_checks_audit.py | test_slice_005_archive_no_longer_fires_proj2 | PASSING |
| 2 | unit | tests/methodology/test_build_checks_audit.py | test_slice_011_archive_no_longer_fires_proj2 | PASSING |
| 3 | unit | tests/methodology/test_build_checks_audit.py | test_slice_001_archive_still_fires_proj2 | PASSING |
| 4 | unit | tests/methodology/test_build_checks_audit.py | test_bc_proj_2_has_methodology_vocabulary_negative_anchors | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_27_0_bc_proj_2_entry_present_in_repo_and_installed | PASSING |
| 5 | unit | tests/methodology/test_methodology_changelog.py | test_plugin_yaml_version_matches_version_file_at_0_27_0 | PASSING |

**Notes**:
- TF-1 PENDING -> WRITTEN-FAILING transitions MUST be genuine per slice-005..011 lesson (N=8 stable). Pin specific signals: AC #1-2 fail pre-fix because `BC-PROJ-2 in applicable` for slice-005 + slice-011 archive backtests; AC #3 must NOT regress (slice-001 still fires); **AC #4 per /critique B1 ACCEPTED-FIXED**: test uses `_parse_rules` + `by_id['BC-PROJ-2'].negative_anchors == expected_negative_anchors` per-rule scoping (NOT naive file-level substring), because all 9 tokens already exist on BC-PROJ-1's `architecture/build-checks.md:20` Negative-anchors line (slice-008) — naive substring would PASS pre-migration, defeating TF-1 genuineness. Pinned failure signal: `AssertionError: BC-PROJ-2 negative_anchors mismatch: got (), expected (...)`; AC #5 row 1 fails pre-fix because v0.27.0 entry-with-canonical-phrase not yet written (`AssertionError: 'BC-PROJ-2 negative-anchor migration' not in <file>`) AND AC #5 row 2 fails pre-fix because PMI-1 versioned-gate still pinned to `_at_0_26_0`.
- Final TF-1 row count locked at `/design-slice` per slice-005..011 grew-during-design precedent. Initial estimate at /slice: 6 rows. May grow to 7-9 at /design-slice if Critic surfaces split-AC rows (e.g., schema-pin N-surface discipline split across in-repo + installed surfaces, or per-anchor location-pin tests).
- PMI-1 versioned-gate supersession N=4 events stable post-slice-011; slice-012 supersedes `_at_0_26_0` → `_at_0_27_0` (N=5 supersession events post-slice-012).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | slice-005 archive no longer fires BC-PROJ-2 | `python -m tools.build_checks_audit --slice architecture/slices/archive/slice-005-add-bc-1-keyword-precision --project-checks architecture/build-checks.md --changed-files tools/build_checks_audit.py --no-carry-over --json` -> assert `applicable` array has no element with `rule_id == "BC-PROJ-2"` |
| 2 | slice-011 archive no longer fires BC-PROJ-2 | same pattern, `--slice architecture/slices/archive/slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose` |
| 3 | slice-001 archive still fires BC-PROJ-2 | `python -m tools.build_checks_audit --slice architecture/slices/archive/slice-001-diagnose-orchestration-fix --project-checks architecture/build-checks.md --changed-files skills/diagnose/write_pass.py --no-carry-over --json` -> assert `applicable` includes element with `rule_id == "BC-PROJ-2"` |
| 4 | BC-PROJ-2 rule body has `Negative anchors:` + all 9 tokens | pytest reads `architecture/build-checks.md`; locates BC-PROJ-2 rule section (`## BC-PROJ-2 — ...` heading); asserts `Negative anchors:` line present; asserts all 9 canonical tokens present in that line |
| 5 | BC-1 v0.27.0 entry pinned in both surfaces + PMI-1 atomic + canonical phrase pin | pytest reads `methodology-changelog.md` AND `~/.claude/methodology-changelog.md`; both contain `## v0.27.0`, `BC-PROJ-2`, `slice-005`, `slice-011`, the 9-token canonical set, AND the substantive canonical phrase `BC-PROJ-2 negative-anchor migration` (per /critique m1 ACCEPTED-FIXED N-surface schema-pin 3-pin shape). Also: PMI-1 audit (`tools.plugin_manifest_audit --root .`) exits 0; `plugin.yaml.version == 0.27.0` matches `VERSION` and `~/.claude/ai-sdlc-VERSION` |

## Must-not-defer

- [ ] Input validation on `Negative anchors:` field for BC-PROJ-2 specifically: the 9 tokens MUST NOT overlap with BC-PROJ-2's existing `Trigger keywords` (`parse, fence, code-block, backtick, llm, agent, prompt, output, response`) or `Trigger anchors` (`fence, code-block, llm`). Per slice-008 `negative-anchor-overlaps-positive` parse-violation kind. Verify at `/design-slice` via explicit token-disjointness check. (None of the 9 methodology-vocabulary tokens overlap with BC-PROJ-2's positive sets — pre-validated, but lock at /design-slice.)
- [ ] TF-1 PENDING -> WRITTEN-FAILING genuine transitions per slice-003..011 lesson (N=8 stable). Pin specific failure signals: AC #1-2 `AssertionError: BC-PROJ-2 in applicable`; AC #3 `AssertionError: BC-PROJ-2 not in applicable` (regression guard); AC #4 `AssertionError: 'Negative anchors:' not in BC-PROJ-2 rule body` or `AssertionError: token X not in negative-anchors line`; AC #5 substring-absent signals.
- [ ] Backward-compat covenant: BC-PROJ-2 positive case (slice-001) continues to fire. Slice-001's `mission-brief.md` + `design.md` MUST NOT contain any of the 9 methodology-vocabulary tokens at word-boundary — verify EMPIRICALLY at `/design-slice` by grepping slice-001 archive for each token. If any token is present in slice-001's text, that token must be dropped from BC-PROJ-2's negative-anchor set (per slice-008 Critic M1 precedent: BC-PROJ-1 / BC-GLOBAL-1 token-set was curated against slice-001 archive at design time to preserve the positive case).
- [ ] BC-1 v0.27.0 entry appended to `methodology-changelog.md` (in-repo) AND `~/.claude/methodology-changelog.md`. Entry MUST name BC-PROJ-2 explicitly, the 9-token canonical set, AND the N=2 cross-slice anchors (`slice-005` + `slice-011`). Per slice-009 + slice-010 + slice-011 N-surface schema-pin discipline (N=3 stable).
- [ ] PMI-1 audit clean post-build: `python -m tools.plugin_manifest_audit --root .` exits 0. `plugin.yaml.version` 0.26.0 → 0.27.0 atomically with `VERSION` + `~/.claude/ai-sdlc-VERSION` (PMI-1 invariant per slice-007 escape-closure pattern).
- [ ] PMI-1 versioned-gate test supersession in `tests/methodology/test_methodology_changelog.py`: REPLACE `test_plugin_yaml_version_matches_version_file_at_0_26_0` with `test_plugin_yaml_version_matches_version_file_at_0_27_0`. Per slice-011 NEW Dim 9 sub-class candidate (entry-pin-vs-pmi-1-gate-semantics-conflation; N=1): scope the Edit `old_string` to ONLY the gate function body — NOT a wider section block that would silently delete the v0.26.0 entry-pin function `test_v_0_26_0_rsad_1_entry_present_in_repo_and_installed`. Entry-pins persist across all versions; only PMI-1 versioned-gates supersede with latest-only.
- [ ] Bidirectional sha256 forensic capture in `build-log.md` (N=7 stable post-slice-011). Phase 0 + Phase 4 sha256 for `methodology-changelog.md` (in-repo + installed). `architecture/build-checks.md` is in-repo only (no installed counterpart — BC-PROJ-2 is project-specific). `agents/critique.md` is NOT touched this slice; no need to capture (CAD-1 byte-equality test continues to pass unchanged as regression guard).
- [ ] Backward-compat covenant: rules without the new `Negative anchors:` field continue to behave with current applicability semantics (per ADR-007 BC-1 v1.2 backward-compat). This slice MIGRATES BC-PROJ-2 from no-negative-anchors to with-negative-anchors; rules NOT touched (e.g., future BC-N additions) remain backward-compat.
- [ ] No regression on the existing BC-1 audit test suite (29+ tests post-slice-011). TF-1 strict-pre-finish refuses on any non-PASSING row; existing tests' continued passing is the regression-guard, NOT a separate AC (per slice-002+004+005 "no meta-AC" lesson).
- [ ] Self-application check (validate-using-your-own-ship, N=9 stable post-slice-011): this slice's OWN `mission-brief.md` + `design.md`, after the BC-PROJ-2 migration ships, MUST NOT trigger BC-PROJ-2 false-positively at Phase 4 BC-1 self-application audit. The slice's text mentions BC-PROJ-2 positive anchors (`fence`, `code-block`, `llm`) as historical-lesson context AND mentions methodology-vocabulary negative-anchors (`vocabulary`, `meta-discussion`, `defer-with-rationale`, `Dim 9`, etc.) — the new negative-anchor filter MUST silence BC-PROJ-2 cleanly. Capture in `build-log.md` Phase 4. Per slice-009 M2 + slice-010 DEVIATION-3 + slice-011 RSAD-1 codification: anticipate /critique B*/M* fix prose introducing or REMOVING anchor substrings into the slice's artifacts (recursive-self-application sub-mode now codified at agents/critique.md Dim 9 6th sub-clause). Verify both at design-time AND at Phase 4 post-build.

## Out of scope

- BC-PROJ-1 / BC-GLOBAL-1 modifications — already migrated at slice-008. Out of scope.
- BC-1 schema-prose changes — the `Negative-context anchors` paragraph in `architecture/build-checks.md` + `~/.claude/build-checks.md` is already present from slice-008. This slice is rule-level data migration only, not schema change.
- BC-1 morphological-variant expansion (e.g., `parses, parsed, parsing` for BC-PROJ-2's `Trigger keywords`) — deferred N=1 from slice-005, still no recurrence at slice-011; out of scope.
- `fix-bc-1-archived-slice-heuristic` (`audit_slice` `parent.parent` heuristic broken for archived paths) — slice-005 carry-over, separate ~30-min slice, workaround `--project-checks` acceptable. Verification plan uses `--project-checks` explicitly.
- `refactor-pmi-1-gate-to-version-agnostic-shape` — deferred 5 times across slices 007/008/009/010/011 (N=4 supersession events stable). Per-bump cost remains ~1 min trivial; defer one more cycle.
- RSAD-1 v2 audit tooling (`tools/rsad_1_audit.py`) — deferred at slice-011 to stay within 0.5-day budget; not this slice's scope.
- MCT-1 v2 audit tooling (`tools/mct_1_audit.py`) — deferred at slice-010; not this slice's scope.
- `/critic-calibrate` run — separate ~1-hour invocation; slice-012-015 window per slice-009/010/011 reflections; THIS slice doesn't run /critic-calibrate, just supplies one more reflection to the corpus.
- Auto-detection of recurring-pattern build-checks at `/critic-calibrate` — BC-1 v2 deferred from v0.10.0 release notes; out of scope.

## Dependencies

- Prior slices: [[slice-005-add-bc-1-keyword-precision]] — N=1 evidence for BC-PROJ-2 false-positive; [[slice-008-refine-bc-1-anchors-with-negative-context]] — schema ground (BC-1 v1.2 `Negative anchors:` field + audit logic + `negative-anchor-overlaps-positive` parse-violation; this slice REUSES that infrastructure verbatim, no code change to `tools/build_checks_audit.py`); [[slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose]] — N=2 evidence for BC-PROJ-2 false-positive (RSAD-1 codification slice surfaced the threshold).
- Vault refs: [[architecture/build-checks.md]] (BC-PROJ-2 rule definition — sole code-edit surface), [[decisions/ADR-007-bc-1-negative-context-anchors-via-final-filter]] (slice-008 ADR — corrected filename per /critique M3 ACCEPTED-FIXED; this slice extends the rollout to BC-PROJ-2), `~/.claude/build-checks.md` (global-level rules + schema prose), [[methodology-changelog.md]] BC-1 entry at v0.23.0 (slice-008) + the upcoming v0.27.0 entry this slice authors.
- Risk register: none (this slice doesn't retire R-1 or R-2; both are /diagnose-related, unchanged at slice-011).
- Tooling: `tools.build_checks_audit` (NO CODE CHANGE — slice-008 already shipped the `Negative anchors:` field parser, the final-filter algorithm, and the `negative-anchor-overlaps-positive` validation). `tools.plugin_manifest_audit` (PMI-1 gate, post-build, atomic 0.26.0 → 0.27.0). Existing 29+ BC-1 tests in `tests/methodology/test_build_checks_audit.py` continue to pass (regression-guard).

## Mid-slice smoke gate

At ~50% of build (after the rule body migration + methodology-changelog v0.27.0 entry are written but before all TF-1 tests are wired):

```
python -m tools.build_checks_audit --slice architecture/slices/archive/slice-011-promote-recursive-self-application-discipline-to-critique-skill-prose --project-checks architecture/build-checks.md --changed-files tools/build_checks_audit.py --no-carry-over
```

Expected: BC-PROJ-2 ABSENT from `applicable`. Existing rule firings on legitimate slice (slice-001 backtest with `--changed-files skills/diagnose/write_pass.py`) UNCHANGED — BC-PROJ-2 still fires.

If still firing on slice-011 (or if slice-001 stops firing): STOP, diagnose. Likely root causes:
- Negative-anchor substring not present in slice-011's archived text — re-read mission-brief + design.md; pick the specific token observed in the archive (slice-011's text contains `Dim 9`, `recursive self-application`, `Critic-MISSED`, `defer-with-rationale`, `back-sync`, `forward-sync`, etc. — at least one MUST match for the suppression to fire).
- Algorithm-path-conformance gap (slice-005 algorithm-path-conformance lesson, N=2 stable at slice-008): the slice-008 negative-anchor mechanism composes uniformly across `always: true` / glob / keyword-anchor paths. BC-PROJ-2 fires on the GLOB path (`skills/**/*.py, tools/**/*.py` matched by `--changed-files tools/build_checks_audit.py`) + the keyword path (`fence` anchor in slice-011's text). The negative filter applies as final filter on EITHER path. Trace through `tools.build_checks_audit._rule_applies` if suppression doesn't fire.
- slice-001's text accidentally contains a methodology-vocabulary token at word-boundary (regression on positive case) — empirically grep slice-001 archive for each of the 9 tokens BEFORE locking the set at /design-slice (slice-008 Critic M1 precedent).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (token-disjointness on BC-PROJ-2's positive sets, TF-1 genuineness, backward-compat for slice-001 positive case, methodology-changelog v0.27.0 bidirectional, PMI-1 atomic + versioned-gate supersession scoped to gate-function-body only per slice-011 NEW sub-class N=1, sha256 capture for methodology-changelog, self-application clean at Phase 4)
- [ ] `/drift-check` passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 audit clean: `python -m tools.plugin_manifest_audit --root .` exits 0
- [ ] Existing 29+ BC-1 tests still pass (TF-1 strict-pre-finish picks up regression-guard via existing rows)
- [ ] Self-application check: this slice's own `mission-brief.md` + `design.md`, after the migration ships, no longer triggers BC-PROJ-2 false-positively. The slice's text mentions BC-PROJ-2 positive anchors (`fence`, `code-block`, `llm`) as historical-lesson context AND methodology-vocabulary negative-anchors (`vocabulary`, `meta-discussion`, `defer-with-rationale`, `Dim 9`, `back-sync`, `forward-sync`, `Critic-MISSED`, `aggregated lessons`, `false positive`) — the new negative-anchor filter MUST silence BC-PROJ-2 cleanly. RSAD-1 build-time recursive-self-application sub-mode anticipation: /critique B*/M* fix prose may RE-INTRODUCE or REMOVE anchor substrings into mission-brief + design.md — verify both at design-time (Phase 0 audit) AND at Phase 4 post-build BC-1 self-application audit. Capture result in `build-log.md` Phase 4 with N=9 → N=10 validate-using-your-own-ship ratchet.
