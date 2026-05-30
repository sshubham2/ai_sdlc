---
id: ADR-076
title: PCR-2a clock-skew guard detects future-dated winners against the resolver's own wall-clock, not via a Claim-seq counter
date: 2026-05-30
slice: slice-084-harden-pcr-2a-clock-skew-winner
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-076: PCR-2a clock-skew guard uses resolver-now future-dating detection

## Context

PCR-2a (slice-078 / [[ADR-071]]) resolves a same-candidate VAULT_CLAIM collision by
strictly-newer `Claimed-at` (`_select_timestamp_winner`,
`tools/parallel_conflict_resolver.py:502`). The comparison trusts that two `Claimed-at`
wall-clock strings — written independently by two sessions on two machines with no shared
serialization point (`tools/slice_queue_claim.py:629`, `_now_iso8601_utc`, second-precision,
no shared counter) — are comparable. Under cross-machine clock-skew the rule can favor the
staler session: an apparent strictly-newer `Claimed-at` that is older in real time (R-23,
likelihood low / impact low / open).

The slice-083 PCR-2b HARD/MIXED gate (gate-on-hand-resolve + TRI-RESOLVE-1) now exists,
giving a skew-suspicious case a documented adjudication venue — which it lacked when R-23 was
registered (R-23 fix-candidate #2). This ADR decides *how* the suspicious case is detected.

## Options considered

1. **`Claim-seq` monotonic counter** (R-23 register fix-candidate #1; the example the
   `_format_vault_claim_audit_entry` docstring at L1031 anticipated). Add a `Claim-seq` field
   to PSQ-2 claim records, incremented per write by `tools/slice_queue_claim`; switch PCR-2a
   from strict-newer `Claimed-at` to strict-greater `Claim-seq`.
   - **Con (fatal)**: a per-CLI-invocation counter is **per-machine-local**. Two machines keep
     independent counters with no shared serialization point before the rebase merge, so a
     cross-machine `Claim-seq` comparison is exactly as meaningless as a cross-machine clock
     comparison. It does **not** retire R-23's stated cross-machine case; it would only order
     same-machine races, which the OS clock already orders correctly. Also a PSQ-2
     sub-mechanism change with forward-compat burden against already-written claims.

2. **Microsecond-precision `_now_iso8601_utc`** (R-23 fix-candidate #3). Narrows the tie window;
   explicitly cosmetic per the register — does not address skew at all.

3. **git commit author/committer date as cross-check.** Compare each claim's `Claimed-at`
   against the date of the commit that wrote it.
   - **Con (fatal)**: that commit date is set by the SAME machine clock that wrote `Claimed-at`.
     A skewed clock skews both equally; they agree; the cross-check detects nothing. Not an
     independent signal.

4. **Resolver-now future-dating detection** (chosen). Before applying the strict-newer winner,
   compare the winner's `claimed_at` against the resolver's own wall-clock at merge time. A
   claim is made before it is merged, so a winner timestamped in the future relative to
   resolver-now (beyond a tolerance) is physically impossible from a synced clock → the
   claiming machine's clock runs ahead → the strict-newer win is untrustworthy → STOP + escalate.

## Decision

Insert a **Step 2.5 skew-plausibility guard** into `resolve_vault_claim_conflict`, after
`_select_timestamp_winner` (Step 2) and strictly before the Step 3 overlay/write. The guard
(`_winner_clock_skew_suspect`) flags the selected winner as suspicious when its `claimed_at`
exceeds `now + _CLOCK_SKEW_TOLERANCE_SECONDS` (proposed 300 s) — using the resolver's own UTC
wall-clock (`now`, injectable for testing) as the trusted reference. The parse is **defensive**
(per /critique B1/B2 APED-1 findings): `Z` is normalized to `+00:00` before `fromisoformat`
(the suffix is unsupported below Python 3.11 and the project floor is `>=3.10`, `pyproject.toml:24`);
an unparseable timestamp → fail-closed STOP; a **tz-naive** timestamp (offset-less — which
`fromisoformat` parses *successfully*, then `naive > aware` would raise `TypeError` mid-rebase) is
treated identically to unparseable → fail-closed STOP, never a crash; and the parse+compare is
`except (ValueError, TypeError)`-guarded as belt-and-suspenders. Only the *selected winner* is
checked (a skewed *loser* does not corrupt a genuinely-newer winner's result).

**Trust assumption (per /critique M2)**: the guard assumes the *merging* machine's clock is the
reference and is itself reasonably synced. A skewed merger clock degrades to over-trigger (an
extra, safe STOP) or under-detect (R-23 residual). Acceptable under the cooperative NTP-synced
fleet model (ADR-067/ADR-071); NOT a security boundary.

On suspicious: append a best-effort `## Vault-claim resolution (clock-skew STOP)` audit section
recording BOTH claims' `Claimed-by`/`Claimed-at` + the resolver-now signal + the determination,
then return `STOP` with `conflict_class=VAULT_CLAIM` and a reason naming the PCR-2b hand-resolve
+ TRI-RESOLVE-1 escalation. No overlay, no `git add`, no `git rebase --continue`. The existing
`skills/commit-slice/SKILL.md:190` already routes a `VAULT_CLAIM` STOP to the SOAD-1 user-
disposition block, so the operator is surfaced the skew finding with the escalation named — no
skill edit required.

`_select_timestamp_winner` stays a pure strict-newer comparator (unchanged). This **mints no new
RULE-ID** — it hardens PCR-2a's resolution in place (MEPD-1 posture: **EXCLUDE**), mirroring
[[ADR-074]] / slice-082's hardening of PCR-1 (no new rule, no VERSION bump).

## Consequences

- R-23 is **narrowed, not retired** (per /critique M1). The guard catches the **future-dated-winner**
  sub-case — a winner whose inflated `claimed_at` lands in the future of merge-time — and escalates
  it; the loser's work is recoverable from the audit trail (R-23 corrigibility hook), adjudication
  routing to the PCR-2b gate. The **staler-but-past** wrong-winner case (an ahead-clock winner whose
  stamp still precedes merge-time by less than the merge delay) is **undetectable from a single
  trusted clock** and remains an explicit R-23 residual. Full retirement would require either a
  shared counter (rejected above — not cross-machine comparable pre-merge) or routing *all*
  VAULT_CLAIM resolutions through PCR-2b human/Critic adjudication, which would defeat PCR-2a's
  auto-resolution value. R-23 therefore stays **open (downgraded)** with the residual registered at
  /reflect — the "retired" verb in any predecessor framing is corrected to "narrowed" across
  mission-brief AC-4 + design.md + this ADR (FBCD-1 claim-parity, per /critique m2).
- The `_format_vault_claim_audit_entry` docstring (L1031) anticipating "R-23 clock-skew
  tiebreaker via PSQ-2 `Claim-seq`" is now stale predecessor-spec; this slice updates that
  comment so it does not stand as a live claim (CSP-1 / brownfield don't-carry-forward-stale).
- Blast radius is a single file (`tools/parallel_conflict_resolver.py`) plus a new test file.
- **Residual** (open, to register at /reflect if confirmed): the 300 s tolerance is a deliberate
  AC-3 over-trigger / under-detect tradeoff — a sub-tolerance skew that flips two near-simultaneous
  claims is not caught (impact low; loser re-picks from audit log). The cooperative threat model
  is preserved: NOT a security boundary; no claim-backdating defense.

## Reversibility

**cheap.** The guard is an internal pre-application check in one function behind one tunable
constant. Removing it, retuning the tolerance, or swapping the signal is a localized edit with no
contract, schema, or persisted-format change (the new audit section is additive). No consumer
depends on the STOP-vs-APPLIED boundary shifting.
