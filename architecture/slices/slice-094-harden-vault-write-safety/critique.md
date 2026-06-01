# Critique: Slice 094 harden-vault-write-safety (v2 — flip-readiness redesign)

**Critic reviewed**: mission-brief.md, design.md, ADR-086 (revised in place), + real worktree code
**Date**: 2026-06-01
**Result**: NEEDS-FIXES (Critic-stated; final verdict computed at TRI-1 after dispositions + `/critique-review`)

> **v2 critique** — supersedes the v1 BLOCKED critique (preserved in git at `c0130ad`; v1 TRI-1 = BLOCKED, all 10 dispositions ratified, recorded in milestone.md). This reviews the flip-readiness redesign. The Critic EXECUTED the byte primitives + concurrency mutations against real bytes in the worktree.

## Summary

The B1 byte-fix is empirically correct (Critic reproduced both the CRLF bug and the LF fix), the PCR scope-out is honest, and the count fan-out reconciles. But the **AC4 concurrency proof is built on two assertions proved vacuous by execution** (whole-file "torn write" can't fail — `os.replace` is atomic; append line-loss won't reliably fail — `O_APPEND` is OS-atomic for a single `os.write`), and the routed RMW callers retain a lost-update window the lock does not cover. Separately, the **MEPD-1 INCLUDE version-bump obligation is materially under-specified** (omits `pyproject.toml`/PVFS-1, entry-pin tests, PMI-1 gate supersession). 2 Blockers, 2 Majors, 6 Minors.

## Findings

### Blockers (must address before /build-slice)

#### B1: AC4 concurrency proof is vacuous as specified — the mutation cannot make either assertion FAIL
- **Claim under review**: design.md / mission-brief AC4 — N `safe_write_text` → "exactly one writer's complete payload (never torn)"; N `safe_append_text` → "lose zero lines… non-vacuity proven by mutation (disable lock → FAILs)".
- **Issue**: Critic executed both mutation variants under `multiprocessing(spawn)`: (a) **whole-file** with lock DISABLED but temp+`os.replace` retained → final file always exactly one payload (`os.replace` is OS-atomic) → "torn write" passes lock-or-not → vacuous; (b) **append** with lock DISABLED → raw single-`os.write` `O_APPEND` lost 0 lines in 7/8 runs → append-loss flakily passes even unlocked → not reliably non-vacuous. The pattern that DOES lose updates (9/10) is **read-modify-write**, requiring a cross-process wall-clock barrier (spawn latency serializes workers otherwise).
- **Evidence**: executed probes — raw whole-file/spawn `final in payloads: True`; raw append/spawn `loss=0`; RMW+shared-start-barrier `LOST=9/10`. Web-confirmed: `os.replace` atomic ([bugs.python.org#46003]); `O_APPEND` single-write atomic ([bugs.python.org#15723]).
- **Proposed fix**: Re-scope AC4 to prove what the lock ACTUALLY protects, non-vacuously: (a) **EPERM-on-concurrent-replace** — raw `os.replace` under contention raises `PermissionError WinError 5`; prove `safe_write_text`'s lock+retry absorbs it and the raw/un-retried variant raises; (b) **RMW lost-update** via a cross-process barrier (only if an RMW-spanning helper is added — see B2); (c) document the mutation FAIL output in build-log.md. If keeping the append/whole-file framing, state they are correctness-under-contention demonstrations, NOT non-vacuity proofs, and move "proven by mutation" to the EPERM/RMW variant.
- **Builder draft**: **ACCEPTED-FIXED** — the Critic executed it; the proof IS vacuous as specified. Fix at redesign (post-TRI-1): rewrite AC4 + design §Concurrency-proof to prove the lock+retry's real protections non-vacuously — **EPERM-under-concurrent-`os.replace`** (raw variant raises WinError 5 → FAIL; `safe_write_text` absorbs) as the primary mutation, plus a **>1024-byte Windows append-interleaving** check if reproducible; drop the atomic-`os.replace` "torn-write" + small-payload append-loss assertions as vacuous. The RMW lost-update moves to B2's documented flip-residual (NOT proven here, since we are NOT adding an RMW helper). **NB (Builder must re-verify at build)**: reconcile with slice-093's "pure `O_APPEND` loses 26/30 lines" — likely a different mechanism (text-mode / multi-write / RMW); re-run before asserting.

#### B2: Routing the seam writers through `safe_write_text` does NOT close their lost-update window — the lock spans the write, not the caller's read
- **Claim under review**: design.md Intent — routing "closes the read-modify-write lost-update window"; ADR-086 — routing makes the writers safe.
- **Issue**: Both routed callers are read-modify-write: `slice_queue_claim.py:592` reads → `:599/:607/:613` writes; `slice_queue_writer.py:732` reads `existing_text` → `:819` writes. `safe_write_text` holds the sidecar lock ONLY for the write (`_vault_write.py:102`), releasing before return — NOT across the caller's earlier `read_text`. Two concurrent claims both read old, both compute, second clobbers first → lost update (Critic reproduced 9/10). Routing makes the write atomic+LF-faithful but does NOT close the RMW window R-32 describes for these exact callers.
- **Evidence**: `slice_queue_claim.py:592→599`, `slice_queue_writer.py:732→819`, `_vault_write.py:95-119` (lock scope = write only).
- **Proposed fix**: (a) State in design + AC2 that routing delivers byte-faithful + atomic-write + EPERM-resilience but does NOT close the RMW window (a flip-residual, git-protected today) — the honest flip-readiness framing, consistent with B3; OR (b) add a `_file_lock`-spanning RMW helper (lock → read → mutate → write → release) and route the 2 callers through it. Given flip-readiness scope + git-tracked targets, (a) is right — but the current Intent/AC2 over-claims the window is closed and must be corrected.
- **Builder draft**: **ACCEPTED-FIXED** — take option (a). The targets are git-tracked today (B3); the RMW window is a documented flip-residual, not this slice's job. Fix at redesign: correct design.md Intent + AC2 + the §primitive/§R-32 prose to claim only byte-faithful + atomic-write + EPERM-resilience + the enforcement audit; explicitly list the RMW window as a flip-residual alongside PCR. Do NOT add the RMW helper (scope creep; the lock-across-read design is the flip's call).

### Majors (address this slice / the redesign)

#### M1: MEPD-1 INCLUDE version-bump fan-out is under-specified — omits pyproject.toml/PVFS-1, entry-pin tests, and the PMI-1 gate supersession
- **Claim under review**: design.md §M2 + mission-brief MND "atomic … PMI-1 bump"; ADR-086 Consequences.
- **Issue**: The live PMI-1 versioned gate `test_version_files_synchronized_at_v_0_78_0` (`tests/methodology/test_methodology_changelog.py:5496`) enforces a **5-part** bump whose leg 3 is **`pyproject.toml [project].version` (PVFS-1)** — the slice's M2 table/MND omit `pyproject`/PVFS entirely and call it "4-part". Further, a new RULE-ID at a new version requires a NEW `test_v_<ver>_vws_1_entry_present_in_repo` + `_shippability_consumer_propagation` entry-pin PAIR, AND superseding the version gate `_at_v_0_78_0` → `_at_v_<new>` while PRESERVING all prior entry-pins (EPGD-1 structural separation). None of this test-side work is in any artifact.
- **Evidence**: `test_methodology_changelog.py:5496-5513` (5-part incl pyproject), `:505/:551` (PMI-1 shape meta-tests), `pyproject.toml [project].version`.
- **Proposed fix**: Add to design M2: (1) `pyproject.toml`/PVFS-1 → it is a **5-part** bump; (2) a new entry-pin pair; (3) supersede the version gate preserving prior pins; enumerate the META-1 `Rule reference` literal + changelog-anchor substrings the entry-pin asserts.
- **Builder draft**: **ACCEPTED-FIXED** — real under-spec; the worktree's PMI-1 gate is 5-part. Fix design §M2 + MND to enumerate `pyproject.toml`/PVFS-1 (5-part) + the entry-pin + gate-supersession (EPGD-1) test obligations. **CRITICAL INTEGRATION NOTE (R-33)**: this worktree is BEHIND master (slices 095/096 merged there, NOT here). slice-095 already took **v0.79.0** (SVW-1). So 094 must bump to **v0.80.0** (not 0.79.0), its entry-pin/gate-supersession must target the POST-095 changelog state, and per R-33 (slice-092/095 lesson) `/commit-slice` must `git merge master` FIRST — the version, the 5-part gate (095 may have advanced it), and the cp1252 list reconcile against master, not the worktree's stale 0.78.0. The Critic's project-frame was worktree-stale (computed 0.78.0); the real target is post-095.

#### M2: ADR-086 "catches PCR" contradicts its own Option-1 undecidability rejection — all 7 PCR write targets are variables
- **Claim under review**: ADR-086 Option-4 pros — "catches PCR (it has vault-literal write targets)"; design §detection-model.
- **Issue**: None of PCR's 7 write ops has a vault literal AT the write-target node: `:430` `out_path.write_text` (loop var from `pending_writes`, built by calls — undecidable); `:1546` `out_path` = `repo_root/"architecture"/"slice-queue.md"` (literal 1 hop back); `:713/:764/:1779/:2133/:2234` `log_path` = `repo_root/_AUDIT_LOG_PATH` where `_AUDIT_LOG_PATH = Path("architecture/...")` is a module constant (literal 1 hop + const resolution). PCR imports no seam, so rule (b) never fires. "Catches PCR" is only true if the audit backtracks Name-assignments + module constants — the exact dataflow ADR Option-1 rejects as undecidable. design §detection doesn't specify the resolution depth; the "accepted residual = fully opaque runtime path" cons doesn't cover the `var = root/"architecture"/"x.md"; var.write_text()` shape all 4 real writers use.
- **Evidence**: `parallel_conflict_resolver.py:71` (`_AUDIT_LOG_PATH` const), `:1544` (`out_path` assign), `:362-368` (`pending_writes`); ADR-086 Option-1 (undecidable) vs Option-4 ("catches PCR").
- **Proposed fix**: Specify the exact target-resolution depth (e.g. resolve a `Name` target through ≤1 intra-function assignment AND module-level `Path(...)`/str constants; NO interprocedural/container resolution). State which PCR ops that depth catches (5 `log_path` + `:1546`; NOT `:430` loop var = accepted residual) and correct the ADR "catches PCR" → "catches the 1-hop-literal shape the seam writers + 6/7 PCR ops use". APED-1 battery MUST plant the `var = root/"architecture"/"x.md"; var.write_text()` shape as a VIOLATION.
- **Builder draft**: **ACCEPTED-FIXED** — the v2 design hand-waved the resolution depth and the ADR over-claimed. Fix design §detection-model + ADR-086 to commit to **≤1-hop intra-function Name-assignment + module-level `Path(...)`/str-constant resolution** (tractable, bounded — NOT the rejected interprocedural dataflow); correct "catches PCR" to the precise 1-hop-literal-shape claim; add the planted `var = root/"architecture"/"x.md"` VIOLATION to the APED-1 battery. This also sharpens the future-writer guarantee (the seam writers use exactly this shape).

### Minors (log; address if cheap)

#### m1: design.md mislocates the changelog — `architecture/methodology-changelog.md` doesn't exist (it's at repo root)
- **Issue**: design §M2 cites `architecture/methodology-changelog.md`; the file is repo-root `methodology-changelog.md` (ADR-086 cites it correctly). FBCD-1 cross-file drift that could misdirect MCFS-1.
- **Builder draft**: **ACCEPTED-FIXED** — change design §M2 to `methodology-changelog.md` (repo root) + note the installed forward-sync target `~/.claude/methodology-changelog.md`.

#### m2: design.md "4 read-only VAULT_ROOT-importers" is factually wrong — 3 of the 4 named don't import VAULT_ROOT
- **Issue**: Only `shippability_decoupling_audit` references VAULT_ROOT of the 4 named; the real seam-referencing set is 11. Conclusion still holds (only 4 `tools/*.py` have ANY write op), but the enumeration is a CCC-1 parity error.
- **Builder draft**: **ACCEPTED-FIXED** — reword to "every module with no write op never reaches classification (only 4 `tools/*.py` contain a write op at all)"; drop the wrong 4-name list.

#### m3: "zero production callers today" is imprecise — `write_vault_root_config` calls `safe_write_text`
- **Issue**: `_vault_write.py:155-162` `write_vault_root_config` is a production wrapper (`:161` calls `safe_write_text`, test-exercised slice-093); pre-fix it wrote `path\r\n` (latent — `read_vault_root_config:174` `.strip()`s it).
- **Builder draft**: **ACCEPTED-FIXED** — reword design §primitive to "the only production caller is in-module `write_vault_root_config` (config writes are `.strip()`-read so the CRLF was latent); the byte-fix also corrects that latent CRLF; the test is first-use validation for the seam writers".

#### m4: BC-PROJ-12 (markdown-writer `newline=""` build-check) interaction with the routing is unanalyzed
- **Issue**: BC-PROJ-12 (`test_build_checks_audit.py:1672-1723`, advisory, `applies_to tools/**/*.py`, anchors `write_text`/`open("a")`/`.md`/`encoding`) fires on changed `tools/*.py` hunks demanding `newline=""` or a deferral. Routing REMOVES `newline=""` from the call sites (moves into `_vault_write.py`); the slice edits `_vault_write.py`'s EOL lines directly. Design never mentions BC-PROJ-12. Likely advisory (negative_anchors include `design.md`), not a hard fail.
- **Builder draft**: **ACCEPTED-FIXED** — add design note: routed sites delegate `newline=""` to `safe_write_text` (now sets it, B1); BC-PROJ-12 advisories on these hunks are satisfied by the primitive or deferred-with-rationale citing it. Run BC-1 on the routed diff at mid-slice smoke (build-time).

#### m5: `_CANONICAL_TOOLS` alphabetical insert point in design.md is slightly off
- **Issue**: `vault_write_safety_audit` sorts after `validate_slice_layers` (`install_audit.py:126`), before `walking_skeleton_audit` (`:127`) — not near `supersede_audit`/`test_first_audit` (`:122/:123`).
- **Builder draft**: **ACCEPTED-FIXED** — correct design §M2 to insert between `:126 tools.validate_slice_layers` and `:127 tools.walking_skeleton_audit`.

#### m6: `*.tmp` gitignore glob is repo-wide
- **Issue**: M4's `*.tmp` (over the non-matching `*.<pid>.tmp`) is right, but `*.tmp` is repo-wide. Likely intended; flag only.
- **Builder draft**: **ACCEPTED** — confirmed repo-wide `*.tmp` + `*.lock` is the simplest correct choice (temp files are `<name>.<pid>.tmp` / `<name>.tmp`; locks are `<name>.lock`); no production `.tmp`/`.lock` is git-tracked. No change needed; note the confirmation in build-log.

## Dimensions checked
- [x] **Unfounded assumptions** — M2 (ADR "catches PCR" not backed by write-target code), m2 (false "4 importers"), m3 ("zero callers" false). B1 byte-fix assumptions verified TRUE by execution (CRLF reproduced; `newline=""`+`O_BINARY`→LF; `O_APPEND` preserved; multibyte/existing-file OK).
- [x] **Missing edge cases** — B1/B2 (proof tests the wrong patterns; RMW window unhandled; EPERM-under-contention/WinError 5 not in the proof).
- [x] **Over-engineering** — none. Scope appropriately narrow; PCR correctly scoped out; COUNT-pinned allowlist reuses precedent.
- [x] **Under-engineering** — M1 (MEPD-1 INCLUDE bump under-specifies pyproject/PVFS + entry-pin + gate-supersession; would fail strict PMI-1/changelog audits at pre-finish).
- [x] **Contract gaps** — none new. Audit CLI 0/1/2 follows RR-1/SRSC-1/BCI-1; `_vault_write` byte-output contract change correctly called out (M4 in design).
- [x] **Security** — none. Data-integrity control per ADR-067; cooperative-writer frame correct; no authz/secret/injection surface.
- [x] **Drift from vault** — m1 (changelog path), m2 (importer enumeration), M2 (ADR self-contradiction). Strategic-direction fit (Dim-7a): flip-readiness + "R-32 retires at the flip" is CONSISTENT with the external-vault-flip trajectory + no-flip invariant — does not fight direction. Architectural-concurrency (Dim-7b): closed-world `tools/` scan, not a runtime detector — N-concurrent-worktree cry-wolf class N/A.
- [x] **Web-known issues** — confirmed `os.replace` atomic + WinError 5 under held handle ([bugs.python.org#46003], [briefcase#1780]) — supports B1's EPERM rationale AND the torn-write vacuity; `O_APPEND` single-write atomic with a Windows 1024-byte split caveat ([notthewizard.com], [bugs.python.org#15723]) — supports the append-loss vacuity. No deprecations affecting `msvcrt.locking`/`os.open`/`multiprocessing(spawn)`.
- [x] **Cross-cutting conformance** — M1 (MEPD-1/EPGD-1/SCPD-1 + pyproject), M2 (resolution-depth vs ADR undecidability), m4 (BC-PROJ-12 pre-existing branch composing with the routing diff). APED-1: Critic EXECUTED the byte primitives + concurrency mutations against real bytes (Builder should RE-RUN, not trust the summary — "re-interrogate the Critic's own claims" lesson). The audit doesn't exist yet → its APED-1 battery runs at build; M2 specifies the planted-VIOLATION shape.

## Triage

**Triaged by**: user (contact@sshubham.me) — TRI-1, reconciling both Critic passes (`/critique` + `/critique-review` EXTEND)
**Date**: 2026-06-01
**Final verdict**: NEEDS-FIXES

_Verdict basis_: ACCEPTED-PENDING present (B1, M1, M-add-1, m-add-1) → built during `/build-slice`; ACCEPTED-FIXED items applied at the post-TRI-1 redesign touch-up; no ESCALATED → not BLOCKED.

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | ACCEPTED-PENDING | Re-scope AC4: **EPERM-on-`os.replace`** mutation (whole-file) + **MANDATORY >1024-byte append-interleaving** proof (meta-Critic: small-payload append-loss vacuous, >1024B non-vacuous per Windows OS-split); drop torn-write/small-append; non-vacuous proof EXECUTED at build. |
| B2 | Blocker | ACCEPTED-FIXED | Corrected Intent/AC2/ADR-086: routing buys byte-faithful + atomic-write + EPERM-resilience, NOT RMW-window closure (documented flip-residual); no RMW helper. |
| M1 | Major | ACCEPTED-PENDING | **5-part** bump incl. `pyproject.toml`/PVFS-1 + entry-pin pair + version-gate supersession (EPGD-1); lands at build. |
| M2 | Major | ACCEPTED-FIXED | ADR-086 + design committed to **≤1-hop Name + module-const** resolution depth; "catches PCR" corrected to the 1-hop-literal-shape claim; APED-1 plants the `var = root/"architecture"/"x.md"` VIOLATION. |
| m1 | Minor | ACCEPTED-FIXED | changelog path → repo root (not `architecture/`). |
| m2 | Minor | ACCEPTED-FIXED | reworded the false "4 VAULT_ROOT-importers" enumeration. |
| m3 | Minor | ACCEPTED-FIXED | reworded "zero production callers" (`write_vault_root_config` calls it). |
| m4 | Minor | ACCEPTED-FIXED | design note: routed sites delegate `newline=""` to the primitive; BC-PROJ-12 satisfied/deferred. |
| m5 | Minor | ACCEPTED-FIXED | `_CANONICAL_TOOLS` insert between `validate_slice_layers`/`walking_skeleton_audit`. |
| m6 | Minor | OVERRIDDEN | Flag-only finding; repo-wide `*.tmp`/`*.lock` is the simplest correct choice (no tracked `.tmp`/`.lock`) — confirmed intended, no change. |
| M-add-1 | Major | ACCEPTED-PENDING | (meta-Critic missed) **v0.79.0 taken by merged slice-095** → 094 targets **v0.80.0**; add `git merge master` to the Pre-finish gate (R-33); entry-pins reconcile against post-095 state. |
| m-add-1 | Minor | ACCEPTED-PENDING | (meta-Critic) byte-identity test: add a large (>1024B) multibyte payload, not just `a\nb\n`. |
| m-add-2 | Minor | ACCEPTED-FIXED | (meta-Critic) shippability row #102 must carve out the PCR scoped-out allowlist (honest coverage, not "total"). |
