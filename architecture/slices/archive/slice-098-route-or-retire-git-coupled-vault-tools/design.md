# Design: Slice 098 route-or-retire-git-coupled-vault-tools

**Date**: 2026-06-01
**Mode**: Standard
**Revision**: r3 — r2 substantially revised after `/critique` (B1/B2/M1–M5 ACCEPTED-FIXED); r3 adds the three `/critique-review` meta-findings (M-add-1/2/3 ACCEPTED-FIXED). The keystone change: the binding RETIRE signal is a **precise per-pathspec git-tracked check** (`git ls-files --error-unmatch`), NOT the `VAULT_ROOT_IS_DEFAULT` resolution proxy; and vault coupling is modelled as **two literal classes** (filesystem-path vs git-string identity), not one. r3 refines WHERE each Class-B read is actually protected (the diagnose-time reads vs the equivalence-guard reads have different guards — M-add-1), the dual-class single-variable case (M-add-2), and the AST predicate's def-use reach (M-add-3).

## The coupling model (two literal classes)

Each of the 3 tools references the vault in **two structurally different ways**, and they need opposite treatment:

- **Class A — filesystem-path literals**: a string used as an operand to `Path.__truediv__` against a runtime `repo_root`/`scan_root` (e.g. `repo_root / "architecture" / "slice-queue.md"`). → **ROUTE** through `VAULT_ROOT`: `<root> / VAULT_ROOT / <subpath>` (pathlib discards `<root>` when `VAULT_ROOT` is absolute, so one form serves the relative-default and absolute-external cases; byte-identical on the no-flip path because `VAULT_ROOT == Path("architecture")`).
- **Class B — git-string identities**: a forward-slash repo-relative string used as (i) a `git status --porcelain` U-file comparison key (`_SOFT_FILE_SET`), (ii) a `git show :N:<pathspec>` / `git show <branch>:<pathspec>` / `git ls-tree … -- <pathspec>` pathspec, (iii) a `git add <pathspec>` argument, or (iv) the equivalence-guard `qrel`/`srel` comparison keys + `regenerated_files`. These are **git-tracked-path identities**. They MUST stay forward-slash repo-relative literals (a `VAULT_ROOT`-composed `Path` is backslash-separated on Windows and absolute when external — feeding it into an f-string pathspec like `f":{stage}:{path}"` produces a malformed `git show :2:C:\…\slice-queue.md`, and `git add <abs-external>` escapes the work tree). Class B is therefore **never routed**; instead it is **governed by the tracked-check RETIRE guard** below.

This corrects the r1 design, which treated all coupling as Class A and so silently omitted PCR's `_SOFT_FILE_SET` membership, `git add` pathspecs, `regenerated_files`, and the equivalence-guard `qrel`/`srel` keys (Critic B1), and mis-located the stranded git-tree sites (Critic M4).

## The RETIRE guard: precise git-tracked check (not the resolution proxy)

> **AS-BUILT (slice-098, USER-RATIFIED — supersedes the r2 per-pathspec tracked-check below; see ADR-089 §Decision + build-log DEVIATION 2026-06-02):** the binding RETIRE signal is the **store-LOCATION** check `tools/_vault_git.vault_is_external(repo_root)` (True iff `VAULT_ROOT` resolves OUTSIDE the repo work tree), used UNIFORMLY by PCR + stranded. The per-pathspec `git ls-files` tracked-check proved unsound twice in build: (1) PCR — it returns True for the still-tracked in-tree `slice-queue.md` in the external-`VAULT_ROOT`-but-not-moved window, MISSING the B2 corruption; (2) stranded — a stranded slice's vault content lives only on its branch, so the tracked-check over-RETIRES every in-tree stranded slice (4 existing fixtures). `vault_is_external` catches B2 (external-abs → RETIRE before `out_path`) and passes the fixtures (in-tree → proceed). `vault_pathspec_is_tracked` is retained in `_vault_git.py` (tested) as a precise primitive for the flip slice. The original tracked-check rationale (below) is preserved for the decision record.

The r2 binding signal was "is this vault pathspec git-tracked?" — `git ls-files --error-unmatch <forward-slash-pathspec>` (returncode 0 = tracked). It **replaced** the `VAULT_ROOT_IS_DEFAULT` proxy as the binding gate (Critic M1):

- The proxy conflated "resolution fell through to default" with "git-untracked" — wrong for a transitional config where the vault is relocated to an absolute path still **inside** the tracked tree (proxy says non-default → would over-RETIRE a perfectly-resolvable git-show). [As-built note: `vault_is_external` handles this case too — under repo_root → not external → proceed.]
- It fires **exactly when no git rebase/branch conflict can arise** (an untracked file has no rebase stage and is absent from a branch tree), so it never strands a *real* conflict in the env-set-but-still-tracked window (Critic M2). [As-built: `vault_is_external` preserves this — in-tree → proceed.]

`VAULT_ROOT_IS_DEFAULT` (a frozen boolean on `_vault_paths.py`) is retained ONLY as an optional cheap fast-path / observability aid, never as the sole gate.

**RETIRE-when-untracked** (renamed from r1's "RETIRE-when-external") sites fail **visibly** and **before** composing any filesystem write path: the guard fires at entry to the resolution function, prior to any `out_path` / `relative_to(repo_root)` composition, so the equivalence-guard `qrel`/`srel` comparison is never reached with a non-comparable path (Critic B2 — an external absolute `out_path` would otherwise raise `ValueError` at `relative_to`, fall through to the full external path, never equal `qrel`, and silently skip the claim-preservation invariant).

**Two Class-B read-site groups in PCR have DIFFERENT protections (Critic M-add-1 — the r2 guard-placement claim was control-flow-imprecise):**
1. **Equivalence-guard reads** — `_git_show_stage(repo_root, N, qrel/srel)` at L1967-1968/2056-2057, plus the `out_path` write path — fire INSIDE `resolve_soft_conflict`/`resolve_vault_claim_conflict`. These are protected by the **resolve-entry tracked-check** (above): the guard at the resolution-function entry refuses before they compose `out_path`/`relative_to`.
2. **Diagnose-time reads** — `_git_show_stage(repo_root, 2/3, "architecture/slice-queue.md")` at L216-217 — fire INSIDE `diagnose_conflict` (L193), which `main` calls **unconditionally at L2287, UPSTREAM of `resolve_soft_conflict` and even `classify_conflict`**. A resolve-entry guard CANNOT reach them. Their binding protection is the **empty-U-file → UNKNOWN fall-through**, which the design now states explicitly: an untracked vault is not git-tracked → `git status --porcelain` (the `_extract_u_files` source, L770-819/L781-788) never emits `architecture/slice-queue.md` as a U-file → `diag.u_files` excludes it → `classify_conflict` returns UNKNOWN (L277-278) → the L216-217 branch (gated on `"architecture/slice-queue.md" in u_files`, L212) is **never entered**, so no diagnose-time `_git_show_stage` ever fires on an untracked vault. **Deliberately NOT adding a redundant tracked-check at `diagnose_conflict` entry** (per the meta-Critic's own caution): the U-file-absence proof makes the read structurally unreachable, so a second guard would be dead code. **AC5 enforcement (build):** a test asserts that with an untracked vault, the live `diagnose_conflict` produces zero vault U-files and L216-217's `_git_show_stage` is never called (e.g. via a call-spy) — pinning the unreachability rather than reasoning it (APED-1).

## What's new

- `VAULT_ROOT_IS_DEFAULT` frozen boolean on `tools/_vault_paths.py` (optional fast-path only; leaf-safe, stdlib-only, read once at import). **Not** the binding RETIRE gate.
- A `_vault_pathspec_is_tracked(repo_root, pathspec) -> bool` helper (exact home a build detail — local to each tool, or a shared `tools/_vault_git.py`; NOT the leaf `_vault_paths`, which must not gain a repo_root-dependent git call) — `git ls-files --error-unmatch`, bytes-captured + main-thread decode per the R-30/slice-091 pattern, `encoding`-safe.
- Class-A routing in all 3 tools: filesystem vault-path composition → `<root> / VAULT_ROOT / <subpath>`.
- A fail-visible **RETIRE guard** at every Class-B git-tree vault-content read + the SOFT/VAULT_CLAIM resolution entry: when the pathspec is untracked, raise a typed error → explicit STOP + audit breadcrumb (with an **actionable operator message** naming the post-flip manual-resolution path / the flip tracking slice — Critic M2), never a falsy/empty result.
- New ADR [[ADR-089]] (r2) recording the two-literal-class model + tracked-check signal + residual.
- New tests: external-root flip-readiness (subprocess env-injection), no-flip byte-identity (incl. `_AUDIT_LOG_PATH` surface — m1), RETIRE fail-visibility via the **tracked-check** (refuse-before-`relative_to`; both stranded git-tree helpers; PCR SOFT/VAULT_CLAIM entry), an **APED-1 execute-on-runtime** test that a routed/untracked pathspec never reaches git malformed, and a **precisely-predicated** AST source-scan (Class-A absence only) proven non-vacuous by mutation.

## What's reused

- [[decisions/ADR-065]] + [[decisions/ADR-085]] — the `VAULT_ROOT` 3-tier resolution seam (`tools/_vault_paths.py`).
- The **consumer-freeze + subprocess-test discipline** (slice-093) — `tools/_vault_paths.py` docstring §"Read-at-import + consumer-freeze cascade" + `tests/methodology/test_vault_root_constant.py::test_consumer_constants_are_frozen_at_first_import`. External-root tests MUST inject `AI_SDLC_VAULT_ROOT` at a **subprocess** boundary; in-process `monkeypatch.setattr` does NOT propagate to frozen consumer constants.
- `tools/_vault_paths._stderr` — the cp1252-safe stderr helper for the new RETIRE diagnostics (call-time, never import-time — m2).
- The byte-mode-`subprocess.run` + explicit main-thread `.decode("utf-8")` pattern in `tools/parallel_conflict_resolver._git_show_stage` (slice-091/R-30) — the new `git ls-files` tracked-check follows it; no new git subprocess lacks `encoding`/byte-decode (BC-GLOBAL-5).
- [[slice-093-add-external-vault-support]] AC4 ("migrate-NONE") — this slice executes the deferred rethink of exactly these 3 tools.

## Components touched

### `tools/_vault_paths.py` (modified)
- **Responsibility**: vault-root resolution seam. Adds the optional frozen `VAULT_ROOT_IS_DEFAULT`. Leaf-purity preserved (stdlib only). The tracked-check helper does NOT live here (it needs `repo_root` + git; keeping it out preserves leaf-purity).

### `tools/pulse_worktree_resolver.py` (modified) — Class-A ROUTE-only + KEEP
- **Change**: ROUTE the milestone.md filesystem reads (`scan_root / "architecture" / "slices" / … / milestone.md`, L217/L220) through `VAULT_ROOT`. **KEEP** worktree-porcelain git reads (tracked worktrees/refs, not vault content). No Class-B vault-content git reads → no RETIRE guard needed here.

### `tools/stranded_slice_audit.py` (modified) — Class-A ROUTE + Class-B RETIRE + KEEP
- **Change**: (ROUTE) the filesystem reads — `repo_root / "architecture" / "slice-queue.md"` (L166), `… / "architecture" / "slices"` (L369), and the **secondary filesystem fallbacks** `(repo_root / archive_path).exists()` (L322) + `repo_root / milestone_path` (L327) — through `VAULT_ROOT`. (KEEP) the `slice/*` branch enumeration + classification + worktree mapping. (RETIRE-when-untracked) **BOTH** bare-branch git-tree vault-content reads: `_branch_tree_has_path` (L201-203, `git ls-tree {branch} -- {path}`) AND `_branch_tree_file` (L206-208, `git show {branch}:{path}`) — fed `archive_path`/`milestone_path` at L302/L308. If only `show` were guarded, `_branch_tree_has_path(... archive_path)` (L302) would silently return `False` for an untracked vault → STRANDED-COMPLETE archive detection silently dropped (AC5 violation). Both helpers' callers gate on the tracked-check.
- **Dual-class single-variable split (Critic M-add-2)**: `archive_path`/`milestone_path` are EACH consumed in BOTH a Class-B git-pathspec position (`_branch_tree_has_path`/`_branch_tree_file`) AND a Class-A filesystem position (`(repo_root / …).exists()` / `repo_root / …`). One string object cannot be both routed and kept forward-slash, so the build **materializes two derivations** from each. **AS-BUILT (refines the r3 "verbatim literal" prescription per /code-review M2 — the derivation below is MORE correct):** (i) the git pathspec = `(VAULT_ROOT / "slices" / "archive" / f"slice-{num}-{name}").as_posix()` — a forward-slash string DERIVED from VAULT_ROOT (NOT a verbatim `architecture/…` literal). Sound because: a RELATIVE VAULT_ROOT (in-tree default OR external-but-tracked `<repo>/vault/`) yields a valid forward-slash pathspec that correctly points at where the branch-tree content actually lives (a verbatim `architecture/…` literal would MISS the relocated-but-tracked case); an ABSOLUTE external VAULT_ROOT never reaches these reads because the `vault_is_external` guard RETIREs first. (ii) the filesystem path = `repo_root / VAULT_ROOT / "slices" / "archive" / f"slice-{num}-{name}"` (Class-A routed). The two are SEPARATE objects (`.as_posix()` string vs `Path`), byte-identical on the no-flip default. A test exercises the external path through BOTH branches (git pathspec governed by the `vault_is_external` RETIRE; filesystem fallback resolves under the external root).

### `tools/parallel_conflict_resolver.py` (modified) — the load-bearing case
- **Class-A ROUTE**: `_AUDIT_LOG_PATH = Path("architecture/parallel-conflict-resolution-log.md")` (L71, consumed `repo_root / _AUDIT_LOG_PATH` at L681/735/1759/2105/2149), `out_path` writes (L1061/1544/1838), `slices_dir` walk (L889).
- **Class-B (tracked-guarded, never routed)** — the whole SOFT/VAULT_CLAIM git-rebase-conflict mechanism is inapplicable to an untracked vault: `_SOFT_FILE_SET` U-file comparison keys (L57-60, used L212/281-282/293/365/1340/2198), `_git_show_stage` rebase-stage reads (L216-217/1016-1017/1476-1477/1798-1799 + `qrel`/`srel`-derived L1967-1968/2056-2057), the equivalence-guard `qrel` (L1965)/`srel` (L2054) keys, `git add` pathspecs (`*regenerated` L436; `"architecture/slice-queue.md"` L1549) + `regenerated_files` (L1565/1575). The RETIRE guard fires at **entry** to `resolve_soft_conflict` / `resolve_vault_claim_conflict` (before any `out_path`/`relative_to` composition) with an actionable STOP breadcrumb.
- **KEEP**: all git rebase/diff/worktree plumbing on tracked refs.
- `_vault_write` lock untouched (the post-flip write-race owner; wiring it as the conflict-mechanism replacement is the flip slice's job — out of scope).

## Per-site table (AC2 deliverable — class-annotated, line refs verified against disk)

| Tool | Site(s) | Literal class | Decision | Post-flip behaviour |
|------|---------|---------------|----------|---------------------|
| pulse_worktree_resolver | `scan_root / architecture / slices / … / milestone.md` (L217/220) | A | ROUTE | reads via `VAULT_ROOT` |
| pulse_worktree_resolver | worktree porcelain git reads | — (git refs) | KEEP | unchanged |
| stranded_slice_audit | `repo_root / architecture / slice-queue.md` (L166), `… / slices` (L369), filesystem fallbacks (L322, L327) | A | ROUTE | reads via `VAULT_ROOT` |
| stranded_slice_audit | `slice/*` branch enumeration + classification | — (git refs) | KEEP | unchanged |
| stranded_slice_audit | `_branch_tree_has_path` ls-tree (L201-203) + `_branch_tree_file` show (L206-208), callers L301/L307 | B | RETIRE-when-untracked | both refuse visibly via tracked-check |
| parallel_conflict_resolver | `_AUDIT_LOG_PATH` (L71→L681/735/1759/2105/2149), `out_path` writes (L1061/1544/1838), `slices_dir` (L889) | A | ROUTE | reads/writes via `VAULT_ROOT` |
| parallel_conflict_resolver | `_SOFT_FILE_SET` U-file keys (L57-60), `_git_show_stage` pathspecs (L216-217/1016-1017/1476-1477/1798-1799/1967-1968/2056-2057), `qrel`/`srel` (L1965/2054), `git add` (L436/L1549) + `regenerated_files` (L1565/1575) | B | RETIRE-when-untracked | guard at resolve-entry → STOP + actionable breadcrumb; never `git show :N:`/`git add` an untracked path |
| parallel_conflict_resolver | git rebase / diff / worktree plumbing on tracked refs | — (git refs) | KEEP | unchanged |

## Contracts added or changed

No HTTP/event contracts. One behavioural-contract change: every Class-B git-tree vault-content read + the SOFT/VAULT_CLAIM resolution entry gain a **precondition** — only exercised when the vault pathspec is git-tracked; otherwise fail visibly (typed error → STOP). Enforced in code + pinned by tests (AC2/AC5).

## Data model deltas

None.

## Wiring matrix

Per **WIRE-1**. If the tracked-check helper lands as a new module (`tools/_vault_git.py`), it gets a row; if it lands as a local helper in each tool (no new file), the matrix stays zero-row. Default: local helper (no new module) → zero-row clean. Decided at build; if a shared module is introduced, add:

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_vault_git.py` (only if extracted) | `tools/parallel_conflict_resolver.py` + `tools/stranded_slice_audit.py` | `tests/methodology/test_vault_pathspec_tracked.py::test_untracked_pathspec_refuses` | — |

## AST/source-scan predicate (AC1 verification — Critic M5)

The scan pins absence of an `architecture` / vault string literal **only in Class-A positions**: a string-constant used as an operand of `Path.__truediv__` (`/`) against a `repo_root`/`scan_root`-derived `Path`. It **allowlists** (i) docstring/comment occurrences and (ii) the named Class-B git-identity literals (`_SOFT_FILE_SET` members, `git add` args, `regenerated_files`, `_git_show_stage`/`_branch_tree_*`/`ls-tree` path args, `qrel`/`srel`) which are correct to keep forward-slash.

**Def-use reach (Critic M-add-3):** the predicate must follow Class-A through **one level of local-variable assignment** — a `Name` operand of `Path.__truediv__` whose binding is an `architecture/…` f-string/str-literal earlier in the same function (the real shape at stranded `archive_path` L301 → `(repo_root / archive_path)` L322, and PCR `qrel = "architecture/slice-queue.md"` L1965). A predicate matching only a literal *directly* in the `/` operand position (`repo_root / "architecture" / "x"`) would FALSE-NEGATIVE the variable-mediated site — re-introducing the M5 vacuity it exists to close. The allowlist disambiguates the L301-style f-string: it is Class-A (must be split per M-add-2 into a routed Path + a kept git string), not a bare docstring/identity.

Proven **non-vacuous by mutation** (slice-092 lesson) using a **variable-mediated** target: re-introduce an un-routed `repo_root / archive_path`-style (variable-mediated) Class-A site, confirm the scan FAILS, revert — NOT only a direct-literal mutation, or the non-vacuity proof is itself vacuous for the hardest real case. A naive `grep architecture` (false-fails on docstrings) and a blanket AST string-constant scan (false-fails on Class-B) are both explicitly rejected.

**Scope of the AC1 guarantee (narrowed per /code-review M1 — honest bound):** the scan covers Class-A composition via `Path.__truediv__` (`/`) ONLY, with **one-hop** local-variable def-use. It does NOT detect Class-A introduced via (a) `Path.joinpath("architecture", …)`, (b) `os.path.join(repo_root, "architecture", …)`, or (c) a **two-hop** alias chain (`a = "architecture/x"; b = a; repo_root / b`). All three currently return no finding. This is acceptable for the as-built diff — the 3 migrated tools use NONE of these shapes (Grep-verified: no `joinpath`/`os.path.join` in any Class-A position) — but the guarantee is "no un-routed `Path / 'architecture'` div-form, one-hop alias", NOT "no Class-A literal by any construction". A future regression introduced via `joinpath`/2-hop would pass silently. Closing this (transitive `marked_names` + `joinpath`-Call detection) is a named residual for the flip slice / a bundled-cleanup; it is latent-not-active.

## Decisions made (ADRs)

- [[ADR-089]] (r2) — two-literal-class routing; precise git-tracked-check RETIRE signal; KEEP git ops on tracked `slice/*` refs + worktrees — reversibility: **cheap**.

## Authorization model for this slice

N/A — local developer tooling, no multi-user surface, no network.

## Error model for this slice

- **RETIRE-when-untracked** sites fail *visibly*: a typed exception → explicit STOP (PCR) / typed audit result (stranded), each with a one-line reason **plus an actionable operator breadcrumb** (Critic M2: name the post-flip manual-resolution procedure / the flip tracking slice) via the cp1252-safe `tools/_vault_paths._stderr` / the tool's existing audit-breadcrumb path. Diagnostics fire at **call-time, not import-time** (m2). **Never** a falsy/empty/`None` silent result (R-7 silent-disable + slice-090/091 silent-claim-drop class).
- **No-flip path** (default `architecture/`, vault git-tracked): zero new error states — byte-identical to pre-slice (the tracked-check returns 0 → every current path runs unchanged).
