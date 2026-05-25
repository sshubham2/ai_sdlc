# Build log: Slice 036 fix-rr1-audit-status-filter

**Date**: 2026-05-17
**Result**: SHIPPED

## Events (append-only — written DURING build per Step 7c)

- 2026-05-17 02:10 BUILD: slice branch slice/036-fix-rr1-audit-status-filter created from master (carried slice-036 repro change, user-confirmed BRANCH-1)
- 2026-05-17 02:12 BUILD: tools/risk_register_audit.py main() JSON branch — out["view"] replaced by out["risks"]=filter_and_sort view; view key dropped
- 2026-05-17 02:13 TEST: AC1 repro test_repro_r9_..._consumed_risks PASS (was WRITTEN-FAILING)
- 2026-05-17 02:14 SMOKE: mid-slice — real register --json --filter-status open → out["risks"] only status:open (R-9,R-2,R-6,R-8); view key absent. PASS
- 2026-05-17 02:15 FINDING: plan-mode design-vs-reality — Critic-stack-proposed oracle `--filter-band high == {R1,R3}` is WRONG; R3 score=low×high=3=medium band. Corrected mission-brief oracle to {R1}; --top 2 --sort score → [R1,R2]
- 2026-05-17 02:18 TEST: 5 new tests written (AC2 x2, AC4 x3) in tests/methodology/test_risk_register_audit.py
- 2026-05-17 02:19 TEST: full module pytest tests/methodology/test_risk_register_audit.py → 30 passed (24 existing + 6 new; no regression)
- 2026-05-17 02:20 BUILD: TF-1 plan all 6 rows → PASSING
- 2026-05-17 02:24 FINDING: TF-1 --strict-pre-finish refused `ac-without-row` on AC3 — the "no-regression gate not a TF-1 row, survives strict TF-1" carve-out (first-Critic m2 + meta-Critic blessed) was WRONG. BC-PROJ-4-class catch (audit-on-real-artifact refutes Critic-stack reasoning). Fixed: AC3 → row mapping existing `test_filter_status_open_excludes_retired` (the concrete no-regression sentinel); carve-out claim corrected in brief
- 2026-05-17 02:25 TEST: TF-1 re-run → clean, 7 rows PASSING
- 2026-05-17 02:26 BUILD: Step6 audits — WIRE-1/BRANCH-1/CRP-1/UTF8-STDOUT-1/PCA-1/BCI-1/LINT-MOCK all clean
- 2026-05-17 02:27 BUILD: BC-1 4 rules apply (2 Critical, 2 Important). BC-PROJ-3/BC-GLOBAL-2 (Critical, destructive-git) ADDRESSED by construction — grep confirms zero git checkout/restore/stash/subprocess/file-mutation in slice code. BC-PROJ-4 (Important) ADDRESSED — gate run on real register (mid-slice smoke + real-register invariant test + pre-finish). BC-GLOBAL-1 (Important) N/A — no LLM/fenced-output parsing in slice (deterministic md→JSON)
- 2026-05-17 02:30 BUILD: /drift-check full — 0 blockers, 0 majors; ADR-036/design code claims verified; drift-log.md appended
- 2026-05-17 02:31 BUILD: pre-finish gate ALL GREEN — slice SHIPPED

## Summary

### Plan executed
1. Code fix — `tools/risk_register_audit.py` `main()` `if args.json:`: `out["risks"] = [r.to_dict() for r in view]` (single filtered list; `view` key removed; `summary`/`violations` register-wide, untouched) — DONE
2. AC1 verify — repro PASS — DONE
3. Mission-brief oracle correction `{R1,R3}`→`{R1}` (R3 is medium band; plan-mode catch) — DONE
4. 5 new tests written + module green (30 passed) — DONE
5. Mid-slice smoke (real register) — PASS — DONE
6. Pre-finish gate + Step 6 audits — see below

### Mid-slice smoke gate
**Result**: PASS
**Evidence**: `python -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` → `statuses in risks: ['open']`, `view key present: False`, ids `[R-9, R-2, R-6, R-8]` (all open). Pre-fix this leaked mitigating/retired (R-1/R-3/R-4/R-5). BC-PROJ-4 dogfood on the real artifact.

### Pre-finish gate
- [x] All ACs pass with evidence — TF-1 6/6 PASSING; see validation.md
- [x] Must-not-defer addressed — JSON contract decided (ADR-036); consumer parity durably test-pinned (M-add-1 fix, NOT CSP-1); error/no-filter path unchanged + pinned; regression tests guard leak + band/top
- [x] Drift-check pass — (run at Step 6)
- [x] Smoke regression check pass — full module 30 passed
- [x] No debug code — none added (one explanatory WHY comment at the fix site, R-9/ADR-036 invariant)

### Deferrals
None.

### Design deviations
- Plan-mode: the Critic-stack-proposed `--filter-band high == {R1,R3}` test oracle was wrong (R3 = low×high = score 3 = medium band, verified vs `_band_for_score` + `test_summary_counts_by_band_and_status` which asserts by_band high==1). Corrected the mission-brief Test-oracle line to `{R1}` and `--top 2 --sort score`→`[R1,R2]` before writing the test. Doc-only; no design/ADR shape change; surfaced to user at plan approval. mission-brief updated: yes.

### Files changed
- `tools/risk_register_audit.py` (main() JSON branch — 1-line behavior change + WHY comment)
- `tests/methodology/test_risk_register_audit.py` (repro from /repro + 5 new tests + `import json`/`main`)
- `architecture/shippability.md` (#36 — added by /repro)
- vault: mission-brief.md, design.md, decisions/ADR-036-*.md, critique.md, critique-review.md, milestone.md, build-log.md
