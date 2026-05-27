# Code Review: Slice 071 bundle-066-to-070-code-critic-cleanup

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths per ADR-062 union-of-three-sources)
**Date**: 2026-05-26
**Result**: FINDINGS (0 Blockers + 0 Majors + 5 Minors — all advisory per CRSI-1 v1 walking-skeleton; satisfies AC#5 must-not-defer "0 new structural Majors")

## Summary

A 31-finding cleanup slice that concentrates ~84% of code mass in `tools/slice_queue_writer.py` (252 insertions) + `tools/branch_workflow_audit.py` (52 insertions). All structural FIXes (4-step canonical path-normalization algorithm, MappingProxyType wrap, regex extraction with verbatim test-side import, gitdir-depth + `.git`-existence guards, AuditResult symmetry surface, fixture rewrite with APED-1 load-bearing negative assertion, paired-pin test completion) appear correctly implemented and aligned to the per-finding disposition table. The /critique B1 + /critique-review M-add-1 docstring/assertion alignment was empirically tightened — the four sentinel-test substring assertions all match the as-written module docstring verbatim. No blockers, no majors — only minor cosmetic / design-time-deferred items. **Bundle nominated for slice-072+ cleanup (this slice IS a bundled cleanup; bundle-of-bundles is voluntary-restraint precedent N=7 cumulative on CRSI-1 v1 advisory-only discipline)** — slice-064/065/066/067/068/070 N=6 → slice-071 N=7 cumulative.

## Changed files (in-scope)

```
.gitignore
architecture/slices/slice-071-bundle-066-to-070-code-critic-cleanup/build-log.md
methodology-changelog.md
skills/build-slice/SKILL.md
tests/bugs/test_psq_1_blast_radius_dict_leak.py
tests/methodology/test_branch_workflow_audit.py
tests/methodology/test_methodology_changelog.py
tests/methodology/test_vault_root_constant.py
tests/skills/slice/test_slice_queue_output.py
tools/branch_workflow_audit.py
tools/slice_queue_writer.py
tools/supersede_audit.py
```

(12 files, 1021 insertions / 134 deletions; matches Step 1 union-of-three-sources file list per [[ADR-062]].)

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

None. Per AC#5 must-not-defer "Slice's own /code-review surfaces 0 new structural Majors" — satisfied.

### Minors

#### m1: `_normalize_abs_to_repo_relative` Step 2 lacks `_PATH_SHAPED_RE` validation; only Step 3 fallback validates

- **Claim under review**: `tools/slice_queue_writer.py:300-305` (Step 2 loop in `_normalize_abs_to_repo_relative`)
- **Issue**: Per the 4-step algorithm, Step 2 (`Path(abs).relative_to(candidate_root)`) returns the relative form un-validated; Step 3 explicitly validates via `_PATH_SHAPED_RE.fullmatch(relpath_posix)`. Asymmetric. When `abs_path == candidate_root.resolve()`, Step 2 returns `'.'` (which fails `_is_path_shaped`); when `abs_path` resolves to an immediate child like `<root>/Makefile`, Step 2 returns `'Makefile'` (also fails `_is_path_shaped`). The M3 PRIMARY-filter at `_node_to_path` does catch these downstream, but validation responsibility is split across two layers.
- **Evidence**: `tools/slice_queue_writer.py:300-305` (Step 2 return un-validated) vs L312 (Step 3 validated).
- **Proposed fix**: Wrap the Step 2 return with the same regex validation. Now `_normalize_abs_to_repo_relative` is a single-layer path-validator; M3's PRIMARY filter becomes pure defense-in-depth rather than load-bearing for `'.'`-edge-case suppression.
- **Builder draft disposition**: DEFERRED to slice-072+ bundled cleanup nomination (CRSI-1 v1 walking-skeleton advisory-only + slice-064/065/066/067/068/070 N=6 cumulative voluntary-restraint precedent → N=7 with slice-071). Latent — bounded today by M3 PRIMARY filter defense-in-depth.

#### m2: `candidate_root.resolve()` called per-node inside the per-candidate inner loop

- **Claim under review**: `tools/slice_queue_writer.py:303` `return abs_path.relative_to(candidate_root.resolve()).as_posix()`
- **Issue**: `_build_id_to_path_map` loops over `data.get("nodes", [])` (potentially hundreds of nodes per graph.json). For each node, `_normalize_abs_to_repo_relative` runs Step 2 against `candidate_roots`, calling `.resolve()` on each candidate root per-node. The candidate roots are stable across the whole call — they could be resolved ONCE in `_discover_known_repo_roots` or in `_build_id_to_path_map` BEFORE the for-node loop. Minor perf wart (Path.resolve is a syscall on most platforms); the wider lru_cache absorbs it from caller perspective but first-fill cost scales O(N_nodes × N_candidates).
- **Evidence**: `tools/slice_queue_writer.py:300-303` (per-node loop entry) and `_discover_known_repo_roots` at L248-279 returns un-resolved Path list.
- **Proposed fix**: In `_build_id_to_path_map`, pre-resolve once: `resolved_candidates = [r.resolve() for r in candidate_roots]`, then pass into `_normalize_abs_to_repo_relative` and drop the inline `.resolve()` calls.
- **Builder draft disposition**: DEFERRED to slice-072+ bundled cleanup. Perf wart only; no behavioral impact.

#### m3: ADR-066:82 still carries pre-fix `~631 files` narrative — file-count drift partially un-reconciled

- **Claim under review**: `architecture/decisions/ADR-066-track-vault-in-git.md:82` `slice-069's /commit-slice --merge is the operationally riskiest merge in this repo's history (~11MB / ~631 files / hundreds of insertions per file)`
- **Issue**: design.md L88 scoped slice-069 m1 disposition to `methodology-changelog.md:45` (effective sweep landed at L45 + L61 + L67). ADR-066:82 carries the SAME stale `~631 files` count that triggered the original slice-069 code-Critic m1 cross-artifact drift complaint. The narrative remains internally inconsistent — methodology-changelog v0.70.0 entry says `644 files / 65504 insertions` while ADR-066 §Consequences still says `~631 files`. By-design partial per design.md scoping, but mirrors the same partial-coverage defect class slice-069 code-Critic m1 originally flagged.
- **Evidence**: `architecture/decisions/ADR-066-track-vault-in-git.md:82` empirical grep confirms `~631 files` literal present; methodology-changelog.md:45 + L61 + L67 all say `644 files`.
- **Proposed fix**: (a) extend slice-069 m1 disposition to ADR-066:82 in a follow-up slice with a one-line edit replacing `~631 files / hundreds of insertions per file` → `644 files / 65504 insertions`, OR (b) explicitly document at the build-log.md disposition row that ADR-066:82 is OUT-OF-SCOPE for this slice + nominate a future cleanup.
- **Builder draft disposition**: DEFERRED to slice-072+ bundled cleanup. The partial-coverage was a design-time scoping decision (slice-069 m1 disposition limited to the 3 changelog sites; the ADR-066 §Consequences narrative was non-targeted). Will land in the bundle.

#### m4: `test_audit_result_surfaces_worktree_skip_fields` is structurally near-duplicate of `test_honours_canonical_worktree_skip_rationale_line`

- **Claim under review**: `tests/methodology/test_branch_workflow_audit.py:425-470` `test_audit_result_surfaces_worktree_skip_fields` + L350-422 `test_honours_canonical_worktree_skip_rationale_line`
- **Issue**: Both tests share the same fixture shape: `_init_repo_on_default_branch` + `_add_worktree(... slice/066-...)` + `_make_slice_folder` + write `WORKTREE=skip — rationale: <text>` build-log line + `audit(... repo_root=repo)`. The differentiator is what each asserts: the former checks AuditResult dataclass fields + to_dict surfaces; the latter checks no worktree-* violations fire + APED-1 negative assertion. Minor — not a defect, but factoring out the common fixture into a helper (e.g., `_setup_worktree_with_skip_line(tmp_path, slice_num, slice_name, rationale)`) would reduce ~15 lines of duplication and reduce drift risk between the two.
- **Evidence**: Diff comparison of L380-396 vs L439-450 — both blocks compute `wt_path = tmp_path / "repo-wt" / "slice-066-..."`, both call `_add_worktree`, both write nearly-identical `build-log.md` content.
- **Proposed fix**: Extract `_setup_canonical_worktree_skip_fixture(tmp_path, slice_num, slice_name, rationale)` returning `(repo, wt_path, slice_folder)`. Both tests call it; differ only in assertions.
- **Builder draft disposition**: DEFERRED to slice-072+ bundled cleanup. Cosmetic; drift-risk is real but small (~15 LOC).

#### m5: `main()`'s `out_arg` is passed to `write_slice_queue` un-resolved while `repo_root` is resolved — minor surface inconsistency

- **Claim under review**: `tools/slice_queue_writer.py:803-822` (main()'s out_arg + repo_root handling)
- **Issue**: `repo_root = args.root.resolve()` (L809) is absolute; `out_arg = args.root / out_arg if not out_arg.is_absolute() else out_arg` (L805) does NOT resolve. When a user passes `--root .` + `--output ./elsewhere/queue.md`, `repo_root` becomes the absolute resolved cwd while `out_arg` becomes `./elsewhere/queue.md`. Then `write_slice_queue(out_path=out_arg, ...)` uses `out_arg.parent.mkdir(parents=True, exist_ok=True)` and atomic-write — these work on relative paths, but downstream tracebacks / error messages carry a relative path. Pre-slice-071 main() did `out_arg.resolve()` for the canonical-vs-custom comparison; post-fix, the resolution disappeared. Minor — not a behavioral regression, just asymmetric surface.
- **Evidence**: `tools/slice_queue_writer.py:803-822` post-fix; pre-fix L676-682 used `out_arg.resolve()` for the canonical-out comparison.
- **Proposed fix**: Single-line `out_arg = out_arg.resolve()` after the relative-to-root composition at L805, so `out_arg` and `repo_root` are both absolute when handed off to `write_slice_queue`.
- **Builder draft disposition**: DEFERRED to slice-072+ bundled cleanup. Surface asymmetry only; no behavioral impact.

## Dimensions checked

- [x] **Unfounded assumptions** — none. The `_PATH_SHAPED_RE` regex's negated `[^\s\`]` classes correctly avoid the `]\-` ambiguity that broke the originally-drafted three-alternative regex (per slice-071 /critique B1 ACCEPTED-FIXED + empirical 4+3 parametrized test cases). The drift-prevention test `test_forward_compat_path_keys_docstring_in_sync_with_constant` verifies the docstring↔constant agreement structurally. The m3 sentinel-test's 4 verbatim-aligned substrings (`"Two-marker convention"`, `"argparse help"`, `"intentionally unmarked"`, `"slice-071 design.md §slice-068-m3"`) all match the as-written module docstring at `tests/methodology/test_vault_root_constant.py:16-22`.
- [x] **Missing edge cases** — none structural. The `_normalize_abs_to_repo_relative` 4-step algorithm covers the cases the slice-070 code-Critic M1 evidence identified (sibling-worktree abs paths leaking into the id-path map). The `unknown` sentinel-skip closes the AC#3 false-positive surface. The fallback retry test pins the `--from` branch that was previously unreached. ADR-066:82 file-count stale narrative is flagged as m3 (cosmetic per design scoping).
- [x] **Over-engineering** — none. The 4-step canonical algorithm is appropriately scoped; not speculative. The `_FORWARD_COMPAT_PATH_KEYS` constant is genuinely consumed in 2 places (production code + drift-prevention test) and named for forward extension (slice-072+ graphify schema evolution); not speculative generality.
- [x] **Under-engineering** — none. All 5 ACs map to discharged dispositions per the build-log Phase-by-phase log. AC#5 (pytest ≥950 + shippability ≥70 + 14 audits + /code-review 0 new structural Majors) is satisfied at 966/966 + 70/70 PASS + 22 audits clean + 2 documented defer-with-rationale + this /code-review surfaces 0 Majors.
- [x] **Contract gaps** — none. The `write_slice_queue` signature widening (`out_path: Path | None = None`) is backward-compatible. `MappingProxyType` return type is documented in the `_build_id_to_path_map` docstring AND consumed compatibly via `_node_to_path`'s `id_to_path accepts dict[str, str] OR MappingProxyType` docstring contract. The new `AuditResult.worktree_skip_used` + `_rationale` fields are symmetric with `escape_hatch_*` pair and reach `to_dict()`. The bare `types.MappingProxyType` annotation (vs parameterized `MappingProxyType[str, str]`) is correct — `MappingProxyType` is not generic-subscriptable in Python ≤ 3.12.
- [x] **Security** — none. No new authn/authz paths, no new user-input boundaries. The `subprocess.run` inside `_discover_known_repo_roots` uses fixed argv list (no shell=True, no user-controlled flags). No new secrets / credentials.
- [x] **Drift from vault** — m3 only (ADR-066:82 partial-coverage). The /code-review skill's diff-scope is in-house methodology surfaces; design.md "Components touched" matches the actual diff. MEPD-1 EXCLUDE posture verified (no new `## v0.71.0` entry, no VERSION bump). The retroactive in-place edits to v0.70.0 entry ride the SUP-1 §Append-only-of-DECISIONS-not-of-FACTS carve-out documented at mission-brief.md L42 + L94.
- [x] **Web-known issues** — Skipped — WebSearch unavailable in this session. `types.MappingProxyType` is stable since Python 3.3; `functools.lru_cache` with `cache_clear()` stable since 3.2; `subprocess.run` with `capture_output=True, text=True, encoding="utf-8"` stable since 3.7. No high-risk recent-API usage.
- [x] **Cross-cutting conformance** — none structural. APED-1 conformance empirically verified (the slice-071 m2 fixture rewrite's APED-1 load-bearing negative assertion at `tests/methodology/test_branch_workflow_audit.py:414-422` actually exercises the dependency). RSAD-1 self-application: the slice's own diff survives its own discipline — `_PATH_SHAPED_RE` regex passed the 4+3 parametrized adversarial-battery cases that would have caught the slice-071 /critique B1 broken regex at design time. No EOL-DRIFT-1 byte-equality compares introduced; no phantom-import. The build-log's prose-honesty discipline accurately credits defect provenance per slice-070 reflection lesson.

## Bundling note

All 5 findings (5 minors) deferred to slice-072+ candidate `bundle-071-code-critic-cleanup` (mirrors slice-065 / slice-071 shape). Bundled-cleanup backlog now stands at:
- slice-071 advisories: 5 (this review)
- **Total: 5 findings**

This is a small backlog relative to the slice-070 30-finding cumulative state. Voluntary-restraint discipline holds; the next-slice bundled cleanup remains nominated (slice-072+).

## Builder calibration note

The code-Critic stack delivered another high-signal review (N=8 cumulative slice-063 → slice-071). m1 in particular sharply identifies a real symmetry gap in the 4-step algorithm. m3 is the most consequential — the slice-069 m1 partial-coverage was a design-time scoping decision, but the artifact-internal inconsistency (changelog says 644, ADR-066 still says 631) is the same defect class that originally fired slice-069 m1. The bundling-of-bundling pattern continues: slice-071 (a bundle) ships 5 minors → slice-072 (next bundle) will inherit them.
