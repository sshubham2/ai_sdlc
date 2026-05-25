# Critique: Slice 059 add-tools-package-version-gate

**Critic reviewed**: mission-brief.md, design.md, new ADR (ADR-058)
**Date**: 2026-05-22
**Result**: BLOCKED (first-Critic verdict) → **CLEAN** (final verdict, post-TRI-1 user triage 2026-05-23)

## Summary

The Critic ran an empirical attack (APED-1): it rewrote the in-repo `ai_sdlc_tools.egg-info/PKG-INFO` version and proved that `importlib.metadata.version("ai-sdlc-tools")` resolves the **in-repo egg-info**, not the venv `.dist-info` — so the original design's load-bearing "CWD-shadowing correctness note" was empirically false and TVFS-1 would have been tautologically green from the source repo. This is the N+1 doctrine in action (the novel `importlib.metadata` edge of a just-minted rule was the Builder's blind spot; the first Critic caught it). 3 blockers, 3 majors, 2 minors. The Builder re-verified the corrected `sysconfig.purelib`-scoped read mechanism live, and has rewritten `design.md` + `ADR-058` accordingly — all 8 findings ACCEPTED-FIXED.

## Findings

### Blockers (must address before /build-slice)

#### B1: `importlib.metadata` is CWD-shadowed by the in-repo `ai_sdlc_tools.egg-info/` — the audit would be tautologically green from the source repo

- **Claim under review**: design.md (original) "CWD-shadowing correctness note" — *"`importlib.metadata.version(...)` … Run from the source repo, where no `.dist-info` exists in-tree, it returns the venv-installed version."* Mission-brief must-not-defer #3.
- **Issue**: `setuptools` writes `ai_sdlc_tools.egg-info/` (with a `Version:`-bearing `PKG-INFO`) into the **source tree** on `pip install`. `importlib.metadata` discovers metadata from every `sys.path` entry, including the CWD. The Critic verified: `distributions()` finds **two** `ai-sdlc-tools` (in-repo egg-info + venv dist-info); a `9.9.9` rewrite of the egg-info made `version()` return `9.9.9`. Because PVFS-1 keeps `pyproject.toml == VERSION` and the egg-info regenerates from `pyproject.toml`, the naive read compares `VERSION` against a source-derived copy of itself — always green even when the venv is stale. Structurally identical to the `install_audit.py` import tautology the slice claims TVFS-1 is immune to.
- **Evidence**: `.gitignore:15`; `ai_sdlc_tools.egg-info/PKG-INFO`; venv `ai_sdlc_tools-0.62.0.dist-info`; the Critic's `9.9.9` rewrite experiment.
- **Proposed fix**: Re-spike the read mechanism — resolve the distribution explicitly from the venv `site-packages`, excluding the in-repo egg-info by construction; add a regression case that places a divergent egg-info on the metadata path and proves the venv version still wins.
- **Builder draft**: **ACCEPTED-FIXED.** Builder re-verified live: `importlib.metadata.distributions(path=[sysconfig.get_path("purelib")])` returns only the venv `.dist-info` (egg-info excluded by construction). `design.md` "Installed-version read mechanism (B1 — corrected)" + `ADR-058` Context/Decision rewritten: the audit uses `_resolve_installed_version()` scoping `distributions(path=[sysconfig.get_path("purelib")])`, never the naive `version()`. A real-resolver egg-info-isolation regression test is added (the test that would have caught this).

#### B2: The regression test's "genuine non-tautological drift case" had no injection seam

- **Claim under review**: mission-brief AC #3 / design.md "a genuine non-tautological drift case".
- **Issue**: A drift fixture cannot be produced by editing `VERSION` alone — per B1 both sides derive from `VERSION`. AVFS-1's template has an injectable `installed` path; TVFS-1's design left the installed-version read as a global with no seam, so AC #3 had no delivering design element.
- **Evidence**: AVFS-1 `check(root, installed=None)` at `tools/ai_sdlc_version_forward_sync.py:132`.
- **Proposed fix**: `check()` takes the installed-version read as an injectable seam.
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "check() injection seam (B2)" added: `check(root, *, installed_version_resolver=_resolve_installed_version)`. Seam-injected tests drive all four states (`lambda: "9.9.9"` drift / `lambda: <VERSION>` synced / `lambda: None` warn / no-`VERSION` `root` usage); the real-resolver egg-info test covers the un-injected path.

#### B3: The slice-059 bootstrap requires a `pip install --upgrade` the build sequence did not own, and runs on a slice branch

- **Claim under review**: design.md (original) "Self-application / bootstrap".
- **Issue**: (1) `/build-slice` has no step that re-installs the venv package; the design asserted "the build sequence MUST run `pip install --upgrade .`" without naming a phase. (2) Per BRANCH-1, `/build-slice` runs on a `slice/059` branch; `pip install --upgrade .` from the branch mutates the **shared** venv used by all projects — a side effect the design treated as a one-liner.
- **Evidence**: live venv `ai-sdlc-tools 0.62.0` vs planned `VERSION 0.63.0`; CLAUDE.md BRANCH-1; ADR-052's `cp`-only bootstrap by contrast.
- **Proposed fix**: Add a named build phase for the re-install AND record the standing obligation + shared-venv side effect in ADR-058; apply ADR-052's bootstrap-honesty precedent (non-zero TVFS-1 at slice-059's own Step 6 is the EXPECTED signal).
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "Self-application / bootstrap (slice-059 only) — B3" rewritten: (1) explicit named build-sequence step `$PY -m pip install --upgrade .` after the 4-part bump, before the Step 6 audit sweep; (2) bootstrap-honesty — a non-zero TVFS-1 before the re-install is the expected signal; (3) the shared-venv-from-branch side effect is disclosed as bounded (the branch becomes the default branch on `/commit-slice --merge`). `ADR-058` Consequences records the standing slice-060+ obligation; no `/build-slice` SKILL.md step is added (the HALT IS the enforcement).

### Majors (address this slice)

#### M1: `--root` carried by clone without the deadness analysis applied to `_normalized_bytes`

- **Claim under review**: design.md "Deliberate divergence" — documented dropping `_normalized_bytes` as dead code, silent on `--root`.
- **Issue**: Inconsistent deadness analysis. `--root` is in fact *not* dead (TVFS-1 reads in-repo `VERSION`), but the design should say so explicitly, as it did for `_normalized_bytes`.
- **Evidence**: `tools/ai_sdlc_version_forward_sync.py:209-214` / `:132`.
- **Proposed fix**: One sentence stating `--root` is retained because TVFS-1 still reads in-repo `VERSION`, naming the test that exercises it.
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "Deliberate divergence from the AVFS-1 clone" now analyses both: `_normalized_bytes` DROPPED (dead — string compare), `--root` RETAINED (live — parameterizes the in-repo `VERSION` read, exercised by the `usage`-state test).

#### M2: Shippability row number unspecified

- **Claim under review**: design.md "one new row in `architecture/shippability.md`".
- **Issue**: ADR-052 pinned AVFS-1's row number ("#50, verified next-free"); TVFS-1's design named none. Catalog max is #58.
- **Evidence**: `architecture/shippability.md` last row `| 58 |`; ADR-052 row-#50 precedent.
- **Proposed fix**: Pin row **#59** (verified next-free: max = #58).
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "What's new" + "Non-catalog" + `ADR-058` Consequences now pin shippability **row #59** (next-free: catalog max #58; Builder re-confirms at build), carrying the two in-repo-only entry-pin tests.

#### M3: WARN-exit-0 on not-installed can mask "installed but invisible to this interpreter"

- **Claim under review**: design.md "Error model" warn branch.
- **Issue**: AVFS-1's absent case (no file) is unambiguously benign. TVFS-1's absent case ("not in this interpreter's metadata") can co-exist with a stale install reachable another way; the design did not distinguish them.
- **Evidence**: AVFS-1 `tools/ai_sdlc_version_forward_sync.py:149-160`; mission-brief Intent (the incident is *stale*, i.e. installed).
- **Proposed fix**: Keep WARN-exit-0 (HALT would over-fire), but make the WARN message name `sys.executable`; record in ADR-058 that TVFS-1's WARN is weaker than AVFS-1's.
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "Error model" warn branch now requires the message to name `sys.executable` + `purelib` and direct the user to verify `$PY`. `ADR-058` Consequences records the weaker-WARN distinction explicitly.

### Minors (log; address if cheap)

#### m1: `install_audit.py` stale tool-count prose worsened by one

- **Claim under review**: design.md "Out of scope" — the stale count prose left untouched while `_CANONICAL_TOOLS` is edited.
- **Issue**: `install_audit.py:25` ("all 13 tool modules") and `:67` ("The 20 tool modules") are already stale (`_CANONICAL_TOOLS` has 26); this slice makes it 27. The slice-058 BC-PROJ-11 lesson says remove the literal when you are already editing the file. The design said "separately tracked" but cited no tracking artifact.
- **Evidence**: `tools/install_audit.py:25`, `:67`, `:77-104`.
- **Proposed fix**: Scrub the two count literals while the file is open, or cite a real tracking artifact.
- **Builder draft**: **ACCEPTED-FIXED.** Folded in — `design.md` "What's modified" now scrubs both stale count literals in `install_audit.py` (reworded to drop the number, per the slice-058 "remove the literal" lesson) in the same edit that adds the 27th `_CANONICAL_TOOLS` entry. "Out of scope" reworded to distinguish the count-scrub (in-scope-adjacent) from the import-tautology (genuinely separate).

#### m2: Version-bump coupling not recorded as verified

- **Claim under review**: design.md plans `## v0.63.0`; ADR-058 "0.62.0 → 0.63.0".
- **Issue**: The Critic verified the changelog head is `v0.62.0` (no `v0.63.0` collision) — fine, but design.md did not record the verification (ADR-052 recorded "verified next-free" for its row).
- **Evidence**: `methodology-changelog.md` head `## v0.62.0`; `VERSION`/`plugin.yaml`/`pyproject.toml` all `0.62.0`.
- **Proposed fix**: Add a one-line "verified head = v0.62.0" note.
- **Builder draft**: **ACCEPTED-FIXED.** `design.md` "What's modified" now records "verified changelog head = `## v0.62.0`; next-free = `## v0.63.0`, no collision."

## Dimensions checked

- [x] Unfounded assumptions — **B1** (the `importlib.metadata` is-CWD-independent claim was empirically false — in-repo `.egg-info` shadows the venv `.dist-info`).
- [x] Missing edge cases — **M3** (`None`/not-installed WARN can mask "installed but invisible to this interpreter"); **B3** (the slice-059-own-Step-6 bootstrap state was an unhandled first-run edge).
- [x] Over-engineering — **M1** (`--root` carried without deadness analysis). Otherwise appropriately scoped (correctly drops `_normalized_bytes`; correctly rejects a PVFS-1-style assertion-only build in ADR-058).
- [x] Under-engineering — **B2** (AC #3's non-tautological drift case had no delivering design element — no injection seam).
- [x] Contract gaps — none beyond B2/M1. Tri-state exit contract well-specified, cloned faithfully; read-only idempotent audit.
- [x] Security — none. Local read-only audit; no untrusted input, no auth surface, no secrets. Authorization correctly N/A.
- [x] Drift from vault — none. ADR-058 sits on the satisfied side of ADR-056's tool-vs-pytest boundary and extends (not supersedes) the AVFS-1/MCFS-1 lineage; `supersedes: null` correct. m1 notes a pre-existing stale-count drift, now folded in.
- [x] Web-known issues — the `importlib.metadata` / `.egg-info`-on-`sys.path` shadowing was verified empirically against the live repo+venv (standard documented setuptools behaviour, not a post-cutoff change).
- [x] Cross-cutting conformance — **B3** (BRANCH-1: `pip install --upgrade .` from a slice branch mutates the shared venv). N+1-doctrine self-application: B1+B3 are the "novel structural edge the first-Critic under-weights" — caught here. APED-1: the `importlib.metadata` read was executed against real artifacts; that execution produced B1.

## Triage

**Triaged by**: user
**Date**: 2026-05-23
**Final verdict**: CLEAN

Reconciles both Critic passes: the first Critic's 8 findings (all meta-Critic-confirmed VALID at correct severity — 0 suspicious, 0 severity adjustments) + the meta-Critic's 2 missed findings (M-add-1, M-add-2, both Minor). User ratified all Builder draft dispositions unchanged. Every fix is applied to `design.md` / `ADR-058` before this triage; B1's corrected mechanism was empirically re-verified.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §"Installed-version read mechanism (B1 — corrected)" + ADR-058 — `distributions(path=[sysconfig purelib])`; egg-info exclusion empirically re-verified |
| B2 | Blocker | ACCEPTED-FIXED | design.md §"check() injection seam (B2)" — `installed_version_resolver` injectable callable |
| B3 | Blocker | ACCEPTED-FIXED | design.md §"Self-application / bootstrap — B3" — named `pip install --upgrade .` build step + bootstrap-honesty + shared-venv disclosure |
| M1 | Major | ACCEPTED-FIXED | design.md §"Deliberate divergence" — `--root` deadness analysis added (retained: live) |
| M2 | Major | ACCEPTED-FIXED | design.md + ADR-058 — shippability row #59 pinned (catalog max #58) |
| M3 | Major | ACCEPTED-FIXED | design.md §"Error model" warn branch — message names `sys.executable` + `purelib` |
| m1 | Minor | ACCEPTED-FIXED | design.md §"What's modified" — 2 stale tool-count literal scrubs folded into the `install_audit.py` edit |
| m2 | Minor | ACCEPTED-FIXED | design.md §"What's modified" — "verified changelog head = v0.62.0" note added |
| M-add-1 | Minor | ACCEPTED-FIXED | design.md install_audit bullet — `:25` scrub carries a cross-ref to the scoped-out `_check_tool_modules` CWD-import-shadowing |
| M-add-2 | Minor | ACCEPTED-FIXED | design.md §"Error model" — distinct `>1` duplicate-`.dist-info` exit-2 sub-message + read-mechanism comment corrected |
