# Reflection: Slice 079 bundle-074-075-077-078-code-critic-cleanup

**Date**: 2026-05-29
**Shipped**: YES-WITH-DEFERRALS

Bundled clearance of 19 accumulated code-Critic v1 advisory findings (Fix A–S) from slices 074/075/077/078 + P1.1/P3.10 source-pending items. Voluntary-restraint discipline N=18 → bundle landed. Full suite 1125/1125; shippability 83/83; all Step-6 audits clean. No new methodology axis, no ADRs, no VERSION bump (MEPD-1(b) conformance/cleanup-discharge class — precedent slice-038/046/071, N=7 no-bump cumulative).

## Validated
- **Fix A var-scope footgun is real and the pre-amble extraction closes it** — validated by `test_build_slice_skill_branch_state_preamble.py` (pre-fix 2 FAIL: vars absent from pre-amble + only 2 numbered codefences; post-fix PASS).
- **B2/Fix S premise correction held** — design-Critic's APED-1 clause-5 grep was right: `tools/slice_queue_writer.py` is already UTF-8-explicit at all 9 sites; the structural-pin (not a fix) is the honest deliverable. Confirmed by `test_slice_queue_writer_utf8_encoding.py` passing against unmodified source + fixture-mutation contrast.
- **Fix P NamedTuple preserves tuple-equality** — the existing `test_pcr_2a_vault_claim_resolver.py:161` `candidates == [(...)]` assertion still passes alongside the new attribute-access test. Validated by 28 PCR-2a tests green.
- **MEPD-1(b) no-bump discharge** — verified by name against the META-1 `^## v…`-split assertion at `tests/methodology/test_methodology_changelog.py:136`; slice adds zero `## v…` sections → vacuously satisfies. PMI-1 confirms VERSION unchanged 0.74.0.

## Corrected
- **Forward-handoff file home** → the per-slice-folder `source-pending-items.txt` pattern (slice-075) archives with its slice and then collides with archive-immutability on any later routing edit. Corrected by establishing a LIVE top-level `[[architecture/source-pending-items.txt]]` as the stable home (user-approved 2026-05-29). The archived slice-075 file remains the frozen historical backlog.
- No design *decisions* were refuted (no ADR supersessions); the corrections below are design→code *realization* deltas, captured in build-log §Design deviations.

## Discovered
- **Design→code translation gap, N=15 cumulative** — three realization deltas this slice, all where the committed Phase-B test (code-is-truth) was stricter/different than design.md prose:
  1. **Fix E corpus invariant is global across 4 files, not the 2 design named** — `test_helper_defined_only_once_in_test_corpus` greps ALL `tests/methodology/test_*.py`; `test_build_slice_skill.py` + `branch_state_preamble.py` also defined `_branch_state_section`. Deduped all 4.
  2. **Fix P needed a NamedTuple, not just a sentinel-string change** — the committed test used `.name`/`.parallel_safety` attribute access; the parser returned plain tuples. `_QueueCandidate` NamedTuple satisfies both surfaces.
  3. **The Phase-B unused-imports meta-test had a `__future__` false-positive** — counted `from __future__ import annotations` as an unused import (could never pass); fixed the AST walker to skip `__future__`.
  - Impact: reinforces that Phase-B-scaffolded WRITTEN-FAILING tests are the binding contract; design prose is the intent. The 3-Critic stack's code-Critic catches the design-realization gap the design+meta-Critic stack structurally cannot.
- **All-tests-scaffolded-in-Phase-B vs phase-by-phase-build collides with the `-x` mid-slice smoke gate** — `pytest tests/methodology -x` halts at the first not-yet-built phase's WRITTEN-FAILING test, reading as a gate FAIL when it's actually the expected pre-fix state. Diagnosed in-substance (984 pass / 8 fail = exactly the un-built Phase F+G tests; zero regressions). Impact: a bundled-cleanup slice that scaffolds all regression tests up front should interpret the smoke gate as "all-built-so-far pass + no pre-existing regression," not literal `-x` exit 0.
- **AC#5 spec-vs-archive tension** — an AC written at /slice time against a then-live handoff file becomes structurally unsatisfiable once that file archives. Impact: ACs that mandate edits to *another slice's* artifacts should pre-carve-out the archive-immutability path (as DEFER-1/3/4/5 did) rather than surface as a validate-time PARTIAL.

## Deferred
- **DEFER-1..5** (design.md): slice-075 m2, slice-077 M1+m1 (→ parallel-slice-family-parity-audit), m2+m7+m10, slice-078 m4 — archive-immutability + extraction-trigger. NOT-YET re-score in their owning future slices.
- **DEFER-6** (new, user-approved 2026-05-29): AC#5 source-pending-items.txt text-removal sub-clause — archive-immutability carve-out; substantive fix+test met; forward handoff authored at `architecture/source-pending-items.txt`.
- **P3.10'** `find-real-mojibake-source` — routed to the live source-pending tracker; candidate for a future slice (not slice-080 PCR-2b LARGE).
- **code-review m1** (dead `diag` param) — WON'T-FIX (renaming breaks the pinned 6-arg signature test; docstring documents intent).
- **code-review m3** (Fix B pathspec enumeration) + **m4** (Fix S fixture-mutation fragility) — latent/low; noted for a future hardening candidate.

## Critic calibration

Per TRI-1, scored against `critique.md` §Triage dispositions + reality observed during build/validate/code-review. The design-Critic findings were all design-time fixes (pre-build), so "VALIDATED" = the Critic was right and the corrected design is what shipped clean.

- **B1** (Fix K wrong reason-keys): **VALIDATED** — APED-1 clause-5 grep caught the cited keys belonged to a different tool; corrected canonical `_UNKNOWN_REASONS` keys are exactly what Fix K implemented; `test_unknown_warn_templates.py` byte-equal invariant passes. APED-1 clause-5 effective on its first governed slice (N=1 catch, not miss).
- **B2 + M3** (Fix S premise empirically false): **VALIDATED** — build confirmed the helper was already UTF-8-correct; the reframe to structural-pin was the only honest path.
- **M1** (Fix K MAP-ONLY demote): **VALIDATED** — implemented MAP-ONLY; no JSON/CLI widening; MEPD-1 EXCLUDE preserved.
- **M2** (Fix O `# pragma: no cover` pick): **VALIDATED** — implemented; and the code-Critic's later M1 confirmed the defensive branch is genuinely unreachable via the resolver (pragma justified).
- **m1** (WIRE-1 exemption note), **m2** (Fix L AND-only), **m3** (precedent N=7 count), **m4** (AC#3 12-not-13), **m5** (effort estimate): **VALIDATED** — all cosmetic/scoping design fixes; reality consistent.
- **m6** (shippability row enumeration deferred to Phase A): **VALIDATED** — Phase A enumerated rows 79-84 with SCPD-1 propagation in the same block; no propagation hazard materialized.
- **M-add-1** (meta-Critic: signature 4-arg not 2-arg): **VALIDATED** — the actual pre-fix signature was 4-arg `(diag, result, timestamp, head_sha)`; Fix O extended 4→6 exactly as the corrected design specified.

**Missed by Critic (design+meta stack)**: the code-Critic (post-build) surfaced **M1 — Fix O's DRY claim was structurally pinned but not behaviorally verified** (design.md row O's behavioral test was not realized; a re-derive regression would pass all structural pins). The design-Critic structurally cannot reach this (it reads design.md, not the realized test bodies). Addressed in-loop by adding the behavioral discriminator. Also missed (necessarily, being code-realization details): the 3 design→code deltas above (Fix E 4-files, Fix P NamedTuple, meta-test `__future__`).

**Pattern**: the 3-Critic stack complementarity holds at **N=14 cumulative** (slice-063→079) — design-Critic + meta-Critic catch design-surface defects (B1/B2/M-add-1) at /critique time; code-Critic catches design→code realization gaps (Fix O behavioral-test absence) at /code-review time that are STRUCTURALLY UNREACHABLE by the design stack. Do NOT collapse the stack. APED-1 clause-5 (first governed slice) added empirical-grep teeth to the design-Critic — B1+B2 are its first catches.

## Lessons for next slice
- Treat Phase-B-scaffolded committed tests as the binding contract over design.md prose — when they disagree, the test wins (code-is-truth); reconcile by widening the fix to satisfy the test, and log the delta.
- For bundled-cleanup slices that scaffold ALL regression tests up front, interpret the `-x` mid-slice smoke gate as "everything built-so-far passes + no pre-existing regression," not literal exit 0 — the un-built phases' WRITTEN-FAILING tests are expected.
- ACs that mandate editing another slice's artifacts must pre-carve-out the archive-immutability path at /slice time (DEFER-shaped), or they surface as validate-time PARTIALs.
- When a design row promises a behavioral test, realize the behavioral test — not just a structural signature/source-grep pin that can't discriminate the defect it guards against (code-review M1).

## Vault updates made (thin vault — small list)
- [[architecture/source-pending-items.txt]] — NEW live top-level forward-handoff tracker (stable home; P3.10' routed; P1.1/P1.2/P3.10 recorded closed; pointer to archived slice-075 backlog).
- [[architecture/shippability.md]] — rows 79-84 (added in /build-slice Phase A; one cluster per fix-group A-S).
- This slice's [[build-log.md]] — §Design deviations records the 3 design→code deltas.
- No ADR supersessions; no risk-register edits (no R-NN transition; design→code-gap recurrence tracked via aggregated lessons N=15, not a risk entry).
