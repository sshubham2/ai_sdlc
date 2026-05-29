# Reflection: Slice 080 harden-bc1-critical-rules-exit-gate

**Date**: 2026-05-29
**Shipped**: YES

## Validated
- `--strict` makes unacknowledged applicable Critical rules into violations → exit 1 via the UNCHANGED `return 1 if result.violations else 0` — validated by the repro + self-dogfood (`--strict` no-ack → exit 1; `--ack-critical BC-PROJ-3 BC-GLOBAL-2` → exit 0).
- Default (no `--strict`) path is byte-identical — validated by 47/47 pre-existing BC-1 tests + `critical_applicable: 2` bare invocation still exit 0 (AC3).
- The acknowledgment-flag design (ADR-072 option 2) cleanly solves the "applicability never disappears once a rule applies" trap that would have made a blunt-count gate un-passable — validated: a Critical-touching slice CAN clear the gate by acknowledging, and DOES fail until it does.
- The strict-append placed after both source loops captures global-source Critical rules (BC-GLOBAL-2), not just project-source — validated by `test_strict_global_source_critical_captured` (M3).

## Corrected
- None at the design level. The design held; the only correction was the code-Critic's M1 (output mislabel + non-path `path` field in `_format_human`), fixed in-band before validation — the design.md `## Build plan` did not anticipate that the strict violations would render under the "parse violation(s)" header (a code-level emergent, not a design claim).

## Discovered
- **Standing-ack consequence**: BC-PROJ-3 + BC-GLOBAL-2 are `always:true` Critical (git-revert-discipline) rules, so wiring `--strict` into Step 6 means EVERY future slice must `--ack-critical BC-PROJ-3 BC-GLOBAL-2` after attesting in build-log.md. Anticipated at /critique B3; confirmed in practice. Impact: a mild recurring friction at every Step 6 — candidate future enhancement (auto-enumerate always-rules + single attestation), NOT a risk-register entry (cooperative, low-cost, working-as-designed).
- **code-Critic m2** (cosmetic): `_format_human` recomputes the applicable-Critical/acked/unacked sets the strict-append already computed. Deferred (the diagnostic needs `acknowledged`+`unmatched` too, not derivable from the violations list alone). Lands in a future bundled code-Critic cleanup slice (CRSI-1 voluntary-restraint precedent).

## Deferred
- `_format_human` set-recomputation dedup (code-Critic m2) — reason: cosmetic, full single-sourcing not clean; lands in: future bundled code-Critic cleanup slice.
- BC-1 v2 executable per-rule auto-verification (run each rule's `Validation hint` to prove the check actually ran, vs the current attestation) — reason: explicitly out of scope per ADR-072; lands in: a future BC-1-v2 slice.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality during build/validate:

- B1 (PMI-1 leg enumeration wrong/contradictory): **VALIDATED** — ACCEPTED-FIXED; the wrong leg count would have failed the renamed `test_version_files_synchronized_at_v_0_75_0` (pyproject leg) had it shipped uncorrected.
- B2 (version-sync supersession + shippability propagation unplanned): **VALIDATED** — ACCEPTED-PENDING; the shippability row #75 command DID cite the renamed test and WOULD have gone stale at /validate Step 5.5 without the propagation (confirmed: row #75 ran green only after the rename propagated).
- B3 (self-application ack — RSAD-1): **VALIDATED** — ACCEPTED-PENDING; the slice's own Step 6 strict run empirically exited 1 without `--ack-critical BC-PROJ-3 BC-GLOBAL-2` and 0 with it.
- M1 (shippability row #85 documented rejected blunt-count design): **VALIDATED** — ACCEPTED-FIXED.
- M2 (lenient-ack silent-no-op needs diagnostic): **VALIDATED** — ACCEPTED-PENDING; the typo'd-ack diagnostic now surfaces visibly.
- M3 (append after both loops + global-source test): **VALIDATED** — ACCEPTED-PENDING; global-source test confirms BC-GLOBAL-2 captured.
- m1 (nargs greediness), m2 (docstring): **VALIDATED** — ACCEPTED-PENDING; both built.
- m-add-1 (meta-Critic: repro docstrings documented rejected design): **VALIDATED** — ACCEPTED-FIXED.

**Missed by [design-]Critic**: the code-level output-honesty defect (M1 — `_format_human` rendering strict findings under the "parse violation(s)" header + `path=r.source` non-path label). This is a CODE-emergent the design-Critic + meta-Critic stack structurally cannot reach (they review design.md/ADR before code exists) — and the **code-Critic caught it exactly as CRSI-1 intends**. This is a clean datapoint for the three-persona division of labor: output-honesty / contract-consistency-inside-functions is a code-Critic surface, not a design-Critic one.

**Pattern**: dual design-Critic stack was 9/9 VALIDATED, zero FALSE-ALARM — consistent with the project's N=9/9 voluntary-Critic-on-methodology-surfaces record. The code-Critic earned its keep with M1. The design-Critic's "found the class, under-swept the surfaces" miss (M1 caught the rejected-design-doc class in the catalog but missed the repro docstrings — meta-Critic's m-add-1) recurred as a meta-Critic catch; sibling of the slice-074/075 RSAD-1 under-sweep. Watch for a 3rd occurrence → `/critic-calibrate` candidate (a "swept ALL surfaces of the flagged class?" Critic-prompt dimension).

## Lessons for next slice
- When adding an enforced gate to a computed-applicability audit (no per-item status field), the acknowledgment-flag design beats both blunt-count (un-passable) and status-row-surface (heavyweight) — reusable pattern for future audit-hardening slices.
- The code-Critic reaches output-honesty/contract defects inside functions that the design-Critic structurally cannot — keep relying on it for code-shape correctness, not just the design stack.
- A new `always:true` Critical rule imposes a standing per-slice ack cost; weigh that before promoting a build-check to Critical+always (vs Important or glob-scoped).

## Vault updates made (thin vault)
- `diagnose-out/backlog.md` — SC-008 round-tripped (`**Addressed:** slice-080-... on 2026-05-29`), dual-tree (main + worktree) per R-20.
- This slice's `design.md` + `ADR-072` — corrected PMI-1 leg enumeration to canonical 5 legs (B1, pre-build).
- `architecture/shippability.md` — row #85 (acknowledgment contract + BC-PROJ-10 citations); row #75 command propagation (B2).
- `methodology-changelog.md` v0.75.0 (BCSG-1) + 5-leg PMI-1 bump + MCFS-1/AVFS-1/TVFS-1/OSDG-1 forward-syncs.
- No new ADR beyond ADR-072; no new risk-register entry (no new risk discovered).
