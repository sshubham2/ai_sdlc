# Design: Slice 083 add-pcr-2b-hard-class-conflict-resolution

**Date**: 2026-05-29
**Mode**: Standard

## What's new

- **PCR-2b** rule (methodology-changelog v0.77.0; [[ADR-075]]) — the HARD + MIXED resolution sub-mechanism on the parallel-conflict-resolution (PCR-N) family axis, sibling to PCR-1 / PCR-2a. Replaces the bare STOP that HARD/MIXED conflicts currently get at `/commit-slice --merge` sub-step 2.5 with a **gate-on-hand-resolve** flow.
- **TRI-RESOLVE-1** rule (same changelog entry; [[ADR-075]]) — a user-owned triage gate for a proposed HARD/MIXED merge resolution, mirroring [[skills/critique]]'s TRI-1 (Step 4.5) structure. Structured-options (SOAD-1), fail-closed.
- `resolve_hard_conflict(diag, repo_root=None) -> ResolutionResult` in `tools/parallel_conflict_resolver.py` — thin public dispatch target for HARD/MIXED, returning an enriched `action="STOP"` carrying the gate metadata (mirrors the `resolve_vault_claim_conflict` dispatch shape at `tools/parallel_conflict_resolver.py:250`). HARD/MIXED route through it from `resolve_soft_conflict`.
- Two new CLI modes on the resolver (the only new machine surface the skill drives):
  - `--verify-resolution` — structural pre-Critic preflight (see B2/M1/M-add-1 fixes below): the resolution is verified-clean iff **(a)** no path remains unmerged (`git diff --name-only --diff-filter=U` returns empty) **and (b)** no **line-anchored conflict-marker opener/closer** (`^<{7}` or `^>{7}`, optionally `+space/label`) survives in the staged diff (`git diff --cached`). Returns STOP (`reason=paths-still-unmerged` or `reason=unresolved-markers-present`) otherwise. Add-state-aware (runs AFTER the user `git add`s their resolution). **NOT `git diff --cached --check`** and **NOT a `=======` scan** — both inherit git's ≥7-`=` heuristic that false-STOPs on Markdown setext headings (M-add-1).
  - `--record-hard-resolution` — appends the `## Hard-conflict resolution - <ISO-8601 UTC>` audit section after a ratified apply; carries the Critic verdict + TRI-RESOLVE-1 disposition.
- `_format_hard_audit_entry(...)` — builds the HARD audit section (mirrors `_format_vault_claim_audit_entry` at `tools/parallel_conflict_resolver.py:973`; **uniform hyphen-space** separator `## Hard-conflict resolution - `, section-type distinguished by the prefix word `Hard-conflict`, per PCR-2a ADR-071 discipline).
- `skills/commit-slice/SKILL.md` sub-step 2.5 — a new HARD/MIXED branch in the `action: STOP` handling (L188 region) that drives: structural preflight → `code-review` agent on the resolved diff (single pass) → TRI-RESOLVE-1 → continue-or-STOP.
- New test modules under `tests/methodology/` (APED-1 battery + skill-prose pins + changelog pin).
- `architecture/shippability.md` — one new row (per RPCD-1 / SCPD-1 consumer-propagation).

## What's reused

- `tools/parallel_conflict_resolver.py` — `classify_conflict` (`:186`) already returns `HARD` / `MIXED`; `resolve_soft_conflict` (`:222`) is the dispatch branch point (the VAULT_CLAIM dispatch at `:250` is the template); `_append_audit_log` (`:1498`), `ResolutionResult` (`:129`), `ConflictDiagnostic` (`:120`), `_git_show_stage`, `_extract_u_files` all reused.
- `_format_vault_claim_audit_entry` (`:973`) — structural template for `_format_hard_audit_entry`.
- `skills/critique/SKILL.md` Step 4.5 (TRI-1) — structural template for TRI-RESOLVE-1.
- **`code-review` agent** (`agents/code-review.md`, slice-060 / [[decisions/ADR-059]]) — the reused adversarial mechanism: it is already diff-calibrated and reviews the resolved merge diff (per the B1 + M-add-2 fix below). NOT the `/critique` skills (hardwired to a slice `design.md`) and NOT the named `critique`/`critique-review` subagents (which fail-stop on missing slice artifacts — M-add-2). [[ADR-075]] records the concrete invocation.
- [[decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen]] — 5-class taxonomy + HARD/MIXED rows + fail-closed contract + audit-log shape.
- [[decisions/ADR-071-mint-pcr-2a-vault-claim-resolver]] — decoupled-class-implementations precedent + uniform-hyphen-space audit separator.
- [[decisions/ADR-067-mint-psq-2-claim-machinery]] — cooperative-not-adversarial threat model (carried forward).
- `tools/_stdout.py` — `reconfigure_stdout_utf8` (UTF8-STDOUT-1 conformance for the new CLI modes).
- PMI-1 / OSDG-1 / MCFS-1 / AVFS-1 / TVFS-1 / PVFS-1 forward-sync discipline (5-part atomic bump pattern, identical to slice-081's v0.76.0).

## Components touched

### `tools/parallel_conflict_resolver.py` (modified)
- **Responsibility**: classify + resolve parallel-slice rebase conflicts. PCR-2b adds the HARD/MIXED gate-support surface (the Critic + user orchestration itself lives in SKILL.md prose — Python cannot spawn skill agents).
- **Lives at**: `tools/parallel_conflict_resolver.py` (modified).
- **Key interactions**: called by `skills/commit-slice/SKILL.md` sub-step 2.5 via CLI (`--resolve-soft`, new `--verify-resolution`, new `--record-hard-resolution`); reads git rebase state via `subprocess`; appends to `architecture/parallel-conflict-resolution-log.md`.
- **New surface**: `resolve_hard_conflict`; `_format_hard_audit_entry`; `_verify_resolution_clean` (private — checks `git diff --name-only --diff-filter=U` empty + no line-anchored `^<{7}`/`^>{7}` opener/closer in `git diff --cached`, per the M-add-1 fix; NOT `git diff --cached --check`, NOT a `=======` scan); CLI modes `--verify-resolution` + `--record-hard-resolution`; `_append_audit_log` dispatch leg for HARD; `main()` mode handlers + `ResolutionResult` reused (HARD carries `action="STOP"` until the skill ratifies & continues — the resolver never runs `git rebase --continue` for HARD).

### `skills/commit-slice/SKILL.md` (modified)
- **Responsibility**: orchestrate the merge sequence. PCR-2b enhances sub-step 2.5's STOP handling with the HARD/MIXED gate flow.
- **Lives at**: `skills/commit-slice/SKILL.md` (modified) — OSDG-1 / mini-CAD guarded; installed copy forward-synced.
- **Key interactions**: spawns the `code-review` agent (single pass, on the resolved diff per B1 + M-add-2 fix); presents the TRI-RESOLVE-1 structured-options ask; invokes the resolver CLI modes.
- **m2 fix — update the stale forward-ref**: the existing L185-192 prose says "**PCR-2b (slice-079) will ship resolution paths for HARD**". This slice IS PCR-2b = slice-083. The same edit block updates that prose (and any `slice-079` / "deferred to PCR-2" forward-references at `skills/commit-slice/SKILL.md:185-192` and the resolver docstring `tools/parallel_conflict_resolver.py:16-18`) to shipped-status; OSDG-1 byte-equal forward-sync carries it. Pre-sign-off sweep: `grep -n "slice-079\|PCR-2\b" skills/commit-slice/SKILL.md tools/parallel_conflict_resolver.py`.

## Contracts added or changed

### Resolver CLI / library contract (no HTTP — local tool surface)
- **`resolve_hard_conflict(diag, repo_root=None) -> ResolutionResult`** — `action="STOP"`, `conflict_class in {HARD, MIXED}`, `reason` carries gate context. Defined in `tools/parallel_conflict_resolver.py`. Never mutates rebase state; never calls `git rebase --continue`.
- **`--verify-resolution [--json] [--repo-root]`** — exit 0 + `action: CLEAN` iff `git diff --name-only --diff-filter=U` is empty AND no line-anchored `^<{7}` / `^>{7}` opener/closer survives in `git diff --cached`; exit 0 + `action: STOP` (`reason=paths-still-unmerged` or `reason=unresolved-markers-present`) otherwise; exit 1 on UNKNOWN/unreadable git state. Fail-closed. **NOT `git diff --cached --check`, NOT a `=======` scan** (M-add-1 fix).
- **`--record-hard-resolution --verdict <CLEAN|NEEDS-FIXES|...> --disposition <apply|abort> [--json] [--repo-root]`** — appends the HARD audit section best-effort; exit 0. Invoked by the skill ONLY after a ratified apply + successful continue.
- **Auth model**: cooperative-not-adversarial per [[ADR-067]]; the **TRI-RESOLVE-1 user gate is the apply authorization** — no resolution is applied without explicit user ratification. A malicious local actor can bypass via direct git ops (out of scope, per ADR-067).
- **Error cases**: paths-still-unmerged / leftover markers → STOP; Critic verdict BLOCKED → STOP (no continue); TRI-RESOLVE-1 anything-but-apply → STOP; resolver-helper import failure → unchanged PSQ-3 SOAD-1 STOP (bootstrap defense); audit-write failure → stderr, non-blocking.

### B2 / M1 / M-add-1 fix — `--verify-resolution` keys on the `<<<<<<<`/`>>>>>>>` openers/closers

**B2 (first Critic)**: the original substring scan for `<<<<<<<` / `=======` / `>>>>>>>` false-positives on a Markdown **setext H1 underline** (`Title\n=======`), seven-`=` prose, and marker-describing docs (ADR-069:33, the resolver's own docstrings, this design.md). HARD U-files are by definition markdown/source, so a substring scan STOPs correct resolutions of the exact file class HARD conflicts comprise.

**M-add-1 (meta-Critic)**: the first round's proposed fix — `git diff --cached --check` — was empirically shown to carry the **identical** defect: git's `--check` flags any line-anchored `=`-run of length ≥7 as a `leftover conflict marker` (exit 2), so a 7-`=` setext underline STOPs just as the substring scan did. `git diff --cached --check` is therefore **rejected** too.

**Resolution** (M-add-1): the unresolved-conflict signal is keyed on the **`<<<<<<<` opener and `>>>>>>>` closer** (line-anchored `^<{7}` / `^>{7}`), which have **no legitimate Markdown/source analog** (unlike `=======`, which collides with setext headings and dividers). `--verify-resolution` is CLEAN iff (a) `git diff --name-only --diff-filter=U` is empty (git itself considers all paths resolved/staged) **and** (b) no `^<{7}` / `^>{7}` line survives in `git diff --cached`. This is a **conservative fail-closed heuristic**: a rare doc that legitimately contains a line *starting with* `<<<<<<<` / `>>>>>>>` (e.g. a code-fence demonstrating a conflict) would false-STOP — but that is SAFE (it refuses to continue and routes the user to re-resolve/abort; it never silently continues), and such lines are far rarer than `=======`. **APED-1 obligation**: the build runs this rule against the repo markdown corpus (setext headings, `=======` dividers, marker-describing prose) AND a genuine unresolved `<<<<<<<`…`>>>>>>>` triple, quoting the result in `build-log.md` — confirming setext/divider markdown is CLEAN and a real marker STOPs. The AC2 test `test_verify_resolution_clean_on_resolved_markdown_setext` asserts a resolved ADR retaining a setext `=======` heading returns CLEAN.

### M2 fix — two HARD-entry paths; skill keys the gate on the returned class

`resolve_hard_conflict` is the dispatch target for the **upfront** path (`classify_conflict` returns HARD/MIXED). But `resolve_soft_conflict` also has a **mid-loop SOFT→HARD escalation** leg: `_merge_shippability` can raise `_SoftResolutionError(..., HARD)` (`tools/parallel_conflict_resolver.py:~1256`) when a SOFT-looking shippability conflict has same-slice-number-different-content, returning a bare `action="STOP", conflict_class=HARD` (`:295-300`) — atomicity holds (no `pending_writes` flushed) but this STOP does NOT pass through `resolve_hard_conflict`. **Decision**: the skill's gate-flow entry keys on the `--resolve-soft` JSON `action=="STOP" AND conflict_class in {HARD, MIXED}` — which uniformly catches BOTH the upfront-classify path and the mid-loop-escalation path. `resolve_hard_conflict` enriches the upfront STOP with gate context; the escalation STOP's reason is informational only (the skill re-runs `--diagnose` for the full diagnostic regardless). A regression test drives the shippability SOFT→HARD-escalation path and asserts it enters the gate flow (not just the upfront-HARD path).

## HARD/MIXED resolution flow (concrete — B1 / M3 / M4 fixes)

### B1 + M-add-2 fix — the Critic mechanism is the `code-review` agent (diff-calibrated)

/critique (B1) correctly flagged that the `/critique` + `/critique-review` *skills* are hardwired to a slice `design.md` (prereq STOP if absent — `skills/critique/SKILL.md:52-55`), write to a slice-folder `critique.md`, and run `tools.triage_audit` / `tools.critique_review_audit` against a slice folder — none of which exist at `/commit-slice --merge` time (post-`/reflect`, post-archive). The first-round fix (reuse the **named** `critique`/`critique-review` subagents with a custom preamble) was then refuted by the meta-Critic (M-add-2): `agents/critique.md` + `agents/critique-review.md` front-matter *demand* slice artifacts ("expects slice artifacts as input… if missing, say so and stop") and bake the design-oriented 9 dimensions (TF-1, PMI-1, MEPD-1) into the **system prompt** — a user-message preamble cannot override that, so the named agents would fail-stop on a merge diff. The contradiction was relocated, not resolved.

**Resolution (TRI-1 M-add-2 decision, 2026-05-29)**: use the **`code-review` agent** (`agents/code-review.md`, slice-060 / [[decisions/ADR-059]]) — it is ALREADY diff-calibrated (its 9 dimensions are the `/critique` dimensions *reframed for a code/content diff*), it exists, and it reviews exactly a code/content diff. No new agent file; no design-folder dependency. Concrete bindings (locked here):

- **Spawned via the Agent tool** (`subagent_type: "code-review"`) on the **resolved merge diff** — a single adversarial pass (the two-pass meta-leg from the /design-slice choice is recovered by the TRI-RESOLVE-1 user gate, which is the actual apply authority).
- **Inputs handed to the agent**: the resolved diff (`git diff --cached` of the U-file set), the pre-resolution `--diagnose` JSON (concerned slices + U-files + claim history), and both rebase stages (`git show :2:<path>` / `:3:<path>`) for the conflicting files. The agent reviews along its existing code-as-artifact dimensions, prompted to focus on: lost-hunk / dropped-side detection, both-sides-intent preservation, semantic correctness of the merge, no stray conflict markers, and vault/ADR contradiction introduced by the resolution.
- **Output captured INLINE** by the skill (rendered into the TRI-RESOLVE-1 presentation) — **NOT** written to a slice-folder file, and **no design-folder audit runs** (TRI-RESOLVE-1 replaces TRI-1 as the gate). Any code-review blocker → BLOCKED → STOP (the `Apply` affordance is removed; the user can only Re-resolve / Abort).

ADR-075 Option B + Decision are updated to record the `code-review` agent (single-pass) as the final mechanism, superseding the /design-slice two-pass-named-agents choice for buildability (M-add-2).

### M3 fix — TRI-RESOLVE-1 fail-closed mechanism (operationalized)

A SOAD-1 `AskUserQuestion` returns one offered option (or is interrupted). TRI-RESOLVE-1's fail-closed contract is made operational by:
- **Option set**: `Apply resolution (continue rebase)` | `Re-resolve (edit again)` | `Abort rebase` — exactly one option (`Apply…`) is the continue path. Every other option, AND any interrupt / no-selection / session-end state, maps to **STOP-no-continue** (the skill never calls `git rebase --continue` except on the explicit `Apply` branch).
- **Two-condition apply**: the `Apply` branch fires `git rebase --continue` only when **both** (i) the user explicitly selected `Apply` **and** (ii) the `code-review` agent returned no blocker finding. A blocking finding removes/greys the `Apply` affordance — the user can only `Re-resolve` or `Abort`. No default-accept exists.
- **Mid-rebase interrupt / resume contract**: an abandoned gate leaves the rebase in-progress and the working tree untouched; re-invoking `/commit-slice --merge` re-enters cleanly at sub-step 2.5 (the rebase is still in progress; WT-clean guardrail + fast-forward no-op semantics per [[ADR-068]] §Re-entry semantics referenced at `skills/commit-slice/SKILL.md:175`). No stale-resolution is auto-applied across sessions.

### M4 fix — `_index.md` is the dominant HIGH-frequency HARD case (framing corrected)

/critique (M4) correctly observed that ADR-069:17 makes **`architecture/slices/_index.md` conflict on essentially every parallel merge** (every slice regenerates it via `/archive`'s Haiku-dispatch; it can never be SOFT — ADR-069:72) and methodology-minting slices also conflict on `methodology-changelog.md`. So the dominant *real* HARD conflict is high-frequency, not low — and routing it through the `code-review` agent + user gate re-introduces the very latency ADR-069:37 rejected for blanket-Critic. This slice does **not** add a lighter auto-resolve path (out of scope per /slice — gate-on-hand-resolve only), but the framing is corrected honestly:
- For an **`_index.md`-sole HARD conflict**, the canonical hand-resolution IS *"re-run `/archive` to regenerate the lessons-block"* (ADR-069:72) — the user's resolution is mechanical; the `code-review` agent then reviews the regenerated `_index.md` diff. The skill prose surfaces this guidance in the `_index.md`-sole STOP diagnostic.
- AC #5's APED-1 battery includes an **`_index.md`-sole HARD scenario** (in addition to a generic source-file HARD) so the dominant path is exercised at build.
- A **lighter-path follow-up** ("deterministic `_index.md` regen or Critic-skip for `_index.md`-sole HARD conflicts") is added as a new `slice-queue.md` candidate (`add-index-md-soft-promotion-or-light-hard-path`); ADR-075 Consequences records the deferral. ADR-075 no longer claims HARD is uniformly "low-frequency".

## Data model deltas

None. No entities, no migrations. The only persisted artifact is the append-only `architecture/parallel-conflict-resolution-log.md`, which gains a new section-type (`## Hard-conflict resolution -`) — additive to the existing `## Soft-conflict resolution -` / `## Vault-claim resolution -` shapes.

## Wiring matrix

Per **WIRE-1**. This slice introduces **no new module/file under `tools/` or `src/`** — all additions are functions within the already-consumed `tools/parallel_conflict_resolver.py` and prose within the already-consumed `skills/commit-slice/SKILL.md`. New public functions are nonetheless mapped to consumers + tests for honesty:

| New surface | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `resolve_hard_conflict` | `resolve_soft_conflict` HARD/MIXED dispatch (`tools/parallel_conflict_resolver.py`) + `skills/commit-slice/SKILL.md` sub-step 2.5 | `tests/methodology/test_pcr_2b_hard_conflict_dispatch.py::test_hard_conflict_fail_closes_to_stop_when_unratified` | — |
| `--verify-resolution` CLI mode | `skills/commit-slice/SKILL.md` sub-step 2.5 (pre-Critic preflight) | `tests/methodology/test_pcr_2b_verify_resolution.py` (git-native detection; setext-markdown no-false-STOP) | — |
| `--record-hard-resolution` CLI mode | `skills/commit-slice/SKILL.md` sub-step 2.5 (post-apply audit) | `tests/methodology/test_parallel_conflict_resolution_log_hard.py::test_hard_conflict_audit_section_appended` | — |
| `_format_hard_audit_entry` | `_append_audit_log` HARD dispatch leg | `tests/methodology/test_parallel_conflict_resolution_log_hard.py` | — |

## Decisions made (ADRs)

- [[ADR-075]] — Mint PCR-2b (HARD/MIXED gate-on-hand-resolve) + TRI-RESOLVE-1 (user triage gate); the Critic mechanism = the `code-review` agent (single pass) on the resolved merge diff (TRI-1 M-add-2 decision — the named critique agents fail-stop on missing slice artifacts; refines ADR-069's "/critique + /critique-review" wording for the diff-artifact shape). — reversibility: **expensive**.

## Authorization model for this slice

Cooperative-not-adversarial (inherited from [[ADR-067]] / [[ADR-069]]). The apply decision is gated by **TRI-RESOLVE-1**: the user is the sole authority that turns a proposed (hand-resolved + Critic-reviewed) HARD/MIXED resolution into an applied `git rebase --continue`. No silent / automatic apply path exists. Bootstrap-missing-helper degrades to the pre-PCR-2b SOAD-1 manual STOP (strictly no weaker than today).

## Error model for this slice

Fail-closed at every leg (extends [[ADR-069]] § Fail-closed contract):
- `classify_conflict` → HARD/MIXED → `resolve_hard_conflict` returns STOP (never auto-continue).
- `--verify-resolution` finds remaining conflict markers → STOP (`unresolved-markers-present`); the diff never reaches the Critic or continue.
- `code-review` agent returns a blocking finding → STOP; surface findings, no continue.
- TRI-RESOLVE-1 resolves to anything other than explicit **apply** (abort / re-resolve / cancel / ambiguous / unanswered) → STOP; no `git rebase --continue`.
- Resolver helper import/exec failure → unchanged PSQ-3 SOAD-1 3-option STOP (try/except bootstrap wrap per slice-067 / [[ADR-064]]).
- Audit-log append failure → stderr breadcrumb, non-blocking (best-effort, mirrors PCR-1 / PCR-2a; the rebase has already been continued at that point).
- UNKNOWN class → STOP loud (APED-1 silent-disable / default-off-on-malformed; never silent-default to HARD-auto-apply).

## Methodology classification

- **MEPD-1 posture: INCLUDE** — mints two RULE-IDs (PCR-2b on the existing PCR-N family axis; TRI-RESOLVE-1 on a new triage-gate axis sibling to TRI-1), each with entry-pins; 5-part PMI-1 atomic bump 0.76.0 → 0.77.0 + forward-sync (MCFS-1 / AVFS-1 / OSDG-1 commit-slice / TVFS-1 / PVFS-1).
- **PCA-1 unchanged** for `/commit-slice` — `auto-advance: false` (always user-invoked). PCR-2b enhances sub-step 2.5 within the same skill.
- **Critic mandatory** — methodology surfaces (`skills/commit-slice/SKILL.md`, `tools/*.py`, new ADR, changelog) + judgment-heavy conflict semantics.

## Out of scope (carried from mission-brief)

- Auto-proposing a HARD resolution (rejected ADR-069 Option 2).
- Explicit R-23 / R-24 detection hooks (emergent-only; both stay OPEN).
- `architecture/slices/_index.md` auto-resolve (stays HARD; Haiku-regen non-deterministic).
- PSQ-4 push-time rebase.
