---
name: user-test
description: "AI SDLC pipeline. Real-user validation gate — mockup, clickable prototype, or working slice tested with an actual person, not a simulated actor. Use when /triage or /reflect identifies UX uncertainty in a B2C or user-facing project, before /design-slice. Trigger phrases: '/user-test', 'test with real user', 'validate UX with users', 'mockup test', 'prototype test'. Skip for pure backend, internal tools, ML research, or CLI-for-engineers projects."
user_invokable: true
argument-hint: mockup | prototype | slice
---

# /user-test — Real User Validation

You are running a real-user validation gate for the AI SDLC pipeline. Goal: get an actual person's reaction to an actual artifact, then update the vault with what their behavior revealed.

## Where this fits

For B2C and user-facing projects: runs before `/design-slice` for the first few slices, and any time a slice introduces a new UX pattern.

For B2B / internal: runs at least once before heavy frontend work.

For pure backend / internal tools / ML research / engineer CLI tools: this skill should not be invoked. If user invokes it for one of these, ask if they're sure — usually it's the wrong tool.

## Mode argument

- **mockup** — static wireframe / sketch / Figma frame (cheapest)
- **prototype** — clickable but not functional (medium)
- **slice** — actual working slice in the user's hands (most expensive, most honest)

Default if no argument: ask the user which mode fits.

## Your task

### Step 1: Confirm fit

Ask: "Is this a B2C or user-facing project where a real user's reaction will surface things actor simulation misses?"

If no → suggest `/critique` instead and stop.

If yes → proceed.

### Step 2: Help prepare the artifact

For **mockup**:
- Suggest tools (Figma, hand sketch, simple HTML mockup, ASCII wireframe)
- If user wants you to produce an HTML mockup: keep it focused on the ONE flow being tested

For **prototype**:
- Suggest tools (Figma prototype, simple Vue/React with mocked data, ProtoPie)
- Scope tightly to the flow being tested

For **slice**:
- Confirm a slice is actually built and runnable
- Help the user prepare a usage scenario / task script

### Step 3: Suggest 3–5 observation questions

Questions must be about **behavior**, not opinion. Examples:

GOOD (behavior):
- "Show me how you'd add a new expense from this screen."
- "You see this notification — what would you do next?"
- "Find the receipt for last Tuesday's coffee."

BAD (opinion):
- "Do you like this design?"
- "How does this look to you?"
- "Would you use this?"

Users are unreliable narrators of their own behavior. Watch what they DO, not what they SAY.

### Step 4: Frame the session

Tell the user:
- Single user per session (group sessions cheap-feel-honest, are not honest)
- Multiple sessions (1 user × 5) > one big session
- Don't lead the user. If they ask "what should I do?" say "What would you do?"
- Don't fix bugs or explain. If they get stuck, that's data.

### Step 5: After the session — capture findings

Create `architecture/user-tests/<test-name>.md`:

```markdown
# User test: <name>

**Mode**: mockup | prototype | slice
**Date**: <YYYY-MM-DD>
**User**: <pseudonym, role, relevant context>
**Artifact tested**: <link or description>
**Tasks given**: <the 3-5 things they were asked to do>

## Observations

### Surprised
<things user did that we didn't predict — assumptions wrong>

### Ignored
<things in the artifact user didn't notice or use — scope bloat candidate>

### Wanted
<things user expected that aren't there — missing feature OR scope creep, judgment call>

### Stuck
<friction points — where user paused, got confused, gave up>

## Risks surfaced
- <new risk to add to risk-register.md>

## Recommended next action
- proceed to /design-slice as planned
- revise design based on findings (specify what)
- new slice targeted at the friction (specify what)
- back to /discover (concept assumption was wrong)
```

### Step 6: Update risk register

For each "Surprised" or "Stuck" finding, evaluate if it's a new risk. Add to `architecture/risk-register.md` with reversibility tag.

### Step 7: Tell user what's next

Based on findings:

- Clean session, no surprises → `/slice` (or proceed with planned design)
- Significant friction in flow → revise design before `/slice`
- Concept assumption challenged → back to `/discover`
- Critical UX miss → new slice targeted at the miss

## Critical rules

- DO NOT skip or fake. If a real user isn't available, say so. Don't simulate.
- DO NOT lead the user. They go where they go.
- DO NOT count "they liked it" as validation. Behavior matters; opinion doesn't.
- DO NOT batch user tests with feature reviews. One artifact, one user, one session.
- DO escalate multi-device tests: features for >1 user / >1 device require the slice to be tested on >1 instance simultaneously.

## Anti-pattern

Skipping `/user-test` because "the actors file already says what users want." Actor files are starting hypotheses, not validated truth. Real users surprise you in ways no actor specification predicts.

## Next step

- Clean findings → `/slice` (or `/design-slice` if slice already exists)
- Heavy findings → `/discover` (concept revision)
- New friction-targeted slice needed → `/slice`
