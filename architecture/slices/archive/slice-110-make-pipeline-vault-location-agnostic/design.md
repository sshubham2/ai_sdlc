# Design: Slice 110 make-pipeline-vault-location-agnostic

**Date**: 2026-06-04
**Mode**: Standard

> **Phase-1-only ship (user-approved 2026-06-04):** at `/build-slice` the design's sanctioned Phase 1→2 split was taken. slice-110 ships **Phase 1** = the location-agnostic test suite (AC1+AC5, `## Phasing` below). **Phase 2** (AC2 skill-op routing + AC3 prose op-gate + AC4 graphify, and [[ADR-102]]'s implementation) is **deferred to a follow-on slice**. The §What's new / §Components touched / §Phasing entries below describe BOTH phases; only the Phase-1 items (the test-isolation helper + the ~85 test repoints) are realized in this slice. Build-discovered: the in-process mechanism is **setattr-pin, not `importlib.reload`** (see the [[ADR-101]] build-time refinement — reload breaks reloaded-module class/enum identity).

The reversible **flip-readiness prep** the BLOCKED flip design forced (`superseded-flip-design/`). Goal: every test + in-loop skill + the readiness audit resolves the vault through the `VAULT_ROOT` seam regardless of where the vault lives, so a future config-only flip is a **suite-neutral no-op**. No move, no `_vault_paths` behavior change; reversible by plain `git revert`; suite green at every commit.

## Decisions settled at /design-slice (mission brief delegated these to design)

| Question | Decision | Why |
|----------|----------|-----|
| The ~36 RETIRE-behavior tests: rewrite-to-assert-RETIRE vs self-control-own-vault-root? | **Self-control own vault root** — same mechanism as the 38 fixture tests. NOT a behavior rewrite. | **Two distinct failure paths** (corrected per `/critique` M1 — bucket by path at build): the **bare-branch** RETIRE tests fail via the forced `vault_is_external=True` STOP guard (`stranded_slice_audit.py:328`); the **worktree-path** tests (e.g. `test_in_progress_parallel_slice_does_not_halt` → `klass=INDETERMINATE/fresh-worktree-no-milestone`) fail via *fixture-path-resolution drift* — `classify_worktree_state` reads the worktree milestone via VAULT_ROOT and misses the in-tree fixture; that path has NO `vault_is_external` guard. BOTH are cured by the test pinning its own in-tree vault root. RETIRE-when-external is already covered by `test_slice_098_vault_routing.py`. |
| Split tests from skills+audit? | **Phase, don't pre-split** — Phase 1 = tests (AC1), Phase 2 = skills+audit (AC2-4); `/build-slice` plan-mode MAY split at the Phase 1→2 boundary if Phase 1 fills the budget. | Both phases are reversible + green-throughout (unlike the flip), so a build-time split is low-risk; pre-splitting adds slice overhead. The phase boundary is clean — Phase 1 is pytest-provable, Phase 2 (SKILL.md prose) is not. |
| AC1 gate = green under `AI_SDLC_VAULT_ROOT=<ext>`? | **Yes, with the over-strict nuance documented** | The env-var sim is an over-strict *superset* of the real (config-based) flip-breaker set: env is inherited by subprocesses, the `$GIT_COMMON_DIR/aisdlc/vault-root` config is NOT (a tmp-repo subprocess resolves its own config-less common-dir). Making the suite robust to the env sim → robust to the real flip AND to a stray env var (defense-in-depth). |

## What's new

- **A shared test vault-isolation helper** (a NEW `tests/_vault_isolation.py`; self-tests in a NEW `tests/methodology/test_vault_isolation.py` — deliberately **NOT** `test_vault_root_constant.py`, whose `assert test_count == 15` pin (`:201`) would trip per FBCD-1 sub-mode (c) / `/critique` B2; if any test MUST land there, bump the `== 15` literal + its docstring rationale in the same commit and grep the repo for other `test_vault_root_constant` count citations): pins a test's vault root to its own tmp fixture **independent of the process-global `VAULT_ROOT`**, so the test is green under the default AND under an absolute `AI_SDLC_VAULT_ROOT`. A `tests/conftest.py` sys.path shim makes the bare `import _vault_isolation` resolve from any test file. Two call-shapes (the freeze cascade dictates both):
  - **in-process** call-sites (`run_audit(project_root=tmp)`): `pin_vault_root(Path("architecture"), <consumer-modules…>, derived=[…])` — a context manager that **setattr-pins** `VAULT_ROOT` in place on `tools._vault_paths` + each listed consumer (cures every function-local `repo_root / VAULT_ROOT / x` reader and every `from tools._vault_paths import VAULT_ROOT` binding) and re-derives any frozen module-level constants via `derived`. **`setattr`, NOT `importlib.reload`** — a build-time refinement of [[ADR-101]] (APED-1): reload rebinds the consumer's classes/enums to new objects and breaks tests that compare reloaded-module identity (`x is ConflictClass.SOFT` in `test_pcr_1_*`); setattr preserves identity. The exact per-test consumer + `derived` set is nailed at `/build-slice` against the real cascade (the consumer froze `VAULT_ROOT` via `from tools._vault_paths import VAULT_ROOT` — confirmed at `supersede_audit.py:16,173` — and frozen constants like `parallel_conflict_resolver._AUDIT_LOG_PATH` / `build_checks_integrity._PROJECT_LIVE_REL` need explicit re-derive). Applied per-file as a small **autouse fixture** (one per breaking test file).
  - **subprocess** call-sites (`$PY -m tools.X --repo-root tmp`): `subprocess_env()` builds the child env with `AI_SDLC_VAULT_ROOT` **unset** (or explicitly the tmp vault) so the child re-resolves to its own tmp repo rather than inheriting the parent's sim env.
- **~82-full / ~74-methodology test repoints** applying the helper (Phase 1; measured against a **SEEDED** byte-faithful external copy — the real-flip-faithful sim). Per `/critique-review` B1, the first Critic's "~99/91" was measured against an EMPTY external dir, which spuriously breaks ~17 content-reading audits (`test_live_repo_self_application_clean`, `test_real_tree_clean`, …) that correctly read real vault content and need NO fix — the real flip MOVES content, it does not empty it. `/build-slice` re-measures the live **SEEDED** flip-sim failure set FIRST and treats THAT as the inventory of record (APED-1; never the empty-dir number, never a copy-forward count). The env-sim is NOT a "defense-in-depth superset" — that framing is struck; the seeded sim is the faithful gate.
- **UNAMBIGUOUS in-loop skill vault-op routing** (Phase 2; narrowed per `/critique` M2): route only the ops whose target is unambiguously the canonical vault — the **archive `mv`** (`/reflect:320`, `/archive:51` → external `archive/`), `/drift-check`'s **drift-log.md** (shared file), `/commit-slice`'s **archived/slice-folder reads** — through `VAULT_ROOT`/`vault_edit`. The bootstrap-entangled per-slice **active-folder** writes (`/reflect` reflection.md, `/validate-slice` validation.md, `/slice` scaffold `<wt_path>/…`, `/build-slice` `git add`) are **deferred to the flip slice** (it owns the worktree-vs-external decision; over-routing now risks moving slice-authoring artifacts out of the worktree — a BRANCH-3 violation). OSDG-1 re-sync ONLY the genuinely-guarded edited skills (`/reflect`, `/commit-slice`); `/archive` + `/drift-check` are edited-but-unguarded (no installed copy — no re-sync; M3).
- **SKILL.md-prose op-gate** (Phase 2 — AC3; the dominant Phase-2 risk): the `vault_flip_readiness_audit` scan is Python-`tokenize`/`ast`-based (`:459`/`:477`) and CANNOT ingest Markdown (`/critique` B3) — a SKILL.md collapses to one `NEEDS_HUMAN(parse-error)`. **REUSE, not a third classifier** (`/critique-review` M-add-1, CSP-1/DRY): `tools/vault_flip_prose_inventory.py` (slice-107) ALREADY scans `skills/**/SKILL.md`, region-anchors on `in_code` + `_OP_VERB_RE` (`:211`), and is gate-capable (`--strict` exit 2). AC3 extends THAT tool with an **operational-op gate mode** (or shares its region-anchoring helper) — the semantic split is explicit: the inventory flags ALL 318 location-literals (rewrite-at-flip); the AC3 gate flags only **un-routed write-OPS** (`mv`/`cp`/`git add`/`Write`-target) inside anchored regions. A bare mention (244 across 24 files) → never gated (AP-1). Prove **both** non-vacuity (synthetic un-routed-write flagged) AND non-over-flag (the 244 NOT flagged) at build (APED-1) + a **code-Critic pass** (AP-4 — parser change). **The deferred per-slice-write prose does NOT get silently baselined** (`/critique-review` M-add-2 / AP-12 — never empty a fail-closed bucket via a silent waiver): it lands in a DISTINCT **gate-visible `DEFERRED_TO_FLIP`** class tagged with its owner (the flip slice) so the flip slice's pre-finish MUST drive it to ∅; it is NOT folded into `DOC_EXAMPLE_SAFE` or a quiet baseline.
- **graphify-vault-target flip-awareness** (Phase 2 — AC4): the `$PY -m graphify vault architecture` invocations (6 skills incl. `/design-slice:62`) resolve the vault root via the seam (or are documented + logged flip-aware).

## What's reused

- `tools/_vault_paths.py` — the seam. **Consumed, NOT changed.** Its read-at-import + consumer-freeze semantics are the exact constraint the isolation helper works around (reload-cascade). The existing pattern: `test_vault_root_constant.py` uses `importlib.reload(tools._vault_paths)` for the seam's own value + subprocess-env for consumer-level override (`_vault_paths.py` docstring §Read-at-import).
- `tools/vault_edit.py` — the routed `append`/`rewrite` channel the skill per-slice-folder writes route through.
- `tools/vault_flip_readiness_audit.py` — extended at AC3 (the `.py`-only `_iter_scan_files` at `:488-507`).
- [[decisions/ADR-089]] — `vault_is_external` (what the RETIRE tests' scenarios key on).
- `superseded-flip-design/` — the BLOCKED flip review + ADR-099/100 drafts that motivated this slice.

## Components touched

### `tests/_vault_isolation.py` (new — test support; or a `conftest.py` fixture)
- **Responsibility**: give any test a vault root pinned to its own tmp fixture, independent of the process-global `VAULT_ROOT`, so the suite is green under any global vault-location state.
- **Lives at**: `tests/_vault_isolation.py` (new) or `tests/methodology/conftest.py` (extended).
- **Key interactions**: `tools._vault_paths` (reload), the consumer-under-test module (reload), `AI_SDLC_VAULT_ROOT` env, subprocess child env.

### `tools/vault_flip_prose_inventory.py` (modified — AC3; the REUSE target per `/critique-review` M-add-1)
- **Responsibility**: gain an **operational-op gate mode** that flags un-routed in-loop-skill vault write-ops (`mv`/`cp`/`git add`/`Write`-target) in `SKILL.md` prose — reusing this tool's existing Markdown region-anchoring (`in_code` + `_OP_VERB_RE`) rather than a third parallel classifier in `vault_flip_readiness_audit` (which is Python-tokenizer-only and would duplicate this tool — CSP-1).
- **Lives at**: `tools/vault_flip_prose_inventory.py` (op-gate mode + the `DEFERRED_TO_FLIP` class).
- **Key interactions**: the in-loop `SKILL.md` files; its existing `--strict` SHA-256 baseline; `architecture/shippability.md` rows 108/109 (RPCD-1/SCPD-1 propagation).

### In-loop skills (modified — AC2/AC4)
- `/reflect`, `/archive`, `/validate-slice`, `/slice`, `/drift-check`, `/commit-slice`, `/build-slice` SKILL.md — route literal in-tree vault writes/reads/`mv`/`git add` + the graphify-vault target through the seam. OSDG-1-guarded copies re-synced.

## Wiring matrix

Per **WIRE-1**. The readiness-audit extension is a modification (no new module). The test helper is a new **test-support** module (no production consumer demanded).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/_vault_isolation.py` | — | — | `test-support helper consumed by the repointed tests in this slice — rationale: pytest support code, not a product module (mirrors tests/methodology/conftest.py); not in PMI-1/INST-1 inventory` |

## Phasing (the build-time split point)

- **Phase 1 (AC1)**: the isolation helper + the ~38–74 test repoints. Verifiable by pytest (default green AND `AI_SDLC_VAULT_ROOT=<ext>` green). Self-contained; `/build-slice` MAY ship this as slice-110 and defer Phase 2 to a follow-on if Phase 1 fills the day.
- **Phase 2 (AC2/3/4)**: in-loop skill prose routing + the readiness-audit SKILL.md-scan + the graphify target. Verifiable by the extended audit + OSDG-1 drift tests + manual trace (NOT pytest — SKILL.md prose isn't executed in the suite).

## Decisions made (ADRs)
- [[ADR-101]] — Tests pin their own vault root via a shared isolation helper (the location-agnostic test convention) — reversibility: **cheap**.
- [[ADR-102]] — `vault_flip_readiness_audit` scans `SKILL.md` prose for in-tree vault literals, closing the `.py`-only blind spot — reversibility: **cheap**.

## Authorization model for this slice
None — local test + skill-prose + audit edits; no auth surface.

## Error model for this slice
No new runtime error codes. The isolation helper fails **loud** if a reload doesn't take effect (assert the consumer's `VAULT_ROOT` actually changed before the test body — non-vacuity per AP-5, so a no-op reload can't green-wash). The extended readiness audit stays fail-closed on an un-routed `SKILL.md` literal (non-vacuity proven by a synthetic un-routed-write fixture). No `_vault_paths` resolution change — the seam's R-7 fail-visible behavior is untouched.

## Notes for /critique
- **The env-sim is an over-strict superset of the real-flip breaker set** (env inherited by subprocesses; the git-common-dir config is not). Fixing the superset is intentional defense-in-depth, not a misunderstanding — flag if you disagree.
- **The consumer-freeze cascade** (`from tools._vault_paths import VAULT_ROOT`) is why the helper must reload the *consumer*, not just `_vault_paths` — verify the reload set is complete (an un-reloaded frozen consumer would silently keep the global VAULT_ROOT → the test would still read the external store). This is the AP-3/APED-1 risk: the reload mechanism MUST be executed against the real cascade at build, not assumed.
- **Phase 2 is not pytest-provable** — the readiness-audit SKILL.md-scan (AC3) is the ONLY deterministic guard for the skill-prose routing (AC2); if the audit extension is weak, AC2 ships unverified. Scrutinize the audit's non-vacuity.
