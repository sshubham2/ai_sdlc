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

- **Last completed action**: Phase A3 (op-gate promoted to a /build-slice Step-6 gate) — committed. A1+A2 committed earlier. Both trees clean; op-gate `--strict` exit 0; targeted suites green (7 + 71).
- **Current work**: A4 in progress — scoped precisely (see below).
- **A4 PRECISE SCOPE (inventory APED-1)**: 127 rewrite-at-flip refs across 22 files split by `reason`: **CONVERT → `<vault>/` = 65** (reason `operational-reference` + value `architecture/…`); **KEEP concrete = 62** (37 `git-pathspec` + 25 `diagnose-out`, classes 1/7 per ADR-105). The 65 convert set spans the loop/process skills + agents (code-review.md:29/:237, critique-review.md:78, critique.md:129/:264 — the flip drains the slice-114-deferred agent carve-outs). **Special handling**: (a) `slice/SKILL.md` 4× `architecture/slice-queue.md` at L250/430/475/515 = the **M5** Step-6.5 commit-on-master REMOVAL (remove the `git add`+commit lines; the CAS queue WRITE stays) — NOT a plain path convert; (b) `slice:264` `architecture/slices/�` mojibake = the **m1** clean render + drop the now-dead `_OP_ALLOWLIST` slice:264 entry; (c) prefix-overlap among 33 distinct values → convert longest-first / value-exact. Then re-pin inventory `_CONVERTED_FILES`/`_CONVERTED_CARVEOUTS`/`_BASELINE_SHA256`/`EXPECTED_TOTAL`/`_CLASS_COUNT_FLOOR[rewrite-at-flip]` + verify `--strict` green + forward-sync edited skills/agents (OSDG-1/CAD-1).
- **Then**: A5 (commit-slice RETIRE verify+prose — guard exists from slice-098) → mid-slice smoke (full pytest, AFTER forward-sync) → **Phase B the physical flip** (quiesce via stranded_slice_audit → `_vault_flip.flip` → full-manifest verify → `git rm -r --cached architecture/` + gitignore + drop slice-queue `.gitattributes` pin → orphan removal) → Phase C (R-32 retire + full audit suite + shippability row 121 + 117/119 count notes + VERSION bump + forward-sync cascade + pip install --upgrade).
- **Resume note**: the physical flip has NOT happened yet (vault in-tree; `vault_is_external`=False). Suite stays location-agnostic-green through Phase A; flip is the LAST build step. Everything committed on `slice/115`; master = queue-pick commit only, clean.

## Phase artifacts

- [mission-brief.md](mission-brief.md)
- [design.md](design.md)
- [ADR-107](../../decisions/ADR-107-flip-vault-to-external-store.md)
- [critique.md](critique.md) — NEEDS-FIXES (triage ratified)
- [critique-review.md](critique-review.md) — EXTEND
- [build-log.md](build-log.md) — pending
- [validation.md](validation.md) — pending
- [reflection.md](reflection.md) — pending
