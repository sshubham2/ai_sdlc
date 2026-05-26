# Critique: Slice 070 fix-psq-1-blast-radius-dict-leak

**Critic reviewed**: mission-brief.md, design.md, no new ADRs (voluntary-restraint EXCLUDE)
**Date**: 2026-05-26
**Result**: CLEAN (post-TRI-1 user ratification; pre-TRI-1 raw verdict was BLOCKED — see "Verdict transition" below)

## Summary

The first Critic delivered a BLOCKED verdict with two textbook-APED-1 blockers — empirical execution against the real `graphify-out/graph.json` proved the proposed `path → name → id` precedence falls through to `id` for every node in this repo (all `path` values are empty strings; the `name` key is absent; only `id` is universally populated). The fix would have silently produced opaque ID-strings in `Blast-radius:` cells, passing AC3's regex while semantically defeating PSQ-1's overlap detection. Builder restructured around the empirically-verified graphify node schema: introduce `_build_id_to_path_map` (reads graph.json once, maps node id → repo-relative `source_file`) and have `_node_to_path` resolve via that map. Six majors + four minors all addressed in same fix-block per TPHD-1 sub-mode (a).

## Verdict transition

- **Raw first-Critic verdict**: BLOCKED (B1 + B2 both blockers)
- **Post-Builder-fix-block draft verdict**: NEEDS-FIXES (all blockers + majors ACCEPTED-FIXED; one minor OVERRIDDEN with rationale verified by /reflect SKILL.md prose)
- **Meta-Critic /critique-review verdict**: EXTEND (3 missed findings M-add-1/2/3 — all same fix-block-residual-stale-precedence defect class; N=4 cumulative recurrence; all ACCEPTED-FIXED in /critique-review fix block; /critic-calibrate candidate filed)
- **Final TRI-1 verdict**: **CLEAN** (user ratified all 15 dispositions as drafted: 14 ACCEPTED-FIXED + 1 OVERRIDDEN; mechanical computation per /critique Step 4.5 — no ACCEPTED-PENDING, no ESCALATED present)

## Findings

### Blockers (must address before /build-slice)

#### B1: Proposed precedence `path → name → id` produces non-path output against the real `graphify-out/graph.json`

- **Claim under review**: design.md L10 + L102 + L113-118 — "`dict` input → preferred key precedence `path` → `name` → `id`; first non-empty string value wins" and "the fix changes ~6 LOC at the two call sites; the helper is ~10 LOC".
- **Issue**: Dimension 9 (audit-parse-rule empirical-execution discipline). Critic executed `$PY -m graphify blast-radius --file slice_queue_writer.py --graph graphify-out/graph.json --format json` against the live graph. Output:
  ```json
  [{"id": "slice_queue_writer_rationale_1", "label": "Parallel-slice queue writer (PSQ-1).  Per **PSQ-1** (`methodology-changelog.md", "type": "", "path": ""}]
  ```
  ALL `path` values are empty strings. Critic further inspected `graphify-out/graph.json` (2791 nodes): **zero nodes have a non-empty `path` field; zero nodes have a `name` key at all**. The actual node schema is `{id, label, file_type, source_file, source_location, community}` per `~/.claude/packages/graphify/graphify/extract.py:656-662`. The blast-radius emitter at `~/.claude/packages/graphify/graphify/__main__.py:1009-1014` does `"path": data.get("path", "")` — always empty in this repo.

  Applying the proposed precedence: `path` → empty (skipped); `name` → key absent (skipped); `id` → ALWAYS non-empty (e.g., `slice_queue_writer_rationale_1`, `slice_queue_writer`, `branch_workflow_audit_rationale_1`). The helper returns IDs, not paths. These IDs do NOT contain `{`, `'`, or `:` — so AC3's regex check passes — but the rendered `Blast-radius:` cells will list opaque internal identifiers instead of file paths. The slice's stated user-visible value (path-shaped tokens in `Blast-radius:` cells) is **not delivered**.

  Worse, `compute_parallel_safety` at `tools/slice_queue_writer.py:337-340` computes overlap as `candidate_files & blast` where `candidate_files` are real paths from `hint_files` (per `tools/slice_queue_writer.py:471-472`). If `blast` contains IDs like `slice_queue_writer_rationale_1`, the intersection with real-path candidate-files is empty — every candidate flags `NON-OVERLAPPING` regardless of true overlap. PSQ-1's core value proposition (overlap detection) silently remains broken.
- **Evidence**:
  - `graphify-out/graph.json` (executed): 0/2791 nodes carry non-empty `path`; 0 carry `name` key. Builder re-verified independently: `python -c "..."` reports key frequencies `{label:2791, file_type:2791, source_file:2791, source_location:2791, community:2791, id:2791}` — `path` and `name` absent from graph node schema.
  - `~/.claude/packages/graphify/graphify/extract.py:656-662` — `add_node()` constructs nodes WITHOUT a `path` key; only `{id, label, file_type, source_file, source_location}`
  - `~/.claude/packages/graphify/graphify/__main__.py:1013` — blast-radius output `"path": data.get("path", "")` always returns `""`
  - `tools/slice_queue_writer.py:471-472` + `:337-340` — overlap intersection requires path-shape symmetry between candidate `hint_files` and blast set
- **Proposed fix** (Critic options 1 + 2 merged): introduce a new helper `_build_id_to_path_map(graph_path: Path) -> dict[str, str]` that reads `graph.json` once and constructs `{node_id → repo-relative source_file}` for every node carrying both fields. Then `_node_to_path` resolves a node-dict's `id` against this map (the primary path); falls back to dict's own `path`/`name`/`source_file` field if path-shaped (forward-compat for future graphify versions emitting those keys); returns None for unresolvable nodes. Skip-on-None at the comprehension level. Empirical verification (Builder ran prototype): for input `slice_queue_writer.py`, graphify returns 1 node (`slice_queue_writer_rationale_1`) which resolves to `tools/slice_queue_writer.py` via id→source_file lookup. Strategy works against real data.
- **Builder draft**: **ACCEPTED-FIXED** at design.md `## Fix shape` redesign + mission-brief.md `## Acceptance criteria` AC#2 widened to four shapes. New helper `_build_id_to_path_map` added; `_node_to_path` simplified to id-lookup-then-defensive-fallback. Tests rewritten to use real graphify shape (B2 fix). Empirical re-verification ran against `graphify-out/graph.json` and confirmed the new precedence resolves to `tools/slice_queue_writer.py` (the expected path).

#### B2: Test mocks return a fictional graphify shape graphify never produces in this repo

- **Claim under review**: test fixture at `tests/bugs/test_psq_1_blast_radius_dict_leak.py:38-51` + design.md L130 — mock JSON contains `"path": "tools/slice_queue_writer.py"`.
- **Issue**: Dimension 2 (missing edge case: real-input shape) + Dimension 9 (APED-1). The mock fixture asserts a node-dict shape where `"path"` is non-empty and path-shaped. **Graphify in this repo NEVER emits this**: the actual schema is `{id, label, type:"", path:""}` (all `path` values empty per B1 evidence). The repro test, all four new unit tests, and the precedence pin all test a graphify output shape the integration target NEVER produces.

  Consequence: All five tests can be made to pass against the proposed `path → name → id` fix, while the LIVE graphify output (with empty `path`, no `name`, non-path `id`) silently degrades to ID-strings and AC3's `no-{':}` regex passes vacuously. The unit tests aren't pinning the actual defect class; they're pinning a hypothetical defect against a hypothetical graphify shape.
- **Evidence**: Same as B1 evidence (executed graphify blast-radius output + extract.py node-construction); `tests/bugs/test_psq_1_blast_radius_dict_leak.py:38-51` — mock fixture's `"path"` field has a path-shaped value, contradicting live behavior
- **Proposed fix**: Replace the /repro mock fixture's fictional `"path": "tools/..."` with the empirically-verified shape `{"id": "<id>", "label": "<label>", "type": "", "path": ""}`. The test asserts the result set contains the EXPECTED repo-relative source_file values that the id→source_file map resolves to. Add a fourth supplemental test for "list-of-dicts-with-EMPTY-path-and-no-name-and-non-path-id-but-with-id-mappable-via-graph" (THE actual current graphify shape). Tighten AC3 from "no `{':}` in the line" to a positive-shape check: every backtick-quoted token in Blast-radius cells contains a path separator (`/` or `\`) OR ends with `.py`/`.md`/`.json`/`.toml`/`.yaml`.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC#2 + design.md TF-1 supplement. /repro test fixture updated in same fix-block (TPHD-1 sub-mode (a) cross-file harmonization — rewriting the fixture is part of the design fix). New supplemental test `test_blast_radius_resolves_real_graphify_node_shape_via_id_lookup` added. AC3 test asserts positive path-shape via backtick-quoted-token regex.

### Majors (address this slice)

#### M1: AC3 integration test is a weak proxy — passes on the proposed fix's wrong output

- **Claim under review**: mission-brief AC#3 + design.md L134 — "asserts no `{`, `'`, or `:` character appears in any such line's value portion".
- **Issue**: Dimension 4 (under-engineering — AC has design element but the design element is insufficient to deliver the stated user value). The test's assertion grammar (no `{`, `'`, `:` chars) was reverse-engineered from the EXACT defect class (Python dict `repr()` shape). It is silent on every other corruption class that violates "path-shaped tokens". Specifically, opaque identifier strings like `slice_queue_writer_rationale_1` would pass the assertion while still being non-paths.
- **Evidence**: design.md L134 + B1 execution evidence
- **Proposed fix**: Tighten AC3's regex to a positive-shape check: each backtick-quoted token in the Blast-radius cell value matches `^[^\s\`]+(?:[/\\][^\s\`]+|\.(?:py|md|json|toml|yaml|txt))$` — i.e., contains a path separator OR ends with a known file extension. Reject any token that is a bare identifier.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC#3 (positive-shape regex; the assertion text in the integration test rewritten) + design.md TF-1 supplement table.

#### M2: Risk R-X2 mis-frames the silent-drop disposition

- **Claim under review**: design.md L145 R-X2 — "a graphify node with no `path`/`name`/`id` would be silently dropped from the result set... pathological-shape input that doesn't appear in the live `graphify-out/graph.json` today (all 2791 nodes carry an `id`)".
- **Issue**: Dimension 1 (unfounded assumption flipped — assumption *correct* that all nodes carry an `id`, but the conclusion is wrong). The Builder's framing assumes the `id` fallback is the correct safety net. Per B1, the `id` fallback is the FAILURE MODE: every node has an `id`, no node has a usable `path` → every node returns its ID-string → the result set is NEVER empty and the silent-drop branch is NEVER reached. The actual risk is the inverse: silent-PRODUCTION of wrong output, not silent-drop of empty output.
- **Evidence**: B1 + design.md L145
- **Proposed fix**: Rewrite R-X2: "Every live graphify node carries a non-empty `id` and an empty `path`; `name` key is absent. The id→source_file lookup map in `_build_id_to_path_map` carries the real path. R-X2 reframes to: 'a graphify node id absent from the graph-build's source_file map would be silently dropped' — true silent-drop edge case for genuinely-anomalous data; bounded by build-time-graph state."
- **Builder draft**: **ACCEPTED-FIXED** at design.md L145 (R-X2 fully rewritten in fix-block).

#### M3: Risk R-X3 understates the `:` collision class

- **Claim under review**: design.md L146 R-X3 — "an `id` like `module:function` (which doesn't occur in current graphify output but theoretically could) would trip the `:` check".
- **Issue**: Dimension 2 (missing edge cases). R-X3 only acknowledges class (a) IDs containing `:` (false-positive against AC3 regex). Class (b) IDs NOT containing `:` (false-negative masking the B1 defect) is invisible to the original AC3 regex but is the active defect class under the proposed fix.
- **Evidence**: design.md L146 + B1
- **Proposed fix**: Subsume R-X3 into M1's positive-shape check. With a positive-shape AC3 test, class (a) is correctly rejected (IDs with `:` lack path separators → caught), and class (b) is correctly rejected (IDs without `/` or file extension → caught).
- **Builder draft**: **ACCEPTED-FIXED** at design.md L146 (R-X3 collapsed into M1 fix; explicit cross-reference added).

#### M4: Multi-shape coverage AC#2 mis-aligned with actual graphify shape

- **Claim under review**: mission-brief AC#2 + design.md L132 — three shapes: list-of-strings (legacy), list-of-dicts-with-path-field (current), dict-with-nodes-keyed-list (line-250 path).
- **Issue**: Dimension 4 (under-engineering). Per B1, the **actual** "current" shape is list-of-dicts-with-EMPTY-path-field-and-no-name-key. The AC#2 enumeration calls the current shape "list-of-dicts-with-`path`-field (current/buggy)" but the live graphify output doesn't populate `path`. None of the three enumerated shapes covers the actual production reality.
- **Evidence**: B1 execution + mission-brief AC#2 + design.md L132
- **Proposed fix**: Add a FOURTH shape to AC#2 enumeration: "list-of-dicts-with-empty-`path`-and-no-`name`-and-non-path-`id`-but-with-`id`-mappable-via-graph-json's-`source_file` (the actual current graphify-in-this-repo shape)". Pin it with a test that uses a fixture matching the real graphify output literally + a fake graph.json. Verify the extractor produces path-shaped output via the id-lookup path.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md AC#2 (4-shape enumeration) + design.md TF-1 supplement (new test row).

#### M5: Mission-brief mis-attributes "PSQ-1's architectural premise is multi-session shared visibility per ADR-064 §Decision"

- **Claim under review**: mission-brief L5 — "PSQ-1 architectural premise is multi-session shared visibility per ADR-064".
- **Issue**: Dimension 1 (unfounded assumption — citation drift). ADR-064 §Decision is a comparison of disk-write vs in-memory vs SQLite vs distributed-lock. The phrase "durable across sessions" appears once as one pro of disk-write (line 23). ADR-064 §Decision does NOT establish "multi-session shared visibility" as the *premise* — that framing was post-hoc-introduced at slice-068 /critique-review. Builder confirmed by reading ADR-064 directly.
- **Evidence**: `architecture/decisions/ADR-064-mint-psq-1-parallel-slice-queue.md:23-29` — "durable across sessions" is one pro of the chosen option, NOT a premise/decision
- **Proposed fix**: Replace the citation "per ADR-064 §Decision" with "per ADR-064 §Decision option 1 'durable across sessions' rationale + backlog.md L564 PSQ-2-blocks framing". Or drop the citation and rely on the backlog.md self-citation.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md L5 (citation reframed to "ADR-064 §Decision option 1 'durable across sessions' rationale + diagnose-out/backlog.md SC-027 PSQ-2-blocks framing").

#### M6: LOC count drift — design.md states "~16 LOC delta" + "~10 LOC of new helper" but the helper as drafted is 14 LOC

- **Claim under review**: design.md L12 + L35 — "~16 LOC delta — one new private helper... + two call-site comprehension rewrites" and "helper is ~10 LOC of new module-private code".
- **Issue**: Dimension 9 (FBCD-1 sub-mode (a) cross-file consistency). Counted helper at design.md L87-106: 20 lines including docstring; ~14 LOC non-blank non-doc. Two call-site rewrites are 3 LOC each. Total delta closer to ~20-22 LOC. Per slice-069 aggregated lesson "count claims need hand-verification" (BC-PROJ-9 inventory-count class N=2 cumulative). With the B1 redesign adding `_build_id_to_path_map` (~15 LOC), the count is now ~35-40 LOC total — the original "~16 LOC" estimate is doubly wrong.
- **Evidence**: design.md L87-106 line counting + L12 + L35
- **Proposed fix**: Drop the precise LOC count. Replace with "small delta (one id-lookup helper + one path-extractor helper + two call-site comprehension rewrites — full source-level diff lands at /build-slice)".
- **Builder draft**: **ACCEPTED-FIXED** at design.md L12 + L35 (LOC numbers excised; structural description retained).

### Minors (log; address if cheap)

#### m1: Mid-slice smoke gate uses singular test name; AC#2 supplemental tests not part of smoke check

- **Claim under review**: mission-brief Mid-slice smoke gate L92 — only `test_blast_radius_returns_only_path_shaped_strings_from_node_list` runs at smoke; AC#3 integration test does not run until pre-finish.
- **Issue**: Per the M1 + B1 redesign, the AC#1 test passes on a precedence chain that produces the wrong output for AC#3. Surfacing AC#3 at smoke gate would catch B1-class silent-wrong-output earlier in the build. As written, smoke gate gives false confidence.
- **Proposed fix**: Add the AC#3 integration test to the smoke gate command list.
- **Builder draft**: **ACCEPTED-FIXED** at mission-brief.md Mid-slice smoke gate L91-93 (smoke gate command broadened to run all tests in `tests/bugs/test_psq_1_blast_radius_dict_leak.py`).

#### m2: WIRE-1 zero-row matrix referenced vs slice-069's; verify the same-shape claim against the actual slice-069 design.md

- **Claim under review**: design.md L59 — "same shape used by slice-069's zero-row matrix at slice-069 design.md".
- **Issue**: Cross-doc consistency check skipped.
- **Evidence**: Builder spot-checked `architecture/slices/archive/slice-069-track-vault-in-git/design.md:60-65` — uses header + separator only, identical shape. Reference is correct.
- **Builder draft**: **ACCEPTED-FIXED** (verification performed; no design.md change required — the reference is accurate as written).

#### m3: BCR-1 sentinel-count cross-doc parity

- **Claim under review**: mission-brief.md contains 4 occurrences of `**Closes:** SC-027` (one structural header + three quoted/inline references). BCR-1's `/reflect` logic looks for the literal `**Closes:** SC-` sentinel.
- **Issue**: Sanity check: does multiple-mention double-trigger the round-trip?
- **Evidence**: Builder read `~/.claude/skills/reflect/SKILL.md:59` (BCR-1 round-trip section). The prose explicitly states: "Multiple `**Addressed:**` lines under one candidate are valid (prior-slice double-shipment per slice-053 m5) — APPEND a new line below the existing one(s); NEVER replace." However, this is about /reflect's behavior on RE-RUN, not about multi-mention. Re-reading: BCR-1 triggers per SC-NNN per slice run, not per mention. /reflect would APPEND ONE `**Addressed:** ...` line per SC-NNN per run. No double-trigger risk.
- **Builder draft**: **OVERRIDDEN** — rationale: /reflect SKILL.md L59 prose confirms BCR-1 appends one Addressed line per closed candidate per slice run; multi-mention of `**Closes:** SC-027` in the SAME slice's mission-brief does NOT double-trigger. No mechanical defect; the multiple mentions are reasonable redundancy (one header + three contextual references in body/risks/etc.).

#### m4: Shippability row #70 prose contains incomplete clause "fix the row's slice-name placeholder when `/slice` confirms a different name"

- **Claim under review**: `architecture/shippability.md:79` row 70's Description cell — trailing clause is a stale TODO from when `/repro` wrote the placeholder row.
- **Issue**: Dimension 9 (FBCD-1 — residual TODO in shipped artifact). The slice name is now confirmed (`slice-070-fix-psq-1-blast-radius-dict-leak`); the placeholder admonition should be excised.
- **Proposed fix**: Excise the trailing "; fix the row's slice-name placeholder when `/slice` confirms a different name" clause.
- **Builder draft**: **ACCEPTED-FIXED** at shippability.md:79 (clause excised in same fix-block).

## Dimensions checked

- [x] **Unfounded assumptions** — B1 + B2 (graphify `path` field assumed populated; mock fixtures assert fictional shape), M5 (ADR-064 §Decision misquoted). Evidence basis: Wiegers — every claim traces to evidence; Critic executed graphify and read the ADR.
- [x] **Missing edge cases** — M3 (R-X3 enumeration incomplete on AC3 collision classes), M4 (missing the actual current-graphify shape from AC#2 enumeration). Standard heuristics applied: empty (the empty-path case), platform-specific (graphify's actual schema in this repo).
- [x] **Over-engineering** — none. The fix surface is appropriately small.
- [x] **Under-engineering** — B1 (proposed design does not deliver AC stated user value against real data), M1 (AC3 test too weak), M4 (AC#2 enumeration omits the actual current shape).
- [x] **Contract gaps** — none new. Internal contract correctly tightened post-redesign.
- [x] **Security** — none. Local-only helper writing a local-only Markdown file.
- [x] **Drift from vault** — M5 (ADR-064 citation). MEPD-1 EXCLUDE correctly applied.
- [x] **Web-known issues** — skipped — graphify is in-house, no external dependencies. WebSearch not invoked.
- [x] **Cross-cutting conformance** —
  - **APED-1** (audit-parse-rule empirical-execution): the Critic's textbook catch. Slice-069 lessons learned: methodology-revision slices need empirical execution; design-Critic + meta-Critic structurally cannot reach mechanic-specific bugs without it. This Critic EXECUTED graphify and discovered the wrong-output class. Builder re-verified with own prototype before drafting fix.
  - **PTFCD-1 / PTFFD-1**: TF-1 plan paths and functions all map to extant locations. Clean.
  - **FBCD-1**: M6 (LOC count drift) + m4 (shippability row 70 stale TODO).
  - **MEPD-1**: correctly EXCLUDE; precedent cited is accurate (N=10 cumulative inclusive of slice-070).
  - **SCPD-1**: m4 stale-clause excised.
  - **TPHD-1**: all test paths harmonized across mission-brief + design.md in same fix-block (sub-mode (a) cross-file harmonization for B1/B2/M1/M4 changes that touch both files).
  - **PCA-1**: not applicable (no skill or audit modification).

## Triage

**Triaged by**: user
**Date**: 2026-05-26
**Final verdict**: CLEAN

| ID | Severity | Disposition (Builder draft) | Rationale |
|----|----------|------------------------------|-----------|
| B1 | Blocker | ACCEPTED-FIXED | `_build_id_to_path_map` helper introduced; precedence redesigned; empirical re-verification by Builder confirms strategy produces `tools/slice_queue_writer.py` for the slice_queue_writer.py input |
| B2 | Blocker | ACCEPTED-FIXED | /repro fixture rewritten to real graphify shape; supplemental test for id-lookup path added |
| M1 | Major | ACCEPTED-FIXED | AC3 regex tightened to positive-shape check (backtick-quoted token must contain path separator OR known file extension) |
| M2 | Major | ACCEPTED-FIXED | R-X2 rewritten to acknowledge the inverted framing (silent-PRODUCTION-of-wrong-output, not silent-drop-of-empty-output) |
| M3 | Major | ACCEPTED-FIXED | R-X3 collapsed into M1's positive-shape regex; cross-reference added |
| M4 | Major | ACCEPTED-FIXED | AC#2 enumeration widened to 4 shapes including the actual current graphify-in-this-repo shape |
| M5 | Major | ACCEPTED-FIXED | ADR-064 citation reframed to "option 1 'durable across sessions' rationale + diagnose-out/backlog.md SC-027 PSQ-2-blocks framing" |
| M6 | Major | ACCEPTED-FIXED | LOC count excised; replaced with structural description |
| m1 | Minor | ACCEPTED-FIXED | Mid-slice smoke gate broadened to run full `tests/bugs/test_psq_1_blast_radius_dict_leak.py` (6 tests post-fix-block, including AC3 integration) |
| m2 | Minor | ACCEPTED-FIXED | Verified — slice-069 design.md L60-65 wiring matrix is the same header+separator-only shape; no action required |
| m3 | Minor | OVERRIDDEN | /reflect SKILL.md L59 prose confirms BCR-1 appends one `**Addressed:** ...` line per closed candidate per slice run; multi-mention of `**Closes:** SC-027` in the SAME slice's mission-brief does NOT double-trigger. No mechanical defect; the multiple mentions are reasonable redundancy. |
| m4 | Minor | ACCEPTED-FIXED | Excised placeholder clause from shippability.md:79 |
| M-add-1 | Major | ACCEPTED-FIXED | Meta-Critic missed-finding: design.md L66 cited STALE `path → name → id` precedence post-fix-block. Builder rewrote L66 to use the new id-via-map PRIMARY precedence in /critique-review fix block. |
| M-add-2 | Major | ACCEPTED-FIXED | Meta-Critic missed-finding: mission-brief.md L51 must-not-defer item #3 cited STALE `path → name → id → skip` precedence post-fix-block. Builder rewrote L51 in /critique-review fix block. |
| M-add-3 | Major | ACCEPTED-FIXED | Meta-Critic missed-finding: TPHD-1 sub-mode (a) cross-file harmonization INCOMPLETE — N=4 cumulative recurrence (slice-062/064/067/070). M-add-1 + M-add-2 swept in fix block; empirical post-sweep grep returns 0 stale-precedence matches. /critic-calibrate candidate filed for next calibration run (cross-slice prompt-update to instruct first Critics to perform a stale-anchor sweep after fix-block dispositions). |
