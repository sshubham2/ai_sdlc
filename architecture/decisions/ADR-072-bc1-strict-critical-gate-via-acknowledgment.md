---
id: ADR-072
title: BC-1 gains an opt-in --strict gate that refuses unacknowledged applicable Critical rules, cleared by explicit --ack-critical rule-ID sign-off
date: 2026-05-29
slice: slice-080-harden-bc1-critical-rules-exit-gate
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-072: BC-1 Strict Critical-Gate via acknowledgment (BCSG-1)

## Context

`tools/build_checks_audit.py` (BC-1) prints "Per BC-1, Critical rules MUST be addressed before /build-slice declares the slice done" and `skills/build-slice/SKILL.md` states "Critical rules are not deferrable" — but `main()` ends in `return 1 if result.violations else 0`, where `result.violations` holds only parse errors (malformed `build-checks.md`). An applicable non-deferrable Critical rule therefore produces **exit 0**. A tooling consumer (an automated `/build-slice` Step 6, CI) that treats the exit code as the gate signal silently passes a slice that violates a Critical rule. This is `diagnose-out/backlog.md` SC-008 (finding F-HALF-9b2e44d1), a self-acknowledged v1 limitation ("v1 surfaces rules; the human/AI builder addresses them. Auto-verification ... deferred to a v2").

A complication blocks the obvious fix: BC-1 rules have **no per-rule status field**. Applicability is *computed* (glob / trigger-keyword / `always: true`) and does NOT disappear once the builder satisfies the rule — unlike TF-1's PENDING→PASSING rows or WS-1's PENDING→EXERCISED rows, which the strict gate checks for terminal status. So a naive "exit nonzero whenever `critical_applicable > 0`" would make every slice touching an always-on Critical rule permanently un-passable.

## Options considered

1. **Blunt count gate** — `--strict` exits nonzero whenever `summary.critical_applicable > 0` (SC-008's literal suggested approach). Pros: smallest code. Cons: no green path for Critical-touching slices; the nonzero degrades to advisory-to-the-LLM ("address + attest, then proceed"), so an automated/CI consumer is *always* red on Critical slices — it doesn't actually close the false-signal class, it inverts it.
2. **Acknowledgment flag (chosen)** — `--strict` + `--ack-critical <RULE-ID...>`; an applicable Critical rule that is NOT in the ack set becomes a violation (→ exit 1). The builder addresses each Critical rule, documents it in build-log.md (the existing refusal-semantics flow already says "document in build-log.md"), and passes its rule ID. Pros: honest exit code (red until explicit per-rule sign-off); completable; reuses the sibling-audit violations→exit-1 idiom with no new exit branch; mirrors the already-required build-log.md documentation; SMALL. Cons: acknowledgment is an attestation, not proof the rule's check was actually performed (the genuine v2 auto-verification gap remains).
3. **Status-row surface** — add a BC-1 PENDING→ADDRESSED table per applicable Critical rule to milestone.md/mission-brief (TF-1/WS-1 idiom); `--strict` fails on non-ADDRESSED rows. Pros: most convention-consistent with the audit family. Cons: MEDIUM — introduces a persistent per-rule tracking surface to maintain; heavier than the defect warrants; the attestation-vs-proof gap is identical to option 2 (a flipped row is also an attestation).

## Decision

Adopt **option 2**. BC-1 gains an opt-in `--strict` flag and an `--ack-critical <RULE-ID...>` sign-off list (RULE-ID **BCSG-1**, refining BC-1 in place — TFFL-1/ADR-034 "refine-and-mint-a-refinement-ID, supersede nothing" precedent). Under `--strict`, `audit_slice` appends one `BuildCheckViolation(kind="unacknowledged-critical", severity="Critical")` per applicable Critical rule whose `rule_id` is absent from the ack set; `main()`'s existing `return 1 if result.violations else 0` then yields exit 1. Default (no `--strict`) behavior is byte-for-byte unchanged: the gate is opt-in and every current caller is unaffected. `/build-slice` Step 6 opts in, passing `--strict --ack-critical <addressed rule IDs>`.

Acknowledgment is **lenient**: an `--ack-critical` rule ID that is not an applicable Critical rule is ignored (only applicable Critical rules are checked against the set). This avoids coupling the ack list to exact applicability and keeps a stale/extraneous ack harmless; detecting over-acknowledgment / stale-ack drift is explicitly out of scope for v1.

The acknowledgment is an attestation (the builder asserts the Critical rule was addressed), NOT machine proof that the rule's required check ran — executable per-rule auto-verification (running each rule's `Validation hint`) remains the deferred BC-1 v2.

## Consequences

- `/build-slice` Step 6 changes from surface-only to an enforced gate for Critical rules: a Critical-touching slice now fails the audit (exit 1) until the builder acknowledges each applicable Critical rule. This is a methodology behavior change to a mandatory gate → MEPD-1 INCLUDE: the `## v0.75.0` methodology-changelog entry + the **5-part PMI-1 atomic version bump** — the 5 canonical legs are (1) `VERSION`, (2) `plugin.yaml` version, (3) `pyproject.toml [project].version` (PVFS-1), (4) `## v0.75.0` changelog header, (5) installed `~/.claude/ai-sdlc-VERSION` (AVFS-1); the installed `~/.claude/methodology-changelog.md` (MCFS-1) is a SEPARATE forward-sync obligation, NOT a PMI-1 atomic leg — plus the BC-PROJ-10 paired entry-pin pair and shippability row #85.
- **Standing acknowledgment consequence** (per slice-080 /critique B3): BC-PROJ-3 (`architecture/build-checks.md`) and BC-GLOBAL-2 (`~/.claude/build-checks.md`) are both `Severity: Critical` + `Applies to: always: true` git-revert-discipline rules, so they apply to EVERY slice. Wiring `--strict` into Step 6 therefore imposes a standing requirement that every future slice pass `--ack-critical BC-PROJ-3 BC-GLOBAL-2` (plus any slice-specific applicable Critical rules) after attesting each in build-log.md. This is the intended enforcement — these rules genuinely warrant a per-slice confirmation that no destructive revert of uncommitted work occurred — but Step 6 prose must instruct the builder to first enumerate applicable Critical rules (run the audit `--json`) and acknowledge those it has addressed.
- Sole runtime consumer is `skills/build-slice/SKILL.md`; the in-repo edit forward-syncs to the installed copy (OSDG-1 / mini-CAD). No other consumer is affected (`/reflect` references BC-1 only in prose).
- No new tool/skill/agent module → no PMI-1 inventory (BC-PROJ-9) bump; only the version field syncs.
- The attestation-vs-proof gap (v2 auto-verification) is unchanged and remains tracked as the BC-1 v2 limitation.

## Reversibility

**cheap.** Removal = delete the `strict`/`ack_critical` branch in `audit_slice` + the two argparse flags, and revert the Step 6 invocation/prose. No data migration, no persistent state, a single runtime consumer, and the default-off path means even a half-revert leaves all legacy behavior intact. The opt-in design is itself the reversibility guarantee.
