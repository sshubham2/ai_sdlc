# Critique Review: Slice 097 harden-skill-driven-vault-rewrites

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-06-01
**First-Critic verdict**: BLOCKED
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is strong and well-grounded — all three Blockers and three Majors are real and correctly severitized, and the Builder's fixes for B3/M1/M3/m1/m2 are sound. But two of the Builder's fix-deltas are themselves incomplete fresh claims: the B1 EOL-normalize contract has an unaddressed trailing-newline / final-byte edge, and the B2 op-class-aware audit prose does not actually specify a buildable discriminator — the bare `tools.vault_edit` token still flat-OR-cleans a rewrite site regardless of subcommand. Plus the first Critic missed the reflect:322 "classify at build" punt and a self-reference hazard on this slice's own `/reflect`.

## Confirmed findings (VALID + correct severity)

- **B1** (CAS byte-exact vs CRLF) — CONFIRMED, Blocker correct. Disk-grounded: `.gitattributes` scopes only `skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`; `architecture/**` untouched (slice-033/ADR-033 scope). Measured: `_index.md` 309783 B / 887 CRLF / **0 lone LF**; `risk-register.md` 137733 B / 588 CRLF / 0 lone LF; `archive/_index.md` 410611 B all CRLF. Byte-exact CAS vs an LF base → 100% false-conflict → livelock. Arithmetically certain, not speculative.
- **B2** (SVW-1 cannot distinguish rewrite- from append-routing) — CONFIRMED, Blocker correct. `skill_vault_write_safety_audit.py:121-123` (flat tuple) + `:126` (`_ROUTE_IN_CODESPAN_RE` matches any token) + `:255-274` (first-hit-wins). RMW site citing `vault_edit append` reads CLEAN today — control bypass of the must-not-defer item.
- **B3** (/archive Haiku-subagent CAS has no home) — CONFIRMED, Blocker correct. `archive/SKILL.md:58-67`: subagent returns content, main thread writes. Builder fix (main thread owns CAS) is the correct topology — see m-add-3 completeness gap.
- **M1** (proof must be spawn/subprocess+barrier) — CONFIRMED, Major correct. Sibling `test_skill_vault_write_safety_concurrency.py:22,54` is ThreadPoolExecutor + `:79` `sleep`-widened (GIL-masked). Gold standard `test_vault_write_safety_concurrency.py:88-89` (`mp.get_context("spawn")` + `ctx.Barrier`). Builder fix accepted.
- **M2** (base-capture unspecified) — CONFIRMED, Major correct. `vault_edit.py:69-72` `_read_content` universal-newlines → LF. Builder joint B1+M2 fix right direction — see m-add on snapshot atomicity.
- **M3** (risk-register.md EOL + whole-file trade-off) — CONFIRMED, Major correct; disk confirms CRLF. Trade-off recorded.
- **m1** (test-update omits enum-break sites) — CONFIRMED, Minor correct. `:313` `test_exempt_reasons_are_closed`, `:83` `test_exempted_site_is_clean`, `:299` `test_count_pin_trips...` all hard-break. Builder enumerated.
- **m2** (R-32 residual must name the 3 git-coupled tools) — CONFIRMED, Minor correct. Builder re-stated.

## Suspicious findings

**None.** Every first-Critic finding survives closer reading — zero false positives. Calibration-positive: the BLOCKED verdict was earned, not over-reach.

## Missed findings

- **B-add-1 [Blocker]: the B2 op-class-aware fix does not specify a buildable discriminator — the bare `tools.vault_edit` token still flat-OR-cleans a rewrite site.** Design §B2 (design.md:18) adds `"vault_edit rewrite"` to `_SAFE_ROUTE_TOKENS` and says a rewrite-class verb citing "ONLY an append-class token → VIOLATION." But `_SAFE_ROUTE_TOKENS` (`:121-123`) still contains the bare `"tools.vault_edit"`, and `_is_routed` (`:267-273`) returns True on the FIRST un-negated token hit. A rewrite-class line citing `` `tools.vault_edit append` `` matches the bare `tools.vault_edit` substring → CLEAN, before any op-class logic runs. The naive fix inherits the very flat-OR hole B2 is about. To close it the audit must (a) drop/down-rank the bare `tools.vault_edit` token so it cannot alone clean a site, (b) classify the CITED SUBCOMMAND (`vault_edit rewrite` vs `vault_edit append`), and (c) match it to the verb class — with an adversarial positive (`$PY -m tools.vault_edit append` on a regenerate verb → VIOLATION) proving the bare-token path is severed. Filed Blocker (not Major) because it is the load-bearing must-not-defer item; leaving the Builder's B2 fix as-is ships AC3 unmet.
- **M-add-1 [Major]: `_normalize_eol` trailing-newline / final-byte edge unspecified — can normalize a genuine lost-update into a false MATCH (silent overwrite) or a benign trailing-newline delta into a false CONFLICT (livelock).** Design §What's-new (design.md:16) defines only "`_normalize_eol(current)==_normalize_eol(expected_base)`, CRLF≡LF". If `_normalize_eol` strips a trailing newline, base="…row\n" vs current="…row" (a real concurrent truncation) compares EQUAL → CAS misses the lost-update and silently overwrites — violating AC1's "lose zero updates SILENTLY". Pin exactly what `_normalize_eol` touches (CRLF→LF ONLY; all other bytes incl. trailing newlines preserved) + unit-test both directions.
- **m-add-1 [Minor]: reflect:322 "append-or-regen, classify at build" is an unresolved fork carried into build, not a decision.** Low-risk (both channels safe) but it interacts with B-add-1 — if :322 is append-routed, the op-class-aware audit must NOT flag it (the append-class-verb-citing-append boundary). Decide at design or flag as the first mid-slice classification check.
- **m-add-2 [Minor]: self-reference hazard — this slice's own `/reflect` runs the just-edited `reflect/SKILL.md` RMW prose against the live 309KB CRLF `_index.md`, the FIRST production exercise of `vault_edit rewrite` CAS.** A bootstrap/self-host edge (slice-088/PFS-1 class). Treat the slice's own `/reflect` as a deliberate live-fire test; verify `_index.md` byte-integrity (no CRLF→LF churn) afterward.
- **m-add-3 [Minor]: B3 fix omits the re-dispatch cost + fail-STOP-after-exhaustion state.** Re-dispatching Haiku up to `_REWRITE_RETRY_MAX` times re-reads ~10-N folders each (archive:64-67); on exhaustion the user gets a fail-STOP mid-archive AFTER the Step-2 `mv` already moved the folder — confirm the state is recoverable (`/archive --index-only` re-runs the regen) and document.

## Severity adjustments

**None.** The first Critic's three Blockers, three Majors, two Minors are all correctly severitized. B-add-1 is filed Blocker (the only severity judgement on a missed finding) because the Builder's B2 fix does not close the load-bearing must-not-defer item.

## Notes

High confidence — grounded against the on-disk tools, the three SKILL.md (all still carrying live `deferred-rmw` markers → design.md is a plan, not-yet-built), the two concurrency tests, and byte-level EOL of all three targets. **Calibration observation**: the first Critic was framework-grade on the concerns it raised (B1/M2 CRLF cross-reference, M1 GIL-mask diagnosis) but exhibited the canonical "a Builder's own fix is a fresh claim" blind spot — it validated that B2 was REAL but accepted the Builder's "op-class-aware" fix prose at face value without checking it is lexically buildable given the existing flat-OR `_is_routed`. B-add-1 is the highest-value output of this second pass. One reservation: B-add-1 + M-add-1 are about UNSPECIFIED design detail, not demonstrably-wrong design — if the Builder has a concrete discriminator in mind that didn't reach design.md, they convert to "specify it + add the adversarial test" rather than "redesign." Either way they must be resolved before build, not deferred to "at build".
