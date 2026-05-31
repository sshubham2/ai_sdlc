# Critique Review: Slice 088 add-project-frame-synthesizer

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-31
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's 11 findings are all VALID with correct severities — verified on disk (heading literals, version convention, cp1252 mechanism, OSDG-1 registry shape). The Builder's 10 ACCEPTED-FIXED deltas are largely sound. But the B1/B2 fixes close the *narrow* cp1252 hole (the tool's own emitted literals) while leaving the *wide* one open: the synth re-emits **extracted source text** (changelog rule-family headers, risk-register titles) that is saturated with U+2014 em-dashes, and neither the B1 fix nor the B2 bespoke-test spec guarantees that path is sanitized or exercised. That is a build-time crash on the hot path the slice exists to protect. One missed finding (M-add-1, Major) plus one severity-adjacent under-specification (M-add-2, Minor).

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1**: ASCII-only emitted preamble/marker — confirmed; Blocker appropriate. The `_(none)_` degrade marker and section bullets are pure ASCII — verified clean. ADR-080 prose `⚔` is markdown, never emitted — correct exclusion. *(But see M-add-1: the fix is incomplete on the extracted-text path.)*
- **B2**: wrong `_ROOT_ONLY_TOOLS` bucket → bespoke test — confirmed; Blocker appropriate. `_root_only_argv` passes only `--root`, which `project_frame_synth` (required `--slice-dir`) would reject with exit 2 before rendering. The bespoke carve-out is the correct pattern (mirrors `test_install_audit_survives_cp1252`). *(But see M-add-2: rollup-sentinel parity obligation unstated.)*
- **B3**: consumption-contract gap — confirmed; Blocker appropriate. The new design.md §"Consumption contract" specifies Bash-capture → verbatim-paste-under-`# project-frame.md` → `(project-frame unavailable)` fallback for all three consumers. The paste-block precedent it mirrors is real (skills/critique/SKILL.md:80,83). Buildable.
- **M1**: smoke command vs required `--slice-dir` — confirmed; Major appropriate. Fixed in mission-brief.
- **M2**: phantom entry-pin convention — confirmed; Major appropriate. All sibling pins use `_entry_present_in_repo` (NOT `_and_installed`); current VERSION 0.77.0, latest pin v0_77_0_pcr_2b → **0.78.0 is correct next**; META-1 `Rule reference` obligation real. Fix correct.
- **M3**: OSDG-1-extension discharge + CLAUDE.md guard — confirmed; Major appropriate. Verified NO hidden per-skill OSDG-1 registry: `_GUARDED_GLOBS` is glob-based (`skills/**/SKILL.md`, auto-covers all three) and `install_audit._CANONICAL_SKILLS` already lists all three. The 3 new drift tests + glob normalization test ARE the membership. M3 fix sufficient.
- **M4**: synthesis-not-concatenation — confirmed; Major appropriate. The new test pins deduped rule-FAMILY extraction + score-sorted-with-score risks + named candidates — genuine synthesis invariants a concat fails. Sound.
- **M5**: Step-0.5 chicken-and-egg — confirmed; Major appropriate. design.md + AC #2 now state Impact expected-degraded; consumerless Step-7 re-synth correctly DROPPED.
- **M6**: structural-pin BC-PROJ-14 — confirmed; Major appropriate. Verified seams against real headings: `### Step 2:` exists in skills/critique/SKILL.md:69 + skills/critique-review/SKILL.md:51; `### Step 0.5` does NOT yet exist in design-slice (Step 0 @ L25, Step 1 @ L78) — the slice CREATES it; forward pin valid, ordinal property satisfiable. No dead pins.
- **m1**: HOME-path changelog read — confirmed; Minor appropriate. Now reads in-repo repo-root changelog.
- **m2**: R-7-class silent-degrade risk — confirmed; Minor appropriate; ACCEPTED-PENDING (build-time register) acceptable.

## Suspicious findings

None. Every first-Critic finding survived on-disk scrutiny; none is a false positive and none is over-severe.

## Missed findings

- **M-add-1 (Major): The B1 fix sanitizes the tool's OWN literals but NOT the extracted source text it re-emits — em-dash (U+2014) from changelog/risk headers will still crash cp1252 stdout on the hot path.** The synth extracts Trajectory rule-families "from changelog headers" and risks from `risk-register.md`. Both sources are saturated with U+2014: changelog headers are `## v0.77.0 — 2026-05-30`; risk headers are `## R-1 — …` and the RR-1 schema *explicitly mandates* the em-dash as the canonical `## R-N — <title>` separator (risk-register.md:3 "em-dash separator, canonical"). If the render emits any extracted family-name/risk-title verbatim, `print()` to cp1252 stdout raises `UnicodeEncodeError` — the exact B1 class, on a path B1's stated fix does not cover. **Proposed fix**: mandate that *all* emitted text — including extracted source tokens — passes an ASCII-fold/transliteration step before stdout; the B1 must-not-defer must say "ASCII-only emitted output **including extracted source text**".

- **M-add-2 (Minor): The B2 bespoke cp1252 test will not exercise the em-dash risk unless its fixture carries U+2014, AND it must emit the literal token `tools.project_frame_synth` to satisfy rollup-sentinel parity.** (1) `project_frame_synth.py` has a `main()` so it lands in the rollup sentinel's `discovered_set` (test_utf8_stdout_regression.py:450-474); the bespoke test MUST call `_assert_no_encoding_error(proc, "tools.project_frame_synth")` with that exact literal or `test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` FAILS with an uncovered-tool parity break. (2) named `_with_u2192` but the real risk is U+2014 em-dash from headers — fixture must contain em-dash-bearing source or the test passes vacuously. **Proposed fix**: state both the literal-token call and the em-dash fixture requirement. *(Parity half is fail-closed at test-time → Minor; vacuous-fixture half could ship a real crash silently.)*

## Severity adjustments

None. All 11 first-Critic severities correctly calibrated.

## Notes

High confidence — every claim verified against on-disk literals in the worktree (heading positions, VERSION=0.77.0, the entry-pin convention across 66 siblings, the `_GUARDED_GLOBS` glob shape, the rollup-sentinel discovered/covered mechanism, em-dash saturation of the two extracted sources). Calibration observation: the first Critic was sharp on the surfaces it inspected (real argv shapes, real convention, real bucket) with zero false positives — but it stopped at the tool's OWN emitted strings for B1 and didn't trace the cp1252 risk one hop further to the EXTRACTED text the synth's whole purpose is to render. That single-hop blind spot is exactly what DR-1 exists to catch. Reservation: M-add-1's severity assumes verbatim emission; if the Builder applies an ASCII-fold on all output, M-add-1 is pre-addressed and downgrades to a documentation gap — confirm the sanitization point explicitly.

## Disposition (folded into critique.md TRI-1 triage)

- M-add-1 → ACCEPTED-FIXED (`_ascii_fold()` on the full rendered frame before stdout — design.md §Components).
- M-add-2 → ACCEPTED-FIXED (rollup token + em-dash fixture stated — design.md §BC-PROJ-9 surface (2)).

User-ratified at TRI-1 (2026-05-31); see critique.md §Triage. Final verdict: NEEDS-FIXES.
