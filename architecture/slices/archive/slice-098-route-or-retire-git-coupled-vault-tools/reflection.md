# Reflection: Slice 098 route-or-retire-git-coupled-vault-tools

**Date**: 2026-06-02
**Shipped**: YES

## Validated
- **Class-A routing through `VAULT_ROOT` is byte-identical on the no-flip default** — validated by the full suite (1450 PASS, env unset) + `test_audit_log_path_no_flip_byte_identity` + the mid-slice pulse byte-identity check. The `<root> / VAULT_ROOT / <subpath>` form collapses to the original literal when `VAULT_ROOT == Path("architecture")`.
- **External-root flip-readiness works via subprocess env-injection** — `test_external_root_flip_readiness_and_retire` (real `python` subprocess, `AI_SDLC_VAULT_ROOT` set) confirms pulse resolves under the external root + PCR/stranded RETIRE. The consumer-freeze cascade (slice-093) held exactly as design predicted: in-process monkeypatch does NOT propagate; only a fresh process re-reads the env.
- **The two-literal-class model partitions the real coupling** — design+meta Critics' B1/M4 enumeration was correct; PCR's coupling is mostly git-string identity (`_SOFT_FILE_SET`/`qrel`/`git add`), not filesystem composition. 21 Class-B literals + the routed Class-A sites, cleanly separated.

## Corrected
- **The binding RETIRE signal is store-LOCATION (`vault_is_external`), NOT the per-pathspec `git ls-files` tracked-check** that `/critique` M1 + ADR-089 r2 originally specified. TWO build-time deviations (both USER-RATIFIED, documented in ADR-089 §Decision + design.md AS-BUILT banner + build-log + drift-log): (1) the tracked-check over-RETIRES every in-tree stranded slice (its content lives only on its branch, never in the invoking index — 4 existing fixtures encode this); (2) the tracked-check returns True for the still-tracked in-tree `slice-queue.md` in the external-abs-`VAULT_ROOT`-but-not-moved window → MISSES the B2 corruption. Updated in [[ADR-089]] + this slice's [[design.md]] (AS-BUILT banner) + drift-log entry.
- **R-32 residual narrowed** — the "3 git-coupled tools" sub-residual is CLOSED (all 3 now routed + RETIRE-guarded, flip-ready). R-32 stays `mitigating`; residual narrowed to physical move + git-untrack + prose + the post-flip PCR conflict-mechanism wiring. Updated in [[risk-register.md]] (status unchanged — STP-1 clean).

## Discovered
- **The worktree-at-`/slice` model dropped the R-20 seed AGAIN (N=2: slice-093 → slice-098)** — `diagnose-out/` + `graphify-out/` were absent in the worktree (the `/build-slice` `cp -r` seed never ran because the worktree was created at `/slice` time, via the user's master-clean request). I manually re-seeded. **slice-099 (`create-worktree-at-slice-pick`, already queued) is precisely the fix** — it should move the seed to worktree-create-at-`/slice`. Impact: confirms slice-099's value; no new risk needed (R-20 scope-clarified at slice-093).
- **The per-pathspec tracked-check is unsound for git-coupling-to-vault-CONTENT in two distinct ways** — surfaced ONLY by running against the real stranded fixtures (over-RETIRE) + tracing PCR's B2 control flow (false-True). Neither the design-Critic nor the meta-Critic caught it (both reasoned about the abstract "is it tracked" question); the code-Critic confirmed the unified fix is sound but did not independently find the stranded-fixture break (the full suite did). The store-location signal is the correct abstraction: "has the vault left the git tree?" not "is this specific file in the index?"
- **`architecture/` IS git-tracked in this repo (918 files)** — slice-044's STP-1 "architecture/ is gitignored" note is stale/inapplicable here. Recorded so a future maintainer doesn't trust that note.

## Deferred
- **The actual external-vault flip** (physical move of `architecture/` + git-untrack + prose rewrite + post-flip PCR `_vault_write`-based conflict-mechanism replacement) — lands in: slice-099+ (`flip-vault-to-external-shared-root`, LARGE). Per ADR-089 §Residual / out-of-scope.
- **AST-scanner `joinpath`/`os.path.join`/2-hop-alias false-negatives** (/code-review M1) — the AC1 guarantee is honestly bounded to the `Path / 'architecture'` div-form + one-hop alias; the 3 tools use none of those shapes. Durable scanner extension lands in: the flip slice or a bundled-cleanup.
- **`vault_pathspec_is_tracked` + `VaultGitUnavailable`** (/code-review m1) + **`VAULT_ROOT_IS_DEFAULT`** (m2) — defined+tested but unconsumed by production; intentional flip-slice primitives. The flip slice wires `vault_pathspec_is_tracked` (it IS the precise per-file signal the flip's git-untrack mechanics need) or retires it.

## Critic calibration

3-Critic stack, **zero false-alarms across all three personas; non-overlapping defect classes** — and the strongest single-slice evidence yet that the stack's job is to correct the BUILDER (and each other's) fixes, not just the original design.

**Design-Critic** (critique.md, BLOCKED → all VALID, code-confirmed against disk): B1 (PCR coupling is git-string not filesystem — the keystone diagnosis), B2 (external `out_path` → `relative_to` ValueError → silent claim-drop), M1 (proxy ≠ untracked), M2 (env-set-before-flip stranding), M3 (Windows backslash/abs pathspec), M4 (stranded sites mis-located + `ls-tree` omitted), M5 (AST-scan vacuity), m1/m2. All ACCEPTED-FIXED/PENDING.

**Meta-Critic** (critique-review.md, EXTEND, all VALID — re-attacked the BUILDER's r2 fixes): **M-add-1** (the B2-fix guard-placement claim was control-flow-imprecise — L216-217 fire upstream in `diagnose_conflict`; real protection is U-file-absence→UNKNOWN), **M-add-2** (stranded dual-class single-variable), **M-add-3** (AST predicate can't match variable-mediated L322). The "a Builder's own fix is a fresh claim" pattern fired at the meta layer exactly as designed.

**code-Critic** (code-review.md, 0B/2M/4m, advisory): M1 (AST-scanner narrower than the design claim — joinpath/2-hop false-neg), M2 (M-add-2 pathspec VAULT_ROOT-derived not verbatim — a class-purity drift it flagged as design-code disagreement). All cleared the 8 high-value targets it attacked (vault_is_external edges, B2 reachability, M-add-1 non-vacuity, 21 markers, byte-identity).

**Missed by Critic**: NONE of the three Critic layers caught that the **per-pathspec tracked-check is unsound for BOTH tools** — it was surfaced by EXECUTING against the real stranded fixtures (the full suite) + tracing PCR's B2 control flow during build. The design+meta Critics ratified the tracked-check as the keystone; only running it found the break. This is the slice-087/091 lesson again: **a newly-minted signal must be EXECUTED against the repo's real fixtures/control-flow at build time, not reasoned about at design time.** Strong `/critic-calibrate` probe candidate: "has this guard signal been run against the repo's real test fixtures AND traced through the actual call graph (not the function it's most natural to name)?"

**Pattern**: design-Critic = design-contract/enumeration; meta-Critic = the Builder's fix-delta; code-Critic = runtime-execution + design-code-drift. Three personas, three non-overlapping classes — AND the load-bearing correction (the unified signal) came from neither Critic but from EXECUTION. Do NOT collapse the stack; AND do not trust a freshly-minted guard signal until it has run against the real corpus.

## Lessons for next slice
- **A guard signal that decides "is a git-tree read of vault CONTENT applicable" must key on store-LOCATION (is the vault outside the repo tree), NOT per-file git-tracked-ness** — a stranded slice's content lives only on its branch (tracked-check over-RETIREs), and an external-but-not-yet-moved vault leaves the in-tree file still tracked (tracked-check false-True misses the corruption). The precise abstraction is "has the vault left the git tree", answered by PurePath ancestry (`resolved != root and root not in resolved.parents`) — immune to the `str.startswith` sibling-prefix bug.
- **EXECUTE a newly-minted guard signal against the repo's REAL test fixtures + trace the ACTUAL call graph at BUILD time** — the design+meta Critics both ratified the per-pathspec tracked-check; it was unsound, and only running it (stranded fixtures over-RETIRE) + tracing control flow (PCR B2) found it. Reasoning about "is it tracked" at design time missed what execution showed in minutes. (Extends the slice-087 classifier-execution + slice-091 real-runtime lessons.)
- **The worktree-at-`/slice` model drops the R-20 `diagnose-out/`+`graphify-out/` seed (N=2)** — re-seed manually until slice-099 (`create-worktree-at-slice-pick`) moves the seed to `/slice`-time worktree creation. The lesson slice-093 logged recurred verbatim.
- **A VAULT_ROOT-derived `.as_posix()` pathspec is MORE correct than a verbatim `architecture/...` literal** — it tracks the vault's actual location (handles the relocated-but-tracked `<repo>/vault/` case the literal would miss), and the absolute-external case is caught by the location guard firing first. "Class-B never routed" means "never feed a backslash/absolute Path into a git pathspec", NOT "never derive the forward-slash string from VAULT_ROOT".

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-32 residual narrowed (3-git-coupled-tools sub-residual CLOSED; status stays `mitigating`) via `vault_edit rewrite` (CAS).
- [[lessons-learned.md]] — slice-098 entry appended via `vault_edit append`.
- [[shippability.md]] — added the no-flip + RETIRE critical-path row via `vault_edit append`.
- This slice's [[design.md]] — AS-BUILT banner (binding signal = `vault_is_external`) + M-add-2/M1 amendments (the build-time deviations).
- [[decisions/ADR-089]] — §Decision/§Consequences/§Residual reflect the as-built unified signal.
- [[drift-log.md]] — slice-098 CLEAN entry (DCE-1 marker).
- No new RULE-ID, no VERSION/methodology-changelog bump (MEPD-1 EXCLUDE — underscore module `tools/_vault_git.py`).
