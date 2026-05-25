---
id: ADR-002
title: VAL-1 Layer B uses explicit --imports-allowlist flag rather than auto-derive from project conventions
date: 2026-05-09
slice: slice-003-add-val-1-imports-allowlist
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-002: VAL-1 Layer B uses explicit `--imports-allowlist` flag

## Context

VAL-1 Layer B (the dependency-hallucination check in `tools/validate_slice_layers.py`) is a Python `ast`-based audit that flags every import not found in stdlib, declared deps (`pyproject.toml` / `requirements.txt`), or a small `_KNOWN_ALIASES` table. It exists to catch AI hallucinations like `import some_pkg_that_does_not_exist` before they ship.

In practice across slice-001 and slice-002, every slice that touches `tests/` or `tools/` produced 3–6 false-positive `hallucinated-import` findings:

- `from tests.methodology.conftest import REPO_ROOT` — `tests` is a pytest-conventional namespace test root, NOT declared as a pip package
- `from tools.validate_slice_layers import …` — `tools` IS declared in `[tool.setuptools] packages = ["tools"]` per INST-1 (v0.20.0), but Layer B never read that table

Both are real packages from Python's perspective; both fail Layer B's resolution; both have to be deferred-with-rationale every slice. The `tools` case is fixable automatically (read the setuptools-packages table). The `tests` case isn't pip-package-shaped — it has no `__init__.py` at the top level (it's a PEP 420 namespace package mounted by pytest's rootdir machinery), so no static metadata lists it as a "package."

For the `tests` case (and similar future cases — `scripts/`, `examples/`, `docs/conf.py`-style sphinx roots), Layer B needs a way to extend the resolved set per project. The question is what shape that mechanism should take.

## Options considered

1. **Explicit CLI flag (`--imports-allowlist <name>`, repeatable).** Project author opts in via skill prose: `--imports-allowlist tests` becomes part of the canonical /validate-slice invocation in `skills/validate-slice/SKILL.md` Step 5b.
   - Pros: deterministic — the audit's behavior is fully captured by its arguments; trivial to grep the codebase to learn what's allowlisted; no hidden magic; consistent with the rest of the methodology tooling's "explicit over implicit" pattern (see `--skip-secrets`, `--skip-deps`, `--no-carry-over`, `--imports-allowlist`)
   - Cons: requires the user to know the flag exists; adds a tiny burden to /validate-slice invocations
   - Reversibility: cheap — a future slice can layer auto-derivation on top without removing the flag

2. **Auto-derive from `tests/__init__.py` presence.** If `<repo>/tests/__init__.py` exists, treat `tests` as resolved.
   - Pros: zero-config for the common case
   - Cons: this repo has `tests/methodology/__init__.py` and `tests/skills/__init__.py` but NO `tests/__init__.py` (namespace package pattern); the heuristic would silently miss this very repo. Generalizing the heuristic to "any directory with a Python module under it" makes Layer B's resolution rules opaque ("why didn't my import get flagged? where's the rule?")
   - Reversibility: cheap once shipped, but invisibly catching cases is hard to debug

3. **Read `[tool.pytest.ini_options] testpaths` from pyproject.toml.** Auto-resolve every entry as an allowlisted import root.
   - Pros: aligned with what pytest actually thinks about test roots
   - Cons: not every project declares `testpaths`; this repo doesn't; the heuristic would still need a fallback. Also conflates "pytest test root" with "Python import root that's not pip-installed" — the two are usually equal but conceptually distinct
   - Reversibility: cheap

4. **Read all top-level directories with `*.py` files at the root.** Treat every such directory as a resolved package.
   - Pros: zero-config
   - Cons: catastrophically permissive. Any AI-hallucinated import like `from random_typo_pkg import …` that happens to share a name with a top-level directory would resolve. Defeats Layer B's whole purpose.
   - Reversibility: cheap to roll back, but the hallucinations slipping through during the rollback window aren't reversible

5. **Combine option 1 (explicit flag) with the additional automatic step of reading `[tool.setuptools] packages`** (the explicit-list form only, NOT the `find` auto-discovery).
   - Pros: gets the `tools` case for free in this repo (and in any project that explicitly declares its packages); leaves `tests` and other non-package roots to the explicit flag
   - Cons: setuptools `find` auto-discovery is more popular in newer projects; v1 will miss those without the flag
   - Reversibility: cheap — `find` support can be layered on later

## Decision

Choose **option 5**: explicit `--imports-allowlist <name>` (repeatable) flag PLUS auto-read of `[tool.setuptools] packages` (explicit-list form only). The combination retires the most pain (the `tools` case) automatically while keeping the non-pip-package case (the `tests` case) under explicit user control.

The flag's value is name-normalized via `_normalize_pkg` for consistency with how `declared` already stores PEP 621 / Poetry / requirements.txt entries. (Note: `_normalize_pkg` is the codebase's own convention — lowercase + collapse `[-_.]+` to single `_`. This deviates from strict [PEP 503](https://peps.python.org/pep-0503/) which mandates collapsing to a single hyphen `-`. The codebase deliberately uses underscores so the normalized form matches Python import names directly. Calling it "PEP 503-normalized" elsewhere in the codebase — including the existing `test_normalize_pkg_pep503` test name — is a documentation accuracy bug; this ADR uses "name-normalized" to avoid propagating it.) Empty / whitespace-only values are rejected at the CLI parse boundary (`parser.error`) for hygiene.

## Consequences

- The `skills/validate-slice/SKILL.md` Step 5b prose now documents both new resolution paths. The canonical example invocation in this repo evolves to `--imports-allowlist tests` (since /validate-slice is THE primary caller and pytest test files are routinely in the changed-files list).
- Future projects adopting the AI SDLC pipeline that ALSO use `[tool.setuptools.packages.find]` auto-discovery will see false-positive findings on their own packages until they (a) switch to explicit `packages = [...]`, (b) add `--imports-allowlist <pkg>` for each, or (c) wait for a follow-on slice to add `find`-mode support to `parse_declared_deps`.
- **Dotted-only declarations are partially served**: a project that declares `packages = ["mypkg.sub", "mypkg.subsub"]` with NO bare `"mypkg"` entry will have `mypkg_sub` and `mypkg_subsub` added to `declared`, but `from mypkg.sub.x import y` resolves on `import_top = "mypkg"` which is NOT in `declared`. The flat-list reading silently underserves this case. Workaround for affected projects: add `--imports-allowlist mypkg`. A follow-on slice could extend the loop to also add the top component of dotted names; this v1 deliberately keeps it simple and explicit.
- `_check_import_resolves` signature is unchanged. The `declared` set it consumes is augmented upstream (in `run_layers`) before being passed in. This keeps the resolve-check function simple and its order of resolution (stdlib → declared → alias) intact.
- The Python API gains `run_layers(imports_allowlist=…)` for programmatic / test usage. CLI plumbs `--imports-allowlist` flags through unchanged. Python API is **lenient** (silently skips empty-after-normalize entries); CLI is **strict** (rejects via `parser.error`). Asymmetry is deliberate: be liberal in what you accept programmatically, strict at user-facing boundaries.
- Existing 30+ tests in `test_validate_slice_layers.py` continue to pass with no modification, because `imports_allowlist=None` (default) is byte-equivalent to today's behavior on the augmented `declared` set.

## Reversibility

**Cheap.** Removing `--imports-allowlist` would mean: drop the argparse entry (3 lines), drop the kwarg from `run_layers` (~3 lines), revert the SKILL.md Step 5b prose (~6 lines), delete 7 test functions in `test_validate_slice_layers.py`. Total revert: ~30–60 minutes. The setuptools-packages auto-read is similarly cheap to revert (~5 lines).

The only thing that's somewhat costly to revert is the methodology / skill-prose precedent: once `/validate-slice` users have grown used to writing `--imports-allowlist tests` in their canonical invocation, taking it away in a future slice would be a behavior break. But that's a "this is now the supported shape" problem, not a code-revert problem.
