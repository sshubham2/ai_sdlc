# Critique: Slice 083 add-pcr-2b-hard-class-conflict-resolution

**Critic reviewed**: mission-brief.md, design.md, ADR-075. Cross-referenced: `tools/parallel_conflict_resolver.py` (full), `skills/commit-slice/SKILL.md` (sub-step 2.5), `skills/critique/SKILL.md`, `skills/critique-review/SKILL.md`, ADR-069, ADR-071.
**Date**: 2026-05-29
**Result** (Critic's own assessment): BLOCKED — final verdict computed at TRI-1 from user-ratified dispositions.

## Summary

Well-scoped slice with a mostly-sound fail-closed posture, but two findings required redesign before build: (B1) the "spawn /critique + /critique-review against the resolved diff" reuse claim collides with how those skills are actually built (hardwired to a slice `design.md`, slice-folder output, design-folder audits); (B2) the `--verify-resolution` substring marker scan false-positives on legitimate markdown (`=======` setext underlines) — APED-1-executed — and would STOP correct HARD resolutions of the ADR/SKILL.md files HARD conflicts are made of. Both, plus all four majors and three minors, were dispositioned ACCEPTED-FIXED (design.md + ADR-075 + mission-brief edits) except m2 (ACCEPTED-PENDING, build-time SKILL.md edit).

## Findings

### Blockers (must address before /build-slice)

#### B1: "Reuse /critique + /critique-review agents against the resolved diff" was unspecified and contradicts how both agents/skills are built
- **Claim under review**: design.md What's-reused + ADR-075 Decision step 4 + AC #2 — "spawn the /critique + /critique-review agents against the resolved merge diff".
- **Issue**: The `/critique` skill STOPs if `design.md` is absent (`skills/critique/SKILL.md:52-55`), pastes `design.md`, writes to slice-folder `critique.md`, and runs `tools.triage_audit` against a slice folder; `/critique-review` writes `critique-review.md` + runs `tools.critique_review_audit`. At `/commit-slice --merge` time (post-`/reflect`, post-archive) there is no slice folder. The named subagents' 9 dimensions are design-calibrated (mission-brief, ACs, TF-1, PMI-1) — none map onto a merge diff. The design specified the invocation only at one-line granularity: no prompt body, no output-capture location, no statement about whether the design-folder audits run.
- **Evidence**: `skills/critique/SKILL.md:52-55,80-97,107,178`; `skills/critique-review/SKILL.md:53,83,92`; the `critique` agent's design-oriented dimensions; ADR-075:48,60.
- **Proposed fix**: pin the mechanism — named subagents (`subagent_type: "critique"` / `"critique-review"`) given a purpose-built merge-resolution-review prompt (dimensions reframed for a diff), output captured inline, design-folder audits NOT run, TRI-RESOLVE-1 replaces TRI-1.
- **Builder draft**: **ACCEPTED-FIXED** — design.md new § "B1 fix — how the Critic stack is actually invoked at merge time" (named subagents reframed for a diff; 6 diff-dimensions; inline output; no slice-folder `critique.md`; `triage_audit`/`critique_review_audit` NOT run). ADR-075 Option B + Decision updated to record "named subagents, not the skills". Honors the /design-slice user choice (the *agents*) while closing the integration gap.

#### B2: `--verify-resolution` substring marker scan false-positives on legitimate markdown (setext `=======`), STOPping correct HARD resolutions
- **Claim under review**: design.md Contracts + ADR-075 Decision step 3 — "no remaining git conflict markers `<<<<<<<` / `=======` / `>>>>>>>` in any U-file".
- **Issue**: APED-1-executed — a bare `=======` substring fires on a Markdown setext H1 underline (`Title\n=======`), on prose with seven `=`, and on any doc that *describes* conflict markers (ADR-069:33, the resolver's own docstrings, this design.md). HARD U-files are by definition markdown/source (ADR-069 HARD row), so the scan would STOP correct resolutions of exactly the file class HARD conflicts comprise. Even line-anchored `^={7}` can't disambiguate setext from a conflict separator.
- **Evidence**: executed battery output (`markdown_hr_setext`, `seven_equals_in_prose`, `diff_fence_in_doc` all matched); git-merge docs (markers are line-start 7-char runs); resolver source contains literal markers in comments.
- **Proposed fix**: use git-native detection — `git diff --name-only --diff-filter=U` (unmerged) + `git diff --cached --check` (git's purpose-built leftover-marker detector); run an APED-1 battery on the repo's markdown corpus at design time.
- **Builder draft**: **ACCEPTED-FIXED** — design.md § "B2/M1 fix": `--verify-resolution` redesigned around `git diff --name-only --diff-filter=U` empty AND `git diff --cached --check` clean; substring scan dropped; build runs the APED-1 markdown-corpus battery and quotes the result in build-log.md.

### Majors (address this slice)

#### M1: `--verify-resolution` timing vs U-file lifecycle (`git add`) unspecified; "stage-resolvable" undefined
- **Issue**: `_extract_u_files` (`tools/parallel_conflict_resolver.py:509-535`) keys on porcelain unmerged codes — once the user `git add`s their resolution, files leave the U-state and the scan checks nothing (false CLEAN). Order (pre/post `git add`) unpinned; "stage-resolvable" had no operationalization.
- **Proposed fix**: pin the order; source the verify set from git state, not the live porcelain-U set; drop/define "stage-resolvable".
- **Builder draft**: **ACCEPTED-FIXED** — folded into the B2/M1 fix: verify runs AFTER `git add` and uses `--diff-filter=U` (empty) + `git diff --cached --check`, which are add-state-aware; "stage-resolvable" removed; order pinned (resolve → `git add` → verify → Critic → TRI-RESOLVE-1 → continue).

#### M2: MIXED atomicity — SOFT→HARD mid-loop escalation path not traced
- **Issue**: `resolve_soft_conflict` can escalate a SOFT-looking shippability conflict to HARD mid-loop via `_SoftResolutionError(..., HARD)` (`~:1256`), returning a bare STOP with `conflict_class=HARD` that does NOT pass through `resolve_hard_conflict`. The Wiring matrix mapped only the upfront dispatch.
- **Proposed fix**: trace both HARD-entry paths; state which class/reason the skill keys on; add a regression test for the escalation path.
- **Builder draft**: **ACCEPTED-FIXED** — design.md § "M2 fix": the skill keys gate-entry on `action=="STOP" AND conflict_class in {HARD,MIXED}` (covers upfront-classify AND mid-loop-escalation uniformly); `resolve_hard_conflict` enriches the upfront STOP; escalation STOP reason is informational. New TF-1 row `test_soft_to_hard_shippability_escalation_enters_gate`.

#### M3: TRI-RESOLVE-1 fail-closed "unanswered/ambiguous → STOP" mechanism unspecified
- **Issue**: a SOAD-1 ask returns an offered option or is interrupted — "ambiguous/unanswered" aren't natural outcomes. How the safe-default and the mid-rebase interrupt/resume contract enforce STOP was unstated (TRI-1 uses `triage_audit`; TRI-RESOLVE-1 is a live gate with no analog).
- **Proposed fix**: specify the option set with explicit safe-default; two-condition apply; interrupt/resume contract.
- **Builder draft**: **ACCEPTED-FIXED** — design.md § "M3 fix": 3-option set (`Apply` | `Re-resolve` | `Abort`); every non-`Apply` + any interrupt/no-selection → STOP-no-continue; `Apply` fires `git rebase --continue` only on explicit selection AND non-blocking Critic verdict (blocking verdict greys `Apply`); abandoned gate leaves rebase in-progress, re-invocation re-enters cleanly per [[ADR-068]] §Re-entry semantics.

#### M4: `_index.md`/`methodology-changelog` HARD-routing is a guaranteed-frequent gate; "low-frequency" framing wrong
- **Issue**: ADR-069:17 — every parallel slice regenerates `_index.md` (HARD because Haiku-regen, ADR-069:72); methodology slices bump the changelog (HARD). So the dominant real HARD conflict is high-frequency, and the two-pass Critic re-introduces the cost ADR-069:37 rejected for blanket-Critic. The "low-frequency" framing understated operational cost; AC #5 battery drove only a generic HARD conflict.
- **Proposed fix**: withdraw the "low-frequency" framing; either add a lighter path for `_index.md`-sole or at least exercise/acknowledge the dominant case.
- **Builder draft**: **ACCEPTED-FIXED** (framing + acknowledgment + exercise) / lighter-path **DEFERRED** — ADR-075 Consequences "M4 fix" withdraws "low-frequency"; design.md § "M4 fix": `_index.md`-sole hand-resolution = "re-run `/archive`" surfaced in the STOP diagnostic; AC #5 battery adds an `_index.md`-sole scenario (`test_index_md_sole_hard_scenario_drives_gate`); lighter-path follow-up queued as `add-index-md-soft-promotion-or-light-hard-path` (out of /slice scope — gate-on-hand-resolve only).

### Minors (log; address if cheap)

#### m1: "annotate not edit" contradiction + cross-file slice-077/079/PCR-2 inconsistency
- **Builder draft**: **ACCEPTED-FIXED** — ADR-075 reworded: ADR-069 left byte-unchanged; ADR-075 supersedes-via-refinement the HARD/MIXED resolution-path cell; readers follow the forward link. (Cross-file `slice-079`/`PCR-2` inconsistency handled under m2.)

#### m2: SKILL.md:192 carries stale "PCR-2b (slice-079)" forward-reference this slice must update
- **Builder draft**: **ACCEPTED-PENDING** — applied at `/build-slice`: the same edit block updates `skills/commit-slice/SKILL.md:185-192` "(slice-079) will ship" → shipped-status + resolver docstring `:16-18`; design.md Components-touched records the pre-sign-off grep sweep (`slice-079` / `PCR-2\b`).

#### m3: TF-1 plan AC-coverage gap — AC #1 (entry-pin) + AC #3 (SOAD-form prose pin) had no rows
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief TF-1 plan gains AC #1 entry-pin row (`test_v_0_77_0_pcr_2b_tri_resolve_1_entry_present_in_repo`) + AC #3 SKILL.md-prose SOAD-form pin (`test_tri_resolve_1_soad1_structured_options_form_pinned`, unique-to-invocation per the slice-075 lesson) + the M2 escalation, setext, and `_index.md`-sole rows (TPHD-1 harmonized in the same fix block).

## Dimensions checked
- [x] Unfounded assumptions — M4 (HARD "low-frequency" contradicted by ADR-069:17); B1 (unbacked reuse claim).
- [x] Missing edge cases — M1 (U-file lifecycle vs `git add`); M2 (SOFT→HARD escalation); B2 (markdown setext / prose markers, APED-1-executed).
- [x] Over-engineering — none (tightly scoped; mirrors VAULT_CLAIM shape; auto-propose explicitly rejected).
- [x] Under-engineering — B1 (Critic-stack integration); M3 (TRI-RESOLVE-1 mechanism); m3 (TF-1 rows).
- [x] Contract gaps — M1 (verify file-set source + "stage-resolvable"); M3 (interrupt contract).
- [x] Security — none beyond inherited cooperative model; TRI-RESOLVE-1 (user) is apply authority; no-silent-auto-continue covered in M3.
- [x] Drift from vault — m1 ("annotate not edit" + cross-file naming); m2 (stale `slice-079` ref). `resolve_hard_conflict` mirrors real `resolve_vault_claim_conflict:1048`.
- [x] Web-known issues — n/a (no external tech; git conflict-marker presentation addressed via git-merge docs in B2).
- [x] Cross-cutting conformance — B2 (APED-1-executed); M2 (algorithm-path conformance with `_SoftResolutionError(HARD)`); m2 (FBCD-1 cross-file); m3 (TF-1 coverage). RSAD-1: slice is exercisable on its own `/commit-slice --merge` (self-validating parallel-family lesson).

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

Reconciled across both passes (first Critic + meta-Critic DR-1). User ratified all Builder draft dispositions (2026-05-29) and selected the M-add-2 fix direction: **use the `code-review` agent** (diff-calibrated, single pass) — the named `critique`/`critique-review` agents were rejected for fail-stopping on missing slice artifacts.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §"B1 + M-add-2 fix" — Critic mechanism is the `code-review` agent (see M-add-2); inline output, no design-folder audits |
| B2 | Blocker | ACCEPTED-FIXED | superseded by M-add-1's better fix — see M-add-1 |
| M1 | Major | ACCEPTED-FIXED | folded into M-add-1 fix — `--diff-filter=U`, add-state-aware, order pinned, "stage-resolvable" dropped |
| M2 | Major | ACCEPTED-FIXED | design.md §"M2 fix" — skill keys gate on returned class (both entry paths); meta-Critic source-verified `conflict_class` is surfaced; escalation test row added |
| M3 | Major | ACCEPTED-FIXED | design.md §"M3 fix" — option set + safe-default + two-condition apply + interrupt/resume contract |
| M4 | Major | ACCEPTED-FIXED | ADR-075/design.md §"M4 fix" — "low-frequency" framing withdrawn, `_index.md`-sole battery scenario; lighter-path queued (DEFERRED follow-up) |
| m1 | Minor | ACCEPTED-FIXED | ADR-075 refinement reworded — ADR-069 left byte-unchanged; forward link |
| m2 | Minor | ACCEPTED-PENDING | build-time SKILL.md `:185-192` + resolver docstring `:16-18` forward-ref update + grep sweep |
| m3 | Minor | ACCEPTED-FIXED | mission-brief TF-1 rows added (AC #1 entry-pin, AC #3 SOAD-form pin, M2 escalation, setext, `_index.md`-sole) |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) design.md §"B2/M1/M-add-1 fix" — verify keys on line-anchored `<<<<<<<`/`>>>>>>>` openers (no markdown analog), NOT `git diff --cached --check`, NOT `=======`; conservative fail-closed; APED-1 at build |
| M-add-2 | Major | ACCEPTED-PENDING | (meta-Critic) user picked **`code-review` agent** (diff-calibrated, single pass; named critique agents fail-stop on missing slice artifacts). ADR-075 Option B + design.md §"B1 + M-add-2 fix" updated; wired into SKILL.md at /build-slice |
