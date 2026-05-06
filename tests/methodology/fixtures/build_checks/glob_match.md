# Build checks (project-specific)

## Rules

## BC-PROJ-2 — Image uploads normalize EXIF orientation before storage

**Severity**: Important
**Applies to**: src/api/uploads/**, src/services/*upload*.py
**Promoted from**: slice-007-receipt-upload (2026-04-15) — recurring across slices 7, 12, 18
**Trigger keywords**: upload, image, jpeg, png, heic, exif

**Check**: Before persisting any uploaded image, the orientation EXIF tag must be normalized to physical pixel orientation (auto-rotate). Verify with a HEIC fixture that has orientation=6 — stored bytes must be rotated.

**Rationale**: iPhone HEIC files have EXIF orientation that JPEG decoders don't auto-apply. Without normalization, thumbnails appear sideways. Pattern recurred 3 times across receipt-upload, profile-photo, and document-scan slices.

**Validation hint**: `grep -r "Image.open" src/ | xargs grep -L "exif_transpose"` should return zero hits.
