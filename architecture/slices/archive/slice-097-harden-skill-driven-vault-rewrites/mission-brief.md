# Slice 097: harden-skill-driven-vault-rewrites

**Mode**: Standard
**Estimated work**: 1 day (MEDIUM-LARGE — the lock-spans-an-LLM-read-modify-write design is the novel part)
**Risk retired**: R-32 (medium — the load-bearing external-vault flip gate; this closes its last write-safety sub-class)
**Test-first**: false
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

slice-094 (VWS-1, Python-writer) and slice-095 (SVW-1, skill-driven *append*) closed two of R-32's three write-safety sub-classes; both have merged. The third — **skill-driven read-modify-write (RMW)** — was deliberately deferred: `vault_edit` ships `append` only because `safe_append_text`/`safe_write_text` are torn-write-safe but **not lost-update-safe** for a read-modify-write, and "the lock cannot span an LLM read+edit+write" (see `tools/vault_edit.py` docstring). This slice closes that residual: it gives the `_index.md` recent-10/Active/Aggregated-lessons regenerations (`/reflect`, `/archive`, `/supersede-slice`) and in-place risk-register status edits a concurrency-safe rewrite path, and flips the SVW-1 audit from *deferring* the RMW class to *enforcing* it. This is the third and final write-safety precondition for the flip (R-32 retires at the flip's physical move; this slice narrows it to that residual alone).

## Acceptance criteria

1. A concurrency-safe **rewrite** channel exists for skill-driven vault RMW writes (the channel slice-095 deliberately deferred), using **compare-and-swap**: under the sidecar lock the tool re-reads the target and writes only if it still matches the base the skill read (**EOL-normalized compare**, **EOL-preserving write** — the CRLF `_index.md`/`risk-register.md` must not false-conflict or churn), else fail-closed exit-3 → skill re-reads + retries. Concurrent worktree rewrites of a shared-aggregate vault file (`_index.md` / in-place risk-register status) lose **zero** updates **silently** — every update either commits or triggers a loud retry, never a silent overwrite.
2. Every `deferred-rmw`-class skill mutation site (`/reflect`, `/archive`, `/supersede-slice` — `_index.md` recent-10/Active/lessons regeneration + in-place risk-register status edits) routes through the new channel; the `deferred-rmw` standing exemption is **removed**, not re-marked.
3. `tools/skill_vault_write_safety_audit.py` (SVW-1) fail-closed-flags an un-routed RMW site AND, **op-class-aware**, flags an RMW site that mis-routes via the lost-update-UNSAFE `append` channel (a negative test proves both, with a documented lexical-ceiling residual); the `project-open-single-shot` sites (`/discover`, `/risk-spike`, `/triage`) **stay exempt** — explicitly out of scope, different class.
4. A **non-vacuous** concurrency proof: N concurrent safe-rewrites on `_index.md` lose zero updates while the naive RMW control loses ≥1 (proven by mutation, per the slice-092/094/095 discipline).
5. R-32 is **narrowed** in the register (skill-driven RMW sub-class closed; only the flip's physical move/untrack/prose residual remains); the full methodology suite + all Step-6 gates are green; OSDG-1 drift tests pass for the three edited SKILL.md files.

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Safe rewrite channel | NEW `tests/methodology/test_skill_vault_rewrite_concurrency.py` (subprocess `vault_edit rewrite` workers + shared barrier, CRLF fixture): N concurrent safe-rewrites → final file contains all N updates, zero lost |
| 2 | Sites routed + exemption removed | `grep` the three SKILL.md files: no `vault-write-safe: deferred-rmw` marker remains; each RMW step cites the safe-rewrite channel; `$PY -m tools.skill_vault_write_safety_audit` → CLEAN |
| 3 | Audit enforces, not defers | Negative test: strip the route token from one RMW site → audit reports a fail-closed VIOLATION (exit non-zero). Positive: `project-open-single-shot` sites still pass |
| 4 | Non-vacuous proof | Run the concurrency test with the lock (0 lost) AND with the lock stripped by mutation (≥1 lost); both asserted |
| 5 | R-32 narrowed + gates green | `$PY -m tools.risk_register_audit architecture/risk-register.md`; `/validate-slice` (VAL-1 + WS-1 + ETC-1 + shippability); the three `test_*_skill_drift.py` pass |

## Must-not-defer

- [ ] The lock MUST genuinely span the read→transform→write — NOT a per-call append masquerading as a rewrite (the exact false-confidence trap `tools/vault_edit.py` calls out; a `rewrite` that just truncates+writes without holding the lock across the read is the failure mode).
- [ ] Byte-faithfulness: LF preserved, no CRLF corruption (EOL-DRIFT-1 / ADR-033 — the slice-094 `newline=""` + `O_BINARY` lesson; a whole-file rewrite is the highest-risk surface for this).
- [ ] Fail-VISIBLE on write/lock failure (R-7 — non-zero + loud, never a silent no-op or partial write).
- [ ] SVW-1 audit is fail-CLOSED for the RMW class (an un-routed RMW site is un-mergeable), not advisory.
- [ ] cp1252-safe stdout/stderr on any new print path (`_stdout.reconfigure_stdout_utf8()` — the recurring N≥8 class; never bare `print()`).

## Out of scope

- `project-open-single-shot` writes (`/discover`, `/risk-spike`, `/triage` initial risk-register writes) — a single-shot project-lifecycle class, not a parallel-RMW hazard; stays `<!-- vault-write-safe: project-open-single-shot -->` exempt.
- The flip itself (physical move of `architecture/` to the external store, git-untrack, prose rewrite) — R-32 *retires* there, not here.
- Routing/retiring the three git-coupled tools (`parallel_conflict_resolver`, `stranded_slice_audit`, `pulse_worktree_resolver`) — folded into the flip's design (their redesign depends on the untracked-vault target).
- Python-writer RMW (already covered by VWS-1 / slice-094) and skill-driven append (already covered by SVW-1 / slice-095).

## Dependencies

- Prior slices: [[slice-095-harden-skill-driven-vault-writes]] — direct predecessor; this slice exposes the `rewrite` it deferred. [[slice-094-harden-vault-write-safety]] — byte-faithfulness + audit pattern. [[slice-093-add-external-vault-support]] — `_vault_write` primitives.
- Vault refs: [[risk-register#R-32]]; [[decisions/ADR-087]] (SVW-1), [[decisions/ADR-086]] (VWS-1), [[decisions/ADR-085]] (`_vault_write`), [[decisions/ADR-066]] (vault git-tracked pre-flip).
- Tools: `tools/vault_edit.py`, `tools/_vault_write.py`, `tools/skill_vault_write_safety_audit.py`, `tools/_vault_paths.py`.
- A new ADR (next free number) will record the safe-rewrite mechanism + the `deferred-rmw`→enforced transition.

## Mid-slice smoke gate

At ~50% of build (rewrite channel built + ONE site routed, e.g. `/reflect`'s `_index.md` regeneration):
```
$PY -m tools.skill_vault_write_safety_audit
$PY -m pytest tests/methodology/test_skill_vault_rewrite_concurrency.py -q
```
Expected: audit CLEAN for the routed site; the concurrency proof (subprocess + barrier, run against a **CRLF** fixture) loses **zero** updates with CAS and **≥1** with the CAS base-check stripped (mutation). If the proof shows loss even WITH CAS, OR the CAS false-conflicts on the CRLF fixture (livelock → STOP) → STOP: the EOL contract or the base-capture is wrong, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
