# Slice 106: route-project-frame-synth-via-vault-root

**Mode**: Standard
**Estimated work**: 0.5 day (SMALL)
**Risk retired**: contributes to [[risk-register#R-32]] flip-readiness — takes the vault-flip production silent-breakage surface from 4 → 0 `must-rewrite` sites (does NOT retire R-32; R-32 retires at the flip itself, M4)
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

`tools/project_frame_synth.py` is the **sole remaining `[production]` `must-rewrite` file** flagged by `tools/vault_flip_readiness_audit.py`: four sites construct vault paths with a hardcoded `repo_root / "architecture" / …` literal (concept.md, triage.md, slice-queue.md, risk-register.md) instead of routing through the `tools/_vault_paths.VAULT_ROOT` seam (ADR-065 / slice-068 / slice-093). The moment the external-shared-vault flip relocates `architecture/`, those four reads silently mis-resolve. This slice routes all four through `VAULT_ROOT`, taking the production `must-rewrite` set to **0** — the immediate M1 prerequisite that unblocks the external-vault flip roadmap. Default `VAULT_ROOT == Path("architecture")`, so there is **zero behavior change on this repo today**; the file simply becomes flip-ready.

## Acceptance criteria

1. All four vault-path constructions in `tools/project_frame_synth.py` (the `concept.md` / `triage.md` / `slice-queue.md` / `risk-register.md` reads at ~L121/L122/L185/L194) resolve through `tools/_vault_paths.VAULT_ROOT`; no bare `"architecture"` path-construction literal remains in the file.
2. `python -m tools.vault_flip_readiness_audit` reports **0** `[production] must-rewrite`; the in-module `_BASELINE` tuple (`tools/vault_flip_readiness_audit.py`) and `tests/methodology/test_vault_flip_readiness_audit.py::test_must_rewrite_baseline_pinned` are updated to the new empty production `must-rewrite` set, and `--strict` exits 0 (no baseline drift).
3. `python -m tools.project_frame_synth` produces **byte-identical** output on this repo before vs. after the change (default `VAULT_ROOT == architecture` ⇒ pure no-op today).
4. `project_frame_synth.py` joining `_MIGRATION_SITE_ALLOWLIST` brings it under the **existing** slice-068 guards (`test_migration_site_allowlist_pinned` + `test_no_orphan_architecture_literal_in_migrated_tools`), which red if a future edit drops the `VAULT_ROOT` import or reintroduces a hardcoded `"architecture"` path-construction — proven **non-vacuous by mutation** (AP-5: revert one routed site → orphan-literal test reds). No new test file is introduced (reconciled with design per /critique M1).
5. Full methodology suite green; `architecture/shippability.md` unregressed. **No new catalog row** is added (no new test file per AC4; the existing slice-068 row that runs `test_vault_root_constant.py` already covers the extended guard set — RPCD-1/SCPD-1 satisfied by the existing consumer reference). The B1 rework of `test_emits_classified_inventory_with_evidence` is what keeps the slice-100/102 readiness rows green when production must-rewrite → 0.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | 4 sites routed | `python -m tools.vault_flip_readiness_audit --json` shows no `project_frame_synth.py` entry under `must-rewrite`; visual read of the 4 sites |
| 2 | production must-rewrite = 0 + baseline re-pinned | `python -m tools.vault_flip_readiness_audit` summary line reads `[production] 0 must-rewrite`; `--strict` exits 0; `pytest tests/methodology/test_vault_flip_readiness_audit.py` green |
| 3 | behavior-preserving no-op | capture `python -m tools.project_frame_synth …` stdout pre-change (on `master`) and post-change; assert byte-identical |
| 4 | regression pin non-vacuous | mutate one routed site back to `"architecture"` → AC4 test FAILS; revert → PASSES |
| 5 | suite + shippability | `python -m tools.shippability_runner` (or `/validate-slice`) green; new catalog row present |

## Must-not-defer

- [ ] `_BASELINE` re-pin (AC2): the 4 `project_frame_synth` entries MUST be removed from the in-module baseline tuple + the pinned test, else `--strict` reports baseline drift and the suite reds.
- [ ] Behavior-preservation proof (AC3): the routing MUST be a pure no-op under the default `VAULT_ROOT`; do not change `synthesize_frame`'s observable output.
- [ ] Mutation-proof of the AC4 regression test (AP-5): a test that passes on already-correct code proves nothing.
- [ ] No silent fallback: consume the existing `_vault_paths` seam only; if `VAULT_ROOT` resolution ever fails, surface it — do not swallow into a hardcoded `"architecture"`.

## Out of scope

- The **prose** surface (~285 `SKILL.md`/`agents`/`CLAUDE.md`/`INSTALL.md` literals) — that is the parallel slice-107 `inventory-vault-flip-prose-surface` (M1 sibling).
- The **tests** surface (154 update-at-flip + 49 pathspec, inventoried at slice-102) — a later M2 routing slice.
- The **flip itself** (M4): physical move of `architecture/` + `diagnose-out/`, flipping the `VAULT_ROOT` default, `git rm --cached`, final prose.
- Any change to `tools/_vault_paths.py` resolution logic — this slice **consumes** the seam, it does not modify it.

## Dependencies

- Prior slices: [[slice-068-add-vault-root-constant]] (the `VAULT_ROOT` seam) — what we route through; [[slice-093-add-external-vault-support]] (capability/no-flip contract); [[slice-100-add-vault-flip-readiness-audit]] (the `_BASELINE` pin we re-pin); [[slice-102-vault-flip-readiness-tests]] (production-surface baseline filter).
- Vault refs: [[decisions/ADR-065]] (env/seam), [[decisions/ADR-091]] (readiness classification model + the ≥4 `project_frame_synth` `must-rewrite` sites called out in §Consequences).
- Risk register: [[risk-register#R-32]] (concurrent-write / flip gate — this slice clears one of its production preconditions).

## Mid-slice smoke gate

At ~50% (after routing the 4 sites, before re-pinning baseline + tests):
```
python -m tools.vault_flip_readiness_audit          # expect: [production] 0 must-rewrite
python -m tools.project_frame_synth <same args>     # expect: output unchanged vs master
```
Expected: production `must-rewrite` drops to 0 AND `project_frame_synth` output is byte-identical. If either fails: STOP, diagnose (a non-no-op routing or a missed/extra site), don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
