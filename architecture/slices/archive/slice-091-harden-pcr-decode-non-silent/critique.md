# Critique: Slice 091 harden-pcr-decode-non-silent

**Critic reviewed**: mission-brief.md, design.md, ADR-083, project-frame.md, aggregated lessons, slice-090 reflection excerpt
**Date**: 2026-05-31
**Result**: NEEDS-FIXES (Builder draft — user ratifies at Triage)

## Summary

The Critic (executing against the real git, not reasoning) found a genuine **Blocker**: the AC1 repro staged a single conflict stage via `git update-index --index-info`, which the dev's Windows `git.exe` silently refuses (`Ignoring path …`) so `git show :2:` returned exit 128 ("absent") — the decode path was never reached and the fix could not make the repro pass. VALIDATED and FIXED in this round (repro rewritten to a real rebase conflict). Plus 3 Majors (1 fixed, 1 pending, 1 overridden-with-evidence) and 2 Minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC1 repro stages no blob — `git show :2:` returns exit 128 ("absent"), so the decode path is never reached and the proposed fix cannot make the repro pass
- **Claim under review**: design.md fail-closed flow `_git_show_stage(:2/:3)` … `UnicodeDecodeError → raise _StageDecodeError`; AC1 "the failing repro PASSES at slice end".
- **Issue**: `git update-index --index-info` with `100644 <sha> 2\tarchitecture/slice-queue.md` prints `Ignoring path …` and stages **nothing** on the dev's Windows `git.exe`; `git show :2:architecture/slice-queue.md` → exit 128 → `_git_show_stage` returns `""` via `except CalledProcessError`, NEVER reaching the `.decode()` line. The repro exercised the *absent*-stage sentinel, not the decode path. AC1 unsatisfiable as designed.
- **Evidence**: I independently reproduced with the **venv Python + Windows `git.exe`** (the real test runtime): `update-index --index-info` → `stderr='Ignoring path architecture/slice-queue.md'`, `ls-files -s` empty; `git show :2:` → rc=128; `_git_show_stage(d,2,rel)` → `''`. (A Git-Bash probe with a top-level path masked it — the Critic's APED-1 execution against the real runtime caught what reasoning missed.)
- **Proposed fix**: Stage a REAL rebase conflict (mirror `_stage_rebase`), committing the non-UTF-8 bytes via `write_bytes` on `master` so they land in **stage 2**; `git rebase master` → genuine conflict, `git show :2:` exit 0 with invalid bytes.
- **Builder draft**: **ACCEPTED-FIXED** — repro rewritten (`tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py`, `_stage_rebase_non_utf8`) + a fixture-guard asserting stage 2 carries `\xff` (so it can never silently degrade back to absent-stage). Verified post-rewrite: rebase conflicts (`UU`), `git show :2:` exit 0 with the bytes, `_git_show_stage(2)` → `None` → the test FAILS for the **right reason** (`Got: None`, the decode-drop) not the absent reason. design.md AC1 test-plan note added.

### Majors (address this slice)

#### M1: AC2/AC3 fail-closed behavioral guard has no planned shippability catalog row (SCPD-1 / RPCD-1)
- **Claim under review**: design.md test plan — AC2/AC3 test `tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py` (new), but AC4 lists only #95 (cp1252) + #96 (count-pin).
- **Issue**: The new test is the canonical regression guard for the slice's core anti-silent-bypass behavior (present-undecodable → `_StageDecodeError` → UNKNOWN → STOP + breadcrumb). Per CLAUDE.md Vault discipline + SCPD-1 a must-never-regress guard needs a catalog row; the design plans none. Row #98 covers only AC1; **#99 is taken by the parallel slice-092**.
- **Evidence**: `architecture/shippability.md` #98 = AC1 repro only; #99 = slice-092-fix-stranded-audit-branchless-blindspot (verified). No `decode_fail_closed` / `claim_extraction_degraded` row.
- **Proposed fix**: Add a shippability row (**#100** — next free, #99 is slice-092's) running `test_parallel_conflict_resolver_decode_fail_closed.py`, with a Regression clause naming (a) `claim_extraction_degraded → UNKNOWN` branch removed; (b) `_git_show_stage` reverts to falsy/uncaught; (c) the `## Decode-failure STOP` breadcrumb dropped.
- **Builder draft**: **ACCEPTED-PENDING** — add shippability #100 at `/build-slice` (verify next-free vs slice-092's #99 at build time, in case more parallel rows land).

#### M2: `classify_conflict` reads `claim_extraction_degraded` — risk it is lost through a `--diagnose --json` → `--classify` round-trip → silent SOFT default
- **Claim under review**: design.md "`classify_conflict` returns UNKNOWN when `claim_extraction_degraded` is set".
- **Issue (as raised)**: if the field is a dataclass attribute not serialized into `--diagnose --json` and re-hydrated on the classify side, a degraded diag round-tripped through JSON loses the flag → classify sees `False` → SOFT → the bypass re-opens via the CLI.
- **Evidence (Builder verification — the premise does not hold against the code)**: `main()` rebuilds the diagnostic **fresh** on every mode — `diag = diagnose_conflict(repo_root)` at L2125; `--classify` (L2148) and `--resolve-soft` (L2157) both consume that live diagnostic. `_to_jsonable` (L2082) is **output-only**; there is **no `_from_jsonable`** and no JSON-in CLI path. The flag is always recomputed from the live repo (re-firing the `_StageDecodeError` catch); it is never deserialized. The L900 "stale diag piped from --diagnose JSON" case is a hypothetical the code does not implement; the `_regen_slice_queue` live re-read already fail-closes it on `--resolve-soft` regardless.
- **Builder draft**: **OVERRIDDEN** — the round-trip vulnerability is not reachable: there is no JSON-deserialization path, and both CLI consumers re-diagnose live (L2125/2148/2157). Serializing the field would be speculative (YAGNI). A clarifying invariant was nonetheless documented (design.md "Contracts" §) so a future JSON-in consumer is warned. *(Deferred to /critique-review for a second opinion on the override.)*

#### M3: "Cover BOTH manifestations" is a must-not-defer, but the bytes-mode fix collapses both to one path — the two-manifestation tests risk being non-faithful
- **Claim under review**: must-not-defer "Cover BOTH manifestations (Windows falsy + POSIX UnicodeDecodeError)".
- **Issue**: the pre-fix split is a property of the reader-thread decode the fix removes; post-fix BOTH platforms raise one main-thread `UnicodeDecodeError → _StageDecodeError`. A "Windows-falsy" post-fix test would assert an unreachable state (cf. slice-090: monkeypatch can't reach the C-level decode).
- **Evidence**: design.md "What's new" (bytes-capture + explicit decode); ADR-083 option 2.
- **Proposed fix**: state in design.md/ADR-083 that the fix **converges** both manifestations; discharge the obligation via the pre-fix repro (documents both) + ONE post-fix converged-raise test; do not author a synthetic monkeypatched test.
- **Builder draft**: **ACCEPTED-FIXED** — convergence note added to design.md ("Decisions made" §), ADR-083 framing, and the mission-brief must-not-defer line.

### Minors (log; address if cheap)

#### m1: `_git_show_stage` docstring (L709-716) will become stale — documents the falsy/`None`-tolerant contract the fix removes
- **Issue**: post-fix the present-undecodable case raises; the "callers must tolerate a falsy value" sentence becomes a misleading contract claim (brownfield "docs are hypothesis").
- **Builder draft**: **ACCEPTED-PENDING** — update the docstring to the three outcomes (absent → `""`; decodable → str; present-undecodable → raises `_StageDecodeError`) during `/build-slice` (part of the fix edit).

#### m2: MEPD-1 posture not stated in design/ADR-083
- **Issue**: a `tools/*.py` slice must discharge the MEPD-1 changelog/RULE-ID obligation via branch (a) mint or (b) documented-none; matches the EXCLUDE precedent (077/079/082/084/085/086/087) but was left implicit.
- **Builder draft**: **ACCEPTED-FIXED** — MEPD-1 EXCLUDE line added to design.md ("Decisions made" §), with a build-time note to verify against `test_methodology_changelog.py`'s enforcing assertion.

## Dimensions checked
- [x] Unfounded assumptions — B1 (decode path unreachable under the repro's own staging — executed, not reasoned); m1 (stale docstring). Count-shift 9→8/4→5 verified grounded.
- [x] Missing edge cases — M2 (round-trip — Builder verified not reachable). Absent / both-absent stages handled.
- [x] Over-engineering — none (one exception subclass, one defaulted field, one classify branch, one audit helper; reuses existing fail-closed plumbing).
- [x] Under-engineering — B1 (no working repro path), M1 (no catalog guard), M3 (convergence framing needed).
- [x] Contract gaps — M2 (serialization — N/A, no JSON-in path; documented).
- [x] Security — none new; fail-closed hardening REDUCES the silent-bypass surface (ADR-069 cooperative model unchanged).
- [x] Drift from vault — m2 (MEPD-1 posture); ADR-083 append-only, supersedes:null, no ADR-069/082 contradiction; frozen+slots+defaulted-field backward-compatible (verified).
- [x] Web-known issues — checked the stronger way: executed git `show`/`update-index`/reader-thread against the real local runtime (B1 evidence).
- [x] Cross-cutting conformance — APED-1 by execution (B1 falsified the reachability assumption); SCPD-1 (M1 catalog); strategic-fit on-trajectory (PCR family, R-30 residual #1).

## Triage

**Triaged by**: user
**Date**: 2026-05-31
**Final verdict**: NEEDS-FIXES

(Reconciled across BOTH passes — first Critic critique.md + meta-Critic critique-review.md. Meta-Critic verdict ADJUST: M2 override independently confirmed correct; m1 elevated; m-add-1/m-add-2 added.)

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | Repro rewritten to real-rebase staging (stage 2 = non-UTF-8 master) + fixture-guard; verified fails for the right reason (`Got: None`, decode-drop) — test file + design.md AC1 note. Meta-Critic confirmed. |
| M1 | Major | ACCEPTED-PENDING | Add shippability #100 (decode-fail-closed guard) at build; #99 is parallel slice-092 |
| M2 | Major | OVERRIDDEN | No JSON-in/round-trip path exists; `--classify`/`--resolve-soft` re-diagnose live (L2125/2148/2157); `_to_jsonable` output-only (L2082), no `_from_jsonable`; flag always live-computed; invariant documented in design.md. Meta-Critic independently traced end-to-end and confirmed the override is correct. |
| M3 | Major | ACCEPTED-FIXED | Convergence note added to design.md + ADR-083 + mission-brief must-not-defer |
| m1 | Minor | ACCEPTED-PENDING | ELEVATED per meta-Critic SEVERITY-WRONG: the docstring documents the *inverted dangerous contract*; build must INVERT the caller-tolerance sentence (document raise-on-undecodable), not trim `None`. Added as explicit must-not-defer in mission-brief. |
| m2 | Minor | ACCEPTED-FIXED | MEPD-1 EXCLUDE posture line added to design.md |
| m-add-1 | Minor | ACCEPTED-FIXED | (meta-Critic) `ConflictDiagnostic` frozen+slots → set `claim_extraction_degraded` via the L221 constructor call, not post-construction mutation; design.md§What's-new clarified |
| m-add-2 | Minor | ACCEPTED-FIXED | (meta-Critic) catch wraps BOTH stage-2 & stage-3 reads; stage-3-undecodable variant added to AC2/AC3 test plan; design.md clarified |
