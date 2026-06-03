# Slice 107: inventory-vault-flip-prose-surface

**Mode**: Standard
**Estimated work**: ~1 day (MEDIUM, upper end) — the classifier + 11 Test-first tests are bounded; the variable cost is hand-curating the `needs-human` residue (the expanded rule-4 operational-verb/sink set auto-classifies most of the 318; the genuinely-ambiguous residue drives the disposition table). If curation pushes past 1 day, fallback split: tool+enumeration+baseline here, full residue-disposition in a follow-up (flagged at TRI-1).
**Risk retired**: contributes to [[risk-register#R-32]] flip-readiness — inventories + drift-guards the **prose surface** (~318 `architecture/` + `diagnose-out/` location-literals across `skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md`, `README.md`) so the M4 flip has a complete, regression-pinned prose checklist. Does **NOT** retire R-32 (R-32 retires at the flip itself, M4). M1 sibling of slice-106.
**Test-first**: true  (per TF-1 — flipped from false at dual-review M-add-2: the directly-mirrored slice-100 + slice-102 were both Test-first; this classifier is MORE defect-prone (no AST, line-based fence-state) so the mirror's "deterministic + naturally testable" rationale applies a fortiori — see Test-first plan below)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

The production-code (`tools/*.py` + `skills/**/*.py`) and tests (`tests/**/*.py`) surfaces are already inventoried + drift-guarded by `tools/vault_flip_readiness_audit.py` (slice-100 / [[ADR-091]]; slice-102 / [[ADR-092]]). The **prose surface** — ~318 hardcoded `architecture/…` + `diagnose-out/…` literals across `skills/**/SKILL.md` (292), `agents/*.md` (16), root `CLAUDE.md` (7), `INSTALL.md` (2), `README.md` (1) — has **no AST** and is entirely uncovered by that audit. When the external-shared-vault flip (M4) relocates `architecture/` + `diagnose-out/`, every *operational* prose instruction that names that location goes stale, while *historical anchors* (ADR citations, `archive/slice-*` Glob-discoverability anchors, changelog version refs) must be **preserved**. This slice ships a deterministic, fail-closed **inventory** of that prose surface — classifying each literal rewrite-at-flip vs. historical-anchor/preserve vs. doc-example, anything ambiguous failing closed — with a pinned baseline + `--strict` drift gate, so the flip has a complete prose checklist that can never silently drift. **Read-only inventory; NO prose is rewritten here** (that is M4).

## Acceptance criteria

1. A new tool `tools/vault_flip_prose_inventory.py` enumerates **all 318** `architecture/` + `diagnose-out/` location-literals (Builder-verified count; **all matches per line** via `re.finditer`, NOT one `re.search`/line) across the prose surface — `skills/**/SKILL.md`, `agents/*.md`, root `CLAUDE.md`, `INSTALL.md`, `README.md` — via a **boundary-free** matcher (`(?:architecture|diagnose-out)/`, NOT the anchored readiness regex — B1/dual-review: the real `_SLASHED_RE` catches only **69** of 318, dropping **249** incl. 216 backtick-wrapped inline-code paths + operational `:(exclude)architecture/...` git-pathspecs), emitting `path:line:col` + the matched literal + assigned class, with `--json` / `--strict` / `--repo-root` flags and UTF8-safe stdout (mirrors the `vault_flip_readiness_audit` CLI + exit-code contract: 0 clean, 2 gate, 1 usage error).
2. Each occurrence is classified by a **documented, context-aware ordered ruleset** into a small taxonomy (`rewrite-at-flip` | `historical-anchor` | `doc-example` | `needs-human`); the tool **exits 2** when any `needs-human` is present (fail-closed). **`doc-example` is RESERVED for genuine plain-prose mentions ONLY** — an inline-code / fenced / git-pathspec vault path NEVER silently becomes `doc-example` (B2). **AS-BUILT (user-ratified recalibration, build-log 2026-06-03):** an in-code / fenced / operational vault path defaults to `rewrite-at-flip` (the dominant LIVE-reference case — on the M4 checklist, B2's goal); `needs-human` fires ONLY for a genuine preserve-marker on an in-code line (a true rewrite-vs-preserve conflict). Final distribution **316 `rewrite-at-flip` / 0 `historical-anchor` / 2 `doc-example` / 0 `needs-human`**. The `needs-human` bucket is resolvable to empty via an explicit **in-tool disposition** (`_DISPOSITION`), **NOT** by editing prose (M4 / out of scope) — the current corpus needs none.
3. A pinned in-module baseline + a methodology test (`tests/methodology/test_vault_flip_prose_inventory.py`) freeze the current `rewrite-at-flip` + `needs-human` classified set; `--strict` exits 2 on any drift — so a new/changed prose literal cannot enter the corpus unclassified and silently. **AS-BUILT (forced by AC5/M1, build-log 2026-06-03):** the baseline is pinned as an in-module **SHA-256** (`_BASELINE_SHA256`) of the sorted multiset, NOT inlined slashed-path tuples (which `readiness_audit` would flag, tripping slice-106) — identical gate behavior, full inventory via `--json`.
4. The classifier is proven **non-vacuous by mutation** (AP-5): a fixture mutation that changes a literal's surrounding context flips its class (or trips the gate); every marker detector is **region/line-anchored, never a whole-file substring scan** (AP-1); the disposition key disambiguates BOTH cross-line duplicates (`test_no_ambiguous_duplicate`, M2) AND intra-line multi-matches via column-offset (`test_no_intra_line_ambiguous_multimatch`, M-add-1 — `code-review.md:103`'s 5 same-line matches are the fixture).
5. Full methodology suite green; the new tool is enumerated in `plugin.yaml` (PMI-1) + `tools/install_audit.py` (INST-1), carries its `architecture/shippability.md` row (RPCD-1 / SCPD-1), and introduces **NO new `[production] must-rewrite` literal** into slice-106's `vault_flip_readiness_audit` baseline (disjoint-blast-radius preservation).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0; flipped to Test-first at dual-review M-add-2 to mirror slice-100/102.) Each AC maps to failing tests written BEFORE implementation; statuses PENDING → WRITTEN-FAILING → PASSING. `/build-slice` Step 6 runs `tools/test_first_audit.py --strict-pre-finish` and refuses any non-PASSING row.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_enumerates_full_corpus_318_all_matches_per_line | PASSING |
| 1 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_bare_vault_dir_arg_residual_enumerated | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_inline_code_routes_rewrite_not_doc_example | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_doc_example_reserved_for_plain_prose | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_anchor_plus_incode_routes_needs_human_exit_2 | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_baseline_pinned | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_per_class_total_count_floor | PASSING |
| 4 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_classifier_mutation_flips_class | PASSING |
| 4 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_no_ambiguous_duplicate | PASSING |
| 4 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_no_intra_line_ambiguous_multimatch | PASSING |
| 5 | unit | tests/methodology/test_vault_flip_prose_inventory.py | test_disjoint_no_new_production_must_rewrite | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | prose surface enumerated | `python -m tools.vault_flip_prose_inventory --json` lists `path:line` + literal + class for every match across the 5 prose globs; spot-check counts vs. `grep -rohE "(architecture\|diagnose-out)/"` (~318 raw) |
| 2 | fail-closed classification | every occurrence carries a class; force an unclassifiable fixture → routes to `needs-human`, exit 2; drive corpus `needs-human` → empty via the in-tool disposition map (no prose edits), exit 0 |
| 3 | baseline pinned + drift-gated | `python -m tools.vault_flip_prose_inventory --strict` exits 0 on the pinned corpus; `pytest tests/methodology/test_vault_flip_prose_inventory.py` green; inject a synthetic prose literal → `--strict` exits 2 |
| 4 | classifier non-vacuous | mutate one fixture literal's context (fenced-code ↔ historical-anchor marker) → its class flips / gate trips; revert → restored |
| 5 | suite + manifests + disjointness | `python -m tools.plugin_manifest_audit` + `python -m tools.install_audit` clean; new shippability row present; `python -m tools.vault_flip_readiness_audit --strict` still **exit 0** (no new production literal) |

## Must-not-defer

- [ ] **Fail-closed `needs-human`** (B2): an unclassifiable / ambiguous prose literal MUST surface (exit 2), never silently dropped or default-bucketed. In particular an **inline-code / fenced / git-pathspec** vault path with no operational or historical-anchor signal routes to `needs-human`, **NOT** `doc-example` (`doc-example` is reserved for genuine plain-prose mentions only).
- [ ] **Complete match (B1, all matches/line)**: the matcher is boundary-free `(?:architecture|diagnose-out)/` scanned with `re.finditer` (all matches per line — 24 lines carry >1 match) — it MUST enumerate the 216 backtick-wrapped inline-code paths + the operational git-pathspec literals (`:(exclude)architecture/...` in `skills/code-review/SKILL.md`) the real anchored `_SLASHED_RE` (only 69/318) drops. The ONLY honest-contract residual is the bare-no-slash args — **7** `graphify vault architecture` (bare `architecture`) PLUS the symmetric bare-`diagnose-out` operational mentions (m-add-1: Builder greps `\bdiagnose-out\b` not-followed-by-`/` across the 5 globs, folds operational hits in or confirms empty) — all enumerated + pinned by `test_bare_vault_dir_arg_residual`.
- [ ] **UTF8-STDOUT-1** (AP-8): call `_stdout.reconfigure_stdout_utf8()` first — the inventory prints non-ASCII (`→`, `—`, paths).
- [ ] **Region/line-anchored marker detection** (AP-1): never `marker in whole_file_text`; anchor every class-decision to the matched literal's line/region.
- [ ] **No self-pollution of the readiness baseline** (M1): the new tool references vault dir names ONLY as bare-segment frozenset members or `|`-joined regex source — **never** as a `/`-BinOp operand or `Path(...)`/`.glob(...)` arg (which `readiness_audit` classifies `must-rewrite-before-flip` → trips the **parallel** slice-106 baseline). Verified by `vault_flip_readiness_audit --strict` exit 0 at BOTH mid-slice AND pre-finish.
- [ ] **PMI-1 / INST-1 enumeration in the SAME slice**: a tool added without `plugin.yaml` + `install_audit.py` entries trips both gates (and per R-29 can be install-invisible) — enumerate explicitly, do not defer.

## Out of scope

- The **production + tests Python surfaces** — already inventoried by `tools/vault_flip_readiness_audit.py` (slice-100 / 102); this slice does **NOT** modify that tool (keeps blast radius disjoint from slice-106's `_BASELINE` re-pin).
- **Vault-internal prose** (`architecture/**/*.md` — ADRs, `methodology-changelog.md`, slice folders): a distinct surface that relocates *with* the vault; its relative cross-links largely survive the move. Not this slice.
- The actual prose **REWRITE** / the flip itself (M4): physical move of `architecture/` + `diagnose-out/`, flipping the `VAULT_ROOT` default, `git rm --cached`, final prose edits.
- `tools/project_frame_synth.py` routing — the parallel **slice-106** (M1 sibling).
- Any **auto-fix / auto-rewrite** of a literal — this slice is inventory + drift-gate only.

## Dependencies

- Prior slices: [[slice-100-add-vault-flip-readiness-audit]] (the production/tests inventory this mirrors for prose — same CLI/exit-code/baseline contract), [[slice-102-vault-flip-readiness-tests]] (the baseline-pin + surface-filter + mutation-proof pattern), [[slice-068-add-vault-root-constant]] (the `VAULT_ROOT` seam the tool's own paths route through), [[slice-093-add-external-vault-support]] (capability-without-flip contract).
- Parallel sibling: **slice-106-route-project-frame-synth-via-vault-root** (M1 sibling — disjoint core blast radius; only soft-overlap is the append-only `architecture/shippability.md` + `plugin.yaml` rows — coordinate at merge, not at build).
- Vault refs: [[decisions/ADR-091]] (readiness classification model), [[decisions/ADR-092]] (two-surface production/tests split — this slice adds **prose** as a third surface), [[decisions/ADR-065]] (env/seam).
- Risk register: [[risk-register#R-32]] (concurrent-write / flip gate — this slice clears one of its prose preconditions).

## Mid-slice smoke gate

At ~50% (after the enumerator + classifier ruleset work, before pinning the baseline + writing the drift test):
```
python -m tools.vault_flip_prose_inventory --json     # expect: every prose literal across the 5 globs enumerated + classified; remaining needs-human surfaced (exit 2) until dispositioned
python -m tools.vault_flip_readiness_audit --strict    # expect: exit 0 — the new tool added NO production must-rewrite literal (disjoint from slice-106)
```
Expected: the prose corpus is fully enumerated (boundary-free matcher = **318** occurrences, all-matches-per-line, == the `grep -rohE "(architecture|diagnose-out)/"` raw count — B3) and the production readiness baseline is unperturbed. The spot-check asserts the tool's OWN count **== 318** (== that grep); the real anchored `_SLASHED_RE` catches only **69** (the 216 inline-code paths are unmatched) and is NOT the comparison baseline. A single-`re.search`-per-line scan would report 286 and FAIL this check (M-add-1). If readiness `--strict` reds: the new tool introduced a production literal — STOP, fix the path-construction, don't continue.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] `python -m tools.vault_flip_readiness_audit --strict` exits 0 (M1 — no new `[production] must-rewrite` literal from the new tool; re-checked at pre-finish, not only mid-slice)
- [ ] `test_no_ambiguous_duplicate` + `test_no_intra_line_ambiguous_multimatch` + `test_bare_vault_dir_arg_residual` green (M2 + M-add-1 + B1 residual pinned)
- [ ] `tools/test_first_audit.py --strict-pre-finish` green — all Test-first-plan rows PASSING (TF-1, flipped at M-add-2)
- [ ] No new TODOs / FIXMEs / debug prints
