# Slice 098: route-or-retire-git-coupled-vault-tools

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (concurrent-write lost-update on a shared mutable vault) — *partial*: this is the last capability piece before the external-vault flip; R-32 stays `mitigating` and retires at the flip slice.
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The external-shared-vault initiative is now unblocked on write-safety (slices 094/095/097 closed all three R-32 write-safety sub-classes). The last capability piece before the flip is the 3 tools slice-093 deliberately declined to migrate (AC4 "migrate-NONE"): `parallel_conflict_resolver`, `stranded_slice_audit`, and `pulse_worktree_resolver`. Each hardcodes `architecture/` vault paths and each is git-coupled — most deeply `parallel_conflict_resolver`, which reads rebase stages via `git show :N:architecture/slice-queue.md` (a mechanism that cannot read a stage for an *untracked* file once the vault relocates). This slice routes each tool's vault-path resolution through the `_vault_paths` seam (ADR-065/085) and makes an explicit ROUTE / RETIRE / KEEP decision for every git-coupling site that touches vault *content* — **without flipping the default** (vault stays `architecture/`; the no-flip safety contract from slices 093/094 is the binding invariant). The scary, irreversible flip (physical move + git-untrack + prose) remains a separate later slice; this one proves the 3 tools are flip-ready.

## Acceptance criteria

1. **Class-A vault-path routing** — all 3 tools resolve every **filesystem** vault-file path (the Class-A literals: PCR audit log + `out_path` writes + `slices_dir`; stranded `slice-queue.md` + `slices` + the filesystem fallbacks; pulse `milestone.md` reads) through the `_vault_paths` seam (`<root> / VAULT_ROOT / <subpath>`); no hardcoded `architecture/<vault-content>` literal remains in a **Class-A filesystem-composition position** (operand to `Path.__truediv__` against a runtime `repo_root`/`scan_root`). Class-B git-string identities (porcelain U-file keys, git pathspecs, `git add` args, `qrel`/`srel`) deliberately stay forward-slash repo-relative literals (governed by AC2's tracked-check, NOT routed). Verified by a precisely-predicated AST/source-scan test (Class-A positions only; mutation-proven non-vacuous) + execution.
2. **Git-coupling classified & enforced** — every git-coupling site in the 3 tools is classified into the two-literal-class model (ROUTE / RETIRE-when-untracked / KEEP) in design.md + ADR-089, with the load-bearing cases (PCR's `_SOFT_FILE_SET` keys + `git show :N:` rebase-stage reads + `git add` pathspecs + the equivalence-guard `qrel`/`srel`; stranded's `_branch_tree_has_path` ls-tree + `_branch_tree_file` show) given an explicit decision. The binding RETIRE signal is a **precise per-pathspec `git ls-files --error-unmatch` tracked-check** (not the resolution proxy), enforced by a test. (Branch-classification + worktree-porcelain reads on git-tracked `slice/*` refs — not vault content — are documented KEEP.)
3. **External-root flip-readiness** — with `AI_SDLC_VAULT_ROOT` set to an external **untracked** directory, each of the 3 tools locates its Class-A vault files in that external root, and the Class-B git-tree reads RETIRE visibly (the tracked-check fires). A test sets the env var (at a **subprocess** boundary, per the consumer-freeze cascade) and asserts both behaviours for all 3 tools.
4. **No-flip safety contract** — with the env unset (default `architecture/`, vault git-tracked), the full test suite passes unchanged and all 3 tools behave byte-identically to their pre-slice output on the live repo (incl. the `_AUDIT_LOG_PATH` surface). The same hard invariant slices 093/094 used.
5. **No silent misbehavior on the RETIRE cases** — wherever a Class-B git-tree vault-content read is genuinely inapplicable to an untracked vault, the tool fails *visibly* (typed error / explicit STOP with an **actionable operator breadcrumb**) **before** composing any `out_path`/`relative_to`, and never silently drops a claim or returns a false-clean. Pinned by a test (R-7 silent-disable + slice-090/091 silent-claim-drop class).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Vault-path routing | `$PY -m pytest` on the new routing test; `grep -nE "architecture/(slice-queue\|shippability\|slices)" tools/{parallel_conflict_resolver,stranded_slice_audit,pulse_worktree_resolver}.py` shows no runtime-path literals (only docstrings/comments, if any, justified) |
| 2 | Git-coupling classified & enforced | design.md carries a per-site ROUTE/RETIRE/KEEP table; new ADR records the `git show :N:` decision; a test pins the chosen behavior (e.g. asserts the RETIRE path raises/STOPs, or the ROUTE path reads via the new mechanism) |
| 3 | External-root flip-readiness | a test sets `AI_SDLC_VAULT_ROOT=<tmp external dir>`, seeds vault fixtures there, and asserts each of the 3 tools reads/writes the external location (not `architecture/`) |
| 4 | No-flip safety contract | `$PY -m pytest` full suite green (env unset); capture each tool's stdout on the live repo before vs after — byte-identical (CRLF-normalized) |
| 5 | No silent misbehavior | a test drives each RETIRE site with an external/untracked-vault condition and asserts a *visible* failure (typed exception / non-zero exit / explicit STOP audit row), never a falsy/empty silent result |

## Must-not-defer

- [ ] **Fail-visible on RETIRE** — no silent disable / claim-drop / false-clean when a Class-B git-tree path is inapplicable to an untracked vault (R-7 silent-disable class; the slice-090/091 PCR silent-claim-drop family). The guard fires **before** any `out_path`/`relative_to` composition (the equivalence-guard `qrel`/`srel` comparison must not be reached with a non-comparable external path — `/critique` B2).
- [ ] **Actionable RETIRE breadcrumb** — every RETIRE STOP carries an operator-actionable message naming the post-flip manual-resolution procedure / the flip tracking slice, so a refused `/commit-slice --merge` is recoverable, not a dead-end (`/critique` M2).
- [ ] **Concurrency invariants preserved** — routing must not weaken the in-tree `_vault_write` sidecar-lock or the PCR conflict-resolution invariants (R-32 mitigation stays intact on the default path).
- [ ] **Encoding discipline** — any git subprocess added/moved in these tools passes `encoding="utf-8"` (BC-GLOBAL-5 / cp1252 class N≥7); no new bare `print()` at import (RSAD-1).
- [ ] **No-flip invariant is binding** — any behavior change on the default `architecture/` path is a deviation requiring an ADR.
- [ ] **Logging** — the ROUTE/RETIRE decisions surface in each tool's audit/observability output where one exists, not silently.

## Out of scope

- The actual flip — physical move of `architecture/`, git-untrack, prose rewrite, history considerations (the LARGE `flip-vault-to-external-shared-root` slice, 099+).
- Changing the default vault root — it stays `architecture/` (no-flip).
- Building the *external-vault replacement* conflict-avoidance mechanism for any RETIRE case (e.g. a `_vault_write`-lock-based substitute for PCR's git-rebase-stage reads) — this slice classifies + guards + proves path-readiness; constructing the post-flip replacement is the flip slice's job unless the design finds it trivially in-scope.
- Per-worktree install isolation (R-28 / R-29) — separate slice.
- `slice_queue_claim.py` / `slice_queue_writer.py` and other vault writers already routed by slices 093–097 — only the 3 named git-coupled tools are in scope here.

## Dependencies

- Prior slices: [[slice-093-add-external-vault-support]] — supplies `_vault_paths` (3-tier `AI_SDLC_VAULT_ROOT` → git-config → `architecture/` precedence) + `_vault_write`, and explicitly deferred these exact 3 tools ("rethought at the flip, not naively migrated"). [[slice-094-harden-vault-write-safety]] / [[slice-095-harden-skill-driven-vault-writes]] / [[slice-097-harden-skill-driven-vault-rewrites]] — closed the 3 R-32 write-safety sub-classes that unblock this work.
- Vault refs: [[decisions/ADR-065]] (vault-root resolution seam), [[decisions/ADR-085]] (extends it + `_vault_write`).
- Risk register: [[risk-register#R-32]] — this slice advances R-32 toward retirement-at-flip; it does NOT retire it.

## Mid-slice smoke gate

At ~50% of build (after the first tool — start with the path-coupling-only `pulse_worktree_resolver` or `stranded_slice_audit`, leaving the deep `parallel_conflict_resolver` for second):
```
$PY -m pytest tests/ -k "<first_tool>" -q
$PY -m tools.<first_tool> <its normal invocation>   # env unset → identical to pre-slice output
$PY -m pytest tests/ -k "external_root or vault_root" -q   # the new flip-readiness test for that tool
```
Expected: targeted tests green; live-repo output byte-identical with env unset; the external-root test passes for the routed tool. If the no-flip invariant breaks (output differs with env unset): STOP, diagnose, don't continue.

## Pre-finish gate

- [ ] All 5 acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Full suite green with `AI_SDLC_VAULT_ROOT` unset (no-flip contract)
