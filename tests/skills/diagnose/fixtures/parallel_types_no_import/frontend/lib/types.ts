// Frontend domain type definitions.
// PARALLEL DEFINITION of NodeType / TaskType / AssigneeType — frontend tier.
// Hand-maintained copy of backend names; independent identity.
// graphify may collapse this into the same symbol node as
// src/backend/types.ts (the witnessed F-LAYER-bca9c001 failure mode).

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
