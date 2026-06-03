# Slice 105: decouple-slice-loop-from-diagnose-out

**Mode**: Standard
**Estimated work**: 1 day (user chose the combined cut over an α/β split; scope is at the ceiling — `/design-slice` enforces the ≤5-AC / shippability limits and may still recommend a split if the build exceeds 1 day)
**Risk retired**: R-20 (fully closed — gitignored derived-dir worktree seed); plus the latent BCR-1 fragilities surfaced below
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The AI SDLC slice loop has one hard dependency on diagnose output: `tests/methodology/test_bcr_1_round_trip_end_to_end.py` reads the **live, gitignored** `diagnose-out/backlog.md` as a self-hosting dogfood fixture. Because that test runs in every slice worktree's smoke + pre-finish suite, it forces a ~7 MB `seed_derived_dirs` copy of `diagnose-out/` + `graphify-out/` into every worktree (the R-20 "cp-r tax") — and the test silently *fails on a fresh clone / CI* where the gitignored file is absent. BCR-1 also has a `/reflect` round-trip-**write** (`**Addressed:** slice-NNN` into `backlog.md`) that, under BRANCH-3, lands in the worktree's gitignored copy and is discarded at merge — a near-dead write.

This slice **fully decouples the slice loop from `diagnose-out/` in both directions**: (1) pin the dogfood test to a checked-in fixture and delete the seed mechanism (closing R-20); (2) retire BCR-1's `/reflect` round-trip-write, redefining BCR-1 as **consume-only** via a new ADR superseding ADR-055's round-trip half. After this, `/slice-candidates` remains the *sole* reader/consumer of diagnose output; the slice loop neither reads (live) nor writes `diagnose-out/`. The `/slice` consume-side consultation (source #7, "when present") is the one legitimate soft coupling and is explicitly **retained**.

## Acceptance criteria

1. `tests/methodology/test_bcr_1_round_trip_end_to_end.py` is **deleted** (it verifies inputs to the `/reflect` round-trip retired by ADR-095 — see design.md "Design refinement"); the full methodology suite passes with **no `diagnose-out/` present** (fresh-clone / seedless-worktree parity).
2. `seed_derived_dirs` + `_DERIVED_DIRS` are removed from `tools/_worktree_paths.py`, and **no skill seeds or `cp -r`s** `diagnose-out/`/`graphify-out/` into a worktree (`/slice` Step 5.5 seed step + `/build-slice` `### Branch state` cp-r/seed-call removed); R-20 marked **retired (fully closed)** in `risk-register.md`.
3. `/reflect` no longer writes the `**Addressed:**` round-trip line into `diagnose-out/backlog.md`; **BCR-1 is redefined consume-only** via a new ADR superseding ADR-055's round-trip half (+ `methodology-changelog.md` version entry + `CLAUDE.md` BCR-1 paragraph + `shippability.md` row updated per RPCD-1/SCPD-1).
4. The `/slice` consume-side BCR-1 behavior (consult `backlog.md` when present) is **unchanged** and its consume-side tests in `test_bcr_1_backlog_round_trip.py` still pass; the reflect-side round-trip anchor tests are removed/inverted; `test_worktree_paths.py` + `test_build_slice_skill_cp_r_step.py` seed/cp-r tests removed/inverted.
5. Full audit + drift suite green — including **OSDG-1 content-equality** for the three edited SKILL.md surfaces (`slice`, `build-slice`, `reflect`) against their installed copies — and the stray nested `diagnose-out/graphify-out/graph.json` is removed.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Test deleted + seedless-clean | `Grep` `test_bcr_1_round_trip_end_to_end.py` → file absent; with `diagnose-out/`+`graphify-out/` renamed aside, `& $PY -m pytest tests/methodology -q` → all PASS (no live diagnose-out read remains) |
| 2 | Seed mechanism gone | `Grep` for `seed_derived_dirs`/`_DERIVED_DIRS`/`cp -r .*diagnose-out` across `tools/` + `skills/` → only historical/ADR references remain; `& $PY -m pytest tests/methodology/test_worktree_paths.py` reflects removal; `risk-register.md` R-20 `**Status**: retired` with closure note |
| 3 | `/reflect` write retired + ADR | `Grep` `skills/reflect/SKILL.md` for the `**Addressed:**` write step → absent; new ADR file exists with `supersedes: ADR-055`; `& $PY -m tools.<changelog/version audits>` green |
| 4 | Consume side intact, reflect tests inverted | `& $PY -m pytest tests/methodology/test_bcr_1_backlog_round_trip.py` → consume-side tests PASS, reflect-side tests removed; `/slice` SKILL.md source-#7 anchor still present |
| 5 | Full suite + OSDG-1 drift green | `/validate-slice` (VAL-1+WS-1+ETC-1) + `& $PY -m tools.critique_agent_drift_audit` + the slice/build-slice/reflect drift tests all PASS |

## Must-not-defer

- [ ] **OSDG-1 mirror**: every in-repo `skills/{slice,build-slice,reflect}/SKILL.md` edit is content-equal (modulo EOL) to its installed `~/.claude/skills/.../SKILL.md` copy — update BOTH.
- [ ] **SUP-1**: new ADR is append-only and carries `supersedes: ADR-055` (round-trip half) + notes the ADR-090 seed-step retirement; never edit ADR-055/ADR-090 in place.
- [ ] **Graceful-degrade**: `/reflect` on a future `**Closes:** SC-NNN` slice in a seedless worktree must no-op cleanly on an absent `backlog.md` (no crash) — verify, since the seed that used to guarantee presence is gone.
- [ ] **Consume side preserved**: `/slice` must still consult `backlog.md` when present (source #7) — do NOT remove the consume-side BCR-1 wiring.
- [ ] **PMI-1 / INST-1**: if `tools/_worktree_paths.py`'s public surface changes, re-run plugin-manifest + install audits.
- [ ] **Reverse-dependency completeness (per /critique-review B-add-1 / M-add-2)**: deleting `test_bcr_1_round_trip_end_to_end.py` reds `test_resolve_slice_dir.py:77` (an `.is_file()` guard on that path) — delete/invert that guard in the SAME batch; deleting `seed_derived_dirs` reds `test_worktree_paths.py:17` (its import) — drop that import too. Run the FULL methodology suite, never just the touched files — every miss this slice's reviews found was a "what else requires this deleted artifact to exist" reverse-reader.

## Out of scope

- Removing `/slice`'s consume-side backlog consultation (source #7) — that soft "when-present" coupling is legitimate and stays.
- Any change to `/diagnose` or `/slice-candidates` — they remain the producers/consumers of `diagnose-out/`.
- Changing how skills invoke graphify (regenerate-on-demand is the existing, retained pattern; graphify-out simply stops being seeded).
- Un-gitignoring `diagnose-out/` or `graphify-out/` (R-20 fix-class (c) — explicitly rejected; derived-not-tracked is correct).

## Dependencies

- Prior slices: [[slice-099-create-worktree-at-slice-pick]] (introduced the pick-time seed; [[ADR-090]]), [[slice-054]]/[[slice-053]] (BCR-1 dogfood; [[ADR-055]]), [[slice-074-codify-cp-r-in-branch-2-skill]] (codified the cp-r step)
- Vault refs: [[decisions/ADR-055]] (BCR-1), [[decisions/ADR-090]] (BRANCH-3 seed step), [[risk-register#R-20]]
- Files: `tools/_worktree_paths.py`, `skills/slice/SKILL.md`, `skills/build-slice/SKILL.md`, `skills/reflect/SKILL.md`, `tests/methodology/test_bcr_1_round_trip_end_to_end.py`, `tests/methodology/test_bcr_1_backlog_round_trip.py`, `tests/methodology/test_worktree_paths.py`, `tests/methodology/test_build_slice_skill_cp_r_step.py`

## Mid-slice smoke gate

At ~50% of build (after the end-to-end test is deleted + the seed mechanism removed, before the `/reflect` round-trip retirement):
```
# In the worktree, prove seedless parity:
Rename-Item diagnose-out diagnose-out.bak ; Rename-Item graphify-out graphify-out.bak
& $PY -m pytest tests/methodology -q
Rename-Item diagnose-out.bak diagnose-out ; Rename-Item graphify-out.bak graphify-out
```
Expected: methodology suite **green with no `diagnose-out/`/`graphify-out/` present**. If it fails: a hidden second consumer of the seed exists (a different latent reader of the live derived dirs — per /critique m2) — STOP, find it, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. OSDG-1 mirror on 3 SKILL.md + SUP-1 ADR)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (seedless parity holds)
- [ ] No new TODOs / FIXMEs / debug prints
