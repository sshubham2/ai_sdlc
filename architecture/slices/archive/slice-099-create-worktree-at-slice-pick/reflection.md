# Reflection: Slice 099 create-worktree-at-slice-pick

**Date**: 2026-06-02
**Shipped**: YES

## Validated
- **Worktree-at-pick keeps master clean** — validated live: slice-099 is its own bootstrap; the worktree holds all scaffold/design/critique/build artifacts, `git -C <main> status --porcelain` is empty. The "master never stays clean" failure (witnessed with slice-098's scaffold landing on master under the old build-time timing) is structurally closed in the normal flow.
- **Shared `_worktree_paths.py` is a single source of truth (AC5)** — `branch_workflow_audit.py` (import) + `/slice` Step 5.5 + `/build-slice` point-2 (CLI + `seed_derived_dirs`) all compute the canonical path/branch/seed from one helper. The `branch_workflow_audit` refactor is byte-behavior-identical (code-Critic verified via diff + delegation test).
- **`## Pick log` preservation across `## Candidates` regen** — `_extract_pick_log_block` read-tail/re-append survives a queue regeneration; idempotent prefix-scan; first-pick create. 6 `test_slice_queue_pick_log` tests + code-Critic empirical probing (candidate-named-heading false-match, CRLF) confirm.
- **Fail-visible pick-provenance (AC2 must-not-defer)** — `record_pick`/`read_git_config_user` is correctly NOT wrapped in the non-fatal try/except, so `ClaimUsageError` propagates on unset git identity. Code-Critic confirmed the structure.
- **`vault_edit rewrite` CAS dogfooded on the real 140KB CRLF risk-register** — the R-31 status flip used `read --out-file` (byte-exact base) → edit → `rewrite --base-file` (exit 0, EOL-preserving). The slice-097/ADR-088 RMW channel works on a live large CRLF file.

## Corrected
- **Design said "4-part PMI-1 bump"; reality is 5-part** — `pyproject.toml [project].version` was omitted in the design's enumeration, but it carries a STATIC version that drives the `pip install --upgrade` wheel; omitting it would have left installed `ai-sdlc-tools` at 0.80.0 and **failed TVFS-1**. Corrected design.md §version-bump-fan-out + the v0.81.0 changelog + the version-sync test. Caught at build time by the codebase's own gate (TVFS-1) — code/gate is truth, the design undercounted. (Logged in build-log DEVIATION.)
- **ADR-090:23 Option-3 cons "depend on PCR" → corrected to lock-serialization** (code-Critic m1) — contradicted the same ADR's §Consequences; the code never imports PCR. Fixed the stale cons clause (in-slice ADR refinement, pre-merge).

## Discovered
- **`branch_workflow_audit._check_worktree_skip_line` substring-collision FP class (m2)** — the function bare-substring-scans the WHOLE build-log.md for `WORKTREE=skip` (despite its docstring claiming it scans only `## Events`), so ANY descriptive prose mention of the contiguous token false-positives `worktree-skip-malformed`. This bit slice-099 **N=3 times** (the code-Critic B1 on build-log:50; my own build-log event prose twice). The same class also produced the SVW-1:43 FP (verb "update" before backticked `methodology-changelog.md`). Impact: annoying-but-fail-SAFE (false positive, not false negative). Pre-existing (slice-099 only re-imported `_SLICE_FOLDER_RE` into that file). → follow-up candidate **`anchor-worktree-skip-scan-to-events-section`** (anchor the scan to the `## Events` block; the docstring already claims this). NOT added to risk-register — it's a usability/quality defect in an audit, not a correctness/fail-open risk.
- **BRANCH-3 raises the abandoned-pick rate** — a worktree+branch now exists from pick (before build-commitment), so a picked-but-abandoned slice leaves a heavier orphan artifact (worktree+branch) than the pre-BRANCH-3 branchless folder. Currently surfaced as informational `IN_PROGRESS:slice` (halt=false) — listed, not GC'd. → follow-up candidate **`abandoned-pick-detection`** (a real abandoned-pick discriminator; design.md §post-critique M1 flagged this as warranted-soon).
- **Parallel slice-098 merged to master mid-build** (`2690daf`) — a parallel session finished + merged slice-098 (route-the-3-git-coupled-vault-tools) while slice-099 was being built. Disjoint by design (no 098 change touched a 099 surface). **Merge-time consequence**: 098 and 099 both touched `shippability.md` + `drift-log.md` (and 098 also `risk-register.md`/`_index.md`/`lessons-learned.md`/`slice-queue.md`, which 099's `/reflect` also touches) → a SOFT append-conflict is expected at the 099 `/commit-slice --merge`. This is PCR's `resolve_soft_conflict` (+ PCR-2a VAULT_CLAIM) territory — the parallel-slice family operating as designed.

## Deferred
- **`anchor-worktree-skip-scan-to-events-section`** (m2 fix) — reason: changing audit detection semantics needs its own slice + adversarial tests (APED-1); out of scope for a BRANCH-3 slice. Lands in: backlog / next `/slice` candidate.
- **`abandoned-pick-detection`** — reason: BRANCH-3's scope explicitly excludes a real abandoned-pick discriminator (mission-brief Out-of-scope; design M1 downscope). Lands in: backlog / next `/slice` candidate (warranted-soon since BRANCH-3 raises the abandon rate).

## Critic calibration

Two adversarial passes ran on this slice: the design-Critic stack (`/critique` + `/critique-review`) BEFORE code, and the code-Critic (`/code-review`) AFTER.

**Design-Critic (`/critique`, verdict BLOCKED→CLEAN at TRI-1; `/critique-review` EXTEND):**
- B1 (PCR doesn't resolve a master-commit race): **VALIDATED** — ACCEPTED-FIXED; the concurrency model was genuinely wrong as first written (route-through-PCR), fixed to index-lock serialization. Reality (code) confirmed the fix is sound.
- B2 (`## Pick log` doesn't survive `format_queue_md`): **VALIDATED** — ACCEPTED-FIXED; empirically re-confirmed (the read-tail/re-append fix tested green).
- B3 (version-bump fan-out unacknowledged): **VALIDATED** — ACCEPTED-FIXED; the 5-part bump was genuinely required (and the design even undercounted it — see Corrected).
- B4 (WORKTREE=skip-at-pick recording surface): **VALIDATED** — ACCEPTED-FIXED.
- M1 (abandoned-pick informational, not stranded): **VALIDATED** — honest downscope; reality matches (informational).
- M-add-1 (ADR-090 frontmatter `supersedes: null` contradiction): **VALIDATED** — meta-Critic catch; fixed to `supersedes: ADR-063`.
- M-add-2/3/4 (minors): **VALIDATED** — all fix-delta gaps confirmed at build (M-add-2's leading-`- ` audit-regex shape was load-bearing).

**Code-Critic (`/code-review`):**
- B1 (slice's own build-log fails `branch_workflow_audit` + false "clean" attestation): **VALIDATED** — reproduced exactly (audit exit 1; contiguous token on build-log:50). My error, introduced in Phase E AFTER my last clean audit run; falsely attested clean. Fixed + re-verified. This is precisely the Builder↔Critic separation working — pytest couldn't see it (no test runs the audit on the live slice folder).
- m1 (ADR-090 PCR self-contradiction): **VALIDATED** — real internal contradiction; code correct, prose drift; fixed.
- m2 (audit substring-scan vs "Events" docstring): **VALIDATED** (DISCOVERED) — the root cause behind all the same-class FPs; deferred to a follow-up.

**Missed by Critic**: Nothing slice-breaking was missed. Notable: NO Critic (design or code) pre-flagged that **my own build-log/disposition PROSE would trip `branch_workflow_audit`'s substring scan** before the code-Critic caught the build-log:50 instance — i.e., the substring-collision FP class is so easy to re-trigger that I hit it 4× across the slice. A `/critic-calibrate` candidate: a heuristic that flags "audit-grepped literal tokens mentioned contiguously in prose artifacts the same audit reads."

**Pattern**: Both Critic passes were high-value, zero false-alarm (N continues the cross-cutting-tooling-slice 100%-VALIDATED record). The code-Critic specifically earned its keep by catching a self-application failure invisible to the 1455-test suite — the strongest argument for the Builder↔Critic separation. The recurring substring-collision FP (N=4 within one slice) is the dominant lesson.

## Lessons for next slice
- **Audits that bare-substring-scan a whole prose artifact for a literal control token are FP-prone** — descriptive prose that mentions the token trips them. Either anchor the scan (m2's fix) or, until then, de-fang token mentions (`` `WORKTREE`=skip ``). This is now N=4 within slice-099 across `branch_workflow_audit` + `SVW-1`. The right fix is in the audit (m2 follow-up), not eternal prose-discipline.
- **When a design enumerates a multi-part mechanical fan-out, verify the count against the codebase's own gates** — the "4-part" PMI bump was an undercount that TVFS-1 caught; trust the gate over the design prose.
- **A clean full-suite (1455) is NOT proof a slice's own methodology artifacts pass their sibling audits** — no test runs `branch_workflow_audit`/`SVW-1` against the live in-flight slice folder; those are Step-6 manual / `/validate-slice` legs. Run the per-slice audits explicitly at pre-finish, and re-run after ANY late edit to build-log.md (the B1 trap was a late Phase-E Summary edit).
- **Parallel slices merging mid-build is normal now** — expect SOFT vault-file conflicts at `/commit-slice` and let PCR resolve them; don't treat a master-HEAD advance during a build as an anomaly (verify it's a sibling merge, not leakage).

## Vault updates made (thin vault)
- [[risk-register.md]] — **R-31 flipped mitigating → retired** (via `vault_edit rewrite` CAS; both axes closed: slice-092 detection + BRANCH-3 root-cause occurrence). R-17 stays retired (slice-066), R-27 stays mitigating (different axis).
- [[lessons-learned.md]] — appended the slice-099 entry (substring-collision-FP + 4→5-part-undercount + parallel-merge lessons).
- [[shippability.md]] — row #106 added at build (slice-099 BRANCH-3 critical path; cites BRANCH-3/ADR-090/R-31/pick).
- [[methodology-changelog.md]] — v0.81.0 BRANCH-3 entry (added at build).
- This slice's [[design.md]] — §version-bump-fan-out corrected 4-part → 5-part (build-time deviation).
- [[decisions/ADR-090-create-worktree-at-slice-pick.md]] — Option-3 cons clause corrected (m1; PCR-not-involved consistency).
- **Not updated**: no `components/`/`contracts/`/`schemas/` (thin vault, code is truth). m2 + abandoned-pick are next-slice candidates, NOT risk-register entries (quality follow-ups, not correctness risks).
