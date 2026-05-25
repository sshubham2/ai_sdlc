---
id: ADR-058
title: Mint TVFS-1 (ai-sdlc-Tools Version Forward-Sync) — the installed ai-sdlc-tools pip-package version MUST equal trimmed VERSION; gate is a standalone tool that reads distribution metadata scoped to the venv site-packages (the read is out-of-repo runtime metadata — the ADR-056 boundary, satisfied side).
date: 2026-05-22
slice: slice-059-add-tools-package-version-gate
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-058: Mint TVFS-1 (ai-sdlc-Tools Version Forward-Sync)

> **Revision note (post-/critique, 2026-05-22)**: the Critic's BLOCKED verdict (B1) proved the original read mechanism (`importlib.metadata.version("ai-sdlc-tools")`) is CWD-shadowed by the in-repo `ai_sdlc_tools.egg-info/` build artifact. The Decision below specifies the corrected venv-scoped mechanism. See `slice-059/critique.md`.

## Context

The installed `ai-sdlc-tools` pip distribution had drifted to `0.20.0` while in-repo `VERSION` was `0.62.0` — 42 methodology versions apart. The venv package carried only 15 of the 26 canonical tool modules; `tools.critique_review_prerequisite_audit` (CRP-1), `tools.pipeline_chain_audit` (PCA-1), `tools.branch_workflow_audit` (BRANCH-1) and 8 others were absent. Surfaced this session when a `/build-slice` run in a *different* adopted project could not resolve those audits.

The drift is invisible from this source repo: `$PY -m tools.X` resolves the importable **package** `tools` from CWD, so every audit runs and `install_audit.py`'s `_check_tool_modules` import check passes tautologically. It only breaks in *other* projects, where there is no local `tools/` and resolution falls through to the stale venv site-packages copy.

The forward-sync gate family already covers four version-bearing legs keyed off the in-repo `VERSION` source of truth: **PMI-1** — `plugin.yaml.version`; **PVFS-1** ([[ADR-056]], slice-054) — `pyproject.toml [project].version`; **AVFS-1** ([[ADR-052]], slice-050) — installed `~/.claude/ai-sdlc-VERSION`; **MCFS-1** (slice-041) — installed `~/.claude/methodology-changelog.md`.

PVFS-1 gates the **source** version label, so every *new* `pip install <repo>` builds a correctly-versioned wheel. But no gate covers the **installed artifact**: PVFS-1 makes the next install correct; it never forces the *re-install*. The installed `ai-sdlc-tools` pip-package version is the last ungated version-bearing leg — and it is the one that drifted.

**Read-mechanism hazard (B1).** The naive `importlib.metadata.version("ai-sdlc-tools")` does NOT read the venv-installed artifact when run from the source repo. `setuptools` writes an `ai_sdlc_tools.egg-info/` directory into the source tree on `pip install`; `importlib.metadata` discovers metadata from every `sys.path` entry including the CWD; the in-repo egg-info shadows the venv `.dist-info`. Because PVFS-1 keeps `pyproject.toml == VERSION` and the egg-info `Version` regenerates from `pyproject.toml`, the naive read is tautologically green even when the venv is stale. Verified live: `importlib.metadata.distributions()` finds two `ai-sdlc-tools` distributions; the gate must therefore scope its read explicitly (see Decision).

## Options considered

1. **Route A — pytest assertion only (PVFS-1 / ADR-056 Route B analogue)**:
   - **Pros**: Cheapest. No new `tools/` module; matches PVFS-1's lightweight shape.
   - **Cons**: The forward-sync family's defining semantics for **out-of-repo legs** is WARN-exit-0-on-absent (AVFS-1, MCFS-1) — a tri-state a binary pytest `assert` cannot express; a not-installed environment would FAIL the assert (false slice-regression signal). It would also break wiring parity: AVFS-1/MCFS-1 are non-opt-out **tool** gates at `/build-slice` Step 6 + `/reflect` Step 5b-X.
   - **Rejected because**: the out-of-repo, environment-mutable read genuinely needs the tri-state (synced / WARN-absent / drift-HALT / usage) — the structural need ADR-056 names as the boundary criterion.

2. **Route B — born-retired conformance class (no RULE-ID / no methodology-changelog entry / no VERSION bump)**:
   - **Pros**: Cheapest of all. Slice-045 R-11 precedent.
   - **Cons**: The installed-pip-artifact forward-sync is a structurally new invariant — no prior rule pinned it. Same reasoning ADR-056 Option 1 rejected for PVFS-1: a new structural invariant deserves methodology-discoverability.
   - **Rejected because**: ADR-056 already settled this exact trade-off for the sibling leg; consistency demands TVFS-1 be a discoverable named rule.

3. **Route C — new RULE-ID TVFS-1 + standalone tool `tools/ai_sdlc_tools_version_forward_sync.py`** *(chosen)*:
   - **Pros**: The installed pip distribution is read OUT of repo, at runtime, from environment-mutable state — exactly the structural need ADR-056 Option 3 names as the tool-bearing members' justification ("AVFS-1 reads OUT-of-repo installed file; MCFS-1 reads OUT-of-repo installed file"). The tool delivers the required tri-state, the attributed drift message, and clean wiring parity with AVFS-1/MCFS-1.
   - **Cons**: One more `tools/` module + regression suite. Marginal — TVFS-1 is a structural clone of AVFS-1.
   - **Chosen because**: TVFS-1 is the genuine AVFS-1 analogue on the installed-pip-artifact leg. ADR-056 *rejected* Route C for PVFS-1 only because pyproject.toml is in-repo and has no "absent" state; TVFS-1 sits on the **satisfied** side of the very same boundary.

## Decision

Mint **TVFS-1 (ai-sdlc-Tools Version Forward-Sync)** as a new methodology-class rule-ID via Route C. TVFS-1 asserts: the version of the `ai-sdlc-tools` pip distribution installed in the pipeline's venv MUST equal the trimmed contents of in-repo `VERSION`.

The gate is a new standalone tool, `tools/ai_sdlc_tools_version_forward_sync.py`, a structural clone of `tools/ai_sdlc_version_forward_sync.py` (AVFS-1): same CLI (`--check` / `--json` / `--root`), same `CheckResult` dataclass, same tri-state exit contract (0 synced · 0 WARN-not-installed · 1 drift-HALT · 2 usage), same `tools._stdout` UTF-8 convention.

**Read mechanism (B1-corrected).** The installed version is resolved by `_resolve_installed_version()`, which enumerates `importlib.metadata.distributions(path=[sysconfig.get_path("purelib")])` and filters for `ai-sdlc-tools` — scoping the read to the running interpreter's site-packages so the in-repo `ai_sdlc_tools.egg-info/` build artifact is excluded **by construction**. Empty → `None` (not installed) → WARN; one → its version; the enumerate-and-filter approach never raises `PackageNotFoundError`. The naive `importlib.metadata.version()` is explicitly NOT used.

**Test seam (B2).** `check(root, *, installed_version_resolver=_resolve_installed_version)` — the resolver is an injectable callable so the regression suite drives a genuine non-tautological drift case (a fabricated mismatched version) without mutating `VERSION` or the global metadata store. A separate real-resolver test places a divergent egg-info on the metadata path and proves `_resolve_installed_version()` still reads the venv version (the test that pins the B1 fix).

**Divergences from the AVFS-1 clone**: (1) no CRLF→LF / `_normalized_bytes` machinery — TVFS-1's installed side is an `importlib.metadata` string, not a file; equality is plain trimmed-string `==`. (2) `--root` is RETAINED (TVFS-1 still reads in-repo `VERSION`; analysed, not clone-inertia).

Wired at two ungated points (AVFS-1 2-point shape): `/build-slice` Step 6 pre-finish (non-opt-out checklist gate) and `/reflect` a new dedicated `Step 5b-tvfs` (explicitly NOT folded into the rule-promotion-gated Step 5b — the R-7/slice-022 silent-disable class).

Atomic 4-part PMI-1 bump `0.62.0 → 0.63.0` applies (VERSION + plugin.yaml.version + pyproject.toml.version + methodology-changelog `## v0.63.0` header + installed `~/.claude/ai-sdlc-VERSION`).

Mints a new rule. Supersedes nothing. Extends the PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 forward-sync family onto the installed-pip-artifact leg — the last ungated version-bearing surface.

## Consequences

- **Downstream gates** (additive, no existing gate disturbed):
  - `/build-slice` Step 6 pre-finish runs `$PY -m tools.ai_sdlc_tools_version_forward_sync` as a new non-opt-out checklist item.
  - `/reflect` Step 5b-tvfs runs the same on any slice that performed a PMI-1 version bump.
- **WARN is weaker than AVFS-1's (B1/M3).** AVFS-1's installed-absent case is unambiguous (no file). TVFS-1's `None` case means "no `ai-sdlc-tools` in *this interpreter's* venv site-packages" — which can co-exist with a stale install reachable by another interpreter. The WARN message therefore names `sys.executable` + `purelib` and directs the user to verify `$PY`. Since the pipeline always runs audits under `$PY`, this is a guard against `$PY` misconfiguration, not a routine state.
- **Self-gating from slice-060 onward**: any future slice that bumps `VERSION` must also `$PY -m pip install --upgrade <source>` before its Step 6, or TVFS-1 HALTs. This institutionalizes the re-install step INSTALL.md Step 3g previously left to memory. **No `/build-slice` SKILL.md step is added** — the TVFS-1 HALT + remediation message is itself the enforcement. This is a real new obligation, heavier than AVFS-1's `cp`-based leg, and it mutates the **shared** `~/.claude/.venv` from a slice branch (bounded: the branch becomes the default branch on `/commit-slice --merge`).
- **slice-059 bootstrap**: discharged at slice-059's own Step 6 — the build sequence runs `$PY -m pip install --upgrade .` after the 4-part bump and before the audit sweep; a non-zero TVFS-1 before that re-install is the EXPECTED signal (ADR-052 bootstrap-honesty precedent).
- **`tools/install_audit.py`** `_CANONICAL_TOOLS` gains `tools.ai_sdlc_tools_version_forward_sync` (INST-1 / PMI-1 parity); the two stale hard-coded tool-count literals in that file are scrubbed in the same edit (slice-058 BC-PROJ-11 "remove the literal" lesson — the slice adds the count those literals are stale against). `plugin.yaml` gains the `- path:` entry. PMI-1's paired test keeps the two lists in lock-step.
- **Methodology-changelog v0.63.0** entry added (verified next-free; head was `v0.62.0`); META-1 + MCFS-1 cover its parity/shape. **shippability row #59** (next-free: catalog max = #58) carries the in-repo entry-pin tests (the tool itself is non-catalog — it reads environment-mutable installed state, AVFS-1 row-#50 precedent).
- **No new code-level runtime/API contract** (the tool's CLI exit-code contract is internal methodology tooling). **No vault component added**. **CLAUDE.md NOT edited** — TVFS-1 is enforced at audit time, not a per-edit discipline (same call ADR-056 made for PVFS-1).

## Reversibility

**Cheap.** Reverting means: (1) delete `tools/ai_sdlc_tools_version_forward_sync.py` + its regression test; (2) remove the two wiring blocks from `skills/build-slice/SKILL.md` + `skills/reflect/SKILL.md` (and forward-sync the installed copies); (3) drop the `_CANONICAL_TOOLS` / `plugin.yaml` entries; (4) drop the shippability row + entry-pin tests; (5) add a SUP-1 supersession ADR. No downstream consumer is built on TVFS-1's existence — PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 are untouched and independent. Est. ~45 minutes.

The atomic 4-part bump itself is cheap-reversible, subject to the methodology-changelog's append-only discipline (a retraction needs a SUP-1 changelog entry).
