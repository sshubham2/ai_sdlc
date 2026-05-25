# Design: Slice 056 fix-bcr1-round-trip-test-archive-paths

**Date**: 2026-05-21
**Mode**: Standard

## What's new

- One new helper in `tests/methodology/conftest.py`: `_resolve_slice_dir(slice_number: int) -> Path` — archive-aware slice-folder resolver.
- One new test module `tests/methodology/test_resolve_slice_dir.py` with 6 test functions pinning the helper:
  - `test_helper_is_importable_from_conftest` — symbol-presence pin (AC2)
  - `test_resolves_archived_slice_054` — archive-path branch on a real archived slice (AC4 row 1)
  - `test_resolves_active_slice_via_tmp_vault` — active-path branch via a `tmp_path` fixture vault (AC4 row 2)
  - `test_raises_assertion_with_diagnostic_when_neither_found` — neither-branch with named-path diagnostic pin (AC4 row 3)
  - `test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir` — structural pin: module-text grep returns no archive-fragile literal-path-RHS (AC3)
  - `test_no_new_archive_fragile_literals_in_methodology_corpus` — **corpus class-closure backstop (per /critique-review M-add-2 ACCEPTED-FIXED)**: greps `tests/methodology/*.py` for any `REPO_ROOT / "architecture" / "slices" / ("archive" / )?"slice-\d{3}-` literal-path-RHS and asserts the match-set is a subset of the known whitelist `{tests/methodology/test_ptffd1_no_false_positive.py:70}` (slice-034 archive path, deferred per /critique M1). When the slice-034 retrofit ships, whitelist shrinks to empty + assertion structurally satisfies R-15's part-(b) retirement criterion without waiting for cross-slice observational evidence (AC4 row 4)
- One mutation to `tests/methodology/test_bcr_1_round_trip_end_to_end.py`: replace the module-level `SLICE_054_DIR = REPO_ROOT / "architecture" / "slices" / "slice-054-fix-pyproject-toml-version-drift"` constant with a call to `_resolve_slice_dir(54)`, threaded through `_read_slice_054_mission_brief()`.
- One new row in `architecture/shippability.md` (row #56) citing slice-056 + R-15 retirement; Machine-cmd column invokes the BFRD-1-repointed test + the new helper regression tests.
- One mutation to `architecture/risk-register.md`: R-15 STAYS `**Status**: mitigating` after this slice ships (per /critique m2 ACCEPTED-FIXED — R-15's risk-register.md:259 retirement gate is TWO-part: (a) slice-056 ships the fix [DONE by this slice], AND (b) a future slice authoring a similar vault-pin test demonstrably uses the helper [pending]). The `**Mitigation**:` line is updated in-place to record part-(a) DONE + name slice-056 + the helper introduction; R-15 escalates to `retired` in the future slice that satisfies part-(b) (the slice-034 retrofit nominated below under Out-of-scope is the natural carrier). This is the safer dogfood of the R-15 entry's own contract vs. silently overriding its part-(b) precondition (per /critique m2 path-(i) choice over path-(ii)).

## What's reused

- [[tests/methodology/conftest.py]] — existing `REPO_ROOT` lives here; new helper joins it (single-file co-location for the small test-utility surface).
- [[tests/methodology/test_bcr_1_round_trip_end_to_end.py]] — slice-054's BFRD-1 input-axis invariant test; the slice-054 PVFS-1 row #54 in shippability.md already invokes it. Repointing it makes shippability row #54 PASS again (it currently FAILs slice-055-innocently on master because the SLICE_054_DIR resolves to a non-existent active path).
- [[architecture/shippability.md]] — existing 55-row catalog; this slice appends row #56 (the catalog already contains the failing test as part of row #54's command set; row #56 is the explicit slice-056 + R-15 trace pin per the slice-054 M-add-1 BCR-1 traceability-axis discipline).
- [[risk-register.md#R-15]] — slice-055-discovered class signal; its `**Status**: mitigating` line flips to `retired` + a `**Retired**: slice-056-fix-bcr1-round-trip-test-archive-paths (2026-05-21; helper introduced; pattern codified)` line.
- `pathlib.Path.glob` for the active/archive directory match (`slice-NNN-*/`).
- [[ADR-055]] — BCR-1 round-trip discipline; this slice does NOT close an SC-NNN (it retires R-15 — risk-register-driven, not backlog-driven), so the `**Closes:** SC-NNN` sentinel is absent and `/reflect`'s BCR-1 injection correctly no-ops.

## Components touched

### `tests/methodology/conftest.py` (MODIFIED — additive)

- **Responsibility**: shared fixtures + path helpers for the methodology self-tests. Currently exports `REPO_ROOT`, `repo_root` (session-scope fixture), and `read_file`. This slice adds `_resolve_slice_dir(slice_number)` — co-located because (a) it's a path helper like `REPO_ROOT`, (b) it's consumed only by sibling `tests/methodology/*.py` modules, (c) the alternative (a new `tests/methodology/_slice_paths.py` module) creates a WIRE-1 consumer-demand surface for one symbol — diseconomy at N=1 use.
- **Lives at**: `tests/methodology/conftest.py` (modified by this slice)
- **Key interactions**:
  - Pure-stdlib: `pathlib.Path`. No new third-party imports.
  - Reads `architecture/slices/slice-NNN-*/` and `architecture/slices/archive/slice-NNN-*/` via `Path.glob`. No writes.
  - Consumed by `test_bcr_1_round_trip_end_to_end.py` (this slice) + `test_resolve_slice_dir.py` (this slice). Future R-15-class fixes (if N=2 emerges) reuse the same helper.

### `tests/methodology/test_bcr_1_round_trip_end_to_end.py` (MODIFIED)

- **Responsibility**: BCR-1 first-end-to-end-dogfood input-axis invariant pin (slice-054 authored). Asserts that mission-brief.md, backlog.md, and the SC-001 block carry the BCR-1-required shape so `/reflect`-time injection fires correctly. This slice does NOT change the test's invariants — it only fixes the path-resolution mechanism the test uses to find slice-054's archived vault.
- **Lives at**: `tests/methodology/test_bcr_1_round_trip_end_to_end.py` (modified by this slice; pre-existing slice-054 authoring)
- **Key interactions**:
  - Imports `_resolve_slice_dir` from `tests.methodology.conftest` (added by this slice)
  - `_read_slice_054_mission_brief()` calls `_resolve_slice_dir(54) / "mission-brief.md"` instead of `SLICE_054_DIR / "mission-brief.md"`
  - `SLICE_054_DIR` constant DELETED (or — equivalent — replaced by `SLICE_054_DIR = _resolve_slice_dir(54)` to preserve any local literal references; choose the cleaner option at build-time)

### `tests/methodology/test_resolve_slice_dir.py` (NEW)

- **Responsibility**: pin the helper's three behaviour branches + the BCR-1 module's structural integrity (post-refactor no hardcoded constant). 5 tests, all under 1 second total.
- **Lives at**: `tests/methodology/test_resolve_slice_dir.py` (created by this slice)
- **Key interactions**:
  - Imports `_resolve_slice_dir`, `REPO_ROOT` from `tests.methodology.conftest`
  - Uses pytest's `tmp_path` fixture for the active-branch test (builds a tmp vault skeleton `<tmp>/architecture/slices/slice-NNN-foo/` and monkeypatches `REPO_ROOT` to point at `tmp_path` for that one test — OR alternatively, the test uses a real archived slice number, since slice-054 + slice-055 are both reliably archived and stable).
  - Uses `pytest.raises(AssertionError, match=...)` for the diagnostic-message pin.

## Contracts added or changed

### Helper `_resolve_slice_dir(slice_number: int) -> Path`

- **Defined in code at**: `tests/methodology/conftest.py` (to be added by this slice)
- **Signature** (pinned at /critique-disposition per M2 ACCEPTED-FIXED — 1-arg form, NOT a 2-arg `repo_root` variant):
  ```python
  def _resolve_slice_dir(slice_number: int) -> Path:
      """Resolve a slice-NNN folder, trying active then archive locations.

      Tries ``architecture/slices/slice-{NNN}-*/`` first (active slice
      directory), falls back to ``architecture/slices/archive/slice-{NNN}-*/``
      (archived). Returns the resolved Path on first match. Raises
      AssertionError with both attempted glob patterns in the message if
      neither resolves.

      The helper reads ``REPO_ROOT`` at function-call-time via module-globals
      (Python's natural binding semantics — ``REPO_ROOT.joinpath(...)`` inside
      the function body resolves the name at each call, NOT at def-time). This
      means ``monkeypatch.setattr("tests.methodology.conftest.REPO_ROOT", tmp)``
      DOES affect subsequent calls — exploited by ``test_resolves_active_slice_via_tmp_vault``
      (AC4b). NO second ``repo_root: Path | None = None`` parameter; the public
      contract is single-arg.

      Per R-15 (slice-055-discovered; mitigating after slice-056 ship per
      /critique m2 ACCEPTED-FIXED — part-(a) DONE, part-(b) pending future
      slice that demonstrably uses this helper): a slice that authors tests
      pinning invariants on its own vault files breaks at the next /reflect's
      archival because the active path becomes an archive path. Callers should
      use this helper instead of hardcoding
      ``REPO_ROOT / "architecture" / "slices" / "slice-NNN-<name>"`` literals.
      """
  ```
- **Resolution algorithm**:
  1. Normalize: format `slice_number` as 3-digit zero-padded string (`f"{slice_number:03d}"`). Reject non-int (use `isinstance(slice_number, int) and not isinstance(slice_number, bool)` — booleans are int-subtype in Python) / negative / >999 with `ValueError` (BRANCH-1 invariant: slice numbers are 0..999 inclusive).
  2. Active-glob: `next(REPO_ROOT.joinpath("architecture", "slices").glob(f"slice-{NNN}-*"), None)`. If a directory match returns, use it.
  3. Archive-glob: same but rooted at `architecture/slices/archive/`. If a directory match returns, use it.
  4. Neither: raise `AssertionError` with a single-line diagnostic naming BOTH attempted glob patterns + the slice number, so a future failure surfaces cause not symptom.
- **Diagnostic-message format pin** (per /critique m4 ACCEPTED-FIXED — Windows path-separator hazard): glob patterns in the AssertionError message MUST be formatted as raw forward-slash strings:
  ```python
  active_pattern = f"architecture/slices/slice-{n_padded}-*"
  archive_pattern = f"architecture/slices/archive/slice-{n_padded}-*"
  raise AssertionError(
      f"neither active nor archive resolution succeeded for slice-{n_padded}; "
      f"tried {active_pattern}, {archive_pattern}"
  )
  ```
  Do NOT compute the pattern as `str(REPO_ROOT / "architecture" / "slices" / f"slice-{n_padded}-*")` — on Windows that produces backslash-separated text (`C:\Users\...\architecture\slices\slice-000-*`) and the AC4c substring assertion `"architecture/slices/slice-000-*" in str(exc.value)` FAILs. Design-time dry-run verifies: `python -c "print(f'architecture/slices/slice-{0:03d}-*')"` produces `architecture/slices/slice-000-*` (forward slash by construction).
- **Cross-platform glob semantics note** (per /critique m5 ACCEPTED-FIXED — pathlib `Path.glob` case sensitivity): `pathlib.Path.glob` matches NTFS case-insensitivity on Windows and POSIX case-sensitivity on Linux/Mac. BRANCH-1 (slice-046 / [[ADR-046]]) enforces lowercase `slice-NNN-` folder naming, so this platform delta is latent (no folder in this repo's history violates lowercase). Cross-platform CI surfaces (if any future) should ensure folder naming is lower-case to keep behavior identical across Windows + Linux.
- **Auth model**: N/A — pure path computation, no I/O beyond `pathlib.Path.glob`.
- **Error cases**:
  - `ValueError("slice_number must be a non-negative integer in [0, 999], got <repr>")` on out-of-range / non-int input. Raised at the top of the function before any glob.
  - `AssertionError("neither active nor archive resolution succeeded for slice-{NNN}; tried <active_pattern>, <archive_pattern>")` when both globs return None. Raised after both attempts.
- **Glob ambiguity behavior**: if a glob matches >1 directory (impossible by BRANCH-1 convention but worth defensive thought), the first match is returned. `Path.glob` returns a generator; `next(..., None)` takes the first. We do NOT enforce uniqueness — that's a BRANCH-1 audit concern, not this helper's job (`tools/branch_workflow_audit.py` already enforces 1:1 number ↔ folder convention per [[ADR-046]]).

(Mission brief Out-of-scope reaffirmed: NO new pipeline-wide contract / rule mints. The helper is a private test utility — single underscore prefix, lowercase, no exported symbol surface.)

## Data model deltas

**None.** No production model touched. The helper performs read-only path lookups via `pathlib`; no schema, no migration, no entity.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_resolve_slice_dir.py` | — | — | test module — rationale: this slice introduces a TEST module (pytest is the consumer; the file IS the test). The WIRE-1 "consumer entry point + consumer test" demand is for new RUNTIME modules; peer test modules under `tests/methodology/` follow the slice-055 / slice-054 / etc. convention. The production runtime helper being added (`_resolve_slice_dir` in `tests/methodology/conftest.py`) is consumed by BOTH `test_bcr_1_round_trip_end_to_end.py` (modified-existing) AND `test_resolve_slice_dir.py` (new) — multiple in-tree consumers, no WIRE-1 entry-point demand. |

(Note: `_resolve_slice_dir` itself lives in `conftest.py` — pytest discovers + injects fixtures from `conftest.py` automatically; the helper is a plain function reused by direct import. It is NOT a new module surface, just an additive function on an existing module, so it does NOT generate a WIRE-1 row.)

## Decisions made (ADRs)

**None.** This slice deliberately mints no ADR + no RULE-ID. Per the slice-037 / slice-046 / slice-050 / slice-052 / slice-055 voluntary-restraint discipline (N≥5 cumulative on codification-class slices): when test-coverage + a small helper retire a class-signal-N=1 risk, the right artifact is the helper + the tests + the risk-register transition — NOT a new rule or a new ADR.

Cross-reference: slice-055 retired its analogous N=1 class signal (SC-005 test-coverage gap on SRSC-1 / [[ADR-039]]) with zero rule mints + zero ADRs and the discipline + dual-Critic + user-TRI-1 all confirmed correct disposition. Slice-056 mirrors that pattern. Compare-and-contrast slice-054 (which DID mint PVFS-1 / [[ADR-056]]) — slice-054's pattern was recurring (pyproject↔VERSION drift class), so rule-minting was right; R-15 is single-witness (one test, slice-054-authored, archive-fragile) so helper + risk-register transition is right.

**MEPD-1(b) discharge** (no-VERSION-bump conformance-fix class):
- Verified against the real META-1 enforcing assertion at `tests/methodology/test_methodology_changelog.py:136` (`re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)`): a no-rule-mint slice with no methodology-surface edit does NOT need a `## vN.N.N` entry.
- Verified against PMI-1 `tests/methodology/test_install_audit.py` invariants: `VERSION`, `plugin.yaml`, `methodology-changelog.md` all untouched.
- Verified against precedent: slice-040 (R-10 retirement, conformance-fix), slice-045 (R-11 retirement, prose-correctness), slice-055 (SC-005, voluntary-restraint).
- Pre-finish proof: `git diff master -- VERSION methodology-changelog.md plugin.yaml` MUST be empty (checked at /build-slice Phase F).

## Authorization model for this slice

N/A — test + risk-register + shippability-catalog slice. No production authorization surface touched.

## Error model for this slice

The slice introduces two error paths in the new helper (defined above under Contracts). Neither is a methodology-surface contract — both are local test-utility behaviors.

| Path | Trigger | What's raised | Pinned by |
|------|---------|---------------|-----------|
| Out-of-range slice number | `_resolve_slice_dir(-1)` / `_resolve_slice_dir(1000)` / `_resolve_slice_dir("054")` | `ValueError("slice_number must be a non-negative integer in [0, 999], got <repr>")` | `test_resolve_slice_dir.py::test_rejects_out_of_range_inputs` (collapsed into the helper-pin family; see AC4c below) |
| Neither active nor archive matches | `_resolve_slice_dir(9999)` would be a ValueError (>999); a valid-range nonexistent number, e.g., `_resolve_slice_dir(0)` (slice-000 has never existed in this repo's history), triggers the AssertionError | `AssertionError("neither active nor archive resolution succeeded for slice-000; tried architecture/slices/slice-000-*, architecture/slices/archive/slice-000-*")` | `test_raises_assertion_with_diagnostic_when_neither_found` |

The slice-054 BFRD-1 invariant test, post-helper-repoint, will gain one indirect behavior: if a future archival rename (e.g., slice-054 renamed by an audit consolidation slice) breaks BOTH globs, the test will fail with a CAUSE-name diagnostic ("neither active nor archive resolution succeeded for slice-054") instead of the SYMPTOM-name diagnostic the current stale-constant produces ("slice-054 mission-brief.md missing at <stale-path>"). That cause-vs-symptom improvement IS the R-15 mitigation pattern's primary purpose.

## Test design (mechanical detail)

### Helper-test fixture choices

For `test_resolves_archived_slice_054` (AC4 row 1, archive-path branch):
- Use slice-054 (or slice-055) as the real archived-slice fixture. Both are stable, archived, and well-known. Slice-054 is preferred because it's the same slice the BFRD-1 test uses — closes the cycle.
- Assertion: `_resolve_slice_dir(54).name == "slice-054-fix-pyproject-toml-version-drift"` AND `_resolve_slice_dir(54).is_dir()` AND `_resolve_slice_dir(54).parent.name == "archive"`.

For `test_resolves_active_slice_via_tmp_vault` (AC4 row 2, active-path branch):
- Use `tmp_path` + `monkeypatch` to point a stub `REPO_ROOT` at a tmp directory containing `architecture/slices/slice-001-tmp-fixture/`. The monkeypatch target is `tests.methodology.conftest.REPO_ROOT`.
- Assertion: `_resolve_slice_dir(1) == tmp_path / "architecture" / "slices" / "slice-001-tmp-fixture"` AND `_resolve_slice_dir(1).is_dir()`.
- **Implementation pin (per /critique M2 ACCEPTED-FIXED — pin the 1-arg form, no Builder-Phase-A optionality)**: the helper MUST read `REPO_ROOT` at function-call-time via module-globals (`REPO_ROOT.joinpath(...)` inline in the function body — Python resolves the name at each call). The helper MUST NOT close over `REPO_ROOT` via a default-argument-evaluated-at-def-time (`def _resolve_slice_dir(slice_number: int, _root: Path = REPO_ROOT)`) OR via a closure cell captured at module-load. The 2-arg `repo_root: Path | None = None` alternative is REJECTED here (was considered at design rev-1; rejected at /critique-disposition because AC2 literally names the 1-arg signature and a `repo_root` kwarg invites future drift — a caller injecting the wrong root).

For `test_raises_assertion_with_diagnostic_when_neither_found` (AC4 row 3):
- Use a slice number known never to exist (e.g., `_resolve_slice_dir(0)`; slice-000 is reserved by BRANCH-1 conventions but no folder exists).
- `pytest.raises(AssertionError, match=r"neither active nor archive resolution succeeded for slice-000")` — narrow substring match on the cause-name diagnostic.
- Secondary assertion: the message text MUST contain BOTH glob-pattern attempts as FORWARD-SLASH strings (per /critique m4 ACCEPTED-FIXED — substring check on the LITERAL strings `"architecture/slices/slice-000-*"` AND `"architecture/slices/archive/slice-000-*"`, NOT against `str(Path(...))` which would backslash on Windows). The helper formats these via `f"architecture/slices/slice-{n_padded}-*"` template — no `Path` round-trip — so the assertion holds identically on Windows and POSIX. This is the must-not-defer "diagnostic message names BOTH attempted paths" mission-brief gate.

For `test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir` (AC3):
- Read the module-text of `test_bcr_1_round_trip_end_to_end.py`.
- Assert: zero occurrences of the literal substring `REPO_ROOT / "architecture" / "slices" / "slice-054`. (Per /critique m1 ACCEPTED-FIXED — AC3's prose-wording harmonized: the test pins absence of the archive-fragile LITERAL-PATH RHS, not absence of the `SLICE_054_DIR` symbol name. Wrapped forms like `SLICE_054_DIR = _resolve_slice_dir(54)` are ACCEPTED — the constant name is convenience; the danger is the literal path RHS.)

For `test_no_new_archive_fragile_literals_in_methodology_corpus` (AC4 row 4, per /critique-review M-add-2 ACCEPTED-FIXED):
- Walk all `*.py` files under `REPO_ROOT / "tests" / "methodology" /`. For each file, read text and search for the regex `r'REPO_ROOT\s*/\s*"architecture"\s*/\s*"slices"\s*/\s*("archive"\s*/\s*)?"slice-\d{3}-'`.
- Collect `(filepath, line_number, matched_text)` for every hit.
- Assert: the collected match-set is a subset of the known whitelist:
  ```python
  WHITELIST: set[tuple[str, int]] = {
      ("tests/methodology/test_ptffd1_no_false_positive.py", 70),
      # When the slice-034 retrofit ships, REMOVE the line above + assert empty match-set.
      # This shrinkage IS the structural mechanism that satisfies R-15's part-(b)
      # retirement criterion (per /critique m2 + /critique-review M-add-2 lineage).
  }
  ```
- Pass if match-set ⊆ WHITELIST; fail with a clear diagnostic naming each non-whitelisted hit otherwise.
- Note: the helper at `tests/methodology/conftest.py` (1 occurrence of `REPO_ROOT / "architecture" / "slices"` at the active-glob computation) is INSIDE the helper itself + does NOT carry a `slice-\d{3}-` suffix — so the regex correctly excludes it (the regex anchors on `"slice-\d{3}-` after the slices path). Verify at design-time by running the regex against `conftest.py` and confirming zero matches.
- AC pinning: the whitelist-shrinkage mechanism is documented in the test's docstring + in design.md§"Defensive / out-of-scope branches" with a forward-pointer to the slice-034 retrofit slice.

### Risk surface for the Critic (transparency, not bias-seeding)

(Per slice-055 m1 OVERRIDDEN-by-user reflection: transparency-only design.md sections are legitimate and Critic should not bias-flag them.)

The Critic SHOULD watch for:
- **Helper signature ambiguity around `slice_number` typing**: `int` strictly excludes `"054"` string form. If a caller writes `_resolve_slice_dir("54")`, it should ValueError, not silently succeed via implicit conversion. Design pins ValueError on non-int; verify the implementation matches.
- **`REPO_ROOT` import-time vs call-time capture**: if the helper closes over `REPO_ROOT` at import-time, the AC4b monkeypatch approach silently no-ops (the test would falsely PASS). Build-time choice between "accept `repo_root` param" vs "read `REPO_ROOT` at call-time" matters — both are valid; one is more testable than the other.
- **Glob multiple-match ambiguity**: `next(iter(glob), None)` returns the first match. Design accepts this; if a slice-number→folder ambiguity exists (would be a BRANCH-1 violation, separately gated), this helper silently picks one. Document the choice; don't add defensive `assert len == 1` here — that's BRANCH-1's job.
- **AC4c diagnostic message integrity**: a future helper refactor that drops the second glob pattern from the AssertionError message silently degrades the cause-name diagnostic. The substring-on-BOTH-patterns pin must survive that class. Test asserts both patterns explicitly.

Empirical reality from slice-055: lightweight transparency sections like this one have not biased subsequent gates or validation behavior; first-Critic OVERRIDDEN-by-user with meta-Critic VALIDATING the override (slice-055 m1).

### Defensive / out-of-scope branches

- The helper does NOT scan other archive-fragile literal-path test modules. **Corpus re-scan at /critique-time (per M1 ACCEPTED-FIXED) surfaced N=2 R-15-class instances**, not N=1: (a) `test_bcr_1_round_trip_end_to_end.py:43` — the slice-054 SLICE_054_DIR hardcoded path, fixed by this slice; (b) `test_ptffd1_no_false_positive.py:70` — `REPO_ROOT / "architecture" / "slices" / "archive" / "slice-034-fix-tf1-audit-field-line-regex" / "mission-brief.md"`, NOT fixed by this slice (deferred — already on the archive side, latent under slice-034 rename pressure only; PTFFD-1 corpus regression test class is structurally distinct from BCR-1 input-axis invariants; retrofitting expands slice scope). The other corpus matches (`test_branch_workflow_audit.py:60` docstring + `test_shippability_runner_execution.py:2` docstring) remain non-actionable prose. The slice-034 retrofit becomes the FUTURE slice that demonstrably uses `_resolve_slice_dir` and discharges R-15's part-(b) retirement criterion (per /critique m2 ACCEPTED-FIXED — R-15 stays `mitigating` after slice-056 ship, flips to `retired` on the slice-034 retrofit). **Updated count**: slice-056 retrofits the first of 2 known R-15-class instances; the second is deferred with rationale recorded in mission-brief.md Out-of-scope.
- The helper does NOT support arbitrary glob patterns (e.g., `_resolve_slice_dir("fix-*")` to find any slice by name suffix). Only int slice numbers. Scope-bounded.
- The helper does NOT memoize results. Each call re-globs. Per-test-call cost is negligible (`< 1 ms` on a hot directory cache); zero memoization keeps the helper stateless + thread-safe + monkeypatch-friendly.

## Shippability row #56 (anticipated shape)

| Col | Value (preview) |
|-----|-----------------|
| # | 56 |
| Slice | slice-056-fix-bcr1-round-trip-test-archive-paths |
| Description | R-15 retirement (slice-056; archive-aware vault-test discipline): `_resolve_slice_dir(NNN)` helper in `tests/methodology/conftest.py` resolves archive-aware slice directories so tests pinning invariants on their own slice's vault files survive `/reflect`'s archival. Regression = the helper signature regresses (active-first/archive-fallback order swapped, or diagnostic message no longer names BOTH attempted globs) OR the BCR-1 input-axis test re-acquires a hardcoded `REPO_ROOT / "architecture" / "slices" / "slice-NNN-..."` literal that re-introduces the slice-054-class archival fragility. |
| Human-cmd | `pytest tests/methodology/test_resolve_slice_dir.py tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant` |
| Time | <2s |
| Machine-cmd | `<interp> -m pytest tests/methodology/test_resolve_slice_dir.py tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant --no-header -q` |

(Exact wording finalized at build-time per the SCMD-1 machine-stable-command convention. Row cites BOTH the slice number AND the R-15 risk ID — the analog of slice-054 M-add-1's BCR-1 traceability-axis discipline for risk-register-driven slices: a future row rewrite that drops `R-15` must FAIL the regression test, preserving the slice-056 retirement audit trail.)

## Pipeline position

- **predecessor**: `/slice`
- **successor**: `/critique`
- **auto-advance**: true
- **on-clean-completion**: design.md written; no ADRs to write (voluntary-restraint discipline); milestone.md updated to stage=design; invoke `/critique` next.
- **user-input gates**: none — Step 2 clarifying questions skipped (mission brief unambiguous; corpus scan confirms single-witness).

> Per PCA-1 (methodology-changelog.md v0.41.0).
