---
id: ADR-046
title: Split-slice follow-up folders/branches are numeric `slice-NNN-`; the `NNNx` letter is a prose lineage label only, and BRANCH-1 emits an actionable convention-naming rejection for the letter-suffixed shape
date: 2026-05-18
slice: slice-043-codify-split-slice-folder-naming-convention
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-046: Split-slice folder-naming convention + actionable BRANCH-1 rejection

## Context

`tools/branch_workflow_audit.py` binds the slice folder to its branch through
two strict regexes: `_SLICE_BRANCH_RE = ^slice/(\d{3})-(.+)$` (line 59) and
`_SLICE_FOLDER_RE = ^slice-(\d{3})-(.+)$` (line 62). Both require **exactly
three digits** — no letter suffix.

The project routinely produces *split slices*: a slice whose dual-Critic loop
fails to converge is split into follow-ups labelled `030A` / `030B` / `030C`
in prose, risk-register sub-entries, and reflection lineage. The actual
folder/branch convention has been: **numeric folder, letter is a prose label
only** — slice-030A shipped as folder `slice-030-...` (the "030A" label lived
only in prose); slice-031 was *initially* created as `slice-030B-complete-...`,
which made `branch_workflow_audit` exit 2 (`usage-error: slice folder name
does not match slice-NNN-<name> pattern`), and was renamed mid-build to
canonical numeric `slice-031-...` with "030B" retained as a prose lineage
label. That mid-build folder+branch+id rename + cross-ref churn is **R-6**
(open, low-band, recurring): the convention was *implicit*, the audit's
rejection message gave *no guidance toward it*, and the next split slice
(030C → slice-041) was a latent repeat.

## Options considered

1. **Codify the convention + improve the rejection message; keep the strict
   `\d{3}` accept regex** (option (a)).
   - Pros: matches the project's existing de-facto practice; behavior-preserving
     (letter-suffixed folders were *already* rejected — only the message text
     and a doc sub-clause change); zero blast radius on the numeric slice-key
     space; firmly in the conformance/clarification class (no new gate, no
     accept-set change, no rule-ID/version-bump obligation).
   - Cons: split-slice follow-ups still cannot encode the `NNNx` label in the
     folder name (acceptable — the label is prose lineage, the number is the key).
2. **Widen `_SLICE_FOLDER_RE`/`_SLICE_BRANCH_RE` to `slice-(\d{3})([A-Z]?)-`**
   (option (b)).
   - Pros: lets split-slice folders encode the lineage label literally.
   - Cons: contradicts the globally-unique *numeric* slice-numbering rule
     (`/slice`: `new = max(existing)+1`); forks the key space consumed by
     `_index.md` / `archive/_index.md` catalogs, `_SLICE_BRANCH_RE` branch
     binding, and the `_make_slice_folder` (`slice-{n:03d}`) test fixture;
     broad, expensive blast radius; would itself be a behavior change
     requiring a new rule-ID + changelog + PMI-1 bump.

## Decision

**Option (a).** The split-slice folder-naming convention is made explicit:
*split-slice follow-up slices use a numeric `slice-NNN-` folder and
`slice/NNN-<name>` branch at the next free slice number; the `NNNx` letter
(e.g. `030C`) is a prose lineage label only — it never appears in the folder
or branch name.* This is codified as a sub-clause of the **Branch-per-slice**
bullet in root `CLAUDE.md`.

`tools/branch_workflow_audit.py` keeps `_SLICE_FOLDER_RE` strict (numeric-only
accept unchanged) and adds a **diagnostic-only** secondary regex
`_SPLIT_SLICE_FOLDER_RE` (`^slice-(\d{3})([A-Z]+)-(.+)$` — **uppercase-only**:
the documented lineage label is uppercase `030A`/`030B`/`030C`, so a lowercase
malformed name like `slice-030misc-x` correctly falls through to the generic
message rather than receiving the split-slice-specific guidance; per Critic
m1, this is intentional message-precision, not permissive-by-default). When
the strict match fails, if the folder name matches the split-slice shape the
existing `usage-error` (kind unchanged, exit code 2 unchanged) carries an
enriched, actionable message that names the convention and the
next-free-number rename remedy and cites this ADR / BRANCH-1; otherwise the
existing generic `slice folder name does not match slice-NNN-<name> pattern`
message is preserved verbatim. A regression test pins the canonical-accept,
the uppercase-letter-suffixed-actionable-reject, and the lowercase-falls-
through-to-generic paths so the convention cannot silently regress and the
next split slice cannot re-discover R-6.

**R-6 retirement mechanic (Critic M2 — explicit):** RR-1
(`tools.risk_register_audit`) derives a risk's status **solely from its
`**Status**:` field line**. Retiring R-6 therefore requires flipping
`architecture/risk-register.md`'s R-6 `**Status**: open` line to
`**Status**: retired` **and** adding a `**Retired**: slice-043-... (2026-05-18;
ADR-046)` line — mirroring R-7's two-part shape. Adding only the `**Retired**:`
prose line without flipping `**Status**:` would leave RR-1 reporting R-6 as
`open` and fail AC4. R-6 transitions `open → retired` directly (no
`mitigating` intermediate, unlike R-4/R-5).

This is a **conformance/convention-clarification of the existing BRANCH-1
rule** — no new RULE-ID, no methodology-changelog entry, no PMI-1 version
bump (precedent class: slice-029/ADR-027, slice-036/R-9, slice-040/R-10).
`/build-slice` verifies that why-none against the *actual* enforcing META-1
and PMI-1 assertions (not the precedent alone — MEPD-1(b) / slice-032
false-precedent guard).

## Consequences

- The implicit convention that ambushed slice-031 (and was a latent repeat for
  slice-041) is now an explicit, discoverable, regression-pinned rule.
- The next split slice that mistakenly names a folder `slice-NNNx-...` gets a
  loud, actionable message at the `/build-slice` prerequisite gate pointing
  straight at the fix — no spelunking, no R-6 rediscovery.
- BRANCH-1's accept/reject set, JSON shape, and exit codes are unchanged;
  existing `test_branch_workflow_audit.py` tests stay green; the existing
  `test_root_claude_md_branch_per_slice_rule.py` contract is unaffected
  (it asserts only the `Branch-per-slice` substring).
- R-6 transitions open → retired (via the `**Status**:` line flip + `**Retired**:`
  line; verified by `risk_register_audit` reporting `R-6.status == "retired"`).

## Reversibility

**Cheap.** The change is one branched message string + one diagnostic regex
constant + a CLAUDE.md doc sub-clause + a test module. Reverting is a <1-hour
deletion with no data, contract, or accept-set implications. Tagged cheap and
locked now because the slice needs it.
