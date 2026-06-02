# Slice 100: add-vault-flip-readiness-audit

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (advances the flip gate by retiring the *flip-completeness unknown* — the dominant flip risk; R-32 itself retires at the actual flip, the next cut)
**Test-first**: true  (per TF-1 — the classification logic is deterministic and naturally testable)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The external-vault flip (relocate `architecture/` + `diagnose-out/` to a shared external store, flip the `_vault_paths` default, git-untrack) is now fully unblocked, but it must land **atomically**: every hardcoded in-tree-vault-location literal (`architecture/…`, `diagnose-out/…`) silently breaks the moment the vault moves, and a single missed reference means code quietly reads the wrong or empty path post-flip. This slice ships a deterministic **readiness audit** that inventories and classifies every such literal — producing the complete, regression-pinned checklist the flip-execute slice (next cut) consumes — **without flipping this repo** (default stays `architecture/`). It mirrors the proven slice-093 *capability-without-flip* de-risking pattern.

**Scope (settled at `/design-slice`):** this first cut targets the **production-code surface** — `tools/**/*.py` + skill-helper scripts (`skills/**/*.py`) — where breakage is **silent** (a tool mis-resolving a path) and classification is **deterministic** via Python AST. The `tests/**/*.py` surface (breaks *loudly*; many literals are intentional seam/migration constants) and the contract-prose surface (`skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md` — bulk-rewritten atomically at flip-execute time, not reliably auto-classifiable) are **deferred to follow-up slices**. See [[decisions/ADR-091]].

## Acceptance criteria

1. New tool `tools/vault_flip_readiness_audit.py` scans the **production-code surface** (`tools/**/*.py` + skill-helper `skills/**/*.py`) and emits a deterministic JSON inventory of every `architecture/` / `diagnose-out/` location-assuming literal, each classified via Python AST/tokenize into exactly one of `{already-seam-routed, must-rewrite-before-flip, doc-example-safe, needs-human-classification}` with `path:line` evidence. (`already-seam-routed` recognizes both `VAULT_ROOT`-derived sites and the slice-098 Class-B `# … Class-B git identity (ADR-089)` retire-guarded markers.)
2. Classification is **fail-closed and deterministic**: an ambiguous / un-recognized hit lands in `needs-human-classification` (never silently dropped), and re-running on an unchanged tree yields byte-identical output (stable sort).
3. A regression pin (`tests/methodology/test_vault_flip_readiness_audit.py`) fixes the baseline `must-rewrite-before-flip` + `needs-human-classification` sets — keyed on `(relpath, ast.Constant.value, klass)` (line-number-independent, full constant value not a line-snippet; M2) — so a NEW un-routed vault-location literal fails the gate; proven **non-vacuous by two mutations** (M2): (a) inject a real *path-construction* literal → it MUST enter `must-rewrite` (test FAILS until reverted); (b) inject an error-*message* vault literal → it MUST NOT enter `must-rewrite` (guards the B1 context-aware fix).
4. CLI exit codes give gate semantics: `0` when no `needs-human-classification` entries exist (and, under `--strict`, the baseline set is unchanged), non-zero otherwise — wired so the flip-execute slice can consume the audit as a pre-flight checklist + drift guard.
5. **Capability-without-flip invariant holds**: `tools/_vault_paths.py` default stays `Path("architecture")`; the full methodology suite and the shippability catalog pass unchanged — every existing tool/test/skill behaves identically (no flip, fully reversible).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0 — paths/function names are a starting sketch; `/design-slice` firms them up)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_emits_classified_inventory_with_evidence | PASSING |
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_every_hit_has_exactly_one_class | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_ambiguous_literal_routes_to_needs_human_not_dropped | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_output_is_deterministic_across_runs | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_must_rewrite_baseline_pinned | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_new_unrouted_literal_fails_gate (non-vacuity, path-construction) | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_error_message_literal_not_must_rewrite (B1 guard) | PASSING |
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_unmarked_git_pathspec_routes_to_needs_human | PASSING |
| 4 | integration | tests/methodology/test_vault_flip_readiness_audit.py | test_cli_exit_zero_when_no_needs_human | PASSING |
| 4 | integration | tests/methodology/test_vault_flip_readiness_audit.py | test_cli_strict_nonzero_on_baseline_drift | PASSING |
| 5 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_vault_paths_default_unchanged | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Inventory + classify | Run `$PY -m tools.vault_flip_readiness_audit --json`; assert output has `path:line`-tagged entries; spot-check known literals (a `parallel_conflict_resolver.py` Class-B-marked `"architecture/slice-queue.md"` → `already-seam-routed`; a docstring/comment `architecture/…` mention → `doc-example-safe`; an unrouted executable path literal → `must-rewrite-before-flip`). |
| 2 | Fail-closed + deterministic | Feed a contrived ambiguous literal in a tmp fixture → lands in `needs-human-classification`; run the audit twice on the unchanged tree → byte-identical stdout. |
| 3 | Regression pin non-vacuity | Inject an un-routed `architecture/foo` literal into a scanned tmp/real file → `test_new_unrouted_literal_fails_gate` FAILS; revert → PASSES. |
| 4 | Gate wiring | `$PY -m tools.vault_flip_readiness_audit` returns 0 on a fully-classified tree; with a seeded `needs-human-classification` hit (or `--strict` baseline drift) returns non-zero (`echo $LASTEXITCODE`). |
| 5 | Capability-without-flip | `Get-Content tools/_vault_paths.py` shows default `Path("architecture")` unchanged; `$PY -m pytest tests/methodology` + `$PY -m tools.shippability_runner` both green. |

## Must-not-defer

- [ ] **Determinism** — stable-sorted output; a non-deterministic audit cannot serve as a regression pin (AC2/AC3).
- [ ] **Fail-closed classification** — no silent drop; every scanned literal lands in exactly one of the four classes, ambiguous → `needs-human-classification`.
- [ ] **Context-aware classification (B1/M1)** — `must-rewrite` requires a path-construction context (≤1-hop usage analysis), NOT node-type alone; recognize the Class-B + error-message-prose markers; specify the match rule + name the two residuals (per ADR-091 §Decision). Close the B2 `_SOFT_FILE_SET` marker-coverage gap in `parallel_conflict_resolver.py`.
- [ ] **Non-vacuity by mutation** — the AC3 pin must be proven to FAIL when an un-routed literal is injected (per slice-092 lesson).
- [ ] **cp1252-safe stdout** — new tool that prints MUST use `tools._stdout.reconfigure_stdout_utf8()` (UTF8-STDOUT-1; cp1252 class N≥8), never bare `print` of non-ASCII.
- [ ] **`encoding="utf-8"`** on every file read + any subprocess text capture (BC-GLOBAL-5).
- [ ] **New-public-tool count fan-out** — register in `plugin.yaml` + `tools/install_audit.py` `_CANONICAL_TOOLS` + `INSTALL.md` counts (PMI-1 / INST-1 / BC-PROJ-9); add the shippability catalog row.

## Out of scope

- **The `tests/**/*.py` surface** — breaks *loudly* (a failing test, not a silent mis-resolve) and many literals are intentional seam/migration test constants; deferred to a follow-up (`vault-flip-readiness-tests`).
- **The contract-prose surface** — `skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md`: real breakage (Claude follows `architecture/…` literally) but bulk-rewritten *atomically* at flip-execute time, and not reliably auto-classifiable into must-vs-doc (AI-hard prose judgement); deferred to a follow-up / owned by flip-execute.
- The actual flip — physical move of `architecture/`+`diagnose-out/`, default-flip, git-untrack, the atomic rewrite (the **next** cut; this slice only inventories + classifies, it does **not** fix any `must-rewrite-before-flip` literal).
- Wiring the post-flip PCR conflict-resolution replacement (`_vault_write`-lock substitute) + consuming the retained `vault_pathspec_is_tracked`.
- Per-worktree-install isolation (R-28 / R-29) — separate queued slice (`isolate-per-worktree-install`).
- C5 history decision (external vault as its own git repo) — flip-execute / prose slice.

## Dependencies

- Prior slices: [[slice-093-add-external-vault-support]] (the `_vault_paths` seam / `VAULT_ROOT`, `_vault_write` safe primitives), [[slice-098-route-or-retire-git-coupled-vault-tools]] (`tools/_vault_git.vault_is_external` + retained `vault_pathspec_is_tracked`), [[slice-068-add-vault-root-constant]] (the seam origin).
- Vault refs: [[decisions/ADR-065]], [[decisions/ADR-085]], [[decisions/ADR-089]]
- Risk register: [[risk-register#R-32]] (concurrent-write lost-update / shared-mutable-vault corruption — the flip gate)
- Initiative context: the `external-shared-vault-initiative` plan (flip is the next major step; this is its reversible first cut).

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m tools.vault_flip_readiness_audit --json
$PY -m pytest tests/methodology -q
```
Expected (M3-reframed): the audit emits a **non-empty TOTAL classified inventory** (>0 occurrences across the four classes — a zero total means the scanner/match-rule is broken) AND **zero un-triaged `needs-human-classification`** (every occurrence resolves; any `needs-human` — e.g. the B2 `_SOFT_FILE_SET` — is reviewed + resolved) AND the full methodology suite still passes (no flip occurred). NOTE: the genuine `must-rewrite-before-flip` set is **small but non-empty** — ≥4 `tools/project_frame_synth.py` bare-`"architecture"` `/`-BinOp path-construction sites (B-add-1) + any others the build re-derives; gate on **total classified >0 AND zero un-triaged `needs-human`**, NOT a specific `must-rewrite` count; the value is the completeness proof (none silently certified clean) + the regression guard. STOP if: total classified is zero, OR `needs-human` is non-empty/unresolved, OR any pre-existing test regresses.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
