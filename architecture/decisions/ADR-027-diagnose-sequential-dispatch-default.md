---
id: ADR-027
title: /diagnose Step-5 analysis-pass dispatch is sequential-by-default with an explicit --parallel opt-in
date: 2026-05-16
slice: slice-029-make-diagnose-dispatch-sequential
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-027: /diagnose sequential-by-default pass dispatch

## Context

`/diagnose` Step 5 fans out the 10 analysis passes as multiple `Agent`
tool calls in a **single message** (parallel batch). The user reports
this reliably triggers the parallel-spawn permission cascade-failure
tracked as **R-1** ([claude-code #57037](https://github.com/anthropics/claude-code/issues/57037)):
spawned `general-purpose` subagents lose Read/Grep/Bash access, yielding
a degraded `diagnosis.html`. R-1's own fix-candidate #3 already records
that dispatching "only one Agent call at a time ... would also defeat
the parallel-spawn cascade-failure mode."

`/diagnose` is a markdown-as-code skill: the dispatch strategy is prose
in SKILL.md, not compiled code. The per-subagent contract (ADR-001) and
the `write_pass.py` post-processing pipeline are orthogonal to *when*
each subagent is spawned.

## Options considered

1. **Keep parallel default, document the failure** — pros: zero behavior
   change; cons: leaves every default `/diagnose` run exposed to R-1;
   the documentation route was already taken in slice-002 and the user
   is still hitting the failure. Rejected.
2. **Sequential-only (remove parallel entirely)** — pros: simplest, fully
   retires the cascade-failure exposure; cons: permanently forfeits the
   wall-clock speedup for users whose runtime tolerates parallel spawn;
   irreversible loss of a working fast path. Rejected as over-correction.
3. **Sequential-by-default + explicit `--parallel` opt-in** — pros:
   the default path is safe (defeats #57037 cascade for the common case),
   the fast path is preserved for environments that tolerate it, the
   choice is the caller's and explicit; cons: two dispatch branches to
   keep in sync (mitigated — the per-pass contract + model table are
   shared, only the spawn-loop wrapper differs). **Chosen.**

## Decision

`/diagnose` Step-5 analysis-pass dispatch is **sequential by default**:
the orchestrator spawns one `Agent` call, awaits its result, runs the
`write_pass.py` flow + 3-attempt cap for that pass, then spawns the next.
Invoking `/diagnose --parallel` restores the prior single-message
multi-`Agent`-call batch. `--parallel` is position-independent and
optional; it is stripped from args *before* TARGET resolution so a
flag-shaped token never becomes the path and never triggers a
flag-induced abort (the pre-existing bad-path check is unchanged). The
ADR-001 subagent contract, the canonical contract string (CSP-1), the
slice-019 LAYER-EVID-1 N=6 pin, and the COST-1.1 per-pass model routing
are unchanged. Step 5.5 + the Step-5 dispatch sentences are rewritten
**dispatch-mode-aware** (an enumerated, auditable set of edits — not
"byte-unchanged"; per /critique B1), preserving the silent-gap
invariant for both the failed-pass and interrupted-loop sub-cases;
Steps 6 / 6.5 / 7 ordering is unchanged.

## Consequences

- Default `/diagnose` runs no longer dispatch N Agents in one message —
  the R-1 cascade-failure mode is defeated on the default path.
- R-1 transitions `open` → `mitigating` (not `retired`): the
  cwd-mismatch hypothesis (risk-register.md R-1 second root-cause
  candidate) is independent of dispatch sequencing, and the `--parallel`
  opt-in path retains the original parallel-spawn exposure by the
  caller's explicit choice. R-1 gains a structured RR-1 `Mitigation:`
  field citing this slice + ADR-027, stating the residual exposure
  explicitly (no silent over-claim). `retired` would be wrong while
  either condition holds.
- New prose-pins in `tests/skills/diagnose/test_skill_md_pins.py` guard
  the sequential-default, `--parallel` opt-in, flag-strip fail-safe, and
  Step-5.5 dispatch-aware + early-exit behaviors against silent
  regression — **no rule-ID is minted** (per /critique M2, following the
  slice-002 prose-pin-only precedent for the sibling R-1/R-2 surface).
  CSP-1 byte-equality + slice-019 LAYER-EVID-1 N=6 + mini-CAD drift tests
  remain unchanged and must keep passing — they are the rewrite's
  regression guard.
- **methodology-changelog v0.43.0 entry added; NO rule-ID minted**
  (per /critique M2 + /critique-review M2 re-scope, TRI-1-ratified
  2026-05-16 → option B). The unconditional inclusion heuristic
  (`methodology-changelog.md:7`) governs: a default-dispatch behavior
  change qualifies, so a `### Changed`-class v0.43.0 entry is added
  citing this ADR + slice-029 — but no audited rule-ID is minted
  (slice-002 prose-pin-only precedent for the rule-ID half stands; the
  slice-002 *changelog omission* is treated as latent
  under-documentation, not precedent). Consequent PMI-1 4-surface
  lockstep is obligatory and atomic: `VERSION` 0.42.0→0.43.0 +
  `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` +
  `test_methodology_changelog.py` v0.43.0 entry-pin.
- Wall-clock cost: default runs are slower (serial subagents); users who
  want the prior speed opt in with `--parallel`, accepting the R-1 risk
  knowingly.

## Reversibility

**cheap.** The default is a single prose branch in `skills/diagnose/SKILL.md`
(forward-synced to the installed copy). Reverting to parallel-by-default
is a one-paragraph edit plus a prose-pin update — no code, contract,
schema, or data-model change, no consumer migration. Tagged cheap, locked
now because this slice needs it to mitigate the user-blocking R-1
default-path exposure (per /critique M1 + /critique-review M-add-2 —
"mitigate" not "retire", consistent with the rest of the post-M1
corpus; cwd-mismatch hypothesis stays open, `--parallel` retains
exposure).
