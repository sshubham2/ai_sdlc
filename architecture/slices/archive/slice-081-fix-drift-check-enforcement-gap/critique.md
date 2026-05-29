# Critique: Slice 081 fix-drift-check-enforcement-gap

**Critic reviewed**: mission-brief.md, design.md, ADR-073
**Date**: 2026-05-29
**Result**: NEEDS-FIXES

## Summary

The slice correctly diagnoses a real gap (drift-check is preached-but-unenforced, the R-7/slice-022 silent-disable class) and the procedural "was-it-run" gate is a sound, in-pattern choice. But the marker-matching contract rests on an LLM-authored, non-deterministic `**Trigger**:` line whose canonical template literally uses a *different* token shape (`sliceNN`, no dash) than the one the audit greps for (`slice-NNN`), which is both a false-refuse surface and a sibling-canonical-form drift. Two cross-doc harmonization obligations (Step 7b preservation, drift-log template) were unaddressed, and one citation (PTFFD-1) is wrong.

## Findings

### Blockers (must address before /build-slice)

#### B1: Marker-match token (`slice-NNN`) contradicts the drift-log skill's own canonical Trigger template (`sliceNN`)
- **Claim under review**: design.md Contracts marker-match: `**Trigger**:` line contains the current slice's `slice-NNN` token.
- **Issue**: The authoritative template `/drift-check` Full mode emits is `skills/drift-check/SKILL.md:114`: `**Trigger**: <pre-commit | manual | sliceNN pre-finish gate>` — `sliceNN`, no hyphen, no zero-padding. If Claude follows the template literally it writes `slice81`/`sliceNN`, and a DCE-1 audit grepping `slice-081` emits `drift-check-not-run` against a slice whose drift-check DID run — a false-refuse that HALTs the build. The 13 historical drift-log entries use the dash form by convergent habit, not contract.
- **Evidence**: `skills/drift-check/SKILL.md:114` (VERIFIED — template is `sliceNN`) vs `architecture/drift-log.md` (dash-form by habit) vs design.md marker-match.
- **Proposed fix**: tolerant regex anchored on the slice number AND canonicalize the producer template to `slice-NNN`; APED-1-execute against `slice-081`/`slice81`/`sliceNN`/`slice-0810`.
- **Builder draft**: **ACCEPTED-PENDING** — both legs adopted: (1) audit matches tolerantly via `slice[- ]?0*<N>\b` (resolves canonical + habit + sloppy forms; `\b`+`0*` reject `slice-0810`/`slice-081x`); (2) `skills/drift-check/SKILL.md:114` template canonicalized to `slice-NNN` form + pinned by a test. design.md updated now (What's-new B1 bullet + Contracts marker-match); APED-1 execution + code/template/test land in `/build-slice`. Confirmed VERIFIED against the file.

#### B2: Step 7b milestone-rewrite preservation of `drift-check-skip:` asserted in ADR but not delivered or in any AC
- **Claim under review**: ADR-073 / design.md — escape-hatch is a `drift-check-skip:` key in milestone.md frontmatter.
- **Issue**: CRP-1's escape-hatch only works because `skills/build-slice/SKILL.md:494` instructs the continuous Step 7b rewrite to preserve `critique-review-skip:` verbatim, and the Step 6 re-run reads it AFTER Step 7b fires. `drift-check-skip:` has the identical lifecycle but no deliverable edits L494 and no AC covered it — a legitimately escape-hatched slice would get its key clobbered then false-refused (the exact bug ADR-024 L494 prevents).
- **Evidence**: `skills/build-slice/SKILL.md:494` (VERIFIED — preserves only `critique-review-skip:`); `~/.claude/templates/milestone.md:22` (VERIFIED — shows only `critique-review-skip:`); original ACs 1–5 (none covered Step 7b).
- **Proposed fix**: add deliverable + AC: L494 lists `drift-check-skip:` alongside `critique-review-skip:`; document key in milestone template; verify template-drift/INST-1.
- **Builder draft**: **ACCEPTED-PENDING** — design.md updated now (new What's-new B2 bullet) + new AC #4 (escape-hatch lifecycle) added to mission-brief. The SKILL.md:494 + milestone-template edits + skip-accept/malformed-refuse fixtures land in `/build-slice`.

### Majors (address this slice)

#### M1: design.md names a nonexistent template file `tools/crp_audit.py` (premise INACCURATE); residue = enumerate verbatim-copy literals
- **Claim under review**: design cites "CRP-1 pattern"; ADR says "CRP-1 clone".
- **Issue (as filed)**: Critic claims design.md names a nonexistent `tools/crp_audit.py` and could mis-locate / paraphrase the template; wants the explicit source path + enumerated verbatim literals (`_SKIP_VALUE_RE` em-dash, `_frontmatter_*` helpers, `_resolve_mode` ladder, VAULT_ROOT routing, exit mapping).
- **Evidence**: `tools/critique_review_prerequisite_audit.py` (real CRP-1 tool); design.md.
- **Proposed fix**: replace bare "CRP-1" with the explicit path + enumerate inherited literals; add sibling-byte-faithfulness check to build plan.
- **Builder draft**: **ACCEPTED-PENDING** (premise correction noted) — the Critic's specific premise is INACCURATE: `design.md:19` has always named the real path `tools/critique_review_prerequisite_audit.py` (VERIFIED — `tools/crp_audit.py` appears nowhere in my design). The valuable residue is adopted: design.md What's-reused line now enumerates the byte-faithful literals to copy (em-dash `_SKIP_VALUE_RE`, helpers, `_resolve_mode` regex + ladder, VAULT_ROOT routing, exit mapping) + a `grep -n` sibling byte-faithfulness check in the build plan.

#### M2: The drift-log producer is LLM-authored prose; the gate verifies a marker, not the audit; `--fast` writes none
- **Claim under review**: design Step 6 wiring — "(a) runs /drift-check ... appends slice-referencing entry THEN (b) invokes the audit."
- **Issue**: `/drift-check --fast` writes NO drift-log entry (stdout only, `skills/drift-check/SKILL.md:87-105`); only full mode writes the marker (`:109-127`). The gate proves "a drift-log entry mentioning this slice exists" — a was-it-*marked* gate, not was-it-*run*. Should pin full-mode + honestly down-scope the language and disclose the residual gap (like NAW-1's known-false-positive disclosure).
- **Evidence**: `skills/drift-check/SKILL.md` --fast vs full mode (VERIFIED).
- **Proposed fix**: (1) require full mode at Step 6; (2) reframe AC/ADR from "enforces /drift-check-was-run" to "enforces a slice-referencing drift-log entry exists" + disclose residual gap.
- **Builder draft**: **ACCEPTED-PENDING** — design.md first What's-new bullet reframed to "was-it-marked gate" with explicit residual-gap disclosure; Step 6 wiring bullet now requires `/drift-check` full mode explicitly; ADR-073 Decision gains a "Scope honesty" paragraph. AC #2 updated to pin full mode. The binding Step 6 skill prose lands in `/build-slice`.

#### M3: AC count + new-rule/ADR/version-bump meta-obligations under-specified vs MCFS-1/AVFS-1/TVFS-1/entry-pin reality
- **Claim under review**: original AC #4 collapsed the multi-leg bump + entry-pin into one clause.
- **Issue**: VERSION is 0.75.0 (VERIFIED); the 4-part atomic bump is VERSION + plugin.yaml + pyproject.toml (TVFS-1 leg) + installed ai-sdlc-VERSION (AVFS-1) + forward-synced changelog (MCFS-1); plus the `test_v_0_76_0_*` entry-pin (slice-059 precedent). AC #4 omitted the entry-pin and was not cleanly testable.
- **Evidence**: `VERSION:1` (0.75.0); `methodology-changelog.md` head `## v0.75.0`; slice-059 entry-pin precedent.
- **Proposed fix**: split into 4a (4-part bump) / 4b (changelog entry + entry-pin) / 4c (PMI-1+INST-1 enumerate tool); name pyproject explicitly.
- **Builder draft**: **ACCEPTED-FIXED** — mission-brief ACs restructured (the old AC #4 is now AC #5, naming all four bump legs + the `## v0.76.0` entry + `test_v_0_76_0_dce_1_*` entry-pin + PMI-1/INST-1 enumeration). AC count is now 6 with a documented >5 rationale (slice-067/072 precedent). Verification plan updated to match.

### Minors (log; address if cheap)

#### m1: Exit-2 mode-unresolvable inherits CRP-1's CLAUDE.md fallback regex — verify it tolerates trailing prose
- **Issue**: CRP-1 `_resolve_mode` regex `^\*\*Mode\*\*\s*:\s*([A-Za-z]+)` captures `Standard` from `**Mode**: Standard — see architecture/triage.md`. A greedy paraphrase would break it.
- **Builder draft**: **ACCEPTED-PENDING** — subsumed by M1's verbatim-inheritance requirement (the regex is copied byte-for-byte, now enumerated in design.md). No separate action.

#### m2: ADR/design cite "fail-visible per PTFFD-1" — PTFFD-1 is the phantom-test-function rule, unrelated
- **Issue**: the fail-visible-over-false-FAIL principle is the STP-1/BCI-1/ADR-037 lineage, not PTFFD-1.
- **Builder draft**: **ACCEPTED-FIXED** — design.md Contracts error-cases line corrected to "ADR-037 / STP-1 / BCI-1 skip-with-note / fail-visible" with an explicit note that this corrects the m2 mis-citation.

#### m3: ADR-073 "no installed pre-commit hook" framing risks reopening the out-of-scope item
- **Issue**: Context cites the missing hook as gap evidence; a reader could read the ADR as promising hook installation.
- **Builder draft**: **ACCEPTED-FIXED** — ADR-073 Decision gains an explicit clause: the pre-commit hook remains out-of-scope; DCE-1 enforces at /build-slice Step 6 only.

## Dimensions checked
- [x] Unfounded assumptions — B1 (marker token assumed but contradicted by producer template), M2 (entry assumed reliably written; --fast writes none). Verified against implementation, not just prose.
- [x] Missing edge cases — B1 (false-refuse on token mismatch), M2 (--fast / hand-written entry), m1 (mode regex on trailing prose).
- [x] Over-engineering — none (design correctly rejects re-implementing semantic drift; minimal procedural closure).
- [x] Under-engineering — B2 (Step 7b preservation named but undelivered), M3 (entry-pin + 4-part bump meta-ACs under-specified). TF-1 N/A (Test-first: false).
- [x] Contract gaps — B1 (producer/consumer token mismatch), M2 (full-vs-fast not pinned). Exit-code 0/1/2 otherwise sound.
- [x] Security — none (no auth/network/secret/untrusted-input surface; local repo reads under same trust boundary as sibling audits).
- [x] Drift from vault — M1 (premise inaccurate — design names the real path; verbatim-literal residue adopted), m2 (PTFFD-1 miscitation). ADR-073 extends CRP-1/ADR-024 + R-7/slice-022 lineage; supersedes null, correct.
- [x] Web-known issues — none (in-house Python stdlib; no external API/SDK surface). Git-hook claim correctly out-of-scope (m3).
- [x] Cross-cutting conformance — B1 (sibling-canonical-form drift + APED-1), B2 + M3 (TPHD-1 cross-doc harmonization). Bootstrap correctly structured (CRP-1/PCA-1/NAW-1 precedent) but its discharge depends on B1 being fixed.

## Triage

**Triaged by**: user
**Date**: 2026-05-29
**Final verdict**: NEEDS-FIXES

Reconciles both passes: first Critic (critique.md) + meta-Critic (critique-review.md, dual-review verdict EXTEND — M1 re-graded SUSPICIOUS/Minor; M-add-1 + m-add-1 added as missed findings). User ratified all Builder drafts as-is (TRI-1, 2026-05-29).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Line-anchored + slice-anchored tolerant matcher + producer-template canonicalization + pin test; design spec applied, code/template/test at /build-slice |
| B2 | Blocker | ACCEPTED-PENDING | `drift-check-skip:` added to design + AC4; `build-slice:494` preserved-keys edit + milestone-template doc + accept/malformed fixtures at /build-slice |
| M1 | Minor | ACCEPTED-PENDING | Re-graded Major→Minor per meta-Critic (filed-premise `tools/crp_audit.py` is false — design always cited the real path); residue adopted = verbatim-literal enumeration (applied to design) + `grep -n` byte-faithfulness check at build |
| M2 | Major | ACCEPTED-PENDING | Honest "was-it-marked" reframe + residual-gap disclosure applied to design+ADR; full-mode requirement pinned in AC2; binding Step 6 prose at /build-slice |
| M3 | Major | ACCEPTED-FIXED | Mission-brief ACs restructured to 6; AC5 names all 4 bump legs + `test_v_0_76_0_dce_1_*` entry-pin + PMI-1/INST-1 enumeration; verification plan updated |
| m1 | Minor | ACCEPTED-PENDING | Subsumed by M1 verbatim-inheritance (`_resolve_mode` regex copied byte-for-byte); no separate action |
| m2 | Minor | ACCEPTED-FIXED | design Contracts error-cases citation corrected PTFFD-1 → ADR-037/STP-1/BCI-1 |
| m3 | Minor | ACCEPTED-FIXED | ADR-073 Decision gains explicit pre-commit-hook-out-of-scope clause |
| M-add-1 | Major | ACCEPTED-PENDING | (meta-Critic missed-finding) Matcher now line-anchored to `**Trigger**:` lines (design applied); build implements anchored matcher + M-add-1 negative fixture (cross-mention → exit 1) |
| m-add-1 | Minor | ACCEPTED-PENDING | (meta-Critic) design bootstrap updated to require a `**Trigger**: slice-081` line; build adds APED-1 assertion that slice-081's written entry exits 0 under the anchored matcher |
