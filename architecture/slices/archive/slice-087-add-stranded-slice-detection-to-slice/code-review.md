# Code Review: Slice 087 add-stranded-slice-detection-to-slice

**code-Critic reviewed**: slice diff vs default branch `master` (base `64f6ea3`), filtered to in-scope paths
**Date**: 2026-05-31
**Result**: FINDINGS

> Spawned via `Agent` `subagent_type: "code-review"`; per SAOF-1 written ONLY from the agent's actual returned content. The code-Critic EXECUTED the classifier against synthetic repos using the REAL vault milestone vocabulary. Advisory in v1 (CRSI-1) — but B1 is a genuine correctness bug in the slice's primary path, so the Builder fixed B1/M1/m1/m2 in-slice (code-aligns-to-design; no design change). See "Builder disposition" per finding.

## Summary

The classifier is well-structured, the reuse of `pulse_worktree_resolver` + `slice_queue_claim` is honest (no re-implementation), parallel-safety holds for the live-worktree case, and the exit-code/UTF8/no-false-positive contracts + all 5 inventory surfaces are correct. But the **bare-branch terminal-milestone detection was broken against this repo's real milestone vocabulary** (`_TERMINAL_STAGES = {"reflect"}` vs the vault's `stage: complete`), so a genuinely-stranded completed slice on a bare branch — the exact slice-086-class incident — silently classified IN-PROGRESS. The 8 tests passed only because the fixture hardcoded the unused `stage: reflect` (incidental pass).

## Changed files (in-scope)
- tools/stranded_slice_audit.py
- tests/methodology/test_stranded_slice_audit.py
- tests/methodology/{test_slice_skill_stranded_prereq,test_pulse_skill_stranded_signal,test_stranded_slice_audit_tool_inventory}.py
- skills/slice/SKILL.md · skills/pulse/SKILL.md
- plugin.yaml · tools/install_audit.py · INSTALL.md
- tests/methodology/{test_utf8_stdout_regression,test_pulse_worktree_resolver_tool_inventory}.py

## Findings

### Blockers (advisory in v1)

#### B1: Bare-branch terminal detection used `stage: reflect`, but the vault's terminal stage is `stage: complete` — a stranded completed slice on a bare branch silently classified IN-PROGRESS (no halt)
- **Claim under review**: `tools/stranded_slice_audit.py:70` `_TERMINAL_STAGES = {"reflect"}`, consumed by `_is_terminal` (L169-174) + the bare-branch milestone path (L287, L307).
- **Issue**: `"reflect"` is the *transient mid-`/reflect`* worktree stage. The vault's **terminal** stage — written by `skills/reflect/SKILL.md:305` (`stage: complete`, `next-action: none (slice complete)`) — is `complete` (85/87 milestones). A bare unmerged branch with a real terminal milestone fails BOTH `_is_terminal` axes (`complete` not in the set; `none (slice complete)` has no `commit`) → falls through to IN-PROGRESS → `halt: false` → `status: clean`. This is the slice's primary new-value path (design.md "the genuinely-new value"), silently missed; the slice-086 incident escaped only because it was archived (`_branch_tree_has_path` saved it).
- **Evidence**: executed — bare branch + `slice-500-realdone/milestone.md` `stage: complete`/`none (slice complete)` (not archived) → `in-progress halt=False status:clean`.
- **Builder disposition**: **FIXED** — `_TERMINAL_STAGES = {"reflect", "complete"}` (cross-ref `skills/reflect/SKILL.md` as source of truth) + new behavioral case `test_complete_stage_bare_branch_is_stranded_complete` (the production-vocabulary terminal case) + TF-1 plan row. Code now matches design.md's generic "milestone terminal" intent.

### Majors

#### M1: The 8 behavioral tests passed against a milestone vocabulary the production vault never uses — incidental pass masking B1
- **Claim under review**: `tests/methodology/test_stranded_slice_audit.py:95-100` `_milestone(...)` — every terminal-case caller passes `stage="reflect"`.
- **Issue**: STRANDED-COMPLETE fixtures (4a/4d/4h) use `stage: reflect` + `commit` next-action — neither emitted by `/reflect` at terminal. Tests green but validate against synthetic-only input; `stage: complete` never exercised → B1 unguarded (the slice-085 incidental-pass lesson recurring on a new axis).
- **Builder disposition**: **FIXED** — added a `stage: complete` / `next-action: none (slice complete)` bare-branch terminal case (4i) that fails-first against the pre-fix `_TERMINAL_STAGES` and passes post-fix. The production terminal vocabulary is now exercised.

#### M2: Lossy branch→queue-key mapping (`slice/NNN-<name>` → `<name>`) lets a foreign claim on a same-suffix different-number slice suppress a halt
- **Claim under review**: `tools/stranded_slice_audit.py:267` `claims.get(name)` (+ L357) — slice number (regex group 1) discarded from the claim key.
- **Issue**: A genuinely-stranded `slice/400-foo` could be downgraded to CLAIMED-BY-OTHER (no halt) by a foreign claim on key `foo` from an unrelated `slice/600-foo`. Inert in solo-dev (one identity) and PSQ-1 itself keys candidates by bare name, but a real precedence-#1-over-#3 downgrade in the multi-session case.
- **Builder disposition**: **ACCEPTED-FIXED (option a — document the residual)** — design.md Claim-resolution note now names the collision as a known residual, bounded by PSQ-1's own bare-name keying; if PSQ keys ever gain slice numbers, key claims by `<NNN>-<name>`. (Given solo-dev inertness, no code change beyond documentation.)

### Minors

#### m1: `_is_terminal` substring match `"commit" in next_action` false-positives on `precommit`/`commitment`
- **Builder disposition**: **FIXED** — `re.search(r"\bcommit\b", ...)` word-boundary match.

#### m2: `_frontmatter_field` does not strip surrounding quotes — a quoted `stage: 'complete'` misses terminal detection
- **Builder disposition**: **FIXED** — `.strip().strip("'\"")` on the parsed value.

#### m3: redundant second `merge-base` call per bare branch (L250 + L262)
- **Builder disposition**: **OVERRIDDEN (no change)** — the two calls serve distinct purposes (ancestry-test vs no-common-ancestor detection for `ahead: null`); bare-branch count is realistically <10; not worth coupling. Noted.

## Dimensions checked
- [x] Unfounded assumptions — B1 (terminal stage assumed `reflect`, contradicted by `skills/reflect/SKILL.md:305`).
- [x] Missing edge cases — B1 (terminal `complete` on bare branch), m1 (`commit` substring), m2 (quoted scalar). CRLF/empty-frontmatter handled.
- [x] Over-engineering — none (5-class enum + dataclass all consumed; CLAIMED-BY-OTHER is justified forward-provision).
- [x] Under-engineering — B1 (the new-value bare-branch path under-delivered for the production vocabulary).
- [x] Contract gaps — public API type-hinted + docstringed; exit-code contract (0/2, no 1) correct. M2 (lossy claim key).
- [x] Security — none (read-only; list-form subprocess, no shell; cooperative-trust boundary documented).
- [x] Drift from vault — B1 was a drift from the milestone vocabulary written by `skills/reflect/SKILL.md`; inventory surfaces consistent; MEPD-1 EXCLUDE matches the diff (the 4 forward-sync drifts are sibling-induced by slice-088, out of scope); SKILL.md prose matches the JSON contract.
- [x] Web-known issues — none (git plumbing is stable/non-deprecated; WebSearch not run, no post-cutoff dependency).
- [x] Cross-cutting conformance — APED-1: the new parse rule (`_TERMINAL_STAGES`/`_is_terminal`) was not executed against the real vault vocabulary → B1/M1 (now fixed by adding the production-vocabulary case). EOL-DRIFT-1: `splitlines()` CRLF-safe. No phantom imports (4 reused symbols verified). Live parallel-safety confirmed (slice/087 → IN-PROGRESS, no halt).
