# Reflection: Slice 107 inventory-vault-flip-prose-surface

**Date**: 2026-06-03
**Shipped**: YES

## Validated
- Boundary-free `re.finditer` matcher enumerates the full prose surface — validated: 318 == raw `grep -rohE` count; `code-review.md:103` yields 5 intra-line matches with distinct columns (a single `re.search` would have undercounted 318→286).
- Disjointness from the parallel slice-106 (AC5) — validated: `vault_flip_readiness_audit --strict` exits 0, production `must-rewrite` unchanged at 4. The new tool adds no slashed literal `readiness_audit` would flag.
- The standalone-third-surface design (ADR-096) — validated: mirroring `readiness_audit`'s CLI/exit-code contract made the M4 operator story trivial; keeping it a separate file preserved disjointness from 106's `_BASELINE` re-pin.
- `repr()`-of-tuple SHA-256 baseline input is deterministic across CPython/platforms — validated by the code-Critic (no dict/set in the structure).

## Corrected
- **design.md ruleset (as-designed inline-code→`needs-human`) → reality is in-code/operational→`rewrite-at-flip`** — the B2-ratified default was corpus-mis-calibrated (124 `needs-human`, overwhelmingly live operational refs). Corrected in `design.md` §Build-time recalibration + mission-brief AC2 (⚠ AS-BUILT callouts); build-log records the deviation. User-ratified.
- **design.md/ADR-097 in-module multiset baseline → reality is in-module SHA-256** — inlined slashed-path tuples self-pollute `readiness_audit` (collection-member + `/` → `needs-human`), violating AC5. Corrected in `design.md` §Baseline/§Data-model + mission-brief AC3 (⚠ AS-BUILT); ADR-097 5-tuple key unchanged. FORCED by AC5, not discretionary.
- No ADR superseded (ADR-096/097 amended in-round before merge via design.md callouts, not after-the-fact — append-only history intact; the deviations refine, not reverse, the ADRs' decisions).

## Discovered
- **The operational prose surface is ~100% rewrite-at-flip (318/0/0/0).** Every operational prose reference names the CURRENT vault location, so the M4 flip must rewrite essentially ALL 318 sites — `historical-anchor` ≈ 0 on this surface (genuine preserve-anchors live in vault-INTERNAL prose, which is out of scope). **Impact**: the M4 prose-rewrite slice is large (318 edit sites) — plan it as a mechanical-but-wide cut, not a quick one.
- **A no-AST lexical classifier's vocabulary must be enumerated against the corpus's ACTUAL forms.** The `\bread\b` word-boundary missed `Reads`/`Produces` (inflected frontmatter verbs), silently routing 2 live paths to the off-checklist `doc-example` — found only by the code-Critic executing the corpus (M1). Impact: any future lexical/verb-driven classifier needs corpus-vocabulary validation, not a hand-guessed verb list.
- **The inventory baseline (SHA-256 + 5 `_RESIDUAL` line numbers + count-floor) is corpus-snapshot-pinned.** Any routine skill edit that adds/removes a vault-path reference will trip `--strict` and require re-pinning (same maintenance profile as `readiness_audit._BASELINE`). Expected, not a defect — but the M4 flip + any prose-touching slice must re-pin.

## Deferred
- **The M4 flip itself** (physical move of `architecture/`+`diagnose-out/` + `VAULT_ROOT` default flip + `git rm --cached` + the 318-site prose rewrite) — reason: this slice is inventory-only (the prerequisite checklist); the rewrite is M4. Lands in: the M4 flip slice (now unblocked on the prose surface — the checklist exists).
- **`historical-anchor` curation for vault-internal prose** — if the flip ever needs to preserve in-vault citations, that's a separate (out-of-scope) surface. Lands in: backlog, only if M4 needs it.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed at build/validate/code-review:

- **B1** (anchored regex drops literals): **VALIDATED** — ACCEPTED-FIXED; the boundary-free fix was genuinely needed (anchored caught only 69/318, Builder-re-verified). The meta-Critic corrected the first Critic's gap-arithmetic (285/33 → 69/249) — itself a VALIDATED meta-finding.
- **B2** (inline-code→non-gating doc-example): **VALIDATED** — ACCEPTED-PENDING; the doc-example mis-route was real AND recurred: the code-Critic's M1 found the design's fix wasn't fully closed (the verb-gap left 2 paths in doc-example). B2's concern was right twice over.
- **B3** (count inconsistency): **VALIDATED** — ACCEPTED-FIXED; boundary-free reconciled tool==grep==318.
- **M1** (self-pollution under-specified for path-construction): **VALIDATED** — ACCEPTED-FIXED; AC5 disjointness was real and manifested HARDER than the Critic predicted — not just path-construction, but the in-module *baseline data* self-polluted, forcing the SHA-256 deviation.
- **M2** (disposition key cross-line collision): **VALIDATED** — ACCEPTED-FIXED; the 5-tuple key was needed (`code-review.md:103`).
- **M3** (ADR-096/097 collision with slice-106): **NOT-YET** — ACCEPTED-FIXED via the user-ratified reservation (106→098+); the collision is prevented, not yet materialized. Re-score when slice-106 runs `/design-slice`.
- **m1** (taxonomy strings), **m2** (baseline class coverage): **VALIDATED** — both cheap, both correct.
- **M-add-1** (meta: intra-line multi-match): **VALIDATED** — the column-offset 5th key component + `re.finditer` were both load-bearing (`code-review.md:103` = 5 same-line matches).
- **M-add-2** (meta: TF-1 deviation): **VALIDATED** — flipping to Test-first paid off: the 16 tests are what made the build's recalibration + the code-review M1/M2 fixes safe to apply.
- **m-add-1** (meta: bare-`diagnose-out` residual): **VALIDATED** — the residual was enumerated (5 bare-`architecture` args; bare-`diagnose-out` turned out empty — the meta-Critic's examples were actually slashed).

**Missed by Critic** (the headline calibration signal):
- **Neither the design-Critic NOR the meta-Critic caught that the B2-ratified ruleset (inline-code→needs-human) would produce 124 needs-human on the REAL corpus.** Both reasoned about the ruleset at design-time but could not RUN it; the corpus mis-calibration surfaced only at BUILD execution (AP-3 / APED-1). The dual-Critic stack is structurally blind to ruleset *calibration* — only execution against the real corpus reveals it.
- **Neither caught that an in-module slashed-path baseline would self-pollute `readiness_audit`.** The Critic flagged path-CONSTRUCTION self-pollution (M1) but not baseline-DATA self-pollution; found at build when `test_disjoint` failed.
- The **code-Critic DID catch** the verb-gap (M1) that the design+meta stack structurally could not (they don't execute the classifier). This is the 3-Critic complementarity (AP-19) confirmed: design-Critic + meta-Critic + code-Critic caught non-overlapping defect classes.

**Pattern**: For a classifier/ruleset slice, design-time review (even dual-Critic) validates STRUCTURE but is blind to CALIBRATION against the real corpus. Two of the three most consequential findings this slice (the recalibration, the verb-gap) were execution-only. This is the Nth confirmation of AP-3/APED-1 — and a calibration signal that a ruleset slice should be EXPECTED to recalibrate at build, with the test harness in place first (M-add-2's TF-1 flip is what made that safe).

## Lessons for next slice
- The M4 flip's prose-rewrite is ~318 sites — scope it as a wide mechanical cut driven by the `vault_flip_prose_inventory --json` output as the checklist.
- A lexical/no-AST classifier slice should plan for a build-time recalibration pass against the real corpus, with the Test-first harness written first (so the recalibration is safe).
- When a baseline must pin many literals, an in-module hash (not inlined literals) avoids self-poisoning sibling lexical audits that scan the same `tools/*.py` surface — a reusable pattern for any future audit that pins vault-path data.

## Vault updates made (thin vault — small list)
- This slice's [[design.md]] — corrected the ruleset (recalibration) + baseline (SHA-256) to as-built, with ⚠ AS-BUILT callouts (build-log records both deviations).
- This slice's [[mission-brief.md]] — AC2/AC3 harmonized to as-built (318/0/0/0; SHA-256 baseline).
- [[architecture/shippability.md]] — row 113 added at build (slice-107 critical path) — the Step 5.3 contribution is already present.
- [[architecture/drift-log.md]] — slice-107 entry (DCE-1).
- [[architecture/lessons-learned.md]] — appended (Step 5).
- No risk-register change: this slice contributes to R-32 flip-readiness (prose surface) but does NOT retire it (R-32 retires at the M4 flip); no reality surprise warranting a new risk.
