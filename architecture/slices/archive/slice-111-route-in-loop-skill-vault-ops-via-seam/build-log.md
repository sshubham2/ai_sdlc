# Build log: Slice 111 route-in-loop-skill-vault-ops-via-seam

**Date**: 2026-06-04
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-06-04 PLAN: approved (one slice, Phase A → mid-slice smoke → Phase B); BRANCH-3 worktree on slice/111
- 2026-06-04 BUILD: tools/vault_edit.py — added `move` subcommand (_cmd_move + subparser; final-landing-path dest guard, M2; shutil.move; no CAS)
- 2026-06-04 TEST: tests/methodology/test_vault_edit_cli.py — +7 move cases; 23 passed
- 2026-06-04 BUILD: AC1 routing — reflect:320 + archive:51 archive `mv` → `vault_edit move`; drift-check:109 drift-log → `vault_edit append`
- 2026-06-04 FINDING: explanatory prose "NOT a literal `mv architecture/...`" re-introduced `architecture/` literals (would inflate the inventory count AND be flagged by the op-gate) — rephrased to drop the `architecture/` token (APED-1 catch)
- 2026-06-04 BUILD: M1 re-pin — inventory 318→313 (K=5 measured live); _BASELINE_SHA256=602c62fd…, _CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]=313, EXPECTED_TOTAL=313; FBCD-1 fan-out (docstring, test name→count-agnostic, shippability #113)
- 2026-06-04 BUILD: OSDG-1 re-sync installed /reflect; m-add-5 hand-sync installed /archive + /drift-check
- 2026-06-04 SMOKE: mid-slice gate PASS — inventory --strict clean @313; 40 tests pass (inventory + vault_edit + reflect_skill_drift)
- 2026-06-04 BUILD: tools/vault_flip_prose_inventory.py — added `--op-gate` mode (4 classes, _IN_LOOP_SKILLS pinned, destination-keyed, _OP_ALLOWLIST hash-keyed for AC5 disjointness)
- 2026-06-04 FINDING: detector v1 over-fired (21 OP_UNROUTED) — bare `add` matched slice-names + "Add --flag"; verb-after-literal caught descriptive prose; `slice-NNN` placeholder missed by `slices/slice-\d+`. Fixed: `git add` bigram only, verb-before-literal, `slices/slice-(?:\d+|NNN)`. → 6 residual, all hand-classified into _OP_ALLOWLIST. Gate green (0 OP_UNROUTED). (APED-1)
- 2026-06-04 FINDING: _OP_ALLOWLIST inlining prose lines re-introduced `architecture/` literals into tools/*.py → vault_flip_readiness_audit AC5-disjointness regression. Fixed by hash-keying the allowlist (slice-107 SHA-256 precedent). test_disjoint green.
- 2026-06-04 TEST: tests/methodology/test_vault_flip_op_gate.py (new) — 18 cases (non-vacuity, B2 dual-literal, M-add-1 out-of-scope+still-bites, non-over-flag, git-add forms, real-corpus-green); 33 pass with inventory
- 2026-06-04 DEVIATION: design said "wire op-gate into /build-slice Step 6 + /validate-slice" — but m2 verification shows the flip-prep precedent (slice-100 readiness audit, slice-107 prose inventory) wires NONE into Step 6; they are suite-test + shippability enforced, no RULE-ID. Deviated to the precedent: op-gate enforced via test_vault_flip_op_gate.py (pre-finish suite) + shippability row. NOT a build-slice/validate-slice edit. Consequence: OSDG-1 re-sync narrows to {/reflect}; MEPD-1 EXCLUDE precedent confirmed (m2 resolved). Sound simplification (less surface, convention-aligned); design.md/mission-brief/ADRs updated.
- 2026-06-04 BUILD: m-add-3 — added query-design:59 to _RESIDUAL (6 bare-arg sites); shippability "5 bare"→"6"
- 2026-06-04 TEST: full suite 1599 passed (138s) — no regression
- 2026-06-04 BUILD: shippability row #117 added (pipe-free, 7 pipes); drift-log marker appended via vault_edit append (dogfood) — DCE-1 clean
- 2026-06-04 TEST: Step-6 audits all green — branch/CRP-1/wiring(after zero-row fix)/PCA-1/BCI-1/MCFS-1/STP-1/AVFS-1/TVFS-1/NAW-1/SVW-1/UTF8-STDOUT-1/PMI-1/CAD-1/index-thinness
- 2026-06-04 FINDING: wiring_matrix_audit flagged a `| — | — | — | ... |` placeholder row (missing-cells) — zero-new-module slices need header+separator ONLY; fixed design.md to the zero-row form
- 2026-06-04 TEST: SRSC-1 shippability_runner 116/116 PASS (row #117 + all rows green) — BC-PROJ-7 discharged
- 2026-06-04 BUILD: BC-1 --strict exit 0 (Critical BC-PROJ-3/BC-PROJ-7/BC-GLOBAL-2 acked); BC-PROJ-10 MEPD-1(b) classification added to design.md; mock-budget clean
- 2026-06-04 BUILD: pre-finish gate PASS — Result SHIPPED
- 2026-06-04 REVIEW: /code-review code-Critic — no blockers, 2 majors + 5 minors (all real AP-4 classifier-soundness; gate honest today, holes latent). All ACCEPTED-FIXED: M1 (seam-token must follow the governing verb, not line-wide — decoy-masking closed), M2 (single-clean-move-only dest collapse; multi-verb line flags all targets), m2 (error names --from/--to), m3 (same-path move → exit 2), m5 (row 117 ordered after 116 + 69/318 provenance restored); m1/m4 documented.
- 2026-06-04 TEST: +6 adversarial tests (M1 decoy / M2 multi-verb / m2 / m3 + 2 behavior-preserving guards); op-gate still 6/11/23/0 (fixes behavior-preserving); full suite 1605 passed (134s)

## Summary (filled at slice end)

### Plan executed
- Phase A (AC1 + vault_edit move + M1 re-pin): COMPLETE — mid-slice smoke PASS.
- Phase B (AC2 op-gate + APED-1 + tests + wiring + shippability): IN-PROGRESS.

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `vault_flip_prose_inventory --strict` exit 0 (313 literals); `pytest test_vault_flip_prose_inventory.py test_vault_edit_cli.py test_reflect_skill_drift.py` = 40 passed.

### Pre-finish gate
- [x] All ACs pass — AC1 (`vault_edit move` + routing, 23 vault_edit tests), AC2 (op-gate green 0 OP_UNROUTED + 18 op-gate tests), AC3 reversible (no physical move / no `git rm` / no `_vault_paths` change; revertible by `git revert`).
- [x] Must-not-defer addressed — OSDG-1 re-sync /reflect; m-add-5 hand-sync /archive+/drift-check; AC2-gate non-vacuity + non-over-flag + dual-literal + M-add-1 (corpus-executed, APED-1); AP-4 code-Critic pending (/code-review, next); `OP_DEFERRED_TO_FLIP` gate-visible + R-32.a; M1 re-pin done; M2 dest-guard done; cross-store R-32.b recorded; no `_vault_paths` change.
- [x] /drift-check full mode → drift-log marker appended via `vault_edit append`; DCE-1 clean.
- [x] Full suite 1599 passed (no regression); seeded flip-sim unaffected.
- [x] No new TODOs/FIXMEs/debug prints (grep clean).
- [x] All Step-6 audits pass (BC-1 --strict / WIRE-1 / BRANCH / CRP-1 / PCA-1 / BCI-1 / MCFS-1 / STP-1 / AVFS-1 / TVFS-1 / NAW-1 / SVW-1 / UTF8-STDOUT-1 / DCE-1 / PMI-1 / CAD-1 / mock-budget / SRSC-1 116/116).

### BC-1 dispositions
- **Critical** BC-PROJ-3 / BC-GLOBAL-2 (destructive git-revert): attested — no `git checkout`/`restore`/`stash` revert of uncommitted work; all slice work preserved in the worktree. Acked.
- **Critical** BC-PROJ-7 (new-audit-tool obligations): no NEW `tools/*.py` module added (extended existing `vault_edit` + `vault_flip_prose_inventory`, both already cp1252-covered — UTF8-STDOUT-1 green); shippability #117 pipe-free (7 pipes) + SRSC-1 116/116 PASS. Acked.
- **Important** BC-PROJ-4 / BC-PROJ-17 (gate/classifier real-corpus execution): ADDRESSED — op-gate EXECUTED against the real corpus at build + mid-slice (per-class distribution 6/11/23/0 inspected; the bare-`add` exclusion + `git add` bigram + inflected-verb handling were direct corpus-execution findings; 3-iteration recalibration). Test-first was false but the corpus-execution + recalibration discipline was followed.
- **Important** BC-PROJ-10 (Inclusion-heuristic): ADDRESSED — `MEPD-1(b) why-none discharged` classification added to design.md decisions table (precedent slice-106/109/110, META-1 vacuous — no new RULE-ID).
- **Important** BC-PROJ-5 (count re-pin from one anchor): the 318→313 re-pin was driven from the single authoritative anchor (live `vault_flip_prose_inventory --json` / `audit_root`); all 3 pins + docstring + test reconciled to it. No identifier-FAMILY rename (one test renamed count-agnostic).
- **Important** BC-PROJ-8 (live vault reads): op-gate reads `skills/**/SKILL.md` live (no git show/diff).
- **Important** BC-PROJ-1/2/6/9/11/16, BC-GLOBAL-1: N/A this slice (no subagent fan-out; no LLM-fence/structured-output parsing added — op-gate reuses the slice-107 static fence-tracking; no risk-status flip; no tools module add/remove → INSTALL.md count unchanged; no INSTALL/README edit; no VERSION bump).

### Deferrals (by design — to the flip / prose-rewrite slice, NOT this slice)
- `OP_DEFERRED_TO_FLIP` (11) — per-slice active-folder writes; flip-slice R-32.a drain obligation.
- `OP_OUT_OF_SCOPE` (23) — out-of-loop + undecided-disposition + Heavy-mode component/contract writes; owned by the prose-rewrite/flip slice.
- AC3 graphify flip-awareness (dropped, B1) + commit-slice archived reads (dropped, M-add-2) → the 318-prose-rewrite slice.

### Design deviations
- **Op-gate enforcement: suite-test + shippability, NOT a /build-slice Step-6 RULE-ID gate** (m2-verified precedent). The design said "wire into /build-slice Step 6 + /validate-slice"; build-time verification (m2) showed the flip-prep precedent (slice-100 readiness audit, slice-107 prose inventory) wires NONE into Step 6 — they are suite-test + shippability enforced, no RULE-ID. Deviated to the precedent (sound simplification: less surface, convention-aligned). Consequence: OSDG-1 re-sync narrowed to {/reflect}; build-slice/validate-slice NOT edited. design.md / mission-brief / ADR-103 / ADR-104 updated. (updated in design.md? yes)
- **The prose-`architecture/`-literal footgun** (build-time correction, not a deviation) — explanatory routing prose initially re-introduced `architecture/` literals; rephrased (APED-1 catch).

### Files changed
- tools/vault_edit.py, tools/vault_flip_prose_inventory.py (Phase B)
- tests/methodology/test_vault_edit_cli.py, test_vault_flip_op_gate.py (Phase B, new)
- skills/reflect/SKILL.md, skills/archive/SKILL.md, skills/drift-check/SKILL.md, skills/build-slice/SKILL.md (Phase B), skills/validate-slice/SKILL.md (Phase B)
- architecture/shippability.md, architecture/risk-register.md
- architecture/decisions/ADR-103-*.md, ADR-104-*.md
