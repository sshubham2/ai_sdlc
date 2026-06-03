# Build log: Slice 107 inventory-vault-flip-prose-surface

**Date**: 2026-06-03
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c; one line per significant action)

- 2026-06-03 10:52 BUILD: plan approved (full build, Test-first ordering); entering Phase A (scaffold commit + failing-tests-first)
- 2026-06-03 10:53 BUILD: scaffold committed on slice/107 (31c8bc3)
- 2026-06-03 10:55 TEST: wrote tests/methodology/test_vault_flip_prose_inventory.py (11 functions) — RED (ModuleNotFoundError, WRITTEN-FAILING) as expected
- 2026-06-03 10:58 BUILD: implementing tools/vault_flip_prose_inventory.py (Phase B)
- 2026-06-03 11:10 BUILD: tool runs — 318 enumerated (AC1 ✓); distribution 183 rewrite / 9 historical / 2 doc-example / 124 needs-human (90 code-no-signal + 34 conflicting)
- 2026-06-03 11:14 FINDING: design-is-wrong-mid-build — the B2-ratified inline-code→needs-human default yields 124 needs-human, but corpus (AP-3) shows these are overwhelmingly LIVE operational refs (`see \`architecture/triage.md\``, drop-into paths). Recalibrated ruleset (in-code default→rewrite-at-flip; narrow anchor markers; needs-human reserved for genuine op+anchor conflict) yields 306 rewrite / 8 needs-human / 4 doc-example — still honors B2 (operational→on-checklist, doc-example=plain-prose only). HALT for user decision.
- 2026-06-03 11:16 DEVIATION: ruleset recalibration — user-ratified (AskUserQuestion "Recalibrate + log deviation"). Narrowed anchor markers further (dropped over-broad "supersed") → final distribution 316 rewrite-at-flip / 0 historical-anchor / 2 doc-example / 0 needs-human. B2 goal preserved (operational paths ON checklist; doc-example=plain-prose only). The needs-human bucket + _DISPOSITION table remain as the fail-closed mechanism for future drift (exercised by unit tests).
- 2026-06-03 11:40 DEVIATION: baseline storage — FORCED by AC5/M1 disjointness (not discretionary). The design's in-module (path,value,klass) multiset baseline = 316 slashed-path tuples in tools/*.py, which readiness_audit classifies as needs-human (collection-member + "/"), tripping slice-106's baseline. Replaced with an in-module SHA-256 of the sorted multiset (no slashed literals → readiness clean). Gate behavior identical (exit 2 on ANY multiset change); full enumerated inventory remains the --json output. AC3 "in-module" + AC5 "disjoint" both satisfied.
- 2026-06-03 11:50 TEST: 15/15 prose-inventory tests PASSING (Test-first plan rows green)
- 2026-06-03 11:52 SMOKE: mid-slice PASS — prose inventory 318 enumerated exit 0 (0 needs-human); readiness_audit --strict exit 0 (disjointness); suite 15/15
- 2026-06-03 12:30 TEST: full methodology suite 1404 passed (build commit 9baa184)
- 2026-06-03 12:45 BUILD: /code-review FINDINGS (0B/2M/3m) — ALL addressed in-round: M1 broadened _OP_VERBS (frontmatter Reads/Produces → on-checklist; distribution 316/0/2/0 → 318/0/0/0, re-pinned baseline+floor); M2 added test_disposition_override_fires_and_is_column_keyed (ADR-097 mechanism now covered on a non-empty table); m1 AP-1 docstring clarified; m2 provenance comment; m3 see/note verb reconciliation

## Summary

### Plan executed
- **Phase A** ✓ — scaffold committed (31c8bc3); 11 Test-first tests written failing-first.
- **Phase B** ✓ — `tools/vault_flip_prose_inventory.py` implemented; recalibrated against the real corpus (user-ratified deviation); SHA-256 baseline (AC5/M1 deviation); 16/16 tests green (incl. /code-review M2 disposition-override test).
- **Phase C** ✓ — wired into `plugin.yaml` (PMI-1, rule ADR-096), `tools/install_audit.py` (INST-1), `architecture/shippability.md` row 113 (RPCD-1/SCPD-1); m-add-1 `_RESIDUAL` = 5 bare-`graphify vault architecture` args.
- **Phase D** ✓ — mid-slice smoke PASS.
- **Phase E** ✓ — full audit battery green; INSTALL.md tool-count 41→42 + 3 count-consumer pins repointed (AP-10 fan-out).

### Acceptance criteria
- **AC1** ✓ — boundary-free `re.finditer` matcher enumerates all **318** literals (all-matches-per-line; `code-review.md:103` = 5 intra-line matches). `test_enumerates_full_corpus_318_all_matches_per_line`.
- **AC2** ✓ — context ruleset; `doc-example` reserved for plain prose; `needs-human` fail-closed bucket (anchor+in-code). Distribution 318/0/0/0 (AS-BUILT recalibration in-code→rewrite-at-flip default + /code-review M1 verb-broadening; B2 goal preserved — all operational refs ON checklist).
- **AC3** ✓ — in-module `_BASELINE_SHA256` + per-class count floor; `--strict` exit 2 on multiset change / shrink (non-vacuous: `test_strict_drift_on_new_literal`).
- **AC4** ✓ — non-vacuous by mutation; 5-tuple disposition key (M2 cross-line + M-add-1 column-offset intra-line); `test_no_ambiguous_duplicate` + `test_no_intra_line_ambiguous_multimatch`.
- **AC5** ✓ — disjointness: `vault_flip_readiness_audit --strict` exits 0 (the SHA-256 baseline keeps `tools/*.py` free of slashed literals that would trip slice-106's baseline). `test_disjoint_no_new_production_must_rewrite`.

### Mid-slice smoke gate
**Result**: PASS — prose inventory 318 enumerated, exit 0 (0 needs-human); `vault_flip_readiness_audit --strict` exit 0; suite 15/15.

### Pre-finish gate
- [x] All ACs pass with evidence — see validation.md (pending /validate-slice)
- [x] Must-not-defer addressed (fail-closed needs-human; UTF8-STDOUT-1; line-anchored AP-1; no self-pollution AC5/M1; PMI-1/INST-1)
- [x] Drift-check pass (full mode; drift-log slice-107 entry; DCE-1 exit 0)
- [x] Smoke regression check pass
- [x] No debug code (one-shot generators `_gen_baseline.py`/`_gen_hash.py` deleted post-use)
- [x] All Step-6 audits exit 0 (PMI-1/INST-1/UTF8-STDOUT-1/PCA-1/BCI-1/MCFS-1/STP-1/AVFS-1/TVFS-1/NAW-1/SVW-1/TF-1/WIRE-1/BRANCH/CRP-1/DCE-1/BC-1/LINT-MOCK-1 + readiness --strict disjointness)

### Deferrals
- None.

### Design deviations
1. **Ruleset recalibration** (user-ratified, AskUserQuestion) — as-designed inline-code→needs-human (124 entries) was corpus-mis-calibrated; shipped in-code/operational→`rewrite-at-flip` default; /code-review M1 broadened the verb set so two frontmatter paths join the checklist → final 318/0/0/0. B2's goal preserved. design.md §ruleset + mission-brief AC2 carry ⚠ AS-BUILT callouts. **Updated in design.md? yes.**
2. **Baseline storage** (FORCED by AC5/M1, not discretionary) — in-module SHA-256 (`_BASELINE_SHA256`) instead of inlined slashed-path tuples (which `readiness_audit` would flag, tripping slice-106). Identical gate behavior; full inventory via `--json`. design.md §Baseline/§Data-model + mission-brief AC3 carry ⚠ AS-BUILT callouts. **Updated in design.md? yes.**

### Files changed
- `tools/vault_flip_prose_inventory.py` (new)
- `tests/methodology/test_vault_flip_prose_inventory.py` (new — 16 tests)
- `plugin.yaml`, `tools/install_audit.py`, `architecture/shippability.md` (row 113), `INSTALL.md` (41→42)
- `tests/methodology/test_utf8_stdout_regression.py` (cp1252 coverage +1), `test_pulse_worktree_resolver_tool_inventory.py` + `test_stranded_slice_audit_tool_inventory.py` (count-pin 41→42)
- `architecture/decisions/ADR-096-*.md` + `ADR-097-*.md` (new), slice artifacts, `architecture/drift-log.md` (slice-107 entry)
