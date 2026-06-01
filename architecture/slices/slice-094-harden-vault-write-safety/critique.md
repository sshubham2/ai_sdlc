# Critique: Slice 094 harden-vault-write-safety

**Critic reviewed**: mission-brief.md, design.md, ADR-086, project-frame.md, milestone.md (+ real code: `tools/_vault_write.py`, `tools/_vault_paths.py`, the 3 named writers, `architecture/risk-register.md` R-32, `architecture/shippability.md`, slice-093 archived design.md)
**Date**: 2026-06-01
**Result**: BLOCKED (Critic-stated; final verdict computed at TRI-1 after dispositions)

## Summary

The design rests on three claims the Critic executed against the real code and found **false**: (1) routing is "transparent / identical bytes" — it is NOT: `safe_write_text`/`safe_append_text` emit CRLF on this repo's interpreter while every existing writer emits LF (`newline=""`), so routing corrupts every vault file's newlines (AC5 + must-not-defer violated); (2) the "3 writers / 3 sites" enumeration is dangerously incomplete — `parallel_conflict_resolver.py` alone has 7 raw write ops and does **not import the VAULT_ROOT seam**, so the primary tripwire cannot detect it (AC1 + AC2 both broken); (3) the risk model is mis-stated — R-32's own register entry says concurrent-process lost-update "becomes live only at the slice-094 flip," but this slice is NOT the flip, and the files being routed are all **git-tracked today**, so routing them through process-locks now adds no safety over the existing `.tmp`+`os.replace` while risking PCR's git-conflict/rebase machinery.

## Findings

### Blockers (must address before /build-slice)

#### B1: "Transparent / identical bytes" (AC5 + must-not-defer) is false — the primitives emit CRLF, the existing writers emit LF
- **Issue**: `tools/_vault_write.py` passes **no `newline=` kwarg** anywhere (`:104` `tmp.write_text(text, encoding=encoding)`; `safe_append_text:150` `os.write(fd, text.encode(encoding))`). The must-not-defer parenthetical "`safe_write_text` keeps `newline=\"\n\"`" is factually wrong. Executed on this repo's venv (utf8_mode=0, os.linesep='\r\n'): `safe_write_text("a\nb\n")` → `b'a\r\nb\r\n'` vs the existing `.tmp.write_text(..., newline="")`+`os.replace` (slice_queue_writer.py:819, slice_queue_claim.py:535, PCR:430) → `b'a\nb\n'`; WHOLE IDENTICAL=False; APPEND IDENTICAL=False. This re-introduces the EOL-DRIFT-1/ADR-033 CRLF class those writers explicitly removed (`newline=""` added for PSQ-2 byte-equal round-trip). "Full suite stays green" (AC5) is unachievable as designed.
- **Evidence**: `tools/_vault_write.py:95-152` (no `newline=`); the three writers' `newline=""` sites with anti-CRLF comments.
- **Proposed fix**: Make the primitive byte-faithful BEFORE any routing — add `newline=""` to `safe_write_text`→`write_text`; confirm/pin `safe_append_text` LF-faithfulness; add a `nt`-guarded byte-identity regression test vs the pre-routing pattern. NB: this changes a slice-093 deliverable's signature → ADR-086 "_vault_write signatures unchanged" must be updated.
- **Builder draft**: ACCEPTED (valid; verified — I asserted `newline="\n"` without checking the code I had read). Fix belongs in the redesign (it changes the `_vault_write` contract + ADR-086).

#### B2: AC1/AC2 enumeration incomplete AND the primary tripwire cannot detect the largest writer — `parallel_conflict_resolver.py` does not import VAULT_ROOT
- **Issue**: AST scan of the real corpus: PCR has **7 raw write ops** to vault paths (`write_text` :430 [writes both slice-queue.md AND shippability.md via `pending_writes`], :1546; `.open("a")` audit appends :713/:764/:1779/:2133/:2234), not 1 — and PCR **imports neither VAULT_ROOT nor `_vault_paths`** (`grep -c → 0`; only imports `_stdout`). So the *primary* (VAULT_ROOT-import) tripwire never fires on PCR; detection collapses to the secondary literal-path tripwire, which ADR-086 itself lists "runtime-computed path" as an accepted residual — and PCR:430's target is composed from `pending_writes` tuples (not a literal at the write site). ADR-086's "isolates EXACTLY the 3 real writers" is contradicted by the code: it isolates the 2 seam-importers and **misses PCR entirely**.
- **Evidence**: AST scan (7 ops); `grep -cE "VAULT_ROOT|_vault_paths" tools/parallel_conflict_resolver.py → 0`; `:50` imports only `_stdout`.
- **Proposed fix**: Redesign the detection. Either (a) a tripwire NOT dependent on the VAULT_ROOT import (resolve write targets under `architecture/`, accepting static-resolution limits), or (b) explicitly scope PCR OUT with a written rationale (slice-093 already classified PCR as git-coupled, "retires at the flip"). Re-run an executed AST scan over the post-routing tree and enumerate every write op + its detection branch.
- **Builder draft**: ACCEPTED (valid; I flagged this gap to the Critic but shipped the design with it unresolved — that was wrong). Redesign required.

#### B3: Contradicts slice-093's own migration map + R-32 model — PCR is git-coupled ("retires at the flip"), and routing git-tracked files through process-locks now adds no safety
- **Issue**: slice-093 design.md classified PCR: "operates on slice-queue.md/shippability.md via git pathspecs… presupposes the vault is git-tracked-in-repo… under untracked+external these go inert → PCR-for-vault retires… `_vault_write` replaces it." R-32's register entry: "becomes live only at the slice-094 flip (vault untracked + shared)… the default stays `architecture/` (no flip), so the vault remains git-tracked and PCR still resolves vault-file conflicts loudly." All three target files are git-tracked today. So under the no-flip default this slice preserves (AC5): (1) concurrent mutation surfaces as a git conflict (PCR territory) — the process-lost-update R-32 guards against is *not live yet*; routing PCR's writes through locks now adds no safety over `.tmp`+`os.replace`+`O_APPEND`, while injecting a cross-process `.lock` held across `git rebase --continue` (PCR :430→:435), unanalyzed new behavior; (2) slice-093 says PCR-for-vault *retires* at the flip — routing it now is contradictory work the flip will undo.
- **Evidence**: slice-093 archived design.md migration map (b); `risk-register.md:567-579` R-32; `git ls-files` (all three tracked); `parallel_conflict_resolver.py:421-447`.
- **Proposed fix**: Reconcile in design.md + ADR-086. The defensible scope for THIS slice is the whole-file class on the seam-importing writers (`slice_queue_writer`, `slice_queue_claim`) + the audit + byte-faithful primitive + concurrency PROOF, reframed as **flip-readiness** (R-32 retires at the flip, not now); scope PCR out per slice-093's map (or analyze the lock-during-rebase interaction explicitly). Narrow AC1's "every vault-writing call site routes through" to a code-grounded, executed enumeration.
- **Builder draft**: ESCALATED — this is a scope/direction decision for the user: re-scope slice-094 to flip-readiness (2 seam writers + audit + primitive byte-fix + concurrency proof; PCR scoped out) and reframe the R-32 claim from "retires now" → "retires at the flip", OR rethink the slice/flip coupling. Needs user ratification before redesign.

### Majors (address this slice / the redesign)

#### M1: Literal-vault-path secondary tripwire has a large false-positive surface — 37 tools name vault files, mostly as READERS
- **Issue**: 37 `tools/*.py` contain those literals, mostly as read targets / error-prose / `git show` pathspecs (PCR alone: 8 `_git_show_stage("architecture/slice-queue.md"/"...shippability.md")` reads + `_SOFT_FILE_SET` literals). "Fires on any raw write whose target literal names a vault file" requires per-write-target AST analysis to avoid false-positiving on reader-with-any-write — the undecidable Option 1 the ADR rejected.
- **Proposed fix**: Specify the AST match precisely (target-of-this-write-op is a `Constant` vault literal vs module-mentions-literal). APED-1 battery MUST include a reader-with-non-vault-write (CLEAN) + error-prose-only module (CLEAN), and be EXECUTED (slice-088 `_RULE_TITLE_RE` precedent).
- **Builder draft**: ACCEPTED (valid). Folds into the B2 detection-model redesign.

#### M2: MEPD-1 INCLUDE is defensible, but reconcile the 5-part vs 4-part PMI-1 bump + count fan-out against real inventory
- **Issue**: INCLUDE itself is correct (non-underscore gate-wired audit + minted RULE-ID). But "5-part PMI-1 atomic bump" is asserted abstractly (the project's PMI-1 surface is VERSION + ~/.claude/ai-sdlc-VERSION + plugin.yaml.version + forward-synced changelog — enumerate against `install_audit.py` `_CANONICAL_*` + INSTALL.md, don't assert "5-part"); the count fan-out cites "cp1252 parametrize list" / "per-tool inventory-pin test" as categories, not concrete `file:line`.
- **Proposed fix**: Replace "5-part" with an executed enumeration of every count literal + install/manifest tuple as concrete `file:line` (N≥3 fan-out lesson demands grep against the real tree).
- **Builder draft**: ACCEPTED-PENDING (resolve in redesign/build via executed grep).

#### M3: Concurrency-test non-vacuity-by-mutation is right, but threads-vs-processes determinism is unspecified
- **Issue**: The "26/30 lines lost" R-32 phenomenon is a *multi-process* effect; `msvcrt.locking` is per-handle + GIL means in-thread "concurrency" may not reproduce the contention → the mutation (disable lock) may still pass on threads → vacuous. AC3 doesn't specify threads vs processes. Cross-process file-lock tests are flaky/can hang under pytest.
- **Proposed fix**: Specify `multiprocessing` (spawn) workers (or justify threads); state worker count + mutation point + a bounded timeout so a lock-hang fails loud.
- **Builder draft**: ACCEPTED-PENDING (specify process model + timeout in the redesigned design.md / build).

#### M4: ADR-086 "_vault_write signatures unchanged" contradicts B1's fix; `.gitignore` `.tmp` glob matches nothing as written
- **Issue**: (a) B1's `newline=` addition makes "signatures unchanged" false → ADR-086 must be updated. (b) `.tmp` files are `<filename>.<pid>.tmp` (`_vault_write.py:103`), so `*.<pid>.tmp` as written matches nothing — use `*.tmp` or `*.*.tmp`; verify `*.lock` doesn't shadow a tracked `.lock`.
- **Proposed fix**: Real globs (`*.lock`, `*.tmp`); update ADR-086 Contracts to reflect the `newline=` change.
- **Builder draft**: ACCEPTED (valid). Folds into B1 + the `.gitignore` work.

### Minors (log; address if cheap)

#### m1: Design/milestone line numbers are stale — cited sites point at comments/docstrings
- **Issue**: `slice_queue_writer.py:107` is the parallel-safety-enum comment (real write :818-820); `slice_queue_claim.py:232` is a docstring (real write helper :527-536); `parallel_conflict_resolver.py:303` is a docstring (no write). Conceded in the design's NOTE-TO-CRITIC.
- **Builder draft**: ACCEPTED — re-derive all line numbers in the redesign (the milestone repeats the wrong numbers).

#### m2: `safe_append_text` has zero production callers today — this is its first production use
- **Issue**: Only `_vault_write.py` references the primitives; the "transparent" claim has no prior production validation → B1's byte-identity test is mandatory first-use validation, not a regression check.
- **Builder draft**: ACCEPTED (noted; reinforces B1).

#### m3: shippability is at 101 numbered rows, not "~99/100"; cited test path doesn't exist yet
- **Issue**: Catalog has 100 data rows, last id 101 (slice-093). New VWS-1 row goes at the correct next index; the wiring-matrix-cited `test_vault_write_safety_audit.py::test_audit_flags_planted_raw_vault_write` is a slice deliverable (fine as PENDING, but the slice plan must author it — PTFCD-1).
- **Builder draft**: ACCEPTED-PENDING (correct row index + author the cited test in the slice plan).

## Dimensions checked
- [x] Unfounded assumptions — B1 (false "keeps newline='\n'"), B3 (assumes process-lost-update live now), M2 (5-part PMI-1 abstract).
- [x] Missing edge cases — M3 (threads-vs-processes; lock-hang timeout), B3 (lock held across `git rebase --continue`), M4 (`.tmp` glob).
- [x] Over-engineering — B3 partial (routing PCR which retires at the flip; process-locks before the hazard is live — YAGNI).
- [x] Under-engineering — B2 (audit can't see the largest writer; AC1 unmet), M1 (FP surface unspecified).
- [x] Contract gaps — M4 (ADR-086 "signatures unchanged" vs B1 fix). Audit exit-code-only otherwise.
- [x] Security — none: cooperative data-integrity control, not a security boundary (ADR-067/086). Correctly N/A.
- [x] Drift from vault — B3 (contradicts slice-093 migration map (b) + R-32 "live only at flip"), m3 (row count), M2 (PMI-1/INST-1 reconcile).
- [x] Web-known issues — confirmed: `os.replace` atomic but no lost-update protection without a lock; `msvcrt.locking` byte-range mandatory; `write_text(newline=)` defaults to `os.linesep` translation (B1 root cause); cross-process lock tests flaky/hang under pytest (M3).
- [x] Cross-cutting conformance — B1 (tooling-impl-vs-prose parity), B2 (APED-1: matcher misses PCR), M1 (APED-1 battery must execute), M2/m3 (mechanical-table-vs-inventory), RSAD-1 (this slice's own design mechanical table is wrong — the class VWS-1 exists to catch).

## Triage

**Triaged by**: (pending — TRI-1, user-owned; runs after /critique-review)
**Date**: (pending)
**Final verdict**: (pending — B3 Builder-drafted ESCALATED ⇒ heading to BLOCKED → /design-slice redesign)
