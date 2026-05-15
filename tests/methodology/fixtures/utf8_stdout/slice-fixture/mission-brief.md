# Slice 999: synthetic-fixture-for-utf8-stdout-regression

**Mode**: Standard
**Estimated work**: not applicable (fixture)
**Risk retired**: not applicable (fixture)
**Test-first**: true
**Walking-skeleton**: false
**Exploratory-charter**: false

## Intent

Synthetic fixture for `tests/methodology/test_utf8_stdout_regression.py`. Contains U+2192 (`→`) in TF-1 row status transitions so that audit-tools that interpolate fixture content into their stdout will exercise the cp1252-vs-UTF-8 encoding path.

## Acceptance criteria

1. The fixture mission-brief contains U+2192 `→` (regression arrow) and U+2014 `—` (em-dash) in interpolatable surfaces.
2. The TF-1 plan table is parseable by `tools.test_first_audit`.
3. The wiring matrix table in design.md is parseable by `tools.wiring_matrix_audit`.

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | synthetic | tests/methodology/fixtures/utf8_stdout/slice-fixture/mission-brief.md | fixture_arrow_present (PENDING → WRITTEN-FAILING → PASSING) | PASSING |
| 2 | synthetic | tests/methodology/fixtures/utf8_stdout/slice-fixture/mission-brief.md | fixture_tf_plan_parseable | PASSING |
| 3 | synthetic | tests/methodology/fixtures/utf8_stdout/slice-fixture/design.md | fixture_wiring_matrix_parseable | PASSING |

## Verification plan

| # | Criterion | How we verify |
|---|-----------|---------------|
| 1 | Arrows present | Grep for U+2192 in this file |
| 2 | TF-1 table parseable | `tools.test_first_audit` runs without parser error |
| 3 | Wiring matrix parseable | `tools.wiring_matrix_audit` runs without parser error |

## Must-not-defer

- [ ] arrow U+2192 actually present in interpolatable content
- [ ] em-dash U+2014 actually present in interpolatable content

## Out of scope

- Real slice work — this is a synthetic fixture for testing.

## Dependencies

- None — synthetic fixture is self-contained.

## Mid-slice smoke gate

Not applicable (fixture).

## Pre-finish gate

- [ ] All ACs PASS at fixture creation
