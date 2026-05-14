// Backend domain type definitions.
// Independent definition of NodeType — backend tier.
// LAYER-EVID-1 regression fixture: parallel_types_no_import.
// Frontend has its OWN parallel definition at frontend/lib/types.ts
// (same enum name, different module) — graphify may collapse these
// into a single phantom-edge node, but no textual frontend->backend
// import statement exists.

export enum NodeType {
    A = "A",
    B = "B",
    C = "C",
}

export enum TaskType {
    PENDING = "PENDING",
    DONE = "DONE",
}

export enum AssigneeType {
    USER = "USER",
    GROUP = "GROUP",
}
