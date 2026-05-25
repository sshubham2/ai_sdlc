---
slice: slice-023-audit-tools-default-utf8-stdout
stage: complete
updated: 2026-05-15
next-action: none (slice complete)
risk-tier: medium
critic-required: true
verdict: NEEDS-FIXES
build-result: SHIPPED
validate-result: PASS
reflect-result: SHIPPED
---

# Milestone: slice-023 audit-tools-default-utf8-stdout

**Stage**: complete
**Next action**: none (slice complete; auto-archived to slices/archive/)
**Updated**: 2026-05-15
**Risk tier**: medium — Critic required: yes (in-house methodology surfaces trigger)
**Final critique verdict**: NEEDS-FIXES (per TRI-1) — all carry-forward applied at /build-slice
**Build result**: SHIPPED
**Validate result**: PASS — all 5 ACs PASS; VAL-1 clean; shippability 23/23 PASS
**Reflect result**: SHIPPED — Windows cp1252 console encoding class N=6 → RETIRED

## Progress

- [x] /slice — 2026-05-15
- [x] /design-slice — 2026-05-15
- [x] /critique — 2026-05-15 — 17 first-Critic findings (5B + 8M + 4m); 14 ACCEPTED-FIXED inline, 3 ACCEPTED-PENDING
- [x] /critique-review — 2026-05-15 — 6 meta-Critic missed findings; all ACCEPTED-FIXED inline; verdict: EXTEND
- [x] TRI-1 user triage — 2026-05-15 — verdict ratified as NEEDS-FIXES; triage audit clean
- [x] /build-slice — 2026-05-15 — 10 phases complete; SHIPPED; all pre-finish audits green; 536/536 pytest PASS in 13.56s
- [x] /validate-slice — 2026-05-15 — PASS; 5/5 ACs PASS with evidence; VAL-1 clean (0 secrets + 0 hallucinated imports); shippability catalog 23/23 PASS in 20.67s
- [x] /reflect — 2026-05-15 — 23 findings ALL VALIDATED (17th consecutive 100% Critic-disposition accuracy slice); lessons-learned + reflection.md authored; auto-archiving next

## Current focus

Slice shipped. Lessons captured. Auto-archiving next.

## On resume

- **Last completed action**: /reflect — reflection.md + lessons-learned.md appended; vault updates documented
- **Current work**: none
- **Next immediate step**: slice auto-archived to `slices/archive/slice-023-audit-tools-default-utf8-stdout/`; `_index.md` refreshed; run `/slice` to define slice-024

## Phase artifacts

- [mission-brief.md](mission-brief.md) — final; 21 TF-1 rows all PASSING; AC #4 references `test_utf8_stdout_regression.py`
- [design.md](design.md) — final
- [critique.md](critique.md) — complete; 17 first-Critic findings + Triage table + verdict NEEDS-FIXES; triage_audit clean
- [critique-review.md](critique-review.md) — complete; 6 meta-Critic findings + Builder dispositions; verdict EXTEND
- [build-log.md](build-log.md) — complete; Events trace (12 entries) + Summary (10 phases enumerated + pre-finish + recursive-self-application impact + test counts); SHIPPED
- [validation.md](validation.md) — complete; 5/5 ACs PASS with per-AC evidence; VAL-1 clean; shippability 23/23 PASS; result PASS
- [reflection.md](reflection.md) — complete; 23/23 findings VALIDATED; 2 MISSED-by-Critic candidates surfaced for /critic-calibrate slice-024; cp1252 class RETIRED

## ACCEPTED-PENDING items to apply at /build-slice

1. **B2: PMI-1 `_list_actual_tools` leading-underscore filter**
   - Edit `tools/plugin_manifest_audit.py` `_list_actual_tools` (L137-140): change filter to `if p.name != "__init__.py" and not p.name.startswith("_")`.
   - Add `tests/methodology/test_plugin_manifest_audit.py::test_list_actual_tools_filters_leading_underscore_helpers` with TWO assertions:
     (a) `_list_actual_tools(real_repo_root)` does NOT include `"tools/_stdout.py"` post-slice-023 ship.
     (b) `_list_actual_tools(tmp_path_with_synthetic_helper)` does NOT include `"tools/_helper.py"`.
   - PMI-1 v1.1 retirement-proof invariant preserved (gate body unchanged; only discovery filter narrows).

2. **M1 + M-add-2: Per-tool argv fixture construction rigor**
   - Behavioural regression test at `tests/methodology/test_utf8_stdout_regression.py` constructs per-tool argv per the verified table in design.md "Error model" surface 3.
   - Fixture file `tests/methodology/fixtures/utf8_stdout/slice-fixture/mission-brief.md` + auxiliary fixture content carrying U+2192 must satisfy each audit's parser shape enough to reach the encoding-emitting code path (TF-1 needs parseable plan table; WIRE-1 needs parseable wiring matrix; etc.).
   - subprocess.run pinned: `text=True, encoding="utf-8", errors="replace", env={..., "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"}`.
   - Failure assertion: `"UnicodeEncodeError" not in result.stderr and "UnicodeDecodeError" not in result.stderr` — NOT exit-code-0.

## Cumulative findings reference

- 17 first-Critic findings — see [critique.md](critique.md) Findings + Triage sections
- 6 meta-Critic missed findings — see [critique-review.md](critique-review.md)
- 23 cumulative — empirical evidence of codification-slice density ratching toward slice-021 HWM N=28; design.md "Cumulative-Critic-influence note" + "Recursive-self-application impact" sections document the catch-class breakdown for /critic-calibrate slice-024+ promotion eligibility

## Context anchors for downstream phases

- **Recurrence baseline**: N=6 cumulative cp1252 console encoding instances across slices 007, 016, 018, 020, 021, 022. Slice-022 reflection L94: "structurally overdue; defer cost is paid at every /build-slice + /validate-slice + /reflect that touches a tool with non-ASCII stdout."
- **Empirical witness**: slice-022 D-5 at `tools/test_first_audit.py` U+2192 arrow (interpolated from TF-1 row status transitions / mission-brief content).
- **Counter-witness**: em-dash (U+2014) IS in cp1252 byte 0x97 so existing em-dashes in audit output didn't crash; the failure class is anything OUTSIDE cp1252 (arrows, box-drawing, CJK, most U+2xxx geometric shapes).
- **Workaround already in place at multiple call sites**: `$env:PYTHONIOENCODING = "utf-8"` inline before audit invocations — slice-023 makes the workaround unnecessary.
- **Scope-fence**: file-write side already handled (slice-021 D-3 `encoding="utf-8"` on `write_text`); this slice is exclusively the **stdout/stderr** side of the same class.
