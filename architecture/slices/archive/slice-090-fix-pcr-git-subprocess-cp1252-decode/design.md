# Design: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Date**: 2026-05-31
**Mode**: Standard

## What's new

- Add `encoding="utf-8"` to the **9 output-decoding** git `subprocess.run(...)` calls in `tools/parallel_conflict_resolver.py` — the sites that pass `capture_output=True, text=True` and therefore decode stdout: **L623, L666, L713 (`_git_show_stage`), L787, L1508, L1523, L1592, L1937, L1980** (`_extract_u_files`'s `git status --porcelain`, `_git_show_stage`'s `git show :N:path`, the `git rev-parse HEAD` / `git diff` / `git status` sites). Decoding becomes locale-independent (UTF-8), so git's UTF-8 output round-trips on a cp1252 host instead of crashing the pipe-reader thread.
- **Intentionally NOT touched — the 4 byte-mode git staging sites at L397, L403, L1378, L1384** (`git add` / `git rebase --continue` in `resolve_soft_conflict` + `resolve_vault_claim_conflict`): these use `capture_output=True` WITHOUT `text=True`, so they capture **bytes** and never decode stdout — output is only surfaced via `{exc!r}` on `CalledProcessError`. Adding `encoding=`/`text=` to them would change the byte/text contract + the `exc` repr shape for no benefit. They are out of scope by design (per B1).
- A structural regression test (`tests/methodology/test_parallel_conflict_resolver_git_encoding.py`): AST-scan the module; for every `subprocess.run` call whose argv begins with the literal `"git"` **AND that decodes output (i.e. `text=True` is present)**, assert an `encoding="utf-8"` keyword is present. The predicate keys on **`text=True`-presence, NOT raw `capture_output`**, so the 4 byte-mode staging sites are correctly excluded (B1 fix). The test asserts the match set is **exactly the 9 decode sites** (count-pinned) and its docstring enumerates the 4 byte-mode exclusions by line. Per APED-1, the finished test is executed against the real module and confirmed to land on exactly those 9 before being declared PASSING. Recurrence-proofs the bug class without a wrapper abstraction.
- [[ADR-082]] — the UTF-8-strict git-decode convention for this module.

## What's reused

- `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` — the failing repro (test-first; established by `/repro`, shippability [[shippability#95]]).
- UTF-8 stdout precedent: `tools/_stdout.reconfigure_stdout_utf8()` (UTF8-STDOUT-1, [[slice-088-add-project-frame-synthesizer]]) — **separate concern** (stdout encoding, not subprocess input decode); reused only as the conceptual precedent, not the mechanism.
- Existing fixture pattern: `_stage_rebase` in `tests/methodology/test_parallel_conflict_resolution_log_hard.py`.

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: classify + auto-resolve parallel-slice rebase conflicts (PCR-1/2a/2b). Reads git conflict-stage content + status via `subprocess.run`.
- **Change**: each of the **9 output-decoding** git `subprocess.run` calls (those passing `text=True`) gains `encoding="utf-8"`. The 4 byte-mode staging calls are untouched. No signature changes, no control-flow changes, no new public API. The existing `except (subprocess.CalledProcessError, FileNotFoundError)` fall-throughs are preserved verbatim.
- **Key interactions**: invoked by `skills/commit-slice/SKILL.md` (CLI sub-step 2.5) and the PCR test suite. Internal-only change → callers unaffected.

## Contracts added or changed

None. No endpoint/event/CLI-flag change. The `--resolve-soft` / `--verify-resolution` / `--record-hard-resolution` CLI surface is untouched.

## Data model deltas

None.

## Wiring matrix

This slice introduces no new **source** modules — it modifies one existing module and adds one **test** file. Zero-row matrix (clean per WIRE-1).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-082]] — git subprocess output in `parallel_conflict_resolver.py` is decoded as UTF-8 with **strict** errors; per-call `encoding="utf-8"` (no wrapper), recurrence-guarded by an AST source-scan test — reversibility: **cheap**.

## Authorization model for this slice

N/A — no auth surface. Pure local git-subprocess decoding.

## Test-coverage model (per /critique-review M-add-1)

Two layers, deliberately split by platform:
- **AC#1 behavioral repro** (`tests/bugs/test_pcr_git_subprocess_cp1252_decode.py`) — runs ONLY on a non-UTF-8 host (Windows/cp1252; `skipif(_host_decodes_utf8_natively())`). Proves the actual round-trip at runtime. Executes for real on the dev's Windows machine where the shippability catalog runs; **skips on UTF-8 CI** (the bug genuinely cannot manifest there).
- **AC#2 AST structural test** (`tests/methodology/test_parallel_conflict_resolver_git_encoding.py`) — runs on ALL hosts. The **cross-platform recurrence guard**: a future edit that drops `encoding="utf-8"` from a decode site fails this test everywhere.

**Why not a cross-platform behavioral test (fix (i) rejected):** forcing cp1252 subprocess decode on a UTF-8 host is infeasible without altering the production call — empirically confirmed during `/repro` that monkeypatching `locale.getpreferredencoding` does NOT propagate into subprocess's text-mode decode (Python 3.13 resolves the pipe encoding at the C/`_io` level, not via the patchable Python `locale` function; the reader thread still decoded cp1252 after the patch). The residual CI-coverage limitation (no runtime decode assertion on UTF-8 CI; only the AST presence-check) is registered as a residual risk at `/reflect`.

## Error model for this slice

- **No new error codes.** The fix changes how bytes are *decoded*, not which exceptions are raised or caught.
- **Strict decode is deliberate** (mission-brief must-not-defer): all content decoded here is UTF-8 vault markdown (`slice-queue.md`, `shippability.md`, mission briefs) by repo convention. `errors="replace"`/`"surrogateescape"` are rejected — they would silently mojibake real data, re-creating the silent-data-loss class this slice closes.
- **Known residual (out of scope, documented for the Critic):** with strict UTF-8, a *genuinely* non-UTF-8 git payload would still raise inside subprocess's reader thread → `subprocess.run` returns `stdout=None` → the same swallowed-failure shape. This is acceptable because (a) all decoded content is UTF-8 by repo convention, and (b) a non-UTF-8 vault file is a *different* defect. Making the swallowed reader-thread failure itself non-silent (e.g. detecting `stdout is None` after a `returncode==0` git call) is a candidate follow-up, NOT this slice — this slice's contract is "UTF-8 content no longer crashes," proven by the repro.
