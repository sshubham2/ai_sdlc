---
id: ADR-101
title: Tests pin their own vault root via a shared isolation helper, independent of the process-global VAULT_ROOT (the location-agnostic test convention)
date: 2026-06-04
slice: slice-110-make-pipeline-vault-location-agnostic
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-101: Location-agnostic test vault-root isolation

## Context

The external-vault flip makes `VAULT_ROOT` an **absolute** external path. Tools compose `repo_root / VAULT_ROOT / x` ([[decisions/ADR-089]] Class-A routing); per pathlib an absolute right operand discards `repo_root`. For PRODUCTION this is correct (all worktrees resolve the one shared external vault). But tests that pass `repo_root=tmp` and build `tmp/architecture/...` fixtures rely on `VAULT_ROOT` being the relative default — under an absolute `VAULT_ROOT` the tool reads the real external store and bypasses the fixture. The slice-110 flip review measured ~30 genuine in-process breakers of exactly this shape (`supersede_audit.py:173`, `project_frame_synth.py`, etc.).

`tools/_vault_paths.py` reads its resolution **once at import** and consumers freeze it (`from tools._vault_paths import VAULT_ROOT`), so an in-process test cannot un-set the global via env alone — the consumer already froze the value (`_vault_paths.py` docstring §Read-at-import + consumer-freeze cascade). The flip cannot ship until the suite is green when `VAULT_ROOT` is external; that is what this slice (the reversible prep) delivers, and this convention is how.

## Options considered

1. **Change the tools to take an explicit `vault_root` param** (so tests pass their tmp vault). Pro: tests trivially hermetic. Con: a production API change across ~11 tools that are **already correct** for production (the shared-external-vault model intends `repo_root`-independent resolution); changing correct production code to ease testing is over-engineering, and a per-`repo_root` vault would *break* the shared-vault model. **Rejected.**
2. **Per-test bespoke env+reload inline.** Con: ~38–74 duplicated reload incantations; the freeze-cascade reload set is error-prone to repeat. **Rejected** (duplication; AP-13 consumer-driven-contract risk inverted).
3. **A shared test isolation helper** (chosen): one helper pins a test's vault root to its own tmp fixture independent of the process-global `VAULT_ROOT` — env-set + reload-cascade for in-process call-sites; child-env-unset/explicit for subprocess call-sites. Pro: one tested mechanism; no production change; tests robust under default AND absolute-`VAULT_ROOT`.

## Decision

Adopt option 3. A shared helper (`tests/_vault_isolation.py` or a `conftest.py` fixture) gives any test a vault root pinned to its own tmp fixture:

- **in-process**: set `AI_SDLC_VAULT_ROOT=<tmp>/architecture` → `importlib.reload(tools._vault_paths)` → reload the **consumer module under test** (because the consumer froze `VAULT_ROOT` at its own import). The helper **asserts the consumer's `VAULT_ROOT` actually changed** before yielding (non-vacuity, AP-5 — a no-op reload must fail loud, not green-wash).
- **subprocess**: launch the child with `AI_SDLC_VAULT_ROOT` unset (or explicitly the tmp vault) so it re-resolves to its own tmp repo rather than inheriting a parent sim env.

The binding gate is **the full suite green under `AI_SDLC_VAULT_ROOT=<external-copy>`** (the flip simulation) AND under the default. The env-var sim is an over-strict **superset** of the real (git-common-dir-config) flip-breaker set — robustness to it implies robustness to the real flip plus a stray env var.

## Build-time refinement (slice-110 `/build-slice` — APED-1): `setattr`-pin, not `importlib.reload`

This ADR originally specified `importlib.reload(<consumer>)` as the in-process re-point mechanism. Executing that against the real cascade at `/build-slice` (the APED-1 obligation this ADR's Consequences flagged) surfaced a **fatal flaw** the reasoned-about design missed: `importlib.reload` re-executes the consumer's module body, **rebinding its classes/enums to NEW objects**. A test that imported a symbol by name — e.g. `from tools.parallel_conflict_resolver import ConflictClass` — and then asserts `classify_conflict(diag) is ConflictClass.SOFT` **breaks**, because the reloaded module's `ConflictClass.SOFT` is a different object than the test's pre-imported one. This reddened `test_pcr_1_*` under BOTH the default suite AND the flip sim (an introduced regression, not a flip-only break).

**Refined mechanism (the one this slice ships): setattr-pin in place, no reload.** The shared helper (`tests/_vault_isolation.pin_vault_root`) is a context manager that:
- `setattr`s `tools._vault_paths.VAULT_ROOT` and each listed consumer's `VAULT_ROOT` to the pinned vault dir (cures every function-local `repo_root / VAULT_ROOT / x` reader and every `from tools._vault_paths import VAULT_ROOT` binding — Python looks the name up in the module dict at call time);
- re-derives each frozen module-level constant via an explicit `derived=[(module, attr, fn)]` list (only the few consumers with such constants — `parallel_conflict_resolver._AUDIT_LOG_PATH`, `build_checks_integrity._PROJECT_LIVE_REL`, `slice_queue_writer._INDEX_MD_REL` — supply one);
- captures prior values and restores them in reverse on exit (no reload → **class/enum identity preserved**; no cross-test pollution).

The **non-vacuity guarantee** (AP-5) is split: the helper asserts ≥1 listed consumer actually binds `VAULT_ROOT` (a pin that touches nothing is a test-author mistake → loud `AssertionError`), and the **binding empirical non-vacuity proof is the flip-sim suite run itself** — a frozen constant left un-`derived` fails loudly under the `AI_SDLC_VAULT_ROOT=<seeded>` gate, which is re-measured at build (never assumed). The pin value is the in-tree-relative `Path("architecture")` (identical to the un-flipped default), so the fixture is a no-op under the default suite and the cure under the flip sim.

Everything else in this ADR stands: one shared mechanism, no production change, tests robust under default AND absolute-`VAULT_ROOT`. Only the *implementation* of "re-point the consumer" moved from reload to setattr.

## Consequences

- After this slice, a future config-only flip is suite-neutral (the suite is already green with an external `VAULT_ROOT`).
- New vault-resolving tests follow this convention (pin your own vault root; never rely on the relative-default coincidence).
- The exact per-consumer reload set is determined by **executing** against the real freeze cascade at `/build-slice` (APED-1 / AP-3) — an un-reloaded frozen consumer would silently keep the global `VAULT_ROOT`, so the helper's non-vacuity assert is load-bearing.
- No production code changes; `_vault_paths` resolution semantics are untouched.

## Reversibility

**Cheap.** A test-support helper + test edits; `git revert` removes it. No production API, schema, or data change. The convention is advisory for future tests, not a locked contract.
