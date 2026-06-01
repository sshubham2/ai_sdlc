# Reflection: Slice 095 harden-skill-driven-vault-writes

**Date**: 2026-06-01
**Shipped**: YES-WITH-DEFERRALS

> SVW-1 (skill-driven vault-write-safety audit + `vault_edit append` safe channel)
> shipped at build (v0.79.0, ADR-087); this reflection covers the whole slice
> including the **code-review hardening round** (M1/M2/M3 + m1/m3) that closed the
> matcher's fail-open holes the code-Critic flagged.

## Validated
- **AC1–AC5 all PASS** (validation.md): SVW audit clean (22 sites / 10 routed / 12 exempted); fail-closed on an injected raw write (exit 1 naming `surface:line`); concurrency proof 2 passed (lock empirically load-bearing — the naive RMW control loses updates); R-32 `mitigating` with the skill-driven sub-class closed-with-evidence; `_resolve_vault_root()` default stays `architecture`; full suite 1367 pass.
- **The no-flip contract held through a large hardening round**: the M1/M2/M3 + m1/m3 edits touched only 095's own deliverables — zero behavioral change to any pre-095 skill/tool (1367 pass, 101/101 shippability, 0 regressions).
- **The design+meta Critic stack's substance was right**: every design-Critic finding (B1 ADR-029 honest-scope, B2 corpus enumeration, M3 closed-allowlist) and both meta-Critic M-adds were VALIDATED — the design was sound.

## Corrected
- **The M1 matcher-precision spec (critique disposition ACCEPTED-PENDING) shipped with three fail-OPEN holes** → corrected at code-review: the route-token check was a naive line-local substring (false-CLEAN on negation/cross-ref), the directive-verb lexicon was too narrow (insert/replace/… passed CLEAN), and the exemption pin was `(file,reason)`-granularity not site-count. All three corrected in-slice (M1/M2/M3). The design's *intent* was right; the *executed matcher* had the gaps — a design→execution gap only the code-Critic reached.
- **The build-time "drop triage from the SVW-1 allowlist" decision** (build-log 2026-06-01 01:05 — which relied on triage's malformed-fence parity to hide its risk-register writes) → reversed. The m1 CommonMark fence fix correctly renders triage:179 OUTSIDE the template fence; it now carries an explicit `project-open-single-shot` exemption (visible + allowlist-pinned) — strictly better for SVW-1's own "visible residual" principle than relying on a bug. Reconciled the 11→12 / 21→22 counts across changelog/build-slice/risk-register (+ installed forward-syncs).

## Discovered
- **A newly-minted content matcher's *negation* handling is an APED-1 trap that unit fixtures miss**: several genuinely-routed real-corpus lines contain `never`, `raw`, and `don't` (`…via \`tools.vault_edit append\` (SVW-1; never a raw \`Write\`/\`Edit\`)`). A naive negation lexicon would VIOLATION those and break the corpus. The real discriminator was structural: a route token only counts inside a backtick code span or `<!-- route: -->` marker, plus a *tight* 2-word negation look-back so a trailing safety assertion (which governs the RAW write, not the route) stays CLEAN. Only executing the candidate matcher against the REAL routed lines surfaced this.
- **A more-correct parser/fence fix SURFACES latent sites the buggy version hid** — the m1 CommonMark fence tracker un-hid triage:179 (a real project-open write). A "minor" fix was NOT contained: it cascaded into classifying a surfaced site + a guarded-opener edit (triage) + a count reconciliation across 4 files + 2 installed syncs. Budget for "what does a correctness fix reveal," not just "what does it fix."
- **The directive-verb lexicon has an irreducible noun/verb residual**: `note` ("**Note** on…"), `record` ("reflection record"), `set`/`log`/`mark`/`put` are common NOUNS adjacent to a file ref (they FP'd on slice:34/221). They were deliberately EXCLUDED and documented as a lexicon-bound residual — honest "fail-closed for RECOGNIZED verbs", not a completeness oracle. (`register` is worse: `\bregister\b` matches inside `risk-register.md`.)
- **triage:163 stays fence-hidden** — the separate, still-deferred triage-markdown bug (the `:142` ```markdown template fence is malformed). This slice exempted the surfaced `:179` but did NOT repair the template fence. Candidate for its own fix slice.

## Deferred
- **triage-markdown-bug** (repair the malformed `:142` template fence; un-hides `:163`) — reason: out of SVW-1 scope (a cosmetic prose-structure defect, not a write-safety hole). Lands in: a dedicated `fix-triage-template-fence` slice.
- **vault_edit m2 (typo-creates-phantom-file) + m4 (empty-content no-op)** — reason: the cooperative model (ADR-067) bounds blast radius; both are robustness footguns, not safety holes. Lands in: backlog / a follow-up hardening slice if they recur.
- **R-32 full retirement** — reason: gated on BOTH sub-classes merging; slice-094 (Python-writer) is parked at critique (BLOCKED, redesign required). R-32 stays `mitigating`; retires when 094 merges. Lands in: the 094 merge.

## Critic calibration

Per TRI-1, scored against `critique.md` `## Triage` dispositions + reality during build/code-review/validate:

- **B1** (ADR-029 over-claim): VALIDATED — ACCEPTED-FIXED; honest-scope framing held through validation (the R-2 runtime axis is genuinely unreachable).
- **B2** (corpus enumeration 23→26): VALIDATED — ACCEPTED-FIXED; the enumerated mutator sites were the real ones (the matcher fired on exactly them).
- **M1** (matcher precision): VALIDATED-but-UNDER-SPECIFIED — ACCEPTED-PENDING; the precision *spec* was built, but the *executed matcher* shipped three fail-open holes (negation, lexicon, pin-granularity) the design-level spec didn't bound. The code-Critic caught all three.
- **M2** (RMW is the primary residual): VALIDATED — ACCEPTED-FIXED.
- **M3** (closed allowlist): VALIDATED — ACCEPTED-FIXED, then HARDENED (pair-set → count granularity at code-review when the code-Critic showed the pair-set let an N+1-th marker slip).
- **m1/m2** (ADR-066 cite / sequencing): VALIDATED — ACCEPTED-FIXED.
- **M-add-1 / M-add-2** (meta-Critic: +user-test/+validate-slice sites; route both via append): VALIDATED — ACCEPTED-FIXED; enumeration was genuinely incomplete (first Critic's "I executed the matcher" under-ran the corpus 2-of-4).
- **code-Critic M1/M2/M3** (route-token false-CLEAN / narrow lexicon / pin granularity): all VALIDATED — this session confirmed each is a real latent fail-open hole by closing it; none was a false alarm. m1/m3 (tilde-fence / vault-root) VALIDATED; m2/m4 NOT-YET (deferred, cooperative-model-bounded).

**Missed by Critic**: (1) the design+meta Critic stack MISSED the matcher's execution-only fail-open holes — only the code-Critic, EXECUTING adversarial inputs, reached them (the recurring slice-037 "audit-vs-real-artifact" law). (2) NOBODY — not even the code-Critic — predicted that the m1 fence fix would SURFACE triage:179; it was discovered only by running the hardened audit against the real tree. (3) the M1 *negation* APED-1 trap (legit routed lines containing `never`/`raw`/`don't`) was caught by me executing the candidate matcher against the real corpus, not by any Critic.

**Pattern**: 3-Critic stack complementarity held N+1 (design+meta = claim-correctness + corpus-enumeration; code-Critic = execution-only fail-open holes). The strongest single signal: **a content-scanning matcher must be APED-1-executed against the REAL corpus — including its negation/noun-prone-word shapes — at the moment it is authored, because the corpus contains the exact tokens (`never`, `raw`, nouns) that a naive heuristic mis-handles.** Extends regex-APED-1/BC-PROJ-13 with the "negation/noun-prone real-corpus shape" axis.

## Lessons for next slice
- **Execute a new content matcher against the real corpus's adversarial shapes (negation words, noun-prone verbs) at authoring time** — the corpus contains the exact tokens a naive heuristic breaks on; unit fixtures written from the same mental model as the matcher share its blind spot (the code-Critic was a required *second* APED-1 author). Extends BC-PROJ-13.
- **Treat a "minor" correctness fix as potentially scope-expanding**: a more-correct parser un-hides latent sites the buggy version masked. The m1 fence fix surfaced triage:179 → a guarded-opener edit + a 4-file count cascade + 2 installed syncs. Estimate "what does correctness reveal," not just "what does it fix."
- **A lexical audit's honest posture is "fail-closed for RECOGNIZED inputs" + a documented residual** — don't chase completeness into FP territory (noun-prone verbs). Name the residual in code + a pinned test so it's visible, not silently assumed closed.
- **A count claim is a fan-out**: changing "11 exempt / 21 sites" rippled to methodology-changelog + build-slice + risk-register + 2 installed copies (OSDG-1/MCFS-1). Grep every count literal across live + synced surfaces the moment a count moves.
- **The slice that builds a vault-write safe channel should dogfood it in its own /reflect** — this reflection's lessons-learned append routes through `$PY -m tools.vault_edit append` (SVW-1's own channel).
- **Branch-behind-master is real here**: slice-095 is based on `5f13582`; master has since merged 096 (shared `_index`/`shippability`/`lessons`/CLAUDE.md). Per R-33, `/commit-slice --merge` should `git merge master` FIRST to reconcile the `_index` additively before the slice→master merge.

## Vault updates made (thin vault — small list)
- [[risk-register.md]] — R-32 closure note count reconciled 11→12 + triage:179 surfacing recorded (this round); status stays `mitigating` (retires on 094 merge).
- [[lessons-learned.md]] — appended the Slice 095 entry (via `vault_edit append` — SVW-1's own channel).
- [[methodology-changelog.md]] + `skills/build-slice/SKILL.md` — SVW-1 counts reconciled 11→12 / 21→22 (+ installed forward-syncs).
- This slice's [[build-log.md]] — code-review hardening round + triage:179 reversal recorded.
- `tools/skill_vault_write_safety_audit.py` + `tools/vault_edit.py` + tests — M1/M2/M3 + m1/m3 hardening (code is the source of truth; no component doc).
- **No shippability append** — slice-095's row (#102) was added at build; not duplicated.
- **No ADR supersession** — ADR-087's mechanism (wrapper + fail-closed audit) is unchanged; the hardening refined the matcher's precision, not the decision.
