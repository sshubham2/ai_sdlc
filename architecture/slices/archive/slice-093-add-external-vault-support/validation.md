# Validation: Slice 093 add-external-vault-support

**Date**: 2026-05-31
**Result**: PASS

## Per-criterion results

### AC1: `_vault_paths.py` resolves env → git-common-dir config → `architecture/` default; default UNCHANGED
- **Status**: PASS
- **Evidence** (live):
  - default (no env/config): `VAULT_ROOT = architecture` — the no-flip safety contract holds.
  - env override `AI_SDLC_VAULT_ROOT=X:/ext-vault`: `VAULT_ROOT = X:\ext-vault`.
  - git-common-dir keying byte-identical across main + THIS worktree: both `C:/Users/sshub/ai_sdlc/.git` (C1 — the spike's central claim, re-confirmed live).
  - tests: `test_resolution_precedence_env_over_pointer_over_default`, `test_default_unchanged_when_no_env_no_pointer`, `test_git_common_dir_key_stable_across_main_and_worktree`, `test_vault_paths_module_is_leaf` — all PASS.
- **Notes**: leaf-purity preserved; the M1 fix makes import cp1252-safe on non-ASCII paths.

### AC2: concurrent-write/append-safe helper; no lost-update under concurrency + (mocked) EPERM
- **Status**: PASS
- **Evidence**: `test_vault_safe_write.py` **7 PASS** — concurrent whole-file writers (final == one complete payload, no torn write), concurrent appenders (all 30 lines survive — the append-log class), mocked-EPERM retry + budget-exhaustion, reader-parity, + the cp1252-import + append-EPERM regression tests. The code-Critic empirically confirmed the lock is load-bearing (pure `O_APPEND` loses 26/30 lines without it).

### AC3: INSTALL.md writes ONLY the global base config; `architecture/` untouched
- **Status**: PASS
- **Evidence**: `test_install_vault_config.py` **2 PASS** — base config written with the chosen value; a pre-existing `architecture/` sentinel byte-identical afterward (capability only, no move). INSTALL.md Step 3i documents the prompt + write via `_vault_write`.

### AC4: classification map documented; allowlist UNCHANGED at 10
- **Status**: PASS
- **Evidence**: live count `VAULT_ROOT importers = 10` (unchanged); `test_no_new_tool_migration_and_classification_map_documented` PASS; design.md §Tool-migration classification map present (a/b/c classes).

### AC5: R-32 registered + ADR-085 extends ADR-065 + full suite + audits green
- **Status**: PASS
- **Evidence**: `risk_register_audit` shows R-32 (status `mitigating`); ADR-085 `supersedes: null` extends ADR-065 (`test_r32_registered_and_adr_extends_065` PASS); full suite **1316 PASS**; 16 Step-6 audits + DCE-1 + BC-1-strict green.

## VAL-1 layered safety (Step 5b)
- Layer A (credentials): **0 secrets**. Layer B (dependency hallucination): **0 findings** (all imports stdlib / internal `tools` / `tests` allowlist). Clean.

## Walking-skeleton (WS-1) / Exploratory-charter (ETC-1)
- Not applicable — mission-brief flags both `false`; audits no-op.

## Multi-instance validation
- **Required?**: no (not a multi-user/device feature). The git-common-dir keying IS a multi-worktree concern; validated live (main + worktree key byte-identical) + by `test_git_common_dir_key_stable_across_main_and_worktree` (real `git worktree add` fixture).
- **Result**: PASS (worktree keying).

## Shippability catalog regression check (Step 5.5)
- SCMD-1 decoupling audit: clean (99 rows). PTFCD-1 path audit: clean (444 tokens). Runner: **99 rows, 99 PASS, 0 FAIL**. No regression introduced by slice-093.

## Reality surprises
- **R-20 diagnose-out seed gap** — worktree-at-`/slice` (this slice's own dogfooded model) skips `/build-slice`'s `cp -r diagnose-out` seed, surfaced live at the mid-slice smoke gate (`test_bcr_1_sc054_round_trip_inputs_invariant`). A worktree-setup artifact, not a code defect; **evidence the broader initiative must move the R-20 seed to `/slice` time** (→ slice-094+).
- **code-review M1** — the observability `print` introduced a cp1252 import-crash (the repo's own documented footgun); caught + fixed. The three-Critic stack each caught its own distinct defect class (design: path + append; meta: fix-residual; code: cp1252-crash).
