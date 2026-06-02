# Code Review: Slice 100 add-vault-flip-readiness-audit

**code-Critic reviewed**: slice diff vs default branch (base 31d78c5; in-scope paths only)
**Date**: 2026-06-02
**Result**: FINDINGS

## Summary

A clean, well-documented read-only audit that runs green (exit 0; 49 files; 4 must-rewrite, 24 already-routed, 60 doc/example, 0 needs-human — matching the slice's claim) and whose 13 tests pass. Registration fan-out complete; B2 `_SOFT_FILE_SET` marker edit semantically inert (PCR pin passes). However, the context-aware classifier has **three latent false-negatives in the silent-breakage direction** (a must-rewrite site silently classed safe) the regression guard cannot catch, plus a documented-but-unimplemented `dynamic-fragment` class. None breaks the current tree, but each undermines the audit's stated purpose. **Builder disposition: all five hardened in-slice (see end).**

## Changed files (in-scope)
- tools/vault_flip_readiness_audit.py (NEW)
- tests/methodology/test_vault_flip_readiness_audit.py (NEW)
- tools/parallel_conflict_resolver.py (MODIFIED)
- tools/install_audit.py (MODIFIED)
- tests/methodology/test_utf8_stdout_regression.py (MODIFIED)
- plugin.yaml (MODIFIED)
- INSTALL.md (MODIFIED)
- architecture/slices/slice-100-add-vault-flip-readiness-audit/build-log.md

## Findings

### Blockers
None. No code path is broken on the current tree, no security/data-ownership defect, no contradiction of an ACCEPTED ADR. The defects below are false-negatives latent against future code, not current-tree breakage.

### Majors

#### M1: `_name_flows_to_path` is structurally dead at module scope — the documented "≤1-hop assigned-name flow" never fires for module-level constants
- **Issue**: rule-3's second clause calls `_name_flows_to_path(name, _enclosing_func(node))`; for a module-level `_DIR = "architecture"` later used in `repo_root / _DIR / "x"`, `_enclosing_func` returns `None` → `_name_flows_to_path` short-circuits `False` → silently classed `doc-example-safe (prose-mention)` — the exact silent-breakage class the slice exists to enumerate.
- **Evidence**: probe `_DIR = "architecture"` + `Path("/r") / _DIR / "x.md"` → `doc-example-safe`, NOT `must-rewrite`; `_name_flows_to_path("x", tree)` → `True` but `(..., None)` → `False`. No test exercises module-level flow. Real-corpus illustration: `tools/vault_write_safety_audit.py:101 _VAULT_SEGMENT = "architecture"` (benign today — membership test, not path-construction).
- **Proposed fix**: fall back to module scope when no enclosing func — `_enclosing_func(node) or _module_root(node)`. Add a test.

#### M2: Whole-line marker substring scan false-routes a genuine path-construction to `already-seam-routed` (the slice-099 lesson, recurring)
- **Issue**: rule 2's `_CLASS_B_MARKER in line_txt` / `_VAULT_ROOT_TOKEN in line_txt` run BEFORE rule-3 path-construction; a real unrouted path-construction with a descriptive prose comment mentioning the marker is silently certified safe.
- **Evidence**: probe `open("architecture/x.md")  # see the Class-B git identity (ADR-089) convention` → `already-seam-routed (class-b-marked)`; `open("architecture/x.md")  # not VAULT_ROOT-routed yet` → `already-seam-routed (vault-root-derived)`. Both unrouted, certified safe by a comment. (Reverse case — marker on a different physical line than `node.lineno` — fails CLOSED to needs-human; acceptable.)
- **Proposed fix**: check path-construction (rule 3) BEFORE the line-text markers, so a resolving context overrides a prose comment. (Class-B git-pathspecs are frozenset members, not path-construction → still reach the marker rule → still already-seam-routed.)

#### M3: `dynamic-fragment` class is documented (ADR-091 / design.md / docstring) but NOT implemented — an ambiguous dynamic path fails OPEN, not closed (drift)
- **Issue**: ADR-091 rule 4 names `dynamic-fragment` as fail-closed `needs-human`; `_classify_constant` rule 4 only implements `_is_collection_member`. An f-string / `+`-concat path whose only constant fragment carries the vault segment, flowing into a path context, is classed `doc-example-safe (prose-mention)` — violating the fail-closed must-not-defer contract.
- **Evidence**: probe `Path("/r") / f"architecture/{name}"` → `doc-example-safe`; `open("architecture/" + name)` → `doc-example-safe`. Neither → `needs-human`.
- **Proposed fix**: implement detection — a matched Constant inside a `JoinedStr` / `+`-BinOp whose composite flows into a path-construction context → `needs-human (dynamic-fragment)`. (Honors the ACCEPTED-ADR contract rather than amending it to a residual, since the fragment IS detectable.)

### Minors

#### m1: `os.path.join(...)` and builtin `open(...)` path-construction sinks not recognized
- **Issue**: `_PATH_CTOR_NAMES`/`_PATH_METHODS`/`_is_div_operand` don't cover `os.path.join("architecture", ...)` or builtin `open("architecture/x.md")` → both classed `doc-example-safe`. No live corpus sites today (`pathlib`-uniform), so the reported 4 must-rewrite is accurate now; latent future miss.
- **Proposed fix**: recognize builtin `open` first-arg + `os.path.join` args as path-construction. Cheap, additive.

#### m2: comment-harvest except tuple narrower than Python 3.12+ tokenizer reality
- **Issue**: `except (tokenize.TokenError, IndentationError)` — CPython 3.12+ raises `SyntaxError` for some malformed input ([#105390](https://github.com/python/cpython/issues/105390), [#105238](https://github.com/python/cpython/issues/105238)); a file that `ast.parse`-s clean but diverges in the standalone tokenizer would crash rather than degrade.
- **Proposed fix**: widen to `except (tokenize.TokenError, IndentationError, SyntaxError)`.

#### m3: docstring rule-4 prose lists "dynamic-fragment" as active, contradicting the code (slice-006 Dim-1 class)
- **Proposed fix**: reconciled by M3's implementation.

## Dimensions checked
- [x] Unfounded assumptions — m3 (docstring vs impl drift). No phantom imports.
- [x] Missing edge cases — M1 (module-level flow), m1 (os.path.join/open), m2 (3.12+ tokenizer).
- [x] Over-engineering — none.
- [x] Under-engineering — M3 (fail-closed dynamic-fragment contract unmet).
- [x] Security — none (read-only audit; one test-only subprocess, fixed argv).
- [x] Drift from vault — M3 (code diverges from ADR-091 rule 4 + design.md error model). AC5 verified (`_DEFAULT = "architecture"` unchanged). Registration consistent. MEPD-1 EXCLUDE honored.
- [x] Web-known issues — m2 (3.12+ tokenizer SyntaxError). `ast.Constant` already 3.14-safe.
- [x] Cross-cutting conformance — M2 (slice-099 whole-line-substring recurrence; APED-1 battery under-executed on the new marker/context rules). RSAD-1: audit passes its own gate. PCR B2 marker frozenset-inert.

## Builder disposition (in-slice hardening — slice-095 "harden now" precedent)

All five findings ACCEPTED + hardened in this slice (a safety audit must not ship known silent-breakage false-negatives):
- **M1** → `_name_flows_to_path` falls back to `_module_root(node)` when no enclosing func.
- **M2** → path-construction (rule 3) checked BEFORE the line-text markers.
- **M3** → `_dynamic_fragment_in_path` implemented → `needs-human (dynamic-fragment)`.
- **m1** → builtin `open` first-arg + `os.path.join` args recognized as path-construction sinks.
- **m2** → tokenize except widened to include `SyntaxError`.
- **m3** → reconciled by M3.

New tests added (APED-1 battery widened per the M2 lesson): module-level-flow → must-rewrite; prose-marker-on-path-construction → must-rewrite (not false-routed); f-string/concat-in-path → needs-human; os.path.join/open → must-rewrite. Baseline re-derived + re-frozen post-fix (see build-log Events).
