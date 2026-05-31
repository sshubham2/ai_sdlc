---
id: ADR-080
title: Project-frame is an ephemeral deterministic extraction-and-render tool fed to design-slice + both Critic layers; mints PFS-1
date: 2026-05-31
slice: slice-088-add-project-frame-synthesizer
reversibility: expensive
status: accepted
supersedes: null
---

# ADR-080: Ephemeral project-frame synthesizer + PFS-1

## Context

A slice can be **locally correct yet strategically wrong**. slice-087 designed a
"flag-all-unmerged-`slice/*`" stranded-detector that breaks the project's own
parallel-slice direction (PSQ / BRANCH-2) — it cry-wolfs on every legitimately
in-flight parallel slice. Neither `/design-slice` nor either Critic layer caught
it; the **user** did, after `/critique-review`. Root cause: the review stack reviews
each slice **in isolation**, with no artifact putting the project's *deliberate
forward direction* (trajectory) in front of the designer or the Critics.

`/critic-calibrate` (2026-05-30) split the fix into two parts. **Part B** (already
shipped, commit `64f6ea3`) added a Dim-7 "strategic-direction fit + architectural-
concurrency" probe to `agents/critique.md`, with an explicit note that "a future
ephemeral project-frame input will hand this over directly." **This slice is Part A**:
build that input.

Two design forks must be resolved:

1. **Tool vs skill** — the mission brief AC1 leaves it open ("`tools/project_frame_synth.py`,
   or a `/frame` skill if prose-judgment is required").
2. **Where the rule lives** — MEPD-1 requires a behaviour-changing methodology slice to
   either mint a RULE-ID (+ entry-pin + version bump) or document why none is needed.

## Options considered

1. **Deterministic Python extraction-and-render tool, ephemeral stdout-only (chosen).**
   - Pros: the brief's own test-first plan demands `test_frame_regenerates_deterministically`
     — only a deterministic tool can satisfy it. Unit-testable (fixture in → byte-identical
     frame out). Keeps **judgment** (is this slice direction-fit?) with the Critic, where it
     belongs; the tool only *assembles* the evidence. Ephemeral stdout ⟹ cannot drift, no new
     tracked file, no gitignore surface. Matches the established `slice_queue_writer` binary-exit
     convention.
   - Cons: a deterministic extractor can produce a frame that is tight but shallow — "synthesis
     not concatenation" is carried by selection + compression heuristics + the hard line budget,
     not by an LLM. Mitigated by the mid-slice smoke gate (eyeball the frame on this repo).

2. **An LLM `/frame` skill that prose-synthesizes the frame.**
   - Pros: richer, genuinely synthesized prose; can weigh trajectory signals qualitatively.
   - Cons: **cannot** satisfy `test_frame_regenerates_deterministically`; non-deterministic,
     un-pinnable; risks becoming a second judge that competes with the Critic (the brief puts
     "auto-deciding direction-fit" explicitly **out of scope**); heavier per-invocation cost on
     a context that already spawns two Critic agents.

3. **Document-why-no-rule (MEPD-1 branch b) instead of minting PFS-1.**
   - Pros: less ceremony, no version bump.
   - Cons: this slice introduces a *reusable cross-skill discipline* (a mandatory context input
     to design + both Critic layers). That is exactly what a RULE-ID is for; (b) would leave the
     discipline unnamed and un-pinned, and a future skill could silently drop the frame input.

## Decision

Build **`tools/project_frame_synth.py`** as a deterministic extraction-and-render tool
(Option 1). The frame is **ephemeral** — emitted to **stdout**, never written to a tracked
file — and carries an explicit adversarial **ATTACK-LENS** preamble so it is read as a lens
to attack with, not a narrative to absorb. It renders three required sections — **Identity**,
**Trajectory**, **Impact** — under a hard `_MAX_FRAME_LINES = 40` budget, deterministically.

Wire it into three review surfaces (Option 3 rejected — mint the rule): **`/design-slice`**
consults the frame **before** designing (Step 0.5, shift-left); **`/critique`** and
**`/critique-review`** hand the frame to their spawned agents as a Step-1 input; and the
`agents/critique.md` Dim-7 probe consumes the **handed-over** frame rather than self-fetching
trajectory. This discipline is minted as **PFS-1** (`methodology-changelog.md` bump at build,
with a `test_methodology_changelog.py` entry-pin and the 5-part PMI-1 atomic version bump).

## Consequences

- New `tools/*.py` module ⟹ BC-PROJ-9 5-surface inventory fan-out (install_audit `_CANONICAL_TOOLS`,
  `test_utf8_stdout_regression._ROOT_ONLY_TOOLS`, `plugin.yaml`, INSTALL.md ×2 count literals,
  shippability row) + 5-part PMI-1 version bump.
- Three skills + one agent change behaviour ⟹ OSDG-1 drift tests (3 skills) + CAD-1 (agent) must
  stay green; installed copies forward-synced.
- The frame is **advisory**, never a gate — a synth failure must not halt `/design-slice` or
  `/critique` (binary exit: 0 success / 2 usage; never 1).
- The **tool-vs-skill** sub-choice is independently **cheap**-reversible: a `/frame` skill wrapper
  could later call the same library function without disturbing PFS-1 or the tests. The expensive,
  hard-to-reverse part is the PFS-1 rule wired into three review surfaces — that is what this ADR's
  reversibility tag reflects.
- Judgment of direction-fit remains with the Critic (Dim-7), not the synthesizer — preserving the
  Builder ↔ Critic separation.

## Reversibility

**Expensive.** PFS-1 becomes a named methodology rule with entry-pin tests, wired into
`/design-slice` + `/critique` + `/critique-review` + the Critic agent. Unwinding it means
removing the rule, the input from three skills, the agent's frame-consumption, and the pin
tests, then re-running the CAD-1/OSDG-1/PMI-1 audits — a coordinated multi-surface revert, not a
local edit. (Tagged expensive on the dominant decision; the subordinate tool-not-skill choice is
cheap as noted above.)
