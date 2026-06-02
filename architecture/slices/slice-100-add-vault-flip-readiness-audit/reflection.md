# Reflection: Slice 100 add-vault-flip-readiness-audit

**Date**: 2026-06-02
**Shipped**: YES

## Validated
- The context-aware ordered ruleset (ADR-091) classifies the production-`.py` surface correctly — validated by the real-tree run (4 must-rewrite / 24 already-routed / 60 doc-example / 0 needs-human) + 17 tests.
- Capability-without-flip holds — `_vault_paths` default `Path("architecture")` unchanged; full suite 1345 + shippability 107/107 (every existing tool/test/skill identical).
- B-add-1 (the bare-segment match) is load-bearing — the 4 `project_frame_synth.py` sites a slash-only matcher would have silently certified clean are correctly `must-rewrite`. Verified by execution, not reasoning.
- The AC3 baseline pin is non-vacuous — proven by 2 mutations AND by catching a live fix-regression (below).

## Corrected
- (none) — no design claim was refuted; the design survived the 3-Critic stack with all findings being *additive hardening*, not corrections of shipped behaviour. The `_vault_paths` seam, Class-B marker convention (slice-098), and VWS-1 template all behaved as the design assumed.

## Discovered
- **The whole-line-substring marker scan (slice-099 lesson) recurred in a NEW tool** — I wrote `marker in line_txt` despite slice-099's aggregated lesson #1 ("a control-token detector must be region-anchored, never whole-file token-in-content"). The code-Critic caught it (M2). The lesson needs stronger propagation (build-check candidate — see lessons).
- **The m2 count fan-out is WIDER than the BC-PROJ-9 checklist + the INSTALL.md prose** — two per-tool inventory-pin tests (`test_pulse_worktree_resolver_tool_inventory`, `test_stranded_slice_audit_tool_inventory`) hardcode the L22/L166 tool count `"39"`. The first INSTALL bump missed them; the full suite caught them. (N+1 on the new-tool count-fan-out lesson.)
- **A guard-test proven non-vacuous catches the BUILDER's own fix-regression, not just future slices** — my M2 reorder put path-construction before seam-internal, mis-classing `_vault_paths.py:53 _DEFAULT` as a 5th must-rewrite; the AC3 baseline pin FAILED loudly and caught it. Concrete payoff of the slice-092 mutation-non-vacuity discipline.
- No new risk-register entry: R-32 stays `mitigating` (this slice advances flip-readiness on the production-`.py` surface but R-32 retires AT the flip). The audit's documented residual (fully-dynamic path with no constant segment is invisible) is a named static-analysis limit, not a new risk.

## Deferred
- **The `tests/**/*.py` surface** (loud breakage; intentional seam constants) — follow-up `vault-flip-readiness-tests`. (Out of scope per ADR-091.)
- **The contract-prose surface** (`SKILL.md`/`agents`/`CLAUDE.md`/`INSTALL.md`) — bulk-rewritten atomically at flip-execute; not reliably auto-classifiable. Owned by flip-execute or a dedicated prose slice.
- **The actual flip** (physical move + git-untrack + default-flip + prose rewrite + PCR-replacement) — the next major cut. The audit + `--strict` baseline guard are now ready to gate it; the must-rewrite checklist for the production-`.py` surface is exactly the 4 `project_frame_synth.py` sites.

## Critic calibration

3-Critic stack, **zero false-alarms across all three layers** — every finding VALIDATED:

- **Design-Critic** (critique.md): B1 (error-strings mis-classed) VALIDATED — ACCEPTED-FIXED; the node-type heuristic was genuinely unsound, verified by the real markers at `state_transition_pin_audit.py:381/395/407`. B2 (`_SOFT_FILE_SET` unmarked) VALIDATED. M1/M2/M3 (match-rule / pin-key / over-claim) VALIDATED. m1/m2 VALIDATED. No OVERRIDDEN, no FALSE-ALARM.
- **Meta-Critic** (critique-review.md): EXTEND — confirmed all 7 first-Critic findings + correct severities, AND surfaced **B-add-1** (the bare-segment false-negative my own M1 fix introduced), VALIDATED by execution + confirmed by the build (4 real sites). The FIRST Critic MISSED B-add-1; the meta-Critic's execution caught it.
- **Code-Critic** (code-review.md): M1 (dead module-scope flow) / M2 (whole-line marker false-route — slice-099 recurrence) / M3 (dynamic-fragment documented-not-implemented) / m1 (open+os.path.join sinks) / m2 (3.12 tokenizer) — all VALIDATED, all hardened in-slice. The design+meta stack structurally could not reach these execution-level false-negatives.

**Missed by ALL Critics**: (a) the m2 count fan-out into the 2 per-tool inventory-pin tests — caught by the full suite, not any Critic; (b) my M2-reorder seam-internal regression — caught by the AC3 baseline pin, not any Critic. Both are deterministic-gate catches, reinforcing that the guards are the backstop for what adversarial review misses.

**Pattern**: the code-Critic is a REQUIRED execution-level pass for any new AST/parser tool (APED-1, N+1) — it found 3 silent-breakage false-negatives + a known-lesson recurrence the design+meta layers can't reach. And "a Critic's own fix is a fresh claim" recursed through the BUILDER's fix (M2 reorder → seam-internal regression), caught by the deterministic pin. Do NOT collapse the 3-Critic stack OR the non-vacuous guard.

## Lessons for next slice
- **The code-Critic is mandatory for a new AST/parser/classifier tool** — it caught 3 silent-breakage false-negatives (incl. a slice-099 whole-line-substring recurrence) that the design+meta stack structurally cannot reach. APED-1-by-execution N+1.
- **The new-public-tool count fan-out includes per-tool inventory-pin tests** (`test_*_tool_inventory.py` hardcode the INSTALL.md L22/L166 count) — beyond the BC-PROJ-9 checklist + INSTALL.md prose. On adding a public tool, grep EVERY `"39"`-style count literal across tests/ too. Strong build-check / `/critic-calibrate` candidate.
- **A guard-test proven non-vacuous by mutation catches the builder's own fix-regression live** — the AC3 baseline pin caught my M2-reorder mis-classing `_vault_paths:53`. The mutation-non-vacuity discipline (slice-092) earns its keep against the builder, not just future slices.
- **The whole-line-substring marker-scan anti-pattern (slice-099) recurred in a fresh tool** — eternal prose-discipline isn't propagating it; a build-check ("a marker/token detector must be node/region-anchored, not `marker in line_text`") would catch the class structurally.
- **For the flip-execute slice (next major cut)**: the production-`.py` must-rewrite checklist is exactly the 4 `project_frame_synth.py` sites; run `vault_flip_readiness_audit --strict` as the pre-flight gate; the tests/ + prose surfaces remain to be scoped.

## Vault updates made (thin vault)
- [[lessons-learned.md]] — appended the slice-100 entry (via `vault_edit append`, SVW-1 channel).
- [[shippability.md]] — row #108 (added at build, T6).
- [[drift-log.md]] — slice-100 CLEAN entry (added at build, DCE-1).
- [[risk-register.md]] — no change (R-32 stays `mitigating`; retires at the flip).
- No ADR superseded; ADR-091 accepted as designed (+ the B-add-1/M1/M2/M3 hardening applied within its `reversibility: cheap` envelope).
- **MCFS-1 / AVFS-1 / TVFS-1**: no-op — MEPD-1 EXCLUDE (no VERSION / methodology-changelog bump), confirmed exit 0 in the Step-6 battery.
- **BC-1 promotion**: NOT auto-applied (opt-in / user-gated). Two strong candidates surfaced for the user (see lessons): the per-tool-inventory count-fan-out, and the node/region-anchored-marker rule.
