# Build log: Slice 113 bulk-convert-remaining-skills-to-vault-seam

**Date**: 2026-06-04
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-06-04 BUILD: prerequisites green — CRP-1 clean, worktree on slice/113, main tree on master.
- 2026-06-04 BUILD: Phase A — classified 287 skill literals via discriminator → 174 convert / 113 carve.
- 2026-06-04 FINDING (AP-3 build-time recalibration): first discriminator pass over-converted 10 ABBREVIATED active-folder refs — the regex `slices/slice-(\d+|NNN)` missed wildcard/placeholder/ellipsis forms (`slices/*/`, `slices/<slice-id>/`, `slices/slice-*/`, `slices/…`). These are class-5 (R-32.a, stay concrete). Reset skill files + re-converted with corrected rule (`architecture/slices/X` carves UNLESS X is `_index.md`/`action-points.md`/`archive`/bare). Result: 184→174 convert, 103→113 carve. Exactly the slice-112 "AP-3 again" lesson, live.
- 2026-06-04 BUILD: applied conversion — 174 literals across 25 skill SKILL.md; total 303→129, rewrite-at-flip 301→127 (verified --json).
- 2026-06-04 BUILD: op-gate seam-aware — added `_OP_SINK_RE` + `_OP_SINK_TOKEN_RE` (matcher + extractor, B2); scan_op_file wired to both.
- 2026-06-04 BUILD: re-pinned EXPECTED_TOTAL=129, _CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]=127, _BASELINE_SHA256=1147b37…; _CONVERTED_FILES grown to 24 (code-review EXCLUDED — M3 real collisions); _CONVERTED_CARVEOUTS 4→43 entries; docstring narrative re-pinned (AP-10).
- 2026-06-04 FINDING (M3 collision check): code-review has 5 REAL same-value collisions (pathspec value == converted shared-aggregate value, e.g. `architecture/slices/_index.md`) → un-ratcheted + documented. slice has 1 NON-exploitable ellipsis collision (`architecture/slices/…`) → ratcheted with documented note.
- 2026-06-04 FINDING (M4): slice:264's main-tree-fallback active-folder ref was correctly CARVED by the corrected discriminator → line unchanged → slice:264 op-allowlist hash UNCHANGED. No 4th re-hash needed (verified --op-gate --json: slice:264 not OP_UNROUTED).
- 2026-06-04 BUILD: re-hashed 3 _OP_ALLOWLIST entries (build-slice:407/commit-slice:216/design-slice:240 — their lines converted).
- 2026-06-04 TEST: inventory `--strict` exit 0 (36 files / 129 literals / 127 rwf / 2 doc-example).
- 2026-06-04 TEST: op-gate `--strict` exit 0, per-class {6,11,23,0} (B2 — seam-aware gate keeps all 40 ops visible, NO floor loosening).
- 2026-06-04 TEST: test_vault_flip_prose_inventory.py + test_vault_flip_op_gate.py + test_bcr_1_backlog_round_trip.py — 43 passed (m1 5-match pin + ratchet + BCR-1 all green via pathspec/diagnose-out carve-out).
- 2026-06-04 TEST: test_build_slice_skill_dirty_tree_resolution.py + test_code_review_skill.py — green (carve-out guards held). test_validate_slice_skill.py:65 FAILED (B1 command-arg) → repointed `architecture/shippability.md`→`<vault>/shippability.md` (AP-13).
- 2026-06-04 BUILD: added 3 `<vault>/`-sink op-gate tests (B2/AP-5) + the M3 differing-value ratchet mutation test (slice/SKILL.md). Both pass (49-test subset green).
- 2026-06-04 FINDING (EOL): the worktree was checked out with CRLF (main tree is LF per `.gitattributes skills/**/SKILL.md eol=lf`); `test_guarded_md_files_have_no_crlf_in_working_tree` failed. Normalized 25 worktree skill SKILL.md (+ agents/slice-queue, no-op for untouched) CRLF→LF. Inventory reads via universal-newlines, so baseline/hashes unaffected. No spurious diff on untouched files (LF matched index).
- 2026-06-04 BUILD: forward-synced 23 converted skill SKILL.md to `~/.claude/skills/` (10 of the 13 OSDG-1-guarded converted; the other 3 guarded — critique-review/query-design/slice-candidates — were unconverted, no sync needed).
- 2026-06-04 TEST: FULL SUITE green — 1617 passed, 2 skipped (no collateral prose-assertion breakage).
- 2026-06-04 TEST: 18 Step-6 audits all green — SVW-1 (filename-keyed, NOT blinded by conversion — unlike op-gate), PCA-1, UTF8-STDOUT-1, PMI-1, INST-1, CAD-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, CRP-1, BRANCH, WIRE-1, mock-budget, DCE-1, BC-1.
- 2026-06-04 BUILD: shippability AP-10 fan-out — rows 113/117/118 live-count refs re-pinned 303→129 / 301→127; added row 119 (slice-113). Path audit clean.
- 2026-06-04 BUILD: drift-log.md slice-113 `**Trigger**` section appended (vault aligned); DCE-1 clean.
- 2026-06-04 FINDING (/code-review B1): the code-Critic caught 3 git-pathspec PROSE mirrors in `code-review.md:102/104/105` (`<vault>/decisions/**` etc.) wrongly converted — they lack the `:(exclude)` syntax ON their line (only the surrounding block has it), so the discriminator saw them as shared-aggregate. A real must-not-defer violation the full suite missed (`test_code_review_skill.py` pins the COMMAND, not the prose). The AP-4 code-Critic value.
- 2026-06-04 BUILD (/code-review B1 fix): reverted the 3 prose literals to concrete `architecture/`; re-pin cascade — `EXPECTED_TOTAL` 129→132, `_CLASS_COUNT_FLOOR[rewrite-at-flip]` 127→130, `_BASELINE_SHA256`→99480a6…, docstring (171 converted / 116 carve-outs), shippability rows 113/117/118/119. code-review installed copy re-synced. (`_CONVERTED_FILES`/`_CONVERTED_CARVEOUTS`/`_OP_ALLOWLIST` unaffected — code-review un-ratcheted.)
- 2026-06-04 BUILD (/code-review m1 fix): the 3rd `<vault>/`-sink op-gate test was vacuous against an extractor-revert (OP_UNROUTED both ways); strengthened it to assert the full token is extracted (`risk-register.md in value`) → now genuinely extractor-sensitive (verified the code-Critic's mutation).
- 2026-06-04 TEST: --strict 0 + --op-gate --strict 0 (132/130); 53-test subset green (incl. strengthened m1 test + reverted code-review pathspec test). Full suite re-run after the cascade.

## Summary

### Plan executed
All 4 phases (A enumerate / B convert+op-gate / C re-pin / D forward-sync+gates) completed. SHIPPED.

- **Phase A**: discriminator classification → 174 convert / 113 carve (→ **171 convert / 116 carve** after the /code-review B1 revert of 3 `code-review.md` git-pathspec prose literals). **AP-3 recalibration**: the active-folder regex was broadened to catch wildcard/placeholder/ellipsis forms (`slices/*/`, `slices/<x>/`, `slices/…`) after the first pass over-converted 10.
- **Phase B**: 174 literals converted across 25 skill SKILL.md; op-gate made seam-aware (`_OP_SINK_RE` + `_OP_SINK_TOKEN_RE` extractor in lockstep, B2).
- **Phase C**: `EXPECTED_TOTAL`=**132**, `_CLASS_COUNT_FLOOR[rewrite-at-flip]`=**130** (final, post-/code-review-B1), `_BASELINE_SHA256` re-pinned; `_CONVERTED_FILES`=24, `_CONVERTED_CARVEOUTS`=43; 3 `_OP_ALLOWLIST` re-hashes; docstring narrative (AP-10).
- **Phase D**: 23 skills forward-synced; shippability rows 113/117/118/119; drift-log; all gates.

### Mid-slice smoke gate
**Result**: PASS — `--json` total math deterministic (converted files contribute 0 rewrite-at-flip); op-class breakdown `{6,11,23,0}` stable (no OP_UNROUTED, no floor shrink); `-k skill_drift` green (after forward-sync).

### Pre-finish gate
- [x] All acceptance criteria PASS with evidence (→ validation.md): AC1 conversion + carve-outs (`--json` 132/130, post-B1); AC2 inventory+op-gate re-pin (`--strict` 0, `--op-gate --strict` 0 + `{6,11,23,0}`, ratchet mutations green); AC3 13-skill forward-sync (`-k skill_drift` green); AC4 consumer contracts (BCR-1 green, validate-slice:65 repointed, shippability re-pinned); AC5 flip-neutral (default `architecture/`, full suite 1617 green) + residual recorded.
- [x] Must-not-defer addressed (seam-aware op-gate incl. extractor; carve-out classes concrete; BCR-1 verified; count fan-out incl. docstring; forward-slash `_CONVERTED_FILES`; git-pathspecs carved; roster=13).
- [x] /drift-check (DCE-1) clean
- [x] Mid-slice smoke still passes
- [x] No new TODOs / FIXMEs / debug prints
- [x] All Step-6 audits green (18)

### Deferrals (if any)
- **Agent-prose surface** (4 agent files: code-review/critic-calibrate/critique-review/diagnose-narrator) — TRI-1-ratified M1 disposition (path b): deferred to a `convert-agent-prose-to-vault-seam` follow-on (each needs its own ADR-105 embedded resolver-context note). Registered in slice-queue at /reflect. User-approved.
- **M3** (ACCEPTED-PENDING): resolved at build — `code-review` un-ratcheted (real same-value pathspec collisions); slice ratcheted with the non-exploitable `…`-ellipsis collision documented + a differing-value mutation test proving non-vacuity.

### Design deviations (if any)
- **AP-3 active-folder discriminator broadening** (in design as the path-shape rule; the live corpus required catching wildcard/placeholder/ellipsis active-folder forms the literal `slice-NNN` regex missed). Reflected in build-log + the discriminator's "carves UNLESS `_index`/`action-points`/`archive`/bare" form. Not an ADR change (applies ADR-105 class-5).
- **M4 resolved cleanly**: slice:264's main-tree-fallback was correctly carved by the broadened discriminator → line unchanged → NO 4th `_OP_ALLOWLIST` re-hash (verified by execution, AP-2).

### Files changed
- `tools/vault_flip_prose_inventory.py` (seam-aware op-gate + re-pins + `_CONVERTED_FILES`/`_CONVERTED_CARVEOUTS` + docstring)
- 23 × `skills/<name>/SKILL.md` (converted) + their installed `~/.claude/` copies
- `tests/methodology/test_vault_flip_op_gate.py` (+3 `<vault>/`-sink tests), `test_vault_flip_prose_inventory.py` (+M3 mutation test), `test_validate_slice_skill.py` (command-arg repoint)
- `architecture/shippability.md` (rows 113/117/118 re-pin + row 119), `architecture/drift-log.md` (slice-113 section)
- `architecture/decisions/ADR-106-*.md` (new), slice folder artifacts
