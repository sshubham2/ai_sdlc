# Reflection: Slice 089 make-commit-slice-stale-branch-check-parallel-slice-aware

**Date**: 2026-05-31
**Shipped**: YES

## Validated
- Worktree-backing is a sound stale-vs-active discriminator — live demo on a real multi-worktree repo: backed peers → `parallel_slices`, worktree-less orphan → `orphan_branches` → `verdict: refuse`. (`tools/stale_branch_classifier.py`)
- Reusing the RAW `pulse_worktree_resolver._parse_worktree_porcelain` (not the name-filtered `detect_active_worktrees`) correctly recognizes a non-canonical worktree-backed branch (`slice/077`) — validated by `test_noncanonical_named_worktree_backed_branch_allowed_not_orphan` + live demo (`slice/077` in `parallel_slices` + `noncanonical_backed`, NOT a false orphan).
- Both `--merge` and `--push` guardrail surfaces are byte-identical (FBCD-1 parity test) — symmetry delivered.
- Genuine-stale protection preserved — isolated worktree-less orphan still refuses (AC3).
- OSDG-1 in-repo == installed SKILL.md holds after sync.

## Corrected
- (No vault corrections.) The design held end-to-end; all dual-Critic + code-Critic fixes were applied during /critique and /build-slice, not discovered as wrong later. ADR-081 reversibility wording was sharpened at /critique (m1).

## Discovered
- **`pulse_worktree_resolver._run_git` (L164) omits `encoding=`** — it has the exact cp1252 git-subprocess-decode bug that the PARALLEL sibling slice-090 exists to fix. slice-089 sidestepped it by NOT reusing `_run_git` (reusing only the pure-string parser) and passing `encoding="utf-8"` on its own git calls. Impact: reinforces slice-090's scope; the fix should sweep ALL git-subprocess call sites, not just `parallel_conflict_resolver.py`.
- **The new-tool count-bump fan-out is now N≥3 (081 / 087 / 089)** — adding one `tools/*.py` touched: `plugin.yaml`, `tools/install_audit.py`, `INSTALL.md` (L22 + L166 count literal), the cp1252 coverage parametrize list in `test_utf8_stdout_regression.py`, AND two sibling per-tool inventory-pin tests (`test_stranded_slice_audit_tool_inventory.py`, `test_pulse_worktree_resolver_tool_inventory.py`) that hardcode the `35` count at L22/L166. No Critic layer caught these; the full suite did. Candidate for a build-check (see Step 5b).

## Deferred
- The `--push` rebase-and-conflict-resolve extension — slice-090-queued follow-on (now renumbered to **091**; 090 is taken by the parked cp1252 fix). slice-089 only makes the rebase path *reachable* by fixing the pre-flight false-positive.
- Codifying the "new git-subprocess tool → `encoding='utf-8'`" build-check — natural home is slice-090 (the dedicated cp1252-decode fix), to avoid premature/duplicate promotion.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality observed in build/validate:

- **B1** (own-worktree self-exclusion): VALIDATED — ACCEPTED-FIXED; the path+branch exclusion was confirmed correct by `test_current_slice_own_worktree_excluded_by_path` + the live worktree demo.
- **B2** (APED-1 reasoned-not-executed): VALIDATED — ACCEPTED-PENDING; executing against REAL `git worktree add` fixtures at build was exactly the right discharge; the fixtures confirmed the classification end-to-end.
- **B3** (filter-cascade misclassification): VALIDATED — ACCEPTED-FIXED; switching to the raw parser confirmed correct (the `slice/077` noncanonical-backed case is allowed, not a false orphan).
- **B-add-1** (meta-Critic; raw-vs-short set-key mismatch): VALIDATED — the highest-value catch of the slice. Without the `refs/heads/`-strip the intersection would always be empty → universal false-refuse. Confirmed by `test_worktree_backing_uses_short_form_not_raw_refname` + live demo.
- **M1** (exit-code parity 0/1/2): VALIDATED — ACCEPTED-FIXED; CLI tests confirm 0/1/2.
- **M2** (symmetry + `--push` window): VALIDATED — ACCEPTED-FIXED; byte-identical block + parity test.
- **M3** (bootstrap self-exclude current): VALIDATED — ACCEPTED-FIXED.
- **M-add-1** (meta-Critic; path-norm belt): VALIDATED — `test_self_exclusion_branch_belt_covers_path_equality_miss` (strengthened per code-m2 to prove the belt is surgical) confirms the branch-belt covers a path-equality miss.
- **m1 / m2 / m-add-1 / MEPD-1**: VALIDATED — all ACCEPTED-FIXED; boundary tests + MEPD-1 EXCLUDE rationale hold.
- **code-Critic**: 0 blockers / 0 majors / 3 minors. code-m2 (branch-belt test not surgical) VALIDATED-and-fixed in-slice; code-m1 (`noncanonical_backed` earns keep) + code-m3 (`_norm_path` no case-fold) accepted-no-change with documented rationale.

**Missed by Critic**: the new-tool count-bump fan-out (INSTALL.md L22/L166 + the two sibling inventory-pin tests' `35` literals + cp1252 parametrize list) was caught by the full suite at build time, NOT by any design/meta/code Critic. This is a recurring class (slice-081 N=1 "~6 second-order sites", slice-088 "old-literal grep across tests + shippability"). The design Critics don't run the suite; the code-Critic reviews the slice diff (where I'd already fixed the siblings). It is structurally a build-time-discovered class.

**Pattern**: 3-Critic stack complementarity held N+1 — design-Critic caught the design-level filter-reuse (B3); meta-Critic caught the Builder's-fix-introduced set-key mismatch (B-add-1, the "a Critic's own fix is a fresh claim" class, now N≥4 across 078/082/083/089); code-Critic confirmed execution-level correctness + a test-oracle surgical-gap (code-m2). Do NOT collapse the stack.

## Lessons for next slice
- **A new tool that runs git (or any external) subprocesses MUST pass `encoding="utf-8"` — and MUST NOT blindly reuse a sibling's git helper without checking its encoding.** `pulse_worktree_resolver._run_git` lacks it (the slice-090 cp1252 class); slice-089 reused only the pure-string parser and ran git itself with explicit encoding. Strong build-check candidate; slice-090 should own the codification.
- **New-tool count-bump fan-out is N≥3 (081/087/089): on adding a `tools/*.py`, immediately grep every count literal** — `plugin.yaml`, `install_audit.py`, `INSTALL.md` L22+L166, cp1252 parametrize list, and per-tool inventory-pin tests' hardcoded count. The BC-PROJ-7/9 checklist under-enumerates the sibling inventory-pin tests.
- **Parallel-slice discovery at build setup is real and valuable** — checking `git status` (not the stale conversation-start snapshot) at the worktree boundary surfaced the parked slice-090, prevented a number collision being committed, and fed cp1252 intel into this slice.

## Vault updates made (thin vault — small list)
- [[decisions/ADR-081]] — minted (worktree-backing discriminator; reversibility cheap)
- [[risk-register.md]] — no new risk (slice closes the parallel-unaware false-positive, which was a noted-but-unregistered defect; not an R-NN flip)
- [[shippability.md]] — added the slice-089 critical-path row (Step 5.3)
- [[lessons-learned.md]] — appended slice-089 entry
- [[slices/_index.md]] — Active table (both 089+090 corrected earlier); 089 archived
