# Code Review: Slice 076 add-pcr-1-conflict-diagnostic-and-soft-regen

**code-Critic reviewed**: slice diff vs default branch (filtered to in-scope paths)
**Date**: 2026-05-29
**Result**: FINDINGS (0 Blockers / 3 Majors / 6 Minors)

## Summary

The PCR-1 implementation is largely well-structured: the 5-class taxonomy, frozen dataclasses, fail-closed UNKNOWN/MIXED paths, lazy audit-log creation, and Windows forward-slash normalization all match the (heavily-Critic-massaged) design. Three real code-level defects that the design-Critic / meta-Critic stack structurally could not reach surface from inspecting the source: **(1) EOL-DRIFT-1 / ADR-033 violation** — three `Path.write_text(...)` call sites omit the `newline=""` kwarg that the sibling PSQ-2 modules (`slice_queue_writer.py:790`, `slice_queue_claim.py:535`) explicitly document as load-bearing for LF-only byte-deterministic emission on Windows; **(2) atomicity gap in `resolve_soft_conflict`** — if `_merge_shippability` raises `_SoftResolutionError` AFTER `_regen_slice_queue` has already written `slice-queue.md` to disk, the file is silently overwritten with the post-overlay content while the resolver returns STOP — the working tree is left in a half-resolved state; **(3) missing defensive VAULT_CLAIM gate inside `_regen_slice_queue`** — design.md's "Resolution algorithm for SOFT class" table explicitly mandates a step-3-of-5 in-helper gate ("if ANY candidate name appears in BOTH with DIFFERENT Claimed-by values, abort") but the helper has no such gate (the `classify_conflict` gate is upstream; the defense-in-depth gate documented inside the resolver is absent). Minors include a `__import__("os")` inline at line 295 instead of a normal import, a broad `except Exception` swallow in `_extract_claim_diff`, and a silent claim-drop path when a candidate block lacks a `Risk-retired:` line.

**CRSI-1 v1 walking-skeleton**: findings are advisory only — do NOT block `/validate-slice`. Per voluntary-restraint precedent (N=16 cumulative at slice-075), code-Critic findings typically defer to a next-slice bundled cleanup (slice-077+ `slice-NNN-bundle-076-code-critic-cleanup`). The 3-Critic stack value-validation extends to **N=12 cumulative** (slice-063 → slice-076) — code-Critic surfaces structurally-distinct defects the design-Critic + meta-Critic stack cannot reach at design time.

## Changed files (in-scope)

```
tools/parallel_conflict_resolver.py
tools/install_audit.py
tests/skills/parallel_conflict_resolver/__init__.py
tests/skills/parallel_conflict_resolver/test_soft_file_set.py
tests/skills/parallel_conflict_resolver/test_diagnose_conflict.py
tests/skills/parallel_conflict_resolver/test_classify_conflict.py
tests/skills/parallel_conflict_resolver/test_overlay_claims_on_queue_text.py
tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py
tests/skills/parallel_conflict_resolver/test_audit_log.py
tests/skills/parallel_conflict_resolver/test_cli.py
tests/methodology/test_pcr_1_adr_present.py
tests/methodology/test_pcr_1_taxonomy_documented.py
tests/methodology/test_commit_slice_skill_pcr_1_diagnostic.py
tests/methodology/test_parallel_conflict_resolver_tool_inventory.py
tests/methodology/test_methodology_changelog.py
tests/methodology/test_utf8_stdout_regression.py
skills/commit-slice/SKILL.md
methodology-changelog.md
plugin.yaml
pyproject.toml
VERSION
INSTALL.md
architecture/slices/slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen/aped_1_battery.py
architecture/slices/slice-076-add-pcr-1-conflict-diagnostic-and-soft-regen/build-log.md
```

## Findings

### Blockers (advisory in v1 — slice-062 will add verdict-driven block on /validate-slice)

None.

### Majors

#### M1: EOL-DRIFT-1 / ADR-033 — three `Path.write_text(...)` sites omit `newline=""`; on Windows produces CRLF where sibling PSQ-2 code explicitly emits LF

- **Claim under review**: `tools/parallel_conflict_resolver.py:561` `out_path.write_text(overlaid, encoding="utf-8")` (in `_regen_slice_queue`); `tools/parallel_conflict_resolver.py:702` `out_path.write_text(output_text, encoding="utf-8")` (in `_merge_shippability`); `tools/parallel_conflict_resolver.py:787` `log_path.write_text(_AUDIT_LOG_HEADER + entry, encoding="utf-8")` (in `_append_audit_log` lazy-create branch); also `log_path.open("a", encoding="utf-8")` at line 789 inherits the same default `newline=None` translation.
- **Issue**: `Path.write_text(...)` defaults to `newline=None`, which on Windows translates every `\n` in the data buffer to `os.linesep` (`\r\n`). Verified locally:
  ```
  >>> p.write_text('a\nb\nc\n', encoding='utf-8')
  >>> p.read_bytes()
  b'a\r\nb\r\nc\r\n'
  ```
  The sibling PSQ-2 modules — `tools/slice_queue_writer.py:781-790` and `tools/slice_queue_claim.py:47-49 + 527-535` — explicitly document this exact failure mode and use `tmp_path.write_text(body, encoding="utf-8", newline="")` for LF-only byte-deterministic emission. PCR-1 is touching the SAME two files (`architecture/slice-queue.md` + `architecture/shippability.md`) but does NOT preserve the LF invariant.

  Consequence on Windows: after a SOFT-class resolution, the regenerated `architecture/slice-queue.md` has CRLF line endings while it was previously LF. The next `git diff` / `git rebase` cycle either (a) silently flips the file's line endings (if `.gitattributes` doesn't pin it — confirmed: `.gitattributes` covers only `skills/**/SKILL.md`, `skills/diagnose/passes/*.md`, `agents/*.md`; `architecture/**/*.md` is NOT pinned), OR (b) when a Windows session runs the next `/slice` regen via `slice_queue_writer.write_slice_queue` which uses `newline=""`, the file gets flipped BACK to LF — producing a noisy round-trip diff for every parallel-merge sequence.

  This is precisely the EOL-DRIFT-1 / ADR-033 class the methodology warns against. The slice's recursive-self-application discipline (RSAD-1, Dim 9) requires the slice's own code to survive its own EOL invariant — PSQ-2's writers explicitly opted in; PCR-1 silently opted out.
- **Evidence**: `tools/parallel_conflict_resolver.py:561,702,787,789`; `tools/slice_queue_writer.py:781-790` (sibling that does it right); `tools/slice_queue_claim.py:527-535` (sibling that does it right); CLAUDE.md `Platform: win32`; `.gitattributes` (no coverage for `architecture/**/*.md`); Python 3.13 `Path.write_text` default `newline=None` behavior verified empirically.
- **Proposed fix**: Apply `newline=""` to all three sites + the `open("a", ...)` append. Concretely:
  ```python
  # line 561 (in _regen_slice_queue):
  out_path.write_text(overlaid, encoding="utf-8", newline="")
  # line 702 (in _merge_shippability):
  out_path.write_text(output_text, encoding="utf-8", newline="")
  # line 787 (in _append_audit_log lazy-create):
  log_path.write_text(_AUDIT_LOG_HEADER + entry, encoding="utf-8", newline="")
  # line 789 (append branch):
  with log_path.open("a", encoding="utf-8", newline="") as f:
  ```
  Add a regression test in `tests/skills/parallel_conflict_resolver/test_resolve_soft_conflict.py` that calls `_regen_slice_queue` on a tmp_path repo and asserts `b"\r\n" not in out_path.read_bytes()`. Cross-reference PSQ-2's `newline=""` rationale in a code comment at the first call site, mirroring `slice_queue_writer.py:781-783`.

#### M2: Atomicity gap in `resolve_soft_conflict` — `_regen_slice_queue` writes to disk before `_merge_shippability` runs; if shippability raises, slice-queue.md is silently overwritten while result is STOP

- **Claim under review**: `tools/parallel_conflict_resolver.py:256-272` (the SOFT-resolution `try:` block) iterates `for u_file in diag.u_files:` and calls `_regen_slice_queue` then `_merge_shippability` for the matching U-files. Both helpers `out_path.write_text(...)` BEFORE returning. The `except _SoftResolutionError as exc:` returns `ResolutionResult(action="STOP", ..., regenerated_files=())`.
- **Issue**: Consider U-files = (`architecture/slice-queue.md`, `architecture/shippability.md`). `_regen_slice_queue` runs first — writes `slice-queue.md` to disk (replacing conflict markers with overlay output). `_merge_shippability` runs second — detects same-slice-number-different-content and raises `_SoftResolutionError(..., ConflictClass.HARD)`. The except clause catches and returns STOP with `regenerated_files=()`.

  Resulting state: `slice-queue.md` on disk is now the post-overlay content (no conflict markers), but the resolver returned STOP. The skill prose at `skills/commit-slice/SKILL.md` Step 5b sub-step 2.5 falls through to SOAD-1's "(a) Abort rebase + investigate" — but `git rebase --abort` will restore the conflict-markered version, masking that PCR-1 silently rewrote the file in a non-atomic partial state. Worse, if the user picks "(b) Resolve conflicts manually + run git rebase --continue", they may inspect the file (which appears already-resolved), `git add` it, and continue — accepting the PCR-1-generated overlay content for a conflict PCR-1 declared HARD. This is precisely the silent partial-resolution that ADR-069's atomicity contract ("never partially auto-resolve") was supposed to prevent.

  Per Newman (Building Microservices, error semantics) and McGraw (defense in depth): a function that mutates two artifacts must either fully succeed both or roll both back; PCR-1 currently has neither tx-atomicity nor rollback.
- **Evidence**: `tools/parallel_conflict_resolver.py:256-272` (SOFT-resolution loop + except clause); design.md L130 "MIXED — atomicity — never partial auto-resolve"; ADR-069 L130-L137 (Resolution algorithm shippability.md Edge-cases column documents HARD-escalation but not the rollback semantics).
- **Proposed fix**: One of the following, by preference:
  1. **Stage-then-commit pattern**: refactor `_regen_slice_queue` and `_merge_shippability` to return the resolved text WITHOUT writing to disk; `resolve_soft_conflict` collects all resolved texts; only if all succeed, write all in a single batch before `git add`. The `_SoftResolutionError` path then leaves the working tree untouched.
  2. **Snapshot + restore**: before the loop, read `git show :1:<file>` / `git show :2:<file>` for each U-file; on `_SoftResolutionError`, restore the original conflict-markered content via `git checkout --conflict=merge <file>` (or equivalent). Less clean than (1).

  Option (1) is preferred — matches the design's intent and avoids depending on git plumbing. Add a regression test: SOFT classification + U-files=(slice-queue.md, shippability.md), but inject a `_merge_shippability` failure via patching; assert `slice-queue.md` on disk remains conflict-markered post-STOP.

#### M3: Defense-in-depth VAULT_CLAIM gate documented in design.md "Resolution algorithm" step 3 of 5 is absent from `_regen_slice_queue`

- **Claim under review**: design.md L136 "Resolution algorithm for SOFT class" `architecture/slice-queue.md` row step (3): "**VAULT_CLAIM gate** (per /critique B4 ACCEPTED-FIXED): walk the keys of both claim dicts; if ANY candidate name appears in BOTH with DIFFERENT `Claimed-by:` values, abort with `action: STOP, conflict_class: VAULT_CLAIM` (do NOT auto-resolve — PSQ-2's existing newest-wins merge would silently auto-resolve what PCR-2 reserves for timestamp-winner + light-Critic; defense-in-depth defeats this here)." critique.md B4 ACCEPTED-FIXED fix (c): "Defensive post-merge guard in `_regen_slice_queue`: re-parse resolved queue's claim dict; abort with `action: STOP, conflict_class: VAULT_CLAIM` if same-candidate-different-identity remains post-merge."
- **Issue**: `_regen_slice_queue` (lines 530-562) reads stages 2 + 3, computes `claims_2, claims_3 = _extract_claim_diff(text_2, text_3)`, then calls `merged_claims = _merge_claim_dicts(claims_2, claims_3)` and overlays. There is NO check that walks both claim dicts for same-candidate-different-identity. `_merge_claim_dicts` (lines 565-584) uses newest-`Claimed-at`-wins regardless of identity — silently auto-resolving the exact VAULT_CLAIM case the design explicitly reserves for PCR-2.

  Currently the only protection is `classify_conflict`'s upstream gate via `_has_same_candidate_different_identity(diag.claim_history)`. That works IF `diag.claim_history` was populated correctly. But:
  - If `_extract_claim_diff` failed silently (e.g., `parse_queue_text` raised an exception — caught by the broad `except Exception` at line 525), `claim_history` is `()` → `_has_same_candidate_different_identity` returns False → classify returns SOFT → `_regen_slice_queue` proceeds with `_merge_claim_dicts` newest-wins, silently picking one of the two different claimants.
  - If `claim_history` was populated by a stale `ConflictDiagnostic` (e.g., the CLI was invoked with a stale-state `--diagnose` output piped into a separate classify), the upstream gate could be lying.

  Defense-in-depth means the regen helper itself re-validates. The design says exactly that ("defense-in-depth defeats this here"). The code does not.
- **Evidence**: `tools/parallel_conflict_resolver.py:530-562` (`_regen_slice_queue`); `tools/parallel_conflict_resolver.py:565-584` (`_merge_claim_dicts` newest-wins); design.md L136 step (3); critique.md B4 fix (c) ACCEPTED-FIXED disposition.
- **Proposed fix**: Inside `_regen_slice_queue`, after computing `claims_2` and `claims_3` and BEFORE calling `_merge_claim_dicts`, add the gate:
  ```python
  # Defense-in-depth VAULT_CLAIM gate (design.md L136 step 3 of 5;
  # critique.md B4 fix (c) ACCEPTED-FIXED). classify_conflict's upstream
  # gate may have been bypassed (silent _extract_claim_diff failure, stale
  # diag); re-validate here.
  for name in set(claims_2) & set(claims_3):
      cb2 = claims_2[name].get("claimed_by")
      cb3 = claims_3[name].get("claimed_by")
      if cb2 and cb3 and cb2 != cb3:
          raise _SoftResolutionError(
              f"slice-queue.md candidate {name!r}: same-candidate-different-"
              f"identity claim collision (Claimed-by stage 2={cb2!r}, "
              f"stage 3={cb3!r}); VAULT_CLAIM deferred to PCR-2",
              ConflictClass.VAULT_CLAIM,
          )
  ```
  Add a regression test: synthesize a `ConflictDiagnostic` with `claim_history=()` (simulating an upstream classify-time gate miss) but actually stage `slice-queue.md` stages 2 and 3 with different-identity claims; assert `_regen_slice_queue` raises `_SoftResolutionError` with `conflict_class=VAULT_CLAIM`.

### Minors

#### m1: `__import__("os")` inline at line 295 instead of standard `import os`

- **Claim under review**: `tools/parallel_conflict_resolver.py:295` inside `resolve_soft_conflict`:
  ```python
  env={**__import__("os").environ, "GIT_EDITOR": "true"},
  ```
- **Issue**: Per Fowler / general Python style: there's no reason to inline-import `os` via `__import__`. The module is already in standard library, used at top of file would be one line, and `__import__("os")` is a code-smell (typically used to defeat tooling like vulture or to defer side-effecting imports). It defeats grep-for-imports tooling, makes the dependency invisible to `pyflakes`/`ruff`, and reads as if there's a special reason it's deferred — but there isn't.
- **Evidence**: `tools/parallel_conflict_resolver.py:295`; no other `__import__` usages in the file.
- **Proposed fix**: Add `import os` at top of file alongside `import argparse`, etc., and change line 295 to `env={**os.environ, "GIT_EDITOR": "true"}`.

#### m2: `_extract_claim_diff` catches bare `Exception` — over-broad swallow per Fowler narrowing

- **Claim under review**: `tools/parallel_conflict_resolver.py:519-526`:
  ```python
  try:
      claims_2 = parse_queue_text(text_2) if text_2 else {}
  except Exception:  # noqa: BLE001 - parser raises ClaimUsageError on partial blocks
      claims_2 = {}
  try:
      claims_3 = parse_queue_text(text_3) if text_3 else {}
  except Exception:  # noqa: BLE001
      claims_3 = {}
  ```
- **Issue**: The docstring at `tools/slice_queue_claim.py:218` says `parse_queue_text` raises `ClaimUsageError` ONLY on partial known claim block. Catching bare `Exception` (with `noqa: BLE001`) swallows EVERYTHING — including `AttributeError` from a bug introduced into `parse_queue_text`, `MemoryError` from a pathological input, `KeyboardInterrupt` (well, KI inherits from BaseException so this one is fine), etc. The narrowed correct form is `except ClaimUsageError:` (importable from `tools.slice_queue_claim`). The comment correctly identifies the expected exception type but the code doesn't narrow to it.

  Compounds with M3: a silent `parse_queue_text` failure here means `claim_history` becomes `()`, which lets a VAULT_CLAIM-class collision slip past `classify_conflict`'s upstream gate undetected. (Defense-in-depth M3 fixes that, but the root cause is here.)
- **Evidence**: `tools/parallel_conflict_resolver.py:519-526`; `tools/slice_queue_claim.py:218` (`Raises ClaimUsageError ONLY on PARTIAL known claim block`).
- **Proposed fix**:
  ```python
  from tools.slice_queue_claim import ClaimUsageError  # noqa: PLC0415 (lazy at top of _extract_claim_diff)
  ...
  try:
      claims_2 = parse_queue_text(text_2) if text_2 else {}
  except ClaimUsageError as exc:
      print(f"parallel-conflict-resolver: stage 2 queue parse failed: {exc!r}",
            file=sys.stderr)
      claims_2 = {}
  ```
  Symmetric for stage 3.

#### m3: `_overlay_claims_on_queue_text` silently drops claims for candidates whose block has no `**Risk-retired:**` line

- **Claim under review**: `tools/parallel_conflict_resolver.py:587-649` (`_overlay_claims_on_queue_text`). The post-emit-hook only fires when a line `startswith("- **Risk-retired:**")`. If a candidate is in `merged_claims` but its block has no `Risk-retired:` line, the new Claimed-by/at lines are never inserted.
- **Issue**: Per Hendrickson / Bach edge-case discovery: a candidate authored without the canonical PSQ-1 5-field shape (e.g., a forward-compat extension that omits `Risk-retired:`, or a temporary scaffolding entry pre-`Risk-retired:`) would silently lose its claim metadata after a SOFT-resolution. The function returns the modified queue text but the claim disappears with no warning. Documented behavior at design.md L137 says "Candidates in `merged_claims` whose names are not present in `text_3` are dropped" — but here the candidate IS present, just malformed. Different class, same silent-drop symptom.
- **Evidence**: `tools/parallel_conflict_resolver.py:637-647` (post-Risk-retired insertion hook).
- **Proposed fix**: After processing all lines, walk `merged_claims` keys and check whether each was inserted. If a candidate was present in `queue_text` (heading seen during walk) but no claim was inserted (because no Risk-retired line was encountered), emit a `print(... file=sys.stderr)` warning per the APED-1 "loud-malformed" criterion. Alternative: track `claim_inserted_for: set[str]` during the walk; at end, log any `merged_claims.keys() & candidates_seen - claim_inserted_for` as "claim dropped — candidate block missing Risk-retired line". Cheap to add, prevents silent loss.

#### m4: Many test files import `pytest` but never use it

- **Claim under review**: `tests/skills/parallel_conflict_resolver/test_classify_conflict.py:22 import pytest` — `pytest` is not referenced anywhere in the file. Same pattern at `test_resolve_soft_conflict.py:25`, `test_diagnose_conflict.py:21`, `test_audit_log.py:20`, `test_soft_file_set.py:23`, `test_pcr_1_adr_present.py:19 import pytest` (not used). `test_cli.py:17 import pytest` IS used for `pytest.fail`. `test_overlay_claims_on_queue_text.py` has no pytest import (correct).
- **Issue**: Cosmetic; per Fowler "dead code" smell. ruff/pyflakes would flag these as unused imports. Doesn't affect runtime but adds noise.
- **Evidence**: see file refs above.
- **Proposed fix**: Remove unused `import pytest` lines from `test_classify_conflict.py`, `test_resolve_soft_conflict.py`, `test_diagnose_conflict.py`, `test_audit_log.py`, `test_soft_file_set.py`, `test_pcr_1_adr_present.py`. Keep in `test_cli.py` (used for `pytest.fail`).

#### m5: `_extract_u_files` does not handle porcelain v1 rename-with-arrow paths for unmerged states

- **Claim under review**: `tools/parallel_conflict_resolver.py:386-400`:
  ```python
  for line in proc.stdout.splitlines():
      ...
      x, y = line[0], line[1]
      if x == "U" or y == "U" or (x == "A" and y == "A") or (x == "D" and y == "D"):
          path = line[3:].strip()
          if path.startswith('"') and path.endswith('"'):
              path = path[1:-1]
          u_files.append(path)
  ```
- **Issue**: Porcelain v1 emits `XY <space> PATH` for non-renames and `XY <space> ORIG_PATH -> NEW_PATH` for some rename cases (typically `R` / `C` for renames/copies, but with rerere or partial renames `UU` can co-occur with a rename arrow in pathological cases per `git status` man). The current code takes `line[3:]` verbatim → would yield `"ORIG_PATH -> NEW_PATH"` as the path, and SOFT-set membership check would silently fail. Defense-in-depth gap. Per Hendrickson edge-cases: this is a rare-but-real path that would fail-closed (HARD class) silently instead of UNKNOWN-loud.
- **Evidence**: `tools/parallel_conflict_resolver.py:386-400`; `git status` man page for `--porcelain` format.
- **Proposed fix**: Add a defensive check — if `" -> "` is in `path`, split and take the new path (or, per APED-1 loud-malformed, log a warning and skip the entry, returning UNKNOWN at classify-time). Concretely:
  ```python
  if " -> " in path:
      # Renamed/copied unmerged path — extract NEW name; or escalate
      # to UNKNOWN if the rename-with-conflict semantics are unclear.
      print(f"parallel-conflict-resolver: rename-with-conflict on {path!r} — "
            f"escalating to UNKNOWN per APED-1 loud-malformed",
            file=sys.stderr)
      return ()  # Force UNKNOWN classification
  ```

#### m6: Audit log `_append_audit_log` lazy-create is TOCTOU non-atomic and loses the first writer's entry on race

- **Claim under review**: `tools/parallel_conflict_resolver.py:786-790`:
  ```python
  if not log_path.exists():
      log_path.write_text(_AUDIT_LOG_HEADER + entry, encoding="utf-8")
  else:
      with log_path.open("a", encoding="utf-8") as f:
          f.write(entry)
  ```
- **Issue**: Two parallel `/commit-slice --merge` sessions both hit `not log_path.exists()` → both `write_text` (which truncates). The last writer's content wins; the first writer's entry is LOST (overwritten, not interleaved). ADR-069's "race-acceptance per ADR-067 cooperative-not-adversarial threat model" documents acceptance of interleaving, but the actual failure mode here is data loss for the first writer, not interleaving. This is partially noted in critique M7 / ACCEPTED-FIXED — but the documented mitigation ("single `open(a, "a")` per append") is not what the code does for the lazy-create branch.
- **Evidence**: `tools/parallel_conflict_resolver.py:786-790`; critique.md M7 fix prose; ADR-069 § Audit log (per design.md L67).
- **Proposed fix**: Use a single `open("a")` for both branches, conditioning the header write on whether the file was just created:
  ```python
  needs_header = not log_path.exists()
  with log_path.open("a", encoding="utf-8", newline="") as f:
      if needs_header:
          f.write(_AUDIT_LOG_HEADER)
      f.write(entry)
  ```
  Still has a TOCTOU window (both writers may see `needs_header=True` and write the header twice), but the entries themselves are preserved via `O_APPEND` semantics. Doubled header is a recoverable cosmetic defect; lost entry is not.

## Dimensions checked

- [x] **Unfounded assumptions** — m2 (`except Exception` masks programming errors via overbroad swallow). The slice's docstrings track its implementation accurately elsewhere; the critique/critique-review stack already swept Dim 1 thoroughly (B1, B3, B4, m1).
- [x] **Missing edge cases** — M2 (mid-loop write atomicity), m3 (malformed candidate block silent claim-drop), m5 (porcelain rename-with-arrow), m6 (TOCTOU lazy-create data loss); critique stack already addressed stage-missing-on-one-side (M2-pre-disposition).
- [x] **Over-engineering** — none new beyond critique-time observations. m1 (`__import__("os")` inline) is a minor smell but borderline Dim 9 (unusual idiom) vs Dim 3.
- [x] **Under-engineering** — M3 (defense-in-depth VAULT_CLAIM gate documented in design but absent from `_regen_slice_queue` — AC4 fail-closed boundary is structurally weaker than designed).
- [x] **Contract gaps** — none new; the dataclass / enum surface is consistent with design.md; CLI exit-code semantics match documented behavior; JSON output shape is grep-stable.
- [x] **Security** — none. PCR-1 is local-only (per ADR-069 § Adversarial model cooperative-not-adversarial). All subprocess args are constant strings (`git status --porcelain`, `git show :STAGE:PATH`, `git add`, `git rebase --continue`, `git log -1 --format=%cI`) — no user-controlled flow into shell. No `shell=True` anywhere. Audit log writes go to a fixed path under `architecture/`. m6 audit-log race is a coordination defect, not a security defect.
- [x] **Drift from vault** — M1 (sibling PSQ-2 EOL discipline at `slice_queue_writer.py:790` + `slice_queue_claim.py:535` not followed by PCR-1's homologous write sites); M3 (design.md L136 step 3 specifies a defense-in-depth gate the code omits).
- [x] **Web-known issues** — Skipped — WebSearch not invoked for this slice. PCR-1's API surface is internal-only (subprocess git + Path I/O + frozen dataclasses + argparse); no third-party SDK / API with versioned quotas to check. Python 3.13 `Path.write_text` default `newline=None` behavior is documented stdlib and verified empirically locally (the M1 evidence) rather than via web search.
- [x] **Cross-cutting conformance** — M1 is **EOL-DRIFT-1 / ADR-033** + algorithm-path-conformance-with-pre-existing-branches (sibling PSQ-2 writers correctly LF-pin; PCR-1's structurally-identical writers do not). M3 is RSAD-1 (slice's own design states an in-helper gate; slice's own code omits it). m5 is APED-1-class (porcelain parse rule not executed against full porcelain-v1-rename-with-arrow corpus). m6 is concurrency / cooperative-coordination-model conformance — the documented race-acceptance is interleaving, not first-writer data loss.

## CRSI-1 v1 disposition (advisory only)

Per CRSI-1 v1 walking-skeleton (`methodology-changelog.md` v0.64.0 / ADR-059): code-Critic findings are advisory and do NOT block `/validate-slice`. Per voluntary-restraint precedent (N=16 cumulative at slice-075), these 9 findings (3 Majors + 6 Minors) are candidates for deferral to a future bundled cleanup slice — **`slice-NNN-bundle-076-code-critic-cleanup`** — rather than in-band /validate-slice blocking. The user retains final disposition authority at `/reflect`'s Critic-calibration section.

**3-Critic stack value-validation N=12 cumulative** (slice-063 → slice-076): code-Critic surfaced 3 structurally-distinct Major defects the design-Critic + meta-Critic stack could not reach at design time:
- M1 EOL-DRIFT-1 — cross-spec parity violation between PCR-1 writers and sibling PSQ-2 writers (design-Critic stack reviews design.md / ADRs / mission-brief, not code-level call-site EOL discipline)
- M2 atomicity gap — mid-loop write-then-raise sequence (design-Critic stack reviews the design's "atomicity — never partial auto-resolve" contract; doesn't trace the actual try/except boundary in the impl)
- M3 missing defense-in-depth gate — the design EXPLICITLY mandates this gate at L136 step 3; the code-Critic catches that the impl is structurally weaker than designed (design-Critic verified the design was correct; the gap is design → code translation)

Voluntary-restraint discipline candidate disposition: **DEFER all 9 to slice-NNN-bundle-076-code-critic-cleanup** (would extend voluntary-restraint to N=17 cumulative). Bundle-074 cleanup work was re-queued at this slice's scaffold per mission-brief Re-scoping history L57-61 — both bundles can ship as a single slice if scope permits, or as separate slice-077+ slices.

User retains override: an explicit "fix-in-band" disposition at `/reflect` would defer `/validate-slice` and `/commit-slice` until M1+M2+M3 (and optionally minors) are fixed. The recommended path for v1 walking-skeleton is voluntary-restraint defer.
