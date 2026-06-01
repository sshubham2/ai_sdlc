# Reflection: Slice 097 harden-skill-driven-vault-rewrites

**Date**: 2026-06-01
**Shipped**: YES

Closed R-32's third and final write-safety sub-class — skill-driven read-modify-write — via compare-and-swap (`vault_edit rewrite`). With slice-094 (VWS-1, Python-writer) + slice-095 (SVW-1, skill-append) + this, the entire write/append/rewrite axis of R-32 is enforced on both the Python and skill paths. R-32 stays `mitigating`; the residual to retirement is now flip-mechanics only.

## Validated
- **CAS closes the RMW lost-update class on real CRLF files** — validated by the N=6 spawn+barrier concurrency proof (all markers land, 0 lost) AND a real-CLI end-to-end demo on a CRLF + UTF-8-em-dash file: `read --out-file` byte-exact, `rewrite` matched-base → all-CRLF result (no churn) + content landed, stale-base → exit 3 untouched.
- **EOL-normalized compare + EOL-preserving write** (B1) — a CRLF target + LF base does NOT false-conflict, and the write preserves CRLF (no 309KB churn). Validated by `test_rewrite_eol_preserving_crlf_via_cli` + the live demo.
- **Op-class-aware enforcement** (B2/B-add-1) — a rewrite-class verb routed via the unsafe `append` channel is a `channel-mismatch` VIOLATION; the bare `tools.vault_edit` token no longer flat-OR-cleans a rewrite site. Validated by the APED-1 battery (incl. the real `$PY -m tools.vault_edit append` corpus form).
- **MEPD-1 EXCLUDE** — no new tool module / RULE-ID / VERSION bump; MCFS-1/AVFS-1/TVFS-1 no-op (VERSION stays 0.80.0). Validated by the green forward-sync gates.

## Corrected
- **`_normalize_eol` must be CRLF→LF ONLY** (meta-Critic M-add-1) — an earlier mental model would have normalized trailing newlines too, which would silently mask a concurrent trailing-newline truncation. Corrected in the design + code: trailing/other bytes preserved → such a truncation is a genuine conflict. (Design contract, not a shipped bug.)
- **`reflect:322` verb reworded Regenerate→Append** (m-add-1) — the op-class audit would have flagged "Regenerate … archive/_index.md … via append" as a channel-mismatch; the operation is genuinely an append, so the prose verb was corrected to match the channel. (The audit FORCING prose-verb/channel agreement is the safety property working.)

## Discovered
- **PowerShell `>` redirection corrupts byte-exact data (UTF-16LE+BOM)** (code-Critic B1) — the documented `vault_edit read … > base.bin` capture would have produced a corrupt CAS base on the project's default shell → guaranteed livelock. The `read` *code* was byte-correct (`stdout.buffer`); the shell `>` the prose prescribed was the bug. Fixed with a `read --out-file` flag (Python writes raw bytes). **Strong BC-GLOBAL candidate** — this is a generic Windows footgun for any byte-exact CLI capture.
- **A verb in `_REWRITE_CLASS_VERBS` but not `_DIRECTIVE_VERBS` is silently undetected** (surfaced fixing M2) — the audit's mutation-site DETECTION lexicon and its op-CLASSIFICATION lexicon must stay consistent: "rewrite" was in the op-class set but not the detection set, so a site led by "Rewrite" was skipped entirely. Adding "rewrite" to `_DIRECTIVE_VERBS` closed it. The code-Critic's own M2 fix suggestion ("lead with Rewrite") was itself incomplete — it only works once the lexicon is consistent.
- **The self-host live-fire is real** (meta-Critic m-add-2) — this slice's own `/reflect` (running the just-installed routed prose) is the first production exercise of `vault_edit rewrite` on the real 309KB CRLF `_index.md` + 137KB `risk-register.md`. See "Vault updates made" — the dogfood succeeded byte-faithfully (CRLF preserved, 0 churn, both files).
- **D1 (live-fire DISCOVERY) — `reflect:322`'s `archive/_index.md` update is a newest-first PREPEND (RMW), mis-classified as an append** — the catalog is "most recent at top", so a new slice goes at the TOP (a read-modify-write insert), NOT an append-at-EOF (which `vault_edit append` does → the OLDEST position). Surfaced ONLY by actually performing the operation at the /reflect live-fire (the dogfood's payoff). Fixed in-slice: `reflect:322` now routes via `vault_edit rewrite` (read --out-file → insert-at-top → rewrite); the m-add-1 "reflect:322 = append" classification was wrong for this newest-first catalog. (Partly self-healing: a later `/archive` full-regen re-sorts newest-first — but the inline /reflect step was wrong.)

## Deferred
- **R-32 full retirement** → the flip slice — residual: route/retire the 3 git-coupled tools (`parallel_conflict_resolver` + `stranded_slice_audit` + `pulse_worktree_resolver`) + physical move of `architecture/` + git-untrack + prose rewrite. R-32 stays `mitigating`.
- **Lexical-ceiling residual** — an RMW phrased with an ambiguous verb (`update`/`write`) routed via `append` is NOT caught (only `regenerate`/`rewrite` are rewrite-class). Documented in code + the honest-scope note; not closed (chasing it buys false positives, per the slice-095 lesson).
- **CAS retry is a skill-prose bound, not a `vault_edit` constant** — `vault_edit rewrite` is single-attempt (can't re-apply an LLM edit internally); the bounded retry (~5) lives in skill prose. A future slice could add a structured set-field for the single-field risk-status flip (lighter than whole-file CAS) if churn proves costly.

## Critic calibration

3-Critic stack, **zero false-alarms across all three personas; non-overlapping defect classes** (the strongest evidence yet for not collapsing the stack):

**Design-Critic** (critique.md, all VALIDATED): B1 CRLF byte-exact-CAS (ACCEPTED-PENDING → confirmed real, the load-bearing catch), B2 op-class audit gap (ACCEPTED-PENDING), B3 Haiku-subagent CAS-home (ACCEPTED-FIXED), M1 spawn+barrier proof (ACCEPTED-FIXED), M2 base-capture (ACCEPTED-FIXED), M3 risk-register EOL (ACCEPTED-FIXED), m1 test-update list (ACCEPTED-FIXED), m2 R-32 residual (ACCEPTED-FIXED). Caught the CRLF environment mismatch the Builder's design hand-waved as "byte-faithfulness inherited."

**Meta-Critic** (critique-review.md, EXTEND, all VALIDATED): **B-add-1** (my B2 fix was an underspecified fresh claim — "op-class-aware" didn't sever the bare-`tools.vault_edit` flat-OR; the highest-value second-pass catch), M-add-1 (my B1 fix's `_normalize_eol` silent-overwrite edge), m-add-1 (reflect:322 classify), m-add-2 (self-host live-fire — happening now), m-add-3 (archive retry recovery state). The canonical "a Builder's own fix is a fresh claim" — the meta-Critic validated B2 was *real* AND that my *fix* didn't close it.

**code-Critic** (code-review.md, 2B/2M/2m, all VALIDATED + fixed in-slice): **B1** (PowerShell `>`/Out-File UTF-16LE+BOM corruption — a runtime-environment class NO design-level reviewer could reach; empirically proven), M1 (archive base-file reuse), **M2** (my reflect:56 reword dropped the site out of audit detection via a hyphen-compound verb — a fresh-claim-from-my-own-fix the code-Critic caught by executing `_is_mutation_site`), m1 (reflect:143 stale deferred-rmw prose), m2 (docstring). The test-gap note (the concurrency test never exercised the shell-redirect protocol) was the sharpest meta-observation.

**Missed by Critic**: the design+meta stack MISSED the PowerShell-`>`-shell-encoding mechanism (caught only by the code-Critic executing it in a real shell) — distinct from the design-Critic's B1 (which caught the *compare* CRLF mismatch but assumed the base capture was byte-exact). The "rewrite ∉ `_DIRECTIVE_VERBS`" lexicon-inconsistency was missed by ALL THREE (caught by the Builder while implementing the code-Critic's M2 fix suggestion, which was itself incomplete).

**Pattern**: "a Builder's own fix is a fresh claim" fired N+2 in ONE slice — the meta-Critic caught it on my B1+B2 fixes (B-add-1, M-add-1), the code-Critic caught it on my reflect:56 reword (M2), and the Builder caught the code-Critic's *own* fix-suggestion being incomplete (rewrite-verb-lexicon). The fix-delta is a recursively-fresh claim at EVERY layer. Strong `/critic-calibrate` signal: a code-Critic Dim-probe "does the audit's DETECTION lexicon cover every verb in its CLASSIFICATION lexicon?" + "is any byte-exact capture done via shell redirection (PowerShell `>` corrupts)?"

## Lessons for next slice
- **Shell redirection `>` is NOT byte-safe on the default shell (PowerShell → UTF-16LE+BOM)** — any byte-exact CLI data capture must use a tool `--out-file` flag (Python writes the bytes) or a binary subprocess pipe, NEVER `> file`. The `read` code was correct; the *prose protocol* was the bug, and the test masked it by capturing in-process. **Promote to BC-GLOBAL.**
- **A test that drives a CLI must exercise the DOCUMENTED capture path, not a convenient in-process proxy** — the concurrency proof captured the base via `read_bytes()` so the shell-redirect protocol it documents was never run; the code-Critic's empirical PowerShell probe found what the green test hid. Extends APED-1: execute the documented end-to-end protocol, on the real shell, not just the mechanism.
- **A lexical audit's DETECTION verb-set and its CLASSIFICATION verb-set must be a consistent pair** — a verb in one but not the other silently drops or mis-classifies a site. Pin the intersection invariant.
- **The 3-Critic stack earns its cost most when correcting the Builder's own fixes** — every layer caught a fresh claim introduced by the prior layer's fix. Do NOT collapse the stack on write-safety/audit slices.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-32 narrowed: skill-driven RMW sub-class CLOSED (slice-097 / [[ADR-088]]); residual re-stated as the 3 git-coupled tools + flip mechanics; status stays `mitigating`. **Applied via `vault_edit rewrite` (the dogfood live-fire on the real 137KB CRLF file).**
- [[decisions/ADR-088]] — recorded the CAS mechanism + EOL contract + op-class enforcement (written at /design-slice; finalized through critique).
- [[lessons-learned.md]] — slice-097 entry appended (via `vault_edit append`).
- [[shippability.md]] — row #105 appended (via `vault_edit append`).
- `architecture/slices/_index.md` — recent-10 + Aggregated-lessons regenerated for slice-097 (087 dropped); `archive/_index.md` — 097 prepended at top. **Both applied via `vault_edit rewrite` (dogfood live-fire #2 on the real 309KB CRLF `_index.md`; archive prepend corrected from append per D1).**
- `~/.claude/build-checks.md` + `tests/methodology/fixtures/build_checks/canonical_global_checks.md` + `test_build_checks_audit.py` — **BC-GLOBAL-6 promoted** (byte-exact CLI capture must use a tool flag / binary pipe, never shell `>` — PowerShell `>` = UTF-16LE+BOM); BCI-1 PASS (live ≡ fixture).
- This slice's [[design.md]] — carries the /critique + /critique-review fix-deltas (B1–m2, B-add-1–m-add-3); the /code-review fixes (B1/M1/M2/m1/m2) are in build-log + code-review.md.
