# Design: Slice 023 add-receipt-upload (fixture)

**Date**: 2026-04-19
**Mode**: Standard

## What's new

- src/services/storage.py — receipt persistence
- src/utils/exif.py — EXIF orientation normalization
- src/utils/_path.py — path manipulation helper

## Wiring matrix

Per WIRE-1: every new module declares its consumer entry point + test, or carries an exemption with rationale.

| New module | Consumer entry point | Consumer test | Exemption |
|------------|---------------------|---------------|-----------|
| `src/services/storage.py` | `src/api/receipts.py` | `tests/test_receipt_upload.py::test_upload_persists` | — |
| `src/utils/exif.py` | `src/services/storage.py` | `tests/test_receipt_upload.py::test_exif_orientation_normalized` | — |
| `src/utils/_path.py` | — | — | `internal helper, no consumer demanded — rationale: shared by other _utils modules; will gain consumer in slice-024` |
