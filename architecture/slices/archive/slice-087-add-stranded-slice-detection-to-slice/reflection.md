# Reflection: Slice 087 add-stranded-slice-detection-to-slice

**Date**: 2026-05-31
**Shipped**: YES-WITH-DEFERRALS

## Validated
- The **parallel-safe 4-class divergence model** works against real state — the live two-worktree repo (slice/087 + slice/088) classifies both as IN-PROGRESS → no halt → `status: clean` (validated by the executed `tools.stranded_slice_audit` run + behavioral case 4c). The pre-reframe flag-all design would have cry-wolfed both; the reframe achieved its goal.
- **Reuse held**: `pulse_worktree_resolver.{detect_active_worktrees,classify_worktree_state,_resolve_default_branch}` + `slice_queue_claim.parse_queue_text` were reused without re-implementation (B1 from the first critique honored) — verified by the live run driving those functions and the inventory cross-spec checks.
- **The `agents/critique.md` Dim-7 probe (committed `64f6ea3`) did its job**: it was the lens that made the parallel-safety concern first-class; re-`/critique` validated the reframe against it (Part B's first live test, per the slice-088 sibling lineage).
- Exit/UTF8/no-false-positive contracts: exit 0 advisory / exit 2 usage / no exit 1; `→` header non-vacuous under cp1252 (M3 verified); `recovery/*` excluded structurally by the `refs/heads/slice/` ref-glob (4f).

## Corrected
- **`_TERMINAL_STAGES = {"reflect"}` was wrong** → reality: the vault's terminal stage is `complete` (written by `skills/reflect/SKILL.md:305`; 85/87 milestones). The code-Critic caught this (B1) by EXECUTING against the real vault; `reflect` is only the transient mid-`/reflect` worktree stage. Corrected in the slice's own `tools/stranded_slice_audit.py` (`{"reflect", "complete"}`) + design.md (the bare-branch path now reads the real terminal vocabulary) + new behavioral case 4i. No ADR supersession — design.md's intent ("milestone terminal") was correct; the code had narrowed it.
- **The behavioral fixtures used a vocabulary the vault never produces at terminal** (`stage: reflect` + `commit` next-action) → corrected by adding case 4i (`stage: complete` / `none (slice complete)`), which fails-first against the old set.

## Discovered
- **The PSQ parallel-slice shared-install hazard (the dominant discovery)** — a version-bumping parallel sibling (slice-088 / PFS-1) that forward-syncs the single shared `~/.claude/` to a new version (agent + changelog + VERSION + venv pip pkg) causes the OTHER worktree's forward-sync/content-equality audits (CAD-1, MCFS-1, AVFS-1, TVFS-1) AND every shippability row bundling those tests (13 rows here) to report DRIFT/FAIL — none of which are defects in the slice under validation. Added to risk register as **R-28**. Impact: false HALTs on the non-version-bumping sibling; reconciles only at merge. This is the strongest `/critic-calibrate` candidate from this slice.
- **Design/meta Critics reason about the design's stated vocabulary; only the code-Critic executes against the repo's REAL data vocabulary.** B1 (terminal `complete`) sailed through both the design-Critic re-critique AND the meta-Critic because neither ran the classifier against an actual `stage: complete` milestone — the APED-1 "execute the new parse rule against the real corpus, not the design's assumed corpus" lesson recurring on the classifier axis. Impact: a classifier/parser slice's design+meta review must be prompted to enumerate and test against the REAL vault vocabulary (`stage:` values, `next-action:` shapes), not the design's narrower assumption.
- **`git show <branch>:` reads committed-tip, which lags an uncommitted working milestone (M-add-1)** — for a bare branch this is the only recoverable state; named in the error model as an acknowledged residual rather than assumed away.

## Deferred
- **The 13 sibling-induced shippability FAILs + the 4 forward-sync audit drifts (CAD-1/MCFS-1/AVFS-1/TVFS-1)** — reason: 100% caused by slice-088's PFS-1 install-sync to v0.78.0; slice-087 touches none of `agents/`, `VERSION`, `methodology-changelog.md`, `pyproject.toml`; no fix is correct from within slice-087 (clobbering would destroy slice-088's work). User-approved deferral (2026-05-31). Lands in: **merge** — reconciles automatically (no file conflict; post-both-merge in-repo == installed). NOT a slice-087 regression.
- **CLAIMED-BY-OTHER multi-session reachability** — the class is inert in solo-dev + the current PSQ-1 top-10 queue-regeneration lifecycle (an in-flight branch is frequently queue-absent). Documented as a forward-provision, not load-bearing. Lands in: a future slice if PSQ keys gain slice numbers (would also close the M2 claim-key collision residual).
- **Claim-key collision (M2)** — lossy `slice/NNN-<name>` → `<name>` mapping; documented residual, bounded by PSQ-1's bare-name keying. Lands in: same future PSQ-keys-by-number slice.

## Critic calibration

Per TRI-1, scored against `critique.md` + `critique-review.md` + `code-review.md` dispositions and reality:

**Design-Critic re-critique** (`critique.md`):
- B1 (CLAIMED-BY-OTHER can't fire vs live queue): **VALIDATED** — ACCEPTED-FIXED option-a; reality confirmed the class is inert in solo-dev exactly as the honesty note predicted (live run: no claims, never fired). Severity-adjusted Blocker→Major (meta-Critic), correct.
- M1 (bare-branch reads wrong tree): **VALIDATED** — ACCEPTED-FIXED; the cross-tree direction was right (and the code-Critic's B1 then deepened it).
- M2 (smoke fixture under-specifies milestone → INDETERMINATE): **VALIDATED** — ACCEPTED-FIXED; concrete fixture shipped.
- M3 (`--root` cp1252 incidental-pass): **VALIDATED** — ACCEPTED-FIXED; the always-emit `→` made the cp1252 test non-vacuous (verified).
- m1 (ahead:null prose) / m2 (INSTALL.md count fan-out): **VALIDATED** — both real; the 33→34 fan-out touched 4 surfaces incl. slice-077's inventory test (m2 was load-bearing).

**Meta-Critic** (`critique-review.md`, EXTEND):
- M-add-1 (committed-tip staleness on the M1 cross-tree read): **VALIDATED** — a real seam-between-subsystems gap the first Critic missed; ACCEPTED-FIXED (named in error model). Classic dual-review catch (one layer trusting the other's framing).

**Code-Critic** (`code-review.md`, FINDINGS):
- **B1 (terminal vocabulary `stage: complete`): VALIDATED — and MISSED by BOTH the design-Critic AND meta-Critic.** The slice's primary new-value path was silently broken; caught only by executing against the real vault. This is the single most important finding of the slice.
- M1 (incidental-pass fixtures): **VALIDATED** — fixed via case 4i.
- M2 (claim-key collision): **VALIDATED** (inert in solo-dev) — documented.
- m1/m2 (commit substring / quote-strip): **VALIDATED** — fixed. m3 (redundant merge-base): OVERRIDDEN (distinct purposes) — defensible.

**Missed by Critic**: B1 (terminal `stage: complete`) — missed by the design-Critic + meta-Critic; the code-Critic caught it. The PSQ shared-install hazard (R-28) was surfaced during validation by the audit runs, not by any Critic (it's an environmental/process property, arguably out of any single Critic's scope).

**Pattern**: the 3-Critic stack complementarity held at its strongest — design-Critic (vocabulary-mapping + inventory), meta-Critic (cross-subsystem seam staleness), code-Critic (the runtime-execution property: real-vault vocabulary). **The recurring calibration signal**: a classifier/parser slice's design+meta Critics reason about the *stated* vocabulary; only execution against the *real* corpus catches a vocabulary mismatch (APED-1 on the classifier axis — a `/critic-calibrate` candidate: add a Dim probe "for a new classifier/parser of vault state, has the rule been executed against the repo's REAL `stage:`/`next-action:`/field vocabulary, not the design's assumed set?").

## Lessons for next slice
- **Forward-sync/content-equality audits (CAD-1/MCFS-1/AVFS-1/TVFS-1) compare each worktree against the single shared `~/.claude/` — structurally fragile under parallel version-bumping slices.** A non-version-bumping slice running parallel to a version-bumping one will see false HALTs it cannot fix. Until a methodology fix (per-worktree-scoped comparison, or merge-time-only enforcement), treat such drifts as documented sibling-induced deferrals (verify `git diff HEAD` is empty on the drifted files to attribute). R-28.
- **A new classifier/parser of vault state must be EXECUTED against the repo's real field vocabulary at design+meta review, not just unit fixtures** — the design's assumed vocabulary (`stage: reflect`) diverged from the vault's real one (`stage: complete`); only the code-Critic caught it. APED-1 on the classifier axis.
- **The 3-Critic stack must NOT be collapsed** — N≥1 more datapoint: each persona caught a non-overlapping defect class (vocabulary-map / cross-subsystem-seam / real-vault-execution).
- **In parallel-slice mode, attribute every audit failure before acting**: `git diff HEAD -- <drifted-files>` empty ⇒ sibling-induced, do NOT clobber the shared install.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-27 stays **mitigating** (the detector ships but is advisory + carries the committed-tip staleness residual; consistent with the slice-084 partial-mitigation pattern); added **R-28** (PSQ shared-install forward-sync fragility under parallel version-bumping slices).
- This slice's [[design.md]] — bare-branch terminal vocabulary corrected to `{reflect, complete}` (B1); M2 claim-key collision residual documented; M-add-1 committed-tip staleness named in error model.
- [[shippability.md]] — row 93 (added at build as part of the 5-surface inventory).
- [[drift-log.md]] — slice-087 audit entry (CLEAN for slice-087 surface; sibling-induced drift documented).
- No ADR supersession (ADR-079 revised in place pre-ship; design intent was correct).
- No BCR-1 round-trip (no `**Closes:** SC-` sentinel in mission-brief or this reflection).
- No PMI-1 version bump (MEPD-1 EXCLUDE) → Step 5b-fs/avfs/tvfs forward-sync gates not triggered by this slice (the installed-side drift is slice-088's, resolved at merge).
