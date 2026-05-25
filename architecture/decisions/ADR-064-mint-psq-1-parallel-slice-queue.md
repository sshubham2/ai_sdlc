---
id: ADR-064
title: Mint PSQ-1 — /slice writes architecture/slice-queue.md with top-10 parallel-safe candidates after every invocation
date: 2026-05-25
slice: slice-067-add-parallel-slice-queue-output
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-064: Mint PSQ-1 — Parallel-Slice Queue Output

## Context

Slice-066 (ADR-063, BRANCH-2) shipped worktree-per-slice discipline — every `/build-slice` runs in a filesystem-isolated worktree on a dedicated `slice/NNN-<name>` branch. This **physically enables** parallel-slice work (two Claude sessions can ship two slices concurrently without corrupting each other's working tree), but ships nothing to make parallel-safe candidates **discoverable**. A second session arriving to do parallel work has no machine-readable list of safe candidates: it would have to re-run `/slice`'s full source-fan-out (sources #1-8) from scratch, then manually cross-check each candidate's blast-radius against the active session's expected blast-radius — every time.

The slice-066 reflection explicitly nominated this as `slice-067 add-parallel-slice-queue-output`, the second of a 4-slice BRANCH-2 family (066 worktree mechanics / 067 queue output / 068 claim state machine / 069 rebase + conflict discipline). PSQ-1 (this slice's deliverable) is the discoverability layer: every `/slice` invocation writes `architecture/slice-queue.md` containing the top-10 parallel-safe candidates from Step 1's source-fan-out, each tagged with graphify-derived blast-radius + parallel-safety classification (`NON-OVERLAPPING` / `OVERLAPS-WITH-slice-NNN` / `UNKNOWN-NO-HINT-FILES` / `UNKNOWN-NO-GRAPH`) against the union of blast-radius file sets for currently-active slices.

The decision facing this slice: **how to surface parallel-safe candidates to a future second session** — a persistent on-disk file regenerated on every `/slice` invocation, an in-memory ranking surfaced only in the current session, or a more elaborate IPC mechanism.

## Options considered

1. **Persistent file regenerated on every `/slice` invocation** (CHOSEN) — `/slice` Step 6.5 (NEW) writes `architecture/slice-queue.md` with the top-10 parallel-safe candidates. Pros: zero-IPC, durable across sessions, human-readable, version-controllable (could be `.gitignore`d or committed per project preference), regenerable on demand, cleanly extensible by slice-068 (claim machinery additively adds field lines), no new dependencies, format pinned by tests. Cons: freshness window is "since last `/slice` invocation" — a stale queue could mislead a session if the active-slice set changed without a fresh `/slice` (mitigated by provenance line + slice-068's claim-machinery will narrow this further); side-output to a methodology surface (`/slice`) that previously had no side-output (mitigated by Step 6.5 prose explicitly bounding the scope + try/except wrapping so queue-write failure never blocks `/slice`'s primary deliverable).

2. **In-memory ranking only** — `/slice` Step 3's ranked list stays in-conversation; future sessions re-run `/slice` to re-compute. Pros: zero on-disk artifact = zero freshness/staleness problem; no format pin to maintain. Cons: defeats the purpose — a second session can't pick a parallel-safe candidate without a full re-discovery; doesn't unblock slice-068's claim machinery (which fundamentally needs a persistent shared file); inverts the slice-066 reflection's nomination intent ("`/slice` **writes** `architecture/slice-queue.md`").

3. **Database / SQLite for queue state** — store candidates + claims in a `architecture/slice-queue.db` SQLite file. Pros: ACID guarantees on multi-session concurrent updates; structured queries for filtering. Cons: massive over-engineering for a top-10 candidate list updated once per `/slice` invocation (typically 1-2 times per day); introduces a binary file the human user can't inspect with their text editor; introduces a runtime dependency on Python's `sqlite3` module being importable in the methodology pipeline (currently no such dependency); breaks the methodology-vault's text-only / git-friendly invariant; no precedent in the codebase for binary methodology artifacts.

4. **Distributed coordination via filesystem locks** — `/slice` writes to `architecture/slice-queue.lock` + uses `fcntl.flock` for cross-session exclusion. Pros: solves race conditions on concurrent `/slice` invocations writing to the same file. Cons: `fcntl` is POSIX-only — breaks Windows (the primary dev platform per this project's CLAUDE.md "On Windows, prefer the PowerShell tool"); cross-session-concurrent `/slice` is an extremely rare scenario (a human typically runs one `/slice` at a time even across parallel slices, since `/slice` is interactive); slice-068's claim-machinery will solve the actual coordination problem (per-candidate claim semantics) at the right layer. PSQ-1 (this slice) ships the discoverability layer; PSQ-2 (slice-068) ships the coordination layer. Don't conflate them.

## Decision

Adopt **Option 1: persistent file regenerated on every `/slice` invocation**. `/slice` Step 6.5 (NEW) writes `architecture/slice-queue.md` with the top-10 parallel-safe candidates from Step 1's source-fan-out. The file format is pinned by `tests/skills/slice/test_slice_queue_output.py` (9 unit tests per the slice's TF-1 plan); the helper module is `tools/slice_queue_writer.py` with a CLI + library API; the queue is regenerated idempotently on every `/slice` invocation (overwrite, not append); the `_Generated: <ISO-8601 timestamp>_` provenance line lets readers assess freshness manually; queue-write failure never blocks `/slice`'s primary deliverable (mission-brief + milestone) — Step 6.5 is wrapped in try/except per the skill prose.

This decision **mints PSQ-1 (Parallel-Slice Queue)**, the first of a 3-rule family that slice-067/068/069 will collectively ship:
- **PSQ-1** (this slice, slice-067): queue output mechanism.
- **PSQ-2** (slice-068 nominee): claim state machine (`Claimed-by/-at/Force-claim` schema + `/slice --claim` + `/slice --force-claim` + session-id detection).
- **PSQ-3** (slice-069 nominee): rebase + conflict discipline in `/commit-slice --merge` (rebases default before merge + structured-options ASK on conflict).

ADR-064 mints PSQ-1 only; PSQ-2 + PSQ-3 are explicitly OUT of scope and depend on this slice shipping first.

## Consequences

**Components affected**:
- `skills/slice/SKILL.md` gains Step 6.5 (PSQ-1 invocation); guarded by existing OSDG-1 (`tests/methodology/test_slice_skill_drift.py`).
- `tools/slice_queue_writer.py` (NEW) is the helper module; registered in `plugin.yaml`, `tools/install_audit.py:_CANONICAL_TOOLS`, `tests/methodology/test_utf8_stdout_regression.py:_ROOT_ONLY_TOOLS`, and `INSTALL.md`'s tool-count literals (×2 sites per slice-050 BC-PROJ-9).
- `architecture/slice-queue.md` (NEW persistent artifact) is the queue file written by `/slice` Step 6.5.
- `methodology-changelog.md` gains `## v0.69.0 — 2026-05-25` minting PSQ-1.
- `architecture/shippability.md` gains row #67 (PSQ-1 audit-rule + consumer propagation per RPCD-1 / SCPD-1).
- `VERSION` / `plugin.yaml.version` / `pyproject.toml [project].version` / `methodology-changelog.md ## v0.69.0` header / installed `~/.claude/ai-sdlc-VERSION` bumped 0.68.0 → 0.69.0 (5-part PMI-1 atomic per slice-066 v0.68.0 canonical legs at `tests/methodology/test_methodology_changelog.py:4483-4491`).
- Separately, TVFS-1 re-install of `ai-sdlc-tools` pip distribution via `pip install --upgrade .` is a BC-PROJ-9 consumer-propagation surface (NOT a PMI-1 part per slice-066 /build-slice Phase A Builder-self-catch precedent); MCFS-1 forward-sync of `methodology-changelog.md` → `~/.claude/methodology-changelog.md` is the analogous consumer-propagation surface for installed-changelog leg (NOT a PMI-1 part).
- Possibly `architecture/risk-register.md` gains R-19 (stale-queue-misleads-session, low-band, mitigated by provenance line + slice-068 claim machinery).

**Contracts implied**:
- The queue file format (5 required field lines per entry: `Source`, `Blast-radius`, `Parallel-safety`, `Effort`, `Risk-retired`) is a stable on-disk contract that slice-068 (PSQ-2) will extend additively.
  - Slice-068 MAY add new field lines per entry (PSQ-1's 5 fields are a minimum, not a maximum).
  - Slice-068 MUST NOT modify or remove the 5 fields PSQ-1 ships.
  - Slice-068 MAY add new top-of-file sections (e.g., `## Claim activity log`) without breaking the `## Candidates` section contract.
- The `Parallel-safety` enum is `NON-OVERLAPPING | OVERLAPS-WITH-slice-NNN[, slice-MMM] | UNKNOWN-NO-HINT-FILES | UNKNOWN-NO-GRAPH`. Slice-068 MAY add new enum members (e.g., `CLAIMED-BY-SESSION-XXX`) without breaking existing readers.
- Queue-write failure is non-fatal to `/slice` — Step 6.5 is wrapped in try/except per the skill prose; the primary `/slice` deliverable (mission-brief + milestone) ships regardless.

**Future flexibility**:
- Slice-068 (PSQ-2) extends the format additively (claim semantics).
- Slice-069 (PSQ-3) extends `/commit-slice` independently (rebase discipline); doesn't touch PSQ-1.
- If PSQ-1 is later dropped entirely, the rollback is: delete `tools/slice_queue_writer.py` + remove `/slice` Step 6.5 prose + delete `architecture/slice-queue.md` + revoke PSQ-1 via a new ADR. Cheap by every axis — no schema migration, no consumer breakage beyond slice-068 (which isn't shipped yet).

**Inclusion-heuristic posture**: this slice mints a new RULE-ID + adds new user-facing behavior + ships a new `tools/*.py` module + introduces a new persistent artifact with a pinned format. Per the slice-049/050/051/057/058/059/060/063 precedent for new-mechanism slices (N=8 cumulative), full Inclusion-heuristic firing applies: methodology-changelog entry + new ADR (this one) + 5-part PMI-1 atomic bump + new shippability row + INST-1 / BC-PROJ-9 fan-out. This is NOT a voluntary-restraint slice (slice-037/046/050/052/055/056/057/061/065/066 N=9 cumulative voluntary-restraint applies to retirement-discharge / in-family-extension shapes, NOT to new-mechanism mints).

**Lineage**: PSQ-1 is the first rule on the **parallel-slice family** axis, adjacent to (NOT extending) the BRANCH family (BRANCH-1 ADR-019 + BRANCH-2 ADR-063). BRANCH-2 makes parallel work *physically possible* (filesystem isolation); PSQ-1 makes it *discoverable* (queue output); PSQ-2 / PSQ-3 will make it *coordinated* (claim semantics + rebase discipline). The three layers are structurally complementary, not nested.

## Reversibility

**Cheap**. Rollback cost:
- Delete `tools/slice_queue_writer.py` (~200 LOC).
- Revert `skills/slice/SKILL.md` Step 6.5 (~25 lines of prose).
- Delete `architecture/slice-queue.md` (regenerable artifact, no consumers in production yet — slice-068's claim machinery is the first real consumer and isn't shipped).
- Revoke PSQ-1 via a new ADR superseding this one.
- Revert `plugin.yaml` + `tools/install_audit.py` + `tests/methodology/test_utf8_stdout_regression.py` + `INSTALL.md` × 2 sites tool-count literals.
- Revert PMI-1 atomic bump (well-trodden 5-part bump per slice-059 TVFS-1 + slice-063 NAW-1 precedent).
- Delete `tests/skills/slice/test_slice_queue_output.py` (~250-300 LOC of test code with fixtures).

Total estimated rollback: ~2 hours of mechanical work, no consumer migrations, no data conversions, no API surface breakage beyond the unshipped slice-068. The queue file format itself is pinned by tests; slice-068's contract with that format is a forward-only commitment that gets renegotiated if PSQ-1 is dropped.

The cheap reversibility tag is **load-bearing**: this slice deliberately ships PSQ-1 BEFORE PSQ-2 (claim machinery) so that if PSQ-1's format turns out to be wrong at slice-068 design time, we can iterate cheaply. PSQ-1 + PSQ-2 are NOT being merged into one slice precisely to preserve this iteration option (per the slice-066 reflection nomination + this slice's mission-brief Out-of-scope §).
