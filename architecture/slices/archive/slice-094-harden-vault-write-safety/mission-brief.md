# Slice 094: harden-vault-write-safety

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 — **NOT retired by this slice**; ships **flip-readiness** toward it. R-32 stays `mitigating` and retires at the flip (it is the load-bearing flip blocker; its concurrent-write hazard becomes live only when the vault is untracked + shared — `risk-register.md:578`).
**Test-first**: false  (the byte-identity + concurrency proofs are authored alongside the fix; the primitives exist but are byte-buggy — see AC1)
**Walking-skeleton**: false
**Exploratory-charter**: false

> **Redesigned 2026-06-01** — v1 ACs 1/5 over-claimed ("every call site routes through" / "transparent / suite green") and were BLOCKED at `/critique`. This v2 reflects the TRI-1-ratified flip-readiness scope. See design.md §"Why v2".
> **Redesigned 2026-06-01 (v3, narrow — AC4 only)** — the v2 ">1024B concurrent-append interleaving" Proof 2 was empirically FALSIFIED at build (`safe_append_text`'s single `os.write` is atomic at all sizes) and replaced by VERIFIED deterministic exclusive-holder EPERM-resilience for BOTH primitives. User TRI: "Halt + formal redesign". See design.md §"Why v3".

## Intent

slice-093 shipped the R-32 write-safety *primitives* (`tools/_vault_write.py`) but `/critique` proved, against the real code, that (a) **both** primitives emit CRLF on Windows while every existing vault writer emits LF (`newline=""`), and (b) the real concurrent-write hazard becomes live **only at the flip** — today every vault file is git-tracked, so concurrent mutation surfaces as a git conflict PCR resolves loudly. So this slice is re-scoped to **flip-readiness**: fix the primitives' byte-faithfulness, route the **2 seam whole-file writers** through them, ship a fail-closed **per-write-target** audit that makes a future bypass un-mergeable, and **prove** no corruption under N parallel processes. `parallel_conflict_resolver` (git-coupled) is scoped OUT — it retires at the flip. R-32 stays `mitigating`.

## Acceptance criteria

1. **Primitive byte-faithfulness**: `safe_write_text` (`newline=""`) and `safe_append_text` (`os.O_BINARY`) emit LF, byte-identical to the canonical `newline=""` writer (`slice_queue_writer.py:819`); an `nt`-guarded byte-identity test — pinning BOTH a small ASCII payload AND a **large (>1024-byte) multibyte (non-ASCII UTF-8)** payload (m-add-1) — confirms byte-identity and that `O_APPEND` still appends. (Prerequisite to routing — empirically verified at redesign.)
2. **Seam writers routed (honest scope)**: the 2 whole-file vault writers — `slice_queue_writer.py:819-820` and `slice_queue_claim._atomic_write_text` (`:535-536`, called `:599`/`:607`/`:613`) — route through `safe_write_text` with byte output unchanged. Routing buys byte-faithful + atomic-write + EPERM-resilience; it does **NOT** close the read-modify-write lost-update window (the caller reads before the lock-scoped write) — that window is a documented **flip-residual** (git-protected today), NOT claimed closed (B2). `parallel_conflict_resolver` is explicitly scoped OUT (git-coupled; retires at flip).
3. **Fail-closed enforcement audit**: `tools/vault_write_safety_audit.py` uses **per-write-target** AST detection (the target of a write op is a vault literal / `VAULT_ROOT`-derived — NOT module-mentions-a-literal), governs the seam writers, carries a rationale-bearing + COUNT-pinned scoped-out allowlist (PCR), exempts `_vault_write.py`, and exits non-zero on any unclassifiable vault write; its APED-1 battery is EXECUTED (planted-raw → VIOLATION; routed → CLEAN; reader-with-non-vault-write → CLEAN; PCR → CLEAN-SCOPED-OUT). Wired into `/build-slice` Step 6 + `/validate-slice` + shippability.
4. **Concurrency proof (non-vacuous, VERIFIED-deterministic — proves what the lock ACTUALLY protects)**: a `multiprocessing`(spawn) + **`mp.Barrier`** + bounded-timeout test proves, per primitive — **Proof 1 (whole-file)**: `nt`-guarded EPERM-resilience under an exclusive `CreateFileW dwShareMode=0` holder (Event-gated so the raw EPERM is deterministic and the safe path has wide retry-budget margin — M1); raw `os.replace` → `WinError 5`, `safe_write_text` → succeeds. **Proof 2 (append LOST-UPDATE prevention — the real R-32 append hazard, B1)**: N barrier-synchronized workers each append a unique multi-KB payload; `safe_append_text` → all N survive; mutation (strip lock → raw `os.open(O_APPEND)`+`os.write`) → whole writes LOST (B1-verified: 16 workers → 5-10 survive unlocked, N/N locked). Non-vacuity by mutation (both proofs FAIL when lock+retry is stripped). **M2**: the lost-update mutation is `nt`-guarded (POSIX `O_APPEND` atomic), but the safe-path "zero writes lost under N concurrent workers" assertion runs cross-platform (a POSIX failure = a flip-blocking discovery) — explicitly a non-regression **CANARY** on POSIX, NOT lock-value coverage there (M-add-1: POSIX unlocked also survives, so no mutation arm fails); genuine POSIX lock-value proof is flip-slice work. **Corrected from v3-first-pass**: the append hazard is lost-UPDATE, NOT byte-interleaving (`os.write` is byte-atomic → no interleaving at any size; but concurrent `O_APPEND` EOF-positioning is non-atomic on Windows → lost writes — design § Why v3). The v2 ">1024B interleaving" framing AND the v3-first-pass "no corruption / drop the proof" were BOTH wrong.
5. **No-flip contract + R-32 reframe**: `resolve_vault_root()` default unchanged (`architecture/`); full suite green; `architecture/risk-register.md` records R-32 **staying `mitigating`, reframed "retires at the flip"** (this slice = flip-readiness, NOT retirement), with the explicit residual (PCR + git/worktree-coupled tools + physical move + prose rewrite).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Primitive byte-faithfulness | `test_vault_safe_write.py` nt-guarded byte-identity test: `safe_write_text` / `safe_append_text` output == canonical `newline=""` writer bytes, for BOTH a small ASCII AND a >1024-byte multibyte payload (m-add-1); a 2nd `safe_append_text` confirms `O_APPEND` still appends |
| 2 | Seam writers routed | grep: `slice_queue_writer.py` + `slice_queue_claim.py` call `safe_write_text`; bytes of a re-written `slice-queue.md` are identical pre/post-routing; PCR untouched (`git diff` empty) |
| 3 | Audit fails closed | `$PY -m tools.vault_write_safety_audit --repo-root .` exits 0; plant a raw vault write → exits 1 naming file:line; restore → 0. APED-1 battery: PCR → CLEAN-SCOPED-OUT, reader-with-non-vault-write → CLEAN. Listed in `/validate-slice` + shippability.md |
| 4 | Concurrency proof (non-vacuous, VERIFIED) | `$PY -m pytest tests/methodology/test_vault_write_safety_concurrency.py` PASSES (spawn + `mp.Barrier` + bounded timeout); mutation strip-lock FAILs BOTH proofs — Proof 1: raw `os.replace` under an exclusive `CreateFileW dwShareMode=0` Event-gated holder → EPERM; Proof 2: raw `os.open(O_APPEND)` barrier-synchronized → whole writes LOST (survivors < N). Safe path: `os.replace` succeeds, all N appends survive. (Append proof is lost-UPDATE prevention, not interleaving — design § Why v3.) |
| 5 | No-flip contract + R-32 reframe | Full suite green (`$PY -m pytest`); `resolve_vault_root()` no env/config → `Path("architecture")`; `$PY -m tools.risk_register_audit … --json` shows R-32 `mitigating`, reframed "retires at flip" |

## Must-not-defer

- [ ] New audit rule (AC3) propagates a shippability.md row (#102) per RPCD-1 / SCPD-1 — write-safety enforcement must never silently regress.
- [ ] The audit is cp1252-safe (UTF8-STDOUT-1 stdout + defensive stderr-at-import) — slice-093 RSAD-1: a vault-infra tool nearly shipped its own cp1252 crash.
- [ ] The completeness audit fails CLOSED — an unclassifiable vault write is a violation, not a silent skip (the R-7 silent-disable class).
- [ ] The concurrency test is non-vacuous — proven by mutation (strip lock+retry → Proof 1 raw `os.replace` EPERMs / Proof 2 raw `os.open(O_APPEND)` loses whole writes); **`multiprocessing`(spawn) + `mp.Barrier`, NOT threads** (M3: GIL masks contention; AND an un-barriered spawn pool staggers ~100ms/worker → never contends → masks the hazard — the B1 false-negative); **bounded timeout** so a lock-hang fails loud. Proof 1 (whole-file EPERM) is `nt`-guarded + Event-gated (M1); Proof 2 (append LOST-UPDATE) safe-assertion is cross-platform, its mutation `nt`-guarded (M2). The append hazard is lost-UPDATE, not interleaving (design § Why v3).
- [ ] **Both** primitives byte-faithful (LF) BEFORE routing — `safe_write_text` `newline=""` AND `safe_append_text` `os.O_BINARY` (the v1 "`safe_write_text` keeps `newline=\"\n\"`" claim was false — empirically both emitted CRLF on Windows).
- [ ] The APED-1 battery is **EXECUTED** against the real `tools/` corpus (BC-PROJ-13); the `/code-review` pass is a required SECOND APED-1 author (slice-085 blind-spot lesson).
- [ ] New-tool count-bump fan-out (N≥3) — the PMI-1 bump is **5-part** (M1): `install_audit.py:92` `_CANONICAL_TOOLS`, `plugin.yaml` (tools + `version`), `VERSION` + **`pyproject.toml [project].version` (PVFS-1)** + `~/.claude/ai-sdlc-VERSION`, `INSTALL.md` count, the cp1252 parametrize list, AND any per-tool inventory-pin test all enumerate `vault_write_safety_audit.py` — grep EVERY count literal.
- [ ] Changelog version-gate supersession + entry-pin pair (M1 / EPGD-1): supersede `test_version_files_synchronized_at_v_0_<latest>` → `_at_v_0_80_0` PRESERVING prior entry-pins; add `test_v_0_80_0_vws_1_entry_present_in_repo` + `_shippability_consumer_propagation`.

## Out of scope

- **`parallel_conflict_resolver` (PCR) routing** — git-coupled; concurrent mutation surfaces as a loud git conflict PCR resolves pre-flip; routing/retiring it is the flip slice's work (slice-093 migration map). Scoped OUT, recorded in the audit allowlist with rationale (B3-ratified).
- The **flip** itself (tier-2 `<git-common-dir>/aisdlc/vault-root` config / physical move of `architecture/` + the git-untrack decision + prose rewrite + rethink the 3 git/worktree-coupled tools) — a later slice, gated on this flip-readiness slice + the already-shipped slice-095.
- The **skill-driven Write/Edit** sub-class — **already shipped** (slice-095 / SVW-1).
- R-30 worktree / multi-root resolver edge cases — separate residual, closes at the flip.
- A migration command for existing projects' in-repo `architecture/` → external vault — later in the initiative.
- Non-vault writes in `tools/*.py` (graphify-out / diagnose-out / temp / tool-own-output) — out of the audit's scope by construction (vault-target-only).

## Dependencies

- Prior slices: [[slice-093-add-external-vault-support]] — ships `tools/_vault_write.py` (the safe primitives) + `tools/_vault_paths.py` (`resolve_vault_root`, the seam).
- Vault refs: [[decisions/ADR-085]] (external-vault capability, no-flip), [[decisions/ADR-065]] (resolver seam).
- Risk register: [[risk-register#R-32]] (the risk this narrows — load-bearing flip blocker), [[risk-register#R-30]] (sibling resolver residual).

## Mid-slice smoke gate

At ~50% of build (writers routed + audit exists), run:
```
$PY -m tools.vault_write_safety_audit --repo-root .          # expect exit 0
# revert ONE routed writer to a raw write_text, re-run            # expect exit non-zero, names file:line
# restore it
$PY -m pytest tests/methodology/test_vault_write_safety_concurrency.py
```
Expected: audit clean on the routed tree, loud on a reverted writer; concurrency test PASSES. If the audit passes on a known-raw write (fails open) or the concurrency test is vacuous: STOP, fix the audit/test before continuing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] Ran in a real BRANCH-2 worktree (NOT WORKTREE=skip — per the slice-090/093 directive; slice-093 used WORKTREE=skip for entangled scaffolds, 094 must isolate)
- [ ] **R-33 master-merge FIRST (M-add-1)**: this worktree is BEHIND master (slices 095/096 merged there, NOT here). `/commit-slice` MUST `git merge master` before the pre-finish full-suite — the version target is **v0.80.0** (NOT 0.79.0, taken by merged slice-095), and the 5-part PMI-1 gate + cp1252 list + entry-pins reconcile against the POST-095 state, not this worktree's stale 0.78.0. Run the in-worktree full suite only AFTER the merge so the gate reflects integration reality.
