# Code Review: Slice 106 route-project-frame-synth-via-vault-root

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-06-03
**Result**: FINDINGS (0 Blockers, 0 Majors, 2 Minors — both advisory)

## Summary

A clean, narrow, correctly-executed routing slice. All 4 production vault-path reads in `tools/project_frame_synth.py` (`concept.md`/`triage.md`/`slice-queue.md`/`risk-register.md`) now compose through the `VAULT_ROOT` seam via the codebase-idiomatic `repo_root / VAULT_ROOT / "X"` form; `_BASELINE` is correctly emptied; the readiness audit reports `[production] 0 must-rewrite` and `--strict` exits 0; the B1 test rework relocates (does not drop) the classifier non-vacuity coverage. Flip-correctness of the join semantics, the count-pin reconciliation, and the orphan-literal guard interaction were verified by execution. No blockers, no majors — stated after adversarially tracing every pressure-test (a)–(f), not as a rubber-stamp.

## Changed files (in-scope)

```
tools/project_frame_synth.py
tools/vault_flip_readiness_audit.py
tests/methodology/test_vault_flip_readiness_audit.py
tests/methodology/test_vault_root_constant.py
tests/methodology/test_external_vault_adr_and_risk.py
```

(`architecture/slices/.../build-log.md` and the other `architecture/**` files in the branch diff are vault-prose / out-of-scope for `/code-review` per the in-scope path filter.)

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None. Three break-attempts failed:

- **Flip-correctness of `repo_root / VAULT_ROOT / "X"`** (pressure-test a): traced pathlib join semantics by execution. Default (`VAULT_ROOT == Path("architecture")`, relative) → `repo_root/architecture/concept.md` — byte-identical to the old `repo_root / "architecture" / "X"`, so AC3's no-op holds. At flip (`VAULT_ROOT` absolute), `Path('/repo') / Path('/abs/vault') / 'concept.md'` == `/abs/vault/concept.md` — the absolute operand discards `repo_root`, which is the *intended* relocation. The exact idiom used by every sibling consumer (`critique_review_prerequisite_audit.py:155`, `drift_check_audit.py:176`, `cross_spec_parity_audit.py:153`, `parallel_conflict_resolver.py:939`, `stranded_slice_audit.py:313`). Correct on both paths.
- **B1 deletion drops no coverage** (pressure-test c): the deleted real-repo `assert MUST_REWRITE in classes` would now be *vacuously false* post-routing (the 4 sites it relied on are exactly what this slice removed). The non-vacuity is independently re-proven by `test_new_unrouted_literal_fails_gate` (`test_vault_flip_readiness_audit.py:93-99` — synthetic bare-`architecture` `/`-BinOp → MUST_REWRITE) and `test_every_hit_has_exactly_one_class` (`:56-61`). Both pass. Coverage relocated to `tmp_path` fixtures, not lost.

### Majors

None. The count-pin (highest-risk silent-drift surface in this slice) reconciles correctly:

- **`len(importers) == 16` is right**: the raw `tools/*.py` VAULT_ROOT-importer count is 17, but `test_external_vault_adr_and_risk.py::_vault_root_importers` (`:26`) excludes `_`-prefixed modules, dropping `_vault_git.py` → 16. The `project_frame_synth.py`-membership assert (`:62-65`) is present and passing. The parallel pin in `test_vault_root_constant.py` (`_MIGRATION_SITE_ALLOWLIST` → 16) and the orphan-literal guard both pass against the live tree. All three changed test files ran: **44 passed**.

### Minors

#### m1: The two surviving `architecture/` prose literals evade the orphan regex by quote-prefix coincidence, not by an explicit prose marker
- **Claim under review**: `tools/project_frame_synth.py:48` (docstring CLI example `--slice-dir architecture/slices/slice-NNN-x`) and `:305` (`help="...e.g. architecture/slices/slice-NNN-<name>"`) — two bare `architecture/` literals remain after routing.
- **Issue**: now that `project_frame_synth.py` is in `_MIGRATION_SITE_ALLOWLIST`, `test_no_orphan_architecture_literal_in_migrated_tools` (`test_vault_root_constant.py:127`) sweeps it. The guard regex `["\']architecture[/"\\]` (`:139`) requires a quote *immediately* before `architecture`. Both surviving literals have non-quote chars immediately before `architecture/` (bare docstring text at `:48`; `e.g. ` mid-help-string at `:305`), so the regex does not match and the guard passes legitimately — but incidentally. A future reword to quote-adjacent (`"architecture/slices/..."`) would red the orphan guard, with no `# NOT VAULT_ROOT-routed ... — error-message prose` marker present to explain it's intentional prose.
- **Evidence**: `literal_re = re.compile(r'["\']architecture[/"\\]')` at `test_vault_root_constant.py:139`; both literals are the only remaining `architecture` occurrences in the file, both prose; the readiness audit independently classifies both as `doc-example-safe` (docstring + `argparse-help`) — neither is a silent path mis-resolve. Guard-fragility note, not a correctness defect.
- **Proposed fix**: optional/cheap — leave as-is (the audit's `doc-example-safe` classification is the robust backstop), OR mirror the L44 update by replacing the `:48`/`:305` literals with a `<vault>/slices/...` placeholder. Not worth a churn cycle on its own.

#### m2: Inline `repo_root / VAULT_ROOT / "X"` repeated 4× rather than module-level constants — idiomatic, logged for completeness
- **Claim under review**: `tools/project_frame_synth.py:122,123,186,195` each inline-compose `repo_root / VAULT_ROOT / "<file>"` rather than defining module-level `_*_REL = VAULT_ROOT / "<file>"` constants (the form used by `slice_queue_writer.py:84` `_INDEX_MD_REL`).
- **Issue**: none, on inspection. Pressure-test (e) resolved as **not a defect**. The constant form is used only where a path is referenced multiple times or supplied as an argparse `default=`; every *single-call-site* vault read uses the inline `repo_root / VAULT_ROOT / "X"` form (`critique_review_prerequisite_audit.py:155`, `drift_check_audit.py:176,205`, `cross_spec_parity_audit.py:153`, `state_transition_pin_audit.py:374`, `supersede_audit.py:173`). Each of project_frame_synth's 4 reads is a distinct single-call-site read → the inline form is the correct convention match.
- **Proposed fix**: none required. Logged so the record shows it was checked against the slice's own cited counter-example (`_INDEX_MD_REL`) and found conformant.

## Dimensions checked
- [x] Unfounded assumptions — none. In-test narratives ("4 sites → ∅", "16 importers") each verified against live audit/test execution; the `methodology-changelog.md` read at `:157` correctly carries no VAULT_ROOT routing (changelog lives at repo-root — verified `architecture/methodology-changelog.md` does not exist; root copy does) — pressure-test (d) resolved.
- [x] Missing edge cases — none new. `_read`'s `except OSError → None` degrade unchanged; routing alters *which directory* is read, not *which failures* occur. At flip an absent/relative `VAULT_ROOT` yields the existing missing-file `warn(...)` + `_(none)_`.
- [x] Over-engineering — none. Pure routing; no new abstraction/module/parameter/dead branch. `_BASELINE = ()` is the minimal correct representation.
- [x] Under-engineering — none. Every AC has a delivering code element (AC1 4 routed reads; AC2 `_BASELINE = ()` + `--strict` exit 0; AC3 default-relative no-op; AC4 allowlist membership + orphan guard; AC5 44 tests green, no new catalog row). RSAD-1 self-application holds (the routed tool now passes the very readiness audit it feeds).
- [x] Contract gaps — none. `synthesize_frame` signature + CLI unchanged. `from tools._vault_paths import VAULT_ROOT` (`:60`) is a real symbol (`_vault_paths.py:165`); no phantom import.
- [x] Security — none. No new input boundary/auth/secret/subprocess/injection. slice only *consumes* the already-shipped seam.
- [x] Drift from vault — none. design.md §Components-touched names exactly the changed files; no symbol/path referenced that doesn't exist; mints no ADR (MEPD-1 EXCLUDE) and code mints none; out-of-scope "the flip itself" respected (`VAULT_ROOT` default unchanged, verified `== Path("architecture")`).
- [x] Web-known issues — checked. pathlib's absolute-operand-discard is documented, intentional, version-stable ([docs.python.org/3/library/pathlib](https://docs.python.org/3/library/pathlib.html)) — the *correct* flip behavior, not a footgun.
- [x] Cross-cutting conformance — none. RSAD-1: routed tool passes its own readiness audit. APED-1: no audit parse-rule modified — `_BASELINE` is pinned *data*; classifier logic byte-untouched, so no adversarial-battery re-execution obligation. Inline join idiom composes correctly with the pre-existing absolute-discard branch and every sibling consumer's identical idiom.

_Advisory (CRSI-1 v1) — these findings do NOT block /validate-slice. m1/m2 are recorded for the /reflect calibration record; neither warrants a code change in this slice (m2 is explicitly a non-defect; m1 is backstopped by the readiness audit's doc-example-safe classification)._
