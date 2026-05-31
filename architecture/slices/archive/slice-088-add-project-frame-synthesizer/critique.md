# Critique: Slice 088 add-project-frame-synthesizer

**Critic reviewed**: mission-brief.md, design.md, ADR-080
**Date**: 2026-05-31
**Result**: NEEDS-FIXES

## Summary

Well-scoped slice; the OSDG-1 self-correction was verified-correct on disk and the MEPD-1 rule-path disposition is sound. The Critic found a build-blocking consumption-contract gap, a Windows cp1252 stdout crash on the tool's hot path, a wrong cp1252-test bucket, a smoke command that violates the CLI contract, a phantom entry-pin convention, and several under-specified surfaces. All 11 findings are VALID (the Critic read literals on disk, not just reasoned). No false alarms. All addressed at design except m2 (risk-register entry deferred to build).

## Findings

### Blockers (must address before /build-slice)

#### B1: ATTACK-LENS preamble + truncation marker emit non-ASCII to cp1252 stdout — UnicodeEncodeError on the hot path
- **Claim under review**: design.md — frame's first line `⚔ ATTACK-LENS — …`; truncation marker `… (frame truncated to budget)`.
- **Issue**: `⚔` (U+2694), `…` (U+2026), `—` (U+2014) printed to stdout crash with `UnicodeEncodeError` on Windows cp1252. stdout is this tool's PRIMARY output — hot path, not an error branch. This is the exact class `test_utf8_stdout_regression.py` exists to catch.
- **Evidence**: `tests/methodology/test_utf8_stdout_regression.py`; `~/.claude/CLAUDE.md` Windows-Python rule.
- **Proposed fix**: ASCII-only emitted preamble/marker (`ATTACK-LENS -- …`, `... (frame truncated to budget)`); pin a cp1252 regression test.
- **Builder draft**: ACCEPTED-FIXED — design.md §Components (`project_frame_synth`) now mandates ASCII-only emitted output (`--`/`...`/`->`), B1 fix noted; cp1252 test added (see B2). ADR-080 prose `⚔` is fine (markdown, not emitted).

#### B2: BC-PROJ-9 surface-2 (`_ROOT_ONLY_TOOLS`) is the wrong bucket — required `--slice-dir` would exit 2 before the render path
- **Claim under review**: design.md §BC-PROJ-9 surface (2) — add to `_ROOT_ONLY_TOOLS`.
- **Issue**: `_root_only_argv` passes no required arg; `project_frame_synth` requires `--slice-dir` → exit 2 (usage), never reaching the stdout-render path the cp1252 test means to exercise. Inventory-pin would pass on wrong-bucket membership while cp1252 coverage is silently absent. Compounds B1.
- **Evidence**: `tests/methodology/test_utf8_stdout_regression.py` `_ROOT_ONLY_TOOLS` + `_root_only_argv`; the existing `test_install_audit_survives_cp1252` / `test_slice_queue_claim_survives_cp1252` carve-outs for required-arg tools.
- **Proposed fix**: bespoke `test_project_frame_synth_survives_cp1252_with_u2192` invoking with real `--repo-root/--slice-dir`; update the BC-PROJ-9 surface-2 row.
- **Builder draft**: ACCEPTED-FIXED — design.md §BC-PROJ-9 surface (2) rewritten to a bespoke cp1252 test, NOT `_ROOT_ONLY_TOOLS`; TF-1 row added.

#### B3: Consumption contract (who runs synth, how stdout is captured into the agent prompt) unspecified — build gap
- **Claim under review**: design.md — "Step 1 Inputs + Step 2 agent-prompt body gain a `# project-frame.md` block"; AC #3.
- **Issue**: `/critique` Step 2 builds the agent prompt by pasting file contents; the frame is stdout-only (no file). The mechanic (skill runs synth via Bash, captures stdout, pastes under which block, which `--slice-dir`, what defensive wrapper) was hand-waved — the Builder cannot write Step-2 prose deterministically and the structural-pin (B4/M6) has no literal to pin.
- **Evidence**: `skills/critique/SKILL.md:69-110`; AC #3.
- **Proposed fix**: specify orchestration (Bash capture → verbatim paste under `# project-frame.md` → `(project-frame unavailable)` on non-zero/empty) for all three consumers.
- **Builder draft**: ACCEPTED-FIXED — new design.md §"Consumption contract (B3) + structural-pin spec (M6)" specifies the Bash-capture-and-paste mechanic for design-slice Step 0.5, critique Step 2, critique-review Step 2, with the defensive fallback.

### Majors (address this slice)

#### M1: Mid-slice smoke command contradicts the CLI contract — would exit 2, not emit a frame
- **Issue**: mission-brief smoke ran `--repo-root .` with no `--slice-dir`; design makes `--slice-dir` required (missing = exit 2). Gate unrunnable as authored.
- **Proposed fix**: add `--slice-dir architecture/slices/slice-088-…`.
- **Builder draft**: ACCEPTED-FIXED — mission-brief.md:75 now passes `--slice-dir architecture/slices/slice-088-add-project-frame-synthesizer`.

#### M2: Phantom entry-pin function-name convention
- **Issue**: design cited `test_v_0_NN_0_pfs1_entry_present_in_repo_and_installed`; the real convention (66 siblings) is `_entry_present_in_repo`. `NN` also left unresolved.
- **Proposed fix**: `test_v_0_78_0_pfs1_entry_present_in_repo`; assert the META-1 `Rule reference` literal.
- **Builder draft**: ACCEPTED-FIXED — design.md §MEPD-1 corrected to `test_v_0_78_0_pfs1_entry_present_in_repo`, version pinned 0.78.0, META-1 `Rule reference` obligation noted; TF-1 entry-pin row added.

#### M3: OSDG-1 guarded-set extension is itself a methodology-surface change — changelog discharge + CLAUDE.md guard
- **Issue**: (a) extending OSDG-1 membership by 3 skills is a rule-scope change that must be discharged (fold into PFS-1 entry or document why). (b) root `CLAUDE.md` OSDG-1 prose is edited but unguarded — slice-086 B2 class (contradicted membership claim shipping).
- **Proposed fix**: (a) explicit OSDG-1-extension line in the PFS-1 v0.78.0 entry; (b) add CLAUDE.md to edited surfaces + state enforcement.
- **Builder draft**: ACCEPTED-FIXED — design.md §MEPD-1 now requires the OSDG-1-extension line in the v0.78.0 entry (M3a); design.md OSDG-1 bullet adds CLAUDE.md as a tracked surface with the 3 drift tests + inventory as load-bearing artifacts and the prose forward-synced as a must-not-defer (M3b).

#### M4: "Synthesis not concatenation" from a deterministic extractor asserted but not operationalized
- **Issue**: AC #1 demands both determinism AND synthesis; only the 40-line cap + a human eyeball guarded against degrading to a tight concatenation (low-signal frame undermines the slice). Acknowledged in ADR-080 Cons but not mitigated with a test.
- **Proposed fix**: add a behavioral test pinning a synthesis property a concat fails (rule-FAMILY dedup, score-sorted risks, named candidates), and/or reword AC #1.
- **Builder draft**: ACCEPTED-FIXED — BOTH: AC #1 reworded to precise "selective extraction + dedup + score-ranking under a hard budget"; new TF-1 row `test_frame_trajectory_synthesizes_not_concatenates` pins rule-FAMILY dedup + score-shown risks + named candidates.

#### M5: Step 0.5 chicken-and-egg — Impact reads design.md, which doesn't exist at design-time
- **Issue**: at `/design-slice` Step 0.5, the slice's `design.md` isn't written yet; Impact reads it → degraded WARN on every design-time run, undocumented. The Step-7 "re-synth against design.md" claim has no consumer/test (AC with no design element).
- **Proposed fix**: state Impact is expected-degraded (mission-brief-only) at Step 0.5; drop or specify Step-7 re-synth.
- **Builder draft**: ACCEPTED-FIXED — design.md §What's-new (design-slice) + AC #2 state the expected-degraded Step-0.5 behavior; the Step-7 re-synth claim is DROPPED (no consumer/test). Impact = mission-brief at design-time, brief+design whenever both exist.

#### M6: Structural-pin tests — BC-PROJ-14 compliance unspecified, blocked on B3
- **Issue**: the 3 pins specified no unique literal, no seam, no shape — risk pinning a non-unique `project-frame` substring via bare `.find()`.
- **Proposed fix**: per-pin unique literal + heading-scoped line-anchored seam + shape assertion.
- **Builder draft**: ACCEPTED-FIXED — design.md §"Consumption contract + structural-pin spec" table gives each pin its unique literal (`# project-frame.md` block header / invocation literal), heading-anchored seam (`(?m)^### Step 0\.5\b`, `(?m)^### Step 2:`), and shape assertion; no bare `.find()`.

### Minors (log; address if cheap)

#### m1: changelog truth-source was a HOME-path read — un-fixturable for the deterministic test
- **Issue**: reading `~/.claude/methodology-changelog.md` makes Trajectory machine-dependent; the deterministic test needs a fixture under `--repo-root`.
- **Proposed fix**: read the in-repo `methodology-changelog.md` under `--repo-root`.
- **Builder draft**: ACCEPTED-FIXED — design.md §What's-reused now reads the in-repo repo-root changelog, not the HOME install copy.

#### m2: R-7-class silent-degrade risk should be registered
- **Issue**: a synth that silently degrades every section still exits 0; the review proceeds with an empty frame (R-7 silent-disable analogue for an advisory input).
- **Proposed fix**: register a risk-register entry; mitigation = stderr WARN visibility + mid-slice eyeball.
- **Builder draft**: ACCEPTED-PENDING — register the risk-register entry during `/build-slice` (with the stderr-WARN + mid-slice-eyeball mitigation); cheap, no design change needed now.

## Dimensions checked

- [x] Unfounded assumptions — M2 (phantom entry-pin convention), M4 (synthesis claim), m1 (HOME-path read). OSDG-1 non-membership self-correction VERIFIED on disk — correct.
- [x] Missing edge cases — M5 (Step 0.5 design.md-absent), m2 (all-sources-degrade silent path). Parallel-slice dogfood (ADR-080 not 079) — correct.
- [x] Over-engineering — none (single-purpose, ephemeral, no speculative interface; tool-over-skill justified in ADR-080).
- [x] Under-engineering — M3b (CLAUDE.md edit unguarded), M5 (Step-7 AC with no design element), M6 (pin shape unspecified).
- [x] Contract gaps — B3 (consumption mechanic), M1 (smoke vs required-`--slice-dir`). CLI exit-code contract otherwise complete.
- [x] Security — none (read-only local, stdout-only, no auth/network/writes/PII).
- [x] Drift from vault — M3 (OSDG-1-scope-change discharge), M2 (changelog convention). MEPD-1 rule-path + 5-part PMI-1 bump verified accurate; ADR-080 append-only/supersedes-nothing — clean.
- [x] Web-known issues — none (no external API/SDK; pure local stdlib). WebSearch not run.
- [x] Cross-cutting conformance — B1 (cp1252/Windows-Python — literals inspected, WILL crash), B2 (`_ROOT_ONLY_TOOLS` bucket wrong for required-arg tool), M1/M2 (FBCD-1/PTFFD-1), M6 (BC-PROJ-14 pin precision).

## Critique-review (meta-Critic, DR-1)

**Reviewed by**: critique-review agent | **Date**: 2026-05-31 | **Dual-review verdict**: EXTEND

Meta-Critic confirmed all 11 first-Critic findings VALID with correct severity (zero false positives, zero severity adjustments) and verified the Builder's fix-deltas on disk (seams match real headings; v0.78.0 + `_entry_present_in_repo` correct; no hidden OSDG-1 registry — `_GUARDED_GLOBS` is glob-based + `_CANONICAL_SKILLS` already lists all three). It added 2 missed findings:

#### M-add-1 (Major): B1 fix sanitizes the tool's OWN literals but not the EXTRACTED source text it re-emits — em-dash (U+2014) from changelog/risk headers still crashes cp1252 stdout
- **Issue**: the synth renders rule-family names + risk titles from sources saturated with U+2014 (RR-1 schema MANDATES the `## R-N — <title>` em-dash separator, `risk-register.md:3`; changelog v-headers `## v0.77.0 — …`). B1's stated fix covered only the preamble/marker — the extracted-text path (the synth's whole purpose) still crashes.
- **Builder draft**: ACCEPTED-FIXED — design.md §Components adds a mandatory `_ascii_fold()` pass over the **full rendered frame immediately before stdout** (`—`→`-`, `→`→`->`, `…`→`...`, strip remaining non-ASCII), covering extracted tokens; must-not-defer + bespoke-test fixture updated accordingly.

#### M-add-2 (Minor): bespoke cp1252 test has 2 unstated obligations — rollup-sentinel token + em-dash fixture
- **Issue**: (i) the test must call `_assert_no_encoding_error(proc, "tools.project_frame_synth")` with that exact token or the rollup-sentinel parity test fails (the tool has `main()` → lands in `discovered_set`); (ii) the fixture must carry U+2014/U+2192 source or the test passes vacuously while the real crash ships.
- **Builder draft**: ACCEPTED-FIXED — design.md §BC-PROJ-9 surface-(2) now states both the exact literal-token call and the em-dash-bearing fixture requirement.

**Meta-Critic reservation**: M-add-1's severity assumes verbatim emission; the `_ascii_fold()` on the full frame pre-addresses it by construction — confirm the sanitization point is the single full-frame fold (it is, per the design edit).

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: NEEDS-FIXES

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | ASCII-only emitted literals — design.md §Components |
| B2 | Blocker | ACCEPTED-FIXED | bespoke required-arg cp1252 test — design.md §BC-PROJ-9 surface (2) |
| B3 | Blocker | ACCEPTED-FIXED | consumption-contract mechanic — design.md §Consumption contract |
| M1 | Major | ACCEPTED-FIXED | smoke cmd `--slice-dir` — mission-brief.md §Mid-slice smoke |
| M2 | Major | ACCEPTED-FIXED | `test_v_0_78_0_pfs1_entry_present_in_repo` + v0.78.0 — design.md §MEPD-1 |
| M3 | Major | ACCEPTED-FIXED | OSDG-1 changelog line + CLAUDE.md tracked surface — design.md §MEPD-1 / §What's-new |
| M4 | Major | ACCEPTED-FIXED | synthesis-property test + AC #1 reword — mission-brief.md AC#1 / TF-1 plan |
| M5 | Major | ACCEPTED-FIXED | Step-0.5 expected-degraded; dropped Step-7 re-synth — design.md §What's-new / AC#2 |
| M6 | Major | ACCEPTED-FIXED | per-pin literal/seam/shape — design.md §structural-pin spec |
| M-add-1 | Major | ACCEPTED-FIXED | `_ascii_fold()` on full frame (extracted text) — design.md §Components |
| M-add-2 | Minor | ACCEPTED-FIXED | rollup token + em-dash fixture — design.md §BC-PROJ-9 surface (2) |
| m1 | Minor | ACCEPTED-FIXED | in-repo repo-root changelog read — design.md §What's-reused |
| m2 | Minor | ACCEPTED-PENDING | register R-7-class silent-degrade risk during /build-slice |
