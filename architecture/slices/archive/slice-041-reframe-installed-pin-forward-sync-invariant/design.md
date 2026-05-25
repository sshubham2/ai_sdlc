# Design: Slice 041 reframe-installed-pin-forward-sync-invariant

**Date**: 2026-05-18 (**rev-3** — post 2× BLOCKED + slice-030A/031 non-convergence pivot + TRI-1 re-ratification; supersedes rev-1's "32 fns/empty-allowlist" and rev-2's "leg-drop the cross-module pin" — both empirically falsified)
**Mode**: Standard
**Split-lineage label**: "030C" (numeric folder per R-6; prose label only)
**RULE-ID minted**: **MCFS-1** — methodology-changelog.md **v0.53.0**

> **Why rev-3**: rev-1 assumed "essential = the 32 `_entry_present_*`" (false — 34 unique incl. a cross-module pin). rev-2 assumed leg-drop reclassifies the cross-module pin `clean` (false — `classify_fn` is an *unordered cross-expression subset test*; the pin keeps `.claude` from a retained `Path.home()/".claude"/"skills"/"diagnose"` line + `methodology-changelog.md` from a retained in-repo surface). Both reviewers reasoned about `_ESSENTIAL_SHAPES` instead of executing `classify_fn`. rev-3 adopts the **charter-literal** design (`risk-register.md` L90: *"intentional-installed allowlist, the read **registered** not **absent**"*) — DR-1-verified by execution: registered set cardinality = **1**, R-4 retireable, no relocation.

## Strategy (charter-faithful, DR-1-verified by execution)

Two distinct essential populations, two distinct treatments:

1. **The in-`tests/methodology/test_methodology_changelog.py` essential fns** (28 `_entry_present_in_repo_and_installed` + 5 `_entry_names_*`/`_supersession`): their `.claude` token comes **only** from the installed-changelog read-leg (their in-repo leg is `read_file("methodology-changelog.md")` — no `.claude`). **Decouple = drop only that read-leg.** DR-1 executed this over all 37 currently-essential fns in that module: **0/37 remain essential** (each → `segs={'methodology-changelog.md'}` → `clean`, the lone token failing the 2-token shape). The whole-file forward-sync these legs redundantly half-asserted is re-homed to MCFS-1 (strictly stronger).
2. **The cross-module `tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces`** (slice-019 LAYER-EVID-1 N=6-surface byte-equality pin): its installed-changelog read is **intentional and protective**, not incidental, and provably cannot be made `clean` by leg-drop while retaining its in-repo changelog surface (which LAYER-EVID-1 requires). It is **REGISTERED** in a non-empty `_REGISTERED_INSTALLED_READERS` with rationale — *accounted-for*, exactly what the R-4 charter chartered. Its body is **untouched** (all N surfaces retained).

Post-rev-3 essential set = exactly `{the cross-module pin}` ⊆ registered ⇒ SCMD-1 exit 0 ⇒ R-4 retireable (DR-1-verified cardinality).

**Scope-cut (TRI-1-ratified)**: the `_entry_present_*`→`_entry_present` rename is **OUT of slice-041** — DR-1-verified orthogonal to R-4 (R-4 retirement depends on the read-leg disposition, not test-fn names; `test_critique_agent.py:1424` is prefix-only/rename-safe; no structural enforcer asserts the `_in_repo_and_installed` suffix). It carries a 41-changelog-line + 27-shippability + ~17-ADR/lessons/index frozen-history blast radius into append-only shipped history — a separate **identifier-truth slice**. Consequence consciously accepted (slice-035: decided, not discovered): post-slice-041 the decoupled `_entry_present_in_repo_and_installed` fns' names temporarily over-claim (they no longer read installed); the chartered follow-up rename slice realigns all uniformly (incl. the new v0.53.0 pin).

## What's new

- `tools/methodology_changelog_forward_sync.py` — **MCFS-1** gate (BCI-1-analogue): in-repo `methodology-changelog.md` content-equal **modulo line endings** to installed `~/.claude/methodology-changelog.md`. Deterministic, non-opt-out, attributed refusal.
- `tests/methodology/test_methodology_changelog_forward_sync.py` — MCFS-1 regression suite: synced⇒0; divergent fixture⇒HALT 1; installed-absent⇒WARN 0; CRLF-only⇒NOT a FAIL (EOL-DRIFT-1 parity); CSP-1 behaviour-parity vs `tests/skill_drift_equality.py::_normalized_sha256`; **M-add-1 relocation proof** (MCFS-1 symbols absent from `tools.shippability_decoupling_audit._cited()` over the real catalog).
- `_REGISTERED_INSTALLED_READERS: frozenset[str] = frozenset({"tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces"})` in `tools/shippability_decoupling_audit.py` — **non-empty**, registers exactly the slice-019 LAYER-EVID-1 cross-module pin with an inline rationale comment. Key form = the exact audit-emitted file-path-qualified `::`-selector (DR-1 flag).
- methodology-changelog.md **v0.53.0** entry minting **MCFS-1**; new entry-pin `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` (existing naming convention retained per the scope-cut) with an **in-repo-only body** so it classifies `clean` (M3).
- New ADRs: [[ADR-042]] (forward-sync re-home — rev-3 scope), [[ADR-043]] (SCMD-1 essential-class → **non-empty** registered allowlist — rev-3).

## What's reused

- `tools/build_checks_integrity.py` — BCI-1 structural template + its **`/build-slice` Step 6 non-opt-out, ungated** wiring point (verified: BCI-1 is in build-slice Step 6's unconditional checklist, runs every slice regardless of rule promotion — silent-disable-proof; m1).
- `tests/skill_drift_equality.py::_normalized_sha256` (EOL-DRIFT-1 / [[ADR-033]]) — MCFS-1 implements the same 1-line CRLF→LF normalization locally + a CSP-1 behaviour-parity regression test ([[ADR-033]] home untouched — no supersession; no tools→tests import).
- `tools/shippability_decoupling_audit.py` — SCMD-1 (`classify_fn`/`_cited`/`_ESSENTIAL_SHAPES`/`audit()`). `classify_fn`/`_ESSENTIAL_SHAPES`/`_reachable_path_segments` **unchanged** (the unordered-subset semantics are correct as-is; rev-2 B1 was a *design* misread, not an audit bug — changing it is explicitly out of scope per mission-brief). Only `audit()`'s essential-disposition + the new constant change.
- `tools/install_audit.py` + `plugin.yaml` + `tools/plugin_manifest_audit.py` — INST-1/PMI-1; enumerate the new tool.

## Components touched

### `tools/methodology_changelog_forward_sync.py` (created)
- **Responsibility**: deterministic downstream gate for the in-repo↔installed `methodology-changelog.md` forward-sync invariant — re-homed from the ~33 per-version installed reads to ONE whole-file EOL-agnostic equality (strictly stronger).
- **Key interactions**: reads in-repo (git-tracked) + `Path.home()/".claude"/"methodology-changelog.md"` (untracked → BCI-1 installed-absent→WARN). **Non-catalog by construction** (M-add-1 — not in any `Machine-cmd` cell, not a callee of any cited fn; mechanically asserted; DR-1-verified `_cited()` cannot reach a non-`Machine-cmd` `tools/*` module).
- **m-add-2 (rev-3 DR-1, ACCEPTED-FIXED) — negative cataloging invariant**: the MCFS-1 *regression suite* `tests/methodology/test_methodology_changelog_forward_sync.py` necessarily reads `Path.home()/".claude"/"methodology-changelog.md"` (its synced / divergent / installed-absent / CRLF-parity cases) ⇒ it AST-classifies `essential`. It MUST therefore be **intentionally NOT shippability-catalog-cited** — `_cited()` resolves any `tests/`-rooted `Machine-cmd` citation, so a catalog row for this suite would make it an unregistered essential ⇒ `essential-unregistered` exit 1 self-violation. The MCFS-1 catalog row (sequenced LAST, RPCD-1/SCPD-1) cites **only** the in-repo-only-body entry-pin `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` (which classifies `clean`, V1). The MCFS-1 tool's consumer-test obligation (WIRE-1) is discharged by the suite *existing and passing*, not by cataloging it. (Counter-instinct to the PTFCD-1 reflex of cataloging every new test module; V2/V6 full-`--json` pre-finish would catch a mistaken citation loud, hence Minor.)

### `tools/shippability_decoupling_audit.py` (modified — `audit()` + 1 constant only)
- Essential disposition flips from passive `result.essential.append(qual)  # recognized, NOT flagged` to **closed-world registered**: a cited fn classified `essential` whose qualname ∈ `_REGISTERED_INSTALLED_READERS` ⇒ recorded as `essential_registered` (accounted-for, NOT a violation); ∉ ⇒ `Violation(reason="essential-unregistered")` exit 1. `to_dict`/`_format_human`: `essential=N (recognized, 030C)` → `essential_registered=N (registered)` + any `essential_unregistered` as violations. Post-rev-3: essential set = `{cross-module pin}` = the sole registered member ⇒ exit 0.

### `tests/methodology/test_methodology_changelog.py` (modified — the decouple)
- Drop **only** the `Path.home()/".claude"/"methodology-changelog.md"` read-leg from every essential fn in this module (the 28 `_entry_present_*` + the 5 `_entry_names_*`/`_supersession`, derived from `shippability_decoupling_audit --json` `essential`, regenerated not hand-copied) ∪ the 4 defined-but-uncited `_entry_present_*` (v43/45/47/48, for body consistency). **Retain every in-repo `## v0.NN.0` / RULE-ID / canonical-phrase assertion** (META-1 content protection; m2). **No rename** (scope-cut). DR-1-verified: 0 of these remain essential post-leg-drop.
- **m-add-1 (rev-3 DR-1, ACCEPTED-FIXED): the installed read-leg appears in TWO syntactic forms** — a **bare assignment** `installed_path = Path.home() / ".claude" / "methodology-changelog.md"` (~17 fns, e.g. L168, v22-class) AND an **inline `.read_text()`** `installed = (Path.home() / ".claude" / "methodology-changelog.md").read_text(...)` (~20 fns, e.g. L1574, v34+). The Builder MUST edit by **both** forms (plus the dependent `installed_path.exists()` / `installed = installed_path.read_text()` follow-on lines for the bare form). A single-pattern leg-drop silently leaves the inline-form fns `essential`. The post-leg-drop `shippability_decoupling_audit --json` `essential`-empty (V2) is the **confirmation** the both-form edit was complete — never the discovery mechanism (rev-1 hand-count failure mode in a syntactic-heterogeneity guise).

### `tests/skills/diagnose/test_skill_md_pins.py` — **UNCHANGED**
- The cross-module LAYER-EVID-1 pin is **registered, not modified**. Its installed-changelog read (L349) + all N surfaces stay. slice-041 does not touch slice-019's artifact body — it *accounts for* it via the registered allowlist (the charter's "registered not absent").

### sibling-scoping helpers (M2 — Minor, carried from rev-2)
- `_extract_version_body`/`_extract_v031_body`/`_extract_v033_body` scope by `## v` changelog-text anchors (not fn names, not installed-half body structure) → leg-drop cannot shift windows. Add a cheap regression assertion that `_extract_v031_body`/`_extract_v033_body` still bound correctly post-leg-drop.

## Contracts added or changed

### MCFS-1 CLI — `tools/methodology_changelog_forward_sync.py`
`$PY -m tools.methodology_changelog_forward_sync` (default `--check`); `--json`; `--root`. Exit **0** synced **or** installed-absent WARN (distinct stdout); **1** HALT installed-present-divergent-after-CRLF→LF, attributed *"METHODOLOGY-CHANGELOG FORWARD-SYNC DRIFT — re-run the PMI-1 forward-sync (in-repo → ~/.claude/); this is NOT a slice regression"*; **2** usage. Read-only. **Empty present installed = divergent → HALT** (empty ≠ absent).

### SCMD-1 audit contract change
`essential ∧ qualname ∉ _REGISTERED_INSTALLED_READERS ⇒ exit 1` (`essential-unregistered`); `essential ∧ ∈ ⇒ accounted-for (exit-0-eligible)`. `--json` `essential` → `essential_registered` + `essential_unregistered`. Closed-world: any future essential cited fn not registered HALTs (relocation-proof).

## Data model deltas
None. `_REGISTERED_INSTALLED_READERS` is a 1-element git-tracked `frozenset` constant + inline rationale comment.

## Wiring matrix

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/methodology_changelog_forward_sync.py` | **Primary (non-opt-out, ungated): `skills/build-slice/SKILL.md` Step 6 pre-finish** (new MCFS-1 sub-section; verified Step 6 BCI-1 is in the unconditional checklist — runs every slice, NOT rule-promotion-gated; m1) + **a NEW dedicated `skills/reflect/SKILL.md` post-write step, explicitly NOT folded into the rule-promotion-gated Step 5b** + `architecture/shippability.md` new catalog row (sequenced LAST) | `tests/methodology/test_methodology_changelog_forward_sync.py::test_synced_tree_exit_0` (+ divergent / installed-absent-WARN / CRLF-parity / CSP-1-parity / M-add-1-relocation-proof / **M3 self-classification**) | — |

## Decisions made (ADRs)
- [[ADR-042]] — re-home the per-version in-repo↔installed forward-sync to a non-catalog whole-file EOL-agnostic MCFS-1 gate; **rev-3**: drop the read-leg from the in-`test_methodology_changelog.py` essential set only; the cross-module slice-019 pin is registered (not re-homed, not modified); rename scope-cut out — reversibility: **cheap**
- [[ADR-043]] — SCMD-1 essential class → closed-world **non-empty** registered intentional-installed allowlist (registers exactly the cross-module LAYER-EVID-1 pin with rationale); charter-literal ("registered not absent"); DR-1-verified cardinality=1, R-4 retireable — reversibility: **cheap**

## Authorization model for this slice
No runtime authz. Load-bearing analogue = the **closed-world registered allowlist** itself: it is the explicit *accounted-for* record (the charter's "registered not absent"). The M-add-1 relocation guard is now двойной: (a) the MCFS-1 *tool* is non-catalog by construction (mechanically asserted; DR-1-verified `_cited()` unreachable for non-`Machine-cmd` `tools/*`); (b) the closed-world rule HALTs any **future** essential cited fn not registered — relocation cannot be silently absorbed. **Sequencing (slice-037)**: the MCFS-1 tool's OWN shippability row + its `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` entry-pin (in-repo-only body) are authored **LAST**, evaluated against the final catalog.

## Error model for this slice
- MCFS-1 exit 1 attributed (both paths + both CRLF-normalized hashes + PMI-1-forward-sync hint; "NOT a slice regression"); exit 0 WARN installed-absent (distinct stdout; BCI-1/slice-030A meta-M3 parity).
- SCMD-1 exit 1 `essential-unregistered` names the offending qualname + the registered set + "decouple it, or — only if genuinely intentional like the LAYER-EVID-1 pin — register with rationale".
- No new exit-2 beyond inherited catalog/AST-parse.

## Methodology-surface obligation (M4 — verified, not asserted)
Only META-1 structural enforcer = `tests/methodology/test_methodology_changelog.py::test_each_changelog_entry_carries_rule_reference` (L127–144): `re.split` on `^## v\S+ — \d{4}-\d{2}-\d{2}`, asserts each body has a `Rule reference` line — **no** test-name suffix convention (DR-1 independently confirmed). Branch = **MEPD-1 (a) rule-path** (SCMD-1 exit-code contract changes + new gate tool ⇒ behaviour-changing): mint **MCFS-1**; **v0.53.0** entry with a `Rule reference` line (satisfies the actual L141 assertion); **4-part PMI-1 bump** — `VERSION` 0.52.0→0.53.0 + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml.version` + forward-synced `~/.claude/methodology-changelog.md` (slice-035 B-add-1 installed-leg blind spot enumerated); `plugin.yaml` + `tools/install_audit.py` enumerate the new tool; `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed` entry-pin, **in-repo-only body** (M3), LAST; new shippability row (LAST). `agents/critique.md:123` MEPD-1 prose is **NOT edited** (scope-cut — no rename this slice; its documented `_entry_present_in_repo_and_installed` example stays accurate for the as-yet-unrenamed fns; `test_critique_agent.py:1424` prefix-only assertion stays green).

## Verification plan (rev-3)

| # | Criterion | How we verify |
|---|-----------|---------------|
| V1 | M3 self-classification | After authoring the v0.53.0 pin + its row LAST: `shippability_decoupling_audit --json` ⇒ `test_v_0_53_0_mcfs_1_entry_present_in_repo_and_installed ∈ clean`. Pre-finish, BC-PROJ-4 class. |
| V2 | Decouple complete (executed, not assumed) | Worklist regenerated from `--json` `essential`; post-decouple `--json` ⇒ `essential` = exactly `{tests/skills/diagnose/test_skill_md_pins.py::test_textual_evidence_rule_byte_equal_across_n_3_surfaces}`; that qualname ∈ `_REGISTERED_INSTALLED_READERS` ⇒ `essential_unregistered` empty ⇒ exit 0. |
| V3 | Registered key form | A regression test asserts the registered qualname resolves against the real catalog (matches the audit-emitted file-path-qualified `::`-selector, DR-1 flag) — a typo'd key would silently fail-open. |
| V4 | m1 ungated wiring | `/build-slice` Step 6 MCFS-1 sub-section non-opt-out + NOT rule-promotion-gated; new `/reflect` step NOT inside Step 5b (read both anchors). |
| V5 | forward-sync not weakened | Deliberately-divergent installed-changelog fixture ⇒ MCFS-1 HALT exit 1; CRLF-only difference ⇒ exit 0 (must-not-mask AND must-not-false-FAIL). |
| V6 | R-4 retireable | `risk_register_audit --json --filter-status retired` lists R-4; `--filter-status mitigating` does not; full catalog no regression, no essential-class env-fragile FAIL. |

## Self-application recursion note (slice-037)
The slice adds its own v0.53.0 entry-pin. It MUST have an in-repo-only body (an installed-changelog read ⇒ `essential` ⇒ unregistered ⇒ exit 1 self-violation). Its name keeps the existing `_entry_present_in_repo_and_installed` convention (scope-cut: no rename; the chartered follow-up rename slice realigns all uniformly). Pin + shippability row sequenced LAST; pre-finish real-artifact runs (V1–V6, `shippability_decoupling_audit` on the final catalog + MCFS-1 on the real tree + full catalog) are the BC-PROJ-4-class structural backstop — not the Critic stack (which twice reasoned-not-executed on exactly this audit-classification surface).
