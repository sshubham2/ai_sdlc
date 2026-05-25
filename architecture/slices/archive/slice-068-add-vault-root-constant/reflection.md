# Reflection: Slice 068 add-vault-root-constant

**Date**: 2026-05-25
**Shipped**: YES-WITH-DEFERRALS (4/4 ACs PASS; full pytest 944/0; all audits clean; 5 /code-review advisory findings + 1 /critique m2 ACCEPTED-PENDING all deferred to follow-on slices per BCR-1 SC-NNN backlog mechanism)

## Validated

- **Single-seam refactor is structurally sound** — design.md's choice of leaf-utility module + module-level constant + env-var override held empirically. Full pytest 944/0 with zero regressions across 8 migration sites + 5 EXCLUDED-prose sites confirms the "pure mechanical refactor, no behavior change" claim.
- **Two-marker convention works in practice** — `# VAULT_ROOT-routed (slice-068)` + `# NOT VAULT_ROOT-routed (slice-068) — error-message prose` distinction cleanly separates filesystem-resolving from prose-asserting sites. Audit test `test_no_orphan_architecture_literal_in_migrated_tools` enforces it.
- **Read-at-import-time + consumer-freeze cascade is correct production semantic** — `test_consumer_constants_are_frozen_at_first_import` empirically demonstrates `tools.slice_queue_writer._INDEX_MD_REL` does NOT update on in-process monkeypatch of `tools._vault_paths.VAULT_ROOT`. Documented as a first-class contract in ADR-065 §Decision rather than implicit assumption.
- **Leading-underscore-helper precedent** — naming `tools/_vault_paths.py` per `tools/_stdout.py` precedent correctly skipped PMI-1 inventory enumeration (29 tools count unchanged in PMI-1 audit — the `_list_actual_tools` filter at `tools/plugin_manifest_audit.py:148` auto-excludes leading-underscore files; verified post-build).
- **MEPD-1 EXCLUDE posture** — no methodology-changelog v0.70.0 entry, no PMI-1 bump. The slice shipped at v0.69.0 unchanged; all forward-sync audits (MCFS-1 / AVFS-1 / TVFS-1) remained clean because there was nothing to forward-sync. Correct per design.

## Corrected

- **NONE in the design.md / ADR-065 / mission-brief axis** — every design claim survived contact with build empirically; no vault file required correction this slice. (The mission-brief AC4 "7-module allowlist" was corrected to 8 during /critique fix-block per B1, not during /reflect; reflection captures it as resolved-in-band.)
- **/code-review M1 spec-vs-code drift identified but NOT corrected this slice** — design.md L25 + mission-brief.md L54 explicitly promise `test_vault_paths_module_is_leaf` regression-pin that does NOT exist in `tests/methodology/test_vault_root_constant.py`. The invariant holds empirically at slice-068 ship time (verified by code-review), so this isn't a current defect; it's a missing regression guard for future edits. Filed as SC-028 in `diagnose-out/backlog.md` for a small follow-on slice rather than corrected in-band (would have required a full Builder fix-block post-validation, expanding slice scope past its stated boundary).

## Discovered

- **N=4 cumulative gitignored-vault-vs-worktree conflict** (build-log.md DEVIATION) — BRANCH-2 worktrees don't carry gitignored content; tests that read `architecture/slices/` or `diagnose-out/backlog.md` from `REPO_ROOT` fail in worktrees until the gitignored trees are copied in. Slice-067 hit this at N=3; slice-068 at N=4. **Methodology adjustment OR slice-069 acceleration warranted** — this is now a recurring class with structural cost (every BRANCH-2 slice pays the `cp -r` tax + risk of forgetting). Added to lessons-learned as a methodology-axis pattern; not adding to risk-register since slice-069 (next in the user-intent chain) structurally fixes it via un-gitignore.
- **Three-Critic stack complementarity validated at N=2 cumulative** (slice-067 N=1; slice-068 N=2) — design-Critic + meta-Critic + code-Critic cover distinct, complementary defect classes (see Pattern below). Worth surfacing to `/critic-calibrate` at next periodic run.
- **Spec-prose-claims-a-test-that-isn't-in-TF-1-plan** is a fresh class neither /critique nor /critique-review caught — design-Critic could add a probe: "for every design.md prose mention of `test_*` by name, verify a TF-1 plan row exists". Worth a `/critic-calibrate` proposal.

## Deferred

- **SC-027 — slice-067 PSQ-1 raw-dict-leak in `tools/slice_queue_writer.py` blast-radius renderer** — per /critique m2 ACCEPTED-PENDING + /critique-review m2 severity adjustment. Filed to `diagnose-out/backlog.md` this `/reflect` step with `Severity: medium`, `Blast: medium`, `Reversibility: cheap`, `Effort: small` per multi-consumer-artifact rule (PSQ-1 architectural premise is multi-session shared visibility per ADR-064). Lands in: a future small slice (likely slice-070+ alongside or after `rename-architecture-to-sdlc-and-track-in-git`).
- **SC-028 — slice-068 `test_vault_root_constant.py` test-quality hardening bundle** — per /code-review M1 + m1 + m2 + m3 advisory findings. Filed to `diagnose-out/backlog.md` this `/reflect` step. Bundles: (a) M1 missing `test_vault_paths_module_is_leaf` (design.md L25 + mission-brief L54 promised); (b) m1 idempotency regex under-coverage (only catches 1 of 4 pre-migration shapes); (c) m2 freeze-pin assertion gap (passes on no-op monkeypatch); (d) m3 two-marker convention regex coverage gap (substring-in-prose unmarked + untested). Lands in: a future small slice; not blocking.
- **m4 PEP-8 blank line in `tools/supersede_audit.py:53-54`** — purely cosmetic. NOT filed as SC; defer to next janitorial pass touching that file.
- **NOT a BCR-1 round-trip**: slice-068 is user-intent-driven (from `/query-design` 2026-05-25), NOT backlog-driven; no `**Closes:** SC-NNN` sentinel anywhere in mission-brief or this reflection. Per BCR-1 prose: absent sentinel → no-op clean for the `**Addressed:**` round-trip mechanism. The two NEW SC entries (SC-027, SC-028) are this slice's CONTRIBUTIONS to the backlog, not closures of existing SC items.

## Critic calibration

Per TRI-1, scoring each finding via the disposition in `critique.md` `## Triage` table + `critique-review.md` + `code-review.md` + reality observed during build/validate:

**Design-Critic findings (`/critique`):**

- **B1** (9th site `tools/build_checks_integrity.py:78` missed): **VALIDATED** — disposition ACCEPTED-FIXED; the missed site was genuinely real (re-grep confirmed); allowlist swept to 8 across all spec surfaces; empirically verified by `test_migration_site_allowlist_pinned`.
- **M1** (consumer-freeze cascade hazard): **VALIDATED** — disposition ACCEPTED-FIXED; the freeze contract documented as production-correctness semantic in ADR-065; `test_consumer_constants_are_frozen_at_first_import` empirically pins it. (Note: /code-review m2 surfaced that THE TEST has an assertion gap — not flagged as VALIDATED for the freeze contract itself; the contract holds, the test pin needs hardening.)
- **M2** (false `conftest.py L37` precedent citation): **VALIDATED** — disposition ACCEPTED-FIXED; the citation was genuinely fabricated; removed from ADR-065 + design.md; concern subsumed by M3 scope-back.
- **M3** (R-15 backstop atrophy via scope-back): **VALIDATED** — disposition ACCEPTED-FIXED via scope-back; `tests/methodology/conftest.py` + 15 other tests/ files DEFERRED; R-15 audit regex at `test_resolve_slice_dir.py:233` UNCHANGED + preserved.
- **m1** (argparse default-eval freeze): **VALIDATED** — folded into M1's broader freeze-contract documentation.
- **m2** (SC-NNN entry for slice-067 PSQ-1 raw-dict-leak): **VALIDATED** at /reflect — SC-027 filed in `diagnose-out/backlog.md` with the /critique-review severity adjustment applied.

**Meta-Critic findings (`/critique-review`):**

- **All 6 first-Critic findings CONFIRMED** (no SUSPICIOUS) — meta-Critic agreement is itself VALIDATED.
- **M-add-1** (two-marker convention asymmetry between mission-brief AC2/must-not-defer #2/Verification-plan row 2 and design.md TF-1 row 4): **VALIDATED** — disposition ACCEPTED-FIXED; Builder swept three sibling-cell mission-brief sites in second fix-block; the two-marker convention is now consistently enumerated across all spec surfaces. **Strengthens slice-067 N=3 → N=4 cumulative pattern** — "Builder applies multi-finding fixes without sweeping all sibling-cell sites" is now well-established meta-Critic specialization signal.
- **m2 severity adjustment** (low/small → medium/medium): **VALIDATED** at /reflect — SC-027 filed with adjusted scoring per multi-consumer-artifact rule.

**Code-Critic findings (`/code-review`):**

- **M1** (missing `test_vault_paths_module_is_leaf` regression-pin promised in design.md L25 + mission-brief.md L54): **MISSED by design-Critic + meta-Critic** — both Critics passed without noticing the design.md prose claim of a test that wasn't enumerated in the TF-1 plan. This is a fresh class: "spec-prose-claims-a-test-that-isn't-in-TF-1-plan". Code-Critic caught it by direct AST inspection of the test module. **Calibration signal for `/critic-calibrate`**: add a probe to the design-Critic (or meta-Critic) prompt — "for every design.md prose mention of `test_*` function name, verify a TF-1 plan row exists".
- **m1** (idempotency regex under-coverage): **MISSED by design-Critic + meta-Critic** — design-Critic discusses the regex idempotency CONTRACT in M3 scope-back discussion, but neither Critic inspected the actual regex shape vs the 4 distinct pre-migration literal shapes the migration covered. Code-Critic specialty.
- **m2** (freeze-pin assertion gap — test passes on no-op monkeypatch): **MISSED by design-Critic + meta-Critic** — design-Critic's M1 discussion ended at "add a TF-1 row pinning the freeze semantic"; neither Critic audited the actual test body's assertion quality. Code-Critic specialty.
- **m3** (two-marker convention regex coverage gap — substring-in-prose cases unmarked + untested): **MISSED by design-Critic + meta-Critic** — both Critics discussed the two-marker convention at the design level; neither examined how the audit regex would match the actual line shapes. Code-Critic specialty.
- **m4** (PEP-8 blank line cosmetic): **MISSED by all three Critics** in a different sense — would be over-reach for any Critic to flag; janitorial-class finding. Code-Critic surfaced it as informational.

**Missed by Critic** (things that surfaced during build/validate that NONE of the three Critics flagged):

- The N=4 cumulative gitignored-vault-vs-worktree conflict (surfaced at /build-slice Phase E full-pytest collection failure). Design-Critic + meta-Critic could have probed: "this slice runs in BRANCH-2 worktree but reads `architecture/slices/` via `_resolve_slice_dir` at module-level — will the worktree have `architecture/`?" — the gitignored convention is documented in `.gitignore:11` + `principles.md:71` + CLAUDE.md, so this is in-vault-discoverable. Worth a `/critic-calibrate` proposal: add a dimension to design-Critic for "if slice runs in worktree, does it depend on gitignored state that won't propagate?". **Strengthens the slice-067 reflection's existing "first-governed-slice N+1 probe" recommendation** — this would be the formal codification of that probe.

**Pattern observation** (for future tuning):

1. **Three-Critic complementarity validated at N=2 cumulative** (slice-067 N=1 + slice-068 N=2). Design-Critic catches conceptual + cross-doc citation + missing-cases-in-spec. Meta-Critic catches Builder-fix-block-introduced regressions + sibling-cell-sweep gaps + empirical re-execution. Code-Critic catches test-quality + regex-coverage + spec-vs-code drift + cosmetic. The three are structurally complementary; **collapsing any one would empirically miss a defect class**. Pattern stable.
2. **Builder fix-block sweep discipline** (slice-067 N=3 → slice-068 N=4 cumulative): when a Critic surfaces a multi-finding fix-block (e.g., B1 + M1 + M2 + M3 + m1 here), the Builder must sweep ALL sibling-cell sites (mission-brief AC + must-not-defer + Verification-plan + design.md + ADRs). Both slice-067 and slice-068 had the Builder sweep design.md but miss one or more mission-brief sibling sites; meta-Critic caught both. **Candidate `/critic-calibrate` proposal**: "first-Critic fix dispositions should explicitly enumerate the cross-document sweep surface, not leave it implicit."
3. **Spec-prose-claims-a-test-that-isn't-in-TF-1-plan**: fresh class surfaced by /code-review M1 in slice-068. Worth a /critic-calibrate proposal for design-Critic dimension addition.
4. **Gitignored-vault-vs-worktree probe**: should become a design-Critic dimension per slice-067 N=3 + slice-068 N=4 cumulative recurrence. /critic-calibrate candidate.

## Lessons for next slice

- **slice-069 (`rename-architecture-to-sdlc-and-track-in-git`) is now the structural fix for the N=4 recurring gitignored-vault pattern** — accelerating it shrinks blast radius for every BRANCH-2 slice that follows. The user-intent chain captured at `/slice` time (slice-068 → slice-069 → slice-070 → slice-071) has slice-069 as the natural next slice; this reflection reinforces that ordering.
- **For slice-069 specifically**: the rename is now a 1-line `_DEFAULT` flip in `tools/_vault_paths.py` (from `"architecture"` to `".sdlc"`) PLUS `.gitignore` edit PLUS the philosophy ADR. The slice-068 seam structurally simplified slice-069's blast radius from 14 files to 3. Original mission-brief estimate of LARGE → likely revisable to MEDIUM at slice-069 `/slice` time.
- **For slice-068 follow-on (SC-028 test-quality hardening)**: bundle the 4 /code-review advisory findings into one small slice — `harden-slice-068-test-vault-root-constant`. SMALL effort; addresses 1 missing test + 3 test-body quality gaps.
- **For /critic-calibrate next periodic run**: 4 proposals queued — (a) design-Critic dimension for "design prose claims a test not in TF-1 plan"; (b) design-Critic / meta-Critic probe for "if slice runs in worktree, does it depend on gitignored state"; (c) the slice-067 N=3 → N=4 cumulative "Builder fix-block sweep" calibration signal; (d) code-Critic patterns now have N=2 cumulative data to inform any prompt refinement.

## Vault updates made (thin vault — small list)

- `architecture/slices/_index.md` — regenerated at Step 6 (archive); slice-068 added to "Most recent 10"; this reflection's "Lessons for next slice" pulled into "Aggregated lessons".
- `architecture/slices/archive/_index.md` — slice-068 appended to chronological catalog at Step 6.
- `architecture/shippability.md` — row #68 added with critical-path test `test_migration_site_allowlist_pinned` (the single test that would catch a slice-068 regression first: any future tool importing VAULT_ROOT without being in the allowlist, or any allowlist member that stops importing VAULT_ROOT, fails this test).
- `architecture/lessons-learned.md` — slice-068 chronological entry appended.
- `diagnose-out/backlog.md` — two new SC entries added (SC-027 slice-067 PSQ-1 raw-dict-leak, SC-028 slice-068 test-quality hardening bundle).
- `graphify-out/graph.json` — refreshed at Step 5.5 to reflect new `tools/_vault_paths.py` + 8 migrated tools.
- NO `methodology-changelog.md` edit (MEPD-1 EXCLUDE posture per design — pure mechanical refactor; no rule mint). NO `plugin.yaml` / `VERSION` / `~/.claude/ai-sdlc-VERSION` bump. NO `pyproject.toml` bump. The slice ships at v0.69.0 unchanged.
- NO `risk-register.md` edit (no R-NN retirement this slice; the N=4 gitignored-vault pattern is methodology-axis not risk-register-axis; slice-069 fixes structurally).
- NO ADR supersession (ADR-065 is a fresh mint; supersedes nothing).
