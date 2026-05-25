---
id: ADR-060
title: Extend R-15 corpus class-closure backstop scope from tests/methodology/ only to all three test corpora (tests/methodology/ + tests/skills/ + tests/agents/) via shared helper + per-corpus test functions
date: 2026-05-23
slice: slice-062-extend-r15-corpus-class-closure-scope
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-060: Extend R-15 corpus class-closure backstop scope to all test corpora

## Context

slice-056 minted the R-15 corpus class-closure backstop (`tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus`) as the structural mechanism for R-15 part-(b) retirement: a regex-walked scan of `tests/methodology/*.py` for archive-fragile literal-path-RHS substrings, asserting the match-set is a subset of the documented-deferred whitelist. slice-057 discharged R-15 to `retired` after the slice-034 retrofit emptied the whitelist (the M-add-2 whitelist-shrinkage mechanism).

The backstop's covered scope is `tests/methodology/*.py` only. slice-061 (`fix-install-python-detection-and-prompt-fallback`) surfaced N=1 evidence the scope is incomplete:
- `tests/skills/code_review/test_code_review_skill.py:17-18` (shipped by slice-060) carried `_SLICE_060_CODE_REVIEW = _REPO_ROOT / "architecture" / "slices" / "slice-060-add-code-review-skill" / "code-review.md"` — an active-path literal-path-RHS of exactly the R-15 class.
- When slice-060 archived, the literal broke at slice-061's `/build-slice` Step 6 shippability dogfood with the canonical R-15 failure-mode signature ("test silently FAILs because the active path is now an archive path"); slice-061 disposed it as a user-approved deferral and explicitly nominated slice-062 as the structural fix.

The slice-056 backstop did not catch this literal because its `rglob('*.py')` walk is scoped to `tests/methodology/`. The defect class is real (N=1) and the slice-061 reflection nominated extending the backstop's coverage to `tests/skills/**/*.py` + `tests/agents/**/*.py`. R-15 STAYS `retired` — the corpus backstop's class-closure mechanism IS sound for its declared scope; the slice-062 fix widens the scope, not the mechanism.

The slice-061 reflection also coupled this with a second fix: the offending literal at `tests/skills/code_review/test_code_review_skill.py:17-18` MUST be repointed via `_resolve_slice_dir(60)` (the slice-056 helper) — otherwise the new wider-scope assertions FAIL at first run with the same `tests/skills/code_review/...` site they were minted to catch.

## Options considered

1. **In-place body extension** of the existing function `test_no_new_archive_fragile_literals_in_methodology_corpus`: change the function body to iterate over 3 corpus directories; widen docstring; keep the function name unchanged.
   - **Pros**: minimal LOC churn; single test, single failure point.
   - **Cons**: function name `..._in_methodology_corpus` becomes a lie (function scans 3 corpora not 1); walk-proof requires explicit additional assertions (each corpus visited at least once); per-corpus failure diagnosis depends on parsing the unified failure message.

2. **In-place body extension + rename** to `test_no_new_archive_fragile_literals_in_test_corpora`: as option 1 but drop the misleading `_in_methodology_corpus` suffix.
   - **Pros**: accurate function name + single test; minimal LOC growth.
   - **Cons**: rename is a code-surface change auditable by STP-1 Sub-form A (verified at /design-slice empirical scan: the function name is NOT pinned by any test elsewhere, so the rename is safe — but the rename surface itself is governance-cost overhead); walk-proof still requires explicit assertions.

3. **Extract helper `_scan_corpus_for_r15_literals(corpus_dir: Path) -> set[tuple[str, int]]` + add 2 new per-corpus test functions**: existing function becomes a thin wrapper on `tests/methodology/`; NEW `test_no_new_archive_fragile_literals_in_tests_skills_corpus` + `test_no_new_archive_fragile_literals_in_tests_agents_corpus` wrappers; ONE aggregated `test_r15_corpus_whitelist_has_no_orphan_entries` integrity check across all 3 corpora; single shared `_R15_CORPUS_WHITELIST`.
   - **Pros**: walk-proof falls out naturally (pytest collecting + passing each test IS the structural proof the walker visits that corpus); per-corpus failure diagnostics are unambiguous (the failing test name names its corpus); existing function name preserved → no STP-1 Sub-form A surface; each new test is its own TF-1 row; the helper extraction is a faithful refactor (per-line equivalent to the inlined logic).
   - **Cons**: ~20 LOC added vs option 1; introduces one new module-level helper (`_scan_corpus_for_r15_literals`).

4. **Extract helper + 1 aggregated function** iterating over the corpora list: helper extraction as option 3 but replace the existing function with a single `test_no_new_archive_fragile_literals_in_test_corpora` that aggregates matches across all 3 corpora.
   - **Pros**: shared logic factored cleanly; one whitelist; single test; less LOC than option 3.
   - **Cons**: walk-proof still implicit (single test means a broken walker would silently pass if matches happen to be empty in the under-walked corpus); per-corpus diagnostic relies on parsing path prefixes in the unified failure message; same rename surface as option 2.

## Decision

**Option 3 — extract helper + 3 per-corpus test functions + 1 aggregated whitelist-integrity test, shared whitelist.**

Walk-proof is the deciding factor. The walk-proof discipline established by slice-056 M-add-2 (the corpus class-closure backstop is the structural mechanism for R-15 part-(b) retirement) and slice-057's `Discovered` section (which records the per-line vs whole-file regex iteration class as a build-time-reachable gate-caught defect — paraphrased here, not quoted) makes one principle unambiguous: without an explicit walk-proof assertion, an extension that walks the wrong directory would silently pass. Option 3 makes the walk-proof structural (pytest collects 3 test functions; each PASSES if and only if its corpus is walked; the absence of a `tests/skills/` test from the pytest report IS the visible alarm if the test were removed). Options 1, 2, 4 require separately authored walk-proof assertions whose absence would silently lose the structural guarantee.

The shared whitelist (`_R15_CORPUS_WHITELIST: set[tuple[str, int]]`) is preserved because the whitelist is currently empty + remains empty post-slice; partitioning into 3 per-corpus whitelists would introduce 3 module-level constants for no current benefit + complicate the aggregated orphan-check semantics. The aggregated `test_r15_corpus_whitelist_has_no_orphan_entries` replaces the per-function `missing_whitelist` shrinkage check (which was tied to a single corpus and would be incorrect on a per-wrapper basis after extraction).

The offending `tests/skills/code_review/test_code_review_skill.py:17-18` literal is repointed via `_resolve_slice_dir(60)` (the slice-056 helper) INSIDE the test function (lazy resolution), not as a module-level binding. Lazy resolution chosen because:
- Failure surface at test-run-time gives a clear single-test diagnostic vs module-import-time AssertionError that errors the entire module's collection.
- Matches the `_resolve_slice_dir` documented contract: AssertionError is raised on neither-match per slice-056's `test_raises_assertion_with_diagnostic_when_neither_found`, which expects test-time surfacing.
- The existing module-level `_REPO_ROOT` and `_SKILL_MD` bindings stay (they reference NON-archived paths — `skills/code-review/SKILL.md` — so import-time resolution is safe + appropriate for them).

## Consequences

- The R-15 corpus class-closure backstop's covered scope becomes `tests/methodology/**/*.py` + `tests/skills/**/*.py` + `tests/agents/**/*.py` (post-slice-062 ship).
- Future archive-fragile literals authored in `tests/skills/` or `tests/agents/` are caught at the next `/build-slice` Step 6 pytest run with a diagnostic naming the file + line + the canonical mitigation hint ("Use `_resolve_slice_dir(NNN)` from `tests.methodology.conftest`"). Latency: one slice (the test FAILs as soon as the offending file is added).
- R-15 STAYS `retired`. The mechanism that retired R-15 in slice-057 (whitelist-shrinkage on `tests/methodology/`) is now reinforced by analogous wider-scope checks; the part-(b) retirement is not re-opened.
- The Inclusion heuristic fires: a new archive-fragile literal in `tests/skills/**` or `tests/agents/**` was acceptable-yesterday (no gate refused it), refused-today (the new per-corpus tests FAIL). Per the slice-049 / slice-051 / slice-057 / slice-058 / slice-059 N=5 precedent, this warrants a methodology-changelog entry + **5-part PMI-1 atomic version bump** (0.64.0 → 0.65.0; `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` per **PVFS-1** + `~/.claude/ai-sdlc-VERSION` per AVFS-1 + this changelog's installed copy per MCFS-1; mirrors the slice-060 v0.64.0 5-part shape verbatim — slice-060 reflection L50 "B2 PMI-1 4-part vs 5-part VALIDATED") + shippability row.
- ADR-060 **mints no new RULE-ID**: the R-15 corpus backstop is the existing rule, scope widened. Naming-class peer of [[ADR-053]] (extends OSDG-1 member set without minting a new rule), which itself naming-class-peers [[ADR-051]] (mints OSDG-1) and the slice-007 CAD-1 / slice-010 mini-CAD / slice-033 EOL-DRIFT-1 / slice-049 OSDG-1 drift-guard family lineage.
- Existing 5 unrelated tests in `test_resolve_slice_dir.py` are unchanged. No regression on the slice-056 / slice-057 verified behavior.
- The slice-061-deferred test `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060` PASSES at slice-062 mid-slice smoke gate (PRE-repoint: FAILS because the literal points at the archive path; POST-repoint: PASSES because `_resolve_slice_dir(60)` correctly resolves to the archived slice-060 folder).
- Cumulative-scope assertion: post-slice-062, the R-15 corpus class-closure mechanism's wired-into-CI scope matches its stated scope in [[architecture/risk-register.md#R-15]]. The CSP-1 cross-spec parity table holds.
- **NOT promoted to a Critic-prompt dimension** per the slice-037 audit-vs-real-artifact law (N≥9 cumulative): the gate caught the N=1 instance at intended latency (one slice / slice-061 deferral); structural mechanism is the correct response; Critic-prompt promotion would be a recurrence-not-yet-observed over-fit.

## Reversibility

**Cheap.** The change is mechanical: helper extraction is per-line equivalent to the inlined logic; the 3 per-corpus tests are independent and each could be merged back into a single function without semantic loss; the lazy resolution in `test_code_review_skill.py` could be moved back to module-level if a future Python version makes import-time resolution safer; the whitelist structure is unchanged. To revert: re-inline the helper body into the original function, delete the 2 new per-corpus tests + 1 aggregated test, restore the per-function `missing_whitelist` check, restore the module-level `_SLICE_060_CODE_REVIEW` binding. Approx 30 minutes of work; no downstream dependencies. The methodology-changelog v0.65.0 entry + PMI-1 bump would require a separate supersession-via-new-ADR + new version bump — not strictly reversible (changelog is append-only) but the LIVE BEHAVIOR can be reverted cheaply via the code path described.

The reversibility is NOT lower than `cheap` because:
- No external consumers (this is methodology self-test surface).
- No data migrations.
- No contract changes visible outside the test suite.
- The R-15 risk-register annotation can be appended-without-edit per the supersession discipline (no ADR-in-place edit).
