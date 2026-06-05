# Slice 114: convert-agent-prose-to-vault-seam

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: R-32 (external-vault flip; `mitigating`) — drains the **agent-prose** residual, one of the two remaining R-32 pre-move residuals (the other being the physical move itself).

## Intent

Complete the [[ADR-105]] `<vault>/` prose-seam rollout by converting the **agent-prose surface** that slice-113 explicitly deferred. Four subagent files (`agents/code-review.md`, `agents/critic-calibrate.md`, `agents/critique-review.md`, `agents/diagnose-narrator.md`) carry `architecture/` / `diagnose-out/` location literals. Because a subagent does **not** inherit the project CLAUDE.md, a file with convertible refs needs its **own** self-sufficient ADR-105 resolver-context note (the slice-112 `agents/critique.md` pilot block) before its convertible refs are rewritten to `<vault>/`. After this slice the only R-32 pre-move residual is the physical vault move.

**Scope sharpened at `/design-slice` (AP-17 / TPHD-1 a):** per-occurrence classification (`vault_flip_prose_inventory --json`) shows only **2** of the 4 files carry *convertible* refs — `code-review.md` (2) + `critic-calibrate.md` (1). The other two (`critique-review.md`, `diagnose-narrator.md`) carry **only carve-out-class refs ADR-105 mandates stay concrete** (active-folder class 5 / diagnose-out class 7); converting them would pre-decide R-32.a or use a non-existent `<diagnose-out>` seam. They stay **untouched** (note-less carve-outs per M-add-1) and the flip slice drains them with all other carve-outs. See `design.md` for the per-file disposition table.

## Acceptance criteria

1. The 2 convertible-bearing agent files (`code-review.md`, `critic-calibrate.md`) each carry a self-sufficient ADR-105 `<vault>/` resolver-context note (the `agents/critique.md` pilot shape), so a subagent resolves `<vault>/` without inheriting CLAUDE.md; the 2 no-op files stay untouched with a recorded rationale.
2. The 3 **convertible** vault-content reads are rewritten to `<vault>/…` (`code-review.md` ×2, `critic-calibrate.md` ×1); every surviving `architecture/`/`diagnose-out/` literal is a deliberate **carve-out** classified per ADR-105 in `design.md`'s per-file disposition table.
3. `tools/vault_flip_prose_inventory.py --strict` passes (one-way ratchet holds, no baseline drift) and the agent-surface convertible count drops to its documented carve-out floor.
4. No new in-repo↔installed agent drift: BOTH edited agents are forward-synced to `~/.claude/agents/` and **drift-guarded** — `code-review.md` by the existing `test_code_review_agent_drift.py`, `critic-calibrate.md` by a NEW `test_critic_calibrate_agent_drift.py` added this slice (closing the unguarded-sync gap, M1); each is content-equal modulo EOL; `agents/critique.md` is **not** touched (CAD-1).
5. `<vault>/risk-register.md` R-32 is updated to record the agent-prose residual as drained, leaving the physical move as the sole pre-move residual.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Self-sufficient seam note on the 2 converted files | `grep -l 'ADR-105' agents/code-review.md agents/critic-calibrate.md` returns both; visually confirm each note states the `<vault>/` default + the "subagent does not inherit CLAUDE.md" resolver line. `critique-review.md` + `diagnose-narrator.md` remain note-less (unchanged). |
| 2 | Convertible refs rewritten, carve-outs kept | Diff each touched file; cross-check every surviving `architecture/`/`diagnose-out/` literal against the `design.md` per-file disposition table |
| 3 | Ratchet passes | `$PY -m tools.vault_flip_prose_inventory --strict` exits 0; `--json` shows `rewrite-at-flip`==127 / `doc-example`==4 / `EXPECTED_TOTAL`==131 (derived expected counts, APED-1-confirmed at design; `_BASELINE_SHA256` is derived at build, never estimated — m3); grep the output for any `<vault>/slices/slice-NNN` mis-bucket (none) |
| 4 | No installed-copy drift | `$PY -m pytest tests/methodology/test_code_review_agent_drift.py tests/methodology/test_critic_calibrate_agent_drift.py` both green after forward-sync; byte/EOL-agnostic diff of `code-review.md` + `critic-calibrate.md` vs `~/.claude/agents/<name>.md`; `$PY -m tools.critique_agent_drift_audit --repo-root .` still green (critique.md untouched) |
| 5 | R-32 updated | `$PY -m tools.risk_register_audit <vault>/risk-register.md --json` shows R-32 mitigation text mentions agent-prose drained; physical move named as sole residual |

## Must-not-defer

- [ ] Each agent's seam note is **self-sufficient** — this is the entire reason the surface was split into its own slice (subagent ≠ CLAUDE.md inheritor).
- [ ] Carve-out determination is **deliberate, per-literal**, not blanket-convert — honor the slice-113 lesson: a literal that is concrete *because a tool consumes it* stays concrete, and distinguish a command-literal from a prose **mirror** of one (the slice-113 `_PATHSPEC_RE` line-local gap).
- [ ] Forward-sync edited agents to `~/.claude/agents/` so the agent surface does not silently drift; sequence against the R-28 shared-`~/.claude/` contention fragility.
- [ ] Do **not** edit `agents/critique.md` (already converted in slice-112; under CAD-1 content-equality).

## Out of scope

- The physical vault move / git-untrack / `/commit-slice` RETIRE no-op — that is the separate `flip-vault-to-external-store` slice; R-32 stays `mitigating` until then.
- The 116 skill carve-outs slice-113 finalized as intentionally concrete (this slice touches only `agents/*.md`).
- `agents/AUTHORING.md` and `agents/field-recon.md` (zero convertible location literals — not in the inventory).
- Minting any new RULE-ID / methodology-changelog entry / VERSION bump (anticipated MEPD-1 EXCLUDE — applying the open-ended ADR-105 rollout within its documented scope; the EXCLUDE call itself is a `/reflect` determination, not assumed here).
- Updating the root `CLAUDE.md` CAD-1 enumeration prose to name `code-review` + `critic-calibrate` (m-add-1) — a separate courtesy-parity cleanup per the slice-096 precedent; the drift *tests* are the authoritative guarded-set and gate regardless. Recorded in `design.md` §Decisions as a deliberate deferral.

## Dependencies

- Prior slices: [[slice-112-make-prose-vault-location-agnostic]] (minted ADR-105 + the `critique.md` pilot seam-note shape), [[slice-113-bulk-convert-remaining-skills-to-vault-seam]] (skill bulk; deferred this agent surface — the M1/TRI-1-ratified follow-on), [[slice-107-inventory-vault-flip-prose-surface]] (the inventory + ratchet tool).
- Vault refs: [[decisions/ADR-105]] (the `<vault>/` seam convention + carve-out classes), [[risk-register#R-32]].
- Tool: `tools/vault_flip_prose_inventory.py` (the one-way ratchet that pins the conversion).

## Mid-slice smoke gate

After converting ~2 of the 4 files, run:
```
$PY -m tools.vault_flip_prose_inventory --json
```
Expected: the agent-surface convertible count is dropping toward the carve-out floor, **and** grepping the output (or the converted files) shows no `<vault>/slices/slice-NNN` active-folder path was wrongly converted (the slice-113 mis-bucket lesson). Spot-read one converted agent end-to-end: its seam note resolves `<vault>/` and the body reads correctly. **Also prove the new `test_critic_calibrate_agent_drift.py` non-vacuous** (AP-5): it must RED on a mutated/un-synced installed copy (the `DRIFT` signature) BEFORE the forward-sync, then green after. If a wrongly-converted carve-out, a missing seam note, or a vacuously-green drift test shows up: STOP, fix before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
