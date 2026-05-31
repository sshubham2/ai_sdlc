# Design: Slice 093 add-external-vault-support

**Date**: 2026-05-31
**Mode**: Standard
**Grounded in**: `architecture/spikes/spike-external-shared-vault.md` (CONDITIONAL/GO, constraints C1–C5) + [[ADR-065]] (the existing `VAULT_ROOT` seam).
**Revision**: rev-2 — incorporates Critic B1/B2/M1–M4/m1–m3 (all ACCEPTED-FIXED) — see critique.md.

## Intent recap (capability cut — NO flip)

Ship the machinery to make the vault relocatable to a shared external location (`~/.aisdlc/<project>/`), with the **default unchanged at `architecture/`** so this repo + every existing tool/test/skill behave identically. The live flip (SKILL-prose rewrite, physical move, default-flip, history decision, PCR retirement) is slice-094.

## What's new

- **`tools/_vault_write.py`** (new leaf helper) — the C2 write-safety primitive (R-32):
  - `safe_write_text(path, text)` — whole-file: acquire a sidecar `<path>.lock` lock → write temp → atomic `os.replace` → bounded retry-on-`PermissionError`/EPERM. **The lock is taken on the sidecar `.lock`, never on the replace target** (a Windows `msvcrt.locking`/`LockFileEx` byte-range lock is *mandatory* — locking the target would block its own `os.replace`; m1).
  - `safe_append_text(path, text)` — append-only (ADRs, `risk-register.md`, `_index.md`, the PCR audit log): `O_APPEND` (POSIX) / `FILE_APPEND_DATA` (Windows) under the sidecar lock — non-clobbering, closes the read-modify-write lost-update window that whole-file replace does NOT (M2; field-recon.md:28,30).
  - `write_vault_root_config(common_dir, vault_path)` / `read_vault_root_config(common_dir)` — the per-project config API (defined + **test-exercised** in 093; first **production**-called at the 094 flip).
- **Resolution-precedence extension** in `tools/_vault_paths.py` (modified, NOT a new module): `AI_SDLC_VAULT_ROOT` env → **git-common-dir config** (`$(git rev-parse --path-format=absolute --git-common-dir)/aisdlc/vault-root`) → default `Path("architecture")`. All resolution stays **stdlib-only** (subprocess/pathlib/os) so the `test_vault_paths_module_is_leaf` invariant holds (config-read inline; no `tools.*` import).
- **`INSTALL.md`** (modified): a new step prompting for the base vault location (default `~/.aisdlc`) via `AskUserQuestion`, writing **only** the global base config `~/.claude/ai-sdlc-vault-base` **via `_vault_write.safe_write_text`** (B2: 093 writes the GLOBAL BASE only; the per-project `vault-root` write is slice-094).
- **R-32** registered + **[[ADR-085]]** (extends ADR-065).
- **Tool-migration classification map** (below) — documented, not executed.

## What's reused

- [[ADR-065]] / `tools/_vault_paths.py` — the existing `VAULT_ROOT` constant + `AI_SDLC_VAULT_ROOT` env override + read-at-import/consumer-freeze cascade (preserved; the new config source is read at the same import point).
- `tests/methodology/test_vault_root_constant.py` — extended; `_MIGRATION_SITE_ALLOWLIST` UNCHANGED (no new migrations this slice).
- Spike-proven facts: `--path-format=absolute --git-common-dir` byte-identical across main + worktrees (C1); external-root reads + `graphify vault` + audits work.

## Components touched

### `tools/_vault_paths.py` (modified)
- **Responsibility**: resolve `VAULT_ROOT` via the 3-tier precedence (env → git-common-dir config → `architecture/` default).
- **Key interactions**: imported by the 10 `_MIGRATION_SITE_ALLOWLIST` consumers; runs `git rev-parse` (stdlib `subprocess`) ONLY when the env var is unset. **Leaf-purity preserved** — stdlib-only, config-read inline.
- **Defensive fallback (R-7)**: no-git/not-a-repo/config-absent → silent `architecture/` default (intended default). Config **present but unreadable/malformed** → fail-visible stderr WARN + default; never silently mis-resolve.

### `tools/_vault_write.py` (new, leaf helper)
- **Responsibility**: the C2 safe-write + safe-append primitives + the per-project config API (above).
- **Lives at**: `tools/_vault_write.py`. Leading-underscore → auto-excluded from PMI-1 inventory (verified: `plugin_manifest_audit.py:147` filters `_`-prefixed) — no `plugin.yaml`/`install_audit` count bump.
- **Key interactions**: may import `tools._vault_paths` for the **shared config relative-path + format constant** (m2: single source of truth for the one-line `vault-root` format, so the inline reader in `_vault_paths` and `read_vault_root_config` here cannot diverge — a parity test pins they agree on a fixture). Invoked by INSTALL.md (`python -c`) for the base-config write; fully exercised by `tests/methodology/test_vault_safe_write.py`.

### `INSTALL.md` (modified)
- **Responsibility**: add the base-vault-location prompt + the global base write. NOT installed to `~/.claude/` (source-only per INSTALL.md:162) → no OSDG-1/drift concern.

## Contracts added or changed

No HTTP/event contracts. Two filesystem config shapes (one shared format, m2):
- **Per-project config**: `$GIT_COMMON_DIR/aisdlc/vault-root` — single line, absolute vault path. Shared across all worktrees (common-dir is shared); never git-tracked (inside `.git/`). Written by `write_vault_root_config` (**production at 094**); read inline by `_vault_paths`.
- **Global base config**: `~/.claude/ai-sdlc-vault-base` — single line, base dir (default `~/.aisdlc`). Written by INSTALL.md (093, via `safe_write_text`); consumed by 094's per-project flip.
- **Auth model**: none — local filesystem, user-owned paths; the `.git/` config inherits repo ownership. Junction/symlink approaches (needing Windows Developer-Mode) rejected — ADR-085.

## Data model deltas
None (no DB/schema). The only persisted state is the two single-line config files.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_vault_write.py` | `INSTALL.md` recipe (`python -c "from tools._vault_write import safe_write_text"` — the global-base-config write) | `tests/methodology/test_vault_safe_write.py::test_concurrent_writers_no_lost_update` | — |

(`_vault_write` has a real 093 consumer — INSTALL.md's base-config write via `safe_write_text` — plus full test coverage; no exemption needed. `write_vault_root_config` (per-project) is test-exercised in 093, production-called at 094. `tools/_vault_paths.py` is modified, not new — no row.)

## Tool-migration classification map (AC4 — documented, NOT executed in 093)

The remaining `architecture/`-path-referencing `tools/*.py` split three ways; **093 migrates none** (default stays `architecture/`, so all stay correct). The map de-risks slice-094:

- **(a) Simple-FS-path — migrate at flip (094)**: `tools/project_frame_synth.py` (reads concept/triage/risk-register/slice-queue under one `repo_root`). Clean `VAULT_ROOT` swap.
- **(b) Worktree/git-model-coupled — RETHINK at flip (094), do NOT naive-migrate**:
  - `tools/parallel_conflict_resolver.py` — operates on `architecture/slice-queue.md`/`shippability.md` via **git pathspecs** (`git show :2:…`, `git add …`) AND appends to its own log via `.open("a")` (`:713,:764`). Presupposes the vault is git-tracked-in-repo. Under untracked+external these go inert → **PCR-for-vault retires** (per the accepted direction; [[ADR-085]]); `_vault_write` (`safe_write_text` + **`safe_append_text`** for the log) replaces it.
  - `tools/stranded_slice_audit.py` — `architecture/slice-queue.md` + per-worktree milestone pathspecs; **also overlaps in-flight slice-092** → excluded regardless.
  - `tools/pulse_worktree_resolver.py` — composes `architecture/` under **each scanned worktree root** (inherently multi-tree). A single `VAULT_ROOT` would break per-worktree scanning; under the shared external vault there is no per-worktree `architecture/` → rethink at flip.
- **(c) Never migrate**: `tools/shippability_decoupling_audit.py:91-92` (AST-pattern tuples — pinned literal); the **error-message-prose sites carrying the `# NOT VAULT_ROOT-routed` marker — currently 7 across 4 tools** (`cross_spec_parity_audit`, `drift_check_audit`×2, `state_transition_pin_audit`×3, `validate_slice_layers`). **M4 note (out of scope for 093, flagged for 094)**: the existing `_ERROR_MESSAGE_STRING_EXCLUSIONS` tuple-set in `test_vault_root_constant.py:62-68` pins only **5** stale `(file,line)` pairs that no longer match the real marker lines (off-by-one + missing the 2 `drift_check_audit` sites). 093 migrates nothing so this is latent (the orphan test matches by marker *substring*, not the tuples); the 094 migration must re-sync the tuples.

## Decisions made (ADRs)
- [[ADR-085]] — External-shared-vault resolution via git-common-dir config + the C2 concurrent-write/append-safety contract + the accepted direction (PCR-for-vault retires at the 094 flip); extends ADR-065 — reversibility: **cheap**.

## Authorization model for this slice
None new. All paths are user-owned local filesystem; the per-project config lives inside the repo's own `.git/`. No network, no multi-user, no new tokens.

## Error model for this slice
- **Resolution**: env set → use it. Env unset + no-git/not-a-repo/config-absent → `architecture/` default (intended, silent). Config **present but unreadable/malformed** → stderr WARN + default fallback (fail-visible; R-7).
- **Safe-write / safe-append**: lock-acquire timeout → raise (bounded). `os.replace` EPERM (held handle, a **Windows-only** transient — POSIX rename-over-open succeeds) → bounded exponential-backoff retry (cap stated in code), then a typed error naming the path + held-handle/OneDrive-AV guidance. Never leave a truncated target (atomic replace; append is non-clobbering).
- **No-flip invariant**: any code path that would change `VAULT_ROOT`'s **resolved default** away from `architecture/` for THIS repo is a build-time STOP (covered by `test_default_unchanged_when_no_env_no_pointer`). This is distinct from the *count-pin update* below — editing a test file's pinned function-count is a sanctioned slice change, NOT a resolution-behavior change.

## Test-pin + count updates (M1)
- AC1 adds **3** functions to `tests/methodology/test_vault_root_constant.py` → its `test_full_pytest_baseline_preserved` pin (currently `test_count == 12`; L177-193) must update to **`== 15`** + docstring (12 = slice-068 10 + slice-071 2; +3 = slice-093 AC1 resolution-precedence tests). **This count-pin update is the ONE sanctioned existing-test change** in this slice; the mid-slice smoke gate's "any existing test behavior change → STOP" applies to the *resolution path*, not this pin.
- **AC2 test strategy (M3)**: the EPERM retry-loop is exercised by **patching `os.replace` to raise `PermissionError` for the first N attempts** (deterministic, cross-platform) — NOT by relying on a real held handle (that EPERMs only on Windows). An optional real-held-handle integration test is marked `@pytest.mark.skipif(sys.platform != "win32")`. Two-layer per slice-090's platform-bug lesson.

## Out of scope (→ slice-094)
Flip the default; rewrite SKILL.md prose; physically move `architecture/`+`diagnose-out/`; retire/rethink the (b) git-coupled tools; re-sync the stale `_ERROR_MESSAGE_STRING_EXCLUSIONS` tuples; the C5 history/own-repo decision; per-project `/triage`+`/adopt` vault-creation wiring; the production call of `write_vault_root_config`; re-syncing the stale `8-element` comments in `test_vault_root_constant.py:41,281` (pre-existing drift — the frozenset has **10** entries; the design's "10 consumers" count is correct; m-add-1) — re-sync at 094 or opportunistically with the AC1 count-pin change, NOT silently mid-slice.

## MEPD-1 Inclusion-heuristic posture
**EXCLUDE** (m3 — resolved at design, not deferred). 093 mints **no new RULE-ID**, makes **no behavior change** for this repo (default unchanged), and ships infrastructural seam-work + an ADR + a risk — the same shape as ADR-065's EXCLUDE (slice-068). Therefore: **no `methodology-changelog.md` entry, no VERSION/`ai-sdlc-VERSION`/`plugin.yaml.version` bump, no entry-pin test** — which is exactly what avoids the "changelog entry without a minted RULE-ID / entry-pin" anti-pattern the Critic flagged (m3). The new `_vault_write.py` is an underscore module → auto-excluded from PMI-1 inventory → no `install_audit`/`plugin.yaml` count bump. Forward-sync gates (MCFS-1/AVFS-1/TVFS-1) are no-ops at an unchanged VERSION. (MEPD-1 EXCLUDE for an ADR+risk infrastructural slice with no RULE-ID is the established pattern, N≥6 per `_index.md` lessons.)
