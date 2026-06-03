# Design: Slice 105 decouple-slice-loop-from-diagnose-out

**Date**: 2026-06-03
**Mode**: Standard

## Project-frame note (PFS-1)

Project-frame consulted (advisory). Identity: spec-driven SDLC pipeline for AI implementers (Claude Code plugin), Standard mode. Trajectory: active families BRANCH / VWS / SVW / PFS / PCR / DCE; external-shared-vault flip in flight. **No misfit** — this slice *reduces* worktree-setup complexity (aligns with the BRANCH/worktree family) and removes in-tree derived-data coupling (aligns with the external-vault flip, which already treats `diagnose-out/` as a relocatable vault-location literal). It fights nothing in the trajectory.

## Design refinement vs. mission brief (read first)

The mission brief's **AC1** assumed the BCR-1 end-to-end test would be *fixtured*. Because this slice (Part 2) **retires** the `/reflect` round-trip-write, that test (`test_bcr_1_round_trip_end_to_end.py`) verifies the **inputs to a removed feature** — fixturing it would leave dead test code. **Decision: delete the test instead of fixturing it.** This satisfies AC1's *intent* (the slice loop no longer reads live `diagnose-out/`) more cleanly — no fixture, no live read at all. AC1 is hereby read as "the slice loop no longer reads the live `diagnose-out/backlog.md`", achieved by deletion. (`/validate-slice` checks the intent, not the mechanism.)

## What's new

- Two ADRs: **ADR-094** (retire the worktree derived-dir seed; partial-supersedes ADR-090's seed-step) + **ADR-095** (redefine BCR-1 as *consume-only*; partial-supersedes ADR-055's round-trip half).
- A `methodology-changelog.md` v0.82.0 entry + the version-pin cascade (VERSION / ai-sdlc-VERSION / ai-sdlc-tools / pyproject) and the forward-sync gates (MCFS-1 / AVFS-1 / TVFS-1).
- **No new code modules** → the WIRE-1 matrix is empty (header + separator only).

## What's reused / depended on

- `tools/_worktree_paths.py` — the seed lives here; `canonical_worktree_path` + `slice_branch_name` (the parts `branch_workflow_audit.py` imports) are **untouched**.
- `tools/branch_workflow_audit.py` — imports only `canonical_worktree_path` + `slice_branch_name` (verified), **NOT** `seed_derived_dirs`; removing the seed does not touch the audit.
- BCR-1 **consume side** ([[decisions/ADR-055]]) — `/slice` SKILL.md source #7 (consult `backlog.md` when present) is **retained unchanged**.
- The git-tracked vault (ADR-066) — slice-054's archived `mission-brief.md` travels to worktrees for free, so no diagnose seed was ever needed for that read.

## Components touched

### `tools/_worktree_paths.py` (modified)
- **Responsibility**: shared worktree path + branch SSOT. Loses its R-20 seed responsibility.
- **Change**: delete `seed_derived_dirs()` (`:94-114`), `_DERIVED_DIRS` (`:65`), and the now-unused `import shutil` (`:48`); update the module docstring (`:1-43`, `:61-64`) to drop the "R-20 derived-dir seed" responsibility.
- **Key interactions**: imported by `branch_workflow_audit.py` (path/branch only — unaffected).

### `skills/slice/SKILL.md` (modified — OSDG-1 guarded)
- **Change**: Step 5.5 — remove the seed step (current **Step 3**, the `seed_derived_dirs(...)` `$PY -c` invocation) and renumber the subsequent steps (Write → 3, queue → 4); drop the "Seed the R-20 gitignored derived dirs" prose + the `## Pipeline position` "R-20 seed" mention. The `WORKTREE=skip` fallback prose stays. **Within-file cross-ref propagation (per /critique M5)**: after renumbering, grep the Step 5.5 section for every `Step 3/4/5` reference and update the downstream narrative — the "**Step-5 (queue-commit) failure AFTER a successful worktree-add**" orphan-worktree note (`skills/slice/SKILL.md:~257`) becomes "Step-4 (queue-commit) failure"; verify "After Steps 5.5 + 6 + 6.5" and the rollback notes (Step-2 / Step-4 Write) stay coherent. The OSDG-1 mirror (installed `~/.claude/skills/slice/SKILL.md`) receives the identical renumber + cross-ref edits.

### `skills/build-slice/SKILL.md` (modified — OSDG-1 guarded)
- **Change**: `### Branch state` — remove the "Do NOT re-seed the R-20 derived dirs" note (`:67`), the `seed_derived_dirs(...)` create-path call (`:76`), and the legacy `cp -r diagnose-out/ graphify-out/` bash (`:96-97`).

### `skills/reflect/SKILL.md` (modified — OSDG-1 guarded)
- **Change**: remove the BCR-1 round-trip-write bullet (`:59`, the `diagnose-out/backlog.md round-trip` step in "Step 2: Update affected vault files"). The Corrected/Discovered/supersession bullets around it stay. BCR-1 becomes consume-only; the `**Closes:** SC-NNN` sentinel becomes inert documentation (no automation consumer) — noted in ADR-095, no longer described as a round-trip trigger.

## Contracts added or changed

No code endpoints/events. The **methodology contract** change: BCR-1 goes from "Consume-**and-Round-trip**" to "Consume-only." Recorded in ADR-095 + `methodology-changelog.md` + the project `CLAUDE.md` BCR-1 paragraph (`## Self-hosting discipline`).

## Data model deltas

None.

## Tests touched

| Test file | Action | Why |
|-----------|--------|-----|
| `tests/methodology/test_bcr_1_round_trip_end_to_end.py` | **delete** | Verifies inputs to the now-retired `/reflect` round-trip; deleting removes the sole live-`diagnose-out/` read (closes the seed need). |
| `tests/methodology/test_build_slice_skill_cp_r_step.py` | **delete** | Pins the cp-r prose step being removed; the contract it guards no longer exists. |
| `tests/methodology/test_worktree_paths.py` | **edit** | Remove the 3 `seed_derived_dirs` tests (`:53-97` region) **AND remove `seed_derived_dirs` from the `from tools._worktree_paths import (...)` block at `:17`** (per /critique-review M-add-2 — else `ImportError` fails the whole module's collection, including the surviving path/branch tests). Keep the path/branch tests. |
| `tests/methodology/test_bcr_1_backlog_round_trip.py` | **edit** | Remove the reflect-side round-trip anchor tests (#4–#8, `:221,:247,:296,:331,:366`); **keep** the consume-side `/slice` tests (#1–#3). Must batch with the `reflect/SKILL.md:59` bullet removal (M-add-1). |
| `tests/methodology/test_resolve_slice_dir.py` | **edit** | Per /critique-review **B-add-1 (BLOCKER)**: `:66-88` (`test_test_bcr_1_module_no_longer_carries_hardcoded_slice_054_dir`) does `assert (...test_bcr_1_round_trip_end_to_end.py).is_file()` at `:77` — deleting that file reds this test. In the SAME delete batch, delete/invert this guard (its slice-054-archive-fragile contract vanishes with the file); verify shippability rows #56/#57 (which run this module) stay green. |
| `tests/methodology/test_methodology_changelog.py` | **edit (add)** | Per /critique M4 (slice-099 `test_v_0_81_0_branch_3_*` paired-pin precedent): add `test_v_0_82_0_decouple_entry_present_in_repo` (asserts the v0.82.0 body cites `ADR-094`/`ADR-095`/`BCR-1`/`R-20`/`consume-only` + a `Rule reference` line — META-1 `:130`) + the paired `test_v_0_82_0_decouple_shippability_consumer_propagation` (asserts new Row #105 cites ADR-094/ADR-095/R-20). The B2/M1 row-#54/#56/#79 command-cell edits must keep `test_methodology_changelog.py:3724`/`:3768` (row-#54/#56-must-exist) green. |

## Vault / config surfaces touched

- `architecture/risk-register.md` — **R-20** → closure note appended (status stays `retired`, scope-broadened to "fully closed — seed mechanism removed; no derived dir is copied into worktrees"). Use the `vault_edit rewrite` CAS path ([[ADR-088]]) per `skills/reflect/SKILL.md:56` (capture base with `--out-file`, never shell `>`).
- `architecture/shippability.md` — the deleted/edited tests are cited across several rows. **Critical distinction (per /critique B2/M1): NEVER delete a catalog row — only edit its `Command` cell token(s).** Rows #54/#56/#79/#107 are independent critical-path rows that *other* tests require to keep existing.
  - **Row #54** (L64, slice-054/PVFS-1) + **Row #56** (L66, slice-056/R-15): drop the `tests/methodology/test_bcr_1_round_trip_end_to_end.py::test_bcr_1_sc054_round_trip_inputs_invariant` token from BOTH command-cell copies (the `<HOME>…` and `<interp>…` variants) in each; **keep the rows**. Verify post-edit row #54 still contains `PVFS-1` + `SC-001` and row #56 still contains `R-15` (else `test_methodology_changelog.py:3724` / `:3768` break). Reword each row's narrative describing the BCR-1 round-trip (the SC-001 `**Addressed:**` injection) to past-tense/retired so the catalog isn't stale-by-construction.
  - **Row #79** (L87, slice-079): drop the `tests/methodology/test_build_slice_skill_cp_r_step.py` token from both command-cell copies; **keep** the row + its 4 surviving test tokens (`test_build_slice_skill_dirty_tree_resolution.py`, `test_r_20_retired.py`, `test_skill_parse_helpers.py`, `test_build_slice_skill_branch_state_preamble.py`).
  - **Row #107** (L116, slice-099): **rewrite the stale narrative** (per /critique-review note, the `seed_derived_dirs` / `test_worktree_paths` mentions in this row are narrative prose, not runnable command tokens — so this is a narrative reword, not a command-token drop) — remove the "primary create path seeds via `seed_derived_dirs`" claim, the "legacy point-4 guarded cp -r count is 2" claim, and the matching regression clauses ("OR the build-slice primary create path stops seeding…", "OR the legacy-point-4 guarded cp -r count drifts from 2"); replace with post-removal reality (no derived-dir copy on any path; graphify regenerated on demand). Keep `BRANCH-3`/`ADR-090`/`R-31`/`pick`/`AC5`/`Pick log` intact (`test_v_0_81_0_branch_3_shippability_consumer_propagation` asserts those survive).
  - **Catalog row #53** (file-line L63, `test_bcr_1_backlog_round_trip`; per /critique-review note this is catalog row **#53**, NOT "#63" — #63 is the unrelated slice-063/NAW-1 occupant): narrow its command/narrative to the consume-side tests (#1–#3) that survive.
  - **NEW Row #105** (slice-105): add a catalog row (paired with the M4 entry-pin below) citing `ADR-094`/`ADR-095`/`R-20`/`consume-only` with a runnable command — the slice's own critical path must be catalogued (RPCD-1/SCPD-1).
  - **Build-sequencing (per /critique M2 + /critique-review M-add-1)**: each prose-edit ↔ test-removal pair MUST land in ONE atomic edit batch — an intermediate half-edited state reds the suite. **Three pairs**: (i) `build-slice/SKILL.md` point-2 `seed_derived_dirs` call + point-4 cp-r (`:96-97`) + point-1 note (`:67`) ↔ delete `test_build_slice_skill_cp_r_step.py` (`:52,113` assert `seed_derived_dirs in section` + `len(cp_r)==2`); (ii) `reflect/SKILL.md:59` round-trip bullet removal ↔ remove `test_bcr_1_backlog_round_trip.py` #4–#8 (they anchor on `**Addressed:**`/`SC-\d{3}`/`**Closes:** SC-` in that section) + the OSDG-1 reflect-mirror rides along; (iii) `_worktree_paths.py` `seed_derived_dirs` deletion (incl. the `:17` import in `test_worktree_paths.py`) ↔ remove the 3 seed tests ↔ delete `test_bcr_1_round_trip_end_to_end.py` ↔ the `test_resolve_slice_dir.py:66-88` guard removal (B-add-1).
- `methodology-changelog.md` (repo root) — new **v0.82.0** entry: "BCR-1 → consume-only (ADR-095); worktree derived-dir seed retired (ADR-094); R-20 fully closed."
- Version cascade (0.81.0 → **0.82.0**) — five distinct surfaces, each gated separately (per /critique m1): `VERSION` + `plugin.yaml` `version:` (**PMI-1**) + `pyproject.toml [project].version` (**PVFS-1**, `test_pyproject_version_matches_version_file`) + installed `~/.claude/ai-sdlc-VERSION` (**AVFS-1**) + installed `~/.claude/methodology-changelog.md` incl. the `## v0.82.0 — 2026-06-03` header (**MCFS-1**); the installed `ai-sdlc-tools` package version rides the AVFS-1/TVFS-1 forward-sync. Also: grep the OLD `0.81.0` literal + the prior versioned-test name repo-wide before finishing (AP-10 count-literal fan-out).
- `CLAUDE.md` (project) — BCR-1 paragraph in `## Self-hosting discipline` → consume-only wording.

## Wiring matrix

Per **WIRE-1**. This slice introduces no new code modules (it deletes a function + tests and edits prose). Zero-row matrix = clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-094]] — Retire the worktree derived-dir seed (`seed_derived_dirs` + cp-r); the slice loop no longer copies `diagnose-out/`/`graphify-out/` into worktrees; graphify regenerates on demand. **partial-supersedes [[ADR-090]]** (seed-step only — BRANCH-3's worktree-at-pick timing + path convention stay). Closes R-20. — reversibility: **cheap**
- [[ADR-095]] — Redefine BCR-1 as **consume-only**: retire the `/reflect` round-trip-write into `diagnose-out/backlog.md` (under BRANCH-3 it lands in the worktree's gitignored copy and is discarded at merge — a dead write). **partial-supersedes [[ADR-055]]** (round-trip half only — the `/slice` consume side stays). — reversibility: **cheap**

### SUP-1 partial-supersession handling (resolved per /critique B1)

ADR-055 and ADR-090 are each only *partially* superseded — their other halves (BCR-1 consume side; BRANCH-3 worktree-at-pick timing + path) remain **active**, so neither original gets `status: superseded` (the full-status-flip in `skills/reflect/SKILL.md:66-70` would wrongly retire still-live decisions). **The originals stay BYTE-UNMODIFIED — no `superseded-by` pointer, no body note.** The supersession is encoded ONLY at each successor's `supersedes:` frontmatter slot (ADR-094 → ADR-090; ADR-095 → ADR-055) plus an explicit **"partial — &lt;which half&gt;"** scope line in the successor's body. This is the test-pinned ADR-family convention: `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py::test_adr_019_unmodified_per_append_only_rule` codifies that supersession is **never** reverse-linked from the superseded ADR — and the live precedent confirms it (ADR-019, twice partial-superseded by ADR-020+ADR-063, carries no `superseded-by`; ADR-063, partial-superseded by ADR-090, was left unmodified). Adding a pointer-note would itself violate append-only. **Resolution of the earlier "highest-judgement call": do nothing to the originals.**

## Authorization model for this slice

N/A — methodology/tooling slice, no runtime auth surface.

## Error model for this slice

- `/reflect` graceful-degrade: with the seed gone, a future `**Closes:** SC-NNN` slice running `/reflect` in a seedless worktree must **no-op cleanly** on an absent `backlog.md`. Since ADR-095 removes the round-trip-write entirely, there is no longer any code path that touches `backlog.md` at `/reflect` — so the "absent file" branch is moot. Verify no residual reference remains.
- No new error codes.

## Scope honesty (carried from /slice)

This is the user's chosen **combined** cut (seed removal + round-trip retirement) over the recommended α/β split. Surface count is high (1 helper + 3 OSDG-1 SKILL.md + 4 test files + R-20 + shippability + changelog + version cascade + CLAUDE.md + 2 ADRs). It is **at/over the 1-day ceiling**. The seam remains clean: if `/build-slice` plan-mode reveals >1 day, split α (seed) from β (round-trip) at that point. `/critique` should weigh in on whether to split now.
