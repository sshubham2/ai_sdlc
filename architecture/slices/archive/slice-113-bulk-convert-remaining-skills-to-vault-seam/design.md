# Design: Slice 113 bulk-convert-remaining-skills-to-vault-seam

**Date**: 2026-06-04
**Mode**: Standard
**Governance**: ADR-only / **MEPD-1 EXCLUDE** (no RULE-ID / no VERSION bump / no `methodology-changelog` entry) — applies [[decisions/ADR-105]]'s convention + extends [[decisions/ADR-104]]'s op-gate; matches the flip-prep house style (slices 106/109/111/112). Enforcement stays suite-test + shippability-pinned, not a new build-slice gate.

## What's new

- **Bulk `<vault>/` conversion** of the *convertible* operational `architecture/…` literals across the 25 skill `SKILL.md` files — the **shared-aggregate vault-file refs only** (risk-register, concept, triage, lessons-learned, shippability, build-checks, `slices/_index.md`, `slices/archive/…`, `slices/action-points.md`, `decisions/ADR-*.md`, `spikes/…`, `*-log.md`, `components/…`, `contracts/…`, `user-tests/…`). Carve-out classes 3–7 stay concrete.
- **Op-gate seam-awareness** ([[decisions/ADR-106]]): a new `_OP_SINK_RE` / `_OP_SINK_TOKEN_RE` in `tools/vault_flip_prose_inventory.py` that matches `<vault>/` **in addition to** `architecture|diagnose-out/`, used by `scan_op_file` — so a converted in-loop write-op stays **visible** to the op-gate. (The user-ratified design fork — preserves protection instead of the brief's anticipated downward floor re-pin.)
- **Move-together re-pin** of the inventory constants + `_OP_ALLOWLIST` hashes + shippability count rows + the tool docstring narrative.
- **`_CONVERTED_FILES`** grown to every converted skill file; **`_CONVERTED_CARVEOUTS`** grown with each converted file's residual carve-out literals (classes 4/5/6/7), hash-keyed.
- **OSDG-1 / mini-CAD forward-sync** of every converted guarded `SKILL.md` to its installed `~/.claude/` copy.

## What's reused

- [[decisions/ADR-105]] — the `<vault>` convention + the 7-class carve-out taxonomy + the ratchet machinery (`_CONVERTED_FILES` / `_CONVERTED_CARVEOUTS` / `converted_file_regressions`). **This slice APPLIES the taxonomy; it does not redefine a class.**
- [[decisions/ADR-104]] / [[decisions/ADR-102]] — the op-gate (`scan_op_file` / `_classify_op` / `_OP_ALLOWLIST` / `_OP_CLASS_FLOOR`); ADR-106 extends its sink vocabulary.
- `tools/vault_flip_prose_inventory.py` — the inventory + op-gate (modified — the only code file this slice touches).
- The `<vault>` resolution rule in `CLAUDE.md` (slice-112) — the resolver the converted skill prose relies on. Per ADR-105 **resolver-context scope**, skill `SKILL.md` is read by the **main agent**, which carries the project `CLAUDE.md` ⇒ the convention resolves ✓ (no per-skill embedded note needed — unlike `agents/*.md`).
- `tools/critique_agent_drift_audit.py` + the `*_skill_drift` suite — the forward-sync content-equality precedent (CAD-1 / mini-CAD / OSDG-1).

## Components touched

### `tools/vault_flip_prose_inventory.py` (modified)
- **Responsibility**: the prose-surface vault-location-literal inventory + the in-loop write-op gate. Both halves share the region-anchoring (`_in_inline_code` + fence tracking) + file walk.
- **Changes**:
  1. **Op-gate seam-awareness ([[decisions/ADR-106]])** — introduce a *distinct* sink matcher for the op-gate:
     - `_OP_SINK_RE = re.compile(r"(?:architecture|diagnose-out)/|<vault>/")`
     - `_OP_SINK_TOKEN_RE` — the token form capturing a full `<vault>/…` OR `(?:architecture|diagnose-out)/…` path.
     - `scan_op_file` uses `_OP_SINK_RE` / `_OP_SINK_TOKEN_RE` **instead of** the inventory's `_MATCH_RE` / `_PATH_TOKEN_RE`. The inventory's `_MATCH_RE` is **UNCHANGED** — converted `<vault>/` literals MUST still drop from the inventory baseline + ratchet (else the converted literal re-appears as an occurrence and the baseline/`EXPECTED_TOTAL` never settle). The two regexes are now **deliberately distinct** — a documented divergence from the slice-111 "same `_MATCH_RE`" reuse (CSP-1: still NOT a third classifier; only the sink-vocabulary widens for the op-gate's forward-looking protection).
     - **The value EXTRACTOR is co-load-bearing, NOT cosmetic (B2 — the AP-4 catch).** `_classify_op` keys on the op's extracted SINK VALUE, not the line (`_ACTIVE_FOLDER_RE.search(sink)` `:543`, `_UNDECIDED_DISPOSITION_RE.search(sink)` `:547`). `scan_op_file` extracts that value at `:592` — TODAY via `_PATH_TOKEN_RE.match(line, col)`, which returns `None` at a `<vault>/` column → the value silently falls back to the bare `m.group(0)` = `"<vault>/"` (path tail LOST) → `_ACTIVE_FOLDER_RE.search("<vault>/")` is False. **So `_OP_SINK_TOKEN_RE` MUST replace `_PATH_TOKEN_RE` as the extractor in lockstep with `_OP_SINK_RE` as the matcher** — the matcher widening alone is vacuous; the extractor is what makes the prefix-agnostic sub-regex claim true. (In THIS slice's corpus the active-folder/slice-queue sinks stay concrete carve-outs, so a miss fails CLOSED — over-flags OP_UNROUTED — but ADR-106's forward-protection claim is FALSE without the extractor upgrade.)
     - The `_classify_op` sub-regexes (`_ACTIVE_FOLDER_RE`, `_ARCHIVE_DEST_RE`, `_UNDECIDED_DISPOSITION_RE`, `_SEAM_TOKEN_RE`) are **prefix-agnostic** (they match path *suffixes* / seam tokens) → they classify a `<vault>/…` sink identically to an `architecture/…` sink **once the value is extracted in full** (per the bullet above). No change to the sub-regexes themselves.
     - **Non-vacuity (B2 / AP-5)**: `test_vault_flip_op_gate.py` has ZERO `<vault>/`-sink fixtures today, so a value-extractor miss passes the whole op-gate suite vacuously. Add three `<vault>/`-sink op-gate tests proving the seam-aware path classifies correctly: a `<vault>/slices/slice-NNN/…` in-loop write → `OP_DEFERRED_TO_FLIP`; a `<vault>/slice-queue.md` write → `OP_OUT_OF_SCOPE`; an un-routed in-loop `<vault>/risk-register.md` write → `OP_UNROUTED` (the gate still bites — this is the proof ADR-106's forward-protection is real). Build asserts the per-class breakdown stays `{6,11,23,0}`, not merely exit 0.
  2. **Move-together inventory re-pin** (APED-1, derived via `--json` AFTER the conversion + carve-out settle — never estimated): `EXPECTED_TOTAL`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `_BASELINE_SHA256`.
  3. **`_CONVERTED_FILES`** — grow to include every converted skill file (forward-slash repo-relative paths — the M3 invariant; a `\`-form member silently never matches → vacuous-green, pinned against by the existing test).
  4. **`_CONVERTED_CARVEOUTS`** — grow with each converted file's residual carve-out literals (classes 1-pathspec/4/5/6/7), hash-keyed `(path, sha256(value))`. Required so a file carrying a concrete carve-out can still join `_CONVERTED_FILES` without tripping `converted_file_regressions`. **Keying-collision caveat (M3)**: `_MATCH_RE` is boundary-free, so a class-4 `<wt_path>/architecture/X` extracts `value = architecture/X` (prefix stripped) → its `(path, sha256(value))` carve-out key is identical to a bare convertible `architecture/X` of the same suffix in the same file → one carve-out entry would whitelist both, so a future bare regression of that value is NOT caught (`converted_file_regressions` `:362-373` is value-only). **Build-time discrimination**: after the carve-out set settles, check whether any *convertible* literal shares a `(path, value)` with a class-1/4/5 carve-out in the same `_CONVERTED_FILES` member — **if a real collision exists → strengthen THAT file's carve-out keying to the disposition 5-tuple** `(path, norm_line, fenced, ordinal, col)` (so the ratchet stays strong); **if none → document the same-value-collision limitation** and add a **differing-value** ratchet mutation test on `skills/slice/SKILL.md` (inject a non-carved bare `architecture/…` → ratchet still exit 2 — the AP-5 non-vacuity proof for the canonical case the must-not-defer names). This is an **ACCEPTED-PENDING build-time decision** (M3, TRI-1).
  5. **`_OP_ALLOWLIST` re-hash** — re-hash the entries whose normalized line text changes under conversion: **3 confirmed** — `build-slice:407` (risk-register), `commit-slice:216` (parallel-conflict-log), `design-slice:240` (components/contracts) — **plus `slice:264` verified at build (M4)**. slice:264 carries TWO literals (`<wt_path>/architecture/slices/…` class-4 + a main-tree-fallback `architecture/slices/…` class-5); BOTH are carve-outs (stay concrete) so the line is *expected* unchanged ⇒ hash unchanged — but that is a CONTINGENT claim: confirm by post-conversion `--op-gate --json` that slice:264 still classifies allowlisted-`OP_DEFERRED_TO_FLIP` with an identical hash (AP-2 — the Builder's own pre-declared outcome is a fresh claim, verify by execution). If either literal converts, slice:264 becomes a **4th** re-hash. `_OP_CLASS_FLOOR` `{OP_UNROUTED:0, OP_DEFERRED_TO_FLIP:11, OP_OUT_OF_SCOPE:23}` **stays** — the seam-aware op-gate keeps all 40 ops visible, so **no downward floor re-pin** (the protection-preserving outcome of the Approach-A decision).
  6. **`_RESIDUAL`** — re-verify the bare-no-slash `architecture` dir-arg entries (conversion is in-place token replacement, same line count ⇒ line numbers are expected stable; confirm at build — closes the slice-112 `m2` bare-arg line-pin deferral).
  7. **Docstring narrative** — re-pin the count narrative (`301 rewrite-at-flip / 2 doc-example` → the new totals) in the module docstring + the `EXPECTED_TOTAL` / `_CLASS_COUNT_FLOOR` provenance comments. This is the **AP-10 / FBCD-1(c) build-time-docstring fan-out** the slice-111 + slice-112 (N=2) lessons flagged — a design-Critic can't see a build-authored docstring; `/code-review` (reads the code) is the catch.
- **Lives at**: `tools/vault_flip_prose_inventory.py`.
- **Key interactions**: consumed by `tests/methodology/test_vault_flip_prose_inventory.py` + `test_vault_flip_op_gate.py`; wired into `/build-slice` Step 6 + `/validate-slice` (both `--strict` and `--op-gate --strict`).

### `skills/<name>/SKILL.md` × 25 (modified — prose conversion)
- **Responsibility**: the operational pipeline prose. Convert the convertible shared-aggregate `architecture/…` refs → `<vault>/…`; leave carve-out classes 3–7 concrete.
- **Per-literal convertible-vs-carve-out discriminator** (the Builder's classification rule — applied to each of the ~287 matched literals):

  | If the matched literal is… | Class | Action |
  |---|---|---|
  | a **git-pathspec** literal (`:(exclude)architecture/…`, `:(glob,exclude)architecture/*.md`, `:(top)…`) | 1 (command-literal) | **concrete** (M-add-2, TRI-1-ratified) — consumed by **git, not the `<vault>` resolver**; converting risks a silent-wrong exclusion set if Claude doesn't substitute inside the pathspec. Stays concrete → flip-residual (rewritten at the physical move). Heavy in `skills/code-review/SKILL.md`. |
  | `<wt_path>/architecture/…` (worktree-composed) | 4 | **concrete** (structural prefix-drop at flip) |
  | `architecture/slices/slice-(NNN\|\d+)-…` active-folder (NOT `archive/`, NOT `_index.md`/`action-points.md`) | 5 | **concrete** (R-32.a — flip slice owns it) |
  | `architecture/slice-queue.md` | 6 | **concrete** (M1 — undecided ledger disposition) |
  | `diagnose-out/…` | 7 | **concrete** (B5 — no `<diagnose-out>` seam) |
  | a genuine historical-anchor / glob-discoverability / changelog line | 3 | **concrete** (rare on `architecture/`-prefixed paths) |
  | a definitional `architecture/` default quoted *as* the resolution default | 2 | **concrete** plain-prose (skills don't define the rule — expected ≈0) |
  | a **CLI command-argument** vault path in a Claude-executed fenced command (`$PY -m tools.X architecture/Y`, a `git add architecture/…` *path* arg — NOT a pathspec) | — | **convert → `<vault>/…`** (B1, TRI-1-ratified) — Claude substitutes `<vault>` at run (the ADR-105 option-1 LLM-resolution tax); **loud-fail** safety net if it forgets (file-not-found, not silent-wrong). **Repoint any test asserting the literal command string in the SAME slice** (AP-13). |
  | **anything else** `architecture/…` (shared-aggregate vault file) | — | **convert → `<vault>/…`** |

  The discriminator is **path-shape-based** and the Builder applies it literal-by-literal off the `--json` occurrence list; the inventory does NOT auto-classify carve-out *class* (it only has rewrite-at-flip / doc-example / historical-anchor / needs-human) — the carve-out decision is the Builder's, pinned afterward by `_CONVERTED_CARVEOUTS`. The **git-pathspec ↔ command-arg distinction is load-bearing** (M-add-2): both are command literals, but a pathspec is git-consumed (silent-wrong on non-substitution → carve out) while a plain path arg is a Claude-constructed reference (loud-fail → convert).

  **Enumerate the by-name consumer set by execution, not memory (B1/M2/M-add-2 — AP-13).** Before finishing, run a grep for every test that reads a *converted* SKILL.md AND asserts a literal `architecture/…` substring — the known seeds are `tests/methodology/test_validate_slice_skill.py:65` (shippability command-arg → converts → repoint), `tests/methodology/test_build_slice_skill_dirty_tree_resolution.py:204,207` (class-5/6 carve-out **guard** → stays green by correct carve-out), `tests/skills/code_review/test_code_review_skill.py:241-275` (10 git-pathspec literal asserts + catch-all-absent → stay green by pathspec carve-out), `tests/methodology/test_vault_flip_prose_inventory.py:72-73` (code-review:103 5-match pin → stays green by pathspec carve-out). The grep is the closed set; this list is the seed.
- **Lives at**: the 25 `skills/<name>/SKILL.md`.
- **Key interactions**: read by the main agent (resolver in context ✓); the guarded subset forward-synced.

### `~/.claude/skills/<name>/SKILL.md` (forward-sync — the on-disk **13** OSDG-1/mini-CAD-guarded; M-add-1, TRI-1-ratified)
- **Responsibility**: the installed copies pinned content-equal (modulo EOL, ADR-033) by the `tests/methodology/*_skill_drift.py` tests.
- **Guarded set — computed at build from `ls tests/methodology/*_skill_drift.py`, NOT a prose roster** (the design's original 12-member list was WRONG — it listed `diagnose`, which has **no** `test_diagnose_skill_drift.py`, and OMITTED `code-review` + `pulse`, which BOTH have one; disk-confirmed). The authoritative 13: `adopt`, `build-slice`, **`code-review`** (47 convertible literals), `commit-slice`, `critique`, `critique-review`, `design-slice`, **`pulse`** (16 convertible literals), `query-design`, `reflect`, `slice`, `slice-candidates`, `triage`. Each converted guarded `SKILL.md` is force-synced to `~/.claude/skills/<name>/SKILL.md` (byte-converted identically — deterministic find-replace, EOL-agnostic equality stays green). **`test_code_review_skill_drift.py` + `test_pulse_skill_drift.py` assert whole-file equality (`assert_md_forward_synced`) — converting either without syncing REDS the suite at finish (the finish-gate Blocker M-add-1 closes).**
- **Note**: `diagnose` (8 convertible literals) + the unguarded skills (`archive`, `discover`, `risk-spike`, `reduce`, `sync`, `user-test`, `supersede-slice`, `heavy-architect`, `critic-calibrate`, `drift-check`) have **no** `*_skill_drift.py` — converting them is safe (no installed-copy pin to red) per slice-096 (OSDG-1 is not total-skill coverage). Force-sync them too as courtesy hygiene (keeps installed copies current) but it is not test-gated. The project `CLAUDE.md` OSDG-1 roster prose is itself stale on this point (it lists `diagnose` as drift-guarded + flags pulse/code-review as "not yet enumerated") — a courtesy-parity cleanup, out of this slice's scope; this slice trusts the on-disk test set, not the prose.

## Contracts added or changed

No API / endpoint / event / schema contracts. Two internal-contract changes, both additive & backward-compatible:
- **Op-gate sink vocabulary** now includes the `<vault>/` seam ([[decisions/ADR-106]]). The op-gate JSON shape + exit codes are unchanged.
- **`_CONVERTED_FILES` / `_CONVERTED_CARVEOUTS`** on-disk sets grow (the slice-112 contract, extended additively — same shape).

## Data model deltas

None (no DB / schema).

## Wiring matrix

This slice introduces **no new module** — it modifies one existing tool (`vault_flip_prose_inventory.py`) + prose. The op-gate seam-awareness is a change to an **already-wired** consumer (`scan_op_file` → `_run_op_gate` → the op-gate tests + `/build-slice` Step 6 + `/validate-slice`). Zero-row matrix (clean per WIRE-1).

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|

## Decisions made (ADRs)

- [[decisions/ADR-106]] — the op-gate sink-detector becomes **seam-aware** (matches `<vault>/` in addition to `architecture|diagnose-out/`), so the bulk prose conversion does not blind the in-loop write-op gate — reversibility: **cheap**.

## Authorization model for this slice

N/A — no auth surface. Cooperative-model methodology tooling (per ADR-029 / ADR-087: a static prose audit cannot enforce runtime obedience; out of scope, documented residual).

## Error model for this slice

Inventory/op-gate exit codes unchanged: `0` clean · `2` gate (needs-human / baseline-drift / count-floor-shrink / converted-file-regression / OP_UNROUTED) · `1` usage. The seam-aware op-gate adds no new exit path. Post-re-pin, `--strict` and `--op-gate --strict` both exit `0` on the converted corpus; the ratchet (`converted_file_regressions`) exits `2` if any of the now-25-converted files regresses to a hardcoded operational `architecture/` — the protection this slice extends from 2 files to 27.

## Build-time / APED-1 plan (the AP-3 discipline — execute against the real corpus, don't reason)

0. **Enumerate consumers by execution (B1/M2/M-add-2)**: `grep -rn "architecture/" tests/` filtered to assertions reading a *converted* SKILL.md → the closed by-name-literal-consumer set (seeds: `test_validate_slice_skill.py:65`, `test_build_slice_skill_dirty_tree_resolution.py:204,207`, `test_code_review_skill.py:241-275`, `test_vault_flip_prose_inventory.py:72-73`). Also `ls tests/methodology/*_skill_drift.py` → the authoritative **13** forward-sync roster (M-add-1).
1. Dump `--json`; for each skill literal apply the discriminator table (incl. the new **git-pathspec → carve-out** + **command-arg → convert** rows) → the convertible set + the per-file carve-out set.
2. Convert the convertible literals in the 25 `SKILL.md` (in the worktree); **git-pathspecs stay concrete** (M-add-2 → `test_code_review_skill.py` + the 5-match pin stay green untouched); **command-arg paths convert** + repoint `test_validate_slice_skill.py:65` (B1).
3. Op-gate seam change (ADR-106): add `_OP_SINK_RE` **AND** the `_OP_SINK_TOKEN_RE` **extractor** (B2 — both in lockstep, the extractor governs `_classify_op`); re-hash the 3 confirmed `_OP_ALLOWLIST` entries + **verify slice:264 hash via `--op-gate --json`** (M4); add the **3 `<vault>/`-sink op-gate tests** (B2/AP-5: DEFERRED active-folder / OUT_OF_SCOPE slice-queue / UNROUTED bite).
4. Re-run `--json`; derive the exact new `EXPECTED_TOTAL` / `REWRITE_AT_FLIP` floor / `_BASELINE_SHA256`; populate `_CONVERTED_FILES` + `_CONVERTED_CARVEOUTS`; **run the M3 collision check** (strengthen a colliding file's keying to the 5-tuple, else document + differing-value mutation test); fix the docstring narrative (AP-10).
5. Force-sync the **13** guarded `SKILL.md` to `~/.claude/` (drop `diagnose`, add `code-review` + `pulse`); courtesy-sync the rest.
6. Re-pin shippability count rows (113/117/118 — exact rows APED-1-confirmed) to the new total; verify BCR-1 (`test_bcr_1_backlog_round_trip.py`) green **untouched** (diagnose-out carve-out keeps its `diagnose-out/backlog.md` literal intact — no repoint needed).
7. **Gate**: `--strict` 0 · `--op-gate --strict` 0 **AND per-class breakdown `{6,11,23,0}`** (not just exit 0, B2) · the converted-file ratchet mutation (inject + re-pin baseline → still exit 2) · the M3 differing-value ratchet mutation on `slice/SKILL.md` · `pytest tests/methodology -k skill_drift` green (all 13) · the enumerated by-name consumer tests green · full suite green.

## Risks / sensitivities

- **The seam-aware op-gate must not leak into the inventory baseline** — keep `_OP_SINK_RE` separate from `_MATCH_RE` (a code-Critic / AP-4 focus: a new/changed classifier verb-set against the real corpus + the actual call graph).
- **Carve-out under-classification** (a shared-aggregate ref wrongly carved out, or an active-folder ref wrongly converted — the M1-class pre-deciding-an-undecided-disposition drift) → the discriminator table is the contract; spot-verify class-5/6/7 sinks stay concrete in `--json`.
- **Forward-sync atomicity** (R-28 / AP-22) — a parallel version-bumping sibling could flip a drift test; sequence the sync, expect a user-approved deferral if contended. (No parallel slice is active — single-slice per the /slice gate.)
