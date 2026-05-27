# Code Review: Slice 072 add-psq-2-claim-machinery

**code-Critic reviewed**: slice diff vs `master` (filtered to in-scope paths per ADR-062 / NAW-1 union-of-three-sources)
**Date**: 2026-05-27
**Result**: FINDINGS (advisory; CRSI-1 v1)

## Summary

PSQ-2 is a well-scoped additive extension of PSQ-1's stable on-disk contract. The 3-Critic stack at /critique + /critique-review caught the heavy structural concerns (CRLF tolerance, `newline=""` on Windows, `_ROOT_ONLY_TOOLS` bucketing, 3-case git-config absence detection, partial-claim malformed detection, forward-compat `_extra_field_lines` extras pass-through, `--queue` override). The remaining code-Critic findings are contract / cross-cutting / edge-case defects that survived dual-Critic review:

- **One Major (M1)**: silent contract divergence between `apply_claim`'s on-disk emission order (extras BEFORE claim) and `_format_entry`'s emission order (claim BEFORE extras) — a `claim` then `/slice` regen rewrites byte ordering of the same logical state, defeating the byte-deterministic round-trip the slice explicitly chose `newline=""` to achieve.
- **Three Majors (M2-M4)**: too-broad `except Exception` in the writer's claim-merge path silently discards `ClaimUsageError` that the user-facing CLI is designed to surface; a malformed sibling entry can block release of a healthy entry (noisy-neighbor); `_atomic_write_text` does not clean up the orphan `.tmp` sibling on `os.replace` failure.
- **Five minors (m1-m5)**: case-sensitivity diagnostic ambiguity on `claimed_by` vs `Claimed-by`; duplicate `Claimed-by:` lines silent last-write-wins; blank-line-between-Risk-retired-and-claim silently drops the claim on parse; test fixture XDG_CONFIG_HOME isolation gap; methodology-changelog "17 tests" prose-vs-actual-18 drift.

**No Blockers** — the slice ships safely as the cooperative-coordination contract ADR-067 §"Adversarial model" documents. Per CRSI-1 v1 walking-skeleton advisory-only discipline + slice-064/065/067/070/071 voluntary-restraint precedent N=12 cumulative — all 9 findings DEFERRED to slice-073+ bundled-cleanup nomination (`slice-NNN-bundle-072-code-critic-cleanup` shape).

## Changed files (in-scope)

- INSTALL.md
- VERSION
- methodology-changelog.md
- plugin.yaml
- pyproject.toml
- skills/slice/SKILL.md
- tools/install_audit.py
- tools/slice_queue_claim.py
- tools/slice_queue_writer.py
- tests/methodology/test_psq_2_claim_machinery.py
- tests/methodology/test_utf8_stdout_regression.py
- tests/methodology/test_methodology_changelog.py
- tests/methodology/test_vault_root_constant.py
- architecture/slices/slice-072-add-psq-2-claim-machinery/build-log.md

## Findings

### Blockers (advisory in v1 — slice-062 ships verdict-driven block; not yet shipped)

None.

### Majors

#### M1: Claim-line position contract diverges between `apply_claim` and `_format_entry` (forward-compat extras ordering)

- **Claim under review**: design.md §"Schema extension" specifies claim block AFTER Risk-retired + AFTER any pre-existing `_extra_field_lines`; `tools/slice_queue_claim.py::_find_insert_index_for_claim` implements this correctly (claim inserted AFTER extras). But `tools/slice_queue_writer.py::_format_entry` emits claim lines BEFORE extras (`f"- **Claimed-by:** {claimed_by}"` + `f"- **Claimed-at:** {claimed_at}"` then `for extra in extras: lines.append(extra)`).
- **Issue**: `apply_claim` (CLI surface) produces on-disk ordering `[Risk-retired, ...extras, Claimed-by, Claimed-at]`. The very next `/slice` Step 6.5 regen via `write_slice_queue` → `_format_entry` rewrites the SAME logical state as `[Risk-retired, Claimed-by, Claimed-at, ...extras]`. Two surfaces, two orderings for the same data. This silently rearranges bytes in the queue file every regen-after-claim cycle, defeating the byte-deterministic round-trip the slice deliberately chose `newline=""` to provide.
- **Evidence**: Empirically confirmed by code-Critic — `apply_claim` on a queue with `Some-Future-Key:` extra emits `Risk-retired → Some-Future-Key → Claimed-by → Claimed-at`; `_format_entry` for the parsed-then-rendered same logical entry emits `Risk-retired → Claimed-by → Claimed-at → Some-Future-Key`. Both `parse_queue_text` round-trip the dict correctly, but the on-disk bytes differ. Per Fowler "Duplicated Code" smell.
- **Proposed fix**: Pick one canonical ordering and apply both surfaces. Recommend `[Risk-retired, Claimed-by, Claimed-at, ...extras]` (matches design.md §"Schema extension" prose). Change `_find_insert_index_for_claim` to insert at `retired_idx + 1` directly (drop the while-loop that advances past extras), OR change `_format_entry` to emit extras BEFORE claim lines. Add a regression test in `test_psq_2_claim_machinery.py` exercising `apply_claim → write_slice_queue regen → byte-equal` on a queue containing forward-compat extras.

#### M2: `write_slice_queue` swallows `ClaimUsageError` silently — defeats the coordination-safety contract

- **Claim under review**: `tools/slice_queue_writer.py::write_slice_queue` — `try: ... parse_queue_text(existing_text) except Exception: existing_claims = {}`.
- **Issue**: `except Exception` catches `ClaimUsageError` (the malformed-claim-block signal `parse_queue_text._validate_entry` raises) along with the intended `ImportError` bootstrap-safety case. If a previously-written queue file has a partial claim block (one of `Claimed-by:`/`Claimed-at:` present without the other), the next `/slice` Step 6.5 invocation silently regenerates the queue with that entry UNCLAIMED. The malformed-claim signal — which the CLI surfaces as exit 2 — is discarded. Per Newman "fail loud" / contract-gaps: the coordination-safety guarantee PSQ-2 advertises is contradicted by the very integration that gates regeneration.
- **Evidence**: Code-trace; the comment ("PSQ-2 module missing OR malformed existing queue — non-fatal") conflates `ImportError` (bootstrap; recovering gracefully is correct) with `ClaimUsageError` (module imported successfully; existing queue has a real defect — silently regenerating unclaimed loses data and hides the defect).
- **Proposed fix**: Narrow the except to `ImportError` + `OSError`; let `ClaimUsageError` propagate (or at minimum, log a stderr warning + bubble up). Or, strictly per the coordination-safety contract — re-raise and let `/slice` Step 6.5 fail loudly.

#### M3: Malformed sibling-entry blocks `apply_release` / `apply_claim` on healthy candidate (noisy-neighbor)

- **Claim under review**: `tools/slice_queue_claim.py::apply_claim` and `apply_release` both call `parse_queue_text(text)` first, which walks the ENTIRE file and raises `ClaimUsageError` on ANY partial-known-claim-block (per `_validate_entry`).
- **Issue**: If `architecture/slice-queue.md` contains a malformed claim block on candidate B (e.g. produced by an interrupted/crashed third-party edit), `--release candidate-A` or `--claim candidate-A` on a HEALTHY candidate A is blocked with `malformed claim block for B`. The user has no per-candidate recovery path other than hand-editing the queue file — which the CLI is supposed to provide instead. Per Hendrickson edge-case heuristic "partial state of unrelated peer".
- **Evidence**: Empirically confirmed by code-Critic — `release BLOCKED by sibling-entry malformed: malformed claim block for sick` when target is `healthy` and a sibling `sick` has partial claim. `--force-claim` has the same problem.
- **Proposed fix**: Loosen `parse_queue_text` to a "best-effort" mode for global parsing, do strict validation only on the target name; OR document the noisy-neighbor coupling in CLI help + provide `--ignore-malformed-siblings`; OR at minimum, change the error message to direct the user to fix the malformed entry. Add a pinned regression test.

#### M4: `_atomic_write_text` leaks orphan `.tmp` sibling on `os.replace` failure

- **Claim under review**: `tools/slice_queue_claim.py::_atomic_write_text` writes `tmp_path` then calls `os.replace(tmp_path, path)` — if replace raises, the `.tmp` sibling stays on disk indefinitely. Same defect at `tools/slice_queue_writer.py` `.tmp` write.
- **Issue**: Per OWASP file-handling / McGraw defense-in-depth: temp-file leakage on partial-failure paths accumulates filesystem detritus that future writers can collide with. The slice's own test (`test_claim_cli_atomic_write_via_tmp_sibling_and_os_replace`) verifies the original file is intact on failure but does NOT assert `.tmp` is cleaned up, hiding this defect from the pin.
- **Evidence**: Empirical — original preserved: True; orphaned .tmp exists: True; orphaned .tmp content: 'new'.
- **Proposed fix**: Wrap `os.replace` in try/except OSError → `tmp_path.unlink(missing_ok=True)` + re-raise. Apply same fix to `tools/slice_queue_writer.py:789-791`. Extend the existing atomic-write test to assert `not tmp_path.exists()` after the simulated-failure assertion.

### Minors

#### m1: Field-line regex permissiveness — case-sensitivity diagnostic ambiguity

- **Claim under review**: `tools/slice_queue_claim.py::_FIELD_LINE_RE` accepts `[A-Za-z][A-Za-z0-9_-]*` keys; only `Claimed-by` / `Claimed-at` exact-match are recognized; all other keys → `_extra_field_lines`.
- **Issue**: `- **claimed_by:** value` (lowercase / underscore variant — plausible human typo) is accepted by the regex, fails the `key == "Claimed-by"` exact-string check, gets stored as an extra forward-compat field. If the same entry has a properly-cased `Claimed-at:` line, `_validate_entry` raises `malformed claim block for <name>` — the diagnostic is misleading (the line LOOKS like a Claimed-by).
- **Proposed fix**: Either case-insensitive matching for the two known fields, OR make the diagnostic include line content: `"malformed claim block for <name> — found Claimed-at without Claimed-by (check key case-sensitivity on field lines)"`. Cosmetic but improves debuggability.

#### m2: Duplicate `Claimed-by:` lines silently last-write-wins

- **Claim under review**: `tools/slice_queue_claim.py::parse_queue_text` — `if key == "Claimed-by": current_entry["claimed_by"] = value`.
- **Issue**: A queue with two `- **Claimed-by:** ...` lines under one entry silently overwrites the first claim. Can happen if `apply_claim` is interrupted between dedupe and insert, OR if a human concurrent-edits the queue. Per the coordination-safety contract, a duplicate ownership signal should be malformed, not silently last-write-wins.
- **Evidence**: Empirical — input with two Claimed-by lines (alice, bob) returns `{'claimed_by': 'bob', ...}` — bob wins silently.
- **Proposed fix**: Add a `claimed_by` / `claimed_at` membership check in the parse loop: `if "claimed_by" in current_entry: raise ClaimUsageError("duplicate Claimed-by for ...")`.

#### m3: `parse_queue_text` silently drops claims if a blank line interrupts the post-Risk-retired field block

- **Claim under review**: `tools/slice_queue_claim.py` — `if not field_match: after_risk_retired = False; continue`.
- **Issue**: A queue with a blank line between `Risk-retired:` and `Claimed-by:` (a plausible human readability edit — markdown convention is to separate logical blocks with blanks) silently has its claim DROPPED. The writer never emits this shape, but `apply_release` round-trips through this code path, and any human edit via vi/nano/IDE-markdown-formatter could insert such a blank.
- **Evidence**: Empirical — `{'foo': {'_extra_field_lines': []}}` — `claimed_by`/`claimed_at` fields absent from parse result, silently.
- **Proposed fix**: Don't reset `after_risk_retired` on blank lines — only on a new entry header or non-field-line that is also non-blank. Add a unit test asserting blank-line tolerance.

#### m4: Test fixture's git-config isolation does not pin XDG_CONFIG_HOME

- **Claim under review**: `tests/methodology/test_psq_2_claim_machinery.py::isolated_git_env` fixture sets `GIT_CONFIG_NOSYSTEM=1`, `HOME`, `USERPROFILE`, `GIT_CONFIG_GLOBAL` but does NOT clear `XDG_CONFIG_HOME`.
- **Issue**: Per `git-config(1)`, git reads `$XDG_CONFIG_HOME/git/config` when set, in addition to `~/.gitconfig`. If a future CI machine or contributor's box has `XDG_CONFIG_HOME` set with a `user.name`/`user.email`, the `test_claim_cli_exits_2_on_missing_user_name_or_user_email` test would falsely PASS (git reads from XDG_CONFIG_HOME; the test's expectation of returncode==2 would FAIL). Verified watertight on this host (XDG_CONFIG_HOME unset).
- **Proposed fix**: Add `monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)` + `monkeypatch.setenv("GIT_CONFIG_SYSTEM", str(tmp_path / "nonexistent-system"))` for symmetry with `GIT_CONFIG_GLOBAL`. Inline rationale comment citing git-config(1) §FILES.

#### m5: Methodology-changelog Validation prose drifts from actual test count

- **Claim under review**: `methodology-changelog.md` v0.71.0 §Validation: "`tests/methodology/test_psq_2_claim_machinery.py` (17 unit tests covering AC1-AC4)".
- **Issue**: Actual file has 18 tests (`grep -c "^def test_" tests/methodology/test_psq_2_claim_machinery.py` = 18). The `test_r_19_retired_in_risk_register` test added at Phase G for AC5 was overlooked when the methodology-changelog entry was authored at Phase F.
- **Proposed fix**: Bump "17 unit tests" → "18 unit tests covering AC1-AC5" in methodology-changelog.md v0.71.0 §Validation. Slice-073+ bundled cleanup.

## Dimensions checked

- [x] **Unfounded assumptions** — m5 (changelog "17 tests" doesn't match actual 18). `apply_release` docstring states forward-compat preservation; verified — preservation is by virtue of NOT touching extras; claim is true.
- [x] **Missing edge cases** — m3 (blank-line interruption of claim block); m2 (duplicate Claimed-by); M3 (malformed sibling-entry noisy-neighbor); M4 (`.tmp` leak on `os.replace` failure). Stronger coverage of "human edit of the queue file" class.
- [x] **Over-engineering** — none. The code is tight; 440 LOC for what it does. `_build_claimed_block` / `_build_unclaimed_block` closure factories could be plain functions but not over-engineered enough to file.
- [x] **Under-engineering** — none specific to documented ACs. The cooperative-coordination scope is documented in ADR-067 §Adversarial model — race-window between read and write, lack of file lock, etc. are all in-scope-deferred per the slice's own contract.
- [x] **Contract gaps** — M1 (`apply_claim` vs `_format_entry` emission-order divergence); M2 (silently-swallowed `ClaimUsageError`); m1 (case-sensitivity diagnostic ambiguity).
- [x] **Security** — none. No injection vectors (`subprocess.run` uses list-form, no `shell=True`); no secrets logged; git config read via `subprocess.run` is bounded with `timeout=5s` + `capture_output=True`. Test fixture sets sandboxed env. Cooperative coordination per ADR-067 §Adversarial model — claim mechanism explicitly NOT a security boundary.
- [x] **Drift from vault** — none load-bearing. design.md §"Components touched" matches the actual diff (440 LOC slice_queue_claim.py; modified slice_queue_writer.py; new test files; 5-part PMI-1 bump). The minor changelog-prose-count drift (m5) is the only material drift.
- [x] **Web-known issues** — `newline=""` on `Path.write_text` is the correct fix for the CRLF-translation defect cited (Python docs + Real Python 2024 tutorial confirm; `newline=""` and `newline="\n"` are equivalent for write-side LF preservation). No post-cutoff API deprecation hits. `subprocess.run(..., capture_output=True, text=True, timeout=5)` pattern canonical for Python 3.13.
- [x] **Cross-cutting conformance** — m4 (test fixture isolation lacks XDG_CONFIG_HOME pin). EOL-DRIFT-1 conformance: the slice's CRLF→LF normalization in `parse_queue_text` is exactly the EOL-DRIFT-1 normalize-before-compare discipline. APED-1: the new `_FIELD_LINE_RE` parse rule was executed against an adversarial battery during this review (key with space, leading-digit, dot-in-key, lowercase, trailing-space — all behaviors confirmed). RSAD-1: the slice's own tests pass — 18 PSQ-2 tests + 21 net new tests + 987 full-pytest. Phantom-import: all imports verified resolvable.

## Disposition

Per CRSI-1 v1 walking-skeleton advisory-only discipline (slice-064/065/067/068/070/071 N=7 precedent for code-Critic advisory-only handling) — all 9 findings ADVISORY; do NOT block `/validate-slice`. Slice-073+ active nomination: `slice-NNN-bundle-072-code-critic-cleanup` (9-finding backlog).

**Voluntary-restraint discipline extends to N=13 cumulative** (slice-037/046/050/052/055/056/057/061/065/067/070/071/072 — slice-072 itself is a new-mechanism mint with full Inclusion-heuristic firing per the v0.71.0 entry, but the code-Critic findings deferred to slice-073+ inherit the voluntary-restraint discharge pattern). Sources:

- [How Is Newline Handled in Python and Various Editors](https://jdhao.github.io/2018/12/08/newline_vim_python_sublime_notepad/)
- [Choosing the Line Ending — Real Python](https://realpython.com/lessons/python-line-ending/)
- [pathlib.Path.write_text newline argument — Python tracker issue 23706](https://bugs.python.org/issue23706)
