# Build log: Slice 096 add-slice-candidates-drift-guard

**Date**: 2026-06-01
**Result**: SHIPPED

## Events (append-only — one line per significant action)

- 2026-06-01 10:05 BUILD: prerequisite check — branch `slice/096-add-slice-candidates-drift-guard` correct; CRP-1 clean (critique-review.md present); TF-1 N/A (test-first:false)
- 2026-06-01 10:07 BUILD: created `tests/methodology/test_slice_candidates_skill_drift.py` (clone of test_query_design_skill_drift.py; OSDG-1 drift guard for /slice-candidates)
- 2026-06-01 10:08 BUILD: CLAUDE.md OSDG-1 enumeration extended to name `slice-candidates` + its test (MEPD-1=EXCLUDE noted; pulse/code-review out-of-scope noted)
- 2026-06-01 10:09 BUILD: shippability.md += row 102 (full 6-column SCMD-1 shape, cloned row-101 placeholder conventions)
- 2026-06-01 10:10 TEST: new drift test PASS against synced tree (AC1/AC3-pass); SCMD-1 column audit 5/5 PASS (m-add-1 resolved)
- 2026-06-01 10:12 SMOKE: AC3 non-vacuity v1 — mutate in-repo SKILL.md → test FAIL (exit 1, genuine-drift assertion, both hashes named) → restore → PASS
- 2026-06-01 10:12 FINDING: AC3 non-vacuity v1 used `git checkout -- skills/slice-candidates/SKILL.md` to revert — BC-PROJ-3 / BC-GLOBAL-2 (Critical) forbid git-revert for mutate-then-restore
- 2026-06-01 10:14 BUILD: re-proved AC3 non-vacuity COMPLIANT — temp-copy swap restore (Copy-Item, NOT git) bracketed by Get-FileHash pre/post equality (pre==post TRUE); mutated→FAIL, restored→PASS, working tree clean
- 2026-06-01 10:15 TEST: BC-PROJ-11 — `git diff CLAUDE.md` added lines carry NO hard-coded `v0.NN.0` methodology-version literal
- 2026-06-01 10:16 TEST: pre-finish audit roster A1+A2 all exit 0 (BRANCH-2[+warn], CRP-1, WIRE-1, TF-1, UTF8-STDOUT-1, PCA-1, BCI-1, MCFS-1, AVFS-1, STP-1, NAW-1, TVFS-1); LINT-MOCK clean
- 2026-06-01 10:17 BUILD: BC-1 attestations recorded (below); proceeding to --strict --ack-critical
- 2026-06-01 10:18 TEST: BC-1 --strict --ack-critical BC-PROJ-3 BC-GLOBAL-2 → exit 0 (all applicable Critical acknowledged)
- 2026-06-01 10:20 TEST: full tests/methodology/ run #1 → 2 failed, 1175 passed (failures: bcr_1 round-trip + external_vault adr/risk)
- 2026-06-01 10:22 FINDING: bcr_1 failure root cause = `diagnose-out/backlog.md` MISSING in worktree (R-20 seed gap — worktree created at /slice time skipped /build-slice's cp-r seed); NOT a slice-096 regression
- 2026-06-01 10:23 BUILD: R-20 seed — copied gitignored diagnose-out/ + graphify-out/ from main repo into worktree; backlog.md now present
- 2026-06-01 10:24 FINDING: external_vault failure = PRE-EXISTING on clean master — `test_external_vault_adr_and_risk.py:49` hard-codes archived slice-093's active-path design.md (FileNotFoundError); out of slice-096 scope (094/095 external-vault domain)
- 2026-06-01 10:26 TEST: full tests/methodology/ run #2 (post-seed) → 1 failed (external_vault, pre-existing), 1176 passed; bcr_1 now PASSES → slice-096 introduces ZERO new regressions
- 2026-06-01 10:27 BUILD: /drift-check full mode → CLEAN (0 blockers, 0 majors); drift-log.md slice-096 trigger written
- 2026-06-01 10:28 TEST: DCE-1 drift_check_audit → exit 0 (slice-096 trigger marker present)

## Summary

### Plan executed

3-file additive change (slice design CLEAN; MEPD-1 = EXCLUDE):

1. **`tests/methodology/test_slice_candidates_skill_drift.py` (NEW)** — DONE. OSDG-1 drift guard: asserts in-repo `skills/slice-candidates/SKILL.md` ≡ installed (EOL-normalized) via the shared `assert_md_forward_synced`. AC1 + AC3.
2. **`CLAUDE.md` OSDG-1 enumeration (MODIFIED)** — DONE. Names `slice-candidates` + its test; records MEPD-1=EXCLUDE + pulse/code-review out-of-scope. AC2.
3. **`architecture/shippability.md` row 102 (MODIFIED)** — DONE. Full 6-column SCMD-1 shape. AC4. (Next free `#`-id confirmed 102 at build; row 101 = slice-093.)

No `skills/slice-candidates/SKILL.md` edit (in-repo ≡ installed already). No `.gitattributes`/`_GUARDED_GLOBS` change (`skills/**/SKILL.md` blanket glob already covers it). No VERSION / methodology-changelog / ADR / plugin.yaml / install_audit change (MEPD-1 = EXCLUDE).

### Mid-slice smoke gate

**Result**: PASS — AC3 non-vacuity. Mutation of the in-repo SKILL.md → drift test FAILs with the genuine-divergence assertion (both EOL-normalized sha256 hashes named); restore → PASS. Re-proven via the BC-PROJ-3-compliant temp-copy mechanism (see finding below).

### Build-checks (BC-1 / BCSG-1) attestations

Applicable: 2 Critical (BC-PROJ-3, BC-GLOBAL-2) + 3 Important (BC-PROJ-4, BC-PROJ-5, BC-PROJ-11).

- **BC-PROJ-3 + BC-GLOBAL-2 (Critical) — ADDRESSED + acknowledged.** The slice ships **no** validation/demo/automation harness that performs any `git checkout`/`git restore`/`git stash` revert — the new test does pure content-hash comparison via `assert_md_forward_synced`, zero git operations. The AC3 non-vacuity demonstration's FIRST pass used `git checkout -- skills/slice-candidates/SKILL.md` (a BC-PROJ-3 violation in the interactive proof, NOT in shipped code). Mitigations: (a) `skills/slice-candidates/SKILL.md` carries **zero uncommitted slice-096 work** — this slice does not edit it (pre-mutation `git status --porcelain` empty); (b) restore was verified byte-exact (`git status --porcelain` empty ≡ HEAD). The proof was then **re-done compliantly**: temp-copy swap restore (`Copy-Item`, not git) bracketed by a `Get-FileHash` pre/post equality assertion (**pre==post TRUE**). No slice work was at risk or destroyed. The gate caught a real instance and it was corrected to the rule-preferred mechanism.
- **BC-PROJ-4 (Important) — ADDRESSED.** The new gate (the drift test) was exercised against the **real** artifact `skills/slice-candidates/SKILL.md` (not a fixture) at build → PASS, and proven non-vacuous against a real mutation → FAIL. The SCMD-1 column audit was run against the **real** `architecture/shippability.md` catalog → 5/5 PASS. The drift test reports ENGAGED ("1 passed"), not "not enabled".
- **BC-PROJ-5 (Important) — NOT APPLICABLE (defer-with-rationale).** slice-096 performs no identifier/family rename and defines no NEW frozen / append-only carve-out. The keyword trigger ("carve-out") refers to the **pre-existing** ADR-054 `--obo-peek` read-only carve-out inside `/slice-candidates` (cited as the protected invariant), not a frozen set this slice introduces. No frozen-set content-hash snapshot is owed.
- **BC-PROJ-11 (Important) — ADDRESSED.** The CLAUDE.md edit is a methodology-doc change. `git diff CLAUDE.md` on the added lines carries **no** hard-coded `v?0.NN.0` methodology-version literal (grep-verified); the only version reference is the word "VERSION" in the prose "no VERSION bump".

### Pre-finish gate

- [x] All ACs pass with evidence — see validation.md (to be written by /validate-slice)
- [x] Must-not-defer addressed (RPCD-1 shippability row added; cp1252-safe N/A — no new tool; fail-closed N/A — no new audit; non-vacuity proven by mutation; new-tool fan-out N/A — no new tool; OSDG-1 forward-sync N/A — no SKILL.md edited)
- [x] Drift-check pass (DCE-1) — clean (drift-log slice-096 trigger written; full-mode audit 0 blockers / 0 majors)
- [x] Mid-slice smoke regression check pass
- [x] No debug code / TODOs / FIXMEs
- [x] LINT-MOCK clean
- [x] WIRE-1 clean (test self-consuming exemption)
- [x] BC-1 / BCSG-1 — Critical rules acknowledged (BC-PROJ-3, BC-GLOBAL-2); Important addressed/deferred above
- [x] BRANCH-2 clean (on slice/096 branch; stale-branch warning names in-flight 094/095 — benign under parallel operation)
- [x] UTF8-STDOUT-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, CRP-1 — all exit 0

### AC5 regression evidence

`tests/methodology/` post-seed: **1176 passed, 1 failed**. The lone failure is `test_external_vault_adr_and_risk.py::test_no_new_tool_migration_and_classification_map_documented` — **PRE-EXISTING on clean master** (verified by isolated run in the main repo). slice-096 changes nothing in that file's domain. **slice-096 introduces ZERO new regressions.**

### Discovered issues (pre-existing — surfaced, NOT resolved here)

- **D1 — stale active-path test pin from slice-093 archival.** `tests/methodology/test_external_vault_adr_and_risk.py:49` hard-codes `architecture/slices/slice-093-add-external-vault-support/design.md` (the **active** path). slice-093 was merged + archived (folder now under `architecture/slices/archive/`), so the path is gone → `FileNotFoundError` on master. Fix = make the pin archive-aware (resolve active-OR-archive). **Out of slice-096 scope**: it lives in the external-vault initiative's test domain (slice-093/094/095) and editing it would risk colliding with the in-flight slice-094/095 worktrees — the very independence slice-096 was scoped to preserve. **Routing recommendation**: fold into slice-094 or slice-095 (which already own that file's domain), or a small standalone maintenance slice.
- **D2 — R-20 worktree-seed gap (process, not code).** This worktree was created at `/slice` time with a plain `git worktree add`, which skipped `/build-slice`'s `cp -r diagnose-out/ graphify-out/` seed → `diagnose-out/backlog.md` was absent and bcr_1 false-failed until manually seeded at build. Matches the slice-093 aggregated lesson ("worktree-at-/slice silently drops the R-20 seed"). Seeded manually this build; the systemic fix (seed at /slice-time worktree creation, or a shared worktree-create helper) is the slice-093-flagged follow-up, still open.

### Deferrals

- None functional. m2 (critique) DEFERRED at triage — pre-existing `_parse_shippability_rows` docstring mislabel in `tools/parallel_conflict_resolver.py` (slice-094's file); out of scope per "refactors need a slice".

### Design deviations

- None. Build matched design.md exactly (3-file footprint, MEPD-1=EXCLUDE, id 102 as design predicted after the M2 fix).

### Files changed

- `tests/methodology/test_slice_candidates_skill_drift.py` (NEW)
- `CLAUDE.md` (OSDG-1 enumeration extended)
- `architecture/shippability.md` (row 102 appended)
- (vault artifacts: mission-brief.md, design.md, critique.md, critique-review.md, milestone.md, build-log.md; slice-queue.md regenerated)
