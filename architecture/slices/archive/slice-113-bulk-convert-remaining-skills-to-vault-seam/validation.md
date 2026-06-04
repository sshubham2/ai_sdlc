# Validation: Slice 113 bulk-convert-remaining-skills-to-vault-seam

**Date**: 2026-06-04
**Result**: PASS

## Per-criterion results

### AC1: Bulk conversion — convertible `architecture/…` refs → `<vault>/…`; carve-out classes stay concrete
- **Status**: PASS
- **Evidence**: `--json` → `{rewrite-at-flip: 130, doc-example: 2}` total 132 (171 converted, 116 carve-outs). The precise observable (carve-out-aware) is the ratchet: `converted_file_regressions(audit_root('.'))` returns **0** un-sanctioned regressions. Spot-checks: `architecture/slice-queue.md` stays literal in `slice/SKILL.md`; `architecture/decisions/**` stays literal in `code-review/SKILL.md` (the /code-review B1 fix). (CLAUDE.md/agents carve-outs are the slice-112 sanctioned `_CONVERTED_CARVEOUTS` — exempt, not regressions.)
- **Notes**: AP-3 build-time recalibration broadened the active-folder discriminator to catch wildcard/placeholder/ellipsis forms.

### AC2: Inventory + op-gate re-pin (seam-aware, floors stable)
- **Status**: PASS
- **Evidence**: `--strict` exit **0** (132/130/2/0); `--op-gate --strict` exit **0** with per-class breakdown `{op-routed: 6, op-deferred-to-flip: 11, op-out-of-scope: 23, op-unrouted: 0}` — floors STABLE (no AP-12 loosening, B2 seam-aware). Ratchet mutations green (`test_converted_file_regression_exits_2`, `test_ratchet_independent_of_repinned_baseline`, `test_ratchet_fires_on_differing_value_despite_same_file_carveout`). The 3 `<vault>/`-sink op-gate tests pass + are extractor-sensitive (m1 fix).
- **Notes**: `EXPECTED_TOTAL`=132, `_CLASS_COUNT_FLOOR[rewrite-at-flip]`=130, `_BASELINE_SHA256`=99480a6… (post-/code-review-B1).

### AC3: OSDG-1 / mini-CAD forward-sync — every converted guarded SKILL.md byte-synced
- **Status**: PASS
- **Evidence**: `pytest tests/methodology -k skill_drift` → **18 passed** (the on-disk 13 `*_skill_drift.py` — incl. `code-review` + `pulse`, NOT `diagnose` — M-add-1 — plus the normalization tests). Installed copies re-synced for all 23 converted skills (incl. the code-review re-sync after the B1 revert).

### AC4: Consumer contracts discharged in-slice (AP-13 / AP-10 / FBCD-1(c))
- **Status**: PASS
- **Evidence**: `test_bcr_1_backlog_round_trip.py` → **3 passed** (BCR-1 anchor green untouched — diagnose-out class-7 carve-out keeps `diagnose-out/backlog.md` literal). `test_validate_slice_skill.py:65` repointed to `<vault>/shippability.md` (command-arg, B1). `test_build_slice_skill_dirty_tree_resolution.py` + `test_code_review_skill.py` (pathspec carve-out guards) green. Shippability count rows 113/117/118 re-pinned (303/301 → 132/130) + new row 119 (AP-10 fan-out incl. the module docstring).

### AC5: Flip-neutrality + residual recorded
- **Status**: PASS
- **Evidence**: `_vault_paths.VAULT_ROOT == Path("architecture")` (default resolves concrete — zero pre-flip behaviour change). Full suite **1617 passed, 2 skipped** (post-B1-fix re-run). The exact residual recorded in build-log + the R-32 register: 116 carve-outs (classes 1/4/5/6/7) land at the physical move; the agent-prose surface (4 agent files) deferred to the `convert-agent-prose-to-vault-seam` follow-on (M1).

## VAL-1 layered safety (Step 5b)
- **Layer A (credentials)**: 0 secrets found.
- **Layer B (dep hallucination)**: 0 import findings (changed `.py`: the tool + 3 tests; `--imports-allowlist tests`).
- **Result**: clean.

## WS-1 / ETC-1
- Walking-skeleton: false → N/A (audit clean by default-off). Exploratory-charter: false → N/A.

## Multi-instance validation
- **Required?**: no (no multi-user/device/account surface — methodology tooling + prose).
- **Result**: not-applicable.

## Shippability catalog regression check (Step 5.5)
- **Pre-catalog gates**: SCMD-1 clean (118 rows), PTFCD-1 clean (483 path tokens), SVW-1 clean (20 routed / 3 exempted).
- **Catalog run**: `tools.shippability_runner` → **118 row(s), 118 PASS, 0 FAIL**. No past slice regressed by slice-113. (Includes the slice's own new row 119 + the slice-112 rows 113/117/118 re-pinned to 132/130.)

## Reality surprises
- The **EOL worktree-checkout artifact**: `git worktree add` checked out CRLF while the main tree + `.gitattributes eol=lf` are LF, failing `test_guarded_md_files_have_no_crlf_in_working_tree`. Resolved by normalizing the worktree's eol=lf-scoped files to LF (no spurious diff — git stores LF). Not a slice defect; a worktree-environment quirk worth noting for future BRANCH-3 slices that edit eol=lf-pinned files.
- The **B1 git-pathspec-prose miss** (caught by /code-review): a pathspec described in prose without `:(exclude)` on its own line is invisible to `_PATHSPEC_RE`, so the discriminator converted it. A latent gap in the discriminator's pathspec detection — documented; the fix kept the 3 concrete.
