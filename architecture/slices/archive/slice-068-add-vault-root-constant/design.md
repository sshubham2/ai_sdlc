# Design: Slice 068 — add-vault-root-constant

**Date**: 2026-05-25
**Mode**: Standard

## What's new

- **New module** `tools/_vault_paths.py` (leading-underscore per `tools/_stdout.py` precedent — see [[ADR-065]] §Naming): single source of truth for vault-relative path construction; exports module-level `VAULT_ROOT: pathlib.Path` constant.
- **New test** `tests/methodology/test_vault_root_constant.py`: **10 unit tests** (per /critique M1 ACCEPTED-FIXED adding `test_consumer_constants_are_frozen_at_first_import` row) pinning module-export contract + default + env-var override + migration allowlist + idempotency + pytest baseline preservation + consumer-freeze contract.
- **New ADR** [[ADR-065]] — env-var-overridable vault-root constant module; reversibility: cheap.

## What's reused

- `tools/_stdout.py` — naming convention precedent (leading-underscore-helper excluded from PMI-1 inventory at `tools/plugin_manifest_audit.py:134-149`).
- `tools/plugin_manifest_audit.py:148` — the `not p.name.startswith("_")` filter that auto-excludes the new helper from PMI-1 enumeration (zero plugin.yaml edit needed).
- `tests/methodology/conftest.py:30-105` `_resolve_slice_dir` — pre-existing `REPO_ROOT.joinpath("architecture", ...)` pattern that this slice migrates inline.
- `methodology-changelog.md` v0.37.0 `UTF8-STDOUT-1` precedent: `tools/_stdout.py` is the prior-art leading-underscore-helper module — establishes the architectural pattern this slice extends.

## Components touched

### `tools/_vault_paths.py` (NEW — leaf utility)

- **Responsibility**: expose a single `VAULT_ROOT: pathlib.Path` constant routing all `tools/*.py` filesystem references to the vault directory through one seam, with env-var override for testing and for slice-069's planned `architecture/` → `.sdlc/` rename.
- **Lives at**: `tools/_vault_paths.py` (created by this slice).
- **Key interactions**: imported by 8 migrated `tools/*.py` modules (see Wiring matrix below — composition corrected per /critique B1 + M3 ACCEPTED-FIXED: `build_checks_integrity.py` added, `conftest.py` deferred). MUST NOT import from any other `tools/` module (leaf invariant — pinned by `test_vault_paths_module_is_leaf` per AC4).
- **Module body (full — small enough to inline; lives in code, not duplicated here for any other component)**:
  ```python
  """Vault-root path constant (slice-068).

  Exports VAULT_ROOT — the single seam routing tools/*.py filesystem
  references to the vault directory. Default ``Path("architecture")``;
  override via env var ``AI_SDLC_VAULT_ROOT`` (read at module import).

  Per ADR-065. Leading-underscore-helper module per UTF8-STDOUT-1 /
  ``tools/_stdout.py`` precedent — auto-excluded from PMI-1 inventory.
  """
  from __future__ import annotations

  import os
  from pathlib import Path

  _ENV_VAR = "AI_SDLC_VAULT_ROOT"
  _DEFAULT = "architecture"

  VAULT_ROOT: Path = Path(os.environ.get(_ENV_VAR, _DEFAULT))
  ```
- **Read-at-import-time semantics** (load-bearing): env-var read happens at module-import, NOT at attribute access. This is the deliberate design (matches Python idiom for path constants; matches mission-brief smoke-gate's subprocess test shape). In-process unit tests that need to vary the value use `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", Path("/tmp/foo"))`; cross-process semantics use subprocess fixtures.

### 8 migrated `tools/*.py` modules (MODIFIED)

The corrected migration allowlist (mission-brief said 7; design discovered 8 then /critique B1 found a 9th site `build_checks_integrity.py:78` AND /critique M3 scoped-back `conftest.py` to DEFERRED — net 8 tools/*.py sites, zero tests/ sites):

| # | File | Line(s) | Migration shape |
|---|------|---------|-----------------|
| 1 | `tools/build_checks_integrity.py` | 78 | `_PROJECT_LIVE_REL = "architecture/build-checks.md"` → `_PROJECT_LIVE_REL = VAULT_ROOT / "build-checks.md"` (type-shape changes from `str` to `Path` — verify L222-223 consumer `root / _PROJECT_LIVE_REL` still composes; per /critique B1 ACCEPTED-FIXED) |
| 2 | `tools/critique_review_prerequisite_audit.py` | 154 | `repo_root / "architecture" / "triage.md"` → `repo_root / VAULT_ROOT / "triage.md"` |
| 3 | `tools/cross_spec_parity_audit.py` | 152, 305, 307, 309 | 4 sites: `triage.md`, `threat-model.md`, `requirements.md`, `nfrs.md` |
| 4 | `tools/risk_register_audit.py` | 381 | `default=Path("architecture/risk-register.md")` → `default=VAULT_ROOT / "risk-register.md"` |
| 5 | `tools/slice_queue_writer.py` | 79, 80, 442, 525, 584 | 5 sites: `_INDEX_MD_REL`, `_SLICES_DIR_REL`, `out_path`, CLI default, `canonical_out` |
| 6 | `tools/state_transition_pin_audit.py` | 367 | `root / "architecture" / "risk-register.md"` → `root / VAULT_ROOT / "risk-register.md"` |
| 7 | `tools/supersede_audit.py` | 171 | `project_root / "architecture" / "slices"` → `project_root / VAULT_ROOT / "slices"` |
| 8 | `tools/validate_slice_layers.py` | 577 | `Path("architecture/.secrets-allowlist")` → `VAULT_ROOT / ".secrets-allowlist"` |

Each migration site carries the inline marker `# VAULT_ROOT-routed (slice-068)` on the migrated line — load-bearing per mission-brief AC2 + must-not-defer #2 (distinguishes filesystem-path migration sites from prose-asserting test fixtures that look superficially similar).

**Sites EXCLUDED from migration (with rationale, all preserved verbatim):**

- **`tools/shippability_decoupling_audit.py:91-92`**: the `("architecture", "slices", "archive")` and `("architecture", "build-checks.md")` tuples are AST-pattern allowlists used to detect Path-shape literals in OTHER `tests/methodology/*.py` files. Migrating these would BREAK the audit's detection purpose (it greps for the LITERAL string `"architecture"` in third-party code, not its own filesystem access). Documented inline at the audit site as `# NOT VAULT_ROOT-routed (slice-068) — AST-pattern allowlist; matches literal "architecture" in audited tree`.
- **Error-message strings**: `tools/cross_spec_parity_audit.py:335`, `tools/state_transition_pin_audit.py:374,388,400`, `tools/validate_slice_layers.py:521` contain the literal `"architecture/..."` as USER-FACING error prose ("not found at...", "X if it exists" hint). These are display strings, not filesystem path resolutions; migrating would inject `VAULT_ROOT.as_posix()` into user-facing error messages with no benefit. Documented inline at the relevant call sites with `# NOT VAULT_ROOT-routed (slice-068) — error-message prose`.
- **`tests/methodology/conftest.py` and all other `tests/methodology/*.py` files** (15 files, ~42 occurrences of `REPO_ROOT / "architecture"`): **DEFERRED** to a follow-on slice per /critique M3 ACCEPTED-FIXED. Rationale: (a) the test-tree migration would require extending the pre-existing R-15 audit regex at `tests/methodology/test_resolve_slice_dir.py:233` (`_R15_LITERAL_PATH_RE`) to also match `REPO_ROOT\s*/\s*VAULT_ROOT\s*/\s*"slices"` shapes, OR conftest's migration silently atrophies the R-15 backstop; (b) the design.md L139 prose-vs-path distinction conflates two test categories (true prose-asserting matchers vs filesystem-resolving REPO_ROOT/architecture/decisions paths) that need per-file disposition; (c) scope-back to `tools/*.py` only avoids opening the first test-tree-to-tools-tree import dependency in conftest, which was the M2 false-precedent concern; (d) the slice-069 follow-on can address tests/ as a coherent unit (or even more cleanly, tests/ migration may not be needed at all if `AI_SDLC_VAULT_ROOT` is never set during test runs).

**Site-level edge cases:**

- **`tools/build_checks_integrity.py:78`** (NEW per /critique B1): the literal is assigned to a module-level `_PROJECT_LIVE_REL = "architecture/build-checks.md"` (a `str`, not a `Path`). Consumer at L222-223 does `root / _PROJECT_LIVE_REL` where `root` is a `Path` — `Path / str` composes correctly. Migration changes the type to `Path`: `_PROJECT_LIVE_REL = VAULT_ROOT / "build-checks.md"` (now a `Path`). `Path / Path` ALSO composes correctly via `pathlib.PurePath.__truediv__` — verified semantics. No consumer-side edit needed; the type change is transparent.
- **`tools/risk_register_audit.py:381`** (NEW vs mission brief): the argparse `default=Path("architecture/risk-register.md")` evaluates at module-import time (argparse default-eval semantics). Migrating to `default=VAULT_ROOT / "risk-register.md"` preserves the import-time evaluation timing. Note per /critique m1 ACCEPTED-FIXED: argparse default-eval interacts with VAULT_ROOT consumer-freeze (see §Consumer-freeze cascade below) — for slice-068 this is safe (no env-var usage); slice-069+ planners must understand the freeze contract.
- **`tools/validate_slice_layers.py:577`** (NEW vs mission brief): a conditional default for `--secrets-allowlist`; direct migration.

### Consumer-freeze cascade (per /critique M1 ACCEPTED-FIXED)

The `VAULT_ROOT` constant is read at `tools._vault_paths` module-import time (option 2 design per ADR-065). Downstream consumers that compose VAULT_ROOT into their own module-level constants at THEIR import time (e.g., `tools/slice_queue_writer.py:79` `_INDEX_MD_REL = VAULT_ROOT / "slices" / "_index.md"`, `tools/risk_register_audit.py:381` `default=VAULT_ROOT / "risk-register.md"`) FREEZE that derived `Path` at the value `VAULT_ROOT` held when the consumer module was first imported. Subsequent `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", Path("/tmp/foo"))` updates `tools._vault_paths.VAULT_ROOT` itself but DOES NOT propagate to any already-frozen `_INDEX_MD_REL` / `default=` / etc.

**This is the deliberate production-correctness semantic** (env var read once per process at startup), not a defect — but it has direct test-isolation implications that the design pins explicitly:

- **In-process tests that need to vary `VAULT_ROOT`** for downstream consumers: use **subprocess fixtures** (env var injection at process boundary; consumer modules re-import with the new value). The 4 env-var AC tests (`test_vault_root_default_equals_path_architecture`, `test_env_var_override_via_subprocess`) all use subprocess shape per mission-brief AC4(b) — this is correct.
- **In-process tests that only need to vary `tools._vault_paths.VAULT_ROOT` itself** (NOT any frozen downstream constant): `monkeypatch.setattr` works for the module's own attribute, but the test author MUST verify no downstream consumer has already frozen the value at import time.
- **`test_consumer_constants_are_frozen_at_first_import`** (NEW per /critique M1 ACCEPTED-FIXED): a regression-pin asserting that `tools.slice_queue_writer._INDEX_MD_REL` does NOT update after `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", Path("/tmp/foo"))`. This pins the freeze semantic as the contract — silent test pollution via expected-but-broken propagation is the failure mode this pin catches.

Documented anti-pattern references: GitHub `pytest-dev/pytest` issue #4226 (env vars at import time), discussion #10027 (test isolation hazards). The `pytest-env` plugin exists precisely to manage env-at-import semantics — slice-068 does not adopt it; subprocess fixtures suffice.

## Contracts added or changed

None. Pure refactor — zero new endpoints, events, or schemas.

## Data model deltas

None. No persistent state, no schema changes.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file MUST declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/_vault_paths.py` | 8 migrated `tools/*.py` modules listed above (collectively the consumer) — first-cited consumer: `tools/slice_queue_writer.py:79` (`_INDEX_MD_REL = VAULT_ROOT / "slices" / "_index.md"`) | `tests/methodology/test_vault_root_constant.py::test_all_tools_modules_import_vault_root` | — |
| `tests/methodology/test_vault_root_constant.py` | — | — | rationale: test module — consumer entry point not applicable per WIRE-1 prior-art (test-only modules are exempt; multiple precedents in `tests/methodology/test_*` corpus) |

Note: no `tests/methodology/conftest.py` migration in this slice (DEFERRED per /critique M3 ACCEPTED-FIXED — see §Sites EXCLUDED from migration above). No new test-tree-to-tools-tree import dependency is introduced by slice-068.

## Decisions made (ADRs)

- [[ADR-065]] — env-var-overridable vault-root constant module (`tools/_vault_paths.py`); reversibility: **cheap** (revert = delete module + revert 8 import lines; zero behavior change to revert).

## Authorization model for this slice

N/A — this slice introduces no user-facing actions, no API endpoints, no security boundaries. Pure compile-time refactor.

## Error model for this slice

- **`AI_SDLC_VAULT_ROOT` env var set to invalid path** (non-existent directory): NOT validated at module-import. `VAULT_ROOT` simply becomes `Path(<whatever-string>)`; downstream `.exists()` / `.read_text()` calls produce the same FileNotFoundError they already would. No new error-handling path introduced. (Rationale: validation at import time would prematurely fail tests/tools that don't actually read the vault; lazy-fail at point-of-use preserves least-surprise.)
- **`AI_SDLC_VAULT_ROOT` env var contains whitespace or special chars**: passed through to `Path()` unchanged. `Path` constructor accepts any string; downstream filesystem ops emit OSError on actually-invalid filenames. No new validation.
- **Module import fails** (e.g. permission error reading env): would bubble as ImportError at first use. No catch; this is a configuration-broken-environment case, not a runtime concern.
- **argparse default-eval freeze** (per /critique m1 ACCEPTED-FIXED): `tools/risk_register_audit.py:381` `default=VAULT_ROOT / "risk-register.md"` and `tools/slice_queue_writer.py:525` `default=VAULT_ROOT / _QUEUE_FILENAME` evaluate at parser-construction time (i.e., module-import). For slice-068 (no env-var usage in production runs) this is correct and safe. For slice-069+ (env-var-driven vault relocation), planners MUST understand that argparse defaults are frozen at module-import; setting `AI_SDLC_VAULT_ROOT` mid-process does NOT re-evaluate the default. This is consistent with the §Consumer-freeze cascade contract above and is NOT a new behavior — pre-slice-068 the argparse default was a hardcoded literal evaluated at the same import-time moment.

## MEPD-1 Inclusion-heuristic posture (methodology-changelog v0.70.0 + PMI-1 5-part bump)

**Decision: EXCLUDE** — NO `## v0.70.0` entry, NO PMI-1 bump.

Per **MEPD-1** (`methodology-changelog.md` v0.45.0) Inclusion-heuristic:

| Criterion | This slice |
|-----------|------------|
| Mints a new methodology rule (`RULE-ID`)? | No — no new rule |
| Adds a new audit surface? | No — `test_vault_root_constant.py` is a unit-test pin, not an audit |
| Adds a new consumer-propagation obligation (RPCD-1 / SCPD-1)? | No — no shippability catalog row needed |
| Adds a new CLAUDE.md / SKILL.md prose surface? | No — zero markdown edits |
| Changes user-facing behavior of any skill/tool? | No — pure mechanical refactor, byte-equivalent runtime behavior |

All 5 criteria EXCLUDE → MEPD-1 Inclusion-heuristic posture is EXCLUDE. No methodology-changelog entry, no version bump. The slice ships at v0.69.0 unchanged.

Audits remaining quiescent at pre-finish:
- PMI-1 (`plugin_manifest_audit.py`) — `_vault_paths.py` leading-underscore auto-excludes from inventory; no manifest edit; version stays at 0.69.0; clean.
- OSDG-1 / mini-CAD / CAD-1 — zero `skills/*/SKILL.md` and `agents/*.md` edits; nothing to drift.
- INST-1 (`install_audit.py`) — no installed-template changes.
- BCR-1 — this slice is NOT closing a `**Closes:** SC-NNN` sentinel (it's a user-intent slice from `/query-design` 2026-05-25, not from `diagnose-out/backlog.md`); reflection MUST note "NOT a BCR-1 round-trip".

## Naming refinement (vs mission brief)

Mission brief AC1 names the module `tools/vault_paths.py` (no underscore). **Design refines this to `tools/_vault_paths.py`** (leading underscore) per the `tools/_stdout.py` / UTF8-STDOUT-1 precedent. Rationale: `tools/plugin_manifest_audit.py:148` excludes leading-underscore modules from PMI-1 enumeration (`if p.name != "__init__.py" and not p.name.startswith("_")`); a public-shaped name would force a `plugin.yaml` `tools:` entry which is wrong for a leaf utility with no `main()`. The mission-brief AC1 hedge `(or `tools/paths.py` or similar)` covers this refinement explicitly.

## Test-first plan finalization

10 TF-1 rows (mission-brief's 9 + 1 new row per /critique M1 ACCEPTED-FIXED for consumer-freeze pinning). Concrete test bodies (locked here, written before any implementation per TF-1):

| AC | Test function | Body sketch |
|----|---------------|-------------|
| 1 | `test_vault_root_module_exports_constant` | `import tools._vault_paths; assert hasattr(tools._vault_paths, "VAULT_ROOT")` + `from pathlib import Path; assert isinstance(tools._vault_paths.VAULT_ROOT, Path)` |
| 1 | `test_vault_root_default_equals_path_architecture` | unset env via monkeypatch + reimport via `importlib.reload`; assert `VAULT_ROOT == Path("architecture")` |
| 2 | `test_all_tools_modules_import_vault_root` | grep-style: for each module in 8-element `_MIGRATION_SITE_ALLOWLIST`, parse AST and assert `tools._vault_paths` is imported AND `VAULT_ROOT` is referenced |
| 2 | `test_no_orphan_architecture_literal_in_migrated_tools` | for each migrated file, grep for `Path("architecture")` / `"architecture/"` literals; assert each occurrence carries the `# VAULT_ROOT-routed (slice-068)` marker OR is on a comment/docstring/error-message-string line (the explicit EXCLUDED-error-message-string sites — `cross_spec_parity_audit.py:335`, `state_transition_pin_audit.py:374,388,400`, `validate_slice_layers.py:521` — carry the `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` marker and are accepted by this test) |
| 2 | `test_shippability_decoupling_audit_tuples_preserve_literal` | parse `tools/shippability_decoupling_audit.py` AST; assert lines 91-92 still contain the literal `("architecture", "slices", "archive")` and `("architecture", "build-checks.md")` tuples (regression-pin against accidental migration of the AST-pattern allowlist) |
| 3 | `test_full_pytest_baseline_preserved` | structural pin — assert this slice's added test count is exactly 10 (per /critique M1 ACCEPTED-FIXED adding the freeze pin); full pytest run is gated by `/build-slice` pre-finish, not duplicated here |
| 3 | `test_migration_is_idempotent` | scripted re-application: take 1 migrated file, apply the migration transform a second time, assert empty diff |
| 4 | `test_env_var_override_via_subprocess` | `subprocess.run([sys.executable, "-c", "from tools._vault_paths import VAULT_ROOT; print(VAULT_ROOT)"], env={**os.environ, "AI_SDLC_VAULT_ROOT": "/tmp/foo"})` — assert stdout == `/tmp/foo\n`; Windows-equivalent path used on Windows runner |
| 4 | `test_migration_site_allowlist_pinned` | the 8-element `_MIGRATION_SITE_ALLOWLIST` (file paths) is a module-level frozenset: `{tools/build_checks_integrity.py, tools/critique_review_prerequisite_audit.py, tools/cross_spec_parity_audit.py, tools/risk_register_audit.py, tools/slice_queue_writer.py, tools/state_transition_pin_audit.py, tools/supersede_audit.py, tools/validate_slice_layers.py}`. Assert it matches the actual grep result for `tools/*.py` files containing filesystem-resolving `"architecture"` literals (catches new tool modules added post-slice-068 that hardcode `Path("architecture")` without migrating, AND would have caught the missed `build_checks_integrity.py:78` site if this audit had existed pre-slice-068 — per /critique B1 lesson). |
| 4 (NEW per /critique M1) | `test_consumer_constants_are_frozen_at_first_import` | empirical regression-pin: `import tools.slice_queue_writer`; capture `tools.slice_queue_writer._INDEX_MD_REL`; `monkeypatch.setattr(tools._vault_paths, "VAULT_ROOT", Path("/tmp/foo"))`; assert `tools.slice_queue_writer._INDEX_MD_REL` is UNCHANGED (the freeze contract). Documents the production-correctness semantic AND warns test authors that in-process monkeypatching of `VAULT_ROOT` does NOT propagate to already-frozen downstream consumer constants. Pinned per ADR-065 §Decision freeze contract. |

## Scope discipline reminder

This slice's scope is **constant introduction + 8-site migration + 1 new test module + 1 new ADR**. Out of scope (per mission-brief §Out of scope): the rename (slice-069), un-gitignore (slice-069), cross-machine claim semantics (slice-070), SKILL.md prose path references (deliberately preserved as default-layout documentation), test-fixture archive references (ADR-030 verbatim-corpus preservation), `graphify-out/` / `diagnose-out/` analogous constants (deferred).

A discovered defect surfaced during `/slice` Step 6.5: `tools/slice_queue_writer.py`'s graphify blast-radius rendering leaks raw node dicts into the `Blast-radius:` column when hint files match graphify nodes (visible at `architecture/slice-queue.md:18,34,42`). This is **out of scope** for slice-068 — it's a slice-067 PSQ-1 v1 defect, will be recorded in `reflection.md` "Discovered" + likely a future small slice candidate.
