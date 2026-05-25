# Critique Review: Slice 068 add-vault-root-constant

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-25
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's pass was substantively strong — B1 (9th-site discovery `tools/build_checks_integrity.py:78`), M1 (consumer-freeze cascade), M2 (false conftest L37 citation), M3 (R-15 backstop atrophy via the scope-back), m1, and m2 are all VALID with correct severities. The Builder fix-block held empirically (re-running the cited grep `Path\(["']architecture|["']architecture/|^_[A-Z_]*REL\s*=` against `tools/*.py` produces exactly the 8-site allowlist named in the post-fix surfaces). However, the Builder fix-block introduced **one cross-document asymmetry** (M-add-1) — design.md TF-1 row 4 line 159 defines a TWO-marker convention while mission-brief AC2 + must-not-defer #2 + Verification-plan row 2 only enumerated the ONE-marker convention. This is exactly the slice-067 N=3 cumulative meta-Critic lesson class — *Builder applies fix without sweeping all sibling-cell sites*. **Strengthens N=3 toward N=4 cumulative.** One additional severity adjustment on m2's prescribed SC-NNN scoring (low/small → medium/medium per Hendrickson multi-consumer-artifact rule).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (9th site `tools/build_checks_integrity.py:78` missing) — CONFIRMED; severity **Blocker** appropriate. Empirically re-verified: `Grep` for `Path\(["']architecture|["']architecture/|^_[A-Z_]*REL\s*=` against `tools/*.py` produces exactly the 8 sites in the post-fix allowlist. Builder swept correctly: mission-brief AC4 + must-not-defer #8 + Dependencies vault-refs + design.md §Components-touched + ADR-065 §Context all name the same 8 modules.
- **M1** (consumer-freeze cascade hazard) — CONFIRMED; severity **Major** appropriate. Per Fowler (*Refactoring*, "Encapsulate Variable"), capturing a module-level value at consumer-import time and exposing it via reassignment is a known footgun. Builder's option (b) — keep option 2 + document freeze contract + add `test_consumer_constants_are_frozen_at_first_import` pin — is the right resolution; design.md §Consumer-freeze-cascade and ADR-065 §Decision both elevate the freeze to a first-class production contract.
- **M2** (false "conftest L37 precedent" citation) — CONFIRMED; severity **Major** appropriate per McGraw's *Software Security* "Beware of unverified citations" principle. Builder dissolved this entirely via the M3 scope-back; ADR-065 §Consequences now correctly states "No test-tree-to-tools-tree import dependency introduced by this slice".
- **M3** (prose-vs-path under-scoping + R-15 backstop atrophy) — CONFIRMED; severity **Major** appropriate per Sommerville (test-suite invariants under refactor). Scope-back to `tools/*.py`-only is the cleanest fix; R-15 audit regex at `tests/methodology/test_resolve_slice_dir.py:233` UNCHANGED preserves the backstop.
- **m1** (argparse default-eval freeze) — CONFIRMED; severity **Minor** appropriate; correctly subsumed by M1.
- **m2** (BCR-1 SC-NNN round-trip for discovered slice-067 PSQ-1 raw-dict-leak) — CONFIRMED **the existence** of the concern; severity-on-the-finding (Minor — file-an-SC, not block-a-slice) is correct. **Severity-on-the-prescribed-SC-scoring** is the over-confident under-severity flagged below in §Severity adjustments.

## Suspicious findings

**None.** Every first-Critic finding has empirical grounding in design.md, ADR-065, or `tools/*.py` source. No over-reach detected.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

### M-add-1: Two-marker convention asymmetry between mission-brief AC2/must-not-defer #2/Verification-plan row 2 and design.md TF-1 row 4

- **Issue**: design.md line 159 (TF-1 row 4 `test_no_orphan_architecture_literal_in_migrated_tools`) introduces a TWO-marker convention — the test accepts either `# VAULT_ROOT-routed (slice-068)` (for 8 migration sites) OR `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` (for 5 enumerated error-message-string EXCLUDED sites: `cross_spec_parity_audit.py:335`, `state_transition_pin_audit.py:374,388,400`, `validate_slice_layers.py:521`). Mission-brief AC2 (line 17) + must-not-defer #2 (line 52) + Verification-plan row 2 (line 45) only enumerated the ONE-marker convention. Per Wiegers (*Software Requirements*): "every acceptance criterion must be testable AND mirror the design's verification shape" — the spec mismatch will cause confusion at `/build-slice`: a Builder reading mission-brief AC2 strictly will not add the `# NOT VAULT_ROOT-routed` marker on the 5 error-message-string sites, and then `test_no_orphan_architecture_literal_in_migrated_tools` will flag those 5 sites as orphan literals — failing the test.
- **Class**: This is exactly the slice-067 N=3 cumulative meta-Critic lesson — *Builder-fix-block-introduced regression where Builder applied fixes without sweeping all sibling-cell sites*. The error-message-string EXCLUDED class was added by the M3 scope-back, but only design.md was updated; mission-brief AC2 + must-not-defer #2 + Verification-plan row 2 weren't swept. **Strengthens the N=3 cumulative observation toward N=4** — candidate `/critic-calibrate` pattern signal: *"first-Critic fix dispositions should explicitly enumerate the cross-document sweep surface, not leave it implicit."*
- **Severity**: **Major**.
- **Proposed fix**: sweep mission-brief AC2 + must-not-defer #2 + Verification-plan row 2 to enumerate the two-marker convention.
- **Builder draft**: **ACCEPTED-FIXED** — All three sibling-cell sites swept:
  - mission-brief AC2 (line 17) rewritten to include the two-marker convention with the 5 EXCLUDED-site enumeration inline + cross-reference to design.md TF-1 row 4
  - mission-brief must-not-defer #2 (line 52) rewritten to name both markers + the 5 EXCLUDED sites + the audit test accepting both marker forms
  - mission-brief Verification-plan row 2 (line 45) rewritten to enumerate the two-marker convention + name the `shippability_decoupling_audit.py:91-92` AST-pattern allowlist + cite the DEFERRED tests/ migration per /critique M3
  - Verification-plan row 4 also updated for the test count (9 → 10 per /critique M1 freeze-pin row addition) and Verification-plan row 3 also updated for the pytest baseline (899 → 909) — these were sibling-cell sweep targets the original Builder fix-block missed; flagging the residual sweep here for completeness
  - Closed. Re-verification: `grep -n "two-marker\|NOT VAULT_ROOT-routed" mission-brief.md` now finds matches in AC2 + must-not-defer #2 + Verification-plan row 2 (3 sweep targets); pre-fix grep returned 0 matches. The audit `test_no_orphan_architecture_literal_in_migrated_tools` per design.md TF-1 row 4 will now find both marker conventions consistently across all spec surfaces.

## Severity adjustments

### m2 SC-NNN prescribed scoring: low/small → medium/medium

- **Claim under review**: critique.md m2 Builder disposition (rev-1) prescribed `**Severity:** low`; `**Blast:** small` for the slice-067 PSQ-1 raw-dict-leak SC-NNN entry to be added to `diagnose-out/backlog.md` at /reflect time.
- **Issue**: The leak (verified at `architecture/slice-queue.md:18,34,42`) injects a raw Python dict-string with embedded prose (`'label': 'Parallel-slice queue writer (PSQ-1)...'`) into the `Blast-radius:` column of a multi-session-visible artifact. The dict-string contains literal characters `{`, `'`, `:` that are NOT valid file-path characters but ARE valid characters in Markdown. Downstream consumers of the queue file (other Claude sessions running `/slice` with PSQ-1 cross-machine coordination semantics — the slice-070 candidate) may parse the leaked dict-string as a hint-file path, attempt to read `{'id': 'slice_queue_writer_rationale_1'...}` as a file, fail with FileNotFoundError, and abort the candidate's blast-radius enrichment.
- **Rule**: Per Hendrickson (*Exploratory Testing*) — *"a defect that produces unparseable output in a multi-consumer artifact is at least Medium, not Low, because the blast-radius is N consumers, not 1."* The PSQ-1 architectural premise is multi-session shared visibility (per ADR-064); a parsing defect against shared multi-session state is by definition Medium-severity and Medium-blast.
- **Recommended scoring**: `**Severity:** medium` (was `low`); `**Blast:** medium` (was `small`); `**Reversibility:** cheap` (unchanged); `**Effort:** small` (unchanged — likely a single-line `str(node.get('path', node))` call-boundary fix).
- **Builder draft**: **ACCEPTED-FIXED** — critique.md m2 disposition updated inline: `**Severity:** low` → `**Severity:** medium`; `**Blast:** small` → `**Blast:** medium`; rationale citing the multi-consumer-artifact rule inserted; the disposition's "Will action at /reflect" sentence preserved. At /reflect time the SC-NNN entry will be written to backlog.md with the medium/medium scoring.

## Notes

Confidence is high. The first Critic's empirical work (re-grepping migration sites, reading `tests/methodology/conftest.py` end-to-end to disprove the L37 precedent, web-searching the read-at-import-time anti-pattern) is exactly the substantive shape the slice-067 N=3 cumulative meta-Critic lesson identified as first-Critic strength — *"first-Critic catches conceptual + cross-doc citation hygiene"*. The Builder fix-block held on all dimensions EXCEPT the M-add-1 two-marker convention asymmetry — which is exactly the slice-067 N=3 cumulative meta-Critic lesson at work: *"meta-Critic catches Builder fix-block-edit-introduced regressions where Builder applied fixes without sweeping all sibling-cell sites."* **N=3 → N=4 cumulative.** Consider a `/critic-calibrate` pattern signal: *"first-Critic fix dispositions should explicitly enumerate the cross-document sweep surface, not leave it implicit; meta-Critic's first responsibility on a multi-finding fix-block is to verify the sweep is exhaustive across all spec surfaces (mission-brief AC + must-not-defer + Verification-plan + design.md + ADRs)."*

One reservation: the m2 severity adjustment is judgement-bounded — slice-070's claim semantics aren't fully specified, so "downstream consumers may mis-parse" is forward-looking concern not present-day failure. Builder may legitimately disagree at TRI-1 and keep the `low/small` scoring; that's a reasonable resolution the user can ratify either way.

The N=4 cumulative pattern also raises the question of whether the `_no_orphan_architecture_literal_in_migrated_tools` test ITSELF needs a corresponding allowlist-pin for the 5 error-message-string EXCLUDED sites — currently the design.md TF-1 row 4 prose says the test accepts EITHER marker; concretely the test needs to ENUMERATE the 5 EXCLUDED sites as a frozenset (`_ERROR_MESSAGE_STRING_EXCLUSIONS`) so a future code-change that adds a 6th EXCLUDED site without updating the allowlist fails the audit. This is a candidate `m-add-2` finding the meta-Critic notes but does NOT escalate — the design.md prose at TF-1 row 4 implicitly assumes the test will pin the 5-element exclusion set; if the implementation at /build-slice does so, no separate finding is needed. Surfacing as a /build-slice attention item.

Reviewer-signature (Heavy mode v2 placeholder): N/A (Standard mode; v1 audit doesn't require signature).
