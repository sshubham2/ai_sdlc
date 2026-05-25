# Critique Review: Slice 059 add-tools-package-version-gate

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-22
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's empirical attack (APED-1) was excellent and load-bearing — it disproved the original design's central correctness claim by experiment, not by reading. All 8 findings are VALID with correct severities and the post-fix design.md addresses each. However, an independent re-application of the 8 dimensions surfaces two missed concerns: a `>1` ("defensive error") exit-2 branch that is empirically reachable on every contributor's machine, not a far-fetched defensive edge, and a stale `--strict` import-time literal in `install_audit.py:25` that the m1 scrub scope misses by one site.

## Confirmed findings

First-Critic findings the meta-Critic agrees with (VALID + correct severity):

- **B1** (`importlib.metadata` CWD-shadowed by in-repo egg-info) — confirmed; Blocker is correct. Independently reproduced: from the repo root `distributions()` returns two `ai-sdlc-tools` entries (`ai_sdlc_tools.egg-info` + the venv `.dist-info`), and naive `version()` resolves the egg-info first; from `/tmp` only the venv copy is found. The shadowing is genuinely CWD-dependent and PVFS-1 keeps the egg-info tautologically equal to `VERSION`. The corrected `distributions(path=[sysconfig.get_path("purelib")])` mechanism was independently verified to return exactly one entry. Matches design.md§"Installed-version read mechanism (B1 — corrected)".

- **B2** (non-tautological drift case had no injection seam) — confirmed; Blocker is correct. Editing `VERSION` moves both comparison sides, so AC3's "genuinely exercises the mismatch branch (not a tautology)" is unmeetable without a seam. The `installed_version_resolver` keyword-only seam in design.md§"`check()` injection seam (B2)" resolves it.

- **B3** (slice-059 bootstrap requires a `pip install --upgrade` the build sequence didn't own; mutates the shared venv on a slice branch) — confirmed; Blocker is correct. TVFS-1 reads the *installed* distribution, so the slice cannot pass its own Step 6 gate until the post-bump artifact is re-installed. design.md§"Self-application / bootstrap (slice-059 only) — B3" addresses it with a named build step, bootstrap-honesty, and the shared-venv disclosure.

- **M1** (`--root` clone-carried without the deadness analysis applied to `_normalized_bytes`) — confirmed; Major is correct. design.md§"Deliberate divergence from the AVFS-1 clone" now analyzes both.

- **M2** (shippability row number unspecified) — confirmed; Major is correct. Independently verified: the catalog's last row is `| 58 |`, so `#59` is next-free.

- **M3** (WARN-exit-0 on not-installed can mask "installed but invisible to this interpreter") — confirmed; Major is correct. The sharpest missed-edge in the first Critic's set: TVFS-1's WARN is structurally weaker than AVFS-1's because AVFS-1 checks a fixed `~/.claude/` path while TVFS-1 checks the *running interpreter's* `purelib`. design.md§"Error model" now requires the WARN message to name `sys.executable` + `purelib`. Correctly Major, not Blocker.

- **m1** (`install_audit.py` stale tool-count prose worsened by one) — confirmed; Minor is correct. Verified the two literals exist and `_CANONICAL_TOOLS` holds 26 entries (slice-059's 27th worsens it). See M-add-1 for a scope refinement.

- **m2** (version-bump coupling not recorded as verified) — confirmed; Minor is correct. Independently verified the changelog head is `## v0.62.0`.

## Suspicious findings

No suspicious findings. Every first-Critic finding is empirically grounded and the severities are well-calibrated. The first Critic did not over-reach on any finding.

## Missed findings

Concerns the first Critic didn't flag, surfaced by independent re-review of the post-fix design.md:

- **M-add-1: the m1 count-literal scrub at `install_audit.py:25` rewords the docstring of the `--strict` flag — itself a B1-class CWD-shadowed surface — without noting the shadowing.** `install_audit.py:25`'s `13` sits in the `Usage:` block documenting `--strict`, whose runtime `_check_tool_modules` importability check is itself CWD-import-shadowed (a `tools/` source folder on `sys.path` shadows the venv install). The design correctly scopes out *fixing* that blind spot — but the m1 scrub rewords exactly that shadowed flag's docstring with no comment, so a future reader sees a freshly-edited line and assumes the flag is sound (McGraw: don't leave a half-corrected hazard looking corrected). Proposed fix: the `:25` scrub appends a one-clause cross-reference to ADR-058 / the scoped-out `_check_tool_modules` shadowing. Minor severity.
  - **Builder draft**: **ACCEPTED-FIXED.** design.md§"What's modified" install_audit bullet now instructs the `:25` scrub to carry a one-clause in-line cross-reference to the scoped-out `_check_tool_modules` CWD-import-shadowing (ADR-058) — turning a silent scope-out into a discoverable one.

- **M-add-2: the `>1 → exit 2 usage` branch is an empirically reachable environment fault, not a far-fetched defensive edge, and its remediation message was unspecified.** The corrected `purelib`-scoped resolver excludes the in-repo egg-info, so `>1` cannot fire from that cause — but `pip` can leave two `.dist-info` directories *inside* `purelib` after an interrupted upgrade / version-renamed reinstall (a documented `importlib.metadata` failure mode). The original design lumped `>1` into `exit 2 usage` with the "repo malformed" message — a message miscalibration: a stale-`.dist-info` `>1` is an environment fault with a clean fix (`pip uninstall` + reinstall), not a malformed repo. The first Critic surfaced M3 (the `None`/WARN arm of the resolver's cardinality space) but not the symmetric `>1` arm. Proposed fix: the `>1` case gets its own actionable exit-2 sub-message naming the duplicate-dist-info remediation. Minor severity. *Meta-Critic note: the Builder should confirm the `>1` branch is wired to a distinct message; if the duplicate-dist-info case is judged too rare to warrant a dedicated string, OVERRIDDEN-AT-TRIAGE is a reasonable outcome and the meta-Critic would not contest it.*
  - **Builder draft**: **ACCEPTED-FIXED.** design.md§"Error model" now splits the `>1` case into its own `exit 2 — usage / duplicate-dist sub-case` with a distinct actionable message (`$PY -m pip uninstall ai-sdlc-tools` then re-run INSTALL.md Step 3g), and the read-mechanism comment is corrected from ">1 → defensive error / impossible" to ">1 → environment fault". Exit code stays 2 — no 4th exit code, the AVFS-1 tri-state contract is preserved. The fix is a 1-line message specialization, cheap and strictly clearer; the Builder judges it worth adopting rather than overriding.

## Severity adjustments

No severity adjustments. All 8 first-Critic findings (B1, B2, B3, M1, M2, M3, m1, m2) are filed at the correct severity. The Blocker/Major/Minor split is well-calibrated: the three Blockers each break an acceptance criterion (B1 → AC2 false-green, B2 → AC3 untestable, B3 → AC4/pre-finish gate unmeetable), the three Majors are real but non-AC-breaking, and the two Minors are prose-only. M-add-1 and M-add-2 are both Minor.

## Notes

Confidence in this review is high — every load-bearing claim in design.md was independently reproduced against the live repo (the two-distribution shadowing, the `purelib`-scoped single-hit, the catalog max row #58, the changelog head v0.62.0, the 26-entry `_CANONICAL_TOOLS`, the two count-literal sites). The first Critic's calibration in this slice is a model case: the APED-1 empirical attack on B1 is exactly right for a codification-class slice whose correctness rests on a runtime-resolution claim; zero manufactured findings, no missed Blocker hiding behind a cluster of Minors. The two missed findings are both Minor-class and both concern the symmetric completeness of edges the first Critic already half-covered (M3 covered the `None` arm of the resolver's cardinality space; M-add-2 covers the `>1` arm). Neither rises to Blocker or Major — this is an EXTEND of modest weight, not a re-litigation.
