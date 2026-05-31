# Critique: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Critic reviewed**: mission-brief.md, design.md, ADR-082, project-frame.md, tests/bugs/test_pcr_git_subprocess_cp1252_decode.py (repro), tools/parallel_conflict_resolver.py (all 13 git subprocess sites)
**Date**: 2026-05-31
**Result**: NEEDS-FIXES (pre-triage; Critic verdict)

## Summary

The core fix is sound and the Critic empirically confirmed it on the actual cp1252 host: `text=True` without `encoding=` swallows a `UnicodeDecodeError` in the reader thread and returns `stdout=None`, while `encoding="utf-8"` round-trips losslessly — the `encoding=` kwarg reaches the reader-thread TextIOWrapper. The problems are scoping precision: the AST regression test as specified would mis-fire on the 4 byte-mode git staging sites (B1); the design under-counted the sites as "~10" (M1); AC #2/#3 needed tighter, bounded definitions (M2, M3).

## Findings

### Blockers (must address before /build-slice)

#### B1: AST scan as specified would flag the 4 byte-mode git staging sites, which the design does NOT plan to edit
- **Claim under review**: design.md AST predicate "captures output (`capture_output=True` or `stdout=...PIPE`) → assert `encoding="utf-8"`".
- **Issue**: There are 13 git `subprocess.run` sites, not ~10. Four — `git add` / `git rebase --continue` at L397, L403 (`resolve_soft_conflict`) and L1378, L1384 (`resolve_vault_claim_conflict`) — capture output (`capture_output=True`) but run in **byte mode** (no `text=True`); they never decode stdout. The predicate as written matches these 4 and would assert `encoding="utf-8"` on them → the new test fails on first run, OR the Builder silently adds `encoding=` to them (scope creep + wrong: changes the `exc` repr/byte contract). APED-1 class (slice-088 N+1).
- **Evidence**: byte-mode capturing sites L397-402, L403-409, L1378-1383, L1384-1390 (`capture_output=True`, no `text=True`); decode sites L623, L666, L713, L787, L1508, L1523, L1592, L1937, L1980 (`capture_output=True, text=True`).
- **Proposed fix**: Narrow the predicate to "decodes (i.e. `text=True` present) AND argv[0]=='git' → require `encoding="utf-8"`". Count-pin to exactly 9; docstring lists the 4 byte-mode exclusions by line; execute the test against the real module before declaring it green (APED-1).
- **Builder draft**: ACCEPTED-FIXED — design.md "What's new" rewritten: predicate now keys on `text=True`-presence (not raw `capture_output`), explicitly excludes L397/403/1378/1384, count-pins to 9, and commits to executing the test against the real module per APED-1. The 9-site L-list (incl. L713) is now explicit.

### Majors (address this slice)

#### M1: design.md + ADR-082 + mission-brief under-count sites ("~10") and the L-list omits L713
- **Issue**: actual = 9 decode sites + 4 byte-mode = 13; the design's L-list had 8 numbers and folded `_git_show_stage` (L713) into prose. "~10" is a hand-wave repeated across three artifacts (FBCD-1).
- **Proposed fix**: replace "~10" with exact "9 decode sites (+4 byte-mode excluded)" across mission-brief.md, design.md, ADR-082, with L713 listed explicitly; AC #2 checks the exact count.
- **Builder draft**: ACCEPTED-FIXED — corrected in all three artifacts (mission-brief AC #2 + must-not-defer; design.md What's-new + Components; ADR-082 Context + Decision). Count is now "exactly 9", L713 explicit, byte-mode sites named.

#### M2: AC #3 "existing test suite" unbounded; new AST test not propagated to shippability
- **Issue**: ~20 PCR test files exist; "the existing test suite" has no enumerated boundary (Wiegers). Also design.md introduces a NEW regression test but doesn't propagate it to the shippability catalog (CLAUDE.md RPCD-1/SCPD-1).
- **Proposed fix**: name AC #3's concrete pytest target; add the AST test to shippability.md.
- **Builder draft**: ACCEPTED-FIXED (AC #3 naming) + ACCEPTED-PENDING (shippability row). AC #3 now reads `pytest tests/methodology/test_parallel_conflict_*.py tests/methodology/test_pcr_*.py tests/bugs/test_pcr_git_subprocess_cp1252_decode.py`. The AST-test shippability row is added at `/build-slice` once the file exists (mirrors #95's add-when-exists timing); recorded as a must-not-defer item.

#### M3: TF-1 plan has no row for AC #2 (AST test) or AC #3
- **Issue**: TF-1 strict coverage needs a row per AC or an explicit deferral; AC #2's AST test (the load-bearing recurrence guard) and AC #3 were unrowed → would fail strict TF-1 at pre-finish.
- **Proposed fix**: add TF-1 rows for AC #2 (AST test, WRITTEN-FAILING/PENDING) and AC #3 (or explicit no-new-test note).
- **Builder draft**: ACCEPTED-FIXED — TF-1 table gains two AC #2 rows (`test_all_git_decode_sites_specify_utf8_encoding`, `test_exactly_nine_git_decode_sites_byte_mode_sites_excluded`, status PENDING) + an AC #3 "N/A — no new test, covered by existing suite" row.

### Minors (log; address if cheap)

#### m1: strict-errors residual re-opens the silent claim-drop path for a genuinely non-UTF-8 payload
- **Issue**: post-fix, a non-UTF-8 stage payload still makes `_git_show_stage` return empty/None silently — the same silent-VAULT_CLAIM-bypass shape, just for a different (out-of-scope) trigger. Design flags it honestly as out-of-scope.
- **Proposed fix**: fold the residual into the cp1252 risk-register entry at `/reflect` rather than leaving it only as an ADR consequence line.
- **Builder draft**: ACCEPTED-PENDING — added to must-not-defer; the `/reflect` cp1252 risk entry gets a strict-decode-residual sub-note (non-silent-reader-thread-failure = queued follow-up).

#### m2: confirm shippability #95 provenance
- **Issue**: row 95 already exists referencing slice-090; confirm it was authored by this slice's `/repro` (not orphaned) and matches the final test set.
- **Builder draft**: ACCEPTED-FIXED — confirmed: row #95 was written by this slice's `/repro` step (the repro test exists and fails as expected); slice-name corrected 089→090 at the parallel-slice decision. The AST-test row is added separately per M2.

## Dimensions checked
- [x] Unfounded assumptions — B1, M1 (the "~10"/predicate claims untraced to the real 13/9 reality); core "encoding= reaches reader thread" claim empirically verified — HOLDS.
- [x] Missing edge cases — m1 (non-UTF-8 residual, documented); byte-mode sites under B1; no new I/O surface.
- [x] Over-engineering — none. Option 1 (per-call + AST test) over wrapper is YAGNI-correct; ADR-082 rejects the wrapper soundly.
- [x] Under-engineering — M3 (AC #2/#3 lacked TF-1 rows).
- [x] Contract gaps — none. Internal-only; no signature/CLI/data-model change; callers unaffected.
- [x] Security — none new; the fix CLOSES a latent integrity hole (silent claim-drop → VAULT_CLAIM auto-resolves as SOFT). Strict errors is secure-by-default.
- [x] Drift from vault — none. ADR-082 supersedes nothing, sits in PCR lineage; UTF8-STDOUT-1 correctly noted as a different concern; aligns with project-frame trajectory (audit-cp1252-decode-pattern-across-tools is the queued follow-up). graph stale (acknowledged).
- [x] Web-known issues — none novel; `subprocess.run(text=True)` locale-default is documented CPython behavior, verified directly on the cp1252 host.
- [x] Cross-cutting conformance — B1 (APED-1: execute the AST test against the module, land on exactly 9); M2 (RPCD-1/SCPD-1 shippability propagation); M3 (TF-1 coverage). `encoding="utf-8"` valid on the 3.10 floor. The skipif-on-utf8 repro does NOT weaken the guarantee (shippability runs on the dev cp1252 host); the AST test is the platform-independent recurrence layer — correct two-layer design.

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: NEEDS-FIXES

Reconciles both passes (first Critic B1/M1/M2/M3/m1/m2 + meta-Critic M-add-1/M-add-2 + severity adjustments B1↓Major, m1↑Major). All dispositions ratified as drafted.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Major | ACCEPTED-FIXED | design.md AST predicate rewritten to key on `text=True`, excludes the 4 byte-mode sites, count-pinned to 9. Severity Blocker→Major (defect in a not-yet-written test, corrected in spec). |
| M1 | Major | ACCEPTED-FIXED | Exact 9-site count (incl. L713) corrected across mission-brief/design.md/ADR-082; byte-mode sites named. |
| M2 | Major | ACCEPTED-PENDING | AC#3 suite named concretely (done); AST-test shippability row added at /build-slice once the file exists (RPCD-1/SCPD-1). |
| M3 | Major | ACCEPTED-FIXED | TF-1 plan gains 2 AC#2 rows + AC#3 N/A row. |
| m1 | Major | ACCEPTED-PENDING | Strict-errors residual registered as a first-class risk entry at /reflect (severity Minor→Major: re-admits the exact silent-claim-drop integrity path). |
| m2 | Minor | ACCEPTED-FIXED | shippability #95 confirmed authored by this slice's /repro; 089→090 corrected. |
| M-add-1 | Major | ACCEPTED-PENDING | Two-layer coverage model documented in design.md (done); CI-coverage limitation registered as residual risk at /reflect. Fix (i) infeasible (monkeypatch doesn't propagate — confirmed at /repro); fix (ii) taken. |
| M-add-2 | Minor | ACCEPTED-FIXED | Reuse-seam sentence added to ADR-082 Consequences (predicate kernel liftable by the queued follow-up). |
