---
id: ADR-099
title: Execute the external-vault flip — relocate architecture/ to ~/.aisdlc/ai-sdlc via git-common-dir config, git rm --cached (no history migration), defer diagnose-out, retire R-32
date: 2026-06-04
slice: slice-110-flip-vault-to-external-store
reversibility: expensive
status: accepted
supersedes: null
---

# ADR-099: Execute the external-vault flip

## Context

The external-shared-vault initiative ([[ADR-065]] → [[ADR-085]]) staged the flip across slices 093→109: write-safety ([[ADR-086]]/[[ADR-087]]/[[ADR-088]]), git-coupled-tool route/retire ([[ADR-089]]), the post-flip CAS write-time replacement for PCR ([[ADR-098]]), and three inventories (production/tests/prose). [[ADR-085]] §Consequences names the remaining flip-slice work: "flip `_DEFAULT`/wire the config, physically move `architecture/`+`diagnose-out/`, decide history (C5), wire `/triage`+`/adopt`." R-32 (concurrent-write lost-update / atomic-rename corruption on a shared mutable vault) is `mitigating` and **retires on the physical move** — the silent-corruption hazard is a property of the shared mutable store, which does not exist pre-flip.

This ADR executes the **architecture-only** atomic move (the user's "atomic move first" cut at `/slice`). The 318-site prose rewrite is deferred to slice-111; this ADR does not touch it.

## Options considered

1. **Move both `architecture/` + `diagnose-out/`** (the literal ADR-085 framing) — Con: `diagnose-out/` has **0 tracked files** (already untracked), is operator-pathed (`--in`/`--out`, default `./diagnose-out`), regenerable, and is NOT the R-32 shared-mutable-concurrent-write hazard. Bundling it adds scope + a second relocation seam for no R-32 benefit. **Rejected** (deferred, not cancelled).
2. **Hashed slug `~/.aisdlc/<bounded-hash>/` + ship the install-prompt machinery now** (the ADR-085 productized default) — Con: the install base-config (`~/.claude/ai-sdlc-vault-base`) was never shipped; building slug-resolution + the `/triage`/`/adopt` prompt is onboarding-NEW-repos machinery, orthogonal to flipping THIS repo. **Rejected for this slice** (a clean concrete path now; the productized generalization is a follow-on).
3. **Migrate full git history into the external store** (C5 = preserve `git log`) — Con: heavy (filter-repo into a separate vault repo); only valuable if versioned vault history at the new location is wanted. For a solo dogfooding repo it is not. **Rejected.**
4. **Relocate `architecture/`'s contents to `~/.aisdlc/ai-sdlc/`; write the git-common-dir config; `git rm --cached`; no history migration; defer `diagnose-out/`** (chosen).

## Decision

Adopt option 4 for this repo:

- **Location**: `architecture/`'s **contents** move to `~/.aisdlc/ai-sdlc/` (resolved `C:\Users\sshub\.aisdlc\ai-sdlc`). The store directory IS `VAULT_ROOT`. Off OneDrive / aggressive-AV / Search-indexer dirs (constraint **C3** — verified: neither the repo nor `~/.aisdlc` is under `C:\Users\sshub\OneDrive`).
- **Activation**: write the single-line absolute path to `$GIT_COMMON_DIR/aisdlc/vault-root` (tier-2 of the already-shipped `_vault_paths` precedence; keyed via `--path-format=absolute --git-common-dir` per **C1**). No code change to the seam — the flip is the config write, not a `_DEFAULT` edit.
- **Untrack (C5)**: `git rm --cached -r architecture` on the slice branch + `.gitignore` `architecture/`. Vault history stays reachable in the repo's past commits; the external store is the live snapshot going forward (no history migration).
- **`diagnose-out/`**: deferred (out of scope) — untracked/regenerable/operator-pathed, not an R-32 hazard.
- **Sequence + rollback**: per `design.md` §Flip execution sequence — sync the master/worktree union, **prove rollback first**, seed byte-faithfully, write config, mid-slice tripwire (`> ~20` genuine breakers → STOP + roll back + split to slice-111), untrack, repoint breakers, write vault deltas to the external store.
- **R-32 retires** at the move (status `mitigating → retired` in `risk-register.md`).

## Consequences

- The vault becomes a single shared external store all worktrees of the repo resolve identically (the git-common-dir config is shared) — the multi-worktree shared-view the initiative exists to deliver; the `_index.md`/`risk-register.md`/`slice-queue.md` git-merge-conflict class is structurally eliminated.
- Post-flip there is **no per-worktree `architecture/`**; vault write-races are owned by `_vault_write` CAS (slice-109); PCR's git-merge vault-conflict role is RETIRED (wired into `/commit-slice` by [[ADR-100]]).
- slice-110's own artifacts converge in the external store (seeded pre-flip, then written there post-flip).
- The productized generalization (bounded-hash slug + `~/.claude/ai-sdlc-vault-base` install prompt + `/triage`/`/adopt` wiring) and the `diagnose-out/` relocation + the 318-prose rewrite remain as named follow-ons.

## Reversibility

**Expensive** (not irreversible; the relocation is recoverable with no data loss). **Within the slice** (pre-`/commit-slice --merge`) it is cheaply reversible via the rollback runbook proven at sequence step 1 (delete config + restore in-tree from the external copy + `git reset` the `rm --cached` + drop the gitignore line). **Post-merge** reversal costs re-tracking 1033 files + moving content back + copying any post-flip external-only vault writes back into git — real effort, but no identity/tenant/entity lock and no data loss. The relocation was de-risked by the CONDITIONAL/GO `spike-external-shared-vault` (the irreversibility precondition).
