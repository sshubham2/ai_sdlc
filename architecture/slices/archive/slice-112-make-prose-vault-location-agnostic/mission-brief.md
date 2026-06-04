# Slice 112: make-prose-vault-location-agnostic

**Mode**: Standard
**Estimated work**: ~1 day (MEDIUM, bounded pilot) — the novel cost is minting the prose-vault-seam convention + flipping `vault_flip_prose_inventory.py` into a converted-aware enforcement gate; the pilot prose conversion is mechanical. The bulk skill conversion is deliberately a follow-on (Step-5 split), so this stays inside the ≤1-day limit. If the convention design or the forward-sync of the converted guarded files pushes past 1 day, fallback split: convention + audit + `CLAUDE.md` only here, `agents/critique.md` + `slice`/`reflect` in the next cut (flag at TRI-1). (INSTALL.md/README.md are carved out entirely — see AC3 / Out-of-scope.)
**Risk retired**: contributes to [[risk-register#R-32]] flip-readiness — makes the **prose surface** (the last surface hardcoding `architecture/`/`diagnose-out/`; 313 operational literals across `skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md`, `README.md`, inventoried by slice-107) **vault-location-agnostic** so the eventual M4 flip is config-only. Does **NOT** retire R-32 (R-32 retires at the physical move). Prose analog of slice-110's `make-pipeline-vault-location-agnostic` (tests) and slice-106/098 (production code).
**Test-first**: true  (per TF-1 — mirrors slice-107 (the inventory tool this extends) + slice-110 (the agnostic-prep sibling), both Test-first; the converted-aware enforcement gate is deterministic, no-AST line-based logic that is more defect-prone than average and must be proven non-vacuous by mutation before the bulk follow-on relies on it — AP-3 / AP-5)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The prose surface is the **last** surface in the AI SDLC pipeline that hardcodes the vault location: 313 operational `architecture/`/`diagnose-out/` literals across the methodology prose (skills, agents, root docs), inventoried by slice-107 but never rewritten. Production code (106/098), the queue/claim writers (109), and the test suite (110) are already routed through the `VAULT_ROOT` seam; only prose still names `architecture/` directly. This slice mints a **prose-vault-seam convention** (a token + the resolution rule stated once), flips `vault_flip_prose_inventory.py` from a *rewrite-checklist* into an *enforce-no-new-hardcoded* ratchet, and converts a **bounded pilot** (`CLAUDE.md` + a self-sufficient `agents/critique.md`; skills deferred to a follow-on per dual-Critic TRI-1) to prove the pattern end-to-end. The convention is **flip-neutral**: a converted reference resolves to `architecture/` today (no behaviour change pre-flip) and to the external store post-flip with zero further prose edits — shrinking the M4 flip to a config-only move. The bulk skill conversion is an explicit, checklist-driven follow-on. **NOT** in scope: the physical flip itself, and the concrete-new-path rewrite (which would be premature drift — the vault is still physically at `architecture/`).

## Acceptance criteria

> **Revised post dual-Critic TRI-1 (2026-06-04)**: pilot reduced to `CLAUDE.md` + a self-sufficient `agents/critique.md`; `<diagnose-out>` token NOT minted (no seam — B5); a 7-class carve-out taxonomy added; the enforcement ratchet hardened (M3). Skill conversion (`slice`/`reflect`/bulk) deferred to a follow-on. See critique.md / critique-review.md / [[decisions/ADR-105]].

1. The **`<vault>` prose-seam convention** is minted and documented ([[decisions/ADR-105]]): the placeholder `<vault>/` names the vault root in operational prose — fitting the existing `<wt_path>`/`<main>`/`slice-NNN-<name>` idiom — with its **resolution rule** (per [[decisions/ADR-065]] + [[decisions/ADR-085]]: env `AI_SDLC_VAULT_ROOT` → git-common-dir config → default `architecture/`) stated **exactly once** in `CLAUDE.md`. **`<diagnose-out>` is NOT minted** (no seam in `_vault_paths.py` — B5); `diagnose-out/` stays concrete. **Resolver-context scope** (M-add-1): the convention applies where the rule is in context — `CLAUDE.md` + `skills/**/SKILL.md` (main agent) + a self-sufficient `agents/*.md` (embeds the rule). ADR-105 records the decision + the **7-class carve-out taxonomy** (INSTALL/README; definitional; historical anchors; worktree-composed `<wt_path>/architecture/…`; per-slice active-folder; `slice-queue.md`; `diagnose-out/`). **Governance: ADR-only / MEPD-1 EXCLUDE**.
2. `tools/vault_flip_prose_inventory.py` gains a **converted-file one-way ratchet** (folded into `--strict`): exit 2 on any `rewrite-at-flip` literal in a `_CONVERTED_FILES` member — keyed on **forward-slash relpaths** matching `Occurrence.path` (a `\`-form must NOT match — load-bearing negative test, M3), and **INDEPENDENT of the re-pinnable `_BASELINE_SHA256`** (it reds even when the baseline is re-pinned to "cover" the regression). Proven **non-vacuous by mutation** (AP-5): inject a literal into a converted file AND re-pin the baseline → exit 2 still fires; every marker check region/line-anchored (AP-1).
3. The **pilot set** — `CLAUDE.md` + `agents/critique.md` — has its operational vault refs replaced by `<vault>/`, each resolving to the same physical `architecture/` path as before (**no pre-flip behaviour change**). `agents/critique.md` carries an **embedded self-sufficient `<vault>` note** (the Critic subagent lacks CLAUDE.md — M-add-1) and is **forward-synced** to `~/.claude/` (byte-identical convert → CAD-1 EOL-agnostic equality green). Definitional literals (the resolution rule's own `architecture/`) stay concrete as **plain-prose `doc-example`**, NOT a `_DISPOSITION` line-key entry (M2 + M-add-2). The agent's `:125` `slice-queue.md` + `:260` active-folder refs are **carved out** (classes 6/5). Exact convertible-vs-carve-out split + the **re-pin fan-out** (`_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`, shippability rows 113 + 117 — B4 / FBCD-1 (c)) are **APED-1-derived via `--json`** at build, not estimated.
4. **Mixed state + resolver-context proven safe**: a converted file and a not-yet-converted file coexist with both resolving to `architecture/` today; the converted `agents/critique.md` is self-sufficient (resolves `<vault>` from its own embedded note, NOT from CLAUDE.md); the full methodology suite + `/validate-slice` pass (incl. CAD-1 green; the op-gate floors UNTOUCHED — CLAUDE.md/agents are not op-gate-scanned).
5. The **remainder is tracked for the follow-on**: the not-yet-converted operational prose literals are enumerated as a complete worklist (the tool's `--json`) — the **exact** count (no estimate, m2) — so the skill-conversion follow-on has no orphaned site, and that follow-on (which OWNS the op-gate floor re-pin + the skill instances of carve-out classes 4/5/6 + the BCR-1 anchor repoint) is registered (slice-queue candidate + a reflection deferred-note).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0; mirrors slice-107/110.) Each AC maps to failing tests written BEFORE implementation; statuses PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row. Exact test names/paths are design-adjustable; the mapping is fixed up front.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_claude_md_states_resolution_rule_exactly_once | PASSING |
| 1 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_adr_105_present_and_lists_seven_carve_out_classes | PASSING |
| 1 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_diagnose_out_token_not_minted | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_converted_file_regression_exits_2 | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_ratchet_independent_of_repinned_baseline | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_converted_files_membership_forward_slash_only | PASSING |
| 3 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_pilot_files_zero_rewrite_at_flip_after_conversion | PASSING |
| 3 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_agent_critique_embeds_self_sufficient_vault_note | PASSING |
| 4 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_seam_token_resolves_to_architecture_default | PASSING |
| 5 | unit | tests/methodology/test_prose_vault_seam_convention.py | test_followon_remainder_worklist_complete | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | convention documented | `CLAUDE.md` carries the resolution-rule block exactly once; the new ADR exists under `architecture/decisions/` and names the operational-only scope + preserved historical anchors; `pytest tests/methodology/test_prose_vault_seam_convention.py -k resolution_rule` green |
| 2 | enforcement gate fail-closed | `python -m tools.vault_flip_prose_inventory --strict` (converted-aware) exits 0 on the pilot-converted corpus; inject a hardcoded `architecture/x.md` into a converted file → exit 2; the not-yet-converted allowlist is listed via `--json` |
| 3 | pilot converted, no behaviour change | every operational literal in the pilot files is the seam token (grep shows 0 bare `architecture/`/`diagnose-out/` operational literals in those files); the documented resolution yields `architecture/` by default; `$PY -m tools.critique_agent_drift_audit --repo-root .` clean + the converted skills' OSDG-1 drift tests green (forward-sync verified) |
| 4 | mixed state safe | full methodology suite green with the pilot converted + the rest still hardcoded; a fixture pairs a converted + an un-converted reference and asserts both resolve to `architecture/` |
| 5 | remainder tracked | `python -m tools.vault_flip_prose_inventory --json` enumerates the complete not-yet-converted worklist (count == 313 minus the pilot-converted count); the follow-on slice is a slice-queue candidate + a reflection deferred-note |

## Must-not-defer

- [ ] **Forward-sync `agents/critique.md` IN THIS SLICE** (CAD-1): the converted in-repo agent whose installed `~/.claude/agents/critique.md` copy is not updated is DRIFT and fails the slice. Convert + sync atomically; byte-identical convert → CAD-1 EOL-agnostic equality stays green.
- [ ] **Agent self-sufficiency** (M-add-1): a Critic SUBAGENT does NOT inherit `CLAUDE.md`, so the converted `agents/critique.md` MUST embed its own one-line `<vault>` resolution note — else the subagent reads an unresolvable token. AC4's resolver-context proof covers this.
- [ ] **Definitional literals stay concrete via plain-prose, not `_DISPOSITION`** (M2 + M-add-2): the resolution rule's own `architecture/` default is stated as plain prose (no backticks) → `doc-example`; a `_DISPOSITION` 5-tuple entry would silently drop the exemption on any future reword of the line (the key embeds the line text).
- [ ] **No pre-flip behaviour change** (the no-flip safety contract): every converted reference MUST resolve to the SAME physical `architecture/` path it did before. Default suite outcome byte-for-byte equivalent (mirrors slice-110).
- [ ] **Enforcement ratchet fails CLOSED + INDEPENDENT of the baseline** (R-7 + M3): a converted file with a hardcoded operational literal MUST red the gate (exit 2) EVEN IF the actor re-pins `_BASELINE_SHA256` to match; `_CONVERTED_FILES` keyed on forward-slash relpaths (a `\`-form must not silently miss). Prove by mutation targeting independence, not assertion (AP-5).
- [ ] **Re-pin fan-out is complete** (B4 / FBCD-1 (c) / AP-10): `_BASELINE_SHA256` + `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]` + `EXPECTED_TOTAL` + `architecture/shippability.md` rows 113 + 117 move together; exact total APED-1-derived via `--json`, never estimated.
- [ ] **Region/line-anchored detection** (AP-1): the ratchet anchors to the matched literal's line/region; never `marker in whole_file_text`.
- [ ] **UTF8-STDOUT-1** (AP-8): preserve `_stdout.reconfigure_stdout_utf8()` across the changes.
- [ ] **Shippability / PMI-1 / INST-1**: the tool gains no new flag (ratchet folded into `--strict`), but keep `architecture/shippability.md` (rows 113/117 + any new row) consistent (RPCD-1 / SCPD-1).
- [ ] **Preserve historical anchors** (slice-107 carve-out, taxonomy class 3): ADR citations, `archive/slice-*` Glob anchors, changelog version refs are NOT operational literals — never rewritten; the gate never demands it.

## Out of scope

- The **physical M4 flip itself** — move of `architecture/`+`diagnose-out/` to the external store, `git rm --cached`, the `VAULT_ROOT` default flip, the `/commit-slice` RETIRE no-op, draining R-32.a/R-32.b. This slice only makes the prose flip-ready; R-32 retires at the move.
- **ALL skill conversion** (`skills/slice/SKILL.md`, `skills/reflect/SKILL.md`, the bulk ~17) — deferred to a **skill-conversion follow-on** (AC5 registers it; TRI-1 dispositions B1/B2/B3/M1). That follow-on OWNS: the op-gate floor re-pin + `_OP_ALLOWLIST` re-hash (B2, a deliberate AP-12 gate-loosening); the worktree-composed-path structural carve-out (B1); the `slice-queue.md` carve-out (M1); and repointing `test_bcr_1_backlog_round_trip.py:108,186` in the SAME slice it converts `slice:73` (B3 / AP-13). This slice converts only `CLAUDE.md` + `agents/critique.md`.
- **The `<diagnose-out>` token** — NOT minted this slice (no seam in `_vault_paths.py` — B5). `diagnose-out/` literals stay concrete; the token + its seam are a later slice's / the flip's deliverable.
- **`INSTALL.md` + `README.md`** — carve-out class 1 (ADR-105): user-facing, read before CLAUDE.md/the vault exist; definitional descriptions of the concrete default. They keep `architecture/`, rewritten at the flip.
- **Vault-internal prose** (`architecture/**/*.md` — ADRs, `methodology-changelog.md`, slice folders): a distinct surface that relocates *with* the vault; its relative cross-links largely survive the move (same out-of-scope boundary as slice-107).
- The **production + tests Python surfaces** — already agnostic via slice-106/098 (`vault_flip_readiness_audit`) and slice-110 (test suite). Untouched here.
- **Concrete-new-path rewrites** (`architecture/…` → `~/.aisdlc/<project>/…`): explicitly rejected — premature drift while the vault is still physically at `architecture/`.

## Dependencies

- Prior slices: [[slice-107-inventory-vault-flip-prose-surface]] — the prose inventory + classifier this slice extends into an enforcement gate (its `--json` output is the worklist); [[slice-110-make-pipeline-vault-location-agnostic]] — the agnostic-prep pattern for the test surface, mirrored here for prose; [[slice-106-route-project-frame-synth-via-vault-root]] — the production-code agnostic-routing analog; [[slice-068-add-vault-root-constant]] + [[slice-093-add-external-vault-support]] — the `VAULT_ROOT` seam + 3-tier resolution the prose token must mirror.
- Vault refs: [[decisions/ADR-065]] (env seam), [[decisions/ADR-085]] (3-tier resolution + git-common-dir config), [[decisions/ADR-091]]/[[decisions/ADR-092]] (the readiness/inventory classification model), [[architecture/shippability.md]] (the inventory tool's row).
- Risk register: [[risk-register#R-32]] — this slice clears the prose precondition of the flip; it does NOT retire R-32.

## Mid-slice smoke gate

At ~50% (after minting the convention + extending the inventory tool to converted-aware enforcement + converting the pilot, before forward-sync + the full suite):
```
python -m tools.vault_flip_prose_inventory --json     # expect: converted pilot files show 0 hardcoded operational literal; not-yet-converted allowlist fully enumerated
python -m tools.vault_flip_prose_inventory --strict    # expect: exit 0 (converted-aware) on the pilot; inject a literal into a converted file → exit 2
pytest tests/methodology/test_prose_vault_seam_convention.py tests/methodology/test_vault_flip_prose_inventory.py
```
Expected: the pilot files carry only the seam token; the gate is fail-closed on a converted file; the remainder is a complete worklist. If a converted file still shows a hardcoded operational literal, OR the gate does not red on the injected mutation → STOP, fix the convention/enforcement, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes (vault claims still match code; the convention ADR is recorded)
- [ ] Mid-slice smoke still passes (no regression)
- [ ] `$PY -m tools.critique_agent_drift_audit --repo-root .` clean + every converted guarded skill's OSDG-1 drift test green (forward-sync complete)
- [ ] `tools/test_first_audit.py --strict-pre-finish` green — all Test-first-plan rows PASSING
- [ ] Enforcement gate proven non-vacuous by mutation (AP-5); no pre-flip behaviour change (default suite outcome-equivalent)
- [ ] No new TODOs / FIXMEs / debug prints
