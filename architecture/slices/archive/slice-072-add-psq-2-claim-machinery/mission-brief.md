# Slice 072: add-psq-2-claim-machinery

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-19 (`mitigating` → `retired`) — `architecture/slice-queue.md` freshness becomes a hint, not a load-bearing collision-safety signal, once a `Claimed-by:` field is the authoritative ownership marker per entry
**Test-first**: true  <!-- TF-1: schema contract is multi-session shared state; pin failing tests before implementing to prevent schema drift mid-build -->
**Walking-skeleton**: false  <!-- this is a feature extension on PSQ-1, not a thinnest-end-to-end vertical -->
**Exploratory-charter**: false  <!-- mechanical schema + CLI work; no novel UX surface to explore -->

## Intent

After PSQ-2, two Claude sessions can claim and execute parallel-safe candidates from `architecture/slice-queue.md` without colliding. Each entry gains optional `Claimed-by:` (git config `user.name` + `user.email`, hard-required — no anonymous-claim default) and `Claimed-at:` (ISO-8601 UTC) field lines written atomically by a new `tools/slice_queue_claim` CLI; `/slice` Step 6.5 regeneration preserves existing claims on still-present candidate names so the helper remains idempotent under parallel sessions. Closes R-19's freshness-dependence axis — queue staleness ceases to be a collision-safety lever once ownership is recorded on the entry itself.

## Acceptance criteria

1. `architecture/slice-queue.md` schema additively extends each candidate entry with optional `**Claimed-by:** <user.name> <user.email>` and `**Claimed-at:** <ISO-8601 UTC>` field lines; PSQ-1's existing 5 fields (`Source`, `Blast-radius`, `Parallel-safety`, `Effort`, `Risk-retired`) preserved verbatim in order; new fields appear immediately AFTER `Risk-retired:` when present, absent when the entry is unclaimed; `parse_queue_text` is permissive to unknown forward-compat field lines (preserves them via `_extra_field_lines` pass-through on roundtrip per PSQ-3+ extensibility per ADR-067 §Consequences); writes via `Path.write_text(..., newline='')` for LF-only byte-deterministic emission; reads tolerate `\r\n` and `\n` input.
2. A new CLI `$PY -m tools.slice_queue_claim --claim <candidate-name>` writes the two claim field lines atomically via `.tmp` sibling + `os.replace()`; user identity is read via `git config user.name` + `git config user.email` with exit-code-based absence detection (subprocess `check=False`; `returncode == 1` → unset; `returncode == 0 + stdout.strip() == ""` → configured-empty; both rejected; other non-zero → git-tool-error); absent → loud `exit 2` error naming the missing config key (no silent fallback to anonymous or `$USER`); the CLI carries a `--queue <path>` override (testing seam — default `<VAULT_ROOT>/slice-queue.md`); a bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` cp1252 regression test mirrors the `test_install_audit_survives_cp1252_with_u2192` precedent (NOT bucketed into `_ROOT_ONLY_TOOLS` — slice_queue_claim has no `--root` flag).
3. `--release <candidate-name>` removes both `Claimed-by:` and `Claimed-at:` lines (idempotent — `--release` on a present-but-unclaimed candidate = exit 0; `--release` on a not-in-queue candidate = exit 2 typo-rejection, symmetric with `--claim`); `--force-claim <candidate-name>` overwrites an existing claim (stale-claim recovery escape-hatch); bare `--claim` on an already-claimed candidate → loud `exit 2` directing the user to `--force-claim`.
4. `/slice` Step 6.5 regeneration (via `tools.slice_queue_writer.write_slice_queue`) PRESERVES existing claims: a claim on a candidate name that survives into the new top-10 is carried forward; claims on candidates dropped from the new top-10 are silently discarded (regenerable on every `/slice` invocation); new candidates start unclaimed; forward-compat unknown field lines are preserved on roundtrip alongside the known claim fields.
5. R-19 status flipped `mitigating` → `retired` in `architecture/risk-register.md` with citation to slice-072 + ADR-067; retirement paragraph explicitly disambiguates the predecessor-spec drift — R-19 Mitigation paragraph + ADR-064 L37 both anticipated `session-id detection` per ADR-064; ADR-067 §"Options considered" Option 2 + §Decision rule that out — PSQ-2 ships git-identity-only ownership. Predecessor prose preserved verbatim as historical record per slice-040 R-10 retirement-precedent; ADR-067 §Decision is authoritative.
6. methodology-changelog gains a `## v0.71.0 — 2026-05-27` entry minting **PSQ-2** as a NEW rule (sibling on parallel-slice family axis; refines no existing rule; supersedes nothing); 5-part PMI-1 atomic bump 0.70.0 → 0.71.0 covers the canonical legs `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` (PVFS-1) + `## v0.71.0` header + installed `~/.claude/ai-sdlc-VERSION` (AVFS-1); paired entry-pin tests `test_v_0_71_0_psq_2_entry_present_in_repo` + `test_v_0_71_0_psq_2_shippability_consumer_propagation` present and PASSING; shippability row #72 added.

> **AC count = 6 documented deviation from ≤5-AC rule** — per slice-067 reflection L26 + L77 (Pattern signal N=1: "AC count > 5 on new-mechanism mints"), slice-072 is the **N=2 promotion instance** on new-mechanism mints whose methodology-changelog v-entry + paired entry-pin tests + PMI-1 atomic bump cannot fold cleanly into AC1–AC5. AC5 (R-19 retirement) + AC6 (v-section meta + PMI-1 + paired-pin entry tests) split per Critic M4 ACCEPTED-FIXED. Slice-073 reflection should propose `/critic-calibrate` action to formalize "≤5 (or ≤6 when AC6 is exclusively a v-section entry-pin meta-AC)" carve-out in `/slice` SKILL.md.

## Test-first plan

Each AC maps to one or more failing tests written BEFORE implementation. Statuses progress PENDING → WRITTEN-FAILING → PASSING through the slice lifecycle. `/build-slice` Step 6 (pre-finish) runs `tools/test_first_audit.py --strict-pre-finish` and refuses if any row is non-PASSING.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_schema_appends_claim_fields_after_risk_retired_when_claimed | PASSING |
| 1 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_schema_omits_claim_fields_when_unclaimed | PASSING |
| 1 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_parse_queue_text_accepts_crlf_input | PASSING |
| 1 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip | PASSING |
| 2 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claim_cli_writes_user_name_and_email_from_git_config | PASSING |
| 2 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claim_cli_exits_2_on_missing_user_name_or_user_email | PASSING |
| 2 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claim_cli_exits_2_on_configured_empty_user_name | PASSING |
| 2 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claim_cli_atomic_write_via_tmp_sibling_and_os_replace | PASSING |
| 2 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claim_cli_uses_queue_path_override_when_provided | PASSING |
| 2 | unit | tests/methodology/test_utf8_stdout_regression.py | test_slice_queue_claim_survives_cp1252_with_u2192 | PASSING |
| 3 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_release_removes_both_claim_field_lines | PASSING |
| 3 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_release_on_unknown_candidate_exits_2 | PASSING |
| 3 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_force_claim_overwrites_existing_claim | PASSING |
| 3 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_bare_claim_on_already_claimed_exits_2 | PASSING |
| 4 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_slice_step_6_5_regen_preserves_existing_claims | PASSING |
| 4 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_claims_on_dropped_candidates_are_silently_discarded | PASSING |
| 5 | unit | tests/methodology/test_psq_2_claim_machinery.py | test_r_19_retired_in_risk_register | PASSING |
| 6 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_71_0_psq_2_entry_present_in_repo | PASSING |
| 6 | unit | tests/methodology/test_methodology_changelog.py | test_v_0_71_0_psq_2_shippability_consumer_propagation | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Schema additive + CRLF tolerance + forward-compat | Inspect `architecture/slice-queue.md` post-claim and post-release; verify field order + PSQ-1 5-field block byte-equal modulo new optional lines; assert `parse_queue_text` accepts CRLF input and preserves unknown forward-compat field lines on roundtrip |
| 2 | Claim CLI + git config + cp1252 | `$PY -m tools.slice_queue_claim --claim add-rebase-and-conflict-discipline` then re-read queue → `Claimed-by:` line shows the resolved git user; remove `git config user.email` in a fixture → CLI exits 2 with named-key message; configured-empty `user.name = ""` also exits 2; bespoke cp1252 regression test passes |
| 3 | Release + force-claim semantics | CLI invocations covering claim → release → claim → bare-claim-fails-exit-2 → force-claim-overwrites; `--release <unknown>` exits 2; `--release <present-unclaimed>` exits 0 idempotent; assertions on the queue file's diff at each step |
| 4 | `/slice` Step 6.5 preservation | Claim a candidate, invoke `write_slice_queue` with the same top-10 list, assert claim survives byte-equal; drop the candidate from the list, assert claim is gone (no orphan claim lines); unknown forward-compat field lines on a surviving candidate also preserved |
| 5 | R-19 retired with disambiguation | `$PY -m tools.risk_register_audit --filter-status mitigating` does not list R-19; retirement paragraph at R-19 section end disambiguates the session-id forward-reference predecessor-spec drift; ADR-064 untouched (append-only ADR discipline) |
| 6 | methodology v0.71.0 entry + 5-part PMI-1 bump + paired-pin tests + shippability row | `$PY -m tools.plugin_manifest_audit` clean post-bump; `methodology-changelog.md` v0.71.0 entry present; `test_v_0_71_0_psq_2_entry_present_in_repo` + `test_v_0_71_0_psq_2_shippability_consumer_propagation` PASS; `$PY -m tools.shippability_runner architecture/shippability.md` ends at 72/72 PASS |

## Must-not-defer

- [ ] Atomic claim writes via `.tmp` sibling + `os.replace()` (mirror PSQ-1's atomicity discipline at `tools/slice_queue_writer.py` `write_slice_queue`)
- [ ] Loud `exit 2` on absent `git config user.name` OR `user.email` — no silent fallback to `$USER` / anonymous / hostname
- [ ] Claim preservation across `/slice` Step 6.5 regeneration (deterministic merge: claims on surviving candidate names carry forward; claims on dropped candidates discarded)
- [ ] Force-claim is a distinct flag (`--force-claim`); plain `--claim` on an already-claimed candidate MUST refuse with exit 2 — never silently overwrite
- [ ] ADR-067 minting PSQ-2 + methodology-changelog `## v0.71.0` entry + 5-part PMI-1 atomic bump 0.70.0 → 0.71.0 + paired entry-pin tests + shippability row #72
- [ ] OSDG-1 / mini-CAD forward-sync if any guarded SKILL.md is touched (Step 6.5 prose in `skills/slice/SKILL.md` is OSDG-1 guarded — re-sync installed `~/.claude/skills/slice/SKILL.md` post-edit per OSDG-1)
- [ ] Authorization: claim CLI MUST NOT touch any file other than `architecture/slice-queue.md` (no `git config --set` calls; READ-only consumption of git config)
- [ ] Logging: claim/release/force-claim emit a single stdout line summarizing the resulting state (`CLAIMED add-foo by Name <email> at 2026-05-27T...Z` etc.) so cross-session audit is human-readable

## Out of scope

- Session-id detection beyond `git config user.name + user.email` (user-explicit direction; no PID/hostname/UUID overlay)
- Cross-machine atomic locking (PSQ-2 is same-machine local-sessions only; cross-machine coordination is PSQ-3+ territory)
- Stale-claim auto-expiry by elapsed time (force-claim is the manual escape-hatch; auto-expiry deferred until a real stale-claim incident emerges)
- `/commit-slice` rebase discipline (separate slice on the parallel-slice family axis — slice-queue PSQ-3 nominee)
- Renaming the slice-067 queue entry `add-LOCAL-slice-queue-claim-state-machine` (slice-072 IS that entry's discharge; the entry drops out of the queue naturally when slice-072 becomes active)

## Dependencies

- Prior slices: [[slice-066-add-worktree-per-slice-discipline]] (BRANCH-2 — physical isolation), [[slice-067-add-parallel-slice-queue-output]] (PSQ-1 — queue schema parent)
- Vault refs: [[ADR-063]] (BRANCH-2), [[ADR-064]] (PSQ-1; explicitly says queue format is "a stable on-disk contract that PSQ-2 claim machinery will extend additively")
- Risk register: [[risk-register#R-19]] (the risk this slice retires)
- Existing helper: `tools/slice_queue_writer.py::write_slice_queue` (PSQ-1; will gain a claim-preservation merge step) + `_format_entry` (will gain optional claim-line emission)
- New module: `tools/slice_queue_claim.py` (PSQ-2 CLI + library API — claim / release / force-claim)

## Mid-slice smoke gate

At ~50% of build (after CLI scaffolding + schema extension land, before Step 6.5 preservation logic and methodology-changelog entry):

```
$PY -m tools.slice_queue_claim --claim add-rebase-and-conflict-discipline
git diff architecture/slice-queue.md
$PY -m tools.slice_queue_claim --release add-rebase-and-conflict-discipline
git diff architecture/slice-queue.md
```

Expected:
- After `--claim`: two new lines (`Claimed-by:` + `Claimed-at:`) appear under the entry; nothing else in the file moves; queue file ends with a newline
- After `--release`: the diff returns to clean (round-trip is reversible)
- Stdout shows one human-readable line per invocation

If fails: STOP, diagnose. The most likely failure mode is non-atomic write leaving a half-written queue, or claim-line placement breaking PSQ-1's existing 5-field block.

## Pre-finish gate

- [ ] All 6 acceptance criteria PASS with evidence captured in `validation.md`
- [ ] Must-not-defer list fully addressed (each item closed with citation)
- [ ] `/drift-check` passes (vault and code aligned post-schema-extension)
- [ ] Mid-slice smoke still passes (claim/release round-trip clean against the live queue)
- [ ] No new TODOs / FIXMEs / debug prints
- [ ] `$PY -m tools.test_first_audit --strict-pre-finish` reports all 18 TF-1 rows PASSING
- [ ] `$PY -m tools.plugin_manifest_audit` clean post-PMI-1 atomic bump 0.70.0 → 0.71.0
- [ ] `$PY -m tools.risk_register_audit --filter-status mitigating` no longer lists R-19
- [ ] `$PY -m tools.shippability_runner architecture/shippability.md` reports 72/72 PASS (post-row-add)
- [ ] `$PY -m tools.branch_workflow_audit` clean (BRANCH-2 worktree on `slice/072-add-psq-2-claim-machinery`)
- [ ] OSDG-1 drift guard PASSes for any touched guarded SKILL.md (`skills/slice/SKILL.md` Step 6.5 prose, if amended for claim-preservation language)
- [ ] CAD-1 + PMI-1 + RR-1 + WIRE-1 + ETC-1 + CSP-1 + SUP-1 + LINT-MOCK-1/2/3 audits clean
- [ ] Full pytest baseline (was 966 at slice-071 ship): expect ~984 (966 + 18 new TF-1 rows); zero regressions
