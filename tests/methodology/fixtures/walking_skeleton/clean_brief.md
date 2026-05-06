# Slice 001: walking-skeleton-foundation

**Mode**: Standard
**Risk tier**: high
**Critic required**: true
**Estimated work**: 1 day
**Walking-skeleton**: true
**Risk retired**: R1 (architecture-end-to-end uncertainty)

## Intent

Ship the thinnest end-to-end vertical that exercises every layer.

## Acceptance criteria

1. POST /healthz returns 200 with body `{"ok": true}`
2. Frontend home page renders the latest health status

## Architectural layers exercised

Per WS-1: every architectural layer this slice touches end-to-end.

| # | Layer | Component | Verification | Status |
|---|-------|-----------|--------------|--------|
| 1 | Frontend | src/web/HomePage.tsx | Page loads in real browser; spinner appears | EXERCISED |
| 2 | API gateway | src/api/server.py | curl GET /healthz returns 200 | EXERCISED |
| 3 | Business logic | src/services/health.py | health_check() returns OK in pytest | EXERCISED |
| 4 | Persistence | src/db/health_log table | row inserted on each /healthz call | EXERCISED |
| 5 | External | api.anthropic.com | trivial completions call returns 200 | EXERCISED |
