# Code Review: Slice 064 fix-code-review-diff-resolution-falsifier

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-23
**Result**: FINDINGS

## Summary

Surgical 7-file slice that delivers exactly what design.md / ADR-062 promise. Empirical execution confirms the three-source bash block resolves all 7 in-scope files correctly. The fix is correct on its own terms, but the test corpus that pins the fix carries two real loosenesses (one substring-leak across the Step-1 preamble prose; one `>= 2` filter-count assertion that admits a 3-leg / 2-filtered regression). Plus an ALWAYS-FALSE shell idiom in the default-branch resolver that escaped the dual-Critic stack because it cannot fail in the current runtime (it only matters when the inner `git symbolic-ref` succeeds with empty output — a different defect class than the slice was scoped against). 1 Major, 2 Minors. No Blockers.

## Changed files (in-scope)

```
VERSION
plugin.yaml
pyproject.toml
methodology-changelog.md
skills/code-review/SKILL.md
tests/methodology/test_methodology_changelog.py
tests/skills/code_review/test_code_review_skill.py
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

#### M1: `test_skill_md_step_1_diff_resolution_uses_union_of_three_sources` Source-(iii) assertion can be satisfied by Step-1 preamble prose alone — the test cannot detect deletion of the Source-(iii) bash command

- **Claim under review**: `tests/skills/code_review/test_code_review_skill.py:142` —
  ```python
  assert 'git diff "$base"...HEAD' in step_1, (
      "skills/code-review/SKILL.md Step 1 missing commits-vs-base source "
      "command `git diff \"$base\"...HEAD` — required as third source in "
      "the union-of-three-sources read mechanism"
  )
  ```
- **Issue**: The substring `git diff "$base"...HEAD` occurs **twice** in Step 1's section-scoped range: once at `skills/code-review/SKILL.md:37` in the preamble prose ("the single-command `git diff "$base"...HEAD` is commit-vs-commit only…") and once at `skills/code-review/SKILL.md:51` in the bash block (the actual Source-(iii) command). If a future regression deletes the Source-(iii) bash command from the block (e.g., a "let's simplify back to two sources" refactor) but leaves the preamble prose intact, this assertion still passes via the preamble substring — exactly the regression class the test is designed to prevent.
- **Evidence**:
  - Empirically `step_1.count('git diff "$base"...HEAD') == 2` on the current SKILL.md (preamble at L37 + bash command at L51). Delete the bash line and the assertion still returns True.
  - This is the same defect class as design.md "R-X1" notes the AC#1 test guards against via section-scoping, but section-scoping alone isn't sufficient when the section ALSO contains prose mentioning the substring.
  - The companion Source-(i) assertion at L126 (`'git diff "$base" --name-only' in step_1`) is NOT exposed to this leak because no preamble prose contains `git diff "$base" --name-only` (verified: count == 1). Source (ii) likewise count == 1. Only Source (iii) is leak-exposed because the preamble at L37 names exactly the commit-vs-commit form being refuted.
- **Proposed fix**: Tighten the Source-(iii) assertion to require the bash-block line specifically. Options:
  1. Assert the substring with full filter-shape: `'\ngit diff "$base"...HEAD --name-only --diff-filter=ACMR -- \':(exclude)architecture/**\''` — the preamble inline-prose form (backtick-quoted, no `--name-only`) cannot match.
  2. Scope to the fenced bash block specifically: find `"```bash\n"` … `"\n```"` boundaries within Step 1 and assert against the block body only, not the section.
  3. Assert `step_1.count('git diff "$base"...HEAD') >= 2` so the bash-block instance is REQUIRED in addition to the preamble. (Brittle if a future edit drops the preamble prose for stylistic reasons.)

  Option 1 is the cleanest — pins the same shape `test_skill_md_step_1_all_three_legs_share_filter_shape` already enforces, but anchored to Source (iii) specifically.

### Minors

#### m1: Default-branch resolver chain `[ -z "$default" ] && default=$(...)` is dead-code-as-written under the canonical happy path AND fails open silently if neither resolver returns

- **Claim under review**: `skills/code-review/SKILL.md:40-42` (bash block):
  ```bash
  default=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
  [ -z "$default" ] && default=$(git config init.defaultBranch 2>/dev/null)
  base=$(git merge-base "$default" HEAD)
  ```
- **Issue**: Two sub-issues bundled because they share a root cause:
  1. **Pipe-with-sed always returns a string** — `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null` exits non-zero on a no-remote repo, but the pipe `| sed '…'` succeeds with empty stdin. Result: `default=""` (empty string, not unset). The `[ -z "$default" ]` test then correctly triggers the fallback. So far OK — but: if BOTH commands fail, `default` is the empty string and `git merge-base "" HEAD` exits with `fatal: bad revision ''` and writes to stderr; `base` ends up empty; the subsequent three `git diff` / `git ls-files` commands then read `$base` as empty string, producing unbounded diff output or per-git-version-dependent failure. This contradicts the Step-1 documented `default-branch-unresolvable` error case at L68, which says "STOP with the BRANCH-1-shaped error and instruct user to re-run after default branch resolves" — but the bash block has NO check for empty `$default` OR empty `$base`. Claude is supposed to enforce the error case in prose, but Claude reading SKILL.md would have no programmatic signal to STOP.
  2. **Compare to the canonical NAW-1 Python implementation** at `tools/new_agent_warning_audit.py:_resolve_default_branch` (referenced by design.md L52 as "the canonical pattern slice-064 mirrors"): that function returns `None` explicitly when neither resolver succeeds, and the caller checks `if base is None: return 2 (usage)`. The bash mirror has no equivalent — it falls through silently to `git merge-base "" HEAD`.
- **Evidence**:
  - `skills/code-review/SKILL.md:40-42` vs `tools/new_agent_warning_audit.py:_resolve_default_branch` (design.md L52 cites this as the canonical reference): the Python version explicitly returns `None`; the bash version has no equivalent guard.
  - `skills/code-review/SKILL.md:68` documents the `default-branch-unresolvable` error case but the bash block at L40-42 has no programmatic way to signal it.
  - The risk is low under the canonical happy path (a repo with `origin/HEAD` set, which any cloned repo has after `git fetch`) — but the slice-064 fix itself rests on the assumption that this resolver chain is correct. A clean-room repo (e.g., a fresh CI clone without `origin/HEAD` and without `init.defaultBranch` configured) would silently misbehave.
- **Proposed fix**: Add an explicit empty-check + STOP between L42 and L44 (`if [ -z "$default" ]; then echo "default-branch-unresolvable" >&2; exit 2; fi`). Or — since SKILL.md prose is the executable contract for Claude (not actual bash) — add a Step-1 prose sentence right after L52: "If `$default` is empty after both resolvers, STOP per the `default-branch-unresolvable` error case at L68; do NOT proceed to the three union commands with an unbound `$base`."

#### m2: `test_skill_md_step_1_all_three_legs_share_filter_shape` `>= 2` count assertion admits a 3-leg / 2-filtered regression where one `git diff` leg silently drops `--diff-filter=ACMR`

- **Claim under review**: `tests/skills/code_review/test_code_review_skill.py:165-171`:
  ```python
  diff_with_filter = step_1.count("--name-only --diff-filter=ACMR")
  assert diff_with_filter >= 2, (...)
  ```
- **Issue**: The `>= 2` rather than `== 2` admits a (low-probability but real) regression class where a future edit adds a fourth `git diff` leg (e.g., "while we're here, add a staged-only Source iv") without `--diff-filter=ACMR`. With 3 `git diff` legs and 2 of them filtered (count = 2), the assertion still passes — but the SEMANTIC contract "all `git diff` legs share filter shape" is broken. The test docstring at L150-154 explicitly says "the two `git diff` legs … MUST share identical … flags" but the assertion only verifies "at least two appearances", not "all `git diff` legs have it".
- **Evidence**: The current SKILL.md has exactly 2 `git diff` legs (the canonical pattern), so the assertion currently passes with count == 2. The defect class is forward-looking only — a 3-leg regression doesn't exist today.
- **Proposed fix**: Either (a) tighten to `== 2` and document "if you add a Source-(iv) leg, update this assertion's expected count"; or (b) compute the number of `git diff "$base"` occurrences in Step 1 and assert `step_1.count("--name-only --diff-filter=ACMR") == step_1.count("git diff \"$base\"")` (filter-count equals git-diff-count, the actual semantic invariant). Option (b) is more robust against the 3-leg-future-add case, but also needs to exclude the L37 preamble's inline `` `git diff "$base"...HEAD` `` reference to avoid the same M1-class substring-leak — section-scoping to bash-block-only is the cleaner fix that addresses both M1 and m2.

## Dimensions checked

- [x] **Unfounded assumptions** — 1 minor (m1): the bash block at SKILL.md:40-42 implicitly assumes both default-branch resolvers will succeed; the documented `default-branch-unresolvable` error case at L68 has no programmatic signal from the bash block.
- [x] **Missing edge cases** — partly covered above (m1 default-branch-unresolvable failure path). No further findings.
- [x] **Over-engineering** — none. The slice is surgical (7 files, no new modules). ADR-062 §Options C correctly rejects the Route C `tools/code_review_diff_resolver.py` over-engineering.
- [x] **Under-engineering** — none. All 5 ACs have backing tests; all 7 tests pass empirically. CRSI-1 walking-skeleton v1 advisory-only disposition preserved.
- [x] **Contract gaps** — 1 major (M1): the Source-(iii) assertion's contract is "the bash command for commits-vs-base exists in Step 1", but the realized assertion is "the substring exists in Step 1 (including preamble prose)" — a contract gap between intent and realization. Plus the m1 default-branch-unresolvable contract gap between SKILL.md:68 (documented error case) and SKILL.md:40-42 (no programmatic signal).
- [x] **Security** — none. No new auth/authz/data-exposure paths. No user-controlled input flowing into shell-interpolation positions.
- [x] **Drift from vault** — none. The 7-file diff exactly matches design.md's "What's new" enumeration. ADR-062 §Decision Step 1 bash block is content-equal to the realized SKILL.md (modulo EOL). The v0.67.0 changelog entry body anchors verbatim match the entry-pin test's 8 assertions. Shippability row #64 cites BOTH ADR-062 AND NAW-1 AND ADR-061 per BCR-1 traceability axis.
- [x] **Web-known issues** — Skipped — WebSearch unavailable in this session; the git command shapes (`--diff-filter=ACMR`, `git ls-files --others --exclude-standard`, `<base>...HEAD` triple-dot) are all stable git CLI surface area.
- [x] **Cross-cutting conformance** — 1 minor (m2): the `>= 2` filter-shape assertion is loose for a hypothetical 3-leg-future regression. Compound-anchor treatment in entry-pin test (slice-063 v0.66.0 precedent for the lineage clauses) is consistent. EOL-DRIFT-1 invariant preserved. No APED-1 violations.

---

**Confidence note**: 7-file slice with significant methodology-surface impact and a heavy dual-Critic stack (1 BLOCKED first-Critic pass with 2B/4M/5m + 3 meta-Critic-added findings — 14 dispositions total, TRI-1 CLEAN). Finding 1 Major + 2 Minors after that level of scrutiny is plausible: M1 is a real test-tightness defect (substring-leak class is hard to spot without empirically counting substring occurrences against the section-scoped range), m1 is a runtime-correctness defect that escaped because it cannot fire on the current developer environment (origin/HEAD is set), m2 is a forward-looking test-tightness defect. All three are minor calibrations on top of a correct fix — none invalidate the slice's B1-falsifier-retirement claim, and empirical execution of Step 1 against this repo at this moment confirms the fix works as designed.

**Files referenced** (all absolute):
- `<HOME>\ai_sdlc\skills\code-review\SKILL.md`
- `<HOME>\ai_sdlc\tests\skills\code_review\test_code_review_skill.py`
- `<HOME>\ai_sdlc\tests\methodology\test_methodology_changelog.py`
- `<HOME>\ai_sdlc\methodology-changelog.md`
- `<HOME>\ai_sdlc\architecture\shippability.md`
- `<HOME>\ai_sdlc\architecture\decisions\ADR-062-extend-naw-1-pattern-to-code-review.md`
- `<HOME>\ai_sdlc\tools\new_agent_warning_audit.py` (referenced from design.md as canonical pattern source)

---

## Builder disposition (CRSI-1 v1 advisory-only)

Per CRSI-1 v1 walking-skeleton (slice-060 / ADR-059): findings are **advisory only**. No triage required; auto-advance to `/validate-slice` proceeds. Slice-063 precedent (reflection L36 + L42): code-Critic findings on a slice with already-CLEAN dual-Critic stack are declined in-band per v1 discipline and deferred to a future slice for bundled cleanup.

All 3 findings (M1, m1, m2) are declined in-band per CRSI-1 v1 + slice-063 precedent. They are nominated for slice-065+ as a bundled test-tightness + bash-resolver-robustness cleanup slice:

- **M1** — Source-(iii) substring-leak in the BFRD-1 repro test. Fix: section-scope to bash-fenced block only (Option 1 / 2). This is a real test-tightness gap but the slice's substantive correctness (the B1 falsifier retirement on /code-review's surface) is unaffected.
- **m1** — default-branch resolver no-programmatic-STOP. Fix: either add the `[ -z "$default" ]` STOP check to the bash block, or document the obligation in Step 1 prose. Both options are in slice-065+ scope.
- **m2** — `>= 2` filter-shape count assertion forward-looking gap. Fix: tighten to `==` count-equals-git-diff-count semantic invariant. Bundles with M1's section-scoping fix (same test surface).

These deferrals are logged in build-log.md Events + carry forward to `/reflect`'s "Deferred" section + slice-065+ candidate list at `/slice`.
