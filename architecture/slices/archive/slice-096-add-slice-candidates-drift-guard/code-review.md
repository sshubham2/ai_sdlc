# Code Review: Slice 096 add-slice-candidates-drift-guard

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-01
**Result**: FINDINGS (minors only — no blockers, no majors)

> v1 advisory: `/code-review` findings do NOT block `/validate-slice`. The Builder accepted + fixed all 3 minors this round (see **Builder response** lines) because they are cheap and correct accuracy fixes on executable-contract / merged-tree surfaces.

## Summary
The core code artifact (`test_slice_candidates_skill_drift.py`) is a faithful, correct clone of the established per-skill drift-test idiom; it imports the right symbols, uses a consistent `label=`, collects under pytest cleanly, passes against the synced tree, and is provably non-vacuous (the comparator's mutation behavior re-proved via temp-files, no git). The CLAUDE.md prose is accurate on its load-bearing claims (pulse/code-review-have-tests-but-unenumerated is true; MEPD-1=EXCLUDE is internally consistent) but contained one mildly overstated completeness word. The build-log's AC5 and BC-PROJ-3 attestations are honest; the headline numbers (1176 passed / 1 failed) reproduced exactly. All findings Minor.

## Changed files (in-scope)
```
tests/methodology/test_slice_candidates_skill_drift.py
CLAUDE.md
architecture/slices/slice-096-add-slice-candidates-drift-guard/build-log.md
```

## Findings

### Blockers (advisory in v1)

None. The diff introduces no broken code path, no unsafe operation, and no contradiction of an ACCEPTED ADR.

### Majors

None. No edge case is hand-waved, no documented failure mode lacks an error path, no function signature has an unspecified contract.

### Minors

#### m1: "final previously-unguarded member" overstates completeness — 12 skills on disk still have no drift test
- **Claim under review**: `CLAUDE.md:42` (added sentence) — "Extended at slice-096 (R-13) to **the final previously-unguarded member** `slice-candidates`"; echoed by `mission-brief.md:5` / `mission-brief.md:12` and `architecture/shippability.md` row 102.
- **Issue**: CLAUDE.md prose is executable contract (Dim 7 / brownfield "code is truth, docs are hypothesis"). "final" asserts set-completeness. Verified: 13 skills have a per-skill drift test + the new `slice-candidates` = 14, but `skills/` has 26 dirs — **12 have NO drift test at all** (`archive critic-calibrate discover drift-check heavy-architect reduce repro risk-spike supersede-slice sync user-test validate-slice`). "final previously-unguarded member" is only true under the narrow reading "final member of the OSDG-1 *named* family" — a scoping the sentence did not state. A future reader could cite this line to conclude OSDG-1 coverage is complete.
- **Evidence**: `ls skills/` → 26 dirs; 13 pre-existing per-skill guards; the gap set is named in this slice's own mission-brief Out-of-scope.
- **Proposed fix**: scope the adjective ("the last named-but-unguarded member of THIS OSDG-1 family"); add an explicit "NOT a total-coverage claim".
- **Builder response**: **ACCEPTED-FIXED.** `CLAUDE.md:42` reworded to "the **last named-but-unguarded member of THIS OSDG-1 family**, NOT a total-skill-coverage claim (≈12 skills such as `discover`/`risk-spike`/`validate-slice` carry no drift test by design — see slice-096 mission-brief Out-of-scope)." Parallel narrowing applied to `mission-brief.md:5`.

#### m2: shippability row 102 reuses the m1 overstatement ("lone previously-unguarded OSDG-1 member")
- **Claim under review**: `architecture/shippability.md` row 102 — "`/slice-candidates` was the lone previously-unguarded OSDG-1 member."
- **Issue**: Same completeness overstatement as m1, propagated to the catalog row (survives into the merged tree). Strictly out-of-scope per the `architecture/*.md` glob exclusion, flagged for parity.
- **Evidence**: identical to m1.
- **Proposed fix**: same narrowing.
- **Builder response**: **ACCEPTED-FIXED.** Row 102 reworded to "the last named-but-unguarded member of the OSDG-1 family (other skills remain unguarded by design — not a total-coverage claim)." SCMD-1 column audit re-run post-edit → 5/5 PASS (6-column shape intact; only the Critical-path prose cell changed).

#### m3: "17 existing per-skill drift tests" count is wrong — actual is 13
- **Claim under review**: `mission-brief.md:12,16,20` + `design.md:8,49` — repeatedly cite "**17** per-skill drift tests guard that family today."
- **Issue**: The actual count of pre-existing per-skill SKILL.md drift guards is **13** (`adopt, build-slice, code-review, commit-slice, critique, critique-review, design-slice, diagnose, pulse, query-design, reflect, slice, triage`). "17" counted files matching `assert_md_forward_synced` — which includes the helper, the normalization test, and the agent-drift tests. The miscount affects no code behavior but is a factual anchor repeated across the slice docs and could mislead a future inventory pin.
- **Evidence**: `tests/methodology/test_*_skill_drift.py` = 12 + `tests/skills/diagnose/test_diagnose_skill_drift.py` = 13 pre-existing; the 17-file grep includes non-per-skill files.
- **Proposed fix**: correct the count to 13.
- **Builder response**: **ACCEPTED-FIXED.** All 5 instances (`design.md:8,49`; `mission-brief.md:12,16,20`) corrected 17 → 13, with a one-line note at `design.md:8` recording the miscount root cause. (The `milestone.md`/`build-log.md` build-stage rewrites no longer carried "17".)

## Dimensions checked
- [x] **Unfounded assumptions** — One minor (m3 "17" miscount, fixed). No docstring/regex drift (the test carries no regex/parser). Imports verified present: `tests.methodology.conftest.REPO_ROOT` + `tests.skill_drift_equality.assert_md_forward_synced` both resolve.
- [x] **Missing edge cases** — None. The comparator inherits all branches from the shared helper (in-repo-missing, installed-missing, genuine divergence, EOL-only→None). EOL-DRIFT-1/ADR-033 honored; the new test file is pure-LF. No load/concurrency/network surface.
- [x] **Over-engineering** — None. Single test function, single helper call, no speculative parameters. Minimal correct shape.
- [x] **Under-engineering** — None. AC1/AC2/AC3 delivered; non-vacuity independently re-proved (EOL-only→None; mutation→AssertionError naming both hashes). WIRE-1 self-consuming exemption legitimate (mirrors all 13 peers).
- [x] **Contract gaps** — None. The test consumes `assert_md_forward_synced(in_repo, installed, *, label)` with all three args correctly positioned + `label` consistent with the path args.
- [x] **Security** — None. Test-only; no auth/input/secret/subprocess/eval/injection; `Path.home()/.claude/...` reads a developer-local file by fixed segments (no traversal from untrusted input). ADR-067 cooperative model.
- [x] **Drift from vault** — One minor (m1 CLAUDE.md "final" overstatement, fixed). Otherwise the code matches design.md exactly: 3-file footprint, no SKILL.md edit, no `.gitattributes`/`_GUARDED_GLOBS` change, no VERSION/changelog/ADR/plugin.yaml churn. MEPD-1=EXCLUDE faithfully implemented (no version literal bumped). No phantom path.
- [x] **Web-known issues** — None applicable. No external API/SDK/framework; stdlib `hashlib`/`pathlib` (via the unchanged helper) + pytest collection.
- [x] **Cross-cutting conformance** — None blocking. The new test collects under `tests/methodology/` with no import error (verified `--collect-only` + a targeted run, green); no `__init__.py` needed. APED-1 N/A (no audit parse-rule/regex changed — a consumer of the unchanged comparator). EOL-DRIFT-1 preserved. BC-PROJ-3 build-log attestation honest + complete (discloses the first non-vacuity proof used `git checkout`, then re-did it compliantly via temp-copy + Get-FileHash; the shipped test does zero git ops). AC5 "1176 passed, 1 failed" reproduced exactly; the lone failure is genuinely pre-existing + outside slice-096's domain (D1 routing sound).
