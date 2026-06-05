# Design: Slice 115 flip-vault-to-external-store

**Date**: 2026-06-05
**Mode**: Standard

> The capstone of the external-shared-vault initiative (slices 093→114). This is the **physical move** — the sole residual to retire R-32. Decisions below were settled with the user at `/design-slice` Step 2: **Option A (whole vault external)** + **plain external directory (no independent git history)**.

## What's new

- **`tools/_vault_flip.py`** (new underscore internal helper) — the flip + rollback engine: computes the external store path, faithfully migrates `architecture/` → the external store, writes the git-common-dir config, and provides a scripted **rollback** (the inverse). Underscore-prefixed → auto-excluded from PMI-1 inventory (the `_vault_paths` / `_vault_write` / `_vault_git` / `_worktree_paths` precedent — no `plugin.yaml` / `install_audit` churn). Justified by the **tested-reversibility must-not-defer**: a scripted rollback cannot be unit-tested if the flip is ad-hoc build prose.
- **The flip itself** (one-time operation, executed during `/build-slice`): write `$GIT_COMMON_DIR/aisdlc/vault-root` = absolute external path; move `architecture/` → `~/.aisdlc/<project>/`; `git rm -r --cached architecture/` + add `architecture/` to `.gitignore`.
- **`/commit-slice` vault-conflict RETIRE** — a `vault_is_external` guard that short-circuits PCR's SOFT/VAULT_CLAIM vault-file regeneration (documented no-op; the files are no longer tracked, so they cannot be rebase U-files). PSQ-3 rebase + HARD *code*-file resolution stay live.
- **Carve-out prose rewrite (classes 4–6)** — the references slices 112–114 deliberately kept concrete because their resolution *was this flip*:
  - **Class 4 (worktree-composed)** — `/slice` Step 5.5/6 + `/build-slice` write the slice scaffold to `<VAULT_ROOT>/slices/slice-NNN/` (external), no longer `<wt>/architecture/slices/…`. **Behavioral**, not just textual.
  - **Class 5 (active-folder)** — `architecture/slices/slice-NNN/…` → `<vault>/slices/slice-NNN/…` across the loop skills (now resolves external uniformly).
  - **Class 6 (slice-queue)** — `architecture/slice-queue.md` → `<vault>/slice-queue.md`; `/slice` Step 6.5's "commit slice-queue.md on master" **retires** (the queue is external/untracked; the CAS-mediated write per slice-109 stays).
- **R-32 → `retired`** in `architecture/risk-register.md`.

## What's reused

- **`tools/_vault_paths.py`** — `VAULT_ROOT` 3-tier resolution (env → `$GIT_COMMON_DIR/aisdlc/vault-root` config → default `architecture/`). The flip writes tier-2's config; **no code change** to resolution (slice-093/[[decisions/ADR-085]]).
- **`tools/_vault_git.py`** — `vault_is_external(repo_root)` (slice-098/[[decisions/ADR-089]]) gates the `/commit-slice` retire; `vault_pathspec_is_tracked` available if needed.
- **`tools/_vault_write.py`** — `safe_write_text` / `safe_append_text` / `safe_rewrite_text` (slices 094/097) + the post-flip queue CAS (slice-109/[[decisions/ADR-098]]) — the write-safety substrate the external store relies on.
- **`tools/vault_edit.py`** — `move` resolves both endpoints under one `VAULT_ROOT` ([[decisions/ADR-103]]). Under Option A this is automatically coherent: active `slices/slice-NNN/` AND `slices/archive/` are both external → archival is an in-store move (**R-32.b dissolves**, the design rationale for choosing A).
- **`tools/_worktree_paths.py`** — unchanged; computes the worktree *root* (code isolation). The vault is no longer under the worktree.
- **`tools/vault_flip_prose_inventory.py`** — `--op-gate` (`OP_DEFERRED_TO_FLIP`) and `--strict` (carve-out inventory). The flip drives `OP_DEFERRED_TO_FLIP` → ∅ and re-pins the converted-prose ratchet (classes 4–6 now convert to `<vault>/`).
- ADR-085 §Install enhancement — base location default `~/.aisdlc`, stored at `~/.claude/ai-sdlc-vault-base`; per-project subdir = bounded hash of the canonicalized git-common-dir (MAX_PATH-safe).

## Components touched

### `tools/_vault_flip.py` (new)
- **Responsibility**: compute the external store path; migrate `architecture/` → external byte-faithfully; write the git-common-dir config; provide the scripted inverse (rollback). Single tested home for the flip's reversibility.
- **Lives at**: `tools/_vault_flip.py` (created by this slice)
- **Key interactions**: reads `~/.claude/ai-sdlc-vault-base` (base, default `~/.aisdlc`); `git rev-parse --path-format=absolute --git-common-dir` (config location + hash seed, the C1 keying); stdlib `shutil` / `hashlib` / `pathlib`. Stays a stdlib leaf (no `tools.*` import beyond `_stdout`), mirroring `_vault_paths` leaf-purity.

### `skills/slice/SKILL.md` + `skills/build-slice/SKILL.md` (modified)
- **Responsibility**: where the slice scaffold + downstream artifacts are written.
- **Change**: scaffold → `<VAULT_ROOT>/slices/slice-NNN/` (external); `/slice` Step 6.5 drops the "commit slice-queue.md on master" step (queue is external). Class-4 worktree-composed paths rewritten.

### `skills/commit-slice/SKILL.md` + `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: the parallel-slice merge/rebase conflict resolver.
- **Change**: a `vault_is_external` guard documents + short-circuits the SOFT/VAULT_CLAIM vault-file regeneration (no-op post-flip — the vault files are untracked). PSQ-3 rebase + HARD code-file resolution unchanged.

### Loop skills carrying class-5/6 prose (modified, mechanical)
- `reflect`, `archive`, `validate-slice`, `critique`, `design-slice`, `pulse`, `supersede-slice`, `drift-check`, `commit-slice` + agent `code-review.md`: `architecture/slices/…` / `architecture/slice-queue.md` → `<vault>/…`, re-pinned in `vault_flip_prose_inventory`'s converted-file ratchet.

## The flip sequence (the self-referential bootstrap)

slice-115 is the **first slice to live through the flip**. Executed during `/build-slice` (in the slice-115 worktree); ordering is load-bearing. `<main>` = main tree root, `<wt>` = slice-115 worktree, `<external>` = `~/.aisdlc/<project-hash>`. The git-common-dir is **shared** by `<main>` + `<wt>`, so the config + hash are identical from either tree.

1. **Code changes first** (prose rewrites, `_vault_flip.py`, the `vault_is_external` guard, tests) — written + committed on `slice/115` while the vault is still in-tree, so the suite can exercise the *flipped-resolution* path via the slice-110 location-agnostic fixtures BEFORE the physical move.
2. **Compute `<external>`** via `_vault_flip` (base `~/.aisdlc` + bounded hash of canonical common-dir). Off-OneDrive/AV (C3).
3. **Migrate** the canonical vault → `<external>`: the **main tree's** `architecture/` is the current shared surface (it holds the `chore(queue): pick slice-115` update the worktree branched *before*). Copy `<main>/architecture/*` → `<external>/` byte-faithfully (no EOL churn), THEN overlay this slice's active scaffold + in-worktree artifacts (`<wt>/architecture/slices/slice-115/`) → `<external>/slices/slice-115/`. The external store now = master-tip shared vault + slice-115 active folder.
4. **Write config** `$GIT_COMMON_DIR/aisdlc/vault-root` = `<external>`. Both trees now resolve `VAULT_ROOT` external; `vault_is_external` → `True`.
5. **git-untrack** on `slice/115`: `git rm -r --cached architecture/` + add `architecture/` to `.gitignore`; commit. Physically remove the now-orphan `<wt>/architecture/` (content safe in `<external>`).
6. **Post-flip artifacts go external**: `/validate-slice` → `<external>/slices/slice-115/validation.md`; `/reflect` → `<external>/…/reflection.md`; archival → in-store move to `<external>/slices/archive/slice-115/`. The active folder ends up **complete** in the external store (AC4 self-archival live-fire = Charter 3).
7. **Main-tree orphan cleanup** is a `/commit-slice --merge` concern: after the no-ff merge lands "architecture/ untracked + gitignored" on master, the main tree's physical `architecture/` is a gitignored orphan → remove it (content is in `<external>`). Documented in build-log; not done before merge (main's index still tracks it pre-merge).

**Invariant**: at no point is the vault’s only copy in flight. Migrate (copy) → verify byte-faithful (hash sample of `_index.md` / `risk-register.md` / an ADR) → only then untrack/remove the in-tree copy. A failed verify STOPs before any delete (mid-slice smoke gate).

## Wiring matrix

Per **WIRE-1**. Every new module declares a consumer entry point + consumer test, or an exemption.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_vault_flip.py` | `skills/build-slice/SKILL.md` (the flip step) + `/commit-slice` rollback hint | `tests/methodology/test_vault_flip.py::test_flip_then_rollback_roundtrip` (fixture-repo: flip → assert external resolves + byte-faithful + untracked → rollback → assert in-tree resolution restored) | — |

(The prose rewrites + the `vault_is_external` guard modify existing files — no new module rows. The op-gate / inventory re-pins are existing-tool edits.)

## Decisions made (ADRs)

- [[decisions/ADR-107]] — Flip the vault to an external shared store (Option A: whole vault external; plain directory, no independent git history); partial-supersedes [[decisions/ADR-090]] (BRANCH-3 vault-artifact-in-worktree-tracking → vault artifacts follow `VAULT_ROOT` external) and consumes [[decisions/ADR-089]]'s `/commit-slice` vault-conflict RETIRE. — reversibility: **cheap** (scripted `_vault_flip` rollback; no data loss).

## Authorization model for this slice

Not a security boundary (ADR-085 §"NOT a security boundary; cooperative-model scope"). The external store is a local user-owned directory; the only "authorization" is filesystem ownership. No auth/authz surface is added.

## Error model for this slice

Fail-visible everywhere (R-7 class — never a silent skip):
- **Base/path unresolvable** (`~/.claude/ai-sdlc-vault-base` absent / common-dir unreadable) → STOP loudly with the resolved values; do not guess a path.
- **Migration verify mismatch** (byte-faithful hash-compare fails on any sampled file) → STOP before any untrack/delete; the in-tree vault is untouched (Invariant above).
- **Config write failure** → STOP; the move already happened, so surface the exact `aisdlc/vault-root` path to write by hand + the rollback command.
- **Partial flip** (move done, untrack not) → `_vault_flip --rollback` restores the in-tree state idempotently; the mid-slice smoke gate catches a half-flip.
- **`vault_is_external` guard in `/commit-slice`** → if a stale tracked vault copy somehow lingers, the guard short-circuits regeneration (no-op) rather than rewriting an external file; logged, not silent.
