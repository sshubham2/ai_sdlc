# Critique Review: Slice 041 reframe-installed-pin-forward-sync-invariant (REV-3 DR-1)

**Reviewed by**: critique-review agent (DR-1, rev-3 — independent re-execution; the rev-1 DR-1 reasoned false-confirm + rev-2 DR-1 execution-correction both in scope)
**Date**: 2026-05-18
**First-Critic verdict**: CLEAN
**First-Critic context**: rev-1 BLOCKED, rev-2 BLOCKED#2 (flaw relocated), structural pivot applied; rev-3 first-Critic CLEAN (0 Blockers/Majors, 2 Minors as recorded build-time obligations)
**Dual-review verdict**: EXTEND

## Summary

The rev-3 CLEAN is **genuine slice-031/030A "structural pivot → one-pass convergence", not a post-fatigue rubber-stamp** — every load-bearing claim independently re-derived by *executing* `tools.shippability_decoupling_audit` / instantiating `classify_fn` against the real and leg-drop-simulated modules, and all hold. m1/m2 correctly Minor. Two genuine **Minor** build-time hazards the rev-3 first-Critic did not surface (m-add-1, m-add-2) — both detection-backstopped at pre-finish, both real, neither manufactured. EXTEND on those two; the CLEAN core is sound and correctly verdicted.

## Empirical verification performed (execute-don't-reason law honored)

1. **Population re-derived**: `--json` ⇒ `rows_scanned 40`, raw essential 37, unique 34 = 33 in `test_methodology_changelog.py` (28 `_entry_present` + 5 `_entry_names_*`/`_supersession`) + exactly 1 cross-module pin. `v_0_42_0` essential-but-uncited; defined-but-uncited = exactly v43/45/47/48. Matches AC#3/design/m2 byte-for-byte.
2. **Leg-drop simulated → 0/37** (correct two-form transformer; a naive single-form one left 20 essential — surfaced m-add-1).
3. **Cardinality-1 + exit 0 confirmed**: cross-module pin unmodified stays `essential` (`segs={.claude,diagnose,methodology-changelog.md,skills}`); registered key byte-exact to audit emission ⇒ `essential_unregistered=[]` ⇒ exit 0.
4. **Closed-world HALT confirmed**: constructed hypothetical future essential fn ∉ registered ⇒ exit 1.
5. **Charter + relocation**: risk-register L90 literally "registered not absent" → rev-3 charter-faithful; `_TEST_PATH_RE = tests/\S+?\.py` structurally cannot match `tools/*` ⇒ MCFS-1 tool non-catalog by construction; MEPD-1 verified vs real L127-144 enforcer (no fn-name-suffix convention → scope-cut breaks nothing); VERSION 0.52.0 ⇒ v0.53.0 correct; ADR-042/043 both `supersedes: null` (SUP-1 OK).

## Confirmed findings

- **m1** (`/reflect` MCFS-1 wiring = NEW dedicated step, NOT rule-promotion-gated Step 5b) — **VALID; Minor correct in rev-3** (not a rev-1-downgrade regression — see Severity).
- **m2** (worklist regenerated from `--json`, never hand-copied) — **VALID, Minor appropriate**.
- The rev-3 first-Critic's pivot-soundness / cardinality-1 / closed-world-HALT / MEPD-1 / M-add-1-tool-half / scope-cut-orthogonality / CLEAN verdict — **all VALID, execution-confirmed**.

## Suspicious findings

None. Every rev-3 first-Critic claim verified by execution holds — the inverse of the rev-1 DR-1's reasoned false-confirm.

## Missed findings

- **m-add-1 (Minor)**: the installed read-leg exists in TWO syntactic forms in `test_methodology_changelog.py` — bare `installed_path = Path.home()/".claude"/"methodology-changelog.md"` (17 fns, e.g. L168) AND inline `installed = (Path.home()/".claude"/"methodology-changelog.md").read_text(…)` (20 fns, e.g. L1574). A single-pattern leg-drop leaves the 20 inline-form fns essential → `essential-unregistered` exit 1 → AC#3/V2 FAIL (rev-1 hand-count failure mode in a new guise — syntactic heterogeneity). **Minor**: V2/V6 pre-finish full-`--json` re-run is a real detection backstop (fails loud, not silent). **Fix**: design.md/mission-brief note that the leg appears in both forms (17/20 split); Builder edits by form, treats post-leg-drop `--json`-empty-essential as confirmation.
- **m-add-2 (Minor)**: the MCFS-1 *regression suite* (`test_methodology_changelog_forward_sync.py`) necessarily reads `Path.home()/".claude"/"methodology-changelog.md"` (synced/divergent/CRLF tests) → classifies `essential`. The M-add-1 relocation proof + AC#2 target the MCFS-1 **tool** (`tools/*`, `_cited()`-unreachable — confirmed), but `_cited()` DOES resolve any `tests/`-rooted Machine-cmd citation. The design positively states the catalog row cites the in-repo-only **entry-pin** (`clean`, V1) but never states the **negative invariant**: do NOT add a catalog row citing the MCFS-1 regression suite (it would self-violate `essential-unregistered` exit 1). Non-obvious foot-gun (PTFCD-1 instinct is to catalog new test modules). **Minor**: V2/V6 catches it loud. **Fix**: design.md/AC#2 explicitly state the MCFS-1 regression suite is intentionally NOT shippability-cited (distinct from the entry-pin row that IS, and is `clean`).

## Severity adjustments

No adjustments. **m1=Minor is correctly calibrated in rev-3 and is NOT a re-introduction of the rev-1 DR-1's Minor→Major.** Load-bearing distinction: at rev-1 the *design did not specify* the ungated placement → latent **design defect** → correctly Major. At rev-3 the design **explicitly mandates** the fix (design.md L31/L69; V4 verifies both anchors) → the residual is a build-time *execution-fidelity obligation on an already-correct design* → textbook Minor. The mission-brief must-not-defer "(Major, DR-1-upgraded)" label is the orthogonal *enforcement-priority* weight (non-negotiable at build), ≠ critique-finding design-defect severity; both internally consistent. m2=Minor correct (worklist-source aspect; the two-form heterogeneity is the *separate* missed m-add-1, not an m2 bump).

## Notes

Confidence **high**, grounded in execution (audit reproduced; leg-drop simulated both forms → 0/37; cardinality-1 + exit 0 + closed-world HALT run against real/simulated modules; registered key proven byte-exact; charter/MEPD-1/`_TEST_PATH_RE` source-confirmed). The rev-3 CLEAN is genuine slice-031/030A convergence: the pivot structurally removes the relocation surface the rev-1/rev-2 leg-drop approaches kept re-creating, and the closed-world rule makes future relocation fail-closed. EXTEND (not ACCEPT) solely because m-add-1/m-add-2 are two genuine, independently-execution-surfaced Minor build-time hazards the rev-3 first-Critic missed — both narrow, both pre-finish-backstopped, neither manufactured to avoid the appearance of rubber-stamping. The CLEAN core stands, with two Minors added for TRI-1.
