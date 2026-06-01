# Validation: Slice 094 harden-vault-write-safety

**Date**: 2026-06-01
**Result**: PASS

## Per-criterion results

### AC1: Primitive byte-faithfulness (`safe_write_text` newline="" / `safe_append_text` os.O_BINARY emit LF, byte-identical to canonical writer; nt-guarded byte-identity test pins small ASCII + >1024B multibyte)
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_vault_safe_write.py` → 10/10 pass, incl. the nt-guarded byte-identity test (small ASCII + 4002B multibyte UTF-8 both LF, byte-identical to the canonical `newline=""` writer) and the O_APPEND-still-appends check. Live-verified during build (post-fix → `b'a\nb\n'`).
- **Notes**: both primitives previously emitted CRLF on Windows (the B1 blocker); the fix makes routing byte-transparent.

### AC2: Seam writers routed (honest scope — byte-transparent; RMW window a documented flip-residual)
- **Status**: PASS
- **Evidence**: `slice_queue_writer.py:817` + `slice_queue_claim.py:539` both call `safe_write_text` (grep-confirmed); 77 queue/PSQ byte-equality tests pass (byte output identical pre/post-routing). `parallel_conflict_resolver` untouched (scoped OUT).
- **Notes**: routing buys byte-faithful + atomic + EPERM-resilience; it does NOT close the read-modify-write lost-update window (documented flip-residual, B2) — not claimed closed.

### AC3: Fail-closed enforcement audit (per-write-target AST; COUNT-pinned scoped-out allowlist; EXEMPT _vault_write; exits non-zero on unclassifiable vault write; executed APED-1 battery)
- **Status**: PASS
- **Evidence**: `vault_write_safety_audit --repo-root . --json` → `status=clean tools=43 write_ops=6 routed=4 scoped_out=6 violations=0`. `pytest test_vault_write_safety_audit.py` → 32/32 (planted-raw→VIOLATION across all channels incl. the /code-review M1 additions os.rename/io.open/shutil; ≤1-hop depth-lock→VIOLATION; reader/error-prose/read_text/tmp/O_RDONLY|O_CREAT→CLEAN; EXEMPT/SCOPED-OUT; 2-hop-alias + container-element residuals pinned; COUNT-pin; CLI 0/1/2 + unparseable→2). Mid-slice smoke proved the real-file revert: un-routing `slice_queue_writer:817` → audit exit 1 naming `:817 [.write_text]`; restored → exit 0. Wired into `/build-slice` Step 6 + `/validate-slice` + shippability #104.
- **Notes**: /code-review M1 broadened the channel set (os.rename twin of os.replace + io.open + shutil movers) — closed a latent fail-OPEN before validation.

### AC4: Concurrency proof (non-vacuous, VERIFIED-deterministic — proves what the lock ACTUALLY protects)
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_vault_write_safety_concurrency.py` → 4/4 (multiprocessing-spawn + `mp.Barrier` + bounded timeout). Proof 1 whole-file EPERM-resilience (exclusive `CreateFileW dwShareMode=0` holder, Event-gated; raw `os.replace`→WinError 5, `safe_write_text` absorbs). Proof 2 append LOST-UPDATE prevention (N=20 barrier-synchronized; unlocked `O_APPEND` loses whole writes, `safe_append_text` loses zero). **Non-vacuity proven by real-lock-strip mutation**: stripping `_file_lock` from the live `safe_append_text` → 10/20 writes LOST; reverted → 0/20.
- **Notes**: AC4 was redesigned mid-build (the original ">1024B interleaving" framing was empirically false; `/critique` B1 + a barrier-synchronized probe established the append lock is load-bearing for lost-UPDATE). The corrected proof is stronger (deterministic).

### AC5: No-flip contract + R-32 reframe
- **Status**: PASS
- **Evidence**: `pytest tests/methodology/test_vault_root_constant.py` → 15/15 (the no-config default resolves to `Path("architecture")` — the no-flip safety contract). `architecture/risk-register.md` R-32 `**Status**: mitigating` with the slice-094 reframe paragraph ("Python-writer sub-class ENFORCED, flip-READINESS, retires at the flip" + explicit residual: PCR + git/worktree-coupled tools + physical move + prose rewrite + slice-095 RMW residual).
- **Notes**: R-32 NOT retired by this slice — flip-readiness only.

## VAL-1 layered safety checks (Step 5b)
- **Layer A (credential scan)**: PASS — 0 secrets.
- **Layer B (dependency hallucination)**: PASS — 0 import findings (the new audit + tests import only stdlib + internal `tools.*` + pytest/multiprocessing/ctypes).

## WS-1 / ETC-1
- Not applicable — `**Walking-skeleton**: false`, `**Exploratory-charter**: false`.

## Multi-instance validation
- **Required?**: no (local data-integrity tooling; ADR-067 cooperative model — defends parallel slices/sessions on one machine, demonstrated via the multiprocessing-spawn concurrency proof, NOT a cross-device/user feature).
- **Result**: not-applicable.

## Shippability catalog regression (Step 5.5)
- Pre-gates: SCMD-1 (decoupling) PASS, PTFCD-1 (path) PASS, SVW-1 (skill-vault-write) PASS.
- Runner (SRSC-1 canonical `shippability_runner`): **103 rows, 103 PASS, 0 FAIL** (slice-094 row #104 present + executed; one pre-existing numbering gap accounts for 103 rows up to #104). No past slice regressed.

## Reality surprises
- **The append lock is load-bearing via lost-UPDATE, not interleaving** (build-time discovery, /critique B1): `os.write` is byte-atomic (no interleaving at any size), but Windows `O_APPEND` EOF-positioning is non-atomic across concurrent opens → whole writes lost. Captured for /reflect.
- **An un-barriered multiprocessing-spawn pool staggers ~100ms/worker and never contends** → masks concurrency hazards (the Builder's own first-probe false-negative). Barrier-synchronize concurrency proofs. Captured for /reflect.
- **VWS-1 channel-set is the fail-closed boundary** (/code-review M1): the audit fails-OPEN for write channels outside its enumeration → broadened to os.rename/io.open/shutil; a future write API needs an explicit channel-set + APED-1 extension. Captured for /reflect.
