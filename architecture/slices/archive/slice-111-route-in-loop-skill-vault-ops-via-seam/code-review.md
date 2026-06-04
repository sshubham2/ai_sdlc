# Code Review: Slice 111 route-in-loop-skill-vault-ops-via-seam

**code-Critic reviewed**: slice diff vs default branch `571c8da` (filtered to in-scope paths), in the worktree
**code-Critic**: separate `code-review` agent (read-only, adversarial; AP-4 class — new/extended classifier)
**Date**: 2026-06-04
**Result**: FINDINGS (no blockers; 2 majors; 5 minors) — advisory in v1

## Summary

Headline invariants verified under live execution: M1 re-pin byte-correct (313 literals, baseline SHA matches, EXPECTED_TOTAL + count-floor consistent), op-gate genuinely green on the real corpus (6 routed / 11 deferred / 23 out-of-scope / 0 unrouted), B2 dual-literal non-vacuity bites, `vault_edit move` M2 final-landing-path guard correct, full methodology suite green, m-add-5 hand-sync in-sync. No blockers. All findings are in the AP-4 classifier-soundness class: 2 latent false-negative paths in the op-gate detector (not exploited on the corpus today, but each is a way a future un-routed in-loop write could slip past silently).

## Changed files (in-scope)
tools/vault_edit.py · tools/vault_flip_prose_inventory.py · tests/methodology/test_vault_edit_cli.py · tests/methodology/test_vault_flip_op_gate.py · tests/methodology/test_vault_flip_prose_inventory.py · skills/reflect/SKILL.md · skills/archive/SKILL.md · skills/drift-check/SKILL.md · architecture/slices/slice-111-.../build-log.md

## Findings

### Blockers (advisory in v1)
None.

### Majors

#### M1: Rule-1 (seam token anywhere on the line) masks a genuinely un-routed write — the AP-15 decoy-marker failure ADR-104 warns against
- **Claim under review**: `tools/vault_flip_prose_inventory.py` `_classify_op` — `if _SEAM_TOKEN_RE.search(line): return (OP_ROUTED, "seam-token")` is line-wide.
- **Issue**: ANY `vault_edit`/`VAULT_ROOT` mention (comment, negation "do NOT run raw, use `vault_edit`", noun) buys OP_ROUTED for a raw write on the same line → suppresses a real OP_UNROUTED. Not exploited on the corpus today (all 6 routed lines genuinely route), but a structural escape hatch.
- **Evidence**: `Instead of \`vault_edit\`, do NOT run raw: mv \`architecture/slices/s-1\` \`architecture/lessons-learned.md\`` → op-routed (should be OP_UNROUTED).
- **Proposed fix**: scope the routed signal to AFTER `first_verb` (already computed in `scan_op_file`), or to the sink's code span; add an adversarial decoy test.
- **Builder draft**: **ACCEPTED-FIXED** — `routed` computed in `scan_op_file` as `_SEAM_TOKEN_RE.search(line, first_verb)` (seam must follow the governing verb) + decoy tests. Behavior-preserving on the corpus (6 routed unchanged).

#### M2: `is_move` single-dest collapse drops earlier write targets when a move/copy verb co-occurs with another write verb
- **Claim under review**: `is_move = _MOVE_VERB_RE.search(line) and not has_git_add` / `targets = [lits[-1]] if is_move else lits`.
- **Issue**: "a move/copy verb ⟹ only the last literal is a target" is unsound on a multi-verb line. `copy \`X\` then create \`Y\`` → drops the `copy X` write (false-negative). Inverse `mv … then git add …` → `has_git_add` forces is_move=False → the mv SOURCE is falsely counted.
- **Evidence**: executed both cases; no multi-op lines on the corpus today.
- **Proposed fix**: only collapse to last-literal when the line is a SINGLE clean move/copy (exactly one write verb, a move-verb); else treat all literals as targets (fail-safe: over-flag, never under-flag) + a guard test.
- **Builder draft**: **ACCEPTED-FIXED** — `is_move` gated on `single-clean-move` (one write verb total, a move-verb, no git-add); multi-verb → all literals targets. Behavior-preserving on the corpus + adversarial tests.

### Minors

#### m1: op-gate only flags a sink literal that is itself in-code — a bare path (verb/flag backticked, path outside) escapes
- **Builder draft**: **ACCEPTED-FIXED (doc)** — documented the intentional in-code-sink trade-off in the `scan_op_file` docstring.

#### m2: `vault_edit move` error messages hardcode `--file` even for `--from`/`--to`
- **Builder draft**: **ACCEPTED-FIXED** — `_resolve_in_vault(file_arg, *, arg_name="--file")` interpolates the arg name; `move` passes `--from`/`--to`.

#### m3: `move --from X --to X` returns exit 0 as a silent no-op
- **Builder draft**: **ACCEPTED-FIXED** — explicit same-path guard → exit 2 with an actionable message.

#### m4: hash-keyed allowlist re-surfaces a KNOWN lexical false-positive as blocking OP_UNROUTED on any line edit
- **Builder draft**: **ACCEPTED (doc, v1)** — accepted for v1: the re-surface-on-edit is fail-safe (forces re-verify); the genuine-deferred entries legitimately stay allowlisted. Documented the brittleness in the `_OP_ALLOWLIST` comment. (Detector-narrowing for verb-as-noun cases is a future refinement.)

#### m5: shippability row 117 out of numeric order + `69/313` stale-provenance sub-count in row 113
- **Builder draft**: **ACCEPTED-FIXED** — row 117 moved after 116; row 113's `69/313` restored to `69 of slice-107's 318` (provenance preserved, mirroring the module docstring caveat).

## Dimensions checked
- [x] Unfounded assumptions — M2 (is_move mixed-verb), m5 (69/313 provenance). Verified: 313/SHA/EXPECTED_TOTAL match live; 0 OP_UNROUTED true; no phantom imports.
- [x] Missing edge cases — M1, M2, m1, m3. Verified handled: `--to` existing-file → exit 2; dst-child-of-src → caught exit 2; vault-root/empty → exit 2; missing source → exit 2 (R-32.b loud).
- [x] Over-engineering — none (minimal subcommand + additive mode; CSP-1-compliant).
- [x] Under-engineering — none material (every AC has a code element; m-add-5 hand-sync verified).
- [x] Contract gaps — m2 (error-msg arg name). Exit contracts documented + match.
- [x] Security — none (paths confined under VAULT_ROOT; no shell=True/eval/injection/secrets).
- [x] Drift from vault — none (code matches design.md/ADR-103/ADR-104; build-slice/validate-slice NOT edited per the deviation; MEPD-1 EXCLUDE honored; `git ls-files architecture` unchanged).
- [x] Web-known issues — `shutil.move` 3.13 semantics confirmed; cross-store (R-32.b) + symlink-cross-device deferred to flip slice (not slice-111 defects).
- [x] Cross-cutting conformance — RSAD-1 (own op-gate green on own edits); APED-1 (parse-rules executed adversarially — M1/M2/m1 are the gaps now being closed); EOL-DRIFT-1 (no new .md byte-compare); cp1252-safe (no print()); test non-vacuity confirmed (gate CAN emit OP_UNROUTED).
