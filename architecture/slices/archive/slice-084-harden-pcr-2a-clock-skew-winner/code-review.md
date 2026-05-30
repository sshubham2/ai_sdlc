# Code Review: Slice 084 harden-pcr-2a-clock-skew-winner

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-30
**Result**: FINDINGS (2 Majors + 3 Minors — all ADDRESSED-IN-SLICE)

## Summary
The code is structurally sound, fail-closed by design, and the APED-1 battery runs clean for the
canonical corpus. Executing the parse/compare logic against an *adversarial* timestamp corpus
surfaced two real defects the design-stage stack could not reach — a lowercase-`z` past-claim
false-positive STOP (M1) and a docstring over-claim about cross-version `fromisoformat` uniformity
(M2) — plus a dead param, a doc line-drift, and corpus gaps. v1 is advisory, but all five were cheap,
in this slice's own just-written surface, and the slice is still uncommitted — so all were fixed
in-slice rather than routed to a bundle. Full suite 1217 PASS post-fix (+4 corpus rows).

## Changed files (in-scope)
tools/parallel_conflict_resolver.py
tests/methodology/test_pcr_2a_clock_skew_winner.py
architecture/slices/slice-084-harden-pcr-2a-clock-skew-winner/build-log.md

## Findings

### Majors

#### M1: Lowercase-`z` UTC designator false-positive STOPs a legitimately-past winner
- **Claim under review**: `tools/parallel_conflict_resolver.py` — `if raw.endswith("Z"): raw = raw[:-1] + "+00:00"`
- **Issue**: The `Z`→`+00:00` normalization was case-sensitive. RFC-3339 §5.6 permits a lowercase `z`. A past `...T08:00:00z` is a valid past UTC stamp that SHOULD resolve (`None`), but fell through unnormalized → `fromisoformat` `ValueError` (all 3.10–3.13) → fail-closed STOP. False-positive on AC-4's "plausible still resolves" / AC-3 no-over-trigger (safe direction — fail-closed, no crash, escalates to PCR-2b — hence Major not Blocker).
- **Evidence**: live exec — `'…08:00:00z' → SUSPECT` (wrong); uppercase `Z` correctly `None`. Test corpus only had uppercase `Z`.
- **Disposition**: **ADDRESSED-IN-SLICE** — normalization now `if raw[-1:] in ("Z", "z")`; comment cites RFC-3339 §5.6 case-insensitivity; APED-1 row `("2026-05-29T08:00:00z", False)` added (+ lowercase-z-future `True`). Re-run: resolves correctly.

#### M2: `fromisoformat` parse-acceptance diverges across the 3.10 floor — docstring over-claimed "version-independent"
- **Claim under review**: `_winner_clock_skew_suspect` `# B2:` comment claiming the normalization makes the gate "version-independent"; `parsed = datetime.datetime.fromisoformat(raw)` on a `>=3.10` floor.
- **Issue**: `fromisoformat` relaxed in 3.11 (cpython#115783 / bpo-86537): offset-without-colon (`+0000`) + space-separated stamps parse on 3.11+ but `ValueError` on 3.10. The "version-independent" claim was only true for the `Z` token, not the broader acceptance surface — a docstring over-claim (Dim 1) atop a real version-conformance gap (Dim 9). Behavior on those forms is fail-closed STOP on 3.10 vs parse-on-merits on 3.11+ (safe direction either way; PSQ-2's canonical writer emits `+00:00` which parses identically on all >=3.10).
- **Evidence**: web-confirmed cpython#115783 / bpo-86537; build-log smoke ran on 3.13 only.
- **Disposition**: **ADDRESSED-IN-SLICE** (fix option (a)) — comment scoped to the `Z`/`z` token only + explicitly documents that pre-3.11 interpreters fail-closed on relaxed forms (the safe direction); no behavior change. APED-1 rows for offset-no-colon + space-separated (both stable `True`: future→suspicious on 3.11+, fail-closed on 3.10) added.

### Minors

#### m1: `_append_skew_stop_audit` carried a dead `diag` parameter (Fowler speculative-generality)
- **Issue**: `diag: ConflictDiagnostic` was never referenced in the body (carried over from mirroring `_append_equivalence_stop_audit`). Caller + test passed it pointlessly.
- **Disposition**: **ADDRESSED-IN-SLICE** — `diag` dropped from the signature, the call site, and the test call.

#### m2: build-log line-citation drift for the comment touch-up
- **Issue**: build-log cited the one-line comment change at `L1031` (×2) and `L1154` (×1) — inconsistent.
- **Disposition**: **ADDRESSED-IN-SLICE** — all three citations reconciled to a line-number-free symbol reference (`_format_vault_claim_audit_entry` docstring), robust to line drift.

#### m3: APED-1 corpus omitted the two classes that actually break
- **Issue**: the battery omitted lowercase-`z`-past (M1) and offset-no-colon / space-separated (M2) — under-covering the failure surface it claims to cover.
- **Disposition**: **ADDRESSED-IN-SLICE** — 4 rows added (lowercase-z past=False / future=True; offset-no-colon=True; space-separated=True). Battery now 13 rows; suite 24 items PASS.

## Dimensions checked
- [x] Unfounded assumptions — M2 (docstring "version-independent" over-claim) — fixed.
- [x] Missing edge cases — M1 (lowercase `z`), m3 (corpus gaps) — fixed. Microsecond-precision (`now` second vs claimed_at microsecond) verified safe by execution; non-UTC-offset stamps correctly normalized by aware comparison; no false-negative on a genuinely-future stamp found.
- [x] Over-engineering — m1 (dead `diag` param) — fixed.
- [x] Under-engineering — none. All four ACs have delivering code; `now`-default interaction with the two dispatch sites verified correct (real-now default; 2026 fixture stamps are past → guard returns `None` → no behavior change; 95-test PCR regression confirms).
- [x] Contract gaps — none. Both helpers fully type-annotated + docstringed; all test imports resolve; the best-effort `except Exception` audit swallow is justified (non-blocking forensic side-effect, mirrors `_append_equivalence_stop_audit`, logs to stderr, STOP returns regardless).
- [x] Security — none. Cooperative threat model (explicitly NOT a security boundary); no new input boundary; `subprocess.run` list-form (no `shell=True`); no secrets.
- [x] Drift from vault — none material. Code matches design.md (Step 2.5 placement, `_select_timestamp_winner` unchanged, `conflict_class` stays VAULT_CLAIM on skew-STOP, no skill edit). ADR-076 mints no RULE-ID → no MEPD-1 bump → consistent with no VERSION bump.
- [x] Web-known issues — M2 confirmed via cpython#115783 + bpo-86537 (`fromisoformat` relaxed in 3.11) — addressed.
- [x] Cross-cutting conformance — M2 (Python 3.10 vs 3.11+ `fromisoformat`) — addressed. APED-1 applied by execution (17-row adversarial corpus) — that execution surfaced M1 + M2. EOL-DRIFT-1 / RSAD-1 N/A.

Sources:
- cpython#115783 — datetime.fromisoformat() accepts invalid ISO 8601 timestamps
- cpython#86537 / bpo-42371 — omitted colon in timezone suffix raises ValueError (pre-3.11)
