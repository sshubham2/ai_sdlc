# Slice 062: extend-r15-corpus-class-closure-scope

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none (R-15 is already retired per slice-057; this slice extends the backstop *mechanism* that retired R-15 to wider corpora — closes the slice-061 N=1 scope-gap watch-list before N=2 emerges in `tests/skills/**` or `tests/agents/**`)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The R-15 corpus class-closure backstop (`tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus`, slice-056) catches archive-fragile literal-path-RHS substrings **only in `tests/methodology/*.py`**. slice-061 surfaced N=1 evidence the scope gap is real: `tests/skills/code_review/test_code_review_skill.py:17-18` shipped a hardcoded `"slice-060-add-code-review-skill"` literal that broke at first archive (the slice-061 user-approved deferral). This slice (a) extends the backstop's effective scope to also cover `tests/skills/**/*.py` + `tests/agents/**/*.py` and (b) repoints the offending slice-060 literal via `_resolve_slice_dir(60)` from `tests.methodology.conftest`. Two coupled fixes; same slice (per slice-061 reflection nomination).

## Acceptance criteria

1. The R-15 corpus class-closure assertion's effective scope covers all three test corpora: `tests/methodology/**/*.py` + `tests/skills/**/*.py` + `tests/agents/**/*.py`. The post-extension test PASSES on the post-repoint codebase with no unexpected matches.
2. `tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060` constructs the slice-060 path via `_resolve_slice_dir(60)` (imported from `tests.methodology.conftest`) instead of the literal `"slice-060-add-code-review-skill"`; the test continues to PASS.
3. Test-first proof: BEFORE the literal repoint, running the extended assertion against the wider scope FAILs and names `tests/skills/code_review/test_code_review_skill.py` at the literal-bearing line. AFTER the repoint, the same assertion PASSES.
4. `architecture/risk-register.md` R-15 entry annotated with a post-retirement scope-extension paragraph documenting the slice-062 widening of the backstop's coverage from `tests/methodology/*.py` to also include `tests/skills/**/*.py` + `tests/agents/**/*.py`. R-15 `**Status**:` stays `retired` (no flip).

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Each AC maps to failing tests written BEFORE the implementation/fix lands. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology-audit (extract) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_methodology_corpus` (extracted-helper wrapper) | PASSING |
| 1 | methodology-audit (NEW) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_skills_corpus` | PASSING |
| 1 | methodology-audit (NEW) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_agents_corpus` | PASSING |
| 1 | methodology-audit (NEW; orphan-check) | `tests/methodology/test_resolve_slice_dir.py` | `test_r15_corpus_whitelist_has_no_orphan_entries` | PASSING |
| 2 | skill-pin (lazy repoint) | `tests/skills/code_review/test_code_review_skill.py` | `test_self_dogfood_produces_code_review_md_on_slice_060` (post-repoint, still PASSES) | PASSING |
| 3 | test-first sequencing proof | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_skills_corpus` (the AC#3 PRE-repoint mid-slice smoke FAIL signature naming `tests/skills/code_review/test_code_review_skill.py:17` is observed on this same test; the WRITTEN-FAILING → PASSING transition is timestamped in build-log.md Events per verification-plan row 3) | PASSING |
| 4 | audit-trail entry-pin (NEW) | `tests/methodology/test_methodology_changelog.py` | `test_v_0_65_0_r15_scope_extension_entry_present_in_repo` (the v0.65.0 methodology-changelog entry IS the audit-trail surface that the R-15 risk-register scope-extension paragraph cross-references; entry-pin presence is the structural proof for AC#4) | PASSING |
| 4 | audit-trail shippability-propagation (NEW) | `tests/methodology/test_methodology_changelog.py` | `test_v_0_65_0_r15_scope_extension_shippability_consumer_propagation` | PASSING |

The 3 per-corpus tests (rows 1-3) are themselves the walk-proof for their corpora (pytest collecting + passing each IS the structural proof the walker visits that corpus); the absence of any one from the pytest report IS the visible alarm. The aggregated orphan-check (row 4) replaces the prior per-function `missing_whitelist` shrinkage check (slice-056 lineage) — correct semantics across all 3 corpora because the whitelist is shared. Row 6 (AC#3) reuses the `test_no_new_archive_fragile_literals_in_tests_skills_corpus` test function as the sequencing-proof anchor — the mid-slice smoke gate observes its WRITTEN-FAILING signature pre-repoint and its PASSING signature post-repoint, timestamped in build-log.md Events. Rows 7-8 (AC#4) are the v0.65.0 methodology-changelog entry-pin + shippability-consumer-propagation pins (the audit-trail surface that AC#4's R-15 risk-register paragraph cross-references), structurally separated under their own SECTION header `# --- Slice-062 / R-15-scope-extension entry pinning ---` per EPGD-1 design-time-pre-empted-success-mode discipline.

**Bare-numeric AC labels + multi-row-per-AC shape per slice-056 /critique-review M-add-1 ACCEPTED-FIXED precedent** (the slice-040 N+1 doctrine — `tools/test_first_audit.py:_normalize_ac_label` does NOT strip commas or paren-bracket-prefix markers, so `"1, 3"` and `"(audit-trace)"` labels both produce `ac-without-row` violations at strict-pre-finish on AC#3 and AC#4). Verified empirically at /critique-review fix block: `$PY -m tools.test_first_audit <slice-folder> --strict-pre-finish` exit 0 (zero violations).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Wider-scope coverage | `& $PY -m pytest tests/methodology/test_resolve_slice_dir.py -v` shows all corpus-class-closure assertions PASS post-fix |
| 2 | Code-review test repoint | `& $PY -m pytest tests/skills/code_review/test_code_review_skill.py::test_self_dogfood_produces_code_review_md_on_slice_060 -v` PASSES with slice-060 archived; `grep -n '_resolve_slice_dir' tests/skills/code_review/test_code_review_skill.py` shows the import + call site |
| 3 | Test-first sequencing proof | `build-log.md` Events log captures the PENDING → WRITTEN-FAILING (assertion fails on `tests/skills/code_review/test_code_review_skill.py:17`) → PASSING transition with timestamps |
| 4 | Risk-register update | `& $PY -m tools.risk_register_audit architecture/risk-register.md --filter-status retired` still includes R-15 (status unchanged); the file's R-15 block contains the new scope-extension paragraph; **STP-1 Sub-form B audit** stays clean (no `..._stays_retired` test contradicts the unchanged `retired` status) |

## Must-not-defer

- [ ] **Whitelist correctness**: post-extension, the whitelist contains only documented-deferred sites (none in the new subtrees, or each explicitly justified in inline comment). No orphan entries.
- [ ] **Walk-proof regression tests** (TF-1 rows 2 + 3 above): without them, an extension that walks the wrong path would silently pass. Closes slice-056 N=1 lesson.
- [ ] **Multi-line regex coverage in wider scope**: the slice-056 N=1 fix ensured `_R15_LITERAL_PATH_RE` matches across newlines in `tests/methodology/`; the extension MUST preserve this in `tests/skills/**` + `tests/agents/**`. Verified by a fixture test or by the post-fix corpus already containing a multi-line construct (none currently observed — explicit verification in design.md).
- [ ] **No silent scope regression**: the existing `tests/methodology/*.py` coverage MUST be preserved (not just replaced).
- [ ] **Naming/structure decision documented**: design.md + ADR-060 weigh 4 candidate shapes (numbered 1-4 in ADR-060 §"Options considered"); option 3 (extract helper + 3 per-corpus tests + 1 aggregated whitelist-integrity test + shared whitelist) selected with rationale (walk-proof falls out structurally); no silent rename. ADR-060 is the authoritative enumeration.

## Out of scope

- **slice-060 `/code-review` v2 enhancements** — AI-bloat passes (deferred from slice-060 to slice-061 then slipped) + TRI-1 triage gate + verdict-driven block on `/validate-slice`. These are substantial `/code-review` skill enhancements, separate from this slice's structural test-infrastructure fix. Belong in slice-063+ on the `/code-review` v2 track. **Acknowledged-divergence note**: `architecture/slices/archive/slice-060-add-code-review-skill/reflection.md:37` explicitly nominated **slice-062** for the TRI-1 gate + verdict-driven block ("slice-060's findings stay advisory only in v1"); slice-062 deliberately deviates from that nomination because (a) the R-15 corpus-class scope-extension addresses slice-061's already-deferred shippability row #60 (a build-time-deterministic gate, higher-priority class than feature-level enhancement); (b) the slice-061 reflection (more recent nominator) ranks the R-15 extension as the primary slice-062 carrier; (c) TRI-1 + verdict-block is a feature-level enhancement that can land independently on the `/code-review` v2 track without coupling to R-15 hygiene. The slice-060 reflection's TRI-1 nomination remains the highest-priority slice-063 candidate per `/code-review`'s documented walking-skeleton advisory-only v1 disposition.
- **R-17 BRANCH-1 clean-tree precondition fix** (slice-062-or-later nomination from slice-061) — adjacent pipeline-hygiene track; separate slice.
- **R-18 mitigation** (agent registry session-cache miss; slice-062-or-later) — separate slice on the methodology-side warning track.
- **Multi-session / parallel-slice / worktree-per-slice execution** (user-raised at /slice invocation 2026-05-23) — out of scope for slice-062; flagged at /slice Step 3 as requiring a design-first sequence of slices, not a single bundled feature. No R-19 minted in this slice.
- **Critic-prompt dimension extension for BC-PROJ-11 sibling-coverage** (slice-061 N=1 watch-list) — defer to /critic-calibrate route at N=2.

## Dependencies

- **Prior slices**:
  - [[slice-056-fix-bcr1-round-trip-test-archive-paths]] — established the corpus class-closure backstop foundation (R-15 part-(b) mechanism) AND the `_resolve_slice_dir` helper in `tests/methodology/conftest.py`
  - [[slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit]] — retired R-15 part-(a) via retrofit; established the retirement-discharge precedent this slice extends
  - [[slice-061-fix-install-python-detection-and-prompt-fallback]] — surfaced the N=1 scope gap + nominated the two-coupled-fixes shape this slice implements
  - [[slice-060-add-code-review-skill]] — shipped the offending literal at `tests/skills/code_review/test_code_review_skill.py:17-18`
- **Code surfaces**:
  - `tests/methodology/test_resolve_slice_dir.py:226-299` (corpus backstop being extended)
  - `tests/methodology/conftest.py` (`_resolve_slice_dir` helper)
  - `tests/skills/code_review/test_code_review_skill.py:14-19` (literal being repointed)
- **Vault refs**:
  - [[architecture/risk-register.md#R-15]] (entry being updated)
  - [[architecture/lessons-learned.md]] (slice-061 N=1 lesson; slice-056 walk-proof lesson)
- **Currently-failing tests claimed**: NONE — no `tests/bugs/*` repro test (this is a structural-scope-extension class slice, NOT a bug fix; BFRD-1 does not fire per Step 3c detection).

## Mid-slice smoke gate

At ~50% of build (after the extended assertion is written but BEFORE the literal repoint), run:

```powershell
& $env:USERPROFILE\.claude\.venv\Scripts\python.exe -m pytest `
  tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus `
  -v
```

**Expected**: assertion **FAILs** with the diagnostic naming `tests/skills/code_review/test_code_review_skill.py` at the literal-bearing line (currently line 17-18 — the `"slice-060-add-code-review-skill"` literal). The failure message MUST cite the new corpus member, NOT a `tests/methodology/*.py` member.

**If it PASSES at this point**: the extension's walker is NOT actually visiting `tests/skills/**` — STOP, diagnose the walk logic, do not continue.
**If it FAILs with a different file**: there's an unexpected pre-existing literal — STOP, surface to user, re-scope.
**If it FAILs with the expected file at the expected line**: proceed to repoint phase.

## Pre-finish gate

- [ ] All 4 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] Test-first audit (TF-1) shows all 4 rows in PASSING state with WRITTEN-FAILING checkpoint timestamped in build-log.md Events
- [ ] Mid-slice smoke gate transitioned cleanly: pre-fix FAIL (with the expected file/line) → post-fix PASS
- [ ] Walk-proof tests (TF-1 rows 2 + 3) PASS — proving the walker actually visits the new corpora
- [ ] `/drift-check` clean (R-15 risk-register update consistent with notes; whitelist consistent with corpus)
- [ ] `& $PY -m tools.risk_register_audit architecture/risk-register.md` JSON output reflects the R-15 status update
- [ ] No new TODOs / FIXMEs / debug prints in the touched files
- [ ] BC-1 / PMI-1 / **PVFS-1** / BRANCH-1 / AVFS-1 / MCFS-1 / SCMD-1 / SCPD-1 / RPCD-1 / STP-1 / PCA-1 / BCI-1 / WIRE-1 / TF-1 / ETC-1 / WS-1 / CSP-1 / SUP-1 / CRP-1 / UTF8-STDOUT-1 / EOL-DRIFT-1 / CAD-1 / OSDG-1 (and the rest of the Standard-mode gate stack) PASS — this slice introduces NO new audit rule, so no shippability-row propagation obligation fires. **PVFS-1 is named explicitly** because the slice bumps `VERSION` 0.64.0→0.65.0 and the 5-part bump leg per slice-060 v0.64.0 precedent MUST include `pyproject.toml [project].version`; a 4-part bump would FAIL PVFS-1's `test_repro_sc001_pyproject_project_version_matches_version_file` at Step 6.
- [ ] Self-application audit (per the OSDG-1 / CAD-1 family discipline): the slice's own touched files do not introduce regressions in the in-house methodology audit pinned by `tests/methodology/`

## Pipeline position

- **predecessor**: `/reflect` (slice-061 reflection nominated this slice)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission brief + milestone.md are written; user picked candidate explicitly via structured options at /slice Step 3 (the `#1 slice-062 corpus-closure (Recommended)` option). Auto-invoke `/design-slice`.
- **user-input gates**: NONE pending — candidate-selection gate cleared; no BFRD-1 trigger fired.

Per **PCA-1** (`methodology-changelog.md` v0.41.0).
