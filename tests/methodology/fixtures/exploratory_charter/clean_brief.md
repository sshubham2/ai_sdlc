# Slice 011: example-exploratory-clean

**Mode**: Standard
**Risk tier**: medium
**Critic required**: true
**Estimated work**: 1 day
**Exploratory-charter**: true

## Intent

Demonstrate exploratory testing charters with completed and deferred rows.

## Acceptance criteria

1. Some criterion

## Exploratory test charter

Per ETC-1: timeboxed exploratory testing charters; capture what surfaces.

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore HEIC upload edge cases using corrupted files to find error-handling gaps | 60min | COMPLETED | 2 issues — see findings.md: corrupted EXIF crashes thumbnail; truncated file gives 500 not 415 |
| 2 | Explore concurrent uploads using 5 simultaneous requests to find race conditions | 45min | COMPLETED | No race observed at 5 concurrent; revisit at 50+ if scale up planned |
| 3 | Explore upload over saturated network using throttled connection to find UX gaps | 60min | DEFERRED | Network throttling not feasible in current local setup; redirect to /risk-spike post-deploy |
