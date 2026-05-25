# Slice 056: fix-bcr1-round-trip-test-archive-paths

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-15 (archive-aware vault-test discipline; class signal **N=2** as of /critique-time corpus re-scan, see design.md L170 — the second instance is `tests/methodology/test_ptffd1_no_false_positive.py:70` which is already on the archive side and not breaking today, latent under slice-034 rename pressure only; per /critique M1, R-15 STAYS `mitigating` after slice-056 ship (part-(a) of risk-register.md:259 retirement-gate DONE; part-(b) future-use evidence pending the next slice that demonstrably uses `_resolve_slice_dir`))
**Test-first**: true  <!-- per TF-1 — BFRD-1 failing repro pre-exists; new helper tests written before helper -->
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant` (authored by slice-054 as the BCR-1 first end-to-end dogfood input-axis invariant pin) currently FAILS on master because its hardcoded `SLICE_054_DIR = REPO_ROOT / "architecture" / "slices" / "slice-054-fix-pyproject-toml-version-drift"` resolves to a path that no longer exists — slice-054 was archived by `/reflect` to `architecture/slices/archive/slice-054-fix-pyproject-toml-version-drift/`. R-15 (slice-055-discovered, mitigating, low-band) names the class: **a slice authoring tests pinning invariants on its own vault files breaks at the next /reflect's archival**.

Slice-056 (a) repairs the slice-054 stale path AND (b) introduces a reusable `_resolve_slice_dir(NNN)` helper that tries active then archive locations + raises a clear diagnostic if neither exists, so the next BCR-1-closing slice that pins its own vault invariants doesn't repeat the trap. Per slice-055 reflection's `Deferred` section + `Lessons for next slice`, this is the explicit slice-056 nomination.

## Acceptance criteria

1. `tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant` PASSES post-fix (BFRD-1 failing-repro-now-passes invariant).
2. A reusable `_resolve_slice_dir(slice_number: int) -> Path` helper exists in `tests/methodology/conftest.py` (alongside `REPO_ROOT`) that tries `architecture/slices/slice-NNN-*/` first, falls back to `architecture/slices/archive/slice-NNN-*/`, and raises `AssertionError` with a clear "neither active nor archive resolution succeeded for slice-NNN; tried architecture/slices/slice-NNN-*, architecture/slices/archive/slice-NNN-*" message if neither matches. **Signature is single-arg `(slice_number: int) -> Path`** (per /critique M2 ACCEPTED-FIXED); the helper reads `REPO_ROOT` at function-call-time via module-globals (Python's natural binding) so `monkeypatch.setattr("tests.methodology.conftest.REPO_ROOT", tmp_path)` works for AC4b. **Diagnostic-message format is platform-neutral** (per /critique m4 ACCEPTED-FIXED): glob patterns are formatted as raw forward-slash strings (`f"architecture/slices/slice-{n:03d}-*"`), not via `str(Path(...))`, so the AssertionError text is identical on Windows and POSIX.
3. The archive-fragile literal-path RHS (`REPO_ROOT / "architecture" / "slices" / "slice-054-..."`) is removed from `tests/methodology/test_bcr_1_round_trip_end_to_end.py` (per /critique m1 ACCEPTED-FIXED — wording clarified). Equivalent forms accepted: (a) the `SLICE_054_DIR` symbol removed entirely AND the helper called inline (`_resolve_slice_dir(54) / "mission-brief.md"`), OR (b) the symbol retained as `SLICE_054_DIR = _resolve_slice_dir(54)` for local-reference convenience. The structural pin asserts absence of the literal substring `REPO_ROOT / "architecture" / "slices" / "slice-054`, NOT absence of the `SLICE_054_DIR` symbol name.
4. Four regression tests for `_resolve_slice_dir(NNN)` + the R-15 class exist and PASS: (a) resolves an archived slice (e.g., 54 or 55), (b) resolves an active slice via a tmp-vault fixture, (c) raises `AssertionError` with the diagnostic when neither location matches an invented slice number, **(d) class-closure backstop (per /critique-review M-add-2 ACCEPTED-FIXED — `tests/methodology/*.py` carries NO new R-15-class archive-fragile literal-path-RHS beyond a known whitelist; when the whitelist shrinks to empty (after the slice-034 retrofit ships), the assertion structurally satisfies R-15's part-(b) retirement criterion without waiting for cross-slice observational evidence)**.
5. The shippability catalog adds row #56 citing slice-056 + R-15 (the BCR-1 traceability axis applied to risk-register-driven slices per slice-054 M-add-1); the row's Machine-cmd column invokes `tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant` AND the new `_resolve_slice_dir` regression tests, and PASSES under `tools/shippability_runner.py`. **Additionally** (per /critique m3 ACCEPTED-FIXED): shippability row #54 (which already cites the same BCR-1 test) PASS-flips from FAIL to PASS post-fix as a side effect — row #54's continued PASS is itself part of the regression contract; the shippability runner verifies both row #54 AND row #56 PASS at /validate-slice Step 5.5.

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. The slice-054 BFRD-1 test pre-exists as the AC1 failing repro; helper-test rows are written first (PENDING → WRITTEN-FAILING → PASSING).

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_bcr_1_round_trip_end_to_end.py | test_bcr_1_sc054_round_trip_inputs_invariant | PASSING |
| 2 | methodology | tests/methodology/test_resolve_slice_dir.py | test_helper_is_importable_from_conftest | PASSING |
| 3 | methodology | tests/methodology/test_resolve_slice_dir.py | test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir | PASSING |
| 4 | methodology | tests/methodology/test_resolve_slice_dir.py | test_resolves_archived_slice_054 | PASSING |
| 4 | methodology | tests/methodology/test_resolve_slice_dir.py | test_resolves_active_slice_via_tmp_vault | PASSING |
| 4 | methodology | tests/methodology/test_resolve_slice_dir.py | test_raises_assertion_with_diagnostic_when_neither_found | PASSING |
| 4 | methodology | tests/methodology/test_resolve_slice_dir.py | test_no_new_archive_fragile_literals_in_methodology_corpus | PASSING |
| 5 | methodology | tests/methodology/test_methodology_changelog.py | test_shippability_row_56_present_and_cites_r15 | PASSING |

(Status enum per slice-054 TF-1 build-time discovery: exact-match values only — no trailing prose in the Status cell. Annotations go in this Notes block instead. AC numbering per /critique-review M-add-1 ACCEPTED-FIXED — TF-1 `_AC_ITEM_RE = r"^\s*(\d+)\.\s+\S"` requires integer AC labels in the body; multi-row-per-AC is the canonical TF-1 shape, so the four sub-tests of AC4 all carry AC cell `4` and the prose retains the (a)/(b)/(c)/(d) lettering. Test-function names disambiguate the sub-branches.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | BFRD-1 failing repro now passes | `$PY -m pytest tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant -v` exits 0 (was exit 1 pre-fix; reproduced live on master 2026-05-21) |
| 2 | Helper exists in conftest | `python -c "from tests.methodology.conftest import _resolve_slice_dir; print(_resolve_slice_dir(54))"` prints the resolved archive path; helper signature is single-arg `(slice_number: int) -> Path` |
| 3 | Archive-fragile literal-path removed | `grep -F 'REPO_ROOT / "architecture" / "slices" / "slice-054' tests/methodology/test_bcr_1_round_trip_end_to_end.py` returns NO match (matches the helper-wrapped form `_resolve_slice_dir(54)` are fine; the audit asserts absence of the LITERAL substring of the archive-fragile RHS, not absence of the `SLICE_054_DIR` symbol name) |
| 4 | Helper regression tests + corpus backstop pass | `$PY -m pytest tests/methodology/test_resolve_slice_dir.py -v` reports 6 passed (helper-import + module-no-longer-hardcoded + 3 resolution cases + 1 corpus-backstop class-closure test); AND `$PY -m tools.test_first_audit architecture/slices/slice-056-fix-bcr1-round-trip-test-archive-paths --strict-pre-finish` exits 0 (AC#4 has 4 plan rows post-fix per /critique-review M-add-1) |
| 5 | Shippability row 56 passes under runner | `$PY -m tools.shippability_runner architecture/shippability.md` exits 0 with row 56 PASS; AND `grep -n "^| 56 " architecture/shippability.md` cites `slice-056-fix-bcr1-round-trip-test-archive-paths` + `R-15` |
| 5b | Shippability row 54 PASS-flipped post-fix (per /critique m3) | same runner invocation as row 5 — row #54 (which cites the same BCR-1 test) PASSed during the same run; pre-fix row #54 FAILed slice-055-innocently (reproduced live 2026-05-21); post-fix BOTH rows PASS |

## Must-not-defer

- [ ] Helper raises with a clear diagnostic message (the slice-055 R-15 documented failure mode is "silent ImportError or AttributeError"; the helper MUST AssertionError loudly with both attempted paths in the message so a future archival rename surfaces the cause, not the symptom).
- [ ] Input validation: `_resolve_slice_dir(NNN)` rejects non-int / negative / >999 with a clear ValueError (slice numbers are 3-digit non-negative integers by BRANCH-1).
- [ ] OSDG-1: no SKILL.md changes in this slice. If a SKILL.md edit becomes necessary mid-build, lock-step the installed `~/.claude/skills/<name>/SKILL.md` copy in the same commit (or refactor-by-its-own-slice per CLAUDE.md).
- [ ] PMI-1 / VERSION / methodology-changelog: this is a no-VERSION-bump conformance/correctness class per MEPD-1(b) (slice-040 / slice-045 precedent). NO methodology-changelog entry, NO ADR, NO VERSION bump, NO PMI-1 4-part atomic bump. Verify pre-finish: `git diff master -- VERSION methodology-changelog.md plugin.yaml` is empty.

## Out of scope

- Minting a new rule (RULE-ID or `-D` discipline) for archive-aware vault-test discipline. R-15 is class-signal N=1; slice-055 reflection explicitly recommends watch-list (`/critic-calibrate` route) over BC-1 promotion. Voluntary-restraint discipline (slice-037/046/050/052/055 N≥5 cumulative): this slice ships the helper + the regression tests + the repair; rule-promotion is NOT the right artifact at N=1.
- Retrofitting the second N=2 R-15-class instance (`tests/methodology/test_ptffd1_no_false_positive.py:70`, which carries `REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"`). Per /critique M1 ACCEPTED-FIXED: corpus re-scan at /critique-time surfaced this second instance (design.md L170 prior single-witness claim was wrong). **Explicit deferral rationale**: (a) the slice-034 path is already on the archive side, NOT breaking today (R-15's active-class is "active path becomes archive path"; this instance is "archive path stays archive path" — latent under slice-034 rename pressure only); (b) the slice-034 reference is in a PTFFD-1 corpus regression test (a different test class from BCR-1 input-axis invariants); (c) retrofitting expands slice scope beyond the slice-054 fix. The slice-034 retrofit becomes the FUTURE slice that demonstrably uses `_resolve_slice_dir` and discharges R-15's part-(b) retirement criterion — which is the cleanest path to R-15 retirement per /critique m2 ACCEPTED-FIXED.
- Extending the archive-aware probe pattern to OTHER tests that may have similar latent surfaces (e.g., any future `_extract_version_body` consumer in `test_methodology_changelog.py`). Beyond `test_ptffd1_no_false_positive.py:70` (deferred above) and `test_bcr_1_round_trip_end_to_end.py:43` (fixed by this slice), the corpus-scan at /critique-time found no further code-surface R-15-class instances.
- BCR-1 trigger-shape changes. The `**Closes:** SC-\d{3}` sentinel grammar (slice-053 / ADR-055) is unchanged by this slice. R-15 retirement does not need the BCR-1 round-trip itself — this slice is **not** closing an SC-NNN candidate from `diagnose-out/backlog.md`. (The slice is risk-register-driven, not backlog-driven.)
- Touching `tools/`, `skills/`, `agents/`, `plugin.yaml`, or `VERSION`. This slice operates purely on `tests/methodology/*.py` + `architecture/shippability.md` + risk-register surface.
- The remaining 23 SC-NNN candidates in `diagnose-out/backlog.md`. The next `/slice` invocation will re-rank with R-15 retired and topo-sorted backlog ordering.

## Dependencies

- Prior slices: [[slice-054-fix-pyproject-toml-version-drift]] — authored the failing test as PVFS-1 input invariant pin; [[slice-055-add-shippability-runner-execution-tests]] — discovered R-15 + explicitly nominated this slice in its Deferred section + Lessons-for-next-slice.
- Failing repro path (BFRD-1 verbal-claim-with-path): `tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant`.
- Vault refs: [[risk-register#R-15]], [[slice-055/reflection.md#Discovered]], [[slice-055/reflection.md#Deferred]].

## Mid-slice smoke gate

At ~50% of build (helper written + slice-054 test repointed; helper regression tests not yet authored OR shippability row not yet added), run:

```
$PY -m pytest tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant -v
```

Expected: **PASSED** in `<1s`. If it fails: STOP, diagnose (likely either the helper resolution logic is wrong OR the test file still has stale imports). Do not continue to author regression tests until the BFRD-1 failing repro is GREEN.

Also at mid-slice smoke:
```
$PY -m pytest tests/methodology/test_bcr_1_round_trip_end_to_end.py -v
```
Expected: all tests in the module PASS (i.e., the helper-repoint did not break the file's other slice-054-input-contract assertions).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in validation.md
- [ ] BFRD-1 invariant: `test_bcr_1_sc054_round_trip_inputs_invariant` PASSES (was FAILING pre-slice; reproduced live on master)
- [ ] Helper raises with a diagnostic message that names BOTH the attempted active path AND the attempted archive path (so future failures surface cause, not symptom)
- [ ] All `tests/methodology/` PASS — `$PY -m pytest tests/methodology/ -q` exits 0 (BC-PROJ-4 full-suite read-the-output discipline per slice-039 N=1 → slice-040/041/043/044/045/046/050/051/052/053/054/055 cumulative; the dual-Critic stack cannot reach cross-slice latent surfaces, the full-suite IS the structural backstop)
- [ ] Shippability runner clean: `$PY -m tools.shippability_runner architecture/shippability.md` exits 0 (row 56 PASS; slice-054 row #54 — which cites this same test — also PASS-flipped from FAIL by this fix)
- [ ] `/drift-check` passes (vault and code aligned)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] OSDG-1: no SKILL.md changes this slice (or if any, lock-step installed copy in same commit)
- [ ] PMI-1: `git diff master -- VERSION methodology-changelog.md plugin.yaml` empty (no-VERSION-bump conformance class per MEPD-1(b))
- [ ] Branch-state (BRANCH-1): on `slice/056-fix-bcr1-round-trip-test-archive-paths` (NOT master); `tools/branch_workflow_audit.py` clean
- [ ] R-15 transition: `architecture/risk-register.md` R-15 entry STAYS `**Status**: mitigating` after this slice ships (per /critique m2 ACCEPTED-FIXED — R-15's retirement gate is TWO-part: (a) slice-056 ships the fix + the resolver helper [satisfied by this slice], AND (b) a future slice authoring a similar vault-pin test demonstrably uses the helper [NOT satisfied by this slice]). The `**Mitigation**:` line is updated to record slice-056 as the first half of the gate ("(a) slice-056 ships the helper → DONE; (b) future-slice-uses-helper evidence → pending"). R-15 escalates to `retired` in the future slice that demonstrably uses `_resolve_slice_dir` (likely the slice-034 retrofit nominated under Out-of-scope).

## Pipeline position

- **predecessor**: `/commit-slice` (canonical chain per PCA-1 `tools/pipeline_chain_audit.py:80-81` — `reflect → /commit-slice (auto-advance false)`, `commit-slice → /slice (auto-advance false)`. Per /critique-review M-add-3 ACCEPTED-FIXED — prior wording `/reflect (slice-055 just shipped)` modeled the loop-entry from user perspective but contradicted the canonical chain; this artifact's authoring skill is `/slice` whose canonical chain predecessor is `/commit-slice`)
- **successor**: `/design-slice`
- **auto-advance**: true
- **on-clean-completion**: mission-brief + milestone.md written; candidate settled (user picked #1 via Step-3 ranked recommendation); BFRD-1 satisfied (Step 3c verbal-claim-with-path confirmed). Invoke `/design-slice` next.
- **user-input gates** (halt auto-advance): none remaining — candidate + BFRD-1 confirm both already resolved above.

> Per PCA-1 (methodology-changelog.md v0.41.0).
