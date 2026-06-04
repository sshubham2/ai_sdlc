# Slice 110: make-pipeline-vault-location-agnostic

**Mode**: Standard
**Estimated work**: 1 day | split-watch — see Scope note
**Risk retired**: none directly — this is the **flip-readiness prep** that de-risks the R-32-retiring flip (a reversible, green-throughout precondition; the flip + R-32 retirement are a follow-on slice)
**Test-first**: false  (location-agnostic repoint of existing tests + skill prose, not new behavior)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Delivered scope (Phase-1-only ship — user-approved 2026-06-04)

This slice **ships Phase 1 only**: the **location-agnostic test suite** (AC1 + AC5). At `/build-slice` the design's sanctioned Phase 1→2 split point was taken — Phase 1 was a full day's work (85 location breakers repointed across 28 files + a build-discovered ADR-101 mechanism deviation). **AC2 (skill-op routing), AC3 (SKILL.md-prose op-gate), and AC4 (graphify flip-awareness) are DEFERRED to a Phase-2 follow-on slice.** The follow-on inherits [[ADR-102]] (decision ratified here; implementation deferred). The binding AC1 proof is achieved: the full suite is byte-identical under the in-tree default AND a SEEDED external `AI_SDLC_VAULT_ROOT` (flip simulation) — the pipeline's test layer is now flip-neutral, the core de-risking value of the original cut.

## Intent

This slice is the **prep cut** that the slice-110 flip-design review (`superseded-flip-design/`) empirically forced. Both Critics measured that flipping the vault to an external store today makes the suite red (74 methodology + 7 skills failures) AND breaks the pipeline's own in-loop skills (`/reflect`'s archive step is a literal in-tree `mv architecture/...`), so the flip-readiness work **must precede the move**. This slice makes the test suite + the in-loop skills + the readiness audit **vault-location-agnostic** — they resolve the vault via the `VAULT_ROOT` seam regardless of whether it lives in-tree or external — so a future config-only flip is a **suite-neutral no-op**. **No move happens here**; the slice is fully reversible and the suite stays green at every step.

## Acceptance criteria

1. **[✅ DELIVERED]** **The suite is location-agnostic (the binding proof).** The full test suite passes **both** with the in-tree default **and** under an absolute `AI_SDLC_VAULT_ROOT=<seeded-tmp-external-copy>` override — the flip simulation. The breaker count is **~82 full / ~74 methodology**, measured against a **SEEDED byte-faithful copy** (the real-flip-faithful sim — the flip MOVES the vault, it does not empty it; per `/critique-review` B1, an EMPTY external dir spuriously inflates to ~99 by breaking ~17 content-reading audits like `test_live_repo_self_application_clean`, which correctly read real content and need NO fix — do NOT "fix" them to pass against an empty vault). `/build-slice` Phase 1 **re-measures the live SEEDED flip-sim failure set FIRST** (`pytest -q | grep FAILED` with `AI_SDLC_VAULT_ROOT` pointed at a SEEDED copy) and treats THAT enumerated set as the AC1 inventory of record (APED-1 — never a copy-forward count, never the empty-dir number); at slice end the sim produces **zero**. (Tests pin their own vault root; the ~36 deliberate-RETIRE tests use the SAME fix — they fail via fixture-path-resolution drift (worktree path) / forced `vault_is_external` (bare-branch path), both cured by pinning the test's own in-tree vault, not a behavior rewrite — bucket by path at build.)
2. **[⏸️ DEFERRED → Phase-2 follow-on]** **The UNAMBIGUOUS in-loop skill vault ops route through the seam.** The ops whose target is unambiguously the canonical vault (NOT entangled with the worktree-vs-external bootstrap) resolve via `VAULT_ROOT`/`vault_edit`: the **archive `mv`** (`/reflect:320` + `/archive:51` → external `archive/`), `/drift-check`'s **drift-log.md** (a shared vault file), and `/commit-slice`'s **reads of archived/slice folders**. The per-slice **active-folder** writes (`/reflect` reflection.md, `/validate-slice` validation.md, `/slice` scaffold, `/build-slice` `git add`) are **deferred to the flip slice** — they depend on the worktree-vs-external bootstrap the flip slice owns (a per-slice ACTIVE folder may stay worktree-local per BRANCH-3; over-routing now would move slice-authoring artifacts out of the worktree). OSDG-1-guarded edited skills re-synced; unguarded edited skills carry no installed copy (note, no re-sync).
3. **[⏸️ DEFERRED → Phase-2 follow-on]** **The SKILL.md-prose blind spot is closed — by REUSE, gate-visible.** Extend the existing `tools/vault_flip_prose_inventory.py` (slice-107 — it already scans `skills/**/SKILL.md`, region-anchors, and is gate-capable) with an **operational-op gate mode** (or share its anchoring helper), NOT a third parallel classifier in the readiness audit (`/critique-review` M-add-1, CSP-1). It flags un-routed in-loop-skill vault **write-OPS** (`mv`/`cp`/`git add`/`Write`-target) inside anchored regions; the 244 bare prose mentions across 24 SKILL.md files are NOT flagged — proven non-over-flagging against the real corpus (APED-1) + a code-Critic pass (AP-4). **The deferred per-slice-write prose (AC2) lands in a DISTINCT gate-visible `DEFERRED_TO_FLIP` class** (owner = the flip slice, which its pre-finish MUST drive to ∅) — NOT a silent baseline (`/critique-review` M-add-2 / AP-12: never empty a fail-closed bucket via a silent waiver).
4. **[⏸️ DEFERRED → Phase-2 follow-on]** **The in-loop `graphify vault` target is flip-aware.** The `$PY -m graphify vault architecture` invocation in the in-loop `/design-slice:62` resolves the vault root via the seam (or is documented + logged flip-aware). The 5 NON-in-loop sites (`/adopt`, `/discover`, `/heavy-architect`, `/query-design`, `/sync`) are deferred to the 318-prose-rewrite slice (out of this prep's in-loop scope — enumerated, not silently dropped).
5. **[✅ DELIVERED]** **Reversible + green-throughout.** No physical move, no `git rm --cached`, no config write, no `_vault_paths` behavior change. The slice is revertible by a plain `git revert`, and the suite is green with the default at every commit (the flip-sim is the only place an external root is exercised).

> **Scope note** (settled at `/design-slice` + the first `/critique`): ~99 test repoints (Phase 1, pytest-provable) + the UNAMBIGUOUS skill-op routing + the SKILL.md-prose audit classifier (Phase 2). Phased with a `/build-slice` split point at the Phase 1→2 boundary; both phases reversible + green-throughout. The freeze-cascade reload mechanism was **executed and confirmed sound** by the first Critic (no unbounded transitive consumers). The bootstrap-entangled per-slice active-folder write routing (`/reflect` reflection.md, `/validate` validation.md, `/slice` scaffold, `/build-slice` git add) is **deferred to the flip slice** (it owns the worktree-vs-external decision) — see AC2.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Suite location-agnostic | `pytest -q` green (default) AND `$env:AI_SDLC_VAULT_ROOT="<SEEDED-tmp-ext>"; pytest -q` green (flip-sim) — red today (~82 full / ~74 methodology against a SEEDED copy; NOT the ~99 empty-dir number), green at slice end |
| 2 | Unambiguous skill ops seam-routed | the archive `mv` (`/reflect:320`,`/archive:51`) + drift-log.md (`/drift-check:109`) + commit-slice archived reads resolve via the seam; OSDG-1 drift tests green for the re-synced guarded skills (`/reflect`,`/commit-slice`) |
| 3 | Audit blind spot closed | `$PY -m tools.vault_flip_readiness_audit` runs the SKILL.md-prose classifier; a synthetic un-routed `Write architecture/...` fixture-skill is flagged (non-vacuity) AND the 244 real bare-prose mentions are NOT flagged (non-over-flag); gate clean |
| 4 | graphify flip-aware | the in-loop `/design-slice:62` `graphify vault` target resolves via the seam / is logged flip-aware |
| 5 | Reversible + green | `git revert` of the slice restores prior state; suite green with the default at every commit; PowerShell `(git ls-files architecture | Measure-Object -Line).Lines` unchanged before/after (nothing untracked/moved) |

## Must-not-defer

- [ ] **Flip-sim is the binding AC1 gate** — a partial "green by skipping the RETIRE tests" is not acceptable; AC1 requires the WHOLE suite green under the override (the RETIRE tests handled, not excluded).
- [ ] **OSDG-1 re-sync** for the genuinely-guarded edited skills ONLY — verified against `tests/methodology/*skill_drift.py` (2026-06-04): **guarded** = `/reflect`, `/commit-slice` (also `/slice`, `/build-slice`, but those are NOT edited in the narrowed AC2). **NOT guarded** (edited but no installed copy / drift test — no re-sync; do NOT chase a phantom guard) = `/archive`, `/drift-check`, `/validate-slice`. A guarded SKILL.md edit without re-sync is a drift-test failure; a phantom-guard citation is a doc defect.
- [ ] **Readiness-audit non-vacuity** — prove the new SKILL.md-prose scan actually catches an un-routed write (mutation/synthetic-fixture), not just passes on already-clean prose (AP-5).
- [ ] **No behavior change to `_vault_paths`** — this slice does NOT touch the seam's resolution logic; it only makes consumers resolve correctly through it.
- [ ] **Don't silently exclude tests** — if a test cannot be made location-agnostic in this slice, it is enumerated + dispositioned (deferred-to-flip with rationale), never quietly skipped.

## Out of scope (→ the follow-on flip slice)

- **The physical flip** — seed the external store, write `.git/aisdlc/vault-root`, `git rm --cached -r architecture`, `.gitignore`, remove in-tree copies. (B1's move; R-32 retires there.) Draft design preserved in `superseded-flip-design/`.
- **The resolver RETIRE signal** (B2) — `parallel_conflict_resolver` `action="RETIRE"`+exit-0 + the `/commit-slice` branch + the full-CLI AC3 test + corrected ADR-100. Belongs where the RETIRE goes live.
- **The rollback runbook** (M1), **AC2 green-suite-under-flip reframe** (M2), **R-32 retire + anti-revert pin**, **stale "slice-094 flip" comment fixes** (m1), **wiring row** (m2).
- **The bootstrap-entangled per-slice active-folder write routing** (`/reflect` reflection.md, `/validate-slice` validation.md, `/slice` scaffold, `/build-slice` `git add`) — deferred to the flip slice, which owns the worktree-vs-external bootstrap decision (per `/critique` M2). Enumerated, not silently dropped.
- **The 5 non-in-loop `graphify vault architecture` sites** (`/adopt`, `/discover`, `/heavy-architect`, `/query-design`, `/sync`) — deferred to the 318-prose-rewrite slice.
- **The 318-site prose rewrite** (skills/agents/CLAUDE.md/README/INSTALL) — still a separate later slice.

## Dependencies

- This slice's own review history: `superseded-flip-design/` (the BLOCKED flip critique + EXTEND meta-review + ADR-099/100 drafts that motivated this re-scope)
- Prior slices: [[slice-098-route-or-retire-git-coupled-vault-tools]] (`vault_is_external` — the signal the RETIRE tests key on), [[slice-100-add-vault-flip-readiness-audit]] (the audit extended at AC3), [[slice-102-vault-flip-readiness-tests]] (the test-update inventory)
- Vault refs: [[decisions/ADR-065]] / [[decisions/ADR-085]] (the `VAULT_ROOT` seam consumers must route through), [[decisions/ADR-089]] (the RETIRE-when-external behavior the RETIRE tests assert)
- Tools: `tools/_vault_paths.py` (the seam — consumed, NOT changed), `tools/_vault_git.py` (`vault_is_external`), `tools/vault_edit.py` (the routed write/append/rewrite channel), `tools/vault_flip_readiness_audit.py` (extended at AC3)

## Mid-slice smoke gate

At ~50% — after the test repoints (AC1) but before/while the skill prose (AC2):
```
$PY -m pytest -q                                          # default — green
$env:AI_SDLC_VAULT_ROOT="<seeded-tmp-ext>"; $PY -m pytest -q; Remove-Item Env:AI_SDLC_VAULT_ROOT   # flip-sim — failures strictly DECREASING toward 0
```
Expected: default stays green; flip-sim failure count falling toward 0. If the default suite goes red at any point → STOP (a location-agnostic repoint must never break the in-tree path).

## Pre-finish gate (Phase-1-only ship)

- [x] AC1 flip-sim: `AI_SDLC_VAULT_ROOT=<SEEDED-ext> pytest` green AND default `pytest` green — **PROVEN**: both modes = 1574 passed, byte-identical results (the sole red is the pre-existing psq_1 queue-staleness, now resolved by syncing the worktree queue from master → suite fully green)
- [x] AC5 reversible (`git revert`); nothing moved/untracked; `_vault_paths` resolution unchanged (no production code touched — tests + test-support helpers only)
- [ ] /drift-check passes (full mode); no new TODOs/FIXMEs/debug prints
- [ ] All Step-6 audits pass (BC-1, WIRE-1, BRANCH, CRP-1, PCA-1, BCI-1, MCFS-1, STP-1, AVFS-1, TVFS-1, NAW-1, DCE-1, SVW-1, UTF8-STDOUT-1, mock-budget)
- **[⏸️ DEFERRED → Phase-2 follow-on]** AC2 (UNAMBIGUOUS skill-op seam-routing + OSDG-1 re-sync + cross-store-`mv` coherence), AC3 (op-gate via `vault_flip_prose_inventory` reuse + non-vacuity/non-over-flag + code-Critic + shippability rows 108/109), AC4 (graphify flip-awareness). See **Delivered scope** banner + [[ADR-102]] implementation-status note.
