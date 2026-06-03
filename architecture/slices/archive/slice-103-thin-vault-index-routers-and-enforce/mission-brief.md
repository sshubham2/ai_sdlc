# Slice 103: thin-vault-index-routers-and-enforce

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: an unregistered structural-drift class — the "thin router" contract that `skills/archive/SKILL.md` asserts in prose (L113 "one-line summary, trimmed to one line"; L115/L120 "~10 from recent reflections") is enforced by *nothing*, so the two hot index routers silently re-bloat on every `/reflect`→`/archive` regeneration. Register the new risk at `/reflect`.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The vault's two hot index routers have drifted from thin lookup tables into fat inline stores: `architecture/slices/_index.md` is 319.5 KB (recent-10 rows are 1,250–2,265-char paragraphs; "Aggregated lessons" is a 631-line all-history log of ~95 slices) and `architecture/slices/archive/_index.md` is 414.1 KB (avg 3,925 chars/line, longest 13,720). Both are read on every `/slice`, `/critique`, and `/design-slice` run (per `skills/archive/SKILL.md:185-187`), so the bloat is pure hot-path context waste — and both regions merely duplicate content that already lives durably elsewhere (per-slice `mission-brief.md`/`reflection.md` in each archive folder; the all-history lessons in `architecture/lessons-learned.md`). This slice makes both files true thin routers (one-liner + folder pointer), replaces the all-history lessons dump with a bounded synthesized cross-slice action-points register that preserves the pattern-recognition job better than 95 verbose summaries did, and — the piece whose absence caused the drift — adds an audit that fails on re-bloat plus a `skills/archive/SKILL.md` spec fix so future regenerations stay thin.

## Acceptance criteria

1. `architecture/slices/_index.md` "Most recent 10" is a thin table of **exactly the 10 most recent** rows, each a single line — `| NNN | [name](archive/slice-NNN-name/) | shipped | one-line intent |` — with the one-line intent derived from that slice's `mission-brief.md` Intent and bounded by a per-row character cap (≤500) the audit enforces. No row exceeds the cap; the audit also rejects >10 recent-10 rows.
2. The all-history "Aggregated lessons" region of `architecture/slices/_index.md` is replaced by a synthesized cross-slice action-points register of ≤25 entries in a **standalone `architecture/slices/action-points.md`** (B1 — linked from `_index.md`, so the regen path can't clobber it), each tagged with exactly one promotion verdict ∈ {`already-a-gate`, `build-check-candidate`, `critic-calibrate-probe`, `cultural`}; the full per-slice lesson history is verified to remain intact in `architecture/lessons-learned.md` via a programmatic orphan-diff (M2 — no aggregated bullet exists only in `_index.md` at cut time; orphans ported before cutting).
3. `architecture/slices/archive/_index.md` is a thin chronological catalog: each row is a single line ≤ the per-row cap (one-liner + `slice-NNN-name/` folder pointer); the file shrinks from 414 KB to a thin router.
4. A new audit `tools/index_router_thinness_audit.py` + paired test pins the thinness invariants (per-row char cap ≤500 on both index tables; recent-10 ≤10 rows; `action-points.md` register entry-count ≤25 and every entry carries exactly one valid verdict tag; total-size backstops), fails non-zero on re-bloat (proven non-vacuous by a mutation), and is **added as an `architecture/shippability.md` regression-catalog row run at `/validate-slice` pre-finish** (RPCD-1/SCPD-1) + enumerated in `plugin.yaml` + `install_audit._CANONICAL_TOOLS` (M1 — shippability-only, NOT a Step-6 `####` gate-roster entry; MEPD-1 EXCLUDE, no VERSION bump). The new tool itself passes `vault_flip_readiness_audit --strict` (M5).
5. The regeneration/consumer spec is updated end-to-end: **writer** skills `skills/archive/SKILL.md` (Step 3/4) + `skills/reflect/SKILL.md` (Step 6 regen) emit the thin one-liner-row form (retaining their `vault_edit rewrite` SVW-1 routing — M4); **reader** skills `skills/slice/SKILL.md` + `skills/critique/SKILL.md` (incl. its Critic-input template) + `skills/pulse/SKILL.md` are repointed at `action-points.md` (M-add-1); OSDG-1-guarded `reflect` + `critique` installed copies forward-synced.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Thin recent-10 | Run the new audit on `_index.md` → exit 0; assert every "Most recent 10" data row is one physical line ≤ cap; `(Get-Item _index.md).Length` is a small fraction of the 319.5 KB baseline |
| 2 | Action-points register | Count register entries ≤ 25; every entry matches the closed verdict-tag enum; confirm `architecture/lessons-learned.md` line count is unchanged (all-history preserved there) and no register-only orphan lesson exists |
| 3 | Thin archive catalog | Run the audit on `archive/_index.md` → exit 0; longest line ≤ cap; file size shrunk from 414 KB |
| 4 | Enforcement is real | `pytest` the new test PASSES; run the audit against a deliberately re-bloated fixture → exits non-zero (mutation non-vacuity); the audit appears in the Step-6 gate roster and a shippability row cites it |
| 5 | Spec fix | Diff `skills/archive/SKILL.md` Step 3/Step 4 templates show the one-liner-row + bounded-register output shape; forward-sync to the installed `~/.claude/skills/archive/SKILL.md` (or a documented deferral) |

## Must-not-defer

- [ ] **No data loss before cutting**: verify every lesson currently in `_index.md` "Aggregated lessons" is already captured in `architecture/lessons-learned.md` — the all-history dump must not be the sole copy of anything before it's replaced.
- [ ] **Faithful synthesis, not fabrication**: the action-points register is derived from real reflections' lessons (the pattern-recognition input `/slice`+`/critique` rely on must survive the cut), not invented.
- [ ] **Audit wired, not orphaned**: the new audit is added to the slice-finish gate roster AND propagates a consumer reference into `architecture/shippability.md` (RPCD-1/SCPD-1) — never a standalone script.
- [ ] **Region-anchored scan, not whole-file token scan**: the audit's char-cap check parses the table region structurally — it must not false-positive on legitimate markdown structure (heeds the slice-099/100 "a marker/token detector must be region-anchored, not `marker in line_text`" lesson, N=4).
- [ ] **Non-vacuity by mutation**: the thinness test is proven non-vacuous by a deliberate re-bloat mutation (a passing test on already-thin files proves nothing).

## Out of scope

- Thinning the cold append-only ledgers — `methodology-changelog.md`, `architecture/risk-register.md`, `architecture/shippability.md`, `architecture/critic-calibration-log.md`, `architecture/drift-log.md`, `architecture/build-checks.md`, `architecture/lessons-learned.md`. They are audit trails; thinning them is a separate, riskier question (`/reduce`: "historical record is valuable").
- Changing the COST-1 Haiku-dispatch regeneration *mechanism* in `/archive` — only the output spec/templates change.
- A general vault-wide "max file size" audit — this slice pins only the two hot routers + the register bound, not every file.
- The action-points register *maintenance/regeneration policy* (curated-vs-auto-regenerated, and who refreshes it on a new promotion) — a `/design-slice` decision, not pre-decided here.
- Adding an OSDG-1 skill-drift test for `skills/archive/SKILL.md` (archive is not currently in the OSDG-1 guarded set) — out of scope unless design chooses to add it.

## Dependencies

- Vault refs: [[skills/archive/SKILL.md]] (the regeneration spec being fixed), [[architecture/lessons-learned.md]] (the durable all-history store that must remain the sole home of full lesson history), [[architecture/slices/_index.md]] + [[architecture/slices/archive/_index.md]] (the two routers being thinned).
- Methodology: RPCD-1/SCPD-1 (new audit → shippability consumer refs), COST-1 (the `/archive` Haiku-dispatch regeneration the spec fix targets).
- Risk register: no existing R-NN covers index-router bloat — this retires an unregistered structural-drift class; register a new risk at `/reflect`.

## Mid-slice smoke gate

At ~50% of build (after the new audit exists and `_index.md` recent-10 has been thinned), run:
```
$PY = "$env:USERPROFILE\.claude\.venv\Scripts\python.exe"
& $PY -m tools.<new_audit>            # against the real (now-thinned) _index.md → exit 0
& $PY -m tools.<new_audit> <bloated-fixture>   # → exits non-zero
```
Expected: clean on the thinned router, non-zero on a re-bloated fixture. If the audit can't distinguish thin from bloated, STOP — the enforcement piece (the whole point of the slice) is broken.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
