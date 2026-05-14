// Frontend component with a REAL cross-tier import.
// Imports the BACKEND types via relative path that reaches into src/.
// LAYER-EVID-1 must NOT suppress this true-positive HIGH boundary finding.
import { NodeType } from "../../src/backend/types";

// Multi-line variant — also a real cross-tier import.
import {
    TaskType,
} from "../../src/backend/types";

// Side-effect import — also cross-tier.
import "../../src/backend/types";

// Re-export — semantically a boundary-crossing import.
export { TaskType as ReExportedTaskType } from "../../src/backend/types";

export function Bar(props: { node: NodeType; task: TaskType }) {
    return props;
}
