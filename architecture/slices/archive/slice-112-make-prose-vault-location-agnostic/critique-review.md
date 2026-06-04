# Critique Review: Slice 112 make-prose-vault-location-agnostic

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-04
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

(First Critic returned 5 Blockers + 3 Majors + 2 Minors.)

## Summary

The first Critic's review is strong and well-grounded — all 5 Blockers and both substantive Majors verify against live code, and the severities are correct. The meta-Critic confirms 9 of 10 findings as VALID, finds NO suspicious (over-reach) findings, and EXTENDS with two false negatives: (M-add-1) the agent-surface runtime-resolution gap — a Critic SUBAGENT does not inherit CLAUDE.md's `<vault>` rule, so AC4's "both resolve to architecture/" is unproven for `agents/critique.md`; and (M-add-2) the `_DISPOSITION` 5-tuple key is line-text-keyed, so a future edit to a dispositioned definitional literal's line silently drops its exemption and re-reds the gate. One severity nudge on m1 (it under-treats the runtime gap as benign).

## Confirmed findings (VALID + correct severity)

- **B1** (`<vault>` not flip-neutral for composed `<wt_path>/architecture/…` paths) — VALID; Blocker correct. slice/SKILL.md:249,264,267,268; ADR-085§Decision:37 (absolute path) + §Context:17 confirm `<vault>` resolves absolute post-flip → `<wt_path>/<vault>/…` malformed. Design tokenizes all 22 slice literals with no carve-out for these 4.
- **B2** (converting slice/reflect breaks `--op-gate --strict`) — VALID; Blocker correct. Op-gate scans the same files via `_MATCH_RE` (:530, `_skill_of` :469-475); `_OP_CLASS_FLOOR` (:446-450) pins DEFERRED:11/OUT_OF_SCOPE:23; `test_vault_flip_op_gate.py:188,192-196`. The Builder's path-B rebuttal also verifies (`_skill_of`→None for CLAUDE.md/agents at :473).
- **B3** (converting slice:73 breaks BCR-1) — VALID; Blocker correct. `test_bcr_1_backlog_round_trip.py:108,186` literal-assert `diagnose-out/backlog.md` + the canonical phrase.
- **B4** (re-pin omits the 2 "313" shippability rows) — VALID; Blocker correct. shippability line 122 (id 113) + line 126 (id 117) hard-state 313. Exactly FBCD-1 sub-mode (c) (minted at slice-108 / id 114 to catch this AP-10 class). Builder's fan-out set (3 constants + shippability 113 + 117, exact total via `--json`) is the right closure.
- **B5** (`<diagnose-out>` token has no seam) — VALID; Blocker correct. `_vault_paths.py` defines only `_DEFAULT="architecture"` (:53) + `_resolve_vault_root` (:145-162); zero diagnose-out resolution. Builder's draft (scope `<diagnose-out>` OUT, keep diagnose-out/ concrete) is the clean fix and also collapses B3.
- **M1** (converting slice-queue.md pre-decides its undecided disposition) — VALID; Major correct. `_UNDECIDED_DISPOSITION_RE` (:403) routes slice-queue ops OUT_OF_SCOPE because ADR-090 keeps it main-tree-pinned; tokenizing slice:250 asserts a deferred disposition.
- **M2** (definitional CLAUDE.md:5 counted in pilot-7, disposition deferred) — VALID; Major correct. CLAUDE.md:5 `**Vault**: architecture/` is definitional, distinct from :67 (`graphify vault architecture` residual). Counting it while build-deferring its class makes the re-pin total non-deterministic at design time.
- **M3** (`_CONVERTED_FILES` separator + ratchet-independence + mutation proof) — VALID; Major correct. `Occurrence.path` is forward-slash (`audit_root` :272); a `\`-keyed member never matches → vacuous green (R-7). `_baseline_drift` (:329) already trips on multiset change, so the ratchet must be stated INDEPENDENT of the re-pinnable baseline; the mutation proof must inject a literal AND re-pin the baseline, proving exit 2 survives.
- **m2** (pin exact remainder via `--json`, not "~17"/"~258") — VALID; Minor correct. AC5 requires a complete worklist; an estimate cannot satisfy it.

## Suspicious findings

None. Every first-Critic finding verifies against live code or the design text. The meta-Critic specifically tried to break B1 (are the 4 composed paths already carved out? — no, AC3 tokenizes all 22), B2 (is the op-gate truly coupled? — yes), and B5 (does a diagnose-out seam exist anywhere? — no). None collapsed.

## Missed findings (false negatives — meta-Critic EXTENDS)

- **M-add-1 [Major] — Agent-surface runtime-resolution gap: AC4 is UNPROVEN for `agents/critique.md`.** The rule lives "once in CLAUDE.md" and "Claude substitutes it" — true for the MAIN agent (carries CLAUDE.md), FALSE for the Critic SUBAGENT. `agents/critique.md` is the subagent's entire system prompt; a Task-spawned subagent does not inherit project CLAUDE.md. Verified: `skills/critique/SKILL.md` passes NO CLAUDE.md / no `<vault>` rule into the subagent (grep `CLAUDE.md|resolution rule|<vault>|substitut` → 0). Converted `agents/critique.md:256` (`<vault>/triage.md`) → the Critic sees a token it can't resolve. AC4's proof test only asserts the DEFAULT string resolves — not runtime substitution in the agent context. The first Critic's m1 grazes this but treats self-resolution as a given. **Proposed fix**: (a) keep `agents/critique.md` literals CONCRETE `architecture/` — carve the AGENT surface out of the convention (agents are subagent prompts without CLAUDE.md context — same rationale as INSTALL/README), OR (b) embed a self-contained `<vault>` resolution note IN `agents/critique.md` itself. Option (a) is cheaper and collapses the m1 CAD-1 concern. **Interacts with path-B**: path-B (CLAUDE.md + agents) would SHIP exactly this unproven conversion — under M-add-1, path-B should be CLAUDE.md-only, or agents must be made self-sufficient.

- **M-add-2 [Major] — `_DISPOSITION` 5-tuple key is line-text-keyed → dispositioning the definitional CLAUDE.md literal is brittle.** `disposition_key()` (:154-157) = `(path, norm_line, fenced, ordinal, col)` embeds the NORMALIZED LINE TEXT. A future reword of the `**Vault**: architecture/` line (or the resolution-rule subsection) changes `norm_line` → the disposition misses → the definitional literal re-classifies REWRITE_AT_FLIP → lands in `_CONVERTED_FILES` (CLAUDE.md is a pilot member) → the new converted-file invariant reds the gate on a literal that is CORRECTLY concrete. **Proposed fix**: prefer the plain-prose (no-backtick → `doc-example`, never in the rewrite-at-flip set) resolution over a `_DISPOSITION` entry for the definitional literal, and STATE that at design time (not deferred to build). If `_DISPOSITION` is used, add a test that the entry survives a benign reword, or document it as a known APED-1 re-pin trigger.

## Severity adjustments

- **m1** — SEVERITY-WRONG: filed Minor, but the self-resolution half should be Major (= M-add-1). The CAD-1-drift half is correctly Minor (whole-file SHA-256 forward-sync, `critique_agent_drift_audit.py:89-103`; a byte-identical convert stays green). But "the Critic self-resolves its own paths" is the unproven runtime gap (M-add-1), Major not Minor. Split m1: keep the CAD-1 forward-sync note as Minor; promote the agent-runtime-resolution concern to Major per M-add-1.

## Notes

High confidence — every first-Critic finding was verified against the live tool, the two affected test files, the two shippability rows, and ADR-085/090, not on the Builder's say-so. The first Critic's calibration on the BREAKAGE axis is excellent (it found every concrete coupling and got all severities right). Its blind spot is the AGENT-CONTEXT axis (it trusted "self-resolves" without checking the subagent lacks the rule) + the `_DISPOSITION` line-key durability — both second-order "does the convention work where it is consumed" concerns, the natural complement a second pass adds. Reservation: M-add-1 and M-add-2 both partly dissolve under the Builder's pilot-reduction — M-add-1 if the pilot drops to CLAUDE.md-only; M-add-2 only if the build takes the plain-prose route — so the user should treat them as conditional-on-disposition at TRI-1.
