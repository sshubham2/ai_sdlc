# Critique Review: Slice 100 add-vault-flip-readiness-audit

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-02
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's seven findings are all VALID with correct severities, and the Builder's fix-deltas (the B1 context-aware ordered ruleset, the B2 `_SOFT_FILE_SET` marker, the M2 full-value pin key, the M3 reframe) are individually sound — verified against the real corpus with an independent AST harness. But the B1/M1 fix introduced a fresh, unflagged false-negative: the trailing-slash match rule renders four live bare-`"architecture"` path-construction sites in `tools/project_frame_synth.py` invisible to the audit, so the slice's central "complete checklist / clean bill of health" claim is false as specified. One missed Blocker.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (error/warning strings mis-classed as breakage) — confirmed; Blocker appropriate. Markers verified (`state_transition_pin_audit.py:381/395/407`, em-dash `—` variant). The Builder's ordered ruleset (ADR-091 rules 1-5) correctly routes them: f-string error messages like `state_transition_pin_audit.py:447-448` (NO marker) still land `doc-example-safe` via rule 5, because rule 4's dynamic-fragment branch requires a path/git context they don't satisfy. Fix holds. (Rule-1 marker recognition is partly redundant with the rule-5 default for f-strings — observation, not a defect.)
- **B2** (`_SOFT_FILE_SET` defn unmarked Class-B) — confirmed; Blocker appropriate. `parallel_conflict_resolver.py:60-61` carry no marker; the 21 usage lines do. The B2 fix (mark 60-61) moves them to `already-seam-routed` via rule 2, introduces no new contradiction — these are git pathspecs fed to `_git_show_stage(...)` → `git show :N:<pathspec>`, retire-at-flip per ADR-089. Merge-contention vs slice-101 is low: `slice/101` has zero diverging commits and does not touch PCR (verified `git diff master...slice/101`).
- **M1** (match rule unspecified, over-match risk) — confirmed; Major appropriate *for the over-match half*. The specified regex + audit-self-source exclusion correctly close the over-match (SVW-1 regex literal, `_DERIVED_DIRS`). But the trailing-slash requirement opens a NEW under-match — see B-add-1.
- **M2** (fragile pin key; mutation proves presence not class) — confirmed; Major appropriate. Adjacent string-literal concatenation merges into a single `ast.Constant` spanning multiple linenos with the full value intact, so the full-`ast.Constant.value` key is the right fix; the added `test_error_message_literal_not_must_rewrite` mutation correctly guards the B1 correct-class property.
- **M3** (`diagnose-out/` near-vacuous; must-rewrite near-empty; AC1/smoke over-claim) — confirmed; Major appropriate. Independently confirmed zero `diagnose-out/` path-construction literals and zero *slashed* path-construction `architecture/` literals in `tools/`. The smoke-gate reframe (gate on total-classified >0, not must-rewrite >0) is honest and correct. **Caveat**: the reframe's *premise* ("must-rewrite near-empty because slice-098 already routed this surface") is itself partly false — see B-add-1; the honesty fix is right but understates a real residual.
- **m1** (`_pyfn._find_repo_root` non-existent) — confirmed; Minor appropriate. Fix correct.
- **m2** (five-site fan-out grep) — confirmed; Minor appropriate; ACCEPTED-PENDING build-time grep right.

## Suspicious findings

No suspicious findings. Every first-Critic finding survives a second-pass execution against the real corpus.

## Missed findings

- **B-add-1: Bare-`"architecture"` path-construction in `tools/project_frame_synth.py` is invisible to the audit — four real `must-rewrite` sites silently certified clean** (Blocker). `project_frame_synth.py` constructs vault paths as `repo_root / "architecture" / "concept.md"` (121), `/ "triage.md"` (122), `/ "slice-queue.md"` (185), `/ "risk-register.md"` (194) — `/`-BinOp path-construction where the vault-dir operand is the **bare string `"architecture"` with no trailing slash**. Two compounding gaps: (1) the M1 match rule requires a trailing slash → the bare literal is never matched → not classified into any of the four classes, violating AC2's fail-closed "every scanned literal lands in exactly one class"; (2) ADR-091 residual (ii) frames "a bare directory-name reference (no slash) is out of this surface" as benign — but `repo_root / "architecture" / "X"` is the *most classic* silent path mis-resolve, not a benign config name. Verified: `project_frame_synth.py` does NOT import `VAULT_ROOT`/`_vault_paths` (genuinely unrouted) and was last touched at slice-088, NOT slice-098 — so M3's "slice-098 already routed this surface" premise does not cover it. Worse: the file's three *slashed* `architecture/` occurrences (44/48/304) ARE prose (docstring + argparse help) and classify correctly `doc-example-safe`, so the audit emits a clean verdict for the file while masking the four real `must-rewrite` sites — the false-completeness outcome AC1 exists to prevent. **Proposed fix**: extend the path-construction detector (rule 3) to recognize a bare-dir-name string literal (`"architecture"` / `"diagnose-out"`, no slash) when it is an operand of a `/`-BinOp or an arg to `Path(...)`/`PurePath(...)` — detect the *context* even when the literal lacks the slash, rather than gating entirely on the slash pattern. Re-derive the baseline (the four `project_frame_synth.py` sites become the slice's genuine first real `must-rewrite` entries) and re-run the AC3 non-vacuity mutation against them. Retires the over-claim in M3's reframe + ADR-091 §Consequences ("near-empty").

## Severity adjustments

No severity adjustments. All seven first-Critic severities (B1/B2 Blocker, M1/M2/M3 Major, m1/m2 Minor) are correctly calibrated. (B-add-1 is filed as a new Blocker, not a reclassification.)

## Notes

High confidence on B-add-1: execution-verified (four AST-confirmed `/`-BinOp sites, no VAULT_ROOT import, slice-088 provenance), not reasoned. Calibration observation on the first Critic: strong on the node-type-vs-context axis (B1/M1 correctly demand usage-context classification) but it stopped at the **slash-shaped** literals its own proposed match rule would catch — it never probed whether the path-construction context it championed could exist WITHOUT the slash. A single blind spot, not a pattern: six of seven findings are airtight and the seventh (M1) is correct on the half it addressed; the Builder faithfully implemented every accepted fix, so the residual is a gap in the first Critic's coverage that the Builder inherited, not a botched fix. Reservation for TRI-1: B-add-1 elevates this from a near-empty must-rewrite set to a real (small) one, so the AC3 baseline pin and the mid-slice smoke-gate "must-rewrite may be near-empty" note both need re-derivation — cheap (per ADR-091 reversibility) but not a no-op.
