# Reflection: Slice 106 route-project-frame-synth-via-vault-root

**Date**: 2026-06-03
**Shipped**: YES

## Validated

- **The `repo_root / VAULT_ROOT / "X"` routing is a pure no-op today AND flip-correct** — validated by AC3 byte-identical frame output (SHA `97340A02` pre == post == validate), the code-Critic's execution trace of pathlib's absolute-operand-discard semantics (`Path('/repo') / Path('/abs') / 'x'` == `/abs/x` — the intended relocation when `VAULT_ROOT` goes absolute at flip), and 44 guard tests green. The seam consumption matches every sibling consumer's idiom.
- **The existing slice-068 migration machinery extends to cover `project_frame_synth` once it joins `_MIGRATION_SITE_ALLOWLIST`** — validated: `test_migration_site_allowlist_pinned` (16 == actual VAULT_ROOT importers) + `test_no_orphan_architecture_literal_in_migrated_tools` both green; the M1 reconciliation ("no new test file, no new row — existing guards cover it") held under build + full-suite.
- **B1's synthetic-fixture relocation preserves classifier non-vacuity** — validated: dropping the real-repo `assert MUST_REWRITE in classes` lost no coverage; `test_new_unrouted_literal_fails_gate` + `test_every_hit_has_exactly_one_class` independently prove (synthetically) the classifier still emits `MUST_REWRITE`. The meta-Critic + code-Critic both confirmed this by execution.
- **Production vault-flip readiness surface 4 → 0 must-rewrite** — validated: `vault_flip_readiness_audit` `[production] 0 must-rewrite` + `--strict` exit 0; shippability catalog 111/111.

## Corrected

- **None.** The slice built exactly per the (Critic-fixed) design; no design.md claim was refuted by reality. The `/critique` NEEDS-FIXES edits were applied to design + mission-brief BEFORE build, so the design that entered build was already correct — there was nothing left to correct at reflect.

## Discovered

- **A 2nd, independent VAULT_ROOT-importer count-pin the full 3-Critic stack missed.** `test_external_vault_adr_and_risk.py::test_no_new_tool_migration_and_classification_map_documented` hard-pins `len(importers) == 15`; adding `project_frame_synth` made it 16. The design-Critic, meta-Critic, AND code-Critic all reviewed the allowlist + readiness consumers — the meta-Critic *specifically* grepped `tests/` for readers of `MUST_REWRITE`/`_BASELINE`/`project_frame_synth` — but NONE enumerated this count-pin, because its miss axis is **"hard-count pins on the cardinality of a counted set,"** distinct from the "readers of the changed symbol" axis that was searched. Caught only by the full suite (BC-PROJ-4). Fixed in-slice (→16 + a `project_frame_synth` membership assert + corrected a pre-existing stale "to 14" docstring). This is **AP-10 ("the count-literal fan-out is wider than any checklist") recurring even under a 3-Critic stack** — N keeps growing.
- **Pre-existing prose drift compounds silently.** The `_MIGRATION_SITE_ALLOWLIST` comment said "14-element" while the live set was already 15 (slice-103 added `index_router_thinness_audit.py` without bumping the prose). slice-106's correction went 14 → 16, skipping 15. Lesson: a slice that changes a counted set's cardinality should grep ALL count narratives for that set, not just the one line it's directly editing.

## Deferred

- **None.** The slice closed its full scope (production surface 4 → 0). The external-shared-vault flip's remaining cuts — M1 prose-inventory (slice-107, queued + parallel), M2 prose+tests routing, M3 the untrack decision, M4 atomic flip-execute — are the separate in-flight initiative, not deferred *by* this slice.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed in build/validate. Three-Critic stack: design-Critic (`/critique`) + meta-Critic (`/critique-review`) + code-Critic (`/code-review`).

- **B1** (routing must-rewrite→0 reds `test_emits_classified_inventory_with_evidence`): **VALIDATED — materialized exactly.** Disposition ACCEPTED-PENDING. The breaker fired live: after task-1 routing the test went red; the synthetic-fixture rework greened it. The design-Critic caught it *by executing `audit_root`* (not design-prose reasoning); the meta-Critic independently reproduced it. A genuine build-breaker that the design's first-pass enumeration missed but the Critic stack caught.
- **M1** (AC4/AC5 ambiguity — new-test/row vs existing-machinery): **VALIDATED.** Disposition ACCEPTED-FIXED. The reconciliation (no new test file, no new row — existing slice-068 guards cover it) held: build added no new test function, the full suite + shippability stayed green.
- **M2** (stale "4 sites" narrative in 4 spots): **VALIDATED.** Disposition ACCEPTED-PENDING. All 4 sites were genuinely stale post-routing and were repointed; no test pinned the prose (grep-confirmed at build).
- **m1** (FBCD-1 two-numbers trap — allowlist membership 16 vs `test_count == 15`): **VALIDATED — and load-bearing.** Disposition ACCEPTED-FIXED. The `== 15` pin was correctly left untouched; the full suite confirms no test function was added. Without this finding the Builder could plausibly have reflexively bumped `== 15` and red'd the suite.
- **m2** (MEPD-1 EXCLUDE no-ADR justification): **VALIDATED.** Disposition ACCEPTED-FIXED. No ADR was correct; the routing minted no rule.
- **code-Critic m1** (orphan-guard fragility — 2 surviving prose literals evade the regex by quote-prefix coincidence): **VALIDATED (advisory).** A real future-fragility note, correctly backstopped by the readiness audit's `doc-example-safe` classification. No action taken (advisory + backstopped); recorded.
- **code-Critic m2** (inline idiom vs module constant): **FALSE-ALARM (self-resolved).** The code-Critic pressure-tested it against the slice's own cited counter-example (`_INDEX_MD_REL`) and resolved it as conformant, not a defect. Honest non-finding — logged for completeness, not over-stated.

**Missed by Critic** (the headline): the **2nd VAULT_ROOT-importer count-pin** in `test_external_vault_adr_and_risk.py` — missed by ALL THREE Critic passes, caught by the full suite. The miss is not a stack weakness on *semantic correctness* (flip-correctness, coverage-relocation, AC reconciliation were all verified by execution) but a recurring blind spot on **count-literal fan-out**: when a slice changes a counted set's cardinality, multiple independent hard-count pins can live across different test files, and the stack enumerates the obvious set-equality pin (the allowlist) while missing sibling `== N` pins elsewhere.

**Pattern**: The 3-Critic stack is excellent at semantic correctness (every load-bearing claim was independently verified by execution — zero FALSE-ALARM on substantive findings, one self-resolved code m2) but has a **structural blind spot on counted-set cardinality fan-out** (AP-10). The actionable `/critic-calibrate` heuristic: *when a slice adds/removes the Nth member of a counted set, grep the WHOLE repo for every `== N` / "N-element" / "set to N" literal on that set — not just the membership-set-equality pin.* This is the 4th consecutive clean-but-for-count-fan-out showing on a cross-cutting tooling slice; combined with slice-105's version-bump-obligations miss and the standing AP-10/AP-21 signals, **`/critic-calibrate` is overdue** and now has a sharp, reproducible miss to encode.

## Lessons for next slice

- **A slice that changes a counted set's cardinality has a fan-out of hard-count pins wider than the obvious membership pin.** Before finishing, grep the whole repo for every `== N`, "N-element", "set to N", "= N consumers" literal referencing that set — across ALL test files, not just the file being edited. (AP-10, N now higher; this slice's `test_external_vault_adr_and_risk.py` miss is the freshest witness.)
- **Stale count-narratives compound across slices.** The "14-element" comment was already wrong (15) before this slice; correcting it required noticing the prior drift. When you touch a count narrative, reconcile it to the *live* value, and check sibling narratives for the same set.
- **The full suite (BC-PROJ-4) remains the irreplaceable backstop for the Critic stack's count-fan-out blind spot.** Even a 3-Critic stack that greps the obvious consumers will miss a sibling count-pin; the full suite caught it. Do not shortcut the full-suite run on "small" routing slices.
- **MEPD-1 EXCLUDE routing slices are genuinely low-risk** — the seam (ADR-065) + the readiness audit (ADR-091) made this a no-behavior-change cut with a deterministic 4→0 success signal. The flip roadmap's remaining production prep is effectively done.

## Vault updates made (thin vault — small list)

- This slice's [[reflection.md]] — written (this file).
- [[lessons-learned.md]] — slice-106 entry appended (via `vault_edit append`).
- [[risk-register.md]] — **no new entry** (the count-fan-out miss is a `/critic-calibrate` signal / AP-10 build-check-candidate, not a new risk — consistent with slice-105's version-bump discovery disposition).
- No ADR edits (MEPD-1 EXCLUDE — slice mints none; ADRs append-only).
- [[shippability.md]] — see the user-decided Step 5.3 disposition below (M1 ratified "no new row"; reconciled against the per-slice convention).
- [[slices/_index.md]] + [[slices/archive/_index.md]] — regenerated at auto-archive (via `vault_edit rewrite` CAS).
