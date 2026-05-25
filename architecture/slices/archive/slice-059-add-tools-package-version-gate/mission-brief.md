# Slice 059: add-tools-package-version-gate

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: No pre-existing register ID — this slice retires a newly-discovered methodology gap: the installed `ai-sdlc-tools` pip package is the only PMI-1 version-bump leg with no deterministic forward-sync gate. A new risk-register entry may be minted at `/design-slice`.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The installed `ai-sdlc-tools` pip package is the one PMI-1 version-bump leg with no deterministic forward-sync gate — it silently drifted to `0.20.0` while the source advanced to `0.62.0` (15/26 canonical tool modules; CRP-1, PCA-1, BRANCH-1 absent). The gap is invisible from the source repo — where `$PY -m tools.X` resolves to live source — yet breaks every other adopted project, where it resolves to the stale venv copy. This slice adds a deterministic gate (proposed rule **TVFS-1**, in the AVFS-1 / MCFS-1 forward-sync-via-downstream-gate lineage) that asserts the installed `ai-sdlc-tools` distribution version equals `VERSION`, so the drift fails a pipeline gate the moment it happens instead of surfacing slices later in an unrelated session.

## Acceptance criteria

1. A new audit module `tools/<name>.py` reads the installed `ai-sdlc-tools` distribution version (via `importlib.metadata`) and the repo `VERSION`, and exits non-zero when they differ — with an actionable message naming the remediation (`pip install --upgrade <source>`, INSTALL.md Step 3g).
2. The audit exits 0 (clean) against the current synced environment (installed package and `VERSION` both at the same value).
3. A regression test pins both directions: a version-mismatch fixture → violation / exit 1; matched versions → clean / exit 0. The drift case genuinely exercises the mismatch branch (not a tautology).
4. The audit is wired into a pipeline gate so it fires automatically on the AVFS-1 lineage path (`/reflect` and/or `/build-slice` Step 6); any edited `SKILL.md` is forward-synced in-repo ↔ installed.
5. The new tool is registered in every canonical inventory — `plugin.yaml`, `tools/install_audit.py` `_CANONICAL_TOOLS`, and `architecture/shippability.md` — and a `methodology-changelog.md` entry + a new ADR record the rule (proposed **TVFS-1**) and its gate wiring. PMI-1 / INST-1 / SCPD-1 stay green.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Audit module exists + detects mismatch | `$PY -m tools.<name>` against a fixture where installed-dist-version ≠ `VERSION` → exit 1, message names the `pip install --upgrade` fix |
| 2 | Clean against synced env | `$PY -m tools.<name>` in the current repo → exit 0, no violations |
| 3 | Regression test pins both directions | `$PY -m pytest tests/methodology/test_tvfs_1_*.py -v` → drift case asserts exit 1, synced case asserts exit 0; both branches executed |
| 4 | Wired into a pipeline gate | Grep the target `SKILL.md` for the audit invocation; run the host skill's pre-finish/Step-5b path and confirm the audit runs; `$PY -m tests/skill_drift_equality` (or the relevant drift test) confirms in-repo ↔ installed parity |
| 5 | Registered + documented | `$PY -m tools.plugin_manifest_audit` exit 0; `$PY -m tools.install_audit --claude-dir ~/.claude` exit 0; `shippability.md` has the new row; `methodology-changelog.md` + new ADR present |

## Must-not-defer

- [ ] Graceful handling when `ai-sdlc-tools` is not installed at all (`importlib.metadata.PackageNotFoundError`) — clear message, no traceback, defined exit code.
- [ ] The mismatch message must be actionable — name the exact remediation command and INSTALL.md Step 3g.
- [ ] Confirm the audit reads the *installed* distribution version (`importlib.metadata` reads `.dist-info`, CWD-independent) and is NOT shadowed by the source repo's `tools/` folder the way `install_audit.py`'s `_check_tool_modules` import check is.
- [ ] Shippability catalog propagation (RPCD-1 / SCPD-1) — the new audit rule propagates its consumer references into `architecture/shippability.md`.
- [ ] Logging / output: the audit emits its result to stdout via the `tools._stdout` UTF-8 convention (UTF8-STDOUT-1).

## Out of scope

- Fixing `install_audit.py`'s import-shadowing blind spot (`_check_tool_modules` resolves `tools.X` from CWD when run in the source repo, so INST-1 is tautologically green there). The version gate makes package-staleness detectable on its own axis; the import tautology is a separate concern — a follow-up slice if still wanted.
- Any change to INSTALL.md's install mechanism (Step 3g stays `pip install --upgrade`).
- Continuous / automatic sync between the source repo and `~/.claude/` — this slice adds *detection*, not automation.
- Gating the venv tools-package *module set* (file-level completeness) — version equality is the proxy; per-module completeness remains `install_audit.py`'s job.

## Dependencies

- Prior slices: [[slice-041-reframe-installed-pin-forward-sync-invariant]] — MCFS-1 forward-sync-via-downstream-gate lineage; the AVFS-1 slice (slice-050) — `tools/ai_sdlc_version_forward_sync.py` is the structural template to clone.
- Vault refs: [[decisions/ADR-052]] (AVFS-1), [[decisions/ADR-029]] (deterministic-downstream-gate rationale for non-deterministic LLM-executed steps), `tools/methodology_changelog_forward_sync.py` (MCFS-1).
- Risk register: no pre-existing ID — a new entry may be minted at `/design-slice`.

## Mid-slice smoke gate

At ~50% of build (audit module exists, not yet wired/registered), run:
```
$PY -m tools.<name>                          # against current synced env
$PY -m tools.<name>   (with a mismatch fixture)   # version forced ≠ VERSION
```
Expected: clean run → exit 0; mismatch fixture → exit 1 with an actionable remediation message. If either is wrong: STOP, diagnose, don't continue to wiring/registration.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] PMI-1 (`plugin_manifest_audit`), INST-1 (`install_audit`), DR-1, the Step 6 audit suite all green
