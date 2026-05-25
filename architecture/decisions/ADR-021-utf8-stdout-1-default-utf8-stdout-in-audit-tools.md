---
id: ADR-021
title: UTF8-STDOUT-1 — every tools/*.py with a main() reconfigures sys.stdout / sys.stderr to UTF-8 via a shared helper as the first executable statement
date: 2026-05-15
slice: slice-023-audit-tools-default-utf8-stdout
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-021: Default UTF-8 stdout in audit tools

## Context

Audit tools under `tools/` are invoked from `$PY -m tools.X` by `/build-slice`, `/validate-slice`, `/reflect`, `/critique`, `/critique-review`, and the user directly. The Python interpreter inherits the platform default console encoding for `sys.stdout` / `sys.stderr`. On Windows that's **cp1252**, which lacks U+2192 (`→`) and a substantial fraction of the U+2xxx geometric / arrow / box-drawing plane that legitimately appears in audit output — either as literal symbols inside tool source strings (em-dash `—` IS in cp1252 at byte 0x97, but arrows and most other punctuation U+2xxx are not) or as **interpolated content** from mission-brief.md / build-log.md / design.md.

The recurrence pattern is empirically established across N=6 slices:

- **slice-007** (2026-05-10, CAD-1 codification) — first witnessed at `tools/critique_review_audit.py` console output (slice-007 DEVIATION-2 in reflection.md); workaround `$env:PYTHONIOENCODING = "utf-8"` applied inline.
- **slice-016** (2026-05-13, RPCD-1 codification) — N=2 cumulative; same tool surface, recurrence under same workaround pattern.
- **slice-018** (2026-05-13, RPCD-1 sibling cleanup) — N=3 cumulative; promotion threshold (N=3) MET. Aggregated lessons named `audit-tools-default-utf8-stdout` as a slice candidate for the first time.
- **slice-020** (2026-05-14, BFRD-1 codification) — N=4 cumulative at `tools/critique_review_audit.py`; ELEVATED to HIGHEST-priority for slice-021.
- **slice-021** (2026-05-14, BRANCH-1 codification) — N=5 cumulative at file-write side (`tests/methodology/test_branch_workflow_audit.py` write_text without `encoding="utf-8"`). Companion-side captured; stdout-side still un-coded; ELEVATED to HIGHEST-priority for slice-022.
- **slice-022** (2026-05-15, ADR-020 PR-aware /commit-slice) — N=6 cumulative at `tools/test_first_audit.py` U+2192 arrow interpolated from TF-1 plan content. Witness anchor: `architecture/slices/archive/slice-022-redesign-commit-slice-for-pr-aware-flow/milestone.md` L44 D-5 entry + `validation.md` L113. Cumulative count provenance: shippability.md row 20 (slice-020 "N=3 → N=4"), row 21 (slice-021 "N=4 → N=5"), row 22 (slice-022 "N=5 → N=6"). Slice-022 was user-invoked on PR-aware redesign rather than the cp1252 slice; aggregated lessons ELEVATED to HIGHEST priority for slice-023.

The defer cost is paid at every `/build-slice` + `/validate-slice` + `/reflect` cycle that touches a tool with non-ASCII stdout: 1-3 minutes per affected audit invocation (DEVIATION logging + workaround application + audit re-run). Slice-022's reflection L94: "structurally overdue; defer cost is paid at every cycle that touches a tool with non-ASCII stdout."

A separate but related class — file-WRITE-side default-encoding — was addressed at slice-021 by adopting an explicit `encoding="utf-8"` convention on all `Path.write_text(...)` call sites in tests + tools. This ADR is the **stdout-WRITE side** of the same parent class.

## Options considered

1. **Per-tool inline `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at top of each `main()`** — pros: minimum surface area; no helper module to import; no audit infrastructure needed. Cons: copy-pasted boilerplate in 16+ files; impossible to test centrally; impossible to enforce by structural audit (regex on every file is brittle); future tools forget the boilerplate at high rate.

2. **Module-level side-effect import (`tools/_stdout_init.py` imported by every tool, reconfigures at import time)** — pros: one-line per tool (`import tools._stdout_init`). Cons: import-time side-effects break tests that intentionally write cp1252 fixtures to stdout via `capsys`; surprise behavior for any code that imports a tool module without invoking `main()` (test discovery, REPL exploration); violates "no module-side-effect imports" Python convention.

3. **Shared helper module `tools/_stdout.py` with `reconfigure_stdout_utf8()` function, called explicitly as first statement of every `main()`, enforced by AST-based structural audit `tools/utf8_stdout_audit.py`** (chosen) — pros: explicit invocation (no surprise side-effects on import); centralized helper means single fix-site for cross-cutting concerns (e.g., adding stdin reconfigure later); AST-based audit is robust (no regex brittleness); idempotent helper is safe to call from tests; `errors="replace"` graceful degradation; testable centrally + per-tool. Cons: 16 tools each get a 2-line modification (import + first-statement call); new structural audit adds 1 more pre-finish gate to maintain.

4. **Shell-side workaround only (`$env:PYTHONIOENCODING = "utf-8"` set globally in PowerShell profile or repo-level `.envrc`)** — pros: zero code change; one-line user config. Cons: invisible to anyone reading the code (no in-repo evidence of the discipline); fragile across user environments (different shells, CI runners, GitHub Actions); fails open if user invokes `python` directly without the env var; not enforceable by any audit. Empirically witnessed at N=6 slices already and continues to fail.

## Decision

**Option 3 chosen**: shared helper module + AST-based structural audit. Rule codified as **UTF8-STDOUT-1** at `methodology-changelog.md` v0.37.0.

The canonical invocation pattern at every `tools/*.py` `main()`:

```python
from tools import _stdout  # or: from . import _stdout

def main(argv: list[str] | None = None) -> int:
    _stdout.reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(...)
    # ... existing main() body unchanged ...
```

The helper at `tools/_stdout.py`:

```python
"""UTF8-STDOUT-1 helper. Idempotent. errors="replace" not "strict"."""
import sys

def reconfigure_stdout_utf8() -> None:
    """Per M6 + M-add-3 ACCEPTED-FIXED: NO encoding short-circuit.

    Stdlib TextIOWrapper.reconfigure is safe to call with the same kwargs
    repeatedly; unconditionally reconfiguring with both encoding="utf-8"
    AND errors="replace" guarantees the post-call state matches the
    slice's required contract regardless of prior state (a prior caller
    may have left errors="strict" — short-circuiting on encoding alone
    would skip our errors="replace" requirement).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        reconfigure(encoding="utf-8", errors="replace")
```

The structural audit at `tools/utf8_stdout_audit.py` AST-parses every `tools/*.py` (excluding `_stdout.py` + `__init__.py`), finds `main()`, and refuses any module where the first executable statement after the docstring is not the canonical `_stdout.reconfigure_stdout_utf8()` call.

**Behavioural regression** at `tests/methodology/test_utf8_stdout_regression.py::test_every_audit_tool_survives_cp1252_stdout_with_u2192_input` (per M5 + M-add-4 ACCEPTED-FIXED — split from audit unit tests for runtime isolation): invokes each audit tool via `subprocess.run(..., text=True, encoding="utf-8", errors="replace", env={"PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0", ...})` against fixture input containing U+2192 (`→`); each subprocess must complete without `UnicodeEncodeError` / `UnicodeDecodeError` traceback in stderr (assertion is encoding-survival, NOT exit-code-0). Per-tool argv strategy enumerated in design.md "Error model" surface 3 (per M1 + M-add-2 ACCEPTED-FIXED — `install_audit` takes `--claude-dir`, NOT `--root`; `mock_budget_lint` requires positional `files`; `validate_slice_layers` requires `--slice`).

**Self-application N=1 canonical reference instance at codification time**: `tools/utf8_stdout_audit.py` itself conforms to UTF8-STDOUT-1; the audit run on the post-slice-023 codebase declares all 17 tools clean.

## Consequences

**Immediate** (slice-023 ship):

- 17 `tools/*.py` files conform to UTF8-STDOUT-1 (16 modified + 1 new audit).
- 1 new helper module + 1 new audit module under `tools/`.
- `plugin.yaml.tools` adds `utf8_stdout_audit`; `_CANONICAL_TOOLS` in `tools/install_audit.py` mirrors; PMI-1 + INST-1 atomic at v0.37.0.
- `methodology-changelog.md` v0.37.0 entry; ADR-021 (this file); `architecture/shippability.md` row 23.
- N-surface schema-pin shape: cross-slice ordinal N=9 (slice-022 pin shape) → N=10 (slice-023 pin shape) stable. Within-slice surface count: N=3 surfaces — helper-module path (`tools/_stdout.py`) + audit-module path (`tools/utf8_stdout_audit.py`) + first-executable-statement invocation phrase. Two distinct counters per m2 ACCEPTED-FIXED.
- -D suffix rule-ID convention: UTF8-STDOUT-1 does NOT carry `-D` suffix (runtime structural discipline, distinct from /critique-time -D family RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 / TPHD-1 / BFRD-1). Convention N=5 stable preserved per slice-019 LAYER-EVID-1 / slice-021 BRANCH-1 precedent (BRANCH-1 + LAYER-EVID-1 also lack -D).
- ADR-pin convention N=8 (slice-022) → N=9 stable (ADR-021 added).
- PMI-1 v1.1 retirement-proof N=8 (slice-022) → N=9 stable (ninth atomic version bump 0.36.0 → 0.37.0; zero gate-body modification).

**Downstream** (post-slice-023):

- `$env:PYTHONIOENCODING = "utf-8"` workaround in PowerShell sessions becomes unnecessary at audit-tool-invocation sites. Any docs / build scripts referencing it can drop it as cleanup (NOT in this slice's scope per Limitations item 11 of design.md).
- Future tools added under `tools/` MUST conform to UTF8-STDOUT-1 from the start, enforced by the audit at every `/build-slice` Step 6.
- The helper is the future extension point for adding `sys.stdin` reconfigure if a future audit reads non-ASCII from stdin (out of scope this slice; deferred to whichever slice surfaces that need).
- Test-capture compatibility: pytest's `_pytest.capture` streams typically lack `reconfigure` attribute → helper no-ops correctly. Verified at `tests/methodology/test_stdout_helper.py::test_reconfigure_noop_on_streams_without_reconfigure_attribute`.

**Cost-of-reversal** (cheap):

- Reversal mechanism: delete `tools/_stdout.py`, delete `tools/utf8_stdout_audit.py`, revert 16 tool one-line additions, retire UTF8-STDOUT-1 from methodology-changelog (supersede via new ADR), drop `plugin.yaml` + `_CANONICAL_TOOLS` entries. ≈30 minutes of mechanical change.
- Reversal scenario: extremely unlikely. The only reason to revert would be if a newer Python release made `sys.stdout.reconfigure` raise on common stream types — at which point the helper's `getattr(stream, "reconfigure", None)` guard would no-op (errors="replace" wouldn't even fire) and behaviour would degrade to pre-UTF8-STDOUT-1 — equivalent to revert without code change.

## Reversibility

**Cheap**. Tagged per /design-slice Step 3 rubric: "cheap = UI tokens, log format, library swap that's a 1-hour change → lock now." Slice-023 fits the "log format" / "I/O encoding default" bucket — pure mechanical change in one logical module-pair (`_stdout` + `utf8_stdout_audit`) plus 16 mechanical one-line additions. Reversal requires no schema migration, no contract break with external consumers (none exist per [[architecture/triage.md]] adoption-record), no data backfill, no user re-training.
