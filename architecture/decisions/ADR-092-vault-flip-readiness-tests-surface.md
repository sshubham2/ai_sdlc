---
id: ADR-092
title: Extend the vault-flip readiness audit to the tests surface with a distinct loud-breakage class, a write_text content-arg fix, a fixtures exclusion, and a fail-closed-completeness regression strategy
date: 2026-06-02
slice: slice-102-vault-flip-readiness-tests
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-092: Vault-flip readiness audit — the `tests/**/*.py` surface

## Context

slice-100 ([[ADR-091]]) shipped `tools/vault_flip_readiness_audit.py`, classifying every `architecture/`/`diagnose-out/` location literal on the **production-code surface** (`tools/*.py` + `skills/**/*.py`), and explicitly **deferred** the `tests/**/*.py` surface (mission-brief Out-of-scope; reflection Deferred) as a follow-up named `vault-flip-readiness-tests`. The flip-execute slice (the next major cut) needs the tests surface inventoried too, or it has no checklist for the test literals that break when the vault relocates.

The tests surface differs from production in a way ADR-091 anticipated: a missed production literal is a **silent** path mis-resolve; a missed *test* literal breaks **loudly** (a failing test). A design-time probe (the existing `audit_file` run as a library over 215 `tests/**/*.py` files) found 287 prose, 160 path-construction, 49 unmarked-collection-pathspec, 1 deliberate parse-error fixture, 1 dynamic-fragment, 2 already-routed. Applying the production ruleset verbatim would (a) flatten the loud-breakage set into the silent `must-rewrite` class, (b) dump 49 intentional vault-path test lists into `needs-human` (so the gate never goes clean), (c) permanently flag a deliberately-malformed parse-error fixture, and (d) mis-flag `write_text(content)` argument prose as a resolving path.

## Options considered

1. **Reuse the production ruleset verbatim on tests** — minimal code, but conflates loud/silent (violates ADR-091's surface distinction), produces ~51 permanent `needs-human` (gate never clean), and inherits the `write_text`-content false-positive. Rejected.
2. **A separate tests-only audit tool** — clean isolation but duplicates the entire ruleset/AST machinery (parallel-copy AI-bloat, the SC-017 signature) and forks two things that must stay consistent. Rejected.
3. **Extend the existing audit with a surface dimension + TWO distinct tests classes (chosen)** — one tool, one ruleset, a `surface` tag, and on the tests surface: `test-update-at-flip` for **path-construction** literals (test code resolving a vault path — WILL update at flip) and `test-collection-pathspec` for **collection-member git-pathspec literals** (`_SOFT_FILE_SET` mirrors, `git add` pathspecs, `applies_to` tuples — AMBIGUOUS: most mirror Class-B production constants that STAY `architecture/…`, reviewed separately, NOT auto-"update"); `fixtures/**` is excluded; `write_text`/`write_bytes` args are treated as content. *(An earlier draft blanket-routed collection members into the update checklist; `/critique` M1 showed this mislabels ~49 Class-B/git-pathspec mirrors as "will update at flip" — the exact artifact the flip-execute slice consumes — so the collection class is split out. The audit can statically tell path-construction from collection-membership; it does NOT cross-reference to prove Class-B mirror-ship — that over-asserts and is left to flip-execute.)*
4. **Regression pin: freeze the ~200-entry tests checklist exactly (slice-100 parity)** vs **fail-closed completeness invariant + floor (chosen)** — the exact freeze churns on most future vault-referencing-test additions and replicates the SC-023 mega-pin anti-pattern; the invariant captures the only safety property that matters (nothing unclassifiable silently slips) and lets the flip slice consume the live checklist. User-ratified at `/design-slice`.

## Decision

Extend `tools/vault_flip_readiness_audit.py` to scan `tests/**/*.py` (excluding `tests/**/fixtures/**`), tagging each occurrence with a `surface` of `production` | `tests`. Introduce **two** tests-surface classes: **`test-update-at-flip`** (the path-construction / path-construction-1hop rules route here — the loud-breakage update checklist) and **`test-collection-pathspec`** (the unmarked-collection-pathspec rule routes here — review-at-flip git-pathspec/Class-B mirrors, NOT the checklist, NOT fail-closed). Fix `_is_path_call_arg_or_recv` so a positional argument to `write_text`/`write_bytes` is **not** treated as a path (the receiver still is) — a correctness fix on both surfaces, verified to leave the production `_BASELINE` (4 sites) unchanged. Scope `baseline_tuple()` to the production surface. The tests-surface regression guard is a **fail-closed completeness invariant** (tests-surface `needs-human` is empty, proven non-vacuous by mutation) plus a **non-vacuity floor** on the checklist count — not a frozen membership pin. The repo is **not flipped**: `_vault_paths` default stays `Path("architecture")` (capability-without-flip, mirroring slice-093/slice-100).

## Consequences

- The flip-execute slice gets a complete, deterministic tests-surface checklist (`test-update-at-flip` path-resolve entries with `path:line`) **plus a separate `test-collection-pathspec` review list** (the git-pathspec/Class-B mirrors — most stay `architecture/…`), consumed live from the audit's JSON. The checklist is not polluted with false "update me" entries.
- The tests-surface regression guard is the fail-closed `needs-human`-empty completeness invariant (non-vacuous by mutation) plus **per-class** non-vacuity floors (one each for `test-update-at-flip` and `test-collection-pathspec`), so a silent collapse of either classification branch is caught (a single aggregate floor would not be — `/critique` m1).
- The non-strict gate stays exit-0 on the clean tree (tests-surface `needs-human` driven to ∅); the smoke gate's "zero un-triaged needs-human" holds.
- `write_text`/`write_bytes`-content vault literals (synthetic test prose) classify as `doc-example-safe`, not as a resolving path — correct, and it also resolves the lone probe `dynamic-fragment`.
- A vault literal placed inside a `tests/**/fixtures/` directory is out of scan scope (documented residual — fixtures are test INPUT artifacts; the one real member is a deliberately-malformed parse-error fixture).
- **`test-collection-pathspec` heterogeneity residual** (`/critique-review` M-add-1, fix (b)): the class is a structural collection-membership signal, so a *genuine* path-resolve that is a bare list/tuple member is demoted here (review, off-checklist, exit-0) rather than to the checklist or fail-closed `needs-human`. This is **acceptable** because the tests surface breaks **LOUDLY** at flip — a mis-bucketed resolve surfaces as a *failing test* at flip-execute, not a silent mis-resolve (the ADR-091 loud-vs-silent rationale) — **provided the flip-execute slice consumes BOTH the `test-update-at-flip` checklist AND the `test-collection-pathspec` review list**. The "all collection members mirror Class-B constants that stay" property is a *current-corpus observation* (zero-instance residual today), NOT a structural invariant; the stronger fix (loop-variable flow tracking / a non-zero review-required gate) was declined at TRI-1 as gold-plating over a zero-instance case. Pinned by `test_collection_member_genuine_resolve_is_review_residual` (slice-095 honest-contract pattern).
- Future slices that add vault-resolving tests grow the live checklist without tripping the suite (no frozen tests baseline); only a genuinely-unclassifiable literal trips the always-on guard.
- No new RULE-ID / VERSION / methodology-changelog entry (MEPD-1 EXCLUDE); the change is additive to ADR-091's lineage.

## Reversibility

**cheap** — the audit is read-only static analysis with no persistent state and no flip performed; every change is a classification refinement reverted by reverting the diff. The `write_text`-content fix is a strict correctness improvement (proven not to perturb the production baseline). Tagged cheap because nothing downstream is locked: the flip itself is a separate, later decision.
