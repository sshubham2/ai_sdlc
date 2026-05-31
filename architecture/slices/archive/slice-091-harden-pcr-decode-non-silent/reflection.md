# Reflection: Slice 091 harden-pcr-decode-non-silent

**Date**: 2026-05-31
**Shipped**: YES

## Validated
- `_git_show_stage` bytes-capture + explicit strict decode fails closed on non-UTF-8 stages — validated by the host-independent repro (`test_pcr_git_show_stage_non_utf8_fail_closed.py`, real rebase conflict) + the 6-test fail-closed battery, all PASS on the real Windows host.
- Routing the degraded diagnostic into the EXISTING UNKNOWN fail-closed channel (no new STOP plumbing) works — `classify_conflict` degraded→UNKNOWN → `resolve_soft_conflict` STOP, and the `_StageDecodeError(_SoftResolutionError)` subclassing makes the `_regen_slice_queue` defense-in-depth path fail-close via the existing handler (validated by `test_defense_in_depth_regen_slice_queue_fail_closed`).
- Frozen+slots constructor-threading of `claim_extraction_degraded` (m-add-1) — validated: no `FrozenInstanceError`, existing 3-arg constructions still valid.
- R-30 residual #1 (the Major) is structurally closed — validated by shippability #98 + #100.

## Corrected
- **Count-pin delta: design said decode 9→8; reality is decode UNCHANGED at 9 / byte-mode 4→5.** The new `_append_decode_stop_audit` helper has its OWN `git rev-parse HEAD` decode site (mirroring `_append_skew_stop_audit`) that offsets the one `_git_show_stage` relinquished. Caught at the mid-slice smoke gate; reconciled across `test_parallel_conflict_resolver_git_encoding.py` (`_EXPECTED_BYTE_MODE_SITES=5`), shippability #96, design.md (BUILD CORRECTION), [[ADR-083]], mission-brief — no stale "9→8" claim remains.
- [[risk-register#R-30]] residual #1 marked RETIRED-by-slice-091 (R-30 stays `mitigating` — only residual #2, the cp1252-repro CI-coverage limitation, remains).

## Discovered
- **Git-Bash `git` ≠ Windows `git.exe` for plumbing edge cases** — `git update-index --index-info` with a nested path STAGES on Git-Bash but prints "Ignoring path …" and stages NOTHING on the dev's Windows `git.exe` (the venv-Python subprocess runtime). My initial repro (and a Git-Bash probe) was masked by this; the design-Critic executing against the REAL runtime caught it (B1).
- **A fix closing a residual spawns its own micro-residual** — the VAULT_CLAIM resolve path had a defense-in-depth asymmetry (no `_StageDecodeError` catch on its stage reads); caught by the code-Critic (m1), fixed in-slice to make the "non-UTF-8 always fails closed" invariant total.
- **Parallel slice-092 entanglement** — a concurrent session created slice-092 (R-31, `tools/stranded_slice_audit.py`, non-overlapping) branchless in the main tree during this slice's lifecycle. Worktree isolation handled the build; the shared-vault merge (risk-register / lessons-learned / _index HARD conflicts) is deferred to `/commit-slice --merge` — the known PCR-N `_index.md`-class gap.

## Deferred
- `audit-cp1252-decode-pattern-across-tools` — reason: ADR-082/083 scoped module-only; the repo-wide `text=True`-without-`encoding=` sweep + a build-check lint remains queued (R-30 mitigation candidate). Lands in: that queued slice.
- R-30 residual #2 (cp1252-repro CI-coverage) — reason: undetectable-by-design (monkeypatch can't reach subprocess's C-level decode); stays as an accepted two-layer-model residual.

## Critic calibration

Per TRI-1, scored against the `critique.md` `## Triage` dispositions + reality at build/validate:

- **B1** (AC1 repro stages no blob — Windows `git.exe` "Ignoring path"): **VALIDATED** — ACCEPTED-FIXED; the design-Critic EXECUTED against the real Windows git and caught a Blocker my Git-Bash probe masked. The repro was genuinely unreachable-as-written; the real-rebase rewrite was necessary. Strongest finding of the slice.
- **M1** (no shippability row for the fail-closed guard): **VALIDATED** — ACCEPTED-PENDING; #100 added at build (#99 correctly reserved for parallel slice-092).
- **M2** (degraded flag lost through `--diagnose→--classify` JSON round-trip): **FALSE-ALARM** — OVERRIDDEN; reality confirmed the override. No JSON-in path exists (`main()` re-diagnoses live at L2125; `_to_jsonable` output-only; no `_from_jsonable`). The meta-Critic independently traced it end-to-end and confirmed the override correct. The design-Critic over-reached on reachability (it hypothesised a round-trip the code doesn't implement) — but correctly DEFERRED the second opinion to the meta-Critic, which is the designed safety net.
- **M3** (both-manifestations convergence): **VALIDATED** — ACCEPTED-FIXED; the bytes-mode fix did converge Windows-falsy + POSIX-raise into one main-thread path, as the design note predicted.
- **m1** (stale docstring documents the inverted contract): **VALIDATED** — ACCEPTED-PENDING, meta-Critic ELEVATED from cosmetic; docstring inverted in-slice. The elevation was right — the stale sentence documented the exact removed dangerous contract.
- **m2** (MEPD-1 posture): **VALIDATED** — ACCEPTED-FIXED.
- **m-add-1** (frozen+slots constructor, meta-Critic): **VALIDATED** — the build confirmed the flag MUST be set via the constructor; no mutation attempt.
- **m-add-2** (catch both stage reads, meta-Critic): **VALIDATED** — `test_stage_3_undecodable_also_degrades` confirms the symmetric catch.
- **code-Critic**: **0 blockers / 0 majors / 3 minors**, all VALIDATED + addressed in-slice — m1 (VAULT_CLAIM defense-in-depth asymmetry — the one residual the design+meta stack structurally couldn't reach, since it required tracing the resolve-path reach analysis against the built code), m2 (count-pin "4 staging" self-violation prose), m3 (repro pre-fix-`None` dev-host tagging).

**Missed by Critic**: the **count-pin decode-count offset**. The design + both design-stack Critics asserted decode `9→8`; NONE flagged that the new `_append_decode_stop_audit` helper's own `git rev-parse HEAD` is a decode site that keeps the count at 9. It surfaced ONLY at the mid-slice smoke gate (the count-pin test went RED at byte-mode, and the decode assertion stayed green at 9). Root cause: the count delta was arithmetic-reasoned, not executed against the post-change AST. Candidate `/critic-calibrate` probe: **"when a slice claims a count-pin / inventory delta (X→Y), has the predicted post-change count been EXECUTED against the built code (run the pin), not reasoned from the diff?"** — a sibling of the APED-1 "execute the regex against the real corpus" family, on the count-arithmetic axis.

**Pattern**: 3-Critic stack complementarity held again, non-overlapping (extends 086-090) — design-Critic = **APED-1-by-execution on the REAL runtime** (B1: Windows `git.exe`, not Git-Bash — the standout); meta-Critic = override-adjudication (M2 confirmed) + frozen-dataclass + symmetric-catch coherence (m-add-1/2); code-Critic = the resolve-path reach-analysis defect (VAULT_CLAIM asymmetry) the design stack can't reach + self-violation prose. The one class ALL THREE missed (count-pin offset) is the count-arithmetic-not-executed axis → /critic-calibrate signal.

## Lessons for next slice
- **A count-pin / inventory delta claim (X→Y) must be EXECUTED against the post-change code before it's asserted** — slice-091 predicted decode 9→8 in design/ADR/shippability, but the new audit-breadcrumb helper's own `git rev-parse` decode site kept it at 9. No Critic layer caught it; the mid-slice smoke gate did. Run the pin against the built code, don't arithmetic-reason from the diff. (Count-axis sibling of APED-1; /critic-calibrate candidate.)
- **Execute against the REAL runtime, not a convenient proxy** — Git-Bash `git` staged the `update-index --index-info` single-stage fine; the dev's Windows `git.exe` (the actual venv-Python subprocess runtime) "Ignoring path" → staged nothing. The Critic executing against the real runtime caught B1; my Git-Bash probe masked it. For any git-plumbing repro, verify on the runtime the code will actually use.
- **Worktree isolation yields a clean validation under parallel slices** — slice-091 in a real BRANCH-2 worktree (vs slice-090's WORKTREE=skip) validated 98/98 shippability PASS, avoiding the sibling-induced PARTIAL pattern of 087/090. "Resolve the parallel state first, use a real worktree" (slice-090 directive) paid off — the user's call to isolate slice-091's scaffold commit (exclusive files only) kept slice-092 untouched.
- **Bytes-capture + explicit main-thread decode is THE cross-platform-safe pattern for CATCHING git-output decode failures** — text-mode swallows them platform-differently (Windows reader-thread → `stdout=None`; POSIX → uncaught propagate). Refines BC-GLOBAL-5 (slice-090): "pass `encoding="utf-8"`" is right for round-tripping, but to FAIL CLOSED on bad bytes you must capture bytes + decode explicitly.
- **The 3-Critic stack's one shared blind spot this slice was count-arithmetic** — design/meta/code Critics each caught their own class but all asserted/accepted the wrong decode count. Count/inventory deltas need execution, like regexes do.

## Vault updates made (thin vault)
- [[risk-register.md]] — R-30 residual #1 marked RETIRED by slice-091 (R-30 stays `mitigating` for residual #2)
- [[decisions/ADR-083]] — created (bytes-capture + explicit decode + fail-closed UNKNOWN STOP; cheap)
- [[shippability.md]] — #98 (repro) + #100 (fail-closed guard) added; #96 corrected to 9 decode / 5 byte-mode
- [[lessons-learned.md]] — slice-091 entry appended
- `tools/parallel_conflict_resolver.py` — `_StageDecodeError`, `_git_show_stage` (bytes+explicit decode+inverted docstring), `_append_decode_stop_audit`, `ConflictDiagnostic.claim_extraction_degraded`, dual-stage catch in `diagnose_conflict`, classify degraded→UNKNOWN, VAULT_CLAIM-path defense-in-depth catch (code-review m1)
- `tests/` — repro (B1-rewritten), new `test_parallel_conflict_resolver_decode_fail_closed.py` (6), count-pin update
