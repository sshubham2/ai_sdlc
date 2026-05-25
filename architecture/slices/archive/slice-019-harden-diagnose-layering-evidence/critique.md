# Critique: Slice 019 harden-diagnose-layering-evidence

**Critic reviewed**: mission-brief.md, design.md, ADR-017
**Date**: 2026-05-13
**Result**: NEEDS-FIXES

## Summary

Witness-driven scope and rule design are sound; ADR-017 makes the Option-A-vs-B trade-off explicit and reversibility-cheap. However, the Critic surfaced three load-bearing under-engineering findings (must-not-defer #1 propagation gap, grep-pattern coverage gap, mini-CAD dual-file TF-1 coverage gap) plus four majors clustering around recursive self-application discipline (RSAD-1 design-time mode) and slice-018 sibling-test scoping inheritance. The Critic correctly identified that the slice codifies LAYER-EVID-1 (textual import-evidence requirement) but its own design.md makes import-class claims without surfacing the grep-verification — exactly the discipline it codifies, applied to the slice itself.

## Findings

### Blockers (must address before /build-slice)

#### B1: design.md scopes the rule to 03f only; mission-brief AC #1 + must-not-defer #1 promise propagation to ALL passes that emit boundary / cross-tier / import-violation findings

- **Claim under review**: mission-brief AC #1: *"`/diagnose` layering pass template (and any sibling pass that emits boundary / cross-tier / import-violation findings — at minimum the layering pass; per Step 5 dispatch enumeration)"*; must-not-defer #1 forecloses the "only 03f" interpretation. design.md "What's new" Surface 1 lists only `skills/diagnose/passes/03f-layering.md`.
- **Issue**: Per Wiegers AC-to-design traceability — every AC must have a design element delivering it. Critic enumerated four sibling passes that could legitimately describe parallel-type-file / cross-tier shapes: `02-architecture.md:21` ("Where the code disagrees with itself"), `03b-duplicates.md` (semantic duplicates may cite phantom import edges), `03d-half-wired.md` (UI↔backend disconnects), `03e-contradictions.md:28-36` (graphify shortest_path consumes symbol-conflated edges).
- **Evidence**: design.md "What's new" Surface 1 scope; mission-brief must-not-defer #1; `passes/02-architecture.md:21`; `passes/03e-contradictions.md:28-36`.
- **Proposed fix**: Add to design.md a NEW subsection **"Step 5 dispatch enumeration (per AC #1 + must-not-defer #1)"** that enumerates all 11 passes from `skills/diagnose/SKILL.md:124-135` dispatch table; for each pass, surface the textual grep-verification of whether its Method emits boundary / cross-tier / import-violation findings; explicitly DECIDE per pass — apply LAYER-EVID-1 (with prose edit) or NOT (with rationale grounded in finding category + Block-contents emission shape).
- **Builder draft**: ACCEPTED-PENDING — extend design.md with the Step 5 dispatch enumeration subsection at /build-slice Phase 1. Investigation at /design-slice time concluded only 03f emits `category: layering-violation` findings (per `passes/03f-layering.md:13,47` + `passes/02-architecture.md:69-71` `findings: []` + `schema/finding.yaml:21-32` category enum). Per-pass decisions: **03f-layering** apply rule (witness pass); **02-architecture** NO — emits `findings: []` per Block contents, prose-only narrative; **03b-duplicates** NO — flags shape-equivalence not import-bypass, evidence shape differs; **03d-half-wired** NO — UI↔backend disconnect category is data-flow not import-boundary; **03e-contradictions** NO — uses graphify shortest_path but for assumption-divergence category, not import-violation. **Escalation path**: R-3 explicit escalation criteria — if `/critic-calibrate` flags symbol-conflation false-positives in ANY of these passes (N≥2 distinct slices), extend LAYER-EVID-1 via follow-on slice. Apply enumeration with grep-evidence pin per pass.

#### B2: grep-pattern under-specifies ES-module / re-export / multi-line / alias-aware import variants — false-negative would cause TRUE-positive HIGH boundary findings to be incorrectly downgraded to `low`

- **Claim under review**: design.md "Modified — `skills/diagnose/passes/03f-layering.md`" Method NEW step 4 grep patterns: `^\s*import\s+.*from\s+['"]<bypassed-path>['"]` + `require\(...\)` + dynamic `import\(...\)` + Python `from`/`import` only.
- **Issue**: Per OWASP/secure-defaults + Wiegers traceability — the rule's downgrade decision turns on grep-match; false negatives in the grep are load-bearing. Per [TypeScript Documentation - Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html) 2026-05-13, the regex misses ≥3 documented TS import variants: (1) **side-effect import** `import "..."` — no `from`; current regex requires `from`. (2) **re-exports** `export { X } from "..."`, `export * from "..."`, `export type { X } from "..."` — uses `export` not `import`; the phantom-graphify-edge problem applies symmetrically. (3) **multi-line imports** `import {\n  NodeType,\n} from "..."` — `.*` does not span newlines without `re.DOTALL` / ripgrep `--multiline`. (4) **alias-aware grep**: the witnessed F-LAYER-bca9c001 used `@/*` alias; if `<bypassed-path>` is repo-relative AND the codebase has tsconfig.json paths/baseUrl, grep MUST try BOTH the repo-relative path AND any alias that resolves to it, else the rule fails closed on the very alias-pattern that produced the witness.
- **Evidence**: design.md Method step 4; [TypeScript: Documentation - Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html); [TypeScript and ES6 import syntax - JDriven Blog](https://jdriven.com/blog/2017/06/typescript-and-es6-import-syntax); mission-brief Intent paragraph 1 (witness used `@/*` alias).
- **Proposed fix**: Tighten Method step 4 to enumerate (i) all 5 TS variants (`import X from`, `import { X } from`, `import * as X from`, `import type { X } from`, side-effect `import "<path>"`); (ii) re-export variants (`export { X } from`, `export * from`, `export type { X } from`); (iii) multi-line semantics (`re.DOTALL` or ripgrep `--multiline`); (iv) alias-aware grep — if `<bypassed-path>` is repo-relative AND tsconfig.json/jsconfig.json has paths/baseUrl, grep BOTH forms; (v) concrete non-TS fallback examples (Rust `use\s+.*<module>`, Go `import\s+["']<path>["']`, Java `import\s+<fqn>;`) replacing the vague "import-keyword neighbor" wording.
- **Builder draft**: ACCEPTED-PENDING — apply at /build-slice Phase 1 (pass-template prose). Also update test-local helper `_grep_textual_import` to handle these variants AND extend regression fixture(s) to include alias-based imports + a side-effect import case + a multi-line import case. Per TPHD-1 sub-mode (a): mission-brief TF-1 plan may gain additional fixture-test rows if Critic-fix-prose requires; harmonize in same fix block.

#### B3: TF-1 row coverage gap — design.md asserts mini-CAD covers BOTH SKILL.md AND passes/03f-layering.md but mission-brief TF-1 plan has only ONE drift-test row scoped semantically to SKILL.md

- **Claim under review**: design.md "What's new": *"first introduction of mini-CAD for `/diagnose`; bidirectional byte-equality on SKILL.md AND passes/03f-layering.md"*. Mission-brief TF-1 plan AC #1 row 4: `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` (single function name semantically scoped to SKILL.md).
- **Issue**: Per Wiegers AC-to-design traceability + RPCD-1 sub-mode (c) NEW-anchor sibling-grep audit (methodology-changelog v0.31.0) + slice-018 cleanup-slice TF-1 row enumeration discipline (DEVIATION-2 N=1): a single test name pinning two files is not the slice-007 CAD-1 / slice-010 mini-CAD convention. CAD-1 + slice-010 mini-CAD both use single-file → single-test mapping.
- **Evidence**: mission-brief TF-1 plan AC #1; design.md "What's new"; `tests/methodology/test_slice_skill_drift.py:35` (slice-010 mini-CAD — single-file convention); `tests/methodology/test_critique_agent_drift.py` (slice-007 CAD-1 — same).
- **Proposed fix**: Split into two TF-1 plan rows (Path A, recommended per single-file convention): (a) `test_in_repo_and_installed_diagnose_skill_md_are_content_equal` + (b) `test_in_repo_and_installed_diagnose_03f_layering_md_are_content_equal`. Per TPHD-1 sub-mode (a): harmonize mission-brief.md TF-1 plan AND design.md "What's new" claim in same fix block.
- **Builder draft**: ACCEPTED-PENDING — Path A split at /build-slice Phase 1. Per TPHD-1 sub-mode (a): apply both edits (mission-brief TF-1 plan + design.md "What's new" `tests/skills/diagnose/test_diagnose_skill_drift.py` test enumeration) in SAME fix block.

### Majors (address this slice)

#### M1: Wiring matrix "Zero rows" is correct but test-local helper `_grep_textual_import` re-implements rule logic; drift between test helper and subagent runtime grep is not pinned

- **Claim under review**: design.md Wiring matrix zero-row entry; design.md "Rationale for test-local helper" defers tools/ promotion to N≥3.
- **Issue**: Per Newman / Fowler + ADR-017 Cons bullet ("Subagent-prose-heuristic"): the test verifies the rule's logic via a helper that re-implements the grep, but the subagent at runtime uses its own Grep tool with its own interpretation of bypassed-path / alias / pattern. The witnessed F-LAYER-bca9c001 IS the rule-prose-vs-runtime drift class. Slice ships defense at prose-pin layer + test-fixture layer, but the test does not exercise the subagent's runtime grep.
- **Evidence**: design.md "Modified — Components" + ADR-017 Cons bullet (acknowledges gap; defers v2 audit per TPHD-1 / RSAD-1 / RPCD-1 N≥3 precedent).
- **Proposed fix**: design.md gains "Test-local helper rationale + drift risk" paragraph naming the limitation. Pass-template Method step 4 prose embeds the EXACT same regex strings (as literal-string blocks) that `_grep_textual_import` uses, so a subagent reading the template sees the same regex the test verifies. This is prose-pin equivalent of CAD-1 byte-equality at the rule-content level.
- **Builder draft**: ACCEPTED-PENDING — apply at /build-slice Phase 1. Cross-byte-equality prose-pin test deferred to v2 per TPHD-1 / RSAD-1 / RPCD-1 N≥3-violations-deferral precedent — visual byte-equality of literal regex strings between pass-template prose and test-helper constants is sufficient at v1; promote to enforced byte-equality if drift surfaces.

#### M2: ADR-017 should explicitly name the slice's own witness verification as canonical reference instance #1 of LAYER-EVID-1 (RSAD-1 design-time mode)

- **Claim under review**: ADR-017 Context paragraph 2 ("Manual grep verification disproved the finding...") — implicit canonical reference instance.
- **Issue**: Per RSAD-1 (slice-011 / Dim 9 sub-clause 6) recursive-self-application design-time-mode + slice-015 SCPD-1 + slice-017 TPHD-1 canonical-reference-instance precedent: codification slices typically name the canonical reference instance #1 explicitly in design.md / ADR. ADR-017's witness verification IS the canonical instance but is not named.
- **Evidence**: ADR-017 Context; slice-011 ADR-010; slice-015/017 canonical-reference-instance N=1 standalone precedent.
- **Proposed fix**: Add 1-2 sentence "Recursive self-application" paragraph to ADR-017.
- **Builder draft**: ACCEPTED-FIXED — applied inline at `architecture/decisions/ADR-017-*.md`. New section "## Recursive self-application (RSAD-1, slice-011 / Dim 9 sub-clause 6)" added after "## Reversibility"; names slice-019 as standalone canonical reference instance #1 of LAYER-EVID-1 at N=1 standalone post-codification. Includes the grep-verification pin for the design.md "only 03f emits layering-violation" claim (verified 2026-05-13).

#### M3: design.md claim "only 03f emits `category: layering-violation`" is grep-verifiable but verification not surfaced (RSAD-1 design-time)

- **Claim under review**: design.md "What's new" + "Components touched" implicit assumption that only 03f-layering is affected. Per RSAD-1 design-time mode, the slice that codifies LAYER-EVID-1 should pin its own import-class claims the way the rule requires.
- **Issue**: Same as B1 in shape — the missing per-pass enumeration is the structural fix; surfacing the grep-verification is the recursive-self-application application.
- **Evidence**: Aggregated-lessons RSAD-1 probe; design.md "What's new" implicit scope.
- **Proposed fix**: One-line evidence pin in design.md: *"03f-layering is the sole emitter of `category: layering-violation` per `grep -h '^- \`category\`:' skills/diagnose/passes/*.md`. The grep returns exactly one match in `passes/03f-layering.md:47`. Verified 2026-05-13."*
- **Builder draft**: ACCEPTED-PENDING — folded into B1's Step 5 dispatch enumeration subsection (the enumeration naturally surfaces this verification per-pass). Apply at /build-slice Phase 1 in same fix block as B1.

#### M4: v0.33.0 entry-pin tests must inherit slice-018 sibling-test scoping discipline (`_extract_v033_body` helper); mission-brief TF-1 plan does not pin this

- **Claim under review**: mission-brief TF-1 plan rows for AC #3: `test_v_0_33_0_layer_evid_1_entry_present_in_repo_and_installed` + `test_v_0_33_0_layer_evid_1_entry_names_textual_import_evidence_canonical_phrase`. Aggregated-lessons watch-list: "test-scoping-flaw-inherited-across-codification-slice-siblings."
- **Issue**: Per slice-018 reflection — global-substring scoping silently masks false-positives. Slice-019's NEW entry-pin tests will need to scope to v0.33.0 entry body via `_extract_v033_body` helper (between `## v0.33.0` and `## v0.32.0` boundaries). Mission-brief TF-1 plan does NOT explicitly require this.
- **Evidence**: slice-018 reflection / shippability row 18; `tests/methodology/test_methodology_changelog.py:942-1000` (slice-018 canonical `_extract_v031_body`); aggregated-lessons explicit watch-list.
- **Proposed fix**: Add to design.md "test-scoping inheritance" paragraph stating slice-019's two new entry-pin tests + bidirectional-installed sibling MUST scope via `_extract_v033_body(content) -> str` helper (between `## v0.33.0` and `## v0.32.0` boundaries) and reference `v033_body` not raw `content`. Add NEW regression test row `test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body` per slice-018 canonical L1010-1060 pattern. Update mission-brief TF-1 plan to include this regression row (TPHD-1 sub-mode (a)).
- **Builder draft**: ACCEPTED-PENDING — apply at /build-slice Phase 1-2. Per TPHD-1 sub-mode (a): mission-brief TF-1 plan + design.md "test-scoping inheritance" paragraph harmonized in same fix block. Regression test pattern mirrors slice-018 L1010-1060 at PATTERN level, NOT literal-code level (per slice-018 /critique-review m-add-2 Audit 3 refinement).

### Minors (log; address if cheap)

#### m1: mission-brief uses "false-positive" (hyphenated); BC-PROJ-2 negative-anchor word-boundary distinction — Phase 4 self-application audit dry-run recommended

- **Claim under review**: mission-brief + design.md use "false-positive" repeatedly; `architecture/build-checks.md:35` BC-PROJ-2 negative-anchor list contains `false positive` (no hyphen). Word-boundary regex `\bfalse positive\b` doesn't match `\bfalse-positive\b`. BC-PROJ-2 positive Trigger anchors `fence, code-block, llm` — design.md and brief use "fence" and "fenced blocks" in slice-001 ADR-001 references.
- **Issue**: BC-PROJ-2 may fire on positive-anchor path even though negative-anchor doesn't suppress. Worth a Phase 4 dry-run.
- **Evidence**: `architecture/build-checks.md:28-41`; mission-brief Intent / design.md repeated use.
- **Proposed fix**: Builder runs `tools/build_checks_audit.py` against slice-019 mission-brief + design.md at /build-slice Phase 4 dry-run; if fires, either (a) rephrase to avoid `fence` anchor, or (b) document expected per slice-018 BC-1 self-application empirical-clean precedent.
- **Builder draft**: ACCEPTED-PENDING — dry-run at /build-slice Phase 4. If clean (likely per slice-018 BC-PROJ-2 negative-anchor migration empirical-clean precedent N=5 cumulative), no design.md change. If fires, document inline.

#### m2: design.md does not explicitly document bidirectional sha256 forensic counter ratchet N=14 → N=15 + new ship hash list

- **Claim under review**: design.md "Audit gates" lists CAD-1 + mini-CAD for /diagnose but did not name the N=14 → N=15 ratchet or surface the new ship hashes for SKILL.md + 03f-layering.md.
- **Issue**: Per slice-018 reflection: forensic counter is a project-wide stability metric; /validate-slice Phase 5.5 needs a known expectation.
- **Proposed fix**: Add to design.md "Audit gates" subsection.
- **Builder draft**: ACCEPTED-FIXED — applied inline at `design.md` "Audit gates" subsection. New bullet: "Bidirectional sha256 forensic capture (slice-018 N=14 stable → slice-019 N=15 stable)" naming preserved `agents/critique.md` hash (`f34c967eaaa34413`) + new methodology-changelog hash at Phase 2c + new SKILL.md + 03f-layering.md hashes entering the forensic capture list (extends from N=2 files to N=4 files).

#### m3: ADR-017 "Future flexibility" framing depends on B1 resolution

- **Claim under review**: ADR-017 Future flexibility bullet 3 mentions 02-architecture / 03d-half-wired as future-extension targets.
- **Issue**: If B1's enumeration explicitly OUT-scopes these (with rationale grounded in finding-category emission shape), the ADR's "future" framing is consistent. If B1's enumeration finds any IN, the ADR needs an addendum.
- **Builder draft**: ACCEPTED-PENDING — revisit ADR-017 Future flexibility bullet 3 AFTER B1's enumeration is applied. Per Builder's B1 draft (only 03f IN; 02/03b/03d/03e OUT with rationale), ADR-017 framing remains consistent — no addendum expected.

## Dimensions checked

- [x] Unfounded assumptions — M3 (design.md "only 03f emits layering-violation" claim grep-verifiable but unsurfaced); B2 (grep-pattern claim doesn't textually verify alias-aware behavior the witnessed false-positive needed). Tooling-doc-vs-implementation parity verified at `passes/03f-layering.md:13,47` + `passes/02-architecture.md:69-71`.
- [x] Missing edge cases — B2 (side-effect imports, re-exports, multi-line imports, alias-aware grep — Hendrickson edge-case heuristics at language-syntax-variant level).
- [x] Over-engineering — none (witness-driven scope; Fowler speculative-generality clean; v2 audit deferred per N≥3 precedent).
- [x] Under-engineering — B1, B3, M4 (must-not-defer #1 propagation; mini-CAD dual-file TF-1 coverage; slice-018 sibling-scoping inheritance).
- [x] Contract gaps — none (subagent contract preserved per design.md; finding schema `evidence[].note` optional verified at `schema/finding.yaml:71`).
- [x] Security — none (prose + tests + fixtures only; downgrade-or-skip rule cannot escalate severity).
- [x] Drift from vault — none (ADR-017 path/refs verified; R-3 RR-1-conformant; PMI-1 v1.1 atomic bump 0.32.0 → 0.33.0 valid).
- [x] Web-known issues — B2 (TS ES-module variants per [TypeScript Documentation - Modules](https://www.typescriptlang.org/docs/handbook/2/modules.html) 2026-05-13).
- [x] Cross-cutting conformance — M3 (RSAD-1 design-time recursive-self-application); M4 (slice-018 sibling-test scoping discipline N=2 cumulative inheritance); m1 (BC-PROJ-2 negative-anchor word-boundary); B3 mini-CAD TF-1 row coverage (methodology-audit conformance sub-class); m2 forensic counter ratchet documentation (mechanical-table-vs-canonical-inventory); TPHD-1 self-application: B1/B2/B3/M4 fixes change TF-1 plan rows + design.md prose — harmonize in same fix block per slice-017 TPHD-1 sub-mode (a).

## Triage

**Triaged by**: user
**Date**: 2026-05-13
**Final verdict**: NEEDS-FIXES

Both first-Critic and meta-Critic (critique-review.md, EXTEND verdict) findings ratified as-is per user "ratify" at /critique Step 4.5. Severity column reflects post-meta-Critic adjustments (B1: Blocker → Major per critique-review.md SEVERITY-WRONG). M-add-1 + M-add-2 added by meta-Critic.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Major | ACCEPTED-PENDING | Severity downgraded Blocker → Major per critique-review.md (ground-truth grep narrows actionable scope; concern is Wiegers documentation-completeness, not OWASP correctness). Enumeration fix unchanged: design.md gains "Step 5 dispatch enumeration" subsection at /build-slice Phase 1 with per-pass decisions (03f IN; 02/03b/03d/03e OUT with rationale) + grep-evidence pin at `passes/03f-layering.md:47`. |
| B2 | Blocker | ACCEPTED-PENDING | Apply at /build-slice Phase 1: tighten Method step 4 with 5 TS variants + 3 re-export forms + multi-line semantics (re.DOTALL / ripgrep --multiline) + alias-aware grep (tsconfig paths/baseUrl: try BOTH repo-relative + alias-resolved forms) + concrete Rust/Go/Java fallbacks. Test helper + fixtures extended to cover variants. Per TPHD-1 sub-mode (a): mission-brief TF-1 plan may gain additional fixture-test rows; harmonize in same fix block. |
| B3 | Blocker | ACCEPTED-PENDING | Path A split at /build-slice Phase 1: replace single mini-CAD TF-1 row with two single-file rows (`..._diagnose_skill_md_are_content_equal` + `..._diagnose_03f_layering_md_are_content_equal`) per slice-007 CAD-1 / slice-010 mini-CAD single-file convention. Per TPHD-1 sub-mode (a): mission-brief TF-1 plan + design.md "What's new" test enumeration harmonized in SAME fix block. |
| M1 | Major | ACCEPTED-PENDING | Apply at /build-slice Phase 1: design.md gains "Test-local helper rationale + drift risk" paragraph; pass-template Method step 4 embeds EXACT literal regex strings (visual byte-equality with `_grep_textual_import` constants). Cross-byte-equality prose-pin audit test deferred to v2 per TPHD-1 / RSAD-1 / RPCD-1 N≥3-violations-deferral precedent. |
| M2 | Major | ACCEPTED-FIXED | Applied inline during /critique Step 4. ADR-017 gains "## Recursive self-application (RSAD-1, slice-011 / Dim 9 sub-clause 6)" section. Post-meta-Critic refinement (M-add-2 below) further tightens the wording. |
| M3 | Major | ACCEPTED-PENDING | Folded into B1's Step 5 dispatch enumeration subsection — the per-pass enumeration with grep-evidence pin naturally surfaces this verification. Apply at /build-slice Phase 1 in same fix block as B1. |
| M4 | Major | ACCEPTED-PENDING | Apply at /build-slice Phase 1-2: design.md gains "test-scoping inheritance" paragraph; introduce `_extract_v033_body(content) -> str` helper (between `## v0.33.0` and `## v0.32.0` boundaries) per slice-018 `_extract_v031_body` precedent; scope two v0.33.0 entry-pin tests to `v033_body` not raw `content`; add NEW regression test `test_v_0_33_0_layer_evid_1_sibling_scoping_rejects_stripped_v033_body`. Per TPHD-1 sub-mode (a): mission-brief TF-1 plan + design.md test-scoping paragraph harmonized in same fix block. Regression test pattern mirrors slice-018 L1010-1060 at PATTERN level, NOT literal-code level (per slice-018 /critique-review m-add-2 Audit 3 refinement). |
| m1 | Minor | ACCEPTED-PENDING | /build-slice Phase 4 dry-run: `tools/build_checks_audit.py` against slice-019 mission-brief + design.md. If BC-PROJ-2 fires on `fence` positive anchor (despite `false-positive` hyphenated escaping `false positive` negative anchor), document inline per slice-018 BC-1 self-application empirical-clean precedent. |
| m2 | Minor | ACCEPTED-FIXED | Applied inline during /critique Step 4. design.md "Audit gates" subsection gains bidirectional sha256 forensic counter ratchet bullet (N=14 → N=15 stable; per-file ship hash list extends from 2 to 4 files). |
| m3 | Minor | ACCEPTED-PENDING | Revisit ADR-017 Future flexibility bullet 3 AFTER B1's enumeration is applied. Per Builder's B1 decision (only 03f IN; 02/03b/03d/03e OUT with rationale), ADR-017 framing remains consistent — no addendum expected. /build-slice Phase 1 verification. |
| M-add-1 | Major | ACCEPTED-PENDING | (Meta-Critic missed-finding; Dim 5 Contract gaps.) Apply at /build-slice Phase 1: tighten mission-brief AC #1 prose AND Risk-retired field to drop speculative "boundary / cross-tier / import-violation" enumeration (no schema referent per `schema/finding.yaml:21-32` ground-truth); only `layering-violation` is materialized; ADR-017 already names the grep-verification at `passes/03f-layering.md:47`. Per TPHD-1 sub-mode (b) self-application: AC #1 rename harmonizes mission-brief TF-1 plan AC #1 rows + design.md "Step 5 dispatch enumeration" subsection in SAME fix block. Reduces B1's actionable scope. |
| M-add-2 | Major | ACCEPTED-FIXED | (Meta-Critic missed-finding; Dim 9 Cross-cutting conformance.) Applied inline at /critique-review Step 4 follow-on. ADR-017 "## Recursive self-application" section rephrased to remove "post-codification N=1" qualifier (logical incoherence — slice-019 IS the codification slice); now reads "Slice-019 is the LAYER-EVID-1 codification slice AND is the canonical reference instance #1 at codification time, mirroring slice-015 SCPD-1 + slice-017 TPHD-1 canonical-reference-instance-at-codification-time precedent". Post-codification N=2 explicitly deferred to "next /diagnose pass authorship that triggers LAYER-EVID-1". DR-1 catch-class diversification ratchets N=6 → N=7 with this NEW class (*Self-application-qualifier coherence on canonical-reference-instance naming*); watch-list at N=1, promote to Dim 9 sub-clause refinement at N≥3. |

**Verdict computation** (mechanical, per /critique Step 4.5):
- 9 ACCEPTED-PENDING (B1, B2, B3, M1, M3, M4, m1, m3, M-add-1) → NEEDS-FIXES
- 3 ACCEPTED-FIXED (M2, m2, M-add-2) → inline-settled
- 0 ESCALATED → no BLOCKED
- 0 OVERRIDDEN → no rationale-required overrides
- 0 DEFERRED → no slice / backlog targets

Pattern: any ACCEPTED-PENDING → NEEDS-FIXES. Verdict matches.
