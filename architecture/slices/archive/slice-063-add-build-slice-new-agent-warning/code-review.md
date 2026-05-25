# Code Review: Slice 063 add-build-slice-new-agent-warning

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths; augmented WT-aware diff resolution per user-ratified SOAD-1 option to route around the /code-review SKILL.md v1 `git diff <base>...HEAD` falsifier — the same B1 falsifier class slice-063 just retired for NAW-1's read mechanism; slice-064+ candidate to mirror the union-of-three-sources fix to /code-review itself)
**Date**: 2026-05-23
**Result**: FINDINGS (1 minor only — no blockers, no majors)

## Summary

The slice ships a structurally clean implementation of NAW-1. The union-of-three-sources read mechanism is correct, both injection seams match their declared callable signatures, the binary exit contract is preserved by construction (zero code paths return exit 1), all 7 regression tests pass, self-application is vacuous-clean, and the PMI-1 5-inventory fan-out is fully discharged. PMI-1 / INST-1 / UTF8-STDOUT-1 / NAW-1 self-application all run clean against the working tree. The Critic + meta-Critic stack visibly caught the same defect classes (B1 commit-vs-commit falsifier, M3 fallback-`main` misattribution, m3 bootstrap-brittle test) that code-review would otherwise have surfaced — there is nothing left for me to find at blocker or major severity. One genuine minor (m1 — narrow docstring ambiguity + UX wart in `_resolve_default_branch`'s FileNotFoundError handling) survives. Honest "no blockers, no majors" verdict.

## Changed files (in-scope)

```
INSTALL.md
VERSION
methodology-changelog.md
plugin.yaml
pyproject.toml
skills/build-slice/SKILL.md
tests/methodology/test_build_slice_skill.py
tests/methodology/test_methodology_changelog.py
tests/methodology/test_risk_register_audit_real_file.py
tests/methodology/test_utf8_stdout_regression.py
tools/install_audit.py
tools/new_agent_warning_audit.py            (NEW)
tests/methodology/test_new_agent_warning_audit.py  (NEW)
```

## Findings

### Blockers (advisory in v1 — slice-062 was supposed to add verdict-driven block on /validate-slice; explicitly re-deferred to slice-064+ at slice-063 /slice Step 3 since slice-063 picked R-18 mitigation over /code-review v2)

None.

### Majors

None.

### Minors

#### m1: `_resolve_default_branch` early-returns on first-call FileNotFoundError, skipping the second call's identical handler

- **Claim under review**: `tools/new_agent_warning_audit.py:163-166` returns `None` from the symbolic-ref `FileNotFoundError` clause, then `tools/new_agent_warning_audit.py:168-179` has a SECOND identical `try / except FileNotFoundError: return None` around the `init.defaultBranch` call.
- **Issue**: If the FIRST `subprocess.run(["git", "symbolic-ref", ...])` raises `FileNotFoundError` (git binary genuinely missing), the function returns `None` at L166 and the second `try/except` at L168-179 is unreachable. The docstring at L144-151 says "Resolve the repo's default branch via `git symbolic-ref` **then** `git config init.defaultBranch`", which reads as a fallback chain, but a missing-git environment will short-circuit at the first call — fine for correctness (both paths funnel to `None` → exit 2 usage), but the SECOND `try/except FileNotFoundError` at L177-178 is dead code under any realistic environment (if the first `subprocess.run` succeeded at finding the `git` binary, the second one will too — `git` doesn't disappear mid-function). Per Fowler *Refactoring* 2nd ed. "speculative generality" smell — a guard wrapping an unreachable failure mode.
- **Evidence**: Cross-comparison with the canonical BRANCH-1 implementation at `tools/branch_workflow_audit.py:127-146` — BRANCH-1's `_resolve_default_branch` uses `_run_git()` (a wrapper around `subprocess.run`) WITHOUT any `try/except FileNotFoundError` because the BRANCH-1 codepath funnels FileNotFoundError up to its caller (per design.md L25 the NAW-1 implementation declares it "mirrors BRANCH-1's `_resolve_default_branch` at `tools/branch_workflow_audit.py:127-146` byte-for-byte semantics" but the implementations diverge on this point — BRANCH-1 propagates, NAW-1 catches-and-returns-None).
- **Proposed fix**: Either (a) remove the inner `try/except FileNotFoundError` at L177-178 since it is unreachable (the L163 handler already absorbed it), or (b) more defensibly — drop BOTH `try/except FileNotFoundError` blocks from `_resolve_default_branch` entirely and let `FileNotFoundError` propagate to `check()`'s explicit handler at L299-303 (which already maps it to `_USAGE_GIT_MISSING` with a more user-actionable error message than the silent `None → _USAGE_DEFAULT_BRANCH_UNRESOLVABLE` path the current code takes). Option (b) also fixes a UX wart: under the current code, a genuinely-missing-`git` environment surfaces `_USAGE_DEFAULT_BRANCH_UNRESOLVABLE` ("Configure an `origin/HEAD` ref or set `init.defaultBranch`") instead of `_USAGE_GIT_MISSING` ("`git` command not found on PATH") — the user gets misleading remediation advice. Severity stays minor because (i) the broken UX only fires on a missing-git environment which is highly unusual, and (ii) exit code is still 2 either way — no functional regression. But the error attribution drift IS a real (small) defect, not cosmetic.

## Dimensions checked

- [x] **Unfounded assumptions** — none. The `_resolve_added_agent_files` docstring at L182-199 accurately describes the union-of-three-sources mechanism; the actual `_run` helper at L202-210 raises `CalledProcessError` (not silently absorbs) so the contract holds. Verified by tracing each subprocess call site. WARN-line template at L115-123 contains all three required anchors (`{agent_path}`, "restart Claude Code", "R-18") — verified by reading the template literal directly.
- [x] **Missing edge cases** — none of consequence:
  - **Empty repo** (no commits): `git diff master` on a repo with no `master` ref → non-zero exit → caught at L304-317 → exit 2 usage (correct fail-closed).
  - **Whitespace-only agent paths**: `_run` filters via `if ln.strip()` (L210) — empty/whitespace lines correctly excluded from the union.
  - **Concurrent slices** / **race**: read-only audit, no shared state mutation — N/A.
  - **CRLF/LF**: pathspec matches by path-string semantics, not file content; no byte-equality compare → EOL-DRIFT-1 doesn't apply.
  - **Detached HEAD**: the `commits-vs-base` source (iii) uses `{base}...HEAD` triple-dot which resolves to merge-base — works in detached state.
  - **Pathspec false-positive class** (`agents/AUTHORING.md` etc.): explicitly documented and accepted as known false-positive class at `tools/new_agent_warning_audit.py:64-76`; minimal-cost WARN, never HALTs — acceptable per ADR-061 §Consequences.
- [x] **Over-engineering** — m1 (above) is the only candidate. The two injection seams (`default_branch_resolver`, `added_files_resolver`) might LOOK speculative, but each has a concrete in-test caller (lines 92-96, 108-110, 152-154, 213-228 of `test_new_agent_warning_audit.py`) — not Fowler speculative-generality. The `CheckResult` dataclass clone of AVFS-1/TVFS-1 is justified by structural-sibling pattern preservation (ADR-061 §Decision L57) — also not speculative.
- [x] **Under-engineering** — none. All 5 ACs have code paths delivering them, all 9 TF-1 plan rows are PASSING, all 14 Step 6 audits pass (including NAW-1's vacuous self-application), shippability row #63 cites the BCR-1 traceability triple (NAW-1 + R-18 + ADR-061), R-18 retirement field-line at `architecture/risk-register.md:303` correctly reads `**Status**: retired` with the `**Retired**: slice-063-...` provenance at L304 and the retirement paragraph at L319.
- [x] **Contract gaps** — none. Function signatures all carry type hints; public functions all carry docstrings; `_resolve_added_agent_files` contract explicitly documents both raise classes (`CalledProcessError` + `FileNotFoundError`) and the caller (`check()`) handles both. Binary exit contract is preserved by construction — verified by inspection: the only assignments to `result.exit_code` are at L284 (=2), L293 (=2), L301 (=2), L306 (=2), L321 (=0), L327 (=0). No code path sets exit_code to 1. The pytest assertion `result.exit_code == 0` on BOTH clean AND warn branches (tests at L98, L112, L156, L178, L190, L219, L228) is the load-bearing pin — verified passes.
- [x] **Security** — none. The audit is read-only — `subprocess.run(["git", ...])` calls are list-form (no shell=True), no user input flows in (cwd comes from `--root` argv resolved via `Path.resolve()`), no env vars consumed, no network, no credentials, no logging of secrets/PII. The WARN-line template L115-123 does not interpolate any user-controlled input besides the agent path string (which comes from git's own output, not raw user input). No OWASP-class vectors.
- [x] **Drift from vault** — none.
  - design.md "Components touched" claim (slice ships 11 modified + 2 new files) matches the actual file list in the working tree.
  - design.md item 5's BC-PROJ-9 5-inventory fan-out (plugin.yaml + install_audit._CANONICAL_TOOLS + test_utf8_stdout._ROOT_ONLY_TOOLS + INSTALL.md ×2 + shippability row) is fully discharged — verified all 5 sites changed (plugin.yaml:121-122; install_audit.py:104; test_utf8_stdout_regression.py:104; INSTALL.md:22 + L166; shippability.md row #63).
  - design.md item 8's EPGD-1 anchor list (7 anchors numbered (a)-(g) in the test docstring) matches the 7 substring assertions in `test_v_0_66_0_naw_1_entry_present_in_repo` at `test_methodology_changelog.py:4211-4245`. **Small caveat worth noting (sub-minor; not filed as a finding)**: design.md item 8 says "**8 anchors**" in prose, but actually enumerates 7 anchors in the test docstring (the slice-060 + slice-062 precedent format counts the `mints + supersedes nothing` lineage clauses as a SINGLE anchor (e), which would make 8 if counted as 2; the test asserts both substrings in one `assert` at L4229. Same convention as slice-060 and slice-062 entry-pin tests). Cross-document consistent, just the prose "8" vs assertion count "7" wording is borderline — not load-bearing.
  - ADR-061 §Decision L60-67 union-of-three-sources description matches `_resolve_added_agent_files` implementation verbatim. M3 critique fix (`None` instead of `main` fallback) correctly implemented at `tools/new_agent_warning_audit.py:144-179` (returns `None` on both unresolvable paths) and at design.md L25 ("`_resolve_default_branch` does NOT have a 'main' fallback in the implementation").
  - PMI-1 atomic-bump leg count (5) matches: VERSION=0.66.0, plugin.yaml.version=0.66.0, pyproject.toml [project].version=0.66.0, `## v0.66.0` header present, installed `~/.claude/ai-sdlc-VERSION` per AVFS-1 forward-sync.
  - INSTALL.md tool-count `28` matches actual tool count (PMI-1 + INST-1 audits both confirm 28).
- [x] **Web-known issues** — checked. Three queries time-boxed at <2 minutes:
  - `git diff <base>` (working-tree-vs-base) semantics — official docs at `git-scm.com/docs/git-diff` confirm 2-dot vs 3-dot semantics behave as the slice's docstring describes; the B1 critique fix is web-sourced (URL embedded in the audit's docstring at L16-17 and in the changelog entry L41-42).
  - `git ls-files --others --exclude-standard` for untracked enumeration — canonical pattern, no recent deprecations or behavior changes.
  - `subprocess.run(..., text=True, encoding="utf-8", capture_output=True)` — standard Python 3.10+ pattern, no recent deprecations. No `shell=True` anywhere. No known-bad patterns.
- [x] **Cross-cutting conformance** —
  - **RSAD-1**: NAW-1's own slice (slice-063) survives NAW-1 — vacuous-clean (verified by `$PY -m tools.new_agent_warning_audit` against the working tree: exit 0, no stdout).
  - **APED-1**: The audit's new pathspec `agents/*.md` matching rule was empirically executed against an adversarial battery — 4 documented states tested (clean / warn-via-untracked / warn-via-staged / negative-contrast no-diff) via 7 pytest tests; all 7 pass. Also re-ran the three sources manually against a fresh tmp git repo: source (i) returned empty pre-staging, the agent path post-staging; source (ii) returned the untracked file; source (iii) returned the path post-commit. The B1 critique-fix sources behave as documented.
  - **EOL-DRIFT-1**: no new byte-equality `==` compare on `.md` file content added.
  - **Language-version conformance**: `from __future__ import annotations` + `str | None` syntax is Python 3.10+ — matches `pyproject.toml:24` `requires-python = ">=3.10"`. No docstring escape-sequence SyntaxWarnings (Python 3.12+ `\-` class).
  - **Tooling-doc-vs-implementation parity**: the WARN line template literal at L115-123 matches the test's substring assertions at `test_new_agent_warning_audit.py:128-133` (agent path + "restart Claude Code" + "R-18") AND matches ADR-061's "Attributed WARN message" template at L77. No drift.
  - **Algorithm-path-conformance**: NAW-1 is appended to the Step 6 enumeration as the LAST gate (after TVFS-1), composing additively with the 13 existing audits. No pre-existing branch's behavior is mutated. PCA-1 chain audit verifies separately.
  - **Build-time-runtime classes** (Claude Code agent registry hot-reload): explicitly out of scope for `/code-review` per CRSI-1 v1 — this is a runtime-environment / cross-session class.

## Notes / observations (not findings)

1. **Edge case worth a /reflect lesson, not a finding**: the m1 dead-code observation surfaces a small documentation accuracy claim ("byte-for-byte semantics" with BRANCH-1 at design.md L25) that is not actually byte-for-byte. NAW-1's resolver catches `FileNotFoundError` inside the function; BRANCH-1's `_resolve_default_branch` does not. Future slices that promote NAW-1's resolver pattern to a shared helper (or vice-versa, normalize NAW-1's resolver to match BRANCH-1's propagation pattern) should resolve the divergence consciously. The current divergence is benign — both produce a `None` return on any unrecoverable git-resolution failure — but the design.md "byte-for-byte" claim slightly overstates fidelity. Filing as observation rather than finding because the actual implementation choice (catch + return None vs propagate) is locally defensible.

2. **Honesty rule discharge**: The 9 central concerns the task description called out (union-of-three-sources read mechanism, binary exit contract by construction, WARN-line template anchors, default-branch resolver returning `None`, subprocess error handling, slice-063's own self-application, PMI-1 5-inventory fan-out completeness, cross-document coherence, test seam-injection signature correctness) — all 9 are clean. Five separate audits run against the working tree confirm zero violations (NAW-1 self, PMI-1, INST-1, UTF8-STDOUT-1, and the 4 anchor-pin tests). The slice's dual-Critic stack already caught the high-value defects (B1 + M1-M4 + m1-m5 at /critique; M-add-1 through M-add-3 at /critique-review). The code-Critic third-pass produces one small observation about dead-code in the resolver, and otherwise validates the work. This is a no-blockers, no-majors slice — code-review verdict matches the dual-Critic verdict (CLEAN per TRI-1).

3. **Meta-observation on /code-review SKILL.md v1 diff-resolution falsifier**: per the user's SOAD-1 ratification at /code-review Step 1, the agent was spawned with an augmented WT-aware file list (routed around the `git diff <base>...HEAD` falsifier — the SAME B1 class slice-063 just retired for NAW-1). The /code-review SKILL.md v1 itself carries the falsifier; slice-064+ candidate to mirror NAW-1's union-of-three-sources fix to /code-review's diff resolution. Without the manual augmentation, this review would have surfaced `Result: NO-CODE-CHANGES` (false-positive) and slice-063 would have shipped with zero adversarial code review. The augmentation worked as intended.

## Disposition summary

**m1** is **advisory only per CRSI-1 v1 walking-skeleton** (no verdict-driven block; slice-064+ candidate for v2 with TRI-1 + verdict-block). Builder declines to fix in-band — fixing post-`/build-slice` would set a precedent that /code-review is a build phase (which v1 explicitly is not). m1 is documented for /reflect Step 4 disposition + as a slice-064+ candidate (alongside the /code-review SKILL.md v1 diff-resolution falsifier per Note 3).
