# Design: Slice 043 codify-split-slice-folder-naming-convention

**Date**: 2026-05-18
**Mode**: Standard

## Decision locked at design (mission-brief AC2 / Step 3)

The R-6 fix-candidate offered two mutually-exclusive options:
- **(a)** codify "split-slice follow-up folders are numeric `slice-NNN-`; the `NNNx` letter is a prose lineage label only" + keep the strict `\d{3}` audit regex, improving only the *rejection message*.
- **(b)** widen `_SLICE_FOLDER_RE` / `_SLICE_BRANCH_RE` to accept an optional letter suffix `slice-NNN[A-Z]?-`.

**Chosen: (a).** Rationale (recorded fully in [[ADR-046]]):
1. **De-facto practice is already (a).** slice-030A shipped with a numeric folder `slice-030-...` ("030A" prose label only); slice-031 was created as `slice-030B-...` and *renamed* to canonical numeric `slice-031-...` (the witnessed R-6 instance). Option (a) codifies what the project already does.
2. **(b) contradicts the globally-unique-numeric slice-numbering rule.** `/slice` computes `new = max(existing) + 1`; `_index.md` / `archive/_index.md` catalogs, the `_SLICE_BRANCH_RE` branch-name binding, and the test fixture `_make_slice_folder` (`slice-{n:03d}`) all assume a monotonic numeric key. Letter-suffixed folders fork the key space and have broad blast radius.
3. **(a) is behavior-preserving.** Letter-suffixed folders are *already* rejected by `_SLICE_FOLDER_RE`; this slice does not change the accept/reject decision — it makes the rejection *actionable* and *names the convention*. That keeps the change in the conformance/clarification class (no new gate, no accept-set change).

## What's new

- A **diagnostic-only** secondary regex `_SPLIT_SLICE_FOLDER_RE` in `tools/branch_workflow_audit.py` (`^slice-(\d{3})([A-Z]+)-(.+)$` — **uppercase-only** per Critic m1, matching the documented uppercase lineage-label convention `030A`/`030B`/`030C`; a lowercase malformed name like `slice-030misc-x` correctly falls through to the generic message) used *exclusively* to recognize a letter-suffixed split-slice folder shape when the strict `_SLICE_FOLDER_RE` match fails, so the `usage-error` can emit a convention-naming, actionable message instead of the current generic one. The strict accept regex `_SLICE_FOLDER_RE` is **unchanged** (numeric-only accept preserved).
- A new "split-slice folder-naming convention" sub-clause appended to the **Branch-per-slice** bullet in root `CLAUDE.md` (Brownfield rules section): "split-slice follow-up slices use a numeric `slice-NNN-` folder + `slice/NNN-<name>` branch (next free number); the `NNNx` letter (e.g. `030C`) is a prose *lineage label* only, never the folder/branch name. Per [[ADR-046]] / BRANCH-1."
- [[ADR-046]] — locks option (a) + the convention statement + the actionable-message behavior.
- New regression test module `tests/methodology/test_branch_workflow_split_slice_folder_convention.py` pinning: (i) canonical numeric `slice-NNN-` folder accepted (no `usage-error`); (ii) letter-suffixed `slice-030B-...` folder rejected **with** the convention-naming message (kind=`usage-error`, message contains the pinned convention phrase + the rename guidance); (iii) the message names the next-free-number remedy; (iv) a lowercase non-convention name (`slice-030misc-x`) falls through to the **generic** message (not the split-specific one — m1 precision guard). Plus a CLAUDE.md prose-pin for the new convention sub-clause (extends, does not modify, `test_root_claude_md_branch_per_slice_rule.py`'s contract — new test fn in the new module).
- **R-6 retirement (M2 — explicit RR-1 mechanic)**: in `architecture/risk-register.md`, **flip the `**Status**: open` field line to `**Status**: retired`** AND add a `**Retired**: slice-043-codify-split-slice-folder-naming-convention (2026-05-18; [[ADR-046]])` line, mirroring R-7's two-part shape (`**Status**: retired` + `**R-7 RETIREMENT (...)**` paragraph). RR-1 (`tools.risk_register_audit`) derives status **solely from the `**Status**:` field** — adding only the `**Retired**:` prose line WITHOUT flipping `**Status**:` leaves R-6 reporting `open` and fails AC4.
- **m2 — shippability cataloguing**: the new test module `test_branch_workflow_split_slice_folder_convention.py` MUST be added to `architecture/shippability.md` (extend BRANCH-1 row 21's command set OR a new row) so the new pin's regression is caught by the /validate-slice Step 5.5 catalog runner — closes the slice-038→R-10 ~5-slice detection-latency class (slice-040 lesson) for this slice's own pin. Applied at /build-slice + recorded at /reflect Step 5.3. (Critic m2 — ACCEPTED-PENDING.)

## What's reused

- `tools/branch_workflow_audit.py` — `audit()` Step "Compute expected slice branch from folder name" (`branch_workflow_audit.py:270-282`) is the single emission site of the folder-name `usage-error`; the new message branches there.
- `_slice_branch_name()` (`branch_workflow_audit.py:148-155`) — unchanged; still returns `""` on strict-regex miss, which already drives the `usage-error` path.
- Existing test patterns in `tests/methodology/test_branch_workflow_audit.py` (`_init_repo_on_default_branch`, `_make_slice_folder`) — reused by the new test module's fixtures.
- `tests/methodology/conftest.py::read_file` — reused for the CLAUDE.md prose-pin.
- [[risk-register#R-6]]; CLAUDE.md Brownfield rules → Branch-per-slice bullet; [[slice-031-complete-shippability-decoupling]] (witnessed instance); [[slice-041-reframe-installed-pin-forward-sync-invariant]] ("030C" split-lineage precedent).

## Components touched

### `tools/branch_workflow_audit.py` (modified)
- **Responsibility**: BRANCH-1 audit — validate current branch vs active slice's `slice/NNN-<name>` pattern. This slice adds an actionable, convention-naming rejection message for the letter-suffixed split-slice folder shape; accept/reject set is unchanged.
- **Lives at**: `tools/branch_workflow_audit.py` (modified — add `_SPLIT_SLICE_FOLDER_RE` module constant; branch the folder-name `usage-error` message at `:271-282`).
- **Key interactions**: invoked at `/build-slice` Step 6 pre-finish; consumed by `tests/methodology/test_branch_workflow_audit.py` + the new convention test module. No new imports, no signature change, exit-code contract unchanged (still `2` for `usage-error`).

### root `CLAUDE.md` (modified)
- **Responsibility**: project pipeline rules. Adds the split-slice folder-naming convention as an explicit sub-clause of the Branch-per-slice bullet so the convention is discoverable and pinned (it was implicit — the R-6 root cause).
- **Lives at**: `CLAUDE.md` (Brownfield rules → Branch-per-slice bullet).
- **Key interactions**: pinned by `test_root_claude_md_branch_per_slice_rule.py` (existing, unaffected — only asserts the `Branch-per-slice` substring) + a new convention-phrase pin in the slice's test module. Not installed-mirrored → no CAD-1 concern.

## Contracts added or changed

None. No endpoints/events. The `branch_workflow_audit` CLI contract (args, JSON shape, exit codes 0/1/2) is unchanged — only the human-readable text of one `usage-error` message is enriched, and a diagnostic-only regex constant is added.

## Data model deltas

None.

## Wiring matrix

This slice introduces no new runtime modules (modifies an existing audit + CLAUDE.md prose; adds one test module). Zero-row matrix — clean per WIRE-1.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-046]] — Split-slice follow-up folders/branches are numeric `slice-NNN-`; the `NNNx` letter is a prose lineage label only (option (a) over widening the regex); BRANCH-1 emits an actionable convention-naming rejection message for the letter-suffixed shape. — reversibility: **cheap** (message text + a diagnostic regex + a doc sub-clause; revertible in <1hr; no accept-set or exit-code change).

## Methodology-surface obligation pre-decision (mission-brief Must-not-defer #1)

**Pre-decided: NO new RULE-ID, NO methodology-changelog entry, NO PMI-1 4-part version bump.** This is a **conformance/convention-clarification** of the *existing* BRANCH-1 rule — it does not mint a gate, does not change BRANCH-1's accept/reject decision, and does not alter any audit exit-code/JSON contract. Recorded via [[ADR-046]] + the R-6 `**Retired**:` line + the CLAUDE.md convention sub-clause + the regression pin. Precedent class: slice-029 (ADR-027, no rule-ID), slice-036/R-9, slice-040/R-10 (conformance-fix; `**Retired**:` line, no parentless changelog `###` entry).

**/build-slice MUST verify this why-none against the *actual* enforcing assertions, not the precedent alone** (MEPD-1(b) / slice-032 false-precedent guard, slice-040 lesson): (1) the real META-1 `re.split(r"^## v\S+ — \d{4}-\d{2}-\d{2}", ...)` assertion in `tests/methodology/test_methodology_changelog.py` — confirm a no-entry decision does not trip it; (2) the real PMI-1 `plugin_manifest_audit` / `test_plugin_yaml_version_matches_version_file_invariant` — confirm no bump is demanded for a no-`tools/`-addition, no-rule change. If either assertion would fail under no-entry/no-bump → escalate the decision at /build-slice plan-mode, do not auto-bless.

## Authorization model for this slice

N/A — no auth surface. The audit is a local read-only CLI over a slice folder + git plumbing.

## Error model for this slice

No new error codes. One existing `usage-error` violation (`kind="usage-error"`, exit code 2) gets a *branched, enriched message*: when the failing folder name matches `_SPLIT_SLICE_FOLDER_RE` (uppercase-letter-suffixed split-slice shape), the message states the convention + the next-free-number rename remedy + cites [[ADR-046]]/BRANCH-1; otherwise the existing generic `slice folder name does not match slice-NNN-<name> pattern` message is preserved verbatim (so the non-split malformed-name path — including lowercase malformed names per m1 — is unchanged).

## Build-time pre-grep obligations (mission-brief Must-not-defer #2 — state-transition)

`/slice` + `/design-slice` + Critic independently confirmed: **no** test pins R-6's `open`/`Status: open` state (grep `R-6|r_6` over `tests/` returned only `fixtures/build_checks/canonical_project_checks.md`, an unrelated BC-1 canonical fixture — NOT an R-6-state assertion). /build-slice must nonetheless re-run the pre-grep at plan-mode (risk-register-state tests can be added between slices) and run the **full `tests/methodology/` suite** at pre-finish (BC-PROJ-4 backstop; R-10-class master-non-green guard).

**M1/M2 pre-finish BC-PROJ-4 step (added per Critic)**: run `$PY -m tools.risk_register_audit architecture/risk-register.md --json` on the REAL file at pre-finish and assert (1) R-6's parsed `status == "retired"` and (2) R-6 is absent from `--filter-status open` — this FAILs pre-slice (R-6 currently parses `status: open` from risk-register.md:120) and PASSes only after the `**Status**:` line flip lands (genuine contrast, satisfies mission-brief AC4 + Verification #4). `--filter-status mitigating` is NOT used (wrong axis for an `open → retired` transition — R-6 never passes through `mitigating`, unlike R-4/R-5).
