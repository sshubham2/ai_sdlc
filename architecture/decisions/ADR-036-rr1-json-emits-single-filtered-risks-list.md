---
id: ADR-036
title: RR-1 audit `--json` emits a single filter/sort/top-applied `risks` list; the redundant `view` key is removed
date: 2026-05-17
slice: slice-036-fix-rr1-audit-status-filter
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-036: RR-1 audit `--json` emits a single filtered `risks` list

## Context

R-9 (medium, score 3): `tools.risk_register_audit --json` does not apply
`--filter-status` / `--filter-band` / `--top` to the risk list its consumers
read. In `main()`'s `if args.json:` branch, `out = result.to_dict()` emits
**all** risks under `out["risks"]`, while the filtered/sorted/topped list goes
into a separate `out["view"]` key. `skills/pulse/SKILL.md` (L40) and
`skills/slice/SKILL.md` (L45) both reference the `--json` invocation. Per the
authoritative R-9 entry (`architecture/risk-register.md` L170, L172) this is a
**latent contract footgun, not a live corruption**: those consumers are
correct *today* because they read the per-risk `status`/`band` fields, not
`--filter-status` membership — "no current correctness impact". The risk is
that a *future* consumer change which trusts `--filter-status` membership
directly would treat retired risks as open. This ADR records a **proactive**
retirement of that footgun; it does not claim or fix a present defect. The
dual-list shape (producer writes one key, every consumer reads the other) IS
the latent defect mechanism.

## Options considered

1. **`risks` = filtered view; drop `view` (chosen)** — single filtered list
   under the key consumers already read; `summary` stays register-wide.
   Pros: matches the already-documented skill prose ("retired/accepted
   excluded automatically", "scored, sorted output") with **zero skill-prose
   edits**; eliminates the dual-source-of-truth footgun that caused R-9;
   single-file code change. Cons: `risks` becomes score-sorted even with no
   flags (consumers already sort/treat it as scored; documented prose already
   says "scored, sorted").
2. **Keep `risks` unfiltered; point consumers at `view`** — edit
   `skills/pulse/SKILL.md` + `skills/slice/SKILL.md` to read `out["view"]`.
   Cons: multi-surface skill-prose change (SRCD-1-class propagation +
   CSP-1/drift surface); leaves the two-list footgun in place; contradicts
   the documented "excluded automatically" prose.
3. **`risks` = filtered; keep `view` as an alias** — both keys present, equal.
   Cons: retains a redundant second list — the precise shape that enabled the
   bug; future code could re-diverge them.

## Decision

In `main()`'s `--json` branch, build the consumed list from `filter_and_sort`
and emit it under `risks`; remove the separate `view` key. `AuditResult`,
`to_dict()`, `filter_and_sort()`, and `_format_human()` are unchanged. The
register-wide `summary` (`by_band` / `by_status` / `total` / `open_high`)
stays computed over all risks — a register-level aggregate must not be
filtered, and the existing library-level summary tests assert it via
`result.to_dict()`, not via `main()`'s JSON, so they are unaffected.

## Consequences

- The `--filter-status`/`--filter-band`/`--top` footgun is closed before any
  consumer comes to depend on filter membership; no skill-prose change (the
  JSON now conforms to the already-documented contract).
- No code module depends on the JSON shape (blast-radius = skill-prose
  consumers only); no `tests/*` reads `out["view"]` (verified twice — design
  author + Critic), so dropping the key breaks nothing.
- Unfiltered `--json` invocations now return risks score-sorted rather than in
  register order; this is consistent with the documented "scored, sorted
  output" and is regression-pinned by
  `test_json_no_flag_invocation_consumed_risks_is_score_desc_then_id` so it
  cannot silently revert.
- Consumer parity is enforced primarily by a NEW durable prose-pin test
  (`test_skill_consumers_pin_rr1_filter_invocation_and_exclusion_prose`) that
  asserts both consumer SKILL.md files contain the `--filter-status open`
  flag + the exclusion/sorted prose the "code-conformance-to-doc" thesis
  rests on, plus the AC #4 contract-pin tests, with a supplementary manual
  `/build-slice` + `/validate-slice` re-read. The pre-existing
  `test_pulse_skill_references_rr_1` / `test_slice_skill_references_rr_1`
  are credited ONLY with pinning the bare `RR-1`/module reference — they do
  not pin the flag or prose (corrected per meta-Critic M-add-1; original
  wording over-claimed their coverage). Parity is **NOT** enforced by CSP-1,
  a Heavy-mode-only threat/req/nfr audit and a structural no-op in this
  Standard-mode project (corrected per Critic B2).

## Reversibility

**cheap** — the change is localized to a ~4-line block in `main()`'s JSON
branch. Reverting (restoring the dual `risks`/`view` shape) is a one-edit
change with no schema, migration, or contract-consumer code to unwind. Tagged
cheap accordingly.
