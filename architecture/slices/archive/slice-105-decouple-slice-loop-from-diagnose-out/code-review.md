# Code Review: Slice 105 decouple-slice-loop-from-diagnose-out

**code-Critic reviewed**: slice diff vs default branch (`ec3393...HEAD`, filtered to the 14 in-scope paths)
**Date**: 2026-06-03
**Result**: FINDINGS (1 Minor — advisory; the slice ships clean on all blocking-class checks)

## Summary

A clean, well-sequenced deletion-and-redefinition slice. The seed removal in `_worktree_paths.py` is complete with no dangling `shutil`/`_DERIVED_DIRS`/`seed_derived_dirs` references; `canonical_worktree_path` + `slice_branch_name` are byte-untouched and `branch_workflow_audit.py`'s import of them is intact (no phantom import). All three OSDG-1 SKILL.md surfaces are content-equal with their installed copies. The `/slice` Step 5.5 renumber and the within-section `Step-5→Step-4` cross-ref are coherent. The two new v0.82.0 changelog tests assert exactly what the entry/shippability row contain (verified: all 8 + 4 substrings present; tests green), the catalog row is correctly `| 112 |` (the sequential catalog index, not slice-number 105 — design.md's "Row #105" was loose prose), and the version-sync rename to `_at_v_0_82_0` is complete across all 4 legs + docstring with no orphaned duplicate. Critically, the **seedless-parity smoke gate holds**: the full methodology suite (1387 tests) passes green with `diagnose-out/` AND `graphify-out/` renamed aside — the design's key validation, and the mid-slice gate's failure condition (a hidden second seed consumer) did NOT trigger. PMI-1, INST-1, branch-workflow-audit, R-20-retired, and all three drift tests pass at v0.82.0.

## Changed files (in-scope)

- tools/_worktree_paths.py
- tests/methodology/test_worktree_paths.py
- tests/methodology/test_resolve_slice_dir.py
- tests/methodology/test_bcr_1_backlog_round_trip.py
- tests/methodology/test_methodology_changelog.py
- skills/slice/SKILL.md
- skills/build-slice/SKILL.md
- skills/reflect/SKILL.md
- CLAUDE.md
- methodology-changelog.md
- VERSION
- plugin.yaml
- pyproject.toml
- architecture/slices/slice-105-decouple-slice-loop-from-diagnose-out/build-log.md

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. The must-not-defer items the prior-Critic reviews flagged are all discharged in-code: M-add-2 (the `seed_derived_dirs` import at `test_worktree_paths.py:17`) is removed; B-add-1 (the `.is_file()` guard at `test_resolve_slice_dir.py:77`) is removed; the consume-side `/slice` source-#7 tests (#1–#3) are preserved; `canonical_worktree_path`/`slice_branch_name` are untouched. Full methodology suite collects 1387 with zero import errors.

### Majors

None.

### Minors

#### m1: Stale deleted-test references in two surviving module docstrings (historical-provenance prose, non-load-bearing)

- **Claim under review**: `tests/methodology/test_resolve_slice_dir.py:25` ("Rule references" block) reads `BFRD-1 (slice-056 reproduction: tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant FAILING on master pre-fix…)`; and `tests/methodology/test_skill_parse_helpers.py:3` reads `Slice-074 m4: tests/methodology/test_build_slice_skill_cp_r_step.py + test_build_slice_skill_dirty_tree_resolution.py both define byte-equivalent _branch_state_section helpers`. Both cite a test file this slice **deletes**.
- **Issue**: Per Wiegers (traceability) / Sommerville (requirements-design-code consistency), a docstring that names a now-nonexistent file as a live provenance anchor is mildly stale-by-construction. These are NOT live imports or `is_file()` asserts (the actual import at `test_skill_parse_helpers.py:11` is from the surviving shared `_skill_parse_helpers` module, and `test_resolve_slice_dir.py`'s `_resolve_slice_dir(54)` is genuinely re-exercised at `:85` by `test_resolves_archived_slice_054`), so there is no runtime breakage — these are historical-lineage notes. The slice's own added comment at `test_resolve_slice_dir.py:64` correctly explains the removal, but the OLDER docstring at `:25` was not harmonized to match.
- **Evidence**: Grep for the deleted filenames across `tests/` returns exactly these two docstring lines + the slice's own explanatory comment; no live import/assert references them. Full suite collects 1387 clean.
- **Proposed fix**: Optional (cheap-if-touched). At `test_resolve_slice_dir.py:25`, append a parenthetical "(test deleted at slice-105 / ADR-095; reference retained as BFRD-1 reproduction lineage)" to match the harmonization the slice already applied at `:64`. At `test_skill_parse_helpers.py:3`, similarly note the cp-r module's deletion. Both are documentation hygiene, not a correctness defect — defer if the disposition discipline prefers minimal churn.

## Dimensions checked

- [x] **Unfounded assumptions** — none load-bearing. The reflect/SKILL.md `:59` reworded bullet's claims (dead-write-under-BRANCH-3, gitignored-discarded-at-merge) match ADR-095's body. The build-slice `:67` note's "regenerate with `$PY -m graphify code .`" claim is consistent with the retained regenerate-on-demand pattern. (Out-of-scope context: ADR-094:24 cites the missing-graph non-fatal test at `tests/methodology/test_slice_queue_output.py` but it actually lives at `tests/skills/slice/test_slice_queue_output.py` — a path-citation drift in ADR prose, NOT in the 14-file code diff; the test itself passes, so the behavior the design relied on is real. ADRs are design-meta, not code-review scope — flagged as context only.)
- [x] **Missing edge cases** — none. Seedless-parity (the "empty" / "derived-dir absent" case) is the slice's core edge case and is **executed**: methodology suite 1387 green with `diagnose-out/`+`graphify-out/` renamed aside (and dirs restored). The graceful-degrade-on-absent-backlog case is moot post-ADR-095 (no `/reflect` code path touches `backlog.md`), and grep confirms no orphaned "no-op clean on absent backlog.md" prose survives in reflect/SKILL.md. No CRLF/LF byte-compare introduced (EOL-DRIFT-1 N/A — pure deletions + version-string edits).
- [x] **Over-engineering** — none. The slice removes a single-consumer helper (`seed_derived_dirs`) and a dead write; this is the opposite of speculative generality (Fowler). The retained `_worktree_paths.py` is a thin path/branch helper with no dead parameters introduced.
- [x] **Under-engineering** — none. Every AC has a delivering code element: AC1 (no live read) = test deletion + seedless-parity green; AC2 (seed gone) = `seed_derived_dirs`/`_DERIVED_DIRS`/`import shutil` deleted + both SKILL.md seed sites removed; AC3 (consume-only redefinition) = reflect bullet + CLAUDE.md + ADR-095 + changelog + shippability row; AC4 (consume side intact) = Tests #1–#3 preserved (verified the only surviving `def test_`); AC5 (drift green) = PMI-1/INST-1/OSDG-1 all pass at v0.82.0. The slice's own 16+ Step-6 audits pre-satisfy: PMI-1 clean, INST-1 clean, OSDG-1 (3 surfaces) clean, R-20-retired pin green, branch-workflow-audit green.
- [x] **Contract gaps** — none. No new function signatures. `_worktree_paths.py`'s public surface shrinks by one function; the sole importer (`branch_workflow_audit.py:61`) imports only the three surviving symbols (`_SLICE_FOLDER_RE`, `canonical_worktree_path`, `slice_branch_name`) — no broken contract dependency, no phantom import.
- [x] **Security** — none. Methodology-internal markdown + version-string + Python-deletion slice; no new auth, input boundary, secret, injection vector, or data-exposure path. The deleted `shutil.copytree` removes filesystem-write surface (net security-neutral-to-positive).
- [x] **Drift from vault** — none material. Code matches design.md "Components touched" exactly (the `:94-114`/`:65`/`:48` deletions in `_worktree_paths.py`; the three build-slice removals; the reflect bullet; the slice renumber). The shippability row number is `| 112 |` (sequential catalog index), not design.md's loose "Row #105" — the test correctly tracks the actual `| 112 |`; this is design-prose imprecision, not code drift. MEPD-1 obligation honored: the v0.82.0 changelog entry, version cascade (VERSION/plugin.yaml/pyproject all → 0.82.0), and the INCLUDE posture the entry declares are all implemented in the diff (no claimed-but-unbumped surface). No scope creep: the `/slice` consume-side source-#7 (out-of-scope to remove) is preserved.
- [x] **Web-known issues** — none by construction. The diff introduces zero new API/SDK/framework calls — it deletes a `shutil.copytree` call, edits markdown prose, and bumps version literals. No post-cutoff platform change, quota, or deprecation surface exists to check. (Not skipped for tool-unavailability; skipped because the artifact class is deletion + prose with no new external dependency.)
- [x] **Cross-cutting conformance** — none. RSAD-1: the slice survives its own discipline — OSDG-1 content-equality holds for all three edited SKILL.md (verified byte-equal modulo EOL against installed copies), and PMI-1/INST-1 pass at v0.82.0. APED-1: the slice modifies no audit parse-rule/regex (it edits test assertions and prose only) — N/A. The two new v0.82.0 changelog tests were **executed** (20-test run green, plus standalone confirmation) and the row-scoping logic (`row_end = find("\n| ")` → -1 fallback to `[row_start:+8000]`) correctly captures the 2307-char last row. Reverse-dependency completeness (the prior reviews' miss-class) is fully discharged: all reverse-readers of the deleted artifacts (`test_worktree_paths.py:17` import, `test_resolve_slice_dir.py:77` `.is_file()` guard, the `_reflect_step2_section` helper + Tests #4–#8) were removed in the same batch; full methodology collection is 1387 clean with no `ImportError`.

## Disposition (main-thread, post-review)

- **m1 → ADDRESSED** at slice-105 (not deferred): both stale-provenance docstrings harmonized with the project's preserve-and-annotate style (the same style the slice already used at `test_resolve_slice_dir.py:64` and in the risk-register R-20 / shippability row rewrites) — the historical reference is retained and a "(deleted at slice-105 / ADR-094|095)" annotation added. Reverse-dependency completeness extended to the documentation surface. See build-log Events.
- The out-of-scope ADR-094:24 path-citation drift (`test_slice_queue_output.py` lives under `tests/skills/slice/`, not `tests/methodology/`) is **noted for /reflect** — ADRs are append-only (cannot edit in place); the cited test passes, so behavior is real. A future ADR/erratum or the /reflect Discovered section can record it; not actioned here (append-only ADR discipline).
