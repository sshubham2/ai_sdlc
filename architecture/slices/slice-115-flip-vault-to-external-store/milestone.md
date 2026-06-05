---
slice: slice-115-flip-vault-to-external-store
stage: build
updated: 2026-06-05
next-action: Phase A1 — tools/_vault_flip.py + test
risk-tier: high
critic-required: true
---

# Milestone: slice-115 flip-vault-to-external-store

**Stage**: build
**Next action**: Phase A1 — `tools/_vault_flip.py` + test (plan approved; VERSION bump in scope)
**Updated**: 2026-06-05
**Risk tier**: high — Critic required: yes (capstone flip; full 3-Critic stack ran)

## Progress

- [x] /slice — 2026-06-05
- [x] /design-slice — 2026-06-05
- [x] /critique — 2026-06-05 — NEEDS-FIXES (first Critic BLOCKED; 3B/5M/2m)
- [x] /critique-review — 2026-06-05 — EXTEND (meta-Critic: 3 missed + 1 severity-adj; 0 suspicious)
- [ ] /build-slice — in progress: A1 ✓ A2 ✓ | next A3 (wire gate) → A4 (prose ~12 files) → A5 (commit-slice) → smoke → B flip → C finalize+VERSION
- [ ] /validate-slice
- [ ] /reflect

## Current focus

Dual-Critic complete; TRI-1 ratified → **NEEDS-FIXES**. Design.md / ADR-107 / mission-brief carry all ACCEPTED-FIXED edits (B1–B3, M1–M5, m1–m2, M-add-1/2, m-add-3, M3-adj). ACCEPTED-PENDING items implemented during `/build-slice`:
- B1: `_vault_flip` migrate = rebase-then-full-branch-tree (carries ADR-107 + risk-register edit).
- B2 + M-add-1: op-gate reclassify active-folder → OUT_OF_SCOPE (sink-keyed), re-pin BOTH floors (DEFERRED 11→0, OUT_OF_SCOPE 23→~34), wire `--op-gate --strict` into build/validate + shippability, non-vacuity proofs.
- B3 + M-add-2: full-manifest LF-normalized verify; LF-normalize text on migrate; re-home ADR-098 byte-identity precondition.
- M3 + M3-adj: pre-flip quiesce guard via `stranded_slice_audit` (catches BRANCHLESS_IN_FLIGHT data-loss).
- M5: 5-site Step-6.5 retire + `git add` removal. m1: render slice:264 cleanly.

## On resume

- **Last completed action**: Phase A2 (op-gate drain) — committed `e5e876d`. A1 (_vault_flip) committed earlier. Both trees clean; targeted suites green (7 + 71).
- **Current work**: none in flight — clean checkpoint after A2.
- **Next immediate step**: **A3** — wire `--op-gate --strict` into `/build-slice` Step 6 + `/validate-slice` pre-finish + a `shippability.md` row (AP-18). Then **A4** (the big one) — convert carve-out prose classes 4–6 `architecture/…` → `<vault>/…` across ~12 skill SKILL.md + agent code-review.md, the 5-site `/slice` Step-6.5 queue-commit-on-master removal (M5), render `slice:264` cleanly (m1) + drop its now-dead allowlist entry, and re-pin the inventory `_BASELINE_SHA256`/converted-file ratchet. Then A5 (commit-slice RETIRE verify+prose) → mid-slice smoke (full pytest) → **Phase B the physical flip** → Phase C (R-32 retire + full audit suite + VERSION bump + forward-sync cascade + pip install --upgrade).
- **Resume note**: the physical flip has NOT happened yet (vault still in-tree; `vault_is_external` = False; default resolution → `architecture/`). The suite stays location-agnostic-green through all of Phase A; the flip is the LAST build step (Phase B). Everything committed on `slice/115`; master holds only the queue-pick commit + is clean.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-107](../../decisions/ADR-107-flip-vault-to-external-store.md)
- [critique.md](critique.md) — NEEDS-FIXES (triage ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
