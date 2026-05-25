# Design: Slice 036 fix-rr1-audit-status-filter

**Date**: 2026-05-17
**Mode**: Standard

> **Impact framing (per Critic B1, authoritative R-9 `risk-register.md` L170/L172)**: R-9 is a **latent contract footgun, not a live corruption**. `/pulse` and `/slice` are correct today because they read the per-risk `status`/`band` fields, not `--filter-status` membership. This slice retires R-9 *proactively*; it does not fix a current correctness defect, and reflection.md must not claim one.

## What's new

- `tools/risk_register_audit.py` `main()` `if args.json:` branch modified so the emitted `risks` list reflects `filter_and_sort` (status / band / sort / top), instead of the unfiltered `result.to_dict()["risks"]`. (Symbol-anchored, not line-pinned, per thin-vault convention — m1.)
- The redundant `out["view"]` key is **removed** — one filtered list, single source of truth (the dual-list shape is the exact footgun that caused R-9: producer filled `view`, every consumer read `risks`).
- New regression tests in the existing `tests/methodology/test_risk_register_audit.py` (AC2/AC4 rows from the mission brief's Test-first plan).

## What's reused

- `filter_and_sort()` `tools/risk_register_audit.py:319` — already correct; unchanged. The fix routes its output into the consumed key.
- `AuditResult.to_dict()` `tools/risk_register_audit.py:119` — unchanged. Its `summary` (register-wide `by_band` / `by_status` / `total` / `open_high`) stays computed over **all** risks; a register-level aggregate must not be filtered.
- `_format_human()` `tools/risk_register_audit.py:348` — already consumes `view` correctly; no change. Human-mode was never broken.
- Repro: `tests/methodology/test_risk_register_audit.py::test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks` (shippability #36, established by `/repro`).
- Decision: [[ADR-036]] (this slice).

## Components touched

### `tools/risk_register_audit.py` (modified)
- **Responsibility**: RR-1 risk-register audit + scoring + the filter/sort/top view that `/pulse` and `/slice` consume to rank slice candidates.
- **Lives at**: `tools/risk_register_audit.py` — `main()` `if args.json:` branch only (the `out = result.to_dict(); out["view"] = …` block).
- **Key interactions**: invoked as `python -m tools.risk_register_audit … --json` by `skills/pulse/SKILL.md` (L40) and `skills/slice/SKILL.md` (L45). Both parse the JSON and read the `risks` key. No code module imports this for the JSON shape (blast-radius: skill-prose consumers only).

## Contracts added or changed

### RR-1 audit `--json` output shape (changed — cheap)
- **Defined in code at**: `tools/risk_register_audit.py` `main()` `if args.json:` branch.
- **Before**: `{ "risks": <ALL risks, unfiltered>, "violations": […], "summary": {…}, "view": <filtered+sorted+topped> }`. Consumers read `risks` → filter silently ignored (R-9).
- **After**: `{ "risks": <filter+sort+top applied>, "violations": […], "summary": <register-wide, unchanged> }`. `view` key removed.
- **Auth model**: N/A (CLI tool, no auth surface).
- **Error cases**: unchanged — `audit_register` violations still populate `violations`; process still returns `1 if result.violations else 0`. No-flag invocation still returns every risk (filter is a no-op pass-through; ordering becomes score-desc per the existing `sort_by="score"` default, which consumers already re-sort by and the documented prose already implies "scored, sorted output"). **This register-order→score-desc ordering delta is an acknowledged behavior change (per Critic M1) and is regression-pinned by `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` so it cannot silently revert.**

## Data model deltas

None. No schema, entity, or field change. The `Risk` / `AuditResult` shapes are untouched.

## Wiring matrix

Per WIRE-1. This slice introduces **no new modules** (it modifies one existing function and adds tests to an existing test file). Zero-row matrix = clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-036]] — RR-1 `--json` emits a single filter/sort/top-applied `risks` list; redundant `view` key removed; `summary` stays register-wide — reversibility: cheap

## Authorization model for this slice

N/A — `tools/risk_register_audit.py` is a local CLI/library audit with no authentication or authorization surface.

## Error model for this slice

No new error codes. Existing behavior preserved exactly: malformed register → `violations` populated + exit 1; missing/empty/legacy register → 0 risks, no false alarm; valid register → exit 0. The fix changes only which risks populate the `risks` key in `--json` mode.

## Consumer-parity note (must-not-defer)

> **Correction per Critic B2**: CSP-1 is **not** the mechanism here. `tools/cross_spec_parity_audit.py` (L1–12) is a **Heavy-mode-only** audit over `architecture/threat-model.md` / `requirements.md` / `nfrs.md`; in this Standard-mode project it returns clean as a structural no-op and has zero relationship to skill-prose↔JSON parity. Any "(CSP-1)" attribution for consumer parity is mis-cited and struck.

`skills/pulse/SKILL.md` L40 and `skills/slice/SKILL.md` L45–49 already document the `--json --filter-status open --sort score [--top N]` invocation and prose ("Retired / accepted risks are excluded automatically", "scored, sorted output"). The fix makes the JSON match that already-documented contract — so **no skill-prose edit is required** (this is a code-conformance-to-doc fix, the inverse of the usual drift).

> **Correction per meta-Critic M-add-1**: the pre-existing `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1` assert ONLY `"RR-1" in text` + `"risk_register_audit" in text` (verified `test_risk_register_audit.py` L356–381) — they do **not** pin the `--filter-status open` flag or the "Retired/accepted excluded automatically" / "scored, sorted" prose that this slice's "code-conformance-to-doc" thesis leans on. Crediting them with that parity was an over-claim. A NEW durable prose-pin test is added so the load-bearing prose cannot silently drift.

**Parity is enforced by**, in order: (1) the NEW `test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose` — asserts both `skills/slice/SKILL.md` and `skills/pulse/SKILL.md` contain `--filter-status open` AND their respective exclusion/sorted prose (the durable guard for the thesis); (2) the AC #4 contract-pin tests (`…_contract_pinned_against_unfiltered_regression` + `…_no_flag_invocation_consumed_risks_is_score_desc_then_id`); (3) the pre-existing `*_references_rr_1` tests, credited ONLY with pinning the bare `RR-1`/module reference; (4) a **supplementary** manual `/build-slice` + `/validate-slice` re-read (not the primary guard — a contract this slice's whole thesis rests on must not depend on a manual step). No test reads `out["view"]` (verified: all `view` references in `test_risk_register_audit.py` are local `filter_and_sort` vars; the Critic independently re-confirmed L420 is the only producer and there is no consumer in `tools/`/`skills/`/`agents/`/`tests/`), so removing the key is safe.
