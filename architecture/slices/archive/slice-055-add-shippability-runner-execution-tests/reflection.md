# Reflection: Slice 055 add-shippability-runner-execution-tests

**Closes:** SC-005

**Date**: 2026-05-21
**Shipped**: YES-WITH-DEFERRALS (5/5 ACs PASS; one user-approved deferral on a pre-existing unrelated failure detected by the runner self-dogfood)

## Validated

- `run_catalog()` PASS branch records `passed += 1` on `subprocess.run` returncode 0 — validated by `test_run_catalog_pass_row_records_pass` against `<interp> -c "pass"` tmp catalog row
- `run_catalog()` FAIL branch records `failed += 1` with canonical detail `f"segment exited {rc}: {seg!r}\n{tail.strip()}"` — validated by `test_run_catalog_fail_row_records_fail` (structural pins on `status`, `line`, `detail` truthiness + narrow first-line substring `"segment exited 1"`)
- `main()` exit codes 0 / 1 / 2 across the three documented paths (`tools/shippability_runner.py:31-34, 193-195, 203`) — validated by 3 direct `runner.main([args]) == N` tests
- `_normalize_interp` substitutes `<interp>` → `sys.executable` for tmp Machine-cmd cells — exercised transitively in all 4 catalog-exercising tests
- BCR-1 position-pin mechanic anchors on LAST `^  - ` Evidence sub-bullet (`re.finditer(r'^  - ', block, re.MULTILINE)[-1]`) — validated empirically at /critique B2 pre-fix verification AND at /reflect output-axis (this slice): `addr_pos=1328 > last_ev_pos=1185` in `diagnose-out/backlog.md` SC-005 block. **Slice-055 is the second end-to-end BCR-1 round-trip dogfood SUCCESS** after slice-054's first — `**Closes:** SC-005` mission-brief sentinel triggered correct `/reflect` injection of `- **Addressed:** slice-055-…` line at the BCR-1-mandated position (AFTER `**Evidence:**` sub-list at L19 of extracted block, BEFORE `### SC-006` header).
- Voluntary-restraint discipline (slice-037/046/050/052) correctly applied — this slice deliberately mints zero rules, locks zero ADRs; test-coverage IS the right artifact for a one-shot evidence-named test gap on an already-pinned rule (SRSC-1, ADR-039)
- Dual-Critic stack precision held: first Critic 7/7 findings VALIDATED at correct severity by meta-Critic (zero suspicious, zero missed, zero severity adjustments); zero-false-alarm streak extends to N=8 on codification-class slices (046/048/050/051/052/053/054/055)

## Corrected

- **mission-brief pre-finish gate reference to `& $PY -m tools.skill_drift_audit` is wrong** — OSDG-1 is enforced via per-skill pytest tests (`tests/methodology/test_*_skill_drift.py`), not a single audit module. Gate worked because slice-055 touched zero SKILL.md files (OSDG-1 trivially safe); the literal module name in the mission-brief Pre-finish gate template was inaccurate. No vault file requires correction — this is a documentation drift in the slice/mission-brief.md template surface. **Action**: surfaced as a /critic-calibrate candidate (mission-brief template prose drift); N=1 today; if recurrent across future slices, the `slice` skill's pre-finish-gate template should be updated to reference the actual enforcement (per-skill pytest tests).

## Discovered

- **Archive-aware vault-test discipline (class signal, N=1)** — added to risk register as [[R-15]]. A slice that authors tests pinning invariants on its own vault files (e.g., reads `architecture/slices/slice-NNN/mission-brief.md`) breaks at the next `/reflect`'s archival because the path `architecture/slices/slice-NNN/` no longer resolves (the slice moves to `architecture/slices/archive/slice-NNN/`). Slice-054's `test_bcr_1_sc054_round_trip_inputs_invariant` is the witnessed case — the test's `SLICE_054_DIR` constant hard-codes the pre-archival path. Caught at slice-055's shippability dogfood (one-slice latency). **Impact for next slices**: any future slice that authors a test pinning its own vault files MUST either (a) use a path-resolving helper that handles both active and archive locations, OR (b) run only at `/reflect`-time before archival, OR (c) mark the catalog row as "pre-archive only". The recommended pattern is (a) — a small `_resolve_slice_dir(NNN)` helper that tries `architecture/slices/slice-NNN-*/` then falls back to `archive/slice-NNN-*/`.
- **Bash pipe `$?` captures the LAST command's exit code, not the producer's** — when running `$PY -m tools.shippability_runner ... | tail -5`, `$?` returns `tail`'s exit code (always 0), masking the runner's real exit code (which was correctly 1 on this slice's dogfood). Build-log discipline note: for ANY runner whose exit-code is the load-bearing signal, redirect to a file (`> /tmp/out.txt 2>&1`) and capture `$?` before any tail/grep. This is widely known but bit me on first dogfood read; worth a build-log note. Not adding to risk register (it's a shell-discipline observation, not a code risk).

## Deferred

- **slice-054 stale-archive-path fix** (`tests/methodology/test_bcr_1_round_trip_end_to_end.py::SLICE_054_DIR` at line 43) — pre-existing failure detected by slice-055's runner self-dogfood; verified not a slice-055 regression by reproducing on `master`. **Reason**: CLAUDE.md "Refactors need a slice" — the fix targets unrelated code and needs its own slice. **User-approved**: yes (TRI-1 structured-options gate at /build-slice). **Lands in**: next slice (likely slice-056) — a small fix slice that (a) repairs the `SLICE_054_DIR` constant to point at `archive/slice-054-...` AND (b) introduces the archive-aware probe pattern from R-15 so the next BCR-1 round-trip pin slice doesn't repeat the trap.

- **BC-GLOBAL-1 (Important, LLM fence parsing)** — keyword-triggered but does not apply to this slice (zero LLM output parsed). Defer-with-rationale per BC-1 Important protocol. **Lands in**: no future slice; the rule simply doesn't apply.

- **Remaining SC-NNN candidates in `diagnose-out/backlog.md`** — 23 owner-confirmed candidates remain open after slice-055 closes SC-005 (SC-002 + SC-003 + SC-004 + SC-006…SC-026 minus SC-024 if a future slice picks it up). The BCR-1-wired `/slice` next-invocation will surface them as source #7 with full topo-sorted ordering. **Lands in**: future `/slice` invocations.

## Critic calibration

Per TRI-1: scoring each finding from `critique.md` Triage table + reality observed during build/validate.

**First Critic** (from `critique.md`):

- **B1 (FAIL-branch `;`-split crash on `<interp> -c "import sys; sys.exit(1)"`)**: **VALIDATED** — disposition ACCEPTED-FIXED; the empirical reproduction at /critique (`_segments('<interp> -c "import sys; sys.exit(1)"')` → 2 segments, both `ValueError` on `shlex.split`) verbatim demonstrated the bug. The fix (`raise SystemExit(1)`) round-tripped clean both at /critique pre-fix verification AND at /build-slice mid-slice smoke gate. Highest-leverage finding of the review — would have produced a vacuous-or-crashing FAIL test (AC2 violation) had it shipped.
- **B2 (BCR-1 position-pin regression to header-only anchor)**: **VALIDATED** — disposition ACCEPTED-FIXED; the fix (`re.finditer(r'^  - ', block, re.MULTILINE)[-1]`) caught the BCR-1 invariant correctly at /reflect output-axis run (`addr_pos=1328 > last_ev_pos=1185`, NOT just `addr_pos > **Evidence:** header position`). Slice-054 AC4 contract preserved. Without this fix, a future `/reflect` regression that injects `Addressed` between the header and the first sub-bullet would have silently passed.
- **M1 (mid-slice smoke gate cross-site name drift, `_records_pass` / `_records_fail` suffix)**: **VALIDATED** — disposition ACCEPTED-FIXED; the fix surfaced at /build-slice's mid-slice smoke gate runtime — without it the pytest `::` selectors would have collected zero tests and produced a confusing "0 tests collected" output. FBCD-1 cross-file consistency law held.
- **M2 (PowerShell-unfriendly `grep -c`)**: **VALIDATED** — disposition ACCEPTED-FIXED; the AST-based count replacement ran cleanly on PowerShell as part of AC1 verification. A bare `grep -c` would have been a runtime parse error or "not recognized" on stock Win11 PowerShell.
- **M3 (brittle substring-only assertion)**: **VALIDATED** — disposition ACCEPTED-FIXED; the structural + narrow first-line combo pinned both axes during AC2 validation. The slice-038 m2 load-bearing-test lesson held: a future edit to the runner's debug-format string at `tools/shippability_runner.py:151` would now produce an informative failure (structural pins still hold; narrow substring would fail) rather than a false-PASS or vacuous-failure.
- **m1 (design.md "Risk surface for the Critic" forecast)**: **FALSE-ALARM** — disposition OVERRIDDEN-by-user with rationale "the forecast IS valuable USER transparency; this very critique's B1 + B2 (NOT in the forecast list) empirically demonstrate the forecast is non-binding"; meta-Critic VALIDATED the override. Reality at /build-slice and /validate-slice confirmed: the forecast did not bias subsequent gates or validation behavior; the actual two Blockers (both gate-caught) were unrelated to forecast items. User override was correct (Critic over-reached). Calibration signal: lightweight "transparency-only design.md sections" are a legitimate pattern; Critic should NOT flag them as bias-seeding when they're explicitly framed for user-visibility.
- **m2 (helper-signature backtick attribution)**: **VALIDATED** — disposition ACCEPTED-FIXED; the corrected docstring accurately reflects `_catalog_rows` (no strip) vs `_segments` (per-segment strip) layering. Reality at /build-slice helper-write held; reading the corrected docstring at /validate-slice confirmed the layering claim against `tools/shippability_decoupling_audit.py:179-213`.

**Meta-Critic** (from `critique-review.md`):

- **All 7 first-Critic finding scorings (VALIDATED at correct severity)**: **VALIDATED** — meta-Critic reasoning held under build/validate reality. Confidence-high meta-review proven correct on this slice; zero suspicious / missed / severity-wrong calls under reality observation.
- **The 2 below-threshold observations the meta-Critic considered + reasoned away** (AC1 PASS asymmetry; multi-segment row not pinned): both correctly judged out-of-scope. The 5 tests delivered exactly what SC-005 evidence wording named; the design.md `Defensive / out-of-scope branches` section pre-emptively justified the multi-segment scope omission per the deliberate "5 tests, no more" scope discipline. Reality didn't surface any need for either; meta-Critic's restraint was right.

**Missed by Critic** (N=2 — both build-time-reachable, gate-caught classes; per slice-037 law, NO BC-1 promotion for build-time-reachable classes):

1. **mission-brief pre-finish gate template-prose drift** (`& $PY -m tools.skill_drift_audit` reference is wrong — the actual enforcement is per-skill pytest tests). Caught at /build-slice Step 6 when the literal module didn't exist. Quick mental-correction (`pytest tests/methodology/test_*_skill_drift.py`). **N=1**; per slice-037 law, the audit-vs-real-artifact class is build-time-reachable and the gate did catch it. Do NOT add a Critic dimension.

2. **shippability dogfood detects a pre-existing failure (slice-054 stale-archive-path)** as a cross-slice latent surface. Caught at /build-slice Step 6 shippability dogfood. **Not properly a Critic-missable** — the failure was authored at slice-054 and only became active post-slice-054-archival; slice-055's Critic could not have flagged it absent reading every prior slice's vault-pin tests against the archived path. Build-time gate (shippability runner) is the structural backstop; surfaces via the runner's intended exit-1 contract (which slice-055 itself pins via `test_main_returns_1_on_any_fail`). **N=1**; gate-caught at intended latency (one slice). Do NOT add a Critic dimension. Worth a `/critic-calibrate` watch-list entry (R-15) on "archive-aware vault-test discipline" — if a SECOND archive-class regression emerges, then promote.

**Pattern (cumulative N≥8 confirmation of slice-037 audit-vs-real-artifact law)**: dual-Critic stack precision held cleanly on slice-055 (8/8 first-Critic findings VALIDATED-at-correct-severity by meta-Critic; both Blockers caught empirically with code citations + reproduction before filing); 0 false alarms; the 2 missed classes were build-time-reachable gate-caught patterns. Cumulative streak N≥8 on codification-class slices (046/048/050/051/052/053/054/055) reaffirms: **do NOT add Critic dimensions for build-time-reachable classes; the existing gates ARE the structural backstop.** The cure for missed classes at this level is calibration of WATCH-LIST entries and `/critic-calibrate` periodic review, not new Critic dimensions.

## Lessons for next slice

- **The slice-037 audit-vs-real-artifact interaction law extends to N≥8 cumulative**: dual-Critic stack precision holds across 8 zero-false-alarm slices on codification-class work; the stack structurally cannot reach build-time audit-vs-real-artifact interactions. Both classes missed on slice-055 (template-prose drift + cross-slice latent archival surface) were caught in-band by the gates. Per slice-037 law: NO Critic dimensions for build-time-reachable classes. Watch-list / `/critic-calibrate` is the right tooling, not new dimensions. (slice-055)

- **Archive-aware vault-test discipline (R-15, N=1, class signal)**: a slice that authors tests pinning invariants on its own vault files breaks at the next `/reflect`'s archival because `architecture/slices/slice-NNN/` becomes `architecture/slices/archive/slice-NNN/`. Use a `_resolve_slice_dir(NNN)` helper that tries active then archive paths, OR mark the test as "pre-archive only" and gate via shippability catalog flag. Slice-054's `test_bcr_1_sc054_round_trip_inputs_invariant` is the witnessed case (caught at slice-055 dogfood, one-slice latency). The proposed slice-056 fix should both repair slice-054's path AND introduce the archive-aware pattern as a reusable helper. **Watch-list `/critic-calibrate` candidate** (track if N=2 emerges). (slice-055)

- **Voluntary restraint at codification-class slices is the right default (slice-037/046/050/052/055 N≥5 cumulative)**: when test-coverage retires a finding on an already-pinned rule (SRSC-1 / ADR-039 in slice-055's case), the right artifact is the test module itself — NOT a new rule, NOT an extension to an existing rule. Slice-055 deliberately minted zero rules + zero ADRs on a HIGH-severity owner-confirmed candidate and the dogfood + dual-Critic + user-TRI-1 all confirmed the discipline was right. The contrast slice (slice-054 minted PVFS-1 on a recurring class) vs slice-055 (no mint on a one-shot gap) is the empirical demonstration that voluntary-restraint is a tunable knob driven by the underlying failure-class recurrence, not by slice severity. (slice-055)

- **BCR-1 round-trip is structurally robust at N=2 dogfoods**: the slice-053→054 rule-mint-then-dogfood pattern + slice-055 N=2 dogfood both produced clean position-pinned round-trips (addressed line correctly placed AFTER last `^  - ` Evidence sub-bullet, BEFORE next `### SC-NNN` header). The sentinel-anchored trigger (`**Closes:** SC-\d{3}`) preserved the mention-vs-application disambiguation (slice-053 M4 / ADR-055) across this slice (the string `SC-005` appears in many design.md and reflection.md prose contexts; only the mission-brief.md sentinel line fired the trigger). **Generalize for next BCR-1 closes**: position-pinned verification + sentinel-anchored trigger is the working pattern; future slices closing SC-NNN should mirror this exact shape. (slice-055)

- **For ANY runner whose exit-code is the load-bearing signal: redirect output to a file, capture `$?` before any tail/grep**. `$PY -m tools.X ... | tail -N; echo $?` returns `tail`'s exit code (always 0), masking the runner's real exit code. Slice-055 build-log briefly miscaptured the shippability runner's exit code via this pattern; fix is `$PY -m tools.X ... > /tmp/out.txt 2>&1; echo $?` then `tail -N /tmp/out.txt` afterward. Shell discipline, not code defect. (slice-055)

## Vault updates made (thin vault — small list)

- [[risk-register.md]] — added R-15 (archive-aware vault-test discipline; class signal N=1; mitigating via R-15 documentation + slice-056 candidate fix; low band).
- [[diagnose-out/backlog.md]] — appended `- **Addressed:** slice-055-add-shippability-runner-execution-tests on 2026-05-21` under SC-005 candidate block at BCR-1-mandated position (AFTER last `^  - ` Evidence sub-bullet, BEFORE `### SC-006` header). Output-axis verified clean: `addr_pos=1328 > last_ev_pos=1185`.
- [[lessons-learned.md]] — appended `## Slice 055` chronological entry.
- [[shippability.md]] — appended slice-055 catalog row (full new test module file as the critical-path; <1s runtime).
- This slice's [[design.md]] — no corrections (design was empirically pre-grounded at /critique; build executed cleanly with zero deviation).

**What was NOT updated** (because the slice didn't touch them):
- No ADR minted (voluntary-restraint discipline per slice-037/046/050/052/055 line).
- No `methodology-changelog.md` version bump (no methodology surface edited; PMI-1 4-part bump N/A this slice).
- No `~/.claude/*` files (no installed-surface edit).
- No `tools/`, `skills/`, `agents/`, `plugin.yaml`, `VERSION` modifications.
- No `architecture/build-checks.md` rule promotion (no recurring pattern N≥2 surfaced — see Step 5b below).
