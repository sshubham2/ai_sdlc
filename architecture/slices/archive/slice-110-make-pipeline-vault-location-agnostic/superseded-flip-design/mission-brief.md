# Slice 110: flip-vault-to-external-store

**Mode**: Standard
**Estimated work**: 1 day | split needed — see Scope note below
**Risk retired**: R-32 (concurrent-write lost-update / atomic-rename corruption on a shared mutable vault) — **retires here**; the physical move is R-32's documented retirement event (`architecture/risk-register.md` R-32; slice-109 reflection "Deferred → the physical flip itself … R-32 retires there")
**Test-first**: false  (migration of path-resolution, not new behavior; regression pins are captured as ACs, not a TF-1 plan)
**Walking-skeleton**: false
**Exploratory-charter**: true  (per ETC-1 — the real external store on a real machine path is the one thing 094/095/097/109's in-tree concurrency proofs could NOT exercise)

## Intent

The external shared-vault initiative (slices 093→109) has closed every readiness axis except the physical move: write-safety (094/095/097), git-coupled tools (098), the post-flip CAS write-time replacement for PCR (109), and the three inventories (100 production / 102 tests / 107 prose). This slice performs the **atomic move first** cut: relocate `architecture/` (the 1033 tracked vault files — the sole R-32 driver) to the shared external store `~/.aisdlc/ai-sdlc/`, untrack it from git, activate the `$GIT_COMMON_DIR/aisdlc/vault-root` resolution config so `_vault_paths.VAULT_ROOT` resolves externally, and repoint the genuinely-breaking tests (the readiness-audit `test-update-at-flip` subset that actually resolves the real vault) so the suite stays green. **R-32 retires at the move.** Two deliberate narrowings settled at `/design-slice`: **`diagnose-out/` is deferred** (already untracked / regenerable / operator-pathed — not the R-32 shared-mutable-write hazard), and the **318-site prose rewrite** (slice-107) is deferred to slice-111 (prose drift does not break the suite).

## Acceptance criteria

1. **The flip is live.** `architecture/`'s contents are physically relocated to the shared external store (`~/.aisdlc/ai-sdlc/` → config value `C:\Users\sshub\.aisdlc\ai-sdlc`), `git rm --cached`'d (untracked), and the `$GIT_COMMON_DIR/aisdlc/vault-root` config is written so resolution picks tier-2. Verified: external store contains the vault; `git ls-files architecture` returns empty; `_vault_paths.VAULT_ROOT` resolves to the external path and `VAULT_ROOT_IS_DEFAULT is False`; a **second worktree of the same repo resolves the identical external VAULT_ROOT** (the shared-visibility property — the git-common-dir config is shared, so this must hold).
2. **System remains shippable.** The full test suite passes against the relocated vault, and `tools/vault_flip_readiness_audit.py`'s gate is clean (`needs-human` = 0; production `must-rewrite` baseline stays ∅). NB: the target is **green suite**, NOT zero `test-update-at-flip` — hermetic tmp-fixtures legitimately keep an `architecture` literal (it is the correct production default for a config-less tmp repo), and that class is a checklist, not a fail-closed gate. The 318 prose-surface literals are untouched (verified out-of-scope: `tools/vault_flip_prose_inventory.py --strict` count unchanged).
3. **Post-flip `/commit-slice` RETIRE is wired** (the AC3 deferred from slice-109 per ADR-089): `/commit-slice --merge`'s git-coupled vault-conflict handling becomes a documented RETIRE no-op with a distinct PCR-RETIRE signal once the vault is untracked, exercised against the **real** external path. Verified by its committed test.
4. **R-32 is retired with an anti-revert pin.** R-32 status `mitigating → retired` in `architecture/risk-register.md`, naming the move as the retirement event; a new regression test asserts both the tier-2 external resolution AND the git-untracked state so the flip cannot silently revert to the in-tree `architecture/` default.
5. **Rollback is safe until merge.** A documented + tested restore path makes the flip fully reversible within the slice (before `/commit-slice --merge`): the move, the untrack, and the config-write can each be undone to restore the pre-flip in-tree git-tracked vault.

> **Scope note (resolved at `/design-slice`)**: the dominant scope driver is the post-flip test-breakage, which is **statically unpredictable** — only the *in-process `repo_root=tmp`* callers genuinely break (post-flip `VAULT_ROOT` is absolute, so `repo_root / VAULT_ROOT` discards `repo_root` and reads the real external store, not the fixture). Static estimate: ~7 hard breakers + up to ~30 more; the true count surfaces only at the mid-slice full-suite run. **Decision (user-confirmed): ONE slice + a mid-slice tripwire** — if genuine breakers exceed ~20 at the mid-slice smoke, STOP, roll back (proven first), and split the remaining test-fixes into slice-111. The rollback-proven-first discipline neutralizes the move's irreversibility for the tripwire path.

## Exploratory test charter

(per **ETC-1**, `methodology-changelog.md` v0.16.0 — the external store on a real machine path is novel reality that no in-tree concurrency proof reached)

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore the relocated vault on the real `~/.aisdlc/` machine path under concurrent multi-worktree writers (queue/claim/append/rewrite) to find EPERM / lost-update / atomic-rename failures the in-tree proofs could not surface — explicitly verify the store is NOT on a OneDrive/antivirus-watched path (R-32 constraint C3 / ADR-085) | 60min | PENDING | — |
| 2 | Explore the post-flip pipeline end-to-end from a SECOND worktree (run `/pulse` + a read-only `/reflect`-shaped vault scan) to find any tool, skill-helper, or test still reading the old in-tree `architecture/` path after the flip | 45min | PENDING | — |

COMPLETED rows MUST have non-empty Findings (even if "no issues observed"). DEFERRED rows MUST carry a rationale in Findings.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | The flip is live | `ls ~/.aisdlc/ai-sdlc/` shows the vault contents; `git ls-files architecture` is empty; a subprocess prints `_vault_paths.VAULT_ROOT` (external) + `VAULT_ROOT_IS_DEFAULT == False`; a second `git worktree add` + the same print resolves the identical path |
| 2 | System shippable | full `pytest` green; `$PY -m tools.vault_flip_readiness_audit` exits 0; `$PY -m tools.vault_flip_prose_inventory --strict` shows the 318 prose sites unchanged (out-of-scope intact) |
| 3 | commit-slice RETIRE wired | the committed post-flip `/commit-slice` test passes against the real external path; the RETIRE/PCR-RETIRE signal is distinct + asserted |
| 4 | R-32 retired + pinned | `$PY -m tools.risk_register_audit architecture/risk-register.md --json --filter-status open` no longer lists R-32; the new anti-revert test fails if resolution falls back to in-tree default OR the vault is re-tracked |
| 5 | Rollback safe | a test (or documented + executed runbook step) restores the pre-flip state from the relocated store, re-tracks, removes the config, and the suite passes in the restored configuration |

## Must-not-defer

- [ ] **Rollback/restore runbook written and proven BEFORE the irreversible `git rm --cached` + move** — the flip must be undoable until `/commit-slice --merge`.
- [ ] **External store location decision + C3 constraint check** — confirm the resolved `~/.aisdlc/ai-sdlc/` path is NOT under OneDrive / an aggressive-AV / Search-indexer-watched directory (R-32 / ADR-085 C3 — verified at /design-slice: neither the repo nor `~/.aisdlc` is under `C:\Users\sshub\OneDrive`); chosen path documented in design.md + ADR-099.
- [ ] **Self-referential bootstrap resolved in design** — this slice's OWN artifacts live under `architecture/slices/slice-110-…/`; the flip moves `architecture/` out. Design MUST specify where slice-110's artifacts live post-flip and how `/reflect` + `/commit-slice` read them, AND whether the worktree-per-slice model holds for a slice that moves the vault out of the tree (if not, a documented deviation/ADR — not a silent skip).
- [ ] **git-untrack is deliberate and loud** — `git rm --cached -r architecture` + a `.gitignore` entry for `architecture/` so it cannot be silently re-added; the untrack is visible in the slice commit. (`diagnose-out/` is already untracked — out of scope.)
- [ ] **Byte-faithful move** — the relocated vault preserves exact bytes/EOL (EOL-DRIFT-1 / ADR-033); no CRLF↔LF churn introduced by the move.
- [ ] **Observability** — a loud one-line signal at flip time (the move + the non-default resolution INFO already emitted by `_vault_paths._resolve_vault_root`); the commit message records the retirement of R-32.

## Out of scope

- **Relocating `diagnose-out/`** — deferred. It is already untracked (0 tracked files), regenerable, operator-pathed (`--in`/`--out`, default `./diagnose-out`), and is NOT the R-32 shared-mutable-concurrent-write hazard. A separable follow-on; not required for R-32 retirement.
- The **318-site prose rewrite** (skills / agents / CLAUDE.md / README.md / INSTALL.md) — slice-111 `rewrite-vault-prose-references-for-flip` (slice-107 inventory). Prose drift does not break the suite.
- The **productized onboarding generalization** — the bounded-hash slug, the `~/.claude/ai-sdlc-vault-base` install prompt, and `/triage`/`/adopt` flip-wiring (ADR-085) are about onboarding NEW repos, orthogonal to flipping THIS one. This slice writes one concrete path.
- Any change to the write-safety machinery itself (094/095/097/109 are shipped and consumed as-is).
- Cross-machine vault sync beyond a single machine-local shared store (the store is machine-global; multi-machine replication is a separate, later concern).
- Re-litigating the resolution precedence (env → git-common-dir config → default) — fixed by ADR-065/ADR-085; this slice activates tier-2, it does not redesign the seam.

## Dependencies

- Prior slices: [[slice-093-add-external-vault-support]] (ADR-085 write-safety infra + the tier-2 config seam this slice activates), [[slice-094-…]]/[[slice-095-…]]/[[slice-097-…]] (the three write-safety sub-classes), [[slice-098-…]] (ADR-089 — git-coupled tools route/retire, the `vault_is_external` signal), [[slice-100-add-vault-flip-readiness-audit]] (production inventory + the readiness audit AC2 gates on), [[slice-102-vault-flip-readiness-tests]] (the 154 test-update inventory this slice consumes), [[slice-107-inventory-vault-flip-prose-surface]] (the 318 prose sites this slice deliberately does NOT touch), [[slice-109-add-post-flip-vault-conflict-safety]] (ADR-098 — the post-flip CAS write-time replacement for PCR; supplies AC3's deferred RETIRE)
- Vault refs: [[decisions/ADR-065]] (VAULT_ROOT env seam), [[decisions/ADR-066]] (pre-flip vault git-tracked — this slice reverses it), [[decisions/ADR-085]] (tier-2 git-common-dir config + C-constraints), [[decisions/ADR-089]] (git-coupled tools + commit-slice RETIRE assignment), [[decisions/ADR-098]] (post-flip queue CAS)
- Tools: `tools/_vault_paths.py` (the seam — activate tier-2), `tools/vault_flip_readiness_audit.py` (AC2 gate), `tools/vault_flip_prose_inventory.py` (out-of-scope guard), `tools/_vault_git.py` (`vault_is_external`)
- Risk register: [[risk-register#R-32]]

## Mid-slice smoke gate

At ~50% of build — immediately after the move + config-write, this is ALSO the **tripwire** (Scope note): run the FULL suite and count genuine breakers BEFORE doing the bulk of the test repoints:
```
$PY -c "import tools._vault_paths as v; print(v.VAULT_ROOT, v.VAULT_ROOT_IS_DEFAULT)"   # expect: external abs path, False
$PY -m tools.vault_flip_readiness_audit          # expect: needs-human=0 (gate clean); test-update-at-flip count does NOT go to 0
$PY -m pytest -q                                 # count genuinely-failing tests = the real breaker set
```
Expected: vault resolves externally, readiness gate clean. **Tripwire**: if the genuine breaker count > ~20 → **STOP**, exercise the (already-proven) rollback runbook, and split the remaining repoints into slice-111. If the move corrupted the vault or resolution still points in-tree → STOP, diagnose, roll back. (Note: a non-zero `test-update-at-flip` count is EXPECTED — hermetic tmp-fixtures legitimately keep `architecture` literals; the signal is the pytest FAIL count, not the audit checklist count.)

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Full test suite green against the relocated vault; `vault_flip_readiness_audit` exits 0
- [ ] R-32 marked retired; anti-revert pin in place
- [ ] Rollback runbook documented AND proven
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
