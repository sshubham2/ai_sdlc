# Slice 115: flip-vault-to-external-store

**Mode**: Standard
**Estimated work**: 1 day (LARGE — deliberate atomic exception; see Intent "Why one atomic slice")
**Risk retired**: **R-32** — concurrent-write lost-update / atomic-rename-EPERM corruption on a shared mutable vault. This slice executes the **physical move**, the sole residual to retirement after 22 prep slices (093→114). R-32 → `retired` at slice end.
**Test-first**: false  (the regression net already exists — slice-110 made the full suite vault-location-agnostic; the flip's proof is "suite byte-identical green against the flipped store")
**Walking-skeleton**: false
**Exploratory-charter**: true  (per ETC-1 — a migration of this blast radius is exactly where post-flip surprises hide; charters below probe fresh-bootstrap, live concurrent writes, and the slice's own self-archival round-trip)

## Intent

Relocate the vault (`architecture/`) from the in-repo, git-tracked default to a **shared, external, per-project store** (`~/.aisdlc/<project>/`, base `~/.aisdlc` per [[decisions/ADR-085]]) and untrack it from git — so every concurrent slice worktree resolves ONE live vault view and the `_index.md` / `risk-register.md` / `slice-queue.md` cross-worktree merge-conflict class is eliminated structurally. This is the **capstone** of the external-shared-vault initiative: slices 093–114 built every piece of flip-readiness (write-safety sub-classes, git-coupled-tool routing, post-flip CAS replacement, location-agnostic suite, prose seam) precisely so the flip itself is the irreducible atomic remainder.

**Why one atomic slice (LARGE, not split):** a half-flip is unshippable. If the files move but R-32.a (active-folder bootstrap) is not drained, the loop cannot scaffold or archive a slice; if R-32.b (archive-`mv` coherence) is not drained, `/reflect` fails loud on archival; if carve-out prose is not rewritten, worktree-composed paths mis-resolve. Splitting produces no shippable intermediate cut — this is the one legitimate LARGE-atomic exception the `/slice` scope rule carves out (split only when a split yields a shippable slice; here it does not).

## Acceptance criteria

1. **Config-driven flip is live and the suite is green against it.** The per-project config at `$GIT_COMMON_DIR/aisdlc/vault-root` holds the absolute external vault path; `tools/_vault_paths.VAULT_ROOT` resolves to the external store and `tools/_vault_git.vault_is_external(repo_root)` returns `True`; the full test suite passes against the flipped store (location-agnostic per slice-110), and the non-default-resolution observability INFO line fires.
2. **Physical move + git-untrack complete with no data loss.** `architecture/`'s contents are relocated to the external store history-aware (ADR-085 C5); `architecture/` is removed from git tracking (`git rm -r --cached`) and gitignored; the repo working tree no longer carries vault files, and the external store holds the complete vault byte-faithfully (no CRLF/EOL churn).
3. **R-32.a drained — active-slice-folder bootstrap settled.** The worktree-vs-external active-folder decision (resolved in `/design-slice`) is implemented; the op-gate's `OP_DEFERRED_TO_FLIP` bucket is driven to ∅ (an un-drained bucket at the flip is a violation, not a waiver — AP-12); a brand-new slice can be scaffolded by `/slice` and built by `/build-slice` post-flip.
4. **R-32.b drained — archive-`mv` cross-store coherence.** The archive move (`vault_edit move --from slices/slice-NNN --to slices/archive/`) resolves both endpoints coherently across the flipped store; `/reflect` can archive a completed slice post-flip without a `source-not-found` loud failure (live-fire: this slice's own self-archival is the proof — see Charter 3).
5. **Carve-out prose + `/commit-slice` RETIRE + R-32 retired.** The remaining concrete carve-out prose (classes 4–7: worktree-composed / active-folder / slice-queue / diagnose-out — enumerated by `tools/vault_flip_prose_inventory.py`) is rewritten consistent with the R-32.a/.b decisions; `/commit-slice`'s PCR git-rebase vault-conflict role is RETIRE'd to a documented no-op (deferred to this slice per [[decisions/ADR-089]]); R-32 status flips to `retired` in the register.

## Exploratory test charter

Charter-based exploratory testing (Bach / Kaner / Hendrickson): each is a timeboxed mission run against the **live flipped store**. Statuses PENDING → IN-PROGRESS → COMPLETED (or DEFERRED with rationale); `/validate-slice` Step 5d runs `tools/exploratory_charter_audit.py --strict-pre-finish`. COMPLETED rows MUST carry non-empty Findings.

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore a fresh second worktree (and a simulated new-machine bootstrap) resolving the external store with only the shared git-common-dir config, to find first-resolve / first-write gaps (does a brand-new worktree see the live vault with zero extra local setup?) | 60min | PENDING | — |
| 2 | Explore real concurrent multi-worktree writes to the same live external vault file (`slice-queue.md`, `_index.md`) under genuine filesystem conditions, to confirm the sidecar-lock + CAS path holds beyond the spawn-proof (no lost update, no EPERM corruption) | 60min | PENDING | — |
| 3 | Explore this slice's OWN self-archival round-trip post-flip (R-32.b live-fire): drive `/reflect`'s archive `move` across the flipped store and confirm no `source-not-found`, no cross-store mis-write | 45min | PENDING | — |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Config flip live + suite green | `cat $(git rev-parse --path-format=absolute --git-common-dir)/aisdlc/vault-root` shows the external abs path; `python -c "import tools._vault_paths as v; print(v.VAULT_ROOT)"` prints the external path; `python -c "import tools._vault_git as g; print(g.vault_is_external('.'))"` → `True`; full `pytest` green; stderr shows the `INFO: AI-SDLC vault root = … (via git-common-dir config)` line |
| 2 | Move + untrack, no data loss | `git ls-files architecture/` returns empty; `architecture/` is gitignored; the external store contains every prior vault file with byte-identical content (hash-compare a sample of `_index.md` / `risk-register.md` / an append-only ADR pre/post move); `git status` clean (no stray tracked vault files) |
| 3 | R-32.a drained | `python -m tools.vault_flip_prose_inventory --op-gate` reports `OP_DEFERRED_TO_FLIP` count = 0; dry-run `/slice` scaffold of a throwaway candidate writes the active folder to the decided location; `/build-slice` Branch-state logic resolves correctly post-flip |
| 4 | R-32.b drained | `vault_edit move` of a fixture active folder → archive resolves both endpoints under the external store (no source-not-found); Charter 3 self-archival succeeds end-to-end |
| 5 | Prose + commit-slice + retire | `python -m tools.vault_flip_prose_inventory --strict` reports the carve-out (classes 4–7) surface rewritten/consistent; `/commit-slice` PCR-vault-conflict path is a documented no-op (test asserts it does not attempt git-rebase vault resolution when `vault_is_external`); `tools.risk_register_audit … --filter-status retired` includes R-32 |

## Must-not-defer

- [ ] **No data loss on the move** — history-aware relocation (ADR-085 C5); verify byte-faithful (no EOL churn) before deleting the in-tree copy
- [ ] **Documented, tested reversibility** — the move-back path (relocate files in, unset `aisdlc/vault-root`, `git add` + restore tracking, revert prose) is documented and exercised at least once; R-32 reversibility is `cheap` and must STAY cheap
- [ ] **`vault_is_external()` gating correctness** — every consumer that branches on store-location (PCR retire, stranded-audit Class-B retire, op-gate) resolves the flipped store with zero silent mis-resolve (R-7 fail-visible)
- [ ] **Off-OneDrive / aggressive-AV store** — store base honors ADR-085 C3 (`~/.aisdlc`, not a OneDrive-synced path) so `os.replace` does not EPERM-loop
- [ ] **No op-gate bucket left un-drained** — `OP_DEFERRED_TO_FLIP` AND any `OP_UNROUTED` → ∅; an un-drained bucket at the flip is a violation (AP-12), surfaced not waived
- [ ] **Full audit suite green post-flip** — VWS-1, SVW-1, op-gate, `/drift-check`, PMI-1, INST-1, CAD-1 all pass against the flipped store
- [ ] **Observability** — the non-default resolution INFO line + any RETIRE-path log fire (operator can see the vault is external)

## Out of scope

- **`diagnose-out/` relocation** — decoupled from the slice loop at slice-105; no `<diagnose-out>` seam was minted (slice-112 B5). A separate future slice if ever wanted.
- **A cross-machine sync mechanism** — the store is a local `~/.aisdlc` dir; syncing it across machines (git submodule, rsync, cloud) is the operator's choice / a future slice, not this one.
- **Re-deciding the `<project>` hash derivation** — settled by ADR-085 (bounded hash of the canonicalized common-dir, MAX_PATH-safe).
- **Minting new write-safety machinery** — all three sub-classes already shipped (094/095/097); this slice consumes them, it does not extend them.

## Dependencies

- Prior slices (the readiness chain): [[slice-093-add-external-vault-support]] (resolution + write-safety primitive), [[slice-094-...]]/[[slice-095-...]]/[[slice-097-...]] (the 3 write-safety sub-classes), [[slice-098-...]] (the 3 git-coupled tools, `vault_is_external`), [[slice-109-add-post-flip-vault-conflict-safety]] (post-flip queue CAS), [[slice-110-make-pipeline-vault-location-agnostic]] (suite agnostic), [[slice-106-route-project-frame-synth-via-vault-root]] (production reads), [[slice-111-route-in-loop-skill-vault-ops-via-seam]] (op-gate + R-32.a/.b capture), [[slice-112-make-prose-vault-location-agnostic]] / [[slice-113-bulk-convert-remaining-skills-to-vault-seam]] / [[slice-114-convert-agent-prose-to-vault-seam]] (prose seam)
- Vault refs: [[decisions/ADR-085]] (resolution + write-safety), [[decisions/ADR-089]] (git-coupled tools + `/commit-slice` RETIRE deferral), [[decisions/ADR-098]] (post-flip CAS), [[decisions/ADR-104]] (op-gate), [[decisions/ADR-105]] (`<vault>/` prose seam + carve-out classes), [[decisions/ADR-066]] (pre-flip git-tracked-vault invariant being retired here)
- Risk register: [[risk-register#R-32]] (+ sub-entries R-32.a active-folder bootstrap, R-32.b archive-`mv` coherence)
- Tools touched: `tools/_vault_paths.py`, `tools/_vault_git.py`, `tools/_vault_write.py`, `tools/vault_edit.py`, `tools/vault_flip_prose_inventory.py` (`--op-gate` / `--strict`), `tools/_worktree_paths.py`; skills `/commit-slice`, `/slice`, `/build-slice`, `/reflect`, `/archive`
- **New ADR**: `/design-slice` mints the flip-decision ADR (next free number, ADR-107+) recording the git-untrack decision + the R-32.a active-folder-location resolution + the R-32.b archive-source-routing resolution.

## Mid-slice smoke gate

At ~50% of build (config written + files moved, before prose/commit-slice work):
```
# from the slice worktree, with the external store live:
python -c "import tools._vault_paths as v, tools._vault_git as g; print(v.VAULT_ROOT, g.vault_is_external('.'))"
python -m pytest -q
python -m tools.vault_flip_prose_inventory --op-gate
```
Expected: `VAULT_ROOT` = external abs path, `vault_is_external` = `True`, suite green, op-gate `OP_DEFERRED_TO_FLIP` shrinking toward 0. If any tool mis-resolves, the suite reds, or a vault file fails the byte-faithful hash-compare → **STOP, diagnose, do not continue** (a mid-flip mis-resolve risks the very corruption R-32 guards against).

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (esp. no-data-loss, reversibility, op-gate buckets ∅)
- [ ] All 3 exploratory charters COMPLETED (or DEFERRED with rationale) with non-empty Findings
- [ ] R-32 status = `retired` in `architecture/risk-register.md`
- [ ] `/drift-check` passes against the flipped store; full audit suite (VWS-1 / SVW-1 / op-gate / PMI-1 / INST-1 / CAD-1) green
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
