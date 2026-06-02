# Validation: Slice 100 add-vault-flip-readiness-audit

**Date**: 2026-06-02
**Result**: PASS

This slice's "real environment" is the live repo: running the audit against the real `tools/` + skill-helper surface, the 17-test module, the full methodology suite, and the shippability catalog. No mocks substitute for real behaviour — the audit is exercised against the actual production code it classifies.

## Per-criterion results

### AC1: deterministic JSON inventory, every literal classified into the 4 classes via AST/tokenize (incl. Class-B + VAULT_ROOT-derived recognition)
- **Status**: PASS
- **Evidence**: `$PY -m tools.vault_flip_readiness_audit --json` on the real tree → 49 files; **4 must-rewrite** (`project_frame_synth.py` 121/122/185/194, reason `path-construction`), **24 already-seam-routed** (incl. PCR `_SOFT_FILE_SET` Class-B-marked + `_vault_paths`/`_vault_git` seam-internal + VAULT_ROOT-derived), **60 doc-example-safe**, **0 needs-human**. Each occurrence carries `path:line:col`, `value`, `klass`, `reason`. Spot-checks confirmed: a Class-B-marked `_SOFT_FILE_SET` member → `already-seam-routed`; an unrouted `repo_root / "architecture" / "x"` → `must-rewrite`; a docstring/comment mention → `doc-example-safe`. `test_emits_classified_inventory_with_evidence`, `test_every_hit_has_exactly_one_class` PASS.
- **Notes**: B-add-1 vindicated — the 4 bare-`"architecture"` path-construction sites a slash-only matcher would have silently certified clean are correctly `must-rewrite`.

### AC2: fail-closed + deterministic
- **Status**: PASS
- **Evidence**: ambiguous inputs → `needs-human` (never dropped): unmarked git-pathspec collection member (`test_ambiguous_literal_routes_to_needs_human_not_dropped`, `test_unmarked_git_pathspec_routes_to_needs_human`), dynamic-fragment (`test_dynamic_fragment_in_path_routes_to_needs_human`), parse-error (one entry/file). Determinism: `audit_root(.).to_dict() == audit_root(.).to_dict()` (`test_output_is_deterministic_across_runs`), stable sort `(path, line, col)`.

### AC3: baseline pin (count + identity, line-independent) + non-vacuity by mutation
- **Status**: PASS
- **Evidence**: `test_must_rewrite_baseline_pinned` — live `baseline_tuple()` == `_BASELINE` (the 4 `project_frame_synth.py` entries), keyed `(relpath, ast value, klass)`. Non-vacuity proven by **two** mutations: a path-construction literal MUST enter must-rewrite (`test_new_unrouted_literal_fails_gate`); an error-message literal MUST NOT (`test_error_message_literal_not_must_rewrite`). **Live demonstration of non-vacuity**: during code-review hardening, an M2 reorder regression mis-classed `_vault_paths.py:53` as a 5th must-rewrite — the baseline pin FAILED loudly and caught it (the guard working exactly as designed).

### AC4: CLI gate semantics
- **Status**: PASS
- **Evidence**: `vault_flip_readiness_audit` → exit 0 (no needs-human); `--strict` → exit 0 (baseline unchanged); a tmp fixture with an out-of-baseline literal under `--strict` → exit 2 (`test_cli_strict_nonzero_on_baseline_drift`). Usage error → exit 1 (tools/ missing). `--root` alias added so the cp1252 regression harness exercises the stdout path.

### AC5: capability-without-flip invariant
- **Status**: PASS
- **Evidence**: `tools/_vault_paths.py` default unchanged — `_DEFAULT = "architecture"`, `VAULT_ROOT == Path("architecture")` (`test_vault_paths_default_unchanged`). Full methodology suite **1345 PASS** + shippability catalog **107/107** → every existing tool/test/skill behaves identically; no flip occurred, fully reversible.

## VAL-1 layered safety checks
- **Layer A (credentials)**: PASS — no committed secrets in the 7 changed files.
- **Layer B (dependency hallucination)**: PASS — all imports resolve (stdlib + `tools` internal pkg + `--imports-allowlist tests`).

## Multi-instance validation
- **Required?**: no — read-only local CLI audit; no multi-user / multi-device / sync surface.
- **Result**: not-applicable.

## Shippability catalog (regression check)
- Pre-catalog gates: SCMD-1 ✅ / PTFCD-1 ✅ / SVW-1 ✅.
- Catalog run: **107 rows, 107 PASS, 0 FAIL** (incl. new #108 = this slice). No past slice broken.

## Reality surprises
- **The code-Critic found 3 latent silent-breakage false-negatives the design+meta stack structurally couldn't reach** (M1 dead module-scope flow, M2 whole-line marker false-route [a slice-099 lesson recurrence], M3 documented-but-unimplemented dynamic-fragment). All hardened in-slice. Reinforces: the code-Critic is a required execution-level pass for any new AST/parser tool (APED-1).
- **The m2 count fan-out is N+1 wider than checklisted**: beyond INSTALL.md prose, two per-tool inventory tests (`test_pulse_worktree_resolver_tool_inventory` / `test_stranded_slice_audit_tool_inventory`) hardcode the L22/L166 count — caught by the full suite, not the first INSTALL bump. (Carry to /reflect.)
- **The AC3 baseline pin caught my own fix-regression live** — concrete evidence that a guard-test proven non-vacuous earns its keep against the builder, not just future slices.
