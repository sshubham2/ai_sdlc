# Design: Slice 071 bundle-066-to-070-code-critic-cleanup

**Date**: 2026-05-26
**Mode**: Standard
**Risk tier**: medium • Critic required: yes (in-house methodology surfaces touched)

## What's new

- **One new module**: none. Pure cleanup slice.
- **Test additions**: **9 new regression-pin test functions** (per-finding FIX rows below): `test_audit_result_surfaces_worktree_skip_fields` (slice-066 m1), `test_vault_paths_module_is_leaf` (slice-068 M1), `test_two_marker_convention_asymmetry_documented` (slice-068 m3), `test_v_0_70_0_adr_066_entry_present_in_repo` (slice-069 M2), `test_v_0_70_0_adr_066_shippability_consumer_propagation` (slice-069 M2), `test_unknown_cell_is_documented_sentinel_not_an_offender` (slice-070 M5), `test_call_graphify_blast_radius_falls_back_to_from_flag_on_node_not_found` (slice-070 m2), `test_main_cli_custom_output_uses_canonical_write_path` (slice-067 m1), `test_forward_compat_path_keys_docstring_in_sync_with_constant` (slice-070 m5 drift-prevention per /critique-review m-add-1). Plus **~5 modifications of existing tests**: slice-066 m2 fixture rewrite, slice-068 m1 regex expansion, slice-068 m2 assertion tightening, slice-070 M2 SUPPORT test-side cases, slice-070 M5 loop modification, slice-070 m1 autouse fixture (per /critique-review m-add-2 ACCEPTED-FIXED — count corrected from earlier "6 new tests" draft). No new test modules; all rows append to existing `tests/methodology/*` and `tests/skills/slice/*` and `tests/bugs/*` modules.
- **Per-finding disposition table**: this slice's load-bearing artifact (see "Finding disposition" §). Every one of the 31 findings (mission-brief said "~30"; precise hand-count yields 31) carries an explicit **FIX / DEFER-AGAIN / DOCUMENT-AS-DESIGNED / ALREADY-FIXED-AT-/reflect** disposition (per /critique-review m-add-2 ACCEPTED-FIXED — vocab list updated; obsolete `ACKNOWLEDGED-NO-FIX` token removed since slice-069 m6 was relabeled to DEFER-AGAIN per /critique M2 ACCEPTED-FIXED).

## What's reused

- `tools/branch_workflow_audit.py` — slice-066 surface (BRANCH-2 audit) — modified by slice-066 M1/m1/m3 + slice-069 m5 disposition lines
- `skills/build-slice/SKILL.md` — slice-066 M2 + m4 surface
- `skills/commit-slice/SKILL.md` — slice-066 m4 sibling-surface (already had the parenthetical; no edit needed; cited as cross-spec parity reference)
- `tools/slice_queue_writer.py` — slice-067 m1 + slice-070 M1/M2/M3/M4/m4/m5 surfaces (single-file structural concentration; biggest blast cluster in the bundle)
- `tests/methodology/test_branch_workflow_audit.py` — slice-066 m1 + m2 disposition surface (extended + fixture rewrite)
- `tests/methodology/test_vault_root_constant.py` — slice-068 SC-028 (M1 + m1 + m2 + m3) disposition surface
- `tests/bugs/test_psq_1_blast_radius_dict_leak.py` — slice-070 M5 + M6 + m1 + m2 disposition surface
- `tools/_vault_paths.py` — slice-068 M1 leaf-invariant target (existing module; no modification, just import-graph assertion test added)
- `tools/supersede_audit.py` — slice-068 m4 PEP-8 surface
- `methodology-changelog.md` — slice-069 M1 + m1 + m2 + m3 + m5 surfaces (all `## v0.70.0` entry edits; MEPD-1 EXCLUDE posture for this slice itself — only RETROACTIVE corrections to the existing v0.70.0 entry, no NEW entry)
- `architecture/decisions/ADR-066-track-vault-in-git.md` — slice-069 M1 surface (count "9" → "10" at L49 + L59)
- `.gitignore` — slice-069 m4 comment-block consolidation surface
- `tests/methodology/test_methodology_changelog.py` — slice-069 M2 surface (add `test_v_0_70_0_*` paired-pin tests)
- `architecture/shippability.md` — slice-069 M2 partial-discharge confirmation (row #69 already added at slice-069 /reflect Step 5.3; no further action for shippability row; only the paired-pin tests outstanding)
- `tests/skills/slice/test_slice_queue_output.py` — slice-067 m1 CLI test surface (new CLI invocation test exercising the collapsed `main()` branch)

## Components touched

### `tools/branch_workflow_audit.py` (slice-066 surface; existing module modified)

- **Responsibility**: BRANCH-2 worktree/branch audit at `/build-slice` Step 6 pre-finish
- **Lives at**: `tools/branch_workflow_audit.py` (existing; modified)
- **Key interactions**: called from `/build-slice` SKILL.md pre-finish gate; subprocess wraps `git worktree list --porcelain` + `git rev-parse`
- **Modifications this slice**:
  - **slice-066 M1 FIX**: in `_is_repo_root_a_worktree` (currently at L243-277), prepend `if len(gitdir.parts) < 4: return (False, None)` AND `if not (main_repo / ".git").exists(): return (False, None)` guards before the `gitdir.parent.parent.parent` walk — closes the "shallow gitdir walks off filesystem returning unrelated ancestor" surface
  - **slice-066 m1 FIX**: add `worktree_skip_used: bool = False` + `worktree_skip_rationale: str | None = None` fields to `AuditResult` dataclass (currently L100-127); surface in `to_dict()`; assign at L513 (`_check_worktree_skip_line` consumer). Symmetric with existing `escape_hatch_used` / `escape_hatch_rationale` BRANCH=skip surface
  - **slice-066 m3 FIX**: hoist `import os` from inside `_paths_equivalent` (currently L298) to module-level imports block
  - **slice-069 m5 FIX**: add `--detach HEAD` sub-case to module-level docstring documenting the slice-069 H4 N=4 verification pattern — "for in-place collision-avoidance verification, use `git worktree add --detach ../<verify-path> HEAD` when the slice branch is already checked out elsewhere"

### `skills/build-slice/SKILL.md` (slice-066 surface; existing skill modified)

- **Responsibility**: build phase skill prose; Claude reads + executes
- **Lives at**: `skills/build-slice/SKILL.md`
- **Modifications this slice**:
  - **slice-066 M2 FIX**: replace `wt_base="$(dirname "$(pwd)")/$(basename "$(pwd)")-wt"` at L55-60 with `repo_root="$(git rev-parse --show-toplevel)"` + `wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"`. Computes canonical wt_base from `.git`-ancestor walk (matches `_resolve_expected_worktree_path` derivation in `tools/branch_workflow_audit.py:280-287`) rather than cwd-derived. Closes the "user runs /build-slice from a subdirectory → audit-vs-actual-worktree path divergence" surface
  - **slice-066 m4 FIX**: append `(POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash — same dependency convention as commit-slice Step 5b/5d)` parenthetical to the bash-snippet at L56. RPCD-1 cross-spec parity with `skills/commit-slice/SKILL.md` (which already carries the parenthetical per slice-066 critique-review M-add-3)
- **OSDG-1 forward-sync obligation**: every edit MUST be mirror-applied to `~/.claude/skills/build-slice/SKILL.md` to preserve content-equality modulo line endings (CAD-1/OSDG-1 discipline; gated by `tests/methodology/test_build_slice_skill_drift.py`)

### `tools/slice_queue_writer.py` (slice-067 + slice-070 surface; biggest blast cluster)

- **Responsibility**: PSQ-1 writer of `architecture/slice-queue.md`; library API + CLI
- **Lives at**: `tools/slice_queue_writer.py`
- **Modifications this slice**:
  - **slice-067 m1 FIX**: refactor `write_slice_queue` to accept optional `out_path: Path | None = None` kwarg (default behavior preserved when None); collapse `main()`'s duplicated 38-line custom-output branch (currently L592-629) into single `write_slice_queue(out_path=out_arg, ...)` call. Eliminates Fowler "Duplicated Code" smell + makes CLI's `--output <custom>` path testable via existing `blast_resolver` injection seam. Forward-compat: when slice-072+ PSQ-2 extends entry shape, single update point
  - **slice-070 M1 FIX**: in `_build_id_to_path_map` (currently L257-261), when `.relative_to(repo_root)` raises, normalize the absolute path via a 4-step canonical algorithm (per /critique M3 ACCEPTED-FIXED — algorithm enumerated explicitly so /build-slice has no design-time decisions to make):
    1. **Discover known repo roots**: run `git -C <repo_root> worktree list --porcelain` via `subprocess.run`; parse output; collect the `worktree <path>` lines as candidate roots. First entry is main-tree; subsequent entries are sibling worktrees (per BRANCH-2 convention, located at `<main-parent>/<main-name>-wt/slice-NNN-*`).
    2. **For each candidate root**, attempt `Path(abs_path_str).relative_to(candidate_root)`; first one that succeeds is the canonical relative form (return `.as_posix()`).
    3. **If no candidate succeeds**, fall back to `os.path.relpath(abs_path_str, repo_root)` and accept the (possibly `..`-prefixed) form ONLY IF `_PATH_SHAPED_RE.fullmatch(result)` validates (gates on B1 fix landing first — the new `_PATH_SHAPED_RE` is the test-side regex that correctly rejects `unknown`/`Makefile`).
    4. **If neither path succeeds** (no candidate root resolves AND `_PATH_SHAPED_RE` rejects the `os.path.relpath` result), **DROP** the entry by returning `None` from the helper; caller skips the node (preserves the existing `if val is None: continue` semantic in `_node_to_path`'s callers).
    Closes latent abs/rel-form duplication surface that today's `architecture/slice-queue.md` cells exhibit at 6/10 candidates (per slice-070 code-review M1 evidence)
  - **slice-070 M2 FIX**: extract module-level constant `_PATH_SHAPED_RE` using the **existing test-side regex verbatim** from `tests/bugs/test_psq_1_blast_radius_dict_leak.py:291-295` — `r"^(?:[^\s`]*[/\\][^\s`]+|[^\s`]*\.[A-Za-z0-9]{1,8}|\.[A-Za-z][A-Za-z0-9_.-]*)$"`. (Per /critique B1 ACCEPTED-FIXED: the originally-drafted three-alternative regex was empirically broken — `[/\\]` parses as `[/\]` terminating the character class early, yielding `_PATH_SHAPED_RE.fullmatch("unknown") → True`. The test-side regex at L291-295 uses negated `[^\s\`]` classes which avoid the ambiguity entirely AND is already empirically verified by the surrounding tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py`.) Replace `_is_path_shaped`'s case-sensitive `endswith((".py", ".md", ".json", ".toml", ".yaml", ".txt"))` (currently L212-222) with `_PATH_SHAPED_RE.fullmatch(token) is not None`. **Test-side imports the constant from `tools.slice_queue_writer`** rather than re-defining it locally (single-source-of-truth seam — the literal regex string moves OUT of the test file and INTO the production module). The existing test-side definition at L291-295 is REPLACED with `from tools.slice_queue_writer import _PATH_SHAPED_RE as _PATH_SHAPED_TOKEN_RE` (alias preserved for surrounding-test backward-compat). Add 4 unit cases pinning `.gitignore`, `.env`, `file.HTML`, `file.cfg` accepted AND 3 negative cases pinning `unknown`, `Makefile`, `abc` REJECTED (APED-1 conformance — the negative cases would have caught B1 at design time)
  - **slice-070 M3 FIX**: at `_node_to_path` PRIMARY map-lookup branch (currently L290-292), wrap return: `val = id_to_path[nid]; if _is_path_shaped(val): return val; else: # fall through to forward-compat`. Defense-in-depth consistency with the existing forward-compat branch filter (L294-297)
  - **slice-070 M4 FIX**: wrap `_build_id_to_path_map`'s return value with `types.MappingProxyType(out)` — read-only view; future mutating callers raise `TypeError`. Closes lru_cache shared-mutable foot-gun
  - **slice-070 m4 FIX**: move `id_to_path = _build_id_to_path_map(...)` build site from function-entry (currently L318) to just-before-the-comprehensions (after JSON parse succeeds). Minor perf wart; skip wasted-work on subprocess-failure paths
  - **slice-070 m5 FIX**: extract `_FORWARD_COMPAT_PATH_KEYS: tuple[str, ...] = ("path", "source_file", "name")` module-level constant; reference in docstring + use in `_node_to_path` forward-compat branch (currently L294 magic tuple). **Drift-prevention test (per /critique m4 ACCEPTED-PENDING + /critique-review m-add-1 ACCEPTED-FIXED — promise inscribed in design.md, not just deferred to /build-slice)**: add `test_forward_compat_path_keys_docstring_in_sync_with_constant` to `tests/bugs/test_psq_1_blast_radius_dict_leak.py` that (a) imports `_FORWARD_COMPAT_PATH_KEYS` from `tools.slice_queue_writer`, (b) reads `tools.slice_queue_writer._node_to_path.__doc__` (or module docstring containing the enumeration), (c) extracts the enumeration tokens via simple substring scan, (d) asserts the docstring lists keys in the SAME order as the constant. Closes slice-070 code-review m5 "magic tuple — easy to silently drift from docstring" with a structural pin, not just an extracted constant

### `tools/_vault_paths.py` (slice-068 M1 surface)

- **Responsibility**: VAULT_ROOT constant module (per slice-068 ADR-065)
- **Lives at**: `tools/_vault_paths.py` (existing; NO modification this slice)
- **Modifications this slice**: none. The slice-068 M1 fix is a NEW test (`test_vault_paths_module_is_leaf`) that AST-walks `tools/_vault_paths.py` asserting stdlib-only imports. The module itself is already compliant; the test is the missing regression-pin design.md L25 + mission-brief.md L54 promised

### `tools/supersede_audit.py` (slice-068 m4 surface)

- **Responsibility**: SUP-1 supersede audit
- **Modifications this slice**: insert PEP-8 blank line between L53 `from pathlib import Path` and L54 `from tools import _stdout`. Trivial cosmetic; aligns with sibling files

### `methodology-changelog.md` (slice-069 surface; RETROACTIVE corrections only)

- **Responsibility**: append-only methodology change log
- **MEPD-1 posture for this slice**: EXCLUDE (no NEW v0.71.0 entry; this slice is cleanup-only per voluntary-restraint discipline N=12 cumulative)
- **Modifications this slice**:
  - **slice-069 M1 FIX**: replace `9 production patterns` → `10 production patterns` at L45 (and any other count mention in the `## v0.70.0` entry)
  - **slice-069 m1 FIX**: reconcile vault file-count drift in v0.70.0 entry — set canonical value to `644 files / 65504 insertions` from build-log Phase H2 `git diff --cached --stat` empirical evidence (replaces "~633 files" prose at L45)
  - **slice-069 m2 FIX**: reconcile PII redaction count narrative in v0.70.0 entry — replace "113 unique absolute paths, 9 GitHub-handle refs, 1 private-project-name leak" at L66 with "build-log Phase C empirical: 36 files / 141 substitutions (136 home-path + 5 standalone-project)" matching build-log evidence
  - **slice-069 m3 FIX** (judgment call: FIX as cheap-and-coherent; improves grep-anchorability per code-Critic disposition; per /critique m3 ACCEPTED-FIXED, time estimate softened from "20-min job" to "small-but-not-trivial prose restructure (30-60 min depending on forward-reference preservation cost)"): split the 600-word first paragraph of the `## v0.70.0` entry into one headline sentence + 3 sub-bullets in the existing `**Primary deliverables**` section. Sub-items: vault-in-git philosophy mint (ADR-066) / BC-PROJ-8 rule-content supersession / STP-1 docstring reframing / M5 INCLUDE direction. **Preserve existing forward-references + downstream-audit grep anchors** (verify pre-edit via grep-cite of paragraph contents from `tests/methodology/test_methodology_changelog.py` + `tools/build_checks_audit.py` keyword classifiers)
  - **CAD-1 / OSDG-1 forward-sync obligation**: `~/.claude/methodology-changelog.md` must mirror these edits (MCFS-1 discipline)

### `architecture/decisions/ADR-066-track-vault-in-git.md` (slice-069 surface)

- **Responsibility**: vault-in-git philosophy ADR
- **Modifications this slice**:
  - **slice-069 M1 FIX**: replace `9 production patterns` → `10 production patterns` at L49 AND `9 VAL-1 patterns` → `10 VAL-1 patterns` at L59. Append-only ADR convention: TEXT corrections are permitted (not supersessions; just count fact)

### `.gitignore` (slice-069 m4 surface)

- **Modifications this slice**: consolidate the two comment blocks (L10-13 forward-reference + L15 `# Build artifacts` header). Drop the forward-reference clause "remain ignored below" at L13 — the L15 header is self-documenting. Pure readability cleanup

### `architecture/shippability.md` (slice-069 M2 partial-discharge confirmation)

- **Modifications this slice**: none required for shippability row #69 (already added at slice-069 /reflect Step 5.3 per the slice-069 reflection narrative). The slice-071 M2 disposition row in build-log.md MUST cite this prior partial-discharge

### `tests/methodology/test_methodology_changelog.py` (slice-069 M2 paired-pin completion)

- **Modifications this slice**:
  - **slice-069 M2 FIX (paired-pin completion)**: append two new tests `test_v_0_70_0_adr_066_entry_present_in_repo` + `test_v_0_70_0_adr_066_shippability_consumer_propagation` modeled on the existing v0.69.0 paired-pin pair (currently at L4305-4681 area). Closes BC-PROJ-10 paired-pin obligation that slice-069's MEPD-1 INCLUDE posture triggered

### `tests/methodology/test_branch_workflow_audit.py` (slice-066 m2 fixture rewrite + m1 surface coverage)

- **Modifications this slice**:
  - **slice-066 m2 FIX**: rewrite `test_honours_canonical_worktree_skip_rationale_line` fixture — create a worktree elsewhere with the slice branch (mirroring `test_rejects_main_tree_cwd_when_worktree_registered_elsewhere`), add the WORKTREE=skip line, assert clean. Empirically remove-the-skip-line → assert audit FAILS (i.e., the test is now actually load-bearing — APED-1 conformance)
  - **slice-066 m1 SUPPORT**: add `test_audit_result_surfaces_worktree_skip_fields` asserting `AuditResult.worktree_skip_used` + `worktree_skip_rationale` reach `to_dict()` output (regression-pin for the new fields)

### `tests/methodology/test_vault_root_constant.py` (slice-068 SC-028 bundle)

- **Modifications this slice**:
  - **slice-068 M1 FIX**: add `test_vault_paths_module_is_leaf` asserting `tools/_vault_paths.py`'s import-set is stdlib-only via AST walk (parse source, walk `ast.Import` + `ast.ImportFrom`, assert no node's `module` startswith `"tools."` — only stdlib roots like `"pathlib"`, `"os"`, plus `__future__`). Update `test_full_pytest_baseline_preserved` test-function count from 10 to 11
  - **slice-068 m1 FIX**: expand `test_migration_is_idempotent` (currently L178-198) regex from `r'Path\(["\']architecture["\']\)'` (catches 1 of 4 shapes) to a 4-alternative pattern covering: `Path("architecture")`, `Path("architecture/<sub>")`, bare `"architecture/<sub>"` string literals, `repo_root / "architecture" / "<sub>"` shapes. Re-runs the substitution + idempotency assertions empirically
  - **slice-068 m2 FIX**: tighten `test_consumer_constants_are_frozen_at_first_import` (currently L256-290) with two-step assertion — first assert `tools._vault_paths.VAULT_ROOT == Path("/tmp/freeze-pin-test")` after monkeypatch (proves monkeypatch took effect); then assert `tools.slice_queue_writer._INDEX_MD_REL` does NOT equal the patched VAULT_ROOT-derived path (proves consumer's frozen constant did not propagate); third assert the consumer's frozen value is the canonical Path("architecture")-derived form (proves the freeze captured the pre-patch state)
  - **slice-068 m3 DOCUMENT-AS-DESIGNED (judgment: option (a) over (b) per code-Critic m3 proposed fix; sentinel-test shape per /critique M6 ACCEPTED-FIXED; assertion↔docstring verbatim alignment per /critique-review M-add-1 ACCEPTED-FIXED)**: accept the two-marker convention asymmetry; add a new test `test_two_marker_convention_asymmetry_documented` that asserts **prose-level descriptor substrings** exist in the test module's `__doc__` — assertions VERBATIM-MATCHED to the docstring prose: `assert "Two-marker convention" in __doc__` (capital T matches docstring), `assert "argparse help" in __doc__`, `assert "intentionally unmarked" in __doc__`, `assert "slice-071 design.md §slice-068-m3" in __doc__` (full anchor matches docstring's `§slice-068-m3`, NOT bare `§m3`). **NO regex literal in any assertion string** (avoids the triple-escape Windows-path-separator hellscape Critic flagged at M6). The module-level docstring carries the actual prose VERBATIM: `"Two-marker convention applies only to lines matched by ``literal_re`` at L118 of this module; substring-in-prose sites at argparse help / error messages / log strings are intentionally unmarked per slice-071 design.md §slice-068-m3 disposition."`. **APED-1 conformance obligation**: at /build-slice Phase B-of-this-finding, run `python -c 'doc = "<verbatim docstring>"; assert "Two-marker convention" in doc; assert "slice-071 design.md §slice-068-m3" in doc; ...'` BEFORE committing — verifies the assertion↔docstring agreement empirically (/critique-review M-add-1 demonstrated that the pre-fix assertion strings did NOT match the proposed docstring; 2/4 assertions would have failed silently — RSAD-1 instance avoided by this alignment fix).

### `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (slice-070 surface)

- **Modifications this slice**:
  - **slice-070 M2 SUPPORT**: import the new module-level `_PATH_SHAPED_RE` from `tools.slice_queue_writer`; replace test-side `_PATH_SHAPED_TOKEN_RE` local definition with the imported constant. Add 4 new test cases asserting `.gitignore`, `.env`, `file.HTML`, `file.cfg` are accepted by both `_is_path_shaped(token)` AND `_PATH_SHAPED_RE.fullmatch(token)`. Single-source-of-truth pin
  - **slice-070 M5 FIX**: at the AC#3 token-extraction test loop (currently around L340), skip `unknown` as a documented sentinel (`if token == "unknown": continue`). Add a unit test `test_unknown_cell_is_documented_sentinel_not_an_offender` pinning the skip. Closes false-positive surface on routine degraded states
  - **slice-070 M6 FIX**: replace all 5 occurrences of `patch.object(subprocess, "run", ...)` (at L98, L143, L177, L227, L263) with `patch("tools.slice_queue_writer.subprocess.run", ...)` for SUT-bound test isolation
  - **slice-070 m1 FIX**: add autouse fixture at module top calling `_build_id_to_path_map.cache_clear()` before each test — prevents cross-test state leak via lru_cache
  - **slice-070 m2 FIX**: add new test `test_call_graphify_blast_radius_falls_back_to_from_flag_on_node_not_found` where `_fake_run` returns `returncode=2` on first call (`--file <basename>`) and the real shape on the second (`--from=<basename>`). Pins the currently-dead fallback retry branch at L323
  - **slice-070 m5 SUPPORT (drift-prevention test per /critique-review m-add-1 ACCEPTED-FIXED)**: add `test_forward_compat_path_keys_docstring_in_sync_with_constant` (see slice-070 m5 FIX in `tools/slice_queue_writer.py` §Components touched for full spec)

### `tests/skills/slice/test_slice_queue_output.py` (slice-067 m1 CLI test surface)

- **Modifications this slice**:
  - **slice-067 m1 SUPPORT**: add new test `test_main_cli_custom_output_uses_canonical_write_path` exercising `main()`'s now-collapsed `--output <custom>` branch via the `blast_resolver` injection seam. Asserts that the rendered queue file at the custom path matches the canonical form byte-for-byte (modulo path) — pins the slice-067 m1 refactor

## Finding disposition

This is the load-bearing artifact. Every one of the 31 findings has an explicit per-finding row in this table; `/build-slice` Phase A will replicate this table verbatim into `build-log.md` Events § as the disposition log per AC#1-#4 verification grep contracts.

### slice-066 (6 findings)

| Finding | Disposition | Specific approach (1-line) |
|---------|-------------|----------------------------|
| slice-066 M1 | **FIX** | Add gitdir depth + `.git`-existence guards in `_is_repo_root_a_worktree` (`tools/branch_workflow_audit.py:243`) |
| slice-066 M2 | **FIX** | Rewrite `wt_base` derivation via `git rev-parse --show-toplevel` (`skills/build-slice/SKILL.md:55-60`) |
| slice-066 m1 | **FIX** | Surface `worktree_skip_used` + `_rationale` in `AuditResult` (`tools/branch_workflow_audit.py:100-127`) |
| slice-066 m2 | **FIX** | Rewrite `test_honours_canonical_worktree_skip_rationale_line` fixture to actually exercise dependency (`tests/methodology/test_branch_workflow_audit.py:351-388`) |
| slice-066 m3 | **FIX** | Hoist `import os` to module-level (`tools/branch_workflow_audit.py:298`) |
| slice-066 m4 | **FIX** | Add PowerShell-portability parenthetical at `skills/build-slice/SKILL.md:56` end-of-snippet |

### slice-067 (1 finding)

| Finding | Disposition | Specific approach (1-line) |
|---------|-------------|----------------------------|
| slice-067 m1 | **FIX** | Add `out_path: Path \| None = None` kwarg to `write_slice_queue`; collapse `main()` custom-output branch to single call (`tools/slice_queue_writer.py:455, 592-629`) |

### slice-068 (5 findings)

| Finding | Disposition | Specific approach (1-line) |
|---------|-------------|----------------------------|
| slice-068 M1 | **FIX** | Add `test_vault_paths_module_is_leaf` AST-walk test pinning stdlib-only imports (`tests/methodology/test_vault_root_constant.py` new function) |
| slice-068 m1 | **FIX** | Expand idempotency regex to 4-shape coverage (`tests/methodology/test_vault_root_constant.py:178-198`) |
| slice-068 m2 | **FIX** | Tighten freeze-pin assertion to two-step verification (`tests/methodology/test_vault_root_constant.py:256-290`) |
| slice-068 m3 | **DOCUMENT-AS-DESIGNED** | Accept two-marker convention asymmetry; add `test_two_marker_convention_asymmetry_documented` sentinel-test per code-Critic option (a) |
| slice-068 m4 | **FIX** | Insert PEP-8 blank line at `tools/supersede_audit.py:53-54` |

### slice-069 (8 findings)

| Finding | Disposition | Specific approach (1-line) |
|---------|-------------|----------------------------|
| slice-069 M1 | **FIX** | Replace `9 patterns` → `10 patterns` in `methodology-changelog.md:45` + `ADR-066-track-vault-in-git.md:49,59`. **Out of scope**: `slice-069 mission-brief.md` is archived (immutable per slice convention) — no edit |
| slice-069 M2 | **FIX (paired-pin completion)** | Add `test_v_0_70_0_adr_066_entry_present_in_repo` + `_shippability_consumer_propagation` in `tests/methodology/test_methodology_changelog.py`. **Already partially discharged at slice-069 /reflect Step 5.3**: shippability row #69 added — no further work on row |
| slice-069 m1 | **FIX** | Reconcile vault file count to canonical `644 files / 65504 insertions` in `methodology-changelog.md:45` |
| slice-069 m2 | **FIX** | Reconcile PII redaction narrative to `36 files / 141 substitutions` (build-log Phase C empirical) in `methodology-changelog.md:66` |
| slice-069 m3 | **FIX** | Split 600-word first paragraph of `## v0.70.0` entry into headline + 3 sub-bullets in **Primary deliverables** section |
| slice-069 m4 | **FIX** | Consolidate `.gitignore` comment blocks at L10-13 + L15 (drop forward-reference clause) |
| slice-069 m5 | **FIX** | Document `--detach HEAD` sub-case in `tools/branch_workflow_audit.py` module-level docstring |
| slice-069 m6 | **DEFER-AGAIN** | BC-1 BC-GLOBAL-2 false-positive class is structurally addressed at /critic-calibrate scope (negative-anchor filtering of prose-discussion vs code-automation), NOT via a single-slice fix. **Lands-in-slice-NNN+**: /critic-calibrate periodic-run candidate; promote to a dedicated BC-1-discrimination slice if pattern recurs at N=3 cumulative. Per /critique M2 ACCEPTED-FIXED: relabeled from initial-draft ACKNOWLEDGED-NO-FIX to DEFER-AGAIN per Critic's prose-honesty observation — the substantive class is not closed by this slice, only acknowledged. Reflection.md §Deferred MUST carry this nomination per mission-brief Must-not-defer #3 |

### slice-070 (11 findings)

| Finding | Disposition | Specific approach (1-line) |
|---------|-------------|----------------------------|
| slice-070 M1 | **FIX** | Harden `_build_id_to_path_map` `.relative_to()` fallback with prefix-stripping retry + `os.path.relpath` + `_PATH_SHAPED_RE` validation (`tools/slice_queue_writer.py:257-261`) |
| slice-070 M2 | **FIX** | Extract module-level `_PATH_SHAPED_RE` constant; replace `_is_path_shaped` `endswith` tuple with regex match; test-side imports the constant (`tools/slice_queue_writer.py:212-222`) |
| slice-070 M3 | **FIX** | Wrap PRIMARY map-lookup return with `_is_path_shaped` filter at `_node_to_path` L290-292 |
| slice-070 M4 | **FIX** | Wrap `_build_id_to_path_map` return with `types.MappingProxyType` (`tools/slice_queue_writer.py:225-262`) |
| slice-070 M5 | **FIX** | Skip `unknown` sentinel in AC#3 token-extraction test loop + add unit test `test_unknown_cell_is_documented_sentinel_not_an_offender` (`tests/bugs/test_psq_1_blast_radius_dict_leak.py:340`) |
| slice-070 M6 | **FIX** | Replace 5 `patch.object(subprocess, "run", ...)` with `patch("tools.slice_queue_writer.subprocess.run", ...)` (`tests/bugs/test_psq_1_blast_radius_dict_leak.py:98,143,177,227,263`) |
| slice-070 m1 | **FIX** | Add autouse `cache_clear()` fixture (`tests/bugs/test_psq_1_blast_radius_dict_leak.py` module top) |
| slice-070 m2 | **FIX** | Add `test_call_graphify_blast_radius_falls_back_to_from_flag_on_node_not_found` exercising `--from` retry branch (`tests/bugs/test_psq_1_blast_radius_dict_leak.py` new function) |
| slice-070 m3 | **ALREADY-FIXED-AT-/reflect** | Build-log honesty correction was applied at slice-070 /reflect; no work this slice (re-confirmation row only) |
| slice-070 m4 | **FIX** | Move `id_to_path` build from function-entry to just-before-comprehensions (`tools/slice_queue_writer.py:318`) |
| slice-070 m5 | **FIX** | Extract `_FORWARD_COMPAT_PATH_KEYS = ("path", "source_file", "name")` module-level constant; reference in docstring + `_node_to_path` (`tools/slice_queue_writer.py:273-275, 294`) |

**Disposition totals**: FIX = 28 • DOCUMENT-AS-DESIGNED = 1 (slice-068 m3) • ALREADY-FIXED-AT-/reflect = 1 (slice-070 m3) • **DEFER-AGAIN = 1** (slice-069 m6)

The user's `/slice` Step 3 full-bundle choice (over the recommended split-options A/B/C) read as "burn down the backlog this slice". 28/31 findings receive substantive FIX dispositions; 1 (slice-068 m3) closes via a DOCUMENT-AS-DESIGNED sentinel-test that genuinely pins the documented asymmetry; 1 (slice-070 m3) was already closed at slice-070 /reflect; **1 (slice-069 m6) honestly carries DEFER-AGAIN** — the BC-1 BC-GLOBAL-2 false-positive class is structurally a /critic-calibrate proposal, not a single-slice fix surface (per /critique M2 ACCEPTED-FIXED — the Critic flagged the prose-honesty risk of renaming DEFER-AGAIN to ACKNOWLEDGED-NO-FIX as an RSAD-1 anti-pattern that would propagate to future bundled-cleanup slices). The 1 DEFER-AGAIN is reflection-tracked at /reflect §Deferred per mission-brief Must-not-defer #3.

## Contracts added or changed

None. This slice introduces no new endpoints, events, schemas, or public APIs. The 28 FIX dispositions are internal hardening (test additions + audit-tool guards + skill-prose corrections + changelog-entry edits + comment-block consolidations + constant extractions). The `write_slice_queue(out_path=...)` kwarg addition (slice-067 m1) is a backward-compatible signature widening (existing single-arg callers unaffected; default value `None` preserves canonical behavior).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). This slice introduces **zero new modules**. All edits modify existing modules listed under "Components touched" above. Per WIRE-1 audit semantics, a zero-row matrix is treated as clean (audit returns 0 violations). Header preserved below for audit-tool parse-compliance:

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

(No rows — no new modules introduced.)

## Decisions made (ADRs)

**None.** This slice mints no new ADRs. Per **MEPD-1 EXCLUDE posture** for cleanup-only slices (voluntary-restraint discipline N=12 cumulative; slice-065 / slice-067 / slice-070 cleanup-slice precedent), no new ADR fires + no `## v0.71.0` methodology-changelog entry + no PMI-1 atomic version bump.

The retroactive corrections to ADR-066 (slice-069 M1 count "9" → "10") are TEXT corrections to a fact-claim, NOT ADR supersessions per SUP-1. ADR remain logically append-only (no `supersedes:` chain mutation); count-fact in body text is patched in-place per the append-only-of-DECISIONS-not-of-FACTS interpretation that ADR-019 §"Append-only discipline scope" implicitly anchors.

## Authorization model for this slice

N/A. No authn/authz surfaces touched. Cleanup-only slice on methodology-internal tooling + skill prose + changelog/ADR text + test additions.

## Error model for this slice

N/A. No new error paths added; the 4 audit-guard FIX rows (slice-066 M1 + slice-070 M1 + slice-070 M3 + slice-066 m1 surface) tighten existing error-shape returns (return `(False, None)` on guard failure / drop unfiltered values / surface skip-rationale field) — no new exception classes, no new sys.exit codes, no new CLI return surface.

## Risk-tier note + Critic-required determination

- **Risk tier**: medium (cross-cutting cleanup; not novel-domain; not first-time-integration)
- **Critic required**: **yes** (in-house methodology surfaces touched: `tools/branch_workflow_audit.py`, `tools/slice_queue_writer.py`, `skills/build-slice/SKILL.md`, `methodology-changelog.md`, `ADR-066`. CLAUDE.md "Always mandatory Critic — In-house methodology surfaces" trigger fires regardless of tier; voluntary-Critic-on-cross-cutting-tooling-slices track record consistently positive across the recent slice window per `_index.md` Aggregated lessons further reinforces — per /critique m2 ACCEPTED-FIXED, the specific count claim "N=9/9" was unverified vs aggregated-lessons N=7 and is replaced with the qualitative "consistently positive" formulation)

## Test-first / walking-skeleton / exploratory-charter postures

- **Test-first** = false (mixed-disposition cleanup; ACs map to per-finding disposition-discharge, not to single-test-per-AC shape; TF-1 audit opt-out per opt-in/default-off TFFL-1 discipline — TF-1 returns trivially clean when test-first=false, not "missing audit" / not "13 of 14"). The 11 regression-pin tests added across the slice are written alongside their paired source-side FIXes (per /critique M5 ACCEPTED-FIXED — the original Phase B1 "RED-first" framing was test-first-by-other-name and is removed; tests-paired-with-FIXes is the consistent posture)
- **Walking-skeleton** = false (not minting a new vertical)
- **Exploratory-charter** = false (no new behavior surface; cleanup of known findings)

## Build-phase order strategy

`/build-slice` Phase B (implementation) executes per-cluster, where each cluster's source-side FIX + its paired regression-pin test land in the SAME commit (per /critique M5 + /critique-review M-add-2 ACCEPTED-FIXED — restructured from earlier "tests first, then source" two-pass ordering to true per-cluster paired discipline; eliminates the test-first-by-other-name RSAD-1 framing the meta-Critic flagged):

1. **Phase B1: `tools/slice_queue_writer.py` cluster** (slice-067 m1 + slice-070 M1 + M2 + M3 + M4 + m4 + m5). Biggest single-file concentration. Each finding lands as one paired-commit: source-side FIX + its regression-pin test (where applicable) co-committed. For slice-067 m1: refactor + new `test_main_cli_custom_output_uses_canonical_write_path` (in `tests/skills/slice/test_slice_queue_output.py`) together. For slice-070 M1 (4-step algorithm) + M2 (regex extraction) + M3 (PRIMARY filter) + M4 (MappingProxyType) + m4 (eager-build move) + m5 (FORWARD_COMPAT_PATH_KEYS constant): each source edit co-committed with its `tests/bugs/test_psq_1_blast_radius_dict_leak.py` test additions (4 positive + 3 negative for M2; M5 sentinel-skip + `test_unknown_cell_is_documented_sentinel_not_an_offender`; M6 subprocess-patch scope fix; m1 autouse fixture; m2 fallback retry test; per /critique-review m-add-1 ACCEPTED-FIXED, slice-070 m5 also lands `test_forward_compat_path_keys_docstring_in_sync_with_constant`).
2. **Phase B2: `tools/branch_workflow_audit.py` cluster** (slice-066 M1 + m1 + m3 + slice-069 m5). Per-finding paired: M1 gitdir guards + (existing `test_is_repo_root_a_worktree` coverage extension); m1 AuditResult fields + new `test_audit_result_surfaces_worktree_skip_fields`; m3 `import os` hoist (no test — cosmetic); slice-069 m5 docstring update (no test — documentation).
3. **Phase B3: `skills/build-slice/SKILL.md` cluster** (slice-066 M2 + m4) + **OSDG-1 forward-sync** to `~/.claude/skills/build-slice/SKILL.md` co-committed (no time gap between in-repo edit + installed-copy mirror — closes the CAD-1/OSDG-1 drift window).
4. **Phase B4: `tests/methodology/test_vault_root_constant.py` cluster (slice-068 SC-028 bundle)** + slice-068 m4 PEP-8 on `tools/supersede_audit.py`. Per-finding paired: slice-068 M1 leaf-invariant new test (source `tools/_vault_paths.py` unchanged — test-only); m1 idempotency regex expansion (test-only); m2 freeze-pin two-step assertion (test-only); m3 sentinel-test for two-marker asymmetry (test + docstring co-committed; verify assertion↔docstring agreement empirically per M-add-1 ACCEPTED-FIXED). slice-066 m2 fixture rewrite on `tests/methodology/test_branch_workflow_audit.py` lands here too (sibling test-only finding). slice-068 m4 PEP-8 is cosmetic source-only (no test).
5. **Phase B5: `tests/methodology/test_branch_workflow_audit.py` slice-066 m2 fixture rewrite** (if not already landed in B4 — it sibling-pairs naturally with B4's test focus).
6. **Phase B6: methodology-changelog.md + ADR-066 + .gitignore cluster** (slice-069 M1 + m1 + m2 + m3 + m4 + ADR-066 M1) + **MCFS-1 forward-sync** to `~/.claude/methodology-changelog.md` co-committed. All `## v0.70.0` entry edits land atomically; ADR-066 L49/L59 count fixes co-committed; `.gitignore` L10-13 + L15 comment-block consolidation as a separate small commit.
7. **Phase B7: slice-069 M2 paired-pin tests** (`tests/methodology/test_methodology_changelog.py`). After this, all `test_v_0_70_0_*` paired-pin obligations from slice-069 INCLUDE posture are discharged.
8. **Phase E mid-slice smoke gate** (per mission-brief): full pytest + shippability runner after Phases B1-B4 complete (covers slice-066/067/068/070 dispositions). Catches first-half regressions before tackling Phase B6's bulk methodology-changelog edits.
9. **Phase F /code-review** for this slice itself: must surface 0 new structural Majors (cosmetic minors permitted per CRSI-1 v1 walking-skeleton).
10. **Phase G all 14 Step-6 audits** clean (CAD-1, OSDG-1, PMI-1, etc.).

## Forward-sync obligations (CAD-1 / OSDG-1 / MCFS-1 lineage)

Per the existing CAD-1 / OSDG-1 / MCFS-1 forward-sync discipline:
- Each `skills/build-slice/SKILL.md` edit MUST be mirrored to `~/.claude/skills/build-slice/SKILL.md` byte-for-byte modulo EOL (per ADR-033 / EOL-DRIFT-1; OSDG-1 audit gates at `tests/methodology/test_build_slice_skill_drift.py`)
- Each `methodology-changelog.md` edit MUST be mirrored to `~/.claude/methodology-changelog.md` (MCFS-1)
- Each `tools/*.py` edit lands at first import + auto-applies to subsequent shippability-runner invocations (no copy needed for source modules; the audits import from the repo via `$PY -m tools.<name>`)

## Out-of-scope confirmations

(Cited from mission-brief.md §Out of scope; restated here as design-time non-goals to prevent in-build scope creep):

- No new methodology rules; no ADR mints; no VERSION bump; no `## v0.71.0` changelog entry
- No wide refactors beyond the enumerated 31 findings
- No WS-1 / ETC-1 TFFL-1 R-7-class extension (still-pending /critic-calibrate proposal; not this slice)
- No PSQ-2 / PSQ-3 / `rename-architecture-to-sdlc` work (slice-072+ nominees)
- No SC-006 / SC-007 / SC-008 documented-but-unenforced-gate cluster work (slice-072+ `implement-or-downgrade-drift-check` nominee)
- No new audit, no new skill, no new tool
- Archived slice mission-briefs/design.mds are immutable — no edits to past slice folders even where slice-069 M1 names `mission-brief.md:19,34` as a count-drift surface
