# Reflection: Slice 081 fix-drift-check-enforcement-gap

**Date**: 2026-05-29
**Shipped**: YES

## Validated
- DCE-1 procedural was-it-marked gate closes the silent-skip hole — validated by self-application (`tools.drift_check_audit` exit 0 on slice-081's own tree after its `/drift-check` wrote a `**Trigger**: slice-081` marker) + 25/25 unit tests.
- The CRP-1 template is a clean clone target — validated by byte-faithful reuse of `_frontmatter_*` / `_resolve_mode` / `_SKIP_VALUE_RE` (em-dash) / exit mapping, confirmed by the code-Critic's cross-cutting-conformance pass.
- Procedural-not-semantic was the right scope (Option A) — validated by zero false-positive surface in the regex battery (slice number is a unique freshness key) and the honest residual-gap disclosure surviving code review.

## Corrected
- None. No design claim was refuted by reality; ADR-073 ↔ code matched exactly. The in-band changes (m1 left-anchor, m2 AC5 "4-part"→"5-part") were refinements/corrections to the slice's OWN artifacts during code-review, not vault corrections.

## Discovered
- **The matcher's left-anchor gap (code-Critic m1)**: `slice[- ]?0*{n}\b` was right-anchored only; `xslice-081` would have matched as a substring. Near-zero real exposure (gated to `**Trigger**:` lines that only ever carry `slice-NNN`), but the docstring's "slice-anchored" claim overstated the regex. Fixed in-band (`\bslice...`). Impact: a reminder that "anchored" claims need BOTH sides asserted in the test battery.
- **New-audit-tool + version-bump slices have a wide second-order drift surface**: 8 realignments fired (STP-1 prose-pin, INSTALL count 32→33, changelog rule-reference line, version-sync test rename `_0_75_0`→`_0_76_0`, cp1252 `_POSITIONAL_SLICE_TOOLS`, VAULT_ROOT `_MIGRATION_SITE_ALLOWLIST`, orphan-`architecture/`-literal markers, pulse-inventory 32→33 pin, shippability row #75 stale function-name citation). All were CAUGHT by existing gates (STP-1 + the full suite) — the discipline net held — but the count is high. BC-PROJ-7 covers only 2 of these sites (cp1252 + shippability row); the rest are uncovered by an enumerated checklist.

## Deferred
- **Mechanical-subset drift verification** (Option B from ADR-073) — deliberately out of scope; DCE-1 enforces the procedural "was-it-run", not the semantic correctness. If a future need to independently re-verify cheap mechanical drift (ADR-lib-vs-pyproject, referenced-path existence) emerges, it's a separate slice. Lands in: backlog.
- **Git pre-commit hook delivery** — out of scope per mission-brief; DCE-1 enforces at Step 6 only. Lands in: backlog (separate decision).

## Critic calibration

Design-Critic (`/critique`) + meta-Critic (`/critique-review`) findings scored against build/validate reality:

- **B1** (marker-token `slice-NNN` vs producer `sliceNN`): **VALIDATED** — ACCEPTED-PENDING; the producer template genuinely emitted `sliceNN` (verified `skills/drift-check/SKILL.md:114`); without the fix the gate would false-refuse. Real.
- **B2** (Step 7b `drift-check-skip:` preservation undelivered): **VALIDATED** — ACCEPTED-PENDING; `skills/build-slice/SKILL.md:494` genuinely preserved only `critique-review-skip:`; the clobber-then-false-refuse lifecycle was real. STP-1 even caught the pin-realignment side-effect.
- **M1** (design names nonexistent `tools/crp_audit.py`): **FALSE-ALARM** — the meta-Critic correctly graded this SUSPICIOUS; the premise was a hallucinated filename (design always cited the real path). The salvaged residue (enumerate verbatim literals) was useful, but the finding as filed was over-reach.
- **M2** (was-it-marked not was-it-run; `--fast` writes nothing): **VALIDATED** — ACCEPTED-PENDING; the honest reframe + full-mode pin was correct and survived code review.
- **M3** (AC#4 collapsed multi-leg bump): **VALIDATED** — ACCEPTED-FIXED; the 5-part bump + entry-pin genuinely needed splitting out (and code-Critic m2 later caught that even the split said "4-part").
- **m1/m2/m3**: VALIDATED (mode-regex inheritance, PTFFD-1 miscitation, hook-out-of-scope) — all real, cheap, fixed.
- **M-add-1** (meta-Critic missed-finding: unanchored regex → false-ACCEPT via cross-slice mention): **VALIDATED** — the single most valuable finding of the slice. Neither the Builder nor the first Critic caught it; the meta-Critic verified it against 29 real cross-mention lines in `drift-log.md`. Had it shipped, the gate would have been silently defeated for any slice cross-mentioned by a prior entry — reopening the exact R-7 class the slice closes.
- **m-add-1** (meta-Critic: bootstrap entry needs a `**Trigger**:` line, not just a heading): **VALIDATED** — correctly anticipated; the bootstrap drift-log entry was written with an explicit `**Trigger**: slice-081 pre-finish gate` line and self-application passed.

**Missed by Critic**: the code-Critic's m1 (left-anchor gap) was missed by BOTH the design-Critic AND the meta-Critic (who reasoned about the matcher but only on the right-side collision direction). The code-Critic — reading the actual regex — caught it. This is the 3-Critic stack working as designed: design-Critic catches conceptual/contract gaps, meta-Critic catches the symmetric-direction false-ACCEPT, code-Critic catches the line-level regex anchor. Three distinct defect classes, three personas.

**Pattern**: the meta-Critic's false-ACCEPT catch (M-add-1) and the code-Critic's left-anchor catch (m1) are the SAME underlying class — "an anchoring claim asserted in prose but not fully delivered/tested" — surfaced from two directions (cross-mention vs left-prefix). N=1 here; worth watching at `/critic-calibrate` whether matcher/regex slices recurrently under-test anchoring.

## Lessons for next slice
- **For any matcher/regex that claims to be "anchored", assert BOTH boundaries in the test battery** — slice-081's regex was right-anchored + tested, left-anchored only after code-review. A single "anchored" claim hides two obligations.
- **BC-PROJ-7 (new-audit-tool checklist) covers only 2 of the ~6 second-order sites a new VAULT_ROOT-consuming + version-bumping audit-tool slice must touch** — the cp1252 list + shippability row are enumerated, but the VAULT_ROOT migration allowlist, INSTALL.md count, the per-slice version-sync test rename, and the entry-pin pair are not. Candidate: extend BC-PROJ-7 (or mint a sibling) to enumerate the full new-audit-tool inventory fan-out so the count of "caught-late-by-full-suite" realignments drops.
- **The CRP-1 → DCE-1 clone is a reusable template**: procedural "was-an-artifact-produced" gates (CRP-1 critique-review.md, DCE-1 drift-log marker) share a structure. A future procedural gate should clone the same skeleton.

## Vault updates made (thin vault)
- [[decisions/ADR-073-drift-check-enforcement-gate.md]] — created (DCE-1; reversibility cheap).
- [[methodology-changelog.md]] — v0.76.0 DCE-1 entry (+ installed forward-sync, MCFS-1).
- [[shippability.md]] — rows #86 (BFRD-1 repro) + #87 (DCE-1 gate critical path).
- [[risk-register.md]] — no new risk registered (the closed gap was a fresh user-reported defect, un-numbered; the residual was-it-marked gap is disclosed in ADR-073, not a tracked risk — the producer/consumer contract is pinned by tests).
- No `components/`/`contracts/`/`schemas/` updates (thin vault — code is truth).
