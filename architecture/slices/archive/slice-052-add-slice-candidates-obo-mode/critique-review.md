# Critique Review: Slice 052 add-slice-candidates-obo-mode

**Reviewed by**: critique-review agent (DR-1)
**Date**: 2026-05-20
**First-Critic verdict**: NEEDS-FIXES
**Dual-review verdict**: EXTEND

## Summary

The first Critic's review is substantively strong: B1, B2, M3, M4 are the right
Blockers/Majors, code-confirmed, and the B2 redefinition of parity to
backlog.md/parse_html_state equality is correct against `assemble.py` L1712.
However the post-fix design leaves two real concerns the first Critic did not
surface — a Deferred-resume irreversibility under-specification, and an
unspecified `--obo-write` substitution mechanic that risks reintroducing the
B1/B2 byte-fragility class one layer down — plus one severity observation on m1.

## Confirmed findings

B1 (ensure_ascii) Blocker, B2 (whole-doc outerHTML parity) Blocker, M1
(collect/key-order) Major, M2 (resume predicate) Major, M3 (test-first:false
for deterministic helpers) Major, M4 (mechanical scoped-peek) Major, m2 (temp
cleanup) Minor, m3 (OSDG-1 nomination physically recorded) Minor — ALL
code-confirmed against `build_backlog.py` L42-117 / `assemble.py` L1635-2176,
severities appropriate, fixes faithful. The escape token `<\/` (single
backslash) in design step 4 matches both L1709 and L2118 — code-correct.

## Suspicious findings

None. Every first-Critic finding is code-confirmed; none is over-reach. The
Builder's B1 note ("once B2 redefines the contract, B1 practical impact narrows
because `json.loads` decodes both forms identically") is accurate but does not
make B1 suspicious — the narrowing is conditional, see M-add-2.

## Missed findings

### M-add-1 (Major, medium-confidence): Deferred-on-resume is irreversible with no documented reopen path
AC5 makes Defer terminal for `--obo` resume (Deferred entries are in
`annotations`, resume predicate is `id ∉ annotations`, so they are permanently
skipped). `confirmed_findings` L96 correctly excludes `defer` from the backlog
— that half is fine. The gap: design.md never documents the escape hatch, so a
one-way Defer with no reopen path is an under-specified state-machine edge
(Wiegers: no-silent-trap completeness). Fix = one documentation sentence
(reopen path) in design.md + SKILL.md operator guidance — likely an intentional
product decision, so the finding is the under-specification, not the behavior.

### M-add-2 (Major, high-confidence): `--obo-write` step 5 substitution mechanic unspecified — risks reintroducing the B1/B2 silent-divergence class
Design step 5 said "substitute only the script-block inner text" without
stating *how*. The original block is emitted at `assemble.py` L2176. If
`--obo-write` uses `re.sub`/`re.Match.expand` with the JSON payload as the
*replacement* string, Python's special handling of `\g<…>`, `\1`, and bare
backslashes will corrupt a payload that legitimately contains `<\/` and
arbitrary `\uXXXX`/backslash sequences from finding text — the same
silent-byte-divergence failure class as B1/B2, one hop down, inside the
must-not-defer serialization-parity item. The first Critic verified the
`json.dumps`+`.replace` half (B1) but not the *insertion* half — a
dimension-local blind spot (checked "serialization correctness", not "in-place
substitution correctness"). Fix: step 5 must specify match-span string slicing
(`text[:m.start(1)] + new_inner + text[m.end(1):]`), NOT `re.sub`; the golden
test must include a finding whose notes contain a literal backslash + a `</`.

## Severity adjustments

### m1 → recommend Major (filed Minor)
`parse_html_state` L47-51 (`re.search` + non-greedy `(.*?)` + `re.DOTALL`)
silently binds the FIRST `diagnose-data` block. A duplicate block is exactly
what an imperfect step-5 substitution (M-add-2) or a partial/aborted write can
produce — a stale block + an appended new one — and `parse_html_state` would
then silently consume the STALE one, yielding a `backlog.md` that looks valid
but encodes pre-decision state. That is silent-correctness corruption on the
primary consumer path (Wiegers verifiability + Sommerville fail-stop), not a
cosmetic robustness gap. The first Critic correctly identified the gap and the
NEW `re.findall` fix; only the severity is under-weighted.

## Notes

High confidence on the confirmed set and m1-severity (direct code reads).
M-add-1 medium-confidence (may be acceptable product decision → one-sentence
doc fix). M-add-2 is the highest-confidence genuine miss. Calibration: the
first Critic showed strong APED-1 rigor (B1+B2 empirically executed) with a
slight tendency to stop at the verified boundary rather than tracing the
payload one hop further into where it is written and re-read. The 2B/4M/3m
distribution is well-calibrated; EXTEND is driven by M-add-2.
