# Slice 999: example-test-first

**Mode**: Standard
**Risk tier**: medium
**Critic required**: true
**Estimated work**: 1 day
**Test-first**: true
**Risk retired**: R7

## Intent

Demonstrate test-first slice variant.

## Acceptance criteria

1. POST /receipts accepts JPEG/PNG/HEIC up to 10MB
2. Files >10MB return 413
3. Authorization rejects non-owners with 403

## Test-first plan

Per TF-1: each AC maps to one or more failing tests written BEFORE implementation.

| AC | Test type | Test path | Test function | Status |
|----|-----------|-----------|---------------|--------|
| 1 | integration | tests/api/test_receipts.py | test_upload_accepts_jpeg | PASSING |
| 1 | integration | tests/api/test_receipts.py | test_upload_accepts_heic | PASSING |
| 2 | integration | tests/api/test_receipts.py | test_upload_oversize_returns_413 | PASSING |
| 3 | integration | tests/api/test_receipts.py | test_upload_non_owner_returns_403 | PASSING |
