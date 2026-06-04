# Critique: Slice 112 make-prose-vault-location-agnostic

**Critic reviewed**: mission-brief.md, design.md, ADR-105, project-frame.md, cross-slice action points; grounded against `tools/vault_flip_prose_inventory.py`, `tests/methodology/test_vault_flip_prose_inventory.py`, `tests/methodology/test_vault_flip_op_gate.py`, `tools/_vault_paths.py`, the OSDG-1/CAD-1 drift tests, `test_bcr_1_backlog_round_trip.py`, ADR-085/090, and the live tool output on the real corpus.
**Date**: 2026-06-04
**Result**: BLOCKED (Critic recommendation; final verdict computed from ratified dispositions at Triage)

All 10 findings independently re-verified by the Builder against the live code (the verification batch is recorded in the build-log / conversation): B1 slice:249,264,267,268; B2 `_skill_of`→None for CLAUDE.md+agents (lines 473/515 — neither is op-gate-scanned); B3 `test_bcr_1_backlog_round_trip.py:108,186`; B4 two `313` rows in shippability; B5 zero `diagnose-out` seam in `_vault_paths.py`; M1 slice:250,430,475. **Every finding is VALID.**

## Summary
The `<vault>` convention + inventory-enforcement design are sound in the abstract, but (1) the placeholder is **not flip-neutral for the four `<wt_path>/architecture/…` composed paths** in `skills/slice/SKILL.md` (B1); (2) converting the skill files **breaks three already-green pinned suites** — the op-gate `--strict` floor + allowlist (B2), the BCR-1 literal anchor (B3), and the shippability "313" narrative fan-out (B4); (3) the `<diagnose-out>` token has **no production resolution seam** (B5). Notably **B1, B2, B3, M1 are ALL confined to the two skill files** (`slice`/`reflect`) — removing skill conversion from the pilot sidesteps all four. The core-convention findings (B5, M2, M3, B4) apply regardless.

## Findings

### Blockers (must address before /build-slice)

#### B1: `<vault>` is not flip-neutral for the four `<wt_path>/architecture/…` composed paths — the core AC4 claim fails for them
- **Claim under review**: design.md §Contracts "default → `architecture/` ⇒ no pre-flip behaviour change … resolves to the external store post-flip with zero further prose edits"; AC4.
- **Issue**: `skills/slice/SKILL.md:249,264,267,268` contain `<wt_path>/architecture/slices/slice-NNN-<name>/…`. `<vault>` resolves to the **full vault root** — today relative `Path("architecture")`, but post-flip an **absolute external path** (ADR-085:17,49 "no per-worktree `architecture/` once shared"). `<wt_path>/<vault>/…` resolves correctly pre-flip but **nonsensically post-flip** (worktree prefix + absolute path). These sites need a structural **prefix-drop** at flip, which a token substitution cannot encode → NOT flip-neutral; silently wrong at M4.
- **Evidence**: `skills/slice/SKILL.md:249,264,267,268`; `tools/_vault_paths.py:53,162,165`; ADR-085:17,49.
- **Proposed fix**: carve the `<wt_path>/architecture/…` paths out of conversion; disposition them as a distinct **structural-rewrite-at-flip** class (they genuinely ARE structural-rewrite, not flip-neutral). Document the class in ADR-105 for the flip/follow-on (which owns the active-folder R-32.a/.b disposition).
- **Builder draft**: **ACCEPTED-FIXED via pilot reduction** (recommended path B — see Triage fork): remove `skills/slice/SKILL.md` from the pilot entirely, so these sites are untouched this slice; document the worktree-composed `<wt_path>/architecture/…` *structural-rewrite-at-flip* carve-out class in ADR-105 so the skill-conversion follow-on handles it (prefix-drop, entangled with the R-32.a active-folder decision). [If user picks path A (keep skills): carve the 4 sites out in-place via `_DISPOSITION`.]

#### B2: Converting slice/reflect prose silently breaks `--op-gate --strict` (floor shrink) + the op-gate allowlist hash-keys → `test_real_corpus_op_gate_strict_clean` FAILS
- **Claim under review**: design.md §Components touched re-pins only `_BASELINE_SHA256`/`_CLASS_COUNT_FLOOR`/`EXPECTED_TOTAL`; AC4 "full suite passes."
- **Issue**: the op-gate (`tools/vault_flip_prose_inventory.py:501-565`) scans the SAME skill SKILL.md with the SAME `_MATCH_RE`. Converting `architecture/…`→`<vault>/…` makes op sinks invisible to `_MATCH_RE` (`_MATCH_RE.search("<vault>/risk-register.md")` → False). Vanishing live occurrences: `slice:249,264,264` (3× OP_DEFERRED), `slice:430` (OP_OUT_OF_SCOPE), `reflect:94` (OP_DEFERRED), `reflect:145,190,266` (OP_ROUTED). Drops OP_DEFERRED 11→~7 (floor=11, `:447`) + OP_OUT_OF_SCOPE below 23 (floor=23, `:449`) → `_op_floor_shrink` non-empty → `--op-gate --strict` exit 2 → `test_vault_flip_op_gate.py:192-194` FAILS. Separately `_OP_ALLOWLIST` (`:427-440`) is SHA-256(normalized-line)-keyed; converting slice:264 changes its hash → the allowlist entry stops matching.
- **Evidence**: `tools/...:446-450,427-440,530,536`; `tests/methodology/test_vault_flip_op_gate.py:192-194`.
- **Proposed fix**: add the op-gate to the re-pin set (re-derive OP_DEFERRED/OP_OUT_OF_SCOPE floors, re-hash the allowlist) via APED-1 against the converted corpus; a downward op-floor re-pin is a deliberate gate-loosening (AP-12) that must be planned, not discovered.
- **Builder draft**: **ACCEPTED-FIXED via pilot reduction** (path B): verified `_skill_of` returns None for CLAUDE.md + agents/critique.md (`tools/...:473`) → `scan_op_file` returns [] (`:515`) → **neither is op-gate-scanned**. So converting only CLAUDE.md + agents leaves the op-gate floors/allowlist **untouched** — B2 does not occur. The op-gate floor re-pin + allowlist re-hash become the explicit, owned deliverable of the skill-conversion follow-on. [If path A: design + execute the op-gate re-pin here per the Critic's fix.]

#### B3: Converting `diagnose-out/backlog.md` at slice:73 breaks the BCR-1 anchor test (literal-substring assertions) — AP-13 consumer-driven-contract
- **Claim under review**: design.md §Contracts lists carve-outs (INSTALL/README, definitional, historical anchors) but not the BCR-1 anchor; AC3 "every operational vault literal replaced."
- **Issue**: `test_bcr_1_backlog_round_trip.py:108` asserts literal `"diagnose-out/backlog.md" in section`; `:186` asserts the canonical phrase `"MUST consult diagnose-out/backlog.md as a mandatory candidate source when it exists"`. slice:73 (×2 `diagnose-out/backlog.md`) is in the pilot's count; converting it → both assertions FAIL (a by-name reader orphaned by a prose rename — AP-13).
- **Evidence**: `tests/methodology/test_bcr_1_backlog_round_trip.py:108,186`; CLAUDE.md:43 ("Pinned by `tests/methodology/test_bcr_1_backlog_round_trip.py`").
- **Proposed fix**: carve slice:73's anchor out (disposition it — load-bearing pinned anchor) OR repoint both BCR-1 assertions to the token IN THE SAME SLICE (AP-13). Recommend carve-out for the pilot.
- **Builder draft**: **ACCEPTED-FIXED via pilot reduction** (path B): slice/SKILL.md isn't converted this slice → the BCR-1 anchor is untouched. The skill-conversion follow-on that converts `slice` MUST repoint `test_bcr_1_backlog_round_trip.py`'s two literal assertions in the same slice (AP-13) — recorded as a follow-on obligation in the reflection. (Also reinforced by B5: `<diagnose-out>` is scoped out entirely this slice.) [Path A: carve slice:73 out via `_DISPOSITION`.]

#### B4: The downward re-pin is not fanned out to the two `architecture/shippability.md` rows that hard-state "313" — FBCD-1 sub-mode (c) / AP-10
- **Claim under review**: design.md §Components touched re-pins only the three module constants.
- **Issue**: "313" is hard-stated in shippability rows 113 ("**313**" / "313/0/0/0") and 117 ("318→313" / "the 313 re-pin reverts"). Per FBCD-1 (c) / AP-10 a counted-set cardinality change fans out to every hard-count literal repo-wide. Leaving them at "313" while the live total drops makes the catalog narrative false (the catalog is the single source of truth per CLAUDE.md §Vault discipline). The design's "~258" is also an estimate; the exact total must be APED-1-derived.
- **Evidence**: `architecture/shippability.md:122` (row 113), `:126` (row 117); 2× "313" confirmed.
- **Proposed fix**: add rows 113 + 117 to the re-pin worklist + mid-slice smoke; derive the exact new `EXPECTED_TOTAL` via `--json` against the converted corpus AFTER carve-outs settle.
- **Builder draft**: **ACCEPTED-FIXED**: enumerate the FULL move-together fan-out set in design.md — `_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`, shippability row 113, shippability row 117 (op-gate floors join the set ONLY under path A). Derive the EXACT total via `--json` at build (APED-1), not the "~258" estimate; drop the estimate from design.md.

#### B5: ADR-105 / AC1 specify a `<diagnose-out>` token but there is no `diagnose-out` seam in `_vault_paths.py` — its flip resolution is undefined
- **Claim under review**: AC1 "(and `<diagnose-out>/`) … resolution rule … mirrors `_vault_paths._resolve_vault_root`."
- **Issue**: `_vault_paths.py` defines `VAULT_ROOT` only (0 `diagnose-out` references confirmed). The stated rule resolves the vault, not `diagnose-out/`. ADR-085:17 says both relocate to `~/.aisdlc/<project>/` but the *relationship* (sibling? `<vault>/../diagnose-out`? own env var?) is undefined in code and unstated in ADR-105 → `<diagnose-out>/` is a token with no production resolution mirror; its flip-correctness (AC3/AC4) is unfounded.
- **Evidence**: `tools/_vault_paths.py` (no diagnose-out); ADR-085:17,53.
- **Proposed fix**: define `<diagnose-out>` resolution in ADR-105 (relative to the vault root, + note the production seam is a flip-slice deliverable) OR scope `<diagnose-out>` OUT of this pilot. Do not ship a token whose flip resolution is undefined.
- **Builder draft**: **ACCEPTED-FIXED**: scope the `<diagnose-out>` token **OUT** of this slice — mint ONLY `<vault>`. All `diagnose-out/` operational refs stay concrete (carve-out); the `<diagnose-out>` token + its seam are deferred to a slice that defines the seam (or the flip). Update ADR-105 + AC1 + the convention scope + the title/intent. (This also removes the diagnose-out conversions that would otherwise interact with B3.)

### Majors (address this slice)

#### M1: Converting `slice-queue.md` refs pre-decides its deliberately-undecided main-tree-pinned disposition (Dim-7 drift / project-frame direction-fit)
- **Claim under review**: AC3 "every operational vault literal replaced."
- **Issue**: slice:250,430,475 reference `architecture/slice-queue.md` — the main-tree coordination ledger ADR-090 pins to the **default branch**; slice-111's op-gate classes its writes `OP_OUT_OF_SCOPE` "undecided-flip-disposition" (`tools/...:403,493`), "the flip slice's call." Converting to `<vault>/slice-queue.md` asserts it relocates WITH the vault — pre-deciding a disposition the project deliberately deferred (AP-15: key on the real structural property; project-frame ATTACK-LENS pending `flip-vault-to-external-store`).
- **Evidence**: `skills/slice/SKILL.md:250,430,475`; `tools/...:403,493-494`; CLAUDE.md §BRANCH-3.
- **Proposed fix**: carve slice-queue.md refs out + disposition them (or a distinct token); do NOT convert until the flip slice decides its disposition. Add to ADR-105 carve-outs.
- **Builder draft**: **ACCEPTED-FIXED via pilot reduction** (path B): slice/SKILL.md isn't converted this slice → slice-queue.md refs untouched. Document `slice-queue.md` (undecided main-tree-pinned disposition, ADR-090 / slice-111 `_UNDECIDED_DISPOSITION`) as a named carve-out class in ADR-105 for the follow-on. [Path A: carve slice:250,430,475 (+515 prose) via `_DISPOSITION`.]

#### M2: Definitional `**Vault**: architecture/` at CLAUDE.md:5 is counted in the pilot 7 but its disposition is deferred to build — the pilot count + re-pin math are not deterministic at design time
- **Claim under review**: design.md "definitional default `architecture/` stays concrete (dispositioned/plain-prose) … finalized at build."
- **Issue**: CLAUDE.md:5 (`**Vault**: architecture/`) DEFINES what `<vault>` resolves to (converting it is circular); it must stay concrete. It is currently `rewrite-at-flip` inside the pilot's "CLAUDE.md (7)". Deferring its handling to build makes the AC3 count (7) + the re-pin total non-deterministic at design time; "strip backticks so it classifies doc-example" is a prose mutation to dodge a classifier (a smell).
- **Evidence**: CLAUDE.md:5; live class = `rewrite-at-flip`.
- **Proposed fix**: pin CLAUDE.md:5 via a `_DISPOSITION` 5-tuple entry to `historical-anchor`/`doc-example` (the mechanism for "resolve a curated literal WITHOUT editing prose", `tools/...:35-37`), NOT backtick-stripping; state the exact CLAUDE.md conversion count (6, not 7) → feed the deterministic re-pin total (B4).
- **Builder draft**: **ACCEPTED-FIXED**: disposition CLAUDE.md:5 (and any other definitional `architecture/` the new resolution-rule subsection itself introduces) via `_DISPOSITION` at design time → state CLAUDE.md conversions = 6 (not 7); no backtick-stripping. The resolution-rule block will state the default as the literal `architecture/` and that literal is dispositioned out of the gate.

#### M3: `_CONVERTED_FILES` (the headline AC2 deliverable): path-separator robustness + ratchet-independence vs. the existing baseline are under-specified
- **Claim under review**: AC2 "fails closed on any `rewrite-at-flip` literal in a `_CONVERTED_FILES` member … non-vacuous by mutation."
- **Issue**: (a) `Occurrence.path` is forward-slash relpath (`tools/...:272`), so `_CONVERTED_FILES` must store forward-slash relpaths; a `\`-keyed set silently never matches → vacuous green (the R-7 case AC2 claims to prevent). (b) The existing `--strict` already exits 2 on ANY baseline-multiset change; after re-pin, re-injecting a literal also trips baseline-drift — so the design must state what `_CONVERTED_FILES` catches that the re-pinned baseline does NOT: a converted file regressing EVEN IF the actor re-pins the baseline to "cover" it (a one-way ratchet INDEPENDENT of the re-pinnable baseline). The mutation proof must target that independence.
- **Evidence**: `tools/...:272,329-341`; design.md (no separator pin, no independence statement).
- **Proposed fix**: (1) pin `_CONVERTED_FILES` to forward-slash relpaths + a test that a `\`-form does NOT match (load-bearing, mirroring the column-offset test); (2) state the check is INDEPENDENT of the re-pinnable baseline; design the mutation proof to inject a literal into a converted file WITH a matching re-pinned baseline and assert exit 2 still fires.
- **Builder draft**: **ACCEPTED-FIXED**: update design.md §Components touched + AC2 — pin the forward-slash relpath convention (with the negative `\`-form test), state the one-way-ratchet independence explicitly, and specify the mutation proof targets independence (literal injected + baseline re-pinned to match → `_CONVERTED_FILES` still exit 2).

### Minors (log; address if cheap)

#### m1: agents/critique.md conversion makes the Critic self-resolve its own operational paths — note it; confirm CAD-1 stays green
- **Issue**: agents/critique.md:256,260 (+9 occurrences) are operational instructions the Critic executes; converting to `<vault>/` means the Critic substitutes at runtime. Acceptable (the documented LLM-resolution tax), but worth a one-line note. CAD-1 is EOL-agnostic content-equality — green IF both copies are byte-converted identically + the forward-sync is atomic-per-file (already a must-not-defer).
- **Evidence**: agents/critique.md:256,260,42,125,160,186-203; CAD-1 currently clean.
- **Builder draft**: **ACCEPTED-FIXED**: add a one-line note in design.md that converting agents/critique.md introduces a self-resolution requirement for the Critic's own read/write paths; mid-slice smoke confirms the forward-synced copy is byte-converted identically (CAD-1 equality).

#### m2: The bulk follow-on "~17 skills" is an estimate — pin the exact remainder via `--json`
- **Issue**: AC5 is satisfied by `--json`; the "~17" estimate shifts with the carve-outs. Cheap to make exact.
- **Builder draft**: **ACCEPTED-PENDING**: at the mid-slice smoke, capture the exact remainder count from `--json` and record it in the reflection deferred-note + slice-queue candidate; drop "~17".

## Dimensions checked
- [x] Unfounded assumptions — B5 (`<diagnose-out>` no seam), M2 (definitional disposition deferred), B1 (flip-neutrality assumed but false for `<wt_path>/architecture/…`).
- [x] Missing edge cases — M3(a) (Windows `\` vs `/` → vacuous green), B2 (op-gate `_MATCH_RE` non-match on converted tokens).
- [x] Over-engineering — M3(b) (`_CONVERTED_FILES` may be redundant with baseline-drift unless independence is stated).
- [x] Under-engineering — B2 (op-gate re-pin not designed), B3 (BCR-1 consumer not enumerated), B4 (shippability "313" not fanned out).
- [x] Contract gaps — B5 (`<diagnose-out>` flip contract undefined), M3 (separator + ratchet-independence unspecified).
- [x] Security — none (no auth/secret/injection/IDOR; pure prose-convention + read-only audit extension).
- [x] Drift from vault — M1 (slice-queue pre-decides ADR-090 undecided disposition), B1 (contradicts ADR-085 "no per-worktree architecture/ once shared").
- [x] Web-known issues — N/A (no external technology/API/platform/third-party dependency; pure internal prose-convention + in-house audit extension).
- [x] Cross-cutting conformance — B2 (AP-3/AP-12), B3/M1 (AP-13 consumer-driven-contract), B4 (FBCD-1 sub-mode (c)/AP-10), M3 (AP-5 non-vacuity / APED-1 exact counts).

## Triage

**Triaged by**: user
**Date**: 2026-06-04
**Final verdict**: NEEDS-FIXES

Reconciled across both Critic passes (first Critic + `/critique-review` meta-Critic, dual-review verdict EXTEND — all 10 first-Critic findings VALID, 0 suspicious, 2 missed). Pilot scope decided at TRI-1: **`CLAUDE.md` + a self-sufficient `agents/critique.md`** (the skill-file blockers B1/B2/B3/M1 deferred to a follow-on). The ACCEPTED-FIXED design edits are applied in this round (design.md + ADR-105 + mission-brief, this commit).

| ID | Severity | Disposition | Rationale |
|----|----------|-------------|-----------|
| B1 | Blocker | DEFERRED | Skill-conversion follow-on: the 4 `<wt_path>/architecture/…` composed paths are in `slice/SKILL.md`, not the pilot. Carve-out **class 4** (structural-rewrite-at-flip) is documented in ADR-105 and proven live in-pilot via the agent's `:260` active-folder carve-out. |
| B2 | Blocker | DEFERRED | Skill-conversion follow-on owns the op-gate floor re-pin + `_OP_ALLOWLIST` re-hash (a deliberate AP-12 gate-loosening). The pilot files are NOT op-gate-scanned (`_skill_of`→None, verified), so the op-gate is untouched here. |
| B3 | Blocker | DEFERRED | Skill-conversion follow-on: `slice:73`'s `diagnose-out/backlog.md` BCR-1 anchor is not in the pilot; the follow-on repoints `test_bcr_1_backlog_round_trip.py:108,186` in the SAME slice it converts `slice` (AP-13). Also moot here: `<diagnose-out>` is not minted (B5). |
| B4 | Blocker | ACCEPTED-FIXED | design.md §Components + ADR-105: the move-together re-pin set is enumerated (`_BASELINE_SHA256`, `_CLASS_COUNT_FLOOR[REWRITE_AT_FLIP]`, `EXPECTED_TOTAL`, shippability rows 113 + 117); exact total APED-1-derived via `--json` at build, no estimate. |
| B5 | Blocker | ACCEPTED-FIXED | ADR-105 + AC1: `<diagnose-out>` is NOT minted (no seam in `_vault_paths.py`); `diagnose-out/` stays concrete (carve-out class 7). |
| M1 | Major | DEFERRED | Skill-conversion follow-on: `slice-queue.md` refs are in `slice/SKILL.md`. Carve-out **class 6** documented in ADR-105 and proven live in-pilot via the agent's `:125` slice-queue carve-out. |
| M2 | Major | ACCEPTED-FIXED | ADR-105 class 2 + design.md: the definitional `architecture/` is plain-prose `doc-example` (deterministic at design time; CLAUDE.md conversion count APED-1-derived), NOT a `_DISPOSITION` line-key entry. |
| M3 | Major | ACCEPTED-FIXED | design.md §Components + AC2: `_CONVERTED_FILES` keyed forward-slash (negative `\`-test); the ratchet is INDEPENDENT of the re-pinnable baseline; the mutation-proof injects a literal AND re-pins the baseline → exit 2 survives. |
| m1 | Minor | ACCEPTED-FIXED | design.md §agents/critique.md: a one-line note that conversion makes the Critic self-resolve its own paths; CAD-1 stays green via byte-identical forward-sync. (The runtime-gap half was promoted to M-add-1.) |
| m2 | Minor | ACCEPTED-PENDING | At the mid-slice smoke, capture the EXACT not-yet-converted remainder via `--json` (drop "~17"/"~258") into the reflection deferred-note + slice-queue candidate. |
| M-add-1 | Major | ACCEPTED-FIXED | ADR-105 (resolver-context scope) + AC3 + Must-not-defer: `agents/critique.md` embeds a self-contained `<vault>` note so the Critic subagent (no CLAUDE.md) can resolve it (fix b). |
| M-add-2 | Major | ACCEPTED-FIXED | ADR-105 class 2 + M2 fix: the definitional literal is resolved by plain-prose `doc-example`, NOT the brittle line-keyed `_DISPOSITION`, so a future reword cannot silently re-red the gate. |
