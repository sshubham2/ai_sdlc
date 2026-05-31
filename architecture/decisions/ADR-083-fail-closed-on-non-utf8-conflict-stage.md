---
id: ADR-083
title: The PCR conflict-stage reader decodes git bytes explicitly and fails closed (UNKNOWN STOP) on non-UTF-8 stage content, never a silent falsy claim-drop
date: 2026-05-31
slice: slice-091-harden-pcr-decode-non-silent
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-083: Fail closed on a non-UTF-8 conflict stage

## Context

slice-090 ([[ADR-082]]) added `encoding="utf-8"` to every decoding git
`subprocess.run` in `tools/parallel_conflict_resolver.py`, closing the
*host-locale* (Windows cp1252) decode crash. R-30 residual #1 remained open: a
**genuinely** non-UTF-8 git payload (invalid UTF-8 bytes — not a host-locale
artifact) still defeats the strict UTF-8 decode, and `_git_show_stage`
mishandled it.

Empirically confirmed on the dev host (Python 3.13, Windows) AND by mechanism
on POSIX:

- **Windows / text-mode** — `subprocess.run(text=True, encoding="utf-8",
  check=True)` decodes inside the pipe **reader thread**; on invalid bytes the
  thread raises `UnicodeDecodeError` (dumping a traceback to stderr), but
  `subprocess.run` does NOT re-raise — it returns `stdout=None`, returncode 0,
  no exception. `_git_show_stage`'s `return proc.stdout` hands back a falsy
  value.
- **POSIX / text-mode** — the decode runs in `_communicate` and the
  `UnicodeDecodeError` propagates OUT of `subprocess.run`, uncaught by
  `_git_show_stage` (which catches only `CalledProcessError` /
  `FileNotFoundError`) → an unhandled crash.

The falsy return is the dangerous manifestation: the caller guards with
`parse_queue_text(text) if text else {}`, so a falsy stage silently DROPS the
candidate's claim from `claim_history`; `_has_same_candidate_different_identity`
then sees no collision, `classify_conflict` returns SOFT instead of
VAULT_CLAIM, and the conflict auto-resolves — re-admitting the exact silent
VAULT_CLAIM bypass the 082–090 hardening arc closed for the *decodable* case.

## Options considered

1. **Keep text-mode; detect the swallow** — after the text-mode call, treat
   `proc.stdout is None` (Windows swallow) and `except UnicodeDecodeError`
   (POSIX propagate) as the fail signal. *Pros*: preserves slice-090's
   9-decode/4-byte-mode count-pin unchanged. *Cons*: relies on the fragile,
   implementation-coupled `stdout is None` swallow-contract; and on Windows the
   reader thread STILL dumps a scary `Exception in thread Thread-1` traceback to
   stderr on every undecodable stage — noise that reads like a crash inside a
   STOP path. Detects the swallow rather than eliminating it.
2. **Bytes-capture + explicit decode (CHOSEN)** — capture raw bytes
   (`capture_output=True`, no `text=`/`encoding=`) and `.decode("utf-8")`
   explicitly in the main thread. *Pros*: no reader-thread decode → no stderr
   noise; deterministic and identical on every platform; the decode failure is
   a normal catchable `UnicodeDecodeError` in the caller's frame. The textbook
   fix for "the reader thread swallows decode errors" is to not decode in the
   reader thread. *Cons*: `_git_show_stage` moves from a text-decode site to a
   byte-read site, so slice-090's AST count-pin shifts (9→8 decode / 4→5
   byte-mode) and its test + shippability #96 description must be updated.
3. **Decode with `errors="replace"`/`"surrogateescape"`** — never raises.
   *Rejected*: that is silent content-mangling, not fail-closed; it would feed
   corrupted claim text to `parse_queue_text` — a different silent bypass.

## Decision

`_git_show_stage` captures git's output as **bytes** and decodes it explicitly
with strict UTF-8:

- `CalledProcessError` / `FileNotFoundError` → return `""` (stage absent — the
  legitimate asymmetric-stage sentinel; unchanged contract).
- `UnicodeDecodeError` on the explicit decode → raise `_StageDecodeError`, a new
  internal exception that **subclasses `_SoftResolutionError`** carrying
  `ConflictClass.UNKNOWN` plus the offending `stage` + `path`.
- Otherwise → return the decoded string (unchanged contract).

Because `_StageDecodeError` IS a `_SoftResolutionError(UNKNOWN)`, the existing
`except _SoftResolutionError` handler in `resolve_soft_conflict` (the
`_regen_slice_queue` defense-in-depth call site) already converts it to a
fail-closed `STOP(UNKNOWN)` — no new STOP plumbing on that leg.

At the primary call site, `diagnose_conflict` catches `_StageDecodeError`,
records a best-effort audit breadcrumb (`_append_decode_stop_audit` — a distinct
`## Decode-failure STOP (non-UTF-8 stage)` section naming stage + path), and
sets a new `ConflictDiagnostic.claim_extraction_degraded` flag instead of
running the claim-history loop on untrustworthy data. `classify_conflict`
returns `ConflictClass.UNKNOWN` whenever that flag is set — routing the
undecodable stage into the **existing** "unparseable rebase state → UNKNOWN,
never silent-default to SOFT" fail-closed channel, which `resolve_soft_conflict`
already turns into a STOP.

This narrows R-30 residual #1 (it does not mint a new RULE-ID). The repro
`tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` (shippability #98)
pins the fix; slice-090's `test_parallel_conflict_resolver_git_encoding.py`
count-pin is updated to 8 decode / 5 byte-mode, and `_git_show_stage` is the
sole byte-mode site that decodes explicitly (it still carries NO `encoding=` on
the `subprocess.run` call, so the "byte-mode sites carry no `encoding=`"
invariant holds).

## Consequences

- `_git_show_stage`'s success/absent contract is unchanged for callers; only the
  present-but-undecodable case changes (was: silent falsy / crash; now: typed
  fail-closed → UNKNOWN STOP).
- `ConflictDiagnostic` gains a `claim_extraction_degraded: bool = False` field
  (default keeps all existing constructions valid).
- slice-090's AST count-pin test and shippability #96 description move to 8/5.
  The 4 STAGING byte-mode sites are untouched.
- The fix reuses ADR-082's "predicate kernel as reuse seam" intent: a future
  repo-wide `audit-cp1252-decode-pattern-across-tools` slice can lift the
  bytes-capture-then-explicit-decode pattern as the canonical safe form.
- R-30 stays `mitigating` (residual #2 — the UTF-8 CI behavioral-coverage
  limitation — is out of scope and remains open).

## Reversibility

cheap — the change is localized to one helper, one new internal exception, one
diagnostic field, one classify branch, and one best-effort audit helper, all in
`tools/parallel_conflict_resolver.py`. Reverting is a mechanical restore of the
text-mode call (re-opening the residual). No external contract or persisted
format changes.
