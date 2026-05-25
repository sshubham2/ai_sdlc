---
id: ADR-040
title: Proposals 1+2 are NEW minted -D rule-IDs APED-1 (Dim 9) and MEPD-1 (Dim 7); the -D suffix denotes a behavioral class, not Dim-9 membership
date: 2026-05-18
slice: slice-039-apply-critic-calibrate-proposals-to-critique-agent
reversibility: cheap
status: accepted
---

# ADR-040: APED-1 + MEPD-1 — new `-D` rule-IDs; `-D` is a behavioral class, not a Dim-9 tag

## Context

Slice-039 applies the two user-ACCEPTED 2026-05-17 `/critic-calibrate`
proposals to `agents/critique.md`. Each codified Critic discipline needs a
rule-ID (per the `_index.md:48` pre-decided behavior-change RULE-ID obligation
— never auto-blessed, never adjudicated late at `/reflect`; pinned here at
`/design-slice`). Two sub-questions:

1. New minted IDs, or version labels on an existing rule?
2. Proposal 2 is a **Dim 7** checklist sub-bullet, not a Dim 9 cross-cutting
   sub-clause. Every existing `-D` rule (RSAD-1, EPGD-1, SCPD-1, RPCD-1,
   TPHD-1, LAYER-EVID-1, FBCD-1, PTFCD-1, PTFFD-1) lives in Dim 9. Does a
   non-Dim-9 prose-heuristic discipline take a `-D` ID or a non-`-D` ID?

## Options considered

1. **`CCC-1 v1.x` version labels** (treat both as refinements of the Dim 9
   cross-cutting rule). Rejected: the `vN.N` label is reserved for the
   NON-`-D` audit-enforced-gate class (BC-1 / CAD-1 / PMI-1 / INST-1 / WIRE-1 /
   BRANCH-1 / SRSC-1 …) per `methodology-changelog.md:161,183` + [[decisions/ADR-038]];
   no `-D` rule has ever taken a `vN.N` refinement label. Proposal 2 is not
   even in Dim 9, so a `CCC-1` version label is doubly wrong.
2. **New minted `-D` IDs, both: APED-1 (Dim 9 #12) + MEPD-1 (Dim 7).**
   - Pro: conforms to the `-D` naming class (ADR-019 / ADR-023 / ADR-038);
     follows the TFFL-1↔TF-1 / EOL-DRIFT-1↔CAD-1 / PTFFD-1↔PTFCD-1
     in-place-mint-new-ID precedent exactly; entry-pins use the established
     `<rule>_<numeral>` underscore form (`aped_1`, `mepd_1`).
   - Resolves sub-question 2 by pinning the class boundary explicitly (see
     Decision): the `-D` suffix denotes the *behavioral* class
     "**/critique-time prose-heuristic discipline**" — a discipline the Critic
     applies by reading the prompt and reasoning, with no audit gate enforcing
     it — as opposed to the non-`-D` audit-enforced-gate class. Dim-9
     membership was incidental to the first nine `-D` rules, never definitional.
   - Con: MEPD-1 is the first `-D` rule outside Dim 9 — a small convention
     extension. Acceptable: it is an *extension* (clarifying the existing
     boundary), not a *contradiction* (no prior ADR ever said `-D` ⊆ Dim 9).
3. **Mint APED-1 `-D` (Dim 9) but give Proposal 2 a non-`-D` ID** (e.g.
   `MEP-1`). Rejected: Proposal 2 is not an audit-enforced gate — it is a
   Critic checklist with no programmatic enforcer (its only enforcement is the
   Critic reading the prompt). Giving it a non-`-D` ID would mis-signal that
   an audit gate exists, the exact category error the `-D`/non-`-D` partition
   prevents.

## Decision

Adopt **Option 2**.

- **Proposal 1 → `APED-1`** ("Audit-Parse-rule Empirical-execution
  Discipline") — a NEW minted `-D`-suffix rule-ID; Dim 9 cross-cutting
  sub-clause **#12**; refines nothing, supersedes nothing.
- **Proposal 2 → `MEPD-1`** ("Methodology-surface Entry-Pin Discipline") — a
  NEW minted `-D`-suffix rule-ID; a **Dim 7** ("Drift from vault") checklist
  sub-bullet; refines nothing, supersedes nothing.
- **Class-boundary pin**: the `-D` suffix denotes the behavioral class
  *"/critique-time prose-heuristic discipline (no audit gate enforces it)"*.
  Dimensional home (Dim 7 vs Dim 9 vs elsewhere) is orthogonal to the suffix.
  MEPD-1 is the first deliberately non-Dim-9 `-D` rule and sets this
  precedent.
- The methodology-changelog `v0.52.0` entry carries `Rule reference: APED-1`
  and `Rule reference: MEPD-1`; entry-pins
  `test_v_0_52_0_aped_1_entry_present_in_repo_and_installed` +
  `test_v_0_52_0_mepd_1_entry_present_in_repo_and_installed`. The `-D`
  calibration trail advances N=9 → **N=11** (… / PTFCD-1 / PTFFD-1 / APED-1 /
  MEPD-1).

## Consequences

- `agents/critique.md`: APED-1 added as Dim 9 sub-clause #12 (the
  `_lists_eleven_sub_clauses` structural-invariant test is superseded →
  `_lists_twelve_sub_clauses`, triggering the SCPD-1 propagation across
  shippability rows 6/11/13/15/16/24/25). MEPD-1 added as a Dim 7 sub-bullet
  (Dim 7 has no structural-count invariant test → no supersession there).
- mission-brief AC1/AC2/AC4, design.md, both changelog `Rule reference`s, the
  entry-pin test names, and the new shippability row are aligned to APED-1 /
  MEPD-1 atomically in one fix block (FBCD-1 cross-file harmonization).
- Future calibration proposals homed in non-Dim-9 dimensions now have a clear
  precedent: still a `-D` rule if it is a prose-heuristic Critic discipline.

## Reversibility

**cheap** — the rule-IDs are strings in the changelog entry, entry-pin test
names, the shippability row, the Critic sub-clause/sub-bullet prose, and the
slice spec docs. No code keys on them; no external consumer. Renaming is a
localized multi-file string change with PMI-1 / INST-1 / the entry-pin tests
as the consistency backstop. Cost ≈ 1 hour.
