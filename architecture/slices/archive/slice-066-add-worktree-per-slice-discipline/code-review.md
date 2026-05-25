# Code Review: Slice 066 add-worktree-per-slice-discipline

**code-Critic reviewed**: slice diff vs master (filtered to in-scope paths)
**Date**: 2026-05-24
**Result**: FINDINGS

## Summary

Sound diff. The dual-Critic stack + N=10 Builder self-catches consumed most defect surface area at design-time + Phase A-D build-time; the remaining concerns are line-level code defects the structural Step 6 audits cannot reach. **0 Blockers / 2 Majors / 4 minors** below. Most load-bearing: **M1** (`_is_repo_root_a_worktree` walks off filesystem on shallow gitdir, returning `(True, <unrelated-ancestor>)` with no guard) and **M2** (SKILL.md bash uses cwd-derived `wt_base` while audit derives the canonical path via `.git`-ancestor-walked `main_repo_root` — divergence breaks if user runs `/build-slice` from a sub-directory). The 14 Step 6 audits all PASS; the codebase is shippable. Per **CRSI-1 v1** ([[ADR-059]]; methodology v0.64.0) findings are **advisory only** — do NOT block `/validate-slice` (slice-062 will add TRI-1 verdict-driven block). Bundled cleanup nomination for slice-067+ per slice-064 / slice-065 advisory feedback loop precedent.

## Changed files (in-scope)

```
CLAUDE.md
VERSION
methodology-changelog.md
plugin.yaml
pyproject.toml
skills/build-slice/SKILL.md
skills/commit-slice/SKILL.md
tools/branch_workflow_audit.py
tests/methodology/test_adr_063_exists_and_supersedes_adr_019.py
tests/methodology/test_r17_retirement.py
tests/methodology/test_branch_workflow_audit.py
tests/methodology/test_build_slice_skill.py
tests/methodology/test_commit_slice_skill_merge_flag.py
tests/methodology/test_commit_slice_skill_sync_after_pr_flag.py
tests/methodology/test_root_claude_md_branch_per_slice_rule.py
tests/methodology/test_methodology_changelog.py
```

(16 files, 858 insertions / 23 deletions; matches Step 1 union-of-three-sources file list per [[ADR-062]].)

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. The 5 first-Critic Blockers + meta-Critic Blocker-class were all ACCEPTED-FIXED pre-build; no structural defects of that severity remain in code.

### Majors

#### M1: `_is_repo_root_a_worktree` walks off the filesystem on shallow gitdir, returning `(True, <unrelated-ancestor>)`

- **Claim under review**: `tools/branch_workflow_audit.py:243-277` — the helper does `main_repo = gitdir.parent.parent.parent` after parsing `gitdir: <path>` from the `.git` file. The contract is "gitdir points to `<main-repo>/.git/worktrees/<name>`; walk up 3 to land on `<main-repo>`."
- **Issue**: when the gitdir path has fewer than 3 parent components (corrupted `.git` file, attacker-crafted pointer, or unusual setup), `Path.parent.parent.parent` silently walks **off the actual repo path into unrelated directories** rather than returning `None` or raising. The `try ... except (IndexError, AttributeError): return (False, None)` block at lines 273-276 is a no-op — `Path.parent` on a root path returns the path itself (no exception), so the exception handler is unreachable.
- **Evidence**: code-Critic agent reproduced concretely: a `.git` file content `gitdir: <3-deep-shallow-path>` causes `gitdir.parent.parent.parent` to walk past the intended worktrees-record-root into an unrelated existing directory. `_worktree_registered(<that-directory>, ...)` then runs `git -C <unrelated-dir> worktree list --porcelain` — silently fails OR worse, succeeds if the unrelated dir happens to be another git repo, returning misleading data.
- **Framework**: Wiegers — every claim in code must trace to evidence. The code's implicit claim "gitdir has at least 3 parents" is not verified. Bach/Bolton edge-case heuristic — depth-truncated paths are a known input edge for `Path.parent`-walks.
- **Proposed fix**: validate the parent walk before returning:
  ```python
  if len(gitdir.parts) < 4:
      return (False, None)   # not deep enough for <main>/.git/worktrees/<name>
  main_repo = gitdir.parent.parent.parent
  if not (main_repo / ".git").exists():
      return (False, None)   # walked off — main repo would have its own .git
  return (True, main_repo)
  ```
  The `(main_repo / ".git").exists()` sanity check is the structurally cheaper guard — also catches the pernicious case where gitdir DOES have 3+ parents but they don't point to a repo. Cost: 1 stat call per audit invocation.

#### M2: SKILL.md `wt_base="$(dirname "$(pwd)")/$(basename "$(pwd)")-wt"` derives from cwd, but audit derives from `.git`-ancestor — divergent if `/build-slice` runs from a sub-directory

- **Claim under review**: `skills/build-slice/SKILL.md:55-60` instructs `wt_base="$(dirname "$(pwd)")/$(basename "$(pwd)")-wt"` followed by `git worktree add "$wt_base/slice-NNN-<slice-name>" -b ...`. The implicit assumption is that `pwd` IS the repo root. `tools/branch_workflow_audit.py:280-287` `_resolve_expected_worktree_path(slice_folder, main_repo_root)` uses `main_repo_root.parent / f"{main_repo_root.name}-wt" / slice_folder.name`, where `main_repo_root` comes from the `.git` ancestor walk.
- **Issue**: if cwd is `<HOME>\ai_sdlc\architecture\slices\` (plausible — `/build-slice` is often invoked mid-conversation from wherever cwd happens to be) when Claude executes the SKILL.md bash snippet, the bash creates the worktree at `<HOME>\ai_sdlc\architecture\slices-wt/slice-NNN-...` but the audit at Step 6 pre-finish computes the expected path as `<HOME>\ai_sdlc-wt/slice-NNN-...` and emits `worktree-path-shape-violation`. The user then has a real registered worktree at one path and an audit insisting on a different path.
- **Evidence**: SKILL.md L57 vs audit L287. There's no `cd "$(git rev-parse --show-toplevel)"` guard before the `wt_base` computation. The dirty-tree check at L64 (`git status --porcelain`) works from any subdirectory because `git` walks up — masking the cwd-vs-repo-root divergence.
- **Framework**: Sommerville requirements-design-code traceability — design.md L46 says "the existing Branch state sub-section" should use the canonical sibling path; the audit's `_resolve_expected_worktree_path` derives the canonical path from `.git` ancestry, but the SKILL.md prose derives it from `$(pwd)`. The two surfaces are supposed to agree on the same canonical path but compute it via different mechanisms.
- **Proposed fix**: either (a) prepend `cd "$(git rev-parse --show-toplevel)"` before the `wt_base` computation; or (b) compute `wt_base` directly from `git rev-parse --show-toplevel`:
  ```bash
  repo_root="$(git rev-parse --show-toplevel)"
  wt_base="$(dirname "$repo_root")/$(basename "$repo_root")-wt"
  git worktree add "$wt_base/slice-NNN-<slice-name>" -b slice/NNN-<slice-name> "$default"
  cd "$wt_base/slice-NNN-<slice-name>"
  ```
  Option (b) is structurally cheaper — preserves the user's cwd while computing the canonical wt_base. Add a regression test asserting bash `git rev-parse --show-toplevel` appears in the prose OR explicit guidance that `/build-slice` must run from repo root.

### Minors

#### m1: `worktree_skip_used` / `worktree_skip_rationale` computed but not exposed via `AuditResult` — asymmetric with `escape_hatch_used` / `escape_hatch_rationale`

- **Claim under review**: `tools/branch_workflow_audit.py:513` — `worktree_skip_used, _worktree_skip_rationale, worktree_skip_malformed = _check_worktree_skip_line(slice_folder)`. The rationale is computed and discarded (`_` prefix); `worktree_skip_used` is used internally for the `combined_skip` logic but never surfaced.
- **Issue**: a consumer parsing `--json` output cannot distinguish "clean because BRANCH=skip" from "clean because WORKTREE=skip" — `AuditResult.escape_hatch_used` reflects only the BRANCH=skip surface. Asymmetric with the established BRANCH=skip surface; the `_check_worktree_skip_line` helper's rationale-extraction code is unused (Fowler speculative generality — computes a value no caller consumes).
- **Framework**: Newman explicit-versioning + Fowler speculative-generality.
- **Proposed fix**: add `worktree_skip_used: bool = False` + `worktree_skip_rationale: str | None = None` to `AuditResult` (`tools/branch_workflow_audit.py:100-127`); assign at line 513; surface in `to_dict()`. Symmetric with the existing BRANCH=skip surface. Cost: 4 added lines, no behavior change.

#### m2: `test_honours_canonical_worktree_skip_rationale_line` is not load-bearing — passes even without the WORKTREE=skip line

- **Claim under review**: `tests/methodology/test_branch_workflow_audit.py:351-388`. The fixture sets up main tree + slice branch checked out IN the main tree + WORKTREE=skip line in build-log.md, then asserts no `worktree-*` Important violations.
- **Issue**: code-Critic empirically reproduced — REMOVING the WORKTREE=skip line from the fixture still produces a clean audit. In main-tree mode with the slice branch already checked out IN the main tree, `_slice_branch_in_worktree(repo_root, expected)` finds the slice branch at the main-tree's worktree-list entry, and `_paths_equivalent(wt_path, repo_root)` returns True (it IS the main tree), so no `worktree-cwd-mismatch` fires regardless. The test asserts a property the fixture already satisfies for an unrelated reason.
- **Framework**: APED-1 (Audit-Predicate-Empirical-Demonstration per slice-066 critique-review M-add-5) — the test should EMPIRICALLY fail without the codified behavior.
- **Proposed fix**: change the fixture to actually require the escape-hatch — create a worktree elsewhere with the slice branch (mirroring `test_rejects_main_tree_cwd_when_worktree_registered_elsewhere`), then add the WORKTREE=skip line, then assert clean. Remove the line and the test should fail with `worktree-cwd-mismatch`. Could be added as a separate test alongside the current one without removing it.

#### m3: `_paths_equivalent` does inline `import os` per call instead of module-level import

- **Claim under review**: `tools/branch_workflow_audit.py:298` — `import os` appears inside the function body, on every call.
- **Issue**: cosmetic; per-call import lookup adds ~microsecond overhead. The module already imports `subprocess`, `re`, etc. at top; `os` should join them.
- **Framework**: PEP 8 / Fowler.
- **Proposed fix**: move `import os` to the module-level imports block. Trivial.

#### m4: SKILL.md's `git worktree add` bash snippet is not annotated for PowerShell-on-Windows (project's preferred shell per `~/.claude/CLAUDE.md`)

- **Claim under review**: `skills/build-slice/SKILL.md:56-60` — bash snippet `wt_base="$(dirname "$(pwd)")/$(basename "$(pwd)")-wt"` etc. Critique-review M-add-3 caught the same class for commit-slice SKILL.md Step 5b/5d and annotated those with "(POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash...)". The build-slice SKILL.md Branch state snippet lacks the parallel annotation.
- **Issue**: PowerShell cannot parse `$(dirname ...)` — the user's preferred shell on Windows is PowerShell. The commit-slice cleanup snippets have the parenthetical; the build-slice prerequisite snippet doesn't.
- **Framework**: Sommerville environment-assumption + cross-spec parity (RPCD-1) — sibling SKILL.md sections with the same shell dependency should annotate consistently.
- **Proposed fix**: add the same parenthetical at `skills/build-slice/SKILL.md:56` end-of-snippet: "(POSIX shell; on Windows invoke via Git for Windows' bundled MSYS bash — same dependency convention as commit-slice Step 5b/5d)".

## Dimensions checked

- [x] **Unfounded assumptions** — M1 (parent-walk depth assumption), M2 (cwd-as-repo-root assumption)
- [x] **Missing edge cases** — M1 (shallow gitdir), m2 (test not exercising the absent-escape-hatch state). Detached-HEAD-in-worktree handled correctly (usage-error). Both-escape-hatches-present handled correctly
- [x] **Over-engineering** — m1 (`_check_worktree_skip_line` rationale extracted but never consumed by `AuditResult`). No other speculative generality observed
- [x] **Under-engineering** — none. Every AC (1-5) has a delivering code element. All 21 TF-1 rows traced. The audit's 4 new violation kinds match the 4 design.md error-model rows 1:1
- [x] **Contract gaps** — m1 (asymmetric `AuditResult` surface). CLI exit-code contract (0/1/2) preserved; type hints on new helpers complete
- [x] **Security** — none. Methodology-internal tooling; no user-facing inputs, no auth surfaces, no secrets, no injection vectors. `_run_git` wrapper uses list-arg subprocess invocation — sound
- [x] **Drift from vault** — M2 (skill prose vs audit code divergence on canonical-path derivation). ADR-063 §"Scope of supersession" surface enumeration (N=3 carry-forward + N=3 new) matches the code at `tools/branch_workflow_audit.py:53-66`. shippability.md row #66 cites BRANCH-2 + ADR-063 + R-17 per BCR-1
- [x] **Web-known issues** — none. Skipping WebSearch — the slice's web-known evidence base (microsoft/vscode#101244 path-mismatch class, git-worktree docs on `branch -d` refusing on checked-out branches, MSYS bash availability) was already exercised in /critique Dim 8 + /critique-review M-add-3; no post-cutoff `git worktree` regressions known
- [x] **Cross-cutting conformance** — m3 (inline `import os` violates PEP 8 / project style of top-level imports), m4 (SKILL.md shell-portability annotation parity gap with commit-slice). UTF8-STDOUT-1 discipline preserved. `from __future__ import annotations` matches existing module style. EOL-DRIFT-1 not triggered. No phantom imports

## Disposition (v1 advisory)

Per **CRSI-1 v1** ([[ADR-059]]; methodology v0.64.0): findings are **advisory only** — do NOT block `/validate-slice`. The slice-064 / slice-065 advisory-feedback-loop precedent applies: defer the 6 findings (M1 + M2 + m1 + m2 + m3 + m4) to a **slice-067+ bundled cleanup nomination** alongside the 2 ACCEPTED-PENDING items from /critique + /critique-review (m4 graphify watch-list + M-add-5 APED-1 bootstrap-variant fixture).

Bundled cleanup target: a future `slice-NNN-bundle-066-code-critic-cleanup` slice (mirrors slice-065 shape) consuming:
- M1: add gitdir depth check + `.git`-existence sanity check in `_is_repo_root_a_worktree`
- M2: rewrite `wt_base` derivation via `git rev-parse --show-toplevel` in build-slice SKILL.md Branch state (or prepend `cd $(git rev-parse --show-toplevel)`)
- m1: surface `worktree_skip_used` + `worktree_skip_rationale` in `AuditResult` + `to_dict()`
- m2: rewrite `test_honours_canonical_worktree_skip_rationale_line` fixture to actually exercise the WORKTREE=skip dependency
- m3: hoist `import os` to module-level in `tools/branch_workflow_audit.py`
- m4: add bash-portability parenthetical to `skills/build-slice/SKILL.md:56` mirroring commit-slice

Total estimated bundled-cleanup work: ~30-45 min.

## Pipeline position

- **predecessor**: `/build-slice`
- **successor**: `/validate-slice`
- **auto-advance**: true
- **on-clean-completion**: code-review.md written; FINDINGS verdict is v1 advisory, no HALT; auto-advance to `/validate-slice` via the Skill tool.
- **user-input gates**: none in v1.
