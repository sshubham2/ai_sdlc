# Code Review: Slice 092 fix-stranded-audit-branchless-blindspot

**code-Critic reviewed**: slice diff vs default branch (`19d7d6a`), filtered to in-scope paths
**Date**: 2026-05-31
**Result**: FINDINGS (minor only — no blockers, no majors)
**Reviewer**: `code-review` subagent (real adversarial agent; 21 tool uses, 78.9k tokens, 214s — verified the B2 dedup empirically + reproduced the 4n scenario)

## Summary

The slice cleanly closes R-31 with the smallest possible surface: one enum member, one subordinate enumeration pass, one helper. The load-bearing B2 dedup-key construction (`b[len("slice/"):]` over `worktree_branches`, which genuinely holds full `slice/NNN-name` refs) is **correct against the real `WorktreeInfo` shape** — the agent verified empirically that the `wt.slice_name`-alone mis-key would have double-reported and that test 4n catches it non-vacuously (the bare-branch path contributes zero for the 240 key when invoked from the worktree, so the suppression provably comes from the worktree-key path). The never-halt invariant holds (`BRANCHLESS_IN_FLIGHT ∉ _HALT_CLASSES`, `compute_status` unchanged), the folder pass is strictly additive and runs last so it cannot mask a branch-derived halt, and the fail-open / terminal / stage-None edges are all pinned. Code matches design.md §Dedup design, §Self-surfacing, and §Error model. Findings are two cosmetic minors.

## Changed files (in-scope)
- tools/stranded_slice_audit.py
- tests/methodology/test_stranded_slice_audit.py
- tests/methodology/test_pulse_skill_stranded_signal.py
- tests/bugs/test_stranded_audit_branchless_slice_blindspot.py
- skills/pulse/SKILL.md
- skills/slice/SKILL.md
- architecture/slices/slice-092-fix-stranded-audit-branchless-blindspot/build-log.md (post-build artifact, not reviewed as code)

## Findings

### Blockers (advisory in v1)

None.

The two highest-risk vectors flagged for special attention both check out clean:
- **B2 dedup-key trap**: `tools/stranded_slice_audit.py` `{b[len("slice/"):] for b in worktree_branches}` is correct. `worktree_branches` is populated from `wt.branch`, and `pulse_worktree_resolver.py:319` sets `branch = branch_ref[len("refs/heads/"):]` → full `slice/NNN-name`, so slicing the 6-char `slice/` prefix yields the `NNN-name` key. Agent reproduced the 4n scenario directly: from inside the worktree, `worktree_branches = {'slice/240-selfwt'}` → key `240-selfwt` (matches folder); the mis-key `wt.slice_name` → `selfwt` (does NOT match) → would surface a spurious BRANCHLESS. Test 4n is genuinely non-vacuous, and `bare_tuples == []` for that key confirms the suppression is exercised via the worktree path, not the bare path.
- **Precedence / masking**: `entries.extend(_branchless_in_flight_slices(...))` runs strictly AFTER both branch passes and only appends; the helper emits only for keys absent from `seen_keys`. It can never downgrade or mask a halt-worthy branch entry. Matches ADR-084 §Decision "Precedence subordination (M2)".

### Majors

None.

### Minors

#### m1: `_index.md`-skip is exercised by 4m but its mechanism is non-obvious — a one-word comment would prevent a future regression
- **Claim under review**: `if not child.is_dir() or child.name == "archive": continue  # files (e.g. _index.md) and the archive/ tree are not in-flight`
- **Issue**: The comment is accurate, but design.md test-plan 4m and the test docstring single out `_index.md` as a "stray file" that must be skipped. The skip works because `_index.md` is a file and fails `child.is_dir()` — NOT because of any name match. Correct, but if a future edit ever moves to name-regex-first ordering, the `_index.md` guarantee silently depends on the `is_dir()` short-circuit remaining first. The `_index.md`-specific guarantee in the test has no dedicated code element — it rides on the generic file filter.
- **Evidence**: test asserts `_index.md` skipped (4m); code delivers it only via `not child.is_dir()`. No defect today — purely a latent-coupling note.
- **Proposed fix**: None required (advisory). If touched later, keep the `is_dir()` check first; test 4m will catch a regression loudly.
- **Builder disposition**: ACCEPTED-NO-CHANGE. The existing comment already names `_index.md`; test 4m loudly guards the behavior. Adding nothing rather than over-annotate.

#### m2: folder-form `\d{3}` strictness is correct-by-symmetry but undocumented as an intentional dedup-safety property
- **Claim under review**: `_SLICE_FOLDER_RE = re.compile(r"^slice-(\d{3})-(.+)$")`
- **Issue**: The `\d{3}` (exactly-3-digit) constraint means a hypothetical `slice-1000-x` / `slice-92-x` folder is skipped. This is the *correct* behavior precisely because it mirrors `_SLICE_BRANCH_RE` (`^slice/(\d{3})-(.+)$`) — if the folder regex were laxer than the branch regex, a folder could match where its branch ref could not be keyed, opening an asymmetric dedup hole. The B2 comment explains the prefix-strip hazard thoroughly but did not state that the digit-count symmetry with `_SLICE_BRANCH_RE` is itself a load-bearing dedup-correctness property.
- **Evidence**: both `_SLICE_BRANCH_RE` and `_SLICE_FOLDER_RE` use `\d{3}` — both reject 2/4-digit identically, so no asymmetry exists.
- **Proposed fix**: one-line comment addition stating the digit-count must stay symmetric with `_SLICE_BRANCH_RE`.
- **Builder disposition**: ACCEPTED-APPLIED. Added the symmetry comment to the `_SLICE_FOLDER_RE` block (`# The \d{3} digit-count MUST stay symmetric with _SLICE_BRANCH_RE or the folder/branch dedup keys diverge … code-review m2`). Comment-only; no behavior/test change.

## Dimensions checked
- [x] Unfounded assumptions — none. Docstrings match implementation; B2 key-source claim verified against `pulse_worktree_resolver.py:319/341`; all reused symbols (`_frontmatter_field`, `_is_terminal`, `_entry`, `_bare_slice_branches`, `DivergenceClass`, `WorktreeInfo.branch/.slice_name`) exist as cited.
- [x] Missing edge cases — none material. Empty/missing `architecture/slices` dir, absent milestone, unreadable/`UnicodeDecodeError`, stage-None (4o), terminal (4l), non-conforming dir, file-vs-dir, archive exclusion all covered. Read-only/advisory → no concurrency race.
- [x] Over-engineering — none. No speculative generality; helper takes exactly the params it uses; enum member consumed by `_entry`/`compute_status`/`_entry_to_dict`.
- [x] Under-engineering — none. Every AC has a delivering code element (AC1 emit path, AC2 dedup, AC3 never-halt, AC4 regression guards + 16-test module green). PMI-1 / OSDG-1 drift / MEPD-1 EXCLUDE all discharged.
- [x] Contract gaps — none. New helper fully type-hinted + docstring'd; JSON `klass` gains `"branchless-in-flight"` (backward-additive); entry carries `halt=false`, `worktree_path=null`, `ahead=null`, `branch`=folder-form `slice-NNN-name`, `vault_state="folder:<stage>"` per ADR-084 §Contracts.
- [x] Security — none. Read-only git/filesystem inspection; no new input boundary, no `shell=True`, no injection/secrets/authz surface. Inherits ADR-079 local-cooperative-trust (design §Authorization model N/A). Folder name flows into display f-strings only, never a subprocess.
- [x] Drift from vault — none. Code matches design.md §Dedup design (seen_keys construction verbatim), §Self-surfacing (no "exclude invoking slice" filter added — correctly omitted), §Error model (stage-None skipped, never `folder:None`; fail-open; no new exit codes), ADR-084 §Decision (hyphen folder-form id, subordinate precedence). `/pulse` adds the real M1 render path; `/slice` adds the doc-only enumeration.
- [x] Web-known issues — one informational, non-blocking: `Path.is_dir()` follows symlinks by default (`follow_symlinks=False` only added Python 3.13). A symlinked `slice-NNN-*` dir would be scanned. NOT a finding: matches the tool's existing non-symlink-aware posture, single-level (no recursive traversal amplification), inside the design's local-cooperative-trust boundary.
- [x] Cross-cutting conformance — none. RSAD-1: the slice's own folder dedupes itself via its `slice/092` worktree branch (context-2, verified live). APED-1: folder regex executed against the adversarial battery (2/4-digit reject, `slice-bad`, `_index.md`, `archive/`, stray dirs) via test 4m + agent probe. Algorithm-path: new pass composes additively and last; `_bare_slice_branches` already filters `worktree_branches` so no double-counting between ref sources.

## References
- [pathlib — Object-oriented filesystem paths](https://docs.python.org/3/library/pathlib.html)
- [Support for not following symlinks in pathlib.Path.is_dir() (cpython#105793)](https://github.com/python/cpython/issues/105793)
