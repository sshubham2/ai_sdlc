# Reflection: Slice 088 add-project-frame-synthesizer

**Date**: 2026-05-31
**Shipped**: YES

## Validated
- **Deterministic tool over LLM skill (ADR-080) was the right call** — `test_frame_regenerates_deterministically` is trivially satisfiable and the synthesis property (`test_frame_trajectory_synthesizes_not_concatenates`) is testable precisely because the tool is deterministic; an LLM `/frame` skill could not have been pinned this way. Judgment of direction-fit stayed with the Critic (Dim-7), not the synthesizer.
- **Ephemeral stdout-only cannot drift** — validated: no tracked file written; regenerated each run; the real-repo smoke and the fixture tests agree.
- **The frame surfaces the parallel-slice family** — the live smoke named `PFS, PCR, DCE, BCSG, PSQ, BRANCH`; the direction-awareness the slice-087 miss lacked is now one Bash call away for `/design-slice` + both Critics.
- **Dogfood**: this slice took ADR-080 (not 079) to avoid colliding with the in-flight slice-087's ADR-079 — a live instance of the exact concurrency-awareness gap PFS-1 closes.

## Corrected
- **cp1252 fix mechanism: `_ascii_fold()` → `_stdout.reconfigure_stdout_utf8()`** (build deviation, user-approved). The dual-Critic (design B1 + meta M-add-1) ratified an ASCII-fold over the whole frame; plan-mode reading the actual code showed UTF8-STDOUT-1 *mandates* `reconfigure_stdout_utf8()` for every tool `main()`, which makes the em-dash crash impossible without transliteration and is what all 20 sibling tools do. The Critics correctly identified the *risk* but prescribed a fix that fought the codebase's established mechanism. Corrected in `design.md` + `methodology-changelog.md` v0.78.0 + `build-log.md`. The code-Critic later **empirically confirmed** reconfigure is necessary AND sufficient.
- **CLAUDE.md:42 OSDG-1 inventory (partial)** — the pre-existing prose claimed `critique`/`diagnose` were OSDG-1-guarded when no `test_*_skill_drift.py` existed for them (slice-086 B2 class, tracked as `reconcile-osdg-1-inventory-claude-md-L42`). This slice makes `critique` true (adds its drift test) and adds `design-slice`/`critique-review`. Residual: `diagnose` still claimed-but-no-test; `code_review`/`pulse` have tests but go unlisted. Updated `CLAUDE.md` for the three I touched; residual flagged below.

## Discovered
- **`_RULE_TITLE_RE` letter-suffix regex collapse (M1, code-Critic)** — a `\b` after `PCR-2b` made the capture collapse to `PCR`, silently dropping letter-suffixed rule-ids from the family scan; `PCR` survived on the real changelog only by luck (`PCR-1` rescued it). Caught ONLY by the code-Critic *executing* the regex against the real changelog corpus. Fixed in-slice. Fresh N+1 instance of the regex-APED-1 / BC-PROJ-13 miss class (now spanning letter-suffix variants).
- **`max_lines <= 0` negative-slice budget breach (M2, code-Critic)** — `--max-lines 0` emitted a near-full frame (negative slice index), defeating the tight-frame must-not-defer. Fixed in-slice (clamp + CLI validation).
- **R-26 registered (open, downgraded-by-design)** — the advisory-frame silent-all-degrade residual (R-7 analogue): a synth that degrades every section still exits 0 and reviews proceed with no trajectory signal. Mitigation = stderr WARN + mid-slice eyeball; inherent to the advisory-never-a-gate contract.

## Deferred
- **`reconcile-osdg-1-inventory-claude-md-L42`** (carried-forward, partially reduced) — fix the residual CLAUDE.md:42 OSDG-1 prose: remove the false `diagnose` claim, add `code_review`/`pulse`. Reason: out of this slice's blast radius (those skills aren't touched here). Lands in: a small cleanup slice or bundled into the next methodology-prose slice.
- **m1/m2/m3 code-Critic minors** — all FIXED in-slice (positive cp1252 assertion, private-API pin test, `_pending_candidates` WARN), so NOT deferred — noted here only because the voluntary-restraint default is to defer; the Builder elected in-slice fix since they harden the just-written code at trivial cost.

## Critic calibration

Per TRI-1, scoring `critique.md` `## Triage` dispositions against reality observed at build/code-review/validate:

- **B1** (cp1252 own-literal crash): **VALIDATED** (risk) — disposition ACCEPTED-FIXED; the code-Critic empirically confirmed the em-dash/arrow reaches stdout and would crash without reconfigure. *Calibration note*: the prescribed fix (ascii-fold) was sound-but-wrong-for-the-codebase; see Missed/Pattern below.
- **B2** (wrong `_ROOT_ONLY_TOOLS` bucket): **VALIDATED** — bespoke required-arg cp1252 test was the correct mechanism; implemented + rollup-parity green.
- **B3** (consumption contract unspecified): **VALIDATED** — the Bash-capture→paste contract was specified and built; structural-pins green.
- **M1–M6** (design-Critic majors): **VALIDATED** — all ACCEPTED-FIXED design corrections held (smoke command, entry-pin convention, OSDG-1 discharge, synthesis-property test, Step-0.5 degraded, BC-PROJ-14 pin spec).
- **M-add-1** (meta-Critic, em-dash extracted text): **VALIDATED** (risk real) — the em-dash IS in extracted changelog/risk text; resolved by reconfigure-stdout (the deviation handles the extracted path identically). Same prescribed-fix calibration note as B1.
- **M-add-2** (meta-Critic, rollup token + em-dash fixture): **VALIDATED** — both obligations met; the bespoke test is non-vacuous (code-Critic confirmed U+2192 survives).
- **m1** (HOME changelog read): **VALIDATED** — fixed to repo-root read.
- **m2** (R-7 silent-degrade): **VALIDATED** — R-26 registered.

**Missed by Critic** (design-Critic + meta-Critic, caught by the code-Critic):
- **M1 letter-suffix regex collapse** — neither design-time Critic could reach it; only executing the regex against the real `-Na` corpus surfaced it.
- **M2 negative-slice budget breach** — only running the tool at budget boundaries surfaced it.
- **cp1252 fix-prescription**: BOTH the design-Critic AND meta-Critic prescribed `_ascii_fold()` without checking the codebase's existing `_stdout.reconfigure_stdout_utf8()` (UTF8-STDOUT-1) mechanism for the flagged risk-class. The risk-flagging was correct; the fix-prescription fought an established codebase convention.

**Pattern**: 3-Critic stack complementarity held cleanly (N+ stable) — design-Critic + meta-Critic caught the design/contract/discharge gaps; the code-Critic caught two correctness/contract defects (M1 regex, M2 budget) that are *structurally unreachable* from design-time review because they only manifest when the regex/tool is EXECUTED. Do NOT collapse the 3-Critic stack. New calibration signal for `/critic-calibrate`: **when a Critic flags an encoding/cp1252/platform risk on a NEW tool, it should check whether the codebase already has a canonical mechanism for that risk-class (here UTF8-STDOUT-1 / `_stdout.py`) before prescribing a novel fix** — both Critic layers prescribed a codebase-inconsistent fix here.

## Lessons for next slice
- **Execute a newly-minted regex/parser against the REAL production corpus including letter-suffix (`-Na`) variants at design time** — BC-PROJ-13 / regex-APED-1 recurs (N+1); the family-scan letter-suffix collapse would have been caught by running the regex on the actual changelog at `/critique`, not just at `/code-review`.
- **Validate any audit-gated count/version pin's fan-out the moment you bump it** — the 0.77→0.78 + 33→34 bump cascaded to 4 stale pins (version-sync test name, INSTALL count, BCR-1 R-20 seed, PTFFD-1 shippability citation) caught only by the full suite. A grep for the old literal across tests + shippability immediately after the bump is cheaper than a full-suite round-trip.
- **A Critic that flags a risk-class should be pointed at the codebase's existing solution for that class before its fix is ratified** (the cp1252 / UTF8-STDOUT-1 prescription miss) — `/critic-calibrate` candidate.
- **The project-frame this slice ships is itself the structural fix for the slice-087 miss** — next direction-touching slice should be designed WITH `$PY -m tools.project_frame_synth` consulted at Step 0.5 (dogfood the new wire).

## Vault updates made (thin vault)
- [[risk-register.md]] — added **R-26** (project-frame silent all-degrade; open, downgraded-by-design)
- [[decisions/ADR-080-project-frame-synthesizer-pfs1.md]] — minted (PFS-1; deterministic tool; ephemeral stdout; reversibility expensive)
- [[methodology-changelog.md]] — v0.78.0 PFS-1 entry (+ OSDG-1-extension discharge line); 5-part PMI-1 bump synced
- [[shippability.md]] — row 93 (added at build per BC-PROJ-9; no duplicate here)
- [[drift-log.md]] — slice-088 CLEAN entry (DCE-1 marker)
- `CLAUDE.md` — OSDG-1 guarded-set prose extended to design-slice/critique/critique-review (partial; residual flagged)
- This slice's [[design.md]] — cp1252 deviation recorded (ascii-fold → reconfigure-stdout)
