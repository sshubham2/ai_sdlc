# Slice 113: bulk-convert-remaining-skills-to-vault-seam

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: NONE *directly* — drains **R-32**'s last prose-rewrite residual (the bulk-skill leg named in the slice-098/109/111/112 R-32 progression), the final prep before the physical flip. Unblocks `flip-vault-to-external-store` (R-32, HIGH).
**Test-first**: false  (prose/tooling conversion; the inventory ratchet + OSDG-1 drift tests + op-gate ARE the regression harness)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Complete the `<vault>/` prose-seam rollout that slice-112 piloted on `CLAUDE.md` + `agents/critique.md`. Convert the convertible `architecture/…` operational literals across the **25 remaining skill `SKILL.md` files** to the flip-neutral `<vault>/` seam (per [[decisions/ADR-105]]), re-pin `tools/vault_flip_prose_inventory.py` + the op-gate as **one atomic move-together set**, forward-sync the OSDG-1-guarded skills, and discharge the consumer-contract obligations slice-112's Critic deferred (B1/B2/B3/M1). After this, R-32's residual is the **physical move** + the **agent-prose surface** (the 4 agent files `code-review`/`critic-calibrate`/`critique-review`/`diagnose-narrator` still carry convertible refs — deferred to a named follow-on per slice-113 `/critique` M1, since each agent needs its own ADR-105 embedded resolver-context note). Now because slice-112 proved every carve-out class live (via the agent's `:125`/`:260` carve-outs) and the flip is otherwise unblocked on every axis.

## Acceptance criteria

1. **Bulk conversion** — the convertible `architecture/…` operational literals across the 25 skill `SKILL.md` files are rewritten to `<vault>/…`; the [[decisions/ADR-105]] carve-out classes stay **concrete** (worktree-composed `<wt_path>/architecture/…` [B1]; `slice-queue.md` undecided-disposition [M1]; `diagnose-out/` no-seam [B5]; `INSTALL.md`/`README.md`; definitional/`doc-example`; historical-anchor). Observable: `--json` shows every file added to `_CONVERTED_FILES` contributes **zero** `rewrite-at-flip` literals.
2. **Inventory + op-gate re-pin (single move-together set)** — `EXPECTED_TOTAL`, `_CLASS_COUNT_FLOOR[rewrite-at-flip]`, `_BASELINE_SHA256`, and `_CONVERTED_FILES` (grown to every converted skill file) re-pinned; the op-gate is made **seam-aware** (`_OP_SINK_RE` matches `<vault>/`, per [[decisions/ADR-106]]) so its floors `{OP_UNROUTED:0, OP_DEFERRED:11, OP_OUT_OF_SCOPE:23}` stay **stable** (the converted write-ops stay visible — **no AP-12 gate-loosening**; this supersedes the brief's original "shrink floors downward" framing per the `/design-slice` Approach-A decision) and only the 3 `_OP_ALLOWLIST` entries whose lines convert are re-hashed. Observable: `--strict` exit 0 **and** `--op-gate --strict` exit 0; the converted-file ratchet still fires on a literal re-injected into a converted file **with the baseline re-pinned to match** (baseline-independent mutation).
3. **OSDG-1 / mini-CAD forward-sync** — every guarded `SKILL.md` that was converted is byte-synced (modulo EOL per ADR-033) to its installed `~/.claude/skills/<name>/SKILL.md`. The guarded set is the **on-disk 13** `tests/methodology/*_skill_drift.py` (computed at build, M-add-1): `adopt`, `build-slice`, **`code-review`**, `commit-slice`, `critique`, `critique-review`, `design-slice`, **`pulse`**, `query-design`, `reflect`, `slice`, `slice-candidates`, `triage` — NOT the stale 12-roster (which wrongly listed `diagnose` (no drift test) + omitted `code-review`/`pulse`). Observable: `pytest tests/methodology -k skill_drift` (all 13) passes.
4. **Consumer contracts discharged in-slice (AP-13 / AP-10 / FBCD-1(c))** — the BCR-1 anchor (`test_bcr_1_backlog_round_trip.py`) and any other by-name literal assertion on a converted file is repointed/preserved; the `architecture/shippability.md` count rows + every count-pin fan-out are re-pinned to the new total. Observable: `test_bcr_1_backlog_round_trip.py` + the inventory/shippability audits pass.
5. **Flip-neutrality + residual recorded** — the default still resolves to `architecture/` (zero pre-flip behaviour change — full suite green via `/validate-slice`); the **exact** remaining residual is recorded via `--json` in `reflection.md` + the R-32 register for the flip slice (closing the slice-112 `m2` "drop the estimate" obligation): (a) the carve-out literals that land at the physical move (classes 1-pathspec/4/5/6/7) AND (b) the **agent-prose surface** (4 agent files) deferred to the `convert-agent-prose-to-vault-seam` follow-on, registered in `slice-queue.md` at `/reflect`. (INSTALL.md/README.md are ADR-105 class-1 user-facing-doc carve-outs — permanent-concrete, NOT a residual.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Bulk conversion + carve-outs concrete | `$PY -m tools.vault_flip_prose_inventory --json` → assert each `_CONVERTED_FILES` skill member has 0 `rewrite-at-flip` occurrences; spot-grep a carved-out site (e.g. `skills/slice/SKILL.md` `<wt_path>/architecture/…`, `slice-queue.md`, `diagnose-out/`) still literal |
| 2 | Re-pin move-together set + ratchet | `$PY -m tools.vault_flip_prose_inventory --strict; echo $?` == 0 **and** `--op-gate --strict; echo $?` == 0; `$PY -m pytest tests/methodology/test_vault_flip_prose_inventory.py tests/methodology/test_vault_flip_op_gate.py -q` green; mutation: inject one literal into a converted file + re-pin `_BASELINE_SHA256` to match → `--strict` still exit 2 |
| 3 | OSDG-1 forward-sync | `$PY -m pytest tests/methodology/ -k skill_drift -q` green; `$PY -m tools.critique_agent_drift_audit --repo-root .` clean (agents untouched but confirm) |
| 4 | Consumer contracts | `$PY -m pytest tests/methodology/test_bcr_1_backlog_round_trip.py -q` green; shippability count-row grep matches new `EXPECTED_TOTAL` |
| 5 | Flip-neutral + residual | `/validate-slice` full suite green; `_vault_paths.VAULT_ROOT == Path("architecture")`; `--json` remainder count written into reflection + R-32 |

## Must-not-defer

- [ ] **OSDG-1 forward-sync** of every converted guarded `SKILL.md` to its installed copy — the guarded set is the **on-disk 13** `tests/methodology/*_skill_drift.py` computed at build (M-add-1: includes `code-review` + `pulse`, EXCLUDES `diagnose`), NOT the stale 12-roster; the drift tests fail-closed at `/build-slice` Step 6 + `/validate-slice`; an un-synced convert of `code-review`/`pulse`/any-of-13 reds the suite at finish.
- [ ] **Enumerate by-name literal consumers by execution, not memory** (B1/M2/M-add-2 / AP-13) — `grep tests/` for assertions reading a *converted* SKILL.md asserting a literal `architecture/…`; repoint command-arg breakers (e.g. `test_validate_slice_skill.py:65`); confirm carve-out guards stay green (`test_build_slice_skill_dirty_tree_resolution.py:204/207`, `test_code_review_skill.py:241-275`, `test_vault_flip_prose_inventory.py:72`). The grep is the closed set.
- [ ] **Git-pathspecs stay concrete (class-1, M-add-2)** — `:(exclude)architecture/…` / `:(glob)architecture/…` are git-consumed (silent-wrong on non-substitution), NOT converted; command-arg *paths* (`$PY -m tools.X architecture/Y`) DO convert (loud-fail). Don't conflate the two.
- [ ] **The op-gate stays seam-aware, NOT loosened** ([[decisions/ADR-106]]): extend BOTH the matcher (`_OP_SINK_RE` matches `<vault>/`) **AND the value EXTRACTOR (`_OP_SINK_TOKEN_RE`) in lockstep** (B2 — the extractor governs `_classify_op`; the matcher alone is vacuous), so converted write-ops stay visible + correctly classified; add the **3 `<vault>/`-sink op-gate tests** (AP-5 non-vacuity). `_OP_CLASS_FLOOR` `{0,11,23}` is **unchanged** (no AP-12 loosening). Re-hash the 3 confirmed `_OP_ALLOWLIST` entries (build-slice:407 / commit-slice:216 / design-slice:240) + **verify slice:264 by `--op-gate --json`** (M4 — expected unchanged, but contingent). Keep `_OP_SINK_RE` distinct from the inventory `_MATCH_RE`. Gate asserts the per-class breakdown `{6,11,23,0}`, not just exit 0.
- [ ] **Carve-out literals in partially-converted files are dispositioned into their carve-out class** so the file's remaining literals are all-converted (else the file cannot join `_CONVERTED_FILES`/the ratchet) — OR the file is explicitly documented as a known non-ratcheted partial-convert with rationale. `skills/slice/SKILL.md` is the canonical case (carries B1 worktree-composed + M1 slice-queue + B5 diagnose-out carve-outs).
- [ ] **BCR-1 anchor: VERIFY green, NO repoint needed** — `test_bcr_1_backlog_round_trip.py` asserts the literal `diagnose-out/backlog.md`, a class-7 carve-out (stays concrete), so the anchor survives the conversion untouched (B3 is moot given B5's diagnose-out carve-out). Confirm green at build; do NOT convert the diagnose-out ref (AP-13 consumer-driven-contract — satisfied by carve-out, not repoint).
- [ ] **Shippability count-pin fan-out** (FBCD-1(c) / AP-10) — every hard-stated count literal re-pinned to the new total, including the tool's OWN docstring narrative (the slice-111/112 N=2 build-time-docstring miss).
- [ ] **`_CONVERTED_FILES` keyed to forward-slash relpaths** (M3 — a `\`-keyed entry silently never matches on Windows → vacuous green).

## Out of scope

- The **physical flip** — move `architecture/` to the external store + git-untrack + the `/commit-slice` RETIRE no-op + draining R-32.a/R-32.b. That is the dedicated `flip-vault-to-external-store` slice; R-32 retires there, not here.
- The **`<diagnose-out>` token + its production seam** — no `diagnose-out` resolution mirror exists in `tools/_vault_paths.py` (slice-112 B5); `diagnose-out/` refs stay concrete this slice.
- Converting the **carve-out literals** (git-pathspec `:(exclude)architecture/…` [M-add-2 — git-consumed, class-1], worktree-composed `<wt_path>/architecture/…`, active-folder `architecture/slices/slice-NNN-…`, `slice-queue.md`, `diagnose-out/`, `INSTALL.md`/`README.md`) — they stay concrete **by design** per ADR-105.
- The **agent-prose surface** — the 4 agent files (`agents/code-review.md`, `agents/critic-calibrate.md`, `agents/critique-review.md`, `agents/diagnose-narrator.md`) carry convertible refs but are **deferred to the `convert-agent-prose-to-vault-seam` follow-on** (M1, TRI-1-ratified): each needs its OWN embedded `<vault>` resolver note (a Task-spawned subagent does NOT inherit `CLAUDE.md` — ADR-105 resolver-context scope / slice-112 M-add-1), a distinct concern from the main-agent-read skill prose.
- `CLAUDE.md` / `agents/critique.md` — already converted in slice-112 (the pilot); not re-touched.
- Re-deciding any ADR-105 carve-out **class** boundary — this slice *applies* the classes (and refines the *application* of class-1 to git-pathspecs + command-args per TRI-1), it does not redefine a class.

## Dependencies

- Prior slices: [[slice-112-make-prose-vault-location-agnostic]] — the `<vault>` convention + converted-file ratchet + ADR-105 carve-out classes (this slice's `m2`/B1/B2/B3/M1 deferrals land here); [[slice-111-route-in-loop-skill-vault-ops-via-seam]] — the op-gate (`--op-gate`) + `vault_edit` seam; [[slice-107-inventory-vault-flip-prose-surface]] — the inventory tool itself.
- Vault refs: [[decisions/ADR-105]] (the `<vault>` convention + 7 carve-out classes), [[decisions/ADR-104]] / [[decisions/ADR-102]] (op-gate), `tools/vault_flip_prose_inventory.py`, `architecture/shippability.md`.
- Risk register: [[risk-register#R-32]] — this slice drains the **prose-rewrite residual**; R-32 stays `mitigating` (retires only at the physical move).
- Tests/consumers (enumerate the closed set by build-time grep — B1/M2/M-add-2): `tests/methodology/test_bcr_1_backlog_round_trip.py` (BCR-1 anchor — green untouched), the on-disk **13** `*_skill_drift.py` (OSDG-1 forward-sync), `tests/methodology/test_vault_flip_op_gate.py` + `test_vault_flip_prose_inventory.py` (re-pin + the new `<vault>/`-sink tests + the 5-match pin), `tests/methodology/test_validate_slice_skill.py:65` (command-arg → repoint), `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py:204,207` (carve-out guard → green), `tests/skills/code_review/test_code_review_skill.py:241-275` (pathspec carve-out → green).

## Mid-slice smoke gate

At ~50% of build (≈half the skill files converted + a first re-pin pass), run:
```
$PY -m tools.vault_flip_prose_inventory --json   # exact convertible count + per-file class breakdown
$PY -m pytest tests/methodology -k skill_drift -q   # all 13 guarded (m2 — was just test_slice_skill_drift.py)
$PY -m pytest tests/methodology/test_vault_flip_op_gate.py -q
```
Expected: every file already in `_CONVERTED_FILES` contributes **zero** `rewrite-at-flip` literals (total math deterministic); with the seam-aware op-gate the op-class counts stay **at/above their stable floors** `{0,11,23}` (a converted op-sink stays visible via `_OP_SINK_RE`; a `<vault>/` op surfacing as **OP_UNROUTED** means the `_OP_ALLOWLIST` re-hash is incomplete, NOT a floor shrink); converted-skill drift tests green after forward-sync. If a converted file still carries an un-carved `rewrite-at-flip` literal, or an op surfaces as OP_UNROUTED, or an op floor *does* shrink (the seam-aware regex missed a sink), or a drift test is red → STOP: the conversion / carve-out-disposition / `_OP_SINK_RE` / forward-sync is incomplete. Don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
