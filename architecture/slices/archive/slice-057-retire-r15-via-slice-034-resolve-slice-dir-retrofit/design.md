# Design: Slice 057 retire-r15-via-slice-034-resolve-slice-dir-retrofit

**Date**: 2026-05-21
**Mode**: Standard

## What's new

This slice introduces no new modules, no new components, no new tools, no new ADRs, no new methodology rules, and no new methodology-changelog entries. It is a pure conformance / retirement-discharge slice (slice-040 R-10 / slice-043 R-6 / slice-045 R-11 precedent class).

The concrete edits are four:

1. **`tests/methodology/test_ptffd1_no_false_positive.py:69-72`** — repoint the multi-line literal `REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"` to `_resolve_slice_dir(34) / "mission-brief.md"`. Add `_resolve_slice_dir` to the top-of-file import from `tests.methodology.conftest` (joins the existing `REPO_ROOT` import on the same `from … import …` line). The `slice034` local binding name is preserved (no rename — minimal diff; the local is private to the test).
2. **`tests/methodology/test_resolve_slice_dir.py:214-220`** — shrink `_R15_CORPUS_WHITELIST` from `{("tests/methodology/test_ptffd1_no_false_positive.py", 70)}` to the empty set `set()` (explicit `set()` form, NOT `{}` which is a dict literal; verified at design-time). Rewrite the surrounding comment block from "deferral surface" framing to "retirement-discharge witness" framing, citing slice-057 + R-15-retired status. Preserve the M-add-2-mechanism docstring lineage so the test's intent stays legible to a future reader who is wondering why the assertion still exists with an empty whitelist (answer: the `unexpected = matches - whitelist` half is the durable forever-pin; the `missing_whitelist = whitelist - matches` half is now trivially true and stays as a regression-tripwire if a future maintainer adds an entry without an accompanying offending literal). **Builder guard-rail (per /critique-review m-add-2 ACCEPTED-FIXED — slice-040 N+1 doctrine: slice-056 just minted the corpus class-closure backstop, slice-057 is its first governed slice)**: the rewritten comment block MUST NOT contain any literal `REPO_ROOT / "architecture" / "slices" / …` Python-source-form construction that the `_R15_LITERAL_PATH_RE` regex (line 226-228) would match — only English prose references to the literal. The self-skip clause at lines 259-260 (`if py_file.resolve() == Path(__file__).resolve(): continue`) DOES shield this file from self-matching at runtime, but the corpus-backstop scan iterates `tests/methodology/*.py` files; ANY future test module that copy-pastes the comment for context would inherit a match. If an in-comment example is needed, use a markdown code-fence inside a docstring (regex matches only the bare `REPO_ROOT / "architecture" / …` sequence, not code-fence-rendered prose) OR a backtick-fenced inline placeholder like `` `REPO_ROOT/…/"slices"/…` `` with internal slashes replaced (regex requires `"architecture"` quoted-string-segment). Verified at design-time: `_R15_LITERAL_PATH_RE` requires the literal `REPO_ROOT` identifier + `/ "architecture" / "slices" / (?:"archive" / )?"slice-\d{3}-` sequence, so pure-prose English mentions ("the slice-034 archive-path reference at line 70" etc.) are safe by construction — but the design.md guard-rail prevents a careless rewrite from re-introducing a self-match that would force re-whitelisting and silently relapse R-15 to mitigating.
3. **`architecture/risk-register.md:250-263`** — flip R-15 `**Status**: mitigating` → `**Status**: retired`; add a `**Retired**: slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit (2026-05-21)` field-line under the existing `**Discovered**:` line; APPEND a new `**slice-057 part-(b) DONE (2026-05-21)**:` paragraph at the END of the section (after the existing "Why mitigating, not retired (post-slice-056)" paragraph — preserved verbatim as historical record per the slice-040 R-10 retirement precedent at `risk-register.md:180-195`). The new paragraph cites: (i) the literal repoint at `test_ptffd1_no_false_positive.py:69-72` (the PRE-EDIT 4-line parenthesized construction span — per /critique m1 ACCEPTED-FIXED, cite `:69-72` not `:70-71`; the post-edit 1-line form shifts subsequent lines up by 3, so propagating the slice-056-era `:70-71` citation into the new paragraph would be structurally stale on landing — the slice-056 paragraph at risk-register.md:259 keeps `:70-71` as historical record of its then-current state); (ii) the whitelist shrink to `set()`; (iii) the corpus-backstop `missing_whitelist == set()` assertion as the structural witness; (iv) META-1 enforcing-assertion verification at `tests/methodology/test_methodology_changelog.py:136` for no-changelog discharge (MEPD-1(b)); (v) slice-040/043/045 retirement-discharge precedent.
4. **`architecture/shippability.md`** — add row #57 `slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit` citing R-15 retirement-part-(b) discharge mechanism (BCR-1-traceability-axis pin discipline per slice-054 /critique-review M-add-1 → slice-056 row-#56 precedent). The pinned pytest command runs `test_no_new_archive_fragile_literals_in_methodology_corpus` (the durable forever-pin) AND `test_slice034_prose_test_function_is_not_false_positive` (the helper resolution post-retrofit) AND the new `test_shippability_row_57_present_and_cites_r15` (the consumer-propagation pin for the row itself).

Plus one new test in `tests/methodology/test_methodology_changelog.py` (added at the end of the file, mirroring slice-056's `test_shippability_row_56_present_and_cites_r15` at L3768 verbatim modulo the row number / slice-name string):

5. **`tests/methodology/test_methodology_changelog.py` (new function at end)** — `test_shippability_row_57_present_and_cites_r15()`. Asserts `| 57 | slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit` substring in `architecture/shippability.md` AND `R-15` substring in catalog. Structural twin of `test_shippability_row_56_present_and_cites_r15` (L3768-3806). Per the slice-054 /critique-review M-add-1 BCR-1-traceability-axis pin discipline applied analogously to risk-register-driven slices (slice-056 design.md L23/L185 precedent).

## What's reused

- `tests/methodology/conftest.py::_resolve_slice_dir(slice_number: int) -> Path` — the slice-056 helper. Module-globals binding semantics (reads `REPO_ROOT` at call-time) means it works under both normal repo execution and `monkeypatch.setattr` tmp-vault tests. Active-glob-first, archive-glob-fallback resolution semantics are exactly what AC1+AC2 need: `_resolve_slice_dir(34)` returns the archived `architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/` directory.
- `tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus` — the slice-056 corpus class-closure backstop. After this slice, the whitelist is `set()`; the `unexpected = matches - whitelist` assertion becomes "no R-15-class literals are allowed anywhere in `tests/methodology/*.py`" (the strongest possible form of the forever-invariant); the `missing_whitelist = whitelist - matches` assertion is trivially true under `set()` and stays as a regression-tripwire if a future maintainer adds a stale whitelist entry.
- `tests/methodology/test_ptffd1_no_false_positive.py::test_slice034_prose_test_function_is_not_false_positive` — the slice-037 PTFFD-1 AC3 corpus-regression test (its three semantic invariants — file-exists, `(full existing module` substring, `is_checkable_function_name` rejection — are preserved verbatim post-retrofit).
- `tests/methodology/test_methodology_changelog.py::test_shippability_row_56_present_and_cites_r15` (L3768-3806) — direct structural template for the new `test_shippability_row_57_…` function.
- `architecture/risk-register.md:180-195` — slice-040 R-10 retirement precedent (preserve historical prose, append new event paragraph, retain `**Discovered**:` line, add `**Retired**:` line, flip `**Status**:` field).
- `architecture/risk-register.md:116-160` and `:197-212` — slice-043 R-6 and slice-045 R-11 retirement precedents (no-changelog / no-ADR / no-VERSION-bump classification corroboration).
- `tools/risk_register_audit.py` — RR-1 audit (re-runs clean post-status-flip; `--filter-status retired` count increases by 1).
- `architecture/shippability.md` — slice-050 row #50 / slice-054 row #54 / slice-055 row #55 / slice-056 row #56 layout precedent for the new row #57 (5-column shape: `| NNN | slice-name | description | machine_cmd | sla | interp_template |`).

## Components touched

This slice touches no source-code components. It touches four vault / test files (enumerated above) and one risk-register entry. No `tools/*.py`, no `skills/*/SKILL.md`, no `agents/*.md`, no `methodology-changelog.md`, no `VERSION`, no `plugin.yaml`, no `~/.claude/` installed-leg surface.

Therefore no OSDG-1 / mini-CAD / CAD-1 drift-guard sync is required, no PMI-1 bump is required, no MCFS-1 / AVFS-1 forward-sync gate fires.

### `tests/methodology/test_ptffd1_no_false_positive.py` (modified)
- **Responsibility**: PTFFD-1 AC3 corpus regression — the function-level test-path discriminator must reject every NON-identifier `Test function` prose value across the archived brief corpus (slice-034's `(full existing module — non-regression)` row is the named seed).
- **Lives at**: `tests/methodology/test_ptffd1_no_false_positive.py:61-79` (one function `test_slice034_prose_test_function_is_not_false_positive`).
- **Key interactions**: imports `REPO_ROOT` + (NEW) `_resolve_slice_dir` from `tests.methodology.conftest`; imports `is_checkable_function_name` from `tools._pyfn`; reads `architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/mission-brief.md` via the helper.
- **Edit shape**: 1-line import addition + 3-line literal-RHS replacement (from 4-line `slice034 = (\n    REPO_ROOT / ... / "mission-brief.md"\n)` parenthesized multi-line construction to a 1-line `slice034 = _resolve_slice_dir(34) / "mission-brief.md"`).

### `tests/methodology/test_resolve_slice_dir.py` (modified)
- **Responsibility**: pin the slice-056 `_resolve_slice_dir` helper invariants + the M-add-2 corpus class-closure backstop.
- **Lives at**: `tests/methodology/test_resolve_slice_dir.py:214-220` (the `_R15_CORPUS_WHITELIST` constant) + `:286-293` (the `missing_whitelist` assertion's diagnostic message — preserved verbatim).
- **Key interactions**: this slice modifies only the constant; no test-function body changes; no helper-import changes. The `_R15_LITERAL_PATH_RE` regex (`:226-228`) is unchanged.
- **Edit shape**: 6-line constant block (the `{ ... }` set literal with one entry + 3-line inline comment) shrinks to a 1-line `_R15_CORPUS_WHITELIST: set[tuple[str, int]] = set()` declaration. The preceding 11-line comment block (`:203-213`) is rewritten in-place from "deferral surface" framing to "retirement-discharge witness" framing.

### `architecture/risk-register.md` (modified)
- **Responsibility**: vault risk register — the single source of truth for open / mitigating / retired / accepted risks.
- **Lives at**: lines 250-263 (R-15 section).
- **Edit shape**: 1-line `**Status**:` field flip (mitigating → retired) + 1-line `**Retired**:` field insertion + ~10-line retirement paragraph appended at section end. Existing prose (Discovered, original Mitigation paragraph, slice-056 part-(a) DONE paragraph, "Why mitigating, not retired (post-slice-056)" paragraph, "Why not Critic-promotion" paragraph) is preserved verbatim as historical record (slice-040 R-10 precedent).

### `architecture/shippability.md` (modified — new row)
- **Responsibility**: shippability catalog — single source of truth for "must never silently regress" claims; consumed by `tools/shippability_runner.py` at /validate-slice Step 5.5 + /build-slice Step 6.
- **Lives at**: append one new `| 57 | slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit | …` row at the end of the catalog table (after the slice-056 row at `:66`).
- **Edit shape**: 1 new row, 5-column shape per the slice-050+ layout precedent (`| NNN | slice-name | description-with-regression-clause | pytest-command-with-absolute-interp | <Nsec | interp-template-with-<interp>-placeholder |`). The description MUST cite R-15 (BCR-1-traceability-axis pin discipline). The pinned pytest command MUST run at least `test_no_new_archive_fragile_literals_in_methodology_corpus` (the forever-pin), `test_slice034_prose_test_function_is_not_false_positive` (the helper resolution), and `test_shippability_row_57_present_and_cites_r15` (the row's own consumer-propagation pin).

### `tests/methodology/test_methodology_changelog.py` (modified — append one function)
- **Responsibility**: methodology-changelog + shippability + cross-cutting structural pins.
- **Lives at**: append `test_shippability_row_57_present_and_cites_r15` at end of file (current end is L3806 after the slice-056 row-#56 function).
- **Edit shape**: copy-paste the slice-056 function at L3768-3806 verbatim, substitute `56` → `57`, `slice-056-fix-bcr1-round-trip-test-archive-paths` → `slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit`, and rewrite the docstring framing from "part-(a)" → "part-(b)" + "mitigation" → "retirement" while preserving the slice-054 /critique-review M-add-1 BCR-1-traceability-axis pin discipline citation. The two `assert` statements are structurally identical (substring presence of the row marker + the `R-15` token).

## Contracts added or changed

No new contracts. No endpoints. No events. No public Python APIs added or modified. The `_resolve_slice_dir` helper is reused, not modified.

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces no new modules — only edits to 4 existing vault / test files + 1 new test function appended to an existing test module. Zero-row matrix per the SKILL.md guidance ("If this slice introduces no new modules … keep the header + separator only — the audit treats zero-row matrices as clean").

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

None. This slice mints no new ADRs. The substantive design decisions are inherited from prior slices:

- The `_resolve_slice_dir` helper + M-add-2 corpus class-closure backstop mechanism — slice-056 (no new ADR; integrated into the slice-056 fix).
- The slice-040 retirement-precedent shape (preserve historical prose, append event paragraph, flip Status, add Retired line) — slice-040 (no ADR; conformance class).
- The BCR-1-traceability-axis pin discipline (row cites R-15 / slice-NNN as a structural pin) — slice-054 /critique-review M-add-1 → slice-056 design.md L23/L185 (no new ADR; codified at-instance into the SCPD-1 family).
- The MEPD-1(b) discharge-by-name-against-META-1 verification — ADR-041 (slice-039; not re-locked here).

The no-ADR classification follows slice-040 R-10 retirement (no ADR), slice-043 R-6 retirement (no ADR, no methodology-changelog entry), slice-045 R-11 born-retired (no ADR, no methodology-changelog entry), and slice-056 R-15 part-(a) (no ADR, no methodology-changelog entry, voluntary-restraint discipline N≥6 cumulative).

## Authorization model for this slice

N/A — no runtime authorization surface. The slice touches only repo-local vault / test files; no auth, no users, no tokens, no API.

## Error model for this slice

The slice introduces no new error paths. The relevant error paths it RELIES ON (without modifying) are:

- `_resolve_slice_dir(34)` raises `AssertionError("neither active nor archive resolution succeeded for slice-034; tried architecture/slices/slice-034-*, architecture/slices/archive/slice-034-*")` if the slice-034 archive directory is missing or renamed away from the `slice-034-*` glob pattern. Caught at the `test_slice034_prose_test_function_is_not_false_positive` test-call site as a hard test failure (not silently skipped — surfaces as `pytest FAILED` with the diagnostic message). The slice-034 archive directory is verified-present at design-time (`architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/`).
- `_resolve_slice_dir(34)` raises `ValueError` only on non-int / bool / out-of-range inputs (`34` is none of these); not reachable for this slice's call-site.
- `test_no_new_archive_fragile_literals_in_methodology_corpus`'s two assertions:
  - `unexpected = matches - whitelist != set()` — FAIL with diagnostic naming offending file + line. After this slice, `unexpected == set()` iff no NEW R-15-class literals have been added to `tests/methodology/*.py` outside `_R15_CORPUS_WHITELIST` (which is now `set()`). This is the durable forever-invariant.
  - `missing_whitelist = whitelist - matches != set()` — FAIL with diagnostic "The whitelist has shrunk — remove these entries. If the whitelist is now empty, R-15 part-(b) is structurally satisfied; consider transitioning R-15 to retired in architecture/risk-register.md." After this slice, `missing_whitelist == set()` trivially under an empty whitelist; the assertion stays as a regression-tripwire against future stale-whitelist-entry additions.

## Step 6 audit-impact analysis

This slice's effect on each Step 6 audit is enumerated to make the pre-finish gate execution predictable:

- **BC-1** (`build_checks_audit`): no `## Build-checks` section needed (no new build-checks rules); audit re-runs clean.
- **BCI-1** (`build_checks_integrity_audit`): no new fixtures; audit re-runs clean.
- **RR-1** (`risk_register_audit`): R-15 status flips mitigating → retired; `--filter-status retired` count increases by 1 (8 → 9); audit re-runs clean (no structural changes to the entry shape — Status / Likelihood / Impact / Reversibility / Discovered / Retired field-lines all present + parseable).
- **CAD-1** (`critique_agent_drift_audit`): no `agents/critique.md` edits; audit re-runs clean.
- **PMI-1** (`plugin_manifest_audit`): no `plugin.yaml` edits, no new skill/agent/tool files; audit re-runs clean.
- **INST-1** (`install_audit`): no new tool modules; audit re-runs clean.
- **MCFS-1** (`methodology_changelog_forward_sync`): no `methodology-changelog.md` edits; audit re-runs clean.
- **AVFS-1** (`ai_sdlc_version_forward_sync`): no `VERSION` edits; audit re-runs clean.
- **PVFS-1** (pyproject version pin via pytest): no `VERSION` / `pyproject.toml` edits; assertion re-runs clean.
- **OSDG-1** (per-skill drift guards): no `skills/*/SKILL.md` edits; all guarded skills (`slice`, `build-slice`, `commit-slice`, `query-design`, `critique`, `diagnose`, `triage`, `adopt`, `reflect`) re-run clean.
- **DR-1 structural** (`critique_review_audit`): no `critique-review.md` written yet (this slice has `critic-required: true` so DR-1 WILL run at /critique-review post-/critique); audit runs clean post-critique-review.
- **TF-1 strict-pre-finish** (`test_first_audit`): `Test-first: false` in mission brief; audit skips (per TF-1 opt-in semantics).
- **WS-1** (`walking_skeleton_audit`): `Walking-skeleton: false`; audit skips.
- **ETC-1** (`exploratory_charter_audit`): `Exploratory-charter: false`; audit skips.
- **WIRE-1** (`wiring_matrix_audit`): zero-row matrix above; audit treats as clean.
- **CSP-1** (`cross_spec_parity_audit`): no spec-surface edits; audit re-runs clean.
- **SUP-1** (`supersede_audit`): no new ADRs / no supersession events; audit re-runs clean.
- **LINT-MOCK-1/2/3** (`mock_budget_lint`): no code edits; audit re-runs clean.
- **STP-1** (`state_transition_pin_audit`):
  - **Sub-form A** (SKILL.md-prose-repoint): no SKILL.md edits; clean.
  - **Sub-form B** (risk-status-stale, `test_r_(\d+)_(stays|remains|is)_(open|mitigating|retired|accepted)` fn-name vs live register): grep verified at design-time — no `test_r_15_…` function exists anywhere in `tests/methodology/` (only `test_r_10_is_retired` exists as a string literal at `test_state_transition_pin_audit.py:343`, which is a regex-parser test fixture, NOT a `def test_r_10_…` function). Therefore Sub-form B has nothing to re-validate against the R-15 status change; clean.
- **SCMD-1** + **PTFCD-1** (shippability machine-cmd discipline + path resolvability): new row #57's `Command` cell uses absolute Python interp + module path + `--no-header -q`; selectors resolve to existing test files / functions post-edit; pre-gates clean.
- **BRANCH-1** (`branch_workflow_audit`): the /build-slice branch creation event is checked at Step 6; the canonical `slice/057-retire-r15-via-slice-034-resolve-slice-dir-retrofit` branch name will be created by /build-slice Step 0 per BRANCH-1.
- **UTF8-STDOUT-1** (`utf8_stdout_regression`): no tool CLI edits; audit re-runs clean.
- **CRP-1** (`critique_review_prerequisite_audit`): critique-review.md prerequisite met post-/critique + /critique-review; audit clean.
- **PCA-1** (`pipeline_chain_audit`): no SKILL.md `## Pipeline position` edits; chain intact; audit clean.
- **Shippability runner** (`shippability_runner`): new row #57 runs the pinned pytest command; expected exit 0; runner-level 57/57 PASS at /validate-slice.

## R-15 retirement-discharge classification (MEPD-1(b) discharge mechanics)

Per MEPD-1 / ADR-041, every methodology-surface behavior change OR rule-state transition MUST either (a) carry a methodology-changelog entry + VERSION bump + ADR, OR (b) discharge MEPD-1(b) by name with explicit verification against the real META-1 enforcing assertion (`tests/methodology/test_methodology_changelog.py:136`'s `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", changelog, flags=re.MULTILINE)` + `Rule reference` substring check on each split section).

This slice elects (b) — no methodology-changelog entry, no VERSION bump, no new ADR — on the classification ground that:

1. **Rule already minted at slice-056** (per /critique m3 ACCEPTED-FIXED — tightened terminology: tests are TEST surfaces that PIN methodology, NOT methodology surfaces in the MEPD-1 / Dim-7 enumeration `skills/*/SKILL.md` + `agents/*.md` + `tools/**/*.py` + `methodology-changelog.md` + in-house audits): R-15 itself (as a risk-register entry at `architecture/risk-register.md:250-263`), the `_resolve_slice_dir(NNN)` helper (in `tests/methodology/conftest.py:20-108` — a test-shared utility, not a `tools/*.py` audit), AND the M-add-2 corpus class-closure backstop test (in `tests/methodology/test_resolve_slice_dir.py:231-293` — a pinning test, not a methodology-surface tool) are all already in the repo as of slice-056; no NEW methodology-surface rule is minted here. (The slice-056 fix was itself classified as "mints no new rule + no ADR per voluntary-restraint discipline slice-037/046/050/052/055/056 N≥6 cumulative".) The decisive MEPD-1(b) discharge argument is item 3 below (META-1 vacuous satisfaction), which carries the discharge regardless of how "methodology surface" is parsed.
2. **State transition is parametric within an already-shipped rule**: R-15's mitigating → retired transition does not add a new methodology contract; it discharges the slice-056-pre-engineered two-part retirement gate (slice-056 explicitly designed the corpus-backstop whitelist-shrinkage mechanism as the structural witness for part-(b) per /critique-review M-add-2 ACCEPTED-FIXED).
3. **META-1 assertion vacuously satisfied**: the META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` splits the changelog on `^## v\S+ — \d{4}-\d{2}-\d{2}` and asserts every split section carries a Rule reference. Since this slice adds zero new `## v…` sections, the assertion is vacuously satisfied — there is no new section that could fail the Rule-reference check. Verified at design-time: `grep -c "^## v" methodology-changelog.md` returns the same count before and after this slice.
4. **Precedent corroboration**: slice-040 retired R-10 with no methodology-changelog entry / no ADR / no VERSION bump under the same conformance-fix / retirement-discharge class, citing META-1 verification by name. slice-043 retired R-6 under the same class. slice-045 born-retired R-11 under the same class. slice-056 itself shipped its R-15 part-(a) fix under the same class (no rule, no ADR, no version). N≥4 same-class precedent.

The build-log MUST cite this MEPD-1(b) discharge explicitly at the no-changelog decision point (per the slice-040 / slice-043 / slice-045 / slice-056 precedent — "discharged by name vs the real META-1 assertion at `tests/methodology/test_methodology_changelog.py:136`, NOT precedent analogy alone").

## Test plan additions

This slice adds exactly one new test function (`test_shippability_row_57_present_and_cites_r15` in `tests/methodology/test_methodology_changelog.py`) — the row-#57 consumer-propagation pin. Its FAIL→PASS contrast:

- **Pre-edit FAIL state**: row #57 does not exist in `architecture/shippability.md` → first assertion FAILs with "missing catalog row #57 for slice-057".
- **Post-edit PASS state**: row #57 added → both assertions pass (substring presence of the row marker + the `R-15` token).

The genuine contrast is provable by running the new test against the pre-edit catalog (will FAIL) vs the post-edit catalog (will PASS). Test-first opt-out (per mission brief `Test-first: false`) is appropriate because:

- The three semantic invariants of `test_slice034_prose_test_function_is_not_false_positive` (AC2) are PRE-EXISTING and STAY GREEN — no new test needs to be authored test-first to pin them.
- The corpus-backstop assertion (AC3) is PRE-EXISTING and stays GREEN under the whitelist shrink — no new test needs to be authored test-first to pin it.
- The RR-1 audit (AC4) is PRE-EXISTING and stays GREEN under the status flip.
- The new row-#57 traceability pin (AC5) is a structural one-shot pin authored AFTER the row is added, not test-first (the slice-056 row-#56 precedent at `test_methodology_changelog.py:3768` was added the same way).

## Validation strategy

Per AC verification plan in mission brief. The mid-slice smoke gate at /build-slice ~50% runs the **three** affected tests (AC2 + AC3 + AC5 row-#57 pin per /critique M1 ACCEPTED-FIXED — post-fix harmonization under TPHD-1 sub-mode (b)) in a single pytest invocation; all three must PASS. Pre-finish gate runs the full Step 6 audit suite + the explicit row-#57-pin checkbox (also per /critique M1) + `shippability_runner` at /validate-slice for the 57/57 catalog runner exit-0.

## Out of scope (re-stated from mission brief for adversarial-review parity)

- No methodology-changelog entry / no VERSION bump / no ADR.
- No changes to slice-034's archived contents.
- No retroactive sweep of other R-15-class literals (none exist post-slice-056 except the slice-034 instance; corpus backstop pre-validated).
- No BFRD-1 `/repro` prelude (this is not a bug-fix slice).
- No OSDG-1 extension to `/slice-candidates` (R-13; deferred to a separate slice).
