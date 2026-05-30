# Slice 086: harden-agent-spawn-skills-await-real-output

**Mode**: Standard
**Estimated work**: 0.5 day (~3–4 AI-hours)
**Risk retired**: R-25 (MEDIUM, score 4) — "Agent-spawning skills don't guard against main-thread fabrication of async-spawned agent output"
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The three agent-spawning skills (`/critique`, `/critique-review`, `/code-review`) instruct the main thread to "write the agent's output to `<file>`", but none warns that the `Agent` tool may return an **asynchronous acknowledgment** ("Async agent launched…") rather than the finished deliverable, and none forbids self-authoring a placeholder while the agent runs. This gap was observed *live* in slice-085: the main thread wrote `critique.md` from its own self-review before the real Critic returned, and the real agent later refuted a fabricated "B2" finding — silently defeating the Builder↔Critic separation those skills exist to provide. This slice migrates the guard from its current stopgap home (a global `~/.claude/CLAUDE.md` directive, not pipeline-enforced) into the in-repo skill contracts where OSDG-1 / structural-pin tests guard it, then removes the now-redundant stopgap.

## Acceptance criteria

1. All three spawn-skills (`skills/critique/SKILL.md`, `skills/critique-review/SKILL.md`, `skills/code-review/SKILL.md`) carry an explicit await-the-real-agent guard at the spawn→write boundary (the Step 2 → Step 3 seam): the `Agent` tool may return an async acknowledgment; the acknowledgment is NOT the deliverable; STOP and wait for the `task-notification`; write the artifact ONLY from the agent's actual returned content; NEVER self-author a placeholder while the agent runs. **The canonical heading literal authored verbatim into all three skills is** `**Await the real agent — never fabricate its output.**` **— the dash is U+2014 EM DASH (NOT hyphen-minus U+002D, NOT en-dash U+2013); this is the single byte-exact source-of-truth string that AC-2's pin test, design.md, and ADR-078 must all match.** (M1/M3)
2. A new structural-pin test asserts the guard's invariant literal is present in all three in-repo `SKILL.md` files and FAILS if any skill loses it; written WRITTEN-FAILING before the edits, PASSING after. **The test pins TWO literals per skill: (a) the canonical heading literal (AC-1), and (b) one unique-to-invocation literal from the operative four-obligation body (e.g. `NEVER self-author a placeholder`) so a heading-only "slogan" with a gutted body cannot pass** — the body literal MUST be verified unique-to-invocation (absent from informative narration) at build time per the slice-075 lesson. (M2) **The assertion is SEAM-SCOPED, not file-global (M-add-1): both literals MUST fall within each skill's Step 2 → Step 3 region (between the "Step 2" and "Step 3" headings), mirroring the SOAD-1 precedent's `_fenced_block_after` section-scoping — a file-global presence check would stay green if the guard were RELOCATED out of the spawn→write seam (into a footer/template section or above Step 2), leaving it inert and silently re-opening R-25 by relocation rather than deletion.**
3. The installed copies of all three skills (`~/.claude/skills/{critique,critique-review,code-review}/SKILL.md`) are updated to match the in-repo edits. **Drift-status reality (Builder-verified against disk, B1/B2):** `code-review` has an in-repo↔installed content-equality drift test (`tests/methodology/test_code_review_skill_drift.py`) which MUST stay green; `critique` and `critique-review` have **NO** such drift test today, so AC-2's new pin test is the sole enforcement of their guard-literal. (There is no `tests/methodology/test_critique_skill_drift.py` — the earlier reference was a phantom citation, now removed.)
4. The global `# Spawned-agent output` section in `~/.claude/CLAUDE.md` (currently L41) is removed as the **closing** step — ONLY after AC-1/AC-2/AC-3 verify the skill-level guard is present and installed — and the stopgap→pipeline migration is recorded in `reflection.md`.
5. `architecture/shippability.md` gains a row pinning the new structural-pin test (per RPCD-1 / SCPD-1) so the guard's presence in all three skills can never silently regress.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Guard present in 3 skills | `grep` each SKILL.md for the guard's invariant literal at the spawn→write seam; read each Step 2/3 boundary to confirm wording (acknowledgment ≠ deliverable / wait for task-notification / no placeholder) |
| 2 | Pin test enforces guard | Run the new test BEFORE edits → FAILS; run AFTER edits → PASSES; `pytest` the new test node. The test pins BOTH the heading literal AND one operative body literal (M2), **seam-scoped to each skill's Step 2 → Step 3 region (M-add-1) — add a fixture that RELOCATES the guard out of the seam and assert the test FAILS, proving placement (not just presence) is enforced**. Build-time APED-1: assert the byte-exact heading literal (U+2014) appears once in each skill's seam region AND the test CANON constant; confirm the body literal is unique-to-invocation (M1/M2). |
| 3 | Drift-clean install | `$PY -m pytest tests/methodology/test_code_review_skill_drift.py` → PASS (the only existing SKILL.md content-equality drift test among the three — B1). Manually confirm `critique` + `critique-review` installed copies updated (no drift test exists for these two; the AC-2 pin test guards their literal). |
| 4 | Stopgap removed last | `grep -c "Spawned-agent output" ~/.claude/CLAUDE.md` → 0, performed only after AC-1/2/3 pass; reflection.md records the migration |
| 5 | Shippability row | `$PY -m tools.shippability_path_audit` (or catalog runner) green with the new row; row Command targets the new pin test |

## Must-not-defer

- [ ] **Ordering is load-bearing**: the global CLAUDE.md stopgap (AC-4) MUST be removed ONLY after the skill-level guard is verified present + installed (AC-1/2/3). Removing it earlier leaves zero protection during the window.
- [ ] OSDG-1 content-equality for the one drift-tested skill (`code-review`, via `test_code_review_skill_drift.py`) MUST be re-verified after edits — do not leave installed/in-repo drift. `critique` + `critique-review` have NO drift test (B1/B2); their installed copies MUST still be manually re-synced after edits so no stale guard ships.
- [ ] The guard MUST carry the same invariant literal across all three skills so the single pin test (AC-2) covers all three uniformly.
- [ ] No regression in the full suite (the changelog/drift/manifest audits and the 1228-test baseline must stay green).
- [ ] RPCD-1 / SCPD-1: the new pin-test consumer reference MUST propagate into `shippability.md` (AC-5) — a new enforcement rule without a catalog row is a violation.

## Out of scope

- Extending **full** OSDG-1 content-equality coverage to `critique-review` (it is NOT currently in the OSDG-1 guarded set; AC-2's structural-pin test covers the specific guard literal in all three skills, which is the R-25 obligation. Full content-equality extension for `critique-review` is a separate R-13-class concern — flag as a follow-up candidate, do not build here).
- Any change to the `Agent`-spawn tooling/mechanics — this slice adds guard PROSE + a presence test, not new orchestration code.
- An automated runtime/agentic test that *simulates* main-thread fabrication — the failure mode is a behavioral/agentic property, not mechanically reproducible (this is why R-25 is enforced by content-presence, not a `tests/bugs/` repro; BFRD-1 `/repro` prelude does not apply).

## Dependencies

- Risk register: [[risk-register#R-25]] — the fix candidate (await-the-real-agent guard, queued slice name `harden-agent-spawn-skills-await-real-output`) is fully specified in the entry.
- Vault refs: `skills/critique/SKILL.md` (Step 2/3), `skills/critique-review/SKILL.md`, `skills/code-review/SKILL.md`; global `~/.claude/CLAUDE.md` `# Spawned-agent output` section (L41, the stopgap to remove).
- Methodology: OSDG-1 / Mini-CAD content-equality discipline (CLAUDE.md Self-hosting discipline §); RPCD-1 / SCPD-1 shippability propagation.

## Mid-slice smoke gate

At ~50% of build (guard added to `critique` + `code-review`, re-installed; pin test written):
```
$PY -m pytest tests/methodology/test_critique_skill_drift.py tests/methodology/test_code_review_skill_drift.py <new-pin-test-node> -q
```
Expected: the two drift tests PASS (install sync intact) and the new pin test PASSES once all three skills carry the guard. If a drift test FAILS → the install copy wasn't synced; STOP and fix before continuing (do NOT remove the CLAUDE.md stopgap yet).

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (especially the AC-4 ordering invariant)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
