# Reflection: Slice 059 add-tools-package-version-gate

**Date**: 2026-05-23
**Shipped**: YES

## Validated

- The purelib-scoped read mechanism (`importlib.metadata.distributions(path=[sysconfig.get_path("purelib")])`) — validated by `test_real_resolver_excludes_in_repo_egg_info` AND the live `/validate-slice` AC1 run (`--root <tmp with VERSION=9.9.9>` → DRIFT exit 1 against the venv `0.63.0`). The B1-corrected design is not just plausible — it is empirically proven to exclude the in-repo `egg-info`.
- The tri-state exit contract (0 synced / 0 not-installed-WARN / 1 drift-HALT / 2 usage) — validated by the 8-test suite exercising every state including the M-add-2 `>1` duplicate-distribution case.
- ADR-058's Route C (standalone tool, not a PVFS-1-style pytest assertion) — validated: the tool needs the WARN-exit-0 tri-state a binary `assert` cannot express; the bootstrap re-install path exercised it.
- TVFS-1 as a self-gating gate — validated at slice-059's own Step 6: after `pip install --upgrade .` the venv `ai-sdlc-tools` = `0.63.0` = VERSION, TVFS-1 exits 0 synced. The gate gated its own slice.
- The `--root` CLI flag is genuinely live (M1) — exercised end-to-end by the AC1 real-mismatch validation run.

## Corrected

- Nothing corrected at `/reflect`. The one load-bearing correction — B1, the original design's false "no `.dist-info` exists in-tree" claim — was caught and fixed at `/critique` (design.md + ADR-058 rewritten before build). Build + validate reality *confirmed* the corrected design; no further correction needed.

## Discovered

- **Adding a new `tools/` module has five registration touchpoints, not three.** The design enumerated `plugin.yaml` + `install_audit.py` `_CANONICAL_TOOLS` + `architecture/shippability.md`. Two more surfaced only as methodology-suite FAILures at build Step 6: (4) `INSTALL.md`'s test-enforced tool-count literal (`test_install_md_tool_count_matches_plugin_yaml` — slice-045/R-11 lineage), and (5) `tests/methodology/test_utf8_stdout_regression.py`'s cp1252-coverage parametrize list (`_ROOT_ONLY_TOOLS` — the ADR-026 version-agnostic UTF-8 rollup sentinel requires every `main()`-bearing tool to carry coverage). Impact: the next tool-adding slice should enumerate all five upfront. Build-time-reachable and gate-caught at intended latency (slice-037 law) — a `/critic-calibrate` watch-list candidate, not a BC-1 promotion at N=1.
- **`install_audit.py` `_check_tool_modules` is itself CWD-import-shadowed** (low-severity residual, explicitly scoped OUT of slice-059): `--strict`'s `importlib.import_module("tools.X")` resolves from `sys.path`, so run from the source repo it imports the in-repo `tools/`, not the venv. INST-1 can report "27/27 importable" while the venv is stale. Practically mostly mooted by TVFS-1 — a synced version implies the current package implies all modules present — so it is a known-limitation, not a tracked risk (no R-NN minted; design.md documents it as out-of-scope with rationale). A future slice could scope `_check_tool_modules` to the venv for completeness — low priority.

## Deferred

- Fixing `install_audit.py` `_check_tool_modules` CWD-import-shadowing — out of scope per design.md; low-priority follow-up candidate (TVFS-1's version axis practically covers it). Lands in: backlog / a future cleanup slice.
- INSTALL.md install-mechanism changes, continuous source↔`~/.claude` auto-sync, file-level module-set completeness gating — deliberate non-goals per mission-brief "Out of scope"; not deferred work, explicit non-scope.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` (all 10 ACCEPTED-FIXED) + reality observed at build/validate:

- B1 (`importlib.metadata` CWD-shadowed by in-repo egg-info): **VALIDATED** — the first Critic empirically proved it (APED-1 `9.9.9` rewrite experiment); without B1 the slice would have shipped a tautologically-green gate. The corrected purelib-scoped mechanism was re-verified at build + validate. The single highest-value finding of the slice.
- B2 (no injection seam → drift case untestable): **VALIDATED** — the `installed_version_resolver` seam was added; the regression suite's drift test depends on it; AC3's non-tautological requirement was unmeetable without it.
- B3 (bootstrap `pip install` unowned + shared-venv side effect): **VALIDATED** — reality confirmed exactly: at slice-059's Step 6 the venv was `0.62.0` vs VERSION `0.63.0`; the named `pip install --upgrade .` build step was genuinely required.
- M1 (`--root` carried without deadness analysis): **VALIDATED** — `--root` is live and was exercised by the AC1 validation run; the design.md analysis was the right fix.
- M2 (shippability row number unspecified): **VALIDATED** — row #59 pinned; catalog 59/59.
- M3 (WARN can mask "installed but invisible to this interpreter"): **VALIDATED** — the WARN message names `sys.executable`; `test_not_installed_is_warn_exit0` pins it.
- m1 (`install_audit.py` stale count literals): **VALIDATED** — scrub done; reality additionally showed the count-literal class is broader than m1 enumerated (see Missed below).
- m2 (version-bump coupling not recorded verified): **VALIDATED** — trivial, done.
- M-add-1 (m1 scrub rewords a shadow-prone flag's docstring without noting it): **VALIDATED** — cross-ref comment added.
- M-add-2 (`>1` duplicate-dist lumped into generic usage message): **VALIDATED** — distinct exit-2 message added; `test_duplicate_dist_is_usage_exit2_distinct_message` pins it.

**Missed by Critic**: neither the first Critic nor the meta-Critic enumerated the *full* registration-touchpoint set for adding a new `tools/` module. m1 caught the `install_audit.py` count literals but not `INSTALL.md`'s separate test-enforced tool-count literal, and neither Critic flagged `test_utf8_stdout_regression.py`'s cp1252-coverage parametrize list. Both surfaced as methodology-suite FAILures at build Step 6 and were fixed in-band.

**Pattern**: the dual-Critic stack was excellent on the NOVEL mechanism — the first Critic caught B1 empirically via APED-1 (the codification-class N+1 doctrine held; the meta-Critic backstop was not even needed for the load-bearing finding). But both Critics under-enumerated the MECHANICAL registration breadth — the complete set of inventories a new tool touches. This is the known "first Critic optimizes the novel structural edge OR the mechanical surface, under-weighting the other" pattern, here landing on the mechanical side. Correctly caught by the build-time methodology suite (BC-PROJ-4 "run every affected gate on the real artifact") — a build-time-reachable class, gate-caught at intended latency per the slice-037 audit-vs-real-artifact law. The right tooling response is a `/critic-calibrate` watch-list entry ("when a slice adds a `tools/` module, the Critic should enumerate ALL registration touchpoints: plugin.yaml, install_audit `_CANONICAL_TOOLS`, shippability, INSTALL.md tool-count, cp1252-coverage list"), NOT a new first-Critic dimension and NOT a BC-1 promotion at N=1.

## Lessons for next slice

- **Adding a `tools/` module touches five inventories, not three**: `plugin.yaml`, `install_audit.py` `_CANONICAL_TOOLS`, `architecture/shippability.md`, `INSTALL.md`'s tool-count literal, and `test_utf8_stdout_regression.py`'s `_ROOT_ONLY_TOOLS`/cp1252-coverage list. Enumerate all five at design time so they are not discovered as build-Step-6 methodology-suite FAILures.
- **An empirical Critic attack (APED-1) is the right move when a slice's correctness rests on a runtime-resolution claim**: B1 was provable only by *executing* `importlib.metadata` against the real repo+venv, not by reading the design. For any future slice whose load-bearing claim is "mechanism M reads source X", the Critic should run M, not reason about it.
- **TVFS-1 closes the version-bearing-leg family** (PMI-1 / PVFS-1 / AVFS-1 / MCFS-1 / TVFS-1). A future tool-package change should re-confirm no sixth leg has appeared; the family is, for now, complete.

## Vault updates made (thin vault — small list)

- This slice's `design.md` + `ADR-058` — corrected at `/critique` (B1 read-mechanism), already on disk; no `/reflect`-time change.
- `methodology-changelog.md` — `## v0.63.0` TVFS-1 entry (added at build; forward-synced to `~/.claude/`, MCFS-1 exit 0).
- `architecture/shippability.md` — row #59 (added at build; catalog 59/59 PASS).
- `architecture/drift-log.md` — slice-059 audit entry (CLEAN), appended at `/build-slice` Step 6.
- No `risk-register.md` change — slice-059 retires no registered risk; the one discovered residual (`_check_tool_modules` shadowing) is a low-severity known-limitation, captured here, not minted as an R-NN.
