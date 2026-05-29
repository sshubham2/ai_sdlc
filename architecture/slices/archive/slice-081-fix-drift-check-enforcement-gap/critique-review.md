# Critique Review: Slice 081 fix-drift-check-enforcement-gap

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-29
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is largely sound and well-calibrated — B1, B2, M2, M3, m2, m3 are all VALID and the Builder's applied fixes mostly resolve them. But M1 was filed on a false premise (the Builder correctly rebutted it), and — more importantly — both Critics missed a genuine **false-ACCEPT** surface: the tolerant marker regex `slice[- ]?0*<N>\b` is specified with **no anchor to the `**Trigger**` line**, while drift-log.md routinely cross-mentions other slice numbers in Scope/Notes/heading lines. M2 hunted the was-it-marked-vs-run direction and missed this opposite-direction defeat of the gate.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (marker-token `slice-NNN` vs producer `sliceNN`) — confirmed; Blocker appropriate. Verified `skills/drift-check/SKILL.md:114` emits `<... sliceNN pre-finish gate>` (no dash); the 13 historical entries use the dash form by habit, not contract. False-refuse surface is real. The Builder's tolerant regex (matches `slice-081`/`slice81`/`slice 81`, rejects `slice-0810`/`slice-081x`/`slice-810`/`slice-018`) plus producer canonicalization correctly resolves it.
- **B2** (Step 7b `drift-check-skip:` preservation undelivered) — confirmed; Blocker appropriate. Verified `skills/build-slice/SKILL.md:494` preserves only `critique-review-skip:`; `~/.claude/templates/milestone.md` shows only `critique-review-skip:`. Identical clobber-then-false-refuse lifecycle to CRP-1. New AC4 + the design B2 bullet correctly scope the fix.
- **M2** (LLM-authored producer; `--fast` writes nothing; was-it-marked not was-it-run) — confirmed; Major appropriate. The honest reframe + full-mode pin + residual-gap disclosure (mirroring NAW-1) is the right disposition. (But see Missed M-add-1 — M2 did not exhaust the marker-reliability dimension.)
- **M3** (collapsed multi-leg bump + omitted entry-pin) — confirmed; Major appropriate. VERSION is 0.75.0; the 4-part bump + `test_v_0_76_0_dce_1_*` entry-pin restructure into AC5 is correct, and the AC-count>5 justification follows slice-067/072 precedent.
- **m2** (PTFFD-1 miscitation) — confirmed; Minor appropriate. ADR-037/STP-1/BCI-1 is the correct fail-visible lineage; design corrected.
- **m3** (ADR "no pre-commit hook" framing risks reopening out-of-scope) — confirmed; Minor appropriate. ADR-073 now carries the explicit out-of-scope clause.

## Suspicious findings

First-Critic findings the meta-Critic challenges (SUSPICIOUS — likely false positive):

- **M1** (design names nonexistent `tools/crp_audit.py`) — **SUSPICIOUS / FALSE-POSITIVE on its filed premise.** Verified independently: `crp_audit.py` appears nowhere in the slice folder or design.md; design.md§What's-reused has always cited the real path `tools/critique_review_prerequisite_audit.py`. The first Critic fabricated the nonexistent-filename premise (a hallucinated specific). **However**, the Builder's salvage is correct: the *residue* (enumerate the byte-faithful literals — em-dash `_SKIP_VALUE_RE`, `_frontmatter_*` helpers, `_resolve_mode` ladder + VAULT_ROOT routing, exit mapping — plus a `grep -n` byte-faithfulness check) is genuinely valuable and confirmed against the live `tools/critique_review_prerequisite_audit.py:69,120-173,341-346`. **Disposition: keep the adopted residue (load-bearing for the build), but the finding as a Major-on-stated-premise was over-reach.** See Severity adjustments.

## Missed findings

Concerns the first Critic didn't flag but the meta-Critic surfaces from independent re-review:

- **M-add-1 (MAJOR): marker regex is unanchored to the `**Trigger**` line — false-ACCEPT via cross-slice mention.** design.md§Contracts narrates the match as "drift-log.md entry whose **Trigger** line matches current slice," but the *specified regex* is the bare `slice[- ]?0*<N>\b` with no `**Trigger**`-line anchor. drift-log.md is append-only and routinely cross-references OTHER slice numbers in `**Scope**`, Notes, Resolutions, and `## Audit (slice-NNN …)` heading lines — **29 non-Trigger lines** carry `slice-0NN` tokens. Consequence: a future slice-NNN whose number was merely *mentioned* by a prior slice's entry (e.g. "deferred to slice-NNN") would be **false-ACCEPTED** — DCE-1 exits 0 though slice-NNN never ran drift-check. This is the **opposite failure direction from M2** and strictly worse: it silently defeats the gate for the affected slice, reopening the very R-7/slice-022 silent-disable class the slice exists to close. **Proposed fix**: anchor the audit match to lines beginning `**Trigger**:` (mirror CRP-1's keyed-frontmatter discipline — keys on the *frontmatter key*, not a body substring scan, precisely to kill this BRANCH-1-style narrative-prose false-positive class per ADR-024). Add an APED-1 fixture: a drift-log with slice-NNN in a prior entry's Notes but NO slice-NNN `**Trigger**` line must exit 1, not 0.

- **m-add-1 (MINOR): bootstrap self-application is ordering-fragile and undertested for the heading-vs-Trigger case.** design.md§Bootstrap requires slice-081's /drift-check to write its `**Trigger**: slice-081` entry before the audit runs. Combined with M-add-1: if the slice-081 entry is written with the slice token only in the `## Audit (slice-081 …)` heading and not a `**Trigger**:` line, an anchored audit would refuse slice-081's own bootstrap. The bootstrap shape is correct (CRP-1/PCA-1/NAW-1 precedent) but the interaction with M-add-1's anchor fix needs an explicit APED-1 assertion that slice-081's actual written entry exits 0 under the anchored matcher.

## Severity adjustments

Findings that are real but mis-filed (SEVERITY-WRONG):

- **M1** — **SEVERITY-WRONG: filed as Major on a false premise; correct severity is Minor (at most).** The actionable content is "enumerate the verbatim literals + add a byte-faithfulness check" — a precision/cross-cutting-conformance nicety, not a Major design defect. The nonexistent-file premise inflated it. Recommend re-grading to Minor in TRI-1 reconciliation; the residue is retained regardless.

## Notes

Confidence high — M-add-1 is verified against the live `architecture/drift-log.md` (29 cross-mention lines) and the live CRP-1 template, which documents the keyed-not-substring discipline (ADR-024) that M-add-1 says DCE-1 should inherit but the design's specified regex does not. Calibration observation: the first Critic's producer-side coverage was thorough on one direction (M2: full-vs-fast) but blind to the symmetric false-ACCEPT direction; the same `**Trigger**`-line evidence cited for B1 contained the cross-mention surface missed for M-add-1 — flag to /critic-calibrate if it recurs. The M1 false-premise (hallucinated filename) is the one calibration concern: it inflated a Minor to a Major. One reservation: M-add-1's Major severity assumes DCE-1 greps the whole file; if the implemented matcher anchors to `**Trigger**:` lines (which the design narrates but the regex does not specify), M-add-1 collapses to a documentation-tightening Minor — the Builder should confirm the implemented matcher anchors and ship the negative fixture either way.
