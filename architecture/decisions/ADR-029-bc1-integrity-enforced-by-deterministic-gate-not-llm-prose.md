---
id: ADR-029
title: BC-1 vault integrity is enforced by a deterministic downstream gate (BCI-1), not by hardening or inspecting the LLM-executed /reflect Step 5b prose
date: 2026-05-16
slice: slice-030-repair-build-checks-vault-and-harden-shippability
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-029: BC-1 integrity via a deterministic gate, not LLM-prose hardening

> Locked now (was a v1 conditional placeholder). The BLOCKED dual-Critic pass (B2) established the premise as fact, so the decision is determinable at design time.

## Context

R-4's suspected corruptor is `/reflect` Step 5b ("promote a recurring lesson to a build-checks rule"). The v1 mission brief required *inspecting Step 5b to confirm/refute an append-vs-overwrite defect and fixing it at its source*. Both Critic passes verified — independently, against the codebase — that **`/reflect` Step 5b is LLM-executed natural-language prose** (`skills/reflect/SKILL.md` L159–208; L187 = "Append the rule to `architecture/build-checks.md` under the `## Rules` heading"). There is **no promotion function anywhere** in `tools/` or `skills/` (grep-verified). The observed truncation (both files reduced to only the last rule, `## Rules` heading + entire schema preamble destroyed) is inconsistent with an "append under `## Rules`" bug — it is whole-file regeneration by an LLM mis-executing prose, not a deterministic code defect.

Consequences for the slice as originally scoped: "fix at source" has **no source to fix**; a regression test "simulating the promotion function" tests a function that does not exist (a tautology guarding nothing the production path calls).

## Options considered

1. **Harden the Step 5b prose itself** (e.g., more emphatic "do not overwrite" wording) — rejected: an LLM following prose is non-deterministic; stronger wording reduces but cannot *guarantee* the failure mode, and nothing detects a recurrence.
2. **Build a deterministic promotion function and route Step 5b through it** — rejected for this slice: large scope (re-architecting `/reflect`'s promotion), out of R-4's charter, and not required to retire the silent-degradation risk.
3. **Accept that the LLM step is non-deterministic and enforce the *invariant* downstream with a deterministic gate** — **chosen**. Add `tools/build_checks_integrity.py` (BCI-1): deterministic, asserts the live build-checks files match the tracked canonical fixtures on **full per-rule structural identity** `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check` (NEVER rule-ID-set-only — meta-M-add-2). **030A wires two points**: (a) a fail-loud post-write step Step 5b instructs the LLM to run, (b) a non-opt-out `/build-slice` pre-finish gate. A shippability catalog row is **deferred to 030B** (it depends on the shippability-row decoupling, out of 030A scope). The LLM step may still err; the invariant violation is caught loudly and immediately, with an attributed message and a reconstruction path.

## Decision

BC-1 vault integrity is enforced by the deterministic BCI-1 tool downstream of the LLM-executed Step 5b, not by attempting to make the LLM-executed prose itself defect-proof. The invariant BCI-1 enforces is **full per-rule structural identity** — `(rule_id, severity, applies_to, trigger_keywords, trigger_anchors, negative_anchors)` + non-empty `check`, live vs the tracked fixture — **never rule-ID-set-only** (meta-M-add-2: an ID-only or 2-tuple check passes a coverage-degraded file, re-opening R-4's substance). AC-3 is reframed accordingly (deliver + wire BCI-1; document that Step 5b has no deterministic source); AC-4 tests the BCI-1 tool against synthetic intact / 1-rule-truncated / single-corrupted-field / absent-global / empty-global cases. The root-cause finding records: *the corruption mechanism is non-deterministic LLM mis-execution of Step 5b prose; it is not "fixable at source"; the durable control is the BCI-1 full-structural-identity invariant gate.*

## Consequences

- The R-4 risk is retired by *detection of the invariant violation*, not by *prevention at a non-existent source* — the only sound control shape for a non-deterministic step (Hendrickson: you cannot deterministically regression-test an LLM step; test the deterministic artifact downstream).
- `/reflect` Step 5b prose is minimally changed (one fail-loud post-write instruction); its promotion semantics are untouched.
- Pairs with [[ADR-028]]: BCI-1 is simultaneously the Step 5b post-write integrity gate (this ADR) and the fixture↔live divergence detector (ADR-028) — one tool, one invariant, **two wiring points in 030A** (Step5b post-write + non-opt-out `/build-slice` pre-finish); the shippability-catalog-row wiring is deferred to 030B.
- A future slice may still choose Option 2 (deterministic promotion function) if `/reflect` is re-architected; this ADR does not preclude it (reversibility cheap).

## Reversibility

**Cheap.** The decision is "enforce an invariant with a downstream tool." Reverting = remove BCI-1 wiring from Step 5b (one paragraph). No semantics, contract, or data change. Superseded cleanly if a deterministic promotion path is later built.
