# Build log: Slice 095 harden-skill-driven-vault-writes

**Date**: 2026-06-01
**Result**: IN-PROGRESS

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-06-01 00:45 BUILD: slice-095 build start; worktree `slice/095-harden-skill-driven-vault-writes`; plan approved (phases A–G); NEEDS-FIXES carried (M1 matcher FP/FN measured here)
- 2026-06-01 00:45 DEVIATION: VERSION=0.79.0 (NOT design's 0.80.0) — rationale: 095 builds first (094 parked at critique, still 0.78.0); natural-next + gapless; user-ratified at plan gate. design.md §Sequencing note to be reconciled.
- 2026-06-01 00:45 BUILD: prereqs — CRP-1 audit clean; on branch slice/095; cwd=worktree resolves worktree tools/ (verified)
- 2026-06-01 00:46 BUILD: matcher grounding — build-slice:394 (NAW-1 bootstrap, backticked `architecture/risk-register.md` + "flip"/"adds" non-clause-start) must NOT flag; reflect:386 bare `risk-register.md` excluded; reflect:56 "→ update" needs → clause-delimiter
- 2026-06-01 00:55 BUILD: tools/vault_edit.py + tools/skill_vault_write_safety_audit.py written; both _stdout-first, exit codes correct; cwd=worktree resolves worktree tools
- 2026-06-01 01:00 TEST: SVW-1 audit on UNROUTED tree → 21 sites (fires correctly). M1 APED-1 inspection found 2 FPs + needed tuning.
- 2026-06-01 01:05 FINDING: triage:163/179 risk-register writes sit inside an UNCLOSED ```markdown fence (Triage-template fence at ~:142 never closed → inverts fence-parity for rest of file). Pre-existing TRIAGE MARKDOWN BUG, out of slice-095 scope. Recorded as DISCOVERED → fix-slice candidate. triage is project-open (not an R-32 hazard); dropped from SVW-1 exemption allowlist.
- 2026-06-01 01:08 BUILD: SVW-1 matcher APED-1 fixes — (1) exclude ~/.claude global refs (reflect:207 FP), (2) exclude hyphen-compound verbs "post-write" (reflect:209 FP). Re-run → 19 sites, ALL REAL. **M1 measured: matcher fires on 19 true sites, FP=0.** Excluded-correctly: build-slice:394, reflect:207/209/386. Known FN: triage:163/179 (fence bug, deferred), reduce:139 (bare `lessons-learned.md` → normalize-by-backtick at routing).

- 2026-06-01 01:30 BUILD: routed append-class prose (reflect ×5 + convention note, reduce, repro, user-test, validate) + exempt markers (reflect/archive/supersede deferred-rmw; discover/risk-spike project-open). reduce:139 normalized bare→backticked `architecture/lessons-learned.md`.
- 2026-06-01 01:32 TEST: SVW-1 audit on ROUTED tree → CLEAN exit 0 (26 skills, 21 sites: 10 routed, 11 exempted); exemption set == pinned allowlist (found==allow, 0 off-allowlist, 0 missing).
- 2026-06-01 01:35 SMOKE: MID-SLICE GATE PASS — (a) audit clean on routed tree; (b) audit fail-closed on planted raw write (1 violation) + clean on routed variant; (c) vault_edit append preserves both lines rc=0; ..-escape rejected rc=2. Concurrency proof = Phase D.

- 2026-06-01 02:10 BUILD: Phase E wired SVW-1 into build-slice Step-6 + validate-slice gate rosters. Phase F in-repo fan-out: plugin.yaml (+2 tools, v0.79.0), install_audit _CANONICAL_TOOLS (+2 = 38), cp1252 parity (+skill_vault to _ROOT_ONLY_TOOLS, +bespoke vault_edit test), VERSION 0.79.0, pyproject 0.79.0, changelog ## v0.79.0 (SVW-1), shippability row #102. Renamed version-sync test _at_v_0_78_0 → _0_79_0. Fixed `\`` SyntaxWarning in audit docstrings.
- 2026-06-01 02:12 TEST: in-repo audits GREEN — PMI-1 (38 tools, v0.79.0), UTF8-STDOUT-1 (38/38), SVW-1 clean, WIRE-1 clean, META-1 changelog (130 pass), version-sync, cp1252 parity, PVFS-1, INST-1 pairing, + new SVW tests (19). 222→223 pass after version-test rename.
- 2026-06-01 02:15 DEVIATION: parallel-version-bump axis (R-28/R-33, design-flagged) — AVFS-1/MCFS-1/TVFS-1 DRIFT + OSDG-1 (reflect/build-slice) FAIL because in-repo bumped to 0.79.0 but shared ~/.claude install + venv pip still 0.78.0. CAD-1 clean (agent untouched). Forward-sync to the shared install + `pip install --upgrade` is the prescribed fix but mutates the install parallel slice-094 reads + risks the editable-master link → CHECKPOINTING for user direction before touching the shared install.

## Summary (filled at slice end)

### Plan executed
(Phases A–G — status filled per task at slice end.)

### Mid-slice smoke gate
**Result**: PENDING

### Pre-finish gate
(filled at slice end)

### Deferrals (if any)
(none yet)

### Design deviations (if any)
- VERSION 0.79.0 vs design.md §Sequencing note's planned 0.80.0 (user-ratified; 095 builds first). To update design.md §Sequencing note in Phase F.

### Files changed
(filled at slice end)
