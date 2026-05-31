# Build log: Slice 091 harden-pcr-decode-non-silent

**Date**: 2026-05-31
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-05-31 11:30 BUILD: BRANCH-2 worktree created at ../ai_sdlc-wt/slice-091-harden-pcr-decode-non-silent on slice/091-harden-pcr-decode-non-silent; scaffold commit staged ONLY slice-091 exclusive files (folder + ADR-083 + repro test) — slice-092 + shared shippability.md/slice-queue.md left untouched in main (user-approved isolation; parallel slice-092 in flight, non-overlapping)
- 2026-05-31 11:30 BUILD: seeded diagnose-out + graphify-out into worktree (R-20)
- 2026-05-31 11:40 BUILD: Phase 1 core fix — _StageDecodeError(_SoftResolutionError) + _git_show_stage bytes-capture+explicit-decode (docstring inverted, m1) + _append_decode_stop_audit breadcrumb + ConflictDiagnostic.claim_extraction_degraded (constructor-set, m-add-1) + diagnose_conflict catches both stage reads (m-add-2) + classify_conflict degraded→UNKNOWN
- 2026-05-31 11:45 SMOKE: mid-slice — repro PASS (fix works); count-pin RED as expected
- 2026-05-31 11:46 DEVIATION: design predicted decode 9→8 but reality is decode UNCHANGED at 9 / byte-mode 4→5 — the new _append_decode_stop_audit `git rev-parse HEAD` decode site offsets the one _git_show_stage gives up. Corrected count-pin (_EXPECTED_BYTE_MODE_SITES 4→5, decode stays 9), shippability #96, design.md/ADR-083/mission-brief. design.md updated: yes
- 2026-05-31 11:50 TEST: count-pin 9/5 PASS; new test_parallel_conflict_resolver_decode_fail_closed.py 6/6 PASS (AC2/AC3 + stage-3 m-add-2 + classify/resolve/defense-in-depth)
- 2026-05-31 11:52 BUILD: shippability #98 (repro) + #100 (decode-fail-closed guard) added; #96 corrected to 9/5; #99 reserved for parallel slice-092
- 2026-05-31 11:55 TEST: all resolver-area tests 53/53 PASS (no regression)
- 2026-05-31 12:05 BUILD: full suite 1295 PASS; all 16 Step-6 audits green (BC-1 strict BC-PROJ-3+BC-GLOBAL-2 acked); SHIPPED
- 2026-05-31 12:15 FINDING: /code-review 0 blockers / 0 majors / 3 minors — all addressed in-slice: m1 (defense-in-depth _StageDecodeError catch on resolve_vault_claim_conflict Step-3 reads — makes fail-closed invariant total), m2 (count-pin test "4 staging"→"5 (4 staging+1 read-decode)" self-violation prose fix), m3 (repro docstring pre-fix-None tagged dev-host-specific + cpython#105312)
- 2026-05-31 12:18 TEST: full suite re-run after code-review fixes — 1295 PASS (m1 code change, no regression)

## Summary (filled at slice end)

### Plan executed
- Phase 0 — BRANCH-2 worktree isolating slice-091 (slice-092 + shared files untouched in main): DONE
- Phase 1 — core fix in `tools/parallel_conflict_resolver.py`: DONE (`_StageDecodeError`, bytes-capture `_git_show_stage` + inverted docstring, `_append_decode_stop_audit`, `claim_extraction_degraded` field, dual-stage catch, classify degraded→UNKNOWN)
- Phase 2 — mid-slice smoke: repro PASS; count deviation discovered + reconciled
- Phase 3 — tests: count-pin 9/5 + new `test_parallel_conflict_resolver_decode_fail_closed.py` (6 tests): DONE
- Phase 4 — shippability #98 + #100 + #96 correction: DONE
- Phase 5 — Step 6 audits + full suite: DONE

### Mid-slice smoke gate
**Result**: PASS — repro `test_pcr_git_show_stage_non_utf8_fail_closed.py` PASSES post-fix; count-pin RED-then-corrected (see deviation).

### Pre-finish gate
- [x] All ACs pass — AC1 repro PASS, AC2/AC3 fail-closed test 6/6 PASS, AC4 count-pin 9/5 + cp1252 #95 + full suite green
- [x] Must-not-defer addressed — absent("")≠undecodable(STOP); audit breadcrumb; both manifestations converged (one main-thread path); docstring inverted (m1); 4 STAGING byte-mode sites untouched
- [x] Drift-check pass (DCE-1 clean; full-mode drift-log Trigger written)
- [x] Smoke regression check pass
- [x] No debug code (the one print() is the best-effort audit-failure stderr warning, matching the existing `_append_audit_log` pattern)
- [x] All 16 Step-6 audits green: DCE-1 / BRANCH-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / TF-1(strict 5/5) / WIRE-1 / STP-1 / NAW-1 / MCFS-1 / AVFS-1 / TVFS-1 / BC-1(strict, BC-PROJ-3+BC-GLOBAL-2 acked) / mock-budget / triage+critique-review (pre-run)
- [x] Full suite 1295 PASSED / 0 FAILED

### BC-1 attestation
- BC-PROJ-3 / BC-GLOBAL-2: slice-091 performs NO destructive `git checkout`/`restore`/`stash`/`reset` revert of uncommitted work. The Phase-0 worktree sequence used `git switch -c` + `git switch master` + `git worktree add` only (carries dirty state, never discards). Acknowledged under `--strict`.

### Deferrals
- None.

### Design deviations
- **Count-pin: design said decode 9→8; reality is decode UNCHANGED at 9 / byte-mode 4→5.** The new `_append_decode_stop_audit` helper has its own `git rev-parse HEAD` decode site (mirroring `_append_skew_stop_audit`) that offsets the one `_git_show_stage` gives up. Reconciled across `test_parallel_conflict_resolver_git_encoding.py` (`_EXPECTED_BYTE_MODE_SITES=5`), shippability #96, design.md (BUILD CORRECTION), ADR-083, mission-brief. **Updated in design.md: yes.**

### Files changed
- `tools/parallel_conflict_resolver.py` — `_StageDecodeError`, `_git_show_stage` (bytes+explicit decode+inverted docstring), `_append_decode_stop_audit`, `ConflictDiagnostic.claim_extraction_degraded`, `diagnose_conflict` (dual-stage catch + breadcrumb + flag), `classify_conflict` (degraded→UNKNOWN)
- `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` — repro (B1 real-rebase staging; established at /repro, hardened at /critique)
- `tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py` — NEW (6 fail-closed tests)
- `tests/methodology/test_parallel_conflict_resolver_git_encoding.py` — count-pin 4→5 byte-mode (decode stays 9) + docstring
- `architecture/shippability.md` — #98 (repro) + #100 (guard) + #96 correction
- vault: `architecture/decisions/ADR-083-*.md`, slice-091 `design.md`/`mission-brief.md`, `architecture/drift-log.md` (Trigger)
