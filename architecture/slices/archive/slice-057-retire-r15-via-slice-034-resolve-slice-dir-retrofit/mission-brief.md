# Slice 057: retire-r15-via-slice-034-resolve-slice-dir-retrofit

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-15 (Archive-aware vault-test discipline — `mitigating` → `retired`)
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Discharge R-15 part-(b) — the second half of slice-056's two-part R-15 retirement gate — by retrofitting the one remaining R-15-class archive-fragile literal-path-RHS in `tests/methodology/test_ptffd1_no_false_positive.py:69-72` to use the `_resolve_slice_dir(34)` helper shipped in slice-056. Removing that literal empties slice-056's `_R15_CORPUS_WHITELIST` to `∅`, at which point the corpus class-closure backstop's `missing_whitelist` diagnostic message ("If the whitelist is now empty, R-15 part-(b) is structurally satisfied; consider transitioning R-15 to retired") becomes the structural witness — and R-15 escalates from `mitigating` to `retired` with citation. This is the slice slice-056 was explicitly engineered to invite (per the M-add-2 ACCEPTED-FIXED whitelist-shrinkage mechanism).

## Acceptance criteria

1. `tests/methodology/test_ptffd1_no_false_positive.py:69-72` is repointed: the multi-line literal `REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"` is replaced with `_resolve_slice_dir(34) / "mission-brief.md"`, with `_resolve_slice_dir` imported from `tests.methodology.conftest` at the top of the file alongside the existing `REPO_ROOT` import.
2. The PTFFD-1 corpus regression test `test_slice034_prose_test_function_is_not_false_positive` continues to PASS post-retrofit, preserving all three semantic invariants (`slice034.is_file()`, `"(full existing module" in text`, and `not is_checkable_function_name("(full existing module — non-regression)")`).
3. `_R15_CORPUS_WHITELIST` in `tests/methodology/test_resolve_slice_dir.py:214-220` shrinks to `set()` (the empty set); `test_no_new_archive_fragile_literals_in_methodology_corpus` PASSes with both `unexpected = matches - whitelist == set()` AND `missing_whitelist = whitelist - matches == set()` — the latter is now trivially true under an empty whitelist, witnessing the structural retirement gate.
4. `architecture/risk-register.md` R-15 entry (lines 250-263) is updated: the `**Status**: mitigating` field-line is flipped to `**Status**: retired`, a `**Retired**: slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit (YYYY-MM-DD)` field-line is added, and a brief retirement paragraph is appended citing both part-(a) (slice-056) and part-(b) (this slice) gates discharged AND the corpus-backstop whitelist=∅ as the structural witness. RR-1 audit (`tools/risk_register_audit.py`) stays clean.
5. `architecture/shippability.md` gains row #57 capturing the corpus-class-closure backstop's whitelist-empty invariant as a forever pin (the row's `Command` cell pins `test_no_new_archive_fragile_literals_in_methodology_corpus` + `test_slice034_prose_test_function_is_not_false_positive` + the NEW `test_shippability_row_57_present_and_cites_r15` per the slice-054 → slice-056 BCR-1-traceability-axis pin discipline applied analogously to risk-register-driven slices) — AND a new test function `test_shippability_row_57_present_and_cites_r15()` is appended at end of `tests/methodology/test_methodology_changelog.py` (structural twin of slice-056's `test_shippability_row_56_present_and_cites_r15` at L3768-3806; asserts `| 57 | slice-057-retire-r15-via-slice-034-resolve-slice-dir-retrofit` substring AND `R-15` substring in catalog). SCMD-1, PTFCD-1, and the shippability runner all stay clean (`run_catalog` exit 0 on the catalog at slice end); the new test PASSes (per /critique-review m-add-1 ACCEPTED-FIXED — AC5 now binds the new pinning test by name, not just by inference via the pre-finish checkbox).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Literal repointed to `_resolve_slice_dir(34)` | `git diff tests/methodology/test_ptffd1_no_false_positive.py` shows the multi-line literal removed AND `_resolve_slice_dir(34) / "mission-brief.md"` added; `grep -n _resolve_slice_dir tests/methodology/test_ptffd1_no_false_positive.py` returns the import + call-site |
| 2 | PTFFD-1 corpus regression PASSes | `& $PY -m pytest tests/methodology/test_ptffd1_no_false_positive.py::test_slice034_prose_test_function_is_not_false_positive -v` exits 0 |
| 3 | Whitelist empty + corpus class-closure clean | `grep -n "_R15_CORPUS_WHITELIST" tests/methodology/test_resolve_slice_dir.py` shows `_R15_CORPUS_WHITELIST: set[tuple[str, int]] = set()`; `& $PY -m pytest tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus -v` exits 0 |
| 4 | R-15 flipped to retired + RR-1 clean | `& $PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status retired --sort score` includes R-15; `--filter-status mitigating` no longer includes R-15; full RR-1 audit (`& $PY -m tools.risk_register_audit architecture/risk-register.md`) exits 0 |
| 5 | Shippability row #57 + runner clean | `grep -n "^| 57 " architecture/shippability.md` returns one row citing the whitelist-empty pin; `& $PY -m tools.shippability_path_audit architecture/shippability.md` exits 0; `& $PY -m tools.shippability_runner architecture/shippability.md` exits 0 |

## Must-not-defer

- [ ] The `_resolve_slice_dir(34)` call MUST resolve to the archived `slice-034-fix-tf1-audit-field-line-regex/` directory (not raise AssertionError) — verified by the PTFFD-1 corpus test continuing to PASS (AC2). If the slice-034 archive directory is somehow not present or is renamed in a way the helper's active-then-archive glob doesn't cover, this surfaces as a hard test failure, not a silent skip.
- [ ] The R-15 status flip MUST be accompanied by a retirement paragraph that names BOTH gate parts (part-(a) slice-056 + part-(b) this slice) AND the corpus-backstop whitelist=∅ structural witness, per the precedent that retirement-discharge entries explain WHY the gate is now met (slice-040 R-10 / slice-043 R-6 / slice-045 R-11 retirement-rationale precedent).
- [ ] The shippability row #57 MUST cite the empty-whitelist invariant as the durable structural pin (not just "the slice-034 retrofit happened") — the forever invariant is "no new R-15-class literals land in `tests/methodology/*.py`", which the corpus backstop's `unexpected == set()` assertion enforces; the whitelist=∅ state is the strongest possible form of that invariant.
- [ ] The corpus-backstop test's `missing_whitelist` diagnostic message ("If the whitelist is now empty, R-15 part-(b) is structurally satisfied; consider transitioning R-15 to retired") MUST remain verbatim in `tests/methodology/test_resolve_slice_dir.py:286-294` so future archive-fragile cleanups inherit the same structural prompt. This is a slice-056 design surface; do not erase it.

## Out of scope

- New `methodology-changelog.md` entry / new `## v0.N.0` header / VERSION bump / new ADR. This slice is a pure conformance / retirement-discharge class — the methodology was already extended at slice-056 (R-15 mitigation + helper + corpus backstop); no new rule is minted here. Precedent: slice-040 (R-10 retired), slice-043 (R-6 retired), slice-045 (R-11 born-retired) all shipped no-changelog under the "conformance / retirement-discharge class" classification with MEPD-1(b) discharged by name vs the real META-1 `^## v…`-split assertion at `tests/methodology/test_methodology_changelog.py:136`. MEPD-1(b) discharge MUST be cited explicitly in `build-log.md` at the no-changelog decision point.
- Any change to slice-034's archived contents (`architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/*`) — read-only target; the retrofit reads it through the helper, never modifies it.
- Any retroactive sweep of OTHER R-15-class literals in `tests/methodology/*.py` — the corpus backstop's current whitelist is N=1 (only the `test_ptffd1_no_false_positive.py:70` instance); slice-056's M-add-2 `re.finditer(text)` whole-file regex with line-number-from-offset has already scanned the full corpus. Empirically verify pre-implementation via the corpus backstop's own scan that no new entries have landed between slice-056 ship and slice-057 start; if N has grown to >1, scope re-evaluation (separate slice for the new entries).
- BFRD-1 `/repro` prelude — this is NOT a bug-fix slice (name verb is `retire` not `fix`; risk-class is discipline-propagation not customer-defect; the existing PTFFD-1 corpus test PASSes today and the retrofit preserves that PASS). Mode (a) name-shape detection: zero match (no `fix-*` / `*-fix` / `bugfix-*` / `hotfix-*` / `defect-*` / `repair-*` / `patch-*` / `harden-*-bug` token). Mode (b) candidate-source signal: R-15 is a latent-fragility-class discipline risk, not a bug-class entry; the slice-056 reflection.md explicitly nominates this slice as a "retrofit" carrier, not a fix-the-defect carrier.
- Extending OSDG-1 to `/slice-candidates` (R-13) — separate next-slice candidate, ranked #2 in the slice-057 selection pass; deliberately deferred to a dedicated slice per the slice-049/051 drift-guard-addition-is-its-own-slice precedent.

## Dependencies

- Prior slices: [[slice-056-fix-bcr1-round-trip-test-archive-paths]] — supplies the `_resolve_slice_dir(slice_number: int) -> Path` helper at `tests/methodology/conftest.py:20-…`, the corpus class-closure backstop test at `tests/methodology/test_resolve_slice_dir.py:231-…`, and the `_R15_CORPUS_WHITELIST` mechanism at `:214-218` whose shrinkage is the M-add-2 structural retirement gate.
- Prior slices: [[slice-034-fix-tf1-audit-field-line-regex]] — archived target; its mission-brief.md at `architecture/slices/archive/slice-034-fix-tf1-audit-field-line-regex/mission-brief.md` is the resolved-via-helper path; carries the prose `Test function` value `(full existing module — non-regression)` that the PTFFD-1 corpus test asserts the discriminator rejects.
- Prior slices: [[slice-037]] — PTFFD-1 minting slice; `test_slice034_prose_test_function_is_not_false_positive` is its AC3 corpus regression-test author.
- Vault refs: [[risk-register#R-15]] — status flip target; lines 250-263.
- Vault refs: [[architecture/shippability.md]] — row #57 add target.
- Risk register: [[risk-register#R-15]] — directly retired by this slice.

## Mid-slice smoke gate

At ~50% of build (after the retrofit + whitelist shrink + shippability row #57 insert + new test_shippability_row_57 function appended, before R-15 status flip):

```powershell
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m pytest `
  tests/methodology/test_ptffd1_no_false_positive.py::test_slice034_prose_test_function_is_not_false_positive `
  tests/methodology/test_resolve_slice_dir.py::test_no_new_archive_fragile_literals_in_methodology_corpus `
  tests/methodology/test_methodology_changelog.py::test_shippability_row_57_present_and_cites_r15 `
  -v
```

Expected: all three PASS (per /critique M1 ACCEPTED-FIXED — the new shippability row-#57 traceability pin runs at the same 50% checkpoint it's authored at, anchoring AC5's verification path). If `test_no_new_archive_fragile_literals_in_methodology_corpus` FAILs with "whitelist has shrunk — remove these entries" → that's actually the *intended* structural witness firing (the whitelist still holds the slice-034 entry but the literal is gone); shrink the whitelist to `set()` and re-run. If `test_slice034_prose_test_function_is_not_false_positive` FAILs with `slice-034 mission-brief.md missing` → `_resolve_slice_dir(34)` couldn't find the archived directory; investigate (most likely cause: slice-034 archive folder name doesn't match `slice-034-*`). If `test_shippability_row_57_present_and_cites_r15` FAILs → the row #57 insert hasn't landed yet OR doesn't cite R-15; add/fix the row before re-running.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in `validation.md`
- [ ] Must-not-defer list fully addressed (all 4 items)
- [ ] R-15 `**Status**:` field is `retired` in `architecture/risk-register.md`; retirement-rationale paragraph cites both gate parts + whitelist=∅ witness
- [ ] `_R15_CORPUS_WHITELIST` is literally `set()` in `tests/methodology/test_resolve_slice_dir.py` (not `{}` which is a dict literal — must be the explicit `set()` form for empty-set unambiguity)
- [ ] `architecture/shippability.md` row #57 present, citing the whitelist-empty invariant
- [ ] `tests/methodology/test_methodology_changelog.py::test_shippability_row_57_present_and_cites_r15` PASSes (per /critique M1 ACCEPTED-FIXED — explicit anchor for AC5's verification path; the new row-#57 BCR-1-traceability-axis pin must fire at pre-finish, not just be assumed-present)
- [ ] `/drift-check` clean (no vault-vs-code divergence introduced)
- [ ] All Step 6 audits clean: BC-1, BCI-1, RR-1, CAD-1, PMI-1, INST-1, DR-1 structural, TF-1 strict-pre-finish, WS-1, WIRE-1, ETC-1, CSP-1, SUP-1, LINT-MOCK-1/2/3, STP-1 (Sub-form A SKILL.md-prose-repoint + Sub-form B risk-status-stale — Sub-form B SHOULD fire on R-15's status change as a NORMAL expected event per slice-040/043 precedent; verify it passes after status flip), SCMD-1, PTFCD-1, BRANCH-1, UTF8-STDOUT-1, CRP-1, PCA-1, AVFS-1, MCFS-1
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] BFRD-1 detection re-confirmed not-triggered (name + source-class both pass the not-a-bug-fix check)
- [ ] MEPD-1(b) discharged-by-name in build-log.md at the no-changelog decision point (cites `^## v…`-split META-1 assertion at `tests/methodology/test_methodology_changelog.py:136` precedent; cites slice-040/043/045 no-changelog precedent)

## Pipeline position

- **predecessor**: `/reflect` (slice-056 completed; loop entry from /slice candidate selection)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: candidate is settled (user picked #1 from the ranked recommendation at /slice Step 3); mission brief + milestone.md written; auto-invoke `/design-slice` via the Skill tool without waiting for the user.
- **user-input gates** (halt auto-advance — surface to user, resume only on explicit user action):
  - Candidate selection — DISCHARGED (user picked #1 explicitly via structured options at /slice Step 3).
  - BFRD-1 bug-fix confirm gate — NOT TRIGGERED (this is not a bug-fix slice; mode (a) name-shape: zero match; mode (b) candidate-source: R-15 is discipline-class not bug-class).

> Per PCA-1 (methodology-changelog.md v0.41.0). The `## Pre-finish gate` section above is the human-readable companion; this block is the machine-actionable auto-advance directive read at skill-completion.
