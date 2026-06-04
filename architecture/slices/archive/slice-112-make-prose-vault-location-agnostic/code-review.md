# Code Review: Slice 112 make-prose-vault-location-agnostic

**code-Critic reviewed**: slice diff vs default branch (merge-base `61483af`; uncommitted worktree)
**Date**: 2026-06-04
**Result**: FINDINGS (0 blockers / 1 major / 2 minors)

## Builder disposition (post-review, advisory v1)
- **M1 → ACCEPTED-FIXED**: updated the tool module docstring (`tools/vault_flip_prose_inventory.py:21,47-52`) to the live 301/303/2-doc-example numbers + slice-112 transition (build-log 2026-06-04). The docstring is now consistent with the re-pinned constants — the FBCD-1(c) fan-out is complete (it had omitted the in-module docstring).
- **m1 → ACCEPTED-FIXED (claim scoped)**: scoped the "durable against rewording" claim in ADR-105 §Carve-out exemption — durable against *value* rewording; the plain-prose definitional stays sensitive to op-verb/backtick *formatting* on its line, which fails CLOSED (the AC3 ratchet test `test_pilot_files_zero_rewrite_at_flip_after_conversion` reds — already the guard). No extra test needed (existing AC3 test covers it).
- **m2 → DEFERRED (accepted residual pattern)**: the bare `graphify vault architecture` arg at `CLAUDE.md:70` stays concrete — the slice-107/111 `_RESIDUAL` bare-no-slash pattern (enumerated, never silent). Noted for the skill-conversion follow-on (handle bare-args via the tool's internal `VAULT_ROOT` default, or pin `_RESIDUAL` line-numbers to live content).

## Summary

The core mechanism is sound and the adversarial probes the brief flagged all came back clean (verified by executing the tool against the worktree corpus, not by reading prose): the hash-keyed `_CONVERTED_CARVEOUTS` exempts exactly the 4 intended carve-outs and is path-scoped + fail-closed across files; `converted_file_regressions` is genuinely independent of `_BASELINE_SHA256` (mutation-proven non-vacuous); the converted pilot files carry only the 4 sanctioned carve-outs + 2 plain-prose definitionals (zero un-exempted `rewrite-at-flip`, zero `needs-human`); the re-pinned constants (301/303/baseline SHA) match the live corpus exactly; CAD-1 forward-sync genuinely landed; AC5 readiness disjointness preserved; full methodology suite green. One real defect (M1: stale module docstring counts) + two minors (overstated durability/conversion-completeness claims). M1 + m1 addressed post-review.

## Changed files (in-scope)
- tools/vault_flip_prose_inventory.py
- tests/methodology/test_prose_vault_seam_convention.py (NEW)
- tests/methodology/test_vault_flip_prose_inventory.py
- CLAUDE.md
- agents/critique.md
- architecture/slices/slice-112-make-prose-vault-location-agnostic/build-log.md

(Diff also touches `architecture/shippability.md` rows 113/117/118, `architecture/drift-log.md` marker, `architecture/slice-queue.md` R-33 sync — out of the declared in-scope code list but verified benign: shippability is the required FBCD-1(c) fan-out, drift-log is the DCE-1 marker, slice-queue is the documented R-33 master-sync.)

## Findings

### Blockers (advisory in v1)

None. No broken code path, no unsafe construct, no contradiction with an ACCEPTED ADR. The ratchet fails closed, the carve-outs are correctly scoped, and the re-pin is internally consistent.

### Majors

#### M1: The tool's module docstring carried stale narrative counts (313 / "0 doc-example" / "all empty") contradicting the re-pinned constants — FBCD-1(c) fan-out incomplete; recurrence of slice-111 m5  — **FIXED**
- **Claim under review**: `tools/vault_flip_prose_inventory.py:21` "the LIVE total is … 313 after slice-111"; `:47` "**313 rewrite-at-flip / 0 historical-anchor / 0 doc-example / 0 needs-human**"; `:50` "all 313 are rewrite-at-flip"; `:51-52` "doc-example, historical-anchor, and needs-human are all empty".
- **Issue**: now FALSE — the slice re-pinned `EXPECTED_TOTAL = 303`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP] = 301`, live distribution **301/0/2/0** (2 doc-example = the new definitionals CLAUDE.md:49 + agents/critique.md:11). Per FBCD-1 sub-mode (c) the cardinality change must fan out to every hard-count literal; the re-pin set omitted the in-module docstring (a hard-count literal). Recurrence of slice-111 m5 (stale sub-count in this docstring family).
- **Evidence**: `tools/vault_flip_prose_inventory.py:21,47,50,51`; live `class_counts()=={'rewrite-at-flip':301,'historical-anchor':0,'doc-example':2,'needs-human':0}`, `EXPECTED_TOTAL==303`. No test pins the docstring narrative → silent rot (the constants below are test-pinned + correct).
- **Proposed fix**: update the docstring to live numbers + slice-112 note. **Applied** (the docstring now reads 301/0/2/0 / 303 with the slice-112 transition).

### Minors

#### m1: The "durable against rewording" claim for the plain-prose definitional (M-add-2) is overstated — durable against *value* rewording, fragile to *formatting/op-verb* rewording  — **claim scoped**
- **Issue**: the plain-prose exemption holds only while the definitional line stays free of `_OP_VERB_RE`/`_ANCHOR_RE` + outside backticks. `_OP_VERBS` includes common words ("see", "note", "read", "located", "defines"); a future reword could flip the line to `rewrite-at-flip` → ratchet exit-2 on a genuine doc example. **Fails CLOSED** (safe), but surprising; the "durable" framing oversold.
- **Evidence**: `_OP_VERBS:101-111`; `_classify_match:214`; both definitional lines pass today only by avoiding every op-verb.
- **Proposed fix**: scope the claim (no code change — fail-closed + already caught by the AC3 ratchet test). **Applied** in ADR-105 §Carve-out exemption.

#### m2: "CLAUDE.md fully converted" is slightly overstated — the bare `graphify vault architecture` arg at `:70` remains concrete, invisible to the ratchet  — **deferred (accepted residual)**
- **Issue**: CLAUDE.md still carries the bare no-slash `architecture` dir-arg at `:70` (tracked in `_RESIDUAL`, invisible to `_MATCH_RE` → never in `converted_file_regressions`). Matches the accepted slice-107/111 bare-arg residual pattern (enumerated, never silent); the line-number-keyed `_RESIDUAL` is itself fragile.
- **Proposed fix**: no action this slice; for the follow-on — flip-handle bare-args via the tool's internal `VAULT_ROOT` default, or pin `_RESIDUAL` `(path, line)` to live content.

## Dimensions checked
- [x] Unfounded assumptions — M1 (docstring counts vs constants). Otherwise none (no phantom import; agent note claims match `_vault_paths`).
- [x] Missing edge cases — none in code paths (empty/single-file, backslash member, value-capture greediness, wrong-file carve-out all probed fail-closed). m1 = the one foreseeable edge (reword the definitional) — fail-closed.
- [x] Over-engineering — none (`_carveout_key` 1-line, 2 callers; `_CONVERTED_CARVEOUTS` exactly 4 live members; hash-keying justified by AC5 disjointness).
- [x] Under-engineering — none (every AC → passing non-vacuous test; M3 independence mutation-proven; CAD-1 forward-sync landed; full suite + readiness + CAD-1 + TF-1 exit 0).
- [x] Contract gaps — none (`converted_file_regressions`/`_carveout_key` type-annotated + docstring'd; exit-code 0/1/2 extended correctly; JSON payload gains `converted_file_regressions`).
- [x] Security — none (no auth/network/input surface; SHA-256 is content-addressing not a security control; no shell/injection).
- [x] Drift from vault — M1 (code-vs-self, fixed). Otherwise none (hash-keyed deviation documented in design.md + ADR-105 AS-BUILT + build-log; no scope creep — skills + op-gate floors untouched, 6/11/23/0 verified; shippability fan-out complete).
- [x] Web-known issues — none applicable (no external API/SDK in the diff; only `hashlib`/`re` stdlib).
- [x] Cross-cutting conformance — M1's FBCD-1(c) framing (fixed). RSAD-1: converted files pass the new ratchet (exit 0). APED-1: convention prose executed against the real classifier (0 needs-human / 2 doc-example confirmed). Forward-slash `_CONVERTED_FILES` matches `Occurrence.path` normalization (negative-tested).
