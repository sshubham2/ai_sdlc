---
id: ADR-044
title: Entry-present methodology-changelog pins drop the `_and_installed` suffix, becoming `_entry_present_in_repo`
date: 2026-05-18
slice: slice-042-realign-entry-present-pin-names-to-decoupled-shape
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-044: Entry-present pins drop `_and_installed` → `_entry_present_in_repo`

## Context

slice-041 (MCFS-1 / ADR-042+ADR-043) decoupled the
`test_v_0_NN_0_<rule>_entry_present_in_repo_and_installed` family so their bodies
assert **in-repo presence only** (the installed-side forward-sync is now enforced
by a separate non-catalog MCFS-1 gate). The function names still carry
`_and_installed` — a shipped name↔body contradiction. slice-041 consciously
deferred the rename (its Deferred / Lessons designate it "the strongest standing
next-slice candidate"). slice-041's reflection is internally inconsistent on the
target: Lessons-L44 says "drop `_and_installed`"; Deferred-L22 says "→ `_entry_present`".
This ADR resolves it.

## Options considered

1. **Drop only `_and_installed` → `..._entry_present_in_repo`** — minimal edit; `_in_repo` remains *accurate* (the body now asserts exactly in-repo presence); preserves the descriptive `entry_present` + scope token; matches slice-041 Lessons-L44 (the forward-looking guidance). Con: slightly longer than option 2.
2. **Drop `_in_repo_and_installed` → `..._entry_present`** — shortest; matches Deferred-L22. Con: drops the now-*true* `_in_repo` scope qualifier, losing the very truth-signal this slice exists to restore; larger diff per name with no semantic gain.
3. **Rename to `..._entry_present_in_repo_only`** — most explicit. Con: needless verbosity; "only" reads as defensive; no precedent for the suffix in the suite.

## Decision

Option 1. Every active over-claiming pin renames by dropping exactly the
`_and_installed` token: `..._entry_present_in_repo_and_installed`
→ `..._entry_present_in_repo`, and the variant
`..._entry_names_<x>_in_repo_and_installed` → `..._entry_names_<x>_in_repo`.
Bodies are unchanged.

**Anchor (regex, authoritative — supersedes any prose count)**: a name is in the
rename set iff it matches
`test_\w*_entry_(?:present|names_\w+)_in_repo_and_installed` in an active
(non-frozen) surface. The anchor is the literal `_in_repo_and_installed` suffix
on the `_entry_present` / `_entry_names_` family. It MUST catch the variant
`test_v_0_36_0_entry_names_three_modes_in_repo_and_installed` (verified-present;
note: **no `_sub_`, no `_<rule>_` segment** — a `_entry_names_*_sub_modes`
anchor would silently miss it and orphan its shippability `::`-selector). It
MUST NOT match the unrelated, still-accurate
`test_in_repo_and_installed_<x>_are_content_equal` CAD-1/mini-CAD drift family
(different lead token — structurally excluded by the `_entry_(present|names_)`
infix). Verified inventory as of 2026-05-18: **37 active defs** = 33
`_entry_present` + 4 `_entry_names` (the slice-041-prose figure "~33" is
superseded). The build-step-1 pre-edit grep is the single source of truth; all
narrative counts reconcile to it.

## Consequences

- 40 function definitions in `tests/methodology/test_methodology_changelog.py` renamed; bodies untouched.
- All live consumers citing these by `::`-selector must track the new name in the same fix block (see ADR-045 for which references are live vs frozen).
- The `_in_repo` token now correctly states the assertion scope — identifier-truth restored (slice-035 class).

## Reversibility

Cheap. The rename is purely lexical with unchanged bodies; a future ADR could
re-rename via the same mechanical map. No data, contract, or behavior depends on
the chosen string. The only non-cheap edge — rewriting append-only shipped
history — is explicitly excluded by ADR-045's carve-out.
