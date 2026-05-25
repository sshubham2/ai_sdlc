---
id: ADR-005
title: Add 9th Critic dimension (Cross-cutting conformance), overriding the 2026-05-10 /critic-calibrate Meta-Critic decline
date: 2026-05-10
slice: slice-006-update-critic-with-cross-cutting-conformance-dimension
reversibility: expensive
status: accepted
---

# ADR-005: Add 9th Critic dimension (Cross-cutting conformance), overriding the 2026-05-10 /critic-calibrate decline

## Context

Per slice-005's reflection (`architecture/slices/archive/slice-005-add-bc-1-keyword-precision/reflection.md` "Critic calibration" section), the **cross-cutting-conformance miss class hardens to N=5 distinct slices with 10 sub-class hits** across slices 001–005:

- slice-001: environmental/runtime conformance (cwd-mismatch tool denial); tooling-conformance (legacy templates contradicting new contract)
- slice-002: methodology-conformance (5-AC TF-1-incompatible); tooling-conformance (RR-1 docstring-vs-regex)
- slice-003: testing-discipline-conformance (TF-1 false-PASS via argparse exit-code-2); tooling-conformance (BC-1 trigger-keyword precision)
- slice-004: testing-discipline-conformance (R-NN vs `\d+` empirical-verification gap, **caught**); language-version-conformance (Python 3.12+ docstring escape-sequence, **missed**)
- slice-005: testing-discipline-conformance (B2 fenced/fence wording, **caught**); algorithm-path-conformance (BC-GLOBAL-1 always-true short-circuit, **missed**)

This is the strongest evidence base in the project for any single Critic-improvement proposal.

The first `/critic-calibrate` run on 2026-05-10 (`architecture/critic-calibration-log.md`, lines 12–60) analyzed the 7 misses, decomposed the super-category into 5 distinct sub-classes (per the table at lines 18–29), and:

- **Promoted** two sub-classes that hit ≥3 distinct slices, as **surgical sub-bullets** under existing dimensions:
  - Tooling-doc-vs-impl parity (3 slices) → Dim 1 4th example bullet (now visible at `agents/critique.md:57`)
  - Methodology-audit conformance (3 slices) → Dim 4 4th main bullet with three sub-sub-bullets including TF-1 row coverage, TF-1 PENDING→WRITTEN-FAILING genuineness, and algorithm-path-conformance with pre-existing branches (now visible at `agents/critique.md:89–92`)
- **Watching but not proposing** the three N=1 sub-classes (algorithm-path-conformance as standalone — folded into Proposal 2 sub-bullet 3; runtime-environment / cwd / tool-permission boundaries; language-version conformance)
- **Explicitly declined** a 9th "Cross-cutting conformance" dimension (lines 41–44) for three reasons:
  1. Both promoted patterns fit existing dimensions naturally (Wiegers/Cockburn for Dim 1 — every claim traces to evidence; Wiegers/Patton for Dim 4 — story-to-design traceability); a 9th dimension would orphan these from their citation framework anchors.
  2. Remaining sub-classes (runtime-environment, language-version, algorithm-path-conformance as standalone) are N=1 anecdote, not pattern.
  3. A "Cross-cutting conformance" 9th dimension would lack a peer-level expert citation, breaking the prompt's "name the framework" specificity rule.

The user is **overriding** this decline. The user's claim is that the Meta-Critic optimally decomposed the evidence within existing dimensions but missed the value of a single named home for the unified pattern — the 10 sub-class hits accumulating across 5 slices is itself the pattern, regardless of which framework anchor each individual sub-class fits. Scattering the cross-cutting concerns across Dim 1, Dim 4, and three "watch but don't propose" entries obscures that future slices' Critics still need a single explicit place to ask "is this slice cross-cutting-conformance failing".

A decision is needed because:

1. The user has invoked `/slice update-critic-with-cross-cutting-conformance-dimension`, explicitly committing to this direction. Without an ADR, the user's decision is undocumented and the prior Meta-Critic decline appears unchallenged in the calibration log.
2. The next `/critic-calibrate` run will look for effectiveness signals; without a record of the override choice and its success criteria, the cross-cutting conformance miss-rate change between slices 6–15 cannot be attributed to any specific intervention.
3. Future maintainers (including the user revisiting in months) will see Dim 9 + the prior decline + the surgical Dim 1/4 sub-bullets and need to understand why the apparent contradiction was deliberately created.

## Options considered

1. **Apply the two surgical proposals only (already done) and skip the 9th dimension** — the path the Meta-Critic recommended.
   - Pros: respects framework-anchor specificity (each surgical sub-bullet sits under its natural framework — Wiegers/Cockburn for Dim 1, Wiegers/Patton for Dim 4); minimal Critic-prompt expansion; the two patterns that hit ≥3 slices ARE addressed; aligns with the existing prompt-design philosophy ("name the framework").
   - Cons: the three N=1 sub-classes (runtime-environment, language-version, algorithm-path-conformance as standalone) have no Critic-prompt home — they're tracked only in `critic-calibration-log.md`'s "Watching but not proposing" table, which the Critic agent does NOT read. Future Critics will continue to miss those classes until they accumulate to N=3 each (potentially 5–15 more slices). The unified pattern is invisible to the per-slice Critic; only the user (reading aggregated lessons) sees it.
   - Verdict: **rejected** — preserves the current invisibility of the unified pattern at the per-slice review surface. The Meta-Critic's reasoning was internally consistent but optimized for citation-anchor purity at the cost of pattern-recognition surface area.

2. **Add a 9th "Cross-cutting conformance" dimension WITH a fabricated peer-level citation** (e.g., assert Cleland-Huang & Gotel's *Software and Systems Traceability* applies, even though their framework is about traceability across SDLC artifacts, not about cross-cutting *concerns* per se).
   - Pros: satisfies the prompt's "name the framework" rule formally; gives the dimension an external anchor for the Critic to retrieve.
   - Cons: dishonest — the citation doesn't actually fit the dimension's content. The Critic at runtime would either (a) reason from the citation and produce findings calibrated to the wrong methodology, or (b) detect the mismatch (the agent's own honesty rule says "if a citation is unfamiliar to you, do not fabricate") and fall back to general principles, defeating the citation's purpose. Either way the prompt is degraded.
   - Verdict: **rejected** — corrupts the citation framework integrity that's the whole point of named-expert grounding.

3. **Add a 9th "Cross-cutting conformance" dimension with the AOP body of work (originating with Kiczales et al. 1997 ECOOP) as the vocabulary anchor + explicit honest-out for the evidence basis**.
   - Pros: Kiczales et al. (1997 ECOOP) introduced the AOP framework whose vocabulary became the canonical home for "cross-cutting concerns" terminology — the noun phrase crystallized as a frozen term-of-art within ~2-3 years of the original paper (the original 1997 paper introduced "aspects" with the verb "cross-cut"; the noun phrase is from subsequent AOP literature). **Per Critic M3 (/critique 2026-05-10), this is a precision tightening of the original "literally his framework's term" claim — the lineage is correct but the original wording overstated.** The honest-out ("no specific evidence-framework cited — operational/empirical accumulation per `architecture/critic-calibration-log.md` 2026-05-10 run, 10 sub-class hits across 5 distinct slices") mirrors Dim 8's existing pattern ("the frame is the live web") and respects the agent's own honesty rule. Threads two of the Meta-Critic's three decline reasons: vocabulary-anchor integrity (Reason 3) is partially addressed; the orphaned-from-framework concern (Reason 1) is acknowledged via cross-references to surgical Dim 1/4 sub-bullets that remain in place. Provides a single named home for all 5 sub-classes (including the three N=1 ones the surgical proposals don't reach).
   - Cons: dimension count grows from 8 → 9, modestly increasing prompt size; cross-references to Dim 1/4 sub-bullets create maintenance dependency (if a future calibration moves the surgical sub-bullets, Dim 9's pointer text becomes stale); the N=1 sub-clauses are still N=1, just visible in a new place.
   - Verdict: **chosen**.

4. **Add a 9th dimension with a pure honest-out** (no Kiczales; just "no specific framework — operational/empirical").
   - Pros: structurally simplest; mirrors Dim 8 most directly.
   - Cons: gives the Critic less retrieval traction. "Cross-cutting concerns" terminology in Dim 9's name without a vocabulary anchor floats free; the Kiczales citation costs nothing (one paper title) and gives the Critic a clear retrieval key for the term.
   - Verdict: **rejected — narrowly** — Option 3 captures all of Option 4's structural benefits while adding a cheap vocabulary anchor.

5. **Defer this decision; let cross-cutting misses accumulate to N=3 each (algorithm-path-conformance as standalone, runtime-environment, language-version), then promote them as surgical sub-bullets at a future /critic-calibrate run**.
   - Pros: respects the Meta-Critic's threshold ("≥3 entries across distinct slices to warrant a proposal") rigorously; minimizes near-term Critic-prompt churn.
   - Cons: leaves the unified pattern invisible at the Critic surface for 5–15 more slices; in the meantime, slices that would benefit from a single cross-cutting check may still miss (as slice-001 missed cwd-mismatch, slice-004 missed Python 3.12+ docstring escapes). The N=10 sub-class hits already represent the strongest evidence base in the project — waiting for further accumulation has diminishing returns.
   - Verdict: **rejected** — the user's pattern-unification claim outweighs the additional N=1→N=3 accumulation discipline for sub-clauses already characterized as cross-cutting at slice-005.

## Decision

Adopt **Option 3**: add a 9th Critic dimension `### 9. Cross-cutting conformance` to `agents/critique.md` with **the AOP body of work (originating with Kiczales et al. 1997 ECOOP) as the vocabulary anchor** AND an **explicit honest-out for the evidence basis** ("no peer-level evidence-framework cited — operational/empirical, per `architecture/critic-calibration-log.md` 2026-05-10 run, 10 sub-class hits across 5 distinct slices"). Body enumerates 5 sub-clauses: three cross-references to surgical sub-bullets at Dim 1 / Dim 4 (which after the slice's first build action — installed→in-repo back-sync per Critic B1 — exist in canonical in-repo source), plus two N=1 standalone sub-clauses (runtime-environment / cwd / tool-permission boundaries; language-version conformance) with concrete examples drawn from slice-001 and slice-004.

Record the override in `architecture/critic-calibration-log.md` as a new dated entry `## User override — 2026-05-10` carrying the override target file:line reference to lines 41–44, the user's pattern-unification rationale, the disposition of each of the Meta-Critic's three decline reasons (partially-acknowledged / acknowledged-with-watch-list / partially-overridden), and a success criterion for the next /critic-calibrate run (the cross-cutting-conformance miss class drops to ≤2 misses across slices 6-15, vs. the current 10-misses-across-5-slices baseline).

Bump methodology version 0.20.0 → 0.21.0 with a new changelog entry carrying rule ID `CCC-1` (Cross-Cutting Conformance dimension v1).

Update the 7 in-repo prose-parity sites where "8 dimensions" appears (`agents/AUTHORING.md`, `agents/critic-calibrate.md`, `skills/critic-calibrate/SKILL.md`, `skills/critique/SKILL.md` — three sites, `plugin.yaml`, `tutorial-site/Hybrid AI SDLC Pipeline.html`) to "9 dimensions". Pin the parity via `tests/methodology/test_critique_agent.py::test_no_in_repo_drift_on_eight_dimensions_phrase`. Do NOT update `methodology-changelog.md` line 191's "the 8 dimensions" reference inside the v0.X.0 DR-1 entry — historical records are append-only.

Re-sync the affected installed copies under `~/.claude/` at /build-slice T-final per the slice-005 out-of-repo forensic-capture pattern.

## Consequences

- **Future `/critique` invocations operate on a 9-dimension Critic**. Slices that conformance-fail to upstream constraints, in-house audits, runtime environment, language version, or pre-existing algorithm branches can now be flagged under a single named dimension rather than requiring the Critic to navigate the surgical Dim 1/4 sub-bullets individually. The Critic's mental model of "what to look for" is unified at the per-slice review surface for the cross-cutting class.
- **The `/critic-calibrate` effectiveness check now has a cleanly attributable intervention to measure** between slices 6–15. Prior to this slice, the 2026-05-10 calibration's two surgical proposals (Dim 1 + Dim 4 sub-bullets) and the watch-listed three N=1 sub-classes were the only interventions; with CCC-1, any change in the cross-cutting miss rate can be partly attributed to the unified-home effect specifically. Success criterion in the calibration-log override entry: ≤2 cross-cutting misses across slices 6-15 (baseline: 10 misses across slices 1-5).
- **The Meta-Critic's three decline reasons remain valid concerns**, partially threaded:
  - **Reason 1 (existing-dimension homes)**: the surgical sub-bullets remain in place; Dim 9 cross-references them rather than duplicating. The orphan risk is mitigated by the cross-reference structure but does add a soft maintenance dependency (if a future calibration restructures Dim 1/4, Dim 9's pointers need updating).
  - **Reason 2 (N=1 sub-clauses being thin)**: runtime-environment and language-version sub-clauses remain N=1 in the body, explicitly labeled as such with promotion criteria. If future slices (6-15) don't accumulate hits in those buckets, a future calibration may demote them out of Dim 9 — that's a clean recovery path.
  - **Reason 3 (citation-anchor purity)**: Kiczales addresses vocabulary; honest-out preserves epistemic accuracy on evidence basis. The dimension is no less rigorous than Dim 8 (which uses the same honest-out structurally); if anything it's more rigorous because Dim 8 has no citation at all while Dim 9 has Kiczales.
- **Critic prompt grows**: roughly 50–80 lines added to `agents/critique.md` (Dim 9 body block) plus 1 row in the Reference frameworks table plus 1 line in the output-format checklist plus 1 word in the line-3 description plus 1 word in the line-47 header. Modest growth; the load-bearing prose-pin tests (existing `test_critique_*` plus new `test_critique_dim_9_*`) lock the structure against drift.
- **Maintenance dependency between in-repo and `~/.claude/` installed copies** for 7 files. Per slice-005's out-of-repo forensic-capture lesson + Critic M2 (/critique 2026-05-10), build-log.md captures **bidirectional** sha256 + line counts (Phase 1 installed→in-repo back-sync of `agents/critique.md` Dim 1/4 surgical sub-bullets; Phase 2 in-repo→installed forward-sync of all 7 files). `tools/install_audit.py`'s canonical-inventory check (per INST-1) ensures full re-installs catch inventory drift but NOT content drift — the structural fix (INST-2 content-equality check, OR `tools/critique_agent_drift_audit.py`, OR updating `/critic-calibrate` skill prose to instruct in-repo edits) is tracked in /reflect Discovered as slice-007+ candidate.
- **`tests/methodology/test_critique_agent.py` test renamed**: `test_critique_lists_eight_dimensions` → `test_critique_lists_nine_dimensions`. Anyone running `pytest -k eight_dimensions` after this slice will get zero tests — acceptable cost for not lying with the function name. **Per Critic m2** (/critique 2026-05-10), the docstring is also updated in lock-step ("all eight review dimensions" → "all nine review dimensions") to avoid prose contradiction.
- **The `/critic-calibrate` skill's prompt at `agents/critic-calibrate.md` line 67 references "Review along these 8 dimensions"** as the section header it reads when mining proposal patterns. After this slice, the section header is "Review along these 9 dimensions"; the skill prose updates in lock-step. If they drift, /critic-calibrate may attempt to read a non-existent header.

## Reversibility

**Expensive — with an irreversible historical-record portion**. Per Critic M5 (/critique 2026-05-10), the original Reversibility section under-counted the irreversible portion of the revert path; the Consequences section's in-context-conditioning paragraph is structurally about reversibility and belongs here for prominence.

### What can be reverted (mechanical edits — ~3-4 hours)

1. Remove the Dim 9 body block from `agents/critique.md` + revert the line-3 description + revert the line-47 header + remove the Reference frameworks table row + remove the output-format checklist row (5 surface edits in 1 file).
2. Revert the 7 in-repo prose-parity sites back from "9 dimensions" → "8 dimensions".
3. Append a new methodology-changelog entry (e.g., v0.22.0) documenting the CCC-1 retirement under `### Retired`; bump VERSION.
4. Append a new `architecture/critic-calibration-log.md` entry documenting the user-override-of-the-override (recursive Meta-Critic intervention).
5. Remove the 4-5 new prose-pin tests + revert the rename `test_critique_lists_nine_dimensions` → `test_critique_lists_eight_dimensions` + remove `test_no_in_repo_drift_on_eight_dimensions_phrase` + remove `test_critique_dim_9_cross_references_resolve`.
6. Re-sync the `~/.claude/` installed copies (7 files).
7. Document the reversal rationale in a new ADR supersedes ADR-005 (status: superseded).

Plus the cognitive cost of re-justifying the Critic-prompt structure in a third ADR.

### Items that cannot be reverted (irreversible portion)

- **Archived `critique.md` files filed under Dim 9 between slices 6-N stay filed under Dim 9** — historical record. Removing Dim 9 from the agent prompt does NOT re-classify findings already produced under it. Future readers of those archived critiques will see Dim 9 in the dimension checklists and need to understand it from this ADR (which by then would be superseded but still present).
- **Calibration-log entries are append-only** — the user-override entry written in this slice (per AC #5), and any subsequent /critic-calibrate analyses that mined Dim 9 patterns, cannot be redacted. The audit trail grows monotonically.
- **Cumulative slice-006-N critique outputs influence pattern-recognition at future calibration runs** irrespective of revert. The Critic at slice-N+1 (post-revert) does not have access to the prior 9-dim Critic's outputs, but the user reading aggregated lessons + the maintainer designing the next /critic-calibrate run does — the conceptual frame "cross-cutting conformance as a unified dimension" persists in the project's collective methodology even after the dimension itself is removed from the prompt.
- **Critic-behavior changes accumulate via prompt-cache + in-context-conditioning effects** that are hard to A/B test cleanly. The Critic agent prompt itself is load-bearing across all future slices' /critique runs; reverting affects the per-slice review surface uniformly. The post-revert Critic-behavior baseline is NOT identical to the pre-slice-006 baseline — the revert ADR + the second calibration-log entry ARE in-context for any operator (human or LLM) reading the methodology vault.

### Cost summary

The dimension addition is *structurally additive* (existing 8 dimensions remain unchanged; back-synced Dim 1/4 surgical sub-bullets remain unchanged after revert because they're orthogonal to Dim 9), so the mechanical revert path has no merge complexity. The expense is in (a) methodology-process discipline (write the third ADR, update the calibration log a third time, revert prose across 8+ files) AND (b) the irreversible portion above. A future "should we revert?" analysis must factor (b) into the cost — once Dim 9 has classified findings across, say, 5+ slices, the irreversible portion makes net-zero impossible.

If the next /critic-calibrate run (per the success criterion: ≤2 cross-cutting misses across slices 6-15) demonstrates the dimension *failed*, the right disposition may not be revert but **refinement** — tighten Dim 9's wording / examples / cross-references rather than removing the dimension. Refinement is cheaper AND respects the irreversible portion. Revert is the option-of-last-resort.
