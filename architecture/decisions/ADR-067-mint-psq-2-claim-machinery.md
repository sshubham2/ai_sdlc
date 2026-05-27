---
id: ADR-067
title: Mint PSQ-2 — claim machinery on the parallel-slice queue with git-identity ownership and explicit force-claim recovery
date: 2026-05-27
slice: slice-072-add-psq-2-claim-machinery
reversibility: cheap
status: accepted
supersedes: null
---

# ADR-067: Mint PSQ-2 — Parallel-Slice Queue Claim Machinery

## Context

Slice-066 (ADR-063, BRANCH-2) made parallel-slice work *physically possible* via worktree isolation. Slice-067 (ADR-064, PSQ-1) made parallel-safe candidates *discoverable* via `architecture/slice-queue.md`. But after PSQ-1 ships, two Claude sessions on the same machine reading the queue simultaneously have no way to *coordinate* — there is no per-candidate ownership marker, so both sessions can rationally pick the same top-ranked candidate and start working on it in parallel worktrees. PSQ-1's provenance line surfaces queue staleness to a human reader but does nothing to prevent collisions.

R-19 tracks exactly this gap: queue freshness is currently load-bearing for collision safety. A second session arriving more than one `/slice` invocation after the active slice was defined sees a queue computed against the wrong `active-slice-set` and may pick an `OVERLAPS-WITH-slice-NNN` candidate as if it were `NON-OVERLAPPING`.

The slice-067 reflection nominated this exact follow-up at L17 of `architecture/slice-queue.md` as `add-LOCAL-slice-queue-claim-state-machine`, on the same parallel-slice family axis as PSQ-1 (PSQ-1 ships discoverability; PSQ-2 ships coordination). The user-direction at slice-072 `/slice` was explicit: claim machinery + git config `user.name` + `user.email` as the ownership identity, surfaced in the queue's claim line.

The decision facing this slice: **what identity to record in the claim, what schema shape, how to handle stale claims, and where to place the CLI in the methodology surface**.

## Options considered

1. **Git-identity ownership + additive schema extension + standalone `tools/slice_queue_claim` CLI** (CHOSEN). Each claimed entry gains two optional field lines `**Claimed-by:** <git user.name> <git user.email>` + `**Claimed-at:** <ISO-8601 UTC>` after PSQ-1's existing `**Risk-retired:**` line. A new `tools/slice_queue_claim.py` module provides `--claim` / `--release` / `--force-claim` CLI verbs. `/slice` Step 6.5 regeneration preserves claims on surviving candidate names; claims on dropped candidates are silently discarded. Force-claim is the only stale-claim recovery path — no time-based auto-expiry. Pros: git identity is the only ambient ownership signal already universal in this codebase (every commit carries it); zero new infrastructure (no session-id daemon, no PID file, no lockfile); cooperative-not-adversarial model matches the actual threat (two trusted Claude sessions on one machine); CLI surface is separable from `tools/slice_queue_writer.py` so PSQ-1's existing tests stay scoped; schema is additive so PSQ-1's pinned format tests stay green. Cons: two sessions running as the same git user cannot distinguish themselves on a single candidate (they are *defined* as the same claimant — see Consequences §); claim file is not a security boundary (a malicious local actor can forge); force-claim has no audit trail beyond replacing the previous claim (no claim history).

2. **Session-id ownership + queue-wide claim log** — assign each Claude session a UUID at start (or detect via PID + hostname); claim entries carry the session-id; queue gains a `## Claim activity log` section accumulating claim/release/force-claim events. Pros: distinguishes co-running sessions of the same git user; provides claim history. Cons: no ambient session-id exists in Claude Code today (would have to invent one — write to `.claude/session-id` at session start, read on every claim); PID + hostname is unreliable (PIDs reused, hostnames identical across sessions on the same machine); the activity log is open-ended growth on a file PSQ-1 already keeps strict format invariants on (test pins would need substantial loosening); two sessions of the same user is not the actual collision scenario (the user explicitly chose git identity as the ownership marker at /slice).

3. **Filesystem-lock claim mechanism** — `flock`/`portalocker` on `architecture/slice-queue.md.lock` per-candidate during claim; queue stays schema-pure. Pros: ACID-like claim semantics; no schema extension on the queue itself. Cons: `fcntl.flock` is POSIX-only (Windows is the primary dev platform per project CLAUDE.md); `portalocker` is a new runtime dependency contradicting the methodology's "no new runtime deps" precedent (slice-053 BCR-1 explicitly stuck to stdlib for the same reason); claim state lives in a lockfile not the queue, so a session reading the queue cannot see who claimed what without opening a second file; loses the human-readability gain PSQ-1 delivers (developers can read the queue in any text editor).

4. **Integrate claim CLI into `/slice` itself** — `/slice --claim <name>` / `/slice --release <name>` flags rather than a standalone `tools/slice_queue_claim` module. Pros: one fewer module to register in `plugin.yaml` + INST-1 inventory; mirrors slice-067's original nomination "`/slice --claim`". Cons: `/slice` is a markdown skill with no native CLI surface — adding flags requires either growing a Python wrapper or having Claude reason about flags at runtime (LLM-prose-as-CLI is fragile per slice-009 R-2 lineage); the claim operation is mechanical, not skill-prose-shaped (no judgement calls, no question gates), so a dedicated tool fits better; separation lets PSQ-1's existing `/slice` SKILL.md prose stay focused on candidate ranking + queue write.

## Decision

Adopt **Option 1: git-identity ownership + additive schema extension + standalone `tools/slice_queue_claim` CLI**.

This decision **mints PSQ-2 (Parallel-Slice Queue Claim Machinery)** — a new RULE-ID on the parallel-slice family axis, sibling to PSQ-1 (PSQ-1 ships the queue file; PSQ-2 ships the claim semantics on that file). PSQ-2 refines NO existing rule, supersedes nothing, and is the first rule on the *claim-machinery* axis adjacent to (not extending) the *queue-output* axis (PSQ-1) and the *worktree-isolation* axis (BRANCH-2).

Concrete shape per ADR-064 §Consequences "Slice-068 MAY add new field lines per entry":

- Two optional field lines per entry — `**Claimed-by:** <user.name> <user.email>` and `**Claimed-at:** <ISO-8601 UTC>` — appended after `**Risk-retired:**` when claimed; both absent when unclaimed; partial state malformed.
- New module `tools/slice_queue_claim.py` provides the CLI (`--claim` / `--release` / `--force-claim`) and the library API (`parse_queue_text`, `apply_claim`, `apply_release`, `read_git_config_user`).
- `tools/slice_queue_writer.py::write_slice_queue` imports `parse_queue_text` to read existing claims at regen time and merge them onto items whose names survive into the new top-10.
- Stale-claim recovery is explicit (`--force-claim`); no auto-expiry by elapsed time (deferred to a future slice if needed).
- Atomic writes via `.tmp` sibling + `os.replace()` reusing PSQ-1's atomicity pattern at `tools/slice_queue_writer.py:729-731`.
- `skills/slice/SKILL.md` Step 6.5 prose gains one sentence documenting claim preservation; OSDG-1 forward-sync to `~/.claude/skills/slice/SKILL.md` required at /build-slice Phase F.

## Consequences

**Components affected**:
- `tools/slice_queue_claim.py` (NEW): registered in `plugin.yaml` tools block + `tools/install_audit._CANONICAL_TOOLS` + `INSTALL.md` tool-count literals (×2 sites per BC-PROJ-9 5-inventory fan-out — **N=9 cumulative INCLUDING slice-072** = the 8 precedent slices slice-049/050/051/057/058/059/060/063 + slice-072 itself; design.md L26 "N=8 cumulative precedent (excluding slice-072)" + this ADR's "N=9 including" are the same fan-out under different framings per Critic m5 ACCEPTED-FIXED). Per Critic B1 ACCEPTED-FIXED, `slice_queue_claim` is NOT bucketed into `tests/methodology/test_utf8_stdout_regression._ROOT_ONLY_TOOLS` (its CLI surface has no `--root` flag); instead a bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` mirrors the `test_install_audit_survives_cp1252_with_u2192` precedent at `tests/methodology/test_utf8_stdout_regression.py:121-129`.
- `tools/slice_queue_writer.py` (MODIFIED): `_format_entry` + `write_slice_queue` claim-aware behavior.
- `skills/slice/SKILL.md` (MODIFIED, OSDG-1-guarded): Step 6.5 1-sentence addition.
- `architecture/slice-queue.md` (SCHEMA EXTENDED): additive 2 optional fields per entry — PSQ-1 5-field block byte-equal modulo new lines.
- `architecture/risk-register.md` R-19 (MODIFIED): status `mitigating` → `retired` with citation; prior prose preserved verbatim (slice-040 R-10 retirement-precedent).
- `methodology-changelog.md` (NEW v0.71.0 entry) mints PSQ-2.
- `architecture/shippability.md` row #72 (NEW).
- `tests/methodology/test_psq_2_claim_machinery.py` (NEW, ~250 LOC, 10 tests).
- `tests/methodology/test_methodology_changelog.py` gains 2 paired-pin tests (`test_v_0_71_0_psq_2_entry_present_in_repo` + `test_v_0_71_0_psq_2_shippability_consumer_propagation`).
- `VERSION` / `plugin.yaml.version` / `pyproject.toml [project].version` / `methodology-changelog.md ## v0.71.0` header / installed `~/.claude/ai-sdlc-VERSION` bumped 0.70.0 → 0.71.0 (5-part PMI-1 atomic per slice-070/071 v0.70.0 canonical legs).
- Separately, post-bump TVFS-1 re-install of `ai-sdlc-tools` (`pip install --upgrade .`) + MCFS-1 forward-sync of `methodology-changelog.md` → `~/.claude/methodology-changelog.md` + OSDG-1 forward-sync of `skills/slice/SKILL.md` — NOT PMI-1 legs (per slice-063 M-add-1 leg-enumeration discipline).

**Contracts implied**:
- The queue's `Claimed-by:` value is `<user.name> <user.email>` with a single space separator. Either both name and email present at claim time (both come from git config) or claim is refused — no partial identity.
- The queue's `Claimed-at:` value is ISO-8601 UTC with `+00:00` offset suffix (e.g. `2026-05-27T14:33:31+00:00`), matching PSQ-1's provenance-line timestamp format.
- A future PSQ-3+ slice MAY add new optional field lines per entry (e.g. `**Claim-rationale:**`) without breaking PSQ-2's schema; PSQ-2's 2 fields are a minimum on the *claim block*, not a maximum.
- A future PSQ-3+ slice MUST NOT modify or remove the `Claimed-by:` / `Claimed-at:` lines PSQ-2 ships.
- `/slice` Step 6.5 regeneration preservation is a load-bearing contract: claims on surviving candidate names MUST be carried forward byte-equal; claims on dropped candidates MUST be silently discarded (no error, no warning). A regression here would resurface R-19.
- Force-claim is the ONLY stale-claim recovery path. PSQ-2 does NOT implement time-based auto-expiry. If a session abandons a claim and never releases, the next claimant must use `--force-claim`.

**Identity model implications**:
- Two Claude sessions running on the same machine as the same git user (e.g. the human runs two terminals both as their personal account) are by PSQ-2's definition the same claimant. They CAN claim distinct candidates but CANNOT distinguish themselves on a single candidate. Mitigation: if this becomes a real collision (N≥1 incident), a future slice introduces session-id overlay; not anticipated as common given the typical workflow (one human, one or two parallel slices, distinct candidates).
- Cross-machine collisions are out of scope. PSQ-2 is same-machine local-sessions only. Cross-machine coordination is PSQ-3+ territory.

**Future flexibility**:
- PSQ-3 (rebase + conflict discipline) is independent — it touches `/commit-slice`, not the queue file.
- A future PSQ-4 could add claim history (`## Claim activity log` section) without breaking PSQ-2's per-entry schema.
- A future PSQ-5 could add time-based auto-expiry by reading `Claimed-at:` + comparing to current time; the schema already carries enough information.
- If PSQ-2 is later dropped entirely, the rollback is: delete `tools/slice_queue_claim.py` + revert `_format_entry` + `write_slice_queue` claim-preservation merge + manually strip any `Claimed-by:` / `Claimed-at:` lines from the live queue (one-shot mechanical edit) + revoke PSQ-2 via a new ADR. Cheap by every axis — no schema migration, no consumer breakage beyond a yet-unshipped PSQ-3+ that depends on claim machinery (none today).

**Inclusion-heuristic posture**: this slice mints a new RULE-ID + adds new user-facing behavior + ships a new `tools/*.py` module + extends a stable on-disk contract additively. Per the slice-049/050/051/057/058/059/060/063/064/067 precedent for new-mechanism slices (N=10 cumulative), full Inclusion-heuristic firing applies: methodology-changelog entry + new ADR (this one) + 5-part PMI-1 atomic bump + new shippability row + INST-1 / BC-PROJ-9 fan-out. NOT a voluntary-restraint slice (voluntary-restraint applies to retirement-discharge / in-family-extension shapes; PSQ-2 is a new-mechanism mint).

**Lineage**: PSQ-2 is the second rule on the parallel-slice family axis (PSQ-1 minted by slice-067; PSQ-2 by this slice; PSQ-3 nominee on `/commit-slice` rebase discipline). The three layers are structurally complementary, not nested: BRANCH-2 (physical isolation) + PSQ-1 (discoverability) + PSQ-2 (coordination) + PSQ-3 (conflict resolution) collectively shape multi-session parallel work. ADR-064 explicitly nominated PSQ-2 at L37 ("claim state machine") with the schema-extension shape ADR-067 now formalizes.

**Lineage divergence note** (per Critic B2 ACCEPTED-FIXED): ADR-064 L37's nomination prose names "`session-id detection`" as part of PSQ-2's anticipated design — *"PSQ-2 (slice-068 nominee): claim state machine (`Claimed-by/-at/Force-claim` schema + `/slice --claim` + `/slice --force-claim` + session-id detection)"*. Likewise R-19's Mitigation paragraph at `architecture/risk-register.md:329` says *"Slice-068's PSQ-2 claim machinery (`Claimed-by/-at/Force-claim` schema + session-id detection) will narrow this further"*. ADR-067 §"Options considered" Option 2 explicitly rules out session-id ownership in favor of git-identity-only; §"Identity model implications" + §Decision both confirm the chosen model. The ADR-064 + R-19 predecessor prose is preserved verbatim as historical record (ADR-064 is append-only per project ADR discipline; R-19 prior prose preserved per slice-040 R-10 retirement-precedent). This is a documented predecessor-spec drift, NOT a supersession — slice-067's PSQ-1 ADR predicted an identity model PSQ-2 ultimately chose not to ship. ADR-067 §Decision is authoritative on the chosen identity model.

## Reversibility

**Cheap**. Rollback cost:
- Delete `tools/slice_queue_claim.py` (~200 LOC).
- Revert `tools/slice_queue_writer.py::_format_entry` claim-aware emission (3-line revert).
- Revert `tools/slice_queue_writer.py::write_slice_queue` claim-preservation merge (~10-line revert).
- Revert `skills/slice/SKILL.md` Step 6.5 1-sentence addition (1-line revert) + OSDG-1 forward-sync re-do.
- Mechanically strip any `Claimed-by:` / `Claimed-at:` lines from the live `architecture/slice-queue.md` (one-shot edit; the queue is regenerable on next `/slice` regardless).
- Revert `architecture/risk-register.md` R-19 status `retired` → `mitigating` and re-add slice-072 nomination as standing follow-up.
- Revoke PSQ-2 via a new ADR superseding this one.
- Revert `plugin.yaml` + `tools/install_audit.py` + `tests/methodology/test_utf8_stdout_regression.py` + `INSTALL.md` × 2 sites tool-count literals.
- Revert PMI-1 atomic bump 0.71.0 → 0.70.0.
- Delete `tests/methodology/test_psq_2_claim_machinery.py` (~250 LOC) + remove the 2 paired-pin tests from `test_methodology_changelog.py`.
- Remove shippability row #72.

Total estimated rollback: ~2 hours of mechanical work, no consumer migrations (PSQ-3 not yet shipped), no data conversions, no API surface breakage beyond the unshipped PSQ-3.

The cheap reversibility tag is **load-bearing**: PSQ-2 deliberately ships claim machinery as a *separate slice from* PSQ-3 (rebase discipline) so that if PSQ-2's claim model turns out to be wrong at PSQ-3's design time (e.g., the git-identity-only model proves insufficient at the rebase + conflict-resolution layer), we can iterate cheaply without rework on PSQ-3. PSQ-1 + PSQ-2 + PSQ-3 are deliberately three slices — not one merged slice — precisely to preserve this iteration option (per the slice-067 reflection nomination + ADR-064 §Decision lineage).
