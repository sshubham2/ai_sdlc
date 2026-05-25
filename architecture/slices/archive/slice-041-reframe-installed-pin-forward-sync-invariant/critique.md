# Critique: Slice 041 reframe-installed-pin-forward-sync-invariant (REV-3)

**Critic reviewed**: mission-brief.md (rev-3), design.md (rev-3), ADR-042, ADR-043, rev-1/rev-2 critique+critique-review lineage, R-4 charter
**Date**: 2026-05-18
**Result**: CLEAN
**Context**: rev-3 implements the slice-030A/031 non-convergence structural pivot (rev-1 BLOCKED + rev-2 BLOCKED#2, flaw relocating). DR-1-pre-verified by execution; the rev-3 first-Critic re-verified every load-bearing claim by *executing* the audit/classifier (the recorded twice-violated "execute don't reason" law).

## Summary

Every load-bearing rev-3 claim confirmed by execution (not reasoned about `_ESSENTIAL_SHAPES`): the leg-drop yields **0/33** in-module essential fns; the cross-module LAYER-EVID-1 pin provably stays `essential` (segs `{.claude, diagnose, methodology-changelog.md, skills}` survive leg-drop); post-decouple essential set is exactly **cardinality-1**; registering that one qualname ⇒ audit **exit 0**; the closed-world rule HALTs a hypothetical future unregistered essential; MCFS-1 is structurally non-catalog (`_cited()` only yields `tests/`-rooted targets); the scope-cut is genuinely orthogonal to R-4; MEPD-1 (a) rule-path discharged against the real `test_each_changelog_entry_carries_rule_reference` L141 assertion. **No blockers, no majors.** slice-031/030A "structural pivot → one-pass convergence"; CLEAN is the correct, non-manufactured verdict.

## Findings

### Blockers (must address before /build-slice)
None.

### Majors (address this slice)
None.

### Minors (recorded build-time obligations the design already states correctly — not design defects)

#### m1: `/reflect` MCFS-1 wiring must be a NEW dedicated step, NOT folded into rule-promotion-gated Step 5b
- **Issue**: verified build-time hazard, not a defect — `skills/reflect/SKILL.md` Step 5b is opt-in ("promotion is opt-in"); BCI-1 fail-loud L208 is "mandatory **when a rule was promoted**". Folding MCFS-1 there silently disables it on no-promotion slices (R-7/slice-022 class). design.md wiring matrix + must-not-defer m1 + V4 already call this out; primary gate is the verified-ungated `/build-slice` Step 6.
- **Evidence**: `skills/reflect/SKILL.md:159,208,219`; `skills/build-slice/SKILL.md:134,151,235`.
- **Builder draft**: ACCEPTED-PENDING — no design change; the design already mandates the correct placement. Honored at `/build-slice` per must-not-defer m1 + V4 (read both anchors, confirm new step ≠ Step 5b). Recorded for calibration tracking.

#### m2: Decouple worklist must be regenerated from `--json` `essential`, never hand-copied (rev-1 failure mode)
- **Issue**: recorded discipline, not a defect — real essential set = 33 in-module + 1 cross-module (rev-1 hand-counted "32", wrong twice). Builder must regenerate the leg-drop worklist from live `--json` at build (+ the 4 defined-but-uncited v43/45/47/48, verified exactly those). AC #3 / V2 already mandate this.
- **Evidence**: executed `tools.shippability_decoupling_audit --json` — 33 in-module unique essential incl. `v_0_42_0`; exactly 4 defined-but-uncited.
- **Builder draft**: ACCEPTED-PENDING — no design change; Builder regenerates from `--json` per AC #3 / V2 at `/build-slice`. Recorded for calibration.

## Dimensions checked
- [x] Unfounded assumptions — none (rev-1/rev-2's two unfounded assumptions were the BLOCKED causes; rev-3 every quantitative claim re-derived by execution; MEPD-1 verified vs the actual L141 assertion).
- [x] Missing edge cases — none material (MCFS-1 covers installed-absent→WARN, empty-present→HALT, CRLF-only→0, divergent→1; closed-world covers future-unregistered-essential).
- [x] Over-engineering — none (1-element frozenset + ADR-gated growth; minimal `audit()` branch; `classify_fn` correctly unchanged).
- [x] Under-engineering — none (every AC ↔ design element ↔ V1–V6; M3 in-repo-only-body pin verified `clean` by simulation; BC-PROJ-4 pre-finish backstop relied on over the twice-wrong Critic stack).
- [x] Contract gaps — none (MCFS-1 CLI + SCMD-1 contract fully specified and execution-verified).
- [x] Security — none (read-only; closed-world registered allowlist is the intended relocation-proof authorization analogue, execution-verified).
- [x] Drift from vault — none; ADR-042/043 append-only/supersede-nothing/preserve ADR-031; **R-4 charter L90 literally "registered not absent" → rev-3 charter-faithful** (rev-1 empty-allowlist was the deviation); MEPD-1 (a) rule-path discharged vs the real enforcing assertion; 4-part PMI-1 enumerated incl. installed `~/.claude/ai-sdlc-VERSION`; `agents/critique.md` correctly NOT edited (scope-cut; CAD-1 preserved; `test_critique_agent.py:1424` prefix-only/rename-safe).
- [x] Web-known issues — none (pure-stdlib comparator, structurally identical to in-production BCI-1/EOL-DRIFT-1; no external surface).
- [x] Cross-cutting conformance — none; APED-1 executed-not-reasoned (closed-world logic run over the real post-decouple set); PTFFD-1 (v0.53.0 pin keeps extant convention, no phantom; MCFS-1 module+row authored LAST + V1 self-classification); scope-cut execution-verified orthogonal + honestly deferred (slice-035, documented ×3); FBCD-1 cardinality-1/"0/33" claims byte-consistent across mission-brief/design/ADR-042/ADR-043.

## Triage

**Triaged by**: user
**Date**: 2026-05-18
**Final verdict**: NEEDS-FIXES

> rev-3 reconciliation (first-Critic CLEAN + DR-1 EXTEND). slice-030A/031 "structural pivot → one-pass convergence, confirmed": rev-1 BLOCKED → rev-2 BLOCKED#2 (flaw relocated) + structural pivot → rev-3 CLEAN-core. DR-1 verified the CLEAN is genuine (every claim execution-confirmed; rev-1 DR-1's reasoned false-confirm explicitly contrasted) + surfaced 2 genuine missed Minors (m-add-1/m-add-2, both pre-finish-backstopped). No blockers/majors; no 4th loop (EXTEND Minors are build-time/design-note, not relocation). m1/m2 = ACCEPTED-PENDING build-time obligations on an already-correct design (m1 correctly Minor at rev-3 — the design now mandates the ungated wiring it lacked at rev-1; the must-not-defer "(Major)" label is the orthogonal enforcement-priority weight). m-add-1/m-add-2 = ACCEPTED-FIXED (design.md notes added pre-triage). Verdict NEEDS-FIXES (ACCEPTED-PENDING present) → proceed to user-invoked `/build-slice` with the 2 build-time obligations tracked.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| m1 | Minor | ACCEPTED-PENDING | Design already mandates the ungated `/build-slice` Step 6 + NEW non-Step-5b `/reflect` step (design.md L31/L69); honored + both anchors read at `/build-slice` per must-not-defer m1 + V4. |
| m2 | Minor | ACCEPTED-PENDING | Decouple worklist regenerated from live `shippability_decoupling_audit --json` `essential` at `/build-slice` per AC#3/V2 (never hand-copied — rev-1 failure mode). |
| m-add-1 | Minor | ACCEPTED-FIXED | Two-syntactic-form (17 bare + 20 inline `.read_text()`) leg-drop note added to design.md `test_methodology_changelog.py` component; post-leg-drop `--json`-empty-essential is confirmation not discovery (V2). |
| m-add-2 | Minor | ACCEPTED-FIXED | Negative-cataloging invariant added to design.md MCFS-1 component: the MCFS-1 regression suite is intentionally NOT shippability-cited (would self-violate `essential-unregistered`); only the in-repo-only entry-pin row is cited (V1). |
