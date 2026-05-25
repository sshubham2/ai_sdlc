# Critique: Slice 029 make-diagnose-dispatch-sequential

**Critic reviewed**: mission-brief.md, design.md, ADR-027
**Date**: 2026-05-16
**Result**: NEEDS-FIXES

## Summary

The core decision (sequential-by-default + `--parallel` opt-in) is well-founded — web evidence confirms claude-code #57037 cascades on multi-Agent-in-one-message and that sequential-in-separate-turns succeeds. But the design commits the slice-022 self-violation defect class on three fronts: it claims "Step 5.5 / post-subagent flow byte-unchanged" while the sequential rewrite makes Step 5.5's own opening clause ("After the parallel batch completes") factually false on the default path; it omits the slice-019 LAYER-EVID-1 N=6 byte-equality pin and the Step-5 cross-reference paragraph that sit inside the exact region being rewritten; and the `--parallel`-only invocation collides with the existing `${1:-$PWD}` Step-1 parsing in a way that aborts rather than fail-safes.

## Findings

### Blockers (must address before /build-slice)

#### B1: Step 5.5 opening clause is dispatch-coupled prose the design claims is "byte-unchanged"
- **Claim under review**: design.md verification plan #3 "post-subagent flow text byte-unchanged except dispatch sequencing"; What's-new "Steps 5.5/6/6.5/7 unchanged"; mission-brief must-not-defer "Step 5.5 silent-gap detection still functions in sequential mode."
- **Issue**: SKILL.md:191 "After the parallel batch completes…"; :187 "Wait for all 10 to finish… before Step 6"; :170 "process them as they finish — order doesn't matter" are dispatch-coupled and become false/contradictory on the sequential default. A methodology-surface slice drifting the Step 5.5 contract it pledges to protect (slice-022 self-violation).
- **Evidence**: SKILL.md:170,187,191; design.md What's-reused; mission-brief must-not-defer #2.
- **Proposed fix**: Enumerate the dispatch-coupled sentences; rewrite them dispatch-mode-aware. Replace "byte-unchanged" with a precise list of intentional edits. Re-express Step 5.5 silent-gap so "do not proceed with gaps" still holds when the sequential loop exits early (passes unspawned, not just failed).
- **Builder draft**: ACCEPTED-FIXED at design.md (verification plan #3 + What's-new rewritten to enumerate dispatch-coupled edits + early-exit silent-gap handling).

#### B2: design.md omits the slice-019 LAYER-EVID-1 N=6 byte-equality pin and Step-5 cross-reference paragraph, both inside the rewrite blast radius
- **Claim under review**: design.md "What's reused" omits LAYER-EVID-1 / the slice-019 N=6 pin.
- **Issue**: SKILL.md:164–166 carries the byte-locked phrase `textual import-evidence requirement`, pinned across N=6 surfaces (`test_skill_md_pins.py:262–374`), and sits *inside Step 5* — exactly the region being rewritten. A restructure that relocates/reflows it silently breaks the N=6 pin + mini-CAD installed-copy byte-equality.
- **Evidence**: SKILL.md:164–166; test_skill_md_pins.py:262–374; aggregated lesson slice-019 N-surface pin.
- **Proposed fix**: Add LAYER-EVID-1/N=6 pin to "What's reused" with explicit "paragraph preserved verbatim + correctly positioned" statement; mid-slice smoke gate must name `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` specifically.
- **Builder draft**: ACCEPTED-FIXED at design.md What's-reused + mission-brief mid-slice smoke gate (N=6 pin test named explicitly).

#### B3: `--parallel`-only invocation collides with existing `${1:-$PWD}` Step-1 parsing — aborts instead of fail-safing
- **Claim under review**: mission-brief AC #2 / must-not-defer "Unknown/garbled args fail safe… no mid-run error-out"; design.md "--parallel is position-independent… everything else is the TARGET path."
- **Issue**: SKILL.md:28 `TARGET="${1:-$PWD}"` + :25/:41 abort-on-missing. `/diagnose --parallel` (no path) → `TARGET=--parallel` → "TARGET does not exist: --parallel" abort — the exact mid-run error-out the must-not-defer forbids, on the *intended* opt-in path.
- **Evidence**: SKILL.md:21–30,40–42; mission-brief AC #2, must-not-defer #3.
- **Proposed fix**: design.md must specify the exact Step-1 bash rewrite (strip `--parallel` from args *before* TARGET resolution, then `${1:-$PWD}` on the residue). Add AC verification: `/diagnose --parallel` (no path) → TARGET=`$PWD` sequential, never abort; typo `--paralll` → `$PWD` sequential.
- **Builder draft**: ACCEPTED-FIXED at design.md (exact Step-1 flag-strip rewrite specified) + mission-brief (verification rows added).

### Majors (address this slice)

#### M1: Internal inconsistency — "Risk retired: R-1" (mission-brief header) vs "R-1 → mitigating" (design.md / ADR-027)
- **Claim under review**: mission-brief header "Risk retired: R-1"; design.md/ADR-027 "R-1 → mitigating".
- **Issue**: `mitigating` is correct (sequential defeats only the #57037 parallel-spawn hypothesis; cwd-mismatch hypothesis at risk-register.md:21 independent + untouched; `--parallel` retains full exposure). The header's "retired" framing + AC #5 "→ mitigating or retired" risks a silent over-claim.
- **Evidence**: mission-brief header + AC #5; risk-register.md:21,23–26; ADR-027 consequences.
- **Proposed fix**: mission-brief header → "Risk mitigated (not retired): R-1"; lock AC #5 to "→ mitigating" (drop "or retired"); R-1 rationale must state cwd-mismatch remains open + `--parallel` retains exposure.
- **Builder draft**: ACCEPTED-FIXED at mission-brief (header + AC #5) + design.md (R-1 rationale spelled out).

#### M2: DSEQ-1 rule-ID + changelog v0.43.0 is speculative ceremony relative to the slice-002 prose-pin-only precedent
- **Claim under review**: design.md open-note (Builder explicitly requested this judgment); What's-new "methodology-changelog.md v0.43.0: DSEQ-1 rule entry".
- **Issue**: slice-002 (sibling R-1/R-2 surface) used prose-pins + *no* rule-ID. DSEQ-1 has no enforcing audit (unlike BC-1/RR-1/CSP-1). Minting a rule-ID + version bump forces PMI-1 lockstep (VERSION/ai-sdlc-VERSION/plugin.yaml + changelog entry-pin tests + shippability) — four forward-sync surfaces flagged as silent-breakage hotspots — buying nothing the prose-pin doesn't.
- **Evidence**: design.md open-note; slice-002 precedent; aggregated lessons (PMI-1 lockstep + N=5 propagation hazards).
- **Proposed fix**: Drop DSEQ-1 + v0.43.0 bump; follow slice-002 prose-pin + ADR-only precedent.
- **Builder draft**: ACCEPTED-FIXED at design.md + ADR-027 (DSEQ-1 rule-ID + v0.43.0 changelog entry + PMI-1 version bump dropped; behavior guarded by prose-pins + ADR-027 only, exactly mirroring slice-002). **User judgment call flagged for TRI-1**: if the changelog discoverability is wanted, the user may override to keep a v0.43.0 entry (accepting the PMI-1 lockstep cost) — the design itself solicited this decision.

#### M3: AC #4(c) byte-stability claim is imprecise — contract subsection single-source vs duplicated in `--parallel` branch
- **Claim under review**: mission-brief AC #4(c); design.md "--parallel branch preserves the prior batch verbatim".
- **Issue**: If the `--parallel` branch re-emits the contract subsection (SKILL.md:149–162, carrying the canonical string at :162), it's a latent CSP-1 maintenance hazard (future edit touches one copy). Design doesn't state whether the branch reuses the single subsection or re-emits it.
- **Evidence**: SKILL.md:158–162; test_skill_md_pins.py:377–399.
- **Proposed fix**: design.md must assert the contract subsection is a *single shared block* referenced by both branches (same single-source rule already applied to the COST-1.1 table), not duplicated.
- **Builder draft**: ACCEPTED-FIXED at design.md (single-source contract subsection asserted).

### Minors (log; address if cheap)

#### m1: Shippability propagation row must survive the slice-024 backtick-strip + count-agnostic + real-command lessons
- **Issue**: shippability rows carry an executable Command run verbatim at /validate-slice. The new row needs a real pytest selector, not prose.
- **Proposed fix**: design.md specifies the exact Command cell (absolute `$PY` path, `--no-header -q`, real selector).
- **Builder draft**: ACCEPTED-FIXED at design.md (exact Command cell specified).

#### m2: ADR-027 says "R-1 open→mitigating" but risk-register.md R-1 has no Mitigation field
- **Issue**: RR-1 accepts optional `Mitigation`/`Notes`. Status flip without a structured `Mitigation:` field leaves "no silent retire" weakly satisfied.
- **Proposed fix**: design.md specifies R-1 gains an RR-1-recognized `Mitigation:` field citing slice-029 + ADR-027.
- **Builder draft**: ACCEPTED-FIXED at design.md (R-1 Mitigation: field specified).

## Dimensions checked
- [x] Unfounded assumptions — B1, B3 (verified against actual SKILL.md source)
- [x] Missing edge cases — B3 (`--parallel`-only = empty-path edge); sequential loop early-exit vs Step 5.5 (B1 fix)
- [x] Over-engineering — M2 (DSEQ-1 + v0.43.0 ceremony vs slice-002 precedent)
- [x] Under-engineering — B3 (fail-safe unreconciled with `${1:-$PWD}`); m1 (shippability prose vs real command)
- [x] Contract gaps — M3 (`--parallel` position-independence vs `${1:-$PWD}`; contract-subsection single-source)
- [x] Security — none (/diagnose local read-only, no auth/data surface; ADR-027 N/A correct)
- [x] Drift from vault — M1, B2, m2; ADR-027 correctly orthogonal to ADR-001
- [x] Web-known issues — confirmed #57037 (v2.1.126) cascade + one-at-a-time success; #2148, #5465 related; #57037 still open ⇒ reinforces `mitigating` not `retired`
- [x] Cross-cutting conformance — B1/B2 = slice-022 self-violation (Step-5 rewrite vs unchanged-Step-5.5 claim; LAYER-EVID-1 N=6 pin in blast radius); SKILL.md:170 "order doesn't matter" contradicts the new ordered loop (B1)

Sources:
- https://github.com/anthropics/claude-code/issues/57037
- https://github.com/anthropics/claude-code/issues/2148
- https://github.com/anthropics/claude-code/issues/5465
- https://claudefa.st/blog/guide/agents/sub-agent-best-practices

## Triage

**Triaged by**: user
**Date**: 2026-05-16
**Final verdict**: CLEAN

Reconciles BOTH passes (first Critic critique.md + meta-Critic critique-review.md, dual-review verdict EXTEND). All dispositions ACCEPTED-FIXED and applied to design.md / mission-brief.md / ADR-027 / critique-review.md before this verdict. Two governance/scoping points were user-ratified at TRI-1: M2 → option (B) (v0.43.0 changelog entry, no rule-ID, PMI-1 lockstep); M-add-1 → option (B) (unknown `--`-flags warned+ignored, never abort).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | design.md "What's new" dispatch-coupled prose inventory + early-exit clause; mission-brief verification #3 reworded byte-unchanged→enumerated-auditable |
| B2 | Blocker  | ACCEPTED-FIXED | design.md "What's reused" adds slice-019 LAYER-EVID-1 N=6 (verbatim-preserve+correct-position); smoke gate names `test_textual_evidence_rule_byte_equal_across_n_3_surfaces` |
| B3 | Blocker  | ACCEPTED-FIXED | design.md exact Step-1 flag-strip-before-TARGET bash (3-arm `case`, strengthened to M-add-1 option B); mission-brief AC2 verification rows |
| M1 | Major    | ACCEPTED-FIXED | mission-brief header → "Risk mitigated (not retired)"; AC5 locked → mitigating; R-1 residual-exposure rationale; ADR-027 aligned (+M-add-2) |
| M2 | Major    | ACCEPTED-FIXED | DR-1 re-scope; TRI-1 user decision = option (B): NO rule-ID + a `### Changed` v0.43.0 changelog entry + atomic PMI-1 0.42.0→0.43.0 lockstep (inclusion heuristic honored; slice-002 changelog-omission treated as latent under-doc) |
| M3 | Major    | ACCEPTED-FIXED | design.md single-shared-contract-subsection no-duplication invariant (same single-source rule as COST-1.1 table) |
| m1 | Minor    | ACCEPTED-FIXED | design.md real runnable Command cell (further refined by M-add-4 to row-1 file-selector form) |
| m2 | Minor    | ACCEPTED-FIXED | design.md specifies R-1 gains a structured RR-1 `Mitigation:` field citing slice-029 + ADR-027 |
| M-add-1 | Major (meta) | ACCEPTED-FIXED | design/mission-brief prose corrected `:25`→`:41` (cd-fails abort); Git-Bash dry-run obligation added to build-log; TRI-1 option (B): unknown `--`-flags warned+ignored, flag typo never aborts |
| M-add-2 | Major (meta) | ACCEPTED-FIXED | ADR-027 Reversibility "retire the user-blocking R-1 exposure" → "mitigate … default-path exposure" (slice-022 self-violation recurrence closed) |
| M-add-3 | Minor (meta) | ACCEPTED-FIXED | design.md Components-touched reworded: step *sequence* unchanged vs Step-5.5 *prose* rewritten dispatch-mode-aware |
| M-add-4 | Minor (meta) | ACCEPTED-FIXED | shippability Command cell switched to row-1 file-selector form (`test_skill_md_pins.py --no-header -q`, no `-k`) — avoids the unexercised slice-024 backtick-strip footgun |

> M2 was raised SUSPICIOUS-partial by the meta-Critic: the rule-ID-drop half was sound, the changelog-omission half conflicted with the unconditional inclusion heuristic. Per TRI-1 the user chose option (B) — honor the heuristic (add the entry, no rule-ID). Recorded ACCEPTED-FIXED because the design + ADR-027 + mission-brief now reflect the ratified shape; the rule-ID-less-`### Changed`-entry vs PMI-1/changelog-audit interaction is a flagged build-slice mechanical risk (mid-slice smoke gate DEVIATION path), not an unresolved triage item.
