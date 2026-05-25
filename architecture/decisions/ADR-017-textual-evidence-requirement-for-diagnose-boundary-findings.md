---
id: ADR-017
title: Textual import-evidence requirement applied at /diagnose 03f-layering pass-template level, not at graphify symbol-resolution level
date: 2026-05-13
slice: slice-019-harden-diagnose-layering-evidence
reversibility: cheap
status: accepted
---

# ADR-017: Textual import-evidence requirement at `/diagnose` pass-template level (LAYER-EVID-1)

## Context

Slice-019 witnessed a HIGH-severity `/diagnose` false-positive finding (`F-LAYER-bca9c001`) that claimed "45 frontend files import `src/workflow/adapters/types.ts` directly, bypassing the HTTP boundary." Manual grep verification disproved the finding: zero frontend files reach into `src/` via relative path or `@/*` alias (the frontend `tsconfig.json` maps `@/*` to `frontend/` root, physically preventing alias-based access). The actual code shape was a parallel type file pattern — `frontend/lib/workflow/types.ts` (537 LOC) hand-maintains a copy of backend domain enums with identical names (`NodeType`, `TaskType`, `AssigneeType`), and 17 frontend files import those enums *from the frontend-local file*, never from the backend.

The most likely root cause is in graphify's symbol-resolution: when two files independently define identically-named symbols (`enum NodeType` in both `src/types.ts` and `frontend/lib/types.ts`), graphify-out apparently collapses them into a single graph node and synthesizes a "cross-file import edge" between callers and the canonical-name node. The `/diagnose` 03f-layering subagent then trusts the graphify edge as authoritative import-evidence and emits a HIGH-severity boundary-violation finding.

A fix is needed because:

1. HIGH-severity false-positives erode user trust in the entire `/diagnose` forensic pass
2. `/slice-candidates` treats confirmed findings as backlog candidates — a false-positive HIGH would seed a fictitious slice
3. Parallel type files (the witnessed shape) are a *common* pattern in monorepos with separate backend + frontend tier (especially TypeScript projects where contract types are duplicated for browser bundling). So the false-positive class will recur on real codebases.

## Options considered

### Option A — Fix at graphify symbol-resolution layer

Modify graphify's code-graph construction (`graphify code .`) to NOT collapse cross-file same-name symbols into a single node. Each definition gets its own node; edges resolve to specific definition sites.

- **Pros**:
  - Root-cause fix; benefits ALL graphify consumers, not just `/diagnose`
  - Symbol-conflation false-positives potentially exist in other consumers (`/architect`, `/validate`, `/discuss`, `/sprint-runner`, `/codebase-analysis`, etc.) — single fix covers all
  - Once shipped, no per-consumer logic needed
- **Cons**:
  - **Broad blast radius** — every consumer's edge interpretation changes. Some consumers may rely on the current collapse behavior for legitimate use cases (e.g., semantic clustering across modules). Untested.
  - **Higher implementation cost** — graphify is editable-installed from `~/.claude/packages/graphify`; changes propagate to all users on next session. A regression in graphify would block all AI SDLC pipeline skills, not just `/diagnose`.
  - **Test surface explosion** — every graphify consumer needs regression coverage to confirm the fix doesn't break them. Slice-019 would balloon from 5 ACs to 15+.
  - **No evidence yet that other consumers are affected** — only `/diagnose` 03f-layering has produced a confirmed false-positive. Fixing all consumers preemptively violates the "build the scary thing first" risk-first principle (Principle 2): we don't have evidence the scary thing exists in other consumers.

### Option B — Fix at `/diagnose` 03f-layering pass-template level (CHOSEN)

Add a "grep-verify the import statement" step to the 03f-layering pass template prose. The subagent, before emitting a HIGH-severity layering/boundary finding, MUST grep the evidence file for an actual textual `import` statement matching the alleged bypass. Zero matches → downgrade to `low` or skip emission.

- **Pros**:
  - **Narrow blast radius** — only `/diagnose` 03f-layering is touched. Other graphify consumers unchanged.
  - **Low implementation cost** — prose changes at 3 surfaces + a regression-fixture integration test + a methodology-changelog entry. ~0.5 day.
  - **Reversibility cheap** — if the rule turns out to over-suppress true-positives (or if graphify is later fixed upstream), the prose can be removed in a follow-on slice without code surgery.
  - **Empirical evidence basis** — the witnessed false-positive (slice-019 F-LAYER-bca9c001) is directly addressed; we're fixing what's broken, not what might be broken.
  - **Aligned with `/diagnose` Hard Rule #5** ("Never invent findings") — the textual-evidence requirement operationalizes that rule for the boundary-finding category.
- **Cons**:
  - **Doesn't fix other consumers** — if graphify symbol-conflation affects `/architect` or `/sprint-runner`, those need their own surgical patches. R-3 tracks this; escalation criteria documented.
  - **Slightly redundant work if Option A is later chosen** — but the prose-level rule remains valid as defense-in-depth even after a graphify-level fix (the textual-evidence requirement is a good practice independent of graphify's symbol resolution quality).
  - **Subagent-prose-heuristic** — the rule is enforced inside the subagent's reasoning loop, not by a separate Python audit module. If the subagent ignores the prose, only manual review catches the regression. Matches slice-017 TPHD-1 / slice-011 RSAD-1 prose-heuristic precedent; a `tools/layer_evid_1_audit.py` v2 is deferred until N≥3 violations recur.

### Option C — Hybrid: Option B now, schedule Option A as a follow-on slice

Apply the pass-level rule first (cheap, fast, witness-driven), then queue a graphify-level investigation in the next 1-2 slices.

- **Pros**: combines short-term safety with long-term root-cause closure
- **Cons**: graphify-level work is currently speculative (no second-witness yet); scheduling it now is over-engineering. Better to wait for `/critic-calibrate` cross-slice pattern mining to confirm the broader-class concern before committing follow-on slice budget.

## Decision

**Option B**: apply the textual import-evidence requirement at the `/diagnose` 03f-layering pass-template level only.

Rationale, in order of weight:

1. **Witness-driven scope**. The witnessed false-positive is in 03f-layering. Other consumers are theoretical. Fixing only the witnessed surface satisfies risk-first ordering.
2. **Reversibility cheap**. Pass-template prose changes can be retired in a future slice if Option A is later chosen. Option A's reversibility is also cheap (graphify code is editable-installed), but Option A's *blast radius* on first ship is the concern, not its reversibility.
3. **R-3 + escalation criteria capture the broader-class risk**. The risk-register entry documents that graphify symbol-conflation may affect other consumers and defines an explicit promotion path: if `/critic-calibrate` flags N≥2 distinct slices with similar phantom-edge issues, a follow-on slice extends LAYER-EVID-1 or fixes graphify upstream. Choice deferred to the moment the evidence basis warrants it.
4. **Defense-in-depth value preserved**. Even if Option A is later chosen, the prose-level rule remains a good practice (the layering subagent SHOULD textually-verify before emitting HIGH findings, regardless of graphify quality). No conflict between A and B.

## Consequences

**Downstream changes within this slice**:

- `skills/diagnose/passes/03f-layering.md` Method gains a new step 4 (textual-import grep-verification); Severity rubric gains a downgrade rule; Anti-patterns gains a negative-pin (see [design.md](../slices/slice-019-harden-diagnose-layering-evidence/design.md) for the mechanical changes)
- `skills/diagnose/SKILL.md` Step 5 gains a one-line cross-reference paragraph to LAYER-EVID-1 (the rule body lives in the pass template; SKILL.md only points at it)
- `methodology-changelog.md` v0.33.0 / LAYER-EVID-1 entry codifies the rule with the canonical phrase `textual import-evidence requirement` pinned at N=3 surfaces (bidirectional in-repo ↔ installed sha256 byte-equal per CAD-1 + mini-CAD precedent)
- Mini-CAD for `/diagnose` (new this slice; first introduction of mini-CAD for the diagnose surface) — bidirectional byte-equality on SKILL.md + 03f-layering.md

**Downstream changes outside this slice**:

- `R-3` added to `architecture/risk-register.md` per RR-1 schema, status `mitigating` (not `retired`) because root cause in graphify is untouched
- Future `/critic-calibrate` runs are explicitly tasked with measuring whether symbol-conflation false-positives recur in other passes / consumers (escalation criteria in R-3 body)

**No changes to**:

- `skills/diagnose/schema/finding.yaml` — the `severity` enum is unchanged; the `evidence[].note` field (already optional in the schema) carries the downgrade rationale when applicable
- ADR-001 (subagent I/O contract) — subagent tool envelope (Read/Grep/Glob within `$TARGET`) is unchanged; the new rule operates within the existing envelope
- Slice-002 canonical contract line (the 12-site byte-equality test continues to pass) — Step 5's NEW paragraph is *additional* prose, not a modification of the canonical contract string

**Future flexibility**:

- If graphify symbol-resolution is later fixed upstream, LAYER-EVID-1 prose can be retired via a follow-on slice (supersede this ADR). The retirement is a prose deletion at 3 surfaces + a methodology-changelog "retired" entry; no code change.
- If LAYER-EVID-1 turns out to over-suppress true-positives (e.g., legitimate cross-tier imports that don't grep-match due to unusual import syntax), the rule can be tightened — e.g., add more import-pattern variants for additional languages (Rust `use`, Go `import`, Java `import`).
- If symbol-conflation false-positives surface in other passes (02-architecture's "where the code disagrees" prose, 03d-half-wired's UI↔backend edges), the rule can be extended to those pass templates via a follow-on slice. The pattern (grep-verify before HIGH emission) generalizes cleanly.

## Reversibility

**Cheap.** The rule lives in pass-template prose at 3 surfaces. Retirement = prose deletion + methodology-changelog "retired" entry + corresponding test-suite cleanup. No code module to deprecate, no API to migrate consumers off, no data migration. Estimated retirement cost: <1 day.

Compare to Option A (graphify-level fix): also reversibility=cheap at the graphify code layer (revert the symbol-resolution code change), but the *blast radius* of either ship-or-revert is broad (all graphify consumers change behavior). Option B's reversibility scope is contained to `/diagnose` 03f-layering.

## Recursive self-application (RSAD-1, slice-011 / Dim 9 sub-clause 6)

The witness investigation in the Context section above — manual-grep disproving F-LAYER-bca9c001 by checking that zero frontend files reach into `src/` via relative path or `@/*` alias — IS the canonical reference instance #1 of LAYER-EVID-1, applied retrospectively to the slice's own witness BEFORE the rule was codified. Slice-019 is the LAYER-EVID-1 codification slice AND is the canonical reference instance #1 at codification time, mirroring slice-015 SCPD-1 + slice-017 TPHD-1 canonical-reference-instance-at-codification-time precedent (slice-017 reflection: *"slice-017 IS canonical reference instance #1 of TPHD-1"* — no "post-codification" qualifier; same shape here). The first post-codification instance (N=2) will land at the next `/diagnose` pass authorship that triggers LAYER-EVID-1 textual-evidence verification per the freshly codified rule.

Per RSAD-1 design-time mode, this ADR's own evidence-base claims should themselves be grep-verifiable. Specifically: the claim "only `03f-layering` emits `category: layering-violation` findings" is empirically true via `grep -h '^- \`category\`:' skills/diagnose/passes/*.md` returning exactly one match at `passes/03f-layering.md:47` (verified 2026-05-13). The slice's `design.md` "Step 5 dispatch enumeration" subsection (added per /critique B1 ACCEPTED-PENDING) surfaces this verification at the design layer; this ADR records it at the decision layer.
