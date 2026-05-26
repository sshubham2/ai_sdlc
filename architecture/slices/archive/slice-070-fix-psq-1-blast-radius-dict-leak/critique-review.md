# Critique Review: Slice 070 fix-psq-1-blast-radius-dict-leak

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-26
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic delivered a textbook APED-1 catch (B1) — empirically executing graphify against the live `graphify-out/graph.json` and discovering the proposed `path → name → id` precedence falls through to opaque IDs because all `path` values are empty and `name` is absent from the schema. The fix-block redesign (`_build_id_to_path_map` + id-lookup-then-forward-compat-fallback) is empirically sound and the new test fails pre-fix for the right reason. However, the SAME fix-block-introduces-residual-drift defect class meta-Critic has caught on slices 062/064/067 recurs here: two surfaces still cite the OLD `path → name → id` precedence (mission-brief.md L51 must-not-defer + design.md L66 prose), contradicting the redesigned id-lookup-PRIMARY precedence pinned at design.md L143-175 pseudocode + L88 Fix-shape opening sentence + AC#2 shape-(b). N=4 cumulative recurrence (slice-062 N=1 + slice-064 N=2 + slice-067 N=3 + slice-070 N=4) of "B/M fix-block introduces residual stale reference at peripheral surface" — same shape as slice-067 /critique-review M-add-3 ("design.md L21 'dogfood seed' residual after M2 fix").

## Confirmed findings

All 11 ACCEPTED-FIXED first-Critic findings reviewed:

- **B1 (path→name→id produces non-path output)** — VALID; severity Blocker is appropriate. Independently re-verified empirically: `graphify-out/graph.json` has 2791 nodes; key frequency is `{label:2791, file_type:2791, source_file:2791, source_location:2791, community:2791, id:2791}` — zero `path` keys, zero `name` keys. The Builder's redesign correctly threads through `_build_id_to_path_map`'s id→source_file lookup. The /repro test FAILS pre-fix for the right reason (verified via `pytest` execution — the dict-string leak appears in the result set as expected).
- **B2 (test mocks fictional shape)** — VALID; severity Blocker. The rewritten /repro fixture `tests/bugs/test_psq_1_blast_radius_dict_leak.py:46-59` now uses the empirically-verified real graphify shape (`{"id": ..., "label": ..., "type": "", "path": ""}`).
- **M1 (AC3 weak-proxy regex)** — VALID; severity Major. Empirically tested the redesigned positive-shape regex `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$`: correctly accepts `tools/foo`, `a/b`, `tools/foo.py`, `docs/readme`, `config.yaml`; correctly rejects `opaque`, `slice_queue_writer_rationale_1`, `noslash_noext`. The regex IS correctly escaped — both in mission-brief L20 and design.md L20.
- **M2 (R-X2 inverted framing)** — VALID; severity Major. R-X2 rewrite at design.md L220 is accurate. Edge case noted: a node `{"id": "exception", ..., "source_file": ""}` (empty `source_file`) is excluded from the id→path map per the `not (... and src)` guard in `_build_id_to_path_map`. The AC#3 positive-shape regex catches any regression that leaked this through.
- **M3 (R-X3 incomplete enumeration)** — VALID; severity Major. R-X3 collapsed into M1's positive-shape regex with cross-reference at design.md L221.
- **M4 (AC#2 mis-aligned)** — VALID; severity Major. Mission-brief AC#2 line 19 correctly widened to 4 shapes including the actual current-graphify shape.
- **M5 (ADR-064 citation drift)** — VALID; severity Major. Independently re-verified: `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md` contains "durable across sessions" as one pro of the chosen option. The Builder's reframed citation at mission-brief L5 is precise.
- **M6 (LOC count drift)** — VALID; severity Major. LOC counts excised from design.md L13 + L38 in fix-block.
- **m1 (smoke gate too narrow)** — VALID; severity Minor. Mission-brief Mid-slice smoke gate L90-95 broadened to run full module (6 tests).
- **m2 (slice-069 wiring matrix unverified)** — VALID; severity Minor. Builder's spot-check at slice-069 design.md L60-65 confirmed same shape.
- **m4 (shippability row placeholder)** — VALID; severity Minor. shippability.md row #70 (per Read at L79) shows no residual placeholder clause — confirmed excised.

## Suspicious findings

- **m3 OVERRIDDEN** — m3 OVERRIDE is sound. Independently verified `~/.claude/skills/reflect/SKILL.md:59` BCR-1 prose: trigger is "this slice's `mission-brief.md` or `reflection.md` carries an explicit `**Closes:** SC-\d{3}` sentinel header" — singular trigger key on the SC-NNN identifier, NOT per-mention count. Multi-mention of `**Closes:** SC-027` does NOT double-trigger. The Builder's m3 OVERRIDDEN rationale tracks /reflect SKILL.md L59 prose accurately.

(No suspicious findings against ACCEPTED-FIXED first-Critic findings.)

## Missed findings

- **M-add-1: design.md L66 Decisions-made-(ADRs) section cites STALE precedence `path → name → id`** — Major. The fix-block redesign (B1 ACCEPTED-FIXED) restructured the precedence to `id-via-map (PRIMARY) → dict-own-keys-if-path-shaped (forward-compat) → None`, pinned at design.md L143-175 pseudocode + L88 Fix-shape opening sentence + AC#2 shape-(b) at mission-brief L19. But design.md L66 still said: *"the preferred-key precedence `path` → `name` → `id` is documented in the `_node_to_path` docstring"*. This is the EXACT old precedence the B1 redesign repudiated. A future maintainer reading L66 (Decisions made section) would believe the `_node_to_path` docstring documents `path → name → id`, attempt to verify, find the docstring documents the NEW precedence, conclude design.md is contradictory, and either (a) revert the docstring to match L66's prose (re-introducing B1's defect class) or (b) waste time reconciling. Framework: Wiegers IEEE 830 §4.3 internal-consistency requirement. Cross-doc drift between design.md sections is a textbook spec-coherence violation. **Builder fix (applied at /critique-review fix block per TPHD-1 sub-mode (b))**: design.md L66 rewritten to *"the precedence — id-via-`graph.json`-`source_file`-map (PRIMARY) → dict-own-`path`/`source_file`/`name` if path-shaped (forward-compat fallback) → None (skip) — is documented in the `_node_to_path` docstring"*. **Builder draft disposition**: ACCEPTED-FIXED.

- **M-add-2: mission-brief.md L51 Must-not-defer item #3 cites STALE precedence `path → name → id → skip`** — Major. Same defect class as M-add-1 but on the mission-brief surface. Line 51 read: *"Deterministic path-extraction precedence — `path` → `name` → `id` → skip; documented in the helper docstring + pinned by the unit tests"*. This was internally inconsistent with mission-brief.md L19 AC#2 shape-(b) description and with line 14 (Intent) which describes the new id-lookup-PRIMARY strategy. "Must-not-defer" items have higher binding weight than design.md prose: they enumerate the slice's BUILD-time obligations. The Builder reading line 51 at /build-slice would be instructed to implement the OLD precedence, contradicting their own redesigned pseudocode. Framework: Sommerville §4.2.3 (must-not-defer items are binding pre-build contracts; cross-spec parity per RPCD-1 / CSP-1 is non-negotiable). **Builder fix (applied at /critique-review fix block per TPHD-1 sub-mode (b))**: mission-brief L51 rewritten to *"Deterministic path-extraction precedence — id-via-`graph.json`-`source_file`-map (PRIMARY) → dict-own-`path`/`source_file`/`name` if path-shaped (forward-compat fallback) → None (skip); documented in the `_node_to_path` docstring + pinned by the 6 tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (closes the 'silently swallow garbage' footgun AND the slice-070 /critique B1 wrong-precedence defect class)"*. **Builder draft disposition**: ACCEPTED-FIXED.

- **M-add-3: TPHD-1 sub-mode (a) cross-file harmonization for B1 fix INCOMPLETE — N=4 cumulative recurrence on N+1 doctrine** — Major. M-add-1 + M-add-2 share a defect class: the first Critic's B1 redesign restructured the precedence across mission-brief L14 + L19 + L20 + design.md L88-92 + L143-175, but the fix-block missed two peripheral surfaces (mission-brief L51 + design.md L66) that still cite the OLD precedence. This is the EXACT same defect class meta-Critic surfaced at: slice-062 /critique-review M-add-1 (m3 ACCEPTED-FIXED fix-block introduced TF-1 audit violations), slice-064 /critique-review M-add-1 (B1 fix INCOMPLETE — 3 residual stale-path sites at mission-brief.md L21+L78 + design.md L109), slice-067 /critique-review M-add-3 (design.md L21 "dogfood seed" residual after M2 fix). N=4 cumulative on the "Builder fix-block sweep gap" axis means this is now a **predictable, structural failure pattern**. Framework: Slice-040 N+1 first-governed-slice doctrine. **Builder fix (applied at /critique-review fix block)**: M-add-1 + M-add-2 already addressed in the same meta-fix block. Empirical post-sweep verification ran: `grep -nE "\`path\` → \`name\` → \`id\`|path → name → id|preferred-key precedence" mission-brief.md design.md` returns ZERO matches — clean. **/critic-calibrate candidate**: meta-Critic suggests a `/critic-calibrate` cross-slice pattern-update to `agents/critique.md` at N=4 — first Critics could be prompted to perform a "stale-anchor sweep" pass AFTER drafting fix-block dispositions, BEFORE finalizing the critique. Deferred to `/critic-calibrate`'s domain (long-term prompt drift), not this DR-1 review's per-slice scope; flagged here only for situational awareness. **Builder draft disposition**: ACCEPTED-FIXED (M-add-1 + M-add-2 sweep complete; /critic-calibrate candidate filed for next calibration run).

## Severity adjustments

(No severity adjustments to first-Critic ACCEPTED-FIXED findings.)

## Notes

Confidence in this review: HIGH. The 3 missed findings are concrete and reproducible (any reader can search mission-brief L51 + design.md L66 pre-fix and confirm the stale `path → name → id` precedence text). The first Critic's 8-dimension coverage was strong on the core APED-1 catch (B1 + B2) and accurate on all 11 ACCEPTED-FIXED findings, but did NOT perform a post-fix-block cross-surface sweep for residual stale references — a discipline meta-Critic has been auditing since slice-062. The N=4 cumulative recurrence on the "fix-block residual stale-reference" defect class is approaching the threshold where a `/critic-calibrate` cross-slice pattern-update to `agents/critique.md` may be warranted. The m3 OVERRIDE rationale was independently verified against /reflect SKILL.md L59 prose and is sound. The redesigned regex AC#3 contract was empirically re-verified and behaves as intended on all conceptual probe cases. The empirical-verification posture the first Critic established (APED-1 in B1) is consistently the strongest catch surface this dual-Critic stack produces — both the first Critic AND meta-Critic depend on it for grounding.

Post-meta-fix-block verification: `grep -nE "\`path\` → \`name\` → \`id\`|path → name → id|preferred-key precedence"` against `mission-brief.md` + `design.md` returns 0 matches. Stale-precedence drift retired across all surfaces.

Sources / files referenced (absolute paths):
- `C:\Users\sshub\ai_sdlc\architecture\slices\slice-070-fix-psq-1-blast-radius-dict-leak\mission-brief.md`
- `C:\Users\sshub\ai_sdlc\architecture\slices\slice-070-fix-psq-1-blast-radius-dict-leak\design.md`
- `C:\Users\sshub\ai_sdlc\architecture\slices\slice-070-fix-psq-1-blast-radius-dict-leak\critique.md`
- `C:\Users\sshub\ai_sdlc\tests\bugs\test_psq_1_blast_radius_dict_leak.py`
- `C:\Users\sshub\ai_sdlc\tools\slice_queue_writer.py`
- `C:\Users\sshub\ai_sdlc\graphify-out\graph.json` (empirically queried — confirmed 2791 nodes, zero `path` keys, zero `name` keys, 2790/2791 populated `source_file`)
- `C:\Users\sshub\ai_sdlc\architecture\decisions\ADR-064-mint-psq-1-parallel-slice-queue.md`
- `C:\Users\sshub\.claude\skills\reflect\SKILL.md` (L59 BCR-1 prose)
- `C:\Users\sshub\ai_sdlc\diagnose-out\backlog.md` (SC-027 block L558-576)
- `C:\Users\sshub\ai_sdlc\architecture\shippability.md` (row 70 at L79)
