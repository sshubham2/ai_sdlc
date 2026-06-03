---
id: ADR-095
title: Redefine BCR-1 as consume-only — retire the /reflect round-trip-write into diagnose-out/backlog.md
date: 2026-06-03
slice: slice-105-decouple-slice-loop-from-diagnose-out
reversibility: cheap
status: accepted
supersedes: ADR-055
---

# ADR-095: Redefine BCR-1 as consume-only (partial-supersede of ADR-055's round-trip half)

## Context

BCR-1 ([[ADR-055]], slice-053) minted a two-direction "Backlog **Consume-and-Round-trip**" discipline on `diagnose-out/backlog.md`:
- **Consume** — `/slice` MUST consult `backlog.md` as a candidate source *when it exists* (absent → silent no-op).
- **Round-trip** — `/reflect` MUST write an in-place `- **Addressed:** slice-NNN on YYYY-MM-DD` line into each closed `SC-NNN` block when the slice carries a `**Closes:** SC-NNN` sentinel (`skills/reflect/SKILL.md:59`).

Under BRANCH-3 ([[ADR-090]]), `/reflect` runs in the slice **worktree**, where `diagnose-out/` is gitignored. The round-trip-write therefore lands in the worktree's gitignored copy, which is **discarded at `/commit-slice --merge`** (only tracked files merge). The write never reaches the main-tree `backlog.md` — it is a **dead write**. (The main tree's `backlog.md` only ever carried SC-001's `**Addressed:**` line because slice-054 predated BRANCH-3 and wrote it in-place locally; the artifact is gitignored and machine-local, so the round-trip was never durably persisted through git.)

The round-trip was also the *sole* reason the slice-loop test suite read live diagnose output (via `test_bcr_1_round_trip_end_to_end.py`), which forced the ~7 MB worktree seed retired by [[ADR-094]]. Keeping a dead write alive perpetuates that coupling for no benefit.

The **consume** side is different: it is soft (when-present), legitimate (a backlog of owner-confirmed candidates is exactly what `/slice` wants as one ranked source), and reads in the **main tree** at `/slice` time — no worktree, no seed. It stays.

## Options considered

1. **Keep BCR-1 round-trip as-is** — pros: no change; cons: the write is dead under BRANCH-3 (lost at merge), and it keeps the slice loop coupled to diagnose output.
2. **Fix the round-trip to persist** (e.g., write to the main-tree backlog from the worktree, or commit `diagnose-out/`) — pros: makes the round-trip real; cons: re-introduces a slice-loop → diagnose-output write coupling, fights the derived-not-tracked principle (R-20 §(c)) and the external-vault flip direction; large surface for a low-value feature.
3. **Retire the round-trip; BCR-1 becomes consume-only** (CHOSEN) — pros: removes a dead write; fully decouples the slice loop from `diagnose-out/` (no read of the live file, no write to it); enables [[ADR-094]]'s seed removal; `/slice-candidates` remains the single owner of diagnose output. Cons: closing an `SC-NNN` is no longer auto-recorded back into `backlog.md` — but it never was, durably (the write was lost at merge), so no real capability is lost. Owners track closure via the slice archive / git history.

## Decision

Adopt **Option 3**. Remove the `/reflect` round-trip-write step (`skills/reflect/SKILL.md:59`). BCR-1 is redefined as **consume-only**: `/slice` still consults `backlog.md` when present (source #7, unchanged). The `**Closes:** SC-NNN` sentinel is demoted to **inert documentation** (a human-readable "this slice closes SC-NNN" marker with no automation consumer); it is no longer a round-trip trigger. The reflect-side BCR-1 anchor tests (`tests/methodology/test_bcr_1_backlog_round_trip.py` #4–#8) and the input-contract end-to-end test (`tests/methodology/test_bcr_1_round_trip_end_to_end.py`) are removed; the consume-side tests (#1–#3) are retained. `CLAUDE.md`'s BCR-1 paragraph + `architecture/shippability.md` rows + `methodology-changelog.md` (v0.82.0) are updated.

This **partial-supersedes [[ADR-055]]**: only the round-trip half is retired. The consume half remains active. ADR-055 stays **byte-unmodified** — no `superseded-by` field, no body note (per /critique B1: supersession is reverse-linked NEVER from the superseded ADR, pinned by `tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py::test_adr_019_unmodified_per_append_only_rule`); its `status` stays `accepted`. The supersession is encoded ONLY in this ADR's `supersedes: ADR-055` frontmatter + the partial scope line above.

## Consequences

- The slice loop neither reads (live) nor writes `diagnose-out/` — combined with [[ADR-094]] this fully closes the loop ↔ diagnose-output coupling. `/slice-candidates` is the sole reader/producer of `diagnose-out/`.
- `/reflect` has no code path touching `backlog.md`; the "absent backlog" graceful-degrade branch becomes moot (nothing to degrade).
- BCR-1's name in `CLAUDE.md` shifts from "Consume-and-Round-trip" to "Consume" discipline; the rule's test surface shrinks to the consume-side anchors.
- A future need to record SC-closure durably would be designed as a main-tree-targeted action (a new decision), not resurrected as a worktree-local write.

## Reversibility

**cheap** — the round-trip-write is a single prose bullet; restoring it (plus its anchor tests) is a small change. No data migration. The historical SC-001 dogfood remains recorded in slice-054's archived reflection regardless.
