# Critique Review: Slice 083 add-pcr-2b-hard-class-conflict-resolution

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's eight findings are all legitimately grounded — B1, B2, M1–M4, m1–m3 each map to a verifiable defect in the pre-fix design or source. But per the standing lesson "a Critic's own proposed fix is a fresh claim," the meta-Critic re-interrogated the ACCEPTED-FIXED deltas against ground truth, and two do not deliver the property they claim: **the B2/M1 git-native fix has the identical setext-`=======` false-positive it was created to eliminate** (verified empirically — `git diff --cached --check` uses the same ≥7-char marker heuristic), and **the B1 fix relocates the design-calibration contradiction from the skills onto the named subagents without resolving it** (the agents' own system prompts hardwire slice-artifact inputs and a fail-stop-on-missing). M2's escalation-path fix and M4's framing fix are source-confirmed sound.

## Confirmed findings (first Critic — all VALID)

- **B1** (reuse claim unspecified/contradicts skills) — VALID, Blocker appropriate. `skills/critique/SKILL.md:52-55` STOPs on missing design.md; design-folder audits don't exist at merge time. *(Fix challenged — see M-add-2.)*
- **B2** (substring scan false-positives on setext) — VALID, Blocker appropriate. *(Fix challenged — see M-add-1.)*
- **M1** (verify timing vs `git add`) — VALID, Major. `_extract_u_files` (`:488-535`) keys on porcelain U-codes; sourcing from `git diff --name-only --diff-filter=U` correctly addresses the staging half; ordering coherent.
- **M2** (SOFT→HARD escalation untraced) — VALID, Major; **fix source-verified sound**: escalation STOP at `:295-300` carries `conflict_class=exc.conflict_class`; `_merge_shippability:1256-1260` raises `_SoftResolutionError(..., HARD)`; `main()` `--resolve-soft --json` emits `"conflict_class"` at `:1669`. Keying the gate on `action=="STOP" AND conflict_class in {HARD,MIXED}` catches both paths. (Interrogation target (c) confirmed — the field IS surfaced.)
- **M4** (`_index.md` HARD high-frequency) — VALID, Major; DEFERRED disposition sound. ADR-069:17/:19/:21 contradict "low-frequency"; the mislabel was inherited from ADR-069, not invented here.
- **m1, m2, m3** — VALID minor. m2's stale forward-ref is real (`skills/commit-slice/SKILL.md:192` reads "PCR-2b (slice-079) will ship…"); ACCEPTED-PENDING correct.

## Suspicious findings

None. Every original first-Critic finding is grounded — no over-reach at the finding level. The challenges below are to the Builder's *fixes*, surfaced as Missed findings per the "fix-is-a-fresh-claim" lesson.

## Missed findings

### M-add-1 (B2-fix regression): `git diff --cached --check` has the SAME setext-`=======` false-positive the B2 fix claims to cure
- **Evidence**: meta-Critic ran `git diff --cached --check` against a staged Markdown setext H1 (`Title\n=======`) and a `=======` divider — git reports `leftover conflict marker` and exits 2 on every `=`-run of length ≥7 at line start (the identical ≥7-char heuristic rejected for the substring scan). A 4-`=` underline passes; a 7-`=` underline STOPs.
- **Consequence**: HARD U-files are by definition ADR/SKILL.md/changelog markdown (ADR-069:57) — exactly the files containing setext headings and `=======` dividers. A correct hand-resolution that adds/modifies a 7-`=` line false-STOPs. design.md§"B2/M1 fix" asserts "zero false-STOP on legitimate markdown" — unbacked and contradicted by execution.
- **Severity**: **Major** (NOT Blocker) — a false STOP is fail-closed-safe (refuses to continue, never silently continues).
- **Builder draft**: **ACCEPTED-FIXED** — redesign the leftover-marker net to key on the **line-anchored `<<<<<<<` opener / `>>>>>>>` closer** (7-char `<`/`>` runs — no legitimate markdown analog, unlike `=======`/setext), NOT `git diff --cached --check`, NOT `=======`-alone. Primary check stays `git diff --name-only --diff-filter=U` empty. Documented as a conservative fail-closed heuristic (a rare doc with a literal line-start `<<<<<<<` may false-STOP — safe). AC2 test `test_verify_resolution_clean_on_resolved_markdown_setext` asserts a resolved ADR with a setext `=======` heading PASSES (CLEAN). APED-1 battery confirms at build. *(Applied to design.md §"B2/M1 fix" + Contracts.)*

### M-add-2 (B1-fix relocates rather than resolves the contradiction): the named `critique`/`critique-review` subagents are themselves design-calibrated and fail-stop on missing slice artifacts
- **Evidence**: `agents/critique.md` front-matter: "Use ONLY when invoked by the /critique skill — this agent expects slice artifacts as input"; Inputs section: "If any of these are missing or you cannot read them, say so explicitly and stop. Do not invent inputs." Its 9 dimensions (MEPD-1 RULE-ID `:122-124`, TF-1 `:90-93`, PMI-1) are baked into the **system prompt**, not the invoking skill — a user-message preamble does not override them; the agent will look for design.md, find none, and STOP. `agents/critique-review.md` is identical in posture.
- **Consequence**: the B1 fix moved the exact defect it flagged (design-hardwiring) from the skill layer to the agent layer, where it persists. "Reuse the named critique/critique-review agents on a diff" is high-risk / likely unbuildable as written.
- **Severity**: **Major** (bordering Blocker) — but the bootstrap fallback (missing/failing helper → unchanged PSQ-3 SOAD-1 STOP, design.md error model) means a non-functional Critic spawn degrades safely to today's behavior, not to a silent auto-continue; does not breach the fail-closed must-not-defer.
- **Meta-Critic fix options**: (i) author a NEW diff-calibrated agent (honest, expands scope: new agent file + CAD-1 guard + PMI-1/INST-1 inventory); (ii) downgrade to inline Critic-stance review carried by SKILL.md prose (no subagent — tightest scope, loses two-persona separation); (iii) verify empirically at build that the `critique` agent handed a merge-diff prompt with no slice folder produces useful findings (high-risk given the explicit fail-stop clause).
- **Builder draft**: **ACCEPTED-PENDING — requires user direction at TRI-1** (this revisits the user's /design-slice Critic-mechanism choice, now shown likely unbuildable as literally stated). **Builder-recommended 4th option**: use the **`code-review` agent** (`agents/code-review.md`, slice-060) — it is ALREADY diff-calibrated ("9 dimensions reframed for code"), exists, is buildable, and reviews exactly a code/content diff; no new agent file. Trade-off vs the user's /design-slice pick: single adversarial pass (the meta-pass leg is recovered by the TRI-RESOLVE-1 user gate + the standing DR-1 discipline). If the user wants to preserve a true two-pass, option (i) (new dedicated two-pass agent) is the fidelity-preserving but scope-expanding path. ADR-075 Option B + design.md §"B1 fix" updated once the user picks.

## Severity adjustments

None. Original findings filed at defensible severities. Both Missed findings filed Major (M-add-1 fail-closed-safe; M-add-2 degrades safely via bootstrap fallback).

## Notes

High confidence on both Missed findings (M-add-1 empirically reproduced across isolated test repos; M-add-2 read directly from agent front-matter). The first Critic did excellent original work (B2 was a sharp APED-1 catch) but exhibited the exact pattern the standing lesson warns about — it did not re-execute its own proposed git-native fix, shipping a B2 fix that reproduces the diagnosed defect and a B1 fix that relocates the gap. Both are second-order misses on the Builder's ACCEPTED-FIXED deltas — precisely the DR-1 meta-pass's reason to exist. No new contradictions beyond M-add-1/M-add-2; the `--verify-resolution` exit-code mapping is internally coherent. Both findings would likely surface when the honest WRITTEN-FAILING TF-1 tests are authored at build — filed now so TRI-1 can choose the fix direction before the Builder commits to the git-native and named-subagent paths.
