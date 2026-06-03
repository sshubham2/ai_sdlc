# Critique Review: Slice 103 thin-vault-index-routers-and-enforce

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-03
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong on the load-bearing axis: B1 (unenforceable-prose preservation), M2 (542-lesson data-loss with no mechanism), M3 (heading-less archive anchor), M4/M5 (SVW-1/OSDG-1/flip-readiness gates) are all VALID with correct severities and verified against the real tree. But the review has one significant blind spot: it tracked the *writer* prose (reflect/archive regen) and missed the *reader* prose — `/slice`, `/critique`, and `/pulse` all read the `## Aggregated lessons` section by name, and the design renames/relocates it while editing none of those three consumers. One Minor (m2) is mis-stated against the file.

## Confirmed findings (VALID + correct severity)

- **B1** (register preservation is unenforceable prose) — confirmed; Blocker appropriate. `slice_queue_writer.py:127/727/660` is genuinely CODE (no LLM); `archive/SKILL.md:64-65` routes `_index.md` regen through a Haiku subagent + `vault_edit rewrite`. `register-missing` catches total loss but not silent entry-dropping within `1 ≤ n ≤ 25`. **The Builder's fix (b) — separate `action-points.md` — is sound on the preservation axis** (removes the LLM from the loop), BUT see M-add-1: it relocates the problem onto an un-updated reader surface.
- **M2** (542-lesson data-loss) — confirmed; Major. Verified 542 bullets vs 2,141-line `lessons-learned.md`; hand-verification infeasible; orphan-diff script is right.
- **M3** (archive has no `## ` heading) — confirmed; Major. `grep '^## '` on `archive/_index.md` returns zero; the region anchor is genuinely undefined; folding APED-1 in is correct.
- **M4** (reflect/archive regen edits risk SVW-1 + OSDG-1) — confirmed; Major. `reflect/SKILL.md:321` carries the `vault_edit rewrite` route token; `reflect` is OSDG-1-guarded. (This is the near-miss — writer-side only; see M-add-1.)
- **M5** (new tool must pass flip-readiness) — confirmed; Major. shippability 108/109 pin `vault_flip_readiness_audit --strict` over all `tools/**/*.py`.
- **m1** (recent-10 has 20 data rows) — confirmed; Minor. 22 pipe-lines = header + separator + 20 data rows; count-cap fix correct.
- **m3** (400-char cap headroom) — confirmed; Minor. Raising to 500 is safe.

## Suspicious findings

- **m2** (code fence at `_index.md:286`) — **SUSPICIOUS as stated; real adjacent concern survives.** Line 286 is a prose bullet with an *inline* triple-backtick literal inside a code-span (`step_1.find("` + "```bash" + `\n")`), NOT a block fence. `grep -c '^```'` = 0; only `grep -c '```'` (anywhere) = 1. The stated framing ("a fence inside the cut region") is inaccurate — there is no block fence to strand. The Builder's ACCEPTED-PENDING fix ("grep for balanced fences") would itself **mis-fire** — a naive substring `` ``` `` count flags this inline literal as unbalanced, re-introducing the `marker in line_text` whole-line-scan false-positive the slice's own Must-not-defer warns against (slice-099/100 N=4). **Re-state**: the concern is "the inline triple-backtick literal must not be mistaken for a block fence by the audit's region parser, nor trip a naive post-cut fence-balance grep"; the fix is a *line-anchored* (`^```) check, not a substring scan. A downgrade of the stated defect, not a drop.

(No other suspicious findings. B1's Blocker severity survives scrutiny — the preservation gap is the slice's own diagnosed root cause recurring.)

## Missed findings

- **M-add-1 (Major): The register rename/relocation orphans the `/slice`, `/critique`, and `/pulse` reader prose — the design edits only the writer surface.** The design replaces `## Aggregated lessons` with `## Cross-slice action points` (and the B1 fix moves it to a separate `action-points.md`), but **four reader surfaces point at the old section by name and are NOT in the design's edit set**:
  - `skills/critique/SKILL.md:67` + **:93-94** (the literal Critic-input template `# Aggregated lessons (from slices/_index.md)`) — the Critic's own pattern-recognition input;
  - `skills/slice/SKILL.md:28, :68, :71` (three reads as `/slice` pattern-recognition + deferral source);
  - `skills/pulse/SKILL.md:43, :236` (pulse reads aggregated lessons).

  Consumer-driven-contract violation (Newman): renaming a producer's published section without updating registered consumers silently degrades the pattern-recognition input to empty with no error after the cut. Same class as M4 but on the **read side**. The irony: ADR-093 Option 2's rejected con was "extra reads for `/slice`, `/critique`" — the B1 fix *adopts* Option 2, making this surface live, yet the design never enumerates the consumer edits. **Proposed fix**: add to design Components-touched + AC set the consumer-prose edits to `skills/slice/SKILL.md` (3 sites), `skills/critique/SKILL.md` (2 sites incl. the input-template block), `skills/pulse/SKILL.md` (2 sites); `critique` IS OSDG-1-guarded (forward-sync — extends M4's obligation to a second skill); `slice`+`pulse` are not OSDG-1-guarded; confirm `skills/slice/SKILL.md:221` (prose evidence-citation) updates or is explicitly left as a historical anchor.

(No other missed findings. The COST-1 Haiku dispatch of the 102-row archive regen is the EXISTING mechanism, explicitly out-of-scope per the mission-brief — a build-execution cost, not a design defect. The new `action-points.md` is curated (never written by `tools/*.py`, never RMW'd by the regen path), so VWS-1/SVW-1 don't gate it, and it has no `architecture` path literal, so flip-readiness is N/A — non-issues, correctly absent.)

## Severity adjustments

None. All confirmed findings carry correct severities. **M1 is correctly Major, not a Blocker** — the MEPD-1 EXCLUDE lane IS defensible: enforcing an already-documented prose contract (`archive/SKILL.md:113/115/120`) + adding a tool, with the slice-100 precedent (shippability row 108 is itself a new audit tool added EXCLUDE), genuinely mints no new RULE-ID. The real defect M1 names is the AC4 *wording* ("wired into the slice-finish gate roster" vs the shippability-only wiring) — a Major consistency fix, resolved by the Builder's "keep shippability-only, reword AC4". **This slice does NOT need a VERSION bump.**

## Notes

High confidence. The first Critic's coverage of the hard axes (B1's prose-vs-code distinction, M2's infeasibility, M3's heading-less anchor, M4/M5's gate obligations) is accurate and verified — a competent review, not over-reach. The single calibration signal is a **reader/writer asymmetry**: the Critic instrumented the producer side of the section-rename (M4) thoroughly but never asked "who *reads* this section by name?" — and the B1 fix it accepted makes that gap larger. That's the single-slice blind spot DR-1 exists to catch. Net: EXTEND (one missed Major) co-occurring with ADJUST (one re-stated Minor).
