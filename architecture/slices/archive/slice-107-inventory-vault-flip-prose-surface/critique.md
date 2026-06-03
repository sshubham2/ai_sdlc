# Critique: Slice 107 inventory-vault-flip-prose-surface

**Critic reviewed**: mission-brief.md, design.md, project-frame.md, new ADRs (ADR-096, ADR-097)
**Date**: 2026-06-03
**Result** (Critic's assessment): BLOCKED — final verdict set at TRI-1 below
**Critic**: separate `critique` agent (subagent), 14 tool-uses, executed the real `_SLASHED_RE` + `_classify_constant` + count-regexes against the live corpus (APED-1 / AP-3 — findings are reproductions, not hypotheticals)

## Summary

The slice's intent (inventory + drift-guard the prose vault-location surface, fail-closed) is sound and well-scoped, and the disjointness-from-slice-106 core claim survived empirical execution. Three load-bearing claims failed against the real corpus: (B1) the anchored match regex silently misses 33 operational literals incl. git-pathspecs; (B2) 119 inline-code operational paths default to the non-gating `doc-example` class so the fail-closed backstop never fires (AP-12 + AP-16); (B3) the corpus-size claim was grep-reasoned (~318) and contradicts the tool's anchored matcher (~285). All three + the three Majors + two Minors were accepted by the Builder; the design was corrected in-round for the design-level items.

## Findings

### Blockers (must address before /build-slice)

#### B1: `_SLASHED_RE` delimiter-class silently drops 33 operational git-pathspec vault literals — the inventory is not complete
- **Claim under review**: design.md Match rule — anchored slashed-prefix form `(?:^|[\s'"(`/=])(?:architecture|diagnose-out)/` mirroring `readiness_audit._SLASHED_RE`; "documented residual" = bare vault-dir argument only.
- **Issue**: Executed both regexes over the real corpus. Anchored `_SLASHED_RE` = **285** matches; the mission-brief's own smoke-gate grep `(architecture|diagnose-out)/` = **318**. The 33-gap is dominated by operational git-pathspecs in `skills/code-review/SKILL.md:48-57,103` (`:(exclude)architecture/decisions/**`, `:(glob)architecture/*.md`, `:(exclude)architecture/slices/_index.md`) where the char before `architecture/` is `)` (not in the delimiter class). These resolve at runtime and **break at M4 flip**, yet are invisible to the tool. The "documented residual" covered only the 9-hit bare-`graphify vault architecture` case, NOT this 33-occurrence delimiter-class hole. A "complete checklist that can never silently drift" that omits a tool's own git-pathspec block is the exact failure the slice exists to prevent.
- **Evidence**: anchored 285 (259 skills + 16 agents + 10 root) vs bare 318 (292 + 16 + 10); 33/33 anchored-misses preceded by `)` or `{`; hotspot `skills/code-review/SKILL.md:48-57,103`.
- **Proposed fix**: replace the anchored regex with boundary-free `(architecture|diagnose-out)/` for the prose surface (the Python-token anchor does not transfer to prose), catching the 33; reconcile the corpus count.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Match rule + mission-brief AC1 — switched to boundary-free `(?:architecture|diagnose-out)/`; the 33 git-pathspecs are now enumerated and classify `rewrite-at-flip` via ruleset rule 4's pathspec sink; the residual is narrowed to the 9 bare-arg hits ONLY, pinned by `test_bare_vault_dir_arg_residual`.

#### B2: 119 inline-code operational paths route to `doc-example` instead of `rewrite-at-flip` — ambiguity re-routed off the gate (AP-12 / AP-16)
- **Claim under review**: design.md ruleset rule 4 (imperative verb set `{read,run,check,consult,see,open}` → rewrite-at-flip) + rule 5 (no verb → `doc-example`). mission-brief Must-not-defer fail-closed claim.
- **Issue**: Of 285 matches, 227 are inline-code; **119** of those sit on lines with NO verb from the design's 6-verb set, so rule 4 fails and rule 5 confidently assigns `doc-example` (non-gating, not on the M4 checklist). But these are operational paths the flip MUST rewrite: `Write \`architecture/concept.md\``, `mv architecture/slices/slice-NNN-* architecture/slices/archive/`, `Update \`architecture/.../milestone.md\``. The governing verbs (`Write, mv, Update, Note, verify, ls`) are absent from the set. AP-12: ambiguity is re-routed into a non-gating class, not resolved. AP-16: the classification verb-set is inconsistent with the corpus's real operational vocabulary. The fail-closed `needs-human` backstop NEVER fires for these 119 because rule 5 catches them first with a confident (wrong) class.
- **Evidence**: context partition fenced=55, inline=227, plain=3; 119/227 inline lines carry none of the 6 verbs; samples `skills/adopt/SKILL.md:231,273`, `skills/archive/SKILL.md:51,76`, `skills/build-slice/SKILL.md:564`, `skills/code-review/SKILL.md:160,164`, `skills/commit-slice/SKILL.md:45`.
- **Proposed fix**: make `needs-human` the default for inline-code not positively classified; reserve `doc-example` for genuine plain prose; expand the operational-verb/sink set to the corpus vocabulary; push the residue to the ADR-097 disposition table.
- **Builder draft**: **ACCEPTED-PENDING** — design.md ruleset rules 4/5/6 restructured in-round (inline-code/fenced/pathspec literals default to `needs-human`, NOT `doc-example`; `doc-example` reserved for plain prose; operational verb/sink set expanded to `read,run,check,consult,see,open,write,mv,move,update,note,verify,ls,cat,create,delete,rm,append,regenerate` + pathspec + fenced/list-step adjacency). **Build obligation**: implement the expanded ruleset AND write a test asserting the ~119 verb-ambiguous inline-code paths route to `needs-human` (surfaced for disposition), never silently to `doc-example` — proven non-vacuous by mutation (AP-5).

#### B3: Internally-inconsistent corpus-size claim (~318 vs tool's ~285) — count was reasoned, not executed (AP-3)
- **Claim under review**: mission-brief / design "~318 ... skills 292"; mission-brief smoke "spot-check vs grep (~318 raw)".
- **Issue**: ~318/292 is the boundary-free grep count; the anchored `_SLASHED_RE` yields 285/259. The design pinned its corpus at one number while the tool would report another (= the B1 hole). The smoke-gate spot-check "vs ~318 raw" would mismatch 285-vs-318 and either be hand-waved (masking B1) or fail. AP-3: the corpus size was grep-reasoned, not run through the actual classifier.
- **Evidence**: skills bare 292 vs anchored 259; agents 16=16; root 10=10.
- **Proposed fix**: re-derive by running the actual tool after the regex decision; update every count site; make the smoke spot-check compare against the tool's own matcher.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Prose surface + mission-brief AC1/smoke — with the boundary-free regex (B1) the tool's count == the grep count (≈318), resolving the contradiction; the smoke spot-check now compares the tool's OWN count vs the grep (the anchored regex is explicitly NOT the comparison baseline). Exact per-surface numbers are pinned by running the built tool when the baseline is created (normal baseline-pinning).

### Majors (address this slice)

#### M1: Self-pollution guard holds for named constants but is under-specified for path-construction
- **Claim under review**: design.md Disjointness — "tool constructs no vault paths in practice none"; mid-slice smoke as the only guard.
- **Issue**: Critic executed `readiness_audit.audit_file` on a fixture mimicking the tool: bare `frozenset({"architecture","diagnose-out"})` → `doc-example-safe` (guard holds), but ANY `root / "architecture" / ...` → `must-rewrite-before-flip` → lands in `_BASELINE_CLASSES` → trips slice-106's re-pinned baseline. The guard rests on a discipline not mechanically enforced beyond the once-fired mid-slice smoke; a late path-construction edit would not be re-checked.
- **Evidence**: fixture exec — frozenset members → 2× `doc-example-safe/prose-mention`; `root / "architecture" / "x"` → `must-rewrite-before-flip`.
- **Proposed fix**: add readiness `--strict` to pre-finish (not only mid-slice); name the mechanical discipline (vault dir names only as bare-segment frozenset / regex source, never a `/`-BinOp operand or `Path(...)` arg).
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Disjointness + mission-brief Pre-finish gate — readiness `--strict` exit-0 added to the pre-finish gate; the bare-segment/regex-only discipline named as a hard must-not-defer.

#### M2: ADR-097 normalized-line-context disposition key has a duplicate-line collision failure mode
- **Claim under review**: ADR-097 — key `(relpath, normalized-line-context)`, claimed "per-occurrence".
- **Issue**: The key is per-LINE-TEXT, not per-occurrence; identical lines recur (`architecture/slices/slice-NNN-` ×10 in `skills/build-slice/SKILL.md`). Two same-text lines needing different classes (one in a fenced example, one a live instruction) collapse to one key; rule 1 then assigns both the same class, silently mis-classifying one — and the fail-closed backstop can't save it once a disposition row exists.
- **Evidence**: `architecture/slices/slice-NNN-` ×10 in one file (Counter executed).
- **Proposed fix**: either document per-line co-classification + pin a no-ambiguous-duplicate test, or strengthen the key with fence-state / occurrence-ordinal.
- **Builder draft**: **ACCEPTED-FIXED** at ADR-097 §Decision + design.md §Baseline — key strengthened to the 4-tuple `(relpath, normalized-line-context, fence-state, ordinal-among-identical-lines)`; a pinned `test_no_ambiguous_duplicate` proves the corpus has no two same-key occurrences needing different classes; a reordering edit re-surfaces affected occurrences as `needs-human` (safe failure direction).

#### M3: ADR-096/097 number collision with parallel slice-106 — "rename at merge" understates 14-site fan-out (AP-10/AP-13)
- **Claim under review**: design.md — collision "resolved at merge by renaming one set ... mechanical, non-semantic".
- **Issue**: Confirmed likely on disk (master=ADR-095, slice-107 authored 096/097, slice-106 not yet). `ADR-096`/`ADR-097` are referenced 14× across slice-107's artifacts; a hand rename that misses one orphans a `[[ADR-096]]` link.
- **Evidence**: worktree/ADR-dir listing + 14 `ADR-09[67]` refs (grep).
- **Proposed fix**: (a) reserve 096/097 for slice-107 now via cross-session coordination so slice-106 mints 098+; or (b) grep-verified rename enumeration at merge.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Parallel-coordination — recorded option (a) preferred (surfaced at the TRI-1 gate as a cross-session coordination action: direct the slice-106 session to mint ADR-098+) + option (b) grep-verified `ADR-09[67]` enumeration as the merge fallback. **Requires a user coordination decision at TRI-1.**

### Minors (log; address if cheap)

#### m1: Taxonomy class-name strings diverge between the slice's taxonomy and the readiness tool it mirrors
- **Issue**: The slice invents `rewrite-at-flip|historical-anchor|doc-example|needs-human` while "mirroring" readiness_audit's `must-rewrite-before-flip|already-seam-routed|doc-example-safe|needs-human-classification`; design.md also uses "must-rewrite" in places.
- **Proposed fix**: pick one set, document deliberately-distinct, ensure mission-brief/design/test/`--json` agree.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Taxonomy contract — the four prose class-strings documented as deliberately distinct from readiness_audit's (prose ≠ production surface); the design's "must-rewrite" mentions are explicit cross-references to readiness_audit's OWN class, not the prose tool's. (Note: the Critic's "design mixes the two" is partly a cross-reference, not drift — clarified rather than rewritten.)

#### m2: `--strict` baseline pins only `rewrite-at-flip + needs-human`; a `historical-anchor ↔ doc-example` flip (or a `rewrite-at-flip → doc-example` demotion) is undetected
- **Issue**: Mirrors readiness's `_BASELINE_CLASSES`; on the prose surface a `rewrite-at-flip → doc-example` demotion silently shrinks the checklist without tripping `--strict`. Given B2 shows `doc-example` is exactly where mis-classification lives, leaving it unpinned is a gap for THIS surface.
- **Proposed fix**: pin `historical-anchor` and/or a total-occurrence-count floor.
- **Builder draft**: **ACCEPTED-FIXED** at design.md §Baseline — added a pinned per-class total-count floor for all four classes; `--strict` exits 2 on any per-class total-count shrink (closes the silent-demotion direction).

## Dimensions checked
- [x] **Unfounded assumptions** — B1 (residual asserted small but real gap=33 incl. operational pathspecs), B3 (count grep-reasoned, contradicts the tool's matcher), M1 ("in practice none" path-construction — verified against the actual classifier). Verified by reading + executing the implementation, not the prose.
- [x] **Missing edge cases** — B1 (delimiter-class boundary `)`-prefixed pathspecs), M2 (duplicate identical lines in one file). Load/network/permission N/A (read-only local CLI).
- [x] **Over-engineering** — none. Tool is appropriately thin; standalone-vs-branch (ADR-096) justified by the disjointness constraint; disposition table is the minimum fail-closed mechanism.
- [x] **Under-engineering** — B2 (AC#2 "fails closed" not delivered for the 119 — confidently route to doc-example), B1 (AC#1 "enumerates EVERY literal" not delivered — 33 invisible). PMI-1/INST-1/RPCD-1/SCPD-1 correctly listed.
- [x] **Contract gaps** — m1 (`--json` `klass` string contract nailed down). Exit-code contract (0/2/1) fully specified. No auth/pagination/idempotency surface.
- [x] **Security** — none. Read-only local CLI; no auth/network/tracked-write/secrets/injection/PII.
- [x] **Drift from vault** — M3 (ADR-096/097 collision with parallel slice-106; both confirmed on disk). No existing-ADR contradiction (091/092 mirrored, not superseded); R-32 correctly NOT claimed retired. Strategic-fit (project-frame): advances the R-32/external-vault trajectory; B2's `doc-example` default was itself a silent-under-report (R-7-shaped) risk — now closed.
- [x] **Web-known issues** — N/A: pure-stdlib in-house audit, no external tech/API/library.
- [x] **Cross-cutting conformance** — APED-1 (headline — all findings executed against the real corpus). AP-16 (B2 verb-set inconsistency), AP-12 (B2 ambiguity re-routed off gate), AP-1 (line-anchored — required, not violated), FBCD-1 (B3 count drift; M3 14-site ADR fan-out), AP-10/AP-13 (M3 rename-orphans-citations).

## Triage

**Triaged by**: user
**Date**: 2026-06-03
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes (first Critic B*/M*/m* + meta-Critic M-add-*/m-add-* from [critique-review.md](critique-review.md); dual-review verdict EXTEND). The first Critic's B1/B3 corpus arithmetic was corrected per the meta-Critic (real anchored=69, gap=249, not 285/33; Builder-re-verified: boundary-free=318, anchored=69, intra-line multi-match=24 lines/32 extra, code-review.md:103=5).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §Match rule + §Prose surface — boundary-free `(?:architecture\|diagnose-out)/` matcher; dual-review arithmetic correction (69/249) applied + Builder-re-verified |
| B2 | Blocker | ACCEPTED-PENDING | design.md ruleset rules 4/5/6 restructured (inline-code/fenced/pathspec default → `needs-human`; `doc-example` reserved for plain prose); BUILD implements the expanded operational verb/sink set + a test that the ~119 verb-ambiguous inline paths route to `needs-human`, never silent `doc-example` (proven by mutation) |
| B3 | Blocker | ACCEPTED-FIXED | boundary-free → tool count == grep == 318 (all-matches-per-line `re.finditer`); smoke spot-check asserts `==318`; design/brief count sites corrected |
| M1 | Major | ACCEPTED-FIXED | `vault_flip_readiness_audit --strict` exit-0 added to the PRE-FINISH gate (not only mid-slice) + the bare-segment/regex-only path-construction discipline named as must-not-defer |
| M2 | Major | ACCEPTED-FIXED | disposition key strengthened to the 5-tuple `(relpath, normalized-line, fence-state, ordinal-among-identical, column-offset)` + `test_no_ambiguous_duplicate` |
| M3 | Major | ACCEPTED-FIXED | **user-ratified option (a)**: ADR-096/097 reserved for slice-107; slice-106 session directed to mint ADR-098+ (reservation noted in `slice-queue.md` on master); option (b) grep-verified rename retained as merge fallback |
| m1 | Minor | ACCEPTED-FIXED | design.md §Taxonomy contract — the 4 prose class-strings documented as deliberately distinct from readiness_audit's |
| m2 | Minor | ACCEPTED-FIXED | per-class total-count floor pinned in the baseline (closes silent `rewrite-at-flip → doc-example` demotion) |
| M-add-1 | Major | ACCEPTED-FIXED | intra-line multi-match closed: column-offset 5th key component + `re.finditer` all-matches-per-line + `test_no_intra_line_ambiguous_multimatch` (`code-review.md:103` fixture); ADR-097 updated |
| M-add-2 | Major | ACCEPTED-FIXED | **user-ratified**: `Test-first` flipped false→true (mirror slice-100/102) + 11-row Test-first plan added; `test_first_audit --strict-pre-finish` gates at build |
| m-add-1 | Minor | ACCEPTED-PENDING | BUILD greps `\bdiagnose-out\b` not-followed-by-`/` across the 5 prose globs; folds operational hits into the residual list or confirms empty (pinned by `test_bare_vault_dir_arg_residual`) |
