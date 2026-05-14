# AI SDLC Tutorial

A practical guide. Pick your situation from the decision tree, jump to the matching worked example, follow it.

---

## How to use this tutorial

1. Read **Quick decision tree** — picks your mode + first skill
2. Read **the worked example** matching your situation (don't read all of them)
3. Reference **Common scenarios** for one-off situations
4. Skim **Anti-patterns** so you avoid the obvious traps

If you only have time for one section: read the **decision tree** + the worked example for your project type.

---

## Quick decision tree

```
Do you have existing code (brownfield) or starting from scratch (greenfield)?
│
├─ GREENFIELD (no code yet, or trivial throwaway code)
│  │
│  ├─ One-off script / prototype / personal MVP / data exploration
│  │  → MINIMAL mode
│  │  → Start: /triage MINIMAL "<description>"   (or plain /triage for interactive)
│  │
│  ├─ B2C product / internal tool / B2B SaaS
│  │  → STANDARD mode (the default)
│  │  → Start: /triage STANDARD "<description>"   (or plain /triage)
│  │
│  └─ HIPAA / PCI / SOC2 / GDPR / public API with external SLAs
│     → HEAVY mode
│     → Start: /triage HEAVY "<description>"     (or plain /triage)
│
├─ BROWNFIELD (existing codebase you want to adopt the pipeline into)
│  → Start: /adopt [MINIMAL|STANDARD|HEAVY]
│  → /adopt reads the code, reverse-engineers initial vault, generates brownfield-aware CLAUDE.md
│  → Use INSTEAD of /triage, not in addition
│
└─ ADDING A FEATURE to an existing AI SDLC project (vault already exists)
   → DON'T re-run /triage or /adopt — vault already exists
   → Start: /slice "<feature in verb-object form>"
```

### Shortcut vs interactive

`/triage` always asks at minimum: what are you building, what's the biggest unknown, team/timeline. Those build the risk register and aren't optional.

The mode-selection questions (audience, compliance) are skipped if you pre-declare with `/triage MINIMAL`, `/triage STANDARD`, or `/triage HEAVY`. Use the shortcut when you're sure of the mode; use plain `/triage` when you want guidance.

If unsure between Minimal and Standard: **pick Standard**. If a real user will ever see the output, pick Standard.

If unsure between Standard and Heavy: **pick Standard**. Upgrade to Heavy only when a specific regulation or external SLA forces it.

If you pre-declare a mode that doesn't fit (e.g., `MINIMAL` for a HIPAA project), `/triage` will flag the mismatch and ask you to confirm or switch.

---

## Graphify is installed by `/triage` and `/adopt`

Both openers install graphify's Claude Code integration (PreToolUse hook + git hooks + initial graph build). From that point on:

- **PreToolUse hook** nudges Claude to read `graphify-out/GRAPH_REPORT.md` (one-page digest of god nodes + communities + surprising connections) before Glob/Grep
- **Post-commit git hook** auto-rebuilds the graph after code changes
- `$PY -m graphify query`, `reachable --from=`, `blast-radius --from=` are available anytime for structured queries (skills also use inline `networkx.shortest_path` for `path A B` since the CLI lacks it)
- **Multi-modal ingestion**: `from graphify.ingest import ingest` pulls research papers, design docs, interview recordings into the graph (the slash form `/graphify add <url>` is also available inside Claude Code chat)

Sub-second structural queries against a pre-built graph instead of re-scanning files. Every skill below leverages this. Full details: [graphify-integration.md](graphify-integration.md).

## What skill to use when (cheat sheet)

| Situation | Skill |
|-----------|-------|
| Starting fresh (greenfield) | `/triage` |
| Adopting into existing codebase (brownfield) | `/adopt` |
| Re-scoping an existing project | `/triage --re-triage` |
| Session start / orientation / returning after time away | `/status` |
| Fixing a non-trivial bug | `/repro` → `/slice` → ... |
| Generating an audit-grade commit after a slice | `/commit-slice` |
| Mapping concept + users + tech | `/discover` |
| Worried about a third-party API or platform behavior | `/risk-spike` |
| About to commit to a UX in a B2C product | `/user-test mockup` |
| Heavy mode only — building the upfront architecture | `/heavy-architect` |
| Defining the next thing to build | `/slice` (with or without description — it actively recommends candidates) |
| Designing what the slice needs | `/design-slice` |
| Want a second AI to attack your design | `/critique` |
| Time to write code | `/build-slice` |
| Testing on a real device / user / data | `/validate-slice` |
| Capturing what the slice taught you | `/reflect` |
| Pre-commit; checking vault matches code | `/drift-check` |
| Heavy mode only — periodic deep reconciliation | `/sync` |
| Vault is bloated; complexity is creeping | `/reduce` |

---

## Worked example 1: Minimal mode — building a personal CLI tool

### Situation

You're building a CLI tool that scans your photo library and generates a CSV of duplicates. Solo project, no users besides you, no compliance, ~1 week of work.

### Mode: Minimal

### Walkthrough

**Step 1 — Triage**

```
You: /triage "CLI tool to find duplicate photos in my library and emit a CSV report"

Claude: One sentence — got it. Few questions:
1. What are you building? (got it from your message)
2. Who uses this? Just you?

You: just me

Claude: 3. Biggest unknown — is it accuracy of duplicate detection, performance on large libraries, or something else?

You: accuracy. similar photos vs duplicates is the gray zone.

Claude: 4. Compliance constraints? (probably none for personal tool)

You: none

Claude: 5. Solo, what timeline?

You: weekend project

Claude: Mode: Minimal. Rationale: solo dev, MVP, one-off. Standard would be overkill.

Risk register:
| ID | Risk | Reversibility | Spike? |
|----|------|---------------|--------|
| R1 | Perceptual hash accuracy on similar-but-different photos | irreversible-if-wrong (ranking determines tool value) | YES — try imagehash on 20 known-similar pairs first |

Pipeline path: /risk-spike R1 → /discover → /slice → /design-slice → /build-slice → /validate-slice → /reflect → loop

I'll create:
- architecture/triage.md
- architecture/risk-register.md
- ./CLAUDE.md (tiny — ~20 lines; hard rule + vault discipline; keeps me on the pipeline next session)

Run /risk-spike R1 next.
```

**Step 2 — Risk-spike**

```
You: /risk-spike R1

Claude: Spike target: perceptual hash (imagehash library) accuracy on similar-but-different photos.

Test: 20 known pairs (10 true duplicates, 10 similar-but-different — different crops, edits, frame grabs).
Code: ~15 lines using imagehash.phash.
Environment: this machine, sample photos.

[Generates throwaway script, runs it]

Result:
- True duplicates: distance ≤ 5 (10/10 detected)
- Similar-but-different: distance 8-25 (separable from duplicates)
- Threshold of 6 cleanly separates the two.

Decision: GO.
Caveat: tool should expose threshold as a CLI flag — different libraries may need tuning.

Wrote: architecture/spikes/spike-phash.md
Updated: risk-register.md (R1 → RETIRED)

Next: /discover (or skip to /slice — risk register is clean now)
```

**Step 3 — Skip /discover, go straight to /slice**

In Minimal mode for a tiny project, /discover can be one paragraph in concept.md or skipped entirely if the triage was clear enough.

```
You: /slice "scan a folder and write CSV of duplicates"

Claude: Slice 001 candidate: scan-folder-emit-csv

Acceptance criteria:
1. CLI accepts a folder path argument
2. Walks recursively, processes JPEG/PNG/HEIC
3. Computes perceptual hash for each
4. Groups by hash distance ≤ threshold (default 6)
5. Emits CSV: cluster_id, file_path, hash

Verification:
- Run on test folder of 50 photos with 5 known duplicate clusters → CSV has 5 cluster_ids with multiple rows

Must-not-defer:
- Handle unreadable files (skip + log, don't crash)
- Show progress on large libraries (≥100 files)

Out of scope:
- GUI
- Auto-deletion
- Cloud sync

Mid-slice smoke: process 10 files, dump output to terminal, eyeball.

Wrote: architecture/slices/slice-001-scan-folder-emit-csv/mission-brief.md
Run /design-slice next.
```

**Step 4 — Design-slice (lightweight in Minimal)**

```
You: /design-slice

Claude: Slice 001 design (Minimal — short).

What's new:
- src/scan.py — folder walking + hash
- src/cluster.py — group by hash distance
- src/cli.py — argparse + orchestration

Reused: imagehash, Pillow, csv (stdlib).

Decisions made (one ADR):
- ADR-001: Use imagehash.phash (validated by spike-phash). reversibility: cheap (can swap to dhash).

Wrote: architecture/slices/slice-001-scan-folder-emit-csv/design.md, decisions/ADR-001.md
Run /build-slice next. (Critique skipped — Minimal mode, trivial slice.)
```

**Step 5 — Build, validate, reflect**

```
You: /build-slice

[Plan mode, code, mid-slice smoke, pre-finish gate]

You: /validate-slice
[Run on 50-photo test folder, eyeball output, all 5 clusters detected correctly]

You: /reflect
[1-paragraph reflection: validated; discovered HEIC handling needed pyheif; deferred: parallel processing for >1000 file libraries]
```

### Total time

~3-4 hours including the spike, build, validation. The pipeline added maybe 30 minutes of overhead vs "just write the script" — but the spike saved a night of fighting hash thresholds.

### Files created

```
architecture/
  CLAUDE.md
  triage.md
  risk-register.md
  spikes/spike-phash.md
  decisions/ADR-001-phash-library.md
  slices/slice-001-scan-folder-emit-csv/
    mission-brief.md
    design.md
    build-log.md
    validation.md
    reflection.md
./CLAUDE.md  (redirect)
src/  (your code)
```

### When NOT to use Minimal mode

- Multi-user features
- Anything with auth that protects others' data
- Anything you'd be embarrassed to ship if it crashed
- Code that other people will maintain

For those: Standard.

---

## Worked example 2: Standard mode — building a B2C web app

### Situation

You're building a household expense tracker — mobile-friendly web app, two users per household share data, subscription tier later. ~3 months solo dev.

### Mode: Standard

### Walkthrough (compressed)

**Step 1 — Triage**

```
You: /triage "household expense tracker — web app, two users share data, subscription later"

Claude: [5 questions, one at a time]

Mode: Standard. Rationale: B2C consumer product, real users will see UI, multi-user data sharing.

Risk register:
| R1 | Cross-user data sharing model (single account vs separate accounts with shared collection) | irreversible | YES — affects auth + DB design |
| R2 | Receipt OCR accuracy at app launch (or skip MVP?) | expensive | Try Tesseract on 30 sample receipts before committing |
| R3 | Subscription billing integration choice | expensive | Stripe vs Paddle, defer until needed |

Pipeline path: /risk-spike R1 R2 → /discover → /user-test mockup → /slice → loop

Wrote: triage.md, risk-register.md, CLAUDE.md (architecture + redirect)

Run /risk-spike R1 next.
```

**Step 2 — Spike both HIGH risks**

```
You: /risk-spike R1

Claude: Spike: data-sharing model.

Test: prototype both approaches with toy data.
- Approach A: shared account with 2 sessions
- Approach B: 2 accounts linked via "household" entity

Result: Approach B is cleaner for permissions, future-proof for >2 users, allows individual login. GO with B.

Caveat: requires "invitation" flow (account 1 invites account 2 → joins household). Adds a slice.

You: /risk-spike R2

Claude: Spike: Tesseract OCR on 30 sample receipts.

Result: 60% extract amount correctly; 40% wrong (handwritten amounts, faded ink). NOT good enough as primary entry method.

Decision: NO-GO for OCR-as-default. CONDITIONAL for OCR-as-assist (user reviews).

Updated risk register; OCR moved to "later, if at all."
```

**Step 3 — Discover**

```
You: /discover

Claude: [3 areas, one at a time]

WHAT: 
[discussion]
Concept written.

WHO:
- Primary: household member (adds expenses, views shared totals)
- Secondary: household admin (the person who created household, can invite/remove members)
[Inline in concept.md, NOT separate actor files — Standard mode is thin vault]

CONSTRAINTS:
- Stack: Next.js + Postgres (you wanted React; Next.js gives you full-stack with one codebase)
- Hosting: Vercel + Supabase
- Decisions captured as ADRs (no separate tech-brief.md — thin vault)

First slice candidate: "household-creation-and-invitation" — exercises auth, multi-user, the household entity (validating R1's redesign).

Wrote: concept.md, decisions/ADR-002-stack.md, ADR-003-data-sharing-model.md
B2C, UX-critical → recommend /user-test mockup next.
```

**Step 4 — User-test mockup**

```
You: /user-test mockup

Claude: For the first slice (household creation + invitation), what mockup form?
[discussion]

Suggested: hand-sketch the 3 screens (login, create-household, invite-member) — fastest.

Observation questions:
1. "Show me how you'd invite your spouse to track expenses with you"
2. "You got an invitation email — show me what you'd do"
3. "After joining, how would you check who's in the household?"

[You sketch, do session with one real user]

[After session]
Findings:
- SURPRISED: User expected "Create household" to ask for household NAME ("our family"). Mockup just said "Continue". → Add name field.
- IGNORED: Long welcome paragraph — ignored entirely. → Cut it.
- WANTED: A way to undo invitation. → Add cancel-invitation in slice 2.
- STUCK: Confused about whether they were "joining" or "creating" — verb mattered. → Clearer button labels.

Wrote: user-tests/test-001-household-flow.md
Risks: R4 added (terminology around joining vs creating).

Recommend: revise mission brief for slice 1 (add household name, cleaner copy), then /slice.
```

**Step 5 — Slice → design-slice → critique → build → validate → reflect**

```
You: /slice "household creation and invitation"

[Mission brief written; incorporates user-test findings: household name field, clear copy, undo invitation in next slice]

You: /design-slice

[Just-enough spec; references code locations like "see src/auth/household.ts" instead of duplicating types]
[ADR-004: invitation token strategy (cheap reversibility — magic link with 24h expiry)]

You: /critique

[Spawns Critic agent]
Critic finds:
- B1: ADR-004 says invitation tokens have 24h expiry, but no DB cleanup mechanism specified. → expired tokens accumulate.
- M1: Re-invitation flow not specified (what if user invites same email twice?)
- m1: "Household name" field has no length limit specified.

You address B1 (add DB cleanup task), M1 (specify "re-invitation cancels previous"), defer m1 to next slice.

You: /build-slice

[Plan mode → user approval → execute]
[Mid-slice smoke at 50%: signup → create household → see household name on dashboard. Pass.]
[Pre-finish gate: all ACs pass, must-not-defer addressed, /drift-check clean.]

You: /validate-slice

[Real test: two browser windows, two emails, full invitation flow]
PASS — all 5 ACs verified with screenshots in validation.md.

You: /reflect

Validated: invitation flow works for normal case; magic links work; household name appears on dashboard.
Corrected: design.md said magic link is sent via Vercel KV; reality used Supabase Edge Functions (cleaner). Updated design.md.
Discovered: re-invitation case wasn't in mission brief, but Critic caught it (M1). Added to lessons-learned: "in invitation/sharing slices, always think about the re-invite case."
Critic calibration: B1 VALIDATED (we hit token cleanup mid-build). M1 VALIDATED (came up in real test). m1 NOT YET (deferred).

Run /slice for next cut: probably "view-shared-expenses" or "invitation-management".
```

### Total time per slice

~4-6 hours per slice in Standard mode. Critique adds ~30 min, validation adds ~30-60 min. Worth it — multiple post-launch bugs avoided.

### Where Standard differs from Minimal

- /critique runs every slice (skipped in Minimal)
- /user-test runs before first UX-critical slice
- Mission briefs are stricter
- Pre-commit /drift-check is installed

---

## Worked example 3: Heavy mode — building a HIPAA-compliant patient intake API

### Situation

You're building an API for clinics to submit patient intake data. PHI involved. SOC2 + HIPAA. Three-person team. 6-month delivery.

### Mode: Heavy

### Walkthrough (more compressed — Heavy is comprehensive but pattern is clear)

**Step 1 — Triage picks Heavy**

```
You: /triage "patient intake API — clinics submit PHI for our processing pipeline"

Claude: [5 questions]
- Compliance: HIPAA + SOC2
- Team: 3 + auditors
- Public API: yes (clinics integrate)

Mode: HEAVY. Rationale: PHI + multiple compliance frameworks + external API consumers + audit trail required.

Heavy pipeline path:
/triage → /discover (full role-play per actor) → /risk-spike all → /heavy-architect → /user-test (clinic UX) → /slice loop with mandatory /critique + sign-off
+ /sync every 5-10 slices
+ /reduce mandatory every 5 slices
+ /drift-check pre-commit

Risk register includes compliance-specific risks (audit logging, encryption-at-rest, BAA agreements with subprocessors).
```

**Step 2 — Discover (full)**

```
You: /discover

[Claude does FULL role-play per actor:]
- Clinic admin: first-time setup, integration test, bulk upload
- Clinical user: single patient submission, error correction, status check
- Auditor: data access log review, BAA compliance check
- Patient (indirect): data access request, deletion request

[Produces concept.md + tech-brief equivalent + actor files in actors/ — Heavy mode allows separate actor files for compliance]
```

**Step 3 — Risk-spike ALL HIGH risks (mandatory in Heavy)**

```
You: /risk-spike all

[For each HIGH risk:]
- Encryption-at-rest with KMS-managed keys: spike with sample PHI, verify KMS audit log captures access
- Audit logging coverage: spike a sample request, verify all access points logged
- BAA-required subprocessors: list all third parties that touch PHI; verify BAAs in place

[Decisions tagged with reversibility; some decisions blocked pending legal sign-off]
```

**Step 4 — Heavy-architect**

```
You: /heavy-architect

Claude: Heavy-mode comprehensive vault. Estimated: 1-2 days.

[Confirms scope with user]
[Produces:]
- 8 components: API gateway, intake service, validation service, persistence service, audit logger, encryption manager, notification service, admin service
- 12 contracts: external API spec + internal service contracts
- 5 schemas: Patient, IntakeRecord, AuditEvent, ClinicAccount, Subprocessor
- threat-model.md: STRIDE per component, with PHI-specific concerns
- cost-estimation.md: per-component costs at 100, 1K, 10K clinics
- requirements.md: functional, by actor
- non-functional.md: latency targets, uptime SLA, encryption requirements, retention policies
- diagrams.md: system overview, sequence diagrams for 5 critical flows, ER, deployment

$PY -m graphify vault built.

Run /user-test next (clinic admin onboarding mockup), then /slice slice-001.
```

**Step 5 — Slice loop with mandatory critique + sign-off**

```
You: /slice "intake-api-receive-and-validate"

[Mission brief; references components from heavy-architect's vault]

You: /design-slice

[Updates components/intake-service.md, contracts/clinic-to-intake.md, schemas/IntakeRecord.md INLINE — vault stays in sync]
[2 new ADRs created]

You: /critique

[Critic spawned with FULL Heavy-mode context — components, contracts, threat-model, NFRs]
[Returns 3 blockers + 5 majors + 4 minors]
[Builder addresses blockers/majors]
[HUMAN reviewer signs off in critique.md (Heavy mode requirement)]

You: /build-slice

[Plan mode → user approval → execute]
[Mid-slice smoke: sample intake POST → audit log entry verified, encryption verified]
[Pre-finish gate: ALL ACs + must-not-defer + drift-check + test coverage report (Heavy req)]

You: /validate-slice

[Reproducible commands captured, timestamped]
[QA reviewer signs validation.md]

You: /reflect

[Updates components/contracts/schemas inline — Heavy vault stays current]
[Compliance trail in reflection: which audit requirements this slice satisfied]
```

**Step 6 — Maintenance (Heavy adds two more)**

```
[Every 5 slices:]
You: /reduce

[Mandatory in Heavy — complexity audit; reduces accumulated layers]

[Every 5-10 slices, or after major refactor:]
You: /sync

[Bidirectional reconciliation — regenerates components/contracts/schemas from code, detects drift on threat model, ADRs, NFRs]
[sync-log.md updated for audit trail]
```

### Heavy mode time

~6-8 hours per slice (vs 4-6 in Standard) due to mandatory critique + sign-off + reproducible validation. /heavy-architect is 1-2 day upfront cost. /sync + /reduce add maintenance overhead but prevent vault rot.

### When NOT to use Heavy mode

- "We might need compliance later" — start Standard, /triage --re-triage to Heavy when compliance is real
- Internal tools with no PII/PHI
- Prototypes (even compliance-bound projects often start Standard for prototype)

---

## Worked example 4: Adding a feature to an existing AI SDLC project

### Situation

Your B2C expense tracker (from Example 2) is live. Users have requested CSV export. You want to add it.

### Mode: existing project (whatever mode it's in)

### Walkthrough

```
You: /triage --re-triage  (optional — check if mode needs to change)

Claude: Existing triage.md found. Mode: Standard. No mode change needed for "add CSV export."

You: /slice "export-expenses-as-csv"

Claude: Slice candidate: export-expenses-as-csv

Looking at risk register: no new HIGH risks for this. Looking at recent reflections: no relevant patterns.

Acceptance criteria:
1. UI button "Export to CSV" on expenses page
2. CSV includes date, amount, category, description, payer
3. Filename: expenses-{household}-{date-range}.csv
4. Filtered: respects active date range filter
5. Privacy: only household-member-visible data (no other household leakage)

Verification: Real user export, open in Excel, verify data matches what's on screen.

Must-not-defer:
- Authorization: only household members can export their household's data
- Filename sanitization (no path traversal)

Out of scope:
- Excel format (CSV only)
- Email export
- Scheduled exports

Mid-slice smoke: export 5-row test household, open in Excel, eyeball.

Wrote mission-brief. Run /design-slice.

[Continue: design-slice → critique → build-slice → validate-slice → reflect]
```

### Key thing about adding features

**Don't run /discover or /heavy-architect again** — those are project-opening skills. For features, jump to /slice. The vault already exists; the new slice's mission-brief.md references existing vault items.

If the feature is BIG (touches new auth model, new external integration, new data model): consider running /risk-spike first.

If you discover the feature requires architectural change: bump it to multiple slices, OR /triage --re-triage if scope shift is significant.

---

## Worked example 5: Recovery — Claude already built code without slices

### Situation

You ran a session where Claude built a feature directly without /slice. Now you want to back-fill the discipline.

### Walkthrough

```
You: I built the receipt-upload feature without using the pipeline. Can we retroactively add a slice?

Claude: Yes. Three options:

A) **Retroactive slice** (light): create a slice folder with mission-brief reverse-engineered from the code, validation.md from manual testing, reflection.md noting the bypass. Low effort, captures decisions.

B) **Slice + critique** (medium): same as A, plus run /critique against the existing code (Critic reads the code, not a design). Catches gaps post-hoc.

C) **Tear-down slice** (heavy): treat the existing code as a draft; run /slice → /design-slice → /critique → re-implement properly. Use only if quality concerns warrant.

For most cases: option A.

Want me to do A?

You: yes

Claude: [Reads the code touched by the change]
[Reverse-engineers acceptance criteria from observed behavior]
[Creates slice folder with mission-brief, validation (manual), reflection noting "retroactive — bypassed live pipeline at <date>"]
[Logs to architecture/changelog.md: "<date>: bypass acknowledged, retroactive slice slice-NNN-receipt-upload created"]
```

### Why this matters

The vault should reflect what was built, even if built outside the pipeline. Otherwise the next slice's design is built on incomplete vault context.

### How to prevent next time

The auto-generated `./CLAUDE.md` (project root, ~20 lines) is supposed to catch this. If it's being ignored:
- Verify `./CLAUDE.md` exists at project root and is the small template (if it's gotten large, regenerate it — big CLAUDE.md gets skimmed)
- Verify it's being loaded into context (Claude Code auto-loads project-root CLAUDE.md)
- Verify the user isn't bypassing without logging — the hard rule requires asking first

---

## Common scenarios — quick reference

### "I want to start a new project"
→ `/triage "<one sentence>"`

### "I want to add a feature to existing project"
→ `/slice "<feature in verb-object form>"` — OR just `/slice` with no description; the skill will actively recommend top candidates based on risk register, deferrals, discoveries, and unbuilt scope. You don't need to know what's next best — Claude will suggest.

### "I don't know what to build next"
→ `/slice` with no description. It will scan the risk register, last 3 reflections' Deferred / Discovered items, aggregated lessons, and concept scope; produce a ranked top 3-5 candidates with rationale; recommend #1 with "why this one." You accept, pick an alternative, or describe your own (which it'll validate).

### "I think the design is wrong mid-build"
→ STOP. Tell the user: "Design says X, code reality requires Y. Stop and revise design, or proceed with documented deviation?" If revise: `/design-slice` updates → `/critique` re-runs on the changes → resume `/build-slice`.

### "Validation failed — what now?"
→ Classify the failure:
- Implementation bug → fix code, re-run `/validate-slice`
- Spec gap → don't fix; let `/reflect` capture; next `/slice` addresses
- Reality surprise → log to risk-register immediately; `/reflect` decides next move

### "Vault has drifted significantly"
→ Standard / Minimal: `/drift-check` → resolve interactively
→ Heavy: `/sync` for full reconciliation

### "Project complexity is creeping"
→ `/reduce` for an audit, then a reduction slice if needed

### "Can I find something from a past slice? (We have 150+ slices)"
→ Check `architecture/slices/_index.md` first. It has:
  - Active slices (currently in progress)
  - Most recent 10 archived with one-line summaries
  - Aggregated lessons from recent reflections
  - Pointer to `archive/_index.md` for the full chronological catalog

→ **Semantic search across ALL archived slices**: `$PY -m graphify query "past lessons about <topic>"` — this is how `/design-slice` and `/critique` surface lessons from slice-008 even when you're on slice-158
→ For a specific archived slice: `architecture/slices/archive/slice-NNN-<name>/` (direct path works)
→ Full-text search: `grep -r "<keyword>" architecture/slices/archive/`
→ By ADR → the ADR's `slice:` frontmatter field tells you which slice locked it

### "Critic keeps missing the same kind of issue"
→ That's the classic signal to run `/critic-calibrate`. It reads the last 15 reflections' "Missed by Critic" sections, patterns the misses, and proposes specific prompt additions to `critique/SKILL.md`. You review and accept; nothing is auto-applied. Running every 10-20 slices closes the feedback loop systematically.

### "Did this slice break something a past slice established?"
→ `/validate-slice` runs the **shippability catalog** at pre-finish — every past slice contributes ONE critical-path test (added by `/reflect`). If any fail, the current slice silently broke past work; fix or explicitly defer. Catches regressions without needing a full CI pipeline.

### "I just started a session on an existing project and I'm lost"
→ `/status`. One command, ~60-line summary: mode, active slice + stage + next action, risk exposure, regression health, Critic calibration status, top 5 aggregated lessons. Reads `architecture/slices/<active>/milestone.md` for explicit stage + next-action instead of deriving from file existence.

### "My session died mid-slice — where am I?"
→ `/status` reads `milestone.md` (rolling state file updated by every skill). The "On resume" section tells Claude exactly where to pick up: last completed action, current work, files being edited, specific next immediate step. Designed to survive session death + context clears.

### "This slice is just a CSS tweak — do I need /critique?"
→ If `/slice` marked the slice tier as `low` AND nothing in the slice touches auth / contracts / data model / multi-device / external integrations: `/critique` skips with a message and updates `milestone.md`. No ceremony for trivial work. Override with `/critique --force` if you want it anyway. Medium/high tier always runs Critic. Heavy mode always runs regardless of tier.

### "I need to fix a bug"
→ `/repro "<issue description>"` first. It writes a failing test that reproduces the bug, confirms it actually fails, adds it to `shippability.md`, then hands off. Now run `/slice "fix <issue>"` — the fix slice's AC is "make the test pass," and the test lives in the regression catalog forever so this bug can't come back silently. Skip `/repro` only for typos/one-liners.

### "I finished a slice — how do I write a good commit?"
→ `/commit-slice`. Pulls from mission-brief / build-log / validation / ADRs and produces a conventional-commit-style message with slice folder reference, ACs passed, Critic blockers addressed, ADR IDs, shippability entry. Use `/commit-slice --merge` (per BRANCH-1, methodology v0.35.0) to commit on the current slice branch + no-ff merge back to the resolved default branch + safe-delete the slice branch (with explicit confirmation at each checkpoint).

### "Compliance requirement just emerged"
→ `/triage --re-triage` → mode upgrade to Heavy → `/heavy-architect` (yes, even mid-project — it can read existing slices and produce comprehensive vault retroactively, though some component descriptions become reverse-engineered)

### "I want to skip the pipeline for a quick fix"
→ Allowed for: typos, single-line tweaks, comment changes, single-test additions
→ Not allowed for: feature work, refactors, contract changes, multi-file edits
→ For borderline: ask Claude to log the bypass in `architecture/changelog.md`

### "Critic is being a rubber stamp / always says 'no issues'"
→ The Critic prompt is too mild. Edit `~/.claude/skills/critique/SKILL.md` to require at least one specific finding per dimension OR explicit "no blockers" statement. Track in `/reflect`'s Critic calibration section.

### "Critic is being a nitpicker / blocking trivial things"
→ Tune severity thresholds. Make sure Critic's prompt distinguishes blocker (must fix before build) from minor (log if cheap). If still bad: dispute findings inline in critique.md with rationale.

### "I'm running out of context mid-build"
→ Mission brief + plan mode are designed for this. Start a new session, run `/build-slice` again — it reads the mission brief and any partial build-log, picks up where it left off. If plan mode revision is needed: re-enter plan mode, get user approval on new plan.

---

## Anti-patterns and gotchas

### Anti-pattern 1: Auto-creating component files in Standard mode

**Symptom**: `/design-slice` produces `components/X.md` and `contracts/Y.md` files in a Standard-mode project.

**Why it's bad**: Thin vault is the Standard default. Component files duplicate what code already shows; they drift; they're maintenance burden.

**Fix**: tell Claude: "We're in Standard mode (thin vault). The design.md should reference code locations, not create separate component files." If the SKILL.md is correctly configured, this shouldn't happen — but verify by reading `architecture/triage.md` shows `mode: Standard`.

### Anti-pattern 2: Skipping /critique because "the design is obvious"

**Symptom**: User or Claude wants to skip critique to save time on a "trivial" slice.

**Why it's bad**: The "trivial" ones are where you stop watching. Critic catches the auth gap on the trivial endpoint that exposes data.

**Fix**: only skip /critique in Minimal mode AND for slices with no new auth, no new contracts, no new external dependencies. When in doubt: run it. ~5 minutes of Critic vs hours of bug.

### Anti-pattern 3: Letting Claude bypass the pipeline without confirming

**Symptom**: User asks Claude to "fix this bug" or "add this feature" and Claude jumps to editing code.

**Why it's bad**: This is the "ditch the pipeline" failure. Discipline collapses; vault rots.

**Fix**: project-root `./CLAUDE.md` (small — ~20 lines) has the hard rule ("before editing code beyond trivial, check for active slice; if none, ASK"). Verify the file exists and is concise. Big CLAUDE.md gets skimmed — keep it small. If Claude still bypasses: explicitly ask "did you check for an active slice?"

### Anti-pattern 4: Treating the vault as documentation for new humans

**Symptom**: Vault grows comprehensive component descriptions, architectural diagrams, "system overview" docs for hypothetical new readers.

**Why it's bad**: That's not what the vault is for in Standard mode. It's the AI's project memory — decisions, risks, slice history. Documentation for humans is a different artifact (and probably best generated on demand from code).

**Fix**: principle 5 (thin vault) — review what's in the vault. If it's "what code does," delete it. If it's "why we decided X," keep it.

### Anti-pattern 5: Running /heavy-architect in Standard mode

**Symptom**: User wants "a real architecture" upfront, runs `/heavy-architect` in a Standard project.

**Why it's bad**: Produces 30+ files of comprehensive vault that will drift, won't be maintained, and weren't needed.

**Fix**: `/heavy-architect`'s prerequisite check should refuse — it asks "are you sure this should be Heavy mode? If so, /triage --re-triage." If you legitimately need it: re-triage to Heavy.

### Anti-pattern 6: One slice for "the whole feature"

**Symptom**: A slice with 12 acceptance criteria and a 3-day estimate.

**Why it's bad**: Defeats the slice model. You won't get mid-slice smoke gates that work; validation becomes fuzzy; reflection becomes "we built a lot."

**Fix**: split. Each slice ≤5 ACs, ≤1 day. If splitting produces a slice with no user-visible value, the feature was probably 3 features mashed together.

### Anti-pattern 7: Reflection as victory lap

**Symptom**: Reflections that say "all ACs passed, design was correct, no issues."

**Why it's bad**: Teaches nothing. Next slice doesn't benefit. Critic calibration data isn't generated.

**Fix**: enforce honesty discipline. Reflections must populate Validated / Corrected / Discovered / Deferred sections explicitly. If Discovered is empty across multiple slices: either you're not learning, or not capturing.

### Anti-pattern 8: Drift-check disabled because it's "annoying"

**Symptom**: Pre-commit hook disabled or bypassed with `--no-verify`.

**Why it's bad**: Drift compounds silently. Six months later the vault claims sendgrid; reality is resend.

**Fix**: if the hook is too slow, use `--fast` mode (target <1 second on thin vault). If the hook is too noisy, the vault probably has bad assumptions about code paths — fix the vault. Disabling the hook is rarely the right answer.

---

## FAQ

### Q: How thin is the thin vault, really?

For a 6-month Standard-mode project with ~30 slices, expect:
- ~30 ADRs (decisions/)
- ~10-20 risks ever in the register (most retired by spike or validate)
- ~30 slice folders (each 4-6 files)
- ~5 user-test files (B2C only)

Total: ~150-200 files, mostly small. Versus the comprehensive (Heavy) vault which can hit 300-500 files for the same project.

### Q: When do I switch from Minimal to Standard?

When ANY of:
- Real user (not you) will see the output
- Multi-user data sharing
- Auth that protects others' data
- Code other people will maintain

Re-run `/triage --re-triage`. Existing vault content preserved.

### Q: What if I disagree with the Critic?

Dispute it in `critique.md`. Each finding has a "Builder response" line — write your rationale. The Critic doesn't have veto power; the Builder owns the decision. But:
- Disputed findings should have specific rationale (not just "I disagree")
- Track in /reflect's Critic calibration whether reality validated you or the Critic
- Pattern: Builder consistently overrides Critic on a dimension → consider tuning the Critic prompt

### Q: How do I integrate the project CLAUDE.md with my existing CLAUDE.md?

`/triage` checks first:
- If `./CLAUDE.md` exists: appends a small (~10 line) section with the hard rule + pointer. Doesn't overwrite.
- If `./CLAUDE.md` doesn't exist: creates a small (~20 line) file with mode, hard rule, and vault discipline.

No separate `architecture/CLAUDE.md` — one small file at project root. Detailed skill guidance lives in each skill's `SKILL.md` (loaded when the skill runs, not always in context).

### Q: How do I know if I need /sync vs /drift-check?

| You're in | Use |
|-----------|-----|
| Minimal or Standard mode | `/drift-check` only |
| Heavy mode, pre-commit | `/drift-check --fast` |
| Heavy mode, periodic audit | `/sync` |
| Heavy mode, after major refactor | `/sync` |
| Heavy mode, /drift-check found 10+ issues | `/sync` (likely systematic drift; needs deeper reconciliation) |

### Q: My project started in Minimal but is growing — when do I bump to Standard?

Run `/triage --re-triage` when:
- You start sharing the codebase with others
- A real user (not you) will use the output
- The risk register has more than 3 active items
- You've shipped >5 slices and discovered patterns

The bump is cheap — existing slices stay; future slices use Standard mode behavior (critique runs, etc.).

### Q: Does /reflect REALLY need to run every slice?

Yes. Skipping it is the #1 way the vault rots. Even if a slice felt routine, the reflection captures what reality validated vs corrected — that's the data that makes the next slice better. A 5-minute reflection saves hours later.

### Q: Can I run `/critique` more than once per slice?

Yes — useful when you change the design substantially in response to first critique. Re-running attacks the new design, not the old one. Don't loop infinitely; if critique-#3 is finding new blockers, the design is structurally wrong (consider /design-slice from scratch or breaking the slice in two).

### Q: How long should slices be?

Target: ≤1 day of AI implementation work. If a slice would take longer, split. If splitting produces a slice with no user-visible value, the original "feature" was probably 2+ features.

For Heavy mode: 1-2 days is OK because per-slice overhead (critique, sign-offs, reproducible validation) is higher.

### Q: What if the Critic missed something and we shipped a bug?

`/reflect` captures it: "Missed by Critic: <thing>." Pattern across reflections informs Critic prompt tuning over time. Critic is fallible; the goal is to catch most things, not all things.

### Q: I'm using a different harness (not Claude Code). Can I still use this pipeline?

The skills/ directory is Claude Code specific (SKILL.md format). For other harnesses:
- The pipeline structure (modes, slice flow, principles) still applies
- Translate each SKILL.md body into your harness's format
- The vault structure is harness-agnostic
- Plan mode equivalent (or human-approved task list) is needed for `/build-slice` discipline

---

## TL;DR

```
Solo / MVP / one-off → MINIMAL: /triage → /discover → /slice loop
B2C / product / team → STANDARD: above + /critique + /user-test
Compliance / regulated → HEAVY: above + /heavy-architect + /sync + sign-offs
```

Read the worked example matching your project. Reference common scenarios as you go. Watch for anti-patterns. Run `/reflect` every slice — it's the cure for spec rot.
