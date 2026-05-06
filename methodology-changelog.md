# AI SDLC Methodology Changelog

This file tracks behavior-changing rules in the AI SDLC pipeline. Each entry carries a **rule reference**, **defect class**, and **validation method**.

## Inclusion heuristic

> If a slice acceptable yesterday would be refused today (or vice versa), it's a changelog entry.

Typo and formatting edits don't qualify; behavior changes do. New skills, new gates, modified pre-finish checks, changed prompt structures for named subagents — these qualify. Doc clarifications that don't change behavior do not.

## How `/status` uses this file

This file is also installed at `~/.claude/methodology-changelog.md` so `/status` can surface the most recent dated entry as a Methodology section, regardless of which project the user is in.

When the file is missing (e.g., older install before this feature shipped), `/status` gracefully skips the Methodology section and optionally hints that re-running the install would surface methodology metadata.

## Format per entry

```markdown
## v<semver> — <YYYY-MM-DD>

<One-paragraph summary>

### Added | Changed | Retired

- **<RULE-ID> — <Rule name>**
  <Description of what this rule enforces and where>
  - **Rule reference**: <RULE-ID>
  - **Defect class**: <what bad behavior this prevents>
  - **Validation**: <how we verify the rule holds — pytest, structural grep, runtime gate, etc.>
```

Rules are identified by short IDs (e.g., `META-1`, `LINT-MOCK-1`, `WIRE-1`) for cross-reference from SKILL.md prose and from later changelog entries that supersede or refine.

---

## v0.9.0 — 2026-05-06

Adds the wiring matrix discipline (WIRE-1). Every new module introduced by a slice must declare its consumer (entry point + test) or carry an exemption with rationale. Audited at `/build-slice` pre-finish; format validation enforced in v1.

### Added

- **WIRE-1 — Wiring matrix discipline**
  Adds `tools/wiring_matrix_audit.py` — a markdown table parser + format validator for the wiring matrix in each slice's `design.md`. Updates `skills/design-slice/SKILL.md` to require a `## Wiring matrix` section in the design.md template (4 columns: New module | Consumer entry point | Consumer test | Exemption). Updates `skills/build-slice/SKILL.md` Step 6 (pre-finish gate) to run the audit and refuse on Important findings.

  The matrix's purpose is structural: every new module/file declares a consumer demand (entry point + test) — preventing dead-modules-with-green-tests where unit tests pass but no entry point ever imports the module. Per Freeman & Pryce (*Growing Object-Oriented Software*) — "consumer demand precedes producer build".

  Exemption mechanism: a row with `internal helper, no consumer demanded — rationale: <reason>` in the Exemption column declares an internal helper without a direct consumer. The audit requires the literal `rationale:` substring; bare exemptions without rationale are flagged as `missing-rationale`. Empty matrices (header + separator + zero data rows) are accepted — the slice introduced no new modules.

  NFR-1 carry-over: slices whose `mission-brief.md` mtime predates `_WIRE_1_RELEASE_DATE` (2026-05-06) are exempt automatically. The rule applies to slices authored on or after the rule's release. CLI flag `--no-carry-over` disables the exemption for testing / CI archive scans.

  CLI: `python -m tools.wiring_matrix_audit <slice-folder>` (auto-finds design.md inside) OR `python -m tools.wiring_matrix_audit <design.md>`. Options: `--json`, `--no-carry-over`. Exit codes: 0 clean (or carry-over exempt), 1 violations, 2 usage error.

  - **Rule reference**: WIRE-1
  - **Defect class**: Dead modules with green tests. A slice introduces a module (passes its own unit tests in isolation) but no entry point imports it — the module never runs in production. Without consumer-demand discipline, this drift is invisible at PR review and surfaces only when someone notices the module was never wired in. WIRE-1 catches it at design time by requiring the consumer to be declared upfront.
  - **Validation**: `tests/methodology/test_wiring_matrix_audit.py` — 11 tests covering: clean design (cells filled or rationalized exemption), missing-cells violation, missing-rationale violation, no-matrix violation, empty-matrix acceptance, missing design.md graceful handling, carry-over exemption with mtime, `--no-carry-over` flag override, missing-mission-brief means no carry-over claim, and skill-prose references in both `/design-slice` and `/build-slice`. Total methodology suite: 106 -> 117.

  Limitations (v1, documented in code):
  - **Format validation only**. A v2 will add existence/import audits: verify each Consumer entry point file exists in the repo, grep its contents for the named module's import + call site. The grep audit is the bigger structural value — without it, the matrix is a documentation discipline, not a refusal-on-dead-code mechanism.
  - **No multi-language module-name normalization**. Module names are treated as opaque strings; the audit doesn't validate Python dotted vs filesystem path conventions, TS module specifiers, or Go import paths.
  - **No test function existence check**. Consumer test cells like `tests/test_x.py::test_foo` are not split into file + function; only the surrounding format is validated. A v2 grep would also verify the function exists in the file.

---

## v0.8.0 — 2026-05-06

Adds Go support to the mock-budget linter (LINT-MOCK-3). Phase 3's mock-budget linter trio now covers Python, TypeScript/JavaScript, and Go.

### Added

- **LINT-MOCK-3 — Mock-budget linter (Go) — mock-budget rule v1**
  Extends `tools/mock_budget_lint.py` with Go support via the `tree_sitter` + `tree_sitter_go` packages (already in the shared venv). Detection covers any `call_expression` whose function name matches `^New(Mock|Fake|Stub|Spy)` — covering gomock-generated mocks (`mocks.NewMockUserService(ctrl)`), manual mocks (`NewMockHTTPClient()`), fakes (`fakes.NewFakeRepository()`), stubs, and spies. Test scopes are top-level `func TestXxx(t *testing.T)` declarations (with the `Test` + uppercase-letter convention to filter helpers like `Testing`) plus `t.Run("name", func ...)` subtest blocks. Mocks are attributed to the innermost containing scope. The dispatcher recognizes `.go` and routes to `_lint_go`. Updates `skills/build-slice/SKILL.md` to broaden the gate to "Python, TS/JS, and Go test files" with the LINT-MOCK-3 reference.

  Function declarations like `func NewMockUserService()` are correctly NOT counted — only `call_expression` nodes match, not `function_declaration` nodes (verified by a dedicated test).

  - **Rule reference**: LINT-MOCK-3
  - **Defect class**: Go test files were unlinted — gomock-generated mock proliferation in Go codebases (multiple `NewMockXxx(ctrl)` calls per `TestXxx` function) had no enforcement. Idiomatic Go testing with gomock makes it easy to bypass multiple internal interfaces in one test, which structurally bypasses the very integration seams the test pretends to verify. The Go extension closes that gap with the mock-budget rule (>1 mock per test = Important). Internal-mock classification is deferred to v2 — Go mocks are type-based without string targets, so accurate boundary classification requires import-aware analysis.
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` adds 5 new tests covering Go clean file, too-many mocks (`TestUserAndOrder` with 2 NewMock* calls), syntax error graceful handling, declaration-vs-call disambiguation rot guard (`func NewMockX()` definitions must NOT count), and `/build-slice` LINT-MOCK-3 reference. Total methodology suite: 101 -> 106.

  Limitations (v1, documented in code):
  - `var x MockUserService` declarations not yet counted (constructor pattern is dominant in Go test code)
  - `testify/mock.Mock` embedding not yet detected (would require type-graph walk; v2 candidate)
  - `gomock.NewController(t)` itself not counted (it's infra; the `NewMockXxx` calls that follow are the actual mocks)
  - `seam_allowlist` parameter accepted but ignored for `.go` files in v1; reserved for v2 internal-mock support

---

## v0.7.0 — 2026-05-06

Adds TypeScript / JavaScript support to the mock-budget linter (LINT-MOCK-2). Same lint contract as the Python implementation — single tool, multi-language dispatch by file extension.

### Added

- **LINT-MOCK-2 — Mock-budget linter (TypeScript / JavaScript)**
  Extends `tools/mock_budget_lint.py` with TypeScript and JavaScript support via the `tree_sitter` + `tree_sitter_typescript` packages (already in the shared venv per `~/.claude/CLAUDE.md`). Detection covers `vi.mock`, `vi.spyOn`, `vi.doMock` (vitest); `jest.mock`, `jest.spyOn`, `jest.doMock` (jest); `td.replace` (testdouble); and `sinon.stub`, `sinon.replace`, `sinon.spy`, `sinon.mock` (sinon). Test scopes are `it()` / `test()` calls (and their `.only` / `.skip` / `.concurrent` / `.each` / `.todo` / `.fails` variants); mocks are attributed to the innermost containing scope. The TS boundary defaults (`_TS_BOUNDARY_DEFAULTS`) cover HTTP (axios, node-fetch, got, ky, undici), Node built-ins (`node:fs`, `fs`, `node:http`, `node:https`, `node:child_process`, etc.), databases (pg, mysql2, mongodb, mongoose, redis, prisma, knex, typeorm), cloud SDKs (`@aws-sdk`, `@google-cloud`, stripe, `@anthropic-ai/sdk`, openai, `@azure`), and email/messaging (nodemailer, kafkajs). Scoped npm packages (e.g., `@aws-sdk/client-s3`) match at the scope level. Relative imports (`./...`, `../...`, `/...`) are never boundaries.

  Refactor: the previous `lint_file` (Python-only) is renamed to `_lint_python`; a new `lint_file` dispatcher routes by file extension (`.py` -> `_lint_python`; `.ts` / `.tsx` / `.js` / `.jsx` / `.mts` / `.cts` -> `_lint_typescript`). Unsupported extensions return a `parse-error` finding rather than crashing — runners can pass any file path safely.

  Updates `skills/build-slice/SKILL.md` to broaden the LINT-MOCK gate to "Python and TS/JS test files" and adds the LINT-MOCK-2 rule reference.

  - **Rule reference**: LINT-MOCK-2
  - **Defect class**: TS test files were unlinted — internal-mock proliferation in TS codebases (`vi.mock('./services/user-service')`, `jest.mock('./api/receipts')`) had no enforcement. AI-generated TS tests gravitate toward mocking everything internal because mocks are syntactically easier than fixtures; without lint, this drift is invisible at PR review and surfaces only when production fails on the unmocked code path. The TS extension closes that gap with the same contract as the Python linter (mock budget + boundary check + seam-allowlist escalation).
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` adds 9 new tests covering TS clean file, too-many mocks, internal-target, seam-with-allowlist, seam-without-allowlist, syntax error, boundary defaults coverage sanity, unsupported-extension graceful handling, and `/build-slice` LINT-MOCK-2 reference. Total methodology suite: 92 -> 101.

  Limitations (v1, documented in code): module-level `vi.mock` / `jest.mock` calls (hoisted; apply to all tests in the file) are not attributed to any specific test's count; only mocks inside the `it()` / `test()` body count. `beforeEach` / `afterEach` mocks are similarly not attributed. These are known gaps; a v2 may track module-level mocks as an implicit per-test contribution.

---

## v0.6.0 — 2026-05-06

Adds the Python mock-budget linter (LINT-MOCK-1) — the first AI SDLC rule that ships executable code rather than markdown-only discipline. Implements TDD-2 enforcement (≤1 mock per test, only at external boundaries) and integrates as a `/build-slice` pre-finish gate.

### Added

- **LINT-MOCK-1 — Mock-budget linter (Python)**
  Adds `tools/mock_budget_lint.py` — an AST-based linter for Python test files. Detects (1) test functions with >1 mock invocation (`mock-budget` violation, severity Important) and (2) tests that mock targets outside the external-boundary allowlist (`internal-mock` violation, severity Important; escalated to Critical if target is in `architecture/.cross-chunk-seams`). The boundary allowlist (`_BOUNDARY_DEFAULTS`) covers HTTP/networking, OS/process, filesystem, databases, cloud SDKs (boto3/google/stripe/anthropic/openai/azure), email/messaging, SSH, and time. Detection covers `@patch`, `@patch.object`, `@mock.patch` decorators and `patch(...)`, `mocker.patch(...)`, `mocker.spy(...)`, `mocker.patch.object(...)` inline calls. Integrated into `skills/build-slice/SKILL.md` Step 6 (pre-finish gate): Critical findings block; Important surface to user (Standard/Minimal) or block (Heavy with `--strict`). CLI: `python -m tools.mock_budget_lint <files...> [--seam-allowlist <path>] [--strict] [--json]`. Exit codes: 0 clean, 1 Critical present, 2 usage error.
  - **Rule reference**: LINT-MOCK-1
  - **Defect class**: Internal-mock proliferation hides integration seams. A test that mocks `UserService` and asserts behavior against the mock is verifying nothing real — the seam the mock pretends to verify is the seam the test silently bypasses (Freeman & Pryce GOOS — protocol drift). Mock-budget violations (>1 per test) compound this: each additional mock disconnects the test further from any single behavior the system actually exhibits. Without lint enforcement, this drift is invisible at PR review and only surfaces in production when the unmocked code path fails.
  - **Validation**: `tests/methodology/test_mock_budget_lint.py` — 12 tests over 5 fixtures (`tests/methodology/fixtures/mock_budget_*.py`): clean file, too-many-mocks, internal-class, seam-with-allowlist, seam-without-allowlist, syntax error, missing file, multi-file aggregation, allowlist file format (comments + blanks + trailing whitespace), missing allowlist file, boundary-defaults coverage sanity, `/build-slice` integration prose pin. Total methodology suite: 80 → 92.

### Changed

- **`pytest.ini`** — added `pythonpath = .` so the test suite can import `tools.mock_budget_lint` from anywhere under `tests/`. No effect on existing tests.

---

## v0.5.0 — 2026-05-06

Adds two improvements: per-pass model assignment for `/diagnose` (COST-1 extension), and explicit critic-calibrate cadence enforcement in `/status` (CAL-1).

### Added

- **COST-1.1 — Per-pass model assignment for /diagnose**
  Adds a Model column to the Step 5 dispatch table in `skills/diagnose/SKILL.md` specifying per-pass model based on cognitive shape: Sonnet for the 5 extraction-shaped passes (03a dead-code, 03c size-outliers, 03f layering, 03g dead-config, 03h test-coverage — reachability + grep + classification work), Opus for the 5 reasoning-shaped passes (01 intent, 02 architecture, 03b duplicates, 03d half-wired, 03e contradictions — synthesis + judgment + cross-module analysis). HTML assembly remains pure Python (no model). Step 6.5 narrator stays Opus. Pass 04-ai-bloat is dispatched in Step 6 separately and remains on the main-thread default.
  - **Rule reference**: COST-1.1 (extension of COST-1 to /diagnose passes)
  - **Defect class**: All 11 /diagnose passes running on the same model wastes Opus budget on extraction-shaped work. The cognitive shape varies — graphify reachable + grep cross-reference is Sonnet's job; semantic equivalence judging across modules is Opus's. A flat model assignment burns 5-10x cost on the extraction passes for no quality difference.
  - **Validation**: `tests/methodology/test_diagnose_pass_models.py` parametrizes over the 10 passes (excluding 04-ai-bloat) and verifies each row in Step 5 names the assigned model. Plus sanity checks: ≥5 extraction passes on Sonnet (rot guard against "everything on Opus"), ≥5 reasoning passes on Opus (rot guard against "everything on Sonnet to save more"), and a `COST-1.1` rule reference for traceability.

- **CAL-1 — Critic-calibrate cadence enforcement in /status**
  Adds explicit four-state cadence categorization to `skills/status/SKILL.md` Step 2: **within window** (0-9 slices), **approaching** (10-14), ⚠️ **recommended** (15-20), ⚠️⚠️ **overdue** (>20). When state is overdue, the calibration flag surfaces as the top line of "Recommended next action" in Step 3 output, overriding other suggestions until calibration runs. The check honors the deferred-first-run rule: empty calibration log + <10 archived slices = no warning, just "first calibration deferred until 10 slices accumulate".
  - **Rule reference**: CAL-1
  - **Defect class**: The "every 10-20 slices" cadence in `/critic-calibrate` was advisory; the previous `/status` had a single `If >15 slices: ⚠️ suggest running` line buried in metrics. Without explicit cadence enforcement, projects let calibration slip past 25, 30, 50 slices — at which point Critic calibration drift has accumulated and missed-pattern data is too noisy to mine effectively. The single-emoji warning was easy to miss; the double-emoji overdue escalation + override of next-action recommendations makes it actionable.
  - **Validation**: `tests/methodology/test_status_cadence_enforcement.py` verifies the SKILL.md prose contains the four cadence categories (within / approaching / recommended / overdue), the literal threshold numbers (10-20), the deferred-first-run language, override semantics for the overdue state, the double-emoji escalation pattern (⚠️⚠️), and a `CAL-1` rule reference.

---

## v0.4.0 — 2026-05-06

Adds cost-optimized model selection (COST-1). Three skills now explicitly dispatch their template-filling and rendering work to a Haiku subagent rather than running entirely on the main thread's model.

### Added

- **COST-1 — Cost-optimized model selection (Haiku-dispatched skills)**
  Adds explicit Haiku dispatch directives to `skills/commit-slice/SKILL.md` (Step 4 — commit message generation), `skills/status/SKILL.md` (Step 3 — summary rendering for default and brief modes), and `skills/archive/SKILL.md` (Step 3 — `slices/_index.md` regeneration; covers Step 4 archive catalog regeneration as well). The pattern: main thread gathers structured inputs (file reads + metric computation), then dispatches the formatting/rendering work to a `general-purpose` subagent with `model: haiku`. Quality is unchanged because the dispatched work is template-filling, not reasoning or synthesis — the cognitive demand is filling slots from a structured input dict, which Haiku does in a fraction of Opus's time and cost.
  - **Rule reference**: COST-1
  - **Defect class**: Skills running on the user's globally-set model (typically Opus) for work that has no reasoning component. `/commit-slice` fills a conventional-commit template from a structured dict — that's Haiku's shape, not Opus's. Running it on Opus burns ~5-10x cost for no quality difference. Same logic applies to `/status` (rendering metrics into a summary) and `/archive --index-only` (assembling tables from folder reads). Without explicit dispatch directives in each SKILL.md, the optimization sits unused — the executor doesn't know to delegate.
  - **Validation**: `tests/methodology/test_skill_model_dispatch.py` parametrizes over the three skills and verifies each SKILL.md contains (1) an explicit `model: haiku` directive, (2) a `subagent_type: "general-purpose"` reference, (3) a "Why Haiku" rationale section so future maintainers understand the cognitive-shape analysis, and (4) a `COST-1` rule reference for cross-link to the changelog. Skills missing any marker fail the test, which is the rot guard against future "to be safe, use Opus" reverts.

---

## v0.3.0 — 2026-05-06

Adds the named-subagent authoring guide and frontmatter conformance tests. New named subagents must conform to the documented frontmatter shape, tool-selection rules, and prompt structure conventions. Existing agents are pinned by static checks.

### Added

- **META-3 — Named-subagent authoring guide and frontmatter conformance**
  Adds `agents/AUTHORING.md` documenting when to use named subagents (vs forks vs general-purpose dispatch), the required frontmatter shape (`name`, `description`, `tools`, `model`), tool-selection rules (read-only roles MUST NOT have write tools), prompt structure conventions, calibration-awareness pattern, and self-test expectations. Adds `tests/methodology/test_agent_frontmatter.py` enforcing frontmatter conformance for every `agents/*.md` file (except `AUTHORING.md` itself), parametrized so new agents are checked automatically. Updates `README.md` to reference the new files.
  - **Rule reference**: META-3
  - **Defect class**: Future named subagents drift from established conventions (missing fields, mismatched name/filename, write tools granted to review roles, models picked by performance preference rather than cognitive demand) without an authoring guide. Drift compounds and erodes the load-bearing isolation property of named subagents — the Critic that becomes a rubber stamp because someone added `Write` to its tools and a "do helpful suggestions" instruction.
  - **Validation**: `tests/methodology/test_agent_frontmatter.py` runs as part of the methodology test suite. Tests verify (1) at-least-one named agent exists, (2) required-fields presence per agent, (3) name-matches-filename per agent, (4) model in allowed set per agent, (5) tools-non-empty per agent, (6) description substantive (>50 chars) per agent. Plus `test_authoring_guide_exists_and_pins_canonical_sections` pins canonical section headers in `AUTHORING.md` itself so the guide can't be paraphrased away.

---

## v0.2.0 — 2026-05-06

Adds the methodology self-test harness. From this version on, every behavior-changing rule introduced in a slice MUST have a corresponding pytest test that pins its prose, so silent paraphrase rot is prevented.

### Added

- **META-2 — Methodology self-test harness**
  Adds `tests/methodology/` directory with pytest harness and ~20 baseline tests covering load-bearing prose across `agents/critique.md`, `agents/critic-calibrate.md`, `agents/diagnose-narrator.md`, `agents/field-recon.md`, `skills/slice/SKILL.md`, `skills/build-slice/SKILL.md`, `skills/validate-slice/SKILL.md`, `skills/reflect/SKILL.md`, `skills/diagnose/SKILL.md`, plus self-tests for `methodology-changelog.md` (version sync, dated entries, rule-reference presence). Adds `pytest.ini` at repo root configuring `testpaths = tests`. Adds `tests/README.md` documenting setup, run, and how to add tests for new rules. CI hook documented (opt-in; no `.github/workflows/` shipped).
  - **Rule reference**: META-2
  - **Defect class**: Silent prose drift in load-bearing SKILL.md and agent files. A Critic prompt that reads "be thoughtful" produces different behavior than one that reads "assume the design is wrong until proven right" — and without enforcement, paraphrase rot is invisible until the Critic has degraded into a rubber stamp.
  - **Validation**: `pytest tests/methodology/ -v` runs cleanly and reports every test passing. `tests/methodology/test_methodology_changelog.py` validates VERSION ↔ changelog version sync and rule-reference presence per entry. Each subsequent slice that introduces a load-bearing rule MUST add a self-test for it; failure to do so is a violation of META-2 surfaced in `/critique`.

---

## v0.1.0 — 2026-05-06

Initial release of methodology versioning and changelog tracking.

### Added

- **META-1 — Methodology versioning + changelog**
  Adds `VERSION` file at the AI SDLC repo root tracking methodology semver. Adds `methodology-changelog.md` recording each behavior-changing rule with rule reference + defect class + validation method. `INSTALL.md` copies both to `~/.claude/` so they're discoverable from any project. `/status` reads `~/.claude/methodology-changelog.md` (if present) and surfaces the most recent dated entry as a Methodology section in default and full modes; the brief mode shows version on the header line.
  - **Rule reference**: META-1
  - **Defect class**: Methodology evolution had no audit trail. Users couldn't tell what changed between AI SDLC updates, why a new rule existed, or whether the methodology had drifted since they last looked. Without an audit trail, refinements get lost and speculative additions accumulate without scrutiny.
  - **Validation**: `VERSION` file exists at repo root with a semver string. `methodology-changelog.md` exists at repo root and has at least one dated entry. The most-recent entry's version matches `VERSION`. `INSTALL.md` Step 4 verifies both are copied to `~/.claude/`. `/status` reads the file gracefully (no error if missing) and surfaces version + most-recent rule.
