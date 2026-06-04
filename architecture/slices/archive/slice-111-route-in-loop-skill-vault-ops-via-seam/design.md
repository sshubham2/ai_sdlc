# Design: Slice 111 route-in-loop-skill-vault-ops-via-seam

**Date**: 2026-06-04
**Mode**: Standard

The **Phase-2 follow-on** to slice-110 (which made the test suite location-agnostic). This slice routes the remaining UNAMBIGUOUS in-loop skill vault **write-ops** through the `VAULT_ROOT` seam (AC1) and closes the SKILL.md-prose write-op blind spot with an in-loop-scoped, gate-visible op-gate that *verifies* the routing (AC2, implements [[ADR-102]]). **No physical move; R-32 retires at the follow-on flip slice.** Reversible (`git revert`); default suite + slice-110 seeded flip-sim green at every commit.

> **Critique-1 refinements**: B1 — dropped AC3 (`graphify vault` flip-awareness) + `vault_edit root` (no in-loop `graphify vault` executor exists). B2 — op-gate keys on the op's *destination*, not any line literal (AP-15). M1 — added the slice-107 inventory baseline re-pin step. M2 — `vault_edit move` dest-guard checks the final landing path. M3 — R-32.a/R-32.b sub-entries.
>
> **Critique-review refinements (meta-Critic EXTEND; user-ratified at TRI-1)**: **M-add-1** — the op-gate gains a 4th gate-visible class `OP_OUT_OF_SCOPE` + a pinned `_IN_LOOP_SKILLS` allowlist; `OP_UNROUTED` (exit 2) fires only for in-loop skills, so the gate goes green on the real corpus without silently excluding out-of-loop / undecided-disposition writes. **M-add-2** — AC1 narrowed: `/commit-slice` archived-**reads** dropped (deferred to the prose-rewrite slice; reads fail loud, 4 ambiguous shapes), making the M1 re-pin `K` deterministic. **m-add-5** — the "no installed copy" rationale for `/archive`+`/drift-check` was FALSE; corrected to "unguarded (no `*_skill_drift.py`)" + hand-sync the installed copies (`/archive`, `/drift-check`, `/validate-slice`) + document the residual. **m-add-3** — add `query-design:59` to `_RESIDUAL` at build. **m-add-4** — fixed the stale `/design-slice` OSDG line. OSDG-1 re-sync set: `{/reflect, /build-slice}`. Verification depth (user TRI-1): proceed to build; the build-time APED-1 corpus-execution + the AP-4 code-Critic are the empirical gate for M-add-1.

## Decisions settled (incl. /critique-1 + /critique-review refinements)

| Question | Decision | Why |
|----------|----------|-----|
| Route the archive `mv` (a dir move)? | **`vault_edit move`** — both endpoints under `VAULT_ROOT`; dest-exists guard on the **final landing path** `<--to>/basename(<--from>)` (M2) — [[ADR-103]]. | Keeps `/archive:56` semantics; cross-store coherence; uniform `vault_edit` routed-signal. |
| Route `/commit-slice` archived reads? | **DROPPED from AC1 (M-add-2)** — defer to the prose-rewrite slice. | 4 ambiguous prose/grep shapes; reads fail LOUD not silent; their literals are already `rewrite-at-flip`. Makes M1 `K` deterministic. |
| Op-gate scope vs taxonomy? | **`_IN_LOOP_SKILLS` allowlist + 4 classes incl. `OP_OUT_OF_SCOPE`** keyed on destination (M-add-1/B2). | Gate goes green on the real corpus; out-of-loop / undecided-disposition writes stay gate-visible (AP-12), not false `OP_UNROUTED`. |
| Reads gated? | **Write-ops only.** | Reads fail LOUD; the R-32 hazard is the SILENT mis-write. |
| Deferred buckets' consumers? | **R-32.a** (drain `OP_DEFERRED_TO_FLIP`) + **R-32.b** (cross-store `mv`) + the prose-rewrite slice (`OP_OUT_OF_SCOPE`) — all contractual (M3/AP-12). | A gate-visible bucket needs a contractually-required consumer. |
| Unguarded skills' installed copies? | **Hand-sync `/archive`+`/drift-check`+`/validate-slice` + document residual** (m-add-5); rationale corrected to "no `*_skill_drift.py`". | They DO have installed copies; in-repo-only routing wouldn't take effect in fielded loops. |
| New RULE-ID / VERSION bump? (methodology-changelog **Inclusion heuristic**, BC-PROJ-10) | **MEPD-1(b) why-none discharged** (= MEPD-1 EXCLUDE): no `## vN.N.0` entry, no 4-part PMI-1 bump, no new RULE-ID. Precedent-class: the flip-prep family slice-106/109/110 (all MEPD-1 EXCLUDE, no changelog entry — verified at build, m2). The op-gate implements the already-minted [[ADR-102]] (its enforcement half), so no new RULE-ID is minted → the META-1 enforcing assertion `tests/methodology/test_methodology_changelog.py` is satisfied vacuously (no new `## vN.N.0` entry to pin). Shippability row #117 still propagates (RPCD-1/SCPD-1). | A new ADR + a new tool subcommand/mode fire BC-PROJ-10(a)/(b); classification is `MEPD-1(b)`, not `bump-required`. |

## What's new

- **`vault_edit move` subcommand** ([[ADR-103]]) in `tools/vault_edit.py`. `move --from <vault-rel> --to <vault-rel>` resolves both under `VAULT_ROOT` (reusing `_resolve_in_vault`), refuses if the **final landing path** `<--to>/basename(<--from>)` exists (M2 — NOT the `--to` dir), then `shutil.move`. No CAS/lock (one-shot dir rename).
- **`--op-gate` mode** ([[ADR-104]]) in `tools/vault_flip_prose_inventory.py`. Reuses `_iter_scan_files` (over `skills/**/SKILL.md`), `_in_inline_code` + fence-tracking, `--strict` baseline. New `_WRITE_OP_VERBS` subset (`mv`/`move`/`cp`/`copy`/`rm`/`delete`/`write`/`edit`/`create`/`append` + `git add` bigram; detection ⊇ classification, AP-16/m1). Pinned **`_IN_LOOP_SKILLS`** allowlist (`slice`, `design-slice`, `critique`, `critique-review`, `build-slice`, `code-review`, `validate-slice`, `reflect`, `commit-slice`, `archive`, `drift-check`; count-floored, FBCD-1). **Destination-keyed** classification, first-wins (sink-undeterminable → `OP_UNROUTED` fail-safe): (1) seam token → `OP_ROUTED`; (2) dest = per-slice active folder → `OP_DEFERRED_TO_FLIP` (owner R-32.a); (3) skill ∉ `_IN_LOOP_SKILLS` OR dest = undecided-disposition file (`slice-queue.md` ledger / `git add` tracked paths) → `OP_OUT_OF_SCOPE` (owner = prose-rewrite slice; pinned allowlist finalized at build via APED-1); (4) else in-loop un-routed shared-aggregate write slice-111 commits to → `OP_UNROUTED` (exit 2). All four buckets enumerated + count-floored (AP-12). Distinct from the inventory's `rewrite-at-flip` classes.
- **AC1 skill-op routing**:
  - `/reflect:320` + `/archive:51` archive `mv` → `$PY -m tools.vault_edit move --from slices/slice-NNN-<name> --to slices/archive/`.
  - `/drift-check:109` `Write architecture/drift-log.md (append)` → `$PY -m tools.vault_edit append --file drift-log.md --content-file <entry>` (bonus: R-32 append-safety).
- **M1 — re-pin the slice-107 inventory baseline (same slice)**: AC1 routing replaces `architecture/...` literals with vault-relative `slices/...`, so `_MATCH_RE` no longer matches them → `REWRITE_AT_FLIP` drops to `318−K` (K now deterministic post-M-add-2: archive `mv` ×4 + drift-log ×1 ≈ 5, measured live). After the AC1 edits, re-run `--json`, re-pin `_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` + `EXPECTED_TOTAL`, FBCD-1-fan-out the `318` literal repo-wide (docstring lines 17-19/45-46/307-312, `tests/methodology/test_vault_flip_prose_inventory.py`, shippability #113).
- **m-add-3** — add `query-design:59` (+ confirm `archive:216`) to `_RESIDUAL` (the bounded bare-`architecture`-arg `graphify vault` set the prose-rewrite slice consumes), updating any `_RESIDUAL` count pin.
- **Op-gate ENFORCEMENT = suite test + shippability row, NOT a `/build-slice` Step-6 RULE-ID gate** (build-time deviation, m2-verified precedent): `test_vault_flip_op_gate.py::test_real_corpus_op_gate_green` runs in the pre-finish full suite and fails on any new OP_UNROUTED. slice-100's `vault_flip_readiness_audit` + slice-107's `vault_flip_prose_inventory` are NOT Step-6-wired either — they are suite-test + shippability enforced, MEPD-1 EXCLUDE, no RULE-ID. The original design's "wire into Step 6" was a wrong assumption; deviating to the precedent drops the build-slice/validate-slice edits (sound simplification — less surface, convention-aligned).
- **OSDG-1 re-sync** of the guarded edited skill: `/reflect` (archive `mv`) — the ONLY guarded skill edited (build-slice/validate-slice NOT edited under the enforcement above). **m-add-5 hand-sync** the unguarded edited skills' installed copies: `/archive`, `/drift-check` (no `*_skill_drift.py` — unenforced; documented residual + future OSDG-1-extension candidate).
- **Shippability rows** (RPCD-1/SCPD-1) for `vault_edit move` + the op-gate.

## What's reused

- `tools/vault_flip_prose_inventory.py` (slice-107) — AC2 REUSE target (`_in_inline_code`, fence-tracking, `_OP_VERB_RE`/`_iter_scan_files`, `--strict` baseline + `_CLASS_COUNT_FLOOR`). Additive mode, NOT a third classifier (CSP-1).
- `tools/vault_edit.py` (slice-095/097) — `append`/`rewrite`/`read` already route the CONTENT RMWs; `_resolve_in_vault` reused for `move`.
- `tools/_vault_paths.py` (`VAULT_ROOT`) — **consumed, NOT changed** (dependency leaf).
- [[ADR-102]] (implemented here), [[ADR-088]] (the `vault_edit rewrite` CAS the `_index.md` writes already use).

## Components touched

### `tools/vault_edit.py` (modified — AC1; [[ADR-103]])
- **Responsibility**: gain a `move` subcommand (seam-resolved dir move, final-landing-path guard).
- **Key interactions**: `_vault_paths.VAULT_ROOT` + `_resolve_in_vault`; `/reflect` + `/archive`.

### `tools/vault_flip_prose_inventory.py` (modified — AC2; [[ADR-104]])
- **Responsibility**: gain `--op-gate` mode — in-loop-scoped, destination-keyed, 4-class; flags `OP_UNROUTED`, enumerates the gate-visible deferred/out-of-scope buckets.
- **Key interactions**: `skills/**/SKILL.md`; `/build-slice` Step 6 + `/validate-slice`; `architecture/shippability.md`.

### In-loop skills (modified — AC1 routing only)
- `/reflect`, `/archive` (archive `mv` → `vault_edit move`), `/drift-check` (drift-log → `vault_edit append`). OSDG-1 re-sync `{/reflect}`; hand-sync installed `/archive`+`/drift-check` (m-add-5). build-slice/validate-slice NOT edited (op-gate is suite-test-enforced — m2 precedent).

## Contracts added or changed

### `vault_edit move` (new subcommand)
- **Defined at**: `tools/vault_edit.py`. Both args resolved under `VAULT_ROOT` via `_resolve_in_vault`. **Dest-exists guard (M2)**: exit 2 iff `<--to>/basename(<--from>)` exists (the `--to` dir existing is NOT a refusal). Success → `shutil.move`, exit 0.

### `--op-gate` exit contract (new)
- **Defined at**: `tools/vault_flip_prose_inventory.py`. 0 clean (no `OP_UNROUTED`; under `--strict` no count-floor shrink across the 4 op-classes + `_IN_LOOP_SKILLS`) · 2 gate · 1 usage error. Mirrors the inventory contract.

## Data model deltas
No persistent schema. **M1**: the inventory count pins (`_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`) re-derived to `318−K`. The op-gate adds in-module pins: `_IN_LOOP_SKILLS` (+ count), the per-op-class count-floors, and the `OP_OUT_OF_SCOPE` deferred-allowlist (+ count) — all FBCD-1 counted sets, re-derivable from the corpus, finalized at build (APED-1).

## Wiring matrix

Per **WIRE-1**. This slice introduces **NO new modules** — `vault_edit move` is a subcommand of existing `tools/vault_edit.py`; `--op-gate` is a mode of existing `tools/vault_flip_prose_inventory.py`. Both are additive surfaces on existing modules, so the matrix is header-only (the audit treats a zero-row matrix as clean); their consumers are the new/extended tests below.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

Consumer tests (existing extended / new):
- `tests/methodology/test_vault_edit_cli.py` — `move`: seam-resolved; **succeeds** when `slices/archive/slice-X` absent even though `slices/archive/` exists (M2); exit 2 when it exists; outside-root refusal on `--from`/`--to`.
- `tests/methodology/test_vault_flip_op_gate.py` (new) — `OP_UNROUTED` non-vacuity (in-loop `mv slices/foo slices/archive/`); dual-literal (`mv slices/slice-NNN slices/archive/` → `OP_UNROUTED`, B2); `OP_OUT_OF_SCOPE` (out-of-loop `Append architecture/<aggregate>` → visible, exit 0) + a NEW in-loop un-routed write still → `OP_UNROUTED` (M-add-1); non-over-flag (244 + reads NOT flagged); `OP_DEFERRED_TO_FLIP` auto-classify (active-folder dest); real-corpus clean post-routing; `--strict` floor-shrink across all 4 classes + `_IN_LOOP_SKILLS`; detection⊇classification + `git add -A`/multi-path (m1).
- `tests/methodology/test_vault_flip_prose_inventory.py` — re-pinned `318−K` (M1); `_RESIDUAL` += `query-design:59` (m-add-3).
- `tests/methodology/test_reflect_skill_drift.py` — green after OSDG-1 re-sync (the only guarded edited skill).

## Phasing (build-time split point — mission-brief split-watch)

- **Phase A (AC1)**: `vault_edit move` + tests + the archive-`mv`/drift-log routing + the M1 baseline re-pin + OSDG-1 re-sync + m-add-5 installed-copy hand-sync. pytest- + drift-test-provable.
- **Phase B (AC2)**: the `--op-gate` mode (4 classes + `_IN_LOOP_SKILLS`) + the full test battery + APED-1 real-corpus execution (the M-add-1 empirical gate — gate must go green) + AP-4 code-Critic + shippability row + suite-test enforcement via `test_vault_flip_op_gate.py` (NOT Step-6 wiring — m2 precedent) + m-add-3. The dominant risk. `/build-slice` MAY ship Phase A + defer Phase B IF Phase A fills the day — but AC1 ships *unverified* without AC2's gate; prefer shipping both.

## Decisions made (ADRs)
- [[ADR-103]] — `vault_edit move` seam-routed directory move — reversibility: **cheap**.
- [[ADR-104]] — in-loop-scoped, destination-keyed, 4-class op-gate (implements [[ADR-102]]) — reversibility: **cheap**.

## Authorization model for this slice
None — local tool + skill-prose + audit edits; no auth surface.

## Error model for this slice
- `vault_edit move`: fail-closed on final-landing-path-exists / outside-root (exit 2).
- `--op-gate`: fail-closed (exit 2) on any in-loop `OP_UNROUTED`; sink-undeterminable → `OP_UNROUTED` (fail-safe). All deferred/out-of-scope buckets visible + count-floored + owner-tagged (R-32.a / prose-rewrite slice), never a silent waiver (AP-12). Non-vacuity asserted by synthetic fixtures incl. dual-literal (B2) + a new-in-loop-write-still-bites case (M-add-1).
- No `_vault_paths` resolution change.

## APED-1 obligations carried to /build-slice (the M-add-1 empirical gate)
The op-gate parser is NOT yet built; per the user's TRI-1 choice the build-time corpus-execution + AP-4 code-Critic ARE the gate for M-add-1. At build, MUST execute against the real corpus and prove: (a) the gate goes GREEN (0 `OP_UNROUTED`) after AC1 routing; (b) every out-of-loop / undecided-disposition shared-aggregate write lands in `OP_OUT_OF_SCOPE` (enumerated, not silent); (c) a NEW synthetic in-loop un-routed shared-aggregate write still → `OP_UNROUTED` (the gate bites in-loop); (d) detection ⊇ classification for all `git add` forms; (e) the `318−K` re-pin + the `_IN_LOOP_SKILLS`/`OP_OUT_OF_SCOPE` count-floors are derived from the live corpus, not assumed.
