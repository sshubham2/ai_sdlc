# Reflection: Slice 083 add-pcr-2b-hard-class-conflict-resolution

**Date**: 2026-05-30
**Shipped**: YES

PCR-2b closes the last two open conflict-classes (HARD + MIXED) in the PCR-N parallel-conflict-resolution taxonomy that PCR-1 (slice-076) and PCR-2a (slice-078) reserved. HARD/MIXED now route through a gate-on-hand-resolve flow (hand-resolve → `--verify-resolution` → `code-review` agent → TRI-RESOLVE-1 user gate → `git rebase --continue`) instead of a bare SOAD-1 STOP. Two new RULE-IDs (PCR-2b + TRI-RESOLVE-1); ADR-075.

## Validated
- HARD/MIXED never auto-merge — `resolve_hard_conflict` returns STOP, rebase left in-progress — validated by `test_pcr_2b_hard_conflict_dispatch.py` on real tmp-repo rebase conflicts.
- `_verify_resolution_clean` keys on `<<<<<<<`/`>>>>>>>`/`|||||||` openers, NOT `=======` — a resolved ADR retaining a setext `=======` heading verifies CLEAN — validated by `test_pcr_2b_verify_resolution.py::test_verify_resolution_clean_on_resolved_markdown_setext`.
- MIXED atomicity (no partial SOFT auto-resolve) — validated by `test_pcr_2b_mixed_routes_to_hard.py`.
- SOFT→HARD shippability escalation surfaces `conflict_class=HARD` for the skill's class-keyed gate-entry (M2) — validated by `test_soft_to_hard_shippability_escalation_enters_gate`.
- 5-part PMI-1 bump 0.76.0→0.77.0 + forward-syncs — validated by MCFS-1/AVFS-1/TVFS-1 PASS + `test_version_files_synchronized_at_v_0_77_0`.
- No regression — shippability catalog 88/88 PASS; full suite 1192.

## Corrected
- The /design-slice-ratified Critic mechanism ("reuse the `critique`+`critique-review` agents on the diff") was CORRECTED at TRI-1 (M-add-2) to the `code-review` agent — the named critique agents are design-calibrated and fail-stop on a missing slice `design.md`. Recorded in ADR-075 Option B (the design choice → the buildable choice). No prior-slice ADR superseded (ADR-075 refines ADR-069 without editing it).
- The first-round B2 "fix" (`git diff --cached --check`) was CORRECTED at the meta-pass (M-add-1) to the `<<<<<<<`/`>>>>>>>` opener scan — `--check` inherits the same `≥7-=` setext false-positive. Then CORRECTED again at /code-review (M2) to add `{7,}` + the diff3 `|||||||` base marker.

## Discovered
- **diff3/zdiff3 base markers (`|||||||`) are a distinct unresolved-marker class** a `<<<<<<<`/`>>>>>>>`-only scan misses (code-review M2). Low-frequency (default `merge.conflictStyle=merge` doesn't emit them) but a real fail-open-in-reverse safety gap; now covered. No risk-register entry — closed in-slice.
- **The dominant real HARD conflict (`architecture/slices/_index.md`-sole) is HIGH-frequency, not low** (code-Critic M4 / ADR-069:17) — every parallel merge regenerates it (Haiku-dispatched, never SOFT). Routing it through the full gate re-introduces the latency ADR-069:37 flagged for blanket-Critic. Lighter-path follow-up queued (`add-index-md-soft-promotion-or-light-hard-path`).
- No new risk-register entries. R-23 (clock-skew) + R-24 (truncated-baseline) stay OPEN — PCR-2b is their remediation *venue* (the `code-review` agent CAN flag unexpected orderings/baseline-shrink), not their closer; no dedicated detection shipped (out of /slice scope).

## Deferred
- R-23 / R-24 dedicated detection hooks — reason: out of /slice scope (gate-on-hand-resolve only) — lands in: their own SMALL queue candidates (`add-claim-sequence-number-for-clock-skew-detection`, `harden-pcr-2a-clock-skew-winner`).
- Lighter `_index.md`-sole HARD path (deterministic regen or Critic-skip) — reason: out of scope; M4 deferral — lands in: queued `add-index-md-soft-promotion-or-light-hard-path`.
- True two-pass meta-Critic on HARD resolutions — reason: single-pass `code-review` agent chosen at TRI-1 for buildability; the TRI-RESOLVE-1 user gate is the backstop — lands in: a new dedicated diff-calibrated agent IF single-pass proves insufficient (ADR-075 Option B-3, not chosen).

## Critic calibration

Per TRI-1, scored against `critique.md` → `## Triage` + `critique-review.md` + `code-review.md` + reality observed during build/validate:

**Design-Critic (`/critique`)** — 2B/4M/3m, all VALIDATED:
- B1 (reuse-claim unspecified): VALIDATED — real integration gap; the /critique skill IS hardwired to a slice design.md.
- B2 (substring marker scan false-positives on setext): VALIDATED — APED-1-executed; the defect was real (and the first proposed fix reproduced it — see meta).
- M1 (verify timing vs `git add`): VALIDATED — `_extract_u_files` does go empty post-add; folded into the git-native fix.
- M2 (SOFT→HARD escalation untraced): VALIDATED — meta-Critic source-confirmed the `conflict_class` field is surfaced; the class-keyed gate-entry covers both paths.
- M3 (TRI-RESOLVE-1 fail-closed mechanism unspecified): VALIDATED — pinned operationally (option set + safe-default + two-condition apply).
- M4 (`_index.md` high-frequency framing): VALIDATED — code-Critic independently re-confirmed; framing withdrawn + lighter-path queued.
- m1/m2/m3: VALIDATED (annotate-not-edit reworded; cross-file naming; TF-1 rows added).

**Meta-Critic (`/critique-review`)** — EXTEND, 2 MISSED, both VALIDATED and LOAD-BEARING:
- M-add-1 (B2-fix reproduced the setext defect): VALIDATED — without it I'd have shipped `git diff --cached --check` which empirically false-STOPs on setext.
- M-add-2 (B1-fix relocated the contradiction to the agent layer): VALIDATED — the named agents' front-matter does demand slice artifacts; the diff-review would have fail-stopped.

**Code-Critic (`/code-review`)** — 0B/2M/4m; M1/M2/m1/m2/m3 VALIDATED, m4 correct-ACKNOWLEDGE:
- M2 (diff3 `|||||||` base marker + `{7}`-exact): VALIDATED — a real safety false-negative the design+meta stack structurally could NOT reach (it's a runtime regex-execution property, found by executing the regex against an adversarial battery). This is the clearest N+1 evidence this slice that the code-Critic is not redundant with the design stack.
- M1 (verify exit-1 contract unconsumed): VALIDATED — the SKILL.md step-4 prose did key only on `action`, never exit code.
- m1/m2 (ADR self-contradiction + stale `=======`): VALIDATED — real authoring drift.
- m3 (committed-marker-context unpinned): VALIDATED — pinned.
- m4 (classify recompute): correct ACKNOWLEDGE — the code-Critic itself concluded "no fix needed"; a true-negative, not a false-alarm.

**Missed by Critic**: nothing reached a shipped state un-caught. One issue self-introduced-then-caught: the code-Critic's M2 fix (which I applied) put a `\|` in a non-raw docstring → `SyntaxWarning`, caught by the pytest run (not by any Critic). This is the "a fix is a fresh claim" pattern firing a THIRD time this slice (after M-add-1 + M-add-2).

**Pattern**:
1. **3-Critic stack complementarity, strongest single-slice evidence yet**: design-Critic (B2 design-level setext) → meta-Critic (M-add-1 the design-fix reproduced it; M-add-2 the other design-fix was unbuildable) → code-Critic (M2 a runtime regex false-negative none of the above could reach). Each persona caught a DISTINCT class the others structurally could not. Do NOT collapse the stack.
2. **"A Critic's own fix is a fresh claim" fired N=3 in ONE slice** (M-add-1, M-add-2, the docstring SyntaxWarning). Strongest /critic-calibrate signal to date for re-interrogating Builder fix-deltas.
3. **New-parser-parity / regex-APED-1 now N=3** (slice-081 anchored matcher, slice-082 heading regex, slice-083 marker regex) — every instance caught ONLY by executing the regex against an adversarial corpus, never by reading the design. Build-check promotion candidate at N=3.

## Lessons for next slice
- When a slice mints a marker/parser regex, write an APED-1 adversarial corpus battery (real markdown/source fixtures incl. the false-positive AND false-negative directions) AT design time — the design-Critic + meta-Critic structurally cannot catch content-shape regex bugs; only executing the regex does. N=3 (slice-081/082/083).
- Re-interrogate EVERY Builder fix-delta (design fixes at the meta-pass; code fixes at /code-review; and watch the full-suite run for fix-introduced regressions). "A Critic's own fix is a fresh claim" fired 3× this slice.
- The dominant real HARD conflict (`_index.md`-sole) is high-frequency — the lighter-path follow-up is the highest-value PCR-N continuation.
- Self-validating-slice property N=4 on the parallel-slice family (slice-077/078/082/083) — codification candidate ("parallel-family slices dogfood their own `/commit-slice --merge`").

## Vault updates made (thin vault — small list)
- [[methodology-changelog.md]] — v0.77.0 entry (PCR-2b + TRI-RESOLVE-1); forward-synced installed.
- [[decisions/ADR-075-mint-pcr-2b-hard-class-conflict-resolution]] — new ADR (mints both rules; refines ADR-069; M-add-2 + code-review m1/m2 fixes applied).
- [[architecture/shippability.md]] — row #89 (+ row #75 citation fix from the version-sync rename fan-out).
- [[architecture/slice-queue.md]] — `add-index-md-soft-promotion-or-light-hard-path` candidate (M4 deferral).
- [[architecture/drift-log.md]] — slice-083 audit entry (DCE-1 marker).
- VERSION / plugin.yaml / pyproject.toml → 0.77.0; installed `~/.claude/ai-sdlc-VERSION` + venv `ai-sdlc-tools` → 0.77.0.
- No ADR superseded; R-23/R-24 unchanged (stay OPEN); no `diagnose-out/backlog.md` round-trip (no `**Closes:** SC-` sentinel).
