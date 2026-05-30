# Design: Slice 084 harden-pcr-2a-clock-skew-winner

**Date**: 2026-05-30
**Mode**: Standard

## What's new

- A **skew-plausibility guard** inserted into `resolve_vault_claim_conflict`
  (`tools/parallel_conflict_resolver.py`) as a new **Step 2.5** — after
  `_select_timestamp_winner` returns a strict-newer winner (Step 2), strictly
  BEFORE the Step 3 baseline overlay/write. On a suspicious result it returns a
  fail-closed `STOP` (no overlay, no `git add`, no `git rebase --continue`).
- New helper `_winner_clock_skew_suspect(winner, now, tolerance_seconds) -> str | None`
  — returns a human-readable skew reason if the selected winner's `claimed_at`
  is implausible relative to the resolver's trusted wall-clock; `None` otherwise.
  (Takes only `winner` — NOT `loser`, per /critique-review m-add-1: the detector reads
  only the winner's stamp; the call site already holds the `winner, loser` pair from
  `_select_timestamp_winner` and passes `loser` straight to the audit helper.)
- New module constant `_CLOCK_SKEW_TOLERANCE_SECONDS = 300` (5 min) — the benign-
  skew absorption band (see Heuristic below). **Tuning candidate for `/critique`.**
- New audit helper `_append_skew_stop_audit(repo_root, diag, reason, winner, loser, now)`
  — appends a distinct `## Vault-claim resolution (clock-skew STOP) - <ts>` section
  recording BOTH claims' `Claimed-by`/`Claimed-at` + the resolver-now signal +
  the determination. Mirrors the slice-082 `_append_equivalence_stop_audit`
  precedent (`tools/parallel_conflict_resolver.py:1683`). Per /critique-review m-add-2,
  the injected `now` is rendered into the section via `now.isoformat()` (aware, `+00:00`)
  so the recorded resolver-now signal is byte-comparable to the canonical `Claimed-at`
  format (`_now_iso8601_utc` emits `+00:00`) — the audit row is directly diffable.
- New test file `tests/methodology/test_pcr_2a_clock_skew_winner.py` (APED-1
  battery, test-first per TF-1).

## What's reused

- `_select_timestamp_winner` (`tools/parallel_conflict_resolver.py:502`) — **unchanged**;
  stays a pure strict-newer comparator. The guard is a *post*-selection gate, not a
  comparator change (keeps the pure-function contract the DRY audit-site at L1761 relies on).
- `resolve_vault_claim_conflict` 7-step algorithm (`:1087`) — the guard slots between
  Step 2 and Step 3; Steps 3-7 are untouched on the non-suspicious path.
- `_append_equivalence_stop_audit` (`:1683`) — structural template for the new
  skew-STOP audit section (ADR-074 / slice-082 STOP-audit precedent).
- `skills/commit-slice/SKILL.md:190` — **unchanged**; a `conflict_class = VAULT_CLAIM`
  STOP already falls through to the SOAD-1 3-option user-disposition block. The skew-STOP
  returns `conflict_class=VAULT_CLAIM`, so the existing skill surfaces it to the operator
  with the PCR-2b escalation named in the reason. **No skill edit required** → blast radius
  stays single-file (matches the slice-queue NON-OVERLAPPING claim).
- [[slice-082-harden-pcr-1-soft-regen-corner-case]] — direct precedent: harden a low/low
  register corner case, APED-1 battery, no new RULE-ID, MEPD-1 EXCLUDE, no VERSION bump,
  warn/STOP-not-over-trigger discipline.
- [[slice-083-add-pcr-2b-hard-class-conflict-resolution]] — the PCR-2b/TRI-RESOLVE-1 gate
  the skew-STOP escalates the operator toward (R-23 fix-candidate #2 venue).

## The independent signal — design rationale (resolves the mission-brief open question)

R-23 is wrong-winner-by-staleness under cross-machine clock-skew. The guard needs a
signal **not** written by the (possibly-skewed) claiming machine's clock.

- **Rejected — git commit author/committer date.** A claim's commit timestamp is written by
  the SAME machine that wrote `Claimed-at`. If that machine's clock is skewed, both values
  skew together and agree — cross-checking them detects nothing. Not independent.
- **Rejected — `Claim-seq` monotonic counter** (R-23 register fix-candidate #1; also the
  example anticipated in the `_format_vault_claim_audit_entry` docstring at L1031). A
  `slice_queue_claim`-incremented seq is **per-machine-local**; two machines maintain
  independent counters with no shared serialization point before the rebase merge, so
  cross-machine seq comparison is exactly as meaningless as cross-machine clock comparison.
  Does not retire the stated cross-machine case. (This rejection is the slice's premise;
  see mission-brief Out of scope.)
- **Chosen — the resolver's own wall-clock at merge time (`now`).** The machine running
  `/commit-slice --merge` provides the one trusted reference. A claim is made *before* it
  is merged, so a winner whose `claimed_at` is in the **future** relative to `now` (beyond a
  tolerance) is physically impossible from a synced clock → its claiming machine's clock runs
  ahead of the resolver → any strict-newer "win" attributable to that lead is untrustworthy.
  This maps directly to R-23's own framing ("fires only on a meaningfully-skewed clock,
  minutes-to-hours off-real-time") and to its corrigibility hook (the audit records both
  timestamps for forensic recovery).

### Heuristic (the load-bearing design choice — `/critique` should scrutinize)

`now := resolver wall-clock UTC (injectable; defaults to datetime.now(tz=utc))`.
`_winner_clock_skew_suspect` parses **defensively** then compares — the parse has THREE
outcomes, not two (per /critique B1/B2 APED-1 findings):

```python
s = winner.claimed_at.strip()
if s.endswith("Z"):
    s = s[:-1] + "+00:00"          # B2: fromisoformat Z-suffix unsupported < py3.11; project floor >=3.10
try:
    parsed = datetime.fromisoformat(s)
except (ValueError, TypeError):
    return <STOP reason: claimed_at unparseable — cannot verify, fail-closed, escalate PCR-2b>
if parsed.tzinfo is None:
    return <STOP reason: claimed_at tz-naive — cannot compare vs aware resolver-now, fail-closed>   # B1
if parsed > now + timedelta(seconds=_CLOCK_SKEW_TOLERANCE_SECONDS):
    return <SUSPICIOUS reason: winner future-dated vs resolver-now beyond tolerance — escalate PCR-2b>
return None                        # plausible — fall through to strict-newer resolution
```

- **B1 — tz-naive is a third state, fail-closed (NOT a crash).** `datetime.fromisoformat("…T12:00:00")`
  (offset-less) parses *successfully* as a naive datetime; comparing `naive > now_aware` raises
  `TypeError` mid-rebase. `slice_queue_writer.py:589-594` emits the offset *conditionally*, so an
  offset-less `claimed_at` is reachable on real (not purely adversarial) data. The guard treats
  parsed-but-naive identically to unparseable → STOP. The parse+compare is wrapped in
  `except (ValueError, TypeError)` belt-and-suspenders.
- **B2 — `Z` normalized to `+00:00` before parse** so the gate is version-independent across the
  declared `>=3.10` floor (`pyproject.toml:24`); PSQ-2's canonical writer emits `+00:00` (never `Z`),
  but an external/hand-edited `Z` is well-formed RFC-3339 and must not flip STOP-vs-resolve by interpreter.
- **Only the *selected* winner is checked, and this catches a SUB-CASE of R-23 (not all of it — /critique M1).**
  If the skewed (future-dated) entry is the strict-newer winner, it is flagged. The undetectable
  case: a winner whose inflated `claimed_at` still lands in the *past* of merge-time (ahead-clock
  by less than the merge delay) wins wrongly yet does NOT fire the gate. That staler-but-past case
  is **undetectable from a single trusted clock** (the fundamental reason R-23's only general fixes
  are a shared counter — rejected, doesn't work cross-machine pre-merge — or routing ALL VAULT_CLAIM
  resolutions through PCR-2b human/Critic adjudication, which would defeat PCR-2a auto-resolution).
  So this slice **narrows** R-23 to its most egregious/detectable sub-case; the residual stays open.
- **Tolerance = 300 s** absorbs benign NTP jitter + legitimate in-flight claim→merge delay on
  a slightly-ahead machine, satisfying AC-3 over-trigger avoidance. Below R-23's minutes-to-
  hours regime. Happy path: `claimed_at` is in the *past* relative to `now` → never flagged.
  **Assumes the merging machine's clock is the reference and is itself reasonably synced** (per
  /critique M2): a skewed *merger* clock degrades to over-trigger (extra safe STOP) or under-detect
  (R-23 residual) — acceptable under the cooperative NTP-synced fleet model; documented in ADR-076.

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: parallel-slice conflict classification + resolution (PCR-N family).
  This slice adds a clock-skew guard to the VAULT_CLAIM (PCR-2a) resolution path.
- **Key interactions**: invoked via `python -m tools.parallel_conflict_resolver --resolve-soft`
  from `skills/commit-slice/SKILL.md` sub-step 2.5; writes the audit log at
  `architecture/parallel-conflict-resolution-log.md`.
- **Comment-drift touch-ups (CSP-1 hygiene, same file)**: update the `_format_vault_claim_audit_entry`
  docstring L1031 example — it cites "R-23 clock-skew tiebreaker via PSQ-2 `Claim-seq`" as the
  anticipated future change; ADR-076 supersedes that anticipated approach with the resolver-now
  guard. Adjust the comment so the predecessor-spec drift is not carried forward as a live claim.

## Contracts added or changed

None. No new endpoints/events. The CLI surface (`--resolve-soft`) is unchanged — the guard is
internal to `resolve_vault_claim_conflict`. The `ResolutionResult` STOP shape
(`action="STOP", conflict_class=VAULT_CLAIM, reason=<skew text naming PCR-2b>`) reuses the
existing contract the skill already handles (`SKILL.md:190`).

## Data model deltas

None. No new fields on claim records (the `Claim-seq` field is explicitly rejected). The audit
log gains a new *section variant* (`clock-skew STOP`), additive to the existing log file format.

## Wiring matrix

Per **WIRE-1**.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `_winner_clock_skew_suspect` (fn in `tools/parallel_conflict_resolver.py`) | `resolve_vault_claim_conflict` Step 2.5 (same file) + CLI `--resolve-soft` | `tests/methodology/test_pcr_2a_clock_skew_winner.py::test_suspicious_ordering_yields_no_auto_winner` | — |
| `_append_skew_stop_audit` (fn in `tools/parallel_conflict_resolver.py`) | `resolve_vault_claim_conflict` Step 2.5 skew branch (same file) | `tests/methodology/test_pcr_2a_clock_skew_winner.py::test_skew_stop_audit_records_both_claims_and_signal` | — |

No new files except the test file (test files are not WIRE-1 modules). Zero new src modules.

## Decisions made (ADRs)
- [[ADR-076]] — PCR-2a clock-skew guard uses resolver-now future-dating detection, not Claim-seq — reversibility: cheap

## Authorization model for this slice

Unchanged. Cooperative-not-adversarial threat model carried from [[ADR-067]] / [[ADR-071]]:
NOT a security boundary. A malicious local actor can backdate their own clock or edit the queue
directly to defeat the guard — out of scope by the threat model. The guard addresses the
COOPERATING-but-clock-skewed case only (R-23 scope). No claim-backdating defense is claimed.

## Error model for this slice

- **Suspicious winner (future-dated beyond tolerance)** → `STOP`, `conflict_class=VAULT_CLAIM`,
  reason naming the PCR-2b hand-resolve + TRI-RESOLVE-1 escalation; best-effort skew-STOP audit
  entry appended first; NO overlay/write/`rebase --continue`.
- **Unparseable winner `claimed_at`** → `STOP` (distinct reason), same fail-closed posture.
- **tz-naive (offset-less, parses but not comparable) winner `claimed_at`** → `STOP` (distinct
  reason), fail-closed — NEVER the `TypeError` crash a direct naive-vs-aware compare would raise
  (per /critique B1). The parse+compare is additionally `except (ValueError, TypeError)`-guarded.
- **Non-suspicious winner** → falls through to the existing Step 3-7 strict-newer resolution,
  byte-for-byte unchanged (no regression).
- **Audit append failure** → best-effort; logged to stderr, never blocks the STOP return
  (mirrors existing `_append_audit_log` / `_append_equivalence_stop_audit` posture).
