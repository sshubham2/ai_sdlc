# Slice 076: bundle-074-code-critic-cleanup

**Mode**: Standard
**Estimated work**: ~2 hours (bounded cleanup; slice-074 code-review L109 estimate ~1-2 hrs)
**Risk retired**: P1.1 (build-slice point-4 variable-scope footgun — fresh-shell unbound `$wt_base`/`$repo_root`/`$default`); P3.10 (cp1252 mojibake in `tools/slice_queue_writer.py` output for non-ASCII Unicode in candidate source descriptions). Both empirical N=0 but the failure shapes are loud (P1.1 → `fatal: missing path`; P3.10 → mojibake'd queue file). Closes the last latent Phase-1 footgun in the solo-cooperative parallel-slice execution roadmap.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Close the 7-finding backlog from slice-074's code-Critic review (M1 + m1–m5, all DEFERRED to slice-075+ bundle per voluntary-restraint N=15 cumulative; see `architecture/slices/archive/slice-074-codify-cp-r-in-branch-2-skill/code-review.md`) plus the P3.10 cp1252 mojibake observation from `architecture/slices/archive/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt`. This is the canonical bundle-cleanup-at-N+1 shape (slice-071 precedent at 31-finding scale; this slice at 7-finding scale).

After this slice ships, the solo-cooperative `/commit-slice --merge` parallel-slice workflow has no known latent footguns — `/build-slice` Phase A's switch-commit-switch recipe at point 4 works in a fresh shell session, and `/slice` Step 6.5's queue output is UTF-8-correct for non-ASCII source descriptions.

## Acceptance criteria

1. **P1.1 / M1 closed — variable-scope at point 4**: `$wt_base`, `$repo_root`, `$default` variable assignments are hoisted OUT of point 1's codefence into a shared pre-amble appearing BEFORE the "1. **If on default branch**" header; point 4's switch-commit-switch codefence executes correctly when reached from a fresh shell session (no prior point's codefence executed). Structural-pin test asserts variable assignments appear OUTSIDE any numbered point's codefence in the `### Branch state` section.

2. **P3.10 closed — cp1252 mojibake**: `tools/slice_queue_writer.py` writes UTF-8-correct output for non-ASCII Unicode source descriptions (`§`, `—`, `→`, etc.); no cp1252 mojibake (`Â§`, `â€"`) in the rendered `architecture/slice-queue.md`. Regression test round-trips a candidate with `§`-prefixed source field through `write_slice_queue` and asserts the on-disk file contains the UTF-8 codepoint, not the cp1252 sequence.

3. **m1 + m2 closed — skill-prose hardening**: (a) `<scaffolding files>` placeholder at `skills/build-slice/SKILL.md:78` replaced with a concrete pathspec (recommended: `architecture/slices/slice-NNN-<slice-name>/ architecture/slice-queue.md`); structural-pin test asserts the codefence contains no bare `git add .` or `git add -A`. (b) cp-r seed at point 4 either de-duplicated (cleaner) OR the test `test_cp_r_lines_use_if_then_guard_for_source_dir_absence` is tightened from `>= 2` to exact-count (`== 4` if duplication intentional); the chosen disposition prevents silent count divergence.

4. **m3 + m4 + m5 closed — test-quality hardening**: (a) `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py:156-160`'s comment-position-fragile no-`-b` regex is replaced with a comment-stripped variant (`code_only = re.sub(r'#[^\n]*', '', codefence); re.search(...)`) OR the regex carries an explanatory docstring. (b) `_branch_state_section` helper duplicated verbatim across `tests/methodology/test_build_slice_skill_cp_r_step.py` + `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py` is promoted to a shared private module (recommended: `tests/methodology/_skill_parse_helpers.py` per WIRE-1 exemption pattern). (c) `tests/methodology/test_r_20_retired.py`'s `subprocess.run(..., check=True)` is replaced with explicit returncode + stderr assertion so audit-internal errors surface readably.

5. **Regression-free + 3-Critic stack disposition recorded**: pytest 100% PASS with no test-count regression vs slice-075 baseline (expected: net-positive — new structural pins + cp1252 regression test add ~5-8 tests); `architecture/shippability.md` all rows clean at /validate-slice Step 5.5; 14 Step-6 audits clean (BC-1/RR-1/PMI-1/CAD-1/OSDG-1/INST-1/WS-1/ETC-1/WIRE-1/TF-1/VAL-1/CSP-1/SUP-1/LINT-MOCK-1-2-3); first-Critic + meta-Critic + code-Critic each produce disposition (CLEAN / NEEDS-FIXES / advisory-deferred) consistent with voluntary-restraint discipline (N=16 cumulative if any code-Critic v1 advisory deferred).

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology / SKILL.md prose | tests/methodology/test_build_slice_skill_branch_state_preamble.py | test_variable_assignments_appear_outside_numbered_points | PENDING |
| 1 | methodology / SKILL.md prose | tests/methodology/test_build_slice_skill_branch_state_preamble.py | test_point_4_codefence_does_not_redefine_preamble_vars | PENDING |
| 2 | regression / tools | tests/methodology/test_slice_queue_writer_utf8.py | test_write_slice_queue_emits_utf8_for_non_ascii_source_descriptions | PENDING |
| 3 | methodology / SKILL.md prose | tests/methodology/test_build_slice_skill_scaffolding_pathspec.py | test_scaffolding_files_placeholder_replaced_with_concrete_pathspec | PENDING |
| 3 | methodology / SKILL.md prose | tests/methodology/test_build_slice_skill_scaffolding_pathspec.py | test_codefence_contains_no_bare_git_add_dot_or_dash_A | PENDING |
| 3 | methodology / cp-r duplication discipline | tests/methodology/test_build_slice_skill_cp_r_step.py | test_cp_r_lines_use_if_then_guard_for_source_dir_absence | MODIFIED-FROM-EXISTING (tighten `>=2` to exact count or de-dup assertion) |
| 4 | methodology / regex readability | tests/methodology/test_build_slice_skill_dirty_tree_resolution.py | test_point_4_no_dash_b_against_codefence | MODIFIED-FROM-EXISTING (comment-stripped regex OR docstring example) |
| 4 | methodology / helper extraction | tests/methodology/test_skill_parse_helpers_shared.py | test_branch_state_section_helper_lives_in_shared_module | PENDING |
| 4 | methodology / subprocess hygiene | tests/methodology/test_r_20_retired.py | test_r_20_retired_in_risk_register_audit_output | MODIFIED-FROM-EXISTING (explicit returncode + stderr surface) |
| 5 | end-to-end regression | (manual) | full pytest + shippability + 14 Step-6 audits | PENDING |

The 3 PENDING test-modification rows on existing test functions (rows 3.cp-r, 4.regex, 4.subprocess) follow the slice-071 precedent for modifying-existing-tests inside a code-Critic-cleanup bundle: the modification weakens a pre-existing passing test then immediately re-strengthens it to the new contract; the WRITTEN-FAILING moment is captured at design-time stress-test review per RSAD-1 (the modified test must fail under the OLD source before the source is fixed to the NEW contract).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Variable-scope at point 4 fixed | Bash-execute the dirty-tree branch's recipe in a fresh subshell with `env -i bash --noprofile --norc` after sourcing only the hoisted preamble; assert all 3 var expansions resolve non-empty. Plus pytest `test_variable_assignments_appear_outside_numbered_points`. |
| 2 | cp1252 mojibake fixed | `python -c "from tools.slice_queue_writer import write_slice_queue; ..."` with a synthetic candidate `source="§foo — bar"`; read `architecture/slice-queue.md` back; assert `§` (UTF-8 0xC2 0xA7) present, `Â§` (cp1252 mojibake 0xC3 0x82 0xC2 0xA7) absent. Plus pytest regression test. |
| 3 | Skill-prose hardening | grep `skills/build-slice/SKILL.md` for the new concrete pathspec; confirm no bare `git add .` or `git add -A` in the `### Branch state` section codefences. Plus the 3 structural-pin tests. |
| 4 | Test-quality hardening | pytest the 3 modified tests + the new shared-helper test; verify all PASS; verify `_branch_state_section` is no longer duplicated (grep for the function definition; expect exactly 1 occurrence in `tests/methodology/_skill_parse_helpers.py` + N imports). |
| 5 | Regression-free + 3-Critic disposition | `pytest --no-header -q` ⇒ 100% PASS; `tools/shippability_catalog_run.py` ⇒ all rows PASS; 14 Step-6 audits ⇒ all clean (or BC-GLOBAL-2 / LINT-MOCK-1 documented-Important-defer per slice-071 precedent); first-Critic + meta-Critic + code-Critic each disposition recorded in `critique.md` + `critique-review.md` + `code-review.md`. |

## Must-not-defer

- [ ] **Fresh-shell empirical execution** of the post-fix dirty-tree branch recipe (P1.1) — `env -i bash --noprofile --norc` against the hoisted preamble + point 4's codefence. NOT just the structural-pin test; APED-1 says execute, not reason.
- [ ] **UTF-8 round-trip verification** for `slice_queue_writer.py` with the actual cp1252-prone characters from slice-074's observation (`§`, `—`). APED-1 + real-corpus input.
- [ ] **Pytest regression-free** at slice end — no decrease in test count from slice-075 baseline; no skipped-or-deferred new tests.
- [ ] **CAD-1 + OSDG-1 byte-equality** for any `skills/*/SKILL.md` or `agents/*.md` edits — if `skills/build-slice/SKILL.md` changes, forward-sync to `~/.claude/skills/build-slice/SKILL.md` + verify via `$PY -m tools.build_slice_skill_drift_audit` (or the canonical drift audit name).
- [ ] **MEPD-1 EXCLUDE rationale documented** — this slice mints no new RULE-ID, no new ADR, no PMI-1 bump; the MEPD-1 EXCLUDE posture must be explicitly declared in design.md per ADR-040 / ADR-041 + slice-071 + slice-075 precedents. Verified at /critique via Dim 7 checklist sub-bullet.

## Out of scope

- **New ADR**: this is in-band methodology-prose-fix + tool-bug-fix; no new architectural decision.
- **New methodology rule**: MEPD-1 EXCLUDE; no new RULE-ID; no PMI-1 bump.
- **R-20 candidates (b)/(c)/(d) escalation**: slice-074's candidate (a) holds; only escalate if empirical refutation surfaces at N≥3 (currently N=0). Out of scope.
- **Concurrent /diagnose worktree-vs-main-tree convergence** (P3.5 race-surface): theoretical risk, not empirical. Defer until P6.3 surfaces it.
- **PSQ-4 (--push-time rebase)**: PR-based workflow; slice-079+ candidate per Phase 3 roadmap.
- **BCR-1 dual-tree replication** (P3.3): N=2 cumulative; promote at N=3. Out of scope.
- **Wider voluntary-restraint v2 work** (TRI-1 + verdict-driven block + AI-bloat passes): slice-062+ deferral; out of scope here.

## Dependencies

- Prior slices: [[slice-074-codify-cp-r-in-branch-2-skill]] — code-Critic findings deferred to this bundle (M1 + m1–m5); [[slice-075-close-merge-substep-3-worktree-collision]] — source-pending-items.txt names P3.10 cp1252 mojibake; [[slice-071-bundle-066-to-070-code-critic-cleanup]] — direct shape precedent for code-Critic-cleanup bundle.
- Vault refs: [[skills/build-slice/SKILL.md]] (Branch state section L45-90); [[tools/slice_queue_writer.py]]; [[tests/methodology/test_build_slice_skill_cp_r_step.py]]; [[tests/methodology/test_build_slice_skill_dirty_tree_resolution.py]]; [[tests/methodology/test_r_20_retired.py]]; [[decisions/ADR-063]] BRANCH-2; [[decisions/ADR-064]] PSQ-1; [[decisions/ADR-067]] PSQ-2; [[decisions/ADR-068]] PSQ-3.
- Risk register: no open HIGH-band risk retired (R-13 + R-2 are LOW-band, unrelated); this slice retires latent footguns documented at slice-074 reflection + source-pending-items.txt.
- Source: `architecture/slices/archive/slice-074-codify-cp-r-in-branch-2-skill/code-review.md` (M1 + m1–m5) + `architecture/slices/archive/slice-075-close-merge-substep-3-worktree-collision/source-pending-items.txt` P1.1 + P3.10.

## Mid-slice smoke gate

At ~50% of build (after AC1 + AC2 source-fixes land, before AC3/AC4 hardening):

```bash
# Smoke 1 — P1.1 fresh-shell execution
env -i HOME="$HOME" PATH="$PATH" bash --noprofile --norc -c '
  source <(awk "/^### Branch state/,/^## /" skills/build-slice/SKILL.md | sed -n "/```bash/,/```/p" | sed "/```/d" | head -20)
  echo "default=$default wt_base=$wt_base repo_root=$repo_root"
'
# Expected: all three vars non-empty.

# Smoke 2 — P3.10 UTF-8 round-trip
PY="$USERPROFILE/.claude/.venv/Scripts/python.exe"
"$PY" -c "
from tools.slice_queue_writer import write_slice_queue
import pathlib, tempfile
cands = [{'name': 'foo', 'source': '§foo — bar', 'hint_files': [], 'effort': 'SMALL', 'risk_retired': 'LOW'}]
write_slice_queue(repo_root=pathlib.Path('.'), candidates=cands, active_slice_num=76, graph_path=pathlib.Path('graphify-out/graph.json'))
text = pathlib.Path('architecture/slice-queue.md').read_bytes()
assert b'\xc2\xa7' in text, 'UTF-8 § (0xC2 0xA7) missing'
assert b'\xc3\x82\xc2\xa7' not in text, 'cp1252 mojibake Â§ present'
print('Smoke 2 OK')
"
```

If either smoke fails: STOP. Diagnose at source. Do not continue to AC3/AC4 hardening on top of a broken AC1/AC2 foundation.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] Must-not-defer list (5 items above) fully addressed
- [ ] `/drift-check` passes (no vault-vs-code divergence)
- [ ] Mid-slice smoke (P1.1 fresh-shell + P3.10 UTF-8 round-trip) still passes
- [ ] No new TODOs / FIXMEs / debug prints in source diff
- [ ] 14 Step-6 audits clean (BC-1 / RR-1 / PMI-1 / CAD-1 / OSDG-1 / INST-1 / WS-1 / ETC-1 / WIRE-1 / TF-1 / VAL-1 / CSP-1 / SUP-1 / LINT-MOCK-1-2-3) — or documented Important-defer per voluntary-restraint
- [ ] 3-Critic stack disposition recorded: `critique.md` (first-Critic) + `critique-review.md` (meta-Critic) + `code-review.md` (code-Critic), each with disposition counts; CRSI-1 v1 walking-skeleton advisory-only — code-Critic findings may defer to slice-077+ next bundle per voluntary-restraint N=16 cumulative
