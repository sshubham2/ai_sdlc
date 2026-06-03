# Critique: Slice 109 add-post-flip-vault-conflict-safety

**Critic reviewed**: mission-brief.md, design.md, ADR-098 (new), project-frame.md
**Date**: 2026-06-04
**Result**: NEEDS-FIXES

## Summary
The core mechanism (route the 3 queue/claim RMW writers through `safe_rewrite_text` under bounded retry) is sound and well-precedented by slice-097's CAS channel; the create-race and lost-update detection work correctly under execution. But the AC4 "byte-for-byte identical" claim is **false when the on-disk queue is ever CRLF** (executed and reproduced); the design under-specifies multi-write/base-capture TOCTOU; record_pick's concurrent path lacks a test; the VWS-1 widening admits a CAS-defeating `expected_base=b""` shape; and ADR-098's relationship to ADR-089's residual should be framed.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC4 "byte-for-byte identical" is false on a CRLF on-disk queue — `safe_rewrite_text` is EOL-PRESERVING, `safe_write_text` is LF-faithful
- **Claim under review**: design.md / ADR-098 §Consequences: "no-flip byte-identity by construction (LF tool-written queue → EOL-preserving CAS matches safe_write_text LF)."
- **Issue**: The claim is conditioned on the queue being LF on disk, which is **not invariant**. Critic executed both writers against a CRLF-on-disk queue: `safe_rewrite_text` preserved CRLF (via `_detect_eol`, `tools/_vault_write.py:64`/`:244`), `safe_write_text` wrote LF — **outputs NOT byte-identical** (`out2 == out3 → False`). `.gitattributes` has **no `eol=lf` rule for `architecture/**`** (verified — only `skills/**/SKILL.md`, `agents/*.md`, etc.). ADR-088 documents that `architecture/**` files ARE CRLF on Windows checkouts precisely because `.gitattributes` doesn't normalize them. A `core.autocrlf=true` checkout / editor save / normalize pass can introduce CRLF into `slice-queue.md`; once that happens the routed writer silently changes EOL behavior vs the pre-slice `safe_write_text` path. Same class slice-097 design-Critic B1 caught (the "byte-faithfulness inherited" hand-wave).
- **Evidence**: Executed CASE2: on-disk CRLF=7 → `safe_rewrite_text` CRLF=10 (preserved), `safe_write_text` CRLF=0; `out2==out3 → False`. `tools/_vault_write.py:64-70`, `:244-251`. `.gitattributes` (no `architecture/**`). ADR-088 §Decision.
- **Proposed fix** (Critic): (a) make the routed queue write LF-canonical; OR (b) add an `eol=lf` rule for the queue to `.gitattributes` so the LF precondition is enforced; OR (c) downgrade AC4 to the conditioned claim + add a CRLF-on-disk test. Whichever path, stop asserting unconditional byte-identity + add a CRLF-on-disk TF-1 row (APED-1: execute the routed writer against a CRLF fixture).
- **Builder draft**: **ACCEPTED-PENDING** — adopt (b)+(c): (1) add `architecture/slice-queue.md eol=lf` to `.gitattributes` to **enforce** the LF precondition (the queue is a tool-owned regenerable artifact, legitimately LF-canonical — unlike the hand-edited CRLF aggregates `_index.md`/`risk-register.md` `safe_rewrite_text` was built EOL-preserving for); (2) correct AC4/design/ADR-098 from unconditional to enforcement-conditioned byte-identity, documenting the EOL-preserving behavior on a stray-CRLF edge; (3) add a CRLF-on-disk TF-1 test row pinning the writer's behavior by execution. **Prose corrections (AC4 wording, design note, ADR framing, TF-1 row) applied now in this round**; `.gitattributes` + the CRLF test land in `/build-slice`.

### Majors (address this slice)

#### M1: Multi-write atomicity + base-capture/read TOCTOU under-specified — CAS protects each whole-file write, not the two-phase sequence or a read-elsewhere
- **Issue**: CAS makes each single whole-file write lost-update-safe, but the design doesn't pin: (a) `write_slice_queue` reads `existing_text` at `tools/slice_queue_writer.py:848` to parse claims + extract pick-log — the `expected_base` (`read_bytes()`) MUST be the SAME bytes decoded into `existing_text` (one read, not `read_bytes()` for base + a separate `read_text()` straddling a concurrent write); (b) between base-capture and CAS write, `write_slice_queue` runs `derive_active_slice_blast_radius` (`:868`) which spawns graphify subprocesses (~30s timeout each) — CAS detects a stale base after it (→ retry) but could re-spawn graphify each retry (livelock cost); (c) `slice_queue_claim.main` (`tools/slice_queue_claim.py:595`→`apply_claim`→`_atomic_write_text`) must re-run `apply_claim`/`apply_release` on the re-read text inside the retry, force-claim path included.
- **Evidence**: `tools/slice_queue_writer.py:846-860,868`; `tools/slice_queue_claim.py:595-616` (4 write sites).
- **Proposed fix** (Critic): pin three invariants in design.md — (1) single `read_bytes()` per attempt feeds both base + composition (decode it, don't re-`read_text()`); (2) re-run full compose on the fresh base inside each retry, and hoist graphify `active_blasts` OUT of the retry loop (independent of queue bytes); (3) `slice_queue_claim.main` re-runs apply_claim/release on re-read inside the retry. Add a test: a concurrent mutation between base-capture and write triggers exactly one retry and both updates land.
- **Builder draft**: **ACCEPTED-PENDING** — all three invariants are correct and close real TOCTOU/livelock gaps. Pinning them in design.md now (this round); implementation + the one-retry-both-land test land in `/build-slice`. The single-read-feeds-both-base-and-composition invariant is the load-bearing one.

#### M2: `record_pick` is a genuine RMW — confirm it is exercised in the AC2 proof + add a concurrent-distinct-slice test row
- **Issue**: `record_pick` (`tools/slice_queue_writer.py:742-802`) reads the queue, idempotency-scans the pick-log, appends a line, writes via `safe_write_text` (`:801`). Two different slices picking concurrently produce different prefixes — both MUST survive (exactly the lost-update this slice fixes), which works only if the retry re-reads the other slice's line and the idempotency prefix-scan re-runs on the fresh base. No TF-1 row covers "two concurrent `record_pick` for distinct slices → both pick-log lines survive," and it's unconfirmed that AC2's N≥4 proof exercises `record_pick` (not only `write_slice_queue`+claim). The pick-log is the BRANCH-3/ADR-090 provenance ledger committed per pick on the shared main-tree default branch — concurrent picks are the normal PSQ+BRANCH-3 state; a lost line is silent provenance corruption.
- **Evidence**: `tools/slice_queue_writer.py:782-801`. CLAUDE.md BRANCH-3 (pick-log committed alone per pick).
- **Proposed fix** (Critic): add a TF-1 row "concurrent `record_pick(slice-A)` ‖ `record_pick(slice-B)` under mp.Barrier → both lines present, 0 lost"; confirm AC2 exercises `record_pick` as a distinct mutation; state in design.md that the idempotency prefix-scan re-runs on each retry's fresh base.
- **Builder draft**: **ACCEPTED-PENDING** — adding the TF-1 row now (this round) + stating AC2 MUST exercise `record_pick` as one of the ≥4 distinct mutations + the re-scan-on-retry note in design.md. Implementation/test land in `/build-slice`.

### Minors (log; address if cheap)

#### m1: VWS-1 `_ROUTED_FUNCS` widening admits a CAS-defeating `expected_base=b""` call shape (name-only match)
- **Issue**: `_is_routed_call` (`tools/vault_write_safety_audit.py:401-408`) matches function NAME only. Adding `safe_rewrite_text` makes `safe_rewrite_text(p, text, expected_base=b'')` read as routed/CLEAN even though a constant-`b""` base is CAS-defeating. **Bounded**: `expected_base` is a *required keyword-only* arg (`tools/_vault_write.py:207`) → `safe_rewrite_text(p, text)` is a runtime `TypeError`, so the "no base" shape can't ship; only the degenerate-constant-base shape is the residual.
- **Proposed fix** (Critic): cheap defense-in-depth — when `_is_routed_call` matches `safe_rewrite_text`, additionally require an `expected_base=` keyword present; at minimum add a visible-residual note to the audit docstring (the module's "residuals pinned VISIBLE" discipline, `:55-59`).
- **Builder draft**: **ACCEPTED-PENDING** — add the `expected_base=`-keyword-present check to VWS-1's `safe_rewrite_text` recognition (rejects the degenerate shape as NOT-routed → it would then be flagged) + a test; this is cheap and closes the residual rather than only documenting it. Lands in `/build-slice`.

#### m2: ADR-098 `supersedes: null` but partially discharges ADR-089's residual — frame the relationship
- **Issue**: ADR-089 §Residual (`ADR-089.md:59`) names "wire the `_vault_write`-lock substitute" as deferred; ADR-098 closes the write-time-replacement half ahead of the flip. `supersedes: null` is correct (narrows, doesn't reverse) but the relationship should be explicit. ADR-098 is the next free number (master tops at ADR-097 — verified).
- **Proposed fix** (Critic): add one sentence to ADR-098 §Context/Consequences: "Partially discharges ADR-089 §Residual's `_vault_write`-lock substitute (the write-time replacement); the PCR RETIRE no-op + distinct PCR signal remain ADR-089's flip-slice residual." Keep `supersedes: null`.
- **Builder draft**: **ACCEPTED-FIXED** at ADR-098 §Context — framing sentence added this round; `supersedes: null` retained.

## Dimensions checked
- [x] Unfounded assumptions — B1 (the "tool-written LF → byte-identical" assumption is false on CRLF, executed); M1 (base-capture==composition-read assumption unstated). No docstring-vs-code drift in `_vault_write`.
- [x] Missing edge cases — concurrent covered by AC2 but M2 (record_pick may be unexercised) + M1 (graphify-in-window livelock); create-race executed → CAS correctly raises (no finding); CRLF on-disk → B1; EPERM-retry inherited (adequate).
- [x] Over-engineering — none. Optional `rewrite_with_retry` helper vs inlined is a minimal Builder choice; no speculative generality.
- [x] Under-engineering — M1 (TOCTOU invariants not pinned); M2 (no concurrent-record_pick TF-1 row); B1 (no CRLF-on-disk test element).
- [x] Contract gaps — none new. `safe_rewrite_text` signature unchanged; retry-exhaustion-RAISES contract specified + fail-visible.
- [x] Security — none. No auth surface (N/A correct); cooperative-model cross-process safety, not a security boundary (ADR-067). m1 is data-integrity audit-widening, not authz.
- [x] Drift from vault — ADR-098 is next free (master tops ADR-097, verified); R-32 stays `mitigating` (correct, risk-register.md:594-596); VWS-1 PCR scoped-out allowlist untouched (correct); m2 (ADR-089-residual framing). Strategic-direction fit: ADVANCES the external-vault flip trajectory (capability-without-flip, mirrors 093/100/102). The queue/pick-log RMW IS the normal N-concurrent PSQ+BRANCH-3 state (no cry-wolf inversion).
- [x] Web-known issues — none novel; local Windows-filesystem CAS over `os.replace`+`msvcrt.locking`, field-validated by 094/097.
- [x] Cross-cutting conformance — APED-1 applied (B1, m1 execution-derived, not prose-derived); VWS-1 membership-pin extension sound (`test_vault_write_safety_audit.py:335,346`); FBCD-1 sub-mode-c: `_ROUTED_FUNCS` cardinality 2→3 — no `len(_ROUTED_FUNCS)==2` literal exists (pin is `sites_routed>=4`, `:69`), so no count-literal fan-out tripped (Builder must confirm none added); MEPD-1-EXCLUDE path correct (097/098 precedent).

## Triage

**Triaged by**: user
**Date**: 2026-06-04
**Final verdict**: NEEDS-FIXES

Reconciles both passes (first Critic B1/M1/M2/m1/m2 + meta-Critic EXTEND missed findings M-add-1/M-add-2). User ratified all draft dispositions as drafted (TRI-1, 2026-06-04).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | `.gitattributes eol=lf` enforce + AC4/design/ADR wording corrected now + CRLF-on-disk test in build |
| M1 | Major | ACCEPTED-PENDING | pin single-read-base + hoist-graphify + claim re-run invariants in design now; impl + one-retry test in build |
| M2 | Major | ACCEPTED-PENDING | add concurrent-record_pick TF-1 row now; AC2 must exercise record_pick; impl in build |
| m1 | Minor | ACCEPTED-PENDING | VWS-1 require `expected_base=` present (reject degenerate shape) + test in build |
| m2 | Minor | ACCEPTED-FIXED | ADR-098 framing sentence added; supersedes:null retained |
| M-add-1 | Major | ACCEPTED-FIXED | (meta-Critic) scoped "loud" must-not-defer to the non-regenerable provenance writer record_pick; write_slice_queue swallow correct per ADR-064 — applied now in mission-brief + design |
| M-add-2 | Major | ACCEPTED-PENDING | (meta-Critic) empty-base first-pick create-race TF-1 row added now; test in build |
