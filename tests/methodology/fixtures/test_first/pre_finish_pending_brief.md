# Slice 999: example-pre-finish-pending

**Mode**: Standard
**Test-first**: true

## Intent

Some rows are PENDING / WRITTEN-FAILING — strict-pre-finish must refuse.

## Acceptance criteria

1. First criterion
2. Second criterion

## Test-first plan

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | unit | tests/test_x.py | test_one | PASSING |
| 2 | unit | tests/test_x.py | test_two | WRITTEN-FAILING |
| 2 | unit | tests/test_x.py | test_two_extra | PENDING |
