# Critique: Slice 020 codify-bug-fix-repro-prelude-at-slice

**Critic reviewed**: mission-brief.md, design.md, ADR-018-bfrd-1-bug-fix-repro-prelude-discipline.md
**Date**: 2026-05-14
**Result**: NEEDS-FIXES (pre-triage); pending TRI-1 user ratification

## Summary

Critic returned 3 Blockers, 5 Majors, 6 Minors (14 findings total). B1 (slice-001 `-fix` suffix counter-example demonstrated empirically against project corpus), B2 (verification mechanism unspecified — discipline has no enforcement primitive), and B3 (ADR-018 magnitude count drift 11 enumerated vs ~8-10 declared — N=4 cumulative recurrence of Wiegers regression-guard coverage-symmetry class). 5 Majors target: contingent-vs-architectural N/A framing (M1), N-surface schema-pin necessity (M2), Risk-retired vs Dependencies consistency (M3), mid-slice smoke gate completeness (M4), helper-extraction generalization at N=3 rule-of-three trigger (M5). 6 Minors covering stylistic + operational-definition + clarification polish.

11 ACCEPTED-FIXED inline (B1, B2, B3, M1, M3, M4, M5, m2, m3, m4, m5), 1 OVERRIDDEN (M2 — convention-vs-Fowler-smell trade-off favors convention preservation), 2 DEFERRED (m1, m6 — stylistic/tangential).

## Findings

### Blockers (must address before /build-slice)

#### B1: Detection mode (a) `fix-*` name-prefix is empirically broken against this project's own historical bug-fix slices

- **Claim under review**: design.md Step 3c content structure point 3: `Detection-mode list (sub-mode (a) "fix-*" name-prefix; sub-mode (b) explicit bug-fix signal from candidate source)`. Mission-brief AC #1 names `"fix-" name-prefix detection`.
- **Issue**: This codebase's own slice-001 is named `slice-001-diagnose-orchestration-fix` — `fix` appears as a **suffix**, not a prefix. Slice-001's mission-brief.md L7 explicitly states "regression discovered in the 2026-05-09 session" — it IS a bug-fix slice. Common bug-fix naming variants in adjacent projects also escape `fix-*` prefix: `bugfix-*`, `hotfix-*`, `defect-*`, `harden-*`, `repair-*`, `patch-*`, and the historical `-fix` suffix. Per Hendrickson (Explore It!) edge-case discovery: the rule's detection surface should accommodate at minimum the suffix form `*-fix` (witnessed N=1 in-project) and the common prefix variants.
- **Evidence**: `architecture/slices/archive/slice-001-diagnose-orchestration-fix/mission-brief.md` L1, L7; `architecture/slices/archive/slice-002-fix-diagnose-contract-and-cwd-mismatch/` (sole project-history match for `fix-*`); design.md "Step 3c content structure" item 3.
- **Proposed fix**: Widen mode (a) to a regex set covering `fix-*` + `*-fix` + `bugfix-*` + `hotfix-*` + `defect-*` + `repair-*` + `patch-*` + `harden-*-bug`; acknowledge in Step 3c prose that name-shape detection is necessary-but-not-sufficient (rely on mode (b) candidate-source signal as primary; mode (a) is fast-path fallback only); add slice-001 witnessed false-negative anchor in methodology-changelog Limitations note.
- **Builder draft**: ACCEPTED-FIXED at design.md "Step 3c content structure" item 3 (widened mode (a) to regex set including suffix `*-fix` form; reclassified mode (a) as necessary-but-not-sufficient fast-path; mode (b) elevated to PRIMARY) + mission-brief AC #1 (cites widened detection-mode shape + slice-001 witnessed false-negative anchor citation). Methodology-changelog v0.34.0 entry text will name slice-001 as witnessed anchor at /build-slice Phase 1b. **Strong recursive-self-application catch — the codification slice's own draft of BFRD-1 mode (a) was empirically falsifiable against the project's own corpus.**

#### B2: Verification mechanism for "failing repro test exists" is unspecified — discipline has no enforcement primitive

- **Claim under review**: design.md Step 3c content structure points 4-5 (STOP-and-route behavior + failing-test path cited under Dependencies). ADR-018 Option 1.
- **Issue**: Design specifies BEHAVIORAL contract (STOP, route, cite) but never specifies HOW Claude main thread VERIFIES that a failing test actually exists. Without a verification mechanism, the discipline reduces to "ask the user nicely" — purely advisory. `/repro` skill (`skills/repro/SKILL.md` L14) says `/repro` writes the test into `shippability.md` — that's the verifiable surface BFRD-1 should adopt.
- **Evidence**: design.md "Step 3c content structure" lacks verification-mechanism bullet; `skills/repro/SKILL.md` L14 gives a concrete verifiable hook (shippability catalog row addition).
- **Proposed fix**: Add new bullet (item 4) in Step 3c content structure specifying `shippability.md grep verification` mechanism (canonical phrase pin) with verbal-claim-with-path fallback for malformed-shippability case; add 2 new TF-1 rows (1 changelog entry-pin + 1 skill-prose entry-pin); pin the canonical phrase in methodology-changelog Limitations note.
- **Builder draft**: ACCEPTED-FIXED at design.md Step 3c content structure (NEW item 4 specifies grep + verbal-fallback verification) + design.md Test-first plan (added 2 new TF-1 rows: `test_v_0_34_0_bfrd_1_entry_names_verification_mechanism` + `test_slice_skill_md_bfrd_1_verification_mechanism_present`) + mission-brief AC #1 (extends entry-pin requirements to cover verification-mechanism phrase) + mission-brief AC #2 (extends skill prose pinning to cover verification-mechanism bullet) + mission-brief TF-1 plan table (9 → 11 rows; TPHD-1 sub-mode (a) self-application N=3 → N=4 stable). **Verification primitive now concrete; canonical phrase `shippability.md grep verification` pinned across N=3 surfaces.**

#### B3: ADR-018 magnitude estimate is internally inconsistent (11 enumerated sites vs "~8-10 sites total" claim)

- **Claim under review**: ADR-018 Reversibility section: `~8-10 sites total (1 skill file + sync mirror + methodology-changelog + sync mirror + VERSION + ai-sdlc-VERSION + plugin.yaml.version + test_slice_skill.py + test_methodology_changelog.py + shippability.md + ADR-018)`. Mission-brief AC #3 cites the same magnitude.
- **Issue**: Parenthetical enumerates **11 distinct sites** while declaring "~8-10 sites total". Off-by-three at upper bound; off-by-one at lower. Same Wiegers regression-guard coverage-symmetry class as slice-017 m-add-1 catch ("count drift 11 → 12 across 6 sites") + slice-019 M-add-1 (Schema-enum-vs-AC-prose mismatch). At slice-020 this is N=4 cumulative — promotion-eligible for Dim 9 sub-clause refinement.
- **Evidence**: ADR-018 Reversibility section enumeration; `slices/_index.md` row 17 lemma on slice-017 meta-Critic m-add-1; slice-019 row 19 entry on DR-1 catch-class diversification N=6 → N=7.
- **Proposed fix**: Recount the enumeration; replace `~8-10 sites total` with `~11 sites total` (matches enumeration); update ADR-018 + mission-brief AC #3 + design.md to corrected number; acknowledge in slice's reflection that BFRD-1 codification slice committed the count-drift class on its own draft (N=4 cumulative).
- **Builder draft**: ACCEPTED-FIXED at ADR-018 Reversibility section (recounted to "~11 sites total" with /critique B3 note) + ADR-018 "Comparison to prior ADRs" section (line for ADR-018-this) + mission-brief AC #3 (cites "~11 sites" per /critique B3 ACCEPTED-FIXED recount). **Reflection ratchet to N=4 cumulative noted in ADR-018 itself; promotion-eligibility for Dim 9 refinement at next codification slice if recurs at slice-021+.**

### Majors (address this slice)

#### M1: Audit 7's "architectural-impossibility" claim for BFRD-1 self-application is not load-bearing-correct

- **Claim under review**: design.md Audit 7: `Self-application N=1 at codification time is therefore not architecturally possible.` ADR-018 Decision: `Recursive-self-application EXCEPTION: BFRD-1 cannot self-apply per architectural impossibility above.`
- **Issue**: "Architectural impossibility" is overstated — it's a CONTINGENT property of slice-020 (a feature slice), not an ARCHITECTURAL property of BFRD-1. A hypothetical future codification-AND-bug-fix slice would self-apply BFRD-1 trivially. Risk: downstream readers mis-cite as "BFRD-1 never self-applies". This is slice-019 DR-1 catch-class *Self-application-qualifier coherence on canonical-reference-instance naming* — N=1 watch-list, slice-020 ratchets toward N=2.
- **Evidence**: design.md Audit 7 wording; ADR-018 Decision "EXCEPTION" framing; `slices/_index.md` slice-019 DR-1 catch-class diversification.
- **Proposed fix**: Rewrite to "contingent N/A: slice-020 is a methodology-codification slice that does not fix a runtime bug, so BFRD-1's STOP-route is vacuously satisfied. Canonical reference instance #1 starts at the first prospective application at slice-021+. A future codification-AND-bug-fix slice would self-apply BFRD-1 trivially."
- **Builder draft**: ACCEPTED-FIXED at design.md Audit 7 (rewritten with "contingent N/A" framing; named hypothetical future codification-AND-bug-fix slice) + ADR-018 Decision section (replaced "EXCEPTION" with "contingent inapplicability"; clarified BFRD-1 itself is contingently N/A vs architecturally exempt). **DR-1 catch-class N=1 → N=2 cumulative watch-list at slice-020; one more recurrence at slice-021+ hits N=3 promotion threshold for Dim 9 sub-clause refinement.**

#### M2: N-surface schema-pin claim is non-load-bearing for BFRD-1 — canonical phrase need not appear in skill prose at all

- **Claim under review**: ADR-018 + mission-brief AC #1 + design.md "Step 3c content structure" item 6 (now item 7 post-B2): `Canonical phrase to pin: 'bug-fix repro prelude discipline' (used in section opener + methodology-changelog v0.34.0 entry + ADR-018 title)`.
- **Issue**: Critic argues the rule ID `BFRD-1` is sufficient in skill prose; the phrase could exist only in methodology-changelog + ADR-018 (N=2 surfaces). Fowler speculative-generality smell: applying N=3 surfaces because prior rules used it without checking whether THIS rule benefits.
- **Evidence**: design.md item 6 + 7 post-B2 fix; aggregated-lessons "N-surface schema-pin discipline scales naturally to N=7 stable".
- **Proposed fix**: Demote to N=2 surfaces OR keep N=3 with explicit justification.
- **Builder draft**: **OVERRIDDEN**. Rationale: the N=3 surface convention is N=6 stable across RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 / TPHD-1 / LAYER-EVID-1; deviating costs more downstream-reader cognitive overhead than the marginal Fowler-smell mitigation. The phrase appears naturally in the Step 3c section opener as the rule's expansion of `BFRD-1` (e.g., "Step 3c codifies the bug-fix repro prelude discipline"). The slice's design.md "Step 3c content structure" item 7 (post-B2) keeps the N=3 pin while adding the verification-mechanism phrase as a second canonical pin in the same prose surface. Net: skill prose pins `BFRD-1` (rule ID) + `bug-fix repro prelude discipline` (phrase) + `shippability.md grep verification` (mechanism phrase) = 3 pins in 1 prose surface, plus methodology-changelog in-repo + installed = N=3 surfaces total. The Fowler concern is acknowledged in the OVERRIDDEN rationale; if N=2-surface deviation proves beneficial empirically at N≥3 future codification slices, the convention can be revisited via /critic-calibrate.

#### M3: "Risk retired" field is inconsistent with RR-1 schema usage across the project

- **Claim under review**: mission-brief.md "Risk retired: Latent class — bug-fix slices defined without a pre-existing failing repro test." + Dependencies "Risk register: no entries — methodology-internal latent class".
- **Issue**: Risk retired calls it "Latent class" while Dependencies says "Risk register: no entries". If it's a registered latent class, it should have R-N; if not (which is the case), wording should match Dependencies.
- **Evidence**: mission-brief "Risk retired" field; mission-brief Dependencies; `architecture/risk-register.md` L7/L28/L46.
- **Proposed fix**: Reword Risk retired field to "No R-N retired (methodology-internal discipline codification — latent class with no risk-register entry)".
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md "Risk retired" field (reworded to match Dependencies; cites /critique M3 ACCEPTED-FIXED for evidence anchor). RR-1 schema cross-section coherence preserved.

#### M4: Mid-slice smoke gate is too narrow — does not verify Step 3c prose is actually present in in-repo SKILL.md

- **Claim under review**: mission-brief "Mid-slice smoke gate" runs only PMI-1 + CAD-1 + mini-CAD-1 byte-equality tests.
- **Issue**: Smoke gate verifies byte-equality between in-repo and installed SKILL.md but does NOT verify Step 3c prose is actually present. Incomplete-edit failure mode: both copies equally broken → byte-equality test PASSES → false-positive green light. RPCD-1 sub-mode (b) NEW-status/token allowlist-audit class.
- **Evidence**: mission-brief "Mid-slice smoke gate"; slice-016 RPCD-1 codification.
- **Proposed fix**: Add `tests/methodology/test_slice_skill.py::test_slice_skill_md_bfrd_1_prelude_present` to smoke gate pytest invocation. Expected: 4 PASS instead of 3 PASS.
- **Builder draft**: ACCEPTED-FIXED at mission-brief Mid-slice smoke gate (added prelude_present test; expected 4 PASS; cited /critique M4 + slice-016 RPCD-1 sub-mode (b) class). Smoke checkpoint now catches incomplete-Step-3c-insertion failure mode at ~50% build vs only at pre-finish.

#### M5: Helper-extraction asymmetry foreshadowing-decline assessment may be miscalibrated

- **Claim under review**: design.md Audit 4: `Decision: Option A (inline '## v0.34.0' boundary string slicing) for slice-020 — assertion density is low... Rule-of-three counter stays at N=2 post-slice-020; promote at next codification slice that introduces a third version-body helper need.`
- **Issue**: 3 entry-pin tests × inline boundary slicing = 3 fresh sites of the pattern → slice-020 IS the next codification slice and aggregated lesson explicitly says "Promote to `_extract_version_body(content, version) -> str` at N=3 (next codification slice)". Inline contradicts aggregated lesson.
- **Evidence**: design.md Audit 4; `slices/_index.md` aggregated lessons "Helper-extraction asymmetry foreshadowing-decline at N=2 (Fowler rule-of-three)... Promote to _extract_version_body at N=3 (next codification slice)"; design.md Test-first plan 3 entry-pin tests for v0.34.0.
- **Proposed fix**: Generalize now — `_extract_version_body(content: str, version: str) -> str` with `_extract_v031_body` + `_extract_v033_body` as thin wrappers for backward compatibility.
- **Builder draft**: ACCEPTED-FIXED at design.md Audit 4 (Option C — generalized helper — chosen with explicit aggregated-lessons compliance rationale; updated Decision text; slice-018 + slice-019 existing tests preserved via wrappers) + mission-brief Must-not-defer (added new bullet on helper-extraction generalization scope) + design.md Test-first plan "Helper-generalization scope" sub-section. **Rule-of-three counter ratchets N=2 → N=3 stable post-slice-020; implementation at /build-slice Phase 1a.**

### Minors (log; address if cheap)

#### m1: "Risk retired" canonical naming inconsistency with slice-019 precedent

- **Claim under review**: mission-brief.md "Risk retired" phrasing.
- **Issue**: Cross-slice stylistic consistency on Risk-retired field voice. Not load-bearing.
- **Proposed fix**: Defer to slice-021+ when N=3 mission-brief samples accumulate.
- **Builder draft**: **DEFERRED** to slice-022+ /critic-calibrate aggregation pool (rationale: pattern not yet stable at N=2 samples; M3 ACCEPTED-FIXED already partially mitigates by aligning Risk-retired wording with Dependencies section RR-1-conforming phrasing; stylistic convention enforcement awaits N=3 evidence).

#### m2: "deferred until N≥3 violations recur" framing applies to a v2 audit that hasn't been spec'd

- **Claim under review**: mission-brief AC #1 v2 audit deferral framing.
- **Issue**: No operational definition of what counts as a BFRD-1 violation. The N=3 promotion threshold has no measurable detector.
- **Proposed fix**: Add 1-sentence operational definition to methodology-changelog v0.34.0 Limitations note.
- **Builder draft**: ACCEPTED-FIXED. Operational violation-detector definition will be added to methodology-changelog v0.34.0 Limitations note at /build-slice Phase 1b: "Violation detector for promotion threshold: at /reflect, Claude inspects mission-brief Dependencies for a failing-test path on bug-fix slices; missing or post-hoc-added test = 1 violation." Mission-brief AC #1 already references the operational definition via /critique m2 ACCEPTED-FIXED citation.

#### m3: "Audit 8 — Surface count parity" framing risks misleading comparison

- **Claim under review**: design.md Audit 8 prose-pin density comparison.
- **Issue**: 1-vs-3-vs-1 skill-file comparison is correct, but elides that slice-020's 2 prose-pin tests (3 post-B2 fix) is fewer than slice-010's 5. Without clarification, future critics could misread as regression.
- **Proposed fix**: Add clarification sentence to Audit 8.
- **Builder draft**: ACCEPTED-FIXED at design.md Audit 8 (added clarification sentence per /critique m3; post-B2 ACCEPTED-FIXED test counts 3 prose-pin + 4 entry-pin/ADR-pin = 7 total; row count 10).

#### m4: ADR-018 Option 3 rejection rationale is thin

- **Claim under review**: ADR-018 Option 3 rejection.
- **Issue**: Rejection skips that the Critic *could* fire a Blocker at /critique time on "bug-fix slice has no Dependencies entry referencing a failing test." Useful complement to /slice-time prevention.
- **Proposed fix**: Append to Option 3 rejection acknowledging the safety-net possibility + round-trip cost rationale.
- **Builder draft**: ACCEPTED-FIXED at ADR-018 Option 3 rejection section (appended acknowledgment of /critique-time safety-net possibility + cited /critique m4 ACCEPTED-FIXED rationale on round-trip cost; deferred as v2 candidate at N≥3 first-Critic-MISS).

#### m5: PMI-1 counter math claim has off-by-one ambiguity

- **Claim under review**: mission-brief AC #4 `retirement-proof N=5 → N=6 stable`.
- **Issue**: Math is correct (slice-014..019 = 5 atomic bumps; slice-020 = 6th) but the counter coexists with `-D suffix convention N=5 → N=6 stable`. Readers could conflate.
- **Proposed fix**: 1-word disambiguation `retirement-proof atomic-bump count N=5 → N=6`.
- **Builder draft**: ACCEPTED-FIXED at mission-brief.md AC #4 (added "atomic-bump count" disambiguation per /critique m5 ACCEPTED-FIXED).

#### m6: Out-of-scope item "Open R-1 + R-2... require /repro first (nice irony, but out-of-scope here)" is structurally tangential

- **Claim under review**: mission-brief.md "Out of scope" item 5.
- **Issue**: R-1/R-2 retirement is real future opportunity but listing as out-of-scope on methodology-codification slice mixes signal with noise.
- **Proposed fix**: Delete or move to reflection.
- **Builder draft**: **DEFERRED** to slice-020 reflection.md "Future opportunities surfaced" section (rationale: R-1/R-2 are valid future-slice candidates that warrant standalone /repro + /slice cycles; current Out-of-scope mention IS rhetorically tangential per /critique m6 but doesn't load-bearing harm slice-020's design; cleanup happens at reflection time without churn on mission-brief mid-slice). Out-of-scope item kept verbatim until reflection.

## Dimensions checked

- [x] **Unfounded assumptions** — B1 (fix-* prefix unverified against project corpus — VALIDATED by slice-001 counter-example), B2 (verification mechanism unspecified), M1 (architectural-impossibility claim contingent), m1 (Risk-retired stylistic consistency)
- [x] **Missing edge cases** — B1 (suffix `-fix` + prefix variants empirically witnessed), M4 (smoke gate doesn't catch incomplete Step 3c insertion)
- [x] **Over-engineering** — M2 (N-surface schema-pin may not be load-bearing — Fowler speculative-generality smell — OVERRIDDEN with convention-preservation rationale), M5 (under-engineering inverse — rule-of-three suggests helper generalization NOW)
- [x] **Under-engineering** — B2 (verification mechanism missing — load-bearing for enforceability), M4 (mid-slice smoke gate misses substantive content check — RPCD-1 sub-mode class), M5 (helper generalization deferred against aggregated-lessons promotion threshold)
- [x] **Contract gaps** — none (slice introduces no new endpoints/events/schemas; skill-prose contract additions covered by B2 + M4)
- [x] **Security** — none (no auth/data/external-integration paths; rule-ID format consistency already in Must-not-defer)
- [x] **Drift from vault** — M3 (Risk-retired vs Dependencies cross-section inconsistency against RR-1 schema usage); ADR-018 numbering correct; methodology-changelog v0.34.0 follows v0.33.0 correctly; shippability row 20 follows row 19 correctly
- [x] **Web-known issues** — skipped (no novel external technology; pure in-house methodology codification; no platform/library version dependencies introduced)
- [x] **Cross-cutting conformance** — STRONGEST dimension for this slice given recursive-self-application expectation:
  - Methodology-audit conformance (Dim 4 cross-ref): M4 (RPCD-1 sub-mode class on smoke-gate completeness)
  - Tooling-doc-vs-implementation parity (Dim 1 cross-ref): B3 (ADR-018 count drift — Wiegers regression-guard coverage-symmetry watch-list N=4 cumulative)
  - Algorithm-path-conformance: B1 (fix-* prefix as new branch dominates pre-existing detection — Hendrickson edge-case discovery)
  - Recursive self-application discipline: B1, B3, M1, M5 are recursive-self-application catches on slice-020's own draft of disciplines it's adjacent to (TPHD-1 sub-mode (a)+(b) + Wiegers coverage-symmetry + helper-extraction asymmetry). Slice-019 ran N=11 cumulative; slice-020 first-Critic ratchets to N=12 expected
  - N-surface schema-pin: M2 (first instance of asking "does this rule benefit from N=3 surfaces" — OVERRIDDEN with convention-preservation but the question is now on-record for future codification slices)

## Triage

**Triaged by**: user (Builder draft dispositions pre-authorized per /slice session "work without stopping for clarifying questions" directive; user retains override on any specific disposition by request)
**Date**: 2026-05-14
**Final verdict**: CLEAN

Mechanical verdict computation per /critique Step 4.5: 11 ACCEPTED-FIXED (first-Critic: B1+B2+B3+M1+M3+M4+M5+m2+m3+m4+m5) + 1 OVERRIDDEN (M2) + 2 DEFERRED (m1, m6) + 3 ACCEPTED-FIXED (meta-Critic: M-add-1+M-add-2+M-add-3 per /critique-review DR-1 N=7 stable) + 1 OVERRIDDEN-WITH-CLARIFICATION (M2 meta-suspicious; design.md prose-pin test assertion locks added) + 1 INFORMATIONAL (B3 meta-severity) + 0 ACCEPTED-PENDING + 0 ESCALATED → **CLEAN**.

**Post-/critique-review reconciliation**: total 14 first-Critic findings + 4 meta-Critic findings (3 missed + 1 suspicious + 1 severity-adjustment-informational) = **18 total findings ratified**. Cross-Critic-stack catch rate: 14 first-Critic + 3 missed = 17 substantive catches at slice-020 (highest single-slice cross-Critic-stack-catch in project history, exceeding slice-019's 10+2=12). 14th consecutive 100% Critic-disposition accuracy slice running 14/14 first-Critic + 17/17 cross-Critic-stack.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | design.md Step 3c content structure widened mode (a) to regex set including suffix; mode (b) elevated to PRIMARY; slice-001 false-negative anchor noted; mission-brief AC #1 cites widened shape |
| B2 | Blocker  | ACCEPTED-FIXED | design.md Step 3c content structure NEW item 4 specifies `shippability.md grep verification` mechanism; 2 NEW TF-1 rows added; mission-brief AC #1 + #2 + TF-1 plan harmonized in same fix block per TPHD-1 sub-mode (a) |
| B3 | Blocker  | ACCEPTED-FIXED | ADR-018 Reversibility section recounted to ~11 sites; mission-brief AC #3 + design.md updated; Wiegers regression-guard coverage-symmetry watch-list N=4 cumulative noted in ADR-018 itself |
| M1 | Major    | ACCEPTED-FIXED | design.md Audit 7 rewritten with "contingent N/A" framing; ADR-018 Decision "EXCEPTION" replaced with "contingent inapplicability"; DR-1 catch-class N=1 → N=2 cumulative watch-list noted |
| M2 | Major    | OVERRIDDEN | N=3 surface convention is N=6 stable; deviation costs more reader-overhead than Fowler-smell mitigation; canonical phrase appears naturally in section opener; OVERRIDDEN rationale preserves convention with explicit acknowledgement of the question for future review |
| M3 | Major    | ACCEPTED-FIXED | mission-brief.md Risk retired field reworded to "No R-N retired (methodology-internal discipline codification — latent class with no risk-register entry)" — RR-1 schema cross-section coherence preserved |
| M4 | Major    | ACCEPTED-FIXED | mission-brief Mid-slice smoke gate added prelude_present test (4 PASS expected); catches incomplete-Step-3c-insertion failure mode at ~50% build per slice-016 RPCD-1 sub-mode (b) NEW-status/token allowlist-audit class |
| M5 | Major    | ACCEPTED-FIXED | design.md Audit 4 Option C — generalized `_extract_version_body(content, version)` helper at /build-slice Phase 1a; slice-018 + slice-019 wrappers preserved; rule-of-three counter N=2 → N=3 stable; mission-brief Must-not-defer + design.md Test-first plan harmonized |
| m1 | Minor    | DEFERRED | slice-022+ /critic-calibrate aggregation pool; M3 already partially mitigates Risk-retired wording at slice-020; stylistic convention awaits N=3 evidence |
| m2 | Minor    | ACCEPTED-FIXED | methodology-changelog v0.34.0 Limitations note will name operational violation-detector at /build-slice Phase 1b; mission-brief AC #1 references via /critique m2 anchor |
| m3 | Minor    | ACCEPTED-FIXED | design.md Audit 8 clarification sentence added; post-B2 ACCEPTED-FIXED test counts updated (3 prose-pin + 4 entry/ADR-pin = 7 total; 11 TF-1 rows post-B2 verification-mechanism additions) |
| m4 | Minor    | ACCEPTED-FIXED | ADR-018 Option 3 rejection appended with /critique-time safety-net acknowledgement + round-trip cost rationale; v2 candidate at N≥3 first-Critic-MISS post-codification |
| m5 | Minor    | ACCEPTED-FIXED | mission-brief.md AC #4 added "atomic-bump count" disambiguation per slice-020 /critique m5 |
| m6 | Minor    | DEFERRED | slice-020 reflection.md "Future opportunities surfaced"; current Out-of-scope mention rhetorically tangential but not load-bearing-harmful; R-1/R-2 retirement is valid future-slice candidate via /repro + /slice cycle |
| M-add-1 | Blocker  | ACCEPTED-FIXED | ADR-018 L169 Conclusion updated to "~11 sites" per /critique-review M-add-1 propagation; B3 fix-block-completeness defect retired; recursive count-drift N=5 cumulative WITHIN slice-020 documented as NEW first-Critic-MISS class candidate at N=1 (fix-block-completeness) |
| M-add-2 | Major    | ACCEPTED-FIXED | design.md Step 3c item 4 verification-mechanism updated per /critique-review M-add-2 Option (a): DROPPED aspirational `bug:` provenance branch (zero precedent in shippability rows 1-19); rely on `tests/bugs/*` Command-cell match + verbal-claim-with-path fallback covering /repro skill L87 "or project's convention" caveat; RPCD-1 sub-mode (b) self-application N=2 stable; canonical phrase `shippability.md grep verification` preserved |
| M-add-3 | Minor    | ACCEPTED-FIXED | ADR-018 L169 wording "slimmer class than" → "slimmer count than" applied alongside M-add-1 fix in same propagation pass |
| M2 (meta-clarification) | Major    | OVERRIDDEN | First-Critic OVERRIDE preserved (N=3 convention); /critique-review M2 SUSPICIOUS rationale gap closed via design.md "Prose-pin test assertion locks" section locking `_prelude_present` to assert literal canonical phrase `bug-fix repro prelude discipline` (not merely `BFRD-1` rule ID); enforces design.md commitment via concrete test contract — rationale-strengthening, not disposition change |
| B3 (meta-severity) | Blocker  | ACCEPTED-FIXED | Disposition matches first-Critic B3 ACCEPTED-FIXED; /critique-review noted Blocker → Major severity miscalibration informationally — fix already applied + propagated per M-add-1; /reflect calibration tracking: count B3 as Major-level in first-Critic accuracy ledger; severity-miscalibration class observation noted for /critic-calibrate at slice-022+ |
