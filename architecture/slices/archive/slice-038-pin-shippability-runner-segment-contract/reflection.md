# Reflection: Slice 038 pin-shippability-runner-segment-contract

**Date**: 2026-05-17
**Shipped**: YES

## Validated
- The runner REUSES SCMD-1 `_segments()` (not re-derives) — validated by an object-identity test (`runner._segments is scmd1._segments` → `REUSE-VERIFIED`) AND the load-bearing naive-strip-vs-`_segments()` contrast on the REAL row #28.
- Pinning the contract behind an INVOKED tool (not prose) closes R-8 — validated by the SRSC-1 dogfood: the new runner ran the full real 38-row catalog at this slice's own /validate-slice Step 5.5, 38/38 PASS, row #28 (the lone multi-segment R-8 target) PASS, no WinError 2.
- Prose-only would have been insufficient (the design's core thesis) — confirmed: R-8 recurred N=2 *despite* the pre-existing SKILL.md L213 "deterministically `;`-split" prose; only the invoked single-sourced runner binds the contract.
- SRSC-1 ≠ SCMD-1 refinement (new non-`-D` `vN.N` rule, supersedes nothing) — validated by meta-Critic candidate (e): grammar-validation vs execution are distinct surfaces/consumers; TFFL-1↔TF-1 in-place precedent correctly rejected as the wrong analogy.

## Corrected
- design.md §What's new said the runner joins `_POSITIONAL_SLICE_TOOLS` (B1's applied-fix mechanism). Reality: that list passes a slice-folder arg a catalog-path tool can't consume; shipped via the sibling-precedent bespoke cp1252 test instead (covered_set mechanism (ii)). Updated in [[design.md]] §What's new + §Recursion; recorded in [[build-log.md]] DEVIATION event. B1's *intent* (runner ∈ covered_set; row #28 green at dogfood) held — only the mechanism corrected.
- AC5 TF-1 row (`test_risk_register_audit.py::test_repro_r8_retired_with_slice_and_adr`) was dropped at plan-mode (user-ratified): R-8 is a runner-contract risk, not an audit-behavior bug like R-9 — such a test = environment-fragile vault bookkeeping. AC5 remapped to the AC2 catalogued runner-contract test. Updated in [[mission-brief.md]] TF-1 plan (+ HTML-comment rationale).

## Discovered
- A Critic prescription of the form "add the new tool to `<specific parametrized test list>`" is a *claim about that list's argv contract*. Both the first-Critic and the DR-1 meta-Critic blessed `_POSITIONAL_SLICE_TOOLS`; the meta-Critic explicitly "verified" it as the "correct bucket" by reasoning about `_positional_slice_argv`'s shape — without checking the sibling precedent or running the argv. Impact: for any slice adding a `main()`-bearing tool, the UTF8-STDOUT-1 covered_set mechanism (parametrized list vs bespoke test) must be chosen by reading the sibling tools' actual membership, not the Critic's bucket conclusion. Not a new risk-register entry (it's an instance of the standing slice-032 "Critic reasons about the claim, not the artifact" law, N+1; the build-time artifact-read backstop worked exactly as the standing lesson predicts — no new Critic dimension warranted per slice-037).

## Deferred
- None. The slice fully retired R-8; no scope cut beyond the user-ratified AC5 TF-1-row correction (which was a strengthening, not a deferral — the guarantee moved to a stronger test).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality during build/validate:

- **B1** (new `main()` breaks UTF8-STDOUT-1 parity = row #28 dogfood): **VALIDATED** — disposition ACCEPTED-FIXED; verified real (runner's `main()` does enter `discovered_set`; without propagation row #28 false-FAILs). First Critic caught it where the Builder's *original* recursion note had explicitly dismissed it — high-value catch on this slice family's standing blind spot. *Caveat*: the prescribed fix mechanism (`_POSITIONAL_SLICE_TOOLS`) was wrong (see Missed-by-Critic); the *finding* was right, the *prescription* was not.
- **B2** (TF-1 plan omits SCPD-1 paired changelog test): **VALIDATED** (severity reclassified Blocker→Major by DR-1) — disposition ACCEPTED-FIXED; the SCPD-1 propagation obligation is real (PTFFD-1 precedent + SRSC-1 has a shippability consumer). First Critic's evidence was over-generalized ("every prior RULE-ID slice has the pair" — actually only PTFFD-1/slice-037, N=1); Builder caught the evidence error, meta-Critic correctly recalibrated severity. Calibration signal: first-Critic severity-inflation from a single-precedent inference rounded up to Blocker.
- **M1** (presence-pin vs content-pin): **VALIDATED** — ACCEPTED-FIXED; the `entry_present` test now asserts canonical anti-silent-weakening phrases (would catch silent gutting). Directly applied the slice-037 meta-Critic M-add-1 lesson.
- **M2** (PMI-1 3-part vs 4-part): **VALIDATED** — ACCEPTED-FIXED; verified all 3 version files were at 0.50.0; the 4-part bump (incl. `~/.claude/ai-sdlc-VERSION`) shipped. The slice-035 B-add-1 lesson held at N≥3+1.
- **m1** (dual non-identical enumeration surfaces): **VALIDATED** — ACCEPTED-FIXED; install_audit `_CANONICAL_TOOLS` (22→23) + plugin.yaml are genuinely separate surfaces; both updated.
- **m2** (negative fixture must be a contrast): **VALIDATED** — ACCEPTED-FIXED; the shipped `test_naive_outer_strip_runner_is_rejected` exercises both branches on real row #28 (load-bearing, not tautological).
- **m-add-1** (DR-1 missed-finding: "18 entries" stale, actual 22): **VALIDATED** — meta-Critic missed-finding; verified 22 entries. Doc-only, no behavioral path, but correctly the FBCD-1 count-drift class; design.md corrected + grep-verify-at-build note.

**Missed by Critic**: the B1 *applied-fix mechanism* (`_POSITIONAL_SLICE_TOOLS`) was wrong and was blessed by BOTH Critic layers — the meta-Critic explicitly listed "does adding to `_POSITIONAL_SLICE_TOOLS` change the invocation path" as a checked candidate and concluded "correct bucket (not `_ROOT_ONLY_TOOLS`)", which was incorrect (it reasoned about `_positional_slice_argv = [PY,-m,tool,FIXTURE_DIR]` being "exactly the runner's shape" without noticing FIXTURE_DIR is a slice *folder* and the runner needs a catalog *file*, and without checking that the two sibling shippability tools are deliberately NOT in that list). Caught only at /build-slice by reading the sibling tests' actual membership.

**Pattern**: dual-Critic stack hit **7/7 findings VALIDATED, 0 FALSE-ALARM** — precision remains strong on codification slices (N+ confirmations). The standing structural blind spot held again: when a Critic *prescribes a concrete mechanism* (here a parametrized-list membership), the prescription is a claim about an artifact's contract that the Critic — even when it says "verified" — reasons about rather than executes (slice-032 law, N+1; slice-034 counter-lesson "empirical execution reaches it" applies but neither Critic ran the argv). The build-time sibling-precedent read was the structural backstop, exactly as the slice-032/036 standing lessons predict — **no new Critic dimension warranted** (slice-037: don't add dimensions for structurally-backstopped blind spots). One new calibration note for `/critic-calibrate`: first-Critic rounds single-precedent inferences up to Blocker (B2); DR-1 correctly recalibrated — the DR-1 layer is doing its job on severity.

## Lessons for next slice
- **A Critic/meta-Critic prescription "add tool X to parametrized list L" is a claim about L's argv contract — verify L's invocation shape against X's actual CLI signature by reading L's existing members at build, never trust the Critic's "correct bucket" conclusion (even when the meta-Critic says "verified").** slice-038: both Critic layers blessed `_POSITIONAL_SLICE_TOOLS` (passes a slice-folder arg) for a catalog-file-path tool; the one-read backstop was "are the sibling shippability tools in that list?" (they are not — they use bespoke tests). N+1 of the slice-032 reason-about-the-claim law; the slice-034 "task the Critic to empirically execute" remedy would have caught it (run the proposed argv) — neither Critic did.
- **For a tool that shares a private helper across modules, assert object-identity reuse in a test (`consumer._fn is source._fn`) — it converts "reuses, not re-derives" from prose into a mechanically-enforced contract.** Worked cleanly here (AC1); cheap, high-signal, recommend for any future CSP-1 cross-`tools` reuse slice.
- **The "run the shipped tool on the full real artifact at the slice's own /validate-slice" dogfood is the decisive validation artifact for runner/executor-class slices** — same role BC-PROJ-4 plays for audit-parse slices. The SRSC-1 38/38 catalog run proved the fix on reality more conclusively than any unit fixture. Keep it the mid-slice + validate gate for this class.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-8 → `Status: retired` (slice-038 + [[ADR-039]] / SRSC-1 / methodology v0.51.0); open risks now R-2, R-6 only
- [[decisions/ADR-039-srsc-1-pinned-shippability-runner.md]] — created (accepted; cheap; supersedes null)
- This slice's [[design.md]] — corrected the B1 `_POSITIONAL_SLICE_TOOLS` mechanism to the shipped sibling-precedent bespoke-test mechanism (build-log.md notes the deviation)
- This slice's [[mission-brief.md]] — TF-1 plan AC5-row correction (+AC3 row; 8/8 PASSING)
- [[shippability.md]] — row #38 appended (the slice's catalogued critical-path test; Step 5.3 satisfied during build)
- `methodology-changelog.md` (+installed) — v0.51.0 SRSC-1 entry; 4-part PMI-1 bump
