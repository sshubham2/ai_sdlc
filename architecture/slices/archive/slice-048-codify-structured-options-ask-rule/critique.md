# Critique: Slice 048 codify-structured-options-ask-rule

**Critic reviewed**: mission-brief.md, design.md, ADR-050
**Date**: 2026-05-19
**Result**: NEEDS-FIXES

## Summary

Platform premise sound (WebSearch + ADR-048 confirm Claude Code does not notify on free-text prompts); genuine-contrast precondition holds (pinned literal absent from all 5 surfaces pre-edit). But the design's "no per-version changelog test" correction misreads what MCFS-1/slice-041 retired — contradicted by the three immediately-preceding slices — a Dimension 7 false-precedent **blocker**. Two majors (AC5 pin internally inconsistent; free-text escape-hatch wording conflates two distinct cases) and two minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: Design's "no per-version changelog test" correction misreads what MCFS-1 retired

- **Claim under review**: design.md "Design corrections": *"adding a test_v_0_56_0_* read would re-introduce exactly the per-version coupling slice-041/MCFS-1 retired."*
- **Issue**: MCFS-1 retired the per-version *installed-copy forward-sync reads* (`test_v_0_NN_0_*` functions reading `~/.claude/methodology-changelog.md`), re-homed onto the whole-file `methodology_changelog_forward_sync.py` gate. It did NOT retire the in-repo `_entry_present_in_repo` pin. Slice-041 itself (v0.53.0/MCFS-1) added `test_v_0_53_0_mcfs_1_entry_present_in_repo` + `_shippability_consumer_propagation`; slice-044 (v0.54.0/STP-1) added both; slice-046 (v0.55.0/BFRD-1) added the entry-pin. The pin convention is unbroken across the three slices preceding this one. Shipping SOAD-1 with no entry-pin breaks the convention silently and leaves v0.56.0 with no entry-level regression guard. False-precedent class (slice-032 m1 / MEPD-1).
- **Evidence**: `tests/methodology/test_methodology_changelog.py` L2921/L2980/L3024/L3068/L3097 (Builder-verified by direct grep + read, not prose).
- **Proposed fix**: Path (a) — add `test_v_0_56_0_soad_1_entry_present_in_repo` + `test_v_0_56_0_soad_1_shippability_consumer_propagation` modeled on the v0.54.0 STP-1 shape; add shippability catalog row for v0.56.0.
- **Builder draft**: **ACCEPTED-FIXED** — Critic correct, verified against `test_methodology_changelog.py` (recompute-don't-trust, N≥4 lesson). design.md "Design corrections" #2 reversed; test plan + AC1 amended to add the two per-version pins (v0.54.0 STP-1 shape) + shippability row #48. Fix applied at design.md "What's new" / "What's reused" / new "## Changelog entry-pin plan" section.

### Majors (address this slice)

#### M1: AC5 pin spec internally inconsistent (full sentence vs prefix substring vs "≥2 occurrences each")

- **Claim under review**: design.md *"≥2 occurrences each in triage/adopt SKILL.md"* + Append-template "prefix substring only" + a longer "stable pinned substring".
- **Issue**: (1) a global `.count() >= 2` passes even if both hits land in Fresh and Append is missed (must-not-defer requires both); (2) the long sentence won't be present verbatim if Append carries only the prefix; (3) the rationale pin fails in Append if Append drops the rationale clause.
- **Evidence**: design.md "Canonical sentence"/"Stable pinned substring"; `test_root_claude_md_branch_per_slice_rule.py` (precedent uses section-scoped `.find()`, not global count).
- **Proposed fix**: One short canonical sentence (mechanic + rationale + escape hatch) reused VERBATIM in all 5 surfaces; test asserts that exact literal inside each of the 4 fenced template blocks + CLAUDE.md independently (section-scoped, slice-021 precedent shape).
- **Builder draft**: **ACCEPTED-FIXED** — canonical sentence rewritten compact enough for the Append blocks while carrying mechanic + rationale + escape hatch; one verbatim literal in all 5 surfaces; AC5 test spec changed to per-fenced-block scoped assertion (no global `.count()`). Fix applied at design.md "Canonical SOAD-1 sentence" + test component.

#### M2: Free-text escape-hatch wording conflates the tool's built-in fallback (notifies) with ADR-048's bare-prose verbal-claim fallback (does NOT notify)

- **Claim under review**: design.md canonical sentence: *"Free-text stays available via the tool's built-in fallback."*
- **Issue**: The `AskUserQuestion` built-in free-text option is still an options prompt and DOES notify; ADR-048's verbal-claim-with-path bare prose ask does NOT notify and is the genuine escape hatch must-not-defer #4 protects. The shipped rule must carve out the notification-less case, not teach "any tool-fallback free-text is fine".
- **Evidence**: WebSearch (Claude Code agent-SDK user-input docs; anthropics/claude-code#13830; Piebald-AI system-prompt mirror) vs ADR-050 §Decision L31.
- **Proposed fix**: Escape-hatch clause names the genuinely-notification-less case: "A bare prose ask is legitimate only where `AskUserQuestion` genuinely cannot model the input."
- **Builder draft**: **ACCEPTED-FIXED** — canonical sentence's escape-hatch clause rewritten to the M2-proposed wording (aligns shipped rule text with ADR-050 §Decision + must-not-defer #4). Fix applied at design.md "Canonical SOAD-1 sentence".

#### M-add-1: SOAD-1 ships verbatim inside templates that contain a bare free-text ASK the rule forbids (meta-Critic missed finding, DR-1 EXTEND)

- **Claim under review**: design.md adds the SOAD-1 sentence ("never a bare free-text prompt") to the same 4 fenced template blocks that already contain the hard-rule line `2. If none → **ASK** the user: "Run \`/slice\` first, or is this small enough to skip?"` (triage Fresh L224 / Append L248; adopt Fresh L373 / Append L404; + this repo's CLAUDE.md).
- **Issue**: a generated `./CLAUDE.md` would carry SOAD-1 and, ~20 lines above it, a bare free-text ASK — a shipped self-violation of the discipline being minted (slice-022 self-violation law / RSAD-1 recursive-self-application). The genuine-contrast test + must-not-defer #1 do nothing about the co-located contradiction.
- **Evidence**: `skills/triage/SKILL.md` L224/L248; `skills/adopt/SKILL.md` L373/L404; `CLAUDE.md` "Hard rule before editing code".
- **Proposed fix**: (a) reword the hard-rule ASK line in all 4 template blocks + this repo's CLAUDE.md to structured-options form (templates become self-consistent with SOAD-1); OR (b) scope SOAD-1 explicitly to *skill* AskUserQuestion ask-points and declare the CLAUDE.md hard-rule ASK out of scope via an ADR-050 scoping clarification. Design-level scoping decision — needs user ratification at TRI-1.
- **Builder draft**: **ACCEPTED-FIXED via option (a)** — recommend (a) over (b): SOAD-1's own rationale (the user is not notified on free-text) applies *most* to the hard-rule ASK (a critical gate); option (b) would carve out exactly the ask that most needs the rule. Option (a) is a surgical one-line reword per block (`**ASK** the user:` → `**ASK** the user via structured options (per the Ask discipline below):`), keeps the hard rule intact, makes the slice satisfy its own rule (RSAD-1), and does not blow scope. Pending user choice at TRI-1 (a vs b).

### Minors (log; address if cheap)

#### m1: design.md line-range citations are brittle

- **Issue**: L212–238 / L242–253 / L360–394 / L398–409 drift on any edit; structural anchors (`#### Fresh template`, `#### Append template`) are stable.
- **Builder draft**: **ACCEPTED-FIXED** — line-number citations demoted to "(informational; anchor edits on the `#### …template` heading + fence)". Cheap; applied at design.md.

#### m2: shippability row #48 forward-asserted

- **Issue**: Row number should be `max(existing)+1`; currently 47 rows (row 47 = slice-047) → 48 correct, but assert as max+1 not a hard literal.
- **Builder draft**: **ACCEPTED-FIXED** — design.md notes row = `max(existing)+1` (currently 48; confirm at /reflect Step 5.3 against then-current max). Cheap; applied.

## Dimensions checked

- [x] Unfounded assumptions — B1 (false-precedent, verified against artifact). Platform premise itself founded (WebSearch + ADR-048).
- [x] Missing edge cases — none material (markdown-prose-only; no runtime/load/concurrency surface). Pin ambiguity captured at M1.
- [x] Over-engineering — none (one sentence + one prose-pin test + one ADR; Standard-mode thin-vault respected).
- [x] Under-engineering — B1 (missing entry-pin breaks 3-slice convention); M1 (AC5 internally inconsistent).
- [x] Contract gaps — none (no runtime contract; correctly stated).
- [x] Security — none (prose discipline; no auth/input/secret/data path).
- [x] Drift from vault — B1 (false-precedent / MEPD-1). ADR-050 supersession claim verified accurate (does NOT supersede ADR-048; ADR-048 on-disk text confirms BFRD-1-gate AskUserQuestion mandate).
- [x] Web-known issues — M2. Premise verified SOUND (anthropics/claude-code#13830 open feature request — no notification on free-text); nuance: tool built-in free-text DOES notify, distinct from ADR-048 bare-prose (M2).
- [x] Cross-cutting conformance — B1 = MEPD-1 + Dimension-4 methodology-audit-conformance sub-class. RSAD-1: SOAD-1 governs skill runtime asks not design docs (no self-violation). PTFCD-1/PTFFD-1: AC5 test file correctly created-not-cited; TF-1=false (no phantom-citation risk). APED-1: N/A (prose-pin, not a parse-rule change).

## Triage

**Triaged by**: user
**Date**: 2026-05-19
**Final verdict**: CLEAN

Dual-review (DR-1): EXTEND — first Critic's B1/M1/M2/m1/m2 all VALID + correct severity (0 suspicious, 0 severity adjustments); +1 missed Major M-add-1. User reconciled both passes at TRI-1 2026-05-19: M-add-1 → fix option (a); B1/M1/M2/m1/m2 → all Builder drafts accepted as-is.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md per-version-test correction reversed; v0.54.0-STP-1-shape entry-pin + propagation pin + shippability row (max+1) added to plan (verified vs test_methodology_changelog.py) |
| M1 | Major | ACCEPTED-FIXED | one verbatim canonical sentence in all 5 surfaces; AC5 test per-fenced-block scoped (slice-021 precedent), no global .count() |
| M2 | Major | ACCEPTED-FIXED | escape-hatch clause rewritten to the notification-less bare-prose case (aligns with ADR-050 §Decision + must-not-defer #4) |
| M-add-1 | Major | ACCEPTED-FIXED | user-ratified fix option (a) at TRI-1: reword the hard-rule ASK in all 5 surfaces to structured-options form so the slice satisfies its own rule (RSAD-1); recorded in design.md "What's new" |
| m1 | Minor | ACCEPTED-FIXED | line-numbers demoted to informational; edits anchor on heading+fence |
| m2 | Minor | ACCEPTED-FIXED | row = max(existing)+1 (48 now); confirm at /reflect |
