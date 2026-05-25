# Critique Review: Slice 019 harden-diagnose-layering-evidence

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's coverage is broadly sound on B2/B3/M1/M2/M3/M4/m1/m2/m3 (VALID at original severity) but contains one SEVERITY-WRONG over-reach (B1 propagation-scope: Blocker → Major after ground-truth narrowing) and misses two concrete concerns surfaced by independent re-application of the 8 review dimensions: M-add-1 (Dim 5 Contract gaps — schema-enum mismatch in mission-brief AC #1 propagation scope) and M-add-2 (Dim 9 Cross-cutting conformance — ADR-017 RSAD-1 self-application coherence). Net adjustment: 1 severity downgrade, 0 suspicious drops, 2 missed findings.

## Confirmed findings (VALID at original severity)

First-Critic findings the meta-Critic agrees with at original severity:

- **B2 — ES-module grep regex variants + alias-aware**: VALID; Blocker. The witnessed F-LAYER-bca9c001 failure mode involves frontend TS code with `@/*` alias resolution; a naive `^\s*import\b.*<module>` regex against an ES-module corpus would itself produce false negatives, re-creating the false-positive symmetrically as a false-negative. Per OWASP/McGraw input-validation discipline, evidence-verification regex must cover the corpus's actual syntactic forms. Diagnostic quality is preserved in the proposed fix (5 TS variants + multi-line + alias-aware are concrete, not vague).
- **B3 — Mini-CAD dual-file TF-1 row gap**: VALID; Blocker. Per CAD-1 / slice-007 + slice-010 mini-CAD precedent, each file under bidirectional byte-equality discipline gets its own TF-1 row. Design.md commits to bidirectional sha256 for 4 files (SKILL.md + 03f-layering.md + methodology-changelog.md + agents/critique.md). If TF-1 plan collapses these into a single row, the audit lattice loses per-file failure-isolation per Hendrickson exploratory-testing observability.
- **M1 — Test-helper drift risk**: VALID; Major. Proposed mitigation (embed literal regex strings in both prose and test helper) closes the drift surface at codification time; deferred-audit decision is reasonable at N=1 with cheap reversibility per Sommerville evolution economics.
- **M2 — ADR-017 canonical reference instance naming (ACCEPTED-FIXED)**: VALID at original filing time; see M-add-2 below for residual wording concern uncovered by re-reading the applied fix.
- **M3 — design.md grep-verification surfacing (folded into B1)**: VALID per folding.
- **M4 — Slice-018 sibling-scoping inheritance with `_extract_v033_body`**: VALID; Major. Per slice-018 reflection precedent, N=2 is the promotion threshold (more aggressive than Fowler rule-of-three's N=3 but already codified at slice-018). Slice-019's M4 proposes the second instance — promotion-eligible.
- **m1 — BC-PROJ-2 word-boundary dry-run**: VALID; Minor.
- **m2 — Forensic counter doc (ACCEPTED-FIXED)**: VALID at original filing.
- **m3 — ADR-017 Future flexibility framing**: VALID; Minor.

## Suspicious findings

None. No first-Critic finding rises to the SUSPICIOUS bar (where the meta-Critic would recommend the user OVERRIDE with reduced friction).

## Missed findings

### M-add-1: Schema-enum mismatch in mission-brief AC #1 propagation scope (Dim 5: Contract gaps)

- **Claim under review**: mission-brief AC #1: *"`/diagnose` layering pass template (and any sibling pass that emits boundary / cross-tier / import-violation findings — at minimum the layering pass; per Step 5 dispatch enumeration)"*. Mission-brief Risk-retired field: *"`/diagnose` layering / boundary / import passes emit HIGH-severity findings..."*. Both enumerate "boundary / cross-tier / import-violation" as categorical surfaces alongside "layering".
- **Issue**: Ground-truth grep of `skills/diagnose/schema/finding.yaml` (category enum at lines 21-32) and all 11 pass templates (`skills/diagnose/passes/*.md`) shows the `category:` enum materializes only **`layering-violation`** at `passes/03f-layering.md:47` for this concern class. The terms `boundary-violation`, `cross-tier`, `import-violation` do NOT exist as schema-enumerated category values anywhere in the diagnose skill surface. Per Newman *Building Microservices* contract-discipline + Wiegers requirements-traceability: an acceptance criterion that enumerates non-existent categorical surfaces ships ambiguity to /build-slice — Builder must either (a) materialize the missing enums (out-of-scope per mission-brief Out-of-scope #1: "Other /diagnose pass false-positive classes... different fix surface") or (b) interpret AC #1 as covering only the one extant category (`layering-violation`). The interpretation-only reading IS what design.md already does, but the AC prose doesn't say so.
- **Evidence**:
  - `skills/diagnose/schema/finding.yaml:21-32` — full category enum: `dead-code | duplicate | size-outlier | half-wired | contradiction | layering-violation | dead-config | test-gap | ai-bloat`. Zero matches for `boundary-violation` / `cross-tier` / `import-violation`.
  - `skills/diagnose/passes/03f-layering.md:47` — sole emitter of `category: layering-violation`.
  - mission-brief AC #1 + Risk-retired field — both enumerate the speculative vocabulary.
- **Proposed fix**: Tighten AC #1 prose to: *"The `/diagnose` 03f-layering pass template (the sole pass emitting `category: layering-violation` per schema enum, ground-truth verified at `passes/03f-layering.md:47`) carries explicit prose..."*. Drop the speculative "boundary / cross-tier / import-violation" enumeration from AC #1 + Risk-retired field. This also tightens B1's actionable scope, reducing the scope-creep risk the first Critic correctly intuited in B1 but mis-attributed to a propagation-gap concern.

### M-add-2: ADR-017 RSAD-1 self-application coherence (Dim 9: Cross-cutting conformance)

- **Claim under review**: ADR-017 "## Recursive self-application (RSAD-1, slice-011 / Dim 9 sub-clause 6)" section (added per /critique M2 ACCEPTED-FIXED inline): *"Slice-019 is therefore the standalone canonical reference instance of LAYER-EVID-1 **(N=1 standalone post-codification**, mirroring slice-015 SCPD-1 + slice-017 TPHD-1 canonical-reference-instance precedent)."*
- **Issue**: Logical incoherence — slice-019 IS the LAYER-EVID-1 codification slice. It cannot simultaneously be "post-codification N=1" of its own codification. Per RSAD-1 (slice-011 / Dim 9 sub-clause 6) the codification slice's self-application is "the codification slice itself counts as instance #0 / N=1 **substantive-codification**, not N=1 **post-codification**." The slice-015 SCPD-1 / slice-017 TPHD-1 precedent the ADR cites applies when a LATER slice retroactively self-applies an EARLIER codification — that's where the "post-codification N=1" framing fits.

  Re-reading slice-017's own self-description: "TPHD-1 self-application N=1 empirically demonstrated across all 3 sub-modes on slice-017's own draft" — slice-017 named ITSELF as instance #1 at codification time, not "post-codification". The same applies here: slice-019 IS instance #1 at codification time. "Post-codification" is the wrong qualifier.
- **Evidence**:
  - `architecture/decisions/ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md` "Recursive self-application" section (the augmented prose).
  - slice-011 RSAD-1 codification (Dim 9 sub-clause 6 of `agents/critique.md`).
  - slice-017 TPHD-1 reflection: "slice-017 IS canonical reference instance #1 of TPHD-1" (no "post-codification" qualifier).
  - slice-015 SCPD-1 reflection: "slice-015 IS canonical reference instance of the discipline it authors" (no "post-codification" qualifier).
- **Proposed fix**: Rephrase the ADR-017 RSAD-1 paragraph to remove the "post-codification" qualifier from the slice-019 self-description: *"Slice-019 is the LAYER-EVID-1 codification slice and IS the canonical reference instance #1 of LAYER-EVID-1 — applied retrospectively to its own witness investigation (manual-grep disproving F-LAYER-bca9c001) BEFORE the rule was codified, mirroring slice-015 SCPD-1 + slice-017 TPHD-1 canonical-reference-instance-at-codification-time precedent. The first post-codification instance will be N=2 at the next slice authoring a /diagnose pass that triggers LAYER-EVID-1 textual-evidence verification per the freshly codified rule."* Per TPHD-1 sub-mode (b) self-application: M-add-2's fix touches ADR-017 prose only — no TF-1 plan rows affected; no mission-brief harmonization needed.

## Severity adjustments

### B1 — Must-not-defer #1 propagation gap: Blocker → Major (SEVERITY-WRONG)

- **Original**: Blocker.
- **Recommended**: Major.
- **Rationale**: The first Critic's concern (design.md doesn't explicitly enumerate which passes besides 03f-layering carry the textual-evidence rule) is real but its severity rests on the assumption that multiple passes emit layering/boundary/import-violation findings. Ground-truth verification (grep across `skills/diagnose/passes/*.md` and `skills/diagnose/schema/finding.yaml`):
  - Only **03f-layering.md** emits `category: layering-violation` (verified at `passes/03f-layering.md:47`).
  - No other `category` enum exists for this concern class (per `schema/finding.yaml:21-32` full enumeration).
  - Pass **02-architecture** explicitly returns `findings: []` per slice-001 contract (verified at `passes/02-architecture.md:69-71`).
  - Pass **03d-half-wired**'s frontend↔backend disconnect findings are endpoint-existence checks (UI button posts to nonexistent endpoint), NOT graphify-edge-based import-violation findings — different evidence shape per `passes/03d-half-wired.md` Method.
  - Pass **03b-duplicates** flags shape-equivalence not import-bypass; pass **03e-contradictions** flags assumption-divergence not import-violation.

  The propagation surface materially is the same set design.md already targets (SKILL.md Step 5 + 03f-layering.md). ADR-017 already names the grep-verification of "only 03f-layering emits category: layering-violation" at `passes/03f-layering.md:47` verified 2026-05-13 (per the M2 ACCEPTED-FIXED inline application during /critique).

  The remaining concern — that design.md should EXPLICITLY enumerate the propagation surface to defend against future passes regressing — is a documentation-completeness concern, **Major-grade per Wiegers requirements-traceability**, not Blocker-grade per OWASP/McGraw correctness-impact. The Builder's draft (per-pass decisions with grep-evidence pin) remains the right fix; only the severity tag changes.
- **Combined with M-add-1**: if M-add-1 is also accepted (tighten AC #1 prose to drop speculative vocabulary), B1's enumeration fix becomes even tighter — only 03f-layering needs surfaced verification; the other 10 passes can be documented in one paragraph as "out of scope per AC #1 schema-bounded category."

## Notes

- **Confidence**: HIGH on M-add-1 (direct ground-truth file grep confirms schema-enum scope). HIGH on M-add-2 (logical coherence check against documented RSAD-1 schema + slice-015/017 precedent wording). MEDIUM-HIGH on B1 severity adjustment (substantive concern is real and matters at codification time, but Blocker classification is over-reach absent the missing schema enums).
- **DR-1 catch-class diversification N=6 → N=7** if M-add-2 is accepted at TRI-1: M-add-2 is a NEW class — *Self-application-qualifier coherence on canonical-reference-instance naming* — distinct from prior 6 classes (3 RPCD-1 sub-modes + 2 Wiegers regression-guard coverage-symmetry + 1 cleanup-slice secondary-cost). Watch-list ratchets at N=1 for this slice; promote to Dim 9 sub-clause refinement at N=3 distinct-slice recurrence.
- **DR-1 class (a) diagnostic-quality regression**: not detected on slice-019 — B2's proposed fix preserves diagnostic context with concrete TS variants; no regression vs slice-017 canonical L1088-1090 surface-context-aware diagnostic pattern.
- **DR-1 class (b) helper-extraction asymmetry**: M4's `_extract_v033_body` would be the SECOND v0.NN entry-body helper (after slice-018's `_extract_v031_body`). Per slice-018 reflection precedent: defer at N=1, promote at N≥2. Slice-019's M4 = N=2 = promotion-eligible. The first Critic correctly captured this in M4 — VALID at Major. No additional DR-1 (b) miss.
- **DR-1 class (c) bidirectional installed-surface evidence-trace gap**: design.md "Audit gates" subsection (per the just-added m2 ACCEPTED-FIXED forensic counter ratchet bullet) commits to 4-file bidirectional ship hashes with per-file enumeration. B3 catches the TF-1-row granularity for the same files. Together they cover the bidirectional surface. No additional DR-1 (c) miss.
- **Pattern observation**: the first Critic's findings on slice-019 lean toward Blocker-grade severity on documentation-completeness concerns (B1, B3). Historically at slices 13-18 these patterns calibrated to Major when ground-truth verification narrowed actionable scope. This is a watchlist signal for `/critic-calibrate` aggregation — if N=2 instances recur in slice-020+, propose a Dim 4 sub-bullet refinement on Blocker-vs-Major calibration for documentation-completeness concerns.
- **TPHD-1 sub-mode (b) self-application**: M-add-1 if accepted at TRI-1 will rename AC #1 prose (drop speculative vocabulary). Builder MUST harmonize mission-brief TF-1 plan AC #1 rows + design.md "Step 5 dispatch enumeration" subsection in the SAME fix block per slice-017 TPHD-1 precedent. M-add-2 if accepted touches ADR-017 prose only — no TF-1 plan / design.md row impact; no harmonization needed.

## Files inspected for ground truth

- `<HOME>\ai_sdlc\skills\diagnose\passes\03f-layering.md`
- `<HOME>\ai_sdlc\skills\diagnose\passes\02-architecture.md`
- `<HOME>\ai_sdlc\skills\diagnose\passes\03d-half-wired.md`
- `<HOME>\ai_sdlc\skills\diagnose\passes\03b-duplicates.md`
- `<HOME>\ai_sdlc\skills\diagnose\passes\03e-contradictions.md`
- `<HOME>\ai_sdlc\skills\diagnose\SKILL.md`
- `<HOME>\ai_sdlc\skills\diagnose\schema\finding.yaml`
- `<HOME>\ai_sdlc\architecture\decisions\ADR-017-textual-evidence-requirement-for-diagnose-boundary-findings.md`
- `<HOME>\ai_sdlc\methodology-changelog.md`
- `<HOME>\ai_sdlc\architecture\risk-register.md`
- `<HOME>\ai_sdlc\plugin.yaml`
