---
id: ADR-082
title: Git subprocess output in parallel_conflict_resolver.py is decoded as UTF-8 (strict), per-call, recurrence-guarded by an AST test
date: 2026-05-31
slice: slice-090-fix-pcr-git-subprocess-cp1252-decode
reversibility: cheap
status: accepted
---

# ADR-082: UTF-8-strict git-subprocess decode in parallel_conflict_resolver.py

## Context

`tools/parallel_conflict_resolver.py` invokes git via `subprocess.run` at 13 sites —
**9 of which decode output** (`capture_output=True, text=True`: L623, L666, L713, L787,
L1508, L1523, L1592, L1937, L1980) and 4 of which capture **bytes** for error-repr only
(`capture_output=True`, no `text=True`: L397, L403, L1378, L1384). The 9 decode sites
carry no `encoding=`. In text mode with no explicit encoding, CPython
decodes the child's stdout pipe using `locale.getpreferredencoding(False)` — cp1252
on Windows (this project's primary dev platform). When git output contains a UTF-8
byte undefined in cp1252 (`0x81/0x8D/0x8F/0x90/0x9D` — e.g. an emoji or non-Latin
char in conflicted vault content), the decode raises `UnicodeDecodeError` inside
subprocess's pipe-*reader thread*; `subprocess.run` does not re-raise it, returning
`stdout=None`/truncated. The helper then returns `None`, and the resolver either
crashes downstream or — worse — **silently drops claim data**, letting a real
VAULT_CLAIM collision auto-resolve as SOFT. User-reported firsthand (slice-090).

A decision is needed on (1) the decode encoding, (2) the `errors=` policy, and
(3) the fix mechanism (per-call vs. a centralized git-runner wrapper).

## Options considered

1. **Per-call `encoding="utf-8"`, strict errors, + AST regression test** —
   pros: minimal diff to a heavily-tested, sensitive module (lowest regression
   risk); no new abstraction; the AST source-scan test catches recurrence on ANY
   future git call, wrapper or not. cons: ~10 near-identical edits; relies on the
   test (not a structural chokepoint) to prevent recurrence.
2. **Centralized `_run_git()` wrapper that always sets `encoding="utf-8"`** —
   pros: single chokepoint; DRY; a new git call can't forget the encoding.
   cons: changes the shape of all ~10 call sites + their error handling in one go
   (higher regression surface in a sensitive module); introduces an abstraction a
   bug-fix slice doesn't strictly need.
3. **`errors="replace"` / `"surrogateescape"`** — pros: never raises. cons:
   silently mojibakes/round-trips bad bytes — re-creates the exact silent-data-loss
   class this slice exists to close. Rejected.

## Decision

Adopt **Option 1**: add `encoding="utf-8"` (strict — no `errors=` override) to the 9
output-**decoding** git `subprocess.run` calls in `tools/parallel_conflict_resolver.py`
(the `text=True` sites; the 4 byte-mode staging sites are intentionally excluded), and
add an AST source-scan regression test asserting every git `subprocess.run` that
**decodes** output (keys on `text=True`-presence, not raw `capture_output`) carries
`encoding="utf-8"` — count-pinned to exactly those 9 sites. The wrapper (Option 2) is deferred:
minimal diff is safer here, and the AST test provides the recurrence guard a wrapper
would, without the abstraction. Strict errors are chosen because all content decoded
on this path is UTF-8 vault markdown by repo convention; a lossy policy would defeat
the slice's purpose.

## Consequences

- The PCR auto-resolver works on Windows/cp1252; the silent claim-drop VAULT_CLAIM
  bypass is closed for UTF-8 content.
- A new git call in this module that captures output MUST pass `encoding="utf-8"`
  or the AST test fails — a loud, structural recurrence guard.
- The **same `text=True`-without-`encoding` class likely exists in other `tools/*.py`**
  (e.g. `slice_queue_writer.py`, `project_frame_synth.py`, `pulse_worktree_resolver.py`).
  This ADR is scoped to `parallel_conflict_resolver.py` only; the repo-wide audit +
  fix is the queued follow-up `audit-cp1252-decode-pattern-across-tools`. When that
  slice ships, it may generalize this ADR's convention repo-wide (supersede-and-widen).
  **Reuse seam (per /critique-review M-add-2):** the AST predicate `argv[0] == "git"`
  AND `text=True` present → require `encoding="utf-8"` is the reusable kernel; the
  follow-up audit should **lift this predicate to a repo-wide scanner** (parametrized
  over `tools/*.py`) rather than re-derive a per-module copy — `test_parallel_conflict_
  resolver_git_encoding.py` is written single-module but its predicate is the intended
  generalization point.
- No contract / CLI / data-model change; callers (`skills/commit-slice/SKILL.md`,
  the PCR test suite) are unaffected.

## Reversibility

**Cheap.** The change is additive keyword arguments on existing calls plus one test.
Reverting (or later folding into a `_run_git` wrapper) is a localized, low-cost edit
with no external consumers depending on the call shapes.
