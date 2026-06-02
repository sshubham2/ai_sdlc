# Code Review: Slice 102 vault-flip-readiness-tests

**code-Critic reviewed**: slice diff vs default branch (base 1987905), filtered to in-scope paths; verified against the live worktree module (`A.__file__` confirmed under `...-wt\slice-102...`)
**Date**: 2026-06-02
**Result**: FINDINGS (0 blockers, 0 majors, 3 minors — advisory in v1)

## Summary
The diff is correct and well-defended. Every design claim verified by execution against the live module: production 4 must-rewrite / 0 needs-human (`baseline_tuple()==_BASELINE`), tests 160 test-update-at-flip / 49 test-collection-pathspec / 0 needs-human, 247 files scanned, deterministic, `--strict` exit 0; full methodology suite 1373 passed; the slice's 27 tests pass. The `_CONTENT_ARG_METHODS` write_text/write_bytes fix is correctly scoped (no false-negative; receiver still caught), tests-surface fail-closed routing is sound (dynamic-fragment + parse-error STAY needs-human and gate CLI exit 2), and the production `--strict` pin is insulated from tests-surface needs-human. 3 minors only — m1 + m3 hardened in-slice; m2 logged.

## Changed files (in-scope)
```
tools/vault_flip_readiness_audit.py
tests/methodology/test_vault_flip_readiness_audit.py
architecture/slices/slice-102-vault-flip-readiness-tests/build-log.md  (flight-recorder prose; not reviewed for code defects)
```

## Findings

### Blockers (advisory in v1)
None. Concerns (a)-(g) all verified correct against the live module:
- (a) `_CONTENT_ARG_METHODS` exclusion introduces NO false-negative: `Path("architecture/x").write_text(c)` receiver-ctor still must-rewrite; `(root/"architecture").write_text(c)` caught via `_is_div_operand`; `joinpath`/`glob`/`with_name` args still caught; the set `{write_text,write_bytes}` is complete.
- (b) `_remap_for_tests` remaps only must-rewrite + unmarked-collection-pathspec; dynamic-fragment + parse-error correctly STAY needs-human (fail-closed).
- (c) `_surface_of`: `skills/foo/tests/helper.py` stays production (no mid-path match); `tools/test_first_audit.py` stays production.
- (d) `_iter_scan_files`: a file named `fixtures.py` is NOT excluded (`.parts` segment check correct); only a `fixtures/` dir is excluded.
- (e) `baseline_tuple()` production-scoped: a tests-surface needs-human does NOT leak into the `--strict` pin AND still drives CLI exit 2 via `main()`.
- (f) floors (120/160, 30/49) appropriately below live; `surface` default does not mask a missing tag.
- (g) deterministic `to_dict()`; `key()` excluding surface has zero collision risk (no path in both surfaces).

### Majors
None.

### Minors

#### m1: `_remap_for_tests` couples to a string-literal reason value (fail-loud, adequately pinned)
- **Claim**: `tools/vault_flip_readiness_audit.py` — `if klass == NEEDS_HUMAN and reason == "unmarked-collection-pathspec"`.
- **Issue**: the reason string is a bare literal produced 30+ lines away in `_classify_constant`; a rename there would silently fall through (collection members stay NEEDS_HUMAN) — though fail-LOUD (`test_tests_surface_needs_human_empty` would fail; production reason pinned at test line 65). Robustness, not a defect.
- **Disposition**: **ACCEPTED-FIXED in-slice** — extracted `_REASON_UNMARKED_COLLECTION` module constant; both `_classify_constant` rule 4 and `_remap_for_tests` reference it (single source of truth).

#### m2: multiline-f-string evidence lineno (CPython quirk) — log only
- **Claim**: `audit_file` emits `node.lineno` for matched Constants incl. fragments in multiline f-strings.
- **Issue**: CPython multiline f-string lineno/col_offset is historically unreliable ([bugs.python.org/issue16806](https://bugs.python.org/issue16806), [cpython#94869](https://github.com/python/cpython/issues/94869)); the audit reports the inner-Constant lineno (verified accurate in probe) so it sidesteps the worst, and remains fail-closed regardless.
- **Disposition**: **LOG-ONLY** (agent: no fix required) — the occurrence is still surfaced + fail-closed; the human reviews the file.

#### m3: `_format_human` summary mislabels cross-surface counts as `[production]` (cosmetic)
- **Claim**: the summary's `[production]` bracket included `already-routed` + `doc/example`, which `by_class` sums across BOTH surfaces (26=24+2; 355=60+295).
- **Issue**: a reader scanning `[production]` would over-count; the itemized listings + JSON `to_dict()` are correct (consumers use JSON). Human-output cosmetics only.
- **Disposition**: **ACCEPTED-FIXED in-slice** — summary now brackets only the surface-exclusive counts (`[production] must-rewrite`; `[tests] update-at-flip + collection-pathspec`) and lists `already-routed`/`doc/example`/`needs-human` as cross-surface totals.

## Dimensions checked
- [x] Unfounded assumptions — none (docstring/comment claims verified against impl; no phantom imports).
- [x] Missing edge cases — none material (empty tree, multiline f-string, backslash rel, fixtures file-vs-dir, parse-error + dynamic-fragment fail-closed, tests needs-human gates exit 2).
- [x] Over-engineering — none (`_CONTENT_ARG_METHODS` justified; `surface` field used).
- [x] Under-engineering — none (every AC has a delivering element + test; must-not-defer all satisfied; cp1252-safe; encoding="utf-8"; RPCD-1/SCPD-1 row 109 present).
- [x] Contract gaps — m1 (string-discriminator coupling; now fixed via constant).
- [x] Security — none (read-only static AST; no shell/eval/network/secrets).
- [x] Drift from vault — none (design.md + ADR-092 claims all hold; `_vault_paths` default untouched; MEPD-1 consistent).
- [x] Web-known issues — m2 (CPython multiline-f-string lineno; benign, logged).
- [x] Cross-cutting conformance — none (RSAD-1 self-exclude survives own scan; APED-1 6 probe batteries + in-file adversarial tests; rule-ordering composition correct — remap applied AFTER classification so production path byte-identical; EOL-DRIFT-1 N/A).
