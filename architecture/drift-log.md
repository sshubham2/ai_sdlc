# Drift Log

Append-only audit trail of `/drift-check` runs. Each entry records vault-vs-code divergence findings + resolutions.

## Audit 2026-05-31 (slice-092-fix-stranded-audit-branchless-blindspot)

**Trigger**: slice-092 pre-finish gate (/build-slice Step 6)
**Scope**: full (active slice-092 design.md/mission-brief + ADR-084 + risk-register R-31 + shippability row 99 vs `tools/stranded_slice_audit.py` + `tests/methodology/test_stranded_slice_audit.py` + `skills/{pulse,slice}/SKILL.md`)
**Result**: CLEAN — no drift.

### Blockers
(none)

### Majors
(none)

### Verified aligned
- `design.md` "What's new" all present in code: `DivergenceClass.BRANCHLESS_IN_FLIGHT = "branchless-in-flight"` exists and is **NOT** in `_HALT_CLASSES` (informational, `halt=False`); the new private `_branchless_in_flight_slices(repo_root, seen_keys)` pass enumerates non-`archive` `architecture/slices/slice-NNN-<name>/` folders, deduped against the union of worktree'd + bare `slice/*` ref keys; `classify_branches` assembles `seen_keys = {b[len("slice/"):] for b in worktree_branches} | {f"{num}-{name}" for (_b,num,name) in bare_tuples}` and calls the new pass after the worktree + bare passes. Verified by `tests/methodology/test_stranded_slice_audit.py` 4j–4o + repro (16 passed).
- **Benign naming note (NOT drift)**: the design prose refers to the dedup input as "the full `slice/*` ref set"; the implemented helper parameter is named `seen_keys`. Same semantics (the union of worktree'd + bare ref keys), internal name only — no contract/behavioral divergence.
- Contract matches: JSON `klass` gains `"branchless-in-flight"` (backward-additive); the entry carries `branch` = folder-form id `slice-NNN-name` (hyphen), `worktree_path=None`, `ahead=None`, `vault_state="folder:<stage>"`, `halt=False`; `compute_status` unchanged (BRANCHLESS_IN_FLIGHT ∉ `_HALT_CLASSES` → a branchless-only repo stays `clean`).
- Error model matches: absent/unparseable milestone → skip; **stage-less-but-parseable → skip (never `folder:None`, m-add-2)**; terminal (`_is_terminal`) folder → skip; missing `architecture/slices/` dir → zero folders (no raise). Pinned by 4l/4m/4o.
- B1 self-surfacing disambiguation + B2 worktree-key dedup match design §Self-surfacing / §Dedup design; non-vacuous 4n verified by mutation-testing the worktree-key derivation (FAIL `2==1` under the bare-name mis-key, PASS after revert).
- M1: `skills/pulse/SKILL.md` (load-bearing render path) + `skills/slice/SKILL.md` (doc-only enumeration) add `branchless-in-flight` as a parallel-normal informational klass; both forward-synced to `~/.claude/` (OSDG-1 `test_pulse_skill_drift.py` / `test_slice_skill_drift.py` green); `test_pulse_skill_stranded_signal.py` pins the new klass name.
- `ADR-084` (`status: accepted`, `reversibility: cheap`, `supersedes: null`) matches design + the implemented enum/pass/dedup/subordination decision; MEPD-1 EXCLUDE (no new RULE-ID, no `methodology-changelog.md` entry, no VERSION bump) — PMI-1/MCFS-1/AVFS-1/TVFS-1 all PASS, unaffected.
- `risk-register.md` R-31 → `mitigating` with an ADR-084 mitigation note + residuals (a) different-worktree folder not cross-scanned, (b) archived-but-never-branched folder; no live test pins R-31 status (STP-1 green).
- `shippability.md` row 99 (added by `/repro`) cites `tests/bugs/test_stranded_audit_branchless_slice_blindspot.py` (exists + passes) and pins the full post-fix contract (informational, dedup, terminal-skip); regression directions enumerated. No new audit RULE-ID → no RPCD-1/SCPD-1 fan-out beyond the existing tool's inventory rows.
- No removed feature; no UNSPECIFIED CODE; no STALE CLAIM in the slice-092 surface.

### Resolutions
- None required — vault and code aligned for the slice-092 surface.

## Audit 2026-05-31 (slice-093-add-external-vault-support)

**Trigger**: slice-093 pre-finish gate (/build-slice Step 6)
**Scope**: full (slice-093 mission-brief/design.md/ADR-085/risk-register R-32 vs `tools/_vault_paths.py` [3-tier resolution] + `tools/_vault_write.py` [C2 safe_write/append] + `INSTALL.md` Step 3i + `tests/methodology/{test_vault_safe_write,test_install_vault_config,test_external_vault_adr_and_risk,test_vault_root_constant}.py`)
**Result**: CLEAN — vault and code aligned; no drift.

### Blockers
(none)

### Majors
(none)

### Verified aligned
- design.md "What's new" all present in code: `_vault_paths.py` `_CONFIG_REL` + `_read_common_dir_config` (stdlib subprocess, defensive R-7) + `_resolve_vault_root` (env → git-common-dir config → `Path("architecture")` default); `_vault_write.py` `safe_write_text` (SIDECAR `.lock`, atomic `os.replace`, bounded EPERM-retry) + `safe_append_text` (O_APPEND) + `write/read_vault_root_config` importing the shared `_CONFIG_REL` (m2 SSoT). Full suite 1314 PASS.
- **No-flip invariant HOLDS**: resolved default unchanged at `architecture/` (no env, no config) — pinned by `test_default_unchanged_when_no_env_no_pointer`; the ONLY existing-test change is the sanctioned `test_full_pytest_baseline_preserved` count-pin 12→15.
- Leaf-purity preserved: `_vault_paths.py` imports only stdlib — `test_vault_paths_module_is_leaf` green. Both new modules underscore → PMI-1 auto-excluded (36 tools scanned; UTF8-STDOUT-1 clean).
- ADR-085 (`status: accepted`, `supersedes: null`) EXTENDS ADR-065 — SUP-1 clean; MEPD-1 EXCLUDE (no RULE-ID, no methodology-changelog entry, no VERSION bump) → MCFS-1/AVFS-1/TVFS-1 all PASS.
- risk-register R-32 (`mitigating`) matches the C2 mitigation in code; no live test pins R-32 status (STP-1 green). AC4 classification map documented; VAULT_ROOT allowlist UNCHANGED at 10.

### Build deviations (NOT vault-vs-code drift)
- `diagnose-out/` seeded into the worktree post-hoc (`cp -r` from main tree) — the R-20 seed that worktree-create-at-`/slice` skips (the slice-088-flagged gap; surfaced here because this slice dogfoods the worktree-at-`/slice` model). A worktree-setup artifact, NOT a vault-vs-code divergence; `test_bcr_1_sc054_round_trip_inputs_invariant` then passes.

### Resolutions
- None required — vault and code aligned for the slice-093 surface.

## Audit 2026-05-31 (slice-090-fix-pcr-git-subprocess-cp1252-decode)

**Trigger**: slice-090 pre-finish gate (/build-slice Step 6)

**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- design.md "What's new" — every claim verified on disk via the AST guard: all **9** output-decoding (`text=True`) git `subprocess.run` sites in `tools/parallel_conflict_resolver.py` now carry `encoding="utf-8"` (`tests/methodology/test_parallel_conflict_resolver_git_encoding.py::test_all_git_decode_sites_specify_utf8_encoding` PASS); count-pinned to exactly 9 (`test_exactly_nine_git_decode_sites_byte_mode_sites_excluded` PASS).
- The 4 byte-mode staging sites (L397/403/1378/1384, `git add`/`git rebase --continue`) are UNtouched and carry no `encoding=` — verified by the same AST test (byte-mode exclusion assertion).
- Error model preserved: only the `encoding="utf-8"` kwarg was added; the existing `except (subprocess.CalledProcessError, FileNotFoundError)` fall-throughs are byte-unchanged. Strict errors (no `errors=` override) per ADR-082.
- ADR-082 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) matches design.md + mission-brief; scoped to this module with the reuse-seam note for the queued `audit-cp1252-decode-pattern-across-tools`.
- shippability.md: rows #95 (behavioral repro) + #96 (AST guard) added, both pipe-free (exactly 7 unescaped pipes); the slice's tests PASS.
- No VERSION bump (ADR-082 is a decision, not a new RULE-ID; MEPD-1 EXCLUDE) — PMI-1/MCFS-1/AVFS-1/TVFS-1 unaffected (all PASS); risk registration (cp1252 + strict-decode residual + CI-coverage + detector-gap) correctly deferred to /reflect.
- No UNSPECIFIED CODE / no STALE CLAIM: purely additive `encoding="utf-8"` kwargs + one new test; no removed feature, no signature/contract change.

### Resolutions
- None required — vault and code aligned for the slice-090 surface.

## Audit 2026-05-31 (slice-088-add-project-frame-synthesizer)

**Trigger**: slice-088 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-080 + active slice-088 design.md/mission-brief + risk-register R-26 + shippability row 93 + methodology-changelog v0.78.0 vs code/prose)
**Result**: CLEAN — no drift.

- `design.md` claims all present in code: `tools/project_frame_synth.py` exists with the documented contract — 3 required sections (`## Identity`/`## Trajectory`/`## Impact`), `_MAX_FRAME_LINES = 40` budget + truncation marker, deterministic (no wall-clock/randomness), deduped active rule FAMILIES (first valid rule-id per `## v` block + `_NON_RULE_FAMILIES` {ADR,R,SC} denylist), score-ranked open risks via `risk_register_audit._parse_risks`, named slice-queue candidates, ATTACK-LENS preamble, binary exit 0/2. Verified by `test_project_frame_synth.py` (5 green) + live smoke on this repo (14-line frame naming PSQ/BRANCH).
- **cp1252 mechanism = `_stdout.reconfigure_stdout_utf8()`** (UTF8-STDOUT-1), NOT the dual-Critic-ratified ascii-fold — design deviation recorded in design.md + build-log.md + the v0.78.0 changelog entry; user-approved. Verified by bespoke `test_project_frame_synth_survives_cp1252_with_u2192` (em-dash + arrow fixture) + UTF8-STDOUT-1 audit (34/34 clean) + the rollup-sentinel parity (discovered==covered incl. the new tool).
- Skill wiring present + installed copies synced: `design-slice` Step 0.5 (frame consult before designing), `critique`/`critique-review` Step 1 Inputs + Step 2 `# project-frame.md` block. 3 structural-pins green (BC-PROJ-14 seam-scoped) + 3 NEW OSDG-1 drift tests green (design-slice/critique/critique-review now guarded). `agents/critique.md` Dim-7 consumes the handed-over frame; CAD-1 green.
- PFS-1 v0.78.0 changelog entry present (entry-pin + shippability-propagation green); 5-part PMI-1 atomic bump 0.77.0→0.78.0 synced across all legs (PMI-1 0.78.0/34 tools, AVFS-1, MCFS-1, TVFS-1 all PASS; pip re-install refreshed ai-sdlc-tools). BC-PROJ-9 5-surface inventory fan-out complete (install_audit `_CANONICAL_TOOLS` + plugin.yaml + INSTALL.md 33→34 + bespoke cp1252 test + shippability row 93).
- `shippability.md` row 93 references `test_project_frame_synth.py` + `test_project_frame_synth_tool_inventory.py` (exist + pass); PTFFD-1 function-level-clean after the version-sync-rename citation fix (row 75 `_at_v_0_77_0`→`_at_v_0_78_0`).
- R-26 registered **open** (downgraded-by-design; advisory-frame silent-all-degrade residual, R-7 analogue). m2 ACCEPTED-PENDING discharged.
- Stale-pin fan-out from the bump resolved: version-sync test renamed `_at_v_0_77_0`→`_at_v_0_78_0` (+ shippability citation), INSTALL.md count pin 33→34 in `test_pulse_worktree_resolver_tool_inventory.py`. R-20 worktree seed: `diagnose-out/` cp'd from main tree (the `/slice`-created worktree skipped the seed).
- Full suite 1253 passed / 0 failed. No removed feature; no UNSPECIFIED CODE; no STALE CLAIM in the slice-088 surface.

### Resolutions
- None required for the slice-088 surface — vault and code aligned.
- **Carried-forward (out of scope, partially reduced)**: the pre-existing CLAUDE.md:42 OSDG-1 inventory inaccuracy (slice-086's `reconcile-osdg-1-inventory-claude-md-L42` follow-up) is REDUCED by this slice — `critique` now has a real `test_critique_skill_drift.py`, and `design-slice`/`critique-review` are added. The residual falsehoods (`diagnose` claimed-but-no-test; `code_review`/`pulse` have tests but unlisted) remain a future cleanup — flagged for /reflect.
## Audit 2026-05-31 (slice-087)

**Trigger**: slice-087 pre-finish gate (/build-slice Step 6)
**Scope**: full (active slice-087 design.md/mission-brief.md + ADR-079 + risk-register R-27 + shippability row 93 vs code/prose)
**Result**: CLEAN — no slice-087 vault-vs-code drift. (Sibling-induced shared-install drift noted below — NOT slice-087 drift.)

- `tools/stranded_slice_audit.py` matches design.md/ADR-079: classifies unmerged `slice/*` branches into the 4-class divergence model, reusing `pulse_worktree_resolver.{detect_active_worktrees,classify_worktree_state,_resolve_default_branch}` + `slice_queue_claim.parse_queue_text`; bare branches read the branch's own tree via `git show <branch>:` (M1); `status ∈ {clean, divergent}`; exit 0 advisory / exit 2 usage; UTF8-STDOUT-1 (human header always emits `→`, M3). 8/8 behavioral + 2 structural-pin + inventory-pin tests green.
- `/slice` Prerequisite consult + `/pulse` bare-branch signal prose present and OSDG-1-synced to installed copies (`test_slice_skill_drift.py` + `test_pulse_skill_drift.py` green; slice-077 offset pins intact per `test_pulse_skill_worktree_awareness.py`).
- BC-PROJ-9 5-surface inventory consistent (plugin.yaml + `_CANONICAL_TOOLS` + INSTALL.md L22/L166 33→34 + slice-077 inventory test 33→34 + `_ROOT_ONLY_TOOLS`); PMI-1/INST-1/UTF8-STDOUT-1 clean at 34 tools. R-27 registered (mitigating); shippability row 93 references the new tests (`shippability_path_audit` expected clean).
- MEPD-1 EXCLUDE confirmed: `VERSION` unchanged at `0.77.0` in-repo; no `methodology-changelog.md` entry; no new RULE-ID (ADR-079 only). PMI-1 manifest gains one tool (34); tests/ not manifested.
- **Sibling-induced shared-install drift (NOT slice-087 drift; do NOT clobber)**: the parallel sibling slice-088 (PFS-1, a version-bumping slice) has forward-synced the shared installed `~/.claude/` to **v0.78.0** (agent `critique.md` PFS-1 edit + `methodology-changelog.md` v0.78.0 entry + `ai-sdlc-VERSION` 0.78.0 + venv `ai-sdlc-tools` 0.78.0). slice-087 is MEPD-1 EXCLUDE at in-repo 0.77.0 and touches NONE of these files (`git diff HEAD -- agents/ VERSION methodology-changelog.md` empty). Consequently CAD-1, MCFS-1, AVFS-1, TVFS-1 all report DRIFT against the slice-088-advanced install — purely the PSQ parallel-window shared-install hazard, reconciling at merge (slice-087 has no conflict on any of these files; post-both-merge master == installed). slice-087 deliberately does NOT clobber slice-088's forward-sync. A `/reflect` calibration-candidate: forward-sync/content-equality audits against the single shared `~/.claude/` are structurally fragile under parallel version-bumping slices.

### Resolutions
- None required for slice-087's own surface — vault and code aligned. The sibling-induced shared-install drift is left for merge-time reconciliation (not a slice-087 action).

## Audit 2026-05-30 (slice-086)

**Trigger**: slice-086 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-078 + active slice-086 design.md/mission-brief + risk-register R-25 + shippability row 92 vs code/prose)
**Result**: CLEAN — no drift.

- design.md/ADR-078 claims all present in code: the canonical guard block (`**Await the real agent — never fabricate its output.**`, U+2014) is authored at the spawn→write seam (between `### Step 2` and `### Step 3`) of all three `skills/{critique,critique-review,code-review}/SKILL.md`; verified by `tests/methodology/test_r25_await_real_agent_guard.py` (7/7 green: seam-scoped heading + body pins across 3 skills + the relocate-fixture proving placement enforcement). APED-1: heading file_count=1 + seam_count=1 per skill, body seam_count=1.
- AC-3 install: installed `~/.claude/skills/{critique,critique-review,code-review}/SKILL.md` synced to the worktree edits; `test_code_review_skill_drift.py` green (the only OSDG-1 content-equality drift test among the three — critique/critique-review have none per B1/B2). critique/critique-review prose-pins + both agent-drift tests green.
- AC-4: global `~/.claude/CLAUDE.md` `# Spawned-agent output` stopgap removed (grep count → 0), performed only AFTER AC-1/2/3 verified (ordering invariant per ADR-078 §Consequences). The migration is recorded here + in build-log.md; full reflection-record deferred to /reflect.
- shippability.md row 92 references `tests/methodology/test_r25_await_real_agent_guard.py`, which exists + passes; `shippability_path_audit` CLEAN.
- R-25 stays **open** this slice (register flip to retired is a /reflect action, consistent with the slice-077/082/084/085 pattern); no STP-1 stale-pin (no test claims R-25 retired). The pre-existing CLAUDE.md:42 OSDG-1 inventory drift (B2) is logged as the out-of-scope follow-up `reconcile-osdg-1-inventory-claude-md-L42` — NOT a slice-086 surface.
- MEPD-1 EXCLUDE confirmed: `VERSION` unchanged at `0.77.0`; no `methodology-changelog.md` entry; no new RULE-ID. PMI-1 inventory gains one file (the new test) — manifest unaffected (tests/ not manifested). MCFS-1/AVFS-1/TVFS-1 all expected PASS with VERSION unchanged.
- No removed feature; no UNSPECIFIED CODE; no STALE CLAIM.

### Resolutions
- None required — vault and code aligned for the slice-086 surface.

## Audit 2026-05-30 (slice-085)

**Trigger**: slice-085 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-077 + active slice-085 design.md/mission-brief + risk-register R-24 narrowing + slice-queue/shippability claims vs code)
**Result**: CLEAN — no drift.

- ADR-077 / design.md claims all present in code: `tools/slice_queue_writer.py:129` `_RENDERED_FIELD_LABELS` constant; `_format_entry` (`:650-667`) renders the 5 PSQ-1 field lines FROM it via zip (genuine SSoT, M3); `tools/parallel_conflict_resolver.py:1690` `_baseline_is_truncation_shaped(queue_text)` (tail-specific last-block scan; CRLF-normalized; empty/`_(no candidates)_` placeholder fail-open; labels read from `slice_queue_writer._RENDERED_FIELD_LABELS` at `:1729`); orphan-branch Option-4 wiring at `:1848-1865` (orphan_claims + truncation-shaped → `_fail` STOP, audit row first; fail-closed on helper raise; well-formed → existing WARN). Verified by reading the live source + 134-test PCR/queue/writer suite green + APED-1 executed battery.
- R-24 carries the `**Narrowed:** slice-085` annotation; Status stays **open** (downgraded, low/low) — RR-1 parses status from the `**Status**:` field (unchanged), no STP-1 stale-pin (no test claims R-24 retired).
- MEPD-1 EXCLUDE confirmed: `VERSION` unchanged at `0.77.0`; no `methodology-changelog.md` entry; PMI-1 inventory unchanged (in-place edits to already-manifested `slice_queue_writer.py` + `parallel_conflict_resolver.py`, no new file). MCFS-1/AVFS-1/TVFS-1 all PASS with VERSION unchanged.
- No removed feature; no UNSPECIFIED CODE; no STALE CLAIM (the pre-existing `:1775-1783` overlay-silent-drop STOP is untouched and pinned by AC-4a `test_overlay_silent_drop_still_stops_1775_1783`).

### Resolutions
- None required — vault and code aligned for the slice-085 surface.

## Audit 2026-05-30 (slice-084)

**Trigger**: slice-084 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-076 + active slice-084 design.md/mission-brief + risk-register R-23 + shippability row 90 vs code)
**Result**: CLEAN — no drift.

- design.md claims all present in `tools/parallel_conflict_resolver.py`: `_CLOCK_SKEW_TOLERANCE_SECONDS = 300`, `_winner_clock_skew_suspect(winner, now, tolerance_seconds)`, `_append_skew_stop_audit(repo_root, diag, reason, winner, loser, now)`, the Step 2.5 guard wired into `resolve_vault_claim_conflict` with the new `now` param, and the L1154 `_format_vault_claim_audit_entry` docstring touch-up (Claim-seq → resolver-now guard). Verified by reading the live source + 20-test suite green.
- ADR-076 claims align with code: resolver-now future-dating detection (NOT Claim-seq); defensive parse (Z→+00:00, unparseable→STOP, tz-naive→STOP, except(ValueError,TypeError)); mints no RULE-ID (MEPD-1 EXCLUDE — no VERSION bump, confirmed by MCFS-1/AVFS-1/TVFS-1 PASS with VERSION unchanged at 0.77.0).
- `_select_timestamp_winner` (:502) unchanged — stays a pure strict-newer comparator (no drift to the DRY audit-site at L1761).
- shippability.md row 90 references `tests/methodology/test_pcr_2a_clock_skew_winner.py`, which exists + passes (20 items).
- risk-register R-23 stays OPEN this slice (narrowed, NOT retired — /critique M1); downgrade + residual registration deferred to /reflect. No status-pin drift (STP-1 clean).
- No removed feature; no UNSPECIFIED CODE; no STALE CLAIM (the L1154 Claim-seq forward-ref was updated to the shipped resolver-now approach in the same edit).

### Resolutions
- None required — vault and code aligned for the slice-084 surface.

## Audit 2026-05-29 (slice-082)

**Trigger**: slice-082 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-074 + risk-register R-21 + active slice-082 design.md/mission-brief)
**Findings**: 0 blockers, 0 majors, 1 minor (slice-local design.md line citations now approximate post-insertion — non-behavioral)

### Blockers
(none)

### Majors
(none)

### Minors
- `design.md` cites absolute line numbers in `tools/parallel_conflict_resolver.py` (e.g. write loop `:316`, helper internals `:666-727`/`:1242`). The guard insertion shifted these (empty-check unchanged at `:302`; write loop now `:339`; new `_verify_soft_equivalence` + `_append_equivalence_stop_audit` added ~150 lines so downstream helpers moved down). The LOGICAL/behavioral claims are accurate (guard runs after the empty-check, before the write loop, read-only; invariants #1-3 as specified; reuses `_SoftResolutionError`). Treated as expected self-insertion offset, NOT behavioral drift; the citations remain useful approximate anchors. Not churned per thin-vault.

### Verified aligned
- ADR-074 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (SOFT equivalence guard, R-21 fix-class (b)) matches design.md + mission-brief; selects the fix-class R-21's own register entry enumerates; contradicts no existing accepted ADR (refines ADR-069/PCR-1 in place, supersedes nothing).
- design.md "What's new" behavioral claims verified on disk: `_verify_soft_equivalence` exists in `tools/parallel_conflict_resolver.py`, is read-only, raises the reused `_SoftResolutionError(..., ConflictClass.UNKNOWN)`, is called from `resolve_soft_conflict` after the `if not pending_writes` empty-check and before the write loop; `_append_equivalence_stop_audit` writes the `(equivalence-guard STOP)` section variant; the 3 invariants (claimed-subset claim-preservation / numbered-row completeness / symmetric prelude set-equality) are implemented as designed; M2 cross-stage-claim-drop is a stderr warn, not a STOP.
- mission-brief must-not-defer all addressed in code: fail-closed default (unprovable → STOP); no partial writes (guard sits strictly before first `write_text`/`git add`/`rebase --continue`; STOP leaves U-files + index + rebase untouched — pinned by `test_stop_leaves_repo_state_unmutated`); audit trail (`_append_equivalence_stop_audit`, best-effort); happy-path preservation (`test_happy_path_*` + full PCR suite 159/159 green); APED-1 empirical battery (8 tests drive the real resolver against real tmp-repo rebase fixtures).
- shippability.md row 88 pins `tests/methodology/test_pcr_1_soft_regen_equivalence_guard.py` (AC-5) — `test_shippability_pins_equivalence_guard` asserts it.
- MEPD-1 EXCLUDE: slice-082 mints no new RULE-ID (hardens PCR-1's SOFT path via ADR-074); no VERSION bump (slice-077/079 EXCLUDE precedent). VERSION stays `0.76.0`; PMI-1/AVFS-1/MCFS-1/TVFS-1 all PASS unchanged. risk-register R-21 retirement happens at /reflect (STP-1 clean now — no test pins R-21 status).

### Resolutions
- None required — vault and code aligned for the slice-082 surface (the one minor is cosmetic line-citation offset, intentionally not churned).

## Audit 2026-05-15 14:40

**Trigger**: slice-024 pre-finish gate (/build-slice Phase 6)
**Scope**: full (thin-vault surface — ADRs + risk-register + active slice design/mission-brief)
**Findings**: 0 blockers, 0 majors

### Blockers

(none)

### Majors

(none)

### Notes

slice-024 is a pure methodology-codification slice. All vault claims verified against code reality by the Phase 6 audit gauntlet:
- ADR-022 (status: accepted, reversibility: cheap, supersedes: null) — matches design.md + mission-brief claims.
- `agents/critique.md` carries the FBCD-1 `Fix-block-completeness discipline` Dim 9 10th sub-clause (CAD-1 byte-equal in-repo ↔ installed; sha256 f0bd6653cf5a97a0...).
- `methodology-changelog.md` v0.38.0 entry present in-repo + installed (bidirectional sha256 byte-equal 3928548a2bddfe68...).
- `architecture/risk-register.md` untouched (0 changed files) — matches "no new risks introduced" claim (R-1/R-2/R-3 unchanged).
- TF-1 plan 13/13 PASSING; PMI-1 clean (version 0.38.0); SCPD-1 propagation clean (5 pytest-cmd rows propagated, 2 historical preserved).

No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM. Vault and code aligned.

## Audit 2026-05-16

**Trigger**: slice-026 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — active slice-026 ADR-024 + design.md + mission-brief.md; risk-register; ADRs status:accepted)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
- ADR-024 claims verified vs code: `tools/critique_review_prerequisite_audit.py` exists and reads the `critique-review-skip` milestone.md frontmatter key (10 refs) with regex `^skip — rationale: .+`; escape-hatch location matches ADR-024 decision.
- ADR-019 conformance verified: zero `CRPD-1`/`-D` rule-ID residue in source (tools/, build-slice SKILL.md, plugin.yaml). The single `CRPD-1` token in methodology-changelog.md v0.40.0 is legitimate historical narrative documenting the /critique B1 catch, not a live naming-class assertion.
- All slice-026 design.md "What's new" file claims exist on disk.
- No risk-register drift (slice-026 retires no registered R-N; it closes a methodology-process gap from slice-025 reflection L37).
- Self-hosting drift gates all clean this slice: CAD-1 (agents/critique.md byte-equal), PMI-1 (v0.40.0, 19 tools), INST-1 (19/19), mini-CAD (build-slice SKILL.md in-repo↔installed byte-equal), milestone.md template in-repo↔installed byte-equal (M-add-1).

### Resolutions
- No findings; no resolutions required.

## Audit 2026-05-16 (slice-028 pre-finish gate)

**Trigger**: slice-028 /build-slice pre-finish gate
**Scope**: active slice-028 (vault ADR-026 + design.md + mission-brief vs code)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- CLEAN — 8 vault claims verified aligned: helpers exist; sentinel name preserved (shippability row 23 target); 3 guard tests exist; no int-count Compare in sentinel body (AC#1); PMI-1 atomic 0.42.0 across VERSION+plugin.yaml+installed; ADR-026 accepted/reversibility:cheap; risk-register unmodified (no R-ID retired); no unspecified changed files (design.md Components-touched complete).

## Audit 2026-05-17 02:40

**Trigger**: slice-031 (split-label 030B) /build-slice pre-finish gate
**Scope**: full (thin vault — ADRs + risk-register + active slice-031 design/mission-brief)
**Findings**: 0 blockers, 0 majors

### Verified aligned
- ADR-030 / ADR-031: status=accepted, reversibility=cheap (slice-031's own decisions).
- design.md "What's new" — all files exist (tools/shippability_decoupling_audit.py, tests/methodology/test_shippability_{decoupling_audit,command_column}.py, fixtures/archive_backtest_corpus/, validate-slice/SKILL.md).
- ADR-031 "6th machine-stable column" ⇔ shippability.md header = 6 columns; "shippability_path_audit reads Machine-cmd" ⇔ `cells[5] if len(cells) > 5 else cells[3]` present.
- risk-register R-4 = `mitigating` (NOT retired — honest incidental-only split); sub-entry charters slice-030C; M-add-1 carried (DEFERRED).
- SCMD-1 self-run clean (incidental=0, essential=31 recognized-not-flagged); TF-1 18/18 PASSING.

### Resolutions
- None required — thin vault authored concurrently with code; zero drift accrued.

### Out-of-scope note (not slice-031 drift)
- `tests/skills/diagnose/test_diagnose_skill_drift.py` fails on R-5/D-1 CRLF-LF fragility (in-repo CRLF vs installed LF, content byte-identical normalized; diagnose SKILL.md git-untouched this slice). Pre-existing, explicitly out-of-scope per slice-031 mission-brief; slice-030A precedent (user-approved-deferral against R-5). Tracked by risk-register R-5.

## Audit 2026-05-17 01:20

**Trigger**: slice-035 pre-finish gate
**Scope**: full (active slice slice-035-rename-status-skill-to-pulse)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- ADR-035 rename claims verified against code: skills/pulse/ exists, no skills/status/, plugin.yaml id:pulse, install_audit canonical "pulse", VERSION/changelog v0.49.0 SRCD-1 — all aligned.
- design.md Bucket A/B/C taxonomy verified: post-edit inventory grep shows Bucket A empty (0 executable path binds, 0 test_status_ fns). Frozen-as-history (ADR-030 corpus, lessons-learned.md:414, historical changelog entry narratives) intentionally retained per ADR-035.
- shippability #35 Command-cell test paths all resolve on disk.
- risk-register.md: no risks claimed retired by this slice (R-1/R-2 untouched).

## Audit 2026-05-17 02:30

**Trigger**: slice-036-fix-rr1-audit-status-filter pre-finish gate
**Scope**: full (active slice slice-036; Standard thin vault)
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Resolutions
- ADR-036 / design.md claim "out['risks'] = filtered view, no out['view']" verified vs `tools/risk_register_audit.py:424` (out["risks"] = [r.to_dict() for r in view]; zero `out["view"]` occurrences).
- design.md "What's reused" (filter_and_sort:319, _format_human:348, to_dict:119 unchanged) verified — anchors present, slice touched only the `if args.json:` block.
- R-9 `architecture/risk-register.md` still `Status: open` (L166) — NOT drift: slice retires R-9 proactively; register entry is updated at /reflect, design.md claims proactive retirement only.
- shippability #36 command target `test_repro_r9_json_filter_status_open_excludes_retired_in_consumed_risks` exists and PASSES.

## Audit 2026-05-17 — slice-038 pre-finish gate

**Trigger**: slice-038 /build-slice pre-finish gate
**Scope**: full (thin vault — active slice slice-038 + ADR-039 + R-8)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified clean
- ADR-039 (accepted): `tools/shippability_runner.py` exists and REUSES SCMD-1 `_segments`/`_catalog_rows`/`_machine_cmd_cell` by object identity (not re-derived) — verified.
- design.md code refs (`tools/shippability_runner.py`, `tests/methodology/test_shippability_runner_segment_contract.py`) exist.
- AC1/AC3 claim: `skills/validate-slice/SKILL.md` Step 5.5 invokes `tools.shippability_runner` + carries the canonical no-hand-roll/reuse pins — present in BOTH in-repo and installed copies.
- methodology-changelog.md v0.51.0 SRSC-1 entry forward-synced in-repo↔installed (EOL-agnostic per EOL-DRIFT-1).
- risk-register R-8 `Status: retired` consistent with shipped SRSC-1 (runner + SKILL.md invocation + catalogued regression #38).
- No UNSPECIFIED CODE / STALE CLAIM: SRSC-1 is additive; no removed feature, no orphan code.

## Audit 2026-05-19 00:30

**Trigger**: slice-045 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin-vault Standard) — focus on slice-045 surface
**Findings**: 0 blockers, 0 majors

### Blockers
- none

### Majors
- none

### Verification performed
- design.md EDIT-1..EDIT-4 claims vs code reality: INSTALL.md:93 = `pip install graphifyy` (✓); `v0.20.0` literal absent from INSTALL.md (✓ repro test 2); INSTALL.md tool-count claims = 25 = plugin.yaml `- path: tools/` count (✓ repro test 3); README.md:69 + tutorial HTML:1050 name `graphifyy` (✓ AC4 test).
- mission-brief must-not-defer "no collateral rename of graphify module/CLI": grep confirms `graphifyy` appears exactly once in INSTALL.md (line 93, pip target only); all 5 `$PY -m graphify` / `graphify --help` / `graphify install` module/CLI refs (lines 58/91/95/99/174) unchanged; no stray `-m graphifyy` / `import graphifyy` (✓).
- risk-register R-11 born-retired: `**Status**: retired` field line present; RR-1 audit clean (total 11, retired 8, 0 violations); R-11's factual claims (wrong PyPI name fixed, stale prose fixed, shippability #45 guard exists) all match code reality (✓).
- shippability #45 consumer reference: catalogued command targets the extant `tests/methodology/test_install_md_correctness.py` (4 tests, all PASSING); SCPD-1/PTFCD-1 consistent.
- No UNSPECIFIED CODE / STALE CLAIM: slice is prose-correctness + a regression test; no removed feature, no orphan vault claim. graphify module/CLI is NOT renamed (only the PyPI distribution token), so no ADR/component drift.

### Resolutions
- none required — vault and code aligned for the slice-045 surface.

## Audit 2026-05-19 15:05

**Trigger**: slice-049 /build-slice pre-finish gate
**Scope**: full (Standard / thin vault; active slice = slice-049 only)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
Vault claims verified against code reality: ADR-051 (status: accepted, reversibility: cheap, supersedes: null) ↔ `tests/methodology/test_{triage,adopt}_skill_drift.py` exist + reuse `assert_md_forward_synced` verbatim (2 refs each, zero new comparator); `methodology-changelog.md` `## v0.57.0` OSDG-1 entry present + forward-synced (MCFS-1 PASS); exactly ONE `| 49 | slice-049-…` shippability row (SRSC-1 runner: 49 rows / 49 PASS); `VERSION`=`plugin.yaml.version`=`~/.claude/ai-sdlc-VERSION`=0.57.0 (PMI-1/INST-1 clean). Full methodology suite 730 passed; CAD-1 + all skill-drift + OSDG-1 + entry-pin guards green. No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM. (Pre-existing `~/.claude/ai-sdlc-VERSION`=0.55.0 slice-048 leg-drift was reconciled to 0.57.0 by this slice's 4-part bump — recorded in slice-049 build-log FINDING for /reflect.)

## Audit 2026-05-19 18:33

**Trigger**: slice-051 pre-finish gate
**Scope**: full (thin vault — ADRs accepted, risk-register, active slice-051 design/brief)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Resolutions
- Clean. ADR-053 claims verified: tests/methodology/test_reflect_skill_drift.py exists; CLAUDE.md OSDG-1 bullet names reflect; methodology-changelog.md v0.59.0 entry present; 4-part PMI-1 bump 0.58.0->0.59.0 (PMI-1/AVFS-1/MCFS-1 PASS); shippability row #51 (SCMD-1 clean 51 rows). risk-register: no retired-claim this slice (STP-1 clean). slice-051 design/brief references all resolve to existing artifacts (746-pass methodology suite).

## Audit 2026-05-20 — slice-052 pre-finish gate

**Trigger**: slice-052-add-slice-candidates-obo-mode pre-finish gate (/build-slice Step 6)
**Scope**: full (thin-vault surface: ADR-054, risk-register R-12/R-13, active slice design.md + mission-brief, methodology-changelog v0.60.0)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Notes
ADR-054 `status: accepted` and its code claim holds — `build_backlog.py` exposes `obo_extract`/`obo_write`/`obo_peek`, and `obo_peek` enforces the allow-set mechanically via `{Path(p).resolve() for p in evidence_files(...)}` containment (not honour-system). `skills/slice-candidates/SKILL.md` carries the `--obo interactive review mode` section + the Hard-rule-#2 ADR-054 carve-out + the `--obo-peek` only-source-read-channel constraint. R-13 ("OSDG-1 not yet extended to /slice-candidates", status `open`) is consistent with reality — `tests/methodology/test_slice_candidates_skill_drift.py` is correctly ABSENT (deliberate own-slice deferral). R-12 ("Hard-rule-#2 controlled relaxation", `mitigating`) matches the mechanical `--obo-peek` gate + shippability row #52. methodology-changelog `## v0.60.0` references real code (`build_backlog.py --obo-peek`); design.md / mission-brief references all resolve to existing artifacts (`test_slice_candidates_obo.py` + fixture + `backlog.golden.md`). 4-part PMI-1 bump 0.59.0→0.60.0 (PMI-1/AVFS-1/MCFS-1 PASS); 764-pass methodology suite; design.md "drift posture unaffected" claim corrected in-slice (logged deviation). No DRIFT / UNSPECIFIED-CODE / STALE-CLAIM.

## Audit 2026-05-22 — slice-058 pre-finish gate

**Trigger**: slice-058-add-install-wakeup-prompt-guardrail /build-slice Step 6 pre-finish gate
**Scope**: full (thin-vault Standard — ADRs accepted, risk-register, active slice-058 design.md + mission-brief.md)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified aligned
- ADR-057 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (seed the guardrail via an INSTALL.md → global `~/.claude/CLAUDE.md` append) matches code: `INSTALL.md` carries `### 3h: Global CLAUDE.md — wakeup-prompt discipline`; `/triage` + `/adopt` SKILL.md are untouched (the option-2 per-project route was not taken).
- design.md "What's new" — all claims verified on disk: INSTALL.md Step 3h present; the `# Wakeup-prompt discipline` block embeds the four load-bearing facts; `tests/methodology/test_install_md_wakeup_guardrail.py` created (3/3 PASS); `architecture/shippability.md` row #58 present (SRSC-1 runner 58/58 PASS); ADR-057 on disk.
- B2 cleanup verified: `INSTALL.md` carries **zero** version-number literals after the line-18 reword (re-grep `v?0\.\d+\.\d+` → no matches) — the `v0.54.0` staleness is drift-proof, not band-aided.
- Inclusion-heuristic "no bump" claim holds against reality: `VERSION` unchanged at `0.62.0`; `methodology-changelog.md` unchanged (MCFS-1 + AVFS-1 PASS); `plugin.yaml` untouched.
- risk-register.md: slice-058 retires no registered risk (it is preventive; no `**Status**:` flip) — STP-1 clean, consistent.
- git tracked changes = exactly `M INSTALL.md` + new `tests/methodology/test_install_md_wakeup_guardrail.py` — matches design.md "Components touched" precisely; no UNSPECIFIED CODE.
- No STALE CLAIM: the slice is additive install-recipe prose + a regression test; no removed feature, no orphan vault claim.

### Resolutions
- None required — vault and code aligned for the slice-058 surface.

## Audit 2026-05-23 01:15

**Trigger**: slice-059 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADRs + risk-register + active slice-059 design.md/mission-brief)
**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- ADR-058 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (mint TVFS-1 as a standalone tool `tools/ai_sdlc_tools_version_forward_sync.py`, purelib-scoped read) matches code: the tool exists on disk; the read mechanism is `importlib.metadata.distributions(path=[sysconfig.get_path("purelib")])` exactly as the ADR specifies.
- design.md "What's new" / "What's modified" — every claim verified on disk: the tool + `tests/methodology/test_ai_sdlc_tools_version_forward_sync.py` (8 tests) created; `tools/install_audit.py` `_CANONICAL_TOOLS` carries the entry + the two count-literal scrubs + the M-add-1 cross-ref; `plugin.yaml` carries the `- path:` entry; `skills/build-slice/SKILL.md` Step 6 + `skills/reflect/SKILL.md` Step 5b-tvfs wired; `methodology-changelog.md` v0.63.0 entry; `architecture/shippability.md` row #59; the two `test_v_0_63_0_tvfs_1_*` entry-pins added.
- mission-brief must-not-defer — all addressed in code: graceful not-installed handling (the `None`→WARN branch, no traceback); actionable mismatch message (`_ATTRIB_DRIFT` names `pip install --upgrade` + INSTALL.md Step 3g); CWD-shadowing confirmed closed (purelib-scoped resolver; `test_real_resolver_excludes_in_repo_egg_info` PASS); shippability propagation (row #59 + consumer-propagation entry-pin); UTF8-STDOUT-1 (`_stdout.reconfigure_stdout_utf8()` first line of `main()`).
- 4-part PMI-1 bump consistent: `VERSION` = `plugin.yaml.version` = `pyproject.toml [project].version` = `0.63.0`; methodology-changelog head `## v0.63.0`; installed `~/.claude/ai-sdlc-VERSION` = `0.63.0` (AVFS-1 PASS); TVFS-1's own gate confirms the installed `ai-sdlc-tools` pip distribution = `0.63.0` (bootstrap re-install done).
- risk-register.md: slice-059 retires no registered risk (the gap it closes was a newly-discovered un-numbered gap; a risk entry may be minted at /reflect per design.md) — STP-1 clean, consistent.
- No UNSPECIFIED CODE / no STALE CLAIM: the slice is additive (a new tool + the new rule TVFS-1); no removed feature, no orphan vault claim. Full methodology suite 807/807 PASS; 14 Step 6 audits exit 0.

### Resolutions
- None required — vault and code aligned for the slice-059 surface.

## Audit 2026-05-29 (slice-081-fix-drift-check-enforcement-gap)

**Trigger**: slice-081 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADRs + risk-register + active slice-081 design.md/mission-brief)
**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- ADR-073 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (mint DCE-1 as a procedural was-it-marked gate, CRP-1 pattern, not semantic) matches design.md + mission-brief claims; no contradiction with an existing accepted ADR.
- design.md "What's new" — every claim verified on disk: `tools/drift_check_audit.py` exists with `main()`; `skills/build-slice/SKILL.md` Step 6 carries the DCE-1 sub-block + checklist item + invokes `tools.drift_check_audit`; Step 7b preserves `drift-check-skip:`; `skills/drift-check/SKILL.md` Trigger template canonicalized `sliceNN`→`slice-NNN`; `templates/milestone.md` documents `drift-check-skip:`; `plugin.yaml` + `tools/install_audit.py` enumerate the tool.
- mission-brief must-not-defer — all addressed in code: the audit performs a genuine check (NOT a stub); fail-closed exit contract 0/1/2; UTF8-STDOUT-1 conformance (`_stdout.reconfigure_stdout_utf8()` first in `main()`); own unit tests with clean + violation + M-add-1 negative fixtures; new rule DCE-1 + ADR-073 + shippability rows 86/87 + 5-part version bump.
- 5-part PMI-1 bump consistent: `VERSION` = `plugin.yaml.version` = `pyproject.toml [project].version` = `0.76.0`; `## v0.76.0` changelog header present in-repo + forward-synced installed; installed `~/.claude/ai-sdlc-VERSION` = `0.76.0`; venv `ai-sdlc-tools` = `0.76.0`.
- risk-register.md: slice-081 retires no registered risk (the gap it closes was a fresh user-reported defect, un-numbered) — STP-1 clean, no stale status pin.
- No UNSPECIFIED CODE / no STALE CLAIM: the slice is additive (a new tool + the new rule DCE-1); no removed feature, no orphan vault claim.

### Resolutions
- None required — vault and code aligned for the slice-081 surface.

## Audit 2026-05-30 (slice-083-add-pcr-2b-hard-class-conflict-resolution)

**Trigger**: slice-083 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-075 + active slice-083 design.md/mission-brief + methodology-changelog v0.77.0 + shippability)
**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- ADR-075 (`status: accepted`, `reversibility: expensive`, `supersedes: null`) — its decision (mint PCR-2b + TRI-RESOLVE-1; gate-on-hand-resolve; `code-review` agent not the critique agents per M-add-2) matches design.md + mission-brief; refines ADR-069's HARD/MIXED rows WITHOUT editing ADR-069 (verified: ADR-069 HARD/MIXED "Shipped in" cells still read "slice-077 (PCR-2)" — byte-unchanged).
- design.md "What's new" — every claim verified on disk: `tools/parallel_conflict_resolver.py` now defines `resolve_hard_conflict`, `_verify_resolution_clean`, `_format_hard_audit_entry`, `_record_hard_resolution`, `_CONFLICT_MARKER_OPENER_RE`, and the `--verify-resolution`/`--record-hard-resolution` CLI modes; the HARD/MIXED dispatch branch in `resolve_soft_conflict` routes through `resolve_hard_conflict`; `skills/commit-slice/SKILL.md` sub-step 2.5 carries the PCR-2b gate-on-hand-resolve flow + TRI-RESOLVE-1.
- B2/M-add-1 fix verified: `_CONFLICT_MARKER_OPENER_RE` keys on `^[ +-]?(?:<{7}|>{7})` — empirically setext `=======` + 30-`=` dividers do NOT match; `<<<<<<<`/`>>>>>>>` openers/closers do (`test_pcr_2b_verify_resolution.py::test_verify_resolution_clean_on_resolved_markdown_setext` PASS).
- M-add-2 fix verified: SKILL.md spawns `subagent_type: "code-review"` (NOT the critique agents) + records WHY (fail-stop on missing design.md).
- mission-brief must-not-defer — all addressed: fail-closed at every leg (HARD/MIXED never auto-continue; resolve_hard_conflict NEVER runs `git rebase --continue`); TRI-RESOLVE-1 is SOAD-1 structured-options (pinned); bootstrap fallback to bare SOAD-1 (pinned); audit-log best-effort `## Hard-conflict resolution -`; OSDG-1 forward-sync of commit-slice SKILL.md done; no new module/agent → PMI-1/INST-1 inventory unchanged (33 tools, 6 agents, 26 skills).
- 5-part PMI-1 bump consistent: `VERSION` = `plugin.yaml.version` = `pyproject.toml [project].version` = `0.77.0`; `## v0.77.0` changelog header present in-repo + forward-synced installed; installed `~/.claude/ai-sdlc-VERSION` = `0.77.0`; venv `ai-sdlc-tools` = `0.77.0` (MCFS-1/AVFS-1/TVFS-1 all PASS).
- risk-register.md: slice-083 retires no registered risk (R-23/R-24 stay OPEN — remediation venue only, per /slice scope) — STP-1 clean, no stale status pin.
- No UNSPECIFIED CODE / no STALE CLAIM: additive (new functions + two new rules PCR-2b/TRI-RESOLVE-1); no removed feature; the stale `slice-079`/`PCR-2` forward-refs (m2) were updated to shipped-status in SKILL.md + resolver docstring.

### Resolutions
- None required — vault and code aligned for the slice-083 surface.

## Audit 2026-05-31 (slice-089-make-commit-slice-stale-branch-check-parallel-slice-aware)

**Trigger**: slice-089 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin vault — ADR-081 + active slice-089 design.md/mission-brief + commit-slice SKILL.md + new tool stale_branch_classifier.py; no VERSION bump, MEPD-1 EXCLUDE)
**Findings**: 0 blockers, 0 majors

### Blockers
(none)

### Majors
(none)

### Verified aligned
- ADR-081 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (worktree-backing discriminator via the RAW `pulse_worktree_resolver._parse_worktree_porcelain`, NOT `detect_active_worktrees`; path-equality + branch self-exclusion; exit 0/1/2; bootstrap-fallback to flag-all-minus-current) matches design.md + the shipped `tools/stale_branch_classifier.py`.
- design.md "What's new" verified on disk: `tools/stale_branch_classifier.py` defines `classify_stale_branches` + `main` + `StaleBranchVerdict` (with `noncanonical_backed`); strips `refs/heads/`→short before set ops (meta-Critic B-add-1); every git subprocess passes `encoding="utf-8"` (heeds parallel slice-090's cp1252 class — does NOT reuse the encoding-less `pulse_worktree_resolver._run_git`).
- `skills/commit-slice/SKILL.md` Step 5b sub-step 1 + Step 5c pre-flight #2 carry the byte-identical `<!-- STALE-BRANCH-CHECK -->` block invoking the classifier; "Stale-slice-branch check" label preserved (anchor test green); OSDG-1 in-repo==installed (drift test green).
- PMI-1/INST-1 inventory updated for the new tool: `plugin.yaml` + `tools/install_audit.py` enumerate `stale_branch_classifier` (36 tools); installed venv `ai-sdlc-tools` force-reinstalled so the module resolves from site-packages.
- MEPD-1 EXCLUDE: no new RULE-ID (refines BRANCH-2/PSQ-family guardrail); VERSION unchanged at 0.78.0 (MCFS-1/AVFS-1/TVFS-1 all PASS — no version-bump legs to sync).
- risk-register.md: slice-089 retires no registered risk (closes the parallel-unaware false-positive noted post-slice-088 merge — not a registered R-NN) — STP-1 clean, no stale status pin.
- No UNSPECIFIED CODE / no STALE CLAIM: additive (one new read-only tool + one new test module + SKILL.md guardrail rewrite); the superseded slice-021 B5 flag-all heuristic prose was replaced in place at both surfaces.

### Resolutions
- None required — vault and code aligned for the slice-089 surface.

---

## 2026-05-31 — slice-091-harden-pcr-decode-non-silent

**Trigger**: slice-091 pre-finish gate (/build-slice Step 6)
**Scope**: full (thin-vault Standard — ADR-083, active slice-091 design.md + mission-brief.md vs `tools/parallel_conflict_resolver.py` + tests)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified aligned
- ADR-083 (`status: accepted`, `reversibility: cheap`, `supersedes: null`) — its decision (bytes-capture + explicit strict decode; `_StageDecodeError(_SoftResolutionError, UNKNOWN)`; degraded-flag → UNKNOWN STOP; best-effort breadcrumb) matches the shipped `tools/parallel_conflict_resolver.py`: `_git_show_stage` now captures bytes + `.decode("utf-8")` and raises `_StageDecodeError`; `diagnose_conflict` catches both stage reads + sets `claim_extraction_degraded` via the constructor; `classify_conflict` returns UNKNOWN when degraded; `_append_decode_stop_audit` writes the `## Decode-failure STOP (non-UTF-8 stage)` section.
- design.md "What's new" verified on disk: `_StageDecodeError` subclasses `_SoftResolutionError`; `ConflictDiagnostic.claim_extraction_degraded: bool = False` (frozen+slots, set via constructor — m-add-1); the catch wraps stage-2 AND stage-3 reads (m-add-2). `_git_show_stage` docstring inverted to document raise-on-undecodable (m1).
- BUILD CORRECTION reconciled across vault: count-pin is byte-mode 4→5, decode unchanged at 9 (the `_append_decode_stop_audit` rev-parse decode site offsets `_git_show_stage`); `test_parallel_conflict_resolver_git_encoding.py` (`_EXPECTED_BYTE_MODE_SITES=5`) + shippability #96 + design.md + ADR-083 + mission-brief all corrected — no stale "9→8" claim remains in the live slice surface.
- shippability.md rows #98 (repro) + #100 (decode-fail-closed guard) present; #99 reserved for parallel slice-092 (non-overlapping, `tools/stranded_slice_audit.py`).
- MEPD-1 EXCLUDE: no new RULE-ID (narrows R-30 residual #1); VERSION unchanged (MCFS-1/AVFS-1/TVFS-1 no-op — no version-bump legs to sync).
- risk-register.md: R-30 stays `mitigating` (this narrows residual #1; residual #2 out of scope) — STP-1 clean, no stale status pin flipped by this slice.
- No UNSPECIFIED CODE / no STALE CLAIM: additive (one module hardened + two test files + catalog rows); no removed feature, no orphan vault claim.

### Resolutions
- None required — vault and code aligned for the slice-091 surface.

## Audit 2026-06-01 10:19

**Trigger**: slice-096 pre-finish gate
**Scope**: full (active slice slice-096-add-slice-candidates-drift-guard)
**Findings**: 0 blockers, 0 majors

### Blockers
- (none)

### Majors
- (none)

### Verified aligned
- design.md "What's new" verified on disk: (1) `tests/methodology/test_slice_candidates_skill_drift.py` EXISTS — asserts in-repo `skills/slice-candidates/SKILL.md` ≡ installed via the shared `assert_md_forward_synced` (runs PASS + proven non-vacuous by mutation); (2) `CLAUDE.md` OSDG-1 `Guarded skills:` enumeration now names `slice-candidates` + its test; (3) `architecture/shippability.md` row #102 present with the full 6-column SCMD-1 shape.
- No new ADR (design.md "Decisions made" = None; MEPD-1 = EXCLUDE). Referenced ADRs unchanged/accepted: ADR-033 (EOL-DRIFT-1), ADR-051 (OSDG-1), ADR-054 (`/slice-candidates` `--obo-peek` carve-out).
- MEPD-1 EXCLUDE: `VERSION` + `methodology-changelog.md` + `plugin.yaml` + `tools/install_audit.py` UNCHANGED → MCFS-1/AVFS-1/TVFS-1 no-op (no version-bump legs to sync); PMI-1/INST-1 no-op (no installed artifact added — a test is not plugin-enumerated).
- risk-register.md: R-13 stays `open` — this slice retires it but the status flip is `/reflect`'s job (the register reflects reality at slice end); no stale status pin flipped here (STP-1 clean).
- `skills/slice-candidates/SKILL.md` NOT edited (in-repo ≡ installed already); `.gitattributes` + `_GUARDED_GLOBS` unchanged (the `skills/**/SKILL.md` blanket glob already covers the new member).
- No UNSPECIFIED CODE / no STALE CLAIM: purely additive (one test + one CLAUDE.md sentence + one catalog row); no removed feature, no orphan vault claim.

### Out-of-scope pre-existing finding (NOT slice-096 drift)
- `tests/methodology/test_external_vault_adr_and_risk.py:49` FAILs on clean master too (FileNotFoundError on the archived slice-093 active-path `design.md`) — a stale active-path test pin left by slice-093's archival. Outside `/drift-check` scope (archived slices are skipped) AND outside slice-096 scope (external-vault initiative / slice-094-095 domain). Surfaced for routing, not resolved here.

### Resolutions
- None required — vault and code aligned for the slice-096 surface.
