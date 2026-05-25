---
id: ADR-038
title: The function-level extension is a NEW minted -D rule-ID PTFFD-1 refining PTFCD-1 in place, not PTFCD-1 v1.1
date: 2026-05-17
slice: slice-037-extend-ptfcd-1-to-test-function-level
reversibility: cheap
status: accepted
---

# ADR-038: PTFFD-1 — new `-D` rule-ID refining PTFCD-1 in place (not a `vN.N` label)

## Context

Slice-037 extends phantom-test-citation detection from FILE level (PTFCD-1,
slice-025) to test-FUNCTION level. The methodology-changelog entry needs a
rule-ID. The slice's first draft labelled it `PTFCD-1 v1.1`, citing the
`vN.N`-for-same-rule-refinement precedents CCC-1 v1.1 / PMI-1 v1.1 / BC-1 v1.2 /
UTF8-STDOUT-1 v1.1. `/critique` B3 flagged this as a vault-convention
contradiction. The decision must be pinned here at `/design-slice` against the
enforcing convention (per `_index.md:48`: behavior-change RULE-ID obligation is
pre-decided, never auto-blessed, never adjudicated late at `/reflect`).

## Options considered

1. **`PTFCD-1 v1.1`** (version-suffix, same rule-ID).
   - Pro: signals "same discipline, refined".
   - Con: every cited `vN.N` precedent (CCC-1, PMI-1, BC-1, UTF8-STDOUT-1) is a
     **NON-`-D` audit-enforced-gate-class** rule. `methodology-changelog.md:161,183`
     explicitly partitions the namespace: the `vN.N` / bare-ID class is
     BC-1/CAD-1/PMI-1/INST-1/WIRE-1/BRANCH-1/UTF8-STDOUT-1/CRP-1/PCA-1; the
     `-D` suffix is "reserved for /critique-time prose-heuristic disciplines"
     (RSAD-1/EPGD-1/SCPD-1/RPCD-1/TPHD-1/LAYER-EVID-1/FBCD-1/PTFCD-1). PTFCD-1
     is a `-D` rule (ADR-023; `methodology-changelog.md:219,239`). **No `-D`
     rule has ever taken a `vN.N` refinement label** — zero precedent.
   - Con: the single most directly analogous case — **TFFL-1 (slice-034,
     v0.48.0)**, an in-place function-granularity refinement of the *same*
     `tools/test_first_audit.py` surface — explicitly **minted a new rule-ID
     refining TF-1 in place, lineage preserved, supersedes nothing**
     (`methodology-changelog.md:51`). The closest precedent decided the
     opposite way.
2. **New minted `-D` rule-ID `PTFFD-1` ("Phantom-Test-Function-citation
   Discipline") refining PTFCD-1 in place, supersedes nothing.**
   - Pro: conforms to the `-D` naming class (ADR-019 / ADR-023); follows the
     TFFL-1↔TF-1 / EOL-DRIFT-1↔CAD-1 in-place-mint precedent exactly; keeps the
     PTFCD-1 lineage intact (FILE-level rule unchanged, FUNCTION-level is its
     sibling); entry-pin uses the established `<rule>_<numeral>` underscore form
     (`ptffd_1`).
   - Con: a new ID is marginally more verbose than a version bump — immaterial
     against convention conformance.
3. **Supersede PTFCD-1 with PTFFD-1.** Rejected: FILE-level PTFCD-1 remains
   fully in force and is untouched; superseding would falsely imply it is
   obsolete and would violate the append-only / lineage-preservation pattern
   the TFFL-1 precedent established.

## Decision

Adopt **Option 2**. The function-level extension is **PTFFD-1**
("Phantom-Test-Function-citation Discipline") — a NEW minted `-D`-suffix
rule-ID that **refines PTFCD-1 in place; rule-ID lineage preserved; supersedes
nothing**. The methodology-changelog v0.50.0 entry carries `Rule reference:
PTFFD-1`; the entry-pin test is
`test_v_0_50_0_ptffd_1_entry_present_in_repo_and_installed`; the SCPD-1
catalog-propagation pin is `test_v_0_50_0_ptffd_1_shippability_consumer_propagation`.
The `-D`-suffix calibration-trail count advances (…/FBCD-1/PTFCD-1 → +PTFFD-1).

## Consequences

- mission-brief AC5, design.md, the changelog entry, the entry-pin test name,
  and the shippability row are aligned to `PTFFD-1` atomically in the same fix
  block (B3 + M1 + TPHD-1 harmonization).
- PTFCD-1 (ADR-023) is unmodified and remains the FILE-level rule; PTFFD-1 is
  its function-level sibling. `agents/critique.md` Dim 9 keeps the single
  "Phantom test-file citation discipline" sub-clause, refined N=2→N=3 with a
  function-level layer naming PTFFD-1 — one sub-clause, two rule-IDs (the
  gates), consistent with how PTFCD-1 already spans two sub-modes.

## Reversibility

**cheap** — the rule-ID is a string in the changelog entry, the entry-pin test
name, the shippability row, and the slice spec docs. No code keys on it; no
external consumer. Renaming is a localized multi-file string change with the
PMI-1/INST-1 audits as the consistency backstop. Cost ≈ 1 hour.
