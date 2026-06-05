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
  - **Class 5 (active-folder)** — `architecture/slices/slice-NNN/…` → `<vault>/slices/slice-NNN/…` across the loop skills (now resolves external uniformly). **Prose-only** — this conversion is NOT what drains the op-gate bucket (see op-gate drain below; Critic B2).
  - **Class 6 (slice-queue)** — `architecture/slice-queue.md` → `<vault>/slice-queue.md`; `/slice` Step 6.5's "commit slice-queue.md on master" **retires** at **5 sites** in `skills/slice/SKILL.md` (≈L250, L432, L474–476, L479, L515 — FBCD-1 cross-file; the bare `git -C <main> add architecture/slice-queue.md` lines are REMOVED, not just the prose — a `git add` of a now-gitignored path warns/re-tracks; Critic M5). The queue WRITE (CAS regen + pick-log, slice-109) STAYS; only the git-commit-on-master is removed.
- **Op-gate `OP_DEFERRED_TO_FLIP` drain (AC3 = R-32.a; the genuine mechanism, Critic B2/APED-1)** — `<vault>/` prose conversion does **NOT** empty the bucket: `tools/vault_flip_prose_inventory._classify_op`'s `_ACTIVE_FOLDER_RE = re.compile(r"slices/slice-(?:\d+|NNN)")` matches `slices/slice-NNN` under BOTH `architecture/` and `<vault>/`, so all 11 deferred ops stay `DEFERRED` after conversion. The flip instead **reclassifies** post-flip active-folder writes OUT of `DEFERRED` → `OP_OUT_OF_SCOPE` (they are **per-slice, non-contended** — two worktrees never write the same slice folder — so they are SAFE as direct writes to the external store and need no CAS routing), **re-pins `_OP_CLASS_FLOOR[OP_DEFERRED_TO_FLIP]` 11→0** with a mutation-proven non-vacuity test (AP-5), and **wires `--op-gate --strict` into `/build-slice` Step 6 + `/validate-slice` pre-finish + a `shippability.md` row** (today the gate is wired into NO skill — a gate-visible bucket is sound only if a contractually-required consumer drains it, AP-12/AP-18). This is a code change to `tools/vault_flip_prose_inventory.py`, executed against the real corpus (AP-3).
- **R-32 → `retired`** in `architecture/risk-register.md` (a branch-authored vault edit the migration must carry — Critic B1).

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
- **Change**: scaffold → `<VAULT_ROOT>/slices/slice-NNN/` (external); class-4 worktree-composed paths rewritten. `/slice` Step 6.5 drops the "commit slice-queue.md on master" mechanic at **5 sites** in `skills/slice/SKILL.md` (≈L250, L432, L474–476, L479, L515 — Critic M5; the bare `git add architecture/slice-queue.md` lines REMOVED, not just prose) — the CAS queue WRITE + pick-log (slice-109) stay; only the git-commit-on-master goes.

### `tools/vault_flip_prose_inventory.py` (modified — the AC3 R-32.a drain, Critic B2)
- **Responsibility**: the op-gate (`OP_DEFERRED_TO_FLIP`) + carve-out inventory ratchet.
- **Change**: reclassify post-flip active-folder writes OUT of `DEFERRED` → `OP_OUT_OF_SCOPE` (per-slice non-contended ⇒ safe direct external writes); re-pin `_OP_CLASS_FLOOR[OP_DEFERRED_TO_FLIP]` 11→0 with a mutation-proven non-vacuity test; re-pin the converted-prose ratchet for classes 4–6. Wire `--op-gate --strict` into `/build-slice` Step 6 + `/validate-slice` pre-finish + a `shippability.md` row (no skill consumes the gate today).

### `skills/commit-slice/SKILL.md` + `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: the parallel-slice merge/rebase conflict resolver.
- **Change**: a `vault_is_external` guard documents + short-circuits the SOFT/VAULT_CLAIM vault-file regeneration (no-op post-flip — the vault files are untracked). PSQ-3 rebase + HARD code-file resolution unchanged.

### Loop skills carrying class-5/6 prose (modified, mechanical)
- `reflect`, `archive`, `validate-slice`, `critique`, `design-slice`, `pulse`, `supersede-slice`, `drift-check`, `commit-slice` + agent `code-review.md`: `architecture/slices/…` / `architecture/slice-queue.md` → `<vault>/…`, re-pinned in `vault_flip_prose_inventory`'s converted-file ratchet.

## The flip sequence (the self-referential bootstrap)

slice-115 is the **first slice to live through the flip**. Executed during `/build-slice` (in the slice-115 worktree); ordering is load-bearing. `<main>` = main tree root, `<wt>` = slice-115 worktree, `<external>` = `~/.aisdlc/<project-hash>`. The git-common-dir is **shared** by `<main>` + `<wt>`, so the config + hash are identical from either tree.

0. **Quiesce precondition (Critic M3 — architectural concurrency)**: the flip requires **zero other in-flight `slice/*` branches** at flip time — a branch that predates the untrack would re-introduce tracked `architecture/` at its own `/commit-slice --merge` (silently un-doing the flip) AND its in-tree vault writes would never reach the external store. Guard: `git branch --list 'slice/*'` minus `slice/115` MUST be ∅ (or a documented manual quiesce: each must be rebased onto post-flip master before merge). Currently satisfiable — the slice-115 `stranded_slice_audit` at `/slice` was clean. STOP if a sibling slice is in-flight.
1. **Code changes first** (prose rewrites, `_vault_flip.py`, the `vault_is_external` guard, the op-gate reclassification + floor re-pin + wiring, tests) — written + committed on `slice/115` while the vault is still in-tree, so the suite can exercise the *flipped-resolution* path via the slice-110 location-agnostic fixtures BEFORE the physical move.
2. **Compute `<external>`** via `_vault_flip` (base `~/.aisdlc` — defaulting when `~/.claude/ai-sdlc-vault-base` is absent, per Error model — + bounded hash of canonical common-dir). Off-OneDrive/AV (C3).
3. **Rebase `slice/115` onto master FIRST**, then **migrate the ENTIRE branch `architecture/` tree** → `<external>/` byte-faithfully (no EOL churn). The rebase brings the `chore(queue): pick slice-115` commit current so the branch's `architecture/` is a strict **superset** of master; migrating the *whole branch tree* (NOT master + a single slice-folder overlay) is load-bearing — it captures every branch-authored vault file that lives OUTSIDE `slices/slice-115/`: **`decisions/ADR-107`**, the R-32-retired `risk-register.md` edit, any `lessons-learned.md` append (Critic B1). The external store now = the complete current vault.
4. **Write config** `$GIT_COMMON_DIR/aisdlc/vault-root` = `<external>`. Both trees now resolve `VAULT_ROOT` external; `vault_is_external` → `True`.
5. **git-untrack** on `slice/115`: `git rm -r --cached architecture/` + add `architecture/` to `.gitignore`; commit. Physically remove the now-orphan `<wt>/architecture/` (content safe in `<external>`).
6. **Post-flip artifacts go external**: `/validate-slice` → `<external>/slices/slice-115/validation.md`; `/reflect` → `<external>/…/reflection.md`; archival → in-store move to `<external>/slices/archive/slice-115/`. The active folder ends up **complete** in the external store (AC4 self-archival live-fire = Charter 3).
7. **Main-tree orphan cleanup** is a `/commit-slice --merge` concern: after the no-ff merge lands "architecture/ untracked + gitignored" on master, the main tree's physical `architecture/` is a gitignored orphan → remove it (content is in `<external>`). Documented in build-log; not done before merge (main's index still tracks it pre-merge).

**Invariant**: at no point is the vault’s only copy in flight. Migrate (copy) → **verify the FULL file set byte-faithfully** → only then untrack/remove the in-tree copy. The verify is a **complete manifest hash walk** (Critic B3): enumerate every source file under the branch `architecture/` tree, assert destination file-**COUNT** equality AND **per-file SHA-256** match — NOT a 3-file sample (a sample passes a partial-copy failure — interrupted `shutil`, a MAX_PATH overflow on a deep archive folder, an AV-locked handle — and then deletes the unsampled originals). `_vault_flip` returns the manifest; ANY count delta or hash mismatch STOPs before any delete (mid-slice smoke gate). A 3-file spot-check MAY run first as a fast fail, but the gate is the full manifest.

## Wiring matrix

Per **WIRE-1**. Every new module declares a consumer entry point + consumer test, or an exemption.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_vault_flip.py` | `skills/build-slice/SKILL.md` (the flip step) + `/commit-slice` rollback hint | `tests/methodology/test_vault_flip.py::test_flip_then_rollback_roundtrip` (fixture-repo seeded with a `decisions/ADR-XXX.md` + a non-slice-folder vault file + nested archive folders: flip → assert external resolves + **file-COUNT equality + per-file hash** + the ADR survives + untracked → rollback → assert COMPLETE in-tree set restored — non-vacuous against Critic B1/B3/m2) `+ ::test_absent_base_defaults` (absent `ai-sdlc-vault-base` ⇒ `~/.aisdlc`, not STOP — Critic M1) | — |

(The prose rewrites + the `vault_is_external` guard + the op-gate reclassification/floor-re-pin modify existing files — no new module rows; their non-vacuity proofs live in the existing tools' test files.)

## Decisions made (ADRs)

- [[decisions/ADR-107]] — Flip the vault to an external shared store (Option A: whole vault external; plain directory, no independent git history); partial-supersedes [[decisions/ADR-090]] (BRANCH-3 vault-artifact-in-worktree-tracking → vault artifacts follow `VAULT_ROOT` external) and consumes [[decisions/ADR-089]]'s `/commit-slice` vault-conflict RETIRE. — reversibility: **cheap** (scripted `_vault_flip` rollback; no data loss).

## Authorization model for this slice

Not a security boundary (ADR-085 §"NOT a security boundary; cooperative-model scope"). The external store is a local user-owned directory; the only "authorization" is filesystem ownership. No auth/authz surface is added.

## Error model for this slice

Fail-visible everywhere (R-7 class — never a silent skip):
- **Base resolution** (Critic M1 — `~/.claude/ai-sdlc-vault-base` is ABSENT on this build machine; adopted 2026-05-13, pre-ADR-085 install-enhancement): an absent base file is the **NORMAL** path → **default to `~/.aisdlc`** (the documented default; silent, do NOT STOP). STOP loudly **only** when the *resolved* base path is unwritable, on OneDrive, or in an AV-aggressive location (ADR-085 C3) — or when the git-common-dir is unreadable. The reused-component note (§What's reused) and this bullet agree: absent file ⇒ default, not STOP.
- **Migration verify mismatch** (the FULL manifest hash walk — count delta or ANY per-file SHA-256 mismatch, not a sample) → STOP before any untrack/delete; the in-tree vault is untouched (Invariant above).
- **Config write failure** → STOP; the move already happened, so surface the exact `aisdlc/vault-root` path to write by hand + the rollback command.
- **Partial flip** (move done, untrack not) → `_vault_flip --rollback` restores the in-tree state idempotently; the mid-slice smoke gate catches a half-flip.
- **`vault_is_external` guard in `/commit-slice`** → if a stale tracked vault copy somehow lingers, the guard short-circuits regeneration (no-op) rather than rewriting an external file; logged, not silent.
