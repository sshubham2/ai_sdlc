# Critique: Slice 095 harden-skill-driven-vault-writes

**Critic reviewed**: mission-brief.md, design.md, ADR-087, project-frame.md, aggregated lessons, ADR-029 / ADR-085 / ADR-086 precedents
**Date**: 2026-06-01
**Result**: NEEDS-FIXES (2 blockers, 3 majors, 2 minors — all ACCEPTED; verdict pending user TRI-1)
**Critic**: separate `critique` agent (subagent_type: critique), ran 21 tool-uses / 98.8k tokens, executed the matcher against the live tree

## Summary

The append/rewrite split, the slice-093 sidecar-lock mechanism, and the "narrow not retire R-32" decision are sound and well-grounded. Two findings cut at load-bearing claims: (B1) AC2 is a static prose audit — the LLM-prose-inspection shape ADR-029/BCI-1 rejected — so its "completeness guarantee" is over prose, not writes; (B2) the "code-grounded enumeration" is demonstrably incomplete (26 skills not 23; misses `/repro` shippability-append + `/supersede-slice` `_index` RMW). The Critic EXECUTED the matcher rather than reasoning about it (APED-1), which is how it found the real gaps.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC2's static prose audit is the LLM-prose-inspection control ADR-029 rejected; it does not meet the BCI-1 "deterministic downstream gate" bar
- **Claim under review**: design.md §What's new — "the AC2 audit is the structural completeness guarantee"; ADR-087 repeatedly "mirrors VWS-1."
- **Issue**: VWS-1 (slice-094) is an AST audit over executable code — the parsed write op IS the ground-truth write. SVW-1 audits SKILL.md *prose* (a description of intent); the actual runtime write is Claude invoking `Write`/`Edit`, which a static audit cannot observe. So AC2's "completeness guarantee" guarantees the *prose says* the safe thing, not that *any write is safe* — exactly ADR-029's rejected Options 1+2 (harden/route the LLM prose) vs its chosen Option 3 (a deterministic downstream gate). Fail-closed-over-prose ≠ fail-closed-over-writes.
- **Evidence**: `ADR-029-*.md` §Options considered; slice-094 `ADR-086` §Decision; design.md §"Honest residual"; slice-030A precedent.
- **Proposed fix**: Don't redesign the mechanism — correct the *claim*. Scope SVW-1's guarantee to the prose-detection surface; add an ADR-087 §Consequences bullet acknowledging it IS the ADR-029-rejected shape and stating *why acceptable here* (no oracle artifact for LLM-authored content, unlike build-checks' canonical fixture).
- **Builder draft**: **ACCEPTED-FIXED**. design.md §What's new AC2-framing-corrected bullet (completeness over prose-detection surface, NOT writes) + new §"Why SVW-1 is acceptable despite ADR-029" (the no-oracle distinction from BCI-1) + ADR-087 §Consequences bullet rewritten. The mechanism (wrapper + prose-audit + concurrency proof) is unchanged; only the over-claim is corrected. The slice's value stands: wrapper = real safe channel when used; audit = drift-prevention (prose stays honest); concurrency proof = channel validated.

#### B2: The "code-grounded enumeration" of mutators is incomplete and the corpus size is mis-stated
- **Claim under review**: design.md §mutator set — "grep … yields the concurrent mutators below … /reflect + /archive"; "the real 23-skill corpus" (×4).
- **Issue** (Critic executed the matcher): (1) **26 skills**, not 23 (live `Glob` + INST-1 history). The "23-skill corpus" is the literal APED-1 target — a battery over 23 of 26 is incomplete by construction. (2) Two genuine sites missed: `skills/repro/SKILL.md:107` "Append a new entry to `architecture/shippability.md`" (append-class concurrent mutator, NOT in routing scope → would self-flag at build); `skills/supersede-slice/SKILL.md:103` "Update `architecture/slices/_index.md`" (`_index` RMW, must be exempt-marked). (3) `skills/build-slice/SKILL.md:394` is a real matcher false-positive (past-tense prose, not a directive).
- **Evidence**: live `Glob skills/*/SKILL.md`→26; grep→`repro:107`, `supersede-slice:103`, `build-slice:394`(FP).
- **Proposed fix**: 23→26 at all 4 sites; add `/repro` (route) + `/supersede-slice` (exempt-rmw) to the table; note the `build-slice:394` FP the matcher must NOT flag.
- **Builder draft**: **ACCEPTED-FIXED**. Corrected 23→26 (design.md L18/L33/L65 + ADR-087); mutator table adds `/repro` (route → `vault_edit append`) and `/supersede-slice` (exempt `deferred-rmw`); `build-slice:394` recorded as a must-stay-clean-without-exemption FP; `/repro` added to the wiring-matrix consumer list. The actual prose-routing of `/repro` happens at build (the AC2 audit forces it).

### Majors (address this slice)

#### M1: The lexical matcher has an unquantified false-positive surface; APED-1 asserted but not executed at design time
- **Claim under review**: design.md §audit Detection model item 2 (verb lexicon + window).
- **Issue**: `Append|Write|Edit|update` near a shared filename produces a confirmed FP at `build-slice:394` (past-tense prose describing slice-063's diff). The lexicon also collides with the *routed* prose itself (which contains verb+filename+safe-route token). Per slice-088 regex-APED-1 ("execute the newly-minted regex against the REAL corpus at /critique time"), this matcher needs its FP/FN rate *measured*, not deferred.
- **Evidence**: `build-slice:394`; routed sites `reflect:143/188/264`.
- **Proposed fix**: Run the matcher against all 26 skills, record FP/FN in design; tighten to a directive shape (imperative at clause start), exclude fenced code blocks + past-tense; `build-slice:394` must be CLEAN without an exemption.
- **Builder draft**: **ACCEPTED-PENDING**. The matcher-precision SPEC is added to design.md now (directive-shape; exclude fenced code blocks + past-tense/descriptive; `build-slice:394`→clean-without-exemption). The load-bearing part — writing the actual matcher, EXECUTING it against the 26-skill corpus, and recording the FP/FN count — is genuine `/build-slice` work (no matcher exists yet to run); recorded in build-log.md per the spec. This is the one finding that can't be fully "fixed" at design time by construction.

#### M2: The deferred RMW residual is the MORE dangerous half of the hazard; the design under-states it
- **Claim under review**: design.md §Q3 + §R-32 disposition; "concurrency-relevant mutators are /reflect + /archive."
- **Issue**: Both named mutators perform an `_index.md` recent-10 RMW (`reflect:319`; `/archive`). The lost-update scenario R-32 was opened for — two concurrent completions both rewriting recent-10, losing a row — is exactly this deferred RMW path, NOT the append path the slice closes. The slice closes the *safer* half. Deferral is defensible (not-yet-live; needs a lock spanning an LLM read+edit), but the framing reads as if it closes the /reflect+/archive concurrency hazard.
- **Evidence**: `reflect:319`; R-32 register §Impact ("a naive whole-file read-modify-write also loses one concurrent append").
- **Proposed fix**: State explicitly that the deferred RMW carries the PRIMARY hazard and the flip slice MUST close it before the flip goes live (not "owns it" as optional polish). No mechanism change.
- **Builder draft**: **ACCEPTED-FIXED**. design.md mutator note + §R-32 disposition now state the deferred RMW is the primary lost-update hazard, the append class is the safer half, and the flip slice MUST close RMW before the flip goes live (sharpens the must-not-defer boundary).

#### M3: The exemption marker is a silent-bypass vector with no second-order audit
- **Claim under review**: design.md §Exemption marker — free-text `<!-- vault-write-safe: <reason> -->`.
- **Issue**: A future skill edit can add `<!-- vault-write-safe: deferred -->` next to a genuinely-unsafe append → audit goes green. This is the R-7 silent-disable class the must-not-defer invokes, reintroduced via the back door — the per-line `# noqa` anti-pattern VWS-1 (ADR-086) deliberately avoided ("a single module exemption, NOT per-line suppressions").
- **Evidence**: design.md §Exemption marker; ADR-086 §Consequences.
- **Proposed fix**: (a) `<reason>` from a closed enumeration (unknown → VIOLATION); (b) pin the total exemption count + locations (allowlist, `_REGISTERED_INSTALLED_READERS` shape) so a new exemption trips a pin regression.
- **Builder draft**: **ACCEPTED-FIXED**. design.md detection model now constrains `<reason>` to `{deferred-rmw, project-open-single-shot}` (unknown → VIOLATION) + pins a closed `_REGISTERED_SKILL_EXEMPTIONS` allowlist with `test_exemption_allowlist_pinned`; ADR-087 §Consequences bullet added. Modest scope add (~closed set + 1 pin test), closes a real R-7 hole.

### Minors (log; address if cheap)

#### m1: "no merge-time PCR to catch it" framing is stale pre-flip — vault is git-TRACKED (ADR-066)
- **Issue**: Per ADR-066, `risk-register.md`/`lessons-learned.md`/`_index.md`/`build-checks.md` etc. are git-tracked, so pre-flip PCR DOES mediate. Strengthens AC5; the design should consistently reflect the hazard is post-flip-only.
- **Builder draft**: **ACCEPTED-FIXED**. design.md §R-32 disposition not-yet-live bullet now cites [[ADR-066]] + "strictly POST-flip"; notes the brief's "no merge-time PCR" phrase describes the post-flip state.

#### m2: VERSION/changelog collision plan doesn't name who rebases what
- **Issue**: "094 rebases up" is more than a rebase — renumber changelog entry + re-pin entry-pin test + re-run PMI-1 atomic bump + shippability propagation (FBCD-1 multi-surface sweep).
- **Builder draft**: **ACCEPTED-FIXED**. design.md §Sequencing note now carries the concrete 4-step second-merger checklist.

## Dimensions checked
- [x] **Unfounded assumptions** — B2 (26≠23; /repro + /supersede missed), M1 (matcher shape pre-selected without execution).
- [x] **Missing edge cases** — B2 (concurrent /repro append; /supersede RMW), M2 (recent-10 RMW is the unaddressed lost-update).
- [x] **Over-engineering** — none (append-only wrapper is correctly minimal).
- [x] **Under-engineering** — B1 (AC over-claims its mechanism), M3 (exemption reintroduces R-7).
- [x] **Contract gaps** — none blocking; note: pick `--content-file` vs `--stdin` default for multi-line markdown blocks (reflect:147-158/190-203/266).
- [x] **Security** — none (ADR-067 cooperative; `vault_edit` rejects `..`-escape — correct path-containment).
- [x] **Drift from vault** — B1 (contradicts ADR-029 without distinguishing), m1 (stale gitignored framing post-ADR-066). Strategic-direction fit (project-frame): advances external-vault initiative, correctly excludes per-slice files (no parallel cry-wolf).
- [x] **Web-known issues** — POSIX O_APPEND atomicity not guaranteed >PIPE_BUF, BUT slice-093 holds an explicit sidecar `.lock` across the whole `os.write` (`_vault_write.py:130-152`) so the non-guarantee is mitigated; Windows `msvcrt` mandatory byte-range consistent with sidecar-not-target design. No issue contradicts the mechanism.
- [x] **Cross-cutting conformance** — B2/M1 (APED-1 execute-don't-reason), m2 (EPGD-1/PMI-1 atomic-bump + FBCD-1 under parallel-094 second-merge). New-tool count-fan-out correctly enumerated ×2 tools.

## Triage

**Triaged by**: user
**Date**: 2026-06-01
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes: first Critic (B1/B2/M1/M2/M3/m1/m2) + meta-Critic EXTEND (M-add-1/M-add-2). User ratified all 9 dispositions ("Accept all → NEEDS-FIXES").

| ID | Severity | Disposition | Rationale / fix ref |
|----|----------|-------------|---------------------|
| B1 | Blocker | ACCEPTED-FIXED | design.md §"Why SVW-1 is acceptable despite ADR-029" (no *content* oracle, unlike BCI-1 fixture) + AC2-framing-corrected bullet + ADR-087 §Consequences; mechanism unchanged, over-claim removed |
| B2 | Blocker | ACCEPTED-FIXED | 23→26 ×4 sites; mutator table +`/repro`+`/supersede-slice`; `build-slice:394` recorded as must-stay-clean FP |
| M1 | Major | ACCEPTED-PENDING | matcher-precision spec added to design (directive-shape; exclude fenced/past-tense); the FP/FN measurement + matcher build is genuine `/build-slice` work, recorded in build-log |
| M2 | Major | ACCEPTED-FIXED | design.md mutator note + §R-32 disposition: deferred RMW is the PRIMARY lost-update hazard; flip slice MUST close it before go-live |
| M3 | Major | ACCEPTED-FIXED | exemption constrained to closed reason-enum `{deferred-rmw, project-open-single-shot}` (unknown→VIOLATION) + pinned `_REGISTERED_SKILL_EXEMPTIONS` allowlist + `test_exemption_allowlist_pinned` |
| m1 | Minor | ACCEPTED-FIXED | design.md §R-32 cites [[ADR-066]]; hazard "strictly POST-flip" |
| m2 | Minor | ACCEPTED-FIXED | design.md §Sequencing note: concrete 4-step second-merger checklist |
| M-add-1 | Major | ACCEPTED-FIXED | meta-Critic (critique-review.md): added `user-test:115` + `validate-slice:291` to mutator table; Builder re-grep re-verified enumeration COMPLETE (no 5th site) |
| M-add-2 | Major | ACCEPTED-FIXED | meta-Critic: route `/validate-slice`+`/user-test` via `vault_edit append` (both appends) — keeps reason-enum at 2 values; `/validate-slice` is NOT project-open (runs per-slice/concurrent) |

**Critic calibration (recorded for /reflect)**: design-Critic 2B/3M/2m all VALIDATED (zero false-positive); meta-Critic EXTEND +2 MISSED (M-add-1/M-add-2) — the recursive-APED-1 catch (first Critic's "I executed the matcher" B2 under-ran the corpus 2-of-4). Stack complementarity held: design-Critic = claim-correctness (B1 ADR-029) + execution (B2); meta-Critic = the under-execution in the first Critic's OWN fix ("a Critic's own fix is a fresh claim", N≥6).
