---
id: ADR-085
title: External-shared-vault resolution (git-common-dir config) + concurrent-write-safety contract; extends ADR-065
date: 2026-05-31
slice: slice-093-add-external-vault-support
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-085: External-shared-vault resolution via git-common-dir config + concurrent-write-safety contract

> Extends [[ADR-065]] (the `VAULT_ROOT` seam). Does NOT supersede it — ADR-065's env-override seam + read-at-import/consumer-freeze semantics stay accepted; this ADR adds a per-project external-resolution layer, a write-safety contract, and records the initiative's direction.

## Context

The user's initiative (see `architecture/slices/slice-093-add-external-vault-support/mission-brief.md` + `architecture/spikes/spike-external-shared-vault.md`): relocate the vault (`architecture/`) + `diagnose-out/` to a **shared external, per-project location** (`~/.aisdlc/<project>/`) so all concurrent slice worktrees resolve ONE live vault view — eliminating the `_index.md`/`risk-register.md`/`slice-queue.md` merge-conflict class structurally.

ADR-065 §Consequences anticipated a vault relocation — but as `rename-architecture-to-sdlc-and-track-in-git` (rename + keep **git-tracked**, share cross-machine via git). The direction has since evolved to **external + untracked** (share via filesystem, not git). That evolution is load-bearing: an untracked vault has **no git conflicts**, which is what makes the relocation kill the conflict class — and also what obsoletes the PCR (`tools/parallel_conflict_resolver.py`) machinery for vault files (it resolves git-stage conflicts on `architecture/slice-queue.md`/`shippability.md` via pathspecs that only exist while the vault is tracked).

The spike (CONDITIONAL/GO) verified empirically: `git rev-parse --path-format=absolute --git-common-dir` is byte-identical across the main tree + a real linked worktree (the stable per-project key); external-root reads + `graphify vault` + audits work. It also surfaced the dominant hazard: a shared **mutable** store converts a loud git merge-conflict into a **silent** Windows lost-update / atomic-rename-EPERM corruption (the `.claude.json`/OneDrive class).

This slice (093) is the **capability cut**: ship the resolution + write-safety + install machinery with the **default unchanged at `architecture/`** (no flip). The flip is slice-094.

## Options considered

1. **Per-project path stored in the git-common-dir** (`$GIT_COMMON_DIR/aisdlc/vault-root`), read inline by `_vault_paths` (THIS ADR). Pros: shared identically across all worktrees of a repo (common-dir is shared — spike-verified); never git-tracked (inside `.git/`); honors a user-chosen location; keeps `_vault_paths` a stdlib leaf. Cons: adds a `git rev-parse` subprocess at `_vault_paths` import when the env var is unset.
2. **Committed repo-root pointer file** (`.aisdlc.toml`). Pros: explicit/greppable. Cons: adds a *tracked* file (contradicts the untracked spirit) + a parser; a committed absolute path is machine-specific.
3. **Pure runtime derivation** (`~/.aisdlc/<sha1(common-dir)>`), no config. Pros: zero config to write/lose. Cons: cannot honor a **user-chosen** location (the user explicitly wants an install prompt, default `~/.aisdlc`).
4. **Env var only** (status quo). Cons: relies on the env var reaching every subprocess; the freeze-cascade + "env-var-forgetting" hazard the spike flagged.
5. **Junction/symlink the external vault into each worktree.** Cons: symlinks need Windows admin/Developer-Mode (deployment footgun); a link inside the worktree re-introduces an in-repo path `git status`/realpath sees. Absolute-path-config avoids both; no source calls it an anti-pattern.

## Decision

Adopt **option 1**, layered on ADR-065's env seam:

- **Resolution precedence** in `tools/_vault_paths.py`: `AI_SDLC_VAULT_ROOT` env → `$(git rev-parse --path-format=absolute --git-common-dir)/aisdlc/vault-root` config (single-line absolute path) → default `Path("architecture")`. **Default unchanged** — backward-compatible; this repo, with no config, resolves to `architecture/` exactly as today.
- **Keying (C1)**: always `--path-format=absolute --git-common-dir` (NEVER bare — relative-in-main footgun); never hand-join `$GIT_DIR` (the vscode#297786 / claude-code#39920 bug class). The user-facing per-project dir default is `~/.aisdlc/<project>` with `<project>` a **bounded hash** of the canonicalized common-dir (direnv pattern; MAX_PATH safety).
- **Leaf-purity preserved**: all resolution is stdlib (`subprocess`/`pathlib`/`os`) inline in `_vault_paths`; it imports no `tools.*` (the `test_vault_paths_module_is_leaf` invariant holds). The `git rev-parse` runs only when the env var is unset, once per process at import.
- **Concurrent-write/append-safety contract (C2 / R-32)**: a new leaf `tools/_vault_write.py` provides `safe_write_text` (sidecar-`.lock` + temp-write + atomic `os.replace` + bounded EPERM-retry — for whole-file vault files) AND `safe_append_text` (`O_APPEND`/`FILE_APPEND_DATA` + lock — for append-only vault files: ADRs, `risk-register.md`, `_index.md`, the PCR audit log; whole-file atomic-replace does NOT close the append read-modify-write lost-update window — field-recon names this distinctly). The lock is a per-file **sidecar `.lock`**, never the replace target (Windows `msvcrt.locking`→`LockFileEx` is *mandatory*, so locking the target would block its own `os.replace`). Together these are the **structural replacement for PCR-on-vault-files** once the flip removes git-conflict resolution — covering both PCR's whole-file edits (`slice-queue.md`/`shippability.md`) AND its append log.
- **Install enhancement**: `INSTALL.md` prompts for the base location (default `~/.aisdlc`), stored at `~/.claude/ai-sdlc-vault-base`.
- **Direction accepted (user-confirmed at /design-slice)**: the external-untracked-vault end-state **retires PCR-for-vault-files at the slice-094 flip**, with `_vault_write` as its replacement. 093 migrates NO additional tools; it documents the migration-classification map (`design.md` §Tool-migration classification map) so 094 has the (a) FS-path / (b) git-model-coupled-rethink / (c) never-migrate split.
- **Fail-visible resolution (R-7)**: no-git/not-a-repo/config-absent → silent `architecture/` default (intended). Config present-but-malformed → stderr WARN + default; never a silent mis-resolve.

## Consequences

- **R-32 registered** (concurrent-write lost-update / atomic-rename-EPERM on a shared mutable vault). `_vault_write` is its mitigation; R-32 stays open/mitigating until the flip exercises it under real parallel writers.
- **PCR-for-vault-files is on a retirement path.** `tools/parallel_conflict_resolver.py` (+ the PCR-N rule family across slices 082–085/091) loses its purpose once vault files are untracked. This is a deliberate, accepted consequence — recorded here, *decided/executed* at slice-094. Until then PCR is untouched and fully functional (093 does not flip).
- **`pulse_worktree_resolver.py` + `stranded_slice_audit.py` are also worktree-model-coupled** and will need rethinking at the flip (no per-worktree `architecture/` once shared). Documented in the classification map.
- **`_vault_paths` now shells out to git once per process** (when env unset). Tolerable (~once-per-process); defensive on failure.
- **Install gains a per-machine base-location config** (`~/.claude/ai-sdlc-vault-base`) — a precedent for future `AI_SDLC_*` install-time prefs.
- **No new public tool** — `_vault_write` is an underscore leaf (no PMI-1/`install_audit` count bump; avoids the new-tool fan-out).
- **slice-094 (the flip)** becomes: flip `_DEFAULT`/wire the config, rewrite SKILL.md prose, physically move `architecture/`+`diagnose-out/`, retire/rethink the (b)-class tools, decide history (C5), wire `/triage`+`/adopt`.

## Reversibility

**Cheap.** Revert path: (1) delete `tools/_vault_write.py`; (2) revert the resolution-precedence block in `tools/_vault_paths.py` back to the bare env-or-default (ADR-065 state); (3) revert the `INSTALL.md` step; (4) delete `tests/methodology/test_vault_safe_write.py` + the extended `test_vault_root_constant.py` rows; (5) leave R-32 noted or mark accepted. No persistent schema, no API contract, no data migration — the only persisted state is two single-line config files that are absent by default. `git revert` of the slice-093 commit handles it atomically. The PCR-retirement *direction* is a statement, not a locked irreversible change — slice-094 can still choose otherwise.
