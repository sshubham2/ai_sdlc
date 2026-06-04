# Slice 111: route-in-loop-skill-vault-ops-via-seam

**Mode**: Standard
**Estimated work**: 1 day | split-watch — AC2-gate (the op-gate parser extension) is the dominant risk; `/build-slice` MAY take a Phase split if it overflows (as slice-110 did)
**Risk retired**: none *directly* — this is the **Phase-2 flip-readiness prep** that de-risks the eventual R-32-retiring flip. It does NOT move the vault; [[risk-register#R-32]] retires at the physical flip (the follow-on slice), not here. This slice closes R-32's last *in-loop-skill* prep residual and implements [[decisions/ADR-102]] (ratified at slice-110, implementation deferred to here).
**Test-first**: false  (skill-prose op routing + an audit-tool parser extension; the AC2-gate carries mandatory non-vacuity/non-over-flag tests — see Must-not-defer — but the slice is not a test-first cut)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-110 made the **test suite** vault-location-agnostic (Phase-1 of the external-vault flip prep). This slice is the **named Phase-2 follow-on** (slice-110 reflection L47): it routes the remaining **UNAMBIGUOUS in-loop skill vault ops** through the `VAULT_ROOT` seam (AC1) and closes the **SKILL.md-prose blind spot** with a gate-visible op-gate that *verifies* that routing — by REUSING the slice-107 prose-inventory tool, not a third classifier (AC2, implements [[decisions/ADR-102]]). **No physical move happens here** — this is the last in-loop-skill prep before the flip slice; the slice stays reversible (`git revert`) and the default suite stays green at every commit.

> **Scope correction (`/critique` B1)**: the originally-planned AC3 ("make the in-loop `graphify vault` target flip-aware") was **dropped** — `/design-slice:62` is *prose* ("if the vault graph was built with…"), not an executable invocation, and **no in-loop skill runs `graphify vault`** (the slice loop rebuilds the *code* graph at `/reflect:298` via `graphify code .`; the only `graphify vault architecture` executors are `/adopt`, `/discover`, `/heavy-architect`, `/sync` — the non-in-loop sites already enumerated in `vault_flip_prose_inventory._RESIDUAL` and deferred to the 318-prose-rewrite slice). The `vault_edit root` subcommand that AC3 would have needed is dropped with it (no consumer). See Out of scope.

## Acceptance criteria

1. **The UNAMBIGUOUS in-loop skill vault WRITE-ops route through the seam.** The write-ops whose destination is unambiguously the canonical vault (NOT entangled with the worktree-vs-external bootstrap) resolve via `vault_edit`: the **archive `mv`** (`/reflect`, `/archive` → `slices/archive/`) → `vault_edit move`; `/drift-check`'s **drift-log.md** append → `vault_edit append`. (Scope-narrowed per `/critique-review` M-add-2: `/commit-slice`'s archived-folder **reads** are DROPPED from AC1 — they are 4 structurally-different prose/grep shapes, reads fail LOUD not silent at flip, and their literals are already `rewrite-at-flip` in the inventory → they fold into the prose-rewrite slice.) The bootstrap-entangled per-slice **active-folder** writes (`/reflect` reflection.md, `/validate-slice` validation.md, `/slice` scaffold, `/build-slice` `git add`) stay **deferred to the flip slice** (it owns the worktree-vs-external decision — over-routing now would move slice-authoring artifacts out of the worktree, a BRANCH-3 violation) → the op-gate's `OP_DEFERRED_TO_FLIP` class. **OSDG-1 re-sync** = `{/reflect}` (the ONLY guarded edited skill — archive-`mv`). The op-gate is enforced by its **suite test + shippability row**, NOT a `/build-slice` Step-6 wiring (build-time deviation, m2-verified precedent: slice-100/107 flip-prep audits are suite-test+shippability enforced, no RULE-ID, no Step-6 wiring) → build-slice/validate-slice are NOT edited. `/archive` + `/drift-check` are edited-but-**unguarded** (no `*_skill_drift.py` content-equality test — NOT "no installed copy": they DO have installed copies, m-add-5) → their installed `~/.claude/skills/` copies are **hand-synced** this slice with a documented no-enforcement residual (a future OSDG-1 extension is flagged as a candidate).
2. **The SKILL.md-prose blind spot is closed — by REUSE, in-loop-scoped, gate-visible.** Extend the existing `tools/vault_flip_prose_inventory.py` (slice-107 — already scans `skills/**/SKILL.md`, region-anchors on `in_code` + `_OP_VERB_RE`, `--strict` gate-capable) with an **`--op-gate` mode** flagging un-routed vault **write-OPS** (`mv`/`cp`/`git add`/`Write`-target) inside anchored regions — NOT a third parallel classifier (CSP-1/DRY). Bare prose mentions (~244) + reads are NEVER flagged. **4 gate-visible classes** keyed structurally on the op's **destination** (B2/AP-15) + a pinned **`_IN_LOOP_SKILLS`** allowlist (M-add-1): `OP_ROUTED` (seam token); `OP_DEFERRED_TO_FLIP` (per-slice active-folder dest; owner = flip slice / **R-32.a**); `OP_OUT_OF_SCOPE` (un-routed write in an out-of-loop skill, or to an undecided-flip-disposition file like the `slice-queue.md` ledger; owner = prose-rewrite/flip slice); `OP_UNROUTED` (un-routed in-loop write to a vault file slice-111 commits to routing → exit 2). All four buckets enumerated + count-floored (AP-12: never a silent waiver). Implements [[decisions/ADR-102]] / [[decisions/ADR-104]]; shippability rows propagated (RPCD-1/SCPD-1). The exact `OP_OUT_OF_SCOPE` / deferred-allowlist membership is finalized at build via APED-1 (gate must go green on the real corpus) + an AP-4 code-Critic pass.
3. **Reversible + green-throughout.** No physical move, no `git rm --cached`, no `.gitignore` edit, no config write, no `_vault_paths` resolution change. The slice is revertible by a plain `git revert`, and the default suite is green at every commit (the AC1 routing removes `architecture/` literals from the slice-107 prose-inventory baseline — `_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` + `EXPECTED_TOTAL` are **re-pinned in the same slice**, FBCD-1 `318` fan-out, so the suite never goes red — M1); the seeded flip-sim (slice-110's binding gate) stays green.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Unambiguous skill WRITE-ops seam-routed | the archive `mv` (`/reflect`, `/archive`) → `vault_edit move` + drift-log.md (`/drift-check`) → `vault_edit append`; `vault_edit move` dest-exists guard checks the **final landing path** `<--to>/basename(<--from>)` not `--to` (M2); OSDG-1 drift test green for the re-synced guarded skill (`/reflect`) — `pytest -q tests/methodology -k "reflect_skill_drift"`; the unguarded edited skills' (`/archive`, `/drift-check`) installed `~/.claude` copies hand-synced (m-add-5) |
| 2 | Prose op-gate closed (REUSE, in-loop-scoped) | `$PY -m tools.vault_flip_prose_inventory --op-gate`: a synthetic in-loop un-routed `mv slices/foo slices/archive/` → **`OP_UNROUTED`** (non-vacuity, AP-5); a dual-literal `mv slices/slice-NNN slices/archive/` → **`OP_UNROUTED`** (source literal ≠ deferral, B2/AP-15); an out-of-loop `Append architecture/<aggregate>` → **`OP_OUT_OF_SCOPE`** + a NEW in-loop un-routed shared-aggregate write → **`OP_UNROUTED`** (M-add-1: gate green AND still bites in-loop); ~244 bare mentions + reads **NOT flagged** (non-over-flag, APED-1); per-slice writes → gate-visible `OP_DEFERRED_TO_FLIP`; `--strict` clean on the real corpus; **AP-4 code-Critic** on the parser change |
| 3 | Reversible + green | `git revert` of the slice restores prior state; default `pytest -q` green at every commit — incl. the slice-107 inventory pins **re-pinned** to the new `318−K` (`_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` + `EXPECTED_TOTAL`, FBCD-1 `318` fan-out — M1); seeded flip-sim green; `(git ls-files architecture | Measure-Object -Line).Lines` unchanged (nothing moved/untracked) |

## Must-not-defer

- [ ] **OSDG-1 re-sync** for the guarded edited skill (`/reflect` archive-`mv`) — verified against `tests/methodology/test_reflect_skill_drift.py`. (build-slice/validate-slice NOT edited — the op-gate is suite-test-enforced, m2 precedent.)
- [ ] **Hand-sync the unguarded edited skills' installed copies (m-add-5)** — `/archive`, `/drift-check` DO have `~/.claude/skills/` copies (the "no installed copy" rationale was FALSE); routing the in-repo copy only takes effect in fielded loops if the installed copy is synced. They lack a `*_skill_drift.py` test, so the sync is unenforced — hand-sync this slice + document the residual + flag a future OSDG-1 extension candidate.
- [ ] **Op-gate enforced via suite test + shippability (m2)** — `test_vault_flip_op_gate.py::test_real_corpus_op_gate_green` runs in the pre-finish full suite (fails on any new in-loop OP_UNROUTED); a shippability row gives discoverability. NOT a build-slice Step-6 RULE-ID gate (MEPD-1 EXCLUDE precedent verified: slice-100/107).
- [ ] **Op-gate in-loop scoping + green-on-corpus (M-add-1)** — `OP_UNROUTED` (exit 2) fires ONLY for `_IN_LOOP_SKILLS`; out-of-loop / undecided-disposition writes → gate-visible `OP_OUT_OF_SCOPE` (count-floored, owner = prose-rewrite/flip slice), so the gate goes green on the real corpus WITHOUT silently excluding anything (APED-1 finalizes the allowlist at build).
- [ ] **AC2-gate non-vacuity** — prove the op-gate catches an un-routed in-loop write (synthetic + dual-literal fixtures) AND still bites a NEW in-loop write while passing out-of-loop ones, not just passes on already-clean prose (AP-5/B2/M-add-1).
- [ ] **AC2-gate non-over-flag** — prove the ~244 real bare-prose mentions are NOT flagged, against the real corpus (APED-1 — execute against the actual SKILL.md set, not a design-time assumption).
- [ ] **AP-4 code-Critic pass** on the parser change (a new/extended classifier mode is exactly the class the code-Critic catches that the design+meta stack structurally cannot).
- [ ] **`OP_DEFERRED_TO_FLIP` is gate-VISIBLE + has a contractual consumer** — the AC1-deferred per-slice-write prose lands in a distinct, owner-tagged bucket; risk-register **R-32.a** names "drain to ∅" as a flip-slice pre-finish obligation (not just "the flip slice will grep it" — AP-12 / M3). Never a silent baseline.
- [ ] **Re-pin the slice-107 inventory baseline in the SAME slice (M1)** — routing removes `architecture/` literals → `_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` + `EXPECTED_TOTAL` must be re-pinned to the new `318−K` (measured live, APED-1), with the FBCD-1 `318` count-literal fan-out grepped repo-wide (tests, docstring lines 17-19/45-46/307-312, shippability #113 narrative). Default suite green at every commit.
- [ ] **`vault_edit move` dest-exists guard (M2)** — checks the FINAL landing path `<--to>/basename(<--from>)`, NEVER the `--to` directory (which always exists for `slices/archive/`); reuses `_resolve_in_vault` for both `--from`/`--to`.
- [ ] **Cross-store `mv` coherence (R-32.b)** — `vault_edit move` resolves both endpoints under one `VAULT_ROOT`; the worktree-local-source residual is recorded as R-32.b for the flip slice (fail-loud, never silent mis-write), NOT silently mis-routed here.
- [ ] **No behavior change to `_vault_paths`** — this slice does NOT touch the seam's resolution logic; it only makes consumers resolve correctly through it.
- [ ] **Don't silently exclude** — any in-loop skill write-op that cannot be routed this slice is enumerated + dispositioned (`OP_DEFERRED_TO_FLIP` with owner), never quietly skipped.

## Out of scope (→ the follow-on flip slice / the prose-rewrite slice)

- **The physical flip** — seed the external store, write the vault-root config, `git rm --cached -r architecture`, `.gitignore`, remove in-tree copies, the `/commit-slice` RETIRE no-op, **R-32 retirement + anti-revert pin**. R-32 retires THERE, not here.
- **The bootstrap-entangled per-slice active-folder write routing** (`/reflect` reflection.md, `/validate-slice` validation.md, `/slice` scaffold, `/build-slice` `git add`) — the flip slice owns the worktree-vs-external bootstrap decision. Enumerated, not silently dropped.
- **ALL `graphify vault` flip-awareness (was AC3; dropped per `/critique` B1)** — there is no in-loop `graphify vault` executor to route. The real `graphify vault architecture` builders are non-in-loop: `/adopt`, `/discover`, `/heavy-architect`, `/sync` + root `CLAUDE.md` (the `vault_flip_prose_inventory._RESIDUAL` set), plus `/design-slice:62`'s *prose* mention (a `rewrite-at-flip` literal, not an op). All fold into the 318-prose-rewrite slice. The `vault_edit root` subcommand is dropped with AC3 (no consumer).
- **The 318-site prose rewrite** (skills/agents/CLAUDE.md/README/INSTALL location-literals) — a separate later slice (now also owns the deferred graphify-vault flip-awareness).

## Dependencies

- Prior slices: [[slice-110-make-pipeline-vault-location-agnostic]] — the Phase-1 prep this directly continues; inherits its deferred AC2/AC3/AC4 + [[decisions/ADR-102]]. [[slice-107-inventory-vault-flip-prose-surface]] — `tools/vault_flip_prose_inventory.py`, the AC2-gate REUSE target (already region-anchors `SKILL.md` + has `_OP_VERB_RE` + `--strict`). [[slice-100-add-vault-flip-readiness-audit]] / [[slice-102-vault-flip-readiness-tests]] — the readiness-audit family (the CSP-1 reason NOT to add a third classifier). [[slice-098-route-or-retire-git-coupled-vault-tools]] — `vault_is_external` signal.
- Vault refs: [[decisions/ADR-102]] (the decision ratified at slice-110, implemented here), [[decisions/ADR-065]] / [[decisions/ADR-085]] (the `VAULT_ROOT` seam consumers route through), [[decisions/ADR-087]] / [[decisions/ADR-088]] (the `vault_edit` append/rewrite channels the routed ops use).
- Risk register: [[risk-register#R-32]] — this slice closes the last in-loop-skill prep residual; R-32 stays `mitigating` and retires at the physical flip (next slice).
- Tools: `tools/_vault_paths.py` (the seam — consumed, NOT changed), `tools/vault_edit.py` (the routed write/append/rewrite channel), `tools/vault_flip_prose_inventory.py` (extended at AC2), `tools/_vault_git.py` (`vault_is_external`).

## Mid-slice smoke gate

At ~50% — after the AC1 skill-op routing edits but before/while the AC2 op-gate parser extension:
```
$PY -m pytest -q tests/methodology -k "skill_drift"          # OSDG-1 drift green for re-synced /reflect, /commit-slice
$PY -m tools.vault_flip_prose_inventory --strict             # inventory still clean (no regression from the skill edits)
```
Expected: default-suite drift tests green; the inventory `--strict` baseline holds (the AC1 routing edits change op-routing, not the location-literal multiset — if a literal count shifts, re-baseline deliberately, never silently). If the default suite goes red at any point → STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. AC2-gate non-vacuity + non-over-flag + AP-4 code-Critic + gate-visible `DEFERRED_TO_FLIP`)
- [ ] OSDG-1 drift tests green for `/reflect` + `/commit-slice` (the re-synced guarded skills)
- [ ] /drift-check passes (full mode)
- [ ] Default suite green AND seeded flip-sim green (slice-110's binding gate not regressed)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints; `git ls-files architecture` line count unchanged (nothing moved/untracked)
