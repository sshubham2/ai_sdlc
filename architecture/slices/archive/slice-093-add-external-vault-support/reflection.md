# Reflection: Slice 093 add-external-vault-support

**Date**: 2026-05-31
**Shipped**: YES-WITH-DEFERRALS

## Validated

- **3-tier resolution precedence** (`tools/_vault_paths.py`: env `AI_SDLC_VAULT_ROOT` → git-common-dir-keyed config → `architecture/` default) — validated by live evidence in validation.md (default with no env/config = `architecture`; env override = `X:\ext-vault`; pointer-tier derives `~/.aisdlc/<hash>`) + `test_resolution_precedence_env_over_pointer_over_default`.
- **The no-flip backward-compat invariant** (the slice's safety contract) — validated: unset/no-config default is byte-`Path("architecture")`, full suite **1316 PASS** with the *only* sanctioned existing-test change being the count-pin 12→15. Every existing tool/test/skill behaves identically.
- **C1 keying** (the spike's central claim) — re-confirmed LIVE: `git rev-parse --path-format=absolute --git-common-dir` is byte-identical across main + this worktree (both `C:/Users/sshub/ai_sdlc/.git`), and by `test_git_common_dir_key_stable_across_main_and_worktree` against a real `git worktree add` fixture.
- **C2 concurrent-write safety / R-32 mitigation** (`tools/_vault_write.py`: `safe_write_text` sidecar-lock + atomic `os.replace` + bounded EPERM-retry; `safe_append_text` `O_APPEND` + lock) — validated by 7 passing tests AND empirically by the code-Critic: pure `O_APPEND` loses **26/30** lines without the lock, concurrent `os.replace` to one target EPERMs — the tests have real teeth, the lock is load-bearing.
- **Install capability without flip** (AC3) — INSTALL.md Step 3i writes ONLY the global `~/.claude/ai-sdlc-vault-base` via `safe_write_text`; a pre-existing `architecture/` sentinel is byte-identical afterward (`test_install_writes_global_base_config_without_moving_vault`).
- **Seam completeness, allowlist unchanged** (AC4) — live `VAULT_ROOT importers = 10` (unchanged); 093 migrates NONE; classification map present in design.md.
- **ADR-085 extends (not supersedes) ADR-065** — `supersedes: null`; SUP-1 clean; R-32 registered `mitigating`.

## Corrected

- **AC4 scope: "migrate ~6 tools" → "migrate NONE"** (corrected at `/design-slice`, pre-build) — the actual scan showed `parallel_conflict_resolver` / `stranded_slice_audit` / `pulse_worktree_resolver` are git/worktree-model-coupled, so naive `architecture/`→`VAULT_ROOT` migration is *wrong*; they are rethought at the 094 flip, not migrated. Captured in this slice's [[design.md]] §Tool-migration classification map + [[ADR-085]]. No further correction needed at reflect.
- **"Structural replacement for PCR-on-vault-files" over-claim → narrowed** (Critic M2) — the whole-file `safe_write_text` alone loses a concurrent append; the claim now explicitly covers BOTH whole-file edits AND the append-log (`safe_append_text`). Corrected in design.md + ADR-085 before build.
- **No code-vs-design deviation** — shipped code matches design rev-2. The one build deviation was a worktree-setup artifact (the `diagnose-out/` cp -r seed; see Discovered), not a code change. build-log.md records it.

## Discovered

- **R-20 seed-gap resurfaces under the worktree-at-`/slice` model** — impact: slice-094 must own this. The R-20 `cp -r diagnose-out/ graphify-out/` seed was "retired" at slice-074 by codifying it into `/build-slice`'s worktree-create prereq. But THIS slice dogfooded creating the worktree at `/slice` time, which never runs `/build-slice`'s seed step → mid-slice smoke `test_bcr_1_sc054_round_trip_inputs_invariant` failed until the dir was manually seeded. The retirement holds for the *create-at-`/build-slice`* model only; the worktree-at-`/slice` model (formalized in slice-094) reopens it. Forward-note added to [[risk-register#R-20]]; the seed must move to `/slice` time (or a shared worktree-create helper invoked by both).
- **cp1252-at-import observability footgun** (code-Critic M1; RSAD-1 self-application) — impact: a third distinct cp1252 sub-class. The must-not-defer "log which vault root was resolved" was delivered via bare `print(…, file=sys.stderr)` run at module import; on a non-ASCII vault path under a raw cp1252 stderr this raises `UnicodeEncodeError` and the import fails for all 10 importers — the repo's OWN documented footgun. Latent in 093 (default path is ASCII/silent), fires post-flip or env-set. Fixed in-slice (leaf-safe `_stderr` helper: UTF-8 bytes to `sys.stderr.buffer`, `errors="replace"`, ascii-fold fallback). The cp1252 class is now N≥8 spanning THREE mechanisms: stdout (UTF8-STDOUT-1), subprocess-capture (BC-PROJ-15/BC-GLOBAL-5), and now **bare-print-to-stderr-at-import**.
- **git-subprocess decode asymmetry on a new tool** (code-Critic m1; the R-30/slice-091 class) — `_read_common_dir_config`'s `subprocess.run(encoding="utf-8")` can raise `UnicodeDecodeError` in the reader thread on non-UTF-8 git output, NOT caught by `except (OSError, SubprocessError)` (`UnicodeDecodeError` ⊄ `OSError`) → ugly thread traceback + mis-classified as "no config" (defeats R-7 fail-visible). Fixed in-slice via the slice-091 pattern: bytes-capture + explicit main-thread `.decode` with `UnicodeDecodeError` caught + WARN.
- **R-32 is now LIVE-pending-094** — registered `mitigating` during build (the scariest spike finding). The mitigation infrastructure ships ahead of the flip; R-32 becomes a live hazard only when slice-094 makes the vault untracked + shared (removing git/PCR's loud conflict resolution).

## Deferred

- **The flip itself** (SKILL-prose rewrite + physical move of `architecture/`+`diagnose-out/`+`graphify-out/` + the C5 history decision) — reason: tools + prose must flip atomically (coherence constraint); out of scope per mission-brief. Lands in: **slice-094**.
- **Wire `safe_write_text`/`safe_append_text` into every real vault writer + rethink the 3 git-coupled tools** (`parallel_conflict_resolver` / `stranded_slice_audit` / `pulse_worktree_resolver`) per the classification map — reason: only correct *at* the flip. Lands in: **slice-094**.
- **`.lock`-sidecar accumulation** (code-Critic m3) — at the flip, real vault writers gain permanent `.lock` siblings beside `_index.md`, etc. — reason: purely latent in 093 (`safe_write_text` only test-exercised in `tmp_path`; INSTALL writes to `~/.claude/`; `git ls-files architecture/**/*.lock` empty). Fix: dedicated `.aisdlc-locks/` dir OR confirm every vault-scanning glob filters `*.md`/`is_dir()` + pin. Lands in: **slice-094**.
- **M4 residual** — stale `_ERROR_MESSAGE_STRING_EXCLUSIONS` (5 pinned tuples vs 7 real `NOT VAULT_ROOT-routed` marker sites) — reason: 093 migrates nothing and the orphan test matches by marker substring, so it's latent. Lands in: **slice-094** re-sync.
- **m-add-1** — stale `8-element` comments at `test_vault_root_constant.py:41,281` (the frozenset is 10; `test_migration_site_allowlist_pinned` computes dynamically so passes) — reason: pre-existing, not introduced by 093; do not touch mid-slice beyond the sanctioned count-pin. Lands in: **slice-094** re-sync.

## Critic calibration

Per TRI-1, scored against each finding's `## Triage` disposition + reality observed during build/validate. **First-Critic (design)**: B1, B2 (Blockers), M1–M4 (Majors), m1–m3 (Minors), all ACCEPTED-FIXED in rev-2. **Meta-Critic (DR-1 EXTEND)**: confirmed all nine VALID with correct severity (zero false-positive), +B-add-1, +m-add-1. **Code-Critic (CRSI-1)**: 0B/1M/3m.

- B1 (TF-1 cites known-bad `tests/tools/`): **VALIDATED** — ACCEPTED-FIXED; third recurrence of the twice-recorded namespace-collision class; fix necessary.
- B2 (AC3 vs design 093/094 scope self-contradiction + phantom `_vault_write` consumer): **VALIDATED** — ACCEPTED-FIXED; routing the base write through `safe_write_text` made the wiring honest; reality confirmed the contradiction was real.
- M1 (`test_count == 12` pin breaks at +3): **VALIDATED** — would have gone RED at build; the sanctioned 12→15 change is the only existing-test change, distinct from the resolution no-behavior-change invariant.
- M2 (whole-file-only misses append-log lost-update): **VALIDATED** — code-Critic empirically confirmed the hazard (26/30 lines lost without the lock); `safe_append_text` was necessary.
- M3 (Windows-only EPERM test strategy): **VALIDATED** — the mock-`os.replace`-raises strategy is the correct cross-platform reproduction; meta-Critic independently confirmed.
- M4 ("5 error-prose sites" wrong — there are 7; stale exclusion tuples): **VALIDATED** — independent grep re-derived exactly 7; correctly scoped the stale-tuple re-sync out to 094.
- m1 (advisory→mandatory lock terminology; never lock the replace target): **VALIDATED** — sidecar `.lock` released after `os.replace` is correct on Windows mandatory-locking semantics.
- m2 (two parsers for the one-line config): **VALIDATED** — shared SSoT `_CONFIG_REL` constant + `test_inline_and_helper_config_readers_agree` parity pin; code-Critic confirmed the SSoT is genuinely shared.
- m3 (MEPD-1 discharge branch unspecified): **VALIDATED** — EXCLUDE posture (no RULE-ID / no changelog / no VERSION bump; underscore `_vault_write` → no PMI-1 count bump) confirmed correct; forward-sync gates no-op at unchanged VERSION (observed green at build Step 6).
- **B-add-1** (meta-Critic — B1-fix residual at `ADR-085:57`, `tests/tools/` survived the rev-2 sweep): **VALIDATED-ON-RECONSIDERATION** — the Builder's B1 sweep was scoped to the two named artifacts and under-swept the ADR; meta-Critic caught the fix-delta; ACCEPTED-FIXED.
- m-add-1 (meta-Critic — "10 consumers" vs stale "8-element" comments): **NOT-YET** — DEFERRED to slice-094 re-sync; re-score there.
- code-Critic M1 (cp1252-at-import print crash): **VALIDATED** — RSAD-1 self-application failure, fixed in-slice + regression test.
- code-Critic m1 (git-decode `UnicodeDecodeError` ⊄ `OSError`): **VALIDATED** — R-30/slice-091 class, fixed in-slice.
- code-Critic m2 (`safe_append_text` lacked EPERM-retry): **VALIDATED** — resilience asymmetry with `safe_write_text`, fixed in-slice + regression test.
- code-Critic m3 (`.lock` accumulation at flip): **NOT-YET** — DEFERRED to slice-094; re-score there.

**Missed by Critic**: the design-Critic + meta-Critic stack missed all THREE line-level execution defects the code-Critic caught — cp1252-at-import (M1), git-decode asymmetry (m1), append-EPERM asymmetry (m2). This is the documented structural division of labor (slice-037 audit-vs-real-artifact law), NOT a Critic-prompt gap: the design stack reads mission-brief/design/ADR prose and cannot reach execution-only / line-level defects. The sharpening signal is that code-Critic M1 was an **RSAD-1 self-application failure** — the slice shipping vault infrastructure for the external-vault initiative nearly shipped its own cp1252 crash.

**Pattern**: 3-Critic complementarity held again on an infrastructure slice with three non-overlapping defect classes — design-Critic = vault-truth/drift (B1 phantom path, B2 scope-contradiction, M4 count) + edge cases (M2 append, M3 EPERM); meta-Critic = the Builder's fix-DELTA ("a Critic's own fix is a fresh claim", B-add-1, now N≥5) + zero-false-positive confirmation; code-Critic = execution-only line-level (cp1252-at-import, git-decode, EPERM-asymmetry). **Do NOT collapse the stack.** Second signal: the cp1252 class is now self-applying (N≥8, three mechanisms) — RSAD-1 ("a slice must survive its own repo's discipline") is the meta-lesson; observability/logging added to a leaf module at import time must use the leaf-safe cp1252-defensive stderr write.

## Lessons for next slice (094 — the flip)

- **Move the R-20 `diagnose-out/`+`graphify-out/` seed to `/slice` time** (or a shared worktree-create helper invoked by both `/slice` and `/build-slice`) — the worktree-at-`/slice` model breaks the `/build-slice`-anchored seed codification. This is the broader-initiative evidence the dogfooding surfaced.
- **At the flip, wire `safe_write_text`/`safe_append_text` into every real vault writer AND rethink the 3 git/worktree-coupled tools** per the design.md classification map — do NOT naively `VAULT_ROOT`-migrate `parallel_conflict_resolver` / `stranded_slice_audit` / `pulse_worktree_resolver`.
- **Re-sync the two stale pin-comment drifts deferred from 093**: M4's `_ERROR_MESSAGE_STRING_EXCLUSIONS` (5→7 marker sites) + m-add-1's "8-element"→10 comments, both at `test_vault_root_constant.py`. Both are latent-but-correct today; the flip is the venue.
- **Solve `.lock`-sidecar accumulation (m3) before real writers gain permanent `.lock` siblings** — dedicated `.aisdlc-locks/` dir OR confirm every vault-scanning glob filters `*.md`/`is_dir()` + pin (`parallel_conflict_resolver:894`, `slice_queue_writer`, `stranded_slice_audit`).
- **Any leaf-module observability added at import time uses the cp1252-defensive stderr write, never bare `print()`** — the third cp1252 sub-class, now self-witnessed.

## Vault updates made (thin vault)

- [[risk-register.md]] — R-20: appended a forward-note (resurfacing under the worktree-at-`/slice` model → slice-094 must move the seed to `/slice` time). R-32 already registered `mitigating` during build — no change.
- [[lessons-learned.md]] — appended the Slice 093 entry.
- [[shippability.md]] — appended row #101 (slice-093 critical path: resolution-precedence + no-flip default + C2 write/append safety).
- This slice's [[design.md]] / [[build-log.md]] — no `/reflect`-time correction (code matched design rev-2; deviations already logged).
- No ADR superseded — [[decisions/ADR-085]] extends [[decisions/ADR-065]] (`supersedes: null`), correct.
- BCR-1: no `**Closes:** SC-` sentinel in mission-brief or this reflection → no-op (no `diagnose-out/backlog.md` round-trip).
