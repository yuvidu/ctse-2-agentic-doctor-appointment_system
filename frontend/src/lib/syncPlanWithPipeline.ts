import { HEALTHCARE_PIPELINE_TASKS } from "@/data/healthcarePipelineTasks";
import type { PipelineResponse } from "@/types/pipeline";
import type { Task } from "@/types/planTask";

function cloneTasks(tasks: Task[]): Task[] {
  return structuredClone(tasks);
}

/** Intent agent block from ``run_system`` — top-level ``status`` is pipeline outcome, not intent. */
function intentBlockStatus(data: PipelineResponse): string | undefined {
  const block = data.intent;
  if (!block || typeof block !== "object") return undefined;
  const s = (block as { status?: unknown }).status;
  return typeof s === "string" ? s : undefined;
}

function resetStages(next: Task[], ids: string[]) {
  for (const id of ids) {
    const i = next.findIndex((t) => t.id === id);
    if (i === -1) continue;
    const t = next[i];
    next[i] = {
      ...t,
      status: "pending",
      subtasks: t.subtasks.map((s) => ({ ...s, status: "pending" })),
    };
  }
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
  const intentSt = intentBlockStatus(data);
  const intentComplete = intentSt === "complete";
  const intentHadError =
    intentSt === "error" ||
    (Array.isArray(data.errors) && data.errors.length > 0);

  const upsert = (id: string, updater: (t: Task) => Task) => {
    const i = next.findIndex((t) => t.id === id);
    if (i === -1) return;
    next[i] = updater(next[i]);
  };

  if (!intentComplete) {
    upsert("1", (t) => ({
      ...t,
      status: intentHadError ? "need-help" : "in-progress",
      subtasks: t.subtasks.map((s, i) => ({
        ...s,
        status: i === 0 ? "completed" : i === 1 ? "in-progress" : "pending",
      })),
    }));
    resetStages(next, ["2", "3", "4", "5"]);
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
  const availabilityStatus = data.availability_status ?? "";
  const availErr =
    (Array.isArray(data.availability_errors) && data.availability_errors.length > 0) ||
    availabilityStatus === "availability_missing_input" ||
    availabilityStatus === "availability_failed";

  if (availErr) {
    upsert("3", (t) => ({
      ...t,
      status: "need-help",
      subtasks: t.subtasks.map((s) => ({ ...s, status: "need-help" })),
    }));
    resetStages(next, ["4", "5"]);
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

  const pipelineStatus = data.status ?? "";
  const isConfirmed = pipelineStatus === "confirmed";
  const isConflict = pipelineStatus === "conflict_detected";
  const isBookingProblem =
    pipelineStatus === "booking_failed" || pipelineStatus === "no_slots_available";

  upsert("5", (t) => ({
    ...t,
    status: isConfirmed
      ? "completed"
      : isConflict || isBookingProblem
        ? "need-help"
        : slotCount > 0
          ? "in-progress"
          : "pending",
    subtasks: t.subtasks.map((s) => ({
      ...s,
      status: isConfirmed
        ? "completed"
        : isConflict || isBookingProblem
          ? "need-help"
          : "pending",
    })),
  }));

  return next;
}
