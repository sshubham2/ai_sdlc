# Critique Review: Slice 095 harden-skill-driven-vault-writes

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-01
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

(First Critic: 2 blockers, 3 majors, 2 minors. Meta-Critic: EXTEND — 0 suspicious, 2 missed (M-add-1/M-add-2), 0 severity adjustments.)

## Summary

The first Critic's review is substantively strong — B1 (the ADR-029 prose-inspection over-claim) and M2/M3 (RMW-is-the-primary-hazard, exemption silent-bypass) cut at real load-bearing claims and the post-fix design/ADR address them well. But B2 — the finding whose entire value proposition was "I EXECUTED the matcher, which is how I found the real gaps" — is **itself incomplete**: the re-enumerated mutator table still omits two directive-shaped `risk-register.md` mutation sites (`user-test:115`, `validate-slice:291`). The Critic's own APED-1 grep under-ran the corpus, recursively reproducing the exact failure mode B2 diagnoses. That gap also de-completes the M3 reason-enum. This is an EXTEND, not a mere ADJUST.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1: AC2 prose-audit is the ADR-029-rejected shape** — confirmed; severity Blocker is appropriate. design.md §"Why SVW-1 is acceptable despite ADR-029" + ADR-087 §Consequences now correctly scope the guarantee to the prose-detection surface and ground the no-content-oracle distinction against BCI-1's `canonical_project_checks.md` fixture. Sound (Wiegers — claims must be verifiable; the corrected claim now is). Nuance in Notes: "structurally unconstructible" is marginally too strong.
- **B2: enumeration incomplete + corpus mis-stated (23→26)** — the *finding* is confirmed VALID and correctly a Blocker; the corpus-size correction and the `/repro` + `/supersede-slice` additions are real. But the *fix* is incomplete — see Missed findings (this is why the verdict is EXTEND, not ACCEPT).
- **M2: deferred RMW is the more dangerous half** — confirmed; Major is appropriate. Consistency check passed: no remaining design/ADR text still claims 094+095 close the `/reflect`+`/archive` concurrency hazard. design.md L49 + §R-32 disposition + ADR-087 consistently scope closure to the write/**append** axis and name RMW as a flip-slice must-not-defer.
- **M3: exemption marker is a silent-bypass vector** — confirmed; Major is appropriate. The closed reason-enum + pinned `_REGISTERED_SKILL_EXEMPTIONS` allowlist genuinely closes the R-7 `# noqa` hole; "edit the allowlist" trips `test_exemption_allowlist_pinned` (slice-041 pattern), so the bypass is not merely relocated. Caveat: the reason-enum's *completeness* is undercut by the B2 gap — see Missed findings.
- **m1: stale "no merge-time PCR" framing** — confirmed; Minor. design.md §R-32 disposition now cites [[ADR-066]] and scopes the hazard "strictly POST-flip."
- **m2: VERSION/changelog second-merger checklist** — confirmed; Minor. design.md §Sequencing note carries the concrete 4-step checklist.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives second-pass scrutiny against the post-fix design — none is a false positive or over-reach. (The first Critic did not over-file; if anything it under-filed, per below.)

## Missed findings

- **M-add-1: The B2 re-enumeration is STILL incomplete — two directive-shaped `risk-register.md` mutation sites are absent from the "code-grounded enumeration"** (Newman — enumerate every mutation site before claiming a completeness gate; and the slice's own APED-1 "execute, don't reason"). An independent grep of all 26 `skills/*/SKILL.md` for imperative-at-clause-start mutation verbs co-located with a backticked shared-aggregate filename surfaces two sites the design's mutator table omits:
  - `skills/user-test/SKILL.md:115` — "Add to `architecture/risk-register.md` with reversibility tag" (append-class, directive-shaped).
  - `skills/validate-slice/SKILL.md:291` — "add to `architecture/risk-register.md` immediately (don't wait)" (append-class, directive-shaped).

  Both are imperative-at-clause-start + a backticked `architecture/risk-register.md` path — they match the design's own M1 directive-shape matcher spec, so a correctly-built audit **will fire on them** and, having no disposition, will either (a) emit a VIOLATION mid-build (forcing an unplanned route/exempt decision), or (b) the matcher misses them too — in which case the B1-corrected "completeness over the prose-detection surface" claim is itself false. Same APED-1 under-execution the first Critic's B2 diagnosed in the Builder, now present in the Critic's own grep. **Proposed fix**: add `/user-test` (`:115`) and `/validate-slice` (`:291`) to the mutator table with an explicit disposition before build; record them in the build-log FP/FN count.

- **M-add-2: The closed exemption reason-enum `{deferred-rmw, project-open-single-shot}` does not cover the `/validate-slice` site M-add-1 surfaces** (coupled to M3; fail-closed default — an unclassifiable site must have a *valid* classification available, or the gate dead-ends). `/validate-slice` runs **per-slice at slice-end** — precisely the parallel-slice concurrency window — so it is NOT `project-open-single-shot` (that reason is justified for `/triage` you-don't-run-twice-in-parallel; `/validate-slice` you demonstrably DO run in parallel across slices). The `:291` write is an *append* of a new risk entry (non-clobbering, safer class), so the honest disposition is **route → `vault_edit append`**, not exempt. If exempted instead, the reason-enum would need a third value (e.g. `concurrent-append-reality-surprise`) — meaning the "closed enumeration" M3 ships is not actually closed over the real corpus. **Proposed fix**: route `/validate-slice:291` and `/user-test:115` through `vault_edit append` (both appends), keeping the reason-enum at two values; OR if deferred, extend the enum and justify. Decide at TRI-1.

## Severity adjustments

No severity adjustments. Every confirmed finding is filed at the correct severity. (B2 stays a Blocker; the EXTEND adds to its remediation rather than re-grading it.)

## Notes

Confidence in the MISSED findings is high — grounded in a live grep of the real 26-skill corpus (`user-test:115`, `validate-slice:291` are reproducible directive-shaped sites), independently re-verified by the Builder. Calibration observation on the first Critic: thorough and correctly un-lenient (zero false positives, sharp B1/M3), but its single most-load-bearing finding (B2, "I executed the matcher") under-executed the corpus — found 2 of 4 unenumerated sites. Highest-value calibration signal: an "I executed it" claim is only as good as the query's coverage; a partial grep that *reports* completeness is more dangerous than an admitted-incomplete reasoning pass (it manufactures false confidence — the exact anti-pattern B2 was filed against). Two explicit reservations: (1) On B1, design's phrase "structurally unconstructible" is marginally too strong — a *content* oracle is genuinely unconstructible, but a tamper-evident append-sequence/receipt oracle over the shared log IS conceivable (and is a queued project-frame candidate, "add-claim-sequence-number"), which could one day reconstruct an ADR-029-Option-3-style gate. Does not change B1's verdict (out of this slice's scope; design honestly scopes SVW-1 to drift-prevention) — noted so "unconstructible" isn't carried forward as settled. (2) M1 (PENDING) is correctly deferred and its directive-shape spec is deterministically implementable — `build-slice:394` is excluded by the closed verb-lexicon-at-clause-start rule ("flip" is neither in the lexicon nor clause-initial), so "exclude past-tense prose" is belt-and-suspenders, not a load-bearing NL requirement. But M1's correct execution is what will surface M-add-1's two sites at build — so M1 and the EXTEND are coupled: fixing the table at TRI-1 is the difference between a planned disposition and a mid-build surprise.
