# Critique: Slice 098 route-or-retire-git-coupled-vault-tools

**Critic reviewed**: mission-brief.md, design.md, ADR-089, project-frame.md, aggregated lessons
**Date**: 2026-06-01
**Result**: BLOCKED (Critic's assessment; final verdict set by TRI-1 triage below)

## Summary

The slice's strategic framing (route filesystem paths, fail-visible RETIRE the git-tree reads, no-flip) is sound, but the design's **mechanical model is wrong**: it treats PCR's vault coupling as "filesystem path composition" when the load-bearing coupling is **string-comparison against git-output U-file names + git pathspec literals** that `<root> / VAULT_ROOT / <subpath>` routing does not touch. 2 Blockers (AC1 routing model incomplete for PCR; AC3/AC4 byte-identity vs. the equivalence-guard `relative_to(repo_root)` composition), 5 Majors (RETIRE proxy soundness, post-flip shippability gap, git-pathspec Windows/abs edge cases, mis-located stranded sites + omitted `ls-tree` site, AST-scan non-vacuity), 2 Minors.

**Builder verification**: every load-bearing code claim was confirmed against disk (`_SOFT_FILE_SET` L57-60; equivalence-guard `relative_to`/`qrel` L1947-1965; `git add *regenerated` L436; stranded `_branch_tree_has_path` L201-203 / `_branch_tree_file` L206-208; filesystem fallback L322). All findings VALID.

## Findings

### Blockers (must address before /build-slice)

#### B1: PCR's vault coupling is mostly git-string-comparison, not filesystem-path composition — AC1's routing form does not reach it
- **Claim under review**: design.md §What's new ("every filesystem vault-path composition switches to `<root> / VAULT_ROOT / <subpath>`"); AC1 ("no hardcoded `architecture/<vault-content>` literal remains on runtime resolution paths").
- **Issue**: PCR couples to the vault in **four** distinct ways, only one of which is filesystem composition: (1) filesystem writes (`out_path = repo_root / "architecture" / "slice-queue.md"` L1061/1544/1838; `repo_root / _AUDIT_LOG_PATH`) — routable as designed; (2) **`_SOFT_FILE_SET` frozenset of forward-slash literals** (L57-60) compared against `git status --porcelain` U-file names (L212/281-282/293/365/1340/2198) — git-output string keys, NOT pathlib compositions; `VAULT_ROOT` routing produces a `Path`, not a forward-slash git-relative string. Post-flip git never reports a U-file named `architecture/slice-queue.md` (untracked) → SOFT/VAULT_CLAIM/HARD classification silently degrades; (3) git pathspec literals to `_git_show_stage(..., "architecture/slice-queue.md")` (the named RETIRE sites); (4) **`git add` pathspec literals** (`*regenerated` L436; `"architecture/slice-queue.md"` L1549) where `regenerated` = `result.regenerated_files` forward-slash literals. The per-site table lists only (1) and (3) and silently omits (2) and (4). AC1 is unsatisfiable for (2)/(4) by the stated mechanism, and those literals are on the live SOFT-resolution runtime path.
- **Evidence**: `tools/parallel_conflict_resolver.py:57-60`, `:212`, `:281-282`, `:293`, `:436`, `:1340`, `:1549`, `:1565`, `:2198`. (Builder-confirmed L57-60 + L436.)
- **Proposed fix**: Redesign the routing model to distinguish two literal classes: (a) **filesystem-path literals** → ROUTE through `VAULT_ROOT`; (b) **git-string identities** (`_SOFT_FILE_SET` keys, `_git_show_stage` pathspecs, `git add` pathspecs, `regenerated_files`) → git-tracked-path identities belonging to the RETIRE classification (or KEEP-as-identity when tracked), never routed. Add all to the per-site table. Amend AC1 to scope "filesystem resolution paths" away from git-string identities.
- **Builder draft**: **ACCEPTED-FIXED** — design.md §What's new + per-site table rewritten around the two-literal-class model; all four PCR coupling classes enumerated; AC1 wording amended in mission-brief.md to scope filesystem-resolution paths.

#### B2: No-flip byte-identity (AC4) unverified against the equivalence-guard's `relative_to(repo_root)` composition — an external `out_path` silently defeats invariants #1/#2/#3
- **Claim under review**: AC4 byte-identity; design "pathlib discards `<root>` when `VAULT_ROOT` is absolute … byte-identical".
- **Issue**: The equivalence guard keys pending writes by `out_path.relative_to(repo_root).as_posix()` (L1947) and compares against hardcoded `qrel = "architecture/slice-queue.md"` (L1965) / `srel = "architecture/shippability.md"` (L2054). With an absolute external `out_path`, `relative_to(repo_root)` raises `ValueError` → the `except ValueError` branch (L1948) falls through to `out_path.as_posix()` = the full external path → never equals `qrel` → invariant #1 claim-preservation is **never checked** → silent claim-drop (the exact R-7 / slice-090/091 class this slice claims to harden). The no-flip case is genuinely byte-identical, but the design provides no test tracing the `qrel`/`srel` comparison under the routed form.
- **Evidence**: `tools/parallel_conflict_resolver.py:1947-1950`, `:1965`, `:2054`. (Builder-confirmed L1947-1965.)
- **Proposed fix**: State that the entire SOFT-resolution write path (`out_path`, equivalence-guard `qrel`/`srel`, `git add`) is part of the **RETIRE-when-untracked** surface, not ROUTE. The RETIRE guard must fire BEFORE `resolve_soft_conflict` composes any `out_path`, so `relative_to` is never reached with an external root. Test: external/untracked SOFT-resolution refuses visibly before composing `out_path`.
- **Builder draft**: **ACCEPTED-FIXED** (design) + **ACCEPTED-PENDING** (test) — design model now places the SOFT-resolution write path under RETIRE-when-untracked with the guard firing at entry to `resolve_soft_conflict`/`resolve_vault_claim_conflict` before any `out_path` composition; the refuse-before-`relative_to` test is realized at /build-slice.

### Majors (address this slice)

#### M1: `VAULT_ROOT_IS_DEFAULT` proxy mis-fires — it conflates "fell through to default" with "git-untracked", the actual RETIRE precondition
- **Claim under review**: ADR-089 §Residual; design "`VAULT_ROOT_IS_DEFAULT` is the 'vault is external' signal the RETIRE guards key off."
- **Issue**: The RETIRE decision depends on **git-untracked-ness**, not default-resolution. An `AI_SDLC_VAULT_ROOT` set to an absolute path **inside the git tree** (a reasonable transitional config — vault relocated to `<repo>/vault/` but still tracked) → `IS_DEFAULT == False` → RETIRE fires → `git show :N:` refuses even though the vault is tracked and git-show would work → AC3 says operate, the tool refuses. Not fail-closed-harmless. The ADR concedes the proxy is inexact, then ships it as the binding gate without a test pinning its failure envelope.
- **Evidence**: ADR-089 §Decision + §Residual; design.md §What's new.
- **Proposed fix**: Replace the proxy with the precise signal at the RETIRE sites — a per-pathspec `git ls-files --error-unmatch <pathspec>` tracked-check (need not live in the leaf seam; lives at the RETIRE guard in PCR/stranded, which already call git) — OR explicitly scope AC3 to "external **untracked** root" + test the over-RETIRE-when-tracked case as documented-intentional.
- **Builder draft**: **ACCEPTED-FIXED** — adopt option (a): the binding RETIRE signal becomes a precise `git ls-files --error-unmatch <pathspec>` tracked-check at the guard (where git is already invoked). `VAULT_ROOT_IS_DEFAULT` is demoted to an optional cheap fast-path / dropped if unneeded. This is the keystone fix — it also resolves B2, M2, M3 (the guard fires exactly on untracked-ness). ADR-089 §Decision + §Residual rewritten.

#### M2: "RETIRE = fail-visible refuse" risks stranding `/commit-slice --merge` in the env-set-before-flip window
- **Claim under review**: ADR-089 §Consequences ("untracked vault can't produce a git merge-conflict; wiring the replacement is the flip slice's job"); mission-brief Out-of-scope (replacement mechanism).
- **Issue**: "Untracked vault can't produce a git merge-conflict" is only true **after** the physical move + git-untrack (the next slice). If this slice keys RETIRE on `not VAULT_ROOT_IS_DEFAULT`, then the moment an operator sets `AI_SDLC_VAULT_ROOT` (before the formal flip), PCR's auto-resolution refuses and `/commit-slice --merge` under PSQ/BRANCH-2 parallel slices hits an unresolvable rebase with no auto-resolver and no documented manual fallback. "Flip-ready that strands the merge path is not ready."
- **Evidence**: ADR-089 §Consequences + §Options(2); project-frame Trajectory (PCR family active, flip pending).
- **Proposed fix**: Add an AC / must-not-defer that the RETIRE refusal emits an **actionable operator breadcrumb** naming the manual-resolution procedure / tracking slice; document the env-set-before-flip window in ADR-089 §Residual; confirm AC3's "env set → operate" compatibility.
- **Builder draft**: **ACCEPTED-FIXED** — the M1 keystone fix (tracked-check, not the proxy) **dissolves the core hazard**: in the env-set-but-still-tracked window the guard sees a tracked pathspec → PCR proceeds normally (no stranding); the guard refuses ONLY when the pathspec is genuinely untracked, which is exactly when no git conflict can arise. Additionally add an actionable operator breadcrumb to the RETIRE refusal (must-not-defer) + document the window in ADR-089 §Residual.

#### M3: git pathspec derivation under Windows backslash + absolute-external-path is unanalyzed
- **Claim under review**: design routes `out_path` writes via `VAULT_ROOT`; slice prompt concern (d).
- **Issue**: git pathspecs must be **forward-slash, repo-relative**. `_git_show_stage` builds `f":{stage}:{path}"` (L851); `git add` takes the pathspec verbatim (L436/L1549). Feeding a `VAULT_ROOT`-composed path (backslash on Windows; absolute when external) into these git string positions yields `git show :2:C:\Users\...\slice-queue.md` (malformed) and `git add <abs-external>` (escapes work tree). "pathlib discards root when absolute" applies to `Path` joins, NOT f-string pathspec construction.
- **Evidence**: `tools/parallel_conflict_resolver.py:851`, `:436`, `:1549`; `tools/stranded_slice_audit.py:207` (`f"{branch}:{path}"`), `:202` (`ls-tree ... -- path`). (Builder-confirmed L201-208 + L436.)
- **Proposed fix**: State explicitly that NO git pathspec position ever receives a routed `Path` — they stay forward-slash repo-relative literals governed by the tracked-check guard. APED-1: add a build-time test that **executes** `_git_show_stage`/`_branch_tree_file` with an external/untracked condition and asserts the guard refuses before any malformed pathspec reaches git.
- **Builder draft**: **ACCEPTED-FIXED** (design) + **ACCEPTED-PENDING** (APED-1 test) — design states git-string positions are never routed (stay forward-slash repo-relative, tracked-guarded); the execute-on-the-real-runtime APED-1 test is realized at /build-slice.

#### M4: stranded_slice_audit git-tree-read sites mis-located in the table (L30-34 is the docstring) and the `ls-tree` vault-content read is omitted
- **Claim under review**: design per-site table: "stranded_slice_audit | bare-branch `git show <branch>:architecture/…` (L30-34) | RETIRE".
- **Issue**: L30-34 is the **module docstring**. The actual git-tree vault-content reads are `_branch_tree_file` at **L206-208** (`git show {branch}:{path}`) and **`_branch_tree_has_path` at L201-203** (`git ls-tree {branch} -- {path}`). The `ls-tree` site reads vault-content existence (`archive_path` L301, checked L302) and is just as inapplicable to an untracked vault — yet the table omits it. If only `show` is guarded, `_branch_tree_has_path(... archive_path)` silently returns `False` → STRANDED-COMPLETE archive-path detection silently dropped (AC5 violation). Also `(repo_root / archive_path).exists()` at L322 is a **filesystem** secondary fallback that needs ROUTE.
- **Evidence**: `tools/stranded_slice_audit.py:201-208`, `:300-326`. (Builder-confirmed.)
- **Proposed fix**: Correct refs to L201-203 + L206-208; add `ls-tree` as a second RETIRE-when-untracked site; route the L322/L327 filesystem fallbacks; test BOTH git-tree helpers refuse visibly when untracked.
- **Builder draft**: **ACCEPTED-FIXED** (design table corrected: both `_branch_tree_has_path`/L201-203 + `_branch_tree_file`/L206-208 RETIRE-when-untracked; L322/L327 filesystem fallbacks ROUTE) + **ACCEPTED-PENDING** (test both refuse).

#### M5: AST/source-scan pin for "no architecture/ literal" underspecified — would over-fire on git-pathspec literals or be gutted to vacuity
- **Claim under review**: design §What's new + AC1 "Verified by an AST/source-scan test".
- **Issue**: ~35 `architecture` occurrences in PCR mix (a) docstrings/comments (prose), (b) the `git add "architecture/slice-queue.md"` pathspec + `_SOFT_FILE_SET` literals that **must remain** forward-slash, and (c) filesystem-composition literals that must be routed. A naive grep false-fails on docstrings; an AST string-scan false-fails on the git-pathspec literals that are correct to keep. No precise predicate is given.
- **Evidence**: PCR has 35 `architecture` lines (docstrings, comments, `git add` L1549, `regenerated_files` L1565/1575, `_SOFT_FILE_SET` L58-59).
- **Proposed fix**: Specify the scan predicate precisely — pin absence of `architecture` **only** in filesystem-composition positions (string literal as an operand to `Path.__truediv__` against a `repo_root`/`scan_root` runtime param), allowlisting (i) docstring/comment occurrences and (ii) named git-identity literals (`_SOFT_FILE_SET`, `git add` args, `regenerated_files`, `_git_show_stage`/`_branch_tree_*` path args). Require a mutation-based non-vacuity proof (slice-092 lesson).
- **Builder draft**: **ACCEPTED-FIXED** (design specifies the precise predicate + allowlist) + **ACCEPTED-PENDING** (test realization incl. mutation non-vacuity proof at /build-slice).

### Minors (log; address if cheap)

#### m1: `_AUDIT_LOG_PATH` routing must preserve `repo_root / _AUDIT_LOG_PATH` byte-for-byte (5 consumers)
- **Issue**: `_AUDIT_LOG_PATH = Path("architecture/parallel-conflict-resolution-log.md")` (L71) consumed at L681/735/1759/2105/2149. Worth one explicit byte-identity assertion on the audit-log path specifically.
- **Evidence**: `tools/parallel_conflict_resolver.py:71`, `:681/735/1759/2105/2149`.
- **Builder draft**: **ACCEPTED-PENDING** — add `_AUDIT_LOG_PATH` to the no-flip byte-identity test's covered surfaces at /build-slice.

#### m2: confirm new RETIRE-guard diagnostics use `_stderr` (call-time), not bare `print`
- **Issue**: New RETIRE diagnostics must route through `tools._vault_paths._stderr`, not bare `print` (cp1252 N≥8). Pre-existing `print(..., file=sys.stderr)` at L229/L1957 are non-import best-effort (acceptable). Confirm-the-discipline note.
- **Evidence**: `tools/parallel_conflict_resolver.py:229`, `:1957`; design §Error model.
- **Builder draft**: **ACCEPTED-FIXED** — design §Error model now states RETIRE-guard diagnostics use `_stderr` and fire at call-time, not import-time.

## Dimensions checked
- [x] Unfounded assumptions — M1 (proxy ≠ untracked); B1 (assumed all PCR coupling is filesystem composition — false: `_SOFT_FILE_SET` + git pathspecs are string identities).
- [x] Missing edge cases — B2 (external `out_path` → `relative_to` ValueError → silent claim-drop); M3 (Windows backslash + abs path into pathspec); M1 (external-but-tracked config).
- [x] Over-engineering — none (minimal routing/guard change; the frozen-boolean signal is if anything too minimal — see M1).
- [x] Under-engineering — B1 (AC1 has no design element covering `_SOFT_FILE_SET`/git-add literals); M2 (AC3 "operate on external vault" has no design element for PCR's conflict-resolution role); M5 (AST-scan element underspecified).
- [x] Contract gaps — M4 (`ls-tree` git-tree-read site omitted from RETIRE; AC2 "every git-coupling site classified" incomplete); B2 (RETIRE enforcement boundary before vs. after `out_path` composition unspecified).
- [x] Security — none (local dev tooling; ADR-089 §Authorization N/A correct; the silent-claim-drop class is covered as correctness under B2/M4).
- [x] Drift from vault — M2 (project-frame direction-fit: RETIRE guard undermines the active PCR/PSQ/BRANCH-2 parallel-merge trajectory in the env-set-before-flip window). No ADR contradiction; MEPD-1 EXCLUDE for a seam-extension slice with an ADR + no new RULE-ID is consistent with N≥8.
- [x] Web-known issues — none applicable (pure in-repo Python + git plumbing; relevant "known issues" are the in-repo Windows-path/pathspec behaviors under M3).
- [x] Cross-cutting conformance — M4 (doc-vs-implementation parity: table refs at docstring L30-34, real sites L201-208); B1 (table omits coupling classes 2+4); APED-1 (M3: execute the pathspec-under-routing behavior, don't reason it); B2 (pre-existing `relative_to`/`except ValueError` branch composes incorrectly with the new routed `out_path`).

## Triage

**Triaged by**: user
**Date**: 2026-06-01
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (first Critic + critique-review meta-Critic EXTEND). User ratified all Builder drafts as-is (no overrides, no deferrals). Design-level fixes applied pre-triage to design.md (r3) + ADR-089 (r2); ACCEPTED-PENDING items are test-realization work for /build-slice.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §coupling-model — two-literal-class (Class-A filesystem / Class-B git-string); AC1 reworded in mission-brief |
| B2 | Blocker | ACCEPTED-PENDING | design.md places SOFT-resolution write path under RETIRE-when-untracked, guard at resolve-entry before out_path; refuse-before-relative_to test at /build-slice |
| M1 | Major | ACCEPTED-FIXED | ADR-089 r2 §Decision — precise `git ls-files --error-unmatch` tracked-check replaces the proxy as binding gate; proxy demoted to optional fast-path |
| M2 | Major | ACCEPTED-FIXED | tracked-check dissolves the env-set-before-flip stranding window (ADR-089 r2 §Consequences); actionable breadcrumb added to must-not-defer |
| M3 | Major | ACCEPTED-PENDING | design.md — git-string positions never routed (stay forward-slash repo-relative); APED-1 execute-on-runtime test at /build-slice |
| M4 | Major | ACCEPTED-FIXED | design.md per-site table corrected (L201-203 ls-tree + L206-208 show both RETIRE; L322/L327 fallbacks ROUTE); test-both-refuse is ACCEPTED-PENDING |
| M5 | Major | ACCEPTED-FIXED | design.md §AST-predicate — precise Class-A predicate + allowlist; test + mutation non-vacuity ACCEPTED-PENDING |
| m1 | Minor | ACCEPTED-PENDING | add `_AUDIT_LOG_PATH` (5 consumers) to the no-flip byte-identity test surface at /build-slice |
| m2 | Minor | ACCEPTED-FIXED | design.md §Error model — RETIRE diagnostics via `_vault_paths._stderr`, call-time not import-time |
| M-add-1 | Major | ACCEPTED-FIXED | design.md r3 — diagnose-time reads (L216-217) protected by U-file-absence→UNKNOWN fall-through (NOT resolve-entry guard); NO redundant guard added; call-spy unreachability test ACCEPTED-PENDING |
| M-add-2 | Major | ACCEPTED-FIXED | design.md r3 — stranded archive_path/milestone_path materialized twice (forward-slash git pathspec + VAULT_ROOT-routed Path); test-both-branches ACCEPTED-PENDING |
| M-add-3 | Major | ACCEPTED-FIXED | design.md r3 §AST-predicate — def-use reach through one local-variable assignment; variable-mediated (L322) mutation target for the non-vacuity proof |
