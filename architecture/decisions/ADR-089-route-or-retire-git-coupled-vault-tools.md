---
id: ADR-089
title: Route Class-A filesystem vault paths in the 3 git-coupled tools through VAULT_ROOT; RETIRE-when-external (fail-visible, gated on a store-location vault_is_external check) the Class-B git-string vault-content reads; KEEP git ops on tracked slice/* refs
date: 2026-06-01
slice: slice-098-route-or-retire-git-coupled-vault-tools
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-089: Route-or-retire the git-coupled vault tools for external-vault readiness

## Context

The external-shared-vault initiative ([[ADR-065]] → [[ADR-085]]) relocates the vault from the git-tracked `architecture/` directory to a shared, **untracked** external store. Slices 094/095/097 closed all three R-32 write-safety sub-classes, so the flip is unblocked on write-safety. The last capability piece is the 3 tools slice-093 AC4 explicitly deferred as "rethought at the flip, not naively migrated": `parallel_conflict_resolver.py`, `stranded_slice_audit.py`, `pulse_worktree_resolver.py`.

These tools couple to the vault in **two structurally distinct ways** (the r1 design of this slice mis-modelled the coupling as one — caught by `/critique` B1/M4):

- **Class A — filesystem-path literals**: a string used as an operand to `Path.__truediv__` against a runtime `repo_root`/`scan_root` (`repo_root / "architecture" / "slice-queue.md"`).
- **Class B — git-string identities**: a forward-slash repo-relative string used as a `git status --porcelain` U-file comparison key (`_SOFT_FILE_SET`), a `git show :N:`/`git show <branch>:`/`git ls-tree -- ` pathspec, a `git add` argument, or the equivalence-guard `qrel`/`srel` keys + `regenerated_files`. Class B only works while the vault is **git-tracked**: an untracked external file has no rebase stage, is absent from a branch's committed tree, and is never reported as a porcelain U-file.

A naive path-migration would route Class B too — feeding a backslash/absolute `VAULT_ROOT`-composed `Path` into an f-string pathspec (`git show :2:C:\…\slice-queue.md` is malformed; `git add <abs-external>` escapes the work tree), or leaving the literal in place so `git show :N:<untracked-path>` returns empty → at worst a **silent claim-drop** (the slice-090/091 history). R-32's whole hazard is silent corruption, so a silent mis-resolve here is the exact failure class to avoid.

This slice does NOT flip the default (vault stays `architecture/`, git-tracked). It makes the 3 tools *flip-ready* and proves the no-flip safety contract holds.

## Options considered

1. **Naive path-migration only** (route every `architecture/` to `VAULT_ROOT`, touch nothing else) — Con: routes Class B too → malformed pathspecs / `git add` escaping the work tree, or silent claim-drop post-flip. Re-opens R-32's silent-corruption class. **Rejected.**
2. **Build the external-vault conflict-resolution replacement now** (re-point PCR's rebase-stage reads at a `_vault_write`-lock / sidecar mechanism) — Con: LARGE; couples this MEDIUM readiness slice to the flip's integration design; the write-race owner `_vault_write` already exists but wiring it is the flip slice's job. **Rejected for this slice** (out of scope).
3. **Resolution-proxy gate** (`not VAULT_ROOT_IS_DEFAULT` decides RETIRE) — Con: conflates "resolution fell through to default" with "git-untracked"; over-RETIREs a vault relocated to an absolute path still **inside** the tracked tree (AC3 says operate, the tool refuses). Inexact as a binding gate. **Rejected** (`/critique` M1).
4. **Two-literal-class routing + precise git-tracked-check RETIRE + KEEP** (chosen) — ROUTE Class A through `VAULT_ROOT`; never route Class B (stays forward-slash repo-relative); gate every Class-B git-tree vault-content read + the SOFT/VAULT_CLAIM resolution entry on a precise per-pathspec `git ls-files --error-unmatch` tracked-check, failing **visibly** when untracked; KEEP git ops on tracked `slice/*` refs + worktrees. Pro: flip-ready, no silent failure, no-flip byte-identity by construction, MEDIUM scope, the guard fires exactly when no git conflict can arise.

## Decision

Adopt option 4. Concretely:

- **Binding RETIRE signal = a store-LOCATION check** (`tools/_vault_git.vault_is_external(repo_root)`): True iff the resolved `VAULT_ROOT` points OUTSIDE `repo_root`'s working tree — the vault has been flipped to an external store. Used UNIFORMLY by both `parallel_conflict_resolver` and `stranded_slice_audit`. NOT in the leaf `tools/_vault_paths.py` (needs `repo_root`; keeping it out preserves leaf-purity).
  - **Build-time refinement (slice-098, USER-RATIFIED — supersedes the per-pathspec `git ls-files` tracked-check option 4 first proposed):** the tracked-check proved UNSOUND in two ways the build surfaced. (1) **PCR** — in the env-set-but-not-yet-moved window, `architecture/slice-queue.md` is STILL tracked + the real rebase-conflict U-file, so the tracked-check returns True (proceed) while `out_path` routes to the external `VAULT_ROOT` → `relative_to(repo_root)` ValueError → the `/critique` B2 corruption goes UNcaught. (2) **stranded** — a stranded slice's vault content lives ONLY on its unmerged branch, never in the invoking tree's index, so the tracked-check over-RETIRES every legitimate in-tree stranded slice (its 4 existing test fixtures encode exactly this). The store-LOCATION signal catches B2 (external-abs `VAULT_ROOT` → True → RETIRE before any `out_path`) AND passes the stranded fixtures (env-unset → in-tree → proceed). It still handles M1's external-but-tracked `<repo>/vault/` case (under `repo_root` → not external → proceed; PCR's `classify`→UNKNOWN→STOP naturally covers a relocated-but-tracked conflict since `vault/slice-queue.md` ∉ `_SOFT_FILE_SET`).
  - `vault_pathspec_is_tracked(repo_root, pathspec)` (the precise `git ls-files --error-unmatch` primitive) is RETAINED in `tools/_vault_git.py` (tested by `test_vault_pathspec_tracked.py`) as a precise primitive for the future external-vault flip slice — NOT the in-loop RETIRE gate.
- A frozen `VAULT_ROOT_IS_DEFAULT` boolean on `tools/_vault_paths.py` is retained ONLY as an optional cheap fast-path / observability aid, **never** a gate.
- **ROUTE (Class A)**: every filesystem vault-path composition → `<root> / VAULT_ROOT / <subpath>` (one form, byte-identical relative-default vs absolute-external).
- **RETIRE-when-untracked (Class B)**: every `_SOFT_FILE_SET` key, `git show :N:`/`git show <branch>:`/`git ls-tree` pathspec, `git add` arg, `regenerated_files`, and `qrel`/`srel` comparison stays a forward-slash repo-relative literal and is governed by the tracked-check. The guard fires at **entry** to `resolve_soft_conflict` / `resolve_vault_claim_conflict` — **before** any `out_path` / `relative_to(repo_root)` composition (so the equivalence-guard `qrel`/`srel` comparison is never reached with a non-comparable external path — `/critique` B2). Failure is *visible*: typed error → STOP + audit breadcrumb carrying an **actionable operator message** (the post-flip manual-resolution procedure / the flip tracking slice).
- **KEEP**: git enumeration/classification of `slice/*` branches + worktree porcelain — git-tracked refs, not vault content.

## Consequences

- The 3 tools become flip-ready: with the vault relocated + untracked, Class-A reads find the external root; Class-B git-tree reads refuse visibly instead of silently mis-resolving.
- The no-flip safety contract holds **by construction**: with env unset + no config, `VAULT_ROOT == Path("architecture")` resolves UNDER `repo_root` → `vault_is_external` is False, the Class-A routing form collapses to the original literal, and every Class-B git path runs exactly as before. Pinned by a byte-identity + full-suite test (AC4), incl. the `_AUDIT_LOG_PATH` surface.
- The store-location guard **dissolves the env-set-before-flip stranding hazard** (`/critique` M2): an in-tree `VAULT_ROOT` (default, or external-but-tracked under the repo) is not external → PCR/stranded proceed normally and `/commit-slice --merge` under PSQ/BRANCH-2 parallel slices still auto-resolves. The guard refuses only once `VAULT_ROOT` points outside the repo work tree — the post-flip external-store state, where the git rebase/branch conflict it resolves cannot exist.
- Post-flip, `parallel_conflict_resolver`'s git-rebase vault-conflict role is **retired** (an untracked vault can't produce a git merge-conflict on its files); the write-time race is owned by the already-shipped `_vault_write` sidecar-lock. Wiring that replacement into PCR is the **flip slice's** job, out of scope here — and the RETIRE breadcrumb names that successor so a refused merge is recoverable, not a dead-end.
- `stranded_slice_audit`'s bare-branch stranded-recovery reads (both `_branch_tree_has_path` ls-tree and `_branch_tree_file` show) are retired-when-untracked; the branch-existence classification still works; an external-store recovery read, if needed, is a flip-slice concern.

## Reversibility

**cheap.** Class-A path-routing + a fail-visible store-location guard on Class-B — no data model, schema, contract, or identity lock. Reverting is a code revert; no migration, no external state.

## Residual (honest scope)

- The store-location signal answers "is `VAULT_ROOT` outside the repo work tree", which is precisely the flip boundary; the deliberate residual is the out-of-scope **post-flip PCR has no vault-conflict-resolution mechanism** until the flip slice wires the `_vault_write`-lock substitute. Acceptable because an external untracked vault produces no git merge-conflict to resolve; the RETIRE breadcrumb makes the path operator-actionable rather than silent.
- A relocated-but-tracked vault under `<repo>/vault/` is treated as in-tree by `vault_is_external` (not external) — PCR then relies on `classify`→UNKNOWN→STOP (its U-file `vault/slice-queue.md` ∉ the hardcoded `_SOFT_FILE_SET`) rather than the entry guard. This is correct fail-visible behaviour (PCR never auto-merges a relocated vault) but means PCR's SOFT/VAULT_CLAIM machinery is coherent ONLY at the in-tree `architecture/` default; making it *work* at an arbitrary tracked location is the flip slice's job, not this one's.
- `vault_is_external` resolves paths once per guard evaluation (not the hot path). `vault_pathspec_is_tracked` is retained unused-by-the-gate but tested, for the flip slice. Acceptable cost.
