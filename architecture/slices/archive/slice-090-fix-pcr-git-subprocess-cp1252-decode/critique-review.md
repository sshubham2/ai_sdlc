# Critique Review: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-31
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary
The first Critic's six findings are all substantively VALID and the Builder's draft resolutions are sound; the site-partition (9 `text=True` decode + 4 byte-mode, all literal `["git", …]` argv) is verified correct against source (probe 3 clears). However, the first Critic missed the most important defect in this slice's test strategy: **AC#1's two repro tests are fully skipped on any UTF-8 host (`pytestmark = skipif(_host_decodes_utf8_natively())`), so on UTF-8 CI the ONLY guard is the AST presence-scan (AC#2) — which proves the kwarg is typed, not that decoding works.** A verification-coverage gap (Hendrickson) the first Critic did not surface. B1's severity is also adjusted.

## Confirmed findings
- **B1** — confirmed real; the rewritten predicate (key on `text=True`, count-pin 9) is the right fix. Sites L397/403/1378/1384 are `git add`/`git rebase --continue` with `capture_output=True` and NO `text=True`, so the naive predicate would have false-failed. (Severity adjusted below.)
- **M1** — confirmed; Major appropriate. Exactly 13 `subprocess.run` sites, 9 with `text=True`; L713 (`_git_show_stage`, the user's actual crash path) was the omitted one.
- **M2** — confirmed; Major appropriate. RPCD-1/SCPD-1 require the AST-test shippability row; ACCEPTED-PENDING at /build-slice is correct sequencing (file verified absent on disk).
- **M3** — confirmed; Major appropriate. TF-1 requires a row per AC; the corrected plan now has them.
- **m1** — confirmed real (severity disputed below, not existence).
- **m2** — confirmed; Minor appropriate. Repro file exists with a self-consistent 089→090 header.

## Suspicious findings
None. Every first-Critic finding maps to a verifiable fact in source or artifacts; no over-reach.

## Missed findings

### M-add-1: AC#1 provides zero regression protection on UTF-8 hosts — the AST test is the sole cross-platform guard, and it cannot detect a runtime decode regression
Per Hendrickson (test-coverage/oracle adequacy) + Fowler (a structural source-scan is not a substitute for a behavioral test). `tests/bugs/test_pcr_git_subprocess_cp1252_decode.py` L98-106 sets `pytestmark = skipif(_host_decodes_utf8_natively())`, skipping BOTH behavioral tests on any UTF-8 host (Linux CI, macOS). On UTF-8 CI the safety net collapses to AC#2's AST presence-check (`encoding="utf-8"` is *typed in source*, not that git output *round-trips at runtime*). Escape paths left open: (a) a future refactor to `encoding=locale.getpreferredencoding()` or a wrapper dropping the kwarg at runtime passes the AST scan if the literal survives but still regresses; (b) the strict-decode `None`-swallow path (m1) is never exercised on CI. **Proposed fix:** (i) add a UTF-8-host-runnable behavioral test that forces cp1252 decoding regardless of host; OR (ii) document in design.md§Error-model + mission-brief that AC#2 is by design the only cross-platform guard and AC#1 is dev-Windows-only, and register that CI-coverage limitation as a residual risk at /reflect. The first Critic verified the tests *exist* but never asked *which tests execute on CI*.
- **Builder draft**: ACCEPTED-FIXED (documentation) + ACCEPTED-PENDING (residual risk at /reflect). **Fix (i) is infeasible** — empirically confirmed during /repro that monkeypatching `locale.getpreferredencoding` does NOT propagate into subprocess's text-mode decode (Python 3.13 reads the encoding at the C/`_io` level, not via the patchable Python `locale` function; the reader thread still decoded cp1252 after the patch). There is no clean seam to force cp1252 subprocess decode on a UTF-8 host without altering the production call. Taking fix (ii): design.md + mission-brief now state the two-layer coverage model explicitly (AC#1 behavioral = dev-Windows/cp1252 only; AC#2 AST = cross-platform structural guard), and the CI-coverage limitation is registered as a residual risk at /reflect alongside the cp1252 risk.

### M-add-2: ADR-082 is module-scoped with no generalization contract, yet `audit-cp1252-decode-pattern-across-tools` is an explicitly queued follow-up
Per Newman (cross-cutting convention consistency) + the project-frame Trajectory. ADR-082 scopes itself module-only, but the AST test is a single-module scanner; the queued follow-up will duplicate or refactor it. Cheap to pre-empt by naming the reuse seam. Minor direction-fit note; slice is correct in isolation.
- **Builder draft**: ACCEPTED-FIXED — one sentence added to ADR-082 Consequences flagging the `argv[0]=="git" AND text=True` predicate as the reusable kernel the follow-up should lift to a repo-wide scanner.

## Severity adjustments

- **B1 — SEVERITY-WRONG: Blocker → Major.** The concern is real but describes a defect in a test that does not yet exist (`test_parallel_conflict_resolver_git_encoding.py` absent; AC#2 PENDING). A flaw in a planned-but-unwritten test, already corrected in the design spec, is a design-correctness Major, not a ship-broken Blocker. Builder action unchanged (predicate fix stands); this corrects the calibration signal.
- **m1 — SEVERITY-WRONG: Minor → Major.** The slice exists to close a silent integrity failure (`_git_show_stage → None → parse_queue_text → {} → VAULT_CLAIM silently auto-resolves as SOFT`). The strict-`errors=` residual re-admits that EXACT silent-claim-drop path for a non-UTF-8 payload (decode raises in reader thread → `stdout=None` → same shape). Per McGraw (don't leave a known integrity-bypass silent) + Wiegers (residual commensurate with the failure it re-admits), the residual warrants a first-class risk-register entry, not a sub-note. Not fix-in-this-slice (the deferral is correct); only the severity label is under-weighted.

## Notes
High confidence on source-grounded findings: all 13 `subprocess.run` sites read, 9/4 partition + literal `["git", …]` argv on every `text=True` site confirmed, no `Popen`/`check_output`/non-literal-argv escape, `pytestmark` skipif confirmed directly. First-Critic pattern: strong on artifact precision (counts, line numbers, TF-1 rows, shippability propagation), light on execution-semantics (verified the fix works on the dev host but never asked which tests run on UTF-8 CI — where M-add-1 lives). Reservation: M-add-1 fix (i) needed a clean monkeypatch seam — the Builder has confirmed none exists, so fix (ii) is the correct, non-over-engineered path for a 0.5-day slice.
