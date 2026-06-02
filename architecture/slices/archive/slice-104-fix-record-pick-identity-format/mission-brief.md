# Slice 104: fix-record-pick-identity-format

**Mode**: Standard
**Estimated work**: 0.5 day
**Risk retired**: an unregistered recurring defect — the `/slice` Step 6.5 pick-provenance writer serializes a Python tuple repr into the `## Pick log`, observed on the slice-103 pick and prior picks per the repo owner. Register the new risk at `/reflect`.
**Test-first**: true

## Intent

`tools/slice_queue_writer.record_pick(picker_identity: str)` f-string-renders its argument directly into the pick-log line `- <slice> — picked <ts> by <picker_identity>`, expecting a pre-joined `"<name> <email>"` string. But `tools/slice_queue_claim.read_git_config_user()` returns a `(name, email)` **tuple**, and the documented `/slice` SKILL.md Step 6.5 invocation passes it raw — so the provenance line came out as `by ('Shubhendu Shubham', 's2.shubh2@gmail.com')` instead of `by Shubhendu Shubham s2.shubh2@gmail.com`. It recurs on every pick until the documented glue is fixed. This slice makes `record_pick` robust to the `(name, email)` shape its real caller supplies, fixes the SKILL.md snippet, and pins a regression test so the malformed line can never silently return.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/bugs/test_record_pick_identity_tuple_repr.py | test_record_pick_with_identity_tuple_emits_well_formed_line | WRITTEN-FAILING |

## Acceptance criteria

1. `tests/bugs/test_record_pick_identity_tuple_repr.py` PASSES: `record_pick`, given the `(name, email)` tuple `read_git_config_user()` returns, writes a well-formed space-joined `by <name> <email>` pick-log line — never a Python tuple repr.
2. `tools/slice_queue_writer.record_pick` normalizes a `(name, email)` 2-sequence identity to `"name email"` and passes a plain `str` through unchanged; the str-path behavior pinned by the existing `tests/methodology/test_slice_queue_pick_log.py` is unregressed.
3. The `/slice` SKILL.md Step 6.5 documented invocation no longer passes a raw tuple — it joins the identity (e.g. `" ".join(read_git_config_user())`) — and in-repo `skills/slice/SKILL.md` is forward-synced to the installed `~/.claude/skills/slice/SKILL.md` (OSDG-1 `test_slice_skill_drift.py` clean).
4. `architecture/shippability.md` gains a row pinning the regression test (RPCD-1/SCPD-1).

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Repro passes | `pytest tests/bugs/test_record_pick_identity_tuple_repr.py` → PASS |
| 2 | Normalize + no str regression | `pytest tests/methodology/test_slice_queue_pick_log.py tests/bugs/test_record_pick_identity_tuple_repr.py` → all PASS |
| 3 | Snippet fixed + synced | Diff `skills/slice/SKILL.md` Step 6.5 shows a joined identity; `$PY -m tools.<slice_drift_audit>` / `pytest tests/methodology/test_slice_skill_drift.py` clean |
| 4 | Shippability row | `architecture/shippability.md` cites the new test; `/validate-slice` shippability runner green |

## Must-not-defer

- [ ] **No str-path regression**: the existing `test_slice_queue_pick_log.py` (which passes a pre-joined string) must stay green — the normalization must not corrupt the documented `str` contract.
- [ ] **Forward-sync the SKILL.md**: editing `skills/slice/SKILL.md` without syncing the installed copy leaves OSDG-1 drift AND leaves the installed `/slice` still emitting the repr — the fix must reach the install-time vector.
- [ ] **Non-vacuity**: the repro test is already proven failing pre-fix (this transcript); confirm it goes green only because of the fix, not a test weakening.

## Out of scope

- Changing `read_git_config_user()`'s `tuple[str, str]` return type (the claim CLI consumes the parts separately — ADR-067) — fix at the consumer/glue, not the producer.
- Reformatting existing historical pick-log lines (slice-100/101/102 are already well-formed; slice-103's was hand-corrected).
- Any change to PSQ-2 claim machinery or the `## Candidates` regeneration.

## Dependencies

- Repro test: `tests/bugs/test_record_pick_identity_tuple_repr.py::test_record_pick_with_identity_tuple_emits_well_formed_line` (established by `/repro`, confirmed FAILING).
- Vault refs: [[skills/slice/SKILL.md]] (Step 6.5 snippet), [[tools/slice_queue_writer.py]] (`record_pick`), [[tools/slice_queue_claim.py]] (`read_git_config_user`).
- Risk register: no existing R-NN; register the recurring pick-log defect at `/reflect`.

## Mid-slice smoke gate

After hardening `record_pick`, run:
```
$PY -m pytest tests/bugs/test_record_pick_identity_tuple_repr.py tests/methodology/test_slice_queue_pick_log.py --no-header -q
```
Expected: all PASS (repro green + no str-path regression). If the str-path tests break, STOP — the normalization is too aggressive.

## Pre-finish gate

- [ ] All acceptance criteria PASS with evidence in validation.md
- [ ] Must-not-defer list fully addressed (forward-sync done; no str regression)
- [ ] /drift-check passes
- [ ] No new TODOs / FIXMEs / debug prints
