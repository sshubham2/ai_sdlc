# Critique Review: Slice 093 add-external-vault-support

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-31
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's nine findings (B1, B2, M1–M4, m1–m3) are all VALID with correct severities — re-verified each against the real code; the empirical evidence holds exactly (zero false positives across nine, including a Blocker re-validated by execution). But the rev-2 fix-delta left one residual on this project's most-recurrent, most-expensive defect class: the B1 `tests/tools/` sweep missed **ADR-085:57**, which still names `tests/tools/test_vault_safe_write.py` — a fresh Blocker-class claim introduced by the fix itself.

## Confirmed findings

All nine first-Critic findings VALID, correct severity. Spot-verifications:
- **B1** — Blocker; mission-brief + design now use `tests/methodology/`; class history real (`lessons-learned.md:882`, slice-021/027/037).
- **B2** — Blocker; rev-2 AC3 writes ONLY `~/.claude/ai-sdlc-vault-base` via `safe_write_text`; wiring now a genuine consumer; INSTALL.md:162 confirms source-only. Resolved.
- **M1** — Major; `test_vault_root_constant.py:188` pins `== 12`; AC1 adds exactly 3 to that file → 15; arithmetic correct; AC2/4/5 land in NEW files (don't perturb the pin).
- **M2** — Major; PCR `.open("a")` at `parallel_conflict_resolver.py:713,764` (exact); field-recon.md:28,30 names O_APPEND distinctly; `safe_append_text` correct.
- **M3** — Major; mock-`os.replace`-raises strategy is the right cross-platform approach (two-layer per slice-090).
- **M4** — Major; independent grep of `NOT VAULT_ROOT-routed` = exactly 7 (cross_spec:336, drift_check:362/366, state_transition:381/395/407, validate:522); `_ERROR_MESSAGE_STRING_EXCLUSIONS` 5 tuples all off-by-one + miss both drift_check sites; out-of-scope-to-094 disposition correct (orphan test matches by substring).
- **m1** — Minor; LockFileEx-mandatory + sidecar-`.lock`-never-target correct.
- **m2** — Minor; SSoT constant + parity pin correct.
- **m3** — Minor; EXCLUDE mirrors ADR-065; underscore PMI-1 auto-exclusion real (`plugin_manifest_audit.py:148`; design cited :147, off-by-one but filter exists).

## Suspicious findings

None. The first Critic did not over-reach on any of the nine — each grounded in re-verified code.

## Missed findings

- **B-add-1 (Blocker): B1-fix residual at ADR-085:57 — the known-bad `tests/tools/` path survives the rev-2 sweep.** The Builder's B1 fix swept mission-brief.md + design.md but left ADR-085 line 57 (Reversibility): *"(4) delete `tests/tools/test_vault_safe_write.py` …"*. Exactly the phantom path B1 eliminates (namespace-collides with the top-level `tools/` package — slice-021 DEVIATION-2, `lessons-learned.md:882`). Per DR-1 task (3) the fix-delta under-swept; the Builder disposition (critique.md:20) claimed "no `tests/tools` remains in either artifact" — true for the two named artifacts, but the sweep scope excluded the ADR. Class has bypassed the dual-Critic stack twice (slice-027/037). **Severity Blocker** (copy-paste-executable path; class history). Reservation: if the user reads ADR Reversibility as non-executable narrative, it could be filed Minor — meta-Critic leans Blocker. **Fix**: ADR-085:57 `tests/tools/` → `tests/methodology/`; re-run FBCD-1 grep across `architecture/decisions/ADR-085*` too.
- **m-add-1 (Minor): design's "10 consumers" vs the file's stale "8-element" comments.** design.md + ADR reference "the 10 `_MIGRATION_SITE_ALLOWLIST` consumers"; the frozenset at `test_vault_root_constant.py:45-56` has 10 (design's count correct), but comments at L41/L281 say "8-element" (pre-existing drift; `test_migration_site_allowlist_pinned` computes dynamically so passes at 10). Pre-existing, not introduced by 093. **Fix (out-of-scope flag, like M4)**: a one-line design note; re-sync comments when the file is next edited (094 / opportunistically with the AC1 count-pin change); do NOT silently fix comments mid-slice beyond the sanctioned count-pin.

## Severity adjustments

None to the first Critic's nine — all correctly calibrated. The one severity assertion is on the NEW B-add-1 (Blocker-class, argued above).

## Notes

High confidence. Re-derived M4's "7" by independent grep; confirmed PCR `.open("a")` at 713/764; verified count-pin arithmetic, PMI-1 underscore filter, INSTALL.md source-only — every first-Critic empirical claim checks out (a genuinely strong first pass). The single calibration signal is in the Builder's fix-delta, not the Critic's findings: the B1 sweep was scoped to the two named artifacts and didn't extend to the ADR. Round-trip in reflection.md: B-add-1 = VALIDATED-ON-RECONSIDERATION; m-add-1 = pre-existing/noted.
