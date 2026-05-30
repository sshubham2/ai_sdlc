# Critique: Slice 084 harden-pcr-2a-clock-skew-winner

**Critic reviewed**: mission-brief.md, design.md, ADR-076 (summarized inline — see m2)
**Date**: 2026-05-30
**Result**: NEEDS-FIXES

## Summary

The core architecture is sound: a post-selection skew gate that fails closed to the shipped
PCR-2b path, checking only the winner against the resolver's trusted wall-clock, is a defensible
R-23 mitigation. But APED-1 execution against the real PSQ-2 timestamp shapes reveals a
comparison-crash defect (B1) and a Python-floor parse gap (B2) the pseudocode hid, plus a missing
honesty about R-23 being *narrowed not retired* (M1).

## Findings

### Blockers (must address before /build-slice)

#### B1: Naive-vs-aware datetime comparison crashes the gate on offset-less `claimed_at`
- **Claim under review**: design.md Heuristic treated "parseable" as binary (parses → compare; else STOP).
- **Issue**: `datetime.fromisoformat("2026-05-30T12:00:00")` (offset-less) parses *successfully* as a
  naive datetime — it does NOT hit the unparseable→STOP branch. The next line `naive > now_aware`
  raises `TypeError: can't compare offset-naive and offset-aware datetimes` — an uncaught crash
  mid-rebase, not a fail-closed STOP. Reachable on real data: `slice_queue_writer.py:589-594` emits
  the offset *conditionally*; the `Claimed-at` parser reads whatever string is in the queue text.
  The existing `_select_timestamp_winner:522` compares strings lexicographically and never parses,
  so it is immune — the new gate introduces the parse and therefore the crash.
- **Evidence**: Executed (py3.13): `fromisoformat("…T12:00:00")` → `tzinfo=None`; `naive > now+Δ` → `TypeError`. `tools/slice_queue_writer.py:591` `if provenance_ts.tzinfo is not None:`.
- **Proposed fix**: Treat parsed-but-tz-naive as fail-closed STOP identically to unparseable; wrap parse+compare in `except (ValueError, TypeError)`; add an APED-1 row asserting offset-less STOPs not crashes.
- **Builder draft**: ACCEPTED-FIXED — design.md §Heuristic now models the third (tz-naive) state → STOP with `except (ValueError, TypeError)` belt-and-suspenders; error model gains the tz-naive row; mission-brief TF plan gains `test_naive_offsetless_claimed_at_stops_not_crashes` + `test_unparseable_claimed_at_stops_fail_closed`; ADR-076 Decision documents it.

#### B2: `Z`-suffix `claimed_at` unparseable on the declared Python floor (3.10), inverting STOP semantics across runtimes
- **Claim under review**: design.md "Unparseable claimed_at ⇒ STOP … PSQ-2 always writes well-formed RFC-3339."
- **Issue**: `fromisoformat` did not accept the RFC-3339 `Z` UTC designator until Python 3.11; `pyproject.toml:24` declares `requires-python = ">=3.10"`. A `Z`-suffixed (well-formed RFC-3339) `claimed_at` raises `ValueError`→STOP on 3.10 but parses→no-STOP on 3.11+ — same input, opposite gate behavior by interpreter.
- **Evidence**: Executed (3.13): `fromisoformat("…Z")` OK. Official: bugs.python.org/issue35829 — `Z` support added 3.11. Floor: `pyproject.toml:24`.
- **Proposed fix**: Normalize `s.replace("Z","+00:00")` before `fromisoformat` (documented 3.10 workaround), OR document Z→STOP intent in ADR-076. Pick one; don't leave it runtime-dependent.
- **Builder draft**: ACCEPTED-FIXED — chose normalize `Z`→`+00:00` before parse (version-independent). design.md §Heuristic + ADR-076 Decision document it; mission-brief TF plan gains `test_z_suffix_claimed_at_handled_version_independently`.

### Majors (address this slice)

#### M1: "R-23 is retired" overstates — the heuristic narrows R-23 to the future-dating sub-case
- **Claim under review**: mission-brief AC-4 "R-23 is retired"; design.md "Checking the winner is sound and sufficient."
- **Issue**: The gate fires ONLY when the winner's `claimed_at` is in the *future* of resolver-now beyond tolerance. R-23 (`risk-register.md:407`) is "apparent strictly-newer Claimed-at that is actually older real-time." Worked example: machine A clock +10 min; A claims at real-time T, stamps T+10; B claims at T+5 (synced), stamps T+5; A wins strict-newer though B is the later real claim; merge at T+20 → A's T+10 stamp is in the *past* → gate does NOT fire → wrong winner silently applied. The gate catches a strict subset. "Retired" is the wrong verb.
- **Evidence**: `risk-register.md:407`; future-dating condition only triggers when `now < winner_stamp − tol`.
- **Proposed fix**: Reframe AC-4 / ADR-076 to "R-23 narrowed: future-dated-winner sub-case detected/escalated; staler-but-past residual remains." Keep R-23 open (downgraded); register residual at /reflect.
- **Builder draft**: ACCEPTED-FIXED — mission-brief frontmatter `Risk retired` + AC-4 + pre-finish gate reframed to "narrowed/partial, residual stays open"; design.md §Heuristic bullet rewritten to name the undetectable staler-but-past case + why it's fundamentally undetectable from one clock; ADR-076 Consequences reframed retired→narrowed with R-23 staying open (downgraded).

#### M2: Independent-signal soundness rests on an unstated assumption that resolver-now is itself trustworthy
- **Claim under review**: design.md "the machine running /commit-slice --merge provides the one trusted reference."
- **Issue**: If the *merging* machine's clock is skewed, the gate over-triggers (false STOP, violates AC-3) or under-detects. The design picks resolver-now as trusted by fiat without stating the assumption that bounds both guarantees.
- **Evidence**: design.md §The independent signal; no assumption recorded in ADR-076.
- **Proposed fix**: Add one sentence to ADR-076 documenting the assumption + degradation modes.
- **Builder draft**: ACCEPTED-FIXED — ADR-076 Decision now carries the "Trust assumption (per /critique M2)" paragraph; design.md §Heuristic tolerance bullet echoes it.

### Minors (log; address if cheap)

#### m1: Tolerance value 300 s asserted, not boundary-pinned in tests
- **Issue**: The `>` (strict) vs `>=` boundary at exactly `now + 300s` is not pinned in the battery.
- **Proposed fix**: Add `now + 300s` (NOT suspicious) and `now + 301s` (suspicious) rows.
- **Builder draft**: ACCEPTED-FIXED — mission-brief TF plan gains `test_tolerance_boundary_at_300s_not_suspicious` + `test_tolerance_boundary_at_301s_suspicious` pinning strict-greater.

#### m2: ADR-076 reviewed via summary; verify reframe propagates to all three claim sites (FBCD-1)
- **Issue**: M1's "retired"→"narrowed" reframe must land identically in mission-brief AC-4 + ADR-076 + design.md.
- **Builder draft**: ACCEPTED-FIXED — reframe applied to all three sites in this fix round; ADR-076 Consequences explicitly notes the FBCD-1 claim-parity.

## Dimensions checked
- [x] Unfounded assumptions — M2 (resolver-now trust); B2 (uniform parse across declared floor).
- [x] Missing edge cases — B1 (tz-naive parses-then-crashes); B2 (`Z` on 3.10); m1 (tolerance boundary).
- [x] Over-engineering — none. Single file, one constant, two helpers each wired.
- [x] Under-engineering — B1 (heuristic had no design element for the parsed-but-naive path).
- [x] Contract gaps — none. Verified `resolve_vault_claim_conflict` returns `conflict_class=VAULT_CLAIM` on STOP (:1149/:1198), so the "no skill edit required" claim (SKILL.md:190 fall-through) holds.
- [x] Security — none. Cooperative-not-adversarial correctly scoped; no claim-backdating defense claimed.
- [x] Drift from vault — ADR-076 supersedes the L1031 docstring's anticipated Claim-seq approach (design schedules the touch-up). MEPD-1 EXCLUDE correct (matches slice-082). M1 was the one traceability issue (now fixed).
- [x] Web-known issues — B2 confirmed via bugs.python.org/issue35829 (`Z` is 3.11+; floor 3.10).
- [x] Cross-cutting conformance — APED-1 by execution against the adversarial corpus (`+00:00`, `Z`, naive, space-sep, microsecond, garbage, empty) yielded B1 + B2. FBCD-1: m2.

## Triage

**Triaged by**: user
**Date**: 2026-05-30
**Final verdict**: CLEAN

Reconciled across both passes: first Critic (B1/B2/M1/M2/m1/m2) + meta-Critic EXTEND (m-add-1/m-add-2).
Meta-Critic confirmed all six first-Critic findings VALID with correct severities and verified the
B1/B2 fix-deltas are defect-free. All dispositions ACCEPTED-FIXED at design stage; code follows the
corrected design + TF rows at /build-slice.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | design.md §Heuristic tz-naive→STOP + `except (ValueError, TypeError)`; error model row; mission-brief TF rows `test_naive_offsetless_claimed_at_stops_not_crashes` + `test_unparseable_claimed_at_stops_fail_closed`; ADR-076 Decision |
| B2 | Blocker  | ACCEPTED-FIXED | design.md §Heuristic `Z`→`+00:00` normalize; ADR-076 Decision; mission-brief TF row `test_z_suffix_claimed_at_handled_version_independently` |
| M1 | Major    | ACCEPTED-FIXED | mission-brief frontmatter+AC-4+pre-finish reframed narrowed; design.md §Heuristic staler-but-past undetectable bullet; ADR-076 Consequences retired→narrowed, R-23 open-downgraded |
| M2 | Major    | ACCEPTED-FIXED | ADR-076 Decision "Trust assumption" paragraph; design.md §Heuristic tolerance bullet |
| m1 | Minor    | ACCEPTED-FIXED | mission-brief TF rows `test_tolerance_boundary_at_300s_not_suspicious` + `..._at_301s_suspicious` (strict-`>` pinned) |
| m2 | Minor    | ACCEPTED-FIXED | three-site reframe parity (mission-brief/design/ADR-076) verified by meta-Critic (FBCD-1) |
| m-add-1 | Minor | ACCEPTED-FIXED | design.md drops `loser` from `_winner_clock_skew_suspect` signature (call site passes `loser` to the audit helper) |
| m-add-2 | Minor | ACCEPTED-FIXED | design.md §What's new + audit-helper: `now` rendered via `.isoformat()` (`+00:00`), byte-comparable to canonical `Claimed-at` |

