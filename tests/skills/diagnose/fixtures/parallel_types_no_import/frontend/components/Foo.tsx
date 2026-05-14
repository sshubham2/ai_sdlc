// Frontend component importing the LOCAL frontend types — not cross-tier.
// All NodeType references resolve to frontend/lib/types.ts via the
// frontend-rooted @/* alias from tsconfig.json (paths: { "@/*": ["./*"] }
// rooted at frontend/), which physically cannot reach src/backend/.
import { NodeType, TaskType } from "@/lib/types";

// Multi-line named import — must also resolve to frontend-local.
import {
    AssigneeType,
} from "@/lib/types";

// Default + named hybrid (from frontend-local helpers file).
import type { NodeType as NT } from "@/lib/types";

export function Foo(props: { node: NodeType; task: TaskType; assignee: AssigneeType }) {
    const _nt: NT = props.node;
    return { node: props.node, task: props.task, assignee: props.assignee, copy: _nt };
}
