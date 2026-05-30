# Slice 084: harden-pcr-2a-clock-skew-winner

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-23 (PARTIAL — narrows the future-dated-winner sub-case; staler-but-past residual stays open per /critique M1)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

PCR-2a's VAULT_CLAIM resolution picks the winner of a same-candidate claim
collision by strictly-newer `Claimed-at` (`tools/parallel_conflict_resolver.py:520-523`),
which silently trusts that the two `Claimed-at` wall-clock timestamps — written
independently by two sessions on two machines with no shared serialization point
(`tools/slice_queue_claim.py:629` `_now_iso8601_utc()`, second-precision, no shared
counter) — are comparable. Under meaningful cross-machine clock-skew the
strict-newer rule favors the wrong (staler) session (R-23). This slice adds a
**skew-plausibility gate**: before declaring a strict-newer winner, the resolver
cross-checks the claim ordering against an independent signal; a suspicious
ordering is **not auto-resolved** — it fails closed to a STOP that carries both
timestamps and escalates to the PCR-2b HARD/MIXED Critic + TRI-RESOLVE-1 triage
path (shipped slice-083). Now, because PCR-2b exists, the escalation has a real
adjudication venue — which it did not when R-23 was first registered (R-23
fix-candidate #2).

Why now: PCR-2b (slice-083) just closed the HARD/MIXED conflict classes, giving
the skew-suspicious VAULT_CLAIM case a documented escalation target. R-23 was the
last open correctness residual on the `PCR-N` parallel-conflict axis.

## Acceptance criteria

1. PCR-2a VAULT_CLAIM resolution gains a skew-plausibility check on the two
   colliding claims; when the ordering is judged suspicious by the defined
   heuristic, no strict-newer auto-winner is produced and the resolver returns
   `action: STOP` with a skew-specific `reason` — it NEVER silently applies
   strict-newer on a suspicious ordering.
2. The skew-STOP path records BOTH claims' `Claimed-by` + `Claimed-at` (and the
   independent cross-check signal) in the resolution audit entry (R-23
   corrigibility hook), and its `reason`/context routes the operator to the
   PCR-2b gate — not a bare dead-end STOP.
3. No happy-path regression: a plausibly-ordered claim collision still
   auto-resolves by strict-newer exactly as PCR-2a does today (the gate is
   additive and fires ONLY on the suspicious case — warn/STOP must not
   over-trigger; cf. slice-082 R-24 warn-not-STOP discipline).
4. R-23 is **narrowed (not fully retired — per /critique M1)**: an APED-1-style
   test battery demonstrates the **future-dated-winner** skew sub-case is now
   detected/escalated rather than silently mis-resolved, AND the plausible case
   still resolves. The staler-but-past wrong-winner case (winner stamped in the
   past relative to merge-time yet wrong by skew) is **undetectable from a single
   trusted clock** and remains an explicit R-23 residual (registered at /reflect;
   R-23 stays open, downgraded). Full suite + shippability catalog green.

## Test-first plan

Per **TF-1** (`methodology-changelog.md` v0.13.0). Each AC maps to failing tests
written BEFORE implementation. Statuses progress PENDING -> WRITTEN-FAILING ->
PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py
--strict-pre-finish` and refuses any non-PASSING row. Test paths/functions below
are provisional — `/design-slice` finalizes them against the chosen helper shape.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_suspicious_ordering_yields_no_auto_winner | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_suspicious_ordering_returns_stop_with_skew_reason | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_naive_offsetless_claimed_at_stops_not_crashes | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_unparseable_claimed_at_stops_fail_closed | PASSING |
| 1 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_z_suffix_claimed_at_handled_version_independently | PASSING |
| 2 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_skew_stop_audit_records_both_claims_and_signal | PASSING |
| 2 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_skew_stop_reason_routes_to_pcr_2b_gate | PASSING |
| 3 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_plausible_ordering_still_auto_resolves_strict_newer | PASSING |
| 3 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_gate_does_not_overtrigger_on_normal_skew_within_threshold | PASSING |
| 3 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_tolerance_boundary_at_300s_not_suspicious | PASSING |
| 3 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_tolerance_boundary_at_301s_suspicious | PASSING |
| 4 | unit | tests/methodology/test_pcr_2a_clock_skew_winner.py | test_aped1_battery_future_dated_winner_caught_past_resolves | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Suspicious ordering → STOP, never strict-newer | Run battery cases with skewed `claimed_at` pairs; assert `action: STOP` + skew `reason`, no winner applied |
| 2 | Both timestamps + signal logged; routes to PCR-2b | Assert audit-entry text contains both `Claimed-by`/`Claimed-at` values + the cross-check signal + PCR-2b escalation pointer |
| 3 | Happy path preserved | Run plausibly-ordered collision; assert strict-newer winner identical to pre-slice behavior; assert gate does NOT fire within threshold |
| 4 | R-23 retired; suite green | `& $PY -m pytest`; `/validate-slice` shippability checks; APED-1 battery 100% |

## Must-not-defer

- [ ] Fail-closed semantics: suspicious ordering STOPs, never auto-picks a winner
- [ ] Both claims' `Claimed-by` + `Claimed-at` + the cross-check signal logged in the audit entry (forensic corrigibility)
- [ ] Happy-path strict-newer resolution preserved bit-for-bit (no over-trigger; warn-not-STOP discipline from slice-082 R-24)
- [ ] Cooperative-not-adversarial threat model preserved — this is NOT a security boundary (ADR-067/ADR-069 §); no claim-backdating defense claimed
- [ ] CAD-1 / Mini-CAD drift: if `skills/commit-slice/SKILL.md` PCR prose changes, keep installed copy content-equal

## Out of scope

- **Claim-seq number / shared counter** (R-23 fix-candidate #1) — rejected: a per-machine `slice_queue_claim`-incremented seq is not cross-machine comparable without a shared serialization point the distributed pre-merge branch model cannot provide; building it would not retire R-23's stated cross-machine case. This rejection is the slice's premise.
- **Microsecond-precision `_now_iso8601_utc`** (R-23 fix-candidate #3) — explicitly cosmetic per the register; narrows the tie window, does not address skew.
- Same-machine tie handling beyond PCR-2a's existing `claimed_at == claimed_at → None → STOP`.
- Multi-candidate (`len(collisions) > 1`) STOP path — already handled by PCR-2a, untouched.
- Any new methodology RULE-ID unless `/design` + `/critique` judge the skew gate a genuinely new rule (likely MEPD-1 EXCLUDE — refines PCR-2a in place; decided at `/design`, not pre-committed here).

## Dependencies

- Prior slices: [[slice-078-add-pcr-2a-vault-claim-resolver]] — the strict-newer rule being hardened; [[slice-083-add-pcr-2b-hard-class-conflict-resolution]] — the PCR-2b/TRI-RESOLVE-1 gate this slice escalates into; [[slice-082-harden-pcr-1-soft-regen-corner-case]] — direct precedent (harden a low/low corner case off the register; APED-1 battery; warn-not-STOP discipline)
- Code: `tools/parallel_conflict_resolver.py` (`_select_timestamp_winner` :502, VAULT_CLAIM dispatch :274-292, `_record`/audit-entry helpers), `tools/slice_queue_claim.py` (`_now_iso8601_utc` :623, claim records)
- Vault refs: [[decisions/ADR-071]] (PCR-2a), [[decisions/ADR-075]] (PCR-2b/TRI-RESOLVE-1), [[decisions/ADR-067]] (cooperative threat model)
- Risk register: [[risk-register#R-23]]

## Mid-slice smoke gate

At ~50% of build (skew gate implemented, happy path not yet re-verified), run:
```
& $PY -m pytest tests/methodology/test_pcr_2a_clock_skew_winner.py -x
```
Expected: suspicious-ordering cases pass (STOP + skew reason); happy-path case
passes (strict-newer still resolves). If a happy-path test now STOPs → the gate
over-triggers → STOP, retune the heuristic, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] test_first_audit.py --strict-pre-finish: all rows PASSING
- [ ] R-23 downgraded + staler-but-past residual registered at /reflect (NOT flipped to retired — per /critique M1)
