# Code Review: Slice 067 add-parallel-slice-queue-output

**code-Critic reviewed**: slice diff vs master merge-base `79081cd0d7ae9f25af86b49a0f20437ea8b3f6a8` (filtered to 12 in-scope paths per ADR-062 union-of-three-sources)
**Date**: 2026-05-25
**Result**: FINDINGS (1 minor; no blockers, no majors)

## Summary

Clean implementation. All 10 new tests pass; both v0.69.0 entry-pin tests pass; OSDG-1 slice SKILL.md drift PASSES; plugin.yaml alphabetical order preserved; PMI-1 5-leg bump consistent across `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` + `## v0.69.0` header + (per design.md) installed `~/.claude/ai-sdlc-VERSION`. The dual-Critic stack's 12 dispositions (11 ACCEPTED-FIXED + 1 OVERRIDDEN) carried through cleanly into the code: B2 enum drift + collision-precedence resolved structurally in `compute_parallel_safety()` early-return guards; M3 SKILL.md insertion at L378-379 verified visually + by OSDG-1 PASS; M2 ImportError guard present in the SKILL.md bash heredoc as designed; BC-PROJ-10 paired-pin test pair present + passing with the canonical naming pattern. The single finding is a minor over-engineering / DRY-violation observation on a defensive duplicate code path in `main()`'s custom-output branch, not load-bearing.

## Changed files (in-scope)

- INSTALL.md
- VERSION
- methodology-changelog.md
- plugin.yaml
- pyproject.toml
- skills/slice/SKILL.md
- tests/methodology/test_methodology_changelog.py
- tests/methodology/test_utf8_stdout_regression.py
- tests/skills/slice/__init__.py
- tests/skills/slice/test_slice_queue_output.py
- tools/install_audit.py
- tools/slice_queue_writer.py

## Findings

### Blockers

None.

### Majors

None.

### Minors

#### m1: `main()` custom-output branch duplicates the canonical write logic (Fowler over-engineering / DRY violation; reachability narrow but maintenance risk on next slice-068 schema extension)

- **Claim under review**: `tools/slice_queue_writer.py:592-629` — the `main()` CLI's "Direct write to custom path (rare)" branch re-implements the entire candidate-blast loop + `format_queue_md` + atomic `.tmp` + `os.replace()` write sequence that `write_slice_queue()` already encapsulates at L455-502.
- **Issue**: Per Fowler (*Refactoring* 2nd ed., "Duplicated Code" smell), the two branches at `main()` L585-591 vs L592-629 differ ONLY in (a) the output Path resolution (canonical-vs-custom) and (b) where the resolved Path lives. The candidate iteration, parallel-safety computation, blast-resolver-vs-direct-call selection, format-md call, and atomic write are structurally identical — duplicated. When slice-068 (PSQ-2 claim machinery) extends the entry shape (adding `Claimed-by/-at` field lines per the ADR-064 §Consequences cross-slice contract), the maintainer MUST update BOTH branches or risk silent divergence on the CLI's `--output <custom>` path. This is exactly the slice-022 RSAD-1 / slice-040 N+1 class — duplicated sites are unguarded adversarial surfaces against future fix-block edits.
- **Evidence**:
  - `tools/slice_queue_writer.py:455-502` — canonical `write_slice_queue()` body (candidate loop + format + atomic write).
  - `tools/slice_queue_writer.py:592-629` — the `else:` branch in `main()` repeating ~38 lines of substantially the same logic, with one structural difference: the candidate-side blast computation at L610-611 ALWAYS calls `_call_graphify_blast_radius` directly (no `blast_resolver` injection seam plumbed through), so the custom-output CLI path is NOT testable via the injection seam either.
  - The test suite (`tests/skills/slice/test_slice_queue_output.py`) exercises ZERO CLI invocations — both branches of `main()` are completely uncovered by this slice's tests.
- **Proposed fix**: Refactor `write_slice_queue()` to accept an optional `out_path: Path | None = None` parameter; when None, default to `repo_root / "architecture" / _QUEUE_FILENAME` (current behavior). Then `main()` collapses to a single call passing `out_path=out_arg` resolved against `--root`. This (a) eliminates the duplicated candidate-blast + format + atomic-write logic; (b) makes the `--output <custom>` CLI path testable via the existing `blast_resolver` injection seam; (c) inoculates against silent divergence on slice-068's PSQ-2 entry-shape extension.
- **Severity rationale**: Minor, not Major, because (a) the canonical-output path is the load-bearing one (it's what `/slice` Step 6.5 invokes via the library API, not the CLI); (b) the custom-output CLI branch is documented as "rare" by the Builder; (c) no test currently exercises CLI mode so a silent divergence wouldn't break existing tests today; (d) slice-068 PSQ-2 will likely add a new test file at the same time it extends the format, providing a natural catch-point. Worth fixing if cheap; not a ship-blocker.

## Dimensions checked

- [x] **Unfounded assumptions** — none. `_call_graphify_blast_radius`'s claim "current graphify node-ID shape uses basenames" empirically validated against actual `graphify blast-radius --help` output (`--file FILE_PATH` flag exists at slice-067 build time). `--from` fallback handles legacy shape. Graphify exits 1 on node-not-found (empirically confirmed against actual graph file), so the `if res.returncode != 0: continue` retry-on-failure semantics correctly trigger the fallback. Docstring example at `tools/slice_queue_writer.py:38-46` matches the actual `write_slice_queue` signature.
- [x] **Missing edge cases** — none load-bearing. Empty hint_files / zero active slices / graph-missing / empty candidates list all covered by AC4's four sub-cases; precedence-collision case explicitly tested in `test_empty_hint_files_overrides_zero_active_slices_to_unknown_no_hint_files`. Concurrent /slice invocations covered structurally by atomic `.tmp` + `os.replace()`; crash-durability via `os.fsync()` explicitly OUT OF SCOPE per design.md L116.
- [x] **Over-engineering** — m1 (DRY duplication in `main()` custom-output branch). No other speculative-generality; 5-function helper API decomposes cleanly along testability axes per slice-059/063 injection-seam precedent.
- [x] **Under-engineering** — none. All 6 ACs have ≥1 passing test; BC-PROJ-10 paired-pin pair present with canonical naming matching slice-066 v0.68.0 BRANCH-2 precedent; OSDG-1 PASSES on `skills/slice/SKILL.md`.
- [x] **Contract gaps** — none. All 4 public functions in `tools/slice_queue_writer.py` carry type hints + substantive docstrings; `compute_parallel_safety()` `graph_missing` kwarg-only parameter forces caller intent at call site. CLI argparse + missing-file + malformed-JSON + non-list-JSON failure modes all empirically traced through code.
- [x] **Security** — none. Methodology-internal helper; no external surface; fixed-argv subprocess invocation (no shell injection); file reads constrained to repo-root with no user-controlled traversal; no secrets/credentials/tokens.
- [x] **Drift from vault** — none. plugin.yaml + install_audit insertions preserve alphabetical order; test_utf8_stdout append follows chronological-by-slice tail pattern; INSTALL.md 28→29 at BOTH L22 + L166 only; VERSION + plugin.yaml + pyproject.toml + ## v0.69.0 header all consistent; methodology-changelog v0.69.0 entry passes META-1 + both BC-PROJ-10 paired-pin tests PASS empirically.
- [x] **Web-known issues** — Skipped — WebSearch not invoked. /critique pass already verified `os.replace()` cross-platform atomicity. No NEW API surfaces require fresh verification (argparse / json / subprocess / pathlib / datetime are stable stdlib). graphify CLI flags verified empirically against local installed graphify.
- [x] **Cross-cutting conformance** — none. **RSAD-1**: PSQ-1 is methodology-output rule; "slice's own code survives the discipline it ships" satisfied trivially (bootstrap-discharge instance #1 documented). **APED-1**: no audit parse-rule changes; not fired. **EOL-DRIFT-1**: no new byte-compares on `.md` content; not fired. **Phantom-import**: `from tools import _stdout` at `tools/slice_queue_writer.py:74` verified — `tools/_stdout.py` exists with `reconfigure_stdout_utf8` symbol at L30. **Algorithm-path-conformance**: `_call_graphify_blast_radius` retry-on-failure semantics empirically traced against actual graphify CLI behavior. **Language-version conformance**: `from __future__ import annotations` makes generic type hints evaluation-deferred (defensive but harmless on Python 3.13). **Runtime-environment**: `pathlib.Path` used throughout (no string concat); `os.replace()` documented atomic on POSIX + Windows; must-not-defer #2 satisfied.

## CRSI-1 v1 disposition

Per CRSI-1 v1 walking-skeleton + slice-063/064/065/066 precedent (N=4 cumulative cleanups deferred in-band to bundled-cleanup slices), the single m1 advisory finding is declined in-band. Slice-068+ bundled cleanup nomination: extract `write_slice_queue(out_path=...)` optional parameter + collapse `main()` to single call + add CLI invocation test via `blast_resolver` injection seam. ~15-20 minutes estimated work.

**CRSI-1 walking-skeleton validated at N=5 cumulative** (slice-063 N=1 + slice-064 N=2 + slice-065 N=3 + slice-066 N=4 + slice-067 N=5 — code-Critic finds genuine novel finding on a slice whose dual-Critic stack passed CLEAN at TRI-1). The structural differentiation pattern (design-stack catches design-claim consistency + ADR identifiers + regex grammar pinning + schema completeness + cross-document citation hygiene; code-stack catches line-level POSIX/runtime portability + Windows path edge cases + DRY-violations in narrow code paths + empirical-fixture-load-bearing-checks) continues to hold at N=5.
