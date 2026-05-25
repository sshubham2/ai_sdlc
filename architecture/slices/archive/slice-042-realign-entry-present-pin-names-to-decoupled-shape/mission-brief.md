# Slice 042: realign-entry-present-pin-names-to-decoupled-shape

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none directly — discharges a consciously-accepted *shipped* identifier over-claim recorded in slice-041 (Deferred / Lessons-for-next-slice: "the strongest standing next-slice candidate")
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-041 decoupled the `_entry_present_in_repo_and_installed`-family methodology-changelog
pins so their bodies now assert **in-repo presence only** (MCFS-1 / ADR-042/043), but the
**37** active test-function names (33 `_entry_present` + **4** `_entry_names_*_in_repo_and_installed`
variants, verified 2026-05-18 — supersedes the slice-041-prose "~33") still carry the
`_and_installed` suffix — a shipped name↔body contradiction.
This slice realigns those identifiers to stop over-claiming, while consciously **not**
touching the frozen-history carve-out (append-only shipped history must not be rewritten).
Identifier-truth class, slice-035 precedent; no R-4 dependency.

## Acceptance criteria

1. All **37** active (non-frozen) `def`s matching `test_\w*_entry_(?:present|names_\w+)_in_repo_and_installed` in `tests/methodology/test_methodology_changelog.py` are renamed to drop the `_and_installed` suffix (resolved per ADR-044: drop exactly `_and_installed` → `_entry_present_in_repo` / `_entry_names_<x>_in_repo`; anchor catches the no-`_sub_` `test_v_0_36_0_entry_names_three_modes_*` variant; never matches the CAD-1 `test_in_repo_and_installed_*_are_content_equal` family).
2. The complete LIVE non-def reference set is realigned to the new shape: 2 in-file comments (`test_methodology_changelog.py:1821`, `:2936`) + 4 sibling test files (`test_critique_agent.py:1426`, `test_methodology_changelog_forward_sync.py:16`, `test_query_design_skill.py:17`, `test_shippability_decoupling_audit.py:57`) + `tools/methodology_changelog_forward_sync.py:58` (live source docstring) + all **69** `shippability.md` occurrences (**32** unique names, 28 rows).
3. The FROZEN carve-out is verifiably **NOT** renamed — defined in design.md/ADR-045 as a **predicate** (`methodology-changelog.md` Validation lines; every `ADR-*.md` except ADR-044/045; `fixtures/archive_backtest_corpus/**`; `slices/archive/**`; historical vault prose `_index.md`/`lessons-learned.md` — `critic-calibration-log.md` carries 0 family refs, not a bucket) and proven untouched by a pre/post inventory snapshot (per-file count + path list byte-identical).
4. Full methodology test suite is green post-rename: pytest collects + passes the renamed functions, and no orphaned `::`-consumer reference (shippability rows, other tests/tools invoking these by name) survives.
5. Identifier-truth holds: repo-wide **active** `_and_installed` family-literal count == **exactly 1** (ADR-044's single documenting example; ADR-045 = 0; all LIVE surfaces = 0); design.md/ADR-045 record the consciously-NOT-renamed FROZEN set as a predicate.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Active fns renamed | `grep -rn "_entry_present_in_repo_and_installed\|_entry_names_.*_in_repo_and_installed" tests/methodology/*.py` → only frozen-history fixtures remain; renamed fns present under new suffix |
| 2 | Pin + refs realigned | grep the v0.53.0 pin fn + the 4 single-occurrence files + `test_methodology_changelog.py:1821` comment → new shape only |
| 3 | Carve-out untouched | pre/post `grep -rn` inventory of `fixtures/archive_backtest_corpus/**`, `archive/**`, changelog `**Validation**:` lines, ADRs → byte-identical count, no rename applied |
| 4 | Suite green | `& $PY -m pytest tests/methodology -q` → all pass, 0 errors/collection failures; `/validate-slice` VAL-1+WS-1+ETC-1 + shippability catalog clean |
| 5 | Identifier-truth | `grep -rn "_and_installed" tests/methodology/*.py` (excluding fixtures) → empty; design.md carve-out section present |

## Must-not-defer

- [ ] Frozen-history carve-out enumeration **before** any rename (getting this wrong rewrites append-only shipped history — the exact reason slice-041 TRI-1 scope-cut this out)
- [ ] Pre/post inventory grep proving the carve-out set is byte-identical (count + paths) after the rename
- [ ] No orphaned `::`-consumer reference: scan `architecture/shippability.md` rows + `tools/**` + other `tests/**` for any call/cite of a renamed fn by old name
- [ ] Full methodology suite green via `/validate-slice` (not raw pytest alone) before finish

## Out of scope

- Any behavior change to the audits or test bodies — this is a pure identifier rename (bodies unchanged; MCFS-1 semantics were already reframed in slice-041)
- Renaming frozen-history occurrences (fixtures corpus, archive, shipped-changelog `**Validation**:` lines, ADRs) — deliberately preserved
- Re-litigating MCFS-1 / the in-repo-only decoupling itself (slice-041 / ADR-042/043 are settled)
- Touching the installed `~/.claude/` forward-sync semantics (slice-041 reframed; not in this slice)

## Dependencies

- Prior slices: [[slice-041-reframe-installed-pin-forward-sync-invariant]] — the decoupling that created the name↔body drift; [[slice-035-rename-status-skill-to-pulse]] — identifier-truth rename precedent (executable vs prose reference buckets, pre/post inventory grep discipline)
- Vault refs: [[decisions/ADR-042]], [[decisions/ADR-043]] (MCFS-1 context), [[methodology-changelog.md#v0.53.0]]
- Risk register: [[risk-register#R-4]] — retired by slice-041; this slice carries no R-4 dependency

## Mid-slice smoke gate

At ~50% of build, after renaming `test_methodology_changelog.py` (37 defs + 2 in-file comments) but before the remaining LIVE set (4 sibling files + `tools/methodology_changelog_forward_sync.py:58` + the 67 `shippability.md` occurrences):
```
& $PY -m pytest tests/methodology/test_methodology_changelog.py -q
& $PY -X utf8 -c "import subprocess,sys; print('residual:', subprocess.run([sys.executable,'-c','pass']))"  # then: grep -rn _and_installed tests/methodology/test_methodology_changelog.py (expect: 0 active, fixtures unaffected)
```
Expected: that file's renamed tests collect + pass; zero active `_and_installed` residual in it; frozen-history fixture counts unchanged. If fails (collection error / orphaned reference / carve-out count drift): STOP, diagnose, don't continue to the other 4 files.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (carve-out enumerated + pre/post grep proven + no orphaned `::`-consumers)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
