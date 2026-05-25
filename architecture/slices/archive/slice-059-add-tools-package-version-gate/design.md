# Design: Slice 059 add-tools-package-version-gate

**Date**: 2026-05-22
**Mode**: Standard

> **Revision note (post-/critique, 2026-05-22)**: rewritten after the Critic's BLOCKED verdict. B1 proved the original "CWD-shadowing correctness note" was empirically false — an in-repo `ai_sdlc_tools.egg-info/` shadows the venv `.dist-info` on the default metadata path. The installed-version read mechanism, the `check()` injection seam, the bootstrap treatment, and the shippability row number are all corrected below. See `critique.md` for the full finding set + dispositions.

## Context refinement (vs. mission brief)

The mission brief framed the gap against AVFS-1 alone. `/design-slice` Step 0 surfaced **ADR-056 / PVFS-1** (slice-054), which gates `pyproject.toml [project].version == VERSION`. This sharpens — not changes — the slice:

- **PVFS-1 gates the SOURCE version label** (`pyproject.toml`, in-repo). After slice-054 every `pip install <repo>` *builds* a correctly-versioned wheel.
- **No gate covers the INSTALLED artifact.** The drift observed this session — installed `ai-sdlc-tools 0.20.0` while `VERSION` is `0.62.0` — is precisely the residue PVFS-1 cannot catch: PVFS-1 makes the *next* install correct; it never forces the *re-install*.

TVFS-1 closes the last ungated version-bearing leg. The full family after this slice: VERSION (source of truth); `plugin.yaml.version` — PMI-1 (in-repo); `pyproject.toml [project].version` — PVFS-1 / [[ADR-056]] (in-repo, pytest assertion); `~/.claude/ai-sdlc-VERSION` — AVFS-1 / [[ADR-052]] (out-of-repo, standalone tool); `~/.claude/methodology-changelog.md` — MCFS-1 (out-of-repo, standalone tool); installed `ai-sdlc-tools` pip-dist version — **TVFS-1 this slice** (out-of-repo, standalone tool).

## What's new

- `tools/ai_sdlc_tools_version_forward_sync.py` — new audit module (TVFS-1). Compares the version of the `ai-sdlc-tools` distribution **installed in the running interpreter's venv site-packages** against the trimmed in-repo `VERSION`. Tri-state exit contract (see Error model).
- `tests/methodology/test_ai_sdlc_tools_version_forward_sync.py` — regression suite. Two layers:
  1. **Seam-injected** state coverage — all four states (synced / drift-HALT / not-installed-WARN / usage) driven through the `installed_version_resolver` injection seam (B2), each genuinely exercising its branch with no tautology.
  2. **Real-resolver egg-info-isolation test** — places a divergent `ai_sdlc_tools.egg-info/PKG-INFO` on the metadata path (a temp dir on `sys.path`) and asserts the *real* `_resolve_installed_version()` still returns the venv `.dist-info` version, not the egg-info version. This is the test that would have caught B1; it pins the B1 fix.
- Two content-bearing entry-pin tests in the existing `tests/methodology/test_methodology_changelog.py`: `test_v_0_63_0_tvfs_1_entry_present_in_repo` + `test_v_0_63_0_tvfs_1_shippability_consumer_propagation` (slice-051 / PVFS-1 precedent — NOT thin presence checks).
- `architecture/decisions/ADR-058-mint-tvfs-1-tools-package-version-forward-sync.md` — new ADR (reversibility: cheap).
- `methodology-changelog.md` — new `## v0.63.0` entry minting **TVFS-1**.
- One new row in `architecture/shippability.md` — **row #59** (next-free: catalog max = #58; Builder re-confirms at build), carrying the two in-repo-only entry-pin tests (not the tool — see Non-catalog note).

## What's modified

- `VERSION` `0.62.0 → 0.63.0`; `plugin.yaml` `version:` + new `- path: tools/ai_sdlc_tools_version_forward_sync.py` entry; `pyproject.toml [project].version` `0.62.0 → 0.63.0` (PVFS-1) — the atomic 4-part PMI-1 bump. (Verified changelog head = `## v0.62.0`; next-free = `## v0.63.0`, no collision — m2.)
- `tools/install_audit.py` — add `"tools.ai_sdlc_tools_version_forward_sync"` to `_CANONICAL_TOOLS` (sorts first; `ai_sdlc_t…` < `ai_sdlc_v…`) + a one-line slice-059 provenance comment. **Also scrub the two stale hard-coded tool-count literals** in the same file (`:25` `Usage:`-docstring "all 13 tool modules", `:67` comment "The 20 tool modules") — reworded to drop the literal, per the slice-058 BC-PROJ-11 lesson ("remove the literal, don't refresh it"). This slice adds the 27th `_CANONICAL_TOOLS` entry; leaving the literals would worsen the drift by one (m1). The `:25` scrub additionally carries a one-clause in-line cross-reference to the scoped-out `_check_tool_modules` CWD-import-shadowing (see Out of scope + [[ADR-058]]): line 25 documents the `--strict` flag, whose importability check is itself B1-class shadow-prone — the reworded line must not read as certifying that flag sound (M-add-1).
- `skills/build-slice/SKILL.md` — Step 6 pre-finish: new checklist item + new `#### ai-sdlc-tools version forward-sync audit (TVFS-1)` section, mirroring the AVFS-1 section.
- `skills/reflect/SKILL.md` — new `### Step 5b-tvfs` block, structural mirror of `Step 5b-avfs`.
- Installed copies `~/.claude/skills/build-slice/SKILL.md` + `~/.claude/skills/reflect/SKILL.md` — forward-synced in lock-step (both skills are in the OSDG-1 / mini-CAD guarded set — see Must-not-defer).
- Installed `~/.claude/ai-sdlc-VERSION` (AVFS-1 leg) + `~/.claude/methodology-changelog.md` (MCFS-1 leg) — forward-synced as part of the 4-part bump.

## What's reused

- `tools/ai_sdlc_version_forward_sync.py` — the structural template. TVFS-1 clones its CLI shape (`--check` / `--json` / `--root`), its `CheckResult` dataclass, its tri-state exit-code contract, and its `_format_human` rendering.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` (UTF8-STDOUT-1).
- [[ADR-029]] — the deterministic-downstream-gate rationale.
- [[ADR-052]] (AVFS-1) — the tool-bearing out-of-repo-leg precedent. [[ADR-056]] (PVFS-1) — the tool-vs-pytest boundary this ADR sits on the other side of.

## Components touched

### `tools/ai_sdlc_tools_version_forward_sync.py` (new)
- **Responsibility**: Assert the `ai-sdlc-tools` pip distribution installed in the pipeline's venv equals in-repo `VERSION`, so a stale venv package (INSTALL.md Step 3g not re-run after a version bump) fails a pipeline gate the moment it happens.
- **Lives at**: `tools/ai_sdlc_tools_version_forward_sync.py` (created by this slice).
- **Key interactions**: reads distribution metadata scoped to `sysconfig.get_path("purelib")` + the in-repo `VERSION` file; emits via `tools._stdout`. Invoked by `/build-slice` Step 6 and `/reflect` Step 5b-tvfs. Leaf module — imported only by its own regression test.

### Installed-version read mechanism (B1 — corrected)

The original design claimed `importlib.metadata.version("ai-sdlc-tools")` returns the venv-installed version because "no `.dist-info` exists in-tree." **This is false** and was proven so by the Critic and re-verified by the Builder:

- `setuptools` writes an `ai_sdlc_tools.egg-info/` directory into the **source tree** on `pip install` (gitignored at `.gitignore:15`, but present on disk; its `PKG-INFO` carries a `Version:` field regenerated from `pyproject.toml`).
- `importlib.metadata` discovers metadata from **every `sys.path` entry**, and `sys.path[0]` is the CWD/invocation dir. Verified live: `importlib.metadata.distributions()` finds **two** `ai-sdlc-tools` — the in-repo `egg-info` AND the venv `.dist-info`; the naive `version()` resolves the **in-repo egg-info first**.
- Because PVFS-1 keeps `pyproject.toml == VERSION` and the egg-info `Version` regenerates from `pyproject.toml`, the naive read compares `VERSION` against a source-derived copy of `VERSION` — **tautologically green even when the venv is stale**. Identical in effect to the `install_audit.py` CWD-import tautology this slice explicitly does NOT claim to fix.

**Corrected mechanism** — `_resolve_installed_version() -> str | None`:
```python
purelib = sysconfig.get_path("purelib")            # the running interpreter's site-packages
dists = [d for d in importlib.metadata.distributions(path=[purelib])
         if _norm(d.metadata["Name"]) == "ai-sdlc-tools"]
# 0 → None (not installed in this venv); 1 → d.version; >1 → environment fault (M-add-2)
```
Scoping `distributions(path=[purelib])` to `sysconfig.get_path("purelib")` excludes the in-repo `egg-info` **by construction** (it is not under site-packages). Verified live: scoped enumeration returns only `…\.venv\Lib\site-packages\ai_sdlc_tools-0.62.0.dist-info`. The audit always runs under `$PY` (the venv interpreter) per the pipeline `$PY` convention, so `purelib` IS the pipeline's venv site-packages — exactly the artifact to gate. This is also why `_resolve_installed_version()` returns `None` on the empty case rather than catching `PackageNotFoundError`: the enumerate-and-filter approach never raises (it satisfies the mission-brief must-not-defer "graceful not-installed handling" by a `None` branch, not exception handling).

### `check()` injection seam (B2)

So the regression suite can drive a genuine non-tautological drift case without mutating `VERSION` or the global metadata store, `check()` takes the installed-version resolver as an injectable seam (AVFS-1's `installed`-path parameter is the precedent — AVFS-1's installed side is an injectable Path; TVFS-1's is an injectable callable):

```python
def check(root: Path, *,
          installed_version_resolver: Callable[[], str | None] = _resolve_installed_version
          ) -> CheckResult
```

The seam-injected tests pass `lambda: "9.9.9"` (drift — distinct from any real `VERSION`), `lambda: <current VERSION>` (synced), `lambda: None` (not-installed WARN). The `usage` state is driven by `root` pointing at a fixture dir with no `VERSION`. The real-resolver egg-info-isolation test (see What's new) exercises `_resolve_installed_version()` itself so the seam tests are not the only coverage of the real read path.

### Deliberate divergence from the AVFS-1 clone
TVFS-1 clones AVFS-1's CLI + exit-code + dataclass structure. Two deliberate divergences, each with the deadness analysis applied:
- **`_normalized_bytes` / CRLF→LF machinery — DROPPED.** AVFS-1 byte-compares two files modulo line endings (EOL-DRIFT-1). TVFS-1's installed side is an `importlib.metadata` version string (already clean — no line endings); equality is plain trimmed-string `==`. The CRLF→LF machinery would be dead code.
- **`--root` — RETAINED.** Unlike `_normalized_bytes`, `--root` is *not* dead: TVFS-1 still reads the in-repo `VERSION` file, whose location depends on the repo root. `--root` parameterizes that read and is exercised by the `usage`-state regression test (a fixture `root` with no `VERSION`). It is kept by analysis, not clone-inertia (M1).

### Why a standalone tool (not a PVFS-1-style pytest assertion)
[[ADR-056]] established: out-of-repo runtime read ⇒ tool; in-repo read ⇒ pytest assertion. TVFS-1 reads the venv-installed distribution — out-of-repo, environment-mutable. Two structural needs a bare pytest `assert` cannot meet: (1) **WARN-exit-0 on "not installed in this venv"** — a binary `assert` would turn a machine that simply hasn't installed the plugin into a false slice-regression FAILURE; the forward-sync family's defining semantics for out-of-repo legs is WARN-exit-0-on-absent. (2) **Wiring parity** — AVFS-1/MCFS-1 are non-opt-out tool gates at `/build-slice` Step 6 + `/reflect` Step 5b-X. ADR-058 records the full options analysis.

## Contracts added or changed

### TVFS-1 audit CLI — exit-code contract
- **Defined in code at**: `tools/ai_sdlc_tools_version_forward_sync.py` (`check()` + `_resolve_installed_version()` + `main()`), to be created.
- **Consumed by**: `skills/build-slice/SKILL.md` Step 6, `skills/reflect/SKILL.md` Step 5b-tvfs (both treat non-zero as HALT).
- **CLI surface**: `python -m tools.ai_sdlc_tools_version_forward_sync [--check] [--json] [--root <path>]` — mirrors AVFS-1.
- **Internal seam**: `check(root, *, installed_version_resolver=_resolve_installed_version)` — the resolver is the test injection point (B2); not a CLI flag.
- No runtime/HTTP contract, no auth surface — local read-only audit tool.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/ai_sdlc_tools_version_forward_sync.py` | `skills/build-slice/SKILL.md` Step 6 + `skills/reflect/SKILL.md` Step 5b-tvfs (both invoke `$PY -m tools.ai_sdlc_tools_version_forward_sync`) | `tests/methodology/test_ai_sdlc_tools_version_forward_sync.py` | — |

The two entry-pin functions are added to the **existing** `tests/methodology/test_methodology_changelog.py` — not a new module, no wiring-matrix row.

### Non-catalog by construction
Like AVFS-1, the TVFS-1 tool reads environment-mutable, untracked installed state — a shippability `Machine-cmd` must not depend on such state (slice-029/030A discipline). The TVFS-1 **tool** is therefore NOT shippability-cited, and `test_ai_sdlc_tools_version_forward_sync.py` (reads installed state) is intentionally NOT catalog-cited. Shippability **row #59** carries the in-repo-only entry-pin tests instead — exact AVFS-1 row-#50 precedent.

## Decisions made (ADRs)

- [[ADR-058]] — Mint TVFS-1: the installed `ai-sdlc-tools` pip-package version MUST equal `VERSION`, enforced by a new standalone tool that reads distribution metadata scoped to the venv site-packages (out-of-repo runtime read justifies a tool per the ADR-056 boundary). Reversibility: **cheap**.

## Authorization model for this slice

N/A — local read-only audit tool, no auth surface, no protected action.

## Error model for this slice

TVFS-1 tri-state exit contract (clone of AVFS-1's, semantics adjusted for the metadata-scoped source):

- **exit 0 — `synced`**: resolver returns a version equal to `VERSION.strip()`.
- **exit 0 — `warn`**: resolver returns `None` — no `ai-sdlc-tools` distribution in this interpreter's venv site-packages. The pip package is environment-dependent/untracked; a machine that simply hasn't installed the plugin must not HALT `/build-slice` (AVFS-1 installed-absent parity). **The WARN message MUST name `sys.executable` and `purelib`** and state: *"if you have installed `ai-sdlc-tools`, it is not visible to THIS interpreter — verify `$PY` points at `~/.claude/.venv` per `~/.claude/CLAUDE.md`."* (M3 — TVFS-1's WARN is *weaker* than AVFS-1's: AVFS-1 absent = unambiguous no-file; TVFS-1 absent = "not in this interpreter's site-packages", which can co-exist with a stale install reachable by another interpreter. Recorded in ADR-058.)
- **exit 1 — `drift` (HALT)**: resolver returns a version ≠ `VERSION`. Attributed message: *"AI-SDLC-TOOLS VERSION DRIFT — installed `ai-sdlc-tools` v\<X\> ≠ in-repo VERSION v\<Y\>; re-run INSTALL.md Step 3g (`$PY -m pip install --upgrade <source>`); this is NOT a slice regression."*
- **exit 2 — `usage`**: in-repo `VERSION` missing/unreadable, or repo root unresolvable.
- **exit 2 — `usage` / duplicate-dist sub-case (M-add-2)**: the resolver finds >1 `ai-sdlc-tools` distribution in `purelib` — NOT impossible (a documented pip failure mode: a stale `ai_sdlc_tools-<old>.dist-info` left beside the current one by an interrupted upgrade / version-renamed reinstall). This is an ENVIRONMENT fault, not a malformed repo, so it carries its OWN distinct actionable message — *"multiple `ai-sdlc-tools` distributions in `<purelib>` — likely a stale `.dist-info` from an interrupted upgrade; run `$PY -m pip uninstall ai-sdlc-tools` then re-run INSTALL.md Step 3g"* — while keeping exit code 2 (no 4th exit code; the AVFS-1 tri-state contract is preserved).

### Self-application / bootstrap (slice-059 only) — B3

slice-059 authors TVFS-1 and is itself the first slice that must satisfy it. The bootstrap is heavier than AVFS-1's (whose installed leg is a `cp` the PMI-1 4-part bump already performs); it must be treated honestly:

1. **Named build-sequence step.** slice-059's build sequence includes, as an **explicit named action AFTER the 4-part version bump (`VERSION`/`plugin.yaml`/`pyproject.toml` → `0.63.0` + changelog) and BEFORE the Step 6 audit sweep**: `$PY -m pip install --upgrade .` — re-installs `ai-sdlc-tools 0.63.0` into the shared venv. `/build-slice`'s phase plan must carry this as a discrete step, not assume it.
2. **Bootstrap-honesty (ADR-052 precedent).** A non-zero TVFS-1 at slice-059's own Step 6 *before* that re-install is the **EXPECTED signal** — the gate working — not a defect. The Step 6 sequence is: run TVFS-1 → if it HALTs on `0.62.0 ≠ 0.63.0`, run the step-1 re-install → re-run TVFS-1 → exit 0.
3. **Shared-venv side effect (honest disclosure).** `/build-slice` runs on a `slice/059-…` branch (BRANCH-1). `pip install --upgrade .` from that branch installs branch-state code into the **shared** `~/.claude/.venv` used by every project. This is bounded and acceptable: the developer IS working on slice-059, so the venv reflecting slice-059 is correct for them; after `/commit-slice --merge` the branch becomes the default branch, so the venv ends up equal to the merged tree. It is recorded as a known side effect, not hidden.

Every slice after 059 inherits a self-gating TVFS-1: any version-bumping slice must `$PY -m pip install --upgrade .` from its branch before Step 6, or TVFS-1 HALTs. **No `/build-slice` SKILL.md step is added for this standing obligation** — the TVFS-1 HALT + its remediation message IS the enforcement (the gate drives the re-install; a separate prose step would be redundant).

## Out of scope (confirmed from mission brief)

- Fixing `install_audit.py`'s `_check_tool_modules` CWD-import-shadowing blind spot — TVFS-1 makes installed-package staleness detectable on its own (version) axis; the module-import tautology is a separate concern. (Note: the stale tool-*count* literals in the same file ARE scrubbed by this slice — see What's modified / m1 — because this slice directly edits the count they are stale against; that is in-scope-adjacent, distinct from the import-tautology which is genuinely separate.)
- Any change to INSTALL.md's install mechanism (Step 3g stays `pip install --upgrade`).
- Continuous / automatic sync between the source repo and `~/.claude/`.
- File-level module-set completeness gating — version equality is the proxy; per-module completeness remains `install_audit.py`'s job.
