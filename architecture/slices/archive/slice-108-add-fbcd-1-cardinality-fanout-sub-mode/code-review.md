# Code Review: Slice 108 add-fbcd-1-cardinality-fanout-sub-mode

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths), base `a01e0bbd14f2bd3609dc874bec9f0d74c7a160d1`
**Date**: 2026-06-03
**Result**: FINDINGS (0 Blockers, 0 Majors, 2 Minors — advisory)

## Summary
A tightly-scoped, well-executed methodology-prose + version-cascade slice. The FBCD-1 sub-mode (c) prose is correctly inserted and indented, the intro count is accurate above exactly three sub-mode bullets, the `(1)→(1b)→(2)→(3)→(4)` closing-instruction numbering is well-formed, the full PMI-1 0.82.0→0.83.0 cascade landed on all surfaces (VERSION / plugin.yaml / pyproject.toml / installed ai-sdlc-VERSION / dist `ai-sdlc-tools` / changelog header), CAD-1 is byte-equal, and both new tests are non-vacuous (mutation-confirmed). The slice's own RSAD-1 sub-mode-(c) self-application is clean — every legitimate "two sub-modes / not three" survivor is either a historical changelog/ADR entry (append-only) or an OTHER-rule reference, correctly left unswept. Only two cosmetic minors.

## Changed files (in-scope)
- VERSION
- plugin.yaml
- pyproject.toml
- agents/critique.md
- methodology-changelog.md
- tests/methodology/test_critique_agent.py
- tests/methodology/test_methodology_changelog.py
- architecture/slices/slice-108-add-fbcd-1-cardinality-fanout-sub-mode/build-log.md

## Findings

### Blockers (advisory in v1)

None. The five attack-focus axes were executed (not reasoned):

1. **Version-cascade correctness** — `git grep "0\.82\.0"` across all diff'd files: every survivor is a legitimate historical reference (`methodology-changelog.md:39` records the bump "0.82.0 → 0.83.0"; `:49/:51` are the persisted v0.82.0 historical entry; `test_methodology_changelog.py:5512` "historical v0.82.0 entry persists", `:5540` "CCC-1 v1.1 / v0.82.0 precedent", and `:5754-5804` the v0.82.0 entry-pin test). **Zero stale version legs.** The renamed `test_version_files_synchronized_at_v_0_83_0` has all 4 leg asserts at 0.83.0 (VERSION / plugin.yaml / pyproject / `## v0.83.0` header), docstring `0.82.0 → 0.83.0 (slice-108)`, precedent chain `…/099/105/108`. Ran the renamed test + the v0.83.0 entry-pin test + the both-sub-modes test + the cardinality-fanout test: **4 passed**. Full module run: **193 passed**.
2. **Test non-vacuity** — mutation sim confirms the regression test goes RED if either the sub-mode (c) heading OR the slice-091 boundary clause is deleted; both anchors are unique (`new runtime behavior not yet a static literal` appears once repo-wide). The v0.83.0 entry-pin's `_extract_version_body(in_repo, "0.83.0")` scopes between `## v0.83.0` and `## v0.82.0`; the substantive phrase `Counted-set cardinality fan-out` occurs only inside that body → genuinely discriminating, not tautological.
3. **RSAD-1 self-application** — the slice's own sub-mode (c) is clean. Of all repo-wide "two sub-modes / not three" hits: `test_critique_agent.py:703` is RPCD-1's own test ("loses coverage of the N=3" — RPCD-1 has 3 sub-modes; correctly NOT a FBCD-1 claim); changelog `:1003/:1028` and ADR-022 are append-only historical entries; the in-scope `test_v_0_38_0_fbcd_1_names_both_sub_modes` pins the *historical v0.38.0 changelog entry body* (asserts the names of (a)+(b), not a "two" count) and correctly stays green untouched. The two live stale sites (test_critique_agent.py L840 comment + `_names_both_sub_modes` docstring) WERE swept. `_lists_twelve_sub_clauses` passes (sub-MODE add ≠ sub-CLAUSE add).
4. **Markdown well-formedness** — sub-mode (c) bullet at `agents/critique.md:197` is `  - **Sub-mode (c)…` (2-space indent matching (a)/(b)); FBCD-1 body contains exactly `[a, b, c]`; body-bound anchors intact; intro (L194) reads "Three sub-modes — two on the temporal axis ((a)/(b)) plus one on the orthogonal SCOPE axis ((c)):"; closing instruction (L199) carries `(1)(1b)(2)(3)(4)` in ascending order. CAD-1 clean (sha256 6a1a0d35, in-repo ≡ installed).
5. **Drift vs design.md** — built code matches design's "What's new" / "Version-bump cascade" / "Self-application sweep" claims on every checked point.

### Majors

None.

### Minors

#### m1: Stale "not three, given FBCD-1's N=10…evidence base" prose in the historical v0.38.0 changelog Validation block is now globally misleading (but correctly NOT edited)
- **Claim under review**: `methodology-changelog.md:1028` — `…_names_both_sub_modes` (AC #1 … two sub-modes, not three, given FBCD-1's N=10-cumulative…evidence base); and `:1003` "FBCD-1's two sub-modes match the RPCD-1 / EPGD-1 / SCPD-1 multi-sub-mode codification template".
- **Issue**: These now-falsified count-claims sit in the **append-only v0.38.0 historical entry**, so the slice was *correct* not to edit them (append-only changelog discipline / SUP-1). Logged only to make the disposition explicit: the slice's RSAD-1 sweep deliberately scoped to *live* surfaces and left historical entries verbatim. A future reader greping "not three" will hit `:1028` and must understand it is frozen v0.38.0-era text, not a live obligation. The v0.83.0 entry is the canonical record of the 2→3 change.
- **Evidence**: `:1028` is inside the v0.38.0 entry; `test_v_0_38_0_fbcd_1_names_both_sub_modes` pins it as immutable.
- **Proposed fix**: None to the code (editing it would violate append-only). The existing `FBCD-1 v1.1` + `versioned refinement of the existing FBCD-1 rule ([[ADR-022]])` language already conveys the supersession. Accept as-is.

#### m2: `_names_both_sub_modes` test function name is now a slight misnomer (FBCD-1 has three sub-modes) but renaming is correctly avoided
- **Claim under review**: `tests/methodology/test_critique_agent.py:892` `def test_critique_dim_9_fix_block_completeness_names_both_sub_modes()` — the name says "both" (=two) but FBCD-1 now has three sub-modes.
- **Issue**: The function legitimately pins ONLY the temporal pair (a)/(b) — its docstring was correctly updated (L899-904) to say so explicitly. Renaming to `_names_temporal_sub_modes` would trip SCPD-1 (the name is cited in shippability row #24 and the v0.38.0 Validation block). The design (§Self-application sweep #2) explicitly reasoned this through and chose to leave the name + asserts unchanged. Correct decision; logged only because the name/semantics mismatch is a readability papercut.
- **Evidence**: design.md L78 documents the deliberate non-rename; the docstring update at L899-904 disambiguates; `_names_cardinality_fanout_sub_mode` carries the (c) pin.
- **Proposed fix**: None — the docstring disambiguation is the right mitigation under the SCPD-1 constraint. Accept as-is.

## Dimensions checked
- [x] Unfounded assumptions — none. The new regression test's docstring example matches the actual asserted substrings, which match the live critique.md L197 prose verbatim. No phantom imports (`CRITIQUE`, `read_file`, `_extract_version_body` all pre-exist and resolve).
- [x] Missing edge cases — none material. No byte-equality `==` compares on `.md` content (new asserts use `in`, EOL-safe per EOL-DRIFT-1). The `_extract_version_body` predecessor-boundary (0.83.0→0.82.0) is exercised and the v0.82.0 boundary entry exists.
- [x] Over-engineering — none. No new abstraction, flag, or module; pure prose + literal-sweep + two thin pin tests.
- [x] Under-engineering — none. Every AC has a delivering code element (AC1→critique.md L197+L199; AC2→CAD-1 exit 0; AC3→v0.83.0 entry + full cascade; AC4→`_names_cardinality_fanout_sub_mode` mutation-confirmed; AC5→193-module-pass + `_lists_twelve_sub_clauses` green).
- [x] Contract gaps — none. New test functions carry contract docstrings (defect-class + rule-reference). No public signatures changed.
- [x] Security — none; no auth/input/injection/secret/data-ownership surface. Pure methodology-internal markdown + test literals.
- [x] Drift from vault — none. Built code matches design's "What's new" / "Version-bump cascade" / "Self-application sweep" on every point; MEPD-1 versioned posture implemented (all surfaces bumped + `Rule reference` line present); build-log "Design deviations: None" corroborated.
- [x] Web-known issues — not applicable; no external API/SDK/framework/library-version/platform-specific pattern in this prose+version diff.
- [x] Cross-cutting conformance — clean. RSAD-1 (slice survives its own sub-mode (c)) confirmed; APED-1 (renamed version-sync + entry-pin + regression tests executed GREEN, not reasoned); EOL-DRIFT-1 (no new byte-equality `.md` compare); CAD-1 re-established (sha256 6a1a0d35); `_lists_twelve_sub_clauses` untripped (sub-MODE ≠ sub-CLAUSE).
