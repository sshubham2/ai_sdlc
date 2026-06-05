# Reflection: Slice 114 convert-agent-prose-to-vault-seam

**Date**: 2026-06-05
**Shipped**: YES

## Validated
- The ADR-105 **value-keyed** carve-out design survives line-shifts — confirmed: inserting the 3-line seam note shifted `code-review.md`'s carve-outs `:25→:29` / `:233→:237`, yet `_CONVERTED_CARVEOUTS` (keyed on `sha256(value)`) + `_BASELINE_SHA256` (multiset hash) held; `--strict` green.
- `agents/code-review.md` is **safely ratchetable** despite the skill `code-review/SKILL.md` not being — its 2 carve-out values are distinct from each other AND from the 2 converted refs (which lose `architecture/` entirely), so no exploitable value-collision. Confirmed by `--strict` exit 0 + the code-Critic's independent hash computation.
- The 127/4/131 arithmetic + the two carve-out hashes (`0a69ee77…`, `46e2f7eb…`) — APED-1-confirmed against the live corpus at design, build, AND code-review (three independent executions).
- M1 non-vacuity: both drift tests RED pre-sync → GREEN post-sync (AP-5 — the new `test_critic_calibrate_agent_drift.py` is provably non-vacuous).

## Corrected
- None. No design claim was refuted. The scope refinement (4 files → 2 convertible) was a *sharpening* surfaced at `/design-slice` and back-propagated to the mission brief in the same fix block (AP-17), not a post-build correction.

## Discovered
- **The agent-prose surface had FEWER convertibles than the gross ref-count implied** — only 2 of 4 files (3 of 7 refs) carried genuinely-convertible refs; the other 4 refs were ADR-105-mandated-concrete carve-outs (classes 5/7). slice-113's reflection said "4 files carry convertible refs" — imprecise. Lesson: classify per-occurrence via `vault_flip_prose_inventory --json`, never estimate from a file count.
- **Converting one reference to an artifact makes every OTHER bare/inconsistent reference to that same artifact in the file newly salient** (the code-Critic's m1: `critic-calibrate.md:80`'s bare `critic-calibration-log.md` became a self-sufficiency wart once `:22` became `<vault>/…`). A conversion raises the intra-file consistency bar — the next converter should grep the whole file for sibling references to the just-converted artifact.

## Deferred
- The 2 no-op agent files (`critique-review.md:78` active-folder class 5; `diagnose-narrator.md:19` diagnose-out class 7) + their carve-outs — lands in: the **flip slice** (`flip-vault-to-external-store`), which drains classes 4-7 + the physical move (per R-32).
- The root `CLAUDE.md` CAD-1 prose-enumeration sweep (enumerate `critique` + `code-review` + `critic-calibrate`) — lands in: a separate **courtesy-parity cleanup** (m-add-1; slice-096 precedent). The drift *tests* are the authoritative guarded-set meanwhile.
- The 2 descriptive bare `critic-calibration-log.md` mentions (`critic-calibrate.md:109` template label, `:154` effectiveness-section description) — left as-is (output-format descriptions, not path-resolution instructions). Optional future polish.

## Critic calibration

Scored against `critique.md` `## Triage` (all 7 ACCEPTED) + reality during build/code-review:

- **M1** (no drift guard on critic-calibrate.md): **VALIDATED** — ACCEPTED-PENDING; the gap was real (only 2 agent drift tests existed on disk); the new `test_critic_calibrate_agent_drift.py` now guards it, non-vacuity proven (RED→GREEN).
- **M2** (code-review.md:25 mislabel "class 1-pathspec"): **VALIDATED** — ACCEPTED-FIXED; the live classifier reports `operational-reference` (NOT git-pathspec — `_PATHSPEC_RE` line-local), exactly as flagged; code-Critic re-confirmed.
- **M3** (2 carve-outs MUST be hash-added or `--strict` exits 2): **VALIDATED** — ACCEPTED-FIXED; both required; `--strict` exit 0 only after both `_carveout_key` entries added; code-Critic verified the hashes.
- **m1** (DOC_EXAMPLE floor stays 0): **VALIDATED** — ACCEPTED-FIXED; floor left at 0, drift covered by baseline+ratchet (confirmed by the m1-fix re-run leaving counts identical).
- **m2** (stale "rows 113/117"): **VALIDATED** — ACCEPTED-FIXED; the live sites were `vault_flip_prose_inventory.py` (8) + `shippability.md` rows 122/126/127/128 — exactly what got re-pinned.
- **m3** (mission-brief row 3 hardcodes 127/4/131): **VALIDATED** — ACCEPTED-FIXED; numbers correct, annotated derived/APED-1.
- **m-add-1** (meta-Critic: CLAUDE.md CAD-1 enumeration loose end): **VALIDATED** — ACCEPTED-FIXED; recorded as a deliberate courtesy-parity deferral.

**Missed by Critic**: the design-Critic + meta-Critic both MISSED `critic-calibrate.md:80`'s bare-reference inconsistency (the code-Critic's m1) — structurally unreachable by the design stack, which reviews the design/mission-brief prose, NOT the post-conversion *file*. The code-Critic caught it by reading the actual converted file. This is the 3-Critic complementarity working as designed (AP-19), not a design-Critic failure.

**Pattern**: clean defect-class partition across the 3-Critic stack (N≥15) — design-Critic → design-prose completeness/label gaps (M1/M2/M3); meta-Critic → on-disk roster/enumeration loose ends (m-add-1); code-Critic → intra-file post-conversion consistency only a real file-read reveals (:80). EXECUTION (APED-1) confirmed every numeric claim. No FALSE-ALARM, no OVERRIDE-MISJUDGED this slice.

## Lessons for next slice
- Per-occurrence classification via the inventory `--json`, never a file-count estimate (the "4 files" imprecision).
- On any seam conversion: grep the whole file for sibling references to the just-converted artifact — converting one ref raises the intra-file consistency bar (the :80 lesson).
- The flip slice (`flip-vault-to-external-store`) now owns the LAST prose residual surface (classes 4-7 carve-outs across skills+agents) + the physical move — R-32's sole remaining pre-retirement work.

## Vault updates made (thin vault — small list)
- This slice's artifacts (mission-brief / design / critique / critique-review / build-log / validation / reflection) — written in the worktree.
- [[risk-register.md]] — R-32 slice-114 paragraph (agent-prose leg drained; physical move = sole residual) — appended **during build** (AC5), status stays `mitigating`.
- `tools/vault_flip_prose_inventory.py` — `_CONVERTED_FILES` +2 agents, `_CONVERTED_CARVEOUTS` +2, floor 127, EXPECTED_TOTAL 131, `_BASELINE_SHA256`, docstrings.
- [[shippability.md]] — rows 122/126/127/128 live-count fan-out + new row 120 (added during build).
- `agents/code-review.md` + `agents/critic-calibrate.md` converted + forward-synced; NEW `tests/methodology/test_critic_calibrate_agent_drift.py`.
- **No new ADR / RULE-ID / VERSION bump — MEPD-1 EXCLUDE** (ADR-105 rollout within documented scope; slice-096 test-only-guard-add precedent for the new drift test).
