---
id: ADR-091
title: Vault-flip readiness is audited by AST-classifying in-tree-vault-location literals on the production-.py surface into a 4-class taxonomy
date: 2026-06-02
slice: slice-100-add-vault-flip-readiness-audit
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-091: Vault-flip readiness classification model + production-`.py` scan scope

## Context

The external-vault flip ([[external-shared-vault-initiative]]; [[ADR-085]] / [[ADR-089]]) relocates `architecture/` + `diagnose-out/` to a shared external store, flips the `tools/_vault_paths.VAULT_ROOT` default, and git-untracks the vault. It must land **atomically**: any hardcoded in-tree-vault-location path literal that is *not* routed through `VAULT_ROOT` (and not a deliberate, retire-guarded [[ADR-089]] Class-B git-string) **silently mis-resolves** the moment the vault moves. A single missed literal is a silent post-flip defect.

The active surface holds ~760 such literals (`tools/` ~120, `tests/` ~382, `skills/**/SKILL.md` ~260, `agents/`/`CLAUDE.md`/`INSTALL.md` ~23). Hand-grepping that is error-prone, and there is no regression guard preventing a *future* slice from adding a fresh unrouted literal. This slice (the flip's reversible first cut, mirroring slice-093 *capability-without-flip*) needs a deterministic, complete, regression-pinned inventory — **without flipping the repo**.

## Options considered

1. **Full-surface classification (tools + tests + skills-prose + agents + root docs).** Pro: one complete checklist. Con: ~760 occurrences; **prose (`SKILL.md`) is not reliably auto-classifiable** into must-rewrite-vs-doc (AI-hard judgement — a prose instruction "read `architecture/X`" reads identically to an illustrative mention); **tests are noisy** (many literals are *intentional* seam/migration constants, and tests break *loudly* anyway). LARGE; fails the ≤1-day scope check; risks dangerous under-flagging on prose if coarse-defaulted.
2. **Production-`.py`-only AST classification (CHOSEN).** Scan `tools/**/*.py` + skill-helper `skills/**/*.py`. Pro: this is the **silent-breakage** surface (a tool mis-resolving a path fails quietly, unlike a failing test); Python `ast` + `tokenize` make classification **deterministic and reliable** (executable string literal vs comment vs docstring vs `argparse help=`); the slice-098 Class-B marker is already a stable parseable signal; comfortably ≤1 day. Con: defers the tests + prose surfaces (acceptable — see Consequences).
3. **Regex-only scan (no AST).** Pro: trivial. Con: cannot distinguish an executable string literal from a comment/docstring/help-string → noisy and imprecise; directly contradicts the project's repeated **APED-1 / BC-PROJ-13** lesson that regex content-classification ships false-positives/negatives caught only by execution. Rejected.

## Decision

Ship `tools/vault_flip_readiness_audit.py`: a read-only audit that scans **`tools/**/*.py` + `skills/**/*.py`** for `architecture/` and `diagnose-out/` path literals and classifies **each occurrence** via `ast` + `tokenize`. Classification is **context-aware, not node-type-only** (the B1/M1 correction — a vault literal inside a diagnostic message string is an `ast.Constant` str but is *not* a path the code resolves; node-type alone over-flags it `must-rewrite`).

**Match rule (M1 + B-add-1)** — an occurrence is a `tokenize` COMMENT token OR an `ast.Constant` str whose **value** contains the vault path segment `architecture` or `diagnose-out`, matched **both** as a slashed prefix `(?:^|[\s'"(/=])(?:architecture|diagnose-out)/` **and** as a bare whole-segment literal equal to `"architecture"` / `"diagnose-out"` (no slash). The trailing-slash form alone is **NOT** the gate (B-add-1: a bare `"architecture"` operand of `repo_root / "architecture" / "X"` is the most classic silent path mis-resolve and MUST be caught). The audit's own source line bearing this regex is self-excluded by path (`tools/vault_flip_readiness_audit.py`). **Whether a matched literal is breakage is decided by CONTEXT (the ordered ruleset below), NOT by the slash**: a bare segment NOT in any path/git context (e.g. `_DERIVED_DIRS = ("diagnose-out", "graphify-out")`, a config tuple) falls to rule 5 (`doc-example-safe`); a bare segment IN a path-construction context (rule 3) is `must-rewrite`.

**Classification — an ordered ruleset, first applicable wins** (per matched occurrence):

1. **`doc-example-safe`** if the occurrence is a `tokenize` COMMENT, a module/class/function **docstring**, an `argparse` `help=`/`description=` kwarg value, OR sits on a line carrying the slice-068 **error-message-prose marker** (`# … — error-message prose`, em-dash variant). Non-executing or seam-acknowledged prose → no path resolution.
2. **`already-seam-routed`** elif: the line carries the [[ADR-089]] **Class-B marker** `Class-B git identity (ADR-089)`; OR the file is the seam itself (`tools/_vault_paths.py` `_DEFAULT`, `tools/_vault_git.py`); OR the literal co-occurs with `VAULT_ROOT` on the same logical line (Class-A `VAULT_ROOT / "…"`). Retire-guarded or VAULT_ROOT-derived → will not silently break.
3. **`must-rewrite-before-flip`** elif the constant literal (bare segment **or** slashed prefix) sits in a **path-construction context** (≤1-hop usage analysis, mirroring VWS-1 `_resolve_target`): an arg to `Path(...)`/`PurePath(...)`; an operand of a `/` `BinOp` (**includes a bare `"architecture"`/`"diagnose-out"` operand of `repo_root / "architecture" / "X"` — the B-add-1 site shape**); the receiver/arg of `.open`/`.read_text`/`.write_text`/`.read_bytes`/`.glob`/`.iterdir`/`.exists`/`.joinpath`; or assigned to a local name that flows (≤1 hop) into one of those. The silent-breakage set the flip must route through `VAULT_ROOT`.
4. **`needs-human-classification`** (fail-closed) elif the occurrence is genuinely ambiguous: an **unmarked git-pathspec** literal — a path-string consumed by a `git` subprocess command or a member of a git-pathspec `frozenset`/`tuple`/`list` (e.g. PCR's `_SOFT_FILE_SET`) that carries no Class-B marker (the human decides rewrite-vs-Class-B); a **dynamic-fragment** (only a fragment is constant, the rest composed via f-string/`+`/`.format()` and it flows into a path/git context); or a **parse-error** file (`SyntaxError` → one entry per file).
5. **`doc-example-safe`** (reason `prose-mention`) else — a matched executable string in no path/git context (a bare diagnostic/message string). At worst cosmetically stale post-flip; never a silent path mis-resolve.

**Determinism**: inventory sorted by `(path, line, col)`; identical input → byte-identical output.

**Documented residual (slice-095 honest-contract — named in code + a test, not silently assumed closed)**: a vault path assembled fully dynamically with **no** `architecture`/`diagnose-out` string-literal segment anywhere (e.g. a dir name built character-by-character) is invisible to a static scan. (B-add-1 **retired** the former residual (ii): bare directory-name literals ARE now matched and classified by context — a bare segment in a path-construction is `must-rewrite`, a bare segment in a config tuple / prose is `doc-example-safe`.) The residual is recorded in the module docstring + a residual-documenting test.

**B2 marker-coverage fix**: slice-098 marked the 21 Class-B *usage* lines but **not** the `_SOFT_FILE_SET` *definition* (`tools/parallel_conflict_resolver.py:59-62`). This slice closes that gap by adding the Class-B marker to those two definition lines, so the constant classifies `already-seam-routed` (rule 2) rather than `needs-human` (rule 4) — keeping the marker convention honest. (This adds `parallel_conflict_resolver.py` to the slice's blast radius.)

**Gate semantics** (CLI): exit `0` when no `needs-human-classification` entries exist (and, under `--strict`, the `must-rewrite-before-flip` baseline set is unchanged); exit `2` on any `needs-human-classification` or `--strict` baseline drift; exit `1` on usage error (R-7 fail-visible). `--json` emits the full inventory.

**Regression pin**: a suite test pins the `must-rewrite-before-flip` + `needs-human-classification` identity sets by `(relpath, stripped-snippet)` — **line-number-independent** — at the slice-100 baseline; a new unrouted literal in a later slice fails it (and `--strict`). Proven **non-vacuous by mutation** (inject an unrouted literal → test fails → revert).

**Scan scope**: in = `tools/**/*.py`, `skills/**/*.py`. Excluded (a hardcoded literal there is a historical/non-executing record, not a runtime mis-resolve): `tests/**/*.py`, all prose (`*.md`), `architecture/slices/archive/**`, `.git/`, `graphify-out/`, `diagnose-out/`, `.venv/`, and the audit's own module + baseline.

## Consequences

- The flip-execute slice gets a **trustworthy classified inventory** of the silent-breakage surface, plus a `--strict` drift guard usable as its pre-flight gate. **M3 honesty**: because slice-098 already routed this surface (Class-A `VAULT_ROOT`-derived / Class-B-marked), the genuine `must-rewrite-before-flip` set here is **small but non-empty** — ≥4 sites in `tools/project_frame_synth.py` (bare-`"architecture"` `/`-BinOp path-construction, unrouted, slice-088-era; B-add-1) plus any other bare/slashed path-construction sites the build re-derives — so the near-term value is the **completeness proof** (every code-surface literal classified, the real `must-rewrite` set enumerated, none silently certified clean) + the **regression guard**, not a large current checklist. The dense must-rewrite surface (`tests/**`, SKILL.md prose) is deferred.
- The suite gains a regression guard: a future slice adding an unrouted `tools/*.py` path-construction literal trips the baseline pin (proven non-vacuous by a correct-class mutation, M2).
- **Deferred** (explicit, not silent): the `tests/**/*.py` surface (`vault-flip-readiness-tests` follow-up) and the contract-prose surface (`SKILL.md`/`agents`/`CLAUDE.md`/`INSTALL.md` — owned by flip-execute or a dedicated prose slice). The flip is NOT flip-ready on prose after this slice; that is by design.
- New **public** tool → PMI-1/INST-1/BC-PROJ-9 inventory updates required. MEPD-1 disposition (tentative EXCLUDE — utility, not a RULE-ID; no VERSION bump) finalized at `/reflect`.
- `tools/_vault_paths.VAULT_ROOT` default is **unchanged** (`Path("architecture")`) — the capability-without-flip safety contract (AC5).

## Reversibility

**Cheap.** The audit is read-only and additive; the taxonomy, heuristics, and scan scope are pure refinements with no downstream lock-in (no data model, no contract, no behavior change to any existing tool). Broadening to tests/prose later, or retuning a class boundary, is a self-contained edit + a baseline re-pin. The tool is discarded outright once the flip ships and the in-tree vault no longer exists.
