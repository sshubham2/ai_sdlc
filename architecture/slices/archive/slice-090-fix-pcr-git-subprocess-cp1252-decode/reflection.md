# Reflection: Slice 090 fix-pcr-git-subprocess-cp1252-decode

**Date**: 2026-05-31
**Shipped**: YES-WITH-DEFERRALS

## Validated
- `encoding="utf-8"` on the 9 `text=True` git subprocess sites fixes the cp1252 crash — validated on the real Windows/cp1252 host: the two behavioral repro tests (round-trip + claim extraction) ran (NOT skipped) and PASS; pre-fix they failed with the user's exact `UnicodeDecodeError: byte 0x8f` reader-thread signature.
- `text=True` + `encoding="utf-8"` is correct, not redundant — code-Critic confirmed against official Python docs + the exact CVE-class bugs (cpython #105312, pip-audit #573).
- The site partition (9 decode + 4 byte-mode, all literal `["git", …]` argv) is exactly correct — verified independently by the meta-Critic and the code-Critic reading all 13 sites, and pinned by the AST guard (count = 9).

## Corrected
- "~10 sites" (mission-brief/design/ADR draft) → reality is exactly **9 decode sites + 4 byte-mode** = 13 total — corrected across all three artifacts at /critique (M1). Design-doc precision, not a behavior correction.
- `_git_show_stage` docstring said "Returns empty string on subprocess failure" → reality also passes back `None` from `proc.stdout` — corrected the docstring at /code-review (m2).

## Discovered
- **cp1252 git-subprocess decode crash** — added to risk register as [[risk-register#R-30]] (mitigating: core crash retired by this slice; residuals open).
- **Strict-decode residual (Major)**: a genuinely non-UTF-8 git payload still silently returns `None` → re-admits the exact VAULT_CLAIM-bypass path. Tracked under R-30 residual #1; queued follow-up = non-silent reader-thread failure.
- **CI-coverage limitation**: the behavioral repro skips on UTF-8 CI; the AST presence-scan is the only cross-platform guard, and monkeypatch-forcing cp1252 is infeasible (subprocess C-level decode). Tracked under R-30 residual #2.
- **stranded_slice_audit branchless blind spot** — added as [[risk-register#R-31]]: the slice-087 detector only sees unmerged `slice/*` branches, so the in-flight branchless slice-089 was invisible at the `/slice` consult (`status: clean`). Caught only by a fresh `git status`.
- **R-28 firsthand again**: slice-089 has leaked its commit-slice SKILL.md edits into the installed `~/.claude/` (404 lines) without committing them in-repo (390 lines), causing 3 sibling-induced shippability FAILs on slice-090's validate. Pure R-28 shared-`~/.claude/` contention.
- **Same `text=True`-without-`encoding=` class likely in other tools/*.py** — feeds the queued `audit-cp1252-decode-pattern-across-tools` candidate; ADR-082 names the predicate kernel as the reuse seam.

## Deferred
- Non-silent reader-thread failure (R-30 residual #1) — reason: out of scope (this slice's contract is "UTF-8 content no longer crashes"); lands in: a follow-up slice.
- Repo-wide cp1252 audit — reason: ADR-082 scoped module-only; lands in: `audit-cp1252-decode-pattern-across-tools` (queued).
- stranded-audit branchless detection (R-31) — reason: separate concern; lands in: `fix-stranded-audit-branchless-blindspot` (queued).
- Risk registration of the cp1252/strict/CI/detector items — done this /reflect (R-30, R-31).

## Critic calibration

Per TRI-1, scored against the `critique.md` `## Triage` dispositions + reality observed at build/validate:

- **B1** (AST predicate would false-flag byte-mode sites): **VALIDATED** — ACCEPTED-FIXED; reading the real module confirmed L397/403/1378/1384 are `capture_output=True` without `text=True`; the rewritten `text=True`-keyed predicate is correct (AST test count = 9 / byte-mode = 4 at build). Severity Blocker→Major (meta-Critic) was the right recalibration — the defect was in a not-yet-written test, already corrected in spec.
- **M1** (imprecise ~10/L713-omitted): **VALIDATED** — exact count of 9 (incl. L713) confirmed by the live diff.
- **M2** (AC#3 unbounded + shippability propagation): **VALIDATED** — AC#3 named; AST-test shippability row #96 added at build.
- **M3** (TF-1 rows missing AC#2/AC#3): **VALIDATED** — and reality bit at build: the first AC#3 row I wrote used an invalid `N/A` status and TF-1 strict refused; fixed to two PASSING regression-test rows.
- **m1** (strict-errors residual): **VALIDATED** — meta-Critic's Minor→Major upgrade was right; registered as a first-class R-30 residual.
- **m2** (shippability #95 provenance): **VALIDATED** — confirmed authored by this slice's /repro.
- **M-add-1** (meta-Critic, UTF-8 CI coverage gap): **VALIDATED** — real; documented two-layer model; fix (i) confirmed infeasible empirically.
- **M-add-2** (meta-Critic, ADR generalization seam): **VALIDATED** — reuse-seam sentence added to ADR-082.
- code-Critic: **0 blockers / 0 majors / 2 minors** (docstring precision) — both VALIDATED + applied in-slice; it empirically confirmed the fix works.

**Missed by Critic**: the design+meta Critics did not flag that the TF-1 AC#3 row would need a valid `{PENDING,WRITTEN-FAILING,PASSING}` status (a "no-new-test" AC has no natural test-first row) — it surfaced at build Step 6 TF-1 strict refusal. Minor process gap, not a design defect. Candidate `/critic-calibrate` probe: "does every AC have a TF-1 row with a VALID status, including no-regression ACs?"

**Pattern**: the 3-Critic stack complementarity held again, non-overlapping as in slices 086-088 — design-Critic = artifact precision (counts/L-numbers/TF-1/shippability propagation); meta-Critic = test-coverage-adequacy (M-add-1, which the first Critic structurally missed by never asking *which tests run on CI*) + severity recalibration (B1↓, m1↑); code-Critic = empirical confirmation (ran the decode on the real host) + contract honesty (docstring `None`-passthrough). Reinforces slice-088's lesson: a cp1252 risk-flag must be checked against the codebase's canonical mechanism — here the design correctly distinguished subprocess-input decode (this slice) from UTF8-STDOUT-1's stdout reconfigure, so no Critic mis-prescribed.

## Lessons for next slice
- **A `text=True` subprocess decode failure is SILENT on Windows** — it raises in the pipe-reader thread, is NOT re-raised by `subprocess.run`, and returns `stdout=None`. Any helper that captures git/CLI output with `text=True` and no `encoding=` is a latent silent-data-loss site, not just a crash site. Always pass `encoding="utf-8"`.
- **A two-layer test model is correct when a bug is platform-specific**: a behavioral repro that `skipif`s on the non-affected platform PLUS a platform-independent structural (AST) guard. Don't try to force the platform condition if the mechanism (here: subprocess C-level locale read) doesn't allow it.
- **Run a fresh `git status` before the `/slice` stranded consult** — the consult only sees branches, not branchless in-flight scaffolds; the in-flight slice-089 was invisible to it.
- **Next slice uses a real BRANCH-2 worktree** (user directive) — slice-090's WORKTREE=skip was forced by entangled parallel scaffolds; resolve the parallel state first.

## Vault updates made (thin vault)
- [[risk-register.md]] — added R-30 (cp1252 decode, mitigating + 2 residuals) and R-31 (stranded-audit branchless blind spot, open)
- [[decisions/ADR-082]] — created (UTF-8-strict git-subprocess decode; reuse-seam note)
- This slice's [[design.md]] — corrected site count to exact 9 + two-layer coverage model; [[mission-brief.md]] TF-1 plan + AC#2/AC#3 rows; [[shippability.md]] rows #95 (repro) + #96 (AST guard)
- `tools/parallel_conflict_resolver.py` — 9 `encoding="utf-8"` kwargs + `_git_show_stage` docstring honesty
