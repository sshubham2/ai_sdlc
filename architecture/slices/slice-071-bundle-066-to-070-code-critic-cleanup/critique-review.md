# Critique Review: Slice 071 bundle-066-to-070-code-critic-cleanup

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-26
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's twelve findings are substantively correct — B1 (broken regex empirically demonstrated), B2 (mission-brief↔design contradiction), and M1-M6 + m1-m4 are all VALID with correct severities. Builder applied 10/12 ACCEPTED-FIXED in-band edits, but the fix-block introduced **four new sibling-cell sweep gaps** + carries one latent contradiction the first Critic surfaced but the fix did not fully close. Adding 4 missed/regression findings; no severity adjustments to existing findings. **N=5 cumulative Builder-fix-block-introduced-regression pattern** (slice-022/067/068/070/071) — meta-Critic's structural specialization continues to validate.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (broken `_PATH_SHAPED_RE` regex): VALID, severity Blocker correct. Critic's empirical claim verified via `/c/Users/sshub/.claude/.venv/Scripts/python.exe` — the original three-alternative regex returns `True` on `unknown`, `Makefile`, `abc`, `.gitignore`, `.env`. The replacement regex (lifted from `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295`) returns `False` on `unknown`/`Makefile`/`abc` and `True` on `.gitignore`/`.env`/`file.HTML`/`file.cfg`/`tools/foo.py` as advertised. Builder's option (a) fix at design.md L65 is correct.
- **B2** (mission-brief↔design "zero edits" contradiction): VALID, severity Blocker correct. Builder's fix at mission-brief L42 + L94 rephrases to "NO new `## v0.71.0` entry" + "retroactive in-place TEXT corrections to the existing `## v0.70.0` entry are permitted" — both surfaces now internally consistent and consistent with design.md L82-91. FBCD-1 sub-mode (a) honored.
- **M1** (AC#3 finding-count bookkeeping): VALID, severity Major correct. Builder's fix at mission-brief L30 includes `M2` in the AC#3 verification regex; mission-brief L34 Note is rewritten (not deleted) to correctly identify M2 as the multi-part finding whose paired-pin half is still outstanding. The rewrite is an acceptable variant of Critic's option (a).
- **M2** (slice-069 m6 ACKNOWLEDGED-NO-FIX → DEFER-AGAIN relabel): VALID, severity Major correct. Builder's fix at design.md L182 relabels disposition + L200 Disposition totals now reads "DEFER-AGAIN = 1 (slice-069 m6)" + L202 narrative carries the honest framing. RSAD-1 prose-honesty discipline preserved.
- **M3** (slice-070 M1 FIX under-specification): VALID, severity Major correct. Builder's fix at design.md L59-64 enumerates the 4-step canonical algorithm. Build-time decisions eliminated.
- **M4** (1-day estimate empirically unrealistic): VALID, severity Major correct. Builder's fix at mission-brief L4 revises to "1-2 days (LARGE+)" + cites mid-slice smoke gate as pressure-valve.
- **M5** (test-first-by-other-name RSAD-1): VALID, severity Major correct as filed (see missed-finding **M-add-2** below for residual partial-fix sweep gap — the surface "RED-first" label is removed but Phase B1/B2/B3 ordering still semantically implements test-first).
- **M6** (sentinel-test escape-soup): VALID, severity Major correct (see missed-finding **M-add-1** below — Builder's fix substring assertions DO NOT match the proposed docstring prose; the structural defect Critic warned about manifests inside Builder's M6 fix-block itself).
- **m1** (WIRE-1 zero-row claim unverified): VALID, severity Minor correct. Meta-Critic empirically verified — `$PY -m tools.wiring_matrix_audit architecture/slices/slice-071-.../design.md` returns "No wiring matrix violations." Builder's ACCEPTED-PENDING is now empirically pre-validated; can be discharged.
- **m2** (N=9/9 unverified): VALID, severity Minor correct. Builder's fix at design.md L238 replaces "N=9/9" with qualitative "consistently positive" — discharged.
- **m3** (20-min prose-split estimate): VALID, severity Minor correct. Builder's fix at design.md L90 softens to "30-60 min depending on forward-reference preservation".
- **m4** (constant↔docstring drift-prevention test): VALID, severity Minor correct (see missed-finding **m-add-1** below — Builder's ACCEPTED-PENDING promise is not reflected in design.md L69 / L198).

## Suspicious findings

**None.** Every first-Critic finding is grounded in a verifiable design.md/mission-brief.md citation; B1's empirical claim is meta-confirmed; M2/M3/M4/M5/M6 are all RSAD-1 / FBCD-1 / APED-1 frame-conformant. The first Critic did not over-reach on any finding.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### M-add-1 (Major): M6 fix-block specifies sentinel-test assertions that DO NOT match the proposed docstring prose — the RSAD-1 anti-pattern Critic M6 warned about manifests inside Builder's M6 fix-block itself

- **Claim under review**: design.md L124 specifies the sentinel test's assertions: `assert "two-marker convention" in __doc__` + `assert "argparse help" in __doc__` + `assert "intentionally unmarked" in __doc__` + `assert "slice-071 design.md §m3" in __doc__`. The proposed docstring prose: "Two-marker convention applies only to lines matched by `literal_re` at L118 of this module; substring-in-prose sites at argparse help / error messages / log strings are intentionally unmarked per slice-071 design.md §slice-068-m3 disposition."
- **Issue (empirically verified via Python execution)**:
  - `"two-marker convention" in doc` → **False** (docstring starts capitalized "Two-marker convention"; case-sensitive substring fails)
  - `"slice-071 design.md §m3" in doc` → **False** (docstring contains `§slice-068-m3`, not `§m3` — non-consecutive substring)
  - `"argparse help" in doc` → True
  - `"intentionally unmarked" in doc` → True
  - **Two of four assertions would fail against the docstring as specified.**
- **Framework**: APED-1 (Dim 9) — when the slice introduces an assertion-against-prose pin, the assertion MUST be empirically executed against the actual prose; Critic M6 explicitly flagged this obligation; Builder's M6 fix did not honor it.
- **Compound impact**: the fix-block edit instantiates exactly the asymmetry-between-documented-and-asserted defect Critic M6 was closing. **Recursive RSAD-1 violation**: the test claiming to pin the documented asymmetry IS the asymmetry's first failure mode.
- **Proposed fix**: align assertions to docstring verbatim — change to `assert "Two-marker convention" in __doc__` (capital T) AND `assert "slice-071 design.md §slice-068-m3" in __doc__`. Verify via `python -c 'doc = "..."; assert ...; ...'` BEFORE landing in design.md.
- **Severity rationale**: Major — repeats exact failure mode Critic M6 closed; would be detected at test-execution time but counts as design-time defect Critic asked Builder to verify-before-landing.
- **Builder draft**: pending

### M-add-2 (Major): M5 fix removes "RED-first" prose at §Test-first postures but does NOT sweep Phase B1+B2+B3 ordering that still implements test-first semantically

- **Claim under review**: design.md L242 (§Test-first postures) says "11 regression-pin tests added ... written alongside their paired source-side FIXes ... tests-paired-with-FIXes is the consistent posture". But design.md L250 (Phase B1) enumerates ONLY test-additions ("slice-068 M1 + m1 + m2 + m3 + slice-066 m1 support + slice-070 M2/M5/M6/m1/m2 tests"); L251 (Phase B2) enumerates source-side FIXes for `tools/slice_queue_writer.py` and concludes "**After this batch, the Phase B1 tests for slice-070 should GREEN**" — presupposing those tests are RED in Phase B1 (i.e., written before their source-side FIXes land). L252 says the same about slice-066 ("After this batch, Phase B1 tests for slice-066 should GREEN").
- **Issue**: Phase B1 tests RED → Phase B2/B3 source GREEN them IS test-first ordering with the "RED-first" label scrubbed. The Critic's M5 substantive concern (test-first-by-other-name RSAD-1) is **not closed** — only the surface-level "RED-first" label is removed.
- **Framework**: RSAD-1 (Dim 9) + FBCD-1 sub-mode (a) — partial sweep.
- **Proposed fix**: restructure Phase B1/B2/B3 into per-cluster paired phases (each cluster lands test + source-side FIX together), OR honestly flip `test-first: true` and add a TF-1 plan table. Per Critic M5 option (b) intent: per-cluster paired is the cheaper structural fix.
- **Severity rationale**: Major — same as the original M5; the fix-block edit was an incomplete sweep that gave the surface label removal without the substantive ordering change.
- **Builder draft**: pending

### m-add-1 (Minor): Builder's m4 ACCEPTED-PENDING constant↔docstring drift-prevention test is not actually inscribed in design.md

- **Claim under review**: Critic m4 noted the slice-070 m5 FIX doesn't add a test pinning constant↔docstring agreement. Builder draft response: "Add the constant↔docstring agreement test alongside the constant extraction; ~3-line test exercising `ast.parse` on the module + reading the docstring's enumeration". But design.md L69 + L198 still only say "reference in docstring" — the promised AST-walk test is NOT enumerated as a new test in §Components touched.
- **Issue**: FBCD-1 sub-mode (a) — promise vs landing.
- **Proposed fix**: add the explicit test specification to design.md as a new function in §Components touched → `tests/bugs/test_psq_1_blast_radius_dict_leak.py` OR add an explicit "TODO: add drift-prevention test at Phase B2 per /critique m4 ACCEPTED-PENDING" anchor in slice-070 m5 FIX spec.
- **Severity rationale**: Minor — discharge by inscribing the promise into design.md.
- **Builder draft**: pending

### m-add-2 (Minor): Count drift across mission-brief and design.md on "30/31 findings" + "6/8-9/11 regression-pin tests" + obsolete "ACKNOWLEDGED" vocab token

- **Claim under review**: Three sweep gaps:
  1. **Finding count**: mission-brief.md L4 says "31-finding" (post-M4 fix); L38 says "**Every one of the ~30 findings**"; L49 says "Wide refactors beyond the enumerated 30 findings"; design.md L11/L142/L272 say 31. Mission-brief carries TWO sites (L38 + L49) where the count was NOT swept when L4 was updated.
  2. **Test count**: design.md L10 says "6 new regression-pin tests"; L242 says "11 regression-pin tests"; mission-brief L4 says "11 regression-pin-test cycles". Three different counts inside the same slice. Meta-Critic hand-count of NEW test FUNCTIONS in §Components touched = 8 (+1 if m4 ACCEPTED-PENDING is honored = 9). Not 6, not 11.
  3. **Stale disposition vocabulary**: design.md L11 still enumerates `"FIX / DEFER-AGAIN / ACKNOWLEDGED / ALREADY-FIXED"` as the disposition vocabulary. Builder's M2 fix removed `ACKNOWLEDGED-NO-FIX` as a final disposition, but L11's vocab list still carries the obsolete `"ACKNOWLEDGED"` token — sibling-cell sweep gap.
- **Issue**: FBCD-1 sub-mode (a) — Builder's fix landed at the primary anchor but did not sweep sibling cells. Three axes; all are correct-the-record items rather than build-blocking (count drift on findings is absorbed by `~` for the 30/31 axis).
- **Framework**: TPHD-1 sub-mode (a) — cross-doc harmonization gap; N=5 cumulative on this pattern.
- **Proposed fix**:
  - Mission-brief L38 "~30 findings" → "~31 findings"
  - Mission-brief L49 "30 findings" → "31 findings"
  - Design.md L10 "6 new regression-pin tests" → "8 new regression-pin tests (9 with m-add-1 / m4 promise discharged)"
  - Design.md L11 vocab: replace `"ACKNOWLEDGED"` with `"DOCUMENT-AS-DESIGNED"`
  - Design.md L242 "11 regression-pin tests" → "8 new regression-pin tests + 5 modifications of existing tests"
  - Mission-brief L4 "11 regression-pin-test cycles" → "8-9 regression-pin-test additions + 5 modifications of existing tests"
- **Severity rationale**: Minor — three correct-the-record items; none block /build-slice (verification commands are unaffected; only the prose narrative drifts).
- **Builder draft**: pending

## Severity adjustments

**None.** All twelve first-Critic findings are correctly filed at Blocker/Major/Minor.

## Notes

- **Meta-Critic confidence**: high on B1 (empirically reproduced via Python execution), high on B2/M1/M2/M3 (clean structural verification against post-fix design.md), **high on M-add-1 (empirically reproduced docstring↔assertion mismatch via Python)**. Medium on M-add-2 (Phase B1+B2/B3 ordering reading depends on whether "Phase B1" is read as a single per-finding bundle of test+source landing together; Builder's prose L250 says "structural-test additions AND source-side FIXes paired per-finding" which could be read either way, but L251's "After this batch [B2], the Phase B1 tests for slice-070 should GREEN" decisively settles that tests precede their slice-070 source-side FIXes).
- **Calibration observation**: the first Critic's coverage of slice-071 is unusually strong for a 31-finding cleanup — both Blockers (B1 empirical regex, B2 cross-file consistency), six Majors covering RSAD-1 / FBCD-1 / APED-1 / Wiegers requirements-honesty, four Minors on count drift and unverified claims. Pattern-blindness check: no obvious dimension missed; APED-1 (Critic empirically ran the regex) + FBCD-1 (cross-file count harmonization) were both fired correctly. Where the first Critic stopped is at the fix-block-introduced-regression boundary — Critic produced the fix proposals and trusted Builder to apply them cleanly; Builder applied 10/12 but introduced M-add-1 (M6 docstring mismatch) + M-add-2 (M5 Phase ordering residual) + m-add-1 (m4 promise-not-landed) + m-add-2 (count sweep gap). **This is the N=5 cumulative Builder-fix-block-introduced-regression pattern** (slice-022/067/068/070/071) the meta-Critic specializes in catching. The slice-070 reflection's "Builder fix-block prose-honesty discipline" lesson is the direct lineage anchor.
- **Reservation**: M-add-1 may be argued as "build-time auto-detect / pytest will catch on first run" rather than design-time defect — but Critic M6 explicitly flagged the structural fragility class and asked Builder to verify empirically before commit (APED-1 obligation); landing the fix-block with two-of-four broken assertions IS the M6 defect class being re-instantiated inside its own closure.
