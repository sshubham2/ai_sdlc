# Design: Slice 091 harden-pcr-decode-non-silent

**Date**: 2026-05-31
**Mode**: Standard

## What's new

- A new internal exception `_StageDecodeError(_SoftResolutionError)` in `tools/parallel_conflict_resolver.py`, carrying `ConflictClass.UNKNOWN` + the offending `stage` and `path`.
- `_git_show_stage` rewritten to capture git output as **bytes** and decode explicitly with strict UTF-8; raises `_StageDecodeError` on a present-but-undecodable stage (instead of silently returning a falsy value or crashing).
- A new best-effort audit-breadcrumb helper `_append_decode_stop_audit(repo_root, stage, path, reason)` — a distinct `## Decode-failure STOP (non-UTF-8 stage) - <ts>` audit-log section.
- A new field on `ConflictDiagnostic`: `claim_extraction_degraded: bool = False`. **`ConflictDiagnostic` is `frozen=True, slots=True` (resolver L162-168)** — the flag is therefore set by **threading `claim_extraction_degraded=True` through the constructor call** at the `diagnose_conflict` return site (L221-225), NOT by post-construction mutation (no `object.__setattr__` workaround). The `= False` default keeps all 4 existing construction sites + synthetic-test constructors valid (m-add-1).
- `diagnose_conflict` wraps **both** the stage-2 (L204) AND stage-3 (L205) `_git_show_stage` reads in the `_StageDecodeError` catch; an undecodable EITHER stage records the breadcrumb and constructs the diagnostic with `claim_extraction_degraded=True` (m-add-2 — symmetric, not stage-2-only).
- `classify_conflict` returns `ConflictClass.UNKNOWN` when `claim_extraction_degraded` is set (fail-closed, never silent-default to SOFT).

## What's reused

- The existing fail-closed channel: `classify_conflict` already returns `UNKNOWN` for unparseable rebase state, and `resolve_soft_conflict` already turns `UNKNOWN` into a `STOP` (no new STOP plumbing).
- `_SoftResolutionError` (`tools/parallel_conflict_resolver.py:444`) — `_StageDecodeError` subclasses it so the **existing** `except _SoftResolutionError` handler in `resolve_soft_conflict` (`:339`) fail-closes the `_regen_slice_queue` defense-in-depth call site (`:878`) automatically.
- The best-effort audit-write pattern of `_append_skew_stop_audit` (`:603`, ADR-076) — `_append_decode_stop_audit` mirrors it (distinct section header, `git rev-parse HEAD` best-effort, internal `datetime.now(utc).isoformat()` timestamp).
- [[decisions/ADR-082]] (slice-090 `encoding="utf-8"` fix) — this slice hardens the residual it left; reuses its "predicate kernel as reuse seam" intent.
- [[risk-register#R-30]] residual #1 — the finding this slice narrows.

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: classify + resolve in-progress rebase conflicts on parallel-slice vault files (`slice-queue.md` / `shippability.md`), failing closed on anything it cannot safely auto-merge.
- **Lives at**: `tools/parallel_conflict_resolver.py` (modified).
- **Key interactions**: `tools.slice_queue_claim.parse_queue_text` (claim extraction); git via `subprocess`; `skills/commit-slice/SKILL.md` sub-step 2.5 (the CLI driver). No skill-prose change in this slice — the behavior change is internal to the library; the skill already treats a `STOP` result as a hand-resolve gate.

### Fail-closed flow (the fix in one path)

```
diagnose_conflict
  └─ _git_show_stage(:2 / :3, slice-queue.md)        bytes-capture + explicit .decode("utf-8")
       ├─ CalledProcessError/FileNotFoundError → ""   (stage absent — unchanged)
       ├─ decode OK                            → str   (unchanged)
       └─ UnicodeDecodeError → raise _StageDecodeError(UNKNOWN, stage, path)
  └─ except _StageDecodeError:
       ├─ _append_decode_stop_audit(...)               best-effort breadcrumb (stage+path)
       └─ claim_extraction_degraded = True
classify_conflict(diag)
  └─ if diag.claim_extraction_degraded → UNKNOWN       fail-closed (never SOFT)
resolve_soft_conflict(diag)
  └─ cls is UNKNOWN → ResolutionResult(action="STOP")  no writes, no rebase --continue

# Defense-in-depth (stale-diag piped to resolve without re-diagnose):
resolve_soft_conflict → _regen_slice_queue → _git_show_stage → _StageDecodeError
  └─ caught by existing `except _SoftResolutionError` (:339) → STOP(UNKNOWN)
```

## Contracts added or changed

No external/CLI contract change. `_git_show_stage`'s caller-visible contract is unchanged for the absent (`""`) and decodable (`str`) cases; only the present-but-undecodable case changes from "silent falsy / uncaught crash" to "typed `_StageDecodeError` → UNKNOWN STOP". `ConflictDiagnostic` gains one defaulted field (backward-compatible).

**`claim_extraction_degraded` is live-computed, never deserialized (M2 grounding).** Every CLI mode rebuilds the diagnostic fresh: `main()` calls `diagnose_conflict(repo_root)` at L2125, and both `--classify` (L2148) and `--resolve-soft` (L2157) consume that live diagnostic. `_to_jsonable` (L2082) is **output-only** — there is no `_from_jsonable` and no JSON-in CLI path — so the new flag cannot be lost through a JSON round-trip (none exists); it is always recomputed from the live repo, where the `_StageDecodeError` catch re-fires. The L900 "stale diag piped from --diagnose JSON" scenario is hypothetical (not a real CLI entrypoint); the `_regen_slice_queue` live re-read (defense-in-depth) already fail-closes it on the `--resolve-soft` path regardless.

## Data model deltas

None (no persisted schema). The audit-log gains one new section variant (`## Decode-failure STOP (non-UTF-8 stage)`), append-only, consistent with the existing best-effort audit format.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new module** — it modifies one existing module and adds test functions to one existing/new test file. Zero new modules ⇒ zero-row matrix (audit treats as clean).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[ADR-083]] — the PCR conflict-stage reader decodes git bytes explicitly and fails closed (UNKNOWN STOP) on non-UTF-8 stage content, never a silent falsy claim-drop — reversibility: cheap.

**MEPD-1 posture: EXCLUDE** — risk-narrowing fix-slice with an ADR and **no new RULE-ID** (precedent: 077/079/082/084/085/086/087, N≥6 per `_index.md` aggregated lessons). No `methodology-changelog.md` version bump, no entry-pin; the AVFS-1/MCFS-1/TVFS-1 forward-sync gates are a no-op for this slice. (Builder verifies against `tests/methodology/test_methodology_changelog.py`'s enforcing assertion at build, not the prior-slice claim — m2.)

**"Both manifestations" convergence (M3)** — the pre-fix Windows-falsy vs POSIX-uncaught split is a property of the **reader-thread** decode that the bytes-mode fix removes. Post-fix, BOTH platforms decode in the main thread and raise the same `UnicodeDecodeError → _StageDecodeError` — the two manifestations **converge** to one path. The must-not-defer "cover both manifestations" is therefore discharged by (a) the pre-fix repro documenting both, and (b) ONE post-fix test asserting the converged `_StageDecodeError` raise — NOT by two platform-divergent post-fix tests, and explicitly NOT by a monkeypatched synthetic "Windows-falsy" test (which would assert a state the fix made unreachable; cf. slice-090's "monkeypatch can't reach subprocess's C-level decode" lesson).

## Authorization model for this slice

N/A — internal resolver library; no auth surface. (The slice touches `tools/*.py`, an in-house methodology surface — mandatory Critic per CLAUDE.md, independent of auth.)

## Error model for this slice

- **Present but non-UTF-8 stage** → `_StageDecodeError(UNKNOWN)` → `classify_conflict` UNKNOWN → `resolve_soft_conflict` `STOP` (no writes, conflict markers preserved, rebase left in-progress for hand-resolve). A best-effort audit breadcrumb names the stage + path; breadcrumb-write failure is swallowed (non-blocking, per the module's existing "audit log is best-effort" philosophy) and never masks the STOP.
- **Stage absent** (git show fails) → `""` (unchanged) — distinct from undecodable, so a one-sided add is NOT mistaken for a decode failure.
- **Both stages absent** → existing `_SoftResolutionError(UNKNOWN)` in `_regen_slice_queue` (unchanged).

## Slice-090 count-pin interaction (deliberate, in-scope)

Converting `_git_show_stage` to bytes-mode shifts the slice-090 AST invariant counts. **BUILD CORRECTION (mid-slice smoke, recorded as a deviation):** the design predicted decode `9 → 8`, but reality is **decode unchanged at 9; byte-mode 4 → 5**. `_git_show_stage` leaves the decode set (now byte-mode + explicit `.decode`), but the new `_append_decode_stop_audit` breadcrumb helper adds its own `git rev-parse HEAD` decode site (mirroring `_append_skew_stop_audit`), so the two offset and the decode count is preserved. This slice updates `tests/methodology/test_parallel_conflict_resolver_git_encoding.py` (`_EXPECTED_BYTE_MODE_SITES` 4→5; `_EXPECTED_DECODE_SITES` stays 9) and the shippability **#96** description accordingly. `_git_show_stage` is the sole byte-mode site that *decodes explicitly*; the other 4 byte-mode sites are staging sites that never decode. It still carries **no `encoding=`** on the `subprocess.run` call, so slice-090's "byte-mode sites must not carry `encoding=`" invariant holds unchanged. The 4 STAGING byte-mode sites are untouched. This cross-slice test edit touches a *live* test file (not the archived slice-090 vault) and is the honest consequence of the fix — recorded in [[ADR-083]].

## Test plan (per mission-brief TF-1)

- AC1 — `tests/bugs/test_pcr_git_show_stage_non_utf8_fail_closed.py` (WRITTEN-FAILING; staging **rewritten at /critique B1** to a REAL rebase conflict — `git update-index --index-info` is dead on the dev's Windows `git.exe`, "Ignoring path …" → exit-128 absent → the decode line was never reached; now non-UTF-8 bytes are committed on `master` → land in conflict **stage 2**, `git show :2:` exit 0, `_git_show_stage` returns falsy `None` pre-fix). A fixture-guard asserts stage 2 carries the `\xff` byte so the test can never silently degrade back to an absent-stage check. Passes post-fix (typed `_StageDecodeError`). AC2/AC3 use the same real-rebase staging.
- AC2/AC3 — `tests/methodology/test_parallel_conflict_resolver_decode_fail_closed.py` (new):
  - present non-UTF-8 stage → `_git_show_stage` raises `_StageDecodeError` (not falsy, not raw `UnicodeDecodeError`);
  - absent stage still → `""` (distinguishable from undecodable);
  - `diagnose_conflict` on an undecodable **stage-2** slice-queue stage → `claim_extraction_degraded` True + an audit breadcrumb naming stage+path;
  - `diagnose_conflict` on an undecodable **stage-3** slice-queue stage (stage-2 decodable) → `claim_extraction_degraded` True too — the catch is symmetric across both reads (m-add-2);
  - `classify_conflict` on a degraded diag → UNKNOWN; `resolve_soft_conflict` → STOP (no writes / no rebase --continue);
  - defense-in-depth: a non-degraded diag piped into `resolve_soft_conflict` whose live queue stage is undecodable → STOP via the existing `_SoftResolutionError` handler.
- AC4 — updated `test_parallel_conflict_resolver_git_encoding.py` (decode 9 unchanged / byte-mode 4→5 — see BUILD CORRECTION above) + the cp1252 behavioral repro (#95) + full resolver suite green.
