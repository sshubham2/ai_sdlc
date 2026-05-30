# Design: Slice 086 harden-agent-spawn-skills-await-real-output

**Date**: 2026-05-30
**Mode**: Standard

## What's new

- A **canonical await-the-real-agent guard** block — one invariant literal authored VERBATIM into the spawn→write seam (the Step 2 → Step 3 boundary) of all three agent-spawning skills:
  - `skills/critique/SKILL.md` — after L99 ("Return the agent's complete critique.md content"), before Step 3 (L105/L107 write).
  - `skills/critique-review/SKILL.md` — after L75 ("Return the agent's complete `critique-review.md` content"), before Step 3 (L81/L83 write).
  - `skills/code-review/SKILL.md` — after L140 ("Return the agent's complete `code-review.md` content"), before Step 3 (L151/L153 write).
- A new structural-pin test `tests/methodology/test_r25_await_real_agent_guard.py` that asserts the canonical guard literals are present **within each skill's Step 2 → Step 3 seam region** (seam-scoped, not file-global — M-add-1) in each of the three in-repo `SKILL.md` files, and FAILS if any skill loses OR relocates the guard out of the seam.
- A shippability catalog row (`architecture/shippability.md`) pinning the new test (RPCD-1 / SCPD-1).
- [[ADR-078]] — records the enforcement-mechanism choice + the stopgap→pipeline migration.

## What's reused

- The OSDG-1 / Mini-CAD content-equality discipline and the **one** existing per-skill drift test among the three spawn-skills: `tests/methodology/test_code_review_skill_drift.py` (re-installing the edited `code-review` SKILL.md keeps it green). See CLAUDE.md "Self-hosting discipline §". **Builder-verified drift-status (B1/B2):** there is NO `tests/methodology/test_critique_skill_drift.py` on disk — `critique` is named in CLAUDE.md:42's OSDG-1 set but has no drift-test file; `code-review` has a drift-test file but is NOT named in CLAUDE.md:42. The earlier "these two ALREADY in the OSDG-1 guarded set" claim was factually wrong and is removed. The new AC-2 pin test is therefore the sole guard-literal enforcement for `critique` and `critique-review` (and a complementary existence-check for `code-review`). The pre-existing CLAUDE.md:42 inventory drift is logged as a DISCOVERED follow-up (`reconcile-osdg-1-inventory-claude-md-L42`), out of scope here.
- The structural-prose-pin test pattern from `tests/methodology/test_soad1_structured_options_ask_rule.py` (single canonical literal reused verbatim across N surfaces; `tests.methodology.conftest.read_file` loader; section-scoped assertions).
- The risk register entry [[risk-register#R-25]] — the fix candidate is pre-specified there.
- The stopgap being retired: the `# Spawned-agent output` section in `~/.claude/CLAUDE.md` (L41).

## Components touched

### `skills/critique/SKILL.md` (modified)
- **Responsibility**: routes the design-Critic review; spawns the `critique` subagent and writes `critique.md` from its return.
- **Lives at**: `skills/critique/SKILL.md` (+ installed mirror `~/.claude/skills/critique/SKILL.md`).
- **Key interactions**: Agent tool (`subagent_type: "critique"`). **No in-repo↔installed drift test exists for `critique`** (B1 — `test_critique_skill_drift.py` is a phantom); the AC-2 pin test guards its guard-literal. Installed copy re-synced manually after edits.

### `skills/critique-review/SKILL.md` (modified)
- **Responsibility**: routes the meta-Critic review of `critique.md`; spawns the `critique-review` subagent and writes `critique-review.md`.
- **Lives at**: `skills/critique-review/SKILL.md` (+ installed mirror).
- **Key interactions**: Agent tool (`subagent_type: "critique-review"`). **Note**: NOT currently in the OSDG-1 content-equality guarded set — the new structural-pin test (AC-2) is what guards its guard literal; full OSDG-1 extension is out of scope (R-13-class follow-up `extend-osdg-1-to-critique-review`, now in the slice-queue).

### `skills/code-review/SKILL.md` (modified)
- **Responsibility**: routes the code-Critic review of the slice diff; spawns the `code-review` subagent and writes `code-review.md`.
- **Lives at**: `skills/code-review/SKILL.md` (+ installed mirror).
- **Key interactions**: Agent tool (`subagent_type: "code-review"`); `tests/methodology/test_code_review_skill_drift.py` (the ONLY existing SKILL.md content-equality drift test among the three spawn-skills — note CLAUDE.md:42 omits code-review from the named OSDG-1 set despite this test existing; B2).

### `tests/methodology/test_r25_await_real_agent_guard.py` (created)
- **Responsibility**: pins BOTH the canonical heading literal AND one operative body literal (M2), **seam-scoped to each skill's Step 2 → Step 3 region (M-add-1)**, across all three SKILL.md surfaces — so neither the guard's identity, its operative instruction, NOR its placement at the spawn→write seam can silently regress.
- **Lives at**: `tests/methodology/test_r25_await_real_agent_guard.py`.
- **Key interactions**: `tests.methodology.conftest.read_file`.

## The canonical guard literal (authored VERBATIM in all three skills)

The invariant literal the pin test asserts is the bold heading sentence (unique-to-invocation per the slice-075/085 "pin a literal unique to the invocation, not a noun-phrase in narration" lesson):

> **Await the real agent — never fabricate its output.**

Followed by a short block carrying the four obligations (final prose wording is the Builder's, but MUST preserve the four facts and the heading literal):
1. The `Agent` tool may return an **asynchronous acknowledgment** ("Async agent launched…") rather than the finished review.
2. That acknowledgment is **NOT** the deliverable.
3. STOP and wait for the `task-notification`; write this file ONLY from the agent's **actual returned content**.
4. NEVER self-author a placeholder, and NEVER write the file from your own main-thread reasoning, while the agent runs.

The pin test asserts **two** literals are present once in each of the three SKILL.md files (M2 — a heading-only pin would let a future edit keep the slogan but gut the operative body, leaving the main thread with no instruction and silently re-opening R-25):

1. **The heading literal** `**Await the real agent — never fabricate its output.**` — the dash is **U+2014 EM DASH**, NOT hyphen-minus U+002D, NOT en-dash U+2013. This exact byte-string is the single source of truth shared across mission-brief AC-1, this design.md, ADR-078, all three SKILL.md files, and the test's CANON constant (M1/M3). Signals **"the guard exists."**
2. **One operative body literal** — a unique-to-invocation phrase from obligation 4, `NEVER self-author a placeholder`. Signals **"the guard still instructs."** Its uniqueness (absent from informative narration in each SKILL.md) MUST be verified at build time per the slice-075 lesson; if it collides with narration in any of the three files, pick an alternative obligation phrase and update the test CANON in the one place it lives.

Pinning heading + one body literal (not the whole four-obligation paragraph) keeps the test robust to prose tuning while failing closed if either the guard's identity OR its operative instruction is dropped.

**Seam-scoping (M-add-1) — load-bearing:** both literals MUST be asserted to fall within each skill's **Step 2 → Step 3 region**, NOT merely present file-globally. The test locates each skill's `Step 2` and `Step 3` section headings and asserts both literals appear (each exactly once) BETWEEN them — directly mirroring the SOAD-1 precedent's `_fenced_block_after` helper (`tests/methodology/test_soad1_structured_options_ask_rule.py:13-16,55-70`), which exists precisely because a repo-global `.count()` passes even when a hit lands in the wrong section. A file-global pin would stay green if a future edit RELOCATED the guard block out of the spawn→write seam (into a footer/template section or above Step 2): the literal still appears once, the test passes, but the main thread no longer reads the guard inline at the spawn→write decision point — silently re-opening R-25 by relocation rather than deletion. This reconciles the "What's reused" claim of reusing SOAD-1 section-scoped assertions (which the prior file-global spec contradicted).

**Build-time APED-1 (M1):** before relying on pytest, assert the byte-exact heading literal (U+2014) appears exactly once in each skill's Step 2→Step 3 region AND equals the test CANON codepoint-for-codepoint — do not eyeball the dash. This avoids the slice-085 false-negative class (pinning a literal that also appears in narration) and the dash-drift false-pass class.

## Contracts added or changed

None — no endpoints, events, or schemas. This slice changes skill PROSE contracts + adds a test.

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tests/methodology/test_r25_await_real_agent_guard.py` | — | — | `test module — self-executing under pytest; it IS the consumer test; pins the guard literal across 3 SKILL.md surfaces, no production consumer demanded — rationale: structural-pin test, no importable production module introduced` |

(No production modules introduced; the three SKILL.md edits are modifications to existing files, not new modules.)

## Decisions made (ADRs)

- [[ADR-078]] — enforce the await-the-real-agent guard via a single canonical-literal structural-pin test across all three spawn-skills, and migrate the guard out of the global CLAUDE.md stopgap into the in-repo skill contracts — reversibility: cheap.

## Authorization model for this slice

N/A — no runtime authorization surface. The change is to methodology prose + a content-presence test.

## Error model for this slice

N/A — no new runtime error codes. The new test's failure mode is a pytest assertion failure naming the offending SKILL.md surface (guard literal absent).

## Ordering invariant (load-bearing — see mission-brief Must-not-defer)

The global `# Spawned-agent output` stopgap in `~/.claude/CLAUDE.md` is the ONLY protection until the skill-level guard is installed. Therefore the removal (AC-4) MUST be the **closing** action, performed only after: (a) the guard literal is present in all three in-repo SKILL.md files, (b) the new pin test PASSES, and (c) the installed mirrors are synced (OSDG-1 drift tests green). Removing it earlier opens an unprotected window. ADR-078 records this ordering as a consequence.
