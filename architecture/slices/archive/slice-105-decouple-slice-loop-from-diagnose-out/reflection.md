# Reflection: Slice 105 decouple-slice-loop-from-diagnose-out

**Date**: 2026-06-03
**Shipped**: YES

## Validated

- **The sole live `diagnose-out/backlog.md` reader was `test_bcr_1_round_trip_end_to_end.py`** — deleting it closes the seed need. Validated by the seedless full suite: 1387 passed / 0 failed with `diagnose-out/` AND `graphify-out/` renamed aside (run twice — mid-build smoke + validate). No hidden second consumer surfaced.
- **`branch_workflow_audit.py` imports only `canonical_worktree_path`/`slice_branch_name` from `_worktree_paths.py`** — removing `seed_derived_dirs`/`_DERIVED_DIRS` doesn't break it. Validated: BRANCH-1 audit exit 0; the two helpers byte-untouched (code-Critic verified).
- **R-20 fully closed** — the cp-r tax is zero on every worktree path. Validated: 0 `seed_derived_dirs`/`_DERIVED_DIRS` refs in `tools/` + `skills/`; `test_r_20_retired` green; STP-1 clean.
- **BCR-1 consume-only redefinition** — `/reflect` round-trip-write retired, `/slice` source-#7 consume side preserved. Validated: reflect/SKILL.md round-trip directive absent, `/slice` "MUST consult diagnose-out/backlog.md" anchor present, consume-side tests #1–#3 pass.
- **SUP-1 partial-supersession** — ADR-055/ADR-090 byte-unmodified; supersession encoded only at ADR-094/ADR-095 `supersedes:`. Validated: `git diff --name-status master..HEAD -- architecture/decisions/` shows only `A ADR-094`/`A ADR-095`.
- **Shippability 111/111** — no past slice regressed.

## Corrected

- **Catalog index: design said "Row #105" → reality is row #112.** Catalog row indices diverged from slice numbers at slice-079 (two rows) and don't track slice numbers; the actual next free index was #112 (slice-103 already held #111). The design's "Row #105" was loose shorthand. Corrected in-build (row #112 added; `test_v_0_82_0_decouple_shippability_consumer_propagation` row-scopes `| 112 |`). Noted in build-log.
- **Design "Tests touched" table omitted the rolling version-sync test.** Every PMI-1 version bump must rename `test_version_files_synchronized_at_v_0_<old>` → `_at_v_0_<new>` (all 4 legs + docstring) AND bump its shippability row #75 command-cell citation. The design didn't list it; it surfaced as the lone seedless-smoke red (`test_version_files_synchronized_at_v_0_81_0` hard-pinned 0.81.0). Corrected in Batch F. This is a *standing* version-bump obligation (the test's own docstring lists the rename chain slice-067/.../099/105, N≥11).
- **Process deviation (not a defect): `vault_edit` CAS → Edit tool** for the build-time vault edits (risk-register R-20 closure, shippability rows). design.md L64 prescribed the `vault_edit rewrite` CAS channel; build used the Edit tool. Rationale: an isolated BRANCH-3 worktree has no concurrent writer, so R-32 CAS is moot, and surgical Edit avoids whole-file-rewrite drift on a giant catalog. No gate enforces the channel for build-time edits (SVW-1 = skill prose; VWS-1 = `tools/*.py` AST). Logged in build-log Design Deviations. (This /reflect's OWN shared-aggregate writes — lessons-learned append, `_index` regens — DO route through `vault_edit` per the skill's mandate.)

## Discovered

- **ADR-094:24 path-citation drift** — ADR-094 cites the missing-graph non-fatal test at `tests/methodology/test_slice_queue_output.py`, but it lives at `tests/skills/slice/test_slice_queue_output.py`. The cited test passes (the behavior ADR-094 relied on is real); only the prose path is wrong. ADRs are append-only → recorded here, NOT edited in place. Impact: cosmetic; a future ADR/erratum can correct it. (Surfaced by the code-Critic as out-of-scope context.)
- **Version-bump mechanics are a Critic/design-template blind spot.** The design-Critic scored 13/13 VALIDATED on structural/PTFCD-1/append-only dimensions but did NOT enumerate (a) the rolling version-sync test rename, nor (b) the actual catalog-index number (it echoed the design's loose "#105"). Both are deterministic consequences of any version-bumping methodology slice. Candidate: a build-check or design-template "version-bump obligations" checklist (see Critic calibration → Pattern).

## Deferred

- None. The slice closed its full scope (both decoupling directions). The external-shared-vault flip remains a separate in-flight initiative — not deferred *by* this slice.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions (all ACCEPTED-FIXED, verdict CLEAN) + reality observed in build/validate:

- **B1** (SUP-1 append-only convention): **VALIDATED** — had the original add-`superseded-by`-pointer plan shipped, it would have violated the `test_adr_019_unmodified_per_append_only_rule`-pinned convention. Build confirmed ADR-055/090 byte-unmodified; convention held.
- **B2** (shippability token-drop vs row-delete + PTFCD-1): **VALIDATED — empirically materialized.** The predicted dangling-citation failure literally fired: `test_ptffd1...corpus_clean_under_func_level` red'd on rows #54/#56 citing the deleted test until the tokens were dropped. Exactly the Critic's PTFCD-1 prediction.
- **B-add-1** (meta-Critic; `test_resolve_slice_dir.py:77` is_file guard): **VALIDATED** — removed in Batch A; would have red'd on the deleted file otherwise.
- **M1** (row #79 cp_r token; PTFCD-1): **VALIDATED — materialized** in the same ptffd1 red (row #79 citing the deleted cp_r test).
- **M2** (atomic batch + stale row #107 narrative): **VALIDATED** — the atomic prose↔test batching held; row #107 seed-narrative was genuinely stale-by-construction and reworded.
- **M-add-1** (meta-Critic; 3 atomic prose↔test pairs incl. reflect): **VALIDATED** — the reflect-side pairing (Batch C) held with no intermediate red.
- **M-add-2** (meta-Critic; `test_worktree_paths.py:17` import removal): **VALIDATED** — removing `seed_derived_dirs` from the import was required to avoid an ImportError collapsing the module.
- **M3** (AC1 delete-vs-fixture back-prop): **VALIDATED** — AC1 was unsatisfiable as worded (fixture); harmonized to "delete".
- **M4** (v0.82.0 entry-pin + propagation + new row): **VALIDATED** — built exactly; without it the slice's critical path is uncatalogued.
- **M5** (/slice step-renumber cross-ref): **VALIDATED** — the renumber cross-ref was coherent post-edit (code-Critic re-confirmed).
- **m1** (5 version surfaces enumerated): **VALIDATED** — all 5 bumped + gated.
- **m2** (smoke-gate graphify-out rename precaution): **VALIDATED** (low-stakes) — no false failure occurred; the STOP-find-it framing was sound.
- **label** (Row #63 → catalog row #53): **VALIDATED** — #53 is slice-053; #63 is slice-063/NAW-1; the correction was right.

**Missed by Critic**:
1. The **rolling version-sync test rename** (`test_version_files_synchronized_at_v_0_NN_0` + its shippability #75 citation) — a deterministic version-bump obligation the design-Critic's M4 (new entry-pin) did NOT extend to the EXISTING rolling pin. Surfaced as the lone seedless-smoke red.
2. The **actual catalog-index number** — the Critic echoed the design's loose "Row #105" rather than verifying the next free index (#112).
3. **ADR-094:24 path citation** — the design-Critic read ADR-094 but did not flag the `tests/methodology/` vs `tests/skills/slice/` path drift (the code-Critic caught it later).

**Pattern**: The design-Critic was **excellent on structural correctness** — 13/13 VALIDATED, zero FALSE-ALARM, zero OVERRIDE-MISJUDGED; it caught two genuine build-breakers (B1 append-only, B2 PTFCD-1) that would have red'd the suite, plus the meta-Critic added 3 valid reverse-dependency findings. Its blind spot is **version-bump mechanics**: the rolling-version-sync-test rename and the catalog-index arithmetic are deterministic, recurring (N≥11 on the rename), and *not* enumerated by the design template or flagged by the Critic. A "version-bump obligations" checklist would close it. This is the third consecutive 9/9-style clean Critic showing on a cross-cutting tooling slice (consistent with the In-house-methodology-surfaces voluntary-Critic evidence), now with a sharpened, actionable blind-spot signal for `/critic-calibrate`.

## Lessons for next slice

- **Version-bumping methodology slices carry a fixed obligation set the design template should enumerate**: (1) 5 version surfaces (VERSION/plugin.yaml/pyproject/ai-sdlc-VERSION/changelog header) + `pip install --upgrade .`; (2) rename `test_version_files_synchronized_at_v_0_NN_0` (+4 legs +docstring) → new version; (3) bump its shippability row #75 command-cell citation; (4) the catalog index for the new row is `max(existing index)+1`, NOT the slice number. Items (2)–(4) bit this slice (caught, but late, by the full suite).
- **Catalog row index ≠ slice number** — always read the actual tail of `shippability.md` for the next index; don't trust a design's "#NNN" shorthand.
- **A surgical Edit can be the right call over `vault_edit` CAS for a private-worktree build-time edit** — but log the deviation explicitly (the CAS channel is mandatory for shared/concurrent vaults and for `/reflect`'s own writes).

## Vault updates made (thin vault — small list)

- This slice's [[reflection.md]] — written (this file).
- [[lessons-learned.md]] — appended slice-105 entry (via `vault_edit append`).
- [[shippability.md]] — row #112 was added during `/build-slice` (Batch D, per RPCD-1/SCPD-1) — NOT re-added here (no duplicate).
- [[risk-register.md]] — no new entry (R-20 already retired/fully-closed in build; the version-bump-obligations discovery is a build-check candidate, not a risk).
- [[slices/_index.md]] + [[slices/archive/_index.md]] — regenerated at auto-archive (via `vault_edit rewrite` CAS).
- **No ADR edits** — ADR-094:24 path drift recorded here only (ADRs append-only).
