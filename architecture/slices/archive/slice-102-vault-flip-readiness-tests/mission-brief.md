# Slice 102: vault-flip-readiness-tests

**Mode**: Standard
**Estimated work**: 1 day
**Risk retired**: R-32 (advances the flip gate by extending the flip-completeness checklist to the `tests/**/*.py` surface — the last auto-classifiable surface slice-100 left deferred; R-32 itself retires AT the actual flip, the next major cut)
**Test-first**: true  (per TF-1 — the classification logic is deterministic and naturally testable, mirroring slice-100)
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Slice-100 shipped `tools/vault_flip_readiness_audit.py` — a deterministic, fail-closed inventory that classifies every in-tree vault-location literal (`architecture/…`, `diagnose-out/…`) on the **production-code surface** (`tools/*.py` + skill-helper `skills/**/*.py`) so the external-vault flip lands atomically with no silently-broken path. It explicitly **deferred the `tests/**/*.py` surface** to this follow-up (named `vault-flip-readiness-tests` in slice-100's mission-brief Out-of-scope + reflection Deferred). This slice extends the readiness audit to scan and classify the **tests surface**, producing the complete, regression-pinned checklist the flip-execute slice consumes for tests — **without flipping this repo** (`_vault_paths` default stays `Path("architecture")`; capability-without-flip, mirroring slice-093/slice-100).

**Why the tests surface is different (settled in detail at `/design-slice`):** unlike the production surface — where a missed literal is a **silent** path mis-resolve — a vault-location literal in a test breaks **LOUDLY** (a failing test) at flip, and a large fraction are **intentional seam/migration test constants** (e.g. a test pinning that `_vault_paths` default is `architecture`, or a fixture that hardcodes a vault path on purpose). The classification model therefore must encode the ADR-091 loud-vs-silent surface distinction so the flip-execute slice gets an accurate per-test checklist rather than a flat must-rewrite dump. The class set + the loud-vs-silent encoding are firmed up at `/design-slice`.

## Acceptance criteria

1. `tools/vault_flip_readiness_audit.py` scans the **`tests/**/*.py` surface** (in addition to the existing production surface) and emits a deterministic JSON inventory of every `architecture/` / `diagnose-out/` location-assuming literal on that surface, each classified — fail-closed — with `path:line` evidence. The **production-surface scan + classification output stays byte-identical to slice-100** (the slice-100 baseline — the 4 `project_frame_synth.py` sites — is unchanged; no regression).
2. The tests-surface classification preserves ADR-091 loud-vs-silent fidelity with **two distinct named classes** — `test-update-at-flip` (a path-construction literal the test *resolves* — WILL update at flip) vs `test-collection-pathspec` (a collection-member git-pathspec / Class-B mirror — reviewed at flip, mostly stays) — neither flattened into the production silent `must-rewrite`; every scanned literal lands in exactly one class and a genuinely-unclassifiable hit routes to `needs-human-classification` (never silently dropped). (Refined post-`/critique` M1: the collection class must NOT be lumped into the update checklist.)
3. A regression pin (extending `tests/methodology/test_vault_flip_readiness_audit.py`) fixes the **tests-surface baseline** keyed line-number-independent on `(relpath, value, klass)`, so a NEW un-classified tests-surface vault literal fails the gate; proven **non-vacuous by mutation** — inject an un-routed tests literal → the pin FAILS until reverted.
4. CLI exit codes give gate semantics across **both surfaces**: clean (`0`) when no `needs-human-classification` entries exist on either surface and, under `--strict`, the **production** must-rewrite+needs-human baseline (the stable 4-set) is unchanged; non-zero (`2`) otherwise. Both surfaces MUST be gate-covered: the **tests** surface via the always-on `needs-human`-empty invariant + per-class non-vacuity floors (no frozen-membership pin, per [[decisions/ADR-092]] — the ratified Option B); the **production** surface additionally via `--strict` drift. (Corrected post-`/critique` M2 — the earlier "combined baseline" wording contradicted the production-scoped `baseline_tuple()`.) The tests surface is always scanned (no `--surface` selector).
5. **Capability-without-flip invariant holds**: `tools/_vault_paths.py` default stays `Path("architecture")`; the full methodology suite and the shippability catalog pass unchanged — every existing tool/test/skill behaves identically (no flip, fully reversible).

## Test-first plan

(per **TF-1**, `methodology-changelog.md` v0.13.0 — paths/function names are a starting sketch; `/design-slice` firms them up)

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_surface_scanned_and_classified | PASSING |
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_production_baseline_unchanged_vs_slice100 | PASSING |
| 1 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_must_rewrite_baseline_pinned | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_path_resolve_is_test_update_at_flip | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_collection_pathspec_is_review_not_checklist | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_write_text_content_is_not_path | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_collection_member_genuine_resolve_is_review_residual | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_surface_needs_human_empty | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_surface_needs_human_pin_non_vacuous | PASSING |
| 3 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_tests_surface_class_floors | PASSING |
| 2 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_fixtures_dir_vault_literal_out_of_scope | PASSING |
| 4 | integration | tests/methodology/test_vault_flip_readiness_audit.py | test_cli_exit_zero_when_no_needs_human | PASSING |
| 4 | integration | tests/methodology/test_vault_flip_readiness_audit.py | test_cli_strict_nonzero_on_baseline_drift | PASSING |
| 5 | unit | tests/methodology/test_vault_flip_readiness_audit.py | test_vault_paths_default_unchanged | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Tests surface inventoried + classified; production unchanged | Run `$PY -m tools.vault_flip_readiness_audit --json`; assert tests-surface entries carry `path:line` evidence AND the `must-rewrite-before-flip` + `needs-human` set for the production surface is byte-identical to the slice-100 baseline (the 4 `project_frame_synth.py` sites). |
| 2 | Loud-vs-silent surface model + fail-closed | Spot-check a real intentional test seam-constant (a `_vault_paths` default-pin test / a fixture hardcoding `architecture/`) → its class is the tests-surface "expected/intentional" class, NOT the production silent-mis-resolve class; feed a contrived ambiguous tests literal in a tmp fixture → `needs-human-classification`. |
| 3 | Regression-pin non-vacuity | Inject an un-routed `architecture/foo` literal into a scanned tmp/real test file → `test_new_unrouted_tests_literal_fails_gate` FAILS; revert → PASSES. |
| 4 | Gate wiring (both surfaces) | `$PY -m tools.vault_flip_readiness_audit` returns 0 on a fully-classified tree; with a seeded tests-surface `needs-human` hit (or `--strict` tests-baseline drift) returns 2 (`echo $LASTEXITCODE`). |
| 5 | Capability-without-flip | `Get-Content tools/_vault_paths.py` shows default `Path("architecture")` unchanged; `$PY -m pytest tests/methodology` + `$PY -m tools.shippability_runner` both green. |

## Must-not-defer

- [ ] **Determinism** — stable-sorted output across both surfaces; a non-deterministic audit cannot serve as a regression pin (AC2/AC3).
- [ ] **Fail-closed classification** — no silent drop; every scanned tests-surface literal lands in exactly one class, ambiguous → `needs-human-classification`.
- [ ] **Loud-vs-silent surface fidelity (ADR-091)** — the tests surface must NOT be flattened into the production silent-breakage `must-rewrite` semantics; an intentional test seam/migration constant is a distinct, named class. Encode the surface distinction; name any residual.
- [ ] **Production-surface non-regression** — the slice-100 production baseline (the 4 `project_frame_synth.py` sites) and its byte-output stay unchanged; extending the scan must not perturb the existing classification.
- [ ] **Non-vacuity by mutation** — the AC3 tests-surface pin must be proven to FAIL when an un-routed literal is injected (per slice-092 lesson).
- [ ] **cp1252-safe stdout** — the tool already uses `tools._stdout.reconfigure_stdout_utf8()` (UTF8-STDOUT-1); preserve it; never bare `print` of non-ASCII.
- [ ] **`encoding="utf-8"`** on every file read (BC-GLOBAL-5) — the new tests-surface scan reads many files.
- [ ] **Inventory/count fan-out IF surface widens public inventory** — if a new public class/flag/shippability row is added, propagate per PMI-1 / INST-1 / BC-PROJ-9 + RPCD-1/SCPD-1 shippability catalog. (Likely MEPD-1 EXCLUDE if it extends the existing tool with no VERSION/RULE-ID — confirm at `/design-slice`.)

## Out of scope

- **The contract-prose surface** — `skills/**/SKILL.md`, `agents/*.md`, `CLAUDE.md`, `INSTALL.md`: bulk-rewritten *atomically* at flip-execute time and not reliably auto-classifiable (AI-hard prose judgement); owned by flip-execute / a dedicated prose slice (slice-100 Out-of-scope, unchanged).
- **The actual flip** — physical move of `architecture/`+`diagnose-out/`, default-flip, git-untrack, the atomic rewrite, PCR conflict-resolution replacement (the **next major** cut). This slice only inventories + classifies the tests surface; it does **not** fix any `must-rewrite` / test-update literal.
- **Per-worktree-install isolation (R-28 / R-29)** — separate queued slice (`isolate-per-worktree-install`).
- **C5 history decision** (external vault as its own git repo) — flip-execute / prose slice.

## Dependencies

- Prior slices: [[slice-100-add-vault-flip-readiness-audit]] (the audit + ordered ruleset + `--strict` baseline + the production-surface scan this extends), [[slice-093-add-external-vault-support]] (the `_vault_paths` seam / `VAULT_ROOT`), [[slice-098-route-or-retire-git-coupled-vault-tools]] (the Class-B markers).
- Vault refs: [[decisions/ADR-091]] (the readiness-audit decision; this realises its deferred `tests/**/*.py` surface), [[decisions/ADR-065]], [[decisions/ADR-089]]
- Risk register: [[risk-register#R-32]] (concurrent-write lost-update / shared-mutable-vault corruption — the flip gate; advanced, retired at the flip)
- Initiative context: the `external-shared-vault-initiative` plan — this is the last auto-classifiable readiness surface before flip-execute.

## Mid-slice smoke gate

At ~50% of build, run:
```
$PY -m tools.vault_flip_readiness_audit --json
$PY -m pytest tests/methodology -q
```
Expected: the audit emits a **non-empty total classified inventory for the tests surface** (>0 occurrences — a zero total means the new scan/glob is broken) AND **zero un-triaged `needs-human-classification`** (every tests-surface occurrence resolves; any `needs-human` is reviewed + resolved) AND the **production-surface baseline is unchanged** (the 4 `project_frame_synth.py` sites still classify identically) AND the full methodology suite still passes (no flip occurred). STOP if: tests-surface total classified is zero, OR `needs-human` is non-empty/unresolved, OR the production baseline shifts, OR any pre-existing test regresses.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed
- [ ] /drift-check passes
- [ ] Mid-slice smoke still passes (no regression)
- [ ] No new TODOs / FIXMEs / debug prints
