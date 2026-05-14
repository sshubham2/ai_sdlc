// Backend domain type definitions (same as parallel_types_no_import fixture).
// LAYER-EVID-1 regression fixture: parallel_types_real_import.
// In THIS fixture, frontend code actually imports from this backend file
// via relative path. The rule must NOT downgrade these true-positive
// cross-tier import findings.

export enum NodeType {
    A = "A",
    B = "B",
    C = "C",
}

export enum TaskType {
    PENDING = "PENDING",
    DONE = "DONE",
}
