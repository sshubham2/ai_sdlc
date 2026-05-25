---
id: ADR-049
title: Install scope is global-only; project-scope-via-cp is platform-infeasible (skill personal>project shadow + agent project>user split-resolution); revisit only via a Claude Code plugin re-architecture
date: 2026-05-19
slice: slice-047-add-two-scope-install
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-049: Install scope is global-only (decision record)

> **Decision-record ADR, not a feature-design ADR.** Slice-047 set out to add
> interactive two-scope (`~/.claude` vs `<project>/.claude`) install support.
> `/critique` BLOCKED it (B1) and `/critique-review` EXTENDed (M-add-1); the
> user's TRI-1 decision (2026-05-19) abandoned the *feature* as
> platform-infeasible and directed that this ADR be rewritten in place — same
> slice, same ADR-ID, `/build-slice` never ran, so no shipped decision is
> being edited (this is not a SUP-1 append-only event). The salvaged value is
> the durable *decision* recorded here: it retires the standing scope-blindness
> deferral by deciding it (global-only), rather than leaving it un-decided.

## Context

`INSTALL.md` (the INST-1 recipe Claude executes verbatim) hardcodes every
install target to the global `~/.claude/`. Nothing ever *decided* scope was
global — it was an accident of how the recipe was first written, carried as a
structural deferral (slice-045 Deferred #2 → slice-046 Deferred #1). Slice-047
existed to make that boundary an explicit, recorded decision (and, originally,
to enable a project-level scope as the pipeline's first user-facing capability
in ~25 conformance micro-slices).

During `/critique` + `/critique-review` the load-bearing platform assumption —
that a project-scope `cp` install "rides Claude Code's native project-level
`.claude/` resolution" — was tested against the official Claude Code docs and
found **false**. Both halves were Builder-confirmed via WebFetch on
2026-05-19, not merely Critic-asserted.

## Platform findings (the reason the feature is infeasible)

1. **Skills: personal overrides project.** Official Claude Code skills docs:
   *"When skills share the same name across levels, enterprise overrides
   personal, and personal overrides project."* Every existing INSTALL.md user
   already has the fixed-named pipeline skills (`slice`, `critique`,
   `build-slice`, …) at user scope. A project-scope copy is **silently
   shadowed** — it never loads. Project-scope is a no-op for the entire
   primary audience and works only on a machine with no user-scope install.
   (B1, Builder-confirmed via WebFetch against the official skills docs.)

2. **Subagents: project overrides user — the inverse.** Official Claude Code
   subagents docs precedence table: `.claude/agents/` (project) = Priority 3 >
   `~/.claude/agents/` (user) = Priority 4; "the higher-priority location
   wins." The pipeline ships 25 skills **and** 5 subagents (`critique`,
   `critique-review`, `critic-calibrate`, `diagnose-narrator`, `field-recon`).
   Under a project-scope install on an existing user-scope machine the result
   is a **split-resolution runtime state**: the 25 skills load from *user*
   scope (project copies shadowed) while the 5 agents' *project* copies
   override the user copies. (M-add-1, Builder-confirmed via WebFetch against
   the official subagents docs.)

3. **INST-1 false-greens the split.** `tools/install_audit.py --claude-dir
   <project>/.claude` verifies every artifact present *on disk* and passes,
   while Claude Code actually loads a mixed skill(user)/agent(project) set at
   runtime. The must-not-defer "INST-1 must verify the *chosen* scope" guard
   is specifically defeated for the skill half — a split-resolution install is
   *worse* than a clean no-op because the audit cannot detect it.

## Options considered

1. **Project-scope as a `cp` content overlay (the original slice-047
   design).** Rejected — INFEASIBLE: shadowing (finding 1) makes it a no-op
   for every existing user; the skill/agent precedence asymmetry (finding 2)
   makes it a silently-broken split-resolution state (finding 3) on any
   machine that also has a user-scope install.
2. **Project-scope + instruct the user to remove/override their user-scope
   copies.** Rejected — migration-adjacent, explicitly mission-brief
   out-of-scope, and fragile (it weaponizes the recipe against the user's own
   global install to defeat a platform precedence rule).
3. **Decide install scope is GLOBAL-ONLY and record the decision.** CHOSEN —
   the smallest correct outcome: it retires the deferral by *deciding* it
   (global-only is now a recorded decision, not an unstated accident),
   preserves byte-identical behavior for every existing user (INSTALL.md
   unchanged), and adds zero broken capability.
4. **Re-architect the install as a Claude Code plugin.** Deferred (future
   work, only if ever demonstrated necessary). A namespaced plugin
   (`plugin-name:skill-name`) cannot collide across levels, so the plugin
   model is the *only* real path to per-project scope — but it is an install
   re-architecture far past this slice's 1-day boundary and is not proposed
   here.

## Decision

**Install scope is global-only.** `INSTALL.md` continues to install all
artifacts under `~/.claude/` and is **not modified** by this slice.
Project-scope-via-`cp` is rejected as platform-infeasible for the reasons
above. The standing scope-blindness deferral (slice-045 Deferred #2 →
slice-046 Deferred #1) is **retired by this decision** — the boundary is now
explicit and recorded (global-only), no longer an un-decided accident.

Per-project scope is revisitable **only** via a future Claude Code **plugin
re-architecture** (namespaced `plugin-name:skill-name`, which cannot collide
across levels). That is a separate, much larger slice and is not committed
here.

This is a **decision-only / withdrawn-feature** outcome (no-behavior-change
conformance class — precedent: slice-043, slice-045). Consequently there is
**no `methodology-changelog.md` v0.56.0 entry** (INSTALL.md behavior is
unchanged; a parentless `###` changelog entry would violate META-1 — the
slice-040/036 no-VERSION-bump discipline: a no-behavior-change outcome is
recorded in the ADR, not the changelog), **no VERSION bump** (stays 0.55.0),
**no shippability row**, and **no v0.56.0 entry-pin test**. The `/critique`
Majors that assumed a shipping feature — M1 (entry-pin test), M2 (Test-first
genuine-contrast pin), M3 (Step 0b/Step 1 reconciliation), m1, m-add-2 — are
moot under this outcome and were DEFERRED-as-obsolete at TRI-1.

## Consequences

- `INSTALL.md`, `tools/install_audit.py`, `plugin.yaml`, `VERSION`, and
  `methodology-changelog.md` are all **unchanged** — zero regression surface
  for every existing user (this is the no-behavior-change property).
- The scope boundary is now a **decided** fact (global-only) instead of a
  latent single-scope assumption silently baked into INST-1 / CAD-1 / PMI-1.
  The slice-045/046 deferral chain is closed by this record.
- Per-project install is a known **non-capability** with a known **only
  future path** (plugin re-architecture) — captured so a future slice does
  not re-discover the precedence asymmetry from scratch.
- Slice-047 is closed out as decision-only / withdrawn-feature: `/build-slice`
  is NOT run; the next candidate is selected via a fresh `/slice` after
  `/reflect` captures the platform-precedence learnings (high-value
  `/critic-calibrate` input: a load-bearing platform assumption that survived
  design + first-Critic and was caught only by Builder WebFetch + meta-Critic
  asymmetry analysis).

## Reversibility

**Cheap.** As a pure decision record this ADR creates **no** durable
consumer: `INSTALL.md` is unchanged, no `$CLAUDE_DIR` indirection exists, no
`methodology-changelog.md` v0.56.0 entry exists, no `architecture/
shippability.md` row is added, no entry-pin test is authored, and no runtime
or code path binds to a scope mechanism (`tools/install_audit.py` was already
`--claude-dir`-generic before slice-047 and is untouched). Reverting = delete
this ADR; there is no data migration, no schema, no code consumer to unwind.
The decision is supersedable in the normal append-only way (SUP-1) via a
future ADR — specifically the plugin-re-architecture ADR, if per-project
scope is ever pursued.
