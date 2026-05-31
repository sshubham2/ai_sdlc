# Critique: Slice 093 add-external-vault-support

**Critic reviewed**: mission-brief.md, design.md, ADR-085, project-frame.md, spike-external-shared-vault.md + field-recon.md (required reading)
**Date**: 2026-05-31
**Result**: CLEAN (post-TRI-1 ratification; first-Critic pass: NEEDS-FIXES; dual-review: EXTEND)

## Summary

Architecture sound; C1 keying empirically re-validated by the Critic (byte-identical `--path-format=absolute --git-common-dir` across main + worktree). One Blocker re-introduces the twice-recorded known-bad `tests/tools/` path; a second Blocker is a 093-vs-094 scope self-contradiction that cascades into a phantom wiring justification; four Majors (count-pin break, append-log lost-update gap, Windows-only EPERM test strategy, "5 vs 7" prose drift); three Minors (mandatory-lock terminology, two-parser divergence, MEPD-1 discharge branch). All nine ACCEPTED-FIXED in rev-2 artifacts before triage.

## Findings

### Blockers (must address before /build-slice)

#### B1: TF-1 plan cites `tests/tools/` — the project's twice-recorded known-bad path convention
- **Claim under review**: mission-brief TF-1 rows AC2/AC3 + design.md cited `tests/tools/test_vault_safe_write.py` / `tests/tools/test_install_vault_config.py`.
- **Issue**: `tests/tools/` does not exist and is **known-bad** — slice-021 build-log DEVIATION-2 relocated it to `tests/methodology/` (namespace collision between a `tests/tools/` test-package and the top-level `tools/` Python package breaks `from tools import …`); `lessons-learned.md:882` records a later recurrence through 4 gates. This is the phantom-path-convention class, third recurrence.
- **Evidence**: `archive/slice-021-…/build-log.md:22,84`; `lessons-learned.md:882`; `ADR-019:135`; `tests/` has no `tools/`.
- **Proposed fix**: rename all cited paths to `tests/methodology/…`.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief TF-1 rows AC2/AC3 + design.md §What's new / §Test-pin + §Components all now use `tests/methodology/test_vault_safe_write.py` + `tests/methodology/test_install_vault_config.py`. FBCD-1 grep-swept; no `tests/tools` remains in either artifact.

#### B2: AC3 says 093 writes the per-project config; design.md says that's 094 — and the `_vault_write` wiring rests on the contradiction
- **Claim under review**: mission-brief AC3 ("writes the per-project pointer/config") vs design.md ("writing `$COMMON_DIR/aisdlc/vault-root` is slice-094") vs the wiring exemption ("`_vault_write` invoked by INSTALL.md").
- **Issue**: cannot all hold. If per-project write is 094, 093's INSTALL.md only writes the per-machine `~/.claude/ai-sdlc-vault-base` (no concurrency) and `_vault_write` would have zero non-test consumers in 093 (speculative generality). If AC3 is literal, the middle config-tier is exercised in 093 — contradicting the no-flip framing + `test_default_unchanged_when_no_env_no_pointer`.
- **Evidence**: mission-brief AC3; design.md L13/L39/L55; ADR-085 (base-only).
- **Proposed fix**: 093 writes ONLY `~/.claude/ai-sdlc-vault-base`; per-project `vault-root` write → 094; make the wiring honest.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief AC3 rewritten to "writes ONLY the GLOBAL base config … the per-project vault-root write is slice-094." design.md routes the base write through `_vault_write.safe_write_text` → `_vault_write` now has a **real 093 consumer** (INSTALL.md base-config write) + full test coverage → wiring-matrix row is a genuine consumer (no exemption); `write_vault_root_config` is test-exercised in 093, production-called at 094 (stated). Contradiction removed.

### Majors (address this slice)

#### M1: `test_full_pytest_baseline_preserved` pins `test_count == 12`; AC1 adds 3 functions → guaranteed FAIL, unmentioned
- **Issue**: AC1 adds 3 functions to `test_vault_root_constant.py`; its `test_count == 12` pin (L177-193) → 15 → FAIL. Unmentioned, and collides head-on with the slice's own mid-slice gate ("any existing test behavior change → STOP") + must-not-defer.
- **Evidence**: `tests/methodology/test_vault_root_constant.py:177-193`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §Test-pin + count updates: AC1 raises the pin 12→15 (+docstring); explicitly designates this as the ONE sanctioned existing-test change, distinct from the no-behavior-change invariant on the *resolution path*. Mission-brief mid-slice gate reworded to match.

#### M2: `safe_write_text` is whole-file-only; field-recon names append-log lost-update as a distinct, unaddressed hazard
- **Issue**: highest-churn shared vault files are append-only (ADRs/SUP-1, `risk-register.md`, PCR log `.open("a")` at `parallel_conflict_resolver.py:713,764`). Whole-file read→modify→atomic-replace still loses a concurrent append (read-modify-write window; atomic rename ≠ closed window). field-recon.md:28,30 names `O_APPEND`/`FILE_APPEND_DATA` as the distinct mitigation. "Structural replacement for PCR-on-vault-files" over-claims.
- **Evidence**: field-recon.md:28,30; spike C2; `parallel_conflict_resolver.py:713,764`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md + ADR-085 add `safe_append_text` (`O_APPEND`/`FILE_APPEND_DATA` + sidecar lock); AC2 gains `test_concurrent_appenders_no_lost_update`; the "structural replacement" claim now explicitly covers BOTH whole-file edits AND the append log.

#### M3: AC2 EPERM-held-handle test is Windows-only; no cross-platform reproduction strategy
- **Issue**: `os.replace` over a held handle EPERMs only on Windows; POSIX rename-over-open succeeds → a literal held-handle test passes vacuously on POSIX or needs mocking. Design specified neither mock nor skipif.
- **Evidence**: Critic APED-1 (`WinError 5` on this box); field-recon.md:26; npm/write-file-atomic#28.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §Test-pin (M3): retry-loop exercised by patching `os.replace` to raise `PermissionError` for the first N attempts (deterministic, cross-platform); optional real-held-handle test `skipif(sys.platform != "win32")`. TF-1 row renamed `test_write_retries_on_mocked_eperm`.

#### M4: design "(c) the 5 error-prose sites" is wrong — there are 7, and the pinned exclusion tuples are stale
- **Issue**: `grep 'NOT VAULT_ROOT-routed' tools/*.py` → 7 marked sites; `_ERROR_MESSAGE_STRING_EXCLUSIONS` pins 5 stale `(file,line)` tuples (off-by-one + missing 2 `drift_check_audit` sites). My design restated the stale "5" as a classification-map claim.
- **Evidence**: grep (7); `test_vault_root_constant.py:62-68` (5 stale tuples); `drift_check_audit.py:362,366`.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §(c) now reads "currently 7 across 4 tools" and explicitly flags the pre-existing stale-tuple drift as **out-of-scope for 093** (093 migrates nothing; the orphan test matches by marker substring, so it's latent) → the 094 migration re-syncs the tuples. No hard "5" survives.

### Minors

#### m1: "advisory lock (`msvcrt.locking`)" is inaccurate — it's *mandatory* on Windows, and must not lock the replace target
- **Issue**: `msvcrt.locking`→`LockFileEx` byte-range locks are mandatory (filesystem-enforced); a mandatory lock on `target` would block its own `os.replace`.
- **Evidence**: boostorg/interprocess#142; flylib msvcrt.
- **Builder draft**: **ACCEPTED-FIXED** — design.md + ADR-085 reworded ("`msvcrt.locking`/`LockFileEx` — mandatory on Windows; `fcntl.flock` — advisory POSIX") and specify the lock is a sidecar `<file>.lock`, released after `os.replace`, **never** the replace target.

#### m2: two parsers for the one-line config (inline in `_vault_paths` + `_vault_write.read_vault_root_config`) — divergence risk
- **Builder draft**: **ACCEPTED-FIXED** — design.md: `_vault_write` imports the **shared config relative-path + format constant** from `_vault_paths` (SSoT); AC2 adds `test_inline_and_helper_config_readers_agree` (parity pin on a fixture).

#### m3: MEPD-1 "INCLUDE (tentative)" doesn't specify the discharge branch — build-gated obligation can't be deferred to /reflect
- **Issue**: a changelog entry + VERSION bump WITHOUT a minted RULE-ID + entry-pin is the anti-pattern PMI-1 guards against; must resolve at design.
- **Builder draft**: **ACCEPTED-FIXED** — design.md MEPD-1 posture changed to **EXCLUDE** (no RULE-ID, no changelog entry, no VERSION bump; ADR-085 + R-32 + reflection suffice — mirrors ADR-065's EXCLUDE for infrastructural seam-work; underscore `_vault_write` → no PMI-1 count bump; forward-sync gates no-op at unchanged VERSION). No build-gated changelog/version obligation remains.

### Meta-Critic missed findings (from /critique-review — DR-1 EXTEND)

#### B-add-1: B1-fix residual at ADR-085:57 — the known-bad `tests/tools/` survived the rev-2 sweep
- **Issue**: the B1 fix swept mission-brief + design but left ADR-085's Reversibility recipe naming `tests/tools/test_vault_safe_write.py` — the exact phantom path B1 removes. Caught by DR-1 task (3) "a Critic's own fix is a fresh claim."
- **Builder draft**: **ACCEPTED-FIXED** — `ADR-085:57` → `tests/methodology/`; FBCD-1 grep re-swept across `architecture/decisions/ADR-085*` (sole residual; the critique.md/critique-review.md mentions are legitimate narrative).

#### m-add-1: design "10 consumers" vs the file's stale "8-element" comments
- **Issue**: design/ADR reference "10 `_MIGRATION_SITE_ALLOWLIST` consumers" (frozenset at `test_vault_root_constant.py:45-56` has 10 — design correct); the file's comments at L41/L281 say "8-element" (pre-existing drift; `test_migration_site_allowlist_pinned` computes dynamically → passes at 10).
- **Builder draft**: **DEFERRED** — pre-existing, not introduced by 093; design §Out of scope flags it for 094 re-sync; do not touch comments mid-slice beyond the sanctioned count-pin.

## Dimensions checked
- [x] Unfounded assumptions — C1 keying VALIDATED by execution; PMI-1 underscore-exclusion VALIDATED; "36 tools" no-bump VALIDATED. Finding: M4 ("5"≠7).
- [x] Missing edge cases — M2 (append lost-update), M3 (Windows-only EPERM).
- [x] Over-engineering — B2 (phantom `_vault_write` consumer if config-write is 094) — resolved by routing the base write through `safe_write_text`.
- [x] Under-engineering — M1 (count-pin), M3 (retry exercise).
- [x] Contract gaps — m2 (two parsers for one format).
- [x] Security — none (user-owned local fs; config inside `.git/`; no network/tokens/authz).
- [x] Drift from vault — B1 (`tests/tools/`), B2 (AC3 vs design), M4 ("5" vs 7); ADR-085 extends (not supersedes) ADR-065 — SUP-1 clean; strategic-direction-fit: ADVANCES the PCR/BRANCH/PSQ trajectory (no conflict); m3 (MEPD-1 discharge).
- [x] Web-known issues — EPERM retry needs bounded backoff (OK); `msvcrt.locking` mandatory (m1). Sources: npm/write-file-atomic#227, nodejs/node#29481, golang/go#8914, boostorg/interprocess#142, flylib msvcrt, File-locking (Wikipedia).
- [x] Cross-cutting conformance — B1 (PTFCD-1 phantom-path, 3rd recurrence), M1 (count-pin), M4 (CCC-1 table-vs-inventory); APED-1 applied by execution throughout; leaf-invariant `test_vault_paths_module_is_leaf` holds — VALIDATED.

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | `tests/tools/`→`tests/methodology/` in mission-brief + design (FBCD-1 swept) |
| B2 | Blocker | ACCEPTED-FIXED | AC3→global-base only; base write routed through `safe_write_text` (real consumer); per-project write→094 |
| M1 | Major | ACCEPTED-FIXED | design §Test-pin: count-pin 12→15 designated the ONE sanctioned existing-test change (distinct from the resolution no-behavior-change invariant) |
| M2 | Major | ACCEPTED-FIXED | added `safe_append_text` (O_APPEND/FILE_APPEND_DATA + lock) + `test_concurrent_appenders_no_lost_update`; "structural replacement" claim narrowed to cover whole-file AND append (design + ADR-085) |
| M3 | Major | ACCEPTED-FIXED | design §Test-pin: retry exercised by patching `os.replace`→PermissionError (cross-platform) + optional `skipif(win32)` real-handle |
| M4 | Major | ACCEPTED-FIXED | design §(c) "5"→"7 across 4 tools"; pre-existing stale 5-tuple drift flagged out-of-scope→094 |
| m1 | Minor | ACCEPTED-FIXED | mandatory-lock terminology (LockFileEx); lock on sidecar `.lock`, never the `os.replace` target |
| m2 | Minor | ACCEPTED-FIXED | shared SSoT config constant + `test_inline_and_helper_config_readers_agree` parity pin |
| m3 | Minor | ACCEPTED-FIXED | MEPD-1 posture → EXCLUDE (no RULE-ID / changelog / VERSION bump; mirrors ADR-065; underscore `_vault_write`→no PMI-1 bump) |
| B-add-1 | Blocker | ACCEPTED-FIXED | `ADR-085:57` `tests/tools/`→`tests/methodology/`; FBCD-1 re-swept across the ADR (meta-Critic catch of the B1-fix residual) |
| m-add-1 | Minor | DEFERRED | pre-existing `8-element` comment drift (frozenset is 10; test passes dynamically); re-sync at slice-094, not silently mid-slice |
