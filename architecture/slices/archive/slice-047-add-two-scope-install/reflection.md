# Reflection: Slice 047 add-two-scope-install

**Date**: 2026-05-19
**Shipped**: NO — feature withdrawn at TRI-1 as platform-infeasible; salvaged as a global-only **decision record** (ADR-049 rewritten in place)

> Decision-only / withdrawn-feature slice. `/build-slice` and `/validate-slice`
> never ran (nothing to build once the premise was refuted), so there is no
> `build-log.md` / `validation.md`. "Reality" for calibration purposes is the
> official Claude Code platform documentation, Builder-confirmed via WebFetch
> on 2026-05-19.

## Validated

- The latent scope-blindness *was* real and worth retiring — INST-1 / CAD-1 /
  PMI-1 genuinely never *decided* scope was global; it was an accident of how
  the recipe was first written (confirmed while reading `INSTALL.md` +
  `install_audit.py` during design/critique). The deferral chain
  (slice-045 Deferred #2 → slice-046 Deferred #1) pointed at a real gap.
- `tools/install_audit.py` is genuinely `--claude-dir`-generic and needed
  zero change — validated by code inspection at design (this part of the
  design held; it just wasn't enough to make the feature work).

## Corrected

- **Core design premise REFUTED.** design.md "What's reused": *"Claude Code's
  native project-level `.claude/` resolution — skills/agents/settings under
  `<project>/.claude/` are active when CC runs in that project"* and ADR-049
  (old) Options §2 pro *"rides Claude Code's native project-level `.claude/`
  resolution"* → reality: **personal `~/.claude/` skills override project
  `.claude/`** (project copy silently shadowed for every existing user).
  Builder-confirmed via WebFetch against the official Claude Code skills docs.
  → corrected in [[decisions/ADR-049-two-scope-install-content-vs-global-boundary]]
  (rewritten in place: feature-design ADR → global-only **decision record**;
  in-place rewrite, not SUP-1, because `/build-slice` never ran — no shipped
  decision was edited; user-directed at TRI-1).
- ADR-049 (old) reversibility "no consumer binds to the scope mechanism" was
  imprecise (m2) → rewritten ADR states precise reversibility: as a pure
  decision record, revert = delete the ADR; no INSTALL.md/changelog/
  shippability/code consumer is created.

## Discovered

- **Claude Code skill vs subagent precedence is ASYMMETRIC** (the load-bearing
  discovery): skills — personal `~/.claude/` **overrides** project `.claude/`;
  subagents — project `.claude/agents/` (Priority 3) **overrides** user
  `~/.claude/agents/` (Priority 4). They resolve in *opposite* directions.
  Both Builder-WebFetch-confirmed 2026-05-19.
- **Split-resolution runtime hazard**: because the pipeline ships BOTH 25
  skills AND 5 subagents, a project-scope `cp` install on an existing
  user-scope machine would load the 25 skills from *user* scope (project
  shadowed) while the 5 agents' *project* copies override — a mixed runtime
  state INST-1's on-disk audit cannot detect (it false-greens: all artifacts
  present on disk, wrong set loaded at runtime). This is *worse* than a clean
  no-op. Impact: any future per-project-scope work must treat this as a
  first-class hazard, not an edge case.
- **The only viable future path to per-project scope is a Claude Code plugin
  re-architecture** (namespaced `plugin-name:skill-name` cannot collide across
  levels) — recorded in ADR-049 so a future slice does not re-discover the
  precedence asymmetry from scratch. NOT added to the risk register: there is
  no open risk here — the boundary is now a *decided* fact, not an open
  exposure (a future plugin-re-architecture slice is opt-in scope, not a
  standing risk).

## Deferred

- **Per-project install scope** — reason: platform-infeasible via `cp`;
  requires a plugin re-architecture far past a 1-day slice. Lands in: backlog
  (only if ever demonstrated necessary; ADR-049 names the path).
- M1 (v0.56.0 entry-pin test), M2 (Test-first genuine-contrast pin), M3
  (Step 0b/Step 1 reconciliation), m1 (scope-unaware remediation prose),
  m-add-2 (installed-copy write) — reason: all presupposed a shipping feature;
  moot under the abandon decision. Lands in: nowhere (obsolete with the
  withdrawn feature; recorded DEFERRED-as-obsolete in the critique.md TRI-1
  table).

## Critic calibration

Per TRI-1, scored from `critique.md` → `## Triage` + the platform reality
(official docs) that the Builder confirmed via WebFetch:

- **B1** (project-scope silently defeated by personal>project skill
  precedence): **VALIDATED** — disposition ESCALATED→BLOCKED; reality (the
  official skills docs) confirmed the Critic's concern exactly. The first
  Critic did not merely assert it — it Builder-verified it via WebFetch
  before filing. A clean, high-value first-Critic catch on the slice's
  load-bearing premise (web-known-issues + unfounded-assumptions dimensions
  both fired correctly).
- **M-add-1** (skill/agent precedence is the INVERSE; the real failure is a
  split-resolution state, not a uniform no-op): **MISSED by Critic** — the
  first Critic verified the *skill* precedence direction and then generalized
  the claim to "skills/agents" without separately verifying the *agent*
  direction (which is inverted). Caught by the `/critique-review` meta-Critic
  (DR-1) and Builder-WebFetch-confirmed. This is the calibration signal of
  the slice.
- **M1 / M2 / M3 / m1 / m-add-2**: **NOT-YET → closed obsolete** — all
  DEFERRED at TRI-1 as moot under the decision-only outcome; no future slice
  re-scores them (the feature they guarded is withdrawn). Not Critic errors:
  each was a correct finding *conditional on* a shipping feature.
- **m2** (ADR-049 reversibility imprecise): **VALIDATED** — disposition
  ACCEPTED-PENDING; the imprecision was real and is removed by the ADR-049
  rewrite.

**Missed by Critic**: M-add-1 — the first Critic confirmed one artifact
class's platform precedence direction (skills) and over-generalized it to a
second class (agents) that resolves in the opposite direction, missing the
split-resolution hazard that is strictly worse than the no-op it did flag.
DR-1 caught it. (Zero false positives across the first Critic's 7 findings —
its accuracy on what it *did* file was perfect; the single gap is a
verify-one-then-generalize blind spot on a multi-artifact-class platform
claim.)

**Pattern**: N+1 to the recurring "DR-1 keeps paying on codification /
methodology-surface slices" law (026/029/038/039/046). Here the first Critic's
miss has a specific, nameable shape — **verify-one-artifact-class-then-
generalize on a platform precedence claim**. Consistent with the slice-037
law: the durable cure is DR-1 (which worked), not a new first-Critic
dimension. Strong `/critic-calibrate` input (the M-add-1 shape is concrete and
generalizable). Also a `/design-slice` process signal: a load-bearing
external-platform resolution assumption was locked into design.md + ADR-049
with `Test-first: false` and no `/risk-spike`, even though it was the single
fact the entire slice's value depended on — exactly the `/risk-spike`
trigger condition.

## Lessons for next slice

- **A load-bearing external-platform behavior (resolution order, precedence,
  quota, API contract) that a slice's *premise* depends on must be
  WebFetch-verified against official docs at `/design-slice` — or
  `/risk-spike`'d — BEFORE design lock, never asserted from prior belief and
  deferred to `/critique` to catch.** Slice-047 burned a full
  design→critique→critique-review→TRI-1 cycle to discover its premise was
  false; a 10-minute design-time WebFetch would have caught it pre-design.
- **Platform precedence is not guaranteed symmetric across artifact classes.**
  When a slice's premise rests on a Claude Code resolution/precedence rule
  that spans more than one artifact class (skills AND agents AND settings),
  verify *each class independently* — skills resolve personal>project; agents
  resolve project>user (the inverse). Verifying one and generalizing is the
  exact M-add-1 miss.
- **A BLOCKED slice can still ship durable value as a decision record.**
  Rewriting the slice's own un-shipped ADR in place (same ID, same slice,
  `/build-slice` never ran → not a SUP-1 event) converts a dead feature into
  a recorded decision that retires the deferral that motivated it. Cheaper
  and more honest than abandoning with nothing captured.

## Vault updates made (thin vault — small list)

- [[decisions/ADR-049-two-scope-install-content-vs-global-boundary]] —
  rewritten in place: feature-design ADR → global-only **decision record**
  (m2 reversibility precision folded in); retires the slice-045/046
  scope-blindness deferral by deciding it (global-only)
- This slice's [[milestone.md]] — `stage: closed` → (this step) `complete`;
  outcome `decision-only / withdrawn-feature`
- [[lessons-learned.md]] — slice-047 chronological entry appended
- [[shippability.md]] — row 47 added (decision-only regression guard:
  INSTALL.md stays global-only AND ADR-049 stays the global-only record)
- `risk-register.md` — **no change** (no open risk; the deferral is closed by
  decision, not carried as exposure)
- `methodology-changelog.md` — **no change / no version bump** (no behavior
  change; INSTALL.md unedited — recording a no-behavior-change decision in the
  ADR, never a parentless changelog `###` entry, per the slice-040/036
  discipline)
