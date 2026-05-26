# Reflection: Slice 070 fix-psq-1-blast-radius-dict-leak

**Date**: 2026-05-26
**Shipped**: YES-WITH-DEFERRALS

**Closes:** SC-027

## Validated

- **Defect class identified empirically by /critique B1**: graphify blast-radius JSON CLI emits `{id, label, type:"", path:""}` with `path` STRUCTURALLY empty; the `name` key is absent from the schema entirely; only `id` is universally populated. Empirically re-verified at /build-slice: `python -c "..."` reports key frequencies `{label:2791, file_type:2791, source_file:2791, source_location:2791, community:2791, id:2791}` across all 2791 nodes. Design.md's described schema matches production reality.
- **`_build_id_to_path_map` id→source_file lookup strategy resolves correctly against real data** — `slice_queue_writer.py` → `tools/slice_queue_writer.py` (relative form when build cwd matches worktree). Confirmed at /build-slice Phase D + /validate-slice AC3 integration test.
- **6 of 6 tests PASS** at /validate-slice (5 unit + 1 integration); transition WRITTEN-FAILING/PENDING → PASSING locked in.
- **Live committed `architecture/slice-queue.md` Blast-radius cells contain only path-shaped tokens post-fix** — AC3 positive-shape regex against backtick-quoted tokens passes; no `{`/`'`/`:` dict-string fragments anywhere. SC-027 defect class STRUCTURALLY RETIRED on the live artifact.
- **VAL-1 Layer A (secrets) clean + Layer B (deps) clean** — no committed credentials; no hallucinated imports.
- **Shippability catalog regression check 70/70 PASS** — zero past-slice critical-paths regressed by this slice's changes.
- **Full pytest baseline preserved at 950 passed** (was 944 pre-slice-070; +6 new tests = exact expected).
- **TPHD-1 sub-mode (a) cross-doc harmonization fix-block discipline** caught the meta-Critic M-add-1/2 stale-precedence drift correctly in /critique-review fix-block; post-sweep grep returned 0 matches. Discipline mechanism works.

## Corrected

- **AC#3 regex literal** (`tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295` + mission-brief AC#3 + design.md TF-1 supplement + shippability.md row #70) → original /critique-time `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$` widened to `^(?:[^\s\`]*[/\\][^\s\`]+|[^\s\`]*\.[A-Za-z0-9]{1,8}|\.[A-Za-z][A-Za-z0-9_.-]*)$`. Empirical Builder-discovery at /build-slice Phase D: the original regex rejected `.gitignore` (a legitimate dotfile in `rename-architecture-to-sdlc`'s `hint_files`). Contract (positive-shape check) unchanged; literal widened to accept dotfile class. Harmonized across all 4 surfaces in same fix-block per TPHD-1 sub-mode (a).
- **Stale test function name anchors in mission-brief.md L18 (AC#1) + L20 (AC#3)** → swept to current names (`test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup` + `test_committed_slice_queue_md_blast_radius_cells_contain_only_path_shaped_tokens`). Original /repro placeholder names persisted through /critique fix-block; caught at /build-slice via inspection. 5th cumulative recurrence of TPHD-1 sub-mode (a) cross-doc harmonization gap (slice-062/064/067/070-meta/070-build).
- **build-log.md provenance correction** (per /code-review m3 ACCEPTED-FIXED-at-/reflect) → original "not a defect this slice introduced" framing on the abs/rel-path duplication was inaccurate; `_build_id_to_path_map` IS slice-070 code, so the defect class IS introduced by this slice. Corrected in build-log Events + Design deviations table.

## Discovered

- **N+1 first-governed-slice catch on BRANCH-2 + vault-in-git intersection** (slice-070 is FIRST post-vault-tracking slice): the slice's pre-build pipeline artifacts (mission-brief, design, critique, critique-review, repro test, shippability row) created on master tree by `/slice → /critique-review` NOW show up as tracked dirty state, tripping BRANCH-2 prereq rule 4 "STOP if dirty". User-ratified the switch-commit-switch-worktree pattern (option 1) — this is now the new canonical pattern. **Impact**: BRANCH-2 SKILL.md needs to codify this pattern for future slices; otherwise every post-vault-in-git slice will re-encounter the same prereq surprise.
- **Worktree absolute-path duplication in Blast-radius cells** (per /code-review M1): `_build_id_to_path_map`'s `.relative_to(repo_root)` fallback keeps full absolute paths when graph.json was built from a different cwd than the worktree. Both forms pass AC3's regex; substantive runtime impact bounded by today's single-source-graphify-out (intersection still resolves via relative form). Latent silent-corruption surface for `compute_parallel_safety` overlap detection under multi-graph scenarios. **Impact**: defect class introduced by slice-070; deferred to slice-071+ bundle. **Risk-register addition**: see R-X below.
- **`graphify-out/` + `diagnose-out/` cp-r tax continues post-slice-069** (N=5 cumulative across slice-066/067/068/069/070): slice-069 retired the `architecture/` class via vault-in-git, but `graphify-out/` + `diagnose-out/` remain gitignored. Every BRANCH-2 worktree slice pays the cp -r tax. **Impact**: slice-071+ candidate to un-gitignore both OR codify the cp -r tax in BRANCH-2 SKILL.md.
- **`_is_path_shaped` vs AC#3 regex contract drift** (per /code-review M2): two functions claim to encode the "path-shaped" contract but disagree on dotfiles + uppercase extensions + non-canonical-extension classes. Today masked because the PRIMARY id-lookup path bypasses `_is_path_shaped`; surfaces if a future graphify schema emits `.gitignore` via the dict-own-`path` key. **Impact**: bundle-cleanup candidate; single-source-of-truth refactor extracting regex into module constant.
- **`lru_cache` returns shared-by-reference mutable dict** (per /code-review M4): no caller mutates today; future optimization would poison the cache. Brittle test isolation if any test invokes unpatched.
- **AC#3 live-artifact test fails on routine degraded `\`unknown\`` cells** (per /code-review M5): the slice-067 design AC4-(b)/(c) explicitly support the degraded state where blast cell renders `\`unknown\``. The AC#3 regex doesn't except `\`unknown\``. **Impact**: latent test fragility; bundle-cleanup candidate (3-LOC test amendment).
- **`subprocess.run` patch scope broader than intended** (per /code-review M6): `patch.object(subprocess, "run", ...)` patches the global module attribute; idiomatic isolation is `patch("tools.slice_queue_writer.subprocess.run", ...)`. Pattern propagates by example.
- **Code-Critic stack continues to deliver high-signal reviews** (N=7 cumulative slice-063→070): code-Critic surfaces real cross-contract drift + defense-in-depth + cache-poisoning concerns the design-Critic stack structurally cannot reach. M1 in particular is sharply argued. Voluntary-restraint discipline holds (advisory only in v1) but the bundle backlog now stands at 30 findings — slice-071+ "bundle-066-to-070-code-critic-cleanup" has crossed the "explicit /slice scope decision" threshold per slice-069 aggregated lessons.
- **Backslash-stripping watch-list bullet from slice-069** re-validated NEGATIVE this slice: no bash-heredoc Python source with backslash-in-regex was authored (regex written in test file source code directly, not via heredoc). /critic-calibrate watch-list N=1 status unchanged.

## Deferred

- **Bundle-cleanup follow-on slice (`bundle-066-to-070-code-critic-cleanup`)** — accumulated code-Critic advisories now at **30 findings** (slice-066:6 + slice-067:1 + slice-068:4 + slice-069:8 + slice-070:11). Strongly recommend nominating as next slice candidate; already #1 in slice-queue.md ranking. Lands in: next `/slice`.
- **`_build_id_to_path_map` absolute-path normalization** (code-review M1): bundle-cleanup candidate (try alternate prefix-stripping against known-repo-parent variants before `as_posix()` fallback). Lands in: bundle-cleanup slice.
- **`_is_path_shaped` single-source-of-truth refactor** (code-review M2): extract regex into module constant `_PATH_SHAPED_RE`, import in test. Lands in: bundle-cleanup slice.
- **PRIMARY id-lookup defense-in-depth filter** (code-review M3): apply `_is_path_shaped` filter to map lookup return value. Lands in: bundle-cleanup slice.
- **`lru_cache` → `MappingProxyType` return** (code-review M4): return read-only view to prevent cache poisoning. Lands in: bundle-cleanup slice.
- **AC#3 `\`unknown\`` skip** (code-review M5): test-side amendment to skip the documented sentinel. Lands in: bundle-cleanup slice.
- **`patch("tools.slice_queue_writer.subprocess.run", ...)` migration** (code-review M6): 5 occurrences in tests/bugs. Lands in: bundle-cleanup slice.
- **`graphify-out/` + `diagnose-out/` cp-r tax codification** (slice-068/069 N=5 cumulative): either un-gitignore both directories per ADR-066 precedent OR codify the cp-r requirement in BRANCH-2 SKILL.md. Lands in: separate slice candidate.
- **BRANCH-2 + vault-in-git transition pattern codification**: the switch-commit-switch-worktree pattern user-ratified at /build-slice prereq needs codification in BRANCH-2 SKILL.md. Lands in: separate slice candidate.
- **BC-1 BC-GLOBAL-2 false-positive class** (slice-069 + slice-070 N=2 cumulative): rule fires on prose-discussion-of-git-commands rather than code-automation. Needs negative-anchor filtering. Lands in: BC-1 calibration or rule-revision slice.
- **BC-1 BC-PROJ-11 scope-mismatch**: rule targets INSTALL.md/README.md hard-coded version literals but trigger fires on any version-literal in any changed file. Needs `applies_to` filename glob tightening. Lands in: BC-1 calibration slice.
- **LINT-MOCK seam-allowlist for internal injection seams**: `_build_id_to_path_map` is a documented test-injection seam mirroring `blast_resolver`'s pattern; LINT-MOCK has no `--seam-allowlist` for in-test mock targets. Lands in: bundle-cleanup slice candidate.

## Critic calibration

Per **TRI-1** (`methodology-changelog.md` v0.11.0):

### Dual-Critic stack (design-Critic + meta-Critic) — 15 findings

- **B1** (path→name→id produces non-path output): **VALIDATED** — first-Critic empirically executed graphify and discovered the wrong-output class; disposition ACCEPTED-FIXED via redesigned id-lookup; Builder verified the new strategy produces correct paths against live data. Textbook APED-1 catch.
- **B2** (test mocks fictional shape): **VALIDATED** — disposition ACCEPTED-FIXED via mock-fixture rewrite; reality confirmed the fictional shape was used (the /repro test originally asserted `"path": "tools/foo.py"` which graphify never emits in this repo).
- **M1** (AC3 weak-proxy regex): **VALIDATED** — disposition ACCEPTED-FIXED via positive-shape regex; reality confirmed the original regex would have allowed opaque IDs to pass. The DEVIATION widening at /build-slice further validated the positive-shape direction (dotfiles needed to be accepted too).
- **M2** (R-X2 inverted framing): **VALIDATED** — disposition ACCEPTED-FIXED via rewrite; reality confirmed the inverted framing (silent-PRODUCTION not silent-drop is the actual risk).
- **M3** (R-X3 incomplete enumeration): **VALIDATED** — disposition ACCEPTED-FIXED via collapse into M1's positive-shape regex.
- **M4** (AC#2 mis-aligned with actual graphify shape): **VALIDATED** — disposition ACCEPTED-FIXED via 4-shape enumeration including the actual current shape.
- **M5** (ADR-064 citation drift): **VALIDATED** — disposition ACCEPTED-FIXED via citation rewording; reality (re-reading ADR-064) confirmed the original "multi-session shared visibility premise" framing was post-hoc not in the ADR itself.
- **M6** (LOC count drift): **VALIDATED** — disposition ACCEPTED-FIXED via excision; reality confirmed the original counts were imprecise (actual delta closer to 35-40 LOC after the redesign).
- **m1** (smoke gate too narrow): **VALIDATED** — disposition ACCEPTED-FIXED via broadening to full module; reality at /build-slice confirmed that smoke-gating the full module + AC3 integration would have caught the regex-widening DEVIATION earlier.
- **m2** (slice-069 wiring matrix cross-ref unverified): **VALIDATED** — disposition ACCEPTED-FIXED via spot-check; reality confirmed the reference was accurate.
- **m3** (BCR-1 sentinel multi-mention double-trigger): **FALSE-ALARM** — disposition OVERRIDDEN with rationale from /reflect SKILL.md L59 prose. Reality at /reflect time: BCR-1 appended exactly ONE `**Addressed:**` line for SC-027 (the multi-mention did NOT double-trigger). The Critic over-reached on this finding; the override was correct.
- **m4** (shippability row placeholder): **VALIDATED** — disposition ACCEPTED-FIXED via clause excision.
- **M-add-1** (meta-Critic missed-finding on design.md L66 stale precedence): **VALIDATED** — disposition ACCEPTED-FIXED via rewrite in /critique-review fix-block; reality post-sweep confirmed 0 residual stale-precedence references.
- **M-add-2** (meta-Critic missed-finding on mission-brief.md L51 stale precedence): **VALIDATED** — same disposition + outcome as M-add-1.
- **M-add-3** (meta-Critic TPHD-1 N=4 cumulative recurrence flag): **VALIDATED** — disposition ACCEPTED-FIXED; reality at /build-slice surfaced ANOTHER 2 stale references (mission-brief L18 + L20 test function names) confirming the pattern recurs even after the meta-Critic fix-block. **N=5 cumulative** as of this slice.

### Code-Critic stack (CRSI-1 v1 walking-skeleton) — 11 findings

All 11 findings (6 Majors + 5 Minors) are NOT-YET (deferred to slice-071+ bundle); will re-score in the bundle's reflection.

- **M1** (worktree absolute-path silent-corruption surface): **NOT-YET** — disposition DEFERRED. Builder partially disputes the framing (today's runtime impact bounded) but accepts the latent fragility. Re-score at bundle-cleanup slice.
- **M2** (`_is_path_shaped` vs AC#3 contract drift): **NOT-YET** — DEFERRED.
- **M3** (PRIMARY id-lookup unfiltered): **NOT-YET** — DEFERRED.
- **M4** (lru_cache shared-mutable foot-gun): **NOT-YET** — DEFERRED.
- **M5** (`\`unknown\`` AC#3 fragility): **NOT-YET** — DEFERRED.
- **M6** (subprocess.run patch scope): **NOT-YET** — DEFERRED.
- **m1** (cache_clear never called): **NOT-YET** — DEFERRED.
- **m2** (`--from` fallback untested): **NOT-YET** — DEFERRED.
- **m3** (build-log honesty): **VALIDATED** — disposition ACCEPTED-FIXED-AT-/reflect; correction applied at start of /reflect.
- **m4** (eager id-map build): **NOT-YET** — DEFERRED.
- **m5** (forward-compat tuple as magic constant): **NOT-YET** — DEFERRED.

### Missed by Critic (across all 3 Critics)

1. **AC#3 regex blind-spot on `.gitignore`**: design-Critic + meta-Critic + code-Critic all reviewed the AC#3 regex literal at /critique time + post-meta-fix-block; none flagged that `.gitignore` (a legitimate dotfile in `rename-architecture-to-sdlc`'s hint_files) would FAIL the regex. Surfaced at /build-slice Phase D via empirical execution. **Pattern**: design-Critic + meta-Critic structurally cannot anticipate regex blind-spots on actual rendered cell content without empirical execution. Aligns with slice-069 aggregated lesson "methodology-revision slices that mint a new mechanism have a structural N+1 first-governed-slice catch surface at the slice's own /code-review hop". **/critic-calibrate watch-list N=1**: design-Critic dimension on "empirical-execution of any minted regex/parse rule against actual data" before declaring done.

2. **BRANCH-2 + vault-in-git transition prereq trip-up**: design-Critic + meta-Critic + code-Critic all missed that slice-070 is the FIRST post-vault-in-git slice and would trip BRANCH-2's "STOP if dirty" prereq. Surfaced at /build-slice prereq check. **Pattern**: cross-cutting methodology-interaction blind-spot — the design-Critic stack reviews mission-brief/design.md/ADRs in isolation; doesn't structurally check "does this slice interact with a recent methodology rule in a way that triggers a known prereq?". /critic-calibrate watch-list N=1.

3. **Worktree absolute-path duplication** (caught by code-Critic M1 but not by design-Critic stack): only the code-Critic — by reading the regenerated slice-queue.md content — caught the abs/rel path duplication. Design-Critic stack reviewed `_build_id_to_path_map`'s `.relative_to() / as_posix()` logic without spotting the multi-prefix scenario. **Pattern**: the design-Critic stack's `_is_path_shaped` review naturally focused on filter-correctness; the multi-prefix-coexistence scenario only surfaces at empirical-execution-against-cross-cwd-graph time. Consistent with #1 above.

4. **AC#3 `\`unknown\`` cell fragility** (caught by code-Critic M5): all 3 Critics + Builder missed that `_format_entry` renders `\`unknown\`` for empty blast cells AND the AC#3 regex doesn't except `\`unknown\``. Latent failure mode for routine degraded states.

5. **lru_cache shared-mutable foot-gun** (caught by code-Critic M4): design-Critic + meta-Critic reviewed the `_build_id_to_path_map` design including the lru_cache choice; neither flagged the shared-by-reference return-value foot-gun for future mutating callers. **Pattern**: lru_cache + mutable-return is a textbook Python idiom risk; should be on the code-Critic's checklist explicitly (already there via Dimension 9; the design-Critic stack reasonably stays out of low-level Python idiom space).

6. **subprocess.run patching scope** (caught by code-Critic M6): test-design isolation pattern — neither design-Critic nor meta-Critic reviews mocking-scope idioms at /critique time (no test code exists yet). Code-Critic catches at /code-review when actual test source is in scope. Working as designed.

**Pattern**: code-Critic surfaces real Python-idiom / test-design / cross-document-consistency concerns that the dual-Critic stack structurally cannot reach. 3-Critic stack complementarity continues to validate at **N=7 cumulative slice-063→070** (slice-069 reflection projected N=6; slice-070 extends).

## Lessons for next slice

1. **The bundle-cleanup slice is structurally overdue.** 30 advisory findings across 5 slices is past the slice-069-projected "explicit /slice scope decision" threshold. Recommend running it as slice-071. Worth a careful /slice scope-check (LARGE effort; may need split-slice between code-quality refactors vs spec-prose corrections).
2. **AC#3 regex blind-spot on `.gitignore` is a /critic-calibrate signal**: any future slice minting a parse-rule / regex / glob pattern should empirically execute it against actual production data BEFORE declaring done. APED-1 already addresses audit-parse-rules; this lesson extends APED-1 to regex/glob/pathspec rules more broadly. Consider promoting if a 2nd instance recurs.
3. **TPHD-1 sub-mode (a) cross-doc harmonization gap is N=5 cumulative** — the pattern is now structural. The meta-Critic catches this consistently. For /critic-calibrate next-run: instruct first-Critic to perform a stale-anchor sweep AFTER drafting fix-block dispositions, BEFORE finalizing the critique (per slice-067 M-add-3 candidate, slice-070 meta-Critic M-add-3 candidate). Threshold may have been crossed.
4. **Switch-commit-switch-worktree pattern for vault-in-git pre-build artifacts is now the canonical post-slice-069 sequence** — BRANCH-2 SKILL.md should codify it. Future post-vault-in-git slices will re-encounter the same prereq surprise otherwise.
5. **The `graphify-out/` + `diagnose-out/` cp-r tax is a stable N=5 recurrence** — un-gitignoring both (slice-069 vault-in-git pattern) is now structurally justifiable. The slice's own diagnose-out edit (BCR-1 round-trip) had to be replicated manually in main tree, which is an audit-grade smell.
6. **Code-Critic stack continues to be the highest-signal Critic surface for slices touching `tools/*.py` code**. Don't collapse it. The N=7 cumulative complementarity proof is now strong.
7. **Builder fix-block prose-honesty discipline**: code-Critic m3 caught "not a defect this slice introduced" framing on slice-070's own code. Builder will tighten future build-log dispositions to credit defect provenance accurately, even when deferring.

## Vault updates made (thin vault — small list)

- `architecture/slices/slice-070-fix-psq-1-blast-radius-dict-leak/build-log.md` — provenance correction per /code-review m3 ACCEPTED-FIXED-at-/reflect (2 prose corrections)
- `diagnose-out/backlog.md` (main tree + worktree) — BCR-1 round-trip Addressed line for SC-027 appended after Evidence sub-list, before SC-028 header
- `architecture/lessons-learned.md` — Slice 070 chronological entry appended (next step)
- `architecture/shippability.md` — row #70 already present (added by /repro Step 5; regex literal updated per /build-slice DEVIATION)
- `architecture/slice-queue.md` — regenerated post-fix at /build-slice Phase C; Blast-radius cells path-shape clean
- `architecture/risk-register.md` — no new risks added (the latent abs/rel-path silent-corruption surface from code-review M1 is bounded by today's runtime; deferred to bundle-cleanup rather than risk-tracked separately)
- `architecture/slices/_index.md` — refreshed at auto-archive step (next)
- `architecture/slices/archive/_index.md` — appended at auto-archive step (next)

No methodology-changelog entry (MEPD-1 EXCLUDE confirmed); no PMI-1 bump; no ADR; no SKILL.md edit; no agents/*.md edit. Voluntary-restraint discipline N=11 cumulative (slice-037/046/050/052/055/056/057/061/065/070).
