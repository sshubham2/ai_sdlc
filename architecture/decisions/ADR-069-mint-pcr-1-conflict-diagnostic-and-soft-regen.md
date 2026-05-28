---
id: ADR-069
title: Mint PCR-1 — parallel-conflict-resolution v1 (diagnostic + soft-conflict auto-regen)
date: 2026-05-28
slice: slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen
reversibility: expensive
status: accepted
supersedes: null
---

# ADR-069: Mint PCR-1 — parallel-conflict-resolution v1 (diagnostic + soft-conflict auto-regen)

## Context

The parallel-slice workflow shipped across slices 066-074 — BRANCH-2 (worktree-per-slice), PSQ-1 (queue output), PSQ-2 (claim machinery), PSQ-3 (rebase + conflict-STOP at `/commit-slice --merge`) — makes parallel slice execution physically possible, queue-discoverable, ownership-coordinated, and rebase-conflict-detected.

But a gap surfaced during the 2026-05-28 conversation about a 5-session parallel workflow: **every parallel slice regenerates `architecture/slice-queue.md` (PSQ-1 Step 6.5) + `architecture/slices/_index.md` (`/archive` Step 4) + appends rows to `architecture/shippability.md` (per-slice convention)**. When 5 sessions concurrently produce slices and `/commit-slice --merge` sequentially, every merge after the first hits rebase conflicts on these auto-regenerated state files even when code blast-radii are perfectly disjoint. PSQ-3 currently STOPs on every such conflict and asks for manual resolution via SOAD-1 3-option ask.

For a 5-session pipeline, that's 4+ manual STOPs per merge sequence — defeating the value proposition of parallel-slice work. The conflict shape is high-frequency (every parallel merge) but low-judgment (mechanical regen, no Builder/Critic decision needed) — exactly the case for auto-resolution.

A graduated solution is needed: auto-resolve the high-frequency low-judgment conflicts (SOFT class); preserve manual + Critic review for low-frequency high-judgment conflicts (HARD class — source code, ADRs); handle the in-between (VAULT_CLAIM — same candidate claimed by two sessions) with a cheaper-than-Critic resolution path (timestamp-winner).

This ADR mints **PCR-1** — the first rule on a new family axis (parallel-conflict-resolution), sibling to PSQ-N. PCR-1 v1 ships the diagnostic + SOFT-class auto-regen path; **PCR-2 (slice-077)** will plug in VAULT_CLAIM resolution + HARD-conflict Critic stack + TRI-RESOLVE-1 user triage.

## Options considered

1. **Status quo — manual SOAD-1 STOP on every conflict (PSQ-3 as-is)**
   - Pros: simple; no new code; no auto-resolution risk
   - Cons: high-frequency manual interrupt for low-judgment merges; 5-session parallel-slice value proposition undermined; defeats the parallel-slice family axis's purpose

2. **Auto-resolve EVERYTHING via heuristic (`-X theirs` / `-X ours` / merge driver)**
   - Pros: zero manual interrupts
   - Cons: HARD-class conflicts on source code silently auto-merged — high risk of silent semantic regression; violates `/commit-slice` "never auto-resolve" Critical rules block; no audit trail for which resolutions were applied; no Critic review on contested resolutions

3. **Blanket Critic stack on every conflict (full `/critique` + `/critique-review` even for SOFT)**
   - Pros: uniformly conservative; consistent with 3-Critic stack discipline
   - Cons: ~80% of parallel-slice conflicts are SOFT (no judgment needed); blanket Critic adds 1-3 minutes per conflict × 4+ conflicts per merge sequence × every parallel-merge = parallel work becomes 4× slower than serial; Critic-agent timeout could halt the entire pipeline; cost-prohibitive

4. **Graduated: 3-class taxonomy (SOFT auto-regen / VAULT_CLAIM timestamp-winner / HARD full Critic stack)** *(chosen)*
   - Pros: high-frequency low-judgment SOFT conflicts auto-resolved without manual interrupt or Critic latency; high-judgment HARD conflicts preserved through the existing 3-Critic stack discipline; VAULT_CLAIM (race condition) resolved cheaply via timestamp; auditable (per-resolution log); reversible (each class has explicit fail-closed STOP fallback)
   - Cons: more design surface (3 classes, 3 resolution paths); SOFT-class file-set must be enumerated and pinned (drift risk if a future slice introduces a new auto-regenerated state file); fail-closed semantics need careful design (UNKNOWN class must never silently default to SOFT)

5. **Extend PSQ-3 inline rather than mint a new rule family**
   - Pros: simpler taxonomy; one rule on the parallel-slice family axis covers both detect + resolve
   - Cons: PSQ-3's scope (rebase-and-conflict-discipline at `/commit-slice --merge`) is structurally narrower than conflict-resolution (which also applies to future `--push`-time rebase per PSQ-4, future `gh pr merge --rebase` integration, future cross-tool conflict surfaces); separating the families keeps PSQ-N focused on rebase mechanics and PCR-N focused on resolution semantics; symmetric to the BC-N / NFR-N / TF-N family separation in the broader methodology

## Decision

**Mint PCR-1** as the first rule on the new parallel-conflict-resolution family axis (PCR-N). PCR-1 v1 ships diagnostic + SOFT-class auto-regen. PCR-2 (slice-077) extends to VAULT_CLAIM resolution + HARD-conflict full Critic stack + TRI-RESOLVE-1 user triage.

### 5-class taxonomy

| Class | Definition | Resolution path | Critic involvement | Shipped in |
|---|---|---|---|---|
| **SOFT** | All U-prefixed files are members of the canonical SOFT file-set: `{architecture/slice-queue.md, architecture/shippability.md}` — **2 canonical files** (per /critique B3 ACCEPTED-FIXED: `_index.md` dropped because `/archive` skill's regen is Haiku-LLM-dispatched per COST-1, not deterministic; per /design-slice Step 2 clarifying answer: methodology-changelog.md dropped because PMI-1 atomic-bump means subtle PMI-1 inconsistency on concurrent bumps). No other U-files present. AND no same-candidate-different-identity claim collision (which classifies as VAULT_CLAIM per the gate below). | Auto-regen via dispatch: for `slice-queue.md`, take rebase-target stage `:3:` as candidate baseline + merge claims from BOTH stages via `tools.slice_queue_claim.parse_queue_text` + write via `tools.slice_queue_writer.write_slice_queue`; for `shippability.md`, row-union by slice number + sort ascending. `git add` + `git rebase --continue`. Append entry to `architecture/parallel-conflict-resolution-log.md`. | **NONE** — deterministic regen from current truth; no judgment to review. | **slice-076 (this slice)** |
| **VAULT_CLAIM** | Sole U-file is `architecture/slice-queue.md` AND the only differences between branches' versions are `Claimed-by:` / `Claimed-at:` field lines on the same candidate — including the **same-candidate-different-identity** case (any candidate name appears in BOTH branches' parsed claim dicts with DIFFERENT `Claimed-by:` values per /critique B4 ACCEPTED-FIXED). | Timestamp-winner: earlier `Claimed-at:` wins; loser auto-re-picks via `/slice-pick` (deferred to slice-078 SP-1 which depends on PCR-2). | **LIGHT** — single Critic pass validates winner's claim integrity (no malformed `Claimed-by:`, no clock-skew anomaly). | **slice-077 (PCR-2)** |
| **HARD** | Any U-file is a source-code file (`skills/*/SKILL.md`, `tools/*.py`, `agents/*.md`, `tests/**`, `architecture/decisions/ADR-*.md`, **`architecture/slices/_index.md`**, **`methodology-changelog.md`**, or any file not in the 2-member SOFT file-set and not a pure-claim VAULT_CLAIM diff). | Full Critic stack: `/critique` reviews proposed resolution; `/critique-review` meta-reviews; TRI-RESOLVE-1 user triage; only on CLEAN apply. | **FULL** stack (Critic + meta-Critic + user). | **slice-077 (PCR-2)** |
| **MIXED** | At least one SOFT-class U-file AND at least one non-SOFT U-file (HARD or VAULT_CLAIM). Both SOFT+HARD and SOFT+VAULT_CLAIM combos classify as MIXED (per /critique M4 ACCEPTED-FIXED disambiguation). | Treated as HARD for resolution purposes (atomicity — do not partially auto-resolve the SOFT portion). Full Critic stack applies to the entire merge. | **FULL** stack. | **slice-077 (PCR-2)** |
| **UNKNOWN** | `classify_conflict` cannot determine class (e.g., rebase state inconsistent / no U-entries despite rebase-in-progress, file content unreadable, git state unexpected, stage-missing on both sides simultaneously). | **Fail-closed STOP** — never auto-resolve. Skill falls through to existing PSQ-3 SOAD-1 ask. APED-1 silent-disable / default-off-on-malformed criterion: never silent-default to SOFT. | N/A — escalates to user. | **slice-076 fail-closed behavior** (pinned by `test_classify_conflict_returns_unknown_when_rebase_state_empty` + `test_resolve_soft_conflict_returns_stop_on_unknown_class`) |

### SOFT-class file-set (load-bearing pin)

```python
_SOFT_FILE_SET: frozenset[str] = frozenset({
    "architecture/slice-queue.md",
    "architecture/shippability.md",
})
```

**2 canonical files, forward-slash-keyed.** Pinned in `tools/parallel_conflict_resolver.py` as a module-level constant; regression-pinned by `test_soft_file_set_is_two_canonical_files_forward_slash_keyed`. Adding a file to this set is a methodology change requiring a new PCR-N rule + ADR + entry-pin (do not silently extend).

**`architecture/slices/_index.md` deliberately NOT in SOFT-set** (per /critique B3 ACCEPTED-FIXED): `skills/archive/SKILL.md` Step 3 regenerates `_index.md` via **Haiku-LLM dispatch** per COST-1, NOT a deterministic scan. The Aggregated-lessons-block prose is Haiku-synthesized from N reflections; re-running `/archive` Haiku-dispatched produces different prose summarizing the same input. PCR-1 cannot reproduce this output. `_index.md` conflicts therefore fall to HARD-class and surface via PSQ-3's existing SOAD-1 STOP; user re-runs `/archive` manually post-merge to regenerate the lessons-block. PCR-2 may revisit if a deterministic algorithm emerges.

**`methodology-changelog.md` deliberately NOT in SOFT-set** (per /design-slice Step 2 clarifying answer 1): PMI-1 5-part atomic bump means two parallel slices both bumping to v0.73.0 could produce subtly inconsistent merged entries (different RULE-IDs, paired-pin test names, ADR refs). Auto-merging changelog risks silent BC-PROJ-10 violations. Keep in HARD; let the Critic stack at PCR-2 review the proposed resolution.

### Path normalization convention (per /critique M1 ACCEPTED-FIXED — APED-1 Windows bug)

`_SOFT_FILE_SET` is forward-slash-keyed (2 string entries — per /critique B3 ACCEPTED-FIXED `_index.md` dropped). `ConflictDiagnostic.u_files` is typed `list[str]` — NOT `list[Path]` — because `git status --porcelain` emits forward-slash paths on all OSes per [git-status documentation](https://git-scm.com/docs/git-status), and `str(Path("architecture/slice-queue.md"))` on Windows produces `"architecture\\slice-queue.md"` which would miss the frozenset membership check. Any `Path` constructed internally is normalized via `.as_posix()` before `_SOFT_FILE_SET` lookup. JSON CLI output (`--json` mode) uses raw forward-slash strings throughout; no `str(Path)` casts in serialization. Pinned by `test_soft_file_set_membership_uses_forward_slash_keys_on_windows_paths`.

This is the canonical fix shape for the M1 finding — APED-1 executed against the membership predicate caught Windows backslash collision before /build-slice. Future PCR-N rules that mint path-based predicates should apply the same convention.

### Layer separation: PCR-1 vs PSQ-3

| Layer | Owner | Activity |
|---|---|---|
| **PSQ-3** (rebase mechanics) | `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 | Runs `git rebase`; categorizes outcome (fast-forward no-op / clean replay / **conflict**). On conflict, identifies U-files. |
| **PCR-1** (conflict resolution v1) | `tools/parallel_conflict_resolver.py` | Given the U-file set, classify (SOFT/VAULT_CLAIM/HARD/MIXED/UNKNOWN); resolve SOFT inline; emit diagnostic for all classes. |
| **PSQ-3 SOAD-1 STOP** | `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 | Fallback after PCR-1 returns `action: STOP` — existing 3-option ask (abort / manual resolve / cancel) plus PCR-1's enhanced concerned-slice diagnostic. |

PCR-1 strictly adds a branch BEFORE PSQ-3's existing STOP path. The existing SOAD-1 3-option ask, `git rebase --abort` recovery hint, and all of PSQ-3's prose remain verbatim. PCR-1 is non-disruptive to PSQ-3 — if PCR-1's helper module is missing or fails to import, PSQ-3 behavior is unchanged (bootstrap defense via try/except wrapping per slice-067 / PSQ-1 precedent at ADR-064 § Consequences).

### Resolution algorithm for SOFT class (2-file, per /critique B1 ACCEPTED-FIXED redesign)

For each SOFT-file U-entry:

| File | Resolution | Edge cases |
|---|---|---|
| `architecture/slice-queue.md` | (1) `git show :2:architecture/slice-queue.md` + `git show :3:architecture/slice-queue.md` → both branches' queue text (stage `:3:` = rebase-target). (2) `tools.slice_queue_claim.parse_queue_text(text_2)` + `parse_queue_text(text_3)` → 2 claim dicts (claim metadata only — per /critique B1, `parse_queue_text` does NOT extract PSQ-1 enumeration fields). (3) **VAULT_CLAIM gate** (per /critique B4 ACCEPTED-FIXED): walk the keys of both claim dicts; if ANY candidate name appears in BOTH with DIFFERENT `Claimed-by:` values, abort with `action: STOP, conflict_class: VAULT_CLAIM` — do NOT proceed (PSQ-2's existing newest-`Claimed-at:`-wins semantics would silently auto-resolve what PCR-2 reserves for timestamp-winner + light-Critic). (4) Otherwise compute `merged_claims = newest-Claimed-at-wins union of claims_2 + claims_3` (in-helper merge, deterministic). (5) Call new private helper `_overlay_claims_on_queue_text(text_3, merged_claims) -> str` per /critique-review M-add-1 ACCEPTED-FIXED option (2) — surgically updates `**Claimed-by:**` + `**Claimed-at:**` lines under each candidate's `**Risk-retired:**` line in `text_3` (which is used **verbatim** as the result-baseline). Candidates in `merged_claims` whose names are not present in `text_3` are dropped — will re-surface at next `/slice` Step 6.5 regen. **NO `write_slice_queue` dispatch** for SOFT-resolve (avoids the B1 phantom-parser trap; no candidate-parser mint scope). (6) Write the overlay result + `git add` + audit-log entry. | (a) `git show :3:` non-zero (file added only on rebased branch): treat as empty target; resolved queue uses `text_2` verbatim with claims merged (the rebased branch is the new baseline; this is the documented exception to the "rebase-target verbatim" rule when target is absent). (b) `git show :2:` non-zero (file added only on rebase-target): treat as empty rebased state; resolved queue uses `text_3` verbatim (no claim overlay needed beyond `text_3`'s existing claims). (c) Both stages missing simultaneously: UNKNOWN class (defense-in-depth). |
| `architecture/shippability.md` | Parse both branches' tables (header + row blocks); union rows keyed by leading `\| <NN> \|` slice number; sort ascending; write back with header preserved. | (a) `git show` non-zero on one stage: treat as empty-rows; resolved file uses the other stage's rows. (b) Same slice number on both stages with different row content (impossible in legitimate state — each slice owns one row): STOP with HARD diagnostic. |

After all SOFT files regenerated + post-VAULT_CLAIM-gate passed: `git add` each + `subprocess.run(['git', 'rebase', '--continue'])`. If `--continue` fails post-stage (additional conflicts beyond the SOFT set surfaced during continuation — defense-in-depth case; shouldn't happen if `classify_conflict` was correct), STOP with diagnostic. **Defensive post-overlay guard in `_regen_slice_queue`** (per /critique-review M-add-1 ACCEPTED-FIXED algorithm redesign): after the `_overlay_claims_on_queue_text` call, re-parse the resolved queue text via `parse_queue_text` and re-verify no same-candidate-different-identity remains (catches `classify_conflict` false-negatives; per /critique B4 ACCEPTED-FIXED defense-in-depth). The check is cheap (single re-parse) and load-bearing — without it a `classify_conflict` predicate bug could let a VAULT_CLAIM-shaped state through to SOFT auto-resolve.

### Audit log: `architecture/parallel-conflict-resolution-log.md`

Append-only audit trail. Created lazily on first append. Each entry: ISO-8601 UTC timestamp + repo HEAD SHA pre-resolution + U-files list + concerned slices + per-file resolution action. Standard append-only-log pattern (mirrors `architecture/critic-calibration-log.md`).

The log is **best-effort** — write failures (disk full, permissions) log to stderr but do NOT block the resolution (the rebase has already been continued). The log is audit trail, not a precondition. One exception to PCR-1's fail-closed pattern; consciously chosen.

**Concurrency / race-acceptance** (per /critique M7 ACCEPTED-FIXED): two parallel `/commit-slice --merge` sessions hitting SOFT-class auto-resolve in the same wall-clock moment could race the lazy-create or interleave appends. Per ADR-067 § Adversarial model (cooperative-not-adversarial), PCR-1 carries this model forward unchanged — concurrent appends may produce interleaved entries; this is documented and ACCEPTED for the cooperative threat model. The slim probability (2 sessions both finishing slice work + both running `--merge` against the same default branch simultaneously) doesn't justify file-locking complexity. If parallel-slice cadence increases to where this becomes empirically observable (audit-log entries garbled), PCR-2 may add `fcntl.flock` / `msvcrt.locking` serialization. Until then: race-acceptance per cooperative model.

Implementation: a single `open(path, "a", encoding="utf-8")` per append (no separate header-write step); the `_AUDIT_LOG_HEADER` is written only when the post-append file ends up starting with the entry header (deterministic check via `os.path.exists` + size==0 BEFORE the append). Atomicity at the bytes-of-one-append level relies on POSIX/Windows append-write semantics (small writes are typically atomic at OS level).

### Fail-closed contract (load-bearing)

- `classify_conflict` returning `UNKNOWN` → resolver exits 1 with stderr diagnostic; skill falls through to existing SOAD-1 STOP. Never silent-default-to-SOFT.
- `_soft_regen_<file>` raising any exception → exit 1 with stderr; rebase remains in conflicted state (no `--continue` called); existing SOAD-1 STOP fallback.
- `slice_queue_writer` import failure (bootstrap window before slice-067) → exit 1 with bootstrap-defense stderr; existing SOAD-1 STOP fallback.
- Any U-file outside `_SOFT_FILE_SET` → classified as HARD (or MIXED if SOFT-files also present); resolver exits 0 with `action: STOP`; existing SOAD-1 STOP fallback.

The APED-1 silent-disable / default-off-on-malformed criterion applies directly: PCR-1 must never silently auto-resolve on UNKNOWN or partial-malformed state. The cost of fail-closed is one extra SOAD-1 ask in the bootstrap case; the cost of fail-open is silent semantic regression — asymmetric in favor of fail-closed.

### Methodology classification

- **MEPD-1 (a) rule path** (per ADR-040 / ADR-041): PCR-1 mints a new RULE-ID + entry-pin (`test_v_0_73_0_pcr_1_entry_present_in_repo` + `test_v_0_73_0_pcr_1_shippability_consumer_propagation`) + 5-leg PMI-1 atomic bump 0.72.0 → 0.73.0. NOT the documented-why-none branch.
- **First rule on the parallel-conflict-resolution family axis**: sibling family to PSQ-N. Cross-references: PSQ-3 (sub-step 2.5 — detect); PSQ-2 (Claimed-by/Claimed-at format — VAULT_CLAIM detection); PSQ-1 (slice_queue_writer reuse — SOFT regen).
- **PCA-1 pipeline position unchanged** for `/commit-slice` — `auto-advance: false` (always user-invoked) per ADR-020. PCR-1 enhances Step 5b sub-step 2.5 within the same skill; doesn't change the skill's auto-advance contract.
- **CRSI-1 v1 walking-skeleton**: code-Critic findings on `tools/parallel_conflict_resolver.py` may defer to bundled-cleanup-at-N+1 per voluntary-restraint discipline if applicable.

### Adversarial model

Per ADR-067 § Adversarial model (PSQ-2 cooperative-not-adversarial threat model), carried forward unchanged:

- PCR-1 is **cooperative coordination**, NOT a security boundary.
- A malicious local actor with filesystem write to the rebase state can bypass any methodology rule by editing files directly.
- A malicious actor with filesystem write to `_SOFT_FILE_SET` files can poison the auto-regen result (the resolver trusts both branches' versions of those files as inputs to the regen).
- Adversarial filesystem-lock-and-transactional-queue protections are out of scope per ADR-067 § Out of scope and remain out of scope for PCR-1.

## Consequences

- **Reversibility**: **expensive**. Once parallel sessions rely on the SOFT auto-regen path, reverting requires either:
  - (a) re-introducing manual STOPs on every state-file conflict — breaks 5-session parallel-slice workflow; OR
  - (b) finding an alternative auto-resolve — non-trivial; the current `slice_queue_writer.write_slice_queue` API + claim-merge semantics + archive-scan regen + shippability row-union are the simplest mechanism on the current vault shape.
  
  The audit log `architecture/parallel-conflict-resolution-log.md` becomes load-bearing once first-appended (downstream consumers may parse it for cross-slice resolution audits).

- **Effects on PSQ-3**: strictly additive — PSQ-3 sub-step 2.5 prose grows by ~1 paragraph + branch logic; existing SOAD-1 3-option ask + `git rebase --abort` recovery + Conflict-STOP path preserved verbatim. CAD-1 + drift-prevention pins on PSQ-3 unchanged.

- **Effects on PSQ-1**: `tools.slice_queue_writer.write_slice_queue` becomes a multi-consumer API (currently 2: `/slice` Step 6.5 + `tools.slice_queue_claim`; PCR-1 adds 3rd consumer). API stability inherited from PSQ-1's documented library API per ADR-064.

- **Effects on PSQ-2**: PSQ-2's `parse_queue_text` becomes a multi-consumer parser (PCR-1's `_extract_claim_diff` calls it). Parser stability inherited from PSQ-2 per ADR-067.

- **New rule family**: PCR-N introduces a new family axis. Future siblings (PCR-2 = vault-claim + hard; PCR-3+ TBD). The naming asymmetry with PSQ-N (parallel-slice-queue) vs PCR-N (parallel-conflict-resolution) is intentional — both prefixed with "P" (parallel) but distinct second token (SQ vs CR) for the operational layer.

- **Forward compatibility**: VAULT_CLAIM + HARD classes are declared and reserved here; PCR-2 will plug in resolution paths. The `ConflictClass` enum's members are stable from this slice; only the resolution dispatch is extended. PCR-1 → PCR-2 contract: PCR-2 mutates `resolve_*` functions; PCR-2 does NOT remove or rename `classify_conflict` outputs.

- **Cross-spec parity audit candidate** (P3.6 in slice-075's source-pending-items.txt): the parallel-slice-family-parity-audit slice (queued at slice-076's regenerated slice-queue.md) becomes more valuable post-PCR-1 — the rule family now has 5 members (BRANCH-2 + PSQ-1 + PSQ-2 + PSQ-3 + PCR-1) with shared default-resolution-helper + WORKTREE=skip-grammar + SOAD-1-form invariants worth auditing.

- **`/code-review` scope inclusion**: `tools/parallel_conflict_resolver.py` is in /code-review's in-scope filter (matches `tools/*.py` glob); shippability row added per BC-PROJ-9 5-inventory. M5 INCLUDE-direction admit per slice-069 ADR-066 covers the new audit log file under `architecture/parallel-conflict-resolution-log.md`.

## Reversibility

**Expensive** (per ADR-066's 3-class reversibility taxonomy — cheap / **expensive** / irreversible).

Concrete reversibility cost: as soon as parallel-slice sessions start relying on PCR-1's SOFT auto-regen (slice-077+ at the earliest, after PCR-2 ships the rest of the conflict story), reverting requires:

1. Restoring `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 to the pre-PCR-1 prose (delete the PCR-1 branch).
2. Removing `tools/parallel_conflict_resolver.py` from `_CANONICAL_TOOLS` + `plugin.yaml` + `INSTALL.md` count + this shippability row (BC-PROJ-9 4-inventory undo).
3. Deleting or archiving `architecture/parallel-conflict-resolution-log.md` (or preserving as audit-only).
4. Methodology-changelog v0.73.0 entry SUPERSEDES via new v0.NN.0 entry (SUP-1 per ADR-040; never edit in place).
5. Forward-syncing all of the above to installed copies (CAD-1 + OSDG-1 byte-equality).
6. Any downstream consumers (PCR-2's resolve_soft_conflict + future PCR-3+ consumers) need parallel reversion.

The 5+ surface revert + the methodology-changelog SUP-1 chain make this an **expensive** reversal but NOT irreversible. The identity model + tenant model are untouched (per ADR-066 examples of irreversible — those would be primary-entity-shape changes, which PCR-1 does not introduce).

Reverting is unlikely in practice: PCR-1's design is well-bounded (SOFT file-set is 2 named files; auto-regen dispatches to existing tooling; fail-closed semantics on UNKNOWN). Empirical refutation would have to come from an unforeseen failure mode of the SOFT auto-regen on a corner case — at which point we'd more likely refine (add to SOFT-file-set audit, tighten classify_conflict predicates) than revert.
