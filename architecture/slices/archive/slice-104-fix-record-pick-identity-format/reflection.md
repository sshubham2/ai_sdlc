# Reflection: slice-104-fix-record-pick-identity-format

**Closes:** (none — newly-surfaced defect; registers R-34)
**Shipped:** 2026-06-02
**Ceremony:** streamlined (owner-waived Critic; see milestone `critic-waiver`)

## Validated

- `record_pick` tuple-normalization makes the documented `/slice` Step 6.5 invocation correct regardless of whether the caller joins — defense in depth (consumer hardening + snippet fix) both landed, 1398-test suite green.

## Corrected

- The `record_pick` docstring claimed `picker_identity` "is the caller-supplied `"<name> <email>"` string … obtained via `read_git_config_user`" — but `read_git_config_user` returns a `tuple[str, str]`, so the implied contract was internally inconsistent. Reconciled: the function now accepts both shapes and the docstring states it.

## Discovered

- The bug was a **prose-snippet defect** (the documented Step 6.5 invocation), not a defect in either function in isolation — `record_pick(str)` and `read_git_config_user()->tuple` were each locally correct; the glue passed the wrong type. A prose snippet can't be unit-tested, so the durable fix had to move the guarantee into testable CODE (harden the consumer). This is the lesson below.
- It recurred silently across multiple picks (owner observed it before; slice-103's pick reproduced it). The well-formed historical lines (slice-100/101/102) were almost certainly hand-corrected at pick time, masking the recurrence in the committed log.

## Deferred

- None.

## Lesson for next slice

- **When a documented code snippet glues two functions with mismatched types, pin the guarantee in the CONSUMER, not the prose.** A `/slice` SKILL.md snippet passing `read_git_config_user()` (a tuple) into `record_pick(picker_identity: str)` emitted a Python tuple repr into the pick-log and recurred every pick because prose carries no test. Fixing only the snippet would leave the next caller exposed; hardening `record_pick` to normalize the `(name, email)` shape its real caller supplies makes the malformed line structurally impossible AND is testable. Promotion verdict: **build-check / critic-calibrate probe** — "does any documented skill snippet pass a value whose type the called function's signature doesn't accept?"

## Critic calibration

- N/A — Critic waived (owner-approved streamlined). Noted as a `/critic-calibrate` data point: a real, recurring methodology-surface defect shipped without Critic; the pre-pinned failing repro test + full-suite regression substituted for adversarial review on a fix this mechanical.

## Risk register

- Registers **R-34** (retired by this slice): `/slice` pick-provenance writer serialized a Python tuple repr into `## Pick log` (documented Step 6.5 snippet passed `read_git_config_user()`'s tuple into `record_pick(str)`). Retired — `record_pick` normalizes the tuple + snippet joins + regression test pinned (shippability #110).
