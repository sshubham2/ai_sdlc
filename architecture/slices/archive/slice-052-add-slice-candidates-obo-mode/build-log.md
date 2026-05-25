# Build log: Slice 052 add-slice-candidates-obo-mode

**Date**: 2026-05-20
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-05-20 00:00 BUILD: slice branch slice/052-add-slice-candidates-obo-mode created from master (WT clean except pre-existing untracked diagnose-out/)
- 2026-05-20 00:05 BUILD: T1 fixture tests/methodology/fixtures/obo_diagnose_out/ written (diagnosis.html ensure_ascii=True orig + repo/*.py evidence + backlog.golden.md)
- 2026-05-20 00:06 FINDING: pre-existing defect in build_backlog.py main() — no stdout UTF-8 reconfigure → crashes rc=2 ('charmap' codec) on Windows when a candidate title/print contains non-ASCII (e.g. emoji). backlog.md file write itself is utf-8-safe; only the terminal stdout prints crash. In-blast-radius of T2 (--obo-extract emits non-ASCII finding text to stdout → identical crash). Will fix in T2 at the shared entrypoint (sys.stdout reconfigure) — logged as in-scope DEVIATION below; backlog.md byte-output is unaffected so AC1 default-path output contract holds.
- 2026-05-20 00:07 DEVIATION: build_backlog.py shared-entrypoint stdout UTF-8 reconfigure added in T2 — rationale: --obo-extract is non-functional on the user's own Windows console without it (the slice's whole purpose); affects console encoding only, backlog.md bytes unchanged, default-path output contract (AC1) preserved; out-of-scope clause targets default-path *output*, not a crash fix on the shared process entrypoint.
- 2026-05-20 00:20 BUILD: T2/T3/T4 done — build_backlog.py +--obo-extract/--obo-write/--obo-peek (argparse mutually-exclusive group; default path dispatch-guarded, render code untouched); compiles clean
- 2026-05-20 00:25 SMOKE: mid-slice gate PASS — extract severity-order [crit,high,med,med] + raw-UTF-8; write Hard-rule-#3 SHA invariance + B1 ensure_ascii=False (no \\u escapes) + M-add-2 backslash/</script> byte-exact + collect() untouched-absent; B2 operational parity backlog.md==golden; peek in-set served & secret/sibling/../absolute/./ + unknown-id all refused; default path no traceback
- 2026-05-20 00:26 FINDING: subprocess child UTF-8 capture — a test/harness calling build_backlog.py MUST pass encoding="utf-8" to subprocess (parent cp1252 default mis-decodes the child's correct UTF-8 emoji bytes). NOT a build_backlog.py defect; codified into the T6 test harness.
- 2026-05-20 00:40 BUILD: T5 SKILL.md (--obo section + Hard-rule-#2 ADR-054 carve-out + Defer-terminal operator guidance + forbid direct Read under --obo); T6 tests/methodology/test_slice_candidates_obo.py 16 PASS (incl stderr-reconfigure fix for em-dash refusal messages); T7 risk-register R-12 (mitigating) + R-13 (open) RR-1-clean; T8 shippability row #52 path-audit-clean; T9 installed copies content-equal mod EOL
- 2026-05-20 00:45 DEVIATION: design said "plugin-manifest / drift posture unaffected" — correct for PMI-1 artifact enumeration but wrongly implied no version bump. ADR-054 + new --obo mode IS a methodology-surface behavior change (changelog Inclusion heuristic + slice-049/ADR-051 law). User-ratified (structured options) → applied v0.60.0 4-part PMI-1 bump (changelog ## v0.60.0 + VERSION + plugin.yaml + forward-synced installed ai-sdlc-VERSION & methodology-changelog) + test_v_0_60_0_obo_{entry_present_in_repo,shippability_consumer_propagation}. design.md corrected. Both Critic layers missed this → reflection "Missed by Critic".
- 2026-05-20 00:46 BUILD: AVFS-1 / MCFS-1 / PMI-1 PASS at 0.60.0

## Summary (filled at slice end)

### Plan executed
T1 fixture+golden — DONE. T2 argparse+--obo-extract — DONE. T3 --obo-write — DONE. T4 --obo-peek — DONE. T5 SKILL.md — DONE. T6 test_slice_candidates_obo.py (16 tests) — DONE. T7 risk-register R-12/R-13 — DONE. T8 shippability #52 — DONE. T9 install lock-step sync — DONE. T10 pre-finish gate + v0.60.0 4-part PMI-1 bump — DONE.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: --obo-extract severity order [critical,high,medium,medium] + raw-UTF-8; --obo-write Hard-rule-#3 SHA invariance + B1 ensure_ascii=False (no \\u escapes in annotated) + M-add-2 backslash/</script> byte-exact + collect() untouched-absent; B2 operational parity backlog.md==golden; --obo-peek in-set served, secret/sibling/../absolute/./ + unknown-finding all refused; default path no traceback. (Re-verified inside the committed test_slice_candidates_obo.py — 16 PASS.)

### Pre-finish gate
- [x] All ACs pass with evidence — test_slice_candidates_obo.py (16) covers AC1-5 + every Critic finding (B1/B2/M1/M2/M3/M4/M-add-1/M-add-2/m1); /validate-slice to formalize per-AC
- [x] Must-not-defer addressed — Hard-rule-#3 SHA assert; input validation fail-closed (missing/duplicate/malformed/zero/unknown-id); scoped-peek mechanical via --obo-peek Path.resolve(); ADR-054 written; ensure_ascii=False parity; OSDG-1 nomination physically written (R-13 + reflection-pending); _obo_log at write+peek paths
- [x] Drift-check pass — architecture/drift-log.md 2026-05-20 entry, 0 blockers/0 majors
- [x] Smoke regression — re-run inside committed test, PASS
- [x] No debug code — build_backlog.py compiles clean, no TODO/FIXME/print-debug
- [x] LINT-MOCK-1 / WIRE-1 / BRANCH-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1 / PMI-1 — all clean
- [x] BC-1 — 4 rules keyword-surfaced (architecture-path, BC-PROJ-9, BC-GLOBAL-1, Critical BC-GLOBAL-2); ALL satisfied by construction: no new tools/*.py; no git checkout/restore/stash (--obo-write writes a NEW file + asserts SHA, never reverts); no LLM-fence parsing (json.loads + fail-closed JSONDecodeError); build_backlog.py reads diagnose-out/ not architecture/**. No Critical violation; no defer needed.
- [x] Full methodology suite — 764 passed; test_install_md_correctness green (BC-PROJ-9 instruction; tool count unchanged at 26)

### Deferrals (if any)
- (none) — OSDG-1 drift-guard extension to /slice-candidates is a deliberate own-slice deferral per slice-049/051 precedent, recorded as risk-register R-13 + a next-slice nomination (NOT a must-not-defer deferral; the lock-step install sync WAS done this slice).

### Design deviations (if any)
1. **build_backlog.py shared-entrypoint stdout+stderr UTF-8 reconfigure** (Events 00:07/00:26) — pre-existing crash class (Windows cp1252) the slice's --obo path inherits; in-scope necessary fix, console-encoding-only, backlog.md bytes byte-identical so AC1 default-path output contract holds (golden test proves it). Logged, not a design.md change beyond the note.
2. **v0.60.0 4-part PMI-1 bump** (Events 00:45) — design.md/mission-brief said "plugin-manifest / drift posture unaffected", correct for PMI-1 artifact enumeration but wrongly implied no version bump. ADR-054 + new --obo mode is a methodology-surface behavior change (changelog Inclusion heuristic + slice-049/ADR-051 law). User-ratified via structured options → applied the bump + test_v_0_60_0_obo_* pair; design.md corrected ("What's new" + this note). Both Critic layers missed this → recorded for reflection "Missed by Critic" calibration.

### Files changed
- `skills/slice-candidates/build_backlog.py` — +stdout/stderr UTF-8 reconfigure; +--obo-extract/--obo-write/--obo-peek subcommands + helpers (_extract_data_block dup-detection, _collect, _sorted_findings, _obo_log); argparse mutually-exclusive dispatch; DAG/render code untouched
- `skills/slice-candidates/SKILL.md` — +`--obo interactive review mode` section; Hard rule #2 ADR-054 carve-out; "does NOT modify" notes; argument-hint
- `~/.claude/skills/slice-candidates/{SKILL.md,build_backlog.py}` — lock-step install sync (content-equal mod EOL)
- `architecture/decisions/ADR-054-scoped-source-peek-for-slice-candidates-obo-validate.md` — new (authored /design-slice, hardened at /critique M4)
- `tests/methodology/test_slice_candidates_obo.py` — new (16 tests)
- `tests/methodology/fixtures/obo_diagnose_out/{diagnosis.html,repo/*.py,backlog.golden.md}` — new fixture
- `tests/methodology/test_methodology_changelog.py` — +test_v_0_60_0_obo_{entry_present_in_repo,shippability_consumer_propagation}
- `methodology-changelog.md` (+`## v0.60.0`) + `~/.claude/methodology-changelog.md` (forward-sync)
- `VERSION` 0.59.0→0.60.0; `plugin.yaml` version 0.60.0; `~/.claude/ai-sdlc-VERSION` 0.60.0 (forward-sync)
- `architecture/risk-register.md` — +R-12 (mitigating) +R-13 (open)
- `architecture/shippability.md` — +row #52
- `architecture/slices/slice-052-*/` — mission-brief.md, design.md (+ADR-054 fixes + deviation note), critique.md, critique-review.md, milestone.md, build-log.md
- `architecture/drift-log.md` — +2026-05-20 slice-052 audit entry
