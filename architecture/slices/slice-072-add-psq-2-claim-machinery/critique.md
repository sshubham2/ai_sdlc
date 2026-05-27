# Critique: Slice 072 add-psq-2-claim-machinery

**Critic reviewed**: mission-brief.md, design.md, ADR-067-mint-psq-2-claim-machinery.md
**Date**: 2026-05-27
**Result**: NEEDS-FIXES

## Summary

Critic returned 2 Blockers (B1 cp1252 bucket mismatch; B2 stale session-id forward-references in R-19 + ADR-064 contradicting ADR-067's identity model) + 4 Majors (M1 Windows CRLF round-trip; M2 `--release` exit-code ambiguity; M3 forward-compat field-line behavior unspecified; M4 AC5 ratchet-packing recurrence of slice-067 N=1 signal) + 5 minors (m1 trailing blank-line position; m2 git-config absence-detection mode; m3 `--queue` flag TF-1 row missing; m4 PMI-1 leg-enumeration drift between mission-brief & design; m5 BC-PROJ-9 N=8 vs N=9 internal inconsistency). All 11 findings VALID and addressable in-band; the design is structurally sound — git-identity-only ownership is defensible, schema extension is additive, atomicity reuses PSQ-1's proven pattern. Builder drafts all ACCEPTED-FIXED via in-slice edits to mission-brief.md + design.md + ADR-067.md plus 6 new TF-1 plan rows (total 18 TF-1 rows) + 1 explicit cite of the N=2 promotion of slice-067's AC-count pattern signal.

## Findings

### Blockers (must address before /build-slice)

#### B1: `_ROOT_ONLY_TOOLS` is the wrong cp1252 regression-test bucket for `slice_queue_claim`

- **Claim under review**: design.md L26 — `_ROOT_ONLY_TOOLS` bucket listed as PSQ-2's cp1252 regression-test home for the new `tools/slice_queue_claim.py` module under the BC-PROJ-9 5-inventory propagation discipline.
- **Issue**: PSQ-2's CLI surface is `--claim <name>` / `--release <name>` / `--force-claim <name>` (mutually exclusive) + `--queue <path>`. There is no `--root` flag — by design (no `--root` in any acceptance criterion). But `_ROOT_ONLY_TOOLS` parametrize invokes `_root_only_argv` which builds `[PY, "-m", tool, "--root", str(REPO_ROOT)]` (`tests/methodology/test_utf8_stdout_regression.py:76-77`). The new CLI will fail with argparse `unrecognized argument: --root` → exit 2 → cp1252 regression test FAILs claiming `slice_queue_claim` doesn't survive cp1252.
- **Evidence**: `tests/methodology/test_utf8_stdout_regression.py:76-77` `_root_only_argv` + L95-106 `_ROOT_ONLY_TOOLS` actual content + L121-129 `test_install_audit_survives_cp1252_with_u2192` (the bespoke-test precedent — `install_audit` takes `--claude-dir`, not `--root`, and has its own dedicated cp1252 test mirror).
- **Proposed fix**: Adopt **option (b)** from the Critic — author a bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` in `tests/methodology/test_utf8_stdout_regression.py` mirroring the `test_install_audit_survives_cp1252_with_u2192` shape (the canonical precedent), invoking the CLI with `["--claim", "fake-candidate-name", "--queue", str(tmp_path/"q.md")]`. Update design.md §"Components touched" to remove the `_ROOT_ONLY_TOOLS` reference and replace with the bespoke-test path. Update ADR-067 §Consequences similarly.
- **Builder draft**: ACCEPTED-FIXED — design.md §"What's reused" / §"Components touched" rewrite + ADR-067 §Consequences rewrite to cite `test_slice_queue_claim_survives_cp1252_with_u2192` bespoke test, mirroring the install_audit precedent; add the bespoke test as a new TF-1 plan row (AC2).

#### B2: R-19 + ADR-064 carry stale forward-references to "session-id detection" that ADR-067 explicitly rejects, contradicting the "prose preserved verbatim" claim

- **Claim under review**: design.md L70 — "All prior R-19 prose preserved verbatim per slice-040 R-10 / slice-057 R-15 retirement-precedent (no edit-in-place of historical record)."
- **Issue**: `architecture/risk-register.md:329` (R-19 Mitigation paragraph) says: *"Slice-068's PSQ-2 claim machinery (`Claimed-by/-at/Force-claim` schema + session-id detection) will narrow this further"*. `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md:37` says: *"PSQ-2 (slice-068 nominee): claim state machine (`Claimed-by/-at/Force-claim` schema + `/slice --claim` + `/slice --force-claim` + session-id detection)."* ADR-067 §"Options considered" Option 2 EXPLICITLY REJECTS session-id ownership; §"Identity model implications" + §Decision both rule it out. R-19 is being retired *while still carrying a contradictory description of what retired it*. ADR-067 is non-superseding ADR-064 (per ADR-067 frontmatter `supersedes: null`), so ADR-064 L37 is append-only-untouchable; the only place to disambiguate is the NEW R-19 retirement note + ADR-067 §Lineage.
- **Evidence**: `architecture/risk-register.md:329` quoted above; `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md:37` quoted above; ADR-067 §"Options considered" Option 2 (rejected); ADR-067 §"Identity model implications" (git-identity-only); design.md L70 ("prior R-19 prose preserved verbatim").
- **Proposed fix**: (i) In the R-19 retirement paragraph this slice ADDS at section end, include an explicit disambiguation: *"The R-19 mitigation prose above (paragraph dated slice-067) + ADR-064 L37 both anticipated `session-id detection` as part of the PSQ-2 design. ADR-067 §"Options considered" Option 2 explicitly rules out session-id ownership in favor of git-identity-only — PSQ-2 ships `Claimed-by:` keyed on `git config user.name + user.email`, no session-id overlay. The predecessor prose is preserved verbatim as historical record per slice-040 R-10 retirement-precedent; ADR-067 §Decision is authoritative on the chosen identity model."* (ii) Add a corresponding "Lineage divergence" note in ADR-067 §Lineage explicitly naming ADR-064 L37's `session-id detection` forward-reference as a documented predecessor-spec drift, NOT a supersession — slice-067's PSQ-1 ADR predicted an identity model PSQ-2 ultimately chose not to ship.
- **Builder draft**: ACCEPTED-FIXED — design.md §"Components touched" R-19 sub-section + ADR-067 §Lineage both gain the disambiguation paragraphs cited above. ADR-064 itself untouched (append-only ADR discipline).

### Majors (address this slice)

#### M1: TextIOWrapper newline handling unspecified — Windows CRLF round-trip risk for byte-equal claim preservation

- **Claim under review**: PSQ-1 writer at `tools/slice_queue_writer.py:729-731` uses `tmp_path.write_text(body, encoding="utf-8")` with no explicit `newline=`. PSQ-2's claim-preservation merge reads existing queue via `parse_queue_text`, mutates, writes back.
- **Issue**: `Path.write_text(...)` defaults `newline=None` which translates `\n`→`\r\n` on Windows in text mode. PSQ-1's existing writer already silently emits CRLF on Windows. PSQ-2's load-bearing byte-equal claim-preservation assertion (mission-brief Verification §4 + design.md §"Test seams") is brittle if reader strips `\r` while writer emits `\r\n`, or vice-versa.
- **Evidence**: WebSearch — modelcontextprotocol/python-sdk#2433 confirms Windows TextIOWrapper emits CRLF; runebook.dev TextIOWrapper docs confirm `newline=None` translates. CLAUDE.md confirms Windows is the primary dev platform. PSQ-1 ships tests on Windows-CRLF baseline (slice-067 reflection).
- **Proposed fix**: Specify in design.md §"Components touched" `write_slice_queue` MODIFIED sub-section: writes use `tmp_path.write_text(body, encoding='utf-8', newline='')` for byte-deterministic LF-only emission; reads via `parse_queue_text` accept both `\r\n` and `\n` input (normalize via `.replace('\r\n', '\n')` before parsing). Add TF-1 row `test_parse_queue_text_accepts_crlf_input`. (PSQ-1's existing pinned tests are unchanged — they assert against `format_queue_md`'s output which is `"\n".join(...)`-shaped already; the LF-only emit aligns the writer with what the formatter already produces.)
- **Builder draft**: ACCEPTED-FIXED — design.md §"Components touched" `write_slice_queue` sub-section + design.md §"Test seams" gain the `newline=''` + CRLF-tolerant-read specification; new TF-1 plan row `test_parse_queue_text_accepts_crlf_input` (AC1).

#### M2: `--release` on nonexistent candidate name — exit code ambiguity

- **Claim under review**: design.md L100 + L148 — two adjacent specifications on release semantics.
- **Issue**: (i) candidate-in-queue + unclaimed → exit 0 idempotent (L100). (ii) candidate-not-in-queue + `--release` → unclear; L148 error table says "candidate not in queue → exit 2 in `apply_claim` / `apply_release`". The two specs cover overlapping but distinct cases; prose is internally consistent but unclearly worded.
- **Evidence**: design.md L100 (release on unclaimed = exit 0 idempotent) vs L148 (release on missing candidate = exit 2). Side-by-side reading reveals ambiguity.
- **Proposed fix**: Reword design.md L100 to disambiguate the two cases explicitly: *"`--release <name>` where `<name>` IS present in the queue AND IS currently unclaimed → exit 0 no-op (idempotent release on an already-released candidate). `--release <name>` where `<name>` is NOT present in the queue → exit 2 (typo-rejection; symmetric with `--claim`'s missing-candidate case)."* Add TF-1 plan row `test_release_on_unknown_candidate_exits_2` (AC3).
- **Builder draft**: ACCEPTED-FIXED — design.md L100 reword + new TF-1 row added.

#### M3: `parse_queue_text` permissiveness to future PSQ-3+ optional fields unspecified

- **Claim under review**: ADR-067 §Consequences "A future PSQ-3+ slice MAY add new optional field lines per entry [...] without breaking PSQ-2's schema" + design.md L40 `parse_queue_text -> dict[str, dict[str, str]]` 2-key signature.
- **Issue**: Forward-compat behavior unspecified. (i) Does parser refuse unknown field lines as "malformed claim block" per L150? (ii) Does `write_slice_queue` preserve unknown PSQ-3+ field lines on roundtrip, or strip them? Strict-and-strips would retroactively break PSQ-3's pinned tests AND erase PSQ-3 candidates' extra fields on every `/slice` regeneration.
- **Evidence**: design.md L40 (parse return-dict 2-key) + L150 (malformed → exit 2) + ADR-067 §Consequences (PSQ-3+ may extend) all in tension.
- **Proposed fix**: Specify in design.md §"Contracts added or changed" — `parse_queue_text` is permissive to forward-compat field lines: unknown `**<Key>:** <value>` field lines after `**Risk-retired:**` are passed through unchanged on roundtrip (preserved on the item dict under `_extra_field_lines: list[str]`); `_format_entry` re-emits them verbatim after the known claim lines. Malformed-claim-block detection fires only on PARTIAL known claim block (`Claimed-by:` without `Claimed-at:` or vice-versa), NOT on unknown forward-compat lines. Add TF-1 plan row `test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip` (AC1).
- **Builder draft**: ACCEPTED-FIXED — design.md §"Contracts added or changed" gains the forward-compat pass-through spec; design.md L40 signature updated to `dict[str, dict[str, str | list[str]]]`; new TF-1 row added.

#### M4: AC count = 5 with multi-ratchet AC5 — N=2 promotion of slice-067 pattern signal

- **Claim under review**: mission-brief.md AC5 packs 3 distinct ratchets (R-19 flip + methodology v0.71.0 entry + 5-part PMI-1 atomic bump) into one AC.
- **Issue**: Slice-067 reflection L26 + L77 logged this as **Pattern signal N=1**: AC count > 5 on new-mechanism mints with prescription "if recurs at slice-068+ new-mechanism mints, evaluate relaxing SKILL.md's ≤5-AC rule via /critic-calibrate". Slice-072 is a new-mechanism mint with 3-ratchet AC5 — this is **N=2 promotion of the slice-067 signal**. Current compression makes AC5's PASS/FAIL verification ambiguous (does AC5 fail if R-19 flipped but PMI-1 partial-applied?).
- **Evidence**: archive/slice-067-add-parallel-slice-queue-output/reflection.md L26 + L77 quoted; mission-brief.md AC5 packing.
- **Proposed fix**: **Option (a)** — split AC5 into AC5 (R-19 retirement) + AC6 (methodology v0.71.0 entry + paired-pin tests + 5-part PMI-1 atomic bump). Explicitly cite this as the N=2 promotion of the slice-067 pattern signal, recommend `/critic-calibrate` action at slice-073 reflection to formalize ≤6-AC carve-out for new-mechanism mints. (Per slice-067 documented-deviation precedent, ≤5-AC rule is relaxable with rationale for entry-pin-meta-ACs.)
- **Builder draft**: ACCEPTED-FIXED — split AC5 → AC5 + AC6 in mission-brief.md; add documented-deviation note immediately after AC6 citing slice-067 reflection L26 + L77 as the N=1 precedent and slice-072 as N=2 promotion; update mission-brief Pre-finish gate L98 to "All 6 acceptance criteria PASS"; update milestone.md "current focus" + design.md L77 references; TPHD-1 sub-mode (a) harmonization: update TF-1 plan rows L38-39 to AC6 (the v0.71.0 entry-pin tests move from AC5 to AC6).

### Minors (log; address if cheap)

#### m1: `_format_entry` trailing blank line position interaction unspecified

- **Claim under review**: design.md L55.
- **Issue**: `_format_entry` returns list ending with `Risk-retired:` line + `""` (trailing empty-line entry-separator). Design says "append two lines after the existing `Risk-retired:` line" — but inserting AT [-1] (after the `""`) collapses entry separation; inserting at [-2] (before the `""`) preserves it.
- **Evidence**: `tools/slice_queue_writer.py:631-640` (return list with trailing `""`).
- **Proposed fix**: Reword design.md L55 to specify insertion at index [-2] (before the trailing empty-line element), preserving the inter-entry blank-line separator.
- **Builder draft**: ACCEPTED-FIXED.

#### m2: `read_git_config_user` absence-detection mode unspecified

- **Claim under review**: design.md L39.
- **Issue**: `git config <key>` returns exit code 1 when key unset (per upstream docs). Design says "if either absent" but doesn't specify HOW absence is detected — exit code, empty stdout, or both. The two detect different things (a configured-empty `git config user.name ""` differs from unset).
- **Evidence**: WebSearch — zetcode + DataCamp confirm `git config` exit code 1 on unset key.
- **Proposed fix**: Specify exit-code-based detection in design.md L39: subprocess `check=False`, treat `returncode == 1` as "unset" (idiomatic git config absence), `returncode == 0 + stdout.strip() == ""` as "configured-empty" (also rejected), other non-zero `returncode` as "git tool error". Add TF-1 plan row `test_claim_cli_exits_2_on_configured_empty_user_name` (AC2).
- **Builder draft**: ACCEPTED-FIXED.

#### m3: `--queue <path>` flag has no TF-1 plan row

- **Claim under review**: design.md L109 (flag exists) vs mission-brief.md TF-1 plan L26-39 (zero rows mention `--queue`).
- **Issue**: `--queue` is the primary testing seam (per design.md L109) but is untested.
- **Proposed fix**: Add TF-1 plan row `test_claim_cli_uses_queue_path_override_when_provided` (AC2) pinning that `--queue <custom-path>` routes writes to the custom path (mirrors PSQ-1's `test_main_cli_custom_output_uses_canonical_write_path` precedent).
- **Builder draft**: ACCEPTED-FIXED.

#### m4: PMI-1 leg enumeration phrasing drift between mission-brief AC5 and design.md L77

- **Claim under review**: mission-brief.md AC5 + design.md L77.
- **Issue**: Both enumerate the same 5 legs in the same order, but mission-brief uses `## v0.71.0 header in methodology-changelog` while design.md uses `## v0.71.0 header + installed ~/.claude/ai-sdlc-VERSION (AVFS-1)` with rule-ID annotations. FBCD-1 sub-mode (a) cross-file consistency class; slice-067 M-add-4 caught exactly this drift class previously.
- **Proposed fix**: Harmonize to design.md L77's form (with rule-ID annotations PVFS-1 / AVFS-1). Propagate to mission-brief.md AC6 (the AC5→AC6 split absorbs this leg now).
- **Builder draft**: ACCEPTED-FIXED — already absorbed into the M4 AC5→AC6 split fix above; harmonized phrasing lands together.

#### m5: BC-PROJ-9 cumulative count N=8 vs N=9 internal discrepancy

- **Claim under review**: design.md L26 "N=8 cumulative" vs ADR-067 §Consequences L51 "N=9 cumulative post-slice-067".
- **Issue**: The two numbers describe the same precedent count under different framings (N=8 = precedent excluding slice-072; N=9 = including). Without explicit framing, the discrepancy reads as a count drift.
- **Proposed fix**: Harmonize phrasing — design.md L26: "N=8 cumulative precedent (slice-049/050/051/057/058/059/060/063 — does NOT include slice-072 itself)"; ADR-067 §Consequences L51: "N=9 cumulative including slice-072 (= the 8 precedent slices above + slice-072 itself)".
- **Builder draft**: ACCEPTED-FIXED.

## Dimensions checked

- [x] Unfounded assumptions — B2 (session-id forward-references) + m2 (git config absence-detection mode)
- [x] Missing edge cases — M1 (Windows CRLF) + M2 (`--release` on missing candidate) + M3 (forward-compat field lines). Concurrent-claim collision documented out-of-scope per ADR-067 §"Adversarial model" — accepted by Critic.
- [x] Over-engineering — none
- [x] Under-engineering — M4 (AC compression) + m3 (`--queue` flag untested)
- [x] Contract gaps — B1 (`_ROOT_ONLY_TOOLS` argv-shape mismatch) + M3 (forward-compat unknown-field behavior)
- [x] Security — none (per ADR-067 §"Adversarial model" — claim mechanism explicitly NOT a security boundary; read-only git-config consumption, single-file-write scope)
- [x] Drift from vault — B2 (R-19 + ADR-064 stale session-id forward-references) + m5 (BC-PROJ-9 N=8 vs N=9). MEPD-1 + PMI-1 + entry-pin obligation (Dim 7) — slice takes the (a) rule path correctly modulo m4 phrasing-drift.
- [x] Web-known issues — M1 (TextIOWrapper newline=None default + modelcontextprotocol/python-sdk#2433) + m2 (`git config` exit code 1 on unset key per git-scm.com/docs/git-config + zetcode + DataCamp). Queries logged: `python os.replace atomic file write windows TextIOWrapper newline gotcha 2025`; `git config user.name user.email subprocess exit code python timeout best practice 2025`.
- [x] Cross-cutting conformance — B1 (audit-tooling-doc-vs-implementation parity) + m1 (algorithm-path-conformance with pre-existing `_format_entry` trailing blank) + m4 (FBCD-1 cross-file PMI-1 leg-enumeration). APED-1 empirical-execution discipline applicable: recommend pre-executing the `parse_queue_text` battery against (i) the live `architecture/slice-queue.md` 10-entry file, (ii) partial-claim-block malformed fixture, (iii) forward-compat unknown-field-line fixture at /build-slice Phase A before declaring AC1 PASSING. Captured in design.md §"Pre-finish dogfood" as the canonical pre-build-time empirical battery.

## Triage

**Triaged by**: user
**Date**: 2026-05-27
**Final verdict**: CLEAN

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker  | ACCEPTED-FIXED | Bespoke `test_slice_queue_claim_survives_cp1252_with_u2192` mirrors install_audit precedent at `tests/methodology/test_utf8_stdout_regression.py:121-129`; design.md L26 + L168 + ADR-067 L51 rewritten to remove `_ROOT_ONLY_TOOLS` reference. |
| B2 | Blocker  | ACCEPTED-FIXED | ADR-067 §Lineage divergence note + design.md R-19 retirement-paragraph spec disambiguate via predecessor-spec-drift framing rather than supersession; ADR-064 stays append-only. |
| M1 | Major    | ACCEPTED-FIXED | design.md `write_slice_queue` MODIFIED sub-section adds explicit `newline=""` for LF-only emit; new TF-1 row `test_parse_queue_text_accepts_crlf_input` (AC1). |
| M2 | Major    | ACCEPTED-FIXED | design.md L101-102 disambiguates `--release` cases (present-unclaimed = exit 0; not-in-queue = exit 2); new TF-1 row `test_release_on_unknown_candidate_exits_2` (AC3). |
| M3 | Major    | ACCEPTED-FIXED | `_extra_field_lines: list[str]` pass-through specified in design.md L40 + L55; new TF-1 row `test_parse_queue_text_preserves_unknown_field_lines_on_roundtrip` (AC1). |
| M4 | Major    | ACCEPTED-FIXED | mission-brief.md AC5→AC5+AC6 split applied; documented-deviation note at L23 cites slice-067 N=1 → slice-072 N=2 promotion of AC-count pattern signal; /critic-calibrate route logged for slice-073 reflection. |
| m1 | Minor    | ACCEPTED-FIXED | design.md L55 pins insertion at index [-2] (preserves trailing empty-line entry-separator). |
| m2 | Minor    | ACCEPTED-FIXED | design.md L39 specifies 3-case exit-code-based absence detection (returncode 1 / configured-empty / git-tool-error); new TF-1 row `test_claim_cli_exits_2_on_configured_empty_user_name` (AC2). |
| m3 | Minor    | ACCEPTED-FIXED | New TF-1 row `test_claim_cli_uses_queue_path_override_when_provided` (AC2) pins the `--queue` testing seam. |
| m4 | Minor    | ACCEPTED-FIXED | Harmonized PMI-1 leg enumeration via AC5→AC6 split — AC6 prose at mission-brief L21 matches design.md L77 rule-ID-annotated form. |
| m5 | Minor    | ACCEPTED-FIXED | design.md L26 ("N=8 precedent excluding slice-072") + ADR-067 L51 ("N=9 including slice-072") explicitly framed as same fan-out under different scope. |
| M-add-1 | Major | ACCEPTED-FIXED | design.md §"What's new" L18-19 rewritten with ~330 LOC / 15 tests / cp1252 bespoke / AC6 reassignment per meta-Critic TPHD-1 N=6 cumulative catch. |
| m-add-1 | Minor | ACCEPTED-FIXED | milestone.md L29 "Current focus" rewritten with AC5/AC6 split + 6-AC count + slice-067 N=1 → slice-072 N=2 citation per meta-Critic m-add-1. |
| m-add-2 | Minor | ACCEPTED-FIXED | design.md L40 `parse_queue_text` spec extended with all-entries-returned + absent-keys-on-unclaimed semantics; `write_slice_queue` merge step uses `.get()` per the new contract. |
