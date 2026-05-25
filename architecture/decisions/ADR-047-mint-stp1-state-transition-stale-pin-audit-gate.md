---
id: ADR-047
title: Mint STP-1 as a NON-`-D` audit-gate rule scoped to two mechanically-detectable stale-pin sub-forms; defer the ADR-supersession sub-form
date: 2026-05-18
slice: slice-044-add-state-transition-stale-pin-audit
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-047: STP-1 — state-transition stale-pin audit gate (two-sub-form scope)

## Context

A single methodology-discipline gap has recurred N≥3: a slice performs a *state transition* — a risk's `**Status**:` flip, an ADR `accepted`→`superseded`, or a `SKILL.md` prose anchor repointed away — but a pre-existing test still asserts the OLD value and is not realigned in the same fix block. The dual-Critic stack structurally cannot reach this audit-vs-artifact interaction; it is caught only at the pre-finish full-suite (BC-PROJ-4) run, sometimes latent for multiple slices:

- **R-10** (slice-038→040): slice-038 SRSC-1 repointed `/validate-slice` Step 5.5 prose, leaving `test_step4_5_5_consumes_machine_stable_command` asserting a since-removed anchor — FAILing slice-innocently on master for ~5 slices until slice-039's BC-PROJ-4 run surfaced it.
- **slice-041**: the R-4 `mitigating`→`retired` flip FAILed a pre-existing `test_r_4_..._stays_mitigating`; neither the design nor 3 Critic revisions / 3 DR-1 passes enumerated it — only the pre-finish full-suite run caught it.
- **slice-042**: the same class recurred at ADR-prose level (N+1).

slice-041 *and* slice-042 reflections each explicitly nominate this as a "Candidate Builder-plan-mode checklist item." This repo's own demonstrated law (slice-038 SRSC-1: *"prose binds nothing executable; the invoked single-sourced runner does"*) says the durable fix is an **executable gate**, not a prose checklist.

## Options considered

1. **Prose plan-mode checklist in `/build-slice` SKILL.md** — cheap, but binds nothing executable; the exact failure mode (Critic + Builder both miss the stale pin) is a human-discipline gap a prose checklist does not close. Rejected as the primary control (slice-038 law; the #2 `/slice` candidate, folded in only where mechanizable).
2. **One audit covering all three sub-forms (risk-status, ADR-supersession, SKILL.md-prose)** — the ADR `accepted`→`superseded` sub-form has no canonical machine-readable signal linking a test to "the superseded ADR's prior claim"; a heuristic would be high-false-positive and would relocate the flaw (slice-041 non-convergence pattern). Rejected: over-broad scope.
3. **One audit, two mechanically-detectable sub-forms; defer the fuzzy third** — Sub-form A (SKILL.md-prose-repoint) is a *git-diff-independent standing invariant* (every prose-pin's asserted literal must exist in its target SKILL.md) that would have caught R-10 the instant slice-038 shipped; Sub-form B (risk-status-stale) ~~was originally specified as *git-diff-dependent* (compare register at merge-base vs working tree)~~ — **revised to a git-diff-independent standing invariant by the 2026-05-18 /build-slice plan-mode deviation; see "Deviation: Sub-form B git-independence" below and the Decision section (the merge-base form was inapplicable: `architecture/` is gitignored)**. Both are low-false-positive and surgical. **Chosen.**
4. **Refine an existing `-D` discipline rule in place** — STP-1 is a new *audit-enforced gate* with its own programmatic tool + Step 6 wiring, not a refinement of an existing rule's parse logic. The `-D`-vs-`vN.N` convention (ADR-038, PTFFD-1↔PTFCD-1 precedent; the audit-gate naming-class is BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1) reserves `vN.N` NON-`-D` IDs for exactly this class. Rejected the `-D` framing.

## Decision

Mint **STP-1** as a NEW NON-`-D` `vN.N` audit-enforced gate (naming-class peer of BRANCH-1 / BC-1 / PMI-1 / UTF8-STDOUT-1 / CRP-1 / PCA-1 / BCI-1 / MCFS-1; supersedes nothing). Its programmatic gate is `tools/state_transition_pin_audit.py`, wired non-opt-out at `/build-slice` Step 6 pre-finish. Scope is exactly two sub-forms:

- **Sub-form A — SKILL.md-prose-repoint stale pin** (git-diff-independent standing invariant): for every `tests/**/test_*skill*.py` prose-pin asserting a constant string literal via `in` membership against a `read_file("skills/<x>/SKILL.md")`-bound name, the literal MUST be present in the current target SKILL.md.
- **Sub-form B — risk-status-stale pin** (git-diff-INDEPENDENT standing invariant; **revised 2026-05-18 by a /build-slice plan-mode design-wrong deviation** — see "Deviation: Sub-form B git-independence" below): a test whose `FunctionDef` name matches the anchored detector `(?:^|_)r[_-]?(\d+).*?_(stays|remains|is)_(open|mitigating|retired|accepted)(?:_|$)` claims `R-<num>` is at the named status; if the **live** `architecture/risk-register.md` `**Status**:` for that risk ≠ the claimed status ⇒ stale. The `(?:^|_)` anchor stops an embedded `r` false-binding a risk-number (targeted-critique M1); the explicit status alternation + `(?:_|$)` boundary catches suffixed names without a greedy-`\w+` false-negative (targeted-critique M2). Parses the live register via the reused `risk_register_audit._parse_risks`. No git, no merge-base, no changed-file set. **Per-scanned-file AST `SyntaxError` is skip-with-visible-note, NOT exit-2** — STP-1 (both sub-forms) inherits the ADR-037/PTFFD-1 parse-failure discipline of the `shippability_path_audit.py`/`_pyfn` precedent it reuses; this does NOT contradict or supersede ADR-037 (targeted-critique B1/B2). Exit-2 fail-closed is reserved for hard-input failure (register unparseable/missing, `tests/`/`skills/` dir missing, repo-root unresolvable). (The literal-detection leg is out of scope for v1 — false-positive-prone, no witnessed non-fn-name instance.)

The ADR `accepted`→`superseded` sub-form is **explicitly out of scope** for STP-1 v1 (no canonical machine-readable test↔superseded-claim signal; deferring avoids a high-false-positive heuristic). It is recorded as a `/reflect` Discovered follow-up candidate, not a silent omission.

STP-1 fails closed: any register-parse / file-read / AST failure is an attributed `usage-error` (exit 2), never a silent exit 0 (the R-7 / TFFL-1 silent-default-off anti-pattern is forbidden by construction).

### Deviation: Sub-form B git-independence (2026-05-18, /build-slice plan-mode design-wrong gate)

The original Sub-form B (git-merge-base baseline diff of `architecture/risk-register.md` + `git diff --name-only` changed-file set) was discovered **inapplicable in this repo** at /build-slice plan-mode: `architecture/` is fully gitignored (`.gitignore:11`), so `git show <base>:architecture/risk-register.md` is `fatal` and `git diff` never surfaces the vault — STP-1 could not self-apply (RSAD-1). The dual-Critic stack (first-Critic M1 + DR-1) probed git semantics but both missed the gitignore root cause; caught only at build-plan-mode (the slice-032/036/037 "build-plan-mode is the backstop the dual-Critic stack structurally cannot reach" pattern — the exact miss-class STP-1 itself systematizes). User-approved deviation ("deviate now + targeted re-critique", build-log.md 2026-05-18 00:02). Sub-form B is re-specified as a **git-diff-independent standing invariant** vs the **live** register (above). Net effect: strictly removes attack surface — moots first-Critic **M1** entirely (no git-diff semantics remain) and **dissolves introduced-residual #2** (no git-base failure mode exists ⇒ no misconfigured-clone universal-HALT); the whole audit is now git-free. The CSP-1 object-identity-reuse discipline M2 advocated is preserved on `_parse_risks`. A targeted `/critique` on this revised Sub-form B mechanism gates the build resumption.

## Consequences

- New `tools/state_transition_pin_audit.py` (+ INST-1 / PMI-1 tool-list lockstep, 4-part atomic version bump, rule-ID-bearing changelog entry-pin).
- `skills/build-slice/SKILL.md` gains a Step 6 checklist item + `#### State-transition stale-pin audit (STP-1)` sub-section + a slice-044 bootstrap note (the authoring slice self-discharges by running STP-1 against the repo at its own Step 6, MUST exit 0). Forward-synced installed copy; skill-drift EOL-agnostic-equal (EOL-DRIFT-1).
- Object-identity reuse of `risk_register_audit._parse_risks` makes Sub-form B's register parse single-sourced (CSP-1; slice-038 `consumer._fn is source._fn` lesson applied).
- The recurring false-PCA-1-HALT / N-slice-latency stale-pin class is structurally closed for the two highest-recurrence sub-forms; the ADR-supersession residual remains an open discovered candidate.
- Future widening to the ADR-supersession sub-form, or to plan-mode-stage invocation, is an additive change to the same tool — no contract break.

### Introduced residuals (critique m2 — new failure surfaces this gate creates)

An ADR that introduces a new gate must enumerate the failure surfaces it *creates*, not only the one it closes:

1. **`not in`/negative-pin false-positive risk (critique B1) — and its over-correction (DR-1 B-add-1)** — a naive "asserted literal absent ⇒ violation" scan would fire on every deliberately-absent `not in` pin (witnessed live: `test_commit_slice_skill_merge_flag.py:38,57`); but the inverse over-correction — excluding *all* `BoolOp`-nested membership — blinds Sub-form A to ~45 of ~140 positive pins, the dominant conjoined-positive R-10-class idiom of this repo (e.g. `test_build_slice_skill.py:187-190`). **Mitigation (in design):** a node is excluded ONLY if its own op is `ast.NotIn`, OR it is a `BoolOp` operand whose *sibling* operands include a `NotIn`/non-constant; positive-only `and`/`or` chains are evaluated per-operand. Verification proves both a `not in` pin → exit 0 AND a positive `BoolOp` pin with one literal absent → exit 1; the full `BoolOp`-pin set is machine-classified at build, not assumed.
2. ~~**Misconfigured-clone default-branch universal-HALT (critique M2)**~~ — **DISSOLVED by the 2026-05-18 Sub-form B git-independence deviation**: STP-1 now makes no git invocation, so there is no default-branch-resolution failure mode and no misconfigured-clone universal-HALT residual. (Recorded for traceability — m2's "enumerate the failure surfaces the gate creates" discipline is satisfied by noting this residual was designed out, not merely mitigated.) M2's CSP-1 object-identity-reuse discipline is preserved on `_parse_risks`.

Both residuals are bounded by design elements + verification cases in this same slice; neither is deferred.

## Reversibility

**cheap**. STP-1 is an additive read-only audit with no persistent state and no runtime/data surface. The detection mechanisms (AST literal/binding scan, live-register parse via the reused `_parse_risks`) are self-contained and tunable; widening, narrowing, or removing a sub-form is a localized edit to one `tools/*.py` module + its Step 6 wiring + tests, comparable to the TFFL-1 / PTFFD-1 / BRANCH-1-R-6 precedent edits. No consumer outside `/build-slice` Step 6 depends on its contract.
