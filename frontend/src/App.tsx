import Plan from "@/components/ui/agent-plan";
import { SmokeBackground } from "@/components/ui/spooky-smoke-animation";
import { VercelV0Chat } from "@/components/ui/v0-ai-chat";
import {
  applyPipelineResultToTasks,
  freshHealthcareTasks,
  markPlanRunning,
} from "@/lib/syncPlanWithPipeline";
import { postPipeline } from "@/lib/api";
import type { PipelineResponse } from "@/types/pipeline";
import type { Task } from "@/types/planTask";
import { useCallback, useState } from "react";

export default function App() {
  const [planTasks, setPlanTasks] = useState<Task[]>(() => freshHealthcareTasks());
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSummary, setLastSummary] = useState<string | null>(null);

  const onSend = useCallback(async (message: string) => {
    setError(null);
    setLastSummary(null);
    setBusy(true);
    setPlanTasks((t) => markPlanRunning(t));
    try {
      const res = await postPipeline(message);
      const text = await res.text();
      let data: PipelineResponse = {};
      try {
        data = text ? (JSON.parse(text) as PipelineResponse) : {};
      } catch {
        setError("Invalid JSON from server.");
        setPlanTasks((t) => applyPipelineResultToTasks(t, {}));
        return;
      }
      if (!res.ok) {
        setError(
          typeof (data as { detail?: unknown }).detail === "string"
            ? (data as { detail: string }).detail
            : `Request failed (${res.status})`,
        );
        setPlanTasks((t) => applyPipelineResultToTasks(t, data));
        return;
      }
      setPlanTasks((t) => applyPipelineResultToTasks(t, data));
      const slots = data.available_slots?.length ?? 0;
      setLastSummary(
        data.status === "complete"
          ? slots > 0
            ? `Found ${slots} slot(s). Check the JSON in devtools or extend the UI to list them.`
            : "Intent complete — no available slots for the requested filters."
          : "Intent needs more information or validation failed.",
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Network error");
      setPlanTasks(freshHealthcareTasks);
    } finally {
      setBusy(false);
    }
  }, []);

  return (
    <div className="relative min-h-dvh w-full overflow-hidden">
      <div className="pointer-events-none fixed inset-0 z-0">
        <SmokeBackground smokeColor="#5b21b6" />
      </div>

      <div className="relative z-10 mx-auto flex min-h-dvh max-w-7xl flex-col gap-4 p-3 md:flex-row md:p-6">
        <main className="flex flex-1 flex-col items-center justify-center">
          <VercelV0Chat
            onSend={onSend}
            disabled={busy}
            errorMessage={error}
            heading="Healthcare scheduling assistant"
            placeholder="e.g. I need a cardiologist in Colombo on 2026-05-02 morning…"
          />
          {lastSummary && !error ? (
            <p className="mt-4 max-w-xl text-center text-sm text-muted-foreground">
              {lastSummary}
            </p>
          ) : null}
        </main>

        <aside className="w-full shrink-0 md:h-auto md:w-[380px] md:max-h-[calc(100dvh-3rem)]">
          <Plan tasks={planTasks} onTasksChange={setPlanTasks} />
        </aside>
      </div>
    </div>
  );
}
