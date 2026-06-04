# Superseded flip-design (the rationale-of-record for re-scoping slice-110)

These files are the **original** slice-110 design — when slice-110 was scoped as
`flip-vault-to-external-store` (the single atomic vault-flip cut). They are
preserved here as the documented reason slice-110 was **re-scoped to the prep
slice** `make-pipeline-vault-location-agnostic`.

## What happened (2026-06-04)

The flip design went through the full review stack and was **BLOCKED**:

- `mission-brief.md` + `design.md` + `ADR-099` (execute the flip) + `ADR-100`
  (commit-slice RETIRE) — the original flip design.
- `critique.md` — first Critic, **BLOCKED** (3 blockers, 2 majors, 2 minors). It
  *executed* the flip mechanism and measured **74 methodology + 7 skills test
  failures** — exceeding the design's ~20 mid-slice tripwire with certainty.
- `critique-review.md` — meta-Critic, **EXTEND**. Reproduced every measurement
  exactly, confirmed all findings VALID with correct severities, and added
  **M-add-1** (the self-referential break is broader than `/reflect` — ALL literal
  per-slice-folder writes break post-flip) + M-add-2/3/4.

The three blockers converged on one structural truth: **the flip-readiness work
must precede the move**, because (a) a red suite cannot merge, and (b) the
in-loop skills (`/reflect`, `/archive`, `/validate-slice`, `/slice`,
`/drift-check`, `/commit-slice`) that run *after* a flip are themselves not
flip-ready — `/reflect`'s archive step is a literal in-tree `mv architecture/...`.

## The re-scope (user-ratified at TRI-1, 2026-06-04)

slice-110 was re-purposed in place (worktree + branch + folder renamed) into the
reversible **prep** slice: make the test suite + the in-loop skills + the
readiness audit **vault-location-agnostic** (resolve the vault via `VAULT_ROOT`
regardless of location), so the eventual flip is a config-only, suite-neutral
no-op. NO move happens in slice-110.

The actual flip + R-32 retirement become a small, predictable **follow-on slice**
(deferred dispositions B2 / M1 / M2 / m1 / m2 + the 36 RETIRE-behavior test
rewrites of M-add-4). `ADR-099`/`ADR-100` here are **draft references** for that
follow-on — they are NOT live decisions of the prep slice (which is why they were
moved out of `architecture/decisions/`).

See the prep slice's own `mission-brief.md` + `design.md` one level up.
