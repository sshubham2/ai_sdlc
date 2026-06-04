# Critique Review: Slice 111 route-in-loop-skill-vault-ops-via-seam

**Reviewed by**: critique-review agent (DR-1, meta-Critic)
**Date**: 2026-06-04
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's eight findings are largely sound and the Builder's fixes are mostly correct on their own terms — but BOTH passes missed the dominant structural risk: the AC2 op-gate's scan scope (`skills/**/SKILL.md` = ALL skills) is wider than its classification taxonomy can safely handle (which only knows "routed / active-folder-deferred / unrouted"), so on the real corpus the gate will flag legitimate out-of-loop and not-in-AC1-scope shared-aggregate writes as `OP_UNROUTED` and cannot go green — directly breaking AC3 "green at every commit." This is a Blocker-class gap (M-add-1) that subsumes and re-frames the B2 fix.

## Confirmed findings (VALID, correct severity)

- **B1** (AC3 `graphify vault` target does not exist) — confirmed; Blocker appropriate. Zero in-loop `graphify vault` executors (`/reflect:298` rebuilds the CODE graph); the extra sites `/query-design:59` + `/archive:216` are out-of-loop/descriptive. Dropping AC3 + `vault_edit root` is correct. (Caveat → m-add-3.)
- **B2** (`OP_DEFERRED_TO_FLIP` source-literal escape) — confirmed; Blocker appropriate. Line-anchoring verified (`vault_flip_prose_inventory.py:211`). Keying on destination is the right direction. (Incomplete for `git add` multi-path → M-add-1.)
- **M2** (`vault_edit move` dest-guard vs `shutil.move`) — confirmed; Major appropriate. `_resolve_in_vault` (`vault_edit.py:53-77`) handles `--to` resolution; final-landing-path guard is the correct semantic.
- **M3** (`OP_DEFERRED_TO_FLIP` needs a contractual consumer) — confirmed; Major appropriate. R-32.a/R-32.b (risk-register.md) are genuinely contractual — satisfies AP-12. Fix sound.
- **m1** (AP-16 detection⊇classification), **m3** (RESOLVED-BY-B1) — confirmed, correct severity/disposition.

## Suspicious findings

- **M1 — SUSPICIOUS on quantification, not existence.** The re-pin plan is correct, but `318−K` is NOT deterministic from the design because the `/commit-slice` "operational archived reads" routing is under-specified (→ M-add-2). The deferred-to-build measurement is APED-1-honest, so not a false positive — but the re-pin is *coupled to* the commit-slice routing decision, not independent. Severity stays Major.

## Missed findings

- **M-add-1 (Blocker): op-gate scan scope (ALL skills) exceeds its taxonomy (in-loop routing only) → the gate cannot go green on the real corpus.** `_iter_scan_files` (`vault_flip_prose_inventory.py:257-262`) scans all skills with NO in-loop filter. Out-of-loop / not-in-AC1-scope shared-aggregate write-ops with no seam token → rule 3 → `OP_UNROUTED` → exit 2: e.g. `critic-calibrate:128` ("Append to `architecture/critic-calibration-log.md`"), `triage:140/163/179`, `sync:179`, `risk-spike:111`, `user-test:78`, `adopt:231/273`, `supersede-slice:67`, and the `git add architecture/...` multi-path forms at `build-slice:88`. Contradicts ADR-104:46 ("0 `OP_UNROUTED` post-routing") + AC3. Fix: either (a) restrict the op-gate scan to a pinned in-loop skill set, or (b) add a fourth gate-visible class for out-of-scope shared-aggregate writes with its own count-floor + owner. Both Critics missed it (neither executed the detection vocabulary against the real corpus). Must resolve before/at build, not defer.
- **M-add-2 (Major): `/commit-slice` "resolve via the seam" is hand-waving across 4 structurally different shapes (untestable requirement).** `commit-slice:14` (descriptive prose), `:45` (prereq existence assertion), `:55` (already bare `slices/archive/`), `:70` (an actual `grep -l ... architecture/decisions/` command). The contract must specify, per shape, whether it is rewritten and to what — this determines K for the M1 re-pin (M1+M-add-2 coupled). Blocks a deterministic M1 + leaves AC1's commit-slice clause unverifiable.
- **m-add-3 (Minor): B1's `_RESIDUAL` is incomplete — `query-design:59` (`graphify vault architecture`, bare) is a genuine residual absent from `_RESIDUAL` (`vault_flip_prose_inventory.py:299-305`).** Since the prose-rewrite slice owns graphify-vault flip-awareness off this list, the missing entry is a silent hand-off gap. slice-107 artifact; query-design out-of-loop → Minor. Fix: add `query-design:59` (+ confirm `archive:216`) to `_RESIDUAL` or scope the gap in the hand-off note.
- **m-add-4 (Minor): ADR-104 still lists `/design-slice` in the OSDG-1 re-sync set in one line — self-contradiction with the same ADR's B1 refinement.** "Drift from vault" should have caught it. Fix: drop `/design-slice` from that line.

## Severity adjustments

- **m-add-5 (re-classify to missed Major): the "no installed copy" rationale for not re-syncing `/archive`+`/drift-check` is FACTUALLY FALSE.** Both have installed copies (`~/.claude/skills/{archive,drift-check}/SKILL.md`). The CONCLUSION (no OSDG-1 *re-sync obligation*) is correct — OSDG-1 only guards skills with a `*_skill_drift.py` content-equality test, which these lack — but the stated REASON is wrong and masks a real defect: if the Builder edits in-repo `/archive`+`/drift-check` for routing but leaves the installed copies un-routed (relying on the false "no installed copy" premise), then at a user's machine Claude reads the INSTALLED copy (still carrying un-routed `mv architecture/...` that breaks at flip) while the op-gate (scanning in-repo only) reports clean. Fix: correct the rationale to "unguarded (no drift test)" AND decide explicitly whether the installed copies of `/archive`+`/drift-check` must be hand-synced for the routing to take effect in fielded loops.

## Notes

Confidence: high on M-add-1 (executed the detection vocabulary against the real corpus; the `critic-calibrate:128` / `triage` / `build-slice:88` un-routed shared-aggregate writes are on disk with no seam token) and m-add-5 (installed copies verified on disk, contradicting three artifacts). Medium on M-add-2 (the commit-slice routing is genuinely ambiguous; the Builder may intend to leave prose-mentions untouched, shrinking K — pin it, don't assume). Calibration observation on the first Critic this slice: strong line-level verification on the four explicit op sites (B1/B2/M1/M2 all carry accurate file:line evidence) but **scope blindness** — it validated the gate's classifier logic without asking whether the gate's scan DOMAIN matches its purpose, and accepted the design's "no installed copy" / "`_RESIDUAL` complete" premises without disk verification. The B2 dual-literal fix is necessary but, alone, gives false comfort. Recommend routing M-add-1 to TRI-1 as a Blocker.
