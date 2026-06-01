# Reflection: Slice 094 harden-vault-write-safety

**Date**: 2026-06-01
**Shipped**: YES-WITH-DEFERRALS

## Validated
- The **two-persona Critic model paid off — it caught a real BUILDER error** (not just a design defect). `/critique` B1 disputed the Builder's own v3 redesign; the Builder reproduced and CONFIRMED the Critic. This is the strongest validation of the dual-Critic discipline this project has recorded.
- Per-write-target AST audit (VWS-1) — clean on the real corpus (43 tools, 6 PCR scoped-out, 4 routed, 0 violations); the design's "6 of PCR's 7 ops resolve, :430 loop-var is the residual" claim held exactly.
- Byte-faithfulness fix (`newline=""` + `os.O_BINARY`) — byte-identical to the canonical writer for small ASCII + >1024B multibyte (AC1, 10/10).
- PCR scope-out (B3) + the 5-part PMI-1 bump + entry-pins — all held; PMI-1/INST-1/UTF8/MCFS-1/AVFS-1/TVFS-1 exit 0 at v0.80.0/39 tools.

## Corrected
- **AC4 concurrency proof — TWO mid-build corrections** (design.md §Why v3 / §Concurrency proof updated; mission-brief AC4 updated):
  1. The v2 meta-Critic-corrected ">1024-byte append interleaving" framing was **empirically FALSIFIED at build** — `os.write` is byte-atomic (one Windows `WriteFile`), so concurrent `O_APPEND` never SPLICES bytes at any size (4KB/64KB/512KB → 0 interleaving). `bugs.python.org#15723`'s ">1024B" is a buffered/text-mode `f.write()` issue, not the raw-`os.write` channel.
  2. The Builder's v3 then **OVER-corrected** to "no interleaving ⇒ no corruption ⇒ drop the append proof." `/critique` B1 disputed it; a barrier-synchronized probe confirmed the Critic: unlocked concurrent `O_APPEND` loses WHOLE writes on Windows (non-atomic EOF-positioning — two opens compute the same end offset; the second clobbers). The append lock is LOAD-BEARING. User chose "Halt + formal redesign" → full `/design-slice`+`/critique`+`/critique-review`+TRI-1 cycle; corrected Proof 2 = append LOST-UPDATE prevention (stronger + deterministic).
- VWS-1 channel set broadened post-`/code-review` (M1): `_write_target` now covers `os.rename`/`io.open`/`shutil.move/copyfile/copy/copy2` (was 5 channels → fail-OPEN for the rest). `_WRITE_OPEN_FLAGS` dropped bare `O_CREAT` (m1).

## Discovered
- **"No byte-interleaving" ≠ "no corruption"**: `os.write` atomicity prevents byte-splicing but NOT lost-update on concurrent `O_APPEND` (Windows non-atomic EOF-positioning). Confirmed against bugs.python.org#42606. Impact: the append safe channel's lock is load-bearing for lost-update, not interleaving.
- **Un-barriered `multiprocessing(spawn)` masks concurrency hazards**: spawn workers start ~100 ms apart → never overlap → a contention probe reports false "no corruption." The Builder's first probe hit exactly this; `mp.Barrier` synchronization is required to force real contention. (This was the proximate cause of the OVER-correction above.)
- **R-33 post-merge count reconciliation**: the shippability catalog was at 103 post-merge (096 + 095), NOT the pre-merge design's 101 → slice-094 row = **#104**, not #102. Execute the count, don't reason it.
- **N≥3 count-literal fan-out is wider than any checklist**: the v0.80.0 bump broke 3 tests the design didn't enumerate — 2 hardcoded INSTALL.md `"38"` inventory pins (`test_stranded_slice_audit_tool_inventory` + `test_pulse_worktree_resolver_tool_inventory`) AND a shippability row-#75 stale citation from the version-gate-test RENAME (`_at_v_0_79_0`→`_at_v_0_80_0`). Renaming a versioned test orphans every catalog row citing it by name.

## Deferred
- **R-32 RMW residual + the 3 git/worktree-coupled tools** (`parallel_conflict_resolver` + `stranded_slice_audit` + `pulse_worktree_resolver`) + the physical move of `architecture/` + the git-untrack decision + the prose rewrite → the **external-vault flip slice** (a later slice). R-32 stays `mitigating`.
- **VWS-1 m2** (nested-function scope over-walk) + **m3** (aliased-import routed-count under-report) — both fail-safe/benign in the current corpus; accepted-as-documented (no fix). Lands in: backlog / a future VWS-1 hardening if a closure or aliased-routed-import enters `tools/`.

## Critic calibration

Per TRI-1, scored against `critique.md` dispositions + reality observed during build/validate:

- **B1 (append lost-update / "drop the proof" premise false)**: **VALIDATED** — disposition ACCEPTED-PENDING; a real under-engineering defect the Builder's own first probe MISSED. The Builder independently confirmed it by barrier-synchronized probe (16 workers → 5-10 survive unlocked, N/N locked). The single most valuable Critic catch this project has recorded — it corrected the Builder, not just the design.
- **B2 (false-premise prose)**: **VALIDATED** — ACCEPTED-FIXED; the prose was genuinely false and was rewritten.
- **M1 (holder-timing flake) / M2 (nt-guard hides POSIX gap)**: **VALIDATED** — ACCEPTED-PENDING; both built (Event-gated holder; cross-platform safe-path canary). No flakiness observed (concurrency 4/4, 20-rep mutation never near 0).
- **m1 / m2 (minors)**: VALIDATED / mooted; built or accepted.
- `/critique-review`: **VALIDATED** — confirmed B1 was NOT a barrier-only artifact (independent un-barriered probe: 64 workers → 10-39 lost); correctly downgraded B2 Blocker→Major (consequence-of-B1); surfaced the missed M-add-1 (POSIX-canary mislabeling).
- `/code-review` **M1 (VWS-1 fail-OPEN for un-enumerated channels)**: **VALIDATED** — the code-Critic EXECUTED the gap (planted `os.rename`/`io.open`/`shutil.move` → status=clean). Real latent fail-open; Builder fixed by broadening the channel set + APED-1 tests.

**Missed by Critic**: nothing material. (The Builder's OWN first concurrency probe was the miss — the spawn-stagger false-negative — and the Critic CAUGHT it. That is the dual-Critic discipline working.)

**Pattern**: **Zero false-alarms across all three Critic layers this slice** (`/critique` + `/critique-review` + `/code-review`), and B1 caught a Builder error the Builder's own verification missed. Strong calibration. The recurring meta-lesson: *re-interrogate the Critic's claims by execution* cuts BOTH ways — it falsified the meta-Critic's interleaving framing AND (when the Builder over-applied it) the Critic re-falsified the Builder's over-correction. Execution, not reasoning, is the arbiter.

## Lessons for next slice
- Barrier-synchronize multiprocessing-spawn concurrency proofs; an un-barriered pool proves nothing (workers stagger). Prove non-vacuity by mutation (slice-092).
- "Atomic write" claims are channel-specific: `os.write` byte-atomicity ≠ concurrent-`O_APPEND` lost-update safety. State which property a test actually proves.
- A versioned test RENAME (the `_at_v_0_NN_0` version-gate) orphans every shippability/citation referencing it by name — grep the OLD name repo-wide before finishing the bump.
- The external-vault FLIP is the next R-32 milestone: it needs BOTH slice-094 (this) + slice-095 merged, plus the RMW residual closed + the 3 git-coupled tools retired.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-32 slice-094 reframe paragraph (stays `mitigating`, flip-readiness, explicit residual) — added during build.
- [[shippability.md]] — row #104 (VWS-1 critical path) + row-#75 citation rename (version-gate test).
- [[lessons-learned.md]] — slice-094 entry appended (Step 5).
- This slice's [[design.md]] / [[mission-brief.md]] — AC4 v3 redesign (concurrency proof corrected) + VWS-1 channel-set broadening.
- No ADR superseded (ADR-086 revised in place, pre-build — not a SUP-1 supersession).
