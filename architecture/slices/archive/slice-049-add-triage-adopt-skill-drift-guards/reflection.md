# Reflection: Slice 049 add-triage-adopt-skill-drift-guards

**Date**: 2026-05-19
**Shipped**: YES

## Validated

- The mini-CAD per-file pattern extends cleanly to the opener skills — `assert_md_forward_synced` reused verbatim (2 refs each, zero new comparator); both new tests pass on the synced tree with an independent genuine non-tautological FAIL→PASS for triage AND adopt (build-log 15:00).
- OSDG-1 / `## v0.57.0` / 4-part PMI-1 bump / entry-pin pair is convention-correct — meta-Critic confirmed against the v0.50–v0.56 entry-pin naming + SOAD-1 plain-RULE-ID precedent; validated by PMI-1/INST-1 clean at version 0.57.0, MCFS-1 PASS, entry-pin pair green.
- One-row-per-slice shippability schema (B-add-1) — exactly one row #49; SRSC-1 pinned runner 49/49 PASS; SCMD-1 + PTFCD-1(b) pre-gates clean (286 test-path tokens all resolve, incl. the new `test_v_0_57_0_osdg_1_*` functions).
- `.gitattributes skills/**/SKILL.md text eol=lf` already covers both new openers — no `.gitattributes` change needed (first Critic + meta-Critic both verified; validated by the EOL-agnostic tests passing on the real CRLF working tree).

## Corrected

- **The rev-0 MEPD-1(b) "no changelog / no VERSION bump" pre-decision was FALSE and is withdrawn** (Critic B2, the load-bearing catch). It cited "slice-035 added build/commit drift tests with no independent bump" — recompute proved those were first added by **slice-021** (commit `8823c53`) riding slice-021/BRANCH-1's *existing* v0.35.0 4-part bump (`methodology-changelog.md:474`); no no-bump precedent exists. Corrected in [[design.md]] rev-1/rev-2 (pre-decision withdrawn; OSDG-1/v0.57.0/[[decisions/ADR-051]] added) — the slice IS a methodology-surface behavior change by the changelog's own Inclusion heuristic.
- rev-0 TF-1 plan cited phantom `test_shippability_catalog.py` (B1), prose-only AC3/AC4 rows (M1), "two shippability rows" (B-add-1) — all corrected in [[mission-brief.md]] rev-2.
- rev-1's own B1 fix re-cited the AC3 PMI-1 test to the WRONG file (`test_plugin_manifest_audit.py`); the real `test_plugin_yaml_version_matches_version_file_invariant` lives in `test_methodology_changelog.py`. Caught by the TPHD-1 `/build-slice` pre-flight (defense-in-depth), corrected before plan-mode entry.

## Discovered

- **The 4-part PMI-1 bump's installed `~/.claude/ai-sdlc-VERSION` leg is a recurring forward-sync miss.** At slice-049 start it was `0.55.0` while in-repo `VERSION` was `0.56.0` — a latent slice-048 leg-drift, surfaced ONLY because Critic-M2's pre-sync evidence-preservation step forced a diff before the copy. MCFS-1 (slice-041) deterministically guards the installed *changelog* leg, but **nothing deterministically guards the installed `ai-sdlc-VERSION` leg** — PMI-1 audits in-repo `VERSION`==`plugin.yaml`, never the installed file. Impact low (the installed `ai-sdlc-VERSION` is informational; no audit consumes it), so NOT promoted to a risk-register ID (consistent with slice-048's handling of the analogous N=1 mini-CAD gap). N=2 recurrence (slice-035 DEVIATION-2 was the prior instance), known cheap fix-shape → **strong next-slice candidate**: an MCFS-1-analogue gate for `~/.claude/ai-sdlc-VERSION` (or fold the VERSION leg into MCFS-1's whole-file gate family).

## Deferred

- `add-soad1-lint-audit` + per-skill ask-prose retrofit — reason: slice-048 backlog items, unchanged this slice. Lands in: backlog.
- Generalized INST-2 multi-file mini-CAD audit — reason: slice-009/010 N=1-actual-drift threshold law unchanged; OSDG-1 is a per-file member-addition, not a generalization. Lands in: nowhere (decided-not-discovered, standing).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + `critique-review.md` (DR-1 EXTEND) + reality observed during build/validate:

- **B1** (phantom `test_shippability_catalog.py`): **VALIDATED** — ACCEPTED-FIXED; PTFCD-1 audit + TPHD-1 pre-flight at validate confirm the phantom would have FAILed `--strict-pre-finish`; fix held (PTFCD-1 clean, 286 tokens resolve).
- **B2** (false slice-035 precedent → slice IS a behavior change): **VALIDATED** — ACCEPTED-PENDING; the load-bearing catch. The recompute (commit `8823c53`, changelog:474) reproduced exactly; v0.57.0/OSDG-1/4-part bump landed green. **First-Critic WIN** — caught a Builder false-precedent that was the slice's own MEPD-1(b) self-violation (RSAD-1 recursive-self-application).
- **M1** (prose-only AC3/AC4): **VALIDATED** — ACCEPTED-FIXED; TF-1 `--strict-pre-finish` passed only after the fold/re-cite (8 rows PASSING). The slice-045 law would have FAILed the original.
- **M2** (forward-sync masks pre-existing drift): **VALIDATED — highest-signal** — ACCEPTED-FIXED; reality VINDICATED it concretely: the pre-sync diff step is *exactly* what surfaced the latent slice-048 `ai-sdlc-VERSION` drift. Without M2 the 4-part bump would have silently overwritten 0.55.0→0.57.0 with zero record. A first-Critic Major that produced a real discovery, not just theoretical safety.
- **m1** (uncorroborated slice-019/021 claim): **VALIDATED** — ACCEPTED-FIXED; deleted (same false-precedent class as B2).
- **m2** (WIRE-1 format): **VALIDATED (no-op)** — format was correct; logged per honesty rule.
- **B-add-1** (meta-Critic: "two rows" violates one-row-per-slice + makes AC3 pin unsatisfiable): **VALIDATED** — ACCEPTED-FIXED; reality confirmed — SRSC-1 49/49 with exactly one row #49, and `test_v_0_57_0_osdg_1_shippability_consumer_propagation` (single-row assertion) passes. "Two rows" would have shipped a self-contradictory contract. **Meta-Critic WIN** (load-bearing missed-finding).
- **M-add-1** (meta-Critic: CLAUDE.md edit unguarded by an existing prose-pin): **VALIDATED** — ACCEPTED-FIXED; `test_root_claude_md_cad1_eol_agnostic.py` is section-scoped to exactly the edited `## Self-hosting discipline` block; re-run green. **Meta-Critic WIN** (slice-039 class).

**Missed by Critic**: the rev-1 B1-fix's wrong-file re-citation of `test_plugin_yaml_version_matches_version_file_invariant` — neither the first Critic nor the meta-Critic flagged it (B1 caught the phantom *file*; the rev-1 fix I authored introduced a new wrong-*file*-for-a-real-*function* citation — the slice-032 "a design correction is itself an unguarded adversarial surface" class, recurring). Caught by the TPHD-1 `/build-slice` pre-flight (defense-in-depth working as designed). This is a **Builder-side** recompute-don't-trust miss (I transcribed without grepping the file), N+1 to the slice-042/048 "the replacement is transcribed from a non-authoritative source" pattern — per the slice-037 law the durable cure is the existing TPHD-1 gate, NOT a new Critic dimension.

**Pattern**: Dual-Critic+DR-1 paid off decisively AGAIN on a methodology-codification slice — **N+1 to the standing 026/029/038/039/046/047/048→049 law**. First Critic caught the load-bearing false-precedent (B2 — the slice's own MEPD-1(b) self-violation, RSAD-1); meta-Critic EXTEND added 2 genuine load-bearing misses (B-add-1 unsatisfiable-contract, M-add-1 unguarded-prose-pin) with **zero false positives across both layers**. The first Critic's recurring structural blind spot is again *contract/regression-scope vs internal-logic* (the meta-Critic's own Notes named this — strong `/critic-calibrate` input: a candidate first-Critic dimension probing "does the rev-N remediation land consistently against existing enforced conventions — catalog schema, prose-pins, entry-pin naming?"). M2 demonstrates a first-Critic Major can yield concrete discoveries, not just theoretical safety — evidence-preservation disciplines earn their cost empirically.

## Lessons for next slice

- **The 4-part PMI-1 bump's installed `~/.claude/ai-sdlc-VERSION` leg has no deterministic forward-sync gate** (MCFS-1 covers only the changelog leg). It silently drifted at slice-048 (N=2 with slice-035 DEVIATION-2). Strong next-slice candidate: **`add-ai-sdlc-version-forward-sync-gate`** — an MCFS-1-analogue (cheap, fix-shape known). Until then, the M2 pre-sync-diff discipline is the only control and it is per-slice-manual.
- **A rev-N design correction that re-cites ANY test path/function is itself an unguarded adversarial surface (slice-032 class, N+1).** When applying ACCEPTED-FIXED edits that re-cite a test, `grep -l` the actual file for the function in the SAME fix block — Builder recompute-don't-trust applied to one's own corrections (slice-042/048 law). TPHD-1 pre-flight is the structural backstop and it worked; the durable cure is that gate, not new Critic machinery.
- **Genuine-contrast for a drift-guard member-addition is cheap and MUST be per-member** (perturb triage AND adopt independently — not one as proxy for both); the slice-048 zero-revert pin technique generalizes to member-additions with no revert ops.
- **A drift-guard family member-addition whose slice has no other bump reason is itself a methodology-surface behavior change** (ADR-051 / B2 resolution) — settles the ambiguity slice-049 rev-0 got wrong: future member-additions follow the v0.57.0/bump path, not the slice-019/021-rode-an-existing-bump non-precedent.

## Vault updates made (thin vault — small list)

- This slice's [[design.md]] — rev-1/rev-2: rev-0 MEPD-1(b) pre-decision withdrawn + corrected analysis (done at /critique TRI-1, before build)
- [[decisions/ADR-051]] — new, accepted, `supersedes: null` (extends CAD-1/mini-CAD/EOL-DRIFT-1 lineage via OSDG-1)
- [[methodology-changelog.md]] — `## v0.57.0` OSDG-1 entry (new rule; supersedes nothing)
- `VERSION` / `plugin.yaml` / `~/.claude/ai-sdlc-VERSION` / `~/.claude/methodology-changelog.md` — 4-part PMI-1 atomic bump 0.56.0→0.57.0 (the installed `ai-sdlc-VERSION` leg reconciled from a pre-existing 0.55.0 slice-048 drift)
- [[shippability.md]] — row #49 (OSDG-1 critical path; one row covering both guards)
- `CLAUDE.md` — `## Self-hosting discipline` Mini-CAD bullet generalized to OSDG-1 / triage+adopt
- [[drift-log.md]] — clean full-audit entry (0/0)
- No risk-register entry (the discovered `ai-sdlc-VERSION` leg-gap is low-impact / a next-slice candidate, not a standing risk — consistent with slice-048's handling of the analogous N=1 mini-CAD gap)
- No ADR superseded
