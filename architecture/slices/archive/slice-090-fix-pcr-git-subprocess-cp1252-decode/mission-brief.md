# Slice 090: fix-pcr-git-subprocess-cp1252-decode

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: NEW (unregistered) — cp1252 git-subprocess decode crash in `tools/parallel_conflict_resolver.py`; user-reported firsthand (PCR auto-resolver crashed on a SOFT `slice-queue.md` conflict, forcing manual resolution). Sits in the PCR-1/2a/2b hardening lineage (slices 082–085).
**Test-first**: true  (failing repro established via `/repro` before this brief — `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py`)

## Intent

On Windows (and any host whose `locale.getpreferredencoding()` is a legacy code page, e.g. cp1252), every git `subprocess.run(...)` in `tools/parallel_conflict_resolver.py` runs with `text=True` and **no `encoding=`**, so git's UTF-8 output is decoded with the locale code page. When git output contains a UTF-8 byte that is *undefined* in cp1252 (0x81/0x8D/0x8F/0x90/0x9D — e.g. an emoji or other non-Latin char in conflicted content), the decode raises `UnicodeDecodeError` **inside subprocess's pipe-reader thread**. `subprocess.run` does not re-raise it; it returns `stdout=None`/truncated, so the helper hands back `None` and the resolver either crashes downstream or **silently mis-resolves** (a dropped claim turns a real VAULT_CLAIM collision into a SOFT auto-merge). This slice forces UTF-8 decoding on every git subprocess call so the auto-resolver works on Windows and stops silently losing claim data.

## Acceptance criteria

1. Both reproduction tests in `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` PASS (currently FAILING) — `_git_show_stage` round-trips UTF-8 stage content losslessly, and `diagnose_conflict` extracts claims from a slice-queue.md whose content carries a cp1252-undefined byte.
2. All **9 output-decoding** git `subprocess.run(...)` invocations in `tools/parallel_conflict_resolver.py` (the `text=True` sites: L623, L666, L713, L787, L1508, L1523, L1592, L1937, L1980) pass `encoding="utf-8"` — no git subprocess decodes via the host locale code page; the 4 byte-mode staging sites (L397/403/1378/1384) are intentionally excluded. Verified by the AST structural test `tests/methodology/test_parallel_conflict_resolver_git_encoding.py`, which count-pins the match set to exactly 9.
3. No behavioral regression: the PCR suite `pytest tests/methodology/test_parallel_conflict_*.py tests/methodology/test_pcr_*.py tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` all pass, and shippability entry #95 (+ the new AST-test row) pass.

## Test-first plan

Per **TF-1** — the failing tests were written by `/repro` BEFORE this brief; they progress WRITTEN-FAILING → PASSING during build.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | integration | tests/bugs/test_pcr_git_subprocess_cp1252_decode.py | test_git_show_stage_decodes_utf8_content_on_cp1252_host | PASSING |
| 1 | integration | tests/bugs/test_pcr_git_subprocess_cp1252_decode.py | test_diagnose_conflict_extracts_claims_from_utf8_slice_queue_on_cp1252_host | PASSING |
| 2 | structural | tests/methodology/test_parallel_conflict_resolver_git_encoding.py | test_all_git_decode_sites_specify_utf8_encoding | PASSING |
| 2 | structural | tests/methodology/test_parallel_conflict_resolver_git_encoding.py | test_exactly_nine_git_decode_sites_byte_mode_sites_excluded | PASSING |
| 3 | regression | tests/methodology/test_parallel_conflict_resolution_log_hard.py | test_hard_conflict_audit_section_appended | PASSING |
| 3 | regression | tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py | test_vault_claim_event_row_format | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro tests pass | `<interp> -m pytest tests/bugs/test_pcr_git_subprocess_cp1252_decode.py -q` → 2 passed (on Windows/cp1252); on a UTF-8 host they skip (bug genuinely absent) |
| 2 | All git subprocess calls encode UTF-8 | Grep `subprocess.run(` in `tools/parallel_conflict_resolver.py`; every git call passing `text=True`/`capture_output=True` also passes `encoding="utf-8"`. Pinned by a structural test asserting no `text=True`-without-`encoding` git call remains. |
| 3 | No regression | `<interp> -m pytest tests/methodology/test_parallel_conflict_resolution_log_hard.py tests/methodology/test_parallel_conflict_resolution_log_vault_claim.py tests/methodology/test_parallel_conflict_resolver_truncated_baseline.py tests/methodology/test_parallel_conflict_resolver_tool_inventory.py -q` → all pass |

## Must-not-defer

- [ ] Fix **all 9** output-decoding (`text=True`) git `subprocess.run` sites in the file (L623, L666, L713, L787, L1508, L1523, L1592, L1937, L1980), not only the `_git_show_stage` path the user hit — a partial fix leaves the same latent crash on other branches. The 4 byte-mode staging sites (L397/403/1378/1384) are intentionally excluded (B1).
- [ ] Decide and document the `errors=` policy: keep **strict** decoding (default) — do NOT paper over the bug with `errors="replace"`, which would silently mojibake real data (regression of the same silent-data-loss class this slice closes).
- [ ] Error handling preserved: the existing `except (CalledProcessError, FileNotFoundError)` fall-throughs must remain; adding `encoding=` must not change the failure semantics of those branches.
- [ ] Propagate the new AST test (`test_parallel_conflict_resolver_git_encoding.py`) into `architecture/shippability.md` per RPCD-1/SCPD-1 (added at `/build-slice` once the test file exists) — M2.
- [ ] Register the NEW risk (cp1252 git-subprocess decode) in `architecture/risk-register.md` (at `/reflect`). Plus, as **first-class risk-register entries** (NOT sub-notes — per /critique-review m1→Major + M-add-1):
  - **Strict-decode residual** (m1, Major): a genuinely non-UTF-8 git payload still raises in the reader thread → `stdout=None` → re-admits the EXACT silent-claim-drop / VAULT_CLAIM-bypass path this slice closes. Making the swallowed reader-thread failure non-silent is the queued follow-up.
  - **CI-coverage limitation** (M-add-1): on UTF-8 CI the only guard is the AST presence-scan; no runtime decode assertion runs there (the behavioral repro skips). Fix (i) infeasible (monkeypatch doesn't propagate — confirmed at /repro).
  - **Detector-gap**: `stranded_slice_audit` cannot see branchless in-progress slices (slice-089 was invisible to it this session) — fold into the queued `fix-stranded-audit-branchless-blindspot`.

## Out of scope

- Auditing/fixing the same `text=True`-without-`encoding` pattern in **other** `tools/*.py` modules — a real but separate bug class; capture as a follow-up slice candidate (a repo-wide lint rule banning unencoded git subprocess decode would be its own slice).
- Changing `_stdout.reconfigure_stdout_utf8()` / stdout-side encoding (UTF8-STDOUT-1) — that path is already correct and unrelated to subprocess *input* decoding.
- The in-flight slice-089 (commit-slice stale-branch parallel-aware) — independent, proceeding in parallel.

## Dependencies

- Failing repro test (TF-1 prerequisite): `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py::test_git_show_stage_decodes_utf8_content_on_cp1252_host` (+ the `diagnose_conflict` claim-extraction test).
- Vault refs: [[shippability#95]]; PCR lineage [[slice-082-harden-pcr-1-soft-regen-corner-case]], [[slice-084-harden-pcr-2a-clock-skew-winner]]; UTF8-STDOUT-1 precedent [[slice-088-add-project-frame-synthesizer]].
- Code: `tools/parallel_conflict_resolver.py` (`_git_show_stage` L706-722; `diagnose_conflict` L185-225; the ~10 git `subprocess.run` sites).

## Mid-slice smoke gate

At ~50% of build (after editing the `_git_show_stage` + `diagnose_conflict` call sites), run:
```
<interp> -m pytest tests/bugs/test_pcr_git_subprocess_cp1252_decode.py -q
```
Expected: 2 passed. If still failing: STOP — the `encoding="utf-8"` is not reaching the reader-thread decode (verify it's on the right `subprocess.run` call, not a wrapper).

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (all git subprocess sites; strict `errors=`; risk + detector-gap registered)
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
