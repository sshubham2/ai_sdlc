# Build log: Slice 112 make-prose-vault-location-agnostic

**Date**: 2026-06-04
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-06-04 12:40 BUILD: plan-mode plan approved (Test-first; pilot=CLAUDE.md+agents/critique.md; hash-keyed carve-out allowlist refinement flagged + approved)
- 2026-06-04 12:42 BUILD: APED-1 fact-find — CLAUDE.md convert 4 (:3/:6/:14/:51) carve-out 3 (:5 definitional, :43×2 diagnose-out); agents/critique.md convert 7 (:42/:160/:186/:188/:190/:203/:256) carve-out 2 (:125 slice-queue, :260 active-folder); corpus total 313
- 2026-06-04 12:43 DEVIATION: design said definitional→plain-prose only; build adds a hash-keyed `_CONVERTED_CARVEOUTS` (path, sha256(value)) allowlist for the 4 OPERATIONAL carve-outs that stay in-code in converted files (diagnose-out ×2/slice-queue/active-folder) — slice-107 AC5 disjointness forbids inlining slashed literals in tools/*.py. design.md/ADR-105 updated as-built.
- 2026-06-04 12:55 BUILD: tool extended (_CONVERTED_FILES + _CONVERTED_CARVEOUTS + converted_file_regressions ratchet folded into --strict); 9 TF-1 tests WRITTEN-FAILING
- 2026-06-04 13:05 FINDING: APED-1 caught 2 prose-classification bugs in NEW convention text — "historical anchors" marker beside in-code diagnose-out → needs-human (exit 2); plain-prose architecture/ sharing a line with read/write op-verbs → rewrite-at-flip. Fixed by re-wording around the line-anchored classifier (AP-3).
- 2026-06-04 13:08 BUILD: CLAUDE.md (5 ops→<vault>/, definitional→plain-prose) + agents/critique.md (7 ops→<vault>/, self-sufficient note, 2 carve-outs) converted; re-pin 313→303 (BASELINE/FLOOR=301/EXPECTED_TOTAL=303 + shippability 113/117 + new row 118)
- 2026-06-04 13:10 BUILD: agents/critique.md forward-synced to ~/.claude/ (CAD-1 clean)
- 2026-06-04 13:12 SMOKE: mid-slice — 25/25 convention+inventory tests PASS; inventory --strict exit 0 (303; 301/0/2/0; regressions []; needs_human []); readiness --strict exit 0 (AC5); op-gate --strict 6/11/23/0 UNCHANGED (B2 sidestepped — skills untouched)
- 2026-06-04 13:30 TEST: full suite 1613 passed / 2 skipped after R-33 fix (140s)
- 2026-06-04 13:28 DEVIATION: R-33 — worktree's stale slice-queue.md (pre-112 rewrite-318 candidate, bare-dir agents/skills blast-radius) failed test_committed_slice_queue_md_blast_radius...; PASSES on master (Step-6.5 regen already path-shaped). Synced via `git checkout master -- architecture/slice-queue.md` (R-33 worktree-current mitigation). NOT a slice-112 regression.
- 2026-06-04 13:40 BUILD: WIRE-1 (zero-row matrix: removed the `—` placeholder row) + TF-1 (added AC5 test_followon_remainder_worklist_complete + row) fixed → both exit 0; DCE-1 drift-log marker appended via `vault_edit append` → exit 0
- 2026-06-04 13:42 BC-1: BC-PROJ-3 + BC-GLOBAL-2 (always:true Critical) ATTESTED — this slice performs NO destructive `git checkout`/`restore`/`stash` revert of UNCOMMITTED work; the lone `git checkout master -- architecture/slice-queue.md` synced a stale COMMITTED shared ledger (R-33), no uncommitted WIP touched.
- 2026-06-04 13:55 TEST: FINAL full suite 1613 passed / 2 skipped (135s); all Step-6 audits exit 0
- 2026-06-04 14:05 BUILD: /code-review 0B/1M/2m. M1 (FBCD-1(c) recurrence — stale module docstring 313/0-doc-example, slice-111 m5 class) FIXED: docstring → 301/0/2/0 + 303 + slice-112 transition. m1 (durability claim) scoped in ADR-105. m2 (bare-arg residual) deferred to follow-on. Re-verified: 26 convention/inventory tests pass; --strict exit 0; UTF8 exit 0.

## Summary

### Plan executed
1. APED-1 fact-find — DONE (CLAUDE.md convert 5 / carve 2; agent convert 7 / carve 2; 313 corpus).
2. 9 (→10) TF-1 tests written WRITTEN-FAILING then PASSING — DONE (`test_prose_vault_seam_convention.py` 7 + `test_vault_flip_prose_inventory.py` +3).
3. Tool extended (`_CONVERTED_FILES` + hash-keyed `_CONVERTED_CARVEOUTS` + `converted_file_regressions` ratchet in `--strict`) — DONE.
4. CLAUDE.md converted (5 ops→`<vault>/`, definitional→plain-prose resolution-rule bullet) — DONE.
5. agents/critique.md converted (7 ops→`<vault>/`, self-sufficient `<vault>` note, 2 carve-outs) + forward-synced (CAD-1) — DONE.
6. APED-1 re-pin 313→303 (`_BASELINE_SHA256` / `_CLASS_COUNT_FLOOR`=301 / `EXPECTED_TOTAL`=303 + shippability rows 113/117 + new row 118) — DONE.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `vault_flip_prose_inventory --json` → converted files carry only the 4 sanctioned carve-outs + 2 plain-prose definitionals; `converted_file_regressions` []; `needs_human` []. `--strict` exit 0 (303; 301/0/2/0). `readiness --strict` exit 0 (AC5). `--op-gate --strict` 6/11/23/0 UNCHANGED (B2 sidestepped — CLAUDE.md/agents not op-gate-scanned).

### Pre-finish gate
- [x] All ACs pass — AC1 convention+ADR; AC2 ratchet (mutation-proven, baseline-independent); AC3 pilot converted + agent forward-synced (CAD-1); AC4 mixed-state + seam=architecture default; AC5 remainder worklist enumerable.
- [x] Must-not-defer addressed — CAD-1 forward-sync; no pre-flip behaviour change (default→architecture/); ratchet fails-closed + baseline-independent + forward-slash-keyed; re-pin fan-out complete (3 constants + shippability 113/117); UTF8-STDOUT-1 preserved; historical anchors preserved; agent self-sufficiency (M-add-1); definitional plain-prose (M2/M-add-2).
- [x] Drift-check pass (DCE-1 marker appended via `vault_edit append`)
- [x] Mid-slice smoke regression pass
- [x] No debug code / TODOs
- [x] Full Step-6 audit battery exit 0 (BRANCH/TF-1/PCA-1/PMI-1/INST-1/UTF8/SVW-1/VWS-1/NAW-1/STP-1/BCI-1/MCFS-1/AVFS-1/TVFS-1/WIRE-1/CRP-1/DCE-1/BC-1) + full suite 1613 pass.

### Deferrals
- m2 (ACCEPTED-PENDING) — exact remainder pinned at build: 301 rewrite-at-flip total, of which the not-yet-converted follow-on worklist = 301 − 4 sanctioned carve-outs in the 2 pilot files = **297 literals across ~24 skill files** (the bulk-convert-remaining-skills-to-vault-seam follow-on; slice-queue candidate registered at Step 6.5).
- B1/B2/B3/M1 (DEFERRED at TRI-1) — skill conversion + op-gate floor re-pin + BCR-1 anchor repoint → the follow-on slice.

### Design deviations
- **Hash-keyed `_CONVERTED_CARVEOUTS` allowlist** (vs design's "plain-prose only"): added for the 4 operational carve-outs that stay in-code in converted files; value-keyed (M-add-2-durable) + hash-keyed (slice-107 AC5 disjointness). Updated in design.md §Components + ADR-105 (AS-BUILT).
- **Build-time prose recalibration (AP-3)**: re-worded the new convention prose so definitional literals avoid anchor-markers + op-verbs on their physical line → `doc-example`. Updated in design.md (AS-BUILT).
- **R-33**: synced the worktree's stale `slice-queue.md` from master (`git checkout master -- …`); not a slice regression.

### Files changed
- `tools/vault_flip_prose_inventory.py` (ratchet + carve-out allowlist + re-pinned constants)
- `CLAUDE.md` (resolution-rule bullet + 5 ops→`<vault>/`)
- `agents/critique.md` (self-sufficient note + 7 ops→`<vault>/`) + forward-synced `~/.claude/agents/critique.md`
- `tests/methodology/test_prose_vault_seam_convention.py` (new), `tests/methodology/test_vault_flip_prose_inventory.py` (+3 ratchet tests + imports)
- `architecture/shippability.md` (rows 113/117 re-pin + new row 118), `architecture/drift-log.md` (DCE-1 marker)
- slice artifacts: mission-brief.md / design.md / ADR-105 / critique.md / critique-review.md / milestone.md
- `architecture/slice-queue.md` (R-33 sync from master)
