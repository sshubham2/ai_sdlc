# Critique: Slice 114 convert-agent-prose-to-vault-seam

**Critic reviewed**: mission-brief.md, design.md, project-frame.md (no new ADRs — rides ADR-105)
**Date**: 2026-06-05
**Result**: NEEDS-FIXES

## Summary
The conversion arithmetic is sound (APED-1-executed: 127/4/131 confirmed against the live corpus), the value-collision-safety claim holds, and the carve-out taxonomy is correctly applied. The defects are in completeness, not direction: (1) `agents/critic-calibrate.md` is forward-synced but has **no drift guard test**, so AC4 leaves the conversion runtime-unprotected and silently regressible; (2) the per-file disposition mislabels `code-review.md:25` as "class 1-pathspec" when the live classifier reports `operational-reference`; (3) several consumer-count sites and floor interactions need explicit enumeration. None require redesign.

## Findings

### Blockers (must address before /build-slice)

None. The slice rides ADR-105 correctly, the carve-out classifications are defensible, and the conversion is flip-neutral.

### Majors (address this slice)

#### M1: AC4 forward-syncs `agents/critic-calibrate.md` but there is NO drift test guarding it — the conversion is runtime-unprotected and silently regressible
- **Claim under review**: AC4 / design.md: "Forward-sync code-review.md + critic-calibrate.md … (keeps test_code_review_agent_drift.py green; runtime-correctness for critic-calibrate)." Error model: "forgotten forward-sync → test_code_review_agent_drift red."
- **Issue**: Only TWO agent drift tests exist on disk — `test_code_review_agent_drift.py` and `test_critique_agent_drift.py`. There is **no `test_critic_calibrate_agent_drift.py`**. So for critic-calibrate.md the forward-sync is unguarded: a future in-repo edit that forgets the `~/.claude/agents/` sync reds NO test. Once critic-calibrate.md carries a `<vault>/` ref + the embedded note, the installed runtime prompt MUST stay in sync (a subagent doesn't inherit CLAUDE.md), or the meta-Critic resolves a stale/note-less prompt. `test_critic_calibrate_agent.py` pins only META-2 prose substrings, not content-equality.
- **Evidence**: `ls tests/methodology/*agent_drift*` → only code_review + critique. `tests/methodology/test_critic_calibrate_agent.py:1-36`. slice-113 reflection M-add-1 (on-disk test set is the authority).
- **Proposed fix**: (a) add `tests/methodology/test_critic_calibrate_agent_drift.py` (mirror code-review's, swap the path) + shippability row + TF-1 row — bring critic-calibrate under the CAD-1/CRSI-1 family; OR (b) state explicitly the forward-sync is deliberately unguarded + correct the error-model line. Critic recommends (a).
- **Builder draft**: ACCEPTED-PENDING — adopt option (a). At `/build-slice`: add `tests/methodology/test_critic_calibrate_agent_drift.py` (verbatim mirror of `test_code_review_agent_drift.py`, path swapped), forward-sync critic-calibrate.md, add a shippability row + a TF-1 plan row. Bringing a member into the already-open-ended CRSI-1/CAD-1 family is "the rule operating within its documented scope" → stays MEPD-1 EXCLUDE (no new RULE-ID/VERSION bump), per the OSDG-1 family-extension precedent. I will ALSO correct the design.md error-model + AC4 prose now (removing the false symmetry) so nothing ships stale to build.

#### M2: `code-review.md:25` (`architecture/**`) is labeled "CARVE-OUT class 1-pathspec" but the live classifier reports `operational-reference` — the carve-out decision is right, its stated evidence is wrong
- **Claim under review**: design.md per-file disposition: "code-review.md:25 `architecture/**` → CARVE-OUT class 1-pathspec (git-pathspec PROSE mirror …)."
- **Issue**: Live `vault_flip_prose_inventory --json` classifies `agents/code-review.md:25` as `klass=rewrite-at-flip reason=operational-reference`, NOT git-pathspec. `_PATHSPEC_RE` requires `:(exclude|glob|…)` syntax, which line 25 (descriptive prose `out-of-scope: architecture/**, docs/**`) does not contain. The carve-out *decision* is correct (the agent prose mirrors the concrete `:(exclude)architecture/...` pathspecs in `skills/code-review/SKILL.md`, so converting it would diverge them), but the "class 1-pathspec" *label* is verifiably false against the tool the slice relies on (slice-113 reflection Discovered #2: pathspec detection is line-local, not block-aware).
- **Evidence**: `--json` → code-review.md:25 reason=operational-reference. `tools/vault_flip_prose_inventory.py:130` (`_PATHSPEC_RE`). `skills/code-review/SKILL.md:47-85` (concrete pathspecs). slice-113 reflection.md:14,19.
- **Proposed fix**: Relabel: "CARVE-OUT (prose mirror of the SKILL.md `:(exclude)architecture/...` diff-scope pathspecs; classifies `operational-reference`, NOT git-pathspec — `_PATHSPEC_RE` is line-local and does not fire on the prose description; stays concrete so the agent prose matches the concrete pathspecs per the slice-113 /code-review B1 lesson)." (CCC-1 tooling-doc-vs-implementation parity.)
- **Builder draft**: ACCEPTED-FIXED at design.md per-file disposition table (relabel applied this round; carve-out decision unchanged).

#### M3: The two carve-out literals in `code-review.md` (:25 and :233) stay `rewrite-at-flip` while the file enters `_CONVERTED_FILES` — design must pre-state both as required `_CONVERTED_CARVEOUTS` hash entries or `--strict` exits 2
- **Claim under review**: design.md: "_CONVERTED_FILES += the 2 agents; _CONVERTED_CARVEOUTS += the 2 code-review.md operational carve-outs (hash-keyed)."
- **Issue**: Correct in intent, but the failure mode is a hard exit-2. Once `agents/code-review.md` enters `_CONVERTED_FILES`, `converted_file_regressions()` flags EVERY non-carve-out `rewrite-at-flip` in it; after conversion code-review.md retains TWO (:25, :233). Both must be hash-added or `--strict` reds. The design should pre-state the exact 2 `_carveout_key` entries (or that they are APED-1-derived at build) so the build doesn't under-add.
- **Evidence**: `tools/vault_flip_prose_inventory.py:460-471` (`converted_file_regressions`), `:356-381` (`_CONVERTED_FILES`), `:396-453` (`_CONVERTED_CARVEOUTS`).
- **Proposed fix**: State explicitly that adding code-review.md to `_CONVERTED_FILES` REQUIRES `_carveout_key('agents/code-review.md','architecture/**')` AND `_carveout_key('agents/code-review.md','architecture/slices/slice-NNN-<name>/code-review.md')` in `_CONVERTED_CARVEOUTS` (APED-1-derived; omission → exit 2). critic-calibrate.md needs none.
- **Builder draft**: ACCEPTED-FIXED at design.md "Ratchet safety" + Enforcement re-pin (explicit two-hash requirement added this round; confirmed at mid-slice smoke gate per AP-3).

### Minors (log; address if cheap)

#### m1: `_CLASS_COUNT_FLOOR[DOC_EXAMPLE]` stays 0 while doc-example goes 2→4 — note the drift direction is covered by baseline+ratchet, not the floor
- **Issue**: Leaving the floor at 0 matches slice-112/113 precedent. The definitional-line drift direction (backtick/op-verb added → demoted to rewrite-at-flip) fails closed via `_BASELINE_SHA256` drift + the ratchet, NOT the floor. Worth a note so the build doesn't "fix" the floor to 4 and red a legitimate future skill conversion that lowers doc-example.
- **Evidence**: `tools/vault_flip_prose_inventory.py:307-312`; ADR-105 line 47.
- **Builder draft**: ACCEPTED-FIXED — one-line note added to design.md Enforcement re-pin.

#### m2: the "rows 113/117" reference is STALE — live-count sites are `vault_flip_prose_inventory.py` (8 sites) + `shippability.md` rows 122/126/127/128
- **Issue**: AP-10 grep shows the LIVE-value 132/130 consumers are `tools/vault_flip_prose_inventory.py:{21,47,48,51,306,308,332,334}` + `architecture/shippability.md` rows 122 (slice-107: "all 132", "130/0/2/0") and the regression-sentinel clauses on rows 126/127/128. The design's "rows 113/117" is slice-112/113-era numbering and is now stale; the build must repoint by CURRENT row IDs. Archive/historical-provenance ("→132 after slice-113") stays as anchors.
- **Evidence**: AP-10 grep; `shippability.md:122,126,127,128`.
- **Builder draft**: ACCEPTED-FIXED — design.md Enforcement re-pin updated to the verified current site list (per-row update-vs-anchor judgment noted); replaces the stale "rows 113/117".

#### m3: mission-brief verification row 3 hardcodes "127/4/131" while design says derive — minor wording tension (numbers are correct)
- **Issue**: APED-1 confirms 127/4/131; `_BASELINE_SHA256` genuinely cannot be pre-computed. Ensure row 3's numbers read as verification of a derived result, not a hand-pinned estimate.
- **Builder draft**: ACCEPTED-FIXED — mission-brief row 3 annotated ("derived expected counts, APED-1-confirmed; _BASELINE_SHA256 derived at build, never estimated").

## Dimensions checked
- [x] **Unfounded assumptions** — M2 (mislabel verified by executing the tool). The "no exploitable value-collision" ratchet-safety claim was **verified sound** (2 carve-out values distinct from each other and from the converted refs).
- [x] **Missing edge cases** — m1 (doc-example floor drift covered by baseline+ratchet). CRLF: build should normalize edited agents to LF before the drift test (slice-113 Discovered #1), backstopped by the EOL-agnostic comparator — build-time concern, not a design defect.
- [x] **Over-engineering** — none. Reuses ADR-105 verbatim; correctly leaves critique-review.md + diagnose-narrator.md note-less (no speculative resolver note on zero-convertible files). MEPD-1 EXCLUDE is right.
- [x] **Under-engineering** — M1 (AC4 with no enforcement element for critic-calibrate), M3 (ratchet-safety AC under-specifies the 2 required hash adds).
- [x] **Contract gaps** — none new (read-only Critic/narrator subagents; the only contract is the --strict/baseline/drift-test enforcement, covered modulo M1).
- [x] **Security** — none. No auth/secrets/injection. code-review.md:119 `.secrets-allowlist` is correctly converted (vault-content read), not a secret.
- [x] **Drift from vault** — none blocking. Honors ADR-105 classes 5 (R-32.a) + 7 (no <diagnose-out> seam) by refusing to convert :78/:19. Strategic-direction fit: this slice IS the project's next pending direction (flip-vault-to-external-store prerequisite). AC5 R-32 update consistent with risk-register.md:604.
- [x] **Web-known issues** — none; no external technology in scope (in-repo methodology prose + audit constants).
- [x] **Cross-cutting conformance** — M2 (CCC-1 doc-vs-implementation parity), M3 (algorithm-path conformance with converted_file_regressions), m2 (FBCD-1(c) count-literal fan-out). APED-1 self-applied (tool executed against live corpus). RSAD-1 (slice edits the Critic agents themselves; seam-note plan checked against ADR-105 M-add-1).

## Triage

**Triaged by**: user
**Date**: 2026-06-05
**Final verdict**: NEEDS-FIXES

Reconciles BOTH passes: 6 first-Critic findings (M1/M2/M3/m1/m2/m3) + 1 meta-Critic missed finding (m-add-1, from `critique-review.md`). Dual-review verdict EXTEND (zero suspicious, zero severity adjustments — all first-Critic findings VALID at correct severity).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| M1 | Major | ACCEPTED-PENDING | Option (a): at `/build-slice` add `tests/methodology/test_critic_calibrate_agent_drift.py` (mirror of code-review's) + shippability row + TF-1 row + forward-sync; author with FAIL→PASS non-vacuity proof (AP-5). Design error-model/AC4 prose corrected this round. |
| M2 | Major | ACCEPTED-FIXED | design.md per-file disposition row relabeled — `code-review.md:25` is `operational-reference`/prose-mirror, NOT git-pathspec (`_PATHSPEC_RE` line-local); carve-out decision unchanged. |
| M3 | Major | ACCEPTED-FIXED | design.md "Ratchet safety" now pre-states BOTH required `_carveout_key` entries (`architecture/**`, `architecture/slices/slice-NNN-<name>/code-review.md`); APED-1-derived; `--strict` exit-0 confirmed at mid-slice smoke. |
| m1 | Minor | ACCEPTED-FIXED | design.md "don't raise DOC_EXAMPLE floor to 4" note added — drift direction fails closed via `_BASELINE_SHA256` + ratchet, not the floor. |
| m2 | Minor | ACCEPTED-FIXED | design.md verified current LIVE-count site list (`vault_flip_prose_inventory.py` 8 sites + `shippability.md` rows 122/126/127/128) replaces the stale "rows 113/117". |
| m3 | Minor | ACCEPTED-FIXED | mission-brief verification row 3 annotated — 127/4/131 are derived/APED-1-confirmed; `_BASELINE_SHA256` derived at build, never estimated. |
| m-add-1 | Minor | ACCEPTED-FIXED | design.md §Decisions + mission-brief §Out-of-scope record the root CLAUDE.md CAD-1 enumeration as a deliberate courtesy-parity deferral (slice-096 precedent); the drift tests are the authoritative guarded-set. |
