# Critique Review: Slice 058 add-install-wakeup-prompt-guardrail

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-22
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary
The first Critic's six findings are all VALID with correct severities, and the Builder's four ACCEPTED-FIXED edits resolve them without relocating the flaw. However, the second pass surfaces two genuine missed concerns — an unspecified install-step placement/numbering (the design says "a new step modelled on Step 3d" but never says *where* it slots into the Step 3a-3g sequence) and a test/text coupling risk (AC2's discrete asserts bind to a block still labelled "Draft:"). Verdict is EXTEND.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (test-function name inconsistent across three sites — FBCD-1 sub-mode (a)) — confirmed; severity Blocker is appropriate. A cross-file name divergence between mission-brief.md test-first plan and design.md wiring matrix is exactly the FBCD-1 class. The Builder's fix (canonical name `test_shippability_row_58_present_and_cites_install_wakeup_guardrail` pinned byte-identical across mission-brief test-first plan, verification plan, and the design.md "Test design notes → AC3" + wiring matrix) genuinely closes it — confirmed the post-fix design.md carries the canonical name at every site. No flaw relocation.
- **B2** (slice touches INSTALL.md but leaves the stale `v0.54.0` literal at INSTALL.md:18) — confirmed; severity Blocker is appropriate per the brownfield rule "doc says X but code/VERSION says Y → fix or log out-of-scope." Verified INSTALL.md:18 reads `methodology v0.54.0` while VERSION is `0.62.0` — a real known-false literal. See Severity adjustments for a scope-precision note on the Builder's *fix wording* — the finding itself is sound.
- **M1** (AC3 row-count ambiguity — one test or two) — confirmed; severity Major is appropriate. The Builder's fix (AC3 delivered by exactly ONE function making two assertions) resolves it cleanly, consistent with the slice-056/057 `test_shippability_row_NN` precedent.
- **M2** ("Genuine contrast" must-not-defer under-specified — AC2 needs discrete per-fact assertions) — confirmed; severity Major is appropriate (a pin that cannot FAIL pre-edit is not a regression guard). The Builder's fix (four discrete asserts) is the right shape. One residual concern about pinnability against a still-"draft" block — see Missed findings M-add-1.
- **m1** (ADR-057 numbering — verified clean) — confirmed. Independently verified `architecture/decisions/ADR-057-seed-wakeup-prompt-guardrail-via-install-global-claude-md.md` exists, `id: ADR-057`, `slice: slice-058`, `supersedes: null`. No collision.
- **m2** (design.md `## v0.63.0` next-version reference — confirmed correct) — confirmed; the BC-PROJ-10 classification carries NO version bump, so any v0.63.0 reference is forward-looking only and not load-bearing.

## Suspicious findings

No suspicious findings. None of the first Critic's six findings is a false positive — each maps to a verifiable defect in the pre-fix authoring set.

## Missed findings

- **M-add-1 (Major): AC2's four-discrete-assertion design pins a block that is still a "draft" — the test contract and the block text can drift apart at build time.** design.md "What's new" item 2 labels the block content "Draft:" while design.md "Test design notes → AC2" specifies four discrete asserts keyed to specific facts. The assertions are described conceptually, not as the literal substrings they will match. If the test author and the INSTALL.md author both work from the "draft" independently, the test's anchor substrings may not survive a reword of the block, OR the block may be reworded in a way that still reads correctly to a human but breaks a brittle substring assert — a false-RED at validate. Proposed fix: design.md should declare the block text in item 2 as the *frozen canonical* wording (drop the "Draft:" label) and have the AC2 test assert against named substrings lifted verbatim from that frozen block — the same canonical-phrase discipline B1 applied to the test-function name.

- **M-add-2 (Major): the new install step has no specified placement or identifier within INSTALL.md's Step 3a-3g sequence.** design.md "What's new" item 1 says "a new install step in INSTALL.md — modelled on Step 3d" and ADR-057 §Consequences says "INSTALL.md gains one new ... step" — but neither says *where* it slots. INSTALL.md Step 3 currently has sub-steps 3a (Venv) through 3g (pip package), then Step 4 (Verify). The step needs a deterministic home: (a) AC1's test asserts the step prose contains an append to ~/.claude/CLAUDE.md — if the test greps for an anchor it needs to know the step's identifier; (b) Step 3d already writes to global CLAUDE.md, so two CLAUDE.md-mutating steps should be ordered intentionally; (c) an unnumbered "somewhere in Step 3" instruction invites build-time drift. Proposed fix: design.md should name the exact insertion point and identifier (new sub-step immediately after 3d with a renumber, OR explicitly append as `3h` with a one-line rationale). Step 4 Verify needs no new line (the new step writes to global CLAUDE.md, not an INST-1 inventory item).

## Severity adjustments

No severity adjustments to the first Critic's filed severities. One scope-precision note on the *Builder's B2 fix wording* (not a re-severity of B2):

- **B2 fix-wording scope note (informational):** design.md "What's new" item 6 instructs build to "grep INSTALL.md for *every* stale current-version literal and reword each drift-proof." Verified the actual surface: `v0.54.0` at INSTALL.md:18 is the **only** stale current-version literal. Every other version reference in INSTALL.md references `VERSION` / `ai-sdlc-VERSION` dynamically or speaks generically. The "every … literal" plural is harmless (the grep finds exactly one) but slightly over-broad — it risks a build-time author "fixing" an already-drift-proof line. Not a defect and not a severity change — flagged so TRI-1 can, if desired, tighten item 6 to "the single stale literal at INSTALL.md:18."

## Notes

Confidence is high on the confirmed findings (all six independently verified against INSTALL.md, VERSION, the on-disk ADR-057, and the slice-045 precedent test) and high on M-add-2 (the missing step placement is an objective gap in the recipe). M-add-1 is medium-confidence — a real coupling risk but a disciplined Builder could resolve it implicitly; filed as Major because the design explicitly carries the word "Draft:" while a downstream test is being pinned against it.

On the two adjudication asks: (1) **B2 boundedness** — the Builder's fix is correctly bounded *in effect* (only one literal exists) but loosely *worded*; see the B2 scope note. (2) **Inclusion-heuristic "no bump"** — concur with both the first Critic and the Builder that NO bump is correct, and specifically reject the slice-049-B2 / slice-052 counter-precedent worry: adding a step to INSTALL.md does not cross the methodology-behavior line because the step changes no pipeline skill capability — it seeds a harness-tool-usage guardrail into global CLAUDE.md, mints no RULE-ID, and touches no `/triage`/`/adopt`/`/slice` SKILL.md. slice-045 is the correct precedent class. The MEPD-1(b) discharge-by-name at /build-slice against META-1 `test_methodology_changelog.py:136` remains the correct closing step.

Calibration observation: the first Critic's pattern was sound — two Blockers, two Majors, two verified-clean minors, all correctly severed and severitied, with no over-reach. Its one blind spot is a recipe-completeness gap (M-add-2): it checked the step's idempotency, confirmation gate, and test design but not the step's location in the procedure. M-add-1 is a residual of M2: the first Critic correctly demanded discrete assertions but did not close the loop on freezing the text those assertions bind to. Both are EXTEND-class additions, not corrections — the first Critic's existing findings stand.
