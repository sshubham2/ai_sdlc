# Validation: Slice 112 make-prose-vault-location-agnostic

**Date**: 2026-06-04
**Result**: PASS

The "real environment" for this methodology slice is executing the tool + the methodology audits against the live worktree corpus (not synthetic fixtures) — the AP-3 "run it against the real corpus" discipline.

## Per-criterion results

### AC1: `<vault>` prose-seam convention minted + documented (ADR-105; rule once in CLAUDE.md; `<diagnose-out>` not minted)
- **Status**: PASS
- **Evidence**: `pytest test_prose_vault_seam_convention.py::test_claude_md_states_resolution_rule_exactly_once` + `::test_adr_105_present_and_lists_seven_carve_out_classes` + `::test_diagnose_out_token_not_minted` PASS. `CLAUDE.md` carries "denotes the vault root" exactly once + `<vault>/` + `AI_SDLC_VAULT_ROOT`; ADR-105 lists all 7 carve-out classes; `<diagnose-out>/` is never used as a path placeholder (diagnose-out/ stays concrete).
- **Notes**: Governance ADR-only / MEPD-1 EXCLUDE (no VERSION bump; PMI-1/MCFS-1/AVFS-1/TVFS-1 exit 0).

### AC2: converted-file one-way ratchet (folded into `--strict`, baseline-independent, mutation-proven)
- **Status**: PASS
- **Evidence**: `pytest …::test_converted_file_regression_exits_2` (subprocess `--strict` exit 2 + "CONVERTED-FILE REGRESSED") + `::test_ratchet_independent_of_repinned_baseline` (re-pin baseline to match → ratchet STILL fires) + `::test_converted_files_membership_forward_slash_only` PASS. `python -m tools.vault_flip_prose_inventory --strict` → **exit 0** on the real converted corpus (303; 301/0/2/0; `converted_file_regressions` []; `needs_human` []).
- **Notes**: M3 ratchet-independence + forward-slash keying both pinned non-vacuous.

### AC3: pilot converted (`CLAUDE.md` + self-sufficient `agents/critique.md`) + forward-synced (CAD-1)
- **Status**: PASS
- **Evidence**: `vault_flip_prose_inventory --json` → the 2 converted files carry ONLY the 4 sanctioned carve-outs (diagnose-out ×2, slice-queue, active-folder) + 2 plain-prose definitionals; 12 operational refs are now `<vault>/`. `tools.critique_agent_drift_audit --repo-root .` → **CAD-1 clean** (agents/critique.md content-equal in-repo ≡ installed; forward-sync landed). `pytest …::test_pilot_files_zero_rewrite_at_flip_after_conversion` + `::test_agent_critique_embeds_self_sufficient_vault_note` PASS (the agent embeds the `<vault>` note at line 10, within the subagent's reading window — M-add-1).

### AC4: mixed state proven safe + seam = `architecture/` default (no pre-flip behaviour change)
- **Status**: PASS
- **Evidence**: full methodology suite **1613 passed / 2 skipped** with the 2 pilot files converted + the rest still hardcoded (coexisting correctly). `pytest …::test_seam_token_resolves_to_architecture_default` PASS (`_vault_paths.VAULT_ROOT == Path("architecture")` — code seam + prose default agree). Op-gate `--strict` **6/11/23/0 UNCHANGED** (CLAUDE.md/agents are not op-gate-scanned — B2 sidestepped).

### AC5: remainder tracked for the follow-on (complete enumerable worklist)
- **Status**: PASS
- **Evidence**: `pytest …::test_followon_remainder_worklist_complete` PASS — every un-converted `rewrite-at-flip` literal outside the pilot files is fully tagged (path/line/value). Exact remainder = **297 literals across ~24 skill files** (301 rewrite-at-flip − 4 sanctioned carve-outs in the 2 pilot files). The `bulk-convert-remaining-skills-to-vault-seam` follow-on is registered in `slice-queue.md` (Step 6.5 pick).

## Layered safety checks (VAL-1)
- **Layer A (credential scan)**: 0 secrets. **Layer B (dep hallucination)**: 0 findings (`--imports-allowlist tests`; only `hashlib`/`re`/stdlib + internal `tools.*` imports). Clean.

## Shippability catalog regression check
- **Pre-gates**: SCMD-1 / PTFCD-1 / SVW-1 all exit 0.
- **Catalog run**: `shippability_runner` → **117 rows, 117 PASS, 0 FAIL**. No past slice regressed; the new row 118 (slice-112 convention + ratchet) passes.

## Multi-instance validation
**Required?**: no (no multi-user / multi-device / multi-account surface — methodology prose + a read-only audit-tool extension).
**Result**: not-applicable

## Reality surprises
- **AP-3 build-time prose recalibration**: executing the classifier against the real corpus (not design-time reasoning) caught 2 prose-classification bugs in the NEW convention text — a "historical anchors" marker beside an in-code `diagnose-out/` → `needs-human` (exit 2), and a plain-prose `architecture/` sharing a physical line with "read/write" op-verbs → `rewrite-at-flip`. Fixed by authoring the definitional prose around the line-anchored classifier. (Captured for /reflect; reinforces AP-3.)
- **R-33 lagging-worktree**: the worktree's stale `slice-queue.md` (pre-112 `rewrite-318` candidate's bare-dir blast-radius) failed one test that PASSES on master; synced via `git checkout master -- …` (documented R-33 mitigation; not a slice regression).
- **m1 footgun (code-review)**: the plain-prose definitional exemption is fail-closed but sensitive to op-verb/backtick reword of its line — the AC3 ratchet test catches it; claim scoped in ADR-105.
