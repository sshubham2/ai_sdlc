# Design: Slice 072 add-psq-2-claim-machinery

**Date**: 2026-05-27
**Mode**: Standard

## What's new

- `tools/slice_queue_claim.py` (NEW module) — CLI + library API for claim / release / force-claim operations on `architecture/slice-queue.md`. Holds the schema parser (`parse_queue_text`), git-config reader (`read_git_config_user`), and text-mutation helpers (`apply_claim`, `apply_release`).
- Additive schema extension on `architecture/slice-queue.md`: each candidate entry MAY carry two new optional field lines (`**Claimed-by:** <user.name> <user.email>` + `**Claimed-at:** <ISO-8601 UTC>`) after `**Risk-retired:**`. PSQ-1's 5 fixed fields (`Source` / `Blast-radius` / `Parallel-safety` / `Effort` / `Risk-retired`) preserved in order — unchanged.
- Modifications to `tools/slice_queue_writer.py`:
  - `_format_entry` (existing at `tools/slice_queue_writer.py:622`) gains optional emission of the two claim lines when item dict has `claimed_by` + `claimed_at` keys.
  - `write_slice_queue` (existing at `tools/slice_queue_writer.py:648`) reads any existing queue file via the new `tools/slice_queue_claim.parse_queue_text` helper, then merges claims onto items where the candidate name survives into the new top-10. Claims on dropped candidates are silently discarded; new candidates start unclaimed.
- `skills/slice/SKILL.md` Step 6.5 prose gains one line documenting claim preservation across regeneration (OSDG-1-guarded — forward-sync to `~/.claude/skills/slice/SKILL.md` required).
- ADR-067 minting **PSQ-2** as a new rule (sibling on parallel-slice family axis; supersedes nothing; first rule on the claim-machinery axis).
- `methodology-changelog.md` `## v0.71.0 — 2026-05-27` entry + 5-part PMI-1 atomic bump 0.70.0 → 0.71.0.
- `architecture/risk-register.md` R-19 status flipped `mitigating` → `retired` with citation.
- `architecture/shippability.md` row #72 (BC-PROJ-10 paired-pin discipline + RPCD-1 / SCPD-1 consumer-reference propagation).
- New test module `tests/methodology/test_psq_2_claim_machinery.py` (~330 LOC, 15 unit tests across AC1-AC4 behavioral surfaces — including AC1's CRLF-tolerance + forward-compat pass-through + AC2's configured-empty git-config + `--queue` override + AC3's release-on-unknown disambiguation, all added post-Critic fix-block per M1/M2/M3/m2/m3/M4 ACCEPTED-FIXED).
- 1 bespoke cp1252 regression test added to `tests/methodology/test_utf8_stdout_regression.py` (`test_slice_queue_claim_survives_cp1252_with_u2192` mirroring the `test_install_audit_survives_cp1252_with_u2192` precedent at L121-129; AC2; per Critic B1 ACCEPTED-FIXED).
- 2 paired-entry-pin tests in `tests/methodology/test_methodology_changelog.py` (AC6 per the AC5→AC6 split documented at mission-brief L23; per Critic M4 ACCEPTED-FIXED).

## What's reused

- PSQ-1 atomicity contract: `.tmp` sibling + `os.replace()` (per `tools/slice_queue_writer.py:729-731`) — claim writes follow the same idempotent overwrite shape.
- PSQ-1 schema constants module (`tools/slice_queue_writer.py:108-110`) `_FLAG_NON_OVERLAPPING` etc. — claim parser does not extend the enum; claims are orthogonal to the 4-value `Parallel-safety` flag.
- PSQ-1 helper architecture (separate library API + CLI in one module) — claim module mirrors that shape.
- BC-PROJ-9 5-inventory propagation discipline ([[ADR-049]] / [[ADR-053]] precedent N=8 cumulative — slice-049/050/051/057/058/059/060/063 — NOT including slice-072 itself; slice-072 makes it N=9) for the new `tools/slice_queue_claim.py` module: `plugin.yaml` tools block + `tools/install_audit._CANONICAL_TOOLS` + INSTALL.md tool-count literal sites — all fan out together. **Cp1252 regression-test bucketing** (per Critic B1 ACCEPTED-FIXED): `slice_queue_claim` is NOT bucketed into `tests/methodology/test_utf8_stdout_regression._ROOT_ONLY_TOOLS` because its CLI surface (`--claim`/`--release`/`--force-claim`/`--queue`) does NOT accept `--root`. Instead, a bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` mirrors the `test_install_audit_survives_cp1252_with_u2192` precedent at `tests/methodology/test_utf8_stdout_regression.py:121-129` (install_audit is the canonical bespoke-test exemplar — `--claude-dir` argv shape, not `--root`).
- `tools/_stdout.py` UTF-8 stdout reconfiguration (per [[ADR-038]] / UTF8-STDOUT-1) — new CLI invokes `_stdout.reconfigure_stdout_utf8()` first thing in `main()`, mirroring slice_queue_writer's pattern.
- `tools/_vault_paths.VAULT_ROOT` constant ([[ADR-065]]) — queue file path resolution routes through `VAULT_ROOT / _QUEUE_FILENAME` (no `"architecture/"` literal).
- BCR-1: NOT a BCR-1 round-trip (this slice closes a risk-register entry R-19, not a `SC-NNN` from `diagnose-out/backlog.md`; no `**Closes:** SC-NNN` sentinel in mission-brief).
- AVFS-1 + MCFS-1 + TVFS-1 + OSDG-1 forward-sync obligations on PMI-1 bump (standard post-bump fan-out per slice-066/067/069 precedent).

## Components touched

### `tools/slice_queue_claim.py` (NEW)

- **Responsibility**: Implements the PSQ-2 claim CLI + library API. Reads git config user identity, parses the existing queue file's claim state, applies claim/release/force-claim mutations atomically, and writes the result.
- **Lives at**: `tools/slice_queue_claim.py` (created by this slice).
- **Public surface**:
  - `read_git_config_user() -> tuple[str, str]` — reads `git config user.name` + `git config user.email` via `subprocess.run(['git', 'config', '<key>'], capture_output=True, text=True, check=False, timeout=5)`; raises `ClaimUsageError` on `returncode == 1` (key unset — idiomatic git absence; per upstream `git-scm.com/docs/git-config`) OR `returncode == 0` with `stdout.strip() == ""` (configured-empty value treated as effectively-unset) OR other non-zero `returncode` (git-tool error). Each absence case names the specific failing key (`user.name` vs `user.email`) in the error message. Per Critic m2 ACCEPTED-FIXED.
  - `parse_queue_text(text: str) -> dict[str, dict[str, str | list[str]]]` — returns `{candidate_name: {"claimed_by": "<name> <email>", "claimed_at": "<iso8601>", "_extra_field_lines": [...]}}` for **every** entry in the queue (claimed or not, per meta-Critic m-add-2 ACCEPTED-FIXED). For unclaimed entries, the `claimed_by` and `claimed_at` keys are ABSENT (consumers MUST use `dict.get(...)`); the `_extra_field_lines` key is ALWAYS present (possibly empty list). For partially-claimed-but-malformed entries (one of `Claimed-by:`/`Claimed-at:` present without the other), `parse_queue_text` raises `ClaimUsageError` rather than returning a half-populated dict. `_extra_field_lines` is the list of unknown forward-compat field-line strings appearing AFTER `**Risk-retired:**` for that entry (PSQ-3+ extensibility per ADR-067 §Consequences; Critic M3 ACCEPTED-FIXED). Reads are CRLF-tolerant — internally normalizes `\r\n` → `\n` before parsing. Empty dict ONLY if file contains no entries (no `### <name>` headings). Unknown forward-compat lines DO NOT trigger malformed detection — they pass through verbatim in `_extra_field_lines`.
  - `apply_claim(text: str, candidate: str, claim_user: str, claim_at: str, *, force: bool) -> str` — returns mutated text; raises `ClaimUsageError` on already-claimed without `force=True`, on missing candidate, or on malformed schema. Preserves `_extra_field_lines` verbatim.
  - `apply_release(text: str, candidate: str) -> str` — returns text with both claim lines removed for that candidate (preserves `_extra_field_lines`); raises `ClaimUsageError` ONLY if candidate is NOT present in the queue (typo-rejection per Critic M2 ACCEPTED-FIXED — symmetric with `apply_claim`'s missing-candidate behavior). If candidate IS present but already unclaimed → exit 0 idempotent (no-op).
  - `main(argv: list[str] | None = None) -> int` — CLI entry; exit 0 success / exit 2 usage error / no other codes.
- **Key interactions**:
  - Subprocess (`git config user.name` / `user.email`) — read-only.
  - `tools/_stdout.reconfigure_stdout_utf8` — first call in `main`.
  - `tools/_vault_paths.VAULT_ROOT` — for default queue file path.
  - `tools/slice_queue_writer` does NOT import this module (reverse dependency only — writer's `write_slice_queue` imports `parse_queue_text` from claim module to read existing claims at regen time).

### `tools/slice_queue_writer.py` (MODIFIED)

- **Responsibility**: Existing PSQ-1 writer (`write_slice_queue` + `_format_entry`) gains claim-aware behavior — preserves existing claims across `/slice` Step 6.5 regeneration.
- **Lives at**: `tools/slice_queue_writer.py` (existing).
- **Changes**:
  - `_format_entry` (L622-640): when item dict has `claimed_by` + `claimed_at` keys (both non-empty), INSERT two `Claimed-by:` + `Claimed-at:` lines AFTER the `Risk-retired:` element AND BEFORE the trailing `""` empty-line separator (preserve inter-entry blank-line separation — insertion position is index `[-2]` not `[-1]`; per Critic m1 ACCEPTED-FIXED). When item dict has `_extra_field_lines` (list of forward-compat unknown lines, PSQ-3+ extensibility), append them verbatim AFTER the claim lines but still BEFORE the trailing `""` (preserves forward-compat schema additions on roundtrip per ADR-067 §Consequences). Otherwise emit the existing 8-line shape unchanged.
  - `write_slice_queue` (L648-732): after computing `items` from new candidates (current behavior unchanged), call `tools.slice_queue_claim.parse_queue_text(existing_text)` against the current queue file content (if it exists); for each item whose `name` appears in the parsed dict, copy `claimed_by` (via `.get(...)`, may be absent on unclaimed entries) + `claimed_at` (via `.get(...)`) + `_extra_field_lines` (always present per m-add-2 spec). Items whose dict-shape lacks `claimed_by`/`claimed_at` are treated as unclaimed at re-emission time. Claims on candidates dropped from the new top-10 are not transferred (silently discarded); their `_extra_field_lines` are also discarded (cross-regen forward-compat preservation requires the candidate to survive into the new top-10). This is the slice's load-bearing PSQ-1↔PSQ-2 integration seam. **Atomic write**: line `tmp_path.write_text(body, encoding="utf-8")` at L730 gains explicit `newline=""` argument (`tmp_path.write_text(body, encoding="utf-8", newline="")`) for LF-only byte-deterministic emission on Windows — per Critic M1 ACCEPTED-FIXED (modelcontextprotocol/python-sdk#2433 + runebook.dev TextIOWrapper docs confirm default `newline=None` translates `\n`→`\r\n` on Windows in text mode, breaking byte-equal claim-preservation round-trip assertions). PSQ-1's existing pinned tests assert against `format_queue_md`'s pure-Python `"\n".join(...)` output — adding `newline=""` aligns the writer with what the formatter already produces (no PSQ-1 regression risk).
- **Key interactions**: Imports `tools.slice_queue_claim.parse_queue_text` at module top (no circular dependency — claim module does not import writer).

### `skills/slice/SKILL.md` Step 6.5 (MODIFIED, OSDG-1-guarded)

- **Responsibility**: Add one sentence to the existing Step 6.5 prose block documenting that claim metadata survives across regeneration.
- **Lives at**: `skills/slice/SKILL.md` Step 6.5 (current canonical anchor: invocation block in the "### Step 6.5: Write the parallel-slice queue (PSQ-1)" section).
- **Change shape**: Insert exactly one sentence at end of the existing PSQ-1 invocation block prose explaining the PSQ-2 preservation behavior — e.g.: "After PSQ-2 ships (slice-072 / [[ADR-067]]), the helper preserves `Claimed-by:` / `Claimed-at:` field lines on candidates whose names survive into the regenerated top-10; claims on dropped candidates are silently discarded. Use `python -m tools.slice_queue_claim --claim <name>` to claim a candidate; see [[ADR-067]] for force-claim semantics."
- **Drift guard**: OSDG-1 guarded via `tests/methodology/test_slice_skill_drift.py` (existing); forward-sync to `~/.claude/skills/slice/SKILL.md` required at /build-slice Phase F.

### `architecture/risk-register.md` R-19 (MODIFIED)

- Status field: `mitigating` → `retired`.
- New `**Retired**:` field-line citing slice-072 + ADR-067 + the retirement rationale (claim machinery makes queue freshness a hint, not a load-bearing collision-safety signal).
- All prior R-19 prose preserved verbatim per slice-040 R-10 / slice-057 R-15 retirement-precedent (no edit-in-place of historical record).
- Append a retirement paragraph at section end naming slice-072 + ADR-067 — and per Critic B2 ACCEPTED-FIXED, explicitly disambiguate the predecessor-spec drift: R-19's mid-2026-05 Mitigation prose AND ADR-064 L37 both anticipated `session-id detection` as part of PSQ-2's design. ADR-067 §"Options considered" Option 2 + §"Identity model implications" explicitly rule out session-id ownership — PSQ-2 ships git-identity-only (`Claimed-by:` keyed on `git config user.name + user.email`, no session-id overlay). Predecessor prose is preserved verbatim as historical record; ADR-067 §Decision is authoritative on the chosen identity model. ADR-064 itself remains untouched (append-only ADR discipline per project rules); the divergence is documented in the new retirement paragraph + ADR-067 §Lineage, NOT via supersession.

### `methodology-changelog.md` `## v0.71.0` entry (NEW)

- Header: `## v0.71.0 — 2026-05-27`
- Body: mints PSQ-2 as new RULE-ID, sibling on parallel-slice family axis (PSQ-1 + PSQ-2 + nominee PSQ-3), additive schema extension on PSQ-1, supersedes nothing. Cites ADR-067, slice-072.
- 5-part PMI-1 atomic bump leg enumeration: `VERSION` + `plugin.yaml.version` + `pyproject.toml [project].version` (PVFS-1) + `## v0.71.0` header + installed `~/.claude/ai-sdlc-VERSION` (AVFS-1).
- Post-bump forward-sync obligations (NOT PMI-1 legs): MCFS-1 (`methodology-changelog.md` → `~/.claude/methodology-changelog.md`); TVFS-1 (`pip install --upgrade .` of `ai-sdlc-tools`); OSDG-1 forward-sync of `skills/slice/SKILL.md` Step 6.5 line; BC-PROJ-9 5-inventory fan-out for the new `tools/slice_queue_claim.py` module; shippability row #72 paired-entry-pin.

### `architecture/shippability.md` row #72 (NEW)

- Title: slice-072-add-psq-2-claim-machinery
- Critical path: PSQ-2 schema extension + claim CLI + claim-preservation merge + R-19 retired + methodology v0.71.0
- Command: `<HOME>/.claude/.venv/Scripts/python.exe -m pytest tests/methodology/test_psq_2_claim_machinery.py tests/methodology/test_methodology_changelog.py::test_v_0_71_0_psq_2_entry_present_in_repo tests/methodology/test_methodology_changelog.py::test_v_0_71_0_psq_2_shippability_consumer_propagation --no-header -q`
- Runtime: <3s
- BCR-1 traceability axis: not applicable (R-19-driven, no SC-NNN closure).

## Contracts added or changed

### `architecture/slice-queue.md` per-entry schema — PSQ-2 additive extension

- **PSQ-1 baseline** (unchanged at this slice): 5 required field lines in order `**Source:**` / `**Blast-radius:**` / `**Parallel-safety:**` / `**Effort:**` / `**Risk-retired:**`, each on its own line, all under a `### <candidate-name>` H3 heading with a blank line above and below the field block. Pinned by `tests/skills/slice/test_slice_queue_output.py`.
- **PSQ-2 additive extension**: 2 optional field lines `**Claimed-by:**` (value: `<git user.name> <git user.email>` — single space between name and email) and `**Claimed-at:**` (value: ISO-8601 UTC timestamp with `+00:00` offset suffix, e.g. `2026-05-27T14:33:31+00:00`), both appearing AFTER `**Risk-retired:**`, in order Claimed-by first then Claimed-at. Either both lines present (claimed) or both absent (unclaimed) — partial state is malformed.
- **Defined in code at**: `tools/slice_queue_writer.py::_format_entry` (emission) + `tools/slice_queue_claim.py::parse_queue_text` (parsing).
- **Auth model**: claim CLI READS `git config user.name` + `user.email` (subprocess); WRITES only to `architecture/slice-queue.md` (single file). No other filesystem access. No `git config --set` calls. See "Authorization model for this slice" below.
- **Error cases**:
  - Absent `git config user.name` (returncode==1 OR returncode==0 with stdout.strip()=="") → exit 2, stderr `PSQ-2 usage error: git config user.name not set; PSQ-2 claims require git identity`.
  - Absent `git config user.email` (returncode==1 OR returncode==0 with stdout.strip()=="") → exit 2, stderr `PSQ-2 usage error: git config user.email not set; PSQ-2 claims require git identity`.
  - Bare `--claim <name>` on already-claimed → exit 2, stderr `PSQ-2 usage error: <name> already claimed by <prev-user> at <prev-ts>; use --force-claim to overwrite`.
  - `--claim <name>` where `<name>` is NOT present in queue → exit 2, stderr `PSQ-2 usage error: candidate <name> not found in queue`.
  - `--release <name>` where `<name>` IS present in queue AND IS currently unclaimed → exit 0 no-op (idempotent release; documented behavior, not an error — per Critic M2 ACCEPTED-FIXED).
  - `--release <name>` where `<name>` is NOT present in queue → exit 2, stderr `PSQ-2 usage error: candidate <name> not found in queue` (typo-rejection; symmetric with `--claim`'s missing-candidate case per Critic M2 ACCEPTED-FIXED).
  - `--force-claim <name>` on unclaimed candidate → succeeds (force-claim == claim when there's nothing to overwrite).
  - Malformed queue file (PARTIAL known claim block: `Claimed-by:` present without `Claimed-at:` OR vice-versa) → exit 2 on any operation, stderr `PSQ-2 usage error: malformed claim block for <name>`. Unknown forward-compat field lines (`**SomeNewField:** ...` after `**Risk-retired:**`) DO NOT trigger malformed detection — they are preserved verbatim on roundtrip via `_extra_field_lines` per Critic M3 ACCEPTED-FIXED.

### New CLI surface

- `python -m tools.slice_queue_claim --claim <candidate-name>` → claim.
- `python -m tools.slice_queue_claim --release <candidate-name>` → release.
- `python -m tools.slice_queue_claim --force-claim <candidate-name>` → force-claim (overwrite or claim).
- `--queue <path>` optional override for non-default queue file location (testing seam — default is `<VAULT_ROOT>/slice-queue.md`).
- Mutually exclusive: exactly one of `--claim` / `--release` / `--force-claim` per invocation.

## Data model deltas

No relational data model. The schema delta is exclusively the markdown file format defined in **Contracts added or changed** above.

## Wiring matrix

Per **WIRE-1** (`methodology-changelog.md` v0.9.0). Every new module/file this slice introduces must declare a consumer entry point AND a consumer test, OR carry an explicit exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `tools/slice_queue_claim.py` | `python -m tools.slice_queue_claim` CLI (invoked by user at any /slice + /build-slice boundary); also imported by `tools/slice_queue_writer.write_slice_queue` for claim preservation at /slice Step 6.5 | `tests/methodology/test_psq_2_claim_machinery.py::test_claim_cli_writes_user_name_and_email_from_git_config` | — |

(No other NEW modules — slice_queue_writer.py is modified, not new.)

## Decisions made (ADRs)

- [[ADR-067]] — Mint PSQ-2: additive claim machinery on PSQ-1's queue file with git-identity ownership and explicit force-claim recovery — reversibility: **cheap**

## Authorization model for this slice

The new `tools/slice_queue_claim` CLI operates entirely with the invoking user's local privileges. Authorization model:

- **Read scope**: `git config user.name` + `git config user.email` (read-only subprocess); `architecture/slice-queue.md` (read).
- **Write scope**: `architecture/slice-queue.md` ONLY (via atomic `.tmp` sibling + `os.replace`). No other filesystem writes. No environment variable mutations. No git config writes. No network access.
- **Identity model**: claim ownership is the git-configured user identity at claim time. No session-id, no PID, no hostname. Two sessions running as the same git user can each claim distinct candidates but cannot distinguish themselves on a single candidate — they are by definition the same claimant per ADR-067 §Decision.
- **Adversarial model**: the claim mechanism is cooperative coordination, NOT a security boundary. A malicious actor with local filesystem write to `architecture/slice-queue.md` can forge any claim or unclaim. PSQ-2 does not defend against that — the threat model is "two cooperating Claude sessions on the same machine should not collide", not "untrusted actor manipulates queue".
- **Privilege escalation**: none possible by design — no setuid/setgid, no IPC, no privileged operations.

## Error model for this slice

PSQ-2 introduces the following error surfaces:

| Error | Exit code | Where raised | Stderr message |
|-------|-----------|--------------|---------------|
| Missing `git config user.name` (unset OR configured-empty) | 2 | `read_git_config_user` | `PSQ-2 usage error: git config user.name not set; PSQ-2 claims require git identity` |
| Missing `git config user.email` (unset OR configured-empty) | 2 | `read_git_config_user` | `PSQ-2 usage error: git config user.email not set; PSQ-2 claims require git identity` |
| Candidate not in queue (claim or release) | 2 | `apply_claim` / `apply_release` | `PSQ-2 usage error: candidate <name> not found in queue` |
| Already-claimed without force | 2 | `apply_claim` (when `force=False`) | `PSQ-2 usage error: <name> already claimed by <prev-user> at <prev-ts>; use --force-claim to overwrite` |
| Malformed claim block (partial known fields only) | 2 | `parse_queue_text` | `PSQ-2 usage error: malformed claim block for <name>` |
| Queue file missing | 2 | `main` (before parse) | `PSQ-2 usage error: queue file not found at <path>; run /slice to create it` |
| Mutually-exclusive flags | 2 | `argparse` (via `_build_parser` mutually-exclusive group) | argparse-standard error message |
| `--release` on present-but-unclaimed candidate | 0 (no-op) | `apply_release` | (none — idempotent release is documented behavior) |

PSQ-1's existing error model (queue-write failure non-fatal, wrapped in try/except in /slice Step 6.5) is preserved unchanged — PSQ-2 adds only the claim-CLI error surfaces above.

## Test-first plan (per AC; see mission-brief.md for the full table)

Test module: `tests/methodology/test_psq_2_claim_machinery.py` (NEW; ~330 LOC). 15 unit tests in the new module + 1 bespoke cp1252 regression test added to `tests/methodology/test_utf8_stdout_regression.py` + 2 paired-pin tests in `test_methodology_changelog.py` = **18 TF-1 rows total** (post-Critic fix-block expansion from 12 to 18: +1 CRLF tolerance + 1 forward-compat preservation + 1 configured-empty + 1 `--queue` override + 1 bespoke cp1252 + 1 release-on-unknown). PENDING → WRITTEN-FAILING → PASSING per AC mapping in mission-brief.

Key test seams:
- Git config isolation: use `monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')` + create a tmp repo with `git init` + `git config user.name <fixture> --local` to control identity per test. Configured-empty case uses `git config user.name ""` (subprocess returncode 0, stdout strips empty).
- Atomic-write proof: monkeypatch `os.replace` to raise mid-call; assert `.tmp` cleanup + original file unchanged (PSQ-1 atomicity test pattern reused).
- Preservation merge: write a queue with a claim, call `write_slice_queue` with same candidates list, read result, assert claim survives byte-equal (writes use `newline=""` for LF-only emit per Critic M1).
- CRLF tolerance: feed `parse_queue_text` a fixture text with `\r\n` line endings; assert returned dict matches LF-input equivalent.
- Forward-compat: feed `parse_queue_text` a fixture with `**SomeNewField:** value` after `**Risk-retired:**`; assert preserved on roundtrip via `_extra_field_lines`.
- Bespoke cp1252 (B1 fix): mirror `test_install_audit_survives_cp1252_with_u2192` at `tests/methodology/test_utf8_stdout_regression.py:121-129` — invoke `[PY, "-m", "tools.slice_queue_claim", "--claim", "fake-name", "--queue", str(tmp_path/"q.md")]` under cp1252; assert no `UnicodeEncodeError` in stderr.

## Pre-finish dogfood (APED-1 empirical-parse-rule-execution discipline)

Per Critic Dim 9 + slice-070/071 APED-1 lineage: this slice introduces a parse-rule (`parse_queue_text`); empirical execution against actual production data is required at /build-slice Phase A BEFORE declaring AC1 PASSING.

**Empirical battery** (Phase A, BEFORE writing the implementation):

1. Run the *failing* `parse_queue_text` tests against the live `architecture/slice-queue.md` (current 10-entry file at slice-072 ship time). Expected: tests assert claim-absent state across all 10 entries; `_extra_field_lines` empty for all entries (PSQ-1 baseline).
2. Construct a malformed-block fixture (entry with `**Claimed-by:**` but NO `**Claimed-at:**`) and run `apply_claim` against it — expect `ClaimUsageError` with `malformed claim block` message naming the offending candidate.
3. Construct a forward-compat fixture (entry with `**Claim-rationale:** future stuff` after `**Risk-retired:**`) and run `parse_queue_text` then roundtrip via `_format_entry` — assert the unknown line survives byte-equal in `_extra_field_lines` and re-emitted output.
4. Construct a CRLF-input fixture (whole file with `\r\n` line endings) and run `parse_queue_text` — assert parsed dict matches LF-input equivalent.

These 4 batteries are the empirical proof that the parse-rule survives real-world variance (slice-070 APED-1 N=1 dotfile blind-spot + slice-071 APED-1 N=2 broken-regex precedent — N=3 promotion candidate if any battery surfaces a defect at Phase A).

At /build-slice Phase E mid-slice smoke, claim a real candidate from the live `architecture/slice-queue.md` and verify the round-trip:

```
$PY -m tools.slice_queue_claim --claim add-rebase-and-conflict-discipline
$PY -m tools.slice_queue_claim --release add-rebase-and-conflict-discipline
```

Expected diff:
- Post-claim: 2 new lines under the candidate entry; nothing else moves.
- Post-release: clean diff (original state restored byte-equal).

If fails: STOP. The most likely cause is non-atomic write or schema position bug.
