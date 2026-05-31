# Spike: external-shared-vault

**Risk**: candidate **R-32** (concurrent-write lost-update / atomic-rename-EPERM corruption on a shared mutable vault) — to be registered when slice-093 is defined; NOT registered now, to avoid touching `risk-register.md` while slice-092 is in flight (charter constraint).
**Date**: 2026-05-31
**Assumption under test**: `architecture/` (the vault) + `diagnose-out/` can be relocated to a single shared external location (default `~/.aisdlc/<project>/`), keyed per-project, so that all slice worktrees + the main tree resolve ONE live vault view — eliminating per-worktree vault copies and their merge conflicts. Supports the broad "every tracked-file-writing skill uses a worktree" initiative.

## Test environment
- Windows 11 Home (10.0.26200), PowerShell 7, git (worktree-enabled).
- Real repo `C:\Users\sshub\ai_sdlc` (main tree, master) + real linked worktree `C:\Users\sshub\ai_sdlc-wt\slice-092-fix-stranded-audit-branchless-blindspot` (slice-092 in flight — UNTOUCHED).
- Shared venv Python 3.13; `tools/_vault_paths.py` (slice-068 / ADR-065); graphify (editable).
- Throwaway external dir `%TEMP%\aisdlc-spike-vault` (copies of `risk-register.md` + `shippability.md`; originals untouched).

## Prior art
- **Local code (code-is-truth correction)**: `tools/_vault_paths.py` (slice-068, **ADR-065**) ALREADY implements the seam — `VAULT_ROOT = Path(os.environ.get("AI_SDLC_VAULT_ROOT", "architecture"))`, read-at-import with a consumer-freeze cascade, a 10-tool `_MIGRATION_SITE_ALLOWLIST`, and a subprocess env-override test. The mechanism the user asked to "build" is ~70% present. Missing: activation (install-time config + per-project derivation), completeness (~6 path-referencing tools + ALL SKILL.md prose bypass it), and the history decision.
- **Field reconnaissance**: see [`spike-external-shared-vault/field-recon.md`](spike-external-shared-vault/field-recon.md). `suggested_action = proceed-with-caveats`. (1) Claude Code (anthropics/claude-code#34437) independently converged on `--git-common-dir`-keyed shared external state for the identical worktree problem — validated prior art. (2) Bare `git rev-parse --git-common-dir` is relative-in-main / absolute-in-linked — literal keying assumption false for the bare form **[Verified-mitigated by this spike]**. (3) Shared mutable store converts loud git merge-conflicts into SILENT Windows lost-update / atomic-rename-EPERM corruption (the `.claude.json`/OneDrive class) **[Untested here → R-32 + mandatory design constraint]**.

## Test
Executed (throwaway; main tree + slice-092 worktree untouched):
1. **Keying**: `git rev-parse --path-format=absolute --git-common-dir` in BOTH the main tree and the real slice-092 worktree.
2. **External resolution**: `AI_SDLC_VAULT_ROOT=%TEMP%\aisdlc-spike-vault` → `from tools._vault_paths import VAULT_ROOT` (subprocess) reading a file at the external root.
3. **External audit**: `python -m tools.risk_register_audit <external>\risk-register.md`.
4. **External graphify**: `python -m graphify vault .` from the external dir.

## Expected outcome
Keying byte-identical across main + worktree; tools resolve + read the external root; an audit + graphify run cleanly against it.

## Actual outcome
1. **Keying — PASS.** Both the main tree and the slice-092 worktree returned byte-identical `C:/Users/sshub/ai_sdlc/.git`. (`--git-dir` differed: `/.git` vs `/.git/worktrees/slice-092-…`; `--show-toplevel` differed per worktree.) The field-recon footgun (bare command relative-in-main) is real but MITIGATED by `--path-format=absolute`, VERIFIED identical on this machine + the real worktree.
2. **External resolution — PASS.** `VAULT_ROOT = C:\Users\sshub\AppData\Local\Temp\aisdlc-spike-vault`; `risk-register.md readable at external root: True`.
3. **External audit — PASS.** `risk_register_audit` parsed the external copy and emitted JSON (top open risk R-13 …).
4. **External graphify — PASS.** `graphify vault .` wrote `graphify-out/vault-graph.json` at the external root (2 files → 2 nodes → 1 community).

## Decision
**CONDITIONAL (GO with constraints).** The architecture is feasible, is validated prior art (claude-code#34437 = same mechanism), the seam already exists (ADR-065), and all empirical tests pass on the real machine + real worktree. NOT a NO-GO. Design MUST respect:

- **C1 — keying**: derive the per-project key from `git rev-parse --path-format=absolute --git-common-dir` (NEVER the bare command; NEVER hand-join `$GIT_DIR` — the vscode#297786 / claude-code#39920 bug class). Canonicalize (realpath; Windows 8.3/case/trailing-slash). Key the `~/.aisdlc/<project>/` subdir as a BOUNDED HASH (direnv: sha1 + readable suffix), not the full mirrored abs-path (MAX_PATH 260 safety). Document move-sensitivity.
- **C2 — concurrent-write safety (MANDATORY — load-bearing)**: relocating `_index.md` / `risk-register.md` / `slice-queue.md` to a shared mutable store converts a LOUD git merge-conflict into a SILENT lost-update / partial-write. Windows `rename()` EPERMs when OneDrive/AV/indexer holds a handle — the class that corrupted `.claude.json`. Design MUST add per-file advisory locking (`portalocker`/`msvcrt.locking`) and/or atomic-write-with-retry-on-EPERM, and `O_APPEND`/`FILE_APPEND_DATA` for ADR-style append-logs. → R-32.
- **C3 — placement**: default `~/.aisdlc/` is good (typically outside OneDrive). Warn/guard if the resolved vault lands under OneDrive or an aggressive AV path.
- **C4 — completeness + the real scoping driver**: the seam is `tools/*`-Python-only AND incompletely adopted (~6 path-referencing tools + EVERY SKILL.md prose path still bypass `VAULT_ROOT` — the env var does NOT reach SKILL.md prose Claude reads literally). slice-093 must (a) extend resolution to env-var → repo-local pointer / `--git-common-dir`-derived default → `architecture/` fallback, (b) migrate remaining tools (extend `_MIGRATION_SITE_ALLOWLIST`), and (c) DECIDE the SKILL.md-prose strategy. (c) is what splits a ~1-day Python-seam+install-config cut (slice-093) from the larger SKILL-prose-rewrite + physical-move (slice-094).
- **C5 — history/auditability (design fork)**: vault-out-of-git loses the git audit trail (append-only ADRs, reflections). Recommended: the external vault is its OWN git repo (`~/.aisdlc/<project>/.git`) — preserves history; note it does NOT itself solve C2. Alternatives: sync-back-at-`/commit-slice`; accept-no-history (weakest).

## Impact
- **Affects**: `tools/_vault_paths.py` + the `VAULT_ROOT` consumer set + `_MIGRATION_SITE_ALLOWLIST`; ~6 unmigrated tools (`parallel_conflict_resolver.py`, `shippability_path_audit.py`, `shippability_runner.py`, `pulse_worktree_resolver.py`, `stranded_slice_audit.py`, `new_agent_warning_audit.py`, …); every `skills/*/SKILL.md` that writes `architecture/...`; `INSTALL.md` (new install-time location prompt + per-project config); `CLAUDE.md`; graphify invocations; the PSQ `slice-queue.md` contract; ADR-065 (extend/supersede); `diagnose-out/` + `graphify-out/` relocation (already gitignored — trivial, but NOT currently under `VAULT_ROOT`).
- **Changes needed before build**: register R-32 + C1–C5 (append-only; deferred now per charter); resolve the C5 history fork at `/design-slice`; decide the SKILL.md-prose strategy (the scope split driver).
- **/critique gate**: per the field-recon authoritative-contradiction rule, `field-recon.md` is **REQUIRED READING** for slice-093's `/critique` (the concurrent-write hazard is sourced from official-repo issues).

## Deviations from `/risk-spike` skill
- **Step 6 (update risk register) intentionally SKIPPED** — charter forbids touching `risk-register.md` while slice-092 is in flight. R-32 + constraints are recorded here and will be registered (append-only, merge-safe) when slice-093 is defined.
- Spike code was inline/throwaway (no `architecture/spikes/code/` artifact retained); the temp external dir is left in `%TEMP%` for the OS to reap (the harness sandbox blocks `Remove-Item -Recurse -Force`).
