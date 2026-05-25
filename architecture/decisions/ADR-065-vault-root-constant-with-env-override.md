---
id: ADR-065
title: Single VAULT_ROOT constant with env-var override seams every tools/*.py vault-path literal
date: 2026-05-25
slice: slice-068-add-vault-root-constant
reversibility: cheap
status: accepted
---

# ADR-065: Single `VAULT_ROOT` constant with env-var override (`AI_SDLC_VAULT_ROOT`) seams every `tools/*.py` vault-path literal

## Context

Through slice-067, every `tools/*.py` audit/utility module re-hardcodes the literal string `"architecture"` (or `Path("architecture")`) at each filesystem-resolving call site. As of slice-068 `/critique` (B1 ACCEPTED-FIXED), a re-grep finds **8 distinct `tools/*.py` files with such literals**:

1. `tools/build_checks_integrity.py:78` (per /critique B1 — missed by mission-brief + design-rev-1)
2. `tools/critique_review_prerequisite_audit.py:154`
3. `tools/cross_spec_parity_audit.py:152,305,307,309`
4. `tools/risk_register_audit.py:381` (argparse default)
5. `tools/slice_queue_writer.py:79,80,442,525,584`
6. `tools/state_transition_pin_audit.py:367`
7. `tools/supersede_audit.py:171`
8. `tools/validate_slice_layers.py:577`

(Note: `tools/shippability_decoupling_audit.py:91-92` ALSO contains the literal string `"architecture"` in tuple-shape AST-pattern allowlists — but those are intentionally NOT call sites for vault access; they are pattern data for detecting `Path("architecture")/...` shapes in OTHER files. Migrating them would BREAK the audit's purpose. Five additional sites — `tools/cross_spec_parity_audit.py:335`, `tools/state_transition_pin_audit.py:374,388,400`, `tools/validate_slice_layers.py:521` — contain `"architecture/..."` literals in USER-FACING error-message prose strings, also NOT migrated. Both classes documented in `design.md` §Sites EXCLUDED from migration.)

**Test-tree files** containing `REPO_ROOT / "architecture"` literals (`tests/methodology/conftest.py` + ~15 other `tests/methodology/*.py` files, ~42 occurrences total per /critique M3 grep) are **DEFERRED to a follow-on slice** rather than migrated in this one. Rationale documented at `design.md` §Sites EXCLUDED from migration — primarily: (a) the pre-existing R-15 audit regex at `tests/methodology/test_resolve_slice_dir.py:233` would silently atrophy without coordinated extension; (b) per-file prose-vs-path disposition needs documentation across 16 files; (c) avoiding the first test-tree-to-tools-tree import dependency simplifies slice-068's blast radius.

Two motivating exposures accumulate on the current state:

1. **Slice-069 blast-radius is unmanageable without a single seam.** The user's stated next direction (surfaced during `/query-design` 2026-05-25 — see `architecture/slices/slice-068-add-vault-root-constant/mission-brief.md` Intent) is `rename-architecture-to-sdlc-and-track-in-git`: rename the vault directory and remove it from `.gitignore` so it can be shared cross-machine. Without a single path-seam, that rename is a chaotic global find/replace across 8+ files with risk of subtle misses; with a seam, the rename is a 1-line constant default change.

2. **Tests that need to point at an alternate vault directory** have no clean way to do so. Today, every audit and tool resolves `Path("architecture")` from cwd or from a passed `repo_root`; integration tests that want to construct a fake-vault under `tmp_path/architecture/...` work, but tests that want to override the relative subdirectory name (e.g., to validate against a `.sdlc` fixture for the slice-069 rename design) cannot.

## Options considered

1. **Status quo — keep hardcoded literals at every call site.** Pros: zero work; zero new module. Cons: slice-069's rename becomes a fragile 8-file find/replace; no testing seam for vault-root variation; reverses neither motivating exposure.

2. **Module-level constant in a new leaf module `tools/_vault_paths.py`, read from env var at import time (this ADR).** Pros: single seam for slice-069 (1-line default change); env-var override (`AI_SDLC_VAULT_ROOT`) enables subprocess-isolated tests; leading-underscore naming follows the established `tools/_stdout.py` / UTF8-STDOUT-1 precedent (auto-excluded from PMI-1 inventory at `tools/plugin_manifest_audit.py:148`, so no `plugin.yaml` edit needed); reversibility cheap (delete module + revert 8 import lines). Cons: in-process tests that want to vary the value must use `monkeypatch.setattr` or subprocess (cannot reassign at module-attribute level without import-time gymnastics).

3. **Lazy function `def vault_root() -> Path` instead of module-level constant.** Pros: in-process mutation propagates to ALL call sites that invoke the function (no consumer-freeze cascade — see Consequences below for the freeze contract that option 2 incurs and that option 3 would avoid). Cons: every call site becomes a function call (`vault_root() / "x"` vs `VAULT_ROOT / "x"`) — verbose and non-idiomatic for path constants; doesn't match the existing `_stdout.reconfigure_stdout_utf8()`-style pattern (which IS a function, but for a side-effecting reconfiguration, not a value access); subprocess tests work identically either way; in-process monkeypatch on a module-level constant only updates `tools._vault_paths.VAULT_ROOT` itself, NOT any downstream consumer module that has already frozen the value at its own import time. **Per /critique M1 ACCEPTED-FIXED**: option 3's "in-process mutation" benefit is NOT illusory — it directly avoids the consumer-freeze cascade that option 2 incurs. The dismissal in this ADR's earlier revision (rev-1) was technically incorrect on that point. Option 2 is still chosen, but with the freeze contract documented explicitly as a deliberate production-correctness semantic (env var read once per process at startup; test isolation managed via subprocess fixtures) rather than as something option 3 would solve unnecessarily.

4. **CLI argument per tool (`--vault-root <path>`).** Pros: no env var; explicit. Cons: 8 tools need new args; tests must pass arg through; doesn't help non-tool consumers (conftest.py); doesn't address slice-069 — the audit framework's path resolution is internal to each tool's main(), and the in-codebase `repo_root / "architecture"` patterns at audit-internals stay hardcoded.

5. **Config file (`.ai-sdlc.toml`) parsed by every tool.** Pros: declarative. Cons: massive over-engineering for a single string value; introduces a TOML-parsing dependency on every audit tool; adds a new file the install-audit must enumerate; reversibility expensive vs option 2's cheap revert.

## Decision

Adopt **option 2**: module-level `VAULT_ROOT: pathlib.Path` constant in a new leaf module `tools/_vault_paths.py`, read from env var `AI_SDLC_VAULT_ROOT` at module-import (default `"architecture"`).

- **Naming**: leading-underscore (`_vault_paths.py`) per `tools/_stdout.py` / UTF8-STDOUT-1 precedent — auto-excluded from PMI-1 inventory; no `plugin.yaml` entry needed.
- **Env-var name**: `AI_SDLC_VAULT_ROOT` (prefixed `AI_SDLC_` for namespace clarity vs bare `VAULT_ROOT`; matches mission-brief's stated name; forward-compat with potential future `AI_SDLC_GRAPHIFY_OUT_ROOT` / `AI_SDLC_DIAGNOSE_OUT_ROOT` analogues if the slice-069 rename motivates them).
- **Read-at-import semantics + consumer-freeze cascade** (per /critique M1 ACCEPTED-FIXED — production-correctness contract): env-var consulted exactly once, at `tools._vault_paths` module-import time. Downstream consumers that compose `VAULT_ROOT` into their own module-level constants (e.g., `tools/slice_queue_writer.py:79` `_INDEX_MD_REL = VAULT_ROOT / "slices" / "_index.md"`; `tools/risk_register_audit.py:381` argparse `default=VAULT_ROOT / "risk-register.md"`) FREEZE that derived `Path` at the value `VAULT_ROOT` held when the consumer module was first imported. This is the deliberate production semantic (env var read once per process at startup), NOT a defect. Test isolation contract: in-process tests vary via subprocess fixtures (env injection at process boundary); in-process `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", ...)` updates only `tools._vault_paths` itself and does NOT propagate to already-frozen consumer constants — pinned by `test_consumer_constants_are_frozen_at_first_import` (TF-1 row added per /critique M1).
- **Migration scope**: 8 `tools/*.py` sites listed above. Sites carry inline `# VAULT_ROOT-routed (slice-068)` marker. `tools/shippability_decoupling_audit.py:91-92` deliberately NOT migrated (AST-pattern allowlist semantics). Five error-message-string sites deliberately NOT migrated (`tools/cross_spec_parity_audit.py:335`, `tools/state_transition_pin_audit.py:374,388,400`, `tools/validate_slice_layers.py:521` — user-facing prose, not filesystem paths). All `tests/methodology/*.py` `REPO_ROOT / "architecture"` literals (~42 occurrences across ~16 files) DEFERRED to a follow-on slice per /critique M3 — rationale in design.md §Sites EXCLUDED from migration.
- **No methodology-changelog entry, no PMI-1 bump**: pure mechanical refactor mints no rule; MEPD-1 Inclusion-heuristic posture is EXCLUDE (see `design.md` §MEPD-1 Inclusion-heuristic posture for the 5-criterion table).

## Consequences

- **Slice-069 (`rename-architecture-to-sdlc-and-track-in-git`) becomes a near-trivial change** — flip the `_DEFAULT` constant in `tools/_vault_paths.py` from `"architecture"` to `".sdlc"`, edit `.gitignore`, write the philosophy ADR, propagate any SKILL.md prose references that document the default layout. No 8-file find/replace.
- **A new architectural convention is established** for leading-underscore-helper modules in `tools/` that export simple values (vs `_stdout.py`'s function-export shape). Future leaf helpers can follow either pattern.
- **Env-var-overridable paths become a precedent** for any future `AI_SDLC_*_ROOT` constants (e.g., `AI_SDLC_GRAPHIFY_OUT_ROOT`, `AI_SDLC_DIAGNOSE_OUT_ROOT`). Not implemented here; precedent only.
- **One new entry in `tests/methodology/test_vault_root_constant.py`'s `_MIGRATION_SITE_ALLOWLIST` is required for any new tool module added post-slice-068 that resolves vault paths.** The `test_migration_site_allowlist_pinned` test catches drift — a new tool module hardcoding `Path("architecture")` without entering the allowlist (or routing through `VAULT_ROOT`) fails this test.
- **No test-tree-to-tools-tree import dependency introduced by this slice** (per /critique M2 ACCEPTED-FIXED — rev-1 falsely cited a non-existent `conftest.py L37` precedent for such an import; the actual `tests/methodology/conftest.py` has zero `from tools.*` imports, with `REPO_ROOT` defined locally at L6 `REPO_ROOT = Path(__file__).resolve().parents[2]`). The test-tree migration is DEFERRED per /critique M3, eliminating the question entirely for slice-068. The first test-tree-to-tools-tree import for `tools._vault_paths`, when it eventually happens in a follow-on slice, will be a clean greenfield decision rather than appended to an imagined precedent.
- **Zero behavior change at v0.69.0 → v0.69.0** (no version bump). Full pytest baseline (899 from slice-067 + 10 new tests per /critique M1 added freeze-pin row = 909 target) preserved.

## Reversibility

**Cheap.** Revert path:

1. Delete `tools/_vault_paths.py` (1 file).
2. Revert 8 import lines in the 8 migrated modules.
3. Revert 8 call-site edits (each was a `Path("architecture")` → `VAULT_ROOT` swap — `git revert` of the slice-068 commit handles it atomically).
4. Delete `tests/methodology/test_vault_root_constant.py` (1 file).
5. Optional: delete this ADR (or leave with a `status: superseded` frontmatter flip + new ADR explaining the reversal).

Total revert cost: <30 minutes including test re-validation. The constant introduces no persistent state, no schema, no API contract, no consumer-propagation obligation, no migration of stored data. The reversibility tag is `cheap` and the cost confirms it.
