# Critique Review: Slice 018 cleanup-slice-016-rpcd-1-sibling-test-scoping-flaw

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-13
**First-Critic verdict**: CLEAN
**Dual-review verdict**: EXTEND

## Summary

The first Critic's coverage of the original draft was strong — B1/B2 caught the AC-vs-TF-1-plan/Decision contradiction (the exact recursive-self-application class the slice retires); M1/M2/M3/M4 plus the three minors form a coherent NEEDS-FIXES set with sound proposed fixes. All 9 dispositions are VALID with correct severities. However, the M2 fix (introducing `_extract_v031_body` helper) introduces a small diagnostic-quality regression vs slice-017's canonical pattern that the first Critic did not flag, and the design.md silently breaks symmetry with slice-017 (which inlines boundary slicing) without explicit foreshadowing-decline — a Fowler/YAGNI design-symmetry concern. One additional empirical-gap on the installed methodology-changelog.md surface deserves a Minor.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- B1: TPHD-1 self-application failure (design "preserve name" vs TF-1 plan "scopes_to_v031_body") — confirmed; severity Blocker is appropriate. Direct recursive-self-application violation per RSAD-1 design-time-mode at `methodology-changelog.md:80-82` (RPCD-1 entry body) and `agents/critique.md` Dim 9 sub-clause 6 (lines 168-172 of in-repo agents/critique.md). The slice retiring `test-scoping-flaw-inherited-across-codification-slice-siblings` cannot ship with a TF-1-plan-vs-design-decision drift on its own draft. Path A fix is the right choice (minimizes blast radius; preserves row 16 shippability discipline). The fix is correctly propagated across all 4 surfaces per post-fix `mission-brief.md:34/41` + `design.md:96` + verification plan row 1.
- B2: AC #1 internal contradiction — confirmed; severity Blocker is appropriate. Mutually exclusive deliverables would have shipped if unresolved; status-only TF-1 audit would not catch (`tools/test_first_audit.py` `_ALLOWED_STATUSES` checks status field, not name-consistency across surfaces). Resolves cleanly as consequence of B1 Path A.
- M1: TF-1 row 3 docstring-meta-test over-engineering — confirmed; severity Major is appropriate. Fowler speculative-generality + Beck YAGNI both apply; docstring on a test function is not a methodology-pin surface (unlike `agents/critique.md` Dim 9 sub-clause titles which ARE pinned). Grep-at-/validate-slice is the right verification.
- M2: regression test partially tautological — confirmed; severity Major is appropriate per Hendrickson regression-guard discipline. `_extract_v031_body` helper extraction is a sound fix: single code path under test means regression-test-passes ↔ sibling-test-fails-on-stripped-fixture link is established by execution, not code-reading. See "Missed findings" below for one diagnostic-quality regression this fix introduces.
- M3: Audit 1 inline-prose collision edge case — confirmed; severity Major is appropriate. Defer-to-watch-list option (b) is the right choice given (1) today's file has no collision (`## v0.31.0` and `## v0.30.0` are unique heading-only occurrences per Grep of `methodology-changelog.md`), (2) tightening would break symmetry with slice-017 TPHD-1 sibling canonical at L1086, (3) cleanup-slice scope.
- M4: SCPD-1 row 16 enumeration empirical gap — confirmed; severity Major is appropriate per CCC-1 v1.1 mechanical-table-vs-canonical-inventory discipline. Audit 4 in post-fix design.md captures the empirical row 16 enumeration. Verified independently: `shippability.md:24` contains `test_v_0_31_0_rpcd_1_entry_names_three_sub_modes_in_repo_and_installed` exactly once.
- m1: fallback-branch symmetry choice — confirmed; severity Minor is appropriate. Keep-fallback-for-symmetry with slice-017 L1091-1094 is the right call.
- m2: conditional-hedge resolution at design.md L13-14 — confirmed; severity Minor is appropriate. Resolution is clean.
- m3: BC-1 empirical verification gap — confirmed; severity Minor is appropriate per Wiegers evidence-traces-to-claim discipline. Audit 5 in post-fix design.md records the literal output `"No build-checks rules apply to this slice."`

## Suspicious findings

No suspicious findings. All 9 first-Critic findings stand on closer reading; none are over-reach.

## Missed findings

Concerns the first Critic did not surface from independent re-review of the POST-fix design state:

- **m-add-1: `_extract_v031_body` helper moves the `surface_name`-aware assert from call-site to helper interior — diagnostic-quality regression vs slice-017 canonical pattern.**

  Per Hendrickson regression-guard discipline + slice-017 canonical pattern at `tests/methodology/test_methodology_changelog.py:1088-1090`, the v0.32.0 TPHD-1 sibling keeps `assert v032_start != -1` at the CALL site INSIDE the `for surface_name, content in [...]` loop, with the error message interpolating `surface_name`: `f"{surface_name} methodology-changelog.md missing v0.32.0 entry"`. This means when the assertion fires, the failure message tells you WHICH surface (in-repo vs installed) is broken. The post-fix design.md helper at L132-135 moves the assert INSIDE `_extract_v031_body`: `assert v031_start != -1, "content missing \`## v0.31.0\` heading — entry-pin broken"`. The helper has no access to `surface_name` — so an assertion failure on the installed file (but not in-repo, or vice versa) produces a context-free error message. This is a diagnostic-quality regression: the test will still correctly fail on real defects, but the operator debugging the failure must inspect the loop iteration to determine which surface failed.

  Framework: Hendrickson "make failures self-explaining"; design-symmetry-with-canonical-pattern per slice-017 L1086-1094.

  Proposed fix: either (a) move the assert back to the call site after `_extract_v031_body(content)` returns (helper assumes pre-validated input; sibling test's loop adds the surface-context assert) — preserves slice-017 symmetry; OR (b) thread `surface_name: str | None = None` through helper signature so error message can interpolate when available — adds API complexity. Option (a) preserves the slice-017 canonical pattern with minimal churn.

  Severity: Minor (test correctness is preserved; diagnostic quality is the gap; impact is felt only at test-failure-debug time which is rare). Recommend Builder address via option (a) at /build-slice as a no-cost adjustment.

- **m-add-2: helper extraction asymmetry vs slice-017 — `_extract_v031_body` introduced for v0.31.0 only; v0.32.0 sibling at L1086-1094 keeps boundary-slicing inline. Design.md does not foreshadow generic `_extract_version_body` helper nor explicitly decline it.**

  Per Fowler "rule of three" + CCC-1 v1.1 sub-clause 2 (mechanical-table-vs-canonical-inventory): once a slice introduces a helper that has natural parametric generalization (`_extract_v031_body` → `_extract_version_body(content, start_marker, end_marker)`), the design.md should either (a) generalize at introduction or (b) explicitly decline with rationale. Design.md introduces `_extract_v031_body` as v0.31.0-specific (post-fix L116-140) without addressing the asymmetry with slice-017's inline boundary-slicing at L1086-1094. The "canonical pattern symmetry with slice-017" Audit 3 claim at design.md L286-297 says "Pattern reproduces verbatim" — but post-fix the v0.31.0 sibling NO LONGER reproduces verbatim; it calls a helper, while v0.32.0 inlines. The verbatim-reproduction claim is now stale at the post-fix state.

  Framework: Fowler rule-of-three + CCC-1 v1.1 design-doc-mechanical-table parity.

  Proposed fix: design.md should add an "Audit 7: helper-extraction asymmetry foreshadowing-decline" note. The decline rationale is sound (N=1 only; YAGNI; future slice can extract `_extract_version_body` if N≥2 emerges). But the decline must be EXPLICIT in design.md, not implicit. Also update Audit 3 claim to acknowledge post-fix the symmetry is now at the boundary-slicing-pattern level (find anchors + assert + fallback), NOT the literal-code level (since v0.31.0 wraps in helper but v0.32.0 doesn't).

  Severity: Minor (design-doc accuracy concern; not a code-defect; doesn't block ship). Worth addressing at /build-slice for design.md fidelity.

- **m-add-3: design.md L371 "Pre-smoke verification: Confirm `## v0.30.0` exists in `methodology-changelog.md` (both in-repo + installed)" — Audit 6 (L334-336) only empirically verifies in-repo, not installed.**

  Per Wiegers "every claim traces to evidence", the post-fix design.md commits to checking BOTH in-repo + installed for `## v0.30.0`. Audit 6 at L334-336 confirms `## v0.31.0` and `## v0.30.0` are unique heading-only occurrences in (presumably) `methodology-changelog.md`, but doesn't disambiguate in-repo vs installed. The CAD-1 byte-equality discipline at slice-007 covers `agents/critique.md`, NOT `methodology-changelog.md`. Existing entry-pin tests at `tests/methodology/test_methodology_changelog.py:910-907` (RPCD-1 sub-clause present) DO pin the v0.31.0 entry bidirectionally — so by transitivity if `## v0.31.0` is present in installed, `## v0.30.0` likely is too (no test pins v0.30.0 explicitly though — slice-015 SCPD-1 entry-pin test at L747 covers v0.30.0 entry presence indirectly).

  Framework: Wiegers + SCPD-1 sub-mode (b) consumer-reference-propagation.

  Proposed fix: design.md Audit 6 should add a one-line empirical verification of installed `## v0.30.0` presence (`Path.home() / ".claude" / "methodology-changelog.md"` Grep). Trivial Builder step at /design-slice or /build-slice Phase 2; closes a Wiegers evidence-trace gap.

  Severity: Minor (entry-pin tests would catch installed drift; this is documentation hygiene, not a real correctness risk).

## Severity adjustments

No severity adjustments. All 9 first-Critic findings are correctly graded (B1+B2 = Blockers because mutually-exclusive deliverables would have shipped; M1-M4 = Majors per Fowler/Hendrickson/CCC-1 frameworks; m1-m3 = Minors per design-choice + evidence-trace hygiene).

## Notes

Confidence: high on the three missed findings, all Minor. The first Critic's coverage of the original draft was strong (caught the exact RSAD-1 design-time-mode violation class the slice retires) and the 9-finding density is appropriate for a small cleanup slice. The post-fix state introduces two helper-extraction-related asymmetries (diagnostic-message context loss + slice-017 symmetry breakage) that emerge ONLY in the post-fix state, so the first Critic cannot be faulted for missing them at original-draft review time — but the meta-Critic SHOULD catch them at post-fix review. Calibration observation: the M2 helper-extraction fix is correct in principle (single code path under test) but introduces a secondary design-symmetry cost that wasn't part of the first Critic's M2 cost-benefit analysis. This pattern — "first Critic proposes architectural change to address Major; meta-Critic catches secondary symmetry cost" — is the same class as slice-013/015/016 M-add-1 (sibling-coverage symmetry tightening). N=1 at slice-018; watch-list candidate for future calibration if recurs at N=2+. The slice should proceed to /build-slice with these three Minors addressed inline at Builder's discretion; none block ship.
