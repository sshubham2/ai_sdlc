# Design: Slice 076 add-pcr-1-conflict-diagnostic-and-soft-regen

**Date**: 2026-05-28
**Mode**: Standard
**Mints**: PCR-1 rule (parallel-conflict-resolution v1; methodology-changelog v0.73.0); ADR-069 (new family axis).
**Posture**: MEPD-1 (a) rule path — RULE-ID + entry-pin + atomic PMI-1 bump per ADR-040 / ADR-041.

## What's new

- **Rule PCR-1** minted in `methodology-changelog.md` § v0.73.0 — first rule on the parallel-conflict-resolution family axis. Sibling family to `PSQ-N` (parallel-slice-queue). Distinct layer from PSQ-3 (PSQ-3 = detect conflict at `/commit-slice --merge` Step 5b sub-step 2.5 rebase; PCR-1 = resolve conflict before STOP fires for SOFT class).
- **ADR-069** at `architecture/decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen.md` — Decision section documents the 3-class taxonomy inline + the SOFT-class file-set + the SOFT-class resolution algorithm. `VAULT_CLAIM` + `HARD` classes are declared and reserved for slice-077 (PCR-2) with explicit "STOP for now" semantics.
- **New helper module** `tools/parallel_conflict_resolver.py` (~400 LOC est.) exposing:
  - Library API: `diagnose_conflict(repo_root: Path) -> ConflictDiagnostic`, `classify_conflict(diag: ConflictDiagnostic) -> ConflictClass`, `resolve_soft_conflict(diag: ConflictDiagnostic) -> ResolutionResult`.
  - Data classes (frozen dataclasses): `ConflictDiagnostic` (u_files: list[Path] + concerned_slices: dict[Path, list[ConcernedSlice]] + claim_history: list[ClaimEntry]), `ConcernedSlice` (slice_id, blast_radius, mission_brief_link, last_commit_iso), `ConflictClass` (Enum: SOFT / VAULT_CLAIM / HARD / MIXED / UNKNOWN), `ResolutionResult` (action: APPLIED | STOP, regenerated_files: list[Path], reason: str | None).
  - CLI: `python -m tools.parallel_conflict_resolver [--diagnose | --classify | --resolve-soft] [--json]` exposing each library API independently for testability + direct invocation.
- **Edit to `skills/commit-slice/SKILL.md`** Step 5b sub-step 2.5 "Conflict" outcome path (currently L183–186): insert a NEW soft-conflict-resolution branch BEFORE the existing SOAD-1 3-option STOP block. Order: rebase fires → conflict surfaces → PCR-1 resolver invoked → if SOFT, auto-resolve + `git rebase --continue` + log + skip SOAD-1 + proceed to sub-step 3; else (VAULT_CLAIM / HARD / MIXED / UNKNOWN) → enhanced diagnostic prints concerned-slice detail + falls through to existing SOAD-1 STOP block. The existing 3-option SOAD-1 ask remains verbatim; the existing `git rebase --abort` recovery hint remains verbatim. PCR-1 is strictly additive to PSQ-3's existing structure.
- **New audit log file** `architecture/parallel-conflict-resolution-log.md` — append-only audit trail of every PCR-1 soft-conflict auto-resolution. Each entry: ISO-8601 UTC timestamp + repo HEAD SHA pre-resolution + U-files list + concerned-slices map + resolution actions taken (which regen invoked per file). Mirrors the `architecture/critic-calibration-log.md` pattern. Created lazily (first append creates the file with a header).
- **Updated tests** across `tests/methodology/` + `tests/skills/parallel_conflict_resolver/` per TF-1 plan (mission-brief Test-first plan, ~20 PENDING rows).
- **5-leg PMI-1 atomic bump** 0.72.0 → 0.73.0: `VERSION`, `plugin.yaml.version`, `pyproject.toml [project].version`, `methodology-changelog.md ## v0.73.0` header, installed `~/.claude/ai-sdlc-VERSION`.
- **BC-PROJ-9 5-inventory fan-out** for the new `tools/parallel_conflict_resolver.py` module: `plugin.yaml` tools block + `tools/install_audit.py::_CANONICAL_TOOLS` + `tests/methodology/test_utf8_stdout_regression.py::_ROOT_ONLY_TOOLS` + `INSTALL.md` tool-count literal **at L22 AND L166 (both `30 → 31`)** per /critique M6 ACCEPTED-FIXED + `architecture/shippability.md` row for slice-076. The two-site INSTALL.md pin is pinned by `test_install_md_tool_count_literal_is_at_31_at_both_sites_post_pcr_1` to prevent INST-1 audit failure from desync.
- **BC-PROJ-10 paired-pin tests** in `tests/methodology/test_methodology_changelog.py`: `test_v_0_73_0_pcr_1_entry_present_in_repo` + `test_v_0_73_0_pcr_1_shippability_consumer_propagation`. Per /critique m3 ACCEPTED-FIXED + /critique-review M-add-3 ACCEPTED-FIXED (precedent harmonization), the v0.73.0 changelog entry MUST include these 5 load-bearing substring anchors (each pinned by the entry-present test): (a) `## v0.73.0` header literal; (b) `PCR-1` rule reference; (c) `ADR-069` reference; (d) `parallel-conflict-resolution` canonical phrase; (e) `mints a new rule` literal (matches v0.68.0 BRANCH-2 + v0.69.0 PSQ-1 + v0.72.0 PSQ-3 precedent at `tests/methodology/test_methodology_changelog.py`). The longer phrase `'mints a new rule on a new family axis'` was an earlier Builder draft that diverged from precedent; per /critique-review M-add-3 reverted to the 3-word literal.

## What's reused

- **`tools/slice_queue_writer.write_slice_queue()`** at `tools/slice_queue_writer.py:665` — dispatched as the SOFT-class resolution path for `architecture/slice-queue.md`. PCR-1 calls it directly (library API, NOT subprocess). The candidates list is NOT re-derived (re-derivation requires `/slice`'s Step 1 sourcing which is Claude-judgment, not deterministic); instead, PCR-1 takes the **rebase-target branch's queue as candidate baseline** (via `git show :3:architecture/slice-queue.md` — stage 3 = rebase-target / MERGE_HEAD per git-rebase semantics; one-branch's candidate metadata is fully sufficient — the next `/slice` regen reconstructs from current vault state). Claim-history (`Claimed-by:` / `Claimed-at:` lines) IS merged from BOTH branches via PSQ-2's existing newest-`Claimed-at:`-wins merge semantics already embodied in `write_slice_queue`'s read-existing-queue-and-merge path at `tools/slice_queue_writer.py:692-708`. Candidates that exist ONLY on the rebased branch (stage 2 / HEAD / ours) are dropped at the soft-resolve and re-surface at the next `/slice` regen — documented behavior, not a bug.
- **`tools/slice_queue_claim.parse_queue_text()`** at `tools/slice_queue_claim.py:201` (PSQ-2 claim parser; signature: `text: str -> dict[str, dict[str, object]]` keyed by candidate name; **returns ONLY claim metadata** — `Claimed-by:` / `Claimed-at:` / forward-compat `_extra_field_lines`, per docstring at `tools/slice_queue_claim.py:230-234`; does NOT extract the PSQ-1 enumeration fields Source/Blast-radius/Parallel-safety/Effort/Risk-retired). Used by PCR-1 `_extract_claim_diff` ONLY to enumerate the claim-state on both branches' versions of `slice-queue.md` for (a) classify_conflict's same-candidate-different-identity VAULT_CLAIM detection and (b) the pre-resolution audit log's claim_history field. NOT used to extract candidate metadata (which comes from `git show :3:` text taken verbatim as the rebase-target's queue body per the bullet above).
- **`architecture/shippability.md`** append discipline (slice convention: each shipped slice adds one row keyed by slice number). PCR-1 implements a simple parser-and-append: parse both branches' shippability tables, take the row union keyed by slice number, sort by slice number ascending, write back. No external helper needed.
- **PSQ-3 sub-step 2.5 structure** at `skills/commit-slice/SKILL.md:176–190` (Conflict outcome path) — PCR-1 is strictly additive: inserts a new branch BEFORE the existing SOAD-1 STOP, leaving all other prose verbatim.
- **PSQ-2 `tools/slice_queue_claim.parse_queue_text` claim-field extension** at `tools/slice_queue_claim.py` — used by PCR-1 `classify_conflict` to detect `VAULT_CLAIM`-class conflicts (when both branches' slice-queue.md differ ONLY in `Claimed-by:` / `Claimed-at:` field lines on the same candidate).
- **`tools/state_transition_pin_audit.py`** — precedent for the "tool as resolver" pattern (audits-that-mutate-vault); PCR-1's `resolve_soft_conflict` follows the same mutation-with-log shape.
- **`tools/pipeline_chain_audit.py`** (referenced for PCA-1 regression guard) — per /critique m4 ACCEPTED-FIXED: this audit runs at /build-slice Step 6 pre-finish and confirms `/commit-slice`'s `auto-advance: false` declaration is preserved post-edit. PCR-1 strictly preserves PSQ-3's `auto-advance: false` contract; the audit gate catches any future regression.
- **`tools/install_audit.py`** + `INSTALL.md` two-site tool-count literal (per /critique M6 ACCEPTED-FIXED): INSTALL.md has the canonical "30 executable methodology tools" literal at **both** L22 and L166 — PCR-1's BC-PROJ-9 5-inventory bump updates BOTH to 31. Pinned by `test_install_md_tool_count_literal_is_at_31_at_both_sites_post_pcr_1`.
- **NAW-1 default-branch resolution helper** — NOT directly used by PCR-1 (PCR-1 operates on the rebase state, which already has the target branch resolved by PSQ-3). Documented for cross-spec parity.
- **MEPD-1 (a) rule path discipline** per ADR-040 / ADR-041 — PCR-1 mints a new RULE-ID + entry-pin + PMI-1 5-part atomic bump.

## Components touched

### tools/parallel_conflict_resolver.py (NEW)

- **Responsibility**: Detect, classify, and (for SOFT class) auto-resolve parallel-slice merge conflicts that surface at `/commit-slice --merge` Step 5b sub-step 2.5 `git rebase` time. Operates on the in-progress rebase state (U-prefixed entries in `git status --porcelain`); does NOT call `git rebase` itself (that's PSQ-3's responsibility).
- **Lives at**: `tools/parallel_conflict_resolver.py` (created by this slice).
- **Key interactions**:
  - Reads `git status --porcelain` to enumerate U-files (subprocess via `subprocess.run`).
  - Reads `git show :2:<file>` / `git show :3:<file>` (the two branches' versions of each U-file) to compare content.
  - Reads `architecture/slices/slice-*-*/mission-brief.md` + `architecture/slice-queue.md` to derive concerned-slice metadata.
  - Calls `tools.slice_queue_writer.write_slice_queue` (library API) for slice-queue.md regen.
  - Writes to `architecture/parallel-conflict-resolution-log.md` (append-only).
  - Calls `subprocess.run(['git', 'add', ...])` + `subprocess.run(['git', 'rebase', '--continue'])` from `resolve_soft_conflict` ONLY (never on UNKNOWN/HARD/MIXED).
- **Module-level constants** (per slice-070 / slice-071 module-constants pattern):
  - `_SOFT_FILE_SET: frozenset[str]` = `{"architecture/slice-queue.md", "architecture/shippability.md"}` — **2 canonical files, forward-slash-keyed** (per /critique B3 ACCEPTED-FIXED: `_index.md` dropped because `/archive` skill's regen is Haiku-LLM-dispatched per COST-1, not deterministic; per /critique B2 ACCEPTED-FIXED: methodology-changelog.md dropped per /design-slice clarifying answer "HARD because PMI-1 atomic-bump risk too high"). Pinned by `test_soft_file_set_is_two_canonical_files_forward_slash_keyed`.
  - `_AUDIT_LOG_PATH: Path` = `Path("architecture/parallel-conflict-resolution-log.md")`.
  - `_AUDIT_LOG_HEADER: str` (constant text; written on lazy-create first append).
- **Path normalization convention** (per /critique M1 ACCEPTED-FIXED Windows-backslash bug; APED-1 finding): `_SOFT_FILE_SET` is forward-slash-keyed. `ConflictDiagnostic.u_files` is typed `list[str]` (raw `git status --porcelain` output is forward-slash on all OSes per git docs). Membership checks: `path_str in _SOFT_FILE_SET` directly — NO `str(Path)` cast (which on Windows would produce backslashes and miss the frozenset). If a Path is constructed internally, normalize via `.as_posix()` before `_SOFT_FILE_SET` membership. JSON CLI output uses raw forward-slash strings throughout (NOT `str(Path)`) to ensure platform-stable shape. Pinned by `test_soft_file_set_membership_uses_forward_slash_keys_on_windows_paths`.
- **Public functions** (library API): `diagnose_conflict`, `classify_conflict`, `resolve_soft_conflict`. Private helpers (leading underscore): `_extract_u_files`, `_derive_concerned_slices`, `_extract_claim_diff`, `_regen_slice_queue`, `_overlay_claims_on_queue_text` (per /critique-review M-add-1 ACCEPTED-FIXED — surgical claim-line overlay on rebase-target queue text; avoids the phantom-parser scope of an earlier draft), `_merge_shippability`, `_append_audit_log`. (`_regen_index` removed per /critique B3 ACCEPTED-FIXED.)
- **Frozen dataclasses** (use `@dataclass(frozen=True, slots=True)`): `ConflictDiagnostic` (`u_files: list[str]` forward-slash strings + `concerned_slices: dict[str, list[ConcernedSlice]]` forward-slash keys + `claim_history: list[ClaimEntry]`), `ConcernedSlice`, `ClaimEntry`, `ResolutionResult`. `ConflictClass` is an `enum.Enum` with members `SOFT / VAULT_CLAIM / HARD / MIXED / UNKNOWN`. JSON output uses raw forward-slash strings; no `Path` objects in the serialization path.
- **CLI** (`main()`): mutually-exclusive flag group `--diagnose | --classify | --resolve-soft` (exactly one required); shared `--json` flag for machine-readable output; `--queue-path` + `--repo-root` for testability injection. Exit codes: 0 on success; 1 on classification error / unresolvable state; 2 on malformed inputs / unknown class (loud-malformed per APED-1).

### skills/commit-slice/SKILL.md (MODIFIED)

- **Responsibility**: Slice-commit + merge/push/sync skill; PSQ-3 lives at Step 5b sub-step 2.5; PCR-1 adds the soft-conflict-resolution branch BEFORE PSQ-3's SOAD-1 STOP.
- **Lives at**: `skills/commit-slice/SKILL.md` (modified by this slice).
- **Edit site**: Step 5b sub-step 2.5 "Conflict" outcome path (currently L183–186). New text inserts a paragraph between "**Conflict**: STOP." (L183) and "Then surface a SOAD-1 structured-options ask" (L183 mid-paragraph). The new paragraph reads (verbatim final wording TBD at /build-slice; this is the design intent):
  > Before STOP, invoke `python -m tools.parallel_conflict_resolver --resolve-soft --json`. If the resolver returns `action: APPLIED` (SOFT-class auto-resolution succeeded), the rebase has already been continued via `git rebase --continue`; log a single-line breadcrumb to the slice's build-log Events section (`PCR-1 soft-conflict resolved — see parallel-conflict-resolution-log.md`) and proceed to sub-step 3. If the resolver returns `action: STOP` (VAULT_CLAIM / HARD / MIXED / UNKNOWN), print the full-detail diagnostic from the resolver's `--diagnose --json` output (concerned slices + blast-radii + claim history + commit times + mission-brief links per U-file) AND fall through to the existing SOAD-1 3-option block below.
- **Forward-sync**: edit in-repo file then copy to `~/.claude/skills/commit-slice/SKILL.md`; verify CAD-1 via existing `tools.commit_slice_skill_drift_audit` (or OSDG-1-equivalent). Per CAD-1 from slice-006, in-repo is canonical; installed copy is the runtime working copy.

### architecture/parallel-conflict-resolution-log.md (NEW, lazy-created)

- **Responsibility**: Append-only audit trail of PCR-1 soft-conflict auto-resolutions.
- **Lives at**: `architecture/parallel-conflict-resolution-log.md` (created lazily on first `_append_audit_log` call by `tools.parallel_conflict_resolver`).
- **Header content** (written once on lazy-create): brief preamble explaining the file's purpose, audit semantics, and a pointer to ADR-069 + PCR-1.
- **Entry format** (per resolution event):
  ```markdown
  ## Soft-conflict resolution — <ISO-8601 UTC timestamp>

  **Repo HEAD SHA pre-resolution**: <40-char SHA>
  **U-files resolved**: <comma-separated relative paths>
  **Concerned slices**: <comma-separated slice IDs>
  **Resolution actions**:
  - `architecture/slice-queue.md` — regenerated via `slice_queue_writer.write_slice_queue` with union-of-branches candidate set (N candidates; M claims preserved)
  <!-- _index.md row REMOVED per /critique B3 ACCEPTED-FIXED — Haiku-LLM-dispatched regen is not deterministic; _index.md conflicts fall to HARD -->
  - `architecture/shippability.md` — row-union merge (N rows from branch A + M rows from branch B → K unique by slice number)
  ```

## Contracts added or changed

### `tools.parallel_conflict_resolver` CLI

- **Endpoint**: `python -m tools.parallel_conflict_resolver`
- **Defined in code at**: `tools/parallel_conflict_resolver.py` `main()` (to be created)
- **Flags**:
  - `--diagnose`: emit structured diagnostic of current rebase-conflict state (no mutation)
  - `--classify`: emit ConflictClass for current state (no mutation)
  - `--resolve-soft`: attempt SOFT-class auto-resolution; mutates on success (writes files + `git add` + `git rebase --continue` + append audit log)
  - `--json`: machine-readable output for all three modes
  - `--queue-path PATH`: override default `architecture/slice-queue.md` (testability)
  - `--repo-root PATH`: override default cwd (testability)
- **Auth model**: none — local-only tool, file-system + subprocess git access.
- **Error cases** (exit codes):
  - `0`: success (DIAGNOSE / CLASSIFY emitted; or RESOLVE-SOFT applied)
  - `1`: rebase not in progress (no U-files); soft-resolve called on non-SOFT class; classify cannot determine class (UNKNOWN)
  - `2`: malformed inputs (invalid `--queue-path`, missing `--repo-root`, etc.); APED-1 loud-malformed contract
- **Idempotency**: `--diagnose` + `--classify` are pure-read. `--resolve-soft` is idempotent against the same rebase state but NOT across runs (it mutates the rebase state).

### Internal: PSQ-3 sub-step 2.5 Conflict path adds PCR-1 invocation

- **Endpoint**: skill prose (not code) at `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 "Conflict" outcome
- **Defined in prose at**: `skills/commit-slice/SKILL.md` (modified by this slice)
- **Contract**: when PSQ-3 detects a rebase conflict (U-prefixed entries in `git status --porcelain`), call `python -m tools.parallel_conflict_resolver --resolve-soft --json` BEFORE printing the existing SOAD-1 block. Branch on resolver exit code + `action` field:
  - exit 0 + `action: APPLIED` → soft-resolved; log breadcrumb; proceed to sub-step 3
  - exit 0 + `action: STOP` → enhanced diagnostic printed; fall through to existing SOAD-1 3-option ask
  - exit 1 → unresolvable (UNKNOWN class or unexpected git state); fall through to SOAD-1 with the resolver's stderr diagnostic
  - exit 2 → malformed inputs (audit error); fall through to SOAD-1 with the malformed diagnostic

## Data model deltas

None — PCR-1 is methodology-prose + new tool module + new audit-log file. No DB schema, no new entity, no migration.

## Wiring matrix

Per WIRE-1 (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/parallel_conflict_resolver.py` | `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 (prose-level invocation via `python -m`) + direct CLI invocation by future automation/Claude sessions | `tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py::test_resolve_soft_conflict_dispatches_to_slice_queue_writer_for_slice_queue_conflict` + `tests/methodology/test_commit_slice_skill_pcr_1_diagnostic.py::test_step_5b_substep_2_5_emits_full_concerned_slice_diagnostic` | — |
| `architecture/parallel-conflict-resolution-log.md` (lazy-created) | `tools/parallel_conflict_resolver.py::_append_audit_log` | `tests/skills/parallel_conflict_resolver/test_audit_log.py::test_soft_conflict_resolution_appends_to_parallel_conflict_resolution_log` | — |
| `architecture/decisions/ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen.md` | `methodology-changelog.md` § v0.73.0 + `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 cross-reference + `architecture/shippability.md` row for slice-076 | `tests/methodology/test_pcr_1_adr_present.py::test_adr_069_parallel_conflict_resolution_mechanism_exists` | — |

## Decisions made (ADRs)

- [[ADR-069-mint-pcr-1-conflict-diagnostic-and-soft-regen]] — mint PCR-1 (parallel-conflict-resolution v1) on a new family axis; 5-class taxonomy (SOFT / VAULT_CLAIM / HARD / MIXED / UNKNOWN) defined inline; SOFT class auto-regenerated for `{slice-queue.md, shippability.md}` — 2 canonical files per /critique B3 ACCEPTED-FIXED (`_index.md` dropped: `/archive` Haiku-LLM-dispatched, non-deterministic) and per /design-slice clarifying answer (methodology-changelog.md dropped: PMI-1 atomic-bump risk); VAULT_CLAIM + HARD + MIXED + UNKNOWN deferred to PCR-2 (slice-077) for resolution paths, all fail-closed to existing PSQ-3 SOAD-1 STOP in PCR-1 v1 — reversibility: **expensive** (once parallel sessions rely on soft-regen path, reverting requires either re-introducing manual STOPs on every state-file conflict OR finding an alternative auto-resolve; the soft-regen log becomes load-bearing audit trail at first append).

## Resolution algorithm for SOFT class (2-file detail)

| File | Resolution | Edge cases |
|---|---|---|
| `architecture/slice-queue.md` | (1) `git show :2:architecture/slice-queue.md` + `git show :3:architecture/slice-queue.md` → both branches' queue text (rebase-target stage `:3:` will be used **verbatim** as the result-baseline — no re-emission via `write_slice_queue`). (2) `tools.slice_queue_claim.parse_queue_text(text_2)` + `parse_queue_text(text_3)` → 2 claim dicts (claim metadata only). (3) **VAULT_CLAIM gate** (per /critique B4 ACCEPTED-FIXED): walk the keys of both claim dicts; if ANY candidate name appears in BOTH with DIFFERENT `Claimed-by:` values, abort with `action: STOP, conflict_class: VAULT_CLAIM` (do NOT auto-resolve — PSQ-2's existing newest-wins merge would silently auto-resolve what PCR-2 reserves for timestamp-winner + light-Critic; defense-in-depth defeats this here). (4) Otherwise compute `merged_claims = newest-Claimed-at-wins union of claims_2 + claims_3` (in-helper merge, NOT a `write_slice_queue` round-trip). (5) Call new private helper `_overlay_claims_on_queue_text(text_3, merged_claims) -> str` per /critique-review M-add-1 ACCEPTED-FIXED option (2) — surgically updates `**Claimed-by:**` + `**Claimed-at:**` lines under each candidate's `**Risk-retired:**` line in `text_3`; candidates in `merged_claims` whose names are not present in `text_3` are dropped (will re-surface at next `/slice` regen — documented behavior, not a bug). NO `write_slice_queue` dispatch (avoids the B1 phantom-parser trap; no candidate parser mint scope). (6) Write the overlay result + `git add` + audit-log entry. | (a) `git show :3:` exits non-zero (file added on rebased branch only): treat empty-target; resolved queue uses `text_2` verbatim with claims merged. (b) `git show :2:` exits non-zero (file added on rebase-target only): symmetric. (c) Both stages missing: UNKNOWN class (defense-in-depth — shouldn't happen in legitimate conflict state). |
| `architecture/shippability.md` | (1) `git show :2:architecture/shippability.md` + `:3:` → both versions. (2) Parse header + rows; key rows by leading `\| <NN> \|` slice number. (3) Union by slice number; if same slice number on both sides with different content, treat as HARD-class collision (defense-in-depth — each slice owns one row; collision implies a slice number collision elsewhere, escalate). (4) Sort by slice number ascending; write with header preserved. (5) `git add` + audit-log entry. | (a) `git show` non-zero on one stage: treat as empty-rows; resolved file contains only the other stage's rows. (b) Same-slice-number with different content: STOP with HARD diagnostic — escalate to PCR-2's source-file Critic path even though shippability is in SOFT-set. |

**`architecture/slices/_index.md` is NOT in SOFT.** The `/archive` skill's regen is **Haiku-LLM-dispatched** per COST-1 (synthesizes the "Aggregated lessons" prose block from N archived reflections — not a deterministic scan). PCR-1 cannot reproduce Haiku's output; any conflict in `_index.md` falls to HARD-class and surfaces via PSQ-3's existing SOAD-1 STOP. The user re-runs `/archive` manually post-merge to regenerate the lessons-block; PCR-2 may revisit if a deterministic algorithm emerges.

**`methodology-changelog.md` is NOT in SOFT.** Per /design-slice clarifying answer 1: PMI-1 5-leg atomic bump means two parallel slices both bumping to v0.73.0 could produce subtly inconsistent merged entries (different RULE-IDs, paired-pin test names, ADR refs). Auto-merging changelog risks silent BC-PROJ-10 violations. Stays HARD; PCR-2's Critic stack reviews the proposed resolution.

## Authorization model for this slice

None — PCR-1 is a local-only methodology tool. No network, no external API, no user-data access. Runs against the developer's own repo working tree as part of `/commit-slice --merge`. Adversarial model per ADR-067 § Adversarial model carries forward: cooperative coordination, not a security boundary. A malicious local actor with filesystem write to the rebase state can bypass any methodology rule by editing files directly.

## Error model for this slice

- **`resolve_soft_conflict` UNKNOWN class**: fail-closed STOP per APED-1 silent-disable / default-off-on-malformed criterion. Resolver exit 1 with stderr `parallel-conflict-resolver: classify_conflict returned UNKNOWN — refusing to resolve; rebase state may be unexpected. Inspect via 'git status' and resolve manually.` Skill falls through to existing SOAD-1 STOP block.
- **`resolve_soft_conflict` HARD / VAULT_CLAIM / MIXED class**: resolver exits 0 with `action: STOP` + diagnostic; skill falls through to enhanced SOAD-1 block. NOT an error in the skill's eyes — the resolver did its job (classified as non-SOFT); the existing PSQ-3 path takes over.
- **`resolve_soft_conflict` `slice_queue_writer.write_slice_queue` import failure** (bootstrap defense): resolver wraps the import in try/except per PSQ-1 ADR-064 § Consequences pattern; on ImportError, exit 1 with stderr `parallel-conflict-resolver: slice_queue_writer not importable — SOFT-class resolution unavailable; falling through to SOAD-1 STOP.`
- **`resolve_soft_conflict` `git rebase --continue` failure post-stage** (rebase state inconsistent despite the soft-files being staged): resolver exits 1 with stderr `parallel-conflict-resolver: git rebase --continue failed post soft-resolution — rebase state may have additional conflicts beyond the SOFT set. Inspect via 'git status' and resolve manually.` This shouldn't happen if `classify_conflict` correctly identified SOFT (no other U-files); the STOP is a defense-in-depth case.
- **Audit-log write failure** (e.g., disk full, permissions): resolver logs to stderr but does NOT block the resolution (the rebase has already been continued; the audit-log is best-effort breadcrumb, not a precondition). This is the one exception to the fail-closed pattern — auditability is desirable but not load-bearing.
- **Non-SOFT class with diagnostic-output failure** (e.g., mission-brief.md unreadable for an active slice): degrade gracefully — emit a partial diagnostic with a `WARN: <slice-id> mission-brief unreadable, blast-radius omitted` note. Never silent-default-off (APED-1).

## Forward references (deferred to PCR-2 / slice-077)

- **VAULT_CLAIM resolution**: when both branches' slice-queue.md differ ONLY in `Claimed-by:` / `Claimed-at:` field lines on the same candidate. PCR-1 detects this class but stops; PCR-2 will add timestamp-winner resolution + light Critic check.
- **HARD-conflict Critic stack**: when any source-code file is in U-entries. PCR-1 emits the enhanced diagnostic; PCR-2 will spawn `/critique` + `/critique-review` agents on the proposed resolution + TRI-RESOLVE-1 user triage.
- **MIXED conflicts** (SOFT + HARD coexist): PCR-1 currently treats as a sub-case of HARD (do not auto-resolve the SOFT portion if any HARD U-file is present — atomicity). PCR-2 may revisit if partial-resolution becomes desirable.
