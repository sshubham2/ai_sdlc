# Slice 011: example-pre-finish-pending

**Mode**: Standard
**Exploratory-charter**: true

## Intent

Mix of statuses — strict-pre-finish must refuse PENDING + IN-PROGRESS,
accept COMPLETED + DEFERRED.

## Acceptance criteria

1. Some criterion

## Exploratory test charter

| # | Mission | Timebox | Status | Findings |
|---|---------|---------|--------|----------|
| 1 | Explore upload edge cases | 60min | COMPLETED | findings noted |
| 2 | Explore concurrent | 45min | IN-PROGRESS | partial — session interrupted |
| 3 | Explore network failure | 30min | PENDING | — |
| 4 | Explore device fragmentation | 30min | DEFERRED | low priority; backlog item BL-021 |
