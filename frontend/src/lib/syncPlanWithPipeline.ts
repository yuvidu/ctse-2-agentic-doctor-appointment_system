import { HEALTHCARE_PIPELINE_TASKS } from "@/data/healthcarePipelineTasks";
import type { PipelineResponse } from "@/types/pipeline";
import type { Task } from "@/types/planTask";

function cloneTasks(tasks: Task[]): Task[] {
  return structuredClone(tasks);
}

export function freshHealthcareTasks(): Task[] {
  return cloneTasks(HEALTHCARE_PIPELINE_TASKS);
}

/** Optimistic “running” state while waiting for the server. */
export function markPlanRunning(tasks: Task[]): Task[] {
  return tasks.map((t) => {
    if (t.id !== "1") {
      return { ...t, status: "pending", subtasks: t.subtasks.map((s) => ({ ...s, status: "pending" })) };
    }
    return {
      ...t,
      status: "in-progress",
      subtasks: t.subtasks.map((s, i) => ({
        ...s,
        status: i === 0 ? "in-progress" : "pending",
      })),
    };
  });
}

/** Reflect the final `run_system` payload on the checklist. */
export function applyPipelineResultToTasks(
  tasks: Task[],
  data: PipelineResponse,
): Task[] {
  const next = cloneTasks(tasks);
  const intentComplete = data.status === "complete";
  const hadIntentErrors =
    Array.isArray(data.errors) && data.errors.length > 0;

  const upsert = (id: string, updater: (t: Task) => Task) => {
    const i = next.findIndex((t) => t.id === id);
    if (i === -1) return;
    next[i] = updater(next[i]);
  };

  if (!intentComplete) {
    upsert("1", (t) => ({
      ...t,
      status: hadIntentErrors ? "need-help" : "in-progress",
      subtasks: t.subtasks.map((s, i) => ({
        ...s,
        status: i === 0 ? "completed" : i === 1 ? "in-progress" : "pending",
      })),
    }));
    for (const id of ["2", "3", "4"]) {
      upsert(id, (t) => ({
        ...t,
        status: "pending",
        subtasks: t.subtasks.map((s) => ({ ...s, status: "pending" })),
      }));
    }
    return next;
  }

  upsert("1", (t) => ({
    ...t,
    status: "completed",
    subtasks: t.subtasks.map((s) => ({ ...s, status: "completed" })),
  }));

  upsert("2", (t) => ({
    ...t,
    status: "completed",
    subtasks: t.subtasks.map((s) => ({ ...s, status: "completed" })),
  }));

  const slotCount =
    (data.available_slots?.length ?? 0) ||
    (data.availability?.available_slots?.length ?? 0);
  const availErr =
    Array.isArray(data.availability_errors) &&
    data.availability_errors.length > 0;

  if (availErr) {
    upsert("3", (t) => ({
      ...t,
      status: "need-help",
      subtasks: t.subtasks.map((s) => ({ ...s, status: "need-help" })),
    }));
    upsert("4", (t) => ({
      ...t,
      status: "pending",
      subtasks: t.subtasks.map((s) => ({ ...s, status: "pending" })),
    }));
    return next;
  }

  upsert("3", (t) => ({
    ...t,
    status: "completed",
    subtasks: t.subtasks.map((s) => ({
      ...s,
      status: "completed",
    })),
  }));

  if (slotCount === 0) {
    upsert("3", (t) => ({
      ...t,
      subtasks: t.subtasks.map((s) =>
        s.id === "3.2" ? { ...s, status: "need-help" } : { ...s, status: "completed" },
      ),
    }));
  }

  upsert("4", (t) => ({
    ...t,
    status: slotCount > 0 ? "completed" : "in-progress",
    subtasks: t.subtasks.map((s) => ({
      ...s,
      status: slotCount > 0 ? "completed" : "pending",
    })),
  }));

  const isConfirmed = data.status === "confirmed";
  const isConflict = data.status === "conflict_detected";

  upsert("5", (t) => ({
    ...t,
    status: isConfirmed ? "completed" : isConflict ? "need-help" : slotCount > 0 ? "in-progress" : "pending",
    subtasks: t.subtasks.map((s) => ({
      ...s,
      status: isConfirmed ? "completed" : isConflict ? "need-help" : "pending",
    })),
  }));

  return next;
}
