# Validation: Slice 058 add-install-wakeup-prompt-guardrail

**Date**: 2026-05-22
**Result**: PASS

This is a documentation + regression-test slice (no deployment target). Per `/validate-slice` "When real validation isn't possible" — validation runs against the **real artifacts on disk**: the actual `INSTALL.md`, the actual `architecture/shippability.md`, real `pytest`, and the real audit tools.

## Per-criterion results

### AC1: INSTALL.md gains a new idempotent, confirmation-gated install step appending a wakeup-prompt-discipline block to global `~/.claude/CLAUDE.md`
- **Status**: PASS
- **Evidence**: `INSTALL.md` carries `### 3h: Global CLAUDE.md — wakeup-prompt discipline` (appended after Step 3g, before `## Step 4`). The step prose: (a) appends to `~/.claude/CLAUDE.md`; (b) "Check `~/.claude/CLAUDE.md` for a `# Wakeup-prompt discipline` heading. If that heading is already present, skip the append (idempotent re-run; no duplicate append)"; (c) "Show the user the diff first and get confirmation — the same discipline as Step 3d". `pytest tests/methodology/test_install_md_wakeup_guardrail.py::test_install_md_has_idempotent_wakeup_discipline_step` → **PASSED** (and FAILed against the pre-edit INSTALL.md at the mid-slice smoke gate — genuine contrast).
- **Notes**: modelled on Step 3d; governed by the existing `INSTALL.md:198` "never modify global CLAUDE.md without showing the diff" rule.

### AC2: the appended block states the three load-bearing facts + the `/loop` carve-out
- **Status**: PASS
- **Evidence**: the embedded `# Wakeup-prompt discipline` block states (a) `ScheduleWakeup` replays `prompt` "literally, as fresh user input" at fire time; (b) never pass a slash-command-shaped string "as a no-op label, heartbeat, or fallback wakeup"; (c) "Intentional wakeup prompts — `/loop`'s own prompt, a genuine scheduled task — are unaffected"; plus the harness-notifies-on-completion context line. `pytest ...::test_wakeup_block_states_load_bearing_facts` → **PASSED** (4 discrete whitespace-collapsed anchor asserts, each FAILed individually pre-edit).
- **Notes**: scope precision confirmed — the block does not ban legitimate `ScheduleWakeup`/`/loop` use; it targets only the no-op/heartbeat misuse.

### AC3: a new regression test pins AC1+AC2 (genuine FAIL→PASS contrast) + registered as a shippability catalog row
- **Status**: PASS
- **Evidence**: `tests/methodology/test_install_md_wakeup_guardrail.py` created; 3 FAIL pre-edit → 3 PASS post-edit (genuine contrast, mid-slice smoke gate). `architecture/shippability.md` row #58 present; `pytest ...::test_shippability_row_58_present_and_cites_install_wakeup_guardrail` → **PASSED**. The SRSC-1 catalog runner executed all 58 rows (incl. #58) → **58 PASS, 0 FAIL**.
- **Notes**: B2 cleanup also validated — `INSTALL.md` carries zero version-number literals after the line-18 drift-proof reword.

`pytest tests/methodology/test_install_md_wakeup_guardrail.py -v` → `3 passed in 0.04s` (all 3 ACs).

## Multi-instance validation
**Required?**: no — install-recipe prose + a regression test; no multi-user / multi-device / multi-account surface.
**Result**: not-applicable

## Step 5b — VAL-1 layered safety
`validate_slice_layers --changed-files INSTALL.md tests/methodology/test_install_md_wakeup_guardrail.py --imports-allowlist tests` → **0 secrets, 0 import findings, 0 suppressed**. Clean — both layers passed.

## Step 5c / 5d
WS-1 (walking-skeleton) and ETC-1 (exploratory-charter): both `false` in mission-brief — audits clean silently, not applicable.

## Step 5.5 — Shippability catalog regression check
- SCMD-1 pre-gate: clean (58 rows; incidental=0, essential_unregistered=0).
- PTFCD-1 pre-gate: clean (58 rows, 311 test-path tokens — all files + cited functions exist).
- SRSC-1 canonical runner (`tools.shippability_runner`): **58 row(s), 58 PASS, 0 FAIL** — no past slice regressed; new row #58 passes.

## Reality surprises
None. The slice executed exactly as designed; no edge case or surprise surfaced during validation.
