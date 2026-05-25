# Slice 058: add-install-wakeup-prompt-guardrail

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: none *tracked* — preventive. Addresses an untracked operational defect class: a `ScheduleWakeup` call whose `prompt` is a slash-command-shaped string passed as a no-op label / heartbeat / fallback re-fires that command as spurious user input at wake time (experienced N=2 in recent sessions). No `architecture/risk-register.md` entry exists; `/reflect` may mint one.
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The lesson "never pass a slash-command-shaped `prompt` to `ScheduleWakeup` as a no-op label" currently lives only in this machine's project memory (`memory/schedulewakeup-replays-prompt-literally.md`) — it does not travel to other machines that install the pipeline. This slice makes the guardrail portable: `INSTALL.md` gains a new idempotent, confirmation-gated step — modelled on the existing Step 3d PY-convention append — that writes a "wakeup-prompt discipline" block into the installing user's global `~/.claude/CLAUDE.md`, so every machine that runs the install inherits the rule. A regression test pins the new step and its block content against `INSTALL.md` drift.

## Acceptance criteria

1. `INSTALL.md` gains a new idempotent, confirmation-gated install step — modelled on Step 3d (`INSTALL.md:101-123`): show the planned diff, ask confirmation, skip if the block's heading is already present — that appends a "wakeup-prompt discipline" block to the user's global `~/.claude/CLAUDE.md`.
2. The appended block states the three load-bearing facts: (a) `ScheduleWakeup` replays its `prompt` argument literally as user input at fire time; (b) a slash-command-shaped string must never be passed as a no-op label, heartbeat, or fallback wakeup — it re-fires the command as spurious input even after the original task already completed; (c) intentional wakeup prompts (`/loop`, genuine scheduled tasks) are unaffected.
3. A new regression test pins AC1 + AC2 against `INSTALL.md` (genuine FAIL-before-edit / PASS-after-edit contrast) and is registered as a shippability catalog row per SCPD-1 with a consumer-presence pin.

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0) Each AC maps to a failing test written BEFORE the `INSTALL.md` edit. Statuses progress PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | methodology | tests/methodology/test_install_md_wakeup_guardrail.py | test_install_md_has_idempotent_wakeup_discipline_step | PASSING |
| 2 | methodology | tests/methodology/test_install_md_wakeup_guardrail.py | test_wakeup_block_states_load_bearing_facts | PASSING |
| 3 | methodology | tests/methodology/test_install_md_wakeup_guardrail.py | test_shippability_row_58_present_and_cites_install_wakeup_guardrail | PASSING |

(Test module path is a proposal — `/design-slice` decides whether to add this new sibling module or extend the existing `tests/methodology/test_install_md_correctness.py` from slice-045; TPHD-1 harmonizes function names if they change.)

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | AC1 — new INSTALL.md step | Read `INSTALL.md`; confirm the new step has a heading-present skip guard, a diff-show, and a confirmation ask (Step 3d shape). `pytest tests/methodology/test_install_md_wakeup_guardrail.py::test_install_md_has_idempotent_wakeup_discipline_step` PASSES — and FAILed when run against pre-edit `INSTALL.md`. |
| 2 | AC2 — block content | `pytest ...::test_wakeup_block_states_load_bearing_facts` PASSES; manual read confirms all three load-bearing facts AND the explicit `/loop`-not-blocked carve-out. |
| 3 | AC3 — shippability row | `$PY -m tools.shippability_runner architecture/shippability.md` includes the new row and it PASSES; `pytest ...::test_shippability_row_58_present_and_cites_install_wakeup_guardrail` PASSES. |

## Must-not-defer

- [ ] **Idempotency** — re-running `INSTALL.md` detects the block via its heading and skips; no duplicate appends (Step 3d `If present → skip` parity).
- [ ] **Confirmation gate** — the step shows the planned diff and asks before mutating the user's global `~/.claude/CLAUDE.md` (`INSTALL.md:198` discipline: never modify global CLAUDE.md without showing the diff + confirmation).
- [ ] **Genuine contrast** — the regression test FAILs on pre-edit `INSTALL.md` and PASSes after; no tautological pin (verified at `/build-slice`).
- [ ] **Scope precision** — the appended block must NOT ban legitimate `ScheduleWakeup` use (`/loop`, intentional scheduled wakeups); it targets only the slash-command-shaped no-op/heartbeat/fallback misuse.
- [ ] **Shippability propagation** — new test registered as a shippability catalog row (SCPD-1).

## Out of scope

- Modifying the `ScheduleWakeup` harness tool itself, or proposing a `CancelWakeup` tool — harness features, outside this repo's control.
- Editing the per-project memory file `memory/schedulewakeup-replays-prompt-literally.md` — it already exists and is correctly phrased; this slice does not touch the memory subsystem.
- Retro-handling any wakeup already scheduled in the current session — operational, not a code change.

## Dependencies

- Vault refs: `INSTALL.md` (the INST-1 install recipe; Step 3d at `INSTALL.md:101-123` is the model; `INSTALL.md:198` the confirmation discipline).
- Prior slices: [[slice-045-fix-install-pypi-package-name-and-stale-prose]] — `tests/methodology/test_install_md_correctness.py` (shippability #45) is the INSTALL.md regression-test precedent. [[slice-047-add-two-scope-install]] — ADR-049's global-only install-scope decision record, relevant if `/design-slice` weighs the per-project route.
- Risk register: no open risk; preventive slice.
- **Design decision deferred to `/design-slice`**: whether to (a) append to global `~/.claude/CLAUDE.md` via `INSTALL.md` — the user's primary choice; (b) fold the guardrail into the per-project `CLAUDE.md` generated by `/triage` + `/adopt` (scopes it to pipeline projects); or (c) both. Routes (b)/(c) would additionally touch the OSDG-1-guarded `/triage` + `/adopt` `SKILL.md` surfaces and broaden Critic scope.

## Mid-slice smoke gate

After writing the new test module (test-first) and BEFORE applying the `INSTALL.md` edit, run:
```
$PY -m pytest tests/methodology/test_install_md_wakeup_guardrail.py -q
```
Expected: the AC1 + AC2 tests FAIL (the new step / block does not yet exist in `INSTALL.md`). If they PASS pre-edit, STOP — the test is tautological and proves nothing.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
