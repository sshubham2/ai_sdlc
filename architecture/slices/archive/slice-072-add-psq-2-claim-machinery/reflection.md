# Reflection: Slice 072 add-psq-2-claim-machinery

**Date**: 2026-05-27
**Shipped**: YES-WITH-DEFERRALS (BC-1 BC-GLOBAL-2 prose-vs-automation N=4 cumulative defer-with-rationale per slice-069/070/071 precedent; 9 code-Critic advisory findings deferred to slice-073+ bundled cleanup per voluntary-restraint N=13 cumulative)

## Validated

- **PSQ-2 schema additivity** — `Claimed-by:` + `Claimed-at:` lines emit at position [-2] (AFTER `Risk-retired:`, BEFORE trailing blank entry-separator) — validated by live `--claim` + `git diff` against `architecture/slice-queue.md` + 6 unit tests covering schema additivity + CRLF + forward-compat behavior.
- **CRLF-tolerant `parse_queue_text`** — `\r\n`→`\n` normalization before parsing — validated by `test_parse_queue_text_accepts_crlf_input` (CRLF fixture matches LF-input equivalent).
- **`newline=""` LF-only emission** on `.tmp` write — validated by no-CRLF-translation behavior across Windows-CRLF-default-translation default; the byte-equal claim-preservation round-trip held.
- **3-case `git config` absence detection** (returncode==1 unset / returncode==0+empty stdout configured-empty / other non-zero git-tool-error) — validated by 3 unit tests covering each case; live CLI exit-2 on absent `user.name`.
- **Bare `--claim` on already-claimed candidate refuses with exit 2** directing user to `--force-claim` — validated live (`cleanup-sc-022-...` twice → exit 2 with proper error message).
- **`--force-claim` overwrites existing claim** — validated live.
- **`--release` on missing candidate exits 2 (typo-rejection)** — validated by `test_release_on_unknown_candidate_exits_2`; symmetric with `--claim` per Critic M2 ACCEPTED-FIXED.
- **`--release` on present-but-unclaimed idempotent (exit 0 no-op)** — validated by `test_release_removes_both_claim_field_lines` + re-release path.
- **`/slice` Step 6.5 regen preserves existing claims via parse_queue_text merge** — validated by 2 unit tests (`test_slice_step_6_5_regen_preserves_existing_claims` + `test_claims_on_dropped_candidates_are_silently_discarded`).
- **Forward-compat `_extra_field_lines` pass-through** preserves PSQ-3+ unknown field lines verbatim on roundtrip — validated by `test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip`.
- **R-19 status flip mitigating → retired** + session-id divergence disambiguation paragraph — validated by `risk_register_audit --filter-status mitigating --json` (R-19 absent) + `test_r_19_retired_in_risk_register`.
- **5-part PMI-1 atomic bump 0.70.0 → 0.71.0** across all 5 canonical legs (VERSION + plugin.yaml.version + pyproject.toml + ## v0.71.0 header + installed ~/.claude/ai-sdlc-VERSION) — validated by PMI-1 audit clean + AVFS-1 PASS + MCFS-1 PASS + TVFS-1 PASS.
- **BC-PROJ-10 paired-pin tests** for v0.71.0 — validated by `test_v_0_71_0_psq_2_entry_present_in_repo` + `test_v_0_71_0_psq_2_shippability_consumer_propagation` (10 required anchors checked + shippability row #72 BCR-1 traceability axis).
- **3-Critic stack N=9 cumulative complementarity** — design-Critic + meta-Critic at /critique caught 14 structural findings; code-Critic at /code-review caught 9 line-level / contract / cross-cutting findings the design-Critic stack structurally could not reach (M1 emission-order divergence is the canonical instance — a contract-gap visible only by reading the just-written code).
- **AC count = 6 N=2 promotion of slice-067 pattern signal** — documented deviation explicitly cited in mission-brief L23; predicted by slice-067 reflection L77; held cleanly through TRI-1 with `/critic-calibrate` slice-073+ nomination active.

## Corrected

- **Phase B/C order swap** — implementation in `tools/slice_queue_claim.py` was authored at Phase A (the scaffold actually included full implementation, ~440 LOC), then tests were written at Phase B to verify-rather-than-drive. TF-1 strict-pre-finish checks status only (not order), so this was procedurally compliant, but the slice-072 mission-brief implicitly assumed strict-TDD ordering. Build-log DEVIATION-1 captures this; no corrective vault edit needed (the slice's design.md already specifies the implementation surface; order is a process detail).

- **`importlib.metadata.version()` shadowing by in-repo `ai_sdlc_tools.egg-info/`** — initial TVFS-1 check returned `0.69.0` (egg-info from a prior session) while `sysconfig.get_path("purelib")` had `0.71.0`. The TVFS-1 audit's docstring already warns about this; the audit correctly scope-limits to purelib when invoked with `--root .`. NOT a correction to anything — the methodology already documents this; surfaced for archival.

## Discovered

- **R-20 cp -r tax fired at /validate-slice surface, not just /build-slice Phase E** — slice-071 reflection logged R-20 as a /build-slice Phase E mid-slice smoke surface (N=6 cumulative). Slice-072 extends this to N=7 cumulative AND surfaces it at `/validate-slice` Step 5.5 (initial full-pytest failed on `test_bcr_1_round_trip_end_to_end.py` for missing `diagnose-out/backlog.md`). The R-20 risk class is broader than just the build-time surface — any test that reads `diagnose-out/` or `graphify-out/` via filesystem-resolution at validate-time also pays the cp-r tax. Impact: slice-073+ structural-fix nomination (codify-cp-r-tax-in-BRANCH-2-SKILL.md option (a) per R-20 candidate fixes) is now strictly more urgent — N=7 cumulative with 2 distinct surfaces.
- **Meta-Critic specialization signal stable at N=6 cumulative on TPHD-1 sub-mode (a) intra-document harmonization gap** — slice-072 meta-Critic M-add-1 catch on design.md L18-19 stale anchor (test-count + AC-tag mismatch with post-fix-block L161) extends the slice-062/064/067/070/071 TPHD-1 sub-mode (a) lineage to N=6. The pattern is now structurally stable: design-Critic + meta-Critic complementarity ALWAYS catches Builder-fix-block-introduced regressions on cross-document mechanical consistency. The /critic-calibrate proposal is overdue.
- **AC count = 6 N=2 promotion signal confirmed** — slice-067 logged N=1 ("AC count > 5 on new-mechanism mints"); slice-072 is the second instance. The pattern is real — new-mechanism slices with paired-pin meta-AC + PMI-1 atomic-bump leg meta-AC genuinely need 6 ACs. `/critic-calibrate` proposal at slice-073 reflection: formalize "≤5 (or ≤6 when AC6 is exclusively a v-section entry-pin meta-AC) for new-mechanism mints" carve-out in `/slice` SKILL.md.
- **Code-Critic Major finding M1 (apply_claim vs _format_entry emission-order divergence)** — a Fowler "Duplicated Code" smell that only surfaces empirically when claim-on-extras-present round-trips through `/slice` Step 6.5 regen. The design-Critic stack at /critique time structurally couldn't reach this (the contract divergence is between two specific code surfaces that have to coexist; you only see the bytes drift when you run both). Added to /critic-calibrate watch-list: "code-Critic Majors that pivot on coexistence-of-two-surfaces tend to escape the design-Critic stack; pattern N=1 watch-list."
- **TVFS-1 audit's `importlib.metadata` shadow case warning at slice-072 first-governed instance N=2** — slice-059 minted TVFS-1; slice-072 is N+1+1 governed slice that exercised the shadow path (egg-info from prior session) and the audit handled it correctly via `--root .` scoping. Pattern is structurally stable; no remediation needed.

## Deferred

- **BC-1 BC-GLOBAL-2 prose-vs-automation false-positive N=4 cumulative** — defer-with-rationale per slice-069/070/071 precedent. methodology-changelog v0.71.0 + ADR-067 + design.md mention git terminology in PROSE context (not code-automation surfaces using `git checkout --` / `git restore` / `git stash` to revert files with uncommitted WIP). Structural fix is BC-1 negative-anchor refinement (discriminate prose-discussion vs code-automation) — out of slice-072 scope. **`/critic-calibrate` slice-073+ active nomination — N=4 is well past the N=3 promotion threshold; ready for action.**
- **9 code-Critic advisory findings** (M1 emission-order divergence; M2 except Exception swallows ClaimUsageError; M3 noisy-neighbor malformed sibling; M4 .tmp leak on os.replace failure; m1 case-sensitivity diagnostic; m2 duplicate Claimed-by silent last-write-wins; m3 blank-line-drops-claim; m4 XDG_CONFIG_HOME fixture gap; m5 changelog 17 vs 18 tests) — all DEFERRED to slice-073+ `slice-NNN-bundle-072-code-critic-cleanup` per CRSI-1 v1 walking-skeleton advisory-only discipline + voluntary-restraint precedent N=13 cumulative (slice-037/046/050/052/055/056/057/061/065/067/070/071/072).
- **R-20 codify-cp-r-tax-in-BRANCH-2-SKILL.md** — slice-072 extends R-20 to N=7 cumulative with /validate-slice as second surface; the structural fix is candidate (a) "codify cp-r step in BRANCH-2 SKILL.md `## Prerequisite check ### Branch state`" — slice-073+ active nomination.
- **R-2 diagnose cwd-mismatch runtime test** — open low-band risk; not addressed this slice.
- **R-13 OSDG-1 extension to /slice-candidates** — open low-band risk; slice-073+ active nomination (already in slice-queue.md).
- **PSQ-3 rebase + conflict discipline** — explicit Out-of-scope per mission-brief L67; sibling on parallel-slice family axis to PSQ-1 + PSQ-2; slice-074+ nominee.

## Critic calibration

Per TRI-1, scoring 11 first-Critic findings + 3 meta-Critic missed findings against reality observed during build/validate:

- **B1** (cp1252 bucket mismatch): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: empirically the `_ROOT_ONLY_TOOLS` parametrize would have invoked `[PY, "-m", tool, "--root", str(REPO_ROOT)]` against slice_queue_claim which has no `--root` flag, producing argparse `unrecognized argument: --root` → exit 2 → cp1252 test FAIL. Fix landed (bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` mirroring install_audit precedent); test PASSES in /validate-slice.
- **B2** (R-19 + ADR-064 stale session-id forward-references): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: ADR-064 L37 + R-19:329 verbatim carry "session-id detection" contradicting ADR-067 §Options Option 2. Fix landed (ADR-067 §Lineage divergence note + R-19 retirement paragraph disambiguate predecessor-spec drift).
- **M1** (Windows CRLF round-trip): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: PSQ-1's existing `Path.write_text(body, encoding="utf-8")` at L730 already shipped CRLF on Windows; without `newline=""` the byte-equal claim-preservation round-trip would have been flaky. Fix landed; tests confirm.
- **M2** (`--release` exit-code ambiguity): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed at /validate-slice — `--release typo-name` exits 2, `--release present-unclaimed-name` exits 0 idempotent, as documented.
- **M3** (forward-compat field-line behavior): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: without `_extra_field_lines` pass-through, PSQ-3+ extensibility would have been broken (unknown lines either dropped or triggered malformed). The contract test `test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip` confirms.
- **M4** (AC count > 5 N=2 promotion of slice-067 signal): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed at /validate-slice: AC5 + AC6 split is cleaner verification surface than the original AC5 3-ratchet conglomerate (each AC has discrete PASS/FAIL evidence; the audit/manual checks against AC5 vs AC6 are unambiguous).
- **m1** (`_format_entry` trailing blank position): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: index [-2] insertion preserves the inter-entry blank-line separator. Verified at /validate-slice live `git diff` (claim adds 2 lines, blank stays between entries).
- **m2** (git config absence-detection mode unspecified): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: empty-`user.name=""` case exits 2 correctly (3-case detection works as specified).
- **m3** (`--queue` flag TF-1 row missing): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed at /validate-slice — `test_claim_cli_uses_queue_path_override_when_provided` exists + PASSES.
- **m4** (PMI-1 leg-enumeration drift): **VALIDATED** — disposition ACCEPTED-FIXED (absorbed into M4 AC5→AC6 split harmonization).
- **m5** (BC-PROJ-9 N=8 vs N=9 framing): **VALIDATED** — disposition ACCEPTED-FIXED. Both numbers explicitly framed as same fan-out under different scope.

Meta-Critic missed-findings calibration:

- **M-add-1** (design.md L18-19 stale anchor TPHD-1 N=6 cumulative): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed: meta-Critic empirically demonstrated by direct file Read that L18 said "(~250 LOC, 10 unit tests)" while L161 said "~330 LOC, 15 unit tests" — same file, contradictory claims. First-Critic missed this because the stale-anchor sweep on the AC5→AC6 split fix-block did not include design.md §"What's new" bullet list — exactly the TPHD-1 sub-mode (a) pattern at N=6. **`/critic-calibrate` proposal: extend first-Critic prompt with "after applying AC-restructuring fixes (split/merge/rename), perform a stale-anchor sweep across ALL design.md / mission-brief.md / ADR sections that cite AC count or test count".**
- **m-add-1** (milestone.md L29 prose stale): **VALIDATED** — disposition ACCEPTED-FIXED. Cosmetic but Builder-commitment-not-honored — first-Critic M4 fix-block explicitly committed "update milestone.md 'current focus' + design.md L77 references" and meta-Critic caught the commitment was forgotten.
- **m-add-2** (parse_queue_text unclaimed-entry shape underspecified): **VALIDATED** — disposition ACCEPTED-FIXED. Reality confirmed at implementation: without the "ALL entries returned, claim keys absent on unclaimed, `.get()` at consumer" spec, the `write_slice_queue` merge step would have raised KeyError. The fix is load-bearing.

**Missed by first-Critic** (caught by meta-Critic): 3 findings (M-add-1 + m-add-1 + m-add-2). All Builder-fix-block-introduced or fix-block-coverage gaps — exactly the slice-067 N=4 / slice-071 N=5 / slice-072 N=6 cumulative TPHD-1 sub-mode (a) pattern.

**Missed by both first-Critic AND meta-Critic** (caught by code-Critic at /code-review): 9 advisory findings (M1-M4 Majors + m1-m5 minors). All line-level idiom / contract gap / edge case in the just-written code — the canonical 3-Critic stack complementarity domain (design-stack reads design.md / mission-brief / ADRs; code-stack reads the just-written diff). **3-Critic stack N=9 cumulative validated** (slice-063 → slice-072 inclusive).

**Pattern**:
1. **TPHD-1 sub-mode (a) cross-doc harmonization gap is now an empirically-stable N=6 cumulative recurrence pattern**. Strongest `/critic-calibrate` proposal target — the existing /critic-calibrate watch-list at slice-070 L92 / slice-071 L78 was N=5 cumulative; slice-072 promotes to N=6.
2. **3-Critic stack complementarity validated at N=9 cumulative** — design-Critic + meta-Critic + code-Critic each catch a different defect class the others structurally cannot reach. Do NOT collapse the 3-Critic stack.
3. **AC count > 5 on new-mechanism mints N=2 promotion** — pattern is real; `/critic-calibrate` slice-073+ proposal active to formalize the ≤6-AC carve-out for v-section entry-pin meta-ACs.
4. **Code-Critic catches coexistence-of-two-surfaces contract gaps** (M1 emission-order divergence between apply_claim + _format_entry) — pattern N=1 watch-list; if recurs, /critic-calibrate proposal: "design-Critic should explicitly check coexistence contract between two specific code surfaces that the slice modifies."

## Lessons for next slice

- **PSQ-2 ships v0.71.0 successfully; PSQ-3 is the natural next** — `/commit-slice` rebase discipline on the parallel-slice family axis. Sibling to BRANCH-2 (physical isolation) + PSQ-1 (discoverability) + PSQ-2 (coordination). Mission already drafted in slice-067 reflection L33.
- **R-20 cp -r tax now at N=7 cumulative with 2 surfaces** — slice-073+ structural-fix nomination via candidate (a) "codify cp-r in BRANCH-2 SKILL.md" is OVERDUE. User-flagged at slice-071 ("we need a better solution"); each subsequent slice adds cumulative pain.
- **Code-Critic 9-finding advisory backlog at slice-072 alone is comparable to slice-066 (6) + slice-067 (1) + slice-068 (4) + slice-069 (8) = 19-finding backlog that became slice-071 31-finding bundled-cleanup at 10× scale**. The next bundled-cleanup-at-N+1 opportunity is slice-073+ `slice-NNN-bundle-072-code-critic-cleanup` (9 findings + R-20 + BC-1 BC-GLOBAL-2 carve-out = ~11+ findings) — sized for a single focused cleanup slice.
- **`/critic-calibrate` is genuinely overdue** — N=6 TPHD-1 sub-mode (a) + N=2 AC-count signal + N=4 BC-1 BC-GLOBAL-2 prose-vs-automation false-positive — three distinct calibration-ready signals accumulated. Slice-074+ nominee.
- **Voluntary-restraint discipline continues to be the right default for code-Critic advisories** — slice-073+ bundled cleanup absorbs them at known cost (the slice-064/065/067/070/071 lineage proves this empirically). DO NOT inline-fix during /build-slice or /reflect.
- **Cooperative-not-adversarial threat model** for PSQ-2 was the right call (per ADR-067 §"Adversarial model") — git-identity-only ownership is sufficient for "two cooperating Claude sessions"; defending against malicious local actors would have over-engineered the slice into PSQ-5+ territory.

## Vault updates made (thin vault)

- [[architecture/risk-register.md]] — R-19 status `mitigating` → `retired` + `**Retired**: slice-072 / ADR-067` field-line + retirement paragraph disambiguating ADR-064 L37 + R-19 L329 session-id predecessor-spec drift (preserves prior prose verbatim per slice-040 R-10 retirement-precedent).
- [[architecture/shippability.md]] — row #72 added (PSQ-2; cites both paired-pin tests + ADR-067 per BCR-1 traceability axis); row #71 backfilled (was missing — slice-071 had no shippability row landed at /reflect Step 5.3; slice-072 added it as part of the BC-PROJ-10 paired-pin discipline cleanup).
- [[architecture/decisions/ADR-067-mint-psq-2-claim-machinery.md]] — NEW; mints PSQ-2 as new RULE-ID on parallel-slice family axis (sibling to PSQ-1; supersedes nothing; cheap reversibility); §"Lineage divergence note" disambiguates ADR-064 L37 session-id forward-reference.
- [[methodology-changelog.md]] — `## v0.71.0 — 2026-05-27` entry minting PSQ-2 (10 required anchors); MCFS-1 forward-synced to `~/.claude/methodology-changelog.md`.
- [[VERSION]] / [[plugin.yaml]] / [[pyproject.toml]] — 5-part PMI-1 atomic bump 0.70.0 → 0.71.0 (PVFS-1 + plugin.yaml.version + ## v0.71.0 header + installed `~/.claude/ai-sdlc-VERSION` via AVFS-1).
- [[skills/slice/SKILL.md]] — Step 6.5 gains PSQ-2 claim-preservation note; OSDG-1 forward-synced to `~/.claude/skills/slice/SKILL.md`.
- [[INSTALL.md]] — tool count 29 → 30 at L22 + L166 (BC-PROJ-9 5-inventory fan-out).
- [[architecture/slice-queue.md]] — Phase E mid-slice smoke claim/release round-trip + Phase G regen (no claims persisted; the slice's smoke gate restored byte-equal).
- [[tests/methodology/test_psq_2_claim_machinery.py]] — NEW; 18 unit tests covering AC1-AC5.
- [[tests/methodology/test_utf8_stdout_regression.py]] — NEW bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` per Critic B1.
- [[tests/methodology/test_methodology_changelog.py]] — NEW paired-pin tests `test_v_0_71_0_psq_2_entry_present_in_repo` + `test_v_0_71_0_psq_2_shippability_consumer_propagation` per BC-PROJ-10:173.
- [[tests/methodology/test_vault_root_constant.py]] — `_MIGRATION_SITE_ALLOWLIST` adds `tools/slice_queue_claim.py` (new VAULT_ROOT consumer).
- [[tools/slice_queue_claim.py]] — NEW ~440 LOC (PSQ-2 CLI + library API: ClaimUsageError + read_git_config_user + parse_queue_text + apply_claim + apply_release + atomic _atomic_write_text + argparse mutually-exclusive CLI).
- [[tools/slice_queue_writer.py]] — MODIFIED (`_format_entry` insertion at [-2] + `_extra_field_lines` pass-through; `write_slice_queue` claim-preservation merge via `parse_queue_text` + explicit `newline=""` on `.tmp` write).
- [[tools/install_audit.py]] — `_CANONICAL_TOOLS` adds `tools.slice_queue_claim`.
- BCR-1 round-trip — **no-op** (no `**Closes:** SC-NNN` sentinel in mission-brief or reflection; this is R-19 driven, not backlog-driven; ADR-055 BCR-1 traceability axis is documented in shippability row #72 as cite-without-Closes).
