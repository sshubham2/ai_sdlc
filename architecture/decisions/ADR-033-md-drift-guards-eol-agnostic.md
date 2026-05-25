---
id: ADR-033
title: .md forward-sync drift guards compare content modulo line endings, not raw bytes
date: 2026-05-17
slice: slice-033-fix-skill-drift-test-crlf-normalization
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-033: `.md` forward-sync drift guards are EOL-agnostic

## Context

The skill-drift / mini-CAD / CAD-1 family of guards asserts that an in-repo
`.md` (skill `SKILL.md`, `skills/diagnose/passes/03f-layering.md`,
`agents/critique.md`) is byte-identical to its installed `~/.claude/...`
copy — the property that guarantees Claude reads current (not stale) prose
at skill/agent runtime. All implementations hash `path.read_bytes()` with
**no line-ending normalization**.

On Windows with `core.autocrlf=true` the working tree is checked out CRLF
while the installed copy is LF. The git **blob is already LF** (so
`git diff` sees zero change and the content is genuinely identical), but the
raw-byte hash differs → spurious FAIL. Recorded firsthand N+2 in
[[risk-register#R-5]] (slices 030A / 031 / 032), each a false PCA-1 HALT on a
slice that never touched the guarded file. slice-030A additionally showed the
failure can be *masked* by a coincidental `cp` that happens to copy a
CRLF working tree onto the installed side — giving false confidence that the
guard is healthy.

The defect class these guards exist to catch is **stale runtime prose**
(a forgotten forward-sync after an in-repo content edit). CRLF↔LF is
semantically invisible to that class: it does not change the prose Claude
reads. So a raw-byte compare is *stricter than the invariant requires* and
its only practical effect on Windows is false positives.

## Options considered

1. **Normalize line endings in every `.md` drift guard before equality, +
   `.gitattributes eol=lf` on the guarded surface, + a regression test that
   genuine (non-EOL) divergence still FAILs.** Pros: kills the entire R-5
   false-FAIL class environment-independently; preserves the real
   safety property under test; single shared helper removes 6 duplicated
   `_sha256` defs and gives the safety property one audited home. Cons:
   relaxes "byte-equal" → "content-equal modulo EOL" for a self-hosting
   discipline (mitigated by the must-not-mask-real-drift regression test).
2. **`.gitattributes eol=lf` + whole-vault `git add --renormalize` only,
   leave the guards raw-byte.** Pros: no test-logic change. Cons: large
   blast radius (every vault `.md` rewritten); fragile — any future file
   that re-enters a CRLF state (new contributor, tool that writes CRLF)
   re-acquires the false-FAIL; does not fix the masking-by-cp false
   confidence; correctness still environment-dependent.
3. **Per-test `pytest.skip` on Windows / autocrlf.** Pros: trivial. Cons:
   silently disables the CAD-1/mini-CAD guard on exactly the platform the
   maintainer develops on — the guard's whole point is to catch real
   forward-sync misses there. Rejected.

## Decision

Option 1. A shared `tests/skill_drift_equality.py::assert_md_forward_synced`
normalizes CRLF→LF before hashing and is the sole comparator for all five
skill-drift test modules. `tools/critique_agent_drift_audit.py::_sha256_of`
(CAD-1) gets the same one-line normalization — it is the canonical `.md`
byte-equality guard and R-5 explicitly generalizes the class to "any drift
guard"; leaving it raw-byte would only partially retire R-5 and leave
`agents/critique.md` exposed to the identical false-FAIL plus the
masking-by-cp false confidence. CAD-1's exit-code contract (0/1/2) is
unchanged — only its equivalence relation becomes EOL-insensitive; the
pre-existing `test_drift_detection_fires_on_artificial_byte_flip` + CLI
exit-code-matrix tests (genuine `# v1`/`# v2` divergence) are bound as the
CAD-1-side must-not-mask proof.

A `.gitattributes` entry declares the guarded surface
(`skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`)
`text eol=lf`. **`.gitattributes` alone does NOT normalize files already
checked out CRLF** under `core.autocrlf=true` (git-scm gitattributes docs:
requires `git add --renormalize` or re-checkout) — so the slice ALSO runs a
**targeted `git add --renormalize -- <those globs>`**. Renormalization is
**scoped to the guarded files only** — whole-vault renormalization is
explicitly out of scope (blast radius; unnecessary once the comparators are
EOL-agnostic). Blast radius is bounded: the git blobs are already LF, so the
renormalize index diff is empty — it only reconciles the working-tree
representation and keeps `git status` clean. The relaxation is bounded by a
mandatory regression test asserting genuine non-EOL divergence still FAILs
every patched guard.

**Helper location (M4)**: the shared comparator lives at top-level
`tests/skill_drift_equality.py`, NOT in a subpackage `conftest.py`. The
repo convention is conftest-based sharing, but the consumer set here spans
TWO sibling subpackages (`tests/skills/diagnose/` and `tests/methodology/`);
neither subpackage's `conftest.py` is the natural home (a `conftest.py` is
pytest-fixture-scoped collection config, not a general cross-subpackage
import surface — importing one subpackage's conftest into another is the
greater convention abuse). A neutral top-level importable module is the
correct structural choice. `pytest.ini` (`python_files = test_*.py`) does
not collect it as a test (verified: 644 tests collect, module not collected).
This deviation is written here per the Brownfield "deviations need an ADR"
rule.

## Consequences

- CAD-1 / mini-CAD invariant is restated as **content-equality modulo line
  endings** (the prose Claude reads is identical), not raw byte-equality.
  This restated invariant is minted as RULE-ID **`EOL-DRIFT-1`** (m-add-1 —
  the v0.47.0 changelog entry header is `**EOL-DRIFT-1 — .md forward-sync
  drift guards are EOL-agnostic**`, and the pin-test name derives from it:
  `test_v_0_47_0_eol_drift_1_entry_present_in_repo_and_installed`, per the
  verified v0.46.0 `qd_1` naming precedent). It does NOT supersede CAD-1 or
  any mini-CAD rule ID — those lineages are preserved; `EOL-DRIFT-1` names
  the cross-guard EOL-agnostic equivalence relation itself.
  This is a behavior-changing methodology rule, so per PMI-1 discipline
  applied uniformly across slices 007–032 the slice ships, **in-slice (NOT
  deferred to `/reflect`)**: (a) a `methodology-changelog.md` `## v0.47.0`
  entry forward-synced in-repo↔installed; (b) an atomic version bump
  `VERSION` + `~/.claude/ai-sdlc-VERSION` + `plugin.yaml` `version`
  0.46.0 → 0.47.0; (c) corrected `CLAUDE.md` L33 (CAD-1) + L36 (Mini-CAD)
  wording from "MUST be byte-equal" to "MUST be content-equal modulo line
  endings (EOL-agnostic per ADR-033)". The rule-ID lineage is preserved (no
  new rule ID — same precedent as PMI-1 v1.0→v1.1 / UTF8-STDOUT-1 v1.1,
  **both of which also shipped a changelog entry + version bump**; the
  earlier draft's analogy wrongly implied lineage-preservation meant skipping
  the changelog — corrected here per Critic B1). Leaving CLAUDE.md saying
  "MUST be byte-equal" after ship would be an actively-false governing
  statement and the slice-022 self-violation law (N≈9) playing out in a
  self-hosting-discipline slice — hence the in-slice correction + a substring
  regression pin.
- The 6 duplicated `_sha256` helpers collapse to one shared comparator;
  future `.md` drift guards import it instead of re-inlining raw-byte hashing.
- R-5's false-PCA-1-HALT window closes for the witnessed instances (skill
  drift rows #1/#19) and the canonical CAD-1 guard, environment-independent.
- The `;`-split shippability-runner concern (slice-032 secondary discovery)
  is **not** addressed here — distinct SCMD-1-adjacent runner-parsing issue.
  It gets a concrete tracked handle: a new risk-register entry `R-8 —
  shippability Step-5.5 runner ;-split contract unpinned` opened at
  `/reflect` (not a bare prose mention — Critic m2).

## Reversibility

**cheap**. Reverting is a one-line change per comparator (drop the
`.replace(b"\r\n", b"\n")`), deleting the shared helper/regression test, and
removing the `.gitattributes` lines — no data migration, no contract
consumer, no irreversible state. Tagged cheap and locked now because this
slice needs it to retire R-5.
