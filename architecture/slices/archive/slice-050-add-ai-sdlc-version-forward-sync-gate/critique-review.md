# Critique Review: Slice 050 add-ai-sdlc-version-forward-sync-gate

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-19
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong: all three Blockers, all four Majors, and all three Minors are VALID with correct severities, and M3's recompute against the real `shippability_decoupling_audit.py` is exactly right (`_ESSENTIAL_SHAPES` is changelog-path-only at `:95-97`; `classify_fn` returns `clean` for any other `~/.claude/...` read — the m-add-2 mechanism provably does not transfer). The Builder's ACCEPTED-FIXED edits are faithful and FBCD-1-harmonized. An independent re-application of the 8 dimensions surfaces two missed concerns the first Critic did not flag and the Builder's fixes did not close — both in the "cross-cutting conformance" and "drift from vault" dimensions, of the slice-032/042/048/049 "a design correction / new gate is itself an unguarded adversarial surface" class.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (tautological entry-pin) — confirmed; Blocker appropriate. `test_v_0_53_0_mcfs_1_entry_present_in_repo` (test_methodology_changelog.py:2952-2977) asserts 5 semantic literals; STP-1 pin (:3041-3065) asserts 5. Post-fix mission-brief AC4/must-not-defer + design.md now enumerate the required literals — faithful.
- **B2** (propagation pin unmapped) — confirmed; Blocker appropriate. Every catalog-bearing slice ships BOTH pins (MCFS-1 :2921/:2980; STP-1 :3024/:3068). Post-fix test-first plan adds the propagation row — correctly mapped.
- **B3** (CRLF-only comparator) — confirmed; Blocker appropriate. `methodology_changelog_forward_sync.py:105` is verbatim `read_bytes().replace(b"\r\n", b"\n")` — no whitespace strip. Post-fix all sites say "modulo line endings (CRLF↔LF) only"; byte-harmonized.
- **M1** (weak bootstrap) — confirmed; Major appropriate. Post-fix reasoning internally consistent (no residual unconditional "→ exit 0").
- **M2** (invented third `_wiring.py`) — confirmed; Major appropriate. MCFS-1 suite holds the relocation-proof + discharges WIRE-1 by "suite existing+passing"; post-fix collapses to two-artifact shape.
- **M3** (non-catalog rationale recomputed) — confirmed; Major appropriate; the single highest-value first-Critic finding, factually correct against `:95-97`+`classify_fn`.
- **M4** (whitespace-only-present edge) — confirmed; Major appropriate. Resolved by construction under the B3 comparator; explicit test row added.
- **m1** (SUP-1 reversibility wording) — confirmed; Minor appropriate. Post-fix ADR-052 says "supersede ADR-052 via a new ADR" — SUP-1-correct.
- **m2** (FBCD-1 comparator harmonization) — confirmed; Minor appropriate; folded into B3.
- **m3** (row #50 recompute) — confirmed; Minor appropriate. Independently verified: rows 40–49; max #49; next-free #50.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives recompute against the real tooling. No over-reach.

## Missed findings

- **M-add-1 (Major): `reflect/SKILL.md` AVFS-1 wiring block is an unguarded-drift surface the must-not-defer characterizes as "sufficient" when, by the slice's own R-7 argument, it is not.** design.md§components-touched correctly *observes* `reflect/SKILL.md` is NOT in the OSDG-1/mini-CAD guarded set and proposes to discharge the drift risk by "must-not-defer manual forward-sync + the post-build AVFS-1 self-run." This is internally circular: AVFS-1 gates the `ai-sdlc-VERSION` *value* leg — it does NOT read `reflect/SKILL.md` and cannot detect a stale installed `~/.claude/skills/reflect/SKILL.md` whose AVFS-1 post-write step was added in-repo but never forward-synced. If the installed copy is stale, `/reflect` reads the OLD prose, the AVFS-1 post-write step silently never runs, nothing detects it — precisely the R-7/slice-022 "gate silently never runs" class the mission-brief itself invokes (must-not-defer) to justify the dedicated-step decision for `build-slice`. The asymmetry is unguarded: `build-slice/SKILL.md` is OSDG-1-guarded; `reflect/SKILL.md` is not. The slice closes the `ai-sdlc-VERSION` leg while opening an analogous unguarded `reflect/SKILL.md` leg (slice-049 "leg-drift surfaced one slice late" class). **Proposed fix (user's TRI-1):** (a) add a scoped must-not-defer requiring the `reflect/SKILL.md` AVFS-1 block be re-verified by hand against the installed copy at the slice's own `/reflect` post-write step AND record an explicit Discovered-gap entry nominating `reflect/SKILL.md` for a future OSDG-1 extension (honest slice-049→050 nomination pattern applied to the gap this slice itself opens); OR (b) expand OSDG-1's guarded set to include `reflect/SKILL.md` in this slice (larger blast radius — likely out-of-scope). At minimum the design must stop characterizing "must-not-defer + post-build self-run" as *sufficient*.

- **M-add-2 (Major): the `/build-slice` skill-drift forward-sync obligation (OSDG-1, guarded SKILL.md) is asserted in prose but NOT pinned as a must-not-defer / pre-finish line.** design.md correctly states the in-repo edit "must be forward-synced to the installed copy in the same fix block (the `/build-slice` skill-drift test will FAIL otherwise)" — but this is prose only. `tests/methodology/test_build_slice_skill_drift.py` will FAIL at pre-finish if installed `~/.claude/skills/build-slice/SKILL.md` is not forward-synced after the AVFS-1 Step-6 block is added — a hard finish-gate the mission-brief pre-finish list (test_first_audit, plugin_manifest_audit, MCFS-1, drift-check) does NOT name. A slice modifying a guarded SKILL.md without naming the forward-sync as a must-not-defer/pre-finish item is the slice-049 OSDG-1 lesson un-applied. Distinct from M-add-1 (the *unguarded* reflect leg); M-add-2 is the *guarded* build-slice leg whose guard-discharge is unpinned. **Proposed fix:** add a pre-finish line "`/build-slice` skill-drift test green — installed `~/.claude/skills/build-slice/SKILL.md` forward-synced with the AVFS-1 Step-6 block (OSDG-1/mini-CAD obligation)" + a parallel must-not-defer item.

## Severity adjustments

No severity adjustments. All ten first-Critic findings carry the correct severity. B1/B2/B3 as Blockers each block `/build-slice` (tautological green / unmapped declared fn FAILing test_first_audit / contract-internal contradiction). M1–M4 Majors correct-this-slice non-build-blocking. m1–m3 Minors cheap. No miscalibration.

## Notes

High confidence on the confirmed set — every first-Critic finding independently recomputed against the real artifacts and all hold. Builder ACCEPTED-FIXED edits faithful + FBCD-1-harmonized (B3/m2 comparator byte-consistent across mission-brief AC1/AC2/must-not-defer + design.md + ADR-052; B1/B2 test fn names byte-identical between mission-brief test-first plan and design.md§What's-new; M3 corrected environment-mutable-state rationale sound + relocation-proof retains a coherent module-absence assertion; M1 bootstrap consistent across ADR-052/mid-slice/pre-finish; M2 collapse keeps the wiring assertion in-repo-only → `clean`). No unnamed META-1/PMI-1/test_methodology_changelog structural obligation surfaces (slice-044/STP-1 + slice-049/OSDG-1 format precedents correctly cited and satisfied). Verdict EXTEND on the strength of M-add-1 + M-add-2 — both the slice-032/042/048/049 recurring "the slice that closes leg N must not silently open analogous leg N+1" class, squarely in the dimensions the first Critic marked checked (cross-cutting conformance, drift from vault) but did not exhaust on the self-hosting-SKILL.md-forward-sync axis. Reservation: M-add-1 option (b) may be judged out-of-scope at TRI-1 (legitimate user call); the load-bearing content is that the design's "sufficient" characterization is, by its own R-7 argument, not sufficient and the gap must be explicit, not silent.
