# Reflection: Slice 048 codify-structured-options-ask-rule

**Date**: 2026-05-19
**Shipped**: YES

## Validated

- SOAD-1 codified verbatim across 5 surfaces (triage Step 5b Fresh+Append, adopt Step 10 Fresh+Append, repo CLAUDE.md `## Ask discipline`) — validated by `test_soad1_structured_options_ask_rule.py` 10/10 (4 section-scoped per-fenced-block pins + repo-CLAUDE.md pin + 5 M-add-1 self-consistency guards).
- The platform premise (Claude Code surfaces a user notification only on options prompts, not on bare free-text) — WebSearch-verified by the first Critic (anthropics/claude-code#13830, open feature request) + ADR-048 lineage. The slice's entire value rests on this external-platform fact; it was verified, not asserted (BC-GLOBAL-3 discipline honoured at /critique rather than burned at TRI-1 like slice-047).
- Genuine-contrast test-first works cleanly for a **pure-additive** prose codification with **zero revert ops**: pin the new literal (grep-verified absent in all 5 surfaces pre-edit) + negative M-add-1 guards (bare ASK literal present in 3/5 pre-edit) → 10 FAIL → 10 PASS, non-tautological, no edit-then-revert (cf. slice-046 lesson; cheaper than slice-045's revert-2-edits technique).
- VAL-1 clean (0 secrets, 0 hallucinated imports); shippability 48/48; PMI-1 lockstep 0.55.0→0.56.0; all 14 Step-6 audit groups clean.

## Corrected

- design.md draft claim *"MCFS-1/slice-041 retired the per-version changelog coupling, so no `test_v_0_56_0_*` is added"* → reality: MCFS-1 retired only the per-version **installed-copy forward-sync reads**; the in-repo `_entry_present_in_repo` pin convention is unbroken (v0.53.0/v0.54.0/v0.55.0). **Corrected in design.md before build** (critique B1, ACCEPTED-FIXED) — the false precedent never shipped; the v0.54.0-STP-1-shape pin pair was added.
- mission-brief must-not-defer #3 *"CAD-1/mini-CAD parity for triage/adopt SKILL.md"* → reality: no `test_triage_skill_drift.py`/`test_adopt_skill_drift.py` exists; obligation is installed-copy forward-sync only. Corrected in design.md "Design corrections" at /design-slice (over-claim removed before build).
- No ADR superseded (ADR-050 accepted, `supersedes: null` — generalizes ADR-048, does not retire it). No risk-register change.

## Discovered

- **triage/adopt SKILL.md are NOT under any mini-CAD in-repo↔installed drift guard** (unlike build_slice/commit_slice/critique/query_design/slice + agents/critique.md CAD-1). A future edit to either opener's SKILL.md could silently diverge from the installed copy with no gate catching it. Impact: this slice's must-not-defer #3 (manual forward-sync) is the only control; it held this slice but is human-dependent. N=1 latent exposure — not promoted to risk-register (no recurrence; manual mitigation applied + verified via the post-T6 MCFS-1-analogue check). Candidate for a future slice: extend the mini-CAD drift-test set to triage/adopt SKILL.md (a clean, well-scoped methodology-hardening cut).

## Deferred

- Per-skill prose retrofit of the existing 24 skills' ask-the-user prose to the AskUserQuestion form — reason: >1 day, user-decided out of scope; the CLAUDE.md SOAD-1 contract governs orchestrator behavior without per-skill edits. Lands in: backlog.
- An executable lint that scans skill prose for free-text-ask anti-patterns — reason: out of scope this slice; SOAD-1 ships as a prose contract + regression pin only. Lands in: backlog (a future "add-soad1-lint-audit" slice if the contract proves insufficient).
- SOAD-1 in the user's personal `~/.claude/CLAUDE.md` — reason: user chose the pipeline-generated project-CLAUDE.md surface; the openers do not manage the personal global file. Lands in: nowhere (decided out of scope, not a standing gap).

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + reality observed during build/validate:

- **B1** (design's "no per-version changelog test" false-precedent): **VALIDATED** — disposition ACCEPTED-FIXED; reality confirmed the concern was load-bearing — `grep`/read of `test_methodology_changelog.py` showed the convention unbroken at v0.53.0/v0.54.0/v0.55.0; the v0.54.0 STP-1 pair was a precise model and the two new pins shipped + pass. **First-Critic WIN**: the Critic rejected a Builder-asserted methodology precedent and verified the why-none against the actual enforcing artifact (the MEPD-1(b) / recompute-don't-trust discipline applied correctly — not a freshly-minted-rule blind spot; MEPD-1 is internalised).
- **M1** (AC5 pin spec internally inconsistent; defeatable global `.count()`): **VALIDATED** — ACCEPTED-FIXED; reality confirmed — the per-fenced-block section-scoped test (slice-021 precedent) was authored and the genuine-contrast worked; a global count would have passed even with Append missed.
- **M2** (free-text escape-hatch conflation): **VALIDATED** — ACCEPTED-FIXED; the corrected notification-less-case wording shipped and aligns with ADR-050 §Decision + must-not-defer #4.
- **M-add-1** (SOAD-1 self-violation inside host templates): **VALIDATED (via DR-1)** — MISSED by the first Critic; caught by the meta-Critic; disposition ACCEPTED-FIXED via user-ratified fix option (a). Reality confirmed it was a genuine literal contradiction: T0 captured 5 M-add-1-guard FAILs (the bare `**ASK** the user: "Run /slice first` literal was present in triage-Fresh / adopt-Fresh / repo-CLAUDE.md pre-edit); the reword removed it from every SOAD-1 surface. **The calibration signal of the slice.**
- **m1** (brittle line-range citations): **VALIDATED** — ACCEPTED-FIXED (demoted to informational; edits anchored on heading+fence).
- **m2** (shippability row #48 forward-asserted): **VALIDATED** — ACCEPTED-FIXED; row was indeed `max(existing)+1` (47→48); confirmed at /reflect against the then-current max.

**Missed by Critic**: M-add-1 — the first Critic verified the rule's *content* and the test oracle's *correctness* thoroughly (B1/M1/M2 all precise, zero false positives across 5 findings) but did not step back to **surface-consistency**: whether the rule, once placed, contradicts its own host artifact. DR-1 caught it. Concrete nameable shape: *"a pure-additive rule-codification slice — does the newly-placed rule literal contradict a pre-existing literal in the SAME host artifact (RSAD-1 surface-consistency / slice-022 self-violation law)?"*

**Pattern**: N+1 to the standing "DR-1 keeps paying decisively on methodology-codification slices; the first Critic's structural blind spot is the slice's novel/own-surface edge, not its mechanical content" law (026/029/038/039/046/047 → 048). Here the shape is specifically *recursive-self-application surface-consistency*. Consistent with the slice-037 law: the durable cure is DR-1 (which worked), **not** a new first-Critic dimension or a build-check. Strong `/critic-calibrate` input — the M-add-1 shape is concrete and generalizable (a codifying slice must be checked for self-violation of the rule it mints, on the rule's own host artifact). First-Critic precision on what it *did* file remains excellent (B1 false-precedent catch is exemplary MEPD-1(b)).

## Lessons for next slice

- **A pure-additive prose-codification slice that injects a new rule into existing artifacts MUST check each host artifact for a pre-existing literal that contradicts the rule** (RSAD-1 surface-consistency — the slice-022 self-violation law generalized from "the codifying slice satisfies the rule" to "the rule does not ship beside its own counter-example on the same artifact"). First Critic blind to this; DR-1 is the structural backstop (slice-037 law — do NOT add a first-Critic dimension or build-check; budget DR-1).
- **Builder false-precedent guard, reconfirmed (B1)**: never assert in design.md that "slice-N / rule-X retired/decoupled Y" without grepping the enforcing test/artifact in the SAME step. The first Critic's MEPD-1(b) recompute-don't-trust caught this one; the durable Builder-side cure is to do that grep at /design-slice authoring time, not rely on the Critic catching it.
- **Genuine-contrast for pure-additive codification needs zero reverts**: pin the new literal (absent pre-edit) + negative guards on the literal being removed (present pre-edit) → one-directional FAIL→PASS, non-tautological, cheaper than any revert technique. Reusable for every future rule-codification slice.
- **Dogfooding SOAD-1 immediately paid**: this very slice used `AskUserQuestion` structured options for the M-add-1 (a)/(b) decision and the plan-approval gate — the rule is exercised by the pipeline that defines it (recursive self-application, N=1 for SOAD-1 itself, clean).

## Vault updates made (thin vault — small list)

- This slice's [[design.md]] — corrected the B1 false-precedent + must-not-defer #3 over-claim (done at /design-slice + /critique, before build; build-log records the M-add-1 fix-option-(a) decision)
- [[methodology-changelog.md]] — v0.56.0 SOAD-1 entry (new rule; generalizes ADR-048; supersedes nothing)
- [[decisions/ADR-050]] — new, accepted, `supersedes: null`
- [[shippability.md]] — row #48 (SOAD-1 critical path)
- `VERSION` / `plugin.yaml` — 0.55.0 → 0.56.0 (PMI-1 lockstep)
- No ADR superseded; no risk-register entry (the discovered triage/adopt mini-CAD gap is a next-slice candidate, not a standing risk at N=1)
