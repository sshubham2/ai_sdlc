# Reflection: Slice 111 route-in-loop-skill-vault-ops-via-seam

**Date**: 2026-06-04
**Shipped**: YES

The Phase-2 follow-on to slice-110: routed the remaining UNAMBIGUOUS in-loop skill vault WRITE-ops via the `vault_edit` seam (AC1) + shipped the in-loop-scoped op-gate that verifies the routing (AC2, implements ADR-102). No physical move — R-32 stays `mitigating`, retires at the follow-on flip slice. MEPD-1 EXCLUDE (no RULE-ID / changelog / VERSION bump).

## Validated
- **Seam-routing works end-to-end** — `/drift-check`'s drift-log write was dogfooded for real at the pre-finish gate via `vault_edit append`, and DCE-1 found the `**Trigger**: slice-111` marker in the real `architecture/drift-log.md`. `vault_edit move` validated by 23 CLI tests + the `/reflect`/`/archive` archive-`mv` routing.
- **The op-gate goes green on the real corpus** — in-loop-scoped (`_IN_LOOP_SKILLS`=11) + destination-keyed + 4-class: 6 routed / 11 deferred / 23 out-of-scope / 0 OP_UNROUTED. Genuinely non-vacuous (it bites a fresh in-loop un-routed write).
- **M1 re-pin byte-correct** — 318→313 (K=5 routed-away); baseline SHA + count-floor + EXPECTED_TOTAL all consistent (code-Critic verified by live recompute).
- **AC5 disjointness preserved** — hash-keyed `_OP_ALLOWLIST` keeps `tools/*.py` free of `architecture/` literals (readiness_audit clean).

## Corrected
- **"wire the op-gate into `/build-slice` Step 6 + `/validate-slice`"** (design) → reality: the flip-prep precedent (slice-100 readiness audit, slice-107 prose inventory) wires NONE into Step 6 — they are **suite-test + shippability enforced, no RULE-ID** (verified at build via m2). Deviated to the precedent: enforcement via `test_vault_flip_op_gate.py::test_real_corpus_op_gate_green` + shippability #117. Consequence: OSDG-1 re-sync narrowed `{/reflect, /build-slice}` → `{/reflect}`; build-slice/validate-slice NOT edited. Updated in design.md / mission-brief / ADR-103 / ADR-104.
- **"`/archive`+`/drift-check` have no installed copy"** (mission-brief/design/ADR-103) → reality: both DO have `~/.claude/skills/` copies (m-add-5); the conclusion (no OSDG-1 *obligation*) held, but the rationale was false → corrected to "no `*_skill_drift.py`" + the installed copies hand-synced.
- **AC3 (in-loop `graphify vault` flip-awareness)** → reality: there is NO in-loop `graphify vault` executor (`/reflect:298` rebuilds the CODE graph; `/design-slice:62` is prose) (B1) → AC3 + the `vault_edit root` subcommand dropped; folded into the prose-rewrite slice.
- **AC1 included `/commit-slice` archived reads** → narrowed (M-add-2): 4 ambiguous prose/grep shapes, reads fail loud not silent → deferred to the prose-rewrite slice (made the M1 K deterministic).

## Discovered
- **Lexical markdown op-detection is inherently imprecise** — bare `add` matches slice-names (`...add-receipt...`) + prose (`Add --flag`); `move`/`edit` appear as nouns; decoy seam tokens; verb-after-literal prose. The sound pattern is: tight detector (`git add` bigram, verb-before-literal, in-code anchoring, seam-AFTER-verb) + an explicit hash-keyed allowlist for the residual + adversarial tests. Surfaced ONLY at build-time corpus execution (APED-1), not design reasoning.
- **The op-gate introduces 3 new counted-set pins** (`_IN_LOOP_SKILLS`=11, `_OP_CLASS_FLOOR` deferred=11/out-of-scope=23) — a future slice editing in-loop skill prose that shifts op-counts will re-surface as OP_UNROUTED or a floor-shrink and need a deliberate re-pin (STP-1/FBCD-1 maintenance surface). Known cost, not a standing product risk → captured as a lesson, not a risk-register entry (mirrors slice-110's reload-gotcha decision).
- **The flip-prep enforcement precedent** (m2): flip-prep audits are suite-test + shippability enforced, NOT build-slice Step-6 RULE-ID gates — a reusable clarification for future flip-prep slices.

## Deferred (to the flip / prose-rewrite slice)
- **`OP_DEFERRED_TO_FLIP` (11)** — per-slice active-folder writes; the flip slice's pre-finish MUST drain to ∅ (risk-register **R-32.a**).
- **Cross-store archive-`mv` coherence** — if the flip keeps active folders worktree-local, `vault_edit move --from slices/slice-NNN` fails loud; flip slice resolves (risk-register **R-32.b**).
- **`OP_OUT_OF_SCOPE` (23)** — out-of-loop + Heavy-mode component/contract + undecided-disposition (`slice-queue.md` ledger) writes → owned by the prose-rewrite/flip slice.
- **AC3 graphify flip-awareness** (dropped B1) + **`/commit-slice` archived reads** (dropped M-add-2) → the 318-prose-rewrite slice.
- **m1 bare-sink-literal hole** + **m4 allowlist-edit-brittleness** — accepted for v1 (documented); a future detector refinement (verb-in-code) could shrink the allowlist.

## Critic calibration

Per TRI-1, scored against the `## Triage` dispositions + reality at build/validate. **The full 3-Critic stack (design + meta + code) was load-bearing this slice — each layer caught defect classes the others structurally could not (AP-19, N+1).**

**Design-Critic (`critique.md`)** — all VALIDATED:
- B1 (AC3 target non-existent): VALIDATED — ACCEPTED-FIXED; no in-loop `graphify vault` executor, confirmed by grep.
- B2 (`OP_DEFERRED` source-literal escape): VALIDATED — ACCEPTED-FIXED; destination-keying was exactly right (the code-Critic's M2 later found a sibling residual in the same dest-detection — the fix-delta recursion, AP-2).
- M1 (318 re-pin), M2 (move dest-guard / shutil.move semantics), M3 (`OP_DEFERRED` consumer): VALIDATED — all materialized as flagged.
- m1 (AP-16 detection⊇classification): VALIDATED — the bare-`add` over-fire was real (caught at build APED-1).
- m2 (MEPD-1 precedent verify): VALIDATED — the verification CHANGED the design (flip-prep audits aren't Step-6-wired) — a high-value "verify, don't assert" finding.
- m3 (root newline): RESOLVED-BY-B1 (moot).

**Meta-Critic (`critique-review.md`, EXTEND)** — all VALIDATED; caught what the design-Critic missed:
- **M-add-1 (op-gate scan scope can't go green)**: VALIDATED — THE load-bearing miss. The first run had out-of-loop OP_UNROUTED; the `_IN_LOOP_SKILLS` + `OP_OUT_OF_SCOPE` fix (the meta-Critic's design) was exactly what made the gate green. The design-Critic validated the classifier LOGIC (B2) without checking the scan DOMAIN — the meta-Critic's complementary lens.
- M-add-2 (commit-slice hand-waving), m-add-3 (`_RESIDUAL` incomplete), m-add-4 (ADR-104 stale line), m-add-5 (false "no installed copy"): all VALIDATED + fixed.

**Code-Critic (`code-review.md`, FINDINGS)** — all VALIDATED; caught implementation defects the design+meta stack structurally cannot reach (the AP-4 class):
- M1 (seam-token line-wide masking — the AP-15 decoy hole ADR-104 itself warns against): VALIDATED — fixed (seam-AFTER-verb).
- M2 (`is_move` single-dest collapse on mixed verbs): VALIDATED — fixed (single-clean-move).
- m1-m5: all VALIDATED + fixed/documented.

**Missed by Critic**: NO Critic (design or meta) predicted the three build-time APED-1 footguns — (a) explanatory prose re-introducing `architecture/` literals, (b) bare-`add` over-firing on slice-names, (c) the `_OP_ALLOWLIST` inlining literals → AC5-disjointness regression. All surfaced ONLY at EXECUTION against the real corpus (AP-3). The code-Critic then caught two MORE latent false-negative paths (M1/M2) by executing adversarial fixtures.

**Pattern**: for a dominant-risk lexical/AST classifier, design-time reasoning — even DUAL-Critic-ratified — cannot enumerate the false-positive/false-negative surface. The discipline that worked: APED-1 corpus execution (build) + the code-Critic's adversarial-fixture execution (post-build), each finding distinct classes. BC-PROJ-17 (classifier-execute-against-corpus) confirmed N+1; the 3-Critic stack's complementarity (AP-19) confirmed N+1. **Calibration heuristic**: when a slice adds a lexical classifier with a "routed/exempt vs flag" decision, the design-Critic should explicitly probe the *masking* axis (can a decoy/adjacent token suppress a real flag?) — the M1 decoy-seam hole is a recurring shape (slice-098 AP-15, slice-099/100 AP-1, now slice-111 M1).

## Lessons for next slice
- The op-gate's count pins (`_IN_LOOP_SKILLS`=11, deferred=11, out-of-scope=23) are STP-1/FBCD-1 surfaces — a slice editing in-loop skill prose should re-run `--op-gate` + re-pin deliberately if counts shift.
- The flip slice owns: drain `OP_DEFERRED_TO_FLIP` (R-32.a), resolve cross-store `mv` (R-32.b), the physical move + git-untrack + `/commit-slice` RETIRE no-op + R-32 retirement.
- The prose-rewrite slice owns: the 23 `OP_OUT_OF_SCOPE` writes + AC3 graphify (the 6 `_RESIDUAL` sites) + commit-slice reads + the 313 location-literals.
- For a lexical classifier, write the adversarial decoy/masking + multi-verb + verb-as-noun fixtures FIRST (the code-Critic's M1/M2 should have been design-time tests).

## Vault updates made (thin vault)
- [[risk-register.md]] — R-32.a (drain `OP_DEFERRED_TO_FLIP`) + R-32.b (cross-store `mv`) sub-entries (added at /critique; R-32 stays `mitigating`).
- [[lessons-learned.md]] — slice-111 entry (this reflection's Worked/Didn't/Pattern).
- [[shippability.md]] — row #117 (vault_edit move + op-gate critical path).
- [[decisions/ADR-103]] (vault_edit `move` seam-CLI) + [[decisions/ADR-104]] (structural in-loop-scoped op-gate, implements ADR-102) — authored this slice.
- This slice's [[design.md]] — the suite-test-enforcement deviation (m2) + the B1/B2/M1/M2/M-add-1/m-add-5 refinements (build-log records them).
- No ADR superseded; no risk-register status flip (R-32 retires at the flip, not here); no concept change; no VERSION/changelog bump (MEPD-1 EXCLUDE).
