# Reflection: Slice 109 add-post-flip-vault-conflict-safety

**Date**: 2026-06-04
**Shipped**: YES

## Validated
- **The CAS channel closes the post-flip queue lost-update class** — validated by a real `multiprocessing(spawn)` N≥4 barrier-synced proof: distinct-slice picks, empty-base create-race, and a mixed record_pick+claim+regen round ALL land 0-lost, while the no-CAS `safe_write_text` control LOSES (non-vacuous). The reconciliation PCR did at git-merge time genuinely transfers to write-time CAS.
- **Single-read base invariant + graphify-hoist are correct** — the code-Critic independently verified the `expected_base` bytes are the same bytes decoded into the compose, and that hoisting `active_blasts` out of the retry loop introduced NO staleness (it depends only on repo_root/graph, not queue bytes).
- **No-flip byte-identity holds with the LF precondition ENFORCED** — `.gitattributes eol=lf` + the executed LF/CRLF tests; full suite 1564 passed (0 behavior change); 102 pre-existing queue/psq/claim byte-equal round-trips unbroken.
- **VWS-1 recognizes the CAS channel + flags the CAS-defeat** — real-corpus audit clean (7 routed); the literal AND name-bound degenerate-base variants are both flagged.

## Corrected
- **This slice's own design.md (m1 wording) → reality** — the initial m1 plan ("recognize routed only when `expected_base=` present") was near-VACUOUS (Python already makes the bare form a `TypeError`); corrected at plan-time to "non-constant `expected_base`", then corrected AGAIN at /code-review to *resolve name-indirection* (a module-const-bound name). design.md + ADR-098 updated to the accurate, gap-closed claim. (No ADR superseded — ADR-098 is this slice's own, edited pre-merge.)
- **ADR-098 stale `_atomic_write_text` reference** — corrected: the claim/release path routes through the new `_cas_rewrite`, not `_atomic_write_text` (now production-orphaned).

## Discovered
- **A versioned guard's "is-this-a-constant" check must resolve NAME-INDIRECTION, not just literal `ast.Constant`** (code-review M1). `expected_base=_NAME` where `_NAME = b""` bypassed the literal-only check. The design-Critic + meta-Critic both reviewed the m1 fix abstractly ("require non-constant base") and neither caught the AST-shape gap; only code-EXECUTION found it. Closed in-slice (resolve via `module_consts`) + an EXECUTED pin. Impact: a fresh instance of AP-4 (code-Critic mandatory for AST/guard tools) + AP-2 (a Critic's/Builder's own FIX is a fresh claim — re-attack the fix-delta on the AST-shape axis). N keeps growing on both.
- **`multiprocessing.Barrier` has no timeout-on-worker-death** (CPython #123899, code-review m2) — a sibling dying after entering the barrier wedges survivors until the join timeout. Latent (the test's `join(120)`+`is_alive` makes it loud); hardened in-slice with `wait(timeout=30)`. Impact: any future barrier-synced concurrency proof should pass a per-`wait` timeout.

## Deferred
- **`_atomic_write_text` full removal** (code-review m1) — production-orphaned but still referenced by `test_psq_2_claim_machinery.py:251`; removal widens scope. Lands in: the slice-061 AI-bloat / cleanup pass.
- **AC3: post-flip `/commit-slice --merge` RETIRE no-op + distinct PCR RETIRE signal** — scope-narrowed at /design-slice per ADR-089 (which assigns commit-slice RETIRE handling to the flip slice + lets it test the REAL external path). Lands in: the flip slice.
- **The physical flip itself** — move `architecture/`+`diagnose-out/` to the external store + `git rm --cached` + `_vault_paths` default flip + the 318-prose rewrite (slice-107 inventory) + the 154 test-update sites (slice-102 inventory). Lands in: the flip-execute slice(s). R-32 retires there.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` + reality observed at build/validate/code-review:

- **B1** (byte-identity false on CRLF): **VALIDATED** — ACCEPTED-PENDING; the executed CRLF test confirmed the divergence exactly as flagged; `.gitattributes eol=lf` + tests closed it.
- **M1** (base-capture/TOCTOU + graphify-livelock): **VALIDATED** — ACCEPTED-PENDING; the single-read invariant + graphify-hoist were genuinely needed; code-Critic confirmed the implementation holds.
- **M2** (record_pick RMW unexercised): **VALIDATED** — ACCEPTED-PENDING; the concurrency proof confirmed distinct picks survive.
- **m1** (VWS-1 expected_base): **VALIDATED-then-EXTENDED** — ACCEPTED-PENDING; the fix was real BUT incomplete (literal-only), and /code-review M1 caught the name-indirection residual — a recursion of "the fix is a fresh claim" (AP-2).
- **m2** (ADR-089 framing): **VALIDATED** — ACCEPTED-FIXED.
- **M-add-1** (meta-Critic; fail-visibility asymmetry): **VALIDATED** — ACCEPTED-FIXED; the `write_slice_queue` raise IS swallowed by Step 6.5's ADR-064 wrapper; the "loud" claim was correctly scoped to the provenance writer.
- **M-add-2** (meta-Critic; empty-base create-race): **VALIDATED** — ACCEPTED-PENDING; the create-race test confirmed concurrent first-picks all create-and-merge.

**Missed by Critic (design + meta stack)**: the code-review **M1 name-indirection CAS-defeat** — neither the design-Critic nor the meta-Critic caught that `isinstance(kw.value, ast.Constant)` only catches LITERAL constants; only code-execution (the code-Critic) found the AST-shape gap. Also **m1** (`_atomic_write_text` would become production-orphaned) — the design-Critic's "what's reused" noted it retained but didn't predict the orphaning.

**Pattern**: the 3-Critic stack caught NON-OVERLAPPING classes AGAIN (AP-19, N keeps growing) — design-Critic: design-prose-vs-reality (B1/M1/M2); meta-Critic: fix-delta + missed coverage (M-add-1/M-add-2); code-Critic: execution-only AST-shape gap (M1) + stale-scaffolding (m1). The code-Critic's unique value is the AST-runtime axis the design+meta stack structurally cannot reach (AP-4).

## Lessons for next slice
- **A guard that checks "is X a constant/literal" must resolve one hop of NAME-INDIRECTION** (module-level name bound to a constant) — and the APED-1 battery must EXECUTE the name-bound variant, not just the literal. The design+meta stack reasons about "constant" abstractly; only code-execution finds the `ast.Name`-vs-`ast.Constant` gap. (AP-3/AP-4 reinforcement.)
- **An audit/guard docstring's advertised guarantee must match its implementation's ACTUAL coverage** — "constant base is flagged" that only flags literals is a contract gap. Narrow the claim OR close the gap; never ship the overstated version (code-review M1).
- **A "fail-loud / raises" claim must be scoped to where the production CALLER doesn't swallow it** — `write_slice_queue`'s raise is caught by Step 6.5's ADR-064 non-fatal wrapper; "loud" applies only to the un-wrapped non-regenerable provenance writer (M-add-1).
- **Budget a "near-vacuous defense-in-depth Minor" carefully** — the m1 "require expected_base present" check was nearly vacuous (Python enforces it); the real fix was the constant-resolution. A defense-in-depth guard's actual leverage must be checked against what the language already enforces.

## Vault updates made (thin vault)
- [[risk-register.md]] — R-32 slice-109 residual-closed paragraph (post-flip PCR conflict-resolution replacement WIRED; stays `mitigating`; physical move = sole remaining retirement precondition).
- [[shippability.md]] — row #115 (post-flip CAS write-safety; runs in the catalog, 114/114 PASS).
- [[decisions/ADR-098-post-flip-queue-cas-write-safety.md]] — new (cheap reversibility); m2 framing + B1 enforcement + M1 name-indirection closure.
- This slice's [[design.md]] — m1 wording corrected to the gap-closed name-resolution form (build-log notes the plan-mode + code-review deltas).
- [[drift-log.md]] — slice-109 DCE-1 marker (CLEAN).
