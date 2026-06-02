# Design: Slice 099 create-worktree-at-slice-pick

**Date**: 2026-06-01 (rev 2026-06-02 — post-/critique ACCEPTED-FIXED edits B1–B4, M1–M3, m1–m3)
**Mode**: Standard

## What's new

- **`tools/_worktree_paths.py`** (NEW) — single source of truth for shared worktree-create logic. Hosts `canonical_worktree_path(slice_folder_name, main_repo_root)` and `slice_branch_name(slice_folder_name)` (moved out of `branch_workflow_audit.py`), plus a thin CLI (`python -m tools._worktree_paths --slice-folder <name> --repo-root <path>`) emitting path + branch on stdout so `/slice` and `/build-slice` prose compute them identically (AC5, primary create path). **Also hosts `seed_derived_dirs(main_repo_root, worktree_path)`** — copies the gitignored `diagnose-out/` + `graphify-out/` into a freshly-created worktree (R-20 seed), called by BOTH `/slice` (at pick-create) and `/build-slice` (only when *it* creates the worktree). This closes the **slice-093 (L47) / slice-088 (L71)-flagged gap**: BRANCH-2's `cp -r` seed is codified only in `/build-slice`, so moving the create to `/slice` would silently drop it.
- **`skills/slice/SKILL.md`** — new **Step 5.5 "Create the worktree at pick"** (between Step 5 scope-check and Step 6 write): once a candidate is settled, create the BRANCH-2 worktree + branch via the shared helper, **seed the R-20 derived dirs**, then write `mission-brief.md` + `milestone.md` **into the worktree**. Step 6.5 (PSQ-1 queue) re-scoped to the **two-tree pick sequence** below (regenerate the **main-tree** queue + append `## Pick log` + commit only the queue file on the default branch). Pick-time `WORKTREE=skip` fallback pre-creates a `build-log.md` Events stub (B4).
- **`skills/build-slice/SKILL.md`** — `### Branch state` reordered so **"worktree already exists → cd + verify"** (current point 2) is the **primary** path; the create branch (point 1) fires only when no worktree exists (legacy slice / `WORKTREE=skip`) and is the ONLY path that still runs `seed_derived_dirs` (a BRANCH-3 pick already seeded at `/slice`, so build must NOT re-seed/clobber); the dirty-default scaffolding dance (point 4) becomes legacy-only (never fires for a BRANCH-3 pick, whose default tree is clean).
- **`tools/slice_queue_writer.py`** — additive `## Pick log` append-only section with a **DISTINCT preservation path** (NOT the PSQ-2 claim mechanism — see B2 note below): `write_slice_queue` reads the existing file's literal `## Pick log\n…EOF` tail BEFORE regeneration and re-appends it verbatim AFTER `## Candidates`; new `record_pick(repo_root, slice_name, picker_identity, now)` appends one line and is **idempotent by scanning the existing pick-log block for a `- slice-NNN-<name> —` prefix** (double-pick → no-op). Picker identity comes from `slice_queue_claim.read_git_config_user` (fail-visible on unset).
- **`CLAUDE.md`** — BRANCH-2 brownfield-rules prose updated: worktree created at `/slice` pick-time (BRANCH-3), not `/build-slice`.
- **`architecture/decisions/ADR-090`** (NEW) + **`methodology-changelog.md`** BRANCH-3 entry at v0.81.0 (see "Methodology version-bump fan-out" below).

## What's reused

- BRANCH-2 worktree machinery — [[decisions/ADR-063]]: canonical path convention `<main-parent>/<main-name>-wt/slice-NNN-<name>`, `slice/NNN-<name>` branch, `git worktree add`, `WORKTREE=skip` escape-hatch. **Unchanged** — slice-099 only moves *when* the create fires.
- PSQ-1 queue writer — [[decisions/ADR-064]] (`tools/slice_queue_writer.py`) + PSQ-2 claim machinery / `read_git_config_user` — [[decisions/ADR-067]] (`tools/slice_queue_claim.py`). The `## Pick log` is an additive section on PSQ-1's "stable on-disk contract" (ADR-064 §Consequences explicitly permits additive sections/fields).
- `tools/_vault_write.safe_write_text` — R-32-safe vault write (sidecar lock + atomic replace). This is the **concurrency primitive for the pick-time queue write** (see "Concurrency model" below) — NOT PCR.
- `tools/branch_workflow_audit.py` — its **end-state** validation (worktree registered at canonical path on matching `slice/NNN` branch) is unchanged by the timing shift; the slice refactors its path helpers out to `_worktree_paths.py` + updates docstrings. (Its *cwd-mismatch* branch is affected — see M2 note + "Concurrency model".)
- [[slice-066-add-worktree-per-slice-discipline]], [[slice-067-add-parallel-slice-queue-output]], [[slice-072-add-psq-2-claim-machinery]] lineage.

## Pick-time sequence (the two-tree dance — addresses M3)

`/slice` runs in the **main tree** (on the default branch). A single `/slice` invocation touches two trees; the order + per-step failure handling is load-bearing:

1. Compute `wt_path` + `branch` via `python -m tools._worktree_paths`. (No side effects.)
2. `git -C <main> worktree add <wt_path> -b <branch> <default>`. **Failure** (path exists / branch collision) → STOP, surface; nothing else has run, no cleanup needed.
3. `seed_derived_dirs(<main>, <wt_path>)`. **Failure** → STOP, surface; `git worktree remove <wt_path>` to roll back (no scaffold written yet).
4. Write `mission-brief.md` + `milestone.md` into `<wt_path>/architecture/slices/slice-NNN-<name>/`. **Failure** → STOP, surface; roll back the worktree.
5. In the **main tree** (on the default branch): regenerate `architecture/slice-queue.md` `## Candidates` + `record_pick` append to `## Pick log` via `_vault_write.safe_write_text` — **`write_slice_queue` is invoked with `repo_root=<main-tree root>` (`git -C <main> rev-parse --show-toplevel`), NOT cwd-relative `Path('.')`** (M-add-4: the session may have `cd`'d toward the worktree in steps 2/4, so `.` would write the worktree's queue, not the main tree's). Then `git -C <main> add architecture/slice-queue.md && git -C <main> commit -m "chore(queue): pick slice-NNN-<name>"` — **only** the queue file. **Failure AFTER step 2 succeeded** → leaves an *orphan worktree* with scaffold but no committed pick-log line: surface the failure explicitly and instruct recovery (`git worktree remove` OR retry the queue commit). This orphan is the M1 abandoned-pick class — it shows as `IN_PROGRESS:slice` informational (see M1), NOT silently lost.

Scaffold lives in the worktree (on `slice/NNN`); only `slice-queue.md` is committed on the default branch. The two trees never both hold the default branch — the main tree holds it, the worktree holds `slice/NNN`.

## Concurrency model (addresses B1)

PSQ-2 is a **same-machine cooperative** model (ADR-067 §Adversarial model): cooperating sessions share ONE repo, so there is exactly ONE main tree with the default branch checked out (`git worktree add` refuses a branch already checked out elsewhere — two trees cannot both hold `master`). Two sessions racing `/slice` therefore interleave on that single main tree, NOT divergent branches:

- The queue **write** is serialized by `_vault_write.safe_write_text`'s sidecar lock (R-32-safe; existing primitive).
- The queue **commit** on the default branch is serialized by git's per-repo locks — the index lock (`.git/index.lock`, for `git add` + tree-build) and the ref lock (`refs/heads/<default>.lock`, for the ref advance); a contending `add`/`commit` fails visibly (`Unable to create '.git/index.lock'`) and is retried. (These are distinct locks; the net guarantee — serialized, fail-visible, retried — holds.)
- `record_pick` idempotency (prefix-scan) makes a retried pick a no-op rather than a duplicate line.

**PCR is NOT involved** — `parallel_conflict_resolver` resolves `git rebase`-stage conflicts at `/commit-slice --merge` Step 5b, a different mechanism that the pick-time path does not enter. **Cross-clone / multi-machine** queue coordination is explicitly OUT OF SCOPE (ADR-067 bounds PSQ-2 to same-machine cooperation); a multi-clone race would surface as a push non-fast-forward handled by the operator, not by this slice.

## Components touched

### `tools/_worktree_paths.py` (NEW)
- **Responsibility**: the ONE place the canonical worktree path + slice branch name are computed AND the R-20 derived-dir seed is performed for the **primary** create path, so `/slice`, `/build-slice` (primary), and `branch_workflow_audit` cannot drift (AC5).
- **Lives at**: `tools/_worktree_paths.py` (created). Underscore-prefixed shared helper, matching `_vault_paths.py` / `_vault_write.py` / `_stdout.py` convention.
- **Public surface**: `canonical_worktree_path(slice_folder_name, main_repo_root) -> Path`, `slice_branch_name(slice_folder_name) -> str`, `seed_derived_dirs(main_repo_root, worktree_path) -> None` (idempotency rule: per derived dir, if the target dir **does not exist** in the worktree → copy it; if it **exists at all** (even partially) → skip and do not clobber. Accepts the low-likelihood partial-seed risk; pinned by `test_seed_derived_dirs_idempotent`).
- **Key interactions**: imported by `tools/branch_workflow_audit.py` (internal audit use — its own `audit()` call sites at `:477`/`:583` rewire to the imported names); invoked as a CLI by `skills/slice/SKILL.md` + `skills/build-slice/SKILL.md` (primary path) prose.

### `skills/slice/SKILL.md` (MODIFIED)
- **Responsibility**: define the next slice AND, new at BRANCH-3, isolate it in a worktree at pick + record pick provenance.
- **Key interactions**: `_worktree_paths` (CLI), `slice_queue_writer.record_pick` + `write_slice_queue`, git (`worktree add` in main tree, queue commit on default branch in main tree).
- **Edges**: worktree-create slots in after candidate is settled (Step 3/3b) + after the scope-check (Step 5), before artifact writes (Step 6), per the two-tree sequence above. The pick-time `WORKTREE=skip` fallback (bootstrap slices like 099 itself): `/slice` does NOT create a worktree, writes scaffold to the main tree as pre-BRANCH-3, **and pre-creates a `build-log.md` with an Events section carrying the canonical bullet `- <YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>`** (the leading `- ` is load-bearing — `_WORKTREE_SKIP_LINE_RE` is anchored `^- \d{4}-…` at `branch_workflow_audit.py:75-78`, M-add-2) so the build-time `branch_workflow_audit` reads it unchanged (B4).

### `skills/build-slice/SKILL.md` (MODIFIED)
- **Responsibility**: build the slice in its worktree; now tolerant of a worktree that already exists from `/slice`.
- **Key interactions**: `_worktree_paths` (CLI, shared) on the create path, git worktree. **Idempotent**: detect-existing-then-cd is the primary path; create (+ seed) only if absent.

### `tools/slice_queue_writer.py` (MODIFIED)
- **Responsibility**: write/regenerate `slice-queue.md`; now also owns the append-only `## Pick log`.
- **Key interactions**: `slice_queue_claim.read_git_config_user` (picker identity), `_vault_write.safe_write_text`.
- **Edge (B2 — distinct preservation path, NOT PSQ-2 claim-preservation)**: PSQ-2 claim-preservation re-attaches `claimed_by`/`claimed_at` to surviving `### <name>` *entry keys* — a `## Pick log` is a top-level section with NO entry key, so `parse_queue_text` cannot see it. Instead, `write_slice_queue` reads the existing file's literal `## Pick log` tail before regenerating `## Candidates` and re-appends it verbatim; `record_pick` is idempotent by prefix-scan. **First-pick edge (M-add-3)**: when no `## Pick log` exists yet (fresh or pre-BRANCH-3 queue), the tail read finds nothing and `record_pick` **creates** the section after `## Candidates`; when present, it re-appends. A regression test asserts BOTH the first-pick (create) and subsequent-pick (re-append) cases — a pre-existing pick-log line survives a `write_slice_queue` round-trip (the existing PSQ-2 round-trip tests do NOT cover this — they assert only entry-keyed claim survival).

### `tools/branch_workflow_audit.py` (MODIFIED — refactor + cwd-clarification)
- **Responsibility**: BRANCH-1/2 validation; **end-state** logic unchanged.
- **Change**: import `canonical_worktree_path` + `slice_branch_name` from `_worktree_paths`; docstring names BRANCH-3 pick-time creation. **M2 clarification**: end-state validation is unchanged, but the previously-dormant `worktree-cwd-mismatch` branch (`:600-620`, fires when the slice branch is in a worktree AND cwd is the main tree) now has live in-flight instances from pick onward. **No audit-logic change is needed** because every pre-finish / mid-slice audit invocation runs from **within the worktree** (cwd = worktree → `_is_repo_root_a_worktree` true → the cwd-mismatch branch is not taken). The mid-slice smoke + `/design-slice` + `/critique` all operate in the worktree under BRANCH-3.

## Contracts added or changed

### `## Pick log` section in `slice-queue.md` (NEW, additive)
- **Defined in code at**: `tools/slice_queue_writer.py` (`record_pick` append + `write_slice_queue` read-tail/re-append preservation).
- **Shape**: a trailing `## Pick log` section; each line `- slice-NNN-<name> — picked <ISO-8601 UTC> by <name> <email>`. Append-only; preserved across regeneration via the read-tail/re-append path above (NOT the claim mechanism). Timestamp matches PSQ-1/PSQ-2's `%Y-%m-%dT%H:%M:%S%z` (`+00:00`-suffixed UTC).
- **Auth model**: picker identity = git `user.name` + `user.email` (same cooperative git-identity model as PSQ-2; not a security boundary — ADR-067 §Adversarial model inherited).
- **Error cases**: git identity unset → `ClaimUsageError` surfaced (fail-visible, never silent skip) — reuses `read_git_config_user`.

### `tools/_worktree_paths.py` CLI (NEW)
- **Defined in code at**: `tools/_worktree_paths.py`.
- **Shape**: `python -m tools._worktree_paths --slice-folder slice-NNN-<name> --repo-root <path>` → stdout: line 1 = canonical worktree path, line 2 = `slice/NNN-<name>`. Exit 0 success; exit 2 on a folder name failing `slice-NNN-<name>` (reuses the audit's split-slice-aware messaging). Encoding-disciplined: `_stdout.reconfigure_stdout_utf8()` at entry; any git subprocess (if added) passes `encoding="utf-8"` (cp1252 class).

## Data model deltas

None — markdown vault only; no DB/schema.

## Methodology version-bump fan-out (addresses B3)

This slice mints a new RULE-ID **BRANCH-3** on in-house methodology surfaces, so it must discharge the full forward-sync / entry-pin / PMI-1 obligation at `/build-slice` (and the pre-finish gate must list it):

1. **Changelog entry** — add `## v0.81.0 — <date>` section to `methodology-changelog.md` with the BRANCH-3 rule (partial-supersedes ADR-063 timing; PSQ cross-ref for the `## Pick log`).
2. **Entry-pin** — add `tests/methodology/test_methodology_changelog.py::test_v_0_81_0_branch_3_entry_present_in_repo_and_installed`. Plan this INSERT structurally separate from any PMI-1 gate Edit (slice-014 entry-pin-vs-PMI-1 discipline).
3. **Atomic 5-part PMI-1 bump** — `VERSION` 0.80.0→0.81.0 + `plugin.yaml` `version:` + **`pyproject.toml` `[project].version`** + the `## v0.81.0` changelog header + installed `~/.claude/ai-sdlc-VERSION`. (**Build-time correction**, slice-099 /build-slice Phase D: this design originally said "4-part" and omitted `pyproject.toml`. The codebase's canonical PMI-1 atomic bump is 5-part per the v0.68.0/v0.80.0 entry-pin precedent — and `pyproject.toml` carries a STATIC `version` that drives the `pip install --upgrade` wheel, so omitting it would have left the rebuilt `ai-sdlc-tools` at 0.80.0 and **failed TVFS-1**. The installed `~/.claude/methodology-changelog.md` forward-sync is a SEPARATE MCFS-1 leg, not a PMI-1 part, per the v0.68.0 pin's own framing.)
4. **Forward-sync legs** — run `tools/methodology_changelog_forward_sync.py` (MCFS-1) + `tools/ai_sdlc_version_forward_sync.py` + `tools/ai_sdlc_tools_version_forward_sync.py`; all must pass.
5. **OSDG-1 re-sync** — re-sync the installed `~/.claude/skills/slice/SKILL.md` + `~/.claude/skills/build-slice/SKILL.md` copies and confirm `test_slice_skill_drift` + `test_build_slice_skill_drift` green (both edited here).
6. **R-28 parallel-slice caveat** — slice-098 is in flight; forward-sync/content-equality audits compare each worktree against the single shared `~/.claude/`. If a drift test red-fails on a file slice-099 didn't touch, apply the documented `git diff HEAD -- <file>` empty ⇒ sibling-induced ⇒ deferral procedure; NEVER clobber the shared install.

(`tools/_worktree_paths.py` is **underscore-prefixed** → no `plugin.yaml`/`install_audit.py`/INSTALL.md inventory count-bump fan-out / no PMI-1 module-count change, per the `_vault_write`/`_vault_paths` MEPD precedent.)

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_worktree_paths.py` | `tools/branch_workflow_audit.py` (import) + `skills/slice/SKILL.md` & `skills/build-slice/SKILL.md` (CLI + seed) | `tests/methodology/test_worktree_paths.py::test_canonical_path_and_branch` + `::test_seed_derived_dirs_idempotent` (incl. partial-seed case) + existing `tests/**/test_branch_workflow_audit*.py` (exercise imported fns) | — |

(The SKILL.md edits + `slice_queue_writer.py`/`branch_workflow_audit.py`/`CLAUDE.md` changes modify existing files — no new-module rows. Drift tests for `slice` + `build-slice` SKILL.md (OSDG-1 / mini-CAD) cover the prose edits.)

## Decisions made (ADRs)
- [[ADR-090]] — create the slice worktree at `/slice` pick-time (partial-supersedes ADR-063 BRANCH-2 build-time timing); `slice-queue.md` remains a shared main-tree coordination ledger with an append-only `## Pick log` recording pick provenance — reversibility: **cheap** (skill-prose timing reorder + additive queue section; revert = move the create step back to `/build-slice`).

## Authorization model for this slice

Pick-provenance records the git-configured identity (`user.name` + `user.email`) of whoever ran `/slice` — the same cooperative, non-security git-identity model as PSQ-2 (ADR-067). No new auth surface. Identity-unset is a hard, visible failure (not a silent skip).

## Error model for this slice

- **Git identity unset at pick** → surface `read_git_config_user`'s `ClaimUsageError` (fail-visible; R-7 silent-disable class). `/slice` reports it and does not silently write an unattributed pick-log line.
- **Concurrent pick (same machine, one main tree)** → queue write serialized by `_vault_write` sidecar lock; queue commit serialized by git's index lock; a contending commit fails visibly and is retried; `record_pick` prefix-scan idempotency makes the retry a no-op (NOT PCR — see Concurrency model).
- **`git worktree add` failure at pick** → STOP, surface; nothing else has run.
- **Step 5 (queue commit) failure after a successful worktree-add** → orphan worktree with scaffold but no committed pick-log: surface explicitly + recovery instruction (M1 abandoned-pick class; visible as `IN_PROGRESS:slice`, never silently lost).
- **Pick-time `WORKTREE=skip`** (bootstrap / legacy) → scaffold on main tree as pre-BRANCH-3 + `/slice` pre-creates a `build-log.md` Events stub with the canonical bullet `- <YYYY-MM-DD HH:MM> DEVIATION: WORKTREE=skip — rationale: <text>` (leading `- ` required by the audit regex, M-add-2) so the build-time audit passes unchanged (B4).

## Post-critique resolution notes

1. **master-clean vs PSQ cross-session visibility** (the ATTACK-LENS tension): the shared-main-tree-queue (Q1) is a *narrow, intentional* queue-only commit on master per pick — master stays clean of *slice work* (scaffold/design/ADRs in the worktree); the queue ledger stays visible to parallel sessions.
2. **Concurrency (B1 — RESOLVED)**: same-machine single-main-tree serialization via `_vault_write` lock + git index lock; PCR is NOT involved; cross-clone out of scope. See "Concurrency model".
3. **Pick-log survival (B2 — RESOLVED)**: distinct read-tail/re-append preservation path, NOT the PSQ-2 claim mechanism; idempotent by prefix-scan; regression-tested. See `slice_queue_writer.py` Edge.
4. **Abandoned pick (M1 — DOWNSCOPED)**: a picked-but-never-built slice shows as `IN_PROGRESS:slice` **informational** (`halt: false`) — it is *listed*, NOT surfaced as an anomaly. No new detection class this slice; full distinction (a real abandoned-pick discriminator) is DEFERRED to a follow-up candidate (`abandoned-pick-detection`). BRANCH-3 raises the abandon rate (worktree created before build-commitment) — noted for that follow-up. The must-not-defer is corrected accordingly.
5. **R-20 derived-dir seed (PRE-EMPTED)**: shared `seed_derived_dirs` at `/slice` pick-create; `/build-slice` seeds ONLY when it creates the worktree (no double-seed). R-20 stays `retired`, scope-clarified to the pick-create model — NOT reopened.
6. **WORKTREE=skip-at-pick (B4 — RESOLVED)**: `/slice` pre-creates a `build-log.md` Events stub with the canonical line; build-time audit unchanged.
7. **Audit cwd (M2 — RESOLVED)**: end-state logic unchanged; all pre-finish/mid-slice audit invocations run from within the worktree so the cwd-mismatch branch stays correct.
8. **AC5 scope (m2)**: "single source of truth" applies to the *primary* (non-legacy) create path; the legacy `WORKTREE=skip`/dirty-default escape-hatch prose in `build-slice` retains its inline convention for self-containment. Mission-brief AC5 wording narrowed accordingly.
