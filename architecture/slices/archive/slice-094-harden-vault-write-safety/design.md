# Design: Slice 094 harden-vault-write-safety (v2 — flip-readiness redesign)

**Date**: 2026-06-01
**Mode**: Standard
**Redesign of**: design v1 (BLOCKED at `/critique` 2026-06-01 — 3 execution-verified blockers, all ratified at TRI-1). This v2 is the ratified **flip-readiness** redesign; it does not supersede a shipped ADR (ADR-086 is revised in place — a same-slice, unshipped, pre-build decision, not a SUP-1 supersession of a merged decision).

## Why v2 (the three ratified blockers)

| Blocker | What the Critic proved against real code | v2 response |
|---------|------------------------------------------|-------------|
| **B1** | Both `_vault_write` primitives emit **CRLF** on Windows while every existing vault writer emits **LF** (`newline=""`). Empirically re-verified this redesign (venv `os.name=nt`, `utf8_mode=0`): `safe_write_text("a\nb\n")` → `b'a\r\nb\r\n'` (text-mode `write_text` default); `safe_append_text(...)` → `b'a\r\nb\r\n'` (**`os.open` defaults to text mode on Windows** — my own code-read wrongly assumed binary; the probe corrected it). Canonical writer (`tmp.write_text(..., newline="")`) → `b'a\nb\n'`. Routing as-is would corrupt every vault file's newlines (EOL-DRIFT-1 / ADR-033 class). | Fix **both** primitives to be byte-faithful (LF) **before** any routing. Empirically confirmed fix → `b'a\nb\n'`, O_APPEND still appends. nt-guarded byte-identity regression test. |
| **B2 / M1** | The v1 "VAULT_ROOT-import tripwire" misses `parallel_conflict_resolver.py` (imports **neither** `VAULT_ROOT` nor `_vault_paths`; 7 raw write ops). The v1 "literal-vault-path secondary" false-positives on 37 reader modules (readers `git show`/`read_text` vault literals). | Redesign detection to **per-write-target AST analysis** — the *target of a write op* is a vault literal / `VAULT_ROOT`-derived expr, not "module mentions a literal." Readers never match (a `read_text`/subprocess-arg is not a write op). |
| **B3** | R-32's concurrent-write lost-update "becomes live only at the slice-094 **flip**" (`risk-register.md:578`). Pre-flip every target is **git-tracked**, so concurrent mutation surfaces as a git conflict PCR resolves; process-locks add no safety now, and slice-093's map classifies PCR as git-coupled → "retires at the flip." | Re-scope to **flip-readiness**: byte-faithful primitive + route only the **2 seam whole-file writers** + enforcement audit + concurrency **proof**. **Scope PCR OUT** (git-coupled). R-32 reframed "retires at the flip," stays `mitigating` (this slice does NOT retire it). |

## Why v3 (the AC4 proof correction — build-time reconciliation, then a /critique B1 self-correction)

> **Redesigned 2026-06-01 (v3, narrow — AC4 concurrency proof ONLY)** — user TRI ("Halt + formal redesign") after a Task-4 probe falsified the v2 Proof 2; then the v3 `/critique` (B1) caught a Builder OVER-correction, re-verified by a barrier-synchronized probe. Everything else (byte-fix Task 1, routing Task 2, the VWS-1 audit + APED-1 battery Task 3) is BUILT, verified, and UNAFFECTED. [[ADR-086]] (audit + byte-fix) references "concurrency proof" generically and is unaffected.

The correction happened in **two turns** (the two-persona model working as designed):

1. **The v2 ">1024-byte concurrent-append INTERLEAVING" framing was wrong.** `safe_append_text`'s single `os.write` is byte-atomic (one Windows `WriteFile`), so concurrent `O_APPEND` never SPLICES bytes within a write — verified: a surviving worker's bytes are always one contiguous run, at any size (4KB/64KB/512KB). `bugs.python.org#15723`'s ">1024B" is a buffered/text-mode `f.write()` issue, not this raw-`os.write` channel.
2. **But the Builder's v3 then OVER-corrected** — concluding "no interleaving ⇒ no corruption ⇒ the append lock protects nothing observable" and DROPPING the append proof. The v3 `/critique` **B1** disputed this. A **barrier-synchronized** probe (forcing real simultaneous contention — the Builder's earlier probe used spawn workers that start ~100 ms apart and so never actually overlapped, masking the hazard) confirmed the Critic: **unlocked concurrent `O_APPEND` loses WHOLE writes** on Windows — 16 workers → 5-10 survive, 32 → 7-15, deterministically at every size 64B-64KB — because the `O_APPEND` EOF-positioning is **not atomic across concurrent opens** (two opens compute the same end offset; the second clobbers the first). `safe_append_text`'s sidecar lock eliminates the loss completely (N/N survive, every run). **The append lock is LOAD-BEARING** — it prevents exactly the R-32 lost-update hazard the primitive's own docstring (`_vault_write.py:14`, :128-129) promises to close. "No byte-interleaving" is NOT "no corruption"; the v3 conflated them.

So corrected v3 keeps a whole-file proof AND an append proof, but the **append proof is lost-update prevention** (not interleaving, not merely EPERM) — the most faithful, deterministic R-32 proof available. See § Concurrency proof.

## What's new

- `tools/vault_write_safety_audit.py` (NEW) — the **VWS-1** fail-closed **per-write-target** AST audit (replaces v1's import-tripwire model). Exit 0 clean / 1 violation / 2 usage-error (fail-visible, R-7 class).
- `tests/methodology/test_vault_write_safety_audit.py` (NEW) — VWS-1 contract + **executed** APED-1 battery (both false-positive AND false-negative directions, run against the real `tools/` corpus).
- `tests/methodology/test_vault_write_safety_concurrency.py` (NEW) — R-32 concurrency **proof** via `multiprocessing` (spawn) + **`mp.Barrier`** + bounded timeout: Proof 1 = whole-file EPERM-resilience (`safe_write_text`/`os.replace`, `nt`-guarded, M1 Event-gated holder); Proof 2 = **append LOST-UPDATE prevention** (`safe_append_text`, barrier-synchronized — B1-verified: unlocked loses whole writes, locked N/N; M2 cross-platform safe assertion); non-vacuity by mutation. See § Why v3 / § Concurrency proof.
- **Byte-identity regression test** — EXTENDS the existing `tests/methodology/test_vault_safe_write.py` (slice-093's primitive test home; no new module) with an `nt`-guarded assertion that both primitives are byte-identical to the canonical `newline=""` writer (B1/M4, m2).
- A new methodology rule **VWS-1** (MEPD-1 **INCLUDE** — non-underscore, gate-wired audit minting a RULE-ID; BCI-1/SRSC-1 shape): methodology-changelog entry + VERSION bump + PMI-1 fan-out + shippability row.
- `.gitignore` entries — corrected globs **`*.lock`** + **`*.tmp`** (M4: v1's `*.<pid>.tmp` matched nothing — temp files are `<name>.<pid>.tmp`, so `*.tmp` is the correct glob).

## What's reused

- `tools/_vault_write.py` — `safe_write_text` / `safe_append_text` ([[ADR-085]]). This slice **fixes their byte-faithfulness** (B1) and routes the 2 seam writers through them. Their concurrency machinery (sidecar `.lock`, atomic `os.replace`, `O_APPEND`, bounded EPERM-retry) is unchanged.
- `tools/_vault_paths.py` — `VAULT_ROOT` / `resolve_vault_root` (the seam, [[ADR-065]]+[[ADR-085]]). The audit uses it as ONE detection signal (VAULT_ROOT-derived write target), no longer the SOLE one.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` (UTF8-STDOUT-1) + the cp1252-defensive stderr pattern; the new audit MUST use it (slice-093 RSAD-1 — a vault-infra tool must not ship its own cp1252 crash).
- Closed-world allowlist precedent — slice-041 `_REGISTERED_INSTALLED_READERS` + slice-095 SVW-1's per-`(file,reason)` COUNT-pinned exemption allowlist. VWS-1's scoped-out allowlist reuses this fail-closed-against-silent-scope-creep posture.
- Existing canonical LF writers: `slice_queue_writer.py:819`, `slice_queue_claim.py:535` (both `write_text(..., newline="")`), and the 7 PCR ops (all `newline=""`) — the byte-faithfulness target.
- Risk: [[risk-register#R-32]] (the load-bearing flip blocker — this slice ships flip-READINESS, does NOT retire it).

## Primitive byte-faithfulness fix (B1 / M4 — the prerequisite to all routing)

The routing in AC2 is only safe (byte-transparent) if the primitives match the canonical `newline=""` LF convention. Both currently fail; both are fixed:

- `safe_write_text` (`tools/_vault_write.py:104`): `tmp.write_text(text, encoding=encoding)` → `tmp.write_text(text, encoding=encoding, newline="")`.
- `safe_append_text` (`tools/_vault_write.py:138`): `os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)` → add `| getattr(os, "O_BINARY", 0)` (Windows defaults `os.open` to **text mode**, translating `\n`→`\r\n`; `O_BINARY` suppresses it; `getattr(...,0)` is a POSIX no-op).

**Empirically verified this redesign** (probe, then deleted): post-fix both → `b'a\nb\n'` (byte-identical to the canonical writer); a second `safe_append_text` still appends (`b'a\nb\nc\nd\n'`), so `O_BINARY` does not disturb `O_APPEND`. This **changes the primitives' observable byte-output** → ADR-086 "signatures unchanged" is corrected (M4). **m3 (corrected)**: the only production caller today is the in-module `write_vault_root_config` (`_vault_write.py:161`; config writes are `.strip()`-read at `:174` so the CRLF was latent) — the byte-fix also corrects that latent CRLF; the byte-identity test is first-use validation for the seam writers. **m-add-1**: the `nt`-guarded byte-identity test (in `test_vault_safe_write.py`) MUST pin a **large (>1024-byte) multibyte (non-ASCII UTF-8)** payload, not just `a\nb\n` — the CRLF-fix interacts with both newline position AND the 1024-byte Windows write boundary (a CRLF surviving past byte 1024, or a multibyte sequence straddling the split, would pass an `a\nb\n` test yet corrupt a real vault file).

## The governed vault-writer set (code-grounded, re-derived — m1 fixes ALL stale line numbers)

| # | Module | **Real** write site (re-derived) | Vault target | Class | v2 action |
|---|--------|----------------------------------|--------------|-------|-----------|
| 1 | `tools/slice_queue_writer.py` | `:819` `tmp_path.write_text(body, newline="")` + `:820` `os.replace` | `slice-queue.md` | whole-file | **route** → `safe_write_text` |
| 2 | `tools/slice_queue_claim.py` | `:535` `tmp_path.write_text(text, newline="")` + `:536` `os.replace` (in `_atomic_write_text`, called `:599`/`:607`/`:613`) | `slice-queue.md` | whole-file | **route** → `safe_write_text` |
| — | `tools/parallel_conflict_resolver.py` | `:430`,`:1546` `write_text(newline="")`; `:713`,`:764`,`:1779`,`:2133`,`:2234` `open("a", newline="")` | `slice-queue.md` / `shippability.md` / PCR audit log | whole-file + append | **SCOPED OUT** — git-coupled; retires at flip ([[slice-093]] map) |

- Routing #1/#2: replace `tmp.write_text(...,newline="") + os.replace(...)` with `safe_write_text(out_path, body)`. Because the fixed primitive is LF-faithful, the final bytes are **identical** (the transparency claim, now true).
- **B2 (routing scope — honest, TRI-1)**: routing delivers byte-faithful + atomic whole-file write + EPERM-resilience. It does **NOT** close the read-modify-write lost-update window: both callers `read_text` BEFORE the write (`slice_queue_claim.py:592`, `slice_queue_writer.py:731`), and `safe_write_text` holds the sidecar lock only for the write (`_vault_write.py:102`), not across the caller's read — two concurrent claims can both read-old → the second clobbers the first. The RMW window is a **documented flip-residual** (git-conflict-protected today; closed at the flip alongside PCR), NOT closed here. No RMW-spanning helper is added (out of flip-readiness scope).
- `parallel_conflict_resolver._regen_slice_queue` delegates to `slice_queue_writer.write_slice_queue` → transitively inherits #1's routing (no separate site), but PCR's OWN 7 ops stay raw (scoped out) — this is consistent because pre-flip PCR's writes are git-conflict-protected.

## Detection model (B2 / M1 redesign) — per-write-target AST, fail-closed

`tools/vault_write_safety_audit.py` AST-walks every `tools/*.py`. For each **write-op node** — `Attribute` call `.write_text`/`.write_bytes`; builtin `open(target, mode)` / `io.open(target, mode)` / `Path.open(mode)` where `mode` contains `w`/`a`/`x`; `os.open(target, flags)` where `flags` include a true write flag `O_WRONLY`/`O_RDWR`/`O_APPEND` (bare `O_CREAT` excluded — /code-review m1); `os.replace`/`os.rename(src, dst)` and `shutil.move`/`copyfile`/`copy`/`copy2(src, dst)` (target = `dst`, arg1) — it resolves the **write target expression** and classifies:
   - **Channel set (/code-review M1)**: the "fail-closed" guarantee is over THIS enumerated channel set; `os.rename` (the direct twin of `os.replace`) + `io.open` + the `shutil` movers were added at /code-review to close the most-likely R-32 re-opening channel (a future writer reaching the vault via an un-tracked move op). A write API outside this set is an APED-1-pinned residual: extend the set + the planted-VIOLATION battery before such an API enters `tools/`.

1. **Is it a vault write?** — TRUE iff the target is (a) a string `Constant` that equals/contains a known vault basename (`slice-queue.md`, `risk-register.md`, `_index.md`, `shippability.md`, `methodology-changelog.md`, `lessons-learned.md`, ADR files) **or** an `architecture/`-segment path, OR (b) an expression **derived from `VAULT_ROOT`** (the module imports the seam and the target name traces to it). A `read_text`/`git show`/error-string mentioning a vault literal is **not a write op** → never matches (the M1 fix: per-write-target, not per-module-mention).
   - **Target-resolution depth (M2 — bounded + decidable; NOT the rejected interprocedural dataflow)**: resolve the write-op's target through (i) **≤1 intra-function `Name` assignment** (`out_path = repo_root / "architecture" / "x.md"; out_path.write_text(...)`) AND (ii) **module-level `Path(...)`/string constants** (`_AUDIT_LOG_PATH = Path("architecture/...")`). NO interprocedural, container-element, or fixpoint resolution. This is precisely what lets the model catch "PCR's shape" without becoming Option-1's undecidable dataflow: it catches the `var = root/"architecture"/"x.md"; var.write_text()` shape that all 4 real writers + **6 of PCR's 7 ops** use; PCR's `:430` `pending_writes` loop-var (container element) is the **documented accepted residual**. The APED-1 battery MUST plant this `var = root/"architecture"/"x.md"; var.write_text()` shape as a VIOLATION to lock the chosen depth (slice-088 `_RULE_TITLE_RE` precedent).
2. **Classification of a vault write:**
   - In `tools/_vault_write.py` → **EXEMPT** (the sanctioned primitive implementation; its raw `write_text`/`os.replace`/`os.open` ARE the safe channel). Module-name allowlist, not per-line suppression.
   - The write op is a **call to `safe_write_text`/`safe_append_text`** → **CLEAN** (routed).
   - The module is on the **scoped-out allowlist** (`parallel_conflict_resolver`) → **CLEAN-SCOPED-OUT**, carrying a mandatory rationale string (git-coupled; concurrent mutation surfaces as a git conflict PCR resolves; VWS-1 routing deferred to the flip per slice-093's migration map).
   - Otherwise → **VIOLATION** (exit 1, names `path/to/file.py:line` + the un-routed channel). Fail-closed: an unclassifiable vault write is a violation, never a silent pass.
- **Scoped-out allowlist** = `{"parallel_conflict_resolver"}`, pinned by a test on **membership + COUNT** (slice-095 per-`(file,reason)` COUNT precedent) so adding a scoped-out module requires an explicit, reviewed change — fail-closed against silent scope creep. **m2 (corrected)**: only **4** `tools/*.py` contain a write op at all (`_vault_write`, `parallel_conflict_resolver`, `slice_queue_claim`, `slice_queue_writer`); every other module — whether or not it references the seam (the real seam-referencing set is ~11, not 4) or names a vault literal in `read_text`/`git show`/error-prose — has **no write op** → never reaches classification, so no reader needs an allowlist entry.
- **APED-1 obligation (BC-PROJ-13 — executed, not reasoned)**: the matcher is a newly-minted parser → the build MUST run it against the real `tools/` corpus AND an adversarial battery, EXECUTED, covering at minimum: planted raw vault write → VIOLATION; routed write → CLEAN; **reader-with-a-non-vault-write** (writes `graphify-out/` or a tmp) → CLEAN (the M1 false-positive guard); **error-prose-only** module naming a vault literal → CLEAN; PCR → CLEAN-SCOPED-OUT; `_vault_write.py` → EXEMPT. The battery author ≠ the matcher author blind-spot (slice-085): the `/code-review` pass is a required second APED-1 author.

## Concurrency proof (v3, B1-corrected — VERIFIED-deterministic; M3 + barrier-synchronized) — prove what the lock ACTUALLY protects, non-vacuously

`tests/methodology/test_vault_write_safety_concurrency.py`. **Workers + holder are `multiprocessing(spawn)` processes** (NOT threads — `msvcrt.locking` is per-handle + the GIL can mask in-thread contention → a thread test risks passing vacuously; Windows has no `fork`). Real contention is forced with a **`multiprocessing.Barrier`** — all workers poise, then release simultaneously. **This is load-bearing**: an un-barriered spawn pool staggers ~100 ms/worker and the workers never overlap, masking the append hazard entirely — that stagger was the Builder's first-pass false negative the v3 `/critique` B1 caught. Each `join` has a **bounded timeout** so a lock-acquire hang fails loud (cross-process lock tests can hang under pytest — web-known).

Two proofs, one per primitive — each VERIFIED at build (deterministic) and non-vacuous by mutation:

- **Proof 1 — whole-file EPERM-resilience** (`safe_write_text`; `nt`-guarded — Windows `MoveFileEx`/sharing-mode hazard, vacuous on POSIX where `os.replace` is atomic and won't EPERM under a reader): under an EXCLUSIVE external handle (`CreateFileW dwShareMode=0` — the OneDrive/AV/indexer scenario `_vault_write`'s docstring cites), a raw `os.replace(tmp, target)` raises `PermissionError WinError 5`; `safe_write_text`'s lock+retry absorbs it. **M1 (no wall-clock coupling)**: the holder signals "held" via an `Event` BEFORE the raw op runs (so the raw EPERM is deterministic regardless of scheduling), and releases after a hold ≪ the ~3.15 s retry budget (`_EPERM_RETRIES=6` × exp-backoff `0.05·2ⁿ`), so the safe path has wide margin; assert the safe op **SUCCEEDS** (not "within N retries"). Mutation: strip lock+retry → raw `os.replace` under the held handle → FAILS (EPERM). (`os.replace` is OS-atomic → the whole-file hazard is EPERM, not lost-update; last-writer-wins RMW is the documented flip-residual, not closed here.)
- **Proof 2 — append LOST-UPDATE prevention** (`safe_append_text`; the real R-32 append hazard — B1): **N barrier-synchronized** spawn workers each append a UNIQUE multi-KB payload to ONE shared target. **Safe path** (`safe_append_text`): assert **all N payloads survive intact** (N distinct markers present; file length == Σ payloads). **Mutation** (strip the lock → raw `os.open(target, O_WRONLY|O_CREAT|O_APPEND|O_BINARY)` + `os.write`): assert writes are **LOST** (survivors < N). VERIFIED at build (Win11/CPython 3.13.13/spawn, `mp.Barrier`): 16 workers → 5-10 survive, 32 → 7-15, deterministically at every size 64B-64KB; **locked → N/N survive, every run**. The hazard is lost-UPDATE (non-atomic `O_APPEND` EOF-positioning across concurrent opens — two opens compute the same end offset, the second clobbers the first), NOT byte-interleaving (`os.write` is byte-atomic; a survivor's bytes are always contiguous — the v2 interleaving framing was wrong, but so was the v3 "therefore no corruption"). **M2 (cross-platform)**: the lost-update **mutation** is `nt`-guarded (POSIX `O_APPEND` is kernel-atomic → unlocked does not lose → mutation vacuous off-Windows), but the **safe-path positive assertion** ("`safe_append_text` under N concurrent workers loses zero writes") runs **cross-platform** — passes trivially on POSIX today; if it EVER fails there, that is a flip-blocking discovery surfaced now, not at the (possibly Linux/Mac) flip. **M-add-1 (meta-Critic)**: the POSIX safe-path leg is explicitly a **non-regression CANARY, NOT non-vacuous lock-value coverage** — on POSIX, unlocked *also* survives (no mutation arm fails there), so POSIX-green proves only "the lock path doesn't crash/lose under contention on this OS," not that the lock is load-bearing on POSIX. Genuine cross-platform lock-value proof is flip-slice work; the flip slice MUST NOT read POSIX-green as "lock proven load-bearing cross-platform."
- **Non-vacuity by mutation** (slice-092): stripping lock+retry MUST make Proof 1 (EPERM raised) AND Proof 2 (writes lost) FAIL; the safe path → 0 failures. Documented in build-log.md (break → see FAIL → revert). The append lost-update mutation is the most non-vacuous proof available — it is exactly the proof the v3 first-pass wrongly deleted before B1 restored it.

## Count-bump fan-out (M2) — concrete surfaces (executed at build, not reasoned — slice-088/091)

VWS-1 is MEPD-1 **INCLUDE** (new non-underscore gate-wired audit + minted RULE-ID — BCI-1/SRSC-1 shape, unchanged by the flip-readiness reframe). The atomic bump touches these **enumerated** surfaces (build re-runs the audits to verify, per "execute the count, don't reason it"):

| Surface | Concrete site | Change |
|---------|---------------|--------|
| Canonical tools tuple | `tools/install_audit.py:92` `_CANONICAL_TOOLS` — insert between `:126 tools.validate_slice_layers` and `:127 tools.walking_skeleton_audit` (**m5** — alphabetical) | + `"tools.vault_write_safety_audit"` |
| Plugin manifest | `plugin.yaml` tools list + `plugin.yaml:15` `version` | + tool entry; version bump |
| **Version SSoT (PMI-1 is 5-part — M1)** | `VERSION` + **`pyproject.toml [project].version` (PVFS-1, leg 3 — M1)** + forward-synced `~/.claude/ai-sdlc-VERSION` | bump → **v0.80.0** (**M-add-1**: NOT 0.79.0 — taken by merged slice-095; reconcile AFTER `git merge master`, R-33) |
| Changelog | **`methodology-changelog.md` (repo root — m1, NOT `architecture/`)** + installed `~/.claude/methodology-changelog.md` (MCFS-1) | + VWS-1 entry at v0.80.0 |
| **Changelog version-gate + entry-pins (M1 / EPGD-1)** | `tests/methodology/test_methodology_changelog.py` — supersede the live `test_version_files_synchronized_at_v_0_<post-master-merge-latest>` → `_at_v_0_80_0` **PRESERVING prior entry-pins**; ADD `test_v_0_80_0_vws_1_entry_present_in_repo` + `_shippability_consumer_propagation` pair | new pins + gate supersession |
| Install count | `INSTALL.md` tool-count literal(s) | +1 |
| Shippability | `architecture/shippability.md` | + row **#102** (catalog at 101) — regression-clause **carves out the PCR scoped-out allowlist** (**m-add-2**: "no un-routed vault write EXCEPT the COUNT-pinned git-coupled PCR allowlist, retires at flip" — NOT total coverage) |
| cp1252 list | `tests/methodology/test_utf8_stdout_regression.py` parametrize list | + the new audit (prints via `_stdout`) |

The N≥3 lesson: at build, `grep` EVERY count literal (incl. any per-tool inventory-pin test) — the fan-out is wider than any checklist enumerates.

## Components touched

### `tools/vault_write_safety_audit.py` (NEW — VWS-1 audit)
- **Responsibility**: prove no `tools/*.py` writes a vault file by a channel other than the `_vault_write` safe primitives (or the explicit scoped-out allowlist); fail closed on any unclassifiable vault write.
- **Detection**: per-write-target AST (above). **Key interactions**: stdlib `ast`; `tools/_stdout.py` (cp1252-safe); consumed by `/build-slice` Step 6 + `/validate-slice` roster (prose-invoked) + `architecture/shippability.md`.

### `tools/_vault_write.py` (MODIFIED — B1 byte-fix)
- `safe_write_text` + `safe_append_text` gain the byte-faithfulness fix above. No other behavior change.

### `tools/slice_queue_writer.py` / `tools/slice_queue_claim.py` (MODIFIED — routed)
- The whole-file write op (`:819-820` / `:535-536`) becomes a `safe_write_text(target, body)` call. Byte output unchanged.

### `tools/parallel_conflict_resolver.py` (UNCHANGED — scoped out)
- No edit. Recorded in the audit's scoped-out allowlist with rationale. Its routing is the flip's work, not this slice's.

## Contracts added or changed

- `_vault_write` primitives: **byte-output contract changes** (CRLF→LF on Windows) — the only behavioral change, and it makes them MATCH the established `newline=""` convention (B1/M4). Function signatures (parameters) are unchanged; the observable-bytes contract is corrected. ADR-086 revised accordingly.
- VWS-1 audit CLI: exit-code-only (0/1/2) — the established audit-tool shape (RR-1/SRSC-1/BCI-1).
- No endpoints, events, schemas.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/vault_write_safety_audit.py` | `skills/build-slice/SKILL.md` Step 6 + `skills/validate-slice/SKILL.md` gate roster (prose-invoked, per the RR-1/SRSC-1/BCI-1 audit-wiring precedent) | `tests/methodology/test_vault_write_safety_audit.py::test_audit_flags_planted_raw_vault_write` | — |
| `tests/methodology/test_vault_write_safety_concurrency.py` | — | — | internal — rationale: pytest-collected concurrency proof; a test module is self-consuming, no downstream module consumer demanded |

(The B1 byte-identity test extends the existing `tests/methodology/test_vault_safe_write.py` → not a new module → no wiring row.)

## Decisions made (ADRs)

- [[ADR-086]] (**revised in place** — same-slice, unshipped, pre-build) — Enforce vault-write-safety via a fail-closed **per-write-target** AST audit (VWS-1) over a closed-world `tools/` scan, with a rationale-bearing scoped-out allowlist for git-coupled writers; fix the `_vault_write` primitives' byte-faithfulness as the prerequisite — reversibility: **cheap**.

### Sub-decisions (recorded here, not ADR-worthy)

- **PCR scoped out, not routed** (B3): git-coupled; concurrent mutation is a loud git conflict pre-flip; routing it now is work the flip would undo + injects an un-analyzed `.lock`-across-`git rebase --continue` interaction. The flip slice routes/retires PCR-for-vault per slice-093's map.
- **`.lock` + `.tmp` persistence (discharges slice-093 m3)**: lock sidecars are intentionally persistent (deleting one a waiter is about to acquire is a TOCTOU race — standard file-lock posture). Resolution: `.gitignore` `*.lock` + `*.tmp` (corrected globs, M4) so they never pollute `git status` / the future external vault tree.
- **MEPD-1 INCLUDE**: new non-underscore gate-wired audit minting RULE-ID VWS-1 (BCI-1/SRSC-1 shape) → changelog + VERSION + **5-part** PMI-1 fan-out (incl. `pyproject.toml`/PVFS-1) + entry-pin pair + version-gate supersession (EPGD-1) + shippability row. The flip-readiness reframe does not change this.
- **BC-PROJ-12 interaction (m4)**: routing REMOVES the literal `newline=""` from `slice_queue_writer:819`/`slice_queue_claim:535` (it moves inside `safe_write_text`, which now sets it per B1). BC-PROJ-12 (advisory markdown-writer `newline=""` build-check, `test_build_checks_audit.py:1672-1723`) fires on the changed `tools/*.py` hunks; it is satisfied by the primitive's `newline=""` or deferred-with-rationale citing it. Run BC-1 on the routed diff at the mid-slice smoke gate to confirm no hard-fail.
- **v3 concurrency-proof correction (build-time empirical + /critique B1, NOT ADR-worthy)**: the append proof went through TWO corrections (two-persona model working). (1) The v2 ">1024B interleaving" framing was falsified — `os.write` is byte-atomic, no interleaving at any size. (2) The Builder's v3 then OVER-corrected to "no interleaving ⇒ no corruption ⇒ drop the append proof"; the v3 `/critique` **B1** disputed it, and a **barrier-synchronized** probe confirmed the Critic — unlocked concurrent `O_APPEND` loses WHOLE writes on Windows (non-atomic EOF-positioning), which the lock prevents (16 workers → 5-10 survive unlocked, N/N locked). Final Proof 2 = append **LOST-UPDATE prevention** (barrier-synchronized). [[ADR-086]]'s decision (per-write-target audit + byte-fix) is unchanged; this corrects a TEST proof only. **Two DISCOVERED findings for `/reflect`**: (a) the meta-Critic's `bugs.python.org#15723` ">1024B" claim mis-applied a buffered-`f.write()` bug to the raw-`os.write` channel; (b) **an un-barriered spawn pool staggers ~100 ms/worker → never contends → masks concurrency hazards** (the Builder's own false-negative that B1 caught) — concurrency proofs MUST barrier-synchronize. "No byte-interleaving" ≠ "no corruption".

## Authorization model for this slice

Not applicable — local audit/build tooling. Per the cooperative-not-adversarial model ([[ADR-067]]): vault-write-safety is a **data-integrity control, NOT a security boundary**. Defends cooperating writers (two Claude sessions / parallel slices on one machine), not a malicious actor.

## Error model for this slice

- `vault_write_safety_audit.py`: exit **0** (clean) / **1** (≥1 violation — names each `path/to/file.py:line` + un-routed channel) / **2** (usage error — `tools/` unreadable/unparseable; fail-VISIBLE, R-7 class).
- Fail-closed: a write op the AST cannot classify as routed/exempt/scoped-out is a **violation**, never a silent pass.
- The routed primitives keep `_vault_write`'s error model (bounded EPERM-retry → loud `PermissionError`; `TimeoutError` on lock-acquire timeout).

## R-32 disposition (recorded at /reflect, framed here)

This slice ships **flip-readiness**, it does **NOT retire R-32**. R-32 stays `mitigating`, reframed: the concurrent-write hazard **becomes live at the flip** (vault untracked + shared), so it retires when the flip slice lands (which routes/retires PCR + the git-coupled tools + closes the skill-driven sub-class already shipped in slice-095). What this slice delivers toward that: byte-faithful primitives + the 2 seam writers routed + the fail-closed enforcement audit + a non-vacuous concurrency proof. The residual to the flip is explicit: PCR + `stranded_slice_audit` + `pulse_worktree_resolver` (git/worktree-coupled), the physical move, and the prose rewrite.
