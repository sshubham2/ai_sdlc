# Code Review: Slice 068 add-vault-root-constant

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-25
**Result**: FINDINGS (1 Major, 4 Minors — no Blockers)

## Summary

Clean, narrowly-scoped mechanical refactor. The 8-site migration is consistent with design.md; markers are present on every migration line; the new `tools/_vault_paths.py` matches the design body verbatim modulo whitespace and respects the leaf-import invariant in practice. Two test-quality gaps surfaced — most consequentially, the design.md L25 + mission-brief must-not-defer #4 explicitly promise a `test_vault_paths_module_is_leaf` regression-pin that is NOT present in the test module; and the `test_migration_is_idempotent` regex only catches one of the four pre-migration literal shapes, so the "idempotency" claim is partially vacuous. Three Minor findings cover the two-marker convention's regex-coverage gap, a freeze-pin assertion that could pass on a no-op monkeypatch, and one cosmetic blank-line drift.

## Changed files (in-scope)

```
tools/build_checks_integrity.py
tools/critique_review_prerequisite_audit.py
tools/cross_spec_parity_audit.py
tools/risk_register_audit.py
tools/slice_queue_writer.py
tools/state_transition_pin_audit.py
tools/supersede_audit.py
tools/validate_slice_layers.py
tools/_vault_paths.py
tests/methodology/test_vault_root_constant.py
```

## Findings

### Blockers

None.

### Majors

#### M1: Leaf-invariant regression-pin promised in design.md + mission-brief is missing from the test module

- **Claim under review**: `design.md:25` — "MUST NOT import from any other `tools/` module (leaf invariant — pinned by `test_vault_paths_module_is_leaf` per AC4)"; reinforced at `mission-brief.md:54` must-not-defer #4 — "Verified by an explicit `ast.parse` test asserting the module's imports are stdlib-only."
- **Issue**: `tests/methodology/test_vault_root_constant.py` does NOT contain a `test_vault_paths_module_is_leaf` function (or any leaf-invariant pin). `grep -n 'leaf\|test_vault_paths_module_is_leaf' tests/methodology/test_vault_root_constant.py` returns zero matches. The TF-1 table in `design.md` L154-165 enumerates 10 test rows; the leaf-invariant pin is not among them — it lives only in prose at design.md L25 and mission-brief.md L54. The current module body (`tools/_vault_paths.py:23-26`) does in fact import only stdlib (`__future__`, `os`, `pathlib.Path`), so the invariant holds at slice-068 ship time; but the promised regression guard does not exist, so a future edit adding `from tools.foo import bar` would not be caught by any test. Per Sommerville (requirements→design→code traceability) and TF-1 discipline this is a missing acceptance-criterion test.
- **Evidence**:
  - `design.md:25` and `mission-brief.md:54` both name the test explicitly.
  - The test module's 10 functions cover AC1-AC4 but none asserts the leaf invariant.
  - `tools/_vault_paths.py:23-26` confirms current compliance: `from __future__ import annotations`, `import os`, `from pathlib import Path` (stdlib only).
- **Proposed fix**: add the 11th test function asserting `tools/_vault_paths.py`'s import-set is stdlib-only via AST walk. Update `test_full_pytest_baseline_preserved` count from `10` to `11`, and update the TF-1 table in design.md and the AC4 prose in mission-brief.

### Minors

#### m1: `test_migration_is_idempotent` only covers `Path("architecture")` shape — 3 of 4 pre-migration literal shapes are not exercised

- **Claim under review**: `tests/methodology/test_vault_root_constant.py:178-198` — the test claims to pin "the migration transform is idempotent" using the regex `r'Path\(["\']architecture["\']\)'`.
- **Issue**: that regex matches exactly one of the four pre-migration shapes the 8-site migration covered. Specifically: `Path("architecture")` MATCHES; `Path("architecture/risk-register.md")`, bare str literals like `"architecture/build-checks.md"`, and `repo_root / "architecture" / "x"` shapes do NOT match. On post-migration code, the regex finds 0 matches → 0 substitutions → trivially equal to input. Any file with no `Path("architecture")` literal passes this test regardless of migration state.
- **Evidence**: empirical regex check confirms only one of four pre-migration shapes matches.
- **Proposed fix**: expand the regex to cover all four shapes OR loop over all 8 files in `_MIGRATION_SITE_ALLOWLIST` asserting each contains zero pre-migration literals outside marker-bearing lines.

#### m2: `test_consumer_constants_are_frozen_at_first_import` passes on a no-op monkeypatch — no assertion proves the patch actually mutated VAULT_ROOT

- **Claim under review**: `tests/methodology/test_vault_root_constant.py:256-290`.
- **Issue**: the assertion is `tools.slice_queue_writer._INDEX_MD_REL == frozen_index_md_rel`. Since both sides are the same captured-then-re-read value of a non-recomputed module constant, the test passes trivially regardless of whether the monkeypatch actually mutated anything. A no-op monkeypatch (or one against the wrong attribute name due to a future rename of `VAULT_ROOT` → `vault_root`) would also pass green.
- **Evidence**: the test does not read `tools._vault_paths.VAULT_ROOT` after the monkeypatch to confirm it equals `Path("/tmp/freeze-pin-test")`.
- **Proposed fix**: add a two-step assertion: first verify the monkeypatch actually mutated `VAULT_ROOT`; then verify the consumer's frozen constant did NOT propagate; AND verify the frozen value is NOT the patched value.

#### m3: Two-marker convention is enforced only for quote-immediately-adjacent `"architecture[/"\\]` shapes — 6+ user-facing-prose sites with `architecture/...` in mid-string are unmarked and untested

- **Claim under review**: `tests/methodology/test_vault_root_constant.py:118` `literal_re = re.compile(r'["\']architecture[/"\\]')`.
- **Issue**: the regex requires `"` or `'` IMMEDIATELY before `architecture` AND `/`, `"`, or `\` IMMEDIATELY after. ~6 lines in `tools/*.py` contain `architecture/...` substring inside larger argparse help strings or error messages but do NOT match the regex. These are conceptually identical to the 5 enumerated EXCLUDED sites but unmarked + untested. The two-marker convention is asymmetric: it holds for sites where the regex catches, not for the broader class the convention rhetorically describes.
- **Evidence**: `grep -n architecture tools/cross_spec_parity_audit.py` shows L329, L374, L378, L382 as user-facing-prose-with-substring sites; only L336 carries the marker.
- **Proposed fix**: either (a) accept the asymmetry and document it explicitly in design.md §Sites EXCLUDED — "marker required only on lines the audit regex matches; substring-in-prose is not covered"; or (b) broaden the regex to `r'architecture/'` and add `# NOT VAULT_ROOT-routed` markers to the additional ~6 prose sites.

#### m4: `tools/supersede_audit.py:53-55` missing PEP-8 blank line between stdlib and tools imports (style drift vs sibling files)

- **Claim under review**: `tools/supersede_audit.py:53-55` — `from pathlib import Path` immediately followed by `from tools import _stdout` and `from tools._vault_paths import VAULT_ROOT` with no blank line.
- **Issue**: PEP 8 and convention of the 7 other migrated files insert a blank line between stdlib and first-party imports. Purely cosmetic — not a bug.
- **Evidence**: sibling files (e.g., `tools/build_checks_integrity.py:67-71`) have the blank line.
- **Proposed fix**: add a blank line between L53 and L54. Trivial; defer to janitorial pass.

## Dimensions checked

- [x] **Unfounded assumptions** — none in code-as-implemented (the docstring at `tools/_vault_paths.py:1-22` accurately describes the module behavior — env-var read at import, freeze cascade, leaf-helper precedent).
- [x] **Missing edge cases** — none surfaced by code-level walkthrough. Empty env var (`AI_SDLC_VAULT_ROOT=""`) → `Path("")` composes acceptably; documented in design §Error model. Absolute env-var override (`AI_SDLC_VAULT_ROOT=C:\alt`) → absolute RHS wins under `pathlib.PurePath.__truediv__` (the desired slice-069 semantic). CRLF vs LF on `re.MULTILINE` `^def test_` works identically. Windows tmp_path subprocess round-trip portable.
- [x] **Over-engineering** — none. `tools/_vault_paths.py` is 9 LOC of code (excluding docstring) for a one-constant module.
- [x] **Under-engineering** — M1 (missing leaf-invariant test), m1 (idempotency test under-covers), m2 (freeze test has assertion gap). All filed above.
- [x] **Contract gaps** — none new in `tools/_vault_paths.py`. No public-API signatures added/changed.
- [x] **Security** — none. No new authn, authz, secrets, injection vectors. `os.environ.get(...)` (not `os.system`/`subprocess`/`eval`); composed structurally not interpolated into shell.
- [x] **Drift from vault** — M1 above (design.md L25 + mission-brief L54 promise a test that does not exist). Minor observation: design.md table L57 lists `cross_spec_parity_audit.py` migration line numbers as `152, 305, 307, 309` but post-migration actual line numbers are `153, 306, 308, 310` (each shifted by 1 from the added import line at L67). Expected pre-vs-post numbering drift; not flagged.
- [x] **Web-known issues** — Skipped — WebSearch not invoked. Slice introduces no new third-party API/SDK calls, no new library dependencies, no version-sensitive language features. The argparse default-eval-at-parser-construction-time behavior is a long-stable Python idiom. Time-box justified.
- [x] **Cross-cutting conformance** — verified. RSAD-1 N/A (no new audit/linter). APED-1 N/A (no existing audit's parse rule modified). EOL-DRIFT-1 clean (test module uses `read_text(encoding="utf-8")` + `.splitlines()` + regex MULTILINE). Zero phantom imports — every `from tools._vault_paths import VAULT_ROOT` resolves. Type-change at `build_checks_integrity.py:78` (`str → Path`) traced through single consumer at L224 (`root / _PROJECT_LIVE_REL` — `Path / Path` composes identically); no f-string interpolation surfaces. Tooling-doc-vs-implementation parity: `tools/_vault_paths.py:1-22` docstring matches implementation at L23-31 verbatim. Runtime-environment semantic documented + pinned.

---

Per CRSI-1 v1 walking-skeleton: findings are advisory; do not block `/validate-slice`. Severity calibration assumes the slice-062 verdict-driven block IS in effect.
