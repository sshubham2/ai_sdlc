# Design: Slice 062 extend-r15-corpus-class-closure-scope

**Date**: 2026-05-23
**Mode**: Standard

## What's new

- A new helper `_scan_corpus_for_r15_literals(corpus_dir: Path) -> set[tuple[str, int]]` extracted from the existing R-15 corpus class-closure backstop body in `tests/methodology/test_resolve_slice_dir.py`. Encapsulates: rglob walk, self-skip, regex finditer, line-number computation, repo-relative path normalization. NO behavior change for the existing methodology-corpus call site (per-line equality vs the prior inlined logic).
- Two NEW per-corpus test functions in the same file:
  - `test_no_new_archive_fragile_literals_in_tests_skills_corpus`
  - `test_no_new_archive_fragile_literals_in_tests_agents_corpus`
  Each calls `_scan_corpus_for_r15_literals` on its corpus directory, asserts `matches ⊆ _R15_CORPUS_WHITELIST`, with diagnostics naming the unexpected sites.
- ONE NEW aggregated whitelist-integrity test:
  - `test_r15_corpus_whitelist_has_no_orphan_entries`
  Asserts `_R15_CORPUS_WHITELIST ⊆ union(matches_methodology, matches_skills, matches_agents)`. This replaces the per-function `missing_whitelist` shrinkage check (which was tied to a single corpus). Aggregated check is correct across all 3 corpora because the whitelist is shared.
- Existing `test_no_new_archive_fragile_literals_in_methodology_corpus` becomes a thin wrapper calling the helper on `tests/methodology/` + asserting `matches ⊆ _R15_CORPUS_WHITELIST`. Function name PRESERVED (verified at /design-slice graphify pass: name appears only in its own file; no string-references elsewhere; renaming would create STP-1 Sub-form A risk for no semantic benefit). The post-scope-extension orphan check is moved to the aggregated test above; removed-in-place at the per-corpus wrapper.
- `tests/skills/code_review/test_code_review_skill.py`: the `_SLICE_060_CODE_REVIEW` module-level binding is removed; resolution is moved INSIDE `test_self_dogfood_produces_code_review_md_on_slice_060` and uses `_resolve_slice_dir(60) / "code-review.md"`. Lazy resolution (not module-level binding) chosen because: (1) failure at test-run-time is a clearer diagnostic than import-time AssertionError that errors the entire module's collection; (2) parallels the existing `_REPO_ROOT` binding pattern which is also module-level but only feeds non-archived paths (`skills/code-review/SKILL.md`); (3) matches the slice-056 helper-precedent semantic (`_resolve_slice_dir` is documented to raise AssertionError on neither-match — test-time is the right surface for that assertion).
- A new ADR-060 records the scope-extension decision with reversibility:cheap.
- A new `## v0.65.0 — 2026-05-23` methodology-changelog entry per the Inclusion heuristic (a methodology-surface drift-guard scope-extension behavior change with no other bump reason: a new archive-fragile literal in `tests/skills/**` or `tests/agents/**` was acceptable-yesterday, refused-today; matches the slice-051 / ADR-053 OSDG-1 member-addition lineage precedent).
- **5-part PMI-1 atomic version bump** 0.64.0 → 0.65.0 (`VERSION` + `plugin.yaml.version` per PMI-1 + `pyproject.toml [project].version` per **PVFS-1** + this `methodology-changelog.md` `## v0.65.0` header + installed `~/.claude/ai-sdlc-VERSION` per AVFS-1, with `methodology-changelog.md` forward-synced to `~/.claude/methodology-changelog.md` per MCFS-1). Matches the slice-060 v0.64.0 5-part shape verbatim (slice-060 reflection L50: "B2 PMI-1 4-part vs 5-part VALIDATED"); a 4-part bump would FAIL `tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file` at /build-slice Step 6 because `pyproject.toml [project].version` would stay at `0.64.0` while `VERSION` moves to `0.65.0`.
- `architecture/shippability.md` gains one row for the new tests + ADR-060 + the v0.65.0 entry-pin tests (single row per slice per RPCD-1).
- Two new entry-pin tests in `tests/methodology/test_methodology_changelog.py`:
  - `test_v_0_65_0_r15_scope_extension_entry_present_in_repo`
  - `test_v_0_65_0_r15_scope_extension_shippability_consumer_propagation`
  Following the v0.58.0 / v0.59.0 / v0.64.0 entry-pin pattern verbatim.
- `CLAUDE.md` (project root) `## Self-hosting discipline` Mini-CAD/OSDG-1 bullet stays unchanged (R-15 corpus backstop is NOT an OSDG-1 member — they are sibling drift-guards in different families). No CLAUDE.md edit.
- `architecture/risk-register.md` R-15 entry gains a post-retirement scope-extension paragraph (status STAYS `retired`; no flip).

## What's reused

- `tests.methodology.conftest._resolve_slice_dir` — slice-056 helper, unchanged. Verified cross-package import works from `tests/skills/code_review/test_code_review_skill.py` at /design-slice empirical pass (`pythonpath = .` in `pytest.ini:6` + explicit `__init__.py` in `tests/methodology/` and `tests/skills/code_review/` make `tests.methodology.conftest` resolve).
- `_R15_LITERAL_PATH_RE` — existing compiled regex, unchanged. Already whitespace-tolerant across newlines per slice-056 N=1 fix. NO new regex.
- `_R15_CORPUS_WHITELIST` — existing `set[tuple[str, int]]`, unchanged shape. Stays a shared single source of truth across all 3 corpora. Currently empty (no documented-deferred sites in any corpus, verified at /design-slice empirical scan).
- `REPO_ROOT` from `tests.methodology.conftest` — module-level binding, unchanged. Available to the new helper via existing import.
- `_resolve_slice_dir(60)` correctly resolves to `architecture/slices/archive/slice-060-add-code-review-skill` (verified empirically at /design-slice — slice-060 IS archived).
- Existing 5 unrelated tests in `test_resolve_slice_dir.py` (`test_helper_is_importable_from_conftest`, `test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir`, `test_resolves_archived_slice_054`, `test_resolves_active_slice_via_tmp_vault`, `test_raises_assertion_with_diagnostic_when_neither_found`) — UNCHANGED. No regression.
- Existing 2 unrelated tests in `test_code_review_skill.py` (`test_skill_md_pipeline_position_block_present`, `test_skill_md_successor_is_validate_slice`) — UNCHANGED. Module-level `_REPO_ROOT` and `_SKILL_MD` bindings stay (still needed for the `skills/code-review/SKILL.md` reads).
- The `_read(path)` helper at `test_code_review_skill.py:22-24` — UNCHANGED.
- [[ADR-029]] sound-control-for-a-non-deterministic-step pattern — invoked indirectly: the slice-056 backstop IS a deterministic downstream gate against the LLM-prose `/reflect` archival step; widening the backstop's coverage strengthens the existing gate's reach without changing the pattern.
- [[ADR-053]] precedent — extending an existing drift-guard's coverage set via a new ADR that mints no new RULE-ID and supersedes nothing. ADR-060 follows this shape (extends R-15 backstop scope vs ADR-053 extends OSDG-1 member set).

## Components touched

### `tests/methodology/test_resolve_slice_dir.py` (modified)

- **Responsibility**: methodology self-test pinning `_resolve_slice_dir` helper + the R-15 corpus class-closure backstop. Post-slice: backstop coverage widens from `tests/methodology/*.py` to also include `tests/skills/**/*.py` + `tests/agents/**/*.py`.
- **Lives at**: `tests/methodology/test_resolve_slice_dir.py` (modified by this slice)
- **Key interactions**: imports `_resolve_slice_dir`, `REPO_ROOT` from `tests.methodology.conftest`; uses `_R15_LITERAL_PATH_RE` compiled regex (same file). Run by `/build-slice` Step 6 pre-finish via the full `pytest` suite (TF-1 / BC-1 / BC-PROJ-4).

### `tests/skills/code_review/test_code_review_skill.py` (modified)

- **Responsibility**: CRSI-1 pin for `/code-review` skill SKILL.md + walking-skeleton self-dogfood proof. Post-slice: the slice-060 archive-path literal is replaced by a `_resolve_slice_dir(60)` call inside the test function.
- **Lives at**: `tests/skills/code_review/test_code_review_skill.py` (modified by this slice)
- **Key interactions**: NEW import `from tests.methodology.conftest import _resolve_slice_dir`; existing `_REPO_ROOT` and `_SKILL_MD` module-level bindings preserved.

### `architecture/decisions/ADR-060-extend-r15-corpus-backstop-scope.md` (new)

- **Responsibility**: records the scope-extension decision (4 options considered in ADR-060 §"Options considered"; option 3 selected with rationale); reversibility:cheap; mints no new RULE-ID; extends slice-056 / slice-057 R-15 lineage.
- **Lives at**: `architecture/decisions/ADR-060-extend-r15-corpus-backstop-scope.md` (created by this slice)
- **Key interactions**: cited by methodology-changelog v0.65.0 entry, by this slice's risk-register R-15 scope-extension paragraph, by the v0.65.0 entry-pin test.

### `methodology-changelog.md` + `~/.claude/methodology-changelog.md` (modified)

- **Responsibility**: append-only methodology-surface behavior-change log. Post-slice: new `## v0.65.0 — 2026-05-23` entry documents the scope extension per the Inclusion heuristic.
- **Lives at**: `methodology-changelog.md` (in-repo, modified by this slice) + `~/.claude/methodology-changelog.md` (installed copy, forward-synced per MCFS-1)
- **Key interactions**: read by `/critic-calibrate`, `/pulse`, this slice's `/reflect` Step 5b; forward-sync gate is the MCFS-1 audit at `/build-slice` Step 6 + `/reflect` Step 5b.

### `VERSION` + `plugin.yaml` + `pyproject.toml` + `~/.claude/ai-sdlc-VERSION` (modified)

- **Responsibility**: 5-part PMI-1 atomic version bump 0.64.0 → 0.65.0 (in-repo VERSION + plugin.yaml.version + **pyproject.toml [project].version per PVFS-1** + AVFS-1 installed copy + MCFS-1 changelog header).
- **Key interactions**: validated by PMI-1 (`tools/plugin_manifest_audit.py`), **PVFS-1 (`tests/methodology/test_pyproject_version_matches_version_file.py`)**, AVFS-1 (`tools/ai_sdlc_version_forward_sync.py`), MCFS-1 (`tools/methodology_changelog_forward_sync.py`) at `/build-slice` Step 6.

### `architecture/shippability.md` (modified)

- **Responsibility**: catalog of "must never silently regress" claims. Post-slice: one new row per RPCD-1 / SCPD-1 carrying the 4 new methodology test functions + the lazy-repointed code-review test.
- **Key interactions**: validated by SCPD-1 / RPCD-1 audits at `/build-slice` Step 6.

### `architecture/risk-register.md` (modified)

- **Responsibility**: R-15 entry gains a post-retirement scope-extension paragraph documenting the slice-062 widening. Status STAYS `retired` (no flip).
- **Key interactions**: STP-1 Sub-form B audit stays clean (no `*_stays_retired` test exists for R-15; no contradiction introduced).

## Contracts added or changed

This slice introduces no new endpoints, events, or external interfaces. The "contract" change is the implicit covered-scope of the R-15 corpus class-closure backstop:

| Surface | Before slice-062 | After slice-062 |
|---|---|---|
| R-15 corpus class-closure backstop covered scope | `tests/methodology/*.py` only | `tests/methodology/*.py` + `tests/skills/**/*.py` + `tests/agents/**/*.py` |
| Whitelist `_R15_CORPUS_WHITELIST` shape | shared `set[tuple[str, int]]` | UNCHANGED |
| Whitelist content | empty | empty (the slice-061-surfaced literal at `tests/skills/code_review/test_code_review_skill.py:17` is REPOINTED, not whitelisted) |
| `test_code_review_skill.py:_SLICE_060_CODE_REVIEW` resolution | module-level literal `..."slice-060-add-code-review-skill"...` | lazy `_resolve_slice_dir(60)` call inside test function |

## Data model deltas

None. This slice introduces no schemas, no entities, no database changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Each new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `architecture/decisions/ADR-060-extend-r15-corpus-backstop-scope.md` | `methodology-changelog.md` v0.65.0 entry-pin (`Rule reference: ADR-060`); `architecture/risk-register.md` R-15 scope-extension paragraph; this slice's `design.md` | `tests/methodology/test_methodology_changelog.py::test_v_0_65_0_r15_scope_extension_entry_present_in_repo` | — |

NO new tool modules in `tools/`, NO new skill in `skills/`, NO new agent in `agents/`. The 4 new test functions are added to EXISTING test modules (`test_resolve_slice_dir.py` + `test_methodology_changelog.py`) — not new files. WIRE-1 audit treats a single-row matrix with the ADR-060 row as clean.

## Decisions made (ADRs)

- [[ADR-060]] — Extend R-15 corpus class-closure backstop scope to all test corpora via shared helper + per-corpus test functions — reversibility: **cheap**

## Authorization model for this slice

N/A. This slice modifies methodology self-tests + version files + documentation. No auth/authz surface touched. No multi-tenancy or user-facing permission model relevant.

## Error model for this slice

- **Helper `_scan_corpus_for_r15_literals` invoked on a missing directory**: raises `AssertionError` (via the existing `is_dir()` precondition pattern from the current `test_no_new_archive_fragile_literals_in_methodology_corpus` L256-258). Consistent with existing semantics.
- **A new R-15-class literal in `tests/skills/**` or `tests/agents/**` (post-slice)**: the relevant per-corpus test FAILs at `/build-slice` Step 6 pytest run with a diagnostic naming the file + line + the canonical mitigation hint ("Use `_resolve_slice_dir(NNN)` from `tests.methodology.conftest`"). NOT exit 2 — this is a pytest assertion failure within a regular test, exit 1. Matches existing methodology-corpus assertion semantics verbatim.
- **`_resolve_slice_dir(60)` invoked when slice-060 is absent (e.g., archive deleted)**: raises `AssertionError` per the slice-056 documented contract (`test_raises_assertion_with_diagnostic_when_neither_found`). Surface is the test function (not module import), so a single test fails with a clear diagnostic instead of erroring the entire module's collection.

## Build sequencing

Per TF-1 (test-first). Sequenced so the WRITTEN-FAILING → PASSING transition is observable + the mid-slice smoke gate gives the expected diagnostic.

**Phase A — extract helper + add per-corpus tests (TF-1 WRITTEN-FAILING phase)**:
1. Extract `_scan_corpus_for_r15_literals(corpus_dir: Path) -> set[tuple[str, int]]` helper from the existing function body (NO behavior change to the methodology-corpus call site).
2. Rewrite `test_no_new_archive_fragile_literals_in_methodology_corpus` as thin wrapper: call helper on `tests/methodology/`, assert `matches ⊆ _R15_CORPUS_WHITELIST`. REMOVE the per-function `missing_whitelist` shrinkage check (will be re-added at Phase A4 as the aggregated test).
3. Add NEW test `test_no_new_archive_fragile_literals_in_tests_skills_corpus`: call helper on `tests/skills/`, assert `matches ⊆ _R15_CORPUS_WHITELIST`.
4. Add NEW test `test_no_new_archive_fragile_literals_in_tests_agents_corpus`: call helper on `tests/agents/`, assert `matches ⊆ _R15_CORPUS_WHITELIST`.
5. Add NEW test `test_r15_corpus_whitelist_has_no_orphan_entries`: scan all 3 corpora, assert `_R15_CORPUS_WHITELIST - union(all_matches) == ∅`.
6. **Mid-slice smoke gate**: run `tests/methodology/test_resolve_slice_dir.py` — EXPECT:
   - `test_no_new_archive_fragile_literals_in_methodology_corpus` → PASS (methodology corpus has no literals)
   - `test_no_new_archive_fragile_literals_in_tests_skills_corpus` → **FAIL** with diagnostic naming `tests/skills/code_review/test_code_review_skill.py` line 17
   - `test_no_new_archive_fragile_literals_in_tests_agents_corpus` → PASS (agents corpus clean)
   - `test_r15_corpus_whitelist_has_no_orphan_entries` → PASS (whitelist empty, vacuous)
   - All other unrelated tests → PASS
   - The build-log.md Events line captures this with timestamp (the WRITTEN-FAILING checkpoint).

**Phase B — repoint code-review test (TF-1 PASSING phase)**:
7. In `tests/skills/code_review/test_code_review_skill.py`:
   - Add import: `from tests.methodology.conftest import _resolve_slice_dir`
   - REMOVE the module-level `_SLICE_060_CODE_REVIEW = ...` binding (L16-19)
   - Inside `test_self_dogfood_produces_code_review_md_on_slice_060`: resolve `slice_060_code_review = _resolve_slice_dir(60) / "code-review.md"` and pass to `_read`.
8. Re-run `tests/methodology/test_resolve_slice_dir.py` + `tests/skills/code_review/test_code_review_skill.py`: ALL 4 corpus + walk-proof + integrity tests PASS; the repointed code-review test PASSES.
9. Build-log.md Events line captures the PASSING transition with timestamp.

**Phase C — ADR + methodology-changelog + version bump + shippability + risk-register**:
10. Author ADR-060.
11. Append `## v0.65.0 — 2026-05-23` methodology-changelog entry following the v0.59.0 / v0.64.0 entry-body template (one-paragraph summary + `### Added`/`### Changed` block + `Rule reference` line + `Defect class` line + `Validation` line, per the methodology-changelog.md L17-31 format spec). The **bump shape is 5-part PMI-1** per step 12 below — explicitly NOT 4-part. The v0.65.0 entry body MUST contain the substring `"5-part PMI-1 atomic bump"` (asserted by the new entry-pin test per the CSP-1 cross-spec parity table).
12. **5-part PMI-1 bump**: `VERSION` 0.64.0→0.65.0; `plugin.yaml.version` 0.64.0→0.65.0; **`pyproject.toml [project].version` 0.64.0→0.65.0 (PVFS-1 leg)**; `cp` `methodology-changelog.md` → `~/.claude/methodology-changelog.md` (MCFS-1 leg, header + body); `cp` `VERSION` → `~/.claude/ai-sdlc-VERSION` (AVFS-1 leg).
13. Append `architecture/shippability.md` row.
14. Add 2 entry-pin tests `test_v_0_65_0_r15_scope_extension_entry_present_in_repo` + `test_v_0_65_0_r15_scope_extension_shippability_consumer_propagation` to `tests/methodology/test_methodology_changelog.py`. **Per EPGD-1 design-time-pre-empted-success-mode discipline**: append the two tests under a NEW dedicated SECTION header `# --- Slice-062 / R-15-scope-extension entry pinning ---` placed AT END of the file (after the v0.64.0 / slice-060 / CRSI-1 entry-pin block closes; current location `tests/methodology/test_methodology_changelog.py:3943` for the slice-060 SECTION header — append the new SECTION below the v0.64.0 block's closing). Do NOT fold the slice-062 tests into the slice-060 SECTION header. Mirrors the SCMD-1 (slice-056) → CRSI-1 (slice-060) per-slice SECTION-header separation pattern.
15. Append the R-15 scope-extension paragraph to `architecture/risk-register.md`. **The new paragraph opens with explicit historical-record framing**: *"**slice-062 scope-extension (2026-05-23)**: the slice-056/057 backstop's effective scope is widened from `tests/methodology/*.py` (as documented in the slice-056/057 historical-record paragraphs above) to also cover `tests/skills/**/*.py` + `tests/agents/**/*.py`. The slice-056/slice-057 paragraphs above preserve their then-current scope claims verbatim as historical record per slice-040 R-10 retirement-precedent (no edit-in-place of prior risk-register prose); the slice-057 retirement paragraph at `risk-register.md:266`'s `tests/methodology/*.py` scope claim describes the pre-slice-062 backstop state. Post-slice-062, the backstop's wired-into-CI scope covers all three test corpora."* This framing makes the slice-057 paragraph's `tests/methodology/*.py` claim explicitly historical (not contradictory) for any future reader of R-15.

**Phase D — pre-finish gate**:
16. Run full pytest suite. ALL tests PASS.
17. Run audit stack: `tools.plugin_manifest_audit`, `tools.install_audit`, `tools.critique_agent_drift_audit`, `tools.methodology_changelog_forward_sync`, `tools.ai_sdlc_version_forward_sync`, **PVFS-1 test (`pytest tests/methodology/test_pyproject_version_matches_version_file.py`)**, `tools.shippability_decoupling_audit`, `tools.state_transition_pin_audit`, `tools.pipeline_chain_audit`, `tools.build_checks_integrity`, `tools.branch_workflow_audit`, `tools.utf8_stdout_audit`, `tools.cross_spec_parity_audit`, `tools.risk_register_audit`. ALL exit 0.
18. `/code-review` runs against the slice diff (per slice-060 CRSI-1).
19. `/validate-slice` confirms ACs PASS.

## Test-first plan (single source of truth — mission-brief.md TF-1 plan section is content-equal to this table)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology-audit (extract) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_methodology_corpus` (extracted-helper wrapper) | PASSING |
| 1 | methodology-audit (NEW) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_skills_corpus` | PASSING |
| 1 | methodology-audit (NEW) | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_agents_corpus` | PASSING |
| 1 | methodology-audit (NEW; orphan-check) | `tests/methodology/test_resolve_slice_dir.py` | `test_r15_corpus_whitelist_has_no_orphan_entries` | PASSING |
| 2 | skill-pin (lazy repoint) | `tests/skills/code_review/test_code_review_skill.py` | `test_self_dogfood_produces_code_review_md_on_slice_060` (post-repoint, still PASSES) | PASSING |
| 3 | test-first sequencing proof | `tests/methodology/test_resolve_slice_dir.py` | `test_no_new_archive_fragile_literals_in_tests_skills_corpus` (AC#3 WRITTEN-FAILING signature observed on this test pre-repoint at mid-slice smoke; PASSING signature post-repoint; transition timestamped in build-log.md Events per verification-plan row 3) | PASSING |
| 4 | audit-trail entry-pin (NEW) | `tests/methodology/test_methodology_changelog.py` | `test_v_0_65_0_r15_scope_extension_entry_present_in_repo` (v0.65.0 methodology-changelog entry IS the audit-trail surface the R-15 risk-register scope-extension paragraph cross-references — entry-pin presence is the structural proof for AC#4) | PASSING |
| 4 | audit-trail shippability-propagation (NEW) | `tests/methodology/test_methodology_changelog.py` | `test_v_0_65_0_r15_scope_extension_shippability_consumer_propagation` | PASSING |

**Bare-numeric AC labels + multi-row-per-AC shape per slice-056 /critique-review M-add-1 ACCEPTED-FIXED precedent** (the slice-040 N+1 doctrine): `tools/test_first_audit.py:_normalize_ac_label` does NOT strip commas or paren-bracket-prefix markers — `"1, 3"` and `"(audit-trace)"` produce `ac-without-row` violations on AC#3 + AC#4 at strict-pre-finish. The 3 per-corpus tests (rows 1-3) are themselves the walk-proof for their corpora (pytest collecting + passing each IS the structural proof the walker visits that corpus); row 6 reuses the `test_no_new_archive_fragile_literals_in_tests_skills_corpus` as the AC#3 sequencing-proof anchor (the mid-slice smoke FAIL→PASS observation lives on this test); rows 7-8 (AC#4 audit-trail) are the v0.65.0 methodology-changelog entry-pin + shippability-consumer-propagation pins under their own EPGD-1 SECTION header. Verified empirically at /critique-review fix block: `$PY -m tools.test_first_audit <slice-folder> --strict-pre-finish` exit 0 (zero violations).

## CSP-1 cross-spec parity check

| Surface | Where stated | Where enforced |
|---|---|---|
| Backstop covers 3 corpora | `methodology-changelog.md` v0.65.0 entry; ADR-060 Decision; this `design.md`; mission-brief AC#1 | 3 per-corpus test functions in `test_resolve_slice_dir.py` |
| Whitelist is shared single SSOT | ADR-060 Decision (option 3 rationale); this `design.md` | `_R15_CORPUS_WHITELIST` single module-level binding + `test_r15_corpus_whitelist_has_no_orphan_entries` aggregated check |
| Lazy resolution in `test_code_review_skill.py` | this `design.md` Components-touched section; ADR-060 Consequences | `tests/skills/code_review/test_code_review_skill.py` (the resolution lives inside the test function, verifiable by reading) |
| R-15 status stays `retired` | this `design.md`; mission-brief AC#4; ADR-060 Reversibility | `tools.risk_register_audit --filter-status retired` lists R-15 + STP-1 Sub-form B (no `*_stays_retired` test contradicts) |
| v0.65.0 entry exists with Rule reference: ADR-060 | `methodology-changelog.md` v0.65.0 | `test_v_0_65_0_r15_scope_extension_entry_present_in_repo` + `test_each_changelog_entry_carries_rule_reference` (pre-existing) |
| **5-part PMI-1 atomic bump shape (incl. PVFS-1)** | `methodology-changelog.md` v0.65.0 entry body (substring `"5-part PMI-1 atomic bump"`) | `test_v_0_65_0_r15_scope_extension_entry_present_in_repo` asserts the substring `"5-part PMI-1 atomic bump"` is present in the v0.65.0 body (mirrors slice-060 v0.64.0 entry-pin assertion (f) at `tests/methodology/test_methodology_changelog.py:3989`); PVFS-1 gate (`pytest tests/methodology/test_pyproject_version_matches_version_file.py::test_repro_sc001_pyproject_project_version_matches_version_file`) PASSES at /build-slice Step 6 |

## Anti-patterns explicitly avoided

- **In-place rename of `test_no_new_archive_fragile_literals_in_methodology_corpus`**: rejected (ADR-060 option 2 — the in-place body extension + rename variant; presented in the /design-slice ASK as option A). STP-1 Sub-form A risk for no semantic benefit. Function name stays — its scope-claiming suffix `_in_methodology_corpus` is locally accurate (it scans `tests/methodology/`); the wider-scope coverage is delivered via the two NEW per-corpus test functions which carry corpus-accurate names.
- **Module-level import-time resolution of slice-060 path**: rejected. Failure-mode would be import-time AssertionError erroring the whole module's collection; lazy in-test-function resolution localizes the failure to the test function and matches `_resolve_slice_dir`'s documented contract surface.
- **Per-corpus whitelist partitioning**: rejected. The current single shared whitelist is empty + remains empty post-slice; partitioning would introduce 3 module-level constants for no current benefit + complicate the orphan-check semantics.
- **Bundling slice-060 `/code-review` v2 enhancements (AI-bloat passes + TRI-1 + verdict-block)**: explicitly out of scope per mission-brief (slice-063+ work). Bundling would push ACs > 5 and effort > 1 day.

## Risks introduced (none retired by this slice; R-15 already retired)

- **R-19 candidate (NOT minted this slice; flagged only)**: parallel-slice execution / worktree-per-slice / claim-locks — user-raised at /slice invocation 2026-05-23. Surfaced as a Step-3 candidate but explicitly out of scope here. If picked up in a future slice, mint as R-19 at that slice's /design-slice, not retroactively from slice-062.
