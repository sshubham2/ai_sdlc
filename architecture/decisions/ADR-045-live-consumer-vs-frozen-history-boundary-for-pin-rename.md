---
id: ADR-045
title: Shippability `::`-selectors are LIVE consumers (realigned in-slice); changelog/ADR/fixtures/archive are append-only frozen history (not renamed)
date: 2026-05-18
slice: slice-042-realign-entry-present-pin-names-to-decoupled-shape
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-045: Live-consumer vs frozen-history boundary for the entry-present pin rename

## Context

The `_entry_present_in_repo_and_installed` family is referenced from many
surfaces. slice-041's Deferred-L22 characterized the blast radius as
"41-changelog-line + 27-shippability + ~17-ADR/lessons/index
**frozen-history-vs-rewrite** ... append-only shipped history" — i.e. it lumped
the shippability references in with the append-only frozen history. That
characterization is **imprecise and load-bearing if followed literally**:
`architecture/shippability.md` `Machine-cmd` cells are executed verbatim by the
/validate-slice Step-5.5 catalog runner (SRSC-1 / ADR-039). A `::`-selector
pointing at a renamed-away function makes pytest collect zero tests → a false
catalog FAIL across every affected row (the R-8 class). The shippability catalog
is a **live executable contract maintained to track reality** (precedent: row 7
carries an in-place slice-008 supersession note), not append-only frozen text.

A rename that touches the functions but treats shippability as "frozen" would
ship a broken catalog. The boundary must be drawn explicitly.

## Options considered

1. **Two-bucket boundary**: shippability `::`-selectors (+ the audit f-string that pins them) = LIVE consumers, realigned in the same fix block; methodology-changelog `**Validation**:` lines + ADRs + fixtures corpus + `archive/**` + `_index.md` historical prose = append-only frozen history, NOT renamed. Pros: catalog stays green; history stays intact; matches slice-035 executable-bind-vs-prose precedent. Cons: post-slice the changelog records the old name while the live catalog uses the new name — an intentional, correct divergence (history ≠ live contract).
2. **Everything frozen (follow Deferred-L22 literally)**: rename nothing that has any historical co-reference. Pros: zero history risk. Cons: the slice cannot rename the functions at all without orphaning 67 live shippability consumers → ships a broken Step-5.5 catalog. Defeats the slice.
3. **Everything live (rename all 159+ refs incl. changelog/ADRs)**: Pros: globally name-consistent. Cons: rewrites append-only shipped history across 39 changelog Validation lines + 13 ADRs + frozen Critic-backtest corpus — the precise irreversible hazard slice-041 scope-cut to avoid; violates CLAUDE.md append-only ADR/changelog discipline.

## Decision

Option 1. The boundary is **executable-liveness**, not co-occurrence with
history, and is stated as a **predicate + pre-edit snapshot** (not a hand-typed
list — hand-transcribed counts drifted across BOTH the original draft and the
rev-1 "fix": original said 13 ADR / 39 changelog / 40 def / 67 ship; rev-1 said
16 / 43 / 37 / 67; the recomputed-via-anchor truth on 2026-05-18 is **13 ADR /
40 changelog / 37 def / 69 ship-occ (32 unique, 28 rows)**. Predicates do not
drift; the build-step-1 grep is authoritative and all counts here are the
2026-05-18 anchor-grep snapshot, reconciled to it):

- **LIVE (realign in this slice's fix block):** `architecture/shippability.md` (**69 occurrences = 32 unique names — 28 `_entry_present` + 4 `_entry_names` — across 28 rows** `[7–27, 30, 32, 35, 37, 38, 39, 41]`); `tests/methodology/test_shippability_decoupling_audit.py:57` (asserts a shippability `Machine-cmd` literal); the **37** `def`s in `test_methodology_changelog.py` + its 2 in-file comments (`:1821`,`:2936`); the 4 sibling active-test descriptive refs; **`tools/methodology_changelog_forward_sync.py:58`** (live source docstring naming the current v0.53.0 pin — leaving it stale re-introduces the name↔reality contradiction this rename removes; FBCD-1/RPCD-1 class).
- **FROZEN (NOT renamed — predicate):** `methodology-changelog.md` all `## v0.NN.0 **Validation**:` family refs (**40** occ / 32 unique as of 2026-05-18; forward-synced ⇒ untouched ⇒ no MCFS-1 interaction); **every `architecture/decisions/ADR-*.md` EXCEPT ADR-044 and ADR-045** (predicate is leak-proof independent of count; **13** prior files contain the fn-name family — ADR-016/018/031 do NOT, contrary to the rev-1 claim); `tests/methodology/fixtures/archive_backtest_corpus/**`; `architecture/slices/archive/**`; historical vault record-prose `architecture/slices/_index.md` (**3**), `architecture/lessons-learned.md` (2) — record what happened, not executable binds. (`critic-calibration-log.md` = 0 family refs — not a bucket.)
- **Build-time invariant**: snapshot the FROZEN set's per-file count + path list pre-edit; assert byte-identical post-edit; any FROZEN drift = hard STOP.

The resulting changelog(old-name) vs catalog(new-name) divergence is **correct**:
the changelog is a point-in-time record of what the pin was *called when it
shipped*; the catalog is a forward-looking executable contract that must name the
function *as it exists now to actually run*. This is exactly the slice-035
identifier-truth split (executable binds realigned; frozen prose preserved).

## Consequences

- The Step-5.5 catalog stays green post-rename (all live `::`-selectors track the rename).
- Append-only shipped history is preserved byte-for-byte; a pre/post inventory grep over the FROZEN set (count + paths identical) is a slice must-not-defer.
- A future reader of a shipped changelog `**Validation**:` line will see the historical name; the live catalog and test file use the current name — documented here so the divergence is not later mistaken for drift.
- Corrects the record: slice-041 Deferred-L22's "27-shippability ... frozen-history" framing is superseded by this liveness-based boundary for the purpose of this rename.
- **ADR-044 intentionally cites the OLD family name exactly once** (ADR-044's Decision section, the no-`_sub_` `entry_names_three_modes` example — the canonical record of *which* names the rename targets). **ADR-045 itself carries ZERO old-name literals** — it refers to that example only in its post-rename form `test_v_0_36_0_entry_names_three_modes_in_repo` (ADR-044 holds the pre-rename `_and_installed` form), so ADR-045's zero-claim is self-true (DR-1 M3-sev corrected the rev-1 prose that overstated "ADR-044/045 cite the old name"; a build-time T0 check then caught that the M3-sev fix had itself re-introduced one literal into ADR-045 — slice-032 design-correction-is-unguarded class — and removed it). ADR-044's single citation is the authoritative documentation of the rename and is **NOT an identifier-truth defect** — a future identifier-truth slice MUST NOT "fix" it. This is why the FROZEN predicate excludes ADR-044/045 from the carve-out (ADR-044 is the rename's own record). Post-rename invariant: exactly **1** intentional active `_and_installed` literal exists repo-wide (ADR-044), plus the FROZEN-predicate set. (RSAD-1 recursive-self-application, consciously dispositioned per M3 / M3-sev.)

## Reversibility

Cheap. The boundary is a scoping decision realized by which files the mechanical
rename map is applied to. Re-drawing it later is another mechanical pass. The
frozen set is deliberately the *irreversible* part and is excluded by design, so
no irreversible action is taken.
