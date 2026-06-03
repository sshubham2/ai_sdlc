---
id: ADR-094
title: Retire the worktree derived-dir seed; the slice loop no longer copies diagnose-out/ or graphify-out/ into worktrees
date: 2026-06-03
slice: slice-105-decouple-slice-loop-from-diagnose-out
reversibility: cheap
status: accepted
supersedes: ADR-090
---

# ADR-094: Retire the worktree derived-dir seed (partial-supersede of ADR-090's seed-step)

## Context

BRANCH-3 ([[ADR-090]], slice-099) created the slice worktree at `/slice` pick-time and, as one of its setup steps, **seeded** the gitignored derived dirs `diagnose-out/` + `graphify-out/` from the main tree into every fresh worktree (`tools/_worktree_paths.py::seed_derived_dirs`, a `shutil.copytree`; mirrored by the legacy `cp -r` bash in `skills/build-slice/SKILL.md`). The seed exists to satisfy R-20 — gitignored derived artifacts a worktree's test suite needs are absent until copied.

Measured on 2026-06-03 the seed copies **~7 MB into every worktree**, of which:
- `graphify-out/graph.json` (3.78 MB) is **fully regenerable** (`graphify code .`) and the copied snapshot is **stale** — it reflects main-tree code, not the slice's code, so a worktree reading it for blast-radius gets the pre-slice graph;
- a stray nested `diagnose-out/graphify-out/graph.json` (2.18 MB) is pure junk;
- only a small `diagnose-out/backlog.md` portion was non-regenerable — and its **sole** consumer was one self-hosting test (`tests/methodology/test_bcr_1_round_trip_end_to_end.py`) reading the **live, gitignored** file.

That test also fails on a fresh clone / CI (the gitignored file is absent there), making it non-portable. Independently, [[ADR-095]] (this slice) retires the `/reflect` round-trip-write that the test validated — so the test verifies inputs to a removed feature and is deleted by this slice, eliminating the last live-`diagnose-out/` read. With no consumer left, the seed has no reason to exist.

`graphify-out/` was never required: `tools/slice_queue_writer` already treats a missing graph as a non-fatal `WARN` → `UNKNOWN-NO-GRAPH` (`tests/methodology/test_slice_queue_output.py::test_missing_graph_emits_warn_and_unknown_flags`); the only other reader is a prose example in `build-slice/SKILL.md`, regenerable on demand.

## Options considered

1. **Keep the full seed** — pros: zero change; cons: ~7 MB stale/junk copied per worktree, fails fresh-clone/CI, perpetuates R-20.
2. **Seed only `diagnose-out/backlog.md`** (drop graphify-out + the 51-file tree) — pros: ~99% byte reduction, no test weakening; cons: keeps a seed mechanism + the live-file test-coupling + the fresh-clone fragility; still couples the slice-loop test suite to live diagnose output.
3. **Retire the seed entirely** (CHOSEN) — pros: zero derived data copied; worktree graphs become slice-accurate (regenerated, not stale); R-20 fully closed; the slice loop has no dependency on live `diagnose-out/`. Enabled by deleting the sole consumer test (made vestigial by [[ADR-095]]). Cons: a future skill that needs `graphify-out/` inside a worktree must regenerate it (`graphify code .`) — which is already the documented pattern in `CLAUDE.md` and is *more* correct than reading a stale copy.

## Decision

Adopt **Option 3**. Delete `seed_derived_dirs()` + `_DERIVED_DIRS` from `tools/_worktree_paths.py`; remove the seed call from `skills/slice/SKILL.md` Step 5.5 and the `seed_derived_dirs`/`cp -r` steps from `skills/build-slice/SKILL.md` `### Branch state`. No skill copies `diagnose-out/`/`graphify-out/` into a worktree. `graphify-out/` is regenerated on demand by whatever skill needs it; `diagnose-out/` is needed by no slice-loop surface (only `/slice-candidates` reads it, and it runs in the main tree). R-20 moves from `retired` (mitigated) to **fully closed** — the mechanism is gone, not codified.

This **partial-supersedes [[ADR-090]]**: only ADR-090's *seed-step* is retired. BRANCH-3's worktree-at-pick **timing** and the canonical sibling-dir **path convention** + branch naming are **unchanged and remain active**. `_worktree_paths.py` keeps `canonical_worktree_path` + `slice_branch_name` (the functions `branch_workflow_audit.py` imports); only the seed is removed.

## Consequences

- ~7 MB no longer copied into each worktree; worktree creation is faster and worktrees carry no stale/junk derived data.
- A worktree that needs the code graph regenerates it (slice-accurate) instead of reading a stale main-tree snapshot — a correctness improvement, not just a saving.
- `branch_workflow_audit.py` is unaffected (it imports path/branch helpers, not the seed — verified).
- `tests/methodology/test_worktree_paths.py` loses its 3 `seed_derived_dirs` tests; `tests/methodology/test_build_slice_skill_cp_r_step.py` is deleted (it pinned the removed cp-r prose); the shippability rows referencing them are removed (RPCD-1/SCPD-1).
- The mid-slice smoke gate proves *seedless parity*: with `diagnose-out/`/`graphify-out/` absent, the methodology suite stays green.
- ADR-090 stays **byte-unmodified** — no `superseded-by` field, no body note (per /critique B1: the ADR-family convention pinned by `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py::test_adr_019_unmodified_per_append_only_rule` reverse-links supersession NEVER from the superseded ADR; ADR-063 was likewise left untouched when ADR-090 superseded it). Its `status` stays `accepted` (its other halves — worktree-at-pick timing + path convention — remain live); the supersession is encoded ONLY here, in this ADR's `supersedes: ADR-090` frontmatter + the partial scope line above.

## Reversibility

**cheap** — re-adding `seed_derived_dirs` + the cp-r step is a ~20-line restoration if a future seed need reappears. No data is lost (the derived dirs still exist in the main tree; they are simply not copied).
