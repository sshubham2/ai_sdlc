---
id: ADR-024
title: CRP-1 documented-skip escape-hatch is the milestone.md `critique-review-skip` frontmatter key (not build-log.md Events as BRANCH-1, not a free-form body line)
date: 2026-05-16
slice: slice-026-enforce-critique-review-prerequisite
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-024: CRP-1 documented-skip escape-hatch location + naming-class placement

## Context

Slice-026 codifies **CRP-1**: a structural `/build-slice` `## Prerequisite check`
that refuses when a mandatory `/critique-review` (DR-1, mandatory in Standard mode
for mandatory-Critic slices per slice-010 / CLAUDE.md) is absent and unrationalised.
The mission brief specified the escape-hatch should mirror BRANCH-1's canonical
`BRANCH=skip — rationale: <text>` shape.

Two location constraints interact:

1. **Pre-build readability.** BRANCH-1's escape-hatch lives in `build-log.md`
   Events and is checked at `/build-slice` **Step 6 pre-finish** — `build-log.md`
   exists by then. CRP-1's *primary* gate fires at the **`## Prerequisite check`**
   — *before* Step 1, when `build-log.md` does not yet exist. A `build-log.md`
   escape-hatch is structurally unreadable at CRP-1's enforcement point.
2. **Step 7b mutation survival.** `skills/build-slice/SKILL.md` Step 7b
   ("Update milestone.md **continuously**", L269-271) rewrites `milestone.md`
   *during* execution. The CRP-1 Step 6 defense-in-depth re-run reads
   `milestone.md` again *after* Step 7b has run. A free-form `milestone.md` body
   line has no defined home in the templated structure and could be clobbered by
   the Step 7b rewrite — a legitimately escape-hatched build would then
   false-refuse at Step 6 (violates mission-brief Must-not-defer "no false-refuse").

## Options considered

1. **`build-log.md` Events (identical to BRANCH-1)** — maximal shape parity, but
   unreadable at prerequisite-check time; would force CRP-1's gate to Step 6
   (post-build), defeating refuse-to-*start*. Rejected.
2. **Free-form canonical line in `milestone.md` body** — readable pre-build, but
   has no reserved home in the milestone.md template and is at risk from the
   Step 7b continuous rewrite; also a body-substring scan (BRANCH-1 style) can
   false-positive on narrative prose that mentions the token. Rejected.
3. **`mission-brief.md` line** — exists early, but `mission-brief.md` is
   intent-frozen after `/slice`; a skip is a process deviation belonging with
   rolling state. Rejected.
4. **Reserved `critique-review-skip:` key in `milestone.md` frontmatter** —
   readable from `/slice` onward (same file that already carries
   `critic-required`); a structured frontmatter key has a defined home the Step 7b
   field-targeted rewrite preserves (Step 7b updates specific fields, not a
   wholesale templated regeneration; the milestone.md template documents the
   optional key and Step 7b is instructed to preserve it); detection keyed on the
   frontmatter key (not a body substring) eliminates the narrative-prose
   false-positive. Same `rationale:` spirit as BRANCH-1. **Chosen.**

## Decision

The CRP-1 documented-skip escape-hatch is the **optional `critique-review-skip:`
key in the active slice's `milestone.md` frontmatter**, with value matching
`^skip — rationale: .+`. The key is absent by default and documented in the
milestone.md template; `skills/build-slice/SKILL.md` Step 7b carries an explicit
instruction to preserve it verbatim across rewrites. A `critique-review-skip:`
key present with an off-canonical value is a malformed-escape-hatch Important
violation (exit 1), mirroring BRANCH-1's malformed-attempt handling. The canonical
shape is pinned in `skills/build-slice/SKILL.md` (the CRP-1 prerequisite
sub-block) and asserted by `tests/methodology/test_critique_review_prerequisite_audit.py`.

**Naming-class placement (not a deviation from ADR-019).** CRP-1 is an
**audit-enforced gate** — its programmatic gate is
`tools/critique_review_prerequisite_audit.py`. Per ADR-019's test-pinned naming
note, the `-D` suffix is reserved for `/critique`-time prose-heuristic
disciplines with *no* programmatic audit (RSAD-1 / EPGD-1 / SCPD-1 / RPCD-1 /
TPHD-1 / BFRD-1); audit-enforced gates (BC-1, CAD-1, PMI-1, INST-1, WIRE-1,
BRANCH-1, UTF8-STDOUT-1, …) do NOT carry `-D`. CRP-1 therefore takes the **bare
`CRP-1`** form and joins the audit-enforced-gate class. This ADR **conforms to**
ADR-019; it does not supersede it (`supersedes: null` is correct).

## Consequences

- CRP-1's primary gate stays at the `## Prerequisite check` (refuse-to-start),
  matching mission-brief AC1, with a Step 6 defense-in-depth re-run that reads the
  same Step-7b-preserved frontmatter key (idempotent, no false-refuse).
- Shape parity with BRANCH-1 is *spiritual* (`skip — rationale: <text>`), not
  byte-identical (no `- <YYYY-MM-DD HH:MM> DEVIATION:` event-log prefix; it is a
  YAML frontmatter value, not an Events line) — documented here so the Critic does
  not read it as an unfounded inconsistency.
- `milestone.md` is per-slice runtime state, not under a CAD-1 byte-equality gate
  — correct, since a skip is a per-slice decision, not a methodology-surface change.
- **milestone.md *template* forward-sync (per /critique-review M-add-1).** The
  `critique-review-skip:` key is documented in the milestone.md *template*, which
  exists as a byte-equal in-repo (`templates/milestone.md`) ↔ installed
  (`~/.claude/templates/milestone.md`) pair. `install_audit.py` `_check_templates`
  checks template *existence only* (no byte-compare) and there is no milestone
  template drift test. This slice does **not** add such a gate (a template
  byte-equality discipline is a separate slice's scope); instead the template
  delta is propagated to BOTH copies in lockstep and the manual+unguarded
  propagation is explicitly enumerated in design.md §"What's new" (N=5). This is
  *enumeration-discharge*, not a byte-equality exemption — the next
  template-touching slice inherits the documented obligation, not silent drift.
- **Bootstrap-reference instance #1.** Mirroring the BRANCH-1 precedent
  (`methodology-changelog.md` L205, slice-021), slice-026 is CRP-1
  bootstrap-reference instance #1: at slice-026's own `/build-slice` Prerequisite
  check the CRP-1 sub-block does not yet exist (this build authors it), so CRP-1
  cannot self-gate this build. Self-application is satisfied by `/critique-review`
  run on slice-026 + the audit run against slice-026's own folder
  (Verification-plan row 5). Future codification slices inherit a self-gating
  CRP-1; slice-026 alone is the bootstrap exception.
- If a future slice moves CRP-1 enforcement to post-build only, the escape-hatch
  could be reunified with BRANCH-1's `build-log.md` location — hence reversibility
  is **cheap**.

## Reversibility

**cheap** — the location is encoded in one frontmatter-key name + one value
regex, one skill prose block, the milestone.md template line, and the test
fixtures. Changing it is a localized edit with no external consumers (the audit
is the only reader). Tagged cheap accordingly.
