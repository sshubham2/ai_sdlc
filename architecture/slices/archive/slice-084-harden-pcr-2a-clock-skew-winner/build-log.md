# Build log: Slice 084 harden-pcr-2a-clock-skew-winner

**Date**: 2026-05-30
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-05-30 BUILD: worktree created at ../ai_sdlc-wt/slice-084-... on branch slice/084-harden-pcr-2a-clock-skew-winner (point-4 switch-commit-switch; scaffold commit dd41e63)
- 2026-05-30 TEST: wrote tests/methodology/test_pcr_2a_clock_skew_winner.py (12 TF rows) → WRITTEN-FAILING (ImportError, helpers absent) confirmed
- 2026-05-30 BUILD: added _CLOCK_SKEW_TOLERANCE_SECONDS=300, _winner_clock_skew_suspect, _append_skew_stop_audit; wired Step 2.5 into resolve_vault_claim_conflict (now param); comment touch-up in the _format_vault_claim_audit_entry docstring (Claim-seq forward-ref → resolver-now guard)
- 2026-05-30 TEST: new suite 20 passed (12 functions; battery expands to 20 items)
- 2026-05-30 SMOKE: PCR regression suite 91 passed, 0 failures (existing PCR-2a/2b/1 callers pass — no `now` → real-now default; their 2026-05-29 stamps are past → guard returns None)
- 2026-05-30 TEST: full suite 1213 passed (was 1193 @ slice-083; +20)
- 2026-05-30 BUILD: appended shippability.md row 90 (pipe-free, 7 pipes; CRLF preserved)

## Summary

### Plan executed
1. Add `_CLOCK_SKEW_TOLERANCE_SECONDS = 300` — DONE
2. Write 12 TF tests first → WRITTEN-FAILING — DONE
3. `_winner_clock_skew_suspect(winner, now, tolerance_seconds)` (Z-normalize / unparseable→STOP / tz-naive→STOP / future-dated→suspicious / else None) — DONE
4. `_append_skew_stop_audit(...)` (clock-skew STOP audit section, both claims + now.isoformat()) — DONE
5. Wire Step 2.5 into `resolve_vault_claim_conflict` (+`now` param, default real UTC) — DONE
6. Comment touch-up in the `_format_vault_claim_audit_entry` docstring (Claim-seq forward-ref → resolver-now guard) — DONE
7. Full suite + Step 6 audits — DONE (see gates)

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `pytest tests/methodology/ -k "pcr_2a or pcr_2b or pcr_1 or parallel_conflict"` → 91 passed, 0 failed. New suite 20 passed. No regression to existing PCR resolution callers.

### Pre-finish gate
- [x] All ACs pass with evidence — TF-1 12/12 PASSING; see validation.md (pending /validate-slice)
- [x] Must-not-defer addressed — fail-closed STOP (suspicious/naive/unparseable); both claims + resolver-now logged; happy-path strict-newer preserved (guard returns None on past stamps); cooperative threat model unchanged; no commit-slice prose change (SKILL.md:190 VAULT_CLAIM→SOAD-1 fall-through)
- [x] Drift-check — run full mode (see Events / drift-log marker)
- [x] Smoke regression check pass
- [x] No new TODOs / FIXMEs / debug prints
- [x] Mock-budget lint (LINT-MOCK-1) — clean (test file)
- [x] WIRE-1 — clean
- [x] BC-1 — see BC-1 attestations below; --strict --ack-critical exit 0
- [x] TF-1 — clean (12 PASSING)
- [x] BRANCH-2 — on slice/084-harden-pcr-2a-clock-skew-winner (matches)
- [x] UTF8-STDOUT-1 — clean (33 tools; no new main())
- [x] CRP-1 — clean (critique-review.md present)
- [x] PCA-1 — clean (9 skills; chain matches)
- [x] BCI-1 — PASS
- [x] MCFS-1 / AVFS-1 / TVFS-1 — PASS (no VERSION bump this slice; forward-sync intact)
- [x] STP-1 — clean
- [x] NAW-1 — clean (zero new agents/*.md)
- [x] DCE-1 — drift-log marker present

### BC-1 attestations (Critical rules applicable: BC-PROJ-3, BC-PROJ-7, BC-GLOBAL-2)
- **BC-PROJ-3 + BC-GLOBAL-2** (no destructive `git checkout`/`restore`/`stash` revert of uncommitted work): this slice performs NO destructive git revert. The only git mutations were `git switch -c slice/084-...`, `git add` + `git commit` (scaffolding committed, not discarded), `git switch master`, and `git worktree add`. No `git checkout -- <file>`, no `git restore`, no `git stash`. Uncommitted work was committed to the slice branch, never reverted.
- **BC-PROJ-7** (new audit-tool slices wire cp1252 coverage + author a pipe-free shippability row): substance N/A — this slice adds NO new `tools/<name>.py` module with `main()`; it MODIFIES the existing `tools/parallel_conflict_resolver.py`. The cp1252 coverage-list obligation does not apply (no new main()-bearing tool → UTF8-STDOUT-1 audit clean at 33/33). The pipe-free shippability-row obligation IS discharged anyway (catalog-completeness, slice-082 precedent): row 90 appended with exactly 7 unescaped pipes, no raw pipe in any cell; SRSC-1 runner confirms (see validation.md).

### Deferrals
None.

### Design deviations
None — built exactly to design.md / ADR-076 (post-/critique-fix version).

### Files changed
- `tools/parallel_conflict_resolver.py` — +`_CLOCK_SKEW_TOLERANCE_SECONDS`, +`_winner_clock_skew_suspect`, +`_append_skew_stop_audit`, Step 2.5 wiring + `now` param in `resolve_vault_claim_conflict`, `_format_vault_claim_audit_entry` docstring comment touch-up. Post-/code-review fixes: M1 case-insensitive `Z`/`z`; M2 docstring scope-correction; m1 dropped dead `diag` param from `_append_skew_stop_audit`
- `tests/methodology/test_pcr_2a_clock_skew_winner.py` — new (12 functions / 20 items)
- `architecture/shippability.md` — +row 90
- (scaffolding: mission-brief.md, design.md, ADR-076, critique.md, critique-review.md, milestone.md, slice-queue.md)
