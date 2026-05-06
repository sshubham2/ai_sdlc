# Slice 001: example-pre-finish-pending

**Mode**: Standard
**Walking-skeleton**: true

## Intent

Some layers still PENDING — strict-pre-finish must refuse.

## Acceptance criteria

1. Some criterion

## Architectural layers exercised

| # | Layer | Component | Verification | Status |
|---|-------|-----------|--------------|--------|
| 1 | Frontend | src/web/HomePage.tsx | page loads | EXERCISED |
| 2 | API | src/api/server.py | curl returns 200 | PENDING |
| 3 | Persistence | src/db/health_log | row inserted | PENDING |
