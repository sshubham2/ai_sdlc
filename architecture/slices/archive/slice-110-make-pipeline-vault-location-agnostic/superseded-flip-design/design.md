# Design: Slice 110 flip-vault-to-external-store

**Date**: 2026-06-04
**Mode**: Standard

The **atomic-move-first** cut of the external-vault flip — the operation R-32 retires on. This is a thin-vault design: it references code locations + the existing seam, and specifies the load-bearing *sequence* rather than introducing machinery (the seam, the write-safety CAS, the `vault_is_external` RETIRE guard, and the readiness audit all already shipped in 093/094/095/097/098/100/109).

## Decisions settled at /design-slice (user-confirmed)

| Decision | Choice | Consequence |
|----------|--------|-------------|
| External store location | `~/.aisdlc/ai-sdlc/` → config value `C:\Users\sshub\.aisdlc\ai-sdlc` | Human-readable, off OneDrive (C3 ✓). `architecture/`'s **contents** move there; the store dir IS `VAULT_ROOT`. |
| Git history (C5) | `git rm --cached` only — no history migration | Full vault history stays reachable in the repo's past commits; the external store is the live working snapshot (filesystem, untracked) from the flip onward. |
| Scope/safety | ONE slice + mid-slice tripwire + rollback-proven-first | If genuine test-breakers > ~20 at the mid-slice smoke → STOP, roll back (proven), split the remainder to slice-111. |
| `diagnose-out/` | **Out of scope for slice-110** | Already untracked (0 tracked files), operator-pathed (`--in`/`--out`, default `./diagnose-out`), regenerable, NOT the R-32 shared-mutable-write hazard. Relocating it is a separable follow-on. |

## What's new

- **An operational flip runbook** (NOT a code module): seed the external store, write the git-common-dir config, `git rm --cached -r architecture`, `.gitignore` it, remove the in-tree working copies. Executed under `/build-slice` plan-mode; documented step-by-step in build-log.md.
- **`.gitignore`**: add `architecture/` (so the untracked dir cannot silently re-enter the index).
- **`skills/commit-slice/SKILL.md`** (modified): the `--merge` rebase-conflict flow recognizes `parallel_conflict_resolver`'s external-RETIRE `ResolutionResult` as a **distinct clean no-op** (AC3 — the slice-109 deferral). OSDG-1 drift-guarded → re-sync the installed copy.
- **Test changes**: repoint the *genuinely-breaking* tests (real-vault readers + in-process `repo_root=tmp` callers) to be vault-location-agnostic; size discovered at the mid-slice smoke (tripwire ≤ ~20). Plus three new tests (anti-revert pin, rollback proof, AC3 RETIRE — below).
- **`architecture/risk-register.md`**: R-32 `mitigating → retired` (written **post-flip to the external store** via `vault_edit rewrite`, the slice-097 CAS channel).
- **ADR-099** (the flip) + **ADR-100** (commit-slice RETIRE).

## What's reused

- `tools/_vault_paths.py` — the seam. Tier-2 (`$GIT_COMMON_DIR/aisdlc/vault-root`) is already read at import; slice-110 **writes** that config. No code change to the seam.
- [[decisions/ADR-085]] — the resolution precedence + the C1–C5 constraints (C1 keying, C3 off-OneDrive, C5 history) this slice executes.
- [[decisions/ADR-089]] — `tools/_vault_git.vault_is_external` (the binding RETIRE signal) + `tools/parallel_conflict_resolver._retire_if_vault_external` (`parallel_conflict_resolver.py:307`, wired at resolve-entry `:367`/`:1455`) — **already RETIREs** when external; slice-110 wires `/commit-slice` to *consume* it.
- [[decisions/ADR-098]] / slice-109 — `tools/_vault_write.safe_rewrite_text` CAS is the post-flip write-race owner that *replaces* PCR's git-merge role for vault files.
- `tools/vault_flip_readiness_audit.py` — AC2 gate (`needs-human` clean; production `must-rewrite` baseline stays ∅).
- `architecture/spikes/spike-external-shared-vault.md` — the CONDITIONAL/GO spike that de-risked the relocation (the irreversibility precondition per ADR Reversibility rules).

## Components touched

### `skills/commit-slice/SKILL.md` (modified — AC3)
- **Responsibility**: in the `--merge` rebase flow, when `parallel_conflict_resolver` returns its external-RETIRE result (vault is an external/untracked store), treat it as a distinct, clean **no-op** — print the RETIRE breadcrumb (vault conflicts cannot exist post-flip; the write-race is owned by `_vault_write` CAS) and route any *genuine non-vault* rebase conflict to the existing manual SOAD-1 path. NOT a crash, NOT a spurious SOFT/HARD classification.
- **Lives at**: `skills/commit-slice/SKILL.md` (the PCR-2b gate block, ~`:196`–`:227`).
- **Key interactions**: `tools/parallel_conflict_resolver._retire_if_vault_external` → `tools/_vault_git.vault_is_external`.

### `.git/aisdlc/vault-root` (new — DATA, written once; not a module)
- **What**: single-line absolute path `C:\Users\sshub\.aisdlc\ai-sdlc`. Read by `_vault_paths` tier-2; shared across all worktrees (git-common-dir is shared). Never git-tracked (inside `.git/`).

## Flip execution sequence (load-bearing — self-referential + dual-tree)

`/slice` ran in the main tree; the slice-110 worktree holds the slice work. The flip moves the **canonical** vault, whose content is currently split: master holds the shared aggregate files (incl. the slice-110 pick in `slice-queue.md`), the worktree holds slice-110's own folder. The sequence re-unifies them.

0. **Sync the union**: `git -C <wt> merge master` (brings the queue-pick commit into slice/110; clean — `slice-queue.md` changed only on master). Now `<wt>/architecture/` = master's shared vault ∪ slice-110's folder = the complete vault.
1. **Prove rollback FIRST** (must-not-defer): exercise the rollback runbook on a tmp-repo simulation → restored state passes. Only then proceed.
2. **Seed external**: byte-faithful copy `<wt>/architecture/` contents → `~/.aisdlc/ai-sdlc/` (LF-preserving; no CRLF churn — EOL-DRIFT-1).
3. **Write config** `.git/aisdlc/vault-root` = the absolute external path. Resolution now picks tier-2 for *both* trees.
4. **Mid-slice smoke / tripwire**: `_vault_paths.VAULT_ROOT` resolves external + `VAULT_ROOT_IS_DEFAULT is False`; a second `git worktree add` resolves the *identical* external root; run the full suite → **count genuine breakers**. `> ~20` → STOP + roll back + split remainder to slice-111.
5. **Untrack + remove**: `git -C <wt> rm --cached -r architecture` (stage on slice/110) + add `architecture/` to `.gitignore`; remove the in-tree `architecture/` working copies (worktree now; main tree post-merge).
6. **Repoint breaking tests**; full suite green; `vault_flip_readiness_audit` `needs-human` clean.
7. **Vault writes (now external)**: R-32 retire, ADR-099/100 finalize, AC3 wiring, anti-revert pin — all land in `~/.aisdlc/ai-sdlc/` via the seam.
8. **At `/commit-slice --merge`**: slice/110 → master; master's index drops `architecture/`; the external store is the live vault. R-32 retires.

**Rollback (proven at step 1, available through step 8 pre-merge)**: delete the config; restore `architecture/` in-tree from the external copy; `git reset` the `rm --cached`; drop the `.gitignore` line; suite green in the restored in-tree configuration. Post-merge reversal is *expensive* (re-track 1033 files + copy back any post-flip external writes) but recoverable — no data loss.

### Self-referential bootstrap (resolved)
slice-110's own artifacts are written pre-flip in the worktree's `architecture/slices/slice-110/` (mission-brief, milestone, design, ADRs, critique, early build-log) → **seeded to external at step 2** → post-flip `/validate-slice` + `/reflect` write directly to external via `VAULT_ROOT`. The folder converges in the external store. The ADRs are tracked pre-flip, seeded, then untracked at step 5 (they live in external thereafter). Post-flip there is **no per-worktree `architecture/`** — all worktrees resolve the one shared external vault (the git-common-dir config is shared). This is exactly the BRANCH-2 × flip transition [[decisions/ADR-085]] §Consequences anticipated ("no per-worktree `architecture/` once shared").

## Wiring matrix

Per **WIRE-1**: slice-110 introduces **no new code module** (the flip is an operational runbook; the config is data; the new tests consume existing tools). Zero-row matrix → clean.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Test plan (the three new tests; repoints discovered at mid-slice)

- `tests/methodology/test_vault_flip_state.py` — **anti-revert pin** (AC4): post-flip, asserts the config exists + `architecture/` is git-untracked (`git ls-files architecture` empty) + `vault_is_external(repo_root)` True. Fails if the flip silently reverts. (Becomes meaningful only post-flip; pre-flip it is xfail/skipped with a guard on `vault_is_external`.)
- rollback-proof test (AC5) — hermetic tmp-repo simulation of flip→rollback asserting byte-restoration + green resolution; never touches the real store.
- AC3 RETIRE test — exercises the `/commit-slice` external-RETIRE recognition against a **real external `VAULT_ROOT`** (tmp repo with the config set to a tmp external dir), asserting a distinct clean no-op (not a crash / not a SOFT/HARD misclassification).
- **Repoints**: the genuine breakers (in-process `repo_root=tmp` callers that route through the now-absolute `VAULT_ROOT`) made location-agnostic (subprocess-with-`AI_SDLC_VAULT_ROOT`-env isolation, or explicit vault-root). Hermetic tmp-fixtures that keep a `architecture` literal are **left unchanged** — that literal is correct for a config-less tmp repo; `test-update-at-flip` is a checklist, not a fail-closed gate.

## Decisions made (ADRs)
- [[ADR-099]] — execute the `architecture/` vault flip to `~/.aisdlc/ai-sdlc`; `git rm --cached`; no history migration; `diagnose-out/` deferred; retire R-32 — reversibility: **expensive**.
- [[ADR-100]] — `/commit-slice --merge` recognizes the resolver's external-RETIRE as a distinct clean no-op (executes ADR-089's assignment) — reversibility: **cheap**.

## Authorization model for this slice
No authorization surface — the flip is a local filesystem + git-index + `.git/` config operation on the developer's own machine. The cooperative write-safety model (sidecar locks, CAS) is scope, not a security boundary (per ADR-085).

## Error model for this slice
Every irreversible step is gated behind the **proven rollback** (step 1). The seed is byte-faithful + hash-verified (EOL-DRIFT-1). Resolution failures are fail-visible (the seam's stderr WARN; never a silent mis-resolve — R-7). The tripwire (step 4) halts on oversized test-breakage rather than grinding past the budget. The untrack is loud (visible in the slice commit + `.gitignore`). Post-flip vault write-races are owned by `_vault_write` CAS (slice-109); PCR's git-merge vault role is RETIRED (AC3).
