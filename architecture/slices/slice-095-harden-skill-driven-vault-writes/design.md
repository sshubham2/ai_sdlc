# Design: Slice 095 harden-skill-driven-vault-writes

**Date**: 2026-06-01
**Mode**: Standard

## Decisions ratified at design (user, 2026-06-01)

Three forks the mission brief left open (the wrapper-vs-discipline choice is ADR-worthy) were resolved by structured-options gate:

1. **Mechanism** → **Wrapper CLI + static audit**. Ship a thin CLI (`tools/vault_edit.py`) over the slice-093 `safe_append_text` primitive; rewrite the append-class skill prose to call it; a static prose audit keeps the prose honest. (The only option that gives Claude a real safe channel for LLM-authored shared-vault content — e.g. a `/reflect` risk-register entry — which per-slice-isolation + PCR cannot.)
2. **Scope** → **Shared aggregate files ONLY**. Guard the genuinely-concurrent set; EXCLUDE per-slice-folder files (isolated by construction).
3. **Rewrite/lost-update class** → **Defer to the flip slice; NARROW R-32 (not full-retire)**. This slice closes the *append* sub-class (fully wrapper-solvable). The whole-file read-modify-write class has a lost-update window no per-call wrapper can close — it only goes live post-flip, so the flip slice owns it. **Consequence: the brief's AC4/Intent "retire R-32" is amended to "narrow R-32" — see §R-32 disposition below.**

## What's new

- `tools/vault_edit.py` (NEW — public CLI, PMI-1-enumerated) — the **skill-path safe channel**: `append --file <vault-rel-path> (--content-file <path> | --stdin)` → resolves the path under `VAULT_ROOT` and calls `_vault_write.safe_append_text`. Exit 0 success / 2 usage-error. **Ships `append` ONLY this slice** (the closed append sub-class); `rewrite` is deliberately NOT exposed — `safe_write_text` is torn-write-safe but NOT lost-update-safe for read-modify-write, so exposing it would give false confidence for the deferred rewrite class.
- `tools/skill_vault_write_safety_audit.py` (NEW — the **SVW-1** enforcement audit): a fail-closed lexical scan proving no `skills/*/SKILL.md` prose prescribes an *unsafe* (raw `Write`/`Edit`/`Append`) mutation of a shared-aggregate vault file. Exit 0 clean / 1 violations / 2 usage-error (fail-VISIBLE).
- `tests/methodology/test_skill_vault_write_safety_audit.py` (NEW) — SVW-1 contract + APED-1 adversarial battery (both directions, executed against the real 26-skill corpus).
- `tests/methodology/test_skill_vault_write_safety_concurrency.py` (NEW) — the R-32 skill-path concurrency proof: N concurrent `$PY -m tools.vault_edit append` **subprocesses** to one file lose zero lines; non-vacuity proven by mutation (lock-disable → FAIL → revert). This proves the **real skill path** (CLI subprocess), NOT just the underlying function (slice-093 already proved `safe_append_text` at the function level — this is the non-redundant end-to-end layer).
- A new methodology rule **SVW-1** (MEPD-1 **INCLUDE** — two non-underscore PMI-1-enumerated tools wired into gates; mirrors slice-094's VWS-1 INCLUDE): methodology-changelog entry + VERSION bump + PMI-1 atomic bump + shippability row.
- Routed append-class prose in `skills/reflect/SKILL.md` (Steps 5 / 5b / 264-row / risk-register-new-entry / methodology-changelog), `skills/reduce/SKILL.md` (Step 8), `skills/repro/SKILL.md` (`:107` shippability append — added per Critic B2), and `skills/archive/SKILL.md` (archive/_index.md append).
- **AC2 framing corrected (Critic B1 — ADR-029/BCI-1)**: the SVW-1 audit is a completeness guarantee over the **prose-detection surface** — no `skills/*/SKILL.md` *prescribes* an unsafe raw mutation of a shared-aggregate file — NOT a completeness guarantee over **runtime writes**. Unlike slice-094's VWS-1 (an AST scan where the parsed write op IS the ground-truth write), SVW-1 audits a *description of intent*; it cannot observe Claude invoking the raw `Write`/`Edit` tool at runtime in violation of correct prose (the R-2 class — structurally unreachable by a static audit, exactly the LLM-prose-inspection shape [[ADR-029]] rejected for BC-1). Runtime-write safety therefore rests on (a) the wrapper actually being USED + (b) the cooperative model ([[ADR-067]]) + (c) the pre-flip git/PCR backstop (m1) — NOT on this audit. The build re-runs the audit against the post-routing tree to catch any *prose* straggler; "fail-closed" is scoped to the prose-detection surface, never claimed over writes. See §"Why SVW-1 is acceptable despite ADR-029" below.

## What's reused

- `tools/_vault_write.py` — `safe_append_text` (`O_APPEND` + sidecar `.lock`). The slice-093 primitive ([[ADR-085]]); this slice WRAPS it in a CLI, does not re-implement it. The docstring (`_vault_write.py:11-14`) already names the append-class targets (`risk-register.md`, `_index.md`, ADRs, PCR log) — this slice realizes that intent on the skill path.
- `tools/_vault_paths.py` — `VAULT_ROOT` (the resolution seam, [[ADR-065]]+[[ADR-085]]); `vault_edit` resolves `--file` against it so the safe channel honors the (future) flip transparently.
- `tools/_stdout.py` — `reconfigure_stdout_utf8()` (UTF8-STDOUT-1) + the encoding-safe stderr pattern (the `_vault_paths._stderr` shape); both new tools MUST use it (RSAD-1: a vault-infra tool must not ship its own cp1252 crash — the self-applying class N≥8).
- Closed-world-allowlist + exemption-with-rationale precedent — slice-094 VWS-1 (`_vault_write.py` self-exemption), wiring-matrix `rationale:` convention, slice-041 `_REGISTERED_INSTALLED_READERS`. SVW-1 reuses the philosophy on the prose surface.
- `tools/parallel_conflict_resolver.py` (PCR) — already merges `slice-queue.md`/`shippability.md` at `/commit-slice` time; SVW-1 is the complementary write-time control for the LLM-authored append class PCR's merge-time path does not cover.

## The skill-driven mutator set (code-grounded enumeration)

`grep` of `skills/*/SKILL.md` (the **26-skill** corpus — corrected from "23" per Critic B2; live `Glob` + INST-1 history both report 26) for mutation verbs co-located with the shared-aggregate filenames yields the genuinely-concurrent mutators below. Most of the 26 skills only *reference* these files (read-context / drift-surface prose) — those are NOT mutation sites and the audit must not flag them (APED-1 false-positive obligation; the Critic EXECUTED the matcher and confirmed a false-positive at `skills/build-slice/SKILL.md:394`, descriptive prose that names "edit"+"risk-register" without prescribing a mutation — the matcher MUST NOT flag it, and MUST NOT need an exemption marker to stay clean). The table below was corrected after the Critic's executed scan added `/repro` and `/supersede-slice`.

| Skill | Shared file(s) mutated | Op class | Disposition this slice |
|-------|------------------------|----------|------------------------|
| `/reflect` | lessons-learned.md (Step 5), shippability.md (Step 264), build-checks.md (Step 188), methodology-changelog.md, risk-register.md (NEW R-NN entry) | **append** | route → `vault_edit append` |
| `/reflect` | risk-register.md (in-place status flip mitigating→retired), _index.md (recent-10 table rewrite) | **rewrite (read-modify-write)** | **exempt-with-rationale** (deferred to flip — visible residual) |
| `/archive` | archive/_index.md (append catalog row) | **append** | route → `vault_edit append` |
| `/archive` | _index.md (recent-10 rewrite + aggregated-lessons) | **rewrite** | **exempt-with-rationale** (deferred) |
| `/reduce` | lessons-learned.md (Step 8) | **append** | route → `vault_edit append` |
| `/repro` | shippability.md (`:107`, Step 5 — added per Critic B2) | **append** | route → `vault_edit append` |
| `/supersede-slice` | _index.md (`:103`, Step 6 — superseded-row in-place edit; added per Critic B2) | **rewrite (read-modify-write)** | **exempt-with-rationale** (`deferred-rmw`) |
| `/triage`, `/discover`, `/risk-spike` | risk-register.md (project-open / spike status) | append/rewrite | **exempt-with-rationale** (`project-open-single-shot` — NOT a parallel-slice concurrency hazard; you don't run `/triage` twice in parallel) |
| `/commit-slice` | slice-queue.md, shippability.md | merge | already Python/PCR-routed (slice-094 scope) — out of skill-path scope |

- **The append sites of `/reflect`, `/reduce`, `/repro`, `/archive` are what this slice routes; the rewrite (RMW) sites of `/reflect`, `/archive`, `/supersede-slice` are the deferred residual.**
- **The deferred RMW residual carries the PRIMARY lost-update hazard, not the safer half (Critic M2).** Both headline concurrency-relevant mutators (`/reflect` + `/archive`) perform an `_index.md` recent-10 **rewrite** (`skills/reflect/SKILL.md:319` "Regenerate _index.md — update the Most recent 10 table"; `/archive` Step 75 does the same). The exact scenario R-32 was opened for — *two concurrent slice completions both rewriting the recent-10 table, losing one slice's row* — is this RMW path, NOT the append path this slice closes. The append class (lessons-learned, archive chronological catalog, shippability rows) is **non-clobbering and lower-risk**; this slice closes the *safer* half. The deferral is defensible (RMW is not-yet-live pre-flip and needs a lock spanning an LLM read+edit — out of a 1-day scope, ADR-087 Option 3), but the **flip slice MUST close the RMW class BEFORE the flip goes live** — it is not optional polish. This sharpens the must-not-defer boundary so the flip cannot treat RMW as deferrable.

## Components touched

### `tools/vault_edit.py` (NEW — the skill-path safe-append CLI)
- **Responsibility**: give Claude (per SKILL.md prose) a concurrency-safe channel to APPEND LLM-authored content to a shared-aggregate vault file, so a skill-driven append no longer bypasses `_vault_write`'s lock.
- **Lives at**: `tools/vault_edit.py` (created by this slice).
- **CLI contract**: `append --file <vault-relative-path> (--content-file <path> | --stdin)`. Resolves `<path>` against `VAULT_ROOT` (rejects an absolute/`..`-escaping path that resolves outside `VAULT_ROOT` → exit 2). Reads the content block from a temp file (`--content-file`, the robust path — avoids Windows-PowerShell multiline-pipe quoting hell) or stdin. Calls `safe_append_text(resolved, content)`. Exit **0** success / **2** usage error (bad path / missing content / escapes vault). No exit-1 (it's a writer, not an auditor).
- **Key interactions**: `tools._vault_write.safe_append_text`, `tools._vault_paths.VAULT_ROOT`, `tools._stdout` (cp1252-safe). Invoked by `/reflect`, `/reduce`, `/archive` prose.
- **Why `append`-only**: the deferred rewrite class needs read-modify-write under a held lock (impossible to span an LLM read+edit) — see [[ADR-087]] §Consequences.

### `tools/skill_vault_write_safety_audit.py` (NEW — the SVW-1 audit)
- **Responsibility**: prove no `skills/*/SKILL.md` prescribes an unsafe raw mutation of a shared-aggregate vault file; fail closed on any unrouted/unexempted mutation site.
- **Lives at**: `tools/skill_vault_write_safety_audit.py` (created by this slice).
- **Detection model** (two tripwires, fail-closed — see [[ADR-087]]):
  1. **Shared-file set** (a module constant, the audited universe): `risk-register.md`, `lessons-learned.md`, `_index.md`, `methodology-changelog.md`, `shippability.md`, `build-checks.md`, the append-only ADR class (`decisions/ADR-*.md`), `archive/_index.md`. Per-slice-folder files are NOT in the set (excluded by construction — Q2).
  2. **Mutation-site detector** (precision-tightened per Critic M1): a line pairing a shared-file reference (backticked filename or an `architecture/…<file>` path) with a **directive-shaped** mutation verb — an imperative at line/clause start (`Append … to`, `Write`, `Edit`, `Update`, `add a/an (row|entry|bullet) to`), NOT the verb appearing anywhere in an 80-char window. **Excluded by construction** (the confirmed false-positive class): lines inside fenced code blocks (```` ``` ````), and **past-tense / descriptive** prose that names a file + verb-stem without prescribing an action (the `skills/build-slice/SKILL.md:394` case — "the slice ships a … `risk-register.md` flip" describes slice-063's diff). Bare read-context mentions (no directive verb) are NOT sites. **Build obligation**: run the matcher against all 26 skills and **record the executed FP/FN count in build-log.md** (`matcher fires on N lines; M are true sites; the K excluded are at <file:line> because <fenced / past-tense / non-directive>`) — `build-slice:394` MUST come out CLEAN without an exemption (it is not a mutation site; exempting it would be wrong).
  3. **Verdict per site (fail-closed)**: a mutation site is CLEAN iff it references a sanctioned safe route (`tools.vault_edit` / `vault_edit append` / `safe_append_text` / `_vault_write`) OR carries an inline exemption marker `<!-- vault-write-safe: <reason> -->` whose `<reason>` is in a **closed enumeration** (see below). Any mutation site that is neither routed nor validly-exempted → **VIOLATION** (exit 1, names `skills/<x>/SKILL.md:line` + the matched filename). An unclassifiable/new mutation pattern defaults to VIOLATION, never a silent pass (R-7 class).
- **Exemption marker — constrained per Critic M3 (close the per-line-`# noqa` silent-bypass vector)**: `<!-- vault-write-safe: <reason> -->`. The `<reason>` MUST be one of a **closed enumeration** `{deferred-rmw, project-open-single-shot}` — an **unknown reason string is itself a VIOLATION** (mirrors VWS-1's closed-world discipline, ADR-086 §Consequences: "a single module-name exemption, NOT per-line `# noqa`-style suppressions"). Additionally, the audit pins a **closed allowlist of exempt site locations** (`_REGISTERED_SKILL_EXEMPTIONS = {(skill, file, reason)}`, the slice-041 `_REGISTERED_INSTALLED_READERS` shape): a NEW exemption added by a future skill edit that is not on the allowlist trips a **pin-count regression** (`tests/methodology/test_skill_vault_write_safety_audit.py::test_exemption_allowlist_pinned`) forcing explicit review. This makes "visible residual" *enforced*, not self-asserted — a free-text marker next to a genuinely-unsafe append can no longer silently green the audit.
- **Key interactions**: stdlib `re`/path-walk over `skills/*/SKILL.md`; `tools/_stdout.py` (cp1252-safe output); consumed by `/build-slice` Step 6 + `/validate-slice` gate roster (prose-invoked) + `architecture/shippability.md`.
- **APED-1 obligation**: the verb/path matcher is a newly-minted parser → the build MUST execute it against the real **26-skill** corpus AND an adversarial battery: (a) planted raw append to a shared file → caught; (b) a routed `vault_edit append` site → clean; (c) a validly-exempted rewrite site (`deferred-rmw`) → clean; (d) a bare read-context mention of a shared filename → clean; (e) a mutation of a per-slice file → clean (out of set); (f) the `build-slice:394` past-tense FP → clean WITHOUT exemption; (g) an exemption with an **unknown reason** → VIOLATION; (h) an off-allowlist exemption → pin regression. BC-PROJ-13 / regex-APED-1 — the Critic already executed (a)/(d)/(f) against the live tree.

## Contracts added or changed

None in the HTTP/event/schema sense. Two CLI contracts are introduced (exit-code + arg shape, the established audit/tool shape RR-1/SRSC-1/BCI-1/VWS-1): `vault_edit append` (0/2) and `skill_vault_write_safety_audit` (0/1/2). `safe_append_text`'s signature is unchanged (slice-093).

## Data model deltas

None.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/vault_edit.py` | `skills/reflect/SKILL.md` (Step 5 / 5b / shippability / risk-register append) + `skills/reduce/SKILL.md` (Step 8) + `skills/repro/SKILL.md` (`:107` shippability append) + `skills/archive/SKILL.md` (archive index append) — prose-invoked | `tests/methodology/test_skill_vault_write_safety_concurrency.py::test_concurrent_cli_appends_lose_zero_lines` | — |
| `tools/skill_vault_write_safety_audit.py` | `skills/build-slice/SKILL.md` Step 6 + `skills/validate-slice/SKILL.md` gate roster (prose-invoked, per the VWS-1/RR-1/SRSC-1 audit-wiring precedent) | `tests/methodology/test_skill_vault_write_safety_audit.py::test_audit_flags_planted_raw_skill_append` + `::test_exemption_allowlist_pinned` (M3) | — |
| `tests/methodology/test_skill_vault_write_safety_audit.py` | — | — | internal — rationale: pytest-collected audit contract; a test module is self-consuming, no downstream module consumer demanded |
| `tests/methodology/test_skill_vault_write_safety_concurrency.py` | — | — | internal — rationale: pytest-collected concurrency proof; self-consuming test module |

## Decisions made (ADRs)

- [[ADR-087]] — Harden skill-driven vault writes via a wrapper CLI (`vault_edit append` over `safe_append_text`) for the append class + a fail-closed lexical SKILL.md audit (SVW-1), deferring the read-modify-write/lost-update class to the flip slice — reversibility: **cheap**.

### Sub-decisions (recorded here, not ADR-worthy — anti-pattern to ADR trivial choices)

- **`append`-only wrapper this slice**: `safe_write_text` is torn-write-safe but a per-call wrapper cannot hold the lock across an LLM read-modify-write, so it cannot close the lost-update window for `_index.md`/in-place risk-status edits. Exposing `rewrite` would invite unsafe use → ship `append` only; the flip slice adds the rewrite mechanism (held lease / serialized reflect+archive).
- **MEPD-1 INCLUDE**: two non-underscore PMI-1-enumerated tools wired into gates → mint RULE-ID **SVW-1**, a methodology-changelog entry, a VERSION bump, a PMI-1 atomic bump, a shippability row. (Mirrors slice-094 VWS-1; contrast slice-093 EXCLUDE which shipped an *underscore* primitive.)
- **Count-fan-out is a TWO-tool bump** (N≥3 lesson, doubled): `plugin.yaml` (PMI-1), `tools/install_audit.py` + `INSTALL.md` counts (INST-1), the cp1252-parametrize list, AND any per-tool inventory-pin test must each enumerate BOTH `vault_edit.py` and `skill_vault_write_safety_audit.py`. The full suite is the backstop; the BC-PROJ-7/9 checklist under-enumerates sibling inventory-pin tests (slice-081/087/089 lesson).

## Authorization model for this slice

Not applicable — local build/skill tooling, no auth/authz surface. Per the cooperative-not-adversarial model ([[ADR-067]]): vault-write-safety is a **data-integrity control, NOT a security boundary**. It defends two cooperating Claude sessions / parallel slices on one machine, not a malicious actor.

## Error model for this slice

- `vault_edit.py`: exit **0** (appended) / **2** (usage — bad/escaping `--file`, missing content; fail-VISIBLE). Inherits `safe_append_text`'s runtime model (bounded EPERM-retry → loud `PermissionError` after exhaustion; `TimeoutError` on lock-acquire timeout).
- `skill_vault_write_safety_audit.py`: exit **0** (clean) / **1** (≥1 unrouted+unexempted mutation site — names each `skills/<x>/SKILL.md:line`) / **2** (usage — `skills/` unreadable; fail-VISIBLE per R-7). Fail-closed: an unclassifiable mutation site is a VIOLATION, never a silent pass.

## R-32 disposition (recorded fully at /reflect; planned here)

This slice closes the **skill-driven APPEND** sub-class of R-32 (the append-class mutators route through `vault_edit`; the SVW-1 audit makes an un-routed skill append un-mergeable). Combined with slice-094 (Python-writer sub-class), the **write/append** axis of R-32 is closed.

**R-32 NARROWS, it does not fully RETIRE** (amends the brief's AC4/Intent per the Q3 decision): a **skill-driven read-modify-write / lost-update residual** remains (`_index.md` recent-10 table; in-place risk-register status flips). This residual:
- is **not-yet-live** (only fires post-flip, when the vault is shared+untracked). **Pre-flip (Critic m1), every shared-aggregate vault file — `risk-register.md`, `lessons-learned.md`, `_index.md`, `build-checks.md`, `shippability.md`, `methodology-changelog.md` — is git-TRACKED ([[ADR-066]]), so `/commit-slice` PCR still resolves their conflicts loudly; R-32's silent-corruption hazard is strictly POST-flip.** (The brief's Intent phrase "no merge-time PCR to catch it" describes the post-flip state, not today — strengthens AC5's no-flip-safety claim.)
- is **explicitly exempt-marked** in the routed skills (visible, not hidden);
- is **owned by the flip slice** (which must serialize `/reflect`+`/archive` rewrites — e.g. a held vault-lease — as part of removing git-conflict mediation).

So at `/reflect`: record R-32 as **`mitigating`** with the append sub-class closed-with-evidence (094+095) and the rewrite/lost-update residual documented as the flip-slice gate. This is the slice-084/085 "narrow, don't force-retire" pattern slice-094's own design cites.

## Sequencing note (parallel slice-094 — NOT cleanly non-overlapping)

slice-094 (Python-writer sub-class) is in-flight in a sibling worktree and shares coordination files with 095. To avoid merge collisions (the R-28/R-33 parallel-version-bump hazard), 095 deliberately sits ABOVE 094's in-flight claims:

- **ADR**: 094 claims **ADR-086** (VWS-1) → 095 takes **ADR-087** (slice-088 "take the higher number" precedent).
- **VERSION / methodology-changelog**: 094 plans **v0.79.0** → 095 plans **v0.80.0** (`## v0.80.0` entry). Concrete **second-merger checklist (Critic m2 — "rebase up" is more than a rebase)**: whichever of 094/095 lands SECOND MUST (1) renumber its changelog entry to the next free version above the first-merger's (e.g. if 095 lands first at v0.80.0, 094 renumbers its entry to v0.81.0); (2) re-pin its `test_v_0_NN_0_*` entry-pin test to the new version; (3) re-run the full PMI-1 atomic bump (`VERSION` + `plugin.yaml` + the installed `ai-sdlc-VERSION` + changelog) so MCFS-1/AVFS-1/TVFS-1 stay green; (4) re-run shippability propagation for any renamed entry-pin test (the FBCD-1 multi-surface version-literal sweep). This is named here so it is not *discovered* at the second merge.
- **Shared coordination files** (`risk-register.md` R-32 note, `shippability.md` row, `/build-slice`+`/validate-slice` gate-roster prose): additive edits → PCR-resolvable SOFT conflicts at merge. Build 095 in its isolated BRANCH-2 worktree (already done — `slice/095-…`); reconcile with master before the pre-finish full-suite (the slice-092/R-33 `git merge master` lesson).
- **RULE-ID**: 094 = VWS-1, 095 = **SVW-1** — disjoint, no collision.

## Why SVW-1 is acceptable despite ADR-029 (Critic B1)

[[ADR-029]] (BC-1 / BCI-1, slice-030A) established that **vault integrity is enforced by a deterministic downstream GATE, not by hardening or inspecting the LLM-executed prose** — Options 1 ("harden the Step-5b prose") and 2 ("route prose through a function") were rejected for Option 3 (a deterministic gate over a tracked canonical fixture that catches the violation regardless of LLM obedience). SVW-1 is a static prose audit, so the fair question is whether it is the very prose-inspection shape ADR-029 rejected.

**It is — and that is acceptable here for a specific reason ADR-029's case did not have: there is no oracle artifact to gate on.** BCI-1 can use Option 3 because `build-checks.md` has a git-tracked canonical fixture (`canonical_project_checks.md`) — a deterministic expected-value the live file is diffed against. An arbitrary `vault_edit append` of **LLM-authored** content (a fresh risk entry, a lessons bullet, a shippability row) has **no expected-value oracle** — the content is generated, not reproducible — so no BCI-1-style downstream invariant gate is constructible for it. The available controls are therefore: **(1)** the wrapper (`vault_edit append`) which makes the write concurrency-safe *when used*; **(2)** the SVW-1 prose audit which guarantees no `skills/*/SKILL.md` *prescribes* a raw bypass (drift-prevention — the CAD-1/OSDG-1 philosophy: keep the executable prose honest); **(3)** the pre-flip git/PCR backstop (m1); **(4)** the cooperative model ([[ADR-067]]). SVW-1 is control (2) — and it is honestly scoped as such, NOT claimed as a fail-closed completeness guarantee over writes. The one control ADR-029 would want — a deterministic gate over the actual write — is **structurally unconstructible** here, which is the material difference from the BCI-1 case. This is recorded in [[ADR-087]] §Consequences.

## Honest residual: runtime obedience (not closed by this slice, by construction)

The SVW-1 audit is **static** — it proves the SKILL.md *prose* prescribes the safe channel. Nothing prevents Claude from invoking the raw `Write`/`Edit` tool on a vault file at runtime in violation of the prose (the same class R-2 documents for prose-driven behavior). This is acceptable under the cooperative model ([[ADR-067]]) and is the intended scope: SVW-1 keeps the prose honest so a future skill edit cannot silently re-introduce an unsafe instruction; runtime obedience is a separate (un-auditable-at-build) axis, noted at /reflect as a known limitation, not a slice-095 deliverable.
